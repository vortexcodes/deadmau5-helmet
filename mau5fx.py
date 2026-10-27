#!/usr/bin/env python3
"""mau5fx -- effects written against the helmet's real geometry.

Nothing here treats the shell as a generic matrix.  Effects address it three
ways, and pick whichever suits them:

  * the 22 x 68 unwrapped grid, for sprites and text (``helmet.grid``);
  * azimuth / elevation in degrees, for sweeps that follow the sphere;
  * plain 1D strips, for the ear blades, ear rims and visor light pipes.

Every effect fills a ``(n_total, 3)`` uint8 buffer -- the same layout that goes
into an FSEQ frame or a DDP packet -- so the simulator and the packager run
identical code.

    import mau5cfg, mau5fx
    h  = mau5cfg.load()
    fx = mau5fx.AzimuthSweep(h, color=(0, 180, 255), period=2.0)
    for buf in mau5fx.render(h, fx, seconds=10):
        ...

Build a show out of cues:

    show = mau5fx.Timeline(h)
    show.add(0,  8, mau5fx.Rainbow(h))
    show.add(4, 12, mau5fx.BladeChase(h, color=(255, 0, 120)), blend="max")
    for buf in show.frames(seconds=12):
        ...
"""

from __future__ import annotations

import colorsys
import json
import math
import os

import numpy as np

# --------------------------------------------------------------------------
# colour helpers
# --------------------------------------------------------------------------
def hsv(h, s=1.0, v=1.0):
    r, g, b = colorsys.hsv_to_rgb(h % 1.0, s, v)
    return (int(r * 255), int(g * 255), int(b * 255))


def scale(color, k):
    k = max(0.0, min(1.0, k))
    return (int(color[0] * k), int(color[1] * k), int(color[2] * k))


def gamma(buf, g=2.2):
    """Perceptual correction.  WLED applies its own, so this is off by default."""
    x = buf.astype(np.float32) / 255.0
    return np.clip((x ** g) * 255.0, 0, 255).astype(np.uint8)


def _paint(buf, idx, values, color, level=1.0, mode="max"):
    """Blend ``color * values * level`` into ``buf`` at ``idx``.

    ``values`` may be a scalar or a per-LED array in 0..1.  "max" is the
    default because stacked cues should not wash out to white.
    """
    if level <= 0:
        return
    col = np.asarray(color, np.float32) * float(level)
    v = np.asarray(values, np.float32)
    add = (v[:, None] if v.ndim else v) * col
    cur = buf[idx].astype(np.float32)
    out = cur + add if mode == "add" else np.maximum(cur, add)
    buf[idx] = np.clip(out, 0, 255).astype(np.uint8)


_HUE_LUT = np.array([[int(c * 255) for c in colorsys.hsv_to_rgb(i / 256.0, 1, 1)]
                     for i in range(256)], np.float32)


