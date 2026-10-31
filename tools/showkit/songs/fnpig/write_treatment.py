#!/usr/bin/env python3
"""FN PIG: the treatment. Run from the repo root."""
import sys
KIT = "tools/showkit"
sys.path.insert(0, KIT)
from fmt import save
BASE = "deadmau5 - FN Pig"
R16 = 8.533333    # a flip book frame every 16th at 128 BPM
R8 = 4.266667     # every 8th
KICK = "x..."     # every beat, at step 0.25
CLAP = "....x..x....x..."
DOME = {"y_lo": 52.0, "y_hi": 172.0, "x_half": 172.0}
FULL = {"y_lo": -116.0, "y_hi": 172.0, "x_half": 172.0}
def book(stem, n=4):
    return "|".join("fnpig_%s%d" % (stem, k) for k in range(n))
FLARE, LOW, HOLES = book("snout"), book("low"), book("holes")
BOB, BOBLOW = book("bob"), book("boblow")
ROOT, ROOTLOW = book("root", 8), book("rootlow", 8)
FACE = book("face")
SHAKE, GLARE = book("shake", 8), book("glare", 8)
NX, NY = 47.0, 106.0
# chord changes in the long opening, measured from the audio
CHORDS = [24.94, 27.19, 28.81, 31.38, 33.38, 36.63, 40.44, 42.06, 43.19, 45.06, 46.5, 48.88,
          51.81, 53.06, 55.38, 56.5, 58.38, 60.69, 63.69, 64.69, 66.81, 72.19]
# the stab riff, four bars from its first note: never closer than 8ths on the shell
RIFF = "..x.....x.x....." "..........x.x.x." "x.x.....x.x....." "........x...x..." "..x.....x.x....." "..........x.x.x." "x.x.....x.x....." "............x..."
# the same split between the nostrils, a sniff from side to side
RIFF_L = "..x.......x....." "..........x...x." "x.......x......." "........x......." "..x.......x....." "..........x...x." "x.......x......." "............x..."
RIFF_R = "........x......." "............x..." "..x.......x....." "............x..." "........x......." "............x..." "..x.......x....." "................"

P = {
 "meat": [[0,0,0],[46,0,5],[140,4,16],[225,14,30],[255,60,55]],
 "pink": [[0,0,0],[80,2,34],[210,8,92],[255,24,130],[255,105,185]],
 "steel": [[0,0,0],[6,14,20],[26,54,74],[80,130,155],[175,220,240]],
 "steam": [[0,0,0],[55,75,88],[165,195,210],[240,248,252]],
 "hazard": [[0,0,0],[0,0,0],[0,0,0],[255,165,0],[255,165,0],[255,180,0]],
 "amber": [[0,0,0],[120,50,0],[255,130,0],[255,190,30]],
 "sausage": [[0,0,0],[0,0,0],[30,60,80],[90,130,150],[255,26,60],[255,40,75]],
 "fat": [[0,0,0],[200,70,80],[255,150,150]],
 "belt": [[0,0,0],[0,0,0],[0,0,0],[60,105,130],[110,165,190],[120,175,200]],
 "stripe": [[0,0,0],[0,0,0],[0,0,0],[255,140,0],[255,140,0],[255,150,0]],
 "teeth": [[0,0,0],[0,0,0],[0,0,0],[255,190,140],[255,225,190],[255,240,215]],
 "rage": [[60,0,10],[220,0,40],[255,24,110],[255,120,60],[255,215,120],[255,255,255]],
 "white": [[255,60,140],[255,180,210],[255,255,255]],
}

def orb(side, rad, soft, gain, c, **kw):
    return dict({"fx": "orb", "on": "shell", "x": NX * side, "y": NY, "rad": rad, "soft": soft, "gain": gain, "c": c}, **kw)

def orbs(rad, soft, gain, c, **kw):
    return [orb(-1, rad, soft, gain, c, **kw), orb(1, rad, soft, gain, c, **kw)]

def sprite(colour, gain=0.3, name=FLARE, rate=R16, gate=None, mix="over", frame=DOME, on="shell", **kw):
    p = dict(frame, sprite=name, color=colour)
    if rate:
        p["rate"] = rate
    L = {"fx": "preset", "name": "sprite", "on": on, "mix": mix, "params": p, "gain": gain}
    if gate:
        L["gate"] = gate
    L.update(kw)
    return L

