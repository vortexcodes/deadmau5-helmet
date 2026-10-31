#!/usr/bin/env python3
"""parity.py "<base>": this show on the laptop's renderer against the phone's, under node, with no helmet and no browser."""
import json, math, os, subprocess, sys
sys.path.insert(0, os.getcwd())
import numpy as np, mau5offline, mau5show, mau5engine as E
base = sys.argv[1]
data = mau5offline.bundle()
show = data["shows"][base]
spec = show["scenes"]
g = spec["grid"]; t0, spb = g["t0"], g["spb"]; holds = g.get("holds") or []
def at(bar):
    return t0 + 4.0 * bar * spb + sum(b * spb for beat, b in holds if 4.0 * bar > beat)
ts = []
for beat, beats in holds:
    a = at(beat / 4.0)
    ts += [a - 0.001, a + 0.001, a + beats * spb / 2.0, a + beats * spb - 0.001, a + beats * spb + 0.001]
for s in spec["scenes"]:
    a, b = at(s["from"]), at(s["to"])
    ts += [a + 0.001, (a + b) / 2.0, b - 0.001]
    if s["out"] > 0:
        ts.append(b - s["out"] * spb / 2.0)
for x in spec["hits"]:
    a = at(x["at"])
    ts += [a + 0.001, a + 0.05, a + x["beats"] * spb / 2.0]
ts += list(np.linspace(0.0, show["duration"], 300))
ts = sorted({round(float(t), 6) for t in ts if t >= 0})
class Drive:
    analysed = True
    bpm = 128.0
    lock_conf = float("nan")
    def band_at(self, t, name, punch=False):
        w = {"bass": 1.1, "mid": 1.9}.get(name, 2.7)
        return 0.5 + 0.4 * math.sin(t * w + (0.3 if punch else 0.0))
    def __getattr__(self, k):
        raise AttributeError(k)
h = E.Helmet()
worst = {}
for analysed in (True,):
    job = {"data": data, "shows": [base], "times": ts, "analysed": analysed}
    p = subprocess.run(["node", "remote/offline/showtest.js"], input=json.dumps(job), capture_output=True, text=True, timeout=300)
    if p.returncode:
        print(p.stderr[-2000:]); raise SystemExit(1)
    res = json.loads(p.stdout)[base]
    print("phone playing scenes:", res["scenes"], "| frames", len(ts), "| mean %.3f ms, worst %.3f ms a frame under node" % (np.mean(res["ms"]), np.max(res["ms"])))
    import mau5scene as SS
    sc = SS.Scenes(show["scenes"], h)
    w, where = 0.0, ""
    for k, t in enumerate(ts):
        out, gain, label = sc.frame(t, Drive())
        a = np.asarray(out, float)
        b = np.asarray(res["frames"][k], float).reshape(-1, 3)
        d = max(float(np.abs(a - b).max()), abs(gain - res["gains"][k]) * 255.0)
        if d > w:
            w, where = d, "t=%.3f %s (phone says %s)" % (t, label, res["labels"][k])
    print("worst difference %.5f counts at %s" % (w, where))
