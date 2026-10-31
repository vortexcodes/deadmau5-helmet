import sys, numpy as np, os
KIT=sys.argv[1]; sys.path.insert(0,KIT); sys.path.insert(0,os.getcwd())
import grid
d=grid.env_of("shows/deadmau5 - Raise Your Weapon.mp3")
od=grid.onsets(d); tt=d["tt"]; dt=tt[1]-tt[0]
# best 16th phase in the 140 section
spb=60/140.
s16=spb/4
ph=np.arange(0,s16,0.001)
for lo,hi in [(242,300),(300,360),(360,430),(242,430)]:
    sc=[grid.comb(od,tt[0],dt,np.arange(lo+p,hi,s16)) for p in ph]
    i=int(np.argmax(sc))
    print(lo,hi,"phase %.3f -> first 16th at %.3f  contrast %.2f"%(ph[i],lo+ph[i],max(sc)/np.median(sc)))
# Onset list per band around the drop
for nm in ("sub","bass","lowmid","mid","pres","air"):
    e=d[nm+"_od"]
    a=np.searchsorted(tt,239.0); b=np.searchsorted(tt,246.0)
    x=e[a:b]
    idx=np.argsort(-x)[:14]
    print(nm," ".join("%.3f"%tt[a+i] for i in sorted(idx)))
