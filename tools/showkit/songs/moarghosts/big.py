#!/usr/bin/env python3
"""big.py "<base>" out.png bar bar ...: like sheet.py but bigger tiles. Run from the repo root."""
import json, os, sys
sys.path.insert(0, os.getcwd())
import numpy as np, mau5show, mau5preview as PV
from PIL import Image, ImageDraw
base, out = sys.argv[1], sys.argv[2]
bars = [float(x) for x in sys.argv[3:]]
show = json.load(open(os.path.join("shows", base + ".json")))
music = mau5show._music_for(show, os.path.join("shows", base + ".mp3"))
g = show["scenes"]["grid"]; spb = g["spb"]; t0 = g["t0"]
pl = mau5show.Player(show, music=music)
sc = PV.Scene(pl.h)
cols = 4; W = 480; H = 390
rows = (len(bars) + cols - 1) // cols
o = Image.new("RGB", (cols * W, rows * H), (0, 0, 0))
d = ImageDraw.Draw(o)
for k, bar in enumerate(bars):
    t = t0 + 4 * bar * spb
    for dt in (0.5, 0.3, 0.16, 0.08, 0.04):
        pl.frame(t - dt)
    f = np.asarray(pl.frame(t), float)
    im = sc.frame(f * pl.gain).crop((60, 40, 700, 560)).resize((W, H))
    o.paste(im, ((k % cols) * W, (k // cols) * H))
    d.text(((k % cols) * W + 5, (k // cols) * H + 3), "bar %g  %s" % (bar, pl.label[:50]), fill=(255, 255, 255))
o.save(out)
print(out, o.size)
