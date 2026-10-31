# What the robot builder ran and saw

Commands and their text output, in order, with long output cut. Images are left out; rerun the tools to see them. Cut off partway: the generator and treatment in the repo are the latest state.

I'll start by reading the brief.

```
$ date; ls -la "tools/showkit/"; ls -la "tools/showkit/songs" 2>/dev/null
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
$ date; ls -la "tools/showkit/"; ls -la "tools/showkit/songs" 2>/dev/null
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
$ KIT=tools/showkit; cd "~/deadmau5 app"; ls -la shows/ | head -60; ls -la shows/scenes | head -60; echo ---; cat "$KIT/fmt.py"; echo ---; cat "$KIT/sheet.py"; echo ---; cat "$KIT/songmap.py"; echo ---; cat "$KIT/spectro.py"; echo ---; cat "$KIT/spritetry.py"
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
$ KIT=tools/showkit; cd "~/deadmau5 app"; ls -la shows/ | head -60; ls -la shows/scenes | head -60; echo ---; cat "$KIT/fmt.py"; echo ---; cat "$KIT/sheet.py"; echo ---; cat "$KIT/songmap.py"; echo ---; cat "$KIT/spectro.py"; echo ---; cat "$KIT/spritetry.py"
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
$ KIT=tools/showkit; mkdir -p "$KIT/work/robot"; cd "~/deadmau5 app"; time python3 "$KIT/grid.py" scan "shows/deadmau5 - Harder Better Faster Stronger.mp3" 2>&1 | tail -30
estimator: 128.000 BPM, first bar 0.006 s, tempo lock 0.670, bar lock 0.13681481508520976; song 299.1 s
refined over the whole song: spb 0.468761 = 127.997 BPM
first half 127.997 BPM, second half 127.997 BPM (these should agree within 0.05)
phase of the music against that grid per 8 bars, ms (flat = right; one 16th = 117 ms; contrast under 1.15 means sparse, ignore it):
  0:-5(1.71)  8:-1(2.62)  16:-3(4.97)  24:-3(4.11)  32:-1(3.65)  40:-3(2.77)  48:-5(1.36)  56:-7(1.43)  64:-5(2.21)  72:-3(1.92)  80:-3(2.14)  88:-3(2.74)  96:-3(3.67)  104:-3(3.71)  112:-5(3.52)  120:+1(3.15)  128:-5(4.02)  136:-5(3.77)  144:-5(3.84)  152:-5(3.88)
change per beat position, estimator's bar 1 at 0.006 s: 0:0.82 1:0.85 2:0.92 3:1.05  (the highest is where bars really start, 0 = estimator is right)
strongest phrase positions, in beats mod 32 from that bar 1: 16(1.62), 14(1.39), 23(1.20), 15(1.15), 11(1.14), 17(1.11)
biggest single changes (time, beat from bar 1, beat mod 4): 7.0s b15 m3; 21.6s b46 m2; 22.5s b48 m0; 25.8s b55 m3; 27.7s b59 m3; 29.5s b63 m3; 30.5s b65 m1; 31.4s b67 m3; 35.2s b75 m3; 37.0s b79 m3; 37.5s b80 m0; 49.2s b105 m1; 50.6s b108 m0; 51.1s b109 m1; 51.6s b110 m2; 52.5s b112 m0; 82.0s b175 m3; 82.5s b176 m0; 112.0s b239 m3; 112.5s b240 m0; 171.6s b366 m2; 172.5s b368 m0; 265.8s b567 m3; 292.5s b624 m0
suggested next: grid.py fold with --spb 0.468761 --anchor 0.006, decide the bar line, then grid.py write
python3 "$KIT/grid.py" scan  2>&1  1.82s user 0.80s system 107% cpu 2.441 total
tail -30  0.00s user 0.00s system 0% cpu 2.441 total
```

```
$ cd "~/deadmau5 app"; python3 mau5scene.py --help 2>&1 | head -30; sed -n 1,80p mau5scene.py; ffprobe -hide_banner "shows/deadmau5 - Harder Better Faster Stronger.mp3" 2>&1 | tail -12
usage: mau5scene.py [-h] {bars,compile,check} ...

mau5scene -- shows choreographed per song, instead of a playlist of effects.

positional arguments:
  {bars,compile,check}
    bars                the bar map, to write marks against
    compile             compile a treatment into its show
    check               power and cost, scene by scene

optional arguments:
  -h, --help            show this help message and exit

mau5scene -- shows choreographed per song, instead of a playlist of effects.

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
#!/usr/bin/env python3
"""mau5scene -- shows choreographed per song, instead of a playlist of effects.

A cue-list show (mau5show.build) picks a stock preset for each phrase
from a pool and holds it.  It follows the music's level and lands on its
beats, and it still reads as a playlist: the same eight effects in a
different order for ever
... [cut] ...
"eyes")
REGIONS = ("all", "shell", "ears", "ear1", "ear2", "tubes", "rims",
           "tube0", "tube1", "tube2", "left", "right", "face", "jaw",
           "rim1", "rim2", "tubes1", "tubes2")
AXES = ("x", "y", "r", "a", "al", "u")
WAVES = ("tri", "saw")
SHAPES = ("p", "saw", "tri")
Input #0, mp3, from 'shows/deadmau5 - Harder Better Faster Stronger.mp3':
  Metadata:
    encoder         : Lavf58.20.100
  Duration: 00:04:59.08, start: 0.025057, bitrate: 192 kb/s
  Stream #0:0: Audio: mp3 (mp3float), 44100 Hz, stereo, fltp, 192 kb/s, start 0.025057
    Metadata:
      encoder         : Lavc58.35
```

```
$ KIT=tools/showkit; cd "~/deadmau5 app"; M="shows/deadmau5 - Harder Better Faster Stronger.mp3"; python3 "$KIT/grid.py" fold "$M" --spb 0.468761 --anchor 0.006 2>&1 | head -100; ls -la "shows/scenes/" | grep -i harder; ls -la shows | grep -i harder
bar 0 at 0.006 s, 127.997 BPM, 159 bars
bars 0-16   (16 steps, | every beat; one row per band)
   sub     @-#-|#==+|%===|%==-   peak 0.39
   bass    @=*-|@=:=|#:+-|#-+.   peak 0.57
   lowmid  #:+:|%-+-|@:*=|+:=:   peak 0.73
   mid     *.=:|@.+-|#:=:|*:+=   peak 0.55
   pres    #.*-|@:#=|@.#=|#-#+   peak 0.38
   air     @:=:|@*%:|%-+:|*-+:   peak 0.30
bars 16-32   (16 steps, | every beat; one row per band)
   sub     %.#.|+:.+|@::=|#::.   peak 0.76
   bass    @:%:|@- +|@.--|+.:.   peak 1.12
   lowmid  % *.|#:.=|@.-=|= :.   peak 1.42
   mid     # * |@.:+|#.=-|= ==   peak 1.19
   pres    * @=|@.==|*.@*|= %-   peak 0.84
   air     + #.|@.+:|-.@.|- %    peak 0.77
bars 32-48   (16 steps, | every beat; one row per band)
   sub     @.+.|*::=|@::+|#.-.   peak 0.67
   bass    @:#:|@::=|@.-+|=:-.   peak 0.94
   lowmid  %.*.|@::=|@.=+|=.-.   peak 0.95
   mid     =.+.|@.:-|*.=-|= -:   peak 0.96
   pres    -.%-|@:-.|-.*-|=.*.   peak 0.70
   air     ..@.|#:* |::@.|-:#.   peak 0.69
bars 48-64   (16 steps, | every beat; one row per band)
   sub     @-::|+:=:|%:=-|@:-:   peak 0.56
   bass    @--:|*:-:|@:=:|@--:   peak 0.48
   lowmid  *=%:|=-@:|+=%:|*=@:   peak 0.24
   mid     @**=|#*+-|@+++|%##=   peak 0.24
   pres    @:=-|%:-:|%:-:|@:-+   peak 0.30
   air     @:-+|%.--|%:--|@-:*   peak 0.29
bars 64-80   (16 steps, | every beat; one row per band)
   sub     @..:|@..:|@:::|@:.:   peak 0.70
   bass    @--.|@--:|@:-:|%-::   peak 0.64
   lowmid  @=+:|@==:|@=+:|%+*:   peak 0.33
   mid     %---|@-=-|@-=-|@:--   peak 0.49
   pres    *==:|@=--|#-+-|%==-   peak 0.39
   air     @.:.|%.:.|%.:.|@:-:   peak 0.54
bars 80-96   (16 steps, | every beat; one row per band)
   sub     %==:|=-=-|@-=-|+-=-   peak 0.53
   bass    @-#-|#-==|@:=-|*--:   peak 0.55
   lowmid  #:%:|%-==|@-#+|+-+:   peak 0.39
   mid
... [cut] ...
=.-.   peak 1.24
   lowmid  @ *.|#:.=|@.-=|- -.   peak 1.38
   mid     @ # |@.:+|@.*=|= *-   peak 1.06
   pres    * @-|*.=.|+.@#|= @:   peak 0.73
   air     . % |+ * |. #.|. @    peak 0.88
bars 144-159   (16 steps, | every beat; one row per band)
   sub     %.*.|#..=|@..+|*:-.   peak 0.77
   bass    @.+.|%: -|@.:-|+.:    peak 1.28
   lowmid  @ + |#..-|@ --|= :    peak 1.40
   mid     @ * |%.::|@ *-|= -    peak 1.15
   pres    % @ |#.+.|#.@-|- @.   peak 0.68
   air     : @ |+ * |. % |. @    peak 0.91
-rw-r--r--@  1 jones  staff   7179120 Oct 31 12:37 deadmau5 - Harder Better Faster Stronger.mp3
```

```
$ KIT=tools/showkit; cd "~/deadmau5 app"; B="deadmau5 - Harder Better Faster Stronger"; time python3 "$KIT/grid.py" write "$B" --spb 0.468761 --anchor 0.003 2>&1 | tail -15; python3 "$KIT/grid.py" check "$B"; python3 "$KIT/songmap.py" "$B"
    1:15.00-1:22.50  lvl3  strobe     {'hz': 6.0}
    1:22.50-2:00.01  lvl0  chase      {'period': 3.75}
    2:00.01-2:15.01  lvl1  earspin    {'period': 2.4}
    2:15.01-2:22.51  lvl1  wipe       {'period': 3.75, 'a': (0, 180, 255), 'b': (120, 0, 255)}
    2:22.51-3:00.01  lvl0  tubepulse  {'period': 7.5}
    3:00.01-3:15.01  lvl2  split      {'shell': 'plasma', 'ears': 'chase'}
    3:15.01-3:30.01  lvl2  eq         {}
    3:30.01-3:37.51  lvl2  rainbow    {'period': 6.0}
    3:37.51-3:52.51  lvl1  comet      {'period': 4.0}
    3:52.51-4:07.51  lvl1  sparkle    {}
    4:07.51-4:15.01  lvl1  chase      {'period': 2.2}
    4:15.01-4:30.01  lvl1  matrix     {}
    4:30.01-4:45.01  lvl1  spiral     {'period': 6.0}
    4:45.01-4:58.13  lvl1  tubepulse  {'period': 3.75}
wrote shows/scenes/deadmau5 - Harder Better Faster Stronger.beats: 639 beats, 159 bars, bar 0 at 0.003 s, 127.997 BPM
python3 "$KIT/grid.py" write "$B" --spb 0.468761 --anchor 0.003 2>&1  0.82s user 0.17s system 99% cpu 1.004 total
tail -15  0.00s user 0.00s system 0% cpu 1.004 total
deadmau5 - Harder Better Faster Stronger: 127.997 BPM, 160 bars, bar 0 at 0.003 s, holds []
music against the grid per 8 bars, ms (contrast): 0:-1(1.66)  8:+3(2.66)  16:-3(4.94)  24:-1(4.24)  32:+1(3.85)  40:+1(2.89)  48:-1(1.36)  56:-3(1.45)  64:-1(2.16)  72:-1(1.89)  80:+1(2.12)  88:+1(2.67)  96:-1(3.57)  104:-1(3.63)  112:-1(3.56)  120:+3(3.25)  128:-1(3.89)  136:-1(3.52)  144:-1(3.75)  152:-3(3.98)
worst 3 ms where the music is clear enough to say, mean -0.1 ms
deadmau5 - Harder Better Faster Stronger: 160 bars, 1.88 s a bar, 299.1 s
 bar     t   E  B  M  H  notes       change
   0    0.0   5  0  4  1  A F# E      
   1    1.9   6  0  5  3  A F# F      
   2    3.8   6  1  5  1  A E F       
   3    5.6   7  0  5  2  E A F  
... [cut] ...
4  5  C A F       
 145  271.9   8  9  4  5  C F A       
 146  273.8   8  8  4  5  C A F       
 147  275.6   9  9  5  5  C F A       
 148  277.5   8  8  4  5  C A F       
 149  279.4   8  9  3  4  C F A       
 150  281.3   8  8  4  5  C A F       
 151  283.1   8  9  5  5  C A F       
 152  285.0   8  8  4  5  C A F       
 153  286.9   8  9  3  4  C F A       
 154  288.8   8  8  4  5  C A F       
 155  290.6   8  9  5  5  C F A       
 156  292.5   5  5  3  6  C F A       >>
 157  294.4   4  4  2  4  C F A       >>
 158  296.3   3  4  1  3  C F A       
 159  298.1   2  3  0  2  C F A
```

