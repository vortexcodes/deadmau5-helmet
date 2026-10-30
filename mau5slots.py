#!/usr/bin/env python3
"""mau5slots -- every LED in a place the CAD says an LED can go.

The helmet was printed from a CAD model with a slot for every shell LED
and three tubes and a rim channel in each ear.  Every LED that exists
sits in one of those places; not every place has an LED.  That is a far
stronger statement than anything a camera can measure, and the map used
to throw it away.

What it did instead, for the shell, was trust the CAD's *wiring order*
-- its 399 slots taken in sequence, strip orientation decided by the
camera -- and then, when the camera disagreed by 15 px, slide each LED
along the sphere until it sat on its own camera ray.  That fits the
camera it was fitted to perfectly (0.02 px, which is the giveaway) and
puts most LEDs between slots, where no LED can physically be.  From the
front it looked right.  From the side it was wrong, because a front
camera barely constrains anything at the edge of the sphere and the
correction ran freely there -- up to 113 mm.

So the map is now built the other way round: positions only ever come
from the CAD, and the cameras decide *which* slot.

The shell.  Two camera poses are solved against slot positions, then
the chain is aligned to the CAD's wiring order by dynamic programming:
each LED is the next slot along its strip, or skips an empty slot, or
starts the next strip at either end.  It cannot reuse a slot, so the
answer is a real assignment rather than a nearest-point snap.  A camera
that sees an LED edge-on is trusted less than one that sees it face-on,
because a glow at grazing angle is clipped by its own recess and its
centroid moves -- by 30-40 px on the strips at the very edge.  Then the
cameras are re-solved against the slots they chose, and round again.

It converges to 398 shell LEDs in 398 distinct slots with exactly one
empty (the top of strip B04), and two places where the wiring visits
strips in a different order from the CAD's list: the channels broken by
the ear mounts, where the data picks mirror-image orders on the two
sides.  Each camera on its own, run through the whole thing from the
CAD with no help from the other, gives the identical assignment.  So
does the walk from the first calibration session: 67 of its 68 strip
boundaries are exactly where the cameras put them, including the
11-LED strip, the two 1-LED strips at the mounts and the shell ending
at 397 -- facts the map had been overriding with the CAD's 399.

The ears.  The cameras are not good enough to say where an ear is in
depth.  The two views are only calibrated on the shell, the ear glows
are diffuse, and an ear pose fitted to the LEDs alone matches the
daylight photograph worse than the CAD's own pose does.  So the ears
stay exactly where the CAD puts them -- tilted back and turned out,
which a photograph from the high pose confirms to within its
resolution -- and the cameras say only where along which tube each LED
sits.  That is the part a camera measures well whatever the depth.

    python3 mau5slots.py              # solve, report, write the map
    python3 mau5slots.py --dry-run    # solve and report only
"""

from __future__ import annotations

import argparse
import collections
import csv
import itertools
import json
import math
import os
import struct
import warnings

import numpy as np

# numpy 2.0 on Apple silicon flags divide/overflow/invalid on ordinary
# matmuls whose results are finite -- a BLAS flag leak, not a fault in
# the numbers -- and the warnings bury the report.
warnings.filterwarnings("ignore", message=".*encountered in matmul")

HERE = os.path.dirname(os.path.abspath(__file__))
CAD = os.path.join(HERE, "data", "cad", "pixel_map_cad.csv")
MESH = os.path.join(HERE, "mau5head_sim_backdrop.glb")
POSES = {
    # the original front view, level with the helmet
    "front": os.path.join(HERE, "data", "cal", "led_positions.csv"),
    # the camera moved up, right and closer: about 34 degrees of baseline
    "high": os.path.join(HERE, "data", "cal", "led_positions_pose4.csv"),
}
OUT = os.path.join(HERE, "data", "cal", "pixel_map.csv")
REPORT = os.path.join(HERE, "data", "cal", "slots.json")

STRIPS = os.path.join(HERE, "data", "cal", "strips.json")

TOTAL_N = 621
ROT = 38                 # the chain starts at CAD strip B39

# Chain indices the pose files were measured on, but which no longer
# exist.  On 2026-10-29 the near ear's rim strip (ear1, the wearer's
# right) was a little long, and its first segment was cut off and the
# feed re-soldered to the next one.  A segment is one pixel -- one
# driver chip under ten COB LEDs -- so the chain lost exactly one index,
# and every LED from there on moved down by one.  Measured afterwards
# from the side camera: the near ear's tubes still end at 491, its rim
# from 495 on lands where the old 496 onwards did, the far ear's tube
# turns and junctions all arrive one index early, and 621 lights
# nothing.  Old 492 was the segment: the one that sat on the inner side
# of the rim's bottom, and the new 492 is at the bottom centre where the
# old 493 was.
CUT = (492,)


