# What the radio builder ran and saw

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
$ KIT=tools/showkit; cd "~/deadmau5 app"; mkdir -p "$KIT/work/radio"; cat "$KIT/fmt.py"; echo ------; cat "$KIT/grid.py"; echo ------; cat "$KIT/sheet.py"; echo -----; cat "$KIT/songmap.py"; echo -----; cat "$KIT/spectro.py"; echo -----; cat "$KIT/spritetry.py"; ls -la shows | head -60; ls -la shows/scenes | head -60
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
------
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
      from the earliest downbeat, deletes the stale an
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
$ KIT=tools/showkit; cd "~/deadmau5 app"; mkdir -p "$KIT/work/radio"; cat "$KIT/fmt.py"; echo ------; cat "$KIT/grid.py"; echo ------; cat "$KIT/sheet.py"; echo -----; cat "$KIT/songmap.py"; echo -----; cat "$KIT/spectro.py"; echo -----; cat "$KIT/spritetry.py"; ls -la shows | head -60; ls -la shows/scenes | head -60
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
------
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
      from the earliest downbeat, deletes the stale an
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
$ KIT=tools/showkit; cd "~/deadmau5 app"; time python3 "$KIT/grid.py" scan "shows/deadmau5 - Some Chords (Radio Edit).mp3" 2>&1 | tail -30; ffprobe -hide_banner "shows/deadmau5 - Some Chords (Radio Edit).mp3" 2>&1 | tail -12
estimator: 127.970 BPM, first bar 0.115 s, tempo lock 0.698, bar lock 0.3978648346095398; song 210.0 s
refined over the whole song: spb 0.468860 = 127.970 BPM
first half 127.996 BPM, second half 127.957 BPM (these should agree within 0.05)
phase of the music against that grid per 8 bars, ms (flat = right; one 16th = 117 ms; contrast under 1.15 means sparse, ignore it):
  0:+3(2.12)  8:+3(2.33)  16:+1(2.93)  24:-5(3.84)  32:-7(5.30)  40:-9(5.06)  48:-13(4.92)  56:-13(4.17)  64:-19(1.71)  72:+9(2.01)  80:+5(2.85)  88:+1(3.61)  96:-5(4.79)  104:-9(4.54)
change per beat position, estimator's bar 1 at 0.115 s: 0:0.85 1:0.58 2:0.71 3:0.60  (the highest is where bars really start, 0 = estimator is right)
strongest phrase positions, in beats mod 32 from that bar 1: 0(1.42), 16(1.40), 15(0.92), 17(0.89), 30(0.82), 18(0.79)
biggest single changes (time, beat from bar 1, beat mod 4): 51.7s b110 m2; 52.2s b111 m3; 52.6s b112 m0; 53.1s b113 m1; 59.2s b126 m2; 60.1s b128 m0; 67.6s b144 m0; 75.1s b160 m0; 112.2s b239 m3; 112.6s b240 m0; 113.1s b241 m1; 119.7s b255 m3; 120.1s b256 m0; 120.6s b257 m1; 135.1s b288 m0; 171.7s b366 m2; 172.2s b367 m3; 173.1s b369 m1; 187.7s b400 m0; 195.2s b416 m0; 200.8s b428 m0; 202.2s b431 m3; 202.7s b432 m0; 203.1s b433 m1
suggested next: grid.py fold with --spb 0.468860 --anchor 0.115, decide the bar line, then grid.py write
python3 "$KIT/grid.py" scan "shows/deadmau5 - Some Chords (Radio Edit).mp3" 2  1.47s user 0.62s system 92% cpu 2.251 total
tail -30  0.00s user 0.00s system 0% cpu 2.250 total
Input #0, mp3, from 'shows/deadmau5 - Some Chords (Radio Edit).mp3':
  Metadata:
    encoder         : Lavf58.20.100
  Duration: 00:03:30.00, start: 0.025057, bitrate: 320 kb/s
  Stream #0:0: Audio: mp3 (mp3float), 44100 Hz, stereo, fltp, 320 kb/s, start 0.025057
    Metadata:
      encoder         : Lavc58.35
```

```
$ KIT=tools/showkit; cd "~/deadmau5 app"; mkdir -p "$KIT/work/radio"; cat > "$KIT/work/radio/phase.py" <<'EOF'
import sys, os
KIT=os.environ.get("KIT")
sys.path.insert(0, KIT); sys.path.insert(0, os.getcwd())
import numpy as np, grid as G
mp3="shows/deadmau5 - Some Chords (Radio Edit).mp3"
d=G.env_of(mp3)
print("dur",float(d["dur"]))
for spb,anchor in [(0.46875,0.115),(0.468860,0.115)]:
    for span in (2,4):
        rows,t0=G.phase_table(d,spb,anchor,span_bars=span)
        print("spb",spb,"span",span)
        print("  "+"  ".join("%d:%+.0f(%.2f)"%r for r in rows))
# fine refine of 128 assumptio ... [cut]
dur 209.99836734693878
spb 0.46875 span 2
  0:-1(2.08)  2:+5(2.19)  4:+5(1.98)  6:+7(2.15)  8:+9(1.59)  10:+11(1.92)  12:+9(2.52)  14:+11(2.79)  16:+11(2.82)  18:+9(3.13)  20:+11(2.79)  22:+9(3.23)  24:+7(2.08)  26:+11(1.82)  28:+11(4.48)  30:+7(4.64)  32:+7(4.83)  34:+7(5.21)  36:+9(5.72)  38:+9(5.29)  40:+9(6.05)  42:+9(5.22)  44:+11(4.64)  46:+11(4.83)  48:+11(5.30)  50:+11(5.26)  52:+11(4.79)  54:+11(4.84)  56:+11(4.96)  58:+11(5.27)  60:+3(1.14)  62:-13(1.20)  64:+11(1.98)  66:+13(1.75)  68:+11(1.75)  70:+5(1.29)  72:-11(1.30)  74:+45(1.87)  76:+43(2.54)  78:+43(2.82)  80:+41(3.02)  82:+41(2.96)  84:+41(2.72)  86:+41(2.61)  88:+41(1.98)  90:+41(1.92)  92:+43(4.20)  94:+43(4.65)  96:+43(5.08)  98:+43(4.59)  100:+37(5.03)  102:+37(5.00)  104:+37(5.46)  106:+41(4.96)  108:+29(1.25)  110:+23(1.40)
spb 0.46875 span 4
  0:+3(2.19)  4:+5(2.06)  8:+11(1.79)  12:+11(2.74)  16:+11(2.98)  20:+11(2.98)  24:+7(1.99)  28:+7(4.70)  32:+7(5.35)  36:+9(5.51)  40:+9(5.45)  44:+11(4.74)  48:+11(5.02)  52:+11(4.81)  56:+11(5.11)  60:+3(1.12)  64:+13(1.92)  68:+11(1.52)  72:+45(1.34)  76:+43(2.70)  80:+41(2.99)  84:+41(2.69)  88:+41(1.91)  92:+43(4.37)  96:+43(5.10)  100:+37(4.99)  104:+37(5.23)  108:+29(1.25)
spb 0.46886 span 2
  0:-3(2.06)  2:+5(2.18)  4:+3(1.99)  6:+3(2.13)  8:+5(1.59)  10:+5(1.95)  12:+3(2.53)  14:+3(2.76)  16:+3(2.84)  18:+1(3.11)  20:+3(2.86)  22:-1(3.23)  24:-3(2.05)  26:-1(1.84)  28:-5(4.45)  30:-7(4.91)  32:-7(4.98)  34:-9(5.00)  36:-7(5.70)  38:-9(5.18)  40:-9(6.07)  42:-9(5.42)  44:-9(4.64)  46:-11(4.78)  48:-9(5.23)  50:-13(5.32)  52:-11(4.76)  54:-15(4.83)  56:-13(5.03)  58:-13(5.15)  60:-21(1.15)  62:-37(1.21)  64:-19(1.99)  66:-15(1.79)  68:-21(1.74)  70:-27(1.27)  72:-43(1.30)  74:+13(1.88)  76:+9(2.54)  78:+7(2.82)  80:+5(3.00)  82:+5(3.04)  84:+5(2.77
... [cut] ...
  28:-5(4.72)  32:-7(5.18)  36:-7(5.36)  40:-9(5.60)  44:-9(4.75)  48:-13(5.16)  52:-13(4.76)  56:-13(5.09)  60:-21(1.12)  64:-15(1.90)  68:-21(1.51)  72:+13(1.34)  76:+7(2.70)  80:+5(2.97)  84:+5(2.72)  88:+1(1.92)  92:+1(4.36)  96:-1(5.15)  100:-7(5.27)  104:-9(5.57)  108:-19(1.24)
0 30 bpm 127.974 spb 0.468844 phase 0.003
30 60 bpm 128.013 spb 0.468703 phase 30.009
60 90 bpm 127.987 spb 0.468797 phase 60.006
90 120 bpm 127.968 spb 0.468867 phase 90.006
120 150 bpm 127.834 spb 0.469359 phase 120.006
150 180 bpm 128.000 spb 0.468750 phase 150.039
180 210 bpm 128.000 spb 0.468750 phase 180.036
```

```
$ KIT=tools/showkit; cd "~/deadmau5 app"; python3 "$KIT/grid.py" fold "shows/deadmau5 - Some Chords (Radio Edit).mp3" --spb 0.46875 --anchor 0.124 --spans "0-8,8-16,16-24,24-28,28-44,44-56,56-60,60-64,64-68,68-72" ; python3 "$KIT/grid.py" fold "shows/deadmau5 - Some Chords (Radio Edit).mp3" --spb 0.46875 --anchor 0.124 --holds "33.9:0.031" --spans "72-76,76-84,84-92,92-100,100-108,108-112"
bar 0 at 0.124 s, 128.000 BPM, 111 bars
bars 0-8   (16 steps, | every beat; one row per band)
   sub     *:::|.-+:|::.:|.:@:   peak 0.51
   bass    +...|..-.|....|..@.   peak 0.53
   lowmid  *:..|:.=.|:::.|..@.   peak 0.46
   mid     =:::|::=:|:-.:|::@.   peak 0.27
   pres    +-=-|--+-|:=--|.=@-   peak 0.16
   air     -.=.|:-+.|:=-:|:-@.   peak 0.12
bars 8-16   (16 steps, | every beat; one row per band)
   sub     +=+-|#+=-|*=-=|#=@-   peak 0.26
   bass    #:::|@--.|@:-:|#.#:   peak 0.36
   lowmid  %:::|--*-|----|-=@-   peak 0.27
   mid     @-::|+-*-|@-::|#-#:   peak 0.24
   pres    +--.|%.=:|=--:|@-+:   peak 0.28
   air     @.: |% -.|@.:.|@ =    peak 0.51
bars 16-24   (16 steps, | every beat; one row per band)
   sub     *%++|=@*+|*@+-|@#*=   peak 0.24
   bass    @...|@:..|%:..|@::.   peak 0.77
   lowmid  @%=:|%%#-|%#=-|##@-   peak 0.25
   mid     @-..|*-:.|%-..|*-:.   peak 0.55
   pres    =-..|%::.|=-:.|@::.   peak 0.49
   air     @ : |@ : |@ . |@ -    peak 0.80
bars 24-28   (16 steps, | every beat; one row per band)
   sub     **#*|=*+#|=***|%@%-   peak 0.14
   bass    :.::|::::|:...|@==-   peak 0.26
   lowmid  ..::|:.-:|:..:|@:.:   peak 0.36
   mid     :.. |-.:.|-.. |@...   peak 0.44
   pres    @---|@-::|+-:.|@:=:   peak 0.20
   air     @:::|%.:.|+.:.|@.:.   peak 0.30
bars 28-44   (16 steps, | every beat; one row per band)
   sub     %.. |@ . |%.:*|. +:   peak 1.08
   bass    %...|@.: |@...|+.:    peak 1.37
   lowmid  %.: |@.= |@.-.|-.     peak 1.08
   mid     -.- |@.= |% = |=. .   peak 1.29
   pres    * - |@ - |% = |+      peak 1.54
   air     *.= |% + |@ + |+ .:   peak 1.36
bars 44-56   (16 steps, | every beat; one row per band)
   sub     % . |@ : |@..#|. +:   peak 1.10
   bass    @.. |@.. |@...|+.:    peak 1.37
   lowmid  %.: |@.: |@.:.|=. .   peak 1.07
   mid  
... [cut] ...
ry beat; one row per band)
   sub     # . |@ : |% .#|. +.   peak 1.10
   bass    @.: |@.. |@.:.|+.:    peak 1.28
   lowmid  #.: |@.: |@.:.|-:     peak 1.07
   mid     -.= |@.= |@.+ |+. .   peak 1.10
   pres    * = |@ = |@ = |*. .   peak 1.24
   air     *.*.|* +.|@.*.|+ .-   peak 1.28
bars 108-112   (16 steps, | every beat; one row per band)
   sub     @:. |    |    |       peak 0.07
   bass    @-@-|.==.|:: .|....   peak 0.10
   lowmid  ***+|:@=+|=+-=|-:--   peak 0.07
   mid     *%@*|#-++|++*:|-=--   peak 0.07
   pres    #+*#|@=-%|+=+=|++-:   peak 0.07
   air     @=*-|+.-:|*+--|=-:-   peak 0.06
```

```
$ KIT=tools/showkit; cd "~/deadmau5 app"; cat > "$KIT/work/radio/seam.py" <<'EOF'
import sys, os
KIT=os.environ.get("KIT")
sys.path.insert(0, KIT); sys.path.insert(0, os.getcwd())
import numpy as np, grid as G
mp3="shows/deadmau5 - Some Chords (Radio Edit).mp3"
d=G.env_of(mp3)
tt=d["tt"]; dt=tt[1]-tt[0]
spb=0.46875; t0=0.124
od=G.onsets(d)
# print the strongest onsets between bars 60 and 80, with the time relative to the nearest 16th of the pre-seam grid
s16=spb/4
th={}
for lo,hi in [(64,72),(72,76),(76,80)]:
    a=t0+lo*4*spb; b=t0+hi*4*spb
    idx=np.where((tt>=a)&(tt<b))[0]
    v=od[idx]
    # ... [cut]
bars 64 72
  t 121.765  bar 64.875  off 16th +1 ms  strength 1.08
  t 121.823  bar 64.906  off 16th -58 ms  strength 0.23
  t 122.021  bar 65.012  off 16th +22 ms  strength 0.22
  t 122.044  bar 65.024  off 16th +45 ms  strength 0.22
  t 122.358  bar 65.191  off 16th +7 ms  strength 0.22
  t 122.381  bar 65.204  off 16th +30 ms  strength 0.26
  t 122.868  bar 65.464  off 16th +49 ms  strength 0.21
  t 123.170  bar 65.625  off 16th -1 ms  strength 0.21
  t 123.646  bar 65.879  off 16th +7 ms  strength 0.84
  t 123.762  bar 65.940  off 16th +6 ms  strength 0.22
  t 124.587  bar 66.380  off 16th +10 ms  strength 0.95
  t 125.515  bar 66.875  off 16th +1 ms  strength 1.12
  t 127.628  bar 68.002  off 16th +4 ms  strength 1.36
  t 127.733  bar 68.058  off 16th -8 ms  strength 0.26
  t 128.046  bar 68.225  off 16th -46 ms  strength 0.21
  t 128.395  bar 68.411  off 16th -50 ms  strength 0.22
  t 128.650  bar 68.547  off 16th -29 ms  strength 0.22
  t 128.882  bar 68.671  off 16th -31 ms  strength 0.27
  t 129.033  bar 68.752  off 16th +3 ms  strength 0.27
  t 129.115  bar 68.795  off 16th -33 ms  strength 0.24
  t 129.265  bar 68.875  off 16th +1 ms  strength 0.68
  t 129.498  bar 68.999  off 16th -1 ms  strength 0.23
  t 129.521  bar 69.012  off 16th +22 ms  strength 0.22
  t 129.544  bar 69.024  off 16th +45 ms  strength 0.28
  t 129.567  bar 69.036  off 16th -49 ms  strength 0.24
  t 129.591  bar 69.049  off 16th -26 ms  strength 0.27
  t 130.032  bar 69.284  off 16th -53 ms  strength 0.25
  t 130.078  bar 69.309  off 16th -7 ms  strength 0.28
  t 130.612  bar 69.594  off 16th +59 ms  strength 0.21
  t 131.146  bar 69.879  off 16th +7 ms  strength 0.99
  t 131.262  bar 69.940  off 16th +6 ms  strength 0.22
  t 131.738  bar 70.194  off 16th +13 ms  strength 0.23
  t 131.762
... [cut] ...
ar 79.266  off 16th +29 ms  strength 1.62
  t 148.817  bar 79.303  off 16th -18 ms  strength 0.41
  t 149.002  bar 79.402  off 16th +50 ms  strength 0.37
  t 149.211  bar 79.513  off 16th +25 ms  strength 1.23
  t 149.293  bar 79.557  off 16th -11 ms  strength 0.29
  t 149.316  bar 79.569  off 16th +12 ms  strength 0.28
  t 149.339  bar 79.581  off 16th +35 ms  strength 0.38
  t 149.467  bar 79.650  off 16th +46 ms  strength 0.29
  t 149.687  bar 79.767  off 16th +32 ms  strength 1.72
  t 149.780  bar 79.817  off 16th +8 ms  strength 0.36
  t 149.931  bar 79.897  off 16th +42 ms  strength 0.49
