#!/usr/bin/env python3
"""mau5locate -- find out where each LED actually is, one at a time.

Each LED is lit alone, at a low level so the diffuser's bloom stays
small, and its weighted centroid in the camera is recorded.  That is
all this does.  Turning centroids into a map is mau5slots.py's job: it
needs two runs from two camera positions, and it uses them to decide
which CAD slot each LED is in rather than to place it directly.

Centroids proved stable to about two pixels across a sevenfold
brightness range, which is finer than the slot spacing by a factor of
seven.

Slow and dull -- about three seconds an LED -- but it only has to be
right once, and it writes as it goes so an interrupted run resumes.

    python3 mau5locate.py --from 398 --to 620
    python3 mau5locate.py --resume
"""

from __future__ import annotations

import argparse
import csv
import math
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


def similarity(src, dst):
    """The rotation, scale and shift that best carries src onto dst.

    Two points are enough -- four equations, four unknowns -- and
    three are better.  Nothing here solves for perspective: a camera
    that has slipped a little is, to the accuracy that matters over a
    few hundred pixels, a picture that has moved, turned slightly and
    changed size slightly.  A full homography from three points is
    not determined anyway.
    """
    src = np.asarray(src, float)
    dst = np.asarray(dst, float)
    mu_s, mu_d = src.mean(0), dst.mean(0)
    S, D = src - mu_s, dst - mu_d
    cov = (D.T @ S) / len(src)
    U, sv, Vt = np.linalg.svd(cov)
    R = U @ Vt
    if np.linalg.det(R) < 0:
        U = U.copy(); U[:, -1] *= -1
        R = U @ Vt
    var = float((S ** 2).sum()) / len(src)
    sc = float(sv.sum() / var) if var > 1e-9 else 1.0
    t = mu_d - sc * (R @ mu_s)
    return sc, R, t


def apply_sim(sim, pt):
    sc, R, t = sim
    return tuple(sc * (R @ np.asarray(pt, float)) + t)


