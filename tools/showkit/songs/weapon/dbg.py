import sys,os,json
sys.path.insert(0,os.getcwd())
import numpy as np, mau5show, mau5scene as MS, mau5engine as E
base="deadmau5 - Raise Your Weapon"
show=json.load(open("shows/%s.json"%base))
music=mau5show._music_for(show,"shows/%s.mp3"%base)
g=show["scenes"]["grid"]; spb=g["spb"]; t0=g["t0"]
def tof(bar):
    B=4*bar
    return t0+B*spb+sum(b*spb for at,b in g.get("holds",[]) if B>at)
h=E.Helmet()
sc=MS.Scenes(show["scenes"],h)
for bar in (98.0,98.5,104.0):
    out,gain,label=sc.frame(tof(bar),music)
    s=h.shell
    print("bar",bar,label,"gain",round(gain,3))
    rows=sorted(set(np.round(h.py[s&(out.max(1)>0)],-1)))
    for y in rows:
        m=s&(np.abs(h.py-y)<5)&(out.max(1)>0)
        print("   y~%4d n=%3d x %.0f..%.0f  max %s"%(y,m.sum(),h.px[m].min(),h.px[m].max(),np.round(out[m].max(0))))
    m=(np.abs(h.py-62)<6)&s
    idx=np.where(m)[0]; idx=idx[np.argsort(h.px[idx])]
    print("   strip:",[int(out[i].max()) for i in idx][:40])
print(sc.beat(tof(98)),)
sn=[x for x in show["scenes"]["scenes"] if x["name"]=="the draw"][0]
print(json.dumps(sn["layers"][0]["params"]))
for L in sn["layers"]:
    print(L["fx"],L["on"],L.get("gain"),L.get("from"),L.get("to"),L.get("width"),L.get("shape"),L.get("mode"))
