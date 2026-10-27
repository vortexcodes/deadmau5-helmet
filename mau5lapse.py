#!/usr/bin/env python3
"""mau5lapse -- stitch the session's captures into one timelapse.

The calibration ran all night with the room lights off, so most of the
frames are a single lit LED on a black helmet: a mean brightness of 1.7
out of 255.  Played back raw that is a black video with an occasional
twinkle.  Every frame is therefore auto-levelled, which turns the
localisation pass into what it actually was -- a dot walking round the
helmet, 622 times.

Levelling is per frame and deliberately so.  A fixed gain either crushes
the daylight frames or leaves the night ones black, and the point of
the video is to show the whole run, not one exposure of it.

    python3 mau5lapse.py                      # everything, newest last
    python3 mau5lapse.py --acts review        # just today's presets
    python3 mau5lapse.py --fps 24 --no-level
"""

from __future__ import annotations

import argparse
import glob
import os
import shutil
import subprocess
import tempfile

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
CAL = os.path.join(HERE, "data", "cal")
OUT = os.path.join(CAL, "session_timelapse.mp4")

SIZE = (1280, 720)

# name -> (glob, caption, how many frames each one is held for)
ACTS = [
    ("calibration", os.path.join(CAL, "timelapse", "f*.jpg"),
     "Calibration · the helmet comes up, one strip at a time", 1),
    ("locate", None,                       # filled from the same pool
     "Localisation · every LED lit alone, centroid measured", 1),
    ("baralign", os.path.join(CAL, "baralign", "s*.jpg"),
     "Alignment · a straight bar swept down the map", 3),
    ("review", os.path.join(CAL, "review", "*_[0-9].jpg"),
     "Presets · 34 of them, photographed on the helmet", 4),
]


def _font(size):
    for p in ("/System/Library/Fonts/Helvetica.ttc",
              "/System/Library/Fonts/Supplemental/Arial.ttf"):
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()


def background(files, step=17, size=(320, 180)):
    """The part of the frame that never changes: room, furniture, lamp.

    A median over a sample, because a mean is dragged up by every lit
    frame and a minimum is dragged down by sensor noise.
    """
    A = np.stack([np.asarray(Image.open(p).convert("RGB").resize(size), np.float32)
                  for p in files[::step]])
    return np.median(A, 0)


def against(path, bg, size=(320, 180)):
    """One frame with the static room subtracted, plus how much is left.

    The wide camera recorded the whole night from across the room, and
    for most of it the only thing lit was a single LED, far too dim
    against a standing lamp for any per-frame gain to recover: the gain
    is set by the lamp.  Subtracting the room removes the lamp as well,
    and what survives is the helmet and nothing else.
    """
    im = Image.open(path).convert("RGB")
    a = np.asarray(im.resize(size), np.float32)
    d = np.clip(a - bg, 0, 255)
    return im, float(np.percentile(d.max(2), 99.9))


def level(a, target=238.0, floor=6.0):
    """Stretch one frame so its brightest real content is near white.

    The 99.7th percentile rather than the maximum, because a single hot
    pixel or a window reflection would otherwise set the gain for the
    whole frame and undo the stretch.
    """
    p = np.percentile(a, 99.7)
    if p < floor:                     # nothing but sensor noise
        p = max(a.max(), floor)
    return np.clip(a * (target / max(p, 1.0)), 0, 255)


def caption(im, text, sub=""):
    d = ImageDraw.Draw(im, "RGBA")
    d.rectangle([0, im.height - 76, im.width, im.height], fill=(0, 0, 0, 150))
    d.text((28, im.height - 62), text, font=_font(26), fill=(255, 255, 255))
    if sub:
        d.text((28, im.height - 30), sub, font=_font(16), fill=(170, 170, 170))
    return im


def title_card(text, sub, n, outdir, start):
    im = Image.new("RGB", SIZE, (8, 8, 10))
    d = ImageDraw.Draw(im)
    f1, f2 = _font(46), _font(22)
    w = d.textlength(text, font=f1)
    d.text(((SIZE[0] - w) / 2, SIZE[1] / 2 - 48), text, font=f1, fill=(255, 255, 255))
    if sub:
        w2 = d.textlength(sub, font=f2)
        d.text(((SIZE[0] - w2) / 2, SIZE[1] / 2 + 14), sub, font=f2, fill=(150, 150, 155))
    for i in range(n):
        im.save(os.path.join(outdir, "%06d.jpg" % (start + i)), quality=90)
    return start + n


