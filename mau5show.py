#!/usr/bin/env python3
"""mau5show -- turn a track into a show, and play it.

Analysis comes from mau5song: an onset envelope, a tempo and beat grid
phase-locked to the downbeats, per-bar energy, and sections cut where
that energy changes.  This module decides what each section should
look like, and plays the result.

The choices are deliberately conservative.  A section gets a preset
from a pool matched to its energy band, held for the whole section so
the look has time to register, with the palette rotating per section so
successive sections differ.  Accents land on beats rather than on
frames, because a sweep that drifts half a beat out reads as sloppy
where the same sweep locked to the grid reads as deliberate.

    python3 mau5show.py build "deadmau5 - Strobe.mp3"
    python3 mau5show.py preview shows/strobe.json --seconds 40
    python3 mau5show.py play shows/strobe.json
"""

from __future__ import annotations

import argparse
import json
import math
import os
import random
import time
import zlib

import numpy as np

import mau5engine as E
import mau5song

HERE = os.path.dirname(os.path.abspath(__file__))
SHOWS = os.path.join(HERE, "shows")

# Preset pools by energy band.  Low sections stay sparse so the loud
# ones have somewhere to go.
POOLS = {
    0: [("breathe", {"period": 8.0}), ("twinkle", {}), ("ripple", {"period": 3.4}),
        ("tubepulse", {}), ("eyes", {}), ("gradient", {"period": 14.0}),
        ("heartbeat", {}), ("wave", {"period": 5.0, "length": 0.8})],
    1: [("scanner", {}), ("wipe", {}), ("comet", {"period": 4.0}),
        ("matrix", {}), ("earspin", {"period": 2.4}), ("chase", {"period": 2.2}),
        ("spiral", {"period": 6.0}), ("sparkle", {})],
    2: [("plasma", {}), ("rainbow", {"period": 6.0}), ("fire", {}),
        ("eq", {}), ("comet", {"period": 1.6}), ("vu", {}),
        ("split", {"shell": "plasma", "ears": "chase"}),
        ("wave", {"period": 1.6}), ("blades", {})],
    3: [("strobe", {"hz": 6.0}), ("eq", {}), ("fire", {"speed": 1.8}),
        ("rainbow", {"period": 2.5}), ("police", {}), ("lightning", {"every": 1.1}),
        ("pinwheel", {"period": 1.2}), ("confetti", {"rate": 26.0}),
        ("split", {"shell": "fire", "ears": "pinwheel"}), ("blades", {})],
}

PALETTES = [
    [(255, 40, 0), (255, 150, 0)],
    [(0, 180, 255), (120, 0, 255)],
    [(255, 0, 120), (255, 200, 0)],
    [(0, 255, 140), (0, 90, 255)],
    [(255, 255, 255), (0, 200, 255)],
]


def _cache_fits(z, cache, path):
    """Whether a cached analysis is of the track at `path`, and its stamp.

    It used to be trusted whenever the frame rate and version matched,
    so a track replaced under the same name -- a radio edit, a copy with
    different leading silence -- kept the old beat grid through every
    rebuild, and mau5drive shipped that grid on to the phone.

    With no track here the cache is all there is, and that is the
    designed case: the music is not distributed with the source.  A
    cache that carries a stamp of its audio is checked against it.  One
    written before stamps falls back to mau5song.decode's rule, a track
    newer than the cache, so the two caches at least agree.
    """
    if not path or not os.path.isfile(path):
        return True, None
    stamp = mau5song.track_stamp(path)
    have = str(z["src"]) if "src" in z else ""
    if have:
        return have == stamp, stamp
    return os.path.getmtime(path) <= os.path.getmtime(cache), stamp


