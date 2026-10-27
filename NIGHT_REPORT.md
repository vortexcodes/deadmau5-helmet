# Overnight build — 27 Oct 2026

*Second pass: test suite, bug fixes, 12 more presets, measured beat-sync correction, favourites, watchdog, health check.*

Everything below runs. Nothing here needs the helmet except where it says so.

## Start here in the morning

```bash
cd "/Users/jones/deadmau5 app" && python3 mau5doctor.py
```

That checks the lot — map, power, colour correction, presets, shows,
network, and the helmet itself — and tells you which part is wrong if any
is. Then:

```bash
cd "/Users/jones/deadmau5 app" && python3 mau5ctl.py
```

Finds the controller, prints a URL, open it on the Pixel. Audio plays **on the
phone**, so it goes to whatever Bluetooth speaker the phone is paired with.

## The heat fix (needs you, ~10 minutes)

Your WLED build already has a relay output configured on **GPIO 18**, unused.
Ethernet holds 21/19/22/25/26/27/5/23/33/0, the strip is on 16, the button on 17.

Put a high-side switch — a 12 V relay module or a P-MOSFET board — on the 12 V
feed **to the strip only**, gated by GPIO 18, with the controller fed from
upstream so it stays on the network. WLED drops that pin whenever the lights are
off, which takes idle draw from 7.5 W to nothing.

Measured: 623 WS2815 pull ~0.62 A with every pixel dark. That is the heat you
feel. No software setting reaches it — the ICs are powered whenever 12 V is.

A Kasa plug on the PSU does the same job without soldering, and would let me cut
power remotely, which I could not do last night.

## What the camera settled

| question | answer |
|---|---|
| chain health | all 623 alive, no dead sections |
| orientation | starts at the chin, ends upper-left — as the CAD predicted |
| symmetry | passes: groups 0 and 29 land equidistant about the centre |
| bottom-band dispute | CAD right (2+2); LED 40 sits 4 px from 41, 34 px from 38–39 |
| colour inversion | indices **492–527** — one fault, both ear rims |
| fix verified | red now reads R 0.96 on the rims, was G 0.87 |

The rims are adjacent in the chain (ear1's rim runs straight into ear2's), which
is why one wiring difference turned both ear outlines green.

Not settled: the two visor clusters. The shell diffuses so hard that nine LEDs
glow across half the sphere, so a one-LED gap is invisible. Using the CAD
reading, which the camera confirmed everywhere it could be checked.

## New files

| file | what |
|---|---|
| `mau5map.py` | builds `data/cal/pixel_map.csv` — 623 LEDs with real 3D positions |
| `mau5engine.py` | geometry-driven preset engine, 20 presets |
| `mau5preview.py` | simulator: renders any preset to png/mp4 |
| `mau5show.py` | builds a show from a track; previews and plays it |
| `mau5ctl.py` | the controller backend: presets, shows, audio clock |
| `remote/control.html` | phone UI |
| `mau5power.py` | region-aware thermal clamp |
| `mau5eye.py` | borrows a camera through a browser |
| `mau5shoot.py` | runs the checks and photographs each |
| `mau5verify.py` | the check definitions |
| `mau5doctor.py` | one-command health check |
| `test_mau5.py` | 21 invariant tests |
| `data/cal/strips.json` | measured colour-order correction |
| `data/cal/power.json` | per-region power profile |

Two safety things load automatically inside `Pixels.send()`, so no tool can skip
them: the power guard and the colour correction.

## Power model

Global budget 1500 mA of LED current. Worst case 2.12 A with standby, 25.5 W.
Verified on the wire: a request for 11.8 A came out as 1.5 A.

| region | LEDs | ceiling | budget |
|---|---|---|---|
| shell | 399 | 64/255 | 300 mA |
| ear1 tubes | 93 | 255/255 | 560 mA |
| ear1 rim | 19 | 160/255 | 260 mA |
| ear2 rim | 17 | 160/255 | 250 mA |
| ear2 tubes | 95 | 255/255 | 580 mA |

