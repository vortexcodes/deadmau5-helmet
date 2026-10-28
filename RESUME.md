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
