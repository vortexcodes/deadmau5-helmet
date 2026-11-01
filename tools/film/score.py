#!/usr/bin/env python3
"""score.py -- music for the helmet's videos, written here so it can be hosted.

The songs can't go on a public website, so nothing here uses them. Two
ways to get a track, both drawn from the same small synth:

  free(...)    a track to a list of sections, for the explainer videos.
  follow(...)  a stand-in for one stretch of a real song: its beat grid and
               its bass, mid and high curves decide when the kick, the bass,
               the pads and the hats play. No notes come from the song. The
               chords are the progressions below, so what you hear is the
               data the helmet has, played back.

Numpy only. Same input, same output: every noise source is seeded.

    python3 tools/film/score.py out.wav --seconds 40 --bpm 124
"""

from __future__ import annotations

import argparse
import subprocess
import wave

import numpy as np

SR = 44100
A4 = 440.0

# Semitones above the root for each chord; each one lasts `bars_per_chord`.
PROGRESSIONS = {
    "drift": [(0, 7, 12, 15), (-4, 3, 8, 12), (-7, 0, 5, 8), (-2, 5, 10, 14)],
    "lift": [(0, 7, 10, 15), (-5, 2, 7, 10), (-4, 3, 7, 12), (-2, 2, 5, 10)],
    "night": [(0, 3, 7, 14), (-3, 4, 7, 12), (-7, 0, 3, 8), (-5, 2, 5, 10)],
}
ARP = (0, 2, 1, 3, 2, 1, 3, 2, 0, 3, 1, 2, 3, 2, 1, 0)


def hz(midi):
    return A4 * 2.0 ** ((np.asarray(midi, float) - 69.0) / 12.0)


def _add(buf, start, sig):
    """Mix a mono or stereo signal into `buf` at a sample offset, clipped to it."""
    i = int(start)
    if i >= len(buf) or i + len(sig) <= 0:
        return
    if i < 0:
        sig, i = sig[-i:], 0
    n = min(len(sig), len(buf) - i)
    buf[i:i + n] += sig[:n]


def _noise(n, seed):
    return np.random.default_rng(seed).standard_normal(n)


def _kick(amp):
    n = int(0.32 * SR)
    t = np.arange(n) / SR
    f = 46 + 120 * np.exp(-t / 0.028)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.16)
    s[:int(0.002 * SR)] += _noise(int(0.002 * SR), 1) * 0.3
    return amp * s


def _clap(amp, seed):
    n = int(0.28 * SR)
    t = np.arange(n) / SR
    s = _noise(n, seed)
    s = np.diff(np.cumsum(s) * 0.25 + s, prepend=0.0)     # thin out the lows
    env = np.exp(-t / 0.07) + 0.6 * np.exp(-((t - 0.012) / 0.003) ** 2)
    return amp * 0.35 * s * env


def _hat(amp, seed, long=False):
    n = int((0.12 if long else 0.045) * SR)
    t = np.arange(n) / SR
    s = np.diff(_noise(n + 1, seed))
    return amp * 0.14 * s * np.exp(-t / (0.04 if long else 0.012))


def _bass(midi, secs, amp):
    n = int(secs * SR)
    t = np.arange(n) / SR
    f = hz(midi)
    s = sum(np.sin(2 * np.pi * f * k * t) * w for k, w in ((1, 1.0), (2, 0.42), (3, 0.2), (4, 0.09)))
    env = np.minimum(t / 0.006, 1) * np.minimum((secs - t) / 0.02, 1) * np.exp(-t / (secs * 1.5))
    return amp * 0.42 * np.tanh(1.4 * s) * env


def _pluck(midi, amp, seed=0):
    n = int(0.5 * SR)
    t = np.arange(n) / SR
    f = hz(midi)
    s = np.zeros(n)
    for k in range(1, 8):
        if f * k > 9000:
            break
        s += np.sin(2 * np.pi * f * k * t + seed) / k ** 1.3 * np.exp(-t * (5 + 7 * k))
    return amp * 0.3 * s * np.minimum(t / 0.002, 1)


