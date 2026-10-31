#!/usr/bin/env python3
"""ON THE RADIO: the treatment for deadmau5 - Some Chords (Radio Edit), written by hand in bars."""
import json, os, sys
KIT = os.environ.get("KIT") or "tools/showkit"
sys.path.insert(0, KIT)
from fmt import save

BASE = "deadmau5 - Some Chords (Radio Edit)"

# ---- the sprites -----------------------------------------------------------
SPRITES = {
 "radioedit_on": [
  "..XXXXX..XX...XX.",
  ".XX...XX.XXX..XX.",
  "XX.....X.XXXX.XX.",
  "XX.....X.XX.XXXX.",
  "XX.....X.XX..XXX.",
  ".XX...XX.XX...XX.",
  "..XXXXX..XX...XX."],
 "radioedit_air": [
  "...XX....XX.XXXX.",
  "..XXXX...XX.XX.XX",
  "..XX.XX..XX.XX.XX",
  ".XX..XX..XX.XXXX.",
  ".XXXXXX..XX.XX.XX",
  ".XX..XX..XX.XX.XX",
  ".XX..XX..XX.XX.XX"],
}
with open(os.path.join("shows", "scenes", BASE + ".sprites.json"), "w") as f:
    f.write("{\n" + ",\n".join(' %s: [\n  %s\n ]' % (json.dumps(k), ",\n  ".join(json.dumps(r) for r in v)) for k, v in SPRITES.items()) + "\n}\n")

SIGN = {"y_lo": 30, "y_hi": 166, "x_half": 165}
FLIP2 = 1 / (2 * 0.46875)          # one flip of the sign every 2 beats at 128 BPM
KICK = "x...x...x...o..."          # the drop's groove: three big kicks and a lighter fourth beat

# ---- the helpers -----------------------------------------------------------
def band(b, lo, hi, punch=False):
    return {"band": b, "lo": lo, "hi": hi, "punch": punch}

def vu(on, v, gain, soft=0.1, c=0.0, cgrad=1.0, pal="vu"):
    """An ear as a meter: the tube fills from the head outward, colder at the bottom, hot at the tip."""
    return {"fx": "sweep", "on": on, "axis": "al", "shape": "p", "mode": "fill", "soft": soft,
            "from": v, "to": v, "pal": pal, "c": c, "cgrad": cgrad, "gain": gain}

RINGGATE = {"pat": KICK, "step": 0.25, "decay": 0.9, "floor": 0.5}
def rings(beats, gain, pal="rings_t", per=1, cg=6.0, rad=440, soft=260, on="shell+rims", inward=False, x=0, y=170, gate=True):
    """Broadcast rings from the top of the head: one leaves on each `per` beats of this scene.
    The palette has the wave's sharp front at c=0.5 and its tail behind it, toward the mast."""
    n = beats / float(per)
    c0 = 0.5
    L = {"fx": "orb", "on": on, "x": x, "y": y, "rad": rad, "soft": soft, "pal": pal,
         "c": [c0, c0 + n] if inward else [c0, c0 - n], "cgrad": cg, "gain": gain}
    if gate:
        L["gate"] = RINGGATE
    return L

def rings2(beats, gain, per=1, cg=6.0, rad=440, soft=260, on="shell+rims", inward=False, x=0, y=170, gate=True):
    pal = "rings_in" if inward else "rings_tm"
    """The same, teal and magenta in turn: the palette holds two rings, so one cycle is 2 x per beats."""
    n = beats / (2.0 * per)
    c0 = 0.25
    L = {"fx": "orb", "on": on, "x": x, "y": y, "rad": rad, "soft": soft, "pal": pal,
         "c": [c0, c0 + n] if inward else [c0, c0 - n], "cgrad": cg / 2.0, "gain": gain}
    if gate:
        L["gate"] = RINGGATE
    return L

