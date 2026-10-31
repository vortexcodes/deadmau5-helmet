#!/usr/bin/env python3
"""The treatment for Kaskade feat. deadmau5 - I Remember: MEMORY."""
import json, os, sys
KIT = "tools/showkit"
sys.path.insert(0, KIT)
from fmt import save

BASE = "Kaskade feat. deadmau5 - I Remember"

# ---------------------------------------------------------------- the chords
# The song is one chord cycle, B A G G F# A G G, and every chord change is on a bar line.
ROSE, LAV, GLASS, AMBER = 0.0, 1 / 3, 2 / 3, 1.0
CYCLE = [ROSE, LAV, GLASS, GLASS, AMBER, LAV, GLASS, GLASS]


def chords(lo, hi, start):
    """Keys for `c`: the colour of the chord at each bar from lo to hi, the cycle starting at `start`."""
    return {str(b): round(CYCLE[(b - start) % 8], 3) for b in range(lo, hi)}


C_A = lambda lo, hi: chords(lo, hi, 2)      # bars 2..95: the cycle starts on 2, 10, 18 ...
C_B = lambda lo, hi: chords(lo, hi, 102)    # bars 102..: the extra bars on G before the sunrise move it by 4

KICK = {"pat": "x", "step": 1, "decay": 0.75, "floor": 0.1}
SOFT = {"pat": "x", "step": 1, "depth": 0.08, "decay": 0.8}
FIG = {"sprite": "remember_two", "y_lo": 45, "y_hi": 165, "x_half": 130}
HEART = {"sprite": "remember_heart", "y_lo": 42, "y_hi": 170, "x_half": 80, "color": "heart@0.7"}

