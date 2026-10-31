#!/usr/bin/env python3
"""THE CHORD ORGAN: treatment generator for deadmau5 - Some Chords."""
import math, os, sys
KIT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, KIT)
from fmt import save
BASE = "deadmau5 - Some Chords"

# ---------------------------------------------------------------- the harmony
GM, EE, FS, GP = 0, 1, 2, 3     # G#m cobalt, E ruby, F# gold, G# major verdigris
GLASS = [[0, 14, 90], [0, 55, 255], [40, 125, 255],
         [80, 0, 10], [255, 0, 26], [255, 60, 60],
         [110, 45, 0], [255, 130, 0], [255, 200, 60],
         [0, 75, 60], [0, 205, 150], [110, 255, 215]]
def cmain(ch): return round((3 * ch + 1) / 11.0, 5)
def clo(ch): return round((3 * ch + 0.25) / 11.0, 5)
def chi(ch): return round((3 * ch + 2) / 11.0, 5)

TL = []
def cycle(start, n):
    for k in range(n):
        b = start + 4 * k
        TL.extend([(b, GM), (b + 0.875, EE), (b + 2.375, FS), (b + 2.875, GP)])
def vamp(start, end):
    b = start
    TL.append((b, GM))
    while b + 8 <= end:
        TL.extend([(b + 7.375, FS), (b + 7.625, EE)])
        b += 8
        if b < end:
            TL.append((b, GM))
cycle(0, 12); vamp(52, 116); cycle(120, 10); vamp(164, 228); TL.append((228, GM))
TL.sort()
def chord_at(bar):
    ch = GM
    for b, c in TL:
        if b <= bar:
            ch = c
        else:
            break
    return ch
def num(b):
    return ("%.4f" % b).rstrip("0").rstrip(".")
def K(lo, hi, f, shift=0.0):
    """Keys from the chord chart, on every change between bars lo and hi."""
    out = {num(lo): f(chord_at(lo - shift))}
    last = out[num(lo)]
    for b, c in TL:
        bs = b + shift
        if lo < bs < hi and f(c) != last:
            out[num(bs)] = f(c)
            last = f(c)
    return out
def TURN(lo, hi, base, flash=0.0):
    """A gain that steps aside while a turnaround plays, so the whole window changes colour."""
    out = {num(lo): base}
    for b, c in TL:
        if lo < b < hi:
            out[num(b)] = base if c == GM else flash
    return out

# ---------------------------------------------------------------- the rhythm
EIGHTHS = {0, 7, 19, 23}      # where the chords change in the 4-bar cycle, in 8ths
def roll(shift):
    return "".join("x" if (i - shift) % 32 in EIGHTHS else "." for i in range(32))
BASS = "x...x...x..x..x."       # the low end of the groove: 1, 2, 3 and the two syncopes
BEAT = "x..."
SPR = dict(y_lo=-116, y_hi=172, x_half=174)
FAN = (0.015, 0.485)            # the fan on the shell's own angle axis, right to left

def kick(decay=0.7, floor=0.12, pat=BASS):
    return {"pat": pat, "step": 0.25, "decay": decay, "floor": floor}
def glass(lo, hi, gain, on="face", **kw):
    L = {"fx": "grad", "on": on, "axis": "x", "axis2": "y", "scale": 1.3, "speed": 0.02, "warp": 0.25, "wscale": 1.3, "wspeed": 0.015,
         "lo": K(lo, hi, clo), "hi": K(lo, hi, chi), "gain": gain}
    L.update(kw)
    return L
def jawkick(lo, hi, gain=0.42, pat=BASS, decay=0.6, floor=0.04):
    return {"fx": "fill", "on": "jaw", "c": K(lo, hi, cmain), "gain": gain, "gate": kick(decay, floor, pat)}
def pedal(lo, hi, gain):
    return {"fx": "fill", "on": "jaw", "c": K(lo, hi, cmain), "gain": gain, "gate": {"pat": roll(0), "step": 0.5, "decay": 3, "floor": 0.55}}
def pipe(t, lo, hi, gain, floor=0.16):
    sh = 0.125 * t
    return {"fx": "grad", "on": "tube%d" % t, "axis": "al", "axis2": "al", "scale": 0.5, "lo": K(lo, hi, clo, sh), "hi": K(lo, hi, chi, sh),
            "gain": gain, "gate": {"pat": roll(t), "step": 0.5, "decay": 2.2, "floor": floor}}
