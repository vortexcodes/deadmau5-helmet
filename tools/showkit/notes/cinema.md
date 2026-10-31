# What the cinema builder ran and saw

Commands and their text output, in order, with long output cut. Images are left out; rerun the tools to see them. Cut off partway: the generator and treatment in the repo are the latest state.

I'll start by reading the brief.

```
$ date; KIT=tools/showkit; ls -la "$KIT"; ls -la "$KIT/work" 2>/dev/null
Sat Oct 31 12:39:04 PDT 2026
total 168
drwxr-xr-x@  11 jones  wheel    352 Oct 31 12:38 .
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
total 1616
drwxr-xr-x@  3 jones  wheel      96 Oct 31 12:37 .
drwxr-xr-x@ 11 jones  wheel     352 Oct 31 12:38 ..
-rw-r--r--@  1 jones  wheel  823816 Oct 31 12:37 deadmau5_The_Veldt_mp3.env.npz
```

```
$ date; KIT=tools/showkit; ls -la "$KIT"; ls -la "$KIT/work" 2>/dev/null
Sat Oct 31 12:39:04 PDT 2026
total 168
drwxr-xr-x@  11 jones  wheel    352 Oct 31 12:38 .
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
total 1616
drwxr-xr-x@  3 jones  wheel      96 Oct 31 12:37 .
drwxr-xr-x@ 11 jones  wheel     352 Oct 31 12:38 ..
-rw-r--r--@  1 jones  wheel  823816 Oct 31 12:37 deadmau5_The_Veldt_mp3.env.npz
```

```
$ KIT=tools/showkit; mkdir -p "$KIT/work/cinema"; cat "$KIT/grid.py"; echo ------; cat "$KIT/fmt.py"; echo ------; cat "$KIT/sheet.py"; echo ------; cat "$KIT/songmap.py"; echo ------; cat "$KIT/spectro.py"; echo -----; cat "$KIT/spritetry.py"
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
t, default=166.0)
ap.add_argument("--x_half", type=float, default=171.0)
a = ap.parse_args()
h = E.Helmet(); sc = PV.Scene(h)
ims = []
for nm in a.names:
    f = np.asarray(E.make("sprite", sprite=nm, color=(255, 170, 40), y_lo=a.y_lo, y_hi=a.y_hi, x_half=a.x_half).render(h, 0.0, None), float)
    im = sc.frame(f).crop((130, 150, 630, 620)).resize((360, 338))
    ImageDraw.Draw(im).text((6, 4), nm, fill=(255, 255, 255))
    ims.append(im)
o = Image.new("RGB", (sum(i.width for i in ims), ims[0].height))
x = 0
for i in ims:
    o.paste(i, (x, 0)); x += i.width
o.save(a.out); print(a.out, o.size)
```

```
$ cat "(scratch)/tiki/write_treatment.py"
import json
KICK="x.......x......."
idolp={"sprite":"tiki","y_lo":-108,"y_hi":166,"x_half":171}
tr={"v":1,"show":"TIKI TIKI - Slowed",
"about":"Bars of a measured grid, shows/scenes/TIKI TIKI - Slowed.beats: bar b starts at 1.796 + 1.739 b seconds (137.98 BPM), 183 bars, and at bar 119.5 the track is spliced, so the music comes back 197 ms late and the grid holds still for it. Everything from there is the song's opening again, bar for bar. The bar line is where the phrases turn, with the kick on 1 and 3 and the clap on 2 and 4 with a flick on the and of 2. A night on the island. Torches get lit one tube at a time; the hooks are fire climbing the shell with the ears burning as torches, the kick on the rims and the clap up the tubes. Every breakdown goes out to the lagoon, cold water and moon glints, with one stopped bar of almost nothing, and the title crosses the face once, in the first. The verses are bamboo: upright stalks swaying on the face, the two sides stomping in turn. The big sections wake the idol, a carved mask drawn to fit the LEDs that exist: brow and eyes on the dome, teeth along the jaw, since the middle of the face has no LEDs. It burns in torch colours the first time, at sunset the second, and half fire, half water the third, swapping sides. The song then starts over, so the show does too, and the last big section has everything, with white once. At the end the torches go out one tube at a time and the idol is last to go. Shell layers are kept near the shell's 300 mA and nothing on it pulses faster than a beat.",
"lead":0,
"marks":{"hush":2,"light":3,"hook":5,"hookb":9,"dip":13,"climb":14,"hook2":15,"burn":21,
 "water":25,"stop":26,"still":27,"swell":30,"verse":31,"vlow":37,"vrise":38,"big":39,"bigb":47,"burn2":57,
 "water2":61,"stop2":62,"still2":63,"s
... [cut] ...
'"lead":0,','"marks":'+json.dumps(tr["marks"])+',']
out.append('"palettes":{\n'+",\n".join("  %s: %s"%(json.dumps(k),json.dumps(v)) for k,v in tr["palettes"].items())+'\n },')
out.append('"motifs":{\n'+",\n".join("  %s: %s"%(json.dumps(k),json.dumps(v)) for k,v in tr["motifs"].items())+'\n },')
out.append('"scenes":'+block(tr["scenes"])+',')
out.append('"hits":'+block(tr["hits"]))
out.append('}')
open('shows/scenes/TIKI TIKI - Slowed.scene.json','w').write("\n".join(out)+"\n")
json.load(open('shows/scenes/TIKI TIKI - Slowed.scene.json'))
print('scenes',len(tr["scenes"]),'hits',len(tr["hits"]))
```

```
$ cd "~/deadmau5 app"; ls -la shows/ | head -80; ls -la shows/scenes/ | head -80; python3 -c "
import json
d=json.load(open('shows/scenes/TIKI TIKI - Slowed.scene.json'))
print(json.dumps(d,indent=None)[:3000])
print(d.keys())
print(d['about'])
print(d.get('marks'))
print(len(d['scenes']),len(d['hits']))
"
total 303624
drwxr-xr-x@ 33 jones  staff      1056 Oct 31 12:37 .
drwxr-xr-x  76 jones  staff      2432 Oct 30 19:24 ..
drwxr-xr-x@  6 jones  staff       192 Oct 31 12:37 .mau5cache
-rw-r--r--@  1 jones  staff    247736 Oct 28 00:04 Fred again.. & Baby Keem - leavemealone.analysis.npz
-rw-r--r--@  1 jones  staff     94043 Oct 30 05:37 Fred again.. & Baby Keem - leavemealone.json
-rw-r--r--@  1 jones  staff   7130157 Sep  1 10:54 Fred again.. & Baby Keem - leavemealone.mp3
-rw-r--r--@  1 jones  staff   5664436 Oct 31 12:37 Kaskade feat. deadmau5 - I Remember.mp3
-rw-r--r--@  1 jones  staff    343358 Oct 30 19:15 TIKI TIKI - Slowed.analysis.npz
-rw-r--r--@  1 jones  staff    171705 Oct 30 19:20 TIKI TIKI - Slowed.json
-rw-r--r--@  1 jones  staff  12807357 Oct 30 19:08 TIKI TIKI - Slowed.mp3
-rw-r--r--@  1 jones  staff   9635715 Oct 30 19:24 TIKI TIKI - Slowed_preview.mp4
-rw-r--r--@  1 jones  staff    293771 Oct 31 12:23 beneath (with raxaj).analysis.npz
-rw-r--r--@  1 jones  staff     66264 Oct 31 12:23 beneath (with raxaj).json
-rw-r--r--@  1 jones  staff  15003733 Oct 31 12:37 deadmau5 & Wolfgang Gartner - Animal Rights.mp3
-rw-r--r--@  1 jones  staff   8504259 Oct 31 12:37 deadmau5 - FN Pig.mp3
-rw-r--r--@  1 jones  staff    438714 Oct 31 12:18 deadmau5 - Ghosts n Stuff (Nero Remix).analysis.npz
-rw-r--r--@  1 jones  staff     54424 Oct 31 12:18 deadmau5 - Ghosts n Stuff (Nero Remix).json
-rw-r--r--@  1 jones  staff   7179120 Oct 31 12:37 deadmau5 - Harder Better Faster Stronger.mp3
-rw-r--r--@  1 jones  staff   6481337 Oct 31 12:37 deadmau5 - Moar Ghosts n Stuff.mp3
-rw-r--r--@  1 jones  staff  12072377 Oct 31 12:37 deadmau5 - Raise Your Weapon.mp3
-rw-r--r--@  1 jones  staff   8402068 Oct 31 12:37 deadmau5 - Some Chords (Radio Edit).mp3
-rw-r--r--@  1 jones  staff  
... [cut] ...
 38, 'big': 39, 'bigb': 47, 'burn2': 57, 'water2': 61, 'stop2': 62, 'still2': 63, 'swell2': 66, 'verse2': 67, 'vlow2': 73, 'vrise2': 74, 'big2': 75, 'big2b': 83, 'burn3': 89, 'water3': 93, 'stop3': 94, 'still3': 95, 'swell3': 98, 'verse3': 99, 'vlow3': 105, 'vrise3': 106, 'big3': 107, 'big3b': 113, 'big3c': 117, 'seam': 119.5, 'hook3': 123, 'dip2': 127, 'climb2': 128, 'hook4': 129, 'burn4': 135, 'water4': 139, 'stop4': 140, 'still4': 141, 'swell4': 144, 'verse4': 145, 'vlow4': 151, 'vrise4': 152, 'final': 153, 'final2': 161, 'wind': 169, 'out1': 173, 'out2': 176, 'out3': 178, 'end': 181}
56 15
```

```
$ KIT=tools/showkit; mkdir -p "$KIT/work/cinema"; cat "$KIT/grid.py"; echo ------; cat "$KIT/fmt.py"; echo ------; cat "$KIT/sheet.py"; echo ------; cat "$KIT/songmap.py"; echo ------; cat "$KIT/spectro.py"; echo -----; cat "$KIT/spritetry.py"
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
t, default=166.0)
ap.add_argument("--x_half", type=float, default=171.0)
a = ap.parse_args()
h = E.Helmet(); sc = PV.Scene(h)
ims = []
for nm in a.names:
    f = np.asarray(E.make("sprite", sprite=nm, color=(255, 170, 40), y_lo=a.y_lo, y_hi=a.y_hi, x_half=a.x_half).render(h, 0.0, None), float)
    im = sc.frame(f).crop((130, 150, 630, 620)).resize((360, 338))
    ImageDraw.Draw(im).text((6, 4), nm, fill=(255, 255, 255))
    ims.append(im)
o = Image.new("RGB", (sum(i.width for i in ims), ims[0].height))
x = 0
for i in ims:
    o.paste(i, (x, 0)); x += i.width
o.save(a.out); print(a.out, o.size)
```

```
$ cat "(scratch)/tiki/write_treatment.py"
import json
KICK="x.......x......."
idolp={"sprite":"tiki","y_lo":-108,"y_hi":166,"x_half":171}
tr={"v":1,"show":"TIKI TIKI - Slowed",
"about":"Bars of a measured grid, shows/scenes/TIKI TIKI - Slowed.beats: bar b starts at 1.796 + 1.739 b seconds (137.98 BPM), 183 bars, and at bar 119.5 the track is spliced, so the music comes back 197 ms late and the grid holds still for it. Everything from there is the song's opening again, bar for bar. The bar line is where the phrases turn, with the kick on 1 and 3 and the clap on 2 and 4 with a flick on the and of 2. A night on the island. Torches get lit one tube at a time; the hooks are fire climbing the shell with the ears burning as torches, the kick on the rims and the clap up the tubes. Every breakdown goes out to the lagoon, cold water and moon glints, with one stopped bar of almost nothing, and the title crosses the face once, in the first. The verses are bamboo: upright stalks swaying on the face, the two sides stomping in turn. The big sections wake the idol, a carved mask drawn to fit the LEDs that exist: brow and eyes on the dome, teeth along the jaw, since the middle of the face has no LEDs. It burns in torch colours the first time, at sunset the second, and half fire, half water the third, swapping sides. The song then starts over, so the show does too, and the last big section has everything, with white once. At the end the torches go out one tube at a time and the idol is last to go. Shell layers are kept near the shell's 300 mA and nothing on it pulses faster than a beat.",
"lead":0,
"marks":{"hush":2,"light":3,"hook":5,"hookb":9,"dip":13,"climb":14,"hook2":15,"burn":21,
 "water":25,"stop":26,"still":27,"swell":30,"verse":31,"vlow":37,"vrise":38,"big":39,"bigb":47,"burn2":57,
 "water2":61,"stop2":62,"still2":63,"s
... [cut] ...
'"lead":0,','"marks":'+json.dumps(tr["marks"])+',']
out.append('"palettes":{\n'+",\n".join("  %s: %s"%(json.dumps(k),json.dumps(v)) for k,v in tr["palettes"].items())+'\n },')
out.append('"motifs":{\n'+",\n".join("  %s: %s"%(json.dumps(k),json.dumps(v)) for k,v in tr["motifs"].items())+'\n },')
out.append('"scenes":'+block(tr["scenes"])+',')
out.append('"hits":'+block(tr["hits"]))
out.append('}')
open('shows/scenes/TIKI TIKI - Slowed.scene.json','w').write("\n".join(out)+"\n")
json.load(open('shows/scenes/TIKI TIKI - Slowed.scene.json'))
print('scenes',len(tr["scenes"]),'hits',len(tr["hits"]))
```

```
$ cd "~/deadmau5 app"; ls -la shows/ | head -80; ls -la shows/scenes/ | head -80; python3 -c "
import json
d=json.load(open('shows/scenes/TIKI TIKI - Slowed.scene.json'))
print(json.dumps(d,indent=None)[:3000])
print(d.keys())
print(d['about'])
print(d.get('marks'))
print(len(d['scenes']),len(d['hits']))
"
total 303624
drwxr-xr-x@ 33 jones  staff      1056 Oct 31 12:37 .
drwxr-xr-x  76 jones  staff      2432 Oct 30 19:24 ..
drwxr-xr-x@  6 jones  staff       192 Oct 31 12:37 .mau5cache
-rw-r--r--@  1 jones  staff    247736 Oct 28 00:04 Fred again.. & Baby Keem - leavemealone.analysis.npz
-rw-r--r--@  1 jones  staff     94043 Oct 30 05:37 Fred again.. & Baby Keem - leavemealone.json
-rw-r--r--@  1 jones  staff   7130157 Sep  1 10:54 Fred again.. & Baby Keem - leavemealone.mp3
-rw-r--r--@  1 jones  staff   5664436 Oct 31 12:37 Kaskade feat. deadmau5 - I Remember.mp3
-rw-r--r--@  1 jones  staff    343358 Oct 30 19:15 TIKI TIKI - Slowed.analysis.npz
-rw-r--r--@  1 jones  staff    171705 Oct 30 19:20 TIKI TIKI - Slowed.json
-rw-r--r--@  1 jones  staff  12807357 Oct 30 19:08 TIKI TIKI - Slowed.mp3
-rw-r--r--@  1 jones  staff   9635715 Oct 30 19:24 TIKI TIKI - Slowed_preview.mp4
-rw-r--r--@  1 jones  staff    293771 Oct 31 12:23 beneath (with raxaj).analysis.npz
-rw-r--r--@  1 jones  staff     66264 Oct 31 12:23 beneath (with raxaj).json
-rw-r--r--@  1 jones  staff  15003733 Oct 31 12:37 deadmau5 & Wolfgang Gartner - Animal Rights.mp3
-rw-r--r--@  1 jones  staff   8504259 Oct 31 12:37 deadmau5 - FN Pig.mp3
-rw-r--r--@  1 jones  staff    438714 Oct 31 12:18 deadmau5 - Ghosts n Stuff (Nero Remix).analysis.npz
-rw-r--r--@  1 jones  staff     54424 Oct 31 12:18 deadmau5 - Ghosts n Stuff (Nero Remix).json
-rw-r--r--@  1 jones  staff   7179120 Oct 31 12:37 deadmau5 - Harder Better Faster Stronger.mp3
-rw-r--r--@  1 jones  staff   6481337 Oct 31 12:37 deadmau5 - Moar Ghosts n Stuff.mp3
-rw-r--r--@  1 jones  staff  12072377 Oct 31 12:37 deadmau5 - Raise Your Weapon.mp3
-rw-r--r--@  1 jones  staff   8402068 Oct 31 12:37 deadmau5 - Some Chords (Radio Edit).mp3
-rw-r--r--@  1 jones  staff  
... [cut] ...
 38, 'big': 39, 'bigb': 47, 'burn2': 57, 'water2': 61, 'stop2': 62, 'still2': 63, 'swell2': 66, 'verse2': 67, 'vlow2': 73, 'vrise2': 74, 'big2': 75, 'big2b': 83, 'burn3': 89, 'water3': 93, 'stop3': 94, 'still3': 95, 'swell3': 98, 'verse3': 99, 'vlow3': 105, 'vrise3': 106, 'big3': 107, 'big3b': 113, 'big3c': 117, 'seam': 119.5, 'hook3': 123, 'dip2': 127, 'climb2': 128, 'hook4': 129, 'burn4': 135, 'water4': 139, 'stop4': 140, 'still4': 141, 'swell4': 144, 'verse4': 145, 'vlow4': 151, 'vrise4': 152, 'final': 153, 'final2': 161, 'wind': 169, 'out1': 173, 'out2': 176, 'out3': 178, 'end': 181}
56 15
```

```
$ cd "~/deadmau5 app"; KIT=tools/showkit; time python3 "$KIT/grid.py" scan "shows/deadmau5 - Strobe (Special Features Remix).mp3" 2>&1 | tail -30
estimator: 128.000 BPM, first bar 0.139 s, tempo lock 0.725, bar lock 0.2527074915223058; song 393.8 s
refined over the whole song: spb 0.468751 = 128.000 BPM
first half 128.000 BPM, second half 128.000 BPM (these should agree within 0.05)
phase of the music against that grid per 8 bars, ms (flat = right; one 16th = 117 ms; contrast under 1.15 means sparse, ignore it):
  0:-7(5.98)  8:-5(4.82)  16:-5(2.63)  24:-5(3.52)  32:-1(3.03)  40:-1(2.97)  48:-5(1.21)  56:-5(2.15)  64:-1(1.97)  72:-1(2.18)  80:-1(1.87)  88:-1(1.95)  96:-5(1.71)  104:-5(1.27)  112:-1(2.67)  120:-1(2.80)  128:-7(5.13)  136:-5(3.56)  144:+1(2.25)  152:-1(1.91)  160:-1(2.13)  168:-3(1.96)  176:-3(3.87)  184:-3(3.78)  192:-3(3.06)  200:-5(3.38)  208:+1(2.70)
change per beat position, estimator's bar 1 at 0.139 s: 0:0.72 1:0.64 2:0.64 3:0.62  (the highest is where bars really start, 0 = estimator is right)
strongest phrase positions, in beats mod 32 from that bar 1: 0(1.97), 30(1.34), 31(1.34), 1(1.30), 29(1.17), 28(0.84)
biggest single changes (time, beat from bar 1, beat mod 4): 89.7s b191 m3; 90.1s b192 m0; 119.7s b255 m3; 120.1s b256 m0; 149.2s b318 m2; 150.1s b320 m0; 163.7s b349 m1; 164.2s b350 m2; 165.1s b352 m0; 179.7s b383 m3; 180.1s b384 m0; 195.1s b416 m0; 269.2s b574 m2; 269.7s b575 m3; 270.1s b576 m0; 298.7s b637 m1; 299.2s b638 m2; 300.1s b640 m0; 314.2s b670 m2; 315.1s b672 m0; 328.3s b700 m0; 329.7s b703 m3; 390.1s b832 m0; 390.6s b833 m1
suggested next: grid.py fold with --spb 0.468751 --anchor 0.139, decide the bar line, then grid.py write
python3 "$KIT/grid.py" scan  2>&1  2.34s user 0.65s system 109% cpu 2.742 total
tail -30  0.00s user 0.00s system 0% cpu 2.741 total
```

