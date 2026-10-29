#!/usr/bin/env python3
"""mau5icon -- the app icon, drawn from the LED map itself.

An icon that is a picture of the thing is worth a little trouble, and
this one needs no artwork: 622 measured positions already describe
the silhouette.  Each LED is a dot, coloured by region, on the dark
the rest of the page uses, which makes the home-screen icon the same
object as the preview on the page.

    python3 mau5icon.py
"""

from __future__ import annotations

import argparse
import os

from PIL import Image, ImageDraw

import mau5engine as E

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "data", "offline")

BG = (11, 11, 16)
SHELL = (255, 92, 0)
EAR = (0, 150, 255)


def draw(size, pad_frac=0.10, maskable=False):
    h = E.Helmet()
    # A maskable icon is cropped to a circle by the launcher, so its
    # content has to sit inside the middle 80% or the ears lose their
    # tops on some phones.
    pad = size * (0.20 if maskable else pad_frac)
    im = Image.new("RGB", (size, size), BG)
    d = ImageDraw.Draw(im)
    x, y = h.px, h.py
    x0, x1, y0, y1 = x.min(), x.max(), y.min(), y.max()
    sc = min((size - 2 * pad) / (x1 - x0), (size - 2 * pad) / (y1 - y0))
    ox = (size - (x1 - x0) * sc) / 2.0
    oy = (size - (y1 - y0) * sc) / 2.0
    r = max(1.0, size / 150.0)
    for i in range(h.n):
        cx = ox + (x[i] - x0) * sc
        cy = size - (oy + (y[i] - y0) * sc)
        col = SHELL if h.shell[i] else EAR
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col)
    return im


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=OUT)
    a = ap.parse_args(argv)
    os.makedirs(a.out, exist_ok=True)
    made = []
    for size, name, mask in ((192, "i192.png", False), (512, "i512.png", False),
                             (512, "i512m.png", True)):
        p = os.path.join(a.out, name)
        draw(size, maskable=mask).save(p, optimize=True)
        made.append((name, os.path.getsize(p)))
        print("  %-10s %4d px  %5d bytes" % (name, size, os.path.getsize(p)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
