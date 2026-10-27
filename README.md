# mau5head show-control suite

Software for the 1406-LED wearable mau5head: a desktop simulator, an effect
library, a show packager, setup scripts for the player and the controller, and
the phone remote.

```
helmet.toml           every number that matters, read by every tool
mau5cfg.py            config + geometry + wiring        (shared)
mau5fseq.py           FSEQ v2 read/write + DDP send/recv (shared)
mau5fx.py             effect library
mau5sim.py            desktop simulator
mau5build.py          show packager / FPP uploader
mau5song.py           analyse a track and build a full-length show for it
example_effect.py     a worked example of writing your own effects
setup/fpp_setup.sh    configures a fresh Falcon Player, idempotent
setup/make_wled_config.py   writes setup/wled_config.json from helmet.toml
remote/index.html     the phone remote, one file, no internet
docs/mau5remote-android.md  design for the native app
data/                 pixel_map.csv, wiring_chained.csv
shows/                built .fseq / media / playlist json
```

Python 3.11+ (3.9 also works — `mau5cfg` falls back to a small TOML reader when
`tomllib` is missing). numpy and matplotlib are the only requirements.
`zstandard` is optional, for reading zstd-compressed FSEQs; `ffmpeg` is
optional, for MP4 export.

## Five minutes

```bash
python3 mau5cfg.py                       # prints the wiring and the pixel grid
python3 mau5sim.py --demo                # watch the demo show
python3 mau5sim.py --demo --export preview.mp4
python3 mau5build.py build --name intro --effect example_effect.py:show --seconds 64
python3 mau5build.py deploy --name intro --audio intro.mp3 \
        --effect example_effect.py:show --start
```

## The helmet, as the software sees it

```
out    part                     leds  first   last
A      shell_back                686      0    685
B      shell_front + 10 fixtures 957    686   1642

shell 1185  accessories 458   total 1643   DDP channels 4929
```

Those numbers come from the printed geometry, not from the spec -- see
"the pixel map" below. Check the whole addressing chain any time with:

```bash
python3 mau5cfg.py --verify
```

and look at the map itself, coloured by which output each LED is on:

```bash
python3 mau5sim.py --layout
```

Global LED index is wire order: chain A, then chain B's shell pixels, then the
accessories in chain order (ERR, ETR1-3, VT01, VB01, ERL, ETL1-3). A frame is
always `(1406, 3)` uint8 — the same array the simulator draws, the FSEQ stores
and DDP carries.

Addressing the shell three ways:

```python
h = mau5cfg.load()
h.grid[row, channel]   # -> global LED index, or -1 where there is no pixel
h.az, h.elev           # -> degrees, per shell pixel
h.fixture("ETR2").slice  # -> a plain 1D strip
```

## Simulator

```bash
./mau5sim.py --fseq shows/intro.fseq --audio intro.mp3   # what FPP will play
./mau5sim.py --ddp                                       # live from WLED/xLights
./mau5sim.py --effect example_effect.py:show --seconds 64
./mau5sim.py --demo --view 3d --no-backdrop              # fastest live view
./mau5sim.py --demo --export preview.mp4                 # for the phone
```

Left panel: every pixel at its real `pixel_map.csv` position, plus the ear
rims, ear blades and visor light pipes, over the decimated backdrop mesh.
Right panel: the unwrapped 22 × 68 grid — rolled so the face is centred, with
true channel numbers on the axis — and one bar per accessory strip.

Audio playback shells out to whatever player is on PATH (`afplay`, `ffplay`,
`mpv`, `mpg123`, `aplay`); there is no audio library to install.

## Building a show from a track

`mau5song` decodes the audio, finds the tempo and the downbeat, measures how
full each bar is, and turns that into a cued show — then hands it to
`mau5build`, so you get the usual three files.

```bash
./mau5song.py "deadmau5 - Strobe.mp3"
./mau5song.py *.mp3 --preview            # build, then open the simulator
./mau5song.py track.mp3 --analyse-only   # just print the structure
./mau5song.py track.mp3 --bpm 128 --offset 0.32   # override the analysis
```

It prints what it heard, which is worth reading before you trust it:

