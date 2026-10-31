#!/usr/bin/env python3
"""songmap.py "<base>" -- the song, bar by bar, to choreograph against. Run from the repo root.
Per bar: seconds, energy, bass, mid, high (0-9), the three strongest pitch classes of the bar
(a chord's fingerprint), and >> where the bar differs most from the one before."""
import json, os, sys
import numpy as np
sys.path.insert(0, os.getcwd())
NOTES = "C C# D D# E F F# G G# A A# B".split()
base = sys.argv[1]
z = np.load(os.path.join("shows", base + ".analysis.npz"), allow_pickle=True)
fps = float(z["fps"]); bars = z["bars"]; dur = float(z["duration"])
e = np.asarray(z["energy"], float)
b = {k: np.asarray(z["b_%s_e" % k], float) for k in ("bass", "mid", "high")}
for k in b:
    b[k] = b[k] / max(b[k].max(), 1e-9)
ch = np.asarray(z["chroma"], float) if "chroma" in z else None
edges = [int(t * fps) for t in bars] + [int(dur * fps)]
rows = []
for i in range(len(bars)):
    a, c = max(0, edges[i]), max(edges[i] + 1, edges[i + 1])
    rows.append([e[a:c].mean(), b["bass"][a:c].mean(), b["mid"][a:c].mean(), b["high"][a:c].mean()])
R = np.array(rows)
R2 = R / np.maximum(R.max(0), 1e-9)
diff = np.r_[0, np.abs(np.diff(R2, axis=0)).sum(1)]
cut = np.percentile(diff, 90)
print("%s: %d bars, %.2f s a bar, %.1f s" % (base, len(bars), float(np.median(np.diff(bars))), dur))
print(" bar     t   E  B  M  H  notes       change")
for i in range(len(bars)):
    n = ""
    if ch is not None and i < len(ch):
        top = np.argsort(-ch[i])[:3]
        n = " ".join(NOTES[j] for j in top)
    print("%4d %6.1f   %d  %d  %d  %d  %-11s %s" % (i, bars[i], *[min(9, int(v * 9.99)) for v in R2[i]], n, ">>" if diff[i] >= cut else ""))
