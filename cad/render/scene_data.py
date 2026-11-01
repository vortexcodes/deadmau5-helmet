import sys, json, math, numpy as np, csv
src = open("../source/mau5head_hat.py").read().replace('MESH_HOLES   = True','MESH_HOLES   = False')
_a = sys.argv; sys.argv = ["x", "visor"]; g = {"__name__": "__main__"}; exec(compile(src, "v18", "exec"), g); sys.argv = _a
tubes = []; ears = []
for (S, u, n, w) in g["ear_frames"]:
    O = S - g["TENON_D"]*u
    zl, zh, ztc = g["TUBE_Z"]
    tubes.append([list(O + u*(-8.0)), list(O + u*ztc)])
    for sx in (g["DOWEL_X"], -g["DOWEL_X"]):
        tubes.append([list(O + w*sx + u*zl), list(O + w*sx + u*zh)])
    ears.append({"u": list(u), "n": list(n), "w": list(w), "S": list(S)})
pix = [[float(r["x"]), float(r["y"]), float(r["z"])] for r in csv.DictReader(open((sys.argv[1] if len(sys.argv) > 1 else "../source/out/") + "pixel_map.csv"))]
json.dump({"tubes": tubes, "ears": ears, "pixels": pix, "R_O": g["R_O"], "tube_d": g["DOWEL_D"]}, open("glb/scene.json", "w"))
print(len(pix), "pixels", len(tubes), "tubes")