```
$ KIT=tools/showkit; cd "~/deadmau5 app"; B="deadmau5 - Harder Better Faster Stronger"; W="$KIT/work/robot"; python3 "$KIT/spectro.py" "$B" "$W/spec_all.png"; python3 "$KIT/spectro.py" "$B" "$W/spec_0_32.png" 0 32; python3 "$KIT/spectro.py" "$B" "$W/spec_32_64.png" 32 64; python3 "$KIT/spectro.py" "$B" "$W/spec_64_96.png" 64 96;python3 "$KIT/spectro.py" "$B" "$W/spec_96_128.png" 96 128;python3 "$KIT/spectro.py" "$B" "$W/spec_128_160.png" 128 160; python3 mau5scene.py bars "$B" 0 16 | head -30
tools/showkit/songs/robot/spec_all.png
tools/showkit/songs/robot/spec_0_32.png
tools/showkit/songs/robot/spec_32_64.png
tools/showkit/songs/robot/spec_64_96.png
tools/showkit/songs/robot/spec_96_128.png
tools/showkit/songs/robot/spec_128_160.png
     0     0.00s  energy 0.44  bass 0.02 (punch 1.00)  mid 0.38  high 0.11
     1     1.88s  energy 0.45  bass 0.06 (punch 1.00)  mid 0.47  high 0.30
     2     3.75s  energy 0.50  bass 0.14 (punch 0.93)  mid 0.48  high 0.15
     3     5.63s  energy 0.58  bass 0.04 (punch 1.00)  mid 0.45  high 0.27
     4     7.50s  energy 0.47  bass 0.04 (punch 0.88)  mid 0.44  high 0.20
     5     9.38s  energy 0.41  bass 0.12 (punch 1.00)  mid 0.48  high 0.36
     6    11.25s  energy 0.49  bass 0.08 (punch 0.64)  mid 0.42  high 0.24
     7    13.13s  energy 0.56  bass 0.35 (punch 1.00)  mid 0.65  high 0.29
     8    15.00s  energy 0.58  bass 0.48 (punch 1.00)  mid 0.47  high 0.24
     9    16.88s  energy 0.56  bass 0.49 (punch 1.00)  mid 0.56  high 0.46
    10    18.75s  energy 0.55  bass 0.49 (punch 1.00)  mid 0.64  high 0.68
    11    20.63s  energy 0.52  bass 0.46 (punch 0.98)  mid 0.65  high 0.60
    12    22.50s  energy 0.68  bass 0.66 (punch 1.00)  mid 0.65  high 0.86
    13    24.38s  energy 0.66  bass 0.71 (punch 1.00)  mid 0.58  high 0.60
    14    26.25s  energy 0.63  bass 0.68 (punch 1.00)  mid 0.52  high 0.40
    15    28.13s  energy 0.63  bass 0.69 (punch 1.00)  mid 0.53  high 0.36
```

```
$ KIT=tools/showkit; W="$KIT/work/robot"; cat > "$W/roll.py" <<'EOF'
#!/usr/bin/env python3
# per bar, 16 steps: onset strength in a band: a piano roll of the groove.
import sys, os, re
import numpy as np
KIT=os.environ["KIT"]
z=np.load(os.path.join(KIT,"work",re.sub(r"\W+","_","deadmau5 - Harder Better Faster Stronger.mp3")+".env.npz"))
tt=z["tt"]; spb=0.468761; t0=0.003
CH=" .:-=+*#%@"
bands=sys.argv[1].split(","); lo=int(sys.argv[2]); hi=int(sys.argv[3]); kind=sys.argv[4] if len(sys.argv)>4 else "od"
for nm in bands:
    e=z[nm+("_od" if kind=="od" else "")]
    # normalise globally
    M=[]
    for b in ... [cut]
tools/showkit/songs/robot/roll.py:21: RuntimeWarning: Mean of empty slice.
  row.append(e[i:j].mean())
~/Library/Python/3.9/lib/python/site-packages/numpy/_core/_methods.py:138: RuntimeWarning: invalid value encountered in divide
  ret = ret.dtype.type(ret / rcount)
Traceback (most recent call last):
  File "tools/showkit/songs/robot/roll.py", line 30, in <module>
    print("%4d "%b+"|".join("".join(CH[int(a*10)] for a in v[i:i+4]) for i in range(0,16,4)))
  File "tools/showkit/songs/robot/roll.py", line 30, in <genexpr>
    print("%4d "%b+"|".join("".join(CH[int(a*10)] for a in v[i:i+4]) for i in range(0,16,4)))
  File "tools/showkit/songs/robot/roll.py", line 30, in <genexpr>
    print("%4d "%b+"|".join("".join(CH[int(a*10)] for a in v[i:i+4]) for i in range(0,16,4)))
ValueError: cannot convert float NaN to integer
sub (bar: | every beat)
```

```
$ KIT=tools/showkit; W="$KIT/work/robot"; export KIT; cd "~/deadmau5 app"; sed -i '' 's/M=np.array(M); /M=np.nan_to_num(np.array(M))/' "$W/roll.py"; python3 "$W/roll.py" sub 0 159 lvl 2>/dev/null | paste - - | head -0; python3 "$W/roll.py" sub 0 159 lvl 2>/dev/null > "$W/roll_sub.txt"; python3 "$W/roll.py" pres 0 159 od 2>/dev/null > "$W/roll_pres.txt"; python3 "$W/roll.py" mid 0 159 lvl 2>/dev/null > "$W/roll_mid.txt"; python3 "$W/roll.py" air 0 159 od 2>/dev/null > "$W/roll_air.txt"; paste -d' ' <(cut -c1-30 "$W/roll_sub.txt") <(cut -c6-30 "$W/roll_pres.txt") <(cut -c6-30 "$W/roll_mid.txt") <(c ... [cut]
head: illegal line count -- 0
sub (bar: | every beat) (bar: | every beat) bar: | every beat) bar: | every beat)
   0 .   |    |    |     + . |-.: |. : |=.:. %+::|@%#%|+.:-|%%#* - : |=.. |. = |:   
   1     |    |    |:    :.- |=.# |- - |-.:  ++=.|%:*%|*:*=|#++# :   | =+ |.:  |    
   2     |    | ...|-.-.    .|- . |    |::*  @#%#|###%|#@@%|@-#= . . |:   |.   |--# 
   3     |.   |.   |.    #   |:   |:   |-. . @@@%|%%@%|@%@%|#=#% = . |-   |: . |-   
   4     |    |  . |  .  :.  |* ..|# : |= .  #+: |@%%+|+.:=|%%## . : |:.. |= - |:   
   5 .   |.  .| .. |-. . = . |- * |+ :.|:.-. +*=.|%:*.|*-*+|#++- -   |-=* |-. .|    
   6 . ..| .. |.. .|:... - : |-.. |#.:.|. +  @*%+|**%+|#++*|%-## : : |: . |-  .|:.# 
   7 ... |.. .|--*=|=*== ... |+ =.|: :.|:.   @@@%|#*--|#%#@|#=%@ : . |: = |  . |:. .
   8 ++.*|+.++|.*+.|*+.+ - +:|. * |: .:|:: : @-:.|#=%-|=::-|-#=@ : :.|: - |-.-:|-. :
   9 =.++|.*+.|*+.+|+.*+ . . |-.. |: .=|. .: *++-|%-*=|+-+*|==** .   |.=* |..  | :  
  10 .**.|**.+|+.*+|.**: . :-|. :=|...:|. .- +=+#|*=*#|+=*#|*+*#    .| . .| .  |    
  11 ****|#++*|--:-|.    . .:|. .:|..- |: :  ***#|*+**|**=+|@#%@  .  |  . |  . |+.. 
  12 @@@@|@%-+|@#++|@%:. :  .|:.. | .:.|. .. +=+#|***#|++#%|*+*# *   |    | .  |    
  13 %@@@|@#::|%@+%|@#@% . :.|. .:|. ::|:.:: ++##|*++*|**+#|*+##     |. . |:   |-   
  14 @@@@|@%-=|@%++|@%:. - +:|=..+|= #-|: ** +=*#|**=#|==%@|+:-+ :  -|=. +|+ =.|.   
  15 %@@@|@#--|@%:-|%%:. * *=|% ==|# +=|= *+ *+*+|+-+*|-++#|+:-= @   |@   |=.: |: . 
  16 @@%@|@%==|@%++|@%:. @ @-|%..#|# @=|- %@ =:*+|++-+|=:#@|+.:- @  -|%. +|* *.|.   
  17 %@@@|@%:.|%%*%|@#@@ @ #+|@ *%|@:@@|= += -.*=|+.:=|=+.*|+.*+ @   |@ ..|@:  |: . 
  18 @%@@|@%-+|@%++|@%:: @ %-|%..#|# @+|: %@ +-*+|++-+|=.#@|= .- %  =|#. *|* *.|. . 
  19 %@%@|@#::|@%::|%%:: @ *=|@ *@|@.@@|+.+  +:*=|+..=|: .+|*+-+ @   |@ .
... [cut] ...
 |: % 
 152 %@%@|@%-=|@%=+|@%:. : *:|-...|*.#-|- #  +.**|++-=|= #@|+ :: . # |- = |  @.|: # 
 153 @@%@|@%..|%%+%|@#@@ + # |* + |= * |- *  - *=|+ :.|==.+|= += . % |+ # |  # |- @ 
 154 @@%@|@%-+|@%++|%%:. * *.|-.: |* %:|= #  +.+*|=+-=|= #@|+ :. . % |-.= |. %.|: # 
 155 %@@@|@#=-|%#:%|*-%% + # |+ : |-.:+|:.-. *.*=|+:==|--++|%+:: . % |* = |  =.|: % 
 156 %%:.|@%::|@%:.|%%:. : - |- = |+ * |+ #  - ==|=.--|: --|+ :: .=- |: # |. % |+ # 
 157 @%:.|%%:.|%#:.|=-   + @ |+ + |+ # |- =  : ::|+ :.|: .:|+    . % |+ % |. # |: @ 
 158 %%:.|%#..|##..|**.  @ * |- * |# * |+ #  . ::|-   |   .|-    @ @ |: # |. % |= #
```

```
$ KIT=tools/showkit; W="$KIT/work/robot"; cat > "$W/zoom.py" <<'EOF'
#!/usr/bin/env python3
# zoom.py out.png from_bar to_bar [flo fhi] : high-res log-frequency spectrogram with 16th grid
import sys, subprocess
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
out=sys.argv[1]; lo=float(sys.argv[2]); hi=float(sys.argv[3]); flo=float(sys.argv[4]) if len(sys.argv)>4 else 150; fhi=float(sys.argv[5]) if len(sys.argv)>5 else 6000
spb=0.468761; t0=0.003
ta=t0+lo*4*spb; tb=t0+hi*4*spb
mp3="shows/deadmau5 - Harder Better Faster Stronger.mp3"
SR=22050
raw=subprocess.run(["ffm ... [cut]
tools/showkit/songs/robot/z_0_8.png
tools/showkit/songs/robot/z_8_16.png
tools/showkit/songs/robot/z_24_32.png
```

```
$ KIT=tools/showkit; W="$KIT/work/robot"; cd "~/deadmau5 app"; for r in "32 40" "40 48" "48 56" "56 64" "64 72" "72 80" "80 88" "88 96"; do set -- $r; python3 "$W/zoom.py" "$W/z_$1_$2.png" $1 $2 >/dev/null; done; ls "$W"; date
Traceback (most recent call last):
  File "tools/showkit/songs/robot/zoom.py", line 7, in <module>
    out=sys.argv[1]; lo=float(sys.argv[2]); hi=float(sys.argv[3]); flo=float(sys.argv[4]) if len(sys.argv)>4 else 150; fhi=float(sys.argv[5]) if len(sys.argv)>5 else 6000
ValueError: could not convert string to float: '32 40'
Traceback (most recent call last):
  File "tools/showkit/songs/robot/zoom.py", line 7, in <module>
    out=sys.argv[1]; lo=float(sys.argv[2]); hi=float(sys.argv[3]); flo=float(sys.argv[4]) if len(sys.argv)>4 else 150; fhi=float(sys.argv[5]) if len(sys.argv)>5 else 6000
ValueError: could not convert string to float: '40 48'
Traceback (most recent call last):
  File "tools/showkit/songs/robot/zoom.py", line 7, in <module>
    out=sys.argv[1]; lo=float(sys.argv[2]); hi=float(sys.argv[3]); flo=float(sys.argv[4]) if len(sys.argv)>4 else 150; fhi=float(sys.argv[5]) if len(sys.argv)>5 else 6000
ValueError: could not convert string to float: '48 56'
Traceback (most recent call last):
  File "tools/showkit/songs/robot/zoom.py", line 7, in <module>
    out=sys.argv[1]; lo=float(sys.argv[2]); hi=float(sys.argv[3]); flo=float(sys.argv[4]) if len(sys.argv)>4 else 150; fhi=float(sys.argv[5]) if len(sys.argv)>5 else 6000
ValueError: could not convert string to float: '56 64'
Traceback (most recent call last):
  File "tools/showkit/songs/ro
... [cut] ...
):
  File "tools/showkit/songs/robot/zoom.py", line 7, in <module>
    out=sys.argv[1]; lo=float(sys.argv[2]); hi=float(sys.argv[3]); flo=float(sys.argv[4]) if len(sys.argv)>4 else 150; fhi=float(sys.argv[5]) if len(sys.argv)>5 else 6000
ValueError: could not convert string to float: '88 96'
roll.py
roll_air.txt
roll_mid.txt
roll_pres.txt
roll_sub.txt
spec_0_32.png
spec_128_160.png
spec_32_64.png
spec_64_96.png
spec_96_128.png
spec_all.png
z_0_8.png
z_24_32.png
z_8_16.png
zoom.py
Sat Oct 31 12:41:44 PDT 2026
```

```
$ KIT=tools/showkit; W="$KIT/work/robot"; cd "~/deadmau5 app"; for a in 32 40 48 56 64 72 80 88; do python3 "$W/zoom.py" "$W/z_${a}_$((a+8)).png" $a $((a+8)) >/dev/null; done; ls "$W" | wc -l; date
      23
Sat Oct 31 12:41:52 PDT 2026
```

```
$ cd "~/deadmau5 app"; wc -l mau5scene.py mau5engine.py mau5preview.py mau5show.py; grep -n "class \|^def " mau5scene.py | head -120
    1344 mau5scene.py
    1388 mau5engine.py
     214 mau5preview.py
    1000 mau5show.py
    3946 total
125:class TreatmentError(ValueError):
132:def treatment_path(base):
136:def load_treatment(base_or_path):
151:def grid_of(music):
190:def src_of(base):
203:def _helmet():
210:def _edge_mm(h):
215:class _Compiler:
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
789:def pal_lookup(stops, wrap, c):
808:def _pal_vec(P, c):
826:def _hash_sin(x):
830:def _h32(h):
844:def _gate(lb, pat, step, decay, floor, HB):
859:class _Val:
898:class Scenes:
1197:def bar_stats(music):
1220:def _row(r):
1225:def print_marks(base, music):
1240:def check(base, fps=25.0, verbose=True):
1303:def main(argv=None):
```

