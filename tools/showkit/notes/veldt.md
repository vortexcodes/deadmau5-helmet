# What the veldt builder ran and saw

Commands and their text output, in order, with long output cut. Images are left out; rerun the tools to see them. Cut off partway: the generator and treatment in the repo are the latest state.

I'll start by reading the brief.

```
$ date; cat "tools/showkit/BRIEF.md"; ls -la "tools/showkit/"
Sat Oct 31 12:39:05 PDT 2026
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
$ KIT="tools/showkit"; cat "(scratch)/tiki/write_treatment.py"; echo ------; cat "$KIT/fmt.py"; echo ------; cat "$KIT/grid.py"; echo -----; cat "$KIT/sheet.py"; echo -----; cat "$KIT/songmap.py"; echo ----; cat "$KIT/spectro.py"; echo ----; cat "$KIT/spritetry.py"; ls -la "$KIT/work"
<persisted-output>
Output too large (34.9KB). Full output saved to: ~/.claude/projects/-Users-jones-deadmau5-app/208332e7-8c9f-4c25-bc21-e9a9df98fa1f/tool-results/bdbpkhl17.txt

Preview (first 2KB):
import json
KICK="x.......x......."
idolp={"sprite":"tiki","y_lo":-108,"y_hi":166,"x_half":171}
tr={"v":1,"show":"TIKI TIKI - Slowed",
"about":"Bars of a measured grid, shows/scenes/TIKI TIKI - Slowed.beats: bar b starts at 1.796 + 1.739 b seconds (137.98 BPM), 183 bars, and at bar 119.5 the track is spliced, so the music comes back 197 ms late and the grid holds still for it. Everything from there is the song's opening again, bar for bar. The bar line is where the phrases turn, with the kick on 1 and 3 and the clap on 2 and 4 with a flick on the and of 2. A night on the island. Torches get lit one tube at a time; the hooks are fire climbing the shell with the ears burning as torches, the kick on the rims and the clap up the tubes. Every breakdown goes out to the lagoon, cold water and moon glints, with one stopped bar of almost nothing, and the title crosses the face once, in the first. The verses are bamboo: upright stalks swaying on the face, the two sides stomping in turn. The big sections wake the idol, a carved mask drawn to fit the LEDs that exist: brow and eyes on the dome, teeth along the jaw, since the middle of the face has no LEDs. It burns in torch colours the first time, at sunset the second, and half fire, half water the third, swapping sides. The song then starts over, so the show does too, and the last big section has everything, with white once. At the end the torches go out one tube at a time and the idol is last to go. Shell layers are kept near the shell's 300 mA and nothing on it pulses faster than a beat.",
"lead":0,
"marks":{"hush":2,"light":3,"hook":5,"hookb":9,"dip":13,"climb":14,"hook2":15,"burn":21,
 "water":25,"stop":26,"still":27,"swell":30,"verse":31,"vlow":37,"vrise":38,"big":39,"bigb":47,"burn2":57,
 "water2":61,"stop2":62,"still2":63,"swell2":66,"verse2":67,"vlow2":73,"vrise2":74,"big2":75,"big2b":83,"burn3":89,
 "water3":93,"stop3":94,"still3":95,"swell3":98,"verse3":99,"vlow3":105,"vrise3":106,"big3":107,"big3b":113,"big3c":117,
...
</persisted-output>
```

```
$ cd "~/deadmau5 app"; ls -la shows/ | head -60; ls -la shows/scenes/ | head -60; python3 -c "
import json
d=json.load(open('shows/scenes/TIKI TIKI - Slowed.scene.json'))
print(d.keys())
print(d['about'])
print(d['marks'])
print(len(d['scenes']),len(d['hits']))
"; cat "shows/scenes/deadmau5 - The Veldt.beats" 2>/dev/null; ls -la "shows/scenes/" | grep -i veldt
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
7.688650
148.157375
148.626100
149.094825
149.563550
150.032275
150.501000
150.969725
151.438450
151.907175
152.375900
152.844625
153.313350
153.782075
154.250800
154.719525
155.188250
155.656975
156.125700
156.594425
157.063150
157.531875
158.000600
158.469325
158.938050
159.406775
159.875500
160.344225
160.812950
161.281675
161.750400
162.219125
162.687850
163.156575
163.625300
164.094025
164.562750
165.031475
165.500200
165.968925
166.437650
166.906375
167.375100
167.843825
168.312550
168.781275
169.250000
169.718725
-rw-r--r--@  1 jones  staff   3748 Oct 31 12:37 deadmau5 - The Veldt.beats
```

```
$ KIT="tools/showkit"; cat "(scratch)/tiki/write_treatment.py"; echo ------; cat "$KIT/fmt.py"; echo ------; cat "$KIT/grid.py"; echo -----; cat "$KIT/sheet.py"; echo -----; cat "$KIT/songmap.py"; echo ----; cat "$KIT/spectro.py"; echo ----; cat "$KIT/spritetry.py"; ls -la "$KIT/work"
<persisted-output>
Output too large (34.9KB). Full output saved to: ~/.claude/projects/-Users-jones-deadmau5-app/208332e7-8c9f-4c25-bc21-e9a9df98fa1f/tool-results/bdbpkhl17.txt

Preview (first 2KB):
import json
KICK="x.......x......."
idolp={"sprite":"tiki","y_lo":-108,"y_hi":166,"x_half":171}
tr={"v":1,"show":"TIKI TIKI - Slowed",
"about":"Bars of a measured grid, shows/scenes/TIKI TIKI - Slowed.beats: bar b starts at 1.796 + 1.739 b seconds (137.98 BPM), 183 bars, and at bar 119.5 the track is spliced, so the music comes back 197 ms late and the grid holds still for it. Everything from there is the song's opening again, bar for bar. The bar line is where the phrases turn, with the kick on 1 and 3 and the clap on 2 and 4 with a flick on the and of 2. A night on the island. Torches get lit one tube at a time; the hooks are fire climbing the shell with the ears burning as torches, the kick on the rims and the clap up the tubes. Every breakdown goes out to the lagoon, cold water and moon glints, with one stopped bar of almost nothing, and the title crosses the face once, in the first. The verses are bamboo: upright stalks swaying on the face, the two sides stomping in turn. The big sections wake the idol, a carved mask drawn to fit the LEDs that exist: brow and eyes on the dome, teeth along the jaw, since the middle of the face has no LEDs. It burns in torch colours the first time, at sunset the second, and half fire, half water the third, swapping sides. The song then starts over, so the show does too, and the last big section has everything, with white once. At the end the torches go out one tube at a time and the idol is last to go. Shell layers are kept near the shell's 300 mA and nothing on it pulses faster than a beat.",
"lead":0,
"marks":{"hush":2,"light":3,"hook":5,"hookb":9,"dip":13,"climb":14,"hook2":15,"burn":21,
 "water":25,"stop":26,"still":27,"swell":30,"verse":31,"vlow":37,"vrise":38,"big":39,"bigb":47,"burn2":57,
 "water2":61,"stop2":62,"still2":63,"swell2":66,"verse2":67,"vlow2":73,"vrise2":74,"big2":75,"big2b":83,"burn3":89,
 "water3":93,"stop3":94,"still3":95,"swell3":98,"verse3":99,"vlow3":105,"vrise3":106,"big3":107,"big3b":113,"big3c":117,
...
</persisted-output>
```

```
$ cd "~/deadmau5 app"; ls -la shows/ | head -60; ls -la shows/scenes/ | head -60; python3 -c "
import json
d=json.load(open('shows/scenes/TIKI TIKI - Slowed.scene.json'))
print(d.keys())
print(d['about'])
print(d['marks'])
print(len(d['scenes']),len(d['hits']))
"; cat "shows/scenes/deadmau5 - The Veldt.beats" 2>/dev/null; ls -la "shows/scenes/" | grep -i veldt
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
7.688650
148.157375
148.626100
149.094825
149.563550
150.032275
150.501000
150.969725
151.438450
151.907175
152.375900
152.844625
153.313350
153.782075
154.250800
154.719525
155.188250
155.656975
156.125700
156.594425
157.063150
157.531875
158.000600
158.469325
158.938050
159.406775
159.875500
160.344225
160.812950
161.281675
161.750400
162.219125
162.687850
163.156575
163.625300
164.094025
164.562750
165.031475
165.500200
165.968925
166.437650
166.906375
167.375100
167.843825
168.312550
168.781275
169.250000
169.718725
-rw-r--r--@  1 jones  staff   3748 Oct 31 12:37 deadmau5 - The Veldt.beats
```

```
$ cd "~/deadmau5 app"; KIT="tools/showkit"; mkdir -p "$KIT/work/veldt"; time python3 "$KIT/grid.py" scan "shows/deadmau5 - The Veldt.mp3" 2>&1 | tail -20; python3 mau5scene.py bars "deadmau5 - The Veldt" 2>&1 | head -30; ffprobe -hide_banner "shows/deadmau5 - The Veldt.mp3" 2>&1 | tail -8; cat "shows/deadmau5 - The Veldt.json" | python3 -c "
import json,sys
d=json.load(sys.stdin)
print(d.keys())
print({k:(v if not isinstance(v,(list,dict)) else type(v)) for k,v in d.items()})
print(d.get('scenes',{}).keys() if isinstance(d.get('scenes'),dict) else '')
print(d.get('scenes',{}).get('grid') if isins ... [cut]
estimator: 128.008 BPM, first bar 0.509 s, tempo lock 0.781, bar lock 0.2563047481780256; song 170.1 s
refined over the whole song: spb 0.468725 = 128.007 BPM
first half 128.007 BPM, second half 128.007 BPM (these should agree within 0.05)
phase of the music against that grid per 8 bars, ms (flat = right; one 16th = 117 ms; contrast under 1.15 means sparse, ignore it):
  0:+1(8.14)  8:+1(3.20)  16:+3(1.82)  24:+1(2.11)  32:-1(1.71)  40:+1(1.93)  48:+3(2.14)  56:+5(2.07)  64:+1(2.62)  72:+3(2.40)  80:+3(2.17)  88:+7(1.44)
change per beat position, estimator's bar 1 at 0.509 s: 0:0.85 1:0.73 2:0.89 3:1.02  (the highest is where bars really start, 0 = estimator is right)
strongest phrase positions, in beats mod 32 from that bar 1: 31(1.77), 0(1.41), 30(1.31), 10(1.16), 26(1.15), 27(1.06)
biggest single changes (time, beat from bar 1, beat mod 4): 15.0s b31 m3; 19.7s b41 m1; 20.2s b42 m2; 26.3s b55 m3; 28.2s b59 m3; 30.5s b64 m0; 36.1s b76 m0; 42.7s b90 m2; 43.2s b91 m3; 44.6s b94 m2; 45.0s b95 m3; 46.0s b97 m1; 63.8s b135 m3; 68.0s b144 m0; 71.3s b151 m3; 75.5s b160 m0; 78.8s b167 m3; 81.1s b172 m0; 119.1s b253 m1; 119.6s b254 m2; 165.0s b351 m3; 165.5s b352 m0; 166.0s b353 m1; 166.4s b354 m2
suggested next: grid.py fold with --spb 0.468725 --anchor 0.509, decide the bar line, then grid.py write
python3 "$KIT/grid.py" scan "shows/deadmau5 - The Veldt.mp3" 2>&1  0.71s user 0.10s system 97% cpu 0.825 total
tail -20  0.00s user 0.00s system 0% cpu 0.825 total
     0     0.51s  energy 0.27  bass 0.37 (punch 0.86)  mid 0.40  high 0.20
     1     2.38s  energy 0.24  bass 0.01 (punch 1.00)  mid 0.42  high 0.21
     2     4.26s  energy 0.38  bass 0.34 (punch 0.83)  mid 0.52  high 0.20
     3     6.13s  energy 0.46  bass 0.64 (punch 0.65)  mid 0.50  high 0.16
     4     8.01s  ener
... [cut] ...
 The Veldt.mp3':
  Metadata:
    encoder         : Lavf58.20.100
  Duration: 00:02:50.14, start: 0.025057, bitrate: 256 kb/s
  Stream #0:0: Audio: mp3 (mp3float), 44100 Hz, stereo, fltp, 256 kb/s, start 0.025057
    Metadata:
      encoder         : Lavc58.35
dict_keys(['track', 'fps', 'duration', 'bpm', 'beats', 'analysis', 'fade', 'accent', 'pulse', 'lock', 'cues'])
{'track': 'deadmau5 - The Veldt.mp3', 'fps': 40, 'duration': 170.14, 'bpm': 128.01, 'beats': 362, 'analysis': 'deadmau5 - The Veldt.analysis.npz', 'fade': 0.45, 'accent': True, 'pulse': 0.4, 'lock': False, 'cues': <class 'list'>}
```

```
$ cd "~/deadmau5 app"; KIT="tools/showkit"; python3 "$KIT/grid.py" fold "shows/deadmau5 - The Veldt.mp3" --spb 0.468725 --anchor 0.509 2>&1 ; python3 "$KIT/songmap.py" "deadmau5 - The Veldt" 2>&1; python3 "$KIT/spectro.py" "deadmau5 - The Veldt" "$KIT/work/veldt/spec_all.png" 2>&1
bar 0 at 0.509 s, 128.007 BPM, 90 bars
bars 0-16   (16 steps, | every beat; one row per band)
   sub     %:::|%.::|@.::|@...   peak 0.45
   bass    @---|#==-|%=--|%---   peak 0.33
   lowmid  #=%-|@+#:|%+%-|@=%-   peak 0.25
   mid     @.# |% % |@.# |@ %    peak 0.67
   pres    @ * |@ + |@ * |@ +    peak 0.91
   air     * = |# = |% = |@ =.   peak 0.66
bars 16-32   (16 steps, | every beat; one row per band)
   sub     @...|%.::|@.::|@ ..   peak 0.80
   bass    @-=-|#-::|@---|@--.   peak 0.54
   lowmid  @=%.|#=+:|@-#.|#=#:   peak 0.36
   mid     - * |%.# |= * |@ #    peak 0.73
   pres    - = |@ = |- -.|@ -    peak 1.02
   air     - - |@ - |- -.|@.-    peak 0.83
bars 32-48   (16 steps, | every beat; one row per band)
   sub     @...|@.:.|@..:|@ ..   peak 0.79
   bass    @:::|#:::|@-::|#::.   peak 0.58
   lowmid  %+@=|@=*:|%=*:|#+%-   peak 0.30
   mid     =.* |%.# |=.# |@.#    peak 0.65
   pres    = - |@ = |- = |@ -    peak 0.94
   air     =.= |%.= |- + |@.+.   peak 0.72
bars 48-64   (16 steps, | every beat; one row per band)
   sub     @ ..|@...|@...|%...   peak 0.78
   bass    @--:|*-::|@--:|%-::   peak 0.58
   lowmid  %%#+|#%*-|*#*=|@#%=   peak 0.21
   mid     *:%.|#-#.|+-%.|@-#.   peak 0.38
   pres    +.+ |@.= |-.=.|@.+    peak 0.72
   air     - * |@.* |- *:|%.*.   peak 0.79
bars 64-80   (16 steps, | every beat; one row per band)
   sub     %:-=|%--=|@---|@::-   peak 0.56
   bass    @+=+|%+++|@=+-|#+=-   peak 0.41
   lowmid  @=@-|#=%:|@=%-|%+@:   peak 0.26
   mid     +.% |@.% |+:@ |@.#    peak 0.46
   pres    + *.|@.+ |=.+.|@.+.   peak 0.61
   air     = #.|@.#.|+ *:|@.#:   peak 0.62
bars 80-90   (16 steps, | every beat; one row per band)
   sub     @:..|@ ..|@..:|@...   peak 0.66
   bass    @=:-|@--:|@-::|%=-:   peak 0.38
   lowmid  ##@*|@#*=|@%#=|%=+=   peak 0.17
   mid 
... [cut] ...
    
  79  148.6   8  7  6  6  A C F       
  80  150.5   9  9  8  5  C F A       
  81  152.4   7  7  7  4  A C E       
  82  154.3   8  7  8  7  A C E       
  83  156.1   7  7  8  7  A C E       
  84  158.0   7  7  9  5  A E C       
  85  159.9   9  8  8  5  C E A       
  86  161.8   9  8  9  8  A C F       
  87  163.6   7  5  8  7  A E F       
  88  165.5   0  0  0  1  A E A#      >>
  89  167.4   0  0  0  0  A E B       
  90  169.2   0  0  0  0  A E B       
tools/showkit/songs/veldt/spec_all.png
```

