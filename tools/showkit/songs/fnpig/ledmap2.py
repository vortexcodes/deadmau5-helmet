import sys
sys.path.insert(0,'.')
import numpy as np, mau5engine as E
h=E.Helmet()
s=h.shell
# rows on the shell
ys=np.round(h.py[s]/3)*3
vals,c=np.unique(np.round(h.py[s]),return_counts=True)
# cluster rows
pts=sorted(zip(h.py[s],h.px[s]))
rows=[]
cur=[pts[0]]
for p in pts[1:]:
    if abs(p[0]-cur[-1][0])<3.0: cur.append(p)
    else:
        rows.append(cur);cur=[p]
rows.append(cur)
for r in rows[::-1]:
    xs=sorted(x for _,x in r)
    print("y %7.1f n %3d x %7.1f .. %7.1f gaps>30: %s"%(np.mean([y for y,_ in r]),len(r),xs[0],xs[-1],[(round(a),round(b)) for a,b in zip(xs,xs[1:]) if b-a>30]))
