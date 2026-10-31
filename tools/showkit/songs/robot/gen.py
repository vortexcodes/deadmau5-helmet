#!/usr/bin/env python3
"""THE ROBOT: the treatment for deadmau5's live Harder Better Faster Stronger."""
import json, os, sys
KIT = "tools/showkit"
sys.path.insert(0, KIT)
from fmt import save
BASE = "deadmau5 - Harder Better Faster Stronger"
SPB = 0.468761
RED, GREEN, BLUE, WHITE = [255, 0, 0], [0, 255, 0], [0, 70, 255], [255, 255, 255]
INK = [5, 0, 0]            # near black: a stencil, painted over, hides what is under it
DOME = {"y_lo": 55, "y_hi": 172, "x_half": 171}
LOW2 = {"y_lo": 55, "y_hi": 81, "x_half": 171}
LOW1 = {"y_lo": 55, "y_hi": 68, "x_half": 171}
KICK = "x...x...x...x..."
RIFF = "x.o.x..xx.o.o...x.x.x...x..o..o."
CLAP = "....x..........."
HATS = "..x...x...x...x."
WORDS = (("HARDER", RED), ("BETTER", GREEN), ("FASTER", BLUE), ("STRONGER", WHITE))

def frames(prefix, n, width=2):
    return "|".join(("robot_%s%0" + str(width) + "d") % (prefix, i) for i in range(n))
def spr(name, color, gain=1.0, mix="over", grid=None, rate=None, **extra):
    p = dict(grid or DOME); p.update(sprite=name, color=color)
    if rate:
        p["rate"] = round(rate, 6)
    L = {"fx": "preset", "name": "sprite", "on": "shell", "mix": mix, "gain": gain, "params": p}
    L.update(extra)
    return L
def eye(cycle, gain=0.9, rows=2, color=RED):
    """The visor's eye: there and back every `cycle` beats, on the bottom rows of the dome."""
    return spr(frames("e", 32), color, gain, "over", LOW2 if rows == 2 else LOW1, 32 / (cycle * SPB))
def line(gain=0.14, rows=2, color=RED):
    return spr("robot_line", color, gain, "max", LOW2 if rows == 2 else LOW1)
def stack(gain=0.2, pal="tiers", **extra):
    L = {"fx": "grad", "on": "face", "axis": "y", "wave": "saw", "scale": 0.999, "pal": pal, "gain": gain}
    L.update(extra)
    return L
def stencil(name="robot_st_pyr", rate=None):
    return spr(name, INK, 0.82, "over", None, rate)
GROW = "robot_st_v|robot_st_t3|robot_st_t2|robot_st_pyr"
def fill(on, pal, gain, pat=None, step=0.25, decay=0.5, floor=0.0, **extra):
    L = {"fx": "fill", "on": on, "pal": pal, "c": 1, "gain": gain}
    if pat:
        L["gate"] = {"pat": pat, "step": step, "decay": decay, "floor": floor}
    L.update(extra)
    return L
def rise(on, pal, gain, shape="p", speed=0.25, frm=-0.1, to=1.05, soft=0.15, **extra):
    L = {"fx": "sweep", "on": on, "axis": "al", "shape": shape, "speed": speed, "mode": "fill", "from": frm, "to": to, "soft": soft, "pal": pal, "c": 1, "gain": gain}
    L.update(extra)
    return L
def vbox(pal="red", lo=0.14, hi=0.5, gain=0.8, band="mid", punch=False):
    """The jaw is a voice box: a bar from the chin outward, as wide as the voice is loud."""
    return {"fx": "sweep", "on": "jaw", "axis": "x", "shape": "p", "mode": "band", "from": 0.495, "to": 0.495,
            "width": {"band": band, "lo": lo, "hi": hi, "punch": punch}, "pal": pal, "c": 1, "gain": gain}
LOCK = {"fx": "grad", "on": "tubes", "axis": "u", "wave": "saw", "scale": 0.999, "pal": "ubars"}
def lock(gain):
    return dict(LOCK, gain=gain)
