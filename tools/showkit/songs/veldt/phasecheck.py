import sys, os
sys.path.insert(0, os.getcwd()); sys.path.insert(0, sys.argv[1])
import numpy as np, grid
d=grid.env_of("shows/deadmau5 - The Veldt.mp3")
for spb in (0.468725,0.468735,0.468745,0.46875,0.468755):
    rows,t0=grid.phase_table(d,spb,0.040275)
    vals=[r[1] for r in rows if r[2]>=1.15]
    print("spb %.6f  BPM %.3f  mean %+.1f  span %.1f   "%(spb,60/spb,np.mean(vals),max(vals)-min(vals))+"  ".join("%d:%+.0f"%(r[0],r[1]) for r in rows))
