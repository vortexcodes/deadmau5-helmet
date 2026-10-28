#!/usr/bin/env python3
"""mau5engine -- presets that know where they are on the helmet.

The old effect library addressed a tidy 68x22 grid wrapped round a whole
sphere.  That helmet does not exist: there are 399 LEDs on the front
shell in strips of wildly uneven length, holes where the eyes and mouth
are, and 224 more on two ears that the CAD never knew about.  Indexing
by row and column against that produces nonsense.

So presets here are written against *geometry* instead.  Every LED
carries its position, the direction it faces, how far along its own
strip it sits, and which part of the helmet it belongs to.  An effect
asks questions like "how far round the face is this" or "is this on an
ear rim", and works regardless of how the strips were actually cut.

Coordinates, millimetres, origin at the centre of the head:
    +x right (as the audience sees it), +y up, +z toward the face.
    fa   front azimuth, -90 at the left edge of the face to +90 at the
         right, 0 straight ahead -- the natural axis for sweeps.
    el   elevation, about -40 at the chin to +76 at the crown.
    u    0..1 along the LED's own strip, for chases that run with the
         wiring rather than across it.
"""

from __future__ import annotations

import math
import os

import numpy as np

import mau5map
from mau5fx import FONT5x7, SPRITES

HERE = os.path.dirname(os.path.abspath(__file__))


# ----------------------------------------------------------------------
class Helmet:
    """The map, as arrays, plus the masks presets actually ask for."""

    def __init__(self, path=None):
        rows = mau5map.load(path) if path else mau5map.load()
        self.n = len(rows)
        self.rows = rows
        self.xyz = np.array([[r["x"], r["y"], r["z"]] for r in rows], float)
        self.az = np.array([r["az_deg"] for r in rows], float)
        self.el = np.array([r["elev_deg"] for r in rows], float)
        self.u = np.array([r["u"] for r in rows], float)
        self.group = np.array([r["group"] for r in rows], int)
        self.region = np.array([r["region"] for r in rows], dtype=object)
        # front azimuth: -180..180 with 0 straight ahead
        self.fa = ((self.az + 180.0) % 360.0) - 180.0

        self.shell = self.region == "shell"
        self.ear1 = np.array([r.startswith("ear1") for r in self.region])
        self.ear2 = np.array([r.startswith("ear2") for r in self.region])
        self.ears = self.ear1 | self.ear2
        self.tubes = np.array([r.endswith("tubes") for r in self.region])
        self.rims = np.array([r.endswith("rim") for r in self.region])

        # normalised 0..1 helpers, computed per part so an effect that
        # sweeps "left to right" does so across the whole helmet
        # Orthographic screen coordinates, in mm.  Glyphs are laid out
        # against these rather than against azimuth: a letter drawn on
        # an azimuth grid bends round the sphere and stops being a
        # letter, whereas one drawn flat reads correctly to anybody
        # standing in front of the helmet, which is the whole point.
        # +z is up in this frame and the face looks along -y, so the
        # screen axes are x across and z up, with -y as depth.
        self.px = self.xyz[:, 0]
        self.py = self.xyz[:, 2]
        self.depth = -self.xyz[:, 1]
        self.nx = self._norm(self.xyz[:, 0])
        self.ny = self._norm(self.xyz[:, 2])
        self.nfa = np.clip((self.fa + 90.0) / 180.0, 0, 1)
        sh_el = self.el[self.shell]
        self.nel = np.clip((self.el - sh_el.min()) / (np.ptp(sh_el) or 1), 0, 1)

    @staticmethod
    def _norm(a):
        lo, hi = a.min(), a.max()
        return (a - lo) / ((hi - lo) or 1)

    def mask(self, *names):
        """mask('shell','rims') -> boolean array for those regions."""
        m = np.zeros(self.n, bool)
        for nm in names:
            m |= getattr(self, nm)
        return m


def hsv(h, s=1.0, v=1.0):
    """Vectorised HSV -> RGB in 0..255.  h wraps."""
    h = np.asarray(h, float) % 1.0
    s = np.broadcast_to(np.asarray(s, float), h.shape)
    v = np.broadcast_to(np.asarray(v, float), h.shape)
    i = np.floor(h * 6.0).astype(int)
    f = h * 6.0 - i
    p, q, t = v * (1 - s), v * (1 - f * s), v * (1 - (1 - f) * s)
    i = i % 6
    r = np.choose(i, [v, q, p, p, t, v])
    g = np.choose(i, [t, v, v, q, p, p])
    b = np.choose(i, [p, p, t, v, v, q])
    return np.stack([r, g, b], -1) * 255.0