def word(text, at, beats, color, extra=None):
    g = 0.7 if color is WHITE else 1.0
    L = [{"fx": "preset", "name": "text", "on": "face", "fit": True, "mix": "over", "gain": g,
          "params": {"text": text, "color": color, "y_lo": 68, "y_hi": 159}}]
    return {"name": text, "at": at, "beats": beats, "layers": L + (extra or [])}
def wipe(name, at, pal="white", beats=2, c=1, gain=0.8):
    return {"name": name, "at": at, "beats": beats, "layers": [
        {"fx": "sweep", "on": "shell", "axis": "x", "shape": "p", "mode": "band", "width": 0.14, "from": 0.1, "to": 0.9, "pal": pal, "c": c, "gain": gain},
        {"fx": "fill", "on": "ears", "pal": pal, "c": c, "gain": [0.3, 0]}]}
def flash(name, at, beats=2):
    """A drop: the pyramid and the visor burn out white and red, the ears with them, on the first kick."""
    return {"name": name, "at": at, "beats": beats, "layers": [
        spr("robot_pyr", WHITE, [0.85, 0]), spr("robot_visor", RED, [1, 0]), {"fx": "fill", "on": "ears", "pal": "white", "c": 1, "gain": [0.3, 0]}]}
def fall(name, at, beats=1):
    """The voice's falling fill before each phrase: one white line, top of the dome to the visor."""
    return {"name": name, "at": at, "beats": beats, "layers": [
        {"fx": "sweep", "on": "face", "axis": "y", "shape": "p", "mode": "band", "width": 0.05, "from": 0.95, "to": 0.5, "pal": "white", "c": 1, "gain": 0.7}]}
def kitlayers(tube0=0.45, tube1=0.4, tube2=0.35):
    """The ears as a drum machine: rims the kick (in the scene), tube 0 the riff, tube 1 the clap, tube 2 the hats."""
    L = []
    if tube0: L.append(fill("tube0", "red", tube0, RIFF, decay=0.4))
    if tube1: L.append(fill("tube1", "green", tube1, CLAP, decay=0.7))
    if tube2: L.append(fill("tube2", "blue", tube2, HATS, decay=0.35))
    return L
def kit(name, at, bars, **kw):
    return {"name": name, "at": at, "beats": bars * 4, "layers": kitlayers(**kw)}
RIM = fill("rims", "white", 0.5, KICK, decay=0.6)
def stepkeys(lo, hi, step_beats, inc, offset=0.0):
    keys = {}; v = 0.0; b = lo * 4 + offset
    keys["%.4f" % lo] = 0.0
    while b < hi * 4 - 1e-9:
        keys["%.4f" % (b / 4)] = round(v, 5); v += inc; b += step_beats
    return keys

# tier colours by the dome's y axis: red up to row 7, green rows 6-5, blue rows 4-3, white rows 2-0
tiers = []
for i in range(41):
    c = i / 40
    tiers.append([110, 0, 0] if c <= 0.5751 else GREEN if c <= 0.6751 else BLUE if c <= 0.7751 else WHITE)
ubars = []
for i in range(51):
    c = i / 50
    ubars.append(BLUE if c <= 0.281 else GREEN if c <= 0.681 else RED)
