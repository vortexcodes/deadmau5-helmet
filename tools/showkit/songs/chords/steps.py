#!/usr/bin/env python3
"""steps.py from to: per-16th level (L) and onset (O) of each band."""
import os,re,sys
import numpy as np
KIT="tools/showkit"
z=np.load(os.path.join(KIT,"work",re.sub(r"\W+","_","deadmau5 - Some Chords.mp3")+".env.npz"))
tt=z["tt"]; spb=0.468747; t0=0.218
B=["sub","bass","lowmid","mid","pres","air"]
lo,hi=float(sys.argv[1]),float(sys.argv[2])
s=lo
print("    bar   | level: "+" ".join("%6s"%b for b in B)+"  | onset: "+" ".join("%6s"%b for b in B))
while s<hi:
    a=t0+s*4*spb; b=a+spb/4
    i0,i1=np.searchsorted(tt,[a,b])
    lev=[z[n][i0:i1].mean() for n in B]; od=[z[n+"_od"][max(0,i0-1):i1+1].max() for n in B]
    print("%8.3f  | "%s+" ".join("%6.2f"%x for x in lev)+" | "+" ".join("%6.2f"%x for x in od))
    s+=1/16
