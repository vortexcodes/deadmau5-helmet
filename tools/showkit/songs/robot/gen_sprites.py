#!/usr/bin/env python3
"""The Robot's sprites, on the dome's own grid: 17 columns x 9 rows over y 55..172, x +-171,
where every row of the sprite holds exactly one row of LEDs (row 0 only four of them)."""
import json, os, subprocess, sys
sys.path.insert(0, os.getcwd())
import numpy as np
import mau5engine as E
BASE = "deadmau5 - Harder Better Faster Stronger"
OUT = os.path.join("shows", "scenes", BASE + ".sprites.json")
R, C = 9, 17
SPB, T0 = 0.468761, 0.003
h = E.Helmet()
# which cells of the grid hold an LED: a stencil never sets the others, because the painter
# would make such a cell claim its nearest LED, and that LED may be one meant to show
ry = (172 - h.py) / (172 - 55) * R
rx = (h.px + 171) / (2 * 171) * C
OCC = np.zeros((R, C), bool)
for i in np.where(h.shell & (h.py > 0))[0]:
    r, c = int(np.floor(ry[i])), int(np.floor(rx[i]))
    if 0 <= r < R and 0 <= c < C:
        OCC[r, c] = True
def blank(r=R, c=C):
    return np.zeros((r, c), bool)
def rows(a):
    return ["".join("#" if v else "." for v in r) for r in a]
S = {}
def put(name, a):
    S["robot_" + name] = rows(a)
# the pyramid: half-widths per row, standing on the visor (rows 7, 8)
HW = {0: 0, 1: 1, 2: 1, 3: 2, 4: 3, 5: 4, 6: 5}
def tri(rs):
    a = blank()
    for r in rs:
        w = HW[r]
        a[r, 8 - w:8 + w + 1] = True
    return a
PYR = tri(range(0, 7))
V = blank(); V[7:9, :] = True
put("pyr", PYR)
put("t1", tri([0, 1, 2]))        # the apex: white, STRONGER
put("t2", tri([3, 4]))           # blue, FASTER
put("t3", tri([5, 6]))           # green, BETTER
put("visor", V)                  # red, HARDER, the eye's own line
a = blank(1); a[0, :] = True; put("line", a)     # one row, stretched by y_lo, y_hi
# stencils: lit cells get painted near-black, over, so what is under shows only in the gaps
def st(name, open_):   # open_: what stays visible
    put(name, ~open_ & OCC)
st("st_pyr", PYR | V)                  # the whole stack
st("st_v", V)                          # the visor only
st("st_t3", tri([5, 6]) | V)           # visor + first tier
st("st_t2", tri([3, 4, 5, 6]) | V)     # + second
st("st_a", PYR)                        # the pyramid alone
st("st_top", ~V)                       # everything but the visor rows: colour bars above it
# the stack cut into tiles by gaps that step sideways: a panel of LED tiles
for k in range(4):
    gap = blank()
    gap[:, (np.arange(C) + k) % 4 == 0] = True
    st("st_tile%d" % k, (PYR & ~gap) | V)
# background panel lines: every 4th column and two rows, stepping, never on the pyramid or visor
for k in range(4):
    a = blank()
    a[:, (np.arange(C) + k) % 4 == 0] = True
    a[[2, 5], :] = True
    a[7:9, :] = False
    put("lines%d" % k, a & ~PYR & OCC)
    b = blank()
    b[:, (np.arange(C) + k) % 4 == 0] = True
    b[[2, 5], :] = True
    b[7:9, :] = False
    put("grid%d" % k, b & OCC)
# the panel lattice: every 3rd column, every 2nd row, stepping sideways
for k in range(3):
    a = blank()
    a[:, (np.arange(C) + k) % 3 == 0] = True
    a[[1, 3, 5], :] = True
    a[7:9, :] = False
    put("lat%d" % k, a & OCC)
