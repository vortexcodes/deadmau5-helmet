import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lab import sheet
BASE = "deadmau5 & Wolfgang Gartner - Animal Rights"
tr = json.load(open("shows/scenes/%s.scene.json" % BASE))
P = tr["palettes"]
DOME = {"y_lo": 40, "y_hi": 170, "x_half": 171}
TIGER = {"fx": "grad", "on": "face", "axis": "x", "axis2": "y", "scale": 9.0, "speed": 0.125, "warp": 0.45, "wscale": 0.8, "wspeed": 0.0625, "lo": 0, "hi": 1, "pal": "tiger", "gain": 0.34}
def E(sprite, color, gain=0.9, box=DOME, **k):
    return dict({"fx": "preset", "name": "sprite", "on": "shell", "mix": "over", "params": dict(box, sprite=sprite, color=color, **k), "gain": gain})
it = [
 ("tiger", "tiger", [TIGER], 8),
 ("tiger + eyes", "tiger", [TIGER, E("animal_eyes", "eye@1")], 8),
 ("tiger + eyes white", "tiger", [TIGER, E("animal_eyes", [255, 255, 220])], 8),
 ("tiger + eyes green", "tiger", [TIGER, E("animal_eyes", [120, 255, 60])], 8),
 ("tiger gain+eyes", "tiger", [dict(TIGER, gain=0.2), E("animal_eyes", "eye@1")], 8),
]
sheet(sys.argv[1], it, P)