# ----------------------------------------------------------------------
class Preset:
    """A named, parameterised effect.

    render() returns an (n,3) float array in 0..255.  It must not clamp
    for power -- that is the guard's job, applied once on the wire, so
    that a preset stays honest about what it is asking for.
    """

    name = "preset"
    params: dict = {}

    # Where a preset's main colour is not called "color".  A UI offering
    # one swatch should not have to know which presets spell it
    # differently, but the Python API stays strict so a typo in code is
    # still an error.
    COLOUR_ALIAS = {"a": True, "lo": True}

    def __init__(self, **kw):
        self.p = dict(self.params)
        bad = set(kw) - set(self.p)
        if bad:
            raise ValueError("%s has no parameter %s" % (self.name, sorted(bad)))
        self.p.update(kw)

    @classmethod
    def accepts(cls, kw):
        """Filter a loose dict down to what this preset takes.

        For the HTTP boundary, where a generic control surface sends the
        same payload to every preset.  A colour offered to a preset that
        names its colour differently is redirected rather than dropped.
        """
        out = {}
        for k, v in (kw or {}).items():
            if isinstance(v, list):
                v = tuple(v)
            if k in cls.params:
                out[k] = v
            elif k == "color":
                for alt in ("a", "lo", "color"):
                    if alt in cls.params and alt not in out:
                        out[alt] = v
                        break
        return out

    @classmethod
    def spec(cls):
        """Describe the parameters so a UI can build controls for them."""
        out = []
        for k, v in cls.params.items():
            if isinstance(v, (tuple, list)) and len(v) == 3 and all(
                    isinstance(c, (int, float)) for c in v):
                out.append({"name": k, "kind": "color", "value": list(v)})
            elif isinstance(v, bool):
                out.append({"name": k, "kind": "bool", "value": v})
            elif isinstance(v, (int, float)):
                lo = 0.0 if v >= 0 else v * 3
                hi = max(v * 4.0, v + 1.0) if v >= 0 else 0.0
                out.append({"name": k, "kind": "number", "value": v,
                            "min": round(lo, 3), "max": round(hi, 3),
                            "step": round(max((hi - lo) / 100.0, 0.001), 4)})
            elif isinstance(v, str):
                out.append({"name": k, "kind": "text", "value": v})
        return out

    def render(self, h, t, music=None):
        raise NotImplementedError

    def __repr__(self):
        return "<%s %s>" % (self.name, self.p)


def _beat(music, t, default=0.0):
    """Music drive in 0..1, or a steady default when there is no track."""
    if music is None:
        return default
    return float(music.level_at(t))


# ----------------------------------------------------------------------
# The library.  Each one is deliberately small; interest comes from
# layering them in a show, not from any single preset doing everything.
# ----------------------------------------------------------------------

class Solid(Preset):
    name = "solid"
    params = {"color": (255, 40, 0), "parts": ("shell", "ears")}

    def render(self, h, t, music=None):
        out = np.zeros((h.n, 3))
        out[h.mask(*self.p["parts"])] = self.p["color"]
        return out


class Breathe(Preset):
    name = "breathe"
    params = {"color": (255, 60, 0), "period": 6.0, "floor": 0.12}

    def render(self, h, t, music=None):
        k = self.p["floor"] + (1 - self.p["floor"]) * (
            0.5 - 0.5 * math.cos(2 * math.pi * t / self.p["period"]))
        return np.tile(np.array(self.p["color"]) * k, (h.n, 1))


class RainbowSweep(Preset):
    name = "rainbow"
    params = {"period": 8.0, "wrap": 1.0, "axis": "fa", "sat": 1.0}

    def render(self, h, t, music=None):
        a = {"fa": h.nfa, "el": h.nel, "x": h.nx, "y": h.ny,
             "u": h.u}[self.p["axis"]]
        return hsv(a * self.p["wrap"] - t / self.p["period"], self.p["sat"], 1.0)


class Scanner(Preset):
    """A bar that sweeps across the face and back."""
    name = "scanner"
    params = {"color": (0, 220, 255), "period": 2.4, "width": 0.22,
              "bounce": True}

    def render(self, h, t, music=None):
        ph = (t / self.p["period"]) % 1.0
        pos = (1 - abs(2 * ph - 1)) if self.p["bounce"] else ph
        d = np.abs(h.nfa - pos)
        k = np.clip(1.0 - d / self.p["width"], 0, 1) ** 2
        return k[:, None] * np.array(self.p["color"])


class Wipe(Preset):
    name = "wipe"
    params = {"a": (255, 0, 80), "b": (0, 60, 255), "period": 4.0,
              "axis": "el", "soft": 0.12}

    def render(self, h, t, music=None):
        v = {"fa": h.nfa, "el": h.nel, "x": h.nx, "y": h.ny}[self.p["axis"]]
        edge = (t / self.p["period"]) % 1.0
        k = np.clip((v - edge) / self.p["soft"] + 0.5, 0, 1)
        return (k[:, None] * np.array(self.p["b"])
                + (1 - k)[:, None] * np.array(self.p["a"]))


class Strobe(Preset):
    name = "strobe"
    params = {"color": (255, 255, 255), "hz": 8.0, "duty": 0.18}

    def render(self, h, t, music=None):
        on = ((t * self.p["hz"]) % 1.0) < self.p["duty"]
        return np.tile(np.array(self.p["color"]) * (1.0 if on else 0.0), (h.n, 1))