class Music:
    """Per-frame curves the presets can ask about."""

    def __init__(self, path, fps=40, verbose=False, cache=None):
        self.path, self.fps = path, fps
        stamp = None
        if cache and os.path.exists(cache):
            z = np.load(cache)
            fits, stamp = _cache_fits(z, cache, path)
            if int(z["fps"]) == fps and int(z.get("v", 1)) >= CACHE_V and fits:
                self.duration = float(z["duration"]); self.bpm = float(z["bpm"])
                self.beats = z["beats"]; self.bars = z["bars"]
                self.levels = z["levels"]; self.energy = z["energy"]
                self.onset = z["onset"]
                self.sections = [tuple(int(v) for v in r) for r in z["sections"]]
                self.lock_conf = float(z["lock"]) if "lock" in z else float("nan")
                self.band = {k: (z["b_%s_e" % k], z["b_%s_p" % k])
                             for k, _, _ in mau5song.BANDS}
                self.chroma = z["chroma"]
                # Not the cached labels: those came from one 25 ms sample
                # per bar (see _bar_levels).  The energy curve and the
                # bars are cached, so the labels are made again from
                # them, and a machine without the audio gets the same.
                self.shape = mau5song.shape_of(self._bar_levels())
                self.bands = True
                return
            if not fits:
                print("  %s has changed since it was analysed: analysing it "
                      "again, and its show wants rebuilding"
                      % os.path.basename(path))
        an = mau5song.analyse(path, verbose=verbose)
        self.duration = an["duration"]
        self.bpm = an["bpm"]
        self.beats = an["beats"]
        self.bars = an["bars"]
        self.levels = an["levels"]
        self.energy, self.onset = mau5song.frame_curves(
            an["audio"], an["sr"], an["env"], an["env_fps"], an["env_t0"],
            fps, self.duration)
        secs = mau5song.sections(self.levels)
        self.sections = mau5song.split_long(secs)
        # How well the tempo estimate actually locked onto the track.
        # Beat-locking an effect to a grid that is only approximately
        # where the beats are is worse than letting it run free: the
        # effect then lands wrong on purpose rather than at random.
        self.lock_conf = float(an.get("lock", float("nan")))
        self.band = mau5song.band_curves(an["audio"], an["sr"], fps, self.duration)
        self.chroma = mau5song.chroma(an["audio"], an["sr"], self.bars)
        self.shape = mau5song.shape_of(self._bar_levels())
        self.bands = True                      # Equaliser may ask for bands
        if cache:
            # `src` says which audio this is an analysis of, so a track
            # replaced under the same name is analysed again instead of
            # being handed somebody else's beat grid.
            np.savez_compressed(
                cache, fps=fps, duration=self.duration, bpm=self.bpm,
                beats=self.beats, bars=self.bars, levels=self.levels,
                energy=self.energy, onset=self.onset,
                sections=np.array(self.sections, int),
                lock=self.lock_conf, v=CACHE_V, chroma=self.chroma,
                shape=np.array(self.shape, dtype="U6"),
                src=np.array(stamp or mau5song.track_stamp(path) or ""),
                **{("b_%s_%s" % (k, w)): self.band[k][i]
                   for k, _, _ in mau5song.BANDS
                   for i, w in ((0, "e"), (1, "p"))})

    def _bar_levels(self):
        """How loud each bar is on average, which is what shape_of reads.

        This was level_at at each downbeat: one 25 ms frame standing in
        for a whole bar, so a missing kick or a fill on the one read as
        a jump or a collapse.  Measured over the shipped analyses that
        found 11 drops in Fred again where the bar means find 1, and 4
        in Strobe (bars 13, 61, 93, 218) where the bar means find 217 --
        and bar 13 put an 8 Hz white strobe over Strobe's soft intro.
        """
        e = np.clip(np.asarray(self.energy, float), 0, 1)
        n, nb = len(e), len(self.bars)
        if not n or not nb:
            return np.zeros(nb)
        edges = [int(float(t) * self.fps) for t in self.bars]
        edges.append(int(self.duration * self.fps))
        out = np.zeros(nb)
        for i in range(nb):
            a = min(max(edges[i], 0), n - 1)
            b = min(max(edges[i + 1], a + 1), n)
            out[i] = float(e[a:b].mean())
        return out

    def band_at(self, t, name="bass", punch=False):
        """0..1 for one band at one instant: loudness, or its punch."""
        b = getattr(self, "band", None)
        if not b or name not in b:
            return self.level_at(t)
        arr = b[name][1 if punch else 0]
        i = int(t * self.fps)
        if i < 0 or i >= len(arr):
            return 0.0
        return float(arr[i])

    def bar_shape(self, t):
        """'build' | 'drop' | 'fall' | 'steady' for the bar containing t."""
        sh = getattr(self, "shape", None)
        if not sh or not len(self.bars):
            return "steady"
        i = int(np.searchsorted(self.bars, t) - 1)
        return sh[i] if 0 <= i < len(sh) else "steady"

    def beat_index(self, t):
        """Continuous position on the beat grid, fractional beats.

        Interpolated between measured beats rather than computed from
        the tempo, so it follows a track that drifts instead of walking
        away from it over four minutes.
        """
        b = self.beats
        if len(b) < 2:
            return float(t * self.bpm / 60.0)
        i = int(np.searchsorted(b, t) - 1)
        if i < 0:
            return float((t - b[0]) / max(b[1] - b[0], 1e-6))
        if i + 1 >= len(b):
            spb = max(b[-1] - b[-2], 1e-6)
            return float(len(b) - 1 + (t - b[-1]) / spb)
        return float(i + (t - b[i]) / max(b[i + 1] - b[i], 1e-6))

    def beat_phase(self, t):
        """0 at a beat, rising to 1 just before the next one."""
        b = self.beats
        if len(b) < 2:
            return 0.0
        i = int(np.searchsorted(b, t) - 1)
        if i < 0 or i + 1 >= len(b):
            return 0.0
        return float((t - b[i]) / max(b[i + 1] - b[i], 1e-6))

    def is_downbeat(self, t, window=0.08):
        d = self.bars
        if not len(d):
            return False
        i = int(np.searchsorted(d, t + window) - 1)
        return bool(0 <= i < len(d) and abs(t - d[i]) < window)

    def level_at(self, t):
        i = int(t * self.fps)
        if i < 0 or i >= len(self.energy):
            return 0.0
        return float(np.clip(self.energy[i], 0, 1))

    def pitch_at(self, t):
        """Where the harmony sits, as a hue in 0..1.  One turn is one
        octave, so the colour follows the chords and ignores the
        bassline walking between octaves.

        A circular mean of the bar's pitch-class profile rather than
        its loudest bin: a track sitting between two neighbouring
        classes should give a colour between them, not flap.
        """
        ch = getattr(self, "chroma", None)
        if ch is None or not len(ch) or not len(self.bars):
            return 0.0
        i = int(np.clip(np.searchsorted(self.bars, t) - 1, 0, len(ch) - 1))
        a = 2 * np.pi * np.arange(12) / 12.0
        v = np.asarray(ch[i], float)
        return float((math.atan2(float((v * np.sin(a)).sum()),
                                 float((v * np.cos(a)).sum()))
                      / (2 * np.pi)) % 1.0)

    def centroid_at(self, t):
        """Spectral brightness in 0..1: 0 is all bass, 1 is all air."""
        b = getattr(self, "band", None)
        if not b:
            return 0.5
        lo = self.band_at(t, "bass")
        mid = self.band_at(t, "mid")
        hi = self.band_at(t, "high")
        tot = lo + mid + hi
        return float(np.clip((0.5 * mid + hi) / tot, 0, 1)) if tot > 1e-6 else 0.5

    def bands_at(self, t, n):
        """Cheap pseudo-spectrum: the energy curve smeared across bands
        with a per-band lag, which looks like a spectrum analyser
        without pretending to be one."""
        i = int(t * self.fps)
        out = np.zeros(n)
        for b in range(n):
            j = max(0, i - b * 2)
            v = self.energy[j] if j < len(self.energy) else 0.0
            out[b] = float(np.clip(v * (1.15 - 0.5 * b / n), 0, 1))
        return out