def plate(colour, g=0.3, gate=None, flare=FLARE, low=LOW, rate=R16, boost=0.45):
    """the plate and the lift for its sparse lower rows, which would otherwise read dimmer than the top"""
    g2 = [x * boost for x in g] if isinstance(g, list) else g * boost
    return [sprite(colour, g, flare, rate, gate), sprite(colour, g2, low, rate, gate, mix="add")]

def steel(gain, **kw):
    return dict({"fx": "grad", "on": "shell", "axis": "y", "axis2": "x", "scale": 8.0, "speed": 0.03125, "warp": 0.1, "wscale": 1.0, "wspeed": 0.0625, "lo": 0.05, "hi": 0.95, "pal": "steel", "gain": gain}, **kw)

def belt(speed, gain, pal="belt", ofs=0.0, scale=12.0, on="jaw", **kw):
    return dict({"fx": "grad", "on": on, "axis": "x", "axis2": "x", "scale": scale, "speed": speed, "ofs": ofs, "lo": 0.0, "hi": 1.0, "pal": pal, "gain": gain}, **kw)

def hazard(speed, gain, on="face", scale=7.0, warp=1.5, pal="hazard", **kw):
    return dict({"fx": "grad", "on": on, "axis": "x", "axis2": "y", "scale": scale, "speed": speed, "warp": warp, "wscale": 0.5, "wspeed": 0.0, "lo": 0.0, "hi": 1.0, "pal": pal, "gain": gain}, **kw)

def steam(gain, rate=0.5, dens=0.5, on="shell", sharp=4.0, **kw):
    return dict({"fx": "twinkle", "on": on, "rate": rate, "sharp": sharp, "dens": dens, "spread": 0.2, "c": 0.6, "pal": "steam", "gain": gain, "seed": 5.0}, **kw)

def mist(gain, **kw):
    return dict({"fx": "grad", "on": "face", "axis": "y", "axis2": "x", "scale": 1.6, "speed": -0.0625, "warp": 0.3, "wscale": 1.5, "wspeed": 0.03125, "lo": 0.0, "hi": 0.45, "pal": "steam", "gain": gain}, **kw)

def flop(side="both", step=0.5, gain=0.6, seq=("12", "01"), c=0.5, ctip=0.9, pal="pink", keep=0.25, rise=0.12, rim=0.0, **kw):
    return dict({"fx": "blades", "on": "ears", "seq": list(seq), "step": step, "rise": rise, "keep": keep, "c": c, "ctip": ctip, "side": side, "pal": pal, "gain": gain, "rim": rim}, **kw)

def trot(gain=0.6, step=0.5, **kw):
    return [flop("ear1", step, gain, ("12", "01"), **kw), flop("ear2", step, gain, ("01", "12"), **kw)]

def thrash(gain=0.65, **kw):
    return [flop("ear1", 0.25, gain, ("12", "1", "01", "1"), **kw), flop("ear2", 0.25, gain, ("01", "1", "12", "1"), **kw)]

def rims(gain, c=0.6, pal="pink", **kw):
    return dict({"fx": "fill", "on": "rims", "c": c, "pal": pal, "gain": gain}, **kw)

def claps(gain=0.4, c=0.95, pal="pink", **kw):
    return dict({"fx": "fill", "on": "tubes", "c": c, "pal": pal, "gain": gain, "gate": {"pat": CLAP, "step": 0.25, "decay": 0.35}}, **kw)

def beacon(speed, gain, width=0.3, pal="amber", on="ears", **kw):
    return dict({"fx": "sweep", "on": on, "axis": "a", "shape": "saw", "mode": "band", "speed": speed, "from": -0.2, "to": 1.2, "width": width, "c": 0.75, "pal": pal, "gain": gain}, **kw)

def sparks(gain, rate=4.0, life=0.6, on="jaw+tubes", pal="amber", seed=7.0, **kw):
    return dict({"fx": "sparks", "on": on, "rate": rate, "life": life, "nbr": 0.5, "c": 0.8, "spread": 0.2, "pal": pal, "gain": gain, "seed": seed}, **kw)

