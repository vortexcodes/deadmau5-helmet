#!/usr/bin/env python3
# THE ZOO BREAKS OUT: writes the treatment for Animal Rights. Run from the repo root.
import sys, os
KIT = "tools/showkit"
sys.path.insert(0, KIT)
from budget import scaled
from fmt import save
BASE = "deadmau5 & Wolfgang Gartner - Animal Rights"
SPB = 0.46875
BAR = 4 * SPB
R16 = round(4 / SPB, 6)      # flip-book rate: one frame a 16th note
R8 = round(2 / SPB, 6)       # one frame an 8th note

# --- the horn riff, read off the track: 32 16ths from an even bar
EVEN = "..x...x..x.x..x."
ODD = "x.x.x.x..x.x.x.."
RIFF = EVEN + ODD

# --- boxes
DOME = {"y_lo": 40, "y_hi": 170, "x_half": 171}
JAWB = {"y_lo": -118, "y_hi": -40, "x_half": 171}
def closer(k, cy=103):
    """The dome's box scaled about the eye line: k above 1 draws the eyes further away, below 1 nearer."""
    return {"y_lo": cy - 65 * k, "y_hi": cy + 65 * k, "x_half": 171 * k}

BLINK = ["animal_eyes"] * 28 + ["animal_eyes_half", "animal_eyes_shut", "animal_eyes_shut", "animal_eyes_half"]
def eyes(color, gain, frames=None, rate=R8, gate=None, env=None, wx=0, wf=0, dx=0, dy=0, box=DOME, mix="over"):
    """The predator's eyes: a flip book that opens, holds and blinks."""
    frames = frames or BLINK
    p = dict(box, sprite="|".join(frames), rate=rate if len(frames) > 1 else 0, color=color, dx=dx, dy=dy)
    if wx:
        p.update(wx=wx, wf=wf)
    L = {"fx": "preset", "name": "sprite", "on": "shell", "mix": mix, "params": p, "gain": gain}
    if gate:
        L["gate"] = gate
    if env:
        L["env"] = env
    return L

def jaw(color, gain=0.7, floor=0.25, shut="animal_jawS", opn="animal_jawO"):
    """The fangs on the jaw arc, shut on every horn stab."""
    fr = [shut if ch == "x" else opn for ch in RIFF]
    for i, ch in enumerate(RIFF):         # a stab holds shut for two 16ths when there is room
        if ch == "x" and RIFF[(i + 1) % 32] == ".":
            fr[(i + 1) % 32] = shut
    return {"fx": "preset", "name": "sprite", "on": "jaw", "mix": "over",
            "params": dict(JAWB, sprite="|".join(fr), rate=R16, color=color),
            "gain": gain, "gate": {"pat": RIFF, "step": 0.25, "decay": 0.5, "floor": floor}}

def claw_groups(side, groups, gain, c=0.75, length=32, rise=0.3, decay=0.3, pal="claw", keep=0.6):
    """Slashes in threes up one ear: groups is [(step, step, step), ...] in a cycle of `length` 16ths."""
    seq = ["2"] * length
    pat = ["."] * length
    for g in groups:
        for tube, st in enumerate(g):
            pat[st] = "x"
            for k in range(st, length):      # this tube until the next slash
                seq[k] = str(tube)
    return {"fx": "blades", "on": "ears", "side": side, "seq": seq, "step": 0.25, "rise": rise, "keep": keep,
            "c": c, "ctip": 1.0, "pal": pal, "gain": gain,
            "gate": {"pat": "".join(pat), "step": 0.25, "decay": decay}}

# The last three stabs of a bar are three slashes: left ear on the even bar, right ear on the odd
def claws(gain=0.9, pal="claw", c=0.75):
    return [claw_groups("ear1", [(9, 11, 14)], gain, c=c, pal=pal),
            claw_groups("ear2", [(25, 27, 29)], gain, c=c, pal=pal)]

def scratch(gain, pal="claw"):
    """Something in the dark at the bars: a small rake on the tom, one ear a bar."""
    return [claw_groups("ear1", [(8, 9, 10)], gain, c=0.3, pal=pal, decay=0.2),
            claw_groups("ear2", [(24, 25, 26)], gain, c=0.3, pal=pal, decay=0.2)]

BEACON_SHELL = {"fx": "sweep", "on": "shell", "axis": "a", "shape": "saw", "mode": "band", "speed": 0.5, "from": -0.1, "to": 1.1,
                "width": 0.22, "pal": "alarm", "c": 0.75}
BEACON_RIMS = {"fx": "sweep", "on": "rims", "axis": "a", "shape": "saw", "mode": "band", "speed": 0.5, "from": -0.1, "to": 1.1,
               "width": 0.35, "pal": "alarm", "c": 0.85}
SEARCH = {"fx": "orb", "on": "all", "x": 0, "y": 130, "rad": 95, "soft": 70, "wx": 300, "xf": 0.0625, "xp": 0, "wy": 30, "yf": 0.14, "pal": "light", "c": 0.8}

