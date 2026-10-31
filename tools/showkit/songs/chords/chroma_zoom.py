#!/usr/bin/env python3
"""chroma_zoom.py out.png from to : zoomed chromagram, with beat and bar lines (higher-resolution, shorter window)."""
import os, sys
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
W=os.path.dirname(os.path.abspath(__file__))
m=np.load(os.path.join(W,"mono.npy")); SR=22050
spb=0.468747; t0=0.218
NOTES="C C# D D# E F F# G G# A A# B".split()
out,lo,hi=sys.argv[1],float(sys.argv[2]),float(sys.argv[3])
N=4096
win=np.hanning(N)
f=np.fft.rfftfreq(N,1/SR)
def pcmap(lo,hi):
    idx=np.flatnonzero((f>=lo)&(f<hi))
    midi=69+12*np.log2(f[idx]/440.0)
    pc=np.round(midi).astype(int)%12
    w=np.exp(-0.5*((midi-np.round(midi))/0.3)**2)
    return idx,pc,w
bands=[("100-300",pcmap(100,300)),("300-800",pcmap(300,800)),("800-2500",pcmap(800,2500))]
steps=int((hi-lo)*32)
res={k:np.zeros((steps,12)) for k,_ in bands}
# long-window bass
NL=16384; winL=np.hanning(NL); fL=np.fft.rfftfreq(NL,1/SR)
idxL=np.flatnonzero((fL>=35)&(fL<110)); midiL=69+12*np.log2(fL[idxL]/440.0); pcL=np.round(midiL).astype(int)%12; wL=np.exp(-0.5*((midiL-np.round(midiL))/0.3)**2)
bassr=np.zeros((steps,12))
for i in range(steps):
    t=t0+(lo+(i+0.5)/32)*4*spb
    c=max(0,int(t*SR)-N//2); F=np.abs(np.fft.rfft(m[c:c+N]*win))**2
    for k,(idx,pc,w) in bands:
        np.add.at(res[k][i],pc,F[idx]*w)
    c=max(0,int(t*SR)-NL//2); fr=m[c:c+NL]
    if len(fr)==NL:
        FL=np.abs(np.fft.rfft(fr*winL))**2; np.add.at(bassr[i],pcL,FL[idxL]*wL)
fig,ax=plt.subplots(4,1,figsize=(22,11),sharex=True)
for a,(k,v) in zip(ax,[("bass 35-110",bassr)]+[(k,res[k]) for k,_ in bands]):
    n=np.sqrt(v/np.maximum(v.max(1,keepdims=True),1e-9))
    a.imshow(n.T,origin="lower",aspect="auto",cmap="magma",extent=[lo,hi,-0.5,11.5],interpolation="nearest")
    a.set_yticks(range(12)); a.set_yticklabels(NOTES); a.set_ylabel(k)
    a.set_xticks(np.arange(lo,hi+0.01,1))
    for b in np.arange(lo,hi,0.25):
        a.axvline(b,color="w",lw=0.25 if (b%1)!=0 else 1.0,alpha=0.5)
fig.tight_layout(); fig.savefig(out,dpi=70)
print(out)
