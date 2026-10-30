#!/usr/bin/env python3
"""mau5scene -- shows choreographed per song, instead of a playlist of effects.

A cue-list show (mau5show.build) picks a stock preset for each phrase
from a pool and holds it.  It follows the music's level and lands on its
beats, and it still reads as a playlist: the same eight effects in a
different order for every song, none of them about the song.  What the
owner asked for is what deadmau5's own shows do -- each track gets its
own visual language: its own colours, its own motifs that come back
when the music does, builds that visibly grow, drops that land on the
bar the bass lands on, a breakdown stripped back to almost nothing, a
title that crosses the face once, and the ears played as an instrument
of their own rather than as more screen.

So a song owns a treatment, shows/scenes/<base>.scene.json, written by
hand in bars against that song's own bar map, and this module compiles
it into the show it belongs to as `show["scenes"]`.  The cue list stays
where it is, untouched, and is what plays if the scenes are absent,
switched off (`mode: "cues"`, MAU5_CUES=1, `?cues` on the phone) or
throw.

Every frame is a pure function of the time, plus optionally the band
curves, on the analysis' beat grid -- which is exactly linear for every
shipped song (the spread of beat intervals is about 2e-14 s).  That one
decision buys three things.  The phone and the laptop can agree to the
last bit, because there is no state for them to disagree about.  Seeking
and pausing cost nothing.  And the show stays in sync from the audio
element's own clock whether or not the phone ever fetched a drive file.

    python3 mau5scene.py bars    "deadmau5 - Strobe" [from] [to]
    python3 mau5scene.py compile "deadmau5 - Strobe"
    python3 mau5scene.py check   "deadmau5 - Strobe"

remote/offline/show.js holds the JavaScript twin of Scenes below.  The
arithmetic is written out in the same order on both sides, because the
test holds them to a hundredth of a count.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import os
import re
import sys
import time

import numpy as np

import mau5engine as E

HERE = os.path.dirname(os.path.abspath(__file__))
SHOWS = os.path.join(HERE, "shows")
SCENES = os.path.join(SHOWS, "scenes")

# The beat pulse's peak hold, the same 70 ms as mau5show.PULSE_HOLD_S:
# longer than the slowest gap between the phone's frames, so every
# gate, spark and blade is seen at its full height on either device
# before it decays.  Imported rather than copied, so they cannot part.
from mau5show import PULSE_HOLD_S  # noqa: E402

CELL = 16.7                 # mm per glyph column, TextScroll's default
LINEAR_TOL_S = 0.005        # a grid this far from straight is refused

FX = ("fill", "grad", "sweep", "sparks", "blades", "preset")
MIX = ("add", "max", "over")
# Only the presets that are stateless and already parity-tested between
# the two languages may be layers: a stateful one would remember a frame
# the other player never rendered.
PRESETS = ("text", "sprite", "eyes")
REGIONS = ("all", "shell", "ears", "ear1", "ear2", "tubes", "rims",
           "tube0", "tube1", "tube2", "left", "right", "face")
AXES = ("x", "y", "r", "a", "al", "u")
WAVES = ("tri", "saw")
SHAPES = ("p", "saw", "tri")
MODES = ("band", "fill")
SIDES = ("both", "alt", "ear1", "ear2")

# Everything a layer may say, with its default.  The compiler writes
# every one of these into the show, so the phone has no table of
# defaults to keep in step: it evaluates exactly what is in the JSON.
COMMON = {"on": None, "mix": "add", "pal": None, "gain": 1.0, "c": 0.5,
          "gate": None, "env": None}
DEFAULT_ON = {"fill": "all", "grad": "shell", "sweep": "shell",
              "sparks": "shell", "blades": "ears", "preset": "face"}
FX_VALUES = {
    "fill": {},
    "grad": {"scale": 1.0, "speed": 0.0, "ofs": 0.0, "warp": 0.0,
             "wscale": 1.0, "wspeed": 0.0, "lo": 0.0, "hi": 1.0},
    "sweep": {"speed": 0.25, "width": 0.15, "soft": 0.1, "cgrad": 0.0,
              "from": 0.0, "to": 1.0},
    "sparks": {"rate": 1.0, "life": 1.0, "spread": 0.0, "nbr": 0.4},
    "blades": {"step": 1.0, "rise": 0.35, "keep": 0.15, "ctip": 1.0, "rim": 0.0},
    "preset": {},
}
FX_STATIC = {
    "fill": {},
    "grad": {"axis": "y", "axis2": "x", "wave": "tri"},
    "sweep": {"axis": "y", "shape": "saw", "mode": "band"},
    "sparks": {"loop": 0, "seed": 0.0},
    "blades": {"seq": ["0", "1", "2", "012"], "side": "both"},
    "preset": {"name": None, "params": None, "fit": False},
}

MAX_SCENE_LAYERS, MAX_HIT_LAYERS, MAX_HITS_AT_ONCE = 6, 3, 2


class TreatmentError(ValueError):
    pass


# ----------------------------------------------------------------------
# the treatment
# ----------------------------------------------------------------------
def treatment_path(base):
    return os.path.join(SCENES, base + ".scene.json")


def load_treatment(base_or_path):
    """Read a treatment, stamped with a hash of its bytes.

    The stamp travels into the compiled show, so a show compiled from an
    older treatment than the one on disk is visible as exactly that.
    """
    path = (base_or_path if base_or_path.endswith(".json")
            else treatment_path(base_or_path))
    with open(path, "rb") as f:
        raw = f.read()
    tr = json.loads(raw.decode("utf-8"))
    tr["_sha"] = hashlib.sha1(raw).hexdigest()[:12]
    return tr


def grid_of(music):
    """(grid, bars) from an analysis, refusing a grid that is not straight.

    Scenes put every frame on t0 + beats * spb.  That is only the music's
    grid if the analysis' beats really are evenly spaced, so this checks
    every beat and every bar against the line and refuses to compile if
    any is more than 5 ms off -- a drifting track would need the measured
    beats, and this format does not carry them.
    """
    beats = np.asarray(music.beats, float)
    bars = np.asarray(music.bars, float)
    if len(beats) < 8 or len(bars) < 2:
        raise TreatmentError("the analysis has too few beats for a scene grid")
    spb = float((beats[-1] - beats[0]) / (len(beats) - 1))
    t0 = float(bars[0])
    off = np.abs(beats - (beats[0] + spb * np.arange(len(beats)))).max()
    boff = np.abs(bars - (t0 + 4.0 * spb * np.arange(len(bars)))).max()
    onbeat = np.abs(beats - t0).min()
    worst = max(float(off), float(boff), float(onbeat))
    if worst > LINEAR_TOL_S:
        raise TreatmentError("the beat grid is %.1f ms from linear; scenes need "
                             "a steady grid" % (worst * 1000))
    return {"t0": t0, "spb": spb}, int(len(bars))


def src_of(base):
    """The analysis' own stamp of its audio, or '' for an older cache."""
    p = os.path.join(SHOWS, base + ".analysis.npz")
    try:
        z = np.load(p)
        return str(z["src"]) if "src" in z else ""
    except (OSError, ValueError):
        return ""


