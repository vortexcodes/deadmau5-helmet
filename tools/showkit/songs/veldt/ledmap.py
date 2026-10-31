import sys,os
sys.path.insert(0,os.getcwd())
import numpy as np, mau5engine as E, mau5preview as PV
from PIL import Image, ImageDraw
h=E.Helmet(); sc=PV.Scene(h)
# parts in colours
f=np.zeros((h.n,3))
f[h.shell]=(60,60,60)
f[np.asarray(h.tube)==0]=(255,40,0)
f[np.asarray(h.tube)==1]=(40,255,0)
f[np.asarray(h.tube)==2]=(0,80,255)
f[np.asarray(h.rims,bool)]=(255,255,0)
a=sc.frame(f)
# along-axis gradient on tubes, y on shell
g=np.zeros((h.n,3))
al=np.maximum(h.along,0)
g[h.tubes]=np.outer(al[h.tubes],(255,255,255))
g[h.shell]=np.outer(h.nel[h.shell],(255,200,0))
b=sc.frame(g)
# region jaw vs face, x axis
k=np.zeros((h.n,3))
k[h.shell&(h.py<=28)]=(255,0,0)
k[h.shell&(h.py>28)]=(0,0,255)
c=sc.frame(k)
# region 'a' axis on rims and shell, r axis
m=np.zeros((h.n,3))
m[h.rims]=np.outer(h.ea[h.rims],(255,255,255))
m[h.shell]=np.outer(h.er[h.shell],(255,255,255))
d=sc.frame(m)
o=Image.new("RGB",(a.width*2,a.height*2))
o.paste(a,(0,0));o.paste(b,(a.width,0));o.paste(c,(0,a.height));o.paste(d,(a.width,a.height))
o.save(sys.argv[1])
print(a.size)
print("shell nel by py:",[ (round(float(h.py[h.shell][i])),round(float(h.nel[h.shell][i]),2)) for i in np.argsort(h.py[h.shell])[::50]])
print("tube along vs py ear2 tube0",[(round(float(h.along[i]),2),round(float(h.px[i])),round(float(h.py[i]))) for i in np.where((np.asarray(h.tube)==0)&h.ear2)[0][::6]])
print("tube along vs py ear2 tube1",[(round(float(h.along[i]),2),round(float(h.px[i])),round(float(h.py[i]))) for i in np.where((np.asarray(h.tube)==1)&h.ear2)[0][::6]])
print("tube along vs py ear2 tube2",[(round(float(h.along[i]),2),round(float(h.px[i])),round(float(h.py[i]))) for i in np.where((np.asarray(h.tube)==2)&h.ear2)[0][::6]])
print("rim ear2",[(round(float(h.px[i])),round(float(h.py[i]))) for i in np.where(np.asarray(h.rims,bool)&h.ear2)[0][::3]])
