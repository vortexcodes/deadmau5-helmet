#!/usr/bin/env python3
"""mau5preview -- see a preset without the helmet.

Draws the chain as the camera sees it: orthographic from the front,
each LED a soft additive blob, ears behind the head.  It deliberately
imitates the real thing's bloom, because the shell diffuses hard --
nine LEDs lit up half the sphere in the calibration photos -- and a
preview of crisp dots would flatter effects that will actually smear.

    python3 mau5preview.py --list
    python3 mau5preview.py text --text "HELLO" --seconds 6 --mp4 out.mp4
    python3 mau5preview.py --sheet            # every preset, one image
"""

from __future__ import annotations

import argparse
import os
import subprocess
import tempfile

import numpy as np
from PIL import Image, ImageDraw

import mau5engine as E

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 760, 620


def _project(h):
    """LED positions -> pixel coords, plus a per-LED blob radius."""
    x, y, z = h.px, h.py, h.depth        # across, up, toward viewer
    sx = x.min() - 60, x.max() + 60
    sy = y.min() - 60, y.max() + 60
    k = min(W / (sx[1] - sx[0]), H / (sy[1] - sy[0]))
    px = (x - (sx[0] + sx[1]) / 2) * k + W / 2
    py = H / 2 - (y - (sy[0] + sy[1]) / 2) * k
    # shell LEDs sit behind a diffusing print; ear tubes are in a
    # diffuser too.  Rims are bare edge-on strip, so they read tighter.
    rad = np.where(h.rims, 5.0, np.where(h.shell, 13.0, 10.0))
    return px, py, rad, z


def _kernels(radii):
    out = {}
    for r in np.unique(np.round(radii, 1)):
        n = int(r * 3) | 1
        a = np.arange(n) - n // 2
        gx, gy = np.meshgrid(a, a)
        d = np.hypot(gx, gy)
        out[float(r)] = np.clip(np.exp(-(d / (r * 0.55)) ** 2), 0, 1)
    return out


class Scene:
    def __init__(self, helmet):
        self.h = helmet
        self.px, self.py, self.rad, self.z = _project(helmet)
        self.kern = _kernels(self.rad)
        self.back = self._backdrop()

    def _backdrop(self):
        """Faint outlines so an unlit helmet is still legible."""
        im = Image.new("RGB", (W, H), (8, 8, 11))
        d = ImageDraw.Draw(im)
        for m, col in ((self.h.ear1, (26, 26, 32)), (self.h.ear2, (26, 26, 32)),
                       (self.h.shell, (20, 20, 26))):
            xs, ys = self.px[m], self.py[m]
            if not len(xs):
                continue
            cx, cy = xs.mean(), ys.mean()
            r = max(np.hypot(xs - cx, ys - cy).max(), 10)
            d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=col, width=2)
        return np.asarray(im, np.float32)

    def frame(self, rgb, gain=1.0):
        buf = self.back.copy()
        order = np.argsort(self.z)          # ears (behind) first
        for i in order:
            c = rgb[i]
            if c.max() < 3:
                continue
            r = float(round(self.rad[i], 1))
            k = self.kern[r]
            n = k.shape[0]
            x0, y0 = int(self.px[i]) - n // 2, int(self.py[i]) - n // 2
            x1, y1 = x0 + n, y0 + n
            kx0, ky0 = max(0, -x0), max(0, -y0)
            x0, y0 = max(0, x0), max(0, y0)
            x1, y1 = min(W, x1), min(H, y1)
            if x1 <= x0 or y1 <= y0:
                continue
            sub = k[ky0:ky0 + (y1 - y0), kx0:kx0 + (x1 - x0)]
            buf[y0:y1, x0:x1] += sub[:, :, None] * (c * gain)[None, None, :]
        return Image.fromarray(np.clip(buf, 0, 255).astype(np.uint8))


def render(preset, seconds=6.0, fps=24, music=None, gain=1.0):
    h = E.Helmet()
    sc = Scene(h)
    for i in range(int(seconds * fps)):
        t = i / fps
        yield sc.frame(preset.render(h, t, music), gain)