```
$ cd "~/deadmau5 app"; KIT="tools/showkit"; W="$KIT/work/veldt"; python3 "$KIT/spectro.py" "deadmau5 - The Veldt" "$W/s0_12.png" 0 12; python3 "$KIT/spectro.py" "deadmau5 - The Veldt" "$W/s60_72.png" 60 74; cat > "$W/beatfold.py" <<'EOF'
import sys, numpy as np, subprocess
# Beat-resolved energy per band for a span: one row per bar, one cell per 16th: see where the kick and claps fall and when things start.
mp3="shows/deadmau5 - The Veldt.mp3"; SR=22050
raw=subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-i",mp3,"-ac","1","-ar",str(SR),"-f","f32le","-"],capture_output=True,check=True ... [cut]
tools/showkit/songs/veldt/s0_12.png
tools/showkit/songs/veldt/s60_72.png
total 8024
drwxr-xr-x@  7 jones  wheel      224 Oct 31 12:39 .
drwxr-xr-x@ 22 jones  wheel      704 Oct 31 12:39 ..
-rw-r--r--@  1 jones  wheel  1407850 Oct 31 12:39 E.npz
-rw-r--r--@  1 jones  wheel      902 Oct 31 12:39 beatfold.py
-rw-r--r--@  1 jones  wheel   799098 Oct 31 12:39 s0_12.png
-rw-r--r--@  1 jones  wheel   864306 Oct 31 12:39 s60_72.png
-rw-r--r--@  1 jones  wheel  1020361 Oct 31 12:39 spec_all.png
```

```
$ cd "~/deadmau5 app"; KIT="tools/showkit"; W="$KIT/work/veldt"; cat > "$W/barimg.py" <<'EOF'
import sys, numpy as np
from PIL import Image, ImageDraw
# One row per bar, 96 columns per bar, one panel per band: bar lines and sections read as rows turning.
z=np.load(sys.argv[1]); out=sys.argv[2]; spb=float(sys.argv[3]); anchor=float(sys.argv[4])
tt=z["tt"]
bands=["sub","low","mid","pres","air"]
bar=4*spb
t0=anchor%bar
nb=int((tt[-1]-t0)/bar)+1
W=96; S=4; 
panels=[]
for k in bands:
    e=np.log1p(z[k]*0.2); 
    e=e/np.percentile(e,99.5)
    img=np.zeros((nb,W))
    for b in range(nb):
        ts=t0 ... [cut]
tools/showkit/songs/veldt/bars_m0.png (1530, 384) t0 0.509
tools/showkit/songs/veldt/bars_m3.png (1530, 384) t0 0.040275
```

```
$ cd "~/deadmau5 app"; KIT="tools/showkit"; W="$KIT/work/veldt"; cat > "$W/prof.py" <<'EOF'
import numpy as np, sys
z=np.load(sys.argv[1]); spb=0.468725; t0=0.040275
tt=z["tt"]
bar=4*spb
lo,hi=int(sys.argv[2]),int(sys.argv[3])
CH=" .:-=+*#%@"
for k in ["sub","low","mid","pres","air"]:
    e=np.log1p(z[k]*0.2)
    P=np.zeros(48)
    for b in range(lo,hi):
        ts=t0+(b+np.arange(48)/48)*bar
        i=np.clip(np.searchsorted(tt,ts),0,len(tt)-1)
        P+=e[i]
    P/=max(hi-lo,1)
    v=(P-P.min())/(P.max()-P.min()+1e-9)
    print("%-5s "%k+"|".join("".join(CH[min(9,int(a*9.99))] for a in v[i:i+1 ... [cut]
Exit code 1
bars 8 16 (bar line at 0.0403, each | is a beat)
Traceback (most recent call last):
  File "tools/showkit/songs/veldt/prof.py", line 5, in <module>
    lo,hi=int(sys.argv[2]),int(sys.argv[3])
ValueError: invalid literal for int() with base 10: '8 16'
bars 16 24 (bar line at 0.0403, each | is a beat)
Traceback (most recent call last):
  File "tools/showkit/songs/veldt/prof.py", line 5, in <module>
    lo,hi=int(sys.argv[2]),int(sys.argv[3])
ValueError: invalid literal for int() with base 10: '16 24'
bars 32 40 (bar line at 0.0403, each | is a beat)
Traceback (most recent call last):
  File "tools/showkit/songs/veldt/prof.py", line 5, in <module>
    lo,hi=int(sys.argv[2]),int(sys.argv[3])
ValueError: invalid literal for int() with base 10: '32 40'
bars 48 56 (bar line at 0.0403, each | is a beat)
Traceback (most recent call last):
  File "tools/showkit/songs/veldt/prof.py", line 5, in <module>
    lo,hi=int(sys.argv[2]),int(sys.argv[3])
ValueError: invalid literal for int() with base 10: '48 56'
bars 56 64 (bar line at 0.0403, each | is a beat)
Traceback (most recent call last):
  File "tools/showkit/songs/veldt/prof.py", line 5, in <module>
    lo,hi=int(sys.argv[2]),int(sys.argv[3])
ValueError: invalid literal for int() with base 10: '56 64'
bars 72 80 (bar line at 0.0403, each | is a beat)
Traceback (most recent call last):
  File "tools/showkit/songs/veldt/prof.py", line 5, in <module>
    lo,hi=int(sys.argv[2]),int(sys.argv[3])
ValueError: invalid literal for int() with base 10: '72 80'
bars 80 88 (bar line at 0.0403, each | is a beat)
Traceback (most recent call last):
  File "tools/showkit/songs/veldt/prof.py", line 5, in <module>
    lo,hi=int(sys.argv[2]),int(sys.argv[3])
ValueError: invalid literal for int() with base 10: '80 88'
```

```
$ cd "~/deadmau5 app"; KIT="tools/showkit"; W="$KIT/work/veldt"; for span in "8 16" "16 24" "32 40" "48 56" "56 64" "72 80" "80 88"; do echo "bars $span (bar line at 0.0403, each | is a beat)"; a=${span% *}; b=${span#* }; python3 "$W/prof.py" "$W/E.npz" $a $b; done
bars 8 16 (bar line at 0.0403, each | is a beat)
sub   .@=:  . ....|.@*...  ..:.|:@+    ....:|:@+   . ...:
low   % .=+**#####|@ .=+##%%%%%|@ :+########|@ .=*##%%%%%
mid   @ :=++@@%##*|@.:-++%@@%%*|@ :=*+#@@%#+|% .=++#@%#**
pres  @..:::**=:--|@::::-+*=--:|@..:::++=:::|@  . .+=-:::
air   @:--==##+=**|@::::=#*++==|@::-:-+=+---|@  ...=-=-::
bars 16 24 (bar line at 0.0403, each | is a beat)
sub   .@+:.....:::|:@*: ..:.:::|-@*:.....:::|.@+:  :.:::-
low   @ :=+####%%#|@: -+**#%###|@ .=+*######|%-:=+**#%%%%
mid   % ::-=#%%#*+|@ :=+=#@%%#+|@ :-+=#%%*=+|@ :--=*#*+==
pres  #  ..:=-:. +|@--:. --::..|%     =-::.*|@--..:=-:..:
air   *   .::::  +|@-+:: .::::.|*     .::..#|@-=  .:. ..:
bars 32 40 (bar line at 0.0403, each | is a beat)
sub   .@*:  ....::|.@+....  ...|:@+:  ...:::|.@*:  . ...:
low   % :-+++#####|@:.-=+*#%###|% .=+**##%%#|@: -=+**###*
mid   %.-=+=*%#*++|@.:---*@##*+|% :==-#%#+==|@ .:--#@#**+
pres  %..:.:=--::+|@--::-+--:::|#  ...=-.  =|@:-...--.. .
air   #..::-+=-=-*|@-+--+*----:|* ... -:.. +|@=+.  -:....
bars 48 56 (bar line at 0.0403, each | is a beat)
sub   .@+.  . ...:|.@+..   ...:| @*.  ....:.|.@+... ..:::
low   # .+*#*#####|@:.-+**##%##|% :=****####|@: -+*******
mid   %.-+++#@%%%%|@.:=+*@@%%##|% .=**#@%###|@ :-+*#@%%#*
pres  #  ...++=-:-|@::. .++=-::|%  ...==--.=|@:: . ==---:
air   *  . .*=-:.=|@=+. .+=::..|*     ==:..+|@=+.  +-::-:
bars 56 64 (bar line at 0.0403, each | is a beat)
sub   :@*: ...::::|:@*- ..:::::|:@*-.:::::-:|.@+:..::::::
low   @.-+****####|@--=*##%#%##|@ .-+**#####|@-:=*##%%%%#
mid   % :=*#%@%%%%|@ :+*#%@@%%#|@ :+**%@@##%|@ -=+*%@%**#
pres  # .::-*+==-=|@::::-=+===-|# .::--=---=|%.:.::==-===
air   *  ..:++-:.=|@=+.::-=-:. |+     --:. =|%-=   =-:::.
bars 72 80 (bar line at 0.0403, each | is a beat)
sub   .@*: ....:::|:@*: ......:|:@*:. ...:::|.@+: .:.::--
low   % .-++*###*#|@:.=+****#**|% .-=+**#***|%-.-++*%%%##
mid   %:-==-*@%#*=|@:::--#@%**+|% :-==#%#+==|@ .:--%@#+=-
pres  #... .=-:..+|@--. .+=:::.|#  ...=-:. +|@--   =-....
air   *     =-.:.+|@=+. .=:... |*     -:...+|@=+.  =: ...
bars 80 88 (bar line at 0.0403, each | is a beat)
sub   .@*:  ......|.@+  .   ..:|.@+.. ......|.@+:. .....:
low   %.:+*######%|@::=+*#**#**|# :=**######|%-:=+*#*####
mid   #.-++**%%###|@ :=++#@@#*#|% :=++#%%#**|% :==+#%%#**
pres  %  ...++-:.=|@::. .===-::|#  ...==-:.-|@::  .=+---:
air   #. ...==...+|@=+..:=-:.. |*     =-.. +|@=+. .==.:::
```

```
$ cd "~/deadmau5 app"; KIT="tools/showkit"; W="$KIT/work/veldt"; cat > "$W/check_clap.py" <<'EOF'
import numpy as np, subprocess
mp3="shows/deadmau5 - The Veldt.mp3"; SR=22050
raw=subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-i",mp3,"-ac","1","-ar",str(SR),"-f","f32le","-"],capture_output=True,check=True).stdout
m=np.frombuffer(raw,dtype=np.float32).copy()
spb=0.468725
# high-pass by differencing a few times + band-limited RMS in 2 ms steps around each beat, averaged over a span, per beat position on the 0.0403 grid
from numpy.fft import rfft, irfft, rfftfreq
def band(x,a,b):
     ... [cut]
sub 30-110
 bars 16 24 peak per beat position (rms) and time of the rise in ms from the beat:
   beat 0 (t=0.040 on bar line grid): peak 1.072 at +28 ms; half-rise at +20 ms; before-beat level 0.173
   beat 1 (t=0.509 on bar line grid): peak 1.002 at +28 ms; half-rise at +20 ms; before-beat level 0.168
   beat 2 (t=0.978 on bar line grid): peak 1.060 at +28 ms; half-rise at +20 ms; before-beat level 0.183
   beat 3 (t=1.446 on bar line grid): peak 1.053 at +28 ms; half-rise at +20 ms; before-beat level 0.183
 bars 32 40 peak per beat position (rms) and time of the rise in ms from the beat:
   beat 0 (t=0.040 on bar line grid): peak 1.040 at +28 ms; half-rise at +20 ms; before-beat level 0.198
   beat 1 (t=0.509 on bar line grid): peak 1.023 at +28 ms; half-rise at +20 ms; before-beat level 0.176
   beat 2 (t=0.978 on bar line grid): peak 1.049 at +28 ms; half-rise at +20 ms; before-beat level 0.159
   beat 3 (t=1.446 on bar line grid): peak 1.013 at +28 ms; half-rise at +20 ms; before-beat level 0.169
 bars 72 80 peak per beat position (rms) and time of the rise in ms from the beat:
   beat 0 (t=0.040 on bar line grid): peak 1.021 at +28 ms; half-rise at +20 ms; before-beat level 0.170
   beat 1 (t=0.509 on bar line grid): peak 1.028 at +28 ms; half-rise at +20 ms; before-beat level 0.177
   beat 2 (t=0.978 on bar line grid): peak 1.049 at +28 ms; half-rise at +20 ms; before-beat level 0.178
   beat 3 (t=1.446 on bar line grid): peak 1.045 at +28 ms; half-rise at +20 ms; before-beat level 0.176
pres 2-5k
 bars 16 24 peak per beat position (rms) and time of the rise in ms from the beat:
   beat 0 (t=0.040 on bar line grid): peak 0.177 at +8 ms; half-rise at +4 ms; before-beat level 0.019
   beat 1 (t=0.509 on bar line grid): peak 0.228 at +0 ms; half-rise at -20 ms; befo
... [cut] ...
   beat 3 (t=1.446 on bar line grid): peak 0.172 at +0 ms; half-rise at -24 ms; before-beat level 0.061
 bars 72 80 peak per beat position (rms) and time of the rise in ms from the beat:
   beat 0 (t=0.040 on bar line grid): peak 0.091 at +4 ms; half-rise at +4 ms; before-beat level 0.019
   beat 1 (t=0.509 on bar line grid): peak 0.167 at +0 ms; half-rise at -20 ms; before-beat level 0.046
   beat 2 (t=0.978 on bar line grid): peak 0.086 at +8 ms; half-rise at +4 ms; before-beat level 0.011
   beat 3 (t=1.446 on bar line grid): peak 0.179 at +0 ms; half-rise at -24 ms; before-beat level 0.059
```

```
$ cd "~/deadmau5 app"; KIT="tools/showkit"; W="$KIT/work/veldt"; cat > "$W/phasecheck.py" <<'EOF'
import sys, os
sys.path.insert(0, os.getcwd()); sys.path.insert(0, sys.argv[1])
import numpy as np, grid
d=grid.env_of("shows/deadmau5 - The Veldt.mp3")
for spb in (0.468725,0.468735,0.468745,0.46875,0.468755):
    rows,t0=grid.phase_table(d,spb,0.040275)
    vals=[r[1] for r in rows if r[2]>=1.15]
    print("spb %.6f  BPM %.3f  mean %+.1f  span %.1f   "%(spb,60/spb,np.mean(vals),max(vals)-min(vals))+"  ".join("%d:%+.0f"%(r[0],r[1]) for r in rows))
EOF
python3 "$W/phasecheck.py" "$KIT"; cat > "$W/kic ... [cut]
spb 0.468725  BPM 128.007  mean +2.6  span 10.0   0:+1  8:+1  16:-1  24:+1  32:-1  40:+1  48:+3  56:+5  64:+1  72:+3  80:+3  88:+9
spb 0.468735  BPM 128.004  mean +0.6  span 8.0   0:+1  8:+1  16:+1  24:+1  32:-3  40:-1  48:-1  56:+1  64:-1  72:-1  80:-1  88:+5
spb 0.468745  BPM 128.001  mean -1.4  span 6.0   0:+1  8:+1  16:-1  24:-1  32:-3  40:-3  48:-3  56:-3  64:-3  72:-3  80:-5  88:+1
spb 0.468750  BPM 128.000  mean -1.9  span 6.0   0:+1  8:+1  16:-1  24:-1  32:-5  40:-3  48:-3  56:-1  64:-5  72:-5  80:-5  88:-1
spb 0.468755  BPM 127.999  mean -3.4  span 8.0   0:+1  8:+1  16:-1  24:-3  32:-5  40:-5  48:-5  56:-5  64:-5  72:-7  80:-7  88:-5
spb 0.468725 sub half-rise ms by span (kick beats): 8:+20 16:+20 24:+20 32:+20 40:+20 48:+20 56:+20 72:+20 80:+22
spb 0.468725 pres half-rise ms by span (kick beats): 8:+4 16:+4 24:+4 32:+4 40:+4 48:+4 56:+4 72:+4 80:+8
spb 0.46875 sub half-rise ms by span (kick beats): 8:+18 16:+18 24:+18 32:+16 40:+16 48:+16 56:+14 72:+14 80:+12
spb 0.46875 pres half-rise ms by span (kick beats): 8:+6 16:+2 24:+2 32:+4 40:+0 48:+0 56:-2 72:-2 80:-2
```

