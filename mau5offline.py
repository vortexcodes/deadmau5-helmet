#!/usr/bin/env python3
"""mau5offline -- the helmet with no network, no laptop and no router.

At a show there is no house WiFi worth trusting and no reason to carry
the laptop, so the helmet has to be its own network and its own server:
the phone joins the controller's access point, opens one page, and the
animations run.  That is what this builds, installs and checks.

Where the page has to live is forced, not chosen.  A browser cannot
send UDP, so DDP is out and the pixels have to go over the controller's
own HTTP API.  An https:// page cannot talk to a plain-http 192.168
address, so it cannot be hosted anywhere with a certificate, which
rules out GitHub Pages and with it the whole installable-PWA route.  A
plain-http page is not a secure context, so no service worker will
cache it -- the laptop cannot serve it either.  Exactly one HTTP server
is present on that network with nothing else running: the controller.
So the player is uploaded to the controller's own filesystem, where it
is same-origin with the API it drives and there is nothing to install
on the phone at all.  Any phone, any time, for as long as the helmet
boots.

    python3 mau5offline.py build            # make the page
    python3 mau5offline.py serve            # drive it against a fake helmet
    python3 mau5offline.py deploy --host X  # upload it, then read it back
    python3 mau5offline.py config --host X  # AP on, power limiter set
    python3 mau5offline.py check  --host X  # is offline mode actually there

`build` and `serve` need no hardware.  `deploy`, `config` and `check`
need to be on a network with the controller -- including its own.
"""

from __future__ import annotations

import argparse
import base64
import gzip
import io
import json
import os
import re
import time
import urllib.error
import urllib.request

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "remote", "offline")
OUT = os.path.join(HERE, "data", "offline")
CAL = os.path.join(HERE, "data", "cal")

PAGE = "mau5.htm"            # what it is called on the controller


# ----------------------------------------------------------------------
# the data bundle
# ----------------------------------------------------------------------
def _b64(a, dtype):
    return base64.b64encode(np.ascontiguousarray(a, dtype).tobytes()).decode()


def bundle():
    """Everything the page needs that is not code.

    The geometry is exported *derived* -- nfa, nel and the rest, as
    Helmet computes them -- rather than re-derived in JavaScript.  A
    second implementation of the map is a second thing to be wrong
    about the ears, and this one would be wrong on a phone at a show
    where nobody can debug it.  Ported code can disagree about colour;
    it cannot disagree about where an LED is.
    """
    import mau5engine as E
    from mau5fx import FONT5x7, SPRITES

    h = E.Helmet()
    runs = []
    for i, r in enumerate(h.region):
        if runs and runs[-1][2] == r:
            runs[-1][1] = i
        else:
            runs.append([i, i, str(r)])

    d = {
        "n": int(h.n),
        "f32": {k: _b64(v, "<f4") for k, v in {
            "px": h.px, "py": h.py, "depth": h.depth, "nx": h.nx, "ny": h.ny,
            "nfa": h.nfa, "nel": h.nel, "u": h.u, "fa": h.fa,
            "ea": h.ea, "er": h.er, "along": h.along,
            "xyz": h.xyz.reshape(-1),
        }.items()},
        "i16": {"group": _b64(h.group, "<i2"), "tube": _b64(h.tube, "<i2")},
        "regions": runs,
        "fonts": {
            "font": {k: list(v) for k, v in FONT5x7.items()},
            "digit3x5": {k: list(v) for k, v in E.DIGIT3x5.items()},
            "sprites": {k: list(v) for k, v in SPRITES.items()},
        },
        "power": json.load(open(os.path.join(CAL, "power.json"))),
        "strips": json.load(open(os.path.join(CAL, "strips.json")))["strips"],
        "presets": _preset_specs(),
        "shows": _shows(),
        "drive": {k: "%s?v=%d" % (v["file"], v.get("gz", 0)) for k, v in _drive_entries().items()},
        "playlist": _playlist(),
        "lock": {"presets": {k: list(v) for k, v in E.LOCKABLE.items()},
                 "divisions": list(E.DIVISIONS)},
        "standby": STANDBY_SLOT,
        "built": time.strftime("%Y-%m-%d"),
    }
    return d


def _unstamped(page):
    """The page with its build date blanked, for comparing two builds.

    The date is there for whoever is holding the phone, and it is the
    one part of a build that changes when nothing else has: `check`
    compared the controller's copy with a fresh build byte for byte,
    so a page deployed at eleven at night was reported out of date the
    next morning, and the only fix it offered was a redeploy that needs
    the laptop on the helmet's network -- the day of a show.
    """
    return re.sub(rb'"built":"[^"]*"', b'"built":""', page)


def _built_on(page):
    m = re.search(rb'"built":"([^"]*)"', page)
    return m.group(1).decode() if m else "?"


# The map has 621 LEDs and the controller is deliberately left driving
# 622: one rim segment was cut on 2026-10-29 and the bus was not
# reconfigured, because the last index has nothing behind it
# (mau5map.TOTAL_N).  Either count is a correct controller; anything
# else is a bus that needs looking at.
def count_agrees(controller, mapped):
    return int(controller or 0) in (int(mapped), int(mapped) + 1)


def _preset_specs():
    """Name, defaults and parameter kinds, so the page can build controls.

    Taken from the Python registry rather than written out again, so a
    preset that gains a parameter gains a slider without anyone
    remembering to add one.
    """
    import mau5engine as E
    out = {}
    for name in sorted(E.REGISTRY):
        cls = E.REGISTRY[name]
        out[name] = {"params": {k: (list(v) if isinstance(v, tuple) else v)
                                for k, v in cls.params.items()},
                     "spec": cls.spec()}
    return out


