# The phone's twin of the renderer against the laptop's, on this show only, under node. No browser, no network.
import base64, json, math, os, subprocess, sys
sys.path.insert(0,os.getcwd())
import numpy as np, mau5engine as E, mau5show
from mau5fx import FONT5x7, SPRITES
BASE="deadmau5 - Raise Your Weapon"
show=json.load(open("shows/%s.json"%BASE))
h=E.Helmet()
b64=lambda v,f: base64.b64encode(np.asarray(v).astype(f).tobytes()).decode()
runs=[]
for i,r in enumerate(h.region):
    if runs and runs[-1][2]==r: runs[-1][1]=i
    else: runs.append([i,i,str(r)])
data={"n":int(h.n),
 "f32":{k:b64(v,"<f4") for k,v in {"px":h.px,"py":h.py,"depth":h.depth,"nx":h.nx,"ny":h.ny,"nfa":h.nfa,"nel":h.nel,"u":h.u,"fa":h.fa,"ea":h.ea,"er":h.er,"along":h.along,"xyz":h.xyz.reshape(-1)}.items()},
 "i16":{"group":b64(h.group,"<i2"),"tube":b64(h.tube,"<i2")},"regions":runs,
 "fonts":{"font":{k:list(v) for k,v in FONT5x7.items()},"digit3x5":{k:list(v) for k,v in E.DIGIT3x5.items()},"sprites":{k:list(v) for k,v in SPRITES.items()}},
 "shows":{BASE:show},"presets":{}}
class Drive:
    bands=True; bpm=128.0; lock_conf=float("nan"); analysed=True
    def level_at(s,t): return 0.5+0.4*math.sin(t*1.7)
    def beat_phase(s,t): return (t*2.13)%1.0
    def beat_index(s,t): return t*2.13
    def is_downbeat(s,t): return ((t*0.53)%1)<0.05
    def pitch_at(s,t): return (t*0.11)%1
    def centroid_at(s,t): return 0.5+0.4*math.sin(t*0.63)
    def bands_at(s,t,n): return np.array([0.5+0.4*math.sin(t*0.9+k*0.6) for k in range(n)])
    def band_at(s,t,name,punch=False):
        w={"bass":1.1,"mid":1.9}.get(name,2.7)
        return 0.5+0.4*math.sin(t*w+(0.3 if punch else 0.0))
spec=show["scenes"]; g=spec["grid"]; spb=g["spb"]; t0=g["t0"]; holds=g.get("holds") or []
def at(bar): return t0+4.0*bar*spb+sum(b*spb for a,b in holds if 4.0*bar>a)
ts=[]
for a,b in holds[::7]+holds[-16:]:
    x=at(a/4.0); ts+=[x-0.001,x+0.001,x+b*spb/2,x+b*spb+0.001]
for s in spec["scenes"]:
    a,b=at(s["from"]),at(s["to"]); ts+=[a+0.001,(a+b)/2,b-0.001]
    if s["out"]>0: ts.append(b-s["out"]*spb/2)
for x in spec["hits"]:
    a=at(x["at"]); ts+=[a+0.001,a+0.05,a+x["beats"]*spb/2]
ts+=list(np.linspace(0,show["duration"],300))
times=sorted({round(float(t),6) for t in ts if t>=0})
print(len(times),"times")
job={"data":data,"shows":[BASE],"times":times,"analysed":True}
p=subprocess.run(["node","remote/offline/showtest.js"],input=json.dumps(job),capture_output=True,text=True,timeout=280)
if p.returncode: print(p.stderr[-2000:]); sys.exit(1)
res=json.loads(p.stdout)[BASE]
print("phone playing scenes:",res["scenes"],"mean %.2f ms a frame, worst %.2f"%(np.mean(res["ms"]),np.max(res["ms"])))
py=mau5show.Player(show,helmet=h,music=Drive())
print("laptop playing scenes:",py.scenes is not None)
worst=0;where="";bad=0
for k,t in enumerate(times):
    a=np.asarray(py.frame(t),float); b=np.asarray(res["frames"][k],float).reshape(-1,3)
    d=max(float(np.abs(a-b).max()),abs(py.gain-res["gains"][k])*255.0)
    if d>worst: worst,where=d,"t=%.3f %s"%(t,py.label)
    if res["labels"][k]!=py.label: bad+=1
print("worst %.4f counts at %s; %d of %d labels differ"%(worst,where,bad,len(times)))
