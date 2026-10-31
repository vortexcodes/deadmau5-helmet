# What the weapon builder ran and saw

Commands and their text output, in order, with long output cut. Images are left out; rerun the tools to see them. Cut off partway: the generator and treatment in the repo are the latest state.

```
$ date; cat "tools/showkit/BRIEF.md"; ls -la "tools/showkit/"
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
$ KIT="tools/showkit"; cd "~/deadmau5 app"; cat "$KIT/grid.py"; echo ------; cat "$KIT/fmt.py"; echo -----; cat "$KIT/sheet.py"; echo -----; cat "$KIT/songmap.py"; echo ----; cat "$KIT/spectro.py"; echo -----; cat "$KIT/spritetry.py"; ls -la "$KIT/work"; ls -la shows/ | head -50; ls -la "shows/scenes" | head -60
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
$ KIT="tools/showkit"; cat "(scratch)/tiki/write_treatment.py"
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
$ KIT="tools/showkit"; cd "~/deadmau5 app"; cat "$KIT/grid.py"; echo ------; cat "$KIT/fmt.py"; echo -----; cat "$KIT/sheet.py"; echo -----; cat "$KIT/songmap.py"; echo ----; cat "$KIT/spectro.py"; echo -----; cat "$KIT/spritetry.py"; ls -la "$KIT/work"; ls -la shows/ | head -50; ls -la "shows/scenes" | head -60
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
$ KIT="tools/showkit"; cat "(scratch)/tiki/write_treatment.py"
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
$ KIT="tools/showkit"; cd "~/deadmau5 app"; mkdir -p "$KIT/work/weapon"; time python3 "$KIT/grid.py" scan "shows/deadmau5 - Raise Your Weapon.mp3" 2>&1 | tail -30
estimator: 128.003 BPM, first bar 0.034 s, tempo lock 0.150, bar lock 0.27683626155406293; song 502.9 s
refined over the whole song: spb 0.468761 = 127.997 BPM
first half 127.997 BPM, second half 127.997 BPM (these should agree within 0.05)
phase of the music against that grid per 8 bars, ms (flat = right; one 16th = 117 ms; contrast under 1.15 means sparse, ignore it):
  0:-5(1.39)  8:-1(1.50)  16:+45(1.11)  24:-11(1.16)  32:-21(1.10)  40:-1(1.24)  48:-13(6.73)  56:-13(7.94)  64:-11(3.46)  72:-11(3.79)  80:-13(3.49)  88:-13(4.10)  96:-11(7.78)  104:-9(6.10)  112:+19(1.25)  120:-5(1.21)  128:+51(1.17)  136:-23(1.17)  144:-49(1.14)  152:-49(1.08)  160:-41(1.14)  168:-41(1.15)  176:+9(1.06)  184:-41(1.14)  192:-25(1.09)  200:+1(1.12)  208:+9(1.12)  216:-17(1.15)  224:-13(1.10)  232:-31(1.06)  240:+23(1.09)  248:-27(1.11)  256:+1(1.11)  264:+31(1.10)
change per beat position, estimator's bar 1 at 0.034 s: 0:1.38 1:1.23 2:1.27 3:1.25  (the highest is where bars really start, 0 = estimator is right)
strongest phrase positions, in beats mod 32 from that bar 1: 16(1.57), 22(1.49), 28(1.49), 0(1.46), 31(1.46), 30(1.44)
biggest single changes (time, beat from bar 1, beat mod 4): 30.0s b64 m0; 35.7s b76 m0; 37.5s b80 m0; 40.3s b86 m2; 40.8s b87 m3; 52.5s b112 m0; 60.0s b128 m0; 220.4s b470 m2; 224.1s b478 m2; 227.9s b486 m2; 238.6s b509 m1; 258.3s b551 m3; 261.6s b558 m2; 268.6s b573 m1; 283.2s b604 m0; 284.1s b606 m2; 289.3s b617 m1; 293.5s b626 m2; 296.3s b632 m0; 323.5s b690 m2; 351.1s b749 m1; 388.6s b829 m1; 389.6s b831 m3; 433.2s b924 m0
suggested next: grid.py fold with --spb 0.468761 --anchor 0.034, decide the bar line, then grid.py write
python3 "$KIT/grid.py" scan "shows/deadmau5 - Raise Your Weapon.mp3" 2>&1  3.24s user 1.03s system 109% cpu 3.902 total
tail -30  0.00s user 0.00s system 0% cpu 3.901 total
```

```
$ KIT="tools/showkit"; cd "~/deadmau5 app"; python3 "$KIT/grid.py" fold "shows/deadmau5 - Raise Your Weapon.mp3" --spb 0.468761 --anchor 0.034 2>&1 | head -160
bar 0 at 0.034 s, 127.997 BPM, 268 bars
bars 0-16   (16 steps, | every beat; one row per band)
   sub     @++=|+-+=|==#+|++==   peak 0.07
   bass    @+++|+===|==#=|=-==   peak 0.19
   lowmid  @...|....|..=.|....   peak 0.44
   mid     @ . |..  | .+ |  .    peak 0.34
   pres    @   |    |  + |       peak 0.05
   air     @:-=|===-|=++=|----   peak 0.00
bars 16-32   (16 steps, | every beat; one row per band)
   sub     @+*+|*=++|+=%=|====   peak 0.10
   bass    @++=|==-:|-:#-|---=   peak 0.22
   lowmid  @--=|-=--|=-#=|=---   peak 0.26
   mid     @.-:|:.=:|+:%:|:...   peak 0.25
   pres    @-@:|=-*:|#+%*|=+:=   peak 0.14
   air     *=@:|:**.|=*==|-::-   peak 0.19
bars 32-48   (16 steps, | every beat; one row per band)
   sub     %-#:|@:*-|#:@:|@:%:   peak 0.15
   bass    @=+-|+-=-|--#-|=-=-   peak 0.26
   lowmid  @-=-|=-=-|+-%-|*-=.   peak 0.28
   mid     #:=.|::+:|*+%:|@:+:   peak 0.18
   pres    @=%=|-#+=|@#@#|@-=-   peak 0.14
   air     +-*-|=#+=|+**@|@-#*   peak 0.18
bars 48-64   (16 steps, | every beat; one row per band)
   sub     @ . |@ . |@ . |@ .    peak 0.78
   bass    @:::|@:-.|%.:.|#.:.   peak 0.69
   lowmid  @=+.|@=+.|@-*.|%-+:   peak 0.35
   mid     % - |@ = |@ + |@ =    peak 0.94
   pres    @ : |@ : |@ - |@ :    peak 1.52
   air     @ . |@ . |@ . |@ .    peak 1.48
bars 64-80   (16 steps, | every beat; one row per band)
   sub     % ==|@ ==|@ =-|%.==   peak 0.43
   bass    @:-:|@--:|@--:|@--:   peak 0.60
   lowmid  *-=:|@-=:|#-#:|%-#:   peak 0.42
   mid     # - |# + |@ + |%.+    peak 0.68
   pres    % = |# = |@ = |% +.   peak 1.09
   air     % % |+ # |@ # |* %.   peak 1.07
bars 80-96   (16 steps, | every beat; one row per band)
   sub     #.+-|@.==|@.=-|% --   peak 0.43
   bass    @--:|%-=:|@--:|%--:   peak 0.58
   lowmid  +-%:|@-@:|#=@:|#-@:   peak 0.39
   mid
... [cut] ...
ry beat; one row per band)
   sub     @#%*|*@#*|#*%*|%%%@   peak 0.07
   bass    #+#+|+@**|@*##|##**   peak 0.14
   lowmid  ++%*|*@*+|%##+|*#+*   peak 0.15
   mid     +=#%|-%==|#+#+|-@+*   peak 0.10
   pres    . *@|-:.=|--:-| ++:   peak 0.07
   air     . +@|--.+|:-.:| =#:   peak 0.07
bars 256-268   (16 steps, | every beat; one row per band)
   sub     *#@*|#*##|*+@*|+**=   peak 0.05
   bass    **@#|**+=|==+=|===*   peak 0.15
   lowmid  +=@*|**==|*=-=|===@   peak 0.10
   mid     =:@+|-==-|----|::-%   peak 0.09
   pres      @ |    |    |   :   peak 0.02
   air     *%@*|###*|##%*|+=%%   peak 0.00
```

```
$ KIT="tools/showkit"; cd "~/deadmau5 app"; cat > "$KIT/work/weapon/tempogram.py" <<'EOF'
import sys, numpy as np, os
KIT=sys.argv[1]; sys.path.insert(0,KIT); sys.path.insert(0,os.getcwd())
import grid
d=grid.env_of("shows/deadmau5 - Raise Your Weapon.mp3")
od=grid.onsets(d); tt=d["tt"]; dt=tt[1]-tt[0]
dur=float(d["dur"])
print("dur",dur,"dt",dt)
win=30.0
cands=np.arange(60,190,0.25)
for t in np.arange(0,dur-win,15.0):
    a=int(t/dt); b=int((t+win)/dt)
    x=od[a:b]; x=x-x.mean()
    # comb score per tempo using autocorrelation
    ac=np.correlate(x,x,'full')[len(x)-1:]
    ac=ac/ max(ac[0],1e-9 ... [cut]
dur 502.9365986394558 dt 0.011609977324263037
   0.0  64.00(0.44)  128.50(0.26)  173.50(0.23)  171.25(0.20)
  15.0  99.50(0.34)  189.75(0.31)   97.00(0.28)  187.50(0.28)
  30.0  63.25(0.14)  126.00(0.09)   99.50(0.08)   84.75(0.07)
  45.0  64.50(0.10)  104.50(0.09)   90.50(0.09)  160.25(0.09)
  60.0  64.25(0.10)  104.50(0.08)  123.00(0.08)   85.50(0.07)
  75.0 127.75(2.18)   64.00(2.11)   85.50(1.57)  130.00(0.99)
  90.0  64.00(2.49)  127.75(2.46)   85.50(1.86)  170.75(1.07)
 105.0 127.75(2.19)   64.00(2.18)   85.50(1.73)  170.75(1.04)
 120.0  64.00(1.93)  127.75(1.92)   85.50(1.65)  170.75(0.98)
 135.0  64.00(2.02)  127.75(2.00)   85.50(1.75)  170.75(1.04)
 150.0  64.00(2.01)  127.75(2.00)   85.50(1.76)  170.75(1.04)
 165.0 127.75(2.22)   64.00(2.22)   85.50(2.06)  170.75(1.33)
 180.0  64.00(2.46)  127.75(2.43)   85.25(2.34)  102.25(1.60)
 195.0 127.75(1.78)   64.00(1.69)   85.25(1.64)  170.75(1.14)
 210.0  66.75(0.18)  134.25(0.16)  136.50(0.10)   90.25(0.09)
 225.0  70.00(0.83)  139.75(0.72)   93.25(0.59)  186.25(0.48)
 240.0  70.00(1.06)  139.75(0.78)   93.25(0.71)  186.25(0.60)
 255.0  70.00(0.99)  139.75(0.79)   93.25(0.63)  186.25(0.52)
 270.0  70.00(1.02)  139.75(0.79)   93.25(0.53)  186.25(0.41)
 285.0  70.00(0.93)  139.75(0.70)   93.25(0.50)  186.25(0.43)
 300.0  70.00(1.05)  139.75(0.76)   93.25(0.58)  186.25(0.45)
 315.0  70.00(1.07)  139.75(0.81)   93.25(0.53)  186.25(0.39)
 330.0  70.00(1.07)  139.75(0.87)   93.25(0.53)  142.00(0.39)
 345.0  70.00(0.97)  139.75(0.76)   93.50(0.48)  186.25(0.37)
 360.0  70.00(0.86)  139.75(0.67)   93.25(0.44)  186.25(0.36)
 375.0  70.00(0.93)  139.75(0.76)   93.50(0.54)  112.25(0.40)
 390.0  70.00(1.04)  139.75(0.78)   93.25(0.55)  186.25(0.41)
 405.0  70.00(1.01)  139.75(0.82)   93.25(0.54)  186.25(0.40)
 420.0 139.75(1.57)   70.00(1.55)   93.50(1.19)  142.00(0.80)
 435.0 139.75(2.29)   70.00(2.21)   93.50(1.85)  142.00(1.26)
 450.0 139.75(1.48)   70.00(1.23)   93.25(0.96)  142.00(0.73)
 465.0 139.75(0.50)  123.00(0.46)  189.75(0.43)  110.00(0.42)
```

```
$ cd "~/deadmau5 app"; wc -l mau5scene.py mau5show.py mau5song.py mau5engine.py mau5fx.py mau5offline.py; grep -n "holds\|\.beats\|def grid\|\"grid\"\|'grid'\|spb" mau5scene.py | head -80; echo ----; grep -n "holds\|\.beats\|\"grid\"\|'grid'" mau5show.py mau5song.py remote/offline/*.js mau5offline.py | head -60
    1344 mau5scene.py
    1000 mau5show.py
     718 mau5song.py
    1388 mau5engine.py
     992 mau5fx.py
    1085 mau5offline.py
    6527 total
5:from a pool and holds it.  It follows the music's level and lands on its
26:the grid holds still for (grid_of).  That one decision buys three things.  The phone and the laptop can agree to the
35:remote/offline/show.js holds the JavaScript twin of Scenes below.  The
37:test holds them to a hundredth of a count.
151:def grid_of(music):
154:    Scenes put every frame on t0 + beats * spb.  That is only the music's
165:    beats = np.asarray(music.beats, float)
172:    spb = float((beats[-1] - beats[0] - held[-1]) / (len(beats) - 1))
175:    off = np.abs(beats - held - (beats[0] + spb * np.arange(len(beats)))).max()
177:    boff = np.abs(bars - barheld - (t0 + 4.0 * spb * np.arange(len(bars)))).max()
183:    grid = {"t0": t0, "spb": spb}
186:        grid["holds"] = [[float(k + 1 - first), float(late[k] / spb)] for k in seams]
422:            span_s = float(span) * self.grid["spb"]
513:        grid = {"t0": self.grid["t0"], "spb": self.grid["spb"],
515:        if self.grid.get("holds"):
516:            grid["holds"] = self.grid["holds"]
518:                "grid": grid, "bars": nb, "pal": self.pal,
652:        if (g["t0"] != spec["grid"]["t0"] or g["spb"] != spec["grid"]["spb"]
653:                or g.get("holds") != spec["grid"].get("holds") or n != nb):
908:        g = spec["grid"]
909:        self.t0, self.spb = float(g["t0"]), float(g["spb"])
911:        self.holds = [(float(at), float(beats)) for at, beats in g.get("holds", ())]
913:        self.HB = PULSE_HOLD_S / self.spb
1135:            tl = lb * self.spb + P["tofs"]
1148:        B = (tt - self.t0) / self.spb
1149:        for at, beats in self.holds:
----
mau5song.py:16:
... [cut] ...
const P of x.layers) this._render(P, B, bar, hb, x.beats, hp, music, tt);
remote/offline/ui.js:479:// held the way NoSleep.js holds it, with a video playing: two seconds
remote/offline/ui.js:1335:const grid = $('grid');
remote/offline/wire.js:163:// next frame goes whole.  With three in flight a lost pong only holds
remote/offline/wire.js:733:  // WLED's nightlight in "instant" mode holds brightness and then
remote/offline/engine.js:811:// tell 12 from 12.0, so they are named.  test_mau5 holds both lists to
mau5offline.py:862:    They did, by design -- a frozen segment holds the last frame for
```

```
$ cd "~/deadmau5 app"; sed -n 1,60p mau5scene.py; sed -n 145,200p mau5scene.py; sed -n 1140,1165p mau5scene.py; sed -n 700,725p remote/offline/show.js; sed -n 120,140p mau5show.py
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
ows", "scenes",
                             os.path.splitext(os.path.basename(path))[0] + ".beats")
        an = (mau5song.analyse(path, beats_file=beats, downbeat=0, verbose=verbose)
              if os.path.exists(beats) else mau5song.analyse(path, verbose=verbose))
        self.duration = an["duration"]
        self.bpm = an["bpm"]
        self.beats = an["beats"]
        self.bars = an["bars"]
        self.levels = an["levels"]
        self.energy, self.onset = mau5song.frame_curves(
            an["audio"], an["sr"], an["env"], an["env_fps"], an["env_t0"],
            fps, self.duration)
```

```
$ KIT="tools/showkit"; cd "~/deadmau5 app"; cat > "$KIT/work/weapon/sections.py" <<'EOF'
import sys, numpy as np, os
KIT=sys.argv[1]; sys.path.insert(0,KIT); sys.path.insert(0,os.getcwd())
import grid
d=grid.env_of("shows/deadmau5 - Raise Your Weapon.mp3")
def rf(lo,hi,bpm,w=0.01,steps=201):
    b=grid.refine(d,60/bpm,lo,hi,width=w,steps=steps)
    return b
for lo,hi,bpm in [(0,90,128),(30,90,128),(90,210,128),(90,150,128),(150,210,128),(225,470,140),(225,340,140),(340,470,140),(420,470,140),(225,300,140)]:
    sc,s,p=rf(lo,hi,bpm)
    print("%4d-%4d: spb %.6f BPM %.3f  phase16 %.3f  score %.3f"% ... [cut]
   0-  90: spb 0.470953 BPM 127.401  phase16 0.117  score 0.211
  30-  90: spb 0.470953 BPM 127.401  phase16 30.024  score 0.273
  90- 210: spb 0.468750 BPM 128.000  phase16 90.027  score 1.230
  90- 150: spb 0.468797 BPM 127.987  phase16 90.021  score 1.326
 150- 210: spb 0.468797 BPM 127.987  phase16 150.024  score 1.157
 225- 470: spb 0.428571 BPM 140.000  phase16 225.105  score 0.736
 225- 340: spb 0.428571 BPM 140.000  phase16 225.105  score 0.755
 340- 470: spb 0.428571 BPM 140.000  phase16 340.069  score 0.717
 420- 470: spb 0.428614 BPM 139.986  phase16 420.102  score 0.646
 225- 300: spb 0.428571 BPM 140.000  phase16 225.105  score 0.752
```

```
$ cd "~/deadmau5 app"; grep -n "holds\|LINEAR_TOL\|nbars\|bars" tests_more/scenes.py | head -50; grep -n "holds" test_mau5.py | head; sed -n 590,625p mau5song.py; grep -n "beats_file" mau5song.py; git -C "~/deadmau5 app" log --oneline -3 -- mau5song.py
44:    holds = g.get("holds") or []
48:                + sum(beats * spb for beat, beats in holds if 4.0 * bar > beat))
51:    for beat, beats in holds:
64:    ts += [at(-1) - 0.5, at(spec["bars"]) + 0.5]
472:def t_scene_grid_holds_for_a_seam():
482:    song.beats, song.bars = straight, straight[::4]
484:    ok("holds" not in g, "a straight grid grew a hold: %s" % g)
485:    eq(n, 16, "bars")
489:    song.beats, song.bars = late, late[::4]
491:    eq(g["holds"], [[32.0, g["holds"][0][1]]], "the hold's place")
492:    ok(abs(g["holds"][0][1] - 0.4) < 1e-9, "a hold of 0.2 s is 0.4 beats: %s" % g)
497:    song.beats, song.bars = early, early[::4]
506:    at, beats = spec["grid"]["holds"][0]
528:         t_scene_grid_holds_for_a_seam, t_sprite_reaches_the_jaw_only_when_asked]
405:def t_floor_holds_the_shape():
923:    shed for that long, plus one bucketful.  That holds for any
1473:              t_floor_holds_the_shape, t_connector_limit,
            offset = off if offset is None else offset
        else:
            conf = float("nan")
            if offset is None:
                grid = np.arange(0, 60.0 / bpm, 0.005)
                idx = np.clip((((grid[:, None] + np.arange(0, dur, 60.0 / bpm)[None, :])
                                - env_t0) * fps).astype(int), 0, len(env) - 1)
                offset = float(grid[int(np.argmax(env[idx].sum(1)))])
        beats = beat_grid(bpm, offset, dur)

    ph = downbeat_phase(env, fps, beats - env_t0) if downbeat is None else downbeat
    bars = beats[ph::4]
    if len(bars) < 4:                     # three whole bars, see above
        raise ValueError("%s is %.1f s long and holds %d downbeat%s at "
                         "%.1f bpm; the analysis needs at least four"
                         % (path, dur, len(bars), "" if le
... [cut] ...
s()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter,
                                 epilog=__doc__)
    ap.add_argument("audio", nargs="+")
564:def analyse(path, bpm=None, offset=None, beats_file=None, verbose=True, downbeat=None):
583:    if beats_file:
584:        beats = mau5fx.Beats.from_file(beats_file).times
3c46af5 Relay opens when asked, song refuses a stinger, cal stops trusting old frames
68220e1 A beat the phone can see, shows that lock there too, and honest live bands
9d6eb1f Rebuild the show engine: phrases, layers, dynamics and cue gain
```

