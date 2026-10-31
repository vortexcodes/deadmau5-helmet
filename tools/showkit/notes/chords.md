# What the chords builder ran and saw

Commands and their text output, in order, with long output cut. Images are left out; rerun the tools to see them. Cut off partway: the generator and treatment in the repo are the latest state.

I'll start by reading the brief.

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
$ KIT="tools/showkit"; cat "$KIT/fmt.py"; echo ------; cat "$KIT/grid.py"; echo ------; cat "$KIT/sheet.py"; echo -----; cat "$KIT/songmap.py"; echo -----; cat "$KIT/spectro.py"; echo -----; cat "$KIT/spritetry.py"
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
$ cd "~/deadmau5 app"; ls -la shows | head -50; ls -la shows/scenes | head -60; wc -c "shows/scenes/TIKI TIKI - Slowed.scene.json"; python3 -c "
import json
d=json.load(open('shows/scenes/TIKI TIKI - Slowed.scene.json'))
print(d.keys())
print(d.get('about'))
print(d.get('marks'))
print(list(d.get('palettes').keys()))
print(list(d.get('motifs',{}).keys()))
for s in d['scenes']: print(s.get('name'), s.get('from'), s.get('to'), s.get('pal'), len(s.get('layers',[])) )
for h in d.get('hits',[]): print(h.get('name'),h.get('at'),h.get('beats'))
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
dip2 climb2 None 0
climb2 climb2 hook4 None 0
hook4 hook4 burn4 None 0
burn4 burn4 water4 None 0
lagoon4 water4 stop4 None 0
stop4 stop4 still4 None 0
still4 still4 swell4 lagoon 4
swell4 swell4 verse4 None 0
verse4 verse4 vlow4 None 0
vlow4 vlow4 vrise4 None 0
vrise4 vrise4 final None 0
final final final2 torch 6
final2 final2 wind None 0
wind wind out1 torch 4
out out1 end ember 4
LIT hook 2
HOOK 2 hook2 2
TIKI TIKI 26.5 18
VERSE verse 2
IDOL big 2
VERSE 2 verse2 2
SUNSET big2 2
VERSE 3 verse3 2
DUEL big3 2
SWAP big3b 1
SWAP 2 big3c 1
OVER seam 2
HOOK 4 hook4 2
VERSE 4 verse4 2
FINAL final 2
```

```
$ KIT="tools/showkit"; cat "$KIT/fmt.py"; echo ------; cat "$KIT/grid.py"; echo ------; cat "$KIT/sheet.py"; echo -----; cat "$KIT/songmap.py"; echo -----; cat "$KIT/spectro.py"; echo -----; cat "$KIT/spritetry.py"
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
$ cd "~/deadmau5 app"; ls -la shows | head -50; ls -la shows/scenes | head -60; wc -c "shows/scenes/TIKI TIKI - Slowed.scene.json"; python3 -c "
import json
d=json.load(open('shows/scenes/TIKI TIKI - Slowed.scene.json'))
print(d.keys())
print(d.get('about'))
print(d.get('marks'))
print(list(d.get('palettes').keys()))
print(list(d.get('motifs',{}).keys()))
for s in d['scenes']: print(s.get('name'), s.get('from'), s.get('to'), s.get('pal'), len(s.get('layers',[])) )
for h in d.get('hits',[]): print(h.get('name'),h.get('at'),h.get('beats'))
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
dip2 climb2 None 0
climb2 climb2 hook4 None 0
hook4 hook4 burn4 None 0
burn4 burn4 water4 None 0
lagoon4 water4 stop4 None 0
stop4 stop4 still4 None 0
still4 still4 swell4 lagoon 4
swell4 swell4 verse4 None 0
verse4 verse4 vlow4 None 0
vlow4 vlow4 vrise4 None 0
vrise4 vrise4 final None 0
final final final2 torch 6
final2 final2 wind None 0
wind wind out1 torch 4
out out1 end ember 4
LIT hook 2
HOOK 2 hook2 2
TIKI TIKI 26.5 18
VERSE verse 2
IDOL big 2
VERSE 2 verse2 2
SUNSET big2 2
VERSE 3 verse3 2
DUEL big3 2
SWAP big3b 1
SWAP 2 big3c 1
OVER seam 2
HOOK 4 hook4 2
VERSE 4 verse4 2
FINAL final 2
```

```
$ cd "~/deadmau5 app"; KIT="tools/showkit"; mkdir -p "$KIT/work/chords"; date; time python3 "$KIT/grid.py" scan "shows/deadmau5 - Some Chords.mp3" 2>&1 | tail -30; sed -n 1,5p "/dev/null"; ffprobe -hide_banner "shows/deadmau5 - Some Chords.mp3" 2>&1 | tail -8
Sat Oct 31 12:39:14 PDT 2026
estimator: 128.001 BPM, first bar 0.223 s, tempo lock 0.727, bar lock 0.6310670262662046; song 447.3 s
refined over the whole song: spb 0.468747 = 128.001 BPM
first half 128.001 BPM, second half 128.001 BPM (these should agree within 0.05)
phase of the music against that grid per 8 bars, ms (flat = right; one 16th = 117 ms; contrast under 1.15 means sparse, ignore it):
  0:-7(2.13)  8:-5(2.32)  16:-7(1.80)  24:-5(2.31)  32:-5(2.91)  40:-5(2.90)  48:-7(4.07)  56:-7(5.18)  64:-7(5.48)  72:-5(6.02)  80:-5(5.64)  88:-7(5.96)  96:-7(5.57)  104:-5(5.43)  112:-5(4.37)  120:-3(1.98)  128:-3(1.67)  136:-3(1.42)  144:-3(2.13)  152:-3(2.93)  160:-5(4.16)  168:-5(5.74)  176:-5(5.46)  184:-5(5.50)  192:-5(4.94)  200:-9(5.07)  208:-3(5.36)  216:-3(5.56)  224:-3(6.86)  232:-7(9.86)
change per beat position, estimator's bar 1 at 0.223 s: 0:0.91 1:0.54 2:0.79 3:0.58  (the highest is where bars really start, 0 = estimator is right)
strongest phrase positions, in beats mod 32 from that bar 1: 16(1.56), 0(1.49), 30(1.11), 15(0.90), 2(0.87), 18(0.87)
biggest single changes (time, beat from bar 1, beat mod 4): 96.8s b206 m2; 105.2s b224 m0; 112.7s b240 m0; 120.2s b256 m0; 217.7s b464 m0; 218.2s b465 m1; 224.8s b479 m3; 225.2s b480 m0; 225.7s b481 m1; 306.8s b654 m2; 367.7s b784 m0; 375.2s b800 m0; 382.7s b816 m0; 390.2s b832 m0; 397.7s b848 m0; 404.3s b862 m2; 405.2s b864 m0; 406.2s b866 m2; 412.7s b880 m0; 419.3s b894 m2; 420.2s b896 m0; 424.9s b906 m2; 427.7s b912 m0; 442.7s b944 m0
suggested next: grid.py fold with --spb 0.468747 --anchor 0.223, decide the bar line, then grid.py write
python3 "$KIT/grid.py" scan "shows/deadmau5 - Some Chords.mp3" 2>&1  2.77s user 0.81s system 112% cpu 3.178 total
tail -30  0.00s user 0.00s system 0% cpu 3.178 total
Input #0, mp3, from 'shows/deadmau5 - Some Chords.mp3':
  Metadata:
    encoder         : Lavf58.20.100
  Duration: 00:07:27.27, start: 0.025057, bitrate: 320 kb/s
  Stream #0:0: Audio: mp3 (mp3float), 44100 Hz, stereo, fltp, 320 kb/s, start 0.025057
    Metadata:
      encoder         : Lavc58.35
```

```
$ cd "~/deadmau5 app"; KIT="tools/showkit"; python3 "$KIT/grid.py" fold "shows/deadmau5 - Some Chords.mp3" --spb 0.468747 --anchor 0.218 2>&1
bar 0 at 0.218 s, 128.001 BPM, 238 bars
bars 0-16   (16 steps, | every beat; one row per band)
   sub     =:..|..=.|....|..@.   peak 0.63
   bass    =...|..-.|....|..@.   peak 0.69
   lowmid  -...|..=.|....|..@.   peak 0.70
   mid     =::.|::=:|::::|::@.   peak 0.32
   pres    =:--|=-=-|----|=-@:   peak 0.13
   air     +-=.|*=*.|+-+:|#:@.   peak 0.05
bars 16-32   (16 steps, | every beat; one row per band)
   sub     *===|+++-|+=-=|+=@=   peak 0.25
   bass    @:::|@=+:|%-:-|*-@-   peak 0.25
   lowmid  %-:-|==*-|=---|-=@-   peak 0.23
   mid     @:::|=:+-|*-:-|+-@:   peak 0.24
   pres    #==-|#-*-|+==-|%=@-   peak 0.21
   air     @:-.|#.=.|%:-:|@.#    peak 0.33
bars 32-48   (16 steps, | every beat; one row per band)
   sub     #%++|*@#=|@@*=|@%%*   peak 0.20
   bass    @:..|@:..|@:..|@::.   peak 0.74
   lowmid  @@-:|#%*-|@%-=|%%@-   peak 0.23
   mid     @=..|*-:.|@-..|#-:.   peak 0.52
   pres    +-..|@::.|=-..|@::.   peak 0.49
   air     @ : |@ - |% :.|% -    peak 0.85
bars 48-64   (16 steps, | every beat; one row per band)
   sub     %...|@ . |@ :#|..*:   peak 0.84
   bass    @.: |@.: |@.::|*.:    peak 1.01
   lowmid  %.: |@.- |@.-.|=:.    peak 0.88
   mid     -.- |@.- |%.- |=  .   peak 1.06
   pres    * - |@ - |% - |+      peak 1.25
   air     * - |@ - |@ - |+ ..   peak 1.19
bars 64-80   (16 steps, | every beat; one row per band)
   sub     % . |@ : |% .#|. *:   peak 1.09
   bass    %.. |@.: |@.:.|+.:    peak 1.32
   lowmid  %.: |@.- |@.: |-:     peak 1.12
   mid     - - |@.- |%.- |=  .   peak 1.32
   pres    * - |@ - |% - |+      peak 1.52
   air     #.+.|# +.|@:*:|+ -:   peak 1.33
bars 80-96   (16 steps, | every beat; one row per band)
   sub     % . |@ . |% .#|. +:   peak 1.10
   bass    %.. |@.. |@..:|+.:    peak 1.33
   lowmid  %.- |@.- |@.-.|--     peak 1.09
   mid
... [cut] ...
ry beat; one row per band)
   sub     % . |@ : |% :%|. *:   peak 1.04
   bass    %.. |@.. |@..=|+ -    peak 1.38
   lowmid  %.: |@.. |@..+|-.-    peak 1.12
   mid     - : |@.: |%..=|-      peak 1.38
   pres    + : |@ - |% --|= :    peak 1.64
   air     + - |@ = |@ --|+ :    peak 1.53
bars 224-238   (16 steps, | every beat; one row per band)
   sub     @ . |@ : |@ :=|+ =.   peak 0.62
   bass    @ . |@ . |@ ..|% .    peak 1.08
   lowmid  @ . |@ . |@ .:|# .    peak 0.97
   mid     * : |@.: |% ::|#..    peak 1.17
   pres    # = |@ - |% =.|% -    peak 1.32
   air     % + |@ + |@ +.|% =    peak 1.28
```

```
$ cd "~/deadmau5 app"; KIT="tools/showkit"; python3 "$KIT/grid.py" write "deadmau5 - Some Chords" --spb 0.468747 --anchor 0.218 2>&1 | tail -5; python3 "$KIT/grid.py" check "deadmau5 - Some Chords" 2>&1 | tail -5; python3 "$KIT/songmap.py" "deadmau5 - Some Chords" 2>&1 | head -260; date
    6:45.21-6:52.71  lvl3  strobe     {'hz': 6.0}
    6:52.71-7:00.21  lvl3  confetti   {'rate': 26.0}
    7:00.21-7:07.71  lvl3  rainbow    {'period': 2.5}
    7:07.71-7:26.46  lvl1  breathe    {'period': 3.75}
wrote shows/scenes/deadmau5 - Some Chords.beats: 954 beats, 238 bars, bar 0 at 0.218 s, 128.001 BPM
deadmau5 - Some Chords: 128.001 BPM, 239 bars, bar 0 at 0.218 s, holds []
music against the grid per 8 bars, ms (contrast): 0:-3(2.12)  8:-1(2.33)  16:-5(1.81)  24:+1(2.33)  32:+1(3.01)  40:+1(2.88)  48:-1(4.07)  56:-1(5.28)  64:-1(5.47)  72:-1(6.28)  80:-1(5.82)  88:-1(6.02)  96:+1(5.72)  104:+1(5.39)  112:+1(4.38)  120:+3(1.98)  128:+3(1.66)  136:+3(1.41)  144:+3(2.13)  152:-1(2.90)  160:+1(4.16)  168:+1(5.71)  176:+1(5.45)  184:+1(5.77)  192:+1(5.04)  200:+1(5.14)  208:+1(5.51)  216:+1(5.80)  224:+3(6.91)  232:-3(11.09)
worst 5 ms where the music is clear enough to say, mean +0.7 ms
deadmau5 - Some Chords: 239 bars, 1.87 s a bar, 447.3 s
 bar     t   E  B  M  H  notes       change
   0    0.2   9  9  0  0  A C F       
   1    2.1   9  9  0  0  F C A       
   2    4.0   9  9  1  0  F C A       
   3    5.8   9  9  2  0  C A F       
   4    7.7   9  9  3  0  C A F       
   5    9.6   9  9  3  0  F C A       
   6   11.5   9  9  3  0  C F A       
   7   13.3   9  9  3  0  A C F       
   8   15.2   9  9  4  1  C A F       
   9   17.1   9  9  5  1  F C A       
  10   19.0   8  8  6  2  A C F       
  11   20.8   9  9  6  2  C A F       
  12   22.7   8  8  7  3  C A F       
  13   24.6   8  8  7  3  A F C       
  14   26.5   8  8  7  3  A F C       
  15   28.3   8  9  8  4  C A F       
  16   30.2   9  9  7  3  A C F       
  17   32.1   8  8  8  3  A F C       
  18   34.0   8  8  8  4  F C A       
  19   35.8   8  8  8  4  C A F       
  20   37.7   8
... [cut] ...
  6  C F A       
 225  422.1   8  7  5  6  C F A       
 226  424.0   7  6  4  6  C F A       
 227  425.8   9  8  6  8  C F A       >>
 228  427.7   5  4  5  9  A C F       >>
 229  429.6   3  3  3  7  A C F       >>
 230  431.5   3  3  2  5  A C F       
 231  433.3   3  3  2  5  A C F       
 232  435.2   3  3  2  5  A C F       
 233  437.1   3  3  2  5  A C F       
 234  439.0   3  3  2  5  A C F       
 235  440.8   3  3  2  5  A C F       
 236  442.7   0  0  0  0  G# D# B     >>
 237  444.6   0  0  0  0  G# D# B     
 238  446.5   0  0  0  0  G# D# B     
Sat Oct 31 12:39:37 PDT 2026
```

```
$ cd "~/deadmau5 app"; KIT="tools/showkit"; W="$KIT/work/chords"; python3 "$KIT/spectro.py" "deadmau5 - Some Chords" "$W/spec_all.png" 2>&1 | tail -1; python3 mau5scene.py bars "deadmau5 - Some Chords" 2>&1 | head -60
tools/showkit/songs/chords/spec_all.png
     0     0.22s  energy 0.78  bass 0.94 (punch 1.00)  mid 0.06  high 0.00
     1     2.09s  energy 0.80  bass 0.94 (punch 0.90)  mid 0.09  high 0.00
     2     3.97s  energy 0.76  bass 0.91 (punch 1.00)  mid 0.17  high 0.00
     3     5.84s  energy 0.76  bass 0.94 (punch 0.14)  mid 0.25  high 0.00
     4     7.72s  energy 0.76  bass 0.92 (punch 1.00)  mid 0.28  high 0.00
     5     9.59s  energy 0.79  bass 0.92 (punch 0.89)  mid 0.28  high 0.00
     6    11.47s  energy 0.77  bass 0.90 (punch 1.00)  mid 0.33  high 0.03
     7    13.34s  energy 0.79  bass 0.96 (punch 0.14)  mid 0.35  high 0.05
     8    15.22s  energy 0.78  bass 0.93 (punch 1.00)  mid 0.40  high 0.08
     9    17.09s  energy 0.78  bass 0.92 (punch 0.96)  mid 0.46  high 0.11
    10    18.97s  energy 0.73  bass 0.87 (punch 1.00)  mid 0.57  high 0.17
    11    20.84s  energy 0.76  bass 0.94 (punch 0.14)  mid 0.59  high 0.20
    12    22.72s  energy 0.72  bass 0.86 (punch 1.00)  mid 0.67  high 0.25
    13    24.59s  energy 0.73  bass 0.85 (punch 0.68)  mid 0.70  high 0.27
    14    26.47s  energy 0.73  bass 0.84 (punch 1.00)  mid 0.72  high 0.30
    15    28.34s  energy 0.72  bass 0.90 (punch 0.14)  mid 0.77  high 0.33
    16    30.22s  energy 0.76  bass 0.90 (punch 1.00)  mid 0.73  high 0.31
    17    32.09s  energy 0.72  bass 0.82 (punch 0.33)  mid 0.77  high 0.32
    18    33.97s  energy 0.74  bass 0.87 (punch 0.25)  mid 0.81  high 0.34
    19    35.84s  energy 0.74  bass 0.85 (punch 0.13)  mid 0.80  high 0.34
    20    37.72s  energy 0.71  bass 0.82 (punch 0.14)  mid 0.83  high 0.36
    21    39.59s  energy 0.75  bass 0.85 (punch 0.23)  mid 0.81  high 0.36
    22    41.47s  energ