def pipes(lo, hi, gain, n=3, floor=0.16):
    return [pipe(t, lo, hi, gain, floor) for t in range(n)]
def sprite(name, color, gain=1.0, **kw):
    L = {"fx": "preset", "name": "sprite", "on": "shell", "mix": "over", "params": dict(SPR, sprite=name, color=color), "gain": gain}
    L.update(kw)
    return L
def lead(name="chords_lead"):
    return sprite(name, [0, 0, 5])
def stain(name, chord, lo, hi, gain, floor=0.4, rate=None):
    L = sprite(name, "glass@%g" % cmain(chord), TURN(lo, hi, gain), gate=kick(0.8, floor))
    if rate:
        L["params"]["rate"] = rate
    return L
def tubes_all(lo, hi, gain, floor=0.16):
    return {"fx": "grad", "on": "tubes", "axis": "al", "axis2": "al", "scale": 0.5, "lo": K(lo, hi, clo), "hi": K(lo, hi, chi), "gain": gain,
            "gate": {"pat": roll(0), "step": 0.5, "decay": 2.2, "floor": floor}}
def organ(lo, hi, gain=0.46, enter=False):
    """The triad in order on the 8ths; on the clap all three tubes at once, with the rims."""
    seq = [("012" if i in (2, 12) else ["0", "1", "2", "1"][i % 4]) for i in range(16)]
    g = TURN(lo, hi, gain, 0.2)
    if enter:
        g[num(lo)] = 0.0; g[num(lo + 0.5)] = gain
    return {"fx": "blades", "seq": seq, "step": 0.5, "rise": 0.3, "keep": 0.08, "rim": 0.45, "c": K(lo, hi, cmain), "ctip": K(lo, hi, chi), "gain": g}
def arp(lo, hi, gain=0.42, step=0.25, seq=("0", "1", "2", "1")):
    return {"fx": "blades", "seq": list(seq), "step": step, "rise": 0.4, "keep": 0.08, "c": K(lo, hi, cmain), "ctip": K(lo, hi, chi), "gain": TURN(lo, hi, gain, 0.16)}