class Twinkle(Preset):
    """Frame-rate independent: each LED's phase is a fixed function of
    its index, so the look does not change with the render fps."""
    name = "twinkle"
    params = {"color": (255, 230, 180), "density": 0.18, "period": 2.2}

    def render(self, h, t, music=None):
        idx = np.arange(h.n)
        seed = (np.sin(idx * 12.9898) * 43758.5453) % 1.0
        ph = (t / self.p["period"] + seed) % 1.0
        k = np.clip(np.sin(ph * math.pi) ** 8, 0, 1)
        k *= (seed < self.p["density"] + 0.5 * (1 - self.p["density"]))
        return k[:, None] * np.array(self.p["color"])


class Comet(Preset):
    """Runs along the chain itself -- follows the wiring, not the shape."""
    name = "comet"
    params = {"color": (255, 120, 0), "period": 3.0, "tail": 0.16}

    def render(self, h, t, music=None):
        head = (t / self.p["period"]) % 1.0
        pos = np.arange(h.n) / h.n
        d = (head - pos) % 1.0
        k = np.exp(-d / self.p["tail"])
        return k[:, None] * np.array(self.p["color"])


class Ripple(Preset):
    name = "ripple"
    params = {"color": (0, 200, 255), "period": 2.6, "width": 0.14,
              "origin": (0.0, 40.0, 173.0)}

    def render(self, h, t, music=None):
        o = np.array(self.p["origin"], float)
        r = np.linalg.norm(h.xyz - o, axis=1)
        r = r / (r.max() or 1)
        ph = (t / self.p["period"]) % 1.0
        k = np.clip(1 - np.abs(r - ph) / self.p["width"], 0, 1) ** 2
        return k[:, None] * np.array(self.p["color"])


class Plasma(Preset):
    name = "plasma"
    params = {"speed": 0.35, "scale": 2.4, "sat": 0.95}

    def render(self, h, t, music=None):
        s = self.p["scale"]
        v = (np.sin(h.nfa * s * math.pi + t * self.p["speed"] * 2)
             + np.sin(h.nel * s * math.pi * 1.3 - t * self.p["speed"] * 1.7)
             + np.sin((h.nfa + h.nel) * s * math.pi * 0.8 + t * self.p["speed"]))
        return hsv(v / 6.0 + 0.5, self.p["sat"], 1.0)


class Fire(Preset):
    name = "fire"
    params = {"speed": 1.1, "cool": 0.55}

    def render(self, h, t, music=None):
        idx = np.arange(h.n)
        n1 = np.sin(h.nfa * 11.0 + t * self.p["speed"] * 3.1 + idx * 0.07)
        n2 = np.sin(h.nel * 7.0 - t * self.p["speed"] * 2.3)
        heat = np.clip(0.5 + 0.5 * (n1 * 0.6 + n2 * 0.4), 0, 1)
        heat *= np.clip(1.15 - h.nel * self.p["cool"], 0, 1.15)
        r = np.clip(heat * 2.2, 0, 1)
        g = np.clip(heat * 1.4 - 0.35, 0, 1)
        b = np.clip(heat * 1.2 - 0.85, 0, 1)
        return np.stack([r, g, b], -1) * 255.0


class EarSpin(Preset):
    """Chase round each ear rim, shell held on a dim bed."""
    name = "earspin"
    params = {"color": (255, 0, 160), "bed": (20, 0, 40), "period": 1.6,
              "width": 0.22}

    def render(self, h, t, music=None):
        out = np.tile(np.array(self.p["bed"], float), (h.n, 1))
        ph = (t / self.p["period"]) % 1.0
        for m in (h.ear1 & h.rims, h.ear2 & h.rims):
            if not m.any():
                continue
            d = np.abs(((h.u[m] - ph + 0.5) % 1.0) - 0.5)
            k = np.clip(1 - d / self.p["width"], 0, 1) ** 2
            out[m] = k[:, None] * np.array(self.p["color"])
        return out


class TubePulse(Preset):
    name = "tubepulse"
    params = {"color": (0, 255, 200), "period": 1.2, "shell": (0, 12, 18)}

    def render(self, h, t, music=None):
        out = np.tile(np.array(self.p["shell"], float), (h.n, 1))
        k = 0.5 - 0.5 * math.cos(2 * math.pi * t / self.p["period"])
        out[h.tubes] = np.array(self.p["color"]) * (0.25 + 0.75 * k)
        return out


class Police(Preset):
    name = "police"
    params = {"hz": 2.5}

    def render(self, h, t, music=None):
        on = int(t * self.p["hz"]) % 2
        out = np.zeros((h.n, 3))
        left, right = h.fa < 0, h.fa >= 0
        out[left] = (255, 0, 0) if on else (0, 0, 0)
        out[right] = (0, 0, 255) if not on else (0, 0, 0)
        return out


class Equaliser(Preset):
    """Bars per azimuth column, height driven by the music."""
    name = "eq"
    params = {"bands": 12, "lo": (0, 80, 255), "hi": (255, 0, 120)}

    def render(self, h, t, music=None):
        nb = self.p["bands"]
        band = np.clip((h.nfa * nb).astype(int), 0, nb - 1)
        if music is not None and getattr(music, "bands", None) is not None:
            amp = music.bands_at(t, nb)
        else:
            amp = 0.5 + 0.5 * np.sin(t * 2.0 + np.arange(nb) * 0.9)
        lvl = amp[band]
        k = (h.nel <= lvl).astype(float)
        col = (np.array(self.p["lo"])[None, :] * (1 - h.nel)[:, None]
               + np.array(self.p["hi"])[None, :] * h.nel[:, None])
        return k[:, None] * col


