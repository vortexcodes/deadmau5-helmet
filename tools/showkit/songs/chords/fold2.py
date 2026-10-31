#!/usr/bin/env python3
"""fold2.py lo hi period_bars : onset folded per 16th over a period, per band."""
import os,re,sys
import numpy as np
KIT="tools/showkit"
z=np.load(os.path.join(KIT,"work",re.sub(r"\W+","_","deadmau5 - Some Chords.mp3")+".env.npz"))
tt=z["tt"]; spb=0.468747; t0=0.218
B=["sub","bass","lowmid","mid","pres","air"]
CH=" .:-=+*#%@"
lo,hi,per=int(sys.argv[1]),int(sys.argv[2]),int(sys.argv[3])
print("bars %d-%d folded over %d bars"%(lo,hi,per))
for nm in B:
    e=z[nm+"_od"]; n=per*16; o=np.zeros(n); c=0
    for b in range(lo,hi,per):
        for k in range(n):
            t=t0+(b+k/16)*4*spb
            i=np.searchsorted(tt,t); o[k]+=e[max(0,i-2):i+3].max()
        c+=1
    o/=c; v=o/max(o.max(),1e-6)
    s="|".join("".join(CH[min(9,int(a*9.99))] for a in v[i:i+4]) for i in range(0,n,4))
    print("  %-7s %s  peak %.2f"%(nm,s,o.max()))
