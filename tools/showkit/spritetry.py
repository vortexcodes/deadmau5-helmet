#!/usr/bin/env python3
"""spritetry.py "<base>" out.png name [name ...] [--y_lo -108 --y_hi 166 --x_half 171] -- how a sprite
from shows/scenes/<base>.sprites.json lands on the real LEDs. Run from the repo root."""
import argparse, json, os, sys
sys.path.insert(0, os.getcwd())
import numpy as np, mau5engine as E, mau5preview as PV
from PIL import Image, ImageDraw
ap = argparse.ArgumentParser()
ap.add_argument("base"); ap.add_argument("out"); ap.add_argument("names", nargs="+")
ap.add_argument("--y_lo", type=float, default=-108.0); ap.add_argument("--y_hi", type=float, default=166.0)
ap.add_argument("--x_half", type=float, default=171.0)
a = ap.parse_args()
h = E.Helmet(); sc = PV.Scene(h)
ims = []
for nm in a.names:
    f = np.asarray(E.make("sprite", sprite=nm, color=(255, 170, 40), y_lo=a.y_lo, y_hi=a.y_hi, x_half=a.x_half).render(h, 0.0, None), float)
    im = sc.frame(f).crop((130, 150, 630, 620)).resize((360, 338))
    ImageDraw.Draw(im).text((6, 4), nm, fill=(255, 255, 255))
    ims.append(im)
o = Image.new("RGB", (sum(i.width for i in ims), ims[0].height))
x = 0
for i in ims:
    o.paste(i, (x, 0)); x += i.width
o.save(a.out); print(a.out, o.size)