class BeatPulse(Preset):
    name = "beatpulse"
    params = {"color": (255, 30, 0), "floor": 0.10}

    def render(self, h, t, music=None):
        k = self.p["floor"] + (1 - self.p["floor"]) * _beat(music, t, 0.5)
        return np.tile(np.array(self.p["color"]) * k, (h.n, 1))


# ----------------------------------------------------------------------
# Text and sprites.
#
# The shell is not a screen.  It is a patch of sphere with holes in it,
# and the strips that survive are different lengths.  So glyphs are
# rasterised into a small bitmap and then *sampled* by each LED's own
# position on the face, rather than blitted to a grid that does not
# exist.  LEDs that fall in a hole simply never sample a lit pixel.
# ----------------------------------------------------------------------

def _text_bitmap(text, spacing=1):
    """5x7 glyphs laid side by side -> (7, w) bool array."""
    cols = []
    for ch in text.upper():
        g = FONT5x7.get(ch, FONT5x7.get("?", (0, 0, 0, 0, 0)))
        for c in g:
            cols.append([(c >> r) & 1 for r in range(7)])
        cols.extend([[0] * 7] * spacing)
    if not cols:
        cols = [[0] * 7]
    return np.array(cols, bool).T          # (7, w)


# A 5x7 glyph held still on the dome gives 35 cells, and the LEDs are
# not spread evenly enough to fill them -- cells that happen to contain
# no LED drop out and the digit stops being readable.  Scrolling text
# survives that because the eye integrates over time; a held digit does
# not.  So digits get their own 3x5 face, where each cell is big enough
# to be certain of catching LEDs.
DIGIT3x5 = {
    "0": ("###", "# #", "# #", "# #", "###"),
    "1": (" # ", "## ", " # ", " # ", "###"),
    "2": ("###", "  #", "###", "#  ", "###"),
    "3": ("###", "  #", "###", "  #", "###"),
    "4": ("# #", "# #", "###", "  #", "  #"),
    "5": ("###", "#  ", "###", "  #", "###"),
    "6": ("###", "#  ", "###", "# #", "###"),
    "7": ("###", "  #", "  #", "  #", "  #"),
    "8": ("###", "# #", "###", "# #", "###"),
    "9": ("###", "# #", "###", "  #", "###"),
}


def _digit_bitmap(ch):
    rows = DIGIT3x5.get(ch, DIGIT3x5["0"])
    return np.array([[c != " " for c in r] for r in rows], bool)


def _sprite_bitmap(name):
    rows = SPRITES[name]
    return np.array([[c != "." for c in r] for r in rows], bool)


class TextScroll(Preset):
    """Scrolling text across the face, laid out flat so it reads."""
    name = "text"
    # The band is where the LEDs actually are: below py~28 is the visor
    # cutout and there is nothing to light.  7 rows over 28..145 mm puts
    # one glyph row per strip pitch, which is the finest the hardware
    # can resolve -- about 14-20 columns across, so two or three
    # characters are legible at once and the rest has to scroll.
    params = {"text": "DEADMAU5", "color": (255, 160, 0), "bg": (0, 0, 0),
              "speed": 70.0, "y_lo": 28.0, "y_hi": 145.0,
              "cell": 16.7, "loop": True, "gap": 6}

    def render(self, h, t, music=None):
        bm = _text_bitmap(self.p["text"], spacing=1)
        rows, w = bm.shape
        if self.p["loop"]:
            bm = np.concatenate([bm, np.zeros((rows, self.p["gap"]), bool)], 1)
            w = bm.shape[1]
        out = np.tile(np.array(self.p["bg"], float), (h.n, 1))

        lo, hi = self.p["y_lo"], self.p["y_hi"]
        ry = (hi - h.py) / max(hi - lo, 1e-6) * rows
        rx = h.px / self.p["cell"] + t * self.p["speed"] / self.p["cell"]

        r = np.floor(ry).astype(int)
        c = np.floor(rx).astype(int)
        if self.p["loop"]:
            c = c % w
            ok = (r >= 0) & (r < rows) & h.shell
        else:
            ok = (r >= 0) & (r < rows) & (c >= 0) & (c < w) & h.shell
            c = np.clip(c, 0, w - 1)
        lit = np.zeros(h.n, bool)
        lit[ok] = bm[r[ok], c[ok]]
        out[lit] = self.p["color"]
        return out


