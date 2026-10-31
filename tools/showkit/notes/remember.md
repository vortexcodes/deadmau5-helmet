# What the remember builder ran and saw

Commands and their text output, in order, with long output cut. Images are left out; rerun the tools to see them. Cut off partway: the generator and treatment in the repo are the latest state.

I'll start by reading the brief.

```
$ date; cat "tools/showkit/BRIEF.md"; ls -la "tools/showkit"
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
$ cd "~/deadmau5 app"; KIT=tools/showkit; mkdir -p "$KIT/work/remember"; cat "(scratch)/tiki/write_treatment.py"; echo ------; cat "$KIT/fmt.py"; echo -----; cat "$KIT/grid.py"; echo ----; cat "$KIT/sheet.py"; echo ---; cat "$KIT/songmap.py"; echo ---; cat "$KIT/spectro.py"; echo ---; cat "$KIT/spritetry.py"; ls -la shows | head -60; ls -la shows/scenes | head -60
<persisted-output>
Output too large (38.1KB). Full output saved to: ~/.claude/projects/-Users-jones-deadmau5-app/208332e7-8c9f-4c25-bc21-e9a9df98fa1f/tool-results/bajqc47u2.txt

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
$ cd "~/deadmau5 app"; ls -la "shows/Kaskade feat. deadmau5 - I Remember"* 2>/dev/null; ls shows/scenes | grep -i remember; wc -c "shows/scenes/TIKI TIKI - Slowed.scene.json"; cat "shows/scenes/TIKI TIKI - Slowed.scene.json" | head -c 9000; which ffprobe ffmpeg; ffprobe -hide_banner "shows/Kaskade feat. deadmau5 - I Remember.mp3" 2>&1 | tail -8
-rw-r--r--@ 1 jones  staff  5664436 Oct 31 12:37 shows/Kaskade feat. deadmau5 - I Remember.mp3
   19578 shows/scenes/TIKI TIKI - Slowed.scene.json
{
"v":1,
"show":"TIKI TIKI - Slowed",
"about":"Bars of a measured grid, shows/scenes/TIKI TIKI - Slowed.beats: bar b starts at 1.796 + 1.739 b seconds (137.98 BPM), 183 bars, and at bar 119.5 the track is spliced, so the music comes back 197 ms late and the grid holds still for it. Everything from there is the song's opening again, bar for bar. The bar line is where the phrases turn, with the kick on 1 and 3 and the clap on 2 and 4 with a flick on the and of 2. A night on the island. Torches get lit one tube at a time; the hooks are fire climbing the shell with the ears burning as torches, the kick on the rims and the clap up the tubes. Every breakdown goes out to the lagoon, cold water and moon glints, with one stopped bar of almost nothing, and the title crosses the face once, in the first. The verses are bamboo: upright stalks swaying on the face, the two sides stomping in turn. The big sections wake the idol, a carved mask drawn to fit the LEDs that exist: brow and eyes on the dome, teeth along the jaw, since the middle of the face has no LEDs. It burns in torch colours the first time, at sunset the second, and half fire, half water the third, swapping sides. The song then starts over, so the show does too, and the last big section has everything, with white once. At the end the torches go out one tube at a time and the idol is last to go. Shell layers are kept near the shell's 300 mA and nothing on it pulses faster than a beat.",
"lead":0,
"marks":{"hush": 2, "light": 3, "hook": 5, "hookb": 9, "dip": 13, "climb": 14, "hook2": 15, "burn": 21, "water": 25, "stop": 26, "still": 27, "swell": 30, "verse": 31, "vlow": 37, "vri
... [cut] ...
": [0.14, 0.04], "hi": 0.35}]},
  {"name": "still", "from": "still", "to": "swell", "pal": "lagoon", "layers": [{"use": "water"}, {"use": "glint"}, {"use": "tide"}]},
  {"name": "swell", "from": "swell", "to": "verse", "pal": "lagoon", "o/opt/homebrew/bin/ffprobe
/opt/homebrew/bin/ffmpeg
Input #0, mp3, from 'shows/Kaskade feat. deadmau5 - I Remember.mp3':
  Metadata:
    encoder         : Lavf58.20.100
  Duration: 00:04:43.14, start: 0.025057, bitrate: 160 kb/s
  Stream #0:0: Audio: mp3 (mp3float), 44100 Hz, stereo, fltp, 160 kb/s, start 0.025057
    Metadata:
      encoder         : Lavc58.35
```

```
$ cd "~/deadmau5 app"; KIT=tools/showkit; mkdir -p "$KIT/work/remember"; cat "(scratch)/tiki/write_treatment.py"; echo ------; cat "$KIT/fmt.py"; echo -----; cat "$KIT/grid.py"; echo ----; cat "$KIT/sheet.py"; echo ---; cat "$KIT/songmap.py"; echo ---; cat "$KIT/spectro.py"; echo ---; cat "$KIT/spritetry.py"; ls -la shows | head -60; ls -la shows/scenes | head -60
<persisted-output>
Output too large (38.1KB). Full output saved to: ~/.claude/projects/-Users-jones-deadmau5-app/208332e7-8c9f-4c25-bc21-e9a9df98fa1f/tool-results/bajqc47u2.txt

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
$ cd "~/deadmau5 app"; ls -la "shows/Kaskade feat. deadmau5 - I Remember"* 2>/dev/null; ls shows/scenes | grep -i remember; wc -c "shows/scenes/TIKI TIKI - Slowed.scene.json"; cat "shows/scenes/TIKI TIKI - Slowed.scene.json" | head -c 9000; which ffprobe ffmpeg; ffprobe -hide_banner "shows/Kaskade feat. deadmau5 - I Remember.mp3" 2>&1 | tail -8
-rw-r--r--@ 1 jones  staff  5664436 Oct 31 12:37 shows/Kaskade feat. deadmau5 - I Remember.mp3
   19578 shows/scenes/TIKI TIKI - Slowed.scene.json
{
"v":1,
"show":"TIKI TIKI - Slowed",
"about":"Bars of a measured grid, shows/scenes/TIKI TIKI - Slowed.beats: bar b starts at 1.796 + 1.739 b seconds (137.98 BPM), 183 bars, and at bar 119.5 the track is spliced, so the music comes back 197 ms late and the grid holds still for it. Everything from there is the song's opening again, bar for bar. The bar line is where the phrases turn, with the kick on 1 and 3 and the clap on 2 and 4 with a flick on the and of 2. A night on the island. Torches get lit one tube at a time; the hooks are fire climbing the shell with the ears burning as torches, the kick on the rims and the clap up the tubes. Every breakdown goes out to the lagoon, cold water and moon glints, with one stopped bar of almost nothing, and the title crosses the face once, in the first. The verses are bamboo: upright stalks swaying on the face, the two sides stomping in turn. The big sections wake the idol, a carved mask drawn to fit the LEDs that exist: brow and eyes on the dome, teeth along the jaw, since the middle of the face has no LEDs. It burns in torch colours the first time, at sunset the second, and half fire, half water the third, swapping sides. The song then starts over, so the show does too, and the last big section has everything, with white once. At the end the torches go out one tube at a time and the idol is last to go. Shell layers are kept near the shell's 300 mA and nothing on it pulses faster than a beat.",
"lead":0,
"marks":{"hush": 2, "light": 3, "hook": 5, "hookb": 9, "dip": 13, "climb": 14, "hook2": 15, "burn": 21, "water": 25, "stop": 26, "still": 27, "swell": 30, "verse": 31, "vlow": 37, "vri
... [cut] ...
": [0.14, 0.04], "hi": 0.35}]},
  {"name": "still", "from": "still", "to": "swell", "pal": "lagoon", "layers": [{"use": "water"}, {"use": "glint"}, {"use": "tide"}]},
  {"name": "swell", "from": "swell", "to": "verse", "pal": "lagoon", "o/opt/homebrew/bin/ffprobe
/opt/homebrew/bin/ffmpeg
Input #0, mp3, from 'shows/Kaskade feat. deadmau5 - I Remember.mp3':
  Metadata:
    encoder         : Lavf58.20.100
  Duration: 00:04:43.14, start: 0.025057, bitrate: 160 kb/s
  Stream #0:0: Audio: mp3 (mp3float), 44100 Hz, stereo, fltp, 160 kb/s, start 0.025057
    Metadata:
      encoder         : Lavc58.35
```

Now I'll measure the grid.

```
$ cd "~/deadmau5 app"; KIT=tools/showkit; date; time python3 $KIT/grid.py scan "shows/Kaskade feat. deadmau5 - I Remember.mp3" 2>&1 | tail -20
Sat Oct 31 12:39:17 PDT 2026
estimator: 128.000 BPM, first bar 1.590 s, tempo lock 0.776, bar lock 0.6695951034694072; song 283.1 s
refined over the whole song: spb 0.468751 = 128.000 BPM
first half 128.000 BPM, second half 128.012 BPM (these should agree within 0.05)
phase of the music against that grid per 8 bars, ms (flat = right; one 16th = 117 ms; contrast under 1.15 means sparse, ignore it):
  0:+3(1.65)  8:+3(4.33)  16:-3(2.19)  24:-3(2.97)  32:-3(3.14)  40:-3(3.34)  48:+1(3.08)  56:+1(3.39)  64:+3(1.83)  72:+1(1.20)  80:+5(1.84)  88:+5(2.46)  96:+3(2.92)  104:-1(3.05)  112:-1(2.95)  120:-1(3.17)  128:-1(2.78)  136:-5(3.17)  144:+35(1.17)
change per beat position, estimator's bar 1 at 1.590 s: 0:1.09 1:0.92 2:1.06 3:1.09  (the highest is where bars really start, 0 = estimator is right)
strongest phrase positions, in beats mod 32 from that bar 1: 24(2.06), 8(1.97), 7(1.66), 23(1.63), 2(1.59), 18(1.47)
biggest single changes (time, beat from bar 1, beat mod 4): 12.8s b24 m0; 35.3s b72 m0; 50.3s b104 m0; 130.0s b274 m2; 132.4s b279 m3; 132.8s b280 m0; 137.1s b289 m1; 137.5s b290 m2; 139.9s b295 m3; 140.3s b296 m0; 145.0s b306 m2; 146.9s b310 m2; 147.4s b311 m3; 147.8s b312 m0; 155.3s b328 m0; 155.8s b329 m1; 160.0s b338 m2; 162.8s b344 m0; 163.3s b345 m1; 199.9s b423 m3; 200.3s b424 m0; 207.8s b440 m0; 214.9s b455 m3; 222.8s b472 m0
suggested next: grid.py fold with --spb 0.468751 --anchor 1.590, decide the bar line, then grid.py write
python3 $KIT/grid.py scan "shows/Kaskade feat. deadmau5 - I Remember.mp3" 2>&  1.60s user 0.49s system 123% cpu 1.690 total
tail -20  0.00s user 0.00s system 0% cpu 1.690 total
```

```
$ cd "~/deadmau5 app"; KIT=tools/showkit; python3 $KIT/grid.py fold "shows/Kaskade feat. deadmau5 - I Remember.mp3" --spb 0.46875 --anchor 1.590 2>&1 | head -120
bar 0 at 1.590 s, 128.000 BPM, 150 bars
bars 0-16   (16 steps, | every beat; one row per band)
   sub     #-=-|=:::|- :.|: @:   peak 0.24
   bass    @--:|=--:|+:*:|*:@-   peak 0.30
   lowmid  @:*-|+:+-|*-#:|#:%-   peak 0.25
   mid     @=*:|+=*-|+-*=|*:@-   peak 0.20
   pres    %:+-|+:*:|#:*-|#:@-   peak 0.26
   air     %.*.|*.#:|#:%.|@.@.   peak 0.27
bars 16-32   (16 steps, | every beat; one row per band)
   sub     @.--|@ =-|@ +-|@ =:   peak 0.42
   bass    %:-.|%--.|%.+.|@:+.   peak 0.66
   lowmid  *:*.|*.*.|#.%.|%:@:   peak 0.50
   mid     @.+.|%.+ |@ #.|%.*.   peak 0.69
   pres    %.: |% - |@.-.|*.=.   peak 0.67
   air     #.- |* +.|@.=.|# *.   peak 0.69
bars 32-48   (16 steps, | every beat; one row per band)
   sub     # =:|@ =:|@ -:|@ =:   peak 0.47
   bass    @:-:|@--.|%:=.|@:+.   peak 0.67
   lowmid  #-#.|+-#:|#-%.|%-@:   peak 0.40
   mid     @.+.|%.# |@.@ |%.%    peak 0.65
   pres    @.+.|% % |@ % |%.*    peak 0.71
   air     % *-|# %:|@ %-|*:#:   peak 0.79
bars 48-64   (16 steps, | every beat; one row per band)
   sub     % ::|@ ::|@ ::|@ ::   peak 0.53
   bass    %:-.|@--.|@-=.|@:=.   peak 0.64
   lowmid  #+#.|+=*-|+=@.|*-@-   peak 0.28
   mid     @:@ |@:@.|@:@.|@:@.   peak 0.34
   pres    %.@.|@.@ |#.@.|% @    peak 0.54
   air     % @-|% @:|%.%-|# @.   peak 0.66
bars 64-80   (16 steps, | every beat; one row per band)
   sub     @-:-|+-::|+...|=.%-   peak 0.20
   bass    @---|+-:-|=.=:|=:@-   peak 0.30
   lowmid  @**-|*+==|+=**|%-%-   peak 0.21
   mid     +++=|#++=|*-@+|%-@*   peak 0.17
   pres    +-=:|+:+:|+:*-|%-@=   peak 0.22
   air     *:*-|*:#-|*-@-|%:@-   peak 0.22
bars 80-96   (16 steps, | every beat; one row per band)
   sub     @#**|=*%*|*##%|**#*   peak 0.11
   bass    @+#*|#=*=|@=#=|%=@*   peak 0.18
   lowmid  @=+-|#-%=|+=*=|*-@-   peak 0.22
   mid
... [cut] ...
ry beat; one row per band)
   sub     %.::|@  :|% ::|* ::   peak 0.47
   bass    @::.|@:::|@.-.|@:=:   peak 0.61
   lowmid  @=*:|#-#-|%-*:|@-@-   peak 0.33
   mid     @.=.|%:+.|%.#.|@.+.   peak 0.50
   pres    % -.|# # |% + |@ =    peak 0.70
   air     @ *:|# *.|@ #.|@ *.   peak 0.67
bars 144-150   (16 steps, | every beat; one row per band)
   sub     @%%@|@+-.|:::.| .::   peak 0.01
   bass    #=+%|@#--|--:-|. ::   peak 0.03
   lowmid  **@=|#=#=|**-=|-.@+   peak 0.05
   mid     +#@#|-*=*|**+#|. +-   peak 0.04
   pres    =+-@|%#=#|::**|-+*+   peak 0.03
   air     =-*=|:-+@|..==|=-=-   peak 0.02
```

