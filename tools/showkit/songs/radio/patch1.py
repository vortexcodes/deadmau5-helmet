import re,os
p=os.environ["W"]+"/write_treatment.py"
s=open(p).read()
# ---- replace everything from the helpers' rings to the end with the second draft
head=s[:s.index("def rings(beats")]
tail=r'''
BEATS_RING = 1.0
def rings(beats, gain, pal="rings_t", per=1, cg=6.0, rad=440, soft=260, on="shell+rims", inward=False, x=0, y=170, gate=True, phase=0.0):
    """Broadcast rings from the top of the head: one leaves on each `per` beats of this scene."""
    st = {"rings_t": 8, "rings_m": 8, "rings_a": 8}[pal]
    n = beats / float(per)
    c0 = 1.0 / st + phase
    L = {"fx": "orb", "on": on, "x": x, "y": y, "rad": rad, "soft": soft, "pal": pal,
         "c": [c0 + n, c0] if inward else [c0, c0 - n], "cgrad": cg, "gain": gain}
    if gate:
        L["gate"] = {"pat": KICK, "step": 0.25, "decay": 0.9, "floor": 0.45}
    return L

def rings2(beats, gain, per=1, cg=6.0, rad=440, soft=260, on="shell+rims", inward=False, x=0, y=170, gate=True):
    """The same, teal and magenta in turn: the palette holds two rings, so one cycle is 2 x per beats."""
    n = beats / (2.0 * per)
    c0 = 1.0 / 16
    L = {"fx": "orb", "on": on, "x": x, "y": y, "rad": rad, "soft": soft, "pal": "rings_tm",
         "c": [c0 + n, c0] if inward else [c0, c0 - n], "cgrad": cg / 2.0, "gain": gain}
    if gate:
        L["gate"] = {"pat": KICK, "step": 0.25, "decay": 0.9, "floor": 0.45}
    return L

def needle_keys(path, b0, b1):
    """A needle along a path of (bar, angle): one straight piece a beat, as from/to keys. Scene starts at b0."""
    def at(b):
        for (a0, v0), (a1, v1) in zip(path, path[1:]):
            if a0 <= b <= a1:
                return v0 + (v1 - v0) * (b - a0) / max(a1 - a0, 1e-9)
        return path[-1][1] if b > path[-1][0] else path[0][1]
    n = int(round((b1 - b0) * 4))
    fr, to = {}, {}
    for k in range(n):
        bb = b0 + k / 4.0
        fr[str(bb)] = round(at(bb), 4)
        to[str(bb)] = round(at(bb + 0.25), 4)
    return fr, to, at

def needle(path, b0, b1, gain, width=0.03, c=0.85):
    fr, to, _ = needle_keys(path, b0, b1)
    return {"fx": "sweep", "on": "face", "axis": "a", "shape": "saw", "speed": 1, "mode": "band", "width": width,
            "from": fr, "to": to, "pal": "dial", "c": c, "gain": gain}

def static_keys(path, b0, b1, level):
    """Static is loudest away from the station: it dips each time the needle crosses the middle."""
    _, _, at = needle_keys(path, b0, b1)
    n = int(round((b1 - b0) * 4))
    keys = {}
    for k in range(n):
        bb = b0 + k / 4.0
        d = min(abs(at(bb + 0.125) - 0.25) / 0.16, 1.0)
        keys[str(bb)] = round(level(bb) * (0.3 + 0.7 * d), 3)
    return keys

LAMP = lambda gain, rad=190, soft=190, c=0.8: {"fx": "orb", "on": "face", "x": 0, "y": 53, "rad": rad, "soft": soft, "pal": "dial", "c": c, "cgrad": -0.45, "gain": gain}
TICKS = lambda gain, scale=16: {"fx": "grad", "on": "face", "axis": "a", "axis2": "r", "scale": scale, "ofs": 0.0, "pal": "tick", "gain": gain}
STATIC = lambda gain, on="all", rate=7: {"fx": "twinkle", "on": on, "rate": rate, "sharp": 5, "dens": 0.75, "pal": "static", "c": 0.0, "spread": 1.0, "seed": 4.0, "gain": gain}
WAVE = lambda pal, warp, gain, wspeed=0.25, wscale=2, ofs=0.0: {"fx": "grad", "on": "face", "axis": "y", "axis2": "x", "scale": 2, "ofs": ofs, "warp": warp, "wscale": wscale, "wspeed": wspeed, "pal": pal, "gain": gain}
JAW = lambda gain, pal="neon", c=0.0, scale=9: {"fx": "grad", "on": "jaw", "axis": "x", "axis2": "y", "scale": scale, "pal": pal, "c": c, "gain": gain, "lo": 0.0, "hi": 1.0}
PEAK = lambda gain, c=0.75, pat=KICK: {"fx": "fill", "on": "rims", "pal": "neon", "c": c, "gain": gain, "gate": {"pat": pat, "step": 0.25, "decay": 0.6}}
BEACON = lambda gain=0.9, pat="x.......", decay=1.2, floor=0.2: {"fx": "orb", "on": "shell", "mix": "over", "x": 0, "y": 166, "rad": 24, "soft": 12, "pal": "beacon", "c": 0.5, "gain": gain, "gate": {"pat": pat, "step": 0.25, "decay": decay, "floor": floor}}
MAST = lambda gain=0.75: {"fx": "sweep", "on": "face", "axis": "x", "shape": "p", "mode": "band", "width": 0.035, "from": 0.5, "to": 0.5, "pal": "dial", "c": 0.95, "gain": gain}
NEEDLE_VU = lambda lo, hi, b="high", gain=0.9, punch=False: {"fx": "sweep", "on": "face", "axis": "a", "shape": "p", "mode": "band", "width": 0.03, "from": band(b, lo, hi, punch), "to": band(b, lo, hi, punch), "pal": "dial", "c": 0.95, "gain": gain}
# The ears: left reads the kick, right reads the chords pumping between the kicks
VU_KICK = lambda on, gain=0.6: vu(on, band("bass", 0.02, 1.25, True), gain)
VU_PUMP = lambda on, gain=0.55: vu(on, band("mid", -0.08, 1.15), gain)
VU_MID = lambda on, gain=0.5: vu(on, band("mid", -1.0, 1.25), gain)
VU_HIGH = lambda on, gain=0.5: vu(on, band("high", -0.7, 1.45), gain)

# ---- the path of the needle ------------------------------------------------
# Angles on the half-moon dial: 0.03 far right, 0.25 straight up (the station), 0.47 far left.
HUNT1 = [(-0.125, 0.44), (0.875, 0.44), (1.25, 0.10), (1.875, 0.10), (2.25, 0.36), (2.875, 0.36), (3.25, 0.06), (3.875, 0.06),
         (4.25, 0.32), (4.875, 0.32), (5.25, 0.14), (5.875, 0.14), (6.25, 0.30), (6.875, 0.30), (7.25, 0.20), (7.625, 0.20), (7.875, 0.27), (8.0, 0.25)]
HUNT2 = [(64.0, 0.08), (64.875, 0.08), (65.25, 0.42), (65.875, 0.42), (66.25, 0.16), (66.875, 0.16), (67.25, 0.38),
         (67.875, 0.38), (68.25, 0.12), (68.875, 0.12), (69.25, 0.33), (69.875, 0.33), (70.25, 0.18), (70.875, 0.18), (71.25, 0.29), (71.625, 0.29), (71.875, 0.23), (72.0, 0.25)]
FALL1 = [(59.0, 0.25), (59.5, 0.25), (59.75, 0.33), (60.0, 0.40), (61.0, 0.47)]
FALL2 = [(107.0, 0.25), (107.25, 0.25), (107.25, 0.31), (107.5, 0.31), (107.5, 0.37), (107.75, 0.37), (107.75, 0.43), (108.0, 0.43)]

def ringpal(rgb, tail=0.24):
    r = [int(x) for x in rgb]
    return {"stops": [[0, 0, 0], r, [int(x * tail) for x in r], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0]], "wrap": True}
TEAL, MAG, AMBER = [0, 255, 210], [255, 0, 170], [255, 150, 30]

tr = {"v": 1, "show": BASE,
"about": ABOUT,
"lead": 0,
"marks": {"tune": 0, "lock": 8, "drums": 12, "song": 16, "songb": 20, "fade": 24, "gap": 27.75, "drop": 28, "rings": 30, "dropb": 36, "dropc": 44, "dropd": 52,
          "fall": 59, "tail": 60, "retune": 64, "lock2": 72, "song2": 76, "song2b": 84, "fade2": 88, "gap2": 91.75, "drop2": 92, "rings2": 94, "drop2b": 100, "fall2": 107, "off": 108, "end": 112},
"palettes": {
 "dial": [[0, 0, 0], [60, 18, 0], [200, 90, 8], [255, 160, 40], [255, 215, 130]],
 "tick": [[0, 0, 0], [0, 0, 0], [255, 150, 30]],
 "static": [[80, 95, 130], [190, 200, 225], [255, 190, 120]],
 "vu": [[0, 220, 180], [0, 235, 120], [255, 170, 20], [255, 30, 60], [255, 0, 130]],
 "neon": [[0, 255, 210], [0, 170, 255], [120, 60, 255], [255, 0, 170], [255, 30, 110]],
 "wave_t": [[0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 50, 45], [0, 255, 210]],
 "wave_m": [[0, 0, 0], [0, 0, 0], [0, 0, 0], [60, 0, 40], [255, 0, 170]],
 "rings_t": ringpal(TEAL),
 "rings_m": ringpal(MAG),
 "rings_a": ringpal(AMBER),
 "rings_tm": {"stops": ringpal(TEAL)["stops"] + ringpal(MAG)["stops"], "wrap": True},
 "beacon": [[255, 0, 60], [255, 0, 90], [255, 60, 130]],
 "sign": [[255, 0, 70], [255, 10, 90], [255, 80, 150]],
 "white": [[255, 200, 120], [255, 240, 220], [255, 255, 255]]},
"motifs": {},
"scenes": [], "hits": []}
S = tr["scenes"].append
PUMP = {"pat": KICK, "step": 0.25, "depth": 0.22, "decay": 0.5}
BEAT = {"pat": "x...", "step": 0.25, "depth": 0.14, "decay": 0.5}

# ---- 0-8: tuning. Static over everything, the needle hunting across the dial, the meters climb as the filter opens
LEVEL1 = lambda b: 0.62 - 0.03 * max(b, 0)
S({"name": "tuning", "from": -0.125, "to": "lock", "pal": "dial", "layers": [
  STATIC(static_keys(HUNT1, -0.125, 8, LEVEL1)),
  LAMP([0.05, 0.14]), TICKS([0.05, 0.14]),
  needle(HUNT1, -0.125, 8, 0.85),
  vu("tubes1", band("mid", -0.05, 1.0), [0.2, 0.45]),
  vu("tubes2", band("high", -0.05, 1.9), [0.2, 0.45])]})
# ---- 8-16: locked on. The static is gone, the dial is lit, the needle now reads the level
S({"name": "locked", "from": "lock", "to": "drums", "pal": "dial", "layers": [
  LAMP(0.22), TICKS(0.16), NEEDLE_VU(0.61, 0.01),
  JAW(band("bass", 0.0, 0.30, True), pal="dial", c=0.8),
  VU_MID("tubes1", 0.45), VU_HIGH("tubes2", 0.45)]})
S({"name": "drums", "from": "drums", "to": "song", "pal": "dial", "pump": BEAT, "layers": [
  LAMP([0.22, 0.28]), TICKS([0.16, 0.2]), NEEDLE_VU(0.61, 0.01),
  JAW(band("bass", 0.05, 0.6, True), pal="dial", c=0.9),
  VU_MID("tubes1"), VU_HIGH("tubes2")]})
# ---- 16-24: the song. The signal itself: a neon sine across the dial, the speaker on the jaw
WARP = band("mid", 0.02, 0.32)
S({"name": "signal", "from": "song", "to": "songb", "pal": "neon", "pump": BEAT, "layers": [
  LAMP(0.09), WAVE("wave_t", WARP, 0.7),
  JAW(band("bass", 0.05, 0.55, True), c=0.1),
  VU_MID("tubes1"), VU_HIGH("tubes2"),
  PEAK(0.3, c=0.8, pat="x...")]})
S({"name": "signal2", "from": "songb", "to": "fade", "like": "signal", "patch": {"1": {"wspeed": 0.5, "wscale": 3}}})
# ---- 24-28: interference. The drums are gone, the sine flattens, the static creeps back
S({"name": "interference", "from": "fade", "to": "drop", "pal": "neon", "out": 1, "layers": [
  STATIC([0.0, 0.7]),
  LAMP([0.09, 0.03]),
  WAVE("wave_t", [0.3, 0.0], [0.6, 0.2], wspeed=0.25),
  vu("tubes1", band("mid", -0.4, 1.0), [0.4, 0.15]),
  vu("tubes2", band("high", -0.4, 1.4), [0.4, 0.15])]})
# ---- 28-60: on air. The sign, then the needle stands up as the mast, the beacon blinks, rings go out on every beat
SIGNL = lambda rate=FLIP2, gain=0.9, c=0.5: {"fx": "preset", "name": "sprite", "on": "shell", "mix": "over", "params": dict(SIGN, sprite="radioedit_on|radioedit_air", rate=rate, color="sign@%g" % c), "gain": gain}
def sign_scene(name, a, b, pump=PUMP, gain=0.9):
    S({"name": name, "from": a, "to": b, "pal": "neon", "pump": pump, "layers": [SIGNL(gain=gain), VU_KICK("tubes1"), VU_PUMP("tubes2"), PEAK(0.5)]})
def air(ring, extra=()):
    return (ring if isinstance(ring, list) else [ring]) + [MAST(), BEACON(), VU_KICK("tubes1"), VU_PUMP("tubes2")] + list(extra)
sign_scene("ON AIR", "drop", "rings")
S({"name": "on air", "from": "rings", "to": "dropb", "pal": "neon", "pump": PUMP, "layers": air(rings(24, 0.6))})
sign_scene("ON AIR b", "dropb", "dropb+1")
S({"name": "on air b", "from": "dropb+1", "to": "dropc", "pal": "neon", "pump": PUMP, "layers": air(rings2(28, 0.6), [PEAK(0.4)])})
sign_scene("ON AIR c", "dropc", "dropc+1")
# two transmitters, one in each ear, the rings crossing on the dome
TXL = rings(14, 0.5, per=1, x=-232, y=232, rad=470, soft=240, on="all", cg=6.0, pal="rings_t")
TXR = rings(14, 0.5, per=1, x=232, y=232, rad=470, soft=240, on="all", cg=6.0, pal="rings_m")
S({"name": "stereo", "from": "dropc+1", "to": "dropc+4.5", "pal": "neon", "pump": PUMP, "layers": [TXL, TXR, BEACON(), VU_KICK("tubes1", 0.45), VU_PUMP("tubes2", 0.4)]})
S({"name": "stereo b", "from": "dropc+4.5", "to": "dropd", "like": "stereo"})
sign_scene("ON AIR d", "dropd", "dropd+1")
S({"name": "on air d", "from": "dropd+1", "to": "fall", "pal": "neon", "pump": PUMP, "layers": [
  rings2(24, 0.5), WAVE("wave_t", band("mid", 0.02, 0.32), 0.45), MAST(0.6), BEACON(), VU_KICK("tubes1"), VU_PUMP("tubes2")]})
# ---- 59: the fill, the needle starts to slip off the station
S({"name": "slip", "from": "fall", "to": "tail", "pal": "neon", "layers": [
  LAMP([0.3, 0.2]), TICKS(0.12), needle(FALL1, 59, 60, 0.9),
  vu("tubes1", band("mid", -0.1, 1.1), 0.5), vu("tubes2", band("high", -0.1, 1.1), 0.5)]})
# ---- 60-64: sign-off. The sound dies, the title crosses once, the static comes back up under it
S({"name": "sign-off", "from": "tail", "to": "retune", "pal": "dial", "layers": [
  LAMP([0.14, 0.03]),
  STATIC([0.0, 0.25], rate=5),
  vu("tubes1", band("mid", 0.0, 1.0), 0.35),
  vu("tubes2", band("high", 0.0, 1.0), 0.35)]})
# ---- 64-72: tuning again
LEVEL2 = lambda b: 0.55 - 0.03 * (b - 64)
S({"name": "retune", "from": "retune", "to": "lock2", "pal": "dial", "layers": [
  STATIC(static_keys(HUNT2, 64, 72, LEVEL2)),
  LAMP([0.05, 0.16]), TICKS([0.05, 0.16]),
  needle(HUNT2, 64, 72, 0.85),
  vu("tubes1", band("mid", -0.05, 1.0), [0.2, 0.45]),
  vu("tubes2", band("high", -0.05, 1.9), [0.2, 0.45])]})
# ---- 72-88: the second song, two sines
S({"name": "signal3", "from": "lock2", "to": "song2", "pal": "neon", "layers": [
  LAMP(0.12), WAVE("wave_t", band("mid", -0.1, 0.34), 0.7), WAVE("wave_m", band("mid", 0.1, -0.34), 0.7),
  JAW(band("bass", 0.02, 0.35, True), c=0.8),
  VU_MID("tubes1", 0.45), VU_HIGH("tubes2", 0.45)]})
S({"name": "signal4", "from": "song2", "to": "song2b", "pal": "neon", "pump": BEAT, "layers": [
  LAMP(0.1), WAVE("wave_t", band("mid", -0.1, 0.34), 0.7), WAVE("wave_m", band("mid", 0.1, -0.34), 0.7),
  JAW(band("bass", 0.05, 0.55, True), c=0.1),
  VU_MID("tubes1"), VU_HIGH("tubes2")]})
S({"name": "signal5", "from": "song2b", "to": "fade2", "like": "signal4"})
S({"name": "interference2", "from": "fade2", "to": "drop2", "like": "interference", "out": 1})
# ---- 92-107: on air, everything
HARD = dict(PUMP, depth=0.28)
sign_scene("ON AIR 2", "drop2", "rings2", pump=HARD)
S({"name": "on air 2", "from": "rings2", "to": "drop2b", "pal": "neon", "pump": HARD, "layers": air(rings2(24, 0.6, per=0.5))})
sign_scene("ON AIR 3", "drop2b", "drop2b+1", pump=HARD)
S({"name": "receive", "from": "drop2b+1", "to": "drop2b+4", "pal": "neon", "pump": HARD, "layers": air(rings2(12, 0.6, inward=True))})
S({"name": "on air 3", "from": "drop2b+4", "to": "fall2", "pal": "neon", "pump": HARD, "layers": air(rings2(12, 0.6, per=0.5), [PEAK(0.4)])})
# ---- 107: the last ladder down
S({"name": "slip2", "from": "fall2", "to": "off", "pal": "neon", "layers": [
  LAMP(0.3), TICKS(0.14), needle(FALL2, 107, 108, 0.9),
  vu("tubes1", band("mid", -0.1, 1.1), 0.5), vu("tubes2", band("high", -0.1, 1.1), 0.5)]})
# ---- 108-112: switched off. The dial lamp cools to a point
S({"name": "off", "from": "off", "to": "end", "pal": "dial", "layers": [
  LAMP({"off": 0.3, "109": 0.24, "110": 0.16, "111": 0.08}, rad=[190, 26], soft=[190, 26], c=[0.8, 0.3]),
  vu("tubes1", band("mid", 0.0, 1.0), 0.3),
  vu("tubes2", band("high", 0.0, 1.0), 0.3)]})

HITF = lambda name, at, beats, layers, pal=None: dict({"name": name, "at": at, "beats": beats, "layers": layers}, **({"pal": pal} if pal else {}))
FLASH = lambda gain=0.6, c=0.0, on="ears": {"fx": "fill", "on": on, "pal": "neon", "c": c, "gain": [gain, 0]}
LOCKFLASH = {"fx": "orb", "on": "face", "x": 0, "y": 53, "rad": 200, "soft": 120, "pal": "dial", "c": 0.95, "gain": [0.7, 0]}
BEACONUP = {"fx": "orb", "on": "shell", "x": 0, "y": 166, "rad": [12, 40], "soft": 14, "pal": "beacon", "c": 0.5, "gain": 0.9}
tr["hits"] = [
  HITF("LOCK", "lock", 3, [LOCKFLASH, FLASH(0.3, c=0.0)]),
  HITF("BEACON", "gap", 1, [BEACONUP]),
  HITF("SLAM", "drop", 2, [FLASH(0.5, c=0.8)]),
  HITF("TITLE", "tail", 16, [{"fx": "preset", "name": "text", "on": "face", "fit": True, "mix": "over", "env": {"in": 1, "out": 2}, "params": {"text": "SOME CHORDS", "color": "dial@0.8"}}]),
  HITF("LOCK 2", "lock2", 3, [LOCKFLASH, FLASH(0.3, c=0.8)]),
  HITF("BEACON 2", "gap2", 1, [BEACONUP]),
  HITF("WHITE", "drop2", 2, [{"fx": "fill", "on": "ears", "pal": "white", "c": 1, "gain": [0.3, 0]}, {"fx": "fill", "on": "shell", "pal": "white", "c": 1, "gain": [0.28, 0]}]),
]
save(tr, os.path.join("shows", "scenes", BASE + ".scene.json"))
'''
about='ABOUT = "(draft)"\n'
open(p,"w").write(head+about+tail)