_HELMET = None


def _helmet():
    global _HELMET
    if _HELMET is None:
        _HELMET = E.Helmet()
    return _HELMET


def _edge_mm(h):
    """Where a word must start to be wholly off the shell: one cell past it."""
    return float(np.abs(h.px[h.shell]).max()) + CELL


class _Compiler:
    """Turns an authored treatment into the canonical, defaults-filled form."""

    def __init__(self, tr, grid, bars, h):
        self.tr, self.grid, self.bars, self.h = tr, grid, bars, h
        # Marks in order, each a number or an earlier mark plus or minus.
        self.marks = {}
        for k, v in (tr.get("marks") or {}).items():
            self.marks[k] = None
            self.marks[k] = self.bar(v, "mark %s" % k)
        self.pal = {}
        for name, p in (tr.get("palettes") or {}).items():
            if isinstance(p, dict):
                stops, wrap = p.get("stops"), bool(p.get("wrap", False))
            else:
                stops, wrap = p, False
            if not isinstance(stops, list) or len(stops) < 2:
                raise TreatmentError("palette %s needs two stops or more" % name)
            stops = [[int(round(float(x))) for x in s] for s in stops]
            for s in stops:
                if len(s) != 3 or min(s) < 0 or max(s) > 255:
                    raise TreatmentError("palette %s has a stop %r outside RGB"
                                         % (name, s))
            self.pal[name] = {"stops": stops, "wrap": wrap}
        if not self.pal:
            raise TreatmentError("a treatment needs at least one palette")
        self.motifs = tr.get("motifs") or {}

    # -- bars and values -------------------------------------------------
    def bar(self, v, what="bar"):
        """A bar: a number, a mark, or 'mark+N' / 'mark-N'."""
        if isinstance(v, bool):
            raise TreatmentError("%s: %r is not a bar" % (what, v))
        if isinstance(v, (int, float)):
            return float(v)
        if isinstance(v, str):
            s = v.strip()
            try:
                return float(s)
            except ValueError:
                pass
            m = re.match(r"^([A-Za-z_][\w ]*?)\s*(?:([+-])\s*([\d.]+))?$", s)
            if m and m.group(1) in self.marks:
                base = self.marks[m.group(1)]
                if base is None:
                    raise TreatmentError("%s: mark %s is defined in terms of "
                                         "itself" % (what, m.group(1)))
                d = float(m.group(3)) if m.group(3) else 0.0
                return base + (d if m.group(2) != "-" else -d)
        raise TreatmentError("%s: %r is not a number or a mark" % (what, v))

    def value(self, v, what):
        """Any authored number into one of the four canonical forms."""
        if isinstance(v, bool):
            raise TreatmentError("%s: %r is not a number" % (what, v))
        if isinstance(v, (int, float)):
            return {"n": float(v)}
        if isinstance(v, list):
            if len(v) != 2:
                raise TreatmentError("%s: a ramp is [from, to]" % what)
            return {"ramp": [float(v[0]), float(v[1])]}
        if isinstance(v, dict):
            if "n" in v:
                return {"n": float(v["n"])}
            if "ramp" in v:
                return self.value(v["ramp"], what)
            if "band" in v:
                if v["band"] not in ("bass", "mid", "high"):
                    raise TreatmentError("%s: no band %r" % (what, v["band"]))
                return {"band": v["band"], "lo": float(v.get("lo", 0.0)),
                        "hi": float(v.get("hi", 1.0)),
                        "punch": bool(v.get("punch", False))}
            src = v["keys"] if "keys" in v else list(v.items())
            keys = sorted([self.bar(b, what), float(x)] for b, x in src)
            if not keys:
                raise TreatmentError("%s: keys need at least one entry" % what)
            return {"keys": keys}
        raise TreatmentError("%s: %r is not a value" % (what, v))

    def colour(self, v, what):
        """An RGB list, or 'pal@pos' looked up in a palette."""
        if isinstance(v, str) and "@" in v:
            name, pos = v.split("@", 1)
            if name not in self.pal:
                raise TreatmentError("%s: no palette %s" % (what, name))
            p = self.pal[name]
            rgb = pal_lookup(np.array(p["stops"], float), p["wrap"], float(pos))
            return [int(round(x)) for x in rgb]
        if isinstance(v, (list, tuple)) and len(v) == 3:
            return [int(round(float(x))) for x in v]
        raise TreatmentError("%s: %r is not a colour" % (what, v))

    # -- layers ----------------------------------------------------------
    def expand(self, layers, what):
        """Motifs in, overrides applied: plain authored layer dicts out."""
        out = []
        for i, L in enumerate(layers or []):
            if not isinstance(L, dict):
                raise TreatmentError("%s layer %d is not an object" % (what, i))
            if "use" in L:
                name = L["use"]
                if name not in self.motifs:
                    raise TreatmentError("%s: no motif %s" % (what, name))
                mot = self.motifs[name]
                over = {k: v for k, v in L.items() if k != "use"}
                for m in (mot if isinstance(mot, list) else [mot]):
                    for sub in self.expand([m], what):
                        out.append(_merge(sub, over))
            else:
                out.append(dict(L))
        return out

    def layer(self, L, pal, what, span):
        fx = L.get("fx")
        if fx not in FX:
            raise TreatmentError("%s: no fx %r (have %s)" % (what, fx, ", ".join(FX)))
        known = set(COMMON) | set(FX_VALUES[fx]) | set(FX_STATIC[fx]) | {"fx"}
        extra = set(L) - known
        if extra:
            raise TreatmentError("%s: %s has no %s" % (what, fx, ", ".join(sorted(extra))))
        out = {"fx": fx}
        out["on"] = L.get("on") or DEFAULT_ON[fx]
        out["mix"] = L.get("mix", "add")
        out["pal"] = L.get("pal") or pal
        out["gain"] = self.value(L.get("gain", 1.0), what + " gain")
        out["c"] = self.value(L.get("c", 0.5), what + " c")
        g = L.get("gate")
        out["gate"] = self.gate(g, what) if g is not None else None
        env = L.get("env") or {}
        out["env"] = {"in": float(env.get("in", 0.0)), "out": float(env.get("out", 0.0))}
        for k, d in FX_VALUES[fx].items():
            out[k] = self.value(L.get(k, d), "%s %s" % (what, k))
        for k, d in FX_STATIC[fx].items():
            out[k] = L.get(k, d)
        if fx == "sparks":
            out["loop"] = int(out["loop"])
            out["seed"] = float(out["seed"])
        if fx == "blades":
            seq = out["seq"]
            if isinstance(seq, str):
                seq = [seq]
            comp = []
            for s in seq:
                if isinstance(s, list):
                    s = "".join(str(int(x)) for x in s)
                digits = sorted({int(ch) for ch in str(s)})
                if not digits or any(d not in (0, 1, 2) for d in digits):
                    raise TreatmentError("%s: blades step %r names a tube that "
                                         "is not 0, 1 or 2" % (what, s))
                comp.append(digits)
            out["seq"] = comp
        if fx == "preset":
            out = self.preset(L, out, what, span)
        return out

    def gate(self, g, what):
        if isinstance(g, str):
            g = {"pat": g}
        elif isinstance(g, list):
            g = dict(zip(("pat", "step", "decay", "floor"), g))
        pat = str(g.get("pat", "x"))
        if not pat or set(pat) - set("xo."):
            raise TreatmentError("%s: a gate pattern is x, o and . only, not %r"
                                 % (what, pat))
        return {"pat": pat, "step": float(g.get("step", 0.25)),
                "decay": float(g.get("decay", 0.5)),
                "floor": float(g.get("floor", 0.0))}

    def pump(self, p, what):
        if p is None or p is False:
            return None
        if isinstance(p, (int, float)) and not isinstance(p, bool):
            p = {"depth": p}
        elif isinstance(p, list):
            p = dict(zip(("pat", "step", "depth", "decay"), p))
        pat = str(p.get("pat", "x..."))
        if not pat or set(pat) - set("xo."):
            raise TreatmentError("%s: a pump pattern is x, o and . only" % what)
        return {"pat": pat, "step": float(p.get("step", 0.25)),
                "decay": float(p.get("decay", 0.5)),
                "depth": float(p.get("depth", 0.3))}

    def preset(self, L, out, what, span):
        name = L.get("name")
        if name not in PRESETS:
            raise TreatmentError("%s: preset layers are %s, not %r"
                                 % (what, ", ".join(PRESETS), name))
        params = dict(L.get("params") or {})
        for k in ("color", "bg"):
            if k in params:
                params[k] = self.colour(params[k], "%s %s" % (what, k))
        cls = E.REGISTRY[name]
        bad = set(params) - set(cls.params)
        if bad:
            raise TreatmentError("%s: %s has no parameter %s" % (what, name, sorted(bad)))
        tofs = 0.0
        if L.get("fit"):
            if name != "text":
                raise TreatmentError("%s: fit is for text" % what)
            # Enter on the right at the start, leave on the left at the
            # end, whatever the length of the word and of the moment.
            text = params.get("text", cls.params["text"])
            w = int(E._text_bitmap(text).shape[1])
            cell = float(params.get("cell", CELL))
            edge = _edge_mm(self.h) - CELL + cell
            span_s = float(span) * self.grid["spb"]
            speed = (w * cell + 2.0 * edge) / span_s
            params["speed"] = round(speed, 6)
            params["loop"] = False
            tofs = round(-edge / params["speed"], 6)
        out["name"] = name
        out["params"] = params
        out["tofs"] = tofs
        out.pop("fit", None)
        return out

    # -- scenes and hits -------------------------------------------------
    def compile(self):
        tr, nb = self.tr, self.bars
        for k, v in self.marks.items():
            if not 0 <= v <= nb:
                raise TreatmentError("mark %s at bar %g is outside the song (0..%d)"
                                     % (k, v, nb))
        first_pal = next(iter(self.pal))
        authored, scenes = {}, []
        for i, s in enumerate(tr.get("scenes") or []):
            name = s.get("name") or "scene %d" % i
            what = "scene %s" % name
            if "like" in s:
                if s["like"] not in authored:
                    raise TreatmentError("%s: like %r, which is not an earlier "
                                         "scene" % (what, s["like"]))
                base = authored[s["like"]]
                layers = copy.deepcopy(base["layers"])
                pump = copy.deepcopy(base.get("pump"))
                pal = base.get("pal")
            else:
                layers, pump, pal = [], None, None
            if "layers" in s:
                layers = copy.deepcopy(s["layers"])
            for k, v in (s.get("patch") or {}).items():
                j = int(k)
                if not 0 <= j < len(layers):
                    raise TreatmentError("%s: patch %d has no layer" % (what, j))
                layers[j] = _merge(layers[j], v)
            layers = layers + copy.deepcopy(s.get("add") or [])
            if "pump" in s:
                pump = s["pump"]
            pal = s.get("pal", pal)
            authored[name] = {"layers": layers, "pump": pump, "pal": pal}
            b0 = self.bar(s["from"], what + " from")
            b1 = self.bar(s["to"], what + " to")
            if not b1 > b0:
                raise TreatmentError("%s ends before it starts (%g..%g)" % (what, b0, b1))
            span = 4.0 * (b1 - b0)
            pal = pal or first_pal
            each = s.get("each") or {}
            comp = []
            for j, L in enumerate(self.expand(layers, what)):
                comp.append(self.layer(_merge(L, each), pal,
                                       "%s layer %d" % (what, j), span))
            scenes.append({"name": name, "from": b0, "to": b1,
                           "out": float(s.get("out", 0.0)),
                           "pump": self.pump(pump, what),
                           "layers": comp, "_pal": pal})
        scenes.sort(key=lambda s: s["from"])
        # Gaps are dark, said in so many words, so the scene list tiles
        # the song and the player never has to ask what is between.
        tiled, at = [], -1.0
        for s in scenes:
            if s["from"] < at - 1e-9:
                raise TreatmentError("scene %s starts at bar %g, inside the scene "
                                     "before it" % (s["name"], s["from"]))
            if s["from"] > at + 1e-9:
                tiled.append(_dark(at, s["from"]))
            tiled.append(s)
            at = s["to"]
        if at < nb - 1e-9:
            tiled.append(_dark(at, float(nb)))

        hits = []
        for i, hdef in enumerate(tr.get("hits") or []):
            name = hdef.get("name") or "hit %d" % i
            what = "hit %s" % name
            at = self.bar(hdef["at"], what + " at")
            beats = float(hdef.get("beats", 2))
            under = [s for s in tiled if s["from"] <= at < s["to"]]
            pal = (hdef.get("pal") or (under[0]["_pal"] if under else None)
                   or first_pal)
            comp = []
            for j, L in enumerate(self.expand(hdef.get("layers"), what)):
                comp.append(self.layer(L, pal, "%s layer %d" % (what, j), beats))
            hits.append({"name": name, "at": at, "beats": beats, "layers": comp})
        hits.sort(key=lambda x: x["at"])
        for s in tiled:
            s.pop("_pal", None)
        return {"v": 1, "src": "", "treatment": tr.get("_sha", ""),
                "grid": {"t0": self.grid["t0"], "spb": self.grid["spb"],
                         "lead": float(tr.get("lead", 0.0))},
                "bars": nb, "pal": self.pal, "scenes": tiled, "hits": hits}