```
$ cd "~/deadmau5 app"; KIT=tools/showkit; B="Kaskade feat. deadmau5 - I Remember"; time python3 $KIT/grid.py write "$B" --spb 0.46875 --anchor 1.590 2>&1 | tail -15; python3 $KIT/grid.py check "$B" 2>&1 | tail -5; python3 $KIT/songmap.py "$B" | tail -160; python3 mau5scene.py bars "$B" 2>&1 | head -40
    1:31.59-1:39.09  lvl3  split      {'shell': 'fire', 'ears': 'pinwheel'}
    1:39.09-1:46.59  lvl3  police     {'hz': 8.533}
    1:46.59-1:54.09  lvl3  pinwheel   {'period': 1.2}
    1:54.09-2:01.59  lvl3  confetti   {'rate': 26.0}
    2:01.59-2:31.59  lvl0  tubepulse  {'period': 7.5}
    2:31.59-2:54.09  lvl0  breathe    {'period': 8.0}
    2:54.09-3:09.09  lvl1  eq         {}
    3:09.09-3:24.09  lvl1  comet      {'period': 4.0}
    3:24.09-3:39.09  lvl1  wipe       {'period': 3.75, 'a': (0, 180, 255), 'b': (120, 0, 255)}
    3:39.09-3:54.09  lvl1  chase      {'period': 2.2}
    3:54.09-4:01.59  lvl1  sparkle    {}
    4:01.59-4:16.59  lvl1  matrix     {}
    4:16.59-4:31.59  lvl1  scanner    {'period': 3.75}
    4:31.59-4:42.84  lvl1  gradient   {'period': 3.75, 'a': (255, 40, 0), 'b': (255, 150, 0)}
wrote shows/scenes/Kaskade feat. deadmau5 - I Remember.beats: 601 beats, 150 bars, bar 0 at 1.590 s, 128.000 BPM
python3 $KIT/grid.py write "$B" --spb 0.46875 --anchor 1.590 2>&1  0.68s user 0.12s system 95% cpu 0.836 total
tail -15  0.00s user 0.00s system 0% cpu 0.836 total
Kaskade feat. deadmau5 - I Remember: 128.000 BPM, 151 bars, bar 0 at 1.590 s, holds []
music against the grid per 8 bars, ms (contrast): 0:+5(1.64)  8:+3(4.31)  16:-1(2.20)  24:-3(2.98)  32:-1(3.07)  40:-1(3.41)  48:-1(3.11)  56:-1(3.36)  64:-1(1.84)  72:-1(1.20)  80:+5(1.80)  88:+5(2.47)  96:+5(2.84)  104:-1(3.15)  112:-1(3.11)  120:+3(3.24)  128:+1(2.85)  136:-1(2.95)  144:+37(1.17)
worst 37 ms where the music is clear enough to say, mean +3.1 ms
Kaskade feat. deadmau5 - I Remember: 151 bars, 1.88 s a bar, 283.1 s
 bar     t   E  B  M  H  notes       change
   0    1.6   0  3  2  2  F# C G      
   1    3.5   5  6  7  7  F# C G      >>
   2    5.3   7  7  7  7  C F# A      
   3    7.2   7  7  
... [cut] ...
0  0  0  F# A D      
 148  279.1   0  0  0  0  F# A D      
 149  281.0   0  0  0  0  A G D       
 150  282.8   0  0  0  0  C C# D      
Traceback (most recent call last):
  File "mau5scene.py", line 1344, in <module>
    sys.exit(main())
  File "mau5scene.py", line 1326, in main
    _, music, _ = _show_and_music(names([a.show])[0])
  File "mau5scene.py", line 558, in _show_and_music
    with open(path) as f:
FileNotFoundError: [Errno 2] No such file or directory: 'shows/Kaskade feat.json'
```

```
$ cd "~/deadmau5 app"; grep -n "def names" -A14 mau5scene.py; sed -n 545,575p mau5scene.py; sed -n 1290,1344p mau5scene.py; grep -n "splitext\|\.rsplit\|\.stem" mau5scene.py mau5show.py mau5song.py mau5offline.py | head -30
1318:    def names(given):
1319-        if given:
1320-            return [os.path.splitext(os.path.basename(g))[0].replace(".scene", "")
1321-                    for g in given]
1322-        return sorted(f[:-len(".scene.json")] for f in os.listdir(SCENES)
1323-                      if f.endswith(".scene.json"))
1324-
1325-    if a.cmd == "bars":
1326-        _, music, _ = _show_and_music(names([a.show])[0])
1327-        rows = bar_stats(music)
1328-        lo = a.lo if a.lo is not None else 0
1329-        hi = a.hi if a.hi is not None else len(rows)
1330-        for r in rows[lo:hi]:
1331-            print(_row(r))
1332-    elif a.cmd == "compile":
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
        for name in order:
            d = per[name]
            print("  %-12s %7.1fs %8.0f %8.0f %7.1f%% %9.1
... [cut] ...
ps)
    return 0


if __name__ == "__main__":
    sys.exit(main())
mau5scene.py:1320:            return [os.path.splitext(os.path.basename(g))[0].replace(".scene", "")
mau5song.py:87:    out = os.path.join(cache_dir, os.path.splitext(os.path.basename(path))[0] + ".wav")
mau5song.py:646:        title = os.path.splitext(os.path.basename(path))[0]
mau5show.py:130:                             os.path.splitext(os.path.basename(path))[0] + ".beats")
mau5show.py:491:    base = os.path.splitext(os.path.basename(track))[0]
mau5show.py:869:    out = out or os.path.splitext(show_path)[0] + "_preview.mp4"
```

```
$ cd "~/deadmau5 app"; KIT=tools/showkit; W=$KIT/work/remember; B="Kaskade feat. deadmau5 - I Remember"; python3 mau5scene.py bars "$B.scene.json" 2>&1 | head -5; python3 $KIT/spectro.py "$B" $W/whole.png; python3 $KIT/spectro.py "$B" $W/a.png 0 40; python3 $KIT/spectro.py "$B" $W/b.png 40 80;python3 $KIT/spectro.py "$B" $W/c.png 80 120;python3 $KIT/spectro.py "$B" $W/d.png 120 151
     0     1.59s  energy 0.02  bass 0.28 (punch 0.65)  mid 0.24  high 0.25
     1     3.46s  energy 0.48  bass 0.63 (punch 0.87)  mid 0.76  high 0.69
     2     5.34s  energy 0.67  bass 0.68 (punch 1.00)  mid 0.79  high 0.71
     3     7.21s  energy 0.68  bass 0.65 (punch 1.00)  mid 0.82  high 0.48
     4     9.09s  energy 0.59  bass 0.63 (punch 0.34)  mid 0.79  high 0.33
tools/showkit/songs/remember/whole.png
tools/showkit/songs/remember/a.png
tools/showkit/songs/remember/b.png
tools/showkit/songs/remember/c.png
tools/showkit/songs/remember/d.png
```

```
$ mkdir -p tools/showkit/songs/remember; cat > tools/showkit/songs/remember/beatnotes.py <<'EOF'
import subprocess, sys, numpy as np
mp3="shows/Kaskade feat. deadmau5 - I Remember.mp3"
SR=22050
raw=subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-i",mp3,"-ac","1","-ar",str(SR),"-f","f32le","-"],capture_output=True,check=True).stdout
m=np.frombuffer(raw,dtype=np.float32)
t0=1.590; spb=0.46875
N=8192
f=np.fft.rfftfreq(N,1/SR)
win=np.hanning(N)
NOTES="C C# D D# E F F# G G# A A# B".split()
def midi(fr): return 69+ ... [cut]
bar.beat  time  bass(40-160)  mid-top(200-1000) high(1000-3000) rmsDb
  0.1    1.59  B1      F#5 D#4 F#4            E6 D#6           -38
  0.2    2.06  B1      F#5 D#4 F#4            D#6 E6           -32
  0.3    2.53  B2      F#4 F#5 D#4            C#6 E6           -25
  0.4    3.00  B2      F#4 D#4 F#5            C#6 E6           -22
  1.1    3.46  B1      D#4 F#4 F#5            E6 D#6           -19
  1.2    3.93  B1      F#5 D#4 F#4            E6 C#6           -17
  1.3    4.40  B1      D#4 F#4 F#5            C#6 E6           -15
  1.4    4.87  B1      F#4 D#4 F#5            D#6 E6           -14
  2.1    5.34  B2      D#4 F#4 B3             C#6 F#6          -10
  2.2    5.81  B2      F#4 D#4 B3             C#6 D#6          -13
  2.3    6.28  B2      F#4 D#4 B3             C#6 F#6          -14
  2.4    6.75  D3      F#4 D#4 B3             C#6 E6           -14
  3.1    7.21  D3      C#4 A4 F#4             E6 C6            -13
  3.2    7.68  A2      F#4 A4 C#4             C#6 E6           -14
  3.3    8.15  A2      C#4 A4 F#5             C#6 D#6          -15
  3.4    8.62  G2      A4 F#4 B3              C#6 E6           -14
  4.1    9.09  G1      F#4 D4 B3              C#6 F#6          -12
  4.2    9.56  D3      F#4 B3 D4              C#6 D6           -13
  4.3   10.03  D3      F#4 B3 D4              C#6 A6           -13
  4.4   10.50  D3      F#4 F#5 D4             C#6 D6           -19
  5.1   10.96  D3      D4 F#5 F#4             C#6 D6           -19
  5.2   11.43  G2      F#4 D4 B3              C#6 D6           -21
  5.3   11.90  G2      F#4 D4 B3              C#6 A6           -21
  5.4   12.37  D3      F#4 D4 B3              C#6 F#6          -21
  6.1   12.84  F#2     F#4 C#5 C#4            F6 C#6           -11
  6.2   13.31  F#2     F#4 C#5 A#3            C#6 F#6  
... [cut] ...
3.4   46.12  A1      B3 C#4 D4              F7 F#7           -10
 24.1   46.59  A1      D4 B3 F#4              C#7 C6           -11
 24.2   47.06  A1      B3 F#4 D4              C#6 F#6          -11
 24.3   47.53  A1      B3 D4 F#4              F#6 C#6          -10
 24.4   48.00  A1      B3 F#5 F#4             F#6 C#7          -11
 25.1   48.47  A1      F#4 B3 D5              C#6 F#6          -11
 25.2   48.93  A1      F#4 B3 D5              C#6 F#6          -11
 25.3   49.40  A1      B3 F#4 D5              F#6 C#6          -10
 25.4   49.87  A1      F#4 B3 D5              F#6 C#6          -11
```

```
$ cd "~/deadmau5 app"; python3 tools/showkit/songs/remember/beatnotes.py 44 104 | awk 'NR==1 || /\.1 /'
bar.beat  time  bass(40-160)  mid-top(200-1000) high(1000-3000) rmsDb
 44.1   84.09  A1      D4 F#4 F#5             F#6 C#6           -8
 45.1   85.97  A1      D4 B3 F#5              F#6 C#6           -8
 46.1   87.84  F#2     C#4 F#4 F#5            G#6 C#6           -8
 47.1   89.72  A1      C#5 E4 C#4             C#6 C#7           -8
 48.1   91.59  A1      D5 D4 F#4              A6 D6             -7
 49.1   93.47  D3      D5 B3 F#4              A6 D6             -7
 50.1   95.34  A1      D#4 B4 B3              F#6 D#6           -8
 51.1   97.22  A1      A4 C#4 B5              A#6 F#6           -8
 52.1   99.09  A1      D4 B4 C5               F#6 G#6           -7
 53.1  100.97  A1      D4 B3 B5               F#6 C#6           -8
 54.1  102.84  F#2     A#4 F#4 C#4            F6 D7             -8
 55.1  104.72  A1      E4 C#4 A#5             C#6 E6            -9
 56.1  106.59  A1      B4 B3 D4               F#6 G#6           -7
 57.1  108.47  D3      B5 B3 F#4              F#6 A6            -8
 58.1  110.34  A1      B4 F#4 B3              F#6 D#6           -8
 59.1  112.22  A1      A4 B5 C#4              C#6 A#6           -8
 60.1  114.09  A1      B4 A4 B3               F#6 C#6           -9
 61.1  115.97  G#1     B3 F#4 B4              F#6 D6            -9
 62.1  117.84  A1      A#4 A#3 C#4            F6 G#6            -9
 63.1  119.72  A1      C#4 C#5 A3             C#6 A#6           -9
 64.1  121.59  G#1     F#4 B4 B3              F#6 C#6           -8
 65.1  123.47  A1      D4 F#4 B4              F#6 D6            -8
 66.1  125.34  B2      D#4 D#5 F#4            A#6 B6           -10
 67.1  127.22  D3      C#4 E4 A3              B6 D#7           -10
 68.1  129.09  G2      B3 D4 F#4              D#7 F7           -10
 69.1  130.97  D3      F#4 C#5 D4             D6 D#6   
... [cut] ...
5.1  179.72  D3      C#5 C#4 E4             C#6 C#7           -7
 96.1  181.59  G2      D5 D4 C#5              A6 D6             -8
 97.1  183.47  G1      D5 B3 F#4              A6 D6             -8
 98.1  185.34  G1      B4 F#4 B3              F#6 C#6           -8
 99.1  187.22  G1      B5 B4 F#4              F#6 A#6           -9
100.1  189.09  G1      B4 D4 F#4              F#6 B5            -9
101.1  190.97  G1      B3 B4 D4               F#6 A6            -9
102.1  192.84  B1      D#4 A4 F#4             D#7 E7            -9
103.1  194.72  A1      A4 C#4 A5              B6 A#6            -9
```

