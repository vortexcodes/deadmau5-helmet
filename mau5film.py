#!/usr/bin/env python3
"""mau5film -- how the map of the helmet was found, as a short film.

Ninety seconds, in the order it actually happened, drawn from the data
rather than described: the CAD's slots, the walk, the camera passes,
the map that graded its own homework, the second camera, the slot
alignment filling in strip by strip, the ears inside their tubes, and
the old map against the new from every side.  The footage is the first
night's; everything else is rendered from the files in data/.

The look is the website's -- a drawing sheet, ink and blue, brass for
detail -- so a clip of it can sit on the project page without looking
like it came from somewhere else.  Dark only where LEDs are lit.

    python3 mau5film.py                       # data/cal/localisation.mp4
    python3 mau5film.py --scenes 7 8          # just those, for iterating
    python3 mau5film.py --stills media/       # and a still from each scene
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import shutil
import subprocess
import tempfile
import warnings

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

import mau5slots

warnings.filterwarnings("ignore", message=".*encountered in matmul")

HERE = os.path.dirname(os.path.abspath(__file__))
CAL = os.path.join(HERE, "data", "cal")
OUT = os.path.join(CAL, "localisation.mp4")
# The daylight photograph from the high camera pose, which the ears
# scene draws the CAD outline on.  It used to be read from eye.jpg, but
# that is mau5eye's live output: rewritten with every frame the camera
# pushes, ignored by git, and by the next camera session a dark room
# seen from somewhere else -- so the scene drew the high camera's
# outline over an unrelated frame, and showed the CAD missing the ears
# it says it lands on.  Nothing writes this file; it is saved here by
# hand, from the high pose, and without it the scene leaves the photo
# out rather than use whatever the camera last saw.
HIGH_PHOTO = os.path.join(CAL, "high_pose_daylight.jpg")
W, H = 1280, 720
FOOT = 96                      # the title strip along the bottom
FPS = 30

# the site's tokens (site.css), light theme
PAPER = (242, 244, 245)
SURFACE = (255, 255, 255)
INK = (22, 25, 29)
INK2 = (59, 66, 74)
MUTED = (100, 109, 119)
RULE = (210, 215, 220)
ACCENT = (35, 71, 198)
BRASS = (141, 100, 32)
RED = (194, 53, 63)
DARK = (11, 13, 16)


def font(size, title=False, weight="Regular"):
    """DIN Condensed for headings, Avenir Next for text -- the nearest
    things on a Mac to the site's Big Shoulders and Atkinson."""
    faces = {"Regular": 7, "Medium": 5, "Demi Bold": 2}
    tries = ([("/System/Library/Fonts/Supplemental/DIN Condensed Bold.ttf", 0)] if title
             else []) + [("/System/Library/Fonts/Avenir Next.ttc", faces.get(weight, 7)),
                         ("/System/Library/Fonts/Helvetica.ttc", 0)]
    for p, i in tries:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size, index=i)
            except OSError:
                continue
    return ImageFont.load_default()


F_TITLE = font(40, True)
F_BIG = font(120, True)
F_MID = font(64, True)
F_BODY = font(21)
F_EM = font(21, weight="Demi Bold")
F_SMALL = font(17, weight="Medium")
F_NUM = font(34, True)


# ------------------------------------------------------------ geometry
class View:
    """An orthographic camera on the CAD frame (+z up, face along -y).

    yaw 0 looks at the face, 90 at the audience's right; pitch lifts the
    camera.  Orthographic because these are drawings, not photographs:
    a slot should be the same size wherever it is.
    """

    # the middle of the whole helmet, ears included, rather than the
    # middle of the head: centring on the head puts the ears off the top
    MID = np.array([0.0, 40.0, 120.0])

    def __init__(self, yaw, pitch=8.0, scale=1.0, cx=880, cy=(H - FOOT) / 2 + 10):
        a, e = math.radians(yaw), math.radians(pitch)
        self.d = np.array([math.sin(a) * math.cos(e), -math.cos(a) * math.cos(e), math.sin(e)])
        r = np.cross([0.0, 0.0, 1.0], self.d)
        self.r = r / np.linalg.norm(r)
        self.u = np.cross(self.d, self.r)
        self.s, self.cx, self.cy = scale, cx, cy
        self.off = np.array([self.MID @ self.r, self.MID @ self.u])

    def __call__(self, P):
        P = np.atleast_2d(P)
        return np.c_[self.cx + self.s * (P @ self.r - self.off[0]),
                     self.cy - self.s * (P @ self.u - self.off[1])]

    def depth(self, P):
        return np.atleast_2d(P) @ self.d


