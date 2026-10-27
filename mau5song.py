#!/usr/bin/env python3
"""mau5song -- listen to a track and build a full-length show for it.

    ./mau5song.py "deadmau5 - Strobe.mp3"
    ./mau5song.py *.mp3 --preview            # build, then open the simulator
    ./mau5song.py track.mp3 --bpm 128 --offset 0.32   # override the analysis

It decodes the audio, finds the tempo and the downbeat, measures how loud each
bar is, and turns that into a `mau5fx.Timeline`: quiet bars get a slow swell,
builds get rising pulses, drops get the face and the blades on every beat.
Then it hands the result to `mau5build`, so you end up with the same three
files any other show produces -- `shows/<name>.fseq`, the media, and the FPP
playlist.

The beat grid is written to `shows/<name>.beats`, one time per line. That file
is what the show is cued from, so if the analysis gets a track wrong you can
edit it (or tap one out by hand) and re-run with `--beats`.

Analysis is offline and needs no extra packages: decoding shells out to
`afconvert` (macOS) or `ffmpeg`, and the rest is numpy. Nothing here runs at
showtime.
"""

from __future__ import annotations

import argparse
import math
import os
import shutil
import subprocess
import sys
import wave

import numpy as np

import mau5build
import mau5cfg
import mau5fx

HOP, N_FFT = 256, 1024

# Residual lateness of the spectral-flux peak after the window-centre
# correction, measured from synthetic click tracks (see onset_envelope).
# Positive moves the detected beat later, towards the real kick.
ONSET_BIAS_S = 0.0133


# --------------------------------------------------------------------------
# decode + analyse
# --------------------------------------------------------------------------
def decode(path, rate=22050, cache_dir=None):
    """mp3/m4a/whatever -> a mono wav we can read with the stdlib."""
    if path.lower().endswith(".wav"):
        return path
    cache_dir = cache_dir or os.path.join(os.path.dirname(os.path.abspath(path)),
                                          ".mau5cache")
    os.makedirs(cache_dir, exist_ok=True)
    out = os.path.join(cache_dir, os.path.splitext(os.path.basename(path))[0] + ".wav")
    if os.path.exists(out) and os.path.getmtime(out) >= os.path.getmtime(path):
        return out
    if shutil.which("afconvert"):
        cmd = ["afconvert", "-f", "WAVE", "-d", "LEI16@%d" % rate, "-c", "1",
               path, out]
    elif shutil.which("ffmpeg"):
        cmd = ["ffmpeg", "-y", "-loglevel", "error", "-i", path,
               "-ac", "1", "-ar", str(rate), out]
    else:
        raise SystemExit(
            "need afconvert (macOS) or ffmpeg to decode %s.\n"
            "  Convert it to a .wav yourself and pass that instead." % path)
    subprocess.run(cmd, check=True)
    return out


def load_wav(path):
    with wave.open(path, "rb") as w:
        sr, n, ch = w.getframerate(), w.getnframes(), w.getnchannels()
        if w.getsampwidth() != 2:
            raise SystemExit("%s is not 16-bit; re-decode it" % path)
        a = np.frombuffer(w.readframes(n), np.int16).astype(np.float32) / 32768.0
    if ch > 1:
        a = a.reshape(-1, ch).mean(1)
    return a, sr


def onset_envelope(a, sr):
    """Half-wave-rectified spectral flux -- where the transients are.

    Returns (env, env_fps, t0).  t0 matters: analysis frame k covers samples
    [k*HOP, k*HOP+N_FFT), so it describes the audio around its CENTRE, and the
    diff against the previous frame sits half a hop earlier still.  Treating
    env[k] as happening at k*HOP/sr places every detected beat about 17 ms
    early, which at 40 fps is most of a frame -- enough to read as the lights
    firing just before the kick.

    That geometric correction is not the whole story.  Measured against
    synthetic click tracks of known tempo and phase, the grid still landed
    early and consistently so: mean -13.2 ms, sd 1.0 ms over 1088 beats
    spanning 90-174 bpm, several start offsets, 4 ms of jitter, and kick,
    noise and pad attacks from 6 to 60 ms decay.  A Hanning window weights
    a transient near its leading edge down, so the flux does not peak until
    the transient is past centre.  Rather than model that, the residual is
    measured and removed -- ONSET_BIAS_S -- which leaves well under a
    millisecond.  The one case it does not fit is a pad with a 30 ms
    attack, where the onset has no single instant to be right about.
    """
    n = 1 + (len(a) - N_FFT) // HOP
    idx = np.arange(N_FFT)[None, :] + HOP * np.arange(n)[:, None]
    win = np.hanning(N_FFT).astype(np.float32)
    mag = np.abs(np.fft.rfft(a[idx] * win, axis=1))
    logm = np.log1p(mag * 8.0)
    flux = np.concatenate([[0.0], np.maximum(0.0, np.diff(logm, axis=0)).sum(1)])
    flux -= np.convolve(flux, np.ones(41) / 41.0, mode="same")   # local baseline
    t0 = (N_FFT / 2.0 - HOP / 2.0) / float(sr) + ONSET_BIAS_S
    return np.maximum(flux, 0.0).astype(np.float64), sr / float(HOP), t0


