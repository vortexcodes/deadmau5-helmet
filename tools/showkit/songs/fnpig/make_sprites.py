#!/usr/bin/env python3
"""The pig, drawn LED by LED: every set cell holds a real LED, so nothing scatters and the phone does no search."""
import json, math, os, sys
sys.path.insert(0, os.getcwd())
import numpy as np, mau5engine as E
h = E.Helmet()
s = np.asarray(h.shell, bool)
PX, PY = np.asarray(h.px, float), np.asarray(h.py, float)
BASE = "deadmau5 - FN Pig"
DOME = dict(y_lo=52.0, y_hi=172.0, x_half=172.0, rows=15, cols=43)
FULL = dict(y_lo=-116.0, y_hi=172.0, x_half=172.0, rows=36, cols=43)

def to_rows(lit, F):
    rows, cols = F["rows"], F["cols"]
    ry = (F["y_hi"] - PY) / (F["y_hi"] - F["y_lo"]) * rows
    rx = (PX + F["x_half"]) / (2 * F["x_half"]) * cols
    yes = np.zeros((rows, cols), int); no = np.zeros((rows, cols), int)
    mask = s & (PY > min(0.0, F["y_lo"]))
    for i in np.where(mask)[0]:
        if 0 <= ry[i] < rows and 0 <= rx[i] < cols:
            r, c = int(ry[i]), int(rx[i])
            if lit[i]: yes[r, c] += 1
            else: no[r, c] += 1
    return ["".join("X" if yes[r, c] > no[r, c] else "." for c in range(cols)) for r in range(rows)]

def ell(cx, cy, a, b):
    return ((PX - cx) / a) ** 2 + ((PY - cy) / b) ** 2 <= 1.0

def nostrils(cx, cy, nx, rx, ry):
    out = np.zeros(len(PX), bool)
    for side in (-1, 1):
        out |= ((PX - (cx + side * nx)) / rx) ** 2 + ((PY - cy) / ry) ** 2 <= 1.0
    return out

ROWS = np.array([139.6, 129.1, 117.4, 104.6, 90.9, 76.3, 61.0])
def holes(widths, cx=0.0, nx=47.0, dy=0.0):
    """two nostrils, given as half widths in mm for each LED row from y 139 down to y 61"""
    out = np.zeros(len(PX), bool)
    for side in (-1, 1):
        for ry, w in zip(ROWS, widths):
            if w > 0:
                out |= (np.abs(PY - (ry + dy)) < 6.5) & (np.abs(PX - (cx + side * nx)) <= w)
    return out

SH = {}
# THE SNOUT: a round plate on the dome. flare 0 (kick, wide open) .. 3 (nearly shut)
CY, A, B, NX, NY = 108.0, 128.0, 56.0, 47.0, 106.0
# half widths per row, y 139 129 117 105 91 76 61: round, with the widest row a little above the middle
FL = [(0, 14, 25, 30, 27, 15, 0), (0, 0, 19, 25, 22, 8, 0), (0, 0, 10, 19, 17, 0, 0), (0, 0, 0, 13, 11, 0, 0)]
SPLIT = 124.0   # the rows above this are packed close, so they read brighter: the boost is for the rows below it
def snout(fl, dx=0.0, dy=0.0):
    return ell(dx, CY + dy, A, B) & ~holes(FL[fl], dx, NX, dy)
for k in range(4):
    SH["fnpig_snout%d" % k] = to_rows(snout(k), DOME)
    SH["fnpig_low%d" % k] = to_rows(snout(k) & (PY < SPLIT), DOME)
    SH["fnpig_holes%d" % k] = to_rows(holes(FL[k], 0.0, NX), DOME)
