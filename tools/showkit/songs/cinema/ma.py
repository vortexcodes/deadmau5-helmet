import sys, os, json
sys.path.insert(0, os.getcwd())
import numpy as np, mau5show, mau5scene, mau5power, mau5engine as E
base="deadmau5 - Strobe (Special Features Remix)"
show=json.load(open("shows/%s.json"%base))
music=mau5show._music_for(show,"shows/%s.mp3"%base)
h=E.Helmet()
sc=mau5scene.Scenes(show["scenes"],h)
g=mau5power.load(count=h.n)
g2=mau5power.load(count=h.n)
spb=show["scenes"]["grid"]["spb"]; t0=show["scenes"]["grid"]["t0"]
fps=25
dur=float(show.get("duration",0))
per={}
order=[]
for i in range(int(dur*fps)):
    t=i/fps
    out,gain,lab=sc.frame(t,music)
    nm=lab.split(" · ")[0] or "-"
    o=out.astype(np.float64)
    a=o.copy();a[~h.shell]=0
    c=o.copy();c[h.shell]=0
    rs=g.frame_ma(a);re=g.frame_ma(c)
    f,rep=g2.apply(out.copy(),now=t,gain=gain)
    f=np.asarray(f,float)
    a=f.copy();a[~h.shell]=0
    c=f.copy();c[h.shell]=0
    d=per.setdefault(nm,{"rs":[],"re":[],"sent":[],"sa":[],"ea":[],"p97":[],"med":[],"over":0,"n":0,"from":t})
    if nm not in order: order.append(nm)
    d["rs"].append(rs);d["re"].append(re);d["sent"].append(rep["sent_ma"]);d["sa"].append(g.frame_ma(a));d["ea"].append(g.frame_ma(c))
    v=f[h.shell].max(1)
    d["p97"].append(np.percentile(v,97));d["med"].append(np.percentile(v,50))
    d["over"]+=rep["sent_ma"]>=985;d["n"]+=1
    d["heat"]=(rep.get("thermal") or {}).get("full_pct",0)
print("scene        | raw shell  ears | sent  max over%% | shell mA  min | ears mA  max | shell LED p97 median | heat")
for nm in order:
    d=per[nm]
    print("%-12s | %6.0f %6.0f | %5.0f %5.0f %3.0f%% | %5.0f %5.0f | %5.0f %5.0f | %4.0f %4.0f | %4.1f"%(nm[:12],np.mean(d["rs"]),np.max(d["re"]),np.mean(d["sent"]),np.max(d["sent"]),100*d["over"]/d["n"],np.mean(d["sa"]),np.min(d["sa"]),np.mean(d["ea"]),np.max(d["ea"]),np.mean(d["p97"]),np.mean(d["med"]),d.get("heat",0)))
