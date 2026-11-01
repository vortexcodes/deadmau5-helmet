"""Tessellate the current CAD into GLBs for the three.js renderer (helmet frame, mm)."""
import sys, os, math, numpy as np, trimesh, cadquery as cq, csv, json
H = sys.argv[1] if len(sys.argv) > 1 else "../source/out/"          # mau5head_hat.py output
W = sys.argv[2] if len(sys.argv) > 2 else "../source/out/"          # wall_mount.py output
VISOR = sys.argv[3] if len(sys.argv) > 3 else "../visor/visor_A_2.9mm-holes_3.8-pitch_RECOMMENDED.3mf"
os.makedirs("glb", exist_ok=True)
def tess(path, tol=0.25, ang=0.35):
    s = cq.importers.importStep(path).val(); v, f = s.tessellate(tol, ang)
    return trimesh.Trimesh(np.array([p.toTuple() for p in v]), np.array(f))
def save(name, m, target=None):
    if target and len(m.faces) > target:
        import fast_simplification as fs
        v, f = fs.simplify(m.vertices.astype(np.float32), m.faces.astype(np.int32), target_reduction=1 - target/len(m.faces))
        m = trimesh.Trimesh(v, f)
    m.export(f"glb/{name}.glb"); print(name, len(m.faces))
save("shell", tess(H+"shell.step", 0.3, 0.4), 260000)
for n in ("ear_L", "ear_R", "pivot_cap", "electronics_tray", "hat_crown_plate", "hardhat_envelope_REFERENCE"):
    save(n, tess(H+(n if n != "hat_crown_plate" else "hat_crown_frame")+".step", 0.3, 0.4), 120000)
save("visor_solid", tess(H+"visor.step", 0.3, 0.4))
vm = trimesh.load(VISOR, force="mesh"); save("visor", vm)
for n in ("bracket", "cradle", "post", "dome"):
    save("wm_"+n, tess(W+f"wallmount_{n}.step", 0.3, 0.4))
for n in ("shell_half_TOP", "shell_half_BOTTOM"):
    save(n, tess(H+n+".step", 0.3, 0.4))
