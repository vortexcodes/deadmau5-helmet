#!/usr/bin/env python3
# rhythm.py lo hi [band ...] : per bar, 16 steps, onset or level per band, so stabs can be read off.
import sys, numpy as np, os, re
KIT = "tools/showkit"
WORK = KIT + "/work"
p = WORK + "/" + re.sub(r"\W+", "_", "deadmau5 & Wolfgang Gartner - Animal Rights.mp3") + ".env.npz"
z = np.load(p)
tt = z["tt"]
spb = 0.46875
lo, hi = int(sys.argv[1]), int(sys.argv[2])
mode = sys.argv[3] if len(sys.argv) > 3 else "od"
bands = sys.argv[4:] or ["bass", "lowmid", "mid", "pres", "air"]
CH = " .:-=+*#%@"
for b in range(lo, hi):
    row = []
    for nm in bands:
        key = nm + "_od" if mode == "od" else nm
        e = z[key]
        out = []
        for k in range(16):
            t = (b + k / 16) * 4 * spb
            i0 = np.searchsorted(tt, t - 0.012)
            i1 = np.searchsorted(tt, t + spb / 4 - 0.012)
            if mode == "od":
                out.append(e[i0:i0 + 5].max() if i0 < len(e) else 0)
            else:
                out.append(e[i0:i1].mean() if i0 < len(e) else 0)
        row.append(np.array(out))
    s = []
    for r, nm in zip(row, bands):
        allv = z[nm + "_od"] if mode == "od" else z[nm]
        top = np.percentile(allv, 99.5)
        bot = 0 if mode == "od" else np.percentile(allv, 20)
        v = np.clip((r - bot) / max(top - bot, 1e-6), 0, 1)
        ss = "".join(CH[min(9, int(a * 9.99))] for a in v)
        s.append(ss[:4] + "|" + ss[4:8] + "|" + ss[8:12] + "|" + ss[12:16])
    print("%4d %s" % (b, "   ".join(s)))
print("     " + "   ".join("%-19s" % n for n in bands))
