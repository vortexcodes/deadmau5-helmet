import sys, os
sys.path.insert(0, os.getcwd()); sys.path.insert(0, os.environ["KIT"])
import numpy as np, grid
d = grid.env_of("shows/deadmau5 - FN Pig.mp3")
spb=0.46875; t0=0.490; tt=d["tt"]
CH=" .:-=+*#%@"
def show(bars,bands=("sub","pres","air")):
    for nm in bands:
        v=d[nm]
        print(nm)
        for b in bars:
            r=[]
            for k in range(16):
                t=t0+(b+k/16)*4*spb
                i=np.searchsorted(tt,t); j=np.searchsorted(tt,t+spb/4)
                r.append(v[i:j].mean())
            print("  %4d "%b+" ".join("%4.1f"%x for x in r))
show([116,117,118,124,125,126,127,91,92,100,207,208,215,216])
