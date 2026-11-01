#!/usr/bin/env python3
"""livefilm.py -- the live analyser working something out as a track plays.

The track is one of ours from score.py. Its spectra get computed the way the Web
Audio spec says an AnalyserNode does it, then live_trace.js feeds them to the real
audio.js and engine.js. So the numbers on screen, the BPM included, and the helmet
are what the page would give on this track, and any wrong guesses are its own.

    python3 tools/film/livefilm.py             # data/cal/live_analysis.mp4
"""

from __future__ import annotations

import json
import os
import subprocess
import tempfile

import numpy as np

from common import E, F, FPS, H, HERE, HelmetView, OUT, Image, ImageDraw, W, encoder, send, strip
import mau5offline
import score

BPM = 124.0
SECONDS = 62.0
TICK = 0.02
FAST, SLOW = 1024, 8192
X0, PANEL_W = 530, W - 530
TOP = H - F.FOOT
SPAN = 8.0       # seconds of history on screen
AMBER, TEAL, ICE = (222, 170, 90), (70, 190, 170), (120, 170, 255)
TEXT, DIM, BG = (232, 235, 238), (130, 138, 146), (17, 20, 24)

SECTIONS = [(0, 0, .42, .12), (10, .85, .52, .42), (30, 0, .62, .3), (40, .95, .85, .75), (58, 0, .35, .05)]

PRESETS = [{"at": 0, "name": "spectrum"}, {"at": 22, "name": "bloom"}, {"at": 40, "name": "spectrum"}]

ROWS = {"spec": (8, 118), "level": (132, 82), "bands": (220, 134), "flux": (360, 142), "bpm": (508, 112)}

CAPTIONS = [
    (0, "spec", "No analysis file here",
     "This is what the page gets for a song it has never seen: the last 23 ms of sound, 50 times a second."),
    (10, "bands", "The same three bands as a show, worked out on the spot",
     "It can't scale them against the whole song because it hasn't heard the whole song, only what has played so far."),
    (17, "level", "Loudness with no reference",
     "It keeps a running quiet mark and loud mark, and places the current reading between them. Works at any volume."),
    (24, "flux", "A beat is a jump well above the recent average",
     "The spectrum's rise has to clear the mean plus 1.4 standard deviations of the last 5 seconds, 0.16 s after the last one."),
    (30, "flux", "When the kick stops, this gets less sure",
     "Pads and plucks still trip it sometimes. Beat position just free-runs from whatever it last called a beat."),
    (40, "bpm", "The tempo is the median gap between beats",
     "It reads 125 on this 124 track because it only looks every 20 ms, so the gaps it measures come in steps."),
    (50, "bpm", "What it doesn't know",
     "Where bar 1 is, or what's coming. There's no delay correction either. That's why the song shows get measured beforehand."),
]


