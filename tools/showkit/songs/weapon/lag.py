import sys, numpy as np, os
KIT=sys.argv[1]; sys.path.insert(0,KIT); sys.path.insert(0,os.getcwd())
import grid
d=grid.env_of("shows/deadmau5 - Raise Your Weapon.mp3")
tt=d["tt"]; dt=tt[1]-tt[0]
M=np.stack([d[n] for n,_,_ in grid.BANDS],1)
def best(a0,a1,exp,w=3.0):
    i0,i1=int(a0/dt),int(a1/dt)
    A=M[i0:i1]-M[i0:i1].mean(0)
    res=[]
    for L in np.arange(exp-w,exp+w,dt):
        j0=int((a0+L)/dt); B=M[j0:j0+(i1-i0)]; B=B-B.mean(0)
        res.append(((A*B).sum()/np.sqrt((A*A).sum()*(B*B).sum()),L))
    res.sort(reverse=True)
    return res[0]
print("vocal 60-88 vs 210-238, expected 150:",best(60,88,150))
print("vocal 66-78 vs ...:",best(66,78,150))
print("vocal 78-87 vs ...:",best(78,87,150))
print("intro 0-28 vs outro? expected ~445 (at 128 vs 140 this will not match cleanly):",best(4,28,445,w=20))
