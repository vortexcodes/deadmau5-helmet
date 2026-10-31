#!/usr/bin/env python3
# per bar, 16 steps: onset strength in a band: a piano roll of the groove.
import sys, os, re
import numpy as np
KIT=os.environ["KIT"]
z=np.load(os.path.join(KIT,"work",re.sub(r"\W+","_","deadmau5 - Harder Better Faster Stronger.mp3")+".env.npz"))
tt=z["tt"]; spb=0.468761; t0=0.003
CH=" .:-=+*#%@"
bands=sys.argv[1].split(","); lo=int(sys.argv[2]); hi=int(sys.argv[3]); kind=sys.argv[4] if len(sys.argv)>4 else "od"
for nm in bands:
    e=z[nm+("_od" if kind=="od" else "")]
    # normalise globally
    M=[]
    for b in range(lo,hi):
        row=[]
        for k in range(16):
            t=t0+(b+k/16)*4*spb; i=np.searchsorted(tt,t); j=np.searchsorted(tt,t+spb/4)
            if kind=="od":
                row.append(e[max(0,i-2):i+3].max())
            else:
                row.append(e[i:j].mean())
        M.append(row)
    M=np.nan_to_num(np.array(M))
    if kind!="od":
        M=M-np.percentile(M,2)
    top=np.percentile(M,99)
    print(nm, "(bar: | every beat)")
    for b,row in zip(range(lo,hi),M):
        v=np.clip(row/max(top,1e-6),0,0.999)
        print("%4d "%b+"|".join("".join(CH[int(a*10)] for a in v[i:i+4]) for i in range(0,16,4)))