class SpriteShow(Preset):
    """One of the built-in faces, held on the front of the helmet."""
    name = "sprite"
    params = {"sprite": "smile", "color": (0, 255, 255), "bg": (0, 0, 0),
              "y_lo": 20.0, "y_hi": 160.0, "x_half": 150.0, "blink": 0.0}

    def render(self, h, t, music=None):
        bm = _sprite_bitmap(self.p["sprite"])
        rows, w = bm.shape
        out = np.tile(np.array(self.p["bg"], float), (h.n, 1))
        if self.p["blink"] and ((t * self.p["blink"]) % 1.0) > 0.5:
            return out
        lo, hi = self.p["y_lo"], self.p["y_hi"]
        ry = (hi - h.py) / max(hi - lo, 1e-6) * rows
        rx = (h.px + self.p["x_half"]) / (2 * self.p["x_half"]) * w
        r, c = np.floor(ry).astype(int), np.floor(rx).astype(int)
        ok = (r >= 0) & (r < rows) & (c >= 0) & (c < w) & h.shell
        lit = np.zeros(h.n, bool)
        lit[ok] = bm[r[ok], c[ok]]
        out[lit] = self.p["color"]
        return out


class Eyes(Preset):
    """Two eyes that track left and right, with the odd blink."""
    name = "eyes"
    params = {"color": (0, 255, 255), "period": 5.0, "size": 58.0,
              "y": 95.0, "spread": 78.0, "blink_every": 4.0}

    def render(self, h, t, music=None):
        out = np.zeros((h.n, 3))
        look = math.sin(2 * math.pi * t / self.p["period"]) * 30.0
        blink = (t % self.p["blink_every"]) < 0.18
        for side in (-1, 1):
            cx = side * self.p["spread"] + look
            d = np.hypot(h.px - cx, (h.py - self.p["y"]) * 1.25)
            k = np.clip(1 - d / self.p["size"], 0, 1) ** 0.6
            if blink:
                k *= np.clip(1 - np.abs(h.py - self.p["y"]) / 10.0, 0, 1)
            out += k[:, None] * np.array(self.p["color"])
        out[~h.shell] = 0
        return np.clip(out, 0, 255)


class Matrix(Preset):
    """Drops falling down the face, one per azimuth column."""
    name = "matrix"
    params = {"color": (0, 255, 70), "columns": 24, "speed": 0.55,
              "tail": 0.30}

    def render(self, h, t, music=None):
        nc = self.p["columns"]
        col = np.clip((h.nfa * nc).astype(int), 0, nc - 1)
        seed = (np.sin(np.arange(nc) * 78.233) * 43758.5453) % 1.0
        head = (t * self.p["speed"] * (0.6 + seed) + seed) % 1.4 - 0.2
        d = (1.0 - h.nel) - head[col]
        k = np.where(d >= 0, np.exp(-d / self.p["tail"]), 0.0)
        out = k[:, None] * np.array(self.p["color"])
        out[~h.shell] = 0
        return out



# ----------------------------------------------------------------------
# More presets.  Several of these deliberately use the ears as a
# separate instrument from the shell, because on this helmet they are:
# different strips, different diffusion, and three times the per-LED
# power allowance.
# ----------------------------------------------------------------------

class Spiral(Preset):
    name = "spiral"
    params = {"period": 3.0, "arms": 3, "sat": 1.0, "tight": 1.6}

    def render(self, h, t, music=None):
        ang = np.arctan2(h.py - 30.0, h.px) / (2 * math.pi)
        rad = np.hypot(h.px, h.py - 30.0) / 260.0
        v = ang * self.p["arms"] + rad * self.p["tight"] - t / self.p["period"]
        return hsv(v, self.p["sat"], 1.0)


class Pinwheel(Preset):
    name = "pinwheel"
    params = {"period": 2.0, "sectors": 6, "color": (255, 255, 255),
              "bg": (0, 0, 0)}

    def render(self, h, t, music=None):
        ang = (np.arctan2(h.py - 30.0, h.px) / (2 * math.pi)
               - t / self.p["period"]) % 1.0
        on = (ang * self.p["sectors"]) % 1.0 < 0.5
        out = np.tile(np.array(self.p["bg"], float), (h.n, 1))
        out[on] = self.p["color"]
        return out


class Heartbeat(Preset):
    """Two thumps then a rest, like an actual heartbeat."""
    name = "heartbeat"
    params = {"color": (255, 0, 40), "bpm": 62.0, "floor": 0.06}

    def render(self, h, t, music=None):
        ph = (t * self.p["bpm"] / 60.0) % 1.0
        k = 0.0
        for at, amp in ((0.00, 1.0), (0.18, 0.62)):
            d = ph - at
            if 0 <= d < 0.14:
                k = max(k, amp * math.exp(-d / 0.045))
        k = self.p["floor"] + (1 - self.p["floor"]) * k
        return np.tile(np.array(self.p["color"]) * k, (h.n, 1))


class Confetti(Preset):
    """Random pops that fade, colour per pop."""
    name = "confetti"
    params = {"rate": 14.0, "fade": 0.55, "sat": 0.9}

    def render(self, h, t, music=None):
        idx = np.arange(h.n)
        out = np.zeros((h.n, 3))
        step = 1.0 / max(self.p["rate"], 0.1)
        k = int(t / step)
        for back in range(6):                       # overlapping pops
            kk = k - back
            if kk < 0:
                continue
            r = (math.sin(kk * 91.7) * 43758.5453) % 1.0
            who = int(r * h.n)
            age = t - kk * step
            amp = math.exp(-age / self.p["fade"])
            if amp < 0.01:
                continue
            lo, hi = max(0, who - 2), min(h.n, who + 3)
            col = hsv(np.array([r]), self.p["sat"], 1.0)[0]
            out[lo:hi] = np.maximum(out[lo:hi], col * amp)
        return out