# How long one idea should last, in bars, by how busy the section is.
# The old builder held a single effect for a whole section -- often
# forty seconds -- which is the main reason the shows looked
# repetitive.  A phrase is the unit a listener already hears.
PHRASE_BARS = {0: 16, 1: 8, 2: 8, 3: 4}

# Effects that suit a particular moment, over and above the level
# pools.  A build wants something that travels, a drop wants impact,
# a fall wants something that decays.
SHAPE_POOLS = {
    "build": [("scanner", {"bounce": False}), ("wipe", {}), ("comet", {}),
              ("chase", {}), ("matrix", {})],
    "drop":  [("strobe", {"hz": 8.0}), ("lightning", {"every": 0.8}),
              ("police", {}), ("eq", {}), ("beatpulse", {}), ("fire", {}),
              ("blades", {})],
    "fall":  [("breathe", {}), ("ripple", {}), ("twinkle", {}),
              ("gradient", {}), ("tubepulse", {})],
}

# Second layers, each riding a frequency band.  Sparse and fast, so
# they add detail without becoming the picture.
OVERLAYS = {
    "high": [("sparkle", {"density": 0.10}), ("twinkle", {"density": 0.08}),
             ("confetti", {"rate": 9.0})],
    "bass": [("beatpulse", {"floor": 0.0}), ("tubepulse", {})],
    "mid":  [("eq", {}), ("vu", {})],
}


_HELMET = None


def _H():
    global _HELMET
    if _HELMET is None:
        _HELMET = E.Helmet()
    return _HELMET


def _phrases(m):
    """Split the track into musical phrases with a level and a shape.

    Sections give the arrangement; phrases give something to change on.
    A phrase inherits its section's level and takes the strongest
    shape any of its bars carried, so a build or a drop inside a long
    section is not averaged away.
    """
    out = []
    nb = len(m.bars)
    for b0, b1, lvl in m.sections:
        step = PHRASE_BARS[int(np.clip(lvl, 0, 3))]
        b = b0
        while b < b1:
            e = min(b + step, b1)
            if b1 - e < step // 2:            # absorb a stub rather than keep it
                e = b1
            shapes = [m.shape[i] for i in range(b, min(e, len(m.shape)))]
            shape = "steady"
            for want in ("drop", "build", "fall"):
                if want in shapes:
                    shape = want
                    break
            t0 = float(m.bars[b]) if b < nb else 0.0
            t1 = float(m.bars[e]) if e < nb else m.duration
            if t1 > t0:
                out.append({"b0": b, "b1": e, "level": int(np.clip(lvl, 0, 3)),
                            "shape": shape, "t0": t0, "t1": t1})
            b = e
    return out


def _palette_regions(m, thresh=0.80):
    """Bar -> palette index, changing only where the harmony moves.

    Cycling the palette every section is arbitrary and looks it.
    Changing it when the chord content actually shifts makes the
    colour feel like it belongs to the music rather than to a counter.
    """
    ch = getattr(m, "chroma", None)
    n = len(m.bars)
    if ch is None or len(ch) < 2:
        return [0] * n
    d = np.linalg.norm(np.diff(ch, axis=0), axis=1)
    cut = np.percentile(d, thresh * 100)
    region, out = 0, [0]
    run = 0
    for i in range(1, len(ch)):
        run += 1
        if d[i - 1] > cut and run >= 8:       # not every bar, please
            region += 1
            run = 0
        out.append(region)
    out += [out[-1]] * (n - len(out))
    return [r % len(PALETTES) for r in out[:n]]