class Model:
    """Everything the film draws, loaded once."""

    def __init__(self):
        rows, self.slots, self.strips, self.order = mau5slots.load_cad()
        self.cad_rows = rows
        self.chain = np.array([r["chain"] for r in rows])
        V, F = mau5slots.load_mesh()
        self.V, self.F = V, F
        parts = mau5slots.mesh_parts(V, F)
        self.part = np.full(len(F), "", dtype=object)
        for k, m in parts.items():
            self.part[m] = k
        T = V[F]
        n = np.cross(T[:, 1] - T[:, 0], T[:, 2] - T[:, 0])
        self.fn = n / (np.linalg.norm(n, axis=1, keepdims=True) + 1e-12)
        e = np.concatenate([F[:, [0, 1]], F[:, [1, 2]], F[:, [2, 0]]])
        f = np.tile(np.arange(len(F)), 3)
        k = np.sort(e, axis=1)
        o = np.lexsort((k[:, 1], k[:, 0]))
        k, f = k[o], f[o]
        same = np.all(k[1:] == k[:-1], axis=1)
        i = np.where(same)[0]
        self.e, self.f1, self.f2 = k[i], f[i], f[i + 1]
        crease = (self.fn[self.f1] * self.fn[self.f2]).sum(1) < math.cos(math.radians(35))
        # the shell's creases are its slot recesses -- 30,000 lines that
        # draw as grey fuzz -- so the shell is drawn by its outline and
        # the slots themselves; the ears and visor keep their creases
        keep = crease & (self.part[self.f1] != "shell")
        self.crease = self.e[keep]
        # open edges: the rims of the shell's openings
        once = np.ones(len(k), bool)
        once[i] = False
        once[i + 1] = False
        self.open = k[once]

        self.new = load_map(os.path.join(CAL, "pixel_map.csv"))
        old = os.path.join(CAL, "pixel_map_before_slots.csv")
        self.old = load_map(old) if os.path.exists(old) else None
        self.rep = json.load(open(os.path.join(CAL, "slots.json")))
        self.walk = json.load(open(os.path.join(CAL, "walk_session.json")))

    def silhouette(self, view):
        """Edges between faces turned towards the view and away from it.

        Not on the shell, whose slot recesses turn every way and would
        draw a silhouette at every slot; the shell gets `outline`.
        """
        front = self.fn @ view.d > 0
        m = (front[self.f1] != front[self.f2]) & (self.part[self.f1] != "shell")
        return self.e[m]

    def outline(self, view, R=177.17, z_cut=-140.0):
        """The shell's own silhouette: a great circle, where the print exists."""
        th = np.linspace(0, 2 * np.pi, 361)
        P = R * (np.outer(np.cos(th), view.r) + np.outer(np.sin(th), view.u))
        keep = P[:, 2] > z_cut
        segs, cur = [], []
        for p, k in zip(view(P), keep):
            if k:
                cur.append(tuple(p))
            elif len(cur) > 1:
                segs.append(cur)
                cur = []
        if len(cur) > 1:
            segs.append(cur)
        return segs


def load_map(path):
    rows = list(csv.DictReader(open(path)))
    return {"xyz": np.array([[float(r[k]) for k in "xyz"] for r in rows]),
            "region": np.array([r["region"] for r in rows]),
            "strip": [r["strip"] for r in rows],
            "group": np.array([int(r["group"]) for r in rows])}


# -------------------------------------------------------------- drawing
def sheet(dark=False):
    im = Image.new("RGB", (W, H), DARK if dark else PAPER)
    return im, ImageDraw.Draw(im, "RGBA")