# the face: two block eyes, a red pupil that looks round in steps, and a blink
def eyeblock(blink=False):
    a = blank()
    for cx in (4, 12):
        if blink:
            a[5, cx - 3:cx + 4] = True
        else:
            a[2:7, cx - 2:cx + 3] = True
            a[2, cx - 2] = a[2, cx + 2] = False
    return a & OCC
def pupil(dx):
    a = blank()
    for cx in (4, 12):
        a[3:6, cx + dx - 1:cx + dx + 1] = True
    return a & OCC
put("fE", eyeblock()); put("fB", eyeblock(True))
put("pL", pupil(-1)); put("pC", pupil(0) | blank()); put("pR", pupil(2)); put("pN", blank())
# the eye: a head 5 cells wide, one row of sprite, 32 frames there and back
seq = list(range(0, 17)) + list(range(15, 0, -1))
for i, c in enumerate(seq):
    a = blank(1)
    a[0, max(0, c - 2):min(C, c + 3)] = True
    put("e%02d" % i, a)
# a row scanner: one column of sprite, row r lit, rows 1 to 6
for r in range(1, 7):
    a = blank(R, 1); a[r, 0] = True; put("r%d" % r, a)
# the equaliser: lids over a rainbow, from the song's own spectrum, 16th by 16th over 4 bars
def spectrum(lo_bar, nbars):
    mp3 = os.path.join("shows", BASE + ".mp3")
    SR = 22050
    ta = T0 + lo_bar * 4 * SPB
    raw = subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-ss", str(ta), "-t", str(nbars * 4 * SPB + 0.2), "-i", mp3, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True, check=True).stdout
    m = np.frombuffer(raw, dtype=np.float32)
    N = 2048; win = np.hanning(N)
    f = np.fft.rfftfreq(N, 1 / SR)
    edges = np.geomspace(35, 11000, 10)
    H = np.zeros((nbars * 16, 9))
    for k in range(nbars * 16):
        s0 = int(k * SPB / 4 * SR)
        vals = []
        for off in (0, 400, 800):
            x = m[s0 + off:s0 + off + N]
            if len(x) < N:
                continue
            F = np.abs(np.fft.rfft(x * win))
            vals.append([np.log1p(F[(f >= a) & (f < b)].mean() * 2) for a, b in zip(edges, edges[1:])])
        H[k] = np.max(vals, axis=0)
    return H
def eq_frames(lo_bar=96, nbars=4):
    H = spectrum(lo_bar, nbars)
    lo = np.percentile(H, 8, axis=0); hi = np.percentile(H, 98, axis=0)
    L = np.clip((H - lo) / np.maximum(hi - lo, 1e-6), 0, 1) ** 1.3
    n = len(L); out = L.copy()
    # ballistics: up at once, down a sixth of the height a 16th, round the loop
    for _ in range(2):
        for k in range(n):
            out[k] = np.maximum(L[k], out[k - 1] - 0.16)
    # the rows each column really has, from its lowest row up
    top = [int(np.where(OCC[:, c])[0].min()) for c in range(C)]
    lit = np.zeros((n, C), int)
    for k in range(n):
        for c in range(C):
            lit[k, c] = int(round(out[k, abs(c - 8)] * (8 - top[c])))
    # white caps: hold the highest row, falling one row every two 16ths
    cap = lit.astype(float).copy()
    for _ in range(2):
        for k in range(n):
            cap[k] = np.maximum(lit[k], cap[k - 1] - 0.5)
    for k in range(n):
        a = blank(); c_ = blank()
        for c in range(C):
            a[8 - lit[k, c]:9, c] = True
            top_cap = 8 - int(np.ceil(cap[k, c]))
            if cap[k, c] >= 1 and top_cap >= top[c]:
                c_[top_cap, c] = True
        put("q%02d" % k, ~a & OCC)   # lid: hide what is not lit
        put("c%02d" % k, c_ & OCC)   # cap
    return out
if __name__ == "__main__":
    Q = eq_frames()
    json.dump(S, open(OUT, "w"), indent=0)
    print("wrote", OUT, len(S), "sprites", os.path.getsize(OUT), "bytes")
    print("\n".join(rows(OCC)))