def _pick(pool, recent, rng, bias=None):
    """Choose from a pool, avoiding what was just used."""
    best, best_s = None, -1e9
    for i, (name, kw) in enumerate(pool):
        score = rng.random()
        if name in recent:
            score -= 2.0 + 0.5 * (len(recent) - recent.index(name))
        if bias and name in bias:
            score += 1.5
        if score > best_s:
            best, best_s = (name, kw), score
    return best


def _musical_params(name, kw, m, phrase):
    """Give a periodic effect a period that is a whole number of bars.

    Beat-locking already snaps the phase, but it can only snap to what
    it is given: a preset whose period is a strange number of beats
    gets quantised hard and loses its character.  Handing it a musical
    period in the first place means the lock has nothing to correct.
    """
    kw = dict(kw)
    spb = 60.0 / max(m.bpm, 1e-6)
    bar = spb * 4.0
    cls = E.REGISTRY[name]
    lvl = phrase["level"]
    if name == "blades" and "period" not in kw:
        kw["period"] = round(bar, 3)         # a tube a beat, whatever the level
    if "period" in cls.params and "period" not in kw:
        bars = {0: 4.0, 1: 2.0, 2: 1.0, 3: 0.5}[lvl]
        if phrase["shape"] == "build":
            bars = max(0.25, bars / 2.0)
        kw["period"] = round(bar * bars, 3)
    if "hz" in cls.params and "hz" not in kw:
        kw["hz"] = round(1.0 / (spb / {0: 1, 1: 1, 2: 2, 3: 4}[lvl]), 3)
    if "bpm" in cls.params and "bpm" not in kw:
        kw["bpm"] = round(m.bpm, 2)
    if "every" in cls.params and "every" not in kw:
        kw["every"] = round(bar / 2.0, 3)
    return kw


# What a phrase should average, on a 0-255 scale, by how busy it is.
# Effects differ by a factor of sixty in how much of the helmet they
# fill -- lightning averages 2, plasma averages 134 -- so without this
# the brightest thing on the helmet is whichever effect happened to be
# chosen, and the music barely shows through at all.  Normalising each
# cue to a target lets level, dynamics and the beat do the work.
CUE_TARGET = {0: 18.0, 1: 32.0, 2: 55.0, 3: 80.0}
SHAPE_GAIN = {"drop": 1.3, "build": 1.0, "fall": 0.8, "steady": 1.0}


def cue_gain(h, name, params, overlay, level, shape, samples=24, period=4.0):
    """A per-cue multiplier that evens out how much effects fill.

    Measured over a spread of times rather than one frame, because a
    strobe is dark for most of its cycle and would otherwise be scaled
    to the moon.  Clamped, because an effect that lights four LEDs
    should stay an effect that lights four LEDs.
    """
    try:
        pre = E.make(name, **{k: (tuple(v) if isinstance(v, list) else v)
                              for k, v in params.items()})
    except Exception:
        return 1.0
    vals = [float(np.clip(pre.render(h, period * i / samples, None), 0, 255).mean())
            for i in range(samples)]
    mean = float(np.mean(vals))
    if overlay:
        mean += 0.5 * cue_mean(h, overlay["preset"], overlay.get("params", {}),
                               samples, period) * float(overlay.get("gain", 1.0))
    want = CUE_TARGET[int(np.clip(level, 0, 3))] * SHAPE_GAIN.get(shape, 1.0)
    if mean < 0.5:
        return 1.0
    return round(float(np.clip(want / mean, 0.2, 5.0)), 3)


def cue_mean(h, name, params, samples=24, period=4.0):
    try:
        pre = E.make(name, **{k: (tuple(v) if isinstance(v, list) else v)
                              for k, v in params.items()})
    except Exception:
        return 0.0
    return float(np.mean([
        float(np.clip(pre.render(h, period * i / samples, None), 0, 255).mean())
        for i in range(samples)]))


