#!/usr/bin/env python3
"""Per scene: how much is the shell being robbed? asked vs. sent on shell and ears, share of frames the global governor bites, its deepest bite."""
import json, os, sys
sys.path.insert(0, os.getcwd())
import numpy as np, mau5show, mau5power, mau5scene, mau5engine as E
base=sys.argv[1]
show=json.load(open(os.path.join("shows",base+".json")))
music=mau5show._music_for(show,os.path.join("shows",base+".mp3"))
h=E.Helmet(); scn=mau5scene.Scenes(show["scenes"],h); guard=mau5power.load(count=h.n)
fps=30.0
per={};order=[]
for i in range(int(float(show["duration"])*fps)):
    t=i/fps
    out,gain,label=scn.frame(t,music)
    sent,rep=guard.apply(out,now=t,gain=1.0)   # gain 1: compare levels without the pump
    nm=label.split(" · ")[0] or "(outside)"
    if nm not in per:
        per[nm]={"sh":[],"ea":[],"gov":[],"s":[],"ma":[],"askS":[],"t":t}; order.append(nm)
    d=per[nm]; sent=np.asarray(sent,float)
    d["sh"].append(sent[h.shell].mean()); d["ea"].append(sent[h.ears].mean()); d["gov"].append(rep["governor_hit"]); d["s"].append(guard._gov_s); d["ma"].append(rep["sent_ma"])
    d["askS"].append(np.clip(out[h.shell],0,255).mean())
print("%-10s %6s  %6s %6s  %5s %6s %6s %6s %6s"%("scene","from","shell","ears","gov%","minS","meanS","mA","pk mA"))
for nm in order:
    d=per[nm]
    print("%-10s %6.1f  %6.1f %6.1f  %5.0f %6.2f %6.2f %6.0f %6.0f   asked shell %5.1f"%(nm[:10],d["t"],np.mean(d["sh"]),np.mean(d["ea"]),100*np.mean(d["gov"]),min(d["s"]),np.mean(d["s"]),np.mean(d["ma"]),max(d["ma"]),np.mean(d["askS"])))