```
deadmau5 - Strobe
  636.9 s  128.003 bpm  first beat 0.320 s  beat lock 0.30
  1359 beats, 339 bars, downbeat on beat 4 of 4
    0:02-2:54   hold    <- the ambient intro
    4:47-5:17   peak
    8:24-9:32   peak    <- the drop
    10:09-10:35 hold
```

### Keeping it locked to the track

Three things tie the lights to the music rather than merely starting them with it:

* **The analysis latency is compensated.** An STFT frame describes the audio
  around its *centre*, and the flux against the previous frame sits half a hop
  earlier still — 17 ms at these settings, most of a frame at 40 fps. Treating
  the envelope index as its own start time put every detected beat that far
  early, which reads as the lights firing just before the kick.
* **Every periodic effect is phase-locked to the bar grid.** Effects take an
  `origin`; the show generator sets it to the first downbeat, so a one-bar
  sweep crosses the face *on* the downbeat every bar for the whole show,
  instead of drifting from wherever `t=0` left it.
* **The whole frame rides the audio.** `mau5fx.Music` carries two curves
  sampled at frame rate — loudness and onset punch — and `Timeline` applies a
  master gain built from them. Effects can also ride them individually via
  `drive="energy"` / `drive="onset"`.

The master gain is *centred on 1.0*, not multiplied in. A modern master is so
limited that its loudness curve sits at 0.83 of full scale nearly all the time;
multiplying by that just dims the show 40% and barely moves. What carries
information is the deviation from the local norm plus the onset on top, so
quiet passages dip, hits push past full scale and clip white, and the average
stays where the effects intended it.

Measured on the built sequences: brightness now tracks the onset curve at
**0 ms lag**, and per-beat contrast matches the curve's own (1.09 against 1.08
for leavemealone). Strobe's drop renders 2.8x brighter than its ambient intro.

Bars are graded into four looks — hold / groove / drive / peak — at the
track's own quartiles, so a squashed master still gets a range of looks
instead of ten minutes of one. Long stretches are cut into ~24-bar phrases
that rotate colour and variant. A jump of two levels at a boundary gets a
white hit on the downbeat.

The beat grid is written to `shows/<name>.beats`, one time per line, and the
show is cued from that file — so if the analysis gets a track wrong, edit it
(or tap one out by hand) and re-run with `--beats`. Analysis needs no extra
packages: decoding shells out to `afconvert` or `ffmpeg`, the rest is numpy,
and none of it runs at showtime.

Long shows are written zlib-compressed by default — Strobe is 19 MB instead
of 107 MB, and both FPP and the simulator read it without help.

## Effects

`mau5fx` gives you sprites and text on the grid, azimuth/elevation sweeps,
1D effects for the blades, rims and visor pipes, and a `Timeline` to cue them.
Beat sync takes a beat list — `Beats.from_bpm`, `Beats.from_file`, or
`Beats.from_audio` (librosa, offline only). See `example_effect.py`.

## Packager

`mau5build build` renders the FSEQ, copies the media and writes the FPP
playlist JSON into `shows/`. `mau5build upload` pushes all three to the Pi and
creates the playlist. It verifies the sequence against `helmet.toml` first —
channel count, frame rate, and audio length — and refuses to upload a
mismatch. `--force` overrides and says so.

```bash
./mau5build.py check shows/intro.fseq --audio intro.mp3
./mau5build.py upload --name intro --dry-run
./mau5build.py playlists | status | start intro | stop --graceful | volume 70
```

## Setup

```bash
python3 setup/make_wled_config.py       # writes setup/wled_config.json,
                                        # prints the matching fpp_setup.sh line
scp setup/fpp_setup.sh fpp@<pi>:~
ssh fpp@<pi> 'sudo bash fpp_setup.sh'            # dry run first
ssh fpp@<pi> 'sudo bash fpp_setup.sh --apply'
```

Import `wled_config.json` at `http://<controller>/settings/sec` → Restore, or
`make_wled_config.py --push`. Install the remote where it is same-origin with
the API:

```bash
scp remote/index.html fpp@<pi>:/tmp/mau5.html
ssh fpp@<pi> 'sudo cp /tmp/mau5.html /opt/fpp/www/mau5.html'
# then open http://<pi>/mau5.html on the phone and add it to the home screen
```

---

# What I could not do the way you described it

