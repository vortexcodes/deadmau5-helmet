#!/usr/bin/env python3
"""power.py "<base>" -- the whole song from a cold helmet, through the real power guard, at 12 fps:
mean watts, where the heat ends up, and the hottest stretches. Run from the repo root.
A set of songs back to back stays fresh only if songs average about 11.5 W or less: the helmet can
shed 11 W for ever, and the 3000 J bucket covers only the excess. Above that, heat builds up song
after song, and once the bucket is full every hit in the rest of the set gets flattened."""
import json, os, sys
sys.path.insert(0, os.getcwd())
import numpy as np, mau5show, mau5power, mau5scene, mau5engine as E
base = sys.argv[1]
fps = 12.0
show = json.load(open(os.path.join("shows", base + ".json")))
music = mau5show._music_for(show, os.path.join("shows", base + ".mp3"))
spec = show.get("scenes")
if not spec:
    raise SystemExit("no scenes compiled yet")
h = E.Helmet()
sc = mau5scene.Scenes(spec, h)
guard = mau5power.load(count=h.n)
dur = float(show["duration"])
per = {}
order = []
watts = []
heat = 0.0
for i in range(int(dur * fps)):
    t = i / fps
    out, gain, label = sc.frame(t, music)
    _, rep = guard.apply(out, now=t, gain=gain)
    w = float(rep.get("watts", 0.0))
    watts.append(w)
    th = rep.get("thermal") or {}
    heat = th.get("full_pct", 0.0)
    nm = label.split(" · ")[0] or "(outside)"
    if nm not in per:
        per[nm] = []
        order.append(nm)
    per[nm].append(w)
print("%s: %.0f s, mean %.1f W (target 11.5 or less), heat at the end %.0f%%" % (base, dur, np.mean(watts), heat))
hot = sorted(order, key=lambda n: -np.mean(per[n]) * (len(per[n]) ** 0.5))[:8]
print("hottest scenes (name, mean W, seconds): " + "; ".join("%s %.1f %.0fs" % (n, np.mean(per[n]), len(per[n]) / fps) for n in hot))
