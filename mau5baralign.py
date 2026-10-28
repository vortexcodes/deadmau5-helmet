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


def own_pixels(meas, shape, radius):
    """For each LED, the pixels nearer to it than to any other LED.

    A square window round each centroid sounds fine until you measure
    the spacing: on the shell the nearest neighbour is 6.6 px away and
    the window is 6 px, so every sample is a blend of two to five LEDs
    and the sweep reads each one lighting when its neighbours do.  The
    shell's correlation sat at 0.90 against the ears' 0.98 for exactly
    this reason, and no amount of map correction would have moved it.

    Assigning each pixel to its nearest LED keeps the window large
    where the LEDs are sparse and shrinks it to nothing where they
    crowd, which is the right behaviour in both places.
    """
    H, W = shape
    idx = sorted(meas)
    pts = np.array([[meas[i]["cx"], meas[i]["cy"]] for i in idx], np.float32)
    own = {}
    for n, i in enumerate(idx):
        cx, cy = pts[n]
        x0, x1 = int(max(0, cx - radius)), int(min(W, cx + radius + 1))
        y0, y1 = int(max(0, cy - radius)), int(min(H, cy + radius + 1))
        if x1 <= x0 or y1 <= y0:
            continue
        yy, xx = np.mgrid[y0:y1, x0:x1]
        d_self = (xx - cx) ** 2 + (yy - cy) ** 2
        near = np.full(d_self.shape, np.inf, np.float32)
        for m in range(len(idx)):
            if m == n:
                continue
            ox, oy = pts[m]
            if abs(ox - cx) > 3 * radius or abs(oy - cy) > 3 * radius:
                continue
            np.minimum(near, (xx - ox) ** 2 + (yy - oy) ** 2, out=near)
        mask = d_self < near
        if mask.sum() < 1:                     # utterly crowded: keep the peak
            mask = d_self <= d_self.min()
        own[i] = (y0, y1, x0, x1, mask)
    return own


def analyse(h, steps, lo, hi, out, meas, radius=6, clip=0.75):
    ref = np.asarray(Image.open(os.path.join(out, "dark.jpg")).convert("L")).astype(np.float32)
    S = np.stack([np.clip(np.asarray(Image.open(os.path.join(out, "s%02d.jpg" % k))
                                     .convert("L")).astype(np.float32) - ref, 0, 255)
                  for k in range(steps)])
    H, W = ref.shape
    own = own_pixels(meas, (H, W), radius)
    res = {}
    for i in range(h.n):
        if i not in own:
            continue
        y0, y1, x0, x1, mask = own[i]
        prof = S[:, y0:y1, x0:x1][:, mask].mean(axis=1)
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


def kinks(h, res, min_step=9.0, min_side=3):
    """Find strips where the error jumps partway along, and say where.

    A global correlation says the map is good on average, which is
    exactly what it was saying while a quarter of the digits were
    dropping out.  The failure this is looking for is local: a strip
    cut around the visor magnets has LEDs physically absent where the
    CAD has some, so everything after the cut is displaced by a whole
    pitch and everything before it is fine.  That is a step in the
    residual, not a slope, and averaging hides it.

    For each strip, try every split point and keep the one that best
    explains the residual as two flat levels.  Report the step.
    """
    out = []
    for g in sorted(set(h.group.tolist())):
        idx = [i for i in sorted(res) if h.group[i] == g]
        if len(idx) < 2 * min_side + 1:
            continue
        want = np.array([h.py[i] for i in idx])
        got = np.array([res[i] for i in idx])
        if np.ptp(want) < 1e-6:
            continue
        sl, ic = np.polyfit(want, got, 1)
        r = got - (sl * want + ic)
        best = None
        for k in range(min_side, len(idx) - min_side):
            a, b = r[:k], r[k:]
            cost = float(a.var() * len(a) + b.var() * len(b))
            if best is None or cost < best[0]:
                best = (cost, k, float(b.mean() - a.mean()))
        if best is None:
            continue
        _, k, step = best
        flat = float(r.var() * len(r))
        if abs(step) >= min_step and best[0] < flat * 0.6:
            out.append({"group": int(g), "at": int(idx[k]),
                        "before": int(idx[k - 1]), "step_mm": round(step, 1),
                        "n": len(idx)})
    out.sort(key=lambda d: -abs(d["step_mm"]))
    return out


def report_kinks(h, res, pitch=16.7):
    ks = kinks(h, res)
    print("\n  strips whose error jumps partway along "
          "(a cut in the strip looks like this):")
    if not ks:
        print("    none above the threshold -- the map is locally consistent")
        return ks
    print("    %-6s %-14s %9s %9s" % ("strip", "jumps between", "step mm", "pitches"))
    for d in ks:
        print("    %-6d %4d -> %-6d %9.1f %9.2f"
              % (d["group"], d["before"], d["at"], d["step_mm"],
                 d["step_mm"] / pitch))
    return ks


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
    report_kinks(h, res)


if __name__ == "__main__":
    main()