def needle_keys(path, b0, b1):
    """A needle along a path of (bar, angle): one straight piece a beat, as from/to keys. Scene starts at b0."""
    def at(b):
        for (a0, v0), (a1, v1) in zip(path, path[1:]):
            if a0 <= b <= a1:
                return v0 + (v1 - v0) * (b - a0) / max(a1 - a0, 1e-9)
        return path[-1][1] if b > path[-1][0] else path[0][1]
    n = int(round((b1 - b0) * 8))
    fr, to = {}, {}
    for k in range(n):
        bb = b0 + k / 8.0
        fr[str(bb)] = round(at(bb), 4)
        to[str(bb)] = round(at(bb + 0.125), 4)
    return fr, to, at

def needle(path, b0, b1, gain, width=0.03, c=0.95):
    fr, to, _ = needle_keys(path, b0, b1)
    return {"fx": "sweep", "on": "face", "axis": "a", "shape": "saw", "speed": 2, "mode": "band", "width": width,
            "from": fr, "to": to, "pal": "dial", "c": c, "gain": gain}

def static_keys(path, b0, b1, level):
    """Static is loudest away from the station: it dips each time the needle crosses the middle."""
    _, _, at = needle_keys(path, b0, b1)
    n = int(round((b1 - b0) * 8))
    keys = {}
    for k in range(n):
        bb = b0 + k / 8.0
        d = min(abs(at(bb + 0.0625) - 0.25) / 0.16, 1.0)
        keys[str(bb)] = round(level(bb) * (0.3 + 0.7 * d), 3)
    return keys

LAMP = lambda gain, rad=190, soft=190, c=0.8: {"fx": "orb", "on": "face", "x": 0, "y": 53, "rad": rad, "soft": soft, "pal": "dial", "c": c, "cgrad": -0.45, "gain": gain}
TICKS = lambda gain, scale=16: {"fx": "grad", "on": "face", "axis": "a", "axis2": "r", "scale": scale, "ofs": 0.0, "pal": "tick", "gain": gain}
DIAL = lambda gain, scale=16: {"fx": "grad", "on": "face", "axis": "a", "axis2": "r", "scale": scale, "pal": "dialface", "gain": gain}
STATIC = lambda gain, on="all", rate=7: {"fx": "twinkle", "on": on, "rate": rate, "sharp": 5, "dens": 0.75, "pal": "static", "c": 0.0, "spread": 1.0, "seed": 4.0, "gain": gain}
WAVE = lambda pal, warp, gain, wspeed=0.25, wscale=2, ofs=0.0: {"fx": "grad", "on": "face", "axis": "y", "axis2": "x", "scale": 2, "ofs": ofs, "warp": warp, "wscale": wscale, "wspeed": wspeed, "pal": pal, "gain": gain}
JAW = lambda gain, pal="neon", c=0.0, scale=9: {"fx": "grad", "on": "jaw", "axis": "x", "axis2": "y", "scale": scale, "pal": pal, "c": c, "gain": gain}
PEAK = lambda gain, c=0.75, pat=KICK: {"fx": "fill", "on": "rims", "pal": "neon", "c": c, "gain": gain, "gate": {"pat": pat, "step": 0.25, "decay": 0.6}}
BEACON = lambda gain=0.9, pat="x.......", decay=1.2, floor=0.2: {"fx": "orb", "on": "shell", "mix": "over", "x": 0, "y": 166, "rad": 24, "soft": 12, "pal": "beacon", "c": 0.5, "gain": gain, "gate": {"pat": pat, "step": 0.25, "decay": decay, "floor": floor}}
MAST = lambda gain=0.9: {"fx": "sweep", "on": "face", "axis": "x", "shape": "p", "mode": "band", "width": 0.06, "from": 0.5, "to": 0.5, "pal": "dial", "c": 0.95, "gain": gain}
NEEDLE_VU = lambda lo, hi, b="high", gain=0.9, punch=False: {"fx": "sweep", "on": "face", "axis": "a", "shape": "p", "mode": "band", "width": 0.03, "from": band(b, lo, hi, punch), "to": band(b, lo, hi, punch), "pal": "dial", "c": 0.95, "gain": gain}