def foot(im, title, sub):
    """The caption strip along the bottom."""
    d = ImageDraw.Draw(im, "RGBA")
    y0 = H - FOOT
    d.rectangle([0, y0, W, H], fill=SURFACE)
    d.line([0, y0, W, y0], fill=INK, width=2)
    d.text((28, y0 + 12), title, font=F_TITLE, fill=INK)
    # one line, so it shrinks to fit rather than running off the frame
    size, f = 21, F_BODY
    while d.textlength(sub, font=f) > W - 56 and size > 15:
        size -= 1
        f = font(size)
    d.text((28, y0 + 56), sub, font=f, fill=INK2)
    return im


def lines(d, view, P, E, fill, width=1):
    if not len(E):
        return
    a, b = view(P[E[:, 0]]), view(P[E[:, 1]])
    for (x0, y0), (x1, y1) in zip(a, b):
        d.line([x0, y0, x1, y1], fill=fill, width=width)


def drawing(d, M, view, ink=(22, 25, 29, 150), crease=(22, 25, 29, 60)):
    """The CAD as a line drawing: outline, openings, and the ears' tubes."""
    lines(d, view, M.V, M.crease, crease)
    lines(d, view, M.V, M.open, ink)
    lines(d, view, M.V, M.silhouette(view), ink, 2)
    for seg in M.outline(view):
        d.line(seg, fill=ink, width=2)


def dots(d, pts, r, fill, outline=None):
    for x, y in pts:
        d.ellipse([x - r, y - r, x + r, y + r], fill=fill, outline=outline)


def glow(im, pts, colors, r=3.0, blur=5.0, gain=1.0):
    """Lit LEDs: a core and a halo, added to the picture."""
    core = Image.new("RGB", (W, H), (0, 0, 0))
    d = ImageDraw.Draw(core)
    for (x, y), c in zip(pts, colors):
        d.ellipse([x - r, y - r, x + r, y + r], fill=tuple(int(v) for v in c))
    halo = core.filter(ImageFilter.GaussianBlur(blur))
    a = np.asarray(im, np.float32) + gain * (np.asarray(halo, np.float32) * 2.2
                                            + np.asarray(core, np.float32))
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def hue(h):
    h = (h % 1.0) * 6
    i, f = int(h), h - int(h)
    return [(255, 255 * f, 0), (255 * (1 - f), 255, 0), (0, 255, 255 * f),
            (0, 255 * (1 - f), 255), (255 * f, 0, 255), (255, 0, 255 * (1 - f))][i % 6]


def ease(t):
    t = min(max(t, 0.0), 1.0)
    return t * t * (3 - 2 * t)


def label(d, xy, text, fill=INK, f=F_SMALL, anchor="la"):
    d.text(xy, text, font=f, fill=fill, anchor=anchor)


# --------------------------------------------------------------- scenes
def s_title(M, n):
    v = View(0, 6, 0.92, cx=930, cy=330)
    for i in range(n):
        im, d = sheet()
        drawing(d, M, v, ink=(22, 25, 29, 110), crease=(22, 25, 29, 40))
        dots(d, v(M.slots[M.chain == "B"]), 1.6, (35, 71, 198, 150))
        d.text((70, 200), "Finding", font=F_BIG, fill=INK)
        d.text((70, 310), "622 LEDs", font=F_BIG, fill=INK)
        d.text((74, 450), "How I worked out where every LED on my helmet is,", font=F_BODY, fill=INK2)
        d.text((74, 480), "including the map I got wrong first.", font=F_BODY, fill=INK2)
        d.line([74, 540, 380, 540], fill=BRASS, width=2)
        d.text((74, 552), "MAU5HEAD V2", font=F_SMALL, fill=BRASS)
        yield im


def s_slots(M, n):
    for i in range(n):
        t = i / max(n - 1, 1)
        v = View(-28 + 56 * ease(t), 10, 0.88)
        im, d = sheet()
        drawing(d, M, v)
        back = M.chain == "A"
        order = np.argsort(v.depth(M.slots))
        P = v(M.slots)
        for k in order:
            x, y = P[k]
            c = (100, 109, 119, 90) if back[k] else (35, 71, 198, 230)
            d.ellipse([x - 2.2, y - 2.2, x + 2.2, y + 2.2], fill=c)
        label(d, (60, 60), "948 slots in the print", INK, F_MID)
        label(d, (64, 140), "blue: the 399 on the front, where LEDs went", ACCENT, F_BODY)
        label(d, (64, 170), "grey: the back, still empty", MUTED, F_BODY)
        yield foot(im, "Every LED has a place in the print",
                   "948 slots in the shell, and three tubes and a rim in each ear. "
                   "The CAD doesn't say which LED ended up where.")