def chirp(lo, hi, gain=0.36, claps=False, enter=False):
    """The off-beat rising plucks: the triad on the beat, and all three pipes firing up on every off-beat, gold at the tip."""
    seq = [("012" if i % 2 or (claps and i in (2, 12)) else ["0", "1", "2", "1"][(i // 2) % 4]) for i in range(16)]
    g = TURN(lo, hi, gain, 0.0)
    if enter:
        g[num(lo)] = 0.0; g[num(lo + 0.5)] = gain
    return {"fx": "blades", "pal": "spark", "seq": seq, "step": 0.5, "rise": 0.5, "keep": 0.06, "c": 0, "ctip": 1, "gain": g}
def rose(lo, hi, gain, speed=0.125, width=0.1):
    """One bright beam going to and fro round the fan, a sun crossing the window."""
    return {"fx": "sweep", "on": "face", "axis": "a", "shape": "tri", "mode": "band", "speed": speed, "from": FAN[0], "to": FAN[1], "width": width, "c": K(lo, hi, chi), "gain": gain}
def hats(gain=0.8):
    return {"fx": "twinkle", "on": "face", "rate": 0.5, "sharp": 2, "dens": 0.35, "seed": 3, "c": chi(GM), "gain": gain, "gate": {"pat": "..x.", "step": 0.25, "decay": 0.5}}
def ring(c, gain=0.6, pal="glass"):
    return {"fx": "sweep", "on": "shell", "axis": "r", "shape": "p", "mode": "band", "from": 0, "to": 1.15, "width": 0.3, "pal": pal, "c": c, "gain": gain}

# ---------------------------------------------------------------- the melody, as a candle behind the glass
MEL = [(0, "B"), (0.75, "A#"), (1.1875, "G#"), (2.4375, "A#"), (3.0625, "C"),
       (4, "B"), (4.75, "A#"), (5.1875, "F#"), (5.75, "G#"), (6.4375, "A#"), (7.0625, "C")]
PITCH = {"F#": 0, "G#": 1, "A#": 2, "B": 3, "C": 4}
def candle(lo, hi, gain, rad=62.0):
    xs, ys = {}, {}
    def pos(n):
        th = math.radians(155 - PITCH[n] * 32.5)     # low on the left, high on the right, round the fan
        return round(112 * math.cos(th), 1), round(32 + 105 * math.sin(th), 1)
    cur = None
    for base in range(120, 170, 8):
        for off, n in MEL:
            b = base + off
            if b <= lo:
                cur = n
            elif b < hi:
                x, y = pos(n)
                xs[num(b)] = x; ys[num(b)] = y
    x0, y0 = pos(cur or "B")
    xs[num(lo)] = x0; ys[num(lo)] = y0
    return {"fx": "orb", "on": "face", "x": xs, "y": ys, "rad": rad, "soft": 40, "c": K(lo, hi, chi), "cgrad": -0.0909, "gain": gain}

# ---------------------------------------------------------------- the song
tr = {"v": 1, "show": BASE, "lead": 0, "about": "",
      "marks": {"pedal": 0, "root": 4, "third": 8, "fifth": 12, "pane1": 16, "pane2": 20, "pane3": 24, "pane4": 28, "window": 32, "window2": 40,
                "hold": 48, "crash": 51.75, "flood": 52, "stain1": 68, "stain2": 84, "stain3": 100, "cut": 116, "pedal2": 120, "candle": 128, "candle2": 136,
                "wash": 144, "beat2": 148, "hold2": 160, "crash2": 163.75, "blaze": 164, "clapback": 172, "trade": 180, "trade2": 188, "stop": 195, "crash3": 195.75, "home": 196,
                "strip": 212, "ticks": 228, "end": 236},
      "palettes": {"glass": GLASS,
                   "white": [[255, 255, 255], [255, 255, 255]],
                   "spark": [[0, 55, 255], [40, 125, 255], [255, 170, 30]]},
      "motifs": {}, "scenes": [], "hits": []}
def S(name, a, b, layers, pump=None, out=0):
    sc = {"name": name, "from": a, "to": b, "pal": "glass", "layers": layers}
    if pump: sc["pump"] = pump
    if out: sc["out"] = out
    tr["scenes"].append(sc)
def H(name, at, beats, layers, pal="glass"):
    tr["hits"].append({"name": name, "at": at, "beats": beats, "pal": pal, "layers": layers})
PUMP = {"pat": BASS, "step": 0.25, "depth": 0.42, "decay": 0.5}
SOFT = {"pat": BEAT, "step": 0.25, "depth": 0.25, "decay": 0.6}

# --- the organ starts in the dark: only the pedal, then the pipes one note at a time
S("pedal", 0, 4, [pedal(0, 4, [0.12, 0.3])])
S("root", 4, 8, [pedal(4, 8, 0.3), pipe(0, 4, 8, [0.26, 0.38])])
S("third", 8, 12, [pedal(8, 12, 0.3), pipe(0, 8, 12, 0.38), pipe(1, 8, 12, [0.26, 0.38])])
S("fifth", 12, 16, [pedal(12, 16, 0.3), pipe(0, 12, 16, 0.38), pipe(1, 12, 16, 0.38), pipe(2, 12, 16, [0.26, 0.38])])
# --- the window goes in, one pane at a time
for k, (a, m, g) in enumerate([(16, "chords_m1", 0.3), (20, "chords_m2", 0.26), (24, "chords_m3", 0.22), (28, "chords_m4", 0.2)]):
    b = a + 4
    S("pane%d" % (k + 1), a, b, [pedal(a, b, 0.28), glass(a, b, g)] + pipes(a, b, 0.34) + [lead(m)], pump=dict(SOFT, depth=0.12) if a >= 28 else None)
for a, m in [(16, "chords_ruby1"), (20, "chords_blue"), (24, "chords_gold"), (28, "chords_p06")]:
    H("PANE", a, 3, [{"fx": "preset", "name": "sprite", "on": "shell", "params": dict(SPR, sprite=m, color="glass@%g" % chi(GM)), "gain": [1.0, 0.0]}])
# --- all of it, with the beat under it
S("window", 32, 40, [jawkick(32, 40, 0.42, pat=BEAT, floor=0.08), glass(32, 40, 0.2, gate=kick(0.9, 0.3, BEAT))] + pipes(32, 40, 0.36) + [lead()], pump=SOFT)
S("windowb", 40, 48, [jawkick(40, 48, 0.46, pat=BEAT, floor=0.08), glass(40, 48, 0.22, gate=kick(0.9, 0.3, BEAT))] + pipes(40, 48, 0.4) + [lead()], pump=SOFT)
H("WHOLE", 32, 2, [ring(chi(GM), 0.5)])
# --- the held G major: light climbing the whole window, the pipes firing faster and faster
def hold(a):
    b = a + 4
    return [{"fx": "sweep", "on": "face", "axis": "y", "shape": "p", "mode": "fill", "soft": 0.2, "from": -0.15, "to": 1.15, "c": cmain(GP), "gain": [0.2, 0.28]},
            {"fx": "sweep", "on": "face", "axis": "y", "shape": "p", "mode": "band", "width": 0.14, "from": -0.05, "to": 1.2, "c": chi(GP), "gain": [0.3, 0.6]},
            {"fx": "fill", "on": "face", "c": clo(GP), "gain": 0.05},
            {"fx": "fill", "on": "jaw", "c": cmain(GP), "gain": [0.32, 0.08]},
            {"fx": "blades", "seq": ["012"], "step": {num(a): 2, num(a + 2): 1, num(a + 3): 0.5, num(a + 3.5): 0.25}, "rise": 0.7, "keep": 0.1, "rim": 0.8, "c": cmain(GP), "ctip": chi(GP), "gain": [0.26, 0.5]},
            lead()]
S("hold", 48, 52, hold(48), out=1)
H("CRASH", "crash", 1, [{"fx": "fill", "on": "rims", "c": chi(GP), "gain": [0.8, 0]}])
# --- the first drop belongs to the shell: dark ears, and the window floods from the middle
H("FLOOD", "flood", 2, [ring(chi(GM), 0.9)])
def flood(name, a, b, extra, under=(), g=0.22, floor=0.12, pump=PUMP):
    S(name, a, b, [glass(a, b, g, gate=kick(0.7, floor))] + list(under) + [jawkick(a, b), lead()] + extra, pump=pump)
flood("flood", 52, 68, [organ(52, 68, enter=True)], under=[rose(52, 68, 0.42)])
flood("stain1", 68, 84, [organ(68, 84), stain("chords_ruby1", EE, 68, 84, 0.34)], under=[hats()], g=0.17)
flood("stain2", 84, 100, [chirp(84, 100), stain("chords_ruby1", EE, 84, 100, 0.3), stain("chords_gold", FS, 84, 100, 0.26)], g=0.15, floor=0.08)
flood("stain3", 100, 116, [arp(100, 116), stain("chords_ruby2", EE, 100, 116, 0.28), stain("chords_gold", FS, 100, 116, 0.26)], g=0.15, floor=0.08)
H("STAIN 1", "stain1", 2, [ring(cmain(EE), 0.6)])
H("STAIN 2", "stain2", 2, [ring(cmain(FS), 0.6)])
H("STAIN 3", "stain3", 2, [ring(cmain(EE), 0.6)])
# --- everything stops; the title crosses the dark
S("cut", 116, 120, [{"fx": "fill", "on": "jaw", "c": clo(EE), "gain": [0.3, 0.0]}])
H("SOME CHORDS", "cut", 22, [{"fx": "preset", "name": "text", "on": "face", "fit": True, "mix": "over", "env": {"in": 1, "out": 2},
                              "params": {"text": "SOME CHORDS", "color": "glass@%g" % cmain(FS)}, "gain": 0.42}])
# --- the second time: pedal and pipes, then a candle walks the melody behind the dark glass
S("pedal2", 120, 128, [pedal(120, 128, 0.26)] + pipes(120, 128, [0.16, 0.3]))
S("candle", 128, 136, [pedal(128, 136, 0.26), candle(128, 136, [0.3, 0.42], rad=[52, 62])] + pipes(128, 136, 0.28) + [lead()])
S("candleb", 136, 144, [pedal(136, 144, 0.28), candle(136, 144, 0.46, rad=[62, 74]), glass(136, 144, [0.02, 0.08]), tubes_all(136, 144, 0.3), lead()])
S("wash", 144, 148, [pedal(144, 148, 0.28), candle(144, 148, 0.46, rad=74), glass(144, 148, 0.12), tubes_all(144, 148, 0.32), lead()])
H("DAWN", "wash", 2, [ring(chi(GM), 0.6)])
S("beat2", 148, 160, [jawkick(148, 160, 0.46, pat=BEAT, floor=0.08), glass(148, 160, 0.13, gate=kick(0.9, 0.3, BEAT)), candle(148, 160, 0.42, rad=80), tubes_all(148, 160, 0.34), lead()], pump=SOFT)
H("BEAT", 148, 2, [ring(chi(GM), 0.5)])
S("hold2", 160, 164, hold(160), out=1)
H("CRASH 2", "crash2", 1, [{"fx": "fill", "on": "rims", "c": chi(GP), "gain": [0.8, 0]}])
# --- the second drop belongs to the ears: white, the only white in the song, then the whole window blooms
H("WHITE", "blaze", 2, [{"fx": "blades", "pal": "white", "seq": ["012"], "step": 2, "rise": 0.08, "keep": 0, "rim": 0.8, "c": 0, "ctip": 0, "gain": 0.6}])
def blaze(name, a, b, ruby, gold, ears, g=0.15):
    S(name, a, b, [glass(a, b, g, gate=kick(0.7, 0.08)), jawkick(a, b), lead(), ears, ruby, gold], pump=PUMP)
BAR_RATE = round(1.0 / (4 * 0.468747), 6)
def stains(a, b, rate=None, g=0.28):
    if rate is None:
        return stain("chords_ruby2", EE, a, b, g), stain("chords_gold", FS, a, b, g)
    return stain("chords_ruby2|chords_gold", EE, a, b, g, rate=rate), stain("chords_gold|chords_ruby2", FS, a, b, g, rate=rate)
blaze("blaze", 164, 172, *stains(164, 172), chirp(164, 172, enter=True))
blaze("clapback", 172, 180, *stains(172, 180, BAR_RATE), chirp(172, 180, 0.4, claps=True))
blaze("trade", 180, 188, *stains(180, 188, BAR_RATE * 2), chirp(180, 188))
blaze("tradeb", 188, 195, *stains(188, 195, BAR_RATE * 4), chirp(188, 195, 0.4, claps=True))
# --- the stopped bar: just the turnaround, in the jaw and the ears
S("stop", 195, 196, [{"fx": "fill", "on": "jaw", "c": K(195, 196, cmain), "gain": {"195": 0, "195.375": 0.5}},
                     {"fx": "grad", "on": "tubes", "axis": "al", "axis2": "al", "scale": 0.5, "lo": K(195, 196, clo), "hi": K(195, 196, chi), "gain": {"195": 0, "195.375": 0.3}}])
H("CRASH 3", "crash3", 1, [{"fx": "fill", "on": "rims", "c": chi(EE), "gain": [0.5, 0]}])
# --- home: cobalt again, the shell's moment again, then the window comes out pane by pane
H("HOME", "home", 2, [ring(chi(GM), 0.9)])
flood("home", 196, 212, [organ(196, 212, enter=True)], under=[rose(196, 212, 0.4, speed=0.0625, width=0.14)], g=0.18)
for a, m in [(212, "chords_m4"), (216, "chords_m3"), (220, "chords_m2"), (224, "chords_m1")]:
    b = a + 4
    S("strip%d" % a, a, b, [glass(a, b, 0.2, gate=kick(0.7, 0.12)), jawkick(a, b, 0.4), lead(m), organ(a, b, 0.4)], pump=PUMP)
# --- every turnaround in the ears: gold, then ruby
for b in [b for b, c in TL if c == FS and (52 < b < 116 or 164 < b < 228) and b != 195.375]:
    H("TURN", b, 2.5, [{"fx": "grad", "on": "tubes", "axis": "al", "axis2": "al", "scale": 0.5, "lo": {num(b): clo(FS), num(b + 0.25): clo(EE)}, "hi": {num(b): chi(FS), num(b + 0.25): chi(EE)}, "gain": 0.24}])
# --- only the ticks left, and the last pane goes out
S("ticks", 228, 236, [glass(228, 236, [0.2, 0.0]), lead("chords_m1"),
                      {"fx": "fill", "on": "rims", "c": cmain(GM), "gain": [0.5, 0.15], "gate": {"pat": "x...", "step": 0.25, "decay": 0.35}},
                      {"fx": "blades", "seq": ["0"], "step": 1, "rise": 0.2, "keep": 0, "c": clo(GM), "ctip": cmain(GM), "gain": [0.3, 0.06]}])

tr["about"] = "draft"
save(tr, os.path.join("shows", "scenes", BASE + ".scene.json"))
