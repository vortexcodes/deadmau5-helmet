#!/usr/bin/env python3
"""
Perforate the visor: an even hex field of holes on a sphere, out to the edges, then a mesh boolean.

    python3 visor_perforate.py                      # variant A: 2.9 mm holes, 3.8 mm spacing (recommended)
    python3 visor_perforate.py --hole 2.5 --pitch 3.4 --out visor_B.3mf

Needs: cadquery, numpy, scipy, trimesh, manifold3d.  Reads the visor shape straight from mau5head_hat.py
(runs its 'visor' stage with the B-rep holes switched off), so any change to the visor there carries over.

Why it is done this way
  * Cutting 3,000+ holes in the B-rep takes hours and makes a 240 MB STEP. Tessellating the solid visor once and
    subtracting all the cylinders in a single manifold3d boolean takes ~10 s and gives a clean watertight mesh.
  * A hex grid laid out in angles about the pivot axis (the first version) crowds toward the sides, because the
    visor is a lune and every row converges on the pivots: 3.8 mm in the middle became 2.7 mm at the ends.
    Here rows are horizontal (constant latitude about Z, which never converge across the visor), and a short
    repulsion pass then removes the shear between rows that builds up toward the sides.  Result: spacing within
    ~5 % everywhere.
  * Keep-outs: the solid edge rims, the pivot hubs, the magnet pads and the grab lip.
"""
import argparse, math, os, sys, time
import numpy as np
from scipy.spatial import cKDTree

ap = argparse.ArgumentParser()
ap.add_argument("--hole", type=float, default=2.9, help="hole diameter, mm")
ap.add_argument("--pitch", type=float, default=3.8, help="hole spacing, mm")
ap.add_argument("--out", default="visor_perforated.3mf", help=".3mf or .stl")
ap.add_argument("--clear", type=float, default=0.8, help="min solid between a hole and any keep-out, mm")
a = ap.parse_args()

# ── visor geometry from the generator ─────────────────────────────────────────
here = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(here, "mau5head_hat.py")).read().replace("MESH_HOLES   = True", "MESH_HOLES   = False")
_argv = sys.argv; sys.argv = ["mau5head_hat.py", "visor"]; g = {"__name__": "__main__"}
exec(compile(src, "mau5head_hat.py", "exec"), g); sys.argv = _argv
RV_O, T = g["RV_O"], g["VISOR_T"]; R = RV_O - T/2
ET, EB = g["E_TOP"], g["E_BOT"]; RIM_W, HUB = g["RIM_W"], g["HUB_ARC"]
MAGS = np.array([list(map(float, p)) for p in g["mag_visor"]]); LIP_X = g["LIP_HALF_X"]
PITCH, D = a.pitch, a.hole

def theta(d): return np.degrees(np.arctan2(d[:, 2], -d[:, 1]))        # elevation about the pivot (X) axis
def edge_dist(d):
    x = d[:, 0]; rho = np.sqrt(np.clip(1 - x*x, 0, 1)); th = np.radians(theta(d))
    top = R*np.arcsin(np.clip(rho*np.sin(math.radians(ET) - th), -1, 1))
    bot = R*np.arcsin(np.clip(rho*np.sin(th - math.radians(EB)), -1, 1))
    return top, bot, R*np.arccos(np.clip(np.abs(x), 0, 1))
def keep(d, r, clr):
    top, bot, pole = edge_dist(d)
    ok = (d[:, 1] < 0) & (top >= RIM_W + r + clr) & (bot >= RIM_W + r + clr) & (pole >= HUB + r + clr)
    pts = d*RV_O
    for m in MAGS: ok &= np.linalg.norm(pts - m, axis=1) >= 6.0 + r + clr
    dl = math.degrees((r + clr)/R)
    ok &= ~((np.abs(pts[:, 0]) < LIP_X + r + clr) & (theta(d) < -31.5 + dl))
    return ok
def domain(d):
    top, bot, pole = edge_dist(d)
    return (d[:, 1] < 0) & (top > 2) & (bot > 2) & (pole > 10)

# ── 1. seed: hex rows of constant latitude ────────────────────────────────────
pts = []; lat = math.radians(-45); i = 0
while lat < math.radians(25):
    c = math.cos(lat); daz = PITCH/(R*c); off = 0.5*daz if i % 2 else 0.0
    az = -math.pi/2 + off - math.floor((math.pi/2)/daz)*daz
    while az < 0.0:
        if az > -math.pi: pts.append((c*math.cos(az), c*math.sin(az), math.sin(lat)))
        az += daz
    lat += PITCH*0.8660/R; i += 1
d = np.array(pts); d = d[domain(d)]
# ── 2. relax: short-range repulsion toward the target pitch ───────────────────
for it in range(250):
    pr = cKDTree(d*R).query_pairs(PITCH, output_type="ndarray")
    v = d[pr[:, 0]] - d[pr[:, 1]]; dist = np.linalg.norm(v, axis=1)*R
    f = (np.clip(PITCH - dist, 0, None)/PITCH)[:, None]*v/(np.linalg.norm(v, axis=1)[:, None] + 1e-12)
    mv = np.zeros_like(d); np.add.at(mv, pr[:, 0], f); np.add.at(mv, pr[:, 1], -f)
    dn = d + 0.25*mv*(PITCH/R); dn /= np.linalg.norm(dn, axis=1)[:, None]
    ins = domain(dn); d[ins] = dn[ins]
d = d[keep(d, D/2, a.clear)]
nn = cKDTree(d*R).query(d*R, k=2)[0][:, 1]
print(f"{len(d)} holes  spacing p1/median {np.percentile(nn, 1):.2f}/{np.median(nn):.2f} mm  "
      f"web min/typ {np.percentile(nn, 1) - D:.2f}/{np.median(nn) - D:.2f} mm  open ≈ {100*np.mean(np.pi*D*D/4/(0.866*nn**2)):.0f}%")

# ── 3. one boolean ────────────────────────────────────────────────────────────
import trimesh
t0 = time.time()
vs, fs = g["visor"].val().tessellate(0.03, 0.12)
base = trimesh.Trimesh(np.array([p.toTuple() for p in vs]), np.array(fs), process=True); trimesh.repair.fix_normals(base)
cyl = trimesh.creation.cylinder(radius=D/2, height=5.0, sections=24); tools = []
for u in d:
    M = trimesh.geometry.align_vectors([0, 0, 1], u); M[:3, 3] = u*(RV_O - 1.0)
    c = cyl.copy(); c.apply_transform(M); tools.append(c)
out = trimesh.boolean.difference([base, trimesh.util.concatenate(tools)], engine="manifold")
out.export(a.out)
print(f"{a.out}: watertight={out.is_watertight} bodies={out.body_count} {time.time() - t0:.0f}s")
