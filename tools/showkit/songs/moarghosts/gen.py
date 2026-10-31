#!/usr/bin/env python3
"""Moar Ghosts n Stuff: Pac-Man after dark. Writes the treatment. Run from the repo root."""
import sys, json
KIT = "tools/showkit"
sys.path.insert(0, KIT)
from fmt import save

BASE = "deadmau5 - Moar Ghosts n Stuff"
SPB = 0.46877
BAR = 4 * SPB
F8 = round(2 / SPB, 6)            # one flip-book frame an 8th note
HZ_BAR = round(1 / BAR, 6)        # one cycle a bar, in cycles a second
SMALL = dict(y_lo=48, y_hi=170, x_half=66)
ROW = dict(y_lo=48, y_hi=170, x_half=288.75)
GIANT = dict(y_lo=-108, y_hi=166, x_half=171)
BIGPAC = dict(y_lo=48, y_hi=170, x_half=128)
TEXTBAND = dict(y_lo=50, y_hi=160)
EDGE = 236.0                      # a small ghost is off the dome this far out
GAP = 148.5                       # a ghost and the next, in a train: 9 cells, so one sprite can hold all four pairs of eyes


def names(*frames, times=1):
    return "|".join(["moar_" + f for f in frames] * times)


def sprite(name, color, gain, frame, on="shell", mix="over", gate=None, env=None, rate=F8, **motion):
    p = dict(frame, sprite=name, color=color, rate=rate, **motion)
    L = {"fx": "preset", "name": "sprite", "on": on, "mix": mix, "gain": gain, "params": p}
    if gate:
        L["gate"] = gate
    if env:
        L["env"] = env
    return L


COL = {"red": "ghosts@0", "pink": "ghosts@0.25", "cyan": "ghosts@0.5", "orange": "ghosts@0.75"}
ORDER = ["red", "pink", "cyan", "orange"]
BLUE = [14, 14, 255]
WHITE = [255, 255, 255]
YELLOW = [255, 215, 0]


EYE = 0.8


def train(bars, right, gain=0.66, who=ORDER, bob=8.0):
    """The ghosts one behind the other, crossing the dome once in `bars`, eyes the way they go."""
    T = bars * BAR
    n = len(who)
    travel = 2 * EDGE + (n - 1) * GAP
    v = travel / T
    sign = 1 if right else -1
    look = "gR" if right else "gL"
    out = []
    for i, c in enumerate(who):
        start = -sign * (EDGE + i * GAP)
        out.append(sprite(names(look + "_a", look + "_b"), COL[c], gain, SMALL,
                          dx=start, vx=round(sign * v, 3), wy=bob, wf=round(HZ_BAR, 6)))
    if n == 4:
        out.append(sprite("moar_trainR" if right else "moar_trainL", WHITE, EYE, ROW, rate=0,
                          dx=round(-sign * (EDGE + 1.5 * GAP), 3), vx=round(sign * v, 3), wy=bob, wf=round(HZ_BAR, 6)))
    return out


def maze(gain, gate=None, env=None, color="maze@1"):
    return sprite("moar_maze", color, gain, GIANT, mix="add", gate=gate, env=env, rate=0)


def bars_bg(gain, axis="x", scale=4.0, speed=0.125, pal="wall"):
    return {"fx": "grad", "on": "shell", "axis": axis, "axis2": "y", "scale": scale, "speed": speed,
            "lo": 0, "hi": 1, "pal": pal, "gain": gain}


def row(color, gain, wx=70.0, wf=HZ_BAR, mix="over", gate=None, env=None):
    return sprite(names("row_a", "row_b"), color, gain, ROW, mix=mix, gate=gate, env=env, wx=wx, wf=wf)


def pellet(rad, gain, c=1, gate=None, x=0, y=108):
    L = {"fx": "orb", "on": "shell", "x": x, "y": y, "rad": rad, "soft": 26, "pal": "dots", "c": c, "gain": gain}
    if gate:
        L["gate"] = gate
    return L


def moon(x, y, rad, gain, on="all"):
    return {"fx": "orb", "on": on, "x": x, "y": y, "rad": rad, "soft": rad * 0.45, "pal": "moon", "c": 1,
            "cgrad": -0.25, "gain": gain}


# --- the ears
def rimdots(gain, speed=0.25, frm=1.05, to=-0.05, shape="saw"):
    "Dots round the rims that disappear as the front eats them."
    return {"fx": "sweep", "on": "rims", "axis": "a", "shape": shape, "mode": "fill", "speed": speed,
            "from": frm, "to": to, "soft": 0.04, "pal": "dotring", "c": 0, "cgrad": 1, "gain": gain}


