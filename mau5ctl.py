#!/usr/bin/env python3
"""mau5ctl -- the controller: presets, shows and sound, from a phone.

Why it is split the way it is.  A browser cannot send UDP, and UDP is
what WLED needs for per-pixel data, so the phone cannot drive the
helmet by itself; this process does the streaming.  But the *audio*
must come out of the phone, because that is what is paired to the
Bluetooth speaker.  So the phone owns the clock: it plays the track,
reports where it has got to a few times a second, and the light engine
here follows that rather than running a clock of its own.

That ordering matters.  If the lights kept their own time they would
drift against the speaker all night and no amount of offset would fix
it; following the audio means the worst case is lights a frame or two
behind, which nobody can see.

    python3 mau5ctl.py                 # find the helmet, serve the UI
    python3 mau5ctl.py --no-wled       # UI only, for working on it
"""

from __future__ import annotations

import argparse
import collections
import json
import base64
import socket
import mimetypes
import os
import threading
import time
import urllib.parse
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler

import numpy as np

import mau5engine as E
import mau5show
import mau5wled

HERE = os.path.dirname(os.path.abspath(__file__))
SHOWS = os.path.join(HERE, "shows")
FAVOURITES = os.path.join(HERE, "data", "cal", "favourites.json")


def _load_favourites():
    try:
        return json.load(open(FAVOURITES))
    except Exception:
        return []


def _save_favourites(favs):
    os.makedirs(os.path.dirname(FAVOURITES), exist_ok=True)
    tmp = FAVOURITES + ".tmp"
    with open(tmp, "w") as f:
        json.dump(favs, f, indent=1)
    os.replace(tmp, FAVOURITES)      # atomic: never leave a half-written list