```
$ KIT="tools/showkit"; cd "~/deadmau5 app"; cat > "$KIT/work/weapon/sections.py" <<'EOF'
import sys, numpy as np, os
KIT=sys.argv[1]; sys.path.insert(0,KIT); sys.path.insert(0,os.getcwd())
import grid
d=grid.env_of("shows/deadmau5 - Raise Your Weapon.mp3")
def rf(lo,hi,bpm,w=0.01,steps=201):
    b=grid.refine(d,60/bpm,lo,hi,width=w,steps=steps)
    return b
for lo,hi,bpm in [(0,90,128),(30,90,128),(90,210,128),(90,150,128),(150,210,128),(225,470,140),(225,340,140),(340,470,140),(420,470,140),(225,300,140)]:
    sc,s,p=rf(lo,hi,bpm)
    print("%4d-%4d: spb %.6f BPM %.3f  phase16 %.3f  score %.3f"% ... [cut]
   0-  90: spb 0.470953 BPM 127.401  phase16 0.117  score 0.211
  30-  90: spb 0.470953 BPM 127.401  phase16 30.024  score 0.273
  90- 210: spb 0.468750 BPM 128.000  phase16 90.027  score 1.230
  90- 150: spb 0.468797 BPM 127.987  phase16 90.021  score 1.326
 150- 210: spb 0.468797 BPM 127.987  phase16 150.024  score 1.157
 225- 470: spb 0.428571 BPM 140.000  phase16 225.105  score 0.736
 225- 340: spb 0.428571 BPM 140.000  phase16 225.105  score 0.755
 340- 470: spb 0.428571 BPM 140.000  phase16 340.069  score 0.717
 420- 470: spb 0.428614 BPM 139.986  phase16 420.102  score 0.646
 225- 300: spb 0.428571 BPM 140.000  phase16 225.105  score 0.752
```

```
$ cd "~/deadmau5 app"; grep -n "holds\|LINEAR_TOL\|nbars\|bars" tests_more/scenes.py | head -50; grep -n "holds" test_mau5.py | head; sed -n 590,625p mau5song.py; grep -n "beats_file" mau5song.py; git -C "~/deadmau5 app" log --oneline -3 -- mau5song.py
44:    holds = g.get("holds") or []
48:                + sum(beats * spb for beat, beats in holds if 4.0 * bar > beat))
51:    for beat, beats in holds:
64:    ts += [at(-1) - 0.5, at(spec["bars"]) + 0.5]
472:def t_scene_grid_holds_for_a_seam():
482:    song.beats, song.bars = straight, straight[::4]
484:    ok("holds" not in g, "a straight grid grew a hold: %s" % g)
485:    eq(n, 16, "bars")
489:    song.beats, song.bars = late, late[::4]
491:    eq(g["holds"], [[32.0, g["holds"][0][1]]], "the hold's place")
492:    ok(abs(g["holds"][0][1] - 0.4) < 1e-9, "a hold of 0.2 s is 0.4 beats: %s" % g)
497:    song.beats, song.bars = early, early[::4]
506:    at, beats = spec["grid"]["holds"][0]
528:         t_scene_grid_holds_for_a_seam, t_sprite_reaches_the_jaw_only_when_asked]
405:def t_floor_holds_the_shape():
923:    shed for that long, plus one bucketful.  That holds for any
1473:              t_floor_holds_the_shape, t_connector_limit,
            offset = off if offset is None else offset
        else:
            conf = float("nan")
            if offset is None:
                grid = np.arange(0, 60.0 / bpm, 0.005)
                idx = np.clip((((grid[:, None] + np.arange(0, dur, 60.0 / bpm)[None, :])
                                - env_t0) * fps).astype(int), 0, len(env) - 1)
                offset = float(grid[int(np.argmax(env[idx].sum(1)))])
        beats = beat_grid(bpm, offset, dur)

    ph = downbeat_phase(env, fps, beats - env_t0) if downbeat is None else downbeat
    bars = beats[ph::4]
    if len(bars) < 4:                     # three whole bars, see above
        raise ValueError("%s is %.1f s long and holds %d downbeat%s at "
                         "%.1f bpm; the analysis needs at least four"
                         % (path, dur, len(bars), "" if le
... [cut] ...
s()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter,
                                 epilog=__doc__)
    ap.add_argument("audio", nargs="+")
564:def analyse(path, bpm=None, offset=None, beats_file=None, verbose=True, downbeat=None):
583:    if beats_file:
584:        beats = mau5fx.Beats.from_file(beats_file).times
3c46af5 Relay opens when asked, song refuses a stinger, cal stops trusting old frames
68220e1 A beat the phone can see, shows that lock there too, and honest live bands
9d6eb1f Rebuild the show engine: phrases, layers, dynamics and cue gain
```

```
$ KIT="tools/showkit"; cd "~/deadmau5 app"; cat > "$KIT/work/weapon/spec.py" <<'EOF'
#!/usr/bin/env python3
# spec.py out.png t0 t1 [--grid "anchor:spb:every[,anchor:spb:every]"]  -- spectrogram over seconds, with grid lines
import sys, subprocess, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
out=sys.argv[1]; t0=float(sys.argv[2]); t1=float(sys.argv[3])
grids=[]
if len(sys.argv)>4:
    for g in sys.argv[4].split(","):
        a,s,e=g.split(":"); grids.append((float(a),float(s),int(e)))
mp3="shows/deadmau5 - Raise Your Weapon.mp3"
raw=subprocess.run(["ffmpeg ... [cut]
tools/showkit/songs/weapon/whole.png
```

```
$ KIT="tools/showkit"; cd "~/deadmau5 app"; W="$KIT/work/weapon"; python3 "$W/spec.py" "$W/z1.png" 200 250 0.027:0.46875:4; python3 "$W/spec.py" "$W/z2.png" 60 100 0.027:0.46875:4
tools/showkit/songs/weapon/z1.png
tools/showkit/songs/weapon/z2.png
```

```
$ KIT="tools/showkit"; cd "~/deadmau5 app"; W="$KIT/work/weapon"; python3 "$W/spec.py" "$W/z3.png" 236 252 241.91:0.4285714:4; cat > "$W/fold140.py" <<'EOF'
import sys, numpy as np, os
KIT=sys.argv[1]; sys.path.insert(0,KIT); sys.path.insert(0,os.getcwd())
import grid
d=grid.env_of("shows/deadmau5 - Raise Your Weapon.mp3")
od=grid.onsets(d); tt=d["tt"]; dt=tt[1]-tt[0]
# best 16th phase in the 140 section
spb=60/140.
s16=spb/4
ph=np.arange(0,s16,0.001)
for lo,hi in [(242,300),(300,360),(360,430),(242,430)]:
    sc=[grid.comb(od,tt[0],dt,np.arange(lo+p,hi,s16)) for p in ph]
    i=int(np.argmax(sc)) ... [cut]
tools/showkit/songs/weapon/z3.png
242 300 phase 0.033 -> first 16th at 242.033  contrast 2.24
300 360 phase 0.105 -> first 16th at 300.105  contrast 2.04
360 430 phase 0.103 -> first 16th at 360.103  contrast 2.02
242 430 phase 0.033 -> first 16th at 242.033  contrast 2.10
sub 241.290 241.731 241.743 242.579 242.590 243.020 243.380 243.531 243.670 243.821 244.193 244.506 244.518 245.586
bass 241.279 241.290 241.720 241.731 242.579 242.730 243.183 243.473 243.612 243.868 244.077 244.332 244.506 244.727
lowmid 241.035 241.046 241.279 241.511 241.522 241.720 241.929 242.567 242.997 243.856 244.181 244.495 245.574 245.992
mid 239.363 239.792 239.804 241.232 241.279 241.511 241.708 241.917 241.929 242.567 242.776 242.997 244.703 244.715
pres 239.212 239.363 239.375 239.792 241.279 241.708 241.929 242.138 242.567 242.985 242.997 243.856 244.703 244.715
air 239.084 239.212 239.224 240.965 241.279 242.138 242.358 242.556 242.567 242.997 244.703 244.715 245.145 245.992
```

```
$ cd "~/deadmau5 app"; sed -n 575,592p mau5song.py; sed -n 36,70p tests_more/scenes.py; grep -n "class Beats" -A32 mau5fx.py | head -70; grep -n "LINEAR_TOL_S =" mau5scene.py; grep -n "\.bpm\|\bbpm\b" mau5show.py | head -30
    # empty", or returned three levels for one bar and sections that ran
    # past the end of the bar list.  A stinger has no bars to light.
    if len(a) < N_FFT + 40 * HOP:
        raise ValueError("%s is %.2f s long; the analysis needs at least "
                         "%.2f s, and a show wants several bars"
                         % (path, dur, (N_FFT + 40 * HOP) / float(sr)))
    env, fps, env_t0 = onset_envelope(a, sr)

    if beats_file:
        beats = mau5fx.Beats.from_file(beats_file).times
        bpm = 60.0 / float(np.median(np.diff(beats))) if len(beats) > 2 else 0.0
        conf = float("nan")
    else:
        if bpm is None:
            bpm, off, conf = estimate_tempo(env, fps, t0=env_t0)
            offset = off if offset is None else offset
        else:
            conf = float("nan")
    """Where a scene show is most likely to disagree with itself.

    Just inside every edge, the middle of everything, inside the peak
    hold of every hit, the middle of every dark beat before a drop, a
    spread across the song, and one moment either side of it.
    """
    g = spec["grid"]
    t0, spb, lead = g["t0"], g["spb"], g.get("lead", 0.0)
    holds = g.get("holds") or []

    def at(bar):
        return (t0 + 4.0 * bar * spb - lead
                + sum(beats * spb for beat, beats in holds if 4.0 * bar > beat))

    ts = []
    for beat, beats in holds:
        a = at(beat / 4.0)
        ts += [a - 0.001, a + 0.001, a + beats * spb / 2.0,
               a + beats * spb - 0.001, a + beats * spb + 0.001]
    for s in spec["scenes"]:
        a, b = at(s["from"]), at(s["to"])
        ts += [a + 0.001, (a + b) / 2.0, b - 0.001]
        if s["out"] > 0:
            ts.append(b - s["out"] * spb / 2.0)
    for x in spec["hits"]:
        a = at(x["at"])
       
... [cut] ...
0 / max(float(bpm or 0.0), 1e-6)
630:def accent_level(bpm):
638:    makes it about half as tall (0.22 at 128 bpm, 0.16 at 174).
640:    spb = 60.0 / max(float(bpm or 0.0), 1e-6)
817:            bpm = getattr(self.music, "bpm", 0.0)
819:                self.gain = beat_gain(ph, bpm, self.pulse * (0.4 + 0.3 * lvl))
824:                k = accent_level(bpm)
980:            print("  %.1f s, %.1f bpm, %d cues" % (show["duration"], show["bpm"], len(show["cues"])))
995:                print("  %-34s %6.1fs  %5.1f bpm  %2d cues"
996:                      % (f, s["duration"], s["bpm"], len(s["cues"])))
```

```
$ KIT="tools/showkit"; cd "~/deadmau5 app"; W="$KIT/work/weapon"; python3 "$W/spec.py" "$W/z4.png" 425 503 242.14:0.4285714:16; python3 "$W/spec.py" "$W/z5.png" 0 62 0.027:0.46875:4
tools/showkit/songs/weapon/z4.png
tools/showkit/songs/weapon/z5.png
```

```
$ KIT="tools/showkit"; cd "~/deadmau5 app"; W="$KIT/work/weapon"; python3 "$KIT/grid.py" fold "shows/deadmau5 - Raise Your Weapon.mp3" --spb 0.42857143 --anchor 242.14 --spans "141-149,149-157,157-165,165-173,173-181,181-197,197-213,213-229,229-237,237-241,241-249,249-265,265-293" 2>&1 | head -100; cat > "$W/lag.py" <<'EOF'
import sys, numpy as np, os
KIT=sys.argv[1]; sys.path.insert(0,KIT); sys.path.insert(0,os.getcwd())
import grid
d=grid.env_of("shows/deadmau5 - Raise Your Weapon.mp3")
tt=d["tt"]; dt=tt[1]-tt[0]
M=np.stack([d[n] for n,_,_ in grid.BANDS],1)
def best(a0,a1,exp,w=3.0):
    i0,i1= ... [cut]
bar 0 at 0.426 s, 140.000 BPM, 293 bars
bars 141-149   (16 steps, | every beat; one row per band)
   sub     %.:%|@.%.|*+#-|-##:   peak 0.48
   bass    @:#%|@.@=|#-#*|::++   peak 0.41
   lowmid  @-+#|*:%:|@:--|-.:-   peak 0.47
   mid     =.:*|=.=.|@ ..|: ::   peak 0.62
   pres    *::*|+.=:|@ ..|+ -    peak 0.69
   air     +.-+|# =.|@ -:|* -    peak 0.75
bars 149-157   (16 steps, | every beat; one row per band)
   sub     @ :@|@.@.|*==:|.**:   peak 0.52
   bass    #.=#|#.@:|+-==|.:-=   peak 0.57
   lowmid  @.-*|*.%.|*..-|::::   peak 0.66
   mid     @ -#|#.# |% ..|-.:.   peak 0.77
   pres    @.=%|@.%:|@ :.|* -    peak 0.74
   air     # =#|@.*.|@ -:|+ =.   peak 0.83
bars 157-165   (16 steps, | every beat; one row per band)
   sub     @ .*|+.*.|+=+:|.+#.   peak 0.60
   bass    @:**|+:*:|+.*=|::++   peak 0.60
   lowmid  %--%|+.%.|@:--|-.:-   peak 0.47
   mid     =.:+|:.=:|@ ::|:..:   peak 0.68
   pres    *.:*|-.+.|@ ..|* :    peak 0.75
   air     +.:*|= =.|@ :.|+ -    peak 0.81
bars 165-173   (16 steps, | every beat; one row per band)
   sub     @ :#|@-@-|#=*:|:#+-   peak 0.53
   bass    * -*|*:@-|*::=|..:=   peak 0.61
   lowmid  %.=#|*-@-|@.:-|-.::   peak 0.53
   mid     #.=%|=.#-|@ .:|: :.   peak 0.68
   pres    * -#|=.#.|@ ..|= :    peak 0.87
   air     + -*|+ +.|@ -:|+ -.   peak 0.86
bars 173-181   (16 steps, | every beat; one row per band)
   sub     @ :%|@:%.|**#:|-#*-   peak 0.46
   bass    @-+#|@.%-|*:-*|::=+   peak 0.47
   lowmid  @:=@|+:@-|@--+|=::-   peak 0.41
   mid     *.=*|=.+-|@ .-|...:   peak 0.53
   pres    +.:*|= =.|@ ..|- :    peak 0.69
   air     +.-*|*:=.|@ ::|+ -.   peak 0.68
bars 181-197   (16 steps, | every beat; one row per band)
   sub     @ :%|@:%.|*+#:|:**-   peak 0.47
   bass    @.##|#:%-|*:++|::=*   peak 0.49
   lowmid  %:=%|*:%:|@::=|-:--   pea
... [cut] ...
.07
   bass    @*++|++==|=-=-|---=   peak 0.19
   lowmid  @:::|::::|::=:|::::   peak 0.28
   mid     @...|....|..+.|....   peak 0.25
   pres    @   |:   |: + |.      peak 0.06
   air     % : |@ . |# : |* :    peak 0.02
vocal 60-88 vs 210-238, expected 150: (np.float32(0.46671498), np.float64(149.90249433106737))
vocal 66-78 vs ...: (np.float32(0.7365885), np.float64(149.80961451247322))
vocal 78-87 vs ...: (np.float32(0.6608676), np.float64(149.0549659863957))
intro 0-28 vs outro? expected ~445 (at 128 vs 140 this will not match cleanly): (np.float32(0.42589507), np.float64(459.9344217687269))
```

```
$ KIT="tools/showkit"; cd "~/deadmau5 app"; W="$KIT/work/weapon"; cat > "$W/lag2.py" <<'EOF'
import sys, numpy as np, os, subprocess
mp3="shows/deadmau5 - Raise Your Weapon.mp3"
raw=subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-i",mp3,"-ac","1","-ar","11025","-f","f32le","-"],capture_output=True,check=True).stdout
m=np.frombuffer(raw,dtype=np.float32)
SR=11025; N=1024; H=64
def stft(a,b):
    x=m[int(a*SR):int(b*SR)]
    n=(len(x)-N)//H
    win=np.hanning(N)
    F=np.abs(np.fft.rfft(np.stack([x[i*H:i*H+N]*win for i in range(n)]),axis=1))
    # 40 log bands
    f=np.fft.rfftfreq(N, ... [cut]
dt 0.005804988662131519
t= 58.0  best lag 150.004 (corr 0.49)   next 149.969 (0.41)
t= 60.0  best lag 149.992 (corr 0.87)   next 150.027 (0.74)
t= 62.0  best lag 149.981 (corr 0.89)   next 149.946 (0.77)
t= 64.0  best lag 149.957 (corr 0.94)   next 149.923 (0.82)
t= 66.0  best lag 149.911 (corr 0.93)   next 149.946 (0.84)
t= 68.0  best lag 149.888 (corr 0.90)   next 149.911 (0.85)
t= 70.0  best lag 149.807 (corr 0.93)   next 149.830 (0.89)
t= 72.0  best lag 149.737 (corr 0.89)   next 149.702 (0.86)
t= 74.0  best lag 149.644 (corr 0.83)   next 149.667 (0.81)
t= 76.0  best lag 149.574 (corr 0.82)   next 149.540 (0.79)
t= 78.0  best lag 149.412 (corr 0.85)   next 149.389 (0.82)
t= 80.0  best lag 149.389 (corr 0.85)   next 149.354 (0.78)
t= 82.0  best lag 149.156 (corr 0.87)   next 149.133 (0.86)
t= 84.0  best lag 149.029 (corr 0.83)   next 148.994 (0.79)
t= 86.0  best lag 148.913 (corr 0.78)   next 148.947 (0.76)
t= 88.0  best lag 148.657 (corr 0.40)   next 148.692 (0.38)
```

```
$ KIT="tools/showkit"; cd "~/deadmau5 app"; W="$KIT/work/weapon"; cat > "$W/anchors.py" <<'EOF'
import sys, numpy as np, os
KIT=sys.argv[1]; sys.path.insert(0,KIT); sys.path.insert(0,os.getcwd())
import grid
d=grid.env_of("shows/deadmau5 - Raise Your Weapon.mp3")
od=grid.onsets(d); tt=d["tt"]; dt=tt[1]-tt[0]
def phase(lo,hi,spb,nominal,band=None,step=0.0005):
    o=od if band is None else d[band+"_od"]
    s16=spb/4
    ph=np.arange(-s16/2,s16/2,step)
    sc=np.array([grid.comb(o,tt[0],dt,np.arange(nominal+p,hi,s16)) for p in ph])
    i=int(sc.argmax()); return nominal+ph[i], sc.max()/np.median(s ... [cut]
A   90.0- 150.0  beat at 90.0249 -> bar0 anchor 0.0249  contrast 4.89
A  150.0- 210.0  beat at 150.0269 -> bar0 anchor 0.0269  contrast 4.62
A   90.0- 210.0  beat at 90.0264 -> bar0 anchor 0.0264  contrast 4.79
C  242.1- 290.0  beat at 242.1399 -> anchor(242.14) 242.1399  contrast 2.22
C  290.0- 340.0  beat at 290.1399 -> anchor(242.14) 242.1399  contrast 2.10
C  340.0- 390.0  beat at 339.8532 -> anchor(242.14) 242.1389  contrast 2.05
C  390.0- 434.0  beat at 389.9956 -> anchor(242.14) 242.1384  contrast 2.05
C  242.1- 434.0  beat at 242.1399 -> anchor(242.14) 242.1399  contrast 2.09
sub A anchor 0.0419 (1.68)   C anchor 242.1604 (1.69)
bass A anchor 0.0394 (2.11)   C anchor 242.1514 (1.62)
lowmid A anchor 0.0309 (2.48)   C anchor 242.1399 (1.94)
mid A anchor 0.0254 (6.56)   C anchor 242.1384 (2.43)
pres A anchor 0.0249 (8.75)   C anchor 242.1384 (2.47)
air A anchor 0.0249 (7.83)   C anchor 242.1384 (2.81)
```

