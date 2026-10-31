#!/usr/bin/env python3
"""Per-8th-note chromagram for Some Chords: bass band and mid band, printed and drawn."""
import os, subprocess, sys
import numpy as np
SR=22050
mp3="shows/deadmau5 - Some Chords.mp3"
W=os.path.dirname(os.path.abspath(__file__))
cache=os.path.join(W,"mono.npy")
if os.path.exists(cache):
    m=np.load(cache)
else:
    raw=subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-i",mp3,"-ac","1","-ar",str(SR),"-f","f32le","-"],capture_output=True,check=True).stdout
    m=np.frombuffer(raw,dtype=np.float32).copy(); np.save(cache,m)
spb=0.468747; t0=0.218
NOTES="C C# D D# E F F# G G# A A# B".split()
N=8192
win=np.hanning(N)
f=np.fft.rfftfreq(N,1/SR)
def pcmap(lo,hi):
    idx=np.flatnonzero((f>=lo)&(f<hi))
    midi=69+12*np.log2(f[idx]/440.0)
    pc=np.round(midi).astype(int)%12
    w=np.exp(-0.5*((midi-np.round(midi))/0.25)**2)
    return idx,pc,w
bands={"bass":pcmap(35,130),"low":pcmap(130,500),"mid":pcmap(500,2000)}
nb=int((len(m)/SR-t0)/(spb/2))
out={k:np.zeros((nb,12)) for k in bands}
for i in range(nb):
    t=t0+(i+0.5)*(spb/2)
    c=int(t*SR)-N//2
    if c<0: c=0
    fr=m[c:c+N]
    if len(fr)<N: break
    F=np.abs(np.fft.rfft(fr*win))**2
    for k,(idx,pc,w) in bands.items():
        np.add.at(out[k][i],pc,F[idx]*w)
np.savez(os.path.join(W,"chroma.npz"),**out)
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
fig,ax=plt.subplots(3,1,figsize=(24,9),sharex=True)
for a,(k,v) in zip(ax,out.items()):
    n=v/np.maximum(v.max(1,keepdims=True),1e-9)
    a.imshow(n.T,origin="lower",aspect="auto",cmap="magma",extent=[0,nb/8,-0.5,11.5],interpolation="nearest")
    a.set_yticks(range(12)); a.set_yticklabels(NOTES); a.set_ylabel(k)
    a.set_xticks(range(0,nb//8,4))
    a.grid(axis="x",color="w",lw=0.3,alpha=0.5)
fig.tight_layout(); fig.savefig(os.path.join(W,"chroma_all.png"),dpi=70)
print("ok",nb)
