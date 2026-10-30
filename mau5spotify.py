#!/usr/bin/env python3
"""mau5spotify -- let Spotify tell the helmet where in the track it is.

Offline, a show was missing one thing: a clock.  The cue list knows
what should be on screen at 3:42 and the carried analysis knows how
loud the track is there, but nothing on the phone knows that it *is*
3:42, so the show has to be started by hand on a downbeat and hoped
over.

Spotify knows.  `GET /v1/me/player/currently-playing` returns the
track and `progress_ms`, which is exactly the missing number, and it
keeps returning it through a pause, a seek or a skip.  Poll it once a
second, correct the local clock against it, and the show follows
whatever is playing with no tap and no drift.

What Spotify will *not* give us is the analysis.  `audio-features`
and `audio-analysis` were restricted on 27 November 2024 to apps that
already had extended access, and a new app gets 403 with no appeal.
That turns out not to matter: mau5song already analyses these tracks
at 40 Hz, which is better than Spotify's segment resolution, and
mau5drive carries it to the controller.  So Spotify supplies the
clock and the laptop supplies everything else.

This does the part a browser cannot: the first authorisation.  The
redirect has to go somewhere Spotify will accept, and the only such
place without a certificate is a loopback address -- 127.0.0.1 is
explicitly permitted and `localhost` is explicitly not.  So the
browser comes back here, and what this keeps is a refresh token.

    python3 mau5spotify.py login --client-id <id>
    python3 mau5spotify.py status
    python3 mau5spotify.py handoff          # the link to open on the phone

The token lands in data/cal/spotify.json, which is gitignored: this
repository is public and a refresh token is a credential.

The phone never gets that token.  Spotify hands back a new refresh
token when a PKCE one is used, and the page is written on the
understanding that the old one then stops working (spotify.js keeps
the new one for exactly that reason).  One token held in two places
is then a token each side kills for the other: `status` on the laptop
could leave the phone's copy dead an hour into a show, and the phone's
own refresh left the laptop handing out dead ones.  So `handoff` signs
in again and gives the phone a grant of its own, which the laptop
never keeps.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import secrets
import threading
import urllib.parse
import urllib.request
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler

HERE = os.path.dirname(os.path.abspath(__file__))
STORE = os.path.join(HERE, "data", "cal", "spotify.json")

# Loopback, because Spotify's rules leave no other option without a
# certificate: redirect URIs must be https, except for the loopback
# literals 127.0.0.1 and [::1].  "localhost" is rejected outright.
PORT = 8766
REDIRECT = "http://127.0.0.1:%d/callback" % PORT

# The one thing the helmet needs, and nothing else.  A token that can
# only read what is playing is a token worth a good deal less if it
# leaks, and this one is going to live on a phone.
SCOPE = "user-read-currently-playing"

AUTH = "https://accounts.spotify.com/authorize"
TOKEN = "https://accounts.spotify.com/api/token"


def _b64url(b):
    return base64.urlsafe_b64encode(b).rstrip(b"=").decode()


def _post_form(url, fields):
    data = urllib.parse.urlencode(fields).encode()
    req = urllib.request.Request(
        url, data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)


def read():
    try:
        with open(STORE) as f:
            return json.load(f)
    except (ValueError, OSError):
        return {}


def write(doc):
    os.makedirs(os.path.dirname(STORE), exist_ok=True)
    tmp = STORE + ".tmp"
    with open(tmp, "w") as f:
        json.dump(doc, f, indent=1)
    os.chmod(tmp, 0o600)
    os.replace(tmp, STORE)


def login(client_id, open_browser=True, store=True):
    """Authorisation Code with PKCE -- no client secret anywhere.

    PKCE exists for clients that cannot keep a secret, which is
    exactly this: whatever comes out of here ends up in a phone's
    localStorage.  The refresh is done by the page itself later, and
    it needs only the client id and the refresh token.

    `store=False` is the phone's sign-in (handoff): the grant is
    returned and never written here, so nothing on the laptop can
    spend it.
    """
    verifier = _b64url(secrets.token_bytes(64))
    challenge = _b64url(hashlib.sha256(verifier.encode()).digest())
    state = _b64url(secrets.token_bytes(16))
    url = AUTH + "?" + urllib.parse.urlencode({
        "client_id": client_id, "response_type": "code",
        "redirect_uri": REDIRECT, "scope": SCOPE, "state": state,
        "code_challenge_method": "S256", "code_challenge": challenge,
    })

    got = {}
    done = threading.Event()

    class H(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"

        def log_message(self, *a):
            pass

        def do_GET(self):
            q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            got.update({k: v[0] for k, v in q.items()})
            body = (b"<!doctype html><meta charset=utf-8>"
                    b"<body style='font:16px system-ui;background:#111;"
                    b"color:#eee;padding:40px'>"
                    b"<h2>mau5head is connected to Spotify.</h2>"
                    b"<p>You can close this tab and go back to the terminal.</p>")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            done.set()

    srv = HTTPServer(("127.0.0.1", PORT), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    print("  opening Spotify's permission page…")
    print("  if it does not open, paste this into a browser:\n\n    %s\n" % url)
    if open_browser:
        try:
            webbrowser.open(url)
        except Exception:
            pass
    if not done.wait(300):
        srv.shutdown()
        raise SystemExit("  timed out waiting for Spotify to come back")
    srv.shutdown()

    if got.get("state") != state:
        raise SystemExit("  the state did not match -- start again")
    if "error" in got:
        raise SystemExit("  Spotify said: %s" % got["error"])
    tok = _post_form(TOKEN, {
        "grant_type": "authorization_code", "code": got["code"],
        "redirect_uri": REDIRECT, "client_id": client_id,
        "code_verifier": verifier,
    })
    if "refresh_token" not in tok:
        raise SystemExit("  no refresh token came back: %s" % json.dumps(tok))
    if store:
        # laptop_only: this token is the laptop's alone, so status may
        # spend it.  A store written before handoff had its own sign-in
        # lacks it, and that token may also be sitting on a phone.
        write({"client_id": client_id, "refresh_token": tok["refresh_token"],
               "scope": tok.get("scope", SCOPE), "laptop_only": True})
        print("  saved %s  (mode 600, and gitignored)" % STORE)
    return tok


def blob(doc=None):
    """What the phone needs, as one string to carry across."""
    doc = doc or read()
    if not doc.get("refresh_token"):
        return None
    return doc["client_id"] + "." + doc["refresh_token"]


def status(spend=False):
    doc = read()
    if not doc.get("refresh_token"):
        print("  not connected.  python3 mau5spotify.py login --client-id <id>")
        return 1
    print("  connected, client %s…, scope %s"
          % (doc["client_id"][:8], doc.get("scope")))
    if not doc.get("laptop_only") and not spend:
        # Checking means refreshing, and refreshing rotates the token.
        # Until handoff signed in separately it gave the phone this very
        # token, so spending it here could leave the phone's copy dead
        # mid-show.  Ask first.
        print("  not checked: this token may also be on a phone (handoff used\n"
              "  to give the phone the laptop's own), and checking it would\n"
              "  stop that copy working.  `status --refresh` checks anyway;\n"
              "  run `handoff` for the phone afterwards.")
        return 0
    try:
        tok = _post_form(TOKEN, {"grant_type": "refresh_token",
                                 "refresh_token": doc["refresh_token"],
                                 "client_id": doc["client_id"]})
    except Exception as e:
        print("  the refresh token did not work: %s" % e)
        print("  python3 mau5spotify.py login --client-id %s" % doc["client_id"])
        return 1
    # Keep the rotated one.  Throwing it away left the store holding a
    # token Spotify had already retired, and the next status said the
    # refresh token did not work.
    if tok.get("refresh_token") and (tok["refresh_token"] != doc["refresh_token"]
                                     or not doc.get("laptop_only")):
        if not doc.get("laptop_only"):
            print("  token rotated: a phone given the old one needs `handoff` again")
        doc["refresh_token"] = tok["refresh_token"]
        doc["laptop_only"] = True
        write(doc)
    req = urllib.request.Request(
        "https://api.spotify.com/v1/me/player/currently-playing",
        headers={"Authorization": "Bearer " + tok["access_token"]})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            if r.status == 204:
                print("  nothing is playing right now")
                return 0
            d = json.load(r)
    except Exception as e:
        print("  could not read what is playing: %s" % e)
        return 1
    item = d.get("item") or {}
    print("  playing: %s  (%.1fs in, %s)"
          % (item.get("name", "?"), (d.get("progress_ms") or 0) / 1000.0,
             "running" if d.get("is_playing") else "paused"))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd")
    s = sub.add_parser("login")
    s.add_argument("--client-id", required=True)
    s.add_argument("--no-browser", dest="browser", action="store_false",
                   default=True)
    s = sub.add_parser("status")
    s.add_argument("--refresh", action="store_true",
                   help="check a token that may also be on a phone anyway")
    s = sub.add_parser("handoff")
    s.add_argument("--host", default=None, help="the controller's address")
    s.add_argument("--client-id", default=None,
                   help="if `login` has not been run on this machine")
    s.add_argument("--no-browser", dest="browser", action="store_false",
                   default=True)
    a = ap.parse_args(argv)

    if a.cmd == "login":
        login(a.client_id, a.browser)
        print("\n  now: python3 mau5spotify.py handoff")
        return 0
    if a.cmd == "status":
        return status(spend=a.refresh)
    if a.cmd == "handoff":
        cid = a.client_id or read().get("client_id")
        if not cid:
            print("  not connected yet: python3 mau5spotify.py handoff "
                  "--client-id <id>")
            return 1
        # A sign-in of the phone's own, never stored here -- see the
        # top of this file for why the laptop's token cannot be shared.
        # Spotify skips the permission page for an app already allowed,
        # so this is usually a browser tab that opens and closes.
        print("  signing in for the phone (its own token, not kept here)")
        b = blob(dict(login(cid, a.browser, store=False), client_id=cid))
        host = a.host or "4.3.2.1"
        print("  Open this once on the phone, on the page the controller")
        print("  serves.  It stores the token in that page and nothing")
        print("  else ever sees it -- the fragment after # is not sent to")
        print("  any server, including the controller's.\n")
        print("    http://%s/mau5.htm#sp=%s\n" % (host, b))
        print("  Or paste this into the Spotify box on the page:\n")
        print("    %s\n" % b)
        return 0
    ap.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