Over budget, it scales everything down weighted — the shell gives up six times
faster than the tubes — rather than cutting regions off. Change `budget_ma` in
`data/cal/power.json` once we know what the helmet can actually take.

**25.5 W peak is still arithmetic, not a measurement.** Worth a thermal test
before a long set.

## Presets (20)

solid, breathe, rainbow, scanner, wipe, strobe, twinkle, comet, ripple, plasma,
fire, earspin, tubepulse, police, eq, beatpulse, **text**, sprite, eyes, matrix

```bash
python3 mau5preview.py --sheet          # all of them, one image
python3 mau5preview.py text --text "HELLO" --mp4 /tmp/t.mp4
python3 mau5preview.py --list           # parameters
```

Text note: the usable band is 7 rows over py 28–145 mm, about 14–20 columns, so
two or three characters are legible at once and the rest scrolls. That is the
hardware's real resolution, not a software limit.

## Shows

```bash
python3 mau5show.py build "deadmau5 - Strobe.mp3"
python3 mau5show.py preview "shows/deadmau5 - Strobe.json" --start 500 --seconds 45
python3 mau5show.py play "shows/deadmau5 - Strobe.json"
```

- **Strobe** — 636.9 s, 128.0 bpm, 18 cues
- **leavemealone** — 222.8 s, 174.0 bpm, 10 cues

Old FSEQ and playlist files from the 1643-LED layout moved to `shows/superseded/`.

## Second pass

**A test suite** — `python3 test_mau5.py`, 21 checks across map, presets,
power, colour, shows, wire format, camera and audio. Written against the
things that actually went wrong, so they cannot come back silently. Two of
the first failures were bugs in the *tests*, not the code: `buf + 1` on a
`uint8` array wraps 255 to 0, and I had assumed a straight-ahead LED must
sit on the equator when it actually sits near the crown.

**A real bug it caught:** six of the twenty presets (`eq`, `fire`,
`plasma`, `police`, `rainbow`, `wipe`) returned HTTP 400 when tapped,
because the UI sends `color` and those presets don't have that parameter.
Now filtered at the HTTP boundary, with a colour redirected to whatever
that preset calls its colour — while the Python API stays strict so a typo
in code is still an error.

**Beat sync, measured and corrected.** Generating click tracks of known
tempo and phase showed the beat grid landing **13.2 ms early**, consistently:
sd 1.0 ms over 1088 beats, 90–174 bpm, several start offsets, 4 ms jitter,
and kick/noise/pad attacks from 6–60 ms decay. The geometric window-centre
correction was right as far as it went; a Hanning window weights a
transient near its leading edge down, so the flux peaks late. Measured and
removed — **now +0.05 ms, worst single beat 5.7 ms**. Both shows rebuilt.

**Crossfades and downbeat accents.** Cues overlap for 0.6 s instead of
cutting: the discontinuity at a boundary drops from 143 to 30. Loud
sections get an accent locked to the bar grid.

**12 more presets** (32 total): spiral, pinwheel, heartbeat, confetti,
lightning, wave, gradient, chase, vu, sparkle, countdown, split. `split`
runs a different effect on the shell and the ears, which are genuinely
different instruments here. `countdown` uses a chunky 3×5 digit face — a
5×7 glyph held still gives 35 cells and the LEDs aren't spread evenly
enough to fill them, so digits came out unreadable.

**Favourites** — tweak a preset's sliders, name it, tap to recall. Saved
atomically to `data/cal/favourites.json`.

**A watchdog.** DDP is UDP, so sending into the void raises nothing: a
controller whose helmet rebooted looked perfectly healthy and simply lit
nothing. It now notices within six seconds, says so in the UI, and re-arms
realtime mode when the helmet returns.

**Live parameter editing** in the phone UI, with the panel redrawing only
when something changed — it used to rebuild every 1.5 s, which would have
yanked a slider out from under your thumb.

**Performance**: 189 µs per frame for the whole send path, 132× headroom at
40 fps. The real ceiling is the wire — 623 WS2815 at 30 µs each caps you
near 53 fps.

