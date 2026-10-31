#!/usr/bin/env python3
"""lab.py: try layer variants without touching the show. Run from the repo root.
   from lab import sheet; sheet(out, [(label, pal_or_None, layers, beat), ...], palettes)"""
import sys, os
sys.path.insert(0, os.getcwd())
import numpy as np, mau5engine as E, mau5preview as PV, mau5scene as M
from PIL import Image, ImageDraw
H = E.Helmet()
SC = PV.Scene(H)
def sheet(out, items, palettes, cols=5, W=300, Hh=245):
    tr = {"v": 1, "show": "lab", "marks": {}, "palettes": palettes, "motifs": {}, "scenes": [], "hits": []}
    rows = (len(items) + cols - 1) // cols
    o = Image.new("RGB", (cols * W, rows * Hh), (0, 0, 0))
    d = ImageDraw.Draw(o)
    grid = {"t0": 0.0, "spb": 0.46875}
    for k, (lab, pal, layers, beat) in enumerate(items):
        tr["scenes"] = [{"name": "x", "from": 0, "to": 64, "pal": pal or next(iter(palettes)), "layers": layers}]
        spec = M.compile_treatment(tr, grid, 64, H)
        sc = M.Scenes(spec, H)
        f, g, _ = sc.frame(beat * 0.46875)
        s = np.asarray(f, float)
        im = SC.frame(s * g).crop((60, 40, 700, 560)).resize((W, Hh))
        o.paste(im, ((k % cols) * W, (k // cols) * Hh))
        d.text(((k % cols) * W + 5, (k // cols) * Hh + 3), lab, fill=(255, 255, 255))
        print("%-20s shell mean %5.1f max %3.0f  ears mean %5.1f max %3.0f" % (lab, s[H.shell].mean(), s[H.shell].max(), s[H.ears].mean(), s[H.ears].max()))
    o.save(out)
    print(out)