```
$ cat > tools/showkit/songs/remember/vocal.py <<'EOF'
# Where is the voice: a mid-minus-side harmonic spectrogram with bar lines, 200 Hz - 4 kHz.
import subprocess, sys, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.ndimage import median_filter
mp3="shows/Kaskade feat. deadmau5 - I Remember.mp3"
SR=22050
raw=subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-i",mp3,"-ac","2","-ar",str(SR),"-f","f32le","-"],capture_output=True,check=True).stdout
st=np.frombuffer(raw,dtype=np.float32).reshape(-1,2)
t0=1.590; spb=0.46875
lo,hi=int(sys.argv[1]),int(sys ... [cut]
Traceback (most recent call last):
  File "tools/showkit/songs/remember/vocal.py", line 5, in <module>
    from scipy.ndimage import median_filter
ModuleNotFoundError: No module named 'scipy'
Traceback (most recent call last):
  File "tools/showkit/songs/remember/vocal.py", line 5, in <module>
    from scipy.ndimage import median_filter
ModuleNotFoundError: No module named 'scipy'
Traceback (most recent call last):
  File "tools/showkit/songs/remember/vocal.py", line 5, in <module>
    from scipy.ndimage import median_filter
ModuleNotFoundError: No module named 'scipy'
Traceback (most recent call last):
  File "tools/showkit/songs/remember/vocal.py", line 5, in <module>
    from scipy.ndimage import median_filter
ModuleNotFoundError: No module named 'scipy'
Traceback (most recent call last):
  File "tools/showkit/songs/remember/vocal.py", line 5, in <module>
    from scipy.ndimage import median_filter
ModuleNotFoundError: No module named 'scipy'
Traceback (most recent call last):
  File "tools/showkit/songs/remember/vocal.py", line 5, in <module>
    from scipy.ndimage import median_filter
ModuleNotFoundError: No module named 'scipy'
Traceback (most recent call last):
  File "<string>", line 1, in <module>
ModuleNotFoundError: No module named 'scipy'
Sat Oct 31 12:41:23 PDT 2026
```

```
$ cd "~/deadmau5 app"; W=tools/showkit/songs/remember; python3 - <<EOF
import re
p="$W/vocal.py"
s=open(p).read()
s=s.replace("from scipy.ndimage import median_filter\n","""def median_filter(A,size):
    k=size[1]
    P=np.pad(A,((0,0),(k//2,k//2)),mode='edge')
    V=np.lib.stride_tricks.sliding_window_view(P,k,axis=1)
    return np.median(V,axis=2)
""")
open(p,"w").write(s)
EOF
python3 $W/vocal.py 0 26 $W/v0.png; python3 $W/vocal.py 26 52 $W/v1.png; python3 $W/vocal.py 52 78 $W/v2.png; python3 $W/vocal.py 78 104 $W/v3.png; python3 $W/vocal.py 104 130 $W/v4.png; python3 $W/vocal.py 124 148 $W/v5.p ... [cut]
tools/showkit/songs/remember/v0.png
tools/showkit/songs/remember/v1.png
tools/showkit/songs/remember/v2.png
tools/showkit/songs/remember/v3.png
tools/showkit/songs/remember/v4.png
tools/showkit/songs/remember/v5.png
Sat Oct 31 12:41:49 PDT 2026
```

```
$ cat > tools/showkit/songs/remember/glide.py <<'EOF'
# Voice finder: a sung line glides and wobbles off the semitone grid, a synth does not.
# For each 8th, the share of the 350-1800 Hz energy (centre channel) that sits more than 28 cents off the song's tuning,
# then a zoom picture with a pitch axis so glides can be seen.
import subprocess, sys, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
mp3="shows/Kaskade feat. deadmau5 - I Remember.mp3"
SR=22050
raw=subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-i",mp3,"-ac","2","-ar",str(SR),"-f","f32le","-"],capt ... [cut]
tuning offset (semitones) -0.015
median 0.14318894427578038
  0   1.6s  0.20 0.19 0.19 0.19  ###########
  1   3.5s  0.20 0.20 0.20 0.23  ############
  2   5.3s  0.13 0.14 0.13 0.14  ########
  3   7.2s  0.09 0.13 0.14 0.07  ######
  4   9.1s  0.07 0.07 0.11 0.13  #####
  5  11.0s  0.14 0.16 0.15 0.15  #########
  6  12.8s  0.06 0.06 0.08 0.07  ###
  7  14.7s  0.06 0.07 0.06 0.06  ###
  8  16.6s  0.08 0.10 0.10 0.11  ######
  9  18.5s  0.11 0.12 0.10 0.11  ######
 10  20.3s  0.11 0.10 0.12 0.09  ######
 11  22.2s  0.07 0.07 0.08 0.10  ####
 12  24.1s  0.07 0.08 0.13 0.12  ######
 13  26.0s  0.10 0.11 0.10 0.09  ######
 14  27.8s  0.07 0.07 0.09 0.09  ####
 15  29.7s  0.09 0.12 0.14 0.11  ######
 16  31.6s  0.11 0.12 0.10 0.11  ######
 17  33.5s  0.16 0.16 0.19 0.21  ##########
 18  35.3s  0.19 0.13 0.16 0.26  ###########
 19  37.2s  0.16 0.19 0.22 0.24  ############
 20  39.1s  0.22 0.20 0.27 0.28  ##############
 21  41.0s  0.31 0.34 0.34 0.32  ###################
 22  42.8s  0.28 0.18 0.21 0.28  ##############
 23  44.7s  0.25 0.27 0.27 0.26  ###############
 24  46.6s  0.28 0.28 0.28 0.24  ################
 25  48.5s  0.29 0.32 0.35 0.35  ###################
 26  50.3s  0.21 0.11 0.20 0.29  ############
 27  52.2s  0.21 0.30 0.25 0.29  ###############
 28  54.1s  0.25 0.25 0.24 0.27  ###############
 29  56.0s  0.29 0.36 0.33 0.34  ###################
 30  57.8s  0.30 0.24 0.28 0.29  ################
 31  59.7s  0.19 0.20 0.29 0.22  #############
 32  61.6s  0.28 0.22 0.27 0.25  ###############
 33  63.5s  0.28 0.32 0.33 0.32  ##################
 34  65.3s  0.16 0.40 0.19 0.34  ################
 35  67.2s  0.16 0.26 0.10 0.25  ###########
 36  69.1s  0.11 0.18 0.19 0.16  #########
 37  71.0s  0.25 0.24 0.22 0.18  #############
 38  72.8s  0.14 0.22 0.16 0.31  ######
... [cut] ...
 0.14 0.26 0.21 0.29  #############
137 258.5s  0.35 0.38 0.36 0.39  ######################
138 260.3s  0.18 0.18 0.24 0.26  ############
139 262.2s  0.18 0.18 0.21 0.22  ###########
140 264.1s  0.19 0.27 0.27 0.27  ###############
141 266.0s  0.31 0.28 0.13 0.19  #############
142 267.8s  0.12 0.05 0.06 0.09  ####
143 269.7s  0.11 0.13 0.13 0.07  ######
144 271.6s  0.07 0.07 0.10 0.14  #####
145 273.5s  0.09 0.12 0.15 0.13  #######
146 275.3s  0.14 0.15 0.14 0.15  ########
147 277.2s  0.16 0.14 0.14 0.14  ########
148 279.1s  0.13 0.15 0.16 0.29  ###########
149 281.0s  0.13 0.00 0.00 0.00  #
```

```
$ cat > tools/showkit/songs/remember/pitch.py <<'EOF'
import subprocess, sys, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
mp3="shows/Kaskade feat. deadmau5 - I Remember.mp3"
SR=22050
raw=subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-i",mp3,"-ac","2","-ar",str(SR),"-f","f32le","-"],capture_output=True,check=True).stdout
st=np.frombuffer(raw,dtype=np.float32).reshape(-1,2)
M=(st[:,0]+st[:,1])*0.5
t0=1.590; spb=0.46875
lo,hi,out=int(sys.argv[1]),int(sys.argv[2]),sys.argv[3]
a=t0+lo*4*spb;b=t0+hi*4*spb
seg=M[int(max(a,0)*SR):int(b*SR)]
N=4096;H=220
win=np. ... [cut]
tools/showkit/songs/remember/p0.png
tools/showkit/songs/remember/p1.png
tools/showkit/songs/remember/p2.png
tools/showkit/songs/remember/p3.png
tools/showkit/songs/remember/p4.png
tools/showkit/songs/remember/p5.png
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
$ cd "~/deadmau5 app"; sed -n 140,560p mau5scene.py
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
$ cd "~/deadmau5 app"; sed -n 140,560p mau5scene.py
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
```

```
$ cd "~/deadmau5 app"; sed -n 575,1000p mau5scene.py
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
                 os.path.relpath(path, HERE)))
    return spec


# ----------------------------------------------------------------------
# lint
# ----------------------------------------------------------------------
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
            raise Trea
... [cut] ...
------------
    def _mix(self, P, idx, v):
        acc = self.acc
        mix = P["mix"]
        if mix == 0:
            acc[idx] += v
        elif mix == 1:
            acc[idx] = np.maximum(acc[idx], v)
        else:
            sel = v.max(1) > 4
            acc[idx[sel]] = v[sel]

    def _render(self, P, B, bar, lb, span, p, music, tt):
        if P["gate"] is not None:
            pat, step, decay, floor = P["gate"]
            gate = _gate(lb, pat, step, decay, floor, self.HB)
        else:
            gate = 1.0
        ein = min(max(lb / P["ein"], 0.0), 1.0) if P["ein"] > 0 else 1.0
```

```
$ cd "~/deadmau5 app"; sed -n 1000,1290p mau5scene.py
        ein = min(max(lb / P["ein"], 0.0), 1.0) if P["ein"] > 0 else 1.0
        eout = min(max((span - lb) / P["eout"], 0.0), 1.0) if P["eout"] > 0 else 1.0
        G = P["gain"].at(p, bar, music, tt) * gate * ein * eout
        if G <= 0:
            return
        c0 = P["c"].at(p, bar, music, tt)
        fx, idx = P["fx"], P["idx"]
        val = lambda k: P[k].at(p, bar, music, tt)  # noqa: E731
        if fx == "fill":
            rgb = pal_lookup(*P["pal"][:2], c0)
            w = G * 1.0
            v = np.broadcast_to(w * rgb, (len(idx), 3))
            self._mix(P, idx, v)
        elif fx == "grad":
            scale, speed, ofs, warp = val("scale"), val("speed"), val("ofs"), val("warp")
            lo, hi = val("lo"), val("hi")
            x = P["a"] * scale + B * speed + ofs
            if warp != 0:
                wscale, wspeed = val("wscale"), val("wspeed")
                x = x + warp * np.sin(2 * math.pi * (P["a2"] * wscale + B * wspeed))
            f = np.mod(x, 1.0)
            wv = f if P["saw"] else 1 - np.abs(2 * f - 1)
            c = lo + (hi - lo) * wv
            rgb = _pal_vec(P["pal"], c)
            w = G * np.ones(len(idx))
            self._mix(P, idx, w[:, None] * rgb)
        elif fx == "sweep":
            speed = val("speed")
            if P["shape"] == 0:
                sh = p
            else:
                f = (lb * speed) % 1.0
                sh = f if P["shape"] == 1 else 1 - abs(2 * f - 1)
            a0, a1 = val("from"), val("to")
            pos = a0 + (a1 - a0) * sh
            d = P["a"] - pos
            if P["band"]:
                q = 1 - np.abs(d) / val("width")
                k = np.where(q > 0, q * q, 0.0)
            else:
                k = np.clip(0.5 - d / val("soft"), 0.0, 1.0)
            c = c0 + val("c
... [cut] ...
     d["heat"].append(th.get("full_pct", 0.0))
        d["allow"].append(th.get("allowance_w", float("inf")))
        d["ms"].append(ms)
    th = guard.thermal
    floor_w = (max(th.sustained_w - th.standby_w, 0.0) if th is not None else 0.0)
    pinned = [nm for nm in order
              if th is not None and min(per[nm]["allow"]) <= floor_w * 1.05]
    if verbose:
        print("%s: %d frames at %g fps through the guard" % (base, n, fps))
        print("  %-12s %8s %8s %8s %8s %9s %7s"
              % ("scene", "from", "mean mA", "p95 mA", "heat", "allow W", "ms"))
        for name in order:
```

```
$ cd "~/deadmau5 app"; sed -n 575,1000p mau5scene.py
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
                 os.path.relpath(path, HERE)))
    return spec


# ----------------------------------------------------------------------
# lint
# ----------------------------------------------------------------------
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
            raise Trea
... [cut] ...
------------
    def _mix(self, P, idx, v):
        acc = self.acc
        mix = P["mix"]
        if mix == 0:
            acc[idx] += v
        elif mix == 1:
            acc[idx] = np.maximum(acc[idx], v)
        else:
            sel = v.max(1) > 4
            acc[idx[sel]] = v[sel]

    def _render(self, P, B, bar, lb, span, p, music, tt):
        if P["gate"] is not None:
            pat, step, decay, floor = P["gate"]
            gate = _gate(lb, pat, step, decay, floor, self.HB)
        else:
            gate = 1.0
        ein = min(max(lb / P["ein"], 0.0), 1.0) if P["ein"] > 0 else 1.0
```

```
$ cd "~/deadmau5 app"; sed -n 1000,1290p mau5scene.py
        ein = min(max(lb / P["ein"], 0.0), 1.0) if P["ein"] > 0 else 1.0
        eout = min(max((span - lb) / P["eout"], 0.0), 1.0) if P["eout"] > 0 else 1.0
        G = P["gain"].at(p, bar, music, tt) * gate * ein * eout
        if G <= 0:
            return
        c0 = P["c"].at(p, bar, music, tt)
        fx, idx = P["fx"], P["idx"]
        val = lambda k: P[k].at(p, bar, music, tt)  # noqa: E731
        if fx == "fill":
            rgb = pal_lookup(*P["pal"][:2], c0)
            w = G * 1.0
            v = np.broadcast_to(w * rgb, (len(idx), 3))
            self._mix(P, idx, v)
        elif fx == "grad":
            scale, speed, ofs, warp = val("scale"), val("speed"), val("ofs"), val("warp")
            lo, hi = val("lo"), val("hi")
            x = P["a"] * scale + B * speed + ofs
            if warp != 0:
                wscale, wspeed = val("wscale"), val("wspeed")
                x = x + warp * np.sin(2 * math.pi * (P["a2"] * wscale + B * wspeed))
            f = np.mod(x, 1.0)
            wv = f if P["saw"] else 1 - np.abs(2 * f - 1)
            c = lo + (hi - lo) * wv
            rgb = _pal_vec(P["pal"], c)
            w = G * np.ones(len(idx))
            self._mix(P, idx, w[:, None] * rgb)
        elif fx == "sweep":
            speed = val("speed")
            if P["shape"] == 0:
                sh = p
            else:
                f = (lb * speed) % 1.0
                sh = f if P["shape"] == 1 else 1 - abs(2 * f - 1)
            a0, a1 = val("from"), val("to")
            pos = a0 + (a1 - a0) * sh
            d = P["a"] - pos
            if P["band"]:
                q = 1 - np.abs(d) / val("width")
                k = np.where(q > 0, q * q, 0.0)
            else:
                k = np.clip(0.5 - d / val("soft"), 0.0, 1.0)
            c = c0 + val("c
... [cut] ...
     d["heat"].append(th.get("full_pct", 0.0))
        d["allow"].append(th.get("allowance_w", float("inf")))
        d["ms"].append(ms)
    th = guard.thermal
    floor_w = (max(th.sustained_w - th.standby_w, 0.0) if th is not None else 0.0)
    pinned = [nm for nm in order
              if th is not None and min(per[nm]["allow"]) <= floor_w * 1.05]
    if verbose:
        print("%s: %d frames at %g fps through the guard" % (base, n, fps))
        print("  %-12s %8s %8s %8s %8s %9s %7s"
              % ("scene", "from", "mean mA", "p95 mA", "heat", "allow W", "ms"))
        for name in order:
```