```
$ KIT="tools/showkit"; cd "~/deadmau5 app"; W="$KIT/work/weapon"; cat > "$W/write_beats.py" <<'EOF'
#!/usr/bin/env python3
"""Raise Your Weapon's real grid: 128.000 BPM for 112 bars, a 16-bar accelerando that is linear in
beats from 128 to 140, then 140.000 BPM to the end. Written as a beat list with every beat at or
above the 140 beat length (the format's holds can only delay), so 140 is the line and everything
before it is one hold per beat. The last beats of the ramp have under 5 ms each to hold, which the
format would drop as noise and then refuse the sum, so those are collected until there i ... [cut]
    4:46.71-5:00.42  lvl2  wipe       {'period': 0.857, 'a': (0, 255, 140), 'b': (0, 90, 255)}
    5:00.42-5:14.14  lvl2  vu         {}
    5:14.14-5:27.85  lvl2  rainbow    {'period': 6.0}
    5:27.85-5:41.57  lvl2  blades     {'period': 1.714}
    5:41.57-5:55.28  lvl2  eq         {}
    5:55.28-6:09.00  lvl2  wave       {'period': 1.6}
    6:09.00-6:22.71  lvl2  chase      {'period': 0.857}
    6:22.71-6:36.42  lvl2  comet      {'period': 1.6}
    6:36.42-6:50.14  lvl2  plasma     {}
    6:50.14-7:03.85  lvl2  fire       {}
    7:03.85-7:10.71  lvl2  rainbow    {'period': 6.0}
    7:10.71-7:24.42  lvl1  matrix     {}
    7:24.42-7:31.28  lvl1  spiral     {'period': 6.0}
    7:31.28-7:45.00  lvl0  scanner    {'bounce': False, 'period': 3.429}
    7:45.00-7:58.71  lvl1  wipe       {'period': 3.429, 'a': (255, 0, 120), 'b': (255, 200, 0)}
    7:58.71-8:05.57  lvl1  comet      {'period': 4.0}
    8:05.57-8:22.71  lvl0  wave       {'period': 5.0, 'length': 0.8}
ramp: bar 112 at 210.0264, bar 128 at 238.7113, 28.6849 s, the linear ramp predicts 28.6759 s, scale 1.000315
written vs true: worst 5.07 ms; last ramp holds: [40.2, 40.2, 40.2, 40.2, 40.2, 40.2, 40.2, 40.2, 40.0, 39.3, 38.6, 37.9, 37.3, 36.6, 35.9, 35.2, 34.6, 33.9, 33.2, 32.6, 31.9, 31.2, 30.6, 29.9, 29.3, 28.6, 28.0, 27.3, 26.7, 26.0, 25.4, 24.7, 24.1, 23.4, 22.8, 22.2, 21.5, 20.9, 20.3, 19.6, 19.0, 18.4, 17.8, 17.1, 16.5, 15.9, 15.3, 14.7, 14.1, 13.5, 12.8, 12.2, 11.6, 11.0, 10.4, 9.8, 9.2, 8.6, 8.0, 7.4, 6.8, 6.2, 5.7, -0.0, 9.6, -0.0, 7.2, -0.0, -0.0, 6.5, -0.0, -0.0, -0.0, -0.0, -0.0]
wrote shows/scenes/deadmau5 - Raise Your Weapon.beats 1129 beats 282 bars
-rw-r--r--@ 1 jones  staff    532200 Oct 31 12:45 shows/deadmau5 - Raise Your Weapon.analysis.npz
-rw-r--r--@ 1 jones  staff     12846 Oct 31 12:45 shows/deadmau5 - Raise Your Weapon.json
-rw-r--r--@ 1 jones  staff  12072377 Oct 31 12:37 shows/deadmau5 - Raise Your Weapon.mp3
     0     0.03s  energy 0.07  bass 0.13 (punch 1.00)  mid 0.01  high 0.00
     1     1.90s  energy 0.06  bass 0.10 (punch 1.00)  mid 0.03  high 0.00
     2     3.78s  energy 0.14  bass 0.27 (punch 1.00)  mid 0.04  high 0.00
['fps', 'duration', 'bpm', 'beats', 'bars', 'levels', 'energy', 'onset', 'sections', 'lock', 'v', 'chroma', 'shape', 'src', 'b_bass_e', 'b_bass_p', 'b_mid_e', 'b_mid_p', 'b_high_e', 'b_high_p']
bpm 139.9998133335721 bars 283 [0.0264 1.9014 3.7764] [235.258099 236.989158 238.709908 240.424194 242.138479 243.852765]
```

```
$ KIT="tools/showkit"; cd "~/deadmau5 app"; W="$KIT/work/weapon"; cat > "$W/gridcheck.py" <<'EOF'
#!/usr/bin/env python3
"""The real check for this grid: the written beat list, 16ths interpolated within each beat, against the audio, per 8 bars.
grid.py check cannot read a grid with hundreds of holds (it applies each hold by comparing an unheld time to a real one)."""
import sys, numpy as np, os
KIT=sys.argv[1]; sys.path.insert(0,KIT); sys.path.insert(0,os.getcwd())
import grid
BASE="deadmau5 - Raise Your Weapon"
d=grid.env_of("shows/%s.mp3"%BASE)
od=grid.onsets(d); tt=d["tt"]; dt=tt[1]-tt[0]
beat ... [cut]
0:+5(1.38)  8:+7(1.48)  16:+47(1.11)  24:-1(1.17)  32:-11(1.10)  40:+9(1.23)  48:-3(5.93)  56:-3(6.56)  64:-1(3.18)  72:-1(3.34)  80:-1(3.10)  88:-1(3.68)  96:+1(6.37)  104:+3(5.30)  112:+53(1.11)  120:+15(1.14)  128:+3(1.99)  136:-1(2.41)  144:+1(2.20)  152:+3(2.14)  160:+3(2.25)  168:-1(2.19)  176:+1(1.95)  184:+3(2.08)  192:+3(2.00)  200:-1(1.94)  208:+1(1.96)  216:+3(2.13)  224:+3(1.98)  232:-1(2.11)  240:+1(3.25)  248:+3(4.60)  256:+9(1.41)  264:+7(1.38)  272:+11(1.10)  280:-51(1.13)
worst 9 ms where contrast >= 1.15, mean +1.8 ms, 30 of 36 spans
deadmau5 - Raise Your Weapon: 140.000 BPM, 283 bars, bar 0 at 0.026 s, holds [(0.49515, 0.04017799999996896), (0.9639, 0.04017799999996896), (1.43265, 0.04017799999996896), (1.9014, 0.04017799999996896), (2.37015, 0.04017799999996918), (2.8389, 0.04017799999996896), (3.30765, 0.04017799999996896), (3.7764, 0.04017799999996896), (4.24515, 0.04017799999996852), (4.7139, 0.04017799999996896), (5.18265, 0.04017799999996896), (5.6514, 0.04017799999996896), (6.12015, 0.04017799999996896), (6.5889, 0.04017799999996896), (7.05765, 0.04017799999996896), (7.5264, 0.04017799999996896), (7.99515, 0.04017799999996896), (8.4639, 0.04017799999996985), (8.93265, 0.04017799999996896), (9.4014, 0.04017799999996896), (9.87015, 0.04017799999996896), (10.3389, 0.04017799999996896), (10.80765, 0.04017799999996896), (11.2764, 0.04017799999996896), (11.74515, 0.04017799999996896), (12.2139, 0.04017799999996896)
music against the grid per 8 bars, ms (contrast): 0:+10(1.09)  8:+52(1.11)  16:-2(1.08)  24:-30(1.32)  32:+32(1.15)  40:-36(1.36)  48:+36(1.55)  56:+44(1.31)  64:+20(1.27)  72:+26(1.15)  80:+0(1.10)  88:+10(1.20)  96:+16(1.11)  104:-30(1.19)  112:-50(1.07)  120:+38(1.13)  128:-24(1.25)  136:+4(1.96)  144:+0(2.18)  152:+4(2.13)  160:+2(2.23
... [cut] ...
-20 ms corr 0.96
phrase beat 20 (t=219.27): residual -43 ms corr 0.96
phrase beat 24 (t=221.09): residual -32 ms corr 0.95
phrase beat 28 (t=222.89): residual -43 ms corr 0.93
phrase beat 32 (t=224.69): residual -49 ms corr 0.86
phrase beat 36 (t=226.48): residual -78 ms corr 0.91
phrase beat 40 (t=228.25): residual -72 ms corr 0.83
phrase beat 44 (t=230.02): residual -78 ms corr 0.42
phrase beat 48 (t=231.78): residual -66 ms corr 0.79
phrase beat 52 (t=233.53): residual -78 ms corr 0.89
phrase beat 56 (t=235.26): residual -66 ms corr 0.76
phrase beat 60 (t=236.99): residual -183 ms corr 0.48
```

```
$ KIT="tools/showkit"; cd "~/deadmau5 app"; W="$KIT/work/weapon"; date; python3 "$KIT/songmap.py" "deadmau5 - Raise Your Weapon"
Sat Oct 31 12:45:38 PDT 2026
deadmau5 - Raise Your Weapon: 283 bars, 1.71 s a bar, 502.9 s
 bar     t   E  B  M  H  notes       change
   0    0.0   0  1  0  0  C A F       
   1    1.9   0  1  0  0  A A# F      
   2    3.8   1  2  0  0  C A D       
   3    5.7   0  1  0  0  C A# A      
   4    7.5   1  1  0  0  C F C#      
   5    9.4   1  1  0  0  C D C#      
   6   11.3   2  3  1  0  A C G       
   7   13.2   2  2  1  0  C A A#      
   8   15.0   2  3  0  0  C A A#      
   9   16.9   2  2  1  0  A C A#      
  10   18.8   0  1  2  0  A D F       
  11   20.7   0  0  0  0  C A# B      
  12   22.5   2  3  3  0  C F D       >>
  13   24.4   2  2  2  0  C C# D      
  14   26.3   3  3  3  0  A C G       
  15   28.2   1  1  2  0  E F A       
  16   30.0   5  3  6  4  C D A#      >>
  17   31.9   3  2  4  4  A C F       
  18   33.8   4  4  5  4  A D C       
  19   35.7   3  3  2  0  C A D       >>
  20   37.5   5  3  6  4  C D A       >>
  21   39.4   3  3  4  2  C D F       
  22   41.3   5  4  6  4  A D C       >>
  23   43.2   4  4  4  1  C A F       
  24   45.0   5  4  5  3  A# A C      
  25   46.9   3  4  4  0  C A A#      
  26   48.8   4  2  6  4  A A# D      >>
  27   50.7   1  0  2  1  C A# A      >>
  28   52.5   5  3  7  3  A# C F#     >>
  29   54.4   4  3  5  3  C D A       
  30   56.3   5  4  6  3  E A C       
  31   58.2   2  3  3  1  A C F       >>
  32   60.0   5  3  6  3  C D A#      >>
  33   61.9   4  2  5  3  A A# C      
  34   63.8   5  4  6  4  C A D       
  35   65.7   4  2  6  4  C A# A      
  36   67.5   5  3  6  3  A C D       
  37   69.4   3  3  4  3  C D F       
  38   71.3   5  4  7  3  A G# C      
  39   73.2   5  3  6  4  F# C A      
  40   75.0   5  4  6  5  C B A       
  41   76.9   4  4  4  2  C A F       
  42   
... [cut] ...
  0  C A A#      
 268  478.7   3  3  3  0  A D F       
 269  480.4   1  0  1  0  C A# A      >>
 270  482.1   4  4  4  0  C F D       >>
 271  483.9   3  3  3  0  C D A       
 272  485.6   4  5  4  0  A C D       
 273  487.3   2  3  2  0  A C F       
 274  489.0   0  2  0  0  A C G       
 275  490.7   0  0  0  0  A C G       
 276  492.4   0  0  0  0  A C D       
 277  494.1   0  0  0  0  A C D       
 278  495.9   0  0  0  0  A G C       
 279  497.6   0  0  0  0  A G C       
 280  499.3   0  0  0  0  A G C       
 281  501.0   0  0  0  0  A A# F      
 282  502.7   0  0  0  0  C C# D
```

```
$ KIT="tools/showkit"; cd "~/deadmau5 app"; W="$KIT/work/weapon"; B="deadmau5 - Raise Your Weapon"; python3 "$KIT/spectro.py" "$B" "$W/s_a.png" 0 48; python3 "$KIT/spectro.py" "$B" "$W/s_b.png" 48 112; python3 "$KIT/spectro.py" "$B" "$W/s_c.png" 112 146;  python3 "$KIT/spectro.py" "$B" "$W/s_d.png" 130 194; python3 "$KIT/spectro.py" "$B" "$W/s_e.png" 194 283
tools/showkit/songs/weapon/s_a.png
tools/showkit/songs/weapon/s_b.png
tools/showkit/songs/weapon/s_c.png
tools/showkit/songs/weapon/s_d.png
tools/showkit/songs/weapon/s_e.png
```

```
$ cd "~/deadmau5 app"; date; sed -n 60,145p mau5scene.py; sed -n 200,420p mau5scene.py
Sat Oct 31 12:47:20 PDT 2026
# The beat pulse's peak hold, the same 70 ms as mau5show.PULSE_HOLD_S:
# longer than the slowest gap between the phone's frames, so every
# gate, spark and blade is seen at its full height on either device
# before it decays.  Imported rather than copied, so they cannot part.
from mau5show import PULSE_HOLD_S  # noqa: E402

CELL = 16.7                 # mm per glyph column, TextScroll's default
LINEAR_TOL_S = 0.005        # a grid this far from straight is refused

FX = ("fill", "grad", "sweep", "sparks", "blades", "preset", "orb", "twinkle")
MIX = ("add", "max", "over")
# Only the presets that are stateless and already parity-tested between
# the two languages may be layers: a stateful one would remember a frame
# the other player never rendered.
PRESETS = ("text", "sprite", "eyes")
REGIONS = ("all", "shell", "ears", "ear1", "ear2", "tubes", "rims",
           "tube0", "tube1", "tube2", "left", "right", "face", "jaw",
           "rim1", "rim2", "tubes1", "tubes2")
AXES = ("x", "y", "r", "a", "al", "u")
WAVES = ("tri", "saw")
SHAPES = ("p", "saw", "tri")
MODES = ("band", "fill")
SIDES = ("both", "alt", "ear1", "ear2")

# Everything a layer may say, with its default.  The compiler writes
# every one of these into the show, so the phone has no table of
# defaults to keep in step: it evaluates exactly what is in the JSON.
COMMON = {"on": None, "mix": "add", "pal": None, "gain": 1.0, "c": 0.5,
          "gate": None, "env": None}
DEFAULT_ON = {"fill": "all", "grad": "shell", "sweep": "shell",
              "sparks": "shell", "blades": "ears", "preset": "face",
              "orb": "shell", "twinkle": "shell"}
FX_VALUES = {
    "fill": {},
    "grad": {"scale": 1.0, "speed": 0.0, "ofs": 0.0, "warp": 0.0,
             "wscale": 1.0, "wspeed": 0.0,
... [cut] ...
name]
        bad = set(params) - set(cls.params)
        if bad:
            raise TreatmentError("%s: %s has no parameter %s" % (what, name, sorted(bad)))
        tofs = 0.0
        if L.get("fit"):
            if name != "text":
                raise TreatmentError("%s: fit is for text" % what)
            # Enter on the right at the start, leave on the left at the
            # end, whatever the length of the word and of the moment.
            text = params.get("text", cls.params["text"])
            w = int(E._text_bitmap(text).shape[1])
            cell = float(params.get("cell", CELL))
```

```
$ cd "~/deadmau5 app"; sed -n 905,1140p mau5scene.py; sed -n 1165,1344p mau5scene.py
    def __init__(self, spec, helmet):
        self.spec = spec
        g = spec["grid"]
        self.t0, self.spb = float(g["t0"]), float(g["spb"])
        self.lead = float(g.get("lead", 0.0))
        self.holds = [(float(at), float(beats)) for at, beats in g.get("holds", ())]
        self.nbars = float(spec["bars"])
        self.HB = PULSE_HOLD_S / self.spb
        self.h = h = _h32(helmet)
        self.n = h.n
        self.pal = {k: (np.array(p["stops"], float), bool(p["wrap"]), len(p["stops"]))
                    for k, p in spec["pal"].items()}
        al = np.maximum(h.along, 0.0)
        self.axes = {"x": h.nfa, "y": h.nel, "r": h.er, "a": h.ea, "al": al, "u": h.u}
        self.al = al
        self.scenes = [self._scene(s) for s in spec["scenes"]]
        self.hits = [{"name": x["name"], "at": float(x["at"]), "beats": float(x["beats"]),
                      "layers": [self._layer(L) for L in x["layers"]]}
                     for x in spec["hits"]]
        self.acc = np.zeros((self.n, 3))

    def _scene(self, s):
        p = s.get("pump")
        return {"name": s["name"], "from": float(s["from"]), "to": float(s["to"]),
                "out": float(s["out"]),
                "pump": (p["pat"], float(p["step"]), float(p["decay"]), float(p["depth"]))
                if p else None,
                "layers": [self._layer(L) for L in s["layers"]]}

    def _layer(self, L):
        h = self.h
        fx = L["fx"]
        m = _region_mask(h, L["on"])
        idx = np.where(m)[0]
        g = L.get("gate")
        P = {"fx": fx, "mix": MIX.index(L["mix"]), "idx": idx,
             "pal": self.pal[L["pal"]],
             "gain": _Val(L["gain"]), "c": _Val(L["c"]),
             "gate": (g["pat"], float(g["step"]), float(g["decay"]), float(g["floor"]))
             if g 
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
$ cd "~/deadmau5 app"; date; sed -n 60,145p mau5scene.py; sed -n 200,420p mau5scene.py
Sat Oct 31 12:47:20 PDT 2026
# The beat pulse's peak hold, the same 70 ms as mau5show.PULSE_HOLD_S:
# longer than the slowest gap between the phone's frames, so every
# gate, spark and blade is seen at its full height on either device
# before it decays.  Imported rather than copied, so they cannot part.
from mau5show import PULSE_HOLD_S  # noqa: E402

CELL = 16.7                 # mm per glyph column, TextScroll's default
LINEAR_TOL_S = 0.005        # a grid this far from straight is refused

FX = ("fill", "grad", "sweep", "sparks", "blades", "preset", "orb", "twinkle")
MIX = ("add", "max", "over")
# Only the presets that are stateless and already parity-tested between
# the two languages may be layers: a stateful one would remember a frame
# the other player never rendered.
PRESETS = ("text", "sprite", "eyes")
REGIONS = ("all", "shell", "ears", "ear1", "ear2", "tubes", "rims",
           "tube0", "tube1", "tube2", "left", "right", "face", "jaw",
           "rim1", "rim2", "tubes1", "tubes2")
AXES = ("x", "y", "r", "a", "al", "u")
WAVES = ("tri", "saw")
SHAPES = ("p", "saw", "tri")
MODES = ("band", "fill")
SIDES = ("both", "alt", "ear1", "ear2")

# Everything a layer may say, with its default.  The compiler writes
# every one of these into the show, so the phone has no table of
# defaults to keep in step: it evaluates exactly what is in the JSON.
COMMON = {"on": None, "mix": "add", "pal": None, "gain": 1.0, "c": 0.5,
          "gate": None, "env": None}
DEFAULT_ON = {"fill": "all", "grad": "shell", "sweep": "shell",
              "sparks": "shell", "blades": "ears", "preset": "face",
              "orb": "shell", "twinkle": "shell"}
FX_VALUES = {
    "fill": {},
    "grad": {"scale": 1.0, "speed": 0.0, "ofs": 0.0, "warp": 0.0,
             "wscale": 1.0, "wspeed": 0.0,
... [cut] ...
name]
        bad = set(params) - set(cls.params)
        if bad:
            raise TreatmentError("%s: %s has no parameter %s" % (what, name, sorted(bad)))
        tofs = 0.0
        if L.get("fit"):
            if name != "text":
                raise TreatmentError("%s: fit is for text" % what)
            # Enter on the right at the start, leave on the left at the
            # end, whatever the length of the word and of the moment.
            text = params.get("text", cls.params["text"])
            w = int(E._text_bitmap(text).shape[1])
            cell = float(params.get("cell", CELL))
```