def rimpac(gain, speed=0.25, gate=None):
    L = {"fx": "sweep", "on": "rims", "axis": "a", "shape": "saw", "mode": "band", "speed": speed,
         "from": 1.05, "to": -0.05, "width": 0.09, "pal": "yellow", "c": 1, "gain": gain}
    if gate:
        L["gate"] = gate
    return L


def tubedots(gain, speed=0.25, frm=1.05, to=-0.05, shape="saw"):
    "A corridor of dots up each tube, eaten from the tip down, once a bar."
    return {"fx": "sweep", "on": "tubes", "axis": "al", "shape": shape, "mode": "fill", "speed": speed,
            "from": frm, "to": to, "soft": 0.03, "pal": "dotline", "c": 0, "cgrad": 1, "gain": gain}


def tubepac(gain, speed=0.25, gate=None):
    "Pac-Man himself, the bright front running down the tubes, chewing."
    L = {"fx": "sweep", "on": "tubes", "axis": "al", "shape": "saw", "mode": "band", "speed": speed,
         "from": 1.05, "to": -0.05, "width": 0.1, "pal": "yellow", "c": 1, "gain": gain}
    if gate:
        L["gate"] = gate
    return L


def jawdots(gain, speed=0.25, frm=1.05, to=-0.05, shape="saw"):
    "A row of dots along the chin, eaten across it."
    return {"fx": "sweep", "on": "jaw", "axis": "x", "shape": shape, "mode": "fill", "speed": speed,
            "from": frm, "to": to, "soft": 0.02, "pal": "dotchin", "c": 0, "cgrad": 1, "gain": gain}


def jawpac(gain, speed=0.25, gate=None):
    L = {"fx": "sweep", "on": "jaw", "axis": "x", "shape": "saw", "mode": "band", "speed": speed,
         "from": 1.05, "to": -0.05, "width": 0.07, "pal": "yellow", "c": 1, "gain": gain}
    if gate:
        L["gate"] = gate
    return L


CHEW = {"pat": "x.", "step": 0.5, "decay": 0.4, "floor": 0.45}


def clapcol(bars, pal="ghosts", gain=0.5, rise=0.14, rim=0.0, seq=("012",)):
    "The clap up the tubes, a different ghost's colour every bar."
    a, b = bars
    keys = {str(k): round(((k - a) % 4) * 0.25, 2) for k in range(int(a), int(b) + 1)}
    return {"fx": "blades", "on": "tubes", "seq": list(seq), "step": 1, "rise": rise, "keep": 0, "c": keys,
            "ctip": keys, "pal": pal, "gain": gain, "rim": rim, "gate": {"pat": ".x.x", "step": 1, "decay": 0.75}}


def clap_side(ear, pat, pal="blues", c=0.6, ctip=1, gain=0.6):
    return {"fx": "blades", "on": ear, "side": "ear1" if ear == "ear1" else "ear2", "seq": ["012"], "step": 1,
            "rise": 0.14, "keep": 0, "c": c, "ctip": ctip, "pal": pal, "gain": gain,
            "gate": {"pat": pat, "step": 1, "decay": 0.8}}


def kick(on="rims", pal="blues", c=0.75, gain=0.8):
    return {"fx": "fill", "on": on, "pal": pal, "c": c, "gain": gain, "gate": {"pat": "x", "step": 1, "decay": 0.6}}


def waka(at, to, pal="ghosts", dots=0.6, pacg=0.9, clap=0.5):
    "The ears' whole game: a corridor of dots eaten down the tubes and the clap up them, in a ghost's colour."
    return {"name": "WAKA %g" % at, "at": at, "beats": (to - at) * 4, "layers": [
        tubedots(dots), tubepac(pacg, gate=CHEW), clapcol((at, to), pal=pal, gain=clap)]}


def chin(at, to, dots=0.6, pacg=0.85, extra=None):
    "The same game on the chin, where it can be seen from the front, and round the rims."
    return {"name": "CHIN %g" % at, "at": at, "beats": (to - at) * 4, "layers": [jawdots(dots), jawpac(pacg, gate=CHEW), extra or rimdots(0.8)]}


def hunt(at, to, base=0.2, rim=0.8):
    "Frightened ears: blue tubes, the hunter going round the rims twice as fast."
    return {"name": "HUNT %g" % at, "at": at, "beats": (to - at) * 4, "layers": [
        {"fx": "fill", "on": "tubes", "pal": "blues", "c": 0.4, "gain": base},
        rimdots(0.6, speed=0.5), rimpac(rim, speed=0.5)]}