... [cut] ...

    52    97.72s  energy 0.76  bass 0.74 (punch 1.00)  mid 0.62  high 0.72
    53    99.59s  energy 0.77  bass 0.76 (punch 1.00)  mid 0.58  high 0.63
    54   101.47s  energy 0.74  bass 0.73 (punch 1.00)  mid 0.56  high 0.58
    55   103.34s  energy 0.77  bass 0.77 (punch 1.00)  mid 0.62  high 0.61
    56   105.22s  energy 0.74  bass 0.74 (punch 1.00)  mid 0.56  high 0.58
    57   107.09s  energy 0.77  bass 0.77 (punch 1.00)  mid 0.57  high 0.59
    58   108.97s  energy 0.74  bass 0.73 (punch 1.00)  mid 0.56  high 0.58
    59   110.84s  energy 0.82  bass 0.86 (punch 1.00)  mid 0.67  high 0.66
```

```
$ mkdir -p "tools/showkit/songs/chords"; cat > "tools/showkit/songs/chords/chroma.py" <<'EOF'
#!/usr/bin/env python3
"""Per-8th-note chromagram for Some Chords: bass band and mid band, printed and drawn."""
import os, subprocess, sys
import numpy as np
SR=22050
mp3="shows/deadmau5 - Some Chords.mp3"
W=os.path.dirname(os.path.abspath(__file__))
cache=os.path.join(W,"mono.npy")
if os.path.exists(cache):
    m=np.load(cache)
else:
    raw=subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-i",mp3,"-ac","1","-ar",str ... [cut]
ok 1907
```

```
$ cat > "tools/showkit/songs/chords/chroma_zoom.py" <<'EOF'
#!/usr/bin/env python3
"""chroma_zoom.py out.png from to : zoomed chromagram, with beat and bar lines (higher-resolution, shorter window)."""
import os, sys
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
W=os.path.dirname(os.path.abspath(__file__))
m=np.load(os.path.join(W,"mono.npy")); SR=22050
spb=0.468747; t0=0.218
NOTES="C C# D D# E F F# G G# A A# B".split()
out,lo,hi=sys.argv[1],float(sys.argv[2]),float(sys.argv[3])
N=4096
win=np.hanning(N)
f=np.fft.rfftfreq(N,1/SR)
def pcmap(lo,hi):
    idx=np.flatn ... [cut]
