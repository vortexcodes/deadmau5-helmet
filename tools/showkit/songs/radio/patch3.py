import os
p=os.environ["W"]+"/write_treatment.py"
s=open(p).read()
def rep(a,b):
    global s
    assert a in s, a[:70]
    s=s.replace(a,b,1)
# needle pieces per half beat, so every waypoint lands exactly
rep('''    n = int(round((b1 - b0) * 4))
    fr, to = {}, {}
    for k in range(n):
        bb = b0 + k / 4.0
        fr[str(bb)] = round(at(bb), 4)
        to[str(bb)] = round(at(bb + 0.25), 4)
    return fr, to, at''','''    n = int(round((b1 - b0) * 8))
    fr, to = {}, {}
    for k in range(n):
        bb = b0 + k / 8.0
        fr[str(bb)] = round(at(bb), 4)
        to[str(bb)] = round(at(bb + 0.125), 4)
    return fr, to, at''')
rep('''"shape": "saw", "speed": 1, "mode": "band", "width": width,''','''"shape": "saw", "speed": 2, "mode": "band", "width": width,''')
rep('''    n = int(round((b1 - b0) * 4))
    keys = {}
    for k in range(n):
        bb = b0 + k / 4.0
        d = min(abs(at(bb + 0.125) - 0.25) / 0.16, 1.0)''','''    n = int(round((b1 - b0) * 8))
    keys = {}
    for k in range(n):
        bb = b0 + k / 8.0
        d = min(abs(at(bb + 0.0625) - 0.25) / 0.16, 1.0)''')
# inward rings get a palette whose tail trails outward
rep('''def rings2(beats, gain, per=1, cg=6.0, rad=440, soft=260, on="shell+rims", inward=False, x=0, y=170, gate=True):''','''def rings2(beats, gain, per=1, cg=6.0, rad=440, soft=260, on="shell+rims", inward=False, x=0, y=170, gate=True):
    pal = "rings_in" if inward else "rings_tm"''')
rep('''"pal": "rings_tm",
         "c": [c0 + n, c0] if inward''','''"pal": pal,
         "c": [c0 + n, c0] if inward''')
rep('''TEAL, MAG = [0, 255, 130], [255, 0, 110]''','''def ringpal_in(rgb):
    """The same ring coming home: bright edge inside, the tail behind it toward the outside."""
    r = [int(x) for x in rgb]
    sc = lambda k: [int(x * k) for x in r]
    return {"stops": [[0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], r, sc(0.3), sc(0.06), [0, 0, 0]], "wrap": True}
TEAL, MAG = [0, 255, 130], [255, 0, 110]''')
rep(''' "rings_tm": {"stops": ringpal(TEAL)["stops"] + ringpal(MAG)["stops"], "wrap": True},''',''' "rings_tm": {"stops": ringpal(TEAL)["stops"] + ringpal(MAG)["stops"], "wrap": True},
 "rings_in": {"stops": ringpal_in(TEAL)["stops"] + ringpal_in(MAG)["stops"], "wrap": True},''')
# the second drop's sign: quieter ears while the rims go white, so the sign keeps its light
rep('''def sign_scene(name, a, b, pump=PUMP, gain=0.62):
    S({"name": name, "from": a, "to": b, "pal": "neon", "pump": pump, "layers": [SIGNL(gain=gain), VU_KICK("tubes1"), VU_PUMP("tubes2"), PEAK(0.5)]})''','''def sign_scene(name, a, b, pump=PUMP, gain=0.62, kick=0.5, chords=EARG):
    S({"name": name, "from": a, "to": b, "pal": "neon", "pump": pump, "layers": [SIGNL(gain=gain), VU_KICK("tubes1", kick), VU_PUMP("tubes2", chords), PEAK(0.5)]})''')
rep('''sign_scene("ON AIR 2", "drop2", "rings2", pump=HARD)''','''sign_scene("ON AIR 2", "drop2", "rings2", pump=HARD, kick=0.36, chords=0.3)''')
rep('''sign_scene("ON AIR", "drop", "rings")''','''sign_scene("ON AIR", "drop", "rings", kick=0.4, chords=0.34)''')
rep('''sign_scene("ON AIR 3", "drop2b", "drop2b+1", pump=HARD)''','''sign_scene("ON AIR 3", "drop2b", "drop2b+1", pump=HARD, kick=0.4, chords=0.34)''')
rep('''WHITERIM = {"fx": "fill", "on": "rims", "pal": "white", "c": 1, "gain": [1.0, 0]}''','''WHITERIM = {"fx": "fill", "on": "rims", "pal": "white", "c": 1, "gain": [0.8, 0]}''')
# the about
rep('''ABOUT = "(draft)"''','''ABOUT = ("Bars of a measured grid, shows/scenes/deadmau5 - Some Chords (Radio Edit).beats: bar b starts at 0.124 + 1.875 b seconds (exactly 128 BPM), 112 bars, "
 "and at bar 72 the radio edit is spliced, so the music comes back 32 ms late and the grid holds still for it. The bar line is where the phrases turn, with the drop's first kick on step 0 of bar 28. "
 "An old radio being tuned at night. The dome is the half-moon dial of a tube set, amber backlight and radial ticks, pivoting at the bottom of the forehead; the jaw is its speaker; the ears are its VU meters. "
 "Bars 0 to 8 are the filter opening on the bass chords, so the show is static over everything with the needle hunting the dial, moving on each chord change, the static thinning each time it crosses the station, the meters climbing by themselves because the track's own mid and high bands are rising. "
 "At bar 8 it locks: the static is gone in one frame and the needle now reads the level. At 16 the kick lands and the signal itself appears, a teal sine across the dome whose height is the track's mid band. "
 "At 24 the drums pull out, so the sine flattens and static creeps back, one dark beat under the noise burst at 27.75 with only a red beacon lit on top of the head, then ON and AIR flip in magenta, two beats each, as a sign rather than a lyric. "
 "The drop is the transmitter: the needle stands up as the mast, the beacon blinks and a ring leaves on every beat, through the dome and down to the jaw, teal, then teal and magenta in turn; "
 "the left ear plays the kick and the right ear plays the chords pumping up between kicks. At 45 the transmitters move into the ears and their rings cross on the dome; at 53 the whole radio runs at once, the kick throwing the needle. "
 "The fill at 59 lets the needle slip off the station, the sound dies, and the title crosses once in amber as the sign-off while the static comes back. At 64 the chords return and it tunes again, a different path, this time with the sine glimmering through whenever the needle crosses the station, "
 "until the edit's hard cut at 72 locks it: two sines now, teal and magenta, braided. The second drop opens with the rims white, the one white moment, the rings go at double speed, come home inward at 101 and go out again at 104. "
 "At 107 the kick stops and the needle walks down the falling notes, and from 108 the set is switched off: the meters fall with the tail and the dial lamp cools to a point and goes out. Tuned through the real guard: shell inside its 300 mA, ears kept under what would make the governor shed the shell.")''')
open(p,"w").write(s)