tr = {"v": 1, "show": BASE, "lead": 0,
      "about": "",
      "marks": {"swell": 0, "photo": 2, "dim": 5, "rose": 6, "lav": 10, "climb": 14, "inhale": 17,
                "dawn": 18, "morn": 22, "voice": 34, "hook": 48, "hook2": 50,
                "fall": 66, "rest0": 69, "g1": 70, "rest1": 73, "g2": 74, "rest2": 77, "g3": 78, "rest3": 81,
                "back": 82, "back2": 90, "sing": 96, "sunrise": 102, "high": 110, "day": 118, "peak": 126, "thin": 134,
                "last": 142, "gone": 146, "end": 148},
      "palettes": {
          "sepia": [[0, 0, 0], [34, 16, 5], [100, 54, 22], [176, 116, 66], [236, 196, 148]],
          "dusk": [[255, 120, 110], [240, 110, 150], [200, 105, 200], [130, 110, 235], [80, 170, 210], [90, 225, 190]],
          "chord": [[255, 105, 135], [165, 120, 255], [70, 215, 175], [255, 165, 80]],
          "ghost": [[0, 0, 0], [16, 80, 84], [115, 90, 205], [240, 130, 170], [255, 205, 175], [255, 245, 232]],
          "sun": [[0, 0, 0], [80, 16, 50], [215, 62, 74], [255, 125, 58], [255, 190, 100], [255, 228, 170]],
          "night": [[0, 0, 0], [26, 18, 60], [72, 56, 150], [100, 120, 190], [170, 225, 220]],
          "pastel": {"stops": [[255, 115, 150], [255, 165, 140], [170, 125, 250], [85, 215, 190]], "wrap": True},
          "heart": [[0, 0, 0], [80, 16, 40], [220, 70, 110], [255, 150, 170]],
      },
      "motifs": {
          # the photograph: sepia at its burnt edge
          "vignette": {"fx": "grad", "on": "shell", "axis": "r", "axis2": "a", "scale": 0.98, "wave": "saw", "warp": 0.04,
                       "wscale": 3, "wspeed": 0.02, "lo": 0, "hi": 0.85, "pal": "sepia", "gain": 0.12},
          # the sky behind it: rose at the jaw, lavender on the brow, sea glass at the crown
          "sky": {"fx": "grad", "on": "shell", "axis": "y", "axis2": "x", "scale": 0.98, "wave": "saw", "warp": 0.05,
                  "wscale": 1.2, "wspeed": 0.03, "lo": 0, "hi": 1, "pal": "dusk", "gain": 0.062},
          # the colours of it, drifting across like cloud
          "clouds": {"fx": "grad", "on": "shell", "axis": "x", "axis2": "y", "scale": 1.3, "speed": 0.02, "wave": "saw", "warp": 0.22,
                     "wscale": 1.1, "wspeed": 0.025, "lo": 0, "hi": 1, "pal": "pastel", "gain": 0.075},
          # dust in a projector beam: long-lived, slowly fading
          "dust": {"fx": "sparks", "on": "shell", "rate": 0.75, "life": 6, "loop": 32, "seed": 5, "nbr": 0.7, "c": 0.65,
                   "spread": 0.3, "pal": "sepia", "gain": 0.5},
          "grain": {"fx": "twinkle", "on": "shell", "rate": 0.4, "sharp": 8, "dens": 0.4, "spread": 0.35, "c": 0.45,
                    "pal": "dusk", "gain": {"band": "high", "lo": 0.0, "hi": 0.2}},
          # the ears breathe: inhale into each 4-bar turn, exhale after it, never quite empty
          "breath": {"fx": "sweep", "on": "tubes", "axis": "al", "shape": "tri", "mode": "fill", "speed": 0.0625,
                     "from": 1.3, "to": -0.05, "soft": 0.7, "cgrad": 0.2, "pal": "chord", "gain": 0.25},
          "rimkick": {"fx": "fill", "on": "rims", "pal": "chord", "gain": 0.36, "gate": KICK},
          # one tube sings each chord and fades before the next
          "sing": {"fx": "blades", "on": "tubes", "seq": ["0", "1", "2", "1"], "step": 4, "rise": 0.5, "keep": 0.0,
                   "ctip": 1.0, "gain": 0.55},
          # the picture in the photograph
          "two": {"fx": "preset", "name": "sprite", "on": "shell", "mix": "max",
                  "params": dict(FIG, color="sepia@0.9"), "gain": 0.3},
          "sun": {"fx": "orb", "on": "all", "x": 0, "pal": "sun", "c": 1.0, "cgrad": -0.75, "soft": 300},
          "rays": {"fx": "grad", "on": "face", "axis": "a", "axis2": "r", "scale": 14, "speed": 0.04, "warp": 0.03,
                   "wscale": 1.5, "wspeed": 0.02, "lo": 0.02, "hi": 0.92, "pal": "sun", "gain": 0.12},
          "disc": {"fx": "orb", "on": "shell", "x": 0, "soft": 35, "pal": "sun", "c": 1.0, "cgrad": -0.2, "mix": "max", "gain": 0.46, "gate": {"pat": "x", "step": 1, "decay": 0.85, "floor": 0.7}},
          "shadow": {"fx": "preset", "name": "sprite", "on": "shell", "mix": "over",
                     "params": dict(FIG, color=[26, 15, 9]), "gain": 1.0},
          "ring": {"fx": "sweep", "on": "all", "axis": "r", "shape": "p", "mode": "band", "from": -0.05, "to": 1.25,
                   "width": [0.22, 0.5]},
          "pollen": {"fx": "sparks", "on": "all", "rate": 1.5, "life": 4, "loop": 48, "seed": 19, "nbr": 0.7, "c": 0.8,
                     "spread": 0.2, "pal": "sun", "gain": 0.4},
      },
      "scenes": [], "hits": []}
S = tr["scenes"].append
H = tr["hits"].append

# ---------------------------------------------------------------- the photograph develops
S({"name": "develop", "from": "swell", "to": "photo", "pal": "sepia", "layers": [
    {"use": "vignette", "gain": [0, 0.12], "hi": [0.25, 0.8]},
    {"use": "dust", "gain": [0.0, 0.5]},
    {"fx": "fill", "on": "rims", "c": 0.5, "gain": [0, 0.3]},
    {"fx": "sweep", "on": "tubes", "axis": "al", "shape": "p", "mode": "fill", "from": -0.3, "to": 0.7, "soft": 0.6, "c": 0.6, "cgrad": 0.3, "gain": [0, 0.4]}]})
S({"name": "photo", "from": "photo", "to": "dim", "pal": "sepia", "layers": [
    {"use": "vignette"}, {"use": "dust"},
    {"use": "two", "gain": [0.05, 0.3], "env": {"in": 4}},
    {"fx": "fill", "on": "rims", "c": 0.5, "gain": 0.2},
    {"use": "sing", "seq": ["0", "1", "2"], "c": 0.5, "pal": "sepia"}]})
