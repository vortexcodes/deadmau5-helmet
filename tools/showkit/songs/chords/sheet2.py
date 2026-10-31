#!/usr/bin/env python3
"""sheet2.py out.png cols bar[:label] ...  -- like the kit's sheet.py, but really through a guard (warmed for 4 s before each tile at the song's real level)."""
import json, os, sys
sys.path.insert(0, os.getcwd())
import numpy as np, mau5show, mau5preview as PV, mau5power
from PIL import Image, ImageDraw
base = os.environ.get("BASEN", "deadmau5 - Some Chords")
out = sys.argv[1]; cols = int(sys.argv[2])
marks = []
for a in sys.argv[3:]:
    b, _, lab = a.partition(":")
    marks.append((float(b), lab))
show = json.load(open(os.path.join("shows", base + ".json")))
music = mau5show._music_for(show, os.path.join("shows", base + ".mp3"))
g = show["scenes"]["grid"]; spb = g["spb"]; t0 = g["t0"]
tof = lambda bar: t0 + 4 * bar * spb
pl = mau5show.Player(show, music=music)
h = pl.h
sc = PV.Scene(h)
W = 300; H = 245
rows = (len(marks) + cols - 1) // cols
o = Image.new("RGB", (cols * W, rows * H), (0, 0, 0))
d = ImageDraw.Draw(o)
for k, (bar, lab) in enumerate(marks):
    t = tof(bar)
    guard = mau5power.load(count=h.n)
    for i in range(64, 0, -1):
        tt = t - i / 16.0
        f = np.asarray(pl.frame(tt), float)
        guard.apply(f, now=tt, gain=pl.gain)
    f = np.asarray(pl.frame(t), float)
    gf, rep = guard.apply(f, now=t, gain=pl.gain)
    gf = np.asarray(gf, float)
    im = sc.frame(gf).crop((60, 40, 700, 560)).resize((W, H))
    o.paste(im, ((k % cols) * W, (k // cols) * H))
    d.text(((k % cols) * W + 5, (k // cols) * H + 3), "%s bar %g" % (lab, bar), fill=(255, 255, 255))
    d.text(((k % cols) * W + 5, (k // cols) * H + 15), (pl.label or "")[:42], fill=(180, 180, 180))
    s = gf[h.shell]; e = gf[h.ears]
    print("bar %-7g %-10s shell max %3.0f mean %5.1f  ears max %3.0f mean %5.1f  sent %4.0f mA  %s" % (bar, lab[:10], s.max(), s.mean(), e.max(), e.mean(), rep["sent_ma"], pl.label))
o.save(out)
print(out, o.size)
