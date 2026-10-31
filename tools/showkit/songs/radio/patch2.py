import os
p=os.environ["W"]+"/write_treatment.py"
s=open(p).read()
def rep(a,b,cnt=1):
    global s
    assert a in s, a[:60]
    s=s.replace(a,b) if cnt==0 else s.replace(a,b,cnt)
# the sign: a plainer I
rep('''  "...XX...XXX.XXXX.",
  "..XXXX...X..XX.XX",
  "..XX.XX..X..XX.XX",
  ".XX..XX..X..XXXX.",
  ".XXXXXX..X..XX.XX",
  ".XX..XX..X..XX.XX",
  ".XX..XX.XXX.XX.XX"],''','''  "...XX....XX.XXXX.",
  "..XXXX...XX.XX.XX",
  "..XX.XX..XX.XX.XX",
  ".XX..XX..XX.XXXX.",
  ".XXXXXX..XX.XX.XX",
  ".XX..XX..XX.XX.XX",
  ".XX..XX..XX.XX.XX"],''')
# dial face: lamp and ticks in one layer, for the scenes that are out of layers
rep('''STATIC = lambda gain''','''DIAL = lambda gain, scale=16: {"fx": "grad", "on": "face", "axis": "a", "axis2": "r", "scale": scale, "pal": "dialface", "gain": gain}
STATIC = lambda gain''')
rep('''"tick": [[0, 0, 0], [0, 0, 0], [255, 90, 8]],''','''"tick": [[0, 0, 0], [0, 0, 0], [255, 90, 8]],
 "dialface": [[60, 13, 0], [60, 13, 0], [255, 90, 8]],''')
rep(''' "rings_w": ringpal([255, 255, 255]),''',''' "rings_a": ringpal([255, 70, 0]),''')
# tuning: static softer on the shell than the needle, shared with the ears
rep('''LEVEL1 = lambda b: 0.5 - 0.02 * max(b, 0)
S({"name": "tuning", "from": -0.125, "to": "lock", "pal": "dial", "layers": [
  STATIC(static_keys(HUNT1, -0.125, 8, LEVEL1)),
  LAMP([0.05, 0.12]), TICKS([0.05, 0.12]),
  needle(HUNT1, -0.125, 8, 0.85),''','''LEVEL1 = lambda b: 0.34 - 0.012 * max(b, 0)
EARSTATIC1 = lambda b: 0.52 - 0.03 * max(b, 0)
S({"name": "tuning", "from": -0.125, "to": "lock", "pal": "dial", "layers": [
  STATIC(static_keys(HUNT1, -0.125, 8, LEVEL1), on="shell"),
  STATIC(static_keys(HUNT1, -0.125, 8, EARSTATIC1), on="ears"),
  DIAL([0.12, 0.3]),
  needle(HUNT1, -0.125, 8, 0.9),''')
# retune: the station glimmers through when the needle crosses it
rep('''LEVEL2 = lambda b: 0.46 - 0.02 * (b - 64)
S({"name": "retune", "from": "retune", "to": "lock2", "pal": "dial", "layers": [
  STATIC(static_keys(HUNT2, 64, 72, LEVEL2)),
  LAMP([0.05, 0.14]), TICKS([0.05, 0.14]),
  needle(HUNT2, 64, 72, 0.85),''','''LEVEL2 = lambda b: 0.36 - 0.015 * (b - 64)
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
  WAVE("wave_t", band("mid", 0.02, 0.3), glimmer(HUNT2, 64, 72, 66)),''')
# sign-off softer under the title
rep('''  LAMP([0.12, 0.03]),
  STATIC([0.0, 0.22], rate=5),''','''  LAMP([0.09, 0.02]),
  STATIC([0.0, 0.16], rate=5),''')
rep('''"color": [255, 80, 0]''','''"color": [255, 50, 0]''')
# the fill bar: rim hits on its own stutter
rep('''  LAMP([0.25, 0.16]), TICKS(0.12), needle(FALL1, 59, 60, 0.9),
  vu("tubes1", band("mid", -1.0, 1.0), 0.32), vu("tubes2", band("high", -1.0, 1.1), 0.32)]})''','''  LAMP([0.25, 0.16]), TICKS(0.12), needle(FALL1, 59, 60, 0.9),
  vu("tubes1", band("mid", -1.0, 1.0), 0.32), vu("tubes2", band("high", -1.0, 1.1), 0.32),
  PEAK(0.6, c=0.8, pat="x...x..x...x....")]})''')
# amber ring per bar in the last verse, not gray
rep('''rings(16, 0.3, pal="rings_w", per=4, cg=1.5, gate=False)''','''rings(16, 0.32, pal="rings_a", per=4, cg=1.5, gate=False)''')
# the shock: rims only, white once
rep('''SHOCK = lambda pal, gain, beats=2: {"fx": "orb", "on": "all", "x": 0, "y": 170, "rad": 460, "soft": 160, "pal": pal, "c": [0.5, -0.5], "cgrad": 1.0, "gain": gain}
''','''WHITERIM = {"fx": "fill", "on": "rims", "pal": "white", "c": 1, "gain": [1.0, 0]}
''')
rep('''HITF("SHOCK", "drop2", 2, [SHOCK("rings_w", 0.8), RIMFLASH(0.9, c=0.8)]),''','''HITF("WHITE", "drop2", 2, [WHITERIM]),''')
rep(''' "sign": [[255, 0, 40], [255, 0, 50], [255, 30, 80]]},''',''' "sign": [[255, 0, 40], [255, 0, 50], [255, 30, 80]],
 "white": [[255, 200, 120], [255, 240, 220], [255, 255, 255]]},''')
# small accents where the kick comes in
rep('''  HITF("BEACON", "gap", 1, [BEACONUP]),''','''  HITF("SONG", "song", 2, [RIMFLASH(0.7, c=0.0)]),
  HITF("BEACON", "gap", 1, [BEACONUP]),''')
rep('''  HITF("BEACON 2", "gap2", 1, [BEACONUP]),''','''  HITF("SONG 2", "song2", 2, [RIMFLASH(0.7, c=0.8)]),
  HITF("BEACON 2", "gap2", 1, [BEACONUP]),''')
open(p,"w").write(s)