def after_cut(meas):
    """Pose centroids keyed by the chain as it is now, not as it was."""
    out = {}
    for i, uv in meas.items():
        if i in CUT:
            continue
        out[i - sum(1 for c in CUT if c < i)] = uv
    return out

# Where the wiring is not the CAD's list: the channels interrupted by
# the ear mounts, each split into a strip above the mount and one below.
# The order inside each cluster is chosen by the data, every permutation
# tried; both sides come out as mirror images of each other.
CLUSTERS = (("B09", "B10", "B11", "B12"), ("B27", "B28", "B29", "B30"))

# Dynamic-programming costs, as log probabilities.  An empty slot is
# rare (one in the whole shell) but must be possible, or a single
# missing LED shifts everything after it by a slot -- which is exactly
# the error the map used to have from strip B04 onwards.
LP_NEXT = math.log(0.9)
LP_EMPTY = -3.0
LP_STRIP = -1.0
LP_OFF = -2.0            # leaving the shell for good (onto the ears)
OFF_LL = -4.5            # how well "not a shell slot" explains a centroid
MAX_SKIP = 3
SIGMA = 2.5              # px, for a glow seen square-on


# ---------------------------------------------------------------- CAD
def load_cad(path=CAD):
    """Slot positions, and chain B's strips in the order they are wired."""
    rows = list(csv.DictReader(open(path)))
    xyz = np.array([[float(r[k]) for k in "xyz"] for r in rows])
    strips = collections.OrderedDict()
    for s, r in enumerate(rows):
        if r["chain"] == "B":
            strips.setdefault(r["strip"], []).append(s)
    for nm in strips:
        strips[nm].sort(key=lambda s: int(rows[s]["led"]))
    names = list(strips)
    order = [names[(ROT + g) % len(names)] for g in range(len(names))]
    return rows, xyz, strips, order


def load_mesh(path=MESH):
    """Vertices and faces of the CAD backdrop, from its glTF binary."""
    with open(path, "rb") as f:
        f.read(12)
        n, _ = struct.unpack("<II", f.read(8))
        doc = json.loads(f.read(n))
        n, _ = struct.unpack("<II", f.read(8))
        buf = f.read(n)

    def acc(i):
        a = doc["accessors"][i]
        bv = doc["bufferViews"][a["bufferView"]]
        off = bv.get("byteOffset", 0) + a.get("byteOffset", 0)
        dt = {5125: np.uint32, 5123: np.uint16, 5126: np.float32}[a["componentType"]]
        k = {"SCALAR": 1, "VEC3": 3}[a["type"]]
        return np.frombuffer(buf, dtype=dt, count=a["count"] * k,
                             offset=off).reshape(a["count"], k)

    prim = doc["meshes"][0]["primitives"][0]
    V = acc(prim["attributes"]["POSITION"]).astype(float)
    F = acc(prim["indices"]).reshape(-1, 3).astype(np.int64)
    return V, F


def mesh_parts(V, F):
    """The mesh's connected pieces, labelled by where they are.

    Seven pieces: the shell in two halves, the visor, and each ear in
    two halves split along a diagonal (it was printed that way).
    """
    parent = np.arange(len(V))

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    for a, b, c in F:
        ra = find(a)
        parent[find(b)] = ra
        parent[find(c)] = ra
    root = np.array([find(i) for i in range(len(V))])[F[:, 0]]
    parts = collections.defaultdict(list)
    for r in np.unique(root):
        P = V[np.unique(F[root == r])]
        far = np.linalg.norm(P, axis=1).max()
        x = P[:, 0].mean()
        if far < 200:
            name = "visor" if P[:, 1].max() < 50 else "shell"
        else:
            name = "ear1" if x < 0 else "ear2"
        parts[name].append(root == r)
    return {k: np.any(v, axis=0) for k, v in parts.items()}