def analyser_data(x):
    """What the two AnalyserNodes would hand back at each 20 ms tick, per the Web Audio
    spec: Blackman window, |FFT|/N, smoothed with the previous tick, then dB."""
    mono = x.mean(axis=1)
    sr = score.SR
    ticks = int(len(mono) / sr / TICK)
    w_f, w_s = _blackman(FAST), _blackman(SLOW)
    db = np.zeros((ticks, FAST // 2), np.float32)
    sb = np.zeros((ticks, SLOW // 2), np.float32)
    tb = np.zeros((ticks, FAST), np.float32)
    pf = np.zeros(FAST // 2)
    ps = np.zeros(SLOW // 2)
    for k in range(ticks):
        i = int(k * TICK * sr)
        seg = _last(mono, i, FAST)
        m = np.abs(np.fft.rfft(seg * w_f))[:FAST // 2] / FAST
        pf = 0.3 * pf + 0.7 * m
        with np.errstate(divide="ignore"):
            db[k] = 20 * np.log10(pf)
        seg = _last(mono, i, SLOW)
        m = np.abs(np.fft.rfft(seg * w_s))[:SLOW // 2] / SLOW
        ps = 0.5 * ps + 0.5 * m
        with np.errstate(divide="ignore"):
            d = 20 * np.log10(ps)
        sb[k] = np.clip(np.floor(255 / 70.0 * (d + 100)), 0, 255)
        tb[k] = np.clip(np.floor(128 * (_last(mono, i, FAST) + 1)), 0, 255)
    return db, sb, tb, ticks


def _blackman(n):
    a = np.arange(n) / n
    return 0.42 - 0.5 * np.cos(2 * np.pi * a) + 0.08 * np.cos(4 * np.pi * a)


def _last(a, i, n):
    if i >= n:
        return a[i - n:i]
    return np.r_[np.zeros(n - i), a[:i]]


def run_trace(x, tmp):
    db, sb, tb, ticks = analyser_data(x)
    paths = {k: os.path.join(tmp, k + ".f32") for k in ("fast_db", "slow_byte", "time_byte")}
    db.tofile(paths["fast_db"])
    sb.tofile(paths["slow_byte"])
    tb.tofile(paths["time_byte"])
    job = dict(paths, data=mau5offline.bundle(), sr=score.SR, ticks=ticks, fast_bins=FAST // 2, slow_bins=SLOW // 2,
               time_len=FAST, fps=FPS, presets=PRESETS, frames_out=os.path.join(tmp, "frames.f32"),
               trace_out=os.path.join(tmp, "trace.json"))
    jp = os.path.join(tmp, "job.json")
    json.dump(job, open(jp, "w"))
    r = subprocess.run(["node", os.path.join(HERE, "live_trace.js"), jp], capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(r.stderr)
    print(r.stdout.strip())
    return db, json.load(open(job["trace_out"])), np.fromfile(job["frames_out"], np.float32)


def scroll_line(d, x0, y, w, h, ts, vs, now, color, width=1):
    xs = x0 + w - (now - ts) / SPAN * w
    keep = xs >= x0
    pts = [(float(a), y + h - float(np.clip(v, 0, 1)) * h) for a, v in zip(xs[keep], vs[keep])]
    if len(pts) > 1:
        d.line(pts, fill=color, width=width)


def main():
    # less sustained bass than the other videos, so the bands have room to move
    x = score.free(SECONDS, BPM, SECTIONS, root=43, prog="night", seed=21, bass=0.35)
    tmp = tempfile.mkdtemp(prefix="mau5live")
    wav = os.path.join(tmp, "a.wav")
    score.write_wav(wav, x)
    print(score.loudness(wav))
    db, tr, frames = run_trace(x, tmp)
    h = E.Helmet()
    frames = frames.reshape(-1, h.n, 3)
    M = F.Model()
    view = HelmetView((0, 0, 520, TOP), M, h)
    A = {k: np.array([r[k] for r in tr], float) for k in
         ("t", "level", "rawDb", "lo", "hi", "flux", "thr", "bpm", "pitch", "phase")}
    onset = np.array([r["onset"] for r in tr], bool)
    bands = {k: np.array([r["b"][k] for r in tr], float) for k in ("bass", "mid", "high")}
    punch = {k: np.array([r["p"][k] for r in tr], float) for k in ("bass", "mid", "high")}
    print("onsets by section:", [(s[0], int(onset[(A["t"] >= s[0])].sum())) for s in SECTIONS])
    print("bpm over time:", [(t, round(float(A["bpm"][int(t / TICK)]), 2)) for t in range(5, 60, 5)])

    out = os.path.join(OUT, "live_analysis.mp4")
    enc = encoder(out, audio=wav)
    flux_top = float(np.percentile(A["flux"], 99.5)) or 1.0
    hz = score.SR / FAST
    n = min(len(frames), int(SECONDS * FPS))
    for i in range(n):
        t = i / FPS
        k = min(int(t / TICK), len(tr) - 1)
        now = A["t"][k]
        im = Image.new("RGB", (W, H), BG)
        view.draw(im, frames[i])
        d = ImageDraw.Draw(im, "RGBA")
        cap = [c for c in CAPTIONS if c[0] <= t][-1]
        x0, w = X0 + 10, PANEL_W - 24

        # the spectrum right now, log frequency
        y, hh = ROWS["spec"]
        s = db[k]
        d.text((x0, y), "SPECTRUM NOW  fftSize 1024, 50 times a second", font=F.F_SMALL, fill=DIM)
        bins = np.arange(1, len(s))
        fx = np.log(bins * hz / 30.0) / np.log(16000 / 30.0)
        pts = [(x0 + float(a) * w, y + hh - float(np.clip((v + 100) / 80, 0, 1)) * (hh - 22))
               for a, v in zip(fx, s[1:]) if 0 <= a <= 1]
        d.polygon([(pts[0][0], y + hh)] + pts + [(pts[-1][0], y + hh)], fill=(60, 66, 76))
        d.line(pts, fill=TEXT, width=1)

        # level between its moving marks
        y, hh = ROWS["level"]
        d.text((x0, y), "LOUDNESS  between its own quiet and loud marks", font=F.F_SMALL, fill=DIM)
        ts = A["t"]
        lo_all, hi_all = -42.0, -4.0
        sc = lambda v: (v - lo_all) / (hi_all - lo_all)
        scroll_line(d, x0, y + 22, w, hh - 22, ts, sc(A["hi"]), now, AMBER)
        scroll_line(d, x0, y + 22, w, hh - 22, ts, sc(A["lo"]), now, AMBER)
        scroll_line(d, x0, y + 22, w, hh - 22, ts, sc(A["rawDb"]), now, TEXT)

        # bands
        y, hh = ROWS["bands"]
        d.text((x0, y), "BASS, MID, HIGH  live", font=F.F_SMALL, fill=DIM)
        for j, (nm, col) in enumerate((("bass", AMBER), ("mid", TEAL), ("high", ICE))):
            yy = y + 22 + j * 37
            scroll_line(d, x0, yy, w, 33, ts, bands[nm], now, col)
            vv = float(punch[nm][k])
            d.rectangle([x0 + w + 2, yy + 33 - vv * 33, x0 + w + 8, yy + 33], fill=col)

        # flux, threshold, onsets
        y, hh = ROWS["flux"]
        d.text((x0, y), "SPECTRAL FLUX, THRESHOLD, AND EVERY BEAT IT CALLED", font=F.F_SMALL, fill=DIM)
        scroll_line(d, x0, y + 22, w, hh - 40, ts, A["flux"] / flux_top, now, (150, 158, 168))
        scroll_line(d, x0, y + 22, w, hh - 40, ts, A["thr"] / flux_top, now, (214, 78, 88), 2)
        for tt in ts[onset & (ts > now - SPAN) & (ts <= now)]:
            xx = x0 + w - (now - tt) / SPAN * w
            d.line([xx, y + 22, xx, y + hh - 18], fill=(222, 170, 90, 150), width=1)
            d.ellipse([xx - 3, y + hh - 16, xx + 3, y + hh - 10], fill=AMBER)

        # bpm readout
        y, hh = ROWS["bpm"]
        b = float(A["bpm"][k])
        d.text((x0, y), "TEMPO IT THINKS IT HEARS", font=F.F_SMALL, fill=DIM)
        d.text((x0, y + 22), ("%.1f BPM" % b) if b else "not sure yet", font=F.F_MID, fill=TEXT)
        d.text((x0 + 360, y + 28), "the track is %.0f" % BPM, font=F.F_BODY, fill=DIM)
        ph = float(A["phase"][k])
        d.rectangle([x0 + 360, y + 62, x0 + 360 + 300, y + 74], fill=(44, 50, 57))
        d.rectangle([x0 + 360, y + 62, x0 + 360 + 300 * ph, y + 74], fill=AMBER)
        d.text((x0 + 360, y + 78), "beat position", font=F.F_SMALL, fill=DIM)

        if cap[1]:
            yy, hh = ROWS[cap[1]]
            d.rectangle([X0 + 2, yy - 2, W - 3, yy + hh + 1], outline=(222, 170, 90, 150), width=1)
        P = [p for p in PRESETS if p["at"] <= t][-1]["name"]
        d.text((16, 14), "preset: %s" % P, font=F.F_BODY, fill=TEXT)
        d.text((16, 42), "running on what it just heard", font=F.F_SMALL, fill=DIM)
        strip(im, cap[2], cap[3])
        send(enc, im)
    enc.stdin.close()
    enc.wait()
    print("wrote %s  %.1f MB" % (out, os.path.getsize(out) / 1e6))


if __name__ == "__main__":
    main()