def flash(at, color="maze@1", beats=2, gain=0.8):
    "The maze flashes, as it does when a level is cleared."
    return {"name": "FLASH %g" % at, "at": at, "beats": beats, "layers": [maze([gain, 0], color=color)]}


def runfill(at, pal="ghosts", c=0.0, gain=0.55):
    "A run up the tubes across the last bar of a phrase, the music's fill."
    return {"name": "RUN %g" % at, "at": at, "beats": 4, "pal": pal, "layers": [
        {"fx": "blades", "on": "tubes", "seq": ["0", "1", "2", "012"], "step": 0.5, "rise": 0.3, "keep": 0.1,
         "c": c, "ctip": 1 if pal != "ghosts" else c, "pal": pal, "gain": gain}]}


PUMP = {"pat": "x...", "step": 0.25, "depth": 0.18, "decay": 0.6}
RIFF = {"pat": "x.....x.x.x...x.", "step": 0.25, "decay": 0.3}


tr = {"v": 1, "show": BASE, "lead": 0, "about": "",
      "marks": {"attract": 0, "drain": 3.5, "dark": 4, "voice": 14, "title": 20, "game": 26, "back": 34, "pellet": 40,
                "drop1": 42, "drop1b": 50, "warn": 56, "recover": 58, "cutscene": 66, "stop": 74, "drop2": 76,
                "flick": 84, "flick2": 88, "flick3": 90, "eaten": 92, "boo": 94, "cyc2": 98, "cyc3": 102, "cyc4": 106,
                "swell": 110, "pellet3": 112, "drop3": 114, "pinky": 118, "inky": 122, "clyde": 126, "stop3": 128,
                "final": 130, "trap": 138, "die": 143, "end": 144},
      "palettes": {
          "ghosts": {"stops": [[255, 0, 0], [255, 60, 180], [0, 220, 255], [255, 110, 0]], "wrap": True},
          "maze": [[0, 0, 0], [6, 6, 70], [24, 24, 230]],
          "wall": [[0, 0, 0], [0, 0, 0], [0, 0, 0], [6, 6, 90], [20, 20, 240]],
          "blues": [[0, 0, 0], [0, 0, 120], [14, 14, 255], [130, 140, 255], [255, 255, 255]],
          "white": [[120, 130, 255], [255, 255, 255]],
          "dots": [[0, 0, 0], [80, 50, 20], [255, 190, 120]],
          "dotring": {"stops": [[0, 0, 0], [255, 180, 110], [0, 0, 0]] * 6, "wrap": True},
          "dotline": {"stops": [[0, 0, 0], [255, 180, 110], [0, 0, 0], [0, 0, 0]] * 5, "wrap": True},
          "dotchin": {"stops": [[0, 0, 0], [255, 180, 110], [0, 0, 0]] * 9, "wrap": True},
          "yellow": [[0, 0, 0], [120, 90, 0], [255, 215, 0]],
          "moon": [[0, 0, 0], [30, 40, 90], [130, 160, 230], [225, 235, 255]],
          "stars": [[0, 0, 0], [20, 30, 80], [120, 140, 220]],
      },
      "motifs": {},
      "scenes": [], "hits": []}
S = tr["scenes"].append
H = tr["hits"].append

# ---------------------------------------------------------------- attract: the first notes, all four, then lights out
S({"name": "attract", "from": "attract", "to": "drain", "pal": "maze", "pump": PUMP, "layers":
   [maze(0.3)] + train(3.5, True)})
H(waka(0, 3.5))
H(flash(0, beats=3))
H(chin(0.75, 3.5))
S({"name": "drain", "from": "drain", "to": "dark", "pal": "maze", "layers": [maze([0.2, 0.02])]})
# ---------------------------------------------------------------- after dark: Clyde alone, and the moon going the other way
S({"name": "afterdark", "from": "dark", "to": "voice", "pal": "maze", "layers": [
    maze([0.04, 0.08]),
    moon([340, -340], 128, 62, 0.5),
    sprite(names("gR_a", "gR_b"), COL["orange"], [0.4, 0.5], SMALL, rate=F8 / 2, dx=-240, vx=round(480 / (10 * BAR), 3), wy=6, wf=round(HZ_BAR / 2, 6)),
    sprite("moar_ewR", WHITE, [0.5, 0.7], SMALL, rate=0, dx=-240, vx=round(480 / (10 * BAR), 3), wy=6, wf=round(HZ_BAR / 2, 6)),
    rimdots(0.22, shape="p", frm=1.05, to=1.05),
    {"fx": "twinkle", "on": "tubes", "rate": 0.125, "sharp": 6, "dens": 0.5, "pal": "stars", "c": 1, "gain": 0.5, "seed": 5}]})