def frame_curves(a, sr, env, env_fps, env_t0, out_fps, duration):
    """The two per-frame curves an effect can ride: loudness and onset punch.

    Sampled at the show's frame rate so the renderer only ever does an array
    lookup.  Both are 0..1, scaled against the track's own distribution so a
    quiet record and a squashed one both use the full range.
    """
    n = int(math.ceil(duration * out_fps))
    t = np.arange(n) / float(out_fps)

    # loudness: RMS over a 50 ms window centred on each frame, in dB
    half = max(1, int(0.025 * sr))
    pos = np.clip((t * sr).astype(int), 0, max(len(a) - 1, 0))
    cs = np.concatenate([[0.0], np.cumsum(a.astype(np.float64) ** 2)])
    lo = np.clip(pos - half, 0, len(a))
    hi = np.clip(pos + half, 0, len(a))
    rms = np.sqrt((cs[hi] - cs[lo]) / np.maximum(hi - lo, 1) + 1e-12)
    db = 20 * np.log10(rms + 1e-9)
    p5, p97 = np.percentile(db, 5), np.percentile(db, 97)
    energy = np.clip((db - p5) / max(p97 - p5, 1e-6), 0, 1)
    energy = np.convolve(energy, np.ones(3) / 3.0, mode="same")

    # onset punch: resample the flux, normalise, then let each hit ring out
    et = env_t0 + np.arange(len(env)) / float(env_fps)
    onset = np.interp(t, et, env, left=0.0, right=0.0)
    onset = np.clip(onset / max(np.percentile(onset, 98), 1e-9), 0, 1)
    decay = math.exp(-1.0 / (0.12 * out_fps))          # ~120 ms tail
    for i in range(1, n):
        if onset[i] < onset[i - 1] * decay:
            onset[i] = onset[i - 1] * decay
    return energy.astype(np.float32), onset.astype(np.float32)


def estimate_tempo(env, fps, bpm_lo=70.0, bpm_hi=180.0, t0=0.0):
    """Coarse autocorrelation, then a fine comb whose phase gives the offset.

    Evaluating sum(env * e^-2*pi*i*f*t) over a fine grid of beat frequencies
    is exactly "how much onset energy lands on a grid at this tempo", and the
    phase of the winner is the first beat -- so tempo and downbeat fall out of
    one calculation.
    """
    t = t0 + np.arange(len(env)) / fps
    e = env - env.mean()
    ac = np.correlate(e, e, "full")[len(e) - 1:]
    lag = np.arange(len(ac)) / fps
    band = np.where((lag > 60.0 / bpm_hi) & (lag < 60.0 / bpm_lo))[0]
    coarse = 60.0 / lag[band[int(np.argmax(ac[band]))]]

    best = None
    total = max(env.sum(), 1e-9)
    for mult in (0.5, 1.0, 2.0):
        b0 = coarse * mult
        if not bpm_lo <= b0 <= bpm_hi:
            continue
        # one frequency at a time: the full outer product would be a 300 MB
        # complex matrix, and this is not the slow part
        for bpm in np.arange(b0 * 0.97, b0 * 1.03, 0.002):
            w = 2 * math.pi * (bpm / 60.0) * t
            re, im = float(np.dot(env, np.cos(w))), float(-np.dot(env, np.sin(w)))
            score = math.hypot(re, im) / total
            if best is None or score > best[0]:
                best = (score, float(bpm), math.atan2(im, re))
    score, bpm, phase = best
    period = 60.0 / bpm
    offset = (-phase / (2 * math.pi)) * period % period
    return bpm, offset, score


