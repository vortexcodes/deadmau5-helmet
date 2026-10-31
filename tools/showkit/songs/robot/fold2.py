import sys, os, re
import numpy as np
KIT=os.environ["KIT"]
z=np.load(os.path.join(KIT,"work",re.sub(r"\W+","_","deadmau5 - Harder Better Faster Stronger.mp3")+".env.npz"))
tt=z["tt"]; spb=0.468761; t0=0.003
CH=" .:-=+*#%@"
def fold(lo,hi,L=32,bands=("sub","bass","lowmid","mid","pres","air")):
    print("bars %d-%d, %d steps"%(lo,hi,L))
    for nm in bands:
        e=z[nm+"_od"]; o=np.zeros(L); n=0
        for b in range(lo,hi,L//16):
            n+=1
            for k in range(L):
                t=t0+(b+k/16)*4*spb; i=np.searchsorted(tt,t)
                o[k]+=e[max(0,i-2):i+3].max()
        o/=n; v=o/max(o.max(),1e-6)
        print("   %-7s %s"%(nm,"|".join("".join(CH[min(9,int(a*9.99))] for a in v[i:i+4]) for i in range(0,L,4))))
for lo,hi in ((12,20),(20,28),(28,36),(36,44),(60,68),(68,76),(92,108),(108,124),(124,140),(140,156)):
    fold(lo,hi)
