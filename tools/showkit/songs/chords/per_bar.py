#!/usr/bin/env python3
import os,re,sys
import numpy as np
KIT="tools/showkit"
z=np.load(os.path.join(KIT,"work",re.sub(r"\W+","_","deadmau5 - Some Chords.mp3")+".env.npz"))
tt=z["tt"]; spb=0.468747; t0=0.218
B=["sub","bass","lowmid","mid","pres","air"]
lo,hi=int(sys.argv[1]),int(sys.argv[2])
print("bar | beat-onset per band (x10) | offbeat-8th onset | mean level")
for b in range(lo,hi):
    on=[];off=[];lev=[]
    for nm in B:
        e=z[nm+"_od"]; 
        a=0;c=0
        for k in range(16):
            t=t0+(b+k/16)*4*spb
            i=np.searchsorted(tt,t); v=e[max(0,i-2):i+3].max()
            if k%4==0:a+=v/4
            elif k%2==0:c+=v/4
        on.append(a);off.append(c)
        i0,i1=np.searchsorted(tt,[t0+b*4*spb,t0+(b+1)*4*spb]); lev.append(z[nm][i0:i1].mean())
    print("%4d | "%b+" ".join("%2d"%min(99,round(x*10)) for x in on)+" | "+" ".join("%2d"%min(99,round(x*10)) for x in off)+" | "+" ".join("%2d"%min(99,round(x*5)) for x in lev))
