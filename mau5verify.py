#!/usr/bin/env python3
"""mau5verify -- light targeted patterns so photos can settle the walk.

The walk of the chain lines up with the CAD to 57 of 68 strips.  The
eleven that disagree are not scattered: they sit in three clusters, and
each cluster has the right *total*, which is what a boundary tapped a
beat early looks like.  Guessing which side is right from the numbers
alone is not possible -- the chain cannot tell you where it is in space.
A photograph can.

So each check here lights a pattern designed to make exactly one
question visually obvious, and says what to look for.  Nothing is
inferred; you look, and tell me.

Same heat rules as the walk: nothing exceeds the lit cap or the
brightness cap, both applied to the pixel data before it is sent.

    python3 mau5verify.py              # find the controller, serve the page
    python3 mau5verify.py --list       # print the checks and exit
"""

from __future__ import annotations

import argparse
import json
import os
import threading
import time
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler

import numpy as np

import mau5map
import mau5wled

HERE = os.path.dirname(os.path.abspath(__file__))

RED, GRN, BLU, WHT, YEL, CYN = ((255, 0, 0), (0, 255, 0), (0, 0, 255),
                                (255, 255, 255), (255, 200, 0), (0, 255, 255))


def _regions():
    """Each region of the map as (lo, hi), both inclusive, in chain order.

    The ear checks used to be written as literal indices, and the
    literals outlived what they described: one segment cut off the near
    rim on 2026-10-29 moved every ear LED after it down by one, and the
    'first rim' of the colour-order check had been on ear1's tubes all
    along.  The map is where the regions are kept up to date, so they
    are read from it.  A region relabelled in adjust.json can come out
    in two pieces; the longest piece is the one used.
    """
    runs = []
    for r in mau5map.load():
        if runs and runs[-1][0] == r["region"] and runs[-1][2] == r["index"] - 1:
            runs[-1][2] = r["index"]
        else:
            runs.append([r["region"], r["index"], r["index"]])
    best = {}
    for name, lo, hi in runs:
        if name not in best or hi - lo > best[name][1] - best[name][0]:
            best[name] = (lo, hi)
    return dict(sorted(best.items(), key=lambda kv: kv[1][0]))


def _middle(lo, hi, n=11):
    """`n` LEDs from the middle of lo..hi, clear of both ends, where a
    boundary that is out by one would otherwise land in the span."""
    k = min(n, hi - lo + 1)
    a = (lo + hi + 1 - k) // 2
    return a, a + k - 1