# The ears: in the song they read the chords and the hats; in the drop the left reads the kick and the right the chords pumping between the kicks.
EARG = 0.28
VU_KICK = lambda on, gain=0.3: vu(on, band("bass", 0.02, 1.15, True), gain)
VU_PUMP = lambda on, gain=EARG: vu(on, band("mid", -0.3, 1.1), gain)
VU_MID = lambda on, gain=EARG, lo=-2.0, hi=1.1: vu(on, band("mid", lo, hi), gain)
VU_HIGH = lambda on, gain=EARG, lo=-1.6, hi=1.6: vu(on, band("high", lo, hi), gain)

# ---- the shell's budget
# The guard caps the shell near 300 mA, so a shell asked for far more than that is thrown away and costs the
# whole song's budget. Each scene's shell layers (and the rings, which go out through shell and rims) are scaled
# so the shell asks for about what the guard would send, measured per scene before the guard. The ears and the
# hits are left as written.
SHELL_ON = {"shell", "face", "jaw", "left", "right", "shell+rims"}
def scaled(v, k):
    if isinstance(v, (int, float)):
        return round(v * k, 4)
    if isinstance(v, list):
        return [scaled(x, k) for x in v]
    if isinstance(v, dict) and "band" in v:
        return dict(v, lo=scaled(v.get("lo", 0.0), k), hi=scaled(v.get("hi", 1.0), k))
    if isinstance(v, dict):
        return {b: scaled(x, k) for b, x in v.items()}
    return v
def fit_shell(scenes, ks):
    for sc in scenes:
        k = ks.get(sc["name"])
        if k is None or "layers" not in sc:
            continue
        sc["layers"] = [dict(L) for L in sc["layers"]]
        for L in sc["layers"]:
            if (L.get("on") or "shell") in SHELL_ON:
                L["gain"] = scaled(L.get("gain", 1.0), k)

# ---- the path of the needle ------------------------------------------------
# Angles on the half-moon dial: 0.03 far right, 0.25 straight up (the station), 0.47 far left.
HUNT1 = [(-0.125, 0.44), (0.875, 0.44), (1.25, 0.10), (1.875, 0.10), (2.25, 0.36), (2.875, 0.36), (3.25, 0.06), (3.875, 0.06),
         (4.25, 0.32), (4.875, 0.32), (5.25, 0.14), (5.875, 0.14), (6.25, 0.30), (6.875, 0.30), (7.25, 0.20), (7.625, 0.20), (7.875, 0.27), (8.0, 0.25)]
HUNT2 = [(64.0, 0.08), (64.875, 0.08), (65.25, 0.42), (65.875, 0.42), (66.25, 0.16), (66.875, 0.16), (67.25, 0.38),
         (67.875, 0.38), (68.25, 0.12), (68.875, 0.12), (69.25, 0.33), (69.875, 0.33), (70.25, 0.18), (70.875, 0.18), (71.25, 0.29), (71.625, 0.29), (71.875, 0.23), (72.0, 0.25)]
DRIFT1 = [(24.0, 0.25), (25.0, 0.25), (25.5, 0.20), (26.0, 0.20), (26.5, 0.30), (27.0, 0.30), (27.5, 0.13), (28.0, 0.13)]
DRIFT2 = [(88.0, 0.25), (89.0, 0.25), (89.5, 0.31), (90.0, 0.31), (90.5, 0.18), (91.0, 0.18), (91.5, 0.38), (92.0, 0.38)]
FALL1 = [(59.0, 0.25), (59.5, 0.25), (59.75, 0.33), (60.0, 0.40), (61.0, 0.47)]
FALL2 = [(107.0, 0.25), (107.25, 0.25), (107.25, 0.31), (107.5, 0.31), (107.5, 0.37), (107.75, 0.37), (107.75, 0.43), (108.0, 0.43)]

