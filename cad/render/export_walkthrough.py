#!/usr/bin/env python3
"""export_walkthrough.py -- meshes and placement data for the CAD walkthrough film.

Reads the committed STEP files in cad/parts and cad/assembly, and the perforated visor in
cad/visor. Every mesh keeps its B-rep faces apart, so the normals are smooth inside a face and
sharp at a CAD edge, and carries its feature edges as line segments. Nothing is simplified.

Where a part exists only flat, ready to print (ear halves, pivot cap, seam plate, spacers), its
assembled placement is taken from the generator's own variables, not typed in here: the script
runs cad/source/mau5head_hat.py's parameter and placement code (stage "visor") in a temp folder
and writes the results to scene.json.

    python3 export_walkthrough.py BUILD [--thick DIR]

BUILD gets mesh/*.bin, mesh/manifest.json and scene.json. --thick names an `out/` folder from a
rerun of the generator with EAR_T = 90, for the "a change is a rerun" shot; see README.md.
"""
import argparse
import contextlib
import csv
import io
import json
import math
import os
import sys
import tempfile

import cadquery as cq
import numpy as np
import trimesh

HERE = os.path.dirname(os.path.abspath(__file__))
CAD = os.path.dirname(HERE)
REPO = os.path.dirname(CAD)


def tess(shape, tol, ang):
    """(vertices, faces), vertices shared only inside one B-rep face."""
    v, f = shape.tessellate(tol, ang)
    return np.array([p.toTuple() for p in v], np.float32), np.array(f, np.uint32)


def normals(v, f):
    fn = np.cross(v[f[:, 1]] - v[f[:, 0]], v[f[:, 2]] - v[f[:, 0]]).astype(np.float64)
    n = np.zeros_like(v, np.float64)
    for i in range(3):
        np.add.at(n, f[:, i], fn)
    n /= np.maximum(np.linalg.norm(n, axis=1, keepdims=True), 1e-12)
    return n.astype(np.float32)


def feature_edges(v, f, deg=28.0):
    m = trimesh.Trimesh(v.astype(np.float64), f, process=True)
    keep = m.face_adjacency_angles > math.radians(deg)
    return m.vertices[m.face_adjacency_edges[keep]].astype(np.float32).reshape(-1, 3)


MANIFEST = {}


def save(out, name, v, f, n=None, edges=None):
    n = normals(v, f) if n is None else n
    e = feature_edges(v, f) if edges is None else edges
    with open(os.path.join(out, f"{name}.bin"), "wb") as fh:
        fh.write(v.tobytes()); fh.write(n.tobytes()); fh.write(f.astype(np.uint32).tobytes()); fh.write(e.tobytes())
    MANIFEST[name] = {"nv": len(v), "nf": len(f), "ne": len(e),
                      "min": v.min(0).tolist(), "max": v.max(0).tolist()}
    print(f"  {name:22s} {len(f):8d} tris  {len(e)//2:7d} edges  "
          f"x {v[:,0].min():7.1f} {v[:,0].max():7.1f}  y {v[:,1].min():7.1f} {v[:,1].max():7.1f}  z {v[:,2].min():7.1f} {v[:,2].max():7.1f}", flush=True)


def step(path):
    """Everything in the file, however many solids the kernel left it as."""
    return cq.Compound.makeCompound(cq.importers.importStep(path).vals())


def generator_data():
    """Run the generator's parameter and placement code, stage "visor", in a temp folder."""
    src = open(os.path.join(CAD, "source", "mau5head_hat.py")).read()
    g = {"__name__": "__main__"}
    argv, cwd = sys.argv, os.getcwd()
    with tempfile.TemporaryDirectory() as tmp:
        os.chdir(tmp); sys.argv = ["x", "visor"]
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                exec(compile(src, "mau5head_hat.py", "exec"), g)
        finally:
            os.chdir(cwd); sys.argv = argv
    return g