tr = {"v": 1, "show": BASE,
"about": "",
"lead": 0,
"marks": {"open": 4, "scan": 8, "near": 12, "scratch": 16, "light": 24, "found": 31, "alarm": 32, "alarm2": 40, "climb": 44, "riser": 46,
  "tiger": 48, "siren1": 54, "tigerb": 56, "siren2": 62, "zebra": 64, "siren3": 70, "zebrab": 72, "siren4": 78,
  "herd": 80, "herdb": 88, "night": 96, "title": 98, "wake": 104, "roll": 110, "cobra": 112, "siren5": 118, "cobrab": 120, "siren6": 126,
  "peacock": 128, "siren7": 134, "peacockb": 136, "siren8": 142, "zoo": 144, "siren9": 150, "zoob": 152, "siren10": 158,
  "empty": 160, "light2": 168, "again": 176, "last": 184, "gone": 192},
"palettes": {
  "eye": [[0, 0, 0], [120, 50, 0], [255, 150, 0], [255, 220, 60]],
  "steel": [[0, 0, 0], [0, 0, 0], [0, 0, 0], [20, 34, 50], [70, 100, 130], [140, 170, 195]],
  "alarm": [[0, 0, 0], [90, 0, 0], [255, 0, 0], [255, 40, 0], [255, 110, 0]],
  "claw": [[0, 0, 0], [160, 20, 0], [255, 110, 10], [255, 200, 90], [255, 255, 255]],
  "tiger": [[0, 0, 0], [0, 0, 0], [255, 70, 0], [255, 110, 0], [255, 150, 10]],
  "zebra": [[0, 0, 0], [0, 0, 0], [240, 240, 245], [255, 255, 255]],
  "dust": [[0, 0, 0], [50, 14, 4], [150, 60, 14], [225, 130, 50], [255, 190, 110]],
  "bull": [[0, 0, 0], [120, 0, 0], [230, 20, 0], [255, 70, 10]],
  "bone": [[0, 0, 0], [90, 80, 60], [200, 180, 140], [255, 240, 205]],
  "leopard": [[0, 0, 0], [70, 34, 0], [210, 130, 15], [255, 200, 70]],
  "fawn": [[0, 0, 0], [20, 10, 0], [50, 26, 2], [90, 48, 6]],
  "cobra": [[0, 0, 0], [0, 0, 0], [0, 30, 10], [0, 170, 50], [100, 255, 40], [220, 255, 70]],
  "venom": [[0, 0, 0], [40, 90, 0], [160, 255, 0], [235, 255, 120]],
  "peacock": {"stops": [[0, 30, 170], [0, 120, 200], [0, 210, 150], [40, 240, 70], [210, 200, 30], [0, 210, 150], [0, 120, 200]], "wrap": True},
  "plume": [[0, 0, 0], [0, 20, 110], [0, 110, 190], [0, 220, 130], [220, 210, 40]],
  "light": [[0, 0, 0], [60, 58, 40], [190, 185, 140], [255, 250, 210]],
  "white": [[255, 110, 0], [255, 200, 110], [255, 255, 255]]},
"motifs": {},
"scenes": [], "hits": []}
THROB = {"pat": "x...", "step": 0.25, "decay": 0.8, "floor": 0.72}
S = tr["scenes"].append
H = tr["hits"].append
PUMP = {"pat": "x...", "step": 0.25, "depth": 0.22, "decay": 0.5}
GREEN = [40, 230, 90]
ROUND = (["animal_low"] * 13 + ["animal_low_shut"] + ["animal_low"] * 6 + ["animal_low_shut", "animal_low_shut"]
         + ["animal_low"] * 10)
def lows(gain, env=None):
    L = eyes(GREEN, gain, frames=ROUND, box=JAWB, env=env)
    L["on"] = "jaw"
    return L

# --------------------------------------------------------------------- the dark zoo
HEART = {"fx": "fill", "on": "rims", "pal": "alarm", "c": 0.5, "gate": {"pat": "x...", "step": 0.25, "decay": 0.6}}
S({"name": "dark", "from": -1, "to": "open", "pal": "eye", "layers": [dict(HEART, gain=[0.1, 0.22])]})
OPEN = ["animal_eyes_shut"] * 4 + ["animal_eyes_half"] * 2 + ["animal_eyes"] * 22 + ["animal_eyes_half", "animal_eyes_shut", "animal_eyes_half", "animal_eyes"]
SLOW = 1 / (8 * BAR)
S({"name": "eyes open", "from": "open", "to": "scan", "pal": "eye", "layers": [
    dict(HEART, gain=0.22),
    eyes("eye@0.6", [0.25, 0.4], frames=OPEN, box=closer(1.35))]})
S({"name": "scan", "from": "scan", "to": "near", "pal": "eye", "layers": [
    dict(HEART, gain=0.22),
    eyes("eye@0.65", 0.5, wx=60, wf=SLOW, box=closer(1.35), gate=THROB)]})
S({"name": "nearer", "from": "near", "to": "scratch", "pal": "eye", "layers": [
    dict(HEART, gain=0.22),
    eyes("eye@0.7", 0.55, wx=48, wf=SLOW * 2, box=closer(1.15), gate=THROB)]})
S({"name": "scratch", "from": "scratch", "to": "light", "pal": "eye", "layers": [
    dict(HEART, gain=0.24),
    lows(0.5, env={"in": 4}),
    eyes("eye@0.7", 0.6, wx=36, wf=SLOW * 2, box=closer(0.95), gate=THROB),
    ] + scratch(0.25)})
S({"name": "searchlight", "from": "light", "to": "found", "pal": "eye", "layers": [
    dict(HEART, gain=0.26),
    lows(0.5),
    eyes("eye@0.7", 0.6, wx=36, wf=SLOW * 2, box=closer(0.95), gate=THROB),
    dict(SEARCH, gain=0.4)] + scratch(0.32)})