S({"name": "dim", "from": "dim", "to": "rose", "pal": "sepia", "layers": [
    {"use": "vignette", "gain": [0.12, 0.06]}, {"use": "dust", "gain": 0.35},
    {"use": "two", "gain": [0.3, 0.06]},
    {"fx": "fill", "on": "rims", "c": 0.5, "gain": [0.3, 0.12]},
    {"fx": "sweep", "on": "tubes", "axis": "al", "shape": "p", "mode": "fill", "from": 1.0, "to": -0.3, "soft": 0.5, "c": 0.5, "cgrad": 0.3, "gain": 0.35}]})
S({"name": "rose", "from": "rose", "to": "lav", "pal": "sepia", "layers": [
    {"use": "vignette", "gain": 0.09}, {"use": "sky", "gain": [0.012, 0.045]},
    {"use": "dust"},
    {"fx": "fill", "on": "rims", "pal": "chord", "c": C_A(6, 10), "gain": 0.15},
    {"use": "sing", "seq": ["0", "1", "2", "2"], "pal": "chord", "c": C_A(6, 10), "ctip": 0.0, "gain": 0.5}]})
S({"name": "lav", "from": "lav", "to": "climb", "pal": "dusk", "layers": [
    {"use": "vignette", "gain": [0.08, 0.04]}, {"use": "sky", "gain": [0.045, 0.065]},
    {"use": "grain"},
    {"fx": "fill", "on": "rims", "pal": "chord", "c": C_A(10, 14), "gain": 0.18},
    {"use": "sing", "seq": ["0", "1", "2", "2"], "pal": "chord", "c": C_A(10, 14), "ctip": 0.33, "gain": 0.55}]})
# the climb: the sky lifts up the shell and the ears fill for three bars ...
S({"name": "climb", "from": "climb", "to": "inhale", "pal": "dusk", "layers": [
    {"use": "sky", "gain": [0.065, 0.085]}, {"use": "grain", "gain": {"band": "high", "lo": 0, "hi": 0.3}},
    {"fx": "sweep", "on": "shell", "axis": "y", "shape": "p", "mode": "band", "from": -0.1, "to": 0.75, "width": 0.3, "pal": "sun", "c": 0.6, "gain": [0.04, 0.26]},
    {"fx": "sweep", "on": "tubes", "axis": "al", "shape": "p", "mode": "fill", "from": -0.2, "to": 0.9, "soft": 0.5, "pal": "chord", "c": C_A(14, 17), "cgrad": 0.1, "gain": [0.24, 0.36]},
    {"fx": "fill", "on": "rims", "pal": "chord", "c": C_A(14, 17), "gain": 0.25}]})
# ... and in the bar with no bass everything goes up into the crown
S({"name": "inhale", "from": "inhale", "to": "dawn", "pal": "dusk", "layers": [
    {"use": "sky", "gain": [0.075, 0.015]},
    {"fx": "sweep", "on": "shell", "axis": "y", "shape": "p", "mode": "band", "from": 0.72, "to": 1.05, "width": 0.25, "pal": "sun", "c": 0.75, "gain": [0.28, 0.4]},
    {"fx": "sweep", "on": "tubes", "axis": "al", "shape": "p", "mode": "fill", "from": 0.9, "to": 1.3, "soft": 0.5, "pal": "ghost", "c": 0.75, "cgrad": 0.2, "gain": [0.24, 0.3]}]})

# ---------------------------------------------------------------- first light, on the first kick
S({"name": "dawn", "from": "dawn", "to": "morn", "pal": "dusk", "pump": SOFT, "layers": [
    {"use": "sky", "gain": [0.04, 0.062]},
    {"use": "sun", "y": [-330, -130], "rad": 340, "gain": [0.18, 0.09]},
    {"use": "breath", "c": C_A(18, 22), "gain": 0.28},
    {"use": "rimkick", "c": C_A(18, 22)},
    {"use": "grain"}]})
MORN = [{"use": "sky"},
        {"use": "sun", "y": [-130, -70], "rad": 340, "gain": [0.085, 0.095]},
        {"use": "breath", "c": C_A(22, 34)},
        {"use": "rimkick", "c": C_A(22, 34)},
        {"use": "grain"},
        {"use": "dust", "pal": "ghost", "c": 0.55, "spread": 0.2, "gain": 0.3}]