**The superseded files now say so.** `mau5sim.py`, `mau5cfg.py`,
`mau5build.py` and `helmet.toml` print or carry a banner explaining they
describe the CAD helmet (1185 pixels, two chains, Pi + FPP) and pointing at
the current path. Nothing reads them any more, but they were a trap.

## Third pass — the alignment test found a real fault

Your swept-bar idea was the right test and it caught a genuine bug.

**27 shell strips were running backwards.** The map guessed each strip's
wiring direction by continuity. Measured against the camera, that guess was
right on **19%** of strips; the CAD's own stored order managed **48%**.
Neither is a wiring diagram. The camera decides now, one strip at a time,
and agreement is **52 of 52**. Whole-shell correlation went from −0.871 to
**−0.977**. This is almost certainly what you could see.

**The chain is 622 LEDs, not 623.** Probing the tail with the bus widened to
640, index 622 is dark at full brightness and so is everything past it. Your
last walk tap went one LED beyond the end. Corrected through the map,
configs, controller and tests.

**The ears were badly wrong and are now measured.** The parametric model was
out by a median of 122 mm. `mau5locate.py` lights each LED alone at low
drive — your brightness suggestion, which shrinks the bloom from 140 px to
25 while the centroid stays put within 2 px — and records its camera
centroid. All 622 measured. The 399 CAD-exact shell points then solve the
camera projection, which is inverted for the ears.

| region | before | after |
|---|---|---|
| shell | r = −0.871 | **−0.977** |
| ear1 | r = −0.355 | **−0.995** |
| ear2 | r = −0.447 | **−0.988** |

On hardware the ears now sit at **6.3 and 8.9 mm** residual against the
shell's 21 mm — better than the CAD, because they are measured directly
while the shell's reading carries optical displacement.

**An independent check I did not fit for:** the two ears come out 310 mm and
302 mm wide, 3% apart, for a part that is identical on both sides. That also
caught a reflection being measured as LED 498 — peak 16 against its
neighbours' 255 — which on its own had stretched one ear by 40%.

**Two measurement artifacts, chased down rather than waved at.** The ear
slope sat at 0.82 where it should be 1.0. Not sweep truncation (fixed by a
margin, which only moved the shell) and not neighbour bleed (flat across
sample radii 2–14). It is the shared translucent disc: every LED on an ear
lights the whole panel, and that pedestal drags each LED's weighted mean
towards the disc average. Clipping it lifts the ears to 0.95/0.90 while the
shell, which shares no panel, does not move.

## Power, in software

You asked for this to be solved in software rather than by cutting power.
Half of it can be.

**The active half is now rationed over time, not just per frame.** The
per-frame guard could not tell a bright chorus from a bright half hour, and
it is the half hour that melts hot glue. `ThermalBudget` is a leaky bucket
over delivered energy: full brightness for about 62 s, then easing to a
sustained 11 W, with quiet passages refilling the bucket. Two minutes of
rest restores full brightness. Both numbers are in
`data/cal/power.json` and are meant to be tuned by feel — run it, touch the
helmet, move `sustained_w`.

**The standby half cannot be.** 622 WS2815 draw about 0.6 A — 7.5 W —
whenever 12 V reaches them, lit or dark. That is the ICs, not the LEDs, and
no data sent down the wire changes it. I have not found a way around it and
I do not think one exists. It is subtracted before anything is rationed, so
the budget never hands out headroom that is not there. The GPIO 18 relay
remains the only thing that removes it.

## Known gaps

1. **No Android app.** No SDK, gradle or adb on this machine, so I could not
   build or test an APK. The web app covers everything except phone-only
   operation, because a browser cannot send the UDP that WLED needs.
2. **Ear positions are estimated**, fitted to the camera view, not measured.
   Marked `estimated` in the pixel map. Effects that care about which ear and
   roughly where are fine; anything needing millimetres is not.
3. **Visor cluster ordering** unresolved — see above.
4. `mau5sim.py`, `mau5fx.py`, `helmet.toml` still describe the old full-sphere
   helmet. The new path does not use them; they should be retired or ported.
