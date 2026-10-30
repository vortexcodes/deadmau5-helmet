#!/usr/bin/env python3
"""mau5relay -- the helmet and the camera, from somewhere else.

Three things live on the home network and nothing else can see them:
the controller, the camera page, and whatever is driving the helmet.
That is fine until the person working on it is at school behind a
VPN, which is most of the time, and it is the main reason a change
takes a day to try.

So: one process on a machine at home, which reaches all three, and
one door into it.  Behind that door are the camera's newest frame,
a proxy to the controller's JSON API, and the player page itself, so
a phone or a laptop anywhere can do what the phone at home can do.

    python3 mau5relay.py --token <something long>
    python3 mau5relay.py --token <...> --tls          # https, self-signed

**The door needs a key and it needs a tunnel.**  The token is checked
on every request -- without `--allow-open` the server refuses to
start without one -- but a token on plain http over the open internet
is a token somebody can read.  How the traffic gets here is not this
script's business and it should not be: forward a port, run a
Tailscale node, point a Cloudflare tunnel at it.  What this does is
make sure that whatever arrives has the key, and that the camera and
the helmet are reachable through one address instead of three.
"""

from __future__ import annotations

import argparse
import hmac
import json
import os
import shutil
import ssl
import threading
import time
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler

import re
import subprocess

import mau5wled


def start_tunnel(port, timeout=45, scheme="http"):
    """A Cloudflare quick tunnel to the local relay, and its URL.

    Tailscale was the plan and the school blocks it: every
    *.tailscale.com host resets on the TLS handshake, controlplane
    and the DERP relays included, so there is nothing to configure
    round it.  Cloudflare is open from the same network, looks like
    ordinary HTTPS to a CDN, and brings a real certificate -- which
    is also the one thing that would let the player install as a
    proper app.

    A quick tunnel is anonymous and its hostname is random and
    changes every restart.  That is fine for working from school and
    it is not a long-term address; a named tunnel on your own domain
    is, and wants a Cloudflare account.

    The URL is public the moment it exists.  The relay's token is the
    only thing in front of the helmet, so make it a long one.
    """
    if not shutil.which("cloudflared"):
        raise SystemExit(
            "cloudflared is not installed.\n"
            "  brew install cloudflared")
    proc = subprocess.Popen(
        ["cloudflared", "tunnel", "--url", "%s://127.0.0.1:%d" % (scheme, port),
         "--no-autoupdate"],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        text=True, bufsize=1)
    url, seen = None, []
    end = time.time() + timeout
    while time.time() < end:
        line = proc.stdout.readline()
        if not line:
            break
        seen.append(line.rstrip())
        m = re.search(r"https://[a-z0-9][a-z0-9-]*\.trycloudflare\.com", line)
        if m:
            url = m.group(0)
            break
    if url is None:
        proc.terminate()
        raise SystemExit("cloudflared did not produce a URL in %ds:\n  %s"
                         % (timeout, "\n  ".join(seen[-8:])))
    # keep draining, or the pipe fills and cloudflared wedges
    threading.Thread(target=lambda: [None for _ in proc.stdout],
                     daemon=True).start()
    return proc, url


def tailnet_ip():
    """This machine's address on the tailnet, if it is on one.

    Worth printing rather than making somebody go and look: the whole
    point of the tunnel is that the address is stable and the LAN one
    is not, so the tailnet URL is the one to bookmark.
    """
    for cmd in (["tailscale", "ip", "-4"],
                ["/Applications/Tailscale.app/Contents/MacOS/Tailscale",
                 "ip", "-4"]):
        try:
            out = subprocess.run(cmd, capture_output=True, text=True,
                                 timeout=5)
        except (OSError, subprocess.SubprocessError):
            continue
        for line in (out.stdout or "").splitlines():
            line = line.strip()
            if line.startswith("100."):
                return line
    return None

HERE = os.path.dirname(os.path.abspath(__file__))
OFFLINE = os.path.join(HERE, "data", "offline")