def _merge(a, b):
    """A shallow merge, except that `env` and `params` merge one level down."""
    out = dict(a)
    for k, v in (b or {}).items():
        if k in ("env", "params") and isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = dict(out[k], **v)
        else:
            out[k] = v
    return out


def _dark(b0, b1):
    return {"name": "dark", "from": float(b0), "to": float(b1), "out": 0.0,
            "pump": None, "layers": [], "_pal": None}


def compile_treatment(tr, grid, bars, h=None, src=""):
    """A treatment, resolved against a grid, into the show's `scenes`.

    Pure: nothing here reads a file, so the synthetic test can hand it a
    made-up grid and the build can hand it the analysis it just made.
    """
    c = _Compiler(tr, grid, bars, h or _helmet())
    out = c.compile()
    out["src"] = src
    return out


def compile_for(base, music):
    """The treatment for `base`, compiled against this analysis."""
    return compile_treatment(load_treatment(base), *grid_of(music), src=src_of(base))


def _show_and_music(base):
    import mau5show
    path = os.path.join(SHOWS, base + ".json")
    with open(path) as f:
        show = json.load(f)
    music = mau5show._music_for(show, os.path.join(HERE, show.get("track", "")))
    if music is None:
        raise TreatmentError("%s has no analysis to compile against" % base)
    return show, music, path


