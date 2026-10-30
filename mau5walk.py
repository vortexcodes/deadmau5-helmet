#!/usr/bin/env python3
"""mau5walk -- walk the chain by hand from your phone, and write down what you see.

A camera that can see every LED at once is awkward to set up, and lighting the
whole helmet to find out where things are will cook it. So instead: light ONE
LED, look at it, tap for the next. When the light jumps somewhere physically
different, you have found a section boundary -- tap "new section", name it,
carry on.

    python3 mau5walk.py --host 4.3.2.1

Then open the printed address on your phone. Both devices need to be on the
same network as the controller.

Why a server rather than a page talking straight to WLED:

  * per-LED control means DDP, and a browser cannot send UDP;
  * WLED reverts to its own effect about 2.5 s after the stream stops, so
    something has to hold the frame;
  * the power limit is enforced here, where a bug in the page cannot get past
    it;
  * the session is recorded as you go, so there is nothing to transcribe.

HEAT.  Everything at full brightness is roughly 18 A on this helmet and will
overheat it. This never lights more than --max-lit LEDs at once (default 120)
and never exceeds --max-bri (default 128/255), both clamped server-side. The
numbers are deliberately conservative; raise them only if you are watching it.

Each session is saved to its own file, data/cal/walk_YYYYmmdd-HHMMSS.json,
and only once something has been recorded in it.  It used to write
data/cal/walk_session.json on every exit: that is the first night's 78-section
hand walk, which the tests, mau5film, mau5verify and mau5shoot all read, and
starting this to look at one strip and pressing ctrl-c replaced it with an
empty session.  To make a new walk the reference, copy it over by hand.
"""

from __future__ import annotations

import argparse
import json
import os
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import numpy as np

import mau5wled

HERE = os.path.dirname(os.path.abspath(__file__))
PAGE = os.path.join(HERE, "remote", "walk.html")
# The first night's walk: read by everything that checks the map against
# an instrument that shares nothing with the cameras.  Never written here.
REFERENCE = "walk_session.json"


def session_path(outdir, when=None):
    """This session's own file, named for when it started."""
    return os.path.join(outdir, "walk_%s.json"
                        % time.strftime("%Y%m%d-%H%M%S", time.localtime(when)))


def save_session(walk, path):
    """Write the session if anything was recorded; return the path or None.

    An empty session -- started to look at something, then ctrl-c --
    is nothing worth a file.  And whatever path it is given, it will
    not write over the reference walk.
    """
    doc = walk.export()
    if not doc["sections"] and not doc["note"]:
        return None
    if os.path.basename(path) == REFERENCE:
        raise ValueError("%s is the reference walk; save this session elsewhere"
                         % path)
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, indent=1)
    os.replace(tmp, path)
    return path


