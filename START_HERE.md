# Picking this up on another machine

```bash
git clone https://github.com/vortexcodes/deadmau5-helmet.git
cd deadmau5-helmet
python3 -m pip install numpy pillow matplotlib
python3 test_mau5.py                            # 41 checks, no hardware needed
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

The phone player is in that category too. It is built from the map and
the power model, so it can be made and driven anywhere:

```bash
python3 mau5offline.py build            # the page the controller will serve
python3 mau5fake.py                     # a controller that is not there
```

Open `http://127.0.0.1:8770/mau5.htm` for the player and
`http://127.0.0.1:8770/fake/view` for what the helmet would be showing.

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

    data/cal/pixel_map.csv            the 621-LED map (built by mau5slots.py)
    data/cal/led_positions.csv        what the front camera measured
    data/cal/led_positions_pose4.csv  what the high camera measured
    data/cal/walk_session.json        the hand walk from the first night
    data/cal/power.json               regions, ceilings, thermal budget
    data/cal/strips.json              the measured colour-order corrections

Losing those means re-running the localisation. Losing the photographs
means nothing.

## The music is not in here

The repo is public, so the tracks are not in it -- they are commercial
releases and not ours to hand out. The show files reference them by
filename, so to play a show, drop the mp3s next to the show JSONs:

    deadmau5 - Strobe.mp3
    deadmau5 - Strobe (Dimension Remix).mp3
    deadmau5 - Ghosts n Stuff (Nero Remix).mp3
    Fred again.. & Baby Keem - leavemealone.mp3
    beneath (with raxaj).mp3

They are in the private `vortexcodes/deadmau5-helmet-archive`, which is
the pre-split repo with everything in it:

    git clone https://github.com/vortexcodes/deadmau5-helmet-archive.git

Everything that does not play audio -- the map, the presets, the power
model, the tests -- works without them.