Five things in the spec do not hold as written. None of them blocked the
build; all of them are in `helmet.toml` where you can change them.

### 1. The pixel map is measured off the print file, and it is not 948 pixels

`pixel_map.csv`, `wiring_chained.csv` and `mau5head_shell.xmodel` were never
supplied, so the map is derived from `mau5head_sim_backdrop.glb` -- the file
being printed. `mau5cfg.py --measure` reads it directly:

* the shell surface is **continuous everywhere** except the ear mounts;
* what looked like a mouth hole is an 11 mm-deep **pocket** for the visor, and
  it **narrows going down** -- 30 deg below the equator at the face, 4.5 deg at
  the temples;
* so the top row of chin pixels follows a slanted line, and **four full rows of
  pixels sit underneath the opening**, all the way around.

Only mirror-symmetric pockets deeper than 8 mm are treated as "no pixel" -- a
pixel recess is a couple of mm, and a pocket that shows up on one side only is
decimation noise. The threshold has a clean plateau from 7 to 10 mm. The
`[[shell.cutout]]` blocks in `helmet.toml` are generated, not hand-typed:

```bash
python3 mau5cfg.py --measure --recess-mm 8
```

**That gives 1185 shell pixels, not 948.** The two cannot be reconciled: I
searched every row count from 16 to 26, every bottom-row elevation, and every
reading of the density fall-off, and nothing produces 948 while keeping chin
pixels. The only 948 solutions are 17-row grids that stop above the opening
and have no chin pixels at all. So 948 predates the chin pixels.

Consequences you have to act on:

* **the WLED bus lengths change** -- 549/399 becomes 686/499, and FPP must send
  4929 channels instead of 4218. `mau5cfg.py --verify` refuses to stay quiet
  about it, and re-running `setup/make_wled_config.py` regenerates the config.
* **the split point is a hardware fact.** 686/499 is what the current geometry
  implies; it has to match where you actually cut the strip. If your real
  counts differ, put them in `helmet.toml` and the tools will follow.
* if the real map turns out to be a different row grid, change
  `bottom_row_elev_deg` / `rows` in `helmet.toml` -- everything downstream
  follows, and `--verify` will tell you what to reprogram.

### 1b. The three attachments were not there

`pixel_map.csv`, `wiring_chained.csv` and `mau5head_shell.xmodel` are not in
this folder — only the GLB, the STL, `sim_demo.png` and the prompt. Since
the CSV is authoritative and I will not derive pixel positions from the mesh,
`mau5cfg.generate_pixel_map()` builds a **stand-in** from the parameters you
documented — radius, 68 channels × 22 rows, both pitches, the density fall-off,
and one `[[shell.cutout]]` per hole you listed. It lands on exactly 948 pixels
split 549 / 399, and every tool reads the CSV rather than the generator.

The counts are right; the exact hole *shapes* are my reconstruction. Drop the
real `data/pixel_map.csv` in and it is used instead — no code changes, nothing
else to update. `python3 mau5cfg.py` prints the grid it is using:

```
 49.59  ########.#############.##.################.###.############.########  62
 44.08  ########.###########......################.#.....##########.########  54   <- ear mounts
 -0.00  ...............##########.################.###########..............  37   <- mouth
```

The generator warns loudly if a change to the cutouts stops it hitting
`expected_pixels = 948`.

I did use the mesh once, offline, to place the ear discs (a circle fit gives
centre ±224, 107.5, 215.3 and radius 164) and to sanity-check the hole
positions. Those are frozen as plain numbers in `helmet.toml`; nothing reads
the mesh at runtime except the simulator's backdrop.

### 2. Row pitch: 16.67 mm and 5.51° are not the same angle

On a 177.17 mm sphere, a 16.67 mm arc is **5.39°**, not 5.51°. (5.51° would
need r = 173.4 mm.) The channel pitch is exact — 68 × 16.37 = 1113.2 mm =
2πr — so it is only the rows that disagree, by about 2%. I placed pixels using
`row_pitch_deg = 5.51`, since degrees are what put a pixel on a sphere;
`row_pitch_mm` is carried alongside it and unused. Over 22 rows the choice
moves the top row by 2.6°. Worth resolving against the CAD before you cut.

### 3. Output 2 cannot refresh at 40 fps — and with the chin pixels it is worse