def ear_geometry(V, F, mask):
    """An ear disc's frame, tubes and rim, measured off the mesh.

    The plates are the large faces parallel to each other; their
    area-weighted normal is the disc's.  The tubes are the long thin
    faces running one way across it, three of them, parallel.
    """
    T = V[F[mask]]
    nrm = np.cross(T[:, 1] - T[:, 0], T[:, 2] - T[:, 0])
    area = 0.5 * np.linalg.norm(nrm, axis=1)
    nrm = nrm / (2 * area[:, None] + 1e-12)
    P = V[np.unique(F[mask])]
    # start from the vertices' flattest direction, then refine on plates
    n = np.linalg.svd(P - P.mean(0))[2][2]
    for _ in range(3):
        sel = np.abs(nrm @ n) > math.cos(math.radians(8))
        nn = nrm[sel] * np.sign(nrm[sel] @ n)[:, None]
        n = (nn * area[sel, None]).sum(0)
        n /= np.linalg.norm(n)
    if n[1] > 0:                       # face forward, along -y
        n = -n
    off = T.mean(1)[sel] @ n
    side = nrm[sel] @ n
    front = np.average(off[side > 0], weights=area[sel][side > 0])
    back = np.average(off[side < 0], weights=area[sel][side < 0])
    mid = (front + back) / 2

    e1 = np.cross([0.0, 0.0, 1.0], n)
    e1 /= np.linalg.norm(e1)
    e2 = np.cross(n, e1)
    # The rim is a circle.  Fitted to every vertex it comes out 8 mm off
    # centre and 15 mm small, because the tubes and the mounting tab
    # vote too; so fit, keep what lies near the circle, fit again.
    uv = np.c_[P @ e1, P @ e2]
    keep = np.ones(len(uv), bool)
    for band in (25, 25, 6, 6, 6, 6):
        A = np.c_[2 * uv[keep], np.ones(keep.sum())]
        sol = np.linalg.lstsq(A, (uv[keep] ** 2).sum(1), rcond=None)[0]
        cu, cv = sol[:2]
        radius = math.sqrt(sol[2] + cu * cu + cv * cv)
        r = np.hypot(uv[:, 0] - cu, uv[:, 1] - cv)
        keep = np.abs(r - radius) < band
    rim_outer = float(np.percentile(r[keep], 95))
    centre = cu * e1 + cv * e2 + mid * n

    # tubes: long faces, one dominant direction in the plane
    ed = np.stack([T[:, 1] - T[:, 0], T[:, 2] - T[:, 1], T[:, 0] - T[:, 2]], 1)
    el = np.linalg.norm(ed, axis=2)
    k = el.argmax(1)
    longest = el.max(1)
    dv = ed[np.arange(len(T)), k]
    d2 = np.c_[dv @ e1, dv @ e2]
    d2 /= np.linalg.norm(d2, axis=1, keepdims=True) + 1e-12
    cand = (longest > 60) & (np.abs(nrm @ n) < 0.97)
    ang = np.degrees(np.arctan2(d2[cand, 1], d2[cand, 0])) % 180
    hist, edges = np.histogram(ang, bins=36, range=(0, 180), weights=longest[cand])
    th = math.radians((edges[hist.argmax()] + edges[hist.argmax() + 1]) / 2)
    ref = np.array([math.cos(th), math.sin(th)])
    near = cand.copy()
    near[cand] = np.abs(d2[cand] @ ref) > math.cos(math.radians(6))
    d = (d2[near] * np.sign(d2[near] @ ref)[:, None]).mean(0)
    d /= np.linalg.norm(d)
    # make "along" run upward, so the numbers read the same on both ears
    if d[1] < 0:
        d = -d
    along = d[0] * e1 + d[1] * e2
    across = np.cross(n, along)
    ends = np.concatenate([T[near, 0], T[near, 1], T[near, 2]])
    lat = (ends - centre) @ across
    tubes = []
    for guess in np.unique(np.round(lat / 45.0)) * 45.0:
        m = np.abs(lat - guess) < 22
        if m.sum() < 20:
            continue
        lo = float(((ends[m] - centre) @ along).min())
        hi = float(((ends[m] - centre) @ along).max())
        tubes.append({"lat": float(np.median(lat[m])), "lo": lo, "hi": hi,
                      "depth": float(np.median((ends[m] - centre) @ n)),
                      "radius": float(np.ptp(lat[m]) / 2)})
    tubes.sort(key=lambda t: t["lat"])
    return {"normal": n, "centre": centre, "along": along, "across": across,
            "radius": radius, "rim_outer": rim_outer,
            "front": front - mid, "back": back - mid, "tubes": tubes}


# ------------------------------------------------------------- cameras
def load_centroids(path, min_peak=40.0):
    out = {}
    if not os.path.exists(path):
        return out
    for r in csv.DictReader(open(path)):
        try:
            if float(r["peak"]) < min_peak:
                continue
            out[int(r["index"])] = (float(r["cx"]), float(r["cy"]))
        except (KeyError, ValueError):
            continue
    return out