```
$ cd "~/deadmau5 app"; sed -n 80,520p mau5scene.py
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
             "wscale": 1.0, "wspeed": 0.0, "lo": 0.0, "hi": 1.0},
    "sweep": {"speed": 0.25, "width": 0.15, "soft": 0.1, "cgrad": 0.0,
              "from": 0.0, "to": 1.0},
    "sparks": {"rate": 1.0, "life": 1.0, "spread": 0.0, "nbr": 0.4},
    "blades": {"step": 1.0, "rise": 0.35, "keep": 0.15, "ctip": 1.0, "rim": 0.0},
    "preset": {},
    # A soft disc on the helmet's flat front view: x and y in mm (px, py), rad
    # and its soft edge in mm, wx and wy swinging it xf and yf times a beat with
    # phases xp and yp, cgrad moving the colour from middle to edge.
    "orb": {"x": 0.0, "y": 95.0, "rad": 50.0, "soft": 14.0, "wx": 0.0, "wy": 0.0,
            "xf": 0.125, "yf": 0.125, "xp": 0.0, "yp": 0.25, "cgrad": 0.0},
    # Every LED on its own slow sine: rate times a beat on average, sharp the
    # power that turns the crest into a glint, dens the share of LEDs that take
    # part, spread how far each LED's colour wanders from c.
    "twinkle": {"rate": 0.25, "sharp": 4.0, "spread": 0.0, "dens": 1.0},
}
FX_STATIC = {
    "fill": {},
    "grad": {"axis": "y", "axis2": "x", "wave": "tri"},
 
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
$ cd "~/deadmau5 app"; wc -l mau5scene.py mau5engine.py mau5preview.py mau5show.py; grep -n "class \|^def " mau5scene.py | head -120
    1344 mau5scene.py
    1388 mau5engine.py
     214 mau5preview.py
    1000 mau5show.py
    3946 total
125:class TreatmentError(ValueError):
132:def treatment_path(base):
136:def load_treatment(base_or_path):
151:def grid_of(music):
190:def src_of(base):
203:def _helmet():
210:def _edge_mm(h):
215:class _Compiler:
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
789:def pal_lookup(stops, wrap, c):
808:def _pal_vec(P, c):
826:def _hash_sin(x):
830:def _h32(h):
844:def _gate(lb, pat, step, decay, floor, HB):
859:class _Val:
898:class Scenes:
1197:def bar_stats(music):
1220:def _row(r):
1225:def print_marks(base, music):
1240:def check(base, fps=25.0, verbose=True):
1303:def main(argv=None):
```

```
$ cd "~/deadmau5 app"; sed -n 80,520p mau5scene.py
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
             "wscale": 1.0, "wspeed": 0.0, "lo": 0.0, "hi": 1.0},
    "sweep": {"speed": 0.25, "width": 0.15, "soft": 0.1, "cgrad": 0.0,
              "from": 0.0, "to": 1.0},
    "sparks": {"rate": 1.0, "life": 1.0, "spread": 0.0, "nbr": 0.4},
    "blades": {"step": 1.0, "rise": 0.35, "keep": 0.15, "ctip": 1.0, "rim": 0.0},
    "preset": {},
    # A soft disc on the helmet's flat front view: x and y in mm (px, py), rad
    # and its soft edge in mm, wx and wy swinging it xf and yf times a beat with
    # phases xp and yp, cgrad moving the colour from middle to edge.
    "orb": {"x": 0.0, "y": 95.0, "rad": 50.0, "soft": 14.0, "wx": 0.0, "wy": 0.0,
            "xf": 0.125, "yf": 0.125, "xp": 0.0, "yp": 0.25, "cgrad": 0.0},
    # Every LED on its own slow sine: rate times a beat on average, sharp the
    # power that turns the crest into a glint, dens the share of LEDs that take
    # part, spread how far each LED's colour wanders from c.
    "twinkle": {"rate": 0.25, "sharp": 4.0, "spread": 0.0, "dens": 1.0},
}
FX_STATIC = {
    "fill": {},
    "grad": {"axis": "y", "axis2": "x", "wave": "tri"},
 
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
$ cd "~/deadmau5 app"; sed -n 898,1195p mau5scene.py
class Scenes:
    """Renders a compiled `scenes` spec.  frame(t) -> (out, gain, label).

    Everything that can be worked out once is worked out here -- region
    index lists, axis values, palettes, preset instances -- so a frame is
    only arithmetic.  remote/offline/show.js has the same class.
    """

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
        idx 
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
$ cd "~/deadmau5 app"; sed -n 1240,1344p mau5scene.py; grep -n "_text_bitmap\|class TextScroll\|class Sprite\|class Eyes\|\"text\"\|\"sprite\"\|\"eyes\"" mau5engine.py | head
def check(base, fps=25.0, verbose=True):
    """Render a whole song through Scenes and a fresh guard, per scene.

    Peaks are allowed to go up; what must not happen is a loud run that
    fills the thermal bucket and leaves a later scene pinned at the
    sustained floor.  If one does, the fix is a lighter scene -- never a
    bigger burst_j, a ceiling or budget_ma.

    `heat` is how full the bucket got in the scene (the guard's
    full_pct): the allowance only starts to fall past 70%, and at 100%
    the scene is held to the sustained floor, which is flagged.
    """
    import mau5power
    show, music, _ = _show_and_music(base)
    spec = show.get("scenes")
    if not spec:
        raise TreatmentError("%s has no scenes compiled into it" % base)
    h = E.Helmet()
    sc = Scenes(spec, h)
    guard = mau5power.load(count=h.n)
    dur = float(show.get("duration", 0))
    n = int(dur * fps)
    per = {}
    order = []
    worst_ms = 0.0
    for i in range(n):
        t = i / fps
        t1 = time.perf_counter()
        out, gain, label = sc.frame(t, music)
        ms = (time.perf_counter() - t1) * 1000
        worst_ms = max(worst_ms, ms)
        _, rep = guard.apply(out, now=t, gain=gain)
        name = label.split(" · ")[0] or "(outside)"
        if name not in per:
            per[name] = {"ma": [], "heat": [], "allow": [], "ms": [], "t0": t}
            order.append(name)
        d = per[name]
        d["ma"].append(rep["sent_ma"])
        th = rep.get("thermal") or {}
        d["heat"].append(th.get("full_pct", 0.0))
        d["allow"].append(th.get("allowance_w", float("inf")))
        d["ms"].append(ms)
    th = guard.thermal
    floor_w = (max(th.sustained_w - th.standby_w, 0.0) if th is not None else 0.0)
    pinned = [nm for nm in order
              if t
... [cut] ...
 base in names(a.show):
            check(base, fps=a.fps)
    return 0


if __name__ == "__main__":
    sys.exit(main())
310:                out.append({"name": k, "kind": "text", "value": v})
580:def _text_bitmap(text, spacing=1):
674:class TextScroll(Preset):
676:    name = "text"
682:    params = {"text": "DEADMAU5", "color": (255, 160, 0), "bg": (0, 0, 0),
687:        bm = _text_bitmap(self.p["text"], spacing=1)
704:class SpriteShow(Preset):
713:    name = "sprite"
714:    params = {"sprite": "smile", "color": (0, 255, 255), "bg": (0, 0, 0),
722:        names = self.p["sprite"].split("|")
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
$ cd "~/deadmau5 app"; sed -n 898,1195p mau5scene.py
class Scenes:
    """Renders a compiled `scenes` spec.  frame(t) -> (out, gain, label).

    Everything that can be worked out once is worked out here -- region
    index lists, axis values, palettes, preset instances -- so a frame is
    only arithmetic.  remote/offline/show.js has the same class.
    """

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
        idx 
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
$ cd "~/deadmau5 app"; sed -n 1240,1344p mau5scene.py; grep -n "_text_bitmap\|class TextScroll\|class Sprite\|class Eyes\|\"text\"\|\"sprite\"\|\"eyes\"" mau5engine.py | head
def check(base, fps=25.0, verbose=True):
    """Render a whole song through Scenes and a fresh guard, per scene.

    Peaks are allowed to go up; what must not happen is a loud run that
    fills the thermal bucket and leaves a later scene pinned at the
    sustained floor.  If one does, the fix is a lighter scene -- never a
    bigger burst_j, a ceiling or budget_ma.

    `heat` is how full the bucket got in the scene (the guard's
    full_pct): the allowance only starts to fall past 70%, and at 100%
    the scene is held to the sustained floor, which is flagged.
    """
    import mau5power
    show, music, _ = _show_and_music(base)
    spec = show.get("scenes")
    if not spec:
        raise TreatmentError("%s has no scenes compiled into it" % base)
    h = E.Helmet()
    sc = Scenes(spec, h)
    guard = mau5power.load(count=h.n)
    dur = float(show.get("duration", 0))
    n = int(dur * fps)
    per = {}
    order = []
    worst_ms = 0.0
    for i in range(n):
        t = i / fps
        t1 = time.perf_counter()
        out, gain, label = sc.frame(t, music)
        ms = (time.perf_counter() - t1) * 1000
        worst_ms = max(worst_ms, ms)
        _, rep = guard.apply(out, now=t, gain=gain)
        name = label.split(" · ")[0] or "(outside)"
        if name not in per:
            per[name] = {"ma": [], "heat": [], "allow": [], "ms": [], "t0": t}
            order.append(name)
        d = per[name]
        d["ma"].append(rep["sent_ma"])
        th = rep.get("thermal") or {}
        d["heat"].append(th.get("full_pct", 0.0))
        d["allow"].append(th.get("allowance_w", float("inf")))
        d["ms"].append(ms)
    th = guard.thermal
    floor_w = (max(th.sustained_w - th.standby_w, 0.0) if th is not None else 0.0)
    pinned = [nm for nm in order
              if t
... [cut] ...
 base in names(a.show):
            check(base, fps=a.fps)
    return 0


if __name__ == "__main__":
    sys.exit(main())
310:                out.append({"name": k, "kind": "text", "value": v})
580:def _text_bitmap(text, spacing=1):
674:class TextScroll(Preset):
676:    name = "text"
682:    params = {"text": "DEADMAU5", "color": (255, 160, 0), "bg": (0, 0, 0),
687:        bm = _text_bitmap(self.p["text"], spacing=1)
704:class SpriteShow(Preset):
713:    name = "sprite"
714:    params = {"sprite": "smile", "color": (0, 255, 255), "bg": (0, 0, 0),
722:        names = self.p["sprite"].split("|")
```

```
$ cd "~/deadmau5 app"; sed -n 575,800p mau5engine.py; grep -n "SPRITES\|sprites.json" mau5fx.py | head -20; grep -n "class Helmet" -A70 mau5engine.py | sed -n 1,130p
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
re.
102-        # It is monotonic in screen x, so nothing can read backwards, and
103-        # the ears no longer depend on the one coordinate a single camera
104-        # cannot measure.
105-        self.fa = np.degrees(np.arctan2(self.px, np.abs(self.px[self.shell]).max()))
106-        self.nfa = self._norm(self.fa)
107-        sh_el = self.el[self.shell]
108-        self.nel = np.clip((self.el - sh_el.min()) / (np.ptp(sh_el) or 1), 0, 1)
109-
110-        # Polar coordinates about the centre of whatever part the LED
111-        # belongs to: angle `ea` in 0..1 anticlockwise, radius `er` in
```

```
$ KIT=tools/showkit; W="$KIT/work/robot"; cd "~/deadmau5 app"; time python3 "$KIT/sheet.py" "TIKI TIKI - Slowed" "$W/tiki.png" 5:hook 11:idolb 27.5:title 31.2:verse 39.0:big 39.25:big 61:water 113:duel 153:final 155:final 169:wind 176:out; python3 - <<'EOF'
import sys,os
sys.path.insert(0,os.getcwd())
import numpy as np, mau5engine as E
h=E.Helmet()
s=h.shell
print("n",h.n,"shell",s.sum())
print("px range",h.px[s].min(),h.px[s].max(),"py range",h.py[s].min(),h.py[s].max())
print("ears px",h.px[h.ear1].min(),h.px[h.ear1].max(),h.px[h.ear2].min(),h.px[h.ear2].max(),"py",h.py[h.ears].min(),h.py[h.ea ... [cut]
bar 5       hook           shell max 130 mean  13.3   ears max 224 mean  70.3   hook · LIT
bar 11      idolb          shell max  61 mean  22.9   ears max 153 mean  32.1   hookb
bar 27.5    title          shell max 221 mean  41.8   ears max  31 mean   8.4   still · TIKI TIKI
bar 31.2    verse          shell max 122 mean  22.3   ears max  28 mean  18.0   verse · VERSE
bar 39      big            shell max 130 mean  24.0   ears max 224 mean  77.0   big · IDOL
bar 39.25   big            shell max 232 mean  48.7   ears max 135 mean  46.5   big · IDOL
bar 61      water          shell max   0 mean   0.0   ears max   0 mean   0.0   lagoon2
bar 113     duel           shell max 114 mean  11.5   ears max 248 mean  78.5   duel2 · SWAP
bar 153     final          shell max 249 mean  94.1   ears max 235 mean  96.3   final · FINAL
bar 155     final          shell max  61 mean  27.9   ears max 255 mean  40.3   final
bar 169     wind           shell max  69 mean  16.7   ears max  87 mean  23.0   final2
bar 176     out            shell max  19 mean   4.0   ears max  52 mean   4.2   out
tools/showkit/songs/robot/tiki.png (1800, 490)
python3 "$KIT/sheet.py" "TIKI TIKI - Slowed" "$W/tiki.png" 5:hook 11:idolb     0.29s user 0.03s system 97% cpu 0.335 total
n 621 shell 398
px range -170.94 170.95 py range -111.27 167.77
ears px -388.21 -55.76 55.56 387.42 py 51.8 384.91
  180  . . . . . . 1 . . 1 2 . . . . . . . . . .
  162  . . . . . 5 4 3 3 3 2 3 2 5 4 . . . . . .
  144  . . . 4 8 5 4 4 3 4 4 3 4 4 5 8 4 . . . .
  126  . . 1 5 2 . 2 2 1 2 2 1 2 2 . 2 5 1 . . .
  108  . 2 9 4 4 3 4 2 4 2 2 4 2 4 3 4 4 9 2 . .
   90  . 4 3 2 1 2 1 1 2 1 1 2 1 1 2 1 2 3 4 . .
   72  . 5 2 2 2 1 1 2 1 1 1 1 2 1 1 2 2 2 5 . .
  
... [cut] ...
 . . . . . 2 5 .
  -54  . 5 1 . . . . . . . . . . . . . . 1 5 . .
  -72  . 3 3 2 . . . . . . . . . . . . 2 3 3 . .
  -90  . . 5 3 2 . . . . . . . . . . 2 3 5 . . .
 -108  . . 3 4 2 2 1 2 1 . . 1 2 1 2 2 4 3 . . .
nel at py: [(-100, 0.05), (-50, 0.19), (0, 0.38), (30, 0.43), (60, 0.52), (90, 0.62), (120, 0.71), (150, 0.86), (170, 1.0)]
nfa at px: [(-170, 0.16), (-100, 0.27), (-50, 0.38), (0, 0.49), (50, 0.62), (100, 0.73), (170, 0.84)]
ear1 side px mean -221.961875 ear2 225.43216216216217
nfa ear1 0.0 0.36374357186477674 ear2 0.6361240549130386 1.0
nel ears 0.4425932320441989 0.9454419889502763
```