# --------------------------------------------------------------------------
# 5x7 pixel font -- columns, bit 0 = top row
# --------------------------------------------------------------------------
FONT5x7 = {
    " ": (0x00, 0x00, 0x00, 0x00, 0x00), "!": (0x00, 0x00, 0x5F, 0x00, 0x00),
    '"': (0x00, 0x07, 0x00, 0x07, 0x00), "#": (0x14, 0x7F, 0x14, 0x7F, 0x14),
    "$": (0x24, 0x2A, 0x7F, 0x2A, 0x12), "%": (0x23, 0x13, 0x08, 0x64, 0x62),
    "&": (0x36, 0x49, 0x55, 0x22, 0x50), "'": (0x00, 0x05, 0x03, 0x00, 0x00),
    "(": (0x00, 0x1C, 0x22, 0x41, 0x00), ")": (0x00, 0x41, 0x22, 0x1C, 0x00),
    "*": (0x14, 0x08, 0x3E, 0x08, 0x14), "+": (0x08, 0x08, 0x3E, 0x08, 0x08),
    ",": (0x00, 0x50, 0x30, 0x00, 0x00), "-": (0x08, 0x08, 0x08, 0x08, 0x08),
    ".": (0x00, 0x60, 0x60, 0x00, 0x00), "/": (0x20, 0x10, 0x08, 0x04, 0x02),
    "0": (0x3E, 0x51, 0x49, 0x45, 0x3E), "1": (0x00, 0x42, 0x7F, 0x40, 0x00),
    "2": (0x42, 0x61, 0x51, 0x49, 0x46), "3": (0x21, 0x41, 0x45, 0x4B, 0x31),
    "4": (0x18, 0x14, 0x12, 0x7F, 0x10), "5": (0x27, 0x45, 0x45, 0x45, 0x39),
    "6": (0x3C, 0x4A, 0x49, 0x49, 0x30), "7": (0x01, 0x71, 0x09, 0x05, 0x03),
    "8": (0x36, 0x49, 0x49, 0x49, 0x36), "9": (0x06, 0x49, 0x49, 0x29, 0x1E),
    ":": (0x00, 0x36, 0x36, 0x00, 0x00), ";": (0x00, 0x56, 0x36, 0x00, 0x00),
    "<": (0x08, 0x14, 0x22, 0x41, 0x00), "=": (0x14, 0x14, 0x14, 0x14, 0x14),
    ">": (0x00, 0x41, 0x22, 0x14, 0x08), "?": (0x02, 0x01, 0x51, 0x09, 0x06),
    "@": (0x32, 0x49, 0x79, 0x41, 0x3E), "A": (0x7E, 0x11, 0x11, 0x11, 0x7E),
    "B": (0x7F, 0x49, 0x49, 0x49, 0x36), "C": (0x3E, 0x41, 0x41, 0x41, 0x22),
    "D": (0x7F, 0x41, 0x41, 0x22, 0x1C), "E": (0x7F, 0x49, 0x49, 0x49, 0x41),
    "F": (0x7F, 0x09, 0x09, 0x09, 0x01), "G": (0x3E, 0x41, 0x49, 0x49, 0x7A),
    "H": (0x7F, 0x08, 0x08, 0x08, 0x7F), "I": (0x00, 0x41, 0x7F, 0x41, 0x00),
    "J": (0x20, 0x40, 0x41, 0x3F, 0x01), "K": (0x7F, 0x08, 0x14, 0x22, 0x41),
    "L": (0x7F, 0x40, 0x40, 0x40, 0x40), "M": (0x7F, 0x02, 0x0C, 0x02, 0x7F),
    "N": (0x7F, 0x04, 0x08, 0x10, 0x7F), "O": (0x3E, 0x41, 0x41, 0x41, 0x3E),
    "P": (0x7F, 0x09, 0x09, 0x09, 0x06), "Q": (0x3E, 0x41, 0x51, 0x21, 0x5E),
    "R": (0x7F, 0x09, 0x19, 0x29, 0x46), "S": (0x46, 0x49, 0x49, 0x49, 0x31),
    "T": (0x01, 0x01, 0x7F, 0x01, 0x01), "U": (0x3F, 0x40, 0x40, 0x40, 0x3F),
    "V": (0x1F, 0x20, 0x40, 0x20, 0x1F), "W": (0x3F, 0x40, 0x38, 0x40, 0x3F),
    "X": (0x63, 0x14, 0x08, 0x14, 0x63), "Y": (0x07, 0x08, 0x70, 0x08, 0x07),
    "Z": (0x61, 0x51, 0x49, 0x45, 0x43), "[": (0x00, 0x7F, 0x41, 0x41, 0x00),
    "\\": (0x02, 0x04, 0x08, 0x10, 0x20), "]": (0x00, 0x41, 0x41, 0x7F, 0x00),
    "^": (0x04, 0x02, 0x01, 0x02, 0x04), "_": (0x40, 0x40, 0x40, 0x40, 0x40),
}
GLYPH_W, GLYPH_H = 5, 7


def text_bitmap(text, spacing=1):
    """Render text to a boolean array [row_from_top][column]."""
    cols = []
    for ch in text.upper():
        g = FONT5x7.get(ch, FONT5x7["?"])
        for c in g:
            cols.append([(c >> r) & 1 for r in range(GLYPH_H)])
        cols.extend([[0] * GLYPH_H] * spacing)
    if not cols:
        cols = [[0] * GLYPH_H]
    return np.array(cols, bool).T          # (7, n)


# --------------------------------------------------------------------------
# sprites -- the classic mau5head faces
# --------------------------------------------------------------------------
SPRITES = {
    "x_eyes": [
        "X.....X   X.....X",
        ".X...X.....X...X.",
        "..X.X.......X.X..",
        "...X.........X...",
        "..X.X.......X.X..",
        ".X...X.....X...X.",
        "X.....X   X.....X",
    ],
    "eyes": [
        ".XXXXX.....XXXXX.",
        "XXXXXXX...XXXXXXX",
        "XXXXXXX...XXXXXXX",
        "XXXXXXX...XXXXXXX",
        "XXXXXXX...XXXXXXX",
        "XXXXXXX...XXXXXXX",
        ".XXXXX.....XXXXX.",
    ],
    "wink": [
        ".XXXXX...........",
        "XXXXXXX..XXXXXXXX",
        "XXXXXXX...XXXXXX.",
        "XXXXXXX..........",
        "XXXXXXX..........",
        "XXXXXXX..........",
        ".XXXXX...........",
    ],
    "smile": [
        "X...............X",
        ".X.............X.",
        "..X...........X..",
        "...X.........X...",
        "....XX.....XX....",
        "......XXXXX......",
        ".................",
    ],
    "frown": [
        "......XXXXX......",
        "....XX.....XX....",
        "...X.........X...",
        "..X...........X..",
        ".X.............X.",
        "X...............X",
        ".................",
    ],
    "arrow_up": [
        "........X........",
        ".......XXX.......",
        "......XXXXX......",
        ".....XXXXXXX....."
        , "....XXXXXXXXX....",
        "......XXXXX......",
        "......XXXXX......",
    ],
    "arrow_right": [
        ".................",
        "....X............",
        "....XXX..........",
        "....XXXXXXXXXX...",
        "....XXX..........",
        "....X............",
        ".................",
    ],
    "heart": [
        "..XXX.....XXX....",
        ".XXXXX...XXXXX...",
        "XXXXXXX.XXXXXXX..",
        "XXXXXXXXXXXXXXX..",
        ".XXXXXXXXXXXXX...",
        "...XXXXXXXXX.....",
        ".....XXXXX.......",
    ],
    "skull": [
        "..XXXXXXXXXXX....",
        ".XXXXXXXXXXXXX...",
        "XX..XXXXXXX..XX..",
        "X....XXXXX....X..",
        "XX..XXXXXXX..XX..",
        ".XXXXX.X.XXXXX...",
        "..X.X.X.X.X.X....",
    ],
    "equals": [
        ".................",
        "XXXXXX.....XXXXXX",
        "XXXXXX.....XXXXXX",
        ".................",
        "XXXXXX.....XXXXXX",
        "XXXXXX.....XXXXXX",
        ".................",
    ],
}