```
$ cd "~/deadmau5 app"; grep -n "SPRITES\|sprites.json" mau5fx.py mau5engine.py mau5show.py mau5scene.py mau5offline.py | head -20; grep -n "class Sprite" -A70 mau5fx.py | head -130; python3 - <<'EOF'
import numpy as np, mau5engine as E
h=E.Helmet()
print("n",h.n,"shell",h.shell.sum(),"ears",h.ears.sum())
s=h.shell
print("shell px",h.px[s].min(),h.px[s].max(),"py",h.py[s].min(),h.py[s].max())
for nm,m in (("ear1",h.ear1),("ear2",h.ear2)):
    print(nm,"px",h.px[m].min(),h.px[m].max(),"py",h.py[m].min(),h.py[m].max())
    for t in range(3):
        k=m&(np.asarray(h.tube)==t)
        print("  tube",t,k.sum(),"px",round(h.px[k].mean()),"py",round(h.py[k].min()),round(h.py[k].max()))
   ... [cut]
mau5scene.py:640:    from mau5fx import SPRITES
mau5scene.py:726:                    if one not in SPRITES:
mau5fx.py:134:SPRITES = {
mau5fx.py:249:# Sprites a song brings with it: shows/scenes/<song>.sprites.json, {name: [rows]},
mau5fx.py:256:        sheets = sorted(f for f in os.listdir(d) if f.endswith(".sprites.json"))
mau5fx.py:266:                SPRITES[name] = list(rows)
mau5fx.py:275:    rows = SPRITES[name_or_rows] if isinstance(name_or_rows, str) else name_or_rows
mau5fx.py:989:    for name in sorted(SPRITES):
mau5engine.py:35:from mau5fx import FONT5x7, SPRITES
mau5engine.py:625:    rows = SPRITES[name]
mau5offline.py:73:    from mau5fx import FONT5x7, SPRITES
mau5offline.py:96:            "sprites": {k: list(v) for k, v in SPRITES.items()},
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
588-                 row_from_top=3, color=(255, 40, 0), **kw):
589-        super().__init__(helmet, color=color, **kw)
590-        self.bmps 
... [cut] ...
90    3 + 4 4 3 4 3 3 3 3 4 3 4 4 + 3  
   70    5 2 2 2 2 1 2 1 1 2 1 2 2 2 2 5  
   50  2 4 2 2 1 2 1 2 1 1 2 1 2 1 2 2 4 2
   30  3 3 2 2 1                 1 2 2 3 3
   10  5 2                             2 5
  -10                                     
  -30  1                                 1
  -50  3                                 3
  -70  3 6 1                         1 6 3
  -90    4 3 1                     1 3 4  
 -110    2 4 3 1                 1 3 4 2  
nel shell 0.0 1.0 nfa 0.16035751702193546 0.8399804407362015 er 0.03929154446196175 1.0 ea 0.004374306928113342 0.9891721577339918
```

```
$ cd "~/deadmau5 app"; KIT=tools/showkit; W=$KIT/work/remember; python3 $KIT/sheet.py "TIKI TIKI - Slowed" $W/tiki.png 2:embers 5:hook 15:hook2 26.5:stop 31:verse 39:big 45:idol 75:sunset 107:duel 153:final 170:wind 178:out 2>&1 | tail -16; sed -n 249,300p mau5fx.py; sed -n 615,680p mau5engine.py
bar 2       embers         shell max  17 mean   0.0   ears max  15 mean   2.1   embers
bar 5       hook           shell max 130 mean  13.3   ears max 224 mean  70.3   hook · LIT
bar 15      hook2          shell max 233 mean  24.3   ears max 224 mean  70.3   hook2 · HOOK 2
bar 26.5    stop           shell max 126 mean   2.0   ears max   0 mean   0.0   stop · TIKI TIKI
bar 31      verse          shell max 100 mean   9.2   ears max  98 mean  46.9   verse · VERSE
bar 39      big            shell max 130 mean  24.0   ears max 224 mean  77.0   big · IDOL
bar 45      idol           shell max  61 mean  22.9   ears max 153 mean  32.1   big
bar 75      sunset         shell max 130 mean  26.6   ears max 224 mean  72.1   sunset · SUNSET
bar 107     duel           shell max 130 mean  10.9   ears max 255 mean  78.6   duel · DUEL
bar 153     final          shell max 249 mean  94.1   ears max 235 mean  96.3   final · FINAL
bar 170     wind           shell max  41 mean  13.3   ears max  92 mean  24.2   wind
bar 178     out            shell max  17 mean   3.6   ears max  47 mean   1.6   out
tools/showkit/songs/remember/tiki.png (1800, 490)
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
    for fn in she
... [cut] ...
rr[:, None] + 0.5)) * row_w,
                     lc[None, :] - (cc[:, None] + 0.5))
        j = d.argmin(1)
        take = d[np.arange(len(rr)), j] <= reach
        lit[idx[j[take]]] = True
    return lit


class TextScroll(Preset):
    """Scrolling text across the face, laid out flat so it reads."""
    name = "text"
    # The band is where the LEDs actually are: below py~28 is the visor
    # cutout and there is nothing to light.  7 rows over 28..145 mm puts
    # one glyph row per strip pitch, which is the finest the hardware
    # can resolve -- about 14-20 columns across, so two or three
```

```
$ cat > tools/showkit/songs/remember/kick.py <<'EOF'
import subprocess, numpy as np
mp3="shows/Kaskade feat. deadmau5 - I Remember.mp3"
SR=22050
raw=subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-i",mp3,"-ac","1","-ar",str(SR),"-f","f32le","-"],capture_output=True,check=True).stdout
m=np.frombuffer(raw,dtype=np.float32)
t0=1.590; spb=0.46875
N=1024;H=128
win=np.hanning(N)
nf=(len(m)-N)//H
f=np.fft.rfftfreq(N,1/SR)
ml=(f>=30)&(f<110); mh=(f>=5000)&(f<11000); mm=(f>=300)&(f<2500)
E=np.zeros((nf,3))
for s in range(0,nf,5000):
    e=min(nf,s+5000)
    F=np.abs(np.fft.rfft(np.stack([m[i*H:i*H+N] fo ... [cut]
bar: per beat, kick = low energy right after the beat over low energy just before; digit is (ratio-1)*3 capped 9; '.' no kick
     then high-hat row on offbeats, then mid level
  0    1.6  ..1.  ....  low     7 mid   106 high  33.6
  1    3.5  1...  ....  low    27 mid   339 high 153.5
  2    5.3  3...  ....  low    47 mid   410 high 155.6
  3    7.2  0...  ....  low    45 mid   385 high  59.7
  4    9.1  ....  .o.o  low    34 mid   374 high  31.0
  5   11.0  .011  ..oo  low    11 mid   202 high  17.9
  6   12.8  9...  .ooo  low    74 mid   436 high  13.1
  7   14.7  ...2  oooo  low    37 mid   465 high  14.9
  8   16.6  ...1  oooo  low    50 mid   461 high  19.3
  9   18.5  429.  oooo  low    52 mid   420 high  28.9
 10   20.3  ....  oooo  low    67 mid   546 high  47.7
 11   22.2  ..11  oooo  low    57 mid   579 high  59.6
 12   24.1  ...1  oooo  low    57 mid   557 high  67.9
 13   26.0  1.21  oooo  low    29 mid   489 high  85.1
 14   27.8  9...  .ooo  low    60 mid   600 high 116.7
 15   29.7  ...1  o.oo  low    44 mid   637 high 133.0
 16   31.6  ....  o...  low    55 mid   610 high 141.5
 17   33.5  ....  ....  low     7 mid   560 high 232.5
 18   35.3  9110  ..oo  low   229 mid   422 high 287.1
 19   37.2  3332  .oo.  low   193 mid   373 high 242.3
 20   39.1  1111  .ooo  low   220 mid   256 high 144.6
 21   41.0  1121  oooo  low   219 mid   224 high  97.8
 22   42.8  1231  .o.o  low   194 mid   374 high 268.8
 23   44.7  5533  .ooo  low   181 mid   339 high 202.3
 24   46.6  1231  .ooo  low   203 mid   238 high 118.0
 25   48.5  1111  oooo  low   217 mid   208 high  74.7
 26   50.3  111.  .o..  low   217 mid   386 high 229.7
 27   52.2  7443  .ooo  low   187 mid   336 high 190.9
 28   54.1  1222  oooo  low   209 mid   270 high 115.0
 29   56.0  1121  oooo  low 
... [cut] ...
 256.6  4532  oooo  low   183 mid   238 high  72.9
137  258.5  2222  oooo  low   200 mid   153 high  76.9
138  260.3  2433  oooo  low   175 mid   181 high  63.9
139  262.2  7944  oooo  low   163 mid   200 high  66.0
140  264.1  4332  oooo  low   175 mid   190 high  68.2
141  266.0  3233  oooo  low   172 mid   323 high 110.6
142  267.8  ....  ....  low    40 mid   509 high 124.9
143  269.7  ....  ....  low    35 mid   345 high  45.8
144  271.6  ....  oooo  low    22 mid   255 high  15.7
145  273.5  ..0.  ....  low     2 mid    88 high   6.2
146  275.3  .0..  ....  low     0 mid    24 high   2.1
```

```
$ cd "~/deadmau5 app"; python3 - <<'EOF'
import numpy as np, mau5engine as E
h=E.Helmet()
s=h.shell
# nel vs py
for lo,hi in ((-115,-80),(-80,-40),(-40,0),(0,30),(30,60),(60,90),(90,120),(120,150),(150,170)):
    k=s&(h.py>=lo)&(h.py<hi)
    if k.any():
        print("py %4d..%4d n=%3d nel %.2f..%.2f er %.2f..%.2f nfa %.2f..%.2f u %.2f..%.2f"%(lo,hi,k.sum(),h.nel[k].min(),h.nel[k].max(),h.er[k].min(),h.er[k].max(),h.nfa[k].min(),h.nfa[k].max(),h.u[k].min(),h.u[k].max()))
for t in range(3):
    k=h.ear1&(np.asarray(h.tube)==t)
    a=h.along[k];i0=a.argmin();i1=a.argmax()
    print("ear1 tube",t,"along %.2f..%.2f"%(a.min(),a.max()),"at min (%.0f,%.0f)  at max (%.0f,%.0f)"%(h.px[k][i0] ... [cut]
py -115.. -80 n= 66 nel 0.00..0.10 er 0.80..1.00 nfa 0.19..0.81 u 0.00..1.00
py  -80.. -40 n= 20 nel 0.14..0.19 er 0.87..0.95 nfa 0.17..0.83 u 0.00..1.00
py  -40..   0 n=  8 nel 0.24..0.29 er 0.87..0.90 nfa 0.16..0.84 u 0.00..1.00
py    0..  30 n= 14 nel 0.38..0.43 er 0.71..0.83 nfa 0.16..0.84 u 0.00..1.00
py   30..  60 n= 22 nel 0.48..0.48 er 0.44..0.78 nfa 0.17..0.83 u 0.00..1.00
py   60..  90 n= 68 nel 0.52..0.57 er 0.04..0.76 nfa 0.17..0.83 u 0.00..1.00
py   90.. 120 n= 98 nel 0.62..0.71 er 0.16..0.71 nfa 0.19..0.81 u 0.00..1.00
py  120.. 150 n= 81 nel 0.76..0.86 er 0.34..0.64 nfa 0.24..0.76 u 0.00..0.91
py  150.. 170 n= 21 nel 0.90..1.00 er 0.47..0.58 nfa 0.32..0.67 u 0.80..1.00
ear1 tube 0 along 0.02..0.89 at min (-207,67)  at max (-348,216) er 0.50..0.86 ea 0.50..0.77
ear2 tube 0 along 0.05..0.92 at min (211,70)  at max (358,214) er 0.50..0.83 ea 0.73..1.00
ear1 tube 1 along 0.17..0.94 at min (-130,139)  at max (-310,303) er 0.03..0.71 ea 0.37..0.90
ear2 tube 1 along 0.15..0.97 at min (133,127)  at max (322,306) er 0.04..0.75 ea 0.07..0.70
ear1 tube 2 along 0.13..0.95 at min (-87,223)  at max (-237,349) er 0.49..0.78 ea 0.01..1.00
ear2 tube 2 along 0.09..0.95 at min (92,205)  at max (237,349) er 0.50..0.81 ea 0.24..0.51
rim1 along 0.0544 0.9904 er 0.9383901427964612 1.0 nel 0.4452693370165746 0.9452693370165746
ears nel 0.4425932320441989 0.9454419889502763 nfa 0.0 1.0
shell low er at px -22..22 py 61..76
shell high er at px -169..169 py -111..-37
55:        self.ear1 = np.array([r.startswith("ear1") for r in self.region])
56:        self.ear2 = np.array([r.startswith("ear2") for r in self.region])
57:        self.ears = self.ear1 | self.ear2
120:        self.ea = np.zeros(self.n)
121:        self.er = np.zeros(self.n)
122:        for _m in (self.shell, self.ear1
... [cut] ...
.abs(h.py - self.p["y"]) / 10.0, 0, 1)
            out += k[:, None] * np.array(self.p["color"])
        out[~h.shell] = 0
        return np.clip(out, 0, 255)


class Matrix(Preset):
    """Rain down every shell strip, and down all six ear tubes.

    A column used to be an arbitrary slice of azimuth; now it is a strip,
    and each strip is one channel of the print, so the rain runs down
    lines that are really there.  The bright head leads and the trail
    follows -- it was the other way round, which read as a curtain.  And
    the ears were simply off for all of it, in what is the shows'
```