def compile_show(base, verbose=False):
    """Load the show and its analysis, compile its treatment, and lint it."""
    show, music, _ = _show_and_music(base)
    spec = compile_for(base, music)
    errs, warns = lint(spec, _helmet(), music=music)
    if verbose:
        for w in warns:
            print("  warning: %s" % w)
    if errs:
        raise TreatmentError("%s does not pass:\n  %s" % (base, "\n  ".join(errs)))
    return spec


def attach(base, verbose=True):
    """Compile, lint, and write the result into shows/<base>.json."""
    show, music, path = _show_and_music(base)
    spec = compile_show(base, verbose=verbose)
    show["scenes"] = spec
    with open(path, "w") as f:
        json.dump(show, f, indent=1)
    if verbose:
        print("%s: %d scenes, %d hits, written into %s"
              % (base, len(spec["scenes"]), len(spec["hits"]),
                 os.path.relpath(path, HERE)))
    return spec


# ----------------------------------------------------------------------
# lint
# ----------------------------------------------------------------------
def _region_mask(h, on):
    m = np.zeros(h.n, bool)
    for nm in str(on).split("+"):
        nm = nm.strip()
        if nm == "all":
            m[:] = True
        elif nm in ("shell", "ears", "ear1", "ear2", "tubes", "rims"):
            m |= np.asarray(getattr(h, nm), bool)
        elif nm in ("tube0", "tube1", "tube2"):
            m |= np.asarray(h.tube) == int(nm[-1])
        elif nm == "left":
            m |= np.asarray(h.shell, bool) & (np.asarray(h.fa) < 0)
        elif nm == "right":
            m |= np.asarray(h.shell, bool) & (np.asarray(h.fa) >= 0)
        elif nm == "face":
            m |= np.asarray(h.shell, bool) & (np.asarray(h.py) > 28)
        else:
            raise TreatmentError("no region %r (have %s)" % (nm, ", ".join(REGIONS)))
    return m


def _min_gap_beats(pat, step):
    """The shortest cyclic distance between two sounding steps, in beats."""
    on = [i for i, ch in enumerate(pat) if ch != "."]
    if not on:
        return float("inf")
    L = len(pat)
    if len(on) == 1:
        return L * step
    gaps = [(on[(k + 1) % len(on)] - on[k]) % L or L for k in range(len(on))]
    return min(gaps) * step


