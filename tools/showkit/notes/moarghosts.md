# What the moarghosts builder ran and saw

Commands and their text output, in order, with long output cut. Images are left out; rerun the tools to see them. Cut off partway: the generator and treatment in the repo are the latest state.

I'll start by reading the brief.

```
$ date; cat "tools/showkit/BRIEF.md"; ls -la "tools/showkit"
Sat Oct 31 12:39:04 PDT 2026
# Making one song's show for the deadmau5 helmet

You are choreographing one song for a real wearable LED helmet (deadmau5-style mau5head), for tonight's Halloween party. The owner's words: "Create these really good animations ... especially ones like the Tiki Tiki one, which was really good because it was unique. Keep doing these cool, unique ones for each song." Read `shows/scenes/TIKI TIKI - Slowed.scene.json` and its generator `(scratch)/tiki/write_treatment.py` first: that is the bar. A show is a story with its own world, palette and characters; motifs come back when the music does; builds visibly grow; drops land exactly on the bass; breakdowns strip back to almost nothing; the ears play as an instrument of their own. It must not look like a sequence of effects, and it must not look like any other show.

Working directory: `~/deadmau5 app` (main checkout, run everything from there). `KIT=tools/showkit`. Your scratch files go in `$KIT/work/<short song name>/`.

## Hard rules
- Only write these files for your song: `shows/scenes/<base>.beats`, `shows/scenes/<base>.scene.json`, `shows/scenes/<base>.sprites.json`, and what the tools make: `shows/<base>.json`, `shows/<base>.analysis.npz`. Nine other authors are working beside you on other songs. Never edit any code, any test, or another song's file. If you truly need an engine feature, finish without it and say so in your report.
- NEVER contact the helmet (192.168.10.172, 4.3.2.1, or anything scanning the network). Do not run `mau5show.py play`, `mau5offline.py`, `mau5ctl`, `test_mau5.py`, or anything that
... [cut] ...
352 Oct 31 12:38 .
drwx------@ 281 jones  wheel   8992 Oct 31 12:37 ..
-rw-r--r--@   1 jones  wheel   9702 Oct 31 12:38 BRIEF.md
-rw-r--r--@   1 jones  wheel    933 Oct 31 12:37 fmt.py
-rw-r--r--@   1 jones  wheel  10884 Oct 31 12:38 grid.py
-rw-r--r--@   1 jones  wheel  38416 Oct 31 12:37 mau5song_new.py
-rw-r--r--@   1 jones  wheel   1925 Oct 31 12:38 sheet.py
-rw-r--r--@   1 jones  wheel   1652 Oct 31 12:37 songmap.py
-rw-r--r--@   1 jones  wheel   2438 Oct 31 12:37 spectro.py
-rw-r--r--@   1 jones  wheel   1173 Oct 31 12:37 spritetry.py
drwxr-xr-x@   3 jones  wheel     96 Oct 31 12:37 work
```

```
$ cd "~/deadmau5 app"; KIT=tools/showkit; mkdir -p "$KIT/work/moarghosts"; cat "(scratch)/tiki/write_treatment.py"; echo ======; cat "$KIT/grid.py"; echo =====; cat "$KIT/sheet.py"; echo ====; cat "$KIT/songmap.py"; echo ====; cat "$KIT/spectro.py"; echo ====; cat "$KIT/spritetry.py"; echo ===; cat "$KIT/fmt.py"; ls -la shows | head -50; ls -la shows/scenes
Exit code 1
import json
KICK="x.......x......."
idolp={"sprite":"tiki","y_lo":-108,"y_hi":166,"x_half":171}
tr={"v":1,"show":"TIKI TIKI - Slowed",
"about":"Bars of a measured grid, shows/scenes/TIKI TIKI - Slowed.beats: bar b starts at 1.796 + 1.739 b seconds (137.98 BPM), 183 bars, and at bar 119.5 the track is spliced, so the music comes back 197 ms late and the grid holds still for it. Everything from there is the song's opening again, bar for bar. The bar line is where the phrases turn, with the kick on 1 and 3 and the clap on 2 and 4 with a flick on the and of 2. A night on the island. Torches get lit one tube at a time; the hooks are fire climbing the shell with the ears burning as torches, the kick on the rims and the clap up the tubes. Every breakdown goes out to the lagoon, cold water and moon glints, with one stopped bar of almost nothing, and the title crosses the face once, in the first. The verses are bamboo: upright stalks swaying on the face, the two sides stomping in turn. The big sections wake the idol, a carved mask drawn to fit the LEDs that exist: brow and eyes on the dome, teeth along the jaw, since the middle of the face has no LEDs. It burns in torch colours the first time, at sunset the second, and half fire, half water the third, swapping sides. The song then starts over, so the show does too, and the last big section has everything, with white once. At the end the torches go out one tube at a time and the idol is last to go. Shell layers are kept near the shell's 300 mA and nothing on it pulses faster than a beat.",
"lead":0,
"marks":{"hush":2,"light":3,"hook":5,"hookb":9,"dip":13,"climb":14,"hook2":15,"burn":21,
 "water":25,"stop":26,"still":27,"swell":30,"verse":31,"vlow":37,"vrise":38,"big":39,"bigb":47,"burn2":57,
 "water2":61,"stop2":62,"s
... [cut] ...
n.dumps(tr["marks"])+',']
out.append('"palettes":{\n'+",\n".join("  %s: %s"%(json.dumps(k),json.dumps(v)) for k,v in tr["palettes"].items())+'\n },')
out.append('"motifs":{\n'+",\n".join("  %s: %s"%(json.dumps(k),json.dumps(v)) for k,v in tr["motifs"].items())+'\n },')
out.append('"scenes":'+block(tr["scenes"])+',')
out.append('"hits":'+block(tr["hits"]))
out.append('}')
open('shows/scenes/TIKI TIKI - Slowed.scene.json','w').write("\n".join(out)+"\n")
json.load(open('shows/scenes/TIKI TIKI - Slowed.scene.json'))
print('scenes',len(tr["scenes"]),'hits',len(tr["hits"]))
(eval):1: ===== not found
```

```
$ sed -n 1,75p "(scratch)/tiki/write_treatment.py" | cut -c1-900 | sed -n 40,75p
 "drain":{"fx":"sweep","on":"shell","axis":"y","shape":"p","mode":"fill","soft":0.2,"from":1.1,"to":-0.15},
 "ring":{"fx":"sweep","on":"shell","axis":"r","shape":"p","mode":"band","from":0,"to":1.2,"width":0.25},
 "blow":{"fx":"fill","on":"ears","c":0.8,"gain":[0.28,0]},
 "lit":[{"use":"flame"},{"use":"torch"},{"use":"kick"},{"use":"clap"}],
 "lift":{"fx":"blades","seq":["0","1","2","012"],"rise":0.2,"c":0.4,"ctip":0.95}},
"scenes":[]}
S=tr["scenes"].append
PUMP={"pat":KICK,"step":0.25,"depth":0.2,"decay":0.5}
HARD=dict(PUMP,depth=0.3)
# --- the torches get lit
S({"name":"embers","from":-0.75,"to":"hush","pal":"ember","layers":[
  {"fx":"sparks","on":"shell","rate":0.5,"life":3,"loop":7,"seed":3,"nbr":0.6,"c":0.7,"spread":0.25,"gain":[0.2,0.55],"env":{"in":4}},
  {"use":"torch","pal":"ember","hi":0.4,"speed":-0.125,"gain":0.25,"env":{"in":6}}]})
S({"name":"hush","from":"hush","to":"light","pal":"ember","layers":[
  {"fx":"sparks","on":"shell","rate":0.5,"life":3,"loop":7,"seed":3,"nbr":0.6,"c":0.7,"spread":0.25,"gain":[0.5,0.2]},
  {"use":"torch","pal":"ember","hi":0.4,"speed":-0.125,"gain":[0.25,0.08]}]})
S({"name":"lighting","from":"light","to":"hook","pal":"torch","out":0.5,"layers":[
  {"use":"lift","step":{"light":2,"4":1},"keep":0.45,"gain":[0.25,0.6]},
  {"use":"rise","c":[0.25,0.6],"gain":[0.02,0.1]},
  {"use":"front","c":[0.45,0.9],"gain":[0.1,0.35]}]})
# --- the hook: fire climbing, the ears as torches
S({"name":"hook","from":"hook","to":"hookb","pal":"torch","pump":PUMP,"layers":[{"use":"lit"},{"use":"flick"}]})
S({"name":"hookb","from":"hookb","to":"dip","like":"hook","add":[{"use":"idol","gain":{"hookb":0,"10":0.24},"env":{"in":4}}]})
S({"name":"dip","from":"dip","to":"climb","pal":"ember","layers":[
  {"use":"drain","c":[0.75,0.3],"gain":0.1},
  {"fx":"fil
... [cut] ...
0.5,"gain":[0.3,0.12]}]})
S({"name":"climb","from":"climb","to":"hook2","pal":"torch","layers":[
  {"use":"rise","c":[0.2,0.6],"gain":[0.02,0.09]},
  {"use":"front","c":[0.45,0.9],"gain":[0.1,0.4]},
  {"use":"lift","step":{"climb":1,"14.5":0.5},"gain":[0.25,0.6]},
  {"use":"kick","gain":0.4}]})
S({"name":"hook2","from":"hook2","to":"burn","pal":"torch","pump":PUMP,"layers":[{"use":"lit"},{"use":"idol"},{"use":"embers"}]})
S({"name":"burn","from":"burn","to":"water","pal":"torch","layers":[
  {"use":"flame","gain":[0.2,0.03],"hi":[0.85,0.5]},
  {"use":"torch","gain":[0.3,0.06],"hi":[0.95,0.5]},
```

```
$ KIT=tools/showkit; cat "$KIT/grid.py"
#!/usr/bin/env python3
"""grid.py -- measure a song's real beat grid against its audio. Run from the repo root.

  python3 $KIT/grid.py scan  "shows/<base>.mp3"
      Tempo from the improved estimator, refined against the onsets; the phase of
      the onsets per 8 bars (flat means right, a step means a splice or tempo
      change); which beat starts a bar and a phrase.
  python3 $KIT/grid.py fold  "shows/<base>.mp3" --spb S --anchor T [--holds "t:s,..."] [--spans "0-8,16-32"]
      Onset strength folded into 16 steps per span, per band: read the kick and clap
      off this. Step 0 of a four-on-the-floor bar should carry the kick.
  python3 $KIT/grid.py write "<base>" --spb S --anchor T [--holds "t:s,..."]
      T is the time of ANY downbeat that starts a bar. Writes shows/scenes/<base>.beats
      from the earliest downbeat, deletes the stale analysis and rebuilds the show.
      A hold "t:s" means the music comes back s seconds late from time t (a splice).
  python3 $KIT/grid.py check "<base>"
      The built show's grid against the audio, per 8 bars. Worst should be under 15 ms.
"""
import argparse, json, os, re, subprocess, sys
import numpy as np
REPO = os.getcwd()
KIT = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.join(KIT, "work")
sys.path.insert(0, REPO); sys.path.insert(0, KIT)
SR, N, HOP = 22050, 1024, 256
BANDS = [("sub", 20, 90), ("bass", 90, 200), ("lowmid", 200, 600), ("mid", 600, 2000),
         ("pres", 2000, 5000), ("air", 5000, 11000)]
CH = " .:-=+*#%@"


def env_of(mp3):
    os.makedirs(WORK, exist_ok=True)
    p = os.path.join(WORK, re.sub(r"\W+", "_", os.path.basename(mp3)) + ".env.npz")
    if os.path.exists(p) and os.path.getmtime(p) >= os.path.getmtime(mp3):
        z = np.load(p)
        return {k: z[k] for k in z.files}
    raw = 
... [cut] ...
add_argument("--spb", type=float, required=True)
    f.add_argument("--anchor", type=float, required=True); f.add_argument("--holds", default=""); f.add_argument("--spans", default="")
    w = sub.add_parser("write"); w.add_argument("base"); w.add_argument("--spb", type=float, required=True)
    w.add_argument("--anchor", type=float, required=True); w.add_argument("--holds", default="")
    c = sub.add_parser("check"); c.add_argument("base")
    a = ap.parse_args()
    {"scan": cmd_scan, "fold": cmd_fold, "write": cmd_write, "check": cmd_check}[a.cmd](a)


if __name__ == "__main__":
    main()
```

```
$ KIT=tools/showkit; cat "$KIT/sheet.py"; echo; echo ----; cat "$KIT/songmap.py"; echo; echo ----; cat "$KIT/spectro.py"; echo; echo ----; cat "$KIT/spritetry.py"; echo; echo ---; cat "$KIT/fmt.py"; echo; cd "~/deadmau5 app"; ls -la shows | head -60; ls -la shows/scenes
#!/usr/bin/env python3
"""sheet.py "<base>" out.png bar[:label] bar[:label] ... -- the show at those bars as the helmet
will really look, through the power guard: a contact sheet, front view. Also prints, per tile, how
bright the shell and ears really are after the guard. Bars may be fractional: 40.25 is the second
beat of bar 40, so catch both a kick and the gap after it. Run from the repo root."""
import json, os, sys
sys.path.insert(0, os.getcwd())
import numpy as np, mau5show, mau5preview as PV
from PIL import Image, ImageDraw
base, out = sys.argv[1], sys.argv[2]
marks = []
for a in sys.argv[3:]:
    b, _, lab = a.partition(":")
    marks.append((float(b), lab))
show = json.load(open(os.path.join("shows", base + ".json")))
music = mau5show._music_for(show, os.path.join("shows", base + ".mp3"))
g = show["scenes"]["grid"]; spb = g["spb"]; t0 = g["t0"]
def tof(bar):
    B = 4 * bar
    return t0 + B * spb + sum(b * spb for at, b in g.get("holds", []) if B > at)
pl = mau5show.Player(show, music=music)
sc = PV.Scene(pl.h)
cols = 6; W = 300; H = 245
rows = (len(marks) + cols - 1) // cols
o = Image.new("RGB", (cols * W, rows * H), (0, 0, 0))
d = ImageDraw.Draw(o)
h = pl.h
for k, (bar, lab) in enumerate(marks):
    t = tof(bar)
    for dt in (0.5, 0.3, 0.16, 0.08, 0.04):
        pl.frame(t - dt)
    f = np.asarray(pl.frame(t), float)
    im = sc.frame(f * pl.gain).crop((60, 40, 700, 560)).resize((W, H))
    o.paste(im, ((k % cols) * W, (k // cols) * H))
    d.text(((k % cols) * W + 5, (k // cols) * H + 3), "%s bar %g" % (lab, bar), fill=(255, 255, 255))
    d.text(((k % cols) * W + 5, (k // cols) * H + 15), pl.label[:42] if getattr(pl, "label", None) else "", fill=(180, 180, 180))
    s = f[h.shell]; e = f[h.ears]
    print("bar %-7g %-14s shell max %3.0f mean %5.1f   ears 
... [cut] ...
ne.json
-rw-r--r--@  1 jones  staff   6076 Oct 31 12:23 beneath (with raxaj).beats
-rw-r--r--@  1 jones  staff  13145 Oct 31 12:23 beneath (with raxaj).scene.json
-rw-r--r--@  1 jones  staff  10412 Oct 31 12:18 deadmau5 - Ghosts n Stuff (Nero Remix).beats
-rw-r--r--@  1 jones  staff   9383 Oct 31 12:18 deadmau5 - Ghosts n Stuff (Nero Remix).scene.json
-rw-r--r--@  1 jones  staff  14383 Oct 30 05:30 deadmau5 - Strobe (Dimension Remix).scene.json
-rw-r--r--@  1 jones  staff   8945 Oct 30 05:03 deadmau5 - Strobe.scene.json
-rw-r--r--@  1 jones  staff   3748 Oct 31 12:37 deadmau5 - The Veldt.beats
```

```
$ sed -n 1,75p "(scratch)/tiki/write_treatment.py" | cut -c1-900 | sed -n 40,75p
 "drain":{"fx":"sweep","on":"shell","axis":"y","shape":"p","mode":"fill","soft":0.2,"from":1.1,"to":-0.15},
 "ring":{"fx":"sweep","on":"shell","axis":"r","shape":"p","mode":"band","from":0,"to":1.2,"width":0.25},
 "blow":{"fx":"fill","on":"ears","c":0.8,"gain":[0.28,0]},
 "lit":[{"use":"flame"},{"use":"torch"},{"use":"kick"},{"use":"clap"}],
 "lift":{"fx":"blades","seq":["0","1","2","012"],"rise":0.2,"c":0.4,"ctip":0.95}},
"scenes":[]}
S=tr["scenes"].append
PUMP={"pat":KICK,"step":0.25,"depth":0.2,"decay":0.5}
HARD=dict(PUMP,depth=0.3)
# --- the torches get lit
S({"name":"embers","from":-0.75,"to":"hush","pal":"ember","layers":[
  {"fx":"sparks","on":"shell","rate":0.5,"life":3,"loop":7,"seed":3,"nbr":0.6,"c":0.7,"spread":0.25,"gain":[0.2,0.55],"env":{"in":4}},
  {"use":"torch","pal":"ember","hi":0.4,"speed":-0.125,"gain":0.25,"env":{"in":6}}]})
S({"name":"hush","from":"hush","to":"light","pal":"ember","layers":[
  {"fx":"sparks","on":"shell","rate":0.5,"life":3,"loop":7,"seed":3,"nbr":0.6,"c":0.7,"spread":0.25,"gain":[0.5,0.2]},
  {"use":"torch","pal":"ember","hi":0.4,"speed":-0.125,"gain":[0.25,0.08]}]})
S({"name":"lighting","from":"light","to":"hook","pal":"torch","out":0.5,"layers":[
  {"use":"lift","step":{"light":2,"4":1},"keep":0.45,"gain":[0.25,0.6]},
  {"use":"rise","c":[0.25,0.6],"gain":[0.02,0.1]},
  {"use":"front","c":[0.45,0.9],"gain":[0.1,0.35]}]})
# --- the hook: fire climbing, the ears as torches
S({"name":"hook","from":"hook","to":"hookb","pal":"torch","pump":PUMP,"layers":[{"use":"lit"},{"use":"flick"}]})
S({"name":"hookb","from":"hookb","to":"dip","like":"hook","add":[{"use":"idol","gain":{"hookb":0,"10":0.24},"env":{"in":4}}]})
S({"name":"dip","from":"dip","to":"climb","pal":"ember","layers":[
  {"use":"drain","c":[0.75,0.3],"gain":0.1},
  {"fx":"fil
... [cut] ...
0.5,"gain":[0.3,0.12]}]})
S({"name":"climb","from":"climb","to":"hook2","pal":"torch","layers":[
  {"use":"rise","c":[0.2,0.6],"gain":[0.02,0.09]},
  {"use":"front","c":[0.45,0.9],"gain":[0.1,0.4]},
  {"use":"lift","step":{"climb":1,"14.5":0.5},"gain":[0.25,0.6]},
  {"use":"kick","gain":0.4}]})
S({"name":"hook2","from":"hook2","to":"burn","pal":"torch","pump":PUMP,"layers":[{"use":"lit"},{"use":"idol"},{"use":"embers"}]})
S({"name":"burn","from":"burn","to":"water","pal":"torch","layers":[
  {"use":"flame","gain":[0.2,0.03],"hi":[0.85,0.5]},
  {"use":"torch","gain":[0.3,0.06],"hi":[0.95,0.5]},
```