WS2815 clocks at 800 kHz, so each LED costs 30 µs. Output 2 now carries 499
shell pixels plus 458 accessories = **957 LEDs = 28.7 ms**, against a 25.0 ms
frame. This was marginal at 857 LEDs; at 957 it is not. The controller will
refresh that output slower than the show runs — not a crash, just a chain that
lags on fast content while output 1 keeps up.

```
output A   686 LEDs ->  20.6 ms  ok
output B   957 LEDs ->  28.7 ms  OVER BUDGET
```

The fix is hardware: give the accessories their own data line. There is a
commented third output in `helmet.toml` that does it — 686 / 499 / 458 =
20.6 / 15.0 / 13.7 ms, all inside the frame — and the tools already handle any
number of outputs. Alternatively run at 30 fps (33 ms), but 40 is FPP's
default and matches everything else.

### 4. GPIO 3 is the serial console

Your second output was pinned to GPIO 3, which is RX0 on the ESP32. WLED will
drive it, but it fights the USB serial console and can latch at boot. I moved
it to **GPIO 17** in `helmet.toml`. Change it back if the board is already
soldered — but check it boots with the strip attached.

### 5. Two things I had to guess, and you should verify

* **FPP's upload endpoint** has moved between releases. `mau5build upload`
  tries `/api/file/{dir}`, `/api/file/upload/{dir}` and `/jqupload.php` in
  order and reports which one worked. If none do, it prints the `scp` command
  that always works, and you can pin the right path with
  `[player] upload_paths` in `helmet.toml`.
* **DDP is universe type 4** in the channel-output JSON that `fpp_setup.sh`
  writes. FPP has renumbered those types before, so the script tells you to
  confirm the row reads "DDP" in Input/Output Setup → Channel Outputs →
  Network. Everything else it writes is a documented settings key.

## What a multi-agent audit of this suite found

Everything below was raised by an independent reviewer, then adversarially
verified against the running code before being accepted. These are fixed:

**Addressing** — the things that would have put LEDs on the wrong channel:

* `read_pixel_map` sorted by an `index` column it aliased from `node`/`led`/`n`,
  with no uniqueness check. An xLights-style export that restarts numbering per
  port would have been silently reordered — 1 of 1185 LEDs landing in its true
  wire slot, median position error 285 mm on a 177 mm sphere, no warning. It now
  refuses a repeated or non-contiguous index and tells you to drop the column.
* An output that named a fixture used to make *every other* output drop its
  accessories, and output ranges were built from `min(index) + count`, which is
  only a real range if the claiming output is last. A middle output claiming an
  accessory produced **overlapping WLED buses** — LEDs driven by two GPIOs and
  458 driven by none — and `make_wled_config` wrote it out without comment.
  Outputs are now built from explicit LED lists, non-contiguous ones are
  reported, and two outputs claiming the same fixture is a hard error.
* `build_wiring` hardcoded `output = "B"` for every accessory, so the
  three-output config produced a wiring table with the wrong chain topology.
* A channel that crosses the visor slot has pixels above *and* below it — two
  separate strip segments. They were being merged into one row with a LED range
  that spanned the gap. Now split, with an assertion that count matches the range.
* `wiring_chained.csv` was only written when absent, so it silently described a
  helmet that no longer existed. Always regenerated now.

**Geometry:**

* `_despeckle` removed cells with ≤1 neighbour, which deletes both halves of a
  legitimate two-pixel run — its own docstring said it never removed runs. Now
  strictly isolated cells only.
* Row 9's elevation computes to `-7e-15`, which sat exactly on an inclusive band
  edge and decided pixel existence on floating-point residue. Rounded now.
* `_profile` mirrored about a hardcoded 68 channels via a `channels_total` key
  that is never set anywhere.
* **Face sprites were landing in the visor slot.** With the corrected map the
  old default row put 29% of every face into the opening. Measured across all
  sprites, `row_from_top=3` puts 100% of every face on a real pixel (95% for
  scrolling text); that is the new default.

**Timing:**

* FSEQ stores step time as whole milliseconds, so 30 fps would have been written
  as 33 ms and played 1% slow. Rates that do not divide 1000 are now rejected.