S({"name": "morning", "from": "morn", "to": "voice", "pal": "dusk", "pump": SOFT, "layers": MORN})

# ---------------------------------------------------------------- the voice comes in, and each line is a pale light
VOICE = json.loads(json.dumps(MORN))
VOICE[0]["gain"] = 0.07
VOICE[1] = {"use": "sun", "y": [-70, -30], "rad": 340, "gain": [0.095, 0.11]}
VOICE[2]["c"] = C_A(34, 48)
VOICE[3]["c"] = C_A(34, 48)
S({"name": "voice", "from": "voice", "to": "hook", "pal": "dusk", "pump": SOFT, "layers": VOICE})

# ---------------------------------------------------------------- the hook: the picture in full colour
# the long note starts it: two bars of the ears breathing in to the turn of the chords on bar 50
S({"name": "longnote", "from": "hook", "to": "hook2", "pal": "pastel", "pump": SOFT, "layers": [
    {"use": "clouds", "gain": [0.04, 0.075]},
    {"use": "breath", "shape": "p", "from": -0.05, "to": 1.3, "c": C_A(48, 50), "gain": 0.28},
    {"use": "rimkick", "c": C_A(48, 50), "gain": 0.4},
    {"use": "pollen", "pal": "ghost", "c": 0.7, "gain": 0.3}]})
HOOK = [{"use": "clouds"},
        {"use": "breath", "c": C_A(50, 66), "gain": 0.26},
        {"use": "rimkick", "c": C_A(50, 66), "gain": 0.4},
        {"use": "sing", "seq": ["012"], "step": 8, "side": "alt", "rise": 0.5, "c": C_A(50, 66), "pal": "chord", "gain": 0.14},
        {"use": "pollen", "pal": "ghost", "c": 0.7, "gain": 0.3}]
S({"name": "hook", "from": "hook2", "to": "fall", "pal": "pastel", "pump": SOFT, "layers": HOOK})

# ---------------------------------------------------------------- the kick stops: the colour drains back to sepia
S({"name": "fall", "from": "fall", "to": "rest0", "pal": "sepia", "layers": [
    {"use": "clouds", "gain": [0.075, 0.0]},
    {"use": "vignette", "gain": [0.0, 0.12]},
    {"fx": "sweep", "on": "tubes", "axis": "al", "shape": "p", "mode": "fill", "from": 1.3, "to": -0.3, "soft": 0.6, "pal": "chord", "c": C_A(66, 69), "cgrad": 0.1, "gain": 0.28},
    {"fx": "fill", "on": "rims", "c": 0.5, "gain": [0.2, 0.03]},
    {"use": "dust"}]})
REST = [{"use": "dust", "gain": 0.3, "rate": 0.5}, {"use": "vignette", "gain": 0.03, "hi": 0.5}]
S({"name": "rest0", "from": "rest0", "to": "g1", "pal": "sepia", "layers": REST})


# three half-remembered flickers, each one a side, and a bar of almost nothing after each
def flicker(x, ear, keys, tint):
    return [{"fx": "orb", "on": "shell", "x": x, "y": 50, "rad": 250, "soft": 190, "pal": "sepia", "c": 0.98, "cgrad": -0.6, "gain": [0.36, 0.02]},
            {"fx": "orb", "on": "shell", "x": x, "y": 50, "rad": 170, "soft": 130, "pal": "ghost", "c": tint, "gain": [0.16, 0.0]},
            {"fx": "sweep", "on": ear, "axis": "al", "shape": "p", "mode": "fill", "from": 1.3, "to": -0.2, "soft": 0.6, "pal": "chord", "c": keys, "cgrad": 0.1, "gain": 0.42},
            {"use": "dust", "gain": 0.3}]


