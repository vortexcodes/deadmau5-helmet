#!/usr/bin/env python3
"""The window: a fan of seven panes on the dome, two lancets on the jaw.  Writes the sprites.
A sprite here is a mask of real LEDs, so nothing lands in the blank middle of the face."""
import json, math, os, sys
sys.path.insert(0, os.getcwd())
import numpy as np, mau5engine as E
BASE = "deadmau5 - Some Chords"
h = E.Helmet()
s = np.asarray(h.shell, bool)
X, Y = h.px[s], h.py[s]
COLS, ROWS = 40, 24
Y_LO, Y_HI, X_HALF = -116.0, 172.0, 174.0
HUB = (0.0, 30.0)
NW = 7          # panes in the fan
LEAD = 6.5      # half width of a lead line, mm

def pane_of(x, y):
    """-1 lead, 0..6 the fan (right to left), 10 the jaw."""
    if y > 28:
        r = math.hypot(x - HUB[0], y - HUB[1])
        th = max(0.0, min(180.0, math.degrees(math.atan2(y - HUB[1], x - HUB[0]))))
        k = th / (180.0 / NW)
        i = min(NW - 1, int(k))
        d = min(k - i, i + 1 - k) * math.radians(180.0 / NW) * r
        if d < LEAD and 0 < round(k) < NW:
            return -1
        return i
    for cut in (-20.0, -75.0):
        if abs(y - cut) < 7.0:
            return -1
    return 10

PANE = np.array([pane_of(a, b) for a, b in zip(X, Y)])
print({int(k): int((PANE == k).sum()) for k in np.unique(PANE)})
ry = np.floor((Y_HI - Y) / (Y_HI - Y_LO) * ROWS).astype(int)
rx = np.floor((X + X_HALF) / (2 * X_HALF) * COLS).astype(int)

def rows_for(test):
    grid = [["."] * COLS for _ in range(ROWS)]
    for r, c, p in zip(ry, rx, PANE):
        if test(int(p)):
            grid[r][c] = "#"
    return ["".join(g) for g in grid]

sp = {"chords_lead": rows_for(lambda p: p == -1)}
order = [{3}, {2, 4}, {1, 5}, {0, 6}]
shown = set()
for k, grp in enumerate(order):
    shown |= grp
    keep = set(shown)
    sp["chords_m%d" % (k + 1)] = rows_for(lambda p: p == -1 or (0 <= p <= 6 and p not in keep))
sp["chords_ruby1"] = rows_for(lambda p: p == 3)
sp["chords_ruby2"] = rows_for(lambda p: p in (0, 3, 6))
sp["chords_gold"] = rows_for(lambda p: p in (1, 5))
sp["chords_blue"] = rows_for(lambda p: p in (2, 4))
sp["chords_p06"] = rows_for(lambda p: p in (0, 6))
out = os.path.join("shows", "scenes", BASE + ".sprites.json")
with open(out, "w") as f:
    f.write("{\n" + ",\n".join("%s: %s" % (json.dumps(k), json.dumps(v)) for k, v in sp.items()) + "\n}\n")
print(out, os.path.getsize(out), "bytes", len(sp), "sprites")
# how often two kinds of pane fall in one cell (those LEDs go with the lead or the mask)
cells = {}
for r, c, p in zip(ry, rx, PANE):
    cells.setdefault((r, c), set()).add(int(p))
print("mixed cells", sum(1 for v in cells.values() if len(v) > 1), "of", len(cells))