```
$ cd "~/deadmau5 app"; sed -n 905,1140p mau5scene.py; sed -n 1165,1344p mau5scene.py
    def __init__(self, spec, helmet):
        self.spec = spec
        g = spec["grid"]
        self.t0, self.spb = float(g["t0"]), float(g["spb"])
        self.lead = float(g.get("lead", 0.0))
        self.holds = [(float(at), float(beats)) for at, beats in g.get("holds", ())]
        self.nbars = float(spec["bars"])
        self.HB = PULSE_HOLD_S / self.spb
        self.h = h = _h32(helmet)
        self.n = h.n
        self.pal = {k: (np.array(p["stops"], float), bool(p["wrap"]), len(p["stops"]))
                    for k, p in spec["pal"].items()}
        al = np.maximum(h.along, 0.0)
        self.axes = {"x": h.nfa, "y": h.nel, "r": h.er, "a": h.ea, "al": al, "u": h.u}
        self.al = al
        self.scenes = [self._scene(s) for s in spec["scenes"]]
        self.hits = [{"name": x["name"], "at": float(x["at"]), "beats": float(x["beats"]),
                      "layers": [self._layer(L) for L in x["layers"]]}
                     for x in spec["hits"]]
        self.acc = np.zeros((self.n, 3))

    def _scene(self, s):
        p = s.get("pump")
        return {"name": s["name"], "from": float(s["from"]), "to": float(s["to"]),
                "out": float(s["out"]),
                "pump": (p["pat"], float(p["step"]), float(p["decay"]), float(p["depth"]))
                if p else None,
                "layers": [self._layer(L) for L in s["layers"]]}

    def _layer(self, L):
        h = self.h
        fx = L["fx"]
        m = _region_mask(h, L["on"])
        idx = np.where(m)[0]
        g = L.get("gate")
        P = {"fx": fx, "mix": MIX.index(L["mix"]), "idx": idx,
             "pal": self.pal[L["pal"]],
             "gain": _Val(L["gain"]), "c": _Val(L["c"]),
             "gate": (g["pat"], float(g["step"]), float(g["decay"]), float(g["floor"]))
             if g 
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
$ cd "~/deadmau5 app"; sed -n 420,520p mau5scene.py; grep -n "def pal_lookup" -A16 mau5scene.py; grep -n "def _pal_vec" -A14 mau5scene.py; grep -n "def _gate" -A16 mau5scene.py; grep -n "def _region_mask" -A40 mau5scene.py; grep -n "class Sprite" -A70 mau5engine.py | head -120
            cell = float(params.get("cell", CELL))
            edge = _edge_mm(self.h) - CELL + cell
            span_s = float(span) * self.grid["spb"]
            speed = (w * cell + 2.0 * edge) / span_s
            params["speed"] = round(speed, 6)
            params["loop"] = False
            tofs = round(-edge / params["speed"], 6)
        out["name"] = name
        out["params"] = params
        out["tofs"] = tofs
        out.pop("fit", None)
        return out

    # -- scenes and hits -------------------------------------------------
    def compile(self):
        tr, nb = self.tr, self.bars
        for k, v in self.marks.items():
            if not 0 <= v <= nb:
                raise TreatmentError("mark %s at bar %g is outside the song (0..%d)"
                                     % (k, v, nb))
        first_pal = next(iter(self.pal))
        authored, scenes = {}, []
        for i, s in enumerate(tr.get("scenes") or []):
            name = s.get("name") or "scene %d" % i
            what = "scene %s" % name
            if "like" in s:
                if s["like"] not in authored:
                    raise TreatmentError("%s: like %r, which is not an earlier "
                                         "scene" % (what, s["like"]))
                base = authored[s["like"]]
                layers = copy.deepcopy(base["layers"])
                pump = copy.deepcopy(base.get("pump"))
                pal = base.get("pal")
            else:
                layers, pump, pal = [], None, None
            if "layers" in s:
                layers = copy.deepcopy(s["layers"])
            for k, v in (s.get("patch") or {}).items():
                j = int(k)
                if not 0 <= j < len(layers):
                    raise TreatmentError("%s: patch %d has no layer" %
... [cut] ...
 cx = side * self.p["spread"] + look
763-            d = np.hypot(h.px - cx, (h.py - self.p["y"]) * 1.25)
764-            e = np.clip((self.p["size"] - d) / self.EDGE, 0, 1)
765-            k = np.clip(1 - d / self.p["size"], 0, 1) ** 0.6 * e * e * (3 - 2 * e)
766-            if blink:
767-                k *= np.clip(1 - np.abs(h.py - self.p["y"]) / 10.0, 0, 1)
768-            out += k[:, None] * np.array(self.p["color"])
769-        out[~h.shell] = 0
770-        return np.clip(out, 0, 255)
771-
772-
773-class Matrix(Preset):
774-    """Rain down every shell strip, and down all six ear tubes.
```

```
$ cd "~/deadmau5 app"; cat > tools/showkit/songs/weapon/geom.py <<'EOF'
import sys,os; sys.path.insert(0,os.getcwd())
import numpy as np, mau5engine as E, mau5scene as S
h=E.Helmet()
print("n",h.n,"shell",h.shell.sum(),"ears",h.ears.sum())
s=h.shell
print("px",h.px[s].min(),h.px[s].max(),"py",h.py[s].min(),h.py[s].max())
print("nfa",h.nfa[s].min(),h.nfa[s].max(),"nel",h.nel[s].min(),h.nel[s].max())
print("er",h.er[s].min(),h.er[s].max(),"ea",h.ea[s].min(),h.ea[s].max())
# Histogram of LEDs by row in 16 mm rows
for y0 in range(176,-120,-16):
    m=s&(h.py>=y0-8)&(h.py<y0+8)
    if m.any():
         ... [cut]
n 621 shell 398 ears 223
px -170.94 170.95 py -111.27 167.77
nfa 0.16035751702193546 0.8399804407362015 nel 0.0 1.0
er 0.03929154446196175 1.0 ea 0.004374306928113342 0.9891721577339918
y  176  none
y  160  n  21  x    -74..    73  nel 0.90..1.00  nfa 0.32..0.67  er 0.47..0.58 ea 0.15..0.35
y  144  n  51  x   -102..   102  nel 0.81..0.86  nfa 0.27..0.73  er 0.39..0.62 ea 0.11..0.39
y  128  n  30  x   -115..   115  nel 0.76..0.76  nfa 0.24..0.76  er 0.34..0.64 ea 0.09..0.41
y  112  n  64  x   -138..   138  nel 0.67..0.71  nfa 0.21..0.79  er 0.23..0.68 ea 0.05..0.45
y   96  n  34  x   -147..   147  nel 0.62..0.62  nfa 0.19..0.81  er 0.16..0.71 ea 0.04..0.46
y   80  n  34  x   -155..   155  nel 0.57..0.57  nfa 0.18..0.82  er 0.10..0.73 ea 0.02..0.48
y   64  n  34  x   -162..   162  nel 0.52..0.52  nfa 0.17..0.83  er 0.04..0.76 ea 0.00..0.50
y   48  n  22  x   -167..   167  nel 0.48..0.48  nfa 0.17..0.83  er 0.44..0.78 ea 0.51..0.99
y   32  n  12  x   -170..   170  nel 0.43..0.43  nfa 0.16..0.84  er 0.71..0.81 ea 0.53..0.97
y   16  n   2  x   -171..   171  nel 0.38..0.38  nfa 0.16..0.84  er 0.82..0.83 ea 0.54..0.96
y    0  none
y  -16  n   2  x   -170..   170  nel 0.29..0.29  nfa 0.16..0.84  er 0.87..0.87 ea 0.57..0.93
y  -32  n   6  x   -169..   169  nel 0.24..0.24  nfa 0.16..0.84  er 0.88..0.90 ea 0.58..0.92
y  -48  n   8  x   -164..   164  nel 0.19..0.19  nfa 0.17..0.83  er 0.89..0.93 ea 0.59..0.91
y  -64  n  12  x   -159..   159  nel 0.14..0.14  nfa 0.18..0.82  er 0.87..0.95 ea 0.61..0.89
y  -80  n  16  x   -151..   151  nel 0.10..0.10  nfa 0.19..0.81  er 0.85..0.97 ea 0.62..0.88
y  -96  n  20  x   -142..   142  nel 0.05..0.05  nfa 0.20..0.80  er 0.84..0.98 ea 0.63..0.87
y -112  n  30  x   -132..   132  nel 0.00..0.00  nfa 0.22..0.79  er 0.80..1.00 ea 0.64..0.86
face 30
... [cut] ...
1.................1.1111222.
   32 .321.............................123.
   20 .....................................
    8 .1.................................1.
   -4 .....................................
  -16 .1.................................1.
  -28 .....................................
  -40 .21...............................12.
  -52 ..4...............................4..
  -64 ..231...........................132..
  -76 .....................................
  -88 ...3212.......................2123...
 -100 ....412111.................111214....
 -112 .....42111111111.....11111111124.....
```

```
$ cd "~/deadmau5 app"; sed -n 420,520p mau5scene.py; grep -n "def pal_lookup" -A16 mau5scene.py; grep -n "def _pal_vec" -A14 mau5scene.py; grep -n "def _gate" -A16 mau5scene.py; grep -n "def _region_mask" -A40 mau5scene.py; grep -n "class Sprite" -A70 mau5engine.py | head -120
            cell = float(params.get("cell", CELL))
            edge = _edge_mm(self.h) - CELL + cell
            span_s = float(span) * self.grid["spb"]
            speed = (w * cell + 2.0 * edge) / span_s
            params["speed"] = round(speed, 6)
            params["loop"] = False
            tofs = round(-edge / params["speed"], 6)
        out["name"] = name
        out["params"] = params
        out["tofs"] = tofs
        out.pop("fit", None)
        return out

    # -- scenes and hits -------------------------------------------------
    def compile(self):
        tr, nb = self.tr, self.bars
        for k, v in self.marks.items():
            if not 0 <= v <= nb:
                raise TreatmentError("mark %s at bar %g is outside the song (0..%d)"
                                     % (k, v, nb))
        first_pal = next(iter(self.pal))
        authored, scenes = {}, []
        for i, s in enumerate(tr.get("scenes") or []):
            name = s.get("name") or "scene %d" % i
            what = "scene %s" % name
            if "like" in s:
                if s["like"] not in authored:
                    raise TreatmentError("%s: like %r, which is not an earlier "
                                         "scene" % (what, s["like"]))
                base = authored[s["like"]]
                layers = copy.deepcopy(base["layers"])
                pump = copy.deepcopy(base.get("pump"))
                pal = base.get("pal")
            else:
                layers, pump, pal = [], None, None
            if "layers" in s:
                layers = copy.deepcopy(s["layers"])
            for k, v in (s.get("patch") or {}).items():
                j = int(k)
                if not 0 <= j < len(layers):
                    raise TreatmentError("%s: patch %d has no layer" %
... [cut] ...
 cx = side * self.p["spread"] + look
763-            d = np.hypot(h.px - cx, (h.py - self.p["y"]) * 1.25)
764-            e = np.clip((self.p["size"] - d) / self.EDGE, 0, 1)
765-            k = np.clip(1 - d / self.p["size"], 0, 1) ** 0.6 * e * e * (3 - 2 * e)
766-            if blink:
767-                k *= np.clip(1 - np.abs(h.py - self.p["y"]) / 10.0, 0, 1)
768-            out += k[:, None] * np.array(self.p["color"])
769-        out[~h.shell] = 0
770-        return np.clip(out, 0, 255)
771-
772-
773-class Matrix(Preset):
774-    """Rain down every shell strip, and down all six ear tubes.
```

```
$ cd "~/deadmau5 app"; cat > tools/showkit/songs/weapon/geom.py <<'EOF'
import sys,os; sys.path.insert(0,os.getcwd())
import numpy as np, mau5engine as E, mau5scene as S
h=E.Helmet()
print("n",h.n,"shell",h.shell.sum(),"ears",h.ears.sum())
s=h.shell
print("px",h.px[s].min(),h.px[s].max(),"py",h.py[s].min(),h.py[s].max())
print("nfa",h.nfa[s].min(),h.nfa[s].max(),"nel",h.nel[s].min(),h.nel[s].max())
print("er",h.er[s].min(),h.er[s].max(),"ea",h.ea[s].min(),h.ea[s].max())
# Histogram of LEDs by row in 16 mm rows
for y0 in range(176,-120,-16):
    m=s&(h.py>=y0-8)&(h.py<y0+8)
    if m.any():
         ... [cut]
n 621 shell 398 ears 223
px -170.94 170.95 py -111.27 167.77
nfa 0.16035751702193546 0.8399804407362015 nel 0.0 1.0
er 0.03929154446196175 1.0 ea 0.004374306928113342 0.9891721577339918
y  176  none
y  160  n  21  x    -74..    73  nel 0.90..1.00  nfa 0.32..0.67  er 0.47..0.58 ea 0.15..0.35
y  144  n  51  x   -102..   102  nel 0.81..0.86  nfa 0.27..0.73  er 0.39..0.62 ea 0.11..0.39
y  128  n  30  x   -115..   115  nel 0.76..0.76  nfa 0.24..0.76  er 0.34..0.64 ea 0.09..0.41
y  112  n  64  x   -138..   138  nel 0.67..0.71  nfa 0.21..0.79  er 0.23..0.68 ea 0.05..0.45
y   96  n  34  x   -147..   147  nel 0.62..0.62  nfa 0.19..0.81  er 0.16..0.71 ea 0.04..0.46
y   80  n  34  x   -155..   155  nel 0.57..0.57  nfa 0.18..0.82  er 0.10..0.73 ea 0.02..0.48
y   64  n  34  x   -162..   162  nel 0.52..0.52  nfa 0.17..0.83  er 0.04..0.76 ea 0.00..0.50
y   48  n  22  x   -167..   167  nel 0.48..0.48  nfa 0.17..0.83  er 0.44..0.78 ea 0.51..0.99
y   32  n  12  x   -170..   170  nel 0.43..0.43  nfa 0.16..0.84  er 0.71..0.81 ea 0.53..0.97
y   16  n   2  x   -171..   171  nel 0.38..0.38  nfa 0.16..0.84  er 0.82..0.83 ea 0.54..0.96
y    0  none
y  -16  n   2  x   -170..   170  nel 0.29..0.29  nfa 0.16..0.84  er 0.87..0.87 ea 0.57..0.93
y  -32  n   6  x   -169..   169  nel 0.24..0.24  nfa 0.16..0.84  er 0.88..0.90 ea 0.58..0.92
y  -48  n   8  x   -164..   164  nel 0.19..0.19  nfa 0.17..0.83  er 0.89..0.93 ea 0.59..0.91
y  -64  n  12  x   -159..   159  nel 0.14..0.14  nfa 0.18..0.82  er 0.87..0.95 ea 0.61..0.89
y  -80  n  16  x   -151..   151  nel 0.10..0.10  nfa 0.19..0.81  er 0.85..0.97 ea 0.62..0.88
y  -96  n  20  x   -142..   142  nel 0.05..0.05  nfa 0.20..0.80  er 0.84..0.98 ea 0.63..0.87
y -112  n  30  x   -132..   132  nel 0.00..0.00  nfa 0.22..0.79  er 0.80..1.00 ea 0.64..0.86
face 30
... [cut] ...
1.................1.1111222.
   32 .321.............................123.
   20 .....................................
    8 .1.................................1.
   -4 .....................................
  -16 .1.................................1.
  -28 .....................................
  -40 .21...............................12.
  -52 ..4...............................4..
  -64 ..231...........................132..
  -76 .....................................
  -88 ...3212.......................2123...
 -100 ....412111.................111214....
 -112 .....42111111111.....11111111124.....
```

```
$ KIT="tools/showkit"; cd "~/deadmau5 app"; W="$KIT/work/weapon"; B="deadmau5 - Raise Your Weapon"; date; python3 "$KIT/spectro.py" "$B" "$W/d1.png" 126 140; python3 "$KIT/spectro.py" "$B" "$W/d2.png" 156 170; python3 "$KIT/spectro.py" "$B" "$W/d3.png" 236 252; grep -n "def paint" -A28 mau5engine.py | head -60; grep -n "_sprite_bitmap" mau5engine.py | head; grep -n "sprites.json\|\.sprites" mau5engine.py mau5scene.py mau5show.py mau5offline.py remote/offline/*.js | head -20; grep -n "class TextScroll" -A40 mau5engine.py | head -70; sed -n 635,700p mau5scene.py
Sat Oct 31 12:49:30 PDT 2026
tools/showkit/songs/weapon/d1.png
tools/showkit/songs/weapon/d2.png
tools/showkit/songs/weapon/d3.png
629:def paint(bm, rowf, colf, mask, wrap=None, reach=1.4, row_w=1.0):
630-    """Draw a bitmap onto the LEDs, by gather and by scatter.
631-
632-    The gather is the obvious half: every LED looks up the cell it
633-    falls in.  On its own it loses strokes, because the LEDs are not a
634-    grid -- a quarter of the cells of a 7-row glyph on this dome
635-    contain no LED at all, so a quarter of every letter silently does
636-    not appear.  Held still, DEADMAU5 is unreadable and a 2 loses its
637-    bottom bar; this is why the digits came out wrong.
638-
639-    The scatter is the other half: every *set* cell that caught no LED
640-    of its own claims the nearest one instead.  Areas still fill from
641-    the gather, and a one-cell-wide stem can no longer vanish into a
642-    gap in the map.  A cell reaches at most `reach` cells, so a stroke
643-    in a genuinely empty corner stays missing rather than dragging in
644-    an LED from somewhere unrelated.
645-    """
646-    rows, cols = bm.shape
647-    r = np.floor(rowf).astype(int)
648-    c = np.floor(colf).astype(int)
649-    cw = (c % cols) if wrap else c
650-    ok = mask & (rowf >= 0) & (rowf < rows)
651-    if not wrap:
652-        ok &= (colf >= 0) & (colf < cols)
653-    lit = np.zeros(mask.shape, bool)
654-    idx = np.where(ok)[0]
655-    if not len(idx):
656-        return lit
657-    lit[idx] = bm[r[idx], cw[id
... [cut] ...
 above zero" % what)
            if max(rates or [0]) * max(lifes) > 8:
                warns.append("%s: life x rate = %.1f, above the 8 sparks drawn"
                             % (what, max(rates) * max(lifes)))
        if L["fx"] == "twinkle":
            if "n" not in L["rate"] and "keys" not in L["rate"]:
                errs.append("%s: a twinkle rate is a number or keys, so the LEDs "
                            "never jump" % what)
            if "n" in L["sharp"] and L["sharp"]["n"] <= 0:
                errs.append("%s: sharp must be above zero" % what)
        if L["fx"] == "orb":
```

```
$ cd "~/deadmau5 app"; grep -rn "sprites" --include=*.py . 2>/dev/null | grep -v "^./tests\|superseded" | head -20; grep -n "sprites" remote/offline/*.js mau5offline.py | head; sed -n 620,629p mau5engine.py; ls shows/scenes/ | head -50; sed -n 700,790p mau5scene.py
(eval):1: no matches found: --include=*.py
remote/offline/engine.js:169:  const rows = fonts.sprites[name];
mau5offline.py:96:            "sprites": {k: list(v) for k, v in SPRITES.items()},
    g = FONT5x7.get(ch.upper(), FONT5x7.get("?", (0, 0, 0, 0, 0)))
    return np.array([[(c >> r) & 1 for c in g] for r in range(7)], bool)


def _sprite_bitmap(name):
    rows = SPRITES[name]
    return np.array([[c != "." for c in r] for r in rows], bool)


def paint(bm, rowf, colf, mask, wrap=None, reach=1.4, row_w=1.0):
Fred again.. & Baby Keem - leavemealone.scene.json
Kaskade feat. deadmau5 - I Remember.beats
Kaskade feat. deadmau5 - I Remember.sprites.json
TIKI TIKI - Slowed.beats
TIKI TIKI - Slowed.scene.json
beneath (with raxaj).beats
beneath (with raxaj).scene.json
deadmau5 & Wolfgang Gartner - Animal Rights.beats
deadmau5 & Wolfgang Gartner - Animal Rights.sprites.json
deadmau5 - FN Pig.beats
deadmau5 - Ghosts n Stuff (Nero Remix).beats
deadmau5 - Ghosts n Stuff (Nero Remix).scene.json
deadmau5 - Harder Better Faster Stronger.beats
deadmau5 - Moar Ghosts n Stuff.beats
deadmau5 - Moar Ghosts n Stuff.sprites.json
deadmau5 - Raise Your Weapon.beats
deadmau5 - Some Chords (Radio Edit).beats
deadmau5 - Some Chords.beats
deadmau5 - Strobe (Dimension Remix).scene.json
deadmau5 - Strobe (Special Features Remix).beats
deadmau5 - Strobe (Special Features Remix).sprites.json
deadmau5 - Strobe.scene.json
deadmau5 - The Veldt.beats
playlist.json
        if L["fx"] == "orb":
            for k in ("xf", "yf"):
                if "n" not in L[k] and "keys" not in L[k]:
                    errs.append("%s: %s is a number or keys, so the orb never "
                                "jumps" % (what, k))
            for k in ("rad", "soft"):
                ends = (L[k].get("ramp") or [L[k].g
... [cut] ...
sum(texts(y["layers"]) for y in over if y is not x)
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
```