S({"name": "left", "from": "g1", "to": "rest1", "pal": "sepia", "layers": flicker(-130, "tubes1", C_A(70, 73), 0.6)})
S({"name": "rest1", "from": "rest1", "to": "g2", "pal": "sepia", "layers": REST})
S({"name": "right", "from": "g2", "to": "rest2", "pal": "sepia", "layers": flicker(130, "tubes2", C_A(74, 77), 0.4)})
S({"name": "rest2", "from": "rest2", "to": "g3", "pal": "sepia", "layers": REST})
S({"name": "both", "from": "g3", "to": "rest3", "pal": "sepia", "layers": [
    {"use": "vignette", "gain": [0.16, 0.025]},
    {"use": "two", "params": {"color": "sepia@1.0"}, "gain": [0.55, 0.22]},
    {"fx": "sweep", "on": "tubes", "axis": "al", "shape": "p", "mode": "fill", "from": 1.3, "to": -0.2, "soft": 0.6, "pal": "chord", "c": C_A(78, 81), "cgrad": 0.1, "gain": 0.36},
    {"use": "dust", "gain": 0.3}]})
# the bar of silence: only the afterimage of the two of them, in the complementary colour
S({"name": "afterimage", "from": "rest3", "to": "back", "pal": "ghost", "layers": [
    {"use": "two", "params": {"color": "ghost@0.2"}, "gain": [0.8, 0.2]}]})

# ---------------------------------------------------------------- blue hour: the bass comes back, no kick yet
STARS = {"fx": "twinkle", "on": "shell", "rate": 0.25, "sharp": 10, "dens": 0.5, "spread": 0.15, "c": 0.85, "pal": "night", "gain": 0.32}
NIGHT = {"fx": "grad", "on": "shell", "axis": "y", "axis2": "x", "scale": 0.98, "wave": "saw", "warp": 0.05, "wscale": 1.2, "wspeed": 0.03, "lo": 0.15, "hi": 0.65, "pal": "night", "gain": 0.11}
S({"name": "blue", "from": "back", "to": "back2", "pal": "night", "layers": [
    NIGHT, STARS,
    {"use": "breath", "on": "tubes1", "pal": "chord", "c": C_A(82, 90), "gain": 0.24},
    {"use": "breath", "on": "tubes2", "pal": "chord", "c": C_A(82, 90), "from": -0.05, "to": 1.3, "gain": 0.24},
    {"fx": "fill", "on": "rims", "pal": "night", "c": 0.7, "gain": {"band": "bass", "lo": 0.03, "hi": 0.28}}]})
S({"name": "blue2", "from": "back2", "to": "sing", "pal": "night", "layers": [
    dict(NIGHT, gain=[0.11, 0.08]), dict(STARS, gain=[0.32, 0.45], rate=0.35),
    {"fx": "orb", "on": "shell", "x": 0, "y": [-420, -300], "rad": 340, "soft": 300, "pal": "sun", "c": 0.8, "cgrad": -0.6, "gain": [0.0, 0.14]},
    {"use": "breath", "pal": "chord", "c": C_A(90, 96), "gain": [0.22, 0.28]},
    {"fx": "fill", "on": "rims", "pal": "night", "c": 0.75, "gain": {"band": "bass", "lo": 0.03, "hi": 0.3}}]})
# the title crosses on the voice's long note; the ears take six bars to breathe in
S({"name": "sing", "from": "sing", "to": "sunrise", "pal": "night", "layers": [
    dict(NIGHT, gain=[0.06, 0.015], hi=0.4),
    dict(STARS, gain=[0.3, 0.05]),
    {"fx": "orb", "on": "shell", "x": 0, "y": [-300, -230], "rad": 340, "soft": 300, "pal": "sun", "c": 0.9, "cgrad": -0.6, "gain": [0.14, 0.26]},
    {"fx": "sweep", "on": "tubes", "axis": "al", "shape": "p", "mode": "fill", "from": -0.3, "to": 1.25, "soft": 0.6, "pal": "sun", "c": 0.45, "cgrad": 0.5, "gain": [0.22, 0.34]},
    {"fx": "fill", "on": "rims", "pal": "sun", "c": 0.6, "gain": [0.08, 0.3]}]})

# ---------------------------------------------------------------- the sunrise, through everything, on the kick
S({"name": "sunrise", "from": "sunrise", "to": "high", "pal": "sun", "pump": SOFT, "layers": [
    {"use": "sun", "y": [-230, -60], "rad": [340, 360], "gain": [0.16, 0.065]},
    {"use": "rays", "gain": [0.035, 0.12]},
    {"use": "disc", "y": [-50, 48], "rad": [70, 90]},
    {"use": "breath", "pal": "sun", "c": 0.55, "cgrad": 0.4, "gain": 0.25},
    {"use": "rimkick", "pal": "sun", "c": 0.8}]})
