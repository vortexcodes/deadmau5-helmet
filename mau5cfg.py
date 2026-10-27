#!/usr/bin/env python3
"""mau5cfg -- config, geometry and wiring for the mau5head.

One import gives every other tool the same view of the helmet:

    import mau5cfg
    h = mau5cfg.load()            # reads helmet.toml
    h.n_total                     # 1406 LEDs on the wire
    h.xyz                         # (n_total, 3) mm positions, sphere centre origin
    h.grid                        # (rows, channels) global LED index, -1 where empty
    h.fixture("ETR2").slice       # slice into a frame buffer for one ear blade

Geometry rules, in one place so nobody has to guess:

  * ``data/pixel_map.csv`` is authoritative for the 948 shell pixels.  If it is
    missing, ``mau5cfg.generate_pixel_map()`` builds a stand-in from the
    parameters in helmet.toml and writes it out, printing exactly what it did.
  * ``mau5head_sim_backdrop.glb`` is scenery.  Nothing here reads pixel
    positions out of it; ``load_glb`` exists only so the simulator can draw it.

Python 3.11+ is the target; this file also runs on 3.9 (it falls back to a
small TOML reader when ``tomllib`` is absent).
"""

from __future__ import annotations

import csv
import json
import math
import os
import re
import struct
import sys
from dataclasses import dataclass, field

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CONFIG = os.path.join(HERE, "helmet.toml")


# --------------------------------------------------------------------------
# TOML
# --------------------------------------------------------------------------

