#!/usr/bin/env python3
"""mau5hue -- find LEDs whose colour order is wrong, by asking them.

A strip wired GRB where the bus is RGB shows red as green.  The
correction is already measured and stored in data/cal/strips.json, but
a span whose boundaries are slightly off leaves a few LEDs at the edge
still swapped, and those are exactly the ones nobody notices until the
helmet is lit and one corner of an ear is the wrong colour.

The test needs no camera calibration and no idea where anything is.
Light a set of LEDs in pure red and photograph: if green appears, the
set contains a swapped LED.  That is a yes/no question, so the search
can halve -- blocks first, then the LEDs inside any block that
answered yes.

    python3 mau5hue.py                     # the ears
    python3 mau5hue.py --lo 0 --hi 398     # the shell
    python3 mau5hue.py --apply             # write the fix to strips.json
"""

from __future__ import annotations

import argparse
import json
import os
import time

import numpy as np
from PIL import Image

import mau5eye
import mau5wled

HERE = os.path.dirname(os.path.abspath(__file__))
STRIPS = os.path.join(HERE, "data", "cal", "strips.json")
OUT = os.path.join(HERE, "data", "cal", "hue")


def _shot(stream, buf, eye_port, out, dark, tag):
    stream.show(buf)
    t0 = time.time()
    time.sleep(0.35)
    p = mau5eye.shot(os.path.join(out, tag + ".jpg"), port=eye_port,
                     after=t0, wait=15.0)
    a = np.asarray(Image.open(p).convert("RGB"), np.float32)
    d = np.clip(a - dark, 0, 255)
    m = d.max(2) > 28
    if m.sum() < 12:
        return None
    return np.array([float(d[..., c][m].sum()) for c in range(3)])


def measure(stream, idx, count, level, eye_port, out, dark, tag):
    """Ask the same LEDs for red, then for green, and compare.

    Reading one red frame and asking whether it looks green sounds
    simpler and does not work: the camera is free-running, and its
    white balance moves enough between frames to turn the answer over.
    Two passes over the same LEDs under near-identical conditions
    cancel that.  A correct LED emits more red when asked for red than
    when asked for green; a swapped one does the opposite, and the
    comparison does not care what the camera thinks neutral is.

    Returns (red asked -> red seen, green asked -> red seen).
    """
    i = np.asarray(idx, int)
    br = np.zeros((count, 3), np.uint8); br[i, 0] = level
    bg = np.zeros((count, 3), np.uint8); bg[i, 1] = level
    a = _shot(stream, br, eye_port, out, dark, tag + "r")
    b = _shot(stream, bg, eye_port, out, dark, tag + "g")
    if a is None or b is None:
        return 0.0, 0.0
    return float(a[0]), float(b[0])


def swapped(red_seen, green_seen, ratio=1.25):
    """Asking for green produced more red light than asking for red did."""
    return green_seen > red_seen * ratio and max(red_seen, green_seen) > 2000


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--host", default=None)
    ap.add_argument("--lo", type=int, default=399)
    ap.add_argument("--hi", type=int, default=621)
    ap.add_argument("--block", type=int, default=8)
    ap.add_argument("--level", type=int, default=90)
    ap.add_argument("--eye-port", type=int, default=8752)
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--apply", action="store_true",
                    help="rewrite strips.json with what was found")
    a = ap.parse_args(argv)
    os.makedirs(a.out, exist_ok=True)

    w = mau5wled.WLED(a.host) if a.host else (mau5wled.scan_subnet() or [None])[0]
    if w is None:
        raise SystemExit("no controller found")
    w.realtime(True, brightness=255)
    count = w.count or 622
    # No colour correction: the whole point is to see the strips raw.
    # The guard stays on -- this is a handful of LEDs and well inside it.
    pix = mau5wled.Pixels(w, count, strips=False)
    stream = mau5wled.Streamer(pix)

    bad = []
    try:
        stream.dark(); time.sleep(0.5)
        p = mau5eye.shot(os.path.join(a.out, "dark.jpg"), port=a.eye_port,
                         after=time.time())
        dark = np.asarray(Image.open(p).convert("RGB"), np.float32)

        blocks = [list(range(s, min(s + a.block, a.hi + 1)))
                  for s in range(a.lo, a.hi + 1, a.block)]
        print("scanning %d..%d in %d blocks of %d" % (a.lo, a.hi, len(blocks), a.block))
        suspect = []
        for b in blocks:
            r, g = measure(stream, b, count, a.level, a.eye_port, a.out, dark,
                           "b%04d" % b[0])
            hit = swapped(r, g)
            print("  %3d-%-3d  askR->red %8.0f   askG->red %8.0f  %s"
                  % (b[0], b[-1], r, g, "SWAP IN HERE" if hit else ""))
            if hit:
                suspect += b
        if suspect:
            print("\nnarrowing %d LEDs one at a time" % len(suspect))
            for i in suspect:
                r, g = measure(stream, [i], count, min(255, a.level * 2),
                               a.eye_port, a.out, dark, "i%04d" % i)
                hit = swapped(r, g)
                print("  %3d  askR->red %7.0f  askG->red %7.0f  %s"
                      % (i, r, g, "SWAPPED" if hit else "ok"))
                if hit:
                    bad.append(i)
    finally:
        stream.stop()
        try:
            w.off()
        except Exception:
            pass

    runs = []
    for i in sorted(bad):
        if runs and i == runs[-1][1] + 1:
            runs[-1][1] = i
        else:
            runs.append([i, i])
    print("\nswapped runs: %s" % (runs or "none"))

    if a.apply and runs:
        cur = json.load(open(STRIPS)) if os.path.exists(STRIPS) else {"count": count, "strips": []}
        keep = [s for s in cur.get("strips", [])
                if not any(s["start"] >= lo and s["start"] + s["count"] - 1 <= hi
                           for lo, hi in runs)]
        for lo, hi in runs:
            keep.append({"start": lo, "count": hi - lo + 1, "order": "GRB",
                         "name": "measured by mau5hue %s" % time.strftime("%Y-%m-%d")})
        keep.sort(key=lambda s: s["start"])
        json.dump({"count": count, "strips": keep}, open(STRIPS, "w"), indent=1)
        print("wrote %s" % STRIPS)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
