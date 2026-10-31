#!/usr/bin/env python3
"""Per scene: how much of the time the governor takes light from the shell, and how bright the shell really is."""
import json, os, sys, time
sys.path.insert(0, os.getcwd())
import numpy as np, mau5show, mau5power, mau5scene as S, mau5engine as E
base = "deadmau5 - Some Chords"
show = json.load(open(os.path.join("shows", base + ".json")))
music = mau5show._music_for(show, os.path.join("shows", base + ".mp3"))
h = E.Helmet(); sc = S.Scenes(show["scenes"], h); guard = mau5power.load(count=h.n)
fps = 25.0; dur = float(show["duration"]); n = int(dur * fps)
per = {}; order = []; shell = np.asarray(h.shell, bool); ears = np.asarray(h.ears, bool)
for i in range(n):
    t = i / fps
    out, gain, label = sc.frame(t, music)
    gf, rep = guard.apply(out, now=t, gain=gain)
    gf = np.asarray(gf, float)
    nm = label or "(out)"
    if nm not in per:
        per[nm] = dict(t=t, ma=[], gov=[], smean=[], smax=[], emean=[], heat=0.0, asked=[])
        order.append(nm)
    d = per[nm]
    d["ma"].append(rep["sent_ma"]); d["gov"].append(rep["governor_hit"]); d["asked"].append(rep["after_region_ma"])
    d["smean"].append(gf[shell].mean()); d["smax"].append(gf[shell].max()); d["emean"].append(gf[ears].mean())
    d["heat"] = max(d["heat"], rep["thermal"]["full_pct"])
print("%-26s %7s %6s %6s %7s %6s %6s %6s %6s" % ("label", "from", "n", "mA", "p95", "gov%", "shell", "smax", "ears"))
for nm in order:
    d = per[nm]
    if len(d["ma"]) < 1: continue
    print("%-26s %7.1f %6d %6.0f %7.0f %6.0f %6.1f %6.0f %6.1f   heat %.1f" % (nm[:26], d["t"], len(d["ma"]), np.mean(d["ma"]), np.percentile(d["asked"], 95), 100 * np.mean(d["gov"]), np.mean(d["smean"]), np.mean(d["smax"]), np.mean(d["emean"]), d["heat"]))