def ringpal(rgb):
    """One ring in a cycle of 8 stops: a soft tail, then the bright front at c=0.5, then nothing."""
    r = [int(x) for x in rgb]
    sc = lambda k: [int(x * k) for x in r]
    return {"stops": [[0, 0, 0], [0, 0, 0], sc(0.06), sc(0.3), r, [0, 0, 0], [0, 0, 0], [0, 0, 0]], "wrap": True}
def ringpal_in(rgb):
    """The same ring coming home: bright edge inside, the tail behind it toward the outside."""
    r = [int(x) for x in rgb]
    sc = lambda k: [int(x * k) for x in r]
    return {"stops": [[0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], r, sc(0.3), sc(0.06), [0, 0, 0]], "wrap": True}
TEAL, MAG = [0, 255, 130], [255, 0, 110]

ABOUT = ("Bars of a measured grid, shows/scenes/deadmau5 - Some Chords (Radio Edit).beats: bar b starts at 0.124 + 1.875 b seconds (exactly 128 BPM), 112 bars, "
 "and at bar 72 the radio edit is spliced, so the music comes back 32 ms late and the grid holds still for it. The bar line is where the phrases turn, with the drop's first kick on step 0 of bar 28. "
 "An old radio being tuned at night. The dome is the half-moon dial of a tube set, amber backlight and radial ticks, pivoting at the bottom of the forehead; the jaw is its speaker; the ears are its VU meters. "
 "Bars 0 to 8 are the filter opening on the bass chords, so the show is static over everything with the needle hunting the dial, moving on each chord change, the static thinning each time it crosses the station, the meters climbing by themselves because the track's own mid and high bands are rising. "
 "At bar 8 it locks: the static is gone in one frame and the needle now reads the level. At 16 the kick lands and the signal itself appears, a teal sine across the dome whose height is the track's mid band. "
 "At 24 the drums pull out, so the sine flattens, the needle drifts off the station and static creeps back, one dark beat under the noise burst at 27.75 with only a red beacon lit on top of the head, then ON and AIR flip in magenta, two beats each, as a sign rather than a lyric. "
 "The drop is the transmitter: the needle stands up as the mast, the beacon blinks and a ring leaves on every beat, through the dome and down to the jaw, teal, then teal and magenta in turn; "
 "the left ear plays the kick and the right ear plays the chords pumping up between kicks. At 45 the transmitters move into the ears and their rings cross on the dome; at 53 the whole radio runs at once, the kick throwing the needle. "
 "The fill at 59 lets the needle slip off the station, the sound dies, and the title crosses once in amber as the sign-off while the static comes back. At 64 the chords return and it tunes again, a different path, this time with the sine glimmering through whenever the needle crosses the station, "
 "until the edit's hard cut at 72 locks it: two sines now, teal and magenta, braided. The second drop opens with the rims white, the one white moment, the rings go at double speed, come home inward at 101 and go out again at 104. "
 "At 107 the kick stops and the needle walks down the falling notes, and from 108 the set is switched off: the meters fall with the tail and the dial lamp cools to a point and goes out. Tuned through the real guard: shell inside its 300 mA, ears kept under what would make the governor shed the shell.")