class Lightning(Preset):
    """Mostly dark, with the occasional double flash."""
    name = "lightning"
    params = {"color": (210, 225, 255), "every": 3.2, "bed": (0, 0, 6)}

    def render(self, h, t, music=None):
        out = np.tile(np.array(self.p["bed"], float), (h.n, 1))
        ph = t % self.p["every"]
        k = 0.0
        for at, amp in ((0.0, 1.0), (0.11, 0.55), (0.17, 0.8)):
            d = ph - at
            if 0 <= d < 0.09:
                k = max(k, amp * (1 - d / 0.09))
        if k > 0:
            seed = int(t / self.p["every"])
            side = (math.sin(seed * 12.9) * 43758.5) % 1.0
            m = (h.nfa > side - 0.42) & (h.nfa < side + 0.42)
            out[m] = np.array(self.p["color"]) * k
        return out


class Wave(Preset):
    """A travelling sine band -- reads well on a curved surface."""
    name = "wave"
    params = {"color": (0, 160, 255), "period": 2.2, "length": 0.55,
              "axis": "fa", "floor": 0.0}

    def render(self, h, t, music=None):
        a = {"fa": h.nfa, "el": h.nel, "u": h.u, "x": h.nx}[self.p["axis"]]
        v = np.sin(2 * math.pi * (a / self.p["length"] - t / self.p["period"]))
        k = np.clip(self.p["floor"] + (1 - self.p["floor"]) * (0.5 + 0.5 * v), 0, 1)
        return k[:, None] * np.array(self.p["color"])


class Gradient(Preset):
    name = "gradient"
    params = {"a": (255, 0, 90), "b": (0, 120, 255), "axis": "el",
              "period": 0.0}

    def render(self, h, t, music=None):
        v = {"fa": h.nfa, "el": h.nel, "x": h.nx, "y": h.ny}[self.p["axis"]]
        if self.p["period"]:
            v = (v + t / self.p["period"]) % 1.0
        return (v[:, None] * np.array(self.p["b"])
                + (1 - v)[:, None] * np.array(self.p["a"]))


class Chase(Preset):
    """Runs up each strip at once -- follows the wiring within a strip
    but stays in step across them, which the comet does not."""
    name = "chase"
    params = {"color": (255, 200, 0), "period": 1.4, "width": 0.22,
              "reverse": False}

    def render(self, h, t, music=None):
        ph = (t / self.p["period"]) % 1.0
        u = 1.0 - h.u if self.p["reverse"] else h.u
        d = np.abs(((u - ph + 0.5) % 1.0) - 0.5)
        k = np.clip(1 - d / self.p["width"], 0, 1) ** 2
        return k[:, None] * np.array(self.p["color"])


class VuMeter(Preset):
    """Fills from the chin upward with the music."""
    name = "vu"
    params = {"lo": (0, 255, 80), "hi": (255, 30, 0), "peak": True,
              "decay": 1.6}

    def __init__(self, **kw):
        super().__init__(**kw)
        self._peak, self._last = 0.0, None

    def render(self, h, t, music=None):
        lvl = _beat(music, t, 0.5 + 0.5 * math.sin(t * 2.3))
        if self._last is None or t < self._last:
            self._peak = lvl
        else:
            self._peak = max(lvl, self._peak - (t - self._last) / self.p["decay"])
        self._last = t
        col = (np.array(self.p["lo"])[None, :] * (1 - h.nel)[:, None]
               + np.array(self.p["hi"])[None, :] * h.nel[:, None])
        out = col * (h.nel <= lvl)[:, None]
        if self.p["peak"]:
            band = np.abs(h.nel - self._peak) < 0.035
            out[band] = (255, 255, 255)
        return out


class Sparkle(Preset):
    """A bed colour with glitter that lands on the beat."""
    name = "sparkle"
    params = {"bed": (40, 0, 60), "glitter": (255, 255, 255),
              "density": 0.10, "rate": 7.0}

    def render(self, h, t, music=None):
        out = np.tile(np.array(self.p["bed"], float), (h.n, 1))
        drive = _beat(music, t, 1.0)
        k = int(t * self.p["rate"])
        r = (np.sin(np.arange(h.n) * 12.9898 + k * 7.13) * 43758.5453) % 1.0
        m = r < self.p["density"] * (0.35 + 0.65 * drive)
        out[m] = self.p["glitter"]
        return out