```
$ KIT=tools/showkit; cat "$KIT/grid.py"
#!/usr/bin/env python3
"""grid.py -- measure a song's real beat grid against its audio. Run from the repo root.

  python3 $KIT/grid.py scan  "shows/<base>.mp3"
      Tempo from the improved estimator, refined against the onsets; the phase of
      the onsets per 8 bars (flat means right, a step means a splice or tempo
      change); which beat starts a bar and a phrase.
  python3 $KIT/grid.py fold  "shows/<base>.mp3" --spb S --anchor T [--holds "t:s,..."] [--spans "0-8,16-32"]
      Onset strength folded into 16 steps per span, per band: read the kick and clap
      off this. Step 0 of a four-on-the-floor bar should carry the kick.
  python3 $KIT/grid.py write "<base>" --spb S --anchor T [--holds "t:s,..."]
      T is the time of ANY downbeat that starts a bar. Writes shows/scenes/<base>.beats
      from the earliest downbeat, deletes the stale analysis and rebuilds the show.
      A hold "t:s" means the music comes back s seconds late from time t (a splice).
  python3 $KIT/grid.py check "<base>"
      The built show's grid against the audio, per 8 bars. Worst should be under 15 ms.
"""
import argparse, json, os, re, subprocess, sys
import numpy as np
REPO = os.getcwd()
KIT = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.join(KIT, "work")
sys.path.insert(0, REPO); sys.path.insert(0, KIT)
SR, N, HOP = 22050, 1024, 256
BANDS = [("sub", 20, 90), ("bass", 90, 200), ("lowmid", 200, 600), ("mid", 600, 2000),
         ("pres", 2000, 5000), ("air", 5000, 11000)]
CH = " .:-=+*#%@"


def env_of(mp3):
    os.makedirs(WORK, exist_ok=True)
    p = os.path.join(WORK, re.sub(r"\W+", "_", os.path.basename(mp3)) + ".env.npz")
    if os.path.exists(p) and os.path.getmtime(p) >= os.path.getmtime(mp3):
        z = np.load(p)
        return {k: z[k] for k in z.files}
    raw = 
... [cut] ...
add_argument("--spb", type=float, required=True)
    f.add_argument("--anchor", type=float, required=True); f.add_argument("--holds", default=""); f.add_argument("--spans", default="")
    w = sub.add_parser("write"); w.add_argument("base"); w.add_argument("--spb", type=float, required=True)
    w.add_argument("--anchor", type=float, required=True); w.add_argument("--holds", default="")
    c = sub.add_parser("check"); c.add_argument("base")
    a = ap.parse_args()
    {"scan": cmd_scan, "fold": cmd_fold, "write": cmd_write, "check": cmd_check}[a.cmd](a)


if __name__ == "__main__":
    main()
```

```
$ KIT=tools/showkit; cat "$KIT/sheet.py"; echo; echo ----; cat "$KIT/songmap.py"; echo; echo ----; cat "$KIT/spectro.py"; echo; echo ----; cat "$KIT/spritetry.py"; echo; echo ---; cat "$KIT/fmt.py"; echo; cd "~/deadmau5 app"; ls -la shows | head -60; ls -la shows/scenes
#!/usr/bin/env python3
"""sheet.py "<base>" out.png bar[:label] bar[:label] ... -- the show at those bars as the helmet
will really look, through the power guard: a contact sheet, front view. Also prints, per tile, how
bright the shell and ears really are after the guard. Bars may be fractional: 40.25 is the second
beat of bar 40, so catch both a kick and the gap after it. Run from the repo root."""
import json, os, sys
sys.path.insert(0, os.getcwd())
import numpy as np, mau5show, mau5preview as PV
from PIL import Image, ImageDraw
base, out = sys.argv[1], sys.argv[2]
marks = []
for a in sys.argv[3:]:
    b, _, lab = a.partition(":")
    marks.append((float(b), lab))
show = json.load(open(os.path.join("shows", base + ".json")))
music = mau5show._music_for(show, os.path.join("shows", base + ".mp3"))
g = show["scenes"]["grid"]; spb = g["spb"]; t0 = g["t0"]
def tof(bar):
    B = 4 * bar
    return t0 + B * spb + sum(b * spb for at, b in g.get("holds", []) if B > at)
pl = mau5show.Player(show, music=music)
sc = PV.Scene(pl.h)
cols = 6; W = 300; H = 245
rows = (len(marks) + cols - 1) // cols
o = Image.new("RGB", (cols * W, rows * H), (0, 0, 0))
d = ImageDraw.Draw(o)
h = pl.h
for k, (bar, lab) in enumerate(marks):
    t = tof(bar)
    for dt in (0.5, 0.3, 0.16, 0.08, 0.04):
        pl.frame(t - dt)
    f = np.asarray(pl.frame(t), float)
    im = sc.frame(f * pl.gain).crop((60, 40, 700, 560)).resize((W, H))
    o.paste(im, ((k % cols) * W, (k // cols) * H))
    d.text(((k % cols) * W + 5, (k // cols) * H + 3), "%s bar %g" % (lab, bar), fill=(255, 255, 255))
    d.text(((k % cols) * W + 5, (k // cols) * H + 15), pl.label[:42] if getattr(pl, "label", None) else "", fill=(180, 180, 180))
    s = f[h.shell]; e = f[h.ears]
    print("bar %-7g %-14s shell max %3.0f mean %5.1f   ears 
... [cut] ...
ne.json
-rw-r--r--@  1 jones  staff   6076 Oct 31 12:23 beneath (with raxaj).beats
-rw-r--r--@  1 jones  staff  13145 Oct 31 12:23 beneath (with raxaj).scene.json
-rw-r--r--@  1 jones  staff  10412 Oct 31 12:18 deadmau5 - Ghosts n Stuff (Nero Remix).beats
-rw-r--r--@  1 jones  staff   9383 Oct 31 12:18 deadmau5 - Ghosts n Stuff (Nero Remix).scene.json
-rw-r--r--@  1 jones  staff  14383 Oct 30 05:30 deadmau5 - Strobe (Dimension Remix).scene.json
-rw-r--r--@  1 jones  staff   8945 Oct 30 05:03 deadmau5 - Strobe.scene.json
-rw-r--r--@  1 jones  staff   3748 Oct 31 12:37 deadmau5 - The Veldt.beats
```

```
$ cd "~/deadmau5 app"; KIT=tools/showkit; time python3 $KIT/grid.py scan "shows/deadmau5 - Moar Ghosts n Stuff.mp3" 2>&1 | tail -20
estimator: 127.997 BPM, first bar 0.052 s, tempo lock 0.817, bar lock 0.6027519535862128; song 270.0 s
refined over the whole song: spb 0.468770 = 127.995 BPM
first half 127.995 BPM, second half 127.995 BPM (these should agree within 0.05)
phase of the music against that grid per 8 bars, ms (flat = right; one 16th = 117 ms; contrast under 1.15 means sparse, ignore it):
  0:-11(2.22)  8:+33(1.11)  16:+7(1.31)  24:-7(9.13)  32:-7(10.09)  40:-9(6.69)  48:-9(6.98)  56:-5(6.46)  64:-7(6.81)  72:-5(5.51)  80:-7(6.90)  88:-7(5.57)  96:-7(2.20)  104:-7(1.36)  112:-7(5.84)  120:-9(5.57)  128:-9(4.94)  136:-9(5.88)
change per beat position, estimator's bar 1 at 0.052 s: 0:0.60 1:0.51 2:0.51 3:0.60  (the highest is where bars really start, 0 = estimator is right)
strongest phrase positions, in beats mod 32 from that bar 1: 8(1.14), 7(1.10), 23(1.03), 16(0.96), 6(0.84), 15(0.82)
biggest single changes (time, beat from bar 1, beat mod 4): 27.2s b58 m2; 36.1s b77 m1; 37.1s b79 m3; 48.8s b104 m0; 78.3s b167 m3; 78.8s b168 m0; 79.3s b169 m1; 138.8s b296 m0; 142.1s b303 m3; 172.1s b367 m3; 172.6s b368 m0; 175.8s b375 m3; 176.3s b376 m0; 213.3s b455 m3; 213.8s b456 m0; 220.8s b471 m3; 228.3s b487 m3; 235.4s b502 m2; 235.8s b503 m3; 239.6s b511 m3; 240.1s b512 m0; 243.3s b519 m3; 250.8s b535 m3; 265.8s b567 m3
suggested next: grid.py fold with --spb 0.468770 --anchor 0.052, decide the bar line, then grid.py write
python3 $KIT/grid.py scan "shows/deadmau5 - Moar Ghosts n Stuff.mp3" 2>&1  1.65s user 0.47s system 121% cpu 1.740 total
tail -20  0.00s user 0.00s system 0% cpu 1.740 total
```

```
$ cd "~/deadmau5 app"; sed -n 1,12p "shows/scenes/TIKI TIKI - Slowed.scene.json" | cut -c1-1500; ffprobe -hide_banner -i "shows/deadmau5 - Moar Ghosts n Stuff.mp3" 2>&1 | head -20; python3 mau5scene.py 2>&1 | head -30; grep -n "def \|^class " mau5scene.py | head -80
{
"v":1,
"show":"TIKI TIKI - Slowed",
"about":"Bars of a measured grid, shows/scenes/TIKI TIKI - Slowed.beats: bar b starts at 1.796 + 1.739 b seconds (137.98 BPM), 183 bars, and at bar 119.5 the track is spliced, so the music comes back 197 ms late and the grid holds still for it. Everything from there is the song's opening again, bar for bar. The bar line is where the phrases turn, with the kick on 1 and 3 and the clap on 2 and 4 with a flick on the and of 2. A night on the island. Torches get lit one tube at a time; the hooks are fire climbing the shell with the ears burning as torches, the kick on the rims and the clap up the tubes. Every breakdown goes out to the lagoon, cold water and moon glints, with one stopped bar of almost nothing, and the title crosses the face once, in the first. The verses are bamboo: upright stalks swaying on the face, the two sides stomping in turn. The big sections wake the idol, a carved mask drawn to fit the LEDs that exist: brow and eyes on the dome, teeth along the jaw, since the middle of the face has no LEDs. It burns in torch colours the first time, at sunset the second, and half fire, half water the third, swapping sides. The song then starts over, so the show does too, and the last big section has everything, with white once. At the end the torches go out one tube at a time and the idol is last to go. Shell layers are kept near the shell's 300 mA and nothing on it pulses faster than a beat.",
"lead":0,
"marks":{"hush": 2, "light": 3, "hook": 5, "hookb": 9, "dip": 13, "climb": 14, "hook2": 15, "burn": 21, "water": 25, "stop": 26, "still": 27, "swell": 30, "verse": 31, "vlow": 37, "vrise": 38, "big": 39, "bigb": 47, "burn2": 57, "water2": 61, "stop2": 62, "still2": 63, "swell2": 66, "verse2": 67, "vlow2": 73, "vrise2": 74, "big2"
... [cut] ...
v):
877:    def at(self, p, bar, music, tt):
898:class Scenes:
906:    def __init__(self, spec, helmet):
927:    def _scene(self, s):
935:    def _layer(self, L):
983:    def _mix(self, P, idx, v):
994:    def _render(self, P, B, bar, lb, span, p, music, tt):
1140:    def scene_at(self, bar):
1146:    def beat(self, tt):
1154:    def frame(self, t, music=None):
1197:def bar_stats(music):
1208:        def mean(k, w):
1211:        def peak(k, w):
1220:def _row(r):
1225:def print_marks(base, music):
1240:def check(base, fps=25.0, verbose=True):
1303:def main(argv=None):
1318:    def names(given):
```

```
$ cd "~/deadmau5 app"; KIT=tools/showkit; python3 $KIT/grid.py fold "shows/deadmau5 - Moar Ghosts n Stuff.mp3" --spb 0.468770 --anchor 0.052 2>&1 | tail -100
bar 0 at 0.052 s, 127.995 BPM, 143 bars
bars 0-16   (16 steps, | every beat; one row per band)
   sub     #--=|*+==|@**#|%**#   peak 0.26
   bass    @=-=|%===|#===|*==:   peak 0.31
   lowmid  @*+*|%+++|@*+=|**#+   peak 0.19
   mid     @:::|%--:|%::-|#:=-   peak 0.32
   pres    @..:|@:.:|#:::|*:=:   peak 0.36
   air     @.=.|@:-:|%.=:|#:-:   peak 0.38
bars 16-32   (16 steps, | every beat; one row per band)
   sub     @.:-|%.=+|@.::|%:-*   peak 0.29
   bass    @:::|#-=.|%.:.|#--:   peak 0.48
   lowmid  @:-:|=.@.|#:%:|-:#:   peak 0.42
   mid     @.::|*.#.|%.%:|=.*.   peak 0.54
   pres    @.::|@.+:|@.#.|+.*.   peak 0.63
   air     % : |% + |@ *.|+ +.   peak 0.56
bars 32-48   (16 steps, | every beat; one row per band)
   sub     @ ..|@ :=|@.. |@.:-   peak 0.60
   bass    @.. |%:: |@ . |%::    peak 0.97
   lowmid  @:..|*.* |@.#:|-.+    peak 0.71
   mid     @...|# = |@.+.|= =    peak 0.98
   pres    @ . |% = |@ +.|+ -    peak 1.22
   air     @ : |% = |@ + |+ =    peak 1.21
bars 48-64   (16 steps, | every beat; one row per band)
   sub     %   |@ ..|@.. |@..:   peak 0.76
   bass    @.  |@:: |@.  |@:.    peak 1.22
   lowmid  @:..|* - |@.-.|-.-    peak 0.95
   mid     @...|* - |@.-.|= -    peak 1.03
   pres    @...|* - |@.=.|+ -    peak 1.27
   air     @ : |+ - |@ - |= -    peak 1.30
bars 64-80   (16 steps, | every beat; one row per band)
   sub     @ . |@.:.|@ . |@ .:   peak 0.65
   bass    @.  |@:: |@.  |@::    peak 1.09
   lowmid  @: .|*.- |@.-.|=.-    peak 0.79
   mid     @...|+ - |@.-.|= :    peak 0.91
   pres    @...|# - |@.=.|* -    peak 1.03
   air     @ = |* + |@ + |+ +    peak 1.05
bars 80-96   (16 steps, | every beat; one row per band)
   sub     @. .|@...|@.. |@...   peak 0.57
   bass    @.  |@:: |@.. |@::    peak 0.92
   lowmid  @...|#.- |@.-.|=.-    peak 0.67
   mid
... [cut] ...
ry beat; one row per band)
   sub     @ . |#...|# : |% :    peak 0.71
   bass    @.  |%:: |% . |%::    peak 1.08
   lowmid  @:..|+.= |#.-.|-.-    peak 0.75
   mid     @...|+ - |%.-.|= :    peak 0.87
   pres    @...|* - |@.- |+ :    peak 1.02
   air     @ . |* - |@ - |+ -    peak 1.01
bars 128-143   (16 steps, | every beat; one row per band)
   sub     @ . |%.:.|% : |@ :.   peak 0.63
   bass    @   |%:: |@ . |%.:    peak 1.05
   lowmid  @:..|+.- |#.=.|-.:    peak 0.71
   mid     @...|+ : |#.-.|= :    peak 0.80
   pres    @.. |* - |#.- |* :    peak 0.96
   air     @ = |* + |% + |* *    peak 0.91
```

```
$ cd "~/deadmau5 app"; ls -la "shows/deadmau5 - Moar Ghosts n Stuff"* shows/scenes/ | grep -i "moar" ; sed -n 125,200p mau5scene.py
-rw-r--r--@ 1 jones  staff  6481337 Oct 31 12:37 shows/deadmau5 - Moar Ghosts n Stuff.mp3
class TreatmentError(ValueError):
    pass


# ----------------------------------------------------------------------
# the treatment
# ----------------------------------------------------------------------
def treatment_path(base):
    return os.path.join(SCENES, base + ".scene.json")


def load_treatment(base_or_path):
    """Read a treatment, stamped with a hash of its bytes.

    The stamp travels into the compiled show, so a show compiled from an
    older treatment than the one on disk is visible as exactly that.
    """
    path = (base_or_path if base_or_path.endswith(".json")
            else treatment_path(base_or_path))
    with open(path, "rb") as f:
        raw = f.read()
    tr = json.loads(raw.decode("utf-8"))
    tr["_sha"] = hashlib.sha1(raw).hexdigest()[:12]
    return tr


def grid_of(music):
    """(grid, bars) from an analysis, refusing a grid that is not straight.

    Scenes put every frame on t0 + beats * spb.  That is only the music's
    grid if the analysis' beats really are evenly spaced, so this checks
    every beat and every bar against the line and refuses to compile if
    any is more than 5 ms off -- a drifting track would need the measured
    beats, and this format does not carry them.

    A seam it can carry: a track edited so that the music comes back late,
    at the same tempo.  One beat that long is a hold, [beat, beats held],
    and the line carries on from the far side of it.  A beat that came
    early would have to run time backwards, so that is refused as drift.
    """
    beats = np.asarray(music.beats, float)
    bars = np.asarray(music.bars, float)
    if len(beats) < 8 or len(bars) < 2:
        raise TreatmentError("the analysis 
... [cut] ...
 %.1f ms from linear; scenes need "
                             "a steady grid" % (worst * 1000))
    grid = {"t0": t0, "spb": spb}
    seams = np.flatnonzero(late)
    if len(seams):
        grid["holds"] = [[float(k + 1 - first), float(late[k] / spb)] for k in seams]
    return grid, int(len(bars))


def src_of(base):
    """The analysis' own stamp of its audio, or '' for an older cache."""
    p = os.path.join(SHOWS, base + ".analysis.npz")
    try:
        z = np.load(p)
        return str(z["src"]) if "src" in z else ""
    except (OSError, ValueError):
        return ""


_HELMET = None
```

```
$ cd "~/deadmau5 app"; KIT=tools/showkit; python3 $KIT/grid.py fold "shows/deadmau5 - Moar Ghosts n Stuff.mp3" --spb 0.468770 --anchor 0.052 2>&1 | tail -100
bar 0 at 0.052 s, 127.995 BPM, 143 bars
bars 0-16   (16 steps, | every beat; one row per band)
   sub     #--=|*+==|@**#|%**#   peak 0.26
   bass    @=-=|%===|#===|*==:   peak 0.31
   lowmid  @*+*|%+++|@*+=|**#+   peak 0.19
   mid     @:::|%--:|%::-|#:=-   peak 0.32
   pres    @..:|@:.:|#:::|*:=:   peak 0.36
   air     @.=.|@:-:|%.=:|#:-:   peak 0.38
bars 16-32   (16 steps, | every beat; one row per band)
   sub     @.:-|%.=+|@.::|%:-*   peak 0.29
   bass    @:::|#-=.|%.:.|#--:   peak 0.48
   lowmid  @:-:|=.@.|#:%:|-:#:   peak 0.42
   mid     @.::|*.#.|%.%:|=.*.   peak 0.54
   pres    @.::|@.+:|@.#.|+.*.   peak 0.63
   air     % : |% + |@ *.|+ +.   peak 0.56
bars 32-48   (16 steps, | every beat; one row per band)
   sub     @ ..|@ :=|@.. |@.:-   peak 0.60
   bass    @.. |%:: |@ . |%::    peak 0.97
   lowmid  @:..|*.* |@.#:|-.+    peak 0.71
   mid     @...|# = |@.+.|= =    peak 0.98
   pres    @ . |% = |@ +.|+ -    peak 1.22
   air     @ : |% = |@ + |+ =    peak 1.21
bars 48-64   (16 steps, | every beat; one row per band)
   sub     %   |@ ..|@.. |@..:   peak 0.76
   bass    @.  |@:: |@.  |@:.    peak 1.22
   lowmid  @:..|* - |@.-.|-.-    peak 0.95
   mid     @...|* - |@.-.|= -    peak 1.03
   pres    @...|* - |@.=.|+ -    peak 1.27
   air     @ : |+ - |@ - |= -    peak 1.30
bars 64-80   (16 steps, | every beat; one row per band)
   sub     @ . |@.:.|@ . |@ .:   peak 0.65
   bass    @.  |@:: |@.  |@::    peak 1.09
   lowmid  @: .|*.- |@.-.|=.-    peak 0.79
   mid     @...|+ - |@.-.|= :    peak 0.91
   pres    @...|# - |@.=.|* -    peak 1.03
   air     @ = |* + |@ + |+ +    peak 1.05
bars 80-96   (16 steps, | every beat; one row per band)
   sub     @. .|@...|@.. |@...   peak 0.57
   bass    @.  |@:: |@.. |@::    peak 0.92
   lowmid  @...|#.- |@.-.|=.-    peak 0.67
   mid
... [cut] ...
ry beat; one row per band)
   sub     @ . |#...|# : |% :    peak 0.71
   bass    @.  |%:: |% . |%::    peak 1.08
   lowmid  @:..|+.= |#.-.|-.-    peak 0.75
   mid     @...|+ - |%.-.|= :    peak 0.87
   pres    @...|* - |@.- |+ :    peak 1.02
   air     @ . |* - |@ - |+ -    peak 1.01
bars 128-143   (16 steps, | every beat; one row per band)
   sub     @ . |%.:.|% : |@ :.   peak 0.63
   bass    @   |%:: |@ . |%.:    peak 1.05
   lowmid  @:..|+.- |#.=.|-.:    peak 0.71
   mid     @...|+ : |#.-.|= :    peak 0.80
   pres    @.. |* - |#.- |* :    peak 0.96
   air     @ = |* + |% + |* *    peak 0.91
```