# the rim alone, a neon edge round the plate
SH["fnpig_rim"] = to_rows(ell(0, CY, A, B) & ~ell(0, CY, A - 24, B - 16), DOME)
# marbling: pale streaks through the raw plate, clear of the widest nostrils
def fat():
    x = PX
    a = np.abs(PY - (146.0 - 0.0016 * x * x + 3.0 * np.sin(x / 22.0))) < 4.5
    b = np.abs(PY - (70.0 + 0.0009 * x * x)) < 5.0
    c = (np.abs(np.abs(x) - (96.0 - 0.25 * (PY - 100.0))) < 7.0) & (PY > 84) & (PY < 124)
    return (a | b | c) & ell(0, CY, A - 3, B - 3) & ~holes(FL[0])
SH["fnpig_fat"] = to_rows(fat(), DOME)
# the head thrown down on the kick, recovering through the bar's gaps
BOB = [(1, -12.0), (2, -8.0), (2, -4.0), (3, 0.0)]
for k, (fl, dy) in enumerate(BOB):
    SH["fnpig_bob%d" % k] = to_rows(snout(fl, dy=dy), DOME)
    SH["fnpig_boblow%d" % k] = to_rows(snout(fl, dy=dy) & (PY < SPLIT), DOME)
# rooting: the snout swinging side to side over a bar, snorting on the beats (8 frames at 8ths)
DX = [0, 16, 30, 16, 0, -16, -30, -16]
for k, dx in enumerate(DX):
    fl = 0 if k % 2 == 0 else 2
    SH["fnpig_root%d" % k] = to_rows(snout(fl, dx=float(dx)), DOME)
    SH["fnpig_rootlow%d" % k] = to_rows(snout(fl, dx=float(dx)) & (PY < SPLIT), DOME)

# THE WHOLE PIG: a smaller snout low on the dome, furious eyes above
FCY, FA, FB, FNX, FNY = 90.0, 104.0, 42.0, 39.0, 88.0
FFL = [(25, 26), (21, 20), (17, 15), (12, 10)]
def face(fl, dx=0.0):
    rx, ry = FFL[fl]
    return ell(dx, FCY, FA, FB) & ~nostrils(dx, FNY, FNX, rx, ry)
for k in range(4):
    SH["fnpig_face%d" % k] = to_rows(face(k), DOME)
def eyes(open_=1.0, dx=0.0):
    """a slanted slit: high at the outer end, low at the inner, the brow of a furious animal"""
    out = np.zeros(len(PX), bool)
    for side in (-1, 1):
        u = side * (PX - dx) - 58.0          # along the eye, outward positive
        centre = 141.0 + 0.32 * u            # the slant
        half = (9.0 + 8.0 * open_) * np.clip(1 - (u / 44.0) ** 2, 0, 1) ** 0.5
        out |= (np.abs(PY - centre) <= half) & (np.abs(u) <= 44.0)
    return out & (PY > FCY + FB - 4)
SH["fnpig_eyes"] = to_rows(eyes(1.0), DOME)
SH["fnpig_slits"] = to_rows(eyes(0.0), DOME)
# the head shaking, furious, eyes and snout together: 8 frames at 8ths
for k, dx in enumerate(DX):
    fl = 0 if k % 2 == 0 else 2
    SH["fnpig_shake%d" % k] = to_rows(face(fl, dx=float(dx) * 0.8), DOME)
    SH["fnpig_glare%d" % k] = to_rows(eyes(1.0, dx=float(dx) * 0.8), DOME)
# TUSKS, on the jaw: bone, from the chin to the corner of the jaw
def tusks():
    out = np.zeros(len(PX), bool)
    for side in (-1, 1):
        u = side * PX
        out |= ((u > 86) & (u < 128) & (PY < -92)) | ((u > 112) & (u < 136) & (PY >= -92) & (PY < -78)) | ((u > 134) & (u < 152) & (PY >= -78) & (PY < -62))
    return out & (PY < 0)
SH["fnpig_tusks"] = to_rows(tusks(), FULL)
p = os.path.join("shows", "scenes", BASE + ".sprites.json")
with open(p, "w") as f:
    f.write("{\n" + ",\n".join("  %s: %s" % (json.dumps(k), json.dumps(v)) for k, v in SH.items()) + "\n}\n")
print("wrote", p, len(SH), "sprites", os.path.getsize(p), "bytes")