tr = {"v": 1, "show": BASE,
"about": ABOUT,
"lead": 0,
"marks": {"tune": 0, "lock": 8, "drums": 12, "song": 16, "songb": 20, "fade": 24, "gap": 27.75, "drop": 28, "rings": 30, "dropb": 36, "dropc": 44, "dropd": 52,
          "fall": 59, "tail": 60, "retune": 64, "lock2": 72, "song2": 76, "song2b": 84, "fade2": 88, "gap2": 91.75, "drop2": 92, "rings2": 94, "drop2b": 100, "fall2": 107, "off": 108, "end": 112},
"palettes": {
 "dial": [[0, 0, 0], [70, 14, 0], [210, 62, 2], [255, 96, 6], [255, 170, 60]],
 "tick": [[0, 0, 0], [0, 0, 0], [255, 90, 8]],
 "dialface": [[60, 13, 0], [60, 13, 0], [255, 90, 8]],
 "static": [[80, 95, 130], [190, 200, 225], [255, 190, 120]],
 "vu": [[0, 200, 150], [0, 225, 90], [255, 130, 0], [255, 10, 30], [255, 0, 110]],
 "neon": [[0, 255, 130], [0, 150, 255], [110, 40, 255], [255, 0, 110], [255, 20, 70]],
 "wave_t": [[0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 50, 26], [0, 255, 130]],
 "wave_m": [[0, 0, 0], [0, 0, 0], [0, 0, 0], [60, 0, 26], [255, 0, 110]],
 "rings_t": ringpal(TEAL),
 "rings_m": ringpal(MAG),
 "rings_a": ringpal([255, 70, 0]),
 "rings_tm": {"stops": ringpal(TEAL)["stops"] + ringpal(MAG)["stops"], "wrap": True},
 "rings_in": {"stops": ringpal_in(TEAL)["stops"] + ringpal_in(MAG)["stops"], "wrap": True},
 "beacon": [[255, 0, 40], [255, 0, 60], [255, 60, 100]],
 "sign": [[255, 0, 40], [255, 0, 50], [255, 30, 80]],
 "white": [[255, 200, 120], [255, 240, 220], [255, 255, 255]]},
"motifs": {},
"scenes": [], "hits": []}
S = tr["scenes"].append
PUMP = {"pat": KICK, "step": 0.25, "depth": 0.22, "decay": 0.5}
BEAT = {"pat": "x...", "step": 0.25, "depth": 0.14, "decay": 0.5}

# ---- 0-8: tuning. Static over everything, the needle hunting across the dial, the meters climb as the filter opens
LEVEL1 = lambda b: 0.34 - 0.012 * max(b, 0)
EARSTATIC1 = lambda b: 0.52 - 0.03 * max(b, 0)
S({"name": "tuning", "from": -0.125, "to": "lock", "pal": "dial", "layers": [
  STATIC(static_keys(HUNT1, -0.125, 8, LEVEL1), on="shell"),
  STATIC(scaled(static_keys(HUNT1, -0.125, 8, EARSTATIC1), 0.7), on="ears"),
  DIAL([0.12, 0.3]),
  needle(HUNT1, -0.125, 8, 0.9),
  vu("tubes1", band("mid", -0.05, 0.95), [0.14, 0.26]),
  vu("tubes2", band("high", -0.05, 1.7), [0.14, 0.26])]})
# ---- 8-16: locked on. The static is gone, the dial is lit, the needle now reads the level
S({"name": "locked", "from": "lock", "to": "drums", "pal": "dial", "layers": [
  LAMP(0.2), TICKS(0.16), NEEDLE_VU(0.61, 0.01),
  JAW(band("bass", 0.0, 0.3, True), pal="dial", c=0.8),
  VU_MID("tubes1", lo=-2.0, hi=1.1), VU_HIGH("tubes2", lo=-0.9, hi=2.1)]})
S({"name": "drums", "from": "drums", "to": "song", "pal": "dial", "pump": BEAT, "layers": [
  LAMP([0.2, 0.25]), TICKS([0.16, 0.2]), NEEDLE_VU(0.61, 0.01),
  JAW(band("bass", 0.05, 0.6, True), pal="dial", c=0.9),
  VU_MID("tubes1", lo=-2.0, hi=1.1), VU_HIGH("tubes2", lo=-1.2, hi=1.8)]})
