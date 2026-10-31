#!/usr/bin/env python3
"""Harmonic part of the whole song, chroma per 16th, saved, then drawn for ranges."""
import os, sys
import numpy as np
from numpy.lib.stride_tricks import sliding_window_view as swv
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
W=os.path.dirname(os.path.abspath(__file__))
m=np.load(os.path.join(W,"mono.npy")); SR=22050
spb=0.468747; t0=0.218
NOTES="C C# D D# E F F# G G# A A# B".split()
N=4096; H=512
win=np.hanning(N)
nf=(len(m)-N)//H
S=np.zeros((nf,N//2+1),np.float32)
for s in range(0,nf,4000):
    e=min(s+4000,nf)
    fr=np.stack([m[i*H:i*H+N] for i in range(s,e)])*win
    S[s:e]=np.abs(np.fft.rfft(fr,axis=1))
print("stft",S.shape)
# median across time keeps sustained tones
nb=int(2600/(SR/N))
S=S[:,:nb]
H_=np.zeros_like(S)
for b in range(nb):
    H_[:,b]=np.median(swv(np.pad(S[:,b],15,mode="edge"),31),axis=1)
P_=np.zeros_like(S)
for s_ in range(0,nf,4000):
    e_=min(s_+4000,nf)
    P_[s_:e_]=np.median(swv(np.pad(S[s_:e_],((0,0),(15,15)),mode="edge"),31,axis=1),axis=2)
mask=(H_**2)/(H_**2+P_**2+1e-9)
HS=S*mask
f=np.fft.rfftfreq(N,1/SR)[:nb]
tt=(np.arange(nf)*H+N/2)/SR
def chroma(lo,hi):
    idx=np.flatnonzero((f>=lo)&(f<hi))
    midi=69+12*np.log2(f[idx]/440.0)
    pc=np.round(midi).astype(int)%12
    w=np.exp(-0.5*((midi-np.round(midi))/0.3)**2)
    C=np.zeros((nf,12),np.float32)
    for k in range(12):
        sel=pc==k
        C[:,k]=(HS[:,idx[sel]]**2*w[sel]).sum(1)
    return C
bands={"bass":chroma(35,110),"low":chroma(110,300),"mid":chroma(300,800),"high":chroma(800,2500)}
np.savez(os.path.join(W,"hchroma.npz"),tt=tt,**bands)
print("saved")