def build(track, fps=40, out=None, seed=None, verbose=False):
    """Turn a track into a show, phrase by phrase.

    Three things the previous version did not do.  It changes on
    phrases rather than sections, so one idea lasts eight bars instead
    of forty seconds.  It knows where the builds and the drops are and
    answers them, rather than changing effect on a section boundary
    that lands near a drop but not on it.  And it layers: a second,
    sparse effect rides a frequency band over the top, so the hats can
    glitter over a slow swell.
    """
    os.makedirs(SHOWS, exist_ok=True)
    base = os.path.splitext(os.path.basename(track))[0]
    m = Music(track, fps=fps, cache=os.path.join(SHOWS, base + ".analysis.npz"))
    # A stable seed from the name.  This was hash(), which Python salts
    # afresh in every process, so rebuilding a show gave a different show
    # each time and no tuning could be repeated.
    rng = random.Random(seed if seed is not None else zlib.crc32(base.encode()))
    pal_of = _palette_regions(m)
    phrases = _phrases(m)
    recent, cues = [], []

    for ph in phrases:
        lvl, shape = ph["level"], ph["shape"]
        pool = list(POOLS[lvl])
        bias = [n for n, _ in SHAPE_POOLS.get(shape, [])]
        if shape in SHAPE_POOLS:
            pool = pool + SHAPE_POOLS[shape]
        name, kw = _pick(pool, recent, rng, bias=bias)
        recent = ([name] + recent)[:5]

        pal = PALETTES[pal_of[min(ph["b0"], len(pal_of) - 1)]]
        kw = _musical_params(name, kw, m, ph)
        cls = E.REGISTRY[name]
        if "color" in cls.params and "color" not in kw:
            kw["color"] = pal[0]
        if "a" in cls.params and "b" in cls.params:
            kw.setdefault("a", pal[0]); kw.setdefault("b", pal[1])

        cue = {"start": round(ph["t0"], 3), "end": round(ph["t1"], 3),
               "preset": name, "params": kw, "level": lvl, "shape": shape}

        # A second layer wherever there is room for one.  Not on the
        # quietest phrases: a breakdown earns its space.
        if lvl >= 2 or shape == "drop":
            band = "high" if lvl >= 2 else "bass"
            if shape == "drop":
                band = "bass"
            oname, okw = _pick(OVERLAYS[band], recent[:2], rng)
            if oname != name:
                okw = dict(okw)
                ocls = E.REGISTRY[oname]
                if "color" in ocls.params:
                    okw["color"] = pal[1]
                cue["overlay"] = {"preset": oname, "params": okw, "band": band,
                                  "gain": 0.9 if shape == "drop" else 0.7,
                                  "floor": 0.1, "mix": "add"}
        cue["gain"] = cue_gain(_H(), name, kw, cue.get("overlay"),
                               lvl, shape, period=4 * 60.0 / max(m.bpm, 1e-6))
        cues.append(cue)

    # Whether to pin effects to the beat grid, decided here as Player
    # decides it and written down for the phone.  Player reads the
    # confidence off the analysis; the phone gets only the cue list and
    # a drive file with the grid in it, so without this every show ran
    # free there while four of the five lock on the laptop.
    conf = float(getattr(m, "lock_conf", float("nan")))
    show = {"track": os.path.basename(track), "fps": fps,
            "duration": round(m.duration, 2), "bpm": round(m.bpm, 2),
            "beats": len(m.beats), "analysis": base + ".analysis.npz",
            "fade": 0.45, "accent": True, "pulse": 0.40,
            "lock": bool(conf == conf and conf >= LOCK_MIN), "cues": cues}
    out = out or os.path.join(SHOWS, base + ".json")
    json.dump(show, open(out, "w"), indent=1)
    if verbose:
        import collections
        print("  %d phrases, %d distinct effects, %d with an overlay"
              % (len(cues), len({c["preset"] for c in cues}),
                 sum(1 for c in cues if c.get("overlay"))))
        print("  shapes:", dict(collections.Counter(c["shape"] for c in cues)))
    return show, out


# Below this the tempo estimate is not trustworthy enough to pin
# effects to: a grid that is only approximately where the beats are
# makes an effect land wrong on purpose rather than at random.
#
# Measured over the five built shows.  Locking moved the big visual
# events on to the beat by +26, +37, +32 and +69 percent for the four
# tracks scoring 0.246 and above, and by -28 percent for the one
# scoring 0.119.  The threshold sits in the gap.  Five tracks is not
# many, so this is a sensible place to start rather than a constant
# anyone should trust to three figures.
LOCK_MIN = 0.18

# Bump when the analysis gains a field, so old caches are rebuilt
# rather than loaded with half the curves missing.
CACHE_V = 2

# How long the beat pulse holds its peak before it decays, in seconds.
#
# The pulse used to be (1 - 3 * phase)^2: a third of a beat, 115 ms at
# 174 bpm.  The laptop samples that three or four times at 40 fps; the
# phone, paced by the controller, sends a frame every 36-70 ms at
# irregular times, so whether a frame landed near the beat was luck.
# Simulated on Strobe (Dimension Remix) with frames at 55 +- 15 ms, the
# per-beat peak spread 0.80-0.92 against 0.90-0.98 on the laptop, and
# the pulse was most of the frame-to-frame change on the whole helmet
# -- 7.9 % per frame through the plasma cue, 0.6 % with no pulse.  Held
# for longer than the slowest frame gap, every beat has a frame at its
# full height on either device, and the same curve as before decays
# after it.
PULSE_HOLD_S = 0.07

# The downbeat accent: how much white it adds at most, and how long
# is_downbeat says yes after a bar -- the accent's whole life.
ACCENT_PEAK = 0.45
ACCENT_WINDOW_S = 0.08