class Controller:
    """Holds what is playing and renders it."""

    def __init__(self, pix, fps=40, wled=None):
        self.pix = pix
        self.wled = wled
        self.fps = fps
        self.h = E.Helmet()
        self.lock = threading.Lock()

        self.mode = "off"              # off | preset | show
        self.preset_name = None
        self.preset = None
        self.params = {}
        self.preset_t0 = time.monotonic()
        self.brightness = 1.0
        # Run live presets on the track's clock when one is playing, so
        # a preset chosen by hand lands with the music exactly as a
        # show cue does.  Without this the two halves of the controller
        # behave differently for no reason the user can see.
        self.sync = True
        self.pulse = 0.40
        self.gain = 1.0          # the beat, applied after the guard

        self.show = None
        self.show_name = None
        self.player = None
        self.music = None
        self._t = 0.0                  # position at _at, as we believe it
        self._at = time.monotonic()
        self._corr = 0.0               # correction being eased in (clock())
        self._sid, self._seq = None, -1
        self._lag = collections.deque(maxlen=25)
        self.playing = False

        # The guard, even with no helmet attached.  The preview is meant
        # to show what the helmet would do, and what it would do is
        # clamped: a preset that asks for 55 W and gets 18 looks very
        # different.  A preview that skipped the guard would flatter
        # every bright preset and be useless for judging one.
        self.guard = pix.guard if pix is not None else None
        if self.guard is None:
            import mau5power
            self.guard = mau5power.load(count=self.h.n)
        self.last_frame = np.zeros((self.h.n, 3), np.uint8)
        self._t0_sim = 0.0
        self._output_on = None
        # Coming out of dark, climb into the load rather than landing on
        # it.  Six hundred LEDs going from nothing to full in one frame
        # is a step the supply has to answer instantly, and it is the
        # moment this rig has always fallen over -- never while already
        # running.  Half a second is nothing to watch and a very long
        # time to a power supply.  It applies only on the way on, so a
        # strobe still strobes.
        self.soft_start = 0.5
        self._soft_t0 = 0.0

        self.favourites = _load_favourites()
        self.last_power = None
        self.error = None
        self.stop = False
        self._fps_seen = 0.0
        # No helmet because none was asked for is a different thing from
        # a helmet that stopped answering, and the UI should not cry
        # wolf about the first.
        self.simulated = wled is None
        self.helmet_ok = wled is not None
        self.helmet_note = None
        threading.Thread(target=self._run, daemon=True).start()
        if wled is not None:
            threading.Thread(target=self._watchdog, daemon=True).start()

    # -- clock ---------------------------------------------------------
    # A report further out than this is a seek, a stall or a new track,
    # and is jumped to.  Anything nearer is eased in over EASE_S, at no
    # more than MAX_CORR_S per report -- a tenth faster or slower for
    # half a second, which nobody can see, where a step is a hitch.
    SNAP_S = 0.5
    EASE_S = 0.5
    GAIN = 0.5
    MAX_CORR_S = 0.05

    def clock(self, t=None, playing=None, seq=None, sid=None, pt=None):
        """The phone tells us where the audio is; we follow it smoothly.

        This used to set the clock to each report as it arrived.  Every
        report is late by its own trip across the network, and on phone
        Wi-Fi, a hotspot or the tunnel those trips differ by tens to
        hundreds of milliseconds, so the show clock stepped forward and
        back by the difference every 400 ms -- and two POSTs handled out
        of order set it back a whole report.  Fast chases and beat
        flashes hitched two or three times a second at a steady 40 fps.

        Three things now, each optional so an older page still works:
        `seq` with `sid` (one per page load) drops a report overtaken by
        a later one; `pt`, the phone's performance.now() when it read
        the position, measures how much later than the quickest recent
        report this one arrived, and adds that back; and the remaining
        error is eased in rather than assigned.
        """
        mono = time.monotonic()
        with self.lock:
            if seq is not None and sid is not None:
                if sid == self._sid and seq <= self._seq:
                    return                         # stale: a later one landed
                if sid != self._sid:
                    self._sid = sid
                    self._lag.clear()
                self._seq = seq
            was = self.playing
            go = was if playing is None else bool(playing)
            cur = self._now_locked(mono)
            if t is None:
                # Only the state changed: hold the position we have.
                self._t, self._at, self._corr = cur, mono, 0.0
                self.playing = go
                return
            t = float(t)
            if pt is not None and go:
                # Arrival minus the phone's own clock is a fixed offset
                # plus this report's delay; against the smallest of the
                # last ten seconds it is just the extra delay.
                self._lag.append(mono - float(pt) / 1000.0)
                t += min(mono - float(pt) / 1000.0 - min(self._lag), 1.0)
            err = t - cur
            if not (go and was) or abs(err) > self.SNAP_S:
                self._t, self._at, self._corr = t, mono, 0.0
            else:
                c = self.GAIN * err
                self._t, self._at = cur, mono
                self._corr = max(-self.MAX_CORR_S, min(self.MAX_CORR_S, c))
            self.playing = go

    def _now_locked(self, mono):
        if not self.playing:
            return self._t
        dt = mono - self._at
        return self._t + dt + self._corr * min(dt / self.EASE_S, 1.0)

    def now(self):
        # Under the lock, or a frame can pair a new position with the
        # old time it was taken at and jump for one frame.
        with self.lock:
            return self._now_locked(time.monotonic())

    # -- what to show --------------------------------------------------
    def set_preset(self, name, **params):
        # Render one frame on a throwaway copy before it replaces what
        # is playing.  The sliders run from the spec's minimum, which is
        # 0 for every positive number, and at 0 twenty-odd presets
        # divide by it -- period, fade, every, step, bands -- and raise
        # on every frame.  Refused here, the old preset carries on and
        # the phone is told why; accepted, the helmet would go dark.
        probe = E.make(name, **params)
        try:
            for m in ((None, self.music) if self.music is not None else (None,)):
                probe.render(self.h, 1.7, m)
        except (Exception, SystemExit) as e:
            raise ValueError("%s will not render with those settings (%s: %s) "
                             "-- kept what was playing"
                             % (name, type(e).__name__, e)) from e
        with self.lock:
            self.preset = E.make(name, **params)
            self.preset_name = name
            self.params = dict(self.preset.p)
            self.mode = "preset"
            # Restart the clock.  Presets that tell a story from t=0 --
            # countdown most obviously -- are permanently finished if
            # handed the wall clock, and periodic ones look better
            # starting at phase zero than wherever the day happens to be.
            self.preset_t0 = time.monotonic()

    def set_show(self, name):
        # A show is a file in shows/ by its bare name, never a path: the
        # name comes from the network, and joined as given it loaded any
        # JSON on the disk ("../../somewhere.json").
        name = str(name)
        if os.path.basename(name) != name or not name.endswith(".json"):
            raise ValueError("no show %r" % name)
        path = os.path.join(SHOWS, name)
        if not os.path.isfile(path):
            raise ValueError("no show %r" % name)
        show = json.load(open(path))
        track = os.path.join(HERE, show["track"])
        music = mau5show._music_for(show, track)
        with self.lock:
            self.show, self.show_name = show, name
            self.music = music
            self.player = mau5show.Player(show, helmet=self.h, music=music)
            self.mode = "show"
            self._t, self._at, self.playing = 0.0, time.monotonic(), False
            self._corr = 0.0

    # -- favourites ----------------------------------------------------
    def save_favourite(self, label):
        """Keep the preset and its current settings under a name."""
        if self.mode != "preset" or not self.preset_name:
            raise ValueError("nothing to save -- pick a preset first")
        label = str(label).strip()[:40]
        if not label:
            raise ValueError("give it a name")
        entry = {"label": label, "preset": self.preset_name,
                 "params": _jsonable(self.params)}
        with self.lock:
            self.favourites = [f for f in self.favourites if f["label"] != label]
            self.favourites.append(entry)
            _save_favourites(self.favourites)
        return entry

    def recall_favourite(self, label):
        for f in self.favourites:
            if f["label"] == label:
                cls = E.REGISTRY.get(f["preset"])
                if cls is None:
                    raise ValueError("%r uses preset %r, which no longer exists"
                                     % (label, f["preset"]))
                self.set_preset(f["preset"], **cls.accepts(f["params"]))
                return f
        raise ValueError("no favourite called %r" % label)

    def forget_favourite(self, label):
        with self.lock:
            before = len(self.favourites)
            self.favourites = [f for f in self.favourites if f["label"] != label]
            if len(self.favourites) == before:
                raise ValueError("no favourite called %r" % label)
            _save_favourites(self.favourites)

    def off(self):
        with self.lock:
            self.mode = "off"
            self.playing = False

    # -- the frame loop -------------------------------------------------
    def _frame(self):
        self.gain = 1.0
        if self.mode == "preset" and self.preset is not None:
            free = time.monotonic() - self.preset_t0
            m = self.music if (self.sync and self.playing) else None
            if m is None:
                return self.preset.render(self.h, free, self.music)
            t = self.now()
            te, _ = E.lock_time(m, self.preset_name, self.params, t)
            out = self.preset.render(self.h, te, m)
            # The beat as a gain applied after the guard, not a lift
            # multiplied in here: the guard flattens any lift on loud
            # material, which is when a pulse matters (mau5show.Player).
            if self.pulse > 0:
                k = max(0.0, 1.0 - m.beat_phase(t) * 3.0) ** 2
                self.gain = (1.0 + self.pulse * k) / (1.0 + self.pulse)
            return out
        if self.mode == "show" and self.player is not None:
            out = self.player.frame(self.now())
            self.gain = self.player.gain
            return out
        return np.zeros((self.h.n, 3))

    def _set_output(self, want):
        """Hand the helmet back when we have nothing to show.

        Streaming black is not the same as being off, and the
        difference matters more than it sounds.  A helmet being sent
        622 black pixels forty times a second is indistinguishable,
        from the outside, from a helmet with a broken data line or a
        dead supply -- and it overrides whatever WLED would otherwise
        be doing, so it stays dark through reboots and power cycles
        too.  An evening was spent pulling apart wiring that was fine
        because of exactly this.  So "off" stops the stream and tells
        the controller to switch off, and selecting anything turns it
        back on.
        """
        if self.wled is None or want == self._output_on:
            self._output_on = want
            return
        try:
            if want:
                self.wled.realtime(True, brightness=255)
                self._soft_t0 = time.monotonic()
            else:
                self.wled.off()
            self._output_on = want
        except Exception as e:
            self.helmet_note = "could not switch output: %s" % type(e).__name__

    def _run(self):
        period = 1.0 / self.fps
        nxt = time.monotonic()
        while not self.stop:
            try:
                live = self.mode != "off"
                self._set_output(live)
                if not live:
                    self.last_frame = np.zeros((self.h.n, 3), np.uint8)
                    # ...and say so.  Leaving the last frame's figure on
                    # screen reads as the helmet still pulling 19 W while
                    # switched off, which is alarming and wrong.
                    if self.guard is not None:
                        sb = self.guard.standby_ma()
                        self.last_power = {"sent_ma": 0.0, "standby_ma": sb,
                                           "total_ma": sb, "amps": round(sb/1000.0, 2),
                                           "watts": round(sb*12/1000.0, 1),
                                           "thermal": (self.guard.thermal.state()
                                                       if self.guard.thermal else None)}
                    time.sleep(period)
                    continue
                buf = self._frame() * self.brightness
                if self.error is not None:
                    # Coming back from black after a render error is
                    # coming out of dark, and gets the same climb.
                    self._soft_t0 = time.monotonic()
                if self.soft_start > 0:
                    k = (time.monotonic() - self._soft_t0) / self.soft_start
                    if k < 1.0:
                        buf = buf * max(0.0, k)
                if self.pix is not None:
                    self.pix.send(buf, gain=self.gain)
                    self.last_power = self.pix.last_power
                    self.last_frame = self.pix.last_sent
                elif self.guard is not None:
                    # Ceilings and region budgets still apply -- those
                    # are properties of the wiring and hold whatever
                    # the helmet is doing.  The thermal bucket does
                    # not: it models heat in an object that is not
                    # here, and letting it drain means a preview left
                    # open for two minutes fades to almost nothing and
                    # looks like a bug.  Hold it full and report what
                    # the real helmet would settle to instead.
                    shown, rep = self.guard.apply(np.clip(buf, 0, 255),
                                                  now=self._t0_sim, gain=self.gain)
                    self.last_power = rep
                    self.last_frame = shown
                else:
                    self.last_frame = np.clip(buf, 0, 255).astype(np.uint8)
                self.error = None
            except (Exception, SystemExit) as e:
                # Report it once rather than looping silently.  SystemExit
                # too: mau5engine.make() raises it for an unknown preset,
                # a show builds its presets lazily, and an uncaught one
                # ended this thread without a word -- no more frames, the
                # same hand-off to WLED, and nothing short of a restart.
                msg = "%s: %s" % (type(e).__name__, e)
                if msg != getattr(self, "error", None):
                    self.error = msg
                    print("  render error: %s" % msg)
                # And keep the stream alive, with black.  Sending nothing
                # did not make the helmet go dark: 2.5 s later WLED left
                # realtime and ran its own effect at the brightness 255
                # _set_output asked for, with no guard and no bucket,
                # while this still said "preset".  Black through the
                # guard holds the helmet here, and dark, until a frame
                # renders again.
                if self.mode != "off":
                    self._blank()
            nxt += period
            slack = nxt - time.monotonic()
            if slack > 0:
                time.sleep(slack)
            else:
                nxt = time.monotonic()

    def _blank(self):
        black = np.zeros((self.h.n, 3), np.uint8)
        try:
            if self.pix is not None:
                self.pix.send(black)
                self.last_power = self.pix.last_power
        except Exception:
            pass                     # unreachable; the watchdog says so
        self.last_frame = black

    def _watchdog(self):
        """Notice if the helmet goes away, and re-arm it when it returns.

        DDP is UDP, so sending into the void raises nothing -- without a
        check, a controller whose helmet rebooted looks perfectly healthy
        and simply does not light anything.  And a reboot clears realtime
        mode, so coming back needs more than the packets resuming.
        """
        while not self.stop:
            time.sleep(6.0)
            try:
                self.wled.info(refresh=True)
                if not self.helmet_ok:
                    self._output_on = None       # a reboot forgets everything
                    self.wled.realtime(True, brightness=255)
                    self.helmet_note = "reconnected at %s" % time.strftime("%H:%M:%S")
                    print("  helmet back: re-armed realtime mode")
                self.helmet_ok = True
            except Exception as e:
                if self.helmet_ok:
                    self.helmet_note = "lost at %s (%s)" % (
                        time.strftime("%H:%M:%S"), type(e).__name__)
                    print("  helmet unreachable: %s" % type(e).__name__)
                self.helmet_ok = False

    def state(self):
        p = self.last_power or {}
        cue = None
        if self.mode == "show" and self.show:
            t = self.now()
            for c in self.show["cues"]:
                if c["start"] <= t < c["end"]:
                    cue = c["preset"]; break
        return {
            "mode": self.mode, "preset": self.preset_name, "params": _jsonable(self.params),
            "preset_t": (round(time.monotonic() - self.preset_t0, 2)
                         if self.mode == "preset" else None),
            "brightness": round(self.brightness, 3),
            "show": self.show_name, "playing": self.playing,
            "track": self.show["track"] if self.show else None,
            "t": round(self.now(), 2),
            "duration": self.show["duration"] if self.show else 0,
            "cue": cue,
            "amps": p.get("amps"), "watts": p.get("watts"),
            "error": self.error,
            "thermal": p.get("thermal"),
            "helmet_ok": self.helmet_ok, "helmet_note": self.helmet_note,
            "simulated": self.simulated,
            "sync": self.sync, "pulse": round(self.pulse, 3),
            "lockable": self.preset_name in E.LOCKABLE,
            "lock_beats": (E.lock_time(self.music, self.preset_name,
                                       self.params, self.now())[1]
                           if (self.music is not None and self.mode == "preset"
                               and self.preset_name in E.LOCKABLE) else None),
            "cycle_s": (round(E.cycle_seconds(self.preset_name, self.params) or 0, 3)
                        if self.mode == "preset" else None),
            "lock_conf": (round(self.music.lock_conf, 3)
                          if self.music is not None
                          and self.music.lock_conf == self.music.lock_conf else None),
            "bpm": round(self.music.bpm, 1) if self.music is not None else None,
            "governor": p.get("governor_hit"), "ceiling": p.get("ceiling_hit"),
            "presets": sorted(E.REGISTRY),
            "favourites": list(self.favourites),
            "spec": (E.REGISTRY[self.preset_name].spec()
                     if self.preset_name in E.REGISTRY else []),
            "shows": sorted(f for f in os.listdir(SHOWS) if f.endswith(".json"))
                     if os.path.isdir(SHOWS) else [],
        }