def _pad(notes, secs, cut, seed=3):
    """A held chord, built from harmonics so the filter is just their weights.
    `cut` is the cutoff in Hz over the length of the chord, as an array or a number."""
    n = int(secs * SR)
    t = np.arange(n) / SR
    cut = np.broadcast_to(np.asarray(cut, float), t.shape)
    L, R = np.zeros(n), np.zeros(n)
    rng = np.random.default_rng(seed)
    for note in notes:
        f0 = float(hz(note))
        for det, pan in ((-0.0035, 0.2), (0.0, 0.5), (0.0042, 0.8)):
            f = f0 * (1 + det)
            ph = rng.uniform(0, 2 * np.pi, 16)
            s = np.zeros(n)
            for k in range(1, 17):
                if f * k > 12000:
                    break
                w = 1.0 / k / (1 + (f * k / cut) ** 4)
                s += w * np.sin(2 * np.pi * f * k * t + ph[k - 1])
            L += s * (1 - pan)
            R += s * pan
    env = np.minimum(t / 0.05, 1) * np.minimum((secs - t) / 0.05, 1)
    return np.c_[L * env, R * env] * 0.05


def _reverb(x, secs=1.8, seed=9):
    """Stereo noise tail, convolved in one go."""
    n = int(secs * SR)
    t = np.arange(n) / SR
    decay = np.exp(-t / (secs / 5))
    out = np.zeros_like(x)
    size = len(x) + n
    for c in (0, 1):
        ir = _noise(n, seed + c) * decay
        ir = ir - np.convolve(ir, np.ones(64) / 64, "same")   # no low rumble
        ir /= np.sqrt((ir ** 2).sum())
        y = np.fft.irfft(np.fft.rfft(x[:, c], size) * np.fft.rfft(ir, size), size)
        out[:, c] = y[:len(x)]
    return out


def _echo(x, every, feedback=0.42, repeats=4):
    out = x.copy()
    d = int(every * SR)
    for r in range(1, repeats + 1):
        if d * r >= len(x):
            break
        c = (0, 1) if r % 2 else (1, 0)       # bounce side to side
        out[d * r:, 0] += x[:-d * r, c[0]] * feedback ** r
        out[d * r:, 1] += x[:-d * r, c[1]] * feedback ** r
    return out


class Curves:
    """What one bit of music is doing at any moment, each 0..1. Plain arrays at
    `rate` Hz from time 0, or a constant."""

    def __init__(self, bass, mid, high, rate=100.0, punch=None):
        self.c = {"bass": np.asarray(bass, float), "mid": np.asarray(mid, float),
                  "high": np.asarray(high, float)}
        self.rate = rate
        self.punch = punch      # {"bass": array, ...}: how hard each band just rose

    def at(self, t, name):
        a = self.c[name]
        return float(a[min(max(int(t * self.rate), 0), len(a) - 1)])

    def over(self, t0, t1, name):
        a = self.c[name]
        i, j = int(t0 * self.rate), int(t1 * self.rate) + 1
        i = min(max(i, 0), len(a) - 1)
        return a[i:max(j, i + 1)]

    def at_many(self, ts, name):
        a = self.c[name]
        return a[np.clip((np.asarray(ts) * self.rate).astype(int), 0, len(a) - 1)]


def _hit(curves, t, dur, name, floor=0.45):
    """The band's punch around this 16th, or 0 if nothing landed on it."""
    a = curves.punch[name]
    r = curves.rate
    i, j = max(int((t - 0.025) * r), 0), int((t + dur * 0.6) * r) + 1
    v = float(a[i:max(j, i + 1)].max()) if i < len(a) else 0.0
    return v if v > floor else 0.0