def lint(spec, h=None, music=None):
    """(errors, warnings) for a compiled spec.  compile refuses on errors."""
    h = h or _helmet()
    errs, warns = [], []
    nb = spec["bars"]
    from mau5fx import SPRITES
    scenes, hits = spec["scenes"], spec["hits"]

    # tiling
    if not scenes or abs(scenes[0]["from"] + 1) > 1e-9 or abs(scenes[-1]["to"] - nb) > 1e-9:
        errs.append("the scenes must run from bar -1 to bar %d" % nb)
    for a, b in zip(scenes, scenes[1:]):
        if abs(a["to"] - b["from"]) > 1e-9:
            errs.append("scenes %s and %s do not meet" % (a["name"], b["name"]))

    if music is not None:
        g, n = grid_of(music)
        if (g["t0"] != spec["grid"]["t0"] or g["spb"] != spec["grid"]["spb"]
                or n != nb):
            errs.append("the compiled grid is not the analysis' grid")

    def layer_checks(L, what, span):
        if L["fx"] not in FX:
            errs.append("%s: no fx %s" % (what, L["fx"]))
        if L["mix"] not in MIX:
            errs.append("%s: no mix %s" % (what, L["mix"]))
        if L["pal"] not in spec["pal"]:
            errs.append("%s: no palette %s" % (what, L["pal"]))
        try:
            m = _region_mask(h, L["on"])
        except TreatmentError as e:
            errs.append("%s: %s" % (what, e))
            return
        if not m.any():
            errs.append("%s: region %s has no LEDs" % (what, L["on"]))
        shell = bool((m & h.shell).any())
        for k in ("axis", "axis2"):
            if k in L and L[k] not in AXES:
                errs.append("%s: no axis %s" % (what, L[k]))
        if L["fx"] == "grad" and L["wave"] not in WAVES:
            errs.append("%s: no wave %s" % (what, L["wave"]))
        if L["fx"] == "sweep":
            if L["shape"] not in SHAPES:
                errs.append("%s: no shape %s" % (what, L["shape"]))
            if L["mode"] not in MODES:
                errs.append("%s: no mode %s" % (what, L["mode"]))
        if L["fx"] == "sparks":
            r = L["rate"]
            if "n" not in r and "keys" not in r:
                errs.append("%s: a sparks rate is a number or keys, so the "
                            "sparks never jump" % what)
            rates = [r["n"]] if "n" in r else [v for _, v in r.get("keys", [])]
            lifes = ([L["life"]["n"]] if "n" in L["life"] else
                     [v for _, v in L["life"].get("keys", [])] or [1.0])
            if any(x <= 0 for x in rates):
                errs.append("%s: sparks rate must be above zero" % what)
            if max(rates or [0]) * max(lifes) > 8:
                warns.append("%s: life x rate = %.1f, above the 8 sparks drawn"
                             % (what, max(rates) * max(lifes)))
        if L["fx"] == "blades":
            if L["side"] not in SIDES:
                errs.append("%s: no side %s" % (what, L["side"]))
            st = L["step"]
            steps = [st["n"]] if "n" in st else (
                [v for _, v in st["keys"]] if "keys" in st else
                [st.get("ramp", [0, 0])[0], st.get("ramp", [0, 0])[1]]
                if "ramp" in st else [st.get("lo", 0), st.get("hi", 0)])
            if min(steps) < 0.25:
                errs.append("%s: blades step %.3g is faster than a 16th"
                            % (what, min(steps)))
        if L["fx"] == "preset":
            if L["name"] not in PRESETS:
                errs.append("%s: preset %s is not one of %s" % (what, L["name"], PRESETS))
            elif L["name"] == "sprite":
                sp = L["params"].get("sprite", E.REGISTRY["sprite"].params["sprite"])
                if sp not in SPRITES:
                    errs.append("%s: no sprite %s" % (what, sp))
        g = L.get("gate")
        if g and shell and span > 4.0 + 1e-9:
            gap = _min_gap_beats(g["pat"], g["step"])
            if gap < 0.5 - 1e-9:
                errs.append("%s: a gate on the shell flashing every %.3g beats -- "
                            "nothing on the shell turns on and off faster than "
                            "8th notes" % (what, gap))

    def texts(layers):
        return sum(1 for L in layers if L["fx"] == "preset" and L["name"] == "text")

    for s in scenes:
        what = "scene %s" % s["name"]
        span = 4.0 * (s["to"] - s["from"])
        if len(s["layers"]) > MAX_SCENE_LAYERS:
            errs.append("%s has %d layers, %d at most" % (what, len(s["layers"]),
                                                          MAX_SCENE_LAYERS))
        if s["out"] > 4.0 or s["out"] < 0 or s["out"] > span:
            errs.append("%s: out is %.3g beats, 4 at most" % (what, s["out"]))
        if s["pump"]:
            gap = _min_gap_beats(s["pump"]["pat"], s["pump"]["step"])
            if gap < 0.5 - 1e-9 and span > 4.0:
                errs.append("%s: the pump beats every %.3g beats, faster than "
                            "8th notes" % (what, gap))
        for j, L in enumerate(s["layers"]):
            layer_checks(L, "%s layer %d" % (what, j), span)
        if texts(s["layers"]) > 1:
            errs.append("%s: two text layers at once" % what)

    for x in hits:
        what = "hit %s" % x["name"]
        if len(x["layers"]) > MAX_HIT_LAYERS:
            errs.append("%s has %d layers, %d at most" % (what, len(x["layers"]),
                                                          MAX_HIT_LAYERS))
        if not 0 <= x["at"] <= nb:
            errs.append("%s at bar %g is outside the song" % (what, x["at"]))
        if x["beats"] <= 0:
            errs.append("%s lasts no time" % what)
        for j, L in enumerate(x["layers"]):
            layer_checks(L, "%s layer %d" % (what, j), x["beats"])
        # what overlaps it
        a0, a1 = 4.0 * x["at"], 4.0 * x["at"] + x["beats"]
        over = [y for y in hits if 4.0 * y["at"] < a1 and a0 < 4.0 * y["at"] + y["beats"]]
        # the most that are active at once: test at each start inside
        most = max(sum(1 for y in over if 4.0 * y["at"] <= q < 4.0 * y["at"] + y["beats"])
                   for q in [a0] + [4.0 * y["at"] for y in over if a0 <= 4.0 * y["at"] < a1])
        if most > MAX_HITS_AT_ONCE:
            errs.append("%s overlaps %d other hits" % (what, most - 1))
        t = texts(x["layers"])
        if t:
            others = sum(texts(y["layers"]) for y in over if y is not x)
            under = [s for s in scenes if 4.0 * s["from"] < a1 and a0 < 4.0 * s["to"]]
            others += max([texts(s["layers"]) for s in under] or [0])
            if t + others > 1:
                errs.append("%s: its text overlaps another text" % what)
    return errs, warns


# ----------------------------------------------------------------------
# the renderer
# ----------------------------------------------------------------------
def pal_lookup(stops, wrap, c):
    """One palette position -> RGB, as the JavaScript computes it."""
    n = len(stops)
    if wrap:
        x = (c % 1.0) * n
        i = math.floor(x)
        f = x - i
        i0 = i % n
        i1 = (i0 + 1) % n
    else:
        x = min(max(c, 0.0), 1.0) * (n - 1)
        i = min(math.floor(x), n - 2)
        f = x - i
        i0, i1 = i, i + 1
    s0, s1 = stops[i0], stops[i1]
    return np.array([s0[0] + (s1[0] - s0[0]) * f, s0[1] + (s1[1] - s0[1]) * f,
                     s0[2] + (s1[2] - s0[2]) * f])


def _pal_vec(P, c):
    stops, wrap, n = P
    if wrap:
        x = np.mod(c, 1.0) * n
        i = np.floor(x)
        f = x - i
        i0 = i.astype(int) % n
        i1 = (i0 + 1) % n
    else:
        x = np.clip(c, 0.0, 1.0) * (n - 1)
        i = np.minimum(np.floor(x), n - 2)
        f = x - i
        i0 = i.astype(int)
        i1 = i0 + 1
    s0, s1 = stops[i0], stops[i1]
    return s0 + (s1 - s0) * f[:, None]


def _hash_sin(x):
    return (math.sin(x) * 43758.5453) % 1.0