def beat_grid(bpm, offset, duration):
    return offset + (60.0 / bpm) * np.arange(int((duration - offset) / (60.0 / bpm)) + 1)


def downbeat_phase(env, fps, beats, per_bar=4):
    """Which of the 4 beats carries the most weight -- that is beat one."""
    idx = np.clip((beats * fps).astype(int), 0, len(env) - 1)
    peak = np.array([env[max(0, i - 2):i + 3].max() for i in idx])
    return int(np.argmax([peak[p::per_bar].mean() for p in range(per_bar)]))


def _rank(x):
    """Map values to their own rank in 0..1 -- immune to how hot the master is."""
    order = np.argsort(np.argsort(np.asarray(x, float)))
    return order / max(len(order) - 1, 1)


def bar_energy(a, sr, bars, env, fps, env_t0=0.0):
    """How "full" each bar is: overall level, bass weight, and onset density.

    Overall level alone does not separate a breakdown from a drop on a modern
    master -- everything is squashed to the same RMS.  What actually leaves
    during a breakdown is the kick and the density of hits, so all three go in.
    """
    rms, low, hits = [], [], []
    band = np.fft.rfftfreq(N_FFT, 1.0 / sr)
    for i in range(len(bars) - 1):
        s0, s1 = int(bars[i] * sr), int(bars[i + 1] * sr)
        seg = a[max(0, s0):max(s0 + 1, s1)].astype(np.float64)
        rms.append(math.sqrt((seg ** 2).mean() + 1e-12))
        if len(seg) >= 256:                     # sub-200 Hz weight = kick + bass
            f = np.abs(np.fft.rfft(seg * np.hanning(len(seg))))
            fr = np.fft.rfftfreq(len(seg), 1.0 / sr)
            low.append(f[fr < 200].sum() / (f.sum() + 1e-9))
        else:
            low.append(0.0)
        e0, e1 = int((bars[i] - env_t0) * fps), int((bars[i + 1] - env_t0) * fps)
        hits.append(float(env[max(0, e0):max(e0 + 1, e1)].mean()))
    v = (_rank(rms) + _rank(low) + _rank(hits)) / 3.0
    return np.convolve(v, np.ones(3) / 3.0, mode="same")      # smooth over 3 bars


def energy_levels(energy):
    """Four bands, split at the track's own quartiles rather than fixed values,
    so every track gets a mix of looks instead of one look for ten minutes."""
    cuts = np.percentile(energy, [30, 60, 85])
    return np.digitize(energy, cuts)


def split_long(secs, max_bars=24):
    """Cut long runs into phrase-length chunks; the look then rotates colour
    and variant per chunk instead of holding one image for minutes."""
    out = []
    for i0, i1, lvl in secs:
        n = i1 - i0
        if n <= max_bars:
            out.append([i0, i1, lvl])
            continue
        parts = int(math.ceil(n / float(max_bars)))
        size = int(round(n / float(parts) / 4.0)) * 4 or 4
        a = i0
        while a < i1:
            b = min(a + size, i1)
            if i1 - b < 4:
                b = i1
            out.append([a, b, lvl])
            a = b
    return out


def sections(levels, min_bars=8, snap=4):
    """Runs of equal level, short ones merged, boundaries snapped to phrases."""
    runs = []
    start = 0
    for i in range(1, len(levels) + 1):
        if i == len(levels) or levels[i] != levels[start]:
            runs.append([start, i, int(levels[start])])
            start = i
    changed = True
    while changed and len(runs) > 1:
        changed = False
        for i, r in enumerate(runs):
            if r[1] - r[0] >= min_bars:
                continue
            j = i - 1 if i else 1
            if i and i + 1 < len(runs):                 # merge into the closer level
                j = i - 1 if abs(runs[i - 1][2] - r[2]) <= abs(runs[i + 1][2] - r[2]) else i + 1
            lo, hi = min(i, j), max(i, j)
            runs[lo] = [runs[lo][0], runs[hi][1], runs[j][2]]
            del runs[hi]
            changed = True
            break
    for r in runs[1:]:
        r[0] = int(round(r[0] / snap) * snap)
    for i in range(len(runs) - 1):
        runs[i][1] = runs[i + 1][0]
    return [r for r in runs if r[1] > r[0]]


