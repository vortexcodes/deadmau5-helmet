# What the fnpig builder ran and saw

Commands and their text output, in order, with long output cut. Images are left out; rerun the tools to see them. Cut off partway: the generator and treatment in the repo are the latest state.

I'll read the brief first.

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
$ cd "~/deadmau5 app"; KIT=tools/showkit; for f in fmt.py grid.py sheet.py songmap.py spectro.py spritetry.py; do echo "=== $f ==="; cat "$KIT/$f"; done; ls -la shows/ | head -50; mkdir -p "$KIT/work/fnpig"
=== fmt.py ===
"""from fmt import save; save(tr, path) -- writes a treatment one thing per line, so it can be edited by hand."""
import json
def block(items):
    return "[\n" + ",\n".join("  " + json.dumps(x) for x in items) + "\n ]"
def table(d):
    return "{\n" + ",\n".join("  %s: %s" % (json.dumps(k), json.dumps(v)) for k, v in d.items()) + "\n }"
def save(tr, path):
    out = ['{', '"v":1,', '"show":' + json.dumps(tr["show"]) + ',', '"about":' + json.dumps(tr.get("about", "")) + ',', '"lead":%s,' % json.dumps(tr.get("lead", 0)),
           '"marks":' + json.dumps(tr["marks"]) + ',', '"palettes":' + table(tr["palettes"]) + ',', '"motifs":' + table(tr.get("motifs", {})) + ',',
           '"scenes":' + block(tr["scenes"]) + ',', '"hits":' + block(tr.get("hits", [])), '}']
    open(path, "w").write("\n".join(out) + "\n")
    json.load(open(path))
    print("wrote", path, "scenes", len(tr["scenes"]), "hits", len(tr.get("hits", [])))
=== grid.py ===
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
      from the earliest downbe
... [cut] ...
es Remix).mp3
-rw-r--r--@  1 jones  staff    671293 Oct 28 00:04 deadmau5 - Strobe.analysis.npz
-rw-r--r--@  1 jones  staff     52776 Oct 30 05:03 deadmau5 - Strobe.json
-rw-r--r--@  1 jones  staff  20381996 Sep  1 10:48 deadmau5 - Strobe.mp3
-rw-r--r--@  1 jones  staff    185509 Oct 31 12:37 deadmau5 - The Veldt.analysis.npz
-rw-r--r--@  1 jones  staff      5072 Oct 31 12:37 deadmau5 - The Veldt.json
-rw-r--r--@  1 jones  staff   5446052 Oct 31 12:37 deadmau5 - The Veldt.mp3
drwxr-xr-x@ 12 jones  staff       384 Oct 31 12:37 scenes
drwxr-xr-x@ 10 jones  staff       320 Oct 27 01:28 superseded
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
$ cd "~/deadmau5 app"; KIT=tools/showkit; for f in fmt.py grid.py sheet.py songmap.py spectro.py spritetry.py; do echo "=== $f ==="; cat "$KIT/$f"; done; ls -la shows/ | head -50; mkdir -p "$KIT/work/fnpig"
=== fmt.py ===
"""from fmt import save; save(tr, path) -- writes a treatment one thing per line, so it can be edited by hand."""
import json
def block(items):
    return "[\n" + ",\n".join("  " + json.dumps(x) for x in items) + "\n ]"
def table(d):
    return "{\n" + ",\n".join("  %s: %s" % (json.dumps(k), json.dumps(v)) for k, v in d.items()) + "\n }"
def save(tr, path):
    out = ['{', '"v":1,', '"show":' + json.dumps(tr["show"]) + ',', '"about":' + json.dumps(tr.get("about", "")) + ',', '"lead":%s,' % json.dumps(tr.get("lead", 0)),
           '"marks":' + json.dumps(tr["marks"]) + ',', '"palettes":' + table(tr["palettes"]) + ',', '"motifs":' + table(tr.get("motifs", {})) + ',',
           '"scenes":' + block(tr["scenes"]) + ',', '"hits":' + block(tr.get("hits", [])), '}']
    open(path, "w").write("\n".join(out) + "\n")
    json.load(open(path))
    print("wrote", path, "scenes", len(tr["scenes"]), "hits", len(tr.get("hits", [])))
=== grid.py ===
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
      from the earliest downbe
... [cut] ...
es Remix).mp3
-rw-r--r--@  1 jones  staff    671293 Oct 28 00:04 deadmau5 - Strobe.analysis.npz
-rw-r--r--@  1 jones  staff     52776 Oct 30 05:03 deadmau5 - Strobe.json
-rw-r--r--@  1 jones  staff  20381996 Sep  1 10:48 deadmau5 - Strobe.mp3
-rw-r--r--@  1 jones  staff    185509 Oct 31 12:37 deadmau5 - The Veldt.analysis.npz
-rw-r--r--@  1 jones  staff      5072 Oct 31 12:37 deadmau5 - The Veldt.json
-rw-r--r--@  1 jones  staff   5446052 Oct 31 12:37 deadmau5 - The Veldt.mp3
drwxr-xr-x@ 12 jones  staff       384 Oct 31 12:37 scenes
drwxr-xr-x@ 10 jones  staff       320 Oct 27 01:28 superseded
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
$ cd "~/deadmau5 app"; KIT=tools/showkit; time python3 $KIT/grid.py scan "shows/deadmau5 - FN Pig.mp3" 2>&1 | tail -30; ffprobe -hide_banner "shows/deadmau5 - FN Pig.mp3" 2>&1 | tail -8; ls -la shows/scenes/ | head -40
estimator: 128.000 BPM, first bar 0.490 s, tempo lock 0.572, bar lock 0.020310386963521394; song 531.4 s
refined over the whole song: spb 0.468751 = 128.000 BPM
first half 128.000 BPM, second half 128.000 BPM (these should agree within 0.05)
phase of the music against that grid per 8 bars, ms (flat = right; one 16th = 117 ms; contrast under 1.15 means sparse, ignore it):
  0:-19(1.23)  8:+11(1.27)  16:+53(1.17)  24:-5(1.11)  32:+33(1.10)  40:+39(1.12)  48:+41(1.06)  56:-37(1.50)  64:+23(1.08)  72:-33(1.07)  80:+57(1.19)  88:+1(2.27)  96:+1(5.34)  104:+1(1.79)  112:-1(2.18)  120:-1(3.76)  128:-1(3.95)  136:-1(3.84)  144:-1(3.87)  152:-1(3.74)  160:-1(3.70)  168:-1(4.04)  176:-1(4.11)  184:-1(4.22)  192:-1(3.93)  200:+1(3.10)  208:+1(5.26)  216:+1(3.11)  224:+5(1.38)  232:-1(3.84)  240:-1(3.91)  248:-1(3.79)  256:-1(3.49)  264:-1(3.89)  272:-5(5.06)  280:-7(4.65)
change per beat position, estimator's bar 1 at 0.490 s: 0:0.72 1:0.65 2:0.69 3:0.80  (the highest is where bars really start, 0 = estimator is right)
strongest phrase positions, in beats mod 32 from that bar 1: 23(1.15), 7(1.03), 21(0.98), 31(0.95), 6(0.94), 15(0.92)
biggest single changes (time, beat from bar 1, beat mod 4): 183.8s b391 m3; 187.5s b399 m3; 191.3s b407 m3; 194.6s b414 m2; 221.3s b471 m3; 325.3s b693 m1; 386.3s b823 m3; 386.7s b824 m0; 390.0s b831 m3; 393.8s b839 m3; 397.1s b846 m2; 401.3s b855 m3; 405.0s b863 m3; 408.8s b871 m3; 501.1s b1068 m0; 503.9s b1074 m2; 504.9s b1076 m0; 507.7s b1082 m2; 508.6s b1084 m0; 511.4s b1090 m2; 512.4s b1092 m0; 513.3s b1094 m2; 528.8s b1127 m3; 529.2s b1128 m0
suggested next: grid.py fold with --spb 0.468751 --anchor 0.490, decide the bar line, then grid.py write
python3 $KIT/grid.py scan "shows/deadmau5 - FN Pig.mp3" 2>&1  2.85s user 1.28s system 100% cpu 4.112
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
$ cd "~/deadmau5 app"; KIT=tools/showkit; python3 $KIT/grid.py fold "shows/deadmau5 - FN Pig.mp3" --spb 0.46875 --anchor 0.490 2>&1 | head -190
bar 0 at 0.490 s, 128.000 BPM, 283 bars
bars 0-16   (16 steps, | every beat; one row per band)
   sub     :=.@|#@@@|*=*#|:@@*   peak 0.14
   bass    -=#%|*@@+|#*#%|-#%%   peak 0.09
   lowmid  =:+#|%=@*|=%@%|#@+%   peak 0.09
   mid     +#%+|+#*=|*#%@|*%##   peak 0.06
   pres    +#%+|=+**|**@@|#@=-   peak 0.02
   air     :-+=|::--|:=-=|*@:.   peak 0.01
bars 16-32   (16 steps, | every beat; one row per band)
   sub     +#=@|=+=#|*%*=|--*+   peak 0.22
   bass    #*+%|-#+#|@###|--##   peak 0.15
   lowmid  *##@|=**+|+#%*|*+@*   peak 0.13
   mid     +%*@|**+*|%%##|**@+   peak 0.11
   pres    *=+@|==+#|-+%@|*#@@   peak 0.02
   air     *+=%|+==*|-=+*|#+=@   peak 0.00
bars 32-48   (16 steps, | every beat; one row per band)
   sub     %#@@|%##%|###@|##+%   peak 0.18
   bass    *@*%|##*@|#++@|#%@#   peak 0.19
   lowmid  +@-#|*+**|+-%*|*%%+   peak 0.16
   mid     =@=+|#=*#|+=%+|=*@=   peak 0.15
   pres    +@++|#+#%|#+@+|=@@#   peak 0.10
   air     =%==|%=*%|*-**|:#@*   peak 0.07
bars 48-64   (16 steps, | every beat; one row per band)
   sub     %%*%|*%%%|#*#%|#*@%   peak 0.17
   bass    @#%%|%@**|#%%@|%#%%   peak 0.17
   lowmid  %@#@|%#*#|%@#%|#%@*   peak 0.11
   mid     %%:@|=#%+|+%##|%+%=   peak 0.13
   pres    %%+@|-#+*|=%##|%=%=   peak 0.17
   air     ##=@|=#*+|-#*#|#+%-   peak 0.20
bars 64-80   (16 steps, | every beat; one row per band)
   sub     ##%%|@#%#|@#@#|%%@@   peak 0.17
   bass    #+%@|%@%#|#%#@|@@@#   peak 0.17
   lowmid  %#*@|@@%%|%#*#|@%#@   peak 0.11
   mid     %%%%|@%%@|%%#@|*%@%   peak 0.10
   pres    @*%@|##%%|%#@@|##@#   peak 0.14
   air     @#%%|*+*%|*#%@|#%#@   peak 0.15
bars 80-96   (16 steps, | every beat; one row per band)
   sub     %#@*|@#%#|#*%*|#@*%   peak 0.11
   bass    @***|@*+*|#+**|@+*=   peak 0.11
   lowmid  ==%+|+=#*|#+**|@==+   peak 0.16
   mid
... [cut] ...
ry beat; one row per band)
   sub     @. :|@: -|@: .|%:..   peak 0.80
   bass    @.: |@..=|*:- |#      peak 1.19
   lowmid  #.: |@ .+|=.:.|*..    peak 1.20
   mid     * - |@..#|: =.|* =:   peak 1.06
   pres    # - |@.:%|= =.|% =    peak 1.15
   air     # + |@.=%|=.+:|%.#    peak 0.91
bars 272-283   (16 steps, | every beat; one row per band)
   sub     #.  |@= .|%.  |%=     peak 0.70
   bass    @:  |@- .|#-. |%-     peak 1.02
   lowmid  @.  |@  .|#   |#      peak 1.38
   mid     #   |@  .|# . |%      peak 1.32
   pres    %   |@  .|# . |%      peak 1.36
   air     @   |%  .|%   |#      peak 1.20
```

```
$ cd "~/deadmau5 app"; KIT=tools/showkit; W=$KIT/work/fnpig; python3 $KIT/grid.py write "deadmau5 - FN Pig" --spb 0.46875 --anchor 0.490 2>&1 | tail -5; python3 $KIT/grid.py check "deadmau5 - FN Pig"; python3 $KIT/spectro.py "deadmau5 - FN Pig" $W/whole.png; python3 $KIT/songmap.py "deadmau5 - FN Pig" > $W/map.txt; wc -l $W/map.txt; cat $W/map.txt | head -300
    8:00.49-8:15.49  lvl2  rainbow    {'period': 6.0}
    8:15.49-8:22.99  lvl2  blades     {'period': 1.875}
    8:22.99-8:37.99  lvl2  vu         {}
    8:37.99-8:51.12  lvl2  tubepulse  {'period': 1.875}
wrote shows/scenes/deadmau5 - FN Pig.beats: 1133 beats, 283 bars, bar 0 at 0.490 s, 128.000 BPM
deadmau5 - FN Pig: 128.000 BPM, 284 bars, bar 0 at 0.490 s, holds []
music against the grid per 8 bars, ms (contrast): 0:-19(1.26)  8:+5(1.27)  16:+53(1.16)  24:-5(1.12)  32:+33(1.09)  40:+39(1.12)  48:+41(1.06)  56:-33(1.51)  64:+25(1.09)  72:-33(1.07)  80:+55(1.19)  88:+1(2.27)  96:+1(5.35)  104:+3(1.75)  112:+1(2.15)  120:-1(3.75)  128:-1(3.87)  136:-1(3.83)  144:-1(3.93)  152:-1(3.73)  160:-1(3.76)  168:+1(4.14)  176:-1(4.10)  184:+1(4.12)  192:+1(3.89)  200:+1(3.05)  208:+3(5.45)  216:+3(3.11)  224:+5(1.39)  232:-1(3.89)  240:-1(3.99)  248:-1(3.79)  256:+1(3.69)  264:-1(3.88)  272:-3(5.09)  280:-3(4.43)
worst 55 ms where the music is clear enough to say, mean +2.6 ms
tools/showkit/songs/fnpig/whole.png
     286 tools/showkit/songs/fnpig/map.txt
deadmau5 - FN Pig: 284 bars, 1.88 s a bar, 531.4 s
 bar     t   E  B  M  H  notes       change
   0    0.5   3  4  0  0  F C D       
   1    2.4   1  3  0  0  F C D       
   2    4.2   2  3  0  0  F C D       
   3    6.1   3  4  0  0  F C A#      
   4    8.0   6  6  0  0  F C A       >>
   5    9.9   2  4  0  0  F C A#      >>
   6   11.7   2  4  0  0  F C D       
   7   13.6   2  3  0  0  F C A#      
   8   15.5   4  4  1  0  F C A#      
   9   17.4   3  4  0  0  F C A#      
  10   19.2   4  6  0  0  F C D       
  11   21.1   4  4  0  0  F C D    
... [cut] ...
6  C F A       
 269  504.9   5  6  4  5  C A F       
 270  506.7   6  7  5  6  C F A       
 271  508.6   5  6  4  5  C A F       
 272  510.5   6  7  5  6  C F A       
 273  512.4   6  5  5  7  C A F       
 274  514.2   5  5  3  6  C A F       
 275  516.1   4  5  2  3  C F A       >>
 276  518.0   4  5  2  3  C F A       
 277  519.9   4  5  2  3  C F A       
 278  521.7   4  5  2  3  C F A       
 279  523.6   4  5  2  3  C F A       
 280  525.5   4  5  2  3  C F A       
 281  527.4   4  4  4  6  C A F       >>
 282  529.2   0  0  0  0  D A C       >>
 283  531.1   0  0  0  0  C C# D
```

```
$ cd "~/deadmau5 app"; KIT=tools/showkit; W=$KIT/work/fnpig; B="deadmau5 - FN Pig"; python3 $KIT/spectro.py "$B" $W/s_088_128.png 88 128; python3 $KIT/spectro.py "$B" $W/s_116_136.png 116 136; python3 $KIT/spectro.py "$B" $W/s_200_240.png 200 240; python3 $KIT/spectro.py "$B" $W/s_260_284.png 260 284
tools/showkit/songs/fnpig/s_088_128.png
tools/showkit/songs/fnpig/s_116_136.png
tools/showkit/songs/fnpig/s_200_240.png
tools/showkit/songs/fnpig/s_260_284.png
```

```
$ cd "~/deadmau5 app"; KIT=tools/showkit; W=$KIT/work/fnpig; B="deadmau5 - FN Pig"; python3 $KIT/spectro.py "$B" $W/s_000_032.png 0 32; python3 $KIT/spectro.py "$B" $W/s_024_064.png 24 64; python3 $KIT/spectro.py "$B" $W/s_060_100.png 60 100; python3 $KIT/spectro.py "$B" $W/s_160_180.png 160 180
tools/showkit/songs/fnpig/s_000_032.png
tools/showkit/songs/fnpig/s_024_064.png
tools/showkit/songs/fnpig/s_060_100.png
tools/showkit/songs/fnpig/s_160_180.png
```

```
$ cd "~/deadmau5 app"; wc -l mau5scene.py mau5engine.py mau5fx.py mau5show.py mau5preview.py; grep -n "def \|sprites" mau5scene.py | head -120; grep -n "sprite" mau5engine.py mau5fx.py | head -50
    1344 mau5scene.py
    1388 mau5engine.py
     992 mau5fx.py
    1000 mau5show.py
     214 mau5preview.py
    4938 total
132:def treatment_path(base):
136:def load_treatment(base_or_path):
151:def grid_of(music):
190:def src_of(base):
203:def _helmet():
210:def _edge_mm(h):
218:    def __init__(self, tr, grid, bars, h):
244:    def bar(self, v, what="bar"):
266:    def value(self, v, what):
294:    def colour(self, v, what):
308:    def expand(self, layers, what):
327:    def layer(self, L, pal, what, span):
372:    def gate(self, g, what):
385:    def pump(self, p, what):
399:    def preset(self, L, out, what, span):
434:    def compile(self):
498:        for i, hdef in enumerate(tr.get("hits") or []):
522:def _merge(a, b):
533:def _dark(b0, b1):
538:def compile_treatment(tr, grid, bars, h=None, src=""):
550:def compile_for(base, music):
555:def _show_and_music(base):
566:def compile_show(base, verbose=False):
579:def attach(base, verbose=True):
596:def _region_mask(h, on):
623:def _min_gap_beats(pat, step):
635:def lint(spec, h=None, music=None):
656:    def layer_checks(L, what, span):
736:    def texts(layers):
789:def pal_lookup(stops, wrap, c):
808:def _pal_vec(P, c):
826:def _hash_sin(x):
830:def _h32(h):
844:def _gate(lb, pat, step, decay, floor, HB):
862:    def __init__(self, v):
877:    def at(self, p, bar, music, tt):
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
1240:d
... [cut] ...
apped shell
mau5fx.py:536:    because that is how sprites and glyphs are written.
mau5fx.py:570:    def __init__(self, helmet, sprite="x_eyes", col=None, row_from_top=3,
mau5fx.py:573:        self.bmp = sprite_bitmap(sprite)
mau5fx.py:585:    """Cycle a list of sprites -- one per beat, or at a fixed rate."""
mau5fx.py:587:    def __init__(self, helmet, sprites=("eyes", "wink"), fps=2.0, col=None,
mau5fx.py:590:        self.bmps = [sprite_bitmap(s) for s in sprites]
mau5fx.py:990:        b = sprite_bitmap(name)
mau5fx.py:991:        print("  sprite %-12s %dx%d" % (name, b.shape[1], b.shape[0]))
```

```
$ cd "~/deadmau5 app"; sed -n 1,130p mau5scene.py
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
, "sharp": 4.0, "spread": 0.0, "dens": 1.0},
}
FX_STATIC = {
    "fill": {},
    "grad": {"axis": "y", "axis2": "x", "wave": "tri"},
    "sweep": {"axis": "y", "shape": "saw", "mode": "band"},
    "sparks": {"loop": 0, "seed": 0.0},
    "blades": {"seq": ["0", "1", "2", "012"], "side": "both"},
    "preset": {"name": None, "params": None, "fit": False},
    "orb": {},
    "twinkle": {"seed": 0.0},
}