BREATH = lambda lo, hi: {"band": "bass", "lo": lo, "hi": hi}
HIGH = lambda lo, hi: {"band": "high", "lo": lo, "hi": hi}
MID = lambda lo, hi: {"band": "mid", "lo": lo, "hi": hi}
PUNCH = lambda lo, hi: {"band": "bass", "lo": lo, "hi": hi, "punch": True}


tr = {"v": 1, "show": BASE, "lead": 0,
 "about": "",
 "marks": {"tone": 6, "chords": 24.94, "rouse": 45, "open": 64, "hold": 72, "fade": 84, "title": 87.75, "pickup": 91.75, "snort": 92,
   "bassin": 100, "waking": 108, "wake2": 112, "wake3": 116, "beat": 118, "inhale1": 125.375, "slam1": 125.75, "drop": 126, "d1b": 134, "d1c": 142, "d1d": 150, "d1e": 158,
   "pace": 166, "inhale2": 173.375, "slam2": 173.75, "pink": 174, "d2b": 182, "d2c": 190, "d2d": 198, "hush": 206, "pickup2": 207.75, "snort2": 208, "rebuild": 216, "r2": 224, "r3": 228, "r4": 232, "slam3": 233.75,
   "fury": 234, "f2": 242, "f3": 250, "squeal": 258, "done": 266, "doze": 274, "lastkick": 281.5, "end": 282},
 "palettes": P, "motifs": {}, "scenes": [], "hits": []}
S = tr["scenes"].append
H = tr["hits"].append
PUMP = {"pat": KICK, "step": 0.25, "depth": 0.18, "decay": 0.5}
HARD = dict(PUMP, depth=0.24)
KG = {"pat": KICK, "step": 0.25, "decay": 0.8, "floor": 0.6}
GATEK = {"pat": KICK, "step": 0.25, "decay": 0.7, "floor": 0.0}
FILL = 0.625   # the noise of a turnaround starts five 16ths into the last bar of an eight

# ACT I: asleep. Two nostrils breathing in the dark, on the song's own pulse, which quickens by itself.
S({"name": "asleep", "from": -1, "to": "tone", "pal": "meat", "layers":
   orbs(BREATH(15, 42), 14, BREATH(0.05, 1.1), 0.55)})
S({"name": "dream", "from": "tone", "to": "chords", "pal": "meat", "layers":
   orbs(BREATH(15, 44), 14, BREATH(0.05, 1.1), 0.55) + orbs(BREATH(30, 90), 40, BREATH(-0.03, 0.14), 0.42, pal="steel") + [steam(MID(-0.02, 0.45), rate=0.25, dens=0.2)]})
# ACT II: it stirs. The machinery clunks a notch on every chord, the lights come up with the filter.
NOTCH = {"keys": [[0, 0.0]] + [[c, round((i + 1) * 0.25, 3)] for i, c in enumerate(CHORDS)]}
S({"name": "stir", "from": "chords", "to": "rouse", "pal": "meat", "layers":
   orbs(BREATH(16, 44), 14, BREATH(0.0, 1.0), [0.55, 0.7]) + [steam(MID(0.0, 0.5), rate=0.25, dens=0.25), belt(0.0, [0.03, 0.16], ofs=NOTCH), steel(HIGH(0.0, 0.3))]})
S({"name": "rouse", "from": "rouse", "to": "open", "pal": "meat", "layers":
   orbs(BREATH(16, 48), 14, BREATH(-0.1, 1.05), [0.7, 0.85], wx=[0.0, 12.0], xf=0.125) + [rims(BREATH(-0.4, 0.5), pal="meat", c=0.6), belt(0.0, [0.16, 0.34], ofs=NOTCH), steel(HIGH(0.0, 0.32))]})
S({"name": "lights", "from": "open", "to": "hold", "pal": "meat", "layers":
   orbs(BREATH(18, 46), 14, BREATH(-0.2, 1.0), 0.9, wx=16.0, xf=0.25, wy=5.0, yf=0.5) + [rims(BREATH(-0.2, 0.45), pal="meat", c=0.6), belt(0.25, 0.42), steel(HIGH(-0.02, 0.32))]})