def sprite_bitmap(name_or_rows):
    rows = SPRITES[name_or_rows] if isinstance(name_or_rows, str) else name_or_rows
    w = max(len(r) for r in rows)
    return np.array([[c not in ".  " for c in r.ljust(w)] for r in rows], bool)


# --------------------------------------------------------------------------
# beats
# --------------------------------------------------------------------------
class Beats:
    """A pre-computed beat list.  No live audio analysis -- shows are authored."""

    def __init__(self, times):
        self.times = np.asarray(sorted(float(t) for t in times), float)

    @classmethod
    def from_bpm(cls, bpm, offset=0.0, duration=600.0):
        step = 60.0 / float(bpm)
        n = int(duration / step) + 1
        return cls(offset + step * np.arange(n))

    @classmethod
    def from_file(cls, path):
        """One time in seconds per line, or a JSON list, or librosa output."""
        with open(path, "r", encoding="utf-8") as fh:
            txt = fh.read().strip()
        if txt.startswith("["):
            data = json.loads(txt)
            if data and isinstance(data[0], dict):
                data = [d.get("time", d.get("t")) for d in data]
            return cls(data)
        out = []
        for line in txt.splitlines():
            line = line.split("#")[0].strip().replace(",", " ")
            for tok in line.split():
                try:
                    out.append(float(tok))
                except ValueError:
                    pass
        return cls(out)

    @classmethod
    def from_audio(cls, path):
        """Optional convenience: librosa beat track, used offline only."""
        import librosa                              # not needed at showtime
        y, sr = librosa.load(path, mono=True)
        _tempo, frames = librosa.beat.beat_track(y=y, sr=sr)
        return cls(librosa.frames_to_time(frames, sr=sr))

    def gain_curve(self, swell=0.60, accent=0.50, floor=0.45, ceiling=1.7):
        """Per-frame master gain, centred on 1.0.

        A modern master is heavily limited -- for one of these tracks the
        loudness curve sits at 0.83 of full scale nearly all the time -- so
        multiplying by it just dims the whole show and barely moves.  What
        carries information is the DEVIATION from the local norm, and the
        onset punch on top.  Centring on 1.0 means quiet passages dip, hits
        push past full scale and clip white, and the average stays where the
        effects intended it.
        """
        n = max(len(self.energy) if self.energy is not None else 0,
                len(self.onset) if self.onset is not None else 0)
        if not n:
            return None
        g = np.ones(n, np.float32)
        if self.energy is not None and swell:
            e = self.energy.astype(np.float32) - float(np.median(self.energy))
            scale = float(np.percentile(np.abs(e), 90)) or 1.0
            g += swell * 0.5 * np.clip(e / scale, -1.5, 1.5)
        if self.onset is not None and accent:
            o = self.onset.astype(np.float32) - float(np.median(self.onset))
            g += accent * o
        return np.clip(g, floor, ceiling)

    def save(self, path):
        with open(path, "w", encoding="utf-8") as fh:
            fh.write("\n".join("%.4f" % t for t in self.times) + "\n")

    def index(self, t):
        return int(np.searchsorted(self.times, t, side="right") - 1)

    def since(self, t):
        """Seconds since the most recent beat (large number before the first)."""
        i = self.index(t)
        return 1e9 if i < 0 else t - self.times[i]

    def envelope(self, t, decay=0.18, floor=0.0):
        """1.0 on the beat, falling to ``floor`` over ``decay`` seconds."""
        d = self.since(t)
        if d >= 1e8:
            return floor
        return floor + (1.0 - floor) * math.exp(-d / max(decay, 1e-3))

    def phase(self, t):
        i = self.index(t)
        if i < 0 or i + 1 >= len(self.times):
            return 0.0
        a, b = self.times[i], self.times[i + 1]
        return (t - a) / max(b - a, 1e-6)