def _h32(h):
    """The helmet as the phone has it: every float through float32 once.

    bundle() ships the geometry as float32, so an axis read on the phone
    is the float32 nearest the laptop's.  Working from the same bytes
    here is what lets the two agree to the bit instead of to a count.
    """
    g = copy.copy(h)
    for k in ("px", "py", "nx", "ny", "nfa", "nel", "u", "fa", "ea", "er",
              "along", "depth", "xyz"):
        setattr(g, k, np.asarray(getattr(h, k)).astype("<f4").astype(float))
    return g


def _gate(lb, pat, step, decay, floor, HB):
    """A rhythm pattern as a gain: newest sounding step, held, then decaying."""
    L = len(pat)
    si = math.floor(lb / step)
    for k in range(L):
        ch = pat[(si - k) % L]
        if ch != ".":
            amp = 1.0 if ch == "x" else 0.5
            age = lb - (si - k) * step
            x = max(0.0, age - HB)
            e = max(0.0, 1.0 - x / decay)
            return floor + (1.0 - floor) * amp * e * e
    return floor


class _Val:
    __slots__ = ("kind", "a", "b", "bars", "vals", "band", "punch")

    def __init__(self, v):
        if "n" in v:
            self.kind, self.a = 0, float(v["n"])
        elif "ramp" in v:
            self.kind, self.a, self.b = 1, float(v["ramp"][0]), float(v["ramp"][1])
        elif "keys" in v:
            self.kind = 2
            self.bars = [float(k[0]) for k in v["keys"]]
            self.vals = [float(k[1]) for k in v["keys"]]
        elif "band" in v:
            self.kind, self.band = 3, str(v["band"])
            self.a, self.b, self.punch = float(v["lo"]), float(v["hi"]), bool(v["punch"])
        else:
            raise ValueError("not a value: %r" % (v,))

    def at(self, p, bar, music, tt):
        k = self.kind
        if k == 0:
            return self.a
        if k == 1:
            return self.a + (self.b - self.a) * p
        if k == 2:
            v = self.vals[0]
            for b, x in zip(self.bars, self.vals):
                if b <= bar:
                    v = x
                else:
                    break
            return v
        if music is not None and getattr(music, "analysed", False) is True:
            x = music.band_at(tt, self.band, punch=self.punch)
        else:
            x = 0.5
        return self.a + (self.b - self.a) * x