def dlt(X, uv):
    """A 3x4 projective camera from 3D-2D pairs, conditioned both sides."""
    xm, xs = X.mean(0), X.std(0).mean()
    cm, cs = uv.mean(0), uv.std(0).mean()
    Xn, Cn = (X - xm) / xs, (uv - cm) / cs
    A = np.zeros((2 * len(X), 12))
    for i, ((x, y, z), (u, v)) in enumerate(zip(Xn, Cn)):
        A[2 * i] = [x, y, z, 1, 0, 0, 0, 0, -u * x, -u * y, -u * z, -u]
        A[2 * i + 1] = [0, 0, 0, 0, x, y, z, 1, -v * x, -v * y, -v * z, -v]
    Pn = np.linalg.svd(A)[2][-1].reshape(3, 4)
    S = np.eye(4)
    S[:3, :3] /= xs
    S[:3, 3] = -xm / xs
    K = np.array([[cs, 0, cm[0]], [0, cs, cm[1]], [0, 0, 1]])
    M = K @ Pn @ S
    return M / np.linalg.norm(M[2, :3])


def project(M, X):
    q = np.c_[X, np.ones(len(X))] @ M.T
    return q[:, :2] / q[:, 2:3]


def camera_centre(M):
    c = np.linalg.svd(M)[2][-1]
    return c[:3] / c[3]


def solve_camera(X, uv, rounds=6):
    """A camera from correspondences, dropping the ones that cannot fit.

    The threshold follows the residuals rather than a fixed fraction, so
    a clean set loses nothing.  Edge-on glows are the usual casualties.
    """
    keep = np.ones(len(uv), bool)
    for _ in range(rounds):
        M = dlt(X[keep], uv[keep])
        e = np.linalg.norm(project(M, X) - uv, axis=1)
        med = np.median(e[keep])
        mad = 1.4826 * np.median(np.abs(e[keep] - med))
        new = e < max(med + 3 * mad, 3.0)
        if (new == keep).all():
            break
        keep = new
    return M, e, keep


def ray(M, uv):
    C = camera_centre(M)
    X = np.linalg.solve(M[:, :3], np.array([uv[0], uv[1], 1.0]) - M[:, 3])
    d = X - C
    return C, d / np.linalg.norm(d)


