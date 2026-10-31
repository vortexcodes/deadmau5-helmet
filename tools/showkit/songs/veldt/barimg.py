import sys, numpy as np
from PIL import Image, ImageDraw
# One row per bar, 96 columns per bar, one panel per band: bar lines and sections read as rows turning.
z=np.load(sys.argv[1]); out=sys.argv[2]; spb=float(sys.argv[3]); anchor=float(sys.argv[4])
tt=z["tt"]
bands=["sub","low","mid","pres","air"]
bar=4*spb
t0=anchor%bar
nb=int((tt[-1]-t0)/bar)+1
W=96; S=4; 
panels=[]
for k in bands:
    e=np.log1p(z[k]*0.2); 
    e=e/np.percentile(e,99.5)
    img=np.zeros((nb,W))
    for b in range(nb):
        ts=t0+(b+np.arange(W)/W)*bar
        i=np.clip(np.searchsorted(tt,ts),0,len(tt)-1)
        img[b]=e[i]
    a=np.clip(img,0,1)**1.5
    im=Image.fromarray((a*255).astype(np.uint8)).resize((W*3,nb*S),Image.NEAREST).convert("RGB")
    d=ImageDraw.Draw(im)
    for q in range(1,4):
        d.line([(q*W*3/4,0),(q*W*3/4,nb*S)],fill=(0,160,255))
    for b in range(0,nb,8):
        d.line([(0,b*S),(W*3,b*S)],fill=(255,80,0))
    panels.append(im)
o=Image.new("RGB",(sum(p.width for p in panels)+10*len(panels)+40,nb*S+20),(30,30,30))
d=ImageDraw.Draw(o)
x=40
for k,p in zip(bands,panels):
    o.paste(p,(x,20)); d.text((x+4,4),k,fill=(255,255,255)); x+=p.width+10
for b in range(0,nb,8):
    d.text((4,20+b*S-5),str(b),fill=(255,255,255))
o.save(out); print(out,o.size,"t0",t0)