```
$ cd "~/deadmau5 app"; KIT="tools/showkit"; W="$KIT/work/veldt"; python3 "$KIT/grid.py" write "deadmau5 - The Veldt" --spb 0.468725 --anchor 0.0425 2>&1 | tail -5; python3 "$KIT/grid.py" check "deadmau5 - The Veldt"; head -3 "shows/scenes/deadmau5 - The Veldt.beats"; python3 "$KIT/spectro.py" "deadmau5 - The Veldt" "$W/a.png" 0 24 ; python3 "$KIT/spectro.py" "deadmau5 - The Veldt" "$W/b.png" 24 48; python3 "$KIT/spectro.py" "deadmau5 - The Veldt" "$W/c.png" 48 72;python3 "$KIT/spectro.py" "deadmau5 - The Veldt" "$W/d.png" 72 91; python3 "$KIT/songmap.py" "deadmau5 - The Veldt" 2>&1 | head -100
    1:52.54-2:00.04  lvl2  eq         {}
    2:00.04-2:22.53  lvl0  wipe       {'period': 3.75, 'a': (255, 40, 0), 'b': (255, 150, 0)}
    2:22.53-2:37.53  lvl1  scanner    {'period': 1.875}
    2:37.53-2:48.78  lvl1  chase      {'period': 1.875}
wrote shows/scenes/deadmau5 - The Veldt.beats: 363 beats, 90 bars, bar 0 at 0.043 s, 128.007 BPM
deadmau5 - The Veldt: 128.007 BPM, 91 bars, bar 0 at 0.043 s, holds []
music against the grid per 8 bars, ms (contrast): 0:-1(8.52)  8:-1(3.19)  16:-1(1.89)  24:-1(2.09)  32:-3(1.68)  40:-1(2.02)  48:-1(2.12)  56:+1(2.08)  64:-1(2.61)  72:-1(2.43)  80:-1(2.21)  88:+5(1.41)
worst 5 ms where the music is clear enough to say, mean -0.1 ms
0.042500
0.511225
0.979950
tools/showkit/songs/veldt/a.png
tools/showkit/songs/veldt/b.png
tools/showkit/songs/veldt/c.png
tools/showkit/songs/veldt/d.png
deadmau5 - The Veldt: 91 bars, 1.87 s a bar, 170.1 s
 bar     t   E  B  M  H  notes       change
   0    0.0   4  5  5  3  A E F       
   1    1.9   3  0  5  3  E A F       
   2    3.8   5  2  6  3  E A C       
   3    5.7   8  8  6  2  E C F       >>
   4    7.5   7  9  6  2  C F E       
   5    9.4   5  3  5  1  E A F       >>
   6   11.3   3  0  5  1  A D E       
   7   13.2   4  5  5  3  A F G       
   8   15.0   5  7  5  8  A C F       >>
   9   16.9   7  7  4  9  C A F       
  10   18.8   8  8  6  6  C A F       
  11   20.7   8  9  2  1  C F A       >>
  12   22.5   8  9  3  4  C A F       
  1
... [cut] ...
 5  7  C A F       
  76  142.5   5  7  6  3  A C F       
  77  144.4   5  6  6  3  C A E       
  78  146.3   6  6  6  5  C A F       
  79  148.2   8  7  5  6  A C F       
  80  150.0   9  9  8  6  C A F       
  81  151.9   8  7  7  4  A E C       
  82  153.8   8  7  8  6  A C E       
  83  155.7   7  7  7  7  A C E       
  84  157.5   7  7  9  6  A C E       
  85  159.4   8  8  8  5  E A C       
  86  161.3   9  9  9  7  A C E       
  87  163.2   9  7  9  8  A E F       
  88  165.0   0  0  1  3  A E A#      >>
  89  166.9   0  0  0  0  A E B       
  90  168.8   0  0  0  0  A E F#
```

```
$ cd "~/deadmau5 app"; KIT="tools/showkit"; W="$KIT/work/veldt"; cat > "$W/notes.py" <<'EOF'
import numpy as np, subprocess
mp3="shows/deadmau5 - The Veldt.mp3"; SR=22050
raw=subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-i",mp3,"-ac","1","-ar",str(SR),"-f","f32le","-"],capture_output=True,check=True).stdout
m=np.frombuffer(raw,dtype=np.float32).copy()
spb=0.468725; t0=0.0425
NOTES="C C# D D# E F F# G G# A A# B".split()
N=8192
win=np.hanning(N)
f=np.fft.rfftfreq(N,1/SR)
def spec(t):
    c=int(t*SR); a=c-N//2
    x=m[max(a,0):a+N]
    if len(x)<N: x=np.pad(x,(N-len(x),0))
    return ... [cut]
per bar, 8 half-beats. low note (50-180 Hz, measured just after each 8th so kick matters less), then upper chroma top-2 400-2000
  0    0.0  E2   D2   D2   D2     G#/E   E/A    E/A    E/D#  
  1    1.9  F#2  A2   A2   A2     E/B    E/B    E/A    E/A   
  2    3.8  B2   A2   A2   D2     F#/D   E/C#   E/C#   E/A   
  3    5.7  D2   D2   D2   D2     E/A    E/A    E/A    E/A   
  4    7.5  E2   B1   B1   B1     E/G#   E/A    E/D#   E/G#  
  5    9.4  F#2  E2   A2   A2     E/B    E/D#   E/G#   E/A   
  6   11.3  B2   A2   A2   D3     F#/D   E/C#   E/C#   F#/A  
  7   13.2  D3   D3   D3   D2     F#/A   A/F#   F#/A   F#/A  
  8   15.0  E3   D3   D3   D2     G#/E   G#/E   E/A    E/A   
  9   16.9  F#1  A1   A1   A2     E/B    E/B    E/B    E/A   
 10   18.8  B1   A2   A2   D2     D/F#   E/G    E/C#   E/A   
 11   20.7  D2   D2   D2   D2     E/A    E/A    E/A    E/A   
 12   22.5  E2   B1   B1   B1     E/G#   E/G#   E/A    E/A   
 13   24.4  F#1  E2   A1   A1     E/B    E/G#   E/C#   E/A   
 14   26.3  B1   A1   A2   D2     F#/D   B/E    E/C#   F#/E  
 15   28.2  D2   D2   D2   D2     E/F#   A/E    E/F#   F#/A  
 16   30.0  E2   D2   D2   D2     E/G#   E/B    F#/E   E/A   
 17   31.9  F#2  A2   A2   A2     B/E    B/E    A/E    E/B   
 18   33.8  B2   A2   A2   D2     F#/D   B/E    A/E    A/E   
 19   35.7  D2   D2   D2   D2     A/E    E/A    E/F#   E/A   
 20   37.5  E3   B2   B1   B1     E/G#   E/G#   E/A    E/G#  
 21   39.4  F#1  E2   A1   A1     F#/B   E/G#   E/B    E/A   
 22   41.3  B1   A1   A1   D2     F#/D   B/C    A/E    A/F#  
 23   43.2  D2   D2   D2   D2     B/E    A/F#   E/F#   B/F#  
 24   45.0  E2   D2   D2   D2     G#/B   A/E    A/E    E/B   
 25   46.9  F#1  A1   A1   A1     E/B    E/F#   E/B    E/A   
 26   48.8  B1   A1   A2   D2     F#/E   E/G#   A/E    E/A 
... [cut] ...
 A1   A1   D2     F#/A   E/B    E/A    A/E   
 79  148.2  D2   D2   D2   D2     F#/B   A/E    E/A    B/A   
 80  150.0  E2   D2   D2   D2     E/G#   A/E    E/F#   B/E   
 81  151.9  F#2  A2   A1   A1     E/F#   E/F#   E/B    E/A   
 82  153.8  B1   A1   A1   D2     F#/D   E/B    E/A    E/A   
 83  155.7  D2   D2   D3   D3     E/B    E/A    E/A    E/B   
 84  157.5  E3   D3   D3   B2     E/B    A/E    E/F#   E/D#  
 85  159.4  F#2  E2   A2   A2     E/A    E/D#   E/B    E/A   
 86  161.3  B2   A2   A2   D2     F#/E   E/C#   E/A    E/F#  
 87  163.2  D2   D2   D2   D2     B/E    E/A    E/A    A/E
```

```
$ cd "~/deadmau5 app"; KIT="tools/showkit"; W="$KIT/work/veldt"; cat > "$W/vox.py" <<'EOF'
import numpy as np, subprocess, sys
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
mp3="shows/deadmau5 - The Veldt.mp3"; SR=22050
raw=subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-i",mp3,"-ac","2","-ar",str(SR),"-f","f32le","-"],capture_output=True,check=True).stdout
x=np.frombuffer(raw,dtype=np.float32).reshape(-1,2).copy()
mid=(x[:,0]+x[:,1])/2; side=(x[:,0]-x[:,1])/2
spb=0.468725; t0=0.0425; bar=4*spb
N=4096;H=512;win=np.hanning(N)
def stft(y,a,b):
    a=int(a*SR ... [cut]
tools/showkit/songs/veldt/v1.png
tools/showkit/songs/veldt/v2.png
tools/showkit/songs/veldt/v3.png
tools/showkit/songs/veldt/v4.png
```

```
$ cd "~/deadmau5 app"; KIT="tools/showkit"; W="$KIT/work/veldt"; cat > "$W/layers.py" <<'EOF'
import numpy as np, subprocess, sys
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
mp3="shows/deadmau5 - The Veldt.mp3"; SR=22050
raw=subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-i",mp3,"-ac","2","-ar",str(SR),"-f","f32le","-"],capture_output=True,check=True).stdout
x=np.frombuffer(raw,dtype=np.float32).reshape(-1,2).copy()
mid=(x[:,0]+x[:,1])/2; side=(x[:,0]-x[:,1])/2
spb=0.468725; t0=0.0425
N=2048;H=256;win=np.hanning(N)
f=np.fft.rfftfreq(N,1/SR)
edges=np.geom ... [cut]
tools/showkit/songs/veldt/layers.png
```

```
$ cd "~/deadmau5 app"; KIT="tools/showkit"; W="$KIT/work/veldt"; cat > "$W/perbeat.py" <<'EOF'
import numpy as np, subprocess
from numpy.fft import rfft, irfft, rfftfreq
mp3="shows/deadmau5 - The Veldt.mp3"; SR=22050
raw=subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-i",mp3,"-ac","2","-ar",str(SR),"-f","f32le","-"],capture_output=True,check=True).stdout
x=np.frombuffer(raw,dtype=np.float32).reshape(-1,2).copy()
m=x.mean(1); sd=(x[:,0]-x[:,1])/2
f=rfftfreq(len(m),1/SR); X=rfft(m); Xs=rfft(sd)
def band(X,a,b):
    Y=X.copy(); Y[(f<a)|(f>=b)]=0; return irfft(Y,len(m))
sub=band(X,30,10 ... [cut]
Exit code 1
~/Library/Python/3.9/lib/python/site-packages/numpy/_core/fromnumeric.py:3596: RuntimeWarning: Mean of empty slice.
  return _methods._mean(a, axis=axis, dtype=dtype,
~/Library/Python/3.9/lib/python/site-packages/numpy/_core/_methods.py:138: RuntimeWarning: invalid value encountered in divide
  ret = ret.dtype.type(ret / rcount)
bar: kick(sub first 100ms) per beat | hats offbeat (air, 8th) per beat | clap (air 0-60ms on 2,4) | mid per beat | E5 side
  0    0.0  k4444  h4444  c3333  m3323  l3544  s4445
  1    1.9  k3200  h4444  c3333  m3332  l4453  s5445
  2    3.8  k0005  h4433  c3333  m4333  l4343  s5445
  3    5.7  k5555  h3333  c3222  m3333  l4333  s6776
  4    7.5  k5555  h3233  c2222  m3323  l3443  s6666
  5    9.4  k5550  h3333  c2222  m2322  l4444  s5555
  6   11.3  k0001  h3332  c2222  m4332  l4454  s5554
  7   13.2  k2233  h2233  c2222  m2233  l5435  s4343
  8   15.0  k7777  h7665  c4554  m2322  l4344  s3333
  9   16.9  k7777  h7795  c4554  m2223  l4443  s3333
 10   18.8  k7777  h7644  c5544  m4422  l3334  s7643
 11   20.7  k7777  h2222  c4444  m2111  l3433  s2232
 12   22.5  k7777  h5656  c4454  m2222  l4344  s2232
 13   24.4  k7777  h5522  c4544  m3222  l3434  s2333
 14   26.3  k7777  h7656  c6555  m2432  l4334  s3443
 15   28.2  k7777  h4444  c4444  m1112  l3333  s2222
 16   30.0  k7777  h4775  c4556  m2243  l4334  s2364
 17   31.9  k7777  h6432  c5646  m3321  l3434  s3323
 18   33.8  k7776  h7647  c5546  m3422  l4444  s5643
 19   35.7  k7777  h3222  c5646  m2122  l3333  s2332
 20   37.5  k7777  h5454  c4546  m2322  l4344  s3333
 21   39.4  k7777  h6665  c4646  m3323  l3334  s3435
 22   41.3  k7677  h5563  c4656  m3332  l4434  s5644
 23   43.2  k7677  h2216  c4546  m2232  l3343  s2222
 24   45.0  k7677  h5533  c4546  m3333  
... [cut] ...
65.0  k1000  h4321  c3221  m2100  l0000  s5420
 89  166.9  k0000  h0000  c0000  m0000  l0000  s0000
Traceback (most recent call last):
  File "tools/showkit/songs/veldt/perbeat.py", line 23, in <module>
    k.append(lev(rms(sub,T,T+0.1),-2,0.2))
  File "tools/showkit/songs/veldt/perbeat.py", line 17, in lev
    return min(9,max(0,int((np.log10(max(v,1e-5))-lo)/(hi-lo)*9.99)))
ValueError: cannot convert float NaN to integer
```

```
$ cd "~/deadmau5 app"; wc -l mau5scene.py mau5fx.py mau5engine.py mau5show.py mau5preview.py; sed -n 1,140p mau5scene.py
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
d": 0.0},
}

MAX_SCENE_LAYERS, MAX_HIT_LAYERS, MAX_HITS_AT_ONCE = 6, 3, 2


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
```