# --------------------------------------------------------------- shell
class Shell:
    """The chain-to-slot alignment, as a left-to-right hidden Markov model.

    A state is (strip in wiring order, slot within it, direction), plus
    one absorbing state for "past the shell".  Moving forward one slot
    is cheap, skipping empty slots costs per slot, and a new strip may
    be entered at either end -- the wiring is not a tidy boustrophedon,
    so direction is per strip and left to the data.
    """

    def __init__(self, xyz, strips, order):
        self.xyz = xyz
        self.normal = xyz / np.linalg.norm(xyz, axis=1, keepdims=True)
        self.strips = strips
        self.set_order(order)

    def set_order(self, order):
        self.order = list(order)
        self.states = []
        for g, nm in enumerate(self.order):
            L = len(self.strips[nm])
            for d in (+1, -1):
                for j in range(L):
                    self.states.append((g, j, d, self.strips[nm][j]))
        self.off = len(self.states)
        self.slot = np.array([s[3] for s in self.states])
        self._T = None

    def transitions(self):
        if self._T is not None:
            return self._T
        S = self.off + 1
        T = np.full((S, S), -np.inf, np.float32)
        at = {(g, j, d): n for n, (g, j, d, _) in enumerate(self.states)}
        size = [len(self.strips[nm]) for nm in self.order]
        for n, (g, j, d, _) in enumerate(self.states):
            L = size[g]
            for k in range(1, MAX_SKIP + 2):
                jj = j + d * k
                if 0 <= jj < L:
                    T[n, at[(g, jj, d)]] = LP_NEXT + LP_EMPTY * (k - 1)
            rest = (L - 1 - j) if d == +1 else j
            for g2 in range(g + 1, min(g + 1 + MAX_SKIP, len(self.order))):
                skipped = sum(size[q] for q in range(g + 1, g2))
                for d2 in (+1, -1):
                    for j2 in range(size[g2]):
                        before = j2 if d2 == +1 else size[g2] - 1 - j2
                        empty = rest + skipped + before
                        if empty <= MAX_SKIP:
                            T[n, at[(g2, j2, d2)]] = LP_STRIP + LP_EMPTY * empty
            T[n, self.off] = LP_OFF
        T[self.off, self.off] = 0.0
        self._T = T
        return T

    def start(self):
        s = np.full(self.off + 1, -np.inf, np.float32)
        size = [len(self.strips[nm]) for nm in self.order]
        for n, (g, j, d, _) in enumerate(self.states):
            if g <= 2:
                before = j if d == +1 else size[g] - 1 - j
                s[n] = LP_EMPTY * (before + sum(size[:g]))
        return s

    def emissions(self, cams, meas, upto):
        """How well each slot explains each LED's centroids.

        Cauchy rather than Gaussian, so one bad centroid costs a bounded
        amount, and a sigma that grows as the view turns edge-on.
        """
        E = np.zeros((upto, self.off + 1), np.float32)
        for name, M in cams.items():
            q = project(M, self.xyz)
            C = camera_centre(M)
            to_cam = C - self.xyz
            to_cam /= np.linalg.norm(to_cam, axis=1, keepdims=True)
            cosv = (to_cam * self.normal).sum(1)
            sig = SIGMA / np.clip(cosv, 0.06, 1.0)
            behind = cosv < -0.25
            for i in range(upto):
                if i not in meas[name]:
                    continue
                u, v = meas[name][i]
                e = np.hypot(q[:, 0] - u, q[:, 1] - v)
                ll = -np.log1p((e / sig) ** 2) - np.log(sig / SIGMA)
                ll[behind] -= 8.0
                E[i, :self.off] += ll[self.slot]
                E[i, self.off] += OFF_LL
        return E

    def viterbi(self, E):
        T = self.transitions()
        n, S = E.shape
        delta = self.start() + E[0]
        back = np.zeros((n, S), np.int32)
        for i in range(1, n):
            cand = delta[:, None] + T
            back[i] = cand.argmax(0)
            delta = cand[back[i], np.arange(S)] + E[i]
        path = np.zeros(n, np.int32)
        path[-1] = int(delta.argmax())
        for i in range(n - 1, 0, -1):
            path[i - 1] = back[i, path[i]]
        score = float(delta.max())
        return path, score

    def align(self, cams, meas, upto):
        path, score = self.viterbi(self.emissions(cams, meas, upto))
        return path, score

    def best_order(self, base, cams, meas, upto):
        """Try every order inside each ear-mount cluster; keep the best."""
        order = list(base)
        for cluster in CLUSTERS:
            members = [nm for nm in order if nm[6:9] in cluster]
            at = min(order.index(nm) for nm in members)
            best = None
            for perm in itertools.permutations(members):
                trial = list(order)
                trial[at:at + len(members)] = perm
                self.set_order(trial)
                _, score = self.align(cams, meas, upto)
                if best is None or score > best[0]:
                    best = (score, perm)
            order[at:at + len(members)] = best[1]
        self.set_order(order)
        return order


def shell_cameras(xyz_by_led, meas):
    cams, fit = {}, {}
    for name, m in meas.items():
        idx = [i for i in xyz_by_led if i in m]
        X = np.array([xyz_by_led[i] for i in idx])
        uv = np.array([m[i] for i in idx])
        M, e, keep = solve_camera(X, uv)
        cams[name] = M
        fit[name] = (float(np.median(e[keep])), int(keep.sum()), len(idx))
    return cams, fit


def solve_shell(xyz, strips, order, meas, upto=420, rounds=4, verbose=True):
    """Alternate: cameras from slots, slots from cameras.

    It starts from the CAD's own wiring order with no help from any
    earlier map -- every strip taken forward, nothing skipped -- which
    is wrong in places but right often enough to give two cameras good
    to about 15 px.  That is plenty for the first alignment.
    """
    naive = [s for nm in order for s in strips[nm]]
    start = {i: xyz[s] for i, s in enumerate(naive[:upto]) if i < len(naive)}
    cams, fit = shell_cameras(start, meas)
    if verbose:
        print("  cameras from the CAD wiring as drawn: %s"
              % ", ".join("%s %.1f px" % (k, v[0]) for k, v in fit.items()))
    shell = Shell(xyz, strips, order)
    for r in range(rounds):
        shell.best_order(order, cams, meas, upto)
        path, _ = shell.align(cams, meas, upto)
        on = {i: xyz[shell.slot[s]] for i, s in enumerate(path) if s != shell.off}
        cams, fit = shell_cameras(on, meas)
        if verbose:
            print("  round %d: %d shell LEDs, cameras %s" % (
                r + 1, len(on), ", ".join("%s %.2f px" % (k, v[0])
                                          for k, v in fit.items())))
    path, _ = shell.align(cams, meas, upto)
    return shell, path, cams


