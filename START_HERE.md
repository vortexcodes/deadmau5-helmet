# Picking this up on another machine

```bash
gh auth login                                   # once, device code, ~1 min
gh repo clone vortexcodes/deadmau5-helmet
cd deadmau5-helmet
python3 -m pip install numpy pillow matplotlib
python3 -m pytest test_mau5.py -q               # 25 tests, no hardware needed
```

Then start Claude Code in that folder.

## What works away from home

Everything except the helmet itself. The map, the power model, the preset
engine, the show builder and the whole test suite run off the committed
calibration, so presets can be written and checked on a laptop anywhere:

```bash
python3 mau5show.py list
python3 mau5doctor.py --offline
```

## What needs to be on the home network

The helmet is a WLED controller on the house LAN (it was 192.168.10.172,
but it is found by scanning, so a new address is fine). Anything that
lights it up -- `mau5wled.py`, `mau5review.py`, `mau5ctl.py`,
`mau5baralign.py` -- needs to be on that network.

## What is deliberately not in the repo

Calibration photographs, the timelapse frames and the rendered videos:
about 280 MB, all of it regenerable in a few minutes with `mau5locate.py`
and `mau5review.py`. The calibration *results* are committed, and those
are the part that took the night:

    data/cal/pixel_map.csv      the 622-LED map
    data/cal/led_positions.csv  what the camera measured
    data/cal/power.json         regions, ceilings, thermal budget
    data/cal/strips.json        the measured colour-order corrections

Losing those means re-running the localisation. Losing the photographs
means nothing.

## The repo is private

It contains your own mp3s. Making it public would redistribute those, so
it is private; the music is gitignored out of nothing, it is simply in a
repo only you can read. If you want a public version, say so and I will
split the code out without the tracks.