def s_wiring(M, n):
    v = View(-18, 10, 0.88)
    seq = [s for nm in M.order for s in M.strips[nm]]
    P = v(M.slots)
    for i in range(n):
        k = int(len(seq) * ease(i / (n * 0.85)))
        im, d = sheet()
        drawing(d, M, v)
        dots(d, P[M.chain == "B"], 1.8, (100, 109, 119, 120))
        if k > 1:
            pts = [tuple(P[s]) for s in seq[:k]]
            d.line(pts, fill=BRASS + (230,), width=2)
            x, y = pts[-1]
            d.ellipse([x - 6, y - 6, x + 6, y + 6], fill=RED)
        label(d, (60, 60), "One data line", INK, F_MID)
        label(d, (64, 140), "the order the CAD meant the strips to be wired in", BRASS, F_BODY)
        label(d, (64, 170), "%d of 399 slots" % k, MUTED, F_BODY)
        yield foot(im, "622 LEDs on one wire",
                   "An LED's number is just how far along the wire it sits. This is the order "
                   "I meant to wire them in, and I didn't stick to it everywhere.")


def footage(path, t0, t1, n):
    """Frames from an earlier timelapse, its own caption cropped away."""
    tmp = tempfile.mkdtemp(prefix="mau5film_")
    try:
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(t0), "-to", str(t1),
                        "-i", path, "-vf", "fps=%f,crop=1280:640:0:0,scale=1280:%d" %
                        (n / max(t1 - t0, 0.1), H - FOOT + 20),
                        os.path.join(tmp, "%05d.jpg")], check=True)
        files = sorted(os.listdir(tmp))
        for k in range(n):
            f = files[min(int(k * len(files) / n), len(files) - 1)]
            src = Image.open(os.path.join(tmp, f)).convert("RGB")
            im = Image.new("RGB", (W, H), DARK)
            im.paste(src, (0, -10))
            yield im
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def s_night(M, n):
    src = os.path.join(CAL, "session_timelapse.mp4")
    secs = sum(1 for s in M.walk["sections"])
    # 2.6-10.6 s of the session timelapse: the room, before dark,
    # between its title cards at 2.3 s and 10.8 s
    for im in footage(src, 2.6, 10.6, n):
        yield foot(im, "The first night",
                   "Before any camera, I lit each strip in turn and wrote down its first and "
                   "last LED: %d sections." % secs)


def s_locate(M, n):
    src = os.path.join(CAL, "session_timelapse.mp4")
    # the dark stretch, up to the next title card at 38 s
    for im in footage(src, 31.8, 37.9, n):
        yield foot(im, "Then one LED at a time",
                   "Each one lit alone in a dark room while the camera logged the centre of its "
                   "glow. Later I did all 622 again from a second spot.")


def s_mistake(M, n):
    v = View(90, 4, 1.05, cx=860)
    if M.old is None:
        return
    old = M.old["xyz"][:399]
    near = np.linalg.norm(old[:, None] - M.slots[None], axis=-1).argmin(1)
    for i in range(n):
        t = i / max(n - 1, 1)
        im, d = sheet()
        drawing(d, M, v)
        S = v(M.slots)
        vis = v.depth(M.slots) > -40
        dots(d, S[vis], 2.2, (100, 109, 119, 110))
        O = v(old)
        if t > 0.35:
            a = int(255 * ease((t - 0.35) / 0.3))
            for (x0, y0), (x1, y1) in zip(O, S[near]):
                d.line([x0, y0, x1, y1], fill=RED + (a,), width=1)
        dots(d, O, 2.6, RED + (230,))
        ears = M.old["xyz"][399:]
        dots(d, v(ears), 2.2, (194, 53, 63, 160))
        label(d, (60, 60), "My first map", INK, F_MID)
        label(d, (64, 140), "from the side: red is where it put each LED,", INK2, F_BODY)
        label(d, (64, 170), "grey is where the print has room for one", INK2, F_BODY)
        if t > 0.55:
            label(d, (64, 230), "matched the camera it came from to 0.02 px", RED, F_BODY)
            label(d, (64, 260), "the ears came out flat, every LED at the same depth", RED, F_BODY)
        yield foot(im, "It only looked right from the front",
                   "That's where the camera was. From the side, most LEDs sat between slots, "
                   "some of them 113 mm off.")


