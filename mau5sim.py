#!/usr/bin/env python3
"""mau5sim -- desktop simulator for the mau5head.

Watch a show before the helmet exists.  Three input forms, one renderer:

    ./mau5sim.py --demo                      built-in demo show
    ./mau5sim.py --fseq show.fseq --audio show.mp3
    ./mau5sim.py --ddp                       listen on UDP 4048
    ./mau5sim.py --effect myfx.py:swirl --seconds 30
    ./mau5sim.py --demo --export preview.mp4

The left panel is the real thing: every pixel drawn at its ``pixel_map.csv``
position on the sphere, with the ear rims, ear blades and visor light pipes as
separate geometry, over the decimated backdrop mesh.  The right panel is the
unwrapped 22 x 68 grid plus the accessory strips -- what xLights shows you.

Timing is clock-driven at 40 fps, not draw-driven: the frame index comes from
the wall clock (which the audio also runs on), so a slow redraw drops frames
instead of drifting out of sync.  Read the "renders at" line it prints on
exit -- matplotlib will not hold 40 fps with 1406 live pixels and it does not
need to.
"""

from __future__ import annotations

import argparse
import importlib.util
import math
import os
import shutil
import subprocess
import sys
import time

import numpy as np

import mau5cfg
import mau5fseq
import mau5fx

# --------------------------------------------------------------------------
# sources
# --------------------------------------------------------------------------

_SUPERSEDED = """
  ------------------------------------------------------------------
  mau5sim reads helmet.toml, which describes the helmet as it was
  CAD'd: a full sphere of 1185 pixels on two chains, driven by a
  Raspberry Pi running FPP.

  The helmet that exists is 622 WS2815 on ONE chain: 399 on the front
  shell, 224 across two rebuilt ears, straight into WLED over DDP.
  Nothing on the current path reads this file.

  Use instead:
      data/cal/pixel_map.csv   the real geometry   (mau5map.py)
      data/cal/power.json      the thermal limits  (mau5power.py)
      mau5engine.py            presets
      mau5preview.py           the simulator
      mau5ctl.py               the controller
      mau5doctor.py            check everything at once
  ------------------------------------------------------------------
"""


def _warn_superseded():
    import sys
    print(_SUPERSEDED, file=sys.stderr)


class Source:
    """Anything that can hand the renderer a (n_total, 3) uint8 frame."""

    name = "source"
    n_frames = None          # None = open ended (a live stream)

    def frame(self, i, t):
        raise NotImplementedError

    def close(self):
        pass


class EffectSource(Source):
    """A Timeline, an Effect, or a plain ``f(buf, i, t)`` callable."""

    def __init__(self, helmet, thing, seconds=None, fps=None):
        self.h = helmet
        self.fps = float(fps or helmet.fps)
        self.name = getattr(thing, "__name__", type(thing).__name__)
        if isinstance(thing, mau5fx.Timeline):
            self.fn = lambda buf, i, t: buf.__setitem__(
                slice(None), thing.render_frame(i, t))
            seconds = seconds or thing.duration
        elif isinstance(thing, mau5fx.Effect):
            self.fn = thing.render
        else:
            self.fn = thing
        self.n_frames = int(seconds * self.fps) if seconds else None

    def frame(self, i, t):
        buf = self.h.blank()
        # render at the frame's own time, not the wall clock, so the preview is
        # the same frame mau5build would put in the FSEQ
        self.fn(buf, i, i / self.fps)
        return buf


class LayoutSource(Source):
    """Not a show -- a picture of the wiring.

    Every LED is lit, hue keyed to its output and brightness ramping along the
    chain, so you can read the data order straight off the helmet and check it
    against the real strip.  This is the view to compare against the CAD.
    """

    name = "layout"

    def __init__(self, helmet, mode="output"):
        self.h = helmet
        self.mode = mode
        buf = helmet.blank()
        base = {0: (0, 200, 255), 1: (255, 40, 160), 2: (120, 255, 60)}
        for k, o in enumerate(helmet.outputs):
            lo, hi = o.start, o.start + o.count
            col = np.array(base.get(k, (255, 255, 255)), np.float32)
            ramp = np.linspace(0.28, 1.0, hi - lo)[:, None]
            buf[lo:hi] = np.clip(col * ramp, 0, 255).astype(np.uint8)
        for f in helmet.fixtures:                      # accessories in amber
            ramp = np.linspace(0.30, 1.0, f.count)[:, None]
            buf[f.slice] = np.clip(np.array([255, 170, 30], np.float32) * ramp,
                                   0, 255).astype(np.uint8)
        self.buf = buf
        self.n_frames = None

    def frame(self, i, t):
        return self.buf

    def status(self):
        return "  ".join("%s=%d" % (o.name, o.count) for o in self.h.outputs)


