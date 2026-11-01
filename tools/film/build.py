#!/usr/bin/env python3
"""build.py -- the website's five videos, finished.

The overview, song-data and live films come out of their own scripts with their
songs already in. This adds a song to the other two (mau5film and mau5lapse render
silent), brings all five to the same loudness, and copies them to a site checkout
with a poster frame each. The songs come from shows/ and stay out of this repo.

    python3 mau5film.py --out /tmp/localisation.mp4
    python3 mau5lapse.py --explain --out /tmp/calibration.mp4
    python3 tools/film/overview.py
    python3 tools/film/datafilm.py
    python3 tools/film/livefilm.py
    python3 tools/film/build.py --localisation /tmp/localisation.mp4 \\
        --calibration /tmp/calibration.mp4 --site ../vortexcodes.github.io
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import tempfile

import numpy as np

from common import OUT, Song, mux
from overview import clip
import score

TARGET_LUFS = -18.0

# song, the bar its kick comes in, and the second in the film that should land on.
# Localisation: Strobe's slow build until the second camera shows up, then the beat.
LOCALISATION = ("deadmau5 - Strobe", 125, 38.5)
# Calibration: already moving when the helmet starts drawing itself.
CALIBRATION = ("deadmau5 & Wolfgang Gartner - Animal Rights", 32, 5.0)

# site file, source, second to take the poster from
FILES = {
    "shows": (os.path.join(OUT, "overview.mp4"), 72),   # tools/film/overview.py, with the real songs
    "song-data": (os.path.join(OUT, "song_data.mp4"), 8),
    "live": (os.path.join(OUT, "live_analysis.mp4"), 45),
}


def duration(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                       capture_output=True, text=True, check=True)
    return float(r.stdout)


def with_music(video, spec, out, tmp):
    base, bar, at = spec
    dur = duration(video)
    start = max(Song(base).t_of_bar(bar) - at, 0.0)
    x = clip(base, start, start + dur)
    x = x * min(1.0, 0.89 / (abs(x).max() + 1e-9))
    for n, ramp in ((int(0.8 * score.SR), 1), (int(2.5 * score.SR), -1)):
        k = np.linspace(0, 1, n)[:, None]
        if ramp > 0:
            x[:n] *= k
        else:
            x[-n:] *= k[::-1]
    wav = os.path.join(tmp, os.path.basename(out) + ".wav")
    score.write_wav(wav, x)
    mux(video, wav, out)
    return out


def measured_lufs(path):
    m = re.search(r"I:\s+(-?[\d.]+) LUFS", score.loudness(path))
    return float(m.group(1))


def level(path, out):
    gain = TARGET_LUFS - measured_lufs(path)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", path, "-map", "0", "-c:v", "copy", "-af",
                    "volume=%.2fdB,alimiter=limit=0.84:level=false" % gain, "-c:a", "aac", "-b:a", "160k",
                    "-movflags", "+faststart", out], check=True)
    return gain


def poster(path, sec, out):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(sec), "-i", path, "-frames:v", "1", "-q:v", "3", out],
                   check=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--localisation", required=True, help="silent render from mau5film.py")
    ap.add_argument("--calibration", required=True, help="silent render from mau5lapse.py --explain")
    ap.add_argument("--site", required=True, help="a checkout of the website")
    a = ap.parse_args()
    tmp = tempfile.mkdtemp(prefix="mau5build")
    sources = dict(FILES)
    sources["localisation"] = (with_music(a.localisation, LOCALISATION, os.path.join(tmp, "loc.mp4"), tmp), 45)
    sources["calibration"] = (with_music(a.calibration, CALIBRATION, os.path.join(tmp, "cal.mp4"), tmp), 30)
    for name, (src, sec) in sources.items():
        out = os.path.join(a.site, "media", "mau5head-v2-%s.mp4" % name)
        g = level(src, out)
        short = "data" if name == "song-data" else name
        poster(out, sec, os.path.join(a.site, "media", "work", "mau5head-v2-poster-%s.jpg" % short))
        print("%-13s %6.1f s  %5.1f MB  gain %+.1f dB  %s" % (name, duration(out), os.path.getsize(out) / 1e6, g,
                                                             score.loudness(out)[:90]))


if __name__ == "__main__":
    main()
