import sys, os
sys.path.insert(0, os.getcwd()); sys.path.insert(0, os.environ["KIT"])
import numpy as np, grid
d = grid.env_of("shows/deadmau5 - FN Pig.mp3")
spb=0.46875; t0=0.490
tt=d["tt"]
CH=" .:-=+*#%@"
def fold(lo,hi,nbars=1,bands=("sub","bass","lowmid","mid","pres","air")):
    n=16*nbars
    print("bars %g-%g, fold over %d bars"%(lo,hi,nbars))
    for nm in bands:
        e=d[nm+"_od"]
        o=np.zeros(n); c=np.zeros(n)
        b=lo
        k=0
        while b+k/16<hi:
            t=t0+(b+k/16)*4*spb
            i=np.searchsorted(tt,t)
            o[k%n]+=e[max(0,i-2):i+3].max(); c[k%n]+=1
            k+=1
        o/=np.maximum(c,1)
        v=o/max(o.max(),1e-6)
        s=""
        for i in range(0,n,4):
            s+="".join(CH[min(9,int(a*9.99))] for a in v[i:i+4])
            s+=("||" if (i+4)%16==0 else "|")
        print("   %-7s %s peak %.2f"%(nm,s,o.max()))
def strip(lo,hi,bands=("sub","bass","lowmid","mid","pres","air"),level=False):
    """one row per bar, onset strength at 16 steps for the summed bands"""
    print("bars %g-%g per-bar onset strip (%s)"%(lo,hi,"+".join(bands)))
    e=sum(d[(nm+"_od") if not level else nm] for nm in bands)
    rows=[]
    for b in range(lo,hi):
        r=[]
        for k in range(16):
            t=t0+(b+k/16)*4*spb
            i=np.searchsorted(tt,t)
            r.append(e[max(0,i-2):i+3].max())
        rows.append(r)
    R=np.array(rows)
    m=np.percentile(R,99)
    for b,r in zip(range(lo,hi),R):
        s=""
        for i in range(0,16,4):
            s+="".join(CH[min(9,int(a/m*9.99))] for a in r[i:i+4])+"|"
        print("  %4d %7.2f  %s"%(b,t0+b*4*spb,s))
if __name__=="__main__":
    cmd=sys.argv[1]
    if cmd=="fold":
        fold(float(sys.argv[2]),float(sys.argv[3]),int(sys.argv[4]) if len(sys.argv)>4 else 1)
    else:
        bands=tuple(sys.argv[4].split(",")) if len(sys.argv)>4 else ("sub","bass","lowmid","mid","pres","air")
        strip(int(sys.argv[2]),int(sys.argv[3]),bands)