K = [0, 0, 0]
tr = {"v": 1, "show": BASE, "lead": 0,
 "about": "Bars of a measured grid, shows/scenes/deadmau5 - Harder Better Faster Stronger.beats: bar b starts at 0.003 + 1.875 b seconds (127.997 BPM), flat to 3 ms from end to end though it is a live rip, 160 bars. The bar line is where the phrases turn: the drop's first kick is bar 12, the blocks run 16 bars from there, and the same falling fill leads into each of them. A helmet about helmets: a robot boots. Bars 0 to 8, the voice alone, and the title crosses the face one word at a time, each word its own primary, the way an LED panel tests itself: HARDER red, BETTER green, FASTER blue, STRONGER all three at once. Each word locks one tier of a pyramid on the dome, like Daft Punk's Alive tour, and one part of the ear: lowest tube, middle tube, top tube, rim. The red tier is the visor, a line along the eye-line with a scanner running in it. The jaw is a voice box, a bar from the chin outward as wide as the voice is loud. Bars 8 to 12 the bass arrives in dotted 8ths, the ears and the stack take that rhythm, and a beat of dark and one falling white line hand over to the kick. Everything then is the machine running: hard edges, no warp, no sparks, every change on the grid. The ears are a drum machine, rims the kick, tube 0 the riff, tube 1 the clap, tube 2 the hats from bar 20, when the pyramid also cuts into LED tiles that step sideways. At 28 the voice returns: the stack rises in two bars, the word crosses in the next two where the words are sung, and the white line falls with the voice at the end of each phrase. The siren on top turns the rims. The breakdown at 44 is the title again, four bars a word, alone on a dark helmet with the eye crawling, the bass charging the tubes from 52. The pump at 60 is a test card: colour bars jumping one place on each kick, the ears firing in turn; at 68 they jump on the dotted 8th stab instead, against the kick. At 76 the words come back and accelerate, two bars each, one bar, two beats, until at 90 the stack is rising every half a beat. Bar 92 is white, once, the whole helmet, all four words added together, and it splits: the first time this show has used any colour but the primaries. A rainbow equaliser, drawn from the song's own spectrum 16th by 16th, bass in the middle in red and treble at the edges in violet, with white peak caps, and the tubes as meters for bass, mid and high. The show keeps speeding up: the scanner goes round in 16 beats at the start, then 8, 4, 2, 1. From 108 the pyramid stacks in rainbow with the words a bar each. At 124 the voice has gone and only the machine is left, so it looks at you: two block eyes with red pupils stepping on the beat, then at 132 the bare LED panel, a lattice with a line scanning it. 140 is the equaliser again with the colours rolling and the last words on top. At 156 it shuts down in reverse order, apex, blue, green, and the eye is last to go out. The stencils are near-black sprites painted over a gradient, so the colour shows only through the gaps. Nothing on the shell gates faster than 8th notes, and white over the whole helmet happens once.",
 "marks": {"h": 0, "b": 2, "f": 4, "s": 6, "test": 8, "on": 12, "hats": 20, "stop": 27, "voice": 28, "voice2": 36, "down": 44, "d2": 48, "d3": 52, "d4": 56,
           "pump": 60, "dot": 68, "talk": 76, "t2": 84, "t3": 88, "t4": 90, "peak": 92, "stack": 108, "bare": 124, "bare2": 132, "final": 140, "off": 156, "o2": 157, "o3": 158, "o4": 159, "end": 160},
 "palettes": {
  "red": [K, RED], "green": [K, GREEN], "blue": [K, BLUE], "white": [K, WHITE],
  "tiers": tiers, "ubars": ubars,
  "bars": {"stops": [RED, RED, RED, K, GREEN, GREEN, GREEN, K, BLUE, BLUE, BLUE, K, WHITE, WHITE, WHITE, K], "wrap": True},
  "rainbow": [[170, 0, 255], [0, 60, 255], [0, 220, 220], [0, 255, 0], [255, 200, 0], [255, 90, 0], [255, 0, 0]],
 },
 "motifs": {},
 "scenes": [], "hits": []}