def s_cameras(M, n):
    cams = {k: np.array(v) for k, v in M.rep["cameras"].items()}
    C = {k: mau5slots.camera_centre(m) for k, m in cams.items()}
    tri = triangulate(M, cams)
    r = np.linalg.norm(tri, axis=1)
    for i in range(n):
        t = i / max(n - 1, 1)
        v = View(0, 89.9, 0.26, cx=470, cy=150)
        im, d = sheet()
        # top view, the cameras to scale
        for (x, y) in v(M.slots[M.chain == "B"]):
            d.point((x, y), fill=ACCENT)
        lines(d, v, M.V, M.silhouette(v), (22, 25, 29, 160))
        for k, c in C.items():
            x, y = v(c)[0]
            hx, hy = v(np.zeros(3))[0]
            d.line([x, y, hx, hy], fill=BRASS + (160,), width=1)
            d.rectangle([x - 9, y - 7, x + 9, y + 7], fill=INK)
            label(d, (x + 14, y - 10), "%s camera" % k, INK, F_SMALL)
        label(d, (60, 50), "Two views", INK, F_MID)
        label(d, (64, 120), "from above, to scale", MUTED, F_BODY)
        # radius histogram, appearing
        if t > 0.3:
            a = ease((t - 0.3) / 0.4)
            x0, y0, w, h = 760, 160, 440, 300
            d.rectangle([x0, y0, x0 + w, y0 + h], outline=INK, width=2, fill=SURFACE)
            label(d, (x0 + 14, y0 + 10), "distance from the head's centre, triangulated", INK, F_SMALL)
            bins = np.arange(160, 190.5, 1.0)
            hist, _ = np.histogram(r, bins=bins)
            bw = (w - 40) / len(hist)
            top = hist.max()
            for k, c in enumerate(hist):
                bh = (h - 90) * c / top * a
                d.rectangle([x0 + 20 + k * bw, y0 + h - 40 - bh,
                             x0 + 20 + (k + 1) * bw - 2, y0 + h - 40], fill=ACCENT)
            def xof(mm):
                return x0 + 20 + (mm - bins[0]) / (bins[-1] - bins[0]) * (w - 40)
            d.line([xof(173.04), y0 + 40, xof(173.04), y0 + h - 40], fill=BRASS, width=2)
            label(d, (xof(173.04) + 6, y0 + 42), "CAD 173.0", BRASS, F_SMALL)
            label(d, (x0 + 20, y0 + h - 32), "160 mm", MUTED, F_SMALL)
            label(d, (x0 + w - 20, y0 + h - 32), "190", MUTED, F_SMALL, "ra")
            if t > 0.6:
                label(d, (x0 + 14, y0 + h + 14), "measured: median %.1f mm, nothing assumed"
                      % np.median(r), INK, F_BODY)
        yield foot(im, "A second camera, 34 degrees away",
                   "Two views give a point where one only gives a ray. The shell LEDs landed "
                   "0.3 mm from the CAD's sphere, so the cameras were fine.")


def triangulate(M, cams):
    meas = {k: mau5slots.load_centroids(p) for k, p in mau5slots.POSES.items()}
    a, b = cams["front"], cams["high"]
    out = []
    for i in range(398):
        if i in meas["front"] and i in meas["high"]:
            (u1, v1), (u2, v2) = meas["front"][i], meas["high"][i]
            A = np.array([u1 * a[2] - a[0], v1 * a[2] - a[1], u2 * b[2] - b[0], v2 * b[2] - b[1]])
            X = np.linalg.svd(A)[2][-1]
            X = X[:3] / X[3]
            ok = True
            for M_, (u, v) in ((a, (u1, v1)), (b, (u2, v2))):
                q = mau5slots.project(M_, X[None])[0]
                ok &= math.hypot(q[0] - u, q[1] - v) < 4
            if ok:
                out.append(X)
    return np.array(out)


