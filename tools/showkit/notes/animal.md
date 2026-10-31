# What the animal builder ran and saw

Commands and their text output, in order, with long output cut. Images are left out; rerun the tools to see them. Cut off partway: the generator and treatment in the repo are the latest state.

I'll start by reading the brief.

```
$ date; ls -la "tools/showkit/"; ls -la "tools/showkit/songs/" 2>/dev/null
Sat Oct 31 12:39:05 PDT 2026
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
$ date; ls -la "tools/showkit/"; ls -la "tools/showkit/songs/" 2>/dev/null
Sat Oct 31 12:39:05 PDT 2026
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
$ cd "~/deadmau5 app"; KIT=tools/showkit; mkdir -p "$KIT/work/animal"; cat "$KIT/grid.py"; echo ------; cat "$KIT/fmt.py"; echo ------; cat "$KIT/sheet.py"; echo -----; cat "$KIT/songmap.py"; echo ----; cat "$KIT/spectro.py"; echo -----; cat "$KIT/spritetry.py"
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
$ cd "~/deadmau5 app"; cat "(scratch)/tiki/write_treatment.py"; ls -la shows/ | head -60; ls -la shows/scenes/ | head -60
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
$ cd "~/deadmau5 app"; KIT=tools/showkit; mkdir -p "$KIT/work/animal"; cat "$KIT/grid.py"; echo ------; cat "$KIT/fmt.py"; echo ------; cat "$KIT/sheet.py"; echo -----; cat "$KIT/songmap.py"; echo ----; cat "$KIT/spectro.py"; echo -----; cat "$KIT/spritetry.py"
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
$ cd "~/deadmau5 app"; cat "(scratch)/tiki/write_treatment.py"; ls -la shows/ | head -60; ls -la shows/scenes/ | head -60
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
$ cd "~/deadmau5 app"; KIT=tools/showkit; time python3 "$KIT/grid.py" scan "shows/deadmau5 & Wolfgang Gartner - Animal Rights.mp3" 2>&1 | tail -30
estimator: 128.000 BPM, first bar 1.874 s, tempo lock 0.821, bar lock 0.5370749281464556; song 375.0 s
refined over the whole song: spb 0.468751 = 128.000 BPM
first half 128.000 BPM, second half 128.012 BPM (these should agree within 0.05)
phase of the music against that grid per 8 bars, ms (flat = right; one 16th = 117 ms; contrast under 1.15 means sparse, ignore it):
  0:-7(6.58)  8:-5(6.25)  16:-5(5.52)  24:-5(5.19)  32:+5(7.12)  40:+5(5.82)  48:-1(4.06)  56:-1(3.82)  64:-1(3.79)  72:+1(3.79)  80:-5(4.05)  88:+1(4.23)  96:+3(7.50)  104:+1(8.33)  112:+1(4.15)  120:+1(3.86)  128:+1(4.25)  136:+1(4.09)  144:+1(3.51)  152:-3(3.82)  160:-7(5.09)  168:-7(4.98)  176:-7(5.68)  184:-7(5.34)  192:+7(3.87)
change per beat position, estimator's bar 1 at 1.874 s: 0:1.13 1:0.87 2:1.02 3:0.91  (the highest is where bars really start, 0 = estimator is right)
strongest phrase positions, in beats mod 32 from that bar 1: 28(1.61), 12(1.37), 22(1.31), 10(1.30), 4(1.27), 29(1.20)
biggest single changes (time, beat from bar 1, beat mod 4): 31.9s b64 m0; 46.9s b96 m0; 60.0s b124 m0; 89.5s b187 m3; 90.0s b188 m0; 90.5s b189 m1; 156.6s b330 m2; 157.5s b332 m0; 164.1s b346 m2; 171.6s b362 m2; 172.5s b364 m0; 180.0s b380 m0; 180.5s b381 m1; 186.6s b394 m2; 270.0s b572 m0; 273.7s b580 m0; 288.7s b612 m0; 292.5s b620 m0; 295.3s b626 m2; 299.5s b635 m3; 300.0s b636 m0; 316.9s b672 m0; 360.0s b764 m0; 360.5s b765 m1
suggested next: grid.py fold with --spb 0.468751 --anchor 1.874, decide the bar line, then grid.py write
python3 "$KIT/grid.py" scan  2>&1  2.28s user 0.80s system 111% cpu 2.758 total
tail -30  0.00s user 0.00s system 0% cpu 2.757 total
```

```
$ cd "~/deadmau5 app"; KIT=tools/showkit; python3 "$KIT/grid.py" fold "shows/deadmau5 & Wolfgang Gartner - Animal Rights.mp3" --spb 0.46875 --anchor 0.0 2>&1 | head -120; ls -la "shows/" | grep -i animal; ls -la shows/scenes | grep -i animal; ls shows/.mau5cache | head
bar 0 at 0.000 s, 128.000 BPM, 200 bars
bars 0-16   (16 steps, | every beat; one row per band)
   sub     @.  |%:  |@.  |%:     peak 0.75
   bass    @.  |@   |@.. |@      peak 1.30
   lowmid  @   |#   |@ . |#      peak 1.05
   mid     % : |@ : |@ - |* .    peak 1.67
   pres    % = |% - |@ = |= :    peak 1.89
   air     @ * |# * |@ * |- *    peak 1.96
bars 16-32   (16 steps, | every beat; one row per band)
   sub     @.  |%:  |@. .|%:     peak 0.75
   bass    @   |@   |@.-.|@      peak 1.29
   lowmid  @   |#   |@ + |%      peak 1.03
   mid     @ : |@ : |@ = |* :    peak 1.42
   pres    % = |% - |@ + |+ +    peak 1.66
   air     @ *.|# *.|@ #.|- +.   peak 1.84
bars 32-48   (16 steps, | every beat; one row per band)
   sub     %=-:|%=#:|*--@|#=::   peak 0.17
   bass    @.: |@.::|%:.=|@ :    peak 0.46
   lowmid  +.% |@ #-| # @|.-+    peak 0.95
   mid     * = |@ +-|-* %|=:+    peak 1.34
   pres    * = |@ =-|+-.=|#.=    peak 1.31
   air       % |%=@+|.#.@|#.@#   peak 0.88
bars 48-64   (16 steps, | every beat; one row per band)
   sub     @:=.|@-%.|=::@|:---   peak 0.52
   bass    %:: |@.=.|*-:=|#.-    peak 1.18
   lowmid  #:+ |@.#:|.#-@|--#.   peak 0.85
   mid     #.= |@ #:|-#-*|-:+    peak 1.27
   pres    @.- |@ +.|*+-=|+.*    peak 1.24
   air     @ * |% #.|*.+-|- *    peak 1.37
bars 64-80   (16 steps, | every beat; one row per band)
   sub     @:=.|@-*.|=:.%|--:-   peak 0.53
   bass    @.: |@.=.|*-:=|#:-.   peak 1.13
   lowmid  #.* |% #.|.%-@|=:*.   peak 0.84
   mid     #.- |@.#-|-#=+|=:+.   peak 1.00
   pres    @.- |@ *:|++-=|=.+    peak 1.16
   air     @ + |% #.|*.*-|= *.   peak 1.35
bars 80-96   (16 steps, | every beat; one row per band)
   sub     #.: |%:-.|@.:-|#::-   peak 0.72
   bass    %.. |@ * |@::.|@ -    peak 1.27
   lowmid  @:- |@.+ |@:: |@.%    peak 0.77
   mid
... [cut] ...
mid     @--:|::.-|:-:.|-:.:   peak 0.11
   pres    @.::|=:::|*..:|*.:.   peak 0.07
   air     @ . |#   |#   |*      peak 0.14
-rw-r--r--@  1 jones  staff  15003733 Oct 31 12:37 deadmau5 & Wolfgang Gartner - Animal Rights.mp3
Kaskade feat. deadmau5 - I Remember.wav
Kaskade feat. deadmau5 - I Remember.wav.src
TIKI TIKI - Slowed.wav
TIKI TIKI - Slowed.wav.src
deadmau5 & Wolfgang Gartner - Animal Rights.wav
deadmau5 & Wolfgang Gartner - Animal Rights.wav.src
deadmau5 - FN Pig.wav
deadmau5 - FN Pig.wav.src
deadmau5 - Harder Better Faster Stronger.wav
deadmau5 - Harder Better Faster Stronger.wav.src
```

```
$ cd "~/deadmau5 app"; KIT=tools/showkit; B="deadmau5 & Wolfgang Gartner - Animal Rights"; time python3 "$KIT/grid.py" write "$B" --spb 0.46875 --anchor 0.0 2>&1 | tail -8; python3 "$KIT/grid.py" check "$B"; python3 "$KIT/songmap.py" "$B"; python3 "$KIT/spectro.py" "$B" "$KIT/work/animal/full.png"
    4:30.00-4:45.00  lvl1  matrix     {}
    4:45.00-5:00.00  lvl1  earspin    {'period': 2.4}
    5:00.00-5:15.00  lvl1  chase      {'period': 2.2}
    5:15.00-5:30.00  lvl1  scanner    {'period': 3.75}
    5:30.00-5:45.00  lvl1  sparkle    {}
    5:45.00-6:00.00  lvl1  spiral     {'period': 6.0}
    6:00.00-6:15.00  lvl0  wave       {'period': 5.0, 'length': 0.8}
wrote shows/scenes/deadmau5 & Wolfgang Gartner - Animal Rights.beats: 801 beats, 200 bars, bar 0 at 0.000 s, 128.000 BPM
python3 "$KIT/grid.py" write "$B" --spb 0.46875 --anchor 0.0 2>&1  0.90s user 0.21s system 94% cpu 1.179 total
tail -8  0.00s user 0.00s system 0% cpu 1.179 total
deadmau5 & Wolfgang Gartner - Animal Rights: 128.000 BPM, 201 bars, bar 0 at 0.000 s, holds []
music against the grid per 8 bars, ms (contrast): 0:-5(6.11)  8:-5(6.19)  16:-5(4.91)  24:-5(4.75)  32:+1(8.07)  40:+5(6.37)  48:-1(4.06)  56:-1(4.11)  64:-1(3.80)  72:-1(3.87)  80:-5(4.29)  88:-5(4.67)  96:+5(6.22)  104:+1(9.02)  112:-1(3.97)  120:-1(3.88)  128:+1(4.15)  136:+1(4.10)  144:+1(3.51)  152:-1(3.65)  160:-7(5.12)  168:-7(4.93)  176:-7(5.71)  184:-7(5.46)  192:+7(3.30)
worst 7 ms where the music is clear enough to say, mean -1.3 ms
deadmau5 & Wolfgang Gartner - Animal Rights: 201 bars, 1.88 s a bar, 375.0 s
 bar     t   E  B  M  H  notes       change
   0    0.0   6  5  2  3  C F A       
   1    1.9   6  6  3  5  C F A       
   2    3.8   6  6  2  4  C F A       
   3    5.6   6  6  3  5  C F A       
   4    7.5   6  6  2  4  C F A       
   5    9.4   6  6  3  5  C F A       
   6   11.2   6  6  2  4  C F A       
   7   13.1   6  6  3  5  C F A       
   8   15.0   6  6  2  4  C F A       
   9   16.9   6  6  3  5  C F A       
  10   18.8   6  6  2  4  C F A       
  11   20.6   6  6  3  5  C F A       
  12   22.5   6 
... [cut] ...
 
 189  354.4   6  6  3  5  C F A       
 190  356.2   6  6  3  4  C F A       
 191  358.1   7  6  4  6  C F A       >>
 192  360.0   4  0  5  4  A D B       >>
 193  361.9   2  0  4  1  A D B       >>
 194  363.8   0  0  1  0  A D B       >>
 195  365.6   0  0  0  0  D A B       
 196  367.5   0  0  0  0  D A B       
 197  369.4   0  0  0  0  D A B       
 198  371.2   0  0  0  0  D A B       
 199  373.1   0  0  0  0  A D A#      
 200  375.0   0  0  0  0  C C# D      
tools/showkit/songs/animal/full.png
```

```
$ cd "~/deadmau5 app"; KIT=tools/showkit; B="deadmau5 & Wolfgang Gartner - Animal Rights"; W="$KIT/work/animal"; python3 "$KIT/spectro.py" "$B" "$W/z0.png" 12 36; python3 "$KIT/spectro.py" "$B" "$W/z1.png" 30 52; python3 "$KIT/spectro.py" "$B" "$W/z2.png" 48 68; python3 "$KIT/spectro.py" "$B" "$W/z3.png" 92 116; python3 "$KIT/spectro.py" "$B" "$W/z4.png" 126 164;
tools/showkit/songs/animal/z0.png
tools/showkit/songs/animal/z1.png
tools/showkit/songs/animal/z2.png
tools/showkit/songs/animal/z3.png
tools/showkit/songs/animal/z4.png
```

```
$ mkdir -p tools/showkit/songs/animal; cat > tools/showkit/songs/animal/rhythm.py <<'EOF'
#!/usr/bin/env python3
# rhythm.py lo hi [band ...] : per bar, 16 steps, onset or level per band, so stabs can be read off.
import sys, numpy as np, os, re
KIT = "tools/showkit"
WORK = KIT + "/work"
p = WORK + "/" + re.sub(r"\W+", "_", "deadmau5 & Wolfgang Gartner - Animal Rights.mp3") + ".env.npz"
z = np.load(p)
tt = z["tt"]
spb = 0.46875
lo, hi = ... [cut]
  28 @   |@   |@.=.|@      @   |*   |@ = |*      % - |- : |@ + |. -    @ + |= - |@ + |- @ 
  29 @.  |@   |@...|%.     %   |%   |% - |%      @ : |* - |@ +.|: .    @ + |* = |@ #.|- : 
  30 %   |@   |@ =.|@      @   |*   |@ = |#      % - |- : |@ = |. -    @ + |= - |@ * |- @ 
  31 @.  |@   |@...|%.     %   |%   |# - |#      @ : |* . |% - |: .    @ + |* - |% - |- : 
  32 -   |=   |-  .|- .    @ # |# #=| @ *|..@    @ . |= :.|=: *|- *    @   |+ ..|=: -|+ - 
  33 - . |=  .|=  .|-      % @ |%.@=| @ *|.@.    # * |@ #=|=* @|-*     + = |@ =+|+= *|*::.
  34 -   |= ..|-  .|- .      * |@ %=| @ @|  @    - - |@ #:|-* @|= @    * = |@ =-|+= *|* % 
  35 -   |:  .|-  .|-      # @ |% *=| + @| #     @ % |@ %=|-@ @|-+     * * |@ ++|+= +|#.:.
  36 -   |= . |-   |- .    : =.|@ #+| # @|  @    = = |@.%-|-* @|=.@    * + |@.+-|+=:*|*.% 
  37 - . |- . |-  .|=      % % |% #-|:+ @| %     @ % |@ %=|:@.@|=*     * * |@ ++|*=.+|%:- 
  38 =   |- . |-  .|-..    -.# |% @.|.# @|  @    : - |@.#=|:* %|= @    * * |@.+-|+-:*|#.% 
  39 - . |:  .|-   |-      #.@ |@ @-|.% @| +     @ # |@ ++|:% @|==     * * |@.+=|=-.-|#:: 
  40 =   |=  .|-: :|- .    :.* |+ *-|.@ @|  #    : : |% +-|:* #|=.@    + : |# ::|+-.=|* * 
  41 - ..|- . |:: -|= .    %.@ |@ =:| % %| * .   @ + |@ #=|-+ #|-=     + + |@ +:|++.=|+-: 
  42 =   |- . |-  .|= :     .# |* *:| @ @|  +    -.: |@ -=|-= #|= @    + + |@ =:|+= -|* = 
  43 - : |:  .|:. .|-.     # @ |@ *=| +.#|...    #.+ |#.+-|:= #|-=     = + |% -.|=: -|=:..
  44 =   |-   |-. -|- .    . = |+.+=| * #|-.*    -.: |%.:.|=: *|= =    + : |% : |=: .|= . 
  45 : . |- . |-. :|=      *.=.|@.*=| = +|..@    = - |*.- |:- -|- =.   - : |=  .|:  .|- . 
  46     | .  |    |       .-  |-. :|  : | ..     .  |:  .|. . | .         |    |    |    
  47     |    |    |.      .  .|    |    |. .    .. .|. ..|.:. |#      
... [cut] ...
 +    :.= |% %-|.#:@|  @    :.+ |- @:|:%:#| .%    #.+ |= +:|+=:+|- @ 
  61 %.: |@ +:|-= +|#:..   #:= |*.%.|:+ @| #:.   @:= |* #-| @.+|.=:.   @.- |* +:|-+:.|-:: 
  62 = . |+.  |+.. |@.:    .. .|:.  | . -|@. :   ....|... |. + |       +.. |= . |= =.|: = 
  63 %:  |%:  |=.*.|*...   -:  |*.  | :%.| ...   -.  |-.. |: % |..     +.. |- : |=.# |:   
  64 @.. |@ *:|+-.:|= =    @:# |* +.|.@.@|..*    *.. |:.:.|.=:=|  %    @   |- : |-=.=|- # 
  65 @.: |% -.|==.+|+..:   % % |# * | @ @|.+.    + - |+ *:|.+.-|:=     %.= |* *:|=+:.|:=. 
     bass                  lowmid                mid                   pres
```