S({"name": "wash", "from": "hold", "to": "title", "pal": "meat", "layers":
   orbs(BREATH(14, 44), 14, BREATH(-0.2, 1.0), [0.9, 0.5], wx=[16.0, 4.0], xf=0.125) + [rims(BREATH(-0.1, 0.35), pal="meat", c=0.5), belt({"hold": 0.125, "fade": 0.0625}, [0.42, 0.1]), steel(HIGH(-0.08, 0.28)), steam([0.0, 0.5])]})
S({"name": "hold breath", "from": "title", "to": "pickup", "pal": "steel", "layers":
   [steel(HIGH(-0.1, 0.1))]})
# ACT III: the first snorts, on the stab riff, side to side, and an ear twitches each time.
def twitch(g):
    return [flop("ear1", 0.25, g, ("2",), keep=0.0, gate={"pat": RIFF_L, "step": 0.25, "decay": 0.5}),
            flop("ear2", 0.25, g, ("2",), keep=0.0, gate={"pat": RIFF_R, "step": 0.25, "decay": 0.5})]
SNORTL = lambda g=0.95: orb(-1, 34, 12, g, 0.72, gate={"pat": RIFF_L, "step": 0.25, "decay": 0.6})
SNORTR = lambda g=0.95: orb(1, 34, 12, g, 0.72, gate={"pat": RIFF_R, "step": 0.25, "decay": 0.6})
S({"name": "pickup", "from": "pickup", "to": "snort", "pal": "pink", "layers":
   orbs(30, 12, 0.9, 0.7, gate={"pat": "x...", "step": 0.25, "decay": 0.6})})
S({"name": "snorts", "from": "snort", "to": "bassin", "pal": "pink", "layers":
   [SNORTL(), SNORTR(), steam(0.42), mist(0.05)] + twitch(0.45)})
# ACT IV: hazard. The bass comes back, the stripes start to roll, the ears turn into alarm beacons. Something is behind the stripes.
S({"name": "hazard", "from": "bassin", "to": "waking", "pal": "pink", "layers": [
   hazard(0.125, [0.08, 0.26]), SNORTL(0.8), SNORTR(0.8), belt(0.25, [0.12, 0.35], pal="stripe"), beacon(0.125, [0.2, 0.45])]})
S({"name": "waking", "from": "waking", "to": "wake3", "pal": "pink", "layers": [
   hazard({"waking": 0.25, "wake2": 0.5}, 0.28),
   sprite("meat@0.55", [0.0, 0.3], "fnpig_snout3", 0),
   belt(0.5, [0.35, 0.5], pal="stripe"),
   beacon({"waking": 0.25, "wake2": 0.5}, [0.45, 0.6])]})
S({"name": "wake3", "from": "wake3", "to": "beat", "out": 1, "pal": "pink", "layers": [
   hazard(1.0, 0.32), sprite("meat@0.6", [0.3, 0.46], "fnpig_snout3", 0), belt(1.0, 0.55, pal="stripe"), beacon(1.0, 0.7)]})
# ACT V: the beat, before the bass: pacing. Nostrils on the kick, ears trotting, the belt running.
def slam(name, frm, to, c=0.75, pal="pink"):
    S({"name": name, "from": frm, "to": to, "out": 0.25, "pal": pal, "layers":
       orbs([46, 34], 12, [1.0, 0.5], c)})
S({"name": "pacing", "from": "beat", "to": "inhale1", "pal": "pink", "layers":
   orbs(36, 12, 0.85, 0.6, pal="meat", gate=GATEK) + [belt(0.5, 0.42), steam(HIGH(-0.1, 0.4), rate=0.5, dens=0.3)] + trot(0.5, 1.0, keep=0.12)})
S({"name": "inhale1", "from": "inhale1", "to": "slam1", "pal": "pink", "layers":
   orbs([34, 46], 12, [0.5, 0.95], 0.65, pal="meat") + [belt(0.5, 0.42)]})