# ---- 16-24: the song. The signal itself: a neon sine across the dial, the speaker on the jaw
WARP = band("mid", 0.02, 0.32)
S({"name": "signal", "from": "song", "to": "songb", "pal": "neon", "pump": BEAT, "layers": [
  LAMP(0.07), WAVE("wave_t", WARP, 0.7),
  JAW(band("bass", 0.05, 0.55, True), c=0.1),
  VU_MID("tubes1"), VU_HIGH("tubes2"),
  PEAK(0.3, c=0.8, pat="x...")]})
S({"name": "signal2", "from": "songb", "to": "fade", "like": "signal", "patch": {"1": {"wspeed": 0.5, "wscale": 3}}})
# ---- 24-28: interference. The drums are gone, the sine flattens, the static creeps back
S({"name": "interference", "from": "fade", "to": "drop", "pal": "neon", "out": 1, "layers": [
  STATIC([0.0, 0.4]),
  LAMP([0.07, 0.02]),
  WAVE("wave_t", [0.3, 0.0], [0.6, 0.2], wspeed=0.25),
  dict(needle(DRIFT1, 24, 28, 0.75), env={"in": 4}),
  vu("tubes1", band("mid", -1.6, 1.0), [0.26, 0.09]),
  vu("tubes2", band("high", -1.0, 1.5), [0.26, 0.09])]})
# ---- 28-60: on air. The sign, then the needle stands up as the mast, the beacon blinks, rings go out on every beat
SIGNL = lambda rate=FLIP2, gain=0.62, c=0.5: {"fx": "preset", "name": "sprite", "on": "shell", "mix": "over", "params": dict(SIGN, sprite="radioedit_on|radioedit_air", rate=rate, color="sign@%g" % c), "gain": gain}
def sign_scene(name, a, b, pump=PUMP, gain=0.62, kick=0.3, chords=EARG):
    S({"name": name, "from": a, "to": b, "pal": "neon", "pump": pump, "layers": [SIGNL(gain=gain), VU_KICK("tubes1", kick), VU_PUMP("tubes2", chords), PEAK(0.5)]})
def air(ring, extra=()):
    return (ring if isinstance(ring, list) else [ring]) + [MAST(), BEACON(), VU_KICK("tubes1"), VU_PUMP("tubes2")] + list(extra)
def radio(ring):
    """The whole radio at once: the dial behind the rings, the needle thrown by every kick."""
    return [ring, LAMP(0.06), NEEDLE_VU(0.27, 0.03, "bass", 0.9, True), BEACON(), VU_KICK("tubes1"), VU_PUMP("tubes2")]
sign_scene("ON AIR", "drop", "rings", kick=0.28, chords=0.24)
S({"name": "on air", "from": "rings", "to": "dropb", "pal": "neon", "pump": PUMP, "layers": air(rings(24, 0.62))})
sign_scene("ON AIR b", "dropb", "dropb+1")
S({"name": "on air b", "from": "dropb+1", "to": "dropc", "pal": "neon", "pump": PUMP, "layers": air(rings2(28, 0.62), [PEAK(0.3)])})
sign_scene("ON AIR c", "dropc", "dropc+1")
# two transmitters, one in each ear, the rings crossing on the dome
TXL = rings(28, 0.34, per=1, x=-232, y=232, rad=470, soft=240, on="all", cg=6.0, pal="rings_t")
TXR = rings(28, 0.34, per=1, x=232, y=232, rad=470, soft=240, on="all", cg=6.0, pal="rings_m")
S({"name": "stereo", "from": "dropc+1", "to": "dropd", "pal": "neon", "pump": PUMP, "layers": [TXL, TXR, BEACON(), VU_KICK("tubes1", 0.26), VU_PUMP("tubes2", 0.22)]})
sign_scene("ON AIR d", "dropd", "dropd+1")
S({"name": "the radio", "from": "dropd+1", "to": "fall", "pal": "neon", "pump": PUMP, "layers": radio(rings2(24, 0.62))})
# ---- 59: the fill, the needle starts to slip off the station
S({"name": "slip", "from": "fall", "to": "tail", "pal": "neon", "layers": [
  LAMP([0.25, 0.16]), TICKS(0.12), needle(FALL1, 59, 60, 0.9),
  vu("tubes1", band("mid", -1.0, 1.0), 0.24), vu("tubes2", band("high", -1.0, 1.1), 0.24),
  PEAK(0.6, c=0.8, pat="x...x..x...x....")]})