class Music:
    """The track, sampled at the show's frame rate.

    ``Beats`` alone only says *when* a beat is.  This adds the two continuous
    curves that make lights feel welded to the music rather than merely
    triggered by it: ``energy`` (how loud it is right now) and ``onset`` (how
    much is happening right now).  Both are 0..1 arrays with one entry per
    rendered frame, so looking one up is an array index -- no analysis at
    render time.
    """

    def __init__(self, beats, fps, energy=None, onset=None):
        self.beats = beats
        self.fps = float(fps)
        self.energy = None if energy is None else np.asarray(energy, np.float32)
        self.onset = None if onset is None else np.asarray(onset, np.float32)

    def _at(self, arr, t):
        if arr is None or not len(arr):
            return 1.0
        i = int(t * self.fps)
        return float(arr[0 if i < 0 else (len(arr) - 1 if i >= len(arr) else i)])

    def energy_at(self, t):
        return self._at(self.energy, t)

    def onset_at(self, t):
        return self._at(self.onset, t)

    def gain_curve(self, swell=0.60, accent=0.50, floor=0.45, ceiling=1.7):
        """Per-frame master gain, centred on 1.0.

        A modern master is heavily limited -- for one of these tracks the
        loudness curve sits at 0.83 of full scale nearly all the time -- so
        multiplying by it just dims the whole show and barely moves.  What
        carries information is the DEVIATION from the local norm, and the
        onset punch on top.  Centring on 1.0 means quiet passages dip, hits
        push past full scale and clip white, and the average stays where the
        effects intended it.
        """
        n = max(len(self.energy) if self.energy is not None else 0,
                len(self.onset) if self.onset is not None else 0)
        if not n:
            return None
        g = np.ones(n, np.float32)
        if self.energy is not None and swell:
            e = self.energy.astype(np.float32) - float(np.median(self.energy))
            scale = float(np.percentile(np.abs(e), 90)) or 1.0
            g += swell * 0.5 * np.clip(e / scale, -1.5, 1.5)
        if self.onset is not None and accent:
            o = self.onset.astype(np.float32) - float(np.median(self.onset))
            g += accent * o
        return np.clip(g, floor, ceiling)

    def save(self, path):
        np.savez_compressed(path, beats=self.beats.times, fps=self.fps,
                            energy=self.energy if self.energy is not None else [],
                            onset=self.onset if self.onset is not None else [])

    @classmethod
    def load(cls, path):
        z = np.load(path)
        e = z["energy"]; o = z["onset"]
        return cls(Beats(z["beats"]), float(z["fps"]),
                   e if len(e) else None, o if len(o) else None)


# --------------------------------------------------------------------------
# base
# --------------------------------------------------------------------------
class Effect:
    """Fill a (n_total, 3) uint8 buffer for one frame."""

    def __init__(self, helmet, brightness=1.0, beats=None, beat_decay=0.18,
                 beat_floor=0.25, origin=0.0, music=None, drive=None,
                 drive_floor=0.35):
        self.h = helmet
        self.brightness = brightness
        self.beats = beats
        self.beat_decay = beat_decay
        self.beat_floor = beat_floor
        # origin is the time this effect's own motion starts from.  Set it to a
        # downbeat and a one-bar sweep crosses the face exactly on the beat
        # instead of wherever t=0 happened to leave it.
        self.origin = float(origin)
        self.music = music
        self.drive = drive              # None | "energy" | "onset"
        self.drive_floor = drive_floor

    def phase(self, t, period):
        """Position in 0..1 through one ``period``, measured from the origin."""
        return ((t - self.origin) / float(period)) % 1.0 if period else 0.0

    def level(self, t):
        b = self.brightness
        if self.beats is not None:
            b *= self.beats.envelope(t, self.beat_decay, self.beat_floor)
        if self.music is not None and self.drive:
            v = (self.music.energy_at(t) if self.drive == "energy"
                 else self.music.onset_at(t))
            b *= self.drive_floor + (1.0 - self.drive_floor) * v
        return b

    def render(self, buf, i, t):
        raise NotImplementedError

    # -- target helpers ---------------------------------------------------
    def target(self, what):
        h = self.h
        if isinstance(what, np.ndarray):
            return what
        if what in ("all", None):
            return np.arange(h.n_total)
        if what == "shell":
            return np.arange(h.n_shell)
        if what == "ears":
            return np.concatenate([np.arange(f.start, f.end) for f in h.fixtures
                                   if f.kind in ("ring", "blade")])
        if what == "rims":
            return np.concatenate([np.arange(f.start, f.end) for f in h.fixtures
                                   if f.kind == "ring"])
        if what == "blades":
            return np.concatenate([np.arange(f.start, f.end) for f in h.fixtures
                                   if f.kind == "blade"])
        if what == "visor":
            return np.concatenate([np.arange(f.start, f.end) for f in h.fixtures
                                   if f.kind == "arc"])
        f = h.fixture(what)
        return np.arange(f.start, f.end)


class Solid(Effect):
    def __init__(self, helmet, color=(255, 255, 255), where="all", **kw):
        super().__init__(helmet, **kw)
        self.color = color
        self.idx = self.target(where)

    def render(self, buf, i, t):
        _paint(buf, self.idx, 1.0, self.color, self.level(t))