def beat_gain(ph, bpm, amp):
    """The beat pulse at beat phase `ph`: at most 1, applied after the guard.

    The peak is held for PULSE_HOLD_S and then decays as the old curve
    did, over a third of a beat.  A longer flash alone would spend more
    current -- a beat would average brighter than it did -- so the floor
    between beats is set to keep the mean over a beat exactly what the
    old curve gave, (1 + amp/9) / (1 + amp).  Same current over a song,
    same peak, which is the guarded frame itself; only the gaps between
    beats are a little darker, and that is the contrast the pulse is
    for.  If a show ever asks for a pulse so deep that no floor can keep
    that mean, the whole curve is scaled down instead, never up.
    """
    spb = 60.0 / max(float(bpm or 0.0), 1e-6)
    hold = min(PULSE_HOLD_S / spb, 0.25)            # in beats
    x = max(0.0, ph - hold)
    k = max(0.0, 1.0 - x * 3.0) ** 2
    mean0 = (1.0 + amp / 9.0) / (1.0 + amp)         # the old curve's mean
    area = hold + 1.0 / 9.0                         # this one's, of k
    floor = (mean0 - area) / (1.0 - area)
    if floor >= 0.0:
        return floor + (1.0 - floor) * k
    return k * mean0 / area


def accent_level(bpm):
    """How much white the downbeat accent adds, flat across its window.

    It was 0.45 * (1 - 6 * phase): a sixth of a beat, 57-80 ms, which
    the phone caught at a random strength or skipped.  Flat across the
    80 ms that is_downbeat allows, any frame gap shorter than that sees
    it, always at the same strength -- and that strength is chosen so
    the accent adds the same light in total as the old ramp did, which
    makes it about half as tall (0.22 at 128 bpm, 0.16 at 174).
    """
    spb = 60.0 / max(float(bpm or 0.0), 1e-6)
    win = ACCENT_WINDOW_S / spb                     # in beats
    m = min(win, 1.0 / 6.0)                         # where the old ramp ran
    return ACCENT_PEAK * (m - 3.0 * m * m) / win


class Player:
    """Walks a show's cues and renders frames.

    Two things happen on top of simply picking the cue for the moment.

    Cues crossfade rather than cut.  A hard switch between two full-face
    effects reads as a glitch -- the eye sees the discontinuity before
    it sees the new effect -- whereas half a second of overlap reads as
    intent.  The fade is short enough not to muddy a drop.

    And on loud sections a downbeat accent is layered over the top,
    locked to the bar grid rather than to a timer.  Half a beat of drift
    is the difference between a show that looks choreographed and one
    that looks like it is running nearby.
    """

    def __init__(self, show, helmet=None, music=None):
        self.show = show
        self.h = helmet or E.Helmet()
        self.music = music
        self.fade = float(show.get("fade", 0.0))
        self.accent = bool(show.get("accent", False))
        # How hard every beat is marked, 0..1, over and above the
        # downbeat flash.  A show that only answers the downbeat moves
        # once a bar and reads as slow; a little lift on each beat is
        # what makes it look driven by the track rather than beside it.
        self.pulse = float(show.get("pulse", 0.22))
        self.gain = 1.0                 # the beat pulse; see frame()
        # How far the whole picture drops in the quiet parts.  Without
        # this a show runs at one level from end to end and the only
        # thing that changes is which effect is on screen, which is
        # why it reads as pasted over the track rather than driven by
        # it.  Measured on Strobe, brightness correlated -0.34 with the
        # music before and +0.24 with this alone -- the sign was wrong,
        # the loud effects having landed in the quiet sections.  The
        # rest of the gap is cue_gain below: how much of the helmet an
        # effect fills swamps how bright the music is.
        #
        # It also costs nothing.  The guard clamps the top anyway, so
        # lowering the floor buys contrast and spends less power.
        self.dyn = float(show.get("dynamics", 0.72))
        self.dyn_gamma = float(show.get("dynamics_gamma", 0.7))
        # Lock when the analysis found the beat, unless the show says
        # not to.  build() writes the same verdict into the show as
        # `lock`, for the phone, which has the grid but not the
        # confidence -- so here `lock: true` is a record, not an order:
        # it cannot make a grid confident that is not.  It used to be
        # an order, back when no show carried it.
        want = show.get("lock")
        conf = getattr(music, "lock_conf", float("nan")) if music is not None else 0.0
        self.lock = (conf == conf and conf >= LOCK_MIN) and want is not False
        self._cache = {}
        self._cues = sorted(show["cues"], key=lambda c: c["start"])

    def _preset(self, cue):
        key = (cue["preset"], json.dumps(cue["params"], sort_keys=True))
        if key not in self._cache:
            self._cache[key] = E.make(cue["preset"], **{
                k: (tuple(v) if isinstance(v, list) else v)
                for k, v in cue["params"].items()})
        return self._cache[key]

    def cue_at(self, t):
        for c in self._cues:
            if c["start"] <= t < c["end"]:
                return c
        return None

    def preset_at(self, t):
        c = self.cue_at(t)
        return self._preset(c) if c else None

    def _one(self, name, params, t):
        key = (name, json.dumps(params, sort_keys=True))
        if key not in self._cache:
            self._cache[key] = E.make(name, **{
                k: (tuple(v) if isinstance(v, list) else v)
                for k, v in params.items()})
        pre = self._cache[key]
        te = t
        if self.lock and self.music is not None:
            te, _ = E.lock_time(self.music, name, params, t)
        return pre.render(self.h, te, self.music)

    def _render(self, cue, t):
        """One cue at time t: its base effect, plus any overlay.

        A cue used to be a single effect held for a whole section, and
        that is most of why the old shows looked repetitive -- forty
        seconds of one idea, then a hard switch to another.  An overlay
        is a second effect composited on top, usually something sparse
        and fast riding a frequency band, so the hats can glitter over
        a slow swell without either of them having to be the whole
        picture.
        """
        out = self._one(cue["preset"], cue.get("params", {}), t)
        g = float(cue.get("gain", 1.0))
        if g != 1.0:
            out = out * g
        ov = cue.get("overlay")
        if not ov:
            return out
        gain = float(ov.get("gain", 1.0))
        band = ov.get("band")
        if band and self.music is not None:
            drive = self.music.band_at(t, band, punch=bool(ov.get("punch", True)))
            gain *= float(ov.get("floor", 0.15)) + (1.0 - float(ov.get("floor", 0.15))) * drive
        lay = self._one(ov["preset"], ov.get("params", {}), t) * gain
        if ov.get("mix", "add") == "over":
            m = lay.max(1) > 4
            out = out.copy(); out[m] = lay[m]
            return out
        return np.maximum(out, lay) if ov.get("mix") == "max" else out + lay

    def frame(self, t):
        self.gain = 1.0
        cur = self.cue_at(t)
        if cur is None:
            return np.zeros((self.h.n, 3))
        out = self._render(cur, t)

        if self.fade > 0:
            into = t - cur["start"]
            if into < self.fade:
                i = self._cues.index(cur)
                if i > 0:
                    prev = self._cues[i - 1]
                    k = into / self.fade
                    out = k * out + (1 - k) * self._render(prev, t)

        if self.music is not None:
            lvl = cur.get("level", 0)
            ph = self.music.beat_phase(t)
            if self.dyn > 0:
                # bass and overall together: a breakdown with a loud pad
                # should not read as loud as a drop with a kick under it
                e = (0.6 * self.music.band_at(t, "bass")
                     + 0.4 * self.music.level_at(t))
                k = (1.0 - self.dyn) + self.dyn * float(e) ** self.dyn_gamma
                out = out * k
            # A pulse on every beat, scaled by how loud the section is --
            # a breakdown should breathe, a drop should hit.  It is not
            # applied here.  Multiplied into the frame it was exactly
            # what the power guard exists to take away again -- the
            # per-LED ceilings and the governor flatten anything loud --
            # and the shows measured 1.00-1.06 on-beat over half a beat
            # later.  So the frame is left as written and the pulse is
            # handed over as `gain`, at most 1, for whoever sends the
            # frame to apply after the guard: the beat is the frame at
            # its limit and the gaps between are dimmer.
            #
            # Its shape is beat_gain's: held long enough that the phone,
            # sending a frame every 36-70 ms, still sees every beat.
            self.gain = 1.0
            bpm = getattr(self.music, "bpm", 0.0)
            if self.pulse > 0 and lvl >= 1:
                self.gain = beat_gain(ph, bpm, self.pulse * (0.4 + 0.3 * lvl))
            # ph < 0.5: is_downbeat is true either side of the bar, and
            # the flash belongs after it
            if (self.accent and lvl >= 2 and ph < 0.5
                    and self.music.is_downbeat(t)):
                k = accent_level(bpm)
                if k > 0:
                    out = out + k * 255.0
        return np.clip(out, 0, 255)