PAGE = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>mau5head · remote</title>
<style>
 :root{--bg:#0b0b10;--fg:#e9e9f0;--dim:#8b8b99;--line:#24242e;--ok:#2f9e63;--bad:#c2344d}
 *{box-sizing:border-box}
 body{margin:0;background:var(--bg);color:var(--fg);padding:12px;
   font:15px/1.45 ui-sans-serif,system-ui,-apple-system,Roboto,sans-serif}
 h1{font-size:17px;margin:0 0 8px}
 img{width:100%;border-radius:10px;border:1px solid var(--line);display:block;background:#000}
 .row{display:flex;gap:8px;align-items:center;margin:8px 0;flex-wrap:wrap}
 .dim{color:var(--dim);font-size:12px;font-variant-numeric:tabular-nums}
 a.btn,button{min-height:44px;border-radius:10px;border:1px solid var(--line);
   background:#191922;color:var(--fg);font:500 15px/1 inherit;padding:0 14px;
   display:inline-flex;align-items:center;text-decoration:none}
 .dot{width:9px;height:9px;border-radius:50%;background:var(--bad);display:inline-block}
 .dot.on{background:var(--ok)}
</style></head><body>
<h1>mau5head <span class="dim">· remote</span></h1>
<div class="row"><span class="dot" id="d"></span>
  <span class="dim" id="s">…</span></div>
<img id="cam" alt="the helmet">
<div class="row">
  <button id="slower">slower</button>
  <button id="faster">faster</button>
  <a class="btn" id="app" href="#">open the player</a>
</div>
<div class="row"><span class="dim" id="helmet">…</span></div>
<script>
const q = new URLSearchParams(location.search);
const tok = q.get('t') || '';
let every = 1000, timer = null, n = 0;
document.getElementById('app').href =
  '/app/mau5.htm?api=/helmet&t=' + encodeURIComponent(tok);
function tick() {
  const img = document.getElementById('cam');
  img.src = '/cam.jpg?t=' + encodeURIComponent(tok) + '&n=' + (n++);
}
async function status() {
  try {
    const r = await fetch('/status?t=' + encodeURIComponent(tok));
    const d = await r.json();
    document.getElementById('d').className = 'dot' + (d.camera_age !== null && d.camera_age < 10 ? ' on' : '');
    document.getElementById('s').textContent =
      d.camera_age === null ? 'no camera frame yet'
        : ('camera ' + d.camera_age.toFixed(1) + 's old · ' + d.frames + ' frames');
    document.getElementById('helmet').textContent = d.helmet
      ? ('helmet ' + d.helmet.name + ' · ' + d.helmet.leds + ' leds · '
         + (d.helmet.on ? 'on' : 'off') + ' · ' + d.helmet.power + ' mA')
      : 'helmet not answering';
  } catch (e) {}
}
function restart() { if (timer) clearInterval(timer); timer = setInterval(tick, every); }
document.getElementById('slower').onclick = () => { every = Math.min(8000, every * 2); restart(); };
document.getElementById('faster').onclick = () => { every = Math.max(250, every / 2); restart(); };
tick(); restart(); status(); setInterval(status, 4000);
</script></body></html>
"""


class Relay:
    def __init__(self, token, helmet=None, eye="127.0.0.1:8752",
                 allow_open=False):
        self.token = token
        self.eye = eye
        self.helmet = helmet
        self.allow_open = allow_open
        self.lock = threading.Lock()

    def ok(self, given):
        # An empty token lets everyone in only under --allow-open, which
        # used to answer 403 to everything because the empty token
        # matched nothing.  Without the flag it still lets nobody in, so
        # a MAU5_TOKEN that went missing cannot quietly open the door.
        if not self.token:
            return bool(self.allow_open)
        # Constant time, because this is the only thing between the
        # internet and a controller with no authentication of its own.
        # Bytes, because compare_digest refuses a str with anything
        # outside ASCII in it: a ?t=%C3%A9, or a token pasted with a
        # smart quote, raised in the handler and dropped the connection
        # with no answer, which looks exactly like the tunnel being down.
        # (surrogateescape for a token that came in through argv or the
        # environment as bytes that were not UTF-8.)
        return hmac.compare_digest(
            str(given).encode("utf-8", "surrogateescape"),
            self.token.encode("utf-8", "surrogateescape"))

    def _eye(self, path, timeout=8):
        with urllib.request.urlopen("http://%s%s" % (self.eye, path),
                                    timeout=timeout) as r:
            return r.read(), r.headers.get("Content-Type", "application/json")

    def _wled(self, path, body=None, timeout=10):
        url = "http://%s%s" % (self.helmet, path)
        req = urllib.request.Request(
            url, data=body,
            headers={"Content-Type": "application/json"} if body else {})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read(), r.headers.get("Content-Type", "application/json")

    def status(self):
        out = {"camera_age": None, "frames": 0, "helmet": None,
               "when": time.strftime("%Y-%m-%dT%H:%M:%S")}
        try:
            raw, _ = self._eye("/api/status", timeout=4)
            d = json.loads(raw)
            out["camera_age"] = d.get("age")
            out["frames"] = d.get("frames", 0)
        except Exception:
            pass
        try:
            raw, _ = self._wled("/json/info", timeout=4)
            d = json.loads(raw)
            out["helmet"] = {"name": d.get("name"), "ver": d.get("ver"),
                             "leds": d.get("leds", {}).get("count"),
                             "power": d.get("leds", {}).get("pwr"),
                             "on": bool(d.get("live") or True)}
            raw, _ = self._wled("/json/state", timeout=4)
            out["helmet"]["on"] = bool(json.loads(raw).get("on"))
        except Exception:
            pass
        return out


def make_handler(relay):
    class H(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"
        server_version = "mau5relay"

        def log_message(self, *a):
            pass

        def _send(self, body, ctype="application/json", code=200):
            if not isinstance(body, bytes):
                body = json.dumps(body).encode()
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            # the relay is the only door; do not let a page elsewhere
            # borrow the browser's credentials to come through it
            self.send_header("X-Frame-Options", "DENY")
            self.send_header("Referrer-Policy", "no-referrer")
            self.end_headers()
            try:
                self.wfile.write(body)
            except (BrokenPipeError, ConnectionResetError):
                pass

        def _token(self):
            from urllib.parse import urlparse, parse_qs
            q = parse_qs(urlparse(self.path).query)
            given = (q.get("t") or [""])[0]
            if not given:
                given = (self.headers.get("X-Mau5-Token") or "")
            return given

        def _guard(self):
            if relay.ok(self._token()):
                return True
            self._send({"error": "no"}, code=403)
            return False

        def do_GET(self):
            from urllib.parse import urlparse
            path = urlparse(self.path).path
            if path == "/healthz":                 # for a tunnel's probe
                return self._send({"ok": True})
            if not self._guard():
                return
            if path in ("/", "/index.html"):
                return self._send(PAGE.encode(), "text/html; charset=utf-8")
            if path == "/status":
                return self._send(relay.status())
            if path == "/cam.jpg":
                try:
                    raw, ctype = relay._eye("/latest")
                except Exception as e:
                    return self._send({"error": str(e)}, code=502)
                return self._send(raw, "image/jpeg")
            if path.startswith("/helmet/"):
                try:
                    raw, ctype = relay._wled(path[len("/helmet"):])
                except Exception as e:
                    return self._send({"error": str(e)}, code=502)
                return self._send(raw, ctype)
            if path.startswith("/app/"):
                name = os.path.basename(path)
                p = os.path.join(OFFLINE, name)
                gz = p + ".gz"
                if os.path.exists(p) or os.path.exists(gz):
                    with open(p if os.path.exists(p) else gz, "rb") as f:
                        body = f.read()
                    ct = ("text/html; charset=utf-8" if name.endswith(".htm")
                          else "application/json" if name.endswith(".json")
                          else "image/png" if name.endswith(".png")
                          else "application/octet-stream")
                    if not os.path.exists(p):
                        self.send_response(200)
                        self.send_header("Content-Type", ct)
                        self.send_header("Content-Encoding", "gzip")
                        self.send_header("Content-Length", str(len(body)))
                        self.end_headers()
                        self.wfile.write(body)
                        return
                    return self._send(body, ct)
            return self._send({"error": "no route"}, code=404)

        def do_POST(self):
            from urllib.parse import urlparse
            path = urlparse(self.path).path
            if not self._guard():
                return
            if path.startswith("/helmet/"):
                n = int(self.headers.get("Content-Length") or 0)
                body = self.rfile.read(n)
                try:
                    raw, ctype = relay._wled(path[len("/helmet"):], body)
                except Exception as e:
                    return self._send({"error": str(e)}, code=502)
                return self._send(raw, ctype)
            return self._send({"error": "no route"}, code=404)
    return H


def write_url_file(path, public, token, ssh_host=None):
    """Leave the public addresses where the far end can find them.

    The relay URL (with its token, hence 0600) and the SSH tunnel's
    host, whichever of them exist.  Best effort: a file that cannot be
    written is no reason to stop serving.
    """
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            if public:
                f.write("%s/%s\n" % (public, ("?t=" + token) if token else ""))
            if ssh_host:
                f.write("ssh host: %s\n" % ssh_host)
        os.chmod(path, 0o600)
    except OSError:
        pass


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--port", type=int, default=8780)
    ap.add_argument("--bind", default="0.0.0.0")
    ap.add_argument("--token", default=os.environ.get("MAU5_TOKEN", ""))
    ap.add_argument("--allow-open", action="store_true",
                    help="serve with no token.  Only on a network you trust "
                         "completely, which is not many of them.")
    ap.add_argument("--host", default=None, help="the controller's address")
    ap.add_argument("--eye", default="127.0.0.1:8752")
    ap.add_argument("--tls", action="store_true")
    ap.add_argument("--tunnel", action="store_true",
                    help="open a Cloudflare tunnel and print a public URL")
    ap.add_argument("--ssh", action="store_true",
                    help="also tunnel this machine's SSH, so the far end can "
                         "actually work on it rather than just look")
    ap.add_argument("--url-file",
                    default=os.path.join(HERE, "data", "cal", "relay_url.txt"),
                    help="where to leave the current public URL, because a "
                         "quick tunnel picks a new hostname every restart "
                         "and the machine running it is not the machine "
                         "you are sitting at")
    a = ap.parse_args(argv)

    if not a.token and not a.allow_open:
        raise SystemExit(
            "refusing to start without --token.\n"
            "  This proxies a controller that has no authentication of its\n"
            "  own, so the token is the only thing in the way.  Make one:\n"
            "    python3 -c \"import secrets;print(secrets.token_urlsafe(24))\"")
    if not a.token and a.tunnel:
        # --allow-open is for a network you trust, and a quick tunnel is
        # the whole internet: its URL is public the moment it exists.
        # Open mode never served anything before, so this pairing was
        # harmless by accident; now that it works it has to be refused.
        raise SystemExit("refusing --allow-open with --tunnel: the tunnel is "
                         "public, so it needs --token.")

    host = a.host
    if not host:
        try:
            w = mau5wled.find_one(None, verbose=False)
            host = w.base.split("//", 1)[-1]
        except Exception:
            host = None
    if not host:
        print("  no controller found; the camera will work and /helmet will not")

    relay = Relay(a.token, host, a.eye, allow_open=a.allow_open)
    srv = ThreadingHTTPServer((a.bind, a.port), make_handler(relay))
    scheme = "http"
    if a.tls:
        import mau5eye
        crt = os.path.join(HERE, "data", "cal", "tls", "eye.crt")
        key = os.path.join(HERE, "data", "cal", "tls", "eye.key")
        try:
            mau5eye.ensure_cert(crt, key, [mau5wled.lan_ip()])
            ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            ctx.load_cert_chain(crt, key)
            srv.socket = ctx.wrap_socket(srv.socket, server_side=True)
            scheme = "https"
        except Exception as e:
            print("  could not start https (%s); serving plain http" % e)

    tunnel = public = None
    ssh_tunnel = ssh_host = None
    if a.tunnel:
        if a.tls:
            raise SystemExit("--tunnel and --tls together would make "
                             "cloudflared talk https to a self-signed "
                             "certificate.  Pick one; the tunnel already "
                             "brings a real one.")
        print("  opening a Cloudflare tunnel...")
        tunnel, public = start_tunnel(a.port)

    if a.ssh:
        # Tailscale would have been the obvious way to get a shell
        # here and it is blocked at the other end: without Cloudflare
        # WARP the school resets every *.tailscale.com, and with WARP
        # on, WARP and Tailscale are both whole-device VPNs and will
        # not share the machine.  Cloudflare rides over WARP happily,
        # being nothing but outbound https.
        import socket as _s
        probe = _s.socket()
        probe.settimeout(2)
        if probe.connect_ex(("127.0.0.1", 22)) != 0:
            print("  nothing is listening on port 22 -- turn Remote Login on\n"
                  "  (System Settings -> General -> Sharing -> Remote Login),\n"
                  "  then run this again with --ssh")
        else:
            print("  opening an SSH tunnel...")
            ssh_tunnel, ssh_host = start_tunnel(22, scheme="ssh")
        probe.close()

    # Written once both tunnels are up.  It used to be written straight
    # after the HTTP one, before the SSH tunnel had a hostname, so the
    # shell host -- the one thing you cannot get from the far end any
    # other way -- never reached the file.
    if public or ssh_host:
        write_url_file(a.url_file, public, a.token, ssh_host)

    ip = mau5wled.lan_ip()
    q = ("?t=" + a.token) if a.token else ""
    tail = tailnet_ip()
    print("mau5relay")
    print("  on this network   %s://%s:%d/%s" % (scheme, ip, a.port, q))
    if tail:
        print("  on the tailnet    %s://%s:%d/%s" % (scheme, tail, a.port, q))
        print("                    (useless from the school network: it "
              "resets every\n                    *.tailscale.com without "
              "Cloudflare WARP, and with WARP\n                    on, WARP "
              "and Tailscale will not share a Mac.  Use the\n"
              "                    tunnel below from there.)")
    else:
        print("  from anywhere     no tailnet found.  `tailscale ip -4` on "
              "this machine\n                    should print a 100.x address "
              "once it has joined.")
    print("  helmet            %s" % (host or "not found"))
    print("  camera            http://%s/api/status" % a.eye)
    if public:
        print("  from anywhere     %s/%s" % (public, q))
        print("                    real certificate, so the player installs "
              "as an app from here.\n                    Public the moment it "
              "exists: the token is the only guard,\n                    and "
              "the hostname changes every time this restarts.")
    if ssh_host:
        who = os.environ.get("USER", "you")
        print("  shell             %s" % ssh_host)
        print("                    from the other machine:")
        print("                      ssh -o ProxyCommand='cloudflared access "
              "ssh --hostname %%h' \\\n                          %s@%s"
              % (who, ssh_host.replace("https://", "")))
    print("\n  routes: /  the dashboard      /cam.jpg  the newest frame")
    print("          /status                /helmet/json/...  the controller")
    print("          /app/mau5.htm          the player, served from here")
    print("\n  Every route needs ?t=<token> or an X-Mau5-Token header.")
    print("  ctrl-c to stop")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\n  stopped.")
    finally:
        for pr in (tunnel, ssh_tunnel):
            if pr is not None:
                pr.terminate()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
