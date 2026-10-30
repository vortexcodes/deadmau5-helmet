#!/usr/bin/env python3
"""mau5cal -- find out what the helmet actually is, with a camera.

The wiring diagram is no longer the truth: the strip got routed by hand, the
back has no pixels, the ears are a different strip, and most of it is now
covered. So instead of describing the helmet, measure it. Point a camera at
it, light one LED at a time, and write down where each one landed.

    ./mau5cal.py probe --host 4.3.2.1          what the controller says it has
    ./mau5cal.py live  --host 4.3.2.1          poke pixels by hand
    ./mau5cal.py order --host 4.3.2.1          which LEDs have swapped colours
    ./mau5cal.py scan  --host 4.3.2.1 --view front
    ./mau5cal.py scan  --host 4.3.2.1 --view side
    ./mau5cal.py solve                          -> data/pixel_map.csv

``scan`` is the long one and wants a still camera and a dark-ish room. It saves
everything it captured to data/cal/, so ``solve`` can be re-run with different
settings without going near the helmet again.

Nothing here needs OpenCV. Capture is ffmpeg reading the webcam; the rest is
numpy.

A note on macOS: the first time anything grabs the camera, the OS asks the app
running it for permission. Run this from Terminal with a human present for the
first scan, click Allow, and it will not ask again.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import shlex
import subprocess
import sys
import threading
import time

import numpy as np

import mau5wled

HERE = os.path.dirname(os.path.abspath(__file__))
CAL_DIR = os.path.join(HERE, "data", "cal")


# --------------------------------------------------------------------------
# camera
# --------------------------------------------------------------------------
class Camera:
    """A webcam, read as raw frames out of ffmpeg.

    A reader thread keeps only the newest frame, because a webcam pipeline
    buffers: if you set an LED and immediately read, you get a frame from
    before the change. ``grab(fresh=n)`` waits for n genuinely new frames.
    """

    def __init__(self, device="0", width=1280, height=720, fps=30,
                 backend=None, extra=None):
        self.device = str(device)
        self.w, self.h, self.fps = int(width), int(height), int(fps)
        self.backend = backend or ("avfoundation" if sys.platform == "darwin"
                                   else "v4l2")
        self.extra = extra or []
        self.proc = None
        self._frame = None
        self._count = 0
        self._lock = threading.Condition()
        self._stop = False
        self._err = []

    def _argv(self):
        inp = ("%s:none" % self.device if self.backend == "avfoundation"
               else self.device)
        return (["ffmpeg", "-hide_banner", "-loglevel", "error",
                 "-f", self.backend,
                 "-framerate", str(self.fps),
                 "-video_size", "%dx%d" % (self.w, self.h)]
                + self.extra +
                ["-i", inp, "-pix_fmt", "rgb24", "-f", "rawvideo", "-"])

    def start(self, timeout=12.0):
        argv = self._argv()
        self.proc = subprocess.Popen(argv, stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE)
        threading.Thread(target=self._pump, daemon=True).start()
        threading.Thread(target=self._drain_err, daemon=True).start()
        t0 = time.monotonic()
        with self._lock:
            while self._count == 0 and time.monotonic() - t0 < timeout:
                self._lock.wait(0.2)
                if self.proc.poll() is not None:
                    break
        if self._count == 0:
            self.stop()
            msg = "".join(self._err)[-500:]
            raise SystemExit(
                "no frames from the camera in %.0f s.\n"
                "  command: %s\n"
                "  ffmpeg said: %s\n"
                "  On macOS the first camera access needs permission -- run this\n"
                "  from Terminal with someone there to click Allow, then retry.\n"
                "  `./mau5cal.py cameras` lists what ffmpeg can see."
                % (timeout, " ".join(shlex.quote(a) for a in argv),
                   msg.strip() or "(nothing)"))
        return self

    def _pump(self):
        n = self.w * self.h * 3
        while not self._stop:
            buf = self.proc.stdout.read(n)
            if not buf or len(buf) < n:
                break
            f = np.frombuffer(buf, np.uint8).reshape(self.h, self.w, 3)
            with self._lock:
                self._frame = f
                self._count += 1
                self._lock.notify_all()

    def _drain_err(self):
        for line in iter(self.proc.stderr.readline, b""):
            self._err.append(line.decode("utf-8", "replace"))

    def grab(self, fresh=2, timeout=None):
        """Return a frame captured at least ``fresh`` frames after now.

        None if that many have not arrived within ``timeout``.  It used
        to hand back the newest frame regardless, which is a frame from
        before the change the caller is waiting to see -- and once
        ffmpeg has died, the same frame for every change from then on,
        so a scan recorded every later LED at the last one's position
        without a word.  A stale frame looks exactly like a live one.

        The default timeout is 5 s, or longer when ``fresh`` asks for
        more than half the nominal rate delivers in that time, so a
        generous ``scan --fresh`` is waited out rather than turned into
        a miss on every LED.
        """
        if timeout is None:
            timeout = max(5.0, 2.0 * max(1, fresh) / float(max(1, self.fps)))
        with self._lock:
            want = self._count + max(1, fresh)
            t0 = time.monotonic()
            while self._count < want and time.monotonic() - t0 < timeout:
                self._lock.wait(0.1)
            if self._count < want or self._frame is None:
                return None
            return self._frame.copy()

    def dark(self, n=3, fresh=2):
        """The mean of ``n`` fresh frames, as the reference with nothing lit.

        Raises rather than returning None: everything after it is
        measured against this frame, so there is no going on without it.
        """
        frames = [self.grab(fresh=fresh) for _ in range(n)]
        if any(f is None for f in frames):
            raise SystemExit("the camera stopped sending frames before the "
                             "dark reference was taken")
        return np.stack(frames).mean(0).astype(np.uint8)

    def stop(self):
        self._stop = True
        if self.proc and self.proc.poll() is None:
            self.proc.terminate()
            try:
                self.proc.wait(timeout=2)
            except Exception:
                self.proc.kill()

    def __enter__(self):
        return self.start()

    def __exit__(self, *a):
        self.stop()


def list_cameras():
    if sys.platform == "darwin":
        p = subprocess.run(["ffmpeg", "-hide_banner", "-f", "avfoundation",
                            "-list_devices", "true", "-i", ""],
                           capture_output=True, text=True)
        out = p.stderr
        keep = [l.split("] ", 1)[-1] for l in out.splitlines()
                if "AVFoundation" in l and "[" in l]
        return "\n".join(keep)
    return "(device listing is macOS-only here; on Linux try /dev/video*)"


# --------------------------------------------------------------------------
# blob finding
# --------------------------------------------------------------------------
def find_blob(frame, dark, window=81, min_score=18.0):
    """Where is the lit LED in this frame?

    Returns (u, v, score, rgb) or None.  Differencing against a dark reference
    removes the room, so this works without a blackout -- it only needs the
    LED to be the brightest *change*, not the brightest thing in the shot.
    """
    d = frame.astype(np.int16) - dark.astype(np.int16)
    np.clip(d, 0, None, out=d)
    lum = d.max(axis=2).astype(np.float32)
    peak = float(lum.max())
    if peak < min_score:
        return None
    vy, vx = np.unravel_index(int(np.argmax(lum)), lum.shape)
    h = window // 2
    y0, y1 = max(0, vy - h), min(lum.shape[0], vy + h + 1)
    x0, x1 = max(0, vx - h), min(lum.shape[1], vx + h + 1)
    patch = lum[y0:y1, x0:x1]
    mask = patch >= peak * 0.5
    if not mask.any():
        return None
    ys, xs = np.nonzero(mask)
    wts = patch[ys, xs]
    u = float((xs * wts).sum() / wts.sum()) + x0
    v = float((ys * wts).sum() / wts.sum()) + y0
    rgb = d[y0:y1, x0:x1][mask].mean(axis=0)
    return u, v, peak, tuple(float(c) for c in rgb)


# --------------------------------------------------------------------------
# scanning
# --------------------------------------------------------------------------
# How long measure_latency watches for one flash before calling it a
# miss.  mau5eye's first guess for the phone camera, which is twice the
# worst it was measured at (1.54 s) -- about 90 frames at 30 fps.  It
# used to look 11 frames ahead and then clamp what it found to 6, so a
# camera slower than that was scanned 6 frames after each change and
# every LED was recorded where the one before it had been.
LATENCY_WATCH_S = 3.0


def measure_latency(cam, pix, tries=6, watch=LATENCY_WATCH_S):
    """How many frames behind the camera is? Flash everything and watch.

    Raises when no flash is ever seen.  It used to return 3, a guess,
    and a scan run on a guessed latency reads every LED from the wrong
    frame with nothing to say so.
    """
    pix.clear()
    time.sleep(0.4)
    lag = []
    for _ in range(tries):
        pix.clear()
        time.sleep(0.25)
        # The reference has to be dark, and on a camera slower than the
        # pause above the last flash is still on screen: every later try
        # then compared lit against lit and saw nothing, holding the
        # helmet white for the whole watch.  Wait out what was measured.
        base = cam.grab(fresh=2 + (max(lag) if lag else 0))
        if base is None:
            break                                   # no camera: say so below
        base = base.astype(np.int16)
        pix.all((255, 255, 255))
        end = time.monotonic() + watch
        k = 0
        while time.monotonic() < end:
            f = cam.grab(fresh=1)
            if f is None:
                break
            k += 1
            if float(np.clip(f.astype(np.int16) - base, 0, None).mean()) > 4.0:
                lag.append(k)
                break
        pix.clear()
        time.sleep(0.2)
    pix.clear()
    if not lag:
        raise SystemExit(
            "the camera never saw the helmet flash (watched %.0f s, %d times).\n"
            "  Is it pointed at the helmet, and still sending frames?  If the\n"
            "  latency is known, `scan --fresh N` skips this measurement."
            % (watch, tries))
    # No ceiling: more frames than needed only makes a scan slower, and
    # fewer reads every LED from before it lit.
    return int(max(2, round(float(np.median(lag)) + 1)))


def scan_view(host, view, count=None, device="0", width=1280, height=720,
              fps=30, color=(255, 255, 255), settle=0.0, repeats=1,
              min_score=18.0, out_dir=CAL_DIR, fresh=None):
    os.makedirs(out_dir, exist_ok=True)
    w = mau5wled.WLED(host)
    print(w.describe())
    n = count or w.count
    if not n:
        raise SystemExit("the controller does not report an LED count -- pass "
                         "--count with your best guess (too many is fine, the "
                         "extras simply never light)")
    w.realtime(True, brightness=255)
    pix = mau5wled.Pixels(w, n)

    with Camera(device, width, height, fps) as cam:
        print("camera up: %dx%d" % (cam.w, cam.h))
        lag = fresh or measure_latency(cam, pix)
        print("pipeline latency: %d frames" % lag)

        pix.clear()
        time.sleep(0.6)
        dark = cam.dark()

        hits = {}
        t0 = time.monotonic()
        for i in range(n):
            best = None
            for _ in range(repeats):
                pix.one(i, color, correct=False)     # raw: order not known yet
                if settle:
                    time.sleep(settle)
                f = cam.grab(fresh=lag)
                if f is None:
                    continue
                b = find_blob(f, dark, min_score=min_score)
                if b and (best is None or b[2] > best[2]):
                    best = b
            if best:
                u, v, s, rgb = best
                hits[i] = dict(u=u, v=v, score=s, rgb=rgb)
            if i % 20 == 0 or i == n - 1:
                el = time.monotonic() - t0
                rate = (i + 1) / max(el, 1e-6)
                sys.stdout.write("\r  %4d/%d seen %4d   %.1f LED/s  eta %4.0f s"
                                 % (i + 1, n, len(hits), rate, (n - i - 1) / rate))
                sys.stdout.flush()
        print()
        pix.clear()

    path = os.path.join(out_dir, "view_%s.json" % view)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(dict(view=view, width=cam.w, height=cam.h, count=n,
                       color=list(color), leds=hits), fh)
    _save_preview(dark, hits, os.path.join(out_dir, "view_%s.png" % view))
    print("saw %d of %d LEDs from this view -> %s" % (len(hits), n, path))
    if len(hits) < n:
        print("  %d not seen: either they face away, are covered, or are dead."
              % (n - len(hits)))
    return path


def scan_order(host, count=None, device="0", width=1280, height=720, fps=30,
               out_dir=CAL_DIR, group=1, min_score=18.0):
    """Light pure R, then G, then B, and see what colour each LED actually is.

    That one measurement is the whole orange-ears-go-green problem: a strip
    wired in a different order than the controller's bus setting shows the
    channels permuted, and this reads the permutation straight off the LED.
    """
    os.makedirs(out_dir, exist_ok=True)
    w = mau5wled.WLED(host)
    n = count or w.count
    w.realtime(True, brightness=255)
    pix = mau5wled.Pixels(w, n)
    seen = {}
    with Camera(device, width, height, fps) as cam:
        lag = measure_latency(cam, pix)
        pix.clear(); time.sleep(0.5)
        dark = cam.dark()
        for i in range(0, n, group):
            resp = []
            for k in range(3):
                col = [0, 0, 0]
                col[k] = 255
                pix.some(range(i, min(i + group, n)), tuple(col), correct=False)
                f = cam.grab(fresh=lag)
                b = find_blob(f, dark, min_score=min_score) if f is not None else None
                resp.append(None if b is None else b[3])
            if any(r is None for r in resp):
                continue
            # sent slot k lit up camera channel argmax(resp[k])
            perm = tuple(int(np.argmax(r)) for r in resp)
            if sorted(perm) != [0, 1, 2]:
                continue                       # ambiguous, skip rather than guess
            seen[i] = perm
            if i % 20 == 0:
                sys.stdout.write("\r  %d/%d" % (i, n)); sys.stdout.flush()
        print()
        pix.clear()
    path = os.path.join(out_dir, "order.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump({str(k): list(v) for k, v in seen.items()}, fh)
    runs = _runs([(i, mau5wled.ORDER_NAME.get(p, "?")) for i, p in sorted(seen.items())])
    print("colour order by LED range:")
    for a, b, name in runs:
        print("  %5d..%-5d  %s%s" % (a, b, name,
                                     "" if name == "RGB" else "   <- needs correcting"))
    print("wrote %s" % path)
    return runs


def _runs(pairs):
    out = []
    for i, name in pairs:
        if out and out[-1][2] == name and i <= out[-1][1] + 8:
            out[-1][1] = i
        else:
            out.append([i, i, name])
    return [tuple(r) for r in out]


def _save_preview(dark, hits, path):
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        return
    im = Image.fromarray(dark).convert("RGB")
    d = ImageDraw.Draw(im)
    pts = sorted(hits.items())
    for k, (i, h) in enumerate(pts):
        u, v = h["u"], h["v"]
        c = (int(255 * k / max(len(pts) - 1, 1)), 80,
             255 - int(255 * k / max(len(pts) - 1, 1)))
        d.ellipse([u - 4, v - 4, u + 4, v + 4], outline=c, width=2)
    for (i0, h0), (i1, h1) in zip(pts, pts[1:]):
        if i1 == i0 + 1:
            d.line([h0["u"], h0["v"], h1["u"], h1["v"]], fill=(0, 190, 90), width=1)
    im.save(path)
    print("preview with the chain path drawn on it -> %s" % path)


# --------------------------------------------------------------------------
# solving
# --------------------------------------------------------------------------
def _load_views(cal_dir):
    out = {}
    if not os.path.isdir(cal_dir):
        return out
    for f in sorted(os.listdir(cal_dir)):
        if f.startswith("view_") and f.endswith(".json"):
            with open(os.path.join(cal_dir, f), encoding="utf-8") as fh:
                v = json.load(fh)
            v["leds"] = {int(k): val for k, val in v["leds"].items()}
            out[v["view"]] = v
    return out


def _normalise(view):
    """Pixel coords -> u,v in roughly -1..1, y up, centred on what was seen."""
    leds = view["leds"]
    if not leds:
        return {}
    us = np.array([h["u"] for h in leds.values()])
    vs = np.array([h["v"] for h in leds.values()])
    cu, cv = (us.min() + us.max()) / 2.0, (vs.min() + vs.max()) / 2.0
    half = max(us.max() - us.min(), vs.max() - vs.min()) / 2.0 or 1.0
    return {i: ((h["u"] - cu) / half, -(h["v"] - cv) / half)
            for i, h in leds.items()}


def _fill_gaps(coords, count, max_span=6):
    """An unseen LED between two seen ones is physically between them.

    Only bridges short gaps: a long unseen run means that stretch of strip is
    hidden or facing away, and inventing a straight line through it would be
    worse than leaving it out.
    """
    out = dict(coords)
    seen = sorted(coords)
    filled = 0
    for a, b in zip(seen, seen[1:]):
        span = b - a
        if 1 < span <= max_span + 1:
            ua, va = coords[a]
            ub, vb = coords[b]
            for k in range(1, span):
                f = k / float(span)
                out[a + k] = (ua + (ub - ua) * f, va + (vb - va) * f)
                filled += 1
    return out, filled


def _sections(coords, jump=0.14, order=None):
    """Split the chain where it stops being one continuous strip.

    Two independent signals, because neither catches everything:

      * a spatial jump -- a continuous strip puts index n and n+1 a few
        millimetres apart, so a leap means the data line ran off somewhere;
      * a change of colour order -- a different strip type is a different
        strip, full stop.  This one matters because two parts that are
        physically adjacent (an ear's rim and the tubes inside it) have no
        spatial gap between them at all, and would otherwise read as one.
    """
    idx = sorted(coords)
    if not idx:
        return []
    runs = [[idx[0], idx[0]]]
    for a, b in zip(idx, idx[1:]):
        ua, va = coords[a]
        ub, vb = coords[b]
        far = math.hypot(ub - ua, vb - va) > jump
        swapped = (order is not None and a in order and b in order
                   and order[a] != order[b])
        if b != a + 1 or far or swapped:
            runs.append([b, b])
        else:
            runs[-1][1] = b
    return [tuple(r) for r in runs]


def _group_runs(runs, coords, jump, link_scale=0.8):
    """Join runs that occupy the same patch of space.

    A strip snaking back and forth over the shell reads as many runs, but it
    is one part.  Two runs belong together when some point of one is within
    about one LED spacing of some point of the other -- which keeps an ear rim
    separate from the ear's inside ring, because those never touch.
    """
    pts = [np.array([coords[i] for i in range(a, b + 1) if i in coords])
           for a, b in runs]
    link = jump * link_scale
    parent = list(range(len(runs)))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    for i in range(len(runs)):
        for j in range(i + 1, len(runs)):
            if not len(pts[i]) or not len(pts[j]):
                continue
            d = np.hypot(pts[i][:, None, 0] - pts[j][None, :, 0],
                         pts[i][:, None, 1] - pts[j][None, :, 1]).min()
            if d <= link:
                parent[find(i)] = find(j)
    groups = {}
    for i, r in enumerate(runs):
        groups.setdefault(find(i), []).append(r)
    return [sorted(g) for _k, g in sorted(groups.items(),
                                          key=lambda kv: min(r[0] for r in kv[1]))]


def _write_draft(parts, coords, order_path, path, named=None):
    """A helmet.toml fragment naming what was found, ready to edit."""
    order = {}
    if os.path.exists(order_path):
        with open(order_path, encoding="utf-8") as fh:
            order = {int(k): tuple(v) for k, v in json.load(fh).items()}
    lines = ["# Drafted by `mau5cal.py solve` from the camera scan.",
             "# Rename the parts to whatever they actually are, then paste into",
             "# helmet.toml.  Ranges are LED indices along the one chain.", ""]
    route_name = {}
    for sec, (a, b) in (named or []):
        route_name[(a, b)] = sec.get("name", "")
    for n, g in enumerate(parts):
        idx = [i for a, b in g for i in range(a, b + 1) if i in coords]
        pts = np.array([coords[i] for i in idx]) if idx else np.zeros((1, 2))
        wide = np.ptp(pts[:, 0]) > 0.5
        guess = route_name.get(tuple(g[0])) or (
            "shell" if wide and len(idx) > 80 else
            "ear_rim" if len(idx) > 30 else "ear_inside")
        lines += ["[[part]]",
                  'name = "%s"      # %s' % (guess, "from chain_route.toml"
                                             if tuple(g[0]) in route_name
                                             else "guessed from shape"),
                  "leds = [%s]" % ", ".join("[%d, %d]" % r for r in g),
                  "count = %d" % len(idx), ""]
        names = {mau5wled.ORDER_NAME.get(order[i], "?") for i in idx if i in order}
        if names and names != {"RGB"}:
            lines += ["# measured colour order here: %s" % ", ".join(sorted(names)), ""]
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))
    print("\ndraft section list -> %s" % path)


def load_route(path=None):
    """The hand-written description of how the chain actually runs.

    Knowing the route turns the scan from "work out what this is" into "check
    this is what I was told", which is a much easier problem and gives real
    section names instead of part_0, part_1.
    """
    path = path or os.path.join(HERE, "chain_route.toml")
    if not os.path.exists(path):
        return None
    sys.path.insert(0, HERE)
    import mau5cfg
    cfg = mau5cfg.read_toml(path)
    ch = cfg.get("chain", {})
    return dict(described_from=ch.get("described_from", "viewer"),
                starts=ch.get("starts", ""),
                sections=ch.get("section", []))


def match_route(runs, coords, route):
    """Line the detected runs up with the expected sections, in order.

    A jumper carries no LEDs, so the indices stay consecutive while the
    position leaps -- which is the same signal that separates one section from
    the next.  Sections that expect a jumper before them should therefore land
    on a run boundary, and that is what gets checked here.
    """
    secs = route["sections"]
    n_expect = len(secs)
    out, notes = [], []
    if len(runs) == n_expect:
        out = list(zip(secs, runs))
        notes.append("the %d runs line up one-to-one with the %d sections in "
                     "chain_route.toml" % (len(runs), n_expect))
    elif len(runs) < n_expect:
        # Do NOT reshuffle -- names assigned to the wrong LEDs are worse than
        # no names. Align from the start and say where it ran out.
        out = list(zip(secs, runs))
        notes.append("found %d runs but the route describes %d sections, so "
                     "%d boundary/boundaries were not detected." %
                     (len(runs), n_expect, n_expect - len(runs)))
        notes.append("names are assigned in chain order up to the point they "
                     "run out; everything from %r onwards is UNNAMED rather "
                     "than guessed. Two parts that touch (an ear rim and the "
                     "tubes inside it) have no spatial gap -- lower --jump, or "
                     "run `order` first so the colour-order change splits them."
                     % secs[len(runs)].get("name", "?"))
    else:
        out = list(zip(secs, runs))
        notes.append("found %d runs but the route describes only %d sections. "
                     "A snaking section reads as several runs when the turns "
                     "are tight -- raise --jump to merge them. Naming the "
                     "first %d in chain order." % (len(runs), n_expect, n_expect))
    return out, notes


def check_handedness(route, coords, named):
    """Did LED 0 land where the description says it should?

    The route was dictated from inside the helmet, so wearer-right is
    camera-left.  Rather than assume the flip, look at where index 0 actually
    lit up and say plainly whether it agrees.
    """
    if not named:
        return []
    first = min(coords) if coords else None
    if first is None or first not in coords:
        return []
    u, v = coords[first]
    side = "camera-left" if u < 0 else "camera-right"
    wearer = "wearer-right" if u < 0 else "wearer-left"
    expect = "wearer-right" if "right" in route.get("starts", "").lower() else "wearer-left"
    msg = ["LED %d (the first one lit) landed on the %s of the frame, which is "
           "the %s side of the helmet." % (first, side, wearer)]
    if route.get("described_from") == "wearer":
        msg.append("  The route says the chain starts on the %s. %s"
                   % (expect,
                      "That agrees." if wearer == expect else
                      "That DISAGREES -- either the camera was behind the "
                      "helmet, or the chain starts at the other end. Check "
                      "before trusting the section names."))
    return msg


def solve(cal_dir=CAL_DIR, out_csv=None, jump=0.14, max_span=6, min_run=4,
          link_scale=0.8, route_path=None):
    views = _load_views(cal_dir)
    if not views:
        raise SystemExit("no scans in %s -- run `mau5cal.py scan --view front` "
                         "first" % cal_dir)
    main = "front" if "front" in views else max(views, key=lambda k: len(views[k]["leds"]))
    print("views: %s   (using %r for the main map)"
          % (", ".join("%s=%d" % (k, len(v["leds"])) for k, v in views.items()), main))
    count = max(v["count"] for v in views.values())

    coords = _normalise(views[main])
    coords, filled = _fill_gaps(coords, count, max_span)
    print("placed %d of %d LEDs (%d of them interpolated across short gaps)"
          % (len(coords), count, filled))

    # depth from a second view, read orthographically: the side view's
    # horizontal axis is depth. Good enough for show geometry and it needs no
    # camera calibration.
    depth = {}
    other = [k for k in views if k != main]
    if other:
        side = _normalise(views[other[0]])
        for i, (u, _v) in side.items():
            depth[i] = u
        print("depth from view %r for %d LEDs" % (other[0], len(depth)))

    order = {}
    opath = os.path.join(cal_dir, "order.json")
    if os.path.exists(opath):
        with open(opath, encoding="utf-8") as fh:
            order = {int(k): tuple(v) for k, v in json.load(fh).items()}
    runs = [r for r in _sections(coords, jump, order) if r[1] - r[0] + 1 >= min_run]
    print("\n%d run%s of continuous strip (a run ends where the data line jumps):"
          % (len(runs), "" if len(runs) == 1 else "s"))
    for a, b in runs[:24]:
        pts = np.array([coords[i] for i in range(a, b + 1) if i in coords])
        print("  %5d..%-5d  %4d LEDs   centre u%+.2f v%+.2f   extent %.2f x %.2f"
              % (a, b, b - a + 1, pts[:, 0].mean(), pts[:, 1].mean(),
                 np.ptp(pts[:, 0]), np.ptp(pts[:, 1])))
    if len(runs) > 24:
        print("  ... and %d more" % (len(runs) - 24))

    parts = _group_runs(runs, coords, jump, link_scale)
    print("\n%d physical part%s (runs that sit on top of each other in space):"
          % (len(parts), "" if len(parts) == 1 else "s"))
    for n, g in enumerate(parts):
        idx = [i for a, b in g for i in range(a, b + 1) if i in coords]
        pts = np.array([coords[i] for i in idx])
        print("  part %d  %4d LEDs over %d run(s)  centre u%+.2f v%+.2f  "
              "extent %.2f x %.2f"
              % (n, len(idx), len(g), pts[:, 0].mean(), pts[:, 1].mean(),
                 np.ptp(pts[:, 0]), np.ptp(pts[:, 1])))
    print("  grouping is a guess -- check it against data/cal/view_%s.png, which\n"
          "  has the chain drawn in order over the scene. --link tightens or\n"
          "  loosens how readily two runs are called the same part." % main)
    route = load_route(route_path)
    named = []
    if route:
        named, notes = match_route(runs, coords, route)
        print("\nagainst chain_route.toml:")
        for n in notes:
            print("  %s" % n)
        for sec, (a, b) in named:
            print("  %5d..%-5d  %-14s %s" % (a, b, sec.get("name", "?"),
                                             sec.get("where", "")))
        for line in check_handedness(route, coords, named):
            print("  %s" % line)
        suspect = [s2.get("name") for s2, _r in named
                   if s2.get("color_order_suspect")]
        if suspect:
            print("  sections the route flags as the odd strip: %s"
                  % ", ".join(suspect))
    _write_draft(parts, coords, order_path=os.path.join(cal_dir, "order.json"),
                 path=os.path.join(cal_dir, "sections.toml"), named=named)

    out_csv = out_csv or os.path.join(HERE, "data", "pixel_map.csv")
    os.makedirs(os.path.dirname(out_csv), exist_ok=True)
    import csv
    fields = ["index", "u", "v", "x", "y", "z", "section", "seen", "order"]
    with open(out_csv, "w", newline="", encoding="utf-8") as fh:
        wr = csv.DictWriter(fh, fieldnames=fields)
        wr.writeheader()
        sec_of = {}
        for n, (a, b) in enumerate(runs):
            for i in range(a, b + 1):
                sec_of[i] = n
        for i in range(count):
            uv = coords.get(i)
            o = order.get(i)
            wr.writerow(dict(
                index=i,
                u="" if uv is None else round(uv[0], 5),
                v="" if uv is None else round(uv[1], 5),
                x="" if uv is None else round(uv[0], 5),
                y="" if i not in depth else round(depth[i], 5),
                z="" if uv is None else round(uv[1], 5),
                section=sec_of.get(i, ""),
                seen=int(i in views[main]["leds"]),
                order="" if o is None else mau5wled.ORDER_NAME.get(o, ""),
            ))
    print("\nwrote %s" % out_csv)

    if order:
        print("\nhelmet.toml colour-order blocks (paste these in):")
        for a, b, name in _runs([(i, mau5wled.ORDER_NAME.get(p, "?"))
                                 for i, p in sorted(order.items())]):
            if name == "RGB":
                continue
            print("[[strip]]\nstart = %d\ncount = %d\norder = \"%s\"\n"
                  % (a, b - a + 1, name))
    return out_csv


# --------------------------------------------------------------------------
# live poking
# --------------------------------------------------------------------------
LIVE_HELP = """\
  <n>            light LED n only            37
  <a>-<b>        light a range               10-40
  all            light everything            off / clear
  c <r,g,b>      set the colour              c 255,0,0   c orange
  + / -          step to the next/previous LED, or press enter to step
  w <n>          walk from n upwards, pausing for enter at each one
  b <0-255>      controller brightness
  snap [name]    save a camera frame to data/cal/
  q              quit (and blank the helmet)"""

NAMED = {"red": (255, 0, 0), "green": (0, 255, 0), "blue": (0, 0, 255),
         "white": (255, 255, 255), "orange": (255, 110, 0),
         "cyan": (0, 255, 255), "magenta": (255, 0, 255),
         "yellow": (255, 200, 0), "off": (0, 0, 0)}


def live(host, count=None, device=None, width=1280, height=720, fps=30):
    """Hand control, for identifying things by eye."""
    w = mau5wled.WLED(host)
    print(w.describe())
    n = count or w.count
    w.realtime(True, brightness=255)
    pix = mau5wled.Pixels(w, n)
    cam = None
    if device is not None:
        cam = Camera(device, width, height, fps).start()

    cur, col = 0, (255, 255, 255)
    held = pix.blank()
    stop = threading.Event()

    def keepalive():
        # WLED falls back to its own effect after ~2.5 s without a packet
        while not stop.is_set():
            pix.send(held)
            time.sleep(0.25)
    threading.Thread(target=keepalive, daemon=True).start()

    def show(buf, what):
        held[:] = buf
        print("  %s   colour %s" % (what, col))

    print(LIVE_HELP)
    try:
        while True:
            try:
                line = input("led[%d]> " % cur).strip()
            except EOFError:
                break
            if line in ("q", "quit", "exit"):
                break
            if line == "":
                line = "+"
            buf = pix.blank()
            if line in ("+", "-"):
                cur = max(0, min(n - 1, cur + (1 if line == "+" else -1)))
                buf[cur] = col
                show(buf, "LED %d" % cur)
            elif line == "all":
                buf[:] = col
                show(buf, "all %d LEDs" % n)
            elif line in ("off", "clear"):
                show(buf, "blank")
            elif line.startswith("c "):
                v = line[2:].strip()
                col = NAMED.get(v) or tuple(int(x) for x in v.split(","))
                buf[cur] = col
                show(buf, "LED %d" % cur)
            elif line.startswith("b "):
                w.set_brightness(int(line[2:]))
                print("  brightness %s" % line[2:])
                continue
            elif line.startswith("snap"):
                if cam is None:
                    print("  no camera attached -- start with --device")
                    continue
                name = (line.split(None, 1) + ["snap"])[1]
                f = cam.grab(fresh=3)
                if f is None:
                    print("  no new frame from the camera -- not saving an old one")
                    continue
                os.makedirs(CAL_DIR, exist_ok=True)
                p = os.path.join(CAL_DIR, "%s.png" % name.replace(" ", "_"))
                try:
                    from PIL import Image
                    Image.fromarray(f).save(p)
                    print("  saved %s" % p)
                except ImportError:
                    print("  need Pillow to save images")
                continue
            elif line.startswith("w "):
                start = int(line[2:])
                for i in range(start, n):
                    b2 = pix.blank(); b2[i] = col
                    held[:] = b2
                    try:
                        if input("  LED %d  (enter = next, q = stop) " % i).strip() == "q":
                            break
                    except EOFError:
                        break
                    cur = i
                continue
            elif "-" in line:
                a, b = line.split("-", 1)
                a, b = int(a), int(b)
                buf[a:b + 1] = col
                cur = a
                show(buf, "LEDs %d..%d" % (a, b))
            elif line.lstrip("-").isdigit():
                cur = max(0, min(n - 1, int(line)))
                buf[cur] = col
                show(buf, "LED %d" % cur)
            else:
                print(LIVE_HELP)
                continue
    finally:
        stop.set()
        time.sleep(0.3)
        pix.clear()
        if cam:
            cam.stop()
        print("blanked.")


# --------------------------------------------------------------------------
def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter,
                                 epilog=__doc__)
    ap.add_argument("--host", default=None, help="controller ip or hostname")
    ap.add_argument("--count", type=int, help="override the LED count")
    ap.add_argument("--device", default="0", help="camera index (see `cameras`)")
    ap.add_argument("--width", type=int, default=1280)
    ap.add_argument("--height", type=int, default=720)
    ap.add_argument("--fps", type=int, default=30)
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("cameras", help="list what ffmpeg can capture from")
    sub.add_parser("probe", help="ask the controller what it has")
    sub.add_parser("live", help="poke pixels by hand")
    p = sub.add_parser("order", help="measure each LED's colour order")
    p.add_argument("--group", type=int, default=1,
                   help="test this many LEDs at once (faster, needs them spread out)")
    p = sub.add_parser("scan", help="sweep the chain and record where each LED is")
    p.add_argument("--view", required=True, help="front | side | whatever you call it")
    p.add_argument("--color", default="255,255,255")
    p.add_argument("--repeats", type=int, default=1)
    p.add_argument("--settle", type=float, default=0.0)
    p.add_argument("--min-score", type=float, default=18.0)
    p.add_argument("--fresh", type=int, help="override the measured camera latency")
    p = sub.add_parser("solve", help="turn the scans into data/pixel_map.csv")
    p.add_argument("--jump", type=float, default=0.14,
                   help="spatial gap between consecutive LEDs that starts a new section")
    p.add_argument("--max-span", type=int, default=6)
    p.add_argument("--link", type=float, default=0.8,
                   help="how close two runs must be to count as one part")
    p.add_argument("--route", help="chain description (default chain_route.toml)")
    a = ap.parse_args(argv)

    if a.cmd == "cameras":
        print(list_cameras())
        return
    if a.cmd == "solve":
        solve(jump=a.jump, max_span=a.max_span, link_scale=a.link,
              route_path=a.route)
        return

    host = a.host
    if host is None:
        found = mau5wled.discover()
        if not found:
            raise SystemExit("no controller found by name -- pass --host <ip>")
        host = found[0].base.split("//")[-1]
        print("found %s" % host)

    if a.cmd == "probe":
        w = mau5wled.WLED(host)
        print(w.describe())
        print()
        print("if the LED count above is wrong, fix it in the WLED UI first --")
        print("everything downstream trusts it.")
    elif a.cmd == "live":
        live(host, a.count, a.device, a.width, a.height, a.fps)
    elif a.cmd == "order":
        scan_order(host, a.count, a.device, a.width, a.height, a.fps,
                   group=a.group)
    elif a.cmd == "scan":
        scan_view(host, a.view, a.count, a.device, a.width, a.height, a.fps,
                  color=tuple(int(x) for x in a.color.split(",")),
                  settle=a.settle, repeats=a.repeats, min_score=a.min_score,
                  fresh=a.fresh)


if __name__ == "__main__":
    main()