WIDE = ["animal_eyes_wide"] * 15 + ["animal_eyes_half"]
S({"name": "found", "from": "found", "to": "alarm", "pal": "eye", "layers": [
    dict(HEART, gain=0.3),
    dict(SEARCH, wx=0, wy=0, y=105, rad=170, soft=90, gain=0.34),
    eyes("eye@1", 0.9, frames=["animal_eyes_wide"], box=closer(0.95))]})

# --------------------------------------------------------------------- the alarm, and the cage
def jolts(a, b, amount):
    """The cage's bars jump sideways and back on every horn stab, a two-bar cycle from even bar a."""
    keys, v = [[a, 0.0]], 0.0
    bar = a
    while bar < b:
        for st, ch in enumerate(EVEN if (bar - a) % 2 == 0 else ODD):
            if ch == "x":
                v = amount - v
                keys.append([bar + st / 16.0, v])
        bar += 1
    return {"keys": keys}
def cage(gain, warp, wspeed=2.0, scale=10.0, ofs=0.0):
    # at 0.45 of the gain it was drawn with, the bars are still far brighter than "over" needs to hide what is behind them
    return {"fx": "grad", "on": "shell", "axis": "x", "axis2": "x", "scale": scale, "warp": warp, "wscale": 0.02, "wspeed": wspeed,
            "lo": 0, "hi": 1, "pal": "steel", "mix": "over", "gain": scaled(gain, 0.45), "ofs": ofs}
def tube_cage(gain, gate=None):
    L = {"fx": "fill", "on": "tubes", "pal": "steel", "c": 0.9, "gain": scaled(gain, 0.6)}
    if gate:
        L["gate"] = gate
    return L
RIFFG = {"pat": RIFF, "step": 0.25, "decay": 0.45, "floor": 0.3}
S({"name": "alarm", "from": "alarm", "to": "alarm2", "pal": "steel", "layers": [
    dict(BEACON_SHELL, gain=[0.3, 0.45]),
    eyes("eye@0.85", 0.55, wx=26, wf=1 / (2 * BAR)),
    cage([0.5, 0.7], 0.05, ofs=jolts(32, 40, 0.16)),
    tube_cage([0.38, 0.48], RIFFG),
    dict(BEACON_RIMS, gain=[0.45, 0.65])]})
S({"name": "alarm 2", "from": "alarm2", "to": "climb", "pal": "steel", "layers": [
    dict(BEACON_SHELL, gain=0.45, speed=1.0),
    eyes("eye@0.9", 0.6, wx=30, wf=1 / BAR),
    cage([0.7, 0.85], 0.07, ofs=jolts(40, 44, 0.24)),
    tube_cage([0.48, 0.55], RIFFG),
    dict(BEACON_RIMS, gain=0.7, speed=1.0),
    claw_groups("alt", [(9, 11, 14)], 0.5, length=16)]})
S({"name": "climb", "from": "climb", "to": "riser", "pal": "steel", "layers": [
    dict(BEACON_SHELL, gain=0.5, speed=1.0),
    eyes("eye@1", 0.7, wx=36, wf=2 / BAR),
    cage([0.85, 1.0], 0.1, ofs=jolts(44, 46, 0.32)),
    tube_cage([0.55, 0.62], RIFFG),
    dict(BEACON_RIMS, gain=0.75, speed=1.0),
    claw_groups("both", [(9, 11, 14)], 0.65, length=16)]})
S({"name": "riser", "from": "riser", "to": "tiger", "pal": "steel", "out": 1, "layers": [
    {"fx": "twinkle", "on": "shell", "rate": 3, "sharp": 6, "dens": 0.6, "pal": "white", "c": 0.9, "gain": [0.02, 0.2]},
    eyes("eye@1", 0.85, frames=["animal_eyes_wide"], wx=40, wf=4 / BAR),
    cage(1.0, [0.15, 0.5], wspeed=2.0),
    {"fx": "sweep", "on": "tubes", "axis": "al", "shape": "p", "mode": "fill", "soft": 0.2, "from": -0.1, "to": 1.05, "pal": "claw", "c": 0.3, "cgrad": 0.4, "gain": [0.35, 0.6]},
    dict(BEACON_RIMS, gain=0.8, speed=2.0)]})
H({"name": "SLAM", "at": "alarm", "beats": 2, "layers": [
    {"fx": "sweep", "on": "shell", "axis": "y", "shape": "p", "mode": "band", "width": 0.5, "from": 1.3, "to": -0.4, "pal": "steel", "c": 1, "gain": 0.8},
    {"fx": "blades", "on": "ears", "seq": ["012"], "step": 2, "rise": 0.08, "keep": 0, "pal": "steel", "c": 0.9, "ctip": 1, "gain": 0.8}]})

# --------------------------------------------------------------------- tiger
TIGER = {"fx": "grad", "on": "face", "axis": "x", "axis2": "y", "scale": 9.0, "speed": 0.125, "warp": 0.45, "wscale": 0.8, "wspeed": 0.0625,
         "lo": 0, "hi": 1, "pal": "tiger", "gain": 0.34}
TIGER_T = {"fx": "grad", "on": "tubes", "axis": "al", "axis2": "al", "scale": 1.5, "speed": -0.25, "lo": 0, "hi": 1, "pal": "tiger", "gain": 0.42}
KICK_R = {"fx": "fill", "on": "rims", "c": 0.85, "gain": 0.55, "gate": {"pat": "x...", "step": 0.25, "decay": 0.5}}
def tiger_lay(rev=1, face=False):
    third = eyes("eye@1", 0.9) if face else dict(KICK_R, pal="tiger")      # the second time round it has the eyes too: the whole tiger
    return [dict(TIGER, speed=0.125 * rev), TIGER_T, third, jaw("bone@1", 0.9, 0.22)] + claws()
