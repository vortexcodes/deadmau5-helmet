#!/usr/bin/env python3
"""mau5fitmap -- put the ears where the camera says they are.

The shell's 3D positions come from the CAD and are trustworthy: a bar
swept across it tracks image height at r=-0.87.  The ears were rebuilt
after the CAD was drawn, and the parametric stand-in for them tracks at
only -0.36 and -0.45, which is barely at all.

So the shell is used as a calibration target.  Every LED on it has a
known position and a measured camera centroid, which is enough to solve
the projection; that projection is then inverted for the ear LEDs,
whose centroids were measured the same way.

One view cannot recover depth -- a camera sees the same picture
wherever along its own axis a point sits.  Across and up come from the
camera; depth has to come from a model, and the model used to be the
parametric ear evaluated at the LED's index.

That was wrong, and wrong in a way that showed.  Keeping the model's y
while replacing its x and z mixes two different ideas of where an LED
is: y said where the model thought LED k sat on the disc, x and z said
where the camera saw it, and the model tracks the real ear at r=-0.36.
The two disagreed by 36 mm rms -- three LED pitches -- and nothing
reconciled them.

It is not harmless either, whatever the note here used to claim.
az_deg is atan2(x, -y), so a wrong depth is a wrong azimuth, and ten
presets sweep along azimuth.  The error is worst where |x| is small,
because that is where the arctangent is most sensitive to y: at the
inner edge of each ear, against the skull, it reaches 19 degrees.
That is the corner of the left ear that looked wrong.

So depth now comes from the ear's own plane, evaluated at the measured
x.  Every LED on a disc gets a depth consistent with where the camera
actually saw it, which is the most a single view can honestly say.

    python3 mau5fitmap.py             # fit, report, write the new map
    python3 mau5fitmap.py --dry-run   # report only
"""

from __future__ import annotations

import argparse
import csv
import math
import os

import numpy as np

import mau5locate
import mau5map

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "data", "cal", "pixel_map.csv")


def fit_projection(meas, rows, verbose=True):
    """Solve a full 3x4 camera matrix from the shell, by DLT.

    An orthographic fit is not good enough.  The camera is a real lens
    about a metre and a half away and the shell is 170 mm deep, so the
    far side of it images about a tenth smaller than the near side --
    which on a 340 mm face is tens of millimetres, swamping the error
    being looked for.  A projective model absorbs that exactly, and
    costs nothing: there are 399 known points and only 11 unknowns.
    """
    use = [(r, meas[r["index"]]) for r in rows
           if r["region"] == "shell" and r["index"] in meas]
    if len(use) < 20:
        raise SystemExit("only %d shell LEDs measured -- run mau5locate "
                         "over 0..398 first" % len(use))
    X = np.array([[r["x"], r["y"], r["z"]] for r, m in use], float)
    C = np.array([[m["cx"], m["cy"]] for r, m in use], float)
    # condition both sides, or the DLT is numerically miserable
    xm, xs = X.mean(0), X.std(0).mean()
    cm, cs = C.mean(0), C.std(0).mean()
    Xn, Cn = (X - xm) / xs, (C - cm) / cs

    n = len(Xn)
    A = np.zeros((2 * n, 12))
    for i, ((x, y, z), (u, v)) in enumerate(zip(Xn, Cn)):
        A[2*i]     = [x, y, z, 1, 0, 0, 0, 0, -u*x, -u*y, -u*z, -u]
        A[2*i + 1] = [0, 0, 0, 0, x, y, z, 1, -v*x, -v*y, -v*z, -v]
    _, _, Vt = np.linalg.svd(A)
    Pn = Vt[-1].reshape(3, 4)

    def project(pts):
        q = (pts - xm) / xs
        d = Pn[2, 0]*q[:, 0] + Pn[2, 1]*q[:, 1] + Pn[2, 2]*q[:, 2] + Pn[2, 3]
        u = (Pn[0, 0]*q[:, 0] + Pn[0, 1]*q[:, 1] + Pn[0, 2]*q[:, 2] + Pn[0, 3]) / d
        v = (Pn[1, 0]*q[:, 0] + Pn[1, 1]*q[:, 1] + Pn[1, 2]*q[:, 2] + Pn[1, 3]) / d
        return np.c_[u, v] * cs + cm

    pred = project(X)
    res = np.linalg.norm(pred - C, axis=1)
    if verbose:
        print("projective fit on %d shell LEDs (positions are CAD-exact)" % len(use))
        print("  residual: mean %.1f px, median %.1f, 90th %.1f, max %.1f"
              % (res.mean(), np.median(res), np.percentile(res, 90), res.max()))
        sc = np.hypot(*(project(np.array([[10., X[:,1].mean(), 0.]]))[0]
                        - project(np.array([[0., X[:,1].mean(), 0.]]))[0])) / 10.0
        print("  about %.3f px/mm near the centre  ->  1 px is %.2f mm" % (sc, 1.0/sc))
    return (Pn, xm, xs, cm, cs, project), res


