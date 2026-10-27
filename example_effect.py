#!/usr/bin/env python3
"""A worked example of the third input form: your own effect code.

Point either tool at any name in this file:

    ./mau5sim.py   --effect example_effect.py:show --audio track.wav
    ./mau5build.py build --name demo --effect example_effect.py:show \
                         --audio track.wav

Three shapes are accepted, and this file has one of each:

  ``show``    a factory ``f(helmet)`` returning a Timeline -- the usual one
  ``spin``    a plain ``f(buf, i, t)`` called once per frame
  ``Breathe`` an Effect subclass, for anything that needs state between frames

``buf`` is a ``(1406, 3)`` uint8 array: shell pixels first in wire order, then
the accessories.  Fill it however you like; it goes straight into an FSEQ
frame or a DDP packet.
"""

import numpy as np

import mau5fx


# -- 1. a Timeline: cues on a clock, which is how real shows get written -----
def show(h):
    beats = mau5fx.Beats.from_bpm(128, offset=0.0, duration=64)
    tl = mau5fx.Timeline(h)

    # intro: the head breathes, the visor edges glow
    tl.add(0, 16, Breathe(h, color=(0, 90, 200)), fade_out=2.0)
    tl.add(0, 16, mau5fx.VisorGlow(h, (40, 110, 255), breathe=4.0))

    # drop: face on, blades on the beat, rims spinning the other way
    tl.add(16, 40, mau5fx.Sprite(h, "x_eyes", color=(255, 30, 0), beats=beats,
                                 beat_decay=0.10, beat_floor=0.30))
    tl.add(16, 40, mau5fx.BladeIgnite(h, (200, 255, 255), beats=beats))
    tl.add(16, 40, mau5fx.RimSpin(h, (255, 150, 0), period=1.2, direction=-1))
    tl.add(24, 40, mau5fx.AzimuthSweep(h, (120, 0, 255), period=0.9375,  # 2 bars
                                       width_deg=30), blend="add")

    # outro: name in lights, then rainbow away
    tl.add(40, 52, mau5fx.ScrollText(h, "MAU5HEAD", speed=20,
                                     color=(0, 255, 150), row_from_top=7))
    tl.add(48, 64, mau5fx.Rainbow(h, period=5.0), fade_in=2.0)
    tl.add(48, 64, mau5fx.Twinkle(h, (255, 255, 255), density=0.08))
    return tl


# -- 2. a bare frame function ------------------------------------------------
def spin(buf, i, t):
    """Hue by azimuth, brightness by elevation. No helmet object needed --
    but note it has to recompute geometry, so prefer an Effect for real work."""
    n = len(buf)
    phase = (np.arange(n) / n + t * 0.25) % 1.0
    buf[:, 0] = (127 * (1 + np.sin(2 * np.pi * phase))).astype(np.uint8)
    buf[:, 1] = (127 * (1 + np.sin(2 * np.pi * phase + 2.1))).astype(np.uint8)
    buf[:, 2] = (127 * (1 + np.sin(2 * np.pi * phase + 4.2))).astype(np.uint8)


# -- 3. an Effect subclass, when you need state ------------------------------
class Breathe(mau5fx.Effect):
    """Elevation-graded swell, brightest at the crown, with a slow drift."""

    def __init__(self, helmet, color=(0, 120, 255), period=6.0, **kw):
        super().__init__(helmet, **kw)
        self.color, self.period = color, period
        el = helmet.elev
        self.grade = (el - el.min()) / max(float(np.ptp(el)), 1e-6)     # 0 at the chin
        self.idx = np.arange(helmet.n_shell)

    def render(self, buf, i, t):
        swell = 0.25 + 0.75 * (0.5 - 0.5 * np.cos(2 * np.pi * t / self.period))
        v = np.clip(self.grade * swell + 0.05, 0, 1) ** 1.6
        mau5fx._paint(buf, self.idx, v, self.color, self.level(t))