slam("slam1", "slam1", "drop", pal="meat", c=0.8)
# ACT VI: the snout, raw meat, and its ears. Each eight bars ends with a great inhale, the nostrils held wide, and a snort on the one.
def phrase(name, frm, to, layers, pump=PUMP, pal="pink", held=None, fill=FILL):
    """eight bars, ending in the held inhale"""
    bar0 = MARKS[frm] if isinstance(frm, str) else frm
    bar1 = MARKS[to] if isinstance(to, str) else to
    if held is None:
        S({"name": name, "from": bar0, "to": bar1, "pal": pal, "pump": pump, "layers": layers})
        return
    S({"name": name, "from": bar0, "to": bar1 - fill, "pal": pal, "pump": pump, "layers": layers})
    S({"name": name + " in", "from": bar1 - fill, "to": bar1, "pal": pal, "pump": pump, "layers": held})
MARKS = tr["marks"]
def held(col, g, beltL, face=False, extra=()):
    gg = [g, g * 1.35]
    if face:
        return [sprite(col, gg, "fnpig_face0", 0), sprite("amber@0.95", [0.7, 1.0], "fnpig_eyes", 0), sprite("rage@0.8", 0.45, "fnpig_tusks", 0, frame=FULL), beltL] + list(extra)
    return plate(col, gg, None, "fnpig_snout0", "fnpig_low0", 0) + [beltL] + list(extra)
MARBLE = sprite("fat@0.75", 0.34, "fnpig_fat", 0, gate=KG)
phrase("raw", "drop", "d1b", plate("meat@0.62", 0.42, KG) + [MARBLE, belt(0.5, 0.42)] + trot(0.5, 1.0, keep=0.12),
       held=held("meat@0.62", 0.42, belt(0.5, 0.42)))
phrase("root", "d1b", "d1c", plate("meat@0.66", 0.42, KG, ROOT, ROOTLOW, R8) + [belt(0.5, 0.42, pal="sausage", scale=7.0)] + trot(0.5, 0.5, keep=0.18) + [rims(PUNCH(0.05, 0.5), c=0.6, pal="meat")],
       held=held("meat@0.66", 0.42, belt(0.5, 0.42, pal="sausage", scale=7.0)))
phrase("cold", "d1c", "d1d", [steel(0.2)] + plate("meat@0.75", 0.42, KG) + [belt(0.5, 0.42, pal="sausage", scale=7.0), flop("both", 0.5, 0.5, keep=0.18), claps(0.3, pal="meat")],
       held=held("meat@0.75", 0.42, belt(0.5, 0.42, pal="sausage", scale=7.0), extra=[steel(0.2)]))
phrase("flush", "d1d", "d1e", plate("pink@0.55", 0.38, KG) + [sprite("pink@0.75", 0.34, "fnpig_rim", 0, gate=GATEK), belt(1.0, 0.45, pal="stripe"), flop("both", 0.5, 0.5, keep=0.18), claps(0.35)],
       held=held("pink@0.55", 0.38, belt(1.0, 0.45, pal="stripe")))
phrase("flush2", "d1e", "pace", [hazard(0.5, 0.2)] + plate("pink@0.62", 0.4, KG, ROOT, ROOTLOW, R8) + [belt(1.0, 0.45, pal="stripe"), flop("both", 0.5, 0.5, keep=0.18), claps(0.35)],
       held=held("pink@0.62", 0.4, belt(1.0, 0.45, pal="stripe")))
# ACT VII: pacing again, the whine climbs.
S({"name": "pacing2", "from": "pace", "to": "inhale2", "pal": "pink", "layers":
   orbs(36, 12, 0.85, 0.7, gate=GATEK) + [hazard(0.5, HIGH(-0.05, 0.22)), belt(1.0, 0.45, pal="stripe"), beacon(0.5, 0.55), claps(0.3)]})
S({"name": "inhale2", "from": "inhale2", "to": "slam2", "pal": "pink", "layers":
   orbs([34, 46], 12, [0.5, 0.95], 0.72) + [belt(1.0, 0.45, pal="stripe")]})
slam("slam2", "slam2", "pink", c=0.85)
# ACT VIII: neon. Hot pink now, and banging its head.
phrase("neon", "pink", "d2b", plate("pink@0.72", 0.44, KG, BOB, BOBLOW) + [belt(1.0, 0.5), flop("both", 0.5, 0.55, ctip=1.0, keep=0.18), claps(0.4)],
       held=held("pink@0.72", 0.44, belt(1.0, 0.5)))
