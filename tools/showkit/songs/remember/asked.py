# per scene: mA asked before the guard, split shell / tubes / rims, and what the guard sent
import json, os, sys
sys.path.insert(0, os.getcwd())
import numpy as np, mau5engine as E, mau5scene as M, mau5power, mau5show
base=sys.argv[1]
show=json.load(open("shows/%s.json"%base))
music=mau5show._music_for(show,"shows/%s.mp3"%base)
h=E.Helmet(); sc=M.Scenes(show["scenes"],h); g=mau5power.load(count=h.n)
fps=20.0
print("MA_PER_LED_FULL_WHITE",mau5power.MA_PER_LED_FULL_WHITE)
per={};order=[]
k=mau5power.MA_PER_LED_FULL_WHITE/(3*255.0)
for i in range(int(float(show["duration"])*fps)):
    t=i/fps
    out,gain,label=sc.frame(t,music)
    name=label.split(" · ")[0] or "-"
    a=np.asarray(out)
    sent,rep=g.apply(out,now=t,gain=gain)
    d=per.setdefault(name,[])
    if not d: order.append(name)
    s=np.asarray(sent,float)
    d.append((a[h.shell].sum()*k,a[h.tubes].sum()*k,a[h.rims].sum()*k,rep["sent_ma"],s[h.shell].sum()*k,s[h.tubes].sum()*k))
print("scene            asked: shell tubes rims | sent total  shell tubes | shell kept")
for n in order:
    v=np.mean(per[n],0)
    print("%-14s %8.0f %6.0f %5.0f | %6.0f %6.0f %6.0f | %4.0f%%"%(n,v[0],v[1],v[2],v[3],v[4],v[5],100*v[4]/max(v[0],1)))