```
$ KIT=tools/showkit; W="$KIT/work/robot"; cd "~/deadmau5 app"; for a in 92 108 124 140; do python3 "$W/zoom.py" "$W/y_${a}.png" $a $((a+16)) >/dev/null; done; python3 "$W/zoom.py" "$W/y_16.png" 16 24 >/dev/null; date
Sat Oct 31 12:44:22 PDT 2026
```

```
$ cd "~/deadmau5 app"; python3 - <<'EOF'
import sys,os
sys.path.insert(0,os.getcwd())
import numpy as np, mau5engine as E
h=E.Helmet()
s=h.shell
# LED rows: histogram of py
ys=np.round(h.py[s]/3)*3
vals,c=np.unique(ys,return_counts=True)
print([(int(v),int(n)) for v,n in zip(vals,c)])
g=h.group[s]
for gid in np.unique(g):
    m=g==gid
    print("group",gid,"n",m.sum(),"px %.0f..%.0f py %.0f..%.0f"%(h.px[s][m].min(),h.px[s][m].max(),h.py[s][m].min(),h.py[s][m].max()))
print("tubes per ear", [(t,(h.tube[h.ear1]==t).sum()) for t in (0,1,2)], "rim1",(h.rims&h.ear1).sum())
print("ear rim er",h.er[h.rims&h.ear1][:3],"ea",h.ea[h.rims&h.ear1][:5])
print("shell er",h.er[s].min(),h.er[s].max( ... [cut]
[(-111, 30), (-99, 20), (-84, 16), (-69, 12), (-54, 8), (-36, 6), (-21, 2), (12, 2), (30, 12), (45, 22), (60, 34), (75, 34), (90, 34), (105, 34), (117, 30), (129, 30), (141, 34), (150, 17), (156, 17), (162, 3), (168, 1)]
group 0 n 6 px -169..-132 py -111..-37
group 1 n 7 px -170..-131 py -111..-21
group 2 n 6 px -164..-129 py -111..-37
group 3 n 5 px -156..-126 py -111..-53
group 4 n 4 px -145..-121 py -111..-69
group 5 n 4 px -139..-116 py -111..-69
group 6 n 3 px -125..-109 py -111..-84
group 7 n 3 px -116..-102 py -111..-84
group 8 n 2 px -101..-94 py -111..-98
group 9 n 2 px -91..-85 py -111..-98
group 10 n 1 px -75..-75 py -111..-111
group 11 n 1 px -64..-64 py -111..-111
group 12 n 1 px -54..-54 py -111..-111
group 13 n 1 px -42..-42 py -111..-111
group 14 n 1 px -30..-30 py -111..-111
group 15 n 1 px 30..30 py -111..-111
group 16 n 1 px 42..42 py -111..-111
group 17 n 1 px 54..54 py -111..-111
group 18 n 1 px 64..64 py -111..-111
group 19 n 1 px 75..75 py -111..-111
group 20 n 2 px 85..91 py -111..-98
group 21 n 2 px 94..101 py -111..-98
group 22 n 3 px 102..116 py -111..-84
group 23 n 3 px 109..125 py -111..-84
group 24 n 4 px 116..139 py -111..-69
group 25 n 4 px 121..145 py -111..-69
group 26 n 5 px 126..156 py -111..-53
group 27 n 6 px 129..164 py -111..-37
group 28 n 7 px 131..170 py -111..-21
group 29 n 6 px 132..169 py -111..-37
group 30 n 9 px 102..170 py 29..140
group 31 n 12 px 73..171 py 12..157
group 32 n 9 px 100..166 py 29..140
group 33 n 11 px 70..162 py 29..157
group 34 n 9 px 94..156 py 29..140
group 35 n 11 px 64..149 py 29..157
group 36 n 8 px 84..138 py 45..140
group 37 n 10 px 57..129 py 45..157
group 38 n 1 px 72..72 py 140..140
group 39 n 5 px 97..118 py 45..105
group 40 n 5 px 88..107 py 45..105
group 41 n 3 px 47..65 py 140..157
group 42 
... [cut] ...
 OSError:
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
    rows = SPRITES[name_or_rows] if isinstance(name_or_rows, str) else name_or_rows
```

```
$ cd "~/deadmau5 app"; sed -n 160,185p remote/offline/engine.js; sed -n 455,490p remote/offline/engine.js; python3 - <<'EOF'
import sys,os
sys.path.insert(0,os.getcwd())
import numpy as np, mau5engine as E
h=E.Helmet()
s=h.shell
print("dome 9 rows of 13mm from y=172, 17 cols of 20.1 mm")
for r in range(9+3):
    hi=172-13*r; lo=hi-13
    row=""
    for c in range(17):
        x0=-171+c*342/17; x1=x0+342/17
        n=((h.px>=x0)&(h.px<x1)&(h.py<hi)&(h.py>=lo)&s).sum()
        row+="%2d"%n if n else " ."
    print("%2d y %4d..%4d %s  [%d]"%(r,lo,hi,row,((h.py<hi)&(h.py>=lo)&s).sum()))
print("jaw")
for hi,lo in ((-30,-50),(-50,-62),(-62,-76),(-76,-92),(-92,-104),(-104,-116)):
    row=" ... [cut]
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
function paint(bm, rowf, colf, mask, n, wrap, reach, rowW) {
  reach = reach === undefined ? 1.4 : reach;
  rowW = rowW === undefined ? 1.0 : rowW;
  const rows = bm.rows, cols = bm.cols;
  const lit = new Uint8Array(n);
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
    if (this.p.blink && fract(t * this.p.blink) > 0.5) 
... [cut] ...
   55..  68  4 3 2 2 1 2 1 1 2 1 1 2 1 2 2 3 4  [34]
 9 y   42..  55  5 2 2 2 . . . . . . . . . 2 2 2 5  [22]
10 y   29..  42  . . . . . . . . . . . . . . . . .  [0]
11 y   16..  29  5 1 . . . . . . . . . . . . . 1 5  [12]
jaw
   y  -50.. -30  3 . . . . . . . . . . . . . . . 3
   y  -62.. -50  4 . . . . . . . . . . . . . . . 4
   y  -76.. -62  3 3 . . . . . . . . . . . . . 3 3
   y  -92.. -76  1 5 2 . . . . . . . . . . . 2 5 1
   y -104.. -92  . 4 3 3 . . . . . . . . . 3 3 4 .
   y -116..-104  . 2 4 3 2 2 2 . . . 2 2 2 3 4 2 .
96:            "sprites": {k: list(v) for k, v in SPRITES.items()},
```

```
$ KIT=tools/showkit; W="$KIT/work/robot"; cat > "$W/gen_sprites.py" <<'EOF'
#!/usr/bin/env python3
"""The Robot's sprites, on the dome's own grid: 17 columns x 9 rows over y 55..172, x +-171,
where every row of the sprite holds exactly one row of LEDs."""
import json, os, sys
import numpy as np
BASE = "deadmau5 - Harder Better Faster Stronger"
OUT = os.path.join("shows", "scenes", BASE + ".sprites.json")
R, C = 9, 17
def blank():
    return np.zeros((R, C), bool)
def rows(a):
    return ["".join("#" if v else "." for v in r) for r in a]
S = {}
def put(name, a):
    S["robot_" + name] = rows(a)
# the pyramid ... [cut]
wrote shows/scenes/deadmau5 - Harder Better Faster Stronger.sprites.json 41 sprites 8516 bytes
tools/showkit/songs/robot/sp1.png (1800, 338)
```

```
$ cd "~/deadmau5 app"; sed -n 859,897p mau5scene.py; grep -n "class Music" -A40 mau5show.py | grep -n "def \|bass\|punch" | head -30; grep -n "def band\|def level\|def punch\|def b_\|punch" mau5show.py | head -30; grep -n "band\b\|\.band\|punch" remote/offline/show.js | head -20; KIT=tools/showkit; W="$KIT/work/robot"; cat > "$W/fold2.py" <<'EOF'
import sys, os, re
import numpy as np
KIT=os.environ["KIT"]
z=np.load(os.path.join(KIT,"work",re.sub(r"\W+","_","deadmau5 - Harder Better Faster Stronger.mp3")+".env.npz"))
tt=z["tt"]; spb=0.468761; t0=0.003
CH=" .:-=+*#%@"
def fold(lo,hi,L=32,bands=("su ... [cut]
class _Val:
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


10:99-    def __init__(self, path, fps=40, verbose=False, cache=None):
191:    def band_at(self, t, name="bass", punch=False):
192:        """0..1 for one band at one instant: loudness, or its punch."""
196:        arr = b[name][1 if punch else 0]
245:    def level_at(self, t):
281:    def bands_at(self, t, n):
760:            drive = self.music.band_at(t, band, punch=bool(ov.get("punch", True)))
172:    if (ov.band && music && music.bandAt) {
174:      const punch = ov.punch === undef
... [cut] ...
#.|+: :|@..#|::*.
   bass    #.*:|%- %|@ =.|= .:|@.*.|#...|%..=|-.+.
   lowmid  * +.|*- +|% +-|- ..|@ = |* ..|%. -|- =.
   mid     @.+.|#. +|@ %=|- +=|% # |@ =-|*.--|+ *-
   pres    + #-|+...|+ @+|- #:|= %-|* +.|-.*#|= #.
   air     . *.|=.- |. #.|: * |  # |+ * |  + |: @ 
bars 140-156, 32 steps
   sub     +.=.|#..*|@..:|%. :|@.#.|+: :|@.:%|-.+.
   bass    *.*:|%- #|@ =.|=   |@.*.|#.  |%..=|=.=.
   lowmid  + +.|+- +|% +-|: . |@ + |* . |%..-|- -.
   mid     % + |*. +|@ #=|- - |% * |# : |#.:-|= :.
   pres    # #.|+::.|# @=|= %.|# @ |# +.|+:*-|=.*.
   air     - # |-.- |. %.|: # |. % |* * |  * |: @
```

```
$ date; cd "~/deadmau5 app"; sed -n 844,858p mau5scene.py; sed -n 540,600p remote/offline/show.js; python3 - <<'EOF'
import sys,os
sys.path.insert(0,os.getcwd())
import numpy as np, mau5engine as E
h=E.Helmet()
for e,nm in ((h.ear1,"ear1"),(h.ear2,"ear2")):
    for t in (0,1,2):
        m=e&(h.tube==t)
        print(nm,"tube",t,"n",m.sum(),"u %.3f..%.3f"%(h.u[m].min(),h.u[m].max()),"ea %.2f..%.2f"%(h.ea[m].min(),h.ea[m].max()),"er %.2f..%.2f"%(h.er[m].min(),h.er[m].max()),"al %.2f..%.2f"%(h.along[m].min(),h.along[m].max()), "px %.0f..%.0f py %.0f..%.0f"%(h.px[m].min(),h.px[m].max(),h.py[m].min(),h.py[m].max()))
    m=e&h.rims
    print(nm,"rim n",m.sum(),"u %.3f..%.3f"%(h.u[m].min() ... [cut]
Sat Oct 31 12:53:59 PDT 2026
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
          const i = idx[m];
          const d = A[i] - pos;
          let k;
          if (band) { const q = 1 - Math.abs(d) / width; k = q > 0 ? q * q : 0; }
          else k = sclamp(0.5 - d / soft, 0, 1);
          this._pal(P, c0 + cgrad * A[i]);
          this._put(mix, i, G * k);
        }
        break;
      }
      case 'sparks': {
        const r = valAt(P.rate, p, bar, music, tt);
        if (r <= 0) return;
        const life = valAt(P.life, p, bar, music, tt);
       
... [cut] ...
al 0.05..0.92 px 207..358 py 70..214
ear2 tube 1 n 36 u 0.308..0.692 ea 0.07..0.70 er 0.04..0.75 al 0.15..0.97 px 133..322 py 127..306
ear2 tube 2 n 28 u 0.000..0.297 ea 0.24..0.51 er 0.50..0.81 al 0.09..0.95 px 83..237 py 205..349
ear2 rim n 19 u 0.000..1.000 ea 0.02..0.98 al 0.03..0.97
shell u 0.000..1.000
jaw n 96 nfa 0.16..0.84 ea 0.54..0.96
jaw ea near centre [0.68 0.69 0.7  0.71 0.72 0.78 0.79 0.8  0.81 0.82]
60 34 nel 0.524
75 34 nel 0.571
90 34 nel 0.619
105 34 nel 0.667
117 30 nel 0.714
129 30 nel 0.762
141 34 nel 0.810
150 17 nel 0.857
156 17 nel 0.905
162 3 nel 0.952
168 1 nel 1.000
```

