#!/usr/bin/env python3
"""mau5map -- the chain, in space.

Everything downstream needs one thing: given a position in the chain,
where is that LED on the helmet.  This builds it.

The 399 shell LEDs come from the CAD, which the camera has now checked
in four independent ways -- the chain starts at the chin, ends at the
upper left, groups 0 and 29 land symmetric about the centre line, and
the disputed pair in the bottom band fell the CAD's way.  So the CAD is
treated as authoritative for the shell.

Two things it is *not* authoritative about.

The direction each strip is wired.  The CAD stores LEDs per strip in a
fixed order, and the spacing proves that is not the order the chain
runs: hops between consecutive strips come out at 34 mm median and up
to 216 mm, where a real boustrophedon snake would hop one strip pitch.
So each strip is flipped or not, greedily, to keep the chain
continuous -- the orientation that puts its first LED nearest the
previous strip's last.

And the ears, which are not in the CAD at all; the ones on the helmet
now were rebuilt by hand after it was drawn.  Those are a parametric
model fitted to what the camera saw, and are marked `estimated` in the
output so nothing downstream mistakes them for measurements.
"""

from __future__ import annotations

import csv
import math
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CAD = os.path.join(HERE, "data", "cad", "pixel_map_cad.csv")
OUT = os.path.join(HERE, "data", "cal", "pixel_map.csv")

ROT = 38                 # walk group 0 is CAD chain-B strip 39 (zero-based 38)
SHELL_N = 399
# 622, not 623.  Index 622 stays dark at full brightness and so does
# everything past it, measured by probing the tail with the bus widened
# to 640 -- the walk's last tap went one LED beyond the end of the chain.
TOTAL_N = 622

# Ear model.  Millimetres, in the CAD's own frame, which is not the
# obvious one: +z is UP and the face looks along -y, so
#     elev = atan2(z, hypot(x, y))      az = atan2(x, -y)
# Verified against the CAD rather than assumed -- getting this wrong
# silently lays every glyph on its side.
# Fitted to the square-on camera view, where the sphere measured ~1 px/mm:
# ear centres sat ~200 px left/right of the head centre and ~200 px above.
EARS = {
    "ear1": {"centre": (-195.0, 30.0, 200.0), "radius": 150.0, "tilt": -20.0},
    "ear2": {"centre": (215.0, 30.0, 205.0), "radius": 150.0, "tilt": 20.0},
}
# Chain layout inside the ear block, measured by lighting blocks and
# watching which ear lit and whether the colour came back swapped.
EAR_SPANS = [
    ("ear1_tubes", 399, 491, "ear1", "tubes"),
    ("ear1_rim",   492, 510, "ear1", "rim"),
    ("ear2_rim",   511, 527, "ear2", "rim"),
    ("ear2_tubes", 528, 621, "ear2", "tubes"),
]
EAR_TUBE_COUNT = 5            # diagonal runs across each disc, from the photos
RIM_ARC_DEG = (200.0, 20.0)   # the rim is an arc, not a full circle


def _dist(a, b):
    return math.dist(a, b)


def shell_chain(path=CAD, meas=None, verbose=False):
    """The 399 shell LEDs in chain order, each strip oriented correctly.

    The CAD knows where each strip's LEDs are; it does not know which
    end of each strip the chain enters.  Two heuristics were tried and
    both failed against the camera -- the CSV's stored order agrees
    with it on 48% of strips and "flip whichever end sits nearer the
    previous strip" on 19%, which is worse than a coin.  The wiring
    simply is not a tidy boustrophedon.

    So the camera decides, one strip at a time.  Within a strip the
    question is only which way round the LEDs run, and ordering
    survives the diffuser's displacement because that displacement is
    smooth: it moves a glow, it does not reshuffle a sequence.  Strips
    too short to give a reliable slope keep continuity with the
    previous strip's end, which is all that is left to go on.
    """
    rows = [r for r in csv.DictReader(open(path)) if r["chain"] == "B"]
    rows.sort(key=lambda r: int(r["index"]))
    strips, order = {}, []
    for r in rows:
        if r["strip"] not in strips:
            strips[r["strip"]] = []
            order.append(r["strip"])
        strips[r["strip"]].append(r)

    seq = [order[(ROT + i) % len(order)] for i in range(len(order))]
    out, prev_end, flips, decided = [], None, 0, 0
    idx = 0
    for gi, name in enumerate(seq):
        leds = list(strips[name])
        pts = [(float(r["x"]), float(r["y"]), float(r["z"])) for r in leds]
        n = len(leds)

        rev = None
        if meas and n >= 3 and all((idx + j) in meas for j in range(n)):
            z = np.array([float(r["z"]) for r in leds])
            cy = np.array([meas[idx + j]["cy"] for j in range(n)])
            k = np.arange(n)
            zs = np.polyfit(k, z, 1)[0]
            cs = np.polyfit(k, cy, 1)[0]
            if abs(zs) > 1.0 and abs(cs) > 1.0:
                # height up in the world means row down in the image
                rev = (zs * cs) > 0
                decided += 1
        if rev is None and prev_end is not None and n > 1:
            rev = _dist(prev_end, pts[-1]) < _dist(prev_end, pts[0])
        if rev:
            leds.reverse(); pts.reverse(); flips += 1

        for j, r in enumerate(leds):
            out.append({"group": gi, "strip": name, "pos": j,
                        "n_in_strip": n,
                        "x": float(r["x"]), "y": float(r["y"]), "z": float(r["z"]),
                        "az": float(r["az_deg"]), "elev": float(r["elev_deg"])})
        idx += n
        prev_end = pts[-1]
    if verbose:
        print("  %d strips oriented from the camera, %d from continuity, %d flipped"
              % (decided, len(seq) - decided, flips))
    return out, flips