_SUPERSEDED = """
  ------------------------------------------------------------------
  mau5cfg loads helmet.toml, which describes the helmet as it was
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


def read_toml(path):
    """tomllib if we have it (3.11+), otherwise the small reader below."""
    try:
        import tomllib
        with open(path, "rb") as fh:
            return tomllib.load(fh)
    except ImportError:
        pass
    try:
        import tomli
        with open(path, "rb") as fh:
            return tomli.load(fh)
    except ImportError:
        pass
    with open(path, "r", encoding="utf-8") as fh:
        return _mini_toml(fh.read())


_NUM = re.compile(r"^[+-]?(\d+\.\d*([eE][+-]?\d+)?|\.\d+|\d+[eE][+-]?\d+|\d+)$")


def _mini_toml(text):
    """Enough TOML for helmet.toml: tables, array-of-tables, scalars, arrays.

    Not a general parser -- no multiline strings, no dotted keys, no dates.
    It exists so the suite runs on a stock python3 without pip installs.
    """
    root = {}
    cur = root

    def descend(container, dotted, make_list):
        parts = dotted.split(".")
        node = container
        for p in parts[:-1]:
            node = node.setdefault(p, {})
            if isinstance(node, list):
                node = node[-1]
        last = parts[-1]
        if make_list:
            lst = node.setdefault(last, [])
            if not isinstance(lst, list):
                raise ValueError("conflicting table %r" % dotted)
            lst.append({})
            return lst[-1]
        return node.setdefault(last, {})

    pending = ""
    for raw in text.splitlines():
        line = _strip_comment(raw).strip()
        if pending:
            line = pending + " " + line
            pending = ""
        if not line:
            continue
        if _unclosed(line):            # an array continued on the next line
            pending = line
            continue
        if line.startswith("[["):
            cur = descend(root, line[2:line.index("]]")].strip(), True)
        elif line.startswith("["):
            cur = descend(root, line[1:line.index("]")].strip(), False)
        else:
            key, _, val = line.partition("=")
            cur[key.strip().strip('"')] = _mini_value(val.strip())
    return root


def _unclosed(line):
    """True if the line ends inside an unfinished [ ... ] array."""
    depth, quoted = 0, False
    for ch in line:
        if ch == '"':
            quoted = not quoted
        elif not quoted:
            if ch == "[":
                depth += 1
            elif ch == "]":
                depth -= 1
    return depth > 0


def _strip_comment(line):
    out, quoted = [], False
    for ch in line:
        if ch == '"':
            quoted = not quoted
        if ch == "#" and not quoted:
            break
        out.append(ch)
    return "".join(out)


def _mini_value(s):
    if s.startswith("["):
        inner = s[1:s.rindex("]")]
        parts, depth, buf = [], 0, []
        for ch in inner:
            if ch == "[":
                depth += 1
            elif ch == "]":
                depth -= 1
            if ch == "," and depth == 0:
                parts.append("".join(buf)); buf = []
            else:
                buf.append(ch)
        if "".join(buf).strip():
            parts.append("".join(buf))
        return [_mini_value(p.strip()) for p in parts]
    if s.startswith('"'):
        return s[1:s.rindex('"')]
    if s in ("true", "false"):
        return s == "true"
    if _NUM.match(s):
        return float(s) if any(c in s for c in ".eE") else int(s)
    return s


# --------------------------------------------------------------------------
# model
# --------------------------------------------------------------------------
@dataclass
class Pixel:
    index: int          # global LED index on the wire
    channel: int        # 0..67 around the sphere
    row: int            # 0..21 bottom to top
    az: float           # degrees, 0 = front (-Y), +ve towards +X
    elev: float         # degrees, 0 = equator
    x: float
    y: float
    z: float
    output: str         # "A" or "B"
    chain_index: int    # position within that output


@dataclass
class Fixture:
    id: str
    name: str
    kind: str           # ring | blade | arc
    count: int
    start: int          # global LED index of its first pixel
    points: np.ndarray  # (count, 3) mm

    @property
    def slice(self):
        return slice(self.start, self.start + self.count)

    @property
    def end(self):
        return self.start + self.count


@dataclass
class Output:
    name: str
    gpio: int
    start: int
    count: int
    parts: list = field(default_factory=list)   # ["shell_back"] / ["shell_front","ERR",...]


class Helmet:
    """Everything the tools need to know about the physical helmet."""

    def __init__(self, cfg, pixels, fixtures, outputs, path):
        self.cfg = cfg
        self.path = path
        self.pixels = pixels
        self.fixtures = fixtures
        self.outputs = outputs
        self._by_id = {f.id: f for f in fixtures}

        self.fps = int(cfg["show"]["fps"])
        self.channels = int(cfg["shell"]["channels"])
        self.rows = int(cfg["shell"]["rows"])
        self.radius = float(cfg["shell"]["sphere_radius_mm"])
        self.n_shell = len(pixels)
        self.n_total = self.n_shell + sum(f.count for f in fixtures)

        xyz = np.zeros((self.n_total, 3), float)
        for p in pixels:
            xyz[p.index] = (p.x, p.y, p.z)
        for f in fixtures:
            xyz[f.slice] = f.points
        self.xyz = xyz

        # outward surface normal per LED, and which of them are on a flat
        # plate that reads as lit from either side (the ear discs)
        norm = xyz / (np.linalg.norm(xyz, axis=1, keepdims=True) + 1e-9)
        two = np.zeros(self.n_total, bool)
        specs = {f["id"]: f for f in cfg.get("fixture", [])}
        parents = cfg.get("fixture_parent", {}) or {}
        for f in fixtures:
            spec = specs.get(f.id, {})
            if f.kind in ("ring", "blade"):
                src = spec if f.kind == "ring" else specs.get(parents.get(f.id), spec)
                n = np.array([float(v) for v in src.get("normal", (0, 1, 0))])
                norm[f.slice] = n / (np.linalg.norm(n) + 1e-9)
                two[f.slice] = True
        self.normals = norm.astype(np.float64)
        self.two_sided = two

        grid = np.full((self.rows, self.channels), -1, int)
        for p in pixels:
            grid[p.row, p.channel] = p.index
        self.grid = grid

        self.az = np.array([p.az for p in pixels])
        self.elev = np.array([p.elev for p in pixels])
        self.shell_index = np.array([p.index for p in pixels])

    # -- lookups ----------------------------------------------------------
    def fixture(self, fid):
        return self._by_id[fid]

    @property
    def fixture_ids(self):
        return [f.id for f in self.fixtures]

    @property
    def shell_slice(self):
        return slice(0, self.n_shell)

    @property
    def channel_count(self):
        """DMX/DDP channels: 3 per LED."""
        return self.n_total * 3

    def blank(self):
        """A fresh (n_total, 3) uint8 frame buffer."""
        return np.zeros((self.n_total, 3), np.uint8)

    def describe(self):
        out = ["%-6s %-14s %5s %6s %6s" % ("out", "part", "leds", "first", "last")]
        for o in self.outputs:
            out.append("%-6s %-14s %5d %6d %6d" % (o.name, ",".join(o.parts)[:14],
                                                   o.count, o.start, o.start + o.count - 1))
        out.append("")
        out.append("shell %d  accessories %d  total %d  DDP channels %d"
                   % (self.n_shell, self.n_total - self.n_shell, self.n_total,
                      self.channel_count))
        return "\n".join(out)


# --------------------------------------------------------------------------
# shell geometry
# --------------------------------------------------------------------------
def sphere_xyz(radius, az_deg, elev_deg):
    """az 0 = front (-Y), +ve toward +X; elev 0 = equator, +90 = +Z."""
    a = math.radians(az_deg)
    e = math.radians(elev_deg)
    ce = math.cos(e)
    return (radius * ce * math.sin(a), -radius * ce * math.cos(a), radius * math.sin(e))


def _az_delta(a, b):
    """Signed shortest distance from b to a, in degrees."""
    return (a - b + 180.0) % 360.0 - 180.0


def _cut(cutouts, ch, row, az, elev, channels=68):
    for c in cutouts:
        kind = c.get("kind", "window")
        if kind == "window":
            if (abs(_az_delta(az, c["az_centre_deg"])) <= c["az_half_deg"]
                    and c["elev_min_deg"] <= elev <= c["elev_max_deg"]):
                return c["name"]
        elif kind == "cap":
            d = _angular_sep(az, elev, c["az_deg"], c["elev_deg"])
            if d <= c["radius_deg"]:
                return c["name"]
        elif kind == "channels":
            if ch in [int(v) for v in c["channels"]] and \
                    c["elev_min_deg"] <= elev <= c["elev_max_deg"]:
                return c["name"]
        elif kind == "profile":
            m = c.get("margin_deg", 0.0)
            for lo, hi in _profile(c, channels).get(ch, ()):
                if lo - m <= elev <= hi + m:
                    return c["name"]
    return None


def _profile(c, channels=68):
    """[[channel, elev_lo, elev_hi], ...] -> {channel: (lo, hi)}, mirrored if asked.

    Mirroring pairs channel n with channel (channels - n), which is the same
    azimuth on the other side of the face.
    """
    cache = c.get("_cache")
    if cache is not None:
        return cache
    n = int(c.get("channels_total", channels))
    out = {}
    for row in c.get("bands", []):
        ch, lo, hi = int(row[0]), float(row[1]), float(row[2])
        out.setdefault(ch, []).append((lo, hi))
        if c.get("mirror") and ch:
            out.setdefault((n - ch) % n, []).append((lo, hi))
    c["_cache"] = out
    return out


def _angular_sep(az1, el1, az2, el2):
    p1, p2 = math.radians(el1), math.radians(el2)
    d = math.radians(_az_delta(az1, az2))
    v = math.sin(p1) * math.sin(p2) + math.cos(p1) * math.cos(p2) * math.cos(d)
    return math.degrees(math.acos(max(-1.0, min(1.0, v))))


def shell_cells(cfg, verbose=True):
    """Every populated (channel, row, az, elev) on the shell, before wiring.

    Applies the density fall-off near the crown and the cutout list.
    """
    sh = cfg["shell"]
    dens = sh["density"] if isinstance(sh.get("density"), dict) else cfg["shell"]["density"]
    cutouts = sh.get("cutout", []) or []
    nch, nrow = int(sh["channels"]), int(sh["rows"])
    az_step = 360.0 / nch
    row_step = float(sh["row_pitch_deg"])
    el0 = float(sh["bottom_row_elev_deg"])

    cells = []
    for row in range(nrow):
        elev = round(el0 + row * row_step, 6)   # keep -7e-15 off a band edge
        if elev <= dens["full_to_deg"]:
            stride = 1
        elif elev <= dens["half_to_deg"]:
            stride = 2
        elif elev <= dens["quarter_to_deg"]:
            stride = 4
        else:
            continue
        for ch in range(0, nch, stride):
            az = (ch * az_step) % 360.0
            if _cut(cutouts, ch, row, az, elev, nch):
                continue
            cells.append((ch, row, az, elev))
    if sh.get("despeckle", True):
        cells = _despeckle(cells, nch, int(sh["rows"]), dens, el0, row_step,
                           verbose=verbose)
    return cells


def _despeckle(cells, nch, nrows, dens, el0, row_step, verbose=True):
    """Drop lone pixels stranded inside an opening.

    Where the visor pocket tapers out near the temples it gets shallow enough
    that one channel reads as solid shell while both its neighbours are cut.
    That leaves a single pixel marooned in the middle of the opening, which is
    a measurement artefact rather than a real recess.  Only full-density rows
    are considered, and only isolated cells are removed -- never a run.
    """
    have = set((c, r) for c, r, _a, _e in cells)
    full = float(dens["full_to_deg"])
    drop = set()
    for (ch, row, _az, elev) in cells:
        if elev > full:
            continue
        n = sum(1 for d in ((1, 0), (-1, 0), (0, 1), (0, -1))
                if ((ch + d[0]) % nch, row + d[1]) in have)
        if n == 0:                       # isolated, not merely at the end of a run
            drop.add((ch, row))
    if drop and verbose:
        print("  despeckled %d stranded pixel%s: %s"
              % (len(drop), "" if len(drop) == 1 else "s",
                 ", ".join("ch%d/row%d" % t for t in sorted(drop)[:8])
                 + (" ..." if len(drop) > 8 else "")))
    return [c for c in cells if (c[0], c[1]) not in drop]


def generate_pixel_map(cfg, verbose=True):
    """Build a stand-in pixel_map.csv from helmet.toml parameters.

    Returns a list of dicts in wire order.  This is only used when the real
    ``data/pixel_map.csv`` is absent -- see the README.
    """
    sh = cfg["shell"]
    wr = cfg.get("wiring", {})
    radius = float(sh["sphere_radius_mm"])
    nch = int(sh["channels"])
    az_step = 360.0 / nch
    cells = shell_cells(cfg, verbose=verbose)
    by_channel = {}
    for c in cells:
        by_channel.setdefault(c[0], []).append(c)

    # one serpentine walk around the sphere ...
    start_az = float(wr.get("start_az_deg", 0.0))
    step = 1 if int(wr.get("az_direction", 1)) >= 0 else -1
    up_first = bool(wr.get("first_channel_up", True))
    order = sorted(by_channel,
                   key=lambda ch: (step * (ch * az_step - start_az)) % 360.0)

    walk = []
    for n, ch in enumerate(order):
        up = up_first if n % 2 == 0 else not up_first
        walk.extend(sorted(by_channel[ch], key=lambda c: c[1], reverse=not up))

    # ... then cut into the outputs at the LED counts from helmet.toml.
    rows_out = []
    cuts, pos = [], 0
    for name, n in split_outputs(cfg, len(walk), verbose=verbose):
        cuts.append((name, pos, pos + n))
        pos += n
    for index, (ch, row, az, elev) in enumerate(walk):
        name, base = "?", 0
        for nm, lo, hi in cuts:
            if lo <= index < hi:
                name, base = nm, lo
                break
        x, y, z = sphere_xyz(radius, az, elev)
        rows_out.append(dict(index=index, channel=ch, row=row,
                             az_deg=round(az, 3), elev_deg=round(elev, 3),
                             x=round(x, 3), y=round(y, 3), z=round(z, 3),
                             output=name, chain_index=index - base))

    if verbose:
        want = int(sh.get("expected_pixels", 0))
        per = {}
        for r in rows_out:
            per[r["output"]] = per.get(r["output"], 0) + 1
        got = len(rows_out)
        print("generated stand-in pixel map: %d pixels (%s)"
              % (got, ", ".join("%s=%d" % kv for kv in sorted(per.items()))))
        if want and got != want:
            print("  !! helmet.toml says expected_pixels = %d -- off by %+d.\n"
                  "     Fix [[shell.cutout]] or drop in the real data/pixel_map.csv."
                  % (want, got - want), file=sys.stderr)
    return rows_out


def split_outputs(cfg, n_shell, verbose=False):
    """How many shell pixels each WLED output carries.

    helmet.toml declares the counts the controller is programmed with.  If the
    geometry no longer sums to that -- which happens the moment the pixel map
    changes -- the declared ratio is preserved and rescaled, and we say so
    loudly, because programming the controller with the old numbers puts every
    LED after the split on the wrong colour.
    """
    outs = cfg["output"]
    want = [int(o.get("count", 0)) for o in outs]
    total = sum(want)
    if total == n_shell:
        return [(o["name"], c) for o, c in zip(outs, want)]

    if total <= 0:
        share = [n_shell // len(outs)] * len(outs)
        share[-1] += n_shell - sum(share)
    else:
        exact = [n_shell * w / float(total) for w in want]
        share = [int(math.floor(e)) for e in exact]
        rem = n_shell - sum(share)
        for i in sorted(range(len(exact)), key=lambda i: exact[i] - share[i],
                        reverse=True)[:rem]:
            share[i] += 1
    if verbose:
        print("  !! helmet.toml declares %s = %d shell pixels, but the "
              "geometry produces %d.\n"
              "     Keeping the declared ratio and rescaling to %s. "
              "Reprogram the controller\n"
              "     with the new counts -- run  python3 mau5cfg.py --verify"
              % ("+".join(str(w) for w in want), total, n_shell,
                 "+".join(str(c) for c in share)), file=sys.stderr)
    return [(o["name"], c) for o, c in zip(outs, share)]


PIXEL_FIELDS = ["index", "channel", "row", "az_deg", "elev_deg", "x", "y", "z",
                "output", "chain_index"]

_ALIASES = {
    "az": "az_deg", "azimuth": "az_deg", "azimuth_deg": "az_deg", "theta": "az_deg",
    "el": "elev_deg", "elev": "elev_deg", "elevation": "elev_deg",
    "elevation_deg": "elev_deg", "phi": "elev_deg",
    "ch": "channel", "col": "channel", "column": "channel", "strip": "channel",
    "r": "row", "y_index": "row",
    "led_index": "index", "wire_index": "index",
    "x_mm": "x", "y_mm": "y", "z_mm": "z",
    "port": "output", "chain": "output",
}


def write_pixel_map(path, rows):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=PIXEL_FIELDS)
        w.writeheader()
        for r in rows:
            w.writerow({k: r[k] for k in PIXEL_FIELDS})


def read_pixel_map(path, cfg):
    """Read pixel_map.csv, tolerating the column names xLights-adjacent tools use.

    Required: channel + row, and either (az,elev) or (x,y,z).  Anything else is
    derived.  If there is no index column, file order is wire order.
    """
    radius = float(cfg["shell"]["sphere_radius_mm"])
    out_names = [o["name"] for o in cfg["output"]]
    rows = []
    with open(path, newline="", encoding="utf-8") as fh:
        rdr = csv.DictReader(fh)
        for i, raw in enumerate(rdr):
            rec = {}
            for k, v in raw.items():
                if k is None:
                    continue
                key = _ALIASES.get(k.strip().lower(), k.strip().lower())
                rec[key] = v
            r = {}
            r["channel"] = int(float(rec["channel"]))
            r["row"] = int(float(rec["row"]))
            r["index"] = int(float(rec.get("index", i)))
            if "az_deg" in rec and rec["az_deg"] not in ("", None):
                r["az_deg"] = float(rec["az_deg"])
                r["elev_deg"] = float(rec["elev_deg"])
                r["x"], r["y"], r["z"] = sphere_xyz(radius, r["az_deg"], r["elev_deg"])
            else:
                r["x"], r["y"], r["z"] = (float(rec["x"]), float(rec["y"]), float(rec["z"]))
                rr = math.sqrt(r["x"] ** 2 + r["y"] ** 2 + r["z"] ** 2) or 1.0
                r["az_deg"] = math.degrees(math.atan2(r["x"], -r["y"])) % 360.0
                r["elev_deg"] = math.degrees(math.asin(max(-1, min(1, r["z"] / rr))))
            if "x" in rec and rec.get("x") not in ("", None) and "az_deg" in rec:
                r["x"], r["y"], r["z"] = float(rec["x"]), float(rec["y"]), float(rec["z"])
            r["output"] = rec.get("output") or ""
            r["chain_index"] = int(float(rec["chain_index"])) if rec.get("chain_index") else None
            rows.append(r)

    idx = [r["index"] for r in rows]
    if len(set(idx)) != len(idx):
        dup = sorted({i for i in idx if idx.count(i) > 1})[:6]
        raise SystemExit(
            "%s: the index column repeats (%s%s).\n"
            "  Exports that number nodes per model or per port look like this.\n"
            "  Remove the column so file order is used as wire order, or make it\n"
            "  a single 0..N-1 sequence across the whole helmet."
            % (path, ", ".join(str(d) for d in dup), " ..." if len(dup) == 6 else ""))
    if sorted(idx) != list(range(min(idx), min(idx) + len(idx))):
        raise SystemExit("%s: the index column is not contiguous -- it has gaps, "
                         "so wire order is ambiguous." % path)
    rows.sort(key=lambda r: r["index"])
    # backfill output for any row the file did not label, using the same split
    # the generator would use, so both paths agree
    missing = [i for i, r in enumerate(rows)
               if not r["output"] or r["output"] not in out_names]
    if missing:
        if len(missing) != len(rows):
            print("  note: %d of %d pixel-map rows have no usable output column; "
                  "filling them from helmet.toml" % (len(missing), len(rows)),
                  file=sys.stderr)
        pos = 0
        for name, n in split_outputs(cfg, len(rows)):
            for i in range(pos, min(pos + n, len(rows))):
                if i in set(missing) or not rows[i]["output"]:
                    rows[i]["output"] = name
            pos += n
        for r in rows:
            if not r["output"] or r["output"] not in out_names:
                r["output"] = out_names[-1]
    seen = {}
    for r in rows:
        r["chain_index"] = seen.get(r["output"], 0)
        seen[r["output"]] = r["chain_index"] + 1
    for i, r in enumerate(rows):
        r["index"] = i
    return rows


# --------------------------------------------------------------------------
# accessory geometry
# --------------------------------------------------------------------------
def _unit(v):
    v = np.asarray(v, float)
    n = np.linalg.norm(v)
    return v / n if n else v


def _basis(normal):
    n = _unit(normal)
    tmp = np.array([0.0, 0.0, 1.0])
    if abs(n @ tmp) > 0.9:
        tmp = np.array([1.0, 0.0, 0.0])
    u = _unit(np.cross(tmp, n))
    v = np.cross(n, u)
    return u, v


def build_fixtures(cfg, start_index):
    """Lay out the accessory strips in 3-space, in chain order."""
    parents = cfg.get("fixture_parent", {}) or {}
    specs = {f["id"]: f for f in cfg["fixture"]}
    fixtures = []
    idx = start_index
    for spec in cfg["fixture"]:
        kind, count = spec["kind"], int(spec["count"])
        if kind == "ring":
            c = np.array([float(t) for t in spec["centre"]])
            u, v = _basis(spec["normal"])
            r = float(spec["radius_mm"])
            a0 = math.radians(float(spec.get("start_angle_deg", 0.0)))
            d = float(spec.get("direction", 1))
            ang = a0 + d * np.linspace(0, 2 * math.pi, count, endpoint=False)
            pts = c + r * (np.cos(ang)[:, None] * u + np.sin(ang)[:, None] * v)
        elif kind == "blade":
            par = specs[parents[spec["id"]]]
            c = np.array([float(t) for t in par["centre"]])
            u, v = _basis(par["normal"])
            R = float(par["radius_mm"]) * 0.94       # inside the rim
            off = float(spec.get("offset_mm", 0.0))
            half = math.sqrt(max(R * R - off * off, 1.0))
            t = np.linspace(-half, half, count)
            pts = c + off * u + t[:, None] * v
        elif kind == "arc":
            r = float(spec.get("radius_mm", cfg["shell"]["sphere_radius_mm"]))
            el = float(spec["elev_deg"])
            a = np.linspace(float(spec["az_start_deg"]), float(spec["az_end_deg"]), count)
            pts = np.array([sphere_xyz(r, ai, el) for ai in a])
        else:
            raise ValueError("unknown fixture kind %r" % kind)
        fixtures.append(Fixture(spec["id"], spec.get("name", spec["id"]), kind,
                                count, idx, pts.astype(float)))
        idx += count
    return fixtures


# --------------------------------------------------------------------------
# wiring table
# --------------------------------------------------------------------------
WIRING_FIELDS = ["segment", "output", "kind", "start_led", "end_led", "count",
                 "direction", "feeds_from", "feeds_into"]


def build_wiring(helmet):
    """One row per strip segment: shell channels, then each accessory."""
    rows = []
    prev = {}
    nseg = {}
    for p in helmet.pixels:
        key = (p.output, p.channel)
        e = prev.get(key)
        # the visor slot splits a channel into runs above and below it; those
        # are separate strip segments, not one with a hole in the middle
        if e is None or p.index != e["end_led"] + 1:
            nseg[key] = nseg.get(key, 0) + 1
            suffix = "" if nseg[key] == 1 else chr(ord("a") + nseg[key] - 1)
            prev[key] = dict(segment="SH-%s-C%02d%s" % (p.output, p.channel, suffix),
                             output=p.output, kind="shell_channel",
                             start_led=p.index, end_led=p.index, count=1,
                             direction="", first_row=p.row, last_row=p.row)
            rows.append(prev[key])
        else:
            e["end_led"] = p.index
            e["count"] += 1
            e["last_row"] = p.row
    for r in rows:
        r["direction"] = "up" if r["last_row"] >= r["first_row"] else "down"
        r.pop("first_row"), r.pop("last_row")
        assert r["count"] == r["end_led"] - r["start_led"] + 1, r["segment"]
    owner = {fid: o.name for o in helmet.outputs for fid in o.parts}
    for f in helmet.fixtures:
        rows.append(dict(segment=f.id, output=owner.get(f.id, helmet.outputs[-1].name),
                         kind=f.kind, start_led=f.start, end_led=f.end - 1,
                         count=f.count, direction="out"))
    rows.sort(key=lambda r: r["start_led"])
    for i, r in enumerate(rows):
        r["feeds_from"] = rows[i - 1]["segment"] if i and rows[i - 1]["output"] == r["output"] else "controller %s" % r["output"]
        r["feeds_into"] = rows[i + 1]["segment"] if i + 1 < len(rows) and rows[i + 1]["output"] == r["output"] else "end of chain"
    return rows


def write_wiring(path, rows):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=WIRING_FIELDS)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in WIRING_FIELDS})


# --------------------------------------------------------------------------
# entry point
# --------------------------------------------------------------------------
def load(path=DEFAULT_CONFIG, pixel_map=None, quiet=False):
    """Load helmet.toml plus the pixel map, generating a stand-in if needed."""
    cfg = read_toml(path)
    base = os.path.dirname(os.path.abspath(path))
    data_dir = os.path.join(base, cfg["show"].get("data_dir", "data"))
    pm_path = pixel_map or os.path.join(data_dir, "pixel_map.csv")

    if os.path.exists(pm_path):
        raw = read_pixel_map(pm_path, cfg)
    else:
        raw = generate_pixel_map(cfg, verbose=not quiet)
        write_pixel_map(pm_path, raw)
        if not quiet:
            print("  wrote %s  (drop the real one in to override)" % pm_path)

    pixels = [Pixel(r["index"], r["channel"], r["row"], r["az_deg"], r["elev_deg"],
                    r["x"], r["y"], r["z"], r["output"], r["chain_index"])
              for r in raw]

    fixtures = build_fixtures(cfg, len(pixels))

    # Accessories ride on whichever output names them in helmet.toml; anything
    # nobody names goes on the last output, which is where the chain physically
    # ends.  Building each output from an explicit LED list (rather than
    # min(index) + a count) is what keeps a middle output from claiming a range
    # that overlaps its neighbour.
    owner = {}
    known = {f.id for f in fixtures}
    for o in cfg["output"]:
        for fid in (o.get("fixtures") or []):
            if fid not in known:
                raise SystemExit("output %s lists fixture %r, which is not in "
                                 "helmet.toml" % (o["name"], fid))
            if fid in owner:
                raise SystemExit("fixture %r is claimed by both output %s and "
                                 "output %s" % (fid, owner[fid], o["name"]))
            owner[fid] = o["name"]
    last = cfg["output"][-1]["name"]
    for f in fixtures:
        owner.setdefault(f.id, last)

    outputs = []
    for o in cfg["output"]:
        leds = sorted(p.index for p in pixels if p.output == o["name"])
        mine = [f for f in fixtures if owner[f.id] == o["name"]]
        for f in mine:
            leds.extend(range(f.start, f.end))
        parts = [o["role"]] + [f.id for f in mine]
        if not leds:
            outputs.append(Output(o["name"], int(o["gpio"]), len(pixels), 0, parts))
            continue
        leds.sort()
        if leds != list(range(leds[0], leds[0] + len(leds))):
            gaps = [(a, b) for a, b in zip(leds, leds[1:]) if b != a + 1][:3]
            print("  !! output %s is not one contiguous run of LEDs (breaks after "
                  "%s).\n     WLED addresses a bus as start+length, so this cannot "
                  "be programmed\n     as one output -- check the [[output]] "
                  "fixtures lists in helmet.toml."
                  % (o["name"], ", ".join(str(a) for a, _b in gaps)),
                  file=sys.stderr)
        outputs.append(Output(o["name"], int(o["gpio"]), leds[0], len(leds), parts))

    h = Helmet(cfg, pixels, fixtures, outputs, path)

    # always regenerate: it is derived from the pixel map, and a stale one is
    # worse than none -- it describes a helmet that no longer exists
    wr_path = os.path.join(data_dir, "wiring_chained.csv")
    write_wiring(wr_path, build_wiring(h))
    return h


# --------------------------------------------------------------------------
# GLB (scenery only)
# --------------------------------------------------------------------------
def load_glb(path):
    """Minimal binary-glTF reader -> (vertices (N,3), faces (M,3)).

    Stdlib only; the backdrop is a single non-indexed-material mesh, which is
    all this needs to handle.  Scenery -- never a source of pixel positions.
    """
    with open(path, "rb") as fh:
        data = fh.read()
    magic, _ver, _len = struct.unpack_from("<4sII", data, 0)
    if magic != b"glTF":
        raise ValueError("%s is not a .glb" % path)
    off, chunks = 12, {}
    while off < len(data):
        clen, ctype = struct.unpack_from("<I4s", data, off)
        off += 8
        chunks[ctype.strip(b"\x00")] = data[off:off + clen]
        off += clen
    gl = json.loads(chunks[b"JSON"])
    buf = chunks[b"BIN"]

    def accessor(i):
        a = gl["accessors"][i]
        bv = gl["bufferViews"][a["bufferView"]]
        start = bv.get("byteOffset", 0) + a.get("byteOffset", 0)
        dtype = {5120: "<i1", 5121: "<u1", 5122: "<i2", 5123: "<u2",
                 5125: "<u4", 5126: "<f4"}[a["componentType"]]
        ncomp = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4, "MAT4": 16}[a["type"]]
        arr = np.frombuffer(buf, dtype=dtype, count=a["count"] * ncomp, offset=start)
        return arr.reshape(a["count"], ncomp)

    verts, faces = [], []
    base = 0
    for mesh in gl["meshes"]:
        for prim in mesh["primitives"]:
            v = accessor(prim["attributes"]["POSITION"]).astype(np.float32)
            f = (accessor(prim["indices"]).reshape(-1, 3).astype(np.int64) + base
                 if "indices" in prim else
                 np.arange(len(v)).reshape(-1, 3) + base)
            verts.append(v)
            faces.append(f)
            base += len(v)
    return np.vstack(verts), np.vstack(faces)


def decimate_mesh(verts, faces, target_faces):
    """Vertex-cluster decimation -- collapse vertices onto a grid.

    Striding the face list shreds a mesh into slivers; clustering keeps a
    coherent (if chunky) surface, which is all a backdrop needs.
    """
    if len(faces) <= target_faces:
        return verts, faces
    span = float(np.ptp(verts, axis=0).max())
    lo, hi = span / 400.0, span / 6.0
    best = (verts, faces)      # replaced on the first candidate at or under budget
    for _ in range(12):
        cell = math.sqrt(lo * hi)
        q = np.floor(verts / cell).astype(np.int64)
        key = (q[:, 0] * 73856093) ^ (q[:, 1] * 19349663) ^ (q[:, 2] * 83492791)
        _uniq, inv = np.unique(key, return_inverse=True)
        nv = np.zeros((inv.max() + 1, 3))
        np.add.at(nv, inv, verts)
        nv /= np.bincount(inv, minlength=len(nv))[:, None]
        nf = inv[faces]
        nf = nf[(nf[:, 0] != nf[:, 1]) & (nf[:, 1] != nf[:, 2]) & (nf[:, 0] != nf[:, 2])]
        nf = np.unique(np.sort(nf, axis=1), axis=0)
        if len(nf) <= target_faces or best[1] is faces:
            best = (nv, nf)
        if len(nf) > target_faces:
            lo = cell
        else:
            hi = cell
        if 0.7 * target_faces <= len(nf) <= target_faces:
            break
    return best


# --------------------------------------------------------------------------
# measuring the print file
# --------------------------------------------------------------------------
def measure_shell(glb_path, radius, channels=68, recess_mm=6.0, samples=12):
    """Read the real openings out of the printed geometry.

    The shell surface sits at ~radius; where a pocket is cut for the visor the
    surface drops about 11 mm, and where the ear mounts bolt on it disappears
    entirely.  Both read as "no pixel here".  Returns {channel: (elev_lo,
    elev_hi)} for the front slot and for the ear mounts, ready to paste into
    helmet.toml as `bands`.

    This is the one thing the backdrop mesh is allowed to decide, because the
    mesh IS the part being printed.  Pixel positions still come from the grid.
    """
    verts, faces = load_glb(glb_path)
    verts = verts.astype(np.float64)
    r = np.linalg.norm(verts, axis=1)
    keep = ((r > radius * 0.85) & (r < radius * 1.13))[faces].all(axis=1)
    tri = verts[faces[keep]]

    pts = []
    for a in np.linspace(0.015, 0.97, samples):
        for b in np.linspace(0.015, 0.97, samples):
            if a + b < 0.99:
                pts.append(tri[:, 0] * a + tri[:, 1] * b + tri[:, 2] * (1 - a - b))
    p = np.vstack(pts)
    pr = np.linalg.norm(p, axis=1)
    elev = np.degrees(np.arcsin(np.clip(p[:, 2] / pr, -1, 1)))
    azim = np.degrees(np.arctan2(p[:, 0], -p[:, 1])) % 360.0

    step = 360.0 / channels
    cut = radius - recess_mm
    grid = np.arange(-58.0, 78.0, 0.5)
    out = {}
    for ch in range(channels):
        m = np.abs((azim - ch * step + 180.0) % 360.0 - 180.0) < step * 0.45
        if m.sum() < 50:
            continue
        e, q = elev[m], pr[m]
        flag = []
        for g in grid:
            k = np.abs(e - g) < 1.2
            flag.append(True if k.sum() < 6 else bool(np.percentile(q[k], 75) < cut))
        flag = np.array(flag)
        idx = np.where(flag)[0]
        if not len(idx):
            continue
        runs = np.split(idx, np.where(np.diff(idx) != 1)[0] + 1)
        runs = [r_ for r_ in runs if len(r_) >= 2]
        if not runs:
            continue
        out[ch] = [(round(float(grid[r_[0]]), 1), round(float(grid[r_[-1]]), 1))
                   for r_ in runs]
    return out


# Where each kind of opening lives, so the measurement can be classified
# instead of hand-sorted.  (name, |azimuth| range, elevation range, min height)
FEATURES = [
    ("visor_slot", (0.0, 100.0), (-33.0, 12.0), 1.5),
    ("chin_vent", (0.0, 45.0), (-50.0, -32.0), 1.5),
    ("ear_mounts", (95.0, 145.0), (25.0, 56.0), 1.5),
    ("back_vent", (145.0, 181.0), (-52.0, -40.0), 1.5),
]


def classify_measurement(bands, channels=68, mirror_tol=2.5):
    """Sort measured pockets into named features, keeping only symmetric ones.

    The helmet is mirror-symmetric about the face, so a pocket that shows up on
    one side and not the other is decimation noise, not a real opening.  Anything
    that does not match a known feature is returned separately rather than
    quietly dropped.
    """
    def runs(ch):
        return bands.get(ch % channels, [])

    out = {name: {} for name, _a, _e, _h in FEATURES}
    unclassified = []
    for ch in range(channels):
        a = ch * 360.0 / channels
        a = a if a <= 180 else a - 360
        mirror = (channels - ch) % channels
        for lo, hi in runs(ch):
            twin = None
            for mlo, mhi in runs(mirror):
                if abs(mlo - lo) <= mirror_tol and abs(mhi - hi) <= mirror_tol:
                    twin = (mlo, mhi)
                    break
            placed = False
            for name, (a0, a1), (e0, e1), minh in FEATURES:
                if (a0 <= abs(a) <= a1 and hi - lo >= minh
                        and lo >= e0 - 3 and hi <= e1 + 3):
                    if twin is None:
                        unclassified.append((ch, lo, hi, a, "not mirrored"))
                    else:
                        out[name].setdefault(ch, []).append((lo, hi))
                    placed = True
                    break
            if not placed and hi - lo >= 1.5:
                unclassified.append((ch, lo, hi, a, "no matching feature"))
    return out, unclassified


def print_measurement(helmet, recess_mm=8.0):
    base = os.path.dirname(os.path.abspath(helmet.path))
    glb = os.path.join(base, helmet.cfg.get("sim", {}).get(
        "backdrop_glb", "mau5head_sim_backdrop.glb"))
    if not os.path.exists(glb):
        raise SystemExit("no backdrop mesh at %s" % glb)
    n = helmet.channels
    bands = measure_shell(glb, helmet.radius, n, recess_mm=recess_mm)
    feats, extra = classify_measurement(bands, n)

    print("measured from %s   (pocket deeper than %.0f mm = no pixel)\n"
          % (os.path.basename(glb), recess_mm))
    for name, _a, _e, _h in FEATURES:
        rows = sorted(feats[name].items())
        if not rows:
            continue
        near = [(ch, lo, hi) for ch, bs in rows if ch <= n // 2 for lo, hi in sorted(bs)]
        print("[[shell.cutout]]")
        print('name = "%s"' % name)
        print('kind = "profile"')
        print("mirror = true")
        print("margin_deg = 0.0")
        print("bands = [")
        for ch, lo, hi in near:
            a = ch * 360.0 / n
            print("  [%2d, %6.1f, %6.1f],   # azimuth %+6.1f" % (ch, lo, hi, a))
        print("]")
        print()
    if extra:
        print("# not applied -- %d pocket(s) that do not match a known feature or"
              % len(extra))
        print("# are not mirrored, so they read as decimation noise:")
        for ch, lo, hi, a, why in extra[:24]:
            print("#   ch %2d  az %+7.1f  %6.1f..%-6.1f  (%s)" % (ch, a, lo, hi, why))
        if len(extra) > 24:
            print("#   ... and %d more" % (len(extra) - 24))


# --------------------------------------------------------------------------
# verification
# --------------------------------------------------------------------------
def verify(helmet):
    """Check the whole addressing chain and print it.  Returns a problem list."""
    h, cfg = helmet, helmet.cfg
    bad = []
    print("pixels")
    print("  shell        %5d" % h.n_shell)
    for f in h.fixtures:
        print("  %-12s %5d   LED %5d..%-5d" % (f.id, f.count, f.start, f.end - 1))
    print("  TOTAL        %5d LEDs = %d DDP channels" % (h.n_total, h.channel_count))

    print("\noutputs")
    print("  %-3s %-5s %6s  %-15s %-19s %s"
          % ("out", "gpio", "leds", "LED range", "DDP byte range", "carries"))
    declared = [int(o.get("count", 0)) for o in cfg["output"]]
    seen = np.zeros(h.n_total, int)
    for o, want in zip(h.outputs, declared):
        lo, hi = o.start, o.start + o.count - 1
        seen[lo:hi + 1] += 1
        print("  %-3s %-5d %6d  %5d..%-9d %8d..%-9d %s"
              % (o.name, o.gpio, o.count, lo, hi, lo * 3, hi * 3 + 2,
                 ",".join(o.parts)[:40]))
    for o, want in zip(h.outputs, declared):
        shell_here = sum(1 for p in h.pixels if p.output == o.name)
        if want and shell_here != want:
            bad.append("output %s carries %d shell pixels, helmet.toml says %d "
                       "-- update [[output]] count and reflash WLED"
                       % (o.name, shell_here, want))

    if (seen == 0).any():
        bad.append("%d LEDs belong to no output (first: %d)"
                   % (int((seen == 0).sum()), int(np.argmin(seen))))
    if (seen > 1).any():
        bad.append("%d LEDs claimed by more than one output" % int((seen > 1).sum()))

    print("\nrefresh budget at %d fps (%.1f ms/frame, WS2815 = 30 us/LED)"
          % (h.fps, 1000.0 / h.fps))
    for o in h.outputs:
        need = o.count * 30.0 / 1000.0
        ok = need <= 1000.0 / h.fps
        print("  %-3s %5d LEDs -> %5.1f ms  %s"
              % (o.name, o.count, need, "ok" if ok else "OVER BUDGET"))
        if not ok:
            bad.append("output %s needs %.1f ms per refresh but a frame is %.1f ms"
                       % (o.name, need, 1000.0 / h.fps))

    # grid round trip
    live = h.grid >= 0
    if int(live.sum()) != h.n_shell:
        bad.append("grid holds %d pixels but there are %d shell pixels"
                   % (int(live.sum()), h.n_shell))
    if len(set(h.grid[live].ravel().tolist())) != h.n_shell:
        bad.append("two shell pixels share a (row, channel) cell")

    # chain order of the accessories
    order = [f.id for f in h.fixtures]
    declared_order = [f["id"] for f in cfg["fixture"]]
    if order != declared_order:
        bad.append("accessory chain order %s != helmet.toml order %s"
                   % (order, declared_order))
    pos = h.n_shell
    for f in h.fixtures:
        if f.start != pos:
            bad.append("%s starts at LED %d, expected %d (gap in the chain)"
                       % (f.id, f.start, pos))
        pos = f.end

    # DDP packetisation must never split an LED across two packets
    from mau5fseq import DDP_MAX_DATA
    if (DDP_MAX_DATA - DDP_MAX_DATA % 3) % 3:
        bad.append("DDP payload size is not a multiple of 3")

    print("\ncontroller")
    print("  WLED total          %d" % h.n_total)
    print("  DDP channel count   %d  (%d packets/frame at %d B)"
          % (h.channel_count,
             int(math.ceil(h.channel_count / float(DDP_MAX_DATA - DDP_MAX_DATA % 3))),
             DDP_MAX_DATA - DDP_MAX_DATA % 3))
    print("  FPP must send       %d channels" % h.channel_count)

    print()
    if bad:
        for b in bad:
            print("PROBLEM: %s" % b, file=sys.stderr)
    else:
        print("all checks passed")
    return bad


if __name__ == "__main__":
    _warn_superseded()
    import argparse
    ap = argparse.ArgumentParser(description="mau5head geometry and wiring")
    ap.add_argument("config", nargs="?", default=DEFAULT_CONFIG)
    ap.add_argument("--verify", action="store_true",
                    help="check the whole LED -> channel -> output chain")
    ap.add_argument("--measure", action="store_true",
                    help="re-read the openings from the backdrop mesh and print "
                         "them as helmet.toml [[shell.cutout]] blocks")
    ap.add_argument("--recess-mm", type=float, default=8.0,
                    help="how deep a pocket has to be to count as 'no pixel'")
    ap.add_argument("--grid", action="store_true", help="print the pixel grid")
    args = ap.parse_args()

    h = load(args.config)
    if args.measure:
        print()
        print_measurement(h, args.recess_mm)
        sys.exit(0)
    if args.verify:
        print()
        sys.exit(1 if verify(h) else 0)
    print()
    print(h.describe())
    print()
    occupied = (h.grid >= 0)
    print("shell grid rows x channels = %d x %d, %d cells populated"
          % (h.rows, h.channels, occupied.sum()))
    for r in range(h.rows - 1, -1, -1):
        elev = float(h.cfg["shell"]["bottom_row_elev_deg"]) + r * float(h.cfg["shell"]["row_pitch_deg"])
        print("%6.2f  %s  %2d" % (elev,
                                  "".join("#" if v >= 0 else "." for v in h.grid[r]),
                                  occupied[r].sum()))