# --------------------------------------------------------------------------
# the show
# --------------------------------------------------------------------------
PALETTE = [
    ((0, 150, 255), (255, 40, 0)),        # cyan / red -- the classic
    ((160, 0, 255), (0, 255, 160)),       # violet / mint
    ((255, 90, 0), (0, 120, 255)),        # amber / blue
    ((255, 0, 110), (0, 220, 255)),       # magenta / ice
    ((0, 255, 120), (255, 200, 0)),       # green / gold
]


def build_timeline(h, beats, bars, levels, duration, title="", music=None):
    """Turn the analysis into cues.  Four looks, chosen by how loud a bar is.

    Two things keep it welded to the track rather than merely started by it:

      * every periodic effect gets ``origin`` = the first downbeat, so a
        one-bar sweep crosses the face ON the downbeat, every bar, all the way
        through the show instead of drifting from wherever t=0 left it;
      * everything rides a continuous curve -- ``energy`` for the slow moving
        looks, ``onset`` for anything percussive -- so the brightness follows
        the music between beats as well as on them.
    """
    b = mau5fx.Beats(beats)
    period = float(np.median(np.diff(beats))) if len(beats) > 2 else 0.47
    bar_s = period * 4
    org = float(bars[0])                      # the global downbeat grid
    tl = mau5fx.Timeline(h, music=music)
    secs = split_long(sections(levels))

    def E(cls, *a, **kw):
        kw.setdefault("origin", org)
        kw.setdefault("music", music)
        return cls(h, *a, **kw)

    for n, (i0, i1, lvl) in enumerate(secs):
        t0 = float(bars[i0])
        t1 = float(bars[min(i1, len(bars) - 1)])
        if n == 0:
            t0 = 0.0                       # cover the pre-roll before bar one
        if n == len(secs) - 1:
            t1 = max(t1, duration)         # and the tail after the last bar
        if t1 - t0 < 0.5:
            continue
        cool, warm = PALETTE[n % len(PALETTE)]
        fade = min(period * 2, (t1 - t0) / 3.0)

        if lvl == 0:                                   # intro / breakdown
            # two variants, alternating per phrase, so a three minute ambient
            # intro is not three minutes of one thing
            if n % 2 == 0:
                tl.add(t0, t1, E(mau5fx.Swell, cool, period=bar_s * 2, floor=0.15,
                                 drive="energy", drive_floor=0.30),
                       fade_in=fade, fade_out=fade)
            else:
                tl.add(t0, t1, E(mau5fx.Swell, cool, period=bar_s * 3, floor=0.1,
                                 invert=True, drive="energy", drive_floor=0.30),
                       fade_in=fade, fade_out=fade)
                tl.add(t0, t1, E(mau5fx.AzimuthSweep, warm, period=bar_s * 4,
                                 width_deg=70, brightness=0.55, drive="energy",
                                 drive_floor=0.22), fade_in=fade, fade_out=fade)
            tl.add(t0, t1, E(mau5fx.Twinkle, (180, 210, 255), density=0.03,
                             decay=0.9, brightness=0.5, drive="onset",
                             drive_floor=0.20), fade_in=fade, fade_out=fade)
            tl.add(t0, t1, E(mau5fx.VisorGlow, cool, breathe=bar_s * 2,
                             drive="energy", drive_floor=0.22),
                   fade_in=fade, fade_out=fade)
            tl.add(t0, t1, E(mau5fx.RimSpin, warm, period=bar_s, brightness=0.5),
                   fade_in=fade, fade_out=fade)

        elif lvl == 1:                                 # groove
            tl.add(t0, t1, E(mau5fx.AzimuthSweep, cool, period=bar_s,
                             width_deg=50, drive="energy", drive_floor=0.355),
                   fade_in=fade)
            tl.add(t0, t1, E(mau5fx.VisorGlow, warm, breathe=0, sweep=bar_s,
                             brightness=0.8))
            tl.add(t0, t1, E(mau5fx.RimSpin, warm, period=bar_s / 2))
            tl.add(t0, t1, E(mau5fx.BladeChase, cool, period=period * 2,
                             drive="onset", drive_floor=0.30))

        elif lvl == 2:                                 # drive
            tl.add(t0, t1, E(mau5fx.Sprite, "eyes", color=warm, beats=b,
                             beat_decay=0.14, beat_floor=0.35,
                             drive="onset", drive_floor=0.45), fade_in=fade)
            tl.add(t0, t1, E(mau5fx.BladeChase, cool, period=period,
                             drive="onset", drive_floor=0.25))
            tl.add(t0, t1, E(mau5fx.RimSpin, warm, period=bar_s / 2, direction=-1))
            tl.add(t0, t1, E(mau5fx.ElevationPulse, cool, period=bar_s / 2,
                             width_deg=16, drive="energy", drive_floor=0.22),
                   blend="add")
            tl.add(t0, t1, E(mau5fx.VisorGlow, cool, breathe=0, brightness=0.6,
                             drive="energy", drive_floor=0.25))

        else:                                          # peak / drop
            tl.add(t0, t1, E(mau5fx.Sprite, "x_eyes", color=warm, beats=b,
                             beat_decay=0.09, beat_floor=0.25,
                             drive="onset", drive_floor=0.355))
            tl.add(t0, t1, E(mau5fx.BladeIgnite, (200, 255, 255), beats=b))
            tl.add(t0, t1, E(mau5fx.RimSpin, warm, period=period * 2))
            tl.add(t0, t1, E(mau5fx.AzimuthSweep, cool, period=period * 2,
                             width_deg=28, drive="onset", drive_floor=0.22),
                   blend="add")
            tl.add(t0, t1, E(mau5fx.VisorGlow, warm, breathe=0,
                             drive="energy", drive_floor=0.22))
            # two flashes per beat, locked to the beat grid
            tl.add(t0, min(t1, t0 + bar_s),
                   E(mau5fx.Strobe, (255, 255, 255), hz=2.0 / period, duty=0.10))

        prev = secs[n - 1][2] if n else 0
        if lvl - prev >= 2:                            # the drop itself
            tl.add(t0, t0 + period * 1.5,
                   E(mau5fx.Solid, (255, 255, 255), brightness=0.85),
                   fade_out=period * 1.4)

    # the name of the track over the first and last quiet stretches
    if title:
        quiet = [x for x in secs if x[2] <= 1 and bars[x[1] - 1] - bars[x[0]] > 12]
        for x in ([quiet[0]] if quiet else []) + ([quiet[-1]] if len(quiet) > 1 else []):
            t0 = float(bars[x[0]]) + bar_s
            tl.add(t0, min(t0 + bar_s * 8, duration),
                   E(mau5fx.ScrollText, title, speed=18, color=(255, 255, 255),
                     brightness=0.85, origin=t0), fade_in=1.0, fade_out=1.0)
    return tl, secs