def layout(h):
    """Where to draw each LED, as the camera in front of the helmet sees it.

    Orthographic x across and z up, the same screen frame the glyph
    presets lay out against, normalised into a 0..1 box with y already
    flipped for a canvas.  Sent once; the frames that follow are just
    colours in this order.
    """
    x, y = h.px.astype(float), h.py.astype(float)
    x0, x1 = float(x.min()), float(x.max())
    y0, y1 = float(y.min()), float(y.max())
    sx, sy = (x1 - x0) or 1.0, (y1 - y0) or 1.0
    k = max(sx, sy)
    return {
        "n": int(h.n),
        "x": [round((v - x0) / k + (1 - sx / k) / 2, 4) for v in x],
        "y": [round(1.0 - ((v - y0) / k + (1 - sy / k) / 2), 4) for v in y],
        "aspect": round(sx / sy, 4),
        "region": [str(r) for r in h.region],
        # the tubes are physically four times brighter per LED than the
        # shell, so the preview draws them bigger or it lies about the look
        "size": [2.6 if t else (1.7 if rim else 1.0)
                 for t, rim in zip(h.tubes.tolist(), h.rims.tolist())],
        # 1 facing the viewer, 0 at the silhouette.  An LED on the edge
        # of the dome is seen almost edge-on and covers a fraction of
        # the area it does head on; without this the shell renders as a
        # flat disc of evenly spaced dots and reads as a dinner plate.
        "face": _facing(h),
        # How much each LED spills into its neighbours.  Not a constant:
        # the tubes are 187 LEDs packed into six lines, and a spill that
        # suits the shell's open grid accumulates there into a solid
        # white slab.  Density has to be paid for in alpha.
        "bloom": [0.22 if t else (0.30 if rim else 0.42)
                  for t, rim in zip(h.tubes.tolist(), h.rims.tolist())],
        "parts": _outlines(h),
    }


