#!/usr/bin/env python3
"""Top line of the lead per 8th: strongest narrow peak 500-1400 Hz in the harmonic-ish spectrum."""
import os,sys
import numpy as np
W=os.path.dirname(os.path.abspath(__file__))
m=np.load(os.path.join(W,"mono.npy")); SR=22050
spb=0.468747; t0=0.218
NOTES="C C# D D# E F F# G G# A A# B".split()
lo,hi=float(sys.argv[1]),float(sys.argv[2])
N=8192; win=np.hanning(N); f=np.fft.rfftfreq(N,1/SR)
sel=np.flatnonzero((f>=450)&(f<1500))
midi=69+12*np.log2(f[sel]/440.0)
keys=np.arange(int(np.floor(midi.min())),int(np.ceil(midi.max()))+1)
rows=[]
s=lo
while s<hi:
    t=t0+(s+1/32)*4*spb
    c=max(0,int(t*SR)-N//2); fr=m[c:c+N]
    F=np.abs(np.fft.rfft(fr*win))[sel]**2
    e=np.array([F[np.abs(midi-k)<0.4].sum() for k in keys])
    top=np.argsort(-e)[:3]
    rows.append((s,[ (keys[j],e[j]) for j in top]))
    s+=1/16
last=None
for s,tp in rows:
    k=tp[0][0]
    txt="%s%d"%(NOTES[k%12],k//12-1)
    if k!=last:
        print("%8.3f  %-4s (%d)   next: %s"%(s,txt,k," ".join("%s%d"%(NOTES[a%12],a//12-1) for a,_ in tp[1:])))
    last=k