S = tr["scenes"].append
H = tr["hits"].append
PK = {"pat": KICK, "step": 0.25, "depth": 0.25, "decay": 0.6}
# ---------- boot: the word is sung, its tier and its part of the ear lock on
V1 = [line(0.1, 1), eye(16, 0.7, 1)]
T3, T2, T1 = spr("robot_t3", GREEN, 0.1, "max"), spr("robot_t2", BLUE, 0.16, "max"), spr("robot_t1", WHITE, 0.08, "max")
TALK = {"band": "mid", "lo": 0.03, "hi": 0.22}
S({"name": "boot H", "from": "h", "to": "b", "pal": "red", "layers": V1 + [rise("tube0", "red", 0.4)]})
S({"name": "boot B", "from": "b", "to": "f", "pal": "red", "layers": [T3] + V1 + [fill("tube0", "red", TALK), rise("tube1", "green", 0.4)]})
S({"name": "boot F", "from": "f", "to": "s", "pal": "red", "layers": [T3, T2] + V1 + [dict(LOCK, on="tube0+tube1", gain=TALK), rise("tube2", "blue", 0.5)]})
S({"name": "boot S", "from": "s", "to": "test", "pal": "red", "layers": [T3, T2, T1] + V1 + [lock(TALK)]})
H(word("HARDER", "h", 8, RED, [vbox("red")])); H(word("BETTER", "b", 8, GREEN, [vbox("green")])); H(word("FASTER", "f", 8, BLUE, [vbox("blue")]))
H(word("STRONGER", "s", 8, WHITE, [vbox("white", gain=0.5), {"fx": "sweep", "on": "rims", "axis": "al", "shape": "p", "mode": "fill", "from": -0.1, "to": 1.05, "soft": 0.2, "pal": "white", "c": 1, "gain": 0.4}]))
# ---------- the test: bass arrives in dotted 8ths, the stack stands up beat by beat
TGATE = {"pat": "x..", "step": 0.25, "decay": 0.6, "floor": 0.25}
S({"name": "test", "from": "test", "to": 10, "pal": "red", "layers": [
    stack([0.14, 0.26]), stencil(GROW, 1 / SPB), eye(8), dict(LOCK, gain=[0.3, 0.5], gate=TGATE), fill("rims", "white", [0.1, 0.4], "x", step=1, decay=0.8), vbox("red", band="bass", punch=True)]})
S({"name": "test2", "from": 10, "to": "on", "pal": "red", "out": 1, "layers": [
    stack([0.26, 0.42]), stencil(GROW, 2 / SPB), eye(4), dict(LOCK, gain=[0.35, 0.5], gate=TGATE), fill("rims", "white", [0.4, 0.6], "x", step=0.5, decay=0.45), vbox("red", band="bass", punch=True)]})
H(fall("fall 1", 11.75))
# ---------- on
SG = {"pat": "x", "step": 1, "decay": 0.9, "floor": 0.55}
ON = [stack(0.5, gate=SG), stencil(), eye(4), RIM, vbox("red", band="bass", punch=True, lo=0.1, hi=0.5)]
S({"name": "on", "from": "on", "to": "hats", "pal": "red", "pump": PK, "layers": ON})
H(flash("ON", "on")); H(kit("kit on", 12.5, 7.5, tube2=0))
S({"name": "hats", "from": "hats", "to": "voice", "pal": "red", "out": 2, "pump": PK, "layers": [
    stack(0.5, gate=SG), stencil(frames("st_tile", 4, 1), 1 / SPB), eye(4), RIM, vbox("red", band="bass", punch=True, lo=0.1, hi=0.5)]})
H(flash("HATS", "hats", 1)); H(kit("kit hats", 20.25, 7.25))
H(fall("fall 2", 27.5, 2))
# ---------- the voice comes back: the stack rises in two bars, the word crosses in the next two, when it is really sung
VOICE = "|".join(["robot_st_v", "robot_st_t3", "robot_st_t2", "robot_st_pyr"] + ["robot_st_v"] * 4)
def siren(keys, gain=0.9):
    return {"fx": "sweep", "on": "rims", "axis": "a", "shape": "saw", "speed": 1, "mode": "band", "width": 0.3, "from": -0.15, "to": 1.15, "pal": "white", "c": 1, "gain": keys}
