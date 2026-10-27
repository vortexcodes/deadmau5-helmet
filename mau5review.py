#!/usr/bin/env python3
"""mau5review -- light every preset on the helmet and photograph it.

A preset that renders correctly in the simulator can still look wrong on
the helmet: a strip wired backwards, a colour order off, a region the
power guard has starved into invisibility.  None of that shows up in a
unit test.  So this drives the real thing and brings back pictures.

Two details make the pictures worth looking at.

First, the animation is *frozen*.  Streaming a preset in real time and
then waiting a second for the camera gives you an unknown phase, and
three unknown phases tell you less than one known one.  Each shot here
renders the preset at a chosen t and holds that single frame until the
shutter has been.

Second, every shot is differenced against a dark reference taken
moments earlier.  The helmet is photographed in a room, and the room is
usually brighter than the LEDs are allowed to be.  The difference
throws the room away and leaves what the LEDs actually contributed.

    python3 mau5review.py                      # all presets, 3 phases
    python3 mau5review.py --only scanner text
    python3 mau5review.py --phases 1 --gain 3
"""

from __future__ import annotations

import argparse
import json
import os
import time

import numpy as np
from PIL import Image, ImageDraw

import mau5engine as E
import mau5eye
import mau5map
import mau5wled

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "data", "cal", "review")

# Presets whose look depends on a music drive.  Reviewed with a
# synthetic one, because at rest they are a flat bar and say nothing.
MUSICAL = {"eq", "vu", "beatpulse", "heartbeat"}

# Phases worth seeing, as a fraction of the preset's period.  A preset
# with no period gets these as plain seconds.
PHASES = (0.17, 0.5, 0.83)

# A few presets are only themselves with non-default arguments.
OVERRIDES = {
    "text": {"text": "MAU5", "speed": 0.0},      # held still, not scrolling
    "countdown": {"from": 3},
    "alignbar": {"axis": "z", "grid": True},
}


class FakeMusic:
    """Enough of a Music to drive the reactive presets off-line."""

    def __init__(self, bpm=128.0):
        self.bpm = bpm
        self.duration = 600.0

    def level_at(self, t):
        return 0.45 + 0.45 * float(np.sin(2 * np.pi * t * self.bpm / 60.0)) ** 2

    def beat_phase(self, t):
        return (t * self.bpm / 60.0) % 1.0

    def is_downbeat(self, t, tol=0.05):
        return (t * self.bpm / 240.0) % 1.0 < tol

    def bands_at(self, t, n=8):
        k = np.arange(n)
        return np.clip(0.25 + 0.7 * np.abs(np.sin(2 * np.pi * (t * 0.7 + k / 5.0))), 0, 1)


def period_of(preset):
    for key in ("period", "every", "cycle"):
        v = preset.p.get(key)
        if isinstance(v, (int, float)) and v > 0:
            return float(v)
    if preset.p.get("hz"):
        return 1.0 / float(preset.p["hz"])
    if preset.p.get("bpm"):
        return 60.0 / float(preset.p["bpm"])
    return None


def phase_times(preset, n):
    per = period_of(preset)
    fr = PHASES[:n] if n <= len(PHASES) else tuple(
        (i + 0.5) / n for i in range(n))
    if per is None:
        return [round(1.0 + 2.3 * f, 3) for f in fr]
    return [round(per * f, 3) for f in fr]


def grab(path, after, port):
    return mau5eye.shot(path, port=port, after=after, wait=25.0)


def dark_frame(stream, port, tmp, n=2):
    """Average a couple of blanked frames, for a quieter reference."""
    stream.dark()
    time.sleep(0.35)
    acc = None
    for i in range(n):
        p = grab(os.path.join(tmp, "dark%d.jpg" % i), time.time(), port)
        a = np.asarray(Image.open(p).convert("RGB")).astype(np.float32)
        acc = a if acc is None else acc + a
    return acc / n


def lit_frame(stream, buf, port, tmp):
    stream.show(buf)
    t0 = time.time()
    time.sleep(0.25)
    p = grab(os.path.join(tmp, "lit.jpg"), t0, port)
    return np.asarray(Image.open(p).convert("RGB")).astype(np.float32)


def difference(lit, dark, gain=1.0):
    d = np.clip((lit - dark) * gain, 0, 255)
    return d.astype(np.uint8)


def label(img, text, sub=""):
    im = Image.fromarray(img) if isinstance(img, np.ndarray) else img
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, im.width, 34], fill=(0, 0, 0))
    d.text((8, 4), text, fill=(255, 255, 255))
    if sub:
        d.text((8, 19), sub, fill=(150, 150, 150))
    return im


