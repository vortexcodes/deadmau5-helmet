import sys,os
KIT=sys.argv[1]; sys.path.insert(0,KIT); sys.path.insert(0,os.getcwd())
import numpy as np, grid
d=grid.env_of("shows/deadmau5 - Strobe (Special Features Remix).mp3")
spb=0.46875; t0=0.136
tt=d["tt"]
CH=" .:-=+*#%@"
def line(nm,b0,b1,norm=None):
    v=d[nm]; 
    vmax=np.percentile(v,99.5)
    vmin=np.percentile(v,5)
    s=""
    for k in range(int(b0*16),int(b1*16)):
        a=t0+k*spb/4; c=a+spb/4
        i,j=np.searchsorted(tt,[a,c])
        x=(v[i:max(j,i+1)].mean()-vmin)/(vmax-vmin)
        s+=CH[int(np.clip(x,0,0.999)*10)]
        if (k+1)%16==0: s+="|"
    return s
for spec in sys.argv[2:]:
    a,b=[float(x) for x in spec.split("-")]
    print("bars",a,b)
    for nm in ("sub","mid","air"):
        print("  %-6s %s"%(nm,line(nm,a,b)))