def _music_for(show, track):
    """Load a show's analysis, from its cache when there is one.

    The cache holds the whole beat grid -- tempo, beats, bars, levels,
    sections -- in about a hundred kilobytes, and Music reads it without
    opening the audio at all.  So a cached show still knows where its
    downbeats are on a machine that has no copy of the track, which is
    every machine but the one the show was built on: the music is not
    distributed with the source.  Only an uncached show needs the file.
    """
    cache = show.get("analysis")
    cache = os.path.join(SHOWS, cache) if cache else None
    if cache and os.path.exists(cache):
        return Music(track, fps=show.get("fps", 40), cache=cache)
    if not os.path.exists(track):
        return None
    return Music(track, fps=show.get("fps", 40), cache=cache)


def mmss(t):
    return "%d:%05.2f" % (int(t) // 60, t % 60)


def preview(show_path, seconds=None, fps=24, out=None, with_audio=True,
            start=0.0):
    """Render the show to an mp4, with the track muxed back in."""
    import subprocess, tempfile
    import mau5preview as PV
    show = json.load(open(show_path))
    track = os.path.join(HERE, show["track"])
    music = _music_for(show, track)
    pl = Player(show, music=music)
    sc = PV.Scene(pl.h)
    dur = min(seconds or show["duration"], show["duration"] - start)
    tmp = tempfile.mkdtemp(prefix="mau5show")
    n = int(dur * fps)
    for i in range(n):
        f = pl.frame(start + i / fps)
        sc.frame(f * pl.gain).save(os.path.join(tmp, "f%05d.png" % i))
    out = out or os.path.splitext(show_path)[0] + "_preview.mp4"
    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
           "-framerate", str(fps), "-i", os.path.join(tmp, "f%05d.png")]
    if with_audio and os.path.exists(track):
        cmd += ["-ss", "%.3f" % start, "-i", track, "-t", "%.3f" % dur,
                "-c:a", "aac", "-b:a", "128k", "-shortest"]
    cmd += ["-vf", "format=yuv420p", "-c:v", "libx264", "-crf", "20", out]
    subprocess.run(cmd, check=True)
    for f in os.listdir(tmp):
        os.remove(os.path.join(tmp, f))
    os.rmdir(tmp)
    return out, n