```
$ cd "~/deadmau5 app"; python3 - <<'EOF'
import json
for f in ["deadmau5 - Strobe","deadmau5 - Strobe (Dimension Remix)"]:
    d=json.load(open('shows/scenes/%s.scene.json'%f))
    print("=====",f)
    print(d.get('about'))
    print(d.get('palettes'))
    print(d.get('marks'))
    print([s['name'] for s in d['scenes']])
    print([h['name'] for h in d['hits']])
EOF
ffprobe -hide_banner "shows/deadmau5 - Strobe (Special Features Remix).mp3" 2>&1 | tail -12
===== deadmau5 - Strobe
Bars of the analysis grid: bar b starts at 1.756 + 1.875 b seconds, 339 bars. One constellation of sixteen sparks is the arpeggio, and it comes back every time the arpeggio does. Ice is the climb, dawn the breakdowns, strobe the drops, pure the ear hits. White once, on the drop at 217.
{'ice': [[0, 0, 0], [0, 20, 90], [0, 140, 255], [200, 240, 255]], 'dawn': [[8, 0, 24], [110, 0, 170], [255, 40, 110], [255, 170, 60]], 'strobe': {'stops': [[0, 60, 255], [0, 230, 255], [255, 255, 255], [120, 0, 255]], 'wrap': True}, 'pure': [[0, 0, 255], [0, 200, 255], [255, 255, 255]]}
{'call': 12, 'climb': 48, 'bloom1': 84, 'break1': 108, 'title': 116, 'riser': 136, 'return': 141, 'eyes': 168, 'build': 184, 'lift': 205, 'suck': 213, 'drop': 217, 'dropB': 233, 'dropC': 249, 'groove': 268, 'wind': 297, 'outro': 316, 'last': 329, 'end': 330}
['arp', 'call', 'climb', 'bloom1', 'break1', 'riser', 'bloom2', 'eyes', 'build', 'lift', 'suck', 'drop A', 'drop B', 'drop A+', 'groove', 'wind', 'outro']
['bloom', 'STROBE', 'return', 'lift', 'DROP', 'last']
===== deadmau5 - Strobe (Dimension Remix)
Bars of the analysis grid: bar b starts at 1.037 + 1.379 b seconds, 224 bars, 174 BPM. The analysis puts its bar line one beat early: the kick, every entry, both drops and every phrase restart land on its beat two, so every mark here sits at .25, a beat past the grid's downbeat. Strobe's own language comes back -- the same sixteen-spark constellation (loop 16, seed 3) whenever the melody is alone, ice for the climb, dawn for the second breakdown, the strobe palette under the drops, the ladder, the spin, the ring, the X eyes -- and the remix adds its own: the two-step breakbeat played on the ears, the kick on both ears' tubes on 1 and the and-of-3, the snare in hot volt pink on the l
... [cut] ...
drop A', 'fill 1', 'drop B', 'fill 2', 'drop A+', 'fill 3', 'breakdown', 'eyes', 'build', 'suck 2', 'drop2 A', 'fill 4', 'drop2 B', 'fill 5', 'drop2 all', 'runout', 'outro']
['boom', 'STROBE (DIMENSION)', 'lift', 'DROP', 'B', 'A+', 'break', 'pickup', 'DROP 2', 'B2', 'all', 'last']
Input #0, mp3, from 'shows/deadmau5 - Strobe (Special Features Remix).mp3':
  Metadata:
    encoder         : Lavf58.20.100
  Duration: 00:06:33.80, start: 0.025057, bitrate: 320 kb/s
  Stream #0:0: Audio: mp3 (mp3float), 44100 Hz, stereo, fltp, 320 kb/s, start 0.025057
    Metadata:
      encoder         : Lavc58.35
```

```
$ cd "~/deadmau5 app"; KIT=tools/showkit; python3 "$KIT/grid.py" fold "shows/deadmau5 - Strobe (Special Features Remix).mp3" --spb 0.46875 --anchor 0.139 --spans "0-8,8-16,16-32,32-48,48-64,64-80,80-96,96-112,112-128,128-144,144-160,160-176,176-192,192-208,208-210" 2>&1
bar 0 at 0.139 s, 128.000 BPM, 209 bars
bars 0-8   (16 steps, | every beat; one row per band)
   sub     @   |@   |@   |@      peak 0.22
   bass    @   |# ..|@   |# ..   peak 0.76
   lowmid  @...|+..:|@...|=.::   peak 0.63
   mid     @   |@   |@   |@      peak 1.30
   pres    @   |@   |@   |@      peak 1.77
   air     @   |@   |@   |@      peak 1.46
bars 8-16   (16 steps, | every beat; one row per band)
   sub     @   |@   |%   |%      peak 0.24
   bass    @. .|% ..|@   |# .    peak 0.67
   lowmid  @-.=|*=-+|%=.-|+==*   peak 0.29
   mid     @. .|#.. |@. .|%..    peak 0.81
   pres    @   |@   |@   |@      peak 1.36
   air     @   |@   |@   |@      peak 1.30
bars 16-32   (16 steps, | every beat; one row per band)
   sub     @   |#   |@   |@      peak 0.18
   bass    @ . |#.: |% . |#..    peak 0.75
   lowmid  @.+:|%:*:|@.+:|%:#:   peak 0.43
   mid     @.#:|# +:|@.*:|+ *-   peak 0.39
   pres    @ : |# . |@ :.|- :    peak 0.93
   air     @ - |- : |@ =.|  -    peak 1.22
bars 32-48   (16 steps, | every beat; one row per band)
   sub     @ ..|%...|%..:|% ::   peak 0.23
   bass    @ ..|% :.|% : |# .    peak 0.96
   lowmid  %.-.|#.=.|@.-.|*.=.   peak 0.66
   mid     @.*.|* +:|@.*:|+ +:   peak 0.41
   pres    @.: |% - |% -.|= =.   peak 0.68
   air     @ + |+ * |% *:| .%    peak 0.67
bars 48-64   (16 steps, | every beat; one row per band)
   sub     -=#+|++%=|++==|@-+.   peak 0.12
   bass    ++*=|==#+|=-+=|@=+:   peak 0.18
   lowmid  @*+%|###*|%+%*|%+@=   peak 0.15
   mid     =-@+|====|==+-|*=++   peak 0.21
   pres    *+*=|++@+|=+%=|**@+   peak 0.11
   air     @-+-|--%-|==+:|%=+-   peak 0.07
bars 64-80   (16 steps, | every beat; one row per band)
   sub     @:.:|*.+:|#:::|%.:-   peak 0.39
   bass    @::.|#:::|%::.|@::.   peak 0.78
   lowmid  @-::|#:::|@-:.|%:..   peak 0.46
   mid  
... [cut] ...
ry beat; one row per band)
   sub     *@+ |+@# |:@* |:#=    peak 0.13
   bass    @.: |%.: |% . |@.:    peak 0.59
   lowmid  @ : |# : |% : |%.:    peak 0.63
   mid     @::=|= ::|@-::|=.--   peak 0.69
   pres    @  .|*   |@...|-  .   peak 1.19
   air     @   |-   |% :.|       peak 1.33
bars 208-210   (16 steps, | every beat; one row per band)
   sub     @   |    |    |       peak 0.01
   bass    @   |.   |    |       peak 0.07
   lowmid  @. .|-   |.   |       peak 0.11
   mid     -:@%|::%#|:.#+|+.*-   peak 0.15
   pres    * . |@ . |*   |+      peak 0.21
   air     @ . |=   |.   |       peak 0.12
```

```
$ cd "~/deadmau5 app"; sed -n 1,200p mau5scene.py
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
$ cd "~/deadmau5 app"; KIT=tools/showkit; python3 "$KIT/grid.py" fold "shows/deadmau5 - Strobe (Special Features Remix).mp3" --spb 0.46875 --anchor 0.139 --spans "0-8,8-16,16-32,32-48,48-64,64-80,80-96,96-112,112-128,128-144,144-160,160-176,176-192,192-208,208-210" 2>&1
bar 0 at 0.139 s, 128.000 BPM, 209 bars
bars 0-8   (16 steps, | every beat; one row per band)
   sub     @   |@   |@   |@      peak 0.22
   bass    @   |# ..|@   |# ..   peak 0.76
   lowmid  @...|+..:|@...|=.::   peak 0.63
   mid     @   |@   |@   |@      peak 1.30
   pres    @   |@   |@   |@      peak 1.77
   air     @   |@   |@   |@      peak 1.46
bars 8-16   (16 steps, | every beat; one row per band)
   sub     @   |@   |%   |%      peak 0.24
   bass    @. .|% ..|@   |# .    peak 0.67
   lowmid  @-.=|*=-+|%=.-|+==*   peak 0.29
   mid     @. .|#.. |@. .|%..    peak 0.81
   pres    @   |@   |@   |@      peak 1.36
   air     @   |@   |@   |@      peak 1.30
bars 16-32   (16 steps, | every beat; one row per band)
   sub     @   |#   |@   |@      peak 0.18
   bass    @ . |#.: |% . |#..    peak 0.75
   lowmid  @.+:|%:*:|@.+:|%:#:   peak 0.43
   mid     @.#:|# +:|@.*:|+ *-   peak 0.39
   pres    @ : |# . |@ :.|- :    peak 0.93
   air     @ - |- : |@ =.|  -    peak 1.22
bars 32-48   (16 steps, | every beat; one row per band)
   sub     @ ..|%...|%..:|% ::   peak 0.23
   bass    @ ..|% :.|% : |# .    peak 0.96
   lowmid  %.-.|#.=.|@.-.|*.=.   peak 0.66
   mid     @.*.|* +:|@.*:|+ +:   peak 0.41
   pres    @.: |% - |% -.|= =.   peak 0.68
   air     @ + |+ * |% *:| .%    peak 0.67
bars 48-64   (16 steps, | every beat; one row per band)
   sub     -=#+|++%=|++==|@-+.   peak 0.12
   bass    ++*=|==#+|=-+=|@=+:   peak 0.18
   lowmid  @*+%|###*|%+%*|%+@=   peak 0.15
   mid     =-@+|====|==+-|*=++   peak 0.21
   pres    *+*=|++@+|=+%=|**@+   peak 0.11
   air     @-+-|--%-|==+:|%=+-   peak 0.07
bars 64-80   (16 steps, | every beat; one row per band)
   sub     @:.:|*.+:|#:::|%.:-   peak 0.39
   bass    @::.|#:::|%::.|@::.   peak 0.78
   lowmid  @-::|#:::|@-:.|%:..   peak 0.46
   mid  
... [cut] ...
ry beat; one row per band)
   sub     *@+ |+@# |:@* |:#=    peak 0.13
   bass    @.: |%.: |% . |@.:    peak 0.59
   lowmid  @ : |# : |% : |%.:    peak 0.63
   mid     @::=|= ::|@-::|=.--   peak 0.69
   pres    @  .|*   |@...|-  .   peak 1.19
   air     @   |-   |% :.|       peak 1.33
bars 208-210   (16 steps, | every beat; one row per band)
   sub     @   |    |    |       peak 0.01
   bass    @   |.   |    |       peak 0.07
   lowmid  @. .|-   |.   |       peak 0.11
   mid     -:@%|::%#|:.#+|+.*-   peak 0.15
   pres    * . |@ . |*   |+      peak 0.21
   air     @ . |=   |.   |       peak 0.12
```

```
$ cd "~/deadmau5 app"; sed -n 1,200p mau5scene.py
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
$ cd "~/deadmau5 app"; KIT=tools/showkit; python3 "$KIT/grid.py" write "deadmau5 - Strobe (Special Features Remix)" --spb 0.46875 --anchor 0.136 2>&1 | tail -15; python3 "$KIT/grid.py" check "deadmau5 - Strobe (Special Features Remix)"; python3 "$KIT/songmap.py" "deadmau5 - Strobe (Special Features Remix)"; python3 "$KIT/spectro.py" "deadmau5 - Strobe (Special Features Remix)" "$KIT/work/cinema/whole.png"
    2:30.14-2:45.14  lvl2  beatpulse  {}
    2:45.14-3:00.14  lvl2  police     {'hz': 4.267}
    3:00.14-3:37.64  lvl0  tubepulse  {'period': 7.5}
    3:37.64-3:52.64  lvl1  wipe       {'period': 3.75, 'a': (255, 0, 120), 'b': (255, 200, 0)}
    3:52.64-4:00.14  lvl1  matrix     {}
    4:00.14-4:30.14  lvl0  breathe    {'period': 8.0}
    4:30.14-4:45.14  lvl2  strobe     {'hz': 8.0}
    4:45.14-5:00.14  lvl2  blades     {'period': 1.875}
    5:00.14-5:15.14  lvl2  eq         {}
    5:15.14-5:30.14  lvl2  police     {'hz': 4.267}
    5:30.14-5:45.14  lvl2  fire       {}
    5:45.14-6:00.14  lvl2  comet      {'period': 1.6}
    6:00.14-6:15.14  lvl1  earspin    {'period': 2.4}
    6:15.14-6:32.01  lvl1  scanner    {'period': 3.75}
wrote shows/scenes/deadmau5 - Strobe (Special Features Remix).beats: 840 beats, 210 bars, bar 0 at 0.136 s, 128.000 BPM
deadmau5 - Strobe (Special Features Remix): 128.000 BPM, 210 bars, bar 0 at 0.136 s, holds []
music against the grid per 8 bars, ms (contrast): 0:-3(6.00)  8:-3(4.78)  16:-1(2.68)  24:-1(3.49)  32:+1(3.06)  40:+1(3.05)  48:-1(1.21)  56:-1(2.15)  64:+3(1.96)  72:+3(2.17)  80:+3(1.86)  88:+3(1.93)  96:-1(1.69)  104:-1(1.27)  112:+3(2.65)  120:+3(2.83)  128:-3(5.13)  136:-1(3.56)  144:+5(2.25)  152:+3(1.91)  160:+3(2.12)  168:+1(1.96)  176:+1(3.87)  184:+1(3.80)  192:+1(3.14)  200:-1(3.37)  208:+5(2.78)
worst 5 ms where the music is clear enough to say, mean +1.3 ms
deadmau5 - Strobe (Special Features Remix): 210 bars, 1.88 s a bar, 393.8 s
 bar     t   E  B  M  H  notes       change
   0    0.1   1  4  1  6  A C D       
   1    2.0   1  4  0  2  C A D       
   2    3.9   1  4  0  1  C A D       
   3    5.8   1  4  0  1  C A D       
   4    7.6   1  4  0  1  C A D       
   5    9.5   1  4  0  1  C A A#      
   6   11.4   1 
... [cut] ...
      
 198  371.4   3  6  3  4  A F C       
 199  373.3   2  5  2  3  A F G#      
 200  375.1   3  7  3  3  C A F       
 201  377.0   3  6  3  3  F C A       
 202  378.9   3  6  2  3  A F C       
 203  380.8   2  6  2  3  A F C       
 204  382.6   2  6  2  3  C F# F      
 205  384.5   1  5  2  3  F C A       
 206  386.4   1  4  3  5  A C F       
 207  388.3   0  2  2  6  A G# B      
 208  390.1   0  0  0  0  B G# A#     >>
 209  392.0   0  0  0  0  G# A# B     
tools/showkit/songs/cinema/whole.png
```

```
$ cd "~/deadmau5 app"; sed -n 200,620p mau5scene.py
_HELMET = None


def _helmet():
    global _HELMET
    if _HELMET is None:
        _HELMET = E.Helmet()
    return _HELMET


def _edge_mm(h):
    """Where a word must start to be wholly off the shell: one cell past it."""
    return float(np.abs(h.px[h.shell]).max()) + CELL


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
        if is
... [cut] ...
shell, bool) & (np.asarray(h.fa) >= 0)
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
```

```
$ cd "~/deadmau5 app"; sed -n 620,1400p mau5scene.py
<persisted-output>
Output too large (29.5KB). Full output saved to: ~/.claude/projects/-Users-jones-deadmau5-app/208332e7-8c9f-4c25-bc21-e9a9df98fa1f/tool-results/bbawiyjp8.txt

Preview (first 2KB):
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
    if not scenes or abs(scenes[0]["from"] + 1) > 1e-9 or abs(scenes[-1]["to"] - nb) > 1e-9:
        errs.append("the scenes must run from bar -1 to bar %d" % nb)
    for a, b in zip(scenes, scenes[1:]):
        if abs(a["to"] - b["from"]) > 1e-9:
            errs.append("scenes %s and %s do not meet" % (a["name"], b["name"]))

    if music is not None:
        g, n = grid_of(music)
        if (g["t0"] != spec["grid"]["t0"] or g["spb"] != spec["grid"]["spb"]
                or g.get("holds") != spec["grid"].get("holds") or n != nb):
            errs.append("the compiled grid is not the analysis' grid")

    def layer_checks(L, what, span):
        if L["fx"] not in FX:
            errs.append("%s: no fx %s" % (what, L["fx"]))
        if L["mix"] not in MIX:
            errs.append("%s: no mix %s" % (what, L["mix"]))
        if L["pal"] not in spec["pal"]:
            errs.append("%s: no palette %s" % (what, L["pal"]))
        try:
            m = _region_mask(h, L["on"])
        except TreatmentError as e:
            errs.append("%s: %s" % (what, e))
            return
        if not m.any():
            errs.append("%s: region %s has no LEDs" % (what, L["on"]))
        shell = bool((m & h.shell).any())
        for k in ("axis", "axis2"):
            if k in L and L[k] not in AXES:
...
</persisted-output>
```

```
$ cd "~/deadmau5 app"; sed -n 620,1400p mau5scene.py
<persisted-output>
Output too large (29.5KB). Full output saved to: ~/.claude/projects/-Users-jones-deadmau5-app/208332e7-8c9f-4c25-bc21-e9a9df98fa1f/tool-results/bbawiyjp8.txt

Preview (first 2KB):
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
    if not scenes or abs(scenes[0]["from"] + 1) > 1e-9 or abs(scenes[-1]["to"] - nb) > 1e-9:
        errs.append("the scenes must run from bar -1 to bar %d" % nb)
    for a, b in zip(scenes, scenes[1:]):
        if abs(a["to"] - b["from"]) > 1e-9:
            errs.append("scenes %s and %s do not meet" % (a["name"], b["name"]))

    if music is not None:
        g, n = grid_of(music)
        if (g["t0"] != spec["grid"]["t0"] or g["spb"] != spec["grid"]["spb"]
                or g.get("holds") != spec["grid"].get("holds") or n != nb):
            errs.append("the compiled grid is not the analysis' grid")

    def layer_checks(L, what, span):
        if L["fx"] not in FX:
            errs.append("%s: no fx %s" % (what, L["fx"]))
        if L["mix"] not in MIX:
            errs.append("%s: no mix %s" % (what, L["mix"]))
        if L["pal"] not in spec["pal"]:
            errs.append("%s: no palette %s" % (what, L["pal"]))
        try:
            m = _region_mask(h, L["on"])
        except TreatmentError as e:
            errs.append("%s: %s" % (what, e))
            return
        if not m.any():
            errs.append("%s: region %s has no LEDs" % (what, L["on"]))
        shell = bool((m & h.shell).any())
        for k in ("axis", "axis2"):
            if k in L and L[k] not in AXES:
...
</persisted-output>
```

```
$ cd "~/deadmau5 app"; grep -n "class Helmet" -A 120 mau5engine.py | sed -n 1,220p
41:class Helmet:
42-    """The map, as arrays, plus the masks presets actually ask for."""
43-
44-    def __init__(self, path=None):
45-        rows = mau5map.load(path) if path else mau5map.load()
46-        self.n = len(rows)
47-        self.rows = rows
48-        self.xyz = np.array([[r["x"], r["y"], r["z"]] for r in rows], float)
49-        self.az = np.array([r["az_deg"] for r in rows], float)
50-        self.el = np.array([r["elev_deg"] for r in rows], float)
51-        self.u = np.array([r["u"] for r in rows], float)
52-        self.group = np.array([r["group"] for r in rows], int)
53-        self.region = np.array([r["region"] for r in rows], dtype=object)
54-        self.shell = self.region == "shell"
55-        self.ear1 = np.array([r.startswith("ear1") for r in self.region])
56-        self.ear2 = np.array([r.startswith("ear2") for r in self.region])
57-        self.ears = self.ear1 | self.ear2
58-        self.tubes = np.array([r.endswith("tubes") for r in self.region])
59-        self.rims = np.array([r.endswith("rim") for r in self.region])
60-        # Each ear is three tubes, numbered 0 (lowest) to 2 on both, and
61-        # `along` is how far up its tube an LED sits, 0 to 1 -- for a rim
62-        # LED, how far round from the bottom.  The strip runs up each
63-        # tube and back down, so both rows share a height.  -1 on the
64-        # shell.  This is what lets an ear be lit as blades rather than
65-        # as one blob.
66-        self.tube = np.array([r.get("tube", -1) for r in rows], int)
67-        self.along = np.array([r.get("along", -1.0) for r in rows], float)
68-
69-        # normalised 0..1 helpers, computed per part so an effect that
70-        # sweeps "left to right" does so across the whole helmet
71-        # Orthographic screen c
... [cut] ...
sarray(v, float), h.shape)
149-    i = np.floor(h * 6.0).astype(int)
150-    f = h * 6.0 - i
151-    p, q, t = v * (1 - s), v * (1 - f * s), v * (1 - (1 - f) * s)
152-    i = i % 6
153-    r = np.choose(i, [v, q, p, p, t, v])
154-    g = np.choose(i, [t, v, v, q, p, p])
155-    b = np.choose(i, [p, p, t, v, v, q])
156-    return np.stack([r, g, b], -1) * 255.0
157-
158-
159-# ----------------------------------------------------------------------
160-# Parameters something is divided by, or that count something.  At zero
161-# a preset raised ZeroDivisionError here and painted NaN on the phone,
```

