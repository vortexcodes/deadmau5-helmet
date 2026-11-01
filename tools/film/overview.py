#!/usr/bin/env python3
"""overview.py -- the one video: what every part of the helmet is, then all sixteen shows.

1080p, with the real songs. The walkthrough lights each part in turn on the real LED map.
The shows are the real scene engine and power guard, the same as reel.py. The result goes
to data/cal/, which git ignores: the songs never go in this repo.

    python3 tools/film/overview.py                 # data/cal/overview.mp4
    python3 tools/film/overview.py --sheet out.png # stills, to check the look
"""

from __future__ import annotations

import argparse
import math
import os
import subprocess
import tempfile
import time

import numpy as np

from common import E, F, ImageDraw, Image, ImageFilter, OUT, ROOT, SHOWS, Song, mau5power
import reel
import score

W, H, FPS = 1920, 1080, 30
PANEL_X, CAP_Y = 1300, 950
BG, PANEL = (11, 13, 16), (17, 20, 24)
AMBER, TEAL, ICE = (222, 170, 90), (70, 190, 170), (120, 170, 255)
TEXT, TEXT2, DIM, RULE = (232, 235, 238), (178, 185, 192), (130, 138, 146), (44, 50, 57)
GAMMA = 2.0
FADE = 0.25           # seconds the lights take to dip between songs
XFADE = 0.5           # seconds the music takes to cross
TARGET_RMS = 0.13

F_HUGE = F.font(112, True)
F_NAME = F.font(76, True)
F_NAME2 = F.font(52, True)
F_CAP = F.font(33)
F_BODY = F.font(31)
F_SMALL = F.font(25, weight="Medium")
F_TAG = F.font(27, True)


class View:
    """The helmet from the front. LEDs are soft blobs that average where they overlap,
    as light does in a diffuser, so the edge of the dome, where strips bunch up in this
    view, doesn't burn out into a line the real helmet doesn't have."""

    def __init__(self, box, model, helmet):
        self.box = box
        x, y, w, h = box
        self.h, self.w_, self.h_ = helmet, w, h
        s = min(w / 735.0, h / 625.0)
        self.xy = F.View(0.0, 6.0, s, cx=w / 2, cy=h / 2 - 2 * s)(model.new["xyz"])[:helmet.n]
        # the outline, drawn at twice the size and scaled down so its lines are smooth
        v2 = F.View(0.0, 6.0, 2 * s, cx=w, cy=h - 4 * s)
        back = Image.new("RGB", (w * 2, h * 2), BG)
        d = ImageDraw.Draw(back, "RGBA")
        F.lines(d, v2, model.V, model.silhouette(v2), (150, 160, 170, 62), width=2)
        for seg in model.outline(v2):
            d.line(seg, fill=(150, 160, 170, 60), width=3)
        self.back = np.asarray(back.resize((w, h), Image.LANCZOS), np.float32)
        rad = np.where(helmet.rims, 3.4, np.where(helmet.shell, 6.8, 5.2)) * s / 0.72
        self.cells = []
        dens = np.zeros((h, w), np.float32)
        for i in range(helmet.n):
            r = float(rad[i])
            n = int(r * 3.4) | 1
            cx, cy = self.xy[i]
            x0, y0 = int(cx) - n // 2, int(cy) - n // 2
            gx, gy = np.meshgrid(np.arange(n) + x0 - cx, np.arange(n) + y0 - cy)
            k = np.exp(-(gx ** 2 + gy ** 2) / (r * 0.62) ** 2)
            xa, ya, xb, yb = max(x0, 0), max(y0, 0), min(x0 + n, w), min(y0 + n, h)
            if xb <= xa or yb <= ya:
                self.cells.append(None)
                continue
            k = k[ya - y0:yb - y0, xa - x0:xb - x0].astype(np.float32)
            dens[ya:yb, xa:xb] += k
            self.cells.append((ya, yb, xa, xb, k[..., None]))
        self.norm = (1.0 / np.maximum(dens, 1.0))[..., None]

    def image(self, rgb):
        rgb = 255.0 * np.clip(np.asarray(rgb, np.float32) / 255.0, 0, 1) ** (1.0 / GAMMA)
        buf = np.zeros_like(self.back)
        for i, cell in enumerate(self.cells):
            c = rgb[i]
            if cell is None or c.max() < 3:
                continue
            ya, yb, xa, xb, k = cell
            buf[ya:yb, xa:xb] += k * c
        buf *= self.norm * 1.3
        # the shell scatters light past each LED: a wide faint glow, worked out small for speed
        small = Image.fromarray(np.clip(buf, 0, 255).astype(np.uint8)).resize((self.w_ // 4, self.h_ // 4), Image.BILINEAR)
        halo = small.filter(ImageFilter.GaussianBlur(5)).resize((self.w_, self.h_), Image.BICUBIC)
        out = self.back + buf + np.asarray(halo, np.float32) * 0.42
        return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))