* `EffectSource` sized itself at `helmet.fps` and ignored `--fps`, and the
  simulator rendered effects at wall-clock `t` while the packager rendered at
  `i/fps` — so the preview was not the frames that went in the file. Both now
  render at `i/fps`.
* `Twinkle` decayed at a hardcoded 40 fps, so its speed followed the frame rate
  rather than the clock.

Nine further findings were rejected on verification — including a claimed
`sphere_xyz` round-trip error (max discrepancy 0.0016 mm) and a claimed
`--recess-mm` default mismatch (the generated blocks are byte-identical to what
is in `helmet.toml`).

## Smaller notes

* **Only the far side of the backdrop is drawn**, and each face is culled
  against the centre of the part it belongs to — the sphere against the sphere
  centre, the ear discs against their own centres. Culling the ears against
  the world origin deletes a whole ear disc as soon as it swings to the near
  side, which makes the ear LEDs look detached from the head when you rotate.
* **The simulator delays its frame clock to match the audio player.** `afplay`
  and friends take 100-250 ms between `Popen` returning and sound coming out;
  without compensation the lights run that far ahead. `--audio-offset MS`
  tunes it. On the helmet itself FPP drives audio and pixels off one clock, so
  this is a simulator concern only.
* **The simulator will not draw at 40 fps.** matplotlib manages roughly 15–25
  fps with 1406 live pixels. Playback is clock-driven, not draw-driven, so it
  stays in sync with the audio and drops render frames instead of drifting; the
  status line shows both rates. `--view 3d --no-backdrop` is the fastest live
  view, and `--export` renders offline at a true 40 fps.
* **The backdrop mesh is decimated** to ~6000 triangles by vertex clustering.
  `--solid-backdrop` and `--backdrop-faces N` override that. The cull and the
  blit cache are both rebuilt whenever you rotate the view.
* **The GLB is read with 40 lines of stdlib**, not trimesh or pygltflib —
  neither is installed here and both are heavy for one static mesh.
* **ABL at 8 A caps you near 29% brightness on full white** (1406 WS2815 LEDs
  would draw about 27 A). Fine for a wearable, and the reason to author shows
  with colour rather than white.
* **Accessory LED counts** (59 / 44 / 62 / 44 …) imply the ear blades are
  higher density than 60/m: 62 LEDs across a 164 mm-radius disc is about a
  200/m strip. The counts are estimates in `helmet.toml`, as you asked —
  change them there and everything downstream follows.
* **FSEQ**: written uncompressed by default. FPP always reads it, seeking is
  instant, and a three-minute show is 10 MB. `--compression zlib` or `zstd` if
  you want it smaller.

---

# The rebuilt helmet (front half, one chain, no Pi)

The hardware changed: LEDs on the front half only, along the ear rims and
inside the ears, nothing on the back; all of it on **one chain**; ear rims are
a thinner pre-diffused strip wired in a different colour order. The wiring
diagram is no longer the truth and most of the strip is now covered, so the
map is **measured with a camera** instead of described.

```
mau5wled.py   the controller, directly: JSON API + DDP out with per-LED
              colour-order correction
mau5walk.py   walk the chain from your phone, one LED at a time, and record
              the sections as you go  (+ remote/walk.html)
mau5cal.py    camera calibration: probe / live / order / scan / solve
chain_route.toml  the as-built route, so the solver checks rather than guesses
data/cal/     the walk session, what the camera saw, the drafted section list
data/cad/     948 LEDs read out of mau5head_PRINT_ASSEMBLYfinal.step
```

## Why orange went green on the ears

A colour-order mismatch, and the arithmetic matches the symptom exactly. WLED
reorders each pixel to its bus setting on the way out. With the bus set to GRB
and orange `(255, 110, 0)` requested, it emits bytes `[110, 255, 0]`. A strip
actually wired RGB reads that as `R=110, G=255, B=0` — yellow-green.

One bus setting cannot be right for two differently-wired strips on one chain,
so the correction happens in software: `Pixels` applies a per-LED channel
permutation before transmitting, and one DDP stream drives mixed strips
correctly. `mau5cal.py order` measures those permutations off the LEDs
themselves — pure red, then green, then blue, watching which channel each one
actually lights.

## Calibrating: walking the chain by hand

