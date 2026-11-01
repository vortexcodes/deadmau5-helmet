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
     "Localisation · every LED lit alone and measured", 1),
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


def accumulate(files, outdir, start, hold=1, gain=1.0, keep_above=0.0,
               bg=None, caption_fmt="Localisation \u00b7 %d of %d LEDs measured"):
    """Each frame adds its LED to the ones before it.

    This is the calibration's own explanation of itself.  Every frame
    in the localisation pass has exactly one LED lit, so taking a
    running maximum draws the helmet in its own light, one pixel at a
    time, in the order the chain is wired -- and what you end up with
    is not an artist's impression of the map, it is the map, measured.

    A maximum rather than a sum: the frames overlap in bloom and a
    sum turns the dense parts of the dome into a white blob about
    forty LEDs in.
    """
    acc = None
    n = 0
    for path in files:
        try:
            im = Image.open(path).convert("RGB")
        except Exception:
            continue
        a = np.asarray(im, np.float32)
        if bg is not None:
            a = np.clip(a - bg, 0, 255)
        if float(a.max()) < keep_above:
            continue
        acc = a if acc is None else np.maximum(acc, a)
        n += 1
        out = np.clip(acc * gain, 0, 255).astype(np.uint8)
        frame = Image.fromarray(out)
        if frame.size != SIZE:
            frame = frame.resize(SIZE, Image.LANCZOS)
        caption(frame, "Localisation \u00b7 every LED lit alone, once",
                caption_fmt % (n, 622))
        for i in range(hold):
            frame.save(os.path.join(outdir, "%06d.jpg" % (start + i)), quality=88)
        start += hold
    return start, n, acc


def trace_map(tmp, start, fps, cal=CAL, per_frame=2.2, tail=10):
    """Draw the measured map, one LED at a time, in wiring order.

    The accumulation of the raw frames was the obvious way to do this
    and it is a white blob by the two hundredth LED: each one blooms
    across a third of the shell and a running maximum piles that up.
    What is actually interesting is not the glow, it is the
    *measurement* -- so this plots the centroids instead, in chain
    order, with a line to the previous LED on the same strip.  Which
    is also the honest picture: those dots are the map, and the line
    is the wire.
    """
    import csv as _csv
    rows = []
    with open(os.path.join(cal, "led_positions.csv")) as f:
        for r in _csv.DictReader(f):
            try:
                if float(r["peak"]) < 40:
                    continue
                rows.append((int(r["index"]), float(r["cx"]), float(r["cy"])))
            except (TypeError, ValueError, KeyError):
                continue
    rows.sort()
    if not rows:
        return start, 0
    import mau5map
    region = {r["index"]: str(r["region"]) for r in mau5map.load(adjust=False)}
    group = {r["index"]: int(r["group"]) for r in mau5map.load(adjust=False)}

    W, H = SIZE
    sx = W / 1280.0
    sy = H / 720.0
    SHELL, EAR = (255, 110, 20), (40, 170, 255)

    canvas = Image.new("RGB", SIZE, (6, 6, 9))
    d = ImageDraw.Draw(canvas)
    n = 0
    shown = 0
    frames = 0
    while shown < len(rows):
        upto = min(len(rows), int((frames + 1) * per_frame))
        for k in range(shown, upto):
            i, cx, cy = rows[k]
            x, y = cx * sx, cy * sy
            col = SHELL if region.get(i, "").startswith("shell") else EAR
            if k and group.get(rows[k-1][0]) == group.get(i):
                px, py = rows[k-1][1] * sx, rows[k-1][2] * sy
                d.line([px, py, x, y], fill=(col[0]//5, col[1]//5, col[2]//5), width=1)
            d.ellipse([x-2, y-2, x+2, y+2], fill=col)
        shown = upto
        f = canvas.copy()
        # the newest few, brighter, so the eye follows the chain
        fd = ImageDraw.Draw(f)
        for k in range(max(0, shown - tail), shown):
            i, cx, cy = rows[k]
            x, y = cx * sx, cy * sy
            g = int(255 * (1.0 - (shown - 1 - k) / float(tail)))
            fd.ellipse([x-3, y-3, x+3, y+3], fill=(g, g, g))
        caption(f, "Each dot is one LED, lit alone and measured",
                "%d of %d. The faint line between them is the wire." % (shown, len(rows)))
        f.save(os.path.join(tmp, "%06d.jpg" % (start + frames)), quality=90)
        frames += 1
    # hold the finished map
    caption(canvas, "Each dot is one LED, lit alone and measured",
            "All %d measured." % len(rows))
    for i in range(int(fps * 3.0)):
        canvas.save(os.path.join(tmp, "%06d.jpg" % (start + frames + i)), quality=92)
    return start + frames + int(fps * 3.0), len(rows)


def build_explainer(tmp, fps, cal=CAL):
    """The calibration, told in the order it happened.

    Four acts, and the first one is the whole argument: the CAD knows
    where the pockets are, the camera knows where the LEDs are, and
    the difference is why any of this exists.
    """
    n = 0
    n = title_card("Where are the LEDs?",
                   "The CAD has every pocket, but it can't tell me which LED "
                   "went in which one.", int(fps * 2.6), tmp, n)
    n = title_card("One at a time",
                   "I lit all 622 one by one in a dark room and measured each.",
                   int(fps * 2.4), tmp, n)

    n, nled = trace_map(tmp, n, fps, cal)
    print("  plotted %d measured positions" % nled)

    bars = sorted(glob.glob(os.path.join(cal, "baralign", "s*.jpg")))
    if bars:
        n = title_card("Is the map straight?",
                       "I swept a flat bar down the helmet. If the map is right, "
                       "the line stays straight.", int(fps * 2.4), tmp, n)
        n, _ = add_frames(bars, "A straight bar swept down the map",
                          3, tmp, n, True, "step %d of %d")

    rev = sorted(glob.glob(os.path.join(cal, "review", "*_[0-9].jpg")))
    if rev:
        n = title_card("Then every effect, on the helmet",
                       "I froze each one for a photo and subtracted a dark "
                       "frame, so you only see the LEDs.",
                       int(fps * 2.4), tmp, n)
        if len(rev) > 320:
            step = len(rev) / 320.0
            rev = [rev[int(i * step)] for i in range(320)]
        n, _ = add_frames(rev, "The presets, photographed one at a time", 4, tmp,
                          n, True, "frame %d of %d")

    n = title_card("vortex1.dev/mau5-simulator.html",
                   "The simulator runs in a browser. Code: "
                   "github.com/vortexcodes/deadmau5-helmet",
                   int(fps * 3.2), tmp, n)
    return n


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--acts", nargs="*", default=None,
                    help="subset of: " + ", ".join(a[0] for a in ACTS))
    ap.add_argument("--no-level", dest="level", action="store_false", default=True)
    ap.add_argument("--max-per-act", type=int, default=700)
    ap.add_argument("--explain", action="store_true",
                    help="build the calibration explainer: the localisation "
                         "pass accumulated so the helmet draws itself, then "
                         "the bar sweep, then the presets")
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
        if a.explain:
            n = build_explainer(tmp, a.fps)
            print("  %d frames -> %.0fs at %d fps" % (n, n / float(a.fps), a.fps))
            cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                   "-framerate", str(a.fps), "-i", os.path.join(tmp, "%06d.jpg"),
                   "-vf", "format=yuv420p", "-c:v", "libx264", "-crf", "23",
                   "-movflags", "+faststart", a.out]
            subprocess.run(cmd, check=True)
            print("\n%s  (%.1f MB)" % (a.out, os.path.getsize(a.out) / 1e6))
            return 0
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