phrase("grinder", "d2b", "d2c", plate("pink@0.72", 0.44, KG, BOB, BOBLOW) + [belt(1.0, 0.45), sparks(1.0), flop("both", 0.5, 0.55, ctip=1.0, keep=0.18)],
       held=held("pink@0.72", 0.44, belt(1.0, 0.45), extra=[sparks(1.0)]))
phrase("xray", "d2c", "d2d", [sprite("pink@0.5", 0.32, FLARE, R16, KG), sprite("pink@0.95", 0.4, "fnpig_rim", 0, gate=GATEK), sprite("meat@0.55", 0.5, HOLES, R16, mix="add"), belt(1.0, 0.45, pal="sausage", scale=7.0), steam(HIGH(-0.1, 0.4), on="tubes", rate=2.0, sharp=3.0, dens=0.7), flop("both", 0.5, 0.55, ctip=1.0, keep=0.18)],
       held=held("pink@0.72", 0.4, belt(1.0, 0.45, pal="sausage", scale=7.0)))
phrase("neon4", "d2d", "hush", [hazard(1.0, 0.22)] + plate("pink@0.78", 0.42, KG, BOB, BOBLOW) + [belt(1.0, 0.45, pal="stripe"), sparks(1.0), flop("both", 0.25, 0.6, ("12", "1", "01", "1"), ctip=1.0, keep=0.18)],
       pump=HARD, held=held("pink@0.78", 0.42, belt(1.0, 0.45, pal="stripe"), extra=[hazard(1.0, 0.22)]))
# ACT IX: the breakdown. Steam, and the whole snout flashes on the stabs now: it has been seen.
S({"name": "hush", "from": "hush", "to": "pickup2", "pal": "steam", "layers": [
   steam(0.5), mist(0.08), sprite("pink@0.5", {"hush": 0.3, "206.5": 0.22, "207": 0.12, "207.5": 0.06}, "fnpig_snout3", 0)]})
S({"name": "pickup2", "from": "pickup2", "to": "snort2", "pal": "pink", "layers":
   plate("pink@0.72", 0.42, {"pat": "x...", "step": 0.25, "decay": 0.6}, "fnpig_snout0", "fnpig_low0", 0)})
STAB = {"pat": RIFF, "step": 0.25, "decay": 0.5}
S({"name": "snorts2", "from": "snort2", "to": "rebuild", "pal": "pink", "layers":
   plate("pink@0.72", 0.42, STAB, "fnpig_snout0", "fnpig_low0", 0) + [steam(0.42), mist(0.05)] + twitch(0.5)})
# ACT X: everything in the plant is flashing.
S({"name": "rebuild", "from": "rebuild", "to": "r2", "pal": "pink", "layers":
   [hazard(0.25, [0.1, 0.28])] + plate("pink@0.6", 0.28, STAB, "fnpig_snout0", "fnpig_low0", 0) + [belt(0.5, [0.2, 0.45], pal="stripe"), beacon(0.25, [0.25, 0.5])]})
S({"name": "rebuild2", "from": "r2", "to": "r4", "pal": "pink", "layers": [
   hazard({"r2": 0.5, "r3": 1.0}, 0.3),
   sprite("pink@0.65", [0.0, 0.36], "fnpig_face3", 0),
   sprite("amber@0.75", [0.0, 0.5], "fnpig_slits", 0),
   belt(1.0, 0.5, pal="stripe"),
   beacon({"r2": 0.5, "r3": 1.0}, [0.5, 0.7])]})
S({"name": "rebuild3", "from": "r4", "to": "slam3", "pal": "pink", "layers": [
   hazard(1.0, 0.34, pal="stripe"),
   sprite("pink@0.7", 0.42, "fnpig_face3", 0),
   sprite("amber@0.85", 0.6, "fnpig_slits", 0),
   belt(1.0, 0.55, pal="stripe"),
   beacon(1.0, 0.75)]})