```
$ KIT=tools/showkit; W="$KIT/work/robot"; cat > "$W/gen_sprites.py" <<'EOF'
#!/usr/bin/env python3
"""The Robot's sprites, on the dome's own grid: 17 columns x 9 rows over y 55..172, x +-171,
where every row of the sprite holds exactly one row of LEDs (row 0 only four of them)."""
import json, os, subprocess, sys
import numpy as np
BASE = "deadmau5 - Harder Better Faster Stronger"
OUT = os.path.join("shows", "scenes", BASE + ".sprites.json")
R, C = 9, 17
SPB, T0 = 0.468761, 0.003
def blank(r=R, c=C):
    return np.zeros((r, c), bool)
def rows(a):
    return ["".join("#" if v else "." for v in r) for r in a] ... [cut]
wrote shows/scenes/deadmau5 - Harder Better Faster Stronger.sprites.json 123 sprites 18679 bytes
########.########
#######...#######
#######...#######
######.....######
###.#.......#.###
###...........###
#...............#
.................
.................

########.########
#######...#######
######.....######
####.#.....#.####
###...........###
##.............##
#...............#
.................
.................

[[1.   1.   0.74 0.5  0.52 0.68 0.32 0.83 0.51]
 [0.85 0.84 0.58 0.34 0.36 0.52 0.16 0.67 0.35]
 [0.81 0.68 0.64 0.69 0.37 0.36 0.34 0.65 0.48]
 [0.89 0.6  0.83 0.82 0.36 0.4  0.26 0.49 0.32]
 [0.95 0.9  0.67 0.66 0.23 0.47 0.68 0.4  0.17]
 [0.79 0.74 0.87 0.98 0.8  0.55 1.   0.54 0.12]
 [0.63 0.58 0.71 0.82 1.   0.68 0.93 0.98 0.89]
 [0.47 0.65 1.   0.74 0.92 0.81 0.77 0.82 0.73]
 [0.99 0.99 0.84 0.58 0.76 0.65 0.61 0.66 0.57]
 [0.83 0.83 0.68 0.42 0.6  0.49 0.45 0.5  0.41]
 [0.67 0.67 0.77 0.98 0.61 0.46 0.42 0.85 0.8 ]
 [0.51 0.72 0.94 0.9  0.63 0.91 0.55 0.69 0.64]
 [0.97 0.94 0.78 0.74 0.47 0.75 0.59 0.53 0.48]
 [0.81 0.78 0.62 0.58 0.31 0.59 0.43 0.37 0.64]
 [0.65 0.62 0.46 0.51 1.   0.43 0.98 0.99 0.92]
 [0.49 0.46 0.37 0.35 1.   0.63 0.82 0.86 0.76]]
```

```
$ KIT=tools/showkit; W="$KIT/work/robot"; cat > "$W/gen.py" <<'EOF'
#!/usr/bin/env python3
"""THE ROBOT: the treatment for deadmau5's live Harder Better Faster Stronger."""
import json, os, sys
KIT = "tools/showkit"
sys.path.insert(0, KIT)
from fmt import save
BASE = "deadmau5 - Harder Better Faster Stronger"
SPB = 0.468761
RED, GREEN, BLUE, WHITE = [255, 0, 0], [0, 255, 0], [0, 70, 255], [255, 255, 255]
INK = [5, 0, 0]            # near black: a stencil, painted over, hides what is under it
DOME = {"y_lo": 55, "y_hi": 1 ... [cut]
wrote shows/scenes/deadmau5 - Harder Better Faster Stronger.scene.json scenes 23 hits 52
     158   296.26s  energy 0.29  bass 0.33 (punch 1.00)  mid 0.13  high 0.29
     159   298.13s  energy 0.20  bass 0.28 (punch 1.00)  mid 0.08  high 0.20
  end        bar 160
     159   298.13s  energy 0.20  bass 0.28 (punch 1.00)  mid 0.08  high 0.20
Traceback (most recent call last):
  File "mau5scene.py", line 1344, in <module>
    sys.exit(main())
  File "mau5scene.py", line 1336, in main
    attach(base)
  File "mau5scene.py", line 582, in attach
    spec = compile_show(base, verbose=verbose)
  File "mau5scene.py", line 575, in compile_show
    raise TreatmentError("%s does not pass:\n  %s" % (base, "\n  ".join(errs)))
__main__.TreatmentError: deadmau5 - Harder Better Faster Stronger does not pass:
  scene hats has 7 layers, 6 at most
```

```
$ KIT=tools/showkit; W="$KIT/work/robot"; cd "~/deadmau5 app"; python3 - <<'EOF'
import os
W=os.environ.get("W")
EOF
python3 - "$W/gen.py" <<'EOF'
import sys
p=sys.argv[1]; s=open(p).read()
s=s.replace('''stack(0.22), stencil(frames("st_tile", 4, 1), 1 / SPB), eye(4)] + kit()})''','''stack(0.22), stencil(frames("st_tile", 4, 1), 1 / SPB), eye(4)] + kit(rim=0)})
H({"name": "HATS KICK", "at": "hats", "beats": 32, "layers": [fill("rims", "white", 0.5, KICK, decay=0.6)]})''')
open(p,"w").write(s)
EOF
python3 "$W/gen.py" && python3 mau5scene.py compile "deadmau5 - Harder Better Faster Stronger" 2>&1 | ... [cut]
wrote shows/scenes/deadmau5 - Harder Better Faster Stronger.scene.json scenes 23 hits 53
  o4         bar 159
     158   296.26s  energy 0.29  bass 0.33 (punch 1.00)  mid 0.13  high 0.29
     159   298.13s  energy 0.20  bass 0.28 (punch 1.00)  mid 0.08  high 0.20
  end        bar 160
     159   298.13s  energy 0.20  bass 0.28 (punch 1.00)  mid 0.08  high 0.20
deadmau5 - Harder Better Faster Stronger: 24 scenes, 53 hits, written into shows/deadmau5 - Harder Better Faster Stronger.json
bar 1       HARDER         shell max 255 mean  24.8   ears max 102 mean   4.5   boot H · HARDER
bar 1.2                    shell max 255 mean  23.2   ears max 102 mean   5.5   boot H · HARDER
bar 3       BETTER         shell max 255 mean  20.3   ears max 102 mean   7.4   boot B · BETTER
bar 5       FASTER         shell max 255 mean  29.9   ears max 128 mean  11.8   boot F · FASTER
bar 7       STRONGER       shell max 178 mean  43.7   ears max 102 mean  16.9   boot S · STRONGER
bar 9       test           shell max 230 mean   9.1   ears max  48 mean  22.0   test
bar 11      test           shell max 230 mean  11.5   ears max  84 mean  39.0   test
bar 11.8    fall           shell max 159 mean   6.9   ears max   0 mean   0.0   test · fall 1
bar 12      on             shell max 255 mean  17.8   ears max 204 mean 107.6   on · ON
bar 12.25                  shell max 255 mean  26.9   ears max 166 mean  80.3   on · ON
bar 13                     shell max 230 mean  13.5   ears max 128 mean  31.1   on
bar 14                     shell max 230 mean  13.5   ears max 128 mean  31.1   on
bar 20      hats           shell max 230 mean  13.6   ears max 204 mean  63.6   hats · HATS KICK · HATS
bar 20.5                   shell max 230 mean  12.2   ears max 128 mean  31.1   hats · HATS KICK
bar 22                
... [cut] ...
an  27.9   ears max 153 mean  34.0   final
bar 156     off            shell max 230 mean   8.9   ears max  51 mean  15.3   off1
bar 157                    shell max 230 mean   7.0   ears max  31 mean   9.2   off2
bar 158                    shell max 153 mean   4.8   ears max  20 mean   1.8   off3
bar 159                    shell max 102 mean   0.8   ears max   0 mean   0.0   off4
bar 159.5                  shell max 102 mean   0.7   ears max   0 mean   0.0   off4
tools/showkit/songs/robot/s1.png (1800, 2695)
```

```
$ date; KIT=tools/showkit; W="$KIT/work/robot"; cd "~/deadmau5 app"; B="deadmau5 - Harder Better Faster Stronger"; python3 mau5scene.py check "$B" 2>&1 | tail -32; python3 "$KIT/sheet.py" "$B" "$W/s2.png" 12.1:on 13.5 20.1:hats 21 21.25 28.5:voice 60.1:pump 69 92.3:peak 97 109:stack 125:bare > /dev/null
Sat Oct 31 12:58:21 PDT 2026
deadmau5 - Harder Better Faster Stronger: 7477 frames at 25 fps through the guard
  scene            from  mean mA   p95 mA     heat   allow W      ms
  dark             0.0s        0        0     0.0%      18.1    0.02
  boot H           0.0s      203      278     0.0%      18.1    0.22
  boot B           3.8s      247      321     0.0%      18.1    0.22
  boot F           7.5s      380      501     0.2%      18.1    0.23
  boot S          11.3s      529      678     0.5%      18.1    0.27
  test            15.0s      436      766     1.0%      18.1    0.20
  on              22.5s      394      870     1.5%      18.1    0.20
  hats            37.5s      394      877     2.1%      18.1    0.19
  voice           52.5s      411      746     3.5%      18.1    0.23
  down            82.5s      223      296     3.5%      18.1    0.19
  charge          97.5s      494      939     4.2%      18.1    0.23
  pump           112.5s      327      573     4.4%      18.1    0.13
  dot            127.5s      395      830     5.0%      18.1    0.13
  talk           142.5s      452      585     6.0%      18.1    0.24
  talk2          157.5s      592      744     6.9%      18.1    0.22
  talk3          165.0s      719     1000     8.2%      18.1    0.18
  peak           172.5s      884     1000    15.2%      18.1    0.23
  stack          202.5s      439      800    16.9%      18.1    0.23
  bare           232.5s      454      817    18.8%      18.1    0.17
  final          262.5s      826     1000    25.2%      18.1    0.20
  off1           292.5s      410      415    25.3%      18.1    0.18
  off2           294.4s      272      278    25.3%      18.1    0.18
  off3           296.3s      123      129    25.2%      18.1    0.17
  off4           298.2s       13       15    25.1%      18.1    0.05
  worst frame 1.25 ms; no scene reaches the sustained floor
```

```
$ cd "~/deadmau5 app"; grep -n "_put" remote/offline/show.js | head -5; sed -n "$(grep -n '_put(mix' remote/offline/show.js | head -1 | cut -d: -f1),+12p" remote/offline/show.js | head -5; grep -n "  _put(" -A14 remote/offline/show.js | head -30; KIT=tools/showkit; python3 "$KIT/../kit/grid.py" check "deadmau5 - Harder Better Faster Stronger" | tail -1; python3 mau5scene.py check "TIKI TIKI - Slowed" 2>&1 | sed -n 2,14p; export KIT; python3 - <<'EOF'
import os,re
import numpy as np
KIT=os.environ["KIT"]
z=np.load(os.path.join(KIT,"work",re.sub(r"\W+","_","deadmau5 - Harder Better Faster Stronger. ... [cut]
499:  _put(mix, i, w) {
523:        for (let m = 0; m < nm; m++) this._put(mix, idx[m], w);
542:          this._put(mix, i, G * 1);
567:          this._put(mix, i, G * k);
600:          this._put(mix, idx[m], G * K[m]);
  _put(mix, i, w) {
    const acc = this.acc, rgb = this.rgb, b = i * 3;
    const v0 = w * rgb[0], v1 = w * rgb[1], v2 = w * rgb[2];
    if (mix === 0) { acc[b] += v0; acc[b + 1] += v1; acc[b + 2] += v2; }
    else if (mix === 1) {
499:  _put(mix, i, w) {
500-    const acc = this.acc, rgb = this.rgb, b = i * 3;
501-    const v0 = w * rgb[0], v1 = w * rgb[1], v2 = w * rgb[2];
502-    if (mix === 0) { acc[b] += v0; acc[b + 1] += v1; acc[b + 2] += v2; }
503-    else if (mix === 1) {
504-      if (v0 > acc[b]) acc[b] = v0;
505-      if (v1 > acc[b + 1]) acc[b + 1] = v1;
506-      if (v2 > acc[b + 2]) acc[b + 2] = v2;
507-    } else if (Math.max(v0, v1, v2) > 4) { acc[b] = v0; acc[b + 1] = v1; acc[b + 2] = v2; }
508-  }
509-
510-  _render(P, B, bar, lb, span, p, music, tt) {
511-    const gate = P.gate
512-      ? patGate(lb, P.gate.pat, P.gate.step, P.gate.decay, P.gate.floor, this.HB) : 1;
513-    const ein = P.ein > 0 ? sclamp(lb / P.ein, 0, 1) : 1;
worst 3 ms where the music is clear enough to say, mean -0.1 ms
  scene            from  mean mA   p95 mA     heat   allow W      ms
  (outside)        0.0s        0        0     0.0%      18.1    0.00
  dark             0.1s        0        0    18.7%      18.1    0.01
  embers           0.5s       31       46     0.0%      18.1    0.05
  hush             5.3s       27       38     0.0%      18.1    0.05
  lighting         7.0s      199      436     0.0%      18.1    0.09
  hook            10.5s      643      886     1.0%      18.1    0.11
  hookb           17.5s      640      862     1.9%      18.1    0.17
 
... [cut] ...
1.8%      18.1    0.10
  hook2           27.9s      636      891     3.2%      18.1    0.22
  burn            38.4s      392      815     3.6%      18.1    0.11
  lagoon          45.3s      182      307     3.5%      18.1    0.09
sub 8 12 3-step fold from section start [0.591 0.184 0.16 ]
sub 68 76 3-step fold from section start [0.3   0.319 0.289]
bass 8 12 3-step fold from section start [0.664 0.114 0.076]
bass 68 76 3-step fold from section start [0.333 0.32  0.313]
lowmid 8 12 3-step fold from section start [0.462 0.248 0.345]
lowmid 68 76 3-step fold from section start [0.182 0.249 0.206]
```