```
$ cd "~/deadmau5 app"; sed -n 140,620p mau5scene.py
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
        raise TreatmentError("the analysis has too few beats for a scene grid")
    late = np.diff(beats) - np.median(np.diff(beats))
    late[late <= LINEAR_TOL_S] = 0.0
    held = np.concatenate(([0.0], np.cumsum(late)))
    spb = float((beats[-1] - beats[0] - held[-1]) / (len(beats) - 1))
    t0 = float(bars[0])
    first = int(np.abs(beats - t0).argmin())
    off = np.abs(beats - held - (beats[0] + spb * np.arange(len(beats)))).max()
    barheld = held[first::4][:len(bars)] - held[first]
    boff = np.abs(bars - barheld - (t0 + 4.0 * spb * np.arange(len(bars)))).max()
    onbeat
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
$ cd "~/deadmau5 app"; sed -n 620,1344p mau5scene.py
<persisted-output>
Output too large (29.5KB). Full output saved to: ~/.claude/projects/-Users-jones-deadmau5-app/208332e7-8c9f-4c25-bc21-e9a9df98fa1f/tool-results/bbzorc35t.txt

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
$ cd "~/deadmau5 app"; sed -n 140,620p mau5scene.py
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
        raise TreatmentError("the analysis has too few beats for a scene grid")
    late = np.diff(beats) - np.median(np.diff(beats))
    late[late <= LINEAR_TOL_S] = 0.0
    held = np.concatenate(([0.0], np.cumsum(late)))
    spb = float((beats[-1] - beats[0] - held[-1]) / (len(beats) - 1))
    t0 = float(bars[0])
    first = int(np.abs(beats - t0).argmin())
    off = np.abs(beats - held - (beats[0] + spb * np.arange(len(beats)))).max()
    barheld = held[first::4][:len(bars)] - held[first]
    boff = np.abs(bars - barheld - (t0 + 4.0 * spb * np.arange(len(bars)))).max()
    onbeat
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
$ cd "~/deadmau5 app"; sed -n 620,1344p mau5scene.py
<persisted-output>
Output too large (29.5KB). Full output saved to: ~/.claude/projects/-Users-jones-deadmau5-app/208332e7-8c9f-4c25-bc21-e9a9df98fa1f/tool-results/bbzorc35t.txt

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
$ cd "~/deadmau5 app"; grep -n "class Sprite\|SPRITES\|def _load_sprites\|sprites.json\|class Eyes\|class TextScroll\|_text_bitmap" mau5fx.py mau5engine.py mau5show.py mau5scene.py | head -40; python3 - <<'EOF'
import sys
sys.path.insert(0,'.')
import numpy as np, mau5engine as E
h=E.Helmet()
print(h.n, h.shell.sum(), h.ears.sum())
print("shell px",h.px[h.shell].min(),h.px[h.shell].max(),"py",h.py[h.shell].min(),h.py[h.shell].max())
print("ear1 px",h.px[h.ear1].min(),h.px[h.ear1].max(),"py",h.py[h.ear1].min(),h.py[h.ear1].max())
print("ear2 px",h.px[h.ear2].min(),h.px[h.ear2].max(),"py",h.py[h.ear2].min(),h.py[h.ear2].max())
# a 17x17 map of which cells hold LEDs, with y_lo -108, y_ ... [cut]
mau5fx.py:134:SPRITES = {
mau5fx.py:249:# Sprites a song brings with it: shows/scenes/<song>.sprites.json, {name: [rows]},
mau5fx.py:256:        sheets = sorted(f for f in os.listdir(d) if f.endswith(".sprites.json"))
mau5fx.py:266:                SPRITES[name] = list(rows)
mau5fx.py:275:    rows = SPRITES[name_or_rows] if isinstance(name_or_rows, str) else name_or_rows
mau5fx.py:567:class Sprite(GridEffect):
mau5fx.py:584:class SpriteFlipbook(GridEffect):
mau5fx.py:989:    for name in sorted(SPRITES):
mau5engine.py:35:from mau5fx import FONT5x7, SPRITES
mau5engine.py:580:def _text_bitmap(text, spacing=1):
mau5engine.py:625:    rows = SPRITES[name]
mau5engine.py:674:class TextScroll(Preset):
mau5engine.py:687:        bm = _text_bitmap(self.p["text"], spacing=1)
mau5engine.py:704:class SpriteShow(Preset):
mau5engine.py:743:class Eyes(Preset):
mau5scene.py:419:            w = int(E._text_bitmap(text).shape[1])
mau5scene.py:640:    from mau5fx import SPRITES
mau5scene.py:726:                    if one not in SPRITES:
621 398 223
shell px -170.94 170.95 py -111.27 167.77
ear1 px -388.21 -55.76 py 51.8 383.94
ear2 px 55.56 387.42 py 54.72 384.91
 0  y=  158    .  .  .  .  2  4  1  3  3  2  2  3  1  .  .  .  .
 1  y=  142    .  .  .  5  8  3  5  3  3  4  4  4  7  5  .  .  .
 2  y=  126    .  .  3  4  1  2  2  2  2  2  2  2  1  4  3  .  .
 3  y=  110    .  3 10  4  3  4  3  3  4  3  3  4  3  4 10  3  .
 4  y=   93    .  5  3  2  2  1  2  1  2  1  2  1  2  2  3  5  .
 5  y=   77    3  3  2  2  2  1  2  1  2  1  2  1  2  2  2  3  3
 6  y=   61    4  3  2  2  1  2  1  1  2  1  1  2  1  2  2  3  4
 7  y=   45    5  2  2  2  .  .  .  .  .  .  .  .  .  2  2  2  5
 8  y=   29    5  1  .  .  .  .  .  .  .  .  .  .  .  .  .  1  5
 9  y=   13    1  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  1
10  y=   -3    .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .
11  y=  -19    1  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  1
12  y=  -35    3  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  3
13  y=  -52    4  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  4
14  y=  -68    3  3  .  .  .  .  .  .  .  .  .  .  .  .  .  3  3
15  y=  -84    1  5  2  .  .  .  .  .  .  .  .  .  .  .  2  5  1
16  y= -100    .  4  3  3  .  .  .  .  .  .  .  .  .  3  3  4  .
```

```
$ cd "~/deadmau5 app"; grep -n "class Sprite\|SPRITES\|def _load_sprites\|sprites.json\|class Eyes\|class TextScroll\|_text_bitmap" mau5fx.py mau5engine.py mau5show.py mau5scene.py | head -40; python3 - <<'EOF'
import sys
sys.path.insert(0,'.')
import numpy as np, mau5engine as E
h=E.Helmet()
print(h.n, h.shell.sum(), h.ears.sum())
print("shell px",h.px[h.shell].min(),h.px[h.shell].max(),"py",h.py[h.shell].min(),h.py[h.shell].max())
print("ear1 px",h.px[h.ear1].min(),h.px[h.ear1].max(),"py",h.py[h.ear1].min(),h.py[h.ear1].max())
print("ear2 px",h.px[h.ear2].min(),h.px[h.ear2].max(),"py",h.py[h.ear2].min(),h.py[h.ear2].max())
# a 17x17 map of which cells hold LEDs, with y_lo -108, y_ ... [cut]
mau5fx.py:134:SPRITES = {
mau5fx.py:249:# Sprites a song brings with it: shows/scenes/<song>.sprites.json, {name: [rows]},
mau5fx.py:256:        sheets = sorted(f for f in os.listdir(d) if f.endswith(".sprites.json"))
mau5fx.py:266:                SPRITES[name] = list(rows)
mau5fx.py:275:    rows = SPRITES[name_or_rows] if isinstance(name_or_rows, str) else name_or_rows
mau5fx.py:567:class Sprite(GridEffect):
mau5fx.py:584:class SpriteFlipbook(GridEffect):
mau5fx.py:989:    for name in sorted(SPRITES):
mau5engine.py:35:from mau5fx import FONT5x7, SPRITES
mau5engine.py:580:def _text_bitmap(text, spacing=1):
mau5engine.py:625:    rows = SPRITES[name]
mau5engine.py:674:class TextScroll(Preset):
mau5engine.py:687:        bm = _text_bitmap(self.p["text"], spacing=1)
mau5engine.py:704:class SpriteShow(Preset):
mau5engine.py:743:class Eyes(Preset):
mau5scene.py:419:            w = int(E._text_bitmap(text).shape[1])
mau5scene.py:640:    from mau5fx import SPRITES
mau5scene.py:726:                    if one not in SPRITES:
621 398 223
shell px -170.94 170.95 py -111.27 167.77
ear1 px -388.21 -55.76 py 51.8 383.94
ear2 px 55.56 387.42 py 54.72 384.91
 0  y=  158    .  .  .  .  2  4  1  3  3  2  2  3  1  .  .  .  .
 1  y=  142    .  .  .  5  8  3  5  3  3  4  4  4  7  5  .  .  .
 2  y=  126    .  .  3  4  1  2  2  2  2  2  2  2  1  4  3  .  .
 3  y=  110    .  3 10  4  3  4  3  3  4  3  3  4  3  4 10  3  .
 4  y=   93    .  5  3  2  2  1  2  1  2  1  2  1  2  2  3  5  .
 5  y=   77    3  3  2  2  2  1  2  1  2  1  2  1  2  2  2  3  3
 6  y=   61    4  3  2  2  1  2  1  1  2  1  1  2  1  2  2  3  4
 7  y=   45    5  2  2  2  .  .  .  .  .  .  .  .  .  2  2  2  5
 8  y=   29    5  1  .  .  .  .  .  .  .  .  .  .  .  .  .  1  5
 9  y=   13    1  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  1
10  y=   -3    .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .
11  y=  -19    1  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  1
12  y=  -35    3  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  3
13  y=  -52    4  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  4
14  y=  -68    3  3  .  .  .  .  .  .  .  .  .  .  .  .  .  3  3
15  y=  -84    1  5  2  .  .  .  .  .  .  .  .  .  .  .  2  5  1
16  y= -100    .  4  3  3  .  .  .  .  .  .  .  .  .  3  3  4  .
```

```
$ cd "~/deadmau5 app"; sed -n 575,800p mau5engine.py; sed -n 245,285p mau5fx.py; cat mau5preview.py | sed -n 1,120p
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
eld sc.frame(preset.render(h, t, music), gain)


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
```

```
$ cd "~/deadmau5 app"; python3 - <<'EOF'
import json
for s in ["deadmau5 - Strobe","beneath (with raxaj)"]:
    d=json.load(open('shows/scenes/%s.scene.json'%s))
    print(s, d['about'][:900]); print()
EOF
python3 - <<'EOF'
import sys
sys.path.insert(0,'.')
import numpy as np, mau5engine as E
h=E.Helmet()
print("attrs",[k for k in dir(h) if not k.startswith('_')])
print("nfa range shell",h.nfa[h.shell].min(),h.nfa[h.shell].max(),"nel range shell",h.nel[h.shell].min(),h.nel[h.shell].max())
print("nx/ny",h.nx[h.shell].min(),h.nx[h.shell].max(),h.ny[h.shell].min(),h.ny[h.shell].max())
print("all px",h.px.min(),h.px.max(),"py",h.py.min(),h.py.max())
for nm in ("rims","tubes"):
    m=np. ... [cut]
deadmau5 - Strobe Bars of the analysis grid: bar b starts at 1.756 + 1.875 b seconds, 339 bars. One constellation of sixteen sparks is the arpeggio, and it comes back every time the arpeggio does. Ice is the climb, dawn the breakdowns, strobe the drops, pure the ear hits. White once, on the drop at 217.

beneath (with raxaj) Bars of the measured grid in the .beats beside this file: bar b starts at 1.275 + 1.905 b seconds (126.0 BPM), 144 bars, and from bar 133.25 the outro slows to 122.0 BPM. The light lives beneath: a pool of magma in the jaw that throbs on every kick, while the ears surge up from their base on the off-beat bass, the way the sidechain pumps. The pool rises through each build until the whole face is molten, drains in the breakdown and is gone in the four silent bars, and wells back up with the sub at bar 67. The grooves are a tide: the left half and ear 1 fill while the right half and ear 2 drain, then they answer. Both builds send a seam of light up the face from the chin, faster each phrase. The song goes silent for three and a half beats at bar 48 and drops on 49; the riser drains everything back down before drop 2 lands on 123. Warm only: ember, magma, obsidian for the cooled breakdown, 

attrs ['along', 'az', 'depth', 'ea', 'ear1', 'ear2', 'ears', 'el', 'er', 'fa', 'group', 'mask', 'n', 'nel', 'nfa', 'nx', 'ny', 'px', 'py', 'region', 'rims', 'rows', 'shell', 'tube', 'tubes', 'u', 'xyz']
nfa range shell 0.16035751702193546 0.8399804407362015 nel range shell 0.0 1.0
nx/ny 0.280120676095561 0.7209107435246187 0.0 0.5623765568946754
all px -388.21 387.42 py -111.27 384.91
rims 37 px -388.21 387.42 py 51.8 384.91
tubes 186 px -349.0 357.75 py 66.93 349.09
tube 0 58 along 0.0247 0.9173 px -349.0 357.75 py 66.93 215.77
tube 1 72 along 0.1467 0.9699 px -309.87 322.01 py 126.76 305.82
tube 2 56 along 0.0885 0.954 px -237.37 236.92 py 205.47 349.09
```

```
$ cd "~/deadmau5 app"; sed -n 575,800p mau5engine.py; sed -n 245,285p mau5fx.py; cat mau5preview.py | sed -n 1,120p
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
eld sc.frame(preset.render(h, t, music), gain)


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
```

```
$ cd "~/deadmau5 app"; python3 - <<'EOF'
import json
for s in ["deadmau5 - Strobe","beneath (with raxaj)"]:
    d=json.load(open('shows/scenes/%s.scene.json'%s))
    print(s, d['about'][:900]); print()
EOF
python3 - <<'EOF'
import sys
sys.path.insert(0,'.')
import numpy as np, mau5engine as E
h=E.Helmet()
print("attrs",[k for k in dir(h) if not k.startswith('_')])
print("nfa range shell",h.nfa[h.shell].min(),h.nfa[h.shell].max(),"nel range shell",h.nel[h.shell].min(),h.nel[h.shell].max())
print("nx/ny",h.nx[h.shell].min(),h.nx[h.shell].max(),h.ny[h.shell].min(),h.ny[h.shell].max())
print("all px",h.px.min(),h.px.max(),"py",h.py.min(),h.py.max())
for nm in ("rims","tubes"):
    m=np. ... [cut]
deadmau5 - Strobe Bars of the analysis grid: bar b starts at 1.756 + 1.875 b seconds, 339 bars. One constellation of sixteen sparks is the arpeggio, and it comes back every time the arpeggio does. Ice is the climb, dawn the breakdowns, strobe the drops, pure the ear hits. White once, on the drop at 217.

beneath (with raxaj) Bars of the measured grid in the .beats beside this file: bar b starts at 1.275 + 1.905 b seconds (126.0 BPM), 144 bars, and from bar 133.25 the outro slows to 122.0 BPM. The light lives beneath: a pool of magma in the jaw that throbs on every kick, while the ears surge up from their base on the off-beat bass, the way the sidechain pumps. The pool rises through each build until the whole face is molten, drains in the breakdown and is gone in the four silent bars, and wells back up with the sub at bar 67. The grooves are a tide: the left half and ear 1 fill while the right half and ear 2 drain, then they answer. Both builds send a seam of light up the face from the chin, faster each phrase. The song goes silent for three and a half beats at bar 48 and drops on 49; the riser drains everything back down before drop 2 lands on 123. Warm only: ember, magma, obsidian for the cooled breakdown, 

attrs ['along', 'az', 'depth', 'ea', 'ear1', 'ear2', 'ears', 'el', 'er', 'fa', 'group', 'mask', 'n', 'nel', 'nfa', 'nx', 'ny', 'px', 'py', 'region', 'rims', 'rows', 'shell', 'tube', 'tubes', 'u', 'xyz']
nfa range shell 0.16035751702193546 0.8399804407362015 nel range shell 0.0 1.0
nx/ny 0.280120676095561 0.7209107435246187 0.0 0.5623765568946754
all px -388.21 387.42 py -111.27 384.91
rims 37 px -388.21 387.42 py 51.8 384.91
tubes 186 px -349.0 357.75 py 66.93 349.09
tube 0 58 along 0.0247 0.9173 px -349.0 357.75 py 66.93 215.77
tube 1 72 along 0.1467 0.9699 px -309.87 322.01 py 126.76 305.82
tube 2 56 along 0.0885 0.954 px -237.37 236.92 py 205.47 349.09
```

```
$ cd "~/deadmau5 app"; KIT="tools/showkit"; W="$KIT/work/veldt"; cat > "$W/ledmap.py" <<'EOF'
import sys,os
sys.path.insert(0,os.getcwd())
import numpy as np, mau5engine as E, mau5preview as PV
from PIL import Image, ImageDraw
h=E.Helmet(); sc=PV.Scene(h)
# parts in colours
f=np.zeros((h.n,3))
f[h.shell]=(60,60,60)
f[np.asarray(h.tube)==0]=(255,40,0)
f[np.asarray(h.tube)==1]=(40,255,0)
f[np.asarray(h.tube)==2]=(0,80,255)
f[np.asarray(h.rims,bool)]=(255,255,0)
a=sc.frame(f)
# along-axis gradient on tubes, y on shell
g=np.zeros((h.n,3))
al=np.maximum(h.along,0)
g[h.tubes]=np.outer(al[h.tubes],(255, ... [cut]
(760, 620)
shell nel by py: [(-111, 0.0), (-84, 0.1), (29, 0.43), (61, 0.52), (91, 0.62), (105, 0.67), (129, 0.76), (140, 0.81)]
tube along vs py ear2 tube0 [(0.05, 211, 70), (0.45, 280, 137), (0.84, 345, 203), (0.66, 314, 171), (0.25, 235, 116)]
tube along vs py ear2 tube1 [(0.15, 133, 127), (0.43, 198, 186), (0.74, 270, 256), (0.97, 322, 306), (0.68, 256, 241), (0.37, 187, 173)]
tube along vs py ear2 tube2 [(0.09, 92, 205), (0.47, 155, 268), (0.89, 227, 339), (0.68, 184, 311), (0.28, 112, 248)]
rim ear2 [(181, 59), (313, 74), (387, 191), (349, 318), (218, 385), (75, 306), (62, 180)]
```