```
$ cd "~/deadmau5 app"; KIT=tools/showkit; W=$KIT/work/remember; B="Kaskade feat. deadmau5 - I Remember"; cat > "shows/scenes/$B.sprites.json" <<'EOF'
{
"remember_heart": [
 ".##...##.",
 "####.####",
 "#########",
 "#########",
 ".#######.",
 "..#####..",
 "...###...",
 "....#...."],
"remember_bigheart": [
 "..####...####..",
 ".######.######.",
 "###############",
 "###############",
 "###############",
 ".#############.",
 ".#############.",
 "..###########..",
 "...#########...",
 "....#######....",
 ".....#####.....",
 "......###......",
 ".......#......."],
"remember_shut": [
 "............. ... [cut]
tools/showkit/songs/remember/s1.png (1440, 338)
tools/showkit/songs/remember/s2.png (360, 338)
tools/showkit/songs/remember/s3.png (360, 338)
```

```
$ cd "~/deadmau5 app"; wc -l mau5power.py; grep -n "ceiling\|budget_ma\|burst_j\|sustained\|per_channel\|shell_max\|ma_per" mau5power.py | head -50; ls *.json | head; python3 - <<'EOF'
import mau5power, json
g=mau5power.load(count=621)
print({k:getattr(g,k) for k in dir(g) if not k.startswith('_') and isinstance(getattr(g,k),(int,float,str,bool))})
th=g.thermal
print({k:getattr(th,k) for k in dir(th) if not k.startswith('_') and isinstance(getattr(th,k),(int,float,str,bool))})
EOF
     513 mau5power.py
15:brightness number cannot express that; a ceiling per region can.
24:  ceiling   a per-LED cap by region, so the shell can never be driven
64:    Two numbers, because they answer different questions.  ``ceiling``
66:    ``budget_ma`` is for the span as a whole: how much current may all
72:    def __init__(self, name, lo, hi, ceiling, budget_ma, shed=1.0, floor=0.0):
74:        self.ceiling = int(ceiling)        # 0-255, per channel, per LED
75:        self.budget_ma = float(budget_ma)  # for the whole span
92:        return self.n * MA_PER_LED_FULL_WHITE * self.ceiling / 255.0
95:        return ("Region(%s %d..%d ceiling=%d budget=%.0fmA shed=%.1f)"
96:                % (self.name, self.lo, self.hi, self.ceiling,
97:                   self.budget_ma, self.shed))
111:    size `burst_j`, which is its thermal mass in the only unit that
113:    the bucket fills, the allowance falls towards `sustained_w` -- not
118:    run it, feel the helmet, and move `sustained_w` until a long set
129:    def __init__(self, sustained_w=11.0, burst_j=900.0, max_w=None,
131:        self.sustained_w = float(sustained_w)
132:        self.burst_j = float(burst_j)
141:        head = 1.0 - self.level / max(self.burst_j, 1e-6)
143:        sustained_led = max(self.sustained_w - self.standby_w, 0.0)
144:        top = (self.max_w - self.standby_w) if self.max_w else sustained_led
145:        return sustained_led + max(top - sustained_led, 0.0) * k
162:        self.level += (total - self.sustained_w) * dt
163:        self.level = min(max(self.level, 0.0), self.burst_j)
167:        return {"level_j": round(self.level, 1), "burst_j": self.burst_j,
168:                "full_pct": round(100.0 * self.level / max(self.burst_j, 1e-6), 1),
170:                "sustained_w": self.sustai
... [cut] ...
h is below both v and the ceiling for every v, so it can
293:        after_ceiling = self.frame_ma(out)
303:            if ma > r.budget_ma and ma > 0:
304:                seg *= r.budget_ma / ma
309:        # The per-frame budget is a ceiling; this is the rolling one.  It
312:        budget = self.budget_ma
348:        # top of the soft ceiling, for 2-6% of their current.  A rate per
(eval):1: no matches found: *.json
{'budget_ma': 1000.0, 'count': 621, 'default_ceiling': 32, 'link_ma': 0.0}
{'burst_j': 3000.0, 'level': 0.0, 'max_w': 25.5, 'ramp': 0.3, 'standby_w': 7.452, 'sustained_w': 11.0}
```

```
$ cd "~/deadmau5 app"; KIT=tools/showkit; W=$KIT/work/remember; B="Kaskade feat. deadmau5 - I Remember"; python3 $W/write_treatment.py && python3 mau5scene.py compile "$B.scene.json" 2>&1 | grep -v "^  *[0-9]\+ \|bar [0-9]" | tail -20; date; python3 $KIT/sheet.py "$B" $W/d1.png 1:develop 3:photo 5.5:dim 6:rose 8:rose 10:lav 12:lav 15:climb 16.5:climb 17.5:inhale 18:dawn 18.25:gap 20:dawn 22:morn 24:morn 30.5:morn 35.5:line 36:line 37:line 40:line 48:hook 48.5:long 49:long 52:hook 56:hook 60:hook 66:fall 68:fall 69.5:rest 70:left 71.5:left 73.5:rest 74:right 78:both 81.5:rest3 82:blue 84:blue 88:b ... [cut]
wrote shows/scenes/Kaskade feat. deadmau5 - I Remember.scene.json scenes 28 hits 39
Kaskade feat. deadmau5 - I Remember: marks against the bar map (bar-1, bar, bar+1)
Kaskade feat. deadmau5 - I Remember: 30 scenes, 39 hits, written into shows/Kaskade feat. deadmau5 - I Remember.json
Sat Oct 31 12:52:50 PDT 2026
bar 1       develop        shell max  29 mean   3.3   ears max  21 mean   4.3   develop
bar 3       photo          shell max 109 mean  16.5   ears max  30 mean   2.9   photo
bar 5.5     dim            shell max  81 mean  14.6   ears max  38 mean   9.0   dim
bar 6       rose           shell max  89 mean  19.3   ears max  76 mean   9.0   rose · ring 6
bar 8       rose           shell max 162 mean  29.0   ears max  75 mean  13.3   rose · ring 6
bar 10      lav            shell max  62 mean  26.0   ears max  89 mean  10.2   lav · ring 10
bar 12      lav            shell max  81 mean  32.7   ears max  82 mean  13.3   lav · ring 10
bar 15      climb          shell max 120 mean  40.7   ears max 102 mean  25.6   climb · ring 14
bar 16.5    climb          shell max 136 mean  49.5   ears max 104 mean  55.2   climb · ring 14
bar 17.5    inhale         shell max 100 mean  25.8   ears max 128 mean  90.6   inhale
bar 18      dawn           shell max  90 mean  19.1   ears max 159 mean  74.9   dawn · first light
bar 18.25   gap            shell max 148 mean  20.8   ears max 229 mean  76.1   dawn · first light
bar 20      dawn           shell max 104 mean  39.3   ears max 126 mean  31.7   dawn · first light
bar 22      morn           shell max 109 mean  31.6   ears max 140 mean  74.1   morning · ring 22
bar 24      morn           shell max 118 mean  36.6   ears max 124 mean  18.6   morning · ring 22
bar 30.5    morn           shell max 110 mean  34.2   ears max 140 mean  68.4   m
... [cut] ...
x  55 mean   8.0   yellow
bar 140     yellow         shell max 152 mean  23.0   ears max  50 mean   5.1   yellow
bar 143     last           shell max 194 mean  22.6   ears max  39 mean  14.3   last · last line
bar 145     last           shell max  84 mean  20.1   ears max   0 mean   0.0   last
bar 146.5   gone           shell max  84 mean  12.5   ears max   0 mean   0.0   gone
bar 147.5   gone           shell max  28 mean   4.2   ears max   0 mean   0.0   gone
tools/showkit/songs/remember/d1.png (1800, 2450)
```

```
$ cd "~/deadmau5 app"; KIT=tools/showkit; W=$KIT/work/remember; B="Kaskade feat. deadmau5 - I Remember"; python3 $W/write_treatment.py && python3 mau5scene.py compile "$B.scene.json" 2>&1 | grep -v "^  *[0-9]\+ \|bar [0-9]" | tail -20; date; python3 $KIT/sheet.py "$B" $W/d1.png 1:develop 3:photo 5.5:dim 6:rose 8:rose 10:lav 12:lav 15:climb 16.5:climb 17.5:inhale 18:dawn 18.25:gap 20:dawn 22:morn 24:morn 30.5:morn 35.5:line 36:line 37:line 40:line 48:hook 48.5:long 49:long 52:hook 56:hook 60:hook 66:fall 68:fall 69.5:rest 70:left 71.5:left 73.5:rest 74:right 78:both 81.5:rest3 82:blue 84:blue 88:b ... [cut]
wrote shows/scenes/Kaskade feat. deadmau5 - I Remember.scene.json scenes 28 hits 39
Kaskade feat. deadmau5 - I Remember: marks against the bar map (bar-1, bar, bar+1)
Kaskade feat. deadmau5 - I Remember: 30 scenes, 39 hits, written into shows/Kaskade feat. deadmau5 - I Remember.json
Sat Oct 31 12:52:50 PDT 2026
bar 1       develop        shell max  29 mean   3.3   ears max  21 mean   4.3   develop
bar 3       photo          shell max 109 mean  16.5   ears max  30 mean   2.9   photo
bar 5.5     dim            shell max  81 mean  14.6   ears max  38 mean   9.0   dim
bar 6       rose           shell max  89 mean  19.3   ears max  76 mean   9.0   rose · ring 6
bar 8       rose           shell max 162 mean  29.0   ears max  75 mean  13.3   rose · ring 6
bar 10      lav            shell max  62 mean  26.0   ears max  89 mean  10.2   lav · ring 10
bar 12      lav            shell max  81 mean  32.7   ears max  82 mean  13.3   lav · ring 10
bar 15      climb          shell max 120 mean  40.7   ears max 102 mean  25.6   climb · ring 14
bar 16.5    climb          shell max 136 mean  49.5   ears max 104 mean  55.2   climb · ring 14
bar 17.5    inhale         shell max 100 mean  25.8   ears max 128 mean  90.6   inhale
bar 18      dawn           shell max  90 mean  19.1   ears max 159 mean  74.9   dawn · first light
bar 18.25   gap            shell max 148 mean  20.8   ears max 229 mean  76.1   dawn · first light
bar 20      dawn           shell max 104 mean  39.3   ears max 126 mean  31.7   dawn · first light
bar 22      morn           shell max 109 mean  31.6   ears max 140 mean  74.1   morning · ring 22
bar 24      morn           shell max 118 mean  36.6   ears max 124 mean  18.6   morning · ring 22
bar 30.5    morn           shell max 110 mean  34.2   ears max 140 mean  68.4   m
... [cut] ...
x  55 mean   8.0   yellow
bar 140     yellow         shell max 152 mean  23.0   ears max  50 mean   5.1   yellow
bar 143     last           shell max 194 mean  22.6   ears max  39 mean  14.3   last · last line
bar 145     last           shell max  84 mean  20.1   ears max   0 mean   0.0   last
bar 146.5   gone           shell max  84 mean  12.5   ears max   0 mean   0.0   gone
bar 147.5   gone           shell max  28 mean   4.2   ears max   0 mean   0.0   gone
tools/showkit/songs/remember/d1.png (1800, 2450)
```

```
$ cd "~/deadmau5 app"; KIT=tools/showkit; W=$KIT/work/remember; B="Kaskade feat. deadmau5 - I Remember"; python3 - <<'EOF'
import json
p="shows/scenes/Kaskade feat. deadmau5 - I Remember.sprites.json"
d=json.load(open(p))
d["remember_shut3"]=[
 ".................",
 ".................",
 ".................",
 ".##.........##...",
 ".................",
]
d["remember_shut3"]=[
 ".................",
 ".................",
 ".................",
 "##...##...##...##",
 ".#####.....#####.",
 "..###.......###..",
 ".................",
 "................."]
d["remember_two"]=[
 "...##.....##...",
 "...##.. ... [cut]
tools/showkit/songs/remember/s4.png (1080, 338)
tools/showkit/songs/remember/s5.png (1080, 338)
ok
tools/showkit/songs/remember/d2.png (1800, 490)
```

```
$ cd "~/deadmau5 app"; KIT=tools/showkit; W=$KIT/work/remember; B="Kaskade feat. deadmau5 - I Remember"; python3 - <<'EOF'
import json
p="shows/scenes/Kaskade feat. deadmau5 - I Remember.sprites.json"
d={}
d["remember_heart"]=[
 ".##...##.",
 "####.####",
 "#########",
 "#########",
 ".#######.",
 "..#####..",
 "...###...",
 "....#...."]
d["remember_a"]=[
 "...##.....##...",
 "...##.....##...",
 "...............",
 "..####...####..",
 "..###########..",
 "..####...####..",
 "...##.....##...",
 "...#.#...#.#..."]
d["remember_b"]=[
 "....##...##....",
 "....##...##....",
 "...####.####...",
 "..### ... [cut]
tools/showkit/songs/remember/s6.png (1080, 338)
tools/showkit/songs/remember/s7.png (720, 338)
```

```
$ cd "~/deadmau5 app"; KIT=tools/showkit; W=$KIT/work/remember; B="Kaskade feat. deadmau5 - I Remember"; cat > "shows/scenes/$B.sprites.json" <<'EOF'
{
"remember_two": [
 "...##.....##...",
 "...##.....##...",
 "...............",
 "..####...####..",
 "..###########..",
 "..####...####..",
 "...##.....##...",
 "...#.#...#.#..."],
"remember_heart": [
 ".##...##.",
 "####.####",
 "#########",
 "#########",
 ".#######.",
 "..#####..",
 "...###...",
 "....#...."]
}
EOF
cat > $W/write_treatment.py <<'PYEOF'
#!/usr/bin/env python3
"""The treatment for Kaskade feat. deadmau5 - I Remember: MEMORY."""
impo ... [cut]
wrote shows/scenes/Kaskade feat. deadmau5 - I Remember.scene.json scenes 30 hits 39
Kaskade feat. deadmau5 - I Remember: marks against the bar map (bar-1, bar, bar+1)
Kaskade feat. deadmau5 - I Remember: 32 scenes, 39 hits, written into shows/Kaskade feat. deadmau5 - I Remember.json
Sat Oct 31 12:58:18 PDT 2026
tools/showkit/songs/remember/d3.png (1800, 1715)
```