MAX_SCENE_LAYERS, MAX_HIT_LAYERS, MAX_HITS_AT_ONCE = 6, 3, 2


class TreatmentError(ValueError):
    pass


# ----------------------------------------------------------------------
# the treatment
```

```
$ cd "~/deadmau5 app"; sed -n 218,520p mau5scene.py
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
            except ValueError:
                pass
            m = re.match(r"^([A-Za-z_][\w ]*?)\s*(?:([+-])\s*(
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
$ cd "~/deadmau5 app"; sed -n 596,790p mau5scene.py; sed -n 1240,1303p mau5scene.py; sed -n 625,790p mau5engine.py
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
n runs down
    lines that are really there.  The bright head leads and the trail
    follows -- it was the other way round, which read as a curtain.  And
    the ears were simply off for all of it, in what is the shows'
    most-used effect; each tube is a column now, falling from its high
    end, with the rims as a faint outline.  `columns` is only used by a
    map that has no strips.
    """
    name = "matrix"
    params = {"color": (0, 255, 70), "columns": 24, "speed": 0.55,
              "tail": 0.30}

    def render(self, h, t, music=None):
        c = np.array(self.p["color"], float)
```

```
$ cd "~/deadmau5 app"; sed -n 1,130p mau5scene.py
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
, "sharp": 4.0, "spread": 0.0, "dens": 1.0},
}
FX_STATIC = {
    "fill": {},
    "grad": {"axis": "y", "axis2": "x", "wave": "tri"},
    "sweep": {"axis": "y", "shape": "saw", "mode": "band"},
    "sparks": {"loop": 0, "seed": 0.0},
    "blades": {"seq": ["0", "1", "2", "012"], "side": "both"},
    "preset": {"name": None, "params": None, "fit": False},
    "orb": {},
    "twinkle": {"seed": 0.0},
}

MAX_SCENE_LAYERS, MAX_HIT_LAYERS, MAX_HITS_AT_ONCE = 6, 3, 2


class TreatmentError(ValueError):
    pass


# ----------------------------------------------------------------------
# the treatment
```

```
$ cd "~/deadmau5 app"; sed -n 218,520p mau5scene.py
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
            except ValueError:
                pass
            m = re.match(r"^([A-Za-z_][\w ]*?)\s*(?:([+-])\s*(
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
$ cd "~/deadmau5 app"; sed -n 596,790p mau5scene.py; sed -n 1240,1303p mau5scene.py; sed -n 625,790p mau5engine.py
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
n runs down
    lines that are really there.  The bright head leads and the trail
    follows -- it was the other way round, which read as a curtain.  And
    the ears were simply off for all of it, in what is the shows'
    most-used effect; each tube is a column now, falling from its high
    end, with the rims as a faint outline.  `columns` is only used by a
    map that has no strips.
    """
    name = "matrix"
    params = {"color": (0, 255, 70), "columns": 24, "speed": 0.55,
              "tail": 0.30}

    def render(self, h, t, music=None):
        c = np.array(self.p["color"], float)
```

```
$ cd "~/deadmau5 app"; sed -n 906,1195p mau5scene.py
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
x["layers"]:
                    self._render(P, B, bar, hb, x["beats"], hp, music, tt)
                label += " · " + x["name"]
                nh += 1
                if nh == MAX_HITS_AT_ONCE:
                    break
        out = np.clip(acc, 0, 255)
        gain = 1.0
        if sc["pump"] is not None:
            pat, step, decay, depth = sc["pump"]
            gain = 1 - depth + depth * _gate(lb, pat, step, decay, 0.0, self.HB)
        return out, gain, label


# ----------------------------------------------------------------------
# what the bar map says, for writing marks against
```

```
$ cd "~/deadmau5 app"; KIT=tools/showkit; W=$KIT/work/fnpig; cat > $W/ledmap.py <<'EOF'
import sys, os
sys.path.insert(0, os.getcwd())
import numpy as np, mau5engine as E
h = E.Helmet()
print("n", h.n, "shell", h.shell.sum(), "ears", h.ears.sum())
px, py = h.px, h.py
s = h.shell
print("shell px range", px[s].min(), px[s].max(), "py range", py[s].min(), py[s].max())
print("ear1 px", px[h.ear1].min(), px[h.ear1].max(), "py", py[h.ear1].min(), py[h.ear1].max())
print("ear2 px", px[h.ear2].min(), px[h.ear2].max(), "py", py[h.ear2].min(), py[h.ear2].max())
# ascii density at 17x17 cells with y_lo -108 ... [cut]
n 621 shell 398 ears 223
shell px range -170.94 170.95 py range -111.27 167.77
ear1 px -388.21 -55.76 py 51.8 383.94
ear2 px 55.56 387.42 py 54.72 384.91
   161 ...........222.11.21211.11112...........
   151 .........2111.11.1.1.1.1.111.21.........
   142 ........422111111111111111111224........
   132 ......3221..11111.1111.11111..1223......
   122 .....4121..111.111.11.111.111..1214.....
   112 ........................................
   102 ...13211111.111.11.11.11.111.11111231...
    93 ..2221111.11.11.11.11.11.11.11.1111222..
    83 ........................................
    73 .131111111.11.11.1.11.1.11.11.111111131.
    63 .3211111.11.11.1.1.11.1.1.11.11.1111123.
    53 ........................................
    44 31211.111......................111.11213
    34 ........................................
    24 321..................................123
    14 1......................................1
     5 ........................................
    -5 ........................................
   -15 ........................................
   -25 1......................................1
   -35 3......................................3
   -44 ........................................
   -54 22....................................22
   -64 ...1.................................1..
   -74 .311................................2.3.
   -84 ..32111..........................11123..
   -93 ...3211111....................1111123...
  -103 ........................................
tube 0 count 58 ear1 x -349.0 -201.0 y 66.93 215.77
tube 1 count 72 ear1 x -309.87 -130.15 y 128.39 302.63
tube 2 count 56 ear1 x -237.37 -86.94 y 215.33 349.09
rim1 count 18 x -388.21 -55.76 y 51.8 383.94
rim2 count 19 x 55.56 387.42 y 54.72 384.91
attrs ['along', 'az', 'depth', 'ea', 'ear1', 'ear2', 'ears', 'el', 'er', 'fa', 'group', 'mask', 'n', 'nel', 'nfa', 'nx', 'ny', 'px', 'py', 'region', 'rims', 'rows', 'shell', 'tube', 'tubes', 'u', 'xyz']
```

```
$ cd "~/deadmau5 app"; sed -n 906,1195p mau5scene.py
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
x["layers"]:
                    self._render(P, B, bar, hb, x["beats"], hp, music, tt)
                label += " · " + x["name"]
                nh += 1
                if nh == MAX_HITS_AT_ONCE:
                    break
        out = np.clip(acc, 0, 255)
        gain = 1.0
        if sc["pump"] is not None:
            pat, step, decay, depth = sc["pump"]
            gain = 1 - depth + depth * _gate(lb, pat, step, decay, 0.0, self.HB)
        return out, gain, label


# ----------------------------------------------------------------------
# what the bar map says, for writing marks against
```

```
$ cd "~/deadmau5 app"; KIT=tools/showkit; W=$KIT/work/fnpig; cat > $W/ledmap.py <<'EOF'
import sys, os
sys.path.insert(0, os.getcwd())
import numpy as np, mau5engine as E
h = E.Helmet()
print("n", h.n, "shell", h.shell.sum(), "ears", h.ears.sum())
px, py = h.px, h.py
s = h.shell
print("shell px range", px[s].min(), px[s].max(), "py range", py[s].min(), py[s].max())
print("ear1 px", px[h.ear1].min(), px[h.ear1].max(), "py", py[h.ear1].min(), py[h.ear1].max())
print("ear2 px", px[h.ear2].min(), px[h.ear2].max(), "py", py[h.ear2].min(), py[h.ear2].max())
# ascii density at 17x17 cells with y_lo -108 ... [cut]
n 621 shell 398 ears 223
shell px range -170.94 170.95 py range -111.27 167.77
ear1 px -388.21 -55.76 py 51.8 383.94
ear2 px 55.56 387.42 py 54.72 384.91
   161 ...........222.11.21211.11112...........
   151 .........2111.11.1.1.1.1.111.21.........
   142 ........422111111111111111111224........
   132 ......3221..11111.1111.11111..1223......
   122 .....4121..111.111.11.111.111..1214.....
   112 ........................................
   102 ...13211111.111.11.11.11.111.11111231...
    93 ..2221111.11.11.11.11.11.11.11.1111222..
    83 ........................................
    73 .131111111.11.11.1.11.1.11.11.111111131.
    63 .3211111.11.11.1.1.11.1.1.11.11.1111123.
    53 ........................................
    44 31211.111......................111.11213
    34 ........................................
    24 321..................................123
    14 1......................................1
     5 ........................................
    -5 ........................................
   -15 ........................................
   -25 1......................................1
   -35 3......................................3
   -44 ........................................
   -54 22....................................22
   -64 ...1.................................1..
   -74 .311................................2.3.
   -84 ..32111..........................11123..
   -93 ...3211111....................1111123...
  -103 ........................................
tube 0 count 58 ear1 x -349.0 -201.0 y 66.93 215.77
tube 1 count 72 ear1 x -309.87 -130.15 y 128.39 302.63
tube 2 count 56 ear1 x -237.37 -86.94 y 215.33 349.09
rim1 count 18 x -388.21 -55.76 y 51.8 383.94
rim2 count 19 x 55.56 387.42 y 54.72 384.91
attrs ['along', 'az', 'depth', 'ea', 'ear1', 'ear2', 'ears', 'el', 'er', 'fa', 'group', 'mask', 'n', 'nel', 'nfa', 'nx', 'ny', 'px', 'py', 'region', 'rims', 'rows', 'shell', 'tube', 'tubes', 'u', 'xyz']
```

```
$ cd "~/deadmau5 app"; KIT=tools/showkit; W=$KIT/work/fnpig; cat > $W/fold2.py <<'EOF'
import sys, os
sys.path.insert(0, os.getcwd()); sys.path.insert(0, os.environ["KIT"])
import numpy as np, grid
d = grid.env_of("shows/deadmau5 - FN Pig.mp3")
spb=0.46875; t0=0.490
tt=d["tt"]
CH=" .:-=+*#%@"
def fold(lo,hi,nbars=1,bands=("sub","bass","lowmid","mid","pres","air")):
    n=16*nbars
    print("bars %g-%g, fold over %d bars"%(lo,hi,nbars))
    for nm in bands:
        e=d[nm+"_od"]
        o=np.zeros(n); c=np.zeros(n)
        b=lo
        k=0
        while b+k/16<hi:
            t=t0+(b+k/16)*4*spb
  ... [cut]
bars 0-32 per-bar onset strip (sub+bass)
     0    0.49      | -. |.   | #  |
     1    2.37      |  :.|  . |  - |
     2    4.24      |  + |    |  @ |
     3    6.12      |  #.|    |  *.|
     4    7.99      |  : | .  | : .|
     5    9.87      | @..|    | .. |
     6   11.74      |#   |   #|   .|
     7   13.62    .:| .  |  - |   .|
     8   15.49   :..|    |#...|   -|
     9   17.36  .. .|   .|..  |.   |
    10   19.24    .@|    |  -:| .  |
    11   21.11    :.| :.@|.   |  .:|
    12   22.99    . |@. .|  # |..  |
    13   24.86   :  |.  *|    | +. |
    14   26.74  .  @|  . | # .|  .=|
    15   28.61      | @ .|: .@|... |
    16   30.49   @..|: .@|    | :. |
    17   32.37    -.| :  |%. .|  . |
    18   34.24  . .#|-   |   .|  # |
    19   36.12  .   |   .| @. |  :.|
    20   37.99      |... | +. |  * |
    21   39.87  .  %| ...|::..| .: |
    22   41.74  .. -|... |=.  | .. |
    23   43.62  ....|  :.| . -|..  |
    24   45.49  %...| *. |. -.|.  -|
    25   47.37  -:.#|.: .|+:. | -. |
    26   49.24   %::| .+ |..#:|   +|
    27   51.12  .. =|....|: . |=. .|
    28   52.99   .  | #  | =  |  . |
    29   54.87  -.= |:.+.|.:% |  ..|
    30   56.74   .  |  .#|   :|   #|
    31   58.62     *|   #|-=-#|::.#|
bars 0-32 per-bar onset strip (lowmid+mid+pres)
     0    0.49      |    | .. | :  |
     1    2.37      | .  |    | :. |
     2    4.24      |  = |.   |..: |
     3    6.12      | .:.|  -.|:.. |
     4    7.99     .|  : |.   | =. |
     5    9.87      |  . |  . |.   |
     6   11.74  . .:|:.. |..:*| :. |
     7   13.62  ...:|..=.|. ..|.:..|
     8   15.49    ..|+.. |..::|  .:|
     9   17.36  .:- |... | .::|:. .|
    10   19.24   .-+|..  |...:|.:. |
    11   21.11  :.  | ..=|: :.|. .:|
    12   22.99  :.::|+ ..| .*.|...-|
    13   24.86   .: |:   |...:|-+:.|
    14   26.74  :.:=|.:..| @.:|:..%|
    15   28.61    - |:=..|. .*|.:: |
    16   30.49  .@:.|:.: |. ..|:...|
    17   32.37  . # |.:..|*.::|....|
    18   34.24   . #|....|.. .| :*.|
    19   36.12  .:. | :::|.#:.|:.@:|
    20   37.99  .:..|.  .|.   |..@:|
    21   39.87  ...%|  . |=:..|.- .|
    22   41.74   .+ |:..=|. -.|:: :|
    23   43.62   :..| :*-|. .*|....|
    24   45.49  %.  |.# .|.-..| .= |
    25   47.37   .:@| . :| ..:|= ..|
    26   49.24  .+:.|..  |:.@.|..: |
    27   51.12  ...@|..:.|..::|# .:|
    28   52.99  %..:|. ..|.@::| @..|
    29   54.87  .. .|..=.|--#:|-:+:|
    30   56.74  .-=-|=-: |. - |.:-#|
    31   58.62  :-.+|=: *|.=-%|-.:%|
```

```
$ cd "~/deadmau5 app"; KIT=tools/showkit; W=$KIT/work/fnpig; cat > $W/pulse.py <<'EOF'
import sys, os
sys.path.insert(0, os.getcwd()); sys.path.insert(0, os.environ["KIT"])
import numpy as np, grid
d = grid.env_of("shows/deadmau5 - FN Pig.mp3")
tt=d["tt"]; dt=tt[1]-tt[0]
spb=.46875
for lo,hi in ((1,45),(47,90),(120,160)):
  for nm in ("sub","bass","lowmid","mid"):
    m=(tt>=lo)&(tt<hi)
    v=d[nm][m]; v=v-np.convolve(v,np.ones(400)/400,"same")
    ac=np.correlate(v,v,"full")[len(v)-1:]
    ac/=ac[0]
    # peaks up to 4 s
    from numpy import argmax
    pk=[(i*dt,ac[i]) for i in range(5,int(4/dt ... [cut]
1 45 sub 0.662(0.33)[1.41b]
1 45 bass 0.163(0.30)[0.35b] 0.325(0.23)[0.69b] 0.580(0.19)[1.24b]
1 45 lowmid 0.604(0.13)[1.29b]
1 45 mid 0.197(0.16)[0.42b] 0.302(0.21)[0.64b] 0.430(0.26)[0.92b] 0.685(0.19)[1.46b] 1.161(0.21)[2.48b] 2.276(0.11)[4.85b] 2.972(0.17)[6.34b] 3.390(0.14)[7.23b]
47 90 sub 0.488(0.45)[1.04b] 0.998(0.28)[2.13b] 1.486(0.13)[3.17b] 2.624(0.10)[5.60b] 2.647(0.11)[5.65b] 2.670(0.10)[5.70b]
47 90 bass 0.441(0.49)[0.94b] 0.871(0.28)[1.86b] 0.894(0.28)[1.91b] 1.312(0.11)[2.80b] 1.335(0.11)[2.85b]
47 90 lowmid 0.360(0.35)[0.77b] 0.511(0.19)[1.09b] 0.685(0.20)[1.46b] 0.708(0.20)[1.51b] 1.045(0.15)[2.23b]
47 90 mid 0.383(0.49)[0.82b] 0.720(0.24)[1.54b] 1.358(0.11)[2.90b]
120 160 sub 0.070(0.81)[0.15b] 0.116(0.75)[0.25b] 0.139(0.73)[0.30b] 0.197(0.66)[0.42b] 0.221(0.65)[0.47b] 0.244(0.61)[0.52b] 0.267(0.56)[0.57b] 0.290(0.50)[0.62b] 0.313(0.46)[0.67b] 0.337(0.43)[0.72b] 0.360(0.39)[0.77b] 0.383(0.35)[0.82b]
120 160 bass 0.221(0.20)[0.47b] 0.244(0.13)[0.52b] 1.649(0.17)[3.52b] 1.672(0.21)[3.57b] 1.730(0.27)[3.69b] 1.753(0.29)[3.74b] 1.776(0.30)[3.79b] 1.800(0.30)[3.84b] 1.823(0.29)[3.89b] 3.390(0.15)[7.23b] 3.448(0.18)[7.36b] 3.471(0.19)[7.41b]
120 160 lowmid 0.313(0.19)[0.67b] 0.337(0.19)[0.72b] 0.418(0.21)[0.89b] 0.441(0.21)[0.94b] 0.836(0.21)[1.78b] 1.057(0.13)[2.25b] 1.161(0.14)[2.48b] 2.334(0.10)[4.98b] 2.357(0.10)[5.03b] 3.425(0.10)[7.31b] 3.495(0.11)[7.46b] 3.529(0.11)[7.53b]
120 160 mid 0.197(0.66)[0.42b] 0.766(0.41)[1.63b] 1.173(0.23)[2.50b] 1.265(0.21)[2.70b] 1.463(0.13)[3.12b] 1.544(0.12)[3.29b]
pulse peaks: 0.07 1.07 1.63 2.07 2.55 3.04 3.56 4.01 4.48 4.97 5.63 5.90 6.84 7.23 7.77 8.30 8.67 9.20 9.58 10.46 11.34 12.21 12.72 13.08 13.60 13.93 14.29 14.77 15.39 15.60 16.44 17.24 18.05 18.85 19.34 19.64 20.42 20.79 21.20 21.51 21.75 21.97 22.72 23.48 23.81 24.23 24.96 25.69 26.42 27.14 27.86 28.56 29.25 29.64 29.95
in beats: -0.90 1.23 2.42 3.36 4.40 5.44 6.56 7.50 8.52 9.56 10.97 11.54 13.54 14.39 15.52 16.66 17.46 18.57 19.39 21.27 23.15 25.01 26.10 26.87 27.96 28.68 29.44 30.46 31.80 32.24 34.03 35.74 37.47 39.18 40.22 40.86 42.52 43.31 44.18 44.85 45.35 45.82 47.43 49.04 49.75 50.65 52.21 53.77 55.33 56.86 58.40 59.88 61.35 62.19 62.86
```

```
$ cd "~/deadmau5 app"; KIT=tools/showkit; W=$KIT/work/fnpig; cat > $W/pulse2.py <<'EOF'
import sys, os, subprocess
sys.path.insert(0, os.getcwd()); sys.path.insert(0, os.environ["KIT"])
import numpy as np
raw = subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-i","shows/deadmau5 - FN Pig.mp3","-ac","1","-ar","22050","-f","f32le","-"],capture_output=True,check=True).stdout
m=np.frombuffer(raw,dtype=np.float32)
sr=22050
np.save(os.environ["KIT"]+"/work/fnpig/mono.npy",m)
# band envelope by short FFT with small hop
N=2048;H=110
win=np.hanning(N)
f=np.fft.rfftfreq(N,1/sr)
def env(t0,t1,lo ... [cut]
t, gap, beats since 0.49
1.06(0.99) 2.06(0.97) 3.03(0.97) 4.00(0.96) 4.96(0.94) 5.90(0.93) 6.83(0.93) 7.76(0.90) 8.66(0.90) 9.56(0.89) 10.45(0.88) 11.33(0.87)
12.20(0.87) 13.07(0.86) 13.93(0.83) 14.76(0.83) 15.59(0.84) 16.43(0.81) 17.24(0.81) 18.05(0.80) 18.85(0.79) 19.64(0.77) 20.41(0.78) 21.19(0.77)
21.96(0.75) 22.71(0.76) 23.47(0.75) 24.22(0.73) 24.95(0.74) 25.69(0.72) 26.42(0.72) 27.13(0.71) 27.85(0.70) 28.55(0.69) 29.25(0.70) 29.94(0.68)
30.63(0.68) 31.31(0.68) 31.99(0.67) 32.66(0.66) 33.32(0.66) 33.97(0.66) 34.63(0.65) 35.28(0.64) 35.92(0.63) 36.55(0.63) 37.19(0.62) 37.81(0.62)
38.43(0.61) 39.05(0.61) 39.66(0.61) 40.27(0.60) 40.87(0.60) 41.48(0.58) 42.06(0.59) 42.65(0.58) 43.23(0.57) 43.81(0.58) 44.39(0.58) 44.97(0.56)
45.53(0.57) 46.10(0.55) 46.65(0.56) 47.21(0.56) 47.77(0.54) 48.31(0.54) 48.86(0.53) 49.39(0.54) 49.93(0.53) 50.46(0.54) 51.00(0.53) 51.52(0.52)
52.04(0.52) 52.57(0.51) 53.08(0.51) 53.59(0.51) 54.10(0.49) 54.59(0.51) 55.11(0.50) 55.61(0.48) 56.09(0.49) 56.58(0.49) 57.07(0.49) 57.57(0.47)
58.04(0.48) 58.52(0.48) 59.00(0.48) 59.49(0.46) 59.95(0.47) 60.42(0.47) 60.89(0.46) 61.35(0.46) 61.81(0.46) 62.28(0.44) 62.72(0.45) 63.17(0.47)
63.65(0.42) 64.07(0.44) 64.51(0.45) 64.96(0.45) 65.41(0.43) 65.85(0.45) 66.30(0.86) 67.16(0.40) 67.56(0.85) 68.41(0.44) 68.85(0.38) 69.23(0.85)
70.08(1.23) 71.31(0.38) 71.70(0.80) 72.50(0.42) 72.92(1.57) 74.48(7.01) 81.50(20.01) 101.51(1.93) 103.44(0.79) 104.22(0.53)
```

```
$ cd "~/deadmau5 app"; sed -n 860,905p mau5scene.py; python3 - <<'EOF'
import numpy as np
z=np.load("shows/deadmau5 - FN Pig.analysis.npz",allow_pickle=True)
print(z.files)
print("fps",z["fps"],"dur",z["duration"])
for k in z.files:
    if k.startswith("b_"):
        v=z[k]; print(k,v.shape,float(v.min()),float(v.max()),float(np.median(v)))
EOF
grep -n "band\b\|\"band\"\|def band\|b_%s\|band_at\|def env\|punch" mau5show.py mau5engine.py | head -30
    __slots__ = ("kind", "a", "b", "bars", "vals", "band", "punch")

    def __init__(self, v):
        if "n" in v:
            self.kind, self.a = 0, float(v["n"])
        elif "ramp" in v:
            self.kind, self.a, self.b = 1, float(v["ramp"][0]), float(v["ramp"][1])
        elif "keys" in v:
            self.kind = 2
            self.bars = [float(k[0]) for k in v["keys"]]
            self.vals = [float(k[1]) for k in v["keys"]]
        elif "band" in v:
            self.kind, self.band = 3, str(v["band"])
            self.a, self.b, self.punch = float(v["lo"]), float(v["hi"]), bool(v["punch"])
        else:
            raise ValueError("not a value: %r" % (v,))

    def at(self, p, bar, music, tt):
        k = self.kind
        if k == 0:
            return self.a
        if k == 1:
            return self.a + (self.b - self.a) * p
        if k == 2:
            v = self.vals[0]
            for b, x in zip(self.bars, self.vals):
                if b <= bar:
                    v = x
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

['fps', 'duration', 'bpm', 'beats', 'bars', 'levels', 'energy', 'onset', 'sections', 'lock', 'v', 'chroma', 'shape', 'src', 'b_bass_e', 'b_bass_p', 'b_mid_e', 'b_mid_p', 'b_high_e', 'b_high_p']
... [cut] ...
s")
mau5show.py:276:        mid = self.band_at(t, "mid")
mau5show.py:277:        hi = self.band_at(t, "high")
mau5show.py:281:    def bands_at(self, t, n):
mau5show.py:283:        with a per-band lag, which looks like a spectrum analyser
mau5show.py:313:# Second layers, each riding a frequency band.  Sparse and fast, so
mau5show.py:487:    sparse effect rides a frequency band over the top, so the hats can
mau5show.py:524:            band = "high" if lvl >= 2 else "bass"
mau5show.py:526:                band = "bass"
mau5show.py:527:            oname, okw = _pick(OVERLAYS[band], recent[:2], rng)
```

```
$ cd "~/deadmau5 app"; KIT=tools/showkit; W=$KIT/work/fnpig; export KIT; python3 $W/fold2.py strip 88 128 lowmid,mid,pres,air; python3 $W/fold2.py strip 88 128 sub,bass;
bars 88-128 per-bar onset strip (lowmid+mid+pres+air)
    88  165.49      |    |    |    |
    89  167.37  .   |    |    |    |
    90  169.24      |    |    |    |
    91  171.12      |    |    |+   |
    92  172.99    = |    |- - |    |
    93  174.87      |    |  -:|- . |
    94  176.74  . - |    |- = |    |
    95  178.62      |    |=   |*   |
    96  180.49    + |    |= = |    |
    97  182.37  .   |    |  -:|= . |
    98  184.24  : = |    |= = |    |
    99  186.12      |    |    |*   |
   100  187.99    * |    |= + |    |
   101  189.87      |    |  =:|- . |
   102  191.74  : = |    |= = |    |
   103  193.62      |    |+   |+   |
   104  195.49    + |    |- = |    |
   105  197.37      |    |  ..|:   |
   106  199.24    . |    |. . |    |
   107  201.12      |    |    |.   |
   108  202.99    . |    |. . |    |
   109  204.87      |    |    |. . |
   110  206.74    . |    |.   |    |
   111  208.62      |    |    |.   |
   112  210.49    . |    |    |    |
   113  212.37      |    |    |.   |
   114  214.24      |    |    |    |
   115  216.12      |    |    |.   |
   116  217.99      |    |    |    |
   117  219.87      |    |    |: . |
   118  221.74  : = |+ :+|: : |% = |
   119  223.62  - # |@ =*|: : |@ =.|
   120  225.49  : * |@ =@|: - |@ = |
   121  227.37  - % |@ =#|: *-|+ =.|
   122  229.24  : * |@ =@|: - |@ + |
   123  231.12  - # |@ =#|: : |@ +.|
   124  232.99  . * |@ =%|: = |@ = |
   125  234.87  - % |@.: |:   |- . |
   126  236.74  : = |+ :#|: : |@ = |
   127  238.62  - # |@ =#|. : |@ = |
bars 88-128 per-bar onset strip (sub+bass)
    88  165.49  ..  |. . |.   |    |
    89  167.37  .   |.. .|    |..  |
    90  169.24  .   |.  .|  . |.   |
    91  171.12      |.   |.   |:   |
    92  172.99     :|.. .|.   |    |
    93  174.87  .   |  . |    |.   |
 
... [cut] ...
::|-:..|
   112  210.49  : ..|.:..|:..:|.-:-|
   113  212.37  :..:|:..:|.:: |.:.:|
   114  214.24  .:::| :::|-...|:...|
   115  216.12  - ..|:::.|. .-| :.-|
   116  217.99  ..-=|: . |:-::|..:.|
   117  219.87  :-:.|=...|.-:.|=: .|
   118  221.74  #:  |%- .|@:-.|+=..|
   119  223.62  #. .|@* :|*-  |#- .|
   120  225.49  #:  |@: .|%:=.|+-. |
   121  227.37  *.  |@+ :|*-  |#:  |
   122  229.24  #:  |@: .|%:-.|++. |
   123  231.12  #:  |@* :|*-  |%:  |
   124  232.99  #-  |@...|#:=.|++. |
   125  234.87  *:  |@: -|+=..|%.: |
   126  236.74  @.=:|@.:+|#.:.|%.::|
   127  238.62  #:::|@.:*|#.  |@.. |
```

```
$ cd "~/deadmau5 app"; KIT=tools/showkit; W=$KIT/work/fnpig; export KIT; python3 $W/fold2.py strip 204 238 lowmid,mid,pres,air; python3 $W/fold2.py strip 264 284 lowmid,mid,pres,air;  python3 $W/fold2.py strip 160 178 lowmid,mid,pres,air; python3 $W/fold2.py fold 126 166 2; python3 $W/fold2.py fold 178 204 2;python3 $W/fold2.py fold 238 264 2; 
bars 204-238 per-bar onset strip (lowmid+mid+pres+air)
   204  382.99  -.+.|%.==|- -.|@.= |
   205  384.87  - + |%.. |: . | .  |
   206  386.74    . |    |    |    |
   207  388.62      |    |    |%   |
   208  390.49    % |    |+ * |    |
   209  392.37      |    |  *:|+ : |
   210  394.24  - + |    |+ * |    |
   211  396.12      |    |%   |*   |
   212  397.99    % |    |+ * |    |
   213  399.87  .   |    |  *:|+ : |
   214  401.74  - + |    |+ * |  . |
   215  403.62      |    |    |#   |
   216  405.49    % |    |+ * |    |
   217  407.37  . . |    |  +:|+ : |
   218  409.24  : + |    |= * |    |
   219  411.12      |.   |*   |+   |
   220  412.99  . * |    |- = |    |
   221  414.87  .   |.   |. :.|- : |
   222  416.74  . : |    |. : |    |
   223  418.62      |    |    |.   |
   224  420.49    . |    |. . |    |
   225  422.37      |    |  . |. . |
   226  424.24    . |    |. . |.   |
   227  426.12      |    |.   |.   |
   228  427.99    . |    |    |   .|
   229  429.87      |   .|.   |.   |
   230  431.74  ..  |..  |    |.   |
   231  433.62    ..|....|. . |:.  |
   232  435.49  ... |... |.. .|..  |
   233  437.37  . ..|.   |:   |-.:.|
   234  439.24  - - |#.-#|- +.|*.+.|
   235  441.12  - * |@=+@|- *-|@ +.|
   236  442.99  # #.|@.=@|- *.|*.* |
   237  444.87  - * |@=*@|: #+|* = |
bars 264-284 per-bar onset strip (lowmid+mid+pres+air)
   264  495.49  - - |+ :-|: - |= : |
   265  497.37  : - |+.. |: . |: . |
   266  499.24  -   |+  +|: - |- : |
   267  501.12  -   |*  *|.   |% : |
   268  502.99  *   |@  #|: + |- - |
   269  504.87  -   |*  #|:   |@ : |
   270  506.74  *   |@  #|:.*.|- - |
   271  508.62  -   |*  #|.   |@ : |
   272  510.49  *   |@  #|: *.|: - |
   273  512.37  -   |*  =|.   |=   |
   274  514.24  -   |=   |+   |%   |
   275  516.12  *   |*   
... [cut] ...
     . * |@.-@|: +.|@.=.||= #.|@:-*|... |..=:|| peak 1.16
   pres    - * |@.-%|- +:|@.=:||+ # |%:=*|= . |: =.|| peak 1.23
   air     . %:|@:%#|=.@-|@:@.||+ @-|@-%*|= :.|..#.|| peak 0.85
bars 238-264, fold over 2 bars
   sub     @: -|@. :|@. .|#.:.||@. -|@ .:|%.  |@.. || peak 0.92
   bass    %.- |@.:+|*.=.|*. .||% :.|%.:-|+:. |% . || peak 1.25
   lowmid  +.= |% .=|=.-.|- . ||+ - |@..=|- : |# . || peak 1.38
   mid     # * |@.-%|: +.|+.+.||- + |%:-+|. =.|+.=:|| peak 1.23
   pres    # * |@.-%|- +.|* +.||= + |#:=*|- =-|#.= || peak 1.34
   air     % #.|@:+%|- *:|#:* ||- #.|#-**|- *:|*.*.|| peak 1.01
```

```
$ cd "~/deadmau5 app"; grep -n '"tiki"' -A 22 mau5fx.py | head -60; sed -n 245,290p mau5fx.py; cat > /tmp/null 2>/dev/null; python3 - <<'EOF'
import sys
sys.path.insert(0,'.')
import numpy as np, mau5engine as E
h=E.Helmet()
s=h.shell
# check axes on the shell: nfa nel vs px py, er, ea, u
for nm in ("nfa","nel","er","ea","along","u"):
    v=getattr(h,nm)
    print(nm,"shell range",float(v[s].min()),float(v[s].max()),"ears range",float(v[h.ears].min()),float(v[h.ears].max()))
j=s&(h.py<=28)
print("jaw count",j.sum(),"face count",(s&(h.py>28)).sum())
order=np.argsort(h.u[j])
idx=np.where(j)[0][order]
print("jaw LEDs by u: (u, px, py, nfa, nel)")
for i in idx[::6]:
    print("%.3f %7.1 ... [cut]
Command did not complete within its 120s timeout and was moved to the background (ID: bm01wft2b). Output is being written to: /private/tmp/claude-501/-Users-jones-deadmau5-app/208332e7-8c9f-4c25-bc21-e9a9df98fa1f/tasks/bm01wft2b.output. If it exits while you are still working you will be notified, but it is terminated when you give your final response and no notification can follow that — so do not end your turn to wait for it; if you need its result, wait for it before giving your final response. To check interim output, use Read on that file path.
Session cwd remains ~/deadmau5 app; directory changes made by the backgrounded command do not apply to subsequent commands.
```

```
$ cd "~/deadmau5 app"; grep -n '"tiki"' -A 22 mau5fx.py | head -60; sed -n 245,290p mau5fx.py; python3 - <<'EOF'
import sys
sys.path.insert(0,'.')
import numpy as np, mau5engine as E
h=E.Helmet()
s=h.shell
# check axes on the shell: nfa nel vs px py, er, ea, u
for nm in ("nfa","nel","er","ea","along","u"):
    v=getattr(h,nm)
    print(nm,"shell range",float(v[s].min()),float(v[s].max()),"ears range",float(v[h.ears].min()),float(v[h.ears].max()))
j=s&(h.py<=28)
print("jaw count",j.sum(),"face count",(s&(h.py>28)).sum())
order=np.argsort(h.u[j])
idx=np.where(j)[0][order]
print("jaw LEDs by u: (u, px, py, nfa, nel)")
for i in idx[::6]:
    print("%.3f %7.1f %7.1f %.3f %.3f"%(h.u[i],h. ... [cut]
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
    ],
}


# Sprites a song brings with it: shows/scenes/<song>.sprites.json, {name: [rows]},
# named after the song so two songs cannot collide.  A sheet that does not parse
# is said and skipped, so one song being edited cannot stop the others compiling;
# a scene asking for a sprite that went with it is refused by mau5scene's lint.
def _song_sprites():
    d = os.path.join(os.path.dirname(os.path.abspath(__file__)), "shows", "scenes")
    try:
        sheets = sorted(f for f in os.listdir(d) if f.endswith(".sprites.json"))
    except OSError:
        return
    for fn in sheets:
        try:
            with open(os.path.join(d, fn)) as f:
                sheet = json.load(f)
            for name, rows in sheet.items():
                if not rows or len({len(r) for r in rows}) != 1:
                    raise ValueError("sprite %s needs rows of one length" % name)
                SPRITES[name] = list(rows)
        except (OSError, ValueError) as e:
            print("  %s: %s" % (fn, e))


_song_sprites()


def sprite_bitmap(name_or_rows):
    rows = SPRITES[name_or_rows] i
... [cut] ...
t 96 face count 302
jaw LEDs by u: (u, px, py, nfa, nel)
0.000  -168.8   -37.2 0.163 0.238
0.000   -53.5  -111.2 0.369 0.000
0.000    64.5  -111.2 0.656 0.000
0.000   138.7   -68.9 0.795 0.143
0.000  -124.9   -83.8 0.227 0.095
0.000  -145.2   -68.9 0.195 0.143
0.200   138.8   -98.0 0.795 0.048
0.333   130.5   -98.0 0.782 0.048
0.400   147.3   -83.8 0.808 0.095
0.500  -157.2   -68.9 0.178 0.143
0.600  -151.2   -83.8 0.187 0.095
0.667  -130.5   -98.0 0.218 0.048
0.800   160.2   -53.3 0.826 0.191
1.000  -121.2  -111.3 0.233 0.000
1.000   100.9   -97.9 0.731 0.048
1.000  -116.5   -83.8 0.241 0.096
```

```
$ cd "~/deadmau5 app"; grep -n '"tiki"' -A 22 mau5fx.py | head -60; sed -n 245,290p mau5fx.py; python3 - <<'EOF'
import sys
sys.path.insert(0,'.')
import numpy as np, mau5engine as E
h=E.Helmet()
s=h.shell
# check axes on the shell: nfa nel vs px py, er, ea, u
for nm in ("nfa","nel","er","ea","along","u"):
    v=getattr(h,nm)
    print(nm,"shell range",float(v[s].min()),float(v[s].max()),"ears range",float(v[h.ears].min()),float(v[h.ears].max()))
j=s&(h.py<=28)
print("jaw count",j.sum(),"face count",(s&(h.py>28)).sum())
order=np.argsort(h.u[j])
idx=np.where(j)[0][order]
print("jaw LEDs by u: (u, px, py, nfa, nel)")
for i in idx[::6]:
    print("%.3f %7.1f %7.1f %.3f %.3f"%(h.u[i],h. ... [cut]
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
    ],
}


# Sprites a song brings with it: shows/scenes/<song>.sprites.json, {name: [rows]},
# named after the song so two songs cannot collide.  A sheet that does not parse
# is said and skipped, so one song being edited cannot stop the others compiling;
# a scene asking for a sprite that went with it is refused by mau5scene's lint.
def _song_sprites():
    d = os.path.join(os.path.dirname(os.path.abspath(__file__)), "shows", "scenes")
    try:
        sheets = sorted(f for f in os.listdir(d) if f.endswith(".sprites.json"))
    except OSError:
        return
    for fn in sheets:
        try:
            with open(os.path.join(d, fn)) as f:
                sheet = json.load(f)
            for name, rows in sheet.items():
                if not rows or len({len(r) for r in rows}) != 1:
                    raise ValueError("sprite %s needs rows of one length" % name)
                SPRITES[name] = list(rows)
        except (OSError, ValueError) as e:
            print("  %s: %s" % (fn, e))


_song_sprites()


def sprite_bitmap(name_or_rows):
    rows = SPRITES[name_or_rows] i
... [cut] ...
t 96 face count 302
jaw LEDs by u: (u, px, py, nfa, nel)
0.000  -168.8   -37.2 0.163 0.238
0.000   -53.5  -111.2 0.369 0.000
0.000    64.5  -111.2 0.656 0.000
0.000   138.7   -68.9 0.795 0.143
0.000  -124.9   -83.8 0.227 0.095
0.000  -145.2   -68.9 0.195 0.143
0.200   138.8   -98.0 0.795 0.048
0.333   130.5   -98.0 0.782 0.048
0.400   147.3   -83.8 0.808 0.095
0.500  -157.2   -68.9 0.178 0.143
0.600  -151.2   -83.8 0.187 0.095
0.667  -130.5   -98.0 0.218 0.048
0.800   160.2   -53.3 0.826 0.191
1.000  -121.2  -111.3 0.233 0.000
1.000   100.9   -97.9 0.731 0.048
1.000  -116.5   -83.8 0.241 0.096
```

```
$ cd "~/deadmau5 app"; KIT=tools/showkit; W=$KIT/work/fnpig; date; rm -f /tmp/null; cat > $W/ledmap2.py <<'EOF'
import sys
sys.path.insert(0,'.')
import numpy as np, mau5engine as E
h=E.Helmet()
s=h.shell
# rows on the shell
ys=np.round(h.py[s]/3)*3
vals,c=np.unique(np.round(h.py[s]),return_counts=True)
# cluster rows
pts=sorted(zip(h.py[s],h.px[s]))
rows=[]
cur=[pts[0]]
for p in pts[1:]:
    if abs(p[0]-cur[-1][0])<3.0: cur.append(p)
    else:
        rows.append(cur);cur=[p]
rows.append(cur)
for r in rows[::-1]:
    xs=sorted(x for _,x in r)
    print("y %7.1f n %3d x %7.1f .. %7.1f gaps>30: %s ... [cut]
Sat Oct 31 12:47:05 PDT 2026
y   167.8 n   1 x     5.9 ..     5.9 gaps>30: []
y   162.9 n   3 x   -56.7 ..     8.1 gaps>30: [(-57, -13)]
y   156.6 n  17 x   -73.6 ..    73.0 gaps>30: []
y   148.7 n  17 x   -88.3 ..    87.6 gaps>30: []
y   139.6 n  34 x  -102.2 ..   102.2 gaps>30: []
y   129.1 n  30 x  -115.1 ..   115.1 gaps>30: []
y   117.4 n  30 x  -127.0 ..   127.0 gaps>30: []
y   104.6 n  34 x  -137.7 ..   137.7 gaps>30: []
y    90.9 n  34 x  -147.1 ..   147.1 gaps>30: []
y    76.3 n  34 x  -155.1 ..   155.1 gaps>30: []
y    61.0 n  34 x  -161.8 ..   161.8 gaps>30: []
y    45.2 n  22 x  -166.9 ..   166.9 gaps>30: [(-94, 94)]
y    28.9 n  12 x  -170.4 ..   170.4 gaps>30: [(-149, 149)]
y    12.3 n   2 x  -170.9 ..   170.9 gaps>30: [(-171, 171)]
y   -20.8 n   2 x  -170.1 ..   170.1 gaps>30: [(-170, 170)]
y   -37.2 n   6 x  -168.8 ..   168.8 gaps>30: [(-164, 164)]
y   -53.3 n   8 x  -164.5 ..   164.5 gaps>30: [(-156, 156)]
y   -68.9 n  12 x  -158.6 ..   158.6 gaps>30: [(-139, 139)]
y   -83.8 n  16 x  -151.2 ..   151.2 gaps>30: [(-116, 116)]
y   -98.0 n  20 x  -142.5 ..   142.5 gaps>30: [(-91, 91)]
y  -111.2 n  30 x  -132.4 ..   132.4 gaps>30: [(-30, 30)]
```

```
$ cd "~/deadmau5 app"; KIT=tools/showkit; W=$KIT/work/fnpig; date; rm -f /tmp/null; cat > $W/ledmap2.py <<'EOF'
import sys
sys.path.insert(0,'.')
import numpy as np, mau5engine as E
h=E.Helmet()
s=h.shell
# rows on the shell
ys=np.round(h.py[s]/3)*3
vals,c=np.unique(np.round(h.py[s]),return_counts=True)
# cluster rows
pts=sorted(zip(h.py[s],h.px[s]))
rows=[]
cur=[pts[0]]
for p in pts[1:]:
    if abs(p[0]-cur[-1][0])<3.0: cur.append(p)
    else:
        rows.append(cur);cur=[p]
rows.append(cur)
for r in rows[::-1]:
    xs=sorted(x for _,x in r)
    print("y %7.1f n %3d x %7.1f .. %7.1f gaps>30: %s ... [cut]
Sat Oct 31 12:47:05 PDT 2026
y   167.8 n   1 x     5.9 ..     5.9 gaps>30: []
y   162.9 n   3 x   -56.7 ..     8.1 gaps>30: [(-57, -13)]
y   156.6 n  17 x   -73.6 ..    73.0 gaps>30: []
y   148.7 n  17 x   -88.3 ..    87.6 gaps>30: []
y   139.6 n  34 x  -102.2 ..   102.2 gaps>30: []
y   129.1 n  30 x  -115.1 ..   115.1 gaps>30: []
y   117.4 n  30 x  -127.0 ..   127.0 gaps>30: []
y   104.6 n  34 x  -137.7 ..   137.7 gaps>30: []
y    90.9 n  34 x  -147.1 ..   147.1 gaps>30: []
y    76.3 n  34 x  -155.1 ..   155.1 gaps>30: []
y    61.0 n  34 x  -161.8 ..   161.8 gaps>30: []
y    45.2 n  22 x  -166.9 ..   166.9 gaps>30: [(-94, 94)]
y    28.9 n  12 x  -170.4 ..   170.4 gaps>30: [(-149, 149)]
y    12.3 n   2 x  -170.9 ..   170.9 gaps>30: [(-171, 171)]
y   -20.8 n   2 x  -170.1 ..   170.1 gaps>30: [(-170, 170)]
y   -37.2 n   6 x  -168.8 ..   168.8 gaps>30: [(-164, 164)]
y   -53.3 n   8 x  -164.5 ..   164.5 gaps>30: [(-156, 156)]
y   -68.9 n  12 x  -158.6 ..   158.6 gaps>30: [(-139, 139)]
y   -83.8 n  16 x  -151.2 ..   151.2 gaps>30: [(-116, 116)]
y   -98.0 n  20 x  -142.5 ..   142.5 gaps>30: [(-91, 91)]
y  -111.2 n  30 x  -132.4 ..   132.4 gaps>30: [(-30, 30)]
```

```
$ cd "~/deadmau5 app"; grep -n "sprite\|function paint\|paint(" remote/offline/*.js | head -30; grep -n "class SpriteShow\|SpriteShow" -n remote/offline/*.js | head; sed -n "$(grep -n 'function paint' remote/offline/engine.js | head -1 | cut -d: -f1),+50p" remote/offline/engine.js
remote/offline/engine.js:168:function spriteBitmap(fonts, name) {
remote/offline/engine.js:169:  const rows = fonts.sprites[name];
remote/offline/engine.js:181:function paint(bm, rowf, colf, mask, n, wrap, reach, rowW) {
remote/offline/engine.js:450:    const lit = paint(bm, ry, rx, mask, h.n, this.p.loop ? bm.cols : 0);
remote/offline/engine.js:458:def('sprite', { sprite: 'smile', color: [0, 255, 255], bg: [0, 0, 0],
remote/offline/engine.js:463:    const names = String(this.p.sprite).split('|');
remote/offline/engine.js:465:    const bm = spriteBitmap(this.fonts, names[at]);
remote/offline/engine.js:482:    const lit = paint(bm, ry, rx, mask, h.n, 0);
remote/offline/engine.js:724:    const lit = paint(bm, ry, rx, mask, h.n, 0);
remote/offline/engine.js:968:              textBitmap, glyphBitmap, digitBitmap, spriteBitmap, fract, pmod,
remote/offline/show.js:280:const SCENE_PRESETS = { text: 1, sprite: 1, eyes: 1 };
remote/offline/ui.js:381:// use -- a sprite this build does not have, an axis it does not know,
remote/offline/engine.js:457:// mau5engine.SpriteShow says what dx, dy, vx, vy, wx, wy, wf and rate do.
function paint(bm, rowf, colf, mask, n, wrap, reach, rowW) {
  reach = reach === undefined ? 1.4 : reach;
  rowW = rowW === undefined ? 1.0 : rowW;
  const rows = bm.rows, cols = bm.cols;
  const lit = new Uint8Array(n);
  const idx = [];
  for (let i = 0; i < n; i++) {
    if (!mask[i]) continue;
    if (!(rowf[i] >= 0 && rowf[i] < rows)) continue;
    if (!wrap && !(colf[i] >= 0 && colf[i] < cols)) continue;
    idx.push(i);
  }
  if (!idx.length) return lit;

  const occupied = new Uint8Array(rows * cols);
  for (const i of idx) {
    const r = Math.floor(rowf[i]);
    const c = wrap ? pmod(Math.floor(colf[i]), cols) : Math.floor(colf[i]);
    lit[i] = bm.d[r
... [cut] ...
rn lit;
}

// ----------------------------------------------------------------------
// the library
// ----------------------------------------------------------------------
const REGISTRY = {};

// Every preset is {name, params, render(h, t, music, out)} where `out`
// is a Float32Array(n*3) the caller owns.  Writing into a buffer rather
// than allocating one keeps the phone from collecting garbage 25 times
// a second, which shows up as dropped frames and nothing else.
function def(name, params, render, init) {
  REGISTRY[name] = { name: name, params: params, render: render, init: init };
}
```

```
$ cd "~/deadmau5 app"; KIT=tools/showkit; W=$KIT/work/fnpig; sed -n 165,180p remote/offline/engine.js; sed -n 620,632p mau5engine.py; grep -n "SPRITES\|sprites" mau5offline.py | head; sed -n 458,490p remote/offline/engine.js; cat > $W/make_sprites.py <<'EOF'
#!/usr/bin/env python3
"""The pig, drawn LED by LED: every set cell holds a real LED, so nothing scatters and the phone does no search."""
import json, os, sys
sys.path.insert(0, os.getcwd())
import numpy as np, mau5engine as E
h = E.Helmet()
s = np.asarray(h.shell, bool)
PX, PY = np.asarray(h.px, float), np.asarray(h.py, float)
BASE = "deadm ... [cut]
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
    g = FONT5x7.get(ch.upper(), FONT5x7.get("?", (0, 0, 0, 0, 0)))
    return np.array([[(c >> r) & 1 for c in g] for r in range(7)], bool)


def _sprite_bitmap(name):
    rows = SPRITES[name]
    return np.array([[c != "." for c in r] for r in rows], bool)


def paint(bm, rowf, colf, mask, wrap=None, reach=1.4, row_w=1.0):
    """Draw a bitmap onto the LEDs, by gather and by scatter.

    The gather is the obvious half: every LED looks up the cell it
73:    from mau5fx import FONT5x7, SPRITES
96:            "sprites": {k: list(v) for k, v in SPRITES.items()},
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
    const hi = this.p.y_hi, lo = t
... [cut] ...
i * 3 + 2] = c[2];
    }
  });

// How far inside its edge an eye fades in, in mm: about one LED pitch.
const EYE_EDGE = 12.0;
wrote shows/scenes/deadmau5 - FN Pig.sprites.json 21 sprites 16204 bytes
tools/showkit/songs/fnpig/try1.png (1440, 338)
tools/showkit/songs/fnpig/try2.png (1440, 338)
tools/showkit/songs/fnpig/try3.png (360, 338)
```

```
$ cd "~/deadmau5 app"; KIT=tools/showkit; W=$KIT/work/fnpig; cat > $W/chords.py <<'EOF'
import sys, os
sys.path.insert(0, os.getcwd())
import numpy as np
m=np.load(os.environ["KIT"]+"/work/fnpig/mono.npy")
sr=22050; spb=.46875; t0=.49
N=8192
win=np.hanning(N)
f=np.fft.rfftfreq(N,1/sr)
NOTES="C C# D D# E F F# G G# A A# B".split()
# chroma per beat
mask=(f>55)&(f<1500)
pc=(np.round(12*np.log2(f[mask]/440.0))+69).astype(int)%12
lo,hi=int(sys.argv[1]),int(sys.argv[2])
res=int(sys.argv[3]) if len(sys.argv)>3 else 1   # slices per beat
rows=[]
ts=[]
for b in range(lo*4*res,hi*4*res):
    t=t0+b*spb/res ... [cut]
chord changes (bar, strength): 25(0.31)  27.25(0.33)  28.75(0.51)  36.75(0.35)  40.5(0.55)  42(0.37)  43.25(0.38)  45(0.50)  46.5(0.44)  49.25(0.29)  51.75(0.51)  53(0.30)  55.25(0.23)  56.5(0.37)  58.25(0.30)  60.75(0.39)  63.75(0.29)  64.75(0.36)
  22  E/B/A#     E/B/F      E/B/D      E/B/D    
  23  E/B/D      E/B/A#     E/B/F      E/B/D    
  24  E/B/D      E/B/D      E/D#/A#    E/B/A#   
  25  F#/E/A     F#/A/E     F#/A/E     F#/A/E   
  26  F#/E/A     F#/E/A     F#/E/A     F#/A/B   
  27  F#/A/G     G/F#/B     G/B/F#     G/B/F#   
  28  G/B/F#     G/B/F#     G/F#/B     A/C#/G#  
  29  A/G#/C#    B/C#/A     B/A#/C#    B/D/A#   
  30  B/D/A#     B/D/A#     B/D/A#     B/D/C    
  31  B/D/A#     D/B/C      D/A/B      D/A/B    
  32  D/A/C#     D/A/C#     D/A/C#     D/A/C#   
  33  D/A/E      D/E/A      E/G#/A     E/D#/D   
  34  E/G#/D#    E/D#/G#    E/D#/G#    E/D#/G#  
  35  E/D#/G#    E/G#/D#    E/G#/D#    E/G#/D#  
  36  E/G#/D#    E/G#/D#    E/F#/F     F#/F/C#  
  37  G/F#/B     G/F#/D     G/F#/D     G/D/F#   
  38  G/D/F#     G/D/F#     G/D/F#     D/F#/A   
  39  D/F#/C#    D/A/F#     D/F#/E     D/F#/C#  
  40  D/F#/A     D/F#/C#    E/B/F#     E/B/D    
  41  E/B/D#     E/B/D#     E/B/D#     E/B/F    
  42  G/B/F#     B/G/D      B/G/F#     B/G/F#   
  43  G/B/F#     A/C#/A#    B/D/A#     B/A#/D   
  44  B/D/C      B/A/F#     B/A#/C     B/C/A#   
  45  D/F#/A     D/F#/A     D/F#/A     D/F#/A   
  46  D/A/F#     D/A/F#     E/B/G#     E/G#/B   
  47  E/G#/B     E/B/G#     E/G#/B     E/B/G#   
  48  E/G#/B     E/B/G#     E/B/G#     E/B/F#   
  49  F#/C#/E    G/D/F#     D/G/F#     G/D/F#   
  50  G/D/B      G/D/F#     D/F#/A     D/F#/A   
  51  F#/D/A     D/F#/A     D/F#/A     B/E/D    
  52  E/B/D      E/B/D      E/B/F#     E/B/F#   
  53  B/G/D      B/D/G      B/G/F#     B/D/A    
  54  A/C#/E     B/D/C      B/D/F#     B/D/C    
  55  B/D/F#     D/A/B      D/A/B      D/A/E    
  56  D/A/E      D/A/E      E/B/A      E/B/G#   
  57  E/G#/B     E/G#/B     E/G#/B     E/G#/B   
  58  E/B/G#     F#/E/C#    F#/G/D     G/D/A    
  59  D/G/F#     G/D/F#     G/D/F#     D/F#/A   
  60  D/F#/A     D/F#/A     F#/D/A     E/F#/B   
  61  E/B/F#     E/B/F#     B/E/F#     B/F#/D   
  62  B/G/F#     B/F#/D     A/C#/B     B/D/C    
  63  B/D/F#     B/D/A      B/F#/D     D/F#/A   
  64  D/F#/A     D/F#/A     D/A/F#     E/A/F#   
  65  E/G#/B     E/G#/B     E/G#/B     E/G#/B
```

```
$ cd "~/deadmau5 app"; KIT=tools/showkit; W=$KIT/work/fnpig; export KIT; python3 $W/chords.py 22 95 4 | head -1;  python3 $W/chords.py 96 118 4 | head -1; python3 $W/chords.py 212 234 4 | head -1
chord changes (bar, strength): 24.9375(0.23)  27.1875(0.20)  28.8125(0.48)  31.375(0.22)  33.375(0.40)  36.625(0.51)  40.4375(0.50)  42.0625(0.38)  43.1875(0.41)  45.0625(0.47)  46.5(0.46)  48.875(0.36)  51.8125(0.46)  53.0625(0.26)  55.375(0.29)  56.5(0.34)  58.375(0.31)  60.6875(0.36)  63.6875(0.30)  64.6875(0.31)  66.8125(0.29)  72.1875(0.24)  92.0625(0.35)  93.625(0.28)
chord changes (bar, strength): 97.5625(0.35)  100.062(0.38)  101.625(0.36)  104.125(0.38)  105.625(0.32)  106.625(0.33)  107.75(0.34)  110.125(0.29)  117.25(0.39)
chord changes (bar, strength): 213.562(0.27)  216.062(0.45)  217.625(0.37)  220.625(0.30)  221.625(0.20)  224.625(0.26)  226.125(0.21)  233.25(0.25)
```

```
$ cd "~/deadmau5 app"; KIT=tools/showkit; W=$KIT/work/fnpig; python3 - <<'EOF'
import re
p="tools/showkit/songs/fnpig/make_sprites.py"
s=open(p).read()
s=s.replace('CY = 106.0; A = 146.0; B = 62.0\nFL = [(30, 34), (25, 29), (20, 23), (16, 17)]','CY = 108.0; A = 130.0; B = 53.0\nFL = [(29, 34), (24, 28), (19, 22), (14, 15)]')
s=s.replace('return ell(dx, cy + dy, a, b) & ~nostrils(dx, cy + dy - 2, nx, rx, ry, 0.18)','return ell(dx, cy + dy, a, b) & ~nostrils(dx, cy + dy - 4, nx, rx, ry, 0.0)')
s=s.replace('def sn ... [cut]
wrote shows/scenes/deadmau5 - FN Pig.sprites.json 21 sprites 16204 bytes
tools/showkit/songs/fnpig/try1.png (1440, 338)
tools/showkit/songs/fnpig/try2.png (1440, 338)
Sat Oct 31 12:52:24 PDT 2026
```

```
$ mkdir -p "tools/showkit/songs/fnpig"; cat > "tools/showkit/songs/fnpig/write_treatment.py" <<'EOF'
#!/usr/bin/env python3
"""FN PIG: the treatment. Run from the repo root."""
import sys
KIT = "tools/showkit"
sys.path.insert(0, KIT)
from fmt import save
BASE = "deadmau5 - FN Pig"
R16 = 8.533333    # a flip book frame every 16th at 128 BPM
KICK = "x..."     # every beat, at step 0.25
DOME = {"y_lo": 52.0, "y_hi": 172.0, "x_half": 172.0} ... [cut]
wrote shows/scenes/deadmau5 - FN Pig.scene.json scenes 35 hits 1
     258   484.24s  energy 0.75  bass 0.72 (punch 1.00)  mid 0.76  high 0.67
     259   486.12s  energy 0.71  bass 0.64 (punch 1.00)  mid 0.72  high 0.66
  done       bar 266
     265   497.37s  energy 0.70  bass 0.67 (punch 1.00)  mid 0.80  high 0.81
     266   499.24s  energy 0.54  bass 0.59 (punch 1.00)  mid 0.67  high 0.70
     267   501.12s  energy 0.44  bass 0.53 (punch 1.00)  mid 0.47  high 0.48
  doze       bar 274
     273   512.37s  energy 0.47  bass 0.49 (punch 1.00)  mid 0.49  high 0.66
     274   514.24s  energy 0.39  bass 0.42 (punch 1.00)  mid 0.36  high 0.60
     275   516.12s  energy 0.35  bass 0.42 (punch 1.00)  mid 0.24  high 0.34
  end        bar 282
     281   527.37s  energy 0.33  bass 0.36 (punch 1.00)  mid 0.42  high 0.54
     282   529.24s  energy 0.00  bass 0.00 (punch 0.34)  mid 0.00  high 0.02
     283   531.12s  energy 0.00  bass 0.00 (punch 0.00)  mid 0.00  high 0.00
deadmau5 - FN Pig: 36 scenes, 1 hits, written into shows/deadmau5 - FN Pig.json
Sat Oct 31 12:53:48 PDT 2026
```

```
$ cd "~/deadmau5 app"; KIT=tools/showkit; W=$KIT/work/fnpig; time python3 $KIT/sheet.py "deadmau5 - FN Pig" $W/a1.png 1:asleep 1.5 3 15:dream 30:stir 38 50:rouse 58 66:lights 70 76:wash 82 89:title 90 91.6:pick 92.125:stab 92.5:stab 94.2 100.5:hazard 104 110:waking 114 117:wake3 118:beat 118.25 118.5 2>&1 | cut -c1-110
bar 1       asleep         shell max   0 mean   0.0   ears max   0 mean   0.0   asleep
bar 1.5                    shell max   0 mean   0.0   ears max   0 mean   0.0   asleep
bar 3                      shell max   0 mean   0.0   ears max   0 mean   0.0   asleep
bar 15      dream          shell max  75 mean   1.0   ears max   0 mean   0.0   dream
bar 30      stir           shell max  99 mean   4.2   ears max   0 mean   0.0   stir
bar 38                     shell max 105 mean   6.0   ears max   0 mean   0.0   stir
bar 50      rouse          shell max 151 mean  11.3   ears max  39 mean   2.5   rouse
bar 58                     shell max 173 mean  26.6   ears max  38 mean   2.5   rouse
bar 66      lights         shell max 201 mean  33.7   ears max  51 mean   3.3   lights
bar 70                     shell max 172 mean  28.5   ears max  43 mean   2.8   lights
bar 76      wash           shell max 139 mean  25.0   ears max  27 mean   1.7   wash
bar 82                     shell max 104 mean  19.4   ears max  21 mean   1.3   wash
bar 89      title          shell max 197 mean  19.6   ears max   0 mean   0.0   hold breath · FN PIG
bar 90                     shell max 197 mean  27.3   ears max   0 mean   0.0   hold breath · FN PIG
bar 91.6    pick           shell max  75 mean   2.4   ears max   0 mean   0.0   snort
bar 92.125  stab           shell max 237 mean   6.2   ears max   0 mean   0.0   snorts
bar 92.5    stab           shell max 255 mean   6.5   ears max   0 mean   0.0   snorts
bar 94.2                   shell max 133 mean   4.6   ears max  24 mean   2.3   snorts
bar 100.5   hazard         shell max 209 mean   7.7   ears max   0 mean   0.0   hazard
bar 104                    shell max  60 mean   7.7   ears max   0 mean   0.0   hazard
bar 110     waking         shell max  99 mea
... [cut] ...
 140 mean  25.1   ears max   0 mean   0.0   wake3
bar 118     beat           shell max 148 mean  13.1   ears max   1 mean   0.0   pacing
bar 118.25                 shell max 148 mean  13.4   ears max   4 mean   0.0   pacing
bar 118.5                  shell max 148 mean  13.5   ears max   2 mean   0.0   pacing
tools/showkit/songs/fnp
python3 $KIT/sheet.py "deadmau5 - FN Pig" $W/a1.png 1:asleep 1.5 3 15:dream    0.34s user 0.04s system 93% cpu 0.402 total
cut -c1-110  0.00s user 0.00s system 0% cpu 0.402 total
```

```
$ cd "~/deadmau5 app"; KIT=tools/showkit; W=$KIT/work/fnpig; python3 - <<'EOF'
import numpy as np
z=np.load("shows/deadmau5 - FN Pig.analysis.npz",allow_pickle=True)
fps=float(z["fps"])
b=z["b_bass_e"];p=z["b_bass_p"];m=z["b_mid_e"];h=z["b_high_e"]
def seg(a,c,v):
    x=v[int(a*fps):int(c*fps)]
    return "min %.2f p10 %.2f med %.2f p90 %.2f max %.2f"%(x.min(),np.percentile(x,10),np.median(x),np.percentile(x,90),x.max())
for a,c in ((0,5),(5,12),(12,25),(25,47),(47,60),(60,85),(85,120),(120,135),(135,165),(165,172)):
    print("%3d-%3d bass %s | high %s | mid %s"%(a,c,seg(a,c,b),seg(a,c,h),seg(a, ... [cut]
  0-  5 bass min 0.00 p10 0.16 med 0.29 p90 0.45 max 0.83 | high min 0.00 p10 0.00 med 0.00 p90 0.00 max 0.05 | mid min 0.00 p10 0.00 med 0.00 p90 0.00 max 0.15
  5- 12 bass min 0.00 p10 0.27 med 0.44 p90 0.59 max 0.80 | high min 0.00 p10 0.00 med 0.00 p90 0.00 max 0.03 | mid min 0.00 p10 0.00 med 0.00 p90 0.03 max 0.09
 12- 25 bass min 0.02 p10 0.20 med 0.34 p90 0.63 max 0.86 | high min 0.00 p10 0.00 med 0.00 p90 0.01 max 0.02 | mid min 0.00 p10 0.03 med 0.07 p90 0.14 max 0.30
 25- 47 bass min 0.00 p10 0.25 med 0.46 p90 0.73 max 0.88 | high min 0.00 p10 0.00 med 0.00 p90 0.01 max 0.05 | mid min 0.00 p10 0.03 med 0.09 p90 0.21 max 0.60
 47- 60 bass min 0.00 p10 0.34 med 0.53 p90 0.75 max 0.89 | high min 0.00 p10 0.00 med 0.01 p90 0.05 max 0.17 | mid min 0.00 p10 0.10 med 0.15 p90 0.45 max 0.77
 60- 85 bass min 0.36 p10 0.58 med 0.73 p90 0.86 max 0.96 | high min 0.01 p10 0.02 med 0.05 p90 0.25 max 0.61 | mid min 0.05 p10 0.11 med 0.24 p90 0.65 max 0.86
 85-120 bass min 0.32 p10 0.59 med 0.72 p90 0.83 max 0.99 | high min 0.07 p10 0.12 med 0.36 p90 0.73 max 0.86 | mid min 0.23 p10 0.36 med 0.70 p90 0.84 max 0.93
120-135 bass min 0.13 p10 0.53 med 0.66 p90 0.76 max 0.86 | high min 0.67 p10 0.75 med 0.81 p90 0.85 max 0.92 | mid min 0.70 p10 0.80 med 0.85 p90 0.89 max 0.96
135-165 bass min 0.02 p10 0.23 med 0.55 p90 0.66 max 0.75 | high min 0.52 p10 0.65 med 0.75 p90 0.81 max 0.87 | mid min 0.66 p10 0.74 med 0.79 p90 0.84 max 0.92
165-172 bass min 0.00 p10 0.00 med 0.10 p90 0.22 max 0.36 | high min 0.38 p10 0.43 med 0.53 p90 0.61 max 0.67 | mid min 0.52 p10 0.61 med 0.71 p90 0.78 max 0.83
first 8 s bass at 10 Hz: 0.00 0.67 0.35 0.24 0.26 0.32 0.32 0.26 0.26 0.28 0.31 0.59 0.37 0.31 0.23 0.32 0.33 0.34 0.38 0.37 0.43 0.56 0.38 0.29 0.27 0.15 0.15 0.20 0.21 0.26 0.30 0.49 0.22 0.15 0.18 0.32 0.24 0.27 0.16 0.20 0.83 0.46 0.12 0.30 0.20 0.15 0.27 0.29 0.22 0.28 0.63 0.42 0.36 0.17 0.19 0.29 0.32 0.33 0.34 0.72 0.48 0.29 0.14 0.22 0.22 0.36 0.38 0.31 0.29 0.60 0.40 0.42 0.49 0.42 0.44 0.37 0.37 0.36 0.57 0.44
```

```
$ cd "~/deadmau5 app"; KIT=tools/showkit; W=$KIT/work/fnpig; python3 $KIT/sheet.py "deadmau5 - FN Pig" $W/a2.png 126.01:drop 126.07 126.13 126.25:gapkick 127.1:clap 136.05 145.05 153.05 160.05 168.1:pace2 174.01:neon 174.07 174.15 185.05 200.05 206.1:hush 208.13:stab 208.5:stab 217:rebuild 225 230 233 234.01:fury 234.07 234.15 245.05 260.05 266.05:tire 270.05 275.01:doze 280.01 281.5 2>&1 | cut -c1-100
bar 126.01  drop           shell max  90 mean  16.5   ears max  34 mean   3.2   raw
bar 126.07                 shell max  90 mean  15.9   ears max  35 mean   4.2   raw
bar 126.13                 shell max  90 mean  14.8   ears max  35 mean   2.5   raw
bar 126.25  gapkick        shell max  89 mean  19.2   ears max   4 mean   0.0   raw
bar 127.1   clap           shell max  90 mean  14.8   ears max  35 mean   4.2   raw
bar 136.05                 shell max 115 mean  15.9   ears max  23 mean   2.2   raw2
bar 145.05                 shell max  90 mean  18.3   ears max  23 mean   2.2   raw3
bar 153.05                 shell max 115 mean  19.8   ears max  23 mean   2.2   raw4
bar 160.05                 shell max 128 mean  22.8   ears max  23 mean   2.2   raw5
bar 168.1   pace2          shell max 115 mean  13.4   ears max  25 mean   3.0   pacing2
bar 174.01  neon           shell max 128 mean  25.2   ears max  73 mean  11.2   neon
bar 174.07                 shell max 128 mean  24.7   ears max  66 mean  11.8   neon
bar 174.15                 shell max 128 mean  21.6   ears max  49 mean   9.0   neon
bar 185.05                 shell max 128 mean  24.4   ears max  82 mean  10.7   neon2
bar 200.05                 shell max 128 mean  28.1   ears max  79 mean  10.3   neon4
bar 206.1   hush           shell max  57 mean   9.1   ears max   0 mean   0.0   hush
bar 208.13  stab           shell max 161 mean  20.4   ears max  89 mean   5.8   snorts2
bar 208.5   stab           shell max 147 mean  20.5   ears max   0 mean   0.0   snorts2
bar 217     rebuild        shell max  59 mean   7.2   ears max   0 mean   0.0   rebuild
bar 225                    shell max 128 mean  15.0   ears max   0 mean   0.0   rebuild2
bar 230                    shell max 128 mean  21.0   ears max   0 mean   0.0   rebuild
... [cut] ...
     shell max 255 mean  45.0   ears max 103 mean  13.2   squeal
bar 266.05  tire           shell max  80 mean  17.8   ears max 101 mean   9.6   tiring
bar 270.05                 shell max  49 mean  12.0   ears max  67 mean   6.4   tiring
bar 275.01  doze           shell max 117 mean   2.5   ears max   0 mean   0.0   dozing
bar 280.01                 shell max  73 mean   1.6   ears max   0 mean   0.0   dozing
bar 281.5                  shell max  59 mean   1.3   ears max   0 mean   0.0   dozing
(scratch)/ki
```

```
$ cd "~/deadmau5 app"; KIT=tools/showkit; W=$KIT/work/fnpig; time python3 mau5scene.py check "deadmau5 - FN Pig" 2>&1 | tail -45 | cut -c1-90; date
deadmau5 - FN Pig: 13286 frames at 25 fps through the guard
  scene            from  mean mA   p95 mA     heat   allow W      ms
  asleep           0.0s        5       17     0.0%      18.1    0.04
  dream           11.8s       14       30     0.0%      18.1    0.08
  stir            47.3s      144      300     0.0%      18.1    0.15
  rouse           84.9s      319      358     0.4%      18.1    0.13
  lights         120.5s      341      357     0.6%      18.1    0.12
  wash           135.5s      318      330     0.9%      18.1    0.12
  hold breath    164.6s      194      300     0.9%      18.1    0.13
  snort          172.1s       36       90     0.6%      18.1    0.05
  snorts         173.0s       73      210     0.5%      18.1    0.07
  hazard         188.0s      259      397     0.1%      18.1    0.10
  waking         203.0s      392      512     0.7%      18.1    0.15
  wake3          218.0s      435      578     0.9%      18.1    0.15
  pacing         221.8s      250      423     0.9%      18.1    0.14
  raw            236.8s      335      514     0.8%      18.1    0.19
  raw2           251.8s      325      514     1.0%      18.1    0.19
  raw3           266.8s      337      514     1.3%      18.1    0.19
  raw4           281.8s      337      514     1.5%      18.1    0.19
  raw5           296.8s      337      514     1.7%      18.1    0.19
  pacing2        311.8s      305      495     1.8%      18.1    0.14
  neon           326.8s      428      675     2.6%      18.1    0.19
  neon2          341.8s      428      670     3.4%      18.1    0.19
  neon3          356.8s      429      669     4.2%      18.1    0.19
  neon4          371.8s      427      670     5.0%      18.1    0.19
  hush           386.8s      128      216     5.0%      18.1    0.10
  snort2       
... [cut] ...
784     8.1%      18.1    0.28
  squeal         484.2s      464      755     9.1%      18.1    0.28
  tiring         499.2s      306      445     9.3%      18.1    0.13
  dozing         514.2s       19       41     9.1%      18.1    0.07
  dark           529.2s        0        0     7.5%      18.1    0.01
  worst frame 1.74 ms; no scene reaches the sustained floor
python3 mau5scene.py check "deadmau5 - FN Pig" 2>&1  3.09s user 0.05s system 99% cpu 3.164 total
tail -45  0.00s user 0.00s system 0% cpu 3.163 total
cut -c1-90  0.00s user 0.00s system 0% cpu 3.158 total
Sat Oct 31 12:56:06 PDT 2026
```

```
$ cat > "tools/showkit/songs/fnpig/make_sprites.py" <<'EOF'
#!/usr/bin/env python3
"""The pig, drawn LED by LED: every set cell holds a real LED, so nothing scatters and the phone does no search."""
import json, math, os, sys
sys.path.insert(0, os.getcwd())
import numpy as np, mau5engine as E
h = E.Helmet()
s = np.asarray(h.shell, bool)
PX, PY = np.asarray(h.px, float), np.asarray(h.py, float)
BASE = "deadmau5 - FN Pig"
DOME = dict(y_lo=52.0, y_hi=172.0, x_half=172.0, rows=15, cols=43)
FULL = dict(y_lo=-116.0, y_hi=172.0, x_half=172.0, rows=36, cols=43)

def to_rows(lit, F):
    rows, cols = F["rows"], F["co ... [cut]
wrote shows/scenes/deadmau5 - FN Pig.sprites.json 60 sprites 44475 bytes
bars 128-160 per-bar onset strip (lowmid+mid+pres+air)
   128  240.49  : + |@ -#|: - |% - |
   129  242.37  - * |% -#|. =-|= - |
   130  244.24  : + |@ -%|: - |% - |
   131  246.12  - # |% -#|. : |# - |
   132  247.99  : + |@ -#|: - |% = |
   133  249.87  - # |% . |. . |- . |
   134  251.74  : : |= :+|: = |=.- |
   135  253.62  - = |%--*|. = |% - |
   136  255.49  : + |@ -%|: =.|= - |
   137  257.37  - = |%--*|. =-|= - |
   138  259.24  : + |% -%|. =.|= - |
   139  261.12  - = |#-=*|: + |% - |
   140  262.99  : + |% -%|. =.|=.- |
   141  264.87  - = |%.. |. . |: - |
   142  266.74  : + |@ -#|. = |=.- |
   143  268.62  - = |%-=+|. =.|% - |
   144  270.49  : + |@ -#|: = |= = |
   145  272.37  : = |%-=+|. +:|= - |
   146  274.24  : + |@ -%|. =.|= = |
   147  276.12  - = |#-=+|. =.|% = |
   148  277.99  : + |@ -#|: = |=.= |
   149  279.87  : = |%.:.|. . |- . |
   150  281.74  : : |+ :*|: =.|- = |
   151  283.62  - = |%--+|. . |. - |
   152  285.49  : + |@.-%|: +.|= - |
   153  287.37  - = |%-=+|. . |: - |
   154  289.24  : + |@ -#|. + |+ = |
   155  291.12  - = |#-=+|. . |. - |
   156  292.99  : + |@.-#|. = |= = |
   157  294.87  - + |# . |.   |: - |
   158  296.74  : = |@ -%|: + |=.= |
   159  298.62  - = |#-=*|. . |. -.|
Sat Oct 31 12:57:26 PDT 2026
```

```
$ cat > "tools/showkit/songs/fnpig/write_treatment.py" <<'EOF'
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
def book(ste ... [cut]
Traceback (most recent call last):
  File "tools/showkit/songs/fnpig/write_treatment.py", line 218, in <module>
    plate("pink@0.6", [0.3, 0.12], KG) + [flop("both", {"done": 1.0, "270": 2.0}, [0.45, 0.2], keep=0.1), belt({"done": 0.5, "270": 0.25}, [0.4, 0.1])]})
  File "tools/showkit/songs/fnpig/write_treatment.py", line 63, in plate
    return [sprite(colour, g, flare, rate, gate), sprite(colour, g * boost, low, rate, gate, mix="add")]
TypeError: can't multiply sequence by non-int of type 'float'
Sat Oct 31 12:59:27 PDT 2026
```

```
$ cd "~/deadmau5 app"; KIT=tools/showkit; W=$KIT/work/fnpig; python3 - <<'EOF'
p="tools/showkit/songs/fnpig/write_treatment.py"
s=open(p).read()
s=s.replace('''    return [sprite(colour, g, flare, rate, gate), sprite(colour, g * boost, low, rate, gate, mix="add")]''','''    g2 = [x * boost for x in g] if isinstance(g, list) else g * boost
    return [sprite(colour, g, flare, rate, gate), sprite(colour, g2, low, rate, gate, mix="add")]''')
open(p,"w").write(s)
EOF
python3 $W/write_treatment.py && python3 mau5sce ... [cut]
wrote shows/scenes/deadmau5 - FN Pig.scene.json scenes 35 hits 53
     283   531.12s  energy 0.00  bass 0.00 (punch 0.00)  mid 0.00  high 0.00
deadmau5 - FN Pig: 36 scenes, 53 hits, written into shows/deadmau5 - FN Pig.json
bar 1.02    asleep         shell max  45 mean   0.4   ears max   0 mean   0.0   asleep
bar 3.3                    shell max  56 mean   0.6   ears max   0 mean   0.0   asleep
bar 15.4    dream          shell max  83 mean   1.6   ears max   0 mean   0.0   dream
bar 40.1    stir           shell max 163 mean  10.1   ears max   0 mean   0.0   stir
bar 58      rouse          shell max 166 mean  26.5   ears max  39 mean   2.5   rouse
bar 66      lights         shell max 179 mean  33.1   ears max  51 mean   3.3   lights
bar 93.02   snort          shell max  96 mean   7.5   ears max   0 mean   0.0   snorts
bar 100.5   hazard         shell max 212 mean   8.7   ears max  52 mean   5.5   hazard
bar 110     waking         shell max  99 mean  12.1   ears max  11 mean   0.2   waking
bar 117.3                  shell max 140 mean  21.7   ears max 177 mean  15.8   wake3
bar 118.02  beat           shell max 183 mean  14.7   ears max 127 mean  30.3   pacing
bar 125.8   inhale         shell max 172 mean  17.5   ears max 204 mean  75.3   pacing · inhale 125
bar 126.03  DROP           shell max 120 mean  17.1   ears max 241 mean  97.0   raw · snort 126
bar 126.1                  shell max 172 mean  20.8   ears max 140 mean  63.9   raw · snort 126
bar 126.2                  shell max 182 mean  27.5   ears max 151 mean  60.1   raw · snort 126
bar 126.27                 shell max 207 mean  32.5   ears max 198 mean  69.5   raw · snort 126
bar 127.02                 shell max  89 mean  14.3   ears max 157 mean  43.2   raw
bar 136.1   root           shell max 107 mean  13.1   ea
... [cut] ...
 165 mean  21.3   fury3
bar 253.3                  shell max 255 mean  39.7   ears max 120 mean  12.0   fury3
bar 260.05  squeal         shell max 255 mean  41.5   ears max 118 mean  16.6   squeal
bar 265.7                  shell max 255 mean  44.6   ears max 255 mean 115.5   squeal · inhale 265
bar 266.1   tire           shell max  79 mean  16.2   ears max  69 mean  16.4   tiring
bar 275.03  doze           shell max 117 mean   2.4   ears max   0 mean   0.0   dozing
(scratch)/ki
Sat Oct 31 12:59:36 PDT 2026
```

```
$ cd "~/deadmau5 app"; KIT=tools/showkit; W=$KIT/work/fnpig; python3 - <<'EOF'
KIT="tools/showkit"
p=KIT+"/work/fnpig/make_sprites.py"
s=open(p).read()
s=s.replace('CY, A, B, NX, NY = 108.0, 116.0, 54.0, 43.0, 104.0\nFL = [(29, 34), (24, 27), (19, 21), (13, 14)]','CY, A, B, NX, NY = 108.0, 128.0, 56.0, 47.0, 106.0\nFL = [(30, 33), (25, 27), (20, 21), (14, 14)]')
s=s.replace('BOB = [(0, -14.0), (1, -9.0), (2, -4.0), (3, 0.0)]','BOB = [(1, -12.0), (2, -8.0), (2, -4.0), (3, 0.0)]')
s=s.replace('SH["fnpig_rim"] =  ... [cut]
wrote shows/scenes/deadmau5 - FN Pig.sprites.json 60 sprites 44475 bytes
wrote shows/scenes/deadmau5 - FN Pig.scene.json scenes 35 hits 54
deadmau5 - FN Pig: 36 scenes, 54 hits, written into shows/deadmau5 - FN Pig.json
bar 15.4    dream          shell max  95 mean   2.5   ears max   0 mean   0.0   dream
bar 31.5    clunk          shell max 128 mean   6.7   ears max   0 mean   0.0   stir · clunk 3
bar 60      rouse          shell max 113 mean  13.9   ears max   2 mean   0.1   rouse
bar 66      lights         shell max 212 mean  34.4   ears max  51 mean   3.3   lights
bar 100.5   hazard         shell max 220 mean  10.1   ears max  52 mean   5.5   hazard
bar 104.1                  shell max  61 mean   9.6   ears max  24 mean   0.6   hazard
bar 110                    shell max  99 mean  10.5   ears max  11 mean   0.2   waking
bar 114.2                  shell max 119 mean  17.3   ears max 143 mean  15.3   waking
bar 117.3                  shell max 140 mean  22.6   ears max 177 mean  15.8   wake3
bar 118.03  KICK           shell max 180 mean  16.1   ears max 231 mean  85.2   pacing · first kick
bar 125.8   inhale         shell max 142 mean  16.8   ears max 213 mean  86.6   pacing · inhale 125
bar 126.03  DROP           shell max 255 mean  48.7   ears max 223 mean  97.4   raw · snort 126
bar 126.1                  shell max 255 mean  47.3   ears max 137 mean  67.3   raw · snort 126
bar 126.2                  shell max 217 mean  46.8   ears max 140 mean  60.5   raw · snort 126
bar 127.02                 shell max 110 mean  19.6   ears max 127 mean  35.9   raw
bar 127.1                  shell max  87 mean  18.0   ears max  55 mean  14.9   raw
bar 127.2                  shell max  84 mean  17.2   ears max  78 mean  19.7   raw
bar 127.35                 shell max  87 mean  18.3 
... [cut] ...
x 130 mean  43.0   fury2
bar 252.1   shake          shell max 204 mean  36.2   ears max 165 mean  21.3   fury3
bar 253.3                  shell max 204 mean  35.2   ears max 120 mean  27.5   fury3
bar 260.05  squeal         shell max 204 mean  37.0   ears max 118 mean  16.6   squeal
bar 265.7                  shell max 244 mean  39.8   ears max 255 mean 120.6   squeal · inhale 265
bar 266.1   tire           shell max  93 mean  22.1   ears max  69 mean  16.4   tiring
(scratch)/ki
Sat Oct 31 13:01:38 PDT 2026
```

```
$ cd "~/deadmau5 app"; KIT=tools/showkit; W=$KIT/work/fnpig; export KIT; cat > $W/lev.py <<'EOF'
import sys, os
sys.path.insert(0, os.getcwd()); sys.path.insert(0, os.environ["KIT"])
import numpy as np, grid
d = grid.env_of("shows/deadmau5 - FN Pig.mp3")
spb=0.46875; t0=0.490; tt=d["tt"]
CH=" .:-=+*#%@"
def show(bars,bands=("sub","pres","air")):
    for nm in bands:
        v=d[nm]
        print(nm)
        for b in bars:
            r=[]
            for k in range(16):
                t=t0+(b+k/16)*4*spb
                i=np.searchsorted(tt,t); j=np.searchsorted(tt,t+spb/4)
                r.app ... [cut]
sub
   132  2.0  2.3  1.3  1.0  2.1  2.3  1.2  0.7  1.9  2.2  1.1  0.8  2.0  2.1  1.4  1.2
   133  1.9  2.3  1.3  1.0  2.0  2.1  1.4  1.2  1.9  2.0  1.1  0.7  2.0  2.0  1.4  1.1
   134  2.0  2.2  1.2  1.0  2.0  2.3  1.2  0.7  1.9  2.2  1.4  1.5  2.0  2.1  1.4  1.2
   165  1.9  2.2  1.2  1.0  2.0  2.2  1.1  1.3  1.9  1.9  1.5  1.3  1.3  1.2  0.6  0.4
   166  1.3  1.3  0.4  0.1  1.3  1.4  0.5  0.1  1.3  1.4  0.8  0.7  1.4  1.3  0.7  0.5
   173  1.2  1.2  0.5  0.2  1.4  1.6  1.6  1.5  1.4  1.5  1.5  1.5  2.0  2.1  1.4  1.1
   174  2.0  2.2  1.2  0.9  2.0  2.2  1.2  0.7  1.9  2.2  1.1  0.7  2.0  2.0  1.4  1.2
   205  1.9  2.2  1.2  1.0  2.0  2.0  1.4  1.3  1.8  1.9  1.3  1.2  0.6  0.3  0.2  0.3
   206  0.4  0.4  0.3  0.4  0.4  0.4  0.4  0.4  0.4  0.4  0.4  0.4  0.4  0.4  0.4  0.4
   233  1.0  1.0  1.0  1.1  1.3  1.4  1.4  1.4  1.2  1.3  1.3  1.2  2.0  2.1  1.4  1.1
   234  1.9  2.2  1.2  0.9  2.1  2.3  1.2  0.7  1.9  2.2  1.5  1.4  2.0  2.1  1.4  1.1
   265  1.9  2.2  1.2  0.9  1.9  2.0  1.3  1.1  1.9  1.9  1.0  0.6  1.5  1.7  1.0  1.0
   266  1.2  1.3  0.4  0.0  1.5  1.5  0.6  0.8  1.3  1.3  1.4  1.7  1.6  1.7  1.1  1.2
   273  1.4  1.3  0.5  0.0  1.4  1.5  0.6  0.8  1.2  1.1  0.4  0.1  1.4  1.4  0.4  0.0
   274  1.2  1.3  0.5  0.0  1.4  1.5  0.6  0.1  1.3  1.3  0.5  0.0  1.4  1.5  0.5  0.0
   281  1.3  1.3  0.5  0.0  1.4  1.6  0.6  0.2  1.1  1.2  0.5  0.0  0.0  0.0  0.0  0.0
   282  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0
pres
   132  2.2  1.1  1.9  0.3  1.6  0.7  1.3  2.1  2.2  1.0  1.0  0.5  1.5  0.6  1.8  1.3
   133  2.2  1.0  1.9  0.3  1.5  1.4  1.8  2.3  2.4  2.0  2.1  2.1  1.5  1.6  2.2  2.3
   134  2.1  1.4  1.9  1.8  1.6  1.1  1.6  2.1  2.1  1.3  1.5  1.7  1.6  0.8  1.7  1.4
   165  2.3  1.1  1.9  0.7  1.5  1.7  2.2  2.3  2.4
... [cut] ...
2.4  1.9  2.0  1.8  1.7  1.2  1.6  2.0  2.4  1.2  1.5  1.4  1.7  0.9  1.8  1.5
   265  2.4  1.3  2.0  0.8  1.7  1.5  2.3  2.2  2.4  1.9  2.1  2.1  1.8  2.4  2.8  2.6
   266  2.0  2.0  2.2  1.9  1.8  1.0  1.3  1.7  1.9  1.3  1.4  1.5  1.8  0.8  1.8  1.3
   273  1.8  1.1  0.2  0.3  1.0  0.3  0.6  2.1  2.7  2.1  1.7  1.4  1.4  2.5  2.8  2.7
   274  2.0  2.0  2.1  2.0  1.1  1.1  1.3  1.3  1.9  1.3  0.6  0.7  0.9  0.3  0.2  0.6
   281  1.8  1.2  0.1  0.3  1.0  0.3  0.5  2.0  2.5  2.1  1.7  1.3  0.9  0.6  0.3  0.2
   282  0.1  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0
```

```
$ cd "~/deadmau5 app"; KIT=tools/showkit; W=$KIT/work/fnpig; export KIT; sed -i '' 's/^show(\[.*$/show([116,117,118,124,125,126,127,91,92,100,207,208,215,216])/' $W/lev.py; python3 $W/lev.py; date
sub
   116  1.0  1.0  1.0  1.2  1.2  1.1  1.1  1.2  1.1  1.3  1.4  1.3  1.1  1.1  1.1  1.1
   117  1.1  1.1  1.2  1.1  1.5  1.7  1.7  1.6  1.5  1.4  1.3  1.3  1.3  1.2  0.6  0.4
   118  1.2  1.2  0.4  0.2  1.3  1.4  0.4  0.1  1.2  1.3  0.7  0.8  1.2  1.3  0.7  0.5
   124  1.2  1.2  0.5  0.1  1.4  1.4  0.4  0.2  1.2  1.3  0.8  0.8  1.4  1.3  0.7  0.4
   125  1.2  1.2  0.5  0.1  1.3  1.2  0.4  0.1  1.2  1.2  0.9  0.8  2.0  2.1  1.3  1.1
   126  2.0  2.2  1.2  1.0  2.0  2.3  1.2  0.7  1.9  2.2  1.1  0.8  2.0  2.1  1.4  1.2
   127  1.9  2.2  1.3  1.0  2.1  2.3  1.1  0.8  2.0  2.2  1.3  0.1  1.9  2.1  1.5  1.2
    91  0.4  0.4  0.3  0.3  0.4  0.4  0.3  0.4  0.5  0.4  0.4  0.4  0.4  0.3  0.3  0.4
    92  0.4  0.4  0.3  0.3  0.3  0.3  0.3  0.3  0.3  0.3  0.2  0.3  0.4  0.4  0.4  0.4
   100  0.5  0.5  0.6  0.4  0.4  0.4  0.5  0.5  0.4  0.5  0.5  0.6  0.8  0.8  0.8  0.9
   207  0.5  0.4  0.4  0.5  0.5  0.4  0.4  0.4  0.4  0.4  0.4  0.4  0.4  0.3  0.4  0.4
   208  0.4  0.4  0.3  0.3  0.4  0.4  0.3  0.4  0.4  0.3  0.3  0.4  0.3  0.3  0.4  0.4
   215  0.4  0.4  0.4  0.4  0.4  0.4  0.5  0.4  0.4  0.4  0.4  0.4  0.3  0.2  0.3  0.4
   216  0.3  0.5  0.7  0.4  0.4  0.5  0.5  0.5  0.4  0.5  0.4  0.5  0.6  0.7  0.8  0.8
pres
   116  2.1  2.1  2.1  2.1  2.1  2.1  2.1  2.1  2.1  2.1  2.1  2.1  2.2  2.1  2.1  2.1
   117  2.2  2.1  2.1  2.1  2.2  2.2  2.1  2.1  2.1  2.1  2.2  2.1  1.5  1.7  2.3  2.3
   118  2.2  1.6  2.0  1.8  1.7  1.3  1.5  2.2  2.3  1.2  1.0  1.2  1.6  0.9  1.7  1.4
   124  2.1  1.1  2.0  0.3  1.8  0.8  1.4  2.2  2.3  1.1  1.0  0.5  1.6  0.8  1.9  1.2
   125  2.3  1.2  2.0  0.3  1.7  1.6  2.0  2.3  2.4  2.0  2.1  2.1  1.6  1.6  2.2  2.3
   126  2.0  1.5  1.9  1.7  1.6  1.1  1.5  2.1  2.1  1.3  1.0  1.2  1.6  0.8  1.8  1.4
   127  2.2  1.1  1.8  0.5  1.1  0.6  0.8  2.1  2.0
... [cut] ...
 0.7  0.6  0.6  0.6  0.6  0.7  1.4  1.2  1.0  0.7
    92  0.7  0.7  1.5  1.3  1.1  0.8  0.8  0.6  1.1  0.9  1.5  1.2  1.1  0.7  0.7  0.6
   100  0.5  0.5  1.6  1.3  1.1  0.5  0.6  0.5  1.0  0.8  1.5  1.2  1.1  0.5  0.6  0.4
   207  0.2  0.2  0.2  0.2  0.1  0.1  0.1  0.1  0.1  0.1  0.1  0.2  1.5  1.1  1.0  0.5
   208  0.4  0.5  1.6  1.3  1.0  0.6  0.5  0.5  1.0  0.7  1.5  1.1  1.0  0.5  0.5  0.4
   215  0.4  0.3  0.3  0.2  0.2  0.1  0.2  0.1  0.1  0.1  0.1  0.1  1.4  1.1  0.9  0.5
   216  0.4  0.5  1.5  1.3  1.1  0.6  0.6  0.5  1.0  0.8  1.5  1.2  1.1  0.5  0.5  0.4
Sat Oct 31 13:03:04 PDT 2026
```

```
$ cd "~/deadmau5 app"; KIT=tools/showkit; W=$KIT/work/fnpig; python3 - <<'EOF'
KIT="tools/showkit"
p=KIT+"/work/fnpig/make_sprites.py"
s=open(p).read()
# rounder nostrils: half widths per LED row, by hand, for the rows the LEDs really have
s=s.replace('''def nostrils(cx, cy, nx, rx, ry):
    out = np.zeros(len(PX), bool)
    for side in (-1, 1):
        out |= ((PX - (cx + side * nx)) / rx) ** 2 + ((PY - cy) / ry) ** 2 <= 1.0
    return out
''','''def nostrils(cx, cy, nx, rx, ry):
    out = np.zeros(len(PX), b ... [cut]
wrote shows/scenes/deadmau5 - FN Pig.sprites.json 61 sprites 45197 bytes
tools/showkit/songs/fnpig/try1.png (1800, 338)
Sat Oct 31 13:04:02 PDT 2026
```

```
$ cd "~/deadmau5 app"; KIT=tools/showkit; W=$KIT/work/fnpig; cat > $W/dbg.py <<'EOF'
import sys, os, json
sys.path.insert(0, os.getcwd())
import numpy as np, mau5engine as E
h=E.Helmet()
out=np.asarray(E.make("sprite",sprite="fnpig_snout0",color=(255,255,255),y_lo=52.0,y_hi=172.0,x_half=172.0).render(h,0.0,None),float)
lit=out[:,0]>0
PX,PY=h.px,h.py
s=h.shell
rows=np.array([167.8,162.9,156.6,148.7,139.6,129.1,117.4,104.6,90.9,76.3,61.0])
for y in rows:
    m=s&(np.abs(PY-y)<3)
    idx=np.where(m)[0]
    idx=idx[np.argsort(PX[idx])]
    line=""
    # map to 40mm-scale columns: print each LED in or ... [cut]
 167.8 n= 1 x    5.9..   5.9  .
 162.9 n= 3 x  -56.7..   8.1  .##
 156.6 n=17 x  -73.6..  73.0  .....#########...
 148.7 n=17 x  -88.3..  87.6  ..###############
 139.6 n=34 x -102.2.. 102.2  ##################################
 129.1 n=30 x -115.1.. 115.1  #########...######...#########
 117.4 n=30 x -127.0.. 127.0  ..######.....####.....######..
 104.6 n=34 x -137.7.. 137.7  .....######.....##.....######.....
  90.9 n=34 x -147.1.. 147.1  ......#####.....##.....#####......
  76.3 n=34 x -155.1.. 155.1  .........####..####..####.........
  61.0 n=34 x -161.8.. 161.8  ............##########............
[-102, -101, -100, -97, -94, -89, -84, -79, -72, -65, -58, -50, -41, -33, -23, -14, -5, 5, 14, 23, 33, 41, 50, 58, 65, 72, 79, 84, 89, 94, 97, 100, 101, 102]
[-115, -114, -112, -109, -105, -101, -95, -89, -65, -56, -47, -37, -26, -16, -5, 5, 16, 26, 37, 47, 56, 65, 89, 95, 101, 105, 109, 112, 114, 115]
```

```
$ cd "~/deadmau5 app"; KIT=tools/showkit; W=$KIT/work/fnpig; python3 - <<'EOF'
KIT="tools/showkit"
p=KIT+"/work/fnpig/write_treatment.py"
s=open(p).read()
a=s.index('tr = {"v": 1')
head=s[:a]
head=head.replace('''"amber": [[0,0,0],[120,50,0],[255,130,0],[255,190,30]],''','''"amber": [[0,0,0],[120,50,0],[255,130,0],[255,190,30]],
 "sausage": [[0,0,0],[0,0,0],[30,60,80],[90,130,150],[255,26,60],[255,40,75]],
 "fat": [[0,0,0],[200,70,80],[255,150,150]],''')
head=head.replace('''"hazard": [[0,0,0],[0,0,0],[0,0,0], ... [cut]
wrote shows/scenes/deadmau5 - FN Pig.scene.json scenes 55 hits 52
     282   529.24s  energy 0.00  bass 0.00 (punch 0.34)  mid 0.00  high 0.02
     283   531.12s  energy 0.00  bass 0.00 (punch 0.00)  mid 0.00  high 0.00
deadmau5 - FN Pig: 56 scenes, 52 hits, written into shows/deadmau5 - FN Pig.json
deadmau5 - FN Pig: 13286 frames at 25 fps through the guard
  scene            from  mean mA   p95 mA     heat   allow W      ms
  asleep           0.0s       23       58     0.0%      18.1    0.07
  dream           11.8s       47      124     0.0%      18.1    0.14
  stir            47.3s      180      300     0.0%      18.1    0.15
  rouse           84.9s      339      368     0.6%      18.1    0.13
  lights         120.5s      341      357     0.9%      18.1    0.13
  wash           135.5s      317      330     1.2%      18.1    0.12
  hold breath    165.0s      179      296     1.2%      18.1    0.12
  pickup         172.6s       36       87     0.8%      18.1    0.06
  snorts         173.0s      219      341     0.8%      18.1    0.10
  hazard         188.0s      375      491     0.8%      18.1    0.10
  waking         203.0s      460      563     1.8%      18.1    0.14
  wake3          218.0s      458      630     2.1%      18.1    0.14
  pacing         221.8s      539      798     3.4%      18.1    0.17
  inhale1        235.6s      658     1000     3.5%      18.1    0.10
  slam1          236.3s      110      202     3.4%      18.1    0.06
  raw            236.8s      574      804     5.0%      18.1    0.27
  raw in         250.6s      646      986     5.1%      18.1    0.16
  root           251.8s      606      889     6.8%      18.1    0.23
  root in        265.6s      646      986     7.0%      18.1    0.16
  cold           266.8s      624     1000     8.8%      18.
... [cut] ...
2    30.5%      18.1    0.25
  squeal         484.2s      638     1000    32.4%      18.1    0.28
  squeal in      498.1s      571      962    32.6%      18.1    0.28
  tiring         499.2s      404      633    33.2%      18.1    0.22
  tiring in      513.1s       94      152    33.1%      18.1    0.07
  dozing         514.2s       19       41    33.1%      18.1    0.07
  last breath    528.3s       52      122    31.5%      18.1    0.06
  dark           529.2s        0        0    31.4%      18.1    0.01
  worst frame 1.32 ms; no scene reaches the sustained floor
Sat Oct 31 13:05:37 PDT 2026
```

```
$ cd "~/deadmau5 app"; python3 mau5scene.py check "TIKI TIKI - Slowed" 2>&1 | tail -62 | cut -c1-80 | awk 'NR%3==1'; KIT=tools/showkit; W=$KIT/work/fnpig; python3 $KIT/sheet.py "deadmau5 - FN Pig" $W/a5.png 40.5:stir 91.76:pickup 92.13:snort 94.13 100.14:hazard 108.1:waking 113.02 117.02 118.03:KICK 122.27 125.5:inhale 125.76:SLAM 125.95 126.02:DROP 126.07 126.13 126.2 127.02 127.27 133.6:held 134.02:root 136.27 138.77 144.02:cold 152.02:flush 153.27 160.27:flush2 165.8 168.02:pacing2 173.8:SLAM2 174.02:NEON 174.13 176.27 177.02 184.27:grinder 192.02:xray 192.27 200.02:neon4 205.5 206.3:hush 207. ... [cut]
TIKI TIKI - Slowed: 8002 frames at 25 fps through the guard
  dark             0.1s        0        0    18.7%      18.1    0.01
  lighting         7.0s      199      436     0.0%      18.1    0.10
  dip             24.4s      140      269     1.9%      18.1    0.07
  burn            38.4s      392      815     3.6%      18.1    0.12
  still           48.8s      465      491     3.6%      18.1    0.23
  vlow            66.2s      187      376     3.8%      18.1    0.05
  bigb            83.6s      565      845     7.1%      18.1    0.24
  stop2          109.6s       38       60     7.1%      18.1    0.07
  verse2         118.4s      313      762     7.3%      18.1    0.12
  sunset         132.3s      588      877     8.8%      18.1    0.21
  lagoon3        163.6s      177      309    10.1%      18.1    0.10
  swell3         172.3s      373      563    10.0%      18.1    0.09
  vrise3         186.2s      224      602    10.0%      18.1    0.10
  duel3          205.3s      565      888    12.2%      18.1    0.15
  dip2           222.9s      146      266    14.1%      18.1    0.07
  burn4          236.8s      329      621    15.6%      18.1    0.10
  still4         247.2s      354      480    15.3%      18.1    0.20
  vlow4          264.6s      189      377    15.5%      18.1    0.05
  final2         282.0s      584     1000    18.5%      18.1    0.25
  worst frame 1.11 ms; no scene reaches the sustained floor
bar 275.02  doze           shell max 116 mean   2.5   ears max   0 mean   0.0   dozing
bar 281.6   last           shell max 125 mean   5.7   ears max   0 mean   0.0   last breath
(scratch)/ki
Sat Oct 31 13:05:51 PDT 2026
```

I'll read the correction and the new tools first.

```
$ cd "~/deadmau5 app"; KIT=tools/showkit; date; tail -30 "$KIT/BRIEF.md"; echo ======; cat $KIT/sheet.py; echo ======; cat $KIT/power.py; echo ======; cat $KIT/scenepower.py
Exit code 1
Sat Oct 31 13:07:04 PDT 2026
4. Write the treatment with a small Python generator in your scratch folder (see Tiki's), using `from fmt import save` with `sys.path.insert(0, KIT)`, then `python3 mau5scene.py compile "<base>"` and fix what it refuses. Put a real `about` string in it describing the concept, the same style as Tiki's.
5. Look at it. `python3 $KIT/sheet.py "<base>" out.png 40:drop 40.25 41 ...` renders tiles as the helmet will really look after the power guard, and prints how bright shell and ears end up. READ THE PNG. Does it read as your idea? Is the shell visible next to the ears? Check every major section, each hit, and both a kick and the gap after it. Iterate.
6. `python3 mau5scene.py check "<base>"`: every scene through the power guard. Heat under about 40%, and no scene "at the sustained floor". `python3 $KIT/grid.py check "<base>"` again at the end.

## The treatment format
Bars, not seconds: bar b is `t0 + 4 b spb` on your grid. Top level: `v:1, show, about, lead:0, marks{name:bar or "other+2"}, palettes{name:[[r,g,b],...] or {"stops":[...],"wrap":true}}, motifs{name: layer or [layers]}, scenes[], hits[]`. A value may be a number, `[from,to]` (a ramp over the scene), `{"<bar or mark>":v,...}` (steps at bars), or `{"band":"bass|mid|high","lo":a,"hi":b,"punch":true|false}` (driven by the track, resolved live; the phone has these curves). Scenes tile the song, from bar -1 (a gap is dark): `{"name","from","to","pal","pump":{"pat":"x...","step":0.25,"depth":0.2,"decay":0.5},"out":beats of darkness before the next scene (max 4),"layers":[...]}`; `like:"earlier scene"` copies one and `patch:{"layerIndex":{...}}`, `add:[...]` or `each:{...}` change it (patch indexes the authored layers before motif expansion). Hits are moments over a scene: `{"n
... [cut] ...
t the guard does that matters: the shell region is capped near 300 mA (mean about 10 of 255) with a soft knee, so anything above about 64 comes out near 62 and hues shift; when the whole frame hits 1000 mA the governor sheds the shell hard, so on a big hit with loud ears the shell can go almost black, and full-shell white comes out gray. So on hits: dark ears on the first beat if the shell has the picture, or give the moment to the ears on purpose. `python3 $KIT/scenepower.py "<base>"` prints per scene the mA, how often the governor hit, shell and ear means, and heat.
(eval):1: ===== not found
```

```
$ cd "~/deadmau5 app"; KIT=tools/showkit; cat $KIT/sheet.py; echo; echo "--- power"; cat $KIT/power.py; echo; echo "--- scenepower"; cat $KIT/scenepower.py; echo; echo "--- run"; python3 $KIT/power.py "deadmau5 - FN Pig"; python3 $KIT/scenepower.py "deadmau5 - FN Pig" | cut -c1-110
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
g = show["scenes"]["grid"]; spb = g["spb"]; t0 = g["t0"]
h = E.Helmet()
sc = PV.Scene(h); sc.back = sc.back * 0
scn = SS.Scenes(show["scenes"], h)
def tof(bar):
    B = 4 * bar
    return t0 + B * spb + sum(bb * spb for at, bb in g.get("holds", []) if B > at)
cols = int(os.environ.get("COLS","6")); W = int(os.environ.get("TW","300")); H = int(W*245/300)
GAM = float(os.environ.get("GAM","2.0"))
rows = (len(marks) + cols - 1) // cols
o = Image.new("RGB", (cols * W, rows * H), (0, 0, 0))
d = ImageDraw.Draw(o)
for k, (bar, lab) in enumerate(marks):
    t = tof(bar)
    guard = mau5power.load(count=h.n)
    for dt in (1.0, 0.8, 0.6, 0.5, 0.4, 0.3, 0.2, 0.12, 0.08, 0.04):
        f0, g0, _ = scn.frame(t - dt, music)
        guard.apply(f0, now=t - dt, gain=g0)
    f, gn, label = s
... [cut] ...
.4     34  30.4%
shake in          604    962     41    100     6.1    24.8     33  30.5%
squeal            638   1000     45    100     5.6    27.6     29  32.4%
squeal in         571    962     66    100     5.0    24.7     21  32.6%
tiring            404    633      2     62     9.0     7.5     38  33.2%
tiring in          94    152      0      0     3.1     0.0     53  33.1%
dozing             19     41      0      0     0.6     0.0     49  33.1%
last breath        52    122      0      0     1.7     0.0     56  31.5%
dark                0      0      0      0     0.0     0.0      0  31.4%
```

```
$ cd "~/deadmau5 app"; KIT=tools/showkit; W=$KIT/work/fnpig; python3 - <<'EOF'
KIT="tools/showkit"
p=KIT+"/work/fnpig/write_treatment.py"
s=open(p).read()
def rep(a,b,cnt=1):
    global s
    assert s.count(a)>=1, a
    s=s.replace(a,b) if cnt==0 else s.replace(a,b,cnt)
# slam smaller so the nostrils stay two
rep('orbs([58, 44], 12, [1.0, 0.5], c)','orbs([46, 34], 12, [1.0, 0.5], c)')
rep('orbs([36, 58], 12, [0.5, 0.95], 0.65, pal="meat")','orbs([34, 46], 12, [0.5, 0.95], 0.65, pal="meat")')
rep('orbs([36, 58] ... [cut]
wrote shows/scenes/deadmau5 - FN Pig.scene.json scenes 55 hits 52
deadmau5 - FN Pig: 56 scenes, 52 hits, written into shows/deadmau5 - FN Pig.json
deadmau5 - FN Pig: 13286 frames at 25 fps through the guard
  stir            47.3s      180      300     0.0%      18.1    0.16
  hold breath    165.0s      179      296     1.5%      18.1    0.13
  waking         203.0s      460      563     2.1%      18.1    0.15
  slam1          236.3s       65      120     3.5%      18.1    0.06
  root in        265.6s      646      986     6.6%      18.1    0.17
  flush in       295.6s      639      986    10.2%      18.1    0.17
  inhale2        325.6s      699     1000    13.6%      18.1    0.11
  grinder        341.8s      607      885    17.2%      18.1    0.25
  neon4          371.8s      614      940    21.4%      18.1    0.27
  snorts2        390.5s      244      410    21.4%      18.1    0.14
  slam3          438.8s      116      181    23.3%      18.1    0.07
  fury2 in       468.1s      604      962    27.5%      18.1    0.30
  squeal in      498.1s      571      962    31.8%      18.1    0.28
  last breath    528.3s       52      122    30.7%      18.1    0.07
  worst frame 2.82 ms; no scene reaches the sustained floor
bar 0.3     breath     sent   63 mA  shell max  54 mean   2.0  ears max   0 mean   0.0  as
bar 0.45               sent   15 mA  shell max  38 mean   0.5  ears max   0 mean   0.0  as
bar 0.84               sent   64 mA  shell max  55 mean   2.1  ears max   0 mean   0.0  as
bar 1                  sent   11 mA  shell max  35 mean   0.3  ears max   0 mean   0.0  as
bar 5                  sent   23 mA  shell max  44 mean   0.8  ears max   0 mean   0.0  as
bar 5.3                sent   23 mA  shell max  44 mean   0.8  ears max   0 mean   0.0  as
bar 12.2             
... [cut] ...
rs max  25 mean   1.5  wa
bar 84                 sent  313 mA  shell max  33 mean   9.6  ears max  12 mean   0.7  wa
bar 86                 sent  305 mA  shell max  42 mean   9.6  ears max   5 mean   0.3  wa
bar 88      title      sent   89 mA  shell max  61 mean   2.6  ears max   0 mean   0.0  ho
bar 89                 sent  215 mA  shell max  61 mean   6.9  ears max   0 mean   0.0  ho
bar 90                 sent  235 mA  shell max  61 mean   7.9  ears max   0 mean   0.0  ho
bar 91                 sent  128 mA  shell max  61 mean   4.3  ears max   0 mean   0.0  ho
Sat Oct 31 13:07:19 PDT 2026
```

The guard changes the picture a lot, so I'll read how it behaves before re-judging.

```
$ cd "~/deadmau5 app"; wc -l mau5power.py; grep -n "def \|class " mau5power.py | head -50; ls -la mau5power*; cat power.json 2>/dev/null | head -40; grep -n "shell\b\|regions\|knee\|ceiling\|budget" mau5power.py | head -60
     513 mau5power.py
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
-rw-r--r--@ 1 jones  staff  24732 Oct 30 04:10 mau5power.py
12:shell are held on with hot glue inside a sealed print, and when that
15:brightness number cannot express that; a ceiling per region can.
24:  ceiling   a per-LED cap by region, so the shell can never be driven
27:  governor  if the whole frame still estimates over budget, scale it
28:            back -- but shed from the shell first and the tubes last,
51:# is never slowed: that is what keeps every frame inside the budget.
64:    Two numbers, because they answer different questions.  ``ceiling``
66:    ``budget_ma`` is for the span as a whole: how much current may all
68:    reaches the budget; a region asked to go solid white dims itself
72:    def __init__(self, name, lo, hi, ceiling, budget_ma, shed=1.0, floor=0.0):
74:        self.ceiling = int(ceiling)        # 0-255, per channel, per LED
75:        self.budget_ma = float(budget_ma)  # for the whole span
78:        # about priority and wrong about the endpoint: a sh
... [cut] ...
      # spends the budget exactly, so a floor applied as a second pass
336:        # moved with whatever the ears were doing, and the shell, at
338:        # sparkle overlay on the tubes pumped the shell frame to frame.
342:        # so never over budget; and it runs on frames under budget too,
347:        # took a further 3-17% off the shell's frame-to-frame jitter on
348:        # top of the soft ceiling, for 2-6% of their current.  A rate per
349:        # region, so the shell climbs no faster than the tubes, lost 30%
351:        # over budget then held the shell down for two seconds.  Half
```

```
$ cd "~/deadmau5 app"; KIT=tools/showkit; W=$KIT/work/fnpig; COLS=8 TW=225 python3 $KIT/sheet.py "deadmau5 - FN Pig" $W/g1.png 15.4:dream 40.5:stir 66:lights 89.5:title 92.13:snort 100.14:hazard 104.1 113.02 117.02 118.03:KICK 122.27 125.5:inhale 125.76:SLAM 126.02:DROP 126.13 126.27 127.02 127.27 133.6:held 134.02:root 136.27 144.02:cold 152.02:flush 153.27 160.27:flush2 165.8 168.02:pace2 173.8:SLAM2 174.02:NEON 174.27 176.27 184.27:grind 192.02:xray 200.02:neon4 206.3:hush 208.13:stab 216.13:rebuild 226.3 232.5 233.8:SLAM3 234.02:FURY 234.5 235.02:face 236.27 244.02:fury2 252.27:shake 262.02:s ... [cut]
bar 15.4    dream      sent   52 mA  shell max  49 mean   1.6  ears max   0 mean   0.0  dream
bar 40.5    stir       sent  202 mA  shell max  57 mean   6.4  ears max   0 mean   0.0  stir · clun
bar 66      lights     sent  354 mA  shell max  28 mean   9.6  ears max  50 mean   3.2  lights
bar 89.5    title      sent  236 mA  shell max  61 mean   7.6  ears max   0 mean   0.0  hold breath 
bar 92.13   snort      sent  311 mA  shell max  62 mean   7.8  ears max 113 mean   4.0  snorts
bar 100.14  hazard     sent  209 mA  shell max  62 mean   6.5  ears max  20 mean   0.6  hazard
bar 104.1              sent  266 mA  shell max  39 mean   8.4  ears max  24 mean   0.6  hazard
bar 113.02             sent  313 mA  shell max  49 mean   9.9  ears max  33 mean   0.7  waking
bar 117.02             sent  348 mA  shell max  38 mean   9.9  ears max  81 mean   2.8  wake3
bar 118.03  KICK       sent 1000 mA  shell max   8 mean   1.3  ears max 166 mean  57.3  pacing · fi
bar 122.27             sent  633 mA  shell max  61 mean   9.0  ears max 127 mean  21.6  pacing
bar 125.5   inhale     sent  397 mA  shell max  54 mean   7.3  ears max  85 mean  10.5  inhale1 · i
bar 125.76  SLAM       sent   44 mA  shell max  14 mean   1.4  ears max   0 mean   0.0  slam1
bar 126.02  DROP       sent 1000 mA  shell max   4 mean   1.4  ears max 163 mean  56.9  raw · snort
bar 126.13             sent  779 mA  shell max   7 mean   2.5  ears max  93 mean  41.3  raw · snort
bar 126.27             sent 1000 mA  shell max  16 mean   6.5  ears max 163 mean  47.4  raw · snort
bar 127.02             sent  648 mA  shell max  38 mean   9.8  ears max 127 mean  20.9  raw
bar 127.27             sent  659 mA  shell max  37 mean   9.8  ears max 127 mean  21.6  raw
bar 133.6   held       sent  464 mA  shell max  35 mean   8.0  
... [cut] ...
.02  squeal     sent  924 mA  shell max  29 mean   9.9  ears max 151 mean  37.3  squeal
bar 265.2              sent  760 mA  shell max   3 mean   1.1  ears max  64 mean  42.8  squeal
bar 266.02  tired      sent  310 mA  shell max   7 mean   2.0  ears max  89 mean  14.4  tiring
bar 273.8              sent   82 mA  shell max  51 mean   2.7  ears max   0 mean   0.0  tiring in
bar 275.02  doze       sent   43 mA  shell max  53 mean   1.4  ears max   0 mean   0.0  dozing
(scratch)/ki
Sat Oct 31 13:07:23 PDT 2026
```

```
$ cd "~/deadmau5 app"; wc -l mau5power.py; grep -n "def \|class " mau5power.py | head -50; ls -la mau5power*; cat power.json 2>/dev/null | head -40; grep -n "shell\b\|regions\|knee\|ceiling\|budget" mau5power.py | head -60
     513 mau5power.py
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
-rw-r--r--@ 1 jones  staff  24732 Oct 30 04:10 mau5power.py
12:shell are held on with hot glue inside a sealed print, and when that
15:brightness number cannot express that; a ceiling per region can.
24:  ceiling   a per-LED cap by region, so the shell can never be driven
27:  governor  if the whole frame still estimates over budget, scale it
28:            back -- but shed from the shell first and the tubes last,
51:# is never slowed: that is what keeps every frame inside the budget.
64:    Two numbers, because they answer different questions.  ``ceiling``
66:    ``budget_ma`` is for the span as a whole: how much current may all
68:    reaches the budget; a region asked to go solid white dims itself
72:    def __init__(self, name, lo, hi, ceiling, budget_ma, shed=1.0, floor=0.0):
74:        self.ceiling = int(ceiling)        # 0-255, per channel, per LED
75:        self.budget_ma = float(budget_ma)  # for the whole span
78:        # about priority and wrong about the endpoint: a sh
... [cut] ...
      # spends the budget exactly, so a floor applied as a second pass
336:        # moved with whatever the ears were doing, and the shell, at
338:        # sparkle overlay on the tubes pumped the shell frame to frame.
342:        # so never over budget; and it runs on frames under budget too,
347:        # took a further 3-17% off the shell's frame-to-frame jitter on
348:        # top of the soft ceiling, for 2-6% of their current.  A rate per
349:        # region, so the shell climbs no faster than the tubes, lost 30%
351:        # over budget then held the shell down for two seconds.  Half
```

```
$ cd "~/deadmau5 app"; KIT=tools/showkit; W=$KIT/work/fnpig; COLS=8 TW=225 python3 $KIT/sheet.py "deadmau5 - FN Pig" $W/g1.png 15.4:dream 40.5:stir 66:lights 89.5:title 92.13:snort 100.14:hazard 104.1 113.02 117.02 118.03:KICK 122.27 125.5:inhale 125.76:SLAM 126.02:DROP 126.13 126.27 127.02 127.27 133.6:held 134.02:root 136.27 144.02:cold 152.02:flush 153.27 160.27:flush2 165.8 168.02:pace2 173.8:SLAM2 174.02:NEON 174.27 176.27 184.27:grind 192.02:xray 200.02:neon4 206.3:hush 208.13:stab 216.13:rebuild 226.3 232.5 233.8:SLAM3 234.02:FURY 234.5 235.02:face 236.27 244.02:fury2 252.27:shake 262.02:s ... [cut]
bar 15.4    dream      sent   52 mA  shell max  49 mean   1.6  ears max   0 mean   0.0  dream
bar 40.5    stir       sent  202 mA  shell max  57 mean   6.4  ears max   0 mean   0.0  stir · clun
bar 66      lights     sent  354 mA  shell max  28 mean   9.6  ears max  50 mean   3.2  lights
bar 89.5    title      sent  236 mA  shell max  61 mean   7.6  ears max   0 mean   0.0  hold breath 
bar 92.13   snort      sent  311 mA  shell max  62 mean   7.8  ears max 113 mean   4.0  snorts
bar 100.14  hazard     sent  209 mA  shell max  62 mean   6.5  ears max  20 mean   0.6  hazard
bar 104.1              sent  266 mA  shell max  39 mean   8.4  ears max  24 mean   0.6  hazard
bar 113.02             sent  313 mA  shell max  49 mean   9.9  ears max  33 mean   0.7  waking
bar 117.02             sent  348 mA  shell max  38 mean   9.9  ears max  81 mean   2.8  wake3
bar 118.03  KICK       sent 1000 mA  shell max   8 mean   1.3  ears max 166 mean  57.3  pacing · fi
bar 122.27             sent  633 mA  shell max  61 mean   9.0  ears max 127 mean  21.6  pacing
bar 125.5   inhale     sent  397 mA  shell max  54 mean   7.3  ears max  85 mean  10.5  inhale1 · i
bar 125.76  SLAM       sent   44 mA  shell max  14 mean   1.4  ears max   0 mean   0.0  slam1
bar 126.02  DROP       sent 1000 mA  shell max   4 mean   1.4  ears max 163 mean  56.9  raw · snort
bar 126.13             sent  779 mA  shell max   7 mean   2.5  ears max  93 mean  41.3  raw · snort
bar 126.27             sent 1000 mA  shell max  16 mean   6.5  ears max 163 mean  47.4  raw · snort
bar 127.02             sent  648 mA  shell max  38 mean   9.8  ears max 127 mean  20.9  raw
bar 127.27             sent  659 mA  shell max  37 mean   9.8  ears max 127 mean  21.6  raw
bar 133.6   held       sent  464 mA  shell max  35 mean   8.0  
... [cut] ...
.02  squeal     sent  924 mA  shell max  29 mean   9.9  ears max 151 mean  37.3  squeal
bar 265.2              sent  760 mA  shell max   3 mean   1.1  ears max  64 mean  42.8  squeal
bar 266.02  tired      sent  310 mA  shell max   7 mean   2.0  ears max  89 mean  14.4  tiring
bar 273.8              sent   82 mA  shell max  51 mean   2.7  ears max   0 mean   0.0  tiring in
bar 275.02  doze       sent   43 mA  shell max  53 mean   1.4  ears max   0 mean   0.0  dozing
(scratch)/ki
Sat Oct 31 13:07:23 PDT 2026
```

```
$ cd "~/deadmau5 app"; sed -n 236,415p mau5power.py; python3 - <<'EOF'
import sys
sys.path.insert(0,'.')
import mau5power, mau5engine as E
h=E.Helmet()
g=mau5power.load(count=h.n)
print(g.describe() if hasattr(g,'describe') else '')
EOF
    def apply(self, buf, now=None, gain=1.0):
        """Return (clamped frame, report).  Never raises on a bad frame.

        `now` overrides the clock, so the thermal behaviour can be driven
        deterministically in a test instead of in real time.

        `gain`, at most 1, is applied after every limit.  It is how a show
        pulses on the beat: anything brighter on the beat than off it,
        applied before the guard, is exactly what the ceilings and the
        governor exist to take away again, so on loud material the pulse
        vanished.  Dimming the result can only stay inside the limits.
        """
        now = time.monotonic() if now is None else now
        with np.errstate(over="ignore", invalid="ignore"):
            out = np.asarray(buf, np.float32).reshape(-1, 3)[:self.count].copy()
        # Only the LEDs both the frame and the profile have: a frame
        # shorter than the profile used to fail on the ceiling below,
        # and the phone's twin read past its end into NaN.
        m = len(out)
        # Anything that is not a number is dark, and infinity is full.
        # np.clip passes NaN through untouched, and the phone guard's
        # clamp did the same: one NaN frame made its current NaN, which
        # no budget compares greater than, and its thermal level NaN for
        # good -- governor and thermal ramp off until the page reloaded.
        np.nan_to_num(out, copy=False, nan=0.0, posinf=255.0, neginf=0.0)
        np.clip(out, 0, 255, out)
        asked = self.frame_ma(out)
        amx = out.max(1)               # what was asked of each LED, for the floor

        # -- the ceiling, as a soft knee ---------------------------------
        # It was min(v, c), a clip, and presets render up to 255 against
        # a shell ceili
... [cut] ...
_rim      492..509    18 leds  ceiling 160/255  budget  200 mA  (all-white would want   215)  shed 3
  ear2_rim      510..528    19 leds  ceiling 160/255  budget  190 mA  (all-white would want   227)  shed 3
  ear2_tubes    529..620    92 leds  ceiling 255/255  budget  640 mA  (all-white would want  1748)  shed 1
  every region at its own limit at once: 1950 mA
  thermal: sustains 11.0 W (of which 7.5 W is standby), bursts to 25.5 W on 3000 J of thermal mass
           full brightness for about 207 s before it eases off
  the global governor holds that to 1000 mA -> 1.62 A with standby, 19.5 W
```

```
$ cd "~/deadmau5 app"; sed -n 236,415p mau5power.py; python3 - <<'EOF'
import sys
sys.path.insert(0,'.')
import mau5power, mau5engine as E
h=E.Helmet()
g=mau5power.load(count=h.n)
print(g.describe() if hasattr(g,'describe') else '')
EOF
    def apply(self, buf, now=None, gain=1.0):
        """Return (clamped frame, report).  Never raises on a bad frame.

        `now` overrides the clock, so the thermal behaviour can be driven
        deterministically in a test instead of in real time.

        `gain`, at most 1, is applied after every limit.  It is how a show
        pulses on the beat: anything brighter on the beat than off it,
        applied before the guard, is exactly what the ceilings and the
        governor exist to take away again, so on loud material the pulse
        vanished.  Dimming the result can only stay inside the limits.
        """
        now = time.monotonic() if now is None else now
        with np.errstate(over="ignore", invalid="ignore"):
            out = np.asarray(buf, np.float32).reshape(-1, 3)[:self.count].copy()
        # Only the LEDs both the frame and the profile have: a frame
        # shorter than the profile used to fail on the ceiling below,
        # and the phone's twin read past its end into NaN.
        m = len(out)
        # Anything that is not a number is dark, and infinity is full.
        # np.clip passes NaN through untouched, and the phone guard's
        # clamp did the same: one NaN frame made its current NaN, which
        # no budget compares greater than, and its thermal level NaN for
        # good -- governor and thermal ramp off until the page reloaded.
        np.nan_to_num(out, copy=False, nan=0.0, posinf=255.0, neginf=0.0)
        np.clip(out, 0, 255, out)
        asked = self.frame_ma(out)
        amx = out.max(1)               # what was asked of each LED, for the floor

        # -- the ceiling, as a soft knee ---------------------------------
        # It was min(v, c), a clip, and presets render up to 255 against
        # a shell ceili
... [cut] ...
_rim      492..509    18 leds  ceiling 160/255  budget  200 mA  (all-white would want   215)  shed 3
  ear2_rim      510..528    19 leds  ceiling 160/255  budget  190 mA  (all-white would want   227)  shed 3
  ear2_tubes    529..620    92 leds  ceiling 255/255  budget  640 mA  (all-white would want  1748)  shed 1
  every region at its own limit at once: 1950 mA
  thermal: sustains 11.0 W (of which 7.5 W is standby), bursts to 25.5 W on 3000 J of thermal mass
           full brightness for about 207 s before it eases off
  the global governor holds that to 1000 mA -> 1.62 A with standby, 19.5 W
```

```
$ KIT=tools/showkit; ls -la $KIT; cat $KIT/sheet.py; diff <(sed -n 1,200p $KIT/BRIEF.md) /dev/null | grep -n "guard\|shell\|sent" | head -20; cd "~/deadmau5 app"; git status --short | head -40; sed -n 1,80p mau5power.py | head -120
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
me, lo, hi, ceiling, budget_ma, shed=1.0, floor=0.0):
        self.name, self.lo, self.hi = name, int(lo), int(hi)
        self.ceiling = int(ceiling)        # 0-255, per channel, per LED
        self.budget_ma = float(budget_ma)  # for the whole span
        # The dimmest this region is allowed to be driven while it is
        # being asked for anything at all.  Weighted shedding is right
        # about priority and wrong about the endpoint: a shell with
        # shed 6 is at nothing long before the tubes have given up, so
        # a helmet left running settles into two glowing stripes and
```

```
$ KIT=tools/showkit; sed -n 40,60p $KIT/BRIEF.md; cat $KIT/power.py; cat $KIT/scenepower.py; cd "~/deadmau5 app"; python3 $KIT/power.py "deadmau5 - FN Pig"; python3 $KIT/scenepower.py "deadmau5 - FN Pig" | cut -c1-110; date
Song-specific concept follows in your task. It is a starting point. If the music says otherwise, follow the music, and keep it unique.

## Added after the first run: the long set
These shows also play back to back in a set of up to 90 minutes. The helmet can shed 11 W for ever (7.4 W of that is the LEDs' own idle draw), and the 3000 J heat bucket only covers what goes above that. When songs run hotter, heat builds up song after song, and after about 20 minutes every hit in the rest of the set gets flattened by the guard. So besides the checks above, run `python3 $KIT/power.py "<base>"` and aim for a whole-song mean of 11.5 W or less, and never above 12.5 W. Heat at the end of the song should be under about 15%. Get there with contrast rather than by dimming everything: darker verses and breakdowns, fewer full-shell layers, more small lit shapes, ears dark between hits. Peaks can stay as high as they are. A dark helmet with one bright thing moving is both cheaper and better-looking than a washed-out one. Do not change any limit.


## Correction: previews before about 13:06 were flattering
`$KIT/sheet.py` used to skip the power guard. It now goes through the real guard, so anything judged by the old sheet must be judged again. What the guard does that matters: the shell region is capped near 300 mA (mean about 10 of 255) with a soft knee, so anything above about 64 comes out near 62 and hues shift; when the whole frame hits 1000 mA the governor sheds the shell hard, so on a big hit with loud ears the shell can go almost black, and full-shell white comes out gray. So on hits: dark ears on the first beat if the shell has the picture, or give the moment to the ears on purpose. `python3 $KIT/scenepower.py "<base>"` prints per scene the mA, how often the governor hit, shell an
... [cut] ...
      604    962     41    100     6.1    24.8     33  29.8%
squeal            638   1000     45    100     5.6    27.6     29  31.7%
squeal in         571    962     66    100     5.0    24.7     21  31.8%
tiring            404    633      2     62     9.0     7.5     38  32.4%
tiring in          66    105      0      0     2.2     0.0     53  32.4%
dozing             19     41      0      0     0.6     0.0     49  32.3%
last breath        52    122      0      0     1.7     0.0     56  30.7%
dark                0      0      0      0     0.0     0.0      0  30.6%
Sat Oct 31 13:08:32 PDT 2026
```

```
$ cd "~/deadmau5 app"; cat data/cal/power.json | head -60; grep -n "def apply" -A 110 mau5power.py | sed -n 1,190p
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
251-        # Only the LEDs both the frame an
... [cut] ...
     # So s may never be more than GOV_RISE e-folds per second above
340-        # the last frame's -- a compressor's slow release -- while a
341-        # smaller s still applies at once.  Never above the s solved for,
342-        # so never over budget; and it runs on frames under budget too,
343-        # or the climb back would be one jump.  Measured through the
344-        # phone's twin with the test suite's music drive, at 15 and 40
345-        # fps, where the governor binds -- blades, spectrum, the Dimension
346-        # Remix blades cue, beneath's split under a sparkle overlay -- it
```

```
$ cd "~/deadmau5 app"; cat data/cal/power.json | head -60; grep -n "def apply" -A 110 mau5power.py | sed -n 1,190p
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
251-        # Only the LEDs both the frame an
... [cut] ...
     # So s may never be more than GOV_RISE e-folds per second above
340-        # the last frame's -- a compressor's slow release -- while a
341-        # smaller s still applies at once.  Never above the s solved for,
342-        # so never over budget; and it runs on frames under budget too,
343-        # or the climb back would be one jump.  Measured through the
344-        # phone's twin with the test suite's music drive, at 15 and 40
345-        # fps, where the governor binds -- blades, spectrum, the Dimension
346-        # Remix blades cue, beneath's split under a sparkle overlay -- it
```
