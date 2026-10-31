p="tools/showkit/work/chords/gen.py"
s=open(p).read()
def rep(a,b,count=1):
    global s
    assert a in s, a
    s=s.replace(a,b) if count==0 else s.replace(a,b,count)
# white, once: the window itself is out for the first half beat
rep('H("WHITE", "blaze", 2, [blow(0.5, 0.16, pal="white"), ring(0.5, 1.0, pal="white"), {"fx": "fill", "on": "rims", "pal": "white", "c": 0, "gain": [0.25, 0]}])',
    'H("WHITE", "blaze", 2, [blow(0.5, 0.15, pal="white"), dict(ring(0.5, 1.0, pal="white"), width=0.2), {"fx": "fill", "on": "shell+rims", "pal": "white", "c": 0, "gain": [0.09, 0]}])')
rep('''blaze("blaze", 164, 172, *stains(164, 172), chirp(164, 172))''','''def after_white(L, g):
    L["gain"] = dict(L["gain"], **{"164": 0, "164.125": g})
    return L
r_, g_ = stains(164, 172)
blaze("blaze", 164, 172, after_white(r_, 0.28), after_white(g_, 0.28), after_white(chirp(164, 172), 0.42))
_L = tr["scenes"][-1]["layers"][0]
_L["gain"] = {"164": 0, "164.125": 0.24}''')
rep('tr["about"] = "draft"','''tr["about"] = ("Bars of a measured grid, shows/scenes/deadmau5 - Some Chords.beats: bar b starts at 0.218 + 1.875 b seconds (128.001 BPM), 238 bars, flat to within 5 ms over the song. "
    "The bar line is where the chord loop, the drops and the phrases turn; the first kicks of the two drops are step 0 of bars 52 and 164. "
    "The harmony was read off the audio. The two long builds are a four-bar loop, G#m, E, F#, G# major, changing an eighth ahead of the bar; the drops are one G#m vamp with an F# and an E in the last beats of every eighth bar. "
    "A cathedral at night. Every chord has its own glass, G#m cobalt, E ruby, F# gold, G# major verdigris, and the whole helmet changes colour exactly on the change. "
    "The shell is a window: a fan of seven leaded panes on the dome, the lead lines drawn dark over the LEDs that are really there, and the jaw below it. "
    "The ears are the organ: each tube is a note of the triad and every chord rolls through them in order, root, third, fifth. The jaw and the rims are the pedal, the bass. "
    "The first build assembles it: the pedal alone, then the pipes one note at a time, then the panes from the centre out, each flaring as it goes in. "
    "The held G major raises light up the whole window, the crash cuts it to black, and the drop floods it cobalt, the triad running in the pipes and the clap on all three. "
    "Every eighth bar the turnaround flashes everything gold, then ruby, and each new instrument leaves panes stained for good: ruby at the open hats, gold at the rising plucks, when the pipes fire up on every off-beat with gold tips, ruby again at the last climb. "
    "Then everything stops and the title crosses the dark once. "
    "In the second build a candle walks the melody behind the dark glass, one place in the fan for each note, in the colour of the chord under it, until the glass wakes behind it. "
    "The second drop opens on the one white of the song with the whole window behind it, ruby and gold trading places every bar, then every two beats, then every beat, up to the bar that stops: only gold and ruby in the jaw and the ears. "
    "Then home to plain cobalt, and the window comes out pane by pane as the instruments leave, the centre pane last, over the ticks. "
    "Shell layers are kept so the governor stays off it, so what is lit stays lit next to the ears.")''')
rep('''      "marks": {"pedal": 0, "root": 4, "third": 8, "fifth": 12, "pane1": 16, "pane2": 20, "pane3": 24, "pane4": 28, "window": 32, "window2": 40,
                "hold": 48, "crash": 51.75, "flood": 52, "stain1": 68, "stain2": 84, "stain3": 100, "cut": 116, "pedal2": 120, "candle": 128, "candle2": 136,
                "wash": 144, "beat2": 148, "hold2": 160, "crash2": 163.75, "blaze": 164, "clapback": 172, "trade": 180, "trade2": 188, "stop": 195, "home": 196,
                "strip": 212, "ticks": 228, "end": 236},''','''      "marks": {"pedal": 0, "root": 4, "third": 8, "fifth": 12, "pane1": 16, "pane2": 20, "pane3": 24, "pane4": 28, "window": 32, "windowb": 40,
                "hold": 48, "crash": 51.75, "flood": 52, "stain1": 68, "stain2": 84, "stain3": 100, "cut": 116, "pedal2": 120, "candle": 128, "candleb": 136,
                "wash": 144, "beat2": 148, "hold2": 160, "crash2": 163.75, "blaze": 164, "clapback": 172, "trade": 180, "tradeb": 188, "stop": 195, "home": 196,
                "strip": 212, "ticks": 228, "end": 236},''')
open(p,"w").write(s)
