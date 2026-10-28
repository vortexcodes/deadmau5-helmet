# Where the preset review got to

`mau5review.py` is new and working: it lights every preset on the real
helmet and photographs it, freezing each animation at a chosen `t` and
differencing against a dark frame taken moments earlier, so the room
falls out of the picture and only the LEDs remain.

    python3 mau5review.py --level 0.22 --phases 3

A full pass is 102 shots in four minutes. The last one is in
`data/cal/review/` on the old laptop -- not committed, just re-run it.

## What that pass showed

The helmet looks good. Colour order is right everywhere (orange reads
orange, green green), both ears light evenly, the shell grid is clean.
No dead regions.

The dark horizontal band across every photograph is **not a fault**: the
map has no LEDs between z = -21 mm and z = +12 mm, because that is the
visor slot. The shell is two disconnected bands -- a 96-LED chin
crescent below it and a 305-LED dome above.

## The one real bug, diagnosed but not yet fixed

The glyph presets -- `text`, `sprite`, `countdown` -- drop strokes.

They gather: each LED looks up which bitmap cell it sits in. On this
dome **27% of the cells contain no LED at all**, so better than a
quarter of every glyph silently vanishes. Held still, "MAU5" is not
readable; `countdown` shows a stub.

The fix is a scatter pass alongside the gather: every *set* cell that
caught no LED of its own claims the nearest one within about 1.5 cells.
Areas keep filling correctly from the gather, and one-cell-wide stems
can no longer disappear. A prototype is in the transcript; it was being
measured when the laptop had to move.

Do **not** switch these presets to an azimuth grid. It equalises LED
density (31% -> 18% empty) but bends the letterforms round the sphere,
and the flat x/z layout is deliberate -- see the comment in `Helmet`.
Fix the sampling, keep the layout.

Two tuning fixes go with it:

- `countdown` has `x_half = 50`, so the digit occupies 100 mm of a
  340 mm face. It should be about 130. Past ~135 the outer column is
  foreshortened more than 2x and the digit starts to look wrong.
- `eyes` uses `size = 58`, `spread = 78` and a `** 0.6` falloff, which
  is two overlapping soft blobs reading as one wash. It needs a smaller
  radius, more spread and a sharper exponent.

## Still open from before

The GPIO 18 relay. 622 WS2815s draw ~0.6 A whenever 12 V reaches them,
whatever the data line says, and no software can touch it. The helmet
had been powered 7.5 hours when this session started.

## The ears were never where the map thought (2026-10-28)

Jones: "on the left ear from inside on the first 10 or so leds (at the
top of the skull) are either behind or something bc it looks wrong".

Right on both counts, and for two separate reasons.

**LEDs 399-406 are a run of their own.** Splitting ear1_tubes where the
step between consecutive LEDs jumps gives runs of 8, 19, 36 and 27, and
that first 8 is the strip crossing the gap between the top of the shell
and the ear disc -- not on the disc at all. The right ear has the same
thing, two LEDs long, at 528-529. Light them and look:

    python3 mau5wled.py --range 399-406 --color 255,0,0 --seconds 20

**The ears' depth was never measured, and it was not even consistent.**
`mau5fitmap` replaced x and z with the camera's answer and kept y from
the parametric model evaluated at the LED's chain index -- a model whose
own docstring says it tracks the real ear at r=-0.36. The two halves of
the same coordinate disagreed by 36 mm rms. Depth now comes from the
ear's own plane evaluated at the measured x.

The tilt of that plane is the one number still guessed, and it is
`DISC_TILT_DEG` in mau5fitmap. It is 0 because the rim says so: a disc
tilted about the vertical images as an ellipse narrower than it is
tall, and both measured rims come out *wider* (1.20 and 1.15, at 4-5 mm
rms). Pitch cannot arbitrate -- solving for the tilt that most evens out
the LED spacing moves the spread by 0.3%, which is noise. **A second
camera pose would measure it outright**, and is still the one test that
would also confirm the shell correction.

**And azimuth was the wrong coordinate for them.** `nfa` was
`clip((fa + 90) / 180, 0, 1)` with `fa` the azimuth about the head's own
centre. The ears are flat plates mounted behind that centre, so their
azimuth ran backwards across them and then clipped: every left-ear LED
read exactly 0.000 and every right-ear LED exactly 1.000. 223 LEDs --
36% of the helmet -- shared two values, so a sweep could only flash the
ears, never cross them. `fa` is now the angle from one shell-radius in
front, which is the same thing for the shell (r=0.985 against the old
scale) and monotonic in screen x, so nothing can read backwards.

Worth knowing: `alignbar --axis z` now lights the whole ear at once.
That is correct -- the ears really are at one depth -- but it means the
depth sweep can no longer tell one part of an ear from another.

## Offline mode (2026-10-28)

Jones: "make sure we have a functional offline mode (where my phone can
connect to the LED controller and play all the animations without
being on a network)."

Built and tested end to end against a fake controller; **not yet run
against the helmet**, because the Mac is on 10.1.7.142/21 and the
helmet is on 192.168.10.x. Three commands are waiting for a network:

    python3 mau5offline.py config --host <ip> --ap-psk '<pick one>' --apply
    python3 mau5offline.py deploy --host <ip>
    python3 mau5offline.py check  --host <ip>

`deploy` uploads the page and then reads it back and compares, so it
tells you if the firmware will not serve a `.gz` under its plain name
rather than leaving a broken helmet; it falls back to the
uncompressed page by itself if that happens.

**The page lives on the controller, and that was forced.** A browser
cannot send UDP, so DDP is out. An https page cannot reach a plain-http
192.168 address, so no GitHub Pages and no installable PWA. A
plain-http page is not a secure context, so no service worker and no
serving it from the laptop. The only HTTP server on that network is
WLED, so the player goes on its filesystem: 51 kB gzipped, same origin
as the API, nothing installed on the phone.

**The engine and the guard are ports, verified as ports.**
`test_mau5.py offline` renders all 34 presets in Python and in
JavaScript at seven times each and compares (worst 0.0002 counts out
of 255), drives both power guards with the same frames and clock
(currents identical), and round-trips the wire encoder through
`mau5fake`'s own `i` parser, including the colour-order permutation.
The geometry is exported from `Helmet` rather than recomputed, so the
port can only disagree about colour.

### What to check the first time it runs on the helmet

- **The dead man.** The player re-arms WLED's nightlight (instant
  mode, 1 minute) every 20 s, so a phone that is dropped or dies
  leaves the helmet lit for at most a minute. Nothing here could test
  that nightlight behaves as the docs say. Start it, lock the phone,
  and time how long the helmet stays on. Watch also for a brightness
  twitch every 20 s -- the re-arm is an off-then-on, and if WLED
  restores a brightness on the off it will show.
- **The frame rate.** Everything about the rate is adaptive, so there
  is no number to get wrong, but the one the ESP32 actually manages is
  unknown. Expect 10-20 fps on `fire` and far more on the cheap ones.
- **Whether the WebSocket echoes state.** The player uses inbound ws
  messages as acknowledgements and paces itself by them; if the build
  stays quiet it falls back to the timer after a second. Either works,
  but which one happens is worth knowing.

### What it deliberately does not do

The five music shows. The cue lists are 13 kB and would go straight
over; the analysis behind them is 250-670 kB a song at 40 Hz, and the
phone would have to hold the clock. That is the next piece.
