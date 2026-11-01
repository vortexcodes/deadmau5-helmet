#!/usr/bin/env python3
"""datafilm.py -- everything stored about one song, scrolling past as the show runs.

Every row is drawn straight from the song's analysis file and compiled show. The
helmet on the left is the real engine through the real guard, at the same moment
as the line down the middle.

    python3 tools/film/datafilm.py            # data/cal/song_data.mp4
"""

from __future__ import annotations

import os
import tempfile

import numpy as np

from common import E, F, FPS, H, HelmetView, OUT, Image, ImageDraw, Song, W, encoder, send, strip
from overview import clip
import score

BASE = "deadmau5 - The Veldt"
BAR_FROM, BAR_TO = 5, 40
PX = 46.0                  # pixels per second
X0, PANEL_W = 530, W - 530
NOW = int(PANEL_W * 0.32)  # where "now" sits in the panel
TOP = H - F.FOOT

AMBER, TEAL, ICE = (222, 170, 90), (70, 190, 170), (120, 170, 255)
TEXT, DIM, GRID = (232, 235, 238), (130, 138, 146), (44, 50, 57)

# name, top, height
ROWS = {
    "show": (6, 72),
    "bass": (84, 66),
    "mid": (156, 66),
    "high": (228, 66),
    "energy": (300, 60),
    "chroma": (366, 118),
    "levels": (490, 44),
    "grid": (540, 80),
}
LABEL = {"show": "SCENES AND HITS, WRITTEN BY HAND IN BARS", "bass": "BASS  30 to 170 Hz", "mid": "MID  170 to 2200 Hz",
         "high": "HIGH  2200 to 10000 Hz", "energy": "LOUDNESS (line) AND ONSETS (fill)",
         "chroma": "CHROMA, ONE COLUMN A BAR", "levels": "ENERGY LEVEL PER BAR, AND SECTIONS",
         "grid": "BEAT GRID"}

# from-bar, rows to light up, title, caption
BEATS = [
    (5, None, "What's stored for one song",
     "This is The Veldt, 170 seconds long. The analysis file is 185 kB and holds no audio. Here's everything in it."),
    (9, ("grid",), "The beat grid comes first",
     "363 beats and 91 bars, as a list of times. In this song bar b starts at 0.043 + 1.875 b seconds. I measured it against the audio."),
    (13, ("bass",), "Three frequency bands, 40 times a second",
     "The solid shape is how loud the band is compared to the rest of the song. The bright ticks show how hard it just jumped."),
    (17, ("mid", "high"), "Mid and high work the same way",
     "Each band is scaled against itself. Otherwise the top end would never register next to the bass."),
    (21, ("energy",), "Loudness and onsets",
     "Loudness goes on the controller. No show reads the onset curve anymore. It's left over from the tempo search."),
    (25, ("chroma",), "Chroma is the harmony",
     "How much of each of the 12 notes is in each bar. You can see the 8-bar chord loop, and that's what the ears play."),
    (29, ("levels",), "Levels and sections",
     "Each bar gets ranked 0 to 3, then grouped into sections. Only the automatic fallback show uses these."),
    (33, ("show",), "The scene list is what really plays",
     "22 scenes and 88 hits, in bars. A frame only needs the grid, and 5 places in this show also read a band curve."),
    (37, None, "On the helmet this comes to 14 kB",
     "7 curves stored as bytes at 10 Hz, plus beats, bars and chroma. The MP3 stays on the phone and the lights follow its clock."),
]


def row_label(d, name):
    y, _ = ROWS[name]
    d.text((X0 + 8, y + 1), LABEL[name], font=F.F_SMALL, fill=DIM)