```
$ cd "~/deadmau5 app"; wc -l mau5scene.py mau5fx.py mau5engine.py mau5show.py mau5preview.py; sed -n 1,200p mau5scene.py
    1344 mau5scene.py
     992 mau5fx.py
    1388 mau5engine.py
    1000 mau5show.py
     214 mau5preview.py
    4938 total
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
and pausing cost nothing.  And the show stays in sync from the
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
$ cd "~/deadmau5 app"; sed -n 200,760p mau5scene.py
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
mp"]["pat"], s["pump"]["step"])
            if gap < 0.5 - 1e-9 and span > 4.0:
                errs.append("%s: the pump beats every %.3g beats, faster than "
                            "8th notes" % (what, gap))
        for j, L in enumerate(s["layers"]):
            layer_checks(L, "%s layer %d" % (what, j), span)
        if texts(s["layers"]) > 1:
            errs.append("%s: two text layers at once" % what)

    for x in hits:
        what = "hit %s" % x["name"]
        if len(x["layers"]) > MAX_HIT_LAYERS:
            errs.append("%s has %d layers, %d at most" % (what, len(x["layers"]),
```

```
$ cd "~/deadmau5 app"; sed -n 760,1344p mau5scene.py
            errs.append("%s has %d layers, %d at most" % (what, len(x["layers"]),
                                                          MAX_HIT_LAYERS))
        if not 0 <= x["at"] <= nb:
            errs.append("%s at bar %g is outside the song" % (what, x["at"]))
        if x["beats"] <= 0:
            errs.append("%s lasts no time" % what)
        for j, L in enumerate(x["layers"]):
            layer_checks(L, "%s layer %d" % (what, j), x["beats"])
        # what overlaps it
        a0, a1 = 4.0 * x["at"], 4.0 * x["at"] + x["beats"]
        over = [y for y in hits if 4.0 * y["at"] < a1 and a0 < 4.0 * y["at"] + y["beats"]]
        # the most that are active at once: test at each start inside
        most = max(sum(1 for y in over if 4.0 * y["at"] <= q < 4.0 * y["at"] + y["beats"])
                   for q in [a0] + [4.0 * y["at"] for y in over if a0 <= 4.0 * y["at"] < a1])
        if most > MAX_HITS_AT_ONCE:
            errs.append("%s overlaps %d other hits" % (what, most - 1))
        t = texts(x["layers"])
        if t:
            others = sum(texts(y["layers"]) for y in over if y is not x)
            under = [s for s in scenes if 4.0 * s["from"] < a1 and a0 < 4.0 * s["to"]]
            others += max([texts(s["layers"]) for s in under] or [0])
            if t + others > 1:
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
        i1 =
... [cut] ...
  if a.cmd == "bars":
        _, music, _ = _show_and_music(names([a.show])[0])
        rows = bar_stats(music)
        lo = a.lo if a.lo is not None else 0
        hi = a.hi if a.hi is not None else len(rows)
        for r in rows[lo:hi]:
            print(_row(r))
    elif a.cmd == "compile":
        for base in names(a.show):
            _, music, _ = _show_and_music(base)
            print_marks(base, music)
            attach(base)
    elif a.cmd == "check":
        for base in names(a.show):
            check(base, fps=a.fps)
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

```
$ cd "~/deadmau5 app"; grep -n "SPRITES\|sprites.json\|class Sprite\|class Eyes\|class TextScroll\|def _text_bitmap" -n mau5fx.py mau5engine.py mau5show.py mau5scene.py | head -40; grep -n '"eyes"\|"sprite"' mau5fx.py mau5engine.py | head
mau5fx.py:134:SPRITES = {
mau5fx.py:249:# Sprites a song brings with it: shows/scenes/<song>.sprites.json, {name: [rows]},
mau5fx.py:256:        sheets = sorted(f for f in os.listdir(d) if f.endswith(".sprites.json"))
mau5fx.py:266:                SPRITES[name] = list(rows)
mau5fx.py:275:    rows = SPRITES[name_or_rows] if isinstance(name_or_rows, str) else name_or_rows
mau5fx.py:567:class Sprite(GridEffect):
mau5fx.py:584:class SpriteFlipbook(GridEffect):
mau5fx.py:989:    for name in sorted(SPRITES):
mau5scene.py:640:    from mau5fx import SPRITES
mau5scene.py:726:                    if one not in SPRITES:
mau5engine.py:35:from mau5fx import FONT5x7, SPRITES
mau5engine.py:580:def _text_bitmap(text, spacing=1):
mau5engine.py:625:    rows = SPRITES[name]
mau5engine.py:674:class TextScroll(Preset):
mau5engine.py:704:class SpriteShow(Preset):
mau5engine.py:743:class Eyes(Preset):
mau5engine.py:713:    name = "sprite"
mau5engine.py:714:    params = {"sprite": "smile", "color": (0, 255, 255), "bg": (0, 0, 0),
mau5engine.py:722:        names = self.p["sprite"].split("|")
mau5engine.py:745:    name = "eyes"
mau5fx.py:165:    "eyes": [
mau5fx.py:587:    def __init__(self, helmet, sprites=("eyes", "wink"), fps=2.0, col=None,
```

```
$ cd "~/deadmau5 app"; sed -n 760,1344p mau5scene.py
            errs.append("%s has %d layers, %d at most" % (what, len(x["layers"]),
                                                          MAX_HIT_LAYERS))
        if not 0 <= x["at"] <= nb:
            errs.append("%s at bar %g is outside the song" % (what, x["at"]))
        if x["beats"] <= 0:
            errs.append("%s lasts no time" % what)
        for j, L in enumerate(x["layers"]):
            layer_checks(L, "%s layer %d" % (what, j), x["beats"])
        # what overlaps it
        a0, a1 = 4.0 * x["at"], 4.0 * x["at"] + x["beats"]
        over = [y for y in hits if 4.0 * y["at"] < a1 and a0 < 4.0 * y["at"] + y["beats"]]
        # the most that are active at once: test at each start inside
        most = max(sum(1 for y in over if 4.0 * y["at"] <= q < 4.0 * y["at"] + y["beats"])
                   for q in [a0] + [4.0 * y["at"] for y in over if a0 <= 4.0 * y["at"] < a1])
        if most > MAX_HITS_AT_ONCE:
            errs.append("%s overlaps %d other hits" % (what, most - 1))
        t = texts(x["layers"])
        if t:
            others = sum(texts(y["layers"]) for y in over if y is not x)
            under = [s for s in scenes if 4.0 * s["from"] < a1 and a0 < 4.0 * s["to"]]
            others += max([texts(s["layers"]) for s in under] or [0])
            if t + others > 1:
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
        i1 =
... [cut] ...
  if a.cmd == "bars":
        _, music, _ = _show_and_music(names([a.show])[0])
        rows = bar_stats(music)
        lo = a.lo if a.lo is not None else 0
        hi = a.hi if a.hi is not None else len(rows)
        for r in rows[lo:hi]:
            print(_row(r))
    elif a.cmd == "compile":
        for base in names(a.show):
            _, music, _ = _show_and_music(base)
            print_marks(base, music)
            attach(base)
    elif a.cmd == "check":
        for base in names(a.show):
            check(base, fps=a.fps)
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

```
$ cd "~/deadmau5 app"; grep -n "SPRITES\|sprites.json\|class Sprite\|class Eyes\|class TextScroll\|def _text_bitmap" -n mau5fx.py mau5engine.py mau5show.py mau5scene.py | head -40; grep -n '"eyes"\|"sprite"' mau5fx.py mau5engine.py | head
mau5fx.py:134:SPRITES = {
mau5fx.py:249:# Sprites a song brings with it: shows/scenes/<song>.sprites.json, {name: [rows]},
mau5fx.py:256:        sheets = sorted(f for f in os.listdir(d) if f.endswith(".sprites.json"))
mau5fx.py:266:                SPRITES[name] = list(rows)
mau5fx.py:275:    rows = SPRITES[name_or_rows] if isinstance(name_or_rows, str) else name_or_rows
mau5fx.py:567:class Sprite(GridEffect):
mau5fx.py:584:class SpriteFlipbook(GridEffect):
mau5fx.py:989:    for name in sorted(SPRITES):
mau5scene.py:640:    from mau5fx import SPRITES
mau5scene.py:726:                    if one not in SPRITES:
mau5engine.py:35:from mau5fx import FONT5x7, SPRITES
mau5engine.py:580:def _text_bitmap(text, spacing=1):
mau5engine.py:625:    rows = SPRITES[name]
mau5engine.py:674:class TextScroll(Preset):
mau5engine.py:704:class SpriteShow(Preset):
mau5engine.py:743:class Eyes(Preset):
mau5engine.py:713:    name = "sprite"
mau5engine.py:714:    params = {"sprite": "smile", "color": (0, 255, 255), "bg": (0, 0, 0),
mau5engine.py:722:        names = self.p["sprite"].split("|")
mau5engine.py:745:    name = "eyes"
mau5fx.py:165:    "eyes": [
mau5fx.py:587:    def __init__(self, helmet, sprites=("eyes", "wink"), fps=2.0, col=None,
```

```
$ cd "~/deadmau5 app"; sed -n 575,800p mau5engine.py; sed -n 245,300p mau5fx.py; python3 - <<'EOF'
import sys
sys.path.insert(0,'.')
import mau5engine as E, numpy as np
h=E.Helmet()
print('n',h.n,'shell',h.shell.sum(),'ears',h.ears.sum())
s=h.shell
print('shell px',h.px[s].min(),h.px[s].max(),'py',h.py[s].min(),h.py[s].max())
# Histogram of y
ys=h.py[s]
hist,edges=np.histogram(ys,bins=14,range=(-110,180))
for c,e in zip(hist,edges): print('y %6.1f %d'%(e,c))
print('ear1 x',h.px[h.ear1].min(),h.px[h.ear1].max(),'y',h.py[h.ear1].min(),h.py[h.ear1].max())
print('ear2 x',h.px[h.ear2].min(),h.px[h.ear2].max(),'y',h.py[h.ear2].min(),h.py[h.ear2].max())
print('nfa',h.nfa[s].min(),h.nfa[s]. ... [cut]
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
 librosa output."""
        with open(path, "r", encoding="utf-8") as fh:
            txt = fh.read().strip()
        if txt.startswith("["):
n 621 shell 398 ears 223
shell px -170.94 170.95 py -111.27 167.77
y -110.0 20
y  -89.3 28
y  -68.6 8
y  -47.9 6
y  -27.1 2
y   -6.4 2
y   14.3 12
y   35.0 22
y   55.7 68
y   76.4 34
y   97.1 64
y  117.9 30
y  138.6 68
y  159.3 4
ear1 x -388.21 -55.76 y 51.8 383.94
ear2 x 55.56 387.42 y 54.72 384.91
nfa 0.16035751702193546 0.8399804407362015 nel 0.0 1.0
fa -44.99832414579261 45.0
er shell 0.03929154446196175 1.0 ea 0.004374306928113342 0.9891721577339918
```

```
$ cd "~/deadmau5 app"; R=tools/showkit/songs/animal/rhythm.py; python3 $R 0 4 od bass lowmid mid pres air; python3 $R 14 20 od bass lowmid mid pres air; python3 $R 66 112 od bass lowmid mid pres
   0     |@   |%   |@          |#   |@   |*        - |= : |@ - |. .      + |= = |@ = |- -      * |+ @ |@ % |- % 
   1 @.  |@   |@...|%.     %   |%   |% - |%      @ : |# - |@ +.|- :    @ = |* = |@ #.|- -    @ @ |# * |% @ |. % 
   2 @   |@   |%   |@      @   |*   |@   |#      % - |- : |@ - |. .    @ + |= = |@ = |- -    @ * |+ @ |@ % |- % 
   3 @.  |@   |@...|%.     %   |#   |% : |%      @ : |# - |@ +.|- :    @ = |* = |@ #.|- -    @ @ |# * |% @ |. % 
     bass                  lowmid                mid                   pres                  air                
  14 @   |@   |%.  |@      @   |*   |@   |*      % - |- : |@ - |. .    @ + |= = |@ = |- -    @ * |+ @ |@ % |- % 
  15 @.  |@   |@...|%.     %   |%   |% - |%      @ : |* - |@ +.|: .    @ = |* = |@ #.|- -    @ @ |# * |% @ |. # 
  16 @   |@   |%.=.|@      @   |*  .|@ = |*      % . |- . |+ - |. :    @   |- . |+ - |- %    @ - |- = |* + |- %.
  17 @.  |@   |@...|%.     %   |#.  |% : |%      * : |* : |% =.|- .    % - |* - |@ # |- :    @ %.|# *:|% @ |. =:
  18 %   |@   |@.=.|@      @   |*   |@ = |#      # : |- : |# = |. :    @ + |= - |@ + |- @    @ *:|+ @:|@ %:|- @.
  19 @.  |@   |@...|%.     %   |%   |% - |%      @ : |* : |@ =.|- .    @ = |* = |@ #.|- :    @ @:|# *:|% @ |. =:
     bass                  lowmid                mid                   pres                  air                
  66 -.. |@ =.|+-=+|=.-     .= |# #.| @.@|- %    ..- |- #.|:=:+|  *    + - |= % |==.*|: # 
  67 @ : |@.=:|@: =|* -    % # |% # |==:-|*.@.   * = |* %*|=@ -|..+    # = |* *.|=# .|- - 
  68 --  |@ *.|*:++|= -    ..= |# %-| @:@|..@    :.- |- @.|-=-=|  *    % :.|= *.|==.=|: # 
  69 @.: |@.*:|=-.%|=:::   %:- |%.%-| * %|:*.:   #:- |* #:|.#.=|.- .   %.- |* +:|++-.|:-. 
  70 : ::|-.  |=.. |@.       ..|:.. | . -|@. :   :.  |:.  |- + |.      = . |- . 
... [cut] ...
 -    . - |@ -.| @ *|  @      . |@ -.|-:--|- -    . : |% -:|.:::|- = 
 107 . - |: .:| - :| =     * % |@ =-| @ #| #+    # - |# -.|--:-|:-:    - = |* --|:-.:|::  
 108   . |: :.| - =|  -    : - |# --| % :|..@    . . |@ - |=.:-|- :    . : |% :.|::..|: = 
 109 : : |: -.| : +|  :    % : |@ ==| % *|  @    = - |* : |-:..|- -    - = |* -:|-:..|: : 
 110 * = |# + |# * |* -    @ +.|@.#.|@ =.|@ *.   = - |+ : |= = |+ -    + = |% - |@ = |* = 
 111 * *-|= +-|= *:|= +.   @ @ |@ @ |@ @.|% @:   # - |+ = |* - |= -.   @ + |+ = |* - |- : 
     bass                  lowmid                mid                   pres
```

```
$ cd "~/deadmau5 app"; R=tools/showkit/songs/animal/rhythm.py; python3 $R 112 164 od bass lowmid mid pres; python3 $R 186 196 od bass lowmid mid pres; python3 "$R" 44 49 lvl sub bass lowmid mid pres air
 112 %.. |@ * |*:--|=.=    %.= |% #.| #.%|: @    =.: |. :.|:=::|: =    +.. |- . |=-..|= + 
 113 @:: |%.=.|+-:*|*. .   %:- |#.#.|.+ %| =     -.= |=.-.|.# :|:: .   *.: |+ -.|+-: |-.. 
 114 =.. |@ -.|*-:-|+ =    ..+ |# * | *:@| .%    ..: |: -.|:*:=|: #    =.- |- -.|+-::|= % 
 115 @.: |% = |@: =|* =    *:% |* # |-=::|*.@.   +:: |+ #-|-@ :|..=    #.: |+ *.|-#  |- - 
 116 -.: |@ *.|+=:-|+.+     :* |@ +.| @.@|. @    :.: |: +:|.=:+|:.%    # - |- +.|=-:-|- @ 
 117 @:: |% - |-=.-|+.:.   % + |@ *.| @ @| +:.   #:- |+ *:|.#:+|.+ .   %.- |+ =.|=+:.|--..
 118 :...|+.  |= . |@..     ..:|... | . -|%. .   :.  |:.  |-.* |=.     * ..|- . |= + |# + 
 119 @:  |%.  |+.-:|+ .    =.  |=   | .@ |.:     +.  |:.  |-.#.| . .   # . |- ..|=.+ |:.. 
 120 @.. |@ -.|+-:=|* +    @.* |+ %-| @.@|:.@    #.: |- :.|:=:*|: %.   %.. |- :.|==.+|- % 
 121 @.. |%.= |--.+|*=..   @ * |@.#:| # %|.#..   # + |+ *.|:*.+|.-..   @ - |+ +.|+*:.|--. 
 122 -:: |@ =.|+:++|+ =     .= |% #:| *:#|. @    :.= |- *.|:*.+|: +    + - |- @.|=-.+|- # 
 123 @...|@.* |@: +|* -    #.* |@ # |==:-|*.@.   #.= |+ %=|=@ -|..+    #.- |+ *.|=# .|- - 
 124 -:  |@ +-|+:-=|=.=    ..+.|% %-| #:@|  @    :.= |- #:|:+:=|- +    #.-.|- *:|==:=|= * 
 125 @=: |@ +.|-:.#|*...   #.* |+ %:|.# @| + :   * - |+ *-| #.=|.=.    %.- |* *:|=+::|:-: 
 126 = . |+.  |+.. |@.:    .. .|-.  | . -|@. .    . .|..  |. + |=      -.. |= . |=.= |* = 
 127 @:  |#:  |=.+:|::::   =:  |+.  | :@ |   .   -.. |:.. |:.* |       +.. |= : |=.+ |.   
 128 #.: |@ +.|*:-*|# +    %:: |% %-|:#.@|:.@    +.- |. : |:=.-|: -    *.. |- . |=-.-|= # 
 129 @.:.|%.=.|=-:*|*::-   #.- |#.%.|:+ @| =.    =.= |= -.|.* =|.: .   %.: |+ -.|+=:.|-...
 130 =.: |@ +.|*-:=|= =    :.- |# % |:*.@| .@    .:= |: =:|:+:=|: *    *.= |- -.|+-:=|= # 
 131 @.: |% = |@. +|* -    #.+ |# @:|:=:-|*.@    =.- |= *-|-@ -|..+    
... [cut] ...
|=+-+|+-#=   ++#+|#+**|**+#|#+*+   +=+=|#==+|++=+|#+++   +-+-|+=++|=+=+|+++*
  46     |    |    |           |    |    |       -=-:|=:::|:.:.|....   ++++|++=+|+===|====   +++=|++++|++++|+++=   =+==|===+|++++|****
  47     |    |    |.:         |    |    |.      .. .| .  |    |       ==-=|--=-|---:|####   +===|====|-==-|+++=   ****|*+++|+++=|--. 
  48 *#: |*+#%|%**%|%+.    +-- |= =+|+:+=|+.=    =*#:|= #%|-+**|=.%.   -=+-|= **|:-**|=.+.   --++|+.=+|-:==|+.+:   +-++|#:==|+.==|# = 
     sub                   bass                  lowmid                mid                   pres                  air
```

```
$ cd "~/deadmau5 app"; KIT=tools/showkit; W=$KIT/work/animal; python3 - <<'EOF'
import sys
sys.path.insert(0,'.')
import mau5engine as E, numpy as np
from PIL import Image, ImageDraw
h=E.Helmet()
S=2
W,H=800,900
im=Image.new('RGB',(W,H),(0,0,0)); d=ImageDraw.Draw(im)
def P(x,y): return (W/2+x*S*0.5*1.1, H-40-(y+120)*S*0.5*1.1) 
# grid lines each 50mm
for y in range(-100,400,50):
    a=P(-400,y); b=P(400,y); d.line([a,b],fill=(40,40,40)); d.text((5,a[1]),str(y),fill=(120,120,120))
for x in range(-350,400,50):
    a=P(x,-120); b=P(x,400); d.line([a,b],fill=(40,40,40)); d.text((a[0],H-20),str(x),fil ... [cut]
full.png
ledmap.png
rhythm.py
z0.png
z1.png
z2.png
z3.png
z4.png
bar 2       hush           shell max  17 mean   0.0   ears max  15 mean   2.1   embers
bar 5       hook           shell max 130 mean  13.3   ears max 224 mean  70.3   hook · LIT
bar 5.25    gap            shell max 232 mean  41.8   ears max 135 mean  43.1   hook · LIT
bar 26      stop           shell max 124 mean   2.5   ears max   0 mean   0.0   stop
bar 31      verse          shell max 100 mean   9.2   ears max  98 mean  46.9   verse · VERSE
bar 39      idol           shell max 130 mean  24.0   ears max 224 mean  77.0   big · IDOL
bar 39.25                  shell max 232 mean  48.7   ears max 135 mean  46.5   big · IDOL
bar 75      sunset         shell max 130 mean  26.6   ears max 224 mean  72.1   sunset · SUNSET
bar 107     duel           shell max 130 mean  10.9   ears max 255 mean  78.6   duel · DUEL
bar 153     final          shell max 249 mean  94.1   ears max 235 mean  96.3   final · FINAL
bar 8       hook           shell max  56 mean  11.6   ears max 153 mean  32.1   hook
bar 178     out            shell max  17 mean   3.6   ears max  47 mean   1.6   out
tools/showkit/songs/animal/tiki_ref.png (1800, 490)
```

```
$ cd "~/deadmau5 app"; KIT=tools/showkit; W=$KIT/work/animal; B="deadmau5 & Wolfgang Gartner - Animal Rights"; python3 "$KIT/spectro.py" "$B" "$W/z5.png" 52 57; python3 "$KIT/spectro.py" "$B" "$W/z6.png" 45 50; python3 "$KIT/spectro.py" "$B" "$W/z7.png" 80 84; python3 "$KIT/spectro.py" "$B" "$W/z8.png" 108 113; date
tools/showkit/songs/animal/z5.png
tools/showkit/songs/animal/z6.png
tools/showkit/songs/animal/z7.png
tools/showkit/songs/animal/z8.png
Sat Oct 31 12:43:40 PDT 2026
```

```
$ cd "~/deadmau5 app"; grep -n "sprite\|rate\b" remote/offline/engine.js | head -30; grep -n "class Sprite\|SpriteShow\|\"|\"\|'|'" remote/offline/*.js | head; KIT=tools/showkit; ls -la "$KIT/work/"; ls shows/scenes | grep sprites; date
168:function spriteBitmap(fonts, name) {
169:  const rows = fonts.sprites[name];
457:// mau5engine.SpriteShow says what dx, dy, vx, vy, wx, wy, wf and rate do.
458:def('sprite', { sprite: 'smile', color: [0, 255, 255], bg: [0, 0, 0],
461:                wx: 0.0, wy: 0.0, wf: 0.0, rate: 0.0 },
463:    const names = String(this.p.sprite).split('|');
464:    const at = this.p.rate > 0 ? pmod(Math.floor(t * this.p.rate), names.length) : 0;
465:    const bm = spriteBitmap(this.fonts, names[at]);
595:def('confetti', { rate: 14.0, fade: 0.55, sat: 0.9 },
598:    const step = 1.0 / Math.max(this.p.rate, 0.1);
688:def('sparkle', { bed: [40, 0, 60], glitter: [255, 255, 255], density: 0.10, rate: 7.0 },
692:    const k = Math.trunc(t * this.p.rate);
968:              textBitmap, glyphBitmap, digitBitmap, spriteBitmap, fract, pmod,
remote/offline/engine.js:457:// mau5engine.SpriteShow says what dx, dy, vx, vy, wx, wy, wf and rate do.
remote/offline/engine.js:463:    const names = String(this.p.sprite).split('|');
remote/offline/show.js:152:    const key = name + '|' + JSON.stringify(params);
total 32920
drwxr-xr-x@ 22 jones  wheel      704 Oct 31 12:39 .
drwxr-xr-x@ 11 jones  wheel      352 Oct 31 12:38 ..
-rw-r--r--@  1 jones  wheel  1368864 Oct 31 12:39 Kaskade_feat_deadmau5_I_Remember_mp3.env.npz
drwxr-xr-x@ 15 jones  wheel      480 Oct 31 12:43 animal
drwxr-xr-x@ 26 jones  wheel      832 Oct 31 12:44 chords
drwxr-xr-x@ 12 jones  wheel      384 Oct 31 12:44 cinema
-rw-r--r--@  1 jones  wheel  2566536 Oct 31 12:39 deadmau5_FN_Pig_mp3.env.npz
-rw-r--r--@  1 jones  wheel  1445752 Oct 31 12:39 deadmau5_Harder_Better_Faster_Stronger_mp3.env.npz
-rw-r--r--@  1 jones  wheel  1305528 Oct 31 12:39 deadmau5_Moar_Ghosts_n_Stuff_mp3.env.npz
-rw-r--r--@  1 jones  wheel  2429056 Oct 31 12:39 
... [cut] ...
 1 jones  wheel   823816 Oct 31 12:37 deadmau5_The_Veldt_mp3.env.npz
-rw-r--r--@  1 jones  wheel  1812048 Oct 31 12:39 deadmau5_Wolfgang_Gartner_Animal_Rights_mp3.env.npz
drwxr-xr-x@ 17 jones  wheel      544 Oct 31 12:43 fnpig
drwxr-xr-x@ 14 jones  wheel      448 Oct 31 12:45 moarghosts
drwxr-xr-x@ 12 jones  wheel      384 Oct 31 12:43 radio
drwxr-xr-x@ 25 jones  wheel      800 Oct 31 12:45 remember
drwxr-xr-x@ 31 jones  wheel      992 Oct 31 12:44 robot
drwxr-xr-x@ 30 jones  wheel      960 Oct 31 12:45 veldt
drwxr-xr-x@ 18 jones  wheel      576 Oct 31 12:45 weapon
Sat Oct 31 12:45:43 PDT 2026
```

```
$ mkdir -p tools/showkit/songs/animal; cat > tools/showkit/songs/animal/write_sprites.py <<'EOF'
#!/usr/bin/env python3
# The zoo's sprites: run from the repo root. Rows drawn by hand, half of them mirrored.
import json
BASE = "deadmau5 & Wolfgang Gartner - Animal Rights"
def mirror(rows):      # the left half, mirrored into the right, centre col given by the row's own last char
    return [r + r[-2::-1] for r in rows]
def flip(rows):
    return [r[::-1] for r in rows]
S = {}
# Predator eyes on the dome, drawn on y_lo 40,  ... [cut]
16 sprites
tools/showkit/songs/animal/s1.png (1440, 338)
tools/showkit/songs/animal/s2.png (720, 338)
tools/showkit/songs/animal/s3.png (1440, 338)
tools/showkit/songs/animal/s4.png (720, 338)
```

```
$ cd "~/deadmau5 app"; python3 - <<'EOF'
import sys
sys.path.insert(0,'.')
import mau5engine as E, numpy as np
h=E.Helmet()
m=h.shell&(h.py<=30)
ys=np.round(h.py[m]/4)*4
for y in sorted(set(ys),reverse=True):
    xs=sorted(h.px[m][ys==y])
    print('%5.0f'%y, ' '.join('%4.0f'%x for x in xs))
# Grid map for 21x9 over y_lo..y_hi
lo,hi,xh=-108.,28.,171.
rows,cols=9,21
g=[['.' for _ in range(cols)] for _ in range(rows)]
for i in np.where(h.shell)[0]:
    ry=(hi-h.py[i])/(hi-lo)*rows; rx=(h.px[i]+xh)/(2*xh)*cols
    if 0<=ry<rows and 0<=rx<cols:
        g[int(ry)][int(rx)]='o'
print('\n'.join(''.join(r) for r in g))
lo,hi,xh=40.,170.,171.
rows,cols=8,21
g=[[0 for _ in range(cols)] for _  ... [cut]
   28 -170 -169 -166 -162 -156 -149  149  156  162  166  169  170
   12 -171  171
  -20 -170  170
  -36 -169 -167 -164  164  167  169
  -52 -164 -163 -160 -156  156  160  163  164
  -68 -159 -157 -155 -151 -145 -139  139  145  151  155  157  159
  -84 -151 -150 -147 -144 -138 -132 -125 -116  116  125  132  138  144  147  150  151
  -96 -142 -125 -110 -101  101  110  118  135  142
 -100 -141 -139 -135 -130 -118  -91   91  125  130  139  141
 -112 -132 -131 -129 -126 -121 -116 -109 -102  -94  -85  -75  -64  -54  -42  -30   30   42   54   64   75   85   94  102  109  116  121  126  129  131  132
.....................
o...................o
.....................
o...................o
o...................o
o...................o
oo.................oo
.ooo.............ooo.
.oooo...........oooo.
.....1331232123......
....5653233324465....
...431122121221134...
..332.212121212.233..
.4753333224223333574.
142212111121111212241
332121111121111121233
42221...........12224
```

```
$ cat > tools/showkit/songs/animal/write_treatment.py <<'EOF'
#!/usr/bin/env python3
# THE ZOO BREAKS OUT: writes the treatment for Animal Rights. Run from the repo root.
import sys, os
KIT = "tools/showkit"
sys.path.insert(0, KIT)
from fmt import save
BASE = "deadmau5 & Wolfgang Gartner - Animal Rights"
SPB = 0.46875
R16 = round(4 / SPB, 6)      # flip-book rate: one frame a 16th note
R8 = round(2 / SPB, 6)       # one frame an 8th note

# --- the horn riff, read off the track: 32 16ths from an even bar
EVEN = "..x...x.. ... [cut]
wrote shows/scenes/deadmau5 & Wolfgang Gartner - Animal Rights.scene.json scenes 43 hits 36
     168   315.00s  energy 0.72  bass 0.62 (punch 1.00)  mid 0.46  high 0.53
     169   316.88s  energy 0.64  bass 0.56 (punch 1.00)  mid 0.36  high 0.45
  again      bar 176
     175   328.12s  energy 0.66  bass 0.60 (punch 1.00)  mid 0.40  high 0.45
     176   330.00s  energy 0.70  bass 0.55 (punch 1.00)  mid 0.54  high 0.55
     177   331.88s  energy 0.67  bass 0.57 (punch 1.00)  mid 0.44  high 0.45
  last       bar 184
     183   343.12s  energy 0.66  bass 0.60 (punch 1.00)  mid 0.41  high 0.45
     184   345.00s  energy 0.67  bass 0.54 (punch 1.00)  mid 0.43  high 0.53
     185   346.88s  energy 0.64  bass 0.56 (punch 1.00)  mid 0.36  high 0.44
  gone       bar 192
     191   358.12s  energy 0.66  bass 0.59 (punch 1.00)  mid 0.41  high 0.47
     192   360.00s  energy 0.45  bass 0.08 (punch 0.39)  mid 0.52  high 0.34
     193   361.88s  energy 0.26  bass 0.00 (punch 0.11)  mid 0.35  high 0.13
deadmau5 & Wolfgang Gartner - Animal Rights: 43 scenes, 36 hits, written into shows/deadmau5 & Wolfgang Gartner - Animal Rights.json
Sat Oct 31 12:50:11 PDT 2026
```

```
$ cd "~/deadmau5 app"; KIT=tools/showkit; W=$KIT/work/animal; B="deadmau5 & Wolfgang Gartner - Animal Rights"; python3 "$KIT/sheet.py" "$B" "$W/a1.png" 3:dark 6:open 12:scan 20:scratch 28:light 30.5:light 33:alarm 42:alarm2 45:climb 46.5:riser 47.5:riser 47.9:gap 48:tiger 48.25:rip 49.56:stab 50.1:rest 54.5:siren 55:stab 56:ripR 60:tigerb 64:zebra 66:zebra 68.25:zgap 71:zsiren 80:herd 80.25:gap 84:herd 83.3:snort 90:herd2 2>&1 | tail -30; date
bar 3       dark           shell max   0 mean   0.0   ears max  21 mean   1.2   dark
bar 6       open           shell max  59 mean   5.1   ears max  26 mean   1.5   eyes open
bar 12      scan           shell max 104 mean   9.1   ears max  30 mean   1.7   scan
bar 20      scratch        shell max 115 mean  13.7   ears max  34 mean   1.9   scratch
bar 28      light          shell max 130 mean  19.4   ears max  58 mean   2.3   searchlight
bar 30.5    light          shell max 134 mean  10.8   ears max  73 mean   5.2   searchlight
bar 33      alarm          shell max 128 mean  19.9   ears max  54 mean  37.4   alarm
bar 42      alarm2         shell max 160 mean  29.4   ears max  60 mean  18.4   alarm 2
bar 45      climb          shell max 185 mean  34.0   ears max  89 mean  61.9   climb
bar 46.5    riser          shell max 222 mean  38.3   ears max  79 mean   4.3   riser
bar 47.5    riser          shell max 238 mean  41.3   ears max 137 mean  40.7   riser
bar 47.9    gap            shell max   0 mean   0.0   ears max   0 mean   0.0   riser
bar 48      tiger          shell max 255 mean  39.7   ears max 140 mean  25.2   tiger · RIP
bar 48.25   rip            shell max 128 mean  45.3   ears max 140 mean  23.2   tiger · RIP
bar 49.56   stab           shell max  76 mean  18.9   ears max  94 mean  20.8   tiger
bar 50.1    rest           shell max  76 mean  13.5   ears max  87 mean  16.0   tiger
bar 54.5    siren          shell max  98 mean   5.5   ears max 188 mean  18.4   tiger siren · CHIRP
bar 55      stab           shell max  32 mean   4.8   ears max  69 mean   3.7   tiger siren
bar 56      ripR           shell max 204 mean  33.5   ears max 140 mean  25.2   tiger b · RIP 2
bar 60      tigerb         shell max  76 mean  14.1   ears max 140 mean  24.9   tiger b
bar 64      zebra 
... [cut] ...
max 255 mean  43.2   ears max 120 mean   8.0   stampede · RIP 5
bar 80.25   gap            shell max 128 mean  43.7   ears max 120 mean   8.0   stampede · RIP 5
bar 84      herd           shell max 107 mean  20.4   ears max 120 mean   7.9   stampede
bar 83.3    snort          shell max 184 mean  43.3   ears max 120 mean  32.3   stampede · SNORT
bar 90      herd2          shell max 107 mean  21.4   ears max 120 mean   7.9   stampede 2
tools/showkit/songs/animal/a1.png (1800, 1225)
Sat Oct 31 12:50:18 PDT 2026
```

```
$ cd "~/deadmau5 app"; KIT=tools/showkit; W=$KIT/work/animal; B="deadmau5 & Wolfgang Gartner - Animal Rights"; python3 "$KIT/sheet.py" "$B" "$W/a2.png" 96.5:night 99:title 101:title 103:title 106:wake 109:wake 110.5:roll 111.5:roll 111.9:gap 112:break 112.25:break 114:cobra 116.3:cobra 118.5:siren 120:rip 124:cobrab 128:peacock 128.25 131:peacock 133.6 134.5:siren 138:peacockb 142.5:siren 144:zoo 147:zebra 149:cobra 152:peacock 155:tiger 157:zebra 158.5:siren 161:empty 165:empty 170:search 174:search 178:watching 182:watching 186:last 190:last 192.1:gone 193:gone 2>&1 | tail -40; date
bar 99      title          shell max 204 mean  37.3   ears max  16 mean   0.0   leopard · ANIMAL RIGHTS
bar 101     title          shell max 204 mean  37.8   ears max  19 mean   0.1   leopard · ANIMAL RIGHTS
bar 103     title          shell max 204 mean  37.2   ears max  17 mean   0.1   leopard · ANIMAL RIGHTS
bar 106     wake           shell max 163 mean  18.3   ears max  21 mean   0.1   wake
bar 109     wake           shell max 162 mean  27.6   ears max  19 mean   0.1   wake
bar 110.5   roll           shell max 204 mean  33.4   ears max  67 mean  47.7   roll
bar 111.5   roll           shell max 204 mean  39.8   ears max  94 mean  66.6   roll
bar 111.9   gap            shell max   0 mean   0.0   ears max   0 mean   0.0   roll
bar 112     break          shell max 255 mean 121.6   ears max 191 mean  90.2   cobra · BREAK
bar 112.25  break          shell max 194 mean  84.1   ears max 232 mean  66.6   cobra · BREAK
bar 114     cobra          shell max 153 mean  23.8   ears max 127 mean  14.5   cobra
bar 116.3   cobra          shell max 153 mean  24.2   ears max 115 mean  25.8   cobra
bar 118.5   siren          shell max  83 mean   6.8   ears max 188 mean  18.4   cobra siren · CHIRP
bar 120     rip            shell max 255 mean  47.7   ears max 120 mean  14.6   cobra b · RIP 6
bar 124     cobrab         shell max 153 mean  23.8   ears max 117 mean  14.4   cobra b
bar 128     peacock        shell max 255 mean  47.4   ears max  98 mean  44.4   peacock · RIP 7
bar 128.25                 shell max 171 mean  46.8   ears max  98 mean  52.8   peacock · RIP 7
bar 131     peacock        shell max 164 mean  25.3   ears max  98 mean  42.9   peacock
bar 133.6                  shell max 159 mean  25.7   ears max 180 mean  33.2   peacock
bar 134.5   siren          shell max  83 mean  11.1
... [cut] ...
ar 182     watching       shell max 115 mean  13.7   ears max  34 mean   1.9   watching
bar 186     last           shell max 115 mean   8.7   ears max  29 mean   1.6   last pair
bar 190     last           shell max 115 mean   8.7   ears max  20 mean   1.1   last pair
bar 192.1   gone           shell max  68 mean   3.6   ears max   0 mean   0.0   gone
bar 193     gone           shell max  68 mean   2.0   ears max   0 mean   0.0   gone
tools/showkit/songs/animal/a2.png (1800, 1715)
Sat Oct 31 12:51:09 PDT 2026
```

```
$ cat > tools/showkit/songs/animal/lab.py <<'EOF'
#!/usr/bin/env python3
"""lab.py: try layer variants without touching the show. Run from the repo root.
   from lab import sheet; sheet(out, [(label, pal_or_None, layers, beat), ...], palettes)"""
import sys, os
sys.path.insert(0, os.getcwd())
import numpy as np, mau5engine as E, mau5preview as PV, mau5scene as M
from PIL import Image, ImageDraw
H = E.Helmet()
SC = PV.Scene(H)
def sheet(out, items, palettes, cols=5, W=300, Hh=245):
    tr = {"v": 1, "show": "lab", "marks": {}, "palettes": palettes, "motifs": {}, "scenes": [], "hits": []}
    rows = (len(items ... [cut]
tiger x7 w.32        shell mean  15.7 max  71  ears mean   0.0 max   0
tiger x8 w.5         shell mean  10.4 max  71  ears mean   0.0 max   0
tiger2 x7 w.4        shell mean  21.4 max  71  ears mean   0.0 max   0
tiger2 x7 slant      shell mean  21.6 max  71  ears mean   0.0 max   0
tiger2 x10           shell mean  19.8 max  71  ears mean   0.0 max   0
zebra x9 w.5         shell mean  25.2 max  61  ears mean   0.0 max   0
zebra y5 w.5         shell mean  30.7 max  61  ears mean   0.0 max   0
zebra y7 w.7         shell mean  34.2 max  61  ears mean   0.0 max   0
zebra r6 w.3         shell mean  30.8 max  61  ears mean   0.0 max   0
zebra a9 r           shell mean  30.0 max  61  ears mean   0.0 max   0
cobra y2.2           shell mean  20.2 max  71  ears mean   0.0 max   0
cobra y3 w.6         shell mean  14.0 max  71  ears mean   0.0 max   0
cobra y4 w.8         shell mean  20.8 max  71  ears mean   0.0 max   0
cobra y3 w1          shell mean  18.3 max  71  ears mean   0.0 max   0
cage x8              shell mean  39.7 max 156  ears mean   0.0 max   0
cage x10             shell mean  31.3 max 156  ears mean   0.0 max   0
fan a9 saw           shell mean  28.1 max  60  ears mean   0.0 max   0
fan a12 saw          shell mean  27.7 max  60  ears mean   0.0 max   0
fan a3 r             shell mean  28.0 max  60  ears mean   0.0 max   0
fan r                shell mean  27.7 max  60  ears mean   0.0 max   0
tools/showkit/songs/animal/t1.png
Sat Oct 31 12:52:30 PDT 2026
```

```
$ cat > tools/showkit/songs/animal/write_sprites.py <<'EOF'
#!/usr/bin/env python3
# The zoo's sprites: run from the repo root. Rows drawn by hand, half of them mirrored.
import json
BASE = "deadmau5 & Wolfgang Gartner - Animal Rights"
def mirror(rows):      # the left half, mirrored into the right, the last char is the centre column
    return [r + r[-2::-1] for r in rows]
def flip(rows):
    return [r[::-1] for r in rows]
S = {}
# Predator eyes on the dome, drawn on y_lo 40, y_hi 170, x_half 171: 21 x 8, about 16 mm a cell. Fierce: the outer corners high.
S["animal_eyes"] = mirror([
 "...........",
 "..... ... [cut]
20 sprites
tools/showkit/songs/animal/s1.png (1800, 338)
tools/showkit/songs/animal/s2.png (1440, 338)
tools/showkit/songs/animal/s4.png (1800, 338)
```

```
$ cat > tools/showkit/songs/animal/write_treatment.py <<'EOF'
#!/usr/bin/env python3
# THE ZOO BREAKS OUT: writes the treatment for Animal Rights. Run from the repo root.
import sys, os
KIT = "tools/showkit"
sys.path.insert(0, KIT)
from fmt import save
BASE = "deadmau5 & Wolfgang Gartner - Animal Rights"
SPB = 0.46875
BAR = 4 * SPB
R16 = round(4 / SPB, 6)      # flip-book rate: one frame a 16th note
R8 = round(2 / SPB, 6)       # one frame an 8th note

# --- the horn riff, read off the track: 32 16ths from an even bar
EVE ... [cut]
20 sprites
wrote shows/scenes/deadmau5 & Wolfgang Gartner - Animal Rights.scene.json scenes 45 hits 38
     192   360.00s  energy 0.45  bass 0.08 (punch 0.39)  mid 0.52  high 0.34
     193   361.88s  energy 0.26  bass 0.00 (punch 0.11)  mid 0.35  high 0.13
deadmau5 & Wolfgang Gartner - Animal Rights: 45 scenes, 38 hits, written into shows/deadmau5 & Wolfgang Gartner - Animal Rights.json
Sat Oct 31 12:55:30 PDT 2026
bar 28.3    light          shell max 212 mean  22.5   ears max  86 mean   6.0   searchlight
bar 31.5    found          shell max 230 mean  58.1   ears max 123 mean   5.0   found
bar 32.1    slam           shell max 218 mean  50.5   ears max 131 mean  83.8   alarm · SLAM
bar 33      alarm          shell max 140 mean  24.4   ears max  64 mean  44.3   alarm
bar 34.3                   shell max 140 mean  28.9   ears max 127 mean  15.6   alarm
bar 42.1    alarm2         shell max 153 mean  38.7   ears max 173 mean  20.5   alarm 2
bar 45.56   climb          shell max 187 mean  48.7   ears max 189 mean  23.6   climb
bar 46.5    riser          shell max 217 mean  47.3   ears max  88 mean   4.6   riser
bar 47.5    riser          shell max 217 mean  48.0   ears max 137 mean  40.9   riser
bar 48      tiger          shell max 255 mean  46.8   ears max 140 mean  33.5   tiger · RIP
bar 48.25   rip            shell max 128 mean  49.0   ears max 140 mean  30.5   tiger · RIP
bar 48.57   s9             shell max 230 mean  46.5   ears max 255 mean  26.9   tiger
bar 48.69   s11            shell max 230 mean  46.5   ears max  76 mean  17.1   tiger
bar 48.88   s14            shell max 230 mean  46.7   ears max 190 mean  21.8   tiger
bar 49.56   stab           shell max  87 mean  23.4   ears max  94 mean  24.5   tiger
bar 50.1    rest           shell max  87 mean  22.4   ears max  
... [cut] ...
80      herd           shell max 255 mean  47.9   ears max 120 mean   8.2   stampede · RIP 4
bar 80.25   gap            shell max 204 mean  49.4   ears max 120 mean   8.1   stampede · RIP 4
bar 84      herd           shell max 204 mean  24.6   ears max 120 mean   8.0   stampede
bar 83.4    snort          shell max 218 mean  55.2   ears max 255 mean  54.4   stampede · SNORT
bar 90      herd2          shell max 204 mean  25.8   ears max 120 mean   8.0   stampede 2
tools/showkit/songs/animal/a1.png (1800, 1470)
```

```
$ cd "~/deadmau5 app"; KIT=tools/showkit; W=$KIT/work/animal; B="deadmau5 & Wolfgang Gartner - Animal Rights"; python3 "$KIT/sheet.py" "$B" "$W/a2.png" 96.2:fall 97.5:night 99:title 101:title 103:title 106:wake 109:wake 110.5:roll 111.5:roll 112:break 112.25:break 113:cobra 114.1 116.3:cobra 118.5:siren 118.8:stab 119.2:eyes 120:bite 124:cobrab 128:peacock 128.25 128.5 131:peacock 133.6 134.5:siren 135:eyes 138:peacockb 144:zoo 144.5 147:zebra 149:cobra 152:rip 153:peacock 155:tiger 157:zebra 158.5:siren 161:empty 165:empty 170:search 174:search 178:watching 182:watching 186:last 190:last 192.1:g ... [cut]
bar 192.1   gone           shell max  80 mean   3.8   ears max   0 mean   0.0   gone
bar 193     gone           shell max  80 mean   1.0   ears max   0 mean   0.0   gone
tools/showkit/songs/animal/a2.png (1800, 1960)
Sat Oct 31 12:55:58 PDT 2026
```

```
$ cd "~/deadmau5 app"; KIT=tools/showkit; W=$KIT/work/animal; B="deadmau5 & Wolfgang Gartner - Animal Rights"; python3 - <<'EOF'
p="tools/showkit/songs/animal/write_sprites.py"
s=open(p).read()
s=s.replace('''# The jaw arc, on y_lo -118''','''# The second animal crouches low, on the thick ends of the jaw arc: same box as the jaw
S["animal_low"] = mirror([
 "...............",
 "...............",
 ".###...........",
 "..###..........",
 "...............",
 "...............",
 ])
S["animal_low_shut"] = mirror([
 " ... [cut]
22 sprites
wrote shows/scenes/deadmau5 & Wolfgang Gartner - Animal Rights.scene.json scenes 45 hits 44
     193   361.88s  energy 0.26  bass 0.00 (punch 0.11)  mid 0.35  high 0.13
deadmau5 & Wolfgang Gartner - Animal Rights: 45 scenes, 44 hits, written into shows/deadmau5 & Wolfgang Gartner - Animal Rights.json
deadmau5 & Wolfgang Gartner - Animal Rights: 9375 frames at 25 fps through the guard
  scene            from  mean mA   p95 mA     heat   allow W      ms
  dark             0.0s        5       18     0.0%      18.1    0.01
  eyes open        7.5s      132      185     0.0%      18.1    0.08
  scan            15.0s      173      213     0.0%      18.1    0.08
  nearer          22.5s      167      210     0.0%      18.1    0.08
  scratch         30.0s      204      251     0.0%      18.1    0.13
  searchlight     45.0s      330      403     0.2%      18.1    0.16
  found           58.2s      350      384     0.2%      18.1    0.11
  alarm           60.0s      793     1000     3.2%      18.1    0.17
  alarm 2         75.0s      792     1000     4.7%      18.1    0.17
  climb           82.5s      768     1000     5.4%      18.1    0.18
  riser           86.3s      554     1000     5.8%      18.1    0.18
  tiger           90.0s      654      878     7.4%      18.1    0.14
  tiger siren    101.3s      491      714     7.7%      18.1    0.17
  tiger b        105.0s      660      924     9.3%      18.1    0.14
  tiger b sire   116.3s      491      714     9.6%      18.1    0.16
  zebra          120.0s      773     1000    11.8%      18.1    0.09
  zebra siren    131.3s      506      714    12.1%      18.1    0.17
  zebra b        135.0s      773     1000    14.3%      18.1    0.09
  zebra b sire   146.3s      506      714    14.6%      18.1    0.17
  stampede       150.0
... [cut] ...
3    28.2%      18.1    0.13
  zoo zebra 2    292.5s      773     1000    28.9%      18.1    0.13
  zoo siren 2    296.3s      506      714    29.2%      18.1    0.17
  empty cage     300.0s      434      572    30.0%      18.1    0.14
  search         315.0s      186      482    30.2%      18.1    0.08
  watching       330.0s      207      387    29.4%      18.1    0.14
  last pair      345.0s      134      176    28.8%      18.1    0.07
  gone           360.0s       10       70    27.8%      18.1    0.02
  worst frame 0.54 ms; no scene reaches the sustained floor
Sat Oct 31 12:57:10 PDT 2026
```

```
$ cd "~/deadmau5 app"; KIT=tools/showkit; W=$KIT/work/animal; B="deadmau5 & Wolfgang Gartner - Animal Rights"; args=""; for i in 0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17; do b=$(python3 -c "print(50+$i/16+0.02)"); args="$args $b:s$i"; done; python3 "$KIT/sheet.py" "$B" "$W/m1.png" $args 2>&1 | tail -20; date
Exit code 1
(eval):1: bad substitution
```

```
$ cd "~/deadmau5 app"; KIT=tools/showkit; W="$KIT/work/animal"; B="deadmau5 & Wolfgang Gartner - Animal Rights"; ARGS=$(python3 -c "print(' '.join('%.4f:s%d' % (50+i/16+0.02, i) for i in range(18)))"); python3 "$KIT/sheet.py" "$B" "$W/m1.png" ${=ARGS} 2>&1 | tail -20; date
bar 50.02   s0             shell max  87 mean  21.6   ears max 140 mean  37.7   tiger
bar 50.0825 s1             shell max  87 mean  22.3   ears max  92 mean  30.6   tiger
bar 50.145  s2             shell max 230 mean  47.1   ears max  92 mean  25.2   tiger
bar 50.2075 s3             shell max 124 mean  35.0   ears max  92 mean  23.4   tiger
bar 50.27   s4             shell max  87 mean  24.2   ears max 140 mean  33.8   tiger
bar 50.3325 s5             shell max  87 mean  24.3   ears max  92 mean  25.8   tiger
bar 50.395  s6             shell max 230 mean  48.5   ears max  92 mean  20.4   tiger
bar 50.4575 s7             shell max 124 mean  35.7   ears max  92 mean  19.8   tiger
bar 50.52   s8             shell max  87 mean  23.8   ears max 140 mean  31.5   tiger
bar 50.5825 s9             shell max 230 mean  46.5   ears max 255 mean  32.3   tiger
bar 50.645  s10            shell max 124 mean  33.3   ears max  92 mean  20.5   tiger
bar 50.7075 s11            shell max 230 mean  45.6   ears max 255 mean  29.4   tiger
bar 50.77   s12            shell max 124 mean  32.7   ears max 140 mean  33.5   tiger
bar 50.8325 s13            shell max  87 mean  21.7   ears max  92 mean  28.1   tiger
bar 50.895  s14            shell max 230 mean  45.9   ears max 255 mean  30.5   tiger
bar 50.9575 s15            shell max 124 mean  33.9   ears max  92 mean  25.4   tiger
bar 51.02   s16            shell max 230 mean  46.9   ears max 140 mean  37.7   tiger
bar 51.0825 s17            shell max 124 mean  34.4   ears max  92 mean  30.6   tiger
tools/showkit/songs/animal/m1.png (1800, 735)
Sat Oct 31 12:57:24 PDT 2026
```

```
$ cd "~/deadmau5 app"; KIT=tools/showkit; W="$KIT/work/animal"; B="deadmau5 & Wolfgang Gartner - Animal Rights"; python3 "$KIT/spectro.py" "$B" "$W/z9.png" 141 146; python3 "$KIT/spectro.py" "$B" "$W/z10.png" 157 162;python3 "$KIT/spectro.py" "$B" "$W/z11.png" 94 98; python3 "$KIT/spectro.py" "$B" "$W/z12.png" 188 196
tools/showkit/songs/animal/z9.png
tools/showkit/songs/animal/z10.png
tools/showkit/songs/animal/z11.png
tools/showkit/songs/animal/z12.png
```

```
$ cd "~/deadmau5 app"; KIT=tools/showkit; W="$KIT/work/animal"; B="deadmau5 & Wolfgang Gartner - Animal Rights"; python3 "$KIT/spectro.py" "$B" "$W/z13.png" 144 148; python3 "$KIT/spectro.py" "$B" "$W/z14.png" 112 116; date
tools/showkit/songs/animal/z13.png
tools/showkit/songs/animal/z14.png
Sat Oct 31 12:58:07 PDT 2026
```

```
$ cd "~/deadmau5 app"; KIT=tools/showkit; W="$KIT/work/animal"; B="deadmau5 & Wolfgang Gartner - Animal Rights"; python3 - <<'EOF'
p="tools/showkit/songs/animal/write_treatment.py"
s=open(p).read()
s=s.replace('''def claw_groups(side, groups, gain, c=0.45, length=32, rise=0.6, decay=0.14, pal="claw"):''','''def claw_groups(side, groups, gain, c=0.75, length=32, rise=0.3, decay=0.3, pal="claw", keep=0.6):''')
s=s.replace('''"seq": seq, "step": 0.25, "rise": rise, "keep": 0.3,''','''"seq": seq, "step": 0.25, "ris ... [cut]
wrote shows/scenes/deadmau5 & Wolfgang Gartner - Animal Rights.scene.json scenes 45 hits 44
deadmau5 & Wolfgang Gartner - Animal Rights: 45 scenes, 44 hits, written into shows/deadmau5 & Wolfgang Gartner - Animal Rights.json
tools/showkit/songs/animal/m2.png (1800, 980)
Sat Oct 31 12:58:28 PDT 2026
```

```
$ cd "~/deadmau5 app"; KIT=tools/showkit; W="$KIT/work/animal"; B="deadmau5 & Wolfgang Gartner - Animal Rights"; python3 - <<'EOF'
p="tools/showkit/songs/animal/write_treatment.py"
s=open(p).read()
# (26) the eyes throb on the kick, (27) they look about faster as they come closer
s=s.replace('''S = tr["scenes"].append''','''THROB = {"pat": "x...", "step": 0.25, "decay": 0.8, "floor": 0.72}
S = tr["scenes"].append''')
s=s.replace('''eyes("eye@0.65", 0.45, wx=60, wf=SLOW, box=closer(1.35))]})''','''eyes("eye@0.65 ... [cut]
wrote shows/scenes/deadmau5 & Wolfgang Gartner - Animal Rights.scene.json scenes 45 hits 44
deadmau5 & Wolfgang Gartner - Animal Rights: 45 scenes, 44 hits, written into shows/deadmau5 & Wolfgang Gartner - Animal Rights.json
-rw-r--r--@ 1 jones  staff  250508 Oct 31 12:59 shows/deadmau5 & Wolfgang Gartner - Animal Rights.json
tiger gain+eyes      shell mean  34.6 max 230  ears mean   0.0 max   0
tools/showkit/songs/animal/t2.png
Sat Oct 31 12:59:45 PDT 2026
```

```
$ cd "~/deadmau5 app"; KIT=tools/showkit; W="$KIT/work/animal"; B="deadmau5 & Wolfgang Gartner - Animal Rights"; python3 - <<'EOF'
p="tools/showkit/songs/animal/write_treatment.py"
s=open(p).read()
s=s.replace('''def tiger_lay(rev=1):
    return [dict(TIGER, speed=0.125 * rev), TIGER_T, dict(KICK_R, pal="tiger"), jaw("bone@1", 0.9, 0.22)] + claws()''','''def tiger_lay(rev=1, face=False):
    third = eyes("eye@1", 0.9) if face else dict(KICK_R, pal="tiger")      # the second time round it has the eyes too: the w ... [cut]
wrote shows/scenes/deadmau5 & Wolfgang Gartner - Animal Rights.scene.json scenes 45 hits 44
deadmau5 & Wolfgang Gartner - Animal Rights: 45 scenes, 44 hits, written into shows/deadmau5 & Wolfgang Gartner - Animal Rights.json
tools/showkit/songs/animal/a3.png (1800, 2450)
Sat Oct 31 13:00:09 PDT 2026
```

```
$ cd "~/deadmau5 app"; KIT=tools/showkit; W="$KIT/work/animal"; B="deadmau5 & Wolfgang Gartner - Animal Rights"; python3 - <<'EOF'
p="tools/showkit/songs/animal/write_treatment.py"
s=open(p).read()
# (a) a heartbeat you can actually see
s=s.replace('''HEART = {"fx": "fill", "on": "rims", "pal": "alarm", "c": 0.4, "gate": {"pat": "x...", "step": 0.25, "decay": 0.6}}
S({"name": "dark", "from": -1, "to": "open", "pal": "eye", "layers": [dict(HEART, gain=[0, 0.14])]})''','''HEART = {"fx": "fill", "on": "rims", "pal ... [cut]
wrote shows/scenes/deadmau5 & Wolfgang Gartner - Animal Rights.scene.json scenes 45 hits 47
deadmau5 & Wolfgang Gartner - Animal Rights: 45 scenes, 47 hits, written into shows/deadmau5 & Wolfgang Gartner - Animal Rights.json
deadmau5 & Wolfgang Gartner - Animal Rights: 9375 frames at 25 fps through the guard
  scene            from  mean mA   p95 mA     heat   allow W      ms
  eyes open        7.5s      142      211     0.0%      18.1    0.07
  searchlight     45.0s      346      439     0.3%      18.1    0.15
  climb           82.5s      774     1000     5.5%      18.1    0.16
  tiger b        105.0s      632      839     9.4%      18.1    0.18
  zebra b        135.0s      777     1000    14.4%      18.1    0.09
  leopard        180.0s      389      618    17.0%      18.1    0.24
  cobra siren    221.3s      469      714    19.3%      18.1    0.15
  peacock sire   251.3s      505      714    23.2%      18.1    0.16
  zoo zebra      273.8s      776     1000    27.0%      18.1    0.12
  zoo tiger 2    288.8s      610      781    28.9%      18.1    0.17
  search         315.0s      196      503    30.8%      18.1    0.08
  worst frame 0.43 ms; no scene reaches the sustained floor
worst 7 ms where the music is clear enough to say, mean -1.3 ms
Sat Oct 31 13:01:33 PDT 2026
```

```
$ cd "~/deadmau5 app"; KIT=tools/showkit; W="$KIT/work/animal"; B="deadmau5 & Wolfgang Gartner - Animal Rights"; ARGS=$(python3 -c "
L=['%.3f:%s' % (x,n) for x,n in [(53.9,'riff'),(54.03,'chirp'),(54.2,'chirp'),(54.4,'chirp'),(54.6,'chirp'),(54.76,'stab'),(54.9,'eyes'),(55.1,'eyes'),(55.5,'eyes'),(55.8,'blink'),(55.95,'end'),(56.03,'bite'),(56.2,'bite'),(56.45,'bite'),(47.6,'riser'),(47.76,'cut'),(48.01,'RIP'),(48.08,'RIP'),(48.15,'RIP'),(48.3,'RIP'),(48.48,'RIP'),(16.03,'rake'),(16.08,'rake'),(16.13,'rake')]]
print(' '.join(L))"); python3 "$KIT/sheet.py" "$B" "$W/m3.png" ${=ARGS} 2>&1 | tail -1; ... [cut]
tools/showkit/songs/animal/m3.png (1800, 980)
Sat Oct 31 13:01:44 PDT 2026
```

```
$ cd "~/deadmau5 app"; KIT=tools/showkit; W="$KIT/work/animal"; B="deadmau5 & Wolfgang Gartner - Animal Rights"; python3 - <<'EOF'
p="tools/showkit/songs/animal/write_sprites.py"
s=open(p).read()
s=s.replace('''json.dump(S, open(''','''# The cobra rears: its hood flared round the dome, the two slits inside it
S["animal_hood"] = mirror([
 ".....######",
 "...###.....",
 ".###.......",
 ".##....#...",
 ".##....#...",
 "..###..#...",
 "....###....",
 ".......####",
 ])
S["animal_hood2"] = mirror([
 "...........",
 ... [cut]
24 sprites
tools/showkit/songs/animal/s5.png (1080, 338)
Sat Oct 31 13:02:20 PDT 2026
```

```
$ cd "~/deadmau5 app"; KIT=tools/showkit; W="$KIT/work/animal"; B="deadmau5 & Wolfgang Gartner - Animal Rights"; python3 - <<'EOF'
p="tools/showkit/songs/animal/write_treatment.py"
s=open(p).read()
# fading gashes and fangs blend out instead of painting grey over the stripes
s=s.replace('''L = [{"fx": "preset", "name": "sprite", "on": "shell", "mix": "over", "params": dict(DOME, sprite="|".join(fr), rate=R16, color="white@1"), "gain": [gain, 0.0]},''','''L = [{"fx": "preset", "name": "sprite", "on": "shell", "m ... [cut]
wrote shows/scenes/deadmau5 & Wolfgang Gartner - Animal Rights.scene.json scenes 45 hits 47
deadmau5 & Wolfgang Gartner - Animal Rights: 45 scenes, 47 hits, written into shows/deadmau5 & Wolfgang Gartner - Animal Rights.json
tools/showkit/songs/animal/m4.png (1800, 980)
Sat Oct 31 13:02:44 PDT 2026
```

```
$ cd "~/deadmau5 app"; KIT=tools/showkit; W="$KIT/work/animal"; B="deadmau5 & Wolfgang Gartner - Animal Rights"; python3 - <<'EOF'
p="tools/showkit/songs/animal/write_treatment.py"
s=open(p).read()
s=s.replace('''TIGER_T = {"fx": "grad", "on": "tubes", "axis": "al", "axis2": "al", "scale": 2.0, "speed": -0.25, "lo": 0, "hi": 1, "pal": "tiger", "gain": 0.36}''','''TIGER_T = {"fx": "grad", "on": "tubes", "axis": "al", "axis2": "al", "scale": 1.5, "speed": -0.25, "lo": 0, "hi": 1, "pal": "tiger", "gain": 0.42}''') ... [cut]
wrote shows/scenes/deadmau5 & Wolfgang Gartner - Animal Rights.scene.json scenes 45 hits 51
deadmau5 & Wolfgang Gartner - Animal Rights: 45 scenes, 51 hits, written into shows/deadmau5 & Wolfgang Gartner - Animal Rights.json
bar 50.3    tiger          shell max  87 mean  24.1   ears max 113 mean  29.5   tiger
bar 51.14   tiger          shell max 230 mean  47.2   ears max 107 mean  22.7   tiger
bar 52.62   s9             shell max 176 mean  40.1   ears max 203 mean  40.8   tiger
bar 58.3    face           shell max 230 mean  44.3   ears max 107 mean  20.1   tiger b
bar 146.02  swap           shell max 193 mean  47.0   ears max 221 mean  70.3   zoo zebra · SWAP
bar 146.2   swap           shell max 141 mean  52.2   ears max 148 mean  41.4   zoo zebra · SWAP
bar 148.05  swap           shell max 177 mean  37.9   ears max 184 mean  29.2   zoo cobra · SWAP
bar 154.05  swap           shell max 230 mean  57.4   ears max 201 mean  37.7   zoo tiger 2 · SWAP
bar 156.05  swap           shell max 177 mean  43.0   ears max 201 mean  41.2   chimera · SWAP
bar 157.56  chimera        shell max  87 mean  31.0   ears max 107 mean  30.5   chimera
tools/showkit/songs/animal/m5.png (1800, 490)
Sat Oct 31 13:03:31 PDT 2026
```

```
$ cd "~/deadmau5 app"; KIT=tools/showkit; W="$KIT/work/animal"; B="deadmau5 & Wolfgang Gartner - Animal Rights"; python3 mau5scene.py compile "$B" 2>&1 | grep -i -E "warning|error|scenes,|refus|Traceback"; python3 mau5scene.py check "$B" 2>&1 | tail -50; python3 "$KIT/grid.py" check "$B"; python3 - <<'EOF'
import json, hashlib
B="deadmau5 & Wolfgang Gartner - Animal Rights"
raw=open("shows/scenes/%s.scene.json"%B,"rb").read()
show=json.load(open("shows/%s.json"%B))
sc=show["scenes"]
print("treatment sha", hashlib.sha1(raw).hexdigest()[:12], "in show", sc["treatment"], "grid", sc["grid"], "bars",  ... [cut]
deadmau5 & Wolfgang Gartner - Animal Rights: 45 scenes, 51 hits, written into shows/deadmau5 & Wolfgang Gartner - Animal Rights.json
deadmau5 & Wolfgang Gartner - Animal Rights: 9375 frames at 25 fps through the guard
  scene            from  mean mA   p95 mA     heat   allow W      ms
  dark             0.0s       14       44     0.0%      18.1    0.01
  eyes open        7.5s      142      211     0.0%      18.1    0.07
  scan            15.0s      175      241     0.0%      18.1    0.07
  nearer          22.5s      171      247     0.0%      18.1    0.07
  scratch         30.0s      219      289     0.0%      18.1    0.12
  searchlight     45.0s      346      439     0.3%      18.1    0.15
  found           58.2s      356      402     0.3%      18.1    0.11
  alarm           60.0s      793     1000     3.3%      18.1    0.16
  alarm 2         75.0s      789     1000     4.8%      18.1    0.16
  climb           82.5s      774     1000     5.5%      18.1    0.16
  riser           86.3s      554     1000     5.9%      18.1    0.16
  tiger           90.0s      714      967     7.8%      18.1    0.13
  tiger siren    101.3s      491      714     8.1%      18.1    0.15
  tiger b        105.0s      674      872     9.8%      18.1    0.17
  tiger b sire   116.3s      491      714    10.1%      18.1    0.15
  zebra          120.0s      776     1000    12.2%      18.1    0.08
  zebra siren    131.3s      506      714    12.5%      18.1    0.15
  zebra b        135.0s      777     1000    14.7%      18.1    0.09
  zebra b sire   146.3s      506      714    15.0%      18.1    0.15
  stampede       150.0s      444     1000    15.9%      18.1    0.24
  stampede 2     165.0s      439     1000    16.8%      18.1    0.25
  leopard        180.0s      389      618    17.3%      18.1    
... [cut] ...
 RIGHTS']
sprites ['animal_bite', 'animal_bull', 'animal_claw1', 'animal_claw2', 'animal_claw3', 'animal_clawR1', 'animal_clawR2', 'animal_clawR3', 'animal_cobra', 'animal_eyes', 'animal_eyes_half', 'animal_eyes_shut', 'animal_eyes_wide', 'animal_fangO', 'animal_fangS', 'animal_hood', 'animal_hood2', 'animal_horns', 'animal_jawO', 'animal_jawS', 'animal_low', 'animal_low_shut', 'animal_round', 'animal_round_shut']
about chars 3129
tools/showkit/songs/animal/final.png (1800, 2205)
Sat Oct 31 13:03:48 PDT 2026
```

```
$ cd "~/deadmau5 app"; python3 - <<'EOF' 2>&1 | tail -12
import sys, json, os
sys.path.insert(0, '.')
import numpy as np, mau5engine as E, mau5power, mau5scene as M, mau5show
B = "deadmau5 & Wolfgang Gartner - Animal Rights"
show, music, _ = M._show_and_music(B)
h = E.Helmet()
sc = M.Scenes(show["scenes"], h)
guard = mau5power.load(count=h.n)
th = guard.thermal
print("thermal:", {k: getattr(th, k) for k in dir(th) if not k.startswith("_") and isinstance(getattr(th, k), (int, float))})
dur = float(show["duration"]); fps = 15.0
t_all = 0.0
for play in range(4):
    peak = 0.0; sent = []
    for i in range(int(dur * fps)):
        t = i / fps
        out, gain, label = sc.frame(t, musi ... [cut]
thermal: {'burst_j': 3000.0, 'level': 0.0, 'max_w': 25.5, 'ramp': 0.3, 'standby_w': 7.452, 'sustained_w': 11.0}
play 1: peak heat 31.5%, mean sent 463 mA, end heat 27.6%
play 2: peak heat 56.6%, mean sent 463 mA, end heat 52.8%
play 3: peak heat 81.7%, mean sent 463 mA, end heat 77.9%
play 4: peak heat 96.6%, mean sent 395 mA, end heat 92.8%
  scene            from  mean mA   p95 mA     heat   allow W      ms
  hook            10.5s      643      886     1.0%      18.1    0.12
  big             69.6s      584      890     5.2%      18.1    0.27
  final          268.1s      578      969    16.9%      18.1    0.25
  final2         282.0s      584     1000    18.5%      18.1    0.24
  worst frame 1.82 ms; no scene reaches the sustained floor
Sat Oct 31 13:04:23 PDT 2026
```

```
$ cat > tools/showkit/songs/animal/draw.py <<'EOF'
#!/usr/bin/env python3
# Where the current goes, per scene: shell and ears, as a share of what the guard sent. Run from the repo root.
import sys, os
sys.path.insert(0, os.getcwd())
import numpy as np, mau5engine as E, mau5power, mau5scene as M
B = "deadmau5 & Wolfgang Gartner - Animal Rights"
show, music, _ = M._show_and_music(B)
h = E.Helmet()
sc = M.Scenes(show["scenes"], h)
guard = mau5power.load(count=h.n)
dur = float(show["duration"]); fps = 15.0
per = {}; order = []
for i in range(int(dur * fps)):
    t = i / fps
    out, gain, label = sc.frame(t, mus ... [cut]
scene              mA    shell     ears      n   heat
dark               13        0      500    113   0.0%
eyes open         143     4912      788    112   0.0%
scan              172     6210      651    113   0.0%
nearer            173     6065      788    112   0.0%
scratch           219     7472     1234    225   0.0%
searchlight       346     9435     4268    197   0.3%
found             361    11669     2391     28   0.3%
alarm             794    10353    20907    225   3.3%
alarm 2           801     7986    23553    113   4.8%
climb             777     6162    24406     56   5.5%
riser             544     9836    11552     56   6.0%
tiger             710     9262    18794    169   7.8%
tiger siren       494    10975     8415     56   8.1%
tiger b           672     9078    17449    169   9.8%
tiger b siren     494    10975     8415     56  10.1%
zebra             773     8346    22127    169  12.2%
zebra siren       509    11485     8415     56  12.5%
zebra b           773     8352    22129    169  14.7%
zebra b siren     509    11471     8414     56  15.0%
stampede          444     9046     8087    225  15.9%
stampede 2        438     9335     7703    225  16.8%
leopard           389    11124     3880    225  17.3%
wake              360    11499     2321    169  17.6%
roll              677     7694    18840     56  18.2%
cobra             568     9473    12815    169  19.4%
cobra siren       492    10852     8415     56  19.7%
cobra b           568     9397    12900    169  20.9%
cobra b siren     492    10852     8415     56  21.2%
peacock           765     8168    21904    169  23.3%
peacock siren     509    11407     8415     56  23.7%
peacock b         767     8244    21887    169  25.8%
peacock b sire    509    11407     8415     56  26.1%
zoo tiger         
... [cut] ...
    9832    14274     56  28.0%
zoo siren         494    10975     8415     56  28.3%
zoo peacock       758     7339    22490     57  29.0%
zoo tiger 2       678     9517    17236     56  29.5%
chimera           676     7610    19029     56  30.1%
zoo siren 2       509    11487     8415     56  30.4%
empty cage        443    11127     6199    225  31.3%
search            197     3913     3872    225  31.5%
watching          219     7048     1608    225  30.8%
last pair         145     4977      758    225  30.3%
gone               10      384        0    225  29.3%
Sat Oct 31 13:05:09 PDT 2026
```

```
$ cd "~/deadmau5 app"; grep -n "def apply\|def load\|shell\|ceiling\|budget_ma\|ears" mau5power.py | head -60; sed -n "$(grep -n 'def apply' mau5power.py | head -1 | cut -d: -f1),+70p" mau5power.py; grep -n "def frame" mau5show.py; sed -n "$(grep -n 'class Player' mau5show.py | cut -d: -f1),+12p" mau5show.py; sed -n "$(grep -n '    def frame' mau5show.py | head -1 | cut -d: -f1),+40p" mau5show.py; ls; cat power.json 2>/dev/null | head -50
12:shell are held on with hot glue inside a sealed print, and when that
15:brightness number cannot express that; a ceiling per region can.
24:  ceiling   a per-LED cap by region, so the shell can never be driven
28:            back -- but shed from the shell first and the tubes last,
64:    Two numbers, because they answer different questions.  ``ceiling``
66:    ``budget_ma`` is for the span as a whole: how much current may all
72:    def __init__(self, name, lo, hi, ceiling, budget_ma, shed=1.0, floor=0.0):
74:        self.ceiling = int(ceiling)        # 0-255, per channel, per LED
75:        self.budget_ma = float(budget_ma)  # for the whole span
78:        # about priority and wrong about the endpoint: a shell with
92:        return self.n * MA_PER_LED_FULL_WHITE * self.ceiling / 255.0
95:        return ("Region(%s %d..%d ceiling=%d budget=%.0fmA shed=%.1f)"
96:                % (self.name, self.lo, self.hi, self.ceiling,
97:                   self.budget_ma, self.shed))
176:    def __init__(self, count, regions, budget_ma, default_ceiling=32,
181:        self.budget_ma = float(budget_ma)
185:        # real ceiling if the current has to cross a contact that
191:        self.default_ceiling = int(default_ceiling)
192:        self._ceil = np.full(self.count, float(default_ceiling), np.float32)
198:                self._ceil[lo:hi + 1] = r.ceiling
200:                self._floor[lo:hi + 1] = min(r.floor, r.ceiling)
201:        # The ceiling is a soft knee (see apply).  It starts to bend at
202:        # _klo and has _kw left above that before the ceiling.  The bend
204:        # e**-4 short of the ceiling, under 2%, so the top end the
205:        # ceilings were tuned for is where it was.  On a ceiling of 255
206:        # it never bends -- a tube is not dimmed by a c
... [cut] ...
y
mau5doctor.py
mau5drive.py
mau5engine.py
mau5eye.py
mau5fake.py
mau5film.py
mau5fseq.py
mau5fx.py
mau5head_sim_backdrop.glb
mau5head_sim_backdrop.stl
mau5head_software_BUILD_PROMPT.md
mau5hue.py
mau5icon.py
mau5lapse.py
mau5lines.py
mau5locate.py
mau5map.py
mau5offline.py
mau5peek.py
mau5power.py
mau5preview.py
mau5psu.py
mau5relay.py
mau5review.py
mau5scene.py
mau5shoot.py
mau5show.py
mau5sim.py
mau5slots.py
mau5song.py
mau5spotify.py
mau5tune.py
mau5verify.py
mau5walk.py
mau5web.py
mau5wled.py
preview_strobe_orbit.gif
remote
route_traced.png
setup
shows
sim_demo.png
test_mau5.py
tests_more
```

```
$ cd "~/deadmau5 app"; grep -n "guard\|power\|def frame\|class Scene\|gamma\|ceiling" mau5preview.py | head -30; sed -n "$(grep -n 'def frame' mau5preview.py | head -1 | cut -d: -f1),+45p" mau5preview.py; ls data | head -20; python3 - <<'EOF'
import sys
sys.path.insert(0,'.')
import mau5power
g=mau5power.load(count=621)
print(g.describe() if hasattr(g,'describe') else '')
print(mau5power.DEFAULT)
import json
print(open(mau5power.DEFAULT).read()[:1800])
EOF
56:class Scene:
77:    def frame(self, rgb, gain=1.0):
    def frame(self, rgb, gain=1.0):
        buf = self.back.copy()
        order = np.argsort(self.z)          # ears (behind) first
        for i in order:
            c = rgb[i]
            if c.max() < 3:
                continue
            r = float(round(self.rad[i], 1))
            k = self.kern[r]
            n = k.shape[0]
            x0, y0 = int(self.px[i]) - n // 2, int(self.py[i]) - n // 2
            x1, y1 = x0 + n, y0 + n
            kx0, ky0 = max(0, -x0), max(0, -y0)
            x0, y0 = max(0, x0), max(0, y0)
            x1, y1 = min(W, x1), min(H, y1)
            if x1 <= x0 or y1 <= y0:
                continue
            sub = k[ky0:ky0 + (y1 - y0), kx0:kx0 + (x1 - x0)]
            buf[y0:y1, x0:x1] += sub[:, :, None] * (c * gain)[None, None, :]
        return Image.fromarray(np.clip(buf, 0, 255).astype(np.uint8))


def render(preset, seconds=6.0, fps=24, music=None, gain=1.0):
    h = E.Helmet()
    sc = Scene(h)
    for i in range(int(seconds * fps)):
        t = i / fps
        yield sc.frame(preset.render(h, t, music), gain)


def to_mp4(frames, path, fps=24):
    tmp = tempfile.mkdtemp(prefix="mau5prev")
    n = 0
    for im in frames:
        im.save(os.path.join(tmp, "f%05d.png" % n)); n += 1
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                    "-framerate", str(fps), "-i", os.path.join(tmp, "f%05d.png"),
                    "-vf", "format=yuv420p", "-c:v", "libx264", "-crf", "20",
                    path], check=True)
    for f in os.listdir(tmp):
        os.remove(os.path.join(tmp, f))
    os.rmdir(tmp)
    return path, n


def sheet(path, t=1.7, cols=5):
cad
cal
offline
pixel_map.csv
web
wiring_chained.csv
global budget 1000 mA of LED current
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
$ cat > tools/showkit/songs/animal/gsheet.py <<'EOF'
#!/usr/bin/env python3
"""gsheet.py out.png bar[:label] ... -- the show as it really leaves the guard: the whole song is walked
through a fresh mau5power guard at 30 fps, so the ceilings, the region budgets, the governor and the heat
are all as they would be at that moment. sheet.py's own tiles are the raw scene output, before any of that."""
import json, os, sys
sys.path.insert(0, os.getcwd())
import numpy as np, mau5power, mau5show, mau5scene as M, mau5preview as PV
from PIL import Image, ImageDraw
B = "deadmau5 & Wolfgang Gartner - Animal Rights"
out =  ... [cut]
bar 12      scan       shell max  56 mean   5.9   ears max  56 mean   3.1    228 mA  nearer
bar 20      low        shell max  58 mean   8.3   ears max  61 mean   3.4    306 mA  scratch
bar 28.3    search     shell max  53 mean   9.9   ears max  86 mean   7.3    422 mA  searchlight
bar 31.2    found      shell max  23 mean   9.8   ears max  66 mean   1.8    332 mA  found
bar 32.1    slam       shell max   3 mean   1.8   ears max  91 mean  56.1   1000 mA  alarm · SLAM
bar 36.15   cage       shell max  18 mean   6.7   ears max 114 mean  47.1   1000 mA  alarm
bar 42.15   cage       shell max   9 mean   4.1   ears max 101 mean  51.7   1000 mA  alarm 2
bar 45.2    climb      shell max  10 mean   4.4   ears max 102 mean  36.6    755 mA  climb
bar 47.3    riser      shell max  22 mean   9.8   ears max 156 mean  33.2    858 mA  riser
bar 48.01   RIP        shell max  16 mean   8.0   ears max 247 mean  44.8   1000 mA  tiger · RIP
bar 48.15   RIP        shell max  13 mean   7.5   ears max 181 mean  27.5    698 mA  tiger · RIP
bar 50.14   tiger      shell max  24 mean   7.7   ears max  84 mean  17.6    533 mA  tiger
bar 50.3    rest       shell max  29 mean   9.4   ears max 108 mean  28.0    757 mA  tiger
bar 50.6    slash      shell max  17 mean   5.3   ears max 198 mean  39.8    835 mA  tiger
bar 54.2    chirp      shell max  48 mean   9.8   ears max 199 mean  22.1    672 mA  tiger siren · CHIRP
bar 55      eyes       shell max  47 mean   9.8   ears max  88 mean   3.7    365 mA  tiger siren · EYES
bar 56.02   bite       shell max   3 mean   1.4   ears max 124 mean  56.7   1000 mA  tiger b · BITE
bar 58.15   face       shell max  19 mean   7.6   ears max  83 mean  17.0    521 mA  tiger b
bar 64.03   zebra      shell max   6 mean   2.4   ears max 190 mean  54.7   1000 mA  zebra · R
... [cut] ...
 mean  52.7    958 mA  peacock · UNFURL
bar 131     peacock    shell max  26 mean   9.4   ears max  96 mean  42.2   1000 mA  peacock
bar 144.02  bite       shell max   3 mean   1.3   ears max 121 mean  56.7   1000 mA  zoo tiger · BITE 3
bar 157.2   chimera    shell max  18 mean   7.5   ears max  83 mean  20.4    578 mA  chimera
bar 165     leaving    shell max  56 mean   8.4   ears max 125 mean  12.3    467 mA  empty cage · LEAVING 3
tools/showkit/songs/animal/g1.png (1800, 1470)
Sat Oct 31 13:06:24 PDT 2026
```

I'll read the correction and the new tools first.

```
$ KIT=tools/showkit; date; wc -l "$KIT/BRIEF.md"; sed -n 38,200p "$KIT/BRIEF.md"; echo ------; cat "$KIT/sheet.py"; echo ------; cat "$KIT/power.py"; echo ------; cat "$KIT/scenepower.py"
Sat Oct 31 13:07:44 PDT 2026
      47 tools/showkit/BRIEF.md
621 LEDs: shell 397, each ear 112 (three tubes and a rim). LEDs sit behind diffusers, so soft shapes and big motion read best; fine detail does not. On the shell: gates and pumps no faster than 8th notes (the compiler refuses faster, because whole-shell flicker reads as a fault). Ears can go faster. Current is tight: the sustained budget is about 300 mA of LED current across the whole helmet with short bursts to 1 A, and when the ears are loud the guard takes it from the shell, so keep shell gains near Tiki's (0.14 to 0.3 for full-shell layers, more for small lit areas) and ear layers 0.25 to 0.7, and confirm in `sheet.py` that the shell is really visible. Bright full-helmet white is for one moment in the whole song at most. Dark is an effect: contrast is most of what makes a hit land.

Song-specific concept follows in your task. It is a starting point. If the music says otherwise, follow the music, and keep it unique.

## Added after the first run: the long set
These shows also play back to back in a set of up to 90 minutes. The helmet can shed 11 W for ever (7.4 W of that is the LEDs' own idle draw), and the 3000 J heat bucket only covers what goes above that. When songs run hotter, heat builds up song after song, and after about 20 minutes every hit in the rest of the set gets flattened by the guard. So besides the checks above, run `python3 $KIT/power.py "<base>"` and aim for a whole-song mean of 11.5 W or less, and never above 12.5 W. Heat at the end of the song should be under about 15%. Get there with contrast rather than by dimming everything: darker verses and breakdowns, fewer full-shell layers, more small lit sha
... [cut] ...
d after the knee: from the mean
    per[nm].append((rep["sent_ma"],rep["governor_hit"],"shell" in rep["regions_hit"],res[sh].mean(),res[ea].mean(),rep["thermal"]["full_pct"] if rep.get("thermal") else 0,res[sh].max()))
print("%-14s %6s %6s %6s %6s %7s %7s %6s %6s"%("scene","mean","p95","gov%","reg%","shellm","earsm","smax","heat"))
for nm in order:
    a=np.array(per[nm],float)
    print("%-14s %6.0f %6.0f %6.0f %6.0f %7.1f %7.1f %6.0f %5.1f%%"%(nm[:14],a[:,0].mean(),np.percentile(a[:,0],95),a[:,1].mean()*100,a[:,2].mean()*100,a[:,3].mean(),a[:,4].mean(),np.percentile(a[:,6],90),a[:,5].max()))
```

```
$ cd "~/deadmau5 app"; KIT=tools/showkit; B="deadmau5 & Wolfgang Gartner - Animal Rights"; python3 "$KIT/power.py" "$B" 2>&1 | tail -20; python3 "$KIT/scenepower.py" "$B" 2>&1 | tail -60; date
deadmau5 & Wolfgang Gartner - Animal Rights: 375 s, mean 13.1 W (target 11.5 or less), heat at the end 28%
hottest scenes (name, mean W, seconds): alarm 17.1 15s; zebra 16.9 11s; zebra b 16.9 11s; peacock b 16.8 11s; peacock 16.7 11s; tiger 16.1 11s; tiger b 15.6 11s; stampede 13.0 15s
scene            mean    p95   gov%   reg%  shellm   earsm   smax   heat
dark               14     44      0      0     0.0     0.8      0   0.0%
eyes open         142    211      0      0     4.1     1.1     47   0.0%
scan              175    241      0      0     5.2     1.1     54   0.0%
nearer            171    247      0      0     5.1     1.1     56   0.0%
scratch           219    289      0      0     6.3     1.8     58   0.0%
searchlight       346    439      0     37     7.9     6.4     58   0.3%
found             356    402      0    100     9.8     3.3     23   0.3%
alarm             793   1000     41    100     8.6    31.3     32   3.3%
alarm 2           789   1000     68    100     6.6    34.7     27   4.8%
climb             774   1000     82    100     4.8    37.0     25   5.5%
riser             554   1000     13     88     8.3    17.9     25   5.9%
tiger             714    967     24    100     7.8    28.3     30   7.8%
tiger siren       491    714      3     75     9.2    12.3     57   8.1%
tiger b           674    872     23    100     7.6    26.1     28   9.8%
tiger b siren     491    714      3     75     9.2    12.3     57  10.1%
zebra             776   1000     50    100     7.0    33.3     17  12.2%
zebra siren       506    714      3    100     9.6    12.3     43  12.5%
zebra b           777   1000     50    100     7.0    33.3     17  14.7%
zebra b siren     506    714      3    100     9.6    12.3     44  15.0%
stampede          444   1000     17    100     7.6   
... [cut] ...
      678    868     18    100     8.0    25.8     25  29.6%
chimera           675    895     47    100     6.4    28.4     23  30.1%
zoo siren 2       506    714      3    100     9.6    12.3     41  30.4%
empty cage        443    580      0     79     9.3     9.3     52  31.3%
search            197    506      0      7     3.3     5.7     44  31.5%
watching          218    400      0      0     5.9     2.4     55  30.8%
last pair         144    196      0      0     4.2     1.1     55  30.3%
gone               10     70      0      0     0.3     0.0     45  29.4%
Sat Oct 31 13:07:50 PDT 2026
```

```
$ KIT=tools/showkit; date; wc -l "$KIT/BRIEF.md"; sed -n 38,200p "$KIT/BRIEF.md"; echo ------; cat "$KIT/sheet.py"; echo ------; cat "$KIT/power.py"; echo ------; cat "$KIT/scenepower.py"
Sat Oct 31 13:07:44 PDT 2026
      47 tools/showkit/BRIEF.md
621 LEDs: shell 397, each ear 112 (three tubes and a rim). LEDs sit behind diffusers, so soft shapes and big motion read best; fine detail does not. On the shell: gates and pumps no faster than 8th notes (the compiler refuses faster, because whole-shell flicker reads as a fault). Ears can go faster. Current is tight: the sustained budget is about 300 mA of LED current across the whole helmet with short bursts to 1 A, and when the ears are loud the guard takes it from the shell, so keep shell gains near Tiki's (0.14 to 0.3 for full-shell layers, more for small lit areas) and ear layers 0.25 to 0.7, and confirm in `sheet.py` that the shell is really visible. Bright full-helmet white is for one moment in the whole song at most. Dark is an effect: contrast is most of what makes a hit land.

Song-specific concept follows in your task. It is a starting point. If the music says otherwise, follow the music, and keep it unique.

## Added after the first run: the long set
These shows also play back to back in a set of up to 90 minutes. The helmet can shed 11 W for ever (7.4 W of that is the LEDs' own idle draw), and the 3000 J heat bucket only covers what goes above that. When songs run hotter, heat builds up song after song, and after about 20 minutes every hit in the rest of the set gets flattened by the guard. So besides the checks above, run `python3 $KIT/power.py "<base>"` and aim for a whole-song mean of 11.5 W or less, and never above 12.5 W. Heat at the end of the song should be under about 15%. Get there with contrast rather than by dimming everything: darker verses and breakdowns, fewer full-shell layers, more small lit sha
... [cut] ...
d after the knee: from the mean
    per[nm].append((rep["sent_ma"],rep["governor_hit"],"shell" in rep["regions_hit"],res[sh].mean(),res[ea].mean(),rep["thermal"]["full_pct"] if rep.get("thermal") else 0,res[sh].max()))
print("%-14s %6s %6s %6s %6s %7s %7s %6s %6s"%("scene","mean","p95","gov%","reg%","shellm","earsm","smax","heat"))
for nm in order:
    a=np.array(per[nm],float)
    print("%-14s %6.0f %6.0f %6.0f %6.0f %7.1f %7.1f %6.0f %5.1f%%"%(nm[:14],a[:,0].mean(),np.percentile(a[:,0],95),a[:,1].mean()*100,a[:,2].mean()*100,a[:,3].mean(),a[:,4].mean(),np.percentile(a[:,6],90),a[:,5].max()))
```

```
$ cd "~/deadmau5 app"; KIT=tools/showkit; B="deadmau5 & Wolfgang Gartner - Animal Rights"; python3 "$KIT/power.py" "$B" 2>&1 | tail -20; python3 "$KIT/scenepower.py" "$B" 2>&1 | tail -60; date
deadmau5 & Wolfgang Gartner - Animal Rights: 375 s, mean 13.1 W (target 11.5 or less), heat at the end 28%
hottest scenes (name, mean W, seconds): alarm 17.1 15s; zebra 16.9 11s; zebra b 16.9 11s; peacock b 16.8 11s; peacock 16.7 11s; tiger 16.1 11s; tiger b 15.6 11s; stampede 13.0 15s
scene            mean    p95   gov%   reg%  shellm   earsm   smax   heat
dark               14     44      0      0     0.0     0.8      0   0.0%
eyes open         142    211      0      0     4.1     1.1     47   0.0%
scan              175    241      0      0     5.2     1.1     54   0.0%
nearer            171    247      0      0     5.1     1.1     56   0.0%
scratch           219    289      0      0     6.3     1.8     58   0.0%
searchlight       346    439      0     37     7.9     6.4     58   0.3%
found             356    402      0    100     9.8     3.3     23   0.3%
alarm             793   1000     41    100     8.6    31.3     32   3.3%
alarm 2           789   1000     68    100     6.6    34.7     27   4.8%
climb             774   1000     82    100     4.8    37.0     25   5.5%
riser             554   1000     13     88     8.3    17.9     25   5.9%
tiger             714    967     24    100     7.8    28.3     30   7.8%
tiger siren       491    714      3     75     9.2    12.3     57   8.1%
tiger b           674    872     23    100     7.6    26.1     28   9.8%
tiger b siren     491    714      3     75     9.2    12.3     57  10.1%
zebra             776   1000     50    100     7.0    33.3     17  12.2%
zebra siren       506    714      3    100     9.6    12.3     43  12.5%
zebra b           777   1000     50    100     7.0    33.3     17  14.7%
zebra b siren     506    714      3    100     9.6    12.3     44  15.0%
stampede          444   1000     17    100     7.6   
... [cut] ...
      678    868     18    100     8.0    25.8     25  29.6%
chimera           675    895     47    100     6.4    28.4     23  30.1%
zoo siren 2       506    714      3    100     9.6    12.3     41  30.4%
empty cage        443    580      0     79     9.3     9.3     52  31.3%
search            197    506      0      7     3.3     5.7     44  31.5%
watching          218    400      0      0     5.9     2.4     55  30.8%
last pair         144    196      0      0     4.2     1.1     55  30.3%
gone               10     70      0      0     0.3     0.0     45  29.4%
Sat Oct 31 13:07:50 PDT 2026
```

```
$ cd "~/deadmau5 app"; sed -n 300,415p mau5power.py; sed -n 30,60p mau5power.py; grep -n "MA_PER_LED_FULL_WHITE *=" mau5power.py
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
        # lands on budget.  Monotonic in s, so bisect: a frame that asks
        # for too much comes back dimmer everywhere, weighted, rather
        # than with the low-priority regions amputated.
        #
        # The floor is solved here too, not afterwards.  The governor
        # spends the budget exactly, so a floor applied as a second pass
        # has nothing left to spend and collapses to nothing: the two
        # have to be one equation.  Each LED ends at
        #     max(s ** shed_i, floor_i / level_i)
        # of what survived its region, so the floored LEDs take their
        # few milliamps off the top and everything else sheds around
        # them.  Still monotonic in s, so the bisection stands.
        #
        # And s gives light back slowly.  So
... [cut] ...

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


46:MA_PER_LED_FULL_WHITE = 19.0      # WS2815 at 12 V
```

```
$ cd "~/deadmau5 app"; KIT=tools/showkit; W="$KIT/work/animal"; B="deadmau5 & Wolfgang Gartner - Animal Rights"; python3 "$KIT/sheet.py" "$B" "$W/g1.png" 2:dark 6:open 12:scan 20:low-eyes 28.3:search 31.2:found 32.1:slam 36.15:cage 42.15:cage 45.2:climb 47.3:riser 47.9:cut 48.01:RIP 48.15:RIP 50.14:tiger 50.6:slash 54.2:chirp 55:eyes 56.02:bite 58.15:face 64.03:zebra 66.15:zebra 71:prey 74.2:arcs 80.03:bull 84.3:gallop 87.4:snort 96.2:fall 99.2:title 103:title 107:wake 110.5:roll 112.01:white 114.25:cobra 119.2:hood 121:cobra 128.3:unfurl 131:peacock 135:prey 144.02:bite 147.2:zebra 149.2:cobra 1 ... [cut]
bar 2       dark       sent   40 mA  shell max   0 mean   0.0  ears max  43 mean   2.4  dark
bar 6       open       sent  208 mA  shell max  44 mean   5.3  ears max  56 mean   3.1  eyes open
bar 12      scan       sent  228 mA  shell max  56 mean   5.9  ears max  56 mean   3.1  nearer
bar 20      low-eyes   sent  306 mA  shell max  58 mean   8.3  ears max  61 mean   3.4  scratch
bar 28.3    search     sent  422 mA  shell max  53 mean   9.9  ears max  86 mean   7.3  searchlight
bar 31.2    found      sent  332 mA  shell max  23 mean   9.8  ears max  66 mean   1.8  found
bar 32.1    slam       sent 1000 mA  shell max   3 mean   1.8  ears max  91 mean  56.1  alarm · SLAM
bar 36.15   cage       sent 1000 mA  shell max  18 mean   6.7  ears max 114 mean  47.1  alarm
bar 42.15   cage       sent 1000 mA  shell max   9 mean   4.1  ears max 101 mean  51.7  alarm 2
bar 45.2    climb      sent  750 mA  shell max  10 mean   4.3  ears max 101 mean  36.5  climb
bar 47.3    riser      sent  858 mA  shell max  22 mean   9.8  ears max 156 mean  33.2  riser
bar 47.9    cut        sent    0 mA  shell max   0 mean   0.0  ears max   0 mean   0.0  riser
bar 48.01   RIP        sent 1000 mA  shell max  16 mean   8.0  ears max 247 mean  44.8  tiger · RIP
bar 48.15   RIP        sent  698 mA  shell max  13 mean   7.5  ears max 181 mean  27.5  tiger · RIP
bar 50.14   tiger      sent  533 mA  shell max  24 mean   7.7  ears max  84 mean  17.6  tiger
bar 50.6    slash      sent  835 mA  shell max  17 mean   5.3  ears max 198 mean  39.8  tiger
bar 54.2    chirp      sent  672 mA  shell max  48 mean   9.8  ears max 199 mean  22.1  tiger siren · CHIRP
bar 55      eyes       sent  365 mA  shell max  47 mean   9.8  ears max  88 mean   3.7  tiger siren · EYES
bar 56.02   bite       sent 1000 mA  shell max  
... [cut] ...
ll max  47 mean   9.9  ears max  61 mean   3.4  search
bar 173     search     sent  240 mA  shell max  36 mean   6.0  ears max  79 mean   3.5  search
bar 178     out        sent  293 mA  shell max  55 mean   7.9  ears max  61 mean   3.4  watching
bar 188     last       sent  215 mA  shell max  55 mean   5.8  ears max  43 mean   2.4  last pair
bar 192.3   close      sent   70 mA  shell max  45 mean   2.3  ears max   0 mean   0.0  gone
tools/showkit/songs/animal/g1.png (1800, 2205)
Sat Oct 31 13:08:30 PDT 2026
```

```
$ cd "~/deadmau5 app"; W=tools/showkit/songs/animal; sed -i '' 's|^B = "deadmau5 \& Wolfgang Gartner - Animal Rights"$|B = os.environ.get("BASE", "deadmau5 \& Wolfgang Gartner - Animal Rights")|' "$W/gsheet.py" "$W/draw.py"; grep -n '^B = ' "$W/gsheet.py" "$W/draw.py"; cat > "$W/draw.py" <<'EOF'
#!/usr/bin/env python3
# Through the real guard, per scene: what the shell and ears take, how often the governor binds and what it leaves of the shell.
import sys, os
sys.path.insert(0, os.getcwd())
import numpy as np, mau5engine as E, mau5power, mau5scene as M
B = os.environ.get("BASE", "deadmau5 & Wolfga ... [cut]
tools/showkit/songs/animal/draw.py:6:B = os.environ.get("BASE", "deadmau5 & Wolfgang Gartner - Animal Rights")
tools/showkit/songs/animal/gsheet.py:9:B = os.environ.get("BASE", "deadmau5 & Wolfgang Gartner - Animal Rights")
scene                mA shellmA  earsmA askedear   gov%  shmax   heat
lighting            203     105      91       93     0%     29   0.0%
hook                647     205     424      538    27%     24   1.0%
hookb               642     223     400      496    18%     22   2.0%
hook2               637     215     402      507    23%     25   3.3%
lagoon              184      72      99      103     0%     30   3.5%
verse               312     137     160      171     1%     23   3.9%
big                 585     194     372      520    22%     19   5.3%
bigb                566     198     348      481    18%     23   7.1%
verse2              314     138     162      173     1%     24   7.3%
sunset              589     190     378      533    26%     16   8.8%
sunsetb             572     195     357      497    22%     20  10.0%
verse3              315     138     162      174     1%     23  10.1%
duel                558     155     385      562    32%     23  11.0%
duel2               560     157     384      556    33%     24  11.8%
duel3               570     157     395      573    33%     23  12.2%
hook3               667     200     446      580    33%     24  13.2%
hook3b              641     223     398      495    17%     21  14.1%
hook4               638     215     402      507    24%     25  15.4%
verse4              315     138     163      174     1%     23  15.6%
fi
... [cut] ...
ell max  14 mean   2.5   ears max 105 mean  54.6   1000 mA  duel2 · SWAP
bar 153.01  final      shell max  42 mean   7.9   ears max 143 mean  30.3    756 mA  vrise4
bar 155     final      shell max  25 mean   6.1   ears max  62 mean  19.2    520 mA  final
bar 161     final2     shell max  17 mean   6.1   ears max  85 mean  19.6    525 mA  final
bar 178     out        shell max  16 mean   3.4   ears max  51 mean   5.5    201 mA  out
tools/showkit/songs/animal/gtiki.png (1800, 735)
Sat Oct 31 13:08:58 PDT 2026
```

```
$ cd "~/deadmau5 app"; W=tools/showkit/songs/animal; sed -i '' 's|^B = "deadmau5 \& Wolfgang Gartner - Animal Rights"$|B = os.environ.get("BASE", "deadmau5 \& Wolfgang Gartner - Animal Rights")|' "$W/gsheet.py" "$W/draw.py"; grep -n '^B = ' "$W/gsheet.py" "$W/draw.py"; cat > "$W/draw.py" <<'EOF'
#!/usr/bin/env python3
# Through the real guard, per scene: what the shell and ears take, how often the governor binds and what it leaves of the shell.
import sys, os
sys.path.insert(0, os.getcwd())
import numpy as np, mau5engine as E, mau5power, mau5scene as M
B = os.environ.get("BASE", "deadmau5 & Wolfga ... [cut]
tools/showkit/songs/animal/draw.py:6:B = os.environ.get("BASE", "deadmau5 & Wolfgang Gartner - Animal Rights")
tools/showkit/songs/animal/gsheet.py:9:B = os.environ.get("BASE", "deadmau5 & Wolfgang Gartner - Animal Rights")
scene                mA shellmA  earsmA askedear   gov%  shmax   heat
lighting            203     105      91       93     0%     29   0.0%
hook                647     205     424      538    27%     24   1.0%
hookb               642     223     400      496    18%     22   2.0%
hook2               637     215     402      507    23%     25   3.3%
lagoon              184      72      99      103     0%     30   3.5%
verse               312     137     160      171     1%     23   3.9%
big                 585     194     372      520    22%     19   5.3%
bigb                566     198     348      481    18%     23   7.1%
verse2              314     138     162      173     1%     24   7.3%
sunset              589     190     378      533    26%     16   8.8%
sunsetb             572     195     357      497    22%     20  10.0%
verse3              315     138     162      174     1%     23  10.1%
duel                558     155     385      562    32%     23  11.0%
duel2               560     157     384      556    33%     24  11.8%
duel3               570     157     395      573    33%     23  12.2%
hook3               667     200     446      580    33%     24  13.2%
hook3b              641     223     398      495    17%     21  14.1%
hook4               638     215     402      507    24%     25  15.4%
verse4              315     138     163      174     1%     23  15.6%
fi
... [cut] ...
ell max  14 mean   2.5   ears max 105 mean  54.6   1000 mA  duel2 · SWAP
bar 153.01  final      shell max  42 mean   7.9   ears max 143 mean  30.3    756 mA  vrise4
bar 155     final      shell max  25 mean   6.1   ears max  62 mean  19.2    520 mA  final
bar 161     final2     shell max  17 mean   6.1   ears max  85 mean  19.6    525 mA  final
bar 178     out        shell max  16 mean   3.4   ears max  51 mean   5.5    201 mA  out
tools/showkit/songs/animal/gtiki.png (1800, 735)
Sat Oct 31 13:08:58 PDT 2026
```

You've hit your session limit · resets 5:10pm (America/Los_Angeles)
