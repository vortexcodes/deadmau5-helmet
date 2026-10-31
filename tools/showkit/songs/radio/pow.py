#!/usr/bin/env python3
"""pow.py "<base>": per scene through a fresh guard: mA, how often the governor sheds the shell, shell level kept."""
import json, os, sys
sys.path.insert(0, os.getcwd())
import numpy as np, mau5show, mau5scene as SS, mau5engine as E, mau5power
base=sys.argv[1]
show=json.load(open("shows/%s.json"%base))
music=mau5show._music_for(show,"shows/%s.mp3"%base)
h=E.Helmet(); sc=SS.Scenes(show["scenes"],h); guard=mau5power.load(count=h.n)
dur=float(show["duration"]); fps=25.0
per={};order=[]
sh=np.asarray(h.shell,bool); ea=np.asarray(h.ears,bool)
for i in range(int(dur*fps)):
    t=i/fps
    out,gain,label=sc.frame(t,music)
    res,rep=guard.apply(out,now=t,gain=gain)
    res=np.asarray(res,float)
    nm=label.split(" · ")[0] or "(out)"
    if nm not in per: per[nm]=[];order.append(nm)
    asked_shell=out[sh].mean()
    # the shell's share of what it asked after the knee: from the mean
    per[nm].append((rep["sent_ma"],rep["governor_hit"],"shell" in rep["regions_hit"],res[sh].mean(),res[ea].mean(),rep["thermal"]["full_pct"] if rep.get("thermal") else 0,res[sh].max()))
print("%-14s %6s %6s %6s %6s %7s %7s %6s %6s"%("scene","mean","p95","gov%","reg%","shellm","earsm","smax","heat"))
for nm in order:
    a=np.array(per[nm],float)
    print("%-14s %6.0f %6.0f %6.0f %6.0f %7.1f %7.1f %6.0f %5.1f%%"%(nm[:14],a[:,0].mean(),np.percentile(a[:,0],95),a[:,1].mean()*100,a[:,2].mean()*100,a[:,3].mean(),a[:,4].mean(),np.percentile(a[:,6],90),a[:,5].max()))