def play(show_path, host=None, seconds=None, fps=40, audio=True, verbose=True,
         av_offset=0.0):
    """Stream the show to the helmet, with the track playing locally.

    Audio is started first and the frame clock is slaved to wall time
    rather than to a frame counter, so a slow frame costs a dropped
    frame instead of silently sliding the whole show late.

    The clock starts when the player is spawned, and the player still
    has to start up, open and decode the mp3 and open the audio device
    before anything is heard -- a tenth to a third of a second, a
    quarter to a half of a beat at these tempos, with the lights ahead
    of the music by all of it.  Nothing reports when the sound actually
    starts, so `av_offset` is that delay, measured once (raise it until
    the downbeat flash lands on the kick) and held back from the light
    clock.  0 is the old behaviour.
    """
    import subprocess
    import mau5wled
    show = json.load(open(show_path))
    track = os.path.join(HERE, show["track"])
    music = _music_for(show, track)
    pl = Player(show, music=music)

    w = mau5wled.find_one(host)
    if verbose:
        print(w.describe())
    w.realtime(True, brightness=255)
    pix = mau5wled.Pixels(w, w.count or 622)
    if pix.guard is None:
        raise SystemExit("refusing to play with no power profile -- this "
                         "helmet overheats.  data/cal/power.json is missing.")
    dur = min(seconds or show["duration"], show["duration"])

    proc = None
    if audio and os.path.exists(track):
        player = "afplay" if os.path.exists("/usr/bin/afplay") else "ffplay"
        cmd = ([player, track] if player == "afplay"
               else [player, "-nodisp", "-autoexit", "-loglevel", "quiet", track])
        proc = subprocess.Popen(cmd)

    t0 = time.monotonic()
    # only when there is sound to wait for; before it, t < 0 has no cue
    # and renders black
    lag = float(av_offset) if proc else 0.0
    nframes = dropped = 0
    try:
        while True:
            t = time.monotonic() - t0 - lag
            if t >= dur:
                break
            f = pl.frame(t)
            pix.send(f, gain=pl.gain)
            nframes += 1
            nxt = t0 + (nframes / fps)
            slack = nxt - time.monotonic()
            if slack > 0:
                time.sleep(slack)
            else:
                dropped += 1
    except KeyboardInterrupt:
        pass
    finally:
        if proc:
            proc.terminate()
        for _ in range(4):
            pix.clear(); time.sleep(0.05)
    if verbose:
        print("played %.1fs, %d frames, %d late (%.1f%%)"
              % (dur, nframes, dropped, 100.0 * dropped / max(nframes, 1)))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter,
                                 epilog=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build"); b.add_argument("track", nargs="+")
    b.add_argument("--fps", type=int, default=40)
    p = sub.add_parser("preview"); p.add_argument("show")
    p.add_argument("--seconds", type=float); p.add_argument("--fps", type=int, default=24)
    p.add_argument("--out"); p.add_argument("--no-audio", action="store_true")
    p.add_argument("--start", type=float, default=0.0)
    y = sub.add_parser("play"); y.add_argument("show")
    y.add_argument("--host"); y.add_argument("--seconds", type=float)
    y.add_argument("--fps", type=int, default=40); y.add_argument("--no-audio", action="store_true")
    y.add_argument("--av-offset", type=float, default=0.0, metavar="SECONDS",
                   help="how long the audio player takes to start sounding; "
                        "the lights wait that long (measure once: raise it "
                        "until the downbeat flash lands on the kick)")
    sub.add_parser("list")
    a = ap.parse_args(argv)

    if a.cmd == "build":
        for t in a.track:
            show, out = build(t, fps=a.fps)
            print("\n%s  ->  %s" % (show["track"], out))
            print("  %.1f s, %.1f bpm, %d cues" % (show["duration"], show["bpm"], len(show["cues"])))
            for c in show["cues"]:
                print("    %s-%s  lvl%d  %-10s %s"
                      % (mmss(c["start"]), mmss(c["end"]), c["level"],
                         c["preset"], {k: v for k, v in c["params"].items() if k != "color"}))
    elif a.cmd == "preview":
        out, n = preview(a.show, a.seconds, a.fps, a.out, not a.no_audio, a.start)
        print("wrote %s (%d frames)" % (out, n))
    elif a.cmd == "play":
        play(a.show, a.host, a.seconds, a.fps, not a.no_audio,
             av_offset=a.av_offset)
    elif a.cmd == "list":
        for f in sorted(os.listdir(SHOWS)):
            if f.endswith(".json"):
                s = json.load(open(os.path.join(SHOWS, f)))
                print("  %-34s %6.1fs  %5.1f bpm  %2d cues"
                      % (f, s["duration"], s["bpm"], len(s["cues"])))


if __name__ == "__main__":
    main()
