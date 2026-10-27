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