```
$ cd "~/deadmau5 app"; grep -rn "sprites" --include=*.py . 2>/dev/null | grep -v "^./tests\|superseded" | head -20; grep -n "sprites" remote/offline/*.js mau5offline.py | head; sed -n 620,629p mau5engine.py; ls shows/scenes/ | head -50; sed -n 700,790p mau5scene.py
(eval):1: no matches found: --include=*.py
remote/offline/engine.js:169:  const rows = fonts.sprites[name];
mau5offline.py:96:            "sprites": {k: list(v) for k, v in SPRITES.items()},
    g = FONT5x7.get(ch.upper(), FONT5x7.get("?", (0, 0, 0, 0, 0)))
    return np.array([[(c >> r) & 1 for c in g] for r in range(7)], bool)


def _sprite_bitmap(name):
    rows = SPRITES[name]
    return np.array([[c != "." for c in r] for r in rows], bool)


def paint(bm, rowf, colf, mask, wrap=None, reach=1.4, row_w=1.0):
Fred again.. & Baby Keem - leavemealone.scene.json
Kaskade feat. deadmau5 - I Remember.beats
Kaskade feat. deadmau5 - I Remember.sprites.json
TIKI TIKI - Slowed.beats
TIKI TIKI - Slowed.scene.json
beneath (with raxaj).beats
beneath (with raxaj).scene.json
deadmau5 & Wolfgang Gartner - Animal Rights.beats
deadmau5 & Wolfgang Gartner - Animal Rights.sprites.json
deadmau5 - FN Pig.beats
deadmau5 - Ghosts n Stuff (Nero Remix).beats
deadmau5 - Ghosts n Stuff (Nero Remix).scene.json
deadmau5 - Harder Better Faster Stronger.beats
deadmau5 - Moar Ghosts n Stuff.beats
deadmau5 - Moar Ghosts n Stuff.sprites.json
deadmau5 - Raise Your Weapon.beats
deadmau5 - Some Chords (Radio Edit).beats
deadmau5 - Some Chords.beats
deadmau5 - Strobe (Dimension Remix).scene.json
deadmau5 - Strobe (Special Features Remix).beats
deadmau5 - Strobe (Special Features Remix).sprites.json
deadmau5 - Strobe.scene.json
deadmau5 - The Veldt.beats
playlist.json
        if L["fx"] == "orb":
            for k in ("xf", "yf"):
                if "n" not in L[k] and "keys" not in L[k]:
                    errs.append("%s: %s is a number or keys, so the orb never "
                                "jumps" % (what, k))
            for k in ("rad", "soft"):
                ends = (L[k].get("ramp") or [L[k].g
... [cut] ...
sum(texts(y["layers"]) for y in over if y is not x)
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
```

```
$ cd "~/deadmau5 app"; grep -n "sprites.json\|SPRITES\b" mau5fx.py | head -12; grep -n "sprites.json" mau5show.py mau5scene.py mau5engine.py mau5offline.py | head; cat "shows/scenes/Kaskade feat. deadmau5 - I Remember.sprites.json" | cut -c1-200 | head -8
134:SPRITES = {
249:# Sprites a song brings with it: shows/scenes/<song>.sprites.json, {name: [rows]},
256:        sheets = sorted(f for f in os.listdir(d) if f.endswith(".sprites.json"))
266:                SPRITES[name] = list(rows)
275:    rows = SPRITES[name_or_rows] if isinstance(name_or_rows, str) else name_or_rows
989:    for name in sorted(SPRITES):
{
"remember_heart": [
 ".##...##.",
 "####.####",
 "#########",
 "#########",
 ".#######.",
 "..#####..",
```

```
$ KIT="tools/showkit"; cd "~/deadmau5 app"; W="$KIT/work/weapon"; cat > "$W/sprites.py" <<'EOF'
import json
S={}
S["weapon_swords"]=[
"##...................##",
"####...............####",
".#####...........#####.",
"...#####.......#####...",
".....#####...#####.....",
".......#########.......",
".........#####.........",
".......#########.......",
"..##.#####...#####.##..",
"..#####.........#####..",
"..#####.........#####..",
".##...............##...",
]
S["weapon_swords"][-1]=".##.................##."
S["weapon_flame1"]=[
"....#....",
"....#....",
"...##....",
"...###...",
"..####...",
"..##### ... [cut]
tools/showkit/songs/weapon/sp1.png (360, 338)
tools/showkit/songs/weapon/sp2.png (720, 338)
tools/showkit/songs/weapon/sp3.png (360, 338)
tools/showkit/songs/weapon/sp4.png (360, 338)
```

```
$ KIT="tools/showkit"; W="$KIT/work/weapon"; python3 - "$W" <<'EOF'
import sys
from PIL import Image
W=sys.argv[1]
ims=[Image.open(f"{W}/sp{i}.png") for i in (1,2,3,4)]
o=Image.new("RGB",(sum(i.width for i in ims),338))
x=0
for i in ims:
    o.paste(i,(x,0)); x+=i.width
o.save(f"{W}/sp_all.png"); print(o.size)
EOF
(1800, 338)
```

```
$ KIT="tools/showkit"; cd "~/deadmau5 app"; W="$KIT/work/weapon"; cat > "$W/trysprites.py" <<'EOF'
import sys,os,json
sys.path.insert(0,os.getcwd())
import numpy as np, mau5engine as E, mau5preview as PV, mau5fx
from PIL import Image, ImageDraw
V={}
V["x11"]=(["#.........#",
"##.......##",
".##.....##.",
"..##...##..",
"...##.##...",
"....###....",
"...##.##...",
".####.####.",
"##.#...#.##"],dict(y_lo=48,y_hi=170,x_half=95))
V["x15"]=(["##...........##",
"###.........###",
".###.......###.",
"..###.....###..",
"...###...###...",
".....#####.....",
"......###......",
".....#####.....",
"..#####.# ... [cut]
(1200, 500)
```

```
$ KIT="tools/showkit"; cd "~/deadmau5 app"; W="$KIT/work/weapon"; date; cat > "$W/sprites.py" <<'EOF'
import json
S={}
S["weapon_swords"]=[
"##...........##",
"###.........###",
".###.......###.",
"..###.....###..",
"...###...###...",
".....#####.....",
"......###......",
".....#####.....",
"..#####.#####..",
".####.....####.",
"###.........###"]
S["weapon_line"]=["#"*40]
# the blade held upright, for the end of the song's long notes
S["weapon_sword"]=[
"...#...",
"...#...",
"..###..",
"..###..",
"..###..",
"..###..",
"..###..",
"#######",
"#######"]
for k,v in S.items():
    assert len({len(r) f ... [cut]
Sat Oct 31 12:54:12 PDT 2026
wrote shows/scenes/deadmau5 - Raise Your Weapon.scene.json scenes 25 hits 39
     246   441.00s  energy 0.13  bass 0.27 (punch 1.00)  mid 0.38  high 0.46
     247   442.71s  energy 0.13  bass 0.33 (punch 0.99)  mid 0.30  high 0.41
  sheathe    bar 250
     249   446.14s  energy 0.23  bass 0.35 (punch 1.00)  mid 0.26  high 0.32
     250   447.85s  energy 0.22  bass 0.35 (punch 1.00)  mid 0.18  high 0.26
     251   449.57s  energy 0.21  bass 0.31 (punch 0.97)  mid 0.21  high 0.19
  gutter     bar 268
     267   477.00s  energy 0.34  bass 0.40 (punch 0.78)  mid 0.31  high 0.01
     268   478.71s  energy 0.27  bass 0.36 (punch 0.61)  mid 0.27  high 0.01
     269   480.42s  energy 0.14  bass 0.03 (punch 0.38)  mid 0.14  high 0.00
  end        bar 276
     275   490.71s  energy 0.00  bass 0.05 (punch 0.81)  mid 0.00  high 0.00
     276   492.42s  energy 0.00  bass 0.00 (punch 0.44)  mid 0.00  high 0.00
     277   494.14s  energy 0.00  bass 0.00 (punch 0.43)  mid 0.00  high 0.00
deadmau5 - Raise Your Weapon: 27 scenes, 39 hits, written into shows/deadmau5 - Raise Your Weapon.json
```

```
$ KIT="tools/showkit"; cd "~/deadmau5 app"; W="$KIT/work/weapon"; B="deadmau5 - Raise Your Weapon"; time python3 "$KIT/sheet.py" "$B" "$W/s1.png" 6:candle 18:sing1 19.5:sing1b 26:sing3 42:moon 47:slide 48:kick 48.25:gap 56:march 66:sung 70.5:sung2 88:full 98:draw1 104:draw2 111:draw3 114:edge 120:edge2 124:title 126:title2 128.5:quiet 129.5:pick 129.875:pick3 130:DROP 130.05:drop+ 2>&1 | tail -30
bar 6       candle         shell max 170 mean   2.9   ears max  26 mean   1.2   candle
bar 18      sing1          shell max 255 mean   8.7   ears max  78 mean  10.8   moonrise · sing 16
bar 19.5    sing1b         shell max 255 mean  11.3   ears max  84 mean   5.3   moonrise · sing 16
bar 26      sing3          shell max 255 mean   9.1   ears max  84 mean  10.5   moonrise · sing 24
bar 42      moon           shell max 255 mean  14.4   ears max 106 mean  15.3   moonlit · sing 40
bar 47      slide          shell max 255 mean  18.1   ears max 104 mean  20.7   moonlit · sing 46
bar 48      kick           shell max   0 mean   0.0   ears max   7 mean   0.2   moonlit · sing 46
bar 48.25   gap            shell max 179 mean   8.7   ears max   0 mean   0.0   march
bar 56      march          shell max 175 mean   8.6   ears max   0 mean   0.0   march
bar 66      sung           shell max 125 mean  14.6   ears max 131 mean  28.8   sung march · sing 64
bar 70.5    sung2          shell max 123 mean  14.1   ears max 131 mean  28.0   sung march · sing 68
bar 88      full           shell max 134 mean  15.1   ears max 154 mean  23.6   full march · sing 88
bar 98      draw1          shell max 140 mean   6.1   ears max  79 mean  12.4   the draw
bar 104     draw2          shell max 184 mean   9.8   ears max 101 mean  33.6   the draw
bar 111     draw3          shell max 233 mean  18.2   ears max 127 mean  82.1   the draw
bar 114     edge           shell max 204 mean  13.6   ears max  74 mean  20.7   on edge · sing 112
bar 120     edge2          shell max 193 mean  12.5   ears max 107 mean  15.9   on edge · sing 120
bar 124     title          shell max 249 mean  51.0   ears max  46 mean   2.4   title · RAISE YOUR WEAPON
bar 126     title2         shell max 249 mean  45.0   ears max  47 mean   2.
... [cut] ...
 · RAISE YOUR WEAPON
bar 129.875 pick3          shell max 255 mean  21.4   ears max   0 mean   0.0   quiet
bar 130     DROP           shell max   0 mean   0.0   ears max   0 mean   0.0   quiet
bar 130.05  drop+          shell max 255 mean 120.2   ears max 243 mean 125.7   first blood · DROP
tools/showkit/songs/weapon/s1.png (1800, 980)
python3 "$KIT/sheet.py" "$B" "$W/s1.png" 6:candle 18:sing1 19.5:sing1b         0.36s user 0.03s system 96% cpu 0.403 total
tail -30  0.00s user 0.00s system 0% cpu 0.403 total
```

```
$ KIT="tools/showkit"; cd "~/deadmau5 app"; W="$KIT/work/weapon"; B="deadmau5 - Raise Your Weapon"; python3 "$KIT/sheet.py" "$B" "$W/s2.png" 130.1:drop 130.25:k 130.5:snare 130.53:s+ 130.56:s++ 130.59 130.62 130.7 130.9 131.0:kick 131.5:snareR 131.53 131.56 131.6 138.1:crossed 138.5 139 139.53 146.1:p2 146.53 146.56 146.6 147.53 147.56 147.6 150 161.2:stop 161.8:riser 162.1 163 2>&1 | tail -32
bar 130.1   drop           shell max 255 mean 118.0   ears max 138 mean 105.1   first blood · DROP
bar 130.25  k              shell max 255 mean 120.6   ears max 162 mean  72.2   first blood · DROP
bar 130.5   snare          shell max  66 mean  12.7   ears max  16 mean   1.4   first blood · DROP
bar 130.53  s+             shell max 255 mean  62.4   ears max 153 mean  38.2   first blood
bar 130.56  s++            shell max 255 mean  41.5   ears max 121 mean  48.3   first blood
bar 130.59                 shell max 255 mean  51.4   ears max  80 mean  32.5   first blood
bar 130.62                 shell max 106 mean  23.6   ears max  54 mean  20.9   first blood
bar 130.7                  shell max  80 mean  17.8   ears max  20 mean   4.7   first blood
bar 130.9                  shell max  66 mean  12.8   ears max  12 mean   1.0   first blood
bar 131     kick           shell max  66 mean  12.6   ears max  12 mean   1.0   first blood
bar 131.5   snareR         shell max  66 mean  12.0   ears max  16 mean   1.4   first blood
bar 131.53                 shell max 255 mean  61.0   ears max 153 mean  38.2   first blood
bar 131.56                 shell max 243 mean  40.9   ears max 121 mean  48.3   first blood
bar 131.6                  shell max 255 mean  59.8   ears max  70 mean  28.2   first blood
bar 138.1   crossed        shell max  76 mean  18.2   ears max  36 mean   3.1   crossed
bar 138.5                  shell max  48 mean  14.3   ears max  16 mean   1.4   crossed
bar 139                    shell max  48 mean  14.2   ears max  12 mean   1.0   crossed
bar 139.53                 shell max 255 mean  54.1   ears max 153 mean  38.2   crossed
bar 146.1   p2             shell max 197 mean  23.9   ears max 117 mean  68.0   arcs · P2
bar 146.53                 shell max 255 mean  39
... [cut] ...
  70 mean  28.2   arcs
bar 150                    shell max  66 mean   8.9   ears max  12 mean   1.0   arcs
bar 161.2   stop           shell max 126 mean  10.5   ears max  19 mean   2.4   stopped
bar 161.8   riser          shell max 126 mean  10.5   ears max  19 mean   2.4   stopped
bar 162.1                  shell max 255 mean  18.2   ears max 117 mean  68.0   sung war · P3
bar 163                    shell max 133 mean   9.2   ears max  12 mean   1.0   sung war
tools/showkit/songs/weapon/s2.png (1800, 1225)
```

```
$ KIT="tools/showkit"; cd "~/deadmau5 app"; W="$KIT/work/weapon"; B="deadmau5 - Raise Your Weapon"; date; python3 "$KIT/sheet.py" "$B" "$W/s3.png" 166:sung 167 170.53 178.1 182 190.5:raised 192 194.1:p5 194.53 198 210.1:p6 214.53 221:raised2 226.1:p7 230.53 238 241.5 242.05:crash 243 245 247:relit 252:sheathe 260 266 270:gutter 274 2>&1 | tail -30; python3 mau5scene.py check "$B" 2>&1 | tail -40
Sat Oct 31 12:55:12 PDT 2026
bar 166     sung           shell max 128 mean  11.4   ears max  76 mean  11.6   sung war · sing 164
bar 167                    shell max 255 mean  15.4   ears max  74 mean  11.5   sung war · sing 164
bar 170.53                 shell max 255 mean  35.6   ears max 158 mean  49.7   sung war · sing 168
bar 178.1                  shell max 223 mean  26.5   ears max 157 mean  78.7   sung war 2 · sing 176 · P4
bar 182                    shell max 111 mean  13.0   ears max  76 mean  11.6   sung war 2 · sing 180
bar 190.5   raised         shell max 218 mean  13.0   ears max  75 mean  12.8   raised · sing 188
bar 192                    shell max 255 mean  14.4   ears max  12 mean   1.3   raised · sing 188
bar 194.1   p5             shell max 201 mean  22.2   ears max 117 mean  68.0   white steel · P5
bar 194.53                 shell max 255 mean  37.4   ears max 153 mean  38.2   white steel
bar 198                    shell max  51 mean  18.9   ears max  12 mean   1.0   white steel
bar 210.1   p6             shell max 211 mean  27.6   ears max 117 mean  68.0   clash · P6
bar 214.53                 shell max 255 mean  54.7   ears max 153 mean  38.2   clash
bar 221     raised2        shell max  96 mean   9.4   ears max  12 mean   1.0   raised 2
bar 226.1   p7             shell max 229 mean  33.1   ears max 123 mean  68.5   last stand · P7
bar 230.53                 shell max 255 mean  60.0   ears max 178 mean  44.6   last stand
bar 238                    shell max  76 mean  16.7   ears max  14 mean   1.2   last stand
bar 241.5                  shell max  76 mean  19.2   ears max  18 mean   1.6   last stand
bar 242.05  crash          shell max 255 mean  44.8   ears max 231 mean 109.1   fall · CRASH
bar 243                    shell max 153 mean  25.4   ear
... [cut] ...
el    351.9s      359      748    18.4%      18.1    0.17
  clash          379.3s      366      750    18.9%      18.1    0.23
  raised 2       396.4s      280      673    18.9%      18.1    0.22
  last stand     406.7s      351      700    19.4%      18.1    0.24
  fall           434.2s      406     1000    19.9%      18.1    0.13
  relit          441.0s      190      236    19.7%      18.1    0.20
  sheathed       447.9s      268      328    19.5%      18.1    0.22
  gutter         478.7s       65      140    19.1%      18.1    0.15
  worst frame 0.52 ms; no scene reaches the sustained floor
```

```
$ KIT="tools/showkit"; cd "~/deadmau5 app"; W="$KIT/work/weapon"; cat > "$W/trysprites.py" <<'EOF'
import sys,os,json
sys.path.insert(0,os.getcwd())
import numpy as np, mau5engine as E, mau5preview as PV, mau5fx
from PIL import Image, ImageDraw
V={}
# three hanging swallow-tail banners, x_half 170
V["ban1"]=(["..................",
"####..#####..####.",
"####..#####..####.",
"####..#####..####.",
".###..#####..###..",
".###..#####..###..",
".###..##.##..###..",
".#.#..#...#..#.#..",
".#.#.........#.#.."],dict(y_lo=48,y_hi=172,x_half=150))
V["ban_a"]=(["#####.#######.#####",
"#####.#######.#####",
 ... [cut]
(1200, 500)
```

```
$ KIT="tools/showkit"; cd "~/deadmau5 app"; W="$KIT/work/weapon"; B="deadmau5 - Raise Your Weapon"; date; python3 "$KIT/spectro.py" "$B" "$W/e1.png" 186 198; python3 "$KIT/spectro.py" "$B" "$W/e2.png" 216 228; python3 - <<'EOF'
import sys,os
sys.path.insert(0,os.getcwd())
import numpy as np, mau5engine as E
h=E.Helmet()
for nm,m in (("ear1",h.ear1),("ear2",h.ear2)):
    print(nm,"er",h.er[m].min(),h.er[m].max(),"ea",h.ea[m].min(),h.ea[m].max(),"al",h.along[m].min(),h.along[m].max())
    t=np.asarray(h.tube)[m]; print(" tube counts",[(k,(t==k).sum()) for k in (-1,0,1,2)])
    r=np.asarray(h.rims)[ ... [cut]
Sat Oct 31 12:58:17 PDT 2026
tools/showkit/songs/weapon/e1.png
tools/showkit/songs/weapon/e2.png
ear1 er 0.027196683415757796 1.0 ea 0.009314194339928106 0.9998557991530969 al 0.0247 0.9904
 tube counts [(-1, np.int64(18)), (0, np.int64(30)), (1, np.int64(36)), (2, np.int64(28))]
 rim er 0.9383901427964612 1.0
 tube 0 er 0.50..0.86 px -349..-201 py 67..216
 tube 1 er 0.03..0.71 px -310..-130 py 128..303
 tube 2 er 0.49..0.78 px -237..-87 py 215..349
ear2 er 0.0372739830672619 1.0 ea 0.019912212211214027 0.9984734368258824 al 0.0327 0.9699
 tube counts [(-1, np.int64(19)), (0, np.int64(28)), (1, np.int64(36)), (2, np.int64(28))]
 rim er 0.9142384187923356 1.0
 tube 0 er 0.50..0.83 px 207..358 py 70..214
 tube 1 er 0.04..0.75 px 133..322 py 127..306
 tube 2 er 0.50..0.81 px 83..237 py 205..349
```

