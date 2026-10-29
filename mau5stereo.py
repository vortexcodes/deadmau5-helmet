#!/usr/bin/env python3
"""mau5stereo -- where the ears are, from two views instead of one.

One camera cannot see depth.  It sees the same picture wherever along
its own axis a point sits, so the single-pose fit took across and up
from the camera and had to get depth from somewhere else -- first
from a parametric model that tracked the real ear at r=-0.36, then
from the ear's own plane, which is honest but still assumes the ear
*is* a plane and assumes its tilt.  `DISC_TILT_DEG` has been a
guessed zero this whole time, with a note saying a second pose would
measure it outright.

This is that measurement.  Two camera poses, each solved against the
shell -- whose positions are CAD-exact and which therefore makes a
399-point calibration target -- and then every LED seen from both is
triangulated.  No model of the ear enters into it at any point.

The shell is triangulated too, and that is the check that matters:
its answer is already known, so the distance between the
triangulated shell and the CAD shell is the method's own error bar.
Trust the ear numbers only as far as that number is small.

    python3 mau5stereo.py
    python3 mau5stereo.py --apply      # write the measured ears into the map
"""

from __future__ import annotations

import argparse
import csv
import math
import os

import numpy as np

import mau5fitmap
import mau5map

HERE = os.path.dirname(os.path.abspath(__file__))
POSE1 = os.path.join(HERE, "data", "cal", "led_positions.csv")
POSE2 = os.path.join(HERE, "data", "cal", "led_positions_pose2.csv")
OUT = os.path.join(HERE, "data", "cal", "ears_stereo.csv")


def load(path, min_peak=40.0):
    out = {}
    if not os.path.exists(path):
        return out
    with open(path) as f:
        for r in csv.DictReader(f):
            try:
                i = int(r["index"])
                if float(r["peak"]) < min_peak:
                    continue
                out[i] = {"cx": float(r["cx"]), "cy": float(r["cy"]),
                          "peak": float(r["peak"])}
            except (TypeError, ValueError, KeyError):
                continue
    return out


def spread(rows, use):
    """How three-dimensional the surviving calibration points are.

    This is the guard that matters.  A 3x4 DLT needs points that are
    not all on a plane, and the shell is a sphere, so dropping the
    worst few per cent repeatedly walks the surviving set onto a
    patch -- and a coplanar set fits a projective camera *exactly*.
    The residual goes to zero, the fit looks perfect, and the matrix
    is meaningless off that plane.  It did: three passes of dropping
    a quarter gave 0.000 px on 224 points, and the shell check built
    on it then reproduced the shell to 1.9 mm, which proved nothing
    at all because it was the same plane answering itself.

    So: the ratio of the smallest to the largest extent of the point
    cloud.  A sphere's shell gives about 0.5; a patch gives nearly 0.
    """
    P = np.array([[r["x"], r["y"], r["z"]] for r in rows
                  if r["region"] == "shell" and r["index"] in use], float)
    if len(P) < 12:
        return 0.0
    sv = np.linalg.svd(P - P.mean(0), compute_uv=False)
    return float(sv[-1] / sv[0])


def robust_camera(meas, rows, label, passes=3, clip=4.0, min_pts=250,
                  min_spread=0.12):
    """Solve the camera, dropping only what is clearly wrong.

    A sigma clip rather than a fixed fraction, so a clean set loses
    nothing, and a hard stop if the survivors stop being a solid.
    """
    use = dict(meas)
    best = None
    for k in range(passes):
        M, project, res = camera(use, rows, label if not k else
                                 "%s p%d" % (label, k + 1))
        sp = spread(rows, use)
        n = sum(1 for r in rows if r["region"] == "shell" and r["index"] in use)
        if sp < min_spread or n < min_pts:
            print("    stopping: %d points, spread %.3f -- too flat to solve"
                  % (n, sp))
            break
        med = float(np.median(res))
        # A camera solved against real centroids does not fit them to a
        # tenth of a pixel; centroid noise alone is a pixel or two.  A
        # median that good means the fit has started describing the
        # points rather than the camera, which is the same failure as
        # the coplanar one and just as invisible downstream.  Keep the
        # last honest fit and stop.
        if med < 0.5 and k:
            print("    stopping: median %.2f px is too good to be a "
                  "measurement; keeping the previous fit" % med)
            break
        best = (M, project, res, dict(use))
        cut = max(clip * med, 8.0)
        shell = [r for r in rows if r["region"] == "shell" and r["index"] in use]
        bad = set(shell[i]["index"] for i in np.where(res > cut)[0])
        if not bad:
            break
        use = {i: v for i, v in use.items() if i not in bad}
    if best is None:
        raise SystemExit("could not solve %s without the points going flat" % label)
    print("    kept %d shell points, spread %.3f"
          % (sum(1 for r in rows if r["region"] == "shell" and r["index"] in best[3]),
             spread(rows, best[3])))
    return best


def _is_shell(rows, i):
    for r in rows:
        if r["index"] == i:
            return r["region"] == "shell"
    return False