S({"name": "high", "from": "high", "to": "day", "pal": "sun", "pump": SOFT, "layers": [
    {"use": "sun", "y": -60, "rad": 360, "gain": 0.065},
    {"use": "rays"},
    {"use": "disc", "y": [48, 58], "rad": 90},
    {"use": "breath", "c": C_B(110, 118)},
    {"use": "rimkick", "c": C_B(110, 118)},
    {"use": "pollen", "gain": 0.3}]})
# day: the sun climbs and the colours of the hook come back into its rays
DAY = [{"use": "sun", "y": -60, "rad": 360, "gain": 0.06},
       {"use": "rays", "gain": 0.105},
       {"use": "disc", "y": [58, 66], "rad": 90, "gain": 0.42},
       {"use": "clouds", "gain": [0.008, 0.035]},
       {"use": "breath", "c": C_B(118, 126)},
       {"use": "rimkick", "c": C_B(118, 126)}]
S({"name": "day", "from": "day", "to": "peak", "pal": "sun", "pump": SOFT, "layers": DAY})
PEAK = [{"use": "sun", "y": -60, "rad": 360, "gain": 0.055},
        {"use": "rays", "pal": "pastel", "lo": 0.0, "hi": 1.0, "wave": "saw", "scale": 3, "speed": 0.03, "gain": 0.1},
        {"use": "rays", "gain": 0.05},
        {"use": "disc", "y": [66, 72], "rad": 90, "gain": 0.4},
        {"use": "breath", "c": C_B(126, 134)},
        {"use": "rimkick", "c": C_B(126, 134)}]
S({"name": "peak", "from": "peak", "to": "thin", "pal": "sun", "pump": SOFT, "layers": PEAK})

# ---------------------------------------------------------------- the photograph yellows
S({"name": "yellow", "from": "thin", "to": "last", "pal": "sepia", "pump": SOFT, "layers": [
    {"use": "sun", "y": [-60, -200], "rad": 360, "gain": [0.06, 0.0]},
    {"use": "vignette", "gain": [0.03, 0.12]},
    {"use": "dust", "gain": [0.3, 0.55]},
    {"use": "two", "gain": [-0.1, 0.42]},
    {"use": "breath", "pal": "sepia", "c": 0.45, "cgrad": 0.5, "gain": [0.28, 0.22]},
    {"fx": "fill", "on": "rims", "c": 0.6, "gain": [0.36, 0.2], "gate": KICK}]})

# ---------------------------------------------------------------- the last line, the ears go out, and the heart
S({"name": "last", "from": "last", "to": "gone", "pal": "sepia", "layers": [
    {"use": "vignette", "gain": [0.12, 0.03]},
    {"use": "two", "gain": [0.42, -0.1]},
    {"fx": "preset", "name": "sprite", "on": "shell", "mix": "max", "params": HEART, "gain": [-0.1, 0.42]},
    {"fx": "fill", "on": "tube0", "c": 0.6, "gain": {"last": 0.2, "143": 0}},
    {"fx": "fill", "on": "tube1", "c": 0.6, "gain": {"last": 0.2, "144": 0}},
    {"fx": "fill", "on": "tube2", "c": 0.6, "gain": {"last": 0.2, "145": 0}}]})
S({"name": "gone", "from": "gone", "to": "end", "pal": "heart", "layers": [
    {"fx": "preset", "name": "sprite", "on": "shell", "mix": "max", "params": HEART, "gain": [0.42, 0.0]}]})


# ---------------------------------------------------------------- hits
def orbit(at, travel, side, th0, th1, lag=0.0, wx=(178, 150), wy=(150, 150)):
    """The orb's values for a path round the shell's edge from angle th0 to th1 over `travel` beats, `lag` beats behind."""
    w = (th1 - th0) / 360.0 / travel
    yp = th0 / 360.0 - (at * 4 + lag) * w
    xp = yp + 0.25
    return {"x": 0, "y": 30, "wx": [side * wx[0], side * wx[1]], "wy": [wy[0], wy[1]], "xf": round(w, 6), "yf": round(w, 6),
            "xp": round(xp, 6), "yp": round(yp, 6)}