S({"name": "voice", "from": "voice", "to": "voice2", "pal": "red", "pump": PK, "layers": [stack(0.42), stencil(VOICE, 0.5 / SPB), eye(2), RIM, vbox("red", band="mid", lo=0.1, hi=0.5), siren({"28": 0, "34.25": 0.9, "35.25": 0, "35.5": 0.9})]})
VOICE2 = "|".join(["robot_st_v", "robot_st_t3", "robot_st_t2", "robot_st_pyr"] * 2 + ["robot_st_v"] * 8)
S({"name": "voice2", "from": "voice2", "to": "down", "pal": "red", "pump": PK, "layers": [stack(0.46), stencil(VOICE2, 1 / SPB), eye(1), RIM, vbox("red", band="mid", lo=0.1, hi=0.5), siren({"36": 0.9, "36.75": 0})]})
H(flash("VOICE", "voice")); H(kit("kit voice", 28.5, 15.25, tube1=0))
for i, (b0, w) in enumerate(zip((30, 34, 38, 42), WORDS)):
    H(word(w[0], b0, 7, w[1])); H(fall("fall v%d" % i, b0 + 1.75))
# the siren: the rims turn
H({"name": "siren", "at": 34.25, "beats": 10, "layers": [{"fx": "sweep", "on": "rims", "axis": "a", "shape": "saw", "speed": 1, "mode": "band", "width": 0.3, "from": 0, "to": 1, "pal": "white", "c": 1, "gain": 0.9}]}) if 0 else None
# ---------- breakdown: the words, slow and alone, the tiers lock on again
SLOW = "robot_st_v|robot_st_t3|robot_st_t2|robot_st_pyr"
S({"name": "down", "from": "down", "to": "d3", "pal": "red", "layers": [stack(0.09), stencil(SLOW, 1 / (16 * SPB)), eye(32, 0.6, 1), lock({"band": "mid", "lo": 0, "hi": 0.14}), siren({"44": 0, "45.125": 0.7, "45.875": 0, "46": 0.7, "47.875": 0})]})
S({"name": "charge", "from": "d3", "to": "pump", "pal": "red", "out": 0.5, "layers": [stack(0.1), stencil("robot_st_t2|robot_st_pyr", 1 / (16 * SPB)), eye(16, 0.7, 1), lock({"band": "bass", "lo": 0, "hi": 0.2}), rise("tube0+tube1+tube2", "white", [0.04, 0.3]), fill("rims", "white", [0.05, 0.4], "x", step=1, decay=0.8)]})
H(word("HARDER", "down", 16, RED)); H(word("BETTER", "d2", 16, GREEN)); H(word("FASTER", "d3", 16, BLUE)); H(word("STRONGER", "d4", 16, WHITE))
H({"name": "JAW", "at": "d3", "beats": 32, "layers": [vbox("red", band="bass", lo=0.1, hi=0.5, gain=0.6)]})
H({"name": "PUMP ON", "at": "pump", "beats": 2, "layers": [{"fx": "fill", "on": "ears", "pal": "white", "c": 1, "gain": [0.3, 0]}]})
# ---------- the pump: colour bars, stepping on the kick
BARS = {"fx": "grad", "on": "face", "axis": "x", "wave": "saw", "scale": 1.47, "pal": "bars", "gain": 0.3}
PUMP = {"pat": "x...", "step": 0.25, "depth": 0.4, "decay": 0.6}
S({"name": "pump", "from": "pump", "to": "dot", "pal": "red", "pump": PUMP, "layers": [
    dict(BARS, ofs=stepkeys(60, 68, 1, 0.25)), stencil("robot_st_top"), line(0.12), eye(2), fill("tube0", "red", 0.5, "x...", step=1, decay=0.8), fill("tube1", "green", 0.5, ".x..", step=1, decay=0.8)]})
H({"name": "PUMP", "at": "pump", "beats": 32, "layers": [fill("rims", "white", 0.5, "...x", step=1, decay=0.8), fill("tube2", "blue", 0.6, "..x.", step=1, decay=0.8), vbox("red", band="bass", punch=True, lo=0.1, hi=0.45)]})
S({"name": "dot", "from": "dot", "to": "talk", "pal": "red", "out": 1, "pump": PUMP, "layers": [
    dict(BARS, ofs=stepkeys(68, 76, 0.75, 0.25, offset=0.25), gate={"pat": ".x.", "step": 0.25, "decay": 0.7, "floor": 0.4}, gain=0.36), stencil("robot_st_top"), line(0.12), eye(1), fill("tube0", "red", 0.5, "x...", step=1, decay=0.8), fill("tube1", "green", 0.5, ".x..", step=1, decay=0.8)]})
