#!/usr/bin/env python3
# Through the real guard, per scene: what the shell and ears take, how often the governor binds and what it leaves of the shell.
import sys, os
sys.path.insert(0, os.getcwd())
import numpy as np, mau5engine as E, mau5power, mau5scene as M
B = os.environ.get("BASE", "deadmau5 & Wolfgang Gartner - Animal Rights")
show, music, _ = M._show_and_music(B)
h = E.Helmet()
sc = M.Scenes(show["scenes"], h)
guard = mau5power.load(count=h.n)
dur = float(show["duration"]); fps = 20.0
per = {}; order = []
for i in range(int(dur * fps)):
    t = i / fps
    out, gain, label = sc.frame(t, music)
    f, rep = guard.apply(out, now=t, gain=gain)
    name = label.split(" · ")[0] or "(outside)"
    if name not in per:
        per[name] = []; order.append(name)
    F = np.asarray(f, float)
    A = np.asarray(out, float)
    per[name].append((rep["sent_ma"], F[h.shell].sum() / 765 * 19, F[h.ears].sum() / 765 * 19, rep["governor_hit"], F[h.shell].max(), np.percentile(F[h.shell].max(1), 95),
                      (rep.get("thermal") or {}).get("full_pct", 0.0), A[h.ears].sum() / 765 * 19))
print("%-16s %6s %7s %7s %8s %6s %6s %6s" % ("scene", "mA", "shellmA", "earsmA", "askedear", "gov%", "shmax", "heat"))
tot = []
for nm in order:
    a = np.array(per[nm], float)
    print("%-16s %6.0f %7.0f %7.0f %8.0f %5.0f%% %6.0f %5.1f%%" % (nm[:16], a[:, 0].mean(), a[:, 1].mean(), a[:, 2].mean(), a[:, 7].mean(), 100 * a[:, 3].mean(), a[:, 4].mean(), a[:, 6].max()))
    tot.append(a)
a = np.vstack(tot)
print("whole song: mean %.0f mA, shell %.0f mA, ears %.0f mA, governed %.0f%% of frames, peak heat %.1f%%" % (a[:, 0].mean(), a[:, 1].mean(), a[:, 2].mean(), 100 * a[:, 3].mean(), a[:, 6].max()))