def siren_lay(pal, stripe, eye=None, frames=None):
    return [dict(stripe, gain=0.08, speed=0), dict(BEACON_SHELL, gain=0.42), dict(BEACON_RIMS, gain=0.8),
            {"fx": "grad", "on": "tubes", "axis": "al", "axis2": "al", "scale": 1, "lo": 0, "hi": 0.35, "pal": "alarm", "gain": 0.16},
            eyes(eye or "eye@1", {"0": 0}, frames=frames or ["animal_eyes"])]
def chirp(at, pal="alarm", c=0.9):
    """The siren's falling chirp over the first three beats of a bar."""
    return {"name": "CHIRP", "at": at, "beats": 3, "pal": pal, "layers": [
        {"fx": "sweep", "on": "tubes", "axis": "al", "shape": "p", "mode": "band", "width": 0.3, "from": 1.1, "to": -0.1, "c": c, "gain": 0.75},
        {"fx": "sweep", "on": "shell", "axis": "y", "shape": "p", "mode": "band", "width": 0.22, "from": 1.05, "to": -0.1, "c": c, "gain": 0.32}]}
def stab(at, pal="alarm", c=0.95, eyec="eye@1", frames=None):
    """The fourth beat stabs, and for a bar the animal looks straight at you."""
    return {"name": "EYES", "at": at, "beats": 5, "pal": pal, "layers": [
        {"fx": "fill", "on": "ears", "c": c, "gain": 0.4, "gate": {"pat": "x" + "." * 19, "step": 0.25, "decay": 0.8}},
        eyes(eyec, 0.85, frames=frames or (["animal_eyes"] * 16 + ["animal_eyes_half", "animal_eyes_shut", "animal_eyes_shut", "animal_eyes_half"]), rate=R16, env={"out": 0.5}),
        {"fx": "preset", "name": "sprite", "on": "jaw", "mix": "over", "params": dict(JAWB, sprite="animal_jawS", color="bone@1"), "gain": 0.9, "gate": {"pat": "x" + "." * 19, "step": 0.25, "decay": 1.0}}]}
def rip(at, name="RIP", right=False, pal="claw", gain=1.0, ears=0.7, beats=2.0, broken=False):
    k = "animal_clawR" if right else "animal_claw"
    fr = [k + "1", k + "2", k + "3"] + [k + "3"] * 13
    L = [{"fx": "preset", "name": "sprite", "on": "shell", "mix": "max", "params": dict(DOME, sprite="|".join(fr), rate=R16, color="white@1"), "gain": [gain, 0.0]},
         {"fx": "blades", "on": "ears", "seq": ["0", "1", "2", "012", "012", "012", "012", "012"], "step": 0.25, "rise": 0.5, "keep": 0.2, "c": 0.5, "ctip": 1, "gain": [ears, 0]}]
    if broken:     # the cage is still there for a moment, going out behind the claws
        L.insert(0, dict(cage([0.7, 0.0], 0.3), mix="add"))
    return {"name": name, "at": at, "beats": beats, "pal": pal, "layers": L}
def bite(at, name="BITE", color="bone@1", gain=1.0, beats=2.0, ears="claw"):
    """Upper fangs on the dome's edge, the lower teeth shut on the jaw: the whole face is a mouth."""
    return {"name": name, "at": at, "beats": beats, "pal": ears, "layers": [
        {"fx": "preset", "name": "sprite", "on": "face", "mix": "max", "params": dict(DOME, sprite="animal_bite", color=color), "gain": [gain, 0]},
        {"fx": "preset", "name": "sprite", "on": "jaw", "mix": "max", "params": dict(JAWB, sprite="animal_jawS", color=color), "gain": [gain, 0]},
        {"fx": "fill", "on": "ears", "c": 0.75, "gain": [0.5, 0]}]}

PREY = ["animal_round"] * 16 + ["animal_round_shut"] * 2 + ["animal_round"] * 2
REAR = ["animal_cobra"] * 2 + ["animal_hood2"] * 2 + ["animal_hood"] * 12 + ["animal_hood2"] * 2 + ["animal_cobra"] * 2
def riff_siren(name, a, b, s, lay, stripe, pal, eye="eye@1", frames=None, out=0):
    """Six bars of riff, two of siren, as the music does it."""
    S({"name": name, "from": a, "to": s, "pal": pal, "pump": PUMP, "layers": lay})
    S({"name": name + " siren", "from": s, "to": b, "pal": pal, "out": out, "layers": siren_lay(pal, stripe)[:4]})
    H(chirp(s))
    H(stab(s + 0.75, eyec=eye, frames=frames))

riff_siren("tiger", "tiger", "tigerb", 54, tiger_lay(1), TIGER, "tiger")
riff_siren("tiger b", "tigerb", "zebra", 62, tiger_lay(-1, face=True), TIGER, "tiger")
H(rip("tiger", "RIP", broken=True))
H(bite("tigerb", "BITE"))