H({"name": "DOT", "at": "dot", "beats": 32, "layers": [fill("rims", "white", 0.5, "...x", step=1, decay=0.8), fill("tube2", "blue", 0.7, ".x.", step=0.25, decay=0.5), vbox("blue", band="high", punch=True, lo=0.1, hi=0.45)]})
H(fall("fall 3", 75.75))
# ---------- talking: the words again, faster and faster until they are a blur
S({"name": "talk", "from": "talk", "to": "t2", "pal": "red", "layers": [stack(0.1), stencil(GROW, 1 / (8 * SPB)), eye(8, 0.7, 1), lock({"band": "mid", "lo": 0.02, "hi": 0.3}), vbox("red", gain=0.6)]})
S({"name": "talk2", "from": "t2", "to": "t3", "pal": "red", "layers": [stack(0.12), stencil(GROW, 1 / (4 * SPB)), eye(4, 0.7, 1), lock({"band": "mid", "lo": 0.05, "hi": 0.4}), vbox("red", gain=0.6)]})
S({"name": "talk3", "from": "t3", "to": "t4", "pal": "red", "layers": [stack(0.14), stencil(GROW, 1 / (2 * SPB)), eye(2, 0.8, 1), lock([0.2, 0.35]), vbox("red", gain=0.6), fill("rims", "white", [0.2, 0.5], "x", step=0.5, decay=0.45)]})
S({"name": "talk4", "from": "t4", "to": "peak", "pal": "red", "out": 2, "layers": [stack([0.3, 0.6]), stencil(GROW, 2 / SPB), eye(1, 0.9), lock([0.35, 0.5]), vbox("red", gain=0.6), fill("rims", "white", [0.5, 0.6], "x", step=0.5, decay=0.45)]})
b = 76
for beats in (8, 4, 2):
    for t, c in WORDS:
        H(word(t, b, beats, c)); b += beats / 4
H(fall("fall t0", 79.75)); H(fall("fall t1", 83.75)); H(fall("fall t2", 87.75))
H(fall("fall 5", 91.5, 2))
# ---------- the peak: white once, then the white splits into every colour
RB = {"fx": "grad", "on": "face+rims", "axis": "x", "wave": "tri", "scale": 1.47, "ofs": -0.235, "pal": "rainbow", "gain": 0.34}
LIDS = stencil(frames("q", 64), 4 / SPB)
CAPS = spr(frames("c", 64), WHITE, 0.5, "over", None, 4 / SPB)
JAWRB = {"fx": "grad", "on": "jaw", "axis": "x", "wave": "tri", "scale": 1.47, "ofs": -0.235, "pal": "rainbow", "gain": {"band": "bass", "lo": 0.05, "hi": 0.55, "punch": True}}
def vu(on, band, c, gain=0.45, lo=0.0, hi=1.0, punch=False):
    v = {"band": band, "lo": lo, "hi": hi, "punch": punch}
    return {"fx": "sweep", "on": on, "axis": "al", "shape": "p", "mode": "fill", "from": v, "to": v, "soft": 0.12, "pal": "rainbow", "c": c, "gain": gain}
VU = [vu("tube0", "bass", 1.0), vu("tube1", "mid", 0.5), vu("tube2", "high", 0.08)]
S({"name": "peak", "from": "peak", "to": 100, "pal": "rainbow", "layers": [RB, LIDS, CAPS, JAWRB]})
S({"name": "peak2", "from": 100, "to": "stack", "pal": "rainbow", "layers": [RB, LIDS, CAPS, eye(1), JAWRB]})
H({"name": "WHITE", "at": "peak", "beats": 2, "layers": [fill("all", "white", [0.42, 0])]})
H({"name": "VU", "at": "peak", "beats": 64, "layers": VU})
for b0 in (95.75, 99.75, 103.75, 107.75):
    H(fall("fall p%g" % b0, b0))