```
$ cd "~/deadmau5 app"; grep -n "SPRITES\|class Sprite\|class Eyes\|class TextScroll\|def _text_bitmap\|REGISTRY\[" mau5fx.py mau5engine.py | head -40; grep -n "class Sprite" -A 90 mau5fx.py | sed -n 1,160p
mau5fx.py:134:SPRITES = {
mau5fx.py:266:                SPRITES[name] = list(rows)
mau5fx.py:275:    rows = SPRITES[name_or_rows] if isinstance(name_or_rows, str) else name_or_rows
mau5fx.py:567:class Sprite(GridEffect):
mau5fx.py:584:class SpriteFlipbook(GridEffect):
mau5fx.py:989:    for name in sorted(SPRITES):
mau5engine.py:35:from mau5fx import FONT5x7, SPRITES
mau5engine.py:580:def _text_bitmap(text, spacing=1):
mau5engine.py:625:    rows = SPRITES[name]
mau5engine.py:674:class TextScroll(Preset):
mau5engine.py:704:class SpriteShow(Preset):
mau5engine.py:743:class Eyes(Preset):
mau5engine.py:1048:                       **REGISTRY[self.p["shell"]].accepts(
mau5engine.py:1051:                       **REGISTRY[self.p["ears"]].accepts(
mau5engine.py:1278:    REGISTRY[_c.name] = _c
mau5engine.py:1334:    v = params.get(key, REGISTRY[name].params.get(key))
mau5engine.py:1371:    return REGISTRY[name](**kw)
mau5engine.py:1384:        p = REGISTRY[nm]()
567:class Sprite(GridEffect):
568-    """A static face, optionally blinking on the beat."""
569-
570-    def __init__(self, helmet, sprite="x_eyes", col=None, row_from_top=3,
571-                 color=(255, 40, 0), **kw):
572-        super().__init__(helmet, color=color, **kw)
573-        self.bmp = sprite_bitmap(sprite)
574-        # faces sit on the front of the head: azimuth 0 is channel 0
575-        self.col = -int(round((self.bmp.shape[1] - 1) / 2.0)) if col is None else col
576-        self.row = row_from_top
577-
578-    def render(self, buf, i, t):
579-        self.clear()
580-        self.blit(self.bmp, self.col, self.row)
581-        self.flush(buf, self.level(t))
582-
583-
584:class SpriteFlipbook(GridEffect):
585-    """Cycle a list of sprites -- one per beat, or at a fixed rate."""
586-
587-    def __init__(
... [cut] ...
__(helmet, **kw)
662-        self.color, self.period, self.width, self.dir = color, period, width_deg, direction
663-        self.az = helmet.az
664-        self.idx = np.arange(helmet.n_shell)
665-
666-    def render(self, buf, i, t):
667-        centre = (self.dir * 360.0 * self.phase(t, self.period)) % 360.0
668-        d = np.abs((self.az - centre + 180.0) % 360.0 - 180.0)
669-        v = np.clip(1.0 - d / self.width, 0, 1) ** 2
670-        _paint(buf, self.idx, v, self.color, self.level(t))
671-
672-
673-class ElevationPulse(Effect):
674-    """A ring rising or falling over the sphere."""
```

```
$ cd "~/deadmau5 app"; grep -n "class Helmet" -A 120 mau5engine.py | sed -n 1,220p
41:class Helmet:
42-    """The map, as arrays, plus the masks presets actually ask for."""
43-
44-    def __init__(self, path=None):
45-        rows = mau5map.load(path) if path else mau5map.load()
46-        self.n = len(rows)
47-        self.rows = rows
48-        self.xyz = np.array([[r["x"], r["y"], r["z"]] for r in rows], float)
49-        self.az = np.array([r["az_deg"] for r in rows], float)
50-        self.el = np.array([r["elev_deg"] for r in rows], float)
51-        self.u = np.array([r["u"] for r in rows], float)
52-        self.group = np.array([r["group"] for r in rows], int)
53-        self.region = np.array([r["region"] for r in rows], dtype=object)
54-        self.shell = self.region == "shell"
55-        self.ear1 = np.array([r.startswith("ear1") for r in self.region])
56-        self.ear2 = np.array([r.startswith("ear2") for r in self.region])
57-        self.ears = self.ear1 | self.ear2
58-        self.tubes = np.array([r.endswith("tubes") for r in self.region])
59-        self.rims = np.array([r.endswith("rim") for r in self.region])
60-        # Each ear is three tubes, numbered 0 (lowest) to 2 on both, and
61-        # `along` is how far up its tube an LED sits, 0 to 1 -- for a rim
62-        # LED, how far round from the bottom.  The strip runs up each
63-        # tube and back down, so both rows share a height.  -1 on the
64-        # shell.  This is what lets an ear be lit as blades rather than
65-        # as one blob.
66-        self.tube = np.array([r.get("tube", -1) for r in rows], int)
67-        self.along = np.array([r.get("along", -1.0) for r in rows], float)
68-
69-        # normalised 0..1 helpers, computed per part so an effect that
70-        # sweeps "left to right" does so across the whole helmet
71-        # Orthographic screen c
... [cut] ...
sarray(v, float), h.shape)
149-    i = np.floor(h * 6.0).astype(int)
150-    f = h * 6.0 - i
151-    p, q, t = v * (1 - s), v * (1 - f * s), v * (1 - (1 - f) * s)
152-    i = i % 6
153-    r = np.choose(i, [v, q, p, p, t, v])
154-    g = np.choose(i, [t, v, v, q, p, p])
155-    b = np.choose(i, [p, p, t, v, v, q])
156-    return np.stack([r, g, b], -1) * 255.0
157-
158-
159-# ----------------------------------------------------------------------
160-# Parameters something is divided by, or that count something.  At zero
161-# a preset raised ZeroDivisionError here and painted NaN on the phone,
```

```
$ cd "~/deadmau5 app"; grep -n "SPRITES\|class Sprite\|class Eyes\|class TextScroll\|def _text_bitmap\|REGISTRY\[" mau5fx.py mau5engine.py | head -40; grep -n "class Sprite" -A 90 mau5fx.py | sed -n 1,160p
mau5fx.py:134:SPRITES = {
mau5fx.py:266:                SPRITES[name] = list(rows)
mau5fx.py:275:    rows = SPRITES[name_or_rows] if isinstance(name_or_rows, str) else name_or_rows
mau5fx.py:567:class Sprite(GridEffect):
mau5fx.py:584:class SpriteFlipbook(GridEffect):
mau5fx.py:989:    for name in sorted(SPRITES):
mau5engine.py:35:from mau5fx import FONT5x7, SPRITES
mau5engine.py:580:def _text_bitmap(text, spacing=1):
mau5engine.py:625:    rows = SPRITES[name]
mau5engine.py:674:class TextScroll(Preset):
mau5engine.py:704:class SpriteShow(Preset):
mau5engine.py:743:class Eyes(Preset):
mau5engine.py:1048:                       **REGISTRY[self.p["shell"]].accepts(
mau5engine.py:1051:                       **REGISTRY[self.p["ears"]].accepts(
mau5engine.py:1278:    REGISTRY[_c.name] = _c
mau5engine.py:1334:    v = params.get(key, REGISTRY[name].params.get(key))
mau5engine.py:1371:    return REGISTRY[name](**kw)
mau5engine.py:1384:        p = REGISTRY[nm]()
567:class Sprite(GridEffect):
568-    """A static face, optionally blinking on the beat."""
569-
570-    def __init__(self, helmet, sprite="x_eyes", col=None, row_from_top=3,
571-                 color=(255, 40, 0), **kw):
572-        super().__init__(helmet, color=color, **kw)
573-        self.bmp = sprite_bitmap(sprite)
574-        # faces sit on the front of the head: azimuth 0 is channel 0
575-        self.col = -int(round((self.bmp.shape[1] - 1) / 2.0)) if col is None else col
576-        self.row = row_from_top
577-
578-    def render(self, buf, i, t):
579-        self.clear()
580-        self.blit(self.bmp, self.col, self.row)
581-        self.flush(buf, self.level(t))
582-
583-
584:class SpriteFlipbook(GridEffect):
585-    """Cycle a list of sprites -- one per beat, or at a fixed rate."""
586-
587-    def __init__(
... [cut] ...
__(helmet, **kw)
662-        self.color, self.period, self.width, self.dir = color, period, width_deg, direction
663-        self.az = helmet.az
664-        self.idx = np.arange(helmet.n_shell)
665-
666-    def render(self, buf, i, t):
667-        centre = (self.dir * 360.0 * self.phase(t, self.period)) % 360.0
668-        d = np.abs((self.az - centre + 180.0) % 360.0 - 180.0)
669-        v = np.clip(1.0 - d / self.width, 0, 1) ** 2
670-        _paint(buf, self.idx, v, self.color, self.level(t))
671-
672-
673-class ElevationPulse(Effect):
674-    """A ring rising or falling over the sphere."""
```

```
$ cd "~/deadmau5 app"; sed -n 575,800p mau5engine.py; sed -n 255,300p mau5fx.py
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
    "6": ("###", "#  ", "###", "# #", "###"),
    "7": ("###", "  #", "  #", "  #", "  #"),
    "8": ("###", "# #", "###", "# #", "###"),
    "9": ("###", "# #", "###", "  #", "###"),
}


def _digit_bitmap(ch):
    rows = DIGIT3x5.get(ch, DIGIT3x5["0"])
    return np.array([[c != " " for c in r] for r in rows], bool)


def _glyph_bitmap(ch):
    """One 5x7 character as a (7, 5) bool array."""
    g = FONT5x7.get(ch.upper(
... [cut] ...
ist.  No live audio analysis -- shows are authored."""

    def __init__(self, times):
        self.times = np.asarray(sorted(float(t) for t in times), float)

    @classmethod
    def from_bpm(cls, bpm, offset=0.0, duration=600.0):
        step = 60.0 / float(bpm)
        n = int(duration / step) + 1
        return cls(offset + step * np.arange(n))

    @classmethod
    def from_file(cls, path):
        """One time in seconds per line, or a JSON list, or librosa output."""
        with open(path, "r", encoding="utf-8") as fh:
            txt = fh.read().strip()
        if txt.startswith("["):
```

```
$ cd "~/deadmau5 app"; python3 - <<'EOF'
import numpy as np, mau5engine as E
h=E.Helmet()
print(h.n, h.shell.sum(), h.ear1.sum(), h.ear2.sum(), h.rims.sum(), h.tubes.sum())
for name,m in (("shell",h.shell),("ear1",h.ear1),("ear2",h.ear2),("rim1",h.rims&h.ear1),("rim2",h.rims&h.ear2),("tubes1",h.tubes&h.ear1),("tubes2",h.tubes&h.ear2)):
    print(name,m.sum(),"x %.0f..%.0f y %.0f..%.0f"%(h.px[m].min(),h.px[m].max(),h.py[m].min(),h.py[m].max()),"centre %.0f %.0f"%(h.px[m].mean(),h.py[m].mean()))
# shell map as ascii, 17 x 17 cells
m=h.shell
xs=h.px[m]; ys=h.py[m]
gx=np.linspace(-171,171,35); gy=np.linspace(-108,172,29)
H,_,_=np.histogram2d(ys,xs,bins=[gy,gx])
for r in H[::-1]:
    pri ... [cut]
621 398 112 111 37 186
shell 398 x -171..171 y -111..168 centre -0 57
ear1 112 x -388..-56 y 52..384 centre -222 215
ear2 111 x 56..387 y 55..385 centre 225 216
rim1 18 x -388..-56 y 52..384 centre -232 233
rim2 19 x 56..387 y 55..385 centre 236 227
tubes1 94 x -349..-87 y 67..349 centre -220 212
tubes2 92 x 83..358 y 70..349 centre 223 213
...........1...1.2................
.........2211.111.1111121.........
........311.111.1.11.11112........
......2322112111111112112232......
.....3311.11111111111111.1133.....
....3311.1111.111111.1111.1133....
...32211111111.1111.11111111223...
..................................
..32211111.1111.11.1111.11111223..
.3211111111.111.11.111.1111111123.
..................................
13211111.111.11.11.11.111.11111231
32111111..................11111123
..................................
411............................114
1................................1
..................................
..................................
..................................
1................................1
3................................3
..................................
22..............................22
..................................
.321..........................123.
.13211......................11231.
..1.1.2....................21.11..
..1211.1..................1..211..
ear1 tube 0 30 x -349..-201 y 67..216
ear2 tube 0 28 x 207..358 y 70..214
ear1 tube 1 36 x -310..-130 y 128..303
ear2 tube 1 36 x 133..322 y 127..306
ear1 tube 2 28 x -237..-87 y 215..349
ear2 tube 2 28 x 83..237 y 205..349
shell centre -0.34484924623115576 56.5637688442211 er max 1.0
```

```
$ cd "~/deadmau5 app"; sed -n 575,800p mau5engine.py; sed -n 255,300p mau5fx.py
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
    "6": ("###", "#  ", "###", "# #", "###"),
    "7": ("###", "  #", "  #", "  #", "  #"),
    "8": ("###", "# #", "###", "# #", "###"),
    "9": ("###", "# #", "###", "  #", "###"),
}


def _digit_bitmap(ch):
    rows = DIGIT3x5.get(ch, DIGIT3x5["0"])
    return np.array([[c != " " for c in r] for r in rows], bool)


def _glyph_bitmap(ch):
    """One 5x7 character as a (7, 5) bool array."""
    g = FONT5x7.get(ch.upper(
... [cut] ...
ist.  No live audio analysis -- shows are authored."""

    def __init__(self, times):
        self.times = np.asarray(sorted(float(t) for t in times), float)

    @classmethod
    def from_bpm(cls, bpm, offset=0.0, duration=600.0):
        step = 60.0 / float(bpm)
        n = int(duration / step) + 1
        return cls(offset + step * np.arange(n))

    @classmethod
    def from_file(cls, path):
        """One time in seconds per line, or a JSON list, or librosa output."""
        with open(path, "r", encoding="utf-8") as fh:
            txt = fh.read().strip()
        if txt.startswith("["):
```

```
$ cd "~/deadmau5 app"; python3 - <<'EOF'
import numpy as np, mau5engine as E
h=E.Helmet()
print(h.n, h.shell.sum(), h.ear1.sum(), h.ear2.sum(), h.rims.sum(), h.tubes.sum())
for name,m in (("shell",h.shell),("ear1",h.ear1),("ear2",h.ear2),("rim1",h.rims&h.ear1),("rim2",h.rims&h.ear2),("tubes1",h.tubes&h.ear1),("tubes2",h.tubes&h.ear2)):
    print(name,m.sum(),"x %.0f..%.0f y %.0f..%.0f"%(h.px[m].min(),h.px[m].max(),h.py[m].min(),h.py[m].max()),"centre %.0f %.0f"%(h.px[m].mean(),h.py[m].mean()))
# shell map as ascii, 17 x 17 cells
m=h.shell
xs=h.px[m]; ys=h.py[m]
gx=np.linspace(-171,171,35); gy=np.linspace(-108,172,29)
H,_,_=np.histogram2d(ys,xs,bins=[gy,gx])
for r in H[::-1]:
    pri ... [cut]
621 398 112 111 37 186
shell 398 x -171..171 y -111..168 centre -0 57
ear1 112 x -388..-56 y 52..384 centre -222 215
ear2 111 x 56..387 y 55..385 centre 225 216
rim1 18 x -388..-56 y 52..384 centre -232 233
rim2 19 x 56..387 y 55..385 centre 236 227
tubes1 94 x -349..-87 y 67..349 centre -220 212
tubes2 92 x 83..358 y 70..349 centre 223 213
...........1...1.2................
.........2211.111.1111121.........
........311.111.1.11.11112........
......2322112111111112112232......
.....3311.11111111111111.1133.....
....3311.1111.111111.1111.1133....
...32211111111.1111.11111111223...
..................................
..32211111.1111.11.1111.11111223..
.3211111111.111.11.111.1111111123.
..................................
13211111.111.11.11.11.111.11111231
32111111..................11111123
..................................
411............................114
1................................1
..................................
..................................
..................................
1................................1
3................................3
..................................
22..............................22
..................................
.321..........................123.
.13211......................11231.
..1.1.2....................21.11..
..1211.1..................1..211..
ear1 tube 0 30 x -349..-201 y 67..216
ear2 tube 0 28 x 207..358 y 70..214
ear1 tube 1 36 x -310..-130 y 128..303
ear2 tube 1 36 x 133..322 y 127..306
ear1 tube 2 28 x -237..-87 y 215..349
ear2 tube 2 28 x 83..237 y 205..349
shell centre -0.34484924623115576 56.5637688442211 er max 1.0
```

```
$ cd "~/deadmau5 app"; KIT=tools/showkit; W="$KIT/work/cinema"; B="deadmau5 - Strobe (Special Features Remix)"; python3 "$KIT/spectro.py" "$B" "$W/s0.png" 0 34; python3 "$KIT/spectro.py" "$B" "$W/s1.png" 30 66; cat > "$W/layout.py" <<'EOF'
import sys,os
sys.path.insert(0,os.getcwd())
import numpy as np, mau5engine as E, mau5preview as PV
h=E.Helmet(); sc=PV.Scene(h)
f=np.zeros((h.n,3))
f[h.rims]=(255,0,0)
for t,c in ((0,(0,255,0)),(1,(60,60,255)),(2,(255,255,0))):
    f[h.tube==t]=c
s=h.shell
f[s]=np.stack([h.nfa[s]*255, 40+0*h.nfa[s], h.nel[s]*255],1)
im=sc.frame(f)
im.save(sys.argv[1]); print(i ... [cut]
tools/showkit/songs/cinema/s0.png
tools/showkit/songs/cinema/s1.png
(760, 620)
```

```
$ cd "~/deadmau5 app"; KIT=tools/showkit; W="$KIT/work/cinema"; B="deadmau5 - Strobe (Special Features Remix)"; python3 "$KIT/spectro.py" "$B" "$W/s2.png" 62 100; python3 "$KIT/spectro.py" "$B" "$W/s3.png" 94 146; python3 "$KIT/spectro.py" "$B" "$W/s4.png" 142 180; python3 "$KIT/spectro.py" "$B" "$W/s5.png" 174 210
tools/showkit/songs/cinema/s2.png
tools/showkit/songs/cinema/s3.png
tools/showkit/songs/cinema/s4.png
tools/showkit/songs/cinema/s5.png
```

```
$ cd "~/deadmau5 app"; KIT=tools/showkit; W="$KIT/work/cinema"; cat > "$W/peek.py" <<'EOF'
import sys,os
KIT=sys.argv[1]; sys.path.insert(0,KIT); sys.path.insert(0,os.getcwd())
import numpy as np, grid
d=grid.env_of("shows/deadmau5 - Strobe (Special Features Remix).mp3")
spb=0.46875; t0=0.136
tt=d["tt"]
CH=" .:-=+*#%@"
def line(nm,b0,b1,norm=None):
    v=d[nm]; 
    vmax=np.percentile(v,99.5)
    vmin=np.percentile(v,5)
    s=""
    for k in range(int(b0*16),int(b1*16)):
        a=t0+k*spb/4; c=a+spb/4
        i,j=np.searchsorted(tt,[a,c])
        x=(v[i:max(j,i+1)].mean()-vmin)/(vmax-vmin)
      ... [cut]
Exit code 1
bars 0.0 3.0
  sub    :.  :.  ::  :.  |::  ::  :.  ::  |::  :.  ::  :.  |
  bass   -.::-:---.::-:--|-.::-:---.::-:--|-.::-:---.::-:--|
  lowmid .  ::.::. .::.--|. .-::--. :-::=-|. :-::==. :-::==|
  mid            .   .   |                |                |
  pres   =---=--==---=-::|-...:   :   .   |:   .   .   :   |
  air    ***+*+++++==+=--|=:::=.  -   -   |-   -   -   -   |
bars 7.0 10.0
  sub    ::  ::  :.  ::  |::  :.  ::  :.  |:.  ::  :.  ::  |
  bass   -..:-:---..:-:--|-..:-:---..:-:--|-..:-:--:..:-:--|
  lowmid ::=+--**::++-=**|::+*-=**::+*-=**|::+*-=**-:+*-=**|
  mid               .. ..|:.:-. .:. .:.  .|   .       .    |
  pres   .   .   : .:-:--|=--=-..::  .:   |.   :   :   .   |
  air    -   -   -..:=:--|=.::-   -   -   |-   -   -   -   |
bars 13.0 18.0
  sub    :.  ::  :.  ::  |::  :.  ::  :.  |      ..::::::::|-.  :.  ::  ::  |::  ::  :.  ::  |
  bass   -..:-:--:..:-:--|-..:-:---..:-:--| ..:..--.:-:.::.|-.:::...-..:-.::|: ..-.::-...-.::|
  lowmid ::+*--**-:+*--**|-:++-=**::++--+*|.:++:=*+:-++.=+=|:.=+--*+:.*+=:=*|--**=:*=: ===:=:|
  mid    ..:-..:-::-=::--|::-=..--::-=:.--| :-=..--.:== :=+|=.+*+:=+-:+**-=+|--+**-**=-+**-+*|
  pres   .   :   :  .:..:|=--==-==+===+===|---::::......   |=--=#==++++*#+++|+==+#===+==*#=-=|
  air    -   -   -   -  .|=..:=::-=---+-==|=++++++++++++=-.|#**#%**+++*%%=-=|=--=%-::=.=##:..|
bars 22.0 26.0
  sub    ::  :.  ::  ::  |:.  ::          |::  :.  ::  ::  |::  ::  :.  ::  |
  bass   :...-.:--.-:-.  |- .:-.::  ..:.::|-   -..:-...:...|- ..:.:::.::-.--|
  lowmid -.==-:-=-.=+-:+-|: ---.=-::==-:==|: +*-.==: ==-:+=|-:+=-.==:.++-:=-|
  mid    =-**+-**--+**-+*|=-*#*-**-:+**-*#|=-##+-**=:+**-**|=:+**-+*=:**+-*+|
  pres   : :-#::-:.-+#---|:.:-#---..=*#===|=-++#-==-.=*#-==|:.==#-==-:=*#-==|
  air    -  :#:  - =#%: .|-  :%:   .=%#
... [cut] ...
-*#--:|-..-#-::-::+#-::|-..-#-:.-.:+#:.:|
  air    -  :%: .- =#%: .|-  :#:    =%#: .|-  :%:  - =#%: .|-  :#:  - =%#:  |
bars 204.0 210.0
Traceback (most recent call last):
  File "tools/showkit/songs/cinema/peek.py", line 24, in <module>
    print("  %-6s %s"%(nm,line(nm,a,b)))
  File "tools/showkit/songs/cinema/peek.py", line 17, in line
    s+=CH[int(np.clip(x,0,0.999)*10)]
ValueError: cannot convert float NaN to integer
```

