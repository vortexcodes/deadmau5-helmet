#!/usr/bin/env python3
"""try.py out.png spec ... ; spec = name[:mode[:dy]] mode p (positive) or s (silhouette on a sun). Guarded. Options via env."""
import json, os, sys
sys.path.insert(0, os.getcwd())
import numpy as np, mau5engine as E, mau5preview as PV, mau5power
from PIL import Image, ImageDraw
out=sys.argv[1]
h=E.Helmet(); sc=PV.Scene(h)
ims=[]
Y_LO=float(os.environ.get("Y_LO",-119)); Y_HI=float(os.environ.get("Y_HI",170)); XH=float(os.environ.get("XH",171))
SY=float(os.environ.get("SUNY",95)); SR=float(os.environ.get("SUNR",260)); SS=float(os.environ.get("SUNS",120))
for spec in sys.argv[2:]:
    p=spec.split(":")
    nm=p[0]; mode=p[1] if len(p)>1 else "p"; dy=float(p[2]) if len(p)>2 else 0.0
    sp=np.asarray(E.make("sprite",sprite=nm,color=(255,255,255),y_lo=Y_LO,y_hi=Y_HI,x_half=XH,dy=dy).render(h,0.0,None),float)
    mask=sp.max(1)>0
    f=np.zeros((h.n,3))
    if mode=="p":
        f[mask]=(60,36,4)
    else:
        d=np.hypot(h.px-0,h.py-SY)
        e=np.clip((SR-d)/SS,0,1); k=e*e*(3-2*e)
        f[h.shell]=np.outer(k[h.shell],(70,42,4))
        f[mask]=(6,3,0)
    g=mau5power.load(count=h.n)
    s,rep=g.apply(f,now=0.0,gain=1.0)
    im=sc.frame(np.asarray(s,float)).crop((180,230,580,560)).resize((400,330))
    ImageDraw.Draw(im).text((6,4),"%s %s dy%g %.0fmA"%(nm,mode,dy,rep["sent_ma"]),fill=(255,255,255))
    ims.append(im)
n=len(ims); cols=min(n,4); rows=(n+cols-1)//cols
o=Image.new("RGB",(400*cols,330*rows))
for i,im in enumerate(ims):
    o.paste(im,((i%cols)*400,(i//cols)*330))
o.save(out);print(out,o.size)