slam("slam3", "slam3", "fury", pal="meat", c=0.8)
# ACT XI: the whole pig, furious.
def fury(col="pink@0.75", g=0.6, ears=None, extra=(), name=FACE, rate=R16, eyes="fnpig_eyes", erate=0, teeth=1.0, eg=0.75):
    return ([sprite(col, g, name, rate, KG), sprite("amber@0.9", eg, eyes, erate), sprite("rage@0.8", 0.45, "fnpig_tusks", 0, frame=FULL),
             belt(teeth, 0.3, pal="teeth")] + (ears or trot(0.62, 0.25, pal="rage", c=0.25, ctip=0.8, keep=0.15)) + list(extra))
TEETH = belt(1.0, 0.3, pal="teeth")
phrase("fury", "fury", "f2", fury(), pump=HARD, held=held("pink@0.75", 0.6, TEETH, face=True))
phrase("fury2", "f2", "f3", fury(extra=[hazard(1.0, 0.16)], ears=[flop("both", 0.25, 0.62, ("012", "1"), pal="rage", c=0.25, ctip=0.8, keep=0.15)]), pump=HARD, held=held("pink@0.75", 0.6, TEETH, face=True, extra=[hazard(1.0, 0.16)]))
phrase("shake", "f3", "squeal", fury(name=SHAKE, rate=R8, eyes=GLARE, erate=R8), pump=HARD, held=held("pink@0.75", 0.6, TEETH, face=True))
phrase("squeal", "squeal", "done",
   [sprite("pink@0.75", 0.6, FACE, R16, KG), sprite("amber@0.9", [0.7, 0.95], "fnpig_eyes", 0), sprite("rage@0.8", 0.45, "fnpig_tusks", 0, frame=FULL), TEETH,
    {"fx": "sweep", "on": "tubes", "axis": "al", "shape": "p", "mode": "fill", "soft": 0.2, "from": -0.1, "to": 1.1, "pal": "rage", "c": [0.15, 0.7], "cgrad": 0.3, "gain": [0.35, 0.8]},
    hazard(1.0, [0.0, 0.24])],
   pump=HARD, held=held("pink@0.8", 0.66, TEETH, face=True, extra=[hazard(1.0, 0.24)]))
# ACT XII: spent, it goes back to sleep.
phrase("tiring", "done", "doze",
   plate("pink@0.6", [0.38, 0.12], KG) + [sprite("amber@0.7", {"done": 0.5, "267": 0.32, "268": 0.16, "269": 0.0}, "fnpig_slits", 0), flop("both", {"done": 1.0, "270": 2.0}, [0.45, 0.2], ("12", "01", "0", "01"), keep=0.1), belt({"done": 0.5, "270": 0.25}, [0.4, 0.1])],
   pump=None, held=orbs([30, 44], 14, [0.4, 0.8], 0.55, pal="meat"))
S({"name": "dozing", "from": "doze", "to": "lastkick", "pal": "meat", "layers":
   orbs(30, 14, [0.8, 0.35], 0.55, gate={"pat": KICK, "step": 0.25, "decay": 0.9})})
S({"name": "last breath", "from": "lastkick", "to": "end", "pal": "meat", "layers":
   orbs([46, 20], 16, [0.9, 0.0], 0.6)})

# ---- hits
# the title, once, as the breath is held
H({"name": "FN PIG", "at": "title", "beats": 16, "layers": [
   {"fx": "preset", "name": "text", "on": "face", "fit": True, "mix": "over", "env": {"in": 1, "out": 1}, "params": {"text": "FN PIG", "color": "pink@0.7"}, "gain": 0.8}]})
# every chord, a band of cold light drops over the dome
for i, c in enumerate(CHORDS[1:], 1):
    H({"name": "clunk %d" % i, "at": c, "beats": 3, "pal": "steel", "layers": [
       {"fx": "sweep", "on": "face", "axis": "y", "shape": "p", "mode": "band", "width": 0.14, "from": 1.1, "to": 0.5, "c": 0.8, "gain": 0.16 + 0.01 * i}]
       + ([{"fx": "fill", "on": "tube0", "pal": "meat", "c": 0.6, "gain": [0.14 + 0.012 * i, 0.0]}] if i >= 9 else [])})