def build_checks(session):
    """The questions worth asking, as lit patterns.

    Every span is pure red, green or blue and no two spans in a check
    share a channel.  That is not decoration: the camera's difference
    image can then be split per channel, and each span's position read
    off directly instead of guessed at from a photograph where white
    spans and sensor saturation have smeared everything together.

    Spans are (first, last, colour, label), both ends inclusive.  The
    shell checks are about the walk and keep its indices, none of which
    the cut moved; the ear spans come from the map's regions.
    """
    # Nothing may run past the end of either the walk or the map.  The
    # walk was taken before the cut and still ends at 622, so on its own
    # it let through two indices that have nothing behind them.
    last = min(max(x["end"] for x in session["sections"]),
               mau5map.TOTAL_N - 1)
    reg = _regions()
    C = []

    C.append(dict(
        id="shell-end", title="Where does the shell stop?",
        look="RED is the walk's last shell strip, GREEN the single "
             "disputed LED, BLUE what follows.",
        settles="Whether the shell is 399 LEDs (green sits on the end of "
                "the red strip) or 398 (green is off with the blue).",
        spans=[(387, 397, RED, "walk's last shell strip"),
               (398, 398, GRN, "disputed LED"),
               (399, 404, BLU, "what follows")]))

    C.append(dict(
        id="group33", title="The one missing LED",
        look="Is GREEN on the end of the RED strip, or the start of the "
             "BLUE one?",
        settles="Group 33: walk says 11 LEDs, CAD says 12. The only "
                "mismatch that does not balance inside its cluster.",
        spans=[(124, 134, RED, "walk's group 33"),
               (135, 135, GRN, "CAD says this belongs with it"),
               (136, 144, BLU, "next strip")]))

    for tag, base in (("left", 173), ("right", 304)):
        C.append(dict(
            id="visor-%s" % tag, title="Visor cluster, %s" % tag,
            look="RED is one LED, GREEN is four, BLUE is one. Is RED "
                 "isolated and BLUE attached to GREEN, or the other way "
                 "round?",
            settles="Walk reads this cluster 1,5,5,3 -- so RED stands "
                    "alone and BLUE continues GREEN. The CAD reads it "
                    "5,1,3,5 -- so RED starts the strip GREEN continues, "
                    "and BLUE is the lone one.",
            spans=[(base, base, RED, "first"),
                   (base + 1, base + 4, GRN, "next four"),
                   (base + 5, base + 5, BLU, "sixth")]))

    C.append(dict(
        id="bottom-pairs", title="Bottom band: is 40 paired left or right?",
        look="Is GREEN on the same little strip as RED, or as BLUE?",
        settles="Groups 8-9: walk says 3+1, CAD says 2+2.",
        spans=[(38, 39, RED, "pair"), (40, 40, GRN, "disputed"),
               (41, 41, BLU, "next")]))

    C.append(dict(
        id="colour-order", title="Colour order across the build",
        look="Every one of these is being sent PURE RED. Any that come "
             "back green or blue are wired in a different channel order "
             "from the bus setting.",
        settles="Which index ranges need a channel permutation.",
        # One span from the middle of every region, so each rim -- the
        # span strips.json says is wired differently -- is lit.
        spans=[_middle(lo, hi) + (RED, name.replace("_", " "))
               for name, (lo, hi) in reg.items()]))

    t1, r1 = reg["ear1_tubes"], reg["ear1_rim"]
    r2, t2 = reg["ear2_rim"], reg["ear2_tubes"]
    C.append(dict(
        id="ears-a", title="Ear grouping, first half",
        look="RED and GREEN, on the first ear in the chain.",
        settles="Whether %d-%d splits into tubes then rim at %d, as the "
                "map has it." % (t1[0], r1[1], r1[0]),
        spans=[(t1[0], t1[1], RED, "tubes?"), (r1[0], r1[1], GRN, "rim?")]))

    C.append(dict(
        id="ears-b", title="Ear grouping, second half",
        look="RED and GREEN, on the second ear.",
        settles="Whether %d-%d is rim then tubes from %d, as the map has "
                "it." % (r2[0], t2[1], t2[0]),
        spans=[(r2[0], r2[1], RED, "rim?"), (t2[0], t2[1], GRN, "tubes?")]))

    C.append(dict(
        id="bottom-mirror", title="Symmetry check",
        look="These two should sit the same distance either side of the "
             "centre line along the bottom.",
        settles="Validates the whole alignment against the CAD.",
        spans=[(0, 5, RED, "group 0"), (88, 93, GRN, "group 29")]))

    for c in C:
        bad = [sp for sp in c["spans"] if sp[1] > last]
        if bad:
            raise SystemExit("check %r runs past the chain (last index "
                             "%d): %s" % (c["id"], last, bad))
        chans = [tuple(sp[2]) for sp in c["spans"]]
        if c["id"] != "colour-order" and len(set(chans)) != len(chans):
            raise SystemExit("check %r reuses a channel, so the difference "
                             "image cannot separate its spans" % c["id"])
    return C