```
$ cd "~/deadmau5 app"; ls -la "shows/deadmau5 - Moar Ghosts n Stuff"* shows/scenes/ | grep -i "moar" ; sed -n 125,200p mau5scene.py
-rw-r--r--@ 1 jones  staff  6481337 Oct 31 12:37 shows/deadmau5 - Moar Ghosts n Stuff.mp3
class TreatmentError(ValueError):
    pass


# ----------------------------------------------------------------------
# the treatment
# ----------------------------------------------------------------------
def treatment_path(base):
    return os.path.join(SCENES, base + ".scene.json")


def load_treatment(base_or_path):
    """Read a treatment, stamped with a hash of its bytes.

    The stamp travels into the compiled show, so a show compiled from an
    older treatment than the one on disk is visible as exactly that.
    """
    path = (base_or_path if base_or_path.endswith(".json")
            else treatment_path(base_or_path))
    with open(path, "rb") as f:
        raw = f.read()
    tr = json.loads(raw.decode("utf-8"))
    tr["_sha"] = hashlib.sha1(raw).hexdigest()[:12]
    return tr


def grid_of(music):
    """(grid, bars) from an analysis, refusing a grid that is not straight.

    Scenes put every frame on t0 + beats * spb.  That is only the music's
    grid if the analysis' beats really are evenly spaced, so this checks
    every beat and every bar against the line and refuses to compile if
    any is more than 5 ms off -- a drifting track would need the measured
    beats, and this format does not carry them.

    A seam it can carry: a track edited so that the music comes back late,
    at the same tempo.  One beat that long is a hold, [beat, beats held],
    and the line carries on from the far side of it.  A beat that came
    early would have to run time backwards, so that is refused as drift.
    """
    beats = np.asarray(music.beats, float)
    bars = np.asarray(music.bars, float)
    if len(beats) < 8 or len(bars) < 2:
        raise TreatmentError("the analysis 
... [cut] ...
 %.1f ms from linear; scenes need "
                             "a steady grid" % (worst * 1000))
    grid = {"t0": t0, "spb": spb}
    seams = np.flatnonzero(late)
    if len(seams):
        grid["holds"] = [[float(k + 1 - first), float(late[k] / spb)] for k in seams]
    return grid, int(len(bars))


def src_of(base):
    """The analysis' own stamp of its audio, or '' for an older cache."""
    p = os.path.join(SHOWS, base + ".analysis.npz")
    try:
        z = np.load(p)
        return str(z["src"]) if "src" in z else ""
    except (OSError, ValueError):
        return ""


_HELMET = None
```

```
$ cd "~/deadmau5 app"; KIT=tools/showkit; time python3 $KIT/grid.py write "deadmau5 - Moar Ghosts n Stuff" --spb 0.468770 --anchor 0.045 2>&1 | tail -15; python3 $KIT/grid.py check "deadmau5 - Moar Ghosts n Stuff" 2>&1 | tail; python3 $KIT/spectro.py "deadmau5 - Moar Ghosts n Stuff" $KIT/work/moarghosts/full.png
    1:52.55-2:00.05  lvl3  confetti   {'rate': 26.0}
    2:00.05-2:15.05  lvl2  plasma     {}
    2:15.05-2:30.05  lvl2  comet      {'period': 1.6}
    2:30.05-2:45.05  lvl2  wave       {'period': 1.6}
    2:45.05-2:52.55  lvl2  fire       {}
    2:52.55-3:07.55  lvl1  gradient   {'period': 3.75, 'a': (255, 40, 0), 'b': (255, 150, 0)}
    3:07.55-3:15.05  lvl1  scanner    {'period': 3.75}
    3:15.05-3:30.05  lvl0  eyes       {'period': 7.5}
    3:30.05-3:37.55  lvl3  eq         {}
    3:37.55-3:45.06  lvl3  pinwheel   {'period': 1.2}
    3:45.06-3:52.56  lvl3  split      {'shell': 'fire', 'ears': 'pinwheel'}
    3:52.56-4:00.06  lvl3  confetti   {'rate': 26.0}
    4:00.06-4:15.06  lvl2  comet      {'period': 0.938}
    4:15.06-4:28.18  lvl2  vu         {}
wrote shows/scenes/deadmau5 - Moar Ghosts n Stuff.beats: 576 beats, 144 bars, bar 0 at 0.045 s, 127.995 BPM
python3 $KIT/grid.py write "deadmau5 - Moar Ghosts n Stuff" --spb 0.468770     0.77s user 0.11s system 99% cpu 0.888 total
tail -15  0.00s user 0.00s system 0% cpu 0.888 total
deadmau5 - Moar Ghosts n Stuff: 127.995 BPM, 144 bars, bar 0 at 0.045 s, holds []
music against the grid per 8 bars, ms (contrast): 0:-3(2.21)  8:+41(1.11)  16:+15(1.29)  24:-1(9.00)  32:-1(10.28)  40:-1(6.77)  48:-1(7.20)  56:+1(6.44)  64:+1(6.72)  72:+1(5.79)  80:+1(6.78)  88:+1(5.34)  96:+1(2.18)  104:+1(1.36)  112:-1(5.52)  120:-1(5.67)  128:-1(5.34)  136:-1(5.52)
worst 15 ms where the music is clear enough to say, mean +1.1 ms
tools/showkit/songs/moarghosts/full.png
```

```
$ cd "~/deadmau5 app"; KIT=tools/showkit; python3 $KIT/songmap.py "deadmau5 - Moar Ghosts n Stuff"; python3 mau5scene.py bars "deadmau5 - Moar Ghosts n Stuff" | head -40
deadmau5 - Moar Ghosts n Stuff: 144 bars, 1.88 s a bar, 270.0 s
 bar     t   E  B  M  H  notes       change
   0    0.0   8  8  8  2  C F A       
   1    1.9   7  8  6  2  C F A       
   2    3.8   7  8  4  2  C F A       
   3    5.7   7  8  7  3  C F A       
   4    7.5   7  8  6  0  A# C A      
   5    9.4   5  7  5  1  C F A       
   6   11.3   5  6  3  0  C A# F      
   7   13.2   5  6  3  0  A# F A      
   8   15.0   4  6  4  0  F C A       
   9   16.9   5  6  4  0  F C A       
  10   18.8   5  6  4  0  F C A       
  11   20.7   5  6  4  0  A# F A      
  12   22.5   6  6  4  1  A# A C      
  13   24.4   6  6  5  1  A# A C      
  14   26.3   9  6  9  3  A A# F      >>
  15   28.2   9  6  9  2  F A A#      
  16   30.0   8  6  9  2  A F A#      
  17   31.9   7  6  9  4  A F C       
  18   33.8   7  6  9  2  F A A#      
  19   35.7   7  6  9  5  A F A#      
  20   37.5   7  4  9  2  A# F A      >>
  21   39.4   7  5  9  1  F A G       
  22   41.3   6  6  8  1  A# A F      
  23   43.2   6  6  8  1  A# A F      
  24   45.0   5  3  8  1  F A# A      
  25   46.9   5  4  8  1  G# F G      
  26   48.8   6  5  3  5  C F A       >>
  27   50.7   6  5  3  5  C F A       
  28   52.5   6  5  3  5  C F A       
  29   54.4   6  5  3  5  C F A       
  30   56.3   6  5  3  5  C F A       
  31   58.2   5  5  3  5  F C A       
  32   60.0   5  5  3  5  C F A       
  33   61.9   5  5  3  5  C F A       
  34   63.8   5  5  3  5  C F A       
  35   65.7   5  5  3  5  C F A       
  36   67.5   5  5  3  5  C F A       
  37   69.4   5  5  4  6  C F A       
  38   71.3   5  5  4  5  C F A       
  39   73.2   5  5  4  6  C F A       
  40   75.0   3  0  7  6  A A# G#     >>
  41   76.9   5  1  8  8  F A A#      >>
  42   78.8   8  7  4  5  C F A       >>
  4
... [cut] ...

    32    60.05s  energy 0.39  bass 0.45 (punch 1.00)  mid 0.34  high 0.48
    33    61.92s  energy 0.39  bass 0.45 (punch 1.00)  mid 0.34  high 0.50
    34    63.80s  energy 0.39  bass 0.45 (punch 1.00)  mid 0.33  high 0.48
    35    65.67s  energy 0.39  bass 0.43 (punch 1.00)  mid 0.35  high 0.50
    36    67.55s  energy 0.38  bass 0.45 (punch 1.00)  mid 0.34  high 0.48
    37    69.42s  energy 0.38  bass 0.45 (punch 1.00)  mid 0.39  high 0.51
    38    71.30s  energy 0.37  bass 0.45 (punch 1.00)  mid 0.36  high 0.50
    39    73.17s  energy 0.36  bass 0.44 (punch 1.00)  mid 0.43  high 0.52
```

```
$ cd "~/deadmau5 app"; KIT=tools/showkit; python3 $KIT/songmap.py "deadmau5 - Moar Ghosts n Stuff"; python3 mau5scene.py bars "deadmau5 - Moar Ghosts n Stuff" | head -40
deadmau5 - Moar Ghosts n Stuff: 144 bars, 1.88 s a bar, 270.0 s
 bar     t   E  B  M  H  notes       change
   0    0.0   8  8  8  2  C F A       
   1    1.9   7  8  6  2  C F A       
   2    3.8   7  8  4  2  C F A       
   3    5.7   7  8  7  3  C F A       
   4    7.5   7  8  6  0  A# C A      
   5    9.4   5  7  5  1  C F A       
   6   11.3   5  6  3  0  C A# F      
   7   13.2   5  6  3  0  A# F A      
   8   15.0   4  6  4  0  F C A       
   9   16.9   5  6  4  0  F C A       
  10   18.8   5  6  4  0  F C A       
  11   20.7   5  6  4  0  A# F A      
  12   22.5   6  6  4  1  A# A C      
  13   24.4   6  6  5  1  A# A C      
  14   26.3   9  6  9  3  A A# F      >>
  15   28.2   9  6  9  2  F A A#      
  16   30.0   8  6  9  2  A F A#      
  17   31.9   7  6  9  4  A F C       
  18   33.8   7  6  9  2  F A A#      
  19   35.7   7  6  9  5  A F A#      
  20   37.5   7  4  9  2  A# F A      >>
  21   39.4   7  5  9  1  F A G       
  22   41.3   6  6  8  1  A# A F      
  23   43.2   6  6  8  1  A# A F      
  24   45.0   5  3  8  1  F A# A      
  25   46.9   5  4  8  1  G# F G      
  26   48.8   6  5  3  5  C F A       >>
  27   50.7   6  5  3  5  C F A       
  28   52.5   6  5  3  5  C F A       
  29   54.4   6  5  3  5  C F A       
  30   56.3   6  5  3  5  C F A       
  31   58.2   5  5  3  5  F C A       
  32   60.0   5  5  3  5  C F A       
  33   61.9   5  5  3  5  C F A       
  34   63.8   5  5  3  5  C F A       
  35   65.7   5  5  3  5  C F A       
  36   67.5   5  5  3  5  C F A       
  37   69.4   5  5  4  6  C F A       
  38   71.3   5  5  4  5  C F A       
  39   73.2   5  5  4  6  C F A       
  40   75.0   3  0  7  6  A A# G#     >>
  41   76.9   5  1  8  8  F A A#      >>
  42   78.8   8  7  4  5  C F A       >>
  4
... [cut] ...

    32    60.05s  energy 0.39  bass 0.45 (punch 1.00)  mid 0.34  high 0.48
    33    61.92s  energy 0.39  bass 0.45 (punch 1.00)  mid 0.34  high 0.50
    34    63.80s  energy 0.39  bass 0.45 (punch 1.00)  mid 0.33  high 0.48
    35    65.67s  energy 0.39  bass 0.43 (punch 1.00)  mid 0.35  high 0.50
    36    67.55s  energy 0.38  bass 0.45 (punch 1.00)  mid 0.34  high 0.48
    37    69.42s  energy 0.38  bass 0.45 (punch 1.00)  mid 0.39  high 0.51
    38    71.30s  energy 0.37  bass 0.45 (punch 1.00)  mid 0.36  high 0.50
    39    73.17s  energy 0.36  bass 0.44 (punch 1.00)  mid 0.43  high 0.52
```

```
$ cd "~/deadmau5 app"; KIT=tools/showkit; W=$KIT/work/moarghosts; for r in "24 30" "38 46" "72 78" "90 96" "110 116" "126 132" "138 144"; do set -- $r; python3 $KIT/spectro.py "deadmau5 - Moar Ghosts n Stuff" $W/z$1.png $1 $2; done; python3 $KIT/grid.py fold "shows/deadmau5 - Moar Ghosts n Stuff.mp3" --spb 0.468770 --anchor 0.045 --spans "0-4,4-8,8-14,14-20,20-26,26-34,34-40,40-42,42-50,50-58,58-66,66-74,74-76,76-84,84-92,92-94,94-100,100-106,106-112,112-114,114-122,122-128,128-130,130-138,138-143"
Traceback (most recent call last):
  File "tools/showkit/spectro.py", line 12, in <module>
    lo = int(sys.argv[3]) if len(sys.argv) > 3 else 0
ValueError: invalid literal for int() with base 10: '24 30'
Traceback (most recent call last):
  File "tools/showkit/spectro.py", line 12, in <module>
    lo = int(sys.argv[3]) if len(sys.argv) > 3 else 0
ValueError: invalid literal for int() with base 10: '38 46'
Traceback (most recent call last):
  File "tools/showkit/spectro.py", line 12, in <module>
    lo = int(sys.argv[3]) if len(sys.argv) > 3 else 0
ValueError: invalid literal for int() with base 10: '72 78'
Traceback (most recent call last):
  File "tools/showkit/spectro.py", line 12, in <module>
    lo = int(sys.argv[3]) if len(sys.argv) > 3 else 0
ValueError: invalid literal for int() with base 10: '90 96'
Traceback (most recent call last):
  File "tools/showkit/spectro.py", line 12, in <module>
    lo = int(sys.argv[3]) if len(sys.argv) > 3 else 0
ValueError: invalid literal for int() with base 10: '110 116'
Traceback (most recent call last):
  File "tools/showkit/spectro.py", line 12, in <module>
    lo = int(sys.argv[3]) if len(sys.argv) > 3 else 0
ValueError: invalid literal for int() with base 10: '126 132'
Traceback (most recent call last):
  F
... [cut] ...
ry beat; one row per band)
   sub     @ . |%.:.|# : |% :    peak 0.71
   bass    @   |%:. |@ . |%::    peak 1.18
   lowmid  @:..|+.- |#.=.|-.:    peak 0.74
   mid     @...|= : |#.-.|= :    peak 0.83
   pres    @...|# - |%.- |* :    peak 0.91
   air     @.= |# * |@.* |# *    peak 0.85
bars 138-143   (16 steps, | every beat; one row per band)
   sub     @ ..|%.: |# : |% ..   peak 0.72
   bass    @.  |%:. |@.. |%.:    peak 1.19
   lowmid  @:..|#.- |%.=.|-.-    peak 0.75
   mid     @.  |+ : |%.:.|= -    peak 0.89
   pres    @ . |* - |%.- |+ -    peak 1.18
   air     @ = |* + |@ = |+ +    peak 1.18
```

```
$ cd "~/deadmau5 app"; KIT=tools/showkit; W=$KIT/work/moarghosts; python3 $KIT/spectro.py "deadmau5 - Moar Ghosts n Stuff" $W/z26.png 24 30; python3 $KIT/spectro.py "deadmau5 - Moar Ghosts n Stuff" $W/z42.png 38 46; python3 $KIT/spectro.py "deadmau5 - Moar Ghosts n Stuff" $W/z76.png 72 78; python3 $KIT/spectro.py "deadmau5 - Moar Ghosts n Stuff" $W/z94.png 90 96; python3 $KIT/spectro.py "deadmau5 - Moar Ghosts n Stuff" $W/z114.png 110 116; python3 $KIT/spectro.py "deadmau5 - Moar Ghosts n Stuff" $W/z130.png 126 132; python3 $KIT/spectro.py "deadmau5 - Moar Ghosts n Stuff" $W/z144.png 138 144; pyt ... [cut]
tools/showkit/songs/moarghosts/z26.png
tools/showkit/songs/moarghosts/z42.png
tools/showkit/songs/moarghosts/z76.png
tools/showkit/songs/moarghosts/z94.png
tools/showkit/songs/moarghosts/z114.png
tools/showkit/songs/moarghosts/z130.png
tools/showkit/songs/moarghosts/z144.png
tools/showkit/songs/moarghosts/z0.png
tools/showkit/songs/moarghosts/z14.png
```

```
$ cd "~/deadmau5 app"; grep -n "sprite" mau5engine.py | head -50; grep -n "class Sprite\|class Text\|class Eyes\|def make\|\"eyes\"\|\"text\"" mau5engine.py mau5fx.py | head -40
571:# Text and sprites.
624:def _sprite_bitmap(name):
707:    `sprite` may be several names joined by |, shown in turn `rate` times a
710:    of it is a function of t, so a moving sprite is still a pure function
713:    name = "sprite"
714:    params = {"sprite": "smile", "color": (0, 255, 255), "bg": (0, 0, 0),
722:        names = self.p["sprite"].split("|")
724:        bm = _sprite_bitmap(names[at])
mau5fx.py:165:    "eyes": [
mau5fx.py:567:class Sprite(GridEffect):
mau5fx.py:584:class SpriteFlipbook(GridEffect):
mau5fx.py:587:    def __init__(self, helmet, sprites=("eyes", "wink"), fps=2.0, col=None,
mau5engine.py:310:                out.append({"name": k, "kind": "text", "value": v})
mau5engine.py:674:class TextScroll(Preset):
mau5engine.py:676:    name = "text"
mau5engine.py:682:    params = {"text": "DEADMAU5", "color": (255, 160, 0), "bg": (0, 0, 0),
mau5engine.py:687:        bm = _text_bitmap(self.p["text"], spacing=1)
mau5engine.py:704:class SpriteShow(Preset):
mau5engine.py:743:class Eyes(Preset):
mau5engine.py:745:    name = "eyes"
mau5engine.py:1362:def make(name, **kw):
```

```
$ cd "~/deadmau5 app"; sed -n 565,800p mau5engine.py
    def render(self, h, t, music=None):
        k = self.p["floor"] + (1 - self.p["floor"]) * _beat(music, t, 0.5)
        return np.tile(np.array(self.p["color"]) * k, (h.n, 1))


# ----------------------------------------------------------------------
# Text and sprites.
#
# The shell is not a screen.  It is a patch of sphere with holes in it,
# and the strips that survive are different lengths.  So glyphs are
# rasterised into a small bitmap and then *sampled* by each LED's own
# position on the face, rather than blitted to a grid that does not
# exist.  LEDs that fall in a hole simply never sample a lit pixel.
# ----------------------------------------------------------------------

def _text_bitmap(text, spacing=1):
    """5x7 glyphs laid side by side -> (7, w) bool array."""
    cols = []
    for ch in text.upper():
        g = FONT5x7.get(ch, FONT5x7.get("?", (0, 0, 0, 0, 0)))
        for c in g:
            cols.append([(c >> r) & 1 for r in range(7)])
        cols.extend([[0] * 7] * spacing)
    if not cols:
        cols = [[0] * 7]
    return np.array(cols, bool).T          # (7, w)


# A 5x7 glyph held still on the dome gives 35 cells, and the LEDs are
# not spread evenly enough to fill them -- cells that happen to contain
# no LED drop out and the digit stops being readable.  Scrolling text
# survives that because the eye integrates over time; a held digit does
# not.  So digits get their own 3x5 face, where each cell is big enough
# to be certain of catching LEDs.
DIGIT3x5 = {
    "0": ("###", "# #", "# #", "# #", "###"),
    "1": (" # ", "## ", " # ", " # ", "###"),
    "2": ("###", "  #", "###", "#  ", "###"),
    "3": ("###", "  #", "###", "  #", "###"),
    "4": ("# #", "# #", "###", "  #", "  #"),
    "5": ("###", "#  ", "###", "  #", "###"),
    "6": 
... [cut] ...
= np.where(h.shell, h.group, -1)
        if not (col[h.shell] >= 0).any():          # no strips: azimuth bins
            nc = int(self.p["columns"])
            col = np.where(h.shell, np.clip((h.nfa * nc).astype(int), 0, nc - 1), -1)
        first = int(col.max()) + 1                # ear tubes after the strips
        on_tube = h.tube >= 0
        col = np.where(on_tube, first + h.tube + 3 * h.ear2.astype(int), col)
        pos = np.where(on_tube, 1.0 - h.along, 1.0 - h.nel)     # 0 at the top
        nc = int(col.max()) + 1
        seed = (np.sin(np.arange(nc) * 78.233) * 43758.5453) % 1.0
```