# ---------- the stack again, in every colour, the words a bar each
RAINS = {"fx": "grad", "on": "face", "axis": "y", "wave": "tri", "scale": 3, "speed": 0.25, "pal": "rainbow", "gain": 0.42}
STK = "|".join((["robot_st_v", "robot_st_t3", "robot_st_t2", "robot_st_pyr"] * 2) + ["robot_st_v"] * 8)
S({"name": "stack", "from": "stack", "to": 116, "pal": "rainbow", "pump": PK, "layers": [RAINS, stencil(STK, 1 / SPB), eye(1), RIM, JAWRB]})
S({"name": "stack2", "from": 116, "to": "bare", "pal": "rainbow", "pump": PK, "layers": [dict(RAINS, speed=0.5), stencil(STK, 1 / SPB), eye(1), RIM, JAWRB]})
H(flash("STACK", "stack")); H(kit("kit stack", 108.5, 15.5, tube1=0))
for i, b0 in enumerate((110, 114, 118, 122)):
    t, c = WORDS[(i * 2) % 4]
    H(word(t, b0, 4, c))
    t, c = WORDS[(i * 2 + 1) % 4]
    H(word(t, b0 + 1, 3, c)); H(fall("fall s%d" % i, b0 + 1.75))
# ---------- bare: no voice, just the machine
LOOK = "CCLLCCRRCCLRCNCN"
LIDS_F = "|".join("robot_fB" if x == "N" else "robot_fE" for x in LOOK)
PUPIL = "|".join("robot_p" + x for x in LOOK)
ROWS = "|".join("robot_r%d" % r for r in range(1, 7))
S({"name": "face", "from": "bare", "to": "bare2", "pal": "red", "pump": PK, "layers": [spr(LIDS_F, WHITE, 0.42, "over", None, 1 / SPB), spr(PUPIL, RED, 1.0, "over", None, 1 / SPB), line(0.12), RIM, vbox("white", band="bass", punch=True, lo=0.1, hi=0.5, gain=0.7)]})
S({"name": "panel", "from": "bare2", "to": "final", "pal": "red", "pump": PK, "layers": [spr(frames("lat", 3, 1), [60, 80, 100], 0.6, "max", None, 1 / SPB), spr(ROWS, WHITE, 0.6, "over", None, 2 / SPB), line(0.12), eye(1), RIM, vbox("white", band="bass", punch=True, lo=0.1, hi=0.5, gain=0.6)]})
H({"name": "BARE", "at": "bare", "beats": 2, "layers": [{"fx": "fill", "on": "ears", "pal": "white", "c": 1, "gain": [0.3, 0]}]}); H(kit("kit bare", 124.5, 15.5))
# ---------- final
RB2 = dict(RB, speed=0.0625, gain={"140": 0.34, "152": 0.12})
S({"name": "final", "from": "final", "to": "off", "pal": "rainbow", "layers": [RB2, LIDS, dict(CAPS, gain={"140": 0.6, "152": 0.2}), eye(1), JAWRB]})
H(flash("FINAL", "final")); H({"name": "VU2", "at": "final", "beats": 64, "layers": VU})
for k, (t, c) in enumerate(WORDS):
    H(word(t, 152 + k, 4, c))
# ---------- shutdown: top down, the eye last
S({"name": "off1", "from": "off", "to": "o2", "pal": "red", "layers": [stack(0.2), stencil("robot_st_t2"), eye(4), lock(0.2)]})
S({"name": "off2", "from": "o2", "to": "o3", "pal": "red", "layers": [stack(0.16), stencil("robot_st_t3"), eye(8), lock(0.12), ]})
S({"name": "off3", "from": "o3", "to": "o4", "pal": "red", "layers": [stack(0.12), stencil("robot_st_v"), eye(16, 0.6), fill("tube0", "red", 0.08)]})
S({"name": "off4", "from": "o4", "to": "end", "pal": "red", "layers": [eye(16, 0.4, 1)]})
tr["hits"] = [x for x in tr["hits"] if x]
save(tr, os.path.join("shows", "scenes", BASE + ".scene.json"))
