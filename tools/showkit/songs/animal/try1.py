import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lab import sheet
P = {
  "tiger": [[0, 0, 0], [0, 0, 0], [40, 5, 0], [255, 80, 0], [255, 125, 5]],
  "tiger2": [[0, 0, 0], [0, 0, 0], [255, 70, 0], [255, 110, 0], [255, 150, 10]],
  "zebra": [[0, 0, 0], [0, 0, 0], [20, 20, 22], [220, 225, 235], [255, 255, 255]],
  "zebra2": [[0, 0, 0], [0, 0, 0], [240, 240, 245], [255, 255, 255]],
  "cobra": [[0, 0, 0], [0, 0, 0], [0, 30, 10], [0, 170, 50], [100, 255, 40], [220, 255, 70]],
  "steel": [[0, 0, 0], [0, 0, 0], [0, 0, 0], [20, 34, 50], [70, 100, 130], [140, 170, 195]],
  "peacock": {"stops": [[0, 30, 170], [0, 120, 200], [0, 210, 150], [40, 240, 70], [210, 200, 30], [0, 210, 150], [0, 120, 200]], "wrap": True},
}
def G(**k):
    d = {"fx": "grad", "on": "shell", "lo": 0, "hi": 1, "gain": 0.28}
    d.update(k); return d
it = [
 ("tiger x7 w.32", "tiger", [G(pal="tiger", axis="x", axis2="y", scale=7, warp=0.32, wscale=0.9)], 0),
 ("tiger x8 w.5", "tiger", [G(pal="tiger", axis="x", axis2="y", scale=8, warp=0.5, wscale=0.7)], 0),
 ("tiger2 x7 w.4", "tiger2", [G(pal="tiger2", axis="x", axis2="y", scale=7, warp=0.4, wscale=0.6)], 0),
 ("tiger2 x7 slant", "tiger2", [G(pal="tiger2", axis="x", axis2="y", scale=7, warp=0.7, wscale=0.35)], 0),
 ("tiger2 x10", "tiger2", [G(pal="tiger2", axis="x", axis2="y", scale=10, warp=0.5, wscale=0.8)], 0),
 ("zebra x9 w.5", "zebra2", [G(pal="zebra2", axis="x", axis2="y", scale=9, warp=0.5, wscale=0.7, gain=0.24)], 0),
 ("zebra y5 w.5", "zebra2", [G(pal="zebra2", axis="y", axis2="x", scale=5, warp=0.5, wscale=1.3, gain=0.24)], 0),
 ("zebra y7 w.7", "zebra2", [G(pal="zebra2", axis="y", axis2="x", scale=7, warp=0.7, wscale=1.0, gain=0.24)], 0),
 ("zebra r6 w.3", "zebra2", [G(pal="zebra2", axis="r", axis2="a", scale=6, warp=0.3, wscale=3, gain=0.24)], 0),
 ("zebra a9 r", "zebra2", [G(pal="zebra2", axis="a", axis2="r", scale=11, warp=0.5, wscale=0.8, gain=0.24)], 0),
 ("cobra y2.2", "cobra", [G(pal="cobra", axis="y", axis2="x", scale=2.2, warp=0.42, wscale=1.5)], 0),
 ("cobra y3 w.6", "cobra", [G(pal="cobra", axis="y", axis2="x", scale=3, warp=0.6, wscale=2)], 0),
 ("cobra y4 w.8", "cobra", [G(pal="cobra", axis="y", axis2="x", scale=4, warp=0.8, wscale=2.5)], 0),
 ("cobra y3 w1", "cobra", [G(pal="cobra", axis="y", axis2="x", scale=2, warp=0.9, wscale=3)], 0),
 ("cage x8", "steel", [G(pal="steel", axis="x", axis2="x", scale=8, gain=0.8)], 0),
 ("cage x10", "steel", [G(pal="steel", axis="x", axis2="x", scale=10, gain=0.8)], 0),
 ("fan a9 saw", None, [G(pal="peacock", axis="a", axis2="r", scale=9, wave="saw", warp=0.06, gain=0.25)], 0),
 ("fan a12 saw", None, [G(pal="peacock", axis="a", axis2="r", scale=14, wave="saw", warp=0.1, gain=0.25)], 0),
 ("fan a3 r", None, [G(pal="peacock", axis="a", axis2="r", scale=3, warp=0.4, wscale=4, gain=0.25)], 0),
 ("fan r", None, [G(pal="peacock", axis="r", axis2="a", scale=2, wave="saw", warp=0.1, wscale=9, gain=0.25)], 0),
]
sheet(sys.argv[1], it, P)
