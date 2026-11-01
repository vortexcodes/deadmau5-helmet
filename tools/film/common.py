"""common.py -- what the helmet's videos share: the look, the helmet drawing,
and running a show the way the helmet really runs it.

A show's frames go through the real power guard and a display gamma, the same
as tools/showkit/sheet.py, so the pictures aren't flattering. Colours and type
come from mau5film, which took them from the website.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, ROOT)
sys.path.insert(0, HERE)
os.chdir(ROOT)

import mau5engine as E  # noqa: E402
import mau5film as F  # noqa: E402
import mau5power  # noqa: E402
import mau5scene as SS  # noqa: E402
import mau5show  # noqa: E402

W, H, FPS = 1280, 720, 30
GAMMA = 2.0
SHOWS = os.path.join(ROOT, "shows")
OUT = os.path.join(ROOT, "data", "cal")


class HelmetView:
    """The helmet from the front, drawn on a dark sheet: CAD outline, LEDs as soft
    blobs where the map puts them. `box` is (x, y, w, h) on the 1280x720 frame."""

    def __init__(self, box, model, helmet, yaw=0.0, pitch=6.0):
        self.box = box
        x, y, w, h = box
        self.h = helmet
        s = min(w / 735.0, h / 610.0)
        v = F.View(yaw, pitch, s, cx=x + w / 2, cy=y + h / 2 - 4 * s)
        self.xy = v(model.new["xyz"])[:helmet.n]
        # shell LEDs sit behind a diffusing print; tubes in a diffuser; rims bare
        self.rad = np.where(helmet.rims, 3.2, np.where(helmet.shell, 6.6, 5.0)) * s / 0.72
        back = Image.new("RGB", (w, h), F.DARK)
        d = ImageDraw.Draw(back, "RGBA")
        off = np.array([x, y])
        vv = F.View(yaw, pitch, s, cx=w / 2, cy=h / 2 - 4 * s)
        F.lines(d, vv, model.V, model.silhouette(vv), (150, 160, 170, 46))
        F.lines(d, vv, model.V, model.crease, (150, 160, 170, 20))
        for seg in model.outline(vv):
            d.line(seg, fill=(150, 160, 170, 40), width=2)
        self.back = np.asarray(back, np.float32)
        self.off = off
        self._prep(w, h)

    def _prep(self, w, h):
        self.cells = []
        for i in range(self.h.n):
            r = float(self.rad[i])
            n = int(r * 3.2) | 1
            cx, cy = self.xy[i] - self.off
            x0, y0 = int(cx) - n // 2, int(cy) - n // 2
            ax = np.arange(n) + x0 - cx
            ay = np.arange(n) + y0 - cy
            gx, gy = np.meshgrid(ax, ay)
            k = np.exp(-(gx ** 2 + gy ** 2) / (r * 0.62) ** 2)
            xa, ya = max(x0, 0), max(y0, 0)
            xb, yb = min(x0 + n, w), min(y0 + n, h)
            if xb <= xa or yb <= ya:
                self.cells.append(None)
                continue
            self.cells.append((ya, yb, xa, xb, k[ya - y0:yb - y0, xa - x0:xb - x0, None].astype(np.float32)))

    def draw(self, canvas, rgb):
        """Add the frame's LEDs to a PIL image. `rgb` is what was sent to the LEDs."""
        x, y, w, h = self.box
        buf = self.back.copy()
        rgb = 255.0 * np.clip(np.asarray(rgb, np.float32) / 255.0, 0, 1) ** (1.0 / GAMMA)
        for i, cell in enumerate(self.cells):
            c = rgb[i]
            if cell is None or c.max() < 3:
                continue
            ya, yb, xa, xb, k = cell
            buf[ya:yb, xa:xb] += k * c * 1.15
        # the shell scatters light well past each LED, so add a wide faint glow
        im = Image.fromarray(np.clip(buf, 0, 255).astype(np.uint8))
        halo = np.asarray(im.filter(ImageFilter.GaussianBlur(11)), np.float32)
        im = Image.fromarray(np.clip(buf + np.maximum(halo - self.back, 0) * 0.55, 0, 255).astype(np.uint8))
        canvas.paste(im, (x, y))