class FseqSource(Source):
    """An FSEQ exported by xLights or built by mau5build."""

    def __init__(self, helmet, path):
        self.h = helmet
        self.seq = mau5fseq.FseqReader(path)
        self.name = os.path.basename(path)
        self.n_frames = self.seq.frame_count
        self.n_leds = min(helmet.n_total, self.seq.channel_count // 3)
        if self.seq.channel_count != helmet.channel_count:
            print("note: %s carries %d channels, the helmet wants %d -- "
                  "showing the first %d LEDs"
                  % (self.name, self.seq.channel_count, helmet.channel_count,
                     self.n_leds), file=sys.stderr)
        if abs(self.seq.fps - helmet.fps) / max(helmet.fps, 1) > 1e-3:
            print("note: %s is %.4g fps, helmet.toml says %d -- playing at the "
                  "file's rate" % (self.name, self.seq.fps, helmet.fps),
                  file=sys.stderr)

    @property
    def fps(self):
        return self.seq.fps or None

    def frame(self, i, t):
        buf = self.h.blank()
        px = self.seq.pixels(min(i, self.n_frames - 1))
        buf[:self.n_leds] = px[:self.n_leds]
        return buf

    def close(self):
        self.seq.close()


class DdpSource(Source):
    """Live DDP -- point WLED, xLights or FPP output straight at this machine."""

    def __init__(self, helmet, port=4048):
        self.h = helmet
        self.name = "DDP :%d" % port
        self.rx = mau5fseq.DDPReceiver(port=port,
                                       channel_count=helmet.channel_count).start()
        self._last = helmet.blank()

    def frame(self, i, t):
        data = self.rx.latest()
        if data is None:
            return self._last
        n = min(self.h.n_total, len(data) // 3)
        buf = self.h.blank()
        buf[:n] = data[:n * 3].reshape(n, 3)
        self._last = buf
        return buf

    def status(self):
        age = time.time() - self.rx.last_time if self.rx.frames else None
        return ("%d pkts / %d frames%s" %
                (self.rx.packets, self.rx.frames,
                 "" if age is None else ", last %.1fs ago" % age))

    def close(self):
        self.rx.stop()


# --------------------------------------------------------------------------
# audio
# --------------------------------------------------------------------------
# (exe, argv, typical seconds between Popen returning and sound coming out)
AUDIO_PLAYERS = [
    ("afplay", ["afplay", "{f}"], 0.25),                        # macOS
    ("ffplay", ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", "{f}"], 0.15),
    ("mpv", ["mpv", "--no-video", "--really-quiet", "{f}"], 0.20),
    ("mpg123", ["mpg123", "-q", "{f}"], 0.10),
    ("aplay", ["aplay", "-q", "{f}"], 0.05),                    # wav only
]


class Audio:
    """Start an external player and let the wall clock do the syncing.

    No audio library: the simulator only needs the show to *start* with the
    music, and every desktop already has one of these on PATH.
    """

    def __init__(self, path, latency=None):
        self.path = path
        self.proc = None
        self.cmd = None
        self.latency = 0.0
        for exe, argv, lat in AUDIO_PLAYERS:
            if shutil.which(exe):
                self.cmd = [a.format(f=path) for a in argv]
                self.latency = lat if latency is None else latency
                self.exe = exe
                break
        if self.cmd is None and latency is not None:
            self.latency = latency

    def start(self):
        if not self.path:
            return False
        if not self.cmd:
            print("no audio player found (tried %s) -- running silent"
                  % ", ".join(e for e, _a, _l in AUDIO_PLAYERS), file=sys.stderr)
            return False
        self.proc = subprocess.Popen(self.cmd, stdout=subprocess.DEVNULL,
                                     stderr=subprocess.DEVNULL)
        return True

    def stop(self):
        if self.proc and self.proc.poll() is None:
            self.proc.terminate()


# --------------------------------------------------------------------------
# renderer
# --------------------------------------------------------------------------
def _eye_vector(azim_deg, elev_deg):
    az, el = math.radians(azim_deg), math.radians(elev_deg)
    return np.array([math.cos(el) * math.cos(az), math.cos(el) * math.sin(az),
                     math.sin(el)], np.float64)


class Renderer:
    def __init__(self, helmet, view="both", backdrop=True, backdrop_faces=6000,
                 figsize=None, dpi=100, title="", azim=-90.0, elev=12.0,
                 pixel_px=22.0, grid_front=True, cull_backdrop=True):
        import matplotlib
        if not os.environ.get("DISPLAY") and sys.platform.startswith("linux"):
            matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from mpl_toolkits.mplot3d.art3d import Poly3DCollection

        self.h = helmet
        self.view = view
        self.plt = plt
        self.cam_azim, self.cam_elev, self.pixel_px = azim, elev, pixel_px
        self.grid_front = grid_front
        self._cam = (round(azim, 3), round(elev, 3))
        self.mesh = self.tri = self.tri_colors = None
        self._cull = cull_backdrop
        cfg = helmet.cfg.get("sim", {})
        bg = cfg.get("background", "#0d0d10")

        cols = {"both": 2, "3d": 1, "2d": 1}[view]
        figsize = figsize or ((13, 6.5) if cols == 2 else (7.5, 6.5))
        self.fig = plt.figure(figsize=figsize, dpi=dpi, facecolor=bg)
        self.fig.canvas.manager.set_window_title("mau5sim -- %s" % title)

        self.ax3 = self.ax2 = None
        slot = 1
        if view in ("both", "3d"):
            self.ax3 = self.fig.add_subplot(1, cols, slot, projection="3d")
            slot += 1
        if view in ("both", "2d"):
            self.ax2 = self.fig.add_subplot(1, cols, slot)

        self.bg = bg
        if self.ax3 is not None:
            self._setup_3d(Poly3DCollection, backdrop, backdrop_faces,
                           cull_backdrop=cull_backdrop)
        if self.ax2 is not None:
            self._setup_2d()

        self.txt = self.fig.text(0.5, 0.975, "", ha="center", va="top",
                                 color="#c8c8d0", fontsize=9, family="monospace")
        self.fig.subplots_adjust(left=0.02, right=0.98, top=0.93, bottom=0.05,
                                 wspace=0.10)
        if self.ax2 is not None:
            self._layout_strips()          # after subplots_adjust, which resets it
        self._bgcache = None

    # -- 3D ---------------------------------------------------------------
    def _setup_3d(self, Poly3DCollection, backdrop, max_faces,
                  cull_backdrop=True):
        h = self.h
        ax = self.ax3
        ax.set_facecolor(self.bg)
        ax.set_axis_off()
        if backdrop:
            path = os.path.join(os.path.dirname(os.path.abspath(h.path)),
                                h.cfg.get("sim", {}).get("backdrop_glb",
                                                         "mau5head_sim_backdrop.glb"))
            if os.path.exists(path):
                V, F = mau5cfg.load_glb(path)
                V, F = mau5cfg.decimate_mesh(V.astype(np.float64), F, max_faces)
                self.tri = V[F]
                n = np.cross(self.tri[:, 1] - self.tri[:, 0],
                             self.tri[:, 2] - self.tri[:, 0])
                n /= (np.linalg.norm(n, axis=1, keepdims=True) + 1e-9)
                light = np.array([0.35, -0.75, 0.55], np.float64)
                shade = 0.20 + 0.40 * np.abs((n * light).sum(1))
                alpha = float(h.cfg.get("sim", {}).get("backdrop_alpha", 0.18))
                self.tri_colors = np.clip(
                    np.column_stack([shade, shade, shade * 1.10,
                                     np.full(len(self.tri), alpha)]), 0, 1)
                self.mesh = Poly3DCollection(self.tri, facecolors=self.tri_colors,
                                             edgecolors="none", zsort="average")
                self.mesh.set_zorder(1)
                ax.add_collection3d(self.mesh)
                self.mesh_bounds = (V.min(0), V.max(0))
                # Each face is culled against the centre of the part it
                # belongs to, not against the world origin.  Culling the ears
                # against the origin deletes a whole ear disc the moment it
                # swings to the near side -- which is what makes the ear LEDs
                # look detached from the head when you rotate the view.
                self.cull_ref = self._part_centres(self.tri.mean(1))
                self._cull = cull_backdrop
                self._update_backdrop(self.cam_azim, self.cam_elev)
            else:
                print("backdrop %s not found -- drawing pixels only" % path,
                      file=sys.stderr)
                self.mesh_bounds = None
        else:
            self.mesh_bounds = None

        xyz = h.xyz
        lo = np.minimum(xyz.min(0), self.mesh_bounds[0] if self.mesh_bounds else xyz.min(0))
        hi = np.maximum(xyz.max(0), self.mesh_bounds[1] if self.mesh_bounds else xyz.max(0))
        pad = (hi - lo) * 0.03
        lo, hi = lo - pad, hi + pad
        ax.set_xlim(lo[0], hi[0])
        ax.set_ylim(lo[1], hi[1])
        ax.set_zlim(lo[2], hi[2])
        try:
            ax.set_box_aspect(tuple(hi - lo), zoom=1.28)   # crop dead margin
        except TypeError:
            ax.set_box_aspect(tuple(hi - lo))              # matplotlib < 3.6
        ax.view_init(elev=self.cam_elev, azim=self.cam_azim)

        sizes = np.full(h.n_total, self.pixel_px)
        for f in h.fixtures:
            sizes[f.slice] = self.pixel_px * (0.6 if f.kind != "ring" else 0.5)
        self.scatter = ax.scatter(xyz[:, 0], xyz[:, 1], xyz[:, 2],
                                  s=sizes, marker="s", depthshade=False,
                                  linewidths=0, c=np.zeros((h.n_total, 4)))
        self.scatter.set_zorder(10)
        self.scatter.set_animated(True)

    def _part_centres(self, centroids):
        """Reference point for each face: the ear disc it lies on, else the
        sphere centre.  The ear geometry comes from helmet.toml, which is
        where the fitted disc centre, normal and radius already live."""
        ref = np.zeros_like(centroids)
        for spec in self.h.cfg.get("fixture", []):
            if spec.get("kind") != "ring":
                continue
            c = np.array([float(v) for v in spec["centre"]])
            n = np.array([float(v) for v in spec["normal"]])
            n = n / (np.linalg.norm(n) + 1e-9)
            d = (centroids - c).astype(np.float64)
            off = (d * n).sum(1)
            inplane = np.linalg.norm(d - off[:, None] * n, axis=1)
            on_disc = (np.abs(off) < 40.0) & (inplane < float(spec["radius_mm"]) * 1.15)
            ref[on_disc] = c
        return ref

    def _update_backdrop(self, azim, elev):
        """Re-cull and re-shade the mesh for a new camera angle.

        Only the far side of the head is drawn, so lit pixels are never behind
        grey polygons -- but "far side" depends on where you are looking from,
        so this has to run again every time the view rotates.
        """
        if getattr(self, "mesh", None) is None:
            return
        if not self._cull:
            return
        eye = _eye_vector(azim, elev)
        keep = ((self.tri.mean(1) - self.cull_ref) * eye).sum(1) < 0
        if not keep.any():
            keep = np.ones(len(self.tri), bool)
        self.mesh.set_verts(self.tri[keep])
        self.mesh.set_facecolor(self.tri_colors[keep])

    def _camera_moved(self):
        """True (and updates the backdrop) if the user has rotated the view."""
        if self.ax3 is None:
            return False
        cam = (round(float(self.ax3.azim), 3), round(float(self.ax3.elev), 3))
        if cam == self._cam:
            return False
        self._cam = cam
        self._update_backdrop(cam[0], cam[1])
        self.invalidate()          # the mesh lives in the blit cache
        return True

    # -- 2D ---------------------------------------------------------------
    def _setup_2d(self):
        h = self.h
        ax = self.ax2
        ax.set_facecolor(self.bg)
        # roll the columns so azimuth 0 (the face) sits in the middle; the tick
        # labels still show real channel numbers
        self.roll = h.channels // 2 if self.grid_front else 0
        self.order = np.roll(np.arange(h.channels), self.roll)
        self.im = ax.imshow(np.zeros((h.rows, h.channels, 3), np.uint8),
                            origin="lower", interpolation="nearest",
                            aspect="auto", extent=(0, h.channels, 0, h.rows))
        self.im.set_animated(True)
        ticks = list(range(0, h.channels + 1, 8))
        ax.set_xticks(ticks)
        ax.set_xticklabels([str(self.order[t % h.channels]) for t in ticks])
        ax.set_yticks(range(0, h.rows + 1, 4))
        ax.tick_params(colors="#606070", labelsize=7)
        for sp in ax.spines.values():
            sp.set_color("#303040")
        ax.set_xlabel("channel  (%s)" % ("face centred" if self.roll else "raw order"),
                      color="#808090", fontsize=8)
        ax.set_ylabel("row (elevation)", color="#808090", fontsize=8)
        if self.roll:
            ax.axvline(h.channels / 2.0, color="#404058", lw=0.8, ls=":")

        # dead cells get a faint wash so the holes stay visible when unlit
        self.grid_idx = h.grid[:, self.order]
        self.dead_rgb = np.zeros((h.rows, h.channels, 3), np.uint8)
        self.dead_rgb[self.grid_idx < 0] = (26, 26, 34)

        # accessory strips under the grid
        self.strip_axes = []
        n = len(h.fixtures)
        box = ax.get_position()
        for k, f in enumerate(h.fixtures):
            sub = self.fig.add_axes([box.x0, 0.0, 0.0, 0.0])
            sub.set_xticks([]); sub.set_yticks([])
            sub.set_facecolor(self.bg)
            for s in sub.spines.values():
                s.set_color("#303040")
            img = sub.imshow(np.zeros((1, f.count, 3), np.uint8), aspect="auto",
                             interpolation="nearest")
            img.set_animated(True)
            sub.text(-0.01, 0.5, f.id, transform=sub.transAxes, ha="right",
                     va="center", color="#808090", fontsize=7, family="monospace")
            self.strip_axes.append((sub, img, f))

    def _layout_strips(self):
        if not self.strip_axes:
            return
        box = self.ax2.get_position()
        n = len(self.strip_axes)
        pad, h_each = 0.006, 0.020
        total = n * (h_each + pad)
        self.ax2.set_position([box.x0, box.y0 + total, box.width,
                               box.height - total])
        y = box.y0
        for sub, _img, _f in reversed(self.strip_axes):
            sub.set_position([box.x0, y, box.width, h_each])
            y += h_each + pad

    # -- per frame --------------------------------------------------------
    def draw(self, buf, label=""):
        h = self.h
        artists = []
        if self.ax3 is not None:
            rgba = np.ones((h.n_total, 4), np.float32)
            rgba[:, :3] = buf.astype(np.float32) / 255.0
            # dim LEDs pointing away from the camera so the far side does not
            # bleed through the translucent shell
            self._camera_moved()
            eye = _eye_vector(self.ax3.azim, self.ax3.elev)
            facing = (h.normals * eye).sum(1)
            vis = np.clip((facing + 0.15) / 0.55, 0.06, 1.0)
            # the ear discs are flat plates: lit from whichever side you see
            flat = h.two_sided
            vis[flat] = np.clip(0.35 + 0.65 * np.abs(facing[flat]), 0.35, 1.0)
            rgba[:, :3] *= vis[:, None]
            rgba[:, 3] = np.clip(0.10 + 0.9 * vis, 0, 1)
            self.scatter.set_facecolors(rgba)
            self.scatter.set_edgecolors(rgba)
            artists.append(self.scatter)
        if self.ax2 is not None:
            img = self.dead_rgb.copy()
            live = self.grid_idx >= 0
            img[live] = buf[self.grid_idx[live]]
            self.im.set_data(img)
            artists.append(self.im)
            for _sub, im, f in self.strip_axes:
                im.set_data(buf[f.slice].reshape(1, f.count, 3))
                artists.append(im)
        if label:
            self.txt.set_text(label)
        return artists

    # -- window loop ------------------------------------------------------
    def show(self):
        self.plt.show(block=False)
        self.fig.canvas.draw()

    def blit(self, artists):
        """Redraw only the animated artists over a cached background."""
        cv = self.fig.canvas
        try:
            if self._bgcache is None:
                self.fig.canvas.draw()
                self._bgcache = cv.copy_from_bbox(self.fig.bbox)
            cv.restore_region(self._bgcache)
            for a in artists:
                a.axes.draw_artist(a)
            self.fig.draw_artist(self.txt)
            cv.blit(self.fig.bbox)
            cv.flush_events()
            return True
        except Exception:
            self._bgcache = None
            cv.draw()
            cv.flush_events()
            return False

    def invalidate(self):
        self._bgcache = None


# --------------------------------------------------------------------------
# playback
# --------------------------------------------------------------------------
def play(helmet, source, audio=None, view="both", loop=False, backdrop=True,
         backdrop_faces=6000, fps=None, camera=(-90.0, 12.0), pixel_px=22.0,
         grid_front=True, cull_backdrop=True, audio_offset=None):
    fps = fps or getattr(source, "fps", None) or helmet.fps
    r = Renderer(helmet, view=view, backdrop=backdrop,
                 backdrop_faces=backdrop_faces, title=source.name,
                 azim=camera[0], elev=camera[1], pixel_px=pixel_px,
                 grid_front=grid_front, cull_backdrop=cull_backdrop)
    r.show()

    au = Audio(audio, audio_offset) if audio else None
    total = source.n_frames
    print("playing %s  %s  %d fps%s"
          % (source.name,
             "%d frames (%.1f s)" % (total, total / fps) if total else "live",
             fps, "  + %s" % os.path.basename(audio) if audio else ""))
    print("close the window or ctrl-c to stop")

    started = bool(au and au.start())
    # A player takes a moment to actually make a sound.  Push the frame clock
    # forward by that much so frame 0 lands when the audio does, instead of the
    # lights running a quarter of a second ahead of the music.  (On the helmet
    # itself FPP drives audio and pixels off one clock, so this is a simulator
    # concern only.)
    lag = au.latency if started else 0.0
    t0 = time.monotonic() + lag
    if started and lag:
        print("audio via %s, frame clock delayed %.0f ms to match "
              "(--audio-offset to tune)" % (au.exe, lag * 1000))
    drawn, last_i = 0, -1
    try:
        while self_open(r):
            t = time.monotonic() - t0
            if t < 0:                       # waiting for the audio to come up
                time.sleep(min(0.01, -t))
                continue
            i = int(t * fps)
            if total and i >= total:
                if not loop:
                    break
                if au:
                    au.stop(); au.start()
                t0 = time.monotonic() + (au.latency if au else 0.0)
                continue
            if i == last_i and drawn:
                time.sleep(0.002)
                continue
            last_i = i
            buf = source.frame(i, t)
            extra = source.status() if hasattr(source, "status") else ""
            label = ("%6.2fs  frame %5d%s   %5.1f fps drawn   %s"
                     % (t, i, "/%d" % total if total else "",
                        drawn / max(t, 1e-6), extra))
            r.blit(r.draw(buf, label))
            drawn += 1
    except KeyboardInterrupt:
        print()
    finally:
        if au:
            au.stop()
        source.close()
        el = time.monotonic() - t0
        print("stopped after %.1f s -- show ran at %d fps, renders at %.1f fps"
              % (el, fps, drawn / max(el, 1e-6)))


def self_open(r):
    return bool(r.plt.fignum_exists(r.fig.number))


# --------------------------------------------------------------------------
# export
# --------------------------------------------------------------------------
def export(helmet, source, out, audio=None, view="both", seconds=None,
           backdrop=True, backdrop_faces=6000, dpi=100, fps=None,
           camera=(-90.0, 12.0), pixel_px=22.0, grid_front=True,
           cull_backdrop=True):
    import matplotlib
    matplotlib.use("Agg")
    fps = fps or getattr(source, "fps", None) or helmet.fps
    n = source.n_frames or int((seconds or 10) * fps)
    if seconds:
        n = min(n, int(seconds * fps))

    r = Renderer(helmet, view=view, backdrop=backdrop,
                 backdrop_faces=backdrop_faces, dpi=dpi, title=source.name,
                 azim=camera[0], elev=camera[1], pixel_px=pixel_px,
                 grid_front=grid_front, cull_backdrop=cull_backdrop)
    r.fig.canvas.draw()
    w, hgt = r.fig.canvas.get_width_height()

    ff = shutil.which("ffmpeg")
    frames_dir = None
    if ff:
        cmd = [ff, "-y", "-loglevel", "error",
               "-f", "rawvideo", "-pix_fmt", "rgba", "-s", "%dx%d" % (w, hgt),
               "-r", str(fps), "-i", "-"]
        if audio:
            cmd += ["-i", audio, "-c:a", "aac", "-shortest"]
        cmd += ["-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", out]
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        sink = proc.stdin
    else:
        from PIL import Image
        print("ffmpeg not on PATH -- writing an animated GIF instead of MP4.\n"
              "  install ffmpeg for a real .mp4 (and to mux the audio in).",
              file=sys.stderr)
        out = os.path.splitext(out)[0] + ".gif"
        gif_frames = []
        proc = sink = None

    print("rendering %d frames -> %s" % (n, out))
    t_start = time.monotonic()
    for i in range(n):
        buf = source.frame(i, i / fps)
        r.draw(buf, "%6.2fs  frame %5d/%d" % (i / fps, i, n))
        r.fig.canvas.draw()
        rgba = np.asarray(r.fig.canvas.buffer_rgba())
        if sink:
            sink.write(rgba.tobytes())
        else:
            gif_frames.append(Image.fromarray(rgba[:, :, :3].copy()))
        if i % 40 == 0 or i == n - 1:
            done = i + 1
            rate = done / max(time.monotonic() - t_start, 1e-6)
            sys.stdout.write("\r  %d/%d  %.1f frames/s  eta %4.0f s"
                             % (done, n, rate, (n - done) / max(rate, 1e-6)))
            sys.stdout.flush()
    print()
    if sink:
        sink.close()
        proc.wait()
    else:
        gif_frames[0].save(out, save_all=True, append_images=gif_frames[1:],
                           duration=int(1000 / fps), loop=0)
    source.close()
    print("wrote %s (%.1f MB)" % (out, os.path.getsize(out) / 1e6))
    return out


# --------------------------------------------------------------------------
# --effect loading
# --------------------------------------------------------------------------
def load_effect(spec, helmet, seconds=None, fps=None):
    """``path/to/file.py:name`` -> Timeline | Effect | f(buf, i, t)."""
    path, _, name = spec.partition(":")
    name = name or "effect"
    mod_name = "mau5_user_" + os.path.splitext(os.path.basename(path))[0]
    sp = importlib.util.spec_from_file_location(mod_name, path)
    if sp is None:
        raise SystemExit("cannot import %s" % path)
    mod = importlib.util.module_from_spec(sp)
    sys.modules[mod_name] = mod
    sp.loader.exec_module(mod)
    if not hasattr(mod, name):
        raise SystemExit("%s has no attribute %r (try file.py:name)" % (path, name))
    thing = getattr(mod, name)
    if isinstance(thing, type):                       # an Effect subclass
        thing = thing(helmet)
    elif callable(thing) and not isinstance(thing, (mau5fx.Effect, mau5fx.Timeline)):
        try:                                          # a factory f(helmet)?
            made = thing(helmet)
            if isinstance(made, (mau5fx.Effect, mau5fx.Timeline)) or callable(made):
                thing = made
        except TypeError:
            pass                                      # plain f(buf, i, t)
    return EffectSource(helmet, thing, seconds, fps)


# --------------------------------------------------------------------------
def main(argv=None):
    ap = argparse.ArgumentParser(
        description="mau5head simulator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__.split("The left panel")[0].split("Watch a show")[1])
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--fseq", help="play an FSEQ file")
    src.add_argument("--ddp", action="store_true",
                     help="listen for a live DDP stream")
    src.add_argument("--effect", metavar="FILE.py:NAME",
                     help="call your own effect once per frame")
    src.add_argument("--demo", action="store_true", help="built-in demo show")
    src.add_argument("--layout", action="store_true",
                     help="light every LED, coloured by output and chain order, "
                          "to check the map against the CAD")

    ap.add_argument("--config", default=mau5cfg.DEFAULT_CONFIG)
    ap.add_argument("--audio", help="audio file to play in sync")
    ap.add_argument("--audio-offset", type=float, metavar="MS",
                    help="ms the player takes to start making sound; the frame "
                         "clock waits that long. Raise it if the lights run "
                         "ahead of the music, lower it if they lag")
    ap.add_argument("--seconds", type=float, help="length for --effect / --demo")
    ap.add_argument("--fps", type=float, help="override the frame rate")
    ap.add_argument("--port", type=int, help="DDP listen port")
    ap.add_argument("--view", choices=["both", "3d", "2d"], default="both")
    ap.add_argument("--loop", action="store_true")
    ap.add_argument("--no-backdrop", action="store_true",
                    help="skip the GLB mesh (much faster)")
    ap.add_argument("--backdrop-faces", type=int, default=6000,
                    help="triangle budget for the backdrop mesh")
    ap.add_argument("--export", metavar="OUT.mp4",
                    help="render to a video instead of showing a window")
    ap.add_argument("--dpi", type=int, default=100)
    ap.add_argument("--azim", type=float, default=-90.0, help="camera azimuth")
    ap.add_argument("--elev", type=float, default=12.0, help="camera elevation")
    ap.add_argument("--pixel-size", type=float, default=22.0,
                    help="drawn size of one pixel in the 3D view")
    ap.add_argument("--solid-backdrop", action="store_true",
                    help="draw the whole backdrop mesh, not just its far side")
    ap.add_argument("--grid-raw", action="store_true",
                    help="2D grid in raw channel order instead of face centred")
    a = ap.parse_args(argv)

    helmet = mau5cfg.load(a.config)
    print(helmet.describe())

    if a.fseq:
        source = FseqSource(helmet, a.fseq)
        if not a.audio and source.seq.media:
            guess = os.path.join(os.path.dirname(os.path.abspath(a.fseq)),
                                 source.seq.media)
            if os.path.exists(guess):
                a.audio = guess
                print("using media from the fseq header: %s" % source.seq.media)
    elif a.ddp:
        port = a.port or int(helmet.cfg.get("sim", {}).get("ddp_listen_port", 4048))
        source = DdpSource(helmet, port)
    elif a.layout:
        source = LayoutSource(helmet)
    elif a.effect:
        source = load_effect(a.effect, helmet, a.seconds, a.fps)
    else:
        tl = mau5fx.demo_show(helmet, a.seconds or 30.0)
        source = EffectSource(helmet, tl, a.seconds or 30.0, a.fps)
        source.name = "demo show"

    if a.export:
        export(helmet, source, a.export, audio=a.audio, view=a.view,
               seconds=a.seconds, backdrop=not a.no_backdrop,
               backdrop_faces=a.backdrop_faces, dpi=a.dpi, fps=a.fps,
               camera=(a.azim, a.elev), pixel_px=a.pixel_size,
               grid_front=not a.grid_raw, cull_backdrop=not a.solid_backdrop)
    else:
        play(helmet, source, audio=a.audio, view=a.view, loop=a.loop,
             backdrop=not a.no_backdrop, backdrop_faces=a.backdrop_faces,
             fps=a.fps, camera=(a.azim, a.elev), pixel_px=a.pixel_size,
             grid_front=not a.grid_raw, cull_backdrop=not a.solid_backdrop,
             audio_offset=None if a.audio_offset is None else a.audio_offset / 1000.0)


if __name__ == "__main__":
    _warn_superseded()
    main()