def light(at, beats, side=1, gain=(0.2, 0.62), th0=-70.0, th1=38.0, rad=(45, 70), c=(0.95, 0.45), ear=True):
    """A pale light rising round the edge of the shell while a line is sung, with its afterimage behind it in the
    complementary colour; as it dissolves it goes up into the ear on its side."""
    travel = beats * 0.72
    tubes = "tubes2" if side > 0 else "tubes1"
    out = [dict(orbit(at, travel, side, th0, th1), fx="orb", on="shell", rad=list(rad), soft=40, pal="ghost", c=list(c), gain=list(gain),
                env={"in": 1, "out": beats * 0.45}),
           dict(orbit(at, travel, side, th0, th1, lag=2.0), fx="orb", on="shell", rad=[rad[0] + 25, rad[1] + 40], soft=60, pal="ghost", c=[0.42, 0.18], gain=0.42,
                env={"in": 2, "out": beats * 0.45})]
    if ear:
        out.append({"fx": "sweep", "on": tubes, "axis": "al", "shape": "p", "mode": "band", "from": -1.7, "to": 1.15, "width": 0.3, "pal": "ghost", "c": 0.9, "cgrad": -0.3, "gain": [0.6, 0.45]})
    return out


def ring(c, gain=0.4, pal="chord"):
    return {"use": "ring", "pal": pal, "c": c, "gain": [gain, 0]}


# chords on the turn of each phrase leave slow rings
for at, c, pal, g in ((6, 0.75, "ghost", 0.3), (10, 0.5, "ghost", 0.3), (14, 0.75, "ghost", 0.3)):
    H({"name": "ring %d" % at, "at": at, "beats": 12, "layers": [ring(c, g, pal)]})
H({"name": "first light", "at": "dawn", "beats": 14, "layers": [ring(0.85, 0.42, "sun"), {"fx": "fill", "on": "shell", "pal": "sun", "c": 0.6, "gain": [0.1, 0.0]}]})
for i, at in enumerate((22, 26, 30, 34, 38, 42)):
    H({"name": "ring %d" % at, "at": at, "beats": 12, "layers": [ring([ROSE, LAV, GLASS, AMBER][i % 4], 0.24)]})
H({"name": "ring 46", "at": 46, "beats": 4, "layers": [ring(AMBER, 0.24)]})
# the first sung lines
for i, at in enumerate((35, 39, 43)):
    H({"name": "line %d" % at, "at": at, "beats": 12, "layers": light(at, 12, 1 if i % 2 == 0 else -1)})
# bar 47 lifts into the long note, which hangs at the crown and spreads for two bars
H({"name": "line 47", "at": 47, "beats": 4, "layers": light(47, 5.5, -1, ear=False)})
H({"name": "long note", "at": "hook", "beats": 8, "layers": [
    {"fx": "orb", "on": "shell", "x": 0, "y": [90, 175], "rad": [70, 170], "soft": 110, "pal": "ghost", "c": [0.98, 0.62], "gain": [0.5, 0.1], "env": {"in": 1}},
    ring(0.85, 0.3, "sun")]})
for i, at in enumerate(range(50, 66, 2)):
    H({"name": "line %d" % at, "at": at, "beats": 8, "layers": light(at, 8, 1 if i % 2 else -1, gain=(0.18, 0.55))})
for at in (50, 54, 58, 62):
    H({"name": "ring %d" % at, "at": at, "beats": 12, "layers": [ring(0.62, 0.2, "ghost")]})
H({"name": "last sunset", "at": "fall", "beats": 12, "layers": [ring(0.75, 0.4, "sun")]})
for at, b in ((82, 12), (86, 12), (90, 12), (94, 8)):
    H({"name": "ring %d" % at, "at": at, "beats": b, "layers": [ring(0.9, 0.3 if at == 82 else 0.22, "night")]})
for at, side in ((83, 1), (87, -1), (91, 1), (95, -1)):
    H({"name": "line %d" % at, "at": at, "beats": 4 if at == 95 else 12, "layers": light(at, 12, side, gain=(0.18, 0.55))[:2] if at == 95 else light(at, 12, side, gain=(0.18, 0.55))})
