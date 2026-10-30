#!/usr/bin/env python3
"""mau5tune -- does the show actually follow the track, and by how much.

The shows were tuned by watching them, which catches a show that is
obviously wrong and misses the thing that was actually wrong here:
brightness correlated *negatively* with the music.  The loud effects
had landed in the quiet sections, and no amount of looking at a
thirty-second clip reveals that -- it needs the whole track and a
number.

So this renders a show end to end through the real engine and the
real power guard, and measures four things:

  follow    Pearson r between what the helmet draws and how loud the
            track is.  This is the one that was negative.  Above
            about +0.4 the helmet reads as driven by the music; near
            zero it reads as running beside it.
  swing     how much of the brightness range the show actually uses.
            A show pinned at the guard's ceiling has nowhere to go
            when the drop lands.
  beat      how much brighter a frame on a beat is than one off it.
  variety   distinct presets, and how long each one holds.

Nothing here needs the helmet.  It wants the track's analysis, which
is in shows/*.npz and does not need the audio either.

    python3 mau5tune.py                    # score all five
    python3 mau5tune.py --sweep dynamics   # and what tuning them does
"""

from __future__ import annotations

import argparse
import json
import os

import numpy as np

import mau5engine as E
import mau5power
import mau5show

HERE = os.path.dirname(os.path.abspath(__file__))
SHOWS = os.path.join(HERE, "shows")


def load_show(name):
    path = name if os.path.isabs(name) else os.path.join(SHOWS, name)
    if not path.endswith(".json"):
        path += ".json"
    with open(path) as f:
        show = json.load(f)
    cache = show.get("analysis")
    npz = os.path.join(SHOWS, cache) if cache else None
    if not npz or not os.path.exists(npz):
        return show, None
    music = mau5show.Music(show.get("track", ""), fps=show.get("fps", 40),
                           cache=npz)
    return show, music


def score(show, music, helmet, guard_for, samples=500, override=None):
    """Render the show across its whole length and measure it.

    Sampled rather than every frame: 500 points over ten minutes is
    one every 1.3 s, which is far finer than any cue and keeps this
    to a couple of seconds a show.
    """
    sh = dict(show)
    if override:
        sh.update(override)
    # A fresh guard per show, or the thermal bucket arrives full from
    # whatever was scored before and every show after the first reads
    # as flat.  That is not a subtle effect: it put three of the five
    # at the sustained floor and made them look like bad shows.
    guard = guard_for()
    player = mau5show.Player(sh, helmet=helmet, music=music)
    dur = float(show.get("duration", 0)) or 1.0
    ts = np.linspace(0.5, dur - 0.5, samples)

    draw, level, onbeat, cues = [], [], [], []
    for t in ts:
        frame = player.frame(float(t))
        shown, rep = guard.apply(np.clip(frame, 0, 255), now=float(t), gain=player.gain)
        draw.append(rep["sent_ma"])
        level.append(music.level_at(float(t)) if music else 0.0)
        onbeat.append(music.beat_phase(float(t)) < 0.25 if music else False)
        c = player.cue_at(float(t))
        cues.append(c["preset"] if c else None)

    draw = np.array(draw, float)
    level = np.array(level, float)
    onbeat = np.array(onbeat, bool)

    out = {}
    if draw.std() > 1e-6 and level.std() > 1e-6:
        out["follow"] = float(np.corrcoef(draw, level)[0, 1])
    else:
        out["follow"] = float("nan")
    hi = float(np.percentile(draw, 95))
    lo = float(np.percentile(draw, 5))
    out["swing"] = (hi - lo) / hi if hi > 1e-6 else 0.0
    out["mean_ma"] = float(draw.mean())
    out["peak_ma"] = hi
    out["beat"] = beat_contrast(sh, music, helmet, guard_for)
    seen = [c for c in cues if c]
    out["presets"] = len(set(seen))
    changes = sum(1 for a, b in zip(seen, seen[1:]) if a != b)
    out["hold_s"] = dur / max(changes, 1)
    return out


def beat_contrast(show, music, helmet, guard_for, pairs=200):
    """How much brighter the helmet is on a beat than half a beat later.

    Paired, on purpose.  This used to compare every sample that fell
    near a beat with every one that did not, across the whole track --
    which mostly compared one section with another, so a drop that
    happened to land in the on-beat bucket moved it more than the pulse
    ever could, and it read 1.0 whatever the pulse did.  Each beat
    against the half-beat after it, through one guard in time order,
    leaves only what the beat itself does.
    """
    beats = np.asarray(getattr(music, "beats", []) if music else [], float)
    if len(beats) < 4:
        return float("nan")
    spb = float(np.median(np.diff(beats)))
    guard = guard_for()
    player = mau5show.Player(show, helmet=helmet, music=music)
    on, off = [], []
    for tb in beats[::max(1, len(beats) // pairs)]:
        for t, acc in ((tb + 0.02, on), (tb + 0.5 * spb, off)):
            frame = player.frame(float(t))
            _, rep = guard.apply(np.clip(frame, 0, 255), now=float(t), gain=player.gain)
            acc.append(rep["sent_ma"])
    return float(np.mean(on) / max(np.mean(off), 1e-6))


def line(name, s):
    return ("  %-30s follow %+.2f  swing %.2f  beat %.2f  "
            "%4.0f mA mean  %2d presets  %4.0fs each"
            % (name[:30], s["follow"], s["swing"], s["beat"],
               s["mean_ma"], s["presets"], s["hold_s"]))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("shows", nargs="*")
    ap.add_argument("--samples", type=int, default=500)
    ap.add_argument("--sweep", default=None,
                    help="a show parameter to try values of: dynamics, "
                         "dynamics_gamma, pulse")
    ap.add_argument("--values", default=None,
                    help="comma separated, for --sweep")
    a = ap.parse_args(argv)

    names = a.shows or sorted(f[:-5] for f in os.listdir(SHOWS)
                              if f.endswith(".json"))
    helmet = E.Helmet()
    guard_for = lambda: mau5power.load(count=helmet.n)

    print("follow: how the helmet's current tracks the track's loudness "
          "(-1..+1, want > +0.4)")
    print("swing:  how much of its own range the show uses (0..1)")
    print("beat:   current on a beat over current half a beat later, paired\n")

    base = {}
    for n in names:
        show, music = load_show(n)
        if music is None:
            print("  %-30s no analysis, skipped" % n[:30])
            continue
        s = score(show, music, helmet, guard_for, a.samples)
        base[n] = (show, music, s)
        print(line(n, s))

    if a.sweep:
        vals = ([float(v) for v in a.values.split(",")] if a.values
                else [0.0, 0.3, 0.5, 0.72, 0.85, 1.0])
        print("\n  sweeping %s" % a.sweep)
        for n, (show, music, _) in base.items():
            print("\n  %s" % n[:60])
            for v in vals:
                s = score(show, music, helmet, guard_for, a.samples,
                          override={a.sweep: v})
                print("    %-6s %s" % ("%.2f" % v, line("", s).strip()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
