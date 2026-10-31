import sys, os
sys.path.insert(0, os.getcwd())
import numpy as np, mau5engine as E
h = E.Helmet()
print("n", h.n, "shell", h.shell.sum(), "ears", h.ears.sum())
px, py = h.px, h.py
s = h.shell
print("shell px range", px[s].min(), px[s].max(), "py range", py[s].min(), py[s].max())
print("ear1 px", px[h.ear1].min(), px[h.ear1].max(), "py", py[h.ear1].min(), py[h.ear1].max())
print("ear2 px", px[h.ear2].min(), px[h.ear2].max(), "py", py[h.ear2].min(), py[h.ear2].max())
# ascii density at 17x17 cells with y_lo -108 y_hi 166 x_half 171
R,C = 28, 40
y_lo,y_hi,x_half=-108.,166.,171.
g=np.zeros((R,C),int)
rr=((y_hi-py[s])/(y_hi-y_lo)*R).astype(int); cc=((px[s]+x_half)/(2*x_half)*C).astype(int)
for r,c in zip(rr,cc):
    if 0<=r<R and 0<=c<C: g[r,c]+=1
for r in range(R):
    print("%6.0f "%(y_hi-(r+.5)*(y_hi-y_lo)/R)+"".join(("%x"%min(15,v) if v else ".") for v in g[r]))
for t in (0,1,2):
    m=np.asarray(h.tube)==t
    print("tube",t,"count",m.sum(),"ear1 x",px[m&h.ear1].min(),px[m&h.ear1].max(),"y",py[m&h.ear1].min(),py[m&h.ear1].max())
m=h.rims&h.ear1
print("rim1 count",m.sum(),"x",px[m].min(),px[m].max(),"y",py[m].min(),py[m].max())
m=h.rims&h.ear2
print("rim2 count",m.sum(),"x",px[m].min(),px[m].max(),"y",py[m].min(),py[m].max())
print("attrs",[a for a in dir(h) if not a.startswith('_')])