```
$ cd "~/deadmau5 app"; sed -n 215,520p mau5scene.py
class _Compiler:
    """Turns an authored treatment into the canonical, defaults-filled form."""

    def __init__(self, tr, grid, bars, h):
        self.tr, self.grid, self.bars, self.h = tr, grid, bars, h
        # Marks in order, each a number or an earlier mark plus or minus.
        self.marks = {}
        for k, v in (tr.get("marks") or {}).items():
            self.marks[k] = None
            self.marks[k] = self.bar(v, "mark %s" % k)
        self.pal = {}
        for name, p in (tr.get("palettes") or {}).items():
            if isinstance(p, dict):
                stops, wrap = p.get("stops"), bool(p.get("wrap", False))
            else:
                stops, wrap = p, False
            if not isinstance(stops, list) or len(stops) < 2:
                raise TreatmentError("palette %s needs two stops or more" % name)
            stops = [[int(round(float(x))) for x in s] for s in stops]
            for s in stops:
                if len(s) != 3 or min(s) < 0 or max(s) > 255:
                    raise TreatmentError("palette %s has a stop %r outside RGB"
                                         % (name, s))
            self.pal[name] = {"stops": stops, "wrap": wrap}
        if not self.pal:
            raise TreatmentError("a treatment needs at least one palette")
        self.motifs = tr.get("motifs") or {}

    # -- bars and values -------------------------------------------------
    def bar(self, v, what="bar"):
        """A bar: a number, a mark, or 'mark+N' / 'mark-N'."""
        if isinstance(v, bool):
            raise TreatmentError("%s: %r is not a bar" % (what, v))
        if isinstance(v, (int, float)):
            return float(v)
        if isinstance(v, str):
            s = v.strip()
            try:
                return float(s)
            exce
... [cut] ...
.layer(L, pal, "%s layer %d" % (what, j), beats))
            hits.append({"name": name, "at": at, "beats": beats, "layers": comp})
        hits.sort(key=lambda x: x["at"])
        for s in tiled:
            s.pop("_pal", None)
        grid = {"t0": self.grid["t0"], "spb": self.grid["spb"],
                "lead": float(tr.get("lead", 0.0))}
        if self.grid.get("holds"):
            grid["holds"] = self.grid["holds"]
        return {"v": 1, "src": "", "treatment": tr.get("_sha", ""),
                "grid": grid, "bars": nb, "pal": self.pal,
                "scenes": tiled, "hits": hits}
```

```
$ cd "~/deadmau5 app"; sed -n 596,800p mau5scene.py
def _region_mask(h, on):
    m = np.zeros(h.n, bool)
    for nm in str(on).split("+"):
        nm = nm.strip()
        if nm == "all":
            m[:] = True
        elif nm in ("shell", "ears", "ear1", "ear2", "tubes", "rims"):
            m |= np.asarray(getattr(h, nm), bool)
        elif nm in ("tube0", "tube1", "tube2"):
            m |= np.asarray(h.tube) == int(nm[-1])
        elif nm == "left":
            m |= np.asarray(h.shell, bool) & (np.asarray(h.fa) < 0)
        elif nm == "right":
            m |= np.asarray(h.shell, bool) & (np.asarray(h.fa) >= 0)
        elif nm == "face":
            m |= np.asarray(h.shell, bool) & (np.asarray(h.py) > 28)
        elif nm == "jaw":
            m |= np.asarray(h.shell, bool) & (np.asarray(h.py) <= 28)
        elif nm in ("rim1", "rim2"):
            m |= np.asarray(h.rims, bool) & np.asarray(getattr(h, "ear" + nm[-1]), bool)
        elif nm in ("tubes1", "tubes2"):
            m |= np.asarray(h.tubes, bool) & np.asarray(getattr(h, "ear" + nm[-1]), bool)
        else:
            raise TreatmentError("no region %r (have %s)" % (nm, ", ".join(REGIONS)))
    return m


def _min_gap_beats(pat, step):
    """The shortest cyclic distance between two sounding steps, in beats."""
    on = [i for i, ch in enumerate(pat) if ch != "."]
    if not on:
        return float("inf")
    L = len(pat)
    if len(on) == 1:
        return L * step
    gaps = [(on[(k + 1) % len(on)] - on[k]) % L or L for k in range(len(on))]
    return min(gaps) * step


def lint(spec, h=None, music=None):
    """(errors, warnings) for a compiled spec.  compile refuses on errors."""
    h = h or _helmet()
    errs, warns = [], []
    nb = spec["bars"]
    from mau5fx import SPRITES
    scenes, hits = spec["scenes"], spec["hits"]

    # tiling
    if not sc
... [cut] ...

                errs.append("%s: its text overlaps another text" % what)
    return errs, warns


# ----------------------------------------------------------------------
# the renderer
# ----------------------------------------------------------------------
def pal_lookup(stops, wrap, c):
    """One palette position -> RGB, as the JavaScript computes it."""
    n = len(stops)
    if wrap:
        x = (c % 1.0) * n
        i = math.floor(x)
        f = x - i
        i0 = i % n
        i1 = (i0 + 1) % n
    else:
        x = min(max(c, 0.0), 1.0) * (n - 1)
        i = min(math.floor(x), n - 2)
```

```
$ cd "~/deadmau5 app"; sed -n 565,800p mau5engine.py
    def render(self, h, t, music=None):
        k = self.p["floor"] + (1 - self.p["floor"]) * _beat(music, t, 0.5)
        return np.tile(np.array(self.p["color"]) * k, (h.n, 1))


# ----------------------------------------------------------------------
# Text and sprites.
#
# The shell is not a screen.  It is a patch of sphere with holes in it,
# and the strips that survive are different lengths.  So glyphs are
# rasterised into a small bitmap and then *sampled* by each LED's own
# position on the face, rather than blitted to a grid that does not
# exist.  LEDs that fall in a hole simply never sample a lit pixel.
# ----------------------------------------------------------------------

def _text_bitmap(text, spacing=1):
    """5x7 glyphs laid side by side -> (7, w) bool array."""
    cols = []
    for ch in text.upper():
        g = FONT5x7.get(ch, FONT5x7.get("?", (0, 0, 0, 0, 0)))
        for c in g:
            cols.append([(c >> r) & 1 for r in range(7)])
        cols.extend([[0] * 7] * spacing)
    if not cols:
        cols = [[0] * 7]
    return np.array(cols, bool).T          # (7, w)


# A 5x7 glyph held still on the dome gives 35 cells, and the LEDs are
# not spread evenly enough to fill them -- cells that happen to contain
# no LED drop out and the digit stops being readable.  Scrolling text
# survives that because the eye integrates over time; a held digit does
# not.  So digits get their own 3x5 face, where each cell is big enough
# to be certain of catching LEDs.
DIGIT3x5 = {
    "0": ("###", "# #", "# #", "# #", "###"),
    "1": (" # ", "## ", " # ", " # ", "###"),
    "2": ("###", "  #", "###", "#  ", "###"),
    "3": ("###", "  #", "###", "  #", "###"),
    "4": ("# #", "# #", "###", "  #", "  #"),
    "5": ("###", "#  ", "###", "  #", "###"),
    "6": 
... [cut] ...
= np.where(h.shell, h.group, -1)
        if not (col[h.shell] >= 0).any():          # no strips: azimuth bins
            nc = int(self.p["columns"])
            col = np.where(h.shell, np.clip((h.nfa * nc).astype(int), 0, nc - 1), -1)
        first = int(col.max()) + 1                # ear tubes after the strips
        on_tube = h.tube >= 0
        col = np.where(on_tube, first + h.tube + 3 * h.ear2.astype(int), col)
        pos = np.where(on_tube, 1.0 - h.along, 1.0 - h.nel)     # 0 at the top
        nc = int(col.max()) + 1
        seed = (np.sin(np.arange(nc) * 78.233) * 43758.5453) % 1.0
```

```
$ cd "~/deadmau5 app"; sed -n 215,520p mau5scene.py
class _Compiler:
    """Turns an authored treatment into the canonical, defaults-filled form."""

    def __init__(self, tr, grid, bars, h):
        self.tr, self.grid, self.bars, self.h = tr, grid, bars, h
        # Marks in order, each a number or an earlier mark plus or minus.
        self.marks = {}
        for k, v in (tr.get("marks") or {}).items():
            self.marks[k] = None
            self.marks[k] = self.bar(v, "mark %s" % k)
        self.pal = {}
        for name, p in (tr.get("palettes") or {}).items():
            if isinstance(p, dict):
                stops, wrap = p.get("stops"), bool(p.get("wrap", False))
            else:
                stops, wrap = p, False
            if not isinstance(stops, list) or len(stops) < 2:
                raise TreatmentError("palette %s needs two stops or more" % name)
            stops = [[int(round(float(x))) for x in s] for s in stops]
            for s in stops:
                if len(s) != 3 or min(s) < 0 or max(s) > 255:
                    raise TreatmentError("palette %s has a stop %r outside RGB"
                                         % (name, s))
            self.pal[name] = {"stops": stops, "wrap": wrap}
        if not self.pal:
            raise TreatmentError("a treatment needs at least one palette")
        self.motifs = tr.get("motifs") or {}

    # -- bars and values -------------------------------------------------
    def bar(self, v, what="bar"):
        """A bar: a number, a mark, or 'mark+N' / 'mark-N'."""
        if isinstance(v, bool):
            raise TreatmentError("%s: %r is not a bar" % (what, v))
        if isinstance(v, (int, float)):
            return float(v)
        if isinstance(v, str):
            s = v.strip()
            try:
                return float(s)
            exce
... [cut] ...
.layer(L, pal, "%s layer %d" % (what, j), beats))
            hits.append({"name": name, "at": at, "beats": beats, "layers": comp})
        hits.sort(key=lambda x: x["at"])
        for s in tiled:
            s.pop("_pal", None)
        grid = {"t0": self.grid["t0"], "spb": self.grid["spb"],
                "lead": float(tr.get("lead", 0.0))}
        if self.grid.get("holds"):
            grid["holds"] = self.grid["holds"]
        return {"v": 1, "src": "", "treatment": tr.get("_sha", ""),
                "grid": grid, "bars": nb, "pal": self.pal,
                "scenes": tiled, "hits": hits}
```

```
$ cd "~/deadmau5 app"; sed -n 596,800p mau5scene.py
def _region_mask(h, on):
    m = np.zeros(h.n, bool)
    for nm in str(on).split("+"):
        nm = nm.strip()
        if nm == "all":
            m[:] = True
        elif nm in ("shell", "ears", "ear1", "ear2", "tubes", "rims"):
            m |= np.asarray(getattr(h, nm), bool)
        elif nm in ("tube0", "tube1", "tube2"):
            m |= np.asarray(h.tube) == int(nm[-1])
        elif nm == "left":
            m |= np.asarray(h.shell, bool) & (np.asarray(h.fa) < 0)
        elif nm == "right":
            m |= np.asarray(h.shell, bool) & (np.asarray(h.fa) >= 0)
        elif nm == "face":
            m |= np.asarray(h.shell, bool) & (np.asarray(h.py) > 28)
        elif nm == "jaw":
            m |= np.asarray(h.shell, bool) & (np.asarray(h.py) <= 28)
        elif nm in ("rim1", "rim2"):
            m |= np.asarray(h.rims, bool) & np.asarray(getattr(h, "ear" + nm[-1]), bool)
        elif nm in ("tubes1", "tubes2"):
            m |= np.asarray(h.tubes, bool) & np.asarray(getattr(h, "ear" + nm[-1]), bool)
        else:
            raise TreatmentError("no region %r (have %s)" % (nm, ", ".join(REGIONS)))
    return m


def _min_gap_beats(pat, step):
    """The shortest cyclic distance between two sounding steps, in beats."""
    on = [i for i, ch in enumerate(pat) if ch != "."]
    if not on:
        return float("inf")
    L = len(pat)
    if len(on) == 1:
        return L * step
    gaps = [(on[(k + 1) % len(on)] - on[k]) % L or L for k in range(len(on))]
    return min(gaps) * step


def lint(spec, h=None, music=None):
    """(errors, warnings) for a compiled spec.  compile refuses on errors."""
    h = h or _helmet()
    errs, warns = [], []
    nb = spec["bars"]
    from mau5fx import SPRITES
    scenes, hits = spec["scenes"], spec["hits"]

    # tiling
    if not sc
... [cut] ...

                errs.append("%s: its text overlaps another text" % what)
    return errs, warns


# ----------------------------------------------------------------------
# the renderer
# ----------------------------------------------------------------------
def pal_lookup(stops, wrap, c):
    """One palette position -> RGB, as the JavaScript computes it."""
    n = len(stops)
    if wrap:
        x = (c % 1.0) * n
        i = math.floor(x)
        f = x - i
        i0 = i % n
        i1 = (i0 + 1) % n
    else:
        x = min(max(c, 0.0), 1.0) * (n - 1)
        i = min(math.floor(x), n - 2)
```

```
$ cd "~/deadmau5 app"; cat > tools/showkit/songs/moarghosts/map.py <<'EOF'
import sys, os
sys.path.insert(0, os.getcwd())
import numpy as np, mau5engine as E
h = E.Helmet()
s = h.shell
print("n", h.n, "shell", s.sum(), "px", h.px[s].min(), h.px[s].max(), "py", h.py[s].min(), h.py[s].max())
print("ears px", h.px[h.ears].min(), h.px[h.ears].max(), "py", h.py[h.ears].min(), h.py[h.ears].max())
# ascii map at 16 mm
xs = np.arange(-176, 177, 16); ys = np.arange(176, -113, -16)
for y in ys:
    row = ""
    for x in xs:
        n = ((h.px[s] >= x) & (h.px[s] < x+16) & (h.py[s] < y) & (h.py[s] >= y-16)). ... [cut]
n 621 shell 398 px -170.94 170.95 py -111.27 167.77
ears px -388.21 387.42 py 51.8 384.91
  176  . . . . . . . 1 . . 1 2 . . . . . . . . . . .
  160  . . . . . 3 4 4 2 3 2 2 2 3 2 5 2 . . . . . .
  144  . . . 3 7 5 4 3 4 2 4 4 2 4 3 4 5 7 3 . . . .
  128  . . . 5 3 . 1 2 1 2 1 1 2 1 2 1 . 3 5 . . . .
  112  . . 4 3 2 1 2 1 1 2 1 1 2 1 1 2 1 2 3 4 . . .
   96  . 2 4 2 1 2 1 1 2 1 1 1 1 2 1 1 2 1 2 4 2 . .
   80  . 4 3 1 2 1 1 2 1 1 1 1 1 1 2 1 1 2 1 3 4 . .
   64  2 3 2 2 1 1 2 1 1 1 1 1 1 1 1 2 1 1 2 2 3 2 .
   48  3 3 2 1 1 1 . . . . . . . . . . 1 1 1 2 3 3 .
   32  4 2 . . . . . . . . . . . . . . . . . . 2 4 .
   16  1 . . . . . . . . . . . . . . . . . . . . 1 .
    0  . . . . . . . . . . . . . . . . . . . . . . .
  -16  1 . . . . . . . . . . . . . . . . . . . . 1 .
  -32  3 . . . . . . . . . . . . . . . . . . . . 3 .
  -48  3 1 . . . . . . . . . . . . . . . . . . 1 3 .
  -64  . 5 1 . . . . . . . . . . . . . . . . 1 5 . .
  -80  . 3 3 2 . . . . . . . . . . . . . . 2 3 3 . .
  -96  . . 8 5 4 3 2 1 1 1 . . 1 1 1 2 3 4 5 8 . . .
 -112  . . . . . . . . . . . . . . . . . . . . . . .
mau5fx.py:146:    "tiki": [
mau5fx.py:249:# Sprites a song brings with it: shows/scenes/<song>.sprites.json, {name: [rows]},
mau5fx.py:256:        sheets = sorted(f for f in os.listdir(d) if f.endswith(".sprites.json"))
146:    "tiki": [
147-        ".XXXXXXXXXXXXXXX.",
148-        ".................",
149-        ".XXXXXXX.XXXXXXX.",
150-        ".XXXXXXX.XXXXXXX.",
151-        ".XX...XX.XX...XX.",
152-        ".XX...XX.XX...XX.",
153-        ".XXXXXXX.XXXXXXX.",
154-        ".................",
155-        "X...............X",
156-        "X...............X",
157-        ".................",
158-        ".................",
159-        "X...............X",
160-        "X...............X",
161-        ".XX.XX.....XX.XX.",
162-        "..X.XX.XXX.XX.X..",
163-        "...X..X...X..X...",
164-    ],
165-    "eyes": [
166-        ".XXXXX.....XXXXX.",
167-        "XXXXXXX...XXXXXXX",
168-        "XXXXXXX...XXXXXXX",
```

```
$ cd "~/deadmau5 app"; sed -n 800,1200p mau5scene.py
        i = min(math.floor(x), n - 2)
        f = x - i
        i0, i1 = i, i + 1
    s0, s1 = stops[i0], stops[i1]
    return np.array([s0[0] + (s1[0] - s0[0]) * f, s0[1] + (s1[1] - s0[1]) * f,
                     s0[2] + (s1[2] - s0[2]) * f])


def _pal_vec(P, c):
    stops, wrap, n = P
    if wrap:
        x = np.mod(c, 1.0) * n
        i = np.floor(x)
        f = x - i
        i0 = i.astype(int) % n
        i1 = (i0 + 1) % n
    else:
        x = np.clip(c, 0.0, 1.0) * (n - 1)
        i = np.minimum(np.floor(x), n - 2)
        f = x - i
        i0 = i.astype(int)
        i1 = i0 + 1
    s0, s1 = stops[i0], stops[i1]
    return s0 + (s1 - s0) * f[:, None]


def _hash_sin(x):
    return (math.sin(x) * 43758.5453) % 1.0


def _h32(h):
    """The helmet as the phone has it: every float through float32 once.

    bundle() ships the geometry as float32, so an axis read on the phone
    is the float32 nearest the laptop's.  Working from the same bytes
    here is what lets the two agree to the bit instead of to a count.
    """
    g = copy.copy(h)
    for k in ("px", "py", "nx", "ny", "nfa", "nel", "u", "fa", "ea", "er",
              "along", "depth", "xyz"):
        setattr(g, k, np.asarray(getattr(h, k)).astype("<f4").astype(float))
    return g


def _gate(lb, pat, step, decay, floor, HB):
    """A rhythm pattern as a gain: newest sounding step, held, then decaying."""
    L = len(pat)
    si = math.floor(lb / step)
    for k in range(L):
        ch = pat[(si - k) % L]
        if ch != ".":
            amp = 1.0 if ch == "x" else 0.5
            age = lb - (si - k) * step
            x = max(0.0, age - HB)
            e = max(0.0, 1.0 - x / decay)
            return floor + (1.0 - floor) * amp * e * e
    return floor


class _Val:
    __slots__ = ("kind", "a", "b", 
... [cut] ...
c, 0, 255)
        gain = 1.0
        if sc["pump"] is not None:
            pat, step, decay, depth = sc["pump"]
            gain = 1 - depth + depth * _gate(lb, pat, step, decay, 0.0, self.HB)
        return out, gain, label


# ----------------------------------------------------------------------
# what the bar map says, for writing marks against
# ----------------------------------------------------------------------
def bar_stats(music):
    """Per bar: energy, bass, bass punch peak, mid, high, high punch peak."""
    fps = music.fps
    e = np.clip(np.asarray(music.energy, float), 0, 1)
```

```
$ cd "~/deadmau5 app"; sed -n 1,125p mau5scene.py; sed -n 245,285p mau5fx.py
#!/usr/bin/env python3
"""mau5scene -- shows choreographed per song, instead of a playlist of effects.

A cue-list show (mau5show.build) picks a stock preset for each phrase
from a pool and holds it.  It follows the music's level and lands on its
beats, and it still reads as a playlist: the same eight effects in a
different order for every song, none of them about the song.  What the
owner asked for is what deadmau5's own shows do -- each track gets its
own visual language: its own colours, its own motifs that come back
when the music does, builds that visibly grow, drops that land on the
bar the bass lands on, a breakdown stripped back to almost nothing, a
title that crosses the face once, and the ears played as an instrument
of their own rather than as more screen.

So a song owns a treatment, shows/scenes/<base>.scene.json, written by
hand in bars against that song's own bar map, and this module compiles
it into the show it belongs to as `show["scenes"]`.  The cue list stays
where it is, untouched, and is what plays if the scenes are absent,
switched off (`mode: "cues"`, MAU5_CUES=1, `?cues` on the phone) or
throw.

Every frame is a pure function of the time, plus optionally the band
curves, on the analysis' beat grid -- which is exactly linear for every
shipped song (the spread of beat intervals is about 2e-14 s), apart from
any seam where the track was edited and the music comes back late, which
the grid holds still for (grid_of).  That one decision buys three things.  The phone and the laptop can agree to the
last bit, because there is no state for them to disagree about.  Seeking
and pausing cost nothing.  And the show stays in sync from the audio
element's own clock whether or not the phone ever fetched a drive file.

    python3 mau5scene.py bars    "deadmau5 -
... [cut] ...
(rows)
        except (OSError, ValueError) as e:
            print("  %s: %s" % (fn, e))


_song_sprites()


def sprite_bitmap(name_or_rows):
    rows = SPRITES[name_or_rows] if isinstance(name_or_rows, str) else name_or_rows
    w = max(len(r) for r in rows)
    return np.array([[c not in ".  " for c in r.ljust(w)] for r in rows], bool)


# --------------------------------------------------------------------------
# beats
# --------------------------------------------------------------------------
class Beats:
    """A pre-computed beat list.  No live audio analysis -- shows are authored."""
```

