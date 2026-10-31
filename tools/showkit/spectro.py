#!/usr/bin/env python3
"""spectro.py "<base>" out.png [from_bar to_bar] -- see the song: a log spectrogram with the bar
lines and numbers on it, and the bass, mid and high curves underneath. Run from the repo root."""
import json, os, subprocess, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
base, out = sys.argv[1], sys.argv[2]
z = np.load(os.path.join("shows", base + ".analysis.npz"), allow_pickle=True)
bars = np.asarray(z["bars"], float); fps = float(z["fps"]); dur = float(z["duration"])
lo = int(sys.argv[3]) if len(sys.argv) > 3 else 0
hi = int(sys.argv[4]) if len(sys.argv) > 4 else len(bars)
t0 = bars[lo]; t1 = bars[hi] if hi < len(bars) else dur
mp3 = os.path.join("shows", base + ".mp3")
raw = subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-ss", str(max(t0, 0)), "-t", str(t1 - t0), "-i", mp3, "-ac", "1", "-ar", "22050", "-f", "f32le", "-"], capture_output=True, check=True).stdout
m = np.frombuffer(raw, dtype=np.float32)
N, H = 2048, 512
nf = max(1, (len(m) - N) // H)
step = max(1, nf // 2400)
win = np.hanning(N)
S = np.array([np.abs(np.fft.rfft(m[i * H:i * H + N] * win)) for i in range(0, nf, step)]).T
f = np.fft.rfftfreq(N, 1 / 22050)
edges = np.geomspace(30, 11000, 90)
L = np.array([S[(f >= a) & (f < b)].sum(0) if ((f >= a) & (f < b)).any() else np.zeros(S.shape[1]) for a, b in zip(edges, edges[1:])])
L = np.log1p(L * 0.05)
fig, ax = plt.subplots(2, 1, figsize=(18, 7), sharex=True, gridspec_kw={"height_ratios": [3, 1]})
ax[0].imshow(L, origin="lower", aspect="auto", extent=[t0, t1, 0, 89], cmap="magma")
ax[0].set_ylabel("30 Hz to 11 kHz")
every = max(1, (hi - lo) // 32)
every = next(x for x in (1, 2, 4, 8, 16, 32) if x >= every)
for b in range(lo, min(hi, len(bars))):
    if b % every == 0:
        ax[0].axvline(bars[b], color="w", lw=0.6, alpha=0.7)
        ax[1].axvline(bars[b], color="k", lw=0.4, alpha=0.5)
        ax[0].text(bars[b], 85, str(b), color="w", fontsize=8)
tt = np.arange(len(z["b_bass_e"])) / fps
mask = (tt >= t0) & (tt <= t1)
for k, c in (("bass", "tab:red"), ("mid", "tab:green"), ("high", "tab:blue")):
    v = np.asarray(z["b_%s_e" % k], float)
    v = v / max(v.max(), 1e-9)
    ax[1].plot(tt[mask], v[mask], color=c, lw=0.6, label=k)
ax[1].legend(loc="upper right", fontsize=8)
ax[1].set_xlim(t0, t1)
ax[1].set_xlabel("seconds; white numbers are bars")
fig.tight_layout()
fig.savefig(out, dpi=80)
print(out)