def _facing(h):
    import numpy as _np
    d = h.depth.astype(float)
    r = _np.hypot(_np.hypot(h.px, h.py - 30.0), d)
    f = _np.clip(d / _np.maximum(r, 1e-6), 0.0, 1.0)
    f[~h.shell] = 1.0                      # the ear discs are flat and face us
    return [round(float(v), 3) for v in f]


def _outlines(h):
    """A faint circle per physical part, so the shape survives the dark.

    Taken from the LEDs themselves rather than from the CAD: the point
    is to frame what is drawn, and what is drawn is the map.
    """
    import numpy as _np
    out = []
    x, y = h.px.astype(float), h.py.astype(float)
    x0, x1 = float(x.min()), float(x.max())
    y0, y1 = float(y.min()), float(y.max())
    k = max(x1 - x0, y1 - y0) or 1.0
    for name, m in (("shell", h.shell), ("ear1", h.ear1), ("ear2", h.ear2)):
        if not m.any():
            continue
        cx, cy = float(x[m].mean()), float(y[m].mean())
        rad = float(_np.percentile(_np.hypot(x[m] - cx, y[m] - cy), 97))
        out.append({
            "name": name,
            "cx": round((cx - x0) / k + (1 - (x1 - x0) / k) / 2, 4),
            "cy": round(1.0 - ((cy - y0) / k + (1 - (y1 - y0) / k) / 2), 4),
            "r": round(rad / k, 4),
        })
    return out


