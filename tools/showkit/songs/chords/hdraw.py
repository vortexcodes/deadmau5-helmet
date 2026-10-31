#!/usr/bin/env python3
import os, sys
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
W=os.path.dirname(os.path.abspath(__file__))
z=np.load(os.path.join(W,"hchroma.npz")); tt=z["tt"]
spb=0.468747; t0=0.218
NOTES="C C# D D# E F F# G G# A A# B".split()
out,lo,hi=sys.argv[1],float(sys.argv[2]),float(sys.argv[3])
bar=(tt-t0)/(4*spb)
sel=(bar>=lo)&(bar<hi)
fig,ax=plt.subplots(4,1,figsize=(22,11),sharex=True)
for a,k in zip(ax,("bass","low","mid","high")):
    v=z[k][sel]
    n=np.sqrt(v/np.maximum(np.percentile(v.max(1),95),1e-9))
    a.imshow(n.T,origin="lower",aspect="auto",cmap="magma",extent=[lo,hi,-0.5,11.5],interpolation="nearest",vmin=0,vmax=1)
    a.set_yticks(range(12)); a.set_yticklabels(NOTES); a.set_ylabel(k)
    st=1 if hi-lo<=40 else 4
    a.set_xticks(np.arange(lo,hi+0.01,st))
    if hi-lo<=40:
        for b in np.arange(lo,hi,1):
            a.axvline(b,color="w",lw=0.5,alpha=0.5)
fig.tight_layout(); fig.savefig(out,dpi=70)
print(out)