# ---------------------------------------------------------------- ears
def place_ears(geo, cams, meas, lo, hi, tube_spans, rim_span):
    """Ear LEDs onto the CAD ear: tubes by the camera, depth by the CAD.

    Each view's ray is met with the plane the tubes lie in, which gives
    a position across the disc.  Two views give two answers; they are
    averaged, weighted by how square-on each camera sees the disc.  Then
    each LED is put inside the tube it is nearest -- the camera says
    where along it and roughly which side, the CAD says the rest.
    """
    n, c = geo["normal"], geo["centre"]
    a, b = geo["along"], geo["across"]
    depth = float(np.mean([t["depth"] for t in geo["tubes"]]))
    p0 = c + depth * n
    seen = {}
    for i in range(lo, hi + 1):
        acc, wsum = np.zeros(2), 0.0
        for name, M in cams.items():
            if i not in meas[name]:
                continue
            C, d = ray(M, meas[name][i])
            denom = d @ n
            if abs(denom) < 1e-6:
                continue
            X = C + ((p0 - C) @ n) / denom * d
            w = abs(denom)
            acc += w * np.array([(X - c) @ a, (X - c) @ b])
            wsum += w
        if wsum:
            seen[i] = acc / wsum

    out, meta = {}, {}
    # Tubes numbered by height, 0 the lowest, judged at each tube's own
    # midpoint -- the tubes are diagonal, so "nearest the head" ranks the
    # middle one first.  Height is the same on both ears whichever way
    # each ear's own axes happen to point, so tube 1 is tube 1 on both.
    def mid_z(k):
        t = geo["tubes"][k]
        return (c + t["lat"] * b + 0.5 * (t["lo"] + t["hi"]) * a)[2]
    by_height = sorted(range(len(geo["tubes"])), key=mid_z)
    number = {k: by_height.index(k) for k in by_height}
    # Along a tube, 0 is the low end and 1 the high one -- up is up on
    # both ears, which is what an effect that "rises" means by it.
    up = 1.0 if a[2] >= 0 else -1.0
    # tube LEDs: hold each pass to a straight run inside its tube
    for t0, t1 in tube_spans:
        idx = [i for i in range(t0, t1 + 1) if i in seen]
        if not idx:
            continue
        lat = np.array([seen[i][1] for i in idx])
        k_tube = min(range(len(geo["tubes"])),
                     key=lambda k: abs(np.median(lat) - geo["tubes"][k]["lat"]))
        tube = geo["tubes"][k_tube]
        room = max(tube["radius"] - 5.0, 2.0)
        for i in range(t0, t1 + 1):
            if i in seen:
                al, la = seen[i]
            else:                  # unmeasured: halfway between neighbours
                nb = [seen[j] for j in (i - 1, i + 1) if j in seen]
                if not nb:
                    continue
                al, la = np.mean(nb, axis=0)
            al = min(max(al, tube["lo"]), tube["hi"])
            la = tube["lat"] + min(max(la - tube["lat"], -room), room)
            out[i] = c + al * a + la * b + tube["depth"] * n
            f = (al - tube["lo"]) / max(tube["hi"] - tube["lo"], 1e-6)
            meta[i] = (number[k_tube], round(f if up > 0 else 1.0 - f, 4))
    # Rim LEDs: on the rim, at the angle the camera saw.  Both cameras
    # agree they sit 172 mm out at mid-depth, which is the outer skin of
    # the rim band (166-173 mm on the mesh), so just inside that.
    r0, r1 = rim_span
    ring = geo["rim_outer"] - 1.5
    for i in range(r0, r1 + 1):
        if i in seen:
            al, la = seen[i]
        else:
            nb = [seen[j] for j in (i - 1, i + 1) if j in seen]
            if not nb:
                continue
            al, la = np.mean(nb, axis=0)
        # the rim circle's centre is the disc centre, in the plate frame
        ang = math.atan2(la, al)
        out[i] = c + ring * (math.cos(ang) * a + math.sin(ang) * b)
        # Round the rim from its lowest point, as a fraction of a turn,
        # measured in the disc's own plane.  The two ears are mirror
        # images, so the same fraction is the same place on each.
        zi = np.array([0.0, 0.0, 1.0]) - n * n[2]
        zi /= np.linalg.norm(zi)
        hz = np.cross(n, zi)
        X = out[i] - c
        meta[i] = (-1, round((math.atan2(X @ hz, -(X @ zi)) / (2 * math.pi)) % 1.0, 4))
    return out, meta


