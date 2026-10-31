#!/usr/bin/env python3
"""gsheet.py out.png bar[:label] ... -- the show as it really leaves the guard: the whole song is walked
through a fresh mau5power guard at 30 fps, so the ceilings, the region budgets, the governor and the heat
are all as they would be at that moment. sheet.py's own tiles are the raw scene output, before any of that."""
import json, os, sys
sys.path.insert(0, os.getcwd())
import numpy as np, mau5power, mau5show, mau5scene as M, mau5preview as PV
from PIL import Image, ImageDraw
B = os.environ.get("BASE", "deadmau5 & Wolfgang Gartner - Animal Rights")
out = sys.argv[1]
marks = []
for a in sys.argv[2:]:
    b, _, lab = a.partition(":")
    marks.append((float(b), lab))
show = json.load(open(os.path.join("shows", B + ".json")))
music = mau5show._music_for(show, os.path.join("shows", B + ".mp3"))
g = show["scenes"]["grid"]; spb = g["spb"]; t0 = g["t0"]
pl = mau5show.Player(show, music=music)
h = pl.h
sc = PV.Scene(h)
guard = mau5power.load(count=h.n)
fps = 30.0
want = sorted(range(len(marks)), key=lambda k: marks[k][0])
times = {k: t0 + 4 * marks[k][0] * spb for k in want}
res = {}
dur = float(show["duration"])
i = 0
jq = 0
n = int(dur * fps)
while i < n and jq < len(want):
    t = i / fps
    # step exactly onto each wanted time, so the sampled phase is the one asked for
    k = want[jq]
    if t + 1 / fps > times[k]:
        t = times[k]
        jq += 1
        f = np.asarray(pl.frame(t), float)
        o, rep = guard.apply(f, now=t, gain=pl.gain)
        res[k] = (np.asarray(o, float), rep, pl.label)
        continue
    f = np.asarray(pl.frame(t), float)
    guard.apply(f, now=t, gain=pl.gain)
    i += 1
cols = 6; W = 300; H = 245
rows = (len(marks) + cols - 1) // cols
im = Image.new("RGB", (cols * W, rows * H), (0, 0, 0))
d = ImageDraw.Draw(im)
for k, (bar, lab) in enumerate(marks):
    o, rep, label = res[k]
    tile = sc.frame(o).crop((60, 40, 700, 560)).resize((W, H))
    im.paste(tile, ((k % cols) * W, (k // cols) * H))
    d.text(((k % cols) * W + 5, (k // cols) * H + 3), "%s bar %g" % (lab, bar), fill=(255, 255, 255))
    d.text(((k % cols) * W + 5, (k // cols) * H + 15), (label or "")[:40], fill=(180, 180, 180))
    s = o[h.shell]; e = o[h.ears]
    print("bar %-7g %-10s shell max %3.0f mean %5.1f   ears max %3.0f mean %5.1f   %4.0f mA  %s" % (bar, lab[:10], s.max(), s.mean(), e.max(), e.mean(), rep["sent_ma"], label))
im.save(out)
print(out, im.size)