def s_align(M, n):
    v = View(-24, 12, 0.92)
    new = M.new["xyz"][:398]
    grp = M.new["group"][:398]
    S = v(M.slots)
    P = v(new)
    order_names = M.rep["wiring_order"]
    empty = [s for s in range(len(M.slots))
             if M.cad_rows[s]["strip"] == "strip_B04_upper_led580-591"
             and M.cad_rows[s]["led"] == "591"]
    run = int(n * 0.82)
    for i in range(n):
        k = min(398, int(398 * i / run))
        im, d = sheet(dark=True)
        lines(d, v, M.V, M.silhouette(v), (180, 190, 200, 70))
        lines(d, v, M.V, M.crease, (180, 190, 200, 35))
        for seg in M.outline(v):
            d.line(seg, fill=(180, 190, 200, 55), width=2)
        dots(d, S[M.chain == "B"], 1.6, (120, 128, 140, 120))
        cols = [hue(j / 398 * 0.85) for j in range(k)]
        im = glow(im, P[:k], cols, r=3.2, blur=4.0, gain=0.9)
        d = ImageDraw.Draw(im, "RGBA")
        if k:
            g = grp[k - 1]
            nm = order_names[g][6:9]
            label(d, (60, 50), "Which slot is each LED in?", (232, 235, 238), F_MID)
            label(d, (64, 122), "LED %d  ·  strip %s" % (k - 1, nm), (210, 168, 90), F_BODY)
            if 124 <= k - 1 <= 140:
                x, y = S[empty[0]]
                d.ellipse([x - 9, y - 9, x + 9, y + 9], outline=(240, 113, 122), width=3)
                label(d, (x + 14, y - 12), "empty slot: B04 is 11 LEDs, not 12", (240, 113, 122), F_SMALL)
            if 172 <= k - 1 <= 200:
                label(d, (64, 152), "at the ear mount the strips run B10, B09, B12, B11", (138, 163, 255), F_BODY)
            if 302 <= k - 1 <= 330:
                label(d, (64, 152), "and the mirror image on the other side: B28, B27, B30, B29", (138, 163, 255), F_BODY)
        if i >= run:
            a = int(255 * ease((i - run) / (n - run) * 2))
            x0, y0 = 60, 210
            d.rectangle([x0, y0, x0 + 470, y0 + 250], fill=(25, 29, 33, a), outline=(232, 235, 238, a), width=2)
            rows = ["398 LEDs in 398 slots", "1 slot empty", "each camera alone: same answer, all 398",
                    "error where a camera sees the LED square-on:",
                    "2 px  (the first map: 15)"]
            for j, s in enumerate(rows):
                label(d, (x0 + 20, y0 + 20 + j * 44), s, (232, 235, 238, a), F_BODY)
        yield foot(im, "Lining the chain up with the wiring",
                   "Each LED is the next slot on its strip, or skips an empty one, or starts "
                   "the next strip from either end. A slot can only be used once.")


def s_walk(M, n):
    secs = [(s["start"], s["end"]) for s in M.walk["sections"] if s["end"] <= 397]
    grp = M.new["group"][:398]
    cam = []
    a = 0
    for i in range(1, 399):
        if i == 398 or grp[i] != grp[i - 1]:
            cam.append((a, i - 1))
            a = i
    # the walk's list begins at its first boundary, 6; the chain itself
    # begins at 0 whatever anyone wrote down
    walk_starts = {0} | {s for s, e in secs}
    cam_starts = {s for s, e in cam}
    for i in range(n):
        t = ease(i / max(n * 0.6, 1))
        im, d = sheet()
        label(d, (60, 50), "The cameras against my notes", INK, F_MID)
        x0, x1 = 70, W - 70
        def X(k):
            return x0 + (x1 - x0) * k / 398
        for row, (name, spans, y) in enumerate((("my notes", secs, 230),
                                                ("the cameras", cam, 360))):
            label(d, (x0, y - 34), name, INK2, F_BODY)
            for j, (s, e) in enumerate(spans):
                if X(s) > x0 + (x1 - x0) * t:
                    continue
                c = (ACCENT if j % 2 else (98, 128, 214)) if row else (BRASS if j % 2 else (190, 150, 80))
                d.rectangle([X(s), y, X(e + 1) - 1, y + 70], fill=c)
        both = sorted(walk_starts & cam_starts)
        diff = sorted(walk_starts ^ cam_starts)
        if t >= 1:
            for s in diff:
                d.line([X(s), 210, X(s), 450], fill=RED, width=2)
            label(d, (x0, 470), "%d strips from the cameras, %d from the walk: %d boundaries "
                  "in exactly the same place" % (len(cam_starts), len(walk_starts), len(both)),
                  INK, F_EM)
            label(d, (x0, 502), "the one difference (red) is a single LED among the two-LED "
                  "strips at the chin", MUTED, F_BODY)
        label(d, (x0, 160), "chain index 0", MUTED, F_SMALL)
        label(d, (x1, 160), "397", MUTED, F_SMALL, "ra")
        yield foot(im, "The notes from the first night had it right",
                   "Shell ends at 397, one strip has 11 LEDs, the mount strips run out of order. "
                   "My first map had replaced all three with the CAD's numbers.")