class Verify:
    """Holds the selected check and streams it, under the heat caps."""

    def __init__(self, pix, count, checks, max_lit, max_bri, idle_blank):
        self.pix, self.count, self.checks = pix, count, checks
        self.max_lit, self.max_bri = max_lit, max_bri
        self.idle_blank = idle_blank
        self.sel = None
        self.touched = time.monotonic()
        self.lock = threading.Lock()
        self.stop = False
        threading.Thread(target=self._pump, daemon=True).start()

    def frame(self):
        buf = np.zeros((self.count, 3), np.uint8)
        if self.sel is None:
            return buf, 0, False
        if time.monotonic() - self.touched > self.idle_blank:
            return buf, 0, False
        lit = 0
        capped = False
        for lo, hi, col, _ in self.checks[self.sel]["spans"]:
            lo, hi = max(0, lo), min(self.count - 1, hi)
            if hi < lo:
                continue
            room = self.max_lit - lit
            if room <= 0:
                capped = True
                break
            if hi - lo + 1 > room:
                hi = lo + room - 1
                capped = True
            buf[lo:hi + 1] = col
            lit += hi - lo + 1
        if self.max_bri < 255:
            buf = (buf.astype(np.uint16) * self.max_bri // 255).astype(np.uint8)
        return buf, lit, capped

    def state(self):
        _, lit, capped = self.frame()
        return {"selected": self.sel, "lit": lit, "capped": capped,
                "max_lit": self.max_lit, "max_bri": self.max_bri,
                "watts": round(lit * 0.0192 * 12 * self.max_bri / 255.0, 1),
                "checks": [{"id": c["id"], "title": c["title"],
                            "look": c["look"], "settles": c["settles"],
                            "spans": [{"lo": s[0], "hi": s[1],
                                       "color": list(s[2]), "label": s[3]}
                                      for s in c["spans"]]}
                           for c in self.checks]}

    def _pump(self):
        while not self.stop:
            with self.lock:
                buf, _, _ = self.frame()
            try:
                self.pix.send(buf, correct=False)
            except Exception:
                pass
            time.sleep(0.05)


def make_handler(v):
    class H(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def _send(self, obj, code=200, ctype="application/json"):
            body = (obj if isinstance(obj, bytes)
                    else json.dumps(obj).encode())
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            if self.path in ("/", "/index.html"):
                p = os.path.join(HERE, "remote", "verify.html")
                return self._send(open(p, "rb").read(), ctype="text/html")
            if self.path == "/api/state":
                return self._send(v.state())
            self._send({"error": "no route"}, code=404)

        def do_POST(self):
            n = int(self.headers.get("Content-Length") or 0)
            body = json.loads(self.rfile.read(n) or b"{}")
            if self.path == "/api/select":
                i = body.get("i")
                v.sel = None if i is None else max(0, min(len(v.checks) - 1, int(i)))
                v.touched = time.monotonic()
                return self._send(v.state())
            self._send({"error": "no route"}, code=404)
    return H


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter,
                                 epilog=__doc__)
    ap.add_argument("--host", help="WLED ip (default: find it)")
    ap.add_argument("--count", type=int)
    ap.add_argument("--port", type=int, default=8751)
    ap.add_argument("--max-lit", type=int, default=120)
    ap.add_argument("--max-bri", type=int, default=128)
    ap.add_argument("--idle-blank", type=float, default=900)
    ap.add_argument("--session", default=os.path.join(HERE, "data", "cal",
                                                      "walk_session.json"))
    ap.add_argument("--list", action="store_true", help="print and exit")
    a = ap.parse_args(argv)

    session = json.load(open(a.session))
    checks = build_checks(session)

    if a.list:
        for i, c in enumerate(checks):
            total = sum(s[1] - s[0] + 1 for s in c["spans"])
            print("%2d  %-42s %3d leds" % (i, c["title"], total))
            for lo, hi, col, lab in c["spans"]:
                print("      %4d..%-4d  %-16s %s" % (lo, hi, lab, col))
        return

    w = mau5wled.find_one(a.host)
    print(w.describe())
    n = a.count or w.count
    w.realtime(True, brightness=255)
    pix = mau5wled.Pixels(w, n)
    v = Verify(pix, n, checks, a.max_lit, a.max_bri, a.idle_blank)

    srv = ThreadingHTTPServer(("0.0.0.0", a.port), make_handler(v))
    print("\n  open this on your phone:   http://%s:%d/\n"
          % (mau5wled.lan_ip(), a.port))
    print("  %d checks.  Capped at %d lit, brightness %d/255."
          % (len(checks), a.max_lit, a.max_bri))
    print("  ctrl-c to stop (the helmet blanks on exit)")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        v.stop = True
        time.sleep(0.15)
        try:
            pix.clear()
        except Exception:
            pass
        print("\n  blanked.")


if __name__ == "__main__":
    main()