```
$ cd "~/deadmau5 app"; sed -n 800,1200p mau5scene.py
        i = min(math.floor(x), n - 2)
        f = x - i
        i0, i1 = i, i + 1
    s0, s1 = stops[i0], stops[i1]
    return np.array([s0[0] + (s1[0] - s0[0]) * f, s0[1] + (s1[1] - s0[1]) * f,
                     s0[2] + (s1[2] - s0[2]) * f])


def _pal_vec(P, c):
    stops, wrap, n = P
    if wrap:
        x = np.mod(c, 1.0) * n
        i = np.floor(x)
        f = x - i
        i0 = i.astype(int) % n
        i1 = (i0 + 1) % n
    else:
        x = np.clip(c, 0.0, 1.0) * (n - 1)
        i = np.minimum(np.floor(x), n - 2)
        f = x - i
        i0 = i.astype(int)
        i1 = i0 + 1
    s0, s1 = stops[i0], stops[i1]
    return s0 + (s1 - s0) * f[:, None]


def _hash_sin(x):
    return (math.sin(x) * 43758.5453) % 1.0


def _h32(h):
    """The helmet as the phone has it: every float through float32 once.

    bundle() ships the geometry as float32, so an axis read on the phone
    is the float32 nearest the laptop's.  Working from the same bytes
    here is what lets the two agree to the bit instead of to a count.
    """
    g = copy.copy(h)
    for k in ("px", "py", "nx", "ny", "nfa", "nel", "u", "fa", "ea", "er",
              "along", "depth", "xyz"):
        setattr(g, k, np.asarray(getattr(h, k)).astype("<f4").astype(float))
    return g


def _gate(lb, pat, step, decay, floor, HB):
    """A rhythm pattern as a gain: newest sounding step, held, then decaying."""
    L = len(pat)
    si = math.floor(lb / step)
    for k in range(L):
        ch = pat[(si - k) % L]
        if ch != ".":
            amp = 1.0 if ch == "x" else 0.5
            age = lb - (si - k) * step
            x = max(0.0, age - HB)
            e = max(0.0, 1.0 - x / decay)
            return floor + (1.0 - floor) * amp * e * e
    return floor


class _Val:
    __slots__ = ("kind", "a", "b", 
... [cut] ...
c, 0, 255)
        gain = 1.0
        if sc["pump"] is not None:
            pat, step, decay, depth = sc["pump"]
            gain = 1 - depth + depth * _gate(lb, pat, step, decay, 0.0, self.HB)
        return out, gain, label


# ----------------------------------------------------------------------
# what the bar map says, for writing marks against
# ----------------------------------------------------------------------
def bar_stats(music):
    """Per bar: energy, bass, bass punch peak, mid, high, high punch peak."""
    fps = music.fps
    e = np.clip(np.asarray(music.energy, float), 0, 1)
```

```
$ cd "~/deadmau5 app"; sed -n 1,125p mau5scene.py; sed -n 245,285p mau5fx.py
#!/usr/bin/env python3
"""mau5scene -- shows choreographed per song, instead of a playlist of effects.

A cue-list show (mau5show.build) picks a stock preset for each phrase
from a pool and holds it.  It follows the music's level and lands on its
beats, and it still reads as a playlist: the same eight effects in a
different order for every song, none of them about the song.  What the
owner asked for is what deadmau5's own shows do -- each track gets its
own visual language: its own colours, its own motifs that come back
when the music does, builds that visibly grow, drops that land on the
bar the bass lands on, a breakdown stripped back to almost nothing, a
title that crosses the face once, and the ears played as an instrument
of their own rather than as more screen.

So a song owns a treatment, shows/scenes/<base>.scene.json, written by
hand in bars against that song's own bar map, and this module compiles
it into the show it belongs to as `show["scenes"]`.  The cue list stays
where it is, untouched, and is what plays if the scenes are absent,
switched off (`mode: "cues"`, MAU5_CUES=1, `?cues` on the phone) or
throw.

Every frame is a pure function of the time, plus optionally the band
curves, on the analysis' beat grid -- which is exactly linear for every
shipped song (the spread of beat intervals is about 2e-14 s), apart from
any seam where the track was edited and the music comes back late, which
the grid holds still for (grid_of).  That one decision buys three things.  The phone and the laptop can agree to the
last bit, because there is no state for them to disagree about.  Seeking
and pausing cost nothing.  And the show stays in sync from the audio
element's own clock whether or not the phone ever fetched a drive file.

    python3 mau5scene.py bars    "deadmau5 -
... [cut] ...
(rows)
        except (OSError, ValueError) as e:
            print("  %s: %s" % (fn, e))


_song_sprites()


def sprite_bitmap(name_or_rows):
    rows = SPRITES[name_or_rows] if isinstance(name_or_rows, str) else name_or_rows
    w = max(len(r) for r in rows)
    return np.array([[c not in ".  " for c in r.ljust(w)] for r in rows], bool)


# --------------------------------------------------------------------------
# beats
# --------------------------------------------------------------------------
class Beats:
    """A pre-computed beat list.  No live audio analysis -- shows are authored."""
```

```
$ cd "~/deadmau5 app"; date; python3 - <<'EOF'
import sys,os
sys.path.insert(0,os.getcwd())
import numpy as np, mau5engine as E
h=E.Helmet()
print("rims",h.rims.sum(),"tubes",h.tubes.sum())
for ear,nm in ((h.ear1,"ear1"),(h.ear2,"ear2")):
    r=h.rims&ear
    print(nm,"rim leds",r.sum(),"px",h.px[r].min(),h.px[r].max(),"py",h.py[r].min(),h.py[r].max(),"u",h.u[r].min(),h.u[r].max())
    print(" a range",h.ea[r].min(),h.ea[r].max()," a sorted sample",np.round(np.sort(h.ea[r])[::5],2))
    idx=np.where(r)[0]; o=np.argsort(h.ea[idx]); print(" first by angle (px,py):",[(int(h.px[idx[i]]),int(h.py[idx[i]])) for i in o[::6]])
    for t in range(3):
        m=(np.asarray(h.tube)==t)&ear
    ... [cut]
Sat Oct 31 12:45:19 PDT 2026
rims 37 tubes 186
ear1 rim leds 18 px -388.21 -55.76 py 51.8 383.94 u 0.0 1.0
 a range 0.04005365891665192 0.997482576530402  a sorted sample [0.04 0.27 0.54 0.76]
 first by angle (px,py): [(-57, 257), (-317, 348), (-342, 97)]
 tube 0 30 px -349 -201 py 66 215 along 0.02 0.89 u 0.688 1.0
 tube 1 36 px -309 -130 py 128 302 along 0.17 0.94 u 0.301 0.677
 tube 2 28 px -237 -86 py 215 349 along 0.13 0.95 u 0.0 0.29
ear2 rim leds 19 px 55.56 387.42 py 54.72 384.91 u 0.0 1.0
 a range 0.019912212211214027 0.9762159819552101  a sorted sample [0.02 0.26 0.5  0.84]
 first by angle (px,py): [(386, 235), (159, 376), (181, 58), (387, 191)]
 tube 0 28 px 207 357 py 70 214 along 0.05 0.92 u 0.703 1.0
 tube 1 36 px 132 322 py 126 305 along 0.15 0.97 u 0.308 0.692
 tube 2 28 px 83 236 py 205 348 along 0.09 0.95 u 0.0 0.297
Bars of the measured grid in the .beats beside this file: bar b starts at 0.129 + 1.714 b seconds, 243 bars. Ghosts drift over the shell whenever the track empties out. The drops are half-time: the kick on the rims, the snare on beat three across the shell, and in the B sections the left half and ear 1 call on beat one while the right half and ear 2 answer on beat three. Drop 2 lands at bar 64, on the sixteen-bar grid like the others; the bar before it is a pickup, the sub swelling under the build. White once, on drop 3.
[('ghost', [[0, 0, 0], [0, 60, 45], [40, 255, 160], [200, 255, 235]]), ('acid', [[0, 0, 0], [40, 255, 0], [150, 0, 255], [255, 255, 255]]), ('nero', {'stops': [[255, 0, 70], [140, 0, 255], [50, 255, 0]], 'wrap': True}), ('pure', [[0, 255, 0], [150, 0, 255], [255, 255, 255]])]
sub    26- 40 %@.     |-%.     |#@.     |-@.     
sub    42- 74 #@....  |*%....  |#@....  |+@....  
sub    76- 92 #@....  |*%....  |%@....  |*%....  
sub   114-128 @@....  |#%....  |%@......|#@....  
sub   130-143 @@....  |%@...:  |%@......|#@....  
pres   26- 40 : ...:..|@.  ::  |:   :::-|%.  ::  
pres   42- 74 -  .:::-|@.  ::  |-   -:-=|@.  --. 
pres   76- 92 -  .::.-|@.  ::  |-   ::-=|#   ::. 
pres  114-128 - .:---+|@...-=::|= .:==+*|#. .:-:.
pres  130-143 = :-=+=@|#..:==--|=..:==+#|%...--::
air    26- 40 =   ..  |@%  :.  |=   :...|@%  :.  
air    42- 74 *  .=:.-|@+  +:  |*   +..:|@*  +.  
air    76- 92 * ..#::=|@*  @: .|*   %:.=|@*  @:  
air   114-128 =  .::.-|@+ .::..|*  .-::+|%*  :..:
air   130-143 + .:%--%|#+..@-::|* .:%::+|@* .@:.-
```

```
$ mkdir -p "tools/showkit/songs/moarghosts"; cat > "tools/showkit/songs/moarghosts/sprites.py" <<'EOF'
#!/usr/bin/env python3
"""Draws the world of Moar Ghosts n Stuff and writes the sprite sheet. Run from the repo root."""
import json
P = "moar_"
S = {}
def add(name, rows):
    w = {len(r) for r in rows}
    assert len(w) == 1, (name, w)
    S[P + name] = rows

# --- small ghost, 8 x 8 cells: looks right / left / ahead, two skirts
def small(eyes, hem):
    return ["..XXXX..",
            ".XXXXXX.",
            eyes,
     ... [cut]
28 sprites
tools/showkit/songs/moarghosts/t1.png (1440, 338)
tools/showkit/songs/moarghosts/t2.png (1440, 338)
```

```
$ cd "~/deadmau5 app"; KIT=tools/showkit; W=$KIT/work/moarghosts; python3 $KIT/spectro.py "deadmau5 - Moar Ghosts n Stuff" $W/z95.png 94 112; python3 $KIT/spectro.py "deadmau5 - Moar Ghosts n Stuff" $W/z54.png 54 62; date
tools/showkit/songs/moarghosts/z95.png
tools/showkit/songs/moarghosts/z54.png
Sat Oct 31 12:46:44 PDT 2026
```

```
$ cd "~/deadmau5 app"; python3 - <<'EOF'
import sys,os
sys.path.insert(0,os.getcwd())
import numpy as np, mau5engine as E
h=E.Helmet()
for ear in (h.ear1,h.ear2):
    r=h.rims&ear
    idx=np.where(r)[0]; o=np.argsort(h.ea[idx])
    print([ (round(float(h.ea[idx[i]]),3), int(h.px[idx[i]]), int(h.py[idx[i]])) for i in o])
EOF
date
[(0.04, -57, 257), (0.09, -76, 307), (0.133, -105, 343), (0.19, -158, 375), (0.223, -193, 383), (0.266, -238, 382), (0.349, -317, 348), (0.385, -344, 323), (0.433, -371, 282), (0.5, -388, 215), (0.541, -384, 173), (0.582, -368, 131), (0.623, -342, 97), (0.687, -286, 61), (0.751, -221, 51), (0.764, -207, 53), (0.97, -60, 185), (0.997, -55, 212)]
[(0.02, 386, 235), (0.068, 371, 282), (0.11, 349, 318), (0.166, 307, 355), (0.204, 272, 374), (0.257, 217, 384), (0.312, 159, 376), (0.37, 105, 343), (0.414, 75, 306), (0.458, 58, 260), (0.5, 55, 215), (0.534, 62, 179), (0.706, 181, 58), (0.722, 197, 54), (0.787, 263, 54), (0.838, 313, 73), (0.882, 348, 102), (0.922, 371, 137), (0.976, 387, 191)]
Sat Oct 31 12:49:56 PDT 2026
```

```
$ cat > "tools/showkit/songs/moarghosts/sprites.py" <<'EOF'
#!/usr/bin/env python3
"""Draws the world of Moar Ghosts n Stuff and writes the sprite sheet. Run from the repo root."""
import json
P = "moar_"
S = {}
def add(name, rows):
    w = {len(r) for r in rows}
    assert len(w) == 1, (name, w)
    S[P + name] = rows

# --- small ghost, 8 x 8 cells: looks right / left / ahead, two skirts
def small(eyes, hem):
    return ["..XXXX..",
            ".XXXXXX.",
            eyes,
            eyes,
            "XXXXXXXX",
            "XXXXXXXX",
            "XXXXXXXX",
            hem]
HEM_A = "X.XX.XX."
HEM_B =  ... [cut]
37 sprites
tools/showkit/songs/moarghosts/t1.png (1440, 338)
tools/showkit/songs/moarghosts/t2.png (1440, 338)
tools/showkit/songs/moarghosts/t3.png (360, 338)
tools/showkit/songs/moarghosts/t4.png (720, 338)
```

```
$ cat > "tools/showkit/songs/moarghosts/gen.py" <<'EOF'
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
ROW = dict(y_lo=48, ... [cut]
wrote shows/scenes/deadmau5 - Moar Ghosts n Stuff.scene.json scenes 31 hits 15
     128   240.06s  energy 0.41  bass 0.26 (punch 0.23)  mid 0.64  high 0.53
     129   241.93s  energy 0.46  bass 0.42 (punch 0.70)  mid 0.59  high 0.64
  final      bar 130
     129   241.93s  energy 0.46  bass 0.42 (punch 0.70)  mid 0.59  high 0.64
     130   243.81s  energy 0.61  bass 0.65 (punch 1.00)  mid 0.62  high 0.75
     131   245.68s  energy 0.62  bass 0.69 (punch 1.00)  mid 0.49  high 0.59
  final2     bar 138
     137   256.93s  energy 0.61  bass 0.70 (punch 1.00)  mid 0.55  high 0.58
     138   258.81s  energy 0.58  bass 0.65 (punch 1.00)  mid 0.42  high 0.52
     139   260.68s  energy 0.62  bass 0.69 (punch 1.00)  mid 0.45  high 0.55
  chord      bar 140
     139   260.68s  energy 0.62  bass 0.69 (punch 1.00)  mid 0.45  high 0.55
     140   262.56s  energy 0.65  bass 0.77 (punch 0.58)  mid 0.62  high 0.61
     141   264.43s  energy 0.58  bass 0.70 (punch 1.00)  mid 0.53  high 0.59
  last       bar 143
     142   266.31s  energy 0.58  bass 0.65 (punch 1.00)  mid 0.48  high 0.55
     143   268.18s  energy 0.62  bass 0.68 (punch 1.00)  mid 0.63  high 0.63
  end        bar 144
     143   268.18s  energy 0.62  bass 0.68 (punch 1.00)  mid 0.63  high 0.63
deadmau5 - Moar Ghosts n Stuff: 32 scenes, 15 hits, written into shows/deadmau5 - Moar Ghosts n Stuff.json
Sat Oct 31 12:52:29 PDT 2026
```

```
$ cd "~/deadmau5 app"; KIT=tools/showkit; W=$KIT/work/moarghosts; time python3 $KIT/sheet.py "deadmau5 - Moar Ghosts n Stuff" $W/s1.png 0.25:attract 1.5:attract 2.5 3.75:drain 7:dark 11 16:voice 17.5 21:title 22.5 24.5 26.1:game 28 30 32 35 39.6 41:pellet 41.8 42:drop 42.25 44.5 46 54 57 57.5 58.1 60 62 67 68 70 75 2>&1 | tail -34; date
bar 0.25    attract        shell max 153 mean  17.9   ears max 159 mean   5.7   attract · WAKA 0
bar 1.5     attract        shell max 153 mean  51.9   ears max 113 mean   3.5   attract · WAKA 0
bar 2.5                    shell max 153 mean  41.4   ears max 178 mean   4.3   attract · WAKA 0
bar 3.75    drain          shell max  25 mean   5.2   ears max   0 mean   0.0   drain
bar 7       dark           shell max  86 mean  11.9   ears max 137 mean   7.5   afterdark
bar 11                     shell max  98 mean  14.7   ears max 140 mean   7.4   afterdark
bar 16      voice          shell max 118 mean  22.3   ears max  76 mean  19.6   voice
bar 17.5                   shell max 120 mean  22.6   ears max  76 mean  20.2   voice
bar 21      title          shell max 153 mean  30.2   ears max  67 mean   1.1   banner · TITLE
bar 22.5                   shell max 153 mean  23.9   ears max  85 mean   6.6   banner · TITLE
bar 24.5                   shell max 153 mean  32.7   ears max  87 mean  13.8   banner · TITLE
bar 26.1    game           shell max 153 mean  12.4   ears max 115 mean   5.4   game · WAKA 26
bar 28                     shell max 153 mean  31.9   ears max 115 mean   5.1   game · WAKA 26
bar 30                     shell max 153 mean  56.5   ears max 115 mean   5.1   game · WAKA 26
bar 32                     shell max 153 mean  38.4   ears max 115 mean   5.1   game · WAKA 26
bar 35                     shell max 153 mean  21.8   ears max 115 mean   5.1   gameback · WAKA 26
bar 39.6                   shell max 153 mean  19.7   ears max 151 mean   3.1   gameback · WAKA 26
bar 41      pellet         shell max 154 mean   6.6   ears max  76 mean  21.2   pellet
bar 41.8                   shell max   0 mean   0.0   ears max 204 mean  32.4   pellet · NOISE 41.75
bar 42      drop    
... [cut] ...
              shell max  51 mean  18.6   ears max 128 mean  13.1   intermission
bar 70                     shell max  51 mean  18.6   ears max 128 mean  13.1   intermission
bar 75                     shell max 154 mean   7.5   ears max  76 mean  21.2   stop
tools/showkit/songs/moarghosts/s1.png (1800, 1470)
python3 $KIT/sheet.py "deadmau5 - Moar Ghosts n Stuff" $W/s1.png 0.25:attract  0.49s user 0.03s system 99% cpu 0.526 total
tail -34  0.00s user 0.00s system 0% cpu 0.526 total
Sat Oct 31 12:52:35 PDT 2026
```