def contact_sheet(tiles, cols, path, tile_w=400):
    if not tiles:
        return None
    scaled = []
    for im, cap, sub in tiles:
        h = int(im.height * tile_w / im.width)
        scaled.append(label(im.resize((tile_w, h), Image.LANCZOS), cap, sub))
    tw, th = scaled[0].width, scaled[0].height
    rows = (len(scaled) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * tw, rows * th), (16, 16, 16))
    for i, im in enumerate(scaled):
        sheet.paste(im, ((i % cols) * tw, (i // cols) * th))
    sheet.save(path, quality=88)
    return path


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--host", default=None)
    ap.add_argument("--eye-port", type=int, default=8752)
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--only", nargs="*", help="preset names")
    ap.add_argument("--skip", nargs="*", default=[])
    ap.add_argument("--phases", type=int, default=3)
    ap.add_argument("--gain", type=float, default=1.0,
                    help="multiply the difference image")
    ap.add_argument("--level", type=float, default=1.0,
                    help="scale the render before the guard sees it.  The "
                         "camera blows out long before the guard's ceiling "
                         "does, and a saturated photograph has no colour in "
                         "it, so geometry and hue are reviewed dimmed.")
    ap.add_argument("--cols", type=int, default=3)
    ap.add_argument("--redark", type=int, default=4,
                    help="re-take the dark reference every N presets")
    ap.add_argument("--raw", action="store_true",
                    help="also keep the undifferenced frames")
    a = ap.parse_args(argv)

    os.makedirs(a.out, exist_ok=True)
    tmp = os.path.join(a.out, "_tmp")
    os.makedirs(tmp, exist_ok=True)

    names = sorted(a.only) if a.only else sorted(E.REGISTRY)
    names = [n for n in names if n not in set(a.skip)]
    bad = [n for n in names if n not in E.REGISTRY]
    if bad:
        raise SystemExit("no such preset: %s" % ", ".join(bad))

    w = mau5wled.WLED(a.host) if a.host else (mau5wled.scan_subnet() or [None])[0]
    if w is None:
        raise SystemExit("no controller found")
    w.realtime(True)
    h = E.Helmet()
    pix = mau5wled.Pixels(w, count=h.n)
    stream = mau5wled.Streamer(pix)
    music = FakeMusic()

    report, tiles = [], []
    t_start = time.time()
    try:
        dark = dark_frame(stream, a.eye_port, tmp)
        for i, name in enumerate(names):
            if i and i % a.redark == 0:
                dark = dark_frame(stream, a.eye_port, tmp)
            kw = OVERRIDES.get(name, {})
            try:
                preset = E.make(name, **kw)
            except Exception as e:
                print("  %-10s SKIP (%s)" % (name, e))
                continue
            m = music if name in MUSICAL else None
            for j, t in enumerate(phase_times(preset, a.phases)):
                buf = np.clip(preset.render(h, t, m) * a.level, 0, 255)
                lit = lit_frame(stream, buf.astype(np.uint8), a.eye_port, tmp)
                d = difference(lit, dark, a.gain)
                stem = "%s_%d" % (name, j)
                Image.fromarray(d).save(os.path.join(a.out, stem + ".jpg"), quality=90)
                if a.raw:
                    Image.fromarray(lit.astype(np.uint8)).save(
                        os.path.join(a.out, stem + "_raw.jpg"), quality=85)
                want = float(buf.sum())
                got = float(d.astype(np.float32).sum())
                rep = stream.last_power or {}
                report.append({"preset": name, "phase": j, "t": t,
                               "asked": want, "seen": got,
                               "lit_leds": int((buf.max(1) > 4).sum()),
                               "scale": rep.get("scale"),
                               "watts": rep.get("watts")})
                tiles.append((Image.fromarray(d), "%s  [%d]" % (name, j),
                              "t=%.2fs  %d leds  %.1f W"
                              % (t, report[-1]["lit_leds"], rep.get("watts") or 0)))
                print("  %-10s phase %d  t=%5.2f  %4d leds  seen %8.0f  %s"
                      % (name, j, t, report[-1]["lit_leds"], got,
                         "scale %.2f" % rep["scale"] if rep.get("scale") else ""))
            stream.dark()
    finally:
        stream.stop()
        try:
            w.off()
        except Exception:
            pass

    with open(os.path.join(a.out, "report.json"), "w") as f:
        json.dump({"when": time.strftime("%Y-%m-%dT%H:%M:%S"),
                   "seconds": round(time.time() - t_start, 1),
                   "rows": report}, f, indent=1)
    sheet = contact_sheet(tiles, a.cols, os.path.join(a.out, "sheet.jpg"))
    print("\n%d shots in %.0fs -> %s" % (len(report), time.time() - t_start, sheet))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