```
$ KIT="tools/showkit"; cd "~/deadmau5 app"; W="$KIT/work/weapon"; date; cat > "$W/sprites.py" <<'EOF'
import json
S={}
S["weapon_swords"]=[
"##...........##",
"###.........###",
".###.......###.",
"..###.....###..",
"...###...###...",
".....#####.....",
"......###......",
".....#####.....",
"..#####.#####..",
".####.....####.",
"###.........###"]
S["weapon_line"]=["#"*40]
# the blade held upright: guard on the lowest full strip of the dome
S["weapon_sword"]=[
"...#...",
"...#...",
"...#...",
"...#...",
"...#...",
"...#...",
"...#...",
"...#...",
"#######"]
# three swallow-tailed banners hanging f ... [cut]
Exit code 1
Sat Oct 31 13:00:21 PDT 2026
Traceback (most recent call last):
  File "tools/showkit/songs/weapon/write_treatment.py", line 189, in <module>
    ring("kick","steel",0.75,ears=0.3,gain=0.5)
  File "tools/showkit/songs/weapon/write_treatment.py", line 185, in ring
    H.append({"name":"ring %g"%at,"at":at,"beats":beats,"pal":pal,"layers":[{"fx":"fill","on":"ears","c":c,"gain":[ears,0]},{"fx":"sweep","on":"shell","axis":"r","shape":"p","mode":"band","from":0,"to":1.2,"width":0.25,"c":c,"gain":gain}]})
TypeError: must be real number, not str
```

```
$ KIT="tools/showkit"; cd "~/deadmau5 app"; W="$KIT/work/weapon"; sed -i '' 's/"name":"ring %g"%at,"at":at/"name":"ring %s"%at,"at":at/' "$W/write_treatment.py"; export KIT; python3 "$W/write_treatment.py" && python3 mau5scene.py compile "deadmau5 - Raise Your Weapon" 2>&1 | tail -6
wrote shows/scenes/deadmau5 - Raise Your Weapon.scene.json scenes 30 hits 45
     269   480.42s  energy 0.14  bass 0.03 (punch 0.38)  mid 0.14  high 0.00
  end        bar 276
     275   490.71s  energy 0.00  bass 0.05 (punch 0.81)  mid 0.00  high 0.00
     276   492.42s  energy 0.00  bass 0.00 (punch 0.44)  mid 0.00  high 0.00
     277   494.14s  energy 0.00  bass 0.00 (punch 0.43)  mid 0.00  high 0.00
deadmau5 - Raise Your Weapon: 32 scenes, 45 hits, written into shows/deadmau5 - Raise Your Weapon.json
```

```
$ KIT="tools/showkit"; cd "~/deadmau5 app"; W="$KIT/work/weapon"; B="deadmau5 - Raise Your Weapon"; sed -i '' 's/shields(132,146); shields(146,161,c=0.45)/shields(130,146); shields(146,161,c=0.45)/' "$W/write_treatment.py"; export KIT; python3 "$W/write_treatment.py" && python3 mau5scene.py compile "$B" 2>&1 | tail -1; python3 "$KIT/sheet.py" "$B" "$W/s5.png" 18:moon 30 40 56.02:march 56.1 56.2 132.02 132.3 132.5 132.53 132.56 132.59 132.62 133.53 133.56 133.59 133.62 133.7 140.02 140.3 140.53 140.56 147.53 147.56 147.6 156.1 156.53 156.57 161.2 161.8 161.95 166 170.53 180 189.1:raise 189.5 190 1 ... [cut]
wrote shows/scenes/deadmau5 - Raise Your Weapon.scene.json scenes 30 hits 45
deadmau5 - Raise Your Weapon: 32 scenes, 45 hits, written into shows/deadmau5 - Raise Your Weapon.json
bar 56.02   march          shell max 173 mean   9.6   ears max 142 mean  27.6   march
bar 56.1                   shell max 163 mean   8.4   ears max  56 mean  21.6   march
bar 56.2                   shell max 178 mean   7.1   ears max   0 mean   0.0   march
bar 132.02                 shell max 150 mean  12.8   ears max  81 mean  31.3   first blood · shiel
bar 132.3                  shell max  86 mean  10.6   ears max  53 mean  26.2   first blood · shiel
bar 132.5                  shell max  59 mean   9.3   ears max   8 mean   4.2   first blood · shiel
bar 132.53                 shell max 255 mean  44.0   ears max 155 mean  29.3   first blood · shiel
bar 132.56                 shell max 255 mean  47.5   ears max 126 mean  42.2   first blood · shiel
bar 132.59                 shell max  86 mean  20.4   ears max 198 mean  58.1   first blood · shiel
bar 132.62                 shell max  82 mean  19.1   ears max 147 mean  42.9   first blood · shiel
bar 133.53                 shell max 255 mean  42.1   ears max 155 mean  29.3   first blood · shiel
bar 133.56                 shell max 255 mean  47.3   ears max 126 mean  42.2   first blood · shiel
bar 133.59                 shell max  87 mean  20.9   ears max 198 mean  58.3   first blood · shiel
bar 133.62                 shell max  79 mean  18.1   ears max 147 mean  43.1   first blood · shiel
bar 133.7                  shell max  64 mean  13.1   ears max  33 mean  10.2   first blood · shiel
bar 140.02                 shell max 124 mean  18.6   ears max  81 mean  31.3   banners · shields 1
bar 140.3                  shell max  76 mean  13.2   ears max
... [cut] ...
bar 189.5                  shell max 105 mean   4.3   ears max   6 mean   3.0   raised · shields 17
bar 190                    shell max 147 mean   5.1   ears max   0 mean   0.0   raised · shields 17
bar 190.8                  shell max 214 mean  13.8   ears max   5 mean   1.6   raised · shields 17
bar 191.5                  shell max 200 mean  16.4   ears max   6 mean   3.0   lowered · shields 1
bar 192.53                 shell max 255 mean  31.3   ears max 116 mean  22.0   lowered · shields 1
(scratch)/ki
```

```
$ KIT="tools/showkit"; cd "~/deadmau5 app"; W="$KIT/work/weapon"; B="deadmau5 - Raise Your Weapon"; date; python3 "$KIT/sheet.py" "$B" "$W/s6.png" 194.1 194.5 194.53 194.56 194.59 194.62 195.53 195.56 195.59 195.62 204.1 204.53 204.56 212.03 212.5 212.53 212.56 212.59 212.62 221.5 222.5 223.5 224.55 226.1 228.53 228.56 236.03 236.53 236.57 241.5 241.9 242.02 243 244 245 247 256 262 266 270 2>&1 | tail -3 | cut -c1-100; python3 mau5scene.py check "$B" 2>&1 | tail -38
Sat Oct 31 13:00:53 PDT 2026
bar 266                    shell max 240 mean   8.9   ears max 103 mean   3.6   sheathed
bar 270                    shell max 148 mean   2.2   ears max  56 mean   2.8   gutter
(scratch)/ki
deadmau5 - Raise Your Weapon: 12573 frames at 25 fps through the guard
  scene            from  mean mA   p95 mA     heat   allow W      ms
  dark             0.0s        0        0    24.8%      18.1    0.04
  candle           0.0s       51       63     0.0%      18.1    0.07
  moonrise        30.0s      360      465     0.8%      18.1    0.21
  moonlit         60.0s      468      607     2.9%      18.1    0.22
  march           90.0s      389      701     4.0%      18.1    0.16
  sung march     120.0s      532      896     6.8%      18.1    0.22
  full march     150.0s      571      953    10.1%      18.1    0.22
  the draw       180.0s      609     1000    13.9%      18.1    0.16
  on edge        210.0s      456      685    15.1%      18.1    0.26
  title          228.2s      410      669    15.5%      18.1    0.36
  quiet          238.7s      308      863    15.6%      18.1    0.23
  first blood    242.2s      426      782    16.3%      18.1    0.23
  banners        255.9s      413      756    16.9%      18.1    0.27
  arcs           269.6s      410      756    17.6%      18.1    0.27
  crossed        283.3s      447      750    18.3%      18.1    0.33
  stopped        295.3s      323      621    18.3%      18.1    0.11
  sung war       297.0s      437      750    19.9%      18.1    0.34
  sung war 2     324.4s      489      750    21.3%      18.1    0.38
  raised         343.3s      295      634    21.3%      18.1    0.26
  lowered        346.7s      366      689  
... [cut] ...
      398.2s      355      749    24.5%      18.1    0.26
  lowered 2      401.6s      420      752    24.7%      18.1    0.31
  last stand     406.7s      460      860    25.6%      18.1    0.33
  last stand 2   420.4s      433      864    26.4%      18.1    0.33
  fall           434.2s      415     1000    26.8%      18.1    0.15
  relit          441.0s      155      186    26.7%      18.1    0.18
  sheathed       447.9s      271      355    26.5%      18.1    0.22
  gutter         478.7s       75      163    26.0%      18.1    0.15
  worst frame 0.72 ms; no scene reaches the sustained floor
```

```
$ KIT="tools/showkit"; cd "~/deadmau5 app"; W="$KIT/work/weapon"; cat > "$W/dbg.py" <<'EOF'
import sys,os,json
sys.path.insert(0,os.getcwd())
import numpy as np, mau5show, mau5scene as MS, mau5engine as E
base="deadmau5 - Raise Your Weapon"
show=json.load(open("shows/%s.json"%base))
music=mau5show._music_for(show,"shows/%s.mp3"%base)
g=show["scenes"]["grid"]; spb=g["spb"]; t0=g["t0"]
def tof(bar):
    B=4*bar
    return t0+B*spb+sum(b*spb for at,b in g.get("holds",[]) if B>at)
h=E.Helmet()
sc=MS.Scenes(show["scenes"],h)
for bar in (98.0,98.5,104.0):
    out,gain,label=sc.frame(tof(bar),music)
    ... [cut]
bar 98.0 the draw gain 1.0
   y~  60 n= 34 x -162..162  max [118. 128. 140.]
   y~  80 n=  4 x -21..21  max [3. 1. 0.]
   y~  90 n=  6 x -34..34  max [26. 11.  1.]
   y~ 100 n=  8 x -44..44  max [46. 25.  5.]
   y~ 120 n=  8 x -40..40  max [46. 27.  7.]
   y~ 130 n=  8 x -37..37  max [35. 16.  3.]
   y~ 140 n=  8 x -33..33  max [16.  6.  0.]
   y~ 150 n=  4 x -20..28  max [3. 1. 0.]
   y~ 160 n=  2 x -3..10  max [0. 0. 0.]
   strip: [140, 140, 140, 140, 140, 140, 140, 52, 52, 52, 52, 52, 52, 52, 52, 52, 52, 52, 51, 52, 52, 52, 52, 52, 52, 52, 52, 52, 52, 52, 52, 52, 52, 52]
bar 98.5 the draw gain 1.0
   y~  60 n= 34 x -162..162  max [121. 132. 144.]
   y~  80 n=  4 x -21..21  max [1. 0. 0.]
   y~  90 n=  6 x -34..34  max [21.  8.  1.]
   y~ 100 n=  7 x -32..44  max [43. 23.  5.]
   y~ 120 n=  8 x -40..40  max [45. 28. 10.]
   y~ 130 n=  9 x -37..47  max [37. 19.  3.]
   y~ 140 n=  9 x -33..41  max [19.  7.  1.]
   y~ 150 n=  4 x -20..28  max [4. 1. 0.]
   y~ 160 n=  2 x -3..10  max [0. 0. 0.]
   strip: [144, 144, 144, 144, 143, 144, 143, 144, 52, 52, 52, 52, 52, 52, 52, 52, 52, 52, 52, 52, 52, 52, 52, 52, 52, 52, 52, 52, 52, 52, 52, 52, 52, 52]
bar 104.0 the draw gain 1.0
   y~  50 n= 22 x -167..167  max [1. 2. 2.]
   y~  60 n= 34 x -162..162  max [158. 169. 184.]
   y~  80 n= 34 x -155..155  max [3. 3. 3.]
   y~  90 n=  6 x -34..34  max [15.  7.  1.]
   y~ 100 n=  6 x -32..32  max [29. 17.  5.]
   y~ 120 n=  6 x -29..29  max [21. 10.  2.]
   y~ 130 n=  6 x -26..26  max [6. 2. 0.]
   y~ 140 n=  4 x -14..14  max [0. 0. 0.]
   strip: [183, 183, 183, 183, 183, 183, 183, 183, 183, 183, 183, 183, 183, 183, 183, 183, 183, 53, 53, 53, 53, 53, 53, 53, 53, 53, 53, 53, 53, 53, 53, 53, 53, 53]
392.0
{"sprite": "weapon_line", "y_lo": 54, "y_hi": 70, "x_half": 172, "color": [229, 23
... [cut] ...
 x
                else:
                    break
            return v
        if music is not None and getattr(music, "analysed", False) is True:
            x = music.band_at(tt, self.band, punch=self.punch)
        else:
            x = 0.5
        return self.a + (self.b - self.a) * x


class Scenes:
    """Renders a compiled `scenes` spec.  frame(t) -> (out, gain, label).

    Everything that can be worked out once is worked out here -- region
    index lists, axis values, palettes, preset instances -- so a frame is
    only arithmetic.  remote/offline/show.js has the same class.
    """
```

```
$ KIT="tools/showkit"; cd "~/deadmau5 app"; W="$KIT/work/weapon"; cat >> "$W/dbg.py" <<'EOF'
for L in sn["layers"]:
    print(L["fx"],L["on"],L.get("gain"),L.get("from"),L.get("to"),L.get("width"),L.get("shape"),L.get("mode"))
EOF
python3 "$W/dbg.py" | tail -6; grep -n "the draw" -A3 "shows/scenes/deadmau5 - Raise Your Weapon.scene.json" | cut -c1-400 | head -8
{"sprite": "weapon_line", "y_lo": 54, "y_hi": 70, "x_half": 172, "color": [229, 237, 247], "dx": -344, "vx": 12.5417}
preset shell {'ramp': [0.3, 0.75]} None None None None None
sweep tubes {'ramp': [0.12, 0.4]} {'n': -0.1} {'n': 1.1} {'n': 0.15} p fill
fill rims {'ramp': [0.3, 0.55]} None None None None None
orb shell {'ramp': [0.2, 0.04]} None None None None None
sweep face {'n': 0.3} {'n': 0.525} {'n': 0.525} {'ramp': [0.03, 0.09]} p band
49:  {"name": "the draw", "from": "draw", "to": "ramp", "pal": "steel", "layers": [{"fx": "preset", "name": "sprite", "on": "shell", "mix": "max", "params": {"sprite": "weapon_line", "y_lo": 54, "y_hi": 70, "x_half": 172, "color": "steel@0.9", "dx": -344, "vx": 12.5417}, "gain": [0.3, 0.75]}, {"fx": "sweep", "on": "tubes", "axis": "al", "shape": "p", "mode": "fill", "from": -0.1, "to": 1.1, "soft"
50-  {"name": "on edge", "from": "ramp", "to": "title", "pal": "moon", "layers": [{"fx": "preset", "name": "sprite", "on": "shell", "mix": "max", "params": {"sprite": "weapon_line", "y_lo": 54, "y_hi": 70, "x_half": 172, "color": "steel@0.8"}, "gain": 0.42}, {"use": "candle", "gain": 0.4}, {"use": "glints", "gain": 0.35}, {"fx": "fill", "on": "rims", "pal": "steel", "c": 0.7, "gain": [0.25, 0.55],
51-  {"name": "title", "from": "title", "to": "quiet", "pal": "moon", "layers": [{"fx": "preset", "name": "sprite", "on": "shell", "mix": "max", "params": {"sprite": "weapon_line", "y_lo": 54, "y_hi": 70, "x_half": 172, "color": "steel@0.7"}, "gain": 0.2}, {"fx": "fill", "on": "rims", "pal": "steel", "c": 0.7, "gain": [0.4, 0.6], "gate": {"pat": "x", "step": 1, "decay": 0.3}}, {"fx": "blades", "on
52-  {"name": "quiet", "from": "quiet", "to": "drop", "pal": "steel", "out": 0.25, "layers": [{"fx": "preset", "name": "sprite", "on": "shell", "mix": "max", "params": {"sprite": "weapon_line", "y_lo": 54, "y_hi": 70, "x_half": 172, "color": "hot@0.9"}, "gain": [0.3, 0.95]}, {"use": "halo", "pal": "hot", "c": 0.5, "gain": {"quiet": 0, "129": 0.05, "129.5": 0.3}, "width": [0.03, 0.12]}]},
```

```
$ KIT="tools/showkit"; cd "~/deadmau5 app"; W="$KIT/work/weapon"; B="deadmau5 - Raise Your Weapon"; date; python3 - "$W/write_treatment.py" <<'EOF'
import sys,re
p=sys.argv[1]; s=open(p).read()
def rep(a,b,n=1):
    global s
    assert a in s, a
    s=s.replace(a,b) if n==0 else s.replace(a,b,n)
# the mark called ramp collides with the value form called ramp
rep('"draw":96,"ramp":112,','"draw":96,"climb":112,')
rep('"from":"draw","to":"ramp"','"from":"draw","to":"climb"')
rep('"110":0.14,"ramp":0.3','"110":0.14,"climb":0.3')
rep('"from":"ramp","to":"title"','"from":"climb","to":"title"')
# the mo ... [cut]
Sat Oct 31 13:02:42 PDT 2026
wrote shows/scenes/deadmau5 - Raise Your Weapon.scene.json scenes 30 hits 46
deadmau5 - Raise Your Weapon: 32 scenes, 46 hits, written into shows/deadmau5 - Raise Your Weapon.json
bar 130.2                  shell max 255 mean 120.0   ears max 143 mean 108.4   first bloo
/private/tmp/claude-501/-Users-jones-deadmau5-app/208332e7-8c9f-4c25-bc21-e9a9df98fa1f/scr
```

```
$ cd "~/deadmau5 app"; sed -n 1,35p tests_more/scenes.py; sed -n 66,130p tests_more/scenes.py; which node; ls tests_more | head -30
"""scenes -- the choreographed shows, held to the same frame on both devices.

A scene show is the one thing here written by hand for a song, and the
one thing whose look depends on two renderers agreeing about arithmetic
nobody can eyeball: mau5scene.Scenes on the laptop and Scenes in
show.js on the phone.  So every test below either compares the two
frame for frame, or makes sure that when the choreography is absent,
switched off or broken, what plays is exactly the cue list that played
before it existed.
"""

import contextlib
import io
import json
import os
import shutil
import subprocess
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from test_mau5 import ok, eq, note, HERE, _node, _ShowDrive  # noqa: E402

# A note made here should reach the run's own list, not a second copy of
# the module that nobody prints.
note = getattr(sys.modules.get("__main__"), "note", note)


class _SceneDrive(_ShowDrive):
    """test_mau5's drive, marked as an analysis: band values read its curves."""
    analysed = True


def _scene_times(spec, duration, even=40):


def _compare(name, show, times, res, music, h):
    """Worst difference in counts, and the first label that disagrees."""
    import mau5show
    py = mau5show.Player(show, helmet=h, music=music)
    ok(py.scenes is not None, "%s: the laptop is not playing its scenes" % name)
    ok(res["scenes"], "%s: the phone is not playing its scenes" % name)
    worst, where = 0.0, ""
    for k, t in enumerate(times):
        a = np.asarray(py.frame(t), float)
        b = np.asarray(res["frames"][k], float).reshape(-1, 3)
        d = max(float(np.abs(a - b).max()), abs(py.gain - res["gains"][k]) * 255.0)
        if d > worst:
            worst, where = d, "%s at t=%.3f (%
... [cut] ...
egion, on a
# made-up grid, so a disagreement in a corner the shipped songs never
# reach still fails here.
SYNTHETIC = {
    "v": 1, "show": "synthetic", "lead": 0.0,
    "marks": {"go": 4, "blades": "go+12", "pre": 20, "title": 22, "boom": 30},
    "palettes": {
        "warm": [[0, 0, 0], [255, 40, 0], [255, 200, 40]],
        "loop": {"stops": [[255, 0, 0], [0, 255, 0], [0, 0, 255]], "wrap": True},
        "pure": [[0, 0, 255], [0, 255, 0], [255, 255, 255]],
/opt/homebrew/bin/node
README.md
binary.py
calib.py
ctl.py
page.py
power.py
relay.py
relayout.py
scenes.py
shows.py
tests.py
tools.py
```