# ----------------------------------------------------------------------
# build
# ----------------------------------------------------------------------
def _read(name):
    with open(os.path.join(SRC, name)) as f:
        return f.read()


def _uncommented(js):
    """js without its whole-line // comments, about 30 kB of the gzipped page.  Only
    whole lines: one can not be inside a string or a regex, and none of the scripts has
    a multi-line template string with such a line in it (test_mau5 holds them to that)."""
    return "\n".join(ln for ln in js.split("\n") if not ln.lstrip().startswith("//"))


def _drive_entries():
    try:
        with open(os.path.join(OUT, "drive.json")) as f:
            return json.load(f)
    except (ValueError, OSError):
        return {}


def _playlist():
    """The set 'Play Music' runs through; shows it leaves out go on the end."""
    try:
        with open(os.path.join(HERE, "shows", "scenes", "playlist.json")) as f:
            return json.load(f)
    except (ValueError, OSError):
        return []


def _drive_index():
    """Which analysis file belongs to which show, if they were built.

    The drives are uploaded beside the page rather than baked into
    it: all five are a quarter of a megabyte, the page is seventy
    kilobytes, and only the show somebody picks needs fetching.
    """
    path = os.path.join(OUT, "drive.json")
    try:
        with open(path) as f:
            return {k: v["file"] for k, v in json.load(f).items()}
    except (ValueError, OSError):
        return {}


def _shows():
    """The cue lists, and nothing else about a show.

    A show is three things on the laptop: a cue list, an analysis of
    the track, and the track.  Only the first fits here -- the five
    analyses are two megabytes and the audio is sixty, against about
    nine hundred kilobytes free on the controller.

    So the cue list rides in the page, the analysis goes up beside it
    as a compact drive file (deploy_drives), and the song lives on the
    phone: `songs` serves it from a laptop once and the page keeps it,
    after which the song is also the clock and nothing has to be
    started by hand.
    """
    out = {}
    d = os.path.join(HERE, "shows")
    if not os.path.isdir(d):
        return out
    for fn in sorted(os.listdir(d)):
        if not fn.endswith(".json"):
            continue
        try:
            with open(os.path.join(d, fn)) as f:
                sh = json.load(f)
        except (ValueError, OSError):
            continue
        if not sh.get("cues"):
            continue
        cues = []
        for c in sorted(sh["cues"], key=lambda c: c["start"]):
            keep = {k: c[k] for k in ("start", "end", "preset", "params",
                                      "level", "gain") if k in c}
            if c.get("overlay"):
                keep["overlay"] = c["overlay"]
            cues.append(keep)
        out[fn[:-5]] = {
            "track": sh.get("track", fn[:-5]),
            "duration": sh.get("duration", 0.0),
            "bpm": sh.get("bpm", 120.0),
            "fade": sh.get("fade", 0.0),
            "accent": bool(sh.get("accent", False)),
            "pulse": sh.get("pulse", 0.22),
            "dynamics": sh.get("dynamics", 0.72),
            "dynamics_gamma": sh.get("dynamics_gamma", 0.7),
            "lock": sh.get("lock"),
            "cues": cues,
        }
        # The choreography, when the song has one.  Compiled on the
        # laptop with every default filled in, so the page evaluates it
        # as it stands; the cues above stay, for ?cues and as the
        # fallback if it throws.
        if sh.get("scenes"):
            out[fn[:-5]]["scenes"] = sh["scenes"]
    return out


def build(verbose=True):
    os.makedirs(OUT, exist_ok=True)
    data = bundle()
    data_js = ("globalThis.MAU5_DATA = %s;\n"
               % json.dumps(data, separators=(",", ":")))
    with open(os.path.join(OUT, "data.js"), "w") as f:
        f.write(data_js)

    html = _read("player.html")
    parts = {"DATA": data_js}
    for js in ("engine.js", "guard.js", "wire.js", "audio.js",
               "drive.js", "spotify.js", "show.js", "ui.js"):
        parts[js.split(".")[0].upper()] = _uncommented(_read(js))
    missing = [k for k in re.findall(r"<!--@(\w+)-->", html) if k not in parts]
    if missing:
        raise SystemExit("player.html wants %s and the build has no such part"
                         % ", ".join(missing))
    page = re.sub(r"<!--@(\w+)-->", lambda m: parts[m.group(1)], html)

    # A page that *loads* something from a CDN is a page that is blank
    # at a show, so nothing it needs to render may come from anywhere
    # but the controller.  That is a rule about src, href, @import and
    # url() -- not about every string containing "https", because the
    # page does call Spotify's API when somebody asks it to, and that
    # is an opt-in feature which the page works perfectly without.
    bad = re.findall(r"""(?:src|href)\s*=\s*["']\s*(?:https?:)?//[^"']+"""
                     r"""|@import[^;]*//[^;]*"""
                     r"""|url\(\s*["']?(?:https?:)?//[^)]*""", page)
    if bad:
        raise SystemExit("offline page loads %s -- it must be self contained"
                         % bad[0][:80])
    reached = sorted(set(re.findall(r"https://([a-z0-9.-]+)/", page)))
    if verbose and reached:
        print("  reaches out, only when asked: %s" % ", ".join(reached))

    plain = os.path.join(OUT, PAGE)
    with open(plain, "w") as f:
        f.write(page)
    raw = page.encode()
    # mtime 0: the same inputs must give the same bytes, or every build
    # looks like a change worth uploading.
    buf = io.BytesIO()
    with gzip.GzipFile(fileobj=buf, mode="wb", compresslevel=9, mtime=0) as g:
        g.write(raw)
    gz = buf.getvalue()
    with open(plain + ".gz", "wb") as f:
        f.write(gz)
    if verbose:
        print("%s   %6.1f kB" % (plain, len(raw) / 1024.0))
        print("%s   %6.1f kB  (what goes on the controller)"
              % (plain + ".gz", len(gz) / 1024.0))
        print("  %d presets, %d shows, %d LEDs, budget %.0f mA"
              % (len(data["presets"]), len(data["shows"]), data["n"],
                 data["power"]["budget_ma"]))
    return plain, raw, gz


