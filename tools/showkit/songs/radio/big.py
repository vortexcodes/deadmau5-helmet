#!/usr/bin/env python3
"""sheet.py "<base>" out.png bar[:label] bar[:label] ... -- the show at those bars as the helmet
will really look, through the power guard: a contact sheet, front view. Also prints, per tile, how
bright the shell and ears really are after the guard. Bars may be fractional: 40.25 is the second
beat of bar 40, so catch both a kick and the gap after it. Run from the repo root."""
import json, os, sys
sys.path.insert(0, os.getcwd())
import numpy as np, mau5show, mau5preview as PV
from PIL import Image, ImageDraw
base, out = sys.argv[1], sys.argv[2]
marks = []
for a in sys.argv[3:]:
    b, _, lab = a.partition(":")
    marks.append((float(b), lab))
show = json.load(open(os.path.join("shows", base + ".json")))
music = mau5show._music_for(show, os.path.join("shows", base + ".mp3"))
g = show["scenes"]["grid"]; spb = g["spb"]; t0 = g["t0"]
def tof(bar):
    B = 4 * bar
    return t0 + B * spb + sum(b * spb for at, b in g.get("holds", []) if B > at)
pl = mau5show.Player(show, music=music)
sc = PV.Scene(pl.h)
cols = int(os.environ.get("COLS","4")); W = int(os.environ.get("TW","480")); H = int(W*245/300)
rows = (len(marks) + cols - 1) // cols
o = Image.new("RGB", (cols * W, rows * H), (0, 0, 0))
d = ImageDraw.Draw(o)
h = pl.h
for k, (bar, lab) in enumerate(marks):
    t = tof(bar)
    for dt in (0.5, 0.3, 0.16, 0.08, 0.04):
        pl.frame(t - dt)
    f = np.asarray(pl.frame(t), float)
    im = sc.frame(f * pl.gain).crop((60, 40, 700, 560)).resize((W, H))
    o.paste(im, ((k % cols) * W, (k // cols) * H))
    d.text(((k % cols) * W + 5, (k // cols) * H + 3), "%s bar %g" % (lab, bar), fill=(255, 255, 255))
    d.text(((k % cols) * W + 5, (k // cols) * H + 15), pl.label[:42] if getattr(pl, "label", None) else "", fill=(180, 180, 180))
    s = f[h.shell]; e = f[h.ears]
    print("bar %-7g %-14s shell max %3.0f mean %5.1f   ears max %3.0f mean %5.1f   %s" % (bar, lab[:14], s.max(), s.mean(), e.max(), e.mean(), pl.label))
o.save(out)
print(out, o.size)
