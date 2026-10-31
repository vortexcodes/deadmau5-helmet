#!/usr/bin/env python3
import os, sys
import numpy as np
W=os.path.dirname(os.path.abspath(__file__))
z=np.load(os.path.join(W,"hchroma.npz")); tt=z["tt"]
spb=0.468747; t0=0.218
NOTES="C C# D D# E F F# G G# A A# B".split()
low=z["low"]; mid=z["mid"]; high=z["high"]
C=np.sqrt(low)+0.8*np.sqrt(mid)+0.3*np.sqrt(high)
nsteps=int((tt[-1]-t0)/(spb/4))
tem={}
for r in range(12):
    for q,iv in (("",(0,4,7)),("m",(0,3,7))):
        v=np.zeros(12); 
        for k,i in enumerate(iv): v[(r+i)%12]=[1,0.8,0.8][k]
        tem[NOTES[r]+q]=v/np.linalg.norm(v)
names=list(tem); M=np.stack([tem[n] for n in names])
labs=[]; score=[]
for s in range(nsteps):
    a=t0+s*(spb/4); b=a+spb/4
    sel=(tt>=a)&(tt<b)
    v=C[sel].mean(0)
    v=v/max(np.linalg.norm(v),1e-9)
    sc=M@v
    j=sc.argmax()
    labs.append(names[j]); score.append(sc[j])
# smooth: majority over +-1 step
out=[]
start=0
for s in range(1,nsteps+1):
    if s==nsteps or labs[s]!=labs[start]:
        out.append((start,s,labs[start],np.mean(score[start:s])))
        start=s
lo=float(sys.argv[1]) if len(sys.argv)>1 else 0; hi=float(sys.argv[2]) if len(sys.argv)>2 else 1e9
minlen=int(sys.argv[3]) if len(sys.argv)>3 else 2
for a,b,l,sc in out:
    if a/16<lo or a/16>=hi: continue
    if b-a<minlen: continue
    print("bar %8.3f  len %5.2f bars  %-4s  %.2f"%(a/16,(b-a)/16,l,sc))
