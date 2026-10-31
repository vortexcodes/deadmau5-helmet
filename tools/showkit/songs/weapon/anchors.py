import sys, numpy as np, os
KIT=sys.argv[1]; sys.path.insert(0,KIT); sys.path.insert(0,os.getcwd())
import grid
d=grid.env_of("shows/deadmau5 - Raise Your Weapon.mp3")
od=grid.onsets(d); tt=d["tt"]; dt=tt[1]-tt[0]
def phase(lo,hi,spb,nominal,band=None,step=0.0005):
    o=od if band is None else d[band+"_od"]
    s16=spb/4
    ph=np.arange(-s16/2,s16/2,step)
    sc=np.array([grid.comb(o,tt[0],dt,np.arange(nominal+p,hi,s16)) for p in ph])
    i=int(sc.argmax()); return nominal+ph[i], sc.max()/np.median(sc)
SA=0.46875; SC=60/140.
for lo,hi in [(90.03,150),(150,210),(90.03,210)]:
    n=0.027+SA*round((lo-0.027)/SA)
    p,c=phase(lo,hi,SA,n)
    print("A %6.1f-%6.1f  beat at %.4f -> bar0 anchor %.4f  contrast %.2f"%(lo,hi,p,p-(n-0.027),c))
for lo,hi in [(242.14,290),(290,340),(340,390),(390,434),(242.14,434)]:
    n=242.14+SC*round((lo-242.14)/SC)
    p,c=phase(lo,hi,SC,n)
    print("C %6.1f-%6.1f  beat at %.4f -> anchor(242.14) %.4f  contrast %.2f"%(lo,hi,p,p-(n-242.14),c))
# Per-band too: where does each band put the beat
for b in ("sub","bass","lowmid","mid","pres","air"):
    p,c=phase(90.03,210,SA,0.027+SA*192,band=b); q,e=phase(242.14,434,SC,242.14,band=b)
    print(b,"A anchor %.4f (%.2f)   C anchor %.4f (%.2f)"%(p-SA*192,c,q,e))