# ---- 60-64: sign-off. The sound dies, the title crosses once, the static comes back up under it
S({"name": "sign-off", "from": "tail", "to": "retune", "pal": "dial", "layers": [
  LAMP([0.09, 0.02]),
  STATIC([0.0, 0.16], rate=5),
  vu("tubes1", band("mid", 0.0, 1.0), 0.28),
  vu("tubes2", band("high", 0.0, 1.0), 0.28)]})
# ---- 64-72: tuning again
LEVEL2 = lambda b: 0.36 - 0.015 * (b - 64)
def glimmer(path, b0, b1, start):
    _, _, at = needle_keys(path, b0, b1)
    n = int(round((b1 - b0) * 8))
    keys = {}
    for k in range(n):
        bb = b0 + k / 8.0
        keys[str(bb)] = round(0.6 * max(0.0, 1 - abs(at(bb + 0.0625) - 0.25) / 0.09), 3) if bb >= start else 0.0
    return keys
S({"name": "retune", "from": "retune", "to": "lock2", "pal": "dial", "layers": [
  STATIC(static_keys(HUNT2, 64, 72, LEVEL2)),
  DIAL([0.12, 0.3]),
  needle(HUNT2, 64, 72, 0.9),
  WAVE("wave_t", band("mid", 0.02, 0.3), glimmer(HUNT2, 64, 72, 66)),
  vu("tubes1", band("mid", -0.05, 0.95), [0.14, 0.26]),
  vu("tubes2", band("high", -0.05, 1.7), [0.14, 0.26])]})
# ---- 72-88: the second song, two sines
WT = WAVE("wave_t", band("mid", -0.1, 0.34), 0.7)
WM = WAVE("wave_m", band("mid", 0.1, -0.34), 0.7)
S({"name": "two signals", "from": "lock2", "to": "song2", "pal": "neon", "layers": [
  LAMP(0.09), WT, WM,
  JAW(band("bass", 0.02, 0.35, True), c=0.8),
  VU_MID("tubes1", lo=-4.5, hi=1.1), VU_HIGH("tubes2", lo=-1.2, hi=2.2)]})
S({"name": "two signals b", "from": "song2", "to": "song2b", "pal": "neon", "pump": BEAT, "layers": [
  LAMP(0.07), WT, WM,
  JAW(band("bass", 0.05, 0.55, True), c=0.1),
  VU_MID("tubes1", lo=-3.0, hi=1.1), VU_HIGH("tubes2")]})
S({"name": "two signals c", "from": "song2b", "to": "fade2", "like": "two signals b", "patch": {"1": {"wspeed": 0.5, "wscale": 3}, "2": {"wspeed": 0.5, "wscale": 3}}})
S({"name": "interference2", "from": "fade2", "to": "drop2", "like": "interference", "out": 1, "patch": {"3": dict(needle(DRIFT2, 88, 92, 0.75), env={"in": 4})}})
# ---- 92-107: on air, everything
HARD = dict(PUMP, depth=0.28)
sign_scene("ON AIR 2", "drop2", "rings2", pump=HARD, kick=0.26, chords=0.22)
S({"name": "on air 2", "from": "rings2", "to": "drop2b", "pal": "neon", "pump": HARD, "layers": air(rings2(24, 0.62, per=0.5))})
sign_scene("ON AIR 3", "drop2b", "drop2b+1", pump=HARD, kick=0.28, chords=0.24)
S({"name": "receive", "from": "drop2b+1", "to": "drop2b+4", "pal": "neon", "pump": HARD, "layers": air(rings2(12, 0.62, inward=True))})
S({"name": "the radio 2", "from": "drop2b+4", "to": "fall2", "pal": "neon", "pump": HARD, "layers": radio(rings2(12, 0.62, per=0.5))})
# ---- 107: the last ladder down
S({"name": "slip2", "from": "fall2", "to": "off", "pal": "neon", "layers": [
  LAMP(0.25), TICKS(0.14), needle(FALL2, 107, 108, 0.9),
  vu("tubes1", band("mid", -1.0, 1.0), 0.24), vu("tubes2", band("high", -1.0, 1.1), 0.24)]})