def ear_leds():
    """Parametric positions for the 224 ear LEDs.

    Each ear is a disc standing roughly upright and facing forward,
    rotated a little about the vertical.  `u` runs across the disc and
    `v` up it; the disc's own plane is then tilted into the head frame.
    """
    out = []
    for name, lo, hi, ear, kind in EAR_SPANS:
        cfg = EARS[ear]
        cx, cy, cz = cfg["centre"]
        R = cfg["radius"]
        tilt = math.radians(cfg["tilt"])
        n = hi - lo + 1
        for k in range(n):
            if kind == "rim":
                a0, a1 = RIM_ARC_DEG
                t = k / max(n - 1, 1)
                ang = math.radians(a0 + (a1 - a0) * t)
                u, v = R * math.cos(ang), R * math.sin(ang)
            else:
                per = max(1, n // EAR_TUBE_COUNT)
                tube = min(k // per, EAR_TUBE_COUNT - 1)
                within = (k % per) / max(per - 1, 1)
                if tube % 2:
                    within = 1.0 - within
                off = (tube - (EAR_TUBE_COUNT - 1) / 2.0) * (1.5 * R / EAR_TUBE_COUNT)
                half = math.sqrt(max(R * R - off * off, 1.0)) * 0.92
                d = math.radians(35.0)      # tubes run diagonally
                u = off * math.cos(d) - (half * (2 * within - 1)) * math.sin(d)
                v = off * math.sin(d) + (half * (2 * within - 1)) * math.cos(d)
            x = cx + u * math.cos(tilt)
            y = cy + u * math.sin(tilt)      # tilt swings the disc about +z
            z = cz + v
            out.append({"group": -1, "strip": name, "pos": k, "n_in_strip": n,
                        "x": x, "y": y, "z": z,
                        "az": math.degrees(math.atan2(x, -y)) % 360.0,
                        "elev": math.degrees(math.atan2(z, math.hypot(x, y)))})
    return out


def build(meas=None, verbose=True):
    shell, flips = shell_chain(meas=meas, verbose=verbose)
    if len(shell) != SHELL_N:
        raise SystemExit("expected %d shell leds, CAD gave %d" % (SHELL_N, len(shell)))
    ears = ear_leds()
    rows = []
    for i, r in enumerate(shell + ears):
        region = ("shell" if i < SHELL_N else r["strip"])
        rows.append({
            "index": i, "region": region, "strip": r["strip"],
            "group": r["group"], "pos_in_strip": r["pos"],
            "u": round(r["pos"] / max(r["n_in_strip"] - 1, 1), 4),
            "x": round(r["x"], 2), "y": round(r["y"], 2), "z": round(r["z"], 2),
            "az_deg": round(r["az"], 2), "elev_deg": round(r["elev"], 2),
            "source": "cad" if i < SHELL_N else "estimated",
            "swap_rg": 1 if 492 <= i <= 527 else 0,
        })
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", newline="") as f:
        wri = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        wri.writeheader(); wri.writerows(rows)
    return rows, flips


def load(path=OUT):
    rows = list(csv.DictReader(open(path)))
    for r in rows:
        for k in ("x", "y", "z", "az_deg", "elev_deg", "u"):
            r[k] = float(r[k])
        for k in ("index", "group", "pos_in_strip", "swap_rg"):
            r[k] = int(r[k])
    return rows


if __name__ == "__main__":
    try:
        import mau5locate
        _meas = mau5locate.load()
        if _meas:
            print("using %d measured centroids to orient the strips" % len(_meas))
    except Exception:
        _meas = None
    rows, flips = build(meas=_meas)
    print("wrote %s  (%d leds, %d strips flipped to keep the chain continuous)"
          % (OUT, len(rows), flips))
    import collections
    print("  by region:", dict(collections.Counter(r["region"] for r in rows)))
    pts = [(r["x"], r["y"], r["z"]) for r in rows[:SHELL_N]]
    hops = [math.dist(pts[i], pts[i+1]) for i in range(len(pts)-1)]
    import statistics as st
    print("  shell consecutive spacing: median %.2f mm, max %.2f mm"
          % (st.median(hops), max(hops)))
    over = [i for i, h in enumerate(hops) if h > 60]
    print("  hops over 60mm: %d %s" % (len(over), over[:8]))