```
$ cd "~/deadmau5 app"; KIT=tools/showkit; W="$KIT/work/cinema"; sed -i '' 's/for nm in ("sub","bass","lowmid","mid","pres","air"):/for nm in ("sub","mid","air"):/' "$W/peek.py"; python3 "$W/peek.py" "$KIT" 70-73 78-81 86-89 94-98 103-105 111-113 127-129 135-137 140-145 2>&1; python3 "$W/peek.py" "$KIT" 204-209 2>&1 | head -5
bars 70.0 73.0
  sub    #@%%%@**#%**#%++|#%==#@++:-=-    |#%==#%%%%@%##%**|
  mid    ==*#*=#*++##*+**|++*#****==*#**##|++*#*+##++*#*+*#|
  air    *+*##+*#+*#%%***|**##%*#**#%@@%@@|**##%*##**#%%*##|
bars 78.0 81.0
  sub    #%**%%*+#@**%@==|-=+=....       :|#%++#%%@%@%%#%**|
  mid    =+*#*=#*++##*+**|++*#****==*#**#*|+*##**##++*#**##|
  air    *+*##*##**#%%*##|*###%#####%@@@@@|###%%######%%###|
bars 86.0 89.0
  sub    %@%%%@++#@++%@**|-=++:::.       -|#%++#%*+#%++#@##|
  mid    ++*#*+#*++###*##|++######=+#%##%#|+*##**##++##***#|
  air    ***#%*##**#%%*##|**##%###**#%%#**|#*##%*##**#%%*%#|
bars 94.0 98.0
  sub    =*##+***-=++..:.|             .=*|++=-=------:-::.|.:...:...       |
  mid    ++*#*+#*+*###*##|**#%##%#+*##*###|++++====::--:-=-|-=---===-==-===-|
  air    **##%*##**#%%*##|*###%#####%@@@@@|**###**+++=====-|---::::.....    |
bars 103.0 105.0
  sub                    |======+**+*+====|
  mid    -============+*+|*++***++++++++++|
  air    :-:-----===+++=+|===+============|
bars 111.0 113.0
  sub    ================|**==+=+****+++==|
  mid    ########**#**###|####%#***#*####*|
  air    +*+***********++|#*##%#***+*%%+==|
bars 127.0 129.0
  sub    +===++==**==+===|::::::::::::::::|
  mid    ****#***++**##**|#*+*#**+%*+*#***|
  air    ####%#####%@@@@@|%**#%#**%+++%++=|
bars 135.0 137.0
  sub    ::::::::::::::::|::::::::::::::::|
  mid    ##**##**##**##**|##*###**%#**##**|
  air    %=:+%===%**#@%@@|@*+%%*%+%%++@+%=|
bars 140.0 145.0
  sub    ::::::..........|                |                |         .:-..  |#%==#%#*%%**#%**|
  mid    %###%%%#%#%%%%%#|%###%%%#@%%%%%%%|@%%%@@%%@%#%@%%#|%%%%@%%%%%%%%#*+|**#*++##++**++*#|
  air    @=%%%%#-@=%%%%%%|@=%%%%%-@+%%%%%%|@%%%@%%%@%%%@%%%|@%%%@%%@@@@@@*-:|**##**##**#%**##|
bars 204.0 209.0
  sub    ::  ::-+--++----|-----:-:-:::::::|-:::::. ::  ::  |::  ::          |                |
  mid    =:-+*:::---=*--:|-::=*----::=+:--|=-:=*-::---=*-:-|-::=+:::...-+::-|:  ..           |
  air    -  :%:  - =#%: .|-  :#:  - =%#: .|-..-%-:-=-+%%===|+++*%++++++*%+-:|-.              |
```

```
$ cd "~/deadmau5 app"; grep -n "sweep" remote/offline/show.js | head -20; grep -n "soft" remote/offline/show.js | head; sed -n 1,40p shows/scenes/deadmau5\ -\ Strobe.scene.json | cut -c1-200 | tail -25
284:  sweep: ['speed', 'width', 'soft', 'cgrad', 'from', 'to'],
446:    } else if (L.fx === 'sweep') {
546:      case 'sweep': {
284:  sweep: ['speed', 'width', 'soft', 'cgrad', 'from', 'to'],
288:  orb: ['x', 'y', 'rad', 'soft', 'wx', 'wy', 'xf', 'yf', 'xp', 'yp', 'cgrad'],
557:        const soft = valAt(P.soft, p, bar, music, tt);
565:          else k = sclamp(0.5 - d / soft, 0, 1);
654:        const rad = valAt(P.rad, p, bar, music, tt), soft = valAt(P.soft, p, bar, music, tt);
660:          const e = sclamp((rad - d) / soft, 0, 1);
  "pure": [[0, 0, 255], [0, 200, 255], [255, 255, 255]]
 },
 "motifs": {
  "arp": {"fx": "sparks", "on": "face", "rate": 2, "life": 1.5, "loop": 16, "seed": 3,
          "pal": "ice", "c": 0.75, "spread": 0.2, "gain": 0.6},
  "spin": {"fx": "grad", "on": "rims", "axis": "a", "scale": 4, "speed": 0.25, "gain": 0.25},
  "ladder": {"fx": "blades", "seq": ["012"], "step": 1, "side": "alt", "rise": 0.12,
             "keep": 0.15, "c": 0.6, "ctip": 1},
  "ring": {"fx": "sweep", "on": "all", "axis": "r", "shape": "p", "mode": "band",
           "from": 0, "to": 1.2, "width": 0.25, "pal": "pure", "c": 0}
 },
 "scenes": [
  {"name": "arp", "from": -1, "to": "call", "pal": "ice",
   "layers": [{"use": "arp", "env": {"in": 8}},
              {"use": "spin"}]},

  {"name": "call", "from": "call", "to": "climb", "pal": "ice",
   "layers": [{"use": "arp", "rate": {"call": 2, "24": 4}},
              {"fx": "grad", "on": "shell", "axis": "y", "speed": 0.03125, "hi": 0.5, "gain": 0.3},
              {"fx": "blades", "seq": ["012"], "step": 4, "side": "alt", "keep": 0, "c": 0.66,
               "gain": {"band": "bass", "punch": true, "lo": 0, "hi": 1}},
              {"use": "spin"}]},

  {"name": "climb", "from": "climb", "to": "bloom1", "pal": "ice",
   "layers": [{"fx": "sweep", "on": "shell", "axis": "y", "shape": "p", "mode": "fill",
```

```
$ cd "~/deadmau5 app"; KIT=tools/showkit; W="$KIT/work/cinema"; sed -i '' 's/for nm in ("sub","bass","lowmid","mid","pres","air"):/for nm in ("sub","mid","air"):/' "$W/peek.py"; python3 "$W/peek.py" "$KIT" 70-73 78-81 86-89 94-98 103-105 111-113 127-129 135-137 140-145 2>&1; python3 "$W/peek.py" "$KIT" 204-209 2>&1 | head -5
bars 70.0 73.0
  sub    #@%%%@**#%**#%++|#%==#@++:-=-    |#%==#%%%%@%##%**|
  mid    ==*#*=#*++##*+**|++*#****==*#**##|++*#*+##++*#*+*#|
  air    *+*##+*#+*#%%***|**##%*#**#%@@%@@|**##%*##**#%%*##|
bars 78.0 81.0
  sub    #%**%%*+#@**%@==|-=+=....       :|#%++#%%@%@%%#%**|
  mid    =+*#*=#*++##*+**|++*#****==*#**#*|+*##**##++*#**##|
  air    *+*##*##**#%%*##|*###%#####%@@@@@|###%%######%%###|
bars 86.0 89.0
  sub    %@%%%@++#@++%@**|-=++:::.       -|#%++#%*+#%++#@##|
  mid    ++*#*+#*++###*##|++######=+#%##%#|+*##**##++##***#|
  air    ***#%*##**#%%*##|**##%###**#%%#**|#*##%*##**#%%*%#|
bars 94.0 98.0
  sub    =*##+***-=++..:.|             .=*|++=-=------:-::.|.:...:...       |
  mid    ++*#*+#*+*###*##|**#%##%#+*##*###|++++====::--:-=-|-=---===-==-===-|
  air    **##%*##**#%%*##|*###%#####%@@@@@|**###**+++=====-|---::::.....    |
bars 103.0 105.0
  sub                    |======+**+*+====|
  mid    -============+*+|*++***++++++++++|
  air    :-:-----===+++=+|===+============|
bars 111.0 113.0
  sub    ================|**==+=+****+++==|
  mid    ########**#**###|####%#***#*####*|
  air    +*+***********++|#*##%#***+*%%+==|
bars 127.0 129.0
  sub    +===++==**==+===|::::::::::::::::|
  mid    ****#***++**##**|#*+*#**+%*+*#***|
  air    ####%#####%@@@@@|%**#%#**%+++%++=|
bars 135.0 137.0
  sub    ::::::::::::::::|::::::::::::::::|
  mid    ##**##**##**##**|##*###**%#**##**|
  air    %=:+%===%**#@%@@|@*+%%*%+%%++@+%=|
bars 140.0 145.0
  sub    ::::::..........|                |                |         .:-..  |#%==#%#*%%**#%**|
  mid    %###%%%#%#%%%%%#|%###%%%#@%%%%%%%|@%%%@@%%@%#%@%%#|%%%%@%%%%%%%%#*+|**#*++##++**++*#|
  air    @=%%%%#-@=%%%%%%|@=%%%%%-@+%%%%%%|@%%%@%%%@%%%@%%%|@%%%@%%@@@@@@*-:|**##**##**#%**##|
bars 204.0 209.0
  sub    ::  ::-+--++----|-----:-:-:::::::|-:::::. ::  ::  |::  ::          |                |
  mid    =:-+*:::---=*--:|-::=*----::=+:--|=-:=*-::---=*-:-|-::=+:::...-+::-|:  ..           |
  air    -  :%:  - =#%: .|-  :#:  - =%#: .|-..-%-:-=-+%%===|+++*%++++++*%+-:|-.              |
```

```
$ cd "~/deadmau5 app"; grep -n "sweep" remote/offline/show.js | head -20; grep -n "soft" remote/offline/show.js | head; sed -n 1,40p shows/scenes/deadmau5\ -\ Strobe.scene.json | cut -c1-200 | tail -25
284:  sweep: ['speed', 'width', 'soft', 'cgrad', 'from', 'to'],
446:    } else if (L.fx === 'sweep') {
546:      case 'sweep': {
284:  sweep: ['speed', 'width', 'soft', 'cgrad', 'from', 'to'],
288:  orb: ['x', 'y', 'rad', 'soft', 'wx', 'wy', 'xf', 'yf', 'xp', 'yp', 'cgrad'],
557:        const soft = valAt(P.soft, p, bar, music, tt);
565:          else k = sclamp(0.5 - d / soft, 0, 1);
654:        const rad = valAt(P.rad, p, bar, music, tt), soft = valAt(P.soft, p, bar, music, tt);
660:          const e = sclamp((rad - d) / soft, 0, 1);
  "pure": [[0, 0, 255], [0, 200, 255], [255, 255, 255]]
 },
 "motifs": {
  "arp": {"fx": "sparks", "on": "face", "rate": 2, "life": 1.5, "loop": 16, "seed": 3,
          "pal": "ice", "c": 0.75, "spread": 0.2, "gain": 0.6},
  "spin": {"fx": "grad", "on": "rims", "axis": "a", "scale": 4, "speed": 0.25, "gain": 0.25},
  "ladder": {"fx": "blades", "seq": ["012"], "step": 1, "side": "alt", "rise": 0.12,
             "keep": 0.15, "c": 0.6, "ctip": 1},
  "ring": {"fx": "sweep", "on": "all", "axis": "r", "shape": "p", "mode": "band",
           "from": 0, "to": 1.2, "width": 0.25, "pal": "pure", "c": 0}
 },
 "scenes": [
  {"name": "arp", "from": -1, "to": "call", "pal": "ice",
   "layers": [{"use": "arp", "env": {"in": 8}},
              {"use": "spin"}]},

  {"name": "call", "from": "call", "to": "climb", "pal": "ice",
   "layers": [{"use": "arp", "rate": {"call": 2, "24": 4}},
              {"fx": "grad", "on": "shell", "axis": "y", "speed": 0.03125, "hi": 0.5, "gain": 0.3},
              {"fx": "blades", "seq": ["012"], "step": 4, "side": "alt", "keep": 0, "c": 0.66,
               "gain": {"band": "bass", "punch": true, "lo": 0, "hi": 1}},
              {"use": "spin"}]},

  {"name": "climb", "from": "climb", "to": "bloom1", "pal": "ice",
   "layers": [{"fx": "sweep", "on": "shell", "axis": "y", "shape": "p", "mode": "fill",
```

```
$ cd "~/deadmau5 app"; KIT=tools/showkit; W="$KIT/work/cinema"; python3 - <<'EOF'
import numpy as np, mau5engine as E
h=E.Helmet()
s=h.shell
c=s&(np.abs(h.px)<60)
y=np.sort(h.py[c])
print(np.round(y).astype(int).tolist())
# LED pitch in the middle band
m=s&(np.abs(h.py-100)<8)
print(np.round(np.sort(h.px[m])).astype(int).tolist())
print("u on shell", h.u[s].min(), h.u[s].max(), "groups", np.unique(h.group[s])[:40])
# the order of the chain on the shell
idx=np.where(s)[0]
print(np.round(h.px[idx[:30]]).astype(int).tolist()); print(np.round(h.py[idx[:30]]).astype(int).tolist())
print("nel at y rows ... [cut]
[-111, -111, -111, -111, -111, -111, 61, 61, 61, 61, 61, 61, 61, 61, 76, 76, 76, 76, 76, 76, 76, 76, 91, 91, 91, 91, 91, 91, 91, 91, 91, 91, 105, 105, 105, 105, 105, 105, 105, 105, 105, 105, 117, 117, 117, 117, 117, 117, 117, 117, 117, 117, 129, 129, 129, 129, 129, 129, 129, 129, 129, 129, 129, 129, 140, 140, 140, 140, 140, 140, 140, 140, 140, 140, 140, 140, 140, 140, 149, 149, 149, 149, 149, 149, 149, 149, 157, 157, 157, 157, 157, 157, 157, 157, 157, 157, 163, 163, 163, 168]
[-138, -136, -134, -131, -126, -120, -114, -106, -97, -88, -78, -67, -56, -44, -32, -19, -6, 6, 19, 32, 44, 56, 67, 78, 88, 97, 106, 114, 120, 126, 131, 134, 137, 138]
u on shell 0.0 1.0 groups [ 0  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17 18 19 20 21 22 23
 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39]
[-169, -164, -159, -151, -142, -132, -131, -141, -150, -157, -163, -167, -170, -164, -160, -155, -147, -139, -129, -126, -135, -144, -151, -156, -145, -138, -130, -121, -116, -125]
[-37, -53, -69, -84, -98, -111, -111, -98, -84, -69, -53, -37, -21, -37, -53, -69, -84, -98, -111, -111, -98, -84, -69, -53, -69, -84, -98, -111, -111, -98]
nel at y rows [(-100, 0.05), (-50, 0.19), (0, 0.38), (30, 0.43), (60, 0.52), (80, 0.57), (100, 0.67), (120, 0.71), (140, 0.81), (160, 0.95)]
nfa at x [(-171, 0.16), (-120, 0.23), (-60, 0.36), (0, 0.49), (60, 0.65), (120, 0.77), (171, 0.84)]
nfa ears 0.0 0.36374357186477674 0.6361240549130386 1.0
er at dome top/ side 0.5205433761808096 0.8268275793986571 0.9947700505019045
```

```
$ cd "~/deadmau5 app"; KIT=tools/showkit; W="$KIT/work/cinema"; cat > "$W/sprites.py" <<'EOF'
import json
P="cinema_"
D={}
# ---- leader digits: bold, 7 wide x 8 tall, on the dome
digits={
"8":["..###..",".##.##.",".##.##.","..###..",".##.##.",".##.##.",".##.##.","..###.."],
"7":[".#####.",".#####.","....##.","...##..","...##..","..##...","..##...","..##..."],
"6":["..###..",".##....",".##....",".####..",".##.##.",".##.##.",".##.##.","..###.."],
"5":[".#####.",".##....",".##....",".####..","....##.","....##.",".##.##.","..###.."],
"4":["...##..","..###..",".#.##..","##.##..","#######","...##.."," ... [cut]
16
tools/showkit/songs/cinema/t1.png (1440, 338)
tools/showkit/songs/cinema/t2.png (1440, 338)
tools/showkit/songs/cinema/t3.png (1440, 338)
```

```
$ date; KIT=tools/showkit; W="$KIT/work/cinema"; cat > "$W/sprites.py" <<'EOF'
import json, sys, os
sys.path.insert(0, os.getcwd())
import numpy as np, mau5engine as E
P="cinema_"
D={}
# ---- leader digits: bold, on the dome.  y_lo 54, y_hi 164, x_half 80: eight rows, six columns
digits={
"8":[".####.","##..##","##..##",".####.",".####.","##..##","##..##",".####."],
"7":["######","######","....##","...##.","...##.","..##..","..##..","..##.."],
"6":[".####.","##....","##....","#####.","##..##","##..##","##..##",".####."],
"5":["######","##....","##....","#####.","....##","....##","##..##",".####."],
"4":[".. ... [cut]
Sat Oct 31 12:48:27 PDT 2026
bulbs 37 canvas 35 43
22
tools/showkit/songs/cinema/t1.png (1440, 338)
tools/showkit/songs/cinema/t1b.png (1440, 338)
tools/showkit/songs/cinema/t2.png (1080, 338)
tools/showkit/songs/cinema/t3.png (1440, 338)
tools/showkit/songs/cinema/t4.png (720, 338)
```

```
$ KIT=tools/showkit; W="$KIT/work/cinema"; cat > "$W/write_treatment.py" <<'EOF'
import sys, os
KIT="tools/showkit"
sys.path.insert(0, KIT)
from fmt import save
SPB=0.46875
BAR=4*SPB
BASE="deadmau5 - Strobe (Special Features Remix)"

def stops(n, table):
    """A palette that is black or flat where it needs to be: `table` is [(pos, rgb), ...]; n even stops."""
    out=[]
    for i in range(n):
        c=i/(n-1)
        for (a,ca),(b,cb) in zip(table,table[1:]):
            if a<=c<=b:
                f=(c-a)/(b-a) if b>a ... [cut]
wrote shows/scenes/deadmau5 - Strobe (Special Features Remix).scene.json scenes 45 hits 30
deadmau5 - Strobe (Special Features Remix): 46 scenes, 30 hits, written into shows/deadmau5 - Strobe (Special Features Remix).json
```