```
$ cd "~/deadmau5 app"; KIT=tools/showkit; W=$KIT/work/remember; B="Kaskade feat. deadmau5 - I Remember"; python3 $KIT/sheet.py "$B" $W/d4.png 101.75:sing 102:SUN 102.25:gap 103:sun 104:sun 105:sun 106:sun 107:sun 108:sun 109:sun 110:high 111:high 112:high 114:melt 115:melt 116:melt 117:melt 118:day 120:day 122:day 124:day 126:peak 128:peak 130:peak 132:peak 134:yellow 136:yellow 138:yellow 140:yellow 141.5:yellow 142:last 143:last 144:last 145:last 146:gone 147:gone 2>&1 | tail -38; python3 mau5scene.py check "$B.scene.json" 2>&1 | tail -45; date
bar 101.75  sing           shell max  64 mean   7.8   ears max 138 mean  84.7   sing · I REMEMBER
bar 102     SUN            shell max  62 mean  10.9   ears max 161 mean  78.5   sunrise · sun
bar 102.25  gap            shell max 124 mean  12.9   ears max 223 mean  79.7   sunrise · sun
bar 103     sun            shell max 128 mean  28.0   ears max 185 mean  62.0   sunrise · sun · line 102
bar 104     sun            shell max 172 mean  44.1   ears max 144 mean  42.5   sunrise · sun · line 102
bar 105     sun            shell max  92 mean  34.4   ears max 180 mean  70.2   sunrise · sun · line 102
bar 106     sun            shell max  93 mean  27.1   ears max 153 mean  77.8   sunrise
bar 107     sun            shell max 204 mean  32.3   ears max 159 mean  56.5   sunrise
bar 108     sun            shell max 204 mean  37.2   ears max 164 mean  22.6   sunrise
bar 109     sun            shell max 204 mean  41.0   ears max 168 mean  58.0   sunrise
bar 110     high           shell max 204 mean  44.3   ears max 184 mean  83.4   high · line 110
bar 111     high           shell max 204 mean  49.8   ears max 160 mean  65.2   high · line 110
bar 112     high           shell max 207 mean  53.7   ears max 161 mean  33.0   high · line 110
bar 114     melt           shell max 231 mean  44.6   ears max 184 mean  82.9   melt · ring 114
bar 115     melt           shell max 194 mean  57.3   ears max 160 mean  70.1   melt · ring 114
bar 116     melt           shell max 178 mean  60.4   ears max 150 mean  28.3   melt · ring 114
bar 117     melt           shell max 166 mean  61.5   ears max 144 mean  58.2   melt
bar 118     day            shell max 182 mean  55.2   ears max 181 mean  83.8   day · line 118
bar 120     day            shell max 229 mean  69.4   ears max 156 mean  33.3   day · line 
... [cut] ...
0    40.1%      18.1    0.24
  high           207.8s      906     1000    41.9%      18.1    0.26
  melt           215.4s      901     1000    43.7%      18.1    0.22
  day            222.8s      908     1000    47.4%      18.1    0.22
  peak           237.8s      905     1000    51.0%      18.1    0.21
  yellow         252.8s      649      946    53.2%      18.1    0.19
  last           267.8s      510      645    53.8%      18.1    0.20
  gone           275.4s      150      249    53.8%      18.1    0.06
  worst frame 0.51 ms; no scene reaches the sustained floor
Sat Oct 31 12:58:49 PDT 2026
```

```
$ cd "~/deadmau5 app"; python3 mau5scene.py check "TIKI TIKI - Slowed" 2>&1 | head -30; sed -n 225,350p mau5power.py
TIKI TIKI - Slowed: 8002 frames at 25 fps through the guard
  scene            from  mean mA   p95 mA     heat   allow W      ms
  (outside)        0.0s        0        0     0.0%      18.1    0.01
  dark             0.1s        0        0    18.7%      18.1    0.01
  embers           0.5s       31       46     0.0%      18.1    0.06
  hush             5.3s       27       38     0.0%      18.1    0.05
  lighting         7.0s      199      436     0.0%      18.1    0.09
  hook            10.5s      643      886     1.0%      18.1    0.11
  hookb           17.5s      640      862     1.9%      18.1    0.18
  dip             24.4s      140      269     1.9%      18.1    0.06
  climb           26.2s      250      538     1.8%      18.1    0.10
  hook2           27.9s      636      891     3.2%      18.1    0.23
  burn            38.4s      392      815     3.6%      18.1    0.12
  lagoon          45.3s      182      307     3.5%      18.1    0.09
  stop            47.0s       72      156     3.4%      18.1    0.11
  still           48.8s      465      491     3.6%      18.1    0.22
  swell           54.0s      461      567     3.7%      18.1    0.19
  verse           55.7s      315      762     3.9%      18.1    0.12
  vlow            66.2s      187      376     3.8%      18.1    0.05
  vrise           67.9s      155      375     3.7%      18.1    0.10
  big             69.6s      584      890     5.2%      18.1    0.20
  bigb            83.6s      565      845     7.1%      18.1    0.23
  burn2          101.0s      330      617     7.4%      18.1    0.10
  lagoon2        107.9s      177      308     7.2%      18.1    0.10
  stop2          109.6s       38       60     7.1%      18.1    0.06
  watched        111.4s      380      488     7.1%      18.1    0.16
  swell2       
... [cut] ...
es under budget too,
        # or the climb back would be one jump.  Measured through the
        # phone's twin with the test suite's music drive, at 15 and 40
        # fps, where the governor binds -- blades, spectrum, the Dimension
        # Remix blades cue, beneath's split under a sparkle overlay -- it
        # took a further 3-17% off the shell's frame-to-frame jitter on
        # top of the soft ceiling, for 2-6% of their current.  A rate per
        # region, so the shell climbs no faster than the tubes, lost 30%
        # of the light on that split and made it jitter more: one frame
```

```
$ cd "~/deadmau5 app"; python3 mau5scene.py check "TIKI TIKI - Slowed" 2>&1 | head -30; sed -n 225,350p mau5power.py
TIKI TIKI - Slowed: 8002 frames at 25 fps through the guard
  scene            from  mean mA   p95 mA     heat   allow W      ms
  (outside)        0.0s        0        0     0.0%      18.1    0.01
  dark             0.1s        0        0    18.7%      18.1    0.01
  embers           0.5s       31       46     0.0%      18.1    0.06
  hush             5.3s       27       38     0.0%      18.1    0.05
  lighting         7.0s      199      436     0.0%      18.1    0.09
  hook            10.5s      643      886     1.0%      18.1    0.11
  hookb           17.5s      640      862     1.9%      18.1    0.18
  dip             24.4s      140      269     1.9%      18.1    0.06
  climb           26.2s      250      538     1.8%      18.1    0.10
  hook2           27.9s      636      891     3.2%      18.1    0.23
  burn            38.4s      392      815     3.6%      18.1    0.12
  lagoon          45.3s      182      307     3.5%      18.1    0.09
  stop            47.0s       72      156     3.4%      18.1    0.11
  still           48.8s      465      491     3.6%      18.1    0.22
  swell           54.0s      461      567     3.7%      18.1    0.19
  verse           55.7s      315      762     3.9%      18.1    0.12
  vlow            66.2s      187      376     3.8%      18.1    0.05
  vrise           67.9s      155      375     3.7%      18.1    0.10
  big             69.6s      584      890     5.2%      18.1    0.20
  bigb            83.6s      565      845     7.1%      18.1    0.23
  burn2          101.0s      330      617     7.4%      18.1    0.10
  lagoon2        107.9s      177      308     7.2%      18.1    0.10
  stop2          109.6s       38       60     7.1%      18.1    0.06
  watched        111.4s      380      488     7.1%      18.1    0.16
  swell2       
... [cut] ...
es under budget too,
        # or the climb back would be one jump.  Measured through the
        # phone's twin with the test suite's music drive, at 15 and 40
        # fps, where the governor binds -- blades, spectrum, the Dimension
        # Remix blades cue, beneath's split under a sparkle overlay -- it
        # took a further 3-17% off the shell's frame-to-frame jitter on
        # top of the soft ceiling, for 2-6% of their current.  A rate per
        # region, so the shell climbs no faster than the tubes, lost 30%
        # of the light on that split and made it jitter more: one frame
```

```
$ cd "~/deadmau5 app"; KIT=tools/showkit; W=$KIT/work/remember; B="Kaskade feat. deadmau5 - I Remember"; python3 - <<'PYEOF'
p="tools/showkit/songs/remember/write_treatment.py"
s=open(p).read()
# --- motif gains
s=s.replace('''"lo": 0, "hi": 1, "pal": "dusk", "gain": 0.14},''','''"lo": 0, "hi": 1, "pal": "dusk", "gain": 0.11},''')
s=s.replace('''"lo": 0, "hi": 1, "pal": "pastel", "gain": 0.2},''','''"lo": 0, "hi": 1, "pal": "pastel", "gain": 0.14},''')
s=s.replace('''"pal": "dusk", "gain": {"band": "high", "lo" ... [cut]
125:S({"name": "dawn", "from": "dawn", "to": "morn", "pal": "dusk", "pump": SOFT, "layers": [
126-    {"use": "sky", "gain": [0.1, 0.16]},
127-    {"use": "sun", "y": [-330, -130], "rad": 340, "gain": [0.4, 0.26]},
128-    {"use": "breath", "c": C_A(18, 22), "gain": 0.45},
129-    {"use": "rimkick", "c": C_A(18, 22)},
wrote shows/scenes/Kaskade feat. deadmau5 - I Remember.scene.json scenes 30 hits 39
Kaskade feat. deadmau5 - I Remember: marks against the bar map (bar-1, bar, bar+1)
Kaskade feat. deadmau5 - I Remember: 32 scenes, 39 hits, written into shows/Kaskade feat. deadmau5 - I Remember.json
Kaskade feat. deadmau5 - I Remember: 7078 frames at 25 fps through the guard
  scene            from  mean mA   p95 mA     heat   allow W      ms
  dark             0.0s        0        0    49.1%      18.1    0.01
  develop          1.6s      251      719     0.1%      18.1    0.09
  photo            5.4s      382      417     0.3%      18.1    0.16
  dim             11.0s      486      755     0.5%      18.1    0.14
  rose            12.8s      563      799     1.3%      18.1    0.16
  lav             20.4s      578      792     2.1%      18.1    0.16
  climb           27.8s      838     1000     3.3%      18.1    0.15
  inhale          33.5s      995     1000     3.9%      18.1    0.08
  dawn            35.4s      883     1000     5.6%      18.1    0.16
  morning         42.8s      821     1000    10.3%      18.1    0.18
  voice           65.4s      830     1000    16.0%      18.1    0.24
  longnote        91.6s      845     1000    16.8%      18.1    0.17
  hook            95.4s      861     1000    23.6%      18.1    0.23
  fall           125.4s      757     1000    24.6%      18.1    0.16
  rest0          131.0s       32       35    24.6%      18.1    0.06
  left         
... [cut] ...
000    40.4%      18.1    0.22
  day            222.8s      849     1000    43.7%      18.1    0.21
  peak           237.8s      846     1000    47.0%      18.1    0.21
  yellow         252.8s      583      829    48.7%      18.1    0.18
  last           267.8s      487      604    49.3%      18.1    0.19
  gone           275.4s      150      249    49.3%      18.1    0.06
  worst frame 1.47 ms; no scene reaches the sustained floor
Sat Oct 31 13:00:51 PDT 2026
tools/showkit/songs/remember/d5.png (1800, 1225)
```

```
$ cat > tools/showkit/songs/remember/asked.py <<'EOF'
# per scene: mA asked before the guard, split shell / tubes / rims, and what the guard sent
import json, os, sys
sys.path.insert(0, os.getcwd())
import numpy as np, mau5engine as E, mau5scene as M, mau5power, mau5show
base=sys.argv[1]
show=json.load(open("shows/%s.json"%base))
music=mau5show._music_for(show,"shows/%s.mp3"%base)
h=E.Helmet(); sc=M.Scenes(show["scenes"],h); g=mau5power.load(count=h.n)
fps=20.0
print("MA_PER_LED_FULL_WHITE",mau5power.MA_PER_LED_FULL_WHITE)
per={};order=[]
k=mau5power.MA_PER_LED_FULL_WHITE/(3*255.0)
for i in range(int(float(s ... [cut]
MA_PER_LED_FULL_WHITE 19.0
scene            asked: shell tubes rims | sent total  shell tubes | shell kept
dark                  0      0     0 |      0      0      0 |    0%
develop             131    106    24 |    249    105    103 |   80%
photo               579     33    49 |    382    285     31 |   49%
dim                 484    157    34 |    486    280    153 |   58%
rose                710    122   141 |    563    285    118 |   40%
lav                 910    116   162 |    577    285    112 |   31%
climb              1245    437   191 |    839    238    406 |   19%
inhale              570   1009     0 |    995    112    862 |   20%
dawn                764    568   141 |    883    226    512 |   30%
morning             864    460   136 |    821    251    423 |   29%
voice              1033    493   137 |    830    238    448 |   23%
longnote           1063    546   148 |    844    214    485 |   20%
hook                901    569   147 |    860    212    504 |   24%
fall                736    458    37 |    758    261    441 |   35%
rest0                34      0     0 |     32     19      0 |   57%
left                455    262     0 |    514    241    260 |   53%
rest1                33      0     0 |     32     19      0 |   57%
right               424    254     0 |    502    238    251 |   56%
rest2                32      0     0 |     31     18      0 |   56%
both                696    442     0 |    712    265    428 |   38%
afterimage          186      0     0 |    138    134      0 |   72%
blue                712    457   123 |    879    284    451 |   40%
blue2               655    506   144 |    863    237    475 |   36%
sing                846    389   111 |    706    235    355 |   28%
sunrise             825    547   154 |    867    221    492 |
... [cut] ...
           2     25     0 |     27      2     21 |   76%
lighting            133     93     0 |    203    105     91 |   79%
hook                486    490    47 |    647    205    384 |   42%
hookb               510    454    42 |    642    223    361 |   44%
dip                  65     45    36 |    140     54     40 |   84%
climb               144    101    28 |    248    113    100 |   78%
hook2               566    462    45 |    637    215    363 |   38%
burn                189    213    25 |    392    146    206 |   77%
lagoon               88     86    16 |    184     72     83 |   82%
```