def wrap(d, text, font, width):
    out, cur = [], ""
    for word in text.split():
        t = (cur + " " + word).strip()
        if d.textlength(t, font=font) > width and cur:
            out.append(cur)
            cur = word
        else:
            cur = t
    return out + [cur] if cur else out


def sheet(view, rgb, caption):
    """The frame without its panel: helmet, panel background, caption."""
    im = Image.new("RGB", (W, H), BG)
    im.paste(view.image(rgb), view.box[:2])
    d = ImageDraw.Draw(im)
    d.rectangle([PANEL_X, 0, W, CAP_Y], fill=PANEL)
    d.rectangle([0, CAP_Y, W, H], fill=PANEL)
    d.line([0, CAP_Y, W, CAP_Y], fill=RULE, width=2)
    lines = wrap(d, caption, F_CAP, W - 96)
    if len(lines) > 2:
        raise ValueError("caption too long: %r" % caption)
    y = CAP_Y + (65 - 21 * len(lines)) + (0 if len(lines) == 2 else 0)
    for ln in lines:
        d.text((48, y), ln, font=F_CAP, fill=TEXT)
        y += 44
    return im, d


def tag(d, xy, text, fill=TEXT, anchor="mm"):
    """A label on the helmet drawing, readable over lit LEDs."""
    d.text(xy, text, font=F_TAG, fill=fill, anchor=anchor, stroke_width=4, stroke_fill=BG)