class Countdown(Preset):
    """Big digits on the face, then everything.  Uses the 3x5 face so
    each cell is large enough to be sure of catching LEDs."""
    name = "countdown"
    params = {"from": 5, "step": 1.0, "color": (255, 40, 0),
              # keep all five rows above the sparse band just over the
              # visor, or the bottom stroke of a 2 drops out
              "flash": (255, 255, 255), "y_hi": 166.0, "y_lo": 48.0,
              # 130 rather than 50: at 50 the digit occupies 100 mm of
              # a 340 mm face and reads as a smudge near the crown.
              # Past about 135 the outer column is foreshortened more
              # than twice and the digit starts to look wrong.
              "x_half": 130.0, "loop": 2.0}

    def render(self, h, t, music=None):
        # Repeat rather than finish.  A one-shot preset leaves the
        # helmet dark for as long as it is selected, which is
        # indistinguishable from a controller that has stopped working
        # -- and it was in fact mistaken for one.  loop is the pause
        # after the flash before it counts again; set it to 0 for a
        # single run.
        span = self.p["from"] * self.p["step"] + 0.8
        if self.p["loop"] > 0:
            t = t % (span + self.p["loop"])
        n = int(self.p["from"]) - int(t / self.p["step"])
        if n <= 0:
            k = max(0.0, 1.0 - (t - self.p["from"] * self.p["step"]) / 0.8)
            return np.tile(np.array(self.p["flash"]) * k, (h.n, 1))
        bm = _digit_bitmap(str(n)[-1])
        rows, w = bm.shape
        out = np.zeros((h.n, 3))
        hi, lo, xh = self.p["y_hi"], self.p["y_lo"], self.p["x_half"]
        ry = (hi - h.py) / max(hi - lo, 1e-6) * rows
        rx = (h.px + xh) / (2.0 * xh) * w
        r, c = np.floor(ry).astype(int), np.floor(rx).astype(int)
        m = (r >= 0) & (r < rows) & (c >= 0) & (c < w) & h.shell
        lit = np.zeros(h.n, bool)
        lit[m] = bm[r[m], c[m]]
        out[lit] = self.p["color"]
        return out


class Split(Preset):
    """Two presets at once: one on the shell, one on the ears.

    The ears are a different instrument -- different strips, different
    diffusion, three times the per-LED power allowance -- so letting
    them run their own effect is usually better than stretching one
    across both.
    """
    name = "split"
    # default the ears to something that uses their tubes -- earspin
    # only lights the 36 rim LEDs and reads as almost nothing beside a
    # full-shell effect.
    params = {"shell": "plasma", "ears": "chase",
              "shell_color": (255, 60, 0), "ear_color": (0, 220, 255)}

    def __init__(self, **kw):
        super().__init__(**kw)
        self._a = make(self.p["shell"],
                       **REGISTRY[self.p["shell"]].accepts(
                           {"color": self.p["shell_color"]}))
        self._b = make(self.p["ears"],
                       **REGISTRY[self.p["ears"]].accepts(
                           {"color": self.p["ear_color"]}))

    def render(self, h, t, music=None):
        out = np.zeros((h.n, 3))
        out[h.shell] = self._a.render(h, t, music)[h.shell]
        out[h.ears] = self._b.render(h, t, music)[h.ears]
        return out



# ----------------------------------------------------------------------
# Alignment.
#
# Every effect here is written against mapped positions, so an LED whose
# mapped position is wrong will be wrong in all of them, in the same way,
# and you will never find it by watching a plasma.  A single straight bar
# swept slowly across the helmet makes it obvious: the bar is only
# straight if the map is right, and a pixel that lights early or late
# stands out from its neighbours immediately.
# ----------------------------------------------------------------------

class AlignBar(Preset):
    """A hard-edged bar swept along one axis, for checking the map.

    Deliberately hard-edged and thin.  A soft bar hides exactly the
    error this is looking for.
    """
    name = "alignbar"
    params = {"axis": "y", "period": 14.0, "thickness": 14.0,
              "color": (255, 255, 255), "edge": (255, 0, 0),
              "bounce": True, "hold": 0.0, "grid": 0.0,
              "grid_color": (0, 40, 80)}

    def render(self, h, t, music=None):
        v = {"y": h.py, "x": h.px, "z": h.depth}[self.p["axis"]]
        lo, hi = float(v.min()), float(v.max())
        if self.p["hold"]:
            pos = lo + (hi - lo) * float(self.p["hold"])
        else:
            ph = (t / self.p["period"]) % 1.0
            if self.p["bounce"]:
                ph = 1.0 - abs(2 * ph - 1)
            pos = lo + (hi - lo) * ph

        out = np.zeros((h.n, 3))
        if self.p["grid"]:
            # faint rulings at a fixed pitch, so you can see how far out
            # a stray pixel is rather than only that it is out
            g = self.p["grid"]
            near = np.abs((v / g) - np.round(v / g)) * g < 1.2
            out[near] = self.p["grid_color"]

        d = np.abs(v - pos)
        half = self.p["thickness"] / 2.0
        out[d <= half] = self.p["color"]
        # the leading and trailing millimetre in another colour: a pixel
        # sitting on the edge of the bar reads as a tint, not a guess
        out[(d > half * 0.62) & (d <= half)] = self.p["edge"]
        return out


class StripId(Preset):
    """Colour every strip differently, so a stray pixel can be traced
    back to the run it belongs to."""
    name = "stripid"
    params = {"sat": 1.0, "value": 1.0, "cycle": 7}

    def render(self, h, t, music=None):
        g = np.where(h.group >= 0, h.group, 68 + np.arange(h.n) % 4)
        return hsv((g % self.p["cycle"]) / float(self.p["cycle"]),
                   self.p["sat"], self.p["value"])


