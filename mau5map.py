#!/usr/bin/env python3
"""mau5map -- the chain, in space.

Everything downstream needs one thing: given a position in the chain,
where is that LED on the helmet.  This is where that answer is read
from, with any hand corrections applied on top.

The map itself is built by mau5slots.py, which puts every LED in a
place the CAD has room for one -- a shell slot, or a tube or the rim
of an ear -- and uses two calibrated camera views only to decide
which.  It used to be built here, from the CAD's wiring order and a
model of the ears, and then corrected along the camera rays; every
part of that turned out to be wrong somewhere, and mau5slots says
where.

Coordinates are the CAD's own, which is not the obvious frame: +z is
UP and the face looks along -y, so

    elev = atan2(z, hypot(x, y))      az = atan2(x, -y)

and +x is the audience's right.  Millimetres, origin at the centre of
the head sphere.

    python3 mau5map.py        # rebuild the map (runs mau5slots)
"""

from __future__ import annotations

import csv
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "data", "cal", "pixel_map.csv")

# 621.  It was 622 -- index 622 stayed dark at full brightness and so
# did everything past it, measured by probing the tail with the bus
# widened to 640 -- until 2026-10-29, when one segment was cut off the
# start of the near ear's rim and 621 went dark too (mau5slots.CUT).
# The controller still drives 622; the last one has nothing behind it.
TOTAL_N = 621
# 398, not the CAD's 399: strip B04 is one LED short of its slots.  The
# first walk said so, and both cameras agree (mau5slots.py).
SHELL_N = 398


ADJUST = os.path.join(os.path.dirname(OUT), "adjust.json")


def apply_adjustments(rows, path=ADJUST):
    """Hand corrections, applied on top of the measured map.

    The map knows what the CAD knows and what two cameras could see.
    Neither knows about a part that was assembled differently from the
    drawing -- an ear bolted on a few degrees off, a strip moved to
    clear a magnet -- and those are visible to somebody standing in
    front of the helmet in about two seconds.  `mau5lines.py` is how
    that person writes down what they saw.

    Kept as a separate file rather than edited into pixel_map.csv so
    that re-running the localisation does not quietly discard them,
    and so that what was measured and what was judged by eye stay
    told apart.  Applied in order; later entries see earlier ones.

      move     add (dx, dy, dz) mm to the span's positions
      reverse  turn the span's positions end for end
      shift    take each LED's position from `by` places further
               along its own strip -- the correction for LEDs cut
               out of a run, where the chain does not skip but the
               geometry does
      region   relabel the span, for a run that is not on the
               surface it was filed under
    """
    if not os.path.exists(path):
        return rows, []
    try:
        with open(path) as f:
            doc = json.load(f)
    except (ValueError, OSError):
        # An empty or half-written file must not take the map with it:
        # this is read by everything, including the show player.
        return rows, []
    done = []
    for a in doc.get("spans", []):
        lo, hi = int(a["lo"]), int(a["hi"])
        span = [r for r in rows if lo <= r["index"] <= hi]
        if not span:
            continue
        op = a.get("op")
        if op == "move":
            for r in span:
                r["x"] += float(a.get("dx", 0.0))
                r["y"] += float(a.get("dy", 0.0))
                r["z"] += float(a.get("dz", 0.0))
        elif op == "reverse":
            pts = [(r["x"], r["y"], r["z"]) for r in span][::-1]
            for r, p in zip(span, pts):
                r["x"], r["y"], r["z"] = p
        elif op == "shift":
            by = int(a.get("by", 0))
            for g in set(r["group"] for r in span):
                strip = [r for r in rows if r["group"] == g]
                strip.sort(key=lambda r: r["pos_in_strip"])
                pts = [(r["x"], r["y"], r["z"]) for r in strip]
                at = {r["index"]: i for i, r in enumerate(strip)}
                for r in span:
                    if r["group"] != g:
                        continue
                    j = min(max(at[r["index"]] + by, 0), len(pts) - 1)
                    r["x"], r["y"], r["z"] = pts[j]
        elif op == "region":
            for r in span:
                r["region"] = str(a["to"])
        else:
            continue
        done.append(a)
    if done:
        _rederive(rows)
    return rows, done


def _rederive(rows):
    """az and elev follow from x, y, z, so a moved LED has to redo them."""
    for r in rows:
        x, y, z = r["x"], r["y"], r["z"]
        r["az_deg"] = round(math.degrees(math.atan2(x, -y)) % 360.0, 2)
        rad = math.hypot(x, y)
        r["elev_deg"] = round(math.degrees(math.atan2(z, rad or 1e-9)), 2)


def load(path=OUT, adjust=True):
    rows = list(csv.DictReader(open(path)))
    for r in rows:
        for k in ("x", "y", "z", "az_deg", "elev_deg", "u"):
            r[k] = float(r[k])
        for k in ("index", "group", "pos_in_strip", "swap_rg"):
            r[k] = int(r[k])
        # Which ear tube, and how far up it (0 low end, 1 high end) --
        # or for a rim LED, how far round from the bottom.  -1 on the
        # shell, and on a map written before mau5slots knew the tubes.
        r["tube"] = int(r.get("tube") or -1)
        r["along"] = float(r.get("along") or -1.0)
    if adjust:
        rows, _ = apply_adjustments(rows)
    return rows


if __name__ == "__main__":
    import mau5slots
    mau5slots.main()