```
$ cd "~/deadmau5 app"; KIT=tools/showkit; W=$KIT/work/moarghosts; python3 $KIT/sheet.py "deadmau5 - Moar Ghosts n Stuff" $W/s2.png 76:drop2 76.25 78 80.25 84.5 88 91.5 92.2:eaten 93.5 94:boo 94.25 94.6 95.2 96 99 103 107 111 112.5 113.8 114:drop3 114.25 116 118.25 123 127 129 130:final 130.25 133 136 138.25 141 143.2 143.8 2>&1 | tail -36; date
bar 76      drop2          shell max 179 mean  60.5   ears max 242 mean 128.0   bigfright · POWER 2
bar 76.25                  shell max 255 mean 123.4   ears max 255 mean 100.0   bigfright · POWER 2
bar 78                     shell max 178 mean  60.2   ears max 128 mean  13.2   bigfright
bar 80.25                  shell max 178 mean  60.2   ears max 128 mean  13.3   bigfright
bar 84.5                   shell max 178 mean  60.2   ears max 128 mean  13.2   bigflick
bar 88                     shell max 235 mean 103.3   ears max 128 mean  13.2   bigflick
bar 91.5                   shell max 178 mean  60.2   ears max 128 mean  13.2   bigflick
bar 92.2    eaten          shell max 189 mean   9.5   ears max   0 mean   0.0   eaten
bar 93.5                   shell max  89 mean   3.1   ears max   0 mean   0.0   eaten
bar 94      boo            shell max 128 mean  32.1   ears max 188 mean  54.3   lone · BOO
bar 94.25                  shell max 178 mean  43.9   ears max 163 mean  45.9   lone · BOO
bar 94.6                   shell max 178 mean  49.6   ears max 130 mean  34.0   lone · BOO
bar 95.2                   shell max 178 mean  23.3   ears max  68 mean  13.6   lone · BOO
bar 96                     shell max  51 mean   4.8   ears max  48 mean   3.4   lone
bar 99                     shell max 107 mean   9.9   ears max  59 mean   4.7   lone2
bar 103                    shell max 117 mean  16.2   ears max  67 mean   2.4   lone3
bar 107                    shell max 128 mean  16.0   ears max  89 mean   4.9   lone4
bar 111                    shell max 128 mean  15.4   ears max  87 mean   8.1   swell
bar 112.5                  shell max 119 mean   7.2   ears max  76 mean   6.9   pellet3
bar 113.8                  shell max   0 mean   0.0   ears max 204 mean  31.6   pellet3 · NOISE 113.
... [cut] ...
ell max 242 mean  53.2   ears max 177 mean  18.4   final · WAKA 130
bar 138.25                 shell max 166 mean  14.5   ears max 159 mean   5.7   final2 · WAKA 138
bar 141                    shell max 166 mean  58.3   ears max 115 mean   5.1   final2 · WAKA 138
bar 143.2                  shell max  71 mean  32.9   ears max   0 mean   0.0   last
bar 143.8                  shell max  94 mean  48.0   ears max 107 mean  11.0   last
tools/showkit/songs/moarghosts/s2.png (1800, 1470)
Sat Oct 31 12:53:17 PDT 2026
```

```
$ cat > "tools/showkit/songs/moarghosts/big.py" <<'EOF'
#!/usr/bin/env python3
"""big.py "<base>" out.png bar bar ...: like sheet.py but bigger tiles. Run from the repo root."""
import json, os, sys
sys.path.insert(0, os.getcwd())
import numpy as np, mau5show, mau5preview as PV
from PIL import Image, ImageDraw
base, out = sys.argv[1], sys.argv[2]
bars = [float(x) for x in sys.argv[3:]]
show = json.load(open(os.path.join("shows", base + ".json")))
music = mau5show._music_for(show, os.path.join("shows", base + ".mp3"))
g = show["scenes"]["grid"]; spb = g["spb"]; t0 = g["t0"]
pl = mau5show.Player(show, music=mu ... [cut]
tools/showkit/songs/moarghosts/b1.png (1920, 780)
deadmau5 - Moar Ghosts n Stuff: 6750 frames at 25 fps through the guard
  scene            from  mean mA   p95 mA     heat   allow W      ms
  dark             0.0s        0        0     0.0%      18.1    0.01
  attract          0.1s      401      853     0.3%      18.1    0.32
  drain            6.6s      128      201     0.3%      18.1    0.09
  afterdark        7.6s      311      386     0.4%      18.1    0.21
  voice           26.3s      702      799     2.2%      18.1    0.29
  banner          37.6s      413      551     2.7%      18.1    0.32
  game            48.8s      395      874     3.3%      18.1    0.32
  gameback        63.8s      393      848     3.7%      18.1    0.32
  pellet          75.1s      479      996     4.0%      18.1    0.16
  fright          78.8s      448      985     4.9%      18.1    0.22
  fright b        93.8s      406      914     5.4%      18.1    0.21
  warning        105.1s      401      906     5.6%      18.1    0.28
  recover        108.8s      392      867     6.1%      18.1    0.35
  intermission   123.8s      410      978     6.8%      18.1    0.23
  stop           138.8s      479     1000     7.1%      18.1    0.15
  bigfright      142.6s      447      971     8.0%      18.1    0.29
  bigflick       157.6s      407      915     8.7%      18.1    0.36
  eaten          172.6s       53       85     8.7%      18.1    0.05
  lone           176.3s      375     1000     8.8%      18.1    0.29
  lone2          183.8s      248      295     8.5%      18.1    0.21
  lone3          191.3s      306      341     8.4%      18.1    0.19
  lone4          198.8s      368      410     8.6%      18.1    0.20
  sw
... [cut] ...
.32
  clyde          236.3s      401      903    10.5%      18.1    0.32
  stop3          240.1s      502     1000    10.8%      18.1    0.16
  final          243.8s      487      988    11.9%      18.1    0.24
  final2         258.8s      391      811    12.3%      18.1    0.32
  last           268.2s      382      518    12.3%      18.1    0.20
  worst frame 1.65 ms; no scene reaches the sustained floor
python3 mau5scene.py check "deadmau5 - Moar Ghosts n Stuff" 2>&1  2.38s user 0.05s system 99% cpu 2.434 total
tail -50  0.00s user 0.00s system 0% cpu 2.434 total
Sat Oct 31 12:54:47 PDT 2026
```

```
$ cd "tools/showkit/songs/moarghosts/"; python3 - <<'EOF'
import re
s = open("sprites.py").read()
# whites: one white block and a dark pupil on the side it looks
a = s.index("# what fills the sockets")
b = s.index("# the giant frightened face")
s = s[:a] + '''# what fills the sockets: the white of the eye, with the pupil left dark on the side it looks
def whites(top, low):
    e = "................."
    return [e, e, e, top, low, low] + [e] * 11
add("Gw_R", whites("......XXXX..XXXX.", "......XX....XX..."))
add("Gw_L", whites(".XXXX..XXXX......", "...XX....XX......"))
add("Gw_F", whites("...XXXX...XXXX...",  ... [cut]
49 sprites
tools/showkit/songs/moarghosts/t1.png (360, 338)
tools/showkit/songs/moarghosts/t2.png (1080, 338)
tools/showkit/songs/moarghosts/t3.png (1800, 338)
Sat Oct 31 12:56:47 PDT 2026
```

```
$ cat > "tools/showkit/songs/moarghosts/gen.py" <<'EOF'
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
ROW = dict(y_lo=48, ... [cut]
wrote shows/scenes/deadmau5 - Moar Ghosts n Stuff.scene.json scenes 33 hits 30
  end        bar 144
     143   268.18s  energy 0.62  bass 0.68 (punch 1.00)  mid 0.63  high 0.63
deadmau5 - Moar Ghosts n Stuff: 34 scenes, 30 hits, written into shows/deadmau5 - Moar Ghosts n Stuff.json
tools/showkit/songs/moarghosts/b1.png (1920, 780)
  trap           258.8s      491      982    28.1%      18.1    0.39
  die            268.2s      738     1000    28.4%      18.1    0.22
  worst frame 2.17 ms; no scene reaches the sustained floor
Sat Oct 31 12:58:33 PDT 2026
```

```
$ cd "tools/showkit/songs/moarghosts/"; python3 - <<'EOF'
s = open("sprites.py").read()
if 'rowface' not in s:
    s = s.replace('# Pac-Man himself, 8 x 8: open, half, shut, facing right and left', '''# just the face of each, to be drawn over the row in another colour
def faces(mouth):
    r = ["........", "........", "..X..X..", "........", mouth, "........", "........", "........"]
    return ["." .join([x] * 4) for x in r]
add("rowface_a", faces(".X.X.X.."))
add("rowface_b", faces("..X.X.X."))
# Pac-Man himself, 8 x 8: open, half, shut, facing right and left''')
open("sprites.py","w").write(s)
g = open("g ... [cut]
51 sprites
wrote shows/scenes/deadmau5 - Moar Ghosts n Stuff.scene.json scenes 33 hits 30
deadmau5 - Moar Ghosts n Stuff: 34 scenes, 30 hits, written into shows/deadmau5 - Moar Ghosts n Stuff.json
head: illegal line count -- 0
Sat Oct 31 12:59:35 PDT 2026
```

```
$ cd "~/deadmau5 app"; KIT=tools/showkit; W=$KIT/work/moarghosts; python3 $KIT/sheet.py "deadmau5 - Moar Ghosts n Stuff" $W/s2.png 66.05:cut 67 68.27 70 71.5 72.6 74.5:stop 75.5 75.8 76:drop2 76.27 78.3 80.6 84.1 88.1 90.6 91.9 92.1:eaten 93 94:boo 94.27 95 96 97 100 104 108 111.5 112.5 113.5 113.8 114:drop3 114.27 116.6 118.05 119 122.27 124.6 126.27 128.5 129.5 129.8 130:final 130.27 132.6 135.27 137.6 138.1 139.5 141 142 142.9 143.05:die 143.3 143.55 143.8 143.95 > $W/s2.txt 2>&1; tail -1 $W/s2.txt;date
tools/showkit/songs/moarghosts/s2.png (1800, 2450)
Sat Oct 31 12:59:55 PDT 2026
```

```
$ cd "~/deadmau5 app"; KIT=tools/showkit; W=$KIT/work/moarghosts; cut -c1-110 $W/s2.txt | sed -n 1,20p; python3 $KIT/spectro.py "deadmau5 - Moar Ghosts n Stuff" $W/z118.png 114 122; python3 $W/big.py "deadmau5 - Moar Ghosts n Stuff" $W/b2.png 78.3 78.55 116.6 118.8; grep -n "sprite" remote/offline/*.js | head -20; date
bar 66.05   cut            shell max 212 mean   7.8   ears max 171 mean  17.4   intermission
bar 67                     shell max 230 mean  32.8   ears max 204 mean  20.8   intermission
bar 68.27                  shell max 230 mean  50.9   ears max 204 mean  56.7   intermission
bar 70                     shell max 230 mean  55.3   ears max 204 mean  20.8   intermission
bar 71.5                   shell max 230 mean  36.7   ears max 204 mean  20.8   intermission
bar 72.6                   shell max 213 mean  26.6   ears max  69 mean   7.0   intermission
bar 74.5    stop           shell max 128 mean  16.8   ears max 127 mean   9.1   stop
bar 75.5                   shell max 179 mean  26.7   ears max 127 mean  45.2   stop
bar 75.8                   shell max   0 mean   0.0   ears max 204 mean  23.5   stop · NOISE 75.75
bar 76      drop2          shell max 195 mean  66.4   ears max 255 mean 149.0   bigfright · POWER 2 · HUNT 7
bar 76.27                  shell max 255 mean 128.6   ears max 255 mean 139.7   bigfright · POWER 2 · HUNT 7
bar 78.3                   shell max 191 mean  66.1   ears max 255 mean  62.0   bigfright · HUNT 76
bar 80.6                   shell max 191 mean  66.1   ears max 208 mean  26.8   bigfright · HUNT 76
bar 84.1                   shell max 244 mean 108.5   ears max 208 mean  26.8   bigflick · HUNT 76
bar 88.1                   shell max 234 mean 100.4   ears max 208 mean  26.8   bigflick2 · HUNT 76
bar 90.6                   shell max 203 mean  75.8   ears max 208 mean  26.8   bigflick3 · HUNT 76
bar 91.9                   shell max 191 mean  66.1   ears max 191 mean  18.0   bigflick3 · HUNT 76
bar 92.1    eaten          shell max 208 mean   6.3   ears max   0 mean   0.0   eaten
bar 93                     shell max 128 mean   3.8   ears max   0 mea
... [cut] ...
:168:function spriteBitmap(fonts, name) {
remote/offline/engine.js:169:  const rows = fonts.sprites[name];
remote/offline/engine.js:458:def('sprite', { sprite: 'smile', color: [0, 255, 255], bg: [0, 0, 0],
remote/offline/engine.js:463:    const names = String(this.p.sprite).split('|');
remote/offline/engine.js:465:    const bm = spriteBitmap(this.fonts, names[at]);
remote/offline/engine.js:968:              textBitmap, glyphBitmap, digitBitmap, spriteBitmap, fract, pmod,
remote/offline/ui.js:413:// use -- a sprite this build does not have, an axis it does not know,
Sat Oct 31 13:00:50 PDT 2026
```

```
$ cd "~/deadmau5 app"; sed -n 160,180p remote/offline/engine.js; sed -n 455,490p remote/offline/engine.js; grep -n "sprites" remote/offline/*.js mau5offline.py | head -20; sed -n 405,440p remote/offline/ui.js
  const rows = fonts.digit3x5[ch] || fonts.digit3x5['0'];
  const bm = { rows: rows.length, cols: rows[0].length,
               d: new Uint8Array(rows.length * rows[0].length) };
  for (let r = 0; r < bm.rows; r++)
    for (let c = 0; c < bm.cols; c++) bm.d[r * bm.cols + c] = rows[r][c] !== ' ' ? 1 : 0;
  return bm;
}

function spriteBitmap(fonts, name) {
  const rows = fonts.sprites[name];
  const bm = { rows: rows.length, cols: rows[0].length,
               d: new Uint8Array(rows.length * rows[0].length) };
  for (let r = 0; r < bm.rows; r++)
    for (let c = 0; c < bm.cols; c++) bm.d[r * bm.cols + c] = rows[r][c] !== '.' ? 1 : 0;
  return bm;
}

// Draw a bitmap onto the LEDs, by gather and by scatter.  The comment
// in mau5engine.paint explains why both halves are needed; this is the
// same algorithm, including the order the scatter resolves ties in --
// argmin takes the first minimum, so the loop below uses a strict <.
  });

// mau5engine.SpriteShow says what dx, dy, vx, vy, wx, wy, wf and rate do.
def('sprite', { sprite: 'smile', color: [0, 255, 255], bg: [0, 0, 0],
                y_lo: 20.0, y_hi: 160.0, x_half: 150.0, blink: 0.0,
                dx: 0.0, dy: 0.0, vx: 0.0, vy: 0.0,
                wx: 0.0, wy: 0.0, wf: 0.0, rate: 0.0 },
  function (h, t, music, out) {
    const names = String(this.p.sprite).split('|');
    const at = this.p.rate > 0 ? pmod(Math.floor(t * this.p.rate), names.length) : 0;
    const bm = spriteBitmap(this.fonts, names[at]);
    fill(out, h.n, this.p.bg);
    if (this.p.blink && fract(t * this.p.blink) > 0.5) return;
    const hi = this.p.y_hi, lo = this.p.y_lo, xh = this.p.x_half;
    let ox = this.p.dx + this.p.vx * t, oy = this.p.dy + this.p.vy * t;
    if (this.p.wf) {
      ox = ox + this.p.wx * Math.sin(2 * Math.PI * thi
... [cut] ...
s);
  test.render(helmet, 0, state.music, scratch);
  return M.make(name, params, helmet, D.fonts);
}

function set(k, v) {
  const was = state.params;
  state.params = Object.assign({}, was, { [k]: v });
  try {
    state.inst = tryMake(state.preset, state.params);
  } catch (e) {
    state.params = was;
    pageWarn(state.preset + ' cannot use ' + k.replace(/_/g, ' ') + ' "' + v + '" ('
             + ((e && e.message) || e) + ')');
    return;
  }
  save();
}

function choose(name, keepParams) {
  state.preset = name;
  state.params = keepParams ? ownParams(name, state.params) : {};
  try {
```

```
$ cd "~/deadmau5 app"; sed -n 160,180p remote/offline/engine.js; sed -n 455,490p remote/offline/engine.js; grep -n "sprites" remote/offline/*.js mau5offline.py | head -20; sed -n 405,440p remote/offline/ui.js
  const rows = fonts.digit3x5[ch] || fonts.digit3x5['0'];
  const bm = { rows: rows.length, cols: rows[0].length,
               d: new Uint8Array(rows.length * rows[0].length) };
  for (let r = 0; r < bm.rows; r++)
    for (let c = 0; c < bm.cols; c++) bm.d[r * bm.cols + c] = rows[r][c] !== ' ' ? 1 : 0;
  return bm;
}

function spriteBitmap(fonts, name) {
  const rows = fonts.sprites[name];
  const bm = { rows: rows.length, cols: rows[0].length,
               d: new Uint8Array(rows.length * rows[0].length) };
  for (let r = 0; r < bm.rows; r++)
    for (let c = 0; c < bm.cols; c++) bm.d[r * bm.cols + c] = rows[r][c] !== '.' ? 1 : 0;
  return bm;
}

// Draw a bitmap onto the LEDs, by gather and by scatter.  The comment
// in mau5engine.paint explains why both halves are needed; this is the
// same algorithm, including the order the scatter resolves ties in --
// argmin takes the first minimum, so the loop below uses a strict <.
  });

// mau5engine.SpriteShow says what dx, dy, vx, vy, wx, wy, wf and rate do.
def('sprite', { sprite: 'smile', color: [0, 255, 255], bg: [0, 0, 0],
                y_lo: 20.0, y_hi: 160.0, x_half: 150.0, blink: 0.0,
                dx: 0.0, dy: 0.0, vx: 0.0, vy: 0.0,
                wx: 0.0, wy: 0.0, wf: 0.0, rate: 0.0 },
  function (h, t, music, out) {
    const names = String(this.p.sprite).split('|');
    const at = this.p.rate > 0 ? pmod(Math.floor(t * this.p.rate), names.length) : 0;
    const bm = spriteBitmap(this.fonts, names[at]);
    fill(out, h.n, this.p.bg);
    if (this.p.blink && fract(t * this.p.blink) > 0.5) return;
    const hi = this.p.y_hi, lo = this.p.y_lo, xh = this.p.x_half;
    let ox = this.p.dx + this.p.vx * t, oy = this.p.dy + this.p.vy * t;
    if (this.p.wf) {
      ox = ox + this.p.wx * Math.sin(2 * Math.PI * thi
... [cut] ...
s);
  test.render(helmet, 0, state.music, scratch);
  return M.make(name, params, helmet, D.fonts);
}

function set(k, v) {
  const was = state.params;
  state.params = Object.assign({}, was, { [k]: v });
  try {
    state.inst = tryMake(state.preset, state.params);
  } catch (e) {
    state.params = was;
    pageWarn(state.preset + ' cannot use ' + k.replace(/_/g, ' ') + ' "' + v + '" ('
             + ((e && e.message) || e) + ')');
    return;
  }
  save();
}

function choose(name, keepParams) {
  state.preset = name;
  state.params = keepParams ? ownParams(name, state.params) : {};
  try {
```

```
$ cd "~/deadmau5 app"; KIT=tools/showkit; W=$KIT/work/moarghosts; python3 $KIT/spectro.py "deadmau5 - Moar Ghosts n Stuff" $W/z122.png 122 128; python3 $KIT/spectro.py "deadmau5 - Moar Ghosts n Stuff" $W/z134.png 130 140; date
tools/showkit/songs/moarghosts/z122.png
tools/showkit/songs/moarghosts/z134.png
Sat Oct 31 13:01:18 PDT 2026
```

```
$ cd "tools/showkit/songs/moarghosts/"; python3 - <<'EOF'
s = open("sprites.py").read()
# eyes of the giant, one column in from the shoulder
s = s.replace('SOCK_R = sockets("XXXXXX....XX....X")', 'SOCK_R = sockets("XXXXX....XX....XX")')
s = s.replace('SOCK_L = sockets("X....XX....XXXXXX")', 'SOCK_L = sockets("XX....XX....XXXXX")')
s = s.replace('add("Gw_R", whites("......XXXX..XXXX.", "......XX....XX..."))', 'add("Gw_R", whites(".....XXXX..XXXX..", ".....XX....XX...."))')
s = s.replace('add("Gw_L", whites(".XXXX..XXXX......", "...XX....XX......"))', 'add("Gw_L", whites("..XXXX..XXXX.....", "....XX....XX..... ... [cut]
51 sprites
Traceback (most recent call last):
  File "tools/showkit/songs/moarghosts/gen.py", line 201, in <module>
    H(noise_hit(13.75))
NameError: name 'noise_hit' is not defined
  banner          37.6s      444      605     4.1%      18.1    0.31
  game            48.8s      595      993     5.9%      18.1    0.34
  gameback        63.8s      596      996     7.3%      18.1    0.34
  pellet          75.1s      509     1000     7.6%      18.1    0.15
  fright          78.8s      621      988     9.5%      18.1    0.32
  fright b        93.8s      575      973    10.8%      18.1    0.31
  warning        105.1s      577      961    11.2%      18.1    0.34
  recover        108.8s      558      993    12.8%      18.1    0.36
  intermission   123.8s      415      991    13.5%      18.1    0.28
  stop           138.8s      623     1000    14.0%      18.1    0.19
  bigfright      142.6s      677     1000    16.3%      18.1    0.32
  bigflick       157.6s      645     1000    17.3%      18.1    0.36
  bigflick2      165.1s      642     1000    17.8%      18.1    0.43
  bigflick3      168.8s      646      999    18.4%      18.1    0.43
  eaten          172.6s       51       85    18.4%      18.1    0.05
  lone           176.3s      428     1000    18.5%      18.1    0.31
  lone2          183.8s      379      501    18.6%      18.1    0.22
  lone3          191.3s      554      634    19.4%      18.1    0.21
  lone4          198.8s      692      736    20.6%      18.1    0.21
  swell          206.3s      794      857    21.3%      18.1    0.21
  pellet3        210.1s      639     1000    21.9%      18.1    0.20
  blinky         213.8s      638      998    22.9%      18.1    0.35
  pinky          221.3s      588     1000    23.8%      18.1    0.34
  inky           228.8s      588     1000    24.6%      18.1    0.35
  clyde          236.3s      611     1000    25.1%      18.1    0.36
  stop3          240.1s      633     1000    25.6%      18.1    0.20
  final          243.8s      621      991    27.6%      18.1    0.38
  trap           258.8s      541      982    28.5%      18.1    0.37
  die            268.2s      738     1000    28.8%      18.1    0.21
  worst frame 0.68 ms; no scene reaches the sustained floor
Sat Oct 31 13:02:31 PDT 2026
```