def camera(meas, rows, label):
    """A full 3x4 pixel-space camera, conditioning folded in.

    fit_projection returns its matrix in a normalised frame with a
    projecting closure around it.  Triangulation needs the matrix
    itself, in the coordinates the measurements are actually in, so
    the two conditioning transforms are multiplied back in.
    """
    (Pn, xm, xs, cm, cs, project), res = mau5fitmap.fit_projection(
        meas, rows, verbose=False)
    S = np.eye(4)
    S[:3, :3] /= xs
    S[:3, 3] = -xm / xs
    K = np.array([[cs, 0, cm[0]], [0, cs, cm[1]], [0, 0, 1]], float)
    M = K @ Pn @ S
    print("  %-7s %3d shell points, residual median %.1f px, 90th %.1f"
          % (label, sum(1 for r in rows
                        if r["region"] == "shell" and r["index"] in meas),
             np.median(res), np.percentile(res, 90)))
    return M, project, res


def triangulate(M1, uv1, M2, uv2):
    """Least-squares intersection of two rays, the usual DLT form."""
    u1, v1 = uv1
    u2, v2 = uv2
    A = np.array([
        u1 * M1[2] - M1[0],
        v1 * M1[2] - M1[1],
        u2 * M2[2] - M2[0],
        v2 * M2[2] - M2[1],
    ], float)
    _, _, Vt = np.linalg.svd(A)
    X = Vt[-1]
    if abs(X[3]) < 1e-12:
        return None
    return X[:3] / X[3]