def s_ears(M, n):
    if not os.path.exists(HIGH_PHOTO):
        # No photograph, no claim about one: the tubes fill the scene.
        print("  ears: no %s, so the CAD outline is not drawn on a photo"
              % os.path.relpath(HIGH_PHOTO, HERE))
        photo, half = None, 0
    else:
        photo, half = Image.open(HIGH_PHOTO).convert("RGB"), n // 2
        cams = {k: np.array(v) for k, v in M.rep["cameras"].items()}
        hi = cams["high"]
        ears = (M.part == "ear1") | (M.part == "ear2")
        T = M.V[M.F[ears]]
        q = mau5slots.project(hi, T.reshape(-1, 3)).reshape(-1, 3, 2)
        over = Image.new("L", photo.size, 0)
        od = ImageDraw.Draw(over)
        for tr in q:
            od.polygon([tuple(p) for p in tr], fill=255)
        # thick enough to read at video size
        edge = np.asarray(over.filter(ImageFilter.FIND_EDGES).filter(ImageFilter.MaxFilter(5))) > 0
    for i in range(n):
        if i < half:
            im = photo.resize((W, H))
            a = np.asarray(im, np.float32) * 0.85
            e = np.asarray(Image.fromarray((edge * 255).astype(np.uint8)).resize((W, H))) > 40
            a[e] = (240, 60, 70)
            im = Image.fromarray(a.astype(np.uint8))
            d = ImageDraw.Draw(im, "RGBA")
            d.rectangle([40, 30, 640, 130], fill=(242, 244, 245, 230))
            label(d, (60, 40), "The CAD's ears, on a photo", INK, F_TITLE)
            label(d, (60, 88), "red: the CAD outline, drawn through the high camera", INK2, F_BODY)
        else:
            t = (i - half) / max(n - half - 1, 1)
            v = View(20, 18, 0.9, cx=910)
            im, d = sheet(dark=True)
            lines(d, v, M.V, M.silhouette(v), (180, 190, 200, 80))
            lines(d, v, M.V, M.crease, (180, 190, 200, 60))
            for seg in M.outline(v):
                d.line(seg, fill=(180, 190, 200, 60), width=2)
            idx = np.where(M.new["region"] != "shell")[0]
            k = int(len(idx) * ease(t / 0.8))
            P = v(M.new["xyz"][idx[:k]])
            cols = [(255, 120, 60) if M.new["region"][j].endswith("rim") else (90, 200, 255)
                    for j in idx[:k]]
            im = glow(im, P, cols, r=3.0, blur=4.0)
            d = ImageDraw.Draw(im, "RGBA")
            label(d, (60, 50), "Inside the tubes", (232, 235, 238), F_MID)
            label(d, (64, 122), "blue: out and back along three tubes  ·  orange: the rim",
                  (200, 205, 210), F_BODY)
        yield foot(im, "The ears stay where the CAD has them",
                   ("The outline lands on the real ears, so the cameras only pick where along "
                    "which tube each LED sits. They can measure that much.") if photo is not None else
                   ("The cameras only pick where along which tube each LED sits. "
                    "They can measure that much."))