```
$ cd "~/deadmau5 app"; date; KIT="tools/showkit"; W="$KIT/work/veldt"; python3 "$KIT/sheet.py" "TIKI TIKI - Slowed" "$W/tiki.png" 4:light 6:hook 12:hookb 28:lagoon 33:verse 40:idol 40.25 76:sunset 108:duel 155:final 170:wind 179:out 2>&1 | tail -14; python3 - <<'EOF'
import sys
sys.path.insert(0,'.')
from mau5fx import SPRITES
for k in ("tiki",):
    print("\n".join(SPRITES[k]))
import mau5power
g=mau5power.load(count=621)
print({k:getattr(g,k) for k in dir(g) if k in ("budget_ma","ceiling","ma_per_channel","shell_ceiling","ear_ceiling")})
EOF
grep -n "ceiling\|budget\|burst_j\|sustained" mau5pow ... [cut]
Sat Oct 31 12:46:48 PDT 2026
bar 4       light          shell max  59 mean   3.8   ears max  27 mean   0.1   lighting
bar 6       hook           shell max  56 mean  11.6   ears max 153 mean  32.1   hook
bar 12      hookb          shell max  61 mean  21.5   ears max 153 mean  32.1   hookb
bar 28      lagoon         shell max 221 mean  39.9   ears max  50 mean  11.4   still · TIKI TIKI
bar 33      verse          shell max  65 mean   8.4   ears max  52 mean  17.0   verse
bar 40      idol           shell max  61 mean  21.5   ears max 153 mean  32.1   big
bar 40.25                  shell max  56 mean  14.9   ears max 100 mean  24.0   big
bar 76      sunset         shell max  61 mean  24.3   ears max 153 mean  32.8   sunset
bar 108     duel           shell max  56 mean   9.4   ears max 230 mean  34.3   duel
bar 155     final          shell max  61 mean  27.9   ears max 255 mean  40.3   final
bar 170     wind           shell max  41 mean  13.3   ears max  92 mean  24.2   wind
bar 179     out            shell max  17 mean   3.6   ears max  47 mean   1.6   out
tools/showkit/songs/veldt/tiki.png (1800, 490)
.XXXXXXXXXXXXXXX.
.................
.XXXXXXX.XXXXXXX.
.XXXXXXX.XXXXXXX.
.XX...XX.XX...XX.
.XX...XX.XX...XX.
.XXXXXXX.XXXXXXX.
.................
X...............X
X...............X
.................
.................
X...............X
X...............X
.XX.XX.....XX.XX.
..X.XX.XXX.XX.X..
...X..X...X..X...
{'budget_ma': 1000.0}
15:brightness number cannot express that; a ceiling per region can.
24:  ceiling   a per-LED cap by region, so the shell can never be driven
27:  governor  if the whole frame still estimates over budget, scale it
51:# is never slowed: that is what keeps every frame insi
... [cut] ...
        self.budget_ma = float(budget_ma)
183:        # can carry, continuously, in total.  The budget above is about
185:        # real ceiling if the current has to cross a contact that
191:        self.default_ceiling = int(default_ceiling)
192:        self._ceil = np.full(self.count, float(default_ceiling), np.float32)
198:                self._ceil[lo:hi + 1] = r.ceiling
200:                self._floor[lo:hi + 1] = min(r.floor, r.ceiling)
201:        # The ceiling is a soft knee (see apply).  It starts to bend at
202:        # _klo and has _kw left above that before the ceiling.  The bend
```

```
$ cd "~/deadmau5 app"; sed -n 200,330p mau5power.py; grep -n "def load" -A40 mau5power.py | head -90; ls *.json | head; python3 - <<'EOF'
import json,os
for fn in ("power.json","mau5power.json"):
    if os.path.exists(fn): print(fn,json.load(open(fn)))
EOF
                self._floor[lo:hi + 1] = min(r.floor, r.ceiling)
        # The ceiling is a soft knee (see apply).  It starts to bend at
        # _klo and has _kw left above that before the ceiling.  The bend
        # is placed so that full drive, 255, is four widths past it:
        # e**-4 short of the ceiling, under 2%, so the top end the
        # ceilings were tuned for is where it was.  On a ceiling of 255
        # it never bends -- a tube is not dimmed by a ceiling it cannot
        # reach -- and on a rim at 160 only the top 20% does.
        c = self._ceil.astype(np.float64)
        self._klo = np.minimum(np.maximum((4.0 * c - 255.0) / 3.0, 0.0), c)
        self._kw = c - self._klo
        self._gov_s = 1.0          # the governor's scale on the last frame
        self._gov_t = None         # and when that was

    # -- estimates ------------------------------------------------------
    def _per_led_ma(self, out):
        return out.sum(1) / (3.0 * 255.0) * MA_PER_LED_FULL_WHITE

    def frame_ma(self, buf):
        """Estimated LED current for a frame, standby excluded."""
        return float(np.asarray(buf, np.float32).sum()
                     / (3 * 255.0) * MA_PER_LED_FULL_WHITE)

    def standby_ma(self):
        return self.count * MA_PER_LED_STANDBY

    # -- the clamp ------------------------------------------------------
    def link_limit_ma(self):
        """LED current the weakest connector leaves room for, or None.

        Standby crosses the same joint, so it comes off the top.
        """
        if not self.link_ma:
            return None
        return max(0.0, self.link_ma - self.standby_ma())

    def apply(self, buf, now=None, gain=1.0):
        """Return (clamped frame, report).  Never raises on a bad frame.

        `now` override
... [cut] ...
th.dirname(path), exist_ok=True)
492-    th = guard.thermal
493-    # Every field load() reads, or a round trip quietly drops it: this
494-    # used to lose each region's floor and the connector limit.
495-    json.dump({"count": guard.count, "budget_ma": guard.budget_ma,
496-               "default_ceiling": guard.default_ceiling,
497-               "thermal": ({"sustained_w": th.sustained_w, "burst_j": th.burst_j,
498-                            "max_w": th.max_w, "standby_w": th.standby_w,
499-                            "ramp": th.ramp} if th else None),
(eval):1: no matches found: *.json
```

```
$ cd "~/deadmau5 app"; python3 - <<'EOF'
import sys
sys.path.insert(0,'.')
import mau5power, numpy as np
g=mau5power.load(count=621)
print(g.budget_ma, g.link_ma, g.default_ceiling)
for r in g.regions: print(r)
print(vars(g.thermal))
print(mau5power.MA_PER_LED_FULL_WHITE, mau5power.MA_PER_LED_STANDBY)
EOF
grep -n "def frame" -A45 mau5show.py | sed -n 1,90p
1000.0 0.0 32
Region(shell 0..397 ceiling=64 budget=300mA shed=6.0)
Region(ear1_tubes 398..491 ceiling=255 budget=620mA shed=1.0)
Region(ear1_rim 492..509 ceiling=160 budget=200mA shed=3.0)
Region(ear2_rim 510..528 ceiling=160 budget=190mA shed=3.0)
Region(ear2_tubes 529..620 ceiling=255 budget=640mA shed=1.0)
{'sustained_w': 11.0, 'burst_j': 3000.0, 'max_w': 25.5, 'standby_w': 7.452, 'ramp': 0.3, 'level': 0.0, '_last': None}
19.0 1.0
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
795-            ph = self.music.beat_phase(t)
796-            if self.dyn > 0:
797-                # bass and overall together: a breakdown with a loud pad
798-                # should not read as loud as a drop with a kick under it
799-                e = (0.6 
... [cut] ...
            # what the power guard exists to take away again -- the
807-            # per-LED ceilings and the governor flatten anything loud --
808-            # and the shows measured 1.00-1.06 on-beat over half a beat
809-            # later.  So the frame is left as written and the pulse is
810-            # handed over as `gain`, at most 1, for whoever sends the
811-            # frame to apply after the guard: the beat is the frame at
812-            # its limit and the gaps between are dimmer.
813-            #
814-            # Its shape is beat_gain's: held long enough that the phone,
```

```
$ cd "~/deadmau5 app"; grep -n "guard\|\.gain" mau5show.py | head -40; sed -n 960,1000p mau5show.py | head -5; cat "tools/showkit/sheet.py" | sed -n 1,8p; grep -n "sendFrame\|guard" remote/offline/show.js | head -10
606:    """The beat pulse at beat phase `ph`: at most 1, applied after the guard.
613:    same peak, which is the guarded frame itself; only the gaps between
673:        self.gain = 1.0                 # the beat pulse; see frame()
684:        # It also costs nothing.  The guard clamps the top anyway, so
772:                out, self.gain, self.label = self.scenes.frame(t, self.music)
778:        self.gain = 1.0
806:            # what the power guard exists to take away again -- the
811:            # frame to apply after the guard: the beat is the frame at
816:            self.gain = 1.0
819:                self.gain = beat_gain(ph, bpm, self.pulse * (0.4 + 0.3 * lvl))
868:        sc.frame(f * pl.gain).save(os.path.join(tmp, "f%05d.png" % i))
912:    if pix.guard is None:
935:            pix.send(f, gain=pl.gain)
    b = sub.add_parser("build"); b.add_argument("track", nargs="+")
    b.add_argument("--fps", type=int, default=40)
    p = sub.add_parser("preview"); p.add_argument("show")
    p.add_argument("--seconds", type=float); p.add_argument("--fps", type=int, default=24)
    p.add_argument("--out"); p.add_argument("--no-audio", action="store_true")
#!/usr/bin/env python3
"""sheet.py "<base>" out.png bar[:label] bar[:label] ... -- the show at those bars as the helmet
will really look, through the power guard: a contact sheet, front view. Also prints, per tile, how
bright the shell and ears really are after the guard. Bars may be fractional: 40.25 is the second
beat of bar 40, so catch both a kick and the gap after it. Run from the repo root."""
import json, os, sys
sys.path.insert(0, os.getcwd())
import numpy as np, mau5show, mau5preview as PV
101:    this.gain = 1.0;          // the beat pulse, for the sender to apply after the guard
240:      // Not multiplied in: the guard flattens a lift on anything loud.
242:      // the guard (mau5show.Player.frame has the whole story).
754:    // After the guard, like the cue lists' beat pulse: on the pattern the
756:    // a frame the guard has already flattened.
```

```
$ cd "~/deadmau5 app"; KIT="tools/showkit"; W="$KIT/work/veldt"; sed -n 330,440p mau5power.py; cat > "$W/gsheet.py" <<'EOF'
#!/usr/bin/env python3
"""gsheet.py "<base>" out.png bar[:label] ... -- like sheet.py but the frames really go through the power guard:
the whole song is run through a fresh guard at 25 fps, so the thermal state is right, and each tile is what leaves the guard.
Prints per tile: shell and ear levels and mA. Optional: --scale N to multiply the display for reading dim tiles (default 1)."""
import json, os, sys
sys.path.insert(0, os.getcwd())
import numpy as np, mau5show, mau5pr ... [cut]
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
        cap = 1.0
        if self._gov_s < 1.0:
            dt = (now - self._gov_t
                  if self._gov_t is not None and math.isfinite(now) else 0.0)
            cap = min(1.0, max(self._gov_s, GOV_FROM)
                      * math.exp(GOV_RISE * min(max(dt, GOV_MIN_DT
... [cut] ...
%.1f W is standby), "
                     "bursts to %.1f W on %.0f J of thermal mass"
                     % (t.sustained_w, t.standby_w, t.max_w or 0, t.burst_j))
            L.append("           full brightness for about %.0f s before it eases off"
                     % (t.burst_j / max((t.max_w or 0) - t.sustained_w, 0.1)))
        L.append("  the global governor holds that to %.0f mA -> %.2f A "
                 "with standby, %.1f W"
                 % (held, (held + self.standby_ma()) / 1000.0,
                    (held + self.standby_ma()) * 12 / 1000.0))
Sat Oct 31 12:47:41 PDT 2026
```

```
$ cd "~/deadmau5 app"; KIT="tools/showkit"; W="$KIT/work/veldt"; cat > "$W/notes16.py" <<'EOF'
import numpy as np, subprocess
mp3="shows/deadmau5 - The Veldt.mp3"; SR=22050
raw=subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-i",mp3,"-ac","1","-ar",str(SR),"-f","f32le","-"],capture_output=True,check=True).stdout
m=np.frombuffer(raw,dtype=np.float32).copy()
spb=0.468725; t0=0.0425
NOTES="C C# D D# E F F# G G# A A# B".split()
N=4096; win=np.hanning(N); f=np.fft.rfftfreq(N,1/SR)
def midi(fr): return 69+12*np.log2(fr/440)
mm=np.where(f>20,midi(np.maximum(f,1)),-1)
def spec(t):
    a=int( ... [cut]
 0 E  E  E  E  | E  E  A  A  | A  A  A  E  | E  D  D  G#
 1 C# C# B  E  | F# F# E  B  | B  B  A  A  | A  A  A  A 
 2 F# D  D  F# | F# B  A  A  | C# C# C# A  | D  D  D  D 
 3 D  D  A  D  | D  D  D  D  | D  D  D  D  | D  D  D  D 
 4 E  E  E  E  | E  E  D  D  | D  D  C  C  | C  C  C  C 
 5 F# F# B  B  | A  F# E  E  | E  E  A  A  | C# C# C# A 
 6 B  B  D  D  | D  D  E  A  | A  C# C# C# | F# F# A  D 
 7 F# D  F# F# | F# F# F# F# | F# D  D  F# | F# F# F# F#
Sat Oct 31 12:49:51 PDT 2026
```

```
$ cd "~/deadmau5 app"; KIT="tools/showkit"; W="$KIT/work/veldt"; cat > "$W/sprites.py" <<'EOF'
import json
S={}
# 17 columns over x +-171; 17 rows from y_hi 170 to y_lo -119 (17 mm a row).
# The flat-topped acacia: drawn as a solid, the umbrella canopy high on the dome, off centre,
# a thick trunk leaning down to the dome's lower edge. Used dark, in front of the sun.
S["veldt_acacia"]=[
"..................",
"..................",
"....XXXXXXXXXXXX..",
"..XXXXXXXXXXXXXXX.",
"...XXXXXXXXXXXXX..",
".......XX.XX......",
"........XXX.......",
"........XXX.......",
".........XX.......",
".........XX... ... [cut]
{'veldt_acacia': (17, 18, {18}), 'veldt_lion': (9, 19, {19})}
17 17 row height 17.0
 0  y=  162   . . . . 2 4 1 3 3 2 2 3 1 . . . .
 1  y=  144   . . . 5 8 3 5 3 3 4 4 4 7 5 . . .
 2  y=  128   . . 3 4 1 2 2 2 2 2 2 2 1 4 3 . .
 3  y=  110   . 310 4 3 4 3 3 4 3 3 4 3 410 3 .
 4  y=   94   . 5 3 2 2 1 2 1 2 1 2 1 2 2 3 5 .
 5  y=   76   3 3 2 2 2 1 2 1 2 1 2 1 2 2 2 3 3
 6  y=   60   4 3 2 2 1 2 1 1 2 1 1 2 1 2 2 3 4
 7  y=   42   5 2 2 2 . . . . . . . . . 2 2 2 5
 8  y=   26   5 1 . . . . . . . . . . . . . 1 5
 9  y=    8   1 . . . . . . . . . . . . . . . 1
10  y=   -8   . . . . . . . . . . . . . . . . .
11  y=  -26   1 . . . . . . . . . . . . . . . 1
12  y=  -42   3 . . . . . . . . . . . . . . . 3
13  y=  -60   4 . . . . . . . . . . . . . . . 4
14  y=  -76   4 8 2 . . . . . . . . . . . 2 8 4
15  y=  -94   . 4 3 3 . . . . . . . . . 3 3 4 .
16  y= -110   . 2 4 3 2 2 2 . . . 2 2 2 3 4 2 .
9 19 row height 32.111111111111114
17 18 row height 17.0
tools/showkit/songs/veldt/t1.png (1600, 330)
```