class Strobe(Effect):
    def __init__(self, helmet, color=(255, 255, 255), hz=8.0, duty=0.25,
                 where="all", **kw):
        super().__init__(helmet, **kw)
        self.color, self.hz, self.duty = color, hz, duty
        self.idx = self.target(where)

    def render(self, buf, i, t):
        if self.phase(t, 1.0 / self.hz) < self.duty:
            _paint(buf, self.idx, 1.0, self.color, self.level(t))


# --------------------------------------------------------------------------
# grid effects -- sprites and text on the 22 x 68 unwrapped shell
# --------------------------------------------------------------------------
class GridEffect(Effect):
    """Base for anything that draws into the unwrapped grid.

    ``self.canvas`` is (rows, channels) float in 0..1, row 0 at the BOTTOM to
    match ``helmet.grid``; drawing helpers take row-from-top coordinates
    because that is how sprites and glyphs are written.
    """

    def __init__(self, helmet, color=(255, 255, 255), **kw):
        super().__init__(helmet, **kw)
        self.color = color
        self.canvas = np.zeros((helmet.rows, helmet.channels), np.float32)
        self._live = helmet.grid >= 0
        self._idx = helmet.grid[self._live]

    def clear(self):
        self.canvas[:] = 0.0

    def blit(self, bitmap, col, row_from_top, wrap=True, level=1.0):
        """Stamp a boolean bitmap; columns wrap around the sphere."""
        bh, bw = bitmap.shape
        rows, cols = self.canvas.shape
        for r in range(bh):
            y = rows - 1 - (row_from_top + r)          # flip to bottom-up rows
            if not 0 <= y < rows:
                continue
            xs = (np.arange(bw) + int(round(col)))
            xs = xs % cols if wrap else xs
            keep = (xs >= 0) & (xs < cols) & bitmap[r]
            if keep.any():
                np.maximum.at(self.canvas[y], xs[keep], level)

    def flush(self, buf, level=1.0):
        _paint(buf, self._idx, self.canvas[self._live], self.color, level)


class Sprite(GridEffect):
    """A static face, optionally blinking on the beat."""

    def __init__(self, helmet, sprite="x_eyes", col=None, row_from_top=3,
                 color=(255, 40, 0), **kw):
        super().__init__(helmet, color=color, **kw)
        self.bmp = sprite_bitmap(sprite)
        # faces sit on the front of the head: azimuth 0 is channel 0
        self.col = -int(round((self.bmp.shape[1] - 1) / 2.0)) if col is None else col
        self.row = row_from_top

    def render(self, buf, i, t):
        self.clear()
        self.blit(self.bmp, self.col, self.row)
        self.flush(buf, self.level(t))


class SpriteFlipbook(GridEffect):
    """Cycle a list of sprites -- one per beat, or at a fixed rate."""

    def __init__(self, helmet, sprites=("eyes", "wink"), fps=2.0, col=None,
                 row_from_top=3, color=(255, 40, 0), **kw):
        super().__init__(helmet, color=color, **kw)
        self.bmps = [sprite_bitmap(s) for s in sprites]
        self.rate = fps
        self.col = col
        self.row = row_from_top

    def render(self, buf, i, t):
        n = (self.beats.index(t) if self.beats is not None
             else int((t - self.origin) * self.rate))
        bmp = self.bmps[n % len(self.bmps)]
        col = -int(round((bmp.shape[1] - 1) / 2.0)) if self.col is None else self.col
        self.clear()
        self.blit(bmp, col, self.row)
        self.flush(buf, self.brightness)


class ScrollText(GridEffect):
    """Scrolling text that wraps right around the sphere."""

    def __init__(self, helmet, text="DEADMAU5", speed=18.0, row_from_top=3,
                 color=(0, 200, 255), direction=-1, **kw):
        super().__init__(helmet, color=color, **kw)
        self.bmp = text_bitmap(text)
        self.speed = speed             # channels per second
        self.row = row_from_top
        self.dir = direction

    def render(self, buf, i, t):
        self.clear()
        w = self.bmp.shape[1]
        span = max(w, self.h.channels)
        x = (self.dir * self.speed * (t - self.origin)) % span
        self.blit(self.bmp, x, self.row)
        if w < self.h.channels:        # repeat so the band is continuous
            self.blit(self.bmp, x - span, self.row)
        self.flush(buf, self.level(t))


class Matrix(GridEffect):
    """Falling columns, because it reads well on a 22-row grid."""

    def __init__(self, helmet, color=(0, 255, 90), density=0.12, speed=14.0,
                 tail=6, **kw):
        super().__init__(helmet, color=color, **kw)
        self.speed, self.tail, self.density = speed, tail, density
        self.rng = np.random.default_rng(7)
        self.offset = self.rng.random(helmet.channels) * helmet.rows
        self.active = self.rng.random(helmet.channels) < 0.5

    def render(self, buf, i, t):
        self.clear()
        rows = self.h.rows
        head = (self.offset + (t - self.origin) * self.speed) % (rows + self.tail + 4)
        for c in range(self.h.channels):
            if not self.active[c]:
                continue
            for k in range(self.tail):
                y = int(head[c]) - k
                if 0 <= y < rows:
                    self.canvas[rows - 1 - y, c] = max(
                        self.canvas[rows - 1 - y, c], 1.0 - k / self.tail)
        self.flush(buf, self.level(t))