def reject_outliers(meas, rows, min_peak=40.0, jump_mm=120.0, verbose=True):
    """Drop measurements that cannot be the LED, and say which.

    Two ways a centroid lies.  A dim one is usually a reflection rather
    than the LED -- 498 came back at peak 16 beside neighbours at 255,
    323 px from its own cluster, and on its own set the whole ear's
    width.  And a bright one can still be wrong if it sits far from
    both of its chain neighbours, since consecutive LEDs on a strip are
    centimetres apart, not tens of centimetres.

    Rejected LEDs are left for the caller to interpolate; a position
    guessed from two neighbours beats one measured off a reflection.
    """
    drop = set()
    for i, m in meas.items():
        if m["peak"] < min_peak:
            drop.add(i)
    # local consistency along the chain, in pixels scaled to mm later
    idx = sorted(meas)
    for a, b, c in zip(idx, idx[1:], idx[2:]):
        if b - a != 1 or c - b != 1 or b in drop:
            continue
        mid = ((meas[a]["cx"] + meas[c]["cx"]) / 2.0,
               (meas[a]["cy"] + meas[c]["cy"]) / 2.0)
        span = np.hypot(meas[a]["cx"] - meas[c]["cx"], meas[a]["cy"] - meas[c]["cy"])
        off = np.hypot(meas[b]["cx"] - mid[0], meas[b]["cy"] - mid[1])
        if off > max(60.0, 2.5 * span):
            drop.add(b)
    if verbose and drop:
        print("rejected %d measurements: %s" % (len(drop), sorted(drop)))
    return drop


def interpolate(byi, missing, lo, hi):
    """Fill a gap from the nearest good LEDs either side, along the chain."""
    filled = 0
    for i in sorted(missing):
        a = next((j for j in range(i - 1, lo - 1, -1) if j not in missing), None)
        b = next((j for j in range(i + 1, hi + 1) if j not in missing), None)
        if a is None and b is None:
            continue
        if a is None:
            src = [byi[b]]
            w = [1.0]
        elif b is None:
            src = [byi[a]]
            w = [1.0]
        else:
            src = [byi[a], byi[b]]
            t = (i - a) / float(b - a)
            w = [1 - t, t]
        byi[i]["x"] = round(sum(s["x"] * k for s, k in zip(src, w)), 2)
        byi[i]["z"] = round(sum(s["z"] * k for s, k in zip(src, w)), 2)
        byi[i]["source"] = "interpolated"
        filled += 1
    return filled


# Each ear is a disc.  Tilt is its rotation about the vertical, which
# decides how depth varies across the disc -- and one view cannot
# measure it: a tilt and an oval disc produce the same picture.
#
# The rim is the one thing that argues.  A circular disc tilted by
# theta images as an ellipse with axes (R cos theta, R), so the
# outline's shape is the tilt.  Fitted to the measured rims it comes
# out 153x128 mm on the left and 157x136 on the right, at 4-5 mm rms:
# both ears WIDER than they are tall.  A tilt about the vertical can
# only make a disc narrower, so the rims give no evidence for one, and
# forcing 26 degrees triples the residual.
#
# Flat it is, then -- not because the ears are certainly flat, but
# because nothing measured says otherwise and a guessed tilt costs 15
# degrees of azimuth.  Pitch cannot arbitrate: solving for the tilt
# that makes the LED spacing most even moves the spread by 0.3%, which
# is noise.  A second camera pose would settle it in one shot, and
# until then this is one number to change.
DISC_TILT_DEG = 0.0
DISC_DEPTH_MM = 30.0           # the discs' depth behind the head centre


def disc_depth(x, ear):
    """Depth of a point on an ear disc, from its measured x."""
    cx = -177.0 if ear == "ear1" else 177.0
    tilt = math.radians(DISC_TILT_DEG * (-1 if ear == "ear1" else 1))
    return DISC_DEPTH_MM + (x - cx) * math.tan(tilt)


def solve_ear(fit, m, r, passes=3):
    """Where one ear LED is: camera for across and up, plane for depth.

    Chicken and egg -- the inversion needs a depth and the plane needs
    an x -- so it is iterated.  It converges in two passes; the third
    is there to show that it has.
    """
    ear = r["region"][:4]
    y = r["y"]
    for _ in range(passes):
        x, z = invert(fit, m["cx"], m["cy"], y)
        y = disc_depth(x, ear)
    return x, y, z