```
$ cd "~/deadmau5 app"; KIT="tools/showkit"; W="$KIT/work/veldt"; date; cat > "$W/sprites.py" <<'EOF'
import json
S={}
# 17 columns over x +-171; 17 rows from y_hi 170 to y_lo -119 (17 mm a row).
# The flat-topped acacia, solid, off centre: drawn dark in front of the sun.
S["veldt_acacia"]=[
".................",
"...XXXXXXXXXXX...",
".XXXXXXXXXXXXXXX.",
"...XXX.XXXX.XX...",
"......X.XX.......",
".......XXX.......",
".......XXX.......",
".......XXX.......",
".................",
".................",
".................",
".................",
".................",
".................",
"................ ... [cut]
Sat Oct 31 12:51:52 PDT 2026
{'veldt_acacia': (17, 17, {17}), 'veldt_lion': (17, 17, {17})}
tools/showkit/songs/veldt/t2.png (1600, 330)
```

```
$ cd "~/deadmau5 app"; KIT="tools/showkit"; W="$KIT/work/veldt"; cat > "$W/write_treatment.py" <<'EOF'
import json, sys
KIT="tools/showkit"
sys.path.insert(0, KIT)
from fmt import save
BASE="deadmau5 - The Veldt"
SP={"y_lo":-119,"y_hi":170,"x_half":171}
DARK=[6,3,0]          # brighter than 4, so "over" paints it: a true silhouette in front of whatever is behind

# ---- the chord loop: 8 bars, always the same. One step per beat. Which tubes each new chord fires:
# low chord low tube, high chord high tube. "."  ... [cut]
wrote shows/scenes/deadmau5 - The Veldt.scene.json scenes 19 hits 17
      83   155.66s  energy 0.45  bass 0.62 (punch 1.00)  mid 0.56  high 0.51
      84   157.53s  energy 0.44  bass 0.58 (punch 1.00)  mid 0.74  high 0.45
      85   159.41s  energy 0.51  bass 0.68 (punch 1.00)  mid 0.65  high 0.33
  off        bar 88
      87   163.16s  energy 0.57  bass 0.58 (punch 1.00)  mid 0.71  high 0.57
      88   165.03s  energy 0.00  bass 0.01 (punch 0.62)  mid 0.12  high 0.22
      89   166.91s  energy 0.00  bass 0.00 (punch 0.30)  mid 0.00  high 0.00
deadmau5 - The Veldt: 21 scenes, 17 hits, written into shows/deadmau5 - The Veldt.json
bar 1       dawn           shell max  55 mean   2.0   ears max 157 mean   0.7   sent   84 mA  heat  0.0%  dawn
bar 3                      shell max  56 mean   3.8   ears max 157 mean   0.7   sent  139 mA  heat  0.0%  dawn
bar 5       rise           shell max  55 mean   5.1   ears max 154 mean   1.6   sent  200 mA  heat  0.0%  sunrise
bar 6.5                    shell max  50 mean   7.7   ears max 146 mean   4.4   sent  322 mA  heat  0.0%  sunrise
bar 7.75                   shell max  34 mean   9.6   ears max  52 mean   8.4   sent  446 mA  heat  0.1%  sunrise
bar 8       kick           shell max  23 mean   9.7   ears max 189 mean  28.1   sent  773 mA  heat  0.1%  savanna · KICK
bar 8.25                   shell max   5 mean   3.3   ears max 217 mean  52.8   sent 1000 mA  heat  0.2%  savanna · KICK
bar 12                     shell max  21 mean   9.6   ears max 145 mean  28.3   sent  776 mA  heat  1.0%  savanna
bar 12.5                   shell max  22 mean   9.7   ears max 189 mean  29.5   sent  795 mA  heat  1.1%  savanna
bar 18      tree           shell max  29 mean   9.7   ears max 190 mean  30.0   sent  805 mA  heat  2.3%  acacia
bar 18.25      
... [cut] ...
x  26 mean   9.8   ears max 148 mean   2.3   sent  338 mA  heat 16.0%  tear · THE VELDT
bar 88      off            shell max  23 mean   9.8   ears max   0 mean   0.0   sent  300 mA  heat 16.1%  dark · OFF
bar 88.3                   shell max  46 mean   9.9   ears max   0 mean   0.0   sent  300 mA  heat 16.1%  dark · OFF
bar 88.7                   shell max  24 mean   0.9   ears max   0 mean   0.0   sent   28 mA  heat 16.1%  dark · OFF
tools/showkit/songs/veldt/g1.png (1800, 1960)
Sat Oct 31 12:53:03 PDT 2026
```

```
$ cd "~/deadmau5 app"; KIT="tools/showkit"; W="$KIT/work/veldt"; date; cat > "$W/sprites.py" <<'EOF'
import json
S={}
# 17 columns over x +-171; 17 rows from y_hi 170 to y_lo -119 (17 mm a row).
# The flat-topped acacia, solid, off centre: drawn dark in front of the sun.
S["veldt_acacia"]=[
".................",
".....XXXXXXXXX...",
"...XXXXXXXXXXXXX.",
".....XX.XXX.XX...",
".......X.X.......",
"........XX.......",
"........XX.......",
".......XXXX......",
".................",
".................",
".................",
".................",
".................",
".................",
"................ ... [cut]
Sat Oct 31 12:54:16 PDT 2026
{'veldt_acacia': (17, 17, {17}), 'veldt_acacia2': (17, 17, {17}), 'veldt_lion': (17, 17, {17})}
tools/showkit/songs/veldt/t3.png (1600, 330)
tools/showkit/songs/veldt/t4.png (1600, 330)
```

```
$ cd "~/deadmau5 app"; KIT="tools/showkit"; W="$KIT/work/veldt"; cat > "$W/sprites.py" <<'EOF'
import json
S={}
E17="."*17
def pad(rows):
    rows=list(rows)
    return rows+[E17]*(17-len(rows))
# 17 columns over x +-171; 17 rows from y_hi 170 to y_lo -119 (17 mm a row).
# The flat-topped acacia, solid, off centre: drawn dark in front of the sun.
TREE=[
E17,
".....XXXXXXXXX...",
"...XXXXXXXXXXXXX.",
".....XX.XXX.XX...",
".......X.X.......",
"........XX.......",
"........XX.......",
".......XXXX......",
]
S["veldt_acacia"]=pad(TREE)
# The lion's head from the front, dark: round ears on top, the ma ... [cut]
{'veldt_acacia': (17, 17, {17}), 'veldt_lion': (17, 17, {17}), 'veldt_eyes': (17, 17, {17}), 'veldt_lion_t1': (17, 17, {17}), 'veldt_lion_t2': (17, 17, {17}), 'veldt_lion_t3': (17, 17, {17}), 'veldt_acacia_t1': (17, 17, {17}), 'veldt_acacia_t2': (17, 17, {17}), 'veldt_vult_a': (17, 17, {17}), 'veldt_vult_b': (17, 17, {17}), 'veldt_off0': (17, 17, {17}), 'veldt_off1': (17, 17, {17}), 'veldt_off2': (17, 17, {17}), 'veldt_off3': (17, 17, {17}), 'veldt_off4': (17, 17, {17}), 'veldt_off5': (17, 17, {17}), 'veldt_off6': (17, 17, {17}), 'veldt_off7': (17, 17, {17}), 'veldt_off8': (17, 17, {17})}
wrote shows/scenes/deadmau5 - The Veldt.scene.json scenes 19 hits 17
deadmau5 - The Veldt: 21 scenes, 17 hits, written into shows/deadmau5 - The Veldt.json
bar 3       dawn           shell max  56 mean   4.4   ears max 157 mean   0.7   sent  155 mA  heat  0.0%  dawn
bar 6.5     rise           shell max  52 mean   9.1   ears max 146 mean   3.0   sent  338 mA  heat  0.0%  sunrise
bar 7.75                   shell max  31 mean   9.6   ears max  52 mean   5.5   sent  397 mA  heat  0.1%  sunrise
bar 8       kick           shell max  25 mean   9.7   ears max 138 mean  22.6   sent  681 mA  heat  0.1%  plain · KICK
bar 8.25                   shell max  19 mean   9.7   ears max 150 mean  37.5   sent  931 mA  heat  0.1%  plain · KICK
bar 12                     shell max  21 mean   9.6   ears max 127 mean  21.0   sent  654 mA  heat  0.8%  plain
bar 18      tree           shell max  28 mean   9.7   ears max 109 mean  20.0   sent  638 mA  heat  1.7%  acacia
bar 18.25                  shell max  29 mean   9.7   ears max 110 mean  21.0   sent  656 mA  heat  1.8%  acacia
bar 26      heat           shell max  33 mean   9.7   ears max 135 mean  22.4   sent  677 mA  heat  2.8%  heatup
bar 30              
... [cut] ...
ell max  62 mean   9.7   ears max   0 mean   0.0   sent  292 mA  heat 11.9%  dark · OFF
bar 88.3                   shell max  62 mean   5.7   ears max   0 mean   0.0   sent  170 mA  heat 11.9%  dark · OFF
bar 88.7                   shell max  60 mean   1.4   ears max   0 mean   0.0   sent   43 mA  heat 11.8%  dark · OFF
bar 89                     shell max  59 mean   0.6   ears max   0 mean   0.0   sent   17 mA  heat 11.7%  dark · OFF
tools/showkit/songs/veldt/g2.png (1800, 2205)
Sat Oct 31 12:56:27 PDT 2026
```

```
$ cd "~/deadmau5 app"; KIT="tools/showkit"; W="$KIT/work/veldt"; date; python3 - <<'EOF'
import re
p="tools/showkit/songs/veldt/gsheet.py"
s=open(p).read()
s=s.replace('''cols=6
if "--cols" in args:
    i=args.index("--cols"); cols=int(args[i+1]); del args[i:i+2]
''','''cols=6
if "--cols" in args:
    i=args.index("--cols"); cols=int(args[i+1]); del args[i:i+2]
BIG=False
if "--big" in args:
    i=args.index("--big"); BIG=True; del args[i]
''')
s=s.replace('''W = 300; H = 245
''','''W = 300; H = 245
if BIG:
     ... [cut]
Sat Oct 31 12:57:33 PDT 2026
bar 86.75                  shell max  23 mean   6.7   ears max 103 mean   1.9   sent  243 mA  heat 11.8%  tear · THE VELDT
bar 87.5                   shell max  47 mean   9.9   ears max 143 mean   2.2   sent  337 mA  heat 11.9%  tear · THE VELDT
tools/showkit/songs/veldt/big1.png (1500, 1218)
```

```
$ cd "~/deadmau5 app"; KIT="tools/showkit"; W="$KIT/work/veldt"; date; python3 - <<'EOF'
import numpy as np
# Which bars carry the recurring noise accent? air-band peak per beat, top beats and their position in the bar
z=np.load("tools/showkit/songs/veldt/E.npz")
tt=z["tt"]; air=z["air"]; pres=z["pres"]
spb=0.468725; t0=0.0425
vals=[]
for b in range(8*4,88*4):
    T=t0+b*spb
    a=np.searchsorted(tt,T+0.08); c=np.searchsorted(tt,T+0.40)
    vals.append((np.log1p(air[a:c].mean()*2),b))
v=np.array([x[0] for x in  ... [cut]
Sat Oct 31 12:58:49 PDT 2026
median 4.684195900384168
[(8, 0, np.float64(1.98)), (8, 2, np.float64(2.57)), (9, 0, np.float64(2.25)), (9, 1, np.float64(3.32)), (9, 2, np.float64(3.48)), (9, 3, np.float64(3.85)), (10, 0, np.float64(2.35)), (10, 1, np.float64(1.72)), (14, 0, np.float64(2.44)), (16, 1, np.float64(3.94)), (16, 2, np.float64(2.16)), (17, 0, np.float64(1.83)), (18, 0, np.float64(1.99)), (18, 3, np.float64(2.37)), (21, 1, np.float64(2.52)), (21, 2, np.float64(3.96)), (22, 0, np.float64(1.67)), (32, 0, np.float64(1.89)), (33, 0, np.float64(2.85)), (33, 1, np.float64(3.67)), (34, 0, np.float64(3.0)), (34, 1, np.float64(3.01)), (34, 3, np.float64(1.9)), (36, 1, np.float64(2.19)), (37, 0, np.float64(2.53)), (37, 1, np.float64(2.71)), (38, 0, np.float64(2.49)), (38, 1, np.float64(1.96)), (38, 2, np.float64(1.67)), (38, 3, np.float64(2.22)), (40, 1, np.float64(4.14)), (41, 1, np.float64(3.72)), (42, 1, np.float64(2.72)), (42, 2, np.float64(3.78)), (43, 0, np.float64(3.82)), (45, 0, np.float64(1.8)), (45, 1, np.float64(2.78)), (45, 2, np.float64(3.88)), (48, 0, np.float64(1.77)), (50, 3, np.float64(1.67)), (51, 0, np.float64(1.67)), (54, 3, np.float64(1.64)), (55, 0, np.float64(1.68)), (72, 0, np.float64(1.82))]
```

```
$ cd "~/deadmau5 app"; KIT="tools/showkit"; W="$KIT/work/veldt"; python3 - <<'EOF'
import numpy as np
z=np.load("tools/showkit/songs/veldt/E.npz")
tt=z["tt"]; air=z["air"]
spb=0.468725; t0=0.0425
# 16th-note resolution level in the air band, in dB above the median of the same position in the beat (so hats and claps are removed)
n=int(88*16)
L=np.zeros(n)
for k in range(n):
    T=t0+k*spb/4
    a=np.searchsorted(tt,T); c=np.searchsorted(tt,T+spb/4)
    L[k]=10*np.log10(air[a:c].mean()+1e-6)
ex=L.copy()
for q in  ... [cut]
  8 .#+. .#+. .##+ ....
  9 .#+. ###. .##. .+##
 10 .##. .#+. .... ....
 11 .... .... .... ....
 12 .... .#.. .#.. .#..
 13 .+.. .... .... ....
 14 .+## .... ...+ .#..
 15 .... .... .... ....
 16 .... .+## .#+. ....
 17 .#.. .+.. .... ...+
 18 .#+. .+.. .... .##.
 19 .... .... .... ....
 20 .... .+.. .+.. ....
 21 .#.. +#.. ..## ....
 22 .#.. .... .... ....
 23 .... .... .... .#..
 24 .+.. .... .... ....
 25 .... .... .... ....
 26 .... .#.. .... .+.+
 27 .#.. .... .... ....
 28 .... .... .... ....
 29 .... .... .... ....
 30 .... .#.. .... .+.+
 31 .#.. .... .... ....
 32 .#+. .+.. .+.. .+..
 33 .### ##+. .... ...+
 34 +##. .#.. .+.. +#+.
 35 .... .... .... ....
 36 .... .#+. .#.. ....
 37 .##. .#+. .... ....
 38 .#+. .#+. .#+. +#..
 39 .... .... .... ....
 40 .... .+## .+.. ....
 41 .#.. ###. .... ....
 42 .#.. .#+. .+## .#..
 43 .+## .... .... ....
 44 .... .+.. .#.. ....
 45 .#+. ##.. ..## ....
 46 .#.. .... .... ....
 47 .... .... .... .#..
 48 .#+. .+.. .... ....
 49 .... .... .... ....
 50 .... .#.. .... .+.+
 51 .#+. .... .... ....
 52 .... .... .... ....
 53 .... .... .... ....
 54 .... .#.. .... .+.+
 55 .#+. .... .... .#..
 56 .+.. .+.. .... ....
 57 .... .... .... ....
 58 .... .#.. .... .+..
 59 .#.. .... .... .#..
 60 .+.. .+.. .... ....
 61 .... .... .... ....
 62 .... .#.. .... ....
 63 .#+. .... .... ....
 64 .... .... .... ....
 65 .... .... .... ....
 66 .... .... .... ....
 67 .... .... .... ....
 68 .... .... .... ....
 69 .... .... .... ....
 70 .... .... .... ....
 71 .... .... .... .#..
 72 .#+. .+.. .... ....
 73 .... .... .... ....
 74 .... .#.. .... .#.+
 75 .#+. .... .... ....
 76 .... .... .... ....
 77 .... .... .... ....
 78 .... .... .... ....
 79 .... .... .... .#..
 80 .+.. .... .... ....
 81 .... .... .... ....
 82 .... .#.. .... .+..
 83 .#.. .... .... .#..
 84 .+.. .... .... ....
 85 .... .... .... ....
 86 .... .#.. .... ....
 87 .+.. .... .... ....
```