def plane_of(P):
    """Best-fit plane through a set of points: centre, normal, rms."""
    c = P.mean(0)
    _, _, Vt = np.linalg.svd(P - c)
    n = Vt[-1]
    rms = float(np.sqrt((((P - c) @ n) ** 2).mean()))
    return c, n, rms


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pose1", default=POSE1)
    ap.add_argument("--pose2", default=POSE2)
    ap.add_argument("--min-peak", type=float, default=40.0)
    ap.add_argument("--max-reproj", type=float, default=12.0,
                    help="drop a point that does not land back on the two "
                         "centroids it was built from")
    ap.add_argument("--apply", action="store_true",
                    help="write the triangulated ears into data/cal/adjust.json")
    a = ap.parse_args(argv)

    rows = mau5map.load(adjust=False)
    m1, m2 = load(a.pose1, a.min_peak), load(a.pose2, a.min_peak)
    both = sorted(set(m1) & set(m2))
    print("pose 1: %d LEDs, pose 2: %d, seen from both: %d\n"
          % (len(m1), len(m2), len(both)))
    if len(both) < 120:
        raise SystemExit("not enough overlap yet -- let mau5locate finish")

    M1, pr1, _, m1 = robust_camera(m1, rows, "pose 1")
    M2, pr2, _, m2 = robust_camera(m2, rows, "pose 2")
    both = sorted(set(m1) & set(m2))

    # Before any triangulation: how far is the map's own answer from
    # where each camera actually saw the LED?  Pose 1 is the view the
    # ears were fitted from, so it cannot fail; pose 2 had no part in
    # making the map and is therefore the only honest number here.
    print("\n  the map against each camera (one LED pitch is 16.7 mm)")
    X = np.array([[r["x"], r["y"], r["z"]] for r in rows], float)
    for tag, M, project, meas in (("pose 1", M1, pr1, m1), ("pose 2", M2, pr2, m2)):
        pred = project(X)
        mid = X[:, 1].mean()
        sc = float(np.hypot(*(project(np.array([[10., mid, 0.]]))[0]
                              - project(np.array([[0., mid, 0.]]))[0])) / 10.0)
        bits = []
        for name, test in (("shell", lambda r: r["region"] == "shell"),
                           ("ear1", lambda r: str(r["region"]).startswith("ear1")),
                           ("ear2", lambda r: str(r["region"]).startswith("ear2"))):
            sel = [k for k, r in enumerate(rows) if test(r) and r["index"] in meas]
            if not sel:
                continue
            e = [float(np.hypot(*(pred[k] - np.array([meas[rows[k]["index"]]["cx"],
                                                      meas[rows[k]["index"]]["cy"]]))))
                 for k in sel]
            bits.append("%s %.1f mm" % (name, float(np.median(e)) / max(sc, 1e-6)))
        print("    %-8s %s" % (tag, "   ".join(bits)))

    byi = {r["index"]: r for r in rows}
    tri, thrown = {}, 0
    for i in both:
        X = triangulate(M1, (m1[i]["cx"], m1[i]["cy"]),
                        M2, (m2[i]["cx"], m2[i]["cy"]))
        if X is None:
            continue
        # A triangulated point that does not reproject onto the two
        # centroids it came from is not a measurement of anything.
        e = 0.0
        for M, m in ((M1, m1[i]), (M2, m2[i])):
            q = M @ np.array([X[0], X[1], X[2], 1.0])
            if abs(q[2]) < 1e-9:
                e = 1e9
                break
            e = max(e, math.hypot(q[0] / q[2] - m["cx"], q[1] / q[2] - m["cy"]))
        if e > a.max_reproj:
            thrown += 1
            continue
        tri[i] = X
    print("\n  %d triangulated, %d thrown out for reprojecting more than %.0f px"
          % (len(tri), thrown, a.max_reproj))

    shell = [i for i in tri if byi[i]["region"] == "shell"]
    if shell:
        P = np.array([tri[i] for i in shell])
        C = np.array([[byi[i]["x"], byi[i]["y"], byi[i]["z"]] for i in shell])
        d = np.linalg.norm(P - C, axis=1)
        print("\n  the check: %d shell LEDs triangulated against CAD" % len(shell))
        print("    error  median %.1f mm, 90th %.1f, max %.1f"
              % (np.median(d), np.percentile(d, 90), d.max()))
        print("    (one LED pitch is 16.7 mm.  This is the error bar on"
              " everything below.)")

    for name in ("ear1", "ear2"):
        got = [i for i in tri if str(byi[i]["region"]).startswith(name)]
        if len(got) < 20:
            print("\n  %s: only %d LEDs from both poses, skipping" % (name, len(got)))
            continue
        P = np.array([tri[i] for i in got])
        c, n, rms = plane_of(P)
        # the tilt the map has been guessing: rotation of the disc's
        # plane about the vertical, measured from a plane facing -y
        tilt = math.degrees(math.atan2(n[0], abs(n[1]) if n[1] else 1e-9))
        if tilt > 90:
            tilt -= 180
        if tilt < -90:
            tilt += 180
        was = np.array([[byi[i]["x"], byi[i]["y"], byi[i]["z"]] for i in got])
        moved = np.linalg.norm(P - was, axis=1)
        print("\n  %s: %d LEDs triangulated" % (name, len(got)))
        print("    centre      (%7.1f, %7.1f, %7.1f) mm" % tuple(c))
        print("    plane rms   %.1f mm  (how flat the disc actually is)" % rms)
        print("    tilt        %+.1f deg about the vertical"
              "   <- DISC_TILT_DEG is %.1f" % (tilt, mau5fitmap.DISC_TILT_DEG))
        print("    depth y     %.1f .. %.1f mm   (map says %.1f .. %.1f)"
              % (P[:, 1].min(), P[:, 1].max(), was[:, 1].min(), was[:, 1].max()))
        print("    moved from the current map: median %.1f mm, max %.1f"
              % (np.median(moved), moved.max()))

    # Split-half, which is the only thing that makes any of the above
    # a measurement rather than a number.  Solve both cameras twice --
    # once from the even shell LEDs, once from the odd -- and
    # triangulate the ears with each.  Same helmet, same photographs,
    # independent calibrations: if the two answers disagree by more
    # than they should, the figure above is noise wearing a decimal
    # point, and that is worth knowing before it reaches the map.
    print("\n  split-half: the same thing measured two independent ways")
    halves = {}
    for tag, pick in (("even", lambda i: i % 2 == 0), ("odd", lambda i: i % 2)):
        sub = [r for r in rows if r["region"] != "shell" or pick(r["index"])]
        try:
            # half as many points, so the floor has to halve too
            Ma, _, _, ua = robust_camera(dict(m1), sub, "  %s/1" % tag,
                                         min_pts=140)
            Mb, _, _, ub = robust_camera(dict(m2), sub, "  %s/2" % tag,
                                         min_pts=140)
        except SystemExit:
            print("    %s: could not solve" % tag)
            continue
        got = {}
        for i in both:
            X = triangulate(Ma, (m1[i]["cx"], m1[i]["cy"]),
                            Mb, (m2[i]["cx"], m2[i]["cy"]))
            if X is not None:
                got[i] = X
        halves[tag] = got
    if len(halves) == 2:
        print()
        for name in ("ear1", "ear2"):
            tilts = []
            for tag, got in halves.items():
                sel = [i for i in got if str(byi[i]["region"]).startswith(name)]
                if len(sel) < 20:
                    continue
                c, n, rms = plane_of(np.array([got[i] for i in sel]))
                t = math.degrees(math.atan2(n[0], abs(n[1]) if n[1] else 1e-9))
                t = t - 180 if t > 90 else (t + 180 if t < -90 else t)
                tilts.append(t)
            if len(tilts) == 2:
                gap = abs(tilts[0] - tilts[1])
                print("    %s tilt: %+.1f from one half, %+.1f from the other"
                      "  -> %s"
                      % (name, tilts[0], tilts[1],
                         "agrees to %.1f deg" % gap if gap < 5
                         else "DISAGREE by %.1f deg; this is not a measurement"
                              % gap))

    with open(OUT, "w", newline="") as f:
        wr = csv.writer(f)
        wr.writerow(["index", "region", "x", "y", "z",
                     "map_x", "map_y", "map_z", "moved_mm"])
        for i in sorted(tri):
            X, r = tri[i], byi[i]
            wr.writerow([i, r["region"]] + [round(float(v), 2) for v in X]
                        + [round(r["x"], 2), round(r["y"], 2), round(r["z"], 2),
                           round(float(np.linalg.norm(
                               X - np.array([r["x"], r["y"], r["z"]]))), 2)])
    print("\n  -> %s" % OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