# ----------------------------------------------------------------- map
def az_el(x, y, z):
    az = math.degrees(math.atan2(x, -y)) % 360.0
    el = math.degrees(math.atan2(z, math.hypot(x, y)))
    return round(az, 2), round(el, 2)


def swapped(path=STRIPS):
    """Indices whose red and green are physically swapped.

    The rims are a different LED type.  Which LEDs that covers was
    measured by colour (mau5hue.py), and that file is what the output
    path corrects with, so the map's flag is read from it rather than
    kept as a second copy that can drift -- it had, by two LEDs.
    """
    out = set()
    if os.path.exists(path):
        for st in json.load(open(path)).get("strips", []):
            # 'order' is the strip relative to the bus: GRB is red and
            # green swapped, RGB would be no correction at all
            if str(st.get("order", "RGB")).upper() == "GRB":
                a = int(st["start"])
                out.update(range(a, a + int(st["count"])))
    return out


def build_rows(cad_rows, xyz, shell, path, ears, regions, ear_meta=None):
    swap = swapped()
    rows = []
    groups = []
    for i, s in enumerate(path):
        if s == shell.off:
            break
        g, j, d, slot = shell.states[s]
        groups.append((g, slot))
    n_shell = len(groups)
    # position within the installed strip, in chain order
    runs = collections.Counter(g for g, _ in groups)
    seen = collections.Counter()
    for i, (g, slot) in enumerate(groups):
        k = seen[g]
        seen[g] += 1
        x, y, z = (float(v) for v in xyz[slot])
        az, el = az_el(x, y, z)
        rows.append({
            "index": i, "region": "shell", "strip": cad_rows[slot]["strip"],
            "group": g, "pos_in_strip": k,
            "u": round(k / max(runs[g] - 1, 1), 4),
            "x": round(x, 2), "y": round(y, 2), "z": round(z, 2),
            "az_deg": az, "elev_deg": el, "source": "cad-slot",
            "swap_rg": 0, "tube": -1, "along": -1.0,
        })
    for name, lo, hi in regions:
        span = [i for i in range(lo, hi + 1)]
        for k, i in enumerate(span):
            if i not in ears:
                raise SystemExit("ear LED %d has no position" % i)
            x, y, z = (float(v) for v in ears[i])
            az, el = az_el(x, y, z)
            rows.append({
                "index": i, "region": name, "strip": name, "group": -1,
                "pos_in_strip": k, "u": round(k / max(len(span) - 1, 1), 4),
                "x": round(x, 2), "y": round(y, 2), "z": round(z, 2),
                "az_deg": az, "elev_deg": el, "source": "cad-ear",
                "swap_rg": 1 if i in swap else 0,
                "tube": (ear_meta or {}).get(i, (-1, -1.0))[0],
                "along": (ear_meta or {}).get(i, (-1, -1.0))[1],
            })
    rows.sort(key=lambda r: r["index"])
    if [r["index"] for r in rows] != list(range(TOTAL_N)):
        raise SystemExit("map does not cover 0..%d exactly" % (TOTAL_N - 1))
    return rows, n_shell