# --------------------------------------------------------------------- zebra: the stripes turn inside out on the horn
def flips(a, b, even=(2, 9, 14), odd=(2, 9, 13), amount=0.5):
    """ofs keys that toggle a tri-wave stripe black for white on the stabs, a two-bar cycle from even bar a."""
    keys, v = [[a, 0.0]], 0.0
    bar = a
    while bar < b:
        for st in (even if (bar - a) % 2 == 0 else odd):
            v = amount - v
            keys.append([bar + st / 16.0, v])
        bar += 1
    return {"keys": keys}
ZEBRA = {"fx": "grad", "on": "shell", "axis": "y", "axis2": "x", "scale": 7.0, "speed": 0.0, "warp": 0.7, "wscale": 1.0, "wspeed": 0.0625,
         "lo": 0, "hi": 1, "pal": "zebra", "gain": 0.26}
ZEBRA2 = {"fx": "grad", "on": "shell", "axis": "r", "axis2": "a", "scale": 6.0, "speed": 0.0, "warp": 0.3, "wscale": 3.0, "wspeed": 0.0625,
         "lo": 0, "hi": 1, "pal": "zebra", "gain": 0.26}
ZEBRA_T = {"fx": "grad", "on": "tubes", "axis": "al", "axis2": "al", "scale": 3.0, "speed": 0.0, "lo": 0, "hi": 1, "pal": "zebra", "gain": 0.3}
def zebra_lay(st, a, b):
    return [dict(st, ofs=flips(a, b)), dict(ZEBRA_T, ofs=flips(a, b, amount=0.5)), dict(KICK_R, pal="zebra", c=0.8, gain=0.45)] + claws(0.9, "zebra", 0.6)
riff_siren("zebra", "zebra", "zebrab", 70, zebra_lay(ZEBRA, 64, 70), ZEBRA, "zebra", eye="zebra@1", frames=PREY)
riff_siren("zebra b", "zebrab", "herd", 78, zebra_lay(ZEBRA2, 72, 78), ZEBRA2, "zebra", eye="zebra@1", frames=PREY)
H(rip("zebra", "RIP 2", right=True, pal="zebra"))
H(rip("zebrab", "RIP 3", pal="zebra", gain=0.8))

# --------------------------------------------------------------------- the stampede: a bull's horns, red dust, a gallop
GALLOP = "x...x.x.x...x..."
DUST = {"fx": "grad", "on": "shell", "axis": "y", "axis2": "x", "scale": 1.5, "speed": -0.25, "warp": 0.3, "wscale": 1.6, "wspeed": 0.25, "lo": 0, "hi": 0.6, "pal": "dust", "gain": 0.18}
HOOVES = {"fx": "sweep", "on": "shell", "axis": "x", "shape": "saw", "mode": "band", "speed": 0.5, "width": 0.14, "from": -0.05, "to": 1.05, "pal": "dust", "c": 0.75, "gain": 0.4}
HORNS = {"fx": "preset", "name": "sprite", "on": "shell", "mix": "over", "params": dict(DOME, sprite="animal_horns", color="bone@0.9"), "gain": 0.5, "gate": {"pat": GALLOP, "step": 0.25, "decay": 0.6, "floor": 0.5}}
BULLEYES = {"fx": "preset", "name": "sprite", "on": "shell", "mix": "over", "params": dict(DOME, sprite="animal_bull", color="bull@1"), "gain": 0.8}
GAL_T = {"fx": "blades", "on": "ears", "seq": ["012"], "step": 0.5, "rise": 0.2, "keep": 0.1, "c": 0.5, "ctip": 0.9, "pal": "dust", "gain": 0.55, "gate": {"pat": GALLOP, "step": 0.25, "decay": 0.4}}
GPUMP = {"pat": GALLOP, "step": 0.25, "depth": 0.25, "decay": 0.5}
S({"name": "stampede", "from": "herd", "to": "herdb", "pal": "dust", "pump": GPUMP, "layers": [
    DUST, HOOVES, HORNS, BULLEYES, GAL_T, dict(KICK_R, pal="bull", c=0.8, gain=0.5)]})
S({"name": "stampede 2", "from": "herdb", "to": "night", "pal": "dust", "pump": GPUMP, "layers": [
    dict(DUST, pal="bull", hi=0.9, gain=0.16), dict(HOOVES, speed=1.0, pal="dust"), HORNS, BULLEYES, GAL_T, dict(KICK_R, pal="bull", c=0.8, gain=0.5)]})
for b in (83, 87, 91, 95):
    H({"name": "SNORT", "at": b + 0.375, "beats": 2, "pal": "bull", "layers": [
        {"fx": "preset", "name": "sprite", "on": "jaw", "mix": "over", "params": dict(JAWB, sprite="animal_jawS", color="bone@1"), "gain": [0.9, 0]},
        claw_groups("both", [(0, 1, 2)], 0.85, length=8, pal="claw")]})
H(rip("herd", "RIP 4", right=True, pal="claw"))

# --------------------------------------------------------------------- the breakdown: a leopard at night, the title
SPOTS = {"fx": "twinkle", "on": "shell", "rate": 0.25, "sharp": 3, "dens": 0.22, "seed": 7, "pal": "leopard", "c": 0.7, "spread": 0.3, "gain": 0.5}
FAWN = {"fx": "grad", "on": "shell", "axis": "x", "axis2": "y", "scale": 1, "warp": 0.2, "wspeed": 0.03125, "lo": 0.3, "hi": 0.8, "pal": "fawn", "gain": 0.5}
ARP = {"fx": "blades", "on": "ears", "seq": ["0", "1", "2", "1"], "step": 0.5, "rise": 0.5, "keep": 0.25, "c": 0.45, "ctip": 0.9, "pal": "leopard", "gain": {"band": "mid", "lo": 0.12, "hi": 0.5}}
S({"name": "leopard", "from": "night", "to": "wake", "pal": "leopard", "layers": [
    dict(FAWN, env={"in": 8}), dict(SPOTS, env={"in": 4}), ARP]})