```
$ KIT=tools/showkit; W="$KIT/work/robot"; cat > "$W/gen_sprites.py" <<'EOF'
#!/usr/bin/env python3
"""The Robot's sprites, on the dome's own grid: 17 columns x 9 rows over y 55..172, x +-171,
where every row of the sprite holds exactly one row of LEDs (row 0 only four of them)."""
import json, os, subprocess, sys
sys.path.insert(0, os.getcwd())
import numpy as np
import mau5engine as E
BASE = "deadmau5 - Harder Better Faster Stronger"
OUT = os.path.join("shows", "scenes", BASE + ".sprites.json")
R, C = 9, 17
SPB, T0 = 0.468761, 0.003
h = E.Helmet()
# which cells of the grid hold an LED: a stencil never sets ... [cut]
wrote shows/scenes/deadmau5 - Harder Better Faster Stronger.sprites.json 190 sprites 32780 bytes
.....#.##........
....#########....
...###########...
..#############..
..#############..
.###############.
.###############.
#################
#################
wrote shows/scenes/deadmau5 - Harder Better Faster Stronger.scene.json scenes 26 hits 69
  hit PUMP overlaps 2 other hits
  hit DOT overlaps 2 other hits
  hit fall 3 overlaps 2 other hits
```

```
$ KIT=tools/showkit; W="$KIT/work/robot"; cd "~/deadmau5 app"; B="deadmau5 - Harder Better Faster Stronger"; sed -i '' 's/"name": "PUMP", "at": "pump", "beats": 64/"name": "PUMP", "at": "pump", "beats": 32/' "$W/gen.py"; python3 "$W/gen.py" && python3 mau5scene.py compile "$B" 2>&1 | tail -4 | cut -c1-200; python3 "$KIT/sheet.py" "$B" "$W/s3a.png" 1:HARDER 3:BETTER 5:FASTER 7:STRONGER 8.1:test 8.3 8.5 8.8 10.1 10.6 11.2 11.8:fall 12:on 12.25 12.6 13 14 15.25 20:hats 21.25 21.5 23 27.6:fall 27.9 | cut -c1-110; python3 "$KIT/sheet.py" "$B" "$W/s3b.png" 28:voice 28.3 28.6 29.1 29.6 30.5:word 31 31.8 ... [cut]
wrote shows/scenes/deadmau5 - Harder Better Faster Stronger.scene.json scenes 26 hits 69
     159   298.13s  energy 0.20  bass 0.28 (punch 1.00)  mid 0.08  high 0.20
  end        bar 160
     159   298.13s  energy 0.20  bass 0.28 (punch 1.00)  mid 0.08  high 0.20
deadmau5 - Harder Better Faster Stronger: 27 scenes, 69 hits, written into shows/deadmau5 - Harder Better Faster Stronger.json
bar 1       HARDER         shell max 255 mean  25.8   ears max 102 mean   4.5   boot H · HARDER
bar 3       BETTER         shell max 255 mean  20.8   ears max 102 mean   7.2   boot B · BETTER
bar 5       FASTER         shell max 255 mean  31.3   ears max  32 mean   9.5   boot F · FASTER
bar 7       STRONGER       shell max 178 mean  45.5   ears max  27 mean   8.1   boot S · STRONGER
bar 8.1     test           shell max 230 mean   7.6   ears max  40 mean  14.3   test
bar 8.3                    shell max 230 mean   8.2   ears max  37 mean  16.4   test
bar 8.5                    shell max 230 mean   8.0   ears max  45 mean  17.6   test
bar 8.8                    shell max 230 mean  13.2   ears max  85 mean  33.7   test
bar 10.1                   shell max 230 mean  11.7   ears max  65 mean  23.0   test2
bar 10.6                   shell max 230 mean  10.2   ears max 139 mean  45.5   test2
bar 11.2                   shell max 230 mean  13.4   ears max 101 mean  40.0   test2
bar 11.8    fall           shell max 159 mean   6.9   ears max   0 mean   0.0   test2 · fall 1
bar 12      on             shell max 255 mean  63.5   ears max 204 mean  97.7   on · ON
bar 12.25                  shell max 128 mean  36.1   ears max 166 mean  59.4   on · ON
bar 12.6                   shell max 230 mean  25.5   ears max  43 mean   8.6   on · kit on
bar 13                     shell max 230 mean  30.4   ears max
... [cut] ...
30 mean  69.6   ears max 140 mean  31.9   final · VU2 · STRONGER
bar 156     off            shell max 230 mean  10.2   ears max  51 mean  15.3   off1
bar 157                    shell max 230 mean   8.0   ears max  31 mean   9.2   off2
bar 158                    shell max 153 mean   5.2   ears max  20 mean   1.8   off3
bar 159                    shell max 102 mean   0.8   ears max   0 mean   0.0   off4
bar 159.3                  shell max 102 mean   1.0   ears max   0 mean   0.0   off4
tools/showkit/songs/rob
```

```
$ date; KIT=tools/showkit; W="$KIT/work/robot"; cd "~/deadmau5 app"; python3 - "$W/gen_sprites.py" "$W/gen.py" <<'EOF'
import sys
ps,pg=sys.argv[1],sys.argv[2]
s=open(ps).read()
# a real lattice for the panel, and the robot's face
s=s.replace('''# the eye: a head 5 cells wide''','''# the panel lattice: every 3rd column, every 2nd row, stepping sideways
for k in range(3):
    a = blank()
    a[:, (np.arange(C) + k) % 3 == 0] = True
    a[[1, 3, 5], :] = True
    a[7:9, :] = False
    put("lat%d" % k, a & OCC)
# the face: two block eyes that look round in steps, and a blink
def face(dx, blink=False ... [cut]
Sat Oct 31 13:04:13 PDT 2026
wrote shows/scenes/deadmau5 - Harder Better Faster Stronger.sprites.json 197 sprites 34221 bytes
wrote shows/scenes/deadmau5 - Harder Better Faster Stronger.scene.json scenes 29 hits 69
deadmau5 - Harder Better Faster Stronger: 30 scenes, 69 hits, written into shows/deadmau5 - Harder Better Faster Stronger.json
bar 13      on             shell max 230 mean  25.4   ears max 128 mean  31.1   on · kit on
bar 21.25   hats           shell max 230 mean  21.1   ears max 128 mean  31.1   hats · kit hats
bar 21.5                   shell max 230 mean  22.5   ears max 128 mean  42.1   hats · kit hats
bar 34.5    siren          shell max 255 mean  27.1   ears max 171 mean  31.6   voice · kit voice �
bar 37      voice2         shell max 230 mean  25.2   ears max 128 mean  31.1   voice2 · kit voice
bar 37.3                   shell max 230 mean  16.2   ears max 107 mean  21.5   voice2 · kit voice
bar 124     face           shell max 178 mean  24.9   ears max 204 mean  97.7   face · BARE
bar 125     face           shell max 178 mean  26.8   ears max 128 mean  31.1   face · kit bare
bar 125.5                  shell max 178 mean  20.3   ears max 128 mean  31.1   face · kit bare
bar 126.5                  shell max 178 mean  20.6   ears max 128 mean  31.1   face · kit bare
bar 127.75                 shell max 178 mean  20.8   ears max 128 mean  42.1   face · kit bare
bar 128.2                  shell max 178 mean  20.4   ears max  57 mean   8.1   face · kit bare
bar 132     panel          shell max 230 mean  29.5   ears max 128 mean  31.1   panel · kit bare
bar 132.2                  shell max 230 mean  31.7   ears max  57 mean   8.1   panel · kit bare
bar 133                    shell max 230 mean  28.5   ears max 128 mean  31.1   panel · kit bare
bar 133.1                  shell max 230 mean  29.3   ears max  43 mean   8.6   panel · kit bare
bar 133.5                  shell max 230 mean  29.7   ears max 128 mean  31.1   panel · kit bare
bar 133.75                 shell max 230 mean  29.6   ears max 128 mean  42.1   panel · kit bare
(scratch)/ki
```

```
$ KIT=tools/showkit; W="$KIT/work/robot"; cd "~/deadmau5 app"; python3 - "$W/gen_sprites.py" "$W/gen.py" <<'EOF'
import sys
ps,pg=sys.argv[1],sys.argv[2]
s=open(ps).read()
a=s.index('def face(dx, blink=False):'); b=s.index('put("fC", face(0))')
s=s[:a]+'''def face(dx, blink=False):
    a = blank()
    for cx in (4, 12):
        if blink:
            a[5, cx + dx - 3:cx + dx + 4] = True
        else:
            a[2:7, cx + dx - 2:cx + dx + 3] = True
            a[2, cx + dx - 2] = a[2, cx + dx + 2] = False       # rounder corners
    return a & OCC
'''+s[b:]
open(ps,"w").write(s)
g=open(pg).read( ... [cut]
wrote shows/scenes/deadmau5 - Harder Better Faster Stronger.sprites.json 197 sprites 34221 bytes
wrote shows/scenes/deadmau5 - Harder Better Faster Stronger.scene.json scenes 29 hits 69
deadmau5 - Harder Better Faster Stronger: 30 scenes, 69 hits, written into shows/deadmau5 - Harder Better Faster Stronger.json
bar 13.1    on             shell max 230 mean  16.9   ears max  43 mean   8.6   on · kit on
bar 14                     shell max 230 mean  20.5   ears max 128 mean  31.1   on · kit on
bar 14.5                   shell max 230 mean  20.6   ears max 128 mean  31.1   on · kit on
bar 28.1    v              shell max 204 mean  45.8   ears max 104 mean  68.4   voice · VOICE
bar 125     face           shell max 178 mean  41.6   ears max 128 mean  31.1   face · kit bare
bar 125.5                  shell max 178 mean  53.5   ears max 128 mean  31.1   face · kit bare
bar 126.5                  shell max 178 mean  53.8   ears max 128 mean  31.1   face · kit bare
bar 127.75                 shell max 178 mean  54.0   ears max 128 mean  42.1   face · kit bare
bar 138.5   panel          shell max 230 mean  30.7   ears max 128 mean  31.1   panel · kit bare
bar 96.25   eq             shell max 128 mean  37.1   ears max 140 mean  48.8   peak · VU
bar 102     eq             shell max 230 mean  41.8   ears max 140 mean  43.3   peak2 · VU
bar 112.5                  shell max 230 mean  25.7   ears max 128 mean  31.1   stack · kit stack
(scratch)/ki
```

```
$ KIT=tools/showkit; W="$KIT/work/robot"; cd "~/deadmau5 app"; python3 - "$W/gen_sprites.py" "$W/gen.py" <<'EOF'
import sys
ps,pg=sys.argv[1],sys.argv[2]
s=open(ps).read()
a=s.index('# the face: two block eyes'); b=s.index('# the eye: a head 5 cells wide')
s=s[:a]+'''# the face: two block eyes, a red pupil that looks round in steps, and a blink
def eyeblock(blink=False):
    a = blank()
    for cx in (4, 12):
        if blink:
            a[5, cx - 3:cx + 4] = True
        else:
            a[2:7, cx - 2:cx + 3] = True
            a[2, cx - 2] = a[2, cx + 2] = False
    return a & OCC
def pupil(d ... [cut]
wrote shows/scenes/deadmau5 - Harder Better Faster Stronger.sprites.json 199 sprites 34631 bytes
wrote shows/scenes/deadmau5 - Harder Better Faster Stronger.scene.json scenes 29 hits 73
  scene boot F has 7 layers, 6 at most
bar 3       B              shell max 255 mean  20.8   ears max 102 mean   7.2   boot B · BETTER
bar 5       F              shell max 255 mean  31.3   ears max  32 mean   9.5   boot F · FASTER
bar 7       S              shell max 178 mean  45.5   ears max  27 mean   8.1   boot S · STRONGER
mau5show: the scenes failed (KeyError: 'robot_fL') -- playing the cue list
bar 125     face           shell max  87 mean  17.5   ears max  87 mean  15.5   None
bar 125.5                  shell max  77 mean  14.5   ears max  77 mean  15.6   None
bar 126.5                  shell max 123 mean  23.4   ears max 123 mean  21.4   None
bar 127.75                 shell max 134 mean  27.8   ears max 134 mean  29.1   None
bar 124.2                  shell max 194 mean  30.8   ears max 133 mean  28.4   None
bar 88.25                  shell max  11 mean   6.3   ears max  45 mean  19.5   None
bar 88.3                   shell max  10 mean   5.6   ears max  42 mean  17.9   None
bar 88.4                   shell max  12 mean   6.4   ears max  53 mean  22.6   None
bar 89.1                   shell max   9 mean   4.8   ears max  84 mean  35.3   None
(scratch)/ki
```

```
$ KIT=tools/showkit; W="$KIT/work/robot"; cd "~/deadmau5 app"; python3 - "$W/gen.py" <<'EOF'
import sys
pg=sys.argv[1]
g=open(pg).read()
a=g.index('S({"name": "boot H"'); b=g.index('# ---------- the test')
g=g[:a]+'''T3, T2, T1 = spr("robot_t3", GREEN, 0.1, "max"), spr("robot_t2", BLUE, 0.16, "max"), spr("robot_t1", WHITE, 0.08, "max")
TALK = {"band": "mid", "lo": 0.03, "hi": 0.22}
S({"name": "boot H", "from": "h", "to": "b", "pal": "red", "layers": V1 + [rise("tube0", "red", 0.4)]})
S({"name": "boot B", "from": "b", "to": "f", "pal": "red", "layers": [T3] + V1 + [fill("tube0", "red", TALK), rise ... [cut]
wrote shows/scenes/deadmau5 - Harder Better Faster Stronger.scene.json scenes 29 hits 73
deadmau5 - Harder Better Faster Stronger: 30 scenes, 73 hits, written into shows/deadmau5 - Harder Better Faster Stronger.json
bar 3       B              shell max 255 mean  21.4   ears max 102 mean   7.2   boot B · BETTER
bar 5       F              shell max 255 mean  32.0   ears max 128 mean  12.1   boot F · FASTER
bar 7       S              shell max 178 mean  45.5   ears max 102 mean  15.8   boot S · STRONGER
bar 125     face           shell max 255 mean  31.9   ears max 128 mean  31.1   face · kit bare
bar 125.5                  shell max 255 mean  31.8   ears max 128 mean  31.1   face · kit bare
bar 126.5                  shell max 255 mean  32.1   ears max 128 mean  31.1   face · kit bare
bar 127.75                 shell max 255 mean  32.3   ears max 128 mean  42.1   face · kit bare
bar 124.2                  shell max 255 mean  31.8   ears max  46 mean  45.9   face · BARE
bar 88.25                  shell max 255 mean  29.1   ears max  83 mean  34.9   talk3 · HARDER
bar 88.3                   shell max 255 mean  26.7   ears max  84 mean  33.4   talk3 · HARDER
bar 88.4                   shell max 255 mean  15.3   ears max  87 mean  37.0   talk3 · HARDER
bar 89.1                   shell max 255 mean  21.6   ears max 105 mean  34.4   talk3 · FASTER
(scratch)/ki
```