# ---------------------------------------------------------------- the voice: the helmet itself wakes up as a ghost
LOOK = names("G_R_a", "G_R_b", times=4) + "|" + names("G_L_a", "G_L_b", times=4)
LOOKW = names("Gw_R", times=8) + "|" + names("Gw_L", times=8)
S({"name": "voice", "from": "voice", "to": "title", "pal": "maze", "layers": [
    sprite(LOOK, COL["orange"], {"band": "mid", "lo": -0.2, "hi": 0.3}, GIANT, env={"in": 6}),
    sprite(LOOKW, WHITE, {"band": "mid", "lo": -0.6, "hi": 0.7}, GIANT, env={"in": 4}),
    {"fx": "sweep", "on": "tubes", "axis": "al", "shape": "p", "mode": "fill", "soft": 0.2,
     "from": {"band": "mid", "lo": -1.5, "hi": 1.0}, "to": {"band": "mid", "lo": -1.5, "hi": 1.0}, "pal": "ghosts", "c": 0.75, "gain": 0.35},
    rimdots(0.3, shape="p", frm=1.05, to=1.05)]})
# ---------------------------------------------------------------- the title, chased; the dots laid out for the game
TEXT = "MOAR GHOSTS"
tw = 6 * len(TEXT)
TBEATS = 20
TSPAN = TBEATS * SPB
CELL = 16.7
tspeed = (tw * CELL + 2 * 171) / TSPAN
S({"name": "banner", "from": "title", "to": "game", "pal": "maze", "out": 0.5, "layers": [
    maze([0.04, 0.16]),
    sprite(names("gL_a", "gL_b"), COL["orange"], 0.55, SMALL, dx=round(171 - 90, 1), vx=round(-tspeed, 3)),
    sprite(names("pacL_o", "pacL_h", "pacL_c", "pacL_h"), YELLOW, 0.6, SMALL, dx=round(171 + tw * CELL + 90, 1), vx=round(-tspeed, 3)),
    rimdots(0.6, shape="p", frm=-0.05, to=1.05),
    tubedots(0.35, shape="p", frm=-0.05, to=1.05),
    jawdots(0.5, shape="p", frm=-0.05, to=1.05)]})
H({"name": "TITLE", "at": "title", "beats": TBEATS, "layers": [
    {"fx": "preset", "name": "text", "on": "face", "fit": True, "mix": "over", "params": dict(TEXTBAND, text=TEXT, color="dots@1"), "gain": 0.62}]})
# ---------------------------------------------------------------- the game: four ghosts, one way and back
S({"name": "game", "from": "game", "to": "back", "pal": "maze", "pump": PUMP, "layers": [maze(0.28)] + train(8, True)})
S({"name": "gameback", "from": "back", "to": "pellet", "pal": "maze", "pump": PUMP, "layers": [maze(0.28)] + train(6, False)})
H(waka(26, 40))
H(flash(26))
H(chin(26.5, 34))
H(flash(34, beats=1, gain=0.5))
H(chin(34.25, 40))
# ---------------------------------------------------------------- the pellet swells, the kick is gone
def pellet_scene(name, frm, to, r0=12, r1=64, m=0.1, watch=0.0):
    L = [maze([m, 0.02]),
         pellet([r0, r1], [0.4, 0.8], gate={"pat": "x.", "step": 0.5, "decay": 0.5, "floor": 0.4}),
         {"fx": "sweep", "on": "tubes", "axis": "al", "shape": "p", "mode": "fill", "from": -0.1, "to": 1.05, "soft": 0.2, "pal": "dots", "c": 1, "gain": [0.1, 0.4]},
         rimdots(0.5, shape="p", frm=1.05, to=1.05)]
    if watch:
        L.append(sprite("moar_watch", WHITE, watch, dict(y_lo=48, y_hi=170, x_half=140), rate=0))
    return {"name": name, "from": frm, "to": to, "pal": "maze", "out": 1, "layers": L}
S(pellet_scene("pellet", "pellet", "drop1"))
def noise_hit(at):
    return {"name": "NOISE %g" % at, "at": at, "beats": 1, "layers": [
        {"fx": "twinkle", "on": "ears", "rate": 4, "sharp": 3, "dens": 0.9, "pal": "dots", "c": 1, "gain": 0.8}]}