def invert(fit, cx, cy, y_hint):
    """Camera pixels back to (x, z) at an assumed depth.

    One view fixes a ray, not a point, so the depth has to be supplied.
    Across and up then follow -- but only as well as the depth does:
    the camera is about a metre and a half away, so 36 mm of depth
    error drags x and z several mm sideways as well.  Hence the second
    pass in main(), which re-inverts once the plane is known.
    """
    Pn, xm, xs, cm, cs, project = fit
    # two linear equations in (x, z) once y is fixed -- solve by
    # projecting two unit steps and inverting the 2x2
    base = np.array([[0.0, y_hint, 0.0]])
    e_x = np.array([[1.0, y_hint, 0.0]])
    e_z = np.array([[0.0, y_hint, 1.0]])
    p0, px, pz = project(base)[0], project(e_x)[0], project(e_z)[0]
    J = np.c_[px - p0, pz - p0]
    sol = np.linalg.solve(J, np.array([cx, cy]) - p0)
    # one refinement, because the projection is not quite linear in (x,z)
    for _ in range(3):
        cur = project(np.array([[sol[0], y_hint, sol[1]]]))[0]
        sol = sol + np.linalg.solve(J, np.array([cx, cy]) - cur)
    return sol[0], sol[1]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter,
                                 epilog=__doc__)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--positions", default=mau5locate.OUT)
    ap.add_argument("--out", default=OUT)
    a = ap.parse_args(argv)

    meas = mau5locate.load(a.positions)
    rows = mau5map.load(a.out)
    print("measured %d LEDs, map has %d\n" % (len(meas), len(rows)))

    drop = reject_outliers(meas, rows)
    meas = {i: m for i, m in meas.items() if i not in drop}
    fit, res = fit_projection(meas, rows)

    ears = [r for r in rows if r["region"] != "shell"]
    have = [r for r in ears if r["index"] in meas]
    print("\nears: %d of %d measured" % (len(have), len(ears)))

    moved = []
    for r in have:
        x, y, z = solve_ear(fit, meas[r["index"]], r)
        d = float(np.hypot(x - r["x"], z - r["z"]))
        moved.append((d, r["index"], r["x"], r["z"], float(x), float(z)))
    moved.sort(reverse=True)
    md = np.array([m[0] for m in moved])
    print("  the model was out by: median %.0f mm, 90th %.0f mm, max %.0f mm"
          % (np.median(md), np.percentile(md, 90), md.max()))
    print("  worst five:")
    for d, i, ox, oz, nx, nz in moved[:5]:
        print("    led %3d  model (%+7.0f,%+7.0f) -> measured (%+7.0f,%+7.0f)  %.0f mm"
              % (i, ox, oz, nx, nz, d))

    if a.dry_run:
        print("\n(dry run, nothing written)")
        return

    # Unmeasured ears keep their modelled position, flagged as such.
    byi = {r["index"]: r for r in rows}
    n_fix = 0
    before = {r["index"]: r["y"] for r in have}
    for r in have:
        x, y, z = solve_ear(fit, meas[r["index"]], r)
        tgt = byi[r["index"]]
        tgt["x"], tgt["y"], tgt["z"] = (round(float(x), 2), round(float(y), 2),
                                        round(float(z), 2))
        tgt["source"] = "measured"
        n_fix += 1
    dy = np.array([byi[i]["y"] - before[i] for i in before])
    print("  depth moved onto the disc plane: median %.0f mm, max %.0f mm"
          % (np.median(np.abs(dy)), np.abs(dy).max()))
    for r in rows:
        x, y, z = r["x"], r["y"], r["z"]
        r["az_deg"] = round(math.degrees(math.atan2(x, -y)) % 360.0, 2)
        r["elev_deg"] = round(math.degrees(math.atan2(z, math.hypot(x, y))), 2)

    fields = list(rows[0].keys())
    tmp = a.out + ".tmp"
    with open(tmp, "w", newline="") as f:
        wri = csv.DictWriter(f, fieldnames=fields)
        wri.writeheader()
        wri.writerows(rows)
    os.replace(tmp, a.out)
    missing = {r["index"] for r in ears if r["index"] not in meas}
    n_interp = interpolate(byi, missing, min(r["index"] for r in ears),
                           max(r["index"] for r in ears)) if missing else 0
    for i in missing:                       # and onto the plane, like the rest
        r = byi[i]
        r["y"] = round(disc_depth(r["x"], r["region"][:4]), 2)
    for r in rows:
        x, y, z = r["x"], r["y"], r["z"]
        r["az_deg"] = round(math.degrees(math.atan2(x, -y)) % 360.0, 2)
        r["elev_deg"] = round(math.degrees(math.atan2(z, math.hypot(x, y))), 2)
    with open(tmp, "w", newline="") as f:
        wri = csv.DictWriter(f, fieldnames=fields)
        wri.writeheader(); wri.writerows(rows)
    os.replace(tmp, a.out)
    print("\nwrote %s -- %d ear LEDs measured, %d interpolated"
          % (a.out, n_fix, n_interp))


if __name__ == "__main__":
    main()