```
$ date; KIT=tools/showkit; W="$KIT/work/robot"; cd "~/deadmau5 app"; python3 - "$W/gen.py" <<'EOF'
import sys
pg=sys.argv[1]
g=open(pg).read()
# boot S keeps the visor line
g=g.replace('''[T3, T2, T1] + V1[1:] + [lock(TALK)]''','''[T3, T2, T1] + V1 + [lock(TALK)]''')
# pump and dot: a dim visor line under the eye; tube 2 moves into the hit
g=g.replace('''dict(BARS, ofs=stepkeys(60, 68, 1, 0.25)), stencil("robot_st_top"), eye(2), fill("tube0", "red", 0.5, "x...", step=1, decay=0.8), fill("tube1", "green", 0.5, ".x..", step=1, decay=0.8), fill("tube2", "blue", 0.6, "..x.", step=1, decay=0.8)]})''', ... [cut]
Sat Oct 31 13:06:47 PDT 2026
wrote shows/scenes/deadmau5 - Harder Better Faster Stronger.scene.json scenes 29 hits 73
deadmau5 - Harder Better Faster Stronger: 30 scenes, 73 hits, written into shows/deadmau5 - Harder Better Faster Stronger.json
deadmau5 - Harder Better Faster Stronger: 7477 frames at 25 fps through the guard
  scene            from  mean mA   p95 mA     heat   allow W      ms
  dark             0.0s        0        0     0.0%      18.1    0.02
  boot H           0.0s      213      292     0.0%      18.1    0.20
  boot B           3.8s      273      351     0.0%      18.1    0.25
  boot F           7.5s      422      555     0.2%      18.1    0.30
  boot S          11.3s      575      771     0.6%      18.1    0.36
  test            15.0s      524      859     1.0%      18.1    0.16
  test2           18.8s      691     1000     1.6%      18.1    0.17
  on              22.5s      420      948     2.3%      18.1    0.16
  hats            37.5s      396      856     3.0%      18.1    0.16
  voice           52.5s      417      805     3.6%      18.1    0.20
  voice2          67.5s      403      797     4.3%      18.1    0.20
  down            82.5s      276      379     4.3%      18.1    0.23
  charge          97.5s      750     1000     6.9%      18.1    0.28
  pump           112.5s      338      652     7.2%      18.1    0.18
  dot            127.5s      385      779     7.7%      18.1    0.19
  talk           142.5s      507      610     8.9%      18.1    0.25
  talk2          157.5s      650      756    10.0%      18.1    0.25
  talk3          165.0s      862     1000    10.9%      18.1    0.26
  talk4          168.8s      779     1000    11.6%      18.1    0.17
  peak           172.5s      874     1000    15.0%      18.1    0.20
  peak2          187.5s 
... [cut] ...
.1 ms
-rw-r--r--@  1 jones  staff    321375 Oct 31 12:39 deadmau5 - Harder Better Faster Stronger.analysis.npz
-rw-r--r--@  1 jones  staff    172651 Oct 31 13:06 deadmau5 - Harder Better Faster Stronger.json
-rw-r--r--@  1 jones  staff   7179120 Oct 31 12:37 deadmau5 - Harder Better Faster Stronger.mp3
-rw-r--r--@  1 jones  staff   6793 Oct 31 12:39 deadmau5 - Harder Better Faster Stronger.beats
-rw-r--r--@  1 jones  staff  68759 Oct 31 13:06 deadmau5 - Harder Better Faster Stronger.scene.json
-rw-r--r--@  1 jones  staff  34631 Oct 31 13:05 deadmau5 - Harder Better Faster Stronger.sprites.json
```

I'll read the correction and the new tools first.

```
$ date; KIT=tools/showkit; ls -la "$KIT"; sed -n 38,200p "$KIT/BRIEF.md"; echo ---; cat "$KIT/sheet.py"; echo ---; cat "$KIT/power.py"; echo ---; cat "$KIT/scenepower.py"
Sat Oct 31 13:07:40 PDT 2026
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
d after the knee: from the mean
    per[nm].append((rep["sent_ma"],rep["governor_hit"],"shell" in rep["regions_hit"],res[sh].mean(),res[ea].mean(),rep["thermal"]["full_pct"] if rep.get("thermal") else 0,res[sh].max()))
print("%-14s %6s %6s %6s %6s %7s %7s %6s %6s"%("scene","mean","p95","gov%","reg%","shellm","earsm","smax","heat"))
for nm in order:
    a=np.array(per[nm],float)
    print("%-14s %6.0f %6.0f %6.0f %6.0f %7.1f %7.1f %6.0f %5.1f%%"%(nm[:14],a[:,0].mean(),np.percentile(a[:,0],95),a[:,1].mean()*100,a[:,2].mean()*100,a[:,3].mean(),a[:,4].mean(),np.percentile(a[:,6],90),a[:,5].max()))
```

```
$ KIT=tools/showkit; cd "~/deadmau5 app"; B="deadmau5 - Harder Better Faster Stronger"; python3 "$KIT/power.py" "$B" 2>&1 | tail -15; python3 "$KIT/scenepower.py" "$B" 2>&1 | tail -50; python3 "$KIT/power.py" "TIKI TIKI - Slowed" 2>&1 | tail -5
deadmau5 - Harder Better Faster Stronger: 299 s, mean 13.8 W (target 11.5 or less), heat at the end 28%
hottest scenes (name, mean W, seconds): final 16.9 30s; peak 17.9 15s; peak2 17.7 15s; charge 16.5 15s; talk 13.6 15s; face 13.2 15s; panel 13.1 15s; stack 13.1 15s
scene            mean    p95   gov%   reg%  shellm   earsm   smax   heat
dark                0      0      0      0     0.0     0.0      0   0.0%
boot H            213    292      0      0     4.6     4.4     62   0.0%
boot B            273    351      0      0     5.0     7.4     62   0.0%
boot F            422    555      0     17     7.4    11.8     62   0.2%
boot S            575    771      0     72     9.1    17.9     60   0.6%
test              524    859      0      0     4.6    22.6     62   1.0%
test2             691   1000     30      0     5.0    32.2     62   1.6%
on                420    948      4     14     7.0    12.4     60   2.3%
hats              396    856      2      6     6.0    12.7     62   3.0%
voice             417    805      4     10     6.0    13.9     62   3.6%
voice2            403    797      0     32     6.5    12.2     61   4.3%
down              276    379      0      0     4.7     7.7     62   4.3%
charge            750   1000     42     52     5.9    33.9     62   6.9%
pump              338    652      3    100     7.1     7.1     44   7.2%
dot               385    779      0     72     7.0    10.1     49   7.7%
talk              507    610      0     29     7.5    16.7     62   8.9%
talk2             650    756      0     32     7.5    25.0     62  10.0%
talk3             862   1000     27     33     7.4    38.0     62  10.9%
talk4             779   1000     65     14     4.9    37.7     62  11.6%
peak              874   1000     25    100     9.1    35.4     28  15.0
... [cut] ...
    789   1000     14    100     9.4    29.9     38  28.4%
off1              391    398      0      0     4.4    15.3     62  28.5%
off2              255    262      0      0     3.3     9.0     62  28.5%
off3              100    107      0      0     2.1     1.7     58  28.4%
off4               13     15      0      0     0.4     0.0     51  28.3%
TIKI TIKI - Slowed: 320 s, mean 12.7 W (target 11.5 or less), heat at the end 19%
hottest scenes (name, mean W, seconds): bigb 14.3 17s; sunset 14.6 14s; final2 14.6 14s; big 14.5 14s; final 14.4 14s; hook2 15.2 10s; hook4 15.2 10s; sunsetb 14.4 10s
```

```
$ date; KIT=tools/showkit; ls -la "$KIT"; sed -n 38,200p "$KIT/BRIEF.md"; echo ---; cat "$KIT/sheet.py"; echo ---; cat "$KIT/power.py"; echo ---; cat "$KIT/scenepower.py"
Sat Oct 31 13:07:40 PDT 2026
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
d after the knee: from the mean
    per[nm].append((rep["sent_ma"],rep["governor_hit"],"shell" in rep["regions_hit"],res[sh].mean(),res[ea].mean(),rep["thermal"]["full_pct"] if rep.get("thermal") else 0,res[sh].max()))
print("%-14s %6s %6s %6s %6s %7s %7s %6s %6s"%("scene","mean","p95","gov%","reg%","shellm","earsm","smax","heat"))
for nm in order:
    a=np.array(per[nm],float)
    print("%-14s %6.0f %6.0f %6.0f %6.0f %7.1f %7.1f %6.0f %5.1f%%"%(nm[:14],a[:,0].mean(),np.percentile(a[:,0],95),a[:,1].mean()*100,a[:,2].mean()*100,a[:,3].mean(),a[:,4].mean(),np.percentile(a[:,6],90),a[:,5].max()))
```

```
$ KIT=tools/showkit; cd "~/deadmau5 app"; B="deadmau5 - Harder Better Faster Stronger"; python3 "$KIT/power.py" "$B" 2>&1 | tail -15; python3 "$KIT/scenepower.py" "$B" 2>&1 | tail -50; python3 "$KIT/power.py" "TIKI TIKI - Slowed" 2>&1 | tail -5
deadmau5 - Harder Better Faster Stronger: 299 s, mean 13.8 W (target 11.5 or less), heat at the end 28%
hottest scenes (name, mean W, seconds): final 16.9 30s; peak 17.9 15s; peak2 17.7 15s; charge 16.5 15s; talk 13.6 15s; face 13.2 15s; panel 13.1 15s; stack 13.1 15s
scene            mean    p95   gov%   reg%  shellm   earsm   smax   heat
dark                0      0      0      0     0.0     0.0      0   0.0%
boot H            213    292      0      0     4.6     4.4     62   0.0%
boot B            273    351      0      0     5.0     7.4     62   0.0%
boot F            422    555      0     17     7.4    11.8     62   0.2%
boot S            575    771      0     72     9.1    17.9     60   0.6%
test              524    859      0      0     4.6    22.6     62   1.0%
test2             691   1000     30      0     5.0    32.2     62   1.6%
on                420    948      4     14     7.0    12.4     60   2.3%
hats              396    856      2      6     6.0    12.7     62   3.0%
voice             417    805      4     10     6.0    13.9     62   3.6%
voice2            403    797      0     32     6.5    12.2     61   4.3%
down              276    379      0      0     4.7     7.7     62   4.3%
charge            750   1000     42     52     5.9    33.9     62   6.9%
pump              338    652      3    100     7.1     7.1     44   7.2%
dot               385    779      0     72     7.0    10.1     49   7.7%
talk              507    610      0     29     7.5    16.7     62   8.9%
talk2             650    756      0     32     7.5    25.0     62  10.0%
talk3             862   1000     27     33     7.4    38.0     62  10.9%
talk4             779   1000     65     14     4.9    37.7     62  11.6%
peak              874   1000     25    100     9.1    35.4     28  15.0
... [cut] ...
    789   1000     14    100     9.4    29.9     38  28.4%
off1              391    398      0      0     4.4    15.3     62  28.5%
off2              255    262      0      0     3.3     9.0     62  28.5%
off3              100    107      0      0     2.1     1.7     58  28.4%
off4               13     15      0      0     0.4     0.0     51  28.3%
TIKI TIKI - Slowed: 320 s, mean 12.7 W (target 11.5 or less), heat at the end 19%
hottest scenes (name, mean W, seconds): bigb 14.3 17s; sunset 14.6 14s; final2 14.6 14s; big 14.5 14s; final 14.4 14s; hook2 15.2 10s; hook4 15.2 10s; sunsetb 14.4 10s
```

```
$ cd "~/deadmau5 app"; python3 mau5scene.py check "TIKI TIKI - Slowed" 2>&1 | sort -k3 -n -r | awk 'NR<14' ; sed -n 1,60p mau5power.py | head -80; grep -n "def apply" -A60 mau5power.py | grep -n "budget\|ceiling\|shell\|ears\|scale" | head -30
  hook3          209.7s      667      904    13.1%      18.1    0.22
  hook            10.5s      643      886     1.0%      18.1    0.12
  hookb           17.5s      640      862     1.9%      18.1    0.18
  hook3b         216.0s      639      849    14.1%      18.1    0.21
  hook4          226.4s      637      891    15.4%      18.1    0.24
  hook2           27.9s      636      891     3.2%      18.1    0.24
  sunset         132.3s      588      877     8.8%      18.1    0.21
  final2         282.0s      584     1000    18.5%      18.1    0.24
  big             69.6s      584      890     5.2%      18.1    0.21
  final          268.1s      578      969    16.9%      18.1    0.25
  sunsetb        146.2s      573      870     9.9%      18.1    0.24
  wind           296.0s      572      709    19.3%      18.1    0.16
  duel3          205.3s      565      888    12.2%      18.1    0.15
#!/usr/bin/env python3
"""mau5power -- keep the helmet cool enough to wear, on the wire.

Three facts set this module's shape.

The board takes 5 A.  622 WS2815 at full white want 11.8 A.  So a frame
that asks for white everywhere is not merely too bright, it is asking
for more than twice what the hardware can deliver, and nothing upstream
of here is obliged to be reasonable.

The LEDs are not all in the same thermal situation.  The 398 on the
shell are held on with hot glue inside a sealed print, and when that
softens they fall off.  The ear tubes hang in free air and have to
shine through a diffuser, so they can take much more.  One global
brightness number cannot express that; a ceiling per region can.

And a WS2815 draws about 1 mA per LED whenever 12 V reaches it, lit or
not.  For this chain that is ~0.6 A, ~7.5 W of heat, before a single
pixel is on.  No setting here touches it.  It i
... [cut] ...
8-        # no budget compares greater than, and its thermal level NaN for
30:265-        # -- the ceiling, as a soft knee ---------------------------------
32:267-        # a shell ceiling of 64.  Everything above a quarter of full came
40:275-        # the ceiling, with slope one at the bend so there is no kink:
42:277-        # which is below both v and the ceiling for every v, so it can
43:278-        # only take current away.  On the shell, a quarter of full, the
48:283-        # the phone's twin the shell's frame-to-frame jitter on eq and
58:293-        after_ceiling = self.frame_ma(out)
```