```

```
$ KIT=tools/showkit; cd "~/deadmau5 app"; B="deadmau5 - Some Chords (Radio Edit)"; time python3 "$KIT/grid.py" write "$B" --spb 0.46875 --anchor 0.124 --holds "135.1:0.032" 2>&1 | tail -15; python3 "$KIT/grid.py" check "$B"; python3 "$KIT/songmap.py" "$B"; python3 "$KIT/spectro.py" "$B" "$KIT/work/radio/spec_all.png"; python3 mau5scene.py bars "$B" | head -60
    0:22.62-0:37.62  lvl1  sparkle    {}
    0:37.62-0:52.62  lvl1  matrix     {}
    0:52.62-1:00.12  lvl3  confetti   {'rate': 26.0}
    1:00.12-1:07.62  lvl3  blades     {'period': 1.875}
    1:07.62-1:15.12  lvl3  lightning  {'every': 1.1}
    1:15.12-1:22.62  lvl3  strobe     {'hz': 6.0}
    1:22.62-1:37.62  lvl2  rainbow    {'period': 6.0}
    1:37.62-1:52.62  lvl2  split      {'shell': 'plasma', 'ears': 'chase'}
    1:52.62-2:07.62  lvl1  wipe       {'period': 1.875, 'a': (255, 255, 255), 'b': (0, 200, 255)}
    2:07.62-2:22.66  lvl0  ripple     {'period': 3.4}
    2:22.66-2:37.66  lvl1  spiral     {'period': 6.0}
    2:37.66-2:52.66  lvl1  scanner    {'period': 3.75}
    2:52.66-3:07.66  lvl1  comet      {'period': 4.0}
    3:07.66-3:28.28  lvl1  breathe    {'period': 3.75}
wrote shows/scenes/deadmau5 - Some Chords (Radio Edit).beats: 448 beats, 112 bars, bar 0 at 0.124 s, 128.000 BPM
python3 "$KIT/grid.py" write "$B" --spb 0.46875 --anchor 0.124 --holds  2>&1  0.53s user 0.10s system 98% cpu 0.642 total
tail -15  0.00s user 0.00s system 0% cpu 0.642 total
deadmau5 - Some Chords (Radio Edit): 128.000 BPM, 112 bars, bar 0 at 0.124 s, holds [(135.156, 0.03200000000001069)]
music against the grid per 8 bars, ms (contrast): 0:-3(2.11)  8:+1(2.34)  16:+3(2.97)  24:-1(3.92)  32:-1(5.39)  40:+3(5.01)  48:+3(5.01)  56:+3(4.25)  64:+1(1.72)  72:+3(2.14)  80:+1(2.83)  88:+1(3.62)  96:-3(5.14)  104:-3(4.44)
worst 3 ms where the music is clear enough to say, mean +1.0 ms
deadmau5 - Some Chords (Radio Edit): 112 bars, 1.88 s a bar, 210.0 s
 bar     t   E  B  M  H  notes       change
   0    0.1   8  9  0  0  C A F       
   1    2.0   8  9  0  0  F C A       
   2    3.9   7  9  3  0  A C F       
   3    5.7   8  9  5  1  C A F       >>
   4    7.6   7  9  6  2  C A F      
... [cut] ...

    52    97.62s  energy 0.73  bass 0.73 (punch 1.00)  mid 0.58  high 0.70
    53    99.50s  energy 0.75  bass 0.76 (punch 1.00)  mid 0.59  high 0.70
    54   101.37s  energy 0.74  bass 0.72 (punch 1.00)  mid 0.59  high 0.70
    55   103.25s  energy 0.75  bass 0.77 (punch 1.00)  mid 0.63  high 0.71
    56   105.12s  energy 0.74  bass 0.74 (punch 1.00)  mid 0.58  high 0.70
    57   107.00s  energy 0.76  bass 0.76 (punch 1.00)  mid 0.59  high 0.70
    58   108.87s  energy 0.73  bass 0.73 (punch 1.00)  mid 0.58  high 0.70
    59   110.75s  energy 0.74  bass 0.84 (punch 1.00)  mid 0.72  high 0.77
```

```
$ KIT=tools/showkit; cd "~/deadmau5 app"; B="deadmau5 - Some Chords (Radio Edit)"; W="$KIT/work/radio"; python3 "$KIT/spectro.py" "$B" "$W/s_0_18.png" 0 18; python3 "$KIT/spectro.py" "$B" "$W/s_16_32.png" 16 32; python3 "$KIT/spectro.py" "$B" "$W/s_56_66.png" 56 66; python3 "$KIT/spectro.py" "$B" "$W/s_66_80.png" 66 80; python3 "$KIT/spectro.py" "$B" "$W/s_84_96.png" 84 96; python3 "$KIT/spectro.py" "$B" "$W/s_100_112.png" 100 112; python3 "$KIT/grid.py" fold "shows/$B.mp3" --spb 0.46875 --anchor 0.124 --spans "0-2,2-4,4-6,6-8,8-10,10-12,12-14,14-16,16-18,18-20,20-22,22-24,24-25,25-26,26-27,27-28 ... [cut]
tools/showkit/songs/radio/s_0_18.png
tools/showkit/songs/radio/s_16_32.png
tools/showkit/songs/radio/s_56_66.png
tools/showkit/songs/radio/s_66_80.png
tools/showkit/songs/radio/s_84_96.png
tools/showkit/songs/radio/s_100_112.png
bar 0 at 0.124 s, 128.000 BPM, 111 bars
bars 0-2   (16 steps, | every beat; one row per band)
   bass    +. .|.  .|  .:| .@:   peak 0.81
   lowmid  *:..|:...|:.:.|..@:   peak 0.71
   mid     . . |. . |....|..@    peak 0.35
   air     .   | :..|..: |::@.   peak 0.03
bars 2-4   (16 steps, | every beat; one row per band)
   bass    ..::| :#.|..  |  @    peak 0.54
   lowmid  ... |..@ | ...|. @    peak 0.43
   mid     -=:-|==@+|.*:=|=+@:   peak 0.20
   air     @==.|#-*.|%%%-|@=#+   peak 0.04
bars 4-6   (16 steps, | every beat; one row per band)
   bass    %.:.|-:.:|:..:|..@:   peak 0.52
   lowmid  @...|....|.:..| .@.   peak 0.63
   mid     @:..|=:-:|:=.:|:-%:   peak 0.33
   air     :.-.|:.- |:=-.|:-@.   peak 0.18
bars 6-8   (16 steps, | every beat; one row per band)
   bass    =.=-|:-+=|=---|--@:   peak 0.25
   lowmid  :..-|-.@:|-:-:|::-.   peak 0.28
   mid     :=:-|.=+.|:-::|::@:   peak 0.25
   air     -.+.|:=*.|.=::| -@.   peak 0.26
bars 8-10   (16 steps, | every beat; one row per band)
   bass    :.:.|:-..| .-:|..@.   peak 0.51
   lowm
... [cut] ...
.-    peak 1.57
   lowmid  *.. |@.: |@ +.|+.     peak 1.06
   mid     =:= |@.= |@.% |%: :   peak 0.69
   air     *.: |# - |@ = |+ :    peak 0.90
bars 29-30   (16 steps, | every beat; one row per band)
   bass    @.=.|@.: |# ..|=..    peak 1.52
   lowmid  %.. |#.- |@.. |:.     peak 1.23
   mid     -.- |@.= |# . |-      peak 1.36
   air     # = |@ + |@ -.|# :    peak 1.16
bars 30-32   (16 steps, | every beat; one row per band)
   bass    @.:.|@.: |@ .:|#.:    peak 1.40
   lowmid  %.- |@.. |@.. |-. :   peak 1.22
   mid     - - |@.- |% : |-  :   peak 1.42
   air     + - |@ - |@ : |= ..   peak 1.72
```

```
$ cd "~/deadmau5 app"; wc -l mau5scene.py mau5fx.py mau5engine.py mau5show.py mau5preview.py; grep -n "^def \|^class \|^    def " mau5scene.py | head -120
    1344 mau5scene.py
     992 mau5fx.py
    1388 mau5engine.py
    1000 mau5show.py
     214 mau5preview.py
    4938 total
125:class TreatmentError(ValueError):
132:def treatment_path(base):
136:def load_treatment(base_or_path):
151:def grid_of(music):
190:def src_of(base):
203:def _helmet():
210:def _edge_mm(h):
215:class _Compiler:
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
859:class _Val:
862:    def __init__(self, v):
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
1220:def _row(r):
1225:def print_marks(base, music):
1240:def check(base, fps=25.0, verbose=True):
1303:def main(argv=None):
1318:    def names(given):
```

```
$ cd "~/deadmau5 app"; sed -n 1,125p mau5scene.py
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
 that take
    # part, spread how far each LED's colour wanders from c.
    "twinkle": {"rate": 0.25, "sharp": 4.0, "spread": 0.0, "dens": 1.0},
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
```

```
$ cd "~/deadmau5 app"; sed -n 215,535p mau5scene.py
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
", ""),
                "grid": grid, "bars": nb, "pal": self.pal,
                "scenes": tiled, "hits": hits}


def _merge(a, b):
    """A shallow merge, except that `env` and `params` merge one level down."""
    out = dict(a)
    for k, v in (b or {}).items():
        if k in ("env", "params") and isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = dict(out[k], **v)
        else:
            out[k] = v
    return out


def _dark(b0, b1):
    return {"name": "dark", "from": float(b0), "to": float(b1), "out": 0.0,
            "pump": None, "layers": [], "_pal": None}
```

```
$ cd "~/deadmau5 app"; sed -n 596,790p mau5scene.py
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
$ cd "~/deadmau5 app"; sed -n 790,1200p mau5scene.py
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
$ cd "~/deadmau5 app"; sed -n 1200,1344p mau5scene.py
    e = np.clip(np.asarray(music.energy, float), 0, 1)
    edges = [int(float(t) * fps) for t in music.bars] + [int(music.duration * fps)]
    band = getattr(music, "band", None) or {}
    rows = []
    for i in range(len(music.bars)):
        a = min(max(edges[i], 0), len(e) - 1)
        b = min(max(edges[i + 1], a + 1), len(e))

        def mean(k, w):
            return float(np.mean(band[k][w][a:b])) if k in band else float("nan")

        def peak(k, w):
            return float(np.max(band[k][w][a:b])) if k in band else float("nan")
        rows.append({"bar": i, "t": float(music.bars[i]), "energy": float(e[a:b].mean()),
                     "bass": mean("bass", 0), "bassp": peak("bass", 1),
                     "mid": mean("mid", 0), "high": mean("high", 0),
                     "highp": peak("high", 1)})
    return rows


def _row(r):
    return ("  %4d  %7.2fs  energy %.2f  bass %.2f (punch %.2f)  mid %.2f  high %.2f"
            % (r["bar"], r["t"], r["energy"], r["bass"], r["bassp"], r["mid"], r["high"]))


def print_marks(base, music):
    tr = load_treatment(base)
    rows = bar_stats(music)
    c = _Compiler(tr, grid_of(music)[0], len(rows), _helmet())
    print("%s: marks against the bar map (bar-1, bar, bar+1)" % base)
    for k, v in sorted(c.marks.items(), key=lambda kv: kv[1]):
        print("  %-10s bar %g" % (k, v))
        for b in (int(math.floor(v)) - 1, int(math.floor(v)), int(math.floor(v)) + 1):
            if 0 <= b < len(rows):
                print("  " + _row(rows[b]))