tools/showkit/songs/chords/cz_16_32.png
tools/showkit/songs/chords/cz_64_80.png
```

```
$ cat > "tools/showkit/songs/chords/hpss.py" <<'EOF'
#!/usr/bin/env python3
"""Harmonic part of the whole song, chroma per 16th, saved, then drawn for ranges."""
import os, sys
import numpy as np
from scipy.ndimage import median_filter
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
W=os.path.dirname(os.path.abspath(__file__))
m=np.load(os.path.join(W,"mono.npy")); SR=22050
spb=0.468747; t0=0.218
NOTES="C C# D D# E F F# G G# A A# B".split()
N=4096; H=512
win=np.hanning(N)
nf=(len(m)-N)//H
S=np.zeros((nf,N//2+1),np.float32)
for s in range(0,nf,4000):
    e=min(s+4000,nf)
    fr=np.sta ... [cut]
Traceback (most recent call last):
  File "tools/showkit/songs/chords/hpss.py", line 5, in <module>
    from scipy.ndimage import median_filter
ModuleNotFoundError: No module named 'scipy'
Sat Oct 31 12:41:01 PDT 2026
```

```
$ cd "tools/showkit/songs/chords/" && python3 - <<'EOF'
import re
s=open("hpss.py").read()
s=s.replace("from scipy.ndimage import median_filter\n","from numpy.lib.stride_tricks import sliding_window_view as swv\n")
s=s.replace("""H_=median_filter(S,size=(31,1))
P_=median_filter(S,size=(1,31))
""","""nb=int(2600/(SR/N))
S=S[:,:nb]
H_=np.zeros_like(S)
for b in range(nb):
    H_[:,b]=np.median(swv(np.pad(S[:,b],15,mode="edge"),31),axis=1)
P_=np.zeros_like(S)
for s_ in range(0,nf,4000):
    e_=min(s_+4000,nf)
    P_[s_:e_]=np.median(swv(np.pad(S[s_:e_],((0,0),(15,15)),mode="edge"),31,axis=1),axis=2)
""")
s=s.rep ... [cut]
stft (19254, 2049)
saved
python3 "$W/hpss.py"  5.20s user 0.23s system 99% cpu 5.459 total
tools/showkit/songs/chords/h_all.png
Sat Oct 31 12:41:16 PDT 2026
```

```
$ cd "~/deadmau5 app"; KIT="tools/showkit"; W="$KIT/work/chords"; B="deadmau5 - Some Chords"; python3 "$KIT/spectro.py" "$B" "$W/spec_44_60.png" 44 60 | tail -1;  python3 "$KIT/spectro.py" "$B" "$W/spec_112_128.png" 112 128 | tail -1; python3 "$KIT/spectro.py" "$B" "$W/spec_156_172.png" 156 172 | tail -1; python3 "$KIT/spectro.py" "$B" "$W/spec_190_238.png" 190 238 | tail -1;python3 "$W/hdraw.py" "$W/h_52_68.png" 52 68; python3 "$W/hdraw.py" "$W/h_100_116.png" 100 116
tools/showkit/songs/chords/spec_44_60.png
tools/showkit/songs/chords/spec_112_128.png
tools/showkit/songs/chords/spec_156_172.png
tools/showkit/songs/chords/spec_190_238.png
tools/showkit/songs/chords/h_52_68.png
tools/showkit/songs/chords/h_100_116.png
```

```
$ cat > "tools/showkit/songs/chords/label.py" <<'EOF'
#!/usr/bin/env python3
import os, sys
import numpy as np
W=os.path.dirname(os.path.abspath(__file__))
z=np.load(os.path.join(W,"hchroma.npz")); tt=z["tt"]
spb=0.468747; t0=0.218
NOTES="C C# D D# E F F# G G# A A# B".split()
low=z["low"]; mid=z["mid"]; high=z["high"]
C=np.sqrt(low)+0.8*np.sqrt(mid)+0.3*np.sqrt(high)
nsteps=int((tt[-1]-t0)/(spb/4))
tem={}
for r in range(12):
    for q,iv in (("",(0,4,7)),("m",(0,3,7))):
        v=np.zeros(12); 
        for k,i in enumerate(iv): v[(r+i)%12]=[1,0.8,0.8][k]
        tem[NOTES[r]+q]=v/np.linalg.norm(v)
names=list ... [cut]
bar    0.000  len  0.88 bars  G#m   0.95
bar    0.875  len  1.50 bars  E     0.91
bar    2.375  len  0.50 bars  F#    0.91
bar    2.875  len  1.12 bars  G#    0.95
bar    4.000  len  0.88 bars  G#m   0.94
bar    4.875  len  1.50 bars  E     0.86
bar    6.375  len  0.50 bars  F#    0.92
bar    6.875  len  1.12 bars  G#    0.95
bar    8.000  len  0.88 bars  G#m   0.88
bar    8.875  len  1.50 bars  E     0.91
bar   10.375  len  0.50 bars  F#    0.90
bar   10.875  len  1.12 bars  G#    0.90
bar   12.000  len  0.88 bars  G#m   0.91
bar   12.875  len  1.50 bars  E     0.87
bar   14.375  len  0.50 bars  F#    0.89
bar   14.875  len  1.12 bars  G#    0.87
bar   16.000  len  0.75 bars  G#m   0.88
bar   16.875  len  0.19 bars  E     0.77
bar   17.062  len  0.25 bars  G#m   0.81
bar   17.312  len  0.50 bars  E     0.85
bar   17.875  len  0.31 bars  E     0.88
bar   18.250  len  0.12 bars  E     0.83
bar   18.375  len  0.50 bars  F#    0.88
bar   18.875  len  0.44 bars  G#    0.91
bar   19.312  len  0.19 bars  Cm    0.87
bar   19.500  len  0.50 bars  G#    0.85
bar   20.000  len  0.12 bars  G#m   0.76
bar   20.188  len  0.38 bars  G#m   0.84
bar   20.625  len  0.25 bars  G#m   0.80
bar   20.875  len  0.38 bars  E     0.87
bar   21.250  len  0.19 bars  G#m   0.80
bar   21.438  len  0.38 bars  E     0.82
bar   21.812  len  0.12 bars  G#m   0.80
bar   21.938  len  0.38 bars  E     0.85
bar   22.375  len  0.50 bars  F#    0.84
bar   22.938  len  0.62 bars  G#    0.88
bar   23.562  len  0.12 bars  Cm    0.81
bar   23.688  len  0.12 bars  G#    0.84
bar   23.812  len  0.12 bars  Cm    0.81
bar   24.000  len  0.25 bars  B     0.79
bar   24.250  len  0.44 bars  G#m   0.85
bar   24.688  len  0.12 bars  B     0.85
bar   24.812  len  0.31 bars  G#m   0.83
bar   25.125  len  0.38 bars  E     0
... [cut] ...
len  0.25 bars  F#    0.80
bar   42.875  len  0.62 bars  Cm    0.83
bar   43.500  len  0.38 bars  G#    0.88
bar   43.875  len  0.12 bars  Cm    0.83
bar   44.000  len  0.62 bars  G#m   0.88
bar   44.625  len  0.12 bars  B     0.87
bar   44.750  len  0.44 bars  G#m   0.85
bar   45.188  len  0.50 bars  E     0.87
bar   45.812  len  0.19 bars  G#m   0.78
bar   46.000  len  0.12 bars  E     0.79
bar   46.125  len  0.12 bars  G#m   0.85
bar   46.375  len  0.50 bars  F#    0.90
bar   47.000  len  4.75 bars  G#    0.90
bar   51.750  len  0.19 bars  Fm    0.67
bar   51.938  len  0.19 bars  G#    0.72
```

```
$ cd "~/deadmau5 app"; wc -l mau5scene.py mau5fx.py mau5engine.py mau5show.py; sed -n 1,200p mau5scene.py
    1344 mau5scene.py
     992 mau5fx.py
    1388 mau5engine.py
    1000 mau5show.py
    4724 total
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
element's own clo
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
$ cd "~/deadmau5 app"; W="tools/showkit/songs/chords"; python3 "$W/label.py" 116 170 2; echo; python3 "$W/label.py" 52 116 2 | awk '$5!="G#m"' ; echo; python3 "$W/label.py" 164 240 2 | awk '$5!="G#m"'
bar  117.625  len  0.69 bars  E     0.75
bar  118.375  len  0.19 bars  E     0.71
bar  118.625  len  0.19 bars  E     0.72
bar  119.062  len  0.12 bars  G#m   0.63
bar  119.188  len  0.12 bars  E     0.65
bar  119.375  len  0.19 bars  E     0.66
bar  119.625  len  0.19 bars  E     0.72
bar  119.875  len  1.00 bars  G#m   0.92
bar  120.875  len  1.50 bars  E     0.89
bar  122.375  len  0.50 bars  F#    0.92
bar  122.875  len  1.12 bars  G#    0.91
bar  124.000  len  0.94 bars  G#m   0.88
bar  124.938  len  1.44 bars  E     0.90
bar  126.375  len  0.50 bars  F#    0.87
bar  126.875  len  1.12 bars  G#    0.95
bar  128.000  len  0.88 bars  G#m   0.93
bar  128.875  len  1.50 bars  E     0.86
bar  130.375  len  0.50 bars  F#    0.83
bar  130.875  len  1.12 bars  G#    0.86
bar  132.000  len  0.88 bars  G#m   0.88
bar  132.875  len  1.50 bars  E     0.82
bar  134.375  len  0.50 bars  F#    0.85
bar  134.875  len  0.31 bars  G#    0.81
bar  135.250  len  0.31 bars  G#    0.80
bar  135.625  len  0.38 bars  G#    0.85
bar  136.000  len  0.19 bars  B     0.76
bar  136.188  len  1.12 bars  G#m   0.78
bar  137.312  len  0.62 bars  E     0.85
bar  137.938  len  0.25 bars  G#m   0.81
bar  138.188  len  0.19 bars  E     0.83
bar  138.375  len  0.25 bars  A#m   0.72
bar  138.625  len  0.25 bars  F#    0.84
bar  138.875  len  0.31 bars  G#    0.82
bar  139.250  len  0.12 bars  G#    0.82
bar  139.375  len  0.12 bars  Cm    0.83
bar  139.562  len  0.12 bars  Cm    0.82
bar  139.688  len  0.31 bars  G#    0.83
bar  140.000  len  0.38 bars  B     0.80
bar  140.375  len  0.75 bars  G#m   0.83
bar  141.125  len  0.94 bars  E     0.79
bar  142.125  len  0.19 bars  E     0.83
bar  142.375  len  0.12 bars  F#    0.72
bar  142.500  len  0.12 bars  A#m   0.81
bar  142.625  len  0.25 bars  F#    0
... [cut] ...
len  0.19 bars  G#m   0.69
bar  229.938  len  0.19 bars  G#m   0.61
bar  231.000  len  0.12 bars  D#m   0.56
bar  231.812  len  0.12 bars  Bm    0.57
bar  232.312  len  0.12 bars  Bm    0.56
bar  232.812  len  0.12 bars  Bm    0.56
bar  233.312  len  0.12 bars  Bm    0.55
bar  233.812  len  0.12 bars  Bm    0.56
bar  234.000  len  0.12 bars  A#    0.55
bar  234.312  len  0.12 bars  Bm    0.56
bar  235.312  len  0.12 bars  Bm    0.56
bar  235.500  len  0.12 bars  A#    0.55
bar  235.688  len  0.12 bars  A#m   0.57
bar  235.875  len  0.12 bars  G#    0.65
bar  236.000  len  2.31 bars  G#m   0.85
```

```
$ cd "~/deadmau5 app"; wc -l mau5scene.py mau5fx.py mau5engine.py mau5show.py; sed -n 1,200p mau5scene.py
    1344 mau5scene.py
     992 mau5fx.py
    1388 mau5engine.py
    1000 mau5show.py
    4724 total
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
element's own clo
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
$ cd "~/deadmau5 app"; W="tools/showkit/songs/chords"; python3 "$W/label.py" 116 170 2; echo; python3 "$W/label.py" 52 116 2 | awk '$5!="G#m"' ; echo; python3 "$W/label.py" 164 240 2 | awk '$5!="G#m"'
bar  117.625  len  0.69 bars  E     0.75
bar  118.375  len  0.19 bars  E     0.71
bar  118.625  len  0.19 bars  E     0.72
bar  119.062  len  0.12 bars  G#m   0.63
bar  119.188  len  0.12 bars  E     0.65
bar  119.375  len  0.19 bars  E     0.66
bar  119.625  len  0.19 bars  E     0.72
bar  119.875  len  1.00 bars  G#m   0.92
bar  120.875  len  1.50 bars  E     0.89
bar  122.375  len  0.50 bars  F#    0.92
bar  122.875  len  1.12 bars  G#    0.91
bar  124.000  len  0.94 bars  G#m   0.88
bar  124.938  len  1.44 bars  E     0.90
bar  126.375  len  0.50 bars  F#    0.87
bar  126.875  len  1.12 bars  G#    0.95
bar  128.000  len  0.88 bars  G#m   0.93
bar  128.875  len  1.50 bars  E     0.86
bar  130.375  len  0.50 bars  F#    0.83
bar  130.875  len  1.12 bars  G#    0.86
bar  132.000  len  0.88 bars  G#m   0.88
bar  132.875  len  1.50 bars  E     0.82
bar  134.375  len  0.50 bars  F#    0.85
bar  134.875  len  0.31 bars  G#    0.81
bar  135.250  len  0.31 bars  G#    0.80
bar  135.625  len  0.38 bars  G#    0.85
bar  136.000  len  0.19 bars  B     0.76
bar  136.188  len  1.12 bars  G#m   0.78
bar  137.312  len  0.62 bars  E     0.85
bar  137.938  len  0.25 bars  G#m   0.81
bar  138.188  len  0.19 bars  E     0.83
bar  138.375  len  0.25 bars  A#m   0.72
bar  138.625  len  0.25 bars  F#    0.84
bar  138.875  len  0.31 bars  G#    0.82
bar  139.250  len  0.12 bars  G#    0.82
bar  139.375  len  0.12 bars  Cm    0.83
bar  139.562  len  0.12 bars  Cm    0.82
bar  139.688  len  0.31 bars  G#    0.83
bar  140.000  len  0.38 bars  B     0.80
bar  140.375  len  0.75 bars  G#m   0.83
bar  141.125  len  0.94 bars  E     0.79
bar  142.125  len  0.19 bars  E     0.83
bar  142.375  len  0.12 bars  F#    0.72
bar  142.500  len  0.12 bars  A#m   0.81
bar  142.625  len  0.25 bars  F#    0
... [cut] ...
len  0.19 bars  G#m   0.69
bar  229.938  len  0.19 bars  G#m   0.61
bar  231.000  len  0.12 bars  D#m   0.56
bar  231.812  len  0.12 bars  Bm    0.57
bar  232.312  len  0.12 bars  Bm    0.56
bar  232.812  len  0.12 bars  Bm    0.56
bar  233.312  len  0.12 bars  Bm    0.55
bar  233.812  len  0.12 bars  Bm    0.56
bar  234.000  len  0.12 bars  A#    0.55
bar  234.312  len  0.12 bars  Bm    0.56
bar  235.312  len  0.12 bars  Bm    0.56
bar  235.500  len  0.12 bars  A#    0.55
bar  235.688  len  0.12 bars  A#m   0.57
bar  235.875  len  0.12 bars  G#    0.65
bar  236.000  len  2.31 bars  G#m   0.85
```

```
$ cd "~/deadmau5 app"; KIT="tools/showkit"; W="$KIT/work/chords"; B="deadmau5 - Some Chords"; python3 "$KIT/spectro.py" "$B" "$W/spec_0_26.png" 0 26 | tail -1;  python3 "$KIT/spectro.py" "$B" "$W/spec_26_48.png" 26 48 | tail -1; python3 "$KIT/spectro.py" "$B" "$W/spec_60_100.png" 60 100 | tail -1; python3 "$KIT/spectro.py" "$B" "$W/spec_128_158.png" 128 158 | tail -1;python3 "$KIT/grid.py" fold "shows/$B.mp3" --spb 0.468747 --anchor 0.218 --spans "12-16,16-20,20-24,24-28,28-32,32-36,36-40,40-44,44-47,47-51" | grep -E "bars|bass|sub|air"
tools/showkit/songs/chords/spec_0_26.png
tools/showkit/songs/chords/spec_26_48.png
tools/showkit/songs/chords/spec_60_100.png
tools/showkit/songs/chords/spec_128_158.png
bar 0 at 0.218 s, 128.001 BPM, 238 bars
bars 12-16   (16 steps, | every beat; one row per band)
   sub     +.:.|-.+.|.:.:|::@:   peak 0.56
   bass    =..:|..-:|:  .|. @.   peak 0.68
   air     +--:|*-*.|+-+:|#:@.   peak 0.10
bars 16-20   (16 steps, | every beat; one row per band)
   sub     @=++|+==+|-==#|==@*   peak 0.23
   bass    @:::|-+=.|-:..|::*-   peak 0.29
   air     +:- |-:=.|:.-.|= @    peak 0.22
bars 20-24   (16 steps, | every beat; one row per band)
   sub     *:=:|-+*-|=---|--@-   peak 0.26
   bass    @:.:|+:*:|=+.-|-:@=   peak 0.24
   air     +:-:|.:+.|:-::|:-@.   peak 0.36
bars 24-28   (16 steps, | every beat; one row per band)
   sub     -===|=---|-:-:|=:@-   peak 0.30
   bass    +:-:|*=-.|+.--|=.@.   peak 0.31
   air     @:+-|*.+=|%--+|@:@    peak 0.25
bars 28-32   (16 steps, | every beat; one row per band)
   sub     %+=+|%#+:|@+-+|@#@=   peak 0.23
   bass    #.. |@.:.|@:..|%:=:   peak 0.50
   air     @ . |@ : |@ : |@ -    peak 0.79
bars 32-36   (16 steps, | every beat; one row per band)
   sub     +@+=|+@*=|#@+-|*@*=   peak 0.24
   bass    %.. |%:..|%. .|@:..   peak 0.79
   air     % : |@ - |@ : |@ -    peak 0.84
bars 36-40   (16 steps, | every beat; one row per band)
   sub     %==+|#%*-|*@==|#*%=   peak 0.23
   bass    @:. |@:..|@...|@::.   peak 0.73
   air     @ : |@ - |% ..|% -    peak 0.92
bars 40-44   (16 steps, | every beat; one row per band)
   sub     +#--|+#=-|@+*+|##**   peak 0.21
   bass    %:..|%.. |@:..|@.:.   peak 0.77
   air     @ . |@ - |% : |% -    peak 0.88
bars 44-47   (16 steps, | every beat; one row per band)
   sub     %%*+|+%#=|@@*-|%*@%   peak 0.23
   bass    %:..|@:..|#.. |%:-.   peak 0.84
   air     @ :.|% : |#...|# -.   peak 0.85
bars 47-51   (16 steps, | every beat; one row per band)
   sub     +#++|=#++|#++-|@+*=   peak 0.15
   bass    @..:|%::.|@::.|#::.   peak 0.24
   air     @.:.|% . |#.. |%..    peak 0.50
```

```
$ cd "~/deadmau5 app"; sed -n 200,640p mau5scene.py
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
```

```
$ cd "~/deadmau5 app"; sed -n 640,1344p mau5scene.py
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
                errs.append("%s: no axis %s" % (what, L[k]))
        if L["fx"] == "grad" and L["wave"] not in WAVES:
            errs.append("%s: no wave %s" % (what, L["wave"]))
        if L["fx"] == "sweep":
            if L["shape"] not in SHAPES:
                errs.append("%s: no shape %s" % (what, L["shape"]))
            if L["mode"] not in MODES:
                errs.append("%s: no mode %s"
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
$ cd "~/deadmau5 app"; sed -n 200,640p mau5scene.py
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
```

```
$ cd "~/deadmau5 app"; sed -n 640,1344p mau5scene.py
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
                errs.append("%s: no axis %s" % (what, L[k]))
        if L["fx"] == "grad" and L["wave"] not in WAVES:
            errs.append("%s: no wave %s" % (what, L["wave"]))
        if L["fx"] == "sweep":
            if L["shape"] not in SHAPES:
                errs.append("%s: no shape %s" % (what, L["shape"]))
            if L["mode"] not in MODES:
                errs.append("%s: no mode %s"
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
$ cat > "tools/showkit/songs/chords/per_bar.py" <<'EOF'
#!/usr/bin/env python3
import os,re,sys
import numpy as np
KIT="tools/showkit"
z=np.load(os.path.join(KIT,"work",re.sub(r"\W+","_","deadmau5 - Some Chords.mp3")+".env.npz"))
tt=z["tt"]; spb=0.468747; t0=0.218
B=["sub","bass","lowmid","mid","pres","air"]
lo,hi=int(sys.argv[1]),int(sys.argv[2])
print("bar | beat-onset per band (x10) | offbeat-8th onset | mean level")
for b in range(lo,hi):
    on=[];off=[];lev=[]
    for nm in B:
        e=z[nm+"_od"]; 
        a=0;c=0 ... [cut]
bar | beat-onset per band (x10) | offbeat-8th onset | mean level
   0 |  3  3  3  0  0  0 |  3  3  3  1  0  0 |  8  8  6  1  0  0
   1 |  2  1  1  0  0  0 |  3  4  3  1  0  0 |  9  7  6  1  0  0
   2 |  1  1  1  1  0  0 |  4  4  5  1  0  0 |  9  7  6  1  0  0
   3 |  1  1  1  0  0  0 |  1  1  1  1  0  0 |  8  7  7  2  1  0
   4 |  3  2  3  1  0  0 |  3  2  3  1  0  0 |  8  7  7  2  1  0
   5 |  1  1  1  1  0  0 |  4  3  3  1  0  0 |  9  7  6  2  1  0
   6 |  1  1  1  0  0  0 |  5  5  4  2  0  0 |  8  7  7  3  1  1
   7 |  1  0  1  1  0  0 |  1  0  1  1  0  0 |  8  8  6  3  2  1
   8 |  3  3  3  2  1  0 |  2  2  4  2  1  0 |  8  8  7  4  2  1
   9 |  1  2  1  1  1  0 |  2  3  4  2  1  0 |  9  7  7  4  3  1
  10 |  1  0  1  1  1  1 |  4  5  6  3  1  0 |  7  7  8  5  3  2
  11 |  1  0  0  1  0  0 |  1  0  1  0  1  0 |  7  7  8  5  4  2
  12 |  3  2  3  2  1  1 |  2  3  3  2  2  1 |  7  6  9  6  5  2
  13 |  2  3  1  1  1  1 |  3  3  3  2  2  1 |  7  7  8  7  5  3
  14 |  2  1  1  1  1  1 |  5  4  6  3  1  1 |  7  7  8  7  6  3
  15 |  1  0  0  1  1  1 |  1  1  0  1  1  1 |  7  6  8  8  6  3
  16 |  2  3  3  3  2  1 |  2  1  1  2  2  1 |  8  7  8  7  6  3
  17 |  1  1  1  1  1  1 |  1  2  1  2  2  1 |  7  6  8  8  6  3
  18 |  2  1  1  1  1  1 |  2  1  2  2  2  2 |  8  6  8  8  6  3
  19 |  1  1  0  1  1  1 |  1  1  1  1  0  0 |  6  6  8  8  6  3
  20 |  1  2  1  2  2  2 |  1  1  1  1  2  2 |  6  6  8  8  6  4
  21 |  2  2  1  1  1  1 |  3  2  1  1  2  2 |  8  6  8  8  6  3
  22 |  1  1  1  1  1  1 |  2  2  2  2  2  3 |  7  6  8  9  7  4
  23 |  1  1  1  1  1  0 |  1  1  0  1  1  1 |  6  5  9  9  7  4
  24 |  1  1  2  2  2  2 |  2  2  2  1  1  1 |  6  6  8  9  9  4
  25 |  2  1  1  1  1  1 |  2  3  2  1  1  1 |  7  6  8  8  8  4
  26 |  1  2  1  1  1  2 |  2  1  2  1  2  2 
... [cut] ...
  2  2  5  8  9
 229 |  6 12 11 11 11 10 |  1  1  1  3  7  8 |  2  2  1  4  6  7
 230 |  6 12 12 13 15 16 |  1  1  1  3  8 10 |  2  2  1  3  4  6
 231 |  6 12 12 12 17 17 |  1  1  1  4  8 10 |  2  2  1  3  4  6
 232 |  6 12 12 15 16 16 |  1  1  1  4  8 10 |  2  2  1  3  4  6
 233 |  6 12 12 13 17 17 |  1  1  1  4  8  9 |  2  2  1  3  4  6
 234 |  6 12 12 15 15 16 |  1  1  1  4  8 10 |  2  2  1  3  4  6
 235 |  6 12 12 13 17 17 |  1  1  1  3  7  9 |  2  2  1  2  4  5
 236 |  0  0  0  0  0  0 |  0  0  0  0  0  0 |  0  0  0  0  0  0
 237 |  0  0  0  0  0  0 |  0  0  0  0  0  0 |  0  0  0  0  0  0
```

```
$ cat > "tools/showkit/songs/chords/layout.py" <<'EOF'
import os,sys
sys.path.insert(0,os.getcwd())
import numpy as np, mau5engine as E
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
h=E.Helmet()
W=os.path.dirname(os.path.abspath(__file__))
print(h.n, h.shell.sum(), h.ears.sum())
print("px",h.px.min(),h.px.max(),"py",h.py.min(),h.py.max())
s=h.shell
print("shell px",h.px[s].min(),h.px[s].max(),"py",h.py[s].min(),h.py[s].max())
print("shell er",h.er[s].min(),h.er[s].max(),"ea",h.ea[s].min(),h.ea[s].max())
print("shell nfa",h.nfa[s].min(),h.nfa[s].max(),"nel",h.nel[s].min(),h.nel[s].m ... [cut]
621 398 223
px -388.21 387.42 py -111.27 384.91
shell px -170.94 170.95 py -111.27 167.77
shell er 0.03929154446196175 1.0 ea 0.004374306928113342 0.9891721577339918
shell nfa 0.16035751702193546 0.8399804407362015 nel 0.0 1.0
ear1 px -388.21 -55.76 py 51.8 383.94
ear2 px 55.56 387.42 py 54.72 384.91
Sat Oct 31 12:45:48 PDT 2026
```

```
$ cat > "tools/showkit/songs/chords/steps.py" <<'EOF'
#!/usr/bin/env python3
"""steps.py from to: per-16th level (L) and onset (O) of each band."""
import os,re,sys
import numpy as np
KIT="tools/showkit"
z=np.load(os.path.join(KIT,"work",re.sub(r"\W+","_","deadmau5 - Some Chords.mp3")+".env.npz"))
tt=z["tt"]; spb=0.468747; t0=0.218
B=["sub","bass","lowmid","mid","pres","air"]
lo,hi=float(sys.argv[1]),float(sys.argv[2])
s=lo
print("    bar   | level: "+" ".join("%6s"%b for b in B)+"  | onset: "+" ".join("%6s"%b for b in B) ... [cut]
    bar   | level:    sub   bass lowmid    mid   pres    air  | onset:    sub   bass lowmid    mid   pres    air
  51.000  |   1.09   1.11   1.57   1.52   1.82   1.03 |   0.08   0.04   0.09   0.15   0.08   0.11
  51.062  |   1.21   1.15   1.53   1.50   1.85   1.04 |   0.10   0.06   0.07   0.09   0.06   0.06
  51.125  |   1.25   1.16   1.46   1.54   1.83   1.07 |   0.08   0.04   0.12   0.10   0.06   0.07
  51.188  |   1.17   1.14   1.50   1.44   1.83   1.05 |   0.07   0.05   0.05   0.14   0.11   0.11
  51.250  |   1.12   1.12   1.50   1.57   1.90   1.13 |   0.11   0.04   0.11   0.14   0.11   0.11
  51.312  |   1.25   1.16   1.43   1.47   1.85   1.13 |   0.13   0.04   0.06   0.10   0.05   0.07
  51.375  |   1.26   1.17   1.40   1.52   1.91   1.24 |   0.09   0.05   0.12   0.12   0.17   0.08
  51.438  |   1.19   1.15   1.41   1.40   1.91   1.36 |   0.09   0.04   0.07   0.23   0.04   0.08
  51.500  |   1.19   1.13   1.36   1.53   1.88   1.49 |   0.10   0.04   0.08   0.23   0.09   0.09
  51.562  |   1.28   1.15   1.35   1.51   1.98   1.61 |   0.10   0.04   0.10   0.12   0.09   0.09
  51.625  |   1.25   1.15   1.32   1.54   1.96   1.77 |   0.11   0.04   0.10   0.09   0.05   0.09
  51.688  |   0.85   0.75   1.10   1.40   2.03   2.01 |   0.18   0.81   1.30   1.21   0.50   0.43
  51.750  |   0.65   1.14   0.96   1.99   2.60   2.72 |   0.23   0.81   1.30   1.21   0.50   0.43
  51.812  |   0.39   0.82   0.71   1.68   2.05   2.04 |   0.15   0.25   0.14   0.11   0.09   0.06
  51.875  |   0.18   0.52   0.76   1.68   2.05   2.00 |   0.10   0.18   0.16   0.10   0.11   0.05
  51.938  |   0.09   0.55   0.74   1.70   1.98   1.93 |   1.06   1.27   0.64   0.27   0.44   0.61
  52.000  |   2.17   1.05   0.63   0.80   1.12   1.63 |   1.06   1.27   0.64   0.27   0.44   0.61
  52.062  |   1.97   
... [cut] ...
 0.31   0.22
 196.125  |   0.78   0.88   1.30   1.70   1.94   1.89 |   0.16   0.34   0.28   0.38   0.31   0.22
 196.188  |   0.12   0.24   0.55   1.19   1.87   1.87 |   0.82   1.21   0.98   0.72   0.60   0.51
 196.250  |   2.16   1.06   0.72   1.14   1.62   2.01 |   0.93   1.21   0.98   0.72   0.60   0.51
 196.312  |   1.97   0.69   0.78   1.07   1.41   1.50 |   0.32   0.23   0.24   0.30   0.38   0.29
 196.375  |   0.83   0.95   1.33   1.68   1.87   1.82 |   0.22   0.21   0.24   0.30   0.38   0.33
 196.438  |   0.12   0.20   0.48   1.13   1.74   1.78 |   1.20   1.29   1.24   0.85   0.70   0.95
```

```
$ cat > "tools/showkit/songs/chords/fold2.py" <<'EOF'
#!/usr/bin/env python3
"""fold2.py lo hi period_bars : onset folded per 16th over a period, per band."""
import os,re,sys
import numpy as np
KIT="tools/showkit"
z=np.load(os.path.join(KIT,"work",re.sub(r"\W+","_","deadmau5 - Some Chords.mp3")+".env.npz"))
tt=z["tt"]; spb=0.468747; t0=0.218
B=["sub","bass","lowmid","mid","pres","air"]
CH=" .:-=+*#%@"
lo,hi,per=int(sys.argv[1]),int(sys.argv[2]),int(sys.argv[3])
print("bars %d-%d folded over %d bars"%(lo,hi,per))
for nm i ... [cut]
bars 60-66 folded over 2 bars
  sub     = . |% . |@ .%|. #-|@ ..|@ . |% .%|: =.  peak 1.16
  bass    * : |#.. |@.:.|= - |#.. |@ : |%...|+..   peak 1.53
  lowmid  =.- |%.. |@.: |-:  |%.: |% : |#...|:. .  peak 1.35
  mid     - = |%.. |% : |-  .|- : |@.- |% : |=  .  peak 1.53
  pres    + - |@ : |* : |=   |= : |* : |% : |=  .  peak 2.04
  air     + - |@ : |# - |-   |= : |# - |@ : |=  .  peak 2.00
bars 76-82 folded over 2 bars
  sub     = . |% . |@  #|  #-|@ : |@   |%  #|. =.  peak 1.19
  bass    *.. |#.. |@...|= - |# : |@.. |@...|=..   peak 1.52
  lowmid  =.: |%.. |@.: |-:  |%.: |%.: |#...|:. .  peak 1.34
  mid     - - |%.: |% : |-  .|-.: |@.- |% : |-  .  peak 1.52
  pres    + - |@ - |# : |=   |+ : |# : |% : |=  .  peak 1.89
  air     *:*:|= +:|%:+:|= --|+.+:|* +.|@:+:|= ::  peak 1.54
bars 92-98 folded over 2 bars
  sub     =   |% . |@ .#|. #-|@ ..|@   |# .#|. =   peak 1.21
  bass    *.. |#.. |@ ::|= - |#.: |@ . |@...|+.:   peak 1.52
  lowmid  =.- |%.: |@.- |--  |%.: |%.- |#.:.|:. .  peak 1.35
  mid     - = |%.- |@ - |-.  |- - |@.= |% - |=. .  peak 1.48
  pres    + - |@ - |* - |+.  |+ - |* - |% - |=  .  peak 1.91
  air     *:+ |+ =.|%:+.|= .-|+.+.|* + |@:+ |= .:  peak 1.60
bars 108-114 folded over 2 bars
  sub     = . |% . |@  #|. *-|@ : |@   |#  #|. =   peak 1.23
  bass    #.. |#.. |@...|= :.|# . |@ . |@  .|*.:   peak 1.51
  lowmid  + : |%.. |@.. |-:  |%.: |@.: |#.. |:. .  peak 1.30
  mid     =.+.|%.+ |%.- |+:  |+:- |@.- |*.= |*. .  peak 0.96
  pres    @ * |% * |% = |%: .|#.+ |@ + |+ * |#. :  peak 0.82
  air     #-#.|+ *.|@:*.|+ .-|#:*.|% *.|@:#.|* .-  peak 1.19
bars 164-170 folded over 2 bars
  sub     # . |# ..|# .#|. *-|% : |@  .|* .%|. =   peak 1.22
  bass    % : |%.  |=..:|= -.|#.. |@.: |+. .|*.:.  peak 1.46
  lowmid  =.= |%.:.|:.: |-= :|#.: |@ -.|:.:.|-: :  peak 1.24
... [cut] ...
|%   |@     peak 1.30
  mid     @ : |@ : |% : |@.. |# : |@.. |@ : |#..   peak 1.57
  pres    * = |@ - |* = |# - |% = |# - |% = |@ :   peak 1.99
  air     # = |@ = |# + |# + |@ + |* = |@ + |@ -   peak 1.94
bars 36-46 folded over 2 bars
  sub     #+=+|-%+-|*@+=|+=#%|%*==|@%*-|@*+-|%@%+  peak 0.22
  bass    #:. |%...|%:. |%.:.|@:..|#.  |%. .|%.:.  peak 0.85
  lowmid  ##:.|*#*-|+*--|+*#:|%#:.|++::|@*.-|%*%-  peak 0.30
  mid     @=. |#-:.|#-:.|*--.|@=..|*-..|@=. |#-:.  peak 0.53
  pres    +:..|%...|-:..|+::.|=:..|#:..|-:. |@...  peak 0.62
  air     @ : |@ :.|% :.|* - |@ . |% : |# . |@ -   peak 0.94
```

```
$ cd "~/deadmau5 app"; KIT="tools/showkit"; W="$KIT/work/chords"; B="deadmau5 - Some Chords"; python3 "$KIT/spectro.py" "$B" "$W/spec_84_88.png" 84 88 | tail -1; python3 "$KIT/spectro.py" "$B" "$W/spec_132_136.png" 132 136 | tail -1; grep -n "class Sprite" -A60 mau5fx.py | head -120; grep -n "SPRITES" mau5fx.py | head; date
tools/showkit/songs/chords/spec_84_88.png
tools/showkit/songs/chords/spec_132_136.png
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
590-        self.bmps = [sprite_bitmap(s) for s in sprites]
591-        self.rate = fps
592-        self.col = col
593-        self.row = row_from_top
594-
595-    def render(self, buf, i, t):
596-        n = (self.beats.index(t) if self.beats is not None
597-             else int((t - self.origin) * self.rate))
598-        bmp = self.bmps[n % len(self.bmps)]
599-        col = -int(round((bmp.shape[1] - 1) / 2.0)) if self.col is None else self.col
600-        self.clear()
601-        self.blit(bmp, col, self.row)
602-    
... [cut] ...
s) * helmet.rows
636-        self.active = self.rng.random(helmet.channels) < 0.5
637-
638-    def render(self, buf, i, t):
639-        self.clear()
640-        rows = self.h.rows
641-        head = (self.offset + (t - self.origin) * self.speed) % (rows + self.tail + 4)
642-        for c in range(self.h.channels):
643-            if not self.active[c]:
644-                continue
134:SPRITES = {
266:                SPRITES[name] = list(rows)
275:    rows = SPRITES[name_or_rows] if isinstance(name_or_rows, str) else name_or_rows
989:    for name in sorted(SPRITES):
Sat Oct 31 12:47:49 PDT 2026
```

```
$ cd "~/deadmau5 app"; sed -n 255,300p mau5fx.py; grep -n '"sprite"' -n mau5engine.py | head; grep -n "class .*Sprite\|class SpriteLayer\|def sprite" mau5engine.py mau5fx.py | head; grep -n "class Eyes\|class Text\|\"eyes\"\|\"text\"" mau5engine.py | head
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
    rows = SPRITES[name_or_rows] if isinstance(name_or_rows, str) else name_or_rows
    w = max(len(r) for r in rows)
    return np.array([[c not in ".  " for c in r.ljust(w)] for r in rows], bool)


# --------------------------------------------------------------------------
# beats
# --------------------------------------------------------------------------
class Beats:
    """A pre-computed beat list.  No live audio analysis -- shows are authored."""

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
713:    name = "sprite"
714:    params = {"sprite": "smile", "color": (0, 255, 255), "bg": (0, 0, 0),
722:        names = self.p["sprite"].split("|")
mau5fx.py:274:def sprite_bitmap(name_or_rows):
mau5fx.py:567:class Sprite(GridEffect):
mau5fx.py:584:class SpriteFlipbook(GridEffect):
mau5engine.py:704:class SpriteShow(Preset):
310:                out.append({"name": k, "kind": "text", "value": v})
674:class TextScroll(Preset):
676:    name = "text"
682:    params = {"text": "DEADMAU5", "color": (255, 160, 0), "bg": (0, 0, 0),
687:        bm = _text_bitmap(self.p["text"], spacing=1)
743:class Eyes(Preset):
745:    name = "eyes"
```

```
$ cd "~/deadmau5 app"; sed -n 255,300p mau5fx.py; grep -n '"sprite"' -n mau5engine.py | head; grep -n "class .*Sprite\|class SpriteLayer\|def sprite" mau5engine.py mau5fx.py | head; grep -n "class Eyes\|class Text\|\"eyes\"\|\"text\"" mau5engine.py | head
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
    rows = SPRITES[name_or_rows] if isinstance(name_or_rows, str) else name_or_rows
    w = max(len(r) for r in rows)
    return np.array([[c not in ".  " for c in r.ljust(w)] for r in rows], bool)


# --------------------------------------------------------------------------
# beats
# --------------------------------------------------------------------------
class Beats:
    """A pre-computed beat list.  No live audio analysis -- shows are authored."""

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
713:    name = "sprite"
714:    params = {"sprite": "smile", "color": (0, 255, 255), "bg": (0, 0, 0),
722:        names = self.p["sprite"].split("|")
mau5fx.py:274:def sprite_bitmap(name_or_rows):
mau5fx.py:567:class Sprite(GridEffect):
mau5fx.py:584:class SpriteFlipbook(GridEffect):
mau5engine.py:704:class SpriteShow(Preset):
310:                out.append({"name": k, "kind": "text", "value": v})
674:class TextScroll(Preset):
676:    name = "text"
682:    params = {"text": "DEADMAU5", "color": (255, 160, 0), "bg": (0, 0, 0),
687:        bm = _text_bitmap(self.p["text"], spacing=1)
743:class Eyes(Preset):
745:    name = "eyes"
```

```
$ cd "~/deadmau5 app"; sed -n 674,790p mau5engine.py; grep -n "def frame" -A40 mau5show.py | sed -n 1,90p
class TextScroll(Preset):
    """Scrolling text across the face, laid out flat so it reads."""
    name = "text"
    # The band is where the LEDs actually are: below py~28 is the visor
    # cutout and there is nothing to light.  7 rows over 28..145 mm puts
    # one glyph row per strip pitch, which is the finest the hardware
    # can resolve -- about 14-20 columns across, so two or three
    # characters are legible at once and the rest has to scroll.
    params = {"text": "DEADMAU5", "color": (255, 160, 0), "bg": (0, 0, 0),
              "speed": 70.0, "y_lo": 28.0, "y_hi": 145.0,
              "cell": 16.7, "loop": True, "gap": 6}

    def render(self, h, t, music=None):
        bm = _text_bitmap(self.p["text"], spacing=1)
        rows, w = bm.shape
        if self.p["loop"]:
            bm = np.concatenate([bm, np.zeros((rows, self.p["gap"]), bool)], 1)
            w = bm.shape[1]
        out = np.tile(np.array(self.p["bg"], float), (h.n, 1))

        lo, hi = self.p["y_lo"], self.p["y_hi"]
        ry = (hi - h.py) / max(hi - lo, 1e-6) * rows
        rx = h.px / self.p["cell"] + t * self.p["speed"] / self.p["cell"]

        lit = paint(bm, ry, rx, h.shell & (h.py > 0),
                    wrap=w if self.p["loop"] else None)
        out[lit] = self.p["color"]
        return out


class SpriteShow(Preset):
    """One of the built-in faces, held on the front of the helmet.

    `sprite` may be several names joined by |, shown in turn `rate` times a
    second, as a flip book.  dx and dy move it in mm, vx and vy in mm a
    second, and wx and wy swing it round an ellipse wf times a second.  All
    of it is a function of t, so a moving sprite is still a pure function
    of the time and the phone and the laptop still agree.
    """
    name = "sprite"
    params = {"sp
... [cut] ...
 self.dyn * float(e) ** self.dyn_gamma
802-                out = out * k
803-            # A pulse on every beat, scaled by how loud the section is --
804-            # a breakdown should breathe, a drop should hit.  It is not
805-            # applied here.  Multiplied into the frame it was exactly
806-            # what the power guard exists to take away again -- the
807-            # per-LED ceilings and the governor flatten anything loud --
808-            # and the shows measured 1.00-1.06 on-beat over half a beat
809-            # later.  So the frame is left as written and the pulse is
```

```
$ cd "~/deadmau5 app"; grep -n "SPRITES\|sprites.json\|sprite" mau5offline.py | head -30; grep -n "def paint" -A28 mau5engine.py | head -60; ls -la remote/offline | head -30; ls shows/scenes | grep sprites; date
73:    from mau5fx import FONT5x7, SPRITES
96:            "sprites": {k: list(v) for k, v in SPRITES.items()},
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
657-    lit[idx] = bm[r[idx], cw[idx]]
total 552
drwxr-xr-x@ 15 jones  staff    480 Oct 30 05:03 .
drwxr-xr-x@  8 jones  staff    256 Oct 30 04:05 ..
-rw-r--r--@  1 jones  staff  26049 Oct 31 12:44 audio.js
-rw-r--r--@  1 jones  staff   1715 Oct 28 11:57 crosscheck.js
-rw-r--r--@  1 jones  staff   6611 Oct 31 12:44
... [cut] ...
31 12:44 player.html
-rw-r--r--@  1 jones  staff  30628 Oct 31 12:34 show.js
-rw-r--r--@  1 jones  staff   2779 Oct 30 05:03 showtest.js
-rw-r--r--@  1 jones  staff   9082 Oct 31 12:44 spotify.js
-rw-r--r--@  1 jones  staff  72154 Oct 31 12:45 ui.js
-rw-r--r--@  1 jones  staff  44690 Oct 30 19:33 wire.js
-rw-r--r--@  1 jones  staff   2476 Oct 30 02:44 wiretest.js
Kaskade feat. deadmau5 - I Remember.sprites.json
deadmau5 & Wolfgang Gartner - Animal Rights.sprites.json
deadmau5 - Moar Ghosts n Stuff.sprites.json
deadmau5 - Strobe (Special Features Remix).sprites.json
Sat Oct 31 12:49:33 PDT 2026
```

```
$ cd "~/deadmau5 app"; sed -n 657,674p mau5engine.py; cat "shows/scenes/deadmau5 - Moar Ghosts n Stuff.sprites.json" | python3 -c "
import json,sys
d=json.load(sys.stdin)
for k,v in d.items(): print(k,len(v),len(v[0]))
print('\n'.join(list(d.values())[0]))"
    lit[idx] = bm[r[idx], cw[idx]]

    occupied = np.zeros((rows, cols), bool)
    occupied[r[idx], cw[idx]] = True
    missing = bm & ~occupied
    if missing.any():
        rr, cc = np.where(missing)
        lr = rowf[idx]
        lc = (colf[idx] % cols) if wrap else colf[idx]
        d = np.hypot((lr[None, :] - (rr[:, None] + 0.5)) * row_w,
                     lc[None, :] - (cc[:, None] + 0.5))
        j = d.argmin(1)
        take = d[np.arange(len(rr)), j] <= reach
        lit[idx[j[take]]] = True
    return lit


class TextScroll(Preset):
moar_gR_a 8 8
moar_gR_b 8 8
moar_gL_a 8 8
moar_gL_b 8 8
moar_gF_a 8 8
moar_gF_b 8 8
moar_eR 8 8
moar_eL 8 8
moar_eF 8 8
moar_f_a 8 8
moar_f_b 8 8
moar_pac_o 8 8
moar_pac_h 8 8
moar_pac_c 8 8
moar_G_R_a 17 17
moar_G_R_b 17 17
moar_G_L_a 17 17
moar_G_L_b 17 17
moar_G_F_a 17 17
moar_G_F_b 17 17
moar_F_a 17 17
moar_F_b 17 17
moar_Fface_a 17 17
moar_Fface_b 17 17
moar_Gw_R 17 17
moar_Gw_L 17 17
moar_Gw_F 17 17
moar_boo 5 18
..XXXX..
.XXXXXX.
XXX.XX.X
XXX.XX.X
XXXXXXXX
XXXXXXXX
XXXXXXXX
X.XX.XX.
```

```
$ cd "~/deadmau5 app"; grep -n -i "gamma" mau5power.py mau5engine.py mau5show.py mau5ctl.py 2>/dev/null | head -20; grep -n -i "gamma" remote/offline/*.js | head; grep -n "def apply" -A30 mau5power.py | head -70; sed -n 1,40p "$HOME/.claude/projects/-Users-jones-deadmau5-app/memory/controller-state-and-open-decisions.md" 2>/dev/null | head -40
mau5show.py:687:        self.dyn_gamma = float(show.get("dynamics_gamma", 0.7))
mau5show.py:801:                k = (1.0 - self.dyn) + self.dyn * float(e) ** self.dyn_gamma
remote/offline/show.js:103:    this.dynGamma = show.dynamics_gamma === undefined ? 0.7 : show.dynamics_gamma;
remote/offline/show.js:237:        const k = (1 - this.dyn) + this.dyn * Math.pow(Math.max(e, 0), this.dynGamma);
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
258-        # no budget compares greater than, and its ther
... [cut] ...
-30 09:00** (`/presets.json` `{"0":{}}`);
  the page switches off on stop. The page's "set up" button next to standby
  glow measures pacifica and saves preset 1 plus the boot preset. Deployed to the
  helmet 2026-10-30, tested against a stand-in only, so check whether it
  has been pressed.
- **WLED 16's limiter is the global `hw.led.maxpwr` (1622), not the per-bus cap.**
  `applyABL` ignores bus caps while the global is non-zero, and it covers phone
  and laptop DDP frames too, so frames above about 0.9 A of LED current get
  scaled (source only, not measured). `mau5offline config/check` and
```

```
$ cat > "tools/showkit/songs/chords/melody.py" <<'EOF'
#!/usr/bin/env python3
"""Top line of the lead per 8th: strongest narrow peak 500-1400 Hz in the harmonic-ish spectrum."""
import os,sys
import numpy as np
W=os.path.dirname(os.path.abspath(__file__))
m=np.load(os.path.join(W,"mono.npy")); SR=22050
spb=0.468747; t0=0.218
NOTES="C C# D D# E F F# G G# A A# B".split()
lo,hi=float(sys.argv[1]),float(sys.argv[2])
N=8192; win=np.hanning(N); f=np.fft.rfftfreq(N,1/SR)
sel=np.flatnonzero((f>=450)&(f<1500))
midi=69+12*np.log2(f[sel]/440.0)
keys=np.arange(int(np.floor(midi.min())),int(np.ceil(midi.max()))+1)
rows=[ ... [cut]
 128.000  B4   (71)   next: C5 C#5
 128.250  B5   (83)   next: B4 C6
 128.375  B4   (71)   next: B5 A#4
 128.625  B5   (83)   next: C6 B4
 128.750  B4   (71)   next: A#4 B5
 128.812  A#4  (70)   next: B4 A#5
 129.000  A#5  (82)   next: B5 A5
 129.188  G#5  (80)   next: A5 G5
 129.750  B4   (71)   next: D#5 F#5
 129.812  G#5  (80)   next: B4 D#5
 129.875  B4   (71)   next: D#5 G#5
 129.938  D#5  (75)   next: G#5 D#6
 130.000  G#5  (80)   next: A5 G5
 130.438  A#4  (70)   next: G#5 A5
 130.562  A#5  (82)   next: A#4 B5
 130.750  A#4  (70)   next: A#5 B4
 130.938  A#5  (82)   next: B5 A5
 131.062  C5   (72)   next: A#5 D#5
 131.312  C6   (84)   next: C5 B5
 131.438  C5   (72)   next: C6 B4
 131.688  C6   (84)   next: C5 C#6
 131.812  C5   (72)   next: C6 B5
 132.000  B4   (71)   next: C5 A#4
 132.250  B5   (83)   next: B4 C6
 132.375  B4   (71)   next: B5 C5
 132.625  B5   (83)   next: B4 C6
 132.750  A#4  (70)   next: B4 B5
 133.000  A#5  (82)   next: B5 A5
 133.188  F#5  (78)   next: G5 F5
 133.750  D#5  (75)   next: G#5 D5
 133.812  G#5  (80)   next: D5 D#5
 133.875  D#5  (75)   next: G#5 F#5
 133.938  G#5  (80)   next: D#5 B4
 134.438  A#4  (70)   next: G#5 G5
 134.562  C#6  (85)   next: A#4 D6
 134.688  A#4  (70)   next: C#5 C#6
 134.750  C#5  (73)   next: A#4 D5
 134.875  C5   (72)   next: C#5 C#6
 134.938  C#6  (85)   next: C5 D6
 135.062  C5   (72)   next: C#5 C#6
 135.312  C6   (84)   next: C5 C#6
 135.438  C5   (72)   next: C6 B4
 135.688  C6   (84)   next: C5 C#6
 135.812  C5   (72)   next: C6 B5
 135.938  B4   (71)   next: C5 C6
 136.250  B5   (83)   next: B4 C6
 136.375  B4   (71)   next: B5 C5
 136.688  B5   (83)   next: B4 C6
 136.750  B4   (71)   next: A#4 B5
 136.812  A#4  (70)   next: B4 A#5
 137.000  A#5  (82)   next: B5 A5
 137.125  G#5  (80)   next: A#
... [cut] ...
xt: B4 D#6
 144.750  B4   (71)   next: A#4 B5
 144.812  A#4  (70)   next: B4 A#5
 145.000  A#5  (82)   next: B5 A5
 145.188  G#5  (80)   next: D#5 C6
 145.688  D#5  (75)   next: F#6 C6
 145.812  G#5  (80)   next: D#5 C6
 145.938  D#6  (87)   next: G#5 C6
 146.000  G#5  (80)   next: C6 A5
 146.500  A#4  (70)   next: A#5 G#5
 146.562  A#5  (82)   next: A#4 B5
 146.688  A#4  (70)   next: F5 A#5
 146.938  A#5  (82)   next: B5 A5
 147.062  C5   (72)   next: G5 A#5
 147.625  C6   (84)   next: C5 E6
 147.812  C5   (72)   next: C6 G5
 147.875  G5   (79)   next: C5 D#5
 147.938  C5   (72)   next: G5 C6
```

```
$ cd "~/deadmau5 app"; sed -n 150,236p mau5power.py; sed -n 262,360p mau5power.py; python3 - <<'EOF'
import sys,os
sys.path.insert(0,os.getcwd())
import numpy as np, mau5engine as E, mau5scene as S
h=E.Helmet()
for r in ("face","jaw","left","right","tube0","tube1","tube2","rims"):
    print(r, S._region_mask(h,r).sum())
EOF
        # NaN plus anything is NaN and the clamp below keeps it, so one
        # bad reading used to switch the ramp off for good (the phone's
        # twin did exactly that).  A reading that is not a number is not
        # a reading: skip it and keep the level we had.
        if not (math.isfinite(led_watts) and math.isfinite(now)):
            return self.allowance_w()
        if self._last is None:
            self._last = now
            return self.allowance_w()
        dt = max(0.0, min(now - self._last, 5.0))   # ignore long stalls
        self._last = now
        total = led_watts + self.standby_w
        self.level += (total - self.sustained_w) * dt
        self.level = min(max(self.level, 0.0), self.burst_j)
        return self.allowance_w()

    def state(self):
        return {"level_j": round(self.level, 1), "burst_j": self.burst_j,
                "full_pct": round(100.0 * self.level / max(self.burst_j, 1e-6), 1),
                "allowance_w": round(self.allowance_w(), 2),
                "sustained_w": self.sustained_w, "standby_w": self.standby_w}


class PowerGuard:
    """Clamps a frame to what the helmet can survive."""

    def __init__(self, count, regions, budget_ma, default_ceiling=32,
                 thermal=None, link_ma=0.0):
        self.count = int(count)
        self.thermal = thermal
        self.regions = sorted(regions, key=lambda r: r.lo)
        self.budget_ma = float(budget_ma)
        # What the weakest connector between the supply and the strips
        # can carry, continuously, in total.  The budget above is about
        # heat in the helmet and headroom at the supply; neither is the
        # real ceiling if the current has to cross a contact that
        # cannot take it.  A Dupont pin is rated about an amp, and this
      
... [cut] ...
plit and made it jitter more: one frame
        # over budget then held the shell down for two seconds.  Half
        # this rate cost up to 15%.
        cap = 1.0
        if self._gov_s < 1.0:
            dt = (now - self._gov_t
                  if self._gov_t is not None and math.isfinite(now) else 0.0)
            cap = min(1.0, max(self._gov_s, GOV_FROM)
                      * math.exp(GOV_RISE * min(max(dt, GOV_MIN_DT), 5.0)))
        over = after_region > budget and after_region > 0
        governed = floored = False
face 302
jaw 96
left 200
right 198
tube0 58
tube1 72
tube2 56
rims 37
```

```
$ cd "~/deadmau5 app"; sed -n 1,60p mau5power.py | head -90; grep -n "MA_PER_LED_FULL_WHITE\s*=\|MA_PER_LED_STANDBY\s*=\|GOV_" mau5power.py | head; grep -n "def load" -A40 mau5power.py | head -70; ls *.json power* 2>/dev/null; python3 - <<'EOF'
import sys,os
sys.path.insert(0,os.getcwd())
import mau5power
g=mau5power.load(count=621)
for r in g.regions: print(r.name,r.lo,r.hi,"ceil",r.ceiling,"budget",r.budget_ma,"shed",r.shed,"floor",r.floor)
print("budget",g.budget_ma,"link",g.link_ma,"thermal", g.thermal.state() if g.thermal else None)
EOF
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

# How fast the governor may give light back,
... [cut] ...
                  "max_w": th.max_w, "standby_w": th.standby_w,
499-                            "ramp": th.ramp} if th else None),
(eval):1: no matches found: *.json
shell 0 397 ceil 64 budget 300.0 shed 6.0 floor 3.0
ear1_tubes 398 491 ceil 255 budget 620.0 shed 1.0 floor 6.0
ear1_rim 492 509 ceil 160 budget 200.0 shed 3.0 floor 5.0
ear2_rim 510 528 ceil 160 budget 190.0 shed 3.0 floor 5.0
ear2_tubes 529 620 ceil 255 budget 640.0 shed 1.0 floor 6.0
budget 1000.0 link 0.0 thermal {'level_j': 0.0, 'burst_j': 3000.0, 'full_pct': 0.0, 'allowance_w': 18.05, 'sustained_w': 11.0, 'standby_w': 7.452}
```

```
$ cat > "tools/showkit/songs/chords/panes.py" <<'EOF'
#!/usr/bin/env python3
"""The window: a fanlight on the dome, two lancets on the jaw.  Writes the sprites."""
import json, math, os, sys
sys.path.insert(0, os.getcwd())
import numpy as np, mau5engine as E
BASE = "deadmau5 - Some Chords"
h = E.Helmet()
s = np.asarray(h.shell, bool)
X, Y = h.px[s], h.py[s]
COLS, ROWS = 30, 28
Y_LO, Y_HI, X_HALF = -112.0, 170.0, 172.0
HUB = (0.0, 28.0)
NW = 7          # wedges in the fan
HUB_R = 62.0    # the inner arc
LEAD = 9.0      # half width of a lead line, mm

def pane_of(x, y):
    """-1 lead, 0..6 wedges (right to l ... [cut]
{-1: 99, 0: 35, 1: 34, 2: 24, 3: 18, 4: 25, 5: 34, 6: 35, 7: 10, 10: 1, 11: 8, 12: 33, 13: 1, 14: 8, 15: 33}
shows/scenes/deadmau5 - Some Chords.sprites.json 9715 bytes 10 sprites
..............................
............#....##...........
.......#...#.#...#....#.......
......###...#....#...###......
.......#....##..##....#.......
........##..##..##..##........
.........##..#..#..##.........
..####...##..####..##...####..
..............................
....####..##......##..####....
........###........###........
..............................
..............................
..............................
..............................
..............................
..............................
..............................
..............................
..............................
..............................
..............................
..............................
.##........................##.
..............................
..............................
..............................
..............................
tools/showkit/songs/chords/try1.png (1800, 338)
```

```
$ cat > "tools/showkit/songs/chords/panesplot.py" <<'EOF'
import os,sys,math
sys.path.insert(0,os.getcwd())
import numpy as np, mau5engine as E
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
h=E.Helmet(); s=np.asarray(h.shell,bool); X,Y=h.px[s],h.py[s]
W=os.path.dirname(os.path.abspath(__file__))
def pane(x,y,HUB=(0,30),NW=7,LEAD=6.5):
    if y<=28:
        for cut in (-20.0,-75.0):
            if abs(y-cut)<7: return -1
        return 10
    r=math.hypot(x-HUB[0],y-HUB[1]); th=max(0,min(180,math.degrees(math.atan2(y-HUB[1],x-HUB[0]))))
    k=th/(180.0/NW); i=min(NW-1,int(k))
    d= ... [cut]
{-1: 75, 0: 45, 1: 40, 2: 29, 3: 23, 4: 31, 5: 40, 6: 33, 10: 82}
```

```
$ cd "~/deadmau5 app"; W="tools/showkit/songs/chords"; python3 "$W/melody.py" 148 164 | awk '{print $1,$2}' | tr '\n' ';' ; echo; python3 "$W/melody.py" 40 52 | awk '{print $1,$2}' | tr '\n' ';' ; date
148.000 F#5;148.062 B5;148.188 B4;148.688 B5;148.750 B4;148.812 A#4;149.000 A#5;149.188 F#5;149.312 D#5;149.375 F#5;149.688 C6;149.875 G#5;149.938 D#5;150.000 D#6;150.062 G#5;150.375 A#4;150.812 C#5;150.875 C5;151.000 C#6;151.062 C5;151.625 G5;151.688 C6;151.812 G5;151.875 C6;151.938 G5;152.000 B4;152.250 B5;152.438 B4;152.625 B5;152.750 A#4;153.000 A#5;153.125 G#5;153.312 D#5;153.375 G#5;153.688 D#6;154.000 G#5;154.125 D#5;154.188 G#5;154.375 A#4;154.438 G#5;154.500 A#4;154.562 A#5;154.688 A#4;154.938 C5;155.312 C6;155.438 C5;156.000 B4;156.250 B5;156.438 B4;156.562 F#5;156.625 C6;156.688 B5;156.750 A#4;157.000 A#5;157.125 D#5;157.250 G#5;157.375 F#5;157.688 D#6;157.812 G#5;157.875 D#6;158.062 G#5;158.375 F#5;158.438 G#5;158.500 A#4;158.625 C#6;158.688 C#5;158.875 D#5;158.938 C#6;159.062 C5;159.312 C6;159.438 C5;160.062 C6;160.188 C5;160.500 C6;160.562 C5;160.875 D#5;161.188 C6;161.312 D#5;161.438 C5;161.562 C6;161.688 D#5;161.750 C5;161.812 D#5;162.000 C5;162.062 D#5;162.125 C5;162.750 D#5;162.812 C5;162.938 D#5;163.750 D#6;163.812 B5;163.938 D#6;
40.000 C5;40.062 B4;40.438 D#6;40.500 F#5;40.812 B4;40.875 D#5;40.938 D#6;41.125 D#5;41.188 D#6;41.250 C6;41.312 D#5;41.438 G#5;41.562 D#6;41.688 D#5;41.750 G#5;41.875 D#5;41.938 C6;42.125 D#5;42.250 G#5;42.312 C6;42.375 F5;42.562 A#4;42.875 C5;43.312 G5;43.625 C5;44.062 B4;44.438 D#6;44.562 D#5;44.688 F#5;44.750 B4;44.812 D#5;44.938 G#5;45.125 D#5;45.188 C6;45.312 D#5;45.438 G#5;45.625 D#6;45.688 D#5;45.812 G#5;45.875 C6;46.000 G#5;46.125 D#6;46.188 G#5;46.375 A#4;46.438 F#5;46.875 D#5;46.938 C5;47.062 D#5;47.125 C5;47.500 D#5;47.625 C6;47.688 G5;47.875 C5;48.188 D#5;48.312 C5;48.375 D#5;48.562 C5;49.125 D#5;49.438 C5;49.938 D#5;50.000 C5;50.062 D#5;50.125 C5;50.188 D#5;51.750 D#6;51.812 B5;51.875 D#6;Sat Oct 31 12:55:05 PDT 2026
```

```
$ cat > "tools/showkit/songs/chords/panes.py" <<'EOF'
#!/usr/bin/env python3
"""The window: a fan of seven panes on the dome, two lancets on the jaw.  Writes the sprites.
A sprite here is a mask of real LEDs, so nothing lands in the blank middle of the face."""
import json, math, os, sys
sys.path.insert(0, os.getcwd())
import numpy as np, mau5engine as E
BASE = "deadmau5 - Some Chords"
h = E.Helmet()
s = np.asarray(h.shell, bool)
X, Y = h.px[s], h.py[s]
COLS, ROWS = 40, 24
Y_LO, Y_HI, X_HALF = -116.0, 172.0, 174.0
HUB = (0.0, 30.0)
NW = 7          # panes in the fan
LEAD = 6.5      # half width of a lead lin ... [cut]
{-1: 75, 0: 45, 1: 40, 2: 29, 3: 23, 4: 31, 5: 40, 6: 33, 10: 82}
shows/scenes/deadmau5 - Some Chords.sprites.json 9654 bytes 9 sprites
mixed cells 4 of 292
wrote shows/scenes/deadmau5 - Some Chords.scene.json scenes 33 hits 10
     211   395.84s  energy 0.83  bass 0.87 (punch 1.00)  mid 0.66  high 0.58
     212   397.72s  energy 0.72  bass 0.67 (punch 1.00)  mid 0.55  high 0.70
     213   399.59s  energy 0.72  bass 0.72 (punch 1.00)  mid 0.50  high 0.59
  ticks      bar 228
     227   425.84s  energy 0.83  bass 0.86 (punch 1.00)  mid 0.62  high 0.70
     228   427.72s  energy 0.44  bass 0.40 (punch 1.00)  mid 0.53  high 0.75
     229   429.59s  energy 0.33  bass 0.35 (punch 1.00)  mid 0.35  high 0.58
  end        bar 236
     235   440.84s  energy 0.29  bass 0.34 (punch 1.00)  mid 0.23  high 0.44
     236   442.72s  energy 0.00  bass 0.00 (punch 0.02)  mid 0.00  high 0.00
     237   444.59s  energy 0.00  bass 0.00 (punch 0.00)  mid 0.00  high 0.00
deadmau5 - Some Chords: 35 scenes, 10 hits, written into shows/deadmau5 - Some Chords.json
Sat Oct 31 12:56:19 PDT 2026
```

Whole-song draft compiles. Now a contact sheet through the guard.

```
$ cd "~/deadmau5 app"; KIT="tools/showkit"; W="$KIT/work/chords"; time python3 "$KIT/sheet.py" "deadmau5 - Some Chords" "$W/s1.png" 2:pedal 5:root 13:fifth 17:pane1 18:pane1E 18.5:gold 19.2:G 21:pane2 25:pane3 29:pane4 33:win 34:winE 34.5:gold 35:G# 41:win2 49:hold 51:hold 51.8:crash 52:DROP 52.1 52.25 56 59.4:gold 59.7:ruby 60 69:st1 70.13:hat 85:st2 85.13 101:st3 108 117:title 119:title 121:ped2 129:cand 133:cand 137:candb 144:dawn 149:beat2 161:hold2 164:WHITE 164.3 166:blaze 181:trade 182:trade 195.2:stop 195.5:stop 195.7:stop 196:home 205 213:strip 221:strip 226 230:tick 2>&1 | tail -70; dat ... [cut]
bar 2       pedal          shell max  29 mean   2.6   ears max   0 mean   0.0   pedal
bar 5       root           shell max  69 mean   6.1   ears max  32 mean   2.7   root
bar 13      fifth          shell max  78 mean   6.9   ears max  82 mean  16.3   fifth
bar 17      pane1          shell max  78 mean   8.3   ears max  87 mean  23.5   pane1
bar 18      pane1E         shell max  76 mean   6.3   ears max  48 mean  12.9   pane1
bar 18.5    gold           shell max  78 mean  11.5   ears max  87 mean  31.3   pane1
bar 19.2    G              shell max  75 mean   9.7   ears max  76 mean  27.1   pane1
bar 21      pane2          shell max  78 mean  12.7   ears max  87 mean  23.5   pane2
bar 25      pane3          shell max  78 mean  15.7   ears max  87 mean  23.5   pane3
bar 29      pane4          shell max  78 mean  18.8   ears max  87 mean  23.5   pane4
bar 33      win            shell max 107 mean  21.8   ears max 107 mean  29.7   window
bar 34      winE           shell max 107 mean  21.6   ears max 107 mean  18.8   window
bar 34.5    gold           shell max 107 mean  29.4   ears max 107 mean  39.6   window
bar 35      G#             shell max  86 mean  28.0   ears max 106 mean  40.1   window
bar 41      win2           shell max 115 mean  23.0   ears max 122 mean  33.5   windowb
bar 49      hold           shell max  51 mean  13.2   ears max  66 mean   6.4   hold
bar 51      hold           shell max  76 mean  32.5   ears max  98 mean   9.6   hold
bar 51.8    crash          shell max   0 mean   0.0   ears max 163 mean  20.5   hold · CRASH
bar 52      DROP           shell max 140 mean  25.7   ears max 255 mean  81.8   flood · FLOOD
bar 52.1                   shell max 231 mean  26.8   ears max 187 mean  67.6   flood · FLOOD
bar 52.25                  shell max 254 mean  55.1   
... [cut] ...
r 221     strip          shell max 115 mean  16.5   ears max 115 mean   7.3   strip220
bar 226                    shell max 115 mean  12.1   ears max 115 mean   7.3   strip224
bar 230     tick           shell max   0 mean   0.0   ears max 108 mean   7.0   ticks
tools/showkit/songs/chords/s1.png (1800, 2205)
python3 "$KIT/sheet.py" "deadmau5 - Some Chords" "$W/s1.png" 2:pedal 5:root    0.85s user 0.04s system 99% cpu 0.892 total
tail -70  0.00s user 0.00s system 0% cpu 0.892 total
Sat Oct 31 12:56:28 PDT 2026
```

```
$ cd "~/deadmau5 app"; grep -n "class Scene" -A70 mau5preview.py | sed -n 1,120p
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
.join(tmp, "f%05d.png" % n)); n += 1
112-    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
113-                    "-framerate", str(fps), "-i", os.path.join(tmp, "f%05d.png"),
114-                    "-vf", "format=yuv420p", "-c:v", "libx264", "-crf", "20",
115-                    path], check=True)
116-    for f in os.listdir(tmp):
117-        os.remove(os.path.join(tmp, f))
118-    os.rmdir(tmp)
119-    return path, n
120-
121-
122-def sheet(path, t=1.7, cols=5):
123-    h = E.Helmet()
124-    sc = Scene(h)
125-    names = sorted(E.REGISTRY)
126-    tw, th = 300, 245
```

```
$ cd "~/deadmau5 app"; grep -n "class Scene" -A70 mau5preview.py | sed -n 1,120p
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
.join(tmp, "f%05d.png" % n)); n += 1
112-    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
113-                    "-framerate", str(fps), "-i", os.path.join(tmp, "f%05d.png"),
114-                    "-vf", "format=yuv420p", "-c:v", "libx264", "-crf", "20",
115-                    path], check=True)
116-    for f in os.listdir(tmp):
117-        os.remove(os.path.join(tmp, f))
118-    os.rmdir(tmp)
119-    return path, n
120-
121-
122-def sheet(path, t=1.7, cols=5):
123-    h = E.Helmet()
124-    sc = Scene(h)
125-    names = sorted(E.REGISTRY)
126-    tw, th = 300, 245
```

```
$ cat > "tools/showkit/songs/chords/sheet2.py" <<'EOF'
#!/usr/bin/env python3
"""sheet2.py out.png cols bar[:label] ...  -- like the kit's sheet.py, but really through a guard (warmed for 4 s before each tile at the song's real level)."""
import json, os, sys
sys.path.insert(0, os.getcwd())
import numpy as np, mau5show, mau5preview as PV, mau5power
from PIL import Image, ImageDraw
base = "deadmau5 - Some Chords"
out = sys.argv[1]; cols = int(sys.argv[2])
marks = []
for a in sys.argv[3:]:
    b, _, lab = a.partition(":")
    marks.append((float(b), lab))
show = json.load(open(os.path.join("shows", base + ".js ... [cut]
deadmau5 - Some Chords: 11181 frames at 25 fps through the guard
  scene            from  mean mA   p95 mA     heat   allow W      ms
  dark             0.0s        0        0    25.2%      18.1    0.01
  pedal            0.2s       87      144     0.0%      18.1    0.02
  root             7.7s      158      264     0.0%      18.1    0.04
  third           15.2s      242      392     0.0%      18.1    0.05
  fifth           22.7s      332      512     0.1%      18.1    0.07
  pane1           30.2s      488      706     0.7%      18.1    0.19
  pane2           37.7s      575      786     1.6%      18.1    0.18
  pane3           45.2s      610      786     2.5%      18.1    0.18
  pane4           52.7s      565      721     3.3%      18.1    0.18
  window          60.2s      617      822     5.2%      18.1    0.18
  windowb         75.2s      634      883     7.3%      18.1    0.18
  hold            90.2s      596      951     8.2%      18.1    0.23
  flood           97.7s      451      815    10.0%      18.1    0.19
  stain1         127.7s      380      654    11.0%      18.1    0.24
  stain2         157.7s      393      649    12.2%      18.1    0.29
  stain3         187.7s      472      629    14.3%      18.1    0.30
  cut            217.7s      303      348    14.3%      18.1    0.20
  pedal2         225.2s      304      479    14.4%      18.1    0.10
  candle         240.2s      487      707    15.5%      18.1    0.18
  candleb        255.2s      590      921    17.3%      18.1    0.18
  wash           270.2s      668     1000    18.4%      18.1    0.18
  beat2          277.7s      604      851    21.2%      18.1    0.18
  hold2          300.2s      596      954    22.1%      18.1    0.24
  blaze          307.7s      418      827    22.8%      18.1    0.30
  clapback
... [cut] ...
9 mean   9.8  ears max 127 mean  14.0  sent  535 mA  flood
bar 69.03              shell max  32 mean   9.7  ears max 127 mean   8.1  sent  436 mA  stain1
bar 85.15              shell max  26 mean   7.7  ears max 121 mean   8.5  sent  380 mA  stain2
bar 101.1              shell max  25 mean   8.3  ears max  97 mean  16.3  sent  530 mA  stain3
bar 108.1              shell max  25 mean   8.3  ears max  97 mean  16.3  sent  530 mA  stain3
tools/showkit/songs/chords/g1.png (1800, 735)
Sat Oct 31 12:57:04 PDT 2026
```

```
$ cd "tools/showkit/songs/chords/" && sed -i '' 's/^base = "deadmau5 - Some Chords"/base = os.environ.get("BASEN", "deadmau5 - Some Chords")/' sheet2.py; cd "~/deadmau5 app"; W="tools/showkit/songs/chords"; BASEN="TIKI TIKI - Slowed" python3 "$W/sheet2.py" "$W/tiki.png" 6 40.03:big 40.3 41.13 47.03 39.03:hit 28 2>&1 | tail -8
bar 40.03   big        shell max  26 mean   9.7  ears max 145 mean  32.0  sent  838 mA  big
bar 40.3               shell max  13 mean   4.0  ears max 107 mean  33.7  sent  700 mA  big
bar 41.13              shell max  18 mean   6.9  ears max  55 mean  16.4  sent  497 mA  big
bar 47.03              shell max  24 mean   9.8  ears max 159 mean  32.3  sent  843 mA  bigb
bar 39.03   hit        shell max  10 mean   3.0  ears max 118 mean  53.9  sent 1000 mA  big · IDOL
bar 28                 shell max  40 mean   9.7  ears max  50 mean  11.2  sent  489 mA  still · TIKI TIKI
tools/showkit/songs/chords/tiki.png (1800, 245)
```

```
$ cat > "tools/showkit/songs/chords/patch1.py" <<'EOF'
import re
p="tools/showkit/songs/chords/gen.py"
s=open(p).read()
s=s.replace('GLASS = [[0, 10, 80], [0, 40, 255], [40, 110, 255],','GLASS = [[0, 14, 90], [0, 55, 255], [40, 125, 255],')
# clap: fires on the beat grid, gated to the two-bar clap
s=s.replace('''def clap(lo, hi, gain=0.6):
    return {"fx": "blades", "seq": ["012"], "step": 0.25, "rise": 0.9, "keep": 0.5, "c": K(lo, hi, cmain), "ctip": K(lo, hi, chi), "gain": gain,
            "gate": {"pat": CLAPS, "step" ... [cut]
wrote shows/scenes/deadmau5 - Some Chords.scene.json scenes 33 hits 25
deadmau5 - Some Chords: 35 scenes, 25 hits, written into shows/deadmau5 - Some Chords.json
bar 60.012             shell max  34 mean   9.7  ears max 127 mean  10.8  sent  480 mA  flood
bar 60.137             shell max  25 mean   7.8  ears max  61 mean   4.5  sent  317 mA  flood
bar 60.262             shell max  33 mean   9.7  ears max 229 mean  27.6  sent  761 mA  flood
bar 60.387             shell max  24 mean   7.8  ears max  81 mean  11.0  sent  430 mA  flood
bar 60.512             shell max  33 mean   9.7  ears max 127 mean  10.8  sent  480 mA  flood
bar 60.637             shell max  24 mean   7.8  ears max  61 mean   4.5  sent  317 mA  flood
bar 60.762             shell max  29 mean   8.7  ears max  84 mean   7.1  sent  391 mA  flood
bar 60.887             shell max  32 mean   9.7  ears max 127 mean  10.4  sent  475 mA  flood
bar 61.012             shell max  32 mean   9.8  ears max 127 mean  10.8  sent  480 mA  flood
bar 61.137             shell max  24 mean   7.9  ears max  61 mean   4.5  sent  317 mA  flood
bar 61.262             shell max  32 mean   9.8  ears max 127 mean  10.1  sent  470 mA  flood
bar 61.387             shell max  23 mean   7.9  ears max  61 mean   4.5  sent  317 mA  flood
bar 61.512             shell max  32 mean   9.8  ears max 229 mean  28.2  sent  771 mA  flood
bar 61.637             shell max  23 mean   7.8  ears max  81 mean  11.0  sent  430 mA  flood
bar 61.762             shell max  28 mean   8.8  ears max  84 mean   7.1  sent  391 mA  flood
bar 61.887             shell max  31 mean   9.7  ears max 127 mean  10.4  sent  475 mA  flood
tools/showkit/songs/chords/st_A.png (2400, 490)
Sat Oct 31 12:59:00 PDT 2026
```

```
$ cat > "tools/showkit/songs/chords/patch2.py" <<'EOF'
p="tools/showkit/songs/chords/gen.py"
s=open(p).read()
s=s.replace('def clo(ch): return round((3 * ch) / 11.0, 5)','def clo(ch): return round((3 * ch + 0.45) / 11.0, 5)')
# one blades layer for the arpeggio and the clap
s=s.replace('''def chirp(lo, hi, gain=0.6, tip=None):''','''def organ(lo, hi, gain=0.55):
    """The triad in order on the 8ths; on the clap all three tubes at once."""
    seq = [("012" if i in (2, 12) else ["0", "1", "2", "1"][i % 4]) for i in range(1 ... [cut]
wrote shows/scenes/deadmau5 - Some Chords.scene.json scenes 33 hits 25
deadmau5 - Some Chords: 35 scenes, 25 hits, written into shows/deadmau5 - Some Chords.json
bar 101.22             shell max  22 mean   6.8  ears max  89 mean  13.5  sent  437 mA  stain3
bar 101.25             shell max  31 mean   9.6  ears max 127 mean   8.6  sent  444 mA  stain3
tools/showkit/songs/chords/g2.png (2400, 980)
Sat Oct 31 12:59:46 PDT 2026
```

```
$ cat > "tools/showkit/songs/chords/patch3.py" <<'EOF'
p="tools/showkit/songs/chords/gen.py"
s=open(p).read()
# the jaw is the bass: it has to stand out from the dome on the kick
s=s.replace('S("%d" % a, a, b, [dome, bass(a, b, 0.5), lead()] + extra, pump=pump)','S("%d" % a, a, b, [dome, bass(a, b, 0.75, floor=0.12), lead()] + extra, pump=pump)')
s=s.replace('def flood(a, b, extra, gate_floor=0.5, g=0.3, pump=PUMP):','def flood(a, b, extra, gate_floor=0.5, g=0.24, pump=PUMP):')
s=s.replace('S(name, a, b, [glass(a, b, 0.3,  ... [cut]
wrote shows/scenes/deadmau5 - Some Chords.scene.json scenes 33 hits 25
deadmau5 - Some Chords: 35 scenes, 25 hits, written into shows/deadmau5 - Some Chords.json
bar 52.02   DROP       shell max  17 mean   5.1  ears max 197 mean  49.9  sent 1000 mA  flood · FLOOD
bar 52.1               shell max  19 mean   6.0  ears max 105 mean  36.2  sent  802 mA  flood · FLOOD
bar 52.25              shell max  20 mean   9.7  ears max 158 mean  30.6  sent  820 mA  flood · FLOOD
bar 85.03              shell max  33 mean   9.8  ears max 155 mean  17.6  sent  594 mA  stain2
bar 85.156             shell max  25 mean   6.9  ears max  81 mean  16.2  sent  487 mA  stain2
bar 85.22              shell max  28 mean   6.8  ears max  34 mean  12.8  sent  428 mA  stain2
bar 85.28              shell max  33 mean   9.8  ears max 155 mean  18.1  sent  603 mA  stain2
bar 85.41              shell max  25 mean   6.8  ears max  81 mean  17.4  sent  508 mA  stain2
bar 59.4    turn       shell max  12 mean   3.3  ears max 145 mean  36.3  sent  719 mA  flood · TURN
bar 59.7               shell max  18 mean   5.1  ears max 159 mean  41.8  sent  861 mA  flood · TURN
bar 60.02              shell max  34 mean   9.8  ears max 155 mean  19.4  sent  623 mA  flood
bar 121.1              shell max  59 mean   6.0  ears max  37 mean   8.8  sent  335 mA  pedal2 · SOME CHORDS
bar 123                shell max  30 mean   4.3  ears max  55 mean  18.6  sent  445 mA  pedal2
bar 125                shell max  39 mean   3.6  ears max  68 mean  16.5  sent  390 mA  pedal2
bar 129     B          shell max  45 mean   5.2  ears max  86 mean  25.7  sent  594 mA  candle
bar 129.5   A#         shell max  42 mean   4.6  ears max  49 mean  13.9  sent  382 mA  candle
bar 130     G#         shell max  43 mean   4.6  ears max  47 mean  13.7
... [cut] ...
ean   9.9  ears max 153 mean  20.5  sent  642 mA  strip220
bar 225.03             shell max  60 mean   8.3  ears max 153 mean  20.5  sent  594 mA  strip224
bar 229.03             shell max  32 mean   1.8  ears max 116 mean  10.8  sent  240 mA  ticks
bar 232.03             shell max  20 mean   1.4  ears max  82 mean   7.5  sent  176 mA  ticks
bar 235.5              shell max   4 mean   1.1  ears max  43 mean   2.9  sent   87 mA  ticks
tools/showkit/songs/chords/g3.png (2400, 1960)
Sat Oct 31 13:00:40 PDT 2026
```

```
$ cd "~/deadmau5 app"; sed -n 360,458p mau5power.py
        governed = floored = False
        scale = 1.0
        if over or cap < 1.0:
            per = self._per_led_ma(out)
            omx = out.max(1)
            lit = (amx > 0) & (omx > 1e-6)
            fs = np.zeros(m, np.float32)
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
            scale = min(lo_s, cap)
            if scale < 1.0:
                base = scale ** shed
                out *= np.maximum(base, fs)[:, None]
                governed = after_region > 0
                floored = bool((fs > base).any())
        self._gov_s = scale
        if math.isfinite(now):
            self._gov_t = now

        g = min(max(float(gain), 0.0), 1.0)
        if g < 1.0:
            out *= g
        final = self.frame_ma(out)
        if self.thermal is not None:
            self.thermal.update(final * 12.0 / 1000.0, now=now)
        return np.clip(out, 0, 255).astype(np.uint8), {
            "asked_ma": round(asked, 1),
            "after_ceiling_ma": round(after_ceiling, 1),
            "after_region_ma": round(after_region, 1),
            "sent_ma": round(final, 1),
            "standby_ma": round(self.standby_ma(), 1),
            "total_ma": round(final + self.standby_ma(), 1),
            "amps": round((final
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
$ cat > "tools/showkit/songs/chords/check2.py" <<'EOF'
#!/usr/bin/env python3
"""Per scene: how much of the time the governor takes light from the shell, and how bright the shell really is."""
import json, os, sys, time
sys.path.insert(0, os.getcwd())
import numpy as np, mau5show, mau5power, mau5scene as S, mau5engine as E
base = "deadmau5 - Some Chords"
show = json.load(open(os.path.join("shows", base + ".json")))
music = mau5show._music_for(show, os.path.join("shows", base + ".mp3"))
h = E.Helmet(); sc = S.Scenes(show["scenes"], h); guard = mau5power.load(count=h.n)
fps = 25.0; dur = float(show["duration"] ... [cut]
label                         from      n     mA     p95   gov%  shell   smax   ears
dark                           0.0    119      0       0      0    0.0      0    0.0   heat 39.0
pedal                          0.2    187     88     144      0    2.9     25    0.0   heat 0.0
root                           7.7    188    167     278      0    3.8     33    3.1   heat 0.0
third                         15.2    187    262     421      0    3.9     35    8.3   heat 0.1
fifth                         22.7    188    363     554      0    4.1     36   14.0   heat 0.2
pane1                         30.2    187    528     760      0    5.8     44   20.4   heat 0.9
pane2                         37.7    188    618     837      0    8.8     41   20.5   heat 1.9
pane3                         45.2    187    647     831      0    9.8     33   20.4   heat 3.0
pane4                         52.7    188    598     837      0    9.0     24   18.9   heat 3.9
window                        60.2    375    657     925      2    9.0     26   22.5   heat 6.0
windowb                       75.2    375    675    1009      6    8.5     25   24.4   heat 8.3
hold                          90.2    176    621     956      2    9.8     24   19.0   heat 9.2
hold · CRASH                  97.3     11    209     347      0    0.0      0   12.5   heat 9.2
flood · FLOOD                 97.7     24    710    1402     58    5.8     18   31.2   heat 9.4
flood                         98.7    668    505     935      6    7.9     29   15.5   heat 11.8
flood · TURN                 111.6     58    773    1773     83    4.7     18   37.1   heat 12.1
stain1 · STAIN 1             127.7     24    508    1099     12    7.5     25   16.3   heat 12.1
stain1                       128.7    668    504     938      6    7.9     30  
... [cut] ...
                   405.2    158    446     798      2    7.4     31   12.9   heat 39.2
strip216 · TURN              411.6     29    758    1685     72    4.9     21   35.9   heat 39.4
strip220                     412.7    188    429     819      2    6.7     36   13.2   heat 39.8
strip224                     420.2    158    378     746      1    5.2     38   12.9   heat 40.0
strip224 · TURN              426.6     29    716    1659     48    3.4     25   36.3   heat 40.2
ticks                        427.7    375     95     211      0    1.5     20    2.6   heat 40.2
Sat Oct 31 13:01:14 PDT 2026
```

```
$ cat > "tools/showkit/songs/chords/patch4.py" <<'EOF'
p="tools/showkit/songs/chords/gen.py"
s=open(p).read()
def rep(a,b,count=1):
    global s
    assert a in s, a
    s=s.replace(a,b) if count==0 else s.replace(a,b,count)
# pipes: lower floors, so the attack shows and the intro costs less
rep('def pipe(t, lo, hi, gain, floor=0.4):','def pipe(t, lo, hi, gain, floor=0.28):')
rep('def pipes(lo, hi, gain, n=3, floor=0.4):','def pipes(lo, hi, gain, n=3, floor=0.28):')
rep('def tubes_all(lo, hi, gain, floor=0.35):','def tubes ... [cut]
wrote shows/scenes/deadmau5 - Some Chords.scene.json scenes 33 hits 25
deadmau5 - Some Chords: 35 scenes, 25 hits, written into shows/deadmau5 - Some Chords.json
label                         from      n     mA     p95   gov%  shell   smax   ears
dark                           0.0    119      0       0      0    0.0      0    0.0   heat 33.1
pedal                          0.2    187     88     144      0    2.9     25    0.0   heat 0.0
root                           7.7    188    156     273      0    3.8     33    2.4   heat 0.0
third                         15.2    187    234     399      0    3.9     35    6.6   heat 0.0
fifth                         22.7    188    317     521      0    4.1     36   11.2   heat 0.1
pane1                         30.2    187    473     720      0    5.8     44   17.2   heat 0.7
pane2                         37.7    188    563     797      0    8.8     41   17.3   heat 1.5
pane3                         45.2    187    592     796      0    9.8     33   17.2   heat 2.3
pane4                         52.7    188    548     797      0    9.0     24   15.9   heat 3.1
window                        60.2    375    563     879      0    8.4     25   17.7   heat 4.7
windowb                       75.2    375    581     933      2    8.3     24   19.1   heat 6.4
hold                          90.2    176    621     956      2    9.8     24   19.0   heat 7.3
hold · CRASH                  97.3     11    209     347      0    0.0      0   12.5   heat 7.3
flood · FLOOD                 97.7     24    571    1111     12    7.5     22   19.8   heat 7.4
flood                         98.7    668    505     935      6    7.9     29   15.5   heat 9.8
flood · TURN                 111.6     58    671    1266     17    7.4     28   26.0   heat 10.0
stain1 · STAIN 
... [cut] ...
                   405.2    158    446     798      2    7.4     31   12.9   heat 33.4
strip216 · TURN              411.6     29    646    1202     17    6.8     29   25.7   heat 33.6
strip220                     412.7    188    429     819      2    6.7     36   13.2   heat 34.0
strip224                     420.2    158    378     746      1    5.2     38   12.9   heat 34.2
strip224 · TURN              426.6     29    576    1176     17    4.6     34   25.8   heat 34.3
ticks                        427.7    375     95     211      0    1.5     20    2.6   heat 34.3
Sat Oct 31 13:02:33 PDT 2026
```

```
$ cd "~/deadmau5 app"; W="tools/showkit/songs/chords"; python3 "$W/sheet2.py" "$W/g4.png" 8 0.3:G#m 2.5:F# 3.2:G# 6:E 9.5:E 13.5:E 16.3:G#m 17:E 18.5:F# 19.2:G# 20.3:G#m 24.3:G#m 28.3:G#m 32.05:G#m 33:E 34.45:F# 35:G# 48.5:hold 50:hold 51.5:hold 51.76:crash 52.015:DROP 52.05 52.13 52.27 53.01 54.3 55.8 59.39:F# 59.65:E 60.01:G#m 68.01:st1 68.13 69.14 76.01 84.01:st2 84.15 84.4 91.4:F# 91.7:E 92.01 100.01:st3 100.1 107.4:F# 107.7:E 108.01 115.4:F# 115.7:E 116.1:cut | tail -3; date
bar 115.7   E          shell max  40 mean   9.9  ears max 155 mean  29.6  sent  798 mA  stain3 · TURN
bar 116.1   cut        shell max  46 mean   3.3  ears max  62 mean   3.8  sent  164 mA  cut · SOME CHORDS
tools/showkit/songs/chords/g4.png (2400, 1715)
Sat Oct 31 13:02:52 PDT 2026
```

```
$ cat > "tools/showkit/songs/chords/patch5.py" <<'EOF'
p="tools/showkit/songs/chords/gen.py"
s=open(p).read()
def rep(a,b,count=1):
    global s
    assert a in s, a
    s=s.replace(a,b) if count==0 else s.replace(a,b,count)
rep('"gain": TURN(lo, hi, gain, 0.2)}','"gain": TURN(lo, hi, gain, 0.0)}')
rep('def blow(c, gain=0.36, pal="glass"):','def blow(c, gain=0.27, pal="glass"):')
rep('def beam(lo, hi, gain=0.3, speed=0.125):','def beam(lo, hi, gain=0.42, speed=0.125):')
open(p,"w").write(s)
EOF
cd "~/deadmau5 ap ... [cut]
wrote shows/scenes/deadmau5 - Some Chords.scene.json scenes 33 hits 25
deadmau5 - Some Chords: 35 scenes, 25 hits, written into shows/deadmau5 - Some Chords.json
bar 234                shell max  11 mean   1.3  ears max  60 mean   4.0  sent  113 mA  ticks
tools/showkit/songs/chords/g5.png (2400, 2205)
Sat Oct 31 13:03:25 PDT 2026
```

```
$ cd "~/deadmau5 app"; grep -n "keys\|kind\|ramp" remote/offline/show.js | head -20; grep -n "'orb'\|\"orb\"\|twinkle\|over\b" remote/offline/show.js | head -20; grep -n "split('+')\|split(\"+\")" remote/offline/*.js | head; grep -n "rate" remote/offline/engine.js | head -10; grep -n "class SpriteShow\|sprite" remote/offline/engine.js | head -10; date
298:  if (v && v.ramp) return { k: 1, a: v.ramp[0], b: v.ramp[1] };
299:  if (v && v.keys) {
300:    return { k: 2, bars: Float64Array.from(v.keys, e => e[0]),
301:             vals: Float64Array.from(v.keys, e => e[1]) };
394:    for (const k of Object.keys(spec.pal)) {
37:// same current over a song, only placed where it can be seen.
182:    if (mix === 'over') {
241:      // Handed over as `gain`, at most 1, for the sender to apply after
277:const MIXES = { add: 0, max: 1, over: 2 };
289:  twinkle: ['rate', 'sharp', 'spread', 'dens'],
461:    } else if (L.fx === 'twinkle') {
643:      case 'orb': {
666:      case 'twinkle': {
remote/offline/show.js:346:  for (const raw of String(on).split('+')) {
84:// positions here, deliberately -- see the note at the top.
457:// mau5engine.SpriteShow says what dx, dy, vx, vy, wx, wy, wf and rate do.
461:                wx: 0.0, wy: 0.0, wf: 0.0, rate: 0.0 },
464:    const at = this.p.rate > 0 ? pmod(Math.floor(t * this.p.rate), names.length) : 0;
595:def('confetti', { rate: 14.0, fade: 0.55, sat: 0.9 },
598:    const step = 1.0 / Math.max(this.p.rate, 0.1);
688:def('sparkle', { bed: [40, 0, 60], glitter: [255, 255, 255], density: 0.10, rate: 7.0 },
692:    const k = Math.trunc(t * this.p.rate);
168:function spriteBitmap(fonts, name) {
169:  const rows = fonts.sprites[name];
458:def('sprite', { sprite: 'smile', color: [0, 255, 255], bg: [0, 0, 0],
463:    const names = String(this.p.sprite).split('|');
465:    const bm = spriteBitmap(this.fonts, names[at]);
968:              textBitmap, glyphBitmap, digitBitmap, spriteBitmap, fract, pmod,
Sat Oct 31 13:04:05 PDT 2026
```

```
$ cd "~/deadmau5 app"; W="tools/showkit/songs/chords"; python3 "$W/steps.py" 143.5 144.25 | awk 'NR==1||NR>1' | cut -c1-110; python3 "$W/steps.py" 163.5 164.1 | cut -c1-110; python3 "$W/steps.py" 27 28.1 | cut -c1-110 | head -6; date
    bar   | level:    sub   bass lowmid    mid   pres    air  | onset:    sub   bass lowmid    mid   pres    a
 143.500  |   1.27   1.16   1.69   1.87   1.71   1.05 |   0.08   0.05   0.08   0.09   0.12   0.08
 143.562  |   1.25   1.04   1.75   1.93   1.74   1.13 |   0.08   0.07   0.05   0.05   0.08   0.08
 143.625  |   1.27   1.16   1.55   1.79   1.75   1.24 |   0.11   0.09   0.05   0.14   0.16   0.08
 143.688  |   0.93   0.97   1.51   2.05   1.95   1.48 |   0.06   0.03   0.08   0.07   0.09   0.08
 143.750  |   0.95   0.94   1.50   1.97   1.89   1.50 |   0.12   0.09   0.10   0.08   0.02   0.05
 143.812  |   0.95   0.82   1.69   1.84   1.69   1.66 |   0.09   0.04   0.06   0.10   0.10   0.08
 143.875  |   0.47   0.77   1.62   1.81   1.70   1.87 |   0.11   0.12   0.08   0.06   0.07   0.08
 143.938  |   0.72   0.94   1.49   1.69   1.86   2.09 |   0.51   0.05   0.44   0.31   0.09   0.09
 144.000  |   1.33   0.70   1.80   1.78   1.97   1.66 |   0.20   0.10   0.44   0.31   0.09   0.02
 144.062  |   1.20   0.70   1.79   1.82   1.95   1.55 |   0.05   0.17   0.16   0.07   0.11   0.02
 144.125  |   1.17   0.62   1.74   1.91   1.90   1.46 |   0.13   0.09   0.15   0.07   0.05   0.06
 144.188  |   1.24   0.79   1.54   1.89   1.91   1.55 |   0.10   0.20   0.17   0.10   0.12   0.15
    bar   | level:    sub   bass lowmid    mid   pres    air  | onset:    sub   bass lowmid    mid   pres    a
 163.500  |   1.17   0.99   1.35   1.52   1.94   1.47 |   0.09   0.02   0.09   0.23   0.15   0.11
 163.562  |   1.23   0.99   1.36   1.48   1.97   1.59 |   0.09   0.06   0.09   0.11   0.10   0.05
 163.625  |   1.20   1.03   1.33   1.47   1.98   1.75 |   0.08   0.05   0.09   0.10   0.10   0.08
 163.688  |   0.81   0.73   1.11   1.40   2.06   2.01 |   0.21   0.74   1.26   1.13   0.55   0.44
 163.750  
... [cut] ...
ass lowmid    mid   pres    air  | onset:    sub   bass lowmid    mid   pres    a
  27.000  |   1.35   0.94   1.68   1.70   1.74   1.19 |   0.10   0.23   0.13   0.07   0.09   0.31
  27.062  |   1.27   0.77   1.68   1.66   1.79   0.99 |   0.08   0.14   0.05   0.12   0.09   0.13
  27.125  |   1.21   1.01   1.39   1.73   1.84   1.12 |   0.08   0.14   0.06   0.12   0.09   0.13
  27.188  |   1.33   0.95   1.39   1.87   1.81   1.07 |   0.11   0.18   0.09   0.07   0.09   0.25
  27.250  |   1.34   1.15   1.58   1.76   1.77   1.39 |   0.12   0.38   0.06   0.07   0.12   0.25
Sat Oct 31 13:04:42 PDT 2026
```

```
$ cat > "tools/showkit/songs/chords/patch6.py" <<'EOF'
p="tools/showkit/songs/chords/gen.py"
s=open(p).read()
def rep(a,b,count=1):
    global s
    assert a in s, a
    s=s.replace(a,b) if count==0 else s.replace(a,b,count)
# --- the opening: the pipes have to be seen
rep('''S("root", 4, 8, [pedal(4, 8, 0.3), pipe(0, 4, 8, [0.12, 0.3])])
S("third", 8, 12, [pedal(8, 12, 0.32), pipe(0, 8, 12, 0.3), pipe(1, 8, 12, [0.12, 0.3])])
S("fifth", 12, 16, [pedal(12, 16, 0.34), pipe(0, 12, 16, 0.32), pipe(1, 12, 16, 0.32), pipe(2, 12 ... [cut]
shows/scenes/deadmau5 - Some Chords.sprites.json 10726 bytes 10 sprites
mixed cells 4 of 292
wrote shows/scenes/deadmau5 - Some Chords.scene.json scenes 33 hits 30
     236   442.72s  energy 0.00  bass 0.00 (punch 0.02)  mid 0.00  high 0.00
     237   444.59s  energy 0.00  bass 0.00 (punch 0.00)  mid 0.00  high 0.00
deadmau5 - Some Chords: 35 scenes, 30 hits, written into shows/deadmau5 - Some Chords.json
label                         from      n     mA     p95   gov%  shell   smax   ears
dark                           0.0    119      0       0      0    0.0      0    0.0   heat 33.8
pane1 · PANE                  30.2     35    554     725      0    6.7     59   20.4   heat 0.8
pane2 · PANE                  37.7     36    646     808      0    9.7     48   20.6   heat 1.5
pane3 · PANE                  45.2     35    646     799      0    9.8     36   20.4   heat 2.4
pane3                         46.6    152    628     884      0    9.8     33   19.3   heat 3.2
pane4 · PANE                  52.7     36    601     808      0    9.0     27   19.1   heat 3.4
hold · CRASH                  97.3     11    208     347      9    0.0      0   12.4   heat 8.1
flood · FLOOD                 97.7     24    532     958      4    7.7     23   17.0   heat 8.2
flood · TURN                 111.6     58    671    1266     17    7.4     30   26.0   heat 10.8
stain1 · STAIN 1             127.7     24    508    1099     12    7.5     25   16.3   heat 10.9
stain1 · TURN                141.6     58    668    1265     17    7.4     25   26.0   heat 13.5
stain2 · STAIN 2             157.7     24    464     761      0    7.8     23   13.1   heat 13.5
stain2 · TURN                171.6     58    711    1101     17    7.5     26   28.3   heat 16.1
stain3 · STAIN 3             187.7     24    458    
... [cut] ...
                   405.2    158    446     798      2    7.4     31   12.9   heat 34.1
strip216 · TURN              411.6     29    646    1202     17    6.8     29   25.7   heat 34.2
strip220                     412.7    188    429     819      2    6.7     36   13.2   heat 34.6
strip224                     420.2    158    378     746      1    5.2     38   12.9   heat 34.8
strip224 · TURN              426.6     29    576    1176     17    4.6     34   25.8   heat 35.0
ticks                        427.7    375     95     211      0    1.5     20    2.6   heat 35.0
Sat Oct 31 13:05:19 PDT 2026
```

```
$ cd "~/deadmau5 app"; W="tools/showkit/songs/chords"; python3 "$W/sheet2.py" "$W/g6.png" 8 5:root 6.5:gold 9:third 13:fifth 14.5:gold 16.02:PANE1 16.3 17 20.02:PANE2 24.02:PANE3 28.02:PANE4 36.88:E 37 37.13 37.25 38.38:F# 38.5 38.88:G 39.1 40.02:G#m 40.2 48.02:hold 48.5 49 49.5 50 50.5 51 51.3 51.6 51.74 51.76:crash 51.9 52.01:drop 52.03 52.06 52.1 | tail -3; date
bar 52.06              shell max  29 mean   8.9  ears max 132 mean  37.8  sent  908 mA  flood · FLOOD
bar 52.1               shell max  24 mean   7.7  ears max  73 mean  25.2  sent  670 mA  flood · FLOOD
tools/showkit/songs/chords/g6.png (2400, 1225)
Sat Oct 31 13:05:27 PDT 2026
```

```
$ cat > "tools/showkit/songs/chords/patch7.py" <<'EOF'
p="tools/showkit/songs/chords/gen.py"
s=open(p).read()
def rep(a,b,count=1):
    global s
    assert a in s, a
    s=s.replace(a,b) if count==0 else s.replace(a,b,count)
rep('return {"fx": "orb", "on": "face", "x": xs, "y": ys, "rad": rad, "soft": 40, "c": K(lo, hi, cmain), "cgrad": 0.0, "gain": gain}',
    'return {"fx": "orb", "on": "face", "x": xs, "y": ys, "rad": rad, "soft": 40, "c": K(lo, hi, chi), "cgrad": -0.0909, "gain": gain}')
rep('def hats(gain=0.35):','def ... [cut]
wrote shows/scenes/deadmau5 - Some Chords.scene.json scenes 33 hits 32
deadmau5 - Some Chords: 35 scenes, 32 hits, written into shows/deadmau5 - Some Chords.json
bar 165.2              shell max  24 mean   6.8  ears max  44 mean  16.2  sent  484 mA  blaze
tools/showkit/songs/chords/g7.png (1800, 980)
-rw-r--r--@ 1 jones  staff  10260 Oct 31 12:39 shows/scenes/deadmau5 - Some Chords.beats
-rw-r--r--@ 1 jones  staff  58926 Oct 31 13:06 shows/scenes/deadmau5 - Some Chords.scene.json
-rw-r--r--@ 1 jones  staff  10726 Oct 31 13:05 shows/scenes/deadmau5 - Some Chords.sprites.json
Sat Oct 31 13:06:30 PDT 2026
```

I'll read the correction and the new tools, then measure the show against them.

```
$ KIT="tools/showkit"; date; tail -40 "$KIT/BRIEF.md"; echo ------; cat "$KIT/sheet.py"; echo ------; cat "$KIT/power.py"; echo ------; cat "$KIT/scenepower.py"; ls -la "$KIT"
Sat Oct 31 13:07:39 PDT 2026
- Only write these files for your song: `shows/scenes/<base>.beats`, `shows/scenes/<base>.scene.json`, `shows/scenes/<base>.sprites.json`, and what the tools make: `shows/<base>.json`, `shows/<base>.analysis.npz`. Nine other authors are working beside you on other songs. Never edit any code, any test, or another song's file. If you truly need an engine feature, finish without it and say so in your report.
- NEVER contact the helmet (192.168.10.172, 4.3.2.1, or anything scanning the network). Do not run `mau5show.py play`, `mau5offline.py`, `mau5ctl`, `test_mau5.py`, or anything that starts a browser. Do not commit. Do not delete MP3s.
- Text on the helmet: the song's title words only. Never spell out any other lyric.
- No power limit gets changed, ever. If a scene is too hot, make the scene lighter.
- Time: check `date`. Stop polishing and return by the deadline in your task. A complete, correct show beats a perfect half of one, so get a whole-song draft compiling early, then improve it.

## The steps
1. `python3 $KIT/grid.py scan "shows/<base>.mp3"` then `fold` over the song. Measure the grid: tempo flat across the song within about 10 ms per 8 bars; a seam or tempo change shows as a step. Decide the bar line from the music, not from the estimator: phrases turn on it and the drop's first kick is step 0 of a bar. The estimator puts bars half a bar off regularly, and a bar line wrong by a beat or two ruins every drop. Use `grid.py scan`'s phrase positions, `fold`, and the spectrogram to be sure. Then `grid.py write "<base>" --spb S --anchor T` (it builds the show), and `grid.py check "<base>"`: worst under 15 ms where the music is clear. A song that truly changes tempo needs holds or, if it speeds up, tell me; do not ship a wrong grid.
2. Und
... [cut] ...
RIEF.md
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
```

```
$ KIT="tools/showkit"; date; tail -40 "$KIT/BRIEF.md"; echo ------; cat "$KIT/sheet.py"; echo ------; cat "$KIT/power.py"; echo ------; cat "$KIT/scenepower.py"; ls -la "$KIT"
Sat Oct 31 13:07:39 PDT 2026
- Only write these files for your song: `shows/scenes/<base>.beats`, `shows/scenes/<base>.scene.json`, `shows/scenes/<base>.sprites.json`, and what the tools make: `shows/<base>.json`, `shows/<base>.analysis.npz`. Nine other authors are working beside you on other songs. Never edit any code, any test, or another song's file. If you truly need an engine feature, finish without it and say so in your report.
- NEVER contact the helmet (192.168.10.172, 4.3.2.1, or anything scanning the network). Do not run `mau5show.py play`, `mau5offline.py`, `mau5ctl`, `test_mau5.py`, or anything that starts a browser. Do not commit. Do not delete MP3s.
- Text on the helmet: the song's title words only. Never spell out any other lyric.
- No power limit gets changed, ever. If a scene is too hot, make the scene lighter.
- Time: check `date`. Stop polishing and return by the deadline in your task. A complete, correct show beats a perfect half of one, so get a whole-song draft compiling early, then improve it.

## The steps
1. `python3 $KIT/grid.py scan "shows/<base>.mp3"` then `fold` over the song. Measure the grid: tempo flat across the song within about 10 ms per 8 bars; a seam or tempo change shows as a step. Decide the bar line from the music, not from the estimator: phrases turn on it and the drop's first kick is step 0 of a bar. The estimator puts bars half a bar off regularly, and a bar line wrong by a beat or two ruins every drop. Use `grid.py scan`'s phrase positions, `fold`, and the spectrogram to be sure. Then `grid.py write "<base>" --spb S --anchor T` (it builds the show), and `grid.py check "<base>"`: worst under 15 ms where the music is clear. A song that truly changes tempo needs holds or, if it speeds up, tell me; do not ship a wrong grid.
2. Und
... [cut] ...
RIEF.md
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
```

My own `sheet2.py` already ran through the real guard, so those earlier verdicts hold. The new whole-song mean target is what could change things, so I'll measure that now.

```
$ cd "~/deadmau5 app"; KIT="tools/showkit"; python3 "$KIT/power.py" "deadmau5 - Some Chords"; python3 "$KIT/scenepower.py" "deadmau5 - Some Chords"; python3 "$KIT/power.py" "TIKI TIKI - Slowed"; date
deadmau5 - Some Chords: 447 s, mean 13.2 W (target 11.5 or less), heat at the end 34%
hottest scenes (name, mean W, seconds): flood 13.7 30s; stain1 13.7 30s; home 13.7 30s; stain2 13.6 30s; stain3 13.5 30s; beat2 14.0 22s; windowb 14.6 15s; window 14.4 15s
scene            mean    p95   gov%   reg%  shellm   earsm   smax   heat
dark                0      0      0      0     0.0     0.0      0  34.2%
pedal              88    144      0      0     2.9     0.0     33   0.0%
root              204    344      0      0     3.8     5.3     42   0.0%
third             340    536      0      0     3.9    13.0     43   0.2%
fifth             455    695      0      0     4.1    19.5     45   0.6%
pane1             520    793      0      0     6.0    19.5     60   1.3%
pane2             608    869      0     56     8.9    19.6     47   2.2%
pane3             632    866      0    100     9.8    19.5     39   3.2%
pane4             584    805      0    100     9.0    18.1     30   4.1%
window            578    863      2    100     8.4    18.7     35   5.8%
windowb           597    912      3    100     8.3    20.1     35   7.6%
hold              529    824      5     58     8.6    15.6     45   8.3%
flood             519    836      7     99     7.8    16.4     34  11.0%
stain1            517    836      7     92     7.8    16.3     35  13.6%
stain2            513    851      1     98     8.0    15.7     34  16.3%
stain3            501    708      0     98     8.0    15.1     33  18.7%
cut               311    349      0     73     9.2     1.9     61  18.8%
pedal2            289    478      0      7     4.2     9.4     52  18.8%
candle            484    729      0      0     6.2    17.2     49  19.9%
candleb           563    916      3     69     9.2    16.3     54  21.5%
wash     
... [cut] ...
    7.8    13.2     34  34.2%
strip216          477    833      4     57     7.3    14.9     42  34.7%
strip220          429    750      2     34     6.7    13.2     53  35.1%
strip224          408    763      3      0     5.1    14.9     60  35.4%
ticks              95    211      0      0     1.5     2.6     32  35.4%
TIKI TIKI - Slowed: 320 s, mean 12.7 W (target 11.5 or less), heat at the end 19%
hottest scenes (name, mean W, seconds): bigb 14.3 17s; sunset 14.6 14s; final2 14.6 14s; big 14.5 14s; final 14.4 14s; hook2 15.2 10s; hook4 15.2 10s; sunsetb 14.4 10s
Sat Oct 31 13:08:27 PDT 2026
```

```
$ cat > "tools/showkit/songs/chords/patch8.py" <<'EOF'
p="tools/showkit/songs/chords/gen.py"
s=open(p).read()
def rep(a,b,count=1):
    global s
    assert a in s, a
    s=s.replace(a,b) if count==0 else s.replace(a,b,count)
# white, once: the window itself is out for the first half beat
rep('H("WHITE", "blaze", 2, [blow(0.5, 0.16, pal="white"), ring(0.5, 1.0, pal="white"), {"fx": "fill", "on": "rims", "pal": "white", "c": 0, "gain": [0.25, 0]}])',
    'H("WHITE", "blaze", 2, [blow(0.5, 0.15, pal="white"), dict(ring(0.5, 1 ... [cut]
wrote shows/scenes/deadmau5 - Some Chords.scene.json scenes 33 hits 32
deadmau5 - Some Chords: 35 scenes, 32 hits, written into shows/deadmau5 - Some Chords.json
bar 164.01  W          shell max  25 mean   9.3  ears max 157 mean  19.9  sent  634 mA  blaze · WHITE
bar 164.03             shell max  25 mean   9.5  ears max 157 mean  37.3  sent  925 mA  blaze · WHITE
bar 164.06             shell max  23 mean   8.7  ears max 138 mean  37.1  sent  906 mA  blaze · WHITE
bar 164.1              shell max  20 mean   7.8  ears max  88 mean  26.5  sent  688 mA  blaze · WHITE
bar 164.14             shell max  14 mean   7.0  ears max  95 mean  25.3  sent  648 mA  blaze · WHITE
bar 164.2              shell max  12 mean   6.6  ears max  56 mean  27.8  sent  679 mA  blaze · WHITE
bar 164.3              shell max  16 mean   9.1  ears max 145 mean  27.1  sent  742 mA  blaze · WHITE
bar 164.5              shell max  33 mean   9.8  ears max 155 mean  10.8  sent  481 mA  blaze
bar 165.01             shell max  33 mean   9.7  ears max 155 mean  13.3  sent  522 mA  blaze
bar 165.2              shell max  24 mean   6.8  ears max  44 mean  16.2  sent  484 mA  blaze
bar 165.45             shell max  24 mean   6.8  ears max  44 mean  16.2  sent  484 mA  blaze
bar 166.2              shell max  24 mean   6.7  ears max  44 mean  16.2  sent  484 mA  blaze
tools/showkit/songs/chords/g8.png (1800, 490)
shows/scenes/deadmau5 - Some Chords.sprites.json
Sat Oct 31 13:08:35 PDT 2026
```