```
$ cd "~/deadmau5 app"; cat remote/offline/showtest.js | head -60; sed -n 85,125p mau5offline.py; grep -n "def _node" -A22 test_mau5.py; grep -n "class _ShowDrive" -A25 test_mau5.py | head -50
// showtest.js -- render shows under node so test_mau5.py can compare
// them with mau5show.Player.  Reads {data, shows:[name], times:[t]}
// and writes, per show per time, the frame as a flat array.
'use strict';
const path = require('path');
global.window = global;
const E = require('./engine.js');
const S = require('./show.js');

let raw = '';
process.stdin.setEncoding('utf8');
process.stdin.on('data', c => { raw += c; });
process.stdin.on('end', () => {
  const job = JSON.parse(raw);
  const D = job.data;
  const dec = (b64, C) => {
    const bin = Buffer.from(b64, 'base64');
    return new C(bin.buffer, bin.byteOffset, bin.byteLength / C.BYTES_PER_ELEMENT);
  };
  const geo = { n: D.n, regions: D.regions };
  for (const k of Object.keys(D.f32)) geo[k] = dec(D.f32[k], Float32Array);
  for (const k of Object.keys(D.i16)) geo[k] = dec(D.i16[k], Int16Array);
  const h = E.makeHelmet(geo);

  // The same drive the Python side uses, written as pure functions of
  // t so neither implementation can have state the other does not.
  const music = {
    bands: true, bpm: 128.0, lock_conf: NaN,
    levelAt: t => 0.5 + 0.4 * Math.sin(t * 1.7),
    beatPhase: t => (t * 2.13) % 1,
    beatIndex: t => t * 2.13,
    isDownbeat: t => ((t * 0.53) % 1) < 0.05,
    pitchAt: t => (t * 0.11) % 1,
    centroidAt: t => 0.5 + 0.4 * Math.sin(t * 0.63),
    bandsAt: (t, n) => {
      const a = new Float64Array(n);
      for (let k = 0; k < n; k++) a[k] = 0.5 + 0.4 * Math.sin(t * 0.9 + k * 0.6);
      return a;
    },
    bandAt: (t, name, punch) => {
      const w = name === 'bass' ? 1.1 : (name === 'mid' ? 1.9 : 2.7);
      return 0.5 + 0.4 * Math.sin(t * w + (punch ? 0.3 : 0.0));
    },
  };

  // A TrackDrive's mark, so band-driven scenes read the curves; without
  // it they take the mid
... [cut] ...
e ported one are driven by the same arithmetic and compared
1300-    frame for frame.
1301-
1302-    lock_conf is NaN deliberately: offline there is no confident beat
1303-    grid to quantise to, so both sides must decide not to lock.
1304-    """
1305-    bands = True
1306-    bpm = 128.0
1307-    lock_conf = float("nan")
1308-
1309-    def level_at(self, t):
1310-        return 0.5 + 0.4 * math.sin(t * 1.7)
1311-
1312-    def beat_phase(self, t):
1313-        return (t * 2.13) % 1.0
1314-
1315-    def beat_index(self, t):
1316-        return t * 2.13
1317-
1318-    def is_downbeat(self, t):
```

```
$ cd "~/deadmau5 app"; sed -n 62,85p mau5offline.py; sed -n 60,110p remote/offline/showtest.js; grep -n "^import\|^from\|^[A-Z_]* = " mau5offline.py | head -30; grep -n "__main__" mau5offline.py
def bundle():
    """Everything the page needs that is not code.

    The geometry is exported *derived* -- nfa, nel and the rest, as
    Helmet computes them -- rather than re-derived in JavaScript.  A
    second implementation of the map is a second thing to be wrong
    about the ears, and this one would be wrong on a phone at a show
    where nobody can debug it.  Ported code can disagree about colour;
    it cannot disagree about where an LED is.
    """
    import mau5engine as E
    from mau5fx import FONT5x7, SPRITES

    h = E.Helmet()
    runs = []
    for i, r in enumerate(h.region):
        if runs and runs[-1][2] == r:
            runs[-1][1] = i
        else:
            runs.append([i, i, str(r)])

    d = {
        "n": int(h.n),
        "f32": {k: _b64(v, "<f4") for k, v in {
      const t0 = process.hrtime.bigint();
      const r = p.frame(t, music, buf);
      ms.push(Number(process.hrtime.bigint() - t0) / 1e6);
      frames.push(Array.from(buf, v => Math.round(v * 1000) / 1000));
      gains.push(p.gain);
      labels.push(r ? r.preset : null);
    }
    out[name] = { frames, gains, labels, scenes: !!p.scenes, ms };
  }
  process.stdout.write(JSON.stringify(out));
});
32:from __future__ import annotations
34:import argparse
35:import base64
36:import gzip
37:import io
38:import json
39:import os
40:import re
41:import time
42:import urllib.error
43:import urllib.request
45:import numpy as np
47:HERE = os.path.dirname(os.path.abspath(__file__))
48:SRC = os.path.join(HERE, "remote", "offline")
49:OUT = os.path.join(HERE, "data", "offline")
50:CAL = os.path.join(HERE, "data", "cal")
52:PAGE = "mau5.htm"            # what it is called on the controller
325:SONGS_PORT = 8799
326:SONGS_POINTER = "/songs.json"
793:EXTRAS = ("manifest.json", "i192.png", "i512.png", "i512m.png")
829:DRIVE_RESERVE = 64 * 1024       # left free for settings and presets
881:STANDBY_FX = {"pacifica": 101, "aurora": 38, "pride": 63,
884:STANDBY_SLOT = 1
1117:if __name__ == "__main__":
```

```
$ KIT="tools/showkit"; cd "~/deadmau5 app"; W="$KIT/work/weapon"; cat > "$W/parity.py" <<'EOF'
# The phone's twin of the renderer against the laptop's, on this show only, under node. No browser, no network.
import base64, json, math, os, subprocess, sys
sys.path.insert(0,os.getcwd())
import numpy as np, mau5engine as E, mau5show
from mau5fx import FONT5x7, SPRITES
BASE="deadmau5 - Raise Your Weapon"
show=json.load(open("shows/%s.json"%BASE))
h=E.Helmet()
b64=lambda v,f: base64.b64encode(np.asarray(v).astype(f).tobytes()).decode()
runs=[]
for i,r in enumerate(h.region):
    if runs and runs[-1][2] ... [cut]
862 times
phone playing scenes: True mean 0.09 ms a frame, worst 0.86
laptop playing scenes: True
worst 0.0005 counts at t=302.773 sung war · shields 162 · sing 162.5; 0 of 862 labels differ
```

```
$ cd "~/deadmau5 app"; date; ls -la shows/*.json | awk '{print $5, $9, $10, $11, $12, $13, $14, $15}'; grep -n "def _shows" -A30 mau5offline.py | head -60; python3 - <<'EOF'
import json,gzip
s=json.load(open("shows/deadmau5 - Raise Your Weapon.json"))
print({k:len(json.dumps(v)) for k,v in s.items()})
sc=s["scenes"]; print({k:len(json.dumps(v)) for k,v in sc.items()})
print("gz",len(gzip.compress(json.dumps(s).encode())), "gz scenes",len(gzip.compress(json.dumps(sc).encode())),"gz holds",len(gzip.compress(json.dumps(sc["grid"]).encode())))
EOF
Sat Oct 31 13:03:36 PDT 2026
94043 shows/Fred again.. & Baby Keem - leavemealone.json
163952 shows/Kaskade feat. deadmau5 - I Remember.json 
171705 shows/TIKI TIKI - Slowed.json   
66264 shows/beneath (with raxaj).json    
261829 shows/deadmau5 & Wolfgang Gartner - Animal Rights.json
187890 shows/deadmau5 - FN Pig.json   
54424 shows/deadmau5 - Ghosts n Stuff (Nero Remix).json
154011 shows/deadmau5 - Harder Better Faster Stronger.json 
179834 shows/deadmau5 - Moar Ghosts n Stuff.json 
199106 shows/deadmau5 - Raise Your Weapon.json  
132215 shows/deadmau5 - Some Chords (Radio Edit).json 
193619 shows/deadmau5 - Some Chords.json   
78141 shows/deadmau5 - Strobe (Dimension Remix).json  
190348 shows/deadmau5 - Strobe (Special Features Remix).json 
52776 shows/deadmau5 - Strobe.json    
189538 shows/deadmau5 - The Veldt.json   
196:def _shows():
197-    """The cue lists, and nothing else about a show.
198-
199-    A show is three things on the laptop: a cue list, an analysis of
200-    the track, and the track.  Only the first fits here -- the five
201-    analyses are two megabytes and the audio is sixty, against about
202-    nine hundred kilobytes free on the controller.
203-
204-    So the cue list rides in the page, the analysis goes up beside it
205-    as a compact drive file (deploy_drives), and the song lives on the
206-    phone: `songs` serves it from a laptop once and the page keeps it,
207-    after which the song is also the clock and nothing has to be
208-    started by hand.
209-    """
210-    out = {}
211-    d = os.path.join(HERE, "shows")
212-    if not os.path.isdir(d):
213-        return out
214-    for fn in sorted(os.listdir(d)):
215-        if not fn.endswith(".json"):
216-            continue
217-        try:
218-            with open(os.path.join(d, fn)) as f:
219-                sh = json.load(f)
220-        except (ValueError, OSError):
221-            continue
222-        if not sh.get("cues"):
223-            continue
224-        cues = []
225-        for c in sorted(sh["cues"], key=lambda c: c["start"]):
226-            keep = {k: c[k] for k in ("start", "end", "preset", "params",
{'track': 34, 'fps': 2, 'duration': 6, 'bpm': 5, 'beats': 4, 'analysis': 43, 'fade': 4, 'accent': 4, 'pulse': 3, 'lock': 5, 'cues': 9097, 'scenes': 103665}
{'v': 1, 'src': 51, 'treatment': 14, 'grid': 15147, 'bars': 3, 'pal': 984, 'scenes': 53391, 'hits': 33992}
gz 8284 gz scenes 6998 gz holds 1989
```

```
$ KIT="tools/showkit"; cd "~/deadmau5 app"; W="$KIT/work/weapon"; B="deadmau5 - Raise Your Weapon"; date; python3 - "$W/write_treatment.py" <<'EOF'
import sys,re
p=sys.argv[1]; s=open(p).read()
def rep(a,b):
    global s
    assert a in s, a
    s=s.replace(a,b,1)
# the flame trembles as the tempo climbs, and goes out for the title
rep('''  blade(col="steel@0.8",gain=0.42),
  {"use":"candle","gain":0.4},''','''  blade(col="steel@0.8",gain=0.42),
  {"use":"flame","gain":0.42,"wx":[4,18],"wy":[6,20],"env":{"out":5}},
  {"use":"core","gain":0.34,"wx":[3,14],"wy":[10,22],"env":{"out":5}},''')
# the b ... [cut]
Sat Oct 31 13:04:38 PDT 2026
wrote shows/scenes/deadmau5 - Raise Your Weapon.scene.json scenes 30 hits 59
deadmau5 - Raise Your Weapon: 32 scenes, 59 hits, written into shows/deadmau5 - Raise Your Weapon.json
bar 267                    shell max 203 mean   7.5   ears max 103 mean   4.5   sheathed
/private/tmp/claude-501/-Users-jones-deadmau5-app/208332e7-8c9f-4c25-bc21-e9a9df98fa1f/scr
  lowered 2      401.6s      420      752    24.4%      18.1    0.32
  last stand     406.7s      462      860    25.3%      18.1    0.35
  last stand 2   420.4s      435      864    26.1%      18.1    0.36
  fall           434.2s      415     1000    26.5%      18.1    0.16
  relit          441.0s      155      186    26.4%      18.1    0.19
  sheathed       447.9s      266      350    26.1%      18.1    0.23
  gutter         478.7s       75      163    25.6%      18.1    0.15
  worst frame 0.83 ms; no scene reaches the sustained floor
```

```
$ KIT="tools/showkit"; cd "~/deadmau5 app"; W="$KIT/work/weapon"; B="deadmau5 - Raise Your Weapon"; date; python3 - "$W/write_beats.py" "$W/write_treatment.py" <<'EOF'
import sys
p=sys.argv[1]; s=open(p).read()
a='''print("written vs true: worst'''
b='''# what is still owed at bar 128 goes onto the last hold, so the 140 section starts exactly on its anchor
r=true[512]-w[512]
last=max(i for i in range(1,513) if (w[i]-w[i-1]-SC)>0.001)
w[last:]+=r
print("residual at bar 128 was %.2f ms, moved onto beat %d"%(r*1000,last))
print("written vs true: worst'''
assert a in s
if "what is still owed" not in  ... [cut]
Sat Oct 31 13:05:42 PDT 2026
ramp: bar 112 at 210.0264, bar 128 at 238.7113, 28.6849 s, the linear ramp predicts 28.6759 s, scale 1.000315
residual at bar 128 was 1.42 ms, moved onto beat 510
written vs true: worst 5.07 ms; last ramp holds: [40.2, 40.2, 40.2, 40.2, 40.2, 40.2, 40.2, 40.2, 40.0, 39.3, 38.6, 37.9, 37.3, 36.6, 35.9, 35.2, 34.6, 33.9, 33.2, 32.6, 31.9, 31.2, 30.6, 29.9, 29.3, 28.6, 28.0, 27.3, 26.7, 26.0, 25.4, 24.7, 24.1, 23.4, 22.8, 22.2, 21.5, 20.9, 20.3, 19.6, 19.0, 18.4, 17.8, 17.1, 16.5, 15.9, 15.3, 14.7, 14.1, 13.5, 12.8, 12.2, 11.6, 11.0, 10.4, 9.8, 9.2, 8.6, 8.0, 7.4, 6.8, 6.2, 5.7, -0.0, 9.6, -0.0, 7.2, -0.0, -0.0, 7.9, -0.0, -0.0, -0.0, -0.0, -0.0]
wrote shows/scenes/deadmau5 - Raise Your Weapon.beats 1129 beats 282 bars
wrote shows/scenes/deadmau5 - Raise Your Weapon.scene.json scenes 30 hits 59
deadmau5 - Raise Your Weapon: 32 scenes, 59 hits, written into shows/deadmau5 - Raise Your Weapon.json
0:+5(1.38)  8:+7(1.48)  16:+47(1.11)  24:-1(1.17)  32:-11(1.10)  40:+9(1.23)  48:-3(5.93)  56:-3(6.56)  64:-1(3.18)  72:-1(3.34)  80:-1(3.10)  88:-1(3.68)  96:+1(6.37)  104:+3(5.30)  112:+53(1.11)  120:+15(1.14)  128:+1(1.99)  136:-1(2.42)  144:-1(2.18)  152:+3(2.12)  160:+1(2.24)  168:+1(2.25)  176:-1(1.92)  184:-3(2.06)  192:+1(2.02)  200:-1(1.97)  208:-1(1.96)  216:+1(2.12)  224:+1(2.01)  232:-3(2.13)  240:-1(3.33)  248:+1(4.36)  256:+7(1.41)  264:+7(1.37)  272:+9(1.11)  280:-45(1.14)
worst 9 ms where contrast >= 1.15, mean +0.9 ms, 30 of 36 spans
bars [2.64000000e-02 9.00264000e+01 2.10026400e+02 2.38711329e+02
 2.42139900e+02 4.34139900e+02] bpm 139.9998133335721
```

```
$ KIT="tools/showkit"; cd "~/deadmau5 app"; W="$KIT/work/weapon"; cat > "$W/ramp2.py" <<'EOF'
# Bars 112-127 sing what bars 32-47 sang, accelerated. Stretch each 4 beats of the first singing onto the same 4 beats of the second and measure the lag that remains.
import sys, numpy as np, os, subprocess
BASE="deadmau5 - Raise Your Weapon"
beats=np.loadtxt("shows/scenes/%s.beats"%BASE)
raw=subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-i","shows/%s.mp3"%BASE,"-ac","1","-ar","11025","-f","f32le","-"],capture_output=True,check=True).stdout
m=np.frombuffer(raw,dtype=np.float32); SR=11025;  ... [cut]
phrase beat  0 t=210.03: left over -1 ms, corr 0.84
phrase beat  4 t=211.90: left over -1 ms, corr 0.91
phrase beat  8 t=213.76: left over +4 ms, corr 0.95
phrase beat 12 t=215.60: left over +4 ms, corr 0.97
phrase beat 16 t=217.44: left over +4 ms, corr 0.96
phrase beat 20 t=219.27: left over +4 ms, corr 0.97
phrase beat 24 t=221.09: left over +4 ms, corr 0.98
phrase beat 28 t=222.89: left over +4 ms, corr 0.97
phrase beat 32 t=224.69: left over +4 ms, corr 0.96
phrase beat 36 t=226.48: left over +4 ms, corr 0.97
phrase beat 40 t=228.25: left over +4 ms, corr 0.95
phrase beat 44 t=230.02: left over +4 ms, corr 0.51
phrase beat 48 t=231.78: left over +4 ms, corr 0.89
phrase beat 52 t=233.53: left over +10 ms, corr 0.93
phrase beat 56 t=235.26: left over +4 ms, corr 0.94
where corr>0.75: mean +4.1 ms, worst 10 ms, 14 windows
```

```
$ KIT="tools/showkit"; cd "~/deadmau5 app"; W="$KIT/work/weapon"; B="deadmau5 - Raise Your Weapon"; date; python3 "$KIT/sheet.py" "$B" "$W/s9.png" 134.02 134.3 134.53 134.57 134.62 134.9 142.03 142.53 142.57 150.03 150.53 150.57 158.03 158.53 158.6 164.5 168.53 172 180.03 180.53 184 186.6 189.6 190.6 196.03 196.56 204.03 204.56 214.03 214.55 222.8 224.2 230.03 230.56 238.03 238.56 2>&1 | awk '{print $2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12}' | tail -38 | cut -c1-70
Sat Oct 31 13:06:31 PDT 2026
134.02 sent 884 mA shell max 43 mean 9.6 ears max
134.3 sent 606 mA shell max 31 mean 7.2 ears max
134.53 sent 685 mA shell max 19 mean 7.2 ears max
134.57 sent 750 mA shell max 5 mean 2.2 ears max
134.62 sent 663 mA shell max 13 mean 4.1 ears max
134.9 sent 331 mA shell max 27 mean 7.3 ears max
142.03 sent 909 mA shell max 52 mean 9.8 ears max
142.53 sent 685 mA shell max 20 mean 7.0 ears max
142.57 sent 750 mA shell max 6 mean 2.1 ears max
150.03 sent 845 mA shell max 54 mean 8.9 ears max
150.53 sent 678 mA shell max 24 mean 7.1 ears max
150.57 sent 750 mA shell max 10 mean 2.1 ears max
158.03 sent 874 mA shell max 32 mean 9.9 ears max
158.53 sent 678 mA shell max 17 mean 7.1 ears max
158.6 sent 721 mA shell max 8 mean 3.1 ears max
164.5 sent 456 mA shell max 47 mean 6.6 ears max
168.53 sent 724 mA shell max 22 mean 7.0 ears max
172 sent 365 mA shell max 46 mean 4.9 ears max
180.03 sent 938 mA shell max 33 mean 9.9 ears max
180.53 sent 721 mA shell max 18 mean 7.2 ears max
184 sent 438 mA shell max 32 mean 7.3 ears max
186.6 sent 747 mA shell max 15 mean 4.7 ears max
189.6 sent 706 mA shell max 41 mean 5.2 ears max
190.6 sent 733 mA shell max 45 mean 6.3 ears max
196.03 sent 1000 mA shell max 31 mean 9.9 ears max
196.56 sent 750 mA shell max 15 mean 4.9 ears max
204.03 sent 1000 mA shell max 23 mean 9.7 ears max
204.56 sent 750 mA shell max 11 mean 4.6 ears max
214.03 sent 909 mA shell max 52 mean 9.8 ears max
214.55 sent 750 mA shell max 13 mean 4.9 ears max
222.8 sent 266 mA shell max 46 mean 4.4 ears max
224.2 sent 673 mA shell max 46 mean 7.1 ears max
230.03 sent 1000 mA shell max 27 mean 9.3 ears max
230.56 sent 700 mA shell max 7 mean 2.9 ears max
238.03 sent 1000 mA shell max 27 mean 9.3 ears max
238.56 sent 650 mA shell max 6 mean 2.7 ears max
(1800, 1470)
```