```
$ cd "~/deadmau5 app"; date; KIT=tools/showkit; W="$KIT/work/cinema"; B="deadmau5 - Strobe (Special Features Remix)"; time python3 "$KIT/sheet.py" "$B" "$W/a1.png" 2:ticks 6:lamp 8.1:d8 9.4:d7 12.6:d4 13.3:d3 14.6:d2 15.5:d1 16:START 18:title 20:title 22:title 28:film2 31:swell 32:kick 34:walk 36:walk 38.25:walk 41:walk2 47:climb 47.75:open 48:SLAM 49:iris 49.75:iris 53:black 57:beams 59:beams 61:beams2 63:cue 63.5:cue2 64:DROP 64.25 65:part 68:oz 68.25:snare 2>&1 | tail -42
Sat Oct 31 12:50:53 PDT 2026
bar 2       ticks          shell max  34 mean   0.7   ears max  95 mean   6.3   ticks
bar 6       lamp           shell max  76 mean  14.1   ears max 140 mean  16.4   lamp
bar 8.1     d8             shell max 180 mean  39.8   ears max  45 mean  18.4   leader
bar 9.4     d7             shell max 180 mean  43.1   ears max  46 mean  15.7   leader
bar 12.6    d4             shell max 181 mean  33.0   ears max  46 mean  18.7   leader
bar 13.3    d3             shell max 178 mean  38.2   ears max 110 mean  24.0   leader
bar 14.6    d2             shell max 181 mean  33.3   ears max  46 mean  18.7   leader
bar 15.5    d1             shell max 178 mean  35.9   ears max 178 mean  43.2   one
bar 16      START          shell max 139 mean  35.9   ears max 233 mean 126.7   film · START
bar 18      title          shell max 204 mean  46.8   ears max 140 mean  36.2   film · STROBE
bar 20      title          shell max 204 mean  74.3   ears max 140 mean  36.2   film · STROBE
bar 22      title          shell max 204 mean  58.5   ears max 140 mean  36.2   film · STROBE
bar 28      film2          shell max 148 mean  35.1   ears max 140 mean  36.2   film2
bar 31      swell          shell max 130 mean  35.5   ears max 140 mean  43.0   swell
bar 32      kick           shell max 129 mean  21.7   ears max 255 mean  88.7   walk · KICK IN
bar 34      walk           shell max 130 mean  31.0   ears max 255 mean  24.9   walk
bar 36      walk           shell max 130 mean  28.4   ears max 255 mean  24.9   walk
bar 38.25   walk           shell max 130 mean  32.4   ears max 255 mean  25.0   walk
bar 41      walk2          shell max 130 mean  30.5   ears max 255 mean  24.9   walk2
bar 47      climb          shell max 108 mean  39.6   ears max 178 mean  50.0   climb
bar 47.75   
... [cut] ...
ax 255 mean  76.1   parting · COLOUR
bar 65      part           shell max  76 mean  17.4   ears max 255 mean  21.4   parting
bar 68      oz             shell max  76 mean  19.6   ears max 255 mean  21.4   oz
bar 68.25   snare          shell max  76 mean  19.0   ears max 255 mean  21.4   oz
tools/showkit/songs/cinema/a1.png (1800, 1470)
python3 "$KIT/sheet.py" "$B" "$W/a1.png" 2:ticks 6:lamp 8.1:d8 9.4:d7 12.6:d4  0.56s user 0.03s system 99% cpu 0.596 total
tail -42  0.00s user 0.00s system 0% cpu 0.596 total
```

```
$ cd "~/deadmau5 app"; KIT=tools/showkit; W="$KIT/work/cinema"; B="deadmau5 - Strobe (Special Features Remix)"; python3 "$KIT/sheet.py" "$B" "$W/a2.png" 72:reel2 72.25 74 76.5 79:gap 79.5:cue 80:reel3 80.25 82 83.5 85 87.5:gap 88:reel4 88.25 90 91 93 95.5 96:fall 97 97.75 99:alone 102 104:roll 106 108 110 112:amber 113 116.25 120:blue 122 128:slip 130 2>&1 | tail -32; python3 "$KIT/sheet.py" "$B" "$W/a3.png" 133 136:slip2 138 140:slip3 141 142:run 143 143.5 143.9 144:D2 144.25 146 150 152:b2 154 159.5:gap 160:night2 162 167.5:gap 168:all 170 174 175:strobe 175.5 175.9 176:drain 178 181 184:d2 188 ... [cut]
bar 76.5                   shell max  51 mean  20.9   ears max 255 mean  49.7   berkeley
bar 79      gap            shell max 224 mean   8.6   ears max 153 mean  21.6   change1 · cue
bar 79.5    cue            shell max 245 mean   9.5   ears max 153 mean  33.1   change1 · cue 2
bar 80      reel3          shell max 188 mean  22.7   ears max 199 mean 119.3   night · REEL 3
bar 80.25                  shell max 255 mean  46.7   ears max 184 mean  81.4   night · REEL 3
bar 82                     shell max 188 mean  21.6   ears max 175 mean  42.3   night
bar 83.5                   shell max 188 mean  21.6   ears max 175 mean  42.0   night
bar 85                     shell max 188 mean  21.6   ears max 175 mean  42.3   night
bar 87.5    gap            shell max 230 mean  10.4   ears max 153 mean  21.9   change2 · cue 2
bar 88      reel4          shell max 168 mean  30.2   ears max 255 mean 104.4   strips · REEL 4
bar 88.25                  shell max 216 mean  54.3   ears max 255 mean  64.9   strips · REEL 4
bar 90                     shell max 111 mean  27.7   ears max 255 mean  24.5   strips
bar 91                     shell max 108 mean  26.8   ears max 255 mean  24.5   strips
bar 93                     shell max 116 mean  22.2   ears max 255 mean  24.5   strips
bar 95.5                   shell max 206 mean  10.6   ears max 153 mean  24.9   change3 · cue 2
bar 96      fall           shell max 204 mean  64.8   ears max 255 mean  99.5   fall · LAST COLOUR
bar 97                     shell max  77 mean  29.8   ears max  76 mean  20.6   fall
bar 97.75                  shell max  38 mean   4.7   ears max  38 mean   9.6   fall
bar 99      alone          shell max  99 mean  10.0   ears max  25 mean   1.5   alone
bar 102                    shell max 104 mean  10.1   ears max  25 mean  
... [cut] ...
ean  12.4   ears max 103 mean   8.9   burn
bar 207.9                  shell max 151 mean   6.9   ears max  74 mean   7.2   burn
bar 208     gone           shell max   0 mean   0.0   ears max  63 mean   2.0   tail
bar 208.5                  shell max   0 mean   0.0   ears max  48 mean   1.6   tail
bar 209                    shell max   0 mean   0.0   ears max  32 mean   1.0   tail
bar 209.5                  shell max   0 mean   0.0   ears max  16 mean   0.5   tail
tools/showkit/songs/cinema/a4.png (1800, 735)
```

```
$ cd "~/deadmau5 app"; date; KIT=tools/showkit; W="$KIT/work/cinema"; B="deadmau5 - Strobe (Special Features Remix)"; sed -e 's/cols = 6; W = 300; H = 245/cols = 4; W = 480; H = 390/' "$KIT/sheet.py" > "$W/big.py"; python3 "$W/big.py" "$B" "$W/b1.png" 34 36 37 58 59.3 60.6 61.3 66:oz 68.3:snare 73:petal 82.4:night 83.1:beams 2>&1 | tail -13
Sat Oct 31 12:52:41 PDT 2026
bar 34                     shell max 130 mean  31.0   ears max 255 mean  24.9   walk
bar 36                     shell max 130 mean  28.4   ears max 255 mean  24.9   walk
bar 37                     shell max 130 mean  29.6   ears max 255 mean  24.9   walk
bar 58                     shell max  84 mean   6.2   ears max  57 mean  15.3   beams
bar 59.3                   shell max  68 mean   5.6   ears max  78 mean  21.4   beams
bar 60.6                   shell max  83 mean   6.6   ears max 104 mean  32.8   beams2
bar 61.3                   shell max  88 mean   7.7   ears max 121 mean  37.9   beams2
bar 66      oz             shell max  76 mean  20.0   ears max 255 mean  21.4   oz
bar 68.3    snare          shell max  76 mean  18.9   ears max 255 mean  42.2   oz
bar 73      petal          shell max  51 mean  20.2   ears max 255 mean  46.3   berkeley
bar 82.4    night          shell max 188 mean  20.3   ears max  76 mean  24.4   night
bar 83.1    beams          shell max 188 mean  20.2   ears max  76 mean  29.8   night
tools/showkit/songs/cinema/b1.png (1920, 1170)
```

```
$ cd "~/deadmau5 app"; date; KIT=tools/showkit; W="$KIT/work/cinema"; python3 - <<'EOF'
KIT="tools/showkit"
p=KIT+"/work/cinema/sprites.py"
s=open(p).read()
a=s.index("# ---- the clapper")
b=s.index("# ---- marquee bulbs")
new='''# ---- the clapper: two striped sticks across the dome, the top one hinged at the left.
#      y_lo 54, y_hi 164, x_half 160: eight rows, 24 columns
def stripe(ofs, w=3):
    return "".join("#" if ((i+ofs)//w)%2==0 else "." for i in range(24))
lower=[stripe(0),stripe(1),stripe(2)]
def ... [cut]
Exit code 1
Sat Oct 31 12:53:55 PDT 2026
bulbs 37 canvas 35 43
34
  deadmau5 - Strobe (Special Features Remix).sprites.json: sprite cinema_train1 needs rows of one length
tools/showkit/songs/cinema/t1.png (1080, 338)
  deadmau5 - Strobe (Special Features Remix).sprites.json: sprite cinema_train1 needs rows of one length
tools/showkit/songs/cinema/t2.png (1440, 338)
  deadmau5 - Strobe (Special Features Remix).sprites.json: sprite cinema_train1 needs rows of one length
tools/showkit/songs/cinema/t3.png (1440, 338)
  deadmau5 - Strobe (Special Features Remix).sprites.json: sprite cinema_train1 needs rows of one length
Traceback (most recent call last):
  File "tools/showkit/spritetry.py", line 16, in <module>
    f = np.asarray(E.make("sprite", sprite=nm, color=(255, 170, 40), y_lo=a.y_lo, y_hi=a.y_hi, x_half=a.x_half).render(h, 0.0, None), float)
  File "mau5engine.py", line 724, in render
    bm = _sprite_bitmap(names[at])
  File "mau5engine.py", line 625, in _sprite_bitmap
    rows = SPRITES[name]
KeyError: 'cinema_train1'
  deadmau5 - Strobe (Special Features Remix).sprites.json: sprite cinema_train1 needs rows of one length
Traceback (most recent call last):
  File "tools/showkit/spritetry.py", line 16, in <module>
    f = np.asarray(E.make("sprite", sprite=nm, color=(255, 170, 40), y_lo=a.y_lo, y_hi=a.y_hi, x_half=a.x_half).render(h, 0.0, None), float)
  File "mau5engine.py", line 724, in render
    bm = _sprite_bitmap(names[at])
  File "mau5engine.py", line 625, in _sprite_bitmap
    rows = SPRITES[name]
KeyError: 'cinema_moon'
```

```
$ cd "~/deadmau5 app"; KIT=tools/showkit; W="$KIT/work/cinema"; python3 - <<'EOF'
KIT="tools/showkit"
p=KIT+"/work/cinema/sprites.py"
s=open(p).read()
old='''    wheel="".join(("##" if ((i+k)%4)<2 else "..") if ((i<20) or (i%21>2 and i%21<18)) else "." for i in range(w))
'''
new='''    wheel="".join(("#" if ((i+k)%4)<2 else ".") if ((i<20) or (i%21>2 and i%21<18)) else "." for i in range(w))
'''
assert old in s
s=s.replace(old,new)
open(p,"w").write(s)
EOF
python3 "$W/sprites.py"; B="deadmau5 - Strobe (Special ... [cut]
  deadmau5 - Strobe (Special Features Remix).sprites.json: sprite cinema_train1 needs rows of one length
bulbs 37 canvas 35 43
34
tools/showkit/songs/cinema/t4.png (1080, 338)
tools/showkit/songs/cinema/t5.png (720, 338)
{'cinema_d8': (8, 6), 'cinema_d7': (8, 6), 'cinema_d6': (8, 6), 'cinema_d5': (8, 6), 'cinema_d4': (8, 6), 'cinema_d3': (8, 6), 'cinema_d2': (8, 6), 'cinema_d1': (8, 6), 'cinema_clap_o': (8, 24), 'cinema_clap_h': (8, 24), 'cinema_clap_c': (8, 24), 'cinema_walk1': (8, 8), 'cinema_walk2': (8, 8), 'cinema_walk3': (8, 8), 'cinema_walk4': (8, 8), 'cinema_far1': (8, 8), 'cinema_far2': (8, 8), 'cinema_far3': (8, 8), 'cinema_far4': (8, 8), 'cinema_horse1': (8, 18), 'cinema_horse2': (8, 18), 'cinema_horse3': (8, 18), 'cinema_horse4': (8, 18), 'cinema_train1': (8, 62), 'cinema_train2': (8, 62), 'cinema_train3': (8, 62), 'cinema_train4': (8, 62), 'cinema_line1': (8, 29), 'cinema_line2': (8, 29), 'cinema_moon': (8, 11), 'cinema_moonhit': (8, 11), 'cinema_bulb0': (35, 43), 'cinema_bulb1': (35, 43), 'cinema_bulb2': (35, 43)}
```

```
$ cd "~/deadmau5 app"; date; KIT=tools/showkit; W="$KIT/work/cinema"; python3 - <<'EOF'
KIT="tools/showkit"
p=KIT+"/work/cinema/sprites.py"
s=open(p).read()
a=s.index("# ---- a chorus line of five")
b=s.index("# ---- marquee bulbs")
new='''# ---- a chorus line of three mau5s, kicking: y_lo 54, y_hi 164, x_half 171, 8 rows, 26 cols
def chorus(a,b):
    fig=hd+[a,b]
    return [".".join([fig[r]]*3)+"" for r in range(8)]
D[P+"line1"]=chorus("..#..#..",".##..##.")
D[P+"line2"]=chorus(".#....#.","##....##")
# ----  ... [cut]
Sat Oct 31 12:57:05 PDT 2026
bulbs 37 canvas 35 43
34
wrote shows/scenes/deadmau5 - Strobe (Special Features Remix).scene.json scenes 45 hits 31
deadmau5 - Strobe (Special Features Remix): 46 scenes, 31 hits, written into shows/deadmau5 - Strobe (Special Features Remix).json
bar 41.3    back           shell max 130 mean  29.5   ears max 173 mean  59.6   walk2
bar 42.5                   shell max 130 mean  28.8   ears max 191 mean  26.9   walk2
bar 47.5                   shell max 131 mean  38.3   ears max 178 mean  55.6   climb
bar 48      slam           shell max 230 mean  92.3   ears max 244 mean 152.9   iris · CLAP
bar 66      oz             shell max  76 mean  21.0   ears max 191 mean  23.8   oz
bar 68.3                   shell max  76 mean  22.1   ears max 174 mean  58.9   oz
bar 104.5   train          shell max 128 mean  16.1   ears max  75 mean  17.9   train
bar 105.5                  shell max 128 mean  31.8   ears max 103 mean  21.6   train
bar 106.5                  shell max 128 mean  50.7   ears max  97 mean  23.6   train
bar 107.5                  shell max 128 mean  44.8   ears max  96 mean  23.3   train
bar 108.5                  shell max 128 mean  42.7   ears max 125 mean  29.9   train
bar 109.5                  shell max 128 mean  41.4   ears max 126 mean  29.6   train
bar 112.1   amber          shell max 254 mean  44.9   ears max 199 mean  80.6   amber · TINT
bar 113.1                  shell max 128 mean  37.4   ears max 118 mean  28.9   amber
bar 113.3                  shell max 128 mean  38.9   ears max 173 mean  57.9   amber
bar 116.1                  shell max 128 mean  37.7   ears max 118 mean  28.9   amber
bar 120.5   moon           shell max 125 mean  22.5   ears max 191 mean  32.2   moon
bar 122                    shell max 125 mean  22.4   ea
... [cut] ...
n  32.0   oz 2
bar 146.3                  shell max 255 mean  58.2   ears max 174 mean  54.5   oz 2
bar 152.3   line           shell max 255 mean  81.8   ears max 220 mean  89.2   berkeley 2 · REEL 6
bar 153.3                  shell max 153 mean  58.2   ears max 174 mean  58.4   berkeley 2
bar 161     n2             shell max 188 mean  28.4   ears max  76 mean  23.0   night 2
bar 162.4                  shell max 188 mean  21.9   ears max  36 mean  11.0   night 2
tools/showkit/songs/cinema/c1.png (1800, 1960)
```

```
$ cd "~/deadmau5 app"; date; time python3 mau5scene.py check "deadmau5 - Strobe (Special Features Remix)" 2>&1 | tail -60
Sat Oct 31 12:57:17 PDT 2026
deadmau5 - Strobe (Special Features Remix): 9845 frames at 25 fps through the guard
  scene            from  mean mA   p95 mA     heat   allow W      ms
  dark             0.0s        0        0     0.0%      18.1    0.01
  ticks            0.2s       44      141     0.0%      18.1    0.05
  lamp             7.6s      391      626     0.4%      18.1    0.10
  leader          15.2s      617      729     2.1%      18.1    0.15
  one             28.3s      883     1000     2.5%      18.1    0.13
  film            30.2s      910     1000     6.2%      18.1    0.22
  horse           45.2s      905      944     8.9%      18.1    0.19
  swell           56.4s      992     1000    10.0%      18.1    0.22
  walk            60.2s      625     1000    12.0%      18.1    0.21
  walk2           75.2s      617     1000    13.4%      18.1    0.21
  climb           86.4s      990     1000    14.5%      18.1    0.19
  iris            90.2s      627     1000    15.0%      18.1    0.09
  black           93.9s      135      152    15.0%      18.1    0.07
  beams          105.2s      387      583    14.5%      18.1    0.13
  beams2         112.6s      782     1000    15.2%      18.1    0.17
  cue            116.4s      955     1000    16.2%      18.1    0.17
  parting        120.2s      643     1000    16.8%      18.1    0.19
  oz             123.9s      551      999    17.9%      18.1    0.16
  berkeley       135.2s      679     1000    19.9%      18.1    0.12
  change1        148.3s      467      582    20.0%      18.1    0.09
  night          150.2s      648      982    21.9%      18.1    0.22
  change2        163.3s      412      535    22.0%      18.1    0.09
  strips         165.2s      661     1000    23.9%      18.1    0.18
  change3        178.3s      39
... [cut] ...
4%      18.1    0.19
  drain 2        345.2s      617     1000    51.4%      18.1    0.21
  out            360.2s      498      572    52.0%      18.1    0.15
  away           367.6s      368      495    52.4%      18.1    0.17
  burn           382.6s      345      430    52.5%      18.1    0.06
  tail           390.2s        5       26    52.5%      18.1    0.02
  worst frame 0.83 ms; no scene reaches the sustained floor
python3 mau5scene.py check "deadmau5 - Strobe (Special Features Remix)" 2>&1  2.75s user 0.04s system 99% cpu 2.796 total
tail -60  0.00s user 0.00s system 0% cpu 2.796 total
```

```
$ cd "~/deadmau5 app"; KIT=tools/showkit; W="$KIT/work/cinema"; B="deadmau5 - Strobe (Special Features Remix)"; python3 "$W/big.py" "$B" "$W/b2.png" 113.1 113.35 153.3 153.6 36.1 37.1 146.3 162.4 2>&1 | tail -3
bar 146.3                  shell max 255 mean  58.2   ears max 174 mean  54.5   oz 2
bar 162.4                  shell max 188 mean  21.9   ears max  36 mean  11.0   night 2
tools/showkit/songs/cinema/b2.png (1920, 780)
```