```
$ cd "tools/showkit/songs/moarghosts/"; python3 - <<'EOF'
g = open("gen.py").read()
g = g.replace('H(noise_hit(13.75))\n# -----', '# -----', 1)
g = g.replace('H(noise_hit(41.75))', 'H(noise_hit(13.75))\nH(noise_hit(41.75))', 1)
open("gen.py","w").write(g)
EOF
cd "~/deadmau5 app"; KIT=tools/showkit; W=$KIT/work/moarghosts; python3 $W/gen.py && python3 mau5scene.py compile "deadmau5 - Moar Ghosts n Stuff" 2>&1 | tail -1 && python3 $W/big.py "deadmau5 - Moar Ghosts n Stuff" $W/b3.png 78.05 78.3 78.55 78.8 116.6 11 ... [cut]
wrote shows/scenes/deadmau5 - Moar Ghosts n Stuff.scene.json scenes 39 hits 37
deadmau5 - Moar Ghosts n Stuff: 40 scenes, 37 hits, written into shows/deadmau5 - Moar Ghosts n Stuff.json
tools/showkit/songs/moarghosts/b3.png (1920, 1170)
  pinky stare    225.1s      814     1000    23.6%      18.1    0.28
  inky           228.8s      603     1000    24.1%      18.1    0.36
  inky stare     232.6s      808     1000    24.8%      18.1    0.28
  clyde          236.3s      611     1000    25.3%      18.1    0.37
  stop3          240.1s      622     1000    25.8%      18.1    0.20
  final          243.8s      679     1000    26.4%      18.1    0.40
  final chord    247.6s      756      993    27.0%      18.1    0.41
  final b        251.3s      648      978    27.6%      18.1    0.40
  final chord    255.1s      756     1000    28.3%      18.1    0.40
  trap           258.8s      634      997    29.5%      18.1    0.35
  die            268.2s      738     1000    29.9%      18.1    0.20
  worst frame 0.65 ms; no scene reaches the sustained floor
Sat Oct 31 13:02:42 PDT 2026
```

```
$ cd "tools/showkit/songs/moarghosts/"; python3 - <<'EOF'
s = open("sprites.py").read()
s = s.replace('''             "XX.............XX",
             "XXXXX..X.X..XXXXX",
             "..XXXXXX.XXXXXX.."])''', '''             "X...............X",
             "X...............X",
             "................."])''')
open("sprites.py","w").write(s)

g = open("gen.py").read()
# jaw dots
g = g.replace('CHEW = {"pat": "x.", "step": 0.5, "decay": 0.4, "floor": 0.45}', '''def jawdots(gain, speed=0.25, frm=1.05, to=-0.05, shape="saw"):
    "A row of dots along the chin, eaten across it."
    return {"fx": "swee ... [cut]
51 sprites
wrote shows/scenes/deadmau5 - Moar Ghosts n Stuff.scene.json scenes 39 hits 43
deadmau5 - Moar Ghosts n Stuff: 40 scenes, 43 hits, written into shows/deadmau5 - Moar Ghosts n Stuff.json
tools/showkit/songs/moarghosts/b4.png (1920, 780)
  die            268.2s      738     1000    29.8%      18.1    0.21
  worst frame 3.19 ms; no scene reaches the sustained floor
Sat Oct 31 13:04:22 PDT 2026
```

```
$ cd "tools/showkit/songs/moarghosts/"; python3 - <<'EOF'
g = open("gen.py").read()
a = g.index('tr["about"] = (')
b = g.index('save(tr, "shows/scenes/%s.scene.json" % BASE)')
g = g[:a] + '''tr["about"] = ("Bars of a measured grid, shows/scenes/deadmau5 - Moar Ghosts n Stuff.beats: bar b starts at 0.045 + 1.875 b seconds (127.995 BPM), 144 bars, "
    "flat to a millisecond wherever there are drums, with the kick on every beat, the clap on 2 and 4, the riff on x.....x.x.x...x. and every section turning on the bar line; the noise burst before each drop sits on the last beat of the bar before it, and the file  ... [cut]
wrote shows/scenes/deadmau5 - Moar Ghosts n Stuff.scene.json scenes 39 hits 43
deadmau5 - Moar Ghosts n Stuff: 40 scenes, 43 hits, written into shows/deadmau5 - Moar Ghosts n Stuff.json
deadmau5 - Moar Ghosts n Stuff: 127.995 BPM, 144 bars, bar 0 at 0.045 s, holds []
music against the grid per 8 bars, ms (contrast): 0:-3(2.21)  8:+41(1.11)  16:+15(1.29)  24:-1(9.00)  32:-1(10.28)  40:-1(6.77)  48:-1(7.20)  56:+1(6.44)  64:+1(6.72)  72:+1(5.79)  80:+1(6.78)  88:+1(5.34)  96:+1(2.18)  104:+1(1.36)  112:-1(5.52)  120:-1(5.67)  128:-1(5.34)  136:-1(5.52)
worst 15 ms where the music is clear enough to say, mean +1.1 ms
deadmau5 - Moar Ghosts n Stuff: 6750 frames at 25 fps through the guard
  scene            from  mean mA   p95 mA     heat   allow W      ms
  dark             0.0s        0        0     0.0%      18.1    0.01
  attract          0.1s      606      999     0.8%      18.1    0.37
  drain            6.6s      107      169     0.8%      18.1    0.08
  afterdark        7.6s      407      505     1.6%      18.1    0.20
  voice           26.3s      714      940     3.5%      18.1    0.29
  banner          37.6s      454      624     4.2%      18.1    0.32
  game            48.8s      595      993     6.0%      18.1    0.36
  gameback        63.8s      596      996     7.3%      18.1    0.36
  pellet          75.1s      498     1000     7.6%      18.1    0.15
  fright          78.8s      623      988     9.6%      18.1    0.34
  fright b        93.8s      575      973    10.9%      18.1    0.32
  warning        105.1s      577      961    11.3%      18.1    0.36
  recover        108.8s      557      993    12.8%      18.1    0.39
  intermission   123.8s      424      991    13.6%      18.1    0.27
  stop           138.8s      599     1000    14.1%      18.1    0.19
  
... [cut] ...
0    25.2%      18.1    0.36
  stop3          240.1s      611     1000    25.7%      18.1    0.19
  final          243.8s      679     1000    26.3%      18.1    0.43
  final chord    247.6s      756      993    27.0%      18.1    0.42
  final b        251.3s      648      978    27.5%      18.1    0.39
  final chord    255.1s      756     1000    28.2%      18.1    0.41
  trap           258.8s      634      997    29.5%      18.1    0.37
  die            268.2s      738     1000    29.8%      18.1    0.21
  worst frame 2.19 ms; no scene reaches the sustained floor
Sat Oct 31 13:05:05 PDT 2026
```

```
$ cd "tools/showkit/songs/moarghosts/"; python3 - <<'EOF'
s = open("sprites.py").read()
if '"trainR"' not in s:
    s = s.replace('# --- frightened small ghost:', '''# white eyes for the holes: one ghost, or four in a train, all in one sprite
add("ewR", small_eyes("...X..X."))
add("ewL", small_eyes(".X..X..."))
add("trainR", ["." .join([r] * 4) for r in small_eyes("...X..X.")])
add("trainL", ["." .join([r] * 4) for r in small_eyes(".X..X...")])
# --- frightened small ghost:''')
open("sprites.py","w").write(s)

g = open("gen.py").read()
g = g.replace('GAP = 140.0                       # a ghost and the next,  ... [cut]
55 sprites
wrote shows/scenes/deadmau5 - Moar Ghosts n Stuff.scene.json scenes 39 hits 43
deadmau5 - Moar Ghosts n Stuff: 40 scenes, 43 hits, written into shows/deadmau5 - Moar Ghosts n Stuff.json
tools/showkit/songs/moarghosts/b5.png (1920, 780)
  die            268.2s      738     1000    30.0%      18.1    0.21
  worst frame 1.04 ms; no scene reaches the sustained floor
Sat Oct 31 13:06:24 PDT 2026
```

I'll read the correction and the new tools first.

