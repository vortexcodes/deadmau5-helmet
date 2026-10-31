#!/usr/bin/env python3
"""sheet.py "<base>" out.png bar[:label] bar[:label] ... -- the show at those bars as the helmet will really look: through the real power guard (cold, settled for a second first), then gamma so the picture is what an eye sees. Prints per tile the mA sent and how bright shell and ears really are after the guard. Bars may be fractional: 40.25 is the second beat of bar 40, so catch both a kick and the gap after it. Env: COLS, TW, GAM. Run from the repo root. Credit: the Radio Edit author, who found the first version skipped the guard."""
import json, os, sys
sys.path.insert(0, os.getcwd())
import numpy as np, mau5show, mau5preview as PV, mau5scene as SS, mau5engine as E, mau5power
from PIL import Image, ImageDraw
base, out = sys.argv[1], sys.argv[2]
marks = []
for a in sys.argv[3:]:
    b, _, lab = a.partition(":")
    marks.append((float(b), lab))
show = json.load(open(os.path.join("shows", base + ".json")))
music = mau5show._music_for(show, os.path.join("shows", base + ".mp3"))
g = show["scenes"]["grid"]; spb = g["spb"]; t0 = g["t0"]
h = E.Helmet()
sc = PV.Scene(h); sc.back = sc.back * 0
scn = SS.Scenes(show["scenes"], h)
def tof(bar):
    B = 4 * bar
    return t0 + B * spb + sum(bb * spb for at, bb in g.get("holds", []) if B > at)
cols = int(os.environ.get("COLS","6")); W = int(os.environ.get("TW","300")); H = int(W*245/300)
GAM = float(os.environ.get("GAM","2.0"))
rows = (len(marks) + cols - 1) // cols
o = Image.new("RGB", (cols * W, rows * H), (0, 0, 0))
d = ImageDraw.Draw(o)
for k, (bar, lab) in enumerate(marks):
    t = tof(bar)
    guard = mau5power.load(count=h.n)
    for dt in (1.0, 0.8, 0.6, 0.5, 0.4, 0.3, 0.2, 0.12, 0.08, 0.04):
        f0, g0, _ = scn.frame(t - dt, music)
        guard.apply(f0, now=t - dt, gain=g0)
    f, gn, label = scn.frame(t, music)
    res, rep = guard.apply(f, now=t, gain=gn)
    res = np.asarray(res, float)
    arr = np.asarray(sc.frame(res), float)
    arr = 255.0 * np.clip(arr / 255.0, 0, 1) ** (1.0 / GAM)
    im = Image.fromarray(arr.astype(np.uint8)).crop((60, 40, 700, 560)).resize((W, H))
    o.paste(im, ((k % cols) * W, (k // cols) * H))
    d.text(((k % cols) * W + 5, (k // cols) * H + 3), "%s bar %g" % (lab, bar), fill=(255, 255, 255))
    d.text(((k % cols) * W + 5, (k // cols) * H + 15), (label or "")[:42], fill=(180, 180, 180))
    s = res[h.shell]; e = res[h.ears]
    print("bar %-7g %-10s sent %4.0f mA  shell max %3.0f mean %5.1f  ears max %3.0f mean %5.1f  %s" % (bar, lab[:10], rep["sent_ma"], s.max(), s.mean(), e.max(), e.mean(), label))
o.save(out)
print(out, o.size)