H({"name": "I REMEMBER", "at": "sing", "beats": 24, "layers": [
    {"fx": "preset", "name": "text", "on": "face", "fit": True, "mix": "over", "env": {"in": 2, "out": 2},
     "params": {"text": "I REMEMBER", "color": [255, 226, 190], "y_lo": 54, "y_hi": 166}, "gain": 0.42}]})
H({"name": "sun", "at": "sunrise", "beats": 16, "layers": [ring(0.9, 0.5, "sun"), {"fx": "fill", "on": "shell", "pal": "sun", "c": 0.7, "gain": [0.16, 0.0]}]})
for at, side in ((110, 1), (118, -1), (126, 1)):
    H({"name": "line %d" % at, "at": at, "beats": 12, "layers": light(at, 12, side, gain=(0.18, 0.55))})
    H({"name": "ring %d" % (at + 4), "at": at + 4, "beats": 12, "layers": [ring(ROSE if side > 0 else LAV, 0.22)]})
H({"name": "line 102", "at": 102.5, "beats": 12, "layers": light(102.5, 12, 1, gain=(0.18, 0.55))})
H({"name": "ring 106", "at": 106, "beats": 12, "layers": [ring(0.85, 0.22, "sun")]})
H({"name": "ring 134", "at": "thin", "beats": 16, "layers": [ring(0.8, 0.26, "sepia")]})
H({"name": "ring 138", "at": 138, "beats": 14, "layers": [ring(0.7, 0.18, "sepia")]})
H({"name": "last line", "at": 141.75, "beats": 13, "layers": light(141.75, 13, 1, gain=(0.18, 0.55))})

# ---------------------------------------------------------------- write
tr["about"] = (
    "Bars of a measured grid, shows/scenes/Kaskade feat. deadmau5 - I Remember.beats: bar b starts at 1.590 + 1.875 b seconds, 128.000 BPM, flat to 5 ms "
    "across the song, 151 bars. The bar line is where the chords turn: the song is one cycle, B A G G F# A G G, every change on a bar, starting on bar 2, "
    "2 + 8n until the six bars on G before bar 102, 102 + 8n after them. The kick lands on bar 18 and again on bar 102, stops on 66 and 142. "
    "MEMORY, the most tender show of the set. A photograph develops from dark in sepia, burnt at its edge, with dust in the light and, slowly, two small figures "
    "holding hands, drawn on the dome where LEDs exist. Colour bleeds in: dusk, rose at the jaw, lavender on the brow, sea glass at the crown. "
    "On the first kick there is first light, a warm bloom on the shell and a slow ring going out through head and ears. Every four bars, on the turn of the chords, "
    "another ring goes out and dims. The ears breathe and never strobe: they inhale into each turn and exhale after it, and their colour is the chord, "
    "rose for B, lavender for A, sea glass for G, amber for F#, so the ears play the progression while the shell keeps time only with a soft pump and the rims with the kick. "
    "From bar 35 each sung line is a single pale light rising round the edge of the shell, its afterimage behind it in the complementary colour, and as it dissolves it goes up "
    "into the ear on its side. The long note on bar 48 hangs at the crown, and the hook is the picture in full colour, drifting like cloud. "
    "When the kick stops on 66 the colour drains back to sepia and the memory breaks up: three flickers, one side, the other side, then both with the two figures, each one "
    "followed by a bar of almost nothing, and in the last silent bar only their afterimage is left, in teal. The bass comes back on 82 at blue hour, stars and the ears breathing "
    "in turn. The title crosses once, slowly, on the voice's long note from 96 to 102, set high enough on the dome for its letters to land on LEDs, while the ears take six bars to breathe in. "
    "Bar 102 is the sunrise rather than an impact: a warm bloom on the returning kick, then over eight bars a half sun rises to the dome's horizon, its rays fanning across the brow. "
    "It stays through the second half and the colours of the hook come back into its rays. On 134 the music thins and the photograph yellows, with the two figures back in it. "
    "On 142 the kick stops for good, one last pale light rises, the tubes go out one at a time, the figures fade and a faint heart develops in their place, the only time it appears, "
    "and it outlasts the music by two bars. Text is the title only. Nothing on the shell pulses faster than a beat, and scenes are kept under the shell's budget rather than raising any limit."
)
save(tr, os.path.join("shows", "scenes", BASE + ".scene.json"))
