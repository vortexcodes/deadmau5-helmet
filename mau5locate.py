#!/usr/bin/env python3
"""mau5locate -- find out where each LED actually is, one at a time.

The shell's positions come from the CAD and the camera agrees with
them.  The ears do not: they were rebuilt by hand after the CAD was
drawn, and the parametric stand-in for them is measurably wrong -- a
bar swept vertically correlates with image height at r=-0.87 on the
head but only -0.36 and -0.45 on the ears.

Rather than guess better, this measures.  Each LED is lit alone, at a
low level so the diffuser's bloom stays small, and its weighted
centroid in the camera is recorded.  Centroids proved stable to about
two pixels across a sevenfold brightness range, which is far finer
than the error being chased.

Slow and dull -- about three seconds an LED -- but it only has to be
right once, and it writes as it goes so an interrupted run resumes.

    python3 mau5locate.py --from 399 --to 622
    python3 mau5locate.py --resume
"""

from __future__ import annotations

import argparse
import csv
import os
import time

import numpy as np
from PIL import Image

import mau5eye
import mau5power as P
import mau5wled

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "data", "cal", "led_positions.csv")
FIELDS = ["index", "cx", "cy", "peak", "px_count", "w", "h", "level"]


def load(path=OUT):
    if not os.path.exists(path):
        return {}
    out = {}
    for r in csv.DictReader(open(path)):
        out[int(r["index"])] = {k: (int(r[k]) if k in ("index", "px_count")
                                    else float(r[k])) for k in FIELDS}
    return out


def save(rows, path=OUT):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", newline="") as f:
        wri = csv.DictWriter(f, fieldnames=FIELDS)
        wri.writeheader()
        for i in sorted(rows):
            wri.writerow(rows[i])
    os.replace(tmp, path)


def centroid(diff, frac=0.5, floor=10.0):
    pk = float(diff.max())
    if pk < floor:
        return None
    m = diff > pk * frac
    if m.sum() < 4:
        return None
    ys, xs = np.where(m)
    w = diff[m].astype(float)
    return {"cx": float((xs * w).sum() / w.sum()),
            "cy": float((ys * w).sum() / w.sum()),
            "peak": pk, "px_count": int(m.sum()),
            "w": float(np.ptp(xs) + 1), "h": float(np.ptp(ys) + 1)}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter,
                                 epilog=__doc__)
    ap.add_argument("--host", default=None)
    ap.add_argument("--count", type=int, default=622)
    ap.add_argument("--from", dest="lo", type=int, default=399)
    ap.add_argument("--to", dest="hi", type=int, default=622)
    ap.add_argument("--level", type=int, default=45,
                    help="per-channel drive; low keeps the bloom small")
    ap.add_argument("--settle", type=float, default=0.75)
    ap.add_argument("--resume", action="store_true", help="skip ones already measured")
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--eye-port", type=int, default=8752)
    a = ap.parse_args(argv)

    rows = load(a.out) if a.resume else {}
    todo = [i for i in range(a.lo, a.hi + 1) if i not in rows]
    if not todo:
        print("nothing to do (%d already measured)" % len(rows)); return

    w = mau5wled.find_one(a.host)
    print(w.describe())
    w._post("/json/state", {"on": True, "bri": 255})
    w.realtime(True, brightness=255)
    # one LED at a time is a handful of milliamps; the ceiling is only
    # here so a bug cannot turn this into a full-helmet blast
    probe = P.PowerGuard(a.count, [P.Region("all", 0, a.count - 1, ceiling=255,
                                            budget_ma=120, shed=1)], budget_ma=140)
    st = mau5wled.Streamer(mau5wled.Pixels(w, a.count, guard=probe), fps=20)
    t0 = time.time()
    misses = []
    try:
        t = time.time(); st.dark(); time.sleep(1.5)
        ref = np.asarray(Image.open(mau5eye.shot(
            os.path.join(HERE, "data", "cal", "_locate_dark.jpg"),
            port=a.eye_port, wait=30, after=t + 0.7)).convert("L")).astype(np.float32)

        for n, led in enumerate(todo):
            buf = np.zeros((a.count, 3), np.uint8)
            buf[led] = (a.level, a.level, a.level)
            t = time.time(); st.show(buf); time.sleep(a.settle)
            f = mau5eye.shot(os.path.join(HERE, "data", "cal", "_locate.jpg"),
                             port=a.eye_port, wait=30, after=t + 0.4)
            d = np.clip(np.asarray(Image.open(f).convert("L")).astype(np.float32) - ref,
                        0, 255)
            c = centroid(d)
            if c is None:
                misses.append(led)
            else:
                c["index"] = led; c["level"] = a.level
                rows[led] = c
            if n % 10 == 9 or n == len(todo) - 1:
                save(rows, a.out)
                done = n + 1
                rate = (time.time() - t0) / done
                print("  %4d/%d  led %3d  %s  %.1fs/led, %.0fs left"
                      % (done, len(todo), led,
                         "miss" if c is None else "(%6.1f,%6.1f) %3dpx"
                         % (c["cx"], c["cy"], c["px_count"]),
                         rate, rate * (len(todo) - done)))
    finally:
        st.stop()
        save(rows, a.out)
    print("\nmeasured %d, missed %d %s" % (len(rows), len(misses), misses[:12]))
    print("wrote %s" % a.out)


if __name__ == "__main__":
    main()