class Scenes:
    """Renders a compiled `scenes` spec.  frame(t) -> (out, gain, label).

    Everything that can be worked out once is worked out here -- region
    index lists, axis values, palettes, preset instances -- so a frame is
    only arithmetic.  remote/offline/show.js has the same class.
    """

    def __init__(self, spec, helmet):
        self.spec = spec
        g = spec["grid"]
        self.t0, self.spb = float(g["t0"]), float(g["spb"])
        self.lead = float(g.get("lead", 0.0))
        self.nbars = float(spec["bars"])
        self.HB = PULSE_HOLD_S / self.spb
        self.h = h = _h32(helmet)
        self.n = h.n
        self.pal = {k: (np.array(p["stops"], float), bool(p["wrap"]), len(p["stops"]))
                    for k, p in spec["pal"].items()}
        al = np.maximum(h.along, 0.0)
        self.axes = {"x": h.nfa, "y": h.nel, "r": h.er, "a": h.ea, "al": al, "u": h.u}
        self.al = al
        self.scenes = [self._scene(s) for s in spec["scenes"]]
        self.hits = [{"name": x["name"], "at": float(x["at"]), "beats": float(x["beats"]),
                      "layers": [self._layer(L) for L in x["layers"]]}
                     for x in spec["hits"]]
        self.acc = np.zeros((self.n, 3))

    def _scene(self, s):
        p = s.get("pump")
        return {"name": s["name"], "from": float(s["from"]), "to": float(s["to"]),
                "out": float(s["out"]),
                "pump": (p["pat"], float(p["step"]), float(p["decay"]), float(p["depth"]))
                if p else None,
                "layers": [self._layer(L) for L in s["layers"]]}

    def _layer(self, L):
        h = self.h
        fx = L["fx"]
        m = _region_mask(h, L["on"])
        idx = np.where(m)[0]
        g = L.get("gate")
        P = {"fx": fx, "mix": MIX.index(L["mix"]), "idx": idx,
             "pal": self.pal[L["pal"]],
             "gain": _Val(L["gain"]), "c": _Val(L["c"]),
             "gate": (g["pat"], float(g["step"]), float(g["decay"]), float(g["floor"]))
             if g else None,
             "ein": float(L["env"]["in"]), "eout": float(L["env"]["out"])}
        for k in FX_VALUES[fx]:
            P[k] = _Val(L[k])
        if fx == "grad":
            P["a"] = self.axes[L["axis"]][idx]
            P["a2"] = self.axes[L["axis2"]][idx]
            P["saw"] = L["wave"] == "saw"
        elif fx == "sweep":
            P["a"] = self.axes[L["axis"]][idx]
            P["shape"] = SHAPES.index(L["shape"])
            P["band"] = L["mode"] == "band"
        elif fx == "sparks":
            P["loop"], P["seed"] = int(L["loop"]), float(L["seed"])
            P["nm"] = len(idx)
        elif fx == "blades":
            tube = np.asarray(h.tube)
            P["tubes"] = [[idx[(tube[idx] == t) & ear[idx]] for t in range(3)]
                          for ear in (h.ear1, h.ear2)]
            P["rims"] = [idx[np.asarray(h.rims)[idx] & ear[idx]]
                         for ear in (h.ear1, h.ear2)]
            P["seq"] = [list(x) for x in L["seq"]]
            P["full"] = [sorted(x) == [0, 1, 2] for x in L["seq"]]
            P["side"] = SIDES.index(L["side"])
        elif fx == "preset":
            P["inst"] = E.make(L["name"], **{k: (tuple(v) if isinstance(v, list) else v)
                                             for k, v in L["params"].items()})
            P["tofs"] = float(L["tofs"])
        return P

    # -- one layer -------------------------------------------------------
    def _mix(self, P, idx, v):
        acc = self.acc
        mix = P["mix"]
        if mix == 0:
            acc[idx] += v
        elif mix == 1:
            acc[idx] = np.maximum(acc[idx], v)
        else:
            sel = v.max(1) > 4
            acc[idx[sel]] = v[sel]

    def _render(self, P, B, bar, lb, span, p, music, tt):
        if P["gate"] is not None:
            pat, step, decay, floor = P["gate"]
            gate = _gate(lb, pat, step, decay, floor, self.HB)
        else:
            gate = 1.0
        ein = min(max(lb / P["ein"], 0.0), 1.0) if P["ein"] > 0 else 1.0
        eout = min(max((span - lb) / P["eout"], 0.0), 1.0) if P["eout"] > 0 else 1.0
        G = P["gain"].at(p, bar, music, tt) * gate * ein * eout
        if G <= 0:
            return
        c0 = P["c"].at(p, bar, music, tt)
        fx, idx = P["fx"], P["idx"]
        val = lambda k: P[k].at(p, bar, music, tt)  # noqa: E731
        if fx == "fill":
            rgb = pal_lookup(*P["pal"][:2], c0)
            w = G * 1.0
            v = np.broadcast_to(w * rgb, (len(idx), 3))
            self._mix(P, idx, v)
        elif fx == "grad":
            scale, speed, ofs, warp = val("scale"), val("speed"), val("ofs"), val("warp")
            lo, hi = val("lo"), val("hi")
            x = P["a"] * scale + B * speed + ofs
            if warp != 0:
                wscale, wspeed = val("wscale"), val("wspeed")
                x = x + warp * np.sin(2 * math.pi * (P["a2"] * wscale + B * wspeed))
            f = np.mod(x, 1.0)
            wv = f if P["saw"] else 1 - np.abs(2 * f - 1)
            c = lo + (hi - lo) * wv
            rgb = _pal_vec(P["pal"], c)
            w = G * np.ones(len(idx))
            self._mix(P, idx, w[:, None] * rgb)
        elif fx == "sweep":
            speed = val("speed")
            if P["shape"] == 0:
                sh = p
            else:
                f = (lb * speed) % 1.0
                sh = f if P["shape"] == 1 else 1 - abs(2 * f - 1)
            a0, a1 = val("from"), val("to")
            pos = a0 + (a1 - a0) * sh
            d = P["a"] - pos
            if P["band"]:
                q = 1 - np.abs(d) / val("width")
                k = np.where(q > 0, q * q, 0.0)
            else:
                k = np.clip(0.5 - d / val("soft"), 0.0, 1.0)
            c = c0 + val("cgrad") * P["a"]
            rgb = _pal_vec(P["pal"], c)
            w = G * k
            self._mix(P, idx, w[:, None] * rgb)
        elif fx == "sparks":
            r = val("rate")
            if r <= 0:
                return
            life, spread, nbr = val("life"), val("spread"), val("nbr")
            nm, loop, seed = P["nm"], P["loop"], P["seed"]
            K = np.zeros(nm)
            C = np.zeros(nm)
            top = math.floor(B * r)
            nb = min(8, math.ceil(life * r))
            HB = self.HB
            for back in range(nb + 1):
                j = top - back
                age = B - j / r
                if not (0 <= age < life):
                    continue
                jj = j % loop if loop > 0 else j
                at = min(math.floor(_hash_sin(jj * 91.7 + seed) * nm), nm - 1)
                x = max(0.0, age - HB)
                e = 1 - x / life
                kk = e * e
                cc = c0 + spread * _hash_sin(jj * 12.9898 + seed)
                if kk > K[at]:
                    K[at], C[at] = kk, cc
                kn = kk * nbr
                for q in (at - 1, at + 1):
                    if 0 <= q < nm and kn > K[q]:
                        K[q], C[q] = kn, cc
            rgb = _pal_vec(P["pal"], C)
            w = G * K
            self._mix(P, idx, w[:, None] * rgb)
        elif fx == "blades":
            st = val("step")
            s = math.floor(lb / st)
            q = lb / st - s
            seq = P["seq"]
            i = s % len(seq)
            tubes, full = seq[i], P["full"][i]
            side = P["side"]
            e1 = side == 0 or side == 2 or (side == 1 and s % 2 == 0)
            e2 = side == 0 or side == 3 or (side == 1 and s % 2 != 0)
            rise, keep, ctip, rim = val("rise"), val("keep"), val("ctip"), val("rim")
            front = min(q / rise, 1)
            x = max(0.0, q * st - self.HB)
            e = max(0.0, 1 - x / st)
            lv = keep + (1 - keep) * e * e
            for ear, on in ((0, e1), (1, e2)):
                if not on:
                    continue
                for tb in tubes:
                    ii = P["tubes"][ear][tb]
                    if not len(ii):
                        continue
                    al = self.al[ii]
                    fk = np.clip((front - al) / 0.1 + 0.5, 0.0, 1.0)
                    k = fk * lv
                    c = c0 + (ctip - c0) * np.maximum(0.0, 1 - np.abs(front - al) / 0.15)
                    rgb = _pal_vec(P["pal"], c)
                    w = G * k
                    self._mix(P, ii, w[:, None] * rgb)
                if rim > 0 and full:
                    ii = P["rims"][ear]
                    if len(ii):
                        k = rim * lv
                        rgb = pal_lookup(*P["pal"][:2], c0)
                        w = G * k
                        self._mix(P, ii, np.broadcast_to(w * rgb, (len(ii), 3)))
        elif fx == "preset":
            tl = lb * self.spb + P["tofs"]
            sc = np.asarray(P["inst"].render(self.h, tl, None), float)
            self._mix(P, idx, G * sc[idx])

    # -- one frame -------------------------------------------------------
    def scene_at(self, bar):
        for s in self.scenes:
            if s["from"] <= bar < s["to"]:
                return s
        return None

    def frame(self, t, music=None):
        tt = t + self.lead
        B = (tt - self.t0) / self.spb
        bar = B / 4
        acc = self.acc
        acc[:] = 0.0
        if not (-1 <= bar < self.nbars):
            return np.zeros((self.n, 3)), 1.0, ""
        sc = self.scene_at(bar)
        if sc is None:
            return np.zeros((self.n, 3)), 1.0, ""
        lb = B - 4 * sc["from"]
        span = 4 * (sc["to"] - sc["from"])
        p = min(max(lb / span, 0.0), 1.0)
        for P in sc["layers"]:
            self._render(P, B, bar, lb, span, p, music, tt)
        # The beat of darkness before a drop.  Contrast is most of what
        # makes a hit land, and the dark beat also banks thermal room.
        if sc["out"] > 0 and lb >= span - sc["out"]:
            acc[:] = 0.0
        label = sc["name"]
        nh = 0
        for x in self.hits:
            hb = B - 4 * x["at"]
            if 0 <= hb < x["beats"]:
                hp = hb / x["beats"]
                for P in x["layers"]:
                    self._render(P, B, bar, hb, x["beats"], hp, music, tt)
                label += " · " + x["name"]
                nh += 1
                if nh == MAX_HITS_AT_ONCE:
                    break
        out = np.clip(acc, 0, 255)
        gain = 1.0
        if sc["pump"] is not None:
            pat, step, decay, depth = sc["pump"]
            gain = 1 - depth + depth * _gate(lb, pat, step, decay, 0.0, self.HB)
        return out, gain, label