class Walk:
    """The live state: where we are in the chain, and what has been named."""

    def __init__(self, pix, count, max_lit=120, max_bri=128, idle_blank=600):
        self.pix = pix
        self.count = count
        self.max_lit = int(max_lit)
        self.max_bri = int(max_bri)
        self.idle_blank = idle_blank
        self.lock = threading.Lock()

        self.index = 0
        self.mode = "single"          # single | trail | section
        self.trail = 12
        self.color = [255, 255, 255]
        self.bri = min(96, self.max_bri)
        self.sections = []            # [{name, start, end}]
        self.correct = False          # send raw, so colours stay diagnostic
        self.last_touch = time.time()
        self.note = ""
        self.show_range = None        # set while photographing a finished section
        self._stop = threading.Event()
        threading.Thread(target=self._pump, daemon=True).start()

    # -- what should be lit right now -------------------------------------
    def lit_indices(self):
        if self.show_range:
            a, b = self.show_range
            idx = [i for i in range(a, b + 1) if 0 <= i < self.count]
            return idx[-self.max_lit:] if len(idx) > self.max_lit else idx
        if self.mode == "single":
            idx = [self.index]
        elif self.mode == "trail":
            idx = list(range(max(0, self.index - self.trail + 1), self.index + 1))
        else:                                   # whole current section so far
            start = self.sections[-1]["start"] if self.sections else 0
            idx = list(range(start, self.index + 1))
        idx = [i for i in idx if 0 <= i < self.count]
        if len(idx) > self.max_lit:             # hard cap, most recent win
            idx = idx[-self.max_lit:]
        return idx

    def frame(self):
        buf = np.zeros((self.count, 3), np.uint8)
        if time.time() - self.last_touch > self.idle_blank:
            return buf                          # nobody is looking; stop heating it
        k = min(self.bri, self.max_bri) / 255.0
        col = [int(c * k) for c in self.color]
        for i in self.lit_indices():
            buf[i] = col
        return buf

    def _pump(self):
        while not self._stop.is_set():
            try:
                self.pix.send(self.frame(), correct=self.correct)
            except Exception:
                pass
            time.sleep(0.05)                    # 20 Hz keepalive

    # -- edits -------------------------------------------------------------
    def touch(self):
        self.last_touch = time.time()

    def step(self, d):
        with self.lock:
            self.show_range = None
            self.index = max(0, min(self.count - 1, self.index + int(d)))
            self.touch()

    def goto(self, i):
        with self.lock:
            self.show_range = None
            self.index = max(0, min(self.count - 1, int(i)))
            self.touch()

    def new_section(self, name):
        """The current LED is the first of a new section."""
        with self.lock:
            if self.sections:
                self.sections[-1]["end"] = max(self.sections[-1]["start"],
                                               self.index - 1)
            self.sections.append(dict(name=name or "section_%d" % (len(self.sections) + 1),
                                      start=self.index, end=self.index))
            self.touch()

    def close_section(self):
        with self.lock:
            if self.sections:
                self.sections[-1]["end"] = self.index
            self.touch()

    def drop_section(self):
        with self.lock:
            if self.sections:
                self.sections.pop()
            self.touch()

    def rename(self, name):
        with self.lock:
            if self.sections and name:
                self.sections[-1]["name"] = name

    def state(self):
        lit = self.lit_indices()
        return dict(index=self.index, count=self.count, mode=self.mode,
                    trail=self.trail, color=self.color, bri=self.bri,
                    max_bri=self.max_bri, max_lit=self.max_lit,
                    lit=len(lit), correct=self.correct, note=self.note,
                    show=list(self.show_range) if self.show_range else None,
                    sections=self.sections,
                    capped=len(lit) >= self.max_lit,
                    watts=round(len(lit) * 0.0192 * 12 * (min(self.bri, self.max_bri) / 255.0), 1))

    def export(self):
        s = [dict(x) for x in self.sections]
        if s:
            s[-1]["end"] = max(s[-1]["start"], self.index)
        return dict(count=self.count, saved=time.strftime("%Y-%m-%dT%H:%M:%S"),
                    sections=s, note=self.note)