def to_mp4(frames, path, fps=24):
    tmp = tempfile.mkdtemp(prefix="mau5prev")
    n = 0
    for im in frames:
        im.save(os.path.join(tmp, "f%05d.png" % n)); n += 1
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                    "-framerate", str(fps), "-i", os.path.join(tmp, "f%05d.png"),
                    "-vf", "format=yuv420p", "-c:v", "libx264", "-crf", "20",
                    path], check=True)
    for f in os.listdir(tmp):
        os.remove(os.path.join(tmp, f))
    os.rmdir(tmp)
    return path, n


def sheet(path, t=1.7, cols=5):
    h = E.Helmet()
    sc = Scene(h)
    names = sorted(E.REGISTRY)
    tw, th = 300, 245
    rows = (len(names) + cols - 1) // cols
    out = Image.new("RGB", (cols * tw, rows * (th + 20)), (6, 6, 8))
    d = ImageDraw.Draw(out)
    for i, nm in enumerate(names):
        p = E.REGISTRY[nm]()
        tt = t if nm != "strobe" else 0.01
        im = sc.frame(p.render(h, tt)).resize((tw, th), Image.LANCZOS)
        x, y = (i % cols) * tw, (i // cols) * (th + 20)
        out.paste(im, (x, y))
        d.text((x + 8, y + th + 4), nm, fill=(190, 190, 205))
    out.save(path, quality=93)
    return path, len(names)


def reel(path, seconds=2.6, fps=24, names=None):
    """Every preset in turn, labelled -- the sheet shows what they look
    like, this shows what they do, which for half of them is the point."""
    import subprocess, tempfile
    h = E.Helmet()
    sc = Scene(h)
    names = names or sorted(E.REGISTRY)
    tmp = tempfile.mkdtemp(prefix="mau5reel")
    n = 0
    for nm in names:
        pr = E.make(nm)
        for i in range(int(seconds * fps)):
            im = sc.frame(pr.render(h, i / fps))
            d = ImageDraw.Draw(im)
            d.rectangle([0, H - 34, W, H], fill=(6, 6, 9))
            d.text((14, H - 25), nm, fill=(225, 225, 240))
            d.text((W - 92, H - 25), "%d/%d" % (names.index(nm) + 1, len(names)),
                   fill=(120, 120, 140))
            im.save(os.path.join(tmp, "f%05d.png" % n))
            n += 1
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                    "-framerate", str(fps), "-i", os.path.join(tmp, "f%05d.png"),
                    "-vf", "format=yuv420p", "-c:v", "libx264", "-crf", "20",
                    path], check=True)
    for f in os.listdir(tmp):
        os.remove(os.path.join(tmp, f))
    os.rmdir(tmp)
    return path, n


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter,
                                 epilog=__doc__)
    ap.add_argument("preset", nargs="?")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--sheet", nargs="?", const=os.path.join(HERE, "data", "cal", "presets.jpg"))
    ap.add_argument("--reel", nargs="?", const=os.path.join(HERE, "data", "cal", "preset_reel.mp4"),
                    help="every preset in motion, labelled")
    ap.add_argument("--seconds", type=float, default=6.0)
    ap.add_argument("--fps", type=int, default=24)
    ap.add_argument("--mp4")
    ap.add_argument("--png")
    ap.add_argument("--text")
    ap.add_argument("--sprite")
    a, rest = ap.parse_known_args()

    if a.list:
        for nm in sorted(E.REGISTRY):
            print("  %-11s %s" % (nm, E.REGISTRY[nm].params))
        return
    if a.sheet:
        p, n = sheet(a.sheet)
        print("wrote %s (%d presets)" % (p, n)); return
    if a.reel:
        p, n = reel(a.reel, a.seconds if a.seconds != 6.0 else 2.6, a.fps)
        print("wrote %s (%d frames)" % (p, n)); return
    if not a.preset:
        ap.error("give a preset name, --list or --sheet")

    kw = {}
    if a.text: kw["text"] = a.text
    if a.sprite: kw["sprite"] = a.sprite
    pr = E.make(a.preset, **kw)
    if a.png:
        h = E.Helmet(); Scene(h).frame(pr.render(h, a.seconds)).save(a.png)
        print("wrote", a.png); return
    out = a.mp4 or os.path.join(HERE, "data", "cal", "preview_%s.mp4" % a.preset)
    p, n = to_mp4(render(pr, a.seconds, a.fps), out, a.fps)
    print("wrote %s (%d frames)" % (p, n))


if __name__ == "__main__":
    main()