```
$ cd "~/deadmau5 app"; wc -l mau5power.py; sed -n 1,60p mau5power.py; grep -n "def \|class " mau5power.py | head -60
     513 mau5power.py
#!/usr/bin/env python3
"""mau5power -- keep the helmet cool enough to wear, on the wire.

Three facts set this module's shape.

The board takes 5 A.  622 WS2815 at full white want 11.8 A.  So a frame
that asks for white everywhere is not merely too bright, it is asking
for more than twice what the hardware can deliver, and nothing upstream
of here is obliged to be reasonable.

The LEDs are not all in the same thermal situation.  The 398 on the
shell are held on with hot glue inside a sealed print, and when that
softens they fall off.  The ear tubes hang in free air and have to
shine through a diffuser, so they can take much more.  One global
brightness number cannot express that; a ceiling per region can.

And a WS2815 draws about 1 mA per LED whenever 12 V reaches it, lit or
not.  For this chain that is ~0.6 A, ~7.5 W of heat, before a single
pixel is on.  No setting here touches it.  It is why the helmet gets
warm with everything dark, and the only cure is to cut the supply.

Two mechanisms, in order:

  ceiling   a per-LED cap by region, so the shell can never be driven
            as hard as a tube even by a frame that asks for it.

  governor  if the whole frame still estimates over budget, scale it
            back -- but shed from the shell first and the tubes last,
            so what survives is the part that is both safe and visible.

A frame is never passed through unchanged on trust.
"""

from __future__ import annotations

import json
import math
import os
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT = os.path.join(HERE, "data", "cal", "power.json")

MA_PER_LED_FULL_WHITE = 19.0      # WS2815 at 12 V
MA_PER_LED_STANDBY = 1.0          # drawn whenever the rail is live

# How fast the governo
... [cut] ...
1:class ThermalBudget:
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
```

```
$ KIT=tools/showkit; W="$KIT/work/robot"; cd "~/deadmau5 app"; B="deadmau5 - Harder Better Faster Stronger"; python3 "$KIT/sheet.py" "$B" "$W/g1.png" 1:HARDER 3:BETTER 5:FASTER 7:STRONGER 9:test 11:test 12:on 12.25 13 14 21:hats 21.5 28:voice 28.6 29.1 29.6 31 34.5 46:down 50 53:charge 58:charge 60:pump 60.25 68.1:dot 72 78:talk 81 88.5:t3 91.4:t4 92:white 92.25 93:peak 96 100 108:stack 108.9 110.5 124:face 125 126.5 132:panel 133 140:final 141 150 154.5 156:off 157 158 159 2>&1 | cut -c1-120
bar 1       HARDER     sent  295 mA  shell max  62 mean   7.3  ears max 102 mean   4.5  boot H · HARDER
bar 3       BETTER     sent  309 mA  shell max  62 mean   6.3  ears max 102 mean   7.2  boot B · BETTER
bar 5       FASTER     sent  500 mA  shell max  53 mean   9.9  ears max 127 mean  11.9  boot F · FASTER
bar 7       STRONGER   sent  563 mA  shell max  35 mean   9.9  ears max 102 mean  15.7  boot S · STRONGER
bar 9       test       sent  764 mA  shell max  62 mean   6.4  ears max  78 mean  33.8  test
bar 11      test       sent 1000 mA  shell max  57 mean   3.4  ears max 122 mean  53.5  test2
bar 12      on         sent 1000 mA  shell max   6 mean   1.8  ears max  60 mean  56.2  on · ON
bar 12.25              sent 1000 mA  shell max  24 mean   6.3  ears max 119 mean  47.9  on · ON
bar 13                 sent  803 mA  shell max  62 mean   9.5  ears max 127 mean  31.0  on · kit on
bar 14                 sent  802 mA  shell max  62 mean   9.5  ears max 127 mean  31.0  on · kit on
bar 21      hats       sent  674 mA  shell max  62 mean   7.9  ears max 127 mean  26.0  hats · kit hats
bar 21.5               sent  947 mA  shell max  62 mean   8.2  ears max 127 mean  41.9  hats · kit hats
bar 28      voice      sent 1000 mA  shell max   6 mean   1.9  ears max  60 mean  56.2  voice · VOICE
bar 28.6               sent  251 mA  shell max  51 mean   4.3  ears max  36 mean   7.1  voice · kit voice
bar 29.1               sent  299 mA  shell max  51 mean   5.9  ears max  36 mean   7.1  voice · kit voice
bar 29.6               sent  353 mA  shell max  51 mean   7.7  ears max  36 mean   7.1  voice · kit voice
bar 31                 sent  785 mA  shell max  62 mean   8.8  ears max 127 mean  31.0  voice · kit voice · HARDER
bar 34.5               sent  745 mA  shell max  62 mean   7.
... [cut] ...
bar 154.5              sent  656 mA  shell max  29 mean   9.8  ears max 140 mean  21.3  final · VU2 · FASTER
bar 156     off        sent  390 mA  shell max  62 mean   4.4  ears max  51 mean  15.3  off1
bar 157                sent  254 mA  shell max  62 mean   3.2  ears max  30 mean   9.0  off2
bar 158                sent   99 mA  shell max  58 mean   2.1  ears max  20 mean   1.7  off3
bar 159                sent   11 mA  shell max  51 mean   0.4  ears max   0 mean   0.0  off4
tools/showkit/songs/robot/g1.png
```

```
$ cd "~/deadmau5 app"; wc -l mau5power.py; sed -n 1,60p mau5power.py; grep -n "def \|class " mau5power.py | head -60
     513 mau5power.py
#!/usr/bin/env python3
"""mau5power -- keep the helmet cool enough to wear, on the wire.

Three facts set this module's shape.

The board takes 5 A.  622 WS2815 at full white want 11.8 A.  So a frame
that asks for white everywhere is not merely too bright, it is asking
for more than twice what the hardware can deliver, and nothing upstream
of here is obliged to be reasonable.

The LEDs are not all in the same thermal situation.  The 398 on the
shell are held on with hot glue inside a sealed print, and when that
softens they fall off.  The ear tubes hang in free air and have to
shine through a diffuser, so they can take much more.  One global
brightness number cannot express that; a ceiling per region can.

And a WS2815 draws about 1 mA per LED whenever 12 V reaches it, lit or
not.  For this chain that is ~0.6 A, ~7.5 W of heat, before a single
pixel is on.  No setting here touches it.  It is why the helmet gets
warm with everything dark, and the only cure is to cut the supply.

Two mechanisms, in order:

  ceiling   a per-LED cap by region, so the shell can never be driven
            as hard as a tube even by a frame that asks for it.

  governor  if the whole frame still estimates over budget, scale it
            back -- but shed from the shell first and the tubes last,
            so what survives is the part that is both safe and visible.

A frame is never passed through unchanged on trust.
"""

from __future__ import annotations

import json
import math
import os
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT = os.path.join(HERE, "data", "cal", "power.json")

MA_PER_LED_FULL_WHITE = 19.0      # WS2815 at 12 V
MA_PER_LED_STANDBY = 1.0          # drawn whenever the rail is live

# How fast the governo
... [cut] ...
1:class ThermalBudget:
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
```

```
$ KIT=tools/showkit; W="$KIT/work/robot"; cd "~/deadmau5 app"; B="deadmau5 - Harder Better Faster Stronger"; python3 "$KIT/sheet.py" "$B" "$W/g1.png" 1:HARDER 3:BETTER 5:FASTER 7:STRONGER 9:test 11:test 12:on 12.25 13 14 21:hats 21.5 28:voice 28.6 29.1 29.6 31 34.5 46:down 50 53:charge 58:charge 60:pump 60.25 68.1:dot 72 78:talk 81 88.5:t3 91.4:t4 92:white 92.25 93:peak 96 100 108:stack 108.9 110.5 124:face 125 126.5 132:panel 133 140:final 141 150 154.5 156:off 157 158 159 2>&1 | cut -c1-120
bar 1       HARDER     sent  295 mA  shell max  62 mean   7.3  ears max 102 mean   4.5  boot H · HARDER
bar 3       BETTER     sent  309 mA  shell max  62 mean   6.3  ears max 102 mean   7.2  boot B · BETTER
bar 5       FASTER     sent  500 mA  shell max  53 mean   9.9  ears max 127 mean  11.9  boot F · FASTER
bar 7       STRONGER   sent  563 mA  shell max  35 mean   9.9  ears max 102 mean  15.7  boot S · STRONGER
bar 9       test       sent  764 mA  shell max  62 mean   6.4  ears max  78 mean  33.8  test
bar 11      test       sent 1000 mA  shell max  57 mean   3.4  ears max 122 mean  53.5  test2
bar 12      on         sent 1000 mA  shell max   6 mean   1.8  ears max  60 mean  56.2  on · ON
bar 12.25              sent 1000 mA  shell max  24 mean   6.3  ears max 119 mean  47.9  on · ON
bar 13                 sent  803 mA  shell max  62 mean   9.5  ears max 127 mean  31.0  on · kit on
bar 14                 sent  802 mA  shell max  62 mean   9.5  ears max 127 mean  31.0  on · kit on
bar 21      hats       sent  674 mA  shell max  62 mean   7.9  ears max 127 mean  26.0  hats · kit hats
bar 21.5               sent  947 mA  shell max  62 mean   8.2  ears max 127 mean  41.9  hats · kit hats
bar 28      voice      sent 1000 mA  shell max   6 mean   1.9  ears max  60 mean  56.2  voice · VOICE
bar 28.6               sent  251 mA  shell max  51 mean   4.3  ears max  36 mean   7.1  voice · kit voice
bar 29.1               sent  299 mA  shell max  51 mean   5.9  ears max  36 mean   7.1  voice · kit voice
bar 29.6               sent  353 mA  shell max  51 mean   7.7  ears max  36 mean   7.1  voice · kit voice
bar 31                 sent  785 mA  shell max  62 mean   8.8  ears max 127 mean  31.0  voice · kit voice · HARDER
bar 34.5               sent  745 mA  shell max  62 mean   7.
... [cut] ...
bar 154.5              sent  656 mA  shell max  29 mean   9.8  ears max 140 mean  21.3  final · VU2 · FASTER
bar 156     off        sent  390 mA  shell max  62 mean   4.4  ears max  51 mean  15.3  off1
bar 157                sent  254 mA  shell max  62 mean   3.2  ears max  30 mean   9.0  off2
bar 158                sent   99 mA  shell max  58 mean   2.1  ears max  20 mean   1.7  off3
bar 159                sent   11 mA  shell max  51 mean   0.4  ears max   0 mean   0.0  off4
tools/showkit/songs/robot/g1.png
```

```
$ KIT=tools/showkit; W="$KIT/work/robot"; cd "~/deadmau5 app"; python3 - "$W/gen.py" <<'EOF'
import sys
pg=sys.argv[1]
g=open(pg).read()
g=g.replace('''"pal": "rainbow", "gain": 0.42}
LIDS''','''"pal": "rainbow", "gain": 0.34}
LIDS''')
g=g.replace('''def vu(on, band, c, gain=0.55,''','''def vu(on, band, c, gain=0.45,''')
g=g.replace('''RB2 = dict(RB, speed=0.0625, gain={"140": 0.42, "152": 0.14})''','''RB2 = dict(RB, speed=0.0625, gain={"140": 0.34, "152": 0.12})''')
g=g.replace('''rise("tube0+tube1+tube2", "white", [0.05, 0.4])''','''rise("tube0+tube1+tube2", "white", [0.04, 0.3])''')
g=g.replac ... [cut]
wrote shows/scenes/deadmau5 - Harder Better Faster Stronger.scene.json scenes 29 hits 73
deadmau5 - Harder Better Faster Stronger: 30 scenes, 73 hits, written into shows/deadmau5 - Harder Better Faster Stronger.json
  test            15.0s      524      859     1.0%      18.1    0.17
  test2           18.8s      622     1000     1.5%      18.1    0.17
  charge          97.5s      725     1000     6.7%      18.1    0.29
  talk           142.5s      507      610     8.7%      18.1    0.26
  talk2          157.5s      650      756     9.8%      18.1    0.25
  talk3          165.0s      728     1000    10.4%      18.1    0.27
  talk4          168.8s      726     1000    11.1%      18.1    0.18
  peak           172.5s      784      966    14.0%      18.1    0.21
  peak2          187.5s      759      938    16.8%      18.1    0.23
  final          262.5s      710      959    25.8%      18.1    0.26
  worst frame 1.32 ms; no scene reaches the sustained floor
```

```
$ cd "~/deadmau5 app"; sed -n 61,100p mau5power.py; sed -n 176,415p mau5power.py; cat data/cal/power.json
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
$ cd "~/deadmau5 app"; sed -n 61,100p mau5power.py; sed -n 176,415p mau5power.py; cat data/cal/power.json
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