# ----------------------------------------------------------------------
# check: the whole song through the power guard
# ----------------------------------------------------------------------
def check(base, fps=25.0, verbose=True):
    """Render a whole song through Sce
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
$ cd "~/deadmau5 app"; sed -n 1,125p mau5scene.py
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
 that take
    # part, spread how far each LED's colour wanders from c.
    "twinkle": {"rate": 0.25, "sharp": 4.0, "spread": 0.0, "dens": 1.0},
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
```

```
$ cd "~/deadmau5 app"; sed -n 215,535p mau5scene.py
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
", ""),
                "grid": grid, "bars": nb, "pal": self.pal,
                "scenes": tiled, "hits": hits}


def _merge(a, b):
    """A shallow merge, except that `env` and `params` merge one level down."""
    out = dict(a)
    for k, v in (b or {}).items():
        if k in ("env", "params") and isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = dict(out[k], **v)
        else:
            out[k] = v
    return out


def _dark(b0, b1):
    return {"name": "dark", "from": float(b0), "to": float(b1), "out": 0.0,
            "pump": None, "layers": [], "_pal": None}
```

```
$ cd "~/deadmau5 app"; sed -n 596,790p mau5scene.py
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
$ cd "~/deadmau5 app"; sed -n 790,1200p mau5scene.py
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
$ cd "~/deadmau5 app"; sed -n 1200,1344p mau5scene.py
    e = np.clip(np.asarray(music.energy, float), 0, 1)
    edges = [int(float(t) * fps) for t in music.bars] + [int(music.duration * fps)]
    band = getattr(music, "band", None) or {}
    rows = []
    for i in range(len(music.bars)):
        a = min(max(edges[i], 0), len(e) - 1)
        b = min(max(edges[i + 1], a + 1), len(e))

        def mean(k, w):
            return float(np.mean(band[k][w][a:b])) if k in band else float("nan")

        def peak(k, w):
            return float(np.max(band[k][w][a:b])) if k in band else float("nan")
        rows.append({"bar": i, "t": float(music.bars[i]), "energy": float(e[a:b].mean()),
                     "bass": mean("bass", 0), "bassp": peak("bass", 1),
                     "mid": mean("mid", 0), "high": mean("high", 0),
                     "highp": peak("high", 1)})
    return rows


def _row(r):
    return ("  %4d  %7.2fs  energy %.2f  bass %.2f (punch %.2f)  mid %.2f  high %.2f"
            % (r["bar"], r["t"], r["energy"], r["bass"], r["bassp"], r["mid"], r["high"]))


def print_marks(base, music):
    tr = load_treatment(base)
    rows = bar_stats(music)
    c = _Compiler(tr, grid_of(music)[0], len(rows), _helmet())
    print("%s: marks against the bar map (bar-1, bar, bar+1)" % base)
    for k, v in sorted(c.marks.items(), key=lambda kv: kv[1]):
        print("  %-10s bar %g" % (k, v))
        for b in (int(math.floor(v)) - 1, int(math.floor(v)), int(math.floor(v)) + 1):
            if 0 <= b < len(rows):
                print("  " + _row(rows[b]))


# ----------------------------------------------------------------------
# check: the whole song through the power guard
# ----------------------------------------------------------------------
def check(base, fps=25.0, verbose=True):
    """Render a whole song through Sce
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
$ cd "~/deadmau5 app"; grep -n "sprites.json\|SPRITES\b" *.py | head -20; git diff --stat -- mau5fx.py | tail -3; grep -n "class Sprite" -A70 mau5fx.py | head -150; grep -n "\"tiki\"" -A24 mau5fx.py | head -60
mau5engine.py:35:from mau5fx import FONT5x7, SPRITES
mau5engine.py:625:    rows = SPRITES[name]
mau5fx.py:134:SPRITES = {
mau5fx.py:249:# Sprites a song brings with it: shows/scenes/<song>.sprites.json, {name: [rows]},
mau5fx.py:256:        sheets = sorted(f for f in os.listdir(d) if f.endswith(".sprites.json"))
mau5fx.py:266:                SPRITES[name] = list(rows)
mau5fx.py:275:    rows = SPRITES[name_or_rows] if isinstance(name_or_rows, str) else name_or_rows
mau5fx.py:989:    for name in sorted(SPRITES):
mau5scene.py:640:    from mau5fx import SPRITES
mau5scene.py:726:                    if one not in SPRITES:
mau5offline.py:73:    from mau5fx import FONT5x7, SPRITES
mau5offline.py:96:            "sprites": {k: list(v) for k, v in SPRITES.items()},
 mau5fx.py | 47 +++++++++++++++++++++++++++++++++++++++++++++++
 1 file changed, 47 insertions(+)
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
587-    def __init__(self, helmet, sprites=("eyes", "wink"), fps=2.0, col=None,
588-                 row_from_top=3, color=(
... [cut] ...
XX...XX.",
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
169-        "XXXXXXX...XXXXXXX",
170-        "XXXXXXX...XXXXXXX",
```

```
$ cd "~/deadmau5 app"; cat > /tmp/null 2>/dev/null; python3 - <<'EOF'
import sys
sys.path.insert(0,'.')
import numpy as np, mau5engine as E
h=E.Helmet()
print("n",h.n)
for nm,m in [("shell",h.shell),("ear1",h.ear1),("ear2",h.ear2),("rims",h.rims),("tubes",h.tubes)]:
    m=np.asarray(m,bool)
    print(nm,m.sum(),"px %.0f..%.0f py %.0f..%.0f"%(h.px[m].min(),h.px[m].max(),h.py[m].min(),h.py[m].max()),
          "nfa %.2f..%.2f nel %.2f..%.2f er %.2f..%.2f ea %.2f..%.2f"%(h.nfa[m].min(),h.nfa[m].max(),h.nel[m].min(),h.nel[m].max(),h.er[m].min(),h.er[m].max(),h.ea[m].min(),h.ea[m].max()))
s=np.asarray(h.shell,bool)
# histogram of shell LED y
print("shell y hist")
hist,edges=np.histogram( ... [cut]
Command did not complete within its 120s timeout and was moved to the background (ID: b4h4g2mr1). Output is being written to: /private/tmp/claude-501/-Users-jones-deadmau5-app/208332e7-8c9f-4c25-bc21-e9a9df98fa1f/tasks/b4h4g2mr1.output. If it exits while you are still working you will be notified, but it is terminated when you give your final response and no notification can follow that — so do not end your turn to wait for it; if you need its result, wait for it before giving your final response. To check interim output, use Read on that file path.
Session cwd remains ~/deadmau5 app; directory changes made by the backgrounded command do not apply to subsequent commands.
```

```
$ cd "~/deadmau5 app"; grep -n "sprites.json\|SPRITES\b" *.py | head -20; git diff --stat -- mau5fx.py | tail -3; grep -n "class Sprite" -A70 mau5fx.py | head -150; grep -n "\"tiki\"" -A24 mau5fx.py | head -60
mau5engine.py:35:from mau5fx import FONT5x7, SPRITES
mau5engine.py:625:    rows = SPRITES[name]
mau5fx.py:134:SPRITES = {
mau5fx.py:249:# Sprites a song brings with it: shows/scenes/<song>.sprites.json, {name: [rows]},
mau5fx.py:256:        sheets = sorted(f for f in os.listdir(d) if f.endswith(".sprites.json"))
mau5fx.py:266:                SPRITES[name] = list(rows)
mau5fx.py:275:    rows = SPRITES[name_or_rows] if isinstance(name_or_rows, str) else name_or_rows
mau5fx.py:989:    for name in sorted(SPRITES):
mau5scene.py:640:    from mau5fx import SPRITES
mau5scene.py:726:                    if one not in SPRITES:
mau5offline.py:73:    from mau5fx import FONT5x7, SPRITES
mau5offline.py:96:            "sprites": {k: list(v) for k, v in SPRITES.items()},
 mau5fx.py | 47 +++++++++++++++++++++++++++++++++++++++++++++++
 1 file changed, 47 insertions(+)
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
587-    def __init__(self, helmet, sprites=("eyes", "wink"), fps=2.0, col=None,
588-                 row_from_top=3, color=(
... [cut] ...
XX...XX.",
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
169-        "XXXXXXX...XXXXXXX",
170-        "XXXXXXX...XXXXXXX",
```

```
$ cd "~/deadmau5 app"; cat > /tmp/null 2>/dev/null; python3 - <<'EOF'
import sys
sys.path.insert(0,'.')
import numpy as np, mau5engine as E
h=E.Helmet()
print("n",h.n)
for nm,m in [("shell",h.shell),("ear1",h.ear1),("ear2",h.ear2),("rims",h.rims),("tubes",h.tubes)]:
    m=np.asarray(m,bool)
    print(nm,m.sum(),"px %.0f..%.0f py %.0f..%.0f"%(h.px[m].min(),h.px[m].max(),h.py[m].min(),h.py[m].max()),
          "nfa %.2f..%.2f nel %.2f..%.2f er %.2f..%.2f ea %.2f..%.2f"%(h.nfa[m].min(),h.nfa[m].max(),h.nel[m].min(),h.nel[m].max(),h.er[m].min(),h.er[m].max(),h.ea[m].min(),h.ea[m].max()))
s=np.asarray(h.shell,bool)
# histogram of shell LED y
print("shell y hist")
hist,edges=np.histogram( ... [cut]
Command did not complete within its 120s timeout and was moved to the background (ID: b4h4g2mr1). Output is being written to: /private/tmp/claude-501/-Users-jones-deadmau5-app/208332e7-8c9f-4c25-bc21-e9a9df98fa1f/tasks/b4h4g2mr1.output. If it exits while you are still working you will be notified, but it is terminated when you give your final response and no notification can follow that — so do not end your turn to wait for it; if you need its result, wait for it before giving your final response. To check interim output, use Read on that file path.
Session cwd remains ~/deadmau5 app; directory changes made by the backgrounded command do not apply to subsequent commands.
```

```
$ ps -ax -o pid,ppid,etime,command | grep -E "[ /]cat$" | head; ls -la /tmp/null 2>/dev/null; date
81451 81450       02:05 cat
-rw-r--r--@ 1 jones  wheel  0 Oct 31 12:41 /tmp/null
Sat Oct 31 12:43:27 PDT 2026
```

```
$ ps -ax -o pid,ppid,etime,command | grep -E "[ /]cat$" | head; ls -la /tmp/null 2>/dev/null; date
81451 81450       02:05 cat
-rw-r--r--@ 1 jones  wheel  0 Oct 31 12:41 /tmp/null
Sat Oct 31 12:43:27 PDT 2026
```

```
$ rm -f /tmp/null; KIT=tools/showkit; cd "~/deadmau5 app"; cat > "$KIT/work/radio/geom.py" <<'EOF'
import sys
sys.path.insert(0,'.')
import numpy as np, mau5engine as E
h=E.Helmet()
print("n",h.n)
for nm,m in [("shell",h.shell),("ear1",h.ear1),("ear2",h.ear2),("rims",h.rims),("tubes",h.tubes)]:
    m=np.asarray(m,bool)
    print(nm,m.sum(),"px %.0f..%.0f py %.0f..%.0f"%(h.px[m].min(),h.px[m].max(),h.py[m].min(),h.py[m].max()),
          "nfa %.2f..%.2f nel %.2f..%.2f er %.2f..%.2f ea %.2f..%.2f"%(h.nfa[m].min(),h.nfa[m].max(),h.nel[m].min(),h.nel[m].max(),h.er[m].min(),h.er[m].max(),h.ea[m].min() ... [cut]
n 621
shell 398 px -171..171 py -111..168 nfa 0.16..0.84 nel 0.00..1.00 er 0.04..1.00 ea 0.00..0.99
ear1 112 px -388..-56 py 52..384 nfa 0.00..0.36 nel 0.45..0.95 er 0.03..1.00 ea 0.01..1.00
ear2 111 px 56..387 py 55..385 nfa 0.64..1.00 nel 0.44..0.95 er 0.04..1.00 ea 0.02..1.00
rims 37 px -388..387 py 52..385 nfa 0.00..1.00 nel 0.44..0.95 er 0.91..1.00 ea 0.02..1.00
tubes 186 px -349..358 py 67..349 nfa 0.02..0.99 nel 0.49..0.89 er 0.03..0.86 ea 0.01..1.00
shell y hist
  y -110.. -90:  20
  y  -90.. -70:  16
  y  -70.. -50:  20
  y  -50.. -30:   6
  y  -30.. -10:   2
  y  -10..  10:   0
  y   10..  30:  14
  y   30..  50:  22
  y   50..  70:  34
  y   70..  90:  34
  y   90.. 110:  68
  y  110.. 130:  60
  y  130.. 150:  51
  y  150.. 170:  21
shell x hist
  x -200..-175:   0
  x -175..-150:  31
  x -150..-125:  40
  x -125..-100:  36
  x -100.. -75:  26
  x  -75.. -50:  26
  x  -50.. -25:  21
  x  -25..   0:  20
  x    0..  25:  20
  x   25..  50:  21
  x   50..  75:  24
  x   75.. 100:  26
  x  100.. 125:  36
  x  125.. 150:  40
  x  150.. 175:  31
  x  175.. 200:   0
Traceback (most recent call last):
  File "tools/showkit/songs/radio/geom.py", line 23, in <module>
    grid[H-1-y][x]=ch
IndexError: list assignment index out of range
}


def _digit_bitmap(ch):
    rows = DIGIT3x5.get(ch, DIGIT3x5["0"])
    return np.array([[c != " " for c in r] for r in rows], bool)


def _glyph_bitmap(ch):
    """One 5x7 character as a (7, 5) bool array."""
    g = FONT5x7.get(ch.upper(), FONT5x7.get("?", (0, 0, 0, 0, 0)))
    return np.array([[(c >> r) & 1 for c in g] for r in range(7)], bool)


def _sprite_bitmap(name):
    rows = SPRITES[name]
    return np.array([[c != "." for c in r] for r in
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
$ rm -f /tmp/null; KIT=tools/showkit; cd "~/deadmau5 app"; cat > "$KIT/work/radio/geom.py" <<'EOF'
import sys
sys.path.insert(0,'.')
import numpy as np, mau5engine as E
h=E.Helmet()
print("n",h.n)
for nm,m in [("shell",h.shell),("ear1",h.ear1),("ear2",h.ear2),("rims",h.rims),("tubes",h.tubes)]:
    m=np.asarray(m,bool)
    print(nm,m.sum(),"px %.0f..%.0f py %.0f..%.0f"%(h.px[m].min(),h.px[m].max(),h.py[m].min(),h.py[m].max()),
          "nfa %.2f..%.2f nel %.2f..%.2f er %.2f..%.2f ea %.2f..%.2f"%(h.nfa[m].min(),h.nfa[m].max(),h.nel[m].min(),h.nel[m].max(),h.er[m].min(),h.er[m].max(),h.ea[m].min() ... [cut]
n 621
shell 398 px -171..171 py -111..168 nfa 0.16..0.84 nel 0.00..1.00 er 0.04..1.00 ea 0.00..0.99
ear1 112 px -388..-56 py 52..384 nfa 0.00..0.36 nel 0.45..0.95 er 0.03..1.00 ea 0.01..1.00
ear2 111 px 56..387 py 55..385 nfa 0.64..1.00 nel 0.44..0.95 er 0.04..1.00 ea 0.02..1.00
rims 37 px -388..387 py 52..385 nfa 0.00..1.00 nel 0.44..0.95 er 0.91..1.00 ea 0.02..1.00
tubes 186 px -349..358 py 67..349 nfa 0.02..0.99 nel 0.49..0.89 er 0.03..0.86 ea 0.01..1.00
shell y hist
  y -110.. -90:  20
  y  -90.. -70:  16
  y  -70.. -50:  20
  y  -50.. -30:   6
  y  -30.. -10:   2
  y  -10..  10:   0
  y   10..  30:  14
  y   30..  50:  22
  y   50..  70:  34
  y   70..  90:  34
  y   90.. 110:  68
  y  110.. 130:  60
  y  130.. 150:  51
  y  150.. 170:  21
shell x hist
  x -200..-175:   0
  x -175..-150:  31
  x -150..-125:  40
  x -125..-100:  36
  x -100.. -75:  26
  x  -75.. -50:  26
  x  -50.. -25:  21
  x  -25..   0:  20
  x    0..  25:  20
  x   25..  50:  21
  x   50..  75:  24
  x   75.. 100:  26
  x  100.. 125:  36
  x  125.. 150:  40
  x  150.. 175:  31
  x  175.. 200:   0
Traceback (most recent call last):
  File "tools/showkit/songs/radio/geom.py", line 23, in <module>
    grid[H-1-y][x]=ch
IndexError: list assignment index out of range
}


def _digit_bitmap(ch):
    rows = DIGIT3x5.get(ch, DIGIT3x5["0"])
    return np.array([[c != " " for c in r] for r in rows], bool)


def _glyph_bitmap(ch):
    """One 5x7 character as a (7, 5) bool array."""
    g = FONT5x7.get(ch.upper(), FONT5x7.get("?", (0, 0, 0, 0, 0)))
    return np.array([[(c >> r) & 1 for c in g] for r in range(7)], bool)


def _sprite_bitmap(name):
    rows = SPRITES[name]
    return np.array([[c != "." for c in r] for r in
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
$ KIT=tools/showkit; cd "~/deadmau5 app"; sed -i '' 's/xmin,xmax=-320,330; ymin,ymax=-110,295/xmin,xmax=-395,395; ymin,ymax=-115,390/; s/W=90;H=34/W=110;H=44/' "$KIT/work/radio/geom.py"; python3 "$KIT/work/radio/geom.py" | sed -n '32,200p'; grep -n "class SpriteFit\|name = \"sprite\"\|name = \"eyes\"" mau5engine.py; sed -n "$(grep -n 'name = "sprite"' mau5engine.py | cut -d: -f1),+55p" mau5engine.py; head -3 "shows/scenes/deadmau5 - The Veldt.beats"; ls shows/scenes | head -50
  x   25..  50:  21
  x   50..  75:  24
  x   75.. 100:  26
  x  100.. 125:  36
  x  125.. 150:  40
  x  150.. 175:  31
  x  175.. 200:   0
                                                                                                              
                     o     o                                                        o                         
                                o                                           o               o                 
                                                                                                o             
          o          2  22             o                             o                22                      
                       2  2                                                        2 2                        
      o                 22 22                                                    2 2                          
                              2                                                2  2                   o       
           1                2  2            o                   o             2  2                1           
            1                 2 2                                           2  2                 1            
   o         11 1              2  2                                        2  2                1         o    
              1                  2 2                          o         2  2                 1                
                11                   2        o                        2  2                11                 
                   1                2 2                              2   2               11                   
                    111               2 2                          2  22                1                 
... [cut] ...
mber.beats
TIKI TIKI - Slowed.beats
TIKI TIKI - Slowed.scene.json
beneath (with raxaj).beats
beneath (with raxaj).scene.json
deadmau5 & Wolfgang Gartner - Animal Rights.beats
deadmau5 - FN Pig.beats
deadmau5 - Ghosts n Stuff (Nero Remix).beats
deadmau5 - Ghosts n Stuff (Nero Remix).scene.json
deadmau5 - Harder Better Faster Stronger.beats
deadmau5 - Moar Ghosts n Stuff.beats
deadmau5 - Some Chords (Radio Edit).beats
deadmau5 - Some Chords.beats
deadmau5 - Strobe (Dimension Remix).scene.json
deadmau5 - Strobe (Special Features Remix).beats
deadmau5 - Strobe.scene.json
deadmau5 - The Veldt.beats
```

```
$ KIT=tools/showkit; cd "~/deadmau5 app"; B="deadmau5 - Some Chords (Radio Edit)"; W="$KIT/work/radio"; python3 "$KIT/spectro.py" "$B" "$W/s_27_30.png" 27 30; python3 "$KIT/spectro.py" "$B" "$W/s_58_60.png" 58 61; python3 "$KIT/spectro.py" "$B" "$W/s_106_108.png" 106 109; cat > "$W/curves.py" <<'EOF'
import sys, os, json
sys.path.insert(0, os.getcwd())
import numpy as np, mau5show
base="deadmau5 - Some Chords (Radio Edit)"
show=json.load(open("shows/%s.json"%base))
music=mau5show._music_for(show,"shows/%s.mp3"%base)
print([k for k in dir(music) if not k.startswith('__')][:40])
g=show.get("scenes" ... [cut]
tools/showkit/songs/radio/s_27_30.png
tools/showkit/songs/radio/s_58_60.png
tools/showkit/songs/radio/s_106_108.png
['_bar_levels', 'analysed', 'band', 'band_at', 'bands', 'bands_at', 'bar_shape', 'bars', 'beat_index', 'beat_phase', 'beats', 'bpm', 'centroid_at', 'chroma', 'duration', 'energy', 'fps', 'is_downbeat', 'level_at', 'levels', 'lock_conf', 'onset', 'path', 'pitch_at', 'sections', 'shape']
grid None
bar 1.0
  bass  env   0.92 0.91 0.86 0.88 0.90 0.89 0.86 0.85 0.88 0.83 0.82 0.84 0.85 0.86 0.20 0.84
  bass  punch 0.14 0.04 0.02 0.05 0.02 0.15 0.04 0.16 0.11 0.03 0.03 0.18 0.10 0.30 0.20 0.37
  mid   env   0.00 0.02 0.01 0.05 0.03 0.08 0.00 0.09 0.12 0.07 0.12 0.03 0.17 0.11 0.00 0.17
  mid   punch 0.07 0.06 0.10 0.03 0.17 0.06 0.04 0.06 0.09 0.18 0.07 0.07 0.12 0.06 0.80 0.25
  high  env   0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00
  high  punch 0.01 0.02 0.00 0.01 0.00 0.02 0.01 0.01 0.01 0.02 0.01 0.02 0.01 0.02 0.03 0.02
bar 4.0
  bass  env   0.20 0.92 0.93 0.91 0.90 0.90 0.89 0.88 0.88 0.88 0.88 0.86 0.85 0.86 0.56 0.88
  bass  punch 0.00 0.37 0.11 0.03 0.05 0.04 0.04 0.02 0.06 0.03 0.03 0.01 0.04 0.03 0.03 0.32
  mid   env   0.00 0.67 0.65 0.66 0.64 0.62 0.64 0.57 0.64 0.59 0.67 0.59 0.65 0.60 0.16 0.60
  mid   punch 0.01 0.37 0.11 0.20 0.18 0.12 0.07 0.07 0.13 0.04 0.11 0.08 0.17 0.15 0.14 0.28
  high  env   0.12 0.19 0.17 0.21 0.14 0.19 0.19 0.18 0.16 0.18 0.18 0.21 0.18 0.20 0.12 0.18
  high  punch 0.01 0.10 0.03 0.09 0.06 0.05 0.13 0.05 0.03 0.03 0.02 0.02 0.
... [cut] ...
2 0.04 0.07 0.16 0.06 0.04
bar 108.0
  bass  env   0.92 0.42 0.43 0.44 0.26 0.29 0.14 0.20 0.24 0.24 0.15 0.16 0.13 0.24 0.19 0.23
  bass  punch 0.33 0.23 0.19 0.13 0.05 0.27 0.08 0.14 0.24 0.09 0.19 0.07 0.04 0.08 0.05 0.15
  mid   env   0.83 0.84 0.77 0.63 0.58 0.65 0.58 0.64 0.60 0.58 0.60 0.56 0.58 0.60 0.54 0.57
  mid   punch 0.07 0.17 0.06 0.07 0.11 0.15 0.07 0.07 0.07 0.12 0.10 0.04 0.04 0.14 0.09 0.06
  high  env   0.80 0.91 0.87 0.85 0.81 0.83 0.81 0.78 0.79 0.76 0.76 0.72 0.72 0.72 0.71 0.67
  high  punch 0.05 0.05 0.02 0.05 0.03 0.04 0.04 0.06 0.04 0.02 0.03 0.03 0.07 0.02 0.01 0.01
```

```
$ KIT=tools/showkit; cd "~/deadmau5 app"; B="deadmau5 - Some Chords (Radio Edit)"; W="$KIT/work/radio"; python3 "$KIT/spectro.py" "$B" "$W/s_27_30.png" 27 30; python3 "$KIT/spectro.py" "$B" "$W/s_58_60.png" 58 61; python3 "$KIT/spectro.py" "$B" "$W/s_106_108.png" 106 109; cat > "$W/curves.py" <<'EOF'
import sys, os, json
sys.path.insert(0, os.getcwd())
import numpy as np, mau5show
base="deadmau5 - Some Chords (Radio Edit)"
show=json.load(open("shows/%s.json"%base))
music=mau5show._music_for(show,"shows/%s.mp3"%base)
print([k for k in dir(music) if not k.startswith('__')][:40])
g=show.get("scenes" ... [cut]
tools/showkit/songs/radio/s_27_30.png
tools/showkit/songs/radio/s_58_60.png
tools/showkit/songs/radio/s_106_108.png
['_bar_levels', 'analysed', 'band', 'band_at', 'bands', 'bands_at', 'bar_shape', 'bars', 'beat_index', 'beat_phase', 'beats', 'bpm', 'centroid_at', 'chroma', 'duration', 'energy', 'fps', 'is_downbeat', 'level_at', 'levels', 'lock_conf', 'onset', 'path', 'pitch_at', 'sections', 'shape']
grid None
bar 1.0
  bass  env   0.92 0.91 0.86 0.88 0.90 0.89 0.86 0.85 0.88 0.83 0.82 0.84 0.85 0.86 0.20 0.84
  bass  punch 0.14 0.04 0.02 0.05 0.02 0.15 0.04 0.16 0.11 0.03 0.03 0.18 0.10 0.30 0.20 0.37
  mid   env   0.00 0.02 0.01 0.05 0.03 0.08 0.00 0.09 0.12 0.07 0.12 0.03 0.17 0.11 0.00 0.17
  mid   punch 0.07 0.06 0.10 0.03 0.17 0.06 0.04 0.06 0.09 0.18 0.07 0.07 0.12 0.06 0.80 0.25
  high  env   0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00
  high  punch 0.01 0.02 0.00 0.01 0.00 0.02 0.01 0.01 0.01 0.02 0.01 0.02 0.01 0.02 0.03 0.02
bar 4.0
  bass  env   0.20 0.92 0.93 0.91 0.90 0.90 0.89 0.88 0.88 0.88 0.88 0.86 0.85 0.86 0.56 0.88
  bass  punch 0.00 0.37 0.11 0.03 0.05 0.04 0.04 0.02 0.06 0.03 0.03 0.01 0.04 0.03 0.03 0.32
  mid   env   0.00 0.67 0.65 0.66 0.64 0.62 0.64 0.57 0.64 0.59 0.67 0.59 0.65 0.60 0.16 0.60
  mid   punch 0.01 0.37 0.11 0.20 0.18 0.12 0.07 0.07 0.13 0.04 0.11 0.08 0.17 0.15 0.14 0.28
  high  env   0.12 0.19 0.17 0.21 0.14 0.19 0.19 0.18 0.16 0.18 0.18 0.21 0.18 0.20 0.12 0.18
  high  punch 0.01 0.10 0.03 0.09 0.06 0.05 0.13 0.05 0.03 0.03 0.02 0.02 0.
... [cut] ...
2 0.04 0.07 0.16 0.06 0.04
bar 108.0
  bass  env   0.92 0.42 0.43 0.44 0.26 0.29 0.14 0.20 0.24 0.24 0.15 0.16 0.13 0.24 0.19 0.23
  bass  punch 0.33 0.23 0.19 0.13 0.05 0.27 0.08 0.14 0.24 0.09 0.19 0.07 0.04 0.08 0.05 0.15
  mid   env   0.83 0.84 0.77 0.63 0.58 0.65 0.58 0.64 0.60 0.58 0.60 0.56 0.58 0.60 0.54 0.57
  mid   punch 0.07 0.17 0.06 0.07 0.11 0.15 0.07 0.07 0.07 0.12 0.10 0.04 0.04 0.14 0.09 0.06
  high  env   0.80 0.91 0.87 0.85 0.81 0.83 0.81 0.78 0.79 0.76 0.76 0.72 0.72 0.72 0.71 0.67
  high  punch 0.05 0.05 0.02 0.05 0.03 0.04 0.04 0.06 0.04 0.02 0.03 0.03 0.07 0.02 0.01 0.01
```

```
$ cd "~/deadmau5 app"; sed -n 538,595p mau5scene.py; sed -n 1,80p mau5preview.py; grep -n "guard\|def frame" mau5show.py | head -40
def compile_treatment(tr, grid, bars, h=None, src=""):
    """A treatment, resolved against a grid, into the show's `scenes`.

    Pure: nothing here reads a file, so the synthetic test can hand it a
    made-up grid and the build can hand it the analysis it just made.
    """
    c = _Compiler(tr, grid, bars, h or _helmet())
    out = c.compile()
    out["src"] = src
    return out


def compile_for(base, music):
    """The treatment for `base`, compiled against this analysis."""
    return compile_treatment(load_treatment(base), *grid_of(music), src=src_of(base))


def _show_and_music(base):
    import mau5show
    path = os.path.join(SHOWS, base + ".json")
    with open(path) as f:
        show = json.load(f)
    music = mau5show._music_for(show, os.path.join(HERE, show.get("track", "")))
    if music is None:
        raise TreatmentError("%s has no analysis to compile against" % base)
    return show, music, path


def compile_show(base, verbose=False):
    """Load the show and its analysis, compile its treatment, and lint it."""
    show, music, _ = _show_and_music(base)
    spec = compile_for(base, music)
    errs, warns = lint(spec, _helmet(), music=music)
    if verbose:
        for w in warns:
            print("  warning: %s" % w)
    if errs:
        raise TreatmentError("%s does not pass:\n  %s" % (base, "\n  ".join(errs)))
    return spec


def attach(base, verbose=True):
    """Compile, lint, and write the result into shows/<base>.json."""
    show, music, path = _show_and_music(base)
    spec = compile_show(base, verbose=verbose)
    show["scenes"] = spec
    with open(path, "w") as f:
        json.dump(show, f, indent=1)
    if verbose:
        print("%s: %d scenes, %d hits, written into %s"
              % (base, len(spec["scenes"]), len(spec["hits"]),

... [cut] ...
at32)

    def frame(self, rgb, gain=1.0):
        buf = self.back.copy()
        order = np.argsort(self.z)          # ears (behind) first
        for i in order:
606:    """The beat pulse at beat phase `ph`: at most 1, applied after the guard.
613:    same peak, which is the guarded frame itself; only the gaps between
684:        # It also costs nothing.  The guard clamps the top anyway, so
769:    def frame(self, t):
806:            # what the power guard exists to take away again -- the
811:            # frame to apply after the guard: the beat is the frame at
912:    if pix.guard is None:
```

```
$ KIT=tools/showkit; W="$KIT/work/radio"; cat > "$W/lab.py" <<'EOF'
"""lab.py: try raw layers on the helmet without touching the show. Used from small scripts."""
import sys, os, json
sys.path.insert(0, os.getcwd())
import numpy as np, mau5engine as E, mau5preview as PV, mau5scene as S, mau5show
from PIL import Image, ImageDraw
BASE="deadmau5 - Some Chords (Radio Edit)"
_h=None;_sc=None;_music=None
def env():
    global _h,_sc,_music
    if _h is None:
        _h=E.Helmet(); _sc=PV.Scene(_h)
        show=json.load(open("shows/%s.json"%BASE))
        _music=mau5show._music_for(show,"shows/%s.mp3"%BASE)
    r ... [cut]
shell lowest er: [(-7, 61, 0.039, 0.411), (7, 61, 0.042, 0.083), (-7, 76, 0.098, 0.303), (7, 76, 0.099, 0.192), (-22, 61, 0.105, 0.468), (22, 61, 0.108, 0.031)]
near (0,157): led (-3,157) er 0.47 ea 0.25 nel 0.90 nfa 0.49
near (150,50): led (153,45) er 0.72 ea 0.99 nel 0.48 nfa 0.82
near (-150,50): led (-153,45) er 0.71 ea 0.51 nel 0.48 nfa 0.18
near (100,120): led (98,117) er 0.54 ea 0.09 nel 0.71 nfa 0.73
near (-100,120): led (-98,117) er 0.54 ea 0.41 nel 0.71 nfa 0.28
near (160,-20): led (170,-21) er 0.87 ea 0.93 nel 0.29 nfa 0.84
near (-160,-20): led (-170,-21) er 0.87 ea 0.57 nel 0.29 nfa 0.16
near (0,-105): led (-30,-111) er 0.80 ea 0.72 nel 0.00 nfa 0.42
near (100,-100): led (101,-98) er 0.86 ea 0.84 nel 0.05 nfa 0.73
near (-100,-100): led (-101,-98) er 0.86 ea 0.66 nel 0.05 nfa 0.27
near (0,40): led (-7,61) er 0.04 ea 0.41 nel 0.52 nfa 0.48
tube 0 along 0.02 at (-207,67); along 0.89 at (-348,216)
tube 1 along 0.17 at (-130,139); along 0.94 at (-310,303)
tube 2 along 0.13 at (-87,223); along 0.95 at (-237,349)
tools/showkit/songs/radio/t1.png (1800, 735)
Sat Oct 31 12:47:58 PDT 2026
```

```
$ KIT=tools/showkit; W="$KIT/work/radio"; cd "~/deadmau5 app"; cat > "$W/pct.py" <<'EOF'
import sys, os, json
sys.path.insert(0, os.getcwd())
import numpy as np, mau5show
base="deadmau5 - Some Chords (Radio Edit)"
show=json.load(open("shows/%s.json"%base))
music=mau5show._music_for(show,"shows/%s.mp3"%base)
print("fps",music.fps)
def tof(bar):
    t=0.124+4*bar*0.46875
    return t+0.032 if t>=135.1 else t
secs=[(0,4),(4,8),(8,12),(12,16),(16,24),(24,27.75),(28,36),(36,44),(44,52),(52,59),(60,62),(62,64),(64,68),(68,72),(72,76),(76,84),(84,88),(88,91.75),(92,100),(100,107),(107,108),(108,110)]
fo ... [cut]
fps 40
  0.00-  4.00  be 0.84/0.90/0.97/1.00  bp 0.02/0.05/0.29/1.00  me 0.00/0.19/0.52/0.60  mp 0.03/0.08/0.24/0.78  he 0.00/0.00/0.14/0.17  hp 0.00/0.02/0.04/0.08
  4.00-  8.00  be 0.77/0.84/0.90/0.93  bp 0.02/0.07/0.28/0.69  me 0.58/0.67/0.81/0.87  mp 0.04/0.09/0.23/0.78  he 0.17/0.21/0.36/0.44  hp 0.02/0.05/0.14/0.33
  8.00- 12.00  be 0.74/0.83/0.89/0.91  bp 0.03/0.09/0.24/0.42  me 0.73/0.82/0.88/0.93  mp 0.04/0.09/0.21/0.52  he 0.41/0.47/0.56/0.67  hp 0.02/0.06/0.19/0.38
 12.00- 16.00  be 0.74/0.83/0.89/0.97  bp 0.03/0.12/0.43/0.78  me 0.70/0.81/0.89/1.00  mp 0.04/0.11/0.36/0.75  he 0.48/0.58/0.79/0.89  hp 0.03/0.11/0.44/0.83
 16.00- 24.00  be 0.72/0.81/0.88/0.99  bp 0.05/0.14/0.39/0.78  me 0.39/0.82/0.92/1.00  mp 0.04/0.14/0.51/1.00  he 0.56/0.65/0.78/1.00  hp 0.03/0.12/0.47/1.00
 24.00- 27.75  be 0.76/0.82/0.85/0.87  bp 0.02/0.05/0.11/0.24  me 0.64/0.82/0.89/0.99  mp 0.04/0.08/0.19/0.37  he 0.43/0.52/0.67/0.83  hp 0.02/0.05/0.19/0.58
 28.00- 36.00  be 0.49/0.86/0.97/1.00  bp 0.05/0.22/0.74/1.00  me 0.07/0.63/0.85/1.00  mp 0.07/0.22/0.63/1.00  he 0.25/0.62/0.87/1.00  hp 0.08/0.22/0.64/1.00
 36.00- 44.00  be 0.48/0.86/0.97/1.00  bp 0.06/0.22/0.78/1.00  me 0.07/0.63/0.87/1.00  mp 0.07/0.23/0.73/1.00  he 0.36/0.74/0.91/1.00  hp 0.10/0.28/0.78/1.00
 44.00- 52.00  be 0.47/0.85/0.96/1.00  bp 0.04/0.22/0.78/1.00  me 0.17/0.65/0.89/1.00  mp 0.07/0.22/0.61/1.00  he 0.44/0.74/0.92/1.00  hp 0.10/0.23/0.72/1.00
 52.00- 59.00  be 0.42/0.84/0.95/1.00  bp 0.04/0.22/0.77/1.00  me 0.20/0.64/0.88/1.00  mp 0.08/0.21/0.61/1.00  he 0.43/0.74/0.93/1.00  hp 0.11/0.25/0.73/1.00
 60.00- 62.00  be 0.03/0.17/0.41/0.78  bp 0.04/0.10/0.22/0.29  me 0.35/0.54/0.70/0.82  mp 0.04/0.09/0.20/0.29  he 0.44/0.67/0.84/0.90  hp 0.02/0.03/0.07/0.09
 62.00- 64.00  be 0.00/0.00/0.00/0.01  bp 0.00/0.01/0.0
... [cut] ...
ys, e => e[1]) };
376:  return Int32Array.from(out);
405:      name: sc.name, from: sc.from, to: sc.to, out: sc.out,
423:    this._si = 0;                                 // the last scene, to start from
457:      P.seq = L.seq.map(x => Int32Array.from(x));
554:        const a0 = valAt(P.from, p, bar, music, tt), a1 = valAt(P.to, p, bar, music, tt);
701:    if (c && c.from <= bar && bar < c.to) return this._si;
703:      if (S[i].from <= bar && bar < S[i].to) { this._si = i; return i; }
732:    const lb = B - 4 * sc.from;
733:    const span = 4 * (sc.to - sc.from);
Sat Oct 31 12:50:14 PDT 2026
```

```
$ KIT=tools/showkit; W="$KIT/work/radio"; cd "~/deadmau5 app"; B="deadmau5 - Some Chords (Radio Edit)"; cat > "shows/scenes/$B.sprites.json" <<'EOF'
{
 "radioedit_on": [
  "..XXXXX..XX...XX.",
  ".XX...XX.XXX..XX.",
  "XX.....X.XXXX.XX.",
  "XX.....X.XX.XXXX.",
  "XX.....X.XX..XXX.",
  ".XX...XX.XX...XX.",
  "..XXXXX..XX...XX."
 ],
 "radioedit_air": [
  "..XX...XXX.XXXX..",
  ".XXXX...X..XX.XX.",
  ".XX.XX..X..XX.XX.",
  "XX..XX..X..XXXX..",
  "XXXXXX..X..XX.XX.",
  "XX..XX..X..XX.XX.",
  "XX..XX.XXX.XX.XX."
 ],
 "radioedit_tower": [
  "........X........",
  ".......XXX.......",
  ".......X.X.... ... [cut]
tools/showkit/songs/radio/sp1.png (1440, 338)
Sat Oct 31 12:51:06 PDT 2026
```

```
$ KIT=tools/showkit; W="$KIT/work/radio"; cd "~/deadmau5 app"; B="deadmau5 - Some Chords (Radio Edit)"; cat > "shows/scenes/$B.sprites.json" <<'EOF'
{
 "radioedit_on": [
  "..XXXXX..XX...XX.",
  ".XX...XX.XXX..XX.",
  "XX.....X.XXXX.XX.",
  "XX.....X.XX.XXXX.",
  "XX.....X.XX..XXX.",
  ".XX...XX.XX...XX.",
  "..XXXXX..XX...XX."
 ],
 "radioedit_air": [
  "..XX...XXX.XXXX..",
  ".XXXX...X..XX.XX.",
  ".XX.XX..X..XX.XX.",
  "XX..XX..X..XXXX..",
  "XXXXXX..X..XX.XX.",
  "XX..XX..X..XX.XX.",
  "XX..XX.XXX.XX.XX."
 ],
 "radioedit_tower": [
  "........X........",
  ".......XXX.......",
  ".......X.X.... ... [cut]
tools/showkit/songs/radio/sp1.png (1440, 338)
Sat Oct 31 12:51:06 PDT 2026
```

```
$ KIT=tools/showkit; W="$KIT/work/radio"; cat > "$W/write_treatment.py" <<'EOF'
#!/usr/bin/env python3
"""ON THE RADIO: the treatment for deadmau5 - Some Chords (Radio Edit), written by hand in bars."""
import json, os, sys
KIT = os.environ.get("KIT") or "tools/showkit"
sys.path.insert(0, KIT)
from fmt import save

BASE = "deadmau5 - Some Chords (Radio Edit)"

# ---- the sprites -----------------------------------------------------------
SPRITES = {
 "radioedit_on": [
  "..XXXXX..XX...XX.",
  ".XX...XX.XXX..XX.",
  "XX.. ... [cut]
wrote shows/scenes/deadmau5 - Some Chords (Radio Edit).scene.json scenes 21 hits 12
     108   202.66s  energy 0.32  bass 0.27 (punch 0.40)  mid 0.63  high 0.78
  off        bar 108
     107   200.78s  energy 0.74  bass 0.83 (punch 1.00)  mid 0.81  high 0.72
     108   202.66s  energy 0.32  bass 0.27 (punch 0.40)  mid 0.63  high 0.78
     109   204.53s  energy 0.06  bass 0.07 (punch 0.26)  mid 0.36  high 0.47
  end        bar 112
     111   208.28s  energy 0.00  bass 0.00 (punch 0.01)  mid 0.00  high 0.00
deadmau5 - Some Chords (Radio Edit): 22 scenes, 12 hits, written into shows/deadmau5 - Some Chords (Radio Edit).json
Sat Oct 31 12:52:25 PDT 2026
```

```
$ KIT=tools/showkit; W="$KIT/work/radio"; cd "~/deadmau5 app"; B="deadmau5 - Some Chords (Radio Edit)"; time python3 "$KIT/sheet.py" "$B" "$W/d1.png" 0.5:tune 1.3:tune 3.5:tune 5.5:tune 7.5:tune 8:lock 8.25:lock 10:locked 14:drums 14.06:drums 16:signal 16.06:signal 18.1:signal 20.5:signal 25:interf 27:interf 27.8:gap 28:drop 28.06:drop 28.25:drop2 29:airsign 30:rings 30.1:rings 30.25:rings 36:b 38:b 38.1:b 44:c 46:c 46.1:c 52:d 54:d 54.1:d 59.3:slip 60.5:title 62:title 63.5:title 65:retune 68:retune 71:retune 72:lock2 74:sig3 78:sig4 78.06:sig4 86:sig5 89:interf 92:drop2 92.06:drop2 94:drop2 94.1 ... [cut]
bar 0.5     tune           shell max 255 mean  18.6   ears max 148 mean  12.8   tuning
bar 1.3     tune           shell max 229 mean  19.1   ears max 125 mean  13.7   tuning
bar 3.5     tune           shell max 255 mean  22.1   ears max 171 mean  24.5   tuning
bar 5.5     tune           shell max 255 mean  18.3   ears max 171 mean  23.3   tuning
bar 7.5     tune           shell max 197 mean  15.2   ears max 160 mean  37.6   tuning
bar 8       lock           shell max 255 mean  90.6   ears max 182 mean  58.5   locked · LOCK
bar 8.25    lock           shell max 255 mean  65.0   ears max 157 mean  52.8   locked · LOCK
bar 10      locked         shell max 255 mean  17.9   ears max 115 mean  16.1   locked
bar 14      drums          shell max 255 mean  18.5   ears max 112 mean   2.2   drums
bar 14.06   drums          shell max 255 mean  20.7   ears max 117 mean  16.9   drums
bar 16      signal         shell max 177 mean  22.1   ears max  76 mean   7.4   signal
bar 16.06   signal         shell max 185 mean  24.9   ears max 117 mean  21.7   signal
bar 18.1    signal         shell max 183 mean  20.2   ears max 116 mean  11.3   signal
bar 20.5    signal         shell max 179 mean  21.9   ears max 105 mean   7.9   signal2
bar 25      interf         shell max 145 mean  18.2   ears max 121 mean  33.4   interference
bar 27      interf         shell max 168 mean  18.1   ears max 152 mean  21.5   interference
bar 27.8    gap            shell max 210 mean   0.7   ears max   0 mean   0.0   interference · BEACON
bar 28      drop           shell max 230 mean  58.2   ears max 255 mean  90.4   on air · ON AIR · WHITE?
bar 28.06   drop           shell max 230 mean  52.3   ears max 255 mean 102.5   on air · ON AIR · WHITE?
bar 28.25   drop2          shell max 230 mean  57.1   ears max 255 mean
... [cut] ...
eceive
bar 107.3   slip2          shell max 255 mean  16.3   ears max 128 mean  41.0   slip2
bar 108.5   off            shell max  73 mean   6.8   ears max  76 mean  22.7   off
bar 110     off            shell max  31 mean   0.6   ears max  70 mean   5.2   off
bar 111.5   off            shell max   4 mean   0.0   ears max  17 mean   0.0   off
tools/showkit/songs/radio/d1.png (1800, 2450)
python3 "$KIT/sheet.py" "$B" "$W/d1.png" 0.5:tune 1.3:tune 3.5:tune 5.5:tune   0.78s user 0.04s system 99% cpu 0.826 total
```

```
$ KIT=tools/showkit; W="$KIT/work/radio"; cd "~/deadmau5 app"; sed -e 's/cols = 6; W = 300; H = 245/cols = int(os.environ.get("COLS","4")); W = int(os.environ.get("TW","480")); H = int(W*245\/300)/' "$KIT/sheet.py" > "$W/big.py"; B="deadmau5 - Some Chords (Radio Edit)"; COLS=4 TW=450 python3 "$W/big.py" "$B" "$W/b1.png" 30 30.0625 30.125 30.1875 30.25 30.3125 30.375 30.4375 30.5 30.5625 30.625 30.6875 30.75 30.8125 30.875 30.9375 | tail -3; date
bar 30.875                 shell max 140 mean  26.5   ears max 252 mean  28.6   on air
bar 30.9375                shell max 137 mean  26.5   ears max 209 mean  28.4   on air
tools/showkit/songs/radio/b1.png (1800, 1468)
Sat Oct 31 12:53:02 PDT 2026
```

```
$ KIT=tools/showkit; W="$KIT/work/radio"; cd "~/deadmau5 app"; sed -e 's/cols = 6; W = 300; H = 245/cols = int(os.environ.get("COLS","4")); W = int(os.environ.get("TW","480")); H = int(W*245\/300)/' "$KIT/sheet.py" > "$W/big.py"; B="deadmau5 - Some Chords (Radio Edit)"; COLS=4 TW=450 python3 "$W/big.py" "$B" "$W/b1.png" 30 30.0625 30.125 30.1875 30.25 30.3125 30.375 30.4375 30.5 30.5625 30.625 30.6875 30.75 30.8125 30.875 30.9375 | tail -3; date
bar 30.875                 shell max 140 mean  26.5   ears max 252 mean  28.6   on air
bar 30.9375                shell max 137 mean  26.5   ears max 209 mean  28.4   on air
tools/showkit/songs/radio/b1.png (1800, 1468)
Sat Oct 31 12:53:02 PDT 2026
```

```
$ KIT=tools/showkit; W="$KIT/work/radio"; cat > "$W/t2.py" <<'EOF'
import sys,os
KIT=os.environ["KIT"];sys.path.insert(0,KIT+"/work/radio")
from lab import *
P={"dial":[[0,0,0],[60,18,0],[200,90,8],[255,160,40],[255,215,130]],
   "r4":{"stops":[[0,0,0],[0,255,210],[0,0,0],[0,0,0]],"wrap":True},
   "r6":{"stops":[[0,0,0],[0,255,210],[0,30,25],[0,0,0],[0,0,0],[0,0,0]],"wrap":True},
   "r8":{"stops":[[0,0,0],[0,255,210],[0,60,50],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0]],"wrap":True},
   "m6":{"stops":[[0,0,0],[255,0,170],[60,0,40],[0,0,0],[0,0,0],[0,0,0]],"wrap":True},
   "beacon":[[255,0,60],[255,0,90],[255,6 ... [cut]
tools/showkit/songs/radio/t2.png (1800, 980)
tools/showkit/songs/radio/b2.png (1800, 367)
Sat Oct 31 12:53:55 PDT 2026
```

```
$ KIT=tools/showkit; W="$KIT/work/radio"; cat > "$W/t2.py" <<'EOF'
import sys,os
KIT=os.environ["KIT"];sys.path.insert(0,KIT+"/work/radio")
from lab import *
P={"dial":[[0,0,0],[60,18,0],[200,90,8],[255,160,40],[255,215,130]],
   "r4":{"stops":[[0,0,0],[0,255,210],[0,0,0],[0,0,0]],"wrap":True},
   "r6":{"stops":[[0,0,0],[0,255,210],[0,30,25],[0,0,0],[0,0,0],[0,0,0]],"wrap":True},
   "r8":{"stops":[[0,0,0],[0,255,210],[0,60,50],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0]],"wrap":True},
   "m6":{"stops":[[0,0,0],[255,0,170],[60,0,40],[0,0,0],[0,0,0],[0,0,0]],"wrap":True},
   "beacon":[[255,0,60],[255,0,90],[255,6 ... [cut]
tools/showkit/songs/radio/t2.png (1800, 980)
tools/showkit/songs/radio/b2.png (1800, 367)
Sat Oct 31 12:53:55 PDT 2026
```

```
$ KIT=tools/showkit; W="$KIT/work/radio"; cd "~/deadmau5 app"; B="deadmau5 - Some Chords (Radio Edit)"; COLS=4 TW=450 python3 "$W/big.py" "$B" "$W/b3.png" 0.5 1.1 1.5 2.5 3.1 3.5 4.5 6.5 7.5 7.9 8 8.5 10 10.5 13 14.06 | tail -18; date
bar 0.5                    shell max 255 mean  18.6   ears max 148 mean  12.8   tuning
bar 1.1                    shell max 243 mean  14.8   ears max  91 mean   8.4   tuning
bar 1.5                    shell max 255 mean  19.3   ears max 120 mean   9.0   tuning
bar 2.5                    shell max 212 mean  17.1   ears max 145 mean  13.6   tuning
bar 3.1                    shell max 228 mean  12.7   ears max  94 mean  12.2   tuning
bar 3.5                    shell max 255 mean  22.1   ears max 171 mean  24.5   tuning
bar 4.5                    shell max 246 mean  13.8   ears max 118 mean  21.3   tuning
bar 6.5                    shell max 206 mean  13.8   ears max 133 mean  30.9   tuning
bar 7.5                    shell max 197 mean  15.2   ears max 160 mean  37.6   tuning
bar 7.9                    shell max 221 mean  13.8   ears max 143 mean  37.1   tuning
bar 8                      shell max 255 mean  90.6   ears max 182 mean  58.5   locked · LOCK
bar 8.5                    shell max 255 mean  41.4   ears max 131 mean  42.7   locked · LOCK
bar 10                     shell max 255 mean  17.9   ears max 115 mean  16.1   locked
bar 10.5                   shell max 238 mean  16.9   ears max 115 mean  32.9   locked
bar 13                     shell max 255 mean  19.5   ears max 116 mean   6.4   drums
bar 14.06                  shell max 255 mean  20.7   ears max 117 mean  16.9   drums
tools/showkit/songs/radio/b3.png (1800, 1468)
Sat Oct 31 12:54:24 PDT 2026
```

```
$ KIT=tools/showkit; W="$KIT/work/radio"; cd "~/deadmau5 app"; B="deadmau5 - Some Chords (Radio Edit)"; COLS=4 TW=450 python3 "$W/big.py" "$B" "$W/b3.png" 0.5 1.1 1.5 2.5 3.1 3.5 4.5 6.5 7.5 7.9 8 8.5 10 10.5 13 14.06 | tail -18; date
bar 0.5                    shell max 255 mean  18.6   ears max 148 mean  12.8   tuning
bar 1.1                    shell max 243 mean  14.8   ears max  91 mean   8.4   tuning
bar 1.5                    shell max 255 mean  19.3   ears max 120 mean   9.0   tuning
bar 2.5                    shell max 212 mean  17.1   ears max 145 mean  13.6   tuning
bar 3.1                    shell max 228 mean  12.7   ears max  94 mean  12.2   tuning
bar 3.5                    shell max 255 mean  22.1   ears max 171 mean  24.5   tuning
bar 4.5                    shell max 246 mean  13.8   ears max 118 mean  21.3   tuning
bar 6.5                    shell max 206 mean  13.8   ears max 133 mean  30.9   tuning
bar 7.5                    shell max 197 mean  15.2   ears max 160 mean  37.6   tuning
bar 7.9                    shell max 221 mean  13.8   ears max 143 mean  37.1   tuning
bar 8                      shell max 255 mean  90.6   ears max 182 mean  58.5   locked · LOCK
bar 8.5                    shell max 255 mean  41.4   ears max 131 mean  42.7   locked · LOCK
bar 10                     shell max 255 mean  17.9   ears max 115 mean  16.1   locked
bar 10.5                   shell max 238 mean  16.9   ears max 115 mean  32.9   locked
bar 13                     shell max 255 mean  19.5   ears max 116 mean   6.4   drums
bar 14.06                  shell max 255 mean  20.7   ears max 117 mean  16.9   drums
tools/showkit/songs/radio/b3.png (1800, 1468)
Sat Oct 31 12:54:24 PDT 2026
```

```
$ KIT=tools/showkit; W="$KIT/work/radio"; cat > "$W/patch1.py" <<'PY'
import re,os
p=os.environ["W"]+"/write_treatment.py"
s=open(p).read()
# ---- replace everything from the helpers' rings to the end with the second draft
head=s[:s.index("def rings(beats")]
tail=r'''
BEATS_RING = 1.0
def rings(beats, gain, pal="rings_t", per=1, cg=6.0, rad=440, soft=260, on="shell+rims", inward=False, x=0, y=170, gate=True, phase=0.0):
    """Broadcast rings from the top of the head: one leaves on each `per` beats of this scene."""
    st = {"rings_t": 8, "rings_m": 8, "rings_a": 8}[pal]
    n = beats / float(per)
    c0 = ... [cut]
wrote shows/scenes/deadmau5 - Some Chords (Radio Edit).scene.json scenes 29 hits 7
     111   208.28s  energy 0.00  bass 0.00 (punch 0.01)  mid 0.00  high 0.00
deadmau5 - Some Chords (Radio Edit): 30 scenes, 7 hits, written into shows/deadmau5 - Some Chords (Radio Edit).json
bar 16      signal         shell max 177 mean  22.1   ears max 128 mean  54.5   signal
bar 16.06   signal         shell max 185 mean  24.9   ears max 128 mean  29.5   signal
bar 18.1    signal         shell max 183 mean  20.2   ears max 128 mean  35.7   signal
bar 18.25   signal         shell max 186 mean  19.6   ears max 128 mean  32.9   signal
bar 20.5    signal         shell max 180 mean  17.7   ears max 128 mean  52.7   signal2
bar 22      signal         shell max 183 mean  22.7   ears max 128 mean  39.8   signal2
bar 28      ON             shell max 230 mean  38.3   ears max 255 mean 114.8   ON AIR · SLAM
bar 28.5    AIR            shell max 230 mean  46.3   ears max 135 mean  26.0   ON AIR
bar 29      ON             shell max 230 mean  38.3   ears max 136 mean  27.2   ON AIR
bar 29.5    AIR            shell max 230 mean  46.3   ears max 136 mean  14.5   ON AIR
bar 30      rings          shell max 230 mean  17.5   ears max 135 mean  16.1   on air
bar 30.06   rings          shell max 203 mean  12.4   ears max 153 mean  20.5   on air
bar 30.125  rings          shell max 138 mean  10.5   ears max 140 mean  22.4   on air
bar 30.25   rings          shell max 151 mean  16.3   ears max 128 mean   2.1   on air
bar 30.5    rings          shell max 230 mean  17.5   ears max 128 mean   2.1   on air
bar 31      rings          shell max 230 mean  17.5   ears max 136 mean  13.6   on air
bar 36      ON             shell max 230 mean  38.3   ears max 140 mean  40.4   ON AIR b
bar 36.5    AIR            shell m
... [cut] ...
01.25                 shell max 151 mean  15.7   ears max 129 mean   2.3   receive
bar 104     rcv            shell max 230 mean  16.9   ears max 230 mean  40.4   on air 3
bar 104.06                 shell max 203 mean  13.3   ears max 204 mean  22.5   on air 3
bar 104.25                 shell max 151 mean  15.8   ears max 230 mean  11.7   on air 3
bar 105                    shell max 230 mean  16.9   ears max 230 mean  68.8   on air 3
tools/showkit/songs/radio/d2.png (1800, 2205)
Sat Oct 31 12:56:09 PDT 2026
```

```
$ cd "~/deadmau5 app"; B="deadmau5 - Some Chords (Radio Edit)"; time python3 mau5scene.py check "$B" 2>&1 | tail -40; sed -n 1,60p mau5power.py | head -80; date
deadmau5 - Some Chords (Radio Edit): 5250 frames at 25 fps through the guard
  scene            from  mean mA   p95 mA     heat   allow W      ms
  tuning           0.0s      652      923     2.2%      18.1    0.16
  locked          15.2s      802     1000     3.7%      18.1    0.14
  drums           22.6s      805     1000     5.2%      18.1    0.14
  signal          30.2s      803     1000     6.7%      18.1    0.12
  signal2         37.6s      835     1000     8.3%      18.1    0.13
  interference    45.2s      707      891     9.6%      18.1    0.14
  ON AIR          52.6s      662     1000    10.1%      18.1    0.13
  on air          56.4s      557     1000    11.3%      18.1    0.13
  ON AIR b        67.6s      617      967    11.5%      18.1    0.12
  on air b        69.5s      571     1000    13.0%      18.1    0.14
  ON AIR c        82.6s      645      961    13.2%      18.1    0.12
  stereo          84.5s      588     1000    14.0%      18.1    0.16
  stereo b        91.1s      610     1000    14.8%      18.1    0.16
  ON AIR d        97.6s      646      942    15.1%      18.1    0.12
  on air d        99.5s      630     1000    16.6%      18.1    0.17
  slip           110.8s      921     1000    17.1%      18.1    0.12
  sign-off       112.6s      535      747    17.8%      18.1    0.28
  retune         120.2s      603      901    19.6%      18.1    0.16
  signal3        135.2s      873     1000    21.4%      18.1    0.15
  signal4        142.7s      844     1000    24.7%      18.1    0.15
  signal5        157.7s      839     1000    26.3%      18.1    0.15
  interference   165.2s      710      905    27.6%      18.1    0.14
  ON AIR 2       172.7s      643     1000    28.1%      18.1    0.13
  on air 2       176.4s      548     1000    29.2%      18.1    0.1
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


Sat Oct 31 12:56:32 PDT 2026
```

```
$ cd "~/deadmau5 app"; python3 mau5scene.py check "TIKI TIKI - Slowed" 2>&1 | tail -60 | awk 'NR<=4 || NR%3==0' | head -36; python3 - <<'EOF'
import json
print(json.load(open("data/cal/power.json")))
EOF
grep -n "class Thermal" -A40 mau5power.py | sed -n 1,70p; date
  scene            from  mean mA   p95 mA     heat   allow W      ms
  (outside)        0.0s        0        0     0.0%      18.1    0.00
  dark             0.1s        0        0    18.7%      18.1    0.01
  embers           0.5s       31       46     0.0%      18.1    0.06
  lighting         7.0s      199      436     0.0%      18.1    0.09
  dip             24.4s      140      269     1.9%      18.1    0.07
  burn            38.4s      392      815     3.6%      18.1    0.12
  still           48.8s      465      491     3.6%      18.1    0.23
  vlow            66.2s      187      376     3.8%      18.1    0.05
  bigb            83.6s      565      845     7.1%      18.1    0.24
  stop2          109.6s       38       60     7.1%      18.1    0.07
  verse2         118.4s      313      762     7.3%      18.1    0.12
  sunset         132.3s      588      877     8.8%      18.1    0.21
  lagoon3        163.6s      177      309    10.1%      18.1    0.10
  swell3         172.3s      373      563    10.0%      18.1    0.10
  vrise3         186.2s      224      602    10.0%      18.1    0.10
  duel3          205.3s      565      888    12.2%      18.1    0.15
  dip2           222.9s      146      266    14.1%      18.1    0.07
  burn4          236.8s      329      621    15.6%      18.1    0.10
  still4         247.2s      354      480    15.3%      18.1    0.19
  vlow4          264.6s      189      377    15.5%      18.1    0.05
  final2         282.0s      584     1000    18.5%      18.1    0.25
  worst frame 0.43 ms; no scene reaches the sustained floor
{'count': 621, 'budget_ma': 1000.0, 'default_ceiling': 32, 'thermal': {'sustained_w': 11.0, 'burst_j': 3000.0, 'max_w': 25.5, 'standby_w': 7.452, 'ramp': 0.3}, 'regions': [{'name': 'shell', 'lo': 0, 'hi': 397, 'ceiling': 6
... [cut] ...
0.0, max_w=None,
130-                 standby_w=0.0, ramp=0.30):
131-        self.sustained_w = float(sustained_w)
132-        self.burst_j = float(burst_j)
133-        self.max_w = float(max_w) if max_w else None
134-        self.standby_w = float(standby_w)
135-        self.ramp = float(ramp)
136-        self.level = 0.0                  # joules banked against us
137-        self._last = None
138-
139-    def allowance_w(self):
140-        """LED watts permitted right now, standby already deducted."""
141-        head = 1.0 - self.level / max(self.burst_j, 1e-6)
Sat Oct 31 12:56:42 PDT 2026
```

```
$ cd "~/deadmau5 app"; sed -n 760,830p mau5show.py; grep -n "def apply" -A75 mau5power.py | sed -n 1,130p
            drive = self.music.band_at(t, band, punch=bool(ov.get("punch", True)))
            gain *= float(ov.get("floor", 0.15)) + (1.0 - float(ov.get("floor", 0.15))) * drive
        lay = self._one(ov["preset"], ov.get("params", {}), t) * gain
        if ov.get("mix", "add") == "over":
            m = lay.max(1) > 4
            out = out.copy(); out[m] = lay[m]
            return out
        return np.maximum(out, lay) if ov.get("mix") == "max" else out + lay

    def frame(self, t):
        if self.scenes is not None:
            try:
                out, self.gain, self.label = self.scenes.frame(t, self.music)
                return out
            except Exception as e:      # a black helmet is the worst outcome
                print("mau5show: the scenes failed (%s: %s) -- playing the cue "
                      "list" % (type(e).__name__, e))
                self.scenes, self.label = None, None
        self.gain = 1.0
        cur = self.cue_at(t)
        if cur is None:
            return np.zeros((self.h.n, 3))
        out = self._render(cur, t)

        if self.fade > 0:
            into = t - cur["start"]
            if into < self.fade:
                i = self._cues.index(cur)
                if i > 0:
                    prev = self._cues[i - 1]
                    k = into / self.fade
                    out = k * out + (1 - k) * self._render(prev, t)

        if self.music is not None:
            lvl = cur.get("level", 0)
            ph = self.music.beat_phase(t)
            if self.dyn > 0:
                # bass and overall together: a breakdown with a loud pad
                # should not read as loud as a drop with a kick under it
                e = (0.6 * self.music.band_at(t, "bass")
                     + 0.4 * self.music.level_at(t))
        
... [cut] ...
inue
301-            seg = out[lo:hi + 1]
302-            ma = float(seg.sum() / (3 * 255.0) * MA_PER_LED_FULL_WHITE)
303-            if ma > r.budget_ma and ma > 0:
304-                seg *= r.budget_ma / ma
305-                hit.append(r.name)
306-        after_region = self.frame_ma(out)
307-
308-        # -- the thermal allowance, if one is in force -------------------
309-        # The per-frame budget is a ceiling; this is the rolling one.  It
310-        # is applied before the global scale so the two compose rather
311-        # than fight: whichever is tighter at this instant wins.
```

```
$ KIT=tools/showkit; W="$KIT/work/radio"; cd "~/deadmau5 app"; sed -n 80,125p mau5preview.py; cat > "$W/gsheet.py" <<'EOF'
#!/usr/bin/env python3
"""gsheet.py "<base>" out.png bar[:label] ... -- like sheet.py, but really through the guard: what leaves for the LEDs, then gamma so the picture is what an eye sees."""
import json, os, sys
sys.path.insert(0, os.getcwd())
import numpy as np, mau5show, mau5preview as PV, mau5scene as SS, mau5engine as E, mau5power
from PIL import Image, ImageDraw
base, out = sys.argv[1], sys.argv[2]
marks = []
for a in sys.argv[3:]:
    b, _, lab = a.partition(":")
     ... [cut]
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
    h = E.Helmet()
    sc = Scene(h)
    names = sorted(E.REGISTRY)
bar 1.3     tune       sent  528 mA  shell max  53 mean   9.7  ears max 124 mean  13.6  tuning
bar 3.5     tune       sent  707 mA  shell max  45 mean   9.7  ears max 171 mean  24.3  tuning
bar 7.5     tune   
... [cut] ...
 mA  shell max  57 mean   9.3  ears max 128 mean   2.3  receive
bar 104.06  air3       sent  376 mA  shell max  26 mean   3.2  ears max 113 mean  16.5  on air 3
bar 107.3   slip2      sent  982 mA  shell max  55 mean   9.7  ears max 127 mean  40.7  slip2
bar 108.5   off        sent  542 mA  shell max  43 mean   5.3  ears max  76 mean  22.4  off
bar 110     off        sent  103 mA  shell max  24 mean   0.5  ears max  69 mean   5.1  off
tools/showkit/songs/radio/g1.png (1800, 1715)
Sat Oct 31 12:57:51 PDT 2026
```

```
$ cd "~/deadmau5 app"; sed -n 311,420p mau5power.py; sed -n 900,935p mau5show.py; date
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
        # And s gives light back slowly.  Solved afresh every frame, it
        # moved with whatever the ears were doing, and the shell, at
        # s ** 6, moved six times as far the other way: eq bars or a
        # sparkle overlay on the tubes pumped the shell frame to frame.
        # So s may never be more than GOV_RISE e-folds per second above
        # the last frame's -- a compressor's slow release -- while a
        # smaller s still applies at once.  Never above the s solved for,
        # so never over budget; and it runs on frames under
... [cut] ...
lay") else "ffplay"
        cmd = ([player, track] if player == "afplay"
               else [player, "-nodisp", "-autoexit", "-loglevel", "quiet", track])
        proc = subprocess.Popen(cmd)

    t0 = time.monotonic()
    # only when there is sound to wait for; before it, t < 0 has no cue
    # and renders black
    lag = float(av_offset) if proc else 0.0
    nframes = dropped = 0
    try:
        while True:
            t = time.monotonic() - t0 - lag
            if t >= dur:
                break
            f = pl.frame(t)
            pix.send(f, gain=pl.gain)
Sat Oct 31 12:58:03 PDT 2026
```

```
$ cd "~/deadmau5 app"; sed -n 311,420p mau5power.py; sed -n 900,935p mau5show.py; date
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
        # And s gives light back slowly.  Solved afresh every frame, it
        # moved with whatever the ears were doing, and the shell, at
        # s ** 6, moved six times as far the other way: eq bars or a
        # sparkle overlay on the tubes pumped the shell frame to frame.
        # So s may never be more than GOV_RISE e-folds per second above
        # the last frame's -- a compressor's slow release -- while a
        # smaller s still applies at once.  Never above the s solved for,
        # so never over budget; and it runs on frames under
... [cut] ...
lay") else "ffplay"
        cmd = ([player, track] if player == "afplay"
               else [player, "-nodisp", "-autoexit", "-loglevel", "quiet", track])
        proc = subprocess.Popen(cmd)

    t0 = time.monotonic()
    # only when there is sound to wait for; before it, t < 0 has no cue
    # and renders black
    lag = float(av_offset) if proc else 0.0
    nframes = dropped = 0
    try:
        while True:
            t = time.monotonic() - t0 - lag
            if t >= dur:
                break
            f = pl.frame(t)
            pix.send(f, gain=pl.gain)
Sat Oct 31 12:58:03 PDT 2026
```

```
$ KIT=tools/showkit; W="$KIT/work/radio"; cat > "$W/pow.py" <<'EOF'
#!/usr/bin/env python3
"""pow.py "<base>": per scene through a fresh guard: mA, how often the governor sheds the shell, shell level kept."""
import json, os, sys
sys.path.insert(0, os.getcwd())
import numpy as np, mau5show, mau5scene as SS, mau5engine as E, mau5power
base=sys.argv[1]
show=json.load(open("shows/%s.json"%base))
music=mau5show._music_for(show,"shows/%s.mp3"%base)
h=E.Helmet(); sc=SS.Scenes(show["scenes"],h); guard=mau5power.load(count=h.n)
dur=float(show["duration"]); fps=25.0
per={};order=[]
sh=np.asarray(h.shell,bool); ea=np ... [cut]
scene            mean    p95   gov%   reg%  shellm   earsm   smax   heat
tuning            652    923      1     88     9.6    21.1     61   2.2%
locked            802   1000     14    100     9.1    30.9     58   3.7%
drums             805   1000     31    100     8.2    32.7     44   5.2%
signal            803   1000     60    100     7.2    34.3     43   6.7%
signal2           835   1000     76    100     7.4    36.0     41   8.3%
interference      707    891      1     83     9.0    25.5     58   9.6%
ON AIR            662   1000     52    100     6.0    28.4     35  10.1%
on air            557   1000     37      0     4.9    24.4     48  11.3%
ON AIR b          617    967     34    100     7.2    23.6     37  11.5%
on air b          571   1000     44      0     4.4    26.0     46  13.0%
ON AIR c          645    961     28    100     7.4    25.1     37  13.2%
stereo            588   1000     21     13     5.5    24.9     49  14.0%
stereo b          610   1000     25     13     5.4    26.4     49  14.8%
ON AIR d          646    942     32    100     7.3    25.2     37  15.1%
on air d          630   1000     38     88     7.0    24.7     45  16.6%
slip              921   1000     74     83     7.9    40.4     60  17.1%
sign-off          535    747      1     80     9.1    15.1     59  17.8%
retune            603    901      0     87     9.6    18.2     61  19.6%
signal3           873   1000     16    100     8.7    35.8     34  21.4%
signal4           844   1000     53    100     7.9    35.6     28  24.7%
signal5           839   1000     74    100     7.6    35.8     28  26.3%
interference2     710    905      0     82     9.0    25.7     58  27.6%
ON AIR 2          643   1000     66    100     5.2    28.7     32  28.1%
on air 2          548   1000     27      0     4.8    23.9     49  29.2%
ON AIR 3          570    968     60    100     5.6    23.7     32  29.4%
receive           523   1000     32      0     4.5    23.1     44  29.9%
on air 3          543   1000     35      0     4.5    24.1     47  30.5%
slip2             978   1000     66    100     8.5    42.7     55  31.0%
off               213    612      0      0     1.8     9.2     43  31.2%
Sat Oct 31 12:59:28 PDT 2026
```

```
$ KIT=tools/showkit; W="$KIT/work/radio"; cat > "$W/write_treatment.py" <<'EOF'
#!/usr/bin/env python3
"""ON THE RADIO: the treatment for deadmau5 - Some Chords (Radio Edit), written by hand in bars."""
import json, os, sys
KIT = os.environ.get("KIT") or "tools/showkit"
sys.path.insert(0, KIT)
from fmt import save

BASE = "deadmau5 - Some Chords (Radio Edit)"

# ---- the sprites -----------------------------------------------------------
SPRITES = {
 "radioedit_on": [
  "..XXXXX..XX...XX.",
  ".XX...XX.XXX..XX.",
  "XX.. ... [cut]
wrote shows/scenes/deadmau5 - Some Chords (Radio Edit).scene.json scenes 28 hits 7
deadmau5 - Some Chords (Radio Edit): 29 scenes, 7 hits, written into shows/deadmau5 - Some Chords (Radio Edit).json
scene            mean    p95   gov%   reg%  shellm   earsm   smax   heat
tuning            536    681      0     43     9.0    15.3     62   1.5%
locked            644    855      1     25     9.0    21.8     62   2.5%
drums             577    797      0     90     8.7    18.2     54   3.3%
signal            572   1000      8     87     8.5    18.2     51   4.2%
signal2           605    897      3     85     8.6    20.0     51   5.1%
interference      511    668      0     48     8.7    14.5     58   5.8%
ON AIR            547    924      9     50     8.2    17.9     51   6.1%
on air            456    935      5      6     6.2    15.8     57   6.8%
ON AIR b          511    794      4     49     8.2    15.7     51   7.0%
on air b          483   1000     11      5     5.9    18.0     55   8.0%
ON AIR c          523    779      4     49     8.2    16.5     51   8.2%
stereo            493    909      0      5     6.0    18.2     59   9.2%
ON AIR d          526    769      4     49     8.2    16.6     51   9.4%
the radio         475    933      5     16     6.6    16.0     56  10.2%
slip              512    704      0      0     7.7    16.2     62  10.3%
sign-off          448    592      0     49     8.5    11.0     62  10.8%
retune            506    683      0     40     9.1    13.4     62  12.1%
two signals       678    989      5    100     9.6    22.6     39  13.2%
two signals b     565    860      0    100     8.7    17.5     33  14.8%
two signals c     605    968      0    100     8.7    19.9     28  15.8%
interference2     514    673      0     49     8.7    14.6     58  16.5%
ON AIR 2          571   1000     32     76     6.6    22.1     46  16.8%
on air 2          434    828      2      3     5.8    15.2     59  17.4%
ON AIR 3          510    971     15     51     7.6    16.7     48  17.6%
receive           429   1000      6      6     5.8    15.0     56  17.9%
the radio 2       435    816      2      9     6.3    14.1     56  18.2%
slip2             555    782      0      2     9.0    16.6     62  18.4%
off               153    437      0      0     1.4     6.4     39  18.5%
tools/showkit/songs/radio/g2.png (1800, 1960)
Sat Oct 31 13:01:09 PDT 2026
```

```
$ KIT=tools/showkit; W="$KIT/work/radio"; cat > "$W/patch2.py" <<'PY'
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
  ".XX..XX..XX.XX.XX"],''' ... [cut]
wrote shows/scenes/deadmau5 - Some Chords (Radio Edit).scene.json scenes 28 hits 9
deadmau5 - Some Chords (Radio Edit): 29 scenes, 9 hits, written into shows/deadmau5 - Some Chords (Radio Edit).json
scene            mean    p95   gov%   reg%  shellm   earsm   smax   heat
tuning            550    713      0     86     9.7    15.0     62   1.5%
locked            644    855      1     25     9.0    21.8     62   2.6%
drums             577    797      0     90     8.7    18.2     54   3.4%
signal            583   1000     11     87     8.5    18.9     51   4.3%
signal2           605    897      3     85     8.6    20.0     51   5.2%
interference      511    668      0     48     8.7    14.5     58   5.9%
ON AIR            547    924      9     50     8.1    17.9     51   6.2%
on air            456    935      5      6     6.2    15.8     57   7.0%
ON AIR b          511    794      4     49     8.2    15.7     51   7.1%
on air b          483   1000     11      5     5.9    18.0     55   8.1%
ON AIR c          523    779      4     49     8.2    16.5     51   8.3%
stereo            493    909      0      5     6.0    18.2     59   9.3%
ON AIR d          526    769      4     49     8.2    16.6     51   9.5%
the radio         475    933      5     16     6.6    16.0     56  10.3%
slip              582    820      0      0     7.7    20.4     62  10.5%
sign-off          415    575      0     31     7.7    10.3     62  10.9%
retune            504    695      0     94     9.7    12.1     60  12.1%
two signals       678    989      5    100     9.6    22.6     39  13.3%
two signals b     571    911      0    100     8.7    17.8     33  14.9%
two signals c     595    959      0    100     8.7    19.3     31  15.8%
interference2     514    673      0     49     8.7    14.6     58  1
... [cut] ...
x 101 mean  22.5  retune
bar 85      sig5       sent  909 mA  shell max  29 mean   9.7  ears max 107 mean  36.3  two signals c
bar 85.5    sig5       sent  621 mA  shell max  29 mean   9.7  ears max 107 mean  19.1  two signals c
bar 60.5    title      sent  495 mA  shell max  62 mean   5.6  ears max  74 mean  18.9  sign-off · TITLE
bar 61.5    title      sent  506 mA  shell max  62 mean   9.3  ears max  72 mean  12.9  sign-off · TITLE
tools/showkit/songs/radio/g3.png (1800, 1468)
Sat Oct 31 13:02:38 PDT 2026
```

```
$ KIT=tools/showkit; W="$KIT/work/radio"; cd "~/deadmau5 app"; B="deadmau5 - Some Chords (Radio Edit)"; COLS=6 TW=300 python3 "$W/gsheet.py" "$B" "$W/g4.png" 31 31.03 31.0625 31.09 31.125 31.1875 31.25 31.28 31.3125 31.375 31.4375 31.5 31.53 31.5625 31.625 31.6875 31.75 31.78 31.8125 31.875 31.9375 18 18.03 18.0625 18.125 18.1875 18.25 18.28 18.3125 18.375 18.4375 18.5 18.5625 18.625 18.75 18.875 | awk '{print $2, $4, $8,$10,$13,$15}' | head -40; date
31 401 57 9.9 138 6.0
31.03 666 62 9.7 147 22.2
31.0625 421 56 7.3 111 11.9
31.09 293 50 5.8 96 6.8
31.125 335 47 5.4 86 10.1
31.1875 492 45 5.3 87 19.5
31.25 351 54 9.9 138 3.0
31.28 912 61 9.3 147 37.4
31.3125 538 55 7.0 111 19.3
31.375 349 47 5.2 85 11.3
31.4375 465 45 5.2 87 18.1
31.5 342 57 9.9 138 2.5
31.53 796 62 9.7 147 30.0
31.5625 388 56 7.3 111 9.9
31.625 356 47 5.4 85 11.4
31.6875 387 45 5.3 83 13.3
31.75 582 51 8.0 100 20.1
31.78 579 52 7.1 113 21.6
31.8125 503 49 5.6 95 19.6
31.875 440 46 4.8 84 17.4
31.9375 400 45 5.1 83 14.5
18 678 53 9.7 94 22.5
18.03 663 37 9.7 107 21.6
18.0625 553 40 9.2 101 15.9
18.125 465 52 8.4 82 12.0
18.1875 407 51 7.3 92 10.6
18.25 460 55 9.7 91 9.5
18.28 528 54 9.7 93 13.5
18.3125 596 56 9.2 101 18.5
18.375 385 41 8.4 82 7.2
18.4375 575 45 8.3 92 18.9
18.5 757 52 9.7 107 27.2
18.5625 423 40 9.2 89 8.2
18.625 309 42 8.4 77 2.7
18.75 889 54 9.7 107 35.1
18.875 301 37 8.4 76 2.3
(1800,     
Sat Oct 31 13:02:53 PDT 2026
```

```
$ KIT=tools/showkit; W="$KIT/work/radio"; cd "~/deadmau5 app"; B="deadmau5 - Some Chords (Radio Edit)"; COLS=6 TW=300 python3 "$W/gsheet.py" "$B" "$W/g4.png" 31 31.03 31.0625 31.09 31.125 31.1875 31.25 31.28 31.3125 31.375 31.4375 31.5 31.53 31.5625 31.625 31.6875 31.75 31.78 31.8125 31.875 31.9375 18 18.03 18.0625 18.125 18.1875 18.25 18.28 18.3125 18.375 18.4375 18.5 18.5625 18.625 18.75 18.875 | awk '{print $2, $4, $8,$10,$13,$15}' | head -40; date
31 401 57 9.9 138 6.0
31.03 666 62 9.7 147 22.2
31.0625 421 56 7.3 111 11.9
31.09 293 50 5.8 96 6.8
31.125 335 47 5.4 86 10.1
31.1875 492 45 5.3 87 19.5
31.25 351 54 9.9 138 3.0
31.28 912 61 9.3 147 37.4
31.3125 538 55 7.0 111 19.3
31.375 349 47 5.2 85 11.3
31.4375 465 45 5.2 87 18.1
31.5 342 57 9.9 138 2.5
31.53 796 62 9.7 147 30.0
31.5625 388 56 7.3 111 9.9
31.625 356 47 5.4 85 11.4
31.6875 387 45 5.3 83 13.3
31.75 582 51 8.0 100 20.1
31.78 579 52 7.1 113 21.6
31.8125 503 49 5.6 95 19.6
31.875 440 46 4.8 84 17.4
31.9375 400 45 5.1 83 14.5
18 678 53 9.7 94 22.5
18.03 663 37 9.7 107 21.6
18.0625 553 40 9.2 101 15.9
18.125 465 52 8.4 82 12.0
18.1875 407 51 7.3 92 10.6
18.25 460 55 9.7 91 9.5
18.28 528 54 9.7 93 13.5
18.3125 596 56 9.2 101 18.5
18.375 385 41 8.4 82 7.2
18.4375 575 45 8.3 92 18.9
18.5 757 52 9.7 107 27.2
18.5625 423 40 9.2 89 8.2
18.625 309 42 8.4 77 2.7
18.75 889 54 9.7 107 35.1
18.875 301 37 8.4 76 2.3
(1800,     
Sat Oct 31 13:02:53 PDT 2026
```

```
$ KIT=tools/showkit; W="$KIT/work/radio"; cat > "$W/patch3.py" <<'PY'
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
        fr[s ... [cut]
wrote shows/scenes/deadmau5 - Some Chords (Radio Edit).scene.json scenes 28 hits 9
deadmau5 - Some Chords (Radio Edit): 29 scenes, 9 hits, written into shows/deadmau5 - Some Chords (Radio Edit).json
scene            mean    p95   gov%   reg%  shellm   earsm   smax   heat
tuning            548    714      0     86     9.6    14.9     62   1.5%
locked            644    855      1     25     9.0    21.8     62   2.6%
drums             577    797      0     90     8.7    18.2     54   3.4%
signal            583   1000     11     87     8.5    18.9     51   4.3%
signal2           605    897      3     85     8.6    20.0     51   5.2%
interference      511    668      0     48     8.7    14.5     58   5.9%
ON AIR            508    852      3     50     8.3    15.4     54   6.2%
on air            456    935      5      6     6.2    15.8     57   6.9%
ON AIR b          511    794      4     49     8.2    15.7     51   7.1%
on air b          483   1000     11      5     5.9    18.0     55   8.0%
ON AIR c          523    779      4     49     8.2    16.5     51   8.2%
stereo            493    909      0      5     6.0    18.2     59   9.3%
ON AIR d          526    769      4     49     8.2    16.6     51   9.4%
the radio         475    933      5     16     6.6    16.0     56  10.2%
slip              582    820      0      0     7.7    20.4     62  10.4%
sign-off          415    575      0     31     7.7    10.3     62  10.8%
retune            503    693      0     96     9.7    12.1     60  12.0%
two signals       678    989      5    100     9.6    22.6     39  13.2%
two signals b     571    911      0    100     8.7    17.8     33  14.8%
two signals c     595    959      0    100     8.7    19.3     31  15.7%
interference2     514    673      0     49     8.7    14.6     58  16.5%
ON AIR 2          507    974      4     51     7.8    16.1     51  16.7%
on air 2          434    828      2      3     5.8    15.2     59  17.3%
ON AIR 3          476    957      4     51     7.8    14.2     53  17.5%
receive           428   1000      6      0     5.7    15.0     58  17.8%
the radio 2       435    816      2      9     6.3    14.1     56  18.1%
slip2             558    780      0     15     9.0    16.6     62  18.3%
off               153    437      0      0     1.4     6.4     39  18.4%
tools/showkit/songs/radio/g5.png (1800, 4655)
Sat Oct 31 13:05:00 PDT 2026
```

```
$ KIT=tools/showkit; W="$KIT/work/radio"; python3 - <<EOF
from PIL import Image
im=Image.open("$W/g5.png")
H=245
n=im.height//H
k=0
for a in range(0,n,7):
    im.crop((0,a*H,1800,min(a+7,n)*H)).save("$W/g5_%d.png"%k); k+=1
print(k,n)
EOF
3 19
```

```
$ KIT=tools/showkit; W="$KIT/work/radio"; python3 - <<EOF
from PIL import Image
im=Image.open("$W/g5.png")
H=245
n=im.height//H
k=0
for a in range(0,n,7):
    im.crop((0,a*H,1800,min(a+7,n)*H)).save("$W/g5_%d.png"%k); k+=1
print(k,n)
EOF
3 19
```

```
$ KIT=tools/showkit; W="$KIT/work/radio"; cat > "$W/patch4.py" <<'PY'
import os
p=os.environ["W"]+"/write_treatment.py"
s=open(p).read()
def rep(a,b):
    global s
    assert a in s, a[:70]
    s=s.replace(a,b,1)
# 84-88: the sines tighten, as they did at bar 20, in place of the amber ring
rep('''S({"name": "two signals c", "from": "song2b", "to": "fade2", "like": "two signals b", "patch": {"0": dict(rings(16, 0.32, pal="rings_a", per=4, cg=1.5, gate=False))}})''',
    '''S({"name": "two signals c", "from": "song2b", "to": "fade2", "like": "two signals b", "patch": {"1": {"wspeed": 0.5, "wscale": 3}, "2": { ... [cut]
wrote shows/scenes/deadmau5 - Some Chords (Radio Edit).scene.json scenes 28 hits 9
deadmau5 - Some Chords (Radio Edit): 29 scenes, 9 hits, written into shows/deadmau5 - Some Chords (Radio Edit).json
scene            mean    p95   gov%   reg%  shellm   earsm   smax   heat
signal            580   1000     10     87     8.5    18.8     51   4.3%
ON AIR            508    852      3     50     8.3    15.4     54   6.2%
on air            446    904      0      6     6.2    15.2     59   6.8%
ON AIR b          502    791      4     49     8.2    15.1     53   7.0%
on air b          469    998      5      5     6.1    16.9     57   7.9%
ON AIR c          515    776      4     49     8.2    15.9     53   8.1%
ON AIR d          517    769      4     49     8.2    16.0     53   9.3%
the radio         465    904      0     16     6.6    15.4     56  10.0%
two signals       678    989      5    100     9.6    22.6     39  13.0%
two signals b     569    911      0    100     8.7    17.7     33  14.6%
two signals c     587    951      0    100     8.7    18.8     35  15.5%
ON AIR 2          507    974      4     51     7.8    16.1     51  16.5%
on air 2          424    795      0      3     5.8    14.6     60  17.1%
ON AIR 3          476    957      4     51     7.8    14.2     53  17.2%
the radio 2       424    785      1      9     6.3    13.4     56  17.8%
103 governed frames of 6300
66 runs; longest and deepest:
  bar 72.18..72.31 (7 frames) asked 2250 mA, two signals · LOCK 2
  bar 16.00..16.04 (3 frames) asked 1659 mA, signal · SONG
  bar 28.00..28.04 (3 frames) asked 1611 mA, ON AIR · SLAM
  bar 37.00..37.04 (3 frames) asked 1311 mA, on air b
  bar 41.00..41.04 (3 frames) asked 1311 mA, on air b
  bar 92.27..92.31 (3 frames) asked 1600 mA, ON AIR 2 · WHITE
  bar 16.25..16.27 (2 frames) asked 1204 mA, signal · SONG
  bar 20.00..20.02 (2 frames) asked 1586 mA, signal2
  bar 28.25..28.27 (2 frames) asked 1560 mA, ON AIR · SLAM
  bar 29.00..29.02 (2 frames) asked 1413 mA, ON AIR
  bar 36.25..36.27 (2 frames) asked 1514 mA, ON AIR b
  bar 37.52..37.53 (2 frames) asked 1314 mA, on air b
  bar 38.01..38.03 (2 frames) asked 1316 mA, on air b
  bar 38.26..38.28 (2 frames) asked 1284 mA, on air b
Sat Oct 31 13:06:17 PDT 2026
```

```
$ KIT=tools/showkit; W="$KIT/work/radio"; cat > "$W/patch5.py" <<'PY'
import os
p=os.environ["W"]+"/write_treatment.py"
s=open(p).read()
a='''"c": [c0 + n, c0] if inward else [c0, c0 - n]'''
assert s.count(a)==2
s=s.replace(a,'''"c": [c0, c0 + n] if inward else [c0, c0 - n]''')
open(p,"w").write(s)
PY
W="$W" python3 "$W/patch5.py"; cd "~/deadmau5 app"; B="deadmau5 - Some Chords (Radio Edit)"; python3 "$W/write_treatment.py" && python3 mau5scene.py compile "$B" 2>&1 | grep -iE "warn|error|scenes, "; COLS=8 TW=225 python3 "$W/gsheet.py" "$B" "$W/g6.png" 101 101.0625 101.125 101.1875 101.25 101.3125 ... [cut]
wrote shows/scenes/deadmau5 - Some Chords (Radio Edit).scene.json scenes 28 hits 9
deadmau5 - Some Chords (Radio Edit): 29 scenes, 9 hits, written into shows/deadmau5 - Some Chords (Radio Edit).json
tools/showkit/songs/radio/g6.png (1800, 366)
-rw-r--r--@ 1 jones  staff  145396 Oct 31 13:06 shows/deadmau5 - Some Chords (Radio Edit).json
-rw-r--r--@ 1 jones  staff    4692 Oct 31 12:40 shows/scenes/deadmau5 - Some Chords (Radio Edit).beats
-rw-r--r--@ 1 jones  staff   44830 Oct 31 13:06 shows/scenes/deadmau5 - Some Chords (Radio Edit).scene.json
-rw-r--r--@ 1 jones  staff     370 Oct 31 13:06 shows/scenes/deadmau5 - Some Chords (Radio Edit).sprites.json
Sat Oct 31 13:06:58 PDT 2026
```

```
$ KIT=tools/showkit; W="$KIT/work/radio"; cat > "$W/patch5.py" <<'PY'
import os
p=os.environ["W"]+"/write_treatment.py"
s=open(p).read()
a='''"c": [c0 + n, c0] if inward else [c0, c0 - n]'''
assert s.count(a)==2
s=s.replace(a,'''"c": [c0, c0 + n] if inward else [c0, c0 - n]''')
open(p,"w").write(s)
PY
W="$W" python3 "$W/patch5.py"; cd "~/deadmau5 app"; B="deadmau5 - Some Chords (Radio Edit)"; python3 "$W/write_treatment.py" && python3 mau5scene.py compile "$B" 2>&1 | grep -iE "warn|error|scenes, "; COLS=8 TW=225 python3 "$W/gsheet.py" "$B" "$W/g6.png" 101 101.0625 101.125 101.1875 101.25 101.3125 ... [cut]
wrote shows/scenes/deadmau5 - Some Chords (Radio Edit).scene.json scenes 28 hits 9
deadmau5 - Some Chords (Radio Edit): 29 scenes, 9 hits, written into shows/deadmau5 - Some Chords (Radio Edit).json
tools/showkit/songs/radio/g6.png (1800, 366)
-rw-r--r--@ 1 jones  staff  145396 Oct 31 13:06 shows/deadmau5 - Some Chords (Radio Edit).json
-rw-r--r--@ 1 jones  staff    4692 Oct 31 12:40 shows/scenes/deadmau5 - Some Chords (Radio Edit).beats
-rw-r--r--@ 1 jones  staff   44830 Oct 31 13:06 shows/scenes/deadmau5 - Some Chords (Radio Edit).scene.json
-rw-r--r--@ 1 jones  staff     370 Oct 31 13:06 shows/scenes/deadmau5 - Some Chords (Radio Edit).sprites.json
Sat Oct 31 13:06:58 PDT 2026
```

```
$ cd "~/deadmau5 app"; which node; node --version; wc -l tests_more/scenes.py; grep -n "node\|playwright\|chromium\|browser\|show.js\|subprocess" tests_more/scenes.py | head -30; grep -n "^export\|^module\|exports\." remote/offline/show.js | head -30; sed -n 262,300p remote/offline/show.js
/opt/homebrew/bin/node
v26.12.0
     528 tests_more/scenes.py
6:show.js on the phone.  So every test below either compares the two
17:import subprocess
23:from test_mau5 import ok, eq, note, HERE, _node, _ShowDrive  # noqa: E402
108:            res = _node("showtest.js", {"data": data, "shows": [name], "times": times,
111:                return note("scenes: node not installed, the phone went unchecked")
262:        res = _node("showtest.js", {"data": data, "shows": ["synthetic"], "times": times,
265:            return note("scenes: node not installed, the primitives went unchecked")
368:    if not shutil.which("node"):
369:        return note("scenes: node not installed, ?cues went unchecked")
377:  const S = require(job.here + '/remote/offline/show.js');
425:    p = subprocess.run(["node", "-e", js], input=json.dumps(
428:    ok(p.returncode == 0, "node failed:\n%s" % p.stderr[-2000:])
442:    Timed under node on this machine, which is several times a phone:
456:        res = _node("showtest.js", {"data": data, "shows": [name], "times": times})
458:            return note("scenes: node not installed, the cost went unchecked")
466:    ok(worst_mean < 0.5, "a scene frame averages %.3f ms under node" % worst_mean)
468:    note("scenes: %.3f ms a frame on average, %.3f at worst, under node"
//
// Every frame is a pure function of t (and, given an analysed track, its
// band curves) on the analysis' beat grid, which is exactly linear for
// every shipped song.  So the clock can be the audio element's own
// currentTime, seeking costs nothing, and the laptop and this page agree
// to the bit: the arithmetic below is mau5scene.Scenes written out in the
// same order, and test_mau5's scenes group holds the two together.
//
// The JSON arrives with every default filled in.  Th
... [cut] ...
ctip', 'rim'],
  preset: [],
  orb: ['x', 'y', 'rad', 'soft', 'wx', 'wy', 'xf', 'yf', 'xp', 'yp', 'cgrad'],
  twinkle: ['rate', 'sharp', 'spread', 'dens'],
};

function sclamp(v, lo, hi) { return v < lo ? lo : (v > hi ? hi : v); }
function shash(x) { return pmod(Math.sin(x) * 43758.5453, 1); }

// A value in one of its four canonical forms -> something cheap to read.
function prepVal(v) {
  if (v && typeof v.n === 'number') return { k: 0, a: v.n };
  if (v && v.ramp) return { k: 1, a: v.ramp[0], b: v.ramp[1] };
  if (v && v.keys) {
    return { k: 2, bars: Float64Array.from(v.keys, e => e[0]),
```

```
$ cd "~/deadmau5 app"; sed -n 85,135p tests_more/scenes.py; grep -n "def _node" -A22 test_mau5.py | head -50; ls tests_more | head -20; find . -name "showtest.js" -not -path "./node_modules/*" | head; sed -n 1,60p "$(find . -name 'showtest.js' -not -path './node_modules/*' | head -1)"
def _scene_shows(data):
    return [n for n in sorted(data["shows"]) if data["shows"][n].get("scenes")]


def t_scene_shows_match_phone():
    """Each scene show, at every edge and hit, the same on both devices.

    Twice: with an analysed drive, so the band-driven values read the
    curves, and with a plain one, where both sides must take the
    midpoint.  Both sides must also say they are playing scenes, so a
    silent fall back to the cue list cannot pass as agreement.
    """
    import mau5engine as E
    import mau5offline
    data = mau5offline.bundle()
    names = _scene_shows(data)
    ok(names, "no bundled show carries scenes")
    h = E.Helmet()
    worst, where, n = 0.0, "", 0
    for name in names:
        show = data["shows"][name]
        times = _scene_times(show["scenes"], show["duration"])
        for analysed, music in ((True, _SceneDrive()), (False, _ShowDrive())):
            res = _node("showtest.js", {"data": data, "shows": [name], "times": times,
                                        "analysed": analysed})
            if res is None:
                return note("scenes: node not installed, the phone went unchecked")
            w, at = _compare(name, show, times, res[name], music, h)
            n += len(times)
            if w > worst:
                worst, where = w, at
    ok(worst < 0.01, "the phone's scenes differ by %.4f counts (%s)" % (worst, where))
    note("scenes: %d shows, %d frames, worst %.5f counts (%s)"
         % (len(names), n, worst, where or "exact"))


# Every primitive, every mix, every value form and every region, on a
# made-up grid, so a disagreement in a corner the shipped songs never
# reach still fails here.
SYNTHETIC = {
    "v": 1, "show": "synthetic", "lead": 0.0,
    "marks": {"go": 4, "blades": "go+12", "pr
... [cut] ...
 off the live analyser.
  if (job.analysed) music.analysed = true;

  const out = {};
  const buf = new Float32Array(h.n * 3);
  for (const name of job.shows) {
    // Warmed up on a separate player, so the timed one starts with no
    // history a stateful cue preset could carry into the comparison.
    const warm = new S.ShowPlayer(D.shows[name], h, D);
    for (const t of job.times) warm.frame(t, music, buf);
    const p = new S.ShowPlayer(D.shows[name], h, D);
    const frames = [], gains = [], labels = [], ms = [];
    for (const t of job.times) {
      const t0 = process.hrtime.bigint();
```

```
$ cd "~/deadmau5 app"; sed -n 60,100p remote/offline/showtest.js; sed -n 40,85p tests_more/scenes.py; grep -n "def bundle" -A45 mau5offline.py | head -90; sed -n 60,72p mau5offline.py; tail -5 mau5offline.py
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
        ts += [a + 0.001, a + 0.05, a + x["beats"] * spb / 2.0]
    ts += list(np.linspace(0.0, duration, even))
    ts += [at(-1) - 0.5, at(spec["bars"]) + 0.5]
    return sorted({round(float(t), 6) for t in ts})


def _compare(name, show, times, res, music, h):
    """Worst difference in counts, and the first label that disagrees."""
    import mau5show
    py = mau5show.Player(show, helmet=h, music=music)
    ok(py.scenes is not None, "%s: the laptop is not playing its scenes" % name)
    ok(res["scenes"], "%s: the phone is not playing its scenes" % name)
    worst, where = 0.0, ""
    for k, t in enumerate(times):
    
... [cut] ...
 "built": time.strftime("%Y-%m-%d"),


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
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
```

```
$ cd "~/deadmau5 app"; grep -n "def _shows" -A32 mau5offline.py | head -60; grep -n "def _b64" -A4 mau5offline.py; grep -n "D\.\w*\|data\.\w*" remote/offline/show.js | grep -v "//" | head -20
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
227-                                      "level", "gain") if k in c}
228-            if c.get("overlay"):
58:def _b64(a, dtype):
59-    return base64.b64encode(np.ascontiguousarray(a, dtype).tobytes()).decode()
60-
61-
62-def bundle():
96:    this.tbl = data.lock;
97:    this.fonts = data.fonts;
385:    this.fonts = data && data.fonts;
```

```
$ KIT=tools/showkit; W="$KIT/work/radio"; cd "~/deadmau5 app"; grep -n "def _drive_entries" -A16 mau5offline.py | head -30; grep -n "open(.*\"w\|makedirs\|\.write(" mau5offline.py | head; grep -n "class _SceneDrive" -A12 tests_more/scenes.py; cat > "$W/parity.py" <<'EOF'
#!/usr/bin/env python3
"""parity.py "<base>": this show on the laptop's renderer against the phone's, under node, with no helmet and no browser."""
import json, math, os, subprocess, sys
sys.path.insert(0, os.getcwd())
import numpy as np, mau5offline, mau5show, mau5engine as E
base = sys.argv[1]
data = mau5offline.bundle()
show = ... [cut]
164:def _drive_entries():
165-    try:
166-        with open(os.path.join(OUT, "drive.json")) as f:
167-            return json.load(f)
168-    except (ValueError, OSError):
169-        return {}
170-
171-
172-def _playlist():
173-    """The set 'Play Music' runs through; shows it leaves out go on the end."""
174-    try:
175-        with open(os.path.join(HERE, "shows", "scenes", "playlist.json")) as f:
176-            return json.load(f)
177-    except (ValueError, OSError):
178-        return []
179-
180-
253:    os.makedirs(OUT, exist_ok=True)
257:    with open(os.path.join(OUT, "data.js"), "w") as f:
258:        f.write(data_js)
288:    with open(plain, "w") as f:
289:        f.write(page)
295:        g.write(raw)
297:    with open(plain + ".gz", "wb") as f:
298:        f.write(gz)
438:                        self.wfile.write(chunk)
30:class _SceneDrive(_ShowDrive):
31-    """test_mau5's drive, marked as an analysis: band values read its curves."""
32-    analysed = True
33-
34-
35-def _scene_times(spec, duration, even=40):
36-    """Where a scene show is most likely to disagree with itself.
37-
38-    Just inside every edge, the middle of everything, inside the peak
39-    hold of every hit, the middle of every dark beat before a drop, a
40-    spread across the song, and one moment either side of it.
41-    """
42-    g = spec["grid"]
phone playing scenes: True | frames 405 | mean 0.047 ms, worst 0.559 ms a frame under node
worst difference 0.00051 counts at t=146.789 two signals b (phone says two signals b)
Sat Oct 31 13:07:41 PDT 2026
```

```
$ KIT=tools/showkit; W="$KIT/work/radio"; cat > "$W/patch6.py" <<'PY'
import os
p=os.environ["W"]+"/write_treatment.py"
s=open(p).read()
def rep(a,b):
    global s
    assert a in s, a[:70]
    s=s.replace(a,b,1)
# the needle drifts off the station while the interference rises
rep('''FALL1 = [(59.0, 0.25)''','''DRIFT1 = [(24.0, 0.25), (25.0, 0.25), (25.5, 0.20), (26.0, 0.20), (26.5, 0.30), (27.0, 0.30), (27.5, 0.13), (28.0, 0.13)]
DRIFT2 = [(88.0, 0.25), (89.0, 0.25), (89.5, 0.31), (90.0, 0.31), (90.5, 0.18), (91.0, 0.18), (91.5, 0.38), (92.0, 0.38)]
FALL1 = [(59.0, 0.25)''')
rep('''  WAVE("wave_t", [0.3, 0 ... [cut]
wrote shows/scenes/deadmau5 - Some Chords (Radio Edit).scene.json scenes 28 hits 9
deadmau5 - Some Chords (Radio Edit): 29 scenes, 9 hits, written into shows/deadmau5 - Some Chords (Radio Edit).json
bar 24.5    drift      sent  621 mA  shell max  58 mean   9.7  ears max  96 mean  19.0  interference
bar 25.3    drift      sent  537 mA  shell max  61 mean   8.8  ears max  94 mean  15.6  interference
bar 25.8    drift      sent  577 mA  shell max  50 mean   9.7  ears max 108 mean  16.4  interference
bar 26.3    drift      sent  539 mA  shell max  56 mean   9.8  ears max  82 mean  14.1  interference
bar 26.8    drift      sent  512 mA  shell max  51 mean   9.7  ears max  92 mean  12.5  interference
bar 27.3    drift      sent  524 mA  shell max  55 mean   9.8  ears max 110 mean  13.3  interference
bar 27.7    drift      sent  599 mA  shell max  52 mean   9.8  ears max 130 mean  17.7  interference
bar 27.8    dark       sent    8 mA  shell max  61 mean   0.3  ears max   0 mean   0.0  interference · BEACON
bar 88.5    drift2     sent  701 mA  shell max  58 mean   9.7  ears max  97 mean  23.8  interference2
bar 89.3    drift2     sent  567 mA  shell max  59 mean   8.8  ears max  91 mean  17.4  interference2
bar 90.3    drift2     sent  529 mA  shell max  55 mean   9.7  ears max 104 mean  13.6  interference2
bar 91.3    drift2     sent  481 mA  shell max  62 mean   9.7  ears max 108 mean  10.9  interference2
tools/showkit/songs/radio/g7.png (1800, 490)
Sat Oct 31 13:08:37 PDT 2026
```

```
$ KIT=tools/showkit; W="$KIT/work/radio"; cat > "$W/patch6.py" <<'PY'
import os
p=os.environ["W"]+"/write_treatment.py"
s=open(p).read()
def rep(a,b):
    global s
    assert a in s, a[:70]
    s=s.replace(a,b,1)
# the needle drifts off the station while the interference rises
rep('''FALL1 = [(59.0, 0.25)''','''DRIFT1 = [(24.0, 0.25), (25.0, 0.25), (25.5, 0.20), (26.0, 0.20), (26.5, 0.30), (27.0, 0.30), (27.5, 0.13), (28.0, 0.13)]
DRIFT2 = [(88.0, 0.25), (89.0, 0.25), (89.5, 0.31), (90.0, 0.31), (90.5, 0.18), (91.0, 0.18), (91.5, 0.38), (92.0, 0.38)]
FALL1 = [(59.0, 0.25)''')
rep('''  WAVE("wave_t", [0.3, 0 ... [cut]
wrote shows/scenes/deadmau5 - Some Chords (Radio Edit).scene.json scenes 28 hits 9
deadmau5 - Some Chords (Radio Edit): 29 scenes, 9 hits, written into shows/deadmau5 - Some Chords (Radio Edit).json
bar 24.5    drift      sent  621 mA  shell max  58 mean   9.7  ears max  96 mean  19.0  interference
bar 25.3    drift      sent  537 mA  shell max  61 mean   8.8  ears max  94 mean  15.6  interference
bar 25.8    drift      sent  577 mA  shell max  50 mean   9.7  ears max 108 mean  16.4  interference
bar 26.3    drift      sent  539 mA  shell max  56 mean   9.8  ears max  82 mean  14.1  interference
bar 26.8    drift      sent  512 mA  shell max  51 mean   9.7  ears max  92 mean  12.5  interference
bar 27.3    drift      sent  524 mA  shell max  55 mean   9.8  ears max 110 mean  13.3  interference
bar 27.7    drift      sent  599 mA  shell max  52 mean   9.8  ears max 130 mean  17.7  interference
bar 27.8    dark       sent    8 mA  shell max  61 mean   0.3  ears max   0 mean   0.0  interference · BEACON
bar 88.5    drift2     sent  701 mA  shell max  58 mean   9.7  ears max  97 mean  23.8  interference2
bar 89.3    drift2     sent  567 mA  shell max  59 mean   8.8  ears max  91 mean  17.4  interference2
bar 90.3    drift2     sent  529 mA  shell max  55 mean   9.7  ears max 104 mean  13.6  interference2
bar 91.3    drift2     sent  481 mA  shell max  62 mean   9.7  ears max 108 mean  10.9  interference2
tools/showkit/songs/radio/g7.png (1800, 490)
Sat Oct 31 13:08:37 PDT 2026
```

```
$ KIT=tools/showkit; W="$KIT/work/radio"; cd "~/deadmau5 app"; B="deadmau5 - Some Chords (Radio Edit)"; python3 - "$W/write_treatment.py" <<'PY'
import sys
p=sys.argv[1]; s=open(p).read()
a="At 24 the drums pull out, so the sine flattens and static creeps back, one dark beat"
assert a in s
s=s.replace(a,"At 24 the drums pull out, so the sine flattens, the needle drifts off the station and static creeps back, one dark beat")
open(p,"w").write(s)
PY
python3 "$W/write_treatment.py" && python3 mau5scene.py compile "$B" 2>&1 | grep -iE "warn|error|scenes, "; python3 mau5scene.py check "$B" 2>&1 | tail ... [cut]
wrote shows/scenes/deadmau5 - Some Chords (Radio Edit).scene.json scenes 28 hits 9
deadmau5 - Some Chords (Radio Edit): 29 scenes, 9 hits, written into shows/deadmau5 - Some Chords (Radio Edit).json
deadmau5 - Some Chords (Radio Edit): 5250 frames at 25 fps through the guard
  scene            from  mean mA   p95 mA     heat   allow W      ms
  tuning           0.0s      548      714     1.5%      18.1    0.15
  locked          15.2s      644      855     2.6%      18.1    0.14
  drums           22.6s      577      797     3.4%      18.1    0.14
  signal          30.2s      580     1000     4.3%      18.1    0.13
  signal2         37.6s      605      897     5.2%      18.1    0.12
  interference    45.2s      516      682     5.9%      18.1    0.17
  ON AIR          52.6s      508      852     6.2%      18.1    0.12
  on air          56.4s      446      904     6.9%      18.1    0.13
  ON AIR b        67.6s      502      791     7.0%      18.1    0.11
  on air b        69.5s      469      998     7.9%      18.1    0.14
  ON AIR c        82.6s      515      776     8.1%      18.1    0.12
  stereo          84.5s      493      909     9.1%      18.1    0.15
  ON AIR d        97.6s      517      769     9.3%      18.1    0.12
  the radio       99.5s      465      904    10.1%      18.1    0.15
  slip           110.8s      582      820    10.3%      18.1    0.12
  sign-off       112.6s      415      575    10.7%      18.1    0.28
  retune         120.2s      503      693    11.9%      18.1    0.15
  two signals    135.2s      678      989    13.0%      18.1    0.15
  two signals    142.7s      569      911    14.7%      18.1    0.14
  two signals    157.7s      587      951    15.5%      18.1    0.14
  interference   165.2s      520      676    16.3%      18.1    0.16
  ON A
... [cut] ...
/claude-501/-Users-jones-deadmau5-app/208332e7-8c9f-4c25-bc21-e9a9df98fa1f/scratchpad/kit/work/radio/final.png (1799, 1881)
tools/showkit/songs/radio/final_preguard.png (1800, 490)
?? "shows/deadmau5 - Some Chords (Radio Edit).analysis.npz"
?? "shows/deadmau5 - Some Chords (Radio Edit).json"
?? "shows/scenes/deadmau5 - Some Chords (Radio Edit).beats"
?? "shows/scenes/deadmau5 - Some Chords (Radio Edit).scene.json"
?? "shows/scenes/deadmau5 - Some Chords (Radio Edit).sprites.json"
Sat Oct 31 13:08:56 PDT 2026
```