class Walkthrough:
    """Each part of the helmet, lit by itself, keeping time with the song underneath."""

    def __init__(self, view, h, song, start):
        self.v, self.h, self.song, self.start = view, h, song, start
        self.guard = mau5power.load(count=h.n)
        s = np.asarray(h.shell, bool)
        self.face = s & (np.asarray(h.py) > 28)
        self.jaw = s & ~self.face
        self.tube = np.asarray(h.tube)
        self.al = np.maximum(np.asarray(h.along), 0.0)
        self.tubes = np.asarray(h.tubes, bool)
        self.rims = np.asarray(h.rims, bool)
        self.ears = np.asarray(h.ears, bool)
        self.ea = np.asarray(h.ea)
        self.hash = np.modf(np.sin(np.arange(h.n) * 12.9898) * 43758.5453)[0] % 1.0
        self.n = h.n
        self.counts = dict(all=h.n, dome=int(self.face.sum()), jaw=int(self.jaw.sum()),
                           ear=int(np.asarray(h.ear1).sum()), rim=int((self.rims & np.asarray(h.ear1, bool)).sum()),
                           tube=int((self.tubes & np.asarray(h.ear1, bool)).sum()))
        c = self.counts
        P = dict(y_lo=20.0, y_hi=160.0, x_half=150.0)
        self.faces = [E.make("sprite", sprite=nm, color=col, **P) for nm, col in
                      (("smile", (70, 230, 210)), ("heart", (255, 50, 90)), ("skull", (235, 235, 235)))]
        self.scenes = [
            (6.5, self.title, "Mau5head",
             "I built and programmed this helmet. First, what all the parts are. Then every song it has a show for, with the song playing."),
            (7.5, self.wire, "One wire",
             "%d lights on one long wire, in order. A phone draws every frame and sends it to the controller in the helmet over Wi-Fi, about 25 times a second." % c["all"]),
            (7.5, self.dome, "The dome",
             "%d LEDs over the forehead and eyes, behind a printed shell. It's the closest thing to a screen on here, so faces, animals and words go on it." % c["dome"]),
            (7.5, self.lower, "The jaw",
             "%d more around the sides and chin. There are no lights across the middle because that's the visor, where I see out, so a mouth has to live down here." % c["jaw"]),
            (8.0, self.tubes_, "Ear tubes",
             "Each ear has three straight tubes, %d LEDs per ear. Light can shoot up a tube from the head outward, so they read as blades. Good for a snare." % c["tube"]),
            (6.5, self.rim, "Ear rims",
             "Around the edge of each ear is a thin ring of %d bare LEDs. They're the small, sharp points of light, and good for a kick." % c["rim"]),
            (9.0, self.band, "Played like a band",
             "Each song gets its own job for each part. A common split is kick on the rims, snare up the tubes, melody on the dome and bass in the jaw."),
            (9.0, self.power, "The power limit",
             "It can't all be bright. It can burst to 1 amp but only hold about 0.3 for long, and when the ears get loud the limiter takes it from the dome, so dark is part of every show."),
            (6.5, self.read, "Next: the shows",
             "These are simulated: the real show code and power limiter, drawn on the measured LED map, not filmed. The panel says what each part is doing for that song."),
        ]
        self.length = sum(s[0] for s in self.scenes)

    def until(self, fn):
        at = 0.0
        for dur, f, _, _ in self.scenes:
            if f == fn:
                return at
            at += dur
        raise ValueError(fn)

    def beat(self, tl):
        return self.song.beat_of(self.start + self.now)

    def title(self, tl, p, d):
        k = 0.5 + 0.5 * np.sin(2 * math.pi * (self.hash + self.beat(tl) / 8.0))
        out = np.zeros((self.n, 3))
        out[self.face] = k[self.face, None] ** 3 * np.array((255, 120, 30)) * 0.5
        return out, None

    def wire(self, tl, p, d):
        head = p * 1.04 * self.n
        i = np.arange(self.n)
        age = head - i
        k = np.where(age >= 0, np.exp(-age / 22.0) + 0.1, 0.0)
        return k[:, None] * np.array((255, 170, 60)), None

    def dome(self, tl, p, d):
        inst = self.faces[min(int(p * 3), 2)]
        out = np.asarray(inst.render(self.h, tl, None), float) * 0.8
        return out, lambda dd: None

    def lower(self, tl, p, d):
        k = 0.45 + 0.35 * np.exp(-(self.beat(tl) % 1) * 3)
        out = np.zeros((self.n, 3))
        out[self.jaw] = np.array((255, 110, 30)) * k
        def marks(dd):
            mid = self.v.xy[self.face].mean(0)
            low = self.v.xy[self.jaw]
            y = (self.v.xy[self.face][:, 1].max() + low[:, 1].max()) / 2 + self.v.box[1] + 28
            tag(dd, (mid[0], y - 22), "no lights here", TEXT2)
            tag(dd, (mid[0], y + 18), "this is where I see out", TEXT2)
        return out, marks

    def tubes_(self, tl, p, d):
        b = self.beat(tl)
        which = int(b // 2) % 3
        front = min((b % 2) / 1.2, 1.0)
        out = np.zeros((self.n, 3))
        m = self.tubes & (self.tube == which)
        k = np.clip((front - self.al) / 0.1 + 0.5, 0, 1) * (0.25 + 0.75 * max(0, 1 - (b % 2) / 2))
        out[m] = k[m, None] * np.array((110, 200, 255))
        def marks(dd):
            for t in range(3):
                for ear in (self.h.ear1, self.h.ear2):
                    q = self.tubes & (self.tube == t) & np.asarray(ear, bool)
                    tip = self.v.xy[q][np.argmax(self.al[q])]
                    tag(dd, (tip[0], tip[1] - 24), "tube %d" % (t + 1), AMBER if t == which else TEXT2)
        return out, marks

    def rim(self, tl, p, d):
        b = self.beat(tl)
        q = (self.ea - b / 4.0) % 1.0
        out = np.zeros((self.n, 3))
        out[self.rims] = (np.exp(-q[self.rims] * 7) + 0.12)[:, None] * np.array((255, 215, 140))
        return out, None

    def band_levels(self, tl):
        b = self.beat(tl)
        kick = math.exp(-(b % 1) * 3.2)     # on every beat: this is house music
        snare_age = (b - 1) % 2
        snare = math.exp(-snare_age * 2.2)
        return b, kick, snare_age, snare

    def band(self, tl, p, d):
        b, kick, sa, snare = self.band_levels(tl)
        out = np.zeros((self.n, 3))
        out[self.rims] = np.array((255, 225, 170)) * kick
        k = np.clip((min(sa / 0.5, 1.0) - self.al) / 0.1 + 0.5, 0, 1) * snare
        out[self.tubes] = k[self.tubes, None] * np.array((110, 200, 255))
        tw = np.clip(np.sin(2 * math.pi * (self.hash * 7 + b * (0.2 + self.hash * 0.5))), 0, 1) ** 5
        out[self.face] = tw[self.face, None] * np.array((255, 90, 200)) * 0.55
        music = self.song.music
        bass = float(music.band_at(self.start + self.now, "bass")) if music is not None else 0.5
        out[self.jaw] = np.array((255, 110, 30)) * (0.12 + 0.5 * bass)
        return out, None

    def power(self, tl, p, d):
        out = np.zeros((self.n, 3))
        out[self.face] = np.array((255, 150, 40)) * 0.26
        out[self.jaw] = np.array((255, 150, 40)) * 0.26
        ears = float(np.clip((p - 0.3) / 0.25, 0, 1))
        out[self.ears] = np.array((90, 190, 255)) * ears
        return out, None

    def read(self, tl, p, d):
        b = self.beat(tl)
        k = np.clip(np.sin(2 * math.pi * (self.hash * 5 + b * 0.12)), 0, 1) ** 6
        return k[:, None] * np.array((255, 170, 90)) * 0.5, None

    def panel(self, d, name, fn, tl, p, rep):
        x, w = PANEL_X + 44, W - PANEL_X - 88
        d.text((x, 44), name, font=F_NAME if d.textlength(name, font=F_NAME) < w else F_NAME2, fill=TEXT)
        y = 170
        c = self.counts
        if fn == self.title:
            for ln in ("%d LEDs" % c["all"], "16 songs", "1 phone"):
                d.text((x, y), ln, font=F_BODY, fill=TEXT2)
                y += 50
        elif fn == self.band:
            b, kick, sa, snare = self.band_levels(tl)
            for lab, part, lit, col in (("KICK", "rims", kick, (255, 225, 170)), ("SNARE", "tubes", snare, (110, 200, 255)),
                                        ("MELODY", "dome", 0.5, (255, 90, 200)), ("BASS", "jaw", 0.5, (255, 110, 30))):
                a = 0.25 + 0.75 * lit
                d.text((x, y), lab, font=F_TAG, fill=tuple(int(q * a) for q in col))
                d.text((x + 170, y - 3), part, font=F_BODY, fill=TEXT)
                y += 66
        elif fn == self.power:
            m = rep["sent_ma"]
            d.text((x, y), "%4.0f mA to the LEDs" % m, font=F_BODY, fill=TEXT)
            y += 60
            top, bw = 1100.0, 44
            hgt = 430
            d.rectangle([x, y, x + bw, y + hgt], outline=RULE, width=2)
            fill = hgt * min(m, top) / top
            d.rectangle([x + 3, y + hgt - fill, x + bw - 3, y + hgt - 3], fill=AMBER)
            for ma, lab in ((1000, "burst limit"), (300, "what it can hold")):
                yy = y + hgt - hgt * ma / top
                d.line([x - 6, yy, x + bw + 16, yy], fill=TEXT2, width=2)
                d.text((x + bw + 26, yy - 15), lab, font=F_SMALL, fill=TEXT2)
        elif fn == self.read:
            for lab, tx in (("BPM, BAR, BEAT", "where the song is. Every show is written by hand against the song's own bars."),
                            ("EARS, DOME, JAW", "what each part is doing right now."),
                            ("mA", "the current after the limiter.")):
                d.text((x, y), lab, font=F_SMALL, fill=AMBER)
                y += 36
                for ln in wrap(d, tx, F_BODY, w):
                    d.text((x, y), ln, font=F_BODY, fill=TEXT)
                    y += 42
                y += 22
        elif fn in (self.wire, self.dome, self.lower, self.tubes_, self.rim):
            big = {self.wire: c["all"], self.dome: c["dome"], self.lower: c["jaw"],
                   self.tubes_: c["tube"] * 2, self.rim: c["rim"] * 2}[fn]
            d.text((x, y), str(big), font=F_HUGE, fill=AMBER)
            d.text((x, y + 128), "LEDs", font=F_BODY, fill=TEXT2)

    def frame(self, t):
        at = 0.0
        for dur, fn, name, cap in self.scenes:
            if t < at + dur or fn == self.read:
                break
            at += dur
        tl, p = t - at, min((t - at) / dur, 1.0)
        self.now = t
        rgb, marks = fn(tl, p, None)
        res, rep = self.guard.apply(rgb, now=t, gain=1.0)
        fade = min(1.0, tl / 0.35, max(dur - tl, 0.0) / 0.35)
        im, d = sheet(self.v, np.asarray(res, float) * fade, cap)
        if marks and fade > 0.5:
            marks(d)
        self.panel(d, name, fn, tl, p, rep)
        return im


def song_panel(d, song, e, t, label, rep):
    x, w = PANEL_X + 44, W - PANEL_X - 88
    y = 40
    title = e[1]
    if d.textlength(title, font=F_NAME) < w:
        d.text((x, y), title, font=F_NAME, fill=TEXT)
        y += 100
    else:
        for ln in wrap(d, title, F_NAME2, w):
            d.text((x, y), ln, font=F_NAME2, fill=TEXT)
            y += 62
        y += 12
    credit = song.base.split(" - ")[0] if " - " in song.base and not song.base.startswith("TIKI") else ""
    if credit:
        d.text((x, y), credit, font=F_SMALL, fill=DIM)
        y += 44
    beat = song.beat_of(t)
    d.text((x, y), "%.0f BPM   bar %d   beat %d" % (60.0 / song.spb, int(np.floor(beat / 4)), int(np.floor(beat)) % 4 + 1),
           font=F_BODY, fill=TEXT2)
    y += 56
    for i in range(4):
        on = int(np.floor(beat)) % 4 == i and beat % 1 < 0.5
        d.ellipse([x + i * 38, y, x + i * 38 + 21, y + 21], fill=AMBER if on else (58, 64, 72))
    y += 56
    for name, text in (("EARS", e[4]), ("DOME", e[5]), ("JAW", e[6])):
        d.text((x, y), name, font=F_SMALL, fill=AMBER)
        y += 34
        for ln in wrap(d, text, F_BODY, w):
            d.text((x, y), ln, font=F_BODY, fill=TEXT)
            y += 41
        y += 20
    d.text((x, CAP_Y - 52), "%4.0f mA after the limiter" % rep["sent_ma"], font=F_SMALL, fill=DIM)


def end_card(entries):
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    d.text((96, 70), "Mau5head", font=F_HUGE, fill=TEXT)
    d.text((100, 205), "Hardware, CAD and software by me, with a lot of help from Claude. The music belongs to these artists:",
           font=F_SMALL, fill=TEXT2)
    names = sorted(e[0] for e in entries)
    for k, n in enumerate(names):
        col, row = k // 8, k % 8
        d.text((100 + col * 880, 290 + row * 72), n, font=F_SMALL, fill=TEXT)
    return im


def clip(base, t0, t1):
    path = os.path.join(SHOWS, base + ".mp3")
    if not os.path.exists(path):
        path = os.path.join(ROOT, base + ".mp3")
    r = subprocess.run(["ffmpeg", "-v", "error", "-ss", "%.3f" % t0, "-t", "%.3f" % (t1 - t0), "-i", path,
                        "-f", "f32le", "-ac", "2", "-ar", str(score.SR), "-"], capture_output=True, check=True)
    x = np.frombuffer(r.stdout, np.float32).reshape(-1, 2).astype(float)
    # one level across sixteen masters, but a quiet passage stays a bit quieter
    gain = np.clip(TARGET_RMS / (np.sqrt((x ** 2).mean()) + 1e-6), 0.5, 2.0)
    return x * gain


def track(parts):
    ov = int(XFADE * score.SR)
    total = sum(len(p) - ov for p in parts) + ov
    out = np.zeros((total, 2))
    ramp = np.linspace(0, 1, ov)[:, None]
    i = 0
    for k, p in enumerate(parts):
        p = p.copy()
        if k:
            p[:ov] *= ramp
        if k < len(parts) - 1:
            p[-ov:] *= ramp[::-1]
        out[i:i + len(p)] += p
        i += len(p) - ov
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--sheet")
    ap.add_argument("--out", default=os.path.join(OUT, "overview.mp4"))
    ap.add_argument("--under", default="deadmau5 - Some Chords", help="the song under the walkthrough")
    ap.add_argument("--kick-bar", type=float, default=56, help="the bar its kick comes in, which the band scene lands on")
    a = ap.parse_args()
    M = F.Model()
    h = E.Helmet()
    view = View((0, 0, PANEL_X, CAP_Y), M, h)
    under = Song(a.under, h)
    walk = Walkthrough(view, h, under, 0.0)
    walk.start = under.t_of_bar(a.kick_bar) - walk.until(walk.band)
    entries = reel.REEL
    songs = [Song(e[0], h) for e in entries]

    if a.sheet:
        tiles = []
        at = 0.0
        for dur, fn, name, cap in walk.scenes:
            t = at + dur * 0.6
            tt = max(at, t - 2)
            while tt < t:
                walk.frame(tt)
                tt += 0.1
            tiles.append(walk.frame(t))
            at += dur
        for k in (0, 4, 6, 9):
            s, e = songs[k], entries[k]
            t0, t1 = s.t_of_bar(e[2]), s.t_of_bar(e[3])
            t = t0 + (t1 - t0) * 0.62
            s.warm(t, 2.0)
            res, label, rep = s.frame(t)
            im, d = sheet(view, res, e[7])
            song_panel(d, s, e, t, label, rep)
            tiles.append(im)
        tiles.append(end_card(entries))
        cols = 3
        rows = (len(tiles) + cols - 1) // cols
        o = Image.new("RGB", (cols * 640, rows * 360))
        for k, im in enumerate(tiles):
            o.paste(im.resize((640, 360), Image.LANCZOS), ((k % cols) * 640, (k // cols) * 360))
        o.save(a.sheet, quality=92)
        tiles[3].save(a.sheet + ".full.png")
        tiles[11].save(a.sheet + ".full2.png")
        print(a.sheet)
        return

    intro_n = int(round(walk.length * FPS))
    lead = intro_n / FPS
    END = 7.0
    parts = [clip(a.under, walk.start, walk.start + lead + XFADE) * 0.8]
    for k, (s, e) in enumerate(zip(songs, entries)):
        t0, t1 = s.t_of_bar(e[2]), s.t_of_bar(e[3])
        tail = END if k == len(entries) - 1 else XFADE
        parts.append(clip(s.base, t0, t1 + tail))
    x = track(parts)
    x = x * min(1.0, 0.89 / (np.abs(x).max() + 1e-9))
    n = int(0.6 * score.SR)
    x[:n] *= np.linspace(0, 1, n)[:, None]
    n = int(4.0 * score.SR)
    x[-n:] *= np.linspace(1, 0, n)[:, None] ** 1.5
    tmp = tempfile.mkdtemp(prefix="mau5over")
    wav = os.path.join(tmp, "a.wav")
    score.write_wav(wav, x)

    cmd = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "%dx%d" % (W, H),
           "-framerate", str(FPS), "-i", "-", "-i", wav,
           "-c:v", "libx264", "-preset", "slow", "-crf", "19", "-tune", "animation", "-pix_fmt", "yuv420p",
           "-g", str(FPS * 2), "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", a.out]
    enc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    started = time.time()
    for i in range(intro_n):
        enc.stdin.write(walk.frame(i / FPS).tobytes())
    print("walkthrough %.1f s, %.0f s elapsed" % (lead, time.time() - started), flush=True)
    done = 0.0
    for s, e in zip(songs, entries):
        t0, t1 = s.t_of_bar(e[2]), s.t_of_bar(e[3])
        s.warm(t0)
        n = int(round((done + (t1 - t0)) * FPS)) - int(round(done * FPS))
        done += t1 - t0
        fade_n = int(FADE * FPS)
        for i in range(n):
            t = t0 + i / FPS
            res, label, rep = s.frame(t)
            k = min(1.0, (i + 1) / fade_n, (n - i) / fade_n)
            im, d = sheet(view, res * k, e[7])
            song_panel(d, s, e, t, label, rep)
            enc.stdin.write(im.tobytes())
        print("  %-34s %.0f s elapsed" % (e[1], time.time() - started), flush=True)
    black = Image.new("RGB", (W, H), BG)
    card_im = end_card(entries)
    for i in range(int(END * FPS)):
        f = min(1.0, (i + 1) / 15.0, (END * FPS - i) / 25.0)
        enc.stdin.write(Image.blend(black, card_im, f).tobytes())
    enc.stdin.close()
    enc.wait()
    print("wrote %s  %.1f MB" % (a.out, os.path.getsize(a.out) / 1e6))


if __name__ == "__main__":
    main()
