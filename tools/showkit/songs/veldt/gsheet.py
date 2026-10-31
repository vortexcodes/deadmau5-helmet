#!/usr/bin/env python3
"""gsheet.py "<base>" out.png bar[:label] ... -- like sheet.py but the frames really go through the power guard:
the whole song is run through a fresh guard at 25 fps, so the thermal state is right, and each tile is what leaves the guard.
Prints per tile: shell and ear levels and mA. Optional: --scale N to multiply the display for reading dim tiles (default 1)."""
import json, os, sys
sys.path.insert(0, os.getcwd())
import numpy as np, mau5show, mau5preview as PV, mau5power, mau5scene, mau5engine as E
from PIL import Image, ImageDraw
args=sys.argv[1:]
scale=1.0
if "--scale" in args:
    i=args.index("--scale"); scale=float(args[i+1]); del args[i:i+2]
cols=6
if "--cols" in args:
    i=args.index("--cols"); cols=int(args[i+1]); del args[i:i+2]
BIG=False
if "--big" in args:
    i=args.index("--big"); BIG=True; del args[i]
base, out = args[0], args[1]
marks = []
for a in args[2:]:
    b, _, lab = a.partition(":")
    marks.append((float(b), lab))
show = json.load(open(os.path.join("shows", base + ".json")))
music = mau5show._music_for(show, os.path.join("shows", base + ".mp3"))
g = show["scenes"]["grid"]; spb = g["spb"]; t0 = g["t0"]
def tof(bar):
    B = 4 * bar
    return t0 + B * spb + sum(b * spb for at, b in g.get("holds", []) if B > at)
h = E.Helmet()
scn = mau5scene.Scenes(show["scenes"], h)
sc = PV.Scene(h)
guard = mau5power.load(count=h.n)
times = sorted((tof(b), k) for k, (b, _) in enumerate(marks))
W = 300; H = 245
if BIG:
    W, H = 500, 406
rows = (len(marks) + cols - 1) // cols
o = Image.new("RGB", (cols * W, rows * H), (0, 0, 0))
d = ImageDraw.Draw(o)
fps = 25.0
tnow = 0.0
ti = 0
res = {}
dur = float(show["duration"])
step = 1 / fps
ts = list(np.arange(0.0, dur, step))
# merge: run frames in order, adding exact times of the requested tiles
want = {round(t, 6): k for t, k in times}
allt = sorted(set([round(x, 6) for x in ts]) | set(want))
last = None
for t in allt:
    outf, gain, label = scn.frame(t, music)
    sent, rep = guard.apply(outf, now=t, gain=gain)
    if t in want:
        k = want[t]
        sent = np.asarray(sent, float)
        bar, lab = marks[k]
        im = sc.frame(sent * scale).crop((60, 40, 700, 560)).resize((W, H))
        o.paste(im, ((k % cols) * W, (k // cols) * H))
        d.text(((k % cols) * W + 5, (k // cols) * H + 3), "%s bar %g" % (lab, bar), fill=(255, 255, 255))
        d.text(((k % cols) * W + 5, (k // cols) * H + 15), label[:42], fill=(180, 180, 180))
        sh = sent[h.shell]; e = sent[h.ears]
        th = rep.get("thermal") or {}
        print("bar %-7g %-14s shell max %3.0f mean %5.1f   ears max %3.0f mean %5.1f   sent %4.0f mA  heat %4.1f%%  %s" % (bar, lab[:14], sh.max(), sh.mean(), e.max(), e.mean(), rep["sent_ma"], th.get("full_pct", 0.0), label))
o.save(out)
print(out, o.size)
