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
import time

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
        ("wave", {"period": 1.6})],
    3: [("strobe", {"hz": 6.0}), ("eq", {}), ("fire", {"speed": 1.8}),
        ("rainbow", {"period": 2.5}), ("police", {}), ("lightning", {"every": 1.1}),
        ("pinwheel", {"period": 1.2}), ("confetti", {"rate": 26.0}),
        ("split", {"shell": "fire", "ears": "pinwheel"})],
}

PALETTES = [
    [(255, 40, 0), (255, 150, 0)],
    [(0, 180, 255), (120, 0, 255)],
    [(255, 0, 120), (255, 200, 0)],
    [(0, 255, 140), (0, 90, 255)],
    [(255, 255, 255), (0, 200, 255)],
]


class Music:
    """Per-frame curves the presets can ask about."""

    def __init__(self, path, fps=40, verbose=False, cache=None):
        self.path, self.fps = path, fps
        if cache and os.path.exists(cache):
            z = np.load(cache)
            if int(z["fps"]) == fps:
                self.duration = float(z["duration"]); self.bpm = float(z["bpm"])
                self.beats = z["beats"]; self.bars = z["bars"]
                self.levels = z["levels"]; self.energy = z["energy"]
                self.onset = z["onset"]
                self.sections = [tuple(int(v) for v in r) for r in z["sections"]]
                self.lock_conf = float(z["lock"]) if "lock" in z else float("nan")
                self.bands = True
                return
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
        self.bands = True                      # Equaliser may ask for bands
        if cache:
            np.savez_compressed(
                cache, fps=fps, duration=self.duration, bpm=self.bpm,
                beats=self.beats, bars=self.bars, levels=self.levels,
                energy=self.energy, onset=self.onset,
                sections=np.array(self.sections, int),
                lock=self.lock_conf)

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


def build(track, fps=40, out=None):
    os.makedirs(SHOWS, exist_ok=True)
    base = os.path.splitext(os.path.basename(track))[0]
    m = Music(track, fps=fps, cache=os.path.join(SHOWS, base + ".analysis.npz"))
    cues = []
    for k, (b0, b1, lvl) in enumerate(m.sections):
        t0 = float(m.bars[b0]) if b0 < len(m.bars) else 0.0
        t1 = float(m.bars[b1]) if b1 < len(m.bars) else m.duration
        pool = POOLS[int(np.clip(lvl, 0, 3))]
        name, kw = pool[k % len(pool)]
        pal = PALETTES[k % len(PALETTES)]
        kw = dict(kw)
        cls = E.REGISTRY[name]
        if "color" in cls.params:
            kw["color"] = pal[0]
        if "a" in cls.params and "b" in cls.params:
            kw["a"], kw["b"] = pal[0], pal[1]
        cues.append({"start": round(t0, 3), "end": round(t1, 3),
                     "preset": name, "params": kw, "level": int(lvl)})
    show = {"track": os.path.basename(track), "fps": fps,
            "duration": round(m.duration, 2), "bpm": round(m.bpm, 2),
            "beats": len(m.beats), "analysis": base + ".analysis.npz",
            "fade": 0.6, "accent": True, "cues": cues}
    out = out or os.path.join(SHOWS, base + ".json")
    json.dump(show, open(out, "w"), indent=1)
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
        # Lock unless the show says otherwise, or the analysis never
        # found the beat in the first place.
        want = show.get("lock")
        conf = getattr(music, "lock_conf", float("nan")) if music is not None else 0.0
        self.lock = bool(want) if want is not None else (
            conf == conf and conf >= LOCK_MIN)
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

    def _render(self, cue, t):
        """One cue at time t, on the beat grid where that is meaningful."""
        te = t
        if self.lock and self.music is not None:
            te, _ = E.lock_time(self.music, cue["preset"], cue["params"], t)
        return self._preset(cue).render(self.h, te, self.music)

    def frame(self, t):
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
            # A short lift on every beat, scaled by how loud the section
            # is -- a breakdown should breathe, a drop should hit.
            if self.pulse > 0 and lvl >= 1:
                k = max(0.0, 1.0 - ph * 3.0) ** 2
                out = out * (1.0 + self.pulse * (0.4 + 0.3 * lvl) * k)
            if self.accent and lvl >= 2 and self.music.is_downbeat(t):
                k = max(0.0, 1.0 - ph * 6.0) * 0.45
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
        sc.frame(pl.frame(start + i / fps)).save(os.path.join(tmp, "f%05d.png" % i))
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


def play(show_path, host=None, seconds=None, fps=40, audio=True, verbose=True):
    """Stream the show to the helmet, with the track playing locally.

    Audio is started first and the frame clock is slaved to wall time
    rather than to a frame counter, so a slow frame costs a dropped
    frame instead of silently sliding the whole show late.
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
    nframes = dropped = 0
    try:
        while True:
            t = time.monotonic() - t0
            if t >= dur:
                break
            pix.send(pl.frame(t))
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
        play(a.show, a.host, a.seconds, a.fps, not a.no_audio)
    elif a.cmd == "list":
        for f in sorted(os.listdir(SHOWS)):
            if f.endswith(".json"):
                s = json.load(open(os.path.join(SHOWS, f)))
                print("  %-34s %6.1fs  %5.1f bpm  %2d cues"
                      % (f, s["duration"], s["bpm"], len(s["cues"])))


if __name__ == "__main__":
    main()