S({"name": "wake", "from": "wake", "to": "roll", "pal": "leopard", "layers": [
    dict(FAWN, gain=0.4), dict(SPOTS, dens=[0.22, 0.55], gain=[0.5, 0.65]), ARP,
    eyes("leopard@1", [0.3, 0.7]), cage([0.0, 0.5], [0.0, 0.1])]})
S({"name": "roll", "from": "roll", "to": "cobra", "pal": "leopard", "out": 0.5, "layers": [
    dict(SPOTS, dens=0.55, gain=0.6), dict(BEACON_SHELL, gain=0.4, speed=1.0),
    eyes("eye@1", 0.85, frames=["animal_eyes_wide"], wx=40, wf=2 / BAR), cage([0.55, 1.0], [0.15, 0.5], wspeed=2.0),
    {"fx": "fill", "on": "tubes", "pal": "steel", "c": 0.95, "gain": [0.3, 0.6], "gate": {"pat": "x.x.", "step": 0.25, "decay": 0.35}},
    dict(BEACON_RIMS, gain=0.8, speed=2.0)]})
H({"name": "FALL", "at": "night", "beats": 6, "pal": "leopard", "layers": [
    {"fx": "sweep", "on": "tubes", "axis": "al", "shape": "p", "mode": "band", "width": 0.35, "from": 1.1, "to": -0.1, "c": 0.8, "gain": 0.55},
    {"fx": "sweep", "on": "shell", "axis": "y", "shape": "p", "mode": "band", "width": 0.25, "from": 1.05, "to": -0.1, "c": 0.7, "gain": 0.28}]})
H({"name": "ANIMAL RIGHTS", "at": "title", "beats": 24, "layers": [{"fx": "preset", "name": "text", "on": "face", "fit": True, "mix": "over", "env": {"in": 2, "out": 2}, "params": {"text": "ANIMAL RIGHTS", "color": "leopard@1"}, "gain": 0.8}]})

# --------------------------------------------------------------------- cobra
COBRA = {"fx": "grad", "on": "face", "axis": "y", "axis2": "x", "scale": 4.0, "speed": -0.125, "warp": 0.8, "wscale": 2.5, "wspeed": 0.25, "lo": 0, "hi": 1, "pal": "cobra", "gain": 0.32}
COBRA_T = {"fx": "sweep", "on": "tubes1", "axis": "al", "shape": "tri", "mode": "band", "speed": 0.25, "width": 0.55, "from": 0.05, "to": 0.95, "pal": "cobra", "c": 0.75, "gain": 0.6}
COBRA_T2 = dict(COBRA_T, on="tubes2", **{"from": 0.95, "to": 0.05})
SLIT = eyes("venom@1", 0.8, frames=["animal_cobra"], wx=50, wf=1 / (2 * BAR))
def cobra_lay(rev=1):
    return [dict(COBRA, wspeed=0.25 * rev), COBRA_T, COBRA_T2, SLIT, jaw("venom@1", 0.8, 0.2, shut="animal_fangS", opn="animal_fangO"),
            {"fx": "sparks", "on": "tubes", "rate": 3, "life": 0.5, "pal": "venom", "c": 0.9, "gain": {"band": "high", "lo": 0, "hi": 0.7}}]
riff_siren("cobra", "cobra", "cobrab", 118, cobra_lay(1), COBRA, "cobra", eye="venom@1", frames=REAR)
riff_siren("cobra b", "cobrab", "peacock", 126, cobra_lay(-1), COBRA, "cobra", eye="venom@1", frames=REAR)
H({"name": "BREAK", "at": "cobra", "beats": 2, "layers": [
    {"fx": "fill", "on": "ears", "pal": "white", "c": 1, "gain": [0.3, 0]},
    {"fx": "fill", "on": "shell", "pal": "white", "c": 1, "gain": [0.32, 0]},
    {"fx": "preset", "name": "sprite", "on": "shell", "mix": "over", "params": dict(DOME, sprite="|".join(["animal_claw1", "animal_claw2"] + ["animal_claw3"] * 14), rate=R16, color="white@1"), "gain": [1, 0.2]}]})
H(bite("cobrab", "BITE 2", color="venom@1"))

# --------------------------------------------------------------------- peacock
FAN = {"fx": "grad", "on": "shell", "axis": "a", "axis2": "r", "scale": 9, "speed": 0.0625, "warp": 0.06, "wscale": 1.2, "wspeed": 0.125, "lo": 0, "hi": 1, "wave": "saw", "pal": "peacock", "gain": 0.26}
OCELLI = {"fx": "twinkle", "on": "shell", "rate": 0.5, "sharp": 5, "dens": 0.2, "seed": 3, "pal": "plume", "c": 1, "gain": 0.65}
PLUME = {"fx": "grad", "on": "tubes", "axis": "al", "axis2": "al", "scale": 0.5, "speed": 0.125, "lo": 0.15, "hi": 1, "pal": "plume", "gain": 0.42}
def peacock_lay(rev=1):
    return [dict(FAN, speed=0.0625 * rev), OCELLI, PLUME, dict(KICK_R, pal="plume", c=0.8, gain=0.45)] + claws(0.85, "plume", 0.85)