# the ears fill as it breathes in; on the one it snorts
def inhale(at, beats=2.5, pal="pink", c=0.95):
    return {"name": "inhale %g" % at, "at": at, "beats": beats, "pal": pal, "layers": [
      {"fx": "sweep", "on": "tubes", "axis": "al", "shape": "p", "mode": "fill", "soft": 0.25, "from": -0.1, "to": 1.15, "c": c, "gain": [0.15, 0.7]}]}
def snort(at, pal="pink", c=0.9, beats=2, g=0.55, name="fnpig_snout0"):
    return {"name": "snort %g" % at, "at": at, "beats": beats, "pal": pal, "layers": [
      {"fx": "fill", "on": "ears", "c": c, "gain": [g * 0.8, 0.0]},
      sprite(pal + "@%g" % c, [g, 0.0], name, 0, mix="add"),
      {"fx": "sweep", "on": "shell", "axis": "r", "shape": "p", "mode": "band", "from": 0.0, "to": 1.2, "width": 0.25, "c": c, "gain": [g, 0.0]}]}
H(inhale(MARKS["inhale1"], 1.5, c=0.75))
H(inhale(MARKS["inhale2"], 1.5))
for x in (134, 142, 150, 158, 166, 182, 190, 198, 206, 242, 250, 258, 266):
    H(inhale(x - FILL))
for x in (126, 134, 142, 150, 158, 174, 182, 190, 198):
    H(snort(x, g=0.5 if x < 170 else 0.6))
for x in (242, 250, 258):
    H(snort(x, g=0.6, name="fnpig_face0"))
H({"name": "first kick", "at": "beat", "beats": 2, "pal": "pink", "layers": [
   {"fx": "fill", "on": "ears", "c": 0.7, "gain": [0.45, 0.0]},
   {"fx": "sweep", "on": "shell", "axis": "r", "shape": "p", "mode": "band", "from": 0.0, "to": 1.2, "width": 0.25, "c": 0.7, "gain": [0.4, 0.0]}]})
H({"name": "pacing 2", "at": "pace", "beats": 2, "pal": "pink", "layers": [
   {"fx": "fill", "on": "ears", "c": 0.7, "gain": [0.4, 0.0]}]})
H({"name": "FURY", "at": "fury", "beats": 2.5, "pal": "white", "layers": [
   {"fx": "fill", "on": "ears", "c": 1.0, "gain": [0.32, 0.0]},
   {"fx": "fill", "on": "shell", "c": 1.0, "gain": [0.34, 0.0]},
   {"fx": "sweep", "on": "shell", "axis": "r", "shape": "p", "mode": "band", "from": 0.0, "to": 1.2, "width": 0.25, "c": 0.6, "gain": 0.7}]})

# The long set's budget: each scene's shell asks for about what the guard sends (levels measured before the
# guard, as written above), the ears a little dimmer all song.
from budget import fit
SHELL_IN = {"rouse": 21.9, "lights": 31.8, "wash": 23.6, "hold breath": 14.2, "snorts": 9.8, "hazard": 13.9, "waking": 17.6,
            "wake3": 23.5, "pacing": 10.8, "inhale1": 13.6, "raw": 21.1, "raw in": 22.3, "root": 19.8, "root in": 24.1, "cold": 31.1,
            "cold in": 40.3, "flush": 21.8, "flush in": 29.0, "flush2": 30.6, "flush2 in": 32.1, "pacing2": 16.9, "inhale2": 19.3,
            "slam2": 14.0, "neon": 30.9, "neon in": 38.5, "grinder": 30.4, "grinder in": 38.1, "xray": 23.3, "xray in": 35.3,
            "neon4": 36.4, "neon4 in": 50.2, "hush": 14.6, "snorts2": 13.9, "rebuild": 16.6, "rebuild2": 25.4, "rebuild3": 36.3,
            "fury": 43.1, "fury in": 43.6, "fury2": 47.2, "fury2 in": 52.1, "shake": 37.7, "shake in": 43.6, "squeal": 46.4,
            "squeal in": 58.2, "tiring": 15.7}
fit(tr, SHELL_IN, ask=7.2, ears=0.85)
save(tr, "shows/scenes/%s.scene.json" % BASE)