# --------------------------------------------------------------------------
def analyse(path, bpm=None, offset=None, beats_file=None, verbose=True):
    wav = decode(path)
    a, sr = load_wav(wav)
    dur = len(a) / sr
    env, fps, env_t0 = onset_envelope(a, sr)

    if beats_file:
        beats = mau5fx.Beats.from_file(beats_file).times
        bpm = 60.0 / float(np.median(np.diff(beats))) if len(beats) > 2 else 0.0
        conf = float("nan")
    else:
        if bpm is None:
            bpm, off, conf = estimate_tempo(env, fps, t0=env_t0)
            offset = off if offset is None else offset
        else:
            conf = float("nan")
            if offset is None:
                grid = np.arange(0, 60.0 / bpm, 0.005)
                idx = np.clip((((grid[:, None] + np.arange(0, dur, 60.0 / bpm)[None, :])
                                - env_t0) * fps).astype(int), 0, len(env) - 1)
                offset = float(grid[int(np.argmax(env[idx].sum(1)))])
        beats = beat_grid(bpm, offset, dur)

    ph = downbeat_phase(env, fps, beats - env_t0)
    bars = beats[ph::4]
    energy = bar_energy(a, sr, bars, env, fps, env_t0)
    levels = energy_levels(energy)

    if verbose:
        print("  %.1f s  %.3f bpm  first beat %.3f s  beat lock %s"
              % (dur, bpm, beats[0],
                 "n/a" if conf != conf else "%.2f" % conf))
        print("  %d beats, %d bars, downbeat on beat %d of 4"
              % (len(beats), len(bars), ph + 1))
    return dict(duration=dur, bpm=bpm, beats=beats, bars=bars, energy=energy,
                levels=levels, audio=a, sr=sr, env=env, env_fps=fps,
                env_t0=env_t0, lock=conf)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter,
                                 epilog=__doc__)
    ap.add_argument("audio", nargs="+")
    ap.add_argument("--config", default=mau5cfg.DEFAULT_CONFIG)
    ap.add_argument("--name", help="show name (defaults to a slug of the filename)")
    ap.add_argument("--bpm", type=float)
    ap.add_argument("--offset", type=float, help="seconds to the first beat")
    ap.add_argument("--beats", help="use this beat file instead of analysing")
    ap.add_argument("--compression", choices=["none", "zlib", "zstd"],
                    default="zlib", help="FSEQ compression (default zlib: a "
                                         "10 minute show is 100 MB otherwise)")
    ap.add_argument("--seconds", type=float, help="stop early, for a quick look")
    ap.add_argument("--preview", action="store_true",
                    help="open the simulator when it is built")
    ap.add_argument("--analyse-only", action="store_true")
    a = ap.parse_args(argv)

    h = mau5cfg.load(a.config, quiet=True)
    built = []
    for path in a.audio:
        if not os.path.exists(path):
            print("no such file: %s" % path, file=sys.stderr)
            continue
        title = os.path.splitext(os.path.basename(path))[0]
        name = a.name or slug(title)
        print("\n%s" % title)
        an = analyse(path, a.bpm, a.offset, a.beats)
        dur = min(an["duration"], a.seconds) if a.seconds else an["duration"]

        base = os.path.dirname(os.path.abspath(h.path))
        out_dir = os.path.join(base, h.cfg["show"].get("shows_dir", "shows"))
        os.makedirs(out_dir, exist_ok=True)
        mau5fx.Beats(an["beats"]).save(os.path.join(out_dir, name + ".beats"))

        energy_c, onset_c = frame_curves(an["audio"], an["sr"], an["env"],
                                         an["env_fps"], an["env_t0"], h.fps, dur)
        music = mau5fx.Music(mau5fx.Beats(an["beats"]), h.fps, energy_c, onset_c)
        music.save(os.path.join(out_dir, name + ".music.npz"))
        tl, secs = build_timeline(h, an["beats"], an["bars"], an["levels"],
                                  dur, title=short_title(title), music=music)
        print("  %d sections, %d cues:" % (len(secs), len(tl.cues)))
        for i0, i1, lvl in secs:
            t0, t1 = an["bars"][i0], an["bars"][min(i1, len(an["bars"]) - 1)]
            if t1 <= dur:
                print("    %s-%s  %2d bars  %s %s"
                      % (mmss(t0), mmss(t1), i1 - i0,
                         ["hold", "groove", "drive", "peak "][lvl],
                         "#" * (lvl * 4 + 1)))
        if a.analyse_only:
            continue

        source = FrameSource(tl)
        mau5build.build(h, name, audio=path, effect=None, fseq=None,
                        seconds=dur, compression=a.compression,
                        timeline=source)
        built.append(name)

    if built:
        print("\nbuilt: %s" % ", ".join(built))
        print("watch one:   python3 mau5sim.py --fseq shows/%s.fseq" % built[0])
        print("send to Pi:  python3 mau5build.py upload --name %s" % built[0])
    if a.preview and built:
        os.execv(sys.executable, [sys.executable, "mau5sim.py", "--fseq",
                                  os.path.join("shows", built[0] + ".fseq")])


class FrameSource:
    """Adapter so mau5build can render a Timeline we already have in hand."""

    def __init__(self, tl):
        self.tl = tl
        self.n_frames = None

    def frame(self, i, t):
        return self.tl.render_frame(i, t)


def slug(s):
    keep = "".join(c if c.isalnum() else "-" for c in s.lower())
    while "--" in keep:
        keep = keep.replace("--", "-")
    return keep.strip("-")[:48]


def short_title(s):
    """'Artist - Title' -> 'TITLE', which is what fits round a sphere."""
    part = s.split(" - ")[-1]
    return "".join(c for c in part.upper() if c.isalnum() or c in " '!?&.-").strip()


def mmss(t):
    t = int(round(float(t)))
    return "%d:%02d" % (t // 60, t % 60)


if __name__ == "__main__":
    main()