riff_siren("peacock", "peacock", "peacockb", 134, [dict(peacock_lay(1)[0], env={"in": 3})] + peacock_lay(1)[1:], FAN, "plume", eye="plume@1", frames=PREY)
riff_siren("peacock b", "peacockb", "zoo", 142, peacock_lay(-1), FAN, "plume", eye="plume@1", frames=PREY)
def unfurl(at, name):
    return {"name": name, "at": at, "beats": 4, "pal": "plume", "layers": [
        {"fx": "sweep", "on": "shell", "axis": "r", "shape": "p", "mode": "band", "from": 0, "to": 1.2, "width": 0.3, "c": 1, "gain": 0.7},
        {"fx": "blades", "on": "ears", "seq": ["012"], "step": 4, "rise": 0.5, "keep": 0, "c": 0.5, "ctip": 1, "gain": 0.8}]}
H(unfurl("peacock", "UNFURL"))
H(unfurl("peacockb", "UNFURL 2"))

# --------------------------------------------------------------------- all of them
JAWBONE = jaw("bone@1", 0.9, 0.25)
def zoo(name, a, b, stripe, tubes, pal, bars_flip=False):
    st = dict(stripe)
    tu = [dict(t) for t in (tubes if isinstance(tubes, list) else [tubes])]
    if bars_flip:
        st["ofs"] = flips(a, b)
        for t in tu:
            t["ofs"] = flips(a, b)
    rims = [] if len(tu) > 1 else [dict(KICK_R, pal=pal, c=0.85, gain=0.55)]
    S({"name": name, "from": a, "to": b, "pal": pal, "pump": PUMP, "layers": [dict(st, on="face")] + tu + rims + [JAWBONE] + claws()})
zoo("zoo tiger", 144, 146, TIGER, TIGER_T, "tiger")
zoo("zoo zebra", 146, 148, ZEBRA, ZEBRA_T, "zebra", bars_flip=True)
zoo("zoo cobra", 148, 150, COBRA, [COBRA_T, COBRA_T2], "cobra")
S({"name": "zoo siren", "from": "siren9", "to": "zoob", "pal": "tiger", "layers": siren_lay("tiger", TIGER)[:4]})
H(chirp("siren9")); H(stab(150.75))
zoo("zoo peacock", 152, 154, FAN, PLUME, "plume")
S({"name": "zoo tiger 2", "from": 154, "to": 156, "pal": "tiger", "pump": PUMP, "layers": tiger_lay(-1, face=True)})
S({"name": "chimera", "from": 156, "to": "siren10", "pal": "tiger", "pump": PUMP, "layers": [
    dict(TIGER, on="left", speed=0.25), dict(ZEBRA, on="right", ofs=flips(156, 158)),
    dict(TIGER_T, on="tubes1"), dict(ZEBRA_T, on="tubes2", ofs=flips(156, 158)), JAWBONE,
    claw_groups("both", [(9, 11, 14), (25, 27, 29)], 0.9)]})
S({"name": "zoo siren 2", "from": "siren10", "to": "empty", "pal": "tiger", "layers": siren_lay("tiger", ZEBRA)[:4]})
H(chirp("siren10")); H(stab(158.75))
H(bite("zoo", "BITE 3"))
H(rip("zoob", "RIP 5", right=True))
# each change of animal is a claw going through the last one
for at, right in ((146, True), (148, False), (154, False), (156, True)):
    H(rip(at, "SWAP", right=right, gain=0.8, beats=1.5, ears=0.6))

# --------------------------------------------------------------------- the empty cage, and eyes that are free
S({"name": "empty cage", "from": "empty", "to": "light2", "pal": "steel", "layers": [
    dict(HEART, gain=0.24),
    cage([0.6, 0.0], 0.04, wspeed=0.25, scale=5.0),
    dict(SEARCH, gain=[0.0, 0.5], env={"in": 8})]})
S({"name": "search", "from": "light2", "to": "again", "pal": "steel", "layers": [
    dict(HEART, gain=0.24),
    dict(SEARCH, xf=0.125, gain=[0.5, 0.1])] + scratch(0.25)})
S({"name": "watching", "from": "again", "to": "last", "pal": "eye", "layers": [
    dict(HEART, gain=0.24),
    lows(0.5, env={"in": 8}),
    eyes("eye@0.7", 0.5, wx=70, wf=1 / (4 * BAR), box=closer(0.95), env={"in": 4})] + scratch(0.25)})
S({"name": "last pair", "from": "last", "to": "gone", "pal": "eye", "layers": [
    dict(HEART, gain=[0.24, 0.1]),
    eyes("eye@0.7", 0.5, wx=48, wf=SLOW, box=closer(0.95))]})
CLOSE = ["animal_eyes_half", "animal_eyes_shut", "animal_eyes_half", "animal_eyes", "animal_eyes", "animal_eyes_half", "animal_eyes_shut"] + ["animal_eyes_shut"] * 9
S({"name": "gone", "from": "gone", "to": 201, "pal": "eye", "layers": [
    eyes("eye@0.6", {"gone": 0.35, "193.5": 0}, frames=CLOSE, box=closer(0.95))]})

for b in ("scratch", "light", "last"):
    H({"name": "RAKE", "at": b, "beats": 1.5, "pal": "claw", "layers": [claw_groups("both", [(0, 1, 2)], 0.55, length=6, c=0.5, decay=0.25)]})