# ----------------------------------------------------------------------
# the controller
# ----------------------------------------------------------------------
def _find(host):
    import mau5wled
    if host:
        return mau5wled.WLED(host)
    found = mau5wled.scan_subnet()
    if not found:
        raise SystemExit(
            "no controller found.\n"
            "  On the house network it is found by scanning; on the helmet's\n"
            "  own access point it is at 4.3.2.1, so pass --host 4.3.2.1.")
    return found[0]


SONGS_PORT = 8799
SONGS_POINTER = "/songs.json"


def _song_files(dirs=None):
    """Show name -> the song file on this machine, for every show that has one.

    Looked for beside the show files and then at the top of the
    repository, which is where the tracks have lived; nothing is ever
    committed, because the repository is public and the tracks are not
    ours to give away.
    """
    look = list(dirs or []) + [os.path.join(HERE, "shows"), HERE]
    out = {}
    for name, sh in _shows().items():
        track = os.path.basename(sh.get("track") or name + ".mp3")
        for d in look:
            p = os.path.join(d, track)
            if os.path.isfile(p):
                out[name] = p
                break
    return out


def _address_towards(w):
    """The address the controller's network knows this machine by."""
    import socket
    host = w.base.split("//", 1)[-1].split("/")[0].split(":")[0]
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect((host, 80))           # no packet is sent; it picks a route
        return s.getsockname()[0]
    finally:
        s.close()


