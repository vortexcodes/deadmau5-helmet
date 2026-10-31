import sys, os, json
sys.path.insert(0, os.getcwd())
import numpy as np, mau5engine as E
h=E.Helmet()
out=np.asarray(E.make("sprite",sprite="fnpig_snout0",color=(255,255,255),y_lo=52.0,y_hi=172.0,x_half=172.0).render(h,0.0,None),float)
lit=out[:,0]>0
PX,PY=h.px,h.py
s=h.shell
rows=np.array([167.8,162.9,156.6,148.7,139.6,129.1,117.4,104.6,90.9,76.3,61.0])
for y in rows:
    m=s&(np.abs(PY-y)<3)
    idx=np.where(m)[0]
    idx=idx[np.argsort(PX[idx])]
    line=""
    # map to 40mm-scale columns: print each LED in order with # or .
    print("%6.1f n=%2d x %6.1f..%6.1f  %s"%(y,len(idx),PX[idx[0]],PX[idx[-1]],"".join("#" if lit[i] else "." for i in idx)))
print(sorted(np.round(PX[s&(np.abs(PY-139.6)<3)]).astype(int).tolist()))
print(sorted(np.round(PX[s&(np.abs(PY-129.1)<3)]).astype(int).tolist()))
