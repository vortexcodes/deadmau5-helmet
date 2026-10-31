#!/usr/bin/env python3
"""like sheet.py, but through a real guard: gsheet.py base out.png cols bar[:label] ..."""
import json, os, sys
sys.path.insert(0, os.getcwd())
import numpy as np, mau5show, mau5preview as PV, mau5power
from PIL import Image, ImageDraw
base, out = sys.argv[1], sys.argv[2]
cols=int(sys.argv[3])
marks = []
for a in sys.argv[4:]:
    b, _, lab = a.partition(":")
    marks.append((float(b), lab))
show = json.load(open(os.path.join("shows", base + ".json")))
music = mau5show._music_for(show, os.path.join("shows", base + ".mp3"))
g = show["scenes"]["grid"]; spb = g["spb"]; t0 = g["t0"]
tof=lambda bar: t0+4*bar*spb
pl = mau5show.Player(show, music=music)
sc = PV.Scene(pl.h)
W = 1800//cols; H = int(W*0.8125)
rows = (len(marks) + cols - 1) // cols
o = Image.new("RGB", (cols * W, rows * H), (0, 0, 0))
d = ImageDraw.Draw(o)
h = pl.h
for k, (bar, lab) in enumerate(marks):
    guard=mau5power.load(count=h.n)
    t = tof(bar)
    for dt in (0.5, 0.4,0.3, 0.2, 0.16,0.12, 0.08, 0.04):
        f=pl.frame(t - dt); guard.apply(np.asarray(f,float).copy(),now=t-dt,gain=pl.gain)
    f = np.asarray(pl.frame(t), float)
    f2,rep = guard.apply(f.copy(),now=t,gain=pl.gain)
    f2=np.asarray(f2,float)
    im = sc.frame(255*(np.clip(f2,0,255)/255)**0.6).crop((60, 40, 700, 560)).resize((W, H))
    o.paste(im, ((k % cols) * W, (k // cols) * H))
    d.text(((k % cols) * W + 5, (k // cols) * H + 3), "%s bar %g %dmA" % (lab, bar, rep["sent_ma"]), fill=(255, 255, 255))
    d.text(((k % cols) * W + 5, (k // cols) * H + 15), pl.label[:42] if getattr(pl, "label", None) else "", fill=(180, 180, 180))
    s = f2[h.shell]; e = f2[h.ears]
    print("bar %-7g %-10s shell max %3.0f mean %5.1f   ears max %3.0f mean %5.1f  sent %4.0f  %s" % (bar, lab[:10], s.max(), s.mean(), e.max(), e.mean(), rep["sent_ma"], pl.label))
o.save(out)
print(out, o.size)