def blend(a, b, k):
    """Part way between two similarities, by angle rather than matrix."""
    sa, Ra, ta = a
    sb, Rb, tb = b
    ang_a = math.atan2(Ra[1, 0], Ra[0, 0])
    ang_b = math.atan2(Rb[1, 0], Rb[0, 0])
    d = (ang_b - ang_a + math.pi) % (2 * math.pi) - math.pi
    ang = ang_a + d * k
    c, s_ = math.cos(ang), math.sin(ang)
    return (sa + (sb - sa) * k, np.array([[c, -s_], [s_, c]]),
            ta + (tb - ta) * k)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter,
                                 epilog=__doc__)
    ap.add_argument("--host", default=None)
    ap.add_argument("--count", type=int, default=621)
    ap.add_argument("--from", dest="lo", type=int, default=398)
    ap.add_argument("--to", dest="hi", type=int, default=620)
    ap.add_argument("--level", type=int, default=45,
                    help="per-channel drive; low keeps the bloom small")
    ap.add_argument("--settle", type=float, default=0.75)
    ap.add_argument("--resume", action="store_true", help="skip ones already measured")
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--eye-port", type=int, default=8752)
    ap.add_argument("--fiducial", type=int, default=25,
                    help="re-measure the first LED every N, to catch the "
                         "camera being nudged mid-run")
    ap.add_argument("--track", action="store_true",
                    help="follow the camera instead of stopping when it "
                         "moves: several fiducials, re-measured as the run "
                         "goes, and every centroid carried back into the "
                         "frame the run started in")
    ap.add_argument("--fid-leds", default=None,
                    help="which LEDs to track by, comma separated.  The "
                         "default spreads three across the range.")
    ap.add_argument("--max-drift", type=float, default=6.0,
                    help="stop if the fiducial moves this many pixels")
    a = ap.parse_args(argv)

    rows = load(a.out) if a.resume else {}
    # --to is inclusive, but it still cannot exceed the chain: asking for
    # index 622 of 622 lit nothing and took the run down at the last LED.
    hi = min(a.hi, a.count - 1)
    todo = [i for i in range(a.lo, hi + 1) if i not in rows]
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
    drift_log = []
    try:
        t = time.time(); st.dark(); time.sleep(1.5)
        ref = np.asarray(Image.open(mau5eye.shot(
            os.path.join(HERE, "data", "cal", "_locate_dark.jpg"),
            port=a.eye_port, wait=30, after=t + 0.7)).convert("L")).astype(np.float32)

        # A fiducial, re-measured every so often.  This run takes an
        # hour, and if the camera or the helmet is nudged halfway
        # through, the first half and the second half are in different
        # frames and the file silently becomes two incompatible sets.
        # That happened: fitting on LEDs 0-199 and testing on 200-398
        # gave 141 px of error where fitting on even and testing on odd
        # gave 38, which is the signature of a move rather than noise.
        # Nothing downstream could tell, and the ear map derived from it
        # was wrong by a third of the frame.
        fid_led = a.lo
        fid0 = None
        drift = []
        # Tracking mode.  The abort above is the right answer when the
        # camera is meant to be still and something knocked it; it is
        # the wrong answer when the camera simply will not stay put,
        # which is what a phone propped against a box does.  Measured
        # on this one: 213 px of drift in five minutes, steadily.  So
        # several fiducials are re-measured as the run goes and every
        # centroid is carried back into the frame the run started in.
        if a.fid_leds:
            fids = [int(v) for v in a.fid_leds.split(",") if v.strip()]
        else:
            span = max(hi - a.lo, 3)
            fids = sorted({a.lo, a.lo + span // 3, a.lo + 2 * span // 3})
        fids = [f for f in fids if a.lo <= f <= hi]
        base = {}                 # fiducial -> its position at the start
        marks = []                # (n, similarity carrying now -> the start)
        raw = {}                  # led -> (n, cx, cy), before correction

        def read_fids():
            got = {}
            for f in fids:
                c = measure(f)
                if c is not None:
                    got[f] = (c["cx"], c["cy"])
            return got

        def measure(led):
            buf = np.zeros((a.count, 3), np.uint8)
            buf[led] = (a.level, a.level, a.level)
            t = time.time(); st.show(buf); time.sleep(a.settle)
            f = mau5eye.shot(os.path.join(HERE, "data", "cal", "_locate.jpg"),
                             port=a.eye_port, wait=30, after=t + 0.4)
            d = np.clip(np.asarray(Image.open(f).convert("L")).astype(np.float32) - ref,
                        0, 255)
            return centroid(d)

        for n, led in enumerate(todo):
            if a.track and n % a.fiducial == 0:
                got = read_fids()
                common = [f for f in fids if f in got and f in base]
                if not base:
                    base = got
                    marks.append((n, (1.0, np.eye(2), np.zeros(2))))
                    print("  tracking by LEDs %s" % fids)
                elif len(common) >= 2:
                    sim = similarity([got[f] for f in common],
                                     [base[f] for f in common])
                    marks.append((n, sim))
                    sh = math.hypot(*sim[2])
                    if sh > a.max_drift:
                        print("  camera has moved; correcting (%.0f px, "
                              "scale %.3f)" % (sh, sim[0]))
                else:
                    print("  only %d fiducials visible; no correction at %d"
                          % (len(common), led))
            elif not a.track and n % a.fiducial == 0:
                c = measure(fid_led)
                if c is not None:
                    if fid0 is None:
                        fid0 = (c["cx"], c["cy"])
                    else:
                        dx, dy = c["cx"] - fid0[0], c["cy"] - fid0[1]
                        drift.append((led, dx, dy))
                        drift_log.append((led, dx, dy))
                        if (dx*dx + dy*dy) ** 0.5 > a.max_drift:
                            print("\n  STOPPING: the fiducial (led %d) has moved "
                                  "%.1f px since the run began." % (fid_led,
                                  (dx*dx + dy*dy) ** 0.5))
                            print("  Everything measured so far is in one frame and "
                                  "everything after would be in another,\n"
                                  "  so the run stops rather than writing a file that "
                                  "looks fine and is not.")
                            break
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
                if a.track:
                    raw[led] = (n, c["cx"], c["cy"])
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
        if a.track and len(marks) >= 1 and raw:
            # Carry every centroid back into the starting frame, easing
            # between the checkpoints either side of it rather than
            # snapping at each one.
            worst = 0.0
            for led, (n, cx, cy) in raw.items():
                before = [m for m in marks if m[0] <= n] or [marks[0]]
                after = [m for m in marks if m[0] > n] or [marks[-1]]
                n0, s0 = before[-1]
                n1, s1 = after[0]
                k = 0.0 if n1 == n0 else (n - n0) / float(n1 - n0)
                x, y = apply_sim(blend(s0, s1, k), (cx, cy))
                worst = max(worst, math.hypot(x - cx, y - cy))
                rows[led]["cx"], rows[led]["cy"] = x, y
            print("\n  tracked out up to %.0f px of camera movement across "
                  "%d checkpoints" % (worst, len(marks)))
        save(rows, a.out)
    print("\nmeasured %d, missed %d %s" % (len(rows), len(misses), misses[:12]))
    print("wrote %s" % a.out)


if __name__ == "__main__":
    main()