def s_compare(M, n):
    if M.old is None:
        return
    for i in range(n):
        yaw = -30 + 360 * i / n
        im, d = sheet(dark=True)
        for side, (name, mp) in enumerate((("before", M.old), ("after", M.new))):
            v = View(yaw, 12, 0.62, cx=330 + side * 620, cy=330)
            lines(d, v, M.V, M.silhouette(v), (180, 190, 200, 70))
            lines(d, v, M.V, M.crease, (180, 190, 200, 30))
            for seg in M.outline(v):
                d.line(seg, fill=(180, 190, 200, 55), width=2)
            label(d, (330 + side * 620, 40), name, (232, 235, 238), F_MID, "ma")
        d = None
        for side, mp in enumerate((M.old, M.new)):
            v = View(yaw, 12, 0.62, cx=330 + side * 620, cy=330)
            X = mp["xyz"]
            dep = v.depth(X)
            cols = []
            for j in range(len(X)):
                base = (90, 160, 255) if mp["region"][j] == "shell" else (255, 140, 70)
                k = 0.45 + 0.55 * (dep[j] - dep.min()) / (np.ptp(dep) or 1)
                cols.append(tuple(c * k for c in base))
            im = glow(im, v(X), cols, r=2.4, blur=3.0, gain=0.8)
        yield foot(im, "Before and after, all the way round",
                   "Left is the first map, with flat ears and LEDs between slots. Right is the "
                   "final one, with every LED in a slot or a tube.")


def s_end(M, n):
    v = View(0, 6, 0.6, cx=1000, cy=330)
    for i in range(n):
        im, d = sheet()
        drawing(d, M, v, ink=(22, 25, 29, 90), crease=(22, 25, 29, 35))
        label(d, (70, 220), "Try it", INK, F_BIG)
        label(d, (74, 370), "vortex1.dev/mau5-simulator.html", ACCENT, F_TITLE)
        label(d, (74, 430), "code: github.com/vortexcodes/deadmau5-helmet", INK2, F_BODY)
        label(d, (74, 462), "the map comes from mau5slots.py", INK2, F_BODY)
        yield im


SCENES = [
    (s_title, 3.0), (s_slots, 6.0), (s_wiring, 6.5), (s_night, 7.0),
    (s_locate, 7.0), (s_mistake, 9.0), (s_cameras, 8.0), (s_align, 16.0),
    (s_walk, 7.0), (s_ears, 10.0), (s_compare, 12.0), (s_end, 3.5),
]


def render(scenes, out, stills=None, fps=FPS):
    M = Model()
    tmp = tempfile.mkdtemp(prefix="mau5film_frames_")
    try:
        n = 0
        for k in scenes:
            fn, secs = SCENES[k]
            frames = int(secs * fps)
            first = n
            for im in fn(M, frames):
                im.save(os.path.join(tmp, "%06d.jpg" % n), quality=92)
                n += 1
            if stills and n > first:
                os.makedirs(stills, exist_ok=True)
                pick = first + int((n - first) * 0.8)
                shutil.copyfile(os.path.join(tmp, "%06d.jpg" % min(pick, n - 1)),
                                os.path.join(stills, "loc-%02d-%s.jpg" % (k, fn.__name__[2:])))
            print("  %-12s %4d frames" % (fn.__name__[2:], n - first))
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(fps),
                        "-i", os.path.join(tmp, "%06d.jpg"), "-c:v", "libx264",
                        "-pix_fmt", "yuv420p", "-crf", "21", "-preset", "slow",
                        "-movflags", "+faststart", out], check=True)
        print("wrote %s  (%.1f s, %.1f MB)" % (os.path.relpath(out, HERE), n / fps,
                                               os.path.getsize(out) / 1e6))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter,
                                 epilog=__doc__)
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--scenes", nargs="*", type=int, default=None,
                    help="scene numbers, 0-based, in SCENES order")
    ap.add_argument("--stills", default=None, help="also save one still per scene here")
    a = ap.parse_args(argv)
    scenes = a.scenes if a.scenes is not None else list(range(len(SCENES)))
    render(scenes, a.out, a.stills)


if __name__ == "__main__":
    main()