```
$ cd "~/deadmau5 app"; date; time python3 mau5scene.py check "deadmau5 - Strobe (Special Features Remix)" 2>&1 | tail -60
Sat Oct 31 12:57:17 PDT 2026
deadmau5 - Strobe (Special Features Remix): 9845 frames at 25 fps through the guard
  scene            from  mean mA   p95 mA     heat   allow W      ms
  dark             0.0s        0        0     0.0%      18.1    0.01
  ticks            0.2s       44      141     0.0%      18.1    0.05
  lamp             7.6s      391      626     0.4%      18.1    0.10
  leader          15.2s      617      729     2.1%      18.1    0.15
  one             28.3s      883     1000     2.5%      18.1    0.13
  film            30.2s      910     1000     6.2%      18.1    0.22
  horse           45.2s      905      944     8.9%      18.1    0.19
  swell           56.4s      992     1000    10.0%      18.1    0.22
  walk            60.2s      625     1000    12.0%      18.1    0.21
  walk2           75.2s      617     1000    13.4%      18.1    0.21
  climb           86.4s      990     1000    14.5%      18.1    0.19
  iris            90.2s      627     1000    15.0%      18.1    0.09
  black           93.9s      135      152    15.0%      18.1    0.07
  beams          105.2s      387      583    14.5%      18.1    0.13
  beams2         112.6s      782     1000    15.2%      18.1    0.17
  cue            116.4s      955     1000    16.2%      18.1    0.17
  parting        120.2s      643     1000    16.8%      18.1    0.19
  oz             123.9s      551      999    17.9%      18.1    0.16
  berkeley       135.2s      679     1000    19.9%      18.1    0.12
  change1        148.3s      467      582    20.0%      18.1    0.09
  night          150.2s      648      982    21.9%      18.1    0.22
  change2        163.3s      412      535    22.0%      18.1    0.09
  strips         165.2s      661     1000    23.9%      18.1    0.18
  change3        178.3s      39
... [cut] ...
4%      18.1    0.19
  drain 2        345.2s      617     1000    51.4%      18.1    0.21
  out            360.2s      498      572    52.0%      18.1    0.15
  away           367.6s      368      495    52.4%      18.1    0.17
  burn           382.6s      345      430    52.5%      18.1    0.06
  tail           390.2s        5       26    52.5%      18.1    0.02
  worst frame 0.83 ms; no scene reaches the sustained floor
python3 mau5scene.py check "deadmau5 - Strobe (Special Features Remix)" 2>&1  2.75s user 0.04s system 99% cpu 2.796 total
tail -60  0.00s user 0.00s system 0% cpu 2.796 total
```

```
$ cd "~/deadmau5 app"; KIT=tools/showkit; W="$KIT/work/cinema"; B="deadmau5 - Strobe (Special Features Remix)"; python3 "$W/big.py" "$B" "$W/b2.png" 113.1 113.35 153.3 153.6 36.1 37.1 146.3 162.4 2>&1 | tail -3
bar 146.3                  shell max 255 mean  58.2   ears max 174 mean  54.5   oz 2
bar 162.4                  shell max 188 mean  21.9   ears max  36 mean  11.0   night 2
tools/showkit/songs/cinema/b2.png (1920, 780)
```

```
$ cd "~/deadmau5 app"; python3 mau5scene.py check "TIKI TIKI - Slowed" 2>&1 | head -30; grep -n "sustained\|burst\|budget\|tau\|full_pct" mau5power.py | head -40
TIKI TIKI - Slowed: 8002 frames at 25 fps through the guard
  scene            from  mean mA   p95 mA     heat   allow W      ms
  (outside)        0.0s        0        0     0.0%      18.1    0.00
  dark             0.1s        0        0    18.7%      18.1    0.01
  embers           0.5s       31       46     0.0%      18.1    0.06
  hush             5.3s       27       38     0.0%      18.1    0.06
  lighting         7.0s      199      436     0.0%      18.1    0.10
  hook            10.5s      643      886     1.0%      18.1    0.12
  hookb           17.5s      640      862     1.9%      18.1    0.18
  dip             24.4s      140      269     1.9%      18.1    0.07
  climb           26.2s      250      538     1.8%      18.1    0.10
  hook2           27.9s      636      891     3.2%      18.1    0.24
  burn            38.4s      392      815     3.6%      18.1    0.12
  lagoon          45.3s      182      307     3.5%      18.1    0.10
  stop            47.0s       72      156     3.4%      18.1    0.11
  still           48.8s      465      491     3.6%      18.1    0.23
  swell           54.0s      461      567     3.7%      18.1    0.20
  verse           55.7s      315      762     3.9%      18.1    0.12
  vlow            66.2s      187      376     3.8%      18.1    0.05
  vrise           67.9s      155      375     3.7%      18.1    0.10
  big             69.6s      584      890     5.2%      18.1    0.21
  bigb            83.6s      565      845     7.1%      18.1    0.24
  burn2          101.0s      330      617     7.4%      18.1    0.10
  lagoon2        107.9s      177      308     7.2%      18.1    0.10
  stop2          109.6s       38       60     7.1%      18.1    0.07
  watched        111.4s      380      488     7.1%      18.1    0.17
  swell2       
... [cut] ...
 is a ceiling; this is the rolling one.  It
312:        budget = self.budget_ma
315:            budget = min(budget, link)
318:            budget = min(budget, max(allowed_ma, 0.0))
322:        # lands on budget.  Monotonic in s, so bisect: a frame that asks
327:        # spends the budget exactly, so a floor applied as a second pass
342:        # so never over budget; and it runs on frames under budget too,
351:        # over budget then held the shell down for two seconds.  Half
359:        over = after_region > budget and after_region > 0
369:            if float((per * fs).sum()) > budget:
```

```
$ cd "~/deadmau5 app"; python3 mau5scene.py check "TIKI TIKI - Slowed" 2>&1 | head -30; grep -n "sustained\|burst\|budget\|tau\|full_pct" mau5power.py | head -40
TIKI TIKI - Slowed: 8002 frames at 25 fps through the guard
  scene            from  mean mA   p95 mA     heat   allow W      ms
  (outside)        0.0s        0        0     0.0%      18.1    0.00
  dark             0.1s        0        0    18.7%      18.1    0.01
  embers           0.5s       31       46     0.0%      18.1    0.06
  hush             5.3s       27       38     0.0%      18.1    0.06
  lighting         7.0s      199      436     0.0%      18.1    0.10
  hook            10.5s      643      886     1.0%      18.1    0.12
  hookb           17.5s      640      862     1.9%      18.1    0.18
  dip             24.4s      140      269     1.9%      18.1    0.07
  climb           26.2s      250      538     1.8%      18.1    0.10
  hook2           27.9s      636      891     3.2%      18.1    0.24
  burn            38.4s      392      815     3.6%      18.1    0.12
  lagoon          45.3s      182      307     3.5%      18.1    0.10
  stop            47.0s       72      156     3.4%      18.1    0.11
  still           48.8s      465      491     3.6%      18.1    0.23
  swell           54.0s      461      567     3.7%      18.1    0.20
  verse           55.7s      315      762     3.9%      18.1    0.12
  vlow            66.2s      187      376     3.8%      18.1    0.05
  vrise           67.9s      155      375     3.7%      18.1    0.10
  big             69.6s      584      890     5.2%      18.1    0.21
  bigb            83.6s      565      845     7.1%      18.1    0.24
  burn2          101.0s      330      617     7.4%      18.1    0.10
  lagoon2        107.9s      177      308     7.2%      18.1    0.10
  stop2          109.6s       38       60     7.1%      18.1    0.07
  watched        111.4s      380      488     7.1%      18.1    0.17
  swell2       
... [cut] ...
 is a ceiling; this is the rolling one.  It
312:        budget = self.budget_ma
315:            budget = min(budget, link)
318:            budget = min(budget, max(allowed_ma, 0.0))
322:        # lands on budget.  Monotonic in s, so bisect: a frame that asks
327:        # spends the budget exactly, so a floor applied as a second pass
342:        # so never over budget; and it runs on frames under budget too,
351:        # over budget then held the shell down for two seconds.  Half
359:        over = after_region > budget and after_region > 0
369:            if float((per * fs).sum()) > budget:
```

```
$ cd "~/deadmau5 app"; sed -n 280,300p mau5power.py; grep -n "ma_per\|per_channel\|mA_per\|def estimate\|def _ma\|def load" -A6 mau5power.py | head -50; python3 - <<'EOF'
import mau5power, mau5engine as E, numpy as np
h=E.Helmet()
g=mau5power.load(count=h.n)
print(g.regions if hasattr(g,'regions') else '')
print(g.thermal.sustained_w,g.thermal.burst_j,g.thermal.standby_w, g.budget_ma)
print([k for k in dir(g) if not k.startswith('__')])
EOF
        # colours come out a little dimmer as well (20 -> 17, 64 -> 40),
        # and its full ones 2% dimmer.  The eyes now leave about 40% of
        # their lit LEDs in that top tenth instead of 80%, and through
        # the phone's twin the shell's frame-to-frame jitter on eq and
        # the Dimension Remix eq cue fell by 35-60%.
        v = out.astype(np.float64)
        lo, w = self._klo[:m, None], self._kw[:m, None]
        bent = v > lo
        if bent.any():
            wd = np.where(w > 0, w, 1.0)       # no room to bend: a hard clip
            with np.errstate(over="ignore", invalid="ignore"):   # LEDs below lo
                soft = np.where(w > 0, lo - w * np.expm1(-(v - lo) / wd), lo)
            out[:] = np.where(bent, soft, v)
        after_ceiling = self.frame_ma(out)

        # -- each region inside its own allowance -----------------------
        hit = []
        for r in self.regions:
            lo, hi = max(0, r.lo), min(m - 1, r.hi)
            if hi < lo:
                continue
459:def load(path=DEFAULT, count=None):
460-    """Read a power profile.  Missing file -> a deliberately timid one.
461-
462-    A file that is there but unreadable is an error, raised, not a
463-    reason to fall back: the fallback is dimmer than any real profile,
464-    so a typo would look like a dull helmet rather than a broken file.
465-    """
[Region(shell 0..397 ceiling=64 budget=300mA shed=6.0), Region(ear1_tubes 398..491 ceiling=255 budget=620mA shed=1.0), Region(ear1_rim 492..509 ceiling=160 budget=200mA shed=3.0), Region(ear2_rim 510..528 ceiling=160 budget=190mA shed=3.0), Region(ear2_tubes 529..620 ceiling=255 budget=640mA shed=1.0)]
11.0 3000.0 7.452 1000.0
['_ceil', '_floor', '_gov_s', '_gov_t', '_klo', '_kw', '_per_led_ma', '_shed', 'apply', 'budget_ma', 'count', 'default_ceiling', 'describe', 'frame_ma', 'link_limit_ma', 'link_ma', 'regions', 'standby_ma', 'thermal']
```

```
$ cd "~/deadmau5 app"; KIT=tools/showkit; W="$KIT/work/cinema"; cat > "$W/ma.py" <<'EOF'
import sys, os, json
sys.path.insert(0, os.getcwd())
import numpy as np, mau5show, mau5scene, mau5power, mau5engine as E
base="deadmau5 - Strobe (Special Features Remix)"
show=json.load(open("shows/%s.json"%base))
music=mau5show._music_for(show,"shows/%s.mp3"%base)
h=E.Helmet()
sc=mau5scene.Scenes(show["scenes"],h)
g=mau5power.load(count=h.n)
g2=mau5power.load(count=h.n)
spb=show["scenes"]["grid"]["spb"]; t0=show["scenes"]["grid"]["t0"]
print("bar  raw shell mA  raw ears mA | sent total | scene")
for name,m0, ... [cut]
bar  raw shell mA  raw ears mA | sent total | scene
ticks           0.0..   4.0  raw shell    15 ears    33 | sent    46 shell    12 ears    32
lamp            4.0..   8.0  raw shell   337 ears   168 | sent   393 shell   217 ears   161
leader          8.0..  15.0  raw shell  1143 ears   320 | sent   619 shell   290 ears   312
one            15.0..  16.0  raw shell  1052 ears   670 | sent   887 shell   244 ears   626
film           16.0..  24.0  raw shell  1477 ears   652 | sent   910 shell   277 ears   613
horse          24.0..  30.0  raw shell  1336 ears   610 | sent   909 shell   288 ears   602
swell          30.0..  32.0  raw shell  1440 ears   830 | sent   994 shell   216 ears   758
walk           32.0..  40.0  raw shell   733 ears   524 | sent   632 shell   206 ears   407
walk2          40.0..  46.0  raw shell   722 ears   490 | sent   624 shell   214 ears   391
climb          46.0..  48.0  raw shell   998 ears  1004 | sent   994 shell   156 ears   819
iris           48.0..  50.0  raw shell   877 ears   573 | sent   632 shell   182 ears   435
black          50.0..  56.0  raw shell    41 ears   102 | sent   134 shell    32 ears    94
beams          56.0..  60.0  raw shell   176 ears   257 | sent   388 shell   127 ears   249
beams2         60.0..  62.0  raw shell   289 ears   594 | sent   784 shell   188 ears   584
cue            62.0..  64.0  raw shell   632 ears  1051 | sent   962 shell   118 ears   822
parting        64.0..  66.0  raw shell  1052 ears   776 | sent   649 shell   141 ears   489
oz             66.0..  72.0  raw shell   663 ears   459 | sent   556 shell   192 ears   345
berkeley       72.0..  79.0  raw shell   641 ears   651 | sent   684 shell   189 ears   475
change1        79.0..  80.0  raw shell   172 ears   377 | sent   475 shell    99 ears   370

... [cut] ...
9 ears  2013 | sent  1000 shell     9 ears   980
drain         176.0.. 184.0  raw shell   656 ears   510 | sent   626 shell   206 ears   399
drain 2       184.0.. 192.0  raw shell   712 ears   490 | sent   624 shell   214 ears   391
out           192.0.. 196.0  raw shell   476 ears   200 | sent   500 shell   288 ears   193
away          196.0.. 204.0  raw shell   291 ears   147 | sent   369 shell   212 ears   140
burn          204.0.. 208.0  raw shell   882 ears    60 | sent   346 shell   275 ears    59
tail          208.0.. 210.0  raw shell     0 ears     5 | sent     5 shell     0 ears     5
```

```
$ cd "~/deadmau5 app"; date; KIT=tools/showkit; W="$KIT/work/cinema"; python3 - <<'EOF'
KIT="tools/showkit"
p=KIT+"/work/cinema/sprites.py"
s=open(p).read()
a=s.index("# ---- a chorus line of three")
b=s.index("# ---- the moon")
new='''# ---- a chorus line of three smaller mau5s, kicking, kept inside the dome's shoulders:
#      y_lo 54, y_hi 150, x_half 165, 7 rows, 22 cols
def chorus(leg):
    fig=["#....#","##..##",".####.",".#..#.",".####.","..##.."]+[leg]
    return ["..".join([fig[r]]*3) for r in range(7 ... [cut]
Sat Oct 31 12:58:40 PDT 2026
bulbs 37 canvas 35 43
35
tools/showkit/songs/cinema/t4.png (720, 338)
tools/showkit/songs/cinema/t5.png (360, 338)
```

```
$ cd "~/deadmau5 app"; KIT=tools/showkit; W="$KIT/work/cinema"; python3 - <<'EOF'
KIT="tools/showkit"
p=KIT+"/work/cinema/write_treatment.py"
s=open(p).read()
def R(a,b,n=1):
    global s
    assert s.count(a)>=1, a
    s=s.replace(a,b) if n==0 else s.replace(a,b,n)
# sprite params
R('LINE={"y_lo":54,"y_hi":164,"x_half":171}','LINE={"y_lo":54,"y_hi":150,"x_half":165}')
# motif defaults
R('"reel":{"fx":"grad","on":"tubes","axis":"a","scale":3,"speed":0.125,"lo":0,"hi":1,"pal":"silver","gain":0.3}','"reel":{"fx" ... [cut]
wrote shows/scenes/deadmau5 - Strobe (Special Features Remix).scene.json scenes 45 hits 31
deadmau5 - Strobe (Special Features Remix): 46 scenes, 31 hits, written into shows/deadmau5 - Strobe (Special Features Remix).json
deadmau5 - Strobe (Special Features Remix): 9845 frames at 25 fps thro
  scene            from  mean mA   p95 mA     heat   allow W      ms
  dark             0.0s        0        0     0.0%      18.1    0.01
  ticks            0.2s       44      141     0.0%      18.1    0.04
  lamp             7.6s      383      598     0.4%      18.1    0.10
  leader          15.2s      519      610     1.5%      18.1    0.13
  one             28.3s      765      921     1.9%      18.1    0.12
  film            30.2s      657      910     4.1%      18.1    0.20
  horse           45.2s      637      662     5.6%      18.1    0.18
  swell           56.4s      756      889     6.3%      18.1    0.20
  walk            60.2s      566      988     7.9%      18.1    0.19
  walk2           75.2s      554      983     9.1%      18.1    0.19
  climb           86.4s      846     1000     9.9%      18.1    0.17
  iris            90.2s      528     1000    10.3%      18.1    0.08
  black           93.9s      135      152    10.3%      18.1    0.07
  beams          105.2s      387      583     9.8%      18.1    0.12
  beams2         112.6s      615      780    10.3%      18.1    0.16
  cue            116.4s      867     1000    11.2%      18.1    0.15
  parting        120.2s      631     1000    11.6%      18.1    0.17
  oz             123.9s      524      973    12.7%      18.1    0.15
  berkeley       135.2s      670     1000    14.6%      18.1    0.12
  change1        148.3s      467      582    14.8%      18.1    0.08
  night          150.2s      562      856    16.2%      18
... [cut] ...
9 ears  2013 | sent  1000 shell     9 ears   980
drain         176.0.. 184.0  raw shell   540 ears   405 | sent   576 shell   223 ears   332
drain 2       184.0.. 192.0  raw shell   596 ears   367 | sent   564 shell   233 ears   312
out           192.0.. 196.0  raw shell   377 ears   200 | sent   478 shell   267 ears   193
away          196.0.. 204.0  raw shell   242 ears   147 | sent   339 shell   183 ears   140
burn          204.0.. 208.0  raw shell   882 ears    60 | sent   346 shell   275 ears    59
tail          208.0.. 210.0  raw shell     0 ears     5 | sent     5 shell     0 ears     5
```

```
$ cd "~/deadmau5 app"; date; KIT=tools/showkit; W="$KIT/work/cinema"; B="deadmau5 - Strobe (Special Features Remix)"; python3 "$KIT/sheet.py" "$B" "$W/d1.png" 2 6 8.1 11.4 13.4 15.5 16 19 21 24.3 26 31 32 33.3 36.1 41.3 44.3 47.5 48 48.75 49.5 53 57.3 60.3 61.3 63 63.8 64 64.3 65 66 68.3 69 72 73.1 76.3 2>&1 | cut -c1-90 | tail -38;
Sat Oct 31 12:59:53 PDT 2026
bar 2                      shell max  34 mean   0.7   ears max  95 mean   6.3   ticks
bar 6                      shell max  76 mean  14.1   ears max 115 mean  14.8   lamp
bar 8.1                    shell max 150 mean  32.8   ears max  30 mean  12.6   leader
bar 11.4                   shell max 148 mean  33.4   ears max  30 mean  10.4   leader
bar 13.4                   shell max 150 mean  31.3   ears max  30 mean  10.4   leader
bar 15.5                   shell max 140 mean  27.3   ears max 153 mean  31.6   one
bar 16                     shell max 127 mean  25.3   ears max 208 mean 110.6   film · ST
bar 19                     shell max 204 mean  57.8   ears max 115 mean  20.0   film · ST
bar 21                     shell max 204 mean  65.2   ears max 115 mean  20.0   film · ST
bar 24.3                   shell max 115 mean  32.9   ears max 114 mean  21.6   horse
bar 26                     shell max 115 mean  33.9   ears max 115 mean  20.1   horse
bar 31                     shell max 115 mean  36.0   ears max 115 mean  23.8   swell
bar 32                     shell max 118 mean  13.4   ears max 236 mean  86.3   walk · KI
bar 33.3                   shell max 118 mean  21.3   ears max 139 mean  46.1   walk
bar 36.1                   shell max 118 mean  22.6   ears max  94 mean  17.3   walk
bar 41.3                   shell max 118 mean  25.0   ears max 139 mean  46.1   walk2
bar 44.3                   shell max 118 mean  23.0   ears max 139 mean  46.1   walk2
bar 47.5                   shell max 112 mean  30.3   ears max 153 mean  30.8   climb
bar 48                     shell max 230 mean  75.2   ears max 231 mean 138.6   iris · CL
bar 48.75                  shell max  48 mean  26.3   ears max  83 mean  18.5   iris
bar 49.5                   shell m
... [cut] ...
                   shell max  56 mean  16.4   ears max 153 mean  20.0   oz
bar 68.3                   shell max  57 mean  17.2   ears max 139 mean  48.2   oz
bar 69                     shell max  60 mean  17.1   ears max 153 mean  20.0   oz
bar 72                     shell max 151 mean  18.5   ears max 255 mean 121.8   berkeley �
bar 73.1                   shell max  43 mean  17.1   ears max  95 mean  29.3   berkeley
bar 76.3                   shell max  43 mean  17.3   ears max 139 mean  51.7   berkeley
/private/tmp/claude-501/-Users-jones-deadmau5-app/208332e7-8c9f-4c25-bc21-e9a9df98fa1f/scr
```