# --------------------------------------------------------------------------
# geometry effects -- azimuth / elevation
# --------------------------------------------------------------------------
class AzimuthSweep(Effect):
    """A band of light travelling around the head."""

    def __init__(self, helmet, color=(0, 180, 255), period=2.0, width_deg=40.0,
                 direction=1, **kw):
        super().__init__(helmet, **kw)
        self.color, self.period, self.width, self.dir = color, period, width_deg, direction
        self.az = helmet.az
        self.idx = np.arange(helmet.n_shell)

    def render(self, buf, i, t):
        centre = (self.dir * 360.0 * self.phase(t, self.period)) % 360.0
        d = np.abs((self.az - centre + 180.0) % 360.0 - 180.0)
        v = np.clip(1.0 - d / self.width, 0, 1) ** 2
        _paint(buf, self.idx, v, self.color, self.level(t))


class ElevationPulse(Effect):
    """A ring rising or falling over the sphere."""

    def __init__(self, helmet, color=(255, 0, 160), period=1.5, width_deg=14.0,
                 direction=1, **kw):
        super().__init__(helmet, **kw)
        self.color, self.period, self.width, self.dir = color, period, width_deg, direction
        self.el = helmet.elev
        self.lo, self.hi = self.el.min() - width_deg, self.el.max() + width_deg
        self.idx = np.arange(helmet.n_shell)

    def render(self, buf, i, t):
        span = self.hi - self.lo
        p = self.phase(t, self.period)
        centre = self.lo + span * (p if self.dir > 0 else 1 - p)
        v = np.clip(1.0 - np.abs(self.el - centre) / self.width, 0, 1) ** 2
        _paint(buf, self.idx, v, self.color, self.level(t))


class Rainbow(Effect):
    """Hue mapped to azimuth so the seam lands at the back."""

    def __init__(self, helmet, period=6.0, saturation=1.0, where="shell", **kw):
        super().__init__(helmet, **kw)
        self.period, self.sat = period, saturation
        self.idx = self.target(where)
        az = np.zeros(helmet.n_total)
        az[:helmet.n_shell] = helmet.az
        for f in helmet.fixtures:                # accessories follow their x/y
            p = helmet.xyz[f.slice]
            az[f.slice] = np.degrees(np.arctan2(p[:, 0], -p[:, 1])) % 360.0
        self.az = az[self.idx] / 360.0

    def render(self, buf, i, t):
        hue = ((self.az + (t - self.origin) / self.period) % 1.0 * 255).astype(np.int32)
        rgb = _HUE_LUT[hue]
        if self.sat < 1.0:
            rgb = rgb + (255.0 - rgb) * (1.0 - self.sat)
        out = np.clip(rgb * self.level(t), 0, 255)
        cur = buf[self.idx].astype(np.float32)
        buf[self.idx] = np.maximum(cur, out).astype(np.uint8)


class Swell(Effect):
    """Elevation-graded breath: brightest at the crown, darkest at the chin.

    The quiet-section workhorse -- it reads as the head being lit from inside
    rather than as an effect running on it.
    """

    def __init__(self, helmet, color=(0, 120, 255), period=6.0, floor=0.25,
                 invert=False, **kw):
        super().__init__(helmet, **kw)
        self.color, self.period, self.floor = color, period, floor
        el = helmet.elev
        g = (el - el.min()) / max(float(np.ptp(el)), 1e-6)
        self.grade = (1.0 - g) if invert else g
        self.idx = np.arange(helmet.n_shell)

    def render(self, buf, i, t):
        breath = self.floor + (1 - self.floor) * (
            0.5 - 0.5 * math.cos(2 * math.pi * self.phase(t, self.period)))
        v = np.clip(self.grade * breath + 0.04, 0, 1) ** 1.6
        _paint(buf, self.idx, v, self.color, self.level(t))


class Twinkle(Effect):
    def __init__(self, helmet, color=(255, 255, 255), density=0.05, decay=0.35,
                 where="shell", seed=3, **kw):
        super().__init__(helmet, **kw)
        self.color, self.density, self.decay = color, density, decay
        self.idx = self.target(where)
        self.rng = np.random.default_rng(seed)
        self.state = np.zeros(len(self.idx), np.float32)
        self._last_t = None

    def render(self, buf, i, t):
        dt = (1.0 / self.h.fps) if self._last_t is None else max(t - self._last_t, 0.0)
        self._last_t = t
        self.state *= math.exp(-dt / max(self.decay, 1e-3))
        n = max(1, int(len(self.idx) * self.density / 8))
        pick = self.rng.integers(0, len(self.idx), n)
        self.state[pick] = 1.0
        _paint(buf, self.idx, self.state, self.color, self.level(t))


