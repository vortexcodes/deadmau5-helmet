import sys, os, json
sys.path.insert(0, os.getcwd())
import numpy as np, mau5show
base="deadmau5 - Some Chords (Radio Edit)"
show=json.load(open("shows/%s.json"%base))
music=mau5show._music_for(show,"shows/%s.mp3"%base)
print([k for k in dir(music) if not k.startswith('__')][:40])
g=show.get("scenes",{}).get("grid") if isinstance(show.get("scenes"),dict) else None
print("grid",g)
t0=0.124; spb=0.46875
def tof(bar):
    t=t0+4*bar*spb
    if t>=135.1: t+=0.032
    return t
for b in sys.argv[1:]:
    bar=float(b)
    print("bar",bar)
    for band in ("bass","mid","high"):
        for punch in (False,True):
            vals=[music.band_at(tof(bar+k/16),band,punch=punch) for k in range(16)]
            print("  %-5s %-5s "%(band,"punch" if punch else "env")+" ".join("%.2f"%v for v in vals))