```
$ cd "~/deadmau5 app"; KIT="tools/showkit"; W="$KIT/work/veldt"; python3 - <<'EOF'
p="tools/showkit/songs/veldt/sprites.py"
s=open(p).read()
# steeper eyes; a closed-eye head; bigger vultures; a flock
s=s.replace('''".XXX...XXX...XXX.",
".XXXX...X...XXXX.",
".XXXXXXXXXXXXXXX.",
"..XXXXX...XXXXX..",''','''".XX...XXXXX...XX.",
".XXXX...X...XXXX.",
".XXXXXXXXXXXXXXX.",
"..XXXXX...XXXXX..",''')
s=s.replace('''S["veldt_eyes"]=pad([E17,E17,E17,"....XXX...XXX....",".....XXX.XXX....."])''','''S["veldt_eyes"]=pad([E17,E ... [cut]
# ---- the kick: the plain by day. The ears are grass, and they play the chord changes.
S({"name":"plain","from":"kick","to":"tree","pal":"sun","pump":PUMP,"layers":[
  {"use":"sun"},{"use":"jawgrass"},{"use":"grass"},{"use":"roots"},chords(8,0.36,pal="grass"),{"use":"birds","gain":0.5}]})
# ---- the acacia against the sun
S({"name":"acacia","from":"tree","to":"heat","pal":"sun","pump":PUMP,"layers":[
{'veldt_acacia': (17, 17, {17}), 'veldt_lion': (17, 17, {17}), 'veldt_eyes': (17, 17, {17}), 'veldt_eyes_half': (17, 17, {17}), 'veldt_eyes_shut': (17, 17, {17}), 'veldt_lion_b': (17, 17, {17}), 'veld
```

```
$ cd "~/deadmau5 app"; KIT="tools/showkit"; W="$KIT/work/veldt"; cat > "$W/write_treatment.py" <<'EOF'
import json, sys
KIT="tools/showkit"
sys.path.insert(0, KIT)
from fmt import save
BASE="deadmau5 - The Veldt"
SPB=0.468725
SP={"y_lo":-119,"y_hi":170,"x_half":171}
DARK=[6,3,0]          # brighter than 4, so "over" paints it: a true silhouette in front of whatever is behind
E8=round(2.0/SPB,5)   # flip-book frames a second for one frame an 8th note

# ---- the chord loop: 8 bars, always the same. One step per ... [cut]
wrote shows/scenes/deadmau5 - The Veldt.scene.json scenes 20 hits 85
      88   165.03s  energy 0.00  bass 0.01 (punch 0.62)  mid 0.12  high 0.22
      89   166.91s  energy 0.00  bass 0.00 (punch 0.30)  mid 0.00  high 0.00
deadmau5 - The Veldt: 22 scenes, 85 hits, written into shows/deadmau5 - The Veldt.json
bar 6.5     rise           shell max  44 mean   9.6   ears max 146 mean   3.0   sent  355 mA  heat  0.0%  sunrise
bar 7.25                   shell max  35 mean   9.6   ears max  56 mean   4.0   sent  371 mA  heat  0.1%  sunrise
bar 8       kick           shell max  26 mean   9.7   ears max 127 mean  16.1   sent  574 mA  heat  0.1%  plain · KICK
bar 8.25                   shell max  20 mean   9.6   ears max 158 mean  41.8   sent 1000 mA  heat  0.2%  plain · KICK · cry
bar 9.3     cry            shell max  25 mean   9.3   ears max 151 mean  17.1   sent  581 mA  heat  0.3%  plain · cry
bar 12                     shell max  22 mean   9.6   ears max 127 mean  12.5   sent  514 mA  heat  0.7%  plain
bar 18      tree           shell max  29 mean   9.7   ears max 157 mean  18.2   sent  608 mA  heat  1.4%  acacia · cry
bar 21.3    cry            shell max  32 mean   9.3   ears max 151 mean  20.9   sent  643 mA  heat  1.8%  acacia · cry
bar 26      heat           shell max  34 mean   9.7   ears max 135 mean  22.4   sent  677 mA  heat  2.4%  heatup
bar 30                     shell max  22 mean   9.7   ears max 135 mean  22.4   sent  677 mA  heat  3.6%  heat
bar 33.1    stalk          shell max  21 mean   8.3   ears max 135 mean  11.7   sent  461 mA  heat  4.0%  stalk · cry
bar 38.1                   shell max  27 mean   8.3   ears max 135 mean  11.6   sent  458 mA  heat  4.5%  stalk · cry
bar 41.1                   shell max  34 mean   8.4   ears max 135 mean   9.4   sent  422 
... [cut] ...
x 147 mean   8.1   sent  441 mA  heat 12.0%  static · THE VELDT
bar 87                     shell max  38 mean   9.7   ears max 159 mean  22.8   sent  682 mA  heat 12.0%  static · THE VELDT · flare
bar 87.5                   shell max  53 mean   9.9   ears max 143 mean   2.2   sent  337 mA  heat 12.1%  static · THE VELDT
bar 88      off            shell max  62 mean   9.7   ears max   0 mean   0.0   sent  292 mA  heat 12.1%  dark · OFF
tools/showkit/songs/veldt/g3.png (1800, 2205)
Sat Oct 31 13:01:33 PDT 2026
```

```
$ cd "~/deadmau5 app"; KIT="tools/showkit"; W="$KIT/work/veldt"; date; python3 "$W/gsheet.py" "deadmau5 - The Veldt" "$W/big2.png" --big --cols 3 6.5:flock 18.1:tree 38.6:stalk 49:pride 53.4:blink 59.5:noon 60.1:noon 71.7:leap 83.75:torn | tail -1
Sat Oct 31 13:01:45 PDT 2026
tools/showkit/songs/veldt/big2.png (1500, 1218)
```

```
$ cd "~/deadmau5 app"; KIT="tools/showkit"; W="$KIT/work/veldt"; date; python3 - <<'EOF'
W="tools/showkit/songs/veldt/"
s=open(W+"sprites.py").read()
a=s.index('LION=['); b=s.index('S["veldt_lion"]=pad(LION)')
s=s[:a]+'''LION=[
"....XX.....XX....",
"...XXXX...XXXX...",
"...XXXXXXXXXXX...",
"..XX...XXX...XX..",
"..XXX...X...XXX..",
"...XXXXXXXXXXX...",
"....XXX...XXX....",
".....XXXXXXX.....",
"......XXXXX......",
]
'''+s[b:]
s=s.replace('''S["veldt_eyes"]=pad([E17,E17,E17,"...XXX.....XXX...",".....XXX.XXX....." ... [cut]
Sat Oct 31 13:03:39 PDT 2026
wrote shows/scenes/deadmau5 - The Veldt.scene.json scenes 20 hits 87
  hit ROAR overlaps 2 other hits
bar 12      plain          shell max  22 mean   9.6   ears max 127 mean  12.5   sent  514 mA  heat  0.7%  plain
bar 18.1    tree           shell max  28 mean   8.3   ears max 135 mean  12.8   sent  479 mA  heat  1.4%  acacia · cry
bar 26      heat           shell max  34 mean   9.7   ears max 135 mean  22.4   sent  677 mA  heat  2.4%  heatup
bar 38.6    stalk          shell max  26 mean   8.3   ears max 135 mean   9.3   sent  420 mA  heat  4.5%  stalk · cry
bar 44                     shell max  41 mean   9.7   ears max  56 mean   8.8   sent  452 mA  heat  4.9%  stalk
bar 47      open           shell max  30 mean   9.7   ears max 133 mean  30.3   sent  810 mA  heat  5.3%  open
bar 49      pride          shell max  23 mean   7.0   ears max  54 mean  13.2   sent  441 mA  heat  5.8%  pride
bar 53.3    blink          shell max  21 mean   6.4   ears max 140 mean  42.7   sent  921 mA  heat  6.8%  pride
bar 55.5    roar           shell max  34 mean   9.7   ears max  75 mean  19.4   sent  628 mA  heat  7.3%  pride
bar 59.5    noon           shell max  40 mean   9.8   ears max  81 mean  21.1   sent  656 mA  heat  8.3%  noon
bar 62      sundown        shell max  41 mean   7.9   ears max  60 mean  17.4   sent  541 mA  heat  9.0%  sundown
bar 74      day2           shell max  32 mean   9.7   ears max  75 mean  18.5   sent  613 mA  heat  9.8%  day2
bar 77.6    flick          shell max  26 mean   8.4   ears max  61 mean  11.8   sent  461 mA  heat 10.5%  flicker · flaw3
bar 81      gold           shell max  29 mean   9.7   ears max  85 mean  20.5   sent  646 mA  heat 11.1%  gold
bar 83.5    roar           shell max  32 mean   9.6   ears max  85 mean  20.5   sent  646 mA  heat 11.7%  gold · flaw9
bar 84.5    tear           shell max  46 mean   9.8   ears max 145 mean  15.8   sent  568 mA  heat 11.9%  tear
tools/showkit/songs/veldt/g4.png (2000, 1624)
Sat Oct 31 13:03:41 PDT 2026
```

```
$ cd "~/deadmau5 app"; KIT="tools/showkit"; W="$KIT/work/veldt"; date; python3 - <<'EOF'
W="tools/showkit/songs/veldt/"
t=open(W+"write_treatment.py").read()
a='HITS+=[flare(74.25,"hot"),flare(75,"hot"),flare(82.25),flare(83)]'
assert a in t
t=t.replace(a,'HITS+=[flare(74.25,"hot"),flare(75,"hot"),flare(82.25)]')
open(W+"write_treatment.py","w").write(t)
EOF
python3 "$W/write_treatment.py" && python3 mau5scene.py compile "deadmau5 - The Veldt" 2>&1 | tail -1 && python3 "$W/gsheet.py" "deadmau5 - The Veldt" "$W/ ... [cut]
Sat Oct 31 13:03:51 PDT 2026
wrote shows/scenes/deadmau5 - The Veldt.scene.json scenes 20 hits 86
deadmau5 - The Veldt: 22 scenes, 86 hits, written into shows/deadmau5 - The Veldt.json
bar 12      plain          shell max  24 mean   9.7   ears max 127 mean  12.5   sent  514 mA  heat  0.7%  plain
bar 18.1    tree           shell max  33 mean   8.3   ears max 135 mean  12.8   sent  479 mA  heat  1.4%  acacia · cry
bar 26      heat           shell max  36 mean   9.8   ears max 135 mean  22.4   sent  677 mA  heat  2.4%  heatup
bar 38.6    stalk          shell max  30 mean   8.3   ears max 135 mean   9.3   sent  420 mA  heat  4.5%  stalk · cry
bar 44                     shell max  43 mean   9.7   ears max  56 mean   8.8   sent  452 mA  heat  4.9%  stalk
bar 47      open           shell max  32 mean   9.7   ears max 133 mean  30.3   sent  810 mA  heat  5.3%  open
bar 49      pride          shell max  28 mean   6.9   ears max  65 mean  15.9   sent  486 mA  heat  5.9%  pride
bar 53.3    blink          shell max  16 mean   3.7   ears max 153 mean  46.7   sent  905 mA  heat  6.9%  pride
bar 55.5    roar           shell max  35 mean   9.7   ears max  91 mean  23.4   sent  694 mA  heat  7.5%  pride · ROAR
bar 59.5    noon           shell max  41 mean   9.8   ears max  81 mean  21.1   sent  656 mA  heat  8.5%  noon
bar 62      sundown        shell max  41 mean   7.8   ears max  60 mean  17.4   sent  538 mA  heat  9.2%  sundown
bar 74      day2           shell max  37 mean   9.7   ears max  91 mean  22.2   sent  675 mA  heat 10.0%  day2
bar 77.6    flick          shell max  29 mean   8.3   ears max  61 mean  11.8   sent  461 mA  heat 10.8%  flicker · flaw3
bar 81      gold           shell max  33 mean   9.8   ears max 111 mean  26.6   sent  747 mA  heat 11.4%  gold
bar 83.5    roar           shell max  34 mean   9.7   ears max 111 mean  26.6   sent  747 mA  heat 12.1%  gold · ROAR · flaw9
bar 84.5    tear           shell max  43 mean   9.8   ears max 145 mean  15.8   sent  568 mA  heat 12.3%  tear
tools/showkit/songs/veldt/g4.png (2000, 1624)
Sat Oct 31 13:03:52 PDT 2026
```

```
$ cd "~/deadmau5 app"; KIT="tools/showkit"; W="$KIT/work/veldt"; date; grep -n "GOV_RISE\s*=\|GOV_FROM\s*=\|GOV_MIN_DT\s*=" mau5power.py; cat > "$W/gov.py" <<'EOF'
#!/usr/bin/env python3
"""Per scene: how much is the shell being robbed? asked vs. sent on shell and ears, share of frames the global governor bites, its deepest bite."""
import json, os, sys
sys.path.insert(0, os.getcwd())
import numpy as np, mau5show, mau5power, mau5scene, mau5engine as E
base=sys.argv[1]
show=json.load(open(os.path.join("shows",base+".json")))
music=mau5show._music_for(show,os.path.join("shows",base+".mp3"))
h=E.Hel ... [cut]
Sat Oct 31 13:04:23 PDT 2026
56:GOV_RISE = 1.0
57:GOV_MIN_DT = 1.0 / 40.0
58:GOV_FROM = 0.01
scene        from   shell   ears   gov%   minS  meanS     mA  pk mA
dark          0.0     1.5    0.0      0   1.00   1.00     46    292   asked shell   5.1
dawn          0.1     3.1    0.5      0   1.00   1.00    115    175   asked shell   4.0
sunrise       7.6     8.3    2.5      0   1.00   1.00    308    401   asked shell  15.1
plain        15.1     9.7   13.8      0   0.96   1.00    535   1000   asked shell  25.9
acacia       30.1     9.7   13.4      0   1.00   1.00    528    815   asked shell  20.4
heatup       45.1     9.5   21.4     13   0.91   0.99    652   1000   asked shell  23.4
heat         52.6     9.6   21.7      6   0.93   1.00    662   1000   asked shell  29.0
stalk        60.1     9.7    9.4      0   1.00   1.00    463    688   asked shell  24.4
open         84.4     9.7   20.1      0   1.00   1.00    640    984   asked shell  22.9
pride        90.1     8.3   30.0     34   0.72   0.96    762   1000   asked shell  28.2
noon        105.1     9.4   28.9     20   0.83   0.99    773   1000   asked shell  22.9
sundown     114.4     7.9   20.5      5   0.94   1.00    593   1000   asked shell  11.5
night       120.1     7.0    2.2      0   1.00   1.00    260    304   asked shell  11.2
closer      127.6     9.2   12.9      0   1.00   1.00    509    552   asked shell  16.6
prowl       131.3     9.2    4.0      0   1.00   1.00    355    453   asked shell  18.3
gone        133.2     2.7    8.0      0   1.00   1.00    217    585   asked shell   5.2
day2        135.1     8.2   30.8     39   0.73   0.96    773   1000   asked shell  31.8
flicker     142.6     9.7   14.8      0   1.00   1.00    551    788   asked shell  20.5
gold        150.1     7.5   34.3     44   0.69   0.94    810   1000   asked shell  33.9
tear        157.6     9.2    9.7      0   1.00   1.00    450    663   asked shell  16.6
static      159.4     9.4   13.3      4   0.97   1.00    511   1000   asked shell  36.9
```