def songs(host=None, port=SONGS_PORT, dirs=None):
    """Give every phone that opens the page the shows' songs, once.

    The songs cannot live on the controller -- sixty megabytes against
    under one free -- and cannot be put anywhere public.  So the laptop
    serves them on the local network for as long as this runs, and
    leaves a pointer on the controller saying where.  The page reads the
    pointer, fetches whatever songs the phone does not have yet into its
    own storage, and from then on plays them with no laptop and no
    network.  Any phone, no files needed on it first.

    The phone has to be on the same network as this machine, and the
    copies are kept per address.  A phone that will use the helmet's own
    Wi-Fi at a show saves them as files from the page at the house, and
    loads those on the helmet's Wi-Fi; the page offers both.
    """
    import http.server
    import socketserver
    import threading
    import mau5wled

    files = _song_files(dirs)
    if not files:
        raise SystemExit("none of the shows' songs are on this machine -- put "
                         "the mp3s beside the show files, or pass --dir")
    w = mau5wled.find_one(host)
    me = _address_towards(w)
    names = sorted(files)
    route = {"/songs/%d.mp3" % k: files[n] for k, n in enumerate(names)}
    pointer = {
        "from": "http://%s:%d" % (me, port),
        "songs": {n: {"path": "/songs/%d.mp3" % k,
                      "track": os.path.basename(files[n]),
                      "bytes": os.path.getsize(files[n])}
                  for k, n in enumerate(names)},
        "since": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }

    class H(http.server.BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"

        def log_message(self, *a):
            pass

        def _cors(self):
            # The page is the controller's origin and this is another:
            # say yes, including Chrome's private-network question.
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Private-Network", "true")

        def do_OPTIONS(self):
            self.send_response(204)
            self._cors()
            self.send_header("Access-Control-Allow-Methods", "GET")
            self.send_header("Content-Length", "0")
            self.end_headers()

        def do_GET(self):
            if self.path.split("?", 1)[0] == SONGS_POINTER:
                # So another machine can ask without going through the controller.
                body = json.dumps(pointer).encode()
                self.send_response(200)
                self._cors()
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return
            p = route.get(self.path.split("?", 1)[0])
            if p is None:
                self.send_response(404)
                self._cors()
                self.send_header("Content-Length", "0")
                self.end_headers()
                return
            size = os.path.getsize(p)
            self.send_response(200)
            self._cors()
            self.send_header("Content-Type", "audio/mpeg")
            self.send_header("Content-Length", str(size))
            self.end_headers()
            with open(p, "rb") as f:
                while True:
                    chunk = f.read(1 << 16)
                    if not chunk:
                        break
                    try:
                        self.wfile.write(chunk)
                    except (BrokenPipeError, ConnectionResetError):
                        return
            print("  sent %s to %s" % (os.path.basename(p), self.client_address[0]))

    class Server(socketserver.ThreadingMixIn, http.server.HTTPServer):
        daemon_threads = True
        allow_reuse_address = True

    def keep_pointing():
        # A laptop's address changes under a server left running, and the
        # pointer then sends every phone to where it used to be.
        while True:
            time.sleep(30)
            try:
                here = "http://%s:%d" % (_address_towards(w), port)
                if here != pointer["from"]:
                    moved = dict(pointer, **{"from": here})
                    _upload(w, SONGS_POINTER, json.dumps(moved).encode(),
                            "application/json")
                    pointer["from"] = here
                    print("  this machine moved: the songs are now at %s" % here)
            except (OSError, SystemExit):
                pass                # out of the controller's reach for now

    srv = Server(("0.0.0.0", port), H)
    _upload(w, SONGS_POINTER, json.dumps(pointer).encode(), "application/json")
    threading.Thread(target=keep_pointing, daemon=True).start()
    total = sum(v["bytes"] for v in pointer["songs"].values()) / 1e6
    print("  serving %d songs, %.0f MB, from %s" % (len(names), total, pointer["from"]))
    for n in names:
        print("    %s" % os.path.basename(files[n]))
    print("  and told the controller, so any phone that opens the page on this")
    print("  network fetches the songs it is missing and keeps them.")
    print("  ctrl-c to stop (the pointer is removed again)")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        srv.server_close()
        _delete(w, SONGS_POINTER)
        print("\n  stopped; pointer removed from the controller")
    return 0


def _upload(w, path, data, ctype="text/html"):
    """WLED's own file manager: a multipart POST, path in the filename.

    Tries /upload and then /edit, because which of the two the file
    manager is mounted on has moved between releases and there is no
    way to tell from outside which build this is.
    """
    b = b"----mau5%d" % int(time.time())
    body = (b"--" + b + b"\r\nContent-Disposition: form-data; name=\"data\"; "
            b"filename=\"" + path.encode() + b"\"\r\n"
            b"Content-Type: " + ctype.encode() + b"\r\n\r\n" + data +
            b"\r\n--" + b + b"--\r\n")
    last = None
    for route in ("/upload", "/edit"):
        req = urllib.request.Request(
            w.base + route, data=body, method="POST",
            headers={"Content-Type":
                     "multipart/form-data; boundary=" + b.decode(),
                     "Content-Length": str(len(body))})
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.status
        except urllib.error.URLError as e:
            last = e
    raise SystemExit("neither /upload nor /edit accepted the file: %s\n"
                     "  If this build has no filesystem the page cannot live "
                     "on the controller;\n  `mau5fake.py --host <ip>` will "
                     "serve it from here instead, laptop and all." % last)


def _delete(w, path):
    """Remove a file, so a fallback does not leave a stale one behind."""
    body = ("path=" + path).encode()
    req = urllib.request.Request(
        w.base + "/edit", data=body, method="DELETE",
        headers={"Content-Type": "application/x-www-form-urlencoded"})
    try:
        urllib.request.urlopen(req, timeout=10)
    except urllib.error.URLError:
        pass


def deploy(host=None, gzipped=True, verbose=True):
    plain, raw, gz = build(verbose=False)
    w = _find(host)
    info = w.info(True)
    fs = info.get("fs") or {}
    body = gz if gzipped else raw
    name = "/" + PAGE + (".gz" if gzipped else "")
    free = (fs.get("t", 0) - fs.get("u", 0)) * 1024 if fs else None
    print("%s  WLED %s   filesystem %s"
          % (info.get("name", "?"), info.get("ver", "?"),
             "%d of %d kB used" % (fs.get("u", 0), fs.get("t", 0)) if fs
             else "not reported"))
    # The page replaces the one already there, so that one's room counts as free.
    if free is not None:
        free += _listing(w).get(name.lstrip("/"), 0)
    if free is not None and free < len(body) + 8192:
        raise SystemExit("only %.1f kB free on the controller and the page is "
                         "%.1f kB" % (free / 1024.0, len(body) / 1024.0))

    print("uploading %s  (%.1f kB)" % (name, len(body) / 1024.0))
    _upload(w, name, body)

    # Read it back.  Uploading is not the risky part -- whether the
    # controller serves a .gz under its plain name is, and that is a
    # property of the firmware build, not of anything here.  Better to
    # find out now than on the phone at a show.
    time.sleep(0.6)
    url = w.base + "/" + PAGE
    try:
        req = urllib.request.Request(url, headers={"Accept-Encoding": "gzip"})
        with urllib.request.urlopen(req, timeout=15) as r:
            got = r.read()
            enc = (r.headers.get("Content-Encoding") or "").lower()
    except urllib.error.URLError as e:
        raise SystemExit("uploaded, but %s does not answer: %s" % (url, e))
    if enc == "gzip":
        got = gzip.decompress(got)
    if got != raw:
        if gzipped:
            print("  the controller does not serve %s.gz under its plain name "
                  "-- falling back to the uncompressed page" % PAGE)
            _delete(w, "/" + PAGE + ".gz")
            return deploy(host, gzipped=False, verbose=verbose)
        raise SystemExit("read back %d bytes, expected %d -- the upload did "
                         "not land" % (len(got), len(raw)))
    print("verified: %s returns the %d-byte page" % (url, len(raw)))
    deploy_extras(w)
    n = deploy_drives(w)
    if n:
        print("  %.0f kB of track analysis alongside it" % (n / 1024.0))
    print("\n  on the helmet's access point that is  http://4.3.2.1/%s" % PAGE)
    return url


# ----------------------------------------------------------------------
# configuration: the two things offline mode needs that a show does not
# ----------------------------------------------------------------------
def bus_budgets(buses, total_ma, per_led_ma):
    """Spread one current budget over however many output buses there are.

    Measured on the helmet's own controller (WLED 0.15.4): the limiter
    that actually runs is the *per bus* one.  Writing the global
    ``hw.led.maxpwr`` changes ``info.leds.maxpwr`` and nothing else --
    asking for 1390 mA of white drew 1178 mA with the global set to
    700.  Moving the same number onto the bus clamps immediately and
    linearly, and the reported draw comes out at the cap less one
    milliamp per LED, which is WLED reserving the same standby figure
    ``mau5power`` uses.  So the cap to write is the budget *including*
    standby, and the firmware subtracts the standby itself.

    The global is written as well.  It is inert here but it is what
    older builds read, and a number that disagrees with the bus would
    be worse than one that is merely ignored.
    """
    out, n = [], sum(max(1, int(b.get("len") or 0)) for b in buses) or 1
    for b in buses:
        c = dict(b)
        c["maxpwr"] = int(round(total_ma * max(1, int(b.get("len") or 0)) / n))
        c["ledma"] = int(round(per_led_ma))
        out.append(c)
    return out


def limiter_ma(power):
    """What WLED's own limiter is set to, in mA at 12 V, standby included.

    WLED's limiter is a per-frame clamp with no memory.  It cannot let
    a chorus through and then ration the next ten minutes the way the
    guard's thermal bucket does: whatever it allows, it allows for
    ever.  And what it governs runs for ever too -- the standby preset
    on a shelf, the hand-back after every phone session, the boot
    preset, a stray tap in WLED's own app -- with no guard and no
    bucket anywhere.  So it gets the figure the helmet can hold
    indefinitely: power.json's sustained watts less standby, 11.0 -
    7.45 W, which is 296 mA of LED current.  It used to get the
    per-frame budget plus standby, 1621 mA, which let WLED's own
    effects sit at about 0.9 A of LED current -- three times the
    sustained figure -- for as long as nobody noticed.

    On top go the two things WLED takes off a bus cap before it lights
    anything: a milliamp per LED of standby (measured, see bus_budgets)
    and 100 mA for the board itself (MA_FOR_ESP, the same in WLED and
    in mau5wled).  Without the second the helmet would sit 100 mA under
    the sustained figure, which is safe and pointlessly dim.

    Never more than the old per-frame figure, whatever a profile says,
    and a profile with no thermal section keeps exactly that.
    """
    import mau5power
    import mau5wled
    standby = power["count"] * mau5power.MA_PER_LED_STANDBY
    old = power["budget_ma"] + standby
    th = power.get("thermal") or {}
    if not th:
        return int(round(old))
    # The same subtraction ThermalBudget.allowance_w makes once the
    # bucket is full, at the 12 V the rest of the power model uses.
    led = max(float(th.get("sustained_w", 11.0))
              - float(th.get("standby_w", 0.0)), 0.0) / 12.0 * 1000.0
    want = led + standby + mau5wled.WLED.MA_FOR_ESP
    return int(min(old, want))          # floor: round towards less light


# What the ESP32's soft-AP will take.  WLED accepts anything over
# /json/cfg and stores it, but the Arduino core's WiFi.softAP() refuses
# a passphrase of one to seven characters and returns false -- so a
# short password does not make a weak access point, it makes none, and
# at a show with no house network that is offline mode gone.
def ap_problem(ssid=None, psk=None):
    """Why this SSID or password would leave the helmet with no AP, or None."""
    if ssid is not None:
        b = str(ssid).encode("utf-8")
        if not 1 <= len(b) <= 32:
            return ("an access point name has to be 1 to 32 bytes; %r is %d"
                    % (ssid, len(b)))
    if psk is not None:
        p = str(psk)
        if not 8 <= len(p) <= 63:
            return ("an access point password has to be 8 to 63 characters "
                    "(that one is %d) -- the controller would accept it and "
                    "then bring up no access point at all" % len(p))
        if any(not 32 <= ord(c) <= 126 for c in p):
            return ("an access point password has to be plain printable "
                    "ASCII -- WPA2 takes nothing else")
    return None


def wanted_cfg(power, ap_ssid=None, ap_psk=None, buses=None):
    """The configuration changes offline mode depends on.

    Two of them, and neither is cosmetic.

    The access point has to come up whether or not a known network is
    in range, because at a show none is, and `ap.behav` 0 only starts
    it when the join fails -- which it does, but a minute later and
    not at all if some open network happens to answer.

    The brightness limiter has to be set from the same profile the
    software guard uses.  On the house network the guard in Pixels.send
    is the only thing between a preset and 11.8 A, and that is fine
    because every frame goes through it.  What the controller renders
    by itself -- standby, boot, the hand-back -- never passes a guard,
    so WLED's own limiter runs below anything a page can reach, set to
    what the helmet can sustain (limiter_ma) and left there.
    """
    why = ap_problem(ap_ssid, ap_psk)
    if why:
        raise ValueError(why)
    # WLED's limiter is pure current arithmetic and never learns the
    # supply voltage, so feeding it milliamps measured at 12 V is
    # consistent as long as ledma is too -- which is why both numbers
    # come from the same place the software guard reads.
    import mau5power
    ma = int(round(power["budget_ma"] + power["count"]
                   * mau5power.MA_PER_LED_STANDBY))
    # Two figures, on purpose.  The buses get the sustained cap, and
    # they are the limiter 0.15 enforces (bus_budgets).  The global
    # keeps the per-frame budget: 0.15 accepts it and ignores it, and
    # test_mau5's t_offline_limiter_matches_the_budget still pins it
    # there.  Lowering the global to match is safe and wanted, and
    # waits on that test.
    led = {"maxpwr": ma, "ledma": int(round(mau5power.MA_PER_LED_FULL_WHITE))}
    if buses:
        led["ins"] = bus_budgets(buses, limiter_ma(power),
                                 mau5power.MA_PER_LED_FULL_WHITE)
    cfg = {"ap": {"behav": 2},        # 2 = always on, not only when lost
           "hw": {"led": led}}
    if ap_ssid:
        cfg["ap"]["ssid"] = ap_ssid
    if ap_psk:
        cfg["ap"]["psk"] = ap_psk
    return cfg


def _flat(d, p=""):
    out = {}
    for k, v in d.items():
        if isinstance(v, dict):
            out.update(_flat(v, p + k + "."))
        else:
            out[p + k] = v
    return out


def config(host=None, apply=False, ap_ssid=None, ap_psk=None):
    # Before anything is sent, or even looked for: `config` used to
    # print "applied." over a password the controller then could not
    # start an access point with.
    why = ap_problem(ap_ssid, ap_psk)
    if why:
        raise SystemExit("not sent: " + why)
    w = _find(host)
    power = json.load(open(os.path.join(CAL, "power.json")))
    cur = w.cfg()
    buses = ((cur.get("hw") or {}).get("led") or {}).get("ins") or []
    want = wanted_cfg(power, ap_ssid, ap_psk, buses)
    changes = []
    for i, b in enumerate(want["hw"]["led"].get("ins") or []):
        have = buses[i] if i < len(buses) else {}
        for k in ("maxpwr", "ledma"):
            if have.get(k) != b[k]:
                changes.append(("bus %d %s" % (i, k), have.get(k), b[k]))
    for k, v in _flat(want).items():
        if k.endswith(".ins"):
            continue
        # 0.15 keeps no global ledma: it accepts the write, stores
        # nothing and reads back 0 for ever.  Reporting that as an
        # outstanding change would mean `config` never came up clean.
        if k == "hw.led.ledma" and buses:
            continue
        if k.endswith(".psk"):
            changes.append((k, "(unchanged or unset)", "(set)"))
            continue
        node = cur
        for part in k.split(".")[:-1]:
            node = (node or {}).get(part) or {}
        have = node.get(k.split(".")[-1])
        if have != v:
            changes.append((k, have, v))
    if not changes:
        print("already configured for offline use")
        return 0
    print("%-16s %-22s %s" % ("setting", "now", "wanted"))
    for k, a, b in changes:
        print("  %-14s %-22s %s" % (k, a, b))
    print("\n  The bus maxpwr is what data/cal/power.json says the helmet can\n"
          "  sustain indefinitely, plus standby and WLED's 100 mA board\n"
          "  reserve, in mA at 12 V: %d mA.  WLED's limiter has no memory,\n"
          "  so it cannot allow a burst and then ration it the way the guard\n"
          "  does -- whatever it allows, it allows for ever.  It covers what\n"
          "  the controller renders by itself: standby, boot, the hand-back\n"
          "  and WLED's own app.  It does not see the phone's frozen-segment\n"
          "  frames (measured).  Whether it also clamps DDP from the laptop\n"
          "  has not been measured; if it does, laptop shows will peak lower\n"
          "  than the guard alone would let them.  The global maxpwr is\n"
          "  inert on 0.15 and keeps the per-frame budget."
          % limiter_ma(power))
    if not apply:
        print("\nnothing changed.  Re-run with --apply.")
        return 0
    w._post("/json/cfg", want)
    print("\napplied.")
    return 0


# ----------------------------------------------------------------------
# check
# ----------------------------------------------------------------------
# What an installed app needs beside the page.  A browser will not
# read a manifest from a data: URL, so these are real files.
EXTRAS = ("manifest.json", "i192.png", "i512.png", "i512m.png")


def deploy_extras(w, verbose=True):
    """The manifest and icons, so the phone can keep it as an app."""
    import mau5icon
    mau5icon.main([])
    have = _listing(w)
    sent = 0
    for fn in EXTRAS:
        path = os.path.join(OUT, fn)
        if not os.path.exists(path):
            continue
        with open(path, "rb") as f:
            blob = f.read()
        if have.get(fn) == len(blob):
            continue
        ctype = "application/json" if fn.endswith(".json") else "image/png"
        _upload(w, "/" + fn, blob, ctype)
        sent += len(blob)
        time.sleep(0.4)
        if verbose:
            print("  %-14s %6d bytes" % (fn, len(blob)))
    return sent


def _listing(w):
    """What is already on the controller, name -> size."""
    try:
        with urllib.request.urlopen(w.base + "/edit?list=/", timeout=15) as r:
            return {e["name"].lstrip("/"): e.get("size", 0)
                    for e in json.load(r) if e.get("type") == "file"}
    except (urllib.error.URLError, ValueError, KeyError):
        return {}


DRIVE_RESERVE = 64 * 1024       # left free for settings and presets


def deploy_drives(w, verbose=True):
    """Put the per-track analyses beside the page.

    Only the ones that are not already there at the right size.  All
    five are a quarter of a megabyte, and pushing that through the
    file manager on every deploy is both slow and the thing that made
    the controller reboot mid-upload -- it is a 240 MHz board holding
    a multipart body in RAM.
    """
    idx = _drive_index()
    if not idx:
        return 0
    have = _listing(w)
    sent = skipped = 0
    # A filesystem that fills up truncates whatever is written next, and the
    # next thing could be the controller's own settings.  A song without its
    # analysis still plays, off what the page hears.
    fs = w.info(True).get("fs") or {}
    room = (fs.get("t", 0) - fs.get("u", 0)) * 1024 - DRIVE_RESERVE if fs else None
    for show, fn in sorted(idx.items()):
        gz = os.path.join(OUT, fn + ".gz")
        if not os.path.exists(gz):
            continue
        with open(gz, "rb") as f:
            blob = f.read()
        if have.get(fn + ".gz") == len(blob):
            skipped += 1
            continue
        grows = len(blob) - have.get(fn + ".gz", 0)
        if room is not None and grows > room:
            print("  no room for the analysis of %s: it would run off what the "
                  "page hears" % show)
            continue
        if room is not None:
            room -= grows
        _upload(w, "/" + fn + ".gz", blob, "application/octet-stream")
        sent += len(blob)
        time.sleep(1.0)                 # let the board breathe
        if verbose:
            print("  %-8s %6d bytes  %s" % (fn, len(blob), show[:40]))
    if verbose and skipped:
        print("  %d track analyses already there, unchanged" % skipped)
    return sent


# A handful of WLED's own effects that cover the whole helmet, move
# slowly, and look like something rather than a test pattern.  They
# are the controller's, not ours, which is the entire point: they
# keep running when the phone is in a pocket.
STANDBY_FX = {"pacifica": 101, "aurora": 38, "pride": 63,
              "colorloop": 8, "breathe": 2, "solid": 0}

STANDBY_SLOT = 1


def standby(host=None, fx="pacifica", bri=32, boot=True, apply=False):
    """Give the helmet something to do when nobody is driving it.

    The brightness here is not measured.  32 is a cautious guess at what
    fits the sustained budget; the page's "set up" button next to standby
    glow measures the same effect on the helmet and is the better way.

    The complaint this answers: close the page and the lights stop.
    They did, by design -- a frozen segment holds the last frame for
    ever, so the player arms a dead man and the helmet goes dark a
    minute after the phone stops talking.  Safe, and useless if what
    you wanted was a lit helmet on a shelf.

    So instead of switching off, the player hands back.  WLED's own
    effects run on the controller with no phone, no laptop and no
    network, and the brightness limiter does cover them -- it is
    blind only to pixels painted into a frozen segment, which is the
    player's path, not this one.  Saved as a preset so the handover
    is one short message, and set as the boot preset so a helmet
    that is simply plugged in comes up lit.
    """
    import mau5wled
    w = _find(host)
    fxid = STANDBY_FX.get(fx)
    if fxid is None:
        raise SystemExit("no standby effect %r.  Known: %s"
                         % (fx, ", ".join(sorted(STANDBY_FX))))
    print("%s  WLED %s" % (w.info().get("name", "?"), w.info().get("ver", "?")))
    print("  standby: %s (fx %d) at brightness %d, preset %d%s"
          % (fx, fxid, bri, STANDBY_SLOT, ", and on boot" if boot else ""))
    if not apply:
        print("\n  nothing changed.  Re-run with --apply.")
        return 0
    # One unfrozen segment over the whole chain, and any others the
    # player left behind deleted -- the same layout wire.js release()
    # hands back -- so that what is saved below is exactly one effect
    # and never a frozen segment, which the limiter cannot see.
    n = w.count
    if not n:
        # stop 0 is how a segment is deleted; never send it for segment 0.
        raise SystemExit("the controller reports no LEDs -- not touching it")
    others = [s.get("id") for s in (w.state().get("seg") or [])
              if s.get("id") not in (None, 0)]
    seg = [{"id": 0, "start": 0, "stop": n, "frz": False, "fx": fxid,
            "sx": 110, "ix": 128, "pal": 0, "on": True, "bri": 255}]
    seg += [{"id": i, "stop": 0} for i in others]
    w._post("/json/state", {"on": True, "bri": int(bri), "transition": 7,
                            "nl": {"on": False}, "seg": seg})
    time.sleep(0.6)
    # ib and sb, or WLED saves neither the brightness nor the segment
    # bounds: a psave that carries anything besides the slot keeps the
    # brightness only with ib and the bounds only with sb (savePreset in
    # WLED's presets.cpp), which is why WLED's own UI always sends both.
    # Without ib the hand-back -- {ps: 1}, with no brightness of its own
    # -- runs at whatever brightness the phone left, 255 by default,
    # instead of the brightness asked for here.  Not yet read back from this controller:
    # preset 1 in /presets.json should now carry "bri".
    w._post("/json/state", {"psave": STANDBY_SLOT, "n": "mau5 standby",
                            "ib": True, "sb": True})
    time.sleep(0.6)
    if boot:
        w._post("/json/cfg", {"def": {"ps": STANDBY_SLOT, "on": True,
                                      "bri": int(bri)}})
    print("\n  applied.  The helmet will hold this whenever the page lets go,")
    print("  and come up in it when it is powered on.")
    return 0


def check(host=None):
    """Would the helmet work on its own, right now, with no laptop?"""
    plain, raw, gz = build(verbose=False)
    w = _find(host)
    info, cfg = w.info(True), w.cfg()
    power = json.load(open(os.path.join(CAL, "power.json")))
    buses = ((cfg.get("hw") or {}).get("led") or {}).get("ins") or []
    want = wanted_cfg(power, buses=buses)
    rows, bad = [], 0

    def row(ok, what, detail):
        nonlocal bad
        rows.append(("ok " if ok else "NO ", what, detail))
        if not ok:
            bad += 1

    ap = cfg.get("ap", {})
    row(ap.get("behav") == 2, "access point always on",
        "ap.behav = %s" % ap.get("behav"))
    row(bool(ap.get("ssid")), "access point has a name",
        "ap.ssid = %r" % ap.get("ssid"))
    # Only the length comes back, never the password, so this cannot
    # tell a chosen one from WLED's own default -- which is also eight
    # characters.  It catches an open access point and nothing else.
    row(int(ap.get("pskl") or 0) >= 8, "access point has a password",
        "%s characters (length only; set yours with --ap-psk)"
        % (ap.get("pskl") or 0))

    # The bus is what 0.15 enforces -- see bus_budgets.  Checking the
    # global instead passed on a helmet whose real limiter was 1800.
    wl = want["hw"]["led"]
    wb = wl.get("ins") or []
    cap = sum(int(b.get("maxpwr") or 0) for b in buses)
    # Measured, not assumed: WLED's estimator does not count pixels
    # painted into a frozen segment, so the limiter it drives does not
    # clamp them either -- /json/info reports a flat idle 120 mA while
    # the page is painting a full rainbow.  The cap is still worth
    # setting, because it does cover everything the controller renders
    # itself, which is what a stray tap in WLED's own UI produces.  It
    # is not what keeps the phone honest; the guard in the page is.
    want_cap = sum(int(b["maxpwr"]) for b in wb)
    row(bool(wb) and all(buses[i].get("maxpwr") == b["maxpwr"]
                         for i, b in enumerate(wb)),
        "limiter set, for WLED's own effects",
        "bus caps total %s mA, wanted %s%s"
        % (cap, want_cap,
           " -- above what the helmet can sustain" if cap > want_cap else ""))
    row(bool(wb) and all(int(buses[i].get("ledma") or 0) == b["ledma"]
                         for i, b in enumerate(wb)),
        "limiter knows the per-LED current",
        "ledma %s mA, wanted %s"
        % ([b.get("ledma") for b in buses], wl["ledma"]))

    try:
        with urllib.request.urlopen(w.base + "/" + PAGE, timeout=10) as r:
            got = r.read()
            if (r.headers.get("Content-Encoding") or "").lower() == "gzip":
                got = gzip.decompress(got)
    except urllib.error.URLError:
        got = b""
    row(bool(got) and _unstamped(got) == _unstamped(raw),
        "player page installed and current",
        "%d bytes on the controller (built %s), %d built"
        % (len(got), _built_on(got) if got else "-", len(raw)))

    row(count_agrees(info.get("leds", {}).get("count"), power["count"]),
        "controller agrees about the LED count",
        "%s, map has %d" % (info.get("leds", {}).get("count"), power["count"]))

    print("%s  WLED %s\n" % (info.get("name", "?"), info.get("ver", "?")))
    for ok, what, detail in rows:
        print("  %s %-38s %s" % (ok, what, detail))
    if bad:
        print("\n%d of %d not ready.  `config --apply` fixes the settings, "
              "`deploy` the page." % (bad, len(rows)))
    else:
        # The name it really has: the README once said mau5head-AP
        # while this controller was still broadcasting WLED-AP.
        print("\noffline mode is ready: join the access point %r and open\n"
              "  http://4.3.2.1/%s" % (ap.get("ssid"), PAGE))
    return 1 if bad else 0


# ----------------------------------------------------------------------
def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd")

    sub.add_parser("build", help="write the page, no hardware needed")

    s = sub.add_parser("serve", help="serve it against a fake controller")
    s.add_argument("--port", type=int, default=8770)
    s.add_argument("--host", default=None,
                   help="forward the JSON API to a real controller instead "
                        "of the fake one, for a dress rehearsal")
    s.add_argument("--tls", action="store_true",
                   help="serve over https, which is the only way the page "
                        "gets a microphone")

    s = sub.add_parser("deploy", help="upload the page to the controller")
    s.add_argument("--host", default=None)
    s.add_argument("--no-gzip", dest="gzip", action="store_false", default=True)

    s = sub.add_parser("config", help="AP and power limiter")
    s.add_argument("--host", default=None)
    s.add_argument("--apply", action="store_true")
    s.add_argument("--ap-ssid", default=None, help="1 to 32 bytes")
    s.add_argument("--ap-psk", default=None,
                   help="8 to 63 printable ASCII characters, refused "
                        "otherwise; not stored in this repo")

    s = sub.add_parser("standby", help="what the helmet does with no phone")
    s.add_argument("--host", default=None)
    s.add_argument("--fx", default="pacifica",
                   help="one of: " + ", ".join(sorted(STANDBY_FX)))
    s.add_argument("--bri", type=int, default=32)
    s.add_argument("--no-boot", dest="boot", action="store_false", default=True)
    s.add_argument("--apply", action="store_true")

    s = sub.add_parser("check", help="is offline mode actually ready")
    s.add_argument("--host", default=None)

    s = sub.add_parser("songs", help="hand the shows' songs to phones, once")
    s.add_argument("--host", default=None)
    s.add_argument("--port", type=int, default=SONGS_PORT)
    s.add_argument("--dir", action="append", default=None,
                   help="another folder to look for the mp3s in")

    a = ap.parse_args(argv)
    if a.cmd in (None, "build"):
        build()
        return 0
    if a.cmd == "serve":
        import mau5fake
        return mau5fake.serve(port=a.port, host=a.host, tls=a.tls,
                              bind="0.0.0.0" if (a.host or a.tls) else "127.0.0.1")
    # Being away from the helmet is the normal case for most of this
    # work, not an exception, so it reads as a sentence rather than a
    # traceback.
    import mau5wled
    try:
        if a.cmd == "deploy":
            deploy(a.host, gzipped=a.gzip)
            return 0
        if a.cmd == "config":
            return config(a.host, a.apply, a.ap_ssid, a.ap_psk)
        if a.cmd == "standby":
            return standby(a.host, a.fx, a.bri, a.boot, a.apply)
        if a.cmd == "check":
            return check(a.host)
        if a.cmd == "songs":
            return songs(a.host, a.port, a.dir)
    except mau5wled.WLEDError as e:
        print(e)
        print("\n  `python3 mau5offline.py build` and `serve` need no helmet; "
              "this does.")
        return 1
    ap.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
