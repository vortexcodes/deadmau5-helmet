#!/usr/bin/env python3
"""mau5drive -- the part of a track the helmet needs, small enough to carry.

A show offline was missing two things: a clock, and a drive.  The cue
list says which effect is on screen at 3:42; it does not say how loud
the track is there, where the beats are, or what the harmony is doing,
and without those a show runs at one brightness from end to end and
reads as pasted over the music.

On the laptop that comes from `mau5song`'s analysis, which is 250 to
670 kB a track and assumes numpy.  This writes the same information
in a form a phone can read off a controller with 900 kB of
filesystem: the envelopes resampled to 20 Hz and quantised to a byte,
the beat and bar grids as they are, and a chroma vector per bar.  All
five tracks come to about 230 kB gzipped.

Twenty hertz and eight bits are not a compromise anybody will see.
The curves are loudness envelopes with a 25 ms window behind them;
the fastest thing in them is a kick transient, which 50 ms resolves,
and the show multiplies the whole frame by them, where a step of
1/255 is below what a diffused LED can show.

    python3 mau5drive.py                     # build them all
    python3 mau5drive.py --upload --host X   # and put them on the helmet
"""

from __future__ import annotations

import argparse
import gzip
import json
import os
import struct

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SHOWS = os.path.join(HERE, "shows")
OUT = os.path.join(HERE, "data", "offline")

MAGIC = b"MAU5DRV1"
FPS = 20                      # samples per second in the written curves

# The curves a show asks for, in the order they are written.  `e` is
# the band's energy and `p` its punch -- how fast that energy just
# rose, which is what an overlay riding a band actually wants.
CURVES = ("energy", "b_bass_e", "b_bass_p", "b_mid_e", "b_mid_p",
          "b_high_e", "b_high_p")


def _resample(a, fps_in, n_out):
    a = np.asarray(a, float)
    if not len(a):
        return np.zeros(n_out, np.uint8)
    t = np.arange(n_out) / float(FPS)
    et = np.arange(len(a)) / float(fps_in)
    v = np.interp(t, et, a, left=float(a[0]), right=float(a[-1]))
    return np.clip(v * 255.0, 0, 255).astype(np.uint8)


def pack(npz_path):
    """One track's drive, as bytes.

    Each band is normalised against its own maximum before quantising.
    The high band carries a twentieth of the energy of the bass and
    would otherwise spend its whole life in the bottom two codes --
    the same reason `band_curves` normalises per band on the laptop.
    """
    z = np.load(npz_path, allow_pickle=True)
    fps_in = float(z["fps"])
    dur = float(z["duration"])
    n = max(1, int(dur * FPS))

    blobs = []
    for name in CURVES:
        if name == "energy":
            v = np.asarray(z["energy"], float)
        elif name in z:
            v = np.asarray(z[name], float)
            v = v / max(float(v.max()), 1e-9)
        else:
            v = np.zeros(1)
        blobs.append(_resample(v, fps_in, n))

    beats = np.asarray(z["beats"], np.float32)
    bars = np.asarray(z["bars"], np.float32)
    chroma = np.asarray(z["chroma"], float) if "chroma" in z else np.zeros((0, 12))
    if len(chroma):
        # per bar, normalised to its own peak so a byte spans the
        # profile rather than the track's overall loudness
        chroma = chroma / np.maximum(chroma.max(1, keepdims=True), 1e-9)
    ch = np.clip(chroma * 255.0, 0, 255).astype(np.uint8)
    if len(ch) != len(bars):                 # keep the two in step
        ch = np.zeros((len(bars), 12), np.uint8)

    head = MAGIC + struct.pack("<HIBIId", FPS, n, len(CURVES),
                               len(beats), len(bars), dur)
    names = b"".join(nm.encode().ljust(12, b"\0") for nm in CURVES)
    return (head + names + b"".join(b.tobytes() for b in blobs)
            + beats.astype("<f4").tobytes() + bars.astype("<f4").tobytes()
            + ch.tobytes())


def build(verbose=True):
    os.makedirs(OUT, exist_ok=True)
    made = {}
    for fn in sorted(os.listdir(SHOWS)):
        if not fn.endswith(".json"):
            continue
        with open(os.path.join(SHOWS, fn)) as f:
            show = json.load(f)
        cache = show.get("analysis")
        path = os.path.join(SHOWS, cache) if cache else None
        if not path or not os.path.exists(path):
            if verbose:
                print("  %-44s no analysis, skipped" % fn[:-5][:44])
            continue
        raw = pack(path)
        gz = gzip.compress(raw, 9)
        name = "d%d.bin" % (len(made) + 1)
        with open(os.path.join(OUT, name), "wb") as f:
            f.write(raw)
        with open(os.path.join(OUT, name + ".gz"), "wb") as f:
            f.write(gz)
        made[fn[:-5]] = {"file": name, "bytes": len(raw), "gz": len(gz)}
        if verbose:
            print("  %-44s -> %s  %6d raw  %6d gzipped"
                  % (fn[:-5][:44], name, len(raw), len(gz)))
    with open(os.path.join(OUT, "drive.json"), "w") as f:
        json.dump(made, f, indent=1)
    if verbose and made:
        print("\n  %d tracks, %.0f kB on the controller"
              % (len(made), sum(v["gz"] for v in made.values()) / 1024.0))
    return made


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--upload", action="store_true")
    ap.add_argument("--host", default=None)
    a = ap.parse_args(argv)
    made = build()
    if a.upload:
        import mau5offline
        import mau5wled
        try:
            w = mau5offline._find(a.host)
        except mau5wled.WLEDError as e:
            print(e)
            return 1
        for v in made.values():
            with open(os.path.join(OUT, v["file"] + ".gz"), "rb") as f:
                blob = f.read()
            mau5offline._upload(w, "/" + v["file"] + ".gz", blob,
                                "application/octet-stream")
            print("  uploaded %-8s %6d bytes" % (v["file"], len(blob)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
