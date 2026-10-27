#!/usr/bin/env python3
"""mau5baralign -- sweep a bar and check every LED answers at its own height.

A bar that should be straight is the sharpest test of a position map,
because it is differential: it asks "did these light at the same
moment", not "where is this glow".  Diffusion ruins the second question
on this helmet -- nine LEDs bloom across half the sphere -- and leaves
the first one perfectly answerable.

The bar is swept in steps over the full vertical extent.  For each LED
with a measured camera centroid, the brightness at that centroid is
tracked across the sweep and the brightness-weighted mean step taken:
the bar height that LED responded to.  If the map is right that height
equals the LED's mapped height, so the two plotted against each other
lie on a line of slope one.  Anything off that line is mis-mapped, and
by how much.

    python3 mau5baralign.py
    python3 mau5baralign.py --steps 48 --thick 22
"""

from __future__ import annotations

import argparse
import os
import time

import numpy as np
from PIL import Image

import mau5engine as E
import mau5eye
import mau5locate
import mau5wled

HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS = os.path.join(HERE, "data", "cal", "baralign")


def sweep(h, steps, thick, level, settle, host, eye_port, out, margin=40.0):
    """Sweep past both ends by `margin`.

    Without it the LEDs at the extremes see a truncated response -- the
    bar arrives but never leaves -- which drags their weighted mean
    inwards and shows up as a slope below one that looks like a map
    error and is not.
    """
    os.makedirs(out, exist_ok=True)
    lo, hi = float(h.py.min()) - margin, float(h.py.max()) + margin
    w = mau5wled.find_one(host)
    w._post("/json/state", {"on": True, "bri": 255})
    w.realtime(True, brightness=255)
    st = mau5wled.Streamer(mau5wled.Pixels(w, h.n), fps=20)
    try:
        t = time.time(); st.dark(); time.sleep(1.6)
        mau5eye.shot(os.path.join(out, "dark.jpg"), port=eye_port, wait=30, after=t + 0.8)
        for k in range(steps):
            pos = lo + (hi - lo) * k / (steps - 1.0)
            buf = np.zeros((h.n, 3), np.uint8)
            buf[np.abs(h.py - pos) <= thick / 2] = (level, level, level)
            t = time.time(); st.show(buf); time.sleep(settle)
            mau5eye.shot(os.path.join(out, "s%02d.jpg" % k), port=eye_port,
                         wait=30, after=t + 0.4)
    finally:
        st.stop()
    return lo, hi


def analyse(h, steps, lo, hi, out, meas, radius=6, clip=0.75):
    ref = np.asarray(Image.open(os.path.join(out, "dark.jpg")).convert("L")).astype(np.float32)
    S = np.stack([np.clip(np.asarray(Image.open(os.path.join(out, "s%02d.jpg" % k))
                                     .convert("L")).astype(np.float32) - ref, 0, 255)
                  for k in range(steps)])
    H, W = ref.shape
    res = {}
    for i in range(h.n):
        if i not in meas:
            continue
        cx, cy = int(round(meas[i]["cx"])), int(round(meas[i]["cy"]))
        x0, x1 = max(0, cx - radius), min(W, cx + radius + 1)
        y0, y1 = max(0, cy - radius), min(H, cy + radius + 1)
        if x1 <= x0 or y1 <= y0:
            continue
        prof = S[:, y0:y1, x0:x1].mean(axis=(1, 2))
        if prof.max() < 8:
            continue
        # Clip hard.  Each ear is one translucent disc, so every LED on
        # it lights the whole panel; that pedestal drags a high LED's
        # weighted mean down towards the disc average and shows up as a
        # slope below one.  Raising the clip from 0.35 to 0.75 lifts the
        # measured ear slope from 0.85 to 0.96 while the shell, which
        # shares no panel, does not move -- which is how we know the
        # shortfall was the panel and not the map.
        p = np.clip(prof - prof.max() * clip, 0, None)
        if p.sum() <= 0:
            continue
        k = float((p * np.arange(steps)).sum() / p.sum())
        res[i] = lo + (hi - lo) * k / (steps - 1.0)
    return res


def report(h, res):
    print("\n  %-11s %5s  %-9s %-11s %s"
          % ("region", "n", "slope", "correlation", "residual"))
    groups = [("shell", h.shell), ("ear1", h.ear1), ("ear2", h.ear2)]
    out = {}
    for lbl, mask in groups:
        idx = [i for i in res if mask[i]]
        if len(idx) < 20:
            print("  %-11s only %d measured" % (lbl, len(idx))); continue
        want = np.array([h.py[i] for i in idx])
        got = np.array([res[i] for i in idx])
        sl, ic = np.polyfit(want, got, 1)
        r = float(np.corrcoef(want, got)[0, 1])
        resid = got - (sl * want + ic)
        out[lbl] = (r, resid.std(), len(idx))
        print("  %-11s %5d  %-9.3f r=%+.3f     sd %5.1f mm, 90th %5.1f mm"
              % (lbl, len(idx), sl, r, resid.std(), np.percentile(np.abs(resid), 90)))
    print("\n  The shell is the control: its positions come from the CAD.")
    print("  An ear matching it means the ear map is as good as the CAD's.")
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter,
                                 epilog=__doc__)
    ap.add_argument("--host", default=None)
    ap.add_argument("--steps", type=int, default=40)
    ap.add_argument("--thick", type=float, default=22.0)
    ap.add_argument("--level", type=int, default=70)
    ap.add_argument("--settle", type=float, default=1.1)
    ap.add_argument("--out", default=SHOTS)
    ap.add_argument("--eye-port", type=int, default=8752)
    ap.add_argument("--margin", type=float, default=40.0,
                    help="sweep this far past each end, so the extremes are "
                         "not truncated")
    ap.add_argument("--reuse", action="store_true", help="analyse the last sweep")
    a = ap.parse_args(argv)

    h = E.Helmet()
    meas = mau5locate.load()
    if not meas:
        raise SystemExit("no measured centroids -- run mau5locate first")
    lo, hi = float(h.py.min()) - a.margin, float(h.py.max()) + a.margin
    if not a.reuse:
        print("sweeping %d steps, %.0f mm bar, level %d ..." % (a.steps, a.thick, a.level))
        lo, hi = sweep(h, a.steps, a.thick, a.level, a.settle, a.host,
                       a.eye_port, a.out, a.margin)
    res = analyse(h, a.steps, lo, hi, a.out, meas)
    print("\n%d of %d LEDs answered the sweep" % (len(res), h.n))
    report(h, res)


if __name__ == "__main__":
    main()