def plane_matrix(origin, xdir, normal):
    """Same frame as cq.Plane(origin, xDir, normal): columns x, y, z, origin."""
    z = np.array(normal, float); z /= np.linalg.norm(z)
    x = np.array(xdir, float); x -= z * (x @ z); x /= np.linalg.norm(x)
    y = np.cross(z, x)
    m = np.eye(4); m[:3, 0], m[:3, 1], m[:3, 2], m[:3, 3] = x, y, z, origin
    return m.T.flatten().tolist()     # column-major, for THREE.Matrix4.fromArray


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("build")
    ap.add_argument("--thick", help="out/ folder of a generator rerun with EAR_T = 90")
    ap.add_argument("--only", help="comma list of mesh names to redo")
    a = ap.parse_args()
    out = os.path.join(a.build, "mesh"); os.makedirs(out, exist_ok=True)
    mf = os.path.join(out, "manifest.json")
    if a.only and os.path.exists(mf):
        MANIFEST.update(json.load(open(mf)))
    want = lambda n: (not a.only) or n in a.only.split(",")
    P = os.path.join(CAD, "parts")
    S = os.path.join(CAD, "assembly")

    jobs = [("shell_top", P + "/shell_half_TOP.step", 0.08, 0.10),
            ("shell_bottom", P + "/shell_half_BOTTOM.step", 0.08, 0.10),
            ("supports", P + "/shell_half_TOP_supports.step", 0.1, 0.2),
            ("ear_top", P + "/ear_half_top.step", 0.06, 0.08),
            ("ear_bottom", P + "/ear_half_bottom.step", 0.06, 0.08),
            ("pivot_cap", P + "/pivot_cap.step", 0.02, 0.1),
            ("seam_plate", P + "/seam_plate.step", 0.02, 0.1),
            ("crown_frame", P + "/hat_crown_frame.step", 0.05, 0.1),
            ("tray", P + "/electronics_tray.step", 0.03, 0.15),
            ("hat", S + "/hardhat_envelope_REFERENCE.step", 0.1, 0.06),
            ("wm_bracket", P + "/wallmount_bracket.step", 0.05, 0.15),
            ("wm_cradle", P + "/wallmount_cradle.step", 0.05, 0.1),
            ("wm_post", P + "/wallmount_post.step", 0.05, 0.1),
            ("wm_dome", P + "/wallmount_dome.step", 0.05, 0.08)]
    if a.thick:
        jobs += [("ear_top_thick", a.thick + "/ear_half_top.step", 0.06, 0.08),
                 ("ear_bottom_thick", a.thick + "/ear_half_bottom.step", 0.06, 0.08)]
    for name, path, tol, ang in jobs:
        if want(name):
            v, f = tess(step(path), tol, ang)
            save(out, name, v, f)

    if want("visor"):
        m = trimesh.load(os.path.join(CAD, "visor", "visor_A_2.9mm-holes_3.8-pitch_RECOMMENDED.3mf"), force="mesh")
        s = m.smooth_shaded
        v, f = np.asarray(s.vertices, np.float32), np.asarray(s.faces, np.uint32)
        save(out, "visor", v, f, edges=np.zeros((0, 3), np.float32))

    # the spacers are a laid-out grid of 16 solids: one mesh per height
    if want("spacer_2"):
        solids = step(P + "/hat_spacers.step").Solids()
        seen = {}
        for s in solids:
            bb = s.BoundingBox()
            h = round(bb.zlen)
            if h not in seen:
                seen[h] = s
                v, f = tess(s.moved(cq.Location(cq.Vector(-bb.center.x, -bb.center.y, -bb.zmin))), 0.02, 0.1)
                save(out, f"spacer_{h}", v, f)
        print("  spacer solids:", len(solids), "heights", sorted(seen))

    g = generator_data()

    # tubes: 1" OD x 3/4" ID, cut to the build guide's lengths (1/8" short of the bores)
    zlo, zhi, ztc = g["TUBE_Z"]
    OD, ID = g["DOWEL_D"], g["TUBE_ID"]
    L_C, L_S = 13.375 * 25.4, 9.75 * 25.4
    if want("tube_c"):
        for name, L in (("tube_c", L_C), ("tube_s", L_S)):
            s = cq.Workplane("XY").circle(OD / 2).circle(ID / 2).extrude(L).val()
            v, f = tess(s, 0.015, 0.06)
            save(out, name, v, f)
    json.dump(MANIFEST, open(mf, "w"), indent=0)

    # ── placements, in the helmet frame ──
    scene = {"R_O": g["R_O"], "R_I": g["R_I"], "NECK_Z": g["NECK_Z"], "SPLIT_Z": g["SPLIT_Z"],
             "params": {k: g[k] for k in ("R_O", "WALL", "SKIN", "PIX", "PIX_HI", "GROOVE_W", "GROOVE_D", "N_CH", "PITCH", "EAR_W", "EAR_H",
                                          "EAR_T", "EAR_RIM_T", "TENON_W", "TENON_T", "TENON_D", "VISOR_R", "VISOR_T", "OPEN_ANGLE",
                                          "PIN_D", "PAD_D", "THICK_T", "HUB_ARC", "MAG_X", "MAG_EL", "BOLT_X", "PAD_LEN", "PAD_ACROSS", "PAD_T", "PLATE_T")}}
    ears = []
    for (S_, u, n, w) in g["ear_frames"]:
        org = S_ - g["TENON_D"] * u
        ears.append({"u": list(map(float, u)), "n": list(map(float, n)), "w": list(map(float, w)), "S": list(map(float, S_)),
                     "m": plane_matrix(org, w, u)})
    scene["ears"] = ears
    # tube local origin at its bottom end, +Z along the tube, in the ear frame (peg tip at z = 0)
    seat = g["DOWEL_SEAT"]
    gap_c = (ztc + seat) - L_C
    scene["tubes_ear"] = [{"x": 0.0, "z0": -seat + gap_c / 2, "L": L_C, "kind": "tube_c"},
                          {"x": g["DOWEL_X"], "z0": zlo + (zhi - zlo - L_S) / 2, "L": L_S, "kind": "tube_s"},
                          {"x": -g["DOWEL_X"], "z0": zlo + (zhi - zlo - L_S) / 2, "L": L_S, "kind": "tube_s"}]
    scene["ear_zc"] = g["TENON_D"] - g["DISC_SINK"] + g["EAR_H"] / 2
    # seam plates, exactly as the generator places them in mau5head_ASSEMBLY.step
    plates = []
    for jp in g["pad_channels"]:
        az = (jp + 0.5) * g["DAZ"]
        d = g["dirv"](az, g["SPLIT_LAT"])
        east = np.array([-math.sin(math.radians(az)), math.cos(math.radians(az)), 0.0])
        plates.append({"m": plane_matrix(d * (g["R_I"] - g["PAD_T"] - g["PLATE_T"]), east, d), "d": list(map(float, d)), "az": az})
    scene["plates"] = plates
    # pivot caps: the pocket bottoms on the pin end, the base faces the middle of the head
    xp = g["X_PIN_END"]
    scene["caps"] = [{"m": plane_matrix((s * (xp - g["CAP_BASE"]), 0, 0), (0, 1, 0), (s, 0, 0)), "s": s} for s in (1, -1)]
    scene["X_PIN_END"] = xp
    # spacer stacks: one of each height under each hat pad, 16 at the pad
    scene["hat_pts"] = [{"x": p[0], "y": p[1], "z": g["hat_pad_z"][p]} for p in g["HAT_PTS"]]
    scene["spacers"] = list(g["SPACER_HS"])
    # magnets: 6 x 3 discs seated in their pockets
    mv = [list(map(float, p)) for p in g["mag_visor"]]
    ms = [list(map(float, p)) for p in g["mag_shell"]]
    scene["mag_visor"], scene["mag_shell"] = mv, ms
    scene["mag_r_visor"] = g["RV_O"] + 3.4 - g["MAG_T"] / 2
    scene["mag_r_shell"] = g["R_I"] - 3.2 + g["MAG_T"] / 2
    scene["crown_pts"] = [list(map(float, q)) for q in g["crown_pts"]]
    scene["tray_pts"] = [list(map(float, d)) for d in g["tray_pts"]]
    scene["conn"] = list(map(float, g["dirv"](g["CONN_AZ"], g["CONN_LAT"]) * g["R_O"]))
    scene["wall_y"] = g["R_O"] + 28.0
    scene["post_z"] = -150.0            # wall_mount.py: post_bot = ARM_TOP_Z + NOM, the nominal middle pin hole

    # ── the LEDs as built: data/cal/pixel_map.csv, 621 rows ──
    rows = list(csv.DictReader(open(os.path.join(REPO, "data", "cal", "pixel_map.csv"))))
    leds = []
    for r in rows:
        leds.append([float(r["x"]), float(r["y"]), float(r["z"]), r["region"], int(r["tube"])])
    scene["leds"] = leds
    # all 948 CAD windows, for the "only the front ones are used" shot
    win = []
    for j, k, az, lat in g["pixels"] if "pixels" in g else []:
        d = g["dirv"](az, lat) * g["R_O"]
        win.append([float(d[0]), float(d[1]), float(d[2]), g["PIX"] if lat <= g["LAT_MAX_ALL"] else g["PIX_HI"]])
    scene["windows"] = win
    print("windows", len(win), "leds", len(leds))

    # the parameter block as written, for the "CAD is code" shot
    src = open(os.path.join(CAD, "source", "mau5head_hat.py")).read().splitlines()
    scene["source_lines"] = src
    json.dump(scene, open(os.path.join(a.build, "scene.json"), "w"))


if __name__ == "__main__":
    main()