# --------------------------------------------------------------------------
# 1D strip effects -- ear blades, ear rims, visor pipes
# --------------------------------------------------------------------------
class StripEffect(Effect):
    """Treat a set of fixtures as independent 1D strips."""

    def __init__(self, helmet, where="blades", **kw):
        super().__init__(helmet, **kw)
        if isinstance(where, str) and where in ("blades", "rims", "visor", "ears"):
            kinds = {"blades": ("blade",), "rims": ("ring",),
                     "visor": ("arc",), "ears": ("blade", "ring")}[where]
            self.strips = [f for f in helmet.fixtures if f.kind in kinds]
        elif isinstance(where, (list, tuple)):
            self.strips = [helmet.fixture(w) for w in where]
        else:
            self.strips = [helmet.fixture(where)]


class BladeChase(StripEffect):
    """Lightsaber wipe: a lit head running the length of each tube."""

    def __init__(self, helmet, color=(255, 0, 120), period=0.8, tail=0.35,
                 where="blades", bounce=True, **kw):
        super().__init__(helmet, where=where, **kw)
        self.color, self.period, self.tail, self.bounce = color, period, tail, bounce

    def render(self, buf, i, t):
        lvl = self.level(t)
        for f in self.strips:
            u = np.linspace(0.0, 1.0, f.count)
            p = self.phase(t, self.period)
            if self.bounce:
                p = 2 * p if p < 0.5 else 2 * (1 - p)
            v = np.clip(1.0 - np.abs(u - p) / self.tail, 0, 1) ** 2
            _paint(buf, f.slice, v, self.color, lvl)


class BladeIgnite(StripEffect):
    """Fill each tube from the hub outwards, then hold -- one per beat."""

    def __init__(self, helmet, color=(180, 255, 255), rise=0.25, hold=0.5,
                 where="blades", **kw):
        super().__init__(helmet, where=where, **kw)
        self.color, self.rise, self.hold = color, rise, hold

    def render(self, buf, i, t):
        since = (self.beats.since(t) if self.beats is not None
                 else ((t - self.origin) % (self.rise + self.hold)))
        if since > self.rise + self.hold:
            return
        frac = min(1.0, since / max(self.rise, 1e-3))
        fade = 1.0 if since <= self.rise else max(
            0.0, 1.0 - (since - self.rise) / max(self.hold, 1e-3))
        for f in self.strips:
            u = np.abs(np.linspace(-1.0, 1.0, f.count))    # 0 at the middle
            v = (u <= frac).astype(np.float32)
            _paint(buf, f.slice, v, self.color, self.brightness * fade)


class RimSpin(StripEffect):
    """Comet running around each ear rim."""

    def __init__(self, helmet, color=(255, 200, 0), period=1.6, tail=0.3,
                 direction=1, **kw):
        super().__init__(helmet, where="rims", **kw)
        self.color, self.period, self.tail, self.dir = color, period, tail, direction

    def render(self, buf, i, t):
        lvl = self.level(t)
        for f in self.strips:
            u = np.linspace(0.0, 1.0, f.count, endpoint=False)
            p = (self.dir * self.phase(t, self.period)) % 1.0
            d = np.abs((u - p + 0.5) % 1.0 - 0.5)
            v = np.clip(1.0 - d / self.tail, 0, 1) ** 2
            _paint(buf, f.slice, v, self.color, lvl)


class VisorGlow(StripEffect):
    """Edge glow on the two light pipes, optionally breathing."""

    def __init__(self, helmet, color=(60, 120, 255), breathe=4.0, floor=0.25,
                 sweep=None, **kw):
        super().__init__(helmet, where="visor", **kw)
        self.color, self.breathe, self.floor, self.sweep = color, breathe, floor, sweep

    def render(self, buf, i, t):
        lvl = self.level(t)
        if self.breathe:
            lvl *= self.floor + (1 - self.floor) * (
                0.5 + 0.5 * math.sin(2 * math.pi * self.phase(t, self.breathe)))
        for f in self.strips:
            if self.sweep:
                u = np.linspace(0.0, 1.0, f.count)
                p = self.phase(t, self.sweep)
                v = np.clip(1.0 - np.abs(u - p) / 0.3, 0, 1)
            else:
                v = np.ones(f.count, np.float32)
            _paint(buf, f.slice, v, self.color, lvl)


# --------------------------------------------------------------------------
# composition
# --------------------------------------------------------------------------
class Cue:
    __slots__ = ("start", "end", "effect", "blend", "fade_in", "fade_out")

    def __init__(self, start, end, effect, blend="max", fade_in=0.0, fade_out=0.0):
        self.start, self.end, self.effect = float(start), float(end), effect
        self.blend, self.fade_in, self.fade_out = blend, fade_in, fade_out

    def gain(self, t):
        if not self.start <= t < self.end:
            return 0.0
        g = 1.0
        if self.fade_in:
            g = min(g, (t - self.start) / self.fade_in)
        if self.fade_out:
            g = min(g, (self.end - t) / self.fade_out)
        return max(0.0, min(1.0, g))