def power_hit(name, at, white=False):
    pal = "white" if white else "blues"
    c = 1 if white else 0.72
    return {"name": name, "at": at, "beats": 3, "pal": pal, "layers": [
        {"fx": "orb", "on": "all", "x": 0, "y": 108, "rad": [40, 620], "soft": 160, "pal": pal, "c": c, "gain": [0.75 if white else 0.7, 0]},
        {"fx": "fill", "on": "ears", "pal": pal, "c": c, "gain": [0.45 if white else 0.6, 0]}]}
H(noise_hit(13.75))
H(noise_hit(41.75))
H(power_hit("POWER", "drop1"))
# ---------------------------------------------------------------- frightened: blue, hunting side to side
def jawrun(gain, speed=0.25):
    "Blue running along the jaw, against the ghosts."
    return {"fx": "grad", "on": "jaw", "axis": "x", "axis2": "y", "scale": 3.0, "speed": speed, "lo": 0, "hi": 1, "pal": "wall", "gain": gain}


def rowface(gain, wx=70.0, wf=HZ_BAR, **kw):
    return sprite(names("rowface_a", "rowface_b"), "dots@1", gain, ROW, wx=wx, wf=wf, **kw)


def fright(name, frm, to, gain=0.9, wx=70.0, jaw=0.9, white=None, flick=RIFF, face=0.7):
    L = [jawrun(jaw), row(BLUE, gain, wx=wx), rowface(face, wx=wx)]
    if white:
        L.append(row(WHITE, white, wx=wx, gate=flick, mix="add"))
    L += [clap_side("ear2", ".x.."), clap_side("ear1", "...x")]
    return {"name": name, "from": frm, "to": to, "pal": "blues", "pump": PUMP, "layers": L}
S(fright("fright", "drop1", "drop1b", white={"drop1": 0.5, "44": 0.0, "49": 0.35}))
S(fright("fright b", "drop1b", "warn", wx=110, white={"drop1b": 0.3, "52": 0}))
S(fright("warning", "warn", "recover", wx=110, white=0.75, flick={"pat": "x.", "step": 0.5, "decay": 0.3}))
H(hunt(42, 58))
H(runfill(49, pal="blues", c=0.6))
# ---------------------------------------------------------------- they recover: the chase is on, him in front
V = round((2 * EDGE + 4 * GAP) / (8 * BAR), 3)
S({"name": "recover", "from": "recover", "to": "cutscene", "pal": "maze", "pump": PUMP, "layers": [
    maze(0.26),
    sprite(names("pacL_o", "pacL_h", "pacL_c", "pacL_h"), YELLOW, 0.66, SMALL, dx=EDGE, vx=-V)] +
   [sprite(names("gL_a", "gL_b"), COL[c], 0.66, SMALL, dx=EDGE + (i + 1) * GAP, vx=-V) for i, c in enumerate(ORDER)]})
H(waka(58, 66))
H(flash(58))
# the eyes of all four, one sprite, whose clock starts with this hit: half a bar later than the ghosts'
EYES58 = sprite("moar_trainL", WHITE, EYE, ROW, rate=0, dx=round(EDGE + GAP + 1.5 * GAP - V * 2 * SPB, 3), vx=-V)
H(chin(58.5, 66, extra=EYES58))
# ---------------------------------------------------------------- the intermission: him big, chasing all four blue the other way
VB = round((915 + 297) / (8 * BAR), 3)
S({"name": "intermission", "from": "cutscene", "to": "stop", "pal": "maze", "pump": PUMP, "layers": [
    jawrun(0.9, speed=-0.25),
    sprite(names("row_a", "row_b"), BLUE, 0.9, ROW, dx=-369, vx=VB),
    sprite(names("rowface_a", "rowface_b"), "dots@1", 0.7, ROW, dx=-369, vx=VB),
    sprite(names("bpR_o", "bpR_h", "bpR_c", "bpR_h"), YELLOW, 0.5, BIGPAC, dx=-915, vx=VB),
    kick(pal="yellow", c=1, gain=0.8),
    clapcol((66, 74), pal="yellowclap", gain=0.5)]})
H(runfill(73, pal="yellow", c=0.6))
# ---------------------------------------------------------------- stop: the pads alone, eyes watching the next pellet
S(pellet_scene("stop", "stop", "drop2", r0=14, r1=70, m=0.08, watch=0.34))
H(noise_hit(75.75))
H(power_hit("POWER 2", "drop2"))
# ---------------------------------------------------------------- the helmet is the frightened ghost
GF = names("F_a", "F_b")
GFF = names("Fface_a", "Fface_b")
def bigf(name, frm, to, white=0, flick=None):
    L = [sprite(GF, BLUE, 0.7, GIANT)]
    if white:
        L.append(sprite(GF, WHITE, white, GIANT, mix="add", gate=flick))
    L += [sprite(GFF, "dots@1", 0.8, GIANT, wx=44, wf=HZ_BAR), clap_side("ear2", ".x.."), clap_side("ear1", "...x")]
    return {"name": name, "from": frm, "to": to, "pal": "blues", "pump": PUMP, "layers": L}