def make_handler(walk, path):
    """`path` is this session's own file (session_path)."""
    def save():
        fn = save_session(walk, path)
        return {"saved": fn} if fn else {"saved": None,
                                         "why": "nothing recorded yet"}

    class H(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"

        def log_message(self, *a):
            pass

        def _send(self, body, ctype="application/json", code=200):
            if isinstance(body, (dict, list)):
                body = json.dumps(body).encode()
            elif isinstance(body, str):
                body = body.encode()
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            p = self.path.split("?")[0]
            if p in ("/", "/index.html", "/walk.html"):
                try:
                    with open(PAGE, "rb") as fh:
                        return self._send(fh.read(), "text/html; charset=utf-8")
                except OSError:
                    return self._send("walk.html missing", "text/plain", 500)
            if p == "/api/state":
                return self._send(walk.state())
            if p == "/api/export":
                return self._send(walk.export())
            if p == "/api/save":
                # still answered on GET because remote/walk.html's save
                # button uses it; it only ever writes this session's file
                return self._send(save())
            return self._send({"error": "no route " + p}, code=404)

        def do_POST(self):
            n = int(self.headers.get("Content-Length", 0))
            try:
                body = json.loads(self.rfile.read(n) or b"{}")
            except ValueError:
                body = {}
            p = self.path.split("?")[0]
            if p == "/api/step":
                walk.step(body.get("d", 1))
            elif p == "/api/goto":
                walk.goto(body.get("i", 0))
            elif p == "/api/mode":
                walk.mode = body.get("mode", "single")
                walk.trail = max(1, int(body.get("trail", walk.trail)))
                walk.touch()
            elif p == "/api/color":
                c = body.get("color", [255, 255, 255])
                walk.color = [max(0, min(255, int(x))) for x in c][:3]
                walk.touch()
            elif p == "/api/bri":
                walk.bri = max(1, min(walk.max_bri, int(body.get("bri", 96))))
                walk.touch()
            elif p == "/api/section":
                a = body.get("action")
                if a == "new":
                    walk.new_section(body.get("name", ""))
                elif a == "close":
                    walk.close_section()
                elif a == "drop":
                    walk.drop_section()
                elif a == "rename":
                    walk.rename(body.get("name", ""))
            elif p == "/api/show":
                if body.get("clear"):
                    walk.show_range = None
                else:
                    walk.show_range = (int(body.get("start", 0)),
                                       int(body.get("end", 0)))
                walk.touch()
            elif p == "/api/note":
                walk.note = str(body.get("note", ""))[:400]
            elif p == "/api/correct":
                walk.correct = bool(body.get("on"))
            elif p == "/api/save":
                return self._send(save())
            else:
                return self._send({"error": "no route " + p}, code=404)
            return self._send(walk.state())
    return H


lan_ip = mau5wled.lan_ip      # the LAN address, not a VPN tunnel's


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter,
                                 epilog=__doc__)
    ap.add_argument("--host", help="WLED ip or hostname "
                                   "(default: find it automatically)")
    ap.add_argument("--count", type=int, help="LED count (default: ask WLED)")
    ap.add_argument("--port", type=int, default=8750, help="port to serve on")
    ap.add_argument("--max-lit", type=int, default=120,
                    help="never light more than this many at once")
    ap.add_argument("--max-bri", type=int, default=128,
                    help="never exceed this brightness (0-255)")
    ap.add_argument("--idle-blank", type=float, default=600,
                    help="blank after this many seconds of no input")
    ap.add_argument("--out", default=os.path.join(HERE, "data", "cal"))
    a = ap.parse_args(argv)

    w = mau5wled.find_one(a.host)
    print(w.describe())
    n = a.count or w.count
    if not n:
        raise SystemExit("LED count unknown -- pass --count")
    w.realtime(True, brightness=255)      # our own cap does the limiting
    pix = mau5wled.Pixels(w, n)
    walk = Walk(pix, n, a.max_lit, a.max_bri, a.idle_blank)
    fn = session_path(a.out)

    srv = ThreadingHTTPServer(("0.0.0.0", a.port), make_handler(walk, fn))
    url = "http://%s:%d/" % (lan_ip(), a.port)
    full = n * 0.0192 * 12
    print("\n  open this on your phone:   %s\n" % url)
    print("  %d LEDs.  Lighting all of them at full would be about %.0f W (%.1f A"
          " at 12 V)." % (n, full, full / 12))
    print("  Capped at %d lit and brightness %d/255 -> at most about %.0f W.\n"
          % (a.max_lit, a.max_bri,
             a.max_lit * 0.0192 * 12 * a.max_bri / 255.0))
    try:
        for r in w.headroom():
            if r["fraction"] is not None:
                print("  Controller limiter: %.0f%% of full white (%d mA on pin %s)."
                      % (r["fraction"] * 100, r["max_ma"], r["pin"]))
    except Exception:
        pass
    print("  this session saves to %s" % os.path.relpath(fn, HERE))
    print("  ctrl-c to stop (the helmet blanks on exit)")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\nstopping")
    finally:
        walk._stop.set()
        time.sleep(0.2)
        try:
            pix.clear()
        except Exception:
            pass
        if save_session(walk, fn):
            print("session saved -> %s" % fn)
        else:
            print("nothing recorded, nothing written")


if __name__ == "__main__":
    main()