```
$ cd "~/deadmau5 app"; KIT=tools/showkit; W=$KIT/work/remember; B="Kaskade feat. deadmau5 - I Remember"; python3 - <<'PYEOF'
p="tools/showkit/songs/remember/write_treatment.py"
s=open(p).read()
def rep(a,b,n=1):
    global s
    assert s.count(a)>=1, a
    s=s.replace(a,b) if n==0 else s.replace(a,b,n)
# --- motifs
rep('KICK = {"pat": "x", "step": 1, "decay": 0.9, "floor": 0.25}','KICK = {"pat": "x", "step": 1, "decay": 0.75, "floor": 0.1}')
rep('"lo": 0, "hi": 0.85, "pal": "sepia", "gain": 0.22},','"lo": 0, "h ... [cut]
wrote shows/scenes/Kaskade feat. deadmau5 - I Remember.scene.json scenes 30 hits 39
Kaskade feat. deadmau5 - I Remember: marks against the bar map (bar-1, bar, bar+1)
Kaskade feat. deadmau5 - I Remember: 32 scenes, 39 hits, written into shows/Kaskade feat. deadmau5 - I Remember.json
Kaskade feat. deadmau5 - I Remember: 7078 frames at 25 fps through the guard
  scene            from  mean mA   p95 mA     heat   allow W      ms
  dark             0.0s        0        0    41.7%      18.1    0.01
  develop          1.6s      226      655     0.1%      18.1    0.09
  photo            5.4s      363      401     0.3%      18.1    0.16
  dim             11.0s      472      755     0.4%      18.1    0.14
  rose            12.8s      495      724     1.0%      18.1    0.16
  lav             20.4s      501      708     1.6%      18.1    0.16
  climb           27.8s      758     1000     2.6%      18.1    0.15
  inhale          33.5s      996     1000     3.2%      18.1    0.08
  dawn            35.4s      815     1000     4.7%      18.1    0.18
  morning         42.8s      732      987     8.7%      18.1    0.18
  voice           65.4s      759     1000    13.5%      18.1    0.23
  longnote        91.6s      795     1000    14.3%      18.1    0.16
  hook            95.4s      778     1000    20.1%      18.1    0.22
  fall           125.4s      734     1000    21.0%      18.1    0.15
  rest0          131.0s       32       35    21.0%      18.1    0.06
  left           132.8s      516      790    21.4%      18.1    0.10
  rest1          138.5s       32       34    21.3%      18.1    0.06
  right          140.4s      501      781    21.7%      18.1    0.10
  rest2          146.0s       31       33    21.6%      18.1    0.06
  both           147.8s      714     1000    22.4%      18.
... [cut] ...
   807    261    441 |   30%
high               1085    404    80 |    746    270    378 |   25%
day                1176    397    78 |    738    270    371 |   23%
peak               1184    394    78 |    735    270    368 |   23%
yellow              433    218    30 |    511    259    202 |   60%
last                609    153     0 |    453    285    149 |   47%
gone                209      0     0 |    152    148      0 |   71%
Sat Oct 31 13:02:48 PDT 2026
tools/showkit/songs/remember/d6.png (1800, 980)
```

```
$ cd "~/deadmau5 app"; KIT=tools/showkit; W=$KIT/work/remember; B="Kaskade feat. deadmau5 - I Remember"; python3 $KIT/sheet.py "$B" $W/d7.png 48.5:long 50:hook 51:hook 52:hook 53.5:hook 54:hook 56:hook 58.5:hook 60:hook 62:hook 65:hook 66:fall 67:fall 68:fall 96.5:title 97.5:title 98.5:title 99.5:title 100.5:title 101.5:title 102:SUN 102.25:bloom 103:sun 104:sun 106:sun 108:sun 110:high 112:high 114:high 116:high 118:day 120:day 122:day 124:day 126:peak 128:peak 130:peak 132:peak 134:yellow 138:yellow 141:yellow 142:last 2>&1 | tail -1
tools/showkit/songs/remember/d7.png (1800, 1715)
```

```
$ cd "~/deadmau5 app"; grep -n "y_lo\|y_hi\|cell" remote/offline/*.js | head -20; grep -n "text" remote/offline/engine.js | head -20
remote/offline/audio.js:186:      audio: { echoCancellation: false, noiseSuppression: false,
remote/offline/audio.js:277:    // cancellation off: a howl, and presets following it.  Unplugged
remote/offline/engine.js:430:              speed: 70.0, y_lo: 28.0, y_hi: 145.0, cell: 16.7,
remote/offline/engine.js:442:    const hi = this.p.y_hi, lo = this.p.y_lo, rows = bm.rows;
remote/offline/engine.js:447:      rx[i] = h.px[i] / this.p.cell + t * this.p.speed / this.p.cell;
remote/offline/engine.js:459:                y_lo: 20.0, y_hi: 160.0, x_half: 150.0, blink: 0.0,
remote/offline/engine.js:468:    const hi = this.p.y_hi, lo = this.p.y_lo, xh = this.p.x_half;
remote/offline/engine.js:479:      // The top half, unless y_lo asks for the jaw as well.
remote/offline/engine.js:702:                   y_hi: 168.0, y_lo: 40.0, x_half: 95.0, loop: 2.0, face: '5x7' },
remote/offline/engine.js:716:    const hi = this.p.y_hi, lo = this.p.y_lo, xh = this.p.x_half;
remote/offline/engine.js:814:                          'size', 'cell', 'every', 'blink_every', 'decay',
remote/offline/ui.js:616:// cancelled, and let go of whatever it had already taken.
remote/offline/ui.js:1647:// it: the start is cancelled and lets go of whatever it had taken.
130:function textBitmap(fonts, text, spacing) {
133:  for (const ch of text.toUpperCase()) {
429:def('text', { text: 'DEADMAU5', color: [255, 160, 0], bg: [0, 0, 0],
433:    let bm = textBitmap(this.fonts, this.p.text, 1);
968:              textBitmap, glyphBitmap, digitBitmap, spriteBitmap, fract, pmod,
```

```
$ cd "~/deadmau5 app"; KIT=tools/showkit; W=$KIT/work/remember; B="Kaskade feat. deadmau5 - I Remember"; python3 - <<'PYEOF'
p="tools/showkit/songs/remember/write_treatment.py"
s=open(p).read()
def rep(a,b):
    global s
    assert s.count(a)>=1, a
    s=s.replace(a,b)
rep('''"params": {"text": "I REMEMBER", "color": [255, 232, 205]}, "gain": 0.5}]})''','''"params": {"text": "I REMEMBER", "color": [255, 226, 190], "y_lo": 54, "y_hi": 166}, "gain": 0.42}]})''')
rep('''{"use": "rays", "gain": [0.015, 0.17]},''',' ... [cut]
wrote shows/scenes/Kaskade feat. deadmau5 - I Remember.scene.json scenes 30 hits 39
Kaskade feat. deadmau5 - I Remember: marks against the bar map (bar-1, bar, bar+1)
Kaskade feat. deadmau5 - I Remember: 32 scenes, 39 hits, written into shows/Kaskade feat. deadmau5 - I Remember.json
bar 96.5    title          shell max 107 mean  11.8   ears max  25 mean   2.5   sing · I REMEMBER
bar 97      title          shell max 107 mean  14.2   ears max  30 mean   3.7   sing · I REMEMBER
bar 97.5    title          shell max 107 mean  22.3   ears max  34 mean   6.0   sing · I REMEMBER
bar 98      title          shell max 107 mean  24.5   ears max  48 mean   9.5   sing · I REMEMBER
bar 98.5    title          shell max 107 mean  34.5   ears max  62 mean  14.2   sing · I REMEMBER
bar 99      title          shell max 107 mean  31.8   ears max  68 mean  20.2   sing · I REMEMBER
bar 99.5    title          shell max 107 mean  36.3   ears max  74 mean  27.1   sing · I REMEMBER
bar 100     title          shell max 107 mean  35.1   ears max  77 mean  34.5   sing · I REMEMBER
bar 100.5   title          shell max 107 mean  33.0   ears max  79 mean  41.3   sing · I REMEMBER
bar 101     title          shell max 107 mean  22.8   ears max  82 mean  47.1   sing · I REMEMBER
bar 101.5   title          shell max 107 mean  13.5   ears max  84 mean  51.5   sing · I REMEMBER
bar 101.9   title          shell max  58 mean   6.0   ears max  86 mean  53.8   sing · I REMEMBER
bar 6.5     rose           shell max  96 mean  14.4   ears max  61 mean  14.2   rose · ring 6
bar 7.5     rose           shell max  99 mean  24.3   ears max  62 mean  25.9   rose · ring 6
bar 8.5     rose           shell max  91 mean  16.3   ears max  40 mean  10.9   rose · ring 6
bar 9.5     rose           shell max  98 mean  16.6   ears max  33 mean   9.4   rose
bar 10.5    lav            shell max  81 mean  19.7   ears max  46 mean  14.7   lav · ring 10
bar 11.5    lav            shell max  67 mean  26.9   ears max  68 mean  24.7   lav · ring 10
tools/showkit/songs/remember/d8.png (1800, 735)
```

```
$ cd "~/deadmau5 app"; KIT=tools/showkit; W=$KIT/work/remember; B="Kaskade feat. deadmau5 - I Remember"; date; python3 - <<'PYEOF'
p="tools/showkit/songs/remember/write_treatment.py"
s=open(p).read()
def rep(a,b):
    global s
    assert s.count(a)>=1, a
    s=s.replace(a,b)
rep('''"from": 1.3, "to": 0.05, "soft": 0.7, "cgrad": 0.2, "pal": "chord", "gain": 0.25},''','''"from": 1.3, "to": -0.05, "soft": 0.7, "cgrad": 0.2, "pal": "chord", "gain": 0.25},''')
rep('''{"use": "breath", "shape": "p", "from": 0.05, "to ... [cut]
Sat Oct 31 13:05:05 PDT 2026
wrote shows/scenes/Kaskade feat. deadmau5 - I Remember.scene.json scenes 30 hits 39
Kaskade feat. deadmau5 - I Remember: marks against the bar map (bar-1, bar, bar+1)
Kaskade feat. deadmau5 - I Remember: 32 scenes, 39 hits, written into shows/Kaskade feat. deadmau5 - I Remember.json
Kaskade feat. deadmau5 - I Remember: 7078 frames at 25 fps through the guard
  scene            from  mean mA   p95 mA     heat   allow W      ms
  dark             0.0s        0        0    40.1%      18.1    0.01
  develop          1.6s      226      655     0.1%      18.1    0.09
  photo            5.4s      363      401     0.3%      18.1    0.16
  dim             11.0s      472      755     0.4%      18.1    0.16
  rose            12.8s      495      724     1.0%      18.1    0.16
  lav             20.4s      501      708     1.6%      18.1    0.16
  climb           27.8s      758     1000     2.6%      18.1    0.16
  inhale          33.5s      996     1000     3.2%      18.1    0.08
  dawn            35.4s      791     1000     4.6%      18.1    0.18
  morning         42.8s      713      988     8.4%      18.1    0.19
  voice           65.4s      748     1000    13.2%      18.1    0.24
  longnote        91.6s      775     1000    13.9%      18.1    0.17
  hook            95.4s      757     1000    19.4%      18.1    0.23
  fall           125.4s      734     1000    20.4%      18.1    0.16
  rest0          131.0s       32       35    20.4%      18.1    0.06
  left           132.8s      516      790    20.8%      18.1    0.11
  rest1          138.5s       32       34    20.7%      18.1    0.07
  right          140.4s      501      781    21.0%      18.1    0.11
  rest2          146.0s       31       33    21.0%      18.1    0.06
  both           147.8s      7
... [cut] ...
      18.1    0.19
  gone           275.4s      150      249    40.3%      18.1    0.06
  worst frame 0.50 ms; no scene reaches the sustained floor
Kaskade feat. deadmau5 - I Remember: 128.000 BPM, 151 bars, bar 0 at 1.590 s, holds []
music against the grid per 8 bars, ms (contrast): 0:+5(1.64)  8:+3(4.31)  16:-1(2.20)  24:-3(2.98)  32:-1(3.07)  40:-1(3.41)  48:-1(3.11)  56:-1(3.36)  64:-1(1.84)  72:-1(1.20)  80:+5(1.80)  88:+5(2.47)  96:+5(2.84)  104:-1(3.15)  112:-1(3.11)  120:+3(3.24)  128:+1(2.85)  136:-1(2.95)  144:+37(1.17)
worst 37 ms where the music is clear enough to say, mean +3.1 ms
```

```
$ cd "~/deadmau5 app"; KIT=tools/showkit; W=$KIT/work/remember; B="Kaskade feat. deadmau5 - I Remember"; python3 $KIT/sheet.py "$B" $W/d9.png 22:m 22.5:m 23:m 23.5:m 24:m 24.5:m 25:m 25.5:m 26:m 26.5:m 27:m 27.5:m 35:l 35.5:l 36:l 36.5:l 37:l 37.5:l 38:l 38.5:l 39:l 39.5:l 40:l 40.5:l 2>&1 | tail -1
tools/showkit/songs/remember/d9.png (1800, 980)
```