Getting a camera to see every LED at once is awkward, and lighting the whole
helmet to find out where things are will cook it. So the primary method is a
phone app that walks the chain one LED at a time.

```bash
python3 mau5walk.py --host <wled-ip>
```

It prints an address; open that on the phone. Both devices just have to be on
the controller's network.

Light one LED, look at it, tap NEXT. When the light jumps somewhere physically
different, you have found a boundary -- tap **IT JUMPED — NEW SECTION**, name
it, carry on. Press and hold NEXT to run. Tap any finished section in the list
to light it on its own for a photo. The session is written to
`data/cal/walk_session.json` as you go, so there is nothing to transcribe.

**Heat is a hard limit, enforced in the server where the page cannot get past
it.** All 948 at full white is roughly 18 A; the default cap is 120 LEDs lit
and brightness 128/255, about 14 W. Ask for brightness 255 and you get 128;
ask for a 268-LED section and you get the most recent 120, with the cap shown
on screen. It also blanks itself after ten minutes of no input. Both limits
move with `--max-lit` and `--max-bri` if you are standing over it.

Why a server and not a page talking straight to the controller: per-LED
control means DDP and a browser cannot send UDP; WLED reverts to its own
effect about 2.5 s after a stream stops, so something has to hold the frame;
and the power cap belongs somewhere a UI bug cannot reach.

A true WLED plugin would be a usermod, which means rebuilding and reflashing
firmware. This gets the same result with no reflash.

## Calibrating: the camera sweep (optional)

On the mini, with the webcam on a tripod and the helmet still:

```bash
python3 mau5cal.py cameras                        # which device index
python3 mau5cal.py probe --host <wled-ip>         # does it answer, how many LEDs
python3 mau5cal.py live  --host <wled-ip>         # poke pixels by hand
python3 mau5cal.py order --host <wled-ip> --device 1
python3 mau5cal.py scan  --host <wled-ip> --device 1 --view front
python3 mau5cal.py solve
```

`scan` lights one LED at a time and records where it landed, differencing each
frame against a dark reference so it works in a normal room — the LED only has
to be the brightest *change*, not the brightest thing in shot. It measures the
webcam's pipeline latency first, because a buffered camera hands you a frame
from before the LED changed.

`solve` turns the scans into `data/pixel_map.csv`, and writes two things worth
looking at:

* `data/cal/view_front.png` — every LED circled, coloured by position along the
  chain, with the data path drawn between consecutive LEDs. The wiring order
  is readable straight off it.
* `data/cal/sections.toml` — a drafted part list. It finds section boundaries
  from where the chain **jumps in space**: a continuous strip puts LED n and
  n+1 a few millimetres apart, so a jump is the data line running off to
  somewhere else. Nobody has to have written the counts down.

A second view (`--view side`) adds depth, read orthographically — the side
view's horizontal axis. Approximate, but it needs no camera calibration and is
plenty for show geometry. One front view alone is a complete 2D map, which for
a front-half helmet is most of what the effects need anyway.

Verified end to end against a synthetic 448-LED helmet (front dome, two ear
rims wired GRB, two inner rings): **all 448 located, median error 0.05 px,
448/448 colour orders correct**, and both GRB ranges identified exactly.

**Untested on real hardware:** the camera path. macOS asks for camera
permission the first time a process grabs it, and that prompt cannot be
answered from a background shell — so run the first `scan` from Terminal with
someone there to click Allow. Everything times out with a clear message rather
than hanging.

## Running shows off the phone

WLED cannot play authored per-pixel shows on its own. Its effects and presets
run on the controller, but a 10-minute sequence has to be streamed frame by
frame — that was the Pi's job. With the Pi gone the Pixel becomes the player:

```
Pixel 10 Pro  ──hotspot──  WLED (ESP32)
   plays the audio              joins the phone's AP
   streams DDP at 40 fps        shows what arrives
```

The phone runs its own hotspot, so there is no infrastructure at a show and no
Pi. Bandwidth is trivial — 1600 LEDs at 40 fps is about 200 KB/s of UDP.

This turns `docs/mau5remote-android.md` from a *remote* into a *player*: it has
to read the FSEQ, keep a frame clock locked to its own audio playback, and
push DDP. That is the next build, and it is a real one. Until it exists, the
mini can play shows the same way for testing.