class Song:
    """One compiled show, ready to render at any time through the guard."""

    def __init__(self, base, helmet=None):
        self.base = base
        self.show = json.load(open(os.path.join(SHOWS, base + ".json")))
        self.music = mau5show._music_for(self.show, os.path.join(SHOWS, base + ".mp3"))
        self.g = self.show["scenes"]["grid"]
        self.t0, self.spb = float(self.g["t0"]), float(self.g["spb"])
        self.holds = [(float(a), float(b)) for a, b in self.g.get("holds", ())]
        self.h = helmet or E.Helmet()
        self.sc = SS.Scenes(self.show["scenes"], self.h)
        self.guard = None
        self.now = None
        self.npz = np.load(os.path.join(SHOWS, base + ".analysis.npz"), allow_pickle=True)
        self.rate = float(self.npz["fps"])

    def t_of_beat(self, B):
        return self.t0 + B * self.spb + sum(b * self.spb for at, b in self.holds if B > at)

    def beat_of(self, t):
        """The inverse of t_of_beat: the song clock stops during a hold."""
        lo, hi = -8.0, 8.0 + (t - self.t0) / self.spb
        for _ in range(40):
            mid = (lo + hi) / 2
            if self.t_of_beat(mid) < t:
                lo = mid
            else:
                hi = mid
        return lo

    def t_of_bar(self, bar):
        return self.t_of_beat(4 * bar)

    def bands(self):
        return {k: self.npz["b_%s_e" % k] for k in ("bass", "mid", "high")}

    def punch(self):
        return {k: self.npz["b_%s_p" % k] for k in ("bass", "mid", "high")}

    def root(self, t_from, t_to):
        """The strongest pitch class over a stretch, so the stand-in sits near the song's key."""
        ch = self.npz["chroma"]
        bars = self.npz["bars"]
        i, j = np.searchsorted(bars, [t_from, t_to])
        pc = int(np.argmax(ch[max(i - 1, 0):max(j, i + 1)].sum(0)))
        return 40 + (pc - 4) % 12

    def warm(self, t, secs=4.0):
        """Start the guard a few seconds before `t`, so its first frame is settled
        and its heat is what the show put there rather than zero."""
        self.guard = mau5power.load(count=self.h.n)
        tt = max(t - secs, 0.0)
        while tt < t:
            f, g, _ = self.sc.frame(tt, self.music)
            self.guard.apply(f, now=tt, gain=g)
            tt += 1 / 30.0

    def frame(self, t):
        f, g, label = self.sc.frame(t, self.music)
        res, rep = self.guard.apply(f, now=t, gain=g)
        return np.asarray(res, float), label, rep


def strip(im, title, sub, sub2=""):
    """The caption strip, in the site's colours, with no numbering."""
    d = ImageDraw.Draw(im)
    y0 = H - F.FOOT
    d.rectangle([0, y0, W, H], fill=F.SURFACE)
    d.line([0, y0, W, y0], fill=F.RULE, width=1)
    d.text((28, y0 + 10), title, font=F.F_TITLE, fill=F.INK)
    d.text((28, y0 + 56 - (12 if sub2 else 0)), sub, font=fit(d, sub, W - 56), fill=F.INK2)
    if sub2:
        d.text((28, y0 + 66), sub2, font=fit(d, sub2, W - 56), fill=F.INK2)
    return im


def fit(d, text, width):
    f = F.F_BODY
    if d.textlength(text, font=f) > width:
        f = F.F_SMALL
    if d.textlength(text, font=f) > width:
        raise ValueError("caption too long: %r" % text)
    return f


def encoder(path, audio=None, crf=21):
    """An ffmpeg that takes JPEG frames on stdin. Returns the Popen."""
    cmd = ["ffmpeg", "-v", "error", "-y", "-f", "image2pipe", "-framerate", str(FPS),
           "-c:v", "mjpeg", "-i", "-"]
    if audio:
        cmd += ["-i", audio]
    cmd += ["-c:v", "libx264", "-preset", "slow", "-pix_fmt", "yuv420p", "-crf", str(crf),
            "-movflags", "+faststart"]
    if audio:
        cmd += ["-c:a", "aac", "-b:a", "160k", "-shortest"]
    cmd += [path]
    return subprocess.Popen(cmd, stdin=subprocess.PIPE)


def send(proc, im):
    im.save(proc.stdin, "JPEG", quality=93, subsampling=0)


def mux(video, audio, out):
    """A video and a track into one file, without re-encoding the picture. Stops at
    the shorter of the two."""
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", video, "-i", audio, "-map", "0:v", "-map", "1:a",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-shortest",
                    "-movflags", "+faststart", out], check=True)