def build_strip(song, t0, t1):
    """The whole stretch as one long image, cropped per frame."""
    w = int((t1 - t0) * PX) + PANEL_W * 2
    pad = PANEL_W
    im = Image.new("RGB", (w, TOP), (17, 20, 24))
    d = ImageDraw.Draw(im)
    z = song.npz
    rate = song.rate

    def X(t):
        return pad + (t - t0) * PX

    def curve(name, color, y, h, punch=None):
        a = z[name]
        ts = np.arange(len(a)) / rate
        keep = (ts > t0 - pad / PX) & (ts < t1 + pad / PX)
        xs, vs = X(ts[keep]), a[keep]
        pts = [(float(x), y + h - float(v) * (h - 18)) for x, v in zip(xs, vs)]
        if len(pts) > 1:
            dim = tuple(int(c * 0.45) for c in color)
            d.polygon([(pts[0][0], y + h)] + pts + [(pts[-1][0], y + h)], fill=dim)
        if punch is not None:
            p = z[punch][keep]
            for x, v in zip(xs, p):
                if v > 0.5:
                    d.line([x, y + h, x, y + h - v * (h - 18)], fill=color, width=1)

    for nm, col in (("bass", AMBER), ("mid", TEAL), ("high", ICE)):
        y, h = ROWS[nm]
        curve("b_%s_e" % nm, col, y, h, "b_%s_p" % nm)

    y, h = ROWS["energy"]
    curve("onset", (92, 100, 110), y, h)
    a = z["energy"]
    ts = np.arange(len(a)) / rate
    keep = (ts > t0 - pad / PX) & (ts < t1 + pad / PX)
    d.line([(float(X(t)), y + h - float(v) * (h - 18)) for t, v in zip(ts[keep], a[keep])], fill=TEXT, width=1)

    # chroma: a column per bar, top row is B
    y, h = ROWS["chroma"]
    bars = z["bars"]
    ch = z["chroma"]
    top = h - 18
    cell = top / 12.0
    for b in range(len(bars) - 1):
        if bars[b + 1] < t0 - pad / PX or bars[b] > t1 + pad / PX:
            continue
        col = ch[b] / max(float(ch[b].max()), 1e-6)
        for k in range(12):
            v = int(255 * float(col[k]) ** 1.6)
            d.rectangle([X(bars[b]), y + 18 + (11 - k) * cell, X(bars[b + 1]) - 1, y + 18 + (12 - k) * cell - 1],
                        fill=(v // 2 + 10, v // 2 + 12, v + 14))

    # levels and sections
    y, h = ROWS["levels"]
    lv = z["levels"]
    shades = [(40, 46, 54), (70, 78, 90), (116, 124, 136), (190, 196, 204)]
    for b in range(len(lv)):
        d.rectangle([X(bars[b]), y + 18, X(bars[b + 1]) - 1, y + 30], fill=shades[int(lv[b])])
    for a_, b_, l in z["sections"]:
        d.rectangle([X(bars[int(a_)]), y + 32, X(bars[min(int(b_), len(bars) - 1)]) - 2, y + h - 1],
                    fill=shades[int(l)])

    # the beat grid
    y, h = ROWS["grid"]
    for t in z["beats"]:
        d.line([X(t), y + 22, X(t), y + 40], fill=(90, 98, 108))
    for k, t in enumerate(bars):
        d.line([X(t), y + 18, X(t), y + 52], fill=AMBER)
        d.text((X(t) + 3, y + 40), "%d" % k, font=F.F_SMALL, fill=TEXT)

    # scenes and hits, from the compiled show
    y, h = ROWS["show"]
    sc = song.show["scenes"]
    for k, s in enumerate(sc["scenes"]):
        a_, b_ = song.t_of_bar(s["from"]), song.t_of_bar(s["to"])
        c = [(36, 52, 92), (44, 66, 116)][k % 2]
        d.rectangle([X(a_), y + 22, X(b_) - 2, y + 44], fill=c)
        d.text((X(a_) + 5, y + 23), s["name"][:int(max((b_ - a_) * PX - 8, 0) / 8)], font=F.F_SMALL, fill=TEXT)
    for x in sc["hits"]:
        a_ = song.t_of_bar(x["at"])
        b_ = song.t_of_bar(x["at"] + x["beats"] / 4.0)
        d.rectangle([X(a_), y + 48, max(X(b_) - 1, X(a_) + 2), y + 62], fill=AMBER)
    return im, pad


def main():
    song = Song(BASE, E.Helmet())
    M = F.Model()
    view = HelmetView((0, 0, 520, TOP), M, song.h)
    t0, t1 = song.t_of_bar(BAR_FROM), song.t_of_bar(BAR_TO)
    long_im, pad = build_strip(song, t0, t1)

    x = clip(BASE, t0, t1)
    fade = int(0.6 * score.SR)
    x[:fade] *= np.linspace(0, 1, fade)[:, None]
    x[-fade:] *= np.linspace(1, 0, fade)[:, None]
    tmp = tempfile.mkdtemp(prefix="mau5data")
    wav = os.path.join(tmp, "a.wav")
    score.write_wav(wav, x)
    print(score.loudness(wav))

    out = os.path.join(OUT, "song_data.mp4")
    enc = encoder(out, audio=wav)
    song.warm(t0)
    n = int((t1 - t0) * FPS)
    for i in range(n):
        t = t0 + i / FPS
        res, label, rep = song.frame(t)
        im = Image.new("RGB", (W, H), (17, 20, 24))
        view.draw(im, res)
        px = pad + (t - t0) * PX - NOW
        panel = long_im.crop((int(px), 0, int(px) + PANEL_W, TOP))
        im.paste(panel, (X0, 0))
        bar = song.beat_of(t) / 4
        cur = [b for b in BEATS if b[0] <= bar][-1] if bar >= BEATS[0][0] else BEATS[0]
        d = ImageDraw.Draw(im, "RGBA")
        if cur[1]:
            for name, (y, h) in ROWS.items():
                if name not in cur[1]:
                    d.rectangle([X0, y, W, y + h], fill=(17, 20, 24, 170))
        for name in ROWS:
            row_label(d, name)
        d.line([X0 + NOW, 0, X0 + NOW, TOP], fill=(255, 255, 255, 200), width=2)
        d.rectangle([X0 - 10, 0, X0, TOP], fill=(17, 20, 24, 255))
        d.text((16, 14), "The Veldt, bar %d" % int(np.floor(bar)), font=F.F_BODY, fill=TEXT)
        d.text((16, 42), "scene: %s" % (label or "-")[:28], font=F.F_SMALL, fill=DIM)
        strip(im, cur[2], cur[3])
        send(enc, im)
    enc.stdin.close()
    enc.wait()
    print("wrote %s  %.1f MB, %.0f s" % (out, os.path.getsize(out) / 1e6, n / FPS))


if __name__ == "__main__":
    main()
