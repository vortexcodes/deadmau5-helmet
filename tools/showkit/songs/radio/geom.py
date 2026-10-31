import sys
sys.path.insert(0,'.')
import numpy as np, mau5engine as E
h=E.Helmet()
print("n",h.n)
for nm,m in [("shell",h.shell),("ear1",h.ear1),("ear2",h.ear2),("rims",h.rims),("tubes",h.tubes)]:
    m=np.asarray(m,bool)
    print(nm,m.sum(),"px %.0f..%.0f py %.0f..%.0f"%(h.px[m].min(),h.px[m].max(),h.py[m].min(),h.py[m].max()),
          "nfa %.2f..%.2f nel %.2f..%.2f er %.2f..%.2f ea %.2f..%.2f"%(h.nfa[m].min(),h.nfa[m].max(),h.nel[m].min(),h.nel[m].max(),h.er[m].min(),h.er[m].max(),h.ea[m].min(),h.ea[m].max()))
s=np.asarray(h.shell,bool)
print("shell y hist")
hist,edges=np.histogram(h.py[s],bins=np.arange(-110,180,20))
for c,e in zip(hist,edges): print("  y %4d..%4d: %3d"%(e,e+20,c))
print("shell x hist")
hist,edges=np.histogram(h.px[s],bins=np.arange(-200,201,25))
for c,e in zip(hist,edges): print("  x %4d..%4d: %3d"%(e,e+25,c))
W=110;H=44
grid=[[" "]*W for _ in range(H)]
xmin,xmax=-395,395; ymin,ymax=-115,390
for i in range(h.n):
    x=int((h.px[i]-xmin)/(xmax-xmin)*(W-1)); y=int((h.py[i]-ymin)/(ymax-ymin)*(H-1))
    ch="s" if h.shell[i] else ("o" if h.rims[i] else str(h.tube[i]))
    grid[H-1-y][x]=ch
print("\n".join("".join(r) for r in grid))
for t in range(3):
    m=np.asarray(h.tube)==t
    m1=m&np.asarray(h.ear1,bool)
    print("tube",t,"ear1 n",m1.sum(),"px %.0f..%.0f py %.0f..%.0f"%(h.px[m1].min(),h.px[m1].max(),h.py[m1].min(),h.py[m1].max()))
r1=np.asarray(h.rims)&np.asarray(h.ear1); r2=np.asarray(h.rims)&np.asarray(h.ear2)
print("ear rim1 center", h.px[r1].mean(), h.py[r1].mean(), "x range", h.px[r1].min(), h.px[r1].max())
print("ear rim2 center", h.px[r2].mean(), h.py[r2].mean(), "x range", h.px[r2].min(), h.px[r2].max())
# forehead strip
fh=s&(h.py>58)
print("dome LEDs",fh.sum(),"nel range on dome", h.nel[fh].min(), h.nel[fh].max(),"r range",h.er[fh].min(),h.er[fh].max())
print("shell er stats",np.percentile(h.er[s],[0,25,50,75,100]))
print("top of head points (x,y):", sorted([(round(float(h.px[i])),round(float(h.py[i]))) for i in np.where(s)[0] if h.py[i]>150])[:30])