# ---- 108-112: switched off. The dial lamp cools to a point
S({"name": "off", "from": "off", "to": "end", "pal": "dial", "layers": [
  LAMP({"off": 0.25, "109": 0.2, "110": 0.14, "111": 0.07}, rad=[190, 26], soft=[190, 26], c=[0.8, 0.3]),
  vu("tubes1", band("mid", 0.0, 1.0), 0.24),
  vu("tubes2", band("high", 0.0, 1.0), 0.24)]})

HITF = lambda name, at, beats, layers, pal=None: dict({"name": name, "at": at, "beats": beats, "layers": layers}, **({"pal": pal} if pal else {}))
RIMFLASH = lambda gain=0.8, c=0.8: {"fx": "fill", "on": "rims", "pal": "neon", "c": c, "gain": [gain, 0]}
LOCKFLASH = {"fx": "orb", "on": "face", "x": 0, "y": 53, "rad": 200, "soft": 120, "pal": "dial", "c": 0.75, "gain": [0.45, 0]}
BEACONUP = {"fx": "orb", "on": "shell", "x": 0, "y": 166, "rad": [12, 40], "soft": 14, "pal": "beacon", "c": 0.5, "gain": 0.9}
WHITERIM = {"fx": "fill", "on": "rims", "pal": "white", "c": 1, "gain": [0.8, 0]}
tr["hits"] = [
  HITF("LOCK", "lock", 3, [LOCKFLASH, RIMFLASH(0.7, c=0.0)]),
  HITF("SONG", "song", 2, [RIMFLASH(0.5, c=0.0)]),
  HITF("BEACON", "gap", 1, [BEACONUP]),
  HITF("SLAM", "drop", 2, [RIMFLASH(0.9, c=0.8)]),
  HITF("TITLE", "tail", 16, [{"fx": "preset", "name": "text", "on": "face", "fit": True, "mix": "over", "env": {"in": 1, "out": 2}, "params": {"text": "SOME CHORDS", "color": [255, 50, 0]}}]),
  HITF("LOCK 2", "lock2", 3, [LOCKFLASH, RIMFLASH(0.7, c=0.8)]),
  HITF("SONG 2", "song2", 2, [RIMFLASH(0.5, c=0.8)]),
  HITF("BEACON 2", "gap2", 1, [BEACONUP]),
  HITF("WHITE", "drop2", 2, [WHITERIM]),
]
SHELL_ASK = 6.0
SHELL_IN = {"tuning": 15.4, "locked": 15.6, "drums": 16.1, "signal": 18.6, "interference": 14.8, "ON AIR": 25.4, "on air": 11.8,
            "ON AIR b": 25.5, "on air b": 11.6, "ON AIR c": 25.5, "stereo": 10.0, "ON AIR d": 25.5, "the radio": 12.5, "slip": 11.0,
            "sign-off": 21.2, "retune": 17.9, "two signals": 31.1, "two signals b": 30.2, "ON AIR 2": 25.6, "on air 2": 11.6,
            "ON AIR 3": 25.6, "receive": 11.9, "the radio 2": 12.6, "slip2": 13.3}
fit_shell(tr["scenes"], {n: min(1.0, SHELL_ASK / v) for n, v in SHELL_IN.items()})
save(tr, os.path.join("shows", "scenes", BASE + ".scene.json"))
