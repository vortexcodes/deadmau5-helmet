#!/usr/bin/env python3
"""The real check for this grid: the written beat list, 16ths interpolated within each beat, against the audio, per 8 bars.
grid.py check cannot read a grid with hundreds of holds (it applies each hold by comparing an unheld time to a real one)."""
import sys, numpy as np, os
KIT=sys.argv[1]; sys.path.insert(0,KIT); sys.path.insert(0,os.getcwd())
import grid
BASE="deadmau5 - Raise Your Weapon"
d=grid.env_of("shows/%s.mp3"%BASE)
od=grid.onsets(d); tt=d["tt"]; dt=tt[1]-tt[0]
beats=np.loadtxt("shows/scenes/%s.beats"%BASE)
def sixteenths(b0,b1):
    out=[]
    for k in range(b0,min(b1,len(beats)-1)):
        out+=list(beats[k]+(beats[k+1]-beats[k])*np.arange(4)/4)
    return np.array(out)
rows=[]
for bar in range(0,283,8):
    ts=sixteenths(bar*4,(bar+8)*4)
    if len(ts)<8: break
    ph=np.arange(-0.055,0.055,0.002)
    sc=np.array([grid.comb(od,tt[0],dt,ts+p) for p in ph])
    rows.append((bar,float(ph[sc.argmax()]*1000),float(sc.max()/max(np.median(sc),1e-6)),float(beats[bar*4])))
print("  ".join("%d:%+.0f(%.2f)"%(r[0],r[1],r[2]) for r in rows))
good=[r for r in rows if r[2]>=1.15]
print("worst %.0f ms where contrast >= 1.15, mean %+.1f ms, %d of %d spans"%(max(abs(r[1]) for r in good),np.mean([r[1] for r in good]),len(good),len(rows)))