def add_frames(files, cap, hold, outdir, start, do_level, sub="",
               bg=None, keep_above=0.0):
    """Write one act's frames, numbered on from `start`.

    With `bg`, each frame is scored against the static room and the ones
    with nothing lit are dropped rather than played as black.
    """
    kept = 0
    for k, path in enumerate(files):
        try:
            if bg is not None:
                im, sc = against(path, bg)
                if sc < keep_above:
                    continue
            else:
                im = Image.open(path).convert("RGB")
        except Exception:
            continue
        if im.size != SIZE:
            im = im.resize(SIZE, Image.LANCZOS)
        if do_level:
            a = level(np.asarray(im).astype(np.float32))
            im = Image.fromarray(a.astype(np.uint8))
        kept += 1
        args = (kept, len(files))[:sub.count("%d")]
        caption(im, cap, sub % args if args else sub)
        for i in range(hold):
            im.save(os.path.join(outdir, "%06d.jpg" % (start + i)), quality=88)
        start += hold
    return start, kept


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--acts", nargs="*", default=None,
                    help="subset of: " + ", ".join(a[0] for a in ACTS))
    ap.add_argument("--no-level", dest="level", action="store_false", default=True)
    ap.add_argument("--max-per-act", type=int, default=700)
    ap.add_argument("--keep-above", type=float, default=25.0,
                    help="on the night act, drop a frame with less than this "
                         "left once the static room is subtracted")
    a = ap.parse_args(argv)

    want = set(a.acts) if a.acts else {x[0] for x in ACTS}
    tmp = tempfile.mkdtemp(prefix="mau5lapse")
    n = 0
    try:
        pool = sorted(glob.glob(ACTS[0][1]))
        # The night half of the pool is the localisation pass: the room
        # is dark and only one LED is on at a time.  Split on that
        # rather than on a frame number, so a reshoot still splits right.
        means = None
        if pool:
            means = np.array([
                float(np.asarray(Image.open(p).convert("L").resize((64, 36))).mean())
                for p in pool[::10]])
        cut = len(pool)
        if means is not None and (means < 8).any():
            cut = int(np.argmax(means < 8) * 10)
        setup, locate = pool[:cut], pool[cut:]
        print("calibration pool: %d frames, split at %d (room goes dark)"
              % (len(pool), cut))

        night = background(locate) if locate else None
        plan = [
            ("calibration", setup, ACTS[0][2], 1, "Setup · %d of %d", None),
            ("locate",      locate, ACTS[1][2], 2, "%d frames with something lit", night),
            ("baralign",    sorted(glob.glob(ACTS[2][1])), ACTS[2][2], 3,
             "step %d of %d", None),
            ("review",      sorted(glob.glob(ACTS[3][1])), ACTS[3][2], 4,
             "frame %d of %d", None),
        ]
        n = title_card("deadmau5 helmet", "622 LEDs, mapped and tested", 45, tmp, n)
        for name, files, cap, hold, sub, bg in plan:
            if name not in want or not files:
                continue
            if len(files) > a.max_per_act:          # keep it watchable
                step = len(files) / float(a.max_per_act)
                files = [files[int(i * step)] for i in range(a.max_per_act)]
            n = title_card(cap.split(" · ")[0], cap.split(" · ")[-1],
                           24, tmp, n)
            n, kept = add_frames(
                files, cap, hold, tmp, n, a.level, sub, bg=bg,
                keep_above=a.keep_above if bg is not None else 0.0)
            print("  %-12s %4d of %4d frames x%d"
                  % (name, kept, len(files), hold))
        if not n:
            raise SystemExit("nothing to stitch -- no captures found")
        print("  %d frames -> %.0fs at %d fps" % (n, n / float(a.fps), a.fps))
        cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
               "-framerate", str(a.fps), "-i", os.path.join(tmp, "%06d.jpg"),
               "-vf", "format=yuv420p", "-c:v", "libx264", "-crf", "21",
               "-movflags", "+faststart", a.out]
        subprocess.run(cmd, check=True)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("\n%s  (%.1f MB)" % (a.out, os.path.getsize(a.out) / 1e6))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