```
$ KIT=tools/showkit; date; tail -30 "$KIT/BRIEF.md"; echo ------; cat "$KIT/sheet.py"; echo ------; cat "$KIT/power.py"; echo -----; cat "$KIT/scenepower.py"
Sat Oct 31 13:07:34 PDT 2026
4. Write the treatment with a small Python generator in your scratch folder (see Tiki's), using `from fmt import save` with `sys.path.insert(0, KIT)`, then `python3 mau5scene.py compile "<base>"` and fix what it refuses. Put a real `about` string in it describing the concept, the same style as Tiki's.
5. Look at it. `python3 $KIT/sheet.py "<base>" out.png 40:drop 40.25 41 ...` renders tiles as the helmet will really look after the power guard, and prints how bright shell and ears end up. READ THE PNG. Does it read as your idea? Is the shell visible next to the ears? Check every major section, each hit, and both a kick and the gap after it. Iterate.
6. `python3 mau5scene.py check "<base>"`: every scene through the power guard. Heat under about 40%, and no scene "at the sustained floor". `python3 $KIT/grid.py check "<base>"` again at the end.

## The treatment format
Bars, not seconds: bar b is `t0 + 4 b spb` on your grid. Top level: `v:1, show, about, lead:0, marks{name:bar or "other+2"}, palettes{name:[[r,g,b],...] or {"stops":[...],"wrap":true}}, motifs{name: layer or [layers]}, scenes[], hits[]`. A value may be a number, `[from,to]` (a ramp over the scene), `{"<bar or mark>":v,...}` (steps at bars), or `{"band":"bass|mid|high","lo":a,"hi":b,"punch":true|false}` (driven by the track, resolved live; the phone has these curves). Scenes tile the song, from bar -1 (a gap is dark): `{"name","from","to","pal","pump":{"pat":"x...","step":0.25,"depth":0.2,"decay":0.5},"out":beats of darkness before the next scene (max 4),"layers":[...]}`; `like:"earlier scene"` copies one and `patch:{"layerIndex":{...}}`, `add:[...]` or `each:{...}` change it (patch indexes the authored layers before motif expansion). Hits are moments over a scene: `{"name","at":ba
... [cut] ...
d after the knee: from the mean
    per[nm].append((rep["sent_ma"],rep["governor_hit"],"shell" in rep["regions_hit"],res[sh].mean(),res[ea].mean(),rep["thermal"]["full_pct"] if rep.get("thermal") else 0,res[sh].max()))
print("%-14s %6s %6s %6s %6s %7s %7s %6s %6s"%("scene","mean","p95","gov%","reg%","shellm","earsm","smax","heat"))
for nm in order:
    a=np.array(per[nm],float)
    print("%-14s %6.0f %6.0f %6.0f %6.0f %7.1f %7.1f %6.0f %5.1f%%"%(nm[:14],a[:,0].mean(),np.percentile(a[:,0],95),a[:,1].mean()*100,a[:,2].mean()*100,a[:,3].mean(),a[:,4].mean(),np.percentile(a[:,6],90),a[:,5].max()))
```

```
$ cd "~/deadmau5 app"; KIT=tools/showkit; W=$KIT/work/moarghosts; python3 $KIT/sheet.py "deadmau5 - Moar Ghosts n Stuff" $W/final.png 0.06:flash 1.3:attract 2.6:gap 3.8:drain 7:Clyde 8.5:moon 11 14.1:voice 16.3:look 18.6:look 21:title 23 25:Pac 26.03:drums 28.3:clap 31:gap 36:back 40.5:pellet 41.5:swell 41.8:noise 42.02:DROP 42.3:blast 44.5:hunt 46.3:right 46.8:left 49.5:run 56.3:warn 58.03:recover 61:chase 64 67:bigPac 70 71.6:bigPac 74.5:stop 75.6:pellet 76.02:DROP2 76.3:blast 78.3:face 78.8:face 84.1:flick 90.6:flick 92.2:eaten 93.5:home 94.02:BOO 94.6:BOO 96:lone 99 103 107:two 111:four 113:p ... [cut]
tools/showkit/songs/moarghosts/final.png (1800, 3185)
bar 0.06    flash      sent  669 mA  shell max  40 mean   9.5  ears max 144 mean  22.9  attract · W
bar 1.3     attract    sent  971 mA  shell max   3 mean   1.2  ears max 181 mean  55.2  attract · W
bar 2.6     gap        sent  457 mA  shell max  28 mean   8.8  ears max 132 mean  11.5  attract · W
bar 3.8     drain      sent   95 mA  shell max  18 mean   3.2  ears max   0 mean   0.0  drain
bar 7       Clyde      sent  490 mA  shell max  36 mean   9.8  ears max 231 mean  11.3  afterdark
bar 8.5     moon       sent  390 mA  shell max  46 mean   9.9  ears max 108 mean   5.3  afterdark
bar 11                 sent  490 mA  shell max  37 mean   9.9  ears max 232 mean  11.3  afterdark
bar 14.1    voice      sent   55 mA  shell max   0 mean   0.0  ears max  76 mean   3.3  voice
bar 16.3    look       sent  377 mA  shell max  29 mean   9.8  ears max  76 mean   4.5  voice
bar 18.6    look       sent  544 mA  shell max  28 mean   9.9  ears max  89 mean  14.5  voice
bar 21      title      sent  334 mA  shell max  38 mean   9.8  ears max 118 mean   2.0  banner · TI
bar 23                 sent  475 mA  shell max  32 mean   9.8  ears max 144 mean  10.4  banner · TI
bar 25      Pac        sent  609 mA  shell max  38 mean   9.9  ears max 145 mean  18.3  banner
bar 26.03   drums      sent  686 mA  shell max  42 mean  10.0  ears max 152 mean  23.0  game · WAKA
bar 28.3    clap       sent  971 mA  shell max   5 mean   1.5  ears max 181 mean  54.8  game · WAKA
bar 31      gap        sent  758 mA  shell max  22 mean   9.7  ears max 156 mean  27.3  game · WAKA
bar 36      back       sent  721 mA  shell max  23 mean   9.8  ears max 152 mean  25.1  gameba
... [cut] ...
IN
bar 142.9   caught     sent  390 mA  shell max  19 mean   8.2  ears max 181 mean   8.4  trap · CHIN
bar 143.1   die        sent 1000 mA  shell max   6 mean   2.9  ears max  94 mean  54.5  die
bar 143.4              sent 1000 mA  shell max  33 mean   8.3  ears max  74 mean  44.8  die
bar 143.7              sent  504 mA  shell max  58 mean   3.8  ears max  38 mean  23.3  die
bar 143.95             sent   76 mA  shell max  58 mean   0.4  ears max   6 mean   3.7  die
(scratch)/ki
Sat Oct 31 13:07:46 PDT 2026
```

```
$ cd "~/deadmau5 app"; KIT=tools/showkit; W=$KIT/work/moarghosts; python3 $KIT/power.py "deadmau5 - Moar Ghosts n Stuff"; python3 $KIT/scenepower.py "deadmau5 - Moar Ghosts n Stuff"; python3 $KIT/sheet.py "deadmau5 - Moar Ghosts n Stuff" $W/g1.png 1.3:train 8:afterdark 16:voice 24:title 29 31 36 41.5:pellet 42:drop 42.27 46.3 56.27 61:chase 67 71.5 76:drop2 78.3 88.1 92.1:eaten 94:BOO 99:lone 107 111 114:drop3 116.6 118.8 130:WHITE 132.6 141:trap 143.05:die 143.55; sed -n 1,60p mau5power.py; date
deadmau5 - Moar Ghosts n Stuff: 270 s, mean 14.4 W (target 11.5 or less), heat at the end 30%
hottest scenes (name, mean W, seconds): bigfright 15.0 15s; fright 15.0 15s; game 14.8 15s; recover 14.1 15s; afterdark 12.4 19s; voice 16.0 11s; intermission 12.8 15s; gameback 14.6 11s
scene            mean    p95   gov%   reg%  shellm   earsm   smax   heat
dark                0      0      0      0     0.0     0.0      0   0.0%
attract           587    999     33     99     7.1    21.9     37   0.8%
drain             107    169      0      0     3.4     0.0     30   0.8%
afterdark         413    517      0     46     7.3    11.2     58   1.6%
voice             714    940      0     91     9.3    25.7     31   3.5%
banner            454    624      0     86     9.6     9.6     55   4.2%
game              597    996     28     98     7.3    22.1     40   6.0%
gameback          587    996     29     96     7.3    21.6     42   7.3%
pellet            498   1000      9      0     3.2    23.7     57   7.6%
fright            623    988     18    100     7.8    22.6     34   9.6%
fright b          575    973      8    100     8.5    18.4     34  10.8%
warning           577    961      4    100     8.6    18.4     30  11.2%
recover           541    990     26     97     7.5    18.4     39  12.7%
intermission      425    991     30     80     6.9    12.7     51  13.5%
stop              599   1000     17     14     6.7    23.4     54  13.9%
bigfright         622    989     19    100     7.6    22.5     22  15.9%
bigflick          576    974      9    100     8.3    18.4     22  16.7%
bigflick2         575    948      4    100     8.4    18.4     21  17.2%
bigflick3         649    983     24    100     7.6    24.1     19  17.7%
eaten              50     85      2      0     1.7     0.0 
... [cut] ...
henever the rail is live

# How fast the governor may give light back, as a factor on its scale
# per second (PowerGuard.apply has the measurements).  Taking light away
# is never slowed: that is what keeps every frame inside the budget.
# GOV_MIN_DT is the step a call counts as when the clock does not move
# -- mau5ctl's preview holds it still on purpose, and the scale must
# still be able to come back -- and GOV_FROM the lowest scale the ramp
# starts from, so a governor driven to zero can climb out at all.
GOV_RISE = 1.0
GOV_MIN_DT = 1.0 / 40.0
GOV_FROM = 0.01


Sat Oct 31 13:08:19 PDT 2026
```

```
$ KIT=tools/showkit; ls -la $KIT; cat $KIT/sheet.py; cd "~/deadmau5 app"; ls -la --time-style=full-iso mau5show.py mau5engine.py mau5scene.py 2>/dev/null || ls -lT mau5show.py mau5engine.py mau5scene.py; git status --short | head -30; git log -3 --format='%h %ad %s' --date=iso
total 184
drwxr-xr-x@  13 jones  wheel    416 Oct 31 13:06 .
drwx------@ 289 jones  wheel   9248 Oct 31 13:07 ..
-rw-r--r--@   1 jones  wheel  11390 Oct 31 13:06 BRIEF.md
-rw-r--r--@   1 jones  wheel    933 Oct 31 12:37 fmt.py
-rw-r--r--@   1 jones  wheel  10884 Oct 31 12:38 grid.py
-rw-r--r--@   1 jones  wheel  38416 Oct 31 12:37 mau5song_new.py
-rw-r--r--@   1 jones  wheel   1751 Oct 31 12:54 power.py
-rw-r--r--@   1 jones  wheel   1484 Oct 31 13:06 scenepower.py
-rw-r--r--@   1 jones  wheel   2587 Oct 31 13:06 sheet.py
-rw-r--r--@   1 jones  wheel   1652 Oct 31 12:37 songmap.py
-rw-r--r--@   1 jones  wheel   2438 Oct 31 12:37 spectro.py
-rw-r--r--@   1 jones  wheel   1173 Oct 31 12:37 spritetry.py
drwxr-xr-x@  23 jones  wheel    736 Oct 31 13:06 work
#!/usr/bin/env python3
"""sheet.py "<base>" out.png bar[:label] bar[:label] ... -- the show at those bars as the helmet will really look: through the real power guard (cold, settled for a second first), then gamma so the picture is what an eye sees. Prints per tile the mA sent and how bright shell and ears really are after the guard. Bars may be fractional: 40.25 is the second beat of bar 40, so catch both a kick and the gap after it. Env: COLS, TW, GAM. Run from the repo root. Credit: the Radio Edit author, who found the first version skipped the guard."""
import json, os, sys
sys.path.insert(0, os.getcwd())
import numpy as np, mau5show, mau5preview as PV, mau5scene as SS, mau5engine as E, mau5power
from PIL import Image, ImageDraw
base, out = sys.argv[1], sys.argv[2]
marks = []
for a in sys.argv[3:]:
    b, _, lab = a.partition(":")
    marks.append((float(b), lab))
show = json.load(open(os.path.join("shows", base + ".json")))
music = mau5show._music_for(show, os.path.join("shows", base + ".mp3"))
g = show["scenes"]["g
... [cut] ...
ysis.npz"
 M "shows/deadmau5 - Ghosts n Stuff (Nero Remix).json"
 M "shows/scenes/beneath (with raxaj).scene.json"
 M "shows/scenes/deadmau5 - Ghosts n Stuff (Nero Remix).scene.json"
 M test_mau5.py
 M tests_more/page.py
 M tests_more/scenes.py
?? firmware/
?? "shows/Kaskade feat. deadmau5 - I Remember.analysis.npz"
4ad9ef2 2026-10-30 07:28:02 -0700 The report: the helmet is on WLED 16.0.1, and what it measured
ce360b5 2026-10-30 07:28:02 -0700 On WLED 16 the filler is binary, so nothing takes the JSON lock
14ba328 2026-10-30 07:12:48 -0700 Binary frames when the controller is WLED 16 or later
```

```
$ KIT=tools/showkit; ls -la $KIT; cat $KIT/sheet.py; cd "~/deadmau5 app"; ls -la --time-style=full-iso mau5show.py mau5engine.py mau5scene.py 2>/dev/null || ls -lT mau5show.py mau5engine.py mau5scene.py; git status --short | head -30; git log -3 --format='%h %ad %s' --date=iso
total 184
drwxr-xr-x@  13 jones  wheel    416 Oct 31 13:06 .
drwx------@ 289 jones  wheel   9248 Oct 31 13:07 ..
-rw-r--r--@   1 jones  wheel  11390 Oct 31 13:06 BRIEF.md
-rw-r--r--@   1 jones  wheel    933 Oct 31 12:37 fmt.py
-rw-r--r--@   1 jones  wheel  10884 Oct 31 12:38 grid.py
-rw-r--r--@   1 jones  wheel  38416 Oct 31 12:37 mau5song_new.py
-rw-r--r--@   1 jones  wheel   1751 Oct 31 12:54 power.py
-rw-r--r--@   1 jones  wheel   1484 Oct 31 13:06 scenepower.py
-rw-r--r--@   1 jones  wheel   2587 Oct 31 13:06 sheet.py
-rw-r--r--@   1 jones  wheel   1652 Oct 31 12:37 songmap.py
-rw-r--r--@   1 jones  wheel   2438 Oct 31 12:37 spectro.py
-rw-r--r--@   1 jones  wheel   1173 Oct 31 12:37 spritetry.py
drwxr-xr-x@  23 jones  wheel    736 Oct 31 13:06 work
#!/usr/bin/env python3
"""sheet.py "<base>" out.png bar[:label] bar[:label] ... -- the show at those bars as the helmet will really look: through the real power guard (cold, settled for a second first), then gamma so the picture is what an eye sees. Prints per tile the mA sent and how bright shell and ears really are after the guard. Bars may be fractional: 40.25 is the second beat of bar 40, so catch both a kick and the gap after it. Env: COLS, TW, GAM. Run from the repo root. Credit: the Radio Edit author, who found the first version skipped the guard."""
import json, os, sys
sys.path.insert(0, os.getcwd())
import numpy as np, mau5show, mau5preview as PV, mau5scene as SS, mau5engine as E, mau5power
from PIL import Image, ImageDraw
base, out = sys.argv[1], sys.argv[2]
marks = []
for a in sys.argv[3:]:
    b, _, lab = a.partition(":")
    marks.append((float(b), lab))
show = json.load(open(os.path.join("shows", base + ".json")))
music = mau5show._music_for(show, os.path.join("shows", base + ".mp3"))
g = show["scenes"]["g
... [cut] ...
ysis.npz"
 M "shows/deadmau5 - Ghosts n Stuff (Nero Remix).json"
 M "shows/scenes/beneath (with raxaj).scene.json"
 M "shows/scenes/deadmau5 - Ghosts n Stuff (Nero Remix).scene.json"
 M test_mau5.py
 M tests_more/page.py
 M tests_more/scenes.py
?? firmware/
?? "shows/Kaskade feat. deadmau5 - I Remember.analysis.npz"
4ad9ef2 2026-10-30 07:28:02 -0700 The report: the helmet is on WLED 16.0.1, and what it measured
ce360b5 2026-10-30 07:28:02 -0700 On WLED 16 the filler is binary, so nothing takes the JSON lock
14ba328 2026-10-30 07:12:48 -0700 Binary frames when the controller is WLED 16 or later
```

```
$ cd "~/deadmau5 app"; sed -n 60,420p mau5power.py; cat data/cal/power.json
class Region:
    """A span of the chain with its own thermal allowance.

    Two numbers, because they answer different questions.  ``ceiling``
    is per LED: how hard may any single pixel here ever be driven.
    ``budget_ma`` is for the span as a whole: how much current may all
    of them draw at once.  Sparse content stays bright because it never
    reaches the budget; a region asked to go solid white dims itself
    instead of browning out the rest of the helmet.
    """

    def __init__(self, name, lo, hi, ceiling, budget_ma, shed=1.0, floor=0.0):
        self.name, self.lo, self.hi = name, int(lo), int(hi)
        self.ceiling = int(ceiling)        # 0-255, per channel, per LED
        self.budget_ma = float(budget_ma)  # for the whole span
        # The dimmest this region is allowed to be driven while it is
        # being asked for anything at all.  Weighted shedding is right
        # about priority and wrong about the endpoint: a shell with
        # shed 6 is at nothing long before the tubes have given up, so
        # a helmet left running settles into two glowing stripes and
        # stops reading as a helmet.  The floor costs a few milliamps
        # and keeps the shape.  It never lights an LED the preset
        # wanted dark, and it yields entirely if it will not fit.
        self.floor = float(floor)          # 0-255, per LED
        self.shed = float(shed)            # relative give under global pressure

    @property
    def n(self):
        return self.hi - self.lo + 1

    def full_white_ma(self):
        return self.n * MA_PER_LED_FULL_WHITE * self.ceiling / 255.0

    def __repr__(self):
        return ("Region(%s %d..%d ceiling=%d budget=%.0fmA shed=%.1f)"
                % (self.name, self.lo, self.hi, self.ceiling,
                   s
... [cut] ...
_ma": 300,
   "shed": 6.0,
   "floor": 3.0
  },
  {
   "name": "ear1_tubes",
   "lo": 398,
   "hi": 491,
   "ceiling": 255,
   "budget_ma": 620,
   "shed": 1.0,
   "floor": 6.0
  },
  {
   "name": "ear1_rim",
   "lo": 492,
   "hi": 509,
   "ceiling": 160,
   "budget_ma": 200,
   "shed": 3.0,
   "floor": 5.0
  },
  {
   "name": "ear2_rim",
   "lo": 510,
   "hi": 528,
   "ceiling": 160,
   "budget_ma": 190,
   "shed": 3.0,
   "floor": 5.0
  },
  {
   "name": "ear2_tubes",
   "lo": 529,
   "hi": 620,
   "ceiling": 255,
   "budget_ma": 640,
   "shed": 1.0,
   "floor": 6.0
  }
 ],
 "link_ma": 0.0
}
```

```
$ cd "~/deadmau5 app"; sed -n 60,420p mau5power.py; cat data/cal/power.json
class Region:
    """A span of the chain with its own thermal allowance.

    Two numbers, because they answer different questions.  ``ceiling``
    is per LED: how hard may any single pixel here ever be driven.
    ``budget_ma`` is for the span as a whole: how much current may all
    of them draw at once.  Sparse content stays bright because it never
    reaches the budget; a region asked to go solid white dims itself
    instead of browning out the rest of the helmet.
    """

    def __init__(self, name, lo, hi, ceiling, budget_ma, shed=1.0, floor=0.0):
        self.name, self.lo, self.hi = name, int(lo), int(hi)
        self.ceiling = int(ceiling)        # 0-255, per channel, per LED
        self.budget_ma = float(budget_ma)  # for the whole span
        # The dimmest this region is allowed to be driven while it is
        # being asked for anything at all.  Weighted shedding is right
        # about priority and wrong about the endpoint: a shell with
        # shed 6 is at nothing long before the tubes have given up, so
        # a helmet left running settles into two glowing stripes and
        # stops reading as a helmet.  The floor costs a few milliamps
        # and keeps the shape.  It never lights an LED the preset
        # wanted dark, and it yields entirely if it will not fit.
        self.floor = float(floor)          # 0-255, per LED
        self.shed = float(shed)            # relative give under global pressure

    @property
    def n(self):
        return self.hi - self.lo + 1

    def full_white_ma(self):
        return self.n * MA_PER_LED_FULL_WHITE * self.ceiling / 255.0

    def __repr__(self):
        return ("Region(%s %d..%d ceiling=%d budget=%.0fmA shed=%.1f)"
                % (self.name, self.lo, self.hi, self.ceiling,
                   s
... [cut] ...
_ma": 300,
   "shed": 6.0,
   "floor": 3.0
  },
  {
   "name": "ear1_tubes",
   "lo": 398,
   "hi": 491,
   "ceiling": 255,
   "budget_ma": 620,
   "shed": 1.0,
   "floor": 6.0
  },
  {
   "name": "ear1_rim",
   "lo": 492,
   "hi": 509,
   "ceiling": 160,
   "budget_ma": 200,
   "shed": 3.0,
   "floor": 5.0
  },
  {
   "name": "ear2_rim",
   "lo": 510,
   "hi": 528,
   "ceiling": 160,
   "budget_ma": 190,
   "shed": 3.0,
   "floor": 5.0
  },
  {
   "name": "ear2_tubes",
   "lo": 529,
   "hi": 620,
   "ceiling": 255,
   "budget_ma": 640,
   "shed": 1.0,
   "floor": 6.0
  }
 ],
 "link_ma": 0.0
}
```

```
$ KIT=tools/showkit; cat $KIT/BRIEF.md; echo ======; cat $KIT/power.py; echo =====; cat $KIT/scenepower.py; date
Exit code 1
# Making one song's show for the deadmau5 helmet

You are choreographing one song for a real wearable LED helmet (deadmau5-style mau5head), for tonight's Halloween party. The owner's words: "Create these really good animations ... especially ones like the Tiki Tiki one, which was really good because it was unique. Keep doing these cool, unique ones for each song." Read `shows/scenes/TIKI TIKI - Slowed.scene.json` and its generator `(scratch)/tiki/write_treatment.py` first: that is the bar. A show is a story with its own world, palette and characters; motifs come back when the music does; builds visibly grow; drops land exactly on the bass; breakdowns strip back to almost nothing; the ears play as an instrument of their own. It must not look like a sequence of effects, and it must not look like any other show.

Working directory: `~/deadmau5 app` (main checkout, run everything from there). `KIT=tools/showkit`. Your scratch files go in `$KIT/work/<short song name>/`.

## Hard rules
- Only write these files for your song: `shows/scenes/<base>.beats`, `shows/scenes/<base>.scene.json`, `shows/scenes/<base>.sprites.json`, and what the tools make: `shows/<base>.json`, `shows/<base>.analysis.npz`. Nine other authors are working beside you on other songs. Never edit any code, any test, or another song's file. If you truly need an engine feature, finish without it and say so in your report.
- NEVER contact the helmet (192.168.10.172, 4.3.2.1, or anything scanning the network). Do not run `mau5show.py play`, `mau5offline.py`, `mau5ctl`, `test_mau5.py`, or anything that starts a browser
... [cut] ...
t the guard does that matters: the shell region is capped near 300 mA (mean about 10 of 255) with a soft knee, so anything above about 64 comes out near 62 and hues shift; when the whole frame hits 1000 mA the governor sheds the shell hard, so on a big hit with loud ears the shell can go almost black, and full-shell white comes out gray. So on hits: dark ears on the first beat if the shell has the picture, or give the moment to the ears on purpose. `python3 $KIT/scenepower.py "<base>"` prints per scene the mA, how often the governor hit, shell and ear means, and heat.
(eval):1: ===== not found
```

```
$ cd "~/deadmau5 app"; grep -n "def \|^class \|^[A-Z_]* = " mau5power.py | head -60; wc -l mau5power.py
43:HERE = os.path.dirname(os.path.abspath(__file__))
44:DEFAULT = os.path.join(HERE, "data", "cal", "power.json")
46:MA_PER_LED_FULL_WHITE = 19.0      # WS2815 at 12 V
47:MA_PER_LED_STANDBY = 1.0          # drawn whenever the rail is live
56:GOV_RISE = 1.0
57:GOV_MIN_DT = 1.0 / 40.0
58:GOV_FROM = 0.01
61:class Region:
72:    def __init__(self, name, lo, hi, ceiling, budget_ma, shed=1.0, floor=0.0):
88:    def n(self):
91:    def full_white_ma(self):
94:    def __repr__(self):
101:class ThermalBudget:
129:    def __init__(self, sustained_w=11.0, burst_j=900.0, max_w=None,
139:    def allowance_w(self):
147:    def update(self, led_watts, now=None):
166:    def state(self):
173:class PowerGuard:
176:    def __init__(self, count, regions, budget_ma, default_ceiling=32,
215:    def _per_led_ma(self, out):
218:    def frame_ma(self, buf):
223:    def standby_ma(self):
227:    def link_limit_ma(self):
236:    def apply(self, buf, now=None, gain=1.0):
416:    def describe(self):
445:def timid(count):
459:def load(path=DEFAULT, count=None):
490:def save(guard, path=DEFAULT):
     513 mau5power.py
```

```
$ KIT=tools/showkit; cat $KIT/BRIEF.md; echo ======; cat $KIT/power.py; echo =====; cat $KIT/scenepower.py; date
Exit code 1
# Making one song's show for the deadmau5 helmet

You are choreographing one song for a real wearable LED helmet (deadmau5-style mau5head), for tonight's Halloween party. The owner's words: "Create these really good animations ... especially ones like the Tiki Tiki one, which was really good because it was unique. Keep doing these cool, unique ones for each song." Read `shows/scenes/TIKI TIKI - Slowed.scene.json` and its generator `(scratch)/tiki/write_treatment.py` first: that is the bar. A show is a story with its own world, palette and characters; motifs come back when the music does; builds visibly grow; drops land exactly on the bass; breakdowns strip back to almost nothing; the ears play as an instrument of their own. It must not look like a sequence of effects, and it must not look like any other show.

Working directory: `~/deadmau5 app` (main checkout, run everything from there). `KIT=tools/showkit`. Your scratch files go in `$KIT/work/<short song name>/`.

## Hard rules
- Only write these files for your song: `shows/scenes/<base>.beats`, `shows/scenes/<base>.scene.json`, `shows/scenes/<base>.sprites.json`, and what the tools make: `shows/<base>.json`, `shows/<base>.analysis.npz`. Nine other authors are working beside you on other songs. Never edit any code, any test, or another song's file. If you truly need an engine feature, finish without it and say so in your report.
- NEVER contact the helmet (192.168.10.172, 4.3.2.1, or anything scanning the network). Do not run `mau5show.py play`, `mau5offline.py`, `mau5ctl`, `test_mau5.py`, or anything that starts a browser
... [cut] ...
t the guard does that matters: the shell region is capped near 300 mA (mean about 10 of 255) with a soft knee, so anything above about 64 comes out near 62 and hues shift; when the whole frame hits 1000 mA the governor sheds the shell hard, so on a big hit with loud ears the shell can go almost black, and full-shell white comes out gray. So on hits: dark ears on the first beat if the shell has the picture, or give the moment to the ears on purpose. `python3 $KIT/scenepower.py "<base>"` prints per scene the mA, how often the governor hit, shell and ear means, and heat.
(eval):1: ===== not found
```

```
$ cd "~/deadmau5 app"; grep -n "def \|^class \|^[A-Z_]* = " mau5power.py | head -60; wc -l mau5power.py
43:HERE = os.path.dirname(os.path.abspath(__file__))
44:DEFAULT = os.path.join(HERE, "data", "cal", "power.json")
46:MA_PER_LED_FULL_WHITE = 19.0      # WS2815 at 12 V
47:MA_PER_LED_STANDBY = 1.0          # drawn whenever the rail is live
56:GOV_RISE = 1.0
57:GOV_MIN_DT = 1.0 / 40.0
58:GOV_FROM = 0.01
61:class Region:
72:    def __init__(self, name, lo, hi, ceiling, budget_ma, shed=1.0, floor=0.0):
88:    def n(self):
91:    def full_white_ma(self):
94:    def __repr__(self):
101:class ThermalBudget:
129:    def __init__(self, sustained_w=11.0, burst_j=900.0, max_w=None,
139:    def allowance_w(self):
147:    def update(self, led_watts, now=None):
166:    def state(self):
173:class PowerGuard:
176:    def __init__(self, count, regions, budget_ma, default_ceiling=32,
215:    def _per_led_ma(self, out):
218:    def frame_ma(self, buf):
223:    def standby_ma(self):
227:    def link_limit_ma(self):
236:    def apply(self, buf, now=None, gain=1.0):
416:    def describe(self):
445:def timid(count):
459:def load(path=DEFAULT, count=None):
490:def save(guard, path=DEFAULT):
     513 mau5power.py
```

```
$ KIT=tools/showkit; cat "$KIT/power.py"; echo; echo ---; cat "$KIT/scenepower.py"; echo; echo ---; cd "~/deadmau5 app"; cat data/cal/power.json; sed -n 173,415p mau5power.py; date
#!/usr/bin/env python3
"""power.py "<base>" -- the whole song from a cold helmet, through the real power guard, at 12 fps:
mean watts, where the heat ends up, and the hottest stretches. Run from the repo root.
A set of songs back to back stays fresh only if songs average about 11.5 W or less: the helmet can
shed 11 W for ever, and the 3000 J bucket covers only the excess. Above that, heat builds up song
after song, and once the bucket is full every hit in the rest of the set gets flattened."""
import json, os, sys
sys.path.insert(0, os.getcwd())
import numpy as np, mau5show, mau5power, mau5scene, mau5engine as E
base = sys.argv[1]
fps = 12.0
show = json.load(open(os.path.join("shows", base + ".json")))
music = mau5show._music_for(show, os.path.join("shows", base + ".mp3"))
spec = show.get("scenes")
if not spec:
    raise SystemExit("no scenes compiled yet")
h = E.Helmet()
sc = mau5scene.Scenes(spec, h)
guard = mau5power.load(count=h.n)
dur = float(show["duration"])
per = {}
order = []
watts = []
heat = 0.0
for i in range(int(dur * fps)):
    t = i / fps
    out, gain, label = sc.frame(t, music)
    _, rep = guard.apply(out, now=t, gain=gain)
    w = float(rep.get("watts", 0.0))
    watts.append(w)
    th = rep.get("thermal") or {}
    heat = th.get("full_pct", 0.0)
    nm = label.split(" · ")[0] or "(outside)"
    if nm not in per:
        per[nm] = []
        order.append(nm)
    per[nm].append(w)
print("%s: %.0f s, mean %.1f W (target 11.5 or less), heat at the end %.0f%%" % (base, dur, np.mean(watts), heat))
hot = sorted(order, key=lambda n: -np.mean(per[n]) * (len(per[n]) ** 0.5))[:8]
print("hottest scenes (name, mean W, seconds): " + "; ".join("%s %.1f %.0fs" % (n, np.mean(per[n]), len(per[n]) / fps) for n in hot))

---
#!/usr/bin/env python3
"""pow.py "<base>": pe
... [cut] ...
 + self.standby_ma(), 1),
            "amps": round((final + self.standby_ma()) / 1000.0, 2),
            "watts": round((final + self.standby_ma()) * 12 / 1000.0, 1),
            "ceiling_hit": asked > after_ceiling + 0.5,
            "regions_hit": hit,
            "governor_hit": governed,
            "floor_hit": floored,
            "budget_ma": round(budget, 1),
            "link_ma": self.link_ma or None,
            "thermal": self.thermal.state() if self.thermal else None,
        }

    # -- reporting ------------------------------------------------------
Sat Oct 31 13:09:28 PDT 2026
```

You've hit your session limit · resets 5:10pm (America/Los_Angeles)
