#!/usr/bin/env python3
"""build.py -- the website's five videos, finished.

The overview, song-data and live films come out of their own scripts with their
music already in. This writes music for the other two (mau5film and mau5lapse render
silent), brings all five to the same loudness, and copies them to a site checkout
with a poster frame each.

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

from common import OUT, mux
import score

TARGET_LUFS = -18.0

# start seconds, then bass, mid and high. Follows the film's scenes: no beat until the
# second camera shows up, most going on while the chain fills in and in the before/after.
LOCALISATION = dict(bpm=122, root=45, prog="drift", sections=[
    (0, 0, .35, .1), (9, 0, .45, .2), (15.5, 0, .5, .3), (29.5, 0, .55, .2), (38.5, .6, .5, .3),
    (46.5, .85, .7, .6), (62.5, .7, .55, .4), (69.5, 0, .45, .3), (79.5, .9, .8, .7), (91.5, 0, .3, 0)])
CALIBRATION = dict(bpm=126, root=47, prog="lift", sections=[
    (0, 0, .35, .1), (5, .7, .5, .35), (15, 0, .5, .3), (18, .85, .7, .55), (40.5, 0, .3, 0)])

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


def with_music(video, spec, out, tmp, seed):
    x = score.free(duration(video), spec["bpm"], spec["sections"], root=spec["root"], prog=spec["prog"], seed=seed)
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
    sources["localisation"] = (with_music(a.localisation, LOCALISATION, os.path.join(tmp, "loc.mp4"), tmp, 31), 45)
    sources["calibration"] = (with_music(a.calibration, CALIBRATION, os.path.join(tmp, "cal.mp4"), tmp, 41), 30)
    for name, (src, sec) in sources.items():
        out = os.path.join(a.site, "media", "mau5head-v2-%s.mp4" % name)
        g = level(src, out)
        short = "data" if name == "song-data" else name
        poster(out, sec, os.path.join(a.site, "media", "work", "mau5head-v2-poster-%s.jpg" % short))
        print("%-13s %6.1f s  %5.1f MB  gain %+.1f dB  %s" % (name, duration(out), os.path.getsize(out) / 1e6, g,
                                                             score.loudness(out)[:90]))


if __name__ == "__main__":
    main()