# ----------------------------------------------------------------------
# what the bar map says, for writing marks against
# ----------------------------------------------------------------------
def bar_stats(music):
    """Per bar: energy, bass, bass punch peak, mid, high, high punch peak."""
    fps = music.fps
    e = np.clip(np.asarray(music.energy, float), 0, 1)
    edges = [int(float(t) * fps) for t in music.bars] + [int(music.duration * fps)]
    band = getattr(music, "band", None) or {}
    rows = []
    for i in range(len(music.bars)):
        a = min(max(edges[i], 0), len(e) - 1)
        b = min(max(edges[i + 1], a + 1), len(e))

        def mean(k, w):
            return float(np.mean(band[k][w][a:b])) if k in band else float("nan")

        def peak(k, w):
            return float(np.max(band[k][w][a:b])) if k in band else float("nan")
        rows.append({"bar": i, "t": float(music.bars[i]), "energy": float(e[a:b].mean()),
                     "bass": mean("bass", 0), "bassp": peak("bass", 1),
                     "mid": mean("mid", 0), "high": mean("high", 0),
                     "highp": peak("high", 1)})
    return rows


def _row(r):
    return ("  %4d  %7.2fs  energy %.2f  bass %.2f (punch %.2f)  mid %.2f  high %.2f"
            % (r["bar"], r["t"], r["energy"], r["bass"], r["bassp"], r["mid"], r["high"]))


def print_marks(base, music):
    tr = load_treatment(base)
    rows = bar_stats(music)
    c = _Compiler(tr, grid_of(music)[0], len(rows), _helmet())
    print("%s: marks against the bar map (bar-1, bar, bar+1)" % base)
    for k, v in sorted(c.marks.items(), key=lambda kv: kv[1]):
        print("  %-10s bar %g" % (k, v))
        for b in (int(math.floor(v)) - 1, int(math.floor(v)), int(math.floor(v)) + 1):
            if 0 <= b < len(rows):
                print("  " + _row(rows[b]))


# ----------------------------------------------------------------------
# check: the whole song through the power guard
# ----------------------------------------------------------------------
def check(base, fps=25.0, verbose=True):
    """Render a whole song through Scenes and a fresh guard, per scene.

    Peaks are allowed to go up; what must not happen is a loud run that
    fills the thermal bucket and leaves a later scene pinned at the
    sustained floor.  If one does, the fix is a lighter scene -- never a
    bigger burst_j, a ceiling or budget_ma.

    `heat` is how full the bucket got in the scene (the guard's
    full_pct): the allowance only starts to fall past 70%, and at 100%
    the scene is held to the sustained floor, which is flagged.
    """
    import mau5power
    show, music, _ = _show_and_music(base)
    spec = show.get("scenes")
    if not spec:
        raise TreatmentError("%s has no scenes compiled into it" % base)
    h = E.Helmet()
    sc = Scenes(spec, h)
    guard = mau5power.load(count=h.n)
    dur = float(show.get("duration", 0))
    n = int(dur * fps)
    per = {}
    order = []
    worst_ms = 0.0
    for i in range(n):
        t = i / fps
        t1 = time.perf_counter()
        out, gain, label = sc.frame(t, music)
        ms = (time.perf_counter() - t1) * 1000
        worst_ms = max(worst_ms, ms)
        _, rep = guard.apply(out, now=t, gain=gain)
        name = label.split(" · ")[0] or "(outside)"
        if name not in per:
            per[name] = {"ma": [], "heat": [], "allow": [], "ms": [], "t0": t}
            order.append(name)
        d = per[name]
        d["ma"].append(rep["sent_ma"])
        th = rep.get("thermal") or {}
        d["heat"].append(th.get("full_pct", 0.0))
        d["allow"].append(th.get("allowance_w", float("inf")))
        d["ms"].append(ms)
    th = guard.thermal
    floor_w = (max(th.sustained_w - th.standby_w, 0.0) if th is not None else 0.0)
    pinned = [nm for nm in order
              if th is not None and min(per[nm]["allow"]) <= floor_w * 1.05]
    if verbose:
        print("%s: %d frames at %g fps through the guard" % (base, n, fps))
        print("  %-12s %8s %8s %8s %8s %9s %7s"
              % ("scene", "from", "mean mA", "p95 mA", "heat", "allow W", "ms"))
        for name in order:
            d = per[name]
            print("  %-12s %7.1fs %8.0f %8.0f %7.1f%% %9.1f %7.2f%s"
                  % (name[:12], d["t0"], np.mean(d["ma"]), np.percentile(d["ma"], 95),
                     max(d["heat"]), min(d["allow"]), np.mean(d["ms"]),
                     "  <- at the sustained floor" if name in pinned else ""))
        print("  worst frame %.2f ms; %s" % (
            worst_ms, "no scene reaches the sustained floor" if not pinned
            else "lighten %s rather than raise any limit" % ", ".join(pinned)))
    return per


# ----------------------------------------------------------------------
def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter,
                                 epilog=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("bars", help="the bar map, to write marks against")
    b.add_argument("show"); b.add_argument("lo", nargs="?", type=int)
    b.add_argument("hi", nargs="?", type=int)
    c = sub.add_parser("compile", help="compile a treatment into its show")
    c.add_argument("show", nargs="*")
    k = sub.add_parser("check", help="power and cost, scene by scene")
    k.add_argument("show", nargs="*")
    k.add_argument("--fps", type=float, default=25.0)
    a = ap.parse_args(argv)

    def names(given):
        if given:
            return [os.path.splitext(os.path.basename(g))[0].replace(".scene", "")
                    for g in given]
        return sorted(f[:-len(".scene.json")] for f in os.listdir(SCENES)
                      if f.endswith(".scene.json"))

    if a.cmd == "bars":
        _, music, _ = _show_and_music(names([a.show])[0])
        rows = bar_stats(music)
        lo = a.lo if a.lo is not None else 0
        hi = a.hi if a.hi is not None else len(rows)
        for r in rows[lo:hi]:
            print(_row(r))
    elif a.cmd == "compile":
        for base in names(a.show):
            _, music, _ = _show_and_music(base)
            print_marks(base, music)
            attach(base)
    elif a.cmd == "check":
        for base in names(a.show):
            check(base, fps=a.fps)
    return 0


if __name__ == "__main__":
    sys.exit(main())