def _render(duration, steps, curves, root, prog, bars_per_chord=2, seed=11, bass_gain=1.0):
    """`steps` lists every 16th: (time, 16ths since the bar line of bar 0, length).
    Everything the track does is decided here from the curves."""
    n = int(duration * SR)
    drums = np.zeros(n)
    hats = np.zeros(n)
    bass = np.zeros(n)
    pluck = np.zeros((n, 2))
    pad = np.zeros((n, 2))
    send = np.zeros((n, 2))
    duck = np.ones(n)
    chords = PROGRESSIONS[prog]
    pad_at = {}
    for t, s, dur in steps:
        beat, sub = s // 4, s % 4
        bar = s // 16
        chord = chords[(bar // bars_per_chord) % len(chords)]
        B = curves.at(t, "bass")
        M = curves.at(t, "mid")
        H = curves.at(t, "high")
        peak = float(curves.over(t, t + dur * 1.5, "bass").max())
        seed += 1
        if curves.punch is not None:
            # A real song says where its own kicks and snares are.
            hit = _hit(curves, t, dur, "bass")
            snare = beat % 2 == 1 and sub == 0 and _hit(curves, t, dur, "mid", 0.3) > 0
            kick_now = hit > 0
            peak = max(peak, hit)
        else:
            kick_now = sub == 0 and peak > 0.45
            snare = sub == 0 and beat % 2 == 1 and M > 0.42
        if kick_now:
            k = 0.62 + 0.38 * min(peak, 1)
            _add(drums, t * SR, _kick(k))
            i = int(t * SR)
            m = min(int(0.42 * SR), n - i)
            if m > 0:
                dt = np.arange(m) / SR
                duck[i:i + m] = np.minimum(duck[i:i + m], 1 - 0.72 * k * np.exp(-dt / 0.13))
        if snare:
            c = _clap(0.6 * min(M + 0.2, 1), seed)
            _add(drums, t * SR, c)
            _add(send[:, 0], t * SR, c * 0.3)
            _add(send[:, 1], t * SR, c * 0.3)
        if H > 0.25:
            if sub == 2:
                _add(hats, t * SR, _hat(H, seed, long=True))
            elif s % 2 == 1:
                _add(hats, t * SR, _hat(H * 0.55, seed))
        if s % 2 == 0 and sub != 0 and B > 0.3:
            _add(bass, t * SR, _bass(root - 12 + chord[0], dur * (1.8 if bass_gain >= 1 else 1.0), min(B + 0.2, 1) * bass_gain))
        if M > 0.3 or H > 0.55:
            note = root + 24 + chord[ARP[s % 16]] + (12 if s % 32 >= 28 else 0)
            p = _pluck(note, 0.25 + 0.75 * max(M, H * 0.7))
            pan = 0.5 + 0.35 * np.sin(s * 0.7)
            _add(pluck[:, 0], t * SR, p * (1 - pan))
            _add(pluck[:, 1], t * SR, p * pan)
        key = bar // bars_per_chord
        if key not in pad_at:
            pad_at[key] = (t, chord)
    keys = sorted(pad_at)
    for a, b in zip(keys, keys[1:] + [None]):
        t, chord = pad_at[a]
        t1 = pad_at[b][0] if b is not None else duration
        secs = max(t1 - t, 0.05) + 0.1
        ts = t + np.arange(int(secs * SR)) / SR
        m = curves.at_many(ts, "mid")
        h = curves.at_many(ts, "high")
        cut = 260 + 3600 * np.clip(0.75 * m + 0.35 * h, 0, 1) ** 1.6
        amp = 0.35 + 0.65 * np.clip(m + 0.3 * h, 0, 1)
        y = _pad([root + c for c in chord], secs, cut)
        y = y * amp[:, None]
        i = int(t * SR)
        m2 = min(len(y), n - i)
        if m2 > 0:
            pad[i:i + m2] += y[:m2]
    spb = steps[1][0] - steps[0][0] if len(steps) > 1 else 0.12
    pluck = _echo(pluck, spb * 3)
    wet = _reverb(pad * 0.5 + pluck * 0.35 + send)
    mix = np.zeros((n, 2))
    # Kick and bass are held well under the pads and plucks: this plays under
    # somebody reading, and a loud kick is all a laptop speaker would give them.
    centre = drums * 0.5 + bass * duck * 0.42
    mix[:, 0] = centre + hats * 0.85
    mix[:, 1] = centre + hats * 0.7
    mix += (pad * 2.4 + pluck * 1.5) * duck[:, None]
    mix += wet * 1.2 * (0.55 + 0.45 * duck[:, None])
    return master(mix)


def master(x, peak=0.72, fade=(0.3, 0.8)):
    """Soft-clip the sum and bring it to a level that sits under reading."""
    x = x / (np.abs(x).max() + 1e-9)
    x = np.tanh(1.5 * x) / np.tanh(1.5)
    x = x * peak
    n = len(x)
    a, b = int(fade[0] * SR), int(fade[1] * SR)
    if a:
        x[:a] *= (np.arange(a) / a)[:, None]
    if b:
        x[-b:] *= (1 - np.arange(b) / b)[:, None]
    return x


def free(duration, bpm, sections, root=45, prog="drift", seed=11, bass=1.0):
    """`sections` is [(start_seconds, bass, mid, high), ...], each level held until
    the next and eased over half a second. A track's arrangement is just this."""
    rate = 100
    m = int(duration * rate) + 2
    arr = {k: np.zeros(m) for k in ("bass", "mid", "high")}
    for i, (t0, b, md, h) in enumerate(sections):
        t1 = sections[i + 1][0] if i + 1 < len(sections) else duration + 1
        a, e = int(t0 * rate), int(t1 * rate)
        arr["bass"][a:e], arr["mid"][a:e], arr["high"][a:e] = b, md, h
    k = np.hanning(int(rate * 0.5) | 1)
    k /= k.sum()
    cv = Curves(np.convolve(arr["bass"], k, "same"), np.convolve(arr["mid"], k, "same"),
                np.convolve(arr["high"], k, "same"), rate)
    # the kick has to stay a hard yes or no, so its curve keeps its edges
    cv.c["bass"] = arr["bass"]
    step = 60.0 / bpm / 4
    steps = [(i * step, i, step) for i in range(int(duration / step) + 1)]
    return _render(duration, steps, cv, root, prog, seed=seed, bass_gain=bass)


def follow(t_from, t_to, spb, grid_t, bands, punch, rate, root=45, prog="drift", seed=11):
    """A stand-in for a stretch of a real song. `grid_t(step)` gives the time of the
    `step`th 16th since bar 0; `bands` and `punch` hold its analysis curves at `rate`
    Hz, whole song. The result is t_to - t_from seconds long."""
    i, j = int(t_from * rate), int(t_to * rate) + 2
    cv = Curves(bands["bass"][i:j], bands["mid"][i:j], bands["high"][i:j], rate,
                {k: v[i:j] for k, v in punch.items()})
    step = spb / 4
    s0 = int(np.floor((t_from - grid_t(0)) / step)) - 1
    steps = []
    s = s0
    while True:
        t = grid_t(s)
        if t >= t_to:
            break
        if t >= t_from:
            steps.append((t - t_from, s, step))
        s += 1
    return _render(t_to - t_from, steps, cv, root, prog, seed=seed)


def write_wav(path, x):
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((np.clip(x, -1, 1) * 32767).astype("<i2").tobytes())


def loudness(path):
    """Integrated loudness and true peak from ffmpeg's EBU R128 meter, as text."""
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-filter_complex",
                        "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True)
    tail = r.stderr[r.stderr.rfind("Summary:"):]
    return " ".join(tail.split())


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("out")
    ap.add_argument("--seconds", type=float, default=40)
    ap.add_argument("--bpm", type=float, default=124)
    a = ap.parse_args()
    d = a.seconds
    x = free(d, a.bpm, [(0, 0, .35, .1), (d * .25, .8, .5, .4), (d * .5, 0, .6, .3),
                        (d * .65, .95, .85, .8), (d * .9, 0, .3, 0)])
    write_wav(a.out, x)
    print(a.out, loudness(a.out))


if __name__ == "__main__":
    main()