S(bigf("bigfright", "drop2", "flick"))
S(bigf("bigflick", "flick", "flick2", white=0.3, flick={"pat": "x...............", "step": 0.5, "decay": 1.5}))
S(bigf("bigflick2", "flick2", "flick3", white=0.3, flick={"pat": "x...", "step": 0.5, "decay": 1}))
S(bigf("bigflick3", "flick3", "eaten", white=0.34, flick={"pat": "x.", "step": 0.5, "decay": 0.4}))
H(hunt(76, 92))
H(runfill(83, pal="blues", c=0.6))
H(runfill(91, pal="blues", c=0.6))
# ---------------------------------------------------------------- eaten: only the eyes left, going home on the noise
S({"name": "eaten", "from": "eaten", "to": "boo", "pal": "maze", "layers": [
    sprite(names("eL"), WHITE, [0.85, 0.15], SMALL, dx=130, vx=round(-200 / (2 * BAR), 3), rate=0)]})
# ---------------------------------------------------------------- BOO, then the long dark
H({"name": "BOO", "at": "boo", "beats": 6, "pal": "white", "layers": [
    sprite(names("G_F_a", "G_F_b"), COL["red"], [0.4, 0.0], GIANT),
    sprite("moar_boo", WHITE, 0.8, dict(y_lo=50, y_hi=160, x_half=128), rate=0, env={"out": 2}),
    {"fx": "fill", "on": "ears", "pal": "ghosts", "c": 0, "gain": [0.6, 0]}]})
def lone(name, frm, to, g, mz, right, bars, mx0, mx1, mg, y=128, rad=66):
    look = "gR" if right else "gL"
    s = 1 if right else -1
    return {"name": name, "from": frm, "to": to, "pal": "maze", "layers": [
        maze(mz), moon([mx0, mx1], y, rad, mg),
        sprite(names(look + "_a", look + "_b"), COL["red"], g, SMALL, rate=F8 / 2, dx=-s * 240, vx=round(s * 480 / (bars * BAR), 3), wy=6, wf=round(HZ_BAR / 2, 6)),
        sprite("moar_ewR" if right else "moar_ewL", WHITE, 0.7, SMALL, rate=0, dx=-s * 240, vx=round(s * 480 / (bars * BAR), 3), wy=6, wf=round(HZ_BAR / 2, 6)),
        rimdots({"band": "high", "lo": 0.06, "hi": 1.1}, shape="p", frm=1.05, to=1.05),
        {"fx": "sweep", "on": "tubes", "axis": "al", "shape": "p", "mode": "fill", "soft": 0.2,
         "from": {"band": "mid", "lo": -0.07, "hi": 1.27}, "to": {"band": "mid", "lo": -0.07, "hi": 1.27}, "pal": "maze", "c": 0.8, "gain": 0.4}]}
S(lone("lone", "boo", "cyc2", [0.0, 0.5], 0.03, True, 4, -340, -210, 0.42))
S(lone("lone2", "cyc2", "cyc3", 0.5, 0.05, False, 4, -210, -80, 0.46))
S(lone("lone3", "cyc3", "cyc4", 0.54, [0.05, 0.1], True, 4, -80, 50, 0.5))
VU = {"fx": "sweep", "on": "tubes", "axis": "al", "shape": "p", "mode": "fill", "soft": 0.2,
      "from": {"band": "mid", "lo": -0.07, "hi": 1.27}, "to": {"band": "mid", "lo": -0.07, "hi": 1.27}, "pal": "maze", "c": 0.8, "gain": 0.4}
