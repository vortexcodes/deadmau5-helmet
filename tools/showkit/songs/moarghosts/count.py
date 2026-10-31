#!/usr/bin/env python3
"""How many shell LEDs each sprite lights, and what that costs at a post-knee colour sum. Run from the repo root."""
import sys, os
sys.path.insert(0, os.getcwd())
import numpy as np, mau5engine as E
h = E.Helmet()
SMALL = dict(y_lo=48, y_hi=170, x_half=66)
ROW = dict(y_lo=48, y_hi=170, x_half=288.75)
GIANT = dict(y_lo=-108, y_hi=166, x_half=171)
BIG = dict(y_lo=48, y_hi=170, x_half=128)
def n(name, fr, **kw):
    f = np.asarray(E.make("sprite", sprite="moar_" + name, color=(255, 255, 255), **fr, **kw).render(h, 0.0, None), float)
    return int((f[:, 0] > 0).sum())
for nm, fr, kw in [("gR_a", SMALL, {}), ("gR_a", SMALL, {"dx": 80}), ("gR_a", SMALL, {"dx": -120}), ("row_a", ROW, {}), ("row_a", ROW, {"dx": 70}),
                   ("G_R_a", GIANT, {}), ("G_F_a", GIANT, {}), ("Gw_R", GIANT, {}), ("Gw_F", GIANT, {}), ("F_a", GIANT, {}), ("Fface_a", GIANT, {}),
                   ("maze", GIANT, {}), ("bpR_o", BIG, {}), ("pacR_o", SMALL, {}), ("die0", GIANT, {}), ("die4", GIANT, {}), ("rowface_a", ROW, {})]:
    print("%-10s %-22s %3d LEDs" % (nm, str(kw), n(nm, fr, **kw)))
print("jaw", int((h.shell & (h.py <= 28)).sum()), "face", int((h.shell & (h.py > 28)).sum()))
