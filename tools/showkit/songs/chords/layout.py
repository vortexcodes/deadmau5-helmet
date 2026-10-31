import os,sys
sys.path.insert(0,os.getcwd())
import numpy as np, mau5engine as E
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
h=E.Helmet()
W=os.path.dirname(os.path.abspath(__file__))
print(h.n, h.shell.sum(), h.ears.sum())
print("px",h.px.min(),h.px.max(),"py",h.py.min(),h.py.max())
s=h.shell
print("shell px",h.px[s].min(),h.px[s].max(),"py",h.py[s].min(),h.py[s].max())
print("shell er",h.er[s].min(),h.er[s].max(),"ea",h.ea[s].min(),h.ea[s].max())
print("shell nfa",h.nfa[s].min(),h.nfa[s].max(),"nel",h.nel[s].min(),h.nel[s].max())
print("ear1 px",h.px[h.ear1].min(),h.px[h.ear1].max(),"py",h.py[h.ear1].min(),h.py[h.ear1].max())
print("ear2 px",h.px[h.ear2].min(),h.px[h.ear2].max(),"py",h.py[h.ear2].min(),h.py[h.ear2].max())
fig,ax=plt.subplots(2,3,figsize=(21,13))
for a,(nm,v) in zip(ax.flat,[("a (ea)",h.ea),("r (er)",h.er),("x (nfa)",h.nfa),("y (nel)",h.nel),("al (along)",h.along),("tube",np.asarray(h.tube,float))]):
    sc=a.scatter(h.px,h.py,c=v,s=18,cmap="turbo"); a.set_title(nm); a.set_aspect("equal"); plt.colorbar(sc,ax=a)
fig.tight_layout(); fig.savefig(os.path.join(W,"layout.png"),dpi=60)