def _jsonable(d):
    out = {}
    for k, v in (d or {}).items():
        out[k] = list(v) if isinstance(v, tuple) else v
    return out


def make_handler(ctl):
    class H(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"

        def log_message(self, *a):
            pass

        def handle_one_request(self):
            # A browser that seeks in an <audio> element, or closes a
            # frame stream, simply drops the connection mid-write.  That
            # is routine, but it arrives as BrokenPipeError out of
            # socketserver and takes the whole handler down with a
            # traceback -- and with keep-alive on, the next request on
            # that connection goes nowhere.  Swallow the disconnect and
            # let the thread end quietly.
            try:
                return BaseHTTPRequestHandler.handle_one_request(self)
            except (BrokenPipeError, ConnectionResetError):
                self.close_connection = True

        def do_HEAD(self):
            # Players ask before they fetch.  Answering 501 makes a
            # track look unplayable before a byte has been requested.
            self._head_only = True
            try:
                self.do_GET()
            finally:
                self._head_only = False

        _head_only = False

        def _send(self, body, ctype="application/json", code=200, extra=None):
            if not isinstance(body, bytes):
                body = json.dumps(body).encode()
            if self._head_only:
                self.send_response(code)
                self.send_header("Content-Type", ctype)
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                return
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            for k, v in (extra or {}):
                self.send_header(k, v)
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            path = urllib.parse.urlparse(self.path).path
            if path in ("/", "/index.html"):
                p = os.path.join(HERE, "remote", "control.html")
                return self._send(open(p, "rb").read(), "text/html; charset=utf-8")
            if path == "/api/state":
                return self._send(ctl.state())
            if path == "/api/layout":
                return self._send(layout(ctl.h))
            if path == "/api/stream":
                return self._stream()
            if path == "/api/frame":
                # Raw bytes, not JSON: 622 LEDs is 1866 bytes this way
                # and about 9 kB as a list of numbers, which matters on
                # a phone pulling it ten times a second.
                return self._send(ctl.last_frame.astype(np.uint8).tobytes(),
                                  "application/octet-stream")
            if path.startswith("/audio/"):
                return self._audio(urllib.parse.unquote(path[len("/audio/"):]))
            self._send({"error": "no route"}, code=404)

        def _stream(self):
            """Push frames until the client goes away.

            Polling cost a round trip per frame, which over a tunnel is
            two hundred milliseconds of nothing happening and a preview
            that runs at four frames a second however fast the renderer
            is.  One open connection and the frames arrive as they are
            made.
            """
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Accel-Buffering", "no")
            self.send_header("Connection", "keep-alive")
            self.end_headers()
            if self._head_only:
                return
            period = 1.0 / 15.0
            try:
                self.wfile.write(b"retry: 2000\n\n")
                while not ctl.stop:
                    b64 = base64.b64encode(ctl.last_frame.astype(np.uint8).tobytes())
                    self.wfile.write(b"data: " + b64 + b"\n\n")
                    self.wfile.flush()
                    time.sleep(period)
            except (BrokenPipeError, ConnectionResetError, OSError):
                pass
            finally:
                self.close_connection = True

        def _audio(self, name):
            """Serve the track with range support -- phones seek by range."""
            safe = os.path.basename(name)
            full = os.path.join(HERE, safe)
            if not os.path.exists(full):
                return self._send({"error": "no such track"}, code=404)
            size = os.path.getsize(full)
            ctype = mimetypes.guess_type(full)[0] or "audio/mpeg"
            rng = self.headers.get("Range")
            start, end = 0, size - 1
            if rng and rng.startswith("bytes="):
                a, _, b = rng[6:].partition("-")
                start = int(a) if a else 0
                end = int(b) if b else size - 1
            end = min(end, size - 1)
            n = end - start + 1
            self.send_response(206 if rng else 200)
            self.send_header("Content-Type", ctype)
            self.send_header("Accept-Ranges", "bytes")
            self.send_header("Content-Length", str(n))
            if rng:
                self.send_header("Content-Range", "bytes %d-%d/%d" % (start, end, size))
            self.end_headers()
            if self._head_only:
                return
            try:
                with open(full, "rb") as f:
                    f.seek(start)
                    left = n
                    while left > 0:
                        chunk = f.read(min(65536, left))
                        if not chunk:
                            break
                        self.wfile.write(chunk)
                        left -= len(chunk)
            except (BrokenPipeError, ConnectionResetError):
                self.close_connection = True

        def do_POST(self):
            path = urllib.parse.urlparse(self.path).path
            n = int(self.headers.get("Content-Length") or 0)
            raw = self.rfile.read(n)
            # JSON only.  This listens on every interface with no login,
            # and a text/plain POST is one any web page can send from any
            # browser on the same network without asking -- it was enough
            # to save a favourite whose label ran script in the control
            # page.  application/json makes the browser ask first, and
            # nothing here answers OPTIONS, so the cross-site write never
            # leaves the browser.  control.html already sends it.
            ctype = (self.headers.get("Content-Type") or "").split(";")[0]
            if ctype.strip().lower() != "application/json":
                return self._send({"error": "send application/json"}, code=415)
            try:
                body = json.loads(raw or b"{}")
                if not isinstance(body, dict):
                    raise ValueError("expected a JSON object")
                if path == "/api/preset":
                    # Filter at the boundary: one generic control surface
                    # sends the same payload to every preset, so unknown
                    # keys are dropped and a colour is redirected to
                    # whatever that preset calls its colour.  The Python
                    # API stays strict.
                    cls = E.REGISTRY.get(body.get("name"))
                    if cls is None:
                        return self._send({"error": "no preset %r" % body.get("name")},
                                          code=404)
                    ctl.set_preset(body["name"], **cls.accepts(body.get("params")))
                elif path == "/api/show":
                    ctl.set_show(body["name"])
                elif path == "/api/clock":
                    ctl.clock(body.get("t"), body.get("playing"),
                              body.get("seq"), body.get("sid"), body.get("pt"))
                elif path == "/api/sync":
                    if "sync" in body:
                        ctl.sync = bool(body["sync"])
                    if "pulse" in body:
                        ctl.pulse = max(0.0, min(1.0, float(body["pulse"])))
                elif path == "/api/brightness":
                    ctl.brightness = max(0.0, min(1.0, float(body["value"])))
                elif path == "/api/save":
                    ctl.save_favourite(body.get("label", ""))
                elif path == "/api/recall":
                    ctl.recall_favourite(body.get("label", ""))
                elif path == "/api/forget":
                    ctl.forget_favourite(body.get("label", ""))
                elif path == "/api/off":
                    ctl.off()
                else:
                    return self._send({"error": "no route"}, code=404)
            except Exception as e:
                return self._send({"error": "%s: %s" % (type(e).__name__, e)}, code=400)
            return self._send(ctl.state())
    return H


class _DualStack(ThreadingHTTPServer):
    """Listen on IPv4 and IPv6 at once.

    Bound to 0.0.0.0 this answers 127.0.0.1 and nothing else, and
    anything that resolves "localhost" to ::1 first -- cloudflared
    does -- gets connection refused and reports the whole service as
    down.  That failure is intermittent, because it depends on which
    address the resolver hands back, which makes it look like flakiness
    rather than a missing listener.
    """

    address_family = socket.AF_INET6
    daemon_threads = True
    allow_reuse_address = True

    def server_bind(self):
        try:
            self.socket.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)
        except OSError:
            pass
        return ThreadingHTTPServer.server_bind(self)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter,
                                 epilog=__doc__)
    ap.add_argument("--host", help="WLED address (default: find it)")
    ap.add_argument("--port", type=int, default=8760)
    ap.add_argument("--fps", type=int, default=40)
    ap.add_argument("--no-wled", action="store_true", help="UI only, no helmet")
    ap.add_argument("--preset", help="start in this preset, e.g. alignbar")
    a = ap.parse_args(argv)

    pix = w = None
    if not a.no_wled:
        w = mau5wled.find_one(a.host)
        print(w.describe())
        w.realtime(True, brightness=255)
        pix = mau5wled.Pixels(w, w.count or 622)
        if pix.guard is None:
            raise SystemExit("refusing to start with no power profile -- "
                             "data/cal/power.json is missing and this helmet "
                             "overheats.")
        print("power guard: %.0f mA budget, %d regions"
              % (pix.guard.budget_ma, len(pix.guard.regions)))
        if pix.guard.link_ma:
            print("             weakest connector rated %.0f mA, leaving %.0f mA "
                  "for the LEDs" % (pix.guard.link_ma, pix.guard.link_limit_ma()))
        else:
            print("             no connector rating set.  The budget assumes the "
                  "wiring can carry\n"
                  "             %.1f A continuously; set link_ma in "
                  "data/cal/power.json if it cannot."
                  % ((pix.guard.budget_ma + pix.guard.standby_ma()) / 1000.0))

    ctl = Controller(pix, fps=a.fps, wled=(None if a.no_wled else w))
    if a.preset:
        cls = E.REGISTRY.get(a.preset)
        if cls is None:
            raise SystemExit("no preset %r.  Known: %s"
                             % (a.preset, ", ".join(sorted(E.REGISTRY))))
        ctl.set_preset(a.preset)
        print("starting in preset: %s" % a.preset)
    srv = _DualStack(("::", a.port), make_handler(ctl))
    print("\n  open on your phone:   http://%s:%d/\n"
          % (mau5wled.lan_ip(), a.port))
    print("  %d presets, %d shows" % (len(E.REGISTRY), len(ctl.state()["shows"])))
    print("  audio plays on the phone, so it follows whatever that is paired to")
    print("  ctrl-c to stop")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        ctl.stop = True
        time.sleep(0.2)
        if pix:
            for _ in range(4):
                pix.clear(); time.sleep(0.05)
        print("\n  blanked.")


if __name__ == "__main__":
    main()