```
$ cd "~/deadmau5 app"; KIT="tools/showkit"; W="$KIT/work/veldt"; date; grep -n "case 'orb'\|fx === 'orb'\|\"orb\"\|'orb'" remote/offline/show.js | head; grep -n "orb" remote/offline/show.js | head -20; sed -n "$(grep -n "'orb'" remote/offline/show.js | head -1 | cut -d: -f1),+24p" remote/offline/show.js; python3 - <<'EOF'
W="tools/showkit/songs/veldt/"
t=open(W+"write_treatment.py").read()
def R(a,b):
    global t
    assert a in t, a
    t=t.replace(a,b)
R('"scale":1.6,"speed":-0.5,"gain":0.36}','"scale":1.6," ... [cut]
Sat Oct 31 13:04:43 PDT 2026
643:      case 'orb': {
288:  orb: ['x', 'y', 'rad', 'soft', 'wx', 'wy', 'xf', 'yf', 'xp', 'yp', 'cgrad'],
643:      case 'orb': {
      case 'orb': {
        let x0 = valAt(P.x, p, bar, music, tt), y0 = valAt(P.y, p, bar, music, tt);
        const wx = valAt(P.wx, p, bar, music, tt), wy = valAt(P.wy, p, bar, music, tt);
        if (wx !== 0) {
          x0 = x0 + wx * Math.sin(2 * Math.PI * (B * valAt(P.xf, p, bar, music, tt)
                                                 + valAt(P.xp, p, bar, music, tt)));
        }
        if (wy !== 0) {
          y0 = y0 + wy * Math.sin(2 * Math.PI * (B * valAt(P.yf, p, bar, music, tt)
                                                 + valAt(P.yp, p, bar, music, tt)));
        }
        const rad = valAt(P.rad, p, bar, music, tt), soft = valAt(P.soft, p, bar, music, tt);
        const cgrad = valAt(P.cgrad, p, bar, music, tt);
        const PX = this.h.px, PY = this.h.py;
        for (let m = 0; m < nm; m++) {
          const i = idx[m];
          const d = Math.hypot(PX[i] - x0, PY[i] - y0);
          const e = sclamp((rad - d) / soft, 0, 1);
          this._pal(P, c0 + cgrad * d / rad);
          this._put(mix, i, G * (e * e * (3 - 2 * e)));
        }
        break;
      }
      case 'twinkle': {
        const rate = valAt(P.rate, p, bar, music, tt), sharp = valAt(P.sharp, p, bar, music, tt);
wrote shows/scenes/deadmau5 - The Veldt.scene.json scenes 20 hits 86
deadmau5 - The Veldt: 22 scenes, 86 hits, written into shows/deadmau5 - The Veldt.json
scene        from   shell   ears   gov%   minS  meanS     mA  pk mA
dark          0.0     1.5    0.0      0   1.00   1.00     46    292   asked shell   5.1
dawn          0.1     3.1    0.5      0   1.00   1.00    115    175   asked shell   4.0
sunrise      
... [cut] ...
.3     9.2    4.0      0   1.00   1.00    355    453   asked shell  18.3
gone        133.2     2.7    8.0      0   1.00   1.00    217    585   asked shell   5.2
day2        135.1     9.3   26.4     13   0.80   0.99    733   1000   asked shell  31.8
flicker     142.6     9.7   14.8      0   1.00   1.00    551    788   asked shell  20.5
gold        150.1     8.9   28.2     21   0.76   0.98    750   1000   asked shell  33.9
tear        157.6     9.2    9.7      0   1.00   1.00    450    663   asked shell  16.6
static      159.4     9.4   12.9      1   0.99   1.00    506   1000   asked shell  36.9
```

```
$ cd "~/deadmau5 app"; KIT="tools/showkit"; W="$KIT/work/veldt"; date; python3 - <<'EOF'
W="tools/showkit/songs/veldt/"
s=open(W+"sprites.py").read()
if "veldt_melt" not in s:
    s=s.replace('# Torn frames:','''# The tree melting in the heat: its cells go a few at a time, from the bottom up.
import random
rng=random.Random(7)
cells=[(r,c) for r,row in enumerate(TREE) for c,ch in enumerate(row) if ch!="."]
cells.sort(key=lambda rc:(-rc[0]+rng.random()*2.5))
def without(k):
    rows=[list(x) for x in TREE]
    f ... [cut]
Sat Oct 31 13:05:55 PDT 2026
wrote shows/scenes/deadmau5 - The Veldt.scene.json scenes 20 hits 86
deadmau5 - The Veldt: 22 scenes, 86 hits, written into shows/deadmau5 - The Veldt.json
tools/showkit/songs/veldt/g5.png (1800, 3430)
Sat Oct 31 13:05:57 PDT 2026
```

```
$ cd "~/deadmau5 app"; KIT="tools/showkit"; W="$KIT/work/veldt"; date; python3 mau5scene.py check "deadmau5 - The Veldt"; python3 "$KIT/grid.py" check "deadmau5 - The Veldt"; python3 "$W/gsheet.py" "deadmau5 - The Veldt" "$W/big3.png" --big --cols 4 8:kick 8.0625 8.125 8.25 55.05:roar 55.3 55.6 55.9 71.55:leap 71.8 71.95 72 83.1:roar 84.1:tear 85.3:static 87.6 | tail -1
Sat Oct 31 13:06:20 PDT 2026
deadmau5 - The Veldt: 4253 frames at 25 fps through the guard
  scene            from  mean mA   p95 mA     heat   allow W      ms
  dark             0.0s       46      290    12.1%      18.1    0.03
  dawn             0.1s      117      169     0.0%      18.1    0.13
  sunrise          7.6s      309      394     0.1%      18.1    0.19
  plain           15.1s      470      709     1.1%      18.1    0.16
  acacia          30.1s      467      718     2.2%      18.1    0.20
  heatup          45.1s      575      994     3.0%      18.1    0.18
  heat            52.6s      583      966     3.9%      18.1    0.14
  stalk           60.0s      409      595     5.0%      18.1    0.23
  open            84.4s      562      858     5.6%      18.1    0.21
  pride           90.0s      589      981     7.3%      18.1    0.27
  noon           105.0s      631     1000     8.6%      18.1    0.17
  sundown        114.4s      517      966     9.1%      18.1    0.15
  night          120.0s      259      297     9.1%      18.1    0.12
  closer         127.6s      509      546     9.3%      18.1    0.15
  prowl          131.3s      356      412     9.3%      18.1    0.18
  gone           133.2s      217      540     9.3%      18.1    0.08
  day2           135.0s      598      979    10.2%      18.1    0.27
  flicker        142.6s      488      731    10.8%      18.1    0.20
  gold           150.0s      611      998    11.7%      18.1    0.29
  tear           157.6s      379      628    11.8%      18.1    0.21
  static         159.4s      418      689    12.1%      18.1    0.26
  worst frame 1.22 ms; no scene reaches the sustained floor
deadmau5 - The Veldt: 128.007 BPM, 91 bars, bar 0 at 0.043 s, holds []
music against the grid per 8 bars, ms (contrast): 0:-1(8.52)  8:-1(3.19)  16:-1(1.89)  24:-1(2.09)  32:-3(1.68)  40:-1(2.02)  48:-1(2.12)  56:+1(2.08)  64:-1(2.61)  72:-1(2.43)  80:-1(2.21)  88:+5(1.41)
worst 5 ms where the music is clear enough to say, mean -0.1 ms
tools/showkit/songs/veldt/big3.png (2000, 1624)
```

```
$ cd "~/deadmau5 app"; KIT="tools/showkit"; W="$KIT/work/veldt"; date; python3 mau5scene.py check "deadmau5 - The Veldt"; python3 "$KIT/grid.py" check "deadmau5 - The Veldt"; python3 "$W/gsheet.py" "deadmau5 - The Veldt" "$W/big3.png" --big --cols 4 8:kick 8.0625 8.125 8.25 55.05:roar 55.3 55.6 55.9 71.55:leap 71.8 71.95 72 83.1:roar 84.1:tear 85.3:static 87.6 | tail -1
Sat Oct 31 13:06:20 PDT 2026
deadmau5 - The Veldt: 4253 frames at 25 fps through the guard
  scene            from  mean mA   p95 mA     heat   allow W      ms
  dark             0.0s       46      290    12.1%      18.1    0.03
  dawn             0.1s      117      169     0.0%      18.1    0.13
  sunrise          7.6s      309      394     0.1%      18.1    0.19
  plain           15.1s      470      709     1.1%      18.1    0.16
  acacia          30.1s      467      718     2.2%      18.1    0.20
  heatup          45.1s      575      994     3.0%      18.1    0.18
  heat            52.6s      583      966     3.9%      18.1    0.14
  stalk           60.0s      409      595     5.0%      18.1    0.23
  open            84.4s      562      858     5.6%      18.1    0.21
  pride           90.0s      589      981     7.3%      18.1    0.27
  noon           105.0s      631     1000     8.6%      18.1    0.17
  sundown        114.4s      517      966     9.1%      18.1    0.15
  night          120.0s      259      297     9.1%      18.1    0.12
  closer         127.6s      509      546     9.3%      18.1    0.15
  prowl          131.3s      356      412     9.3%      18.1    0.18
  gone           133.2s      217      540     9.3%      18.1    0.08
  day2           135.0s      598      979    10.2%      18.1    0.27
  flicker        142.6s      488      731    10.8%      18.1    0.20
  gold           150.0s      611      998    11.7%      18.1    0.29
  tear           157.6s      379      628    11.8%      18.1    0.21
  static         159.4s      418      689    12.1%      18.1    0.26
  worst frame 1.22 ms; no scene reaches the sustained floor
deadmau5 - The Veldt: 128.007 BPM, 91 bars, bar 0 at 0.043 s, holds []
music against the grid per 8 bars, ms (contrast): 0:-1(8.52)  8:-1(3.19)  16:-1(1.89)  24:-1(2.09)  32:-3(1.68)  40:-1(2.02)  48:-1(2.12)  56:+1(2.08)  64:-1(2.61)  72:-1(2.43)  80:-1(2.21)  88:+5(1.41)
worst 5 ms where the music is clear enough to say, mean -0.1 ms
tools/showkit/songs/veldt/big3.png (2000, 1624)
```

```
$ cd "~/deadmau5 app"; KIT="tools/showkit"; W="$KIT/work/veldt"; date; tail -30 "$KIT/BRIEF.md"; echo ----; cat "$KIT/sheet.py"; echo ----; cat "$KIT/power.py"; echo ----; cat "$KIT/scenepower.py"; echo ----; python3 "$KIT/power.py" "deadmau5 - The Veldt"; python3 "$KIT/scenepower.py" "deadmau5 - The Veldt"
Sat Oct 31 13:07:16 PDT 2026
4. Write the treatment with a small Python generator in your scratch folder (see Tiki's), using `from fmt import save` with `sys.path.insert(0, KIT)`, then `python3 mau5scene.py compile "<base>"` and fix what it refuses. Put a real `about` string in it describing the concept, the same style as Tiki's.
5. Look at it. `python3 $KIT/sheet.py "<base>" out.png 40:drop 40.25 41 ...` renders tiles as the helmet will really look after the power guard, and prints how bright shell and ears end up. READ THE PNG. Does it read as your idea? Is the shell visible next to the ears? Check every major section, each hit, and both a kick and the gap after it. Iterate.
6. `python3 mau5scene.py check "<base>"`: every scene through the power guard. Heat under about 40%, and no scene "at the sustained floor". `python3 $KIT/grid.py check "<base>"` again at the end.

## The treatment format
Bars, not seconds: bar b is `t0 + 4 b spb` on your grid. Top level: `v:1, show, about, lead:0, marks{name:bar or "other+2"}, palettes{name:[[r,g,b],...] or {"stops":[...],"wrap":true}}, motifs{name: layer or [layers]}, scenes[], hits[]`. A value may be a number, `[from,to]` (a ramp over the scene), `{"<bar or mark>":v,...}` (steps at bars), or `{"band":"bass|mid|high","lo":a,"hi":b,"punch":true|false}` (driven by the track, resolved live; the phone has these curves). Scenes tile the song, from bar -1 (a gap is dark): `{"name","from","to","pal","pump":{"pat":"x...","step":0.25,"depth":0.2,"decay":0.5},"out":beats of darkness before the next scene (max 4),"layers":[...]}`; `like:"earlier scene"` copies one and `patch:{"layerIndex":{...}}`, `add:[...]` or `each:{...}` change it (patch indexes the authored layers before motif expansion). Hits are moments over a scene: `{"name","at":ba
... [cut] ...
.2     57   9.1%
closer            509    546      0     19     9.2    12.9     61   9.3%
prowl             356    412      0     40     9.2     4.0     62   9.3%
gone              217    540      0      0     2.7     8.0     62   9.3%
day2              598    979     13    100     7.5    21.7     38  10.2%
flicker           488    731      0    100     8.5    13.2     35  10.8%
gold              611    998     22    100     7.1    23.1     31  11.7%
tear              379    628      0     64     7.4     8.7     41  11.8%
static            418    689      2     84     7.6    10.9     48  12.1%
```

```
$ cd "~/deadmau5 app"; KIT="tools/showkit"; W="$KIT/work/veldt"; date; python3 - <<'EOF'
W="tools/showkit/songs/veldt/"
t=open(W+"write_treatment.py").read()
def R(a,b):
    global t
    assert a in t, a
    t=t.replace(a,b)
R('''      {"fx":"orb","on":"jaw","mix":"over","x":0,"y":-112,"rad":[20,200],"soft":50,"pal":"hot","c":0.8,"cgrad":-0.5,"gain":[0.8,0.25]},
      {"fx":"preset","name":"sprite","on":"shell","mix":"over","gain":[1.0,0.5],"params":dict(SP,sprite="veldt_eyes",color=[255,190,70])}]}''','''      ... [cut]
Sat Oct 31 13:08:25 PDT 2026
wrote shows/scenes/deadmau5 - The Veldt.scene.json scenes 20 hits 86
deadmau5 - The Veldt: 22 scenes, 86 hits, written into shows/deadmau5 - The Veldt.json
tools/showkit/songs/veldt/big4.png (2000, 1624)
```

```
$ cd "~/deadmau5 app"; date; grep -n "SPRITES\|sprites" mau5offline.py | head -20; grep -n "sprite" remote/offline/engine.js | head -20; ls -la "shows/deadmau5 - The Veldt.json" "shows/TIKI TIKI - Slowed.json"; git status --short | grep -i "veldt" | head; ls -la shows/scenes | grep -c sprites
Sat Oct 31 13:09:12 PDT 2026
73:    from mau5fx import FONT5x7, SPRITES
96:            "sprites": {k: list(v) for k, v in SPRITES.items()},
168:function spriteBitmap(fonts, name) {
169:  const rows = fonts.sprites[name];
458:def('sprite', { sprite: 'smile', color: [0, 255, 255], bg: [0, 0, 0],
463:    const names = String(this.p.sprite).split('|');
465:    const bm = spriteBitmap(this.fonts, names[at]);
968:              textBitmap, glyphBitmap, digitBitmap, spriteBitmap, fract, pmod,
-rw-r--r--@ 1 jones  staff  171705 Oct 30 19:20 shows/TIKI TIKI - Slowed.json
-rw-r--r--@ 1 jones  staff  192796 Oct 31 13:08 shows/deadmau5 - The Veldt.json
?? "shows/deadmau5 - The Veldt.analysis.npz"
?? "shows/deadmau5 - The Veldt.json"
?? "shows/scenes/deadmau5 - The Veldt.beats"
?? "shows/scenes/deadmau5 - The Veldt.scene.json"
?? "shows/scenes/deadmau5 - The Veldt.sprites.json"
10
```

```
$ cd "~/deadmau5 app"; KIT="tools/showkit"; W="$KIT/work/veldt"; date; python3 - <<'EOF'
W="tools/showkit/songs/veldt/"
s=open(W+"sprites.py").read()
if "veldt_low1" not in s:
    s=s.replace('# Torn frames:','''# Two eyes low in the dark, cat's slits following the jaw's own curve; they grow as he comes closer.
def low(r14,r15,r16):
    rows=[E17]*14+[r14,r15,r16]
    return rows
S["veldt_low1"]=low(E17,E17,"....XXX...XXX....")
S["veldt_low2"]=low(E17,"...X.........X...","...XXXX...XXXX...")
S["veldt_low3"]=low ... [cut]
Sat Oct 31 13:09:33 PDT 2026
wrote shows/scenes/deadmau5 - The Veldt.scene.json scenes 20 hits 86
deadmau5 - The Veldt: 22 scenes, 86 hits, written into shows/deadmau5 - The Veldt.json
tools/showkit/songs/veldt/big5.png (2000, 812)
```

You've hit your session limit · resets 5:10pm (America/Los_Angeles)