def leave(at, pal, c, name):
    return {"name": name, "at": at, "beats": 8, "pal": pal, "layers": [
        {"fx": "sweep", "on": "shell", "axis": "x", "shape": "p", "mode": "band", "width": 0.16, "from": 0.05, "to": 0.95, "c": c, "gain": 0.45},
        {"fx": "sweep", "on": "tubes", "axis": "al", "shape": "p", "mode": "band", "width": 0.3, "from": -0.1, "to": 1.1, "c": c, "gain": [0.4, 0.1]}]}
H(leave(160, "tiger", 1, "LEAVING"))
H(leave(162, "zebra", 1, "LEAVING 2"))
H(leave(164, "cobra", 0.8, "LEAVING 3"))
H(leave(166, "plume", 0.85, "LEAVING 4"))
H(rip("light2", "MARKS", gain=0.4, ears=0.35, beats=4))
H(rip("again", "MARKS 2", right=True, gain=0.3, ears=0.3, beats=4))

tr["about"] = ("Bars of a measured grid, shows/scenes/deadmau5 & Wolfgang Gartner - Animal Rights.beats: bar b starts at 1.875 b seconds (128.000 BPM), bar 0 is the first kick at the very start of the file, "
 "and the phrases turn on bars 32, 48, 96, 112 and 160, with the falling siren chirp on the last two bars of every eight in the drops. The zoo at night, and everything in it gets out. "
 "It starts in the dark with a heartbeat on the rims and a pair of amber slit eyes that open, blink and scan, a little nearer every few bars; at bar 16 a second animal's green eyes open low down on the jaw arc and something scratches at the bars on the tom. "
 "A watchman's searchlight goes across the whole helmet, ear to ear, and on bar 31 it finds them. Bar 32 is the alarm: the cage slams down, steel bars painted over the eyes so they look out between them, a red beacon going round the shell and the rims, and the bars jolt sideways on every stab of the horn riff, harder each phrase, until the riser shakes them loose and everything cuts one beat before the drop. "
 "Bar 48 the claws go through it, three white gashes one 16th apart. From there each section is a different animal, and it wears the helmet: the tiger is orange and black stripes sweeping the dome with white teeth on the jaw arc, shutting on every horn stab, the fangs being the jaw arc's own LEDs with the dark visor as the open mouth. "
 "The zebra is black and white stripes, wavy and then arched, that turn inside out on the horn. The stampede drops the riff for the gallop in the bass: a bull's horns round the top of the dome, small red eyes, dust rolling, all six tubes kicking on the gallop, and it snorts on the stab that comes every fourth bar. "
 "The ears are claws the whole way through: the last three horn stabs of each bar are three slashes up the three tubes of one ear, left ear then right. And every eight bars the music does its siren, so the show does: the animal drops to almost nothing, the beacon comes back, the chirp falls down the tubes and the shell, and on the stab the animal looks straight at you for a bar: slit eyes for the hunters, round wide-set ones in white for the zebra and gold for the peacock, and the cobra rears, its hood flaring round the dome with the two slits inside. "
 "The breakdown is a leopard at night: gold spots and a fawn glow, the arpeggio going up the tubes, and the title crossing once. The eyes come back, the spots multiply, the cage comes back, and the same riser breaks it at bar 112, the one moment of white in the song. "
 "The second drop is a cobra, interlaced green snakes with two slit eyes swaying and two fangs on the jaw, then a peacock whose fan opens across the dome in blue, green and gold with its plumes up the ears. The last sixteen bars are all of them, a different animal every two bars, ending in a chimera, half tiger, half zebra. "
 "Then the drums are alone again, as they were at the start, and the animals cross the empty cage one last time on their way out while the searchlight comes back and finds nothing. At bar 176 the eyes open again, out here with you. One pair is left at the end, and when the music stops they close.")
# The long set's budget: each scene's shell asks for about what the guard sends (levels measured before the
# guard, as written above), the ears dimmer all song, the cage left as written: it hides by painting over.
from budget import fit
SHELL_IN = {"scan": 9.6, "nearer": 10.0, "scratch": 12.3, "searchlight": 18.5, "found": 58.1, "alarm": 32.9, "alarm 2": 40.5,
            "climb": 49.4, "riser": 50.1, "tiger": 37.2, "tiger siren": 25.8, "tiger b": 57.9, "tiger b siren": 25.8, "zebra": 33.4,
            "zebra siren": 33.6, "zebra b": 33.3, "zebra b siren": 33.1, "stampede": 27.0, "stampede 2": 27.0, "leopard": 30.6,
            "wake": 21.6, "roll": 48.3, "cobra": 30.1, "cobra siren": 37.7, "cobra b": 27.6, "cobra b siren": 37.7, "peacock": 33.8,
            "peacock siren": 26.0, "peacock b": 35.9, "peacock b siren": 26.0, "zoo tiger": 42.4, "zoo zebra": 42.5, "zoo cobra": 33.6,
            "zoo siren": 25.8, "zoo peacock": 42.3, "zoo tiger 2": 59.2, "chimera": 43.1, "zoo siren 2": 31.2, "empty cage": 20.6,
            "watching": 11.0, "last pair": 8.5}
fit(tr, SHELL_IN, ask=6.0, ears=0.6, keep=lambda L: L.get("pal") == "steel" and L.get("mix") == "over")
save(tr, "shows/scenes/%s.scene.json" % BASE)