class Timeline:
    """A show: cues on a clock, rendered to frames.

    ``music`` welds the whole show to the track.  Individual effects can ride
    the loudness and onset curves themselves, but stacking them with "max"
    blending flattens that out -- whichever effect is brightest wins, and the
    modulation disappears.  So the finished frame also gets a master gain:

        slow   loudness  ->  the helmet breathes with the track
        fast   onset     ->  every hit lands on the whole head at once

    ``swell`` and ``accent`` are how much of the range each one owns; 0 for
    either turns it off.
    """

    def __init__(self, helmet, fps=None, music=None, swell=0.60, accent=0.50):
        self.h = helmet
        self.fps = fps or helmet.fps
        self.cues = []
        self.music = music
        self._gain = music.gain_curve(swell, accent) if music is not None else None

    def gain(self, t):
        if self._gain is None:
            return 1.0
        i = int(t * self.fps)
        return float(self._gain[0 if i < 0 else
                                (len(self._gain) - 1 if i >= len(self._gain) else i)])

    def add(self, start, end, effect, blend="max", fade_in=0.0, fade_out=0.0):
        self.cues.append(Cue(start, end, effect, blend, fade_in, fade_out))
        return self

    @property
    def duration(self):
        return max([c.end for c in self.cues], default=0.0)

    def render_frame(self, i, t=None):
        t = i / self.fps if t is None else t
        buf = self.h.blank()
        for c in self.cues:
            g = c.gain(t)
            if g <= 0:
                continue
            if g >= 1.0:
                c.effect.render(buf, i, t)
            else:
                tmp = self.h.blank()
                c.effect.render(tmp, i, t)
                if c.blend == "add":
                    buf[:] = np.clip(buf.astype(np.int16)
                                     + (tmp.astype(np.float32) * g), 0, 255).astype(np.uint8)
                else:
                    buf[:] = np.maximum(buf, (tmp.astype(np.float32) * g).astype(np.uint8))
        m = self.gain(t)
        if abs(m - 1.0) > 0.002:
            buf[:] = np.clip(buf.astype(np.float32) * m, 0, 255).astype(np.uint8)
        return buf

    def frames(self, seconds=None):
        n = int(round((seconds if seconds is not None else self.duration) * self.fps))
        for i in range(n):
            yield self.render_frame(i)


def render(helmet, effect, seconds, fps=None):
    """Frames from a single effect or a plain callable ``f(buf, i, t)``."""
    fps = fps or helmet.fps
    n = int(round(seconds * fps))
    fn = effect.render if isinstance(effect, Effect) else effect
    for i in range(n):
        buf = helmet.blank()
        fn(buf, i, i / fps)
        yield buf


# --------------------------------------------------------------------------
# a ready-made demo show, used by mau5sim --demo and mau5build --demo
# --------------------------------------------------------------------------
def demo_show(helmet, duration=30.0, bpm=128.0):
    b = Beats.from_bpm(bpm, 0.0, duration + 5)
    tl = Timeline(helmet)
    q = duration / 4.0
    tl.add(0, q * 2, AzimuthSweep(helmet, (0, 160, 255), period=2.0, width_deg=45))
    tl.add(0, q * 2, VisorGlow(helmet, (30, 90, 255), breathe=3.0), fade_in=1.0)
    tl.add(0, q * 2, RimSpin(helmet, (255, 160, 0), period=1.6))
    tl.add(q, q * 3, Sprite(helmet, "x_eyes", color=(255, 30, 0), beats=b,
                            beat_decay=0.12, beat_floor=0.35))
    tl.add(q, q * 3, BladeChase(helmet, (255, 0, 120), period=0.7))
    tl.add(q * 2, q * 3.2, ElevationPulse(helmet, (180, 0, 255), period=1.2))
    tl.add(q * 2.5, q * 3.5, ScrollText(helmet, "MAU5HEAD", speed=22,
                                        color=(0, 255, 140)))
    tl.add(q * 3, duration, Rainbow(helmet, period=4.0))
    tl.add(q * 3, duration, BladeIgnite(helmet, (200, 255, 255), beats=b))
    tl.add(q * 3.6, duration, Strobe(helmet, (255, 255, 255), hz=10, duty=0.12,
                                     where="shell", brightness=0.9),
           fade_in=0.5)
    return tl


if __name__ == "__main__":
    import mau5cfg
    h = mau5cfg.load(quiet=True)
    tl = demo_show(h, 8.0)
    lit = 0
    for f in tl.frames(2.0):
        lit += int((f.any(axis=1)).sum())
    print("ok: %d LEDs, %d cues, %d lit-LED-frames in 2 s"
          % (h.n_total, len(tl.cues), lit))
    for name in sorted(SPRITES):
        b = sprite_bitmap(name)
        print("  sprite %-12s %dx%d" % (name, b.shape[1], b.shape[0]))
    print("  font glyphs: %d" % len(FONT5x7))
