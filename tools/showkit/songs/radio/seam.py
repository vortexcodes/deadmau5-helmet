import sys, os
KIT=os.environ.get("KIT")
sys.path.insert(0, KIT); sys.path.insert(0, os.getcwd())
import numpy as np, grid as G
mp3="shows/deadmau5 - Some Chords (Radio Edit).mp3"
d=G.env_of(mp3)
tt=d["tt"]; dt=tt[1]-tt[0]
spb=0.46875; t0=0.124
od=G.onsets(d)
# print the strongest onsets between bars 60 and 80, with the time relative to the nearest 16th of the pre-seam grid
s16=spb/4
th={}
for lo,hi in [(64,72),(72,76),(76,80)]:
    a=t0+lo*4*spb; b=t0+hi*4*spb
    idx=np.where((tt>=a)&(tt<b))[0]
    v=od[idx]
    # local peaks
    pk=[i for i in range(1,len(v)-1) if v[i]>v[i-1] and v[i]>=v[i+1]]
    pk=sorted(pk,key=lambda i:-v[i])[:40]
    pk=sorted(pk)
    print("bars",lo,hi)
    for i in pk:
        t=tt[idx[i]]
        q=(t-t0)/s16
        print("  t %.3f  bar %.3f  off 16th %+.0f ms  strength %.2f"%(t,(t-t0)/(4*spb),(q-round(q))*s16*1000,v[i]))