```
$ cd "~/deadmau5 app"; grep -n "class Player" -A 12 mau5show.py | head -40; grep -n "def frame" -A 40 mau5show.py | sed -n 1,90p; sed -n 176,215p mau5power.py; cat power_profile.json 2>/dev/null | head -40; ls *.json | head
646:class Player:
647-    """Walks a show's cues and renders frames.
648-
649-    Two things happen on top of simply picking the cue for the moment.
650-
651-    Cues crossfade rather than cut.  A hard switch between two full-face
652-    effects reads as a glitch -- the eye sees the discontinuity before
653-    it sees the new effect -- whereas half a second of overlap reads as
654-    intent.  The fade is short enough not to muddy a drop.
655-
656-    And on loud sections a downbeat accent is layered over the top,
657-    locked to the bar grid rather than to a timer.  Half a beat of drift
658-    is the difference between a show that looks choreographed and one
769:    def frame(self, t):
770-        if self.scenes is not None:
771-            try:
772-                out, self.gain, self.label = self.scenes.frame(t, self.music)
773-                return out
774-            except Exception as e:      # a black helmet is the worst outcome
775-                print("mau5show: the scenes failed (%s: %s) -- playing the cue "
776-                      "list" % (type(e).__name__, e))
777-                self.scenes, self.label = None, None
778-        self.gain = 1.0
779-        cur = self.cue_at(t)
780-        if cur is None:
781-            return np.zeros((self.h.n, 3))
782-        out = self._render(cur, t)
783-
784-        if self.fade > 0:
785-            into = t - cur["start"]
786-            if into < self.fade:
787-                i = self._cues.index(cur)
788-                if i > 0:
789-                    prev = self._cues[i - 1]
790-                    k = into / self.fade
791-                    out = k * out + (1 - k) * self._render(prev, t)
792-
793-        if self.music is not None:
794-            lvl = cur.get("level", 0)
795-            ph = self.mu
... [cut] ...
 for is where it was.  On a ceiling of 255
        # it never bends -- a tube is not dimmed by a ceiling it cannot
        # reach -- and on a rim at 160 only the top 20% does.
        c = self._ceil.astype(np.float64)
        self._klo = np.minimum(np.maximum((4.0 * c - 255.0) / 3.0, 0.0), c)
        self._kw = c - self._klo
        self._gov_s = 1.0          # the governor's scale on the last frame
        self._gov_t = None         # and when that was

    # -- estimates ------------------------------------------------------
    def _per_led_ma(self, out):
(eval):1: no matches found: *.json
```

```
$ cd "~/deadmau5 app"; grep -n "class Scene" -A 60 mau5preview.py | sed -n 1,120p; sed -n 760,770p mau5show.py; grep -n "guard\|mau5power" mau5show.py | head -30
56:class Scene:
57-    def __init__(self, helmet):
58-        self.h = helmet
59-        self.px, self.py, self.rad, self.z = _project(helmet)
60-        self.kern = _kernels(self.rad)
61-        self.back = self._backdrop()
62-
63-    def _backdrop(self):
64-        """Faint outlines so an unlit helmet is still legible."""
65-        im = Image.new("RGB", (W, H), (8, 8, 11))
66-        d = ImageDraw.Draw(im)
67-        for m, col in ((self.h.ear1, (26, 26, 32)), (self.h.ear2, (26, 26, 32)),
68-                       (self.h.shell, (20, 20, 26))):
69-            xs, ys = self.px[m], self.py[m]
70-            if not len(xs):
71-                continue
72-            cx, cy = xs.mean(), ys.mean()
73-            r = max(np.hypot(xs - cx, ys - cy).max(), 10)
74-            d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=col, width=2)
75-        return np.asarray(im, np.float32)
76-
77-    def frame(self, rgb, gain=1.0):
78-        buf = self.back.copy()
79-        order = np.argsort(self.z)          # ears (behind) first
80-        for i in order:
81-            c = rgb[i]
82-            if c.max() < 3:
83-                continue
84-            r = float(round(self.rad[i], 1))
85-            k = self.kern[r]
86-            n = k.shape[0]
87-            x0, y0 = int(self.px[i]) - n // 2, int(self.py[i]) - n // 2
88-            x1, y1 = x0 + n, y0 + n
89-            kx0, ky0 = max(0, -x0), max(0, -y0)
90-            x0, y0 = max(0, x0), max(0, y0)
91-            x1, y1 = min(W, x1), min(H, y1)
92-            if x1 <= x0 or y1 <= y0:
93-                continue
94-            sub = k[ky0:ky0 + (y1 - y0), kx0:kx0 + (x1 - x0)]
95-            buf[y0:y1, x0:x1] += sub[:, :, None] * (c * gain)[None, None, :]
96-        return Image.fromarray(np.clip(buf, 0, 255).astype(np.uin
... [cut] ...
 = out.copy(); out[m] = lay[m]
            return out
        return np.maximum(out, lay) if ov.get("mix") == "max" else out + lay

    def frame(self, t):
        if self.scenes is not None:
606:    """The beat pulse at beat phase `ph`: at most 1, applied after the guard.
613:    same peak, which is the guarded frame itself; only the gaps between
684:        # It also costs nothing.  The guard clamps the top anyway, so
806:            # what the power guard exists to take away again -- the
811:            # frame to apply after the guard: the beat is the frame at
912:    if pix.guard is None:
```

```
$ cd "~/deadmau5 app"; date; KIT=tools/showkit; W="$KIT/work/cinema"; cat > "$W/gsheet.py" <<'EOF'
#!/usr/bin/env python3
"""like sheet.py, but through a real guard: gsheet.py base out.png cols bar[:label] ..."""
import json, os, sys
sys.path.insert(0, os.getcwd())
import numpy as np, mau5show, mau5preview as PV, mau5power
from PIL import Image, ImageDraw
base, out = sys.argv[1], sys.argv[2]
cols=int(sys.argv[3])
marks = []
for a in sys.argv[4:]:
    b, _, lab = a.partition(":")
    marks.append((float(b), lab))
show = json.load(open(os.path.join("shows", base + ".json")))
music = mau5show._music ... [cut]
Sat Oct 31 13:00:38 PDT 2026
bar 8.1                shell max  34 mean   9.8   ears max  30 mean  12.1  sent  509  leader
bar 13.4               shell max  33 mean   9.7   ears max  30 mean  10.1  sent  474  leader
bar 19                 shell max  23 mean   9.7   ears max 114 mean  19.6  sent  633  film · STROBE
bar 26                 shell max  27 mean   9.8   ears max 114 mean  19.7  sent  634  horse
bar 33.3               shell max  28 mean   7.2   ears max 116 mean  41.3  sent  919  walk
bar 36.1               shell max  32 mean   8.2   ears max  80 mean  14.2  sent  499  walk
bar 48                 shell max   3 mean   1.8   ears max  76 mean  55.6  sent 1000  iris · CLAP
bar 53                 shell max  31 mean   1.3   ears max  25 mean   5.8  sent  144  black
bar 60.3               shell max  53 mean   5.9   ears max  95 mean  21.3  sent  539  beams2
bar 64.3               shell max   2 mean   1.1   ears max 136 mean  53.2  sent  942  parting · COLOUR
bar 66                 shell max  29 mean   9.7   ears max 145 mean  19.5  sent  631  oz
bar 68.3               shell max  19 mean   6.4   ears max 117 mean  41.7  sent  902  oz
bar 73.1               shell max  17 mean   7.4   ears max  73 mean  22.3  sent  610  berkeley
bar 76.3               shell max  14 mean   6.0   ears max 118 mean  44.2  sent  932  berkeley
bar 82.4               shell max  33 mean   6.7   ears max  39 mean  12.3  sent  422  night
bar 90.3               shell max   7 mean   2.6   ears max  95 mean  47.0  sent  879  strips
bar 99                 shell max  54 mean   7.5   ears max  25 mean   1.4  sent  252  alone
bar 106.5              shell max  22 mean   9.8   ears max  97 mean  18.4  sent  613  train
bar 113.1              shell max  32 mean   8.3   ears max  80 mean  21.0  sent  612  am
... [cut] ...
 145 mean  19.5  sent  631  drain 2
bar 194                shell max  52 mean   9.7   ears max  89 mean  15.4  sent  563  out
bar 199                shell max  54 mean   8.1   ears max  76 mean  11.8  sent  453  away
bar 205                shell max  20 mean   9.6   ears max  63 mean   4.2  sent  370  burn
bar 206                shell max  23 mean   9.7   ears max  80 mean   6.2  sent  404  burn
bar 207                shell max  49 mean   9.9   ears max 112 mean   9.7  sent  462  burn
tools/showkit/songs/cin
```

```
$ cd "~/deadmau5 app"; KIT=tools/showkit; W="$KIT/work/cinema"; python3 - <<'EOF'
import numpy as np, mau5power, mau5engine as E
h=E.Helmet(); g=mau5power.load(count=h.n)
def ma(rgb,m):
    f=np.zeros((h.n,3)); f[m]=rgb; return g.frame_ma(f)
print("per LED white 255:",g._per_led_ma(np.full((h.n,3),255.0))[:3], "standby",g.standby_ma)
for name,m in (("ears",h.ears),("tubes",h.tubes),("rims",h.rims),("shell",h.shell)):
    print(name,[ (rgb,round(ma(rgb,m))) for rgb in ((51,51,51),(51,0,0),(0,51,0),(0,0,51),(51,14,12),(25,25,25),(10,10,10))])
EOF
sed -n 300,380p mau5power.py
per LED white 255: [19. 19. 19.] standby <bound method PowerGuard.standby_ma of <mau5power.PowerGuard object at 0x10a32ad30>>
ears [((51, 51, 51), 847), ((51, 0, 0), 282), ((0, 51, 0), 282), ((0, 0, 51), 282), ((51, 14, 12), 426), ((25, 25, 25), 415), ((10, 10, 10), 166)]
tubes [((51, 51, 51), 707), ((51, 0, 0), 236), ((0, 51, 0), 236), ((0, 0, 51), 236), ((51, 14, 12), 356), ((25, 25, 25), 346), ((10, 10, 10), 139)]
rims [((51, 51, 51), 141), ((51, 0, 0), 47), ((0, 51, 0), 47), ((0, 0, 51), 47), ((51, 14, 12), 71), ((25, 25, 25), 69), ((10, 10, 10), 28)]
shell [((51, 51, 51), 1512), ((51, 0, 0), 504), ((0, 51, 0), 504), ((0, 0, 51), 504), ((51, 14, 12), 761), ((25, 25, 25), 741), ((10, 10, 10), 297)]
                continue
            seg = out[lo:hi + 1]
            ma = float(seg.sum() / (3 * 255.0) * MA_PER_LED_FULL_WHITE)
            if ma > r.budget_ma and ma > 0:
                seg *= r.budget_ma / ma
                hit.append(r.name)
        after_region = self.frame_ma(out)

        # -- the thermal allowance, if one is in force -------------------
        # The per-frame budget is a ceiling; this is the rolling one.  It
        # is applied before the global scale so the two compose rather
        # than fight: whichever is tighter at this instant wins.
        budget = self.budget_ma
        link = self.link_limit_ma()
        if link is not None:
            budget = min(budget, link)
        if self.thermal is not None:
            allowed_ma = self.thermal.allowance_w() / 12.0 * 1000.0
            budget = min(budget, max(allowed_ma, 0.0))

        # -- and the whole frame inside the global one ------------------
        # Scale region g by s**shed_g and solve for the single s that
        # lands on budget.  Monotonic in s, so bisect: a frame that ask
... [cut] ...
      np.divide(self._floor[:m], omx, out=fs, where=lit)
            np.clip(fs, 0.0, 1.0, out=fs)
            if float((per * fs).sum()) > budget:
                fs[:] = 0.0            # the floor does not fit; budget wins
            shed = self._shed[:m]
            lo_s = 1.0
            if over:
                lo_s, hi_s = 0.0, 1.0
                for _ in range(40):
                    mid = (lo_s + hi_s) / 2.0
                    if float((per * np.maximum(mid ** shed, fs)).sum()) > budget:
                        hi_s = mid
                    else:
                        lo_s = mid
```

```
$ cd "~/deadmau5 app"; KIT=tools/showkit; W="$KIT/work/cinema"; cat > "$W/ma.py" <<'EOF'
import sys, os, json
sys.path.insert(0, os.getcwd())
import numpy as np, mau5show, mau5scene, mau5power, mau5engine as E
base="deadmau5 - Strobe (Special Features Remix)"
show=json.load(open("shows/%s.json"%base))
music=mau5show._music_for(show,"shows/%s.mp3"%base)
h=E.Helmet()
sc=mau5scene.Scenes(show["scenes"],h)
g=mau5power.load(count=h.n)
g2=mau5power.load(count=h.n)
spb=show["scenes"]["grid"]["spb"]; t0=show["scenes"]["grid"]["t0"]
fps=25
dur=float(show.get("duration",0))
per={}
order=[]
for i in range(i ... [cut]
wrote shows/scenes/deadmau5 - Strobe (Special Features Remix).scene.json scenes 45 hits 31
deadmau5 - Strobe (Special Features Remix): 46 scenes, 31 hits, written into shows/deadmau5 - Strobe (Special Features Remix).json
scene        | raw shell  ears | sent  max over%% | shell mA  min | ears mA  max | shell LED p97 median | heat
dark         |      0      0 |     0     0   0% |     0     0 |     0     0 |    0    0 |  0.0
ticks        |     15    143 |    44   169   0% |    12     0 |    31   142 |    8    0 |  0.0
lamp         |    336    339 |   383   639   0% |   217    26 |   150   331 |   30    7 |  0.4
leader       |    580    330 |   519   630   0% |   290   287 |   211   322 |   37    3 |  1.5
one          |    495    541 |   708   837   0% |   267     0 |   424   529 |   39    4 |  1.9
film         |    594    852 |   640  1000   2% |   276   205 |   345   775 |   32    7 |  3.9
horse        |    589    367 |   637   667   0% |   288   286 |   330   359 |   35    3 |  5.5
swell        |    634    701 |   756  1000   1% |   288   286 |   449   693 |   32    5 |  6.2
walk         |    375    996 |   529  1000   3% |   213    95 |   296   859 |   37    6 |  7.5
walk2        |    366    762 |   512  1000   3% |   213   102 |   280   741 |   38    6 |  8.5
climb        |    480    859 |   846  1000  11% |   285   201 |   542   779 |   36    4 |  9.3
iris         |    408    899 |   522  1000   9% |   209     0 |   299   799 |   20    6 |  9.7
black        |     41    106 |   135   168   0% |    32     7 |    94    98 |   17    0 |  9.0
beams        |    160    393 |   379   593   0% |   118    34 |   249   385 |   32    0 |  9.2
beams2       |    291    602 |   615   825   0% |   192   125 |   410   595 |   44    0 |  9.7
cue          |    485    913 |   856  1000
... [cut] ...
7
drain        |    318   1031 |   510  1000   2% |   195    43 |   294   847 |   17   11 | 34.0
drain 2      |    358    762 |   509  1000   2% |   209    88 |   280   744 |   37    6 | 35.2
out          |    203    289 |   356   462   0% |   146   126 |   191   281 |   47    5 | 35.4
away         |    157    221 |   275   390   0% |   119    65 |   139   214 |   34    3 | 35.3
burn         |    572    163 |   340   456   0% |   270    70 |    58   162 |   33   11 | 35.4
tail         |      0     36 |     5    36   0% |     0     0 |     5    36 |    0    0 | 35.0
Sat Oct 31 13:03:02 PDT 2026
```

```
$ cd "~/deadmau5 app"; date; KIT=tools/showkit; W="$KIT/work/cinema"; python3 - <<'EOF'
KIT="tools/showkit"
p=KIT+"/work/cinema/write_treatment.py"
s=open(p).read()
def R(a,b,n=1):
    global s
    assert s.count(a)>=1, a
    s=s.replace(a,b) if n==0 else s.replace(a,b,n)
R('{"use":"reel","speed":{"climb":0.25,"47":0.5},"gain":[0.14,0.26]},\n {"use":"lift","pal":"silver","step":{"climb":0.5,"47":0.25},"gain":[0.14,0.32]}]})','{"use":"reel","speed":{"climb":0.25,"47":0.5},"gain":[0.1,0.16]},\n {"use":"lift","pa ... [cut]
Sat Oct 31 13:03:25 PDT 2026
wrote shows/scenes/deadmau5 - Strobe (Special Features Remix).scene.json scenes 45 hits 31
deadmau5 - Strobe (Special Features Remix): 46 scenes, 31 hits, written into shows/deadmau5 - Strobe (Special Features Remix).json
bar 6                  shell max  41 mean   9.8   ears max 114 mean  14.3  sent  545  lamp
bar 8.1                shell max  40 mean   9.8   ears max  30 mean  12.1  sent  509  leader
bar 13.4               shell max  40 mean   9.7   ears max  30 mean  10.1  sent  474  leader
bar 15.5               shell max  44 mean   9.8   ears max 145 mean  27.3  sent  762  one
bar 16                 shell max  36 mean   6.8   ears max 119 mean  46.9  sent 1000  film · START
bar 19                 shell max  29 mean   9.7   ears max 114 mean  19.6  sent  633  film · STROBE
bar 21                 shell max  29 mean   9.7   ears max 114 mean  19.6  sent  633  film · STROBE
bar 26                 shell max  34 mean   9.7   ears max 114 mean  19.7  sent  634  horse
bar 31                 shell max  31 mean   9.7   ears max 114 mean  23.3  sent  695  swell
bar 33.3               shell max  45 mean   8.4   ears max 131 mean  37.1  sent  884  walk
bar 36.1               shell max  40 mean   8.0   ears max  80 mean  14.2  sent  492  walk
bar 41.3               shell max  42 mean   9.3   ears max 131 mean  37.1  sent  913  walk2
bar 47.5               shell max  37 mean   9.7   ears max 145 mean  22.4  sent  681  climb
bar 48                 shell max  26 mean   9.6   ears max 106 mean  41.2  sent  992  iris · CLAP
bar 48.5               shell max  15 mean   9.8   ears max  64 mean  10.3  sent  479  iris
bar 49.5               shell max  31 mean   4.5   ears max  42 mean   7.0  sent  260  iris
bar 53                 shell max  31 mean   1.3   ear
... [cut] ...
1.9  sent 1000  night · REEL 
bar 82.4               shell max  41 mean   6.7   ears max  39 mean  12.3  sent  422  night
bar 83.1               shell max  45 mean   7.5   ears max  43 mean  17.1  sent  524  night
bar 88                 shell max  22 mean   7.2   ears max 136 mean  45.9  sent 1000  strips · REEL
bar 90.3               shell max  21 mean   8.4   ears max 124 mean  39.8  sent  930  strips
bar 93                 shell max  30 mean   9.7   ears max 145 mean  17.0  sent  588  strips
(scratch)/ki
```

```
$ cd "~/deadmau5 app"; date; KIT=tools/showkit; W="$KIT/work/cinema"; python3 - <<'EOF'
KIT="tools/showkit"
p=KIT+"/work/cinema/write_treatment.py"
s=open(p).read()
def R(a,b,n=1):
    global s
    assert s.count(a)>=1, a
    s=s.replace(a,b) if n==0 else s.replace(a,b,n)
R('FILM=[{"use":"vignette","pal":"silver","gate":FLICK},{"use":"grain","pal":"silver"},','FILM=[{"use":"vignette","pal":"silver","gain":0.05,"gate":FLICK},{"use":"grain","pal":"silver","gain":0.1},')
R('"params":{"text":"STROBE","color":"sepi ... [cut]
Sat Oct 31 13:03:54 PDT 2026
wrote shows/scenes/deadmau5 - Strobe (Special Features Remix).scene.json scenes 45 hits 31
deadmau5 - Strobe (Special Features Remix): 46 scenes, 31 hits, written into shows/deadmau5 - Strobe (Special Features Remix).json
bar 96                 shell max  27 mean   9.6   ears max 142 mean  38.2  sent  944  fall · LAST C
bar 96.5               shell max  18 mean   9.6   ears max  82 mean  13.1  sent  525  fall
bar 97.5               shell max  24 mean   5.9   ears max  44 mean   7.3  sent  317  fall
bar 99                 shell max  51 mean   6.4   ears max  25 mean   1.4  sent  218  alone
bar 102                shell max  49 mean   6.5   ears max  25 mean   1.6  sent  224  alone
bar 104.5              shell max  44 mean   5.1   ears max  75 mean  14.6  sent  414  train
bar 106                shell max  34 mean   9.7   ears max  87 mean  16.1  sent  576  train
bar 107.5              shell max  31 mean   9.8   ears max  95 mean  17.6  sent  601  train
bar 109.5              shell max  33 mean   9.7   ears max 125 mean  22.1  sent  676  train
bar 112                shell max  25 mean   5.0   ears max 113 mean  50.1  sent 1000  amber · TINT
bar 113.1              shell max  37 mean   8.2   ears max  80 mean  21.0  sent  612  amber
bar 113.35             shell max  34 mean   8.3   ears max  80 mean  25.1  sent  680  amber
bar 116.5              shell max  42 mean   9.7   ears max 145 mean  27.2  sent  759  amber
bar 120                shell max  31 mean   5.0   ears max 115 mean  50.1  sent 1000  moon · TINT 2
bar 122                shell max  44 mean   9.1   ears max 145 mean  25.5  sent  713  moon
bar 124                shell max  44 mean   9.1   ears max 145 mean  25.5  sent  713  moon
bar 126                shell max  58 mean   9.7   ears max
... [cut] ...
7   ears max  77 mean   6.3  sent  405  burn
bar 206.75             shell max  45 mean   9.8   ears max  70 mean   5.2  sent  388  burn
bar 207.25             shell max  52 mean   9.2   ears max 108 mean   9.7  sent  440  burn
bar 207.75             shell max  54 mean   5.8   ears max 102 mean   8.8  sent  321  burn
bar 208                shell max   0 mean   0.0   ears max  63 mean   1.9  sent   33  tail
bar 208.5              shell max   0 mean   0.0   ears max  47 mean   1.6  sent   27  tail
(scratch)/ki
```