```
$ cd "~/deadmau5 app"; sed -n 520,560p remote/offline/show.js; KIT=tools/showkit; W=$KIT/work/remember; B="Kaskade feat. deadmau5 - I Remember"; python3 - <<'PYEOF'
p="tools/showkit/songs/remember/write_treatment.py"
s=open(p).read()
def rep(a,b):
    global s
    assert s.count(a)>=1, a
    s=s.replace(a,b)
rep('''{"use": "breath", "on": "tubes1", "pal": "chord", "c": C_A(82, 90), "gain": 0.26},''','''{"use": "breath", "on": "tubes1", "pal": "chord", "c": C_A(82, 90), "gain": 0.24},''')
rep('''"from": -0.05, " ... [cut]
      case 'fill': {
        this._pal(P, c0);
        const w = G * 1;
        for (let m = 0; m < nm; m++) this._put(mix, idx[m], w);
        break;
      }
      case 'grad': {
        const scale = valAt(P.scale, p, bar, music, tt);
        const speed = valAt(P.speed, p, bar, music, tt);
        const ofs = valAt(P.ofs, p, bar, music, tt);
        const warp = valAt(P.warp, p, bar, music, tt);
        const lo = valAt(P.lo, p, bar, music, tt), hi = valAt(P.hi, p, bar, music, tt);
        const wscale = warp !== 0 ? valAt(P.wscale, p, bar, music, tt) : 0;
        const wspeed = warp !== 0 ? valAt(P.wspeed, p, bar, music, tt) : 0;
        const A = P.a, A2 = P.a2, saw = P.saw;
        for (let m = 0; m < nm; m++) {
          const i = idx[m];
          let x = A[i] * scale + B * speed + ofs;
          if (warp !== 0) x = x + warp * Math.sin(2 * Math.PI * (A2[i] * wscale + B * wspeed));
          const f = pmod(x, 1);
          const wv = saw ? f : 1 - Math.abs(2 * f - 1);
          this._pal(P, lo + (hi - lo) * wv);
          this._put(mix, i, G * 1);
        }
        break;
      }
      case 'sweep': {
        const speed = valAt(P.speed, p, bar, music, tt);
        let sh;
        if (P.shape === 0) sh = p;
        else {
          const f = pmod(lb * speed, 1);
          sh = P.shape === 1 ? f : 1 - Math.abs(2 * f - 1);
        }
        const a0 = valAt(P.from, p, bar, music, tt), a1 = valAt(P.to, p, bar, music, tt);
        const pos = a0 + (a1 - a0) * sh;
        const width = valAt(P.width, p, bar, music, tt);
        const soft = valAt(P.soft, p, bar, music, tt);
        const cgrad = valAt(P.cgrad, p, bar, music, tt);
        const A = P.a, band = P.band;
        for (let m = 0; m < nm; m++) {
wrote shows/scenes/Kaskade feat. deadmau5 - I Remember.scene.js
... [cut] ...
t. deadmau5 - I Remember.json
  day            222.8s      716      989    36.7%      18.1    0.21
  peak           237.8s      713      989    39.2%      18.1    0.20
  yellow         252.8s      543      736    40.7%      18.1    0.22
  last           267.8s      453      555    41.2%      18.1    0.19
  gone           275.4s      150      249    41.2%      18.1    0.05
  worst frame 0.42 ms; no scene reaches the sustained floor
tools/showkit/songs/remember/d10.png (1800, 1225)
Sat Oct 31 13:06:10 PDT 2026
```

```
$ cd "~/deadmau5 app"; KIT=tools/showkit; W=$KIT/work/remember; B="Kaskade feat. deadmau5 - I Remember"; sed -n 20,75p $W/write_treatment.py | cut -c1-170 | grep -n '"gain"' | head -30; python3 - <<'PYEOF'
p="tools/showkit/songs/remember/write_treatment.py"
s=open(p).read()
def rep(a,b):
    global s
    assert s.count(a)>=1, a
    s=s.replace(a,b)
# base layers of the shell down, so the guard squeezes the highlights less; the base ends up about where it was
rep('"lo": 0, "hi": 0.85, "pal": "sepia", "gain": 0.1 ... [cut]
30:                       "wscale": 3, "wspeed": 0.02, "lo": 0, "hi": 0.85, "pal": "sepia", "gain": 0.15},
33:                  "wscale": 1.2, "wspeed": 0.03, "lo": 0, "hi": 1, "pal": "dusk", "gain": 0.085},
36:                     "wscale": 1.1, "wspeed": 0.025, "lo": 0, "hi": 1, "pal": "pastel", "gain": 0.1},
39:                   "spread": 0.3, "pal": "sepia", "gain": 0.5},
41:                    "pal": "dusk", "gain": {"band": "high", "lo": 0.0, "hi": 0.2}},
44:                     "from": 1.3, "to": -0.05, "soft": 0.7, "cgrad": 0.2, "pal": "chord", "gain": 0.25},
45:          "rimkick": {"fx": "fill", "on": "rims", "pal": "chord", "gain": 0.36, "gate": KICK},
48:                   "ctip": 1.0, "gain": 0.55},
51:                  "params": dict(FIG, color="sepia@0.9"), "gain": 0.3},
54:                   "wscale": 1.5, "wspeed": 0.02, "lo": 0.02, "hi": 0.92, "pal": "sun", "gain": 0.17},
55:          "disc": {"fx": "orb", "on": "shell", "x": 0, "soft": 35, "pal": "sun", "c": 1.0, "cgrad": -0.2, "mix": "max", "gain": 0.62, "gate": {"pat": "x", "step": 1, "dec
wrote shows/scenes/Kaskade feat. deadmau5 - I Remember.scene.json scenes 30 hits 50
Kaskade feat. deadmau5 - I Remember: marks against the bar map (bar-1, bar, bar+1)
Kaskade feat. deadmau5 - I Remember: 32 scenes, 50 hits, written into shows/Kaskade feat. deadmau5 - I Remember.json
Kaskade feat. deadmau5 - I Remember: 7078 frames at 25 fps through the guard
  scene            from  mean mA   p95 mA     heat   allow W      ms
  dark             0.0s        0        0    40.8%      18.1    0.01
  develop          1.6s      209      615     0.1%      18.1    0.10
  photo            5.4s      352      401     0.2%      18.1    0.17
  dim             11.0s      462      755     0.3%      18.1    0.16
  rose          
... [cut] ...
  714    270    347 |   32%
peak                920    368    77 |    711    270    345 |   29%
yellow              450    235    33 |    537    265    218 |   59%
last                566    153     0 |    453    285    149 |   50%
gone                209      0     0 |    152    148      0 |   71%
Sat Oct 31 13:07:01 PDT 2026
tools/showkit/songs/remember/d11.png (1800, 980)
tools/showkit/songs/remember/d12.png (1800, 735)
```

I'll read the correction and re-measure with the fixed tools.

```
$ cd "~/deadmau5 app"; KIT=tools/showkit; date; tail -30 $KIT/BRIEF.md; echo ------; cat $KIT/sheet.py; echo -----; cat $KIT/power.py; echo -----; cat $KIT/scenepower.py; B="Kaskade feat. deadmau5 - I Remember"; echo ----; python3 $KIT/power.py "$B"; python3 $KIT/scenepower.py "$B"
Sat Oct 31 13:07:37 PDT 2026
4. Write the treatment with a small Python generator in your scratch folder (see Tiki's), using `from fmt import save` with `sys.path.insert(0, KIT)`, then `python3 mau5scene.py compile "<base>"` and fix what it refuses. Put a real `about` string in it describing the concept, the same style as Tiki's.
5. Look at it. `python3 $KIT/sheet.py "<base>" out.png 40:drop 40.25 41 ...` renders tiles as the helmet will really look after the power guard, and prints how bright shell and ears end up. READ THE PNG. Does it read as your idea? Is the shell visible next to the ears? Check every major section, each hit, and both a kick and the gap after it. Iterate.
6. `python3 mau5scene.py check "<base>"`: every scene through the power guard. Heat under about 40%, and no scene "at the sustained floor". `python3 $KIT/grid.py check "<base>"` again at the end.

## The treatment format
Bars, not seconds: bar b is `t0 + 4 b spb` on your grid. Top level: `v:1, show, about, lead:0, marks{name:bar or "other+2"}, palettes{name:[[r,g,b],...] or {"stops":[...],"wrap":true}}, motifs{name: layer or [layers]}, scenes[], hits[]`. A value may be a number, `[from,to]` (a ramp over the scene), `{"<bar or mark>":v,...}` (steps at bars), or `{"band":"bass|mid|high","lo":a,"hi":b,"punch":true|false}` (driven by the track, resolved live; the phone has these curves). Scenes tile the song, from bar -1 (a gap is dark): `{"name","from","to","pal","pump":{"pat":"x...","step":0.25,"depth":0.2,"decay":0.5},"out":beats of darkness before the next scene (max 4),"layers":[...]}`; `like:"earlier scene"` copies one and `patch:{"layerIndex":{...}}`, `add:[...]` or `each:{...}` change it (patch indexes the authored layers before motif expansion). Hits are moments over a scene: `{"name","at":ba
... [cut] ...
.7     48  26.9%
sing              652   1000     24     69     8.4    22.9     52  28.6%
sunrise           787   1000     15    100     9.0    30.0     34  31.5%
high              722    989      6    100     9.1    25.9     30  34.1%
day               714    989      5    100     9.1    25.4     26  36.6%
peak              711    989      5    100     9.1    25.2     23  39.1%
yellow            537    712      0     82     9.0    15.0     41  40.5%
last              452    555      0     91     9.6     8.9     45  41.0%
gone              150    249      0      0     5.0     0.0     47  41.0%
```

```
$ cd "~/deadmau5 app"; KIT=tools/showkit; date; ls -la --time-style=full-iso mau5preview.py 2>/dev/null || ls -lT mau5preview.py mau5show.py mau5power.py mau5fx.py mau5engine.py mau5scene.py $KIT/sheet.py $KIT/fmt.py; git -C "~/deadmau5 app" diff --stat -- mau5preview.py | tail -2; git log -3 --format='%h %ad %s' --date=iso -- mau5preview.py; cat $KIT/sheet.py | head -40; sed -n 1,60p mau5preview.py
Sat Oct 31 13:08:39 PDT 2026
-rw-r--r--@ 1 jones  wheel    933 Oct 31 12:37:00 2026 tools/showkit/fmt.py
-rw-r--r--@ 1 jones  wheel   2587 Oct 31 13:06:11 2026 tools/showkit/sheet.py
-rw-r--r--@ 1 jones  staff  57742 Oct 31 12:51:03 2026 mau5engine.py
-rwxr-xr-x@ 1 jones  staff  39078 Oct 31 12:34:16 2026 mau5fx.py
-rw-r--r--@ 1 jones  staff  24732 Oct 30 04:10:02 2026 mau5power.py
-rw-r--r--@ 1 jones  staff   7844 Oct 29 13:08:29 2026 mau5preview.py
-rw-r--r--@ 1 jones  staff  56869 Oct 31 12:34:16 2026 mau5scene.py
-rw-r--r--@ 1 jones  staff  43836 Oct 30 19:15:52 2026 mau5show.py
4bd0347 2026-10-29 13:12:04 -0700 No profile no longer means no limit; the README describes this helmet
6adb22d 2026-10-27 09:05:44 -0700 deadmau5 helmet: mapping, power guard, preset engine, shows, controller
#!/usr/bin/env python3
"""sheet.py "<base>" out.png bar[:label] bar[:label] ... -- the show at those bars as the helmet will really look: through the real power guard (cold, settled for a second first), then gamma so the picture is what an eye sees. Prints per tile the mA sent and how bright shell and ears really are after the guard. Bars may be fractional: 40.25 is the second beat of bar 40, so catch both a kick and the gap after it. Env: COLS, TW, GAM. Run from the repo root. Credit: the Radio Edit author, who found the first version skipped the guard."""
import json, os, sys
sys.path.insert(0, os.getcwd())
import numpy as np, mau5show, mau5preview as PV, mau5scene as SS, mau5engine as E, mau5power
from PIL import Image, ImageDraw
base, out = sys.argv[1], sys.argv[2]
marks = []
for a in sys.argv[3:]:
    b, _, 
... [cut] ...
ims are bare edge-on strip, so they read tighter.
    rad = np.where(h.rims, 5.0, np.where(h.shell, 13.0, 10.0))
    return px, py, rad, z


def _kernels(radii):
    out = {}
    for r in np.unique(np.round(radii, 1)):
        n = int(r * 3) | 1
        a = np.arange(n) - n // 2
        gx, gy = np.meshgrid(a, a)
        d = np.hypot(gx, gy)
        out[float(r)] = np.clip(np.exp(-(d / (r * 0.55)) ** 2), 0, 1)
    return out


class Scene:
    def __init__(self, helmet):
        self.h = helmet
        self.px, self.py, self.rad, self.z = _project(helmet)
        self.kern = _kernels(self.rad)
```

```
$ cd "~/deadmau5 app"; KIT=tools/showkit; W=$KIT/work/remember; sed -n 40,60p $KIT/sheet.py; python3 $KIT/sheet.py "TIKI TIKI - Slowed" $W/tiki2.png 2:embers 5:hook 5.25:hook 15:hook2 26.5:stop 28:lagoon 31:verse 39:big 45:idol 75:sunset 107:duel 153:final 2>&1 | tail -14
    d.text(((k % cols) * W + 5, (k // cols) * H + 15), (label or "")[:42], fill=(180, 180, 180))
    s = res[h.shell]; e = res[h.ears]
    print("bar %-7g %-10s sent %4.0f mA  shell max %3.0f mean %5.1f  ears max %3.0f mean %5.1f  %s" % (bar, lab[:10], rep["sent_ma"], s.max(), s.mean(), e.max(), e.mean(), label))
o.save(out)
print(out, o.size)
bar 2       embers     sent   36 mA  shell max  14 mean   0.0  ears max  14 mean   1.8  embers
bar 5       hook       sent 1000 mA  shell max  21 mean   3.7  ears max 126 mean  52.5  hook · LIT
bar 5.25    hook       sent  800 mA  shell max  21 mean   7.4  ears max 107 mean  33.8  hook · LIT
bar 15      hook2      sent 1000 mA  shell max  14 mean   3.7  ears max 126 mean  52.6  hook2 · HOOK 2
bar 26.5    stop       sent   49 mA  shell max  55 mean   1.3  ears max   0 mean   0.0  stop · TIKI TIKI
bar 28      lagoon     sent  489 mA  shell max  40 mean   9.7  ears max  50 mean  11.2  still · TIKI TIKI
bar 31      verse      sent 1000 mA  shell max  49 mean   7.2  ears max  97 mean  46.0  verse · VERSE
bar 39      big        sent 1000 mA  shell max   9 mean   2.5  ears max 120 mean  54.3  big · IDOL
bar 45      idol       sent  826 mA  shell max  24 mean   9.8  ears max 145 mean  31.3  big
bar 75      sunset     sent 1000 mA  shell max  10 mean   3.2  ears max 124 mean  53.2  sunset · SUNSET
bar 107     duel       sent 1000 mA  shell max  16 mean   2.5  ears max 120 mean  54.7  duel · DUEL
bar 153     final      sent 1000 mA  shell max   3 mean   2.2  ears max 139 mean  54.8  final · FINAL
tools/showkit/songs/remember/tiki2.png (1800, 490)
```