REGISTRY = {}
for _c in (Solid, Breathe, RainbowSweep, Scanner, Wipe, Strobe, Twinkle,
           Comet, Ripple, Plasma, Fire, EarSpin, TubePulse, Police,
           Equaliser, BeatPulse, TextScroll, SpriteShow, Eyes, Matrix,
           Spiral, Pinwheel, Heartbeat, Confetti, Lightning, Wave,
           Gradient, Chase, VuMeter, Sparkle, Countdown, Split,
           AlignBar, StripId):
    REGISTRY[_c.name] = _c


# ----------------------------------------------------------------------
# Locking a preset to the beat.
#
# A scanner with a 2.4 s period against a 128 bpm track completes
# 1.28 cycles per bar.  It is never wrong and never once lands with the
# music, and no amount of colour choice rescues it: the eye reads the
# drift long before it reads the palette.  Quantise the period to a
# whole number of beats and take the phase from the beat grid instead
# of the clock, and the same preset lands every bar.
#
# Only presets that are exactly periodic in their cycle parameter can
# be treated this way -- a preset carrying state across the cycle
# boundary would stutter each time the phase wrapped.  Which ones those
# are is measured, not assumed: t_lockable_presets re-derives this
# table by comparing render(t) with render(t + period).
#
# name -> (parameter, unit, cycles of the parameter per visual cycle)
LOCKABLE = {
    "alignbar":  ("period", "s", 1.0),
    "breathe":   ("period", "s", 1.0),
    "chase":     ("period", "s", 1.0),
    "comet":     ("period", "s", 1.0),
    "earspin":   ("period", "s", 1.0),
    "heartbeat": ("bpm", "bpm", 1.0),
    "pinwheel":  ("period", "s", 1.0),
    "police":    ("hz", "hz", 2.0),     # a full red/blue swap is two flashes
    "rainbow":   ("period", "s", 1.0),
    "ripple":    ("period", "s", 1.0),
    "scanner":   ("period", "s", 1.0),
    "spiral":    ("period", "s", 1.0),
    "stripid":   ("cycle", "s", 1.0),
    "strobe":    ("hz", "hz", 1.0),
    "tubepulse": ("period", "s", 1.0),
    "twinkle":   ("period", "s", 1.0),
    "wave":      ("period", "s", 1.0),
    "wipe":      ("period", "s", 1.0),
}

# Cycle lengths worth snapping to, in beats.  Sixteenths at the bottom
# for strobes, eight bars at the top for a slow wipe across a
# breakdown.  Powers of two only: this is four-to-the-floor music, and
# a three-beat cycle lands on the bar once every three bars, which
# reads as a mistake rather than as a triplet.
DIVISIONS = (0.25, 0.5, 1.0, 2.0, 4.0, 8.0, 16.0, 32.0)


def cycle_seconds(name, params):
    """How long one visual cycle of this preset lasts, or None."""
    ent = LOCKABLE.get(name)
    if ent is None:
        return None
    key, unit, mul = ent
    v = params.get(key, REGISTRY[name].params.get(key))
    try:
        v = float(v)
    except (TypeError, ValueError):
        return None
    if v <= 0:
        return None
    base = v if unit == "s" else (1.0 / v if unit == "hz" else 60.0 / v)
    return base * mul


def lock_time(music, name, params, t):
    """The time to hand render() so the cycle lands on the beat grid.

    The preset keeps its own period parameter and never learns about
    the music; it is simply given a phase rather than a clock.  Returns
    t unchanged when there is nothing to lock to.
    """
    per = cycle_seconds(name, params)
    if music is None or per is None:
        return t, None
    spb = 60.0 / max(getattr(music, "bpm", 0.0) or 0.0, 1e-6)
    want = per / spb
    beats = min(DIVISIONS, key=lambda d: abs(math.log(d / want)))
    phase = (music.beat_index(t) % beats) / beats
    return phase * per, beats


def make(name, **kw):
    if name not in REGISTRY:
        raise SystemExit("no preset %r.  Known: %s"
                         % (name, ", ".join(sorted(REGISTRY))))
    return REGISTRY[name](**kw)


if __name__ == "__main__":
    h = Helmet()
    print("helmet: %d leds" % h.n)
    print("  shell %d  ear1 %d  ear2 %d  tubes %d  rims %d"
          % (h.shell.sum(), h.ear1.sum(), h.ear2.sum(),
             h.tubes.sum(), h.rims.sum()))
    print("  fa  %.1f .. %.1f   el %.1f .. %.1f"
          % (h.fa.min(), h.fa.max(), h.el.min(), h.el.max()))
    print("\n%d presets:" % len(REGISTRY))
    for nm in sorted(REGISTRY):
        p = REGISTRY[nm]()
        out = p.render(h, 1.234)
        assert out.shape == (h.n, 3), nm
        print("   %-11s peak %3.0f  mean %5.1f  lit %3d%%"
              % (nm, out.max(), out.mean(), int(100 * (out.max(1) > 8).mean())))