```
$ KIT="tools/showkit"; ls -la --time-style=full-iso "$KIT" 2>/dev/null || ls -laT "$KIT"; cat "$KIT/sheet.py"; diff <(sed -n 1,200p "$KIT/BRIEF.md") /dev/null | grep -n "power\|guard\|mA\|sheet" | head -20
total 184
drwxr-xr-x@  13 jones  wheel    416 Oct 31 13:06:11 2026 .
drwx------@ 288 jones  wheel   9216 Oct 31 13:07:12 2026 ..
-rw-r--r--@   1 jones  wheel  11390 Oct 31 13:06:11 2026 BRIEF.md
-rw-r--r--@   1 jones  wheel    933 Oct 31 12:37:00 2026 fmt.py
-rw-r--r--@   1 jones  wheel  10884 Oct 31 12:38:05 2026 grid.py
-rw-r--r--@   1 jones  wheel  38416 Oct 31 12:37:00 2026 mau5song_new.py
-rw-r--r--@   1 jones  wheel   1751 Oct 31 12:54:25 2026 power.py
-rw-r--r--@   1 jones  wheel   1484 Oct 31 13:06:11 2026 scenepower.py
-rw-r--r--@   1 jones  wheel   2587 Oct 31 13:06:11 2026 sheet.py
-rw-r--r--@   1 jones  wheel   1652 Oct 31 12:37:00 2026 songmap.py
-rw-r--r--@   1 jones  wheel   2438 Oct 31 12:37:00 2026 spectro.py
-rw-r--r--@   1 jones  wheel   1173 Oct 31 12:37:00 2026 spritetry.py
drwxr-xr-x@  23 jones  wheel    736 Oct 31 13:06:11 2026 work
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
show = json.load(open(os.path.join("shows", base + 
... [cut] ...
 must be judged again. What the guard does that matters: the shell region is capped near 300 mA (mean about 10 of 255) with a soft knee, so anything above about 64 comes out near 62 and hues shift; when the whole frame hits 1000 mA the governor sheds the shell hard, so on a big hit with loud ears the shell can go almost black, and full-shell white comes out gray. So on hits: dark ears on the first beat if the shell has the picture, or give the moment to the ears on purpose. `python3 $KIT/scenepower.py "<base>"` prints per scene the mA, how often the governor hit, shell and ear means, and heat.
```

```
$ KIT="tools/showkit"; cd "~/deadmau5 app"; date; tail -40 "$KIT/BRIEF.md"; echo ------; cat "$KIT/sheet.py"; echo -----; cat "$KIT/power.py"; echo ------; cat "$KIT/scenepower.py"; echo ----; python3 "$KIT/power.py" "deadmau5 - Raise Your Weapon" 2>&1 | tail -20; python3 "$KIT/scenepower.py" "deadmau5 - Raise Your Weapon" 2>&1 | tail -50
Sat Oct 31 13:07:36 PDT 2026
- Only write these files for your song: `shows/scenes/<base>.beats`, `shows/scenes/<base>.scene.json`, `shows/scenes/<base>.sprites.json`, and what the tools make: `shows/<base>.json`, `shows/<base>.analysis.npz`. Nine other authors are working beside you on other songs. Never edit any code, any test, or another song's file. If you truly need an engine feature, finish without it and say so in your report.
- NEVER contact the helmet (192.168.10.172, 4.3.2.1, or anything scanning the network). Do not run `mau5show.py play`, `mau5offline.py`, `mau5ctl`, `test_mau5.py`, or anything that starts a browser. Do not commit. Do not delete MP3s.
- Text on the helmet: the song's title words only. Never spell out any other lyric.
- No power limit gets changed, ever. If a scene is too hot, make the scene lighter.
- Time: check `date`. Stop polishing and return by the deadline in your task. A complete, correct show beats a perfect half of one, so get a whole-song draft compiling early, then improve it.

## The steps
1. `python3 $KIT/grid.py scan "shows/<base>.mp3"` then `fold` over the song. Measure the grid: tempo flat across the song within about 10 ms per 8 bars; a seam or tempo change shows as a step. Decide the bar line from the music, not from the estimator: phrases turn on it and the drop's first kick is step 0 of a bar. The estimator puts bars half a bar off regularly, and a bar line wrong by a beat or two ruins every drop. Use `grid.py scan`'s phrase positions, `fold`, and the spectrogram to be sure. Then `grid.py write "<base>" --spb S --anchor T` (it builds the show), and `grid.py check "<base>"`: worst under 15 ms where the music is clear. A song that truly changes tempo needs holds or, if it speeds up, tell me; do not ship a wrong grid.
2. Und
... [cut] ...
.1     45  27.7%
raised 2          429    750     13      5     3.9    17.8     47  27.9%
lowered 2         494    808     12     21     6.0    17.9     51  28.3%
last stand        542    936     23     99     6.5    19.9     25  29.6%
last stand 2      510    946     23     99     6.1    18.7     24  30.8%
fall              415   1000     14     38     6.3    13.0     55  31.2%
relit             155    186      0      0     5.0     0.2     62  31.1%
sheathed          266    350      0      0     6.7     3.2     62  30.9%
gutter             75    163      0      0     1.3     2.1     61  30.4%
```

```
$ KIT="tools/showkit"; cd "~/deadmau5 app"; date; tail -40 "$KIT/BRIEF.md"; echo ------; cat "$KIT/sheet.py"; echo -----; cat "$KIT/power.py"; echo ------; cat "$KIT/scenepower.py"; echo ----; python3 "$KIT/power.py" "deadmau5 - Raise Your Weapon" 2>&1 | tail -20; python3 "$KIT/scenepower.py" "deadmau5 - Raise Your Weapon" 2>&1 | tail -50
Sat Oct 31 13:07:36 PDT 2026
- Only write these files for your song: `shows/scenes/<base>.beats`, `shows/scenes/<base>.scene.json`, `shows/scenes/<base>.sprites.json`, and what the tools make: `shows/<base>.json`, `shows/<base>.analysis.npz`. Nine other authors are working beside you on other songs. Never edit any code, any test, or another song's file. If you truly need an engine feature, finish without it and say so in your report.
- NEVER contact the helmet (192.168.10.172, 4.3.2.1, or anything scanning the network). Do not run `mau5show.py play`, `mau5offline.py`, `mau5ctl`, `test_mau5.py`, or anything that starts a browser. Do not commit. Do not delete MP3s.
- Text on the helmet: the song's title words only. Never spell out any other lyric.
- No power limit gets changed, ever. If a scene is too hot, make the scene lighter.
- Time: check `date`. Stop polishing and return by the deadline in your task. A complete, correct show beats a perfect half of one, so get a whole-song draft compiling early, then improve it.

## The steps
1. `python3 $KIT/grid.py scan "shows/<base>.mp3"` then `fold` over the song. Measure the grid: tempo flat across the song within about 10 ms per 8 bars; a seam or tempo change shows as a step. Decide the bar line from the music, not from the estimator: phrases turn on it and the drop's first kick is step 0 of a bar. The estimator puts bars half a bar off regularly, and a bar line wrong by a beat or two ruins every drop. Use `grid.py scan`'s phrase positions, `fold`, and the spectrogram to be sure. Then `grid.py write "<base>" --spb S --anchor T` (it builds the show), and `grid.py check "<base>"`: worst under 15 ms where the music is clear. A song that truly changes tempo needs holds or, if it speeds up, tell me; do not ship a wrong grid.
2. Und
... [cut] ...
.1     45  27.7%
raised 2          429    750     13      5     3.9    17.8     47  27.9%
lowered 2         494    808     12     21     6.0    17.9     51  28.3%
last stand        542    936     23     99     6.5    19.9     25  29.6%
last stand 2      510    946     23     99     6.1    18.7     24  30.8%
fall              415   1000     14     38     6.3    13.0     55  31.2%
relit             155    186      0      0     5.0     0.2     62  31.1%
sheathed          266    350      0      0     6.7     3.2     62  30.9%
gutter             75    163      0      0     1.3     2.1     61  30.4%
```

```
$ KIT="tools/showkit"; date; sed -n 38,80p "$KIT/BRIEF.md"; echo ------; cat "$KIT/power.py"; echo -----; cat "$KIT/scenepower.py"; cd "~/deadmau5 app"; python3 "$KIT/power.py" "deadmau5 - Raise Your Weapon"; python3 "$KIT/scenepower.py" "deadmau5 - Raise Your Weapon"
Sat Oct 31 13:07:42 PDT 2026
621 LEDs: shell 397, each ear 112 (three tubes and a rim). LEDs sit behind diffusers, so soft shapes and big motion read best; fine detail does not. On the shell: gates and pumps no faster than 8th notes (the compiler refuses faster, because whole-shell flicker reads as a fault). Ears can go faster. Current is tight: the sustained budget is about 300 mA of LED current across the whole helmet with short bursts to 1 A, and when the ears are loud the guard takes it from the shell, so keep shell gains near Tiki's (0.14 to 0.3 for full-shell layers, more for small lit areas) and ear layers 0.25 to 0.7, and confirm in `sheet.py` that the shell is really visible. Bright full-helmet white is for one moment in the whole song at most. Dark is an effect: contrast is most of what makes a hit land.

Song-specific concept follows in your task. It is a starting point. If the music says otherwise, follow the music, and keep it unique.

## Added after the first run: the long set
These shows also play back to back in a set of up to 90 minutes. The helmet can shed 11 W for ever (7.4 W of that is the LEDs' own idle draw), and the 3000 J heat bucket only covers what goes above that. When songs run hotter, heat builds up song after song, and after about 20 minutes every hit in the rest of the set gets flattened by the guard. So besides the checks above, run `python3 $KIT/power.py "<base>"` and aim for a whole-song mean of 11.5 W or less, and never above 12.5 W. Heat at the end of the song should be under about 15%. Get there with contrast rather than by dimming everything: darker verses and breakdowns, fewer full-shell layers, more small lit shapes, ears dark between hits. Peaks can stay as high as they are. A dark helmet with one bright thing moving is both chea
... [cut] ...
.1     45  27.7%
raised 2          429    750     13      5     3.9    17.8     47  27.9%
lowered 2         494    808     12     21     6.0    17.9     51  28.3%
last stand        542    936     23     99     6.5    19.9     25  29.6%
last stand 2      510    946     23     99     6.1    18.7     24  30.8%
fall              415   1000     14     38     6.3    13.0     55  31.2%
relit             155    186      0      0     5.0     0.2     62  31.1%
sheathed          266    350      0      0     6.7     3.2     62  30.9%
gutter             75    163      0      0     1.3     2.1     61  30.4%
```

```
$ KIT="tools/showkit"; cd "~/deadmau5 app"; W="$KIT/work/weapon"; B="deadmau5 - Raise Your Weapon"; wc -l mau5power.py; grep -n "def apply" -A90 mau5power.py | head -170; cat data/cal/power.json | head -60; TW=250 python3 "$KIT/sheet.py" "$B" "$W/g1.png" 10:candle 22:sing 38:moon 47.2:slide 48.02:kick 52.02 52.2:gap 66:sung 66.02 82.02 95 100:draw 108 111.5 112.05:shing 118 124:title 129.8:pick 130.03:DROP 130.2 130.5 130.54 130.57 130.62 131.02 131.5 2>&1 | cut -c1-110
     513 mau5power.py
236:    def apply(self, buf, now=None, gain=1.0):
237-        """Return (clamped frame, report).  Never raises on a bad frame.
238-
239-        `now` overrides the clock, so the thermal behaviour can be driven
240-        deterministically in a test instead of in real time.
241-
242-        `gain`, at most 1, is applied after every limit.  It is how a show
243-        pulses on the beat: anything brighter on the beat than off it,
244-        applied before the guard, is exactly what the ceilings and the
245-        governor exist to take away again, so on loud material the pulse
246-        vanished.  Dimming the result can only stay inside the limits.
247-        """
248-        now = time.monotonic() if now is None else now
249-        with np.errstate(over="ignore", invalid="ignore"):
250-            out = np.asarray(buf, np.float32).reshape(-1, 3)[:self.count].copy()
251-        # Only the LEDs both the frame and the profile have: a frame
252-        # shorter than the profile used to fail on the ceiling below,
253-        # and the phone's twin read past its end into NaN.
254-        m = len(out)
255-        # Anything that is not a number is dark, and infinity is full.
256-        # np.clip passes NaN through untouched, and the phone guard's
257-        # clamp did the same: one NaN frame made its current NaN, which
258-        # no budget compares greater than, and its thermal level NaN for
259-        # good -- governor and thermal ramp off until the page reloaded.
260-        np.nan_to_num(out, copy=False, nan=0.0, posinf=255.0, neginf=0.0)
261-        np.clip(out, 0, 255, out)
262-        asked = self.frame_ma(out)
263-        amx = out.max(1)               # what was asked of each LED, for the floor
264-
265-        # -- the ceiling, as 
... [cut] ...
8  ears max 122 mean  33.2  first blood · shields
bar 130.57             sent  750 mA  shell max   5 mean   2.3  ears max 127 mean  39.9  first blood · shields
bar 130.62             sent  663 mA  shell max  13 mean   4.1  ears max 103 mean  31.5  first blood · shields
bar 131.02             sent  884 mA  shell max  43 mean   9.6  ears max  88 mean  34.9  first blood · shields
bar 131.5              sent  367 mA  shell max  28 mean   7.1  ears max  16 mean   8.0  first blood · shields
tools/showkit/songs/wea
```

```
$ cd "~/deadmau5 app"; sed -n 326,470p mau5power.py; sed -n 60,110p mau5power.py; grep -n "MA_PER_LED_FULL_WHITE =" mau5power.py; grep -n "def allowance_w" -A25 mau5power.py
        # The floor is solved here too, not afterwards.  The governor
        # spends the budget exactly, so a floor applied as a second pass
        # has nothing left to spend and collapses to nothing: the two
        # have to be one equation.  Each LED ends at
        #     max(s ** shed_i, floor_i / level_i)
        # of what survived its region, so the floored LEDs take their
        # few milliamps off the top and everything else sheds around
        # them.  Still monotonic in s, so the bisection stands.
        #
        # And s gives light back slowly.  Solved afresh every frame, it
        # moved with whatever the ears were doing, and the shell, at
        # s ** 6, moved six times as far the other way: eq bars or a
        # sparkle overlay on the tubes pumped the shell frame to frame.
        # So s may never be more than GOV_RISE e-folds per second above
        # the last frame's -- a compressor's slow release -- while a
        # smaller s still applies at once.  Never above the s solved for,
        # so never over budget; and it runs on frames under budget too,
        # or the climb back would be one jump.  Measured through the
        # phone's twin with the test suite's music drive, at 15 and 40
        # fps, where the governor binds -- blades, spectrum, the Dimension
        # Remix blades cue, beneath's split under a sparkle overlay -- it
        # took a further 3-17% off the shell's frame-to-frame jitter on
        # top of the soft ceiling, for 2-6% of their current.  A rate per
        # region, so the shell climbs no faster than the tubes, lost 30%
        # of the light on that split and made it jitter more: one frame
        # over budget then held the shell down for two seconds.  Half
        # this rate cost up to 15%.
        cap = 1.
... [cut] ...
 not
153-        # a reading: skip it and keep the level we had.
154-        if not (math.isfinite(led_watts) and math.isfinite(now)):
155-            return self.allowance_w()
156-        if self._last is None:
157-            self._last = now
158-            return self.allowance_w()
159-        dt = max(0.0, min(now - self._last, 5.0))   # ignore long stalls
160-        self._last = now
161-        total = led_watts + self.standby_w
162-        self.level += (total - self.sustained_w) * dt
163-        self.level = min(max(self.level, 0.0), self.burst_j)
164-        return self.allowance_w()
```

```
$ cd "~/deadmau5 app"; sed -n 326,470p mau5power.py; sed -n 60,110p mau5power.py; grep -n "MA_PER_LED_FULL_WHITE =" mau5power.py; grep -n "def allowance_w" -A25 mau5power.py
        # The floor is solved here too, not afterwards.  The governor
        # spends the budget exactly, so a floor applied as a second pass
        # has nothing left to spend and collapses to nothing: the two
        # have to be one equation.  Each LED ends at
        #     max(s ** shed_i, floor_i / level_i)
        # of what survived its region, so the floored LEDs take their
        # few milliamps off the top and everything else sheds around
        # them.  Still monotonic in s, so the bisection stands.
        #
        # And s gives light back slowly.  Solved afresh every frame, it
        # moved with whatever the ears were doing, and the shell, at
        # s ** 6, moved six times as far the other way: eq bars or a
        # sparkle overlay on the tubes pumped the shell frame to frame.
        # So s may never be more than GOV_RISE e-folds per second above
        # the last frame's -- a compressor's slow release -- while a
        # smaller s still applies at once.  Never above the s solved for,
        # so never over budget; and it runs on frames under budget too,
        # or the climb back would be one jump.  Measured through the
        # phone's twin with the test suite's music drive, at 15 and 40
        # fps, where the governor binds -- blades, spectrum, the Dimension
        # Remix blades cue, beneath's split under a sparkle overlay -- it
        # took a further 3-17% off the shell's frame-to-frame jitter on
        # top of the soft ceiling, for 2-6% of their current.  A rate per
        # region, so the shell climbs no faster than the tubes, lost 30%
        # of the light on that split and made it jitter more: one frame
        # over budget then held the shell down for two seconds.  Half
        # this rate cost up to 15%.
        cap = 1.
... [cut] ...
 not
153-        # a reading: skip it and keep the level we had.
154-        if not (math.isfinite(led_watts) and math.isfinite(now)):
155-            return self.allowance_w()
156-        if self._last is None:
157-            self._last = now
158-            return self.allowance_w()
159-        dt = max(0.0, min(now - self._last, 5.0))   # ignore long stalls
160-        self._last = now
161-        total = led_watts + self.standby_w
162-        self.level += (total - self.sustained_w) * dt
163-        self.level = min(max(self.level, 0.0), self.burst_j)
164-        return self.allowance_w()
```

```
$ cd "~/deadmau5 app"; date; cat data/cal/power.json | head -60; wc -l mau5power.py; grep -n "def apply" -A90 mau5power.py | head -170
Sat Oct 31 13:09:09 PDT 2026
{
 "count": 621,
 "budget_ma": 1000.0,
 "default_ceiling": 32,
 "thermal": {
  "sustained_w": 11.0,
  "burst_j": 3000.0,
  "max_w": 25.5,
  "standby_w": 7.452,
  "ramp": 0.3
 },
 "regions": [
  {
   "name": "shell",
   "lo": 0,
   "hi": 397,
   "ceiling": 64,
   "budget_ma": 300,
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
     513 mau5power.py
236:    def apply(self, buf, now=None, gain=1.0):
237-        """Return (clamped frame, report).  Never raises on a bad frame.
238-
239-        `now` overrides the clock, so the thermal behaviour can be driven
240-        deterministically in a test instead of in real time.
241-
242-        `gain`, at most 1, is applied after every limit.  It is how a show
243-        pulses on the beat: anything brighter on the beat than off it,
244-        applied before the guard, is exactly what the ceilings and the
245-        governor exist to take away again, so on loud material the pulse
246-        vanished.  Dimming the result can only stay inside the limits.
247-        """
248-        now = time.monotonic() if now is None else now
249-        with np.errstate(over="ignore", invalid="ignore"):
250-            out = np.asarray(buf, np.float32).reshape(-1, 3)[:self.count].c
... [cut] ...
 is not None:
317-            allowed_ma = self.thermal.allowance_w() / 12.0 * 1000.0
318-            budget = min(budget, max(allowed_ma, 0.0))
319-
320-        # -- and the whole frame inside the global one ------------------
321-        # Scale region g by s**shed_g and solve for the single s that
322-        # lands on budget.  Monotonic in s, so bisect: a frame that asks
323-        # for too much comes back dimmer everywhere, weighted, rather
324-        # than with the low-priority regions amputated.
325-        #
326-        # The floor is solved here too, not afterwards.  The governor
```
