import sys,os
KIT=os.environ["KIT"];sys.path.insert(0,KIT+"/work/radio")
from lab import *
h,sc,music=env()
s=np.asarray(h.shell,bool)
i=np.where(s)[0]
j=i[np.argsort(h.er[i])[:6]]
print("shell lowest er:",[(round(float(h.px[q])),round(float(h.py[q])),round(float(h.er[q]),3),round(float(h.ea[q]),3)) for q in j])
# angle per quadrant
for (x,y) in [(0,157),(150,50),(-150,50),(100,120),(-100,120),(160,-20),(-160,-20),(0,-105),(100,-100),(-100,-100),(0,40)]:
    q=i[np.argmin(np.hypot(h.px[i]-x,h.py[i]-y))]
    print("near (%d,%d): led (%.0f,%.0f) er %.2f ea %.2f nel %.2f nfa %.2f"%(x,y,h.px[q],h.py[q],h.er[q],h.ea[q],h.nel[q],h.nfa[q]))
e1=np.asarray(h.tubes,bool)&np.asarray(h.ear1,bool)
for t in range(3):
    m=e1&(np.asarray(h.tube)==t)
    ii=np.where(m)[0]
    a=h.along[ii]
    print("tube",t,"along %.2f at (%.0f,%.0f); along %.2f at (%.0f,%.0f)"%(a.min(),h.px[ii[a.argmin()]],h.py[ii[a.argmin()]],a.max(),h.px[ii[a.argmax()]],h.py[ii[a.argmax()]]))
amber={"stops":[[0,0,0],[60,22,0],[255,140,20],[255,200,90]]}
P={"amber":[[0,0,0],[70,26,0],[255,140,20],[255,210,120]],
   "tick":[[0,0,0],[0,0,0],[255,150,30]],
   "wave":[[0,0,0],[0,0,0],[0,0,0],[0,40,40],[0,255,210]],
   "wave2":[[0,0,0],[0,0,0],[0,0,0],[60,0,40],[255,0,170]],
   "ringz":{"stops":[[0,0,0],[0,255,210],[0,0,0],[0,0,0]],"wrap":True},
   "vu":[[0,200,170],[0,230,140],[255,170,30],[255,30,90]],
   "static":[[120,120,140],[220,220,240],[255,180,90]]}
T=[]
T.append(("a axis gray",1,0,8,[{"fx":"grad","on":"shell","axis":"a","axis2":"x","scale":1,"pal":"amber","gain":0.8,"wave":"saw"}]))
T.append(("r axis gray",1,0,8,[{"fx":"grad","on":"shell","axis":"r","axis2":"x","scale":1,"pal":"amber","gain":0.8,"wave":"saw"}]))
T.append(("x axis",1,0,8,[{"fx":"grad","on":"all","axis":"x","axis2":"x","scale":1,"pal":"amber","gain":0.8,"wave":"saw"}]))
T.append(("y axis",1,0,8,[{"fx":"grad","on":"all","axis":"y","axis2":"x","scale":1,"pal":"amber","gain":0.8,"wave":"saw"}]))
T.append(("al axis",1,0,8,[{"fx":"grad","on":"tubes","axis":"al","axis2":"x","scale":1,"pal":"amber","gain":0.8,"wave":"saw"}]))
T.append(("a on ears",1,0,8,[{"fx":"grad","on":"ears","axis":"a","axis2":"x","scale":1,"pal":"amber","gain":0.8,"wave":"saw"}]))
# dial: backlight + ticks on x, needle
T.append(("dial ticks x12",1,0,8,[{"fx":"fill","on":"face","pal":"amber","c":0.33,"gain":0.5},{"fx":"grad","on":"face","axis":"x","axis2":"y","scale":12,"pal":"tick","gain":0.5},{"fx":"sweep","on":"face","axis":"x","shape":"p","mode":"band","width":0.03,"from":0.4,"to":0.6,"pal":"amber","c":1,"gain":1}]))
T.append(("dial ticks x8",1,0,8,[{"fx":"fill","on":"face","pal":"amber","c":0.33,"gain":0.5},{"fx":"grad","on":"face","axis":"x","axis2":"y","scale":8,"pal":"tick","gain":0.5},{"fx":"sweep","on":"face","axis":"x","shape":"p","mode":"band","width":0.03,"from":0.4,"to":0.6,"pal":"amber","c":1,"gain":1}]))
T.append(("needle a",1,0,8,[{"fx":"fill","on":"face","pal":"amber","c":0.33,"gain":0.5},{"fx":"sweep","on":"face","axis":"a","shape":"p","mode":"band","width":0.02,"from":0.1,"to":0.2,"pal":"amber","c":1,"gain":1}]))
# wave
T.append(("wave y2 w.08",1,0,8,[{"fx":"grad","on":"face","axis":"y","axis2":"x","scale":2,"ofs":0.0,"warp":0.2,"wscale":2,"wspeed":0.25,"pal":"wave","gain":0.8}]))
T.append(("wave y1.5",1,0,8,[{"fx":"grad","on":"face","axis":"y","axis2":"x","scale":3,"ofs":0.25,"warp":0.3,"wscale":3,"wspeed":0.25,"pal":"wave","gain":0.8}]))
T.append(("wave two",1,0,8,[{"fx":"grad","on":"face","axis":"y","axis2":"x","scale":2,"ofs":0.0,"warp":0.25,"wscale":2,"wspeed":0.25,"pal":"wave","gain":0.8},{"fx":"grad","on":"face","axis":"y","axis2":"x","scale":2,"ofs":0.0,"warp":-0.25,"wscale":2,"wspeed":0.25,"pal":"wave2","gain":0.8}]))
# rings
for cg,rad in ((3,420),(4,420),(6,420)):
    T.append(("rings cg%d"%cg,1.25,0,8,[{"fx":"orb","on":"all","x":0,"y":170,"rad":rad,"soft":200,"pal":"ringz","c":0.0,"cgrad":cg,"gain":0.9}]))
T.append(("static",1,0,8,[{"fx":"twinkle","on":"shell","rate":6,"sharp":6,"dens":0.8,"pal":"static","c":0,"spread":0.5,"gain":0.5}]))
T.append(("static ears",1,0,8,[{"fx":"twinkle","on":"all","rate":6,"sharp":6,"dens":0.8,"pal":"static","c":0,"spread":0.5,"gain":0.3}]))
T.append(("vu",29.06,0,112,[{"fx":"sweep","on":"tubes","axis":"al","shape":"p","mode":"fill","soft":0.1,"from":{"band":"bass","lo":0,"hi":1},"to":{"band":"bass","lo":0,"hi":1},"pal":"vu","c":0,"cgrad":1,"gain":0.8}]))
sheet(T,P,KIT+"/work/radio/t1.png")
