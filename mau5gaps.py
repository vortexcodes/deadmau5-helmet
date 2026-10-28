#!/usr/bin/env python3
"""mau5gaps -- find places where the strip skips and the map does not.

The shell's positions come from the CAD, which lays every strip out as
an unbroken run at a 16.7 mm pitch.  The real strips are cut around
the visor magnets, so a few LEDs are physically absent where the model
says there are some.  Chain indices do not skip -- the data line
carries straight on -- so every LED after a cut sits one pitch further
along than the map believes, and nothing downstream of it is where an
effect thinks it is.  A bar swept across the helmet shows it as a kink
and nothing else does.

The measured centroids already know.  Within one strip the camera sees
a roughly constant step, so a step several pitches wide is a cut.
This reports them; correcting the map needs the sweep, because a
centroid alone cannot say how many LEDs are missing, only that
something is.

    python3 mau5gaps.py
    python3 mau5gaps.py --min-pitches 1.8 --region shell
"""

from __future__ import annotations

import argparse
import csv
import os

import numpy as np

import mau5map

HERE = os.path.dirname(os.path.abspath(__file__))
POSITIONS = os.path.join(HERE, "data", "cal", "led_positions.csv")


def measured(path=POSITIONS, min_peak=30.0):
    out = {}
    if not os.path.exists(path):
        return out
    with open(path) as f:
        for r in csv.DictReader(f):
            try:
                i, cx, cy = int(r["index"]), float(r["cx"]), float(r["cy"])
                pk = float(r["peak"])
            except (TypeError, ValueError, KeyError):
                continue
            if pk >= min_peak:
                out[i] = (cx, cy)
    return out


def find_against_projection(rows, meas, min_ratio=1.9, min_pred_px=12.0):
    """Compare each measured step to the step the map predicts.

    Better than comparing to the strip's median step, which assumes a
    constant apparent pitch and so flags the silhouette, where a sphere
    compresses one pitch into a couple of pixels.  Solving the camera
    and projecting the map removes that.

    It is still not proof.  The projective fit's own residual is about
    18 px, and one LED pitch images at roughly 21 px, so a single
    missing LED is the same size as the noise.  Pairs whose predicted
    step is already tiny are excluded for that reason -- a 3 px
    prediction turns 15 px of noise into a factor of five.  Treat the
    output as somewhere to point the bar sweep, not as a conclusion.
    """
    import mau5fitmap
    (Pn, xm, xs, cm, cs, project), res = mau5fitmap.fit_projection(
        meas, rows, verbose=False)
    X = np.array([[r["x"], r["y"], r["z"]] for r in rows], float)
    pred = project(X)
    grp = np.array([r["group"] for r in rows])
    reg = np.array([r["region"] for r in rows], dtype=object)
    hits = []
    for g in sorted(set(grp[reg == "shell"].tolist())):
        idx = [int(i) for i in np.where((grp == g) & (reg == "shell"))[0]
               if int(i) in meas]
        for a, b in zip(idx, idx[1:]):
            if b != a + 1:
                continue
            exp = float(np.hypot(*(pred[b] - pred[a])))
            m = meas
            got = float(np.hypot(m[b]["cx"] - m[a]["cx"], m[b]["cy"] - m[a]["cy"]))
            if exp >= min_pred_px and got / exp >= min_ratio:
                hits.append({"group": int(g), "after": a, "before": b,
                             "px": round(got, 1), "pred_px": round(exp, 1),
                             "ratio": round(got / exp, 2),
                             "missing": int(round(got / exp)) - 1,
                             "region": "shell"})
    hits.sort(key=lambda h: -h["ratio"])
    return hits, float(np.median(res))


def find(rows, pos, region=None, min_pitches=2.0):
    grp = np.array([r["group"] for r in rows])
    reg = np.array([r["region"] for r in rows], dtype=object)
    sel = np.ones(len(rows), bool) if region is None else np.array(
        [str(r).startswith(region) for r in reg])
    hits = []
    for g in sorted(set(grp[sel].tolist())):
        idx = [int(i) for i in np.where((grp == g) & sel)[0] if int(i) in pos]
        if len(idx) < 4:
            continue
        p = np.array([pos[i] for i in idx])
        d = np.linalg.norm(np.diff(p, axis=0), axis=1)
        med = float(np.median(d))
        if med < 1.0:
            continue
        for b in np.where(d > med * min_pitches)[0]:
            hits.append({"group": int(g), "after": idx[b], "before": idx[b + 1],
                         "px": round(float(d[b]), 1), "median_px": round(med, 1),
                         "pitches": round(float(d[b] / med), 2),
                         "missing": int(round(d[b] / med)) - 1,
                         "region": str(reg[idx[b]])})
    hits.sort(key=lambda h: -h["pitches"])
    return hits


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--positions", default=POSITIONS)
    ap.add_argument("--region", default=None, help="shell, ear1, ear2")
    ap.add_argument("--min-pitches", type=float, default=2.0)
    ap.add_argument("--min-ratio", type=float, default=1.9,
                    help="measured step over predicted step")
    a = ap.parse_args(argv)

    rows = mau5map.load()
    pos = measured(a.positions)
    if not pos:
        raise SystemExit("no measured positions at %s -- run mau5locate first"
                         % a.positions)
    print("%d of %d LEDs have a measured centroid\n" % (len(pos), len(rows)))

    full = {i: {"cx": c[0], "cy": c[1], "peak": 255.0} for i, c in pos.items()}
    hits, resid = find_against_projection(rows, full, a.min_ratio)
    pitch_px = 16.7 * 1.293                       # map pitch at the measured scale
    print("projective fit residual: %.1f px median.  One LED pitch is about "
          "%.0f px,\nso a single missing LED is the same size as the noise -- "
          "these are\nplaces to aim the bar sweep, not findings.\n"
          % (resid, pitch_px))
    if not hits:
        print("nothing above %.1fx" % a.min_ratio)
        return 0
    print("%-6s %-11s %9s %10s %7s  implies missing" % ("group", "between",
                                                        "measured", "predicted", "ratio"))
    for h in hits:
        print("  %-4d %3d -> %-3d %9.1f %10.1f %7.2f   %d"
              % (h["group"], h["after"], h["before"], h["px"], h["pred_px"],
                 h["ratio"], h["missing"]))
    print("\n%d steps above %.1fx." % (len(hits), a.min_ratio))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
