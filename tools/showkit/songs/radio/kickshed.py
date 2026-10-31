import json, os, sys
sys.path.insert(0, os.getcwd())
import numpy as np, mau5show, mau5scene as SS, mau5engine as E, mau5power
base=sys.argv[1]
show=json.load(open("shows/%s.json"%base))
music=mau5show._music_for(show,"shows/%s.mp3"%base)
h=E.Helmet(); sc=SS.Scenes(show["scenes"],h); guard=mau5power.load(count=h.n)
dur=float(show["duration"]); fps=30.0
rows=[]
sh=np.asarray(h.shell,bool)
for i in range(int(dur*fps)):
    t=i/fps
    out,gain,label=sc.frame(t,music)
    res,rep=guard.apply(out,now=t,gain=gain)
    if rep["governor_hit"]:
        asked=out[sh].sum(); got=np.asarray(res,float)[sh].sum()
        rows.append((t,(t-0.124)/1.875,rep["asked_ma"],rep["sent_ma"],got/(max(asked,1)),label))
print(len(rows),"governed frames of",int(dur*fps))
# group into runs
runs=[];
for r in rows:
    if runs and r[0]-runs[-1][-1][0]<0.1: runs[-1].append(r)
    else: runs.append([r])
print(len(runs),"runs; longest and deepest:")
runs.sort(key=lambda u:(-len(u)))
for u in runs[:14]:
    print("  bar %.2f..%.2f (%d frames) asked %.0f mA, %s"%(u[0][1],u[-1][1],len(u),max(x[2] for x in u),u[0][5]))