def write_map(rows, path=OUT):
    tmp = path + ".tmp"
    with open(tmp, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    os.replace(tmp, path)


def residual_report(rows, cams, meas):
    """Pixel error of the final map in each view, split by how square-on."""
    out = {}
    for name, M in cams.items():
        C = camera_centre(M)
        face, edge = [], []
        for r in rows:
            if r["region"] != "shell" or r["index"] not in meas[name]:
                continue
            X = np.array([r["x"], r["y"], r["z"]])
            q = project(M, X[None])[0]
            e = float(np.hypot(*(q - np.array(meas[name][r["index"]]))))
            cosv = float((C - X) @ X / (np.linalg.norm(C - X) * np.linalg.norm(X)))
            (face if cosv > 0.4 else edge).append(e)
        out[name] = {"square_on_median_px": round(float(np.median(face)), 2),
                     "square_on_90th_px": round(float(np.percentile(face, 90)), 2),
                     "square_on_n": len(face),
                     "edge_on_median_px": round(float(np.median(edge)), 2)}
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter,
                                 epilog=__doc__)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--out", default=OUT)
    a = ap.parse_args(argv)

    cad_rows, xyz, strips, order = load_cad()
    meas = {k: after_cut(load_centroids(p)) for k, p in POSES.items()}
    missing = [k for k, v in meas.items() if not v]
    if missing:
        raise SystemExit("no centroids for %s -- run mau5locate first" % missing)
    print("CAD: %d slots, chain B %d strips; centroids: %s"
          % (len(xyz), len(order), ", ".join("%s %d" % (k, len(v)) for k, v in meas.items())))

    shell, path, cams = solve_shell(xyz, strips, order, meas)
    on = [(i, shell.states[s]) for i, s in enumerate(path) if s != shell.off]
    n_shell = len(on)
    used = {st[3] for _, st in on}
    empty = [s for nm in shell.order for s in strips[nm] if s not in used]
    if len(used) != n_shell:
        raise SystemExit("alignment reused a slot -- this cannot happen")
    print("\nshell: %d LEDs (0..%d) in %d distinct CAD slots; %d empty: %s"
          % (n_shell, n_shell - 1, len(used), len(empty),
             ", ".join("%s led %s" % (cad_rows[s]["strip"][6:9], cad_rows[s]["led"])
                       for s in empty)))
    changed = [nm[6:9] for nm, base in zip(shell.order, order) if nm != base]
    print("  wired out of CAD order: %s" % " ".join(changed))
    # The check that makes it a measurement: each camera on its own,
    # through the whole pipeline -- its own start from the CAD, its own
    # camera fit, its own choice of order at the mounts.  Two views that
    # never saw each other's answer should land on the same slots.
    joint = [shell.slot[s] if s != shell.off else -1 for s in path]
    for name in meas:
        sh1, p1, _ = solve_shell(xyz, strips, order, {name: meas[name]}, verbose=False)
        alone = [sh1.slot[s] if s != sh1.off else -1 for s in p1]
        agree = sum(1 for a, b in zip(joint[:n_shell], alone[:n_shell]) if a == b)
        same_order = sh1.order == shell.order
        print("  the %s camera alone, start to finish: same slot for %d of %d%s"
              % (name, agree, n_shell, "" if same_order else " (mount order differs)"))

    V, F = load_mesh()
    parts = mesh_parts(V, F)
    geo = {e: ear_geometry(V, F, parts[e]) for e in ("ear1", "ear2")}
    for e, g in geo.items():
        print("%s: faces %s, centre (%s), rim radius %.0f mm, tubes at %s mm"
              % (e, np.round(g["normal"], 3), ", ".join("%.0f" % v for v in g["centre"]),
                 g["radius"], ", ".join("%+.0f" % t["lat"] for t in g["tubes"])))

    # Chain layout of the ears, from the walk and confirmed by watching
    # which ear lit: each ear's three tubes, each run out and back, then
    # the rims, which are one RGB-ordered run over the top of the head.
    # The near rim is one shorter than it was: see CUT.
    first = n_shell
    ear1_tubes = [(first, 425), (426, 461), (462, 491)]
    ear2_tubes = [(529, 556), (557, 592), (593, 620)]
    ears, ear_meta = {}, {}
    for e, lo, hi, spans, rim in (("ear1", first, 509, ear1_tubes, (492, 509)),
                                  ("ear2", 510, 620, ear2_tubes, (510, 528))):
        pos, meta = place_ears(geo[e], cams, meas, lo, hi, spans, rim)
        ears.update(pos)
        ear_meta.update(meta)
    regions = [("ear1_tubes", first, 491), ("ear1_rim", 492, 509),
               ("ear2_rim", 510, 528), ("ear2_tubes", 529, 620)]
    rows, _ = build_rows(cad_rows, xyz, shell, path, ears, regions, ear_meta)

    rep = residual_report(rows, cams, meas)
    for name, r in rep.items():
        print("  %s camera against the final shell: square-on %.2f px median "
              "(90th %.2f, n=%d), edge-on %.1f px"
              % (name, r["square_on_median_px"], r["square_on_90th_px"],
                 r["square_on_n"], r["edge_on_median_px"]))
    if a.dry_run:
        print("\n(dry run, nothing written)")
        return rows
    write_map(rows, a.out)
    report = {
        "shell_leds": n_shell,
        "empty_slots": [{"strip": cad_rows[s]["strip"], "led": int(cad_rows[s]["led"])}
                        for s in empty],
        "wiring_order": shell.order,
        "cameras": {k: M.tolist() for k, M in cams.items()},
        "residuals": rep,
    }
    # beside the map it describes, so a trial run elsewhere does not
    # overwrite the report for the real one
    rep_path = os.path.join(os.path.dirname(os.path.abspath(a.out)), os.path.basename(REPORT))
    with open(rep_path, "w") as f:
        json.dump(report, f, indent=1)
    print("\nwrote %s and %s" % (os.path.relpath(a.out, HERE), os.path.relpath(rep_path, HERE)))
    return rows


if __name__ == "__main__":
    main()