L4 = lone("lone4", "cyc4", "swell", 0.58, [0.1, 0.16], False, 4, 50, 180, 0.5)
rim106 = L4["layers"].pop(4)
L4["layers"].insert(3, sprite(names("gL_a", "gL_b"), COL["pink"], 0.5, SMALL, rate=F8 / 2, dx=240 + GAP, vx=round(-(480 + GAP) / (4 * BAR), 3), wy=6, wf=round(HZ_BAR / 2, 6)))
S(L4)
H({"name": "RIMS 106", "at": "cyc4", "beats": 16, "layers": [rim106]})
S({"name": "swell", "from": "swell", "to": "pellet3", "pal": "maze", "layers": [maze([0.16, 0.26])] + train(2, True, gain=0.6, bob=0)})
H({"name": "SWELL", "at": "swell", "beats": 8, "layers": [
    VU,
    rimdots({"band": "high", "lo": 0.06, "hi": 1.1}, shape="p", frm=1.05, to=1.05),
    {"fx": "twinkle", "on": "tubes", "rate": 2, "sharp": 4, "dens": 0.6, "pal": "dots", "c": 1, "gain": [0.0, 0.5]}]})
S(pellet_scene("pellet3", "pellet3", "drop3", r0=14, r1=72, m=0.18, watch=0.34))
H(noise_hit(113.75))
H(power_hit("POWER 3", "drop3"))
# ---------------------------------------------------------------- close-ups: each ghost the whole helmet in turn
def close(name, frm, to, col, ear_c):
    return {"name": name, "from": frm, "to": to, "pal": "ghosts", "pump": PUMP, "layers": [
        sprite(LOOK, COL[col], 0.26, GIANT), sprite(LOOKW, WHITE, 0.75, GIANT),
        rimdots(0.8), tubedots(0.55), tubepac(0.9, gate=CHEW),
        {"fx": "blades", "on": "tubes", "seq": ["012"], "step": 1, "rise": 0.14, "keep": 0, "c": ear_c, "ctip": ear_c, "pal": "ghosts", "gain": 0.55, "gate": {"pat": ".x.x", "step": 1, "decay": 0.75}}]}
def stare(name, frm, to, col, ear_c, out=0.5):
    return {"name": name, "from": frm, "to": to, "pal": "ghosts", "pump": PUMP, "out": out, "layers": [
        sprite(names("G_F_a", "G_F_b"), COL[col], 0.36, GIANT), sprite("moar_Gw_F", WHITE, 0.85, GIANT, rate=0),
        {"fx": "fill", "on": "tubes", "pal": "ghosts", "c": ear_c, "gain": [0.22, 0.4]},
        {"fx": "fill", "on": "rims", "pal": "ghosts", "c": ear_c, "gain": 0.9, "gate": {"pat": "x", "step": 1, "decay": 0.6}}]}
S(close("blinky", "drop3", "116", "red", 0))
S(stare("blinky stare", "116", "pinky", "red", 0))
S(close("pinky", "pinky", "120", "pink", 0.25))
S(stare("pinky stare", "120", "inky", "pink", 0.25))
S(close("inky", "inky", "124", "cyan", 0.5))
S(stare("inky stare", "124", "clyde", "cyan", 0.5))
S(close("clyde", "clyde", "stop3", "orange", 0.75))
for at, c in (("pinky", 0.25), ("inky", 0.5), ("clyde", 0.75)):
    H({"name": "NEXT " + at, "at": at, "beats": 2, "layers": [
        {"fx": "fill", "on": "ears", "pal": "ghosts", "c": c, "gain": [0.5, 0]},
        {"fx": "orb", "on": "shell", "x": 0, "y": 108, "rad": [40, 400], "soft": 120, "pal": "ghosts", "c": c, "gain": [0.4, 0]}]})
S(pellet_scene("stop3", "stop3", "final", r0=14, r1=76, m=0.12, watch=0.34))
H(noise_hit(129.75))
H(power_hit("WHITE", "final", white=True))
# ---------------------------------------------------------------- everything, blue
def held(name, frm, to, out=0.5):
    L = fright(name, frm, to, wx=0, white=0.4, flick={"pat": "x", "step": 1, "decay": 0.7}, gain=1.0)
    L["out"] = out
    return L
S(fright("final", "final", "132", wx=120, white={"final": 0.55, "131": 0.3}, gain=1.0))
S(held("final chord", "132", "134"))
S(fright("final b", "134", "136", wx=120, white=0.3, gain=1.0))
S(held("final chord 2", "136", "trap"))
H(hunt(130, 132, rim=1.0))
H(hunt(132, 134, base=0.45, rim=1.0))
H(hunt(134, 136, rim=1.0))
H(hunt(136, 138, base=0.45, rim=1.0))
H(runfill(135, pal="blues", c=0.6))
# ---------------------------------------------------------------- the trap: him in the middle, two from each side, closing
CHOMP = names("pacR_o", "pacR_c", "pacL_o", "pacL_c", "pacL_o", "pacL_c", "pacR_o", "pacR_c")
T5 = 5 * BAR
def closing(c, x0, x1, look):
    return sprite(names(look + "_a", look + "_b"), COL[c], 0.7, SMALL, dx=x0, vx=round((x1 - x0) / T5, 3), wy=8, wf=HZ_BAR)