```
$ cd "~/deadmau5 app"; grep -n "sprite" remote/offline/engine.js | head -20; grep -n "SPRITES\|sprites" mau5offline.py | head -20; grep -n "GOV_RISE\s*=\|GOV_FROM\s*=\|GOV_MIN_DT\s*=" mau5power.py
168:function spriteBitmap(fonts, name) {
169:  const rows = fonts.sprites[name];
458:def('sprite', { sprite: 'smile', color: [0, 255, 255], bg: [0, 0, 0],
463:    const names = String(this.p.sprite).split('|');
465:    const bm = spriteBitmap(this.fonts, names[at]);
968:              textBitmap, glyphBitmap, digitBitmap, spriteBitmap, fract, pmod,
73:    from mau5fx import FONT5x7, SPRITES
96:            "sprites": {k: list(v) for k, v in SPRITES.items()},
56:GOV_RISE = 1.0
57:GOV_MIN_DT = 1.0 / 40.0
58:GOV_FROM = 0.01
```

```
$ cd "~/deadmau5 app"; date; KIT=tools/showkit; W="$KIT/work/cinema"; python3 - <<'EOF'
KIT="tools/showkit"
p=KIT+"/work/cinema/write_treatment.py"
s=open(p).read()
def R(a,b,n=1):
    global s
    assert s.count(a)>=1, a
    s=s.replace(a,b) if n==0 else s.replace(a,b,n)
# ---- darkness before each drop lands on the music's own hole
R('S({"name":"one","from":"last","to":"film","pal":"silver","out":0.25,','S({"name":"one","from":"last","to":"film","pal":"silver","out":0.5,')
R('S({"name":"cue","from":"cue1","t ... [cut]
Sat Oct 31 13:05:47 PDT 2026
wrote shows/scenes/deadmau5 - Strobe (Special Features Remix).scene.json scenes 45 hits 31
deadmau5 - Strobe (Special Features Remix): 46 scenes, 31 hits, written into shows/deadmau5 - Strobe (Special Features Remix).json
scene        | raw shell  ears | sent  max over%% | shell mA  min | ears mA  max | shell LED p97 median | heat
dark         |      0      0 |     0     0   0% |     0     0 |     0     0 |    0    0 |  0.0
ticks        |     15    143 |    44   169   0% |    12     0 |    31   142 |    8    0 |  0.0
lamp         |    336    339 |   383   639   0% |   217    26 |   150   331 |   30    7 |  0.4
leader       |    511    330 |   518   630   0% |   289   273 |   211   322 |   36    4 |  1.5
one          |    453    541 |   657   837   0% |   248     0 |   392   529 |   37    3 |  1.8
film         |    772    505 |   636   804   0% |   280   228 |   335   496 |   32    5 |  3.9
horse        |    511    367 |   637   667   0% |   288   286 |   330   359 |   34    3 |  5.4
swell        |    555    701 |   756  1000   1% |   288   286 |   449   693 |   31    5 |  6.1
walk         |    337    868 |   512  1000   3% |   203    95 |   289   773 |   35    6 |  7.4
walk2        |    326    762 |   494  1000   2% |   201   101 |   274   741 |   35    6 |  8.3
climb        |    480    589 |   717   887   0% |   289   286 |   410   579 |   36    4 |  8.9
iris         |    408    532 |   404   832   0% |   214     0 |   175   524 |   21    6 |  9.1
black        |     41    106 |   135   168   0% |    32     7 |    94    98 |   17    0 |  8.3
beams        |    160    393 |   379   593   0% |   118    34 |   249   385 |   32    0 |  8.6
beams2       |    291    602 |   615   825   0% |   192   125 |   410   595 |   44    0 |  9.1
cue          
... [cut] ...
bar 120                shell max  58 mean   8.6   ears max 154 mean  34.4  sent  847  moon · TINT 2
bar 128                shell max  38 mean   9.7   ears max 149 mean  32.9  sent  858  slip · IMPACT
bar 144                shell max  20 mean   9.7   ears max 153 mean  31.7  sent  835  oz 2 · TAKE 2
bar 144.25             shell max  22 mean   9.6   ears max 148 mean  23.7  sent  702  oz 2 · TAKE 2
bar 152                shell max  36 mean   9.7   ears max 154 mean  31.9  sent  838  berkeley 2 · 
(scratch)/ki
```

```
$ cd "~/deadmau5 app"; date; KIT=tools/showkit; W="$KIT/work/cinema"; python3 - <<'EOF'
KIT="tools/showkit"
p=KIT+"/work/cinema/write_treatment.py"
s=open(p).read()
def R(a,b,n=1):
    global s
    assert s.count(a)>=1, a
    s=s.replace(a,b) if n==0 else s.replace(a,b,n)
R('{"use":"dye","scale":0.8,"speed":0.0625,"gain":0.09},\n {"use":"stars"},\n walker("white@0.8",0,0,"cinema_walk1|cinema_walk2",0.3,1/SPB,False),','{"use":"dye","scale":0.8,"speed":0.0625,"gain":0.09,"env":{"in":1.5}},\n {"use":"stars","env" ... [cut]
Sat Oct 31 13:06:16 PDT 2026
wrote shows/scenes/deadmau5 - Strobe (Special Features Remix).scene.json scenes 45 hits 31
deadmau5 - Strobe (Special Features Remix): 46 scenes, 31 hits, written into shows/deadmau5 - Strobe (Special Features Remix).json
bar 26                 shell max  34 mean   9.7   ears max 114 mean  19.7  sent  634  horse
bar 26.125             shell max  35 mean   9.8   ears max 114 mean  19.5  sent  632  horse
bar 36.1               shell max  36 mean   7.4   ears max  80 mean  14.2  sent  474  walk
bar 113.1              shell max  37 mean   8.2   ears max  80 mean  17.9  sent  560  amber
bar 113.35             shell max  34 mean   8.3   ears max  80 mean  21.9  sent  627  amber
bar 122                shell max  45 mean   8.3   ears max 145 mean  25.5  sent  691  moon
bar 144                shell max  47 mean   9.9   ears max 153 mean  31.7  sent  835  oz 2 · TAKE 2
bar 146.3              shell max  32 mean   9.1   ears max 129 mean  34.5  sent  864  oz 2
bar 153.3              shell max  28 mean   9.1   ears max 129 mean  38.7  sent  935  berkeley 2
(scratch)/ki
```

I'll read the correction and the new power tools.

```
$ date; KIT=tools/showkit; ls -la "$KIT"; sed -n 38,200p "$KIT/BRIEF.md"; echo ------; cat "$KIT/power.py"; echo ------; cat "$KIT/scenepower.py"; echo ------; cat "$KIT/sheet.py"
Sat Oct 31 13:07:33 PDT 2026
total 184
drwxr-xr-x@  13 jones  wheel    416 Oct 31 13:06 .
drwx------@ 288 jones  wheel   9216 Oct 31 13:07 ..
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
621 LEDs: shell 397, each ear 112 (three tubes and a rim). LEDs sit behind diffusers, so soft shapes and big motion read best; fine detail does not. On the shell: gates and pumps no faster than 8th notes (the compiler refuses faster, because whole-shell flicker reads as a fault). Ears can go faster. Current is tight: the sustained budget is about 300 mA of LED current across the whole helmet with short bursts to 1 A, and when the ears are loud the guard takes it from the shell, so keep shell gains near Tiki's (0.14 to 0.3 for full-shell layers, more for small lit areas) and ear layers 0.25 to 0.7, and confirm in `sheet.py` that the shell is really visible. Bright full-helmet white is for one moment in the whole song at most. Dark is an effect: contrast is most of what makes a hit land.

Song-specific concept follows in your task. It is a starting point. If the music says otherwise, follow the music, and keep it unique.

## Added after the first run: the long set
These shows also play back to 
... [cut] ...
** (1.0 / GAM)
    im = Image.fromarray(arr.astype(np.uint8)).crop((60, 40, 700, 560)).resize((W, H))
    o.paste(im, ((k % cols) * W, (k // cols) * H))
    d.text(((k % cols) * W + 5, (k // cols) * H + 3), "%s bar %g" % (lab, bar), fill=(255, 255, 255))
    d.text(((k % cols) * W + 5, (k // cols) * H + 15), (label or "")[:42], fill=(180, 180, 180))
    s = res[h.shell]; e = res[h.ears]
    print("bar %-7g %-10s sent %4.0f mA  shell max %3.0f mean %5.1f  ears max %3.0f mean %5.1f  %s" % (bar, lab[:10], rep["sent_ma"], s.max(), s.mean(), e.max(), e.mean(), label))
o.save(out)
print(out, o.size)
```

```
$ cd "~/deadmau5 app"; date; KIT=tools/showkit; W="$KIT/work/cinema"; python3 - <<'EOF'
KIT="tools/showkit"
p=KIT+"/work/cinema/write_treatment.py"
s=open(p).read()
def R(a,b,n=1):
    global s
    assert s.count(a)>=1, a
    s=s.replace(a,b) if n==0 else s.replace(a,b,n)
# trio inside the shoulders
R('LINE={"y_lo":54,"y_hi":150,"x_half":165}','LINE={"y_lo":54,"y_hi":150,"x_half":150}')
# the rocket goes for the eye
R('{"fx":"orb","on":"shell","x":[300,30],"y":[175,122],"rad":13,"soft":8,"pal":"gold","c":1,"mi ... [cut]
Sat Oct 31 13:07:38 PDT 2026
bulbs 37 canvas 35 43
34
wrote shows/scenes/deadmau5 - Strobe (Special Features Remix).scene.json scenes 45 hits 31
deadmau5 - Strobe (Special Features Remix): 46 scenes, 31 hits, written into shows/deadmau5 - Strobe (Special Features Remix).json
bar 103.5              shell max  51 mean   6.4   ears max  25 mean   1.6  sent  222  alone
bar 104.5              shell max  43 mean   9.7   ears max  48 mean  12.4  sent  514  train
bar 105                shell max  33 mean   9.8   ears max  58 mean  12.8  sent  521  train
bar 105.5              shell max  42 mean   9.7   ears max  74 mean  14.2  sent  544  train
bar 106                shell max  34 mean   9.7   ears max  48 mean  13.1  sent  526  train
bar 113.1              shell max  41 mean   8.1   ears max  80 mean  17.9  sent  558  amber
bar 113.35             shell max  39 mean   8.3   ears max  80 mean  21.9  sent  627  amber
bar 126                shell max  60 mean   9.0   ears max 145 mean  25.5  sent  711  moon
bar 127.9              shell max  48 mean   6.7   ears max  52 mean  15.9  sent  482  moon
bar 128                shell max  39 mean   9.7   ears max 149 mean  32.9  sent  858  slip · IMPACT
bar 128.25             shell max  44 mean   9.7   ears max 145 mean  34.4  sent  879  slip · IMPACT
bar 128.75             shell max  29 mean   9.7   ears max 135 mean  29.3  sent  795  slip · IMPACT
bar 203.5              shell max  47 mean   2.5   ears max  76 mean  11.6  sent  281  away
bar 204                shell max   0 mean   0.0   ears max  76 mean   5.0  sent   84  burn
bar 204.25             shell max  21 mean   9.6   ears max  73 mean   4.8  sent  381  burn
bar 208                shell max   0 mean   0.0   ears max  63 mean   1.9  sent   33  tail
(scratch)/ki
```

```
$ cd "~/deadmau5 app"; date; KIT=tools/showkit; B="deadmau5 - Strobe (Special Features Remix)"; python3 "$KIT/power.py" "$B"; python3 "$KIT/scenepower.py" "$B"; python3 "$KIT/power.py" "TIKI TIKI - Slowed"; python3 - <<'EOF'
import mau5power, mau5engine as E, numpy as np
h=E.Helmet(); g=mau5power.load(count=h.n)
print("standby W", g.thermal.standby_w, "sustained", g.thermal.sustained_w)
f=np.zeros((h.n,3))
_,rep=g.apply(f,now=0.0,gain=1.0)
print(rep)
EOF
sed -n 380,458p mau5power.py
Sat Oct 31 13:07:38 PDT 2026
deadmau5 - Strobe (Special Features Remix): 394 s, mean 13.4 W (target 11.5 or less), heat at the end 32%
hottest scenes (name, mean W, seconds): slip 16.1 15s; film 15.1 15s; amber 14.6 15s; moon 14.5 15s; oz 2 14.1 15s; train 14.1 15s; walk 13.6 15s; drain 13.5 15s
scene            mean    p95   gov%   reg%  shellm   earsm   smax   heat
dark                0      0      0      0     0.0     0.0      0   0.0%
ticks              44    141      0      0     0.4     1.8     33   0.0%
lamp              383    598      0     48     7.3     9.1     40   0.4%
leader            518    610      0     96     9.8    12.7     45   1.5%
one               657    828      0     70     8.4    23.6     48   1.8%
film              636    671      0     79     9.5    20.1     53   3.9%
horse             637    662      0    100     9.7    19.8     36   5.4%
swell             756    889      1    100     9.7    27.0     34   6.1%
walk              512    925      3     12     6.8    17.4     45   7.4%
walk2             494    894      2      9     6.8    16.5     45   8.3%
climb             717    826      0    100     9.7    24.6     39   8.9%
iris              404    743      0     55     7.2    10.6     32   9.1%
black             135    152      0      0     1.1     5.7     38   9.1%
beams             379    563      0      0     4.0    15.0     51   8.6%
beams2            615    780      0      0     6.5    24.7     57   9.1%
cue               664    840      0     50     7.8    24.8     55   9.7%
parting           470    885      1     19     6.7    15.2     30   9.9%
oz                458    864      1      3     7.0    13.8     30  10.6%
berkeley          570    969      5    100     7.6    19.6     23  12.1%
change1           467    582      0      0 
... [cut] ...
en there is no measured profile.

    Every LED at an eighth of full drive, 300 mA of LED current in all
    and a thermal bucket a tenth the size of the measured one.  Dim, but
    nothing it can be asked to show will hurt the helmet, which is the
    point: this used to return None, every caller took None to mean "no
    guard", and a missing file therefore meant an unlimited helmet.
    """
    return PowerGuard(count, [Region("all", 0, count - 1, 32, 300.0)], 300.0,
                      default_ceiling=32,
                      thermal=ThermalBudget(9.0, 300.0, 12.0, count * 0.012, 0.30))
```

```
$ cd "~/deadmau5 app"; date; KIT=tools/showkit; B="deadmau5 - Strobe (Special Features Remix)"; python3 "$KIT/power.py" "$B"; python3 "$KIT/scenepower.py" "$B"; python3 "$KIT/power.py" "TIKI TIKI - Slowed"; python3 - <<'EOF'
import mau5power, mau5engine as E, numpy as np
h=E.Helmet(); g=mau5power.load(count=h.n)
print("standby W", g.thermal.standby_w, "sustained", g.thermal.sustained_w)
f=np.zeros((h.n,3))
_,rep=g.apply(f,now=0.0,gain=1.0)
print(rep)
EOF
sed -n 380,458p mau5power.py
Sat Oct 31 13:07:38 PDT 2026
deadmau5 - Strobe (Special Features Remix): 394 s, mean 13.4 W (target 11.5 or less), heat at the end 32%
hottest scenes (name, mean W, seconds): slip 16.1 15s; film 15.1 15s; amber 14.6 15s; moon 14.5 15s; oz 2 14.1 15s; train 14.1 15s; walk 13.6 15s; drain 13.5 15s
scene            mean    p95   gov%   reg%  shellm   earsm   smax   heat
dark                0      0      0      0     0.0     0.0      0   0.0%
ticks              44    141      0      0     0.4     1.8     33   0.0%
lamp              383    598      0     48     7.3     9.1     40   0.4%
leader            518    610      0     96     9.8    12.7     45   1.5%
one               657    828      0     70     8.4    23.6     48   1.8%
film              636    671      0     79     9.5    20.1     53   3.9%
horse             637    662      0    100     9.7    19.8     36   5.4%
swell             756    889      1    100     9.7    27.0     34   6.1%
walk              512    925      3     12     6.8    17.4     45   7.4%
walk2             494    894      2      9     6.8    16.5     45   8.3%
climb             717    826      0    100     9.7    24.6     39   8.9%
iris              404    743      0     55     7.2    10.6     32   9.1%
black             135    152      0      0     1.1     5.7     38   9.1%
beams             379    563      0      0     4.0    15.0     51   8.6%
beams2            615    780      0      0     6.5    24.7     57   9.1%
cue               664    840      0     50     7.8    24.8     55   9.7%
parting           470    885      1     19     6.7    15.2     30   9.9%
oz                458    864      1      3     7.0    13.8     30  10.6%
berkeley          570    969      5    100     7.6    19.6     23  12.1%
change1           467    582      0      0 
... [cut] ...
en there is no measured profile.

    Every LED at an eighth of full drive, 300 mA of LED current in all
    and a thermal bucket a tenth the size of the measured one.  Dim, but
    nothing it can be asked to show will hurt the helmet, which is the
    point: this used to return None, every caller took None to mean "no
    guard", and a missing file therefore meant an unlimited helmet.
    """
    return PowerGuard(count, [Region("all", 0, count - 1, 32, 300.0)], 300.0,
                      default_ceiling=32,
                      thermal=ThermalBudget(9.0, 300.0, 12.0, count * 0.012, 0.30))
```

```
$ cd "~/deadmau5 app"; date; KIT=tools/showkit; W="$KIT/work/cinema"; python3 - <<'EOF'
KIT="tools/showkit"
p=KIT+"/work/cinema/write_treatment.py"
s=open(p).read()
def R(a,b,n=1):
    global s
    assert s.count(a)>=1, a
    s=s.replace(a,b) if n==0 else s.replace(a,b,n)
# the short bass holes at 71.5 and 151.5 are reel changes too
R('S({"name":"oz","from":"open","to":"kalei","pal":"gold","pump":HARD,"layers":[','S({"name":"oz","from":"open","to":"kalei","pal":"gold","pump":HARD,"out":1,"layers":[')
R('S({"na ... [cut]
Sat Oct 31 13:09:28 PDT 2026
wrote shows/scenes/deadmau5 - Strobe (Special Features Remix).scene.json scenes 45 hits 35
deadmau5 - Strobe (Special Features Remix): 46 scenes, 35 hits, written into shows/deadmau5 - Strobe (Special Features Remix).json
  drain 2        345.2s      493      908    32.3%      18.1    0.20
  out            360.2s      350      441    32.4%      18.1    0.14
  away           367.6s      266      364    32.5%      18.1    0.16
  burn           382.6s      333      407    32.4%      18.1    0.05
  tail           390.2s        5       26    32.4%      18.1    0.02
  worst frame 2.10 ms; no scene reaches the sustained floor
deadmau5 - Strobe (Special Features Remix): 128.000 BPM, 210 bars, bar 0 at 0.136 s, holds []
music against the grid per 8 bars, ms (contrast): 0:-3(6.00)  8:-3(4.78)  16:-1(2.68)  24:-1(3.49)  32:+1(3.06)  40:+1(3.05)  48:-1(1.21)  56:-1(2.15)  64:+3(1.96)  72:+3(2.17)  80:+3(1.86)  88:+3(1.93)  96:-1(1.69)  104:-1(1.27)  112:+3(2.65)  120:+3(2.83)  128:-3(5.13)  136:-1(3.56)  144:+5(2.25)  152:+3(1.91)  160:+3(2.12)  168:+1(1.96)  176:+1(3.87)  184:+1(3.80)  192:+1(3.14)  200:-1(3.37)  208:+5(2.78)
worst 5 ms where the music is clear enough to say, mean +1.3 ms
bar 207.75  burn       shell max  54 mean   5.8   ears max 102 mean   9.0  sent  325  burn
bar 208.5   tail       shell max   0 mean   0.0   ears max  47 mean   1.6  sent   27  tail
tools/showkit/songs/cinema/final_g.png (1800, 1456)
```

You've hit your session limit · resets 5:10pm (America/Los_Angeles)