S({"name": "trap", "from": "trap", "to": "die", "pal": "maze", "pump": PUMP, "layers": [
    maze(0.26),
    closing("orange", 440, 165, "gL"), closing("pink", -440, -165, "gR"),
    closing("cyan", 300, 96, "gL"), closing("red", -300, -96, "gR"),
    sprite(CHOMP, YELLOW, 0.75, SMALL, wx=34, wf=HZ_BAR)]})
H(waka(138, 140))
H(flash(138))
H(chin(138.5, 143))
H({"name": "CLOSING", "at": 140, "beats": 7.5, "layers": [
    {"fx": "fill", "on": "tube0", "pal": "ghosts", "c": 0, "gain": [0.2, 0.5]},
    {"fx": "fill", "on": "tube1", "pal": "ghosts", "c": 0.25, "gain": [0.2, 0.5]},
    {"fx": "fill", "on": "tube2", "pal": "ghosts", "c": 0.5, "gain": [0.2, 0.5]}]})
H(waka(142, 143))
# ---------------------------------------------------------------- caught: his death takes the whole helmet, and the track cuts
S({"name": "die", "from": "die", "to": "end", "pal": "yellow", "layers": [
    sprite(names(*["die%d" % i for i in range(8)]), YELLOW, 0.6, GIANT),
    {"fx": "fill", "on": "ears", "pal": "yellow", "c": 1, "gain": [0.5, 0.0]}]})

tr["palettes"]["yellowclap"] = {"stops": [[255, 215, 0], [255, 215, 0]], "wrap": True}

tr["about"] = ("Bars of a measured grid, shows/scenes/deadmau5 - Moar Ghosts n Stuff.beats: bar b starts at 0.045 + 1.875 b seconds (127.995 BPM), 144 bars, "
    "flat to a millisecond wherever there are drums, with the kick on every beat, the clap on 2 and 4, the riff on x.....x.x.x...x. and every section turning on the bar line; the noise burst before each drop sits on the last beat of the bar before it, and the file stops dead at bar 144. "
    "Pac-Man after dark, a game told in rounds. The first notes are all four ghosts crossing the dome in their own colours, red, pink, cyan, orange, wavy skirts and eyes looking the way they go, over a maze drawn to fit the LEDs. Then the filter shuts and the lights go out: Clyde alone, walking one way while the moon goes the other. "
    "When the voice comes in the helmet itself wakes up as a giant ghost whose eyes look side to side and whose body and ears breathe with the singing. The title crosses once, a ghost running ahead of it and Pac-Man chewing behind it, while the dots get laid out up the ears and along the chin. "
    "When the drums land the game is on: the train of four drifts one way and back; dots are eaten round the rims, down each ear tube and across the chin, once a bar, by a yellow front that chews on the 8ths; the clap goes up the tubes in a different ghost's colour every bar. "
    "Before each drop the kick falls away and one power pellet swells and blinks on the forehead; a beat of dark on the noise burst; and on the bass everything goes frightened blue with a blast out from the pellet. "
    "The first time, a row of blue ghosts with squiggle mouths hunts side to side, the ears answering right and left on the claps and the ghosts flickering white on the riff, until they flash white on the warning and recover. They chase him off the left of the dome, and then, as in the old intermission, he comes back big and chases all four of them blue the other way. "
    "The second time the helmet is the frightened ghost, its face hunting side to side across it, flashing faster and faster until at the hard stop it is eaten: nothing left but its eyes going home on the dying noise. Then the sub drops and it comes back red with one BOO, the only word in the show that is not the title. "
    "The long breakdown is a dark maze, a lone red ghost pacing back and forth and the moon crossing from ear to ear, with the ears filling only as the track's own filter opens; a second ghost joins at bar 106 and all four at 110. "
    "The third drop gives each ghost its close-up, the whole helmet in its colour: on the two bars of riff its eyes go side to side and the dots get eaten, on the two bars of held chord it stares straight at you and the tubes hold, and the half beat of nothing before the riff comes back is black. "
    "White once, on the last pellet; the blue hunts on the riff and holds on the chord. And at the end the ghosts finally get him: he is trapped in the middle of the dome with two closing from each side, and on the last bar his death takes the whole helmet, a wedge opening from the top until nothing is left, exactly as the track cuts off.")
save(tr, "shows/scenes/%s.scene.json" % BASE)
