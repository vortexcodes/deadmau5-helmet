#!/usr/bin/env python3
"""grid.py -- measure a song's real beat grid against its audio. Run from the repo root.

  python3 $KIT/grid.py scan  "shows/<base>.mp3"
      Tempo from the improved estimator, refined against the onsets; the phase of
      the onsets per 8 bars (flat means right, a step means a splice or tempo
      change); which beat starts a bar and a phrase.
  python3 $KIT/grid.py fold  "shows/<base>.mp3" --spb S --anchor T [--holds "t:s,..."] [--spans "0-8,16-32"]
      Onset strength folded into 16 steps per span, per band: read the kick and clap
      off this. Step 0 of a four-on-the-floor bar should carry the kick.
  python3 $KIT/grid.py write "<base>" --spb S --anchor T [--holds "t:s,..."]
      T is the time of ANY downbeat that starts a bar. Writes shows/scenes/<base>.beats
      from the earliest downbeat, deletes the stale analysis and rebuilds the show.
      A hold "t:s" means the music comes back s seconds late from time t (a splice).
  python3 $KIT/grid.py check "<base>"
      The built show's grid against the audio, per 8 bars. Worst should be under 15 ms.
"""
import argparse, json, os, re, subprocess, sys
import numpy as np
REPO = os.getcwd()
KIT = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.join(KIT, "work")
sys.path.insert(0, REPO); sys.path.insert(0, KIT)
SR, N, HOP = 22050, 1024, 256
BANDS = [("sub", 20, 90), ("bass", 90, 200), ("lowmid", 200, 600), ("mid", 600, 2000),
         ("pres", 2000, 5000), ("air", 5000, 11000)]
CH = " .:-=+*#%@"


def env_of(mp3):
    os.makedirs(WORK, exist_ok=True)
    p = os.path.join(WORK, re.sub(r"\W+", "_", os.path.basename(mp3)) + ".env.npz")
    if os.path.exists(p) and os.path.getmtime(p) >= os.path.getmtime(mp3):
        z = np.load(p)
        return {k: z[k] for k in z.files}
    raw = subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-i", mp3, "-ac", "1",
                          "-ar", str(SR), "-f", "f32le", "-"], capture_output=True, check=True).stdout
    m = np.frombuffer(raw, dtype=np.float32)
    win = np.hanning(N).astype(np.float32)
    f = np.fft.rfftfreq(N, 1 / SR)
    nf = (len(m) - N) // HOP
    out = {nm: np.zeros(nf, np.float32) for nm, _, _ in BANDS}
    masks = {nm: (f >= a) & (f < b) for nm, a, b in BANDS}
    for s in range(0, nf, 4000):
        e = min(s + 4000, nf)
        fr = np.stack([m[i * HOP:i * HOP + N] for i in range(s, e)]) * win
        F = np.abs(np.fft.rfft(fr, axis=1))
        for nm in out:
            out[nm][s:e] = np.log1p(F[:, masks[nm]].sum(1) * 0.02)
    d = {"tt": (np.arange(nf) * HOP + N / 2) / SR, "dur": np.array(len(m) / SR)}
    for nm, v in out.items():
        d[nm] = v
        d[nm + "_od"] = np.maximum(0, np.diff(v, prepend=v[0]))
    np.savez(p, **d)
    return d


def onsets(d):
    return d["pres_od"] + d["air_od"] + 0.7 * d["lowmid_od"] + 0.7 * d["bass_od"]


def comb(od, tt0, dt, ts):
    i = np.round((ts - tt0) / dt).astype(int)
    i = i[(i >= 1) & (i < len(od) - 1)]
    return od[i].mean() + 0.5 * (od[i - 1].mean() + od[i + 1].mean()) if len(i) else 0.0


def refine(d, spb0, lo=0.0, hi=None, width=0.004, steps=161):
    """The best beat length near spb0 and a 16th phase, from a comb at the 16th."""
    od, tt = onsets(d), d["tt"]
    dt = tt[1] - tt[0]
    hi = hi if hi is not None else float(d["dur"])
    best = None
    for s in np.linspace(spb0 * (1 - width), spb0 * (1 + width), steps):
        s16 = s / 4
        for p in np.arange(0, s16, 0.003):
            sc = comb(od, tt[0], dt, np.arange(lo + p, hi, s16))
            if best is None or sc > best[0]:
                best = (sc, s, lo + p)
    return best


def phase_table(d, spb, anchor, holds=(), span_bars=8):
    od, tt = onsets(d), d["tt"]
    dt = tt[1] - tt[0]
    dur = float(d["dur"])
    t0 = anchor % (4 * spb)
    rows = []
    bar = 0
    s16 = spb / 4

    def late(t):
        return sum(s for at, s in holds if t >= at)
    while True:
        lo = t0 + bar * 4 * spb
        if lo + late(lo) >= dur - 1:
            break
        base = np.arange(0, span_bars * 16) * s16 + lo
        base = base + np.array([late(x) for x in base])
        base = base[base < dur]
        ph = np.arange(-s16 / 2, s16 / 2, 0.002)
        sc = np.array([comb(od, tt[0], dt, base + p) for p in ph])
        rows.append((bar, float(ph[sc.argmax()] * 1000), float(sc.max() / max(np.median(sc), 1e-6))))
        bar += span_bars
    return rows, t0


def parse_holds(s):
    return [tuple(float(x) for x in h.split(":")) for h in s.split(",")] if s else []


def fold_print(d, spb, t0, holds, lo, hi):
    print("bars %d-%d   (16 steps, | every beat; one row per band)" % (lo, hi))
    tt = d["tt"]

    def late(t):
        return sum(s for at, s in holds if t >= at)
    for nm, _, _ in BANDS:
        e = d[nm + "_od"]
        o = np.zeros(16)
        for b in range(lo, hi):
            for k in range(16):
                t = t0 + (b + k / 16) * 4 * spb
                t += late(t)
                i = np.searchsorted(tt, t)
                o[k] += e[max(0, i - 2):i + 3].max()
        o /= max(hi - lo, 1)
        v = o / max(o.max(), 1e-6)
        s = "|".join("".join(CH[min(9, int(a * 9.99))] for a in v[i:i + 4]) for i in range(0, 16, 4))
        print("   %-7s %s   peak %.2f" % (nm, s, o.max()))


def beat_novelty(d, spb, t0):
    tt = d["tt"]
    dur = float(d["dur"])
    n = int((dur - t0) / spb)
    e = np.stack([d[nm] for nm, _, _ in BANDS], 1)
    out = np.zeros(n)
    for k in range(2, n - 2):
        a0, a1, b0 = [np.searchsorted(tt, t0 + (k + o) * spb) for o in (-2, 0, 2)]
        out[k] = np.abs(e[a1:b0].mean(0) - e[a0:a1].mean(0)).sum()
    return out


def cmd_scan(a):
    import mau5song_new as S
    d = env_of(a.track)
    an = S.analyse(a.track, verbose=False)
    bpm0 = float(an["bpm"])
    bars = np.asarray(an["bars"], float)
    print("estimator: %.3f BPM, first bar %.3f s, tempo lock %.3f, bar lock %s; song %.1f s"
          % (bpm0, bars[0], float(an.get("lock_conf", an.get("lock", float("nan")))), an.get("bar_lock", "?"), float(d["dur"])))
    _, spb, ph = refine(d, 60.0 / bpm0)
    _, spb2, ph2 = refine(d, spb, width=0.0006, steps=61)
    print("refined over the whole song: spb %.6f = %.3f BPM" % (spb2, 60 / spb2))
    half = float(d["dur"]) / 2
    A = refine(d, spb2, 0.0, half, width=0.002, steps=41)
    B = refine(d, spb2, half, None, width=0.002, steps=41)
    print("first half %.3f BPM, second half %.3f BPM (these should agree within 0.05)" % (60 / A[1], 60 / B[1]))
    anchor = float(bars[0])
    rows, t0 = phase_table(d, spb2, anchor)
    print("phase of the music against that grid per 8 bars, ms (flat = right; one 16th = %.0f ms; contrast under 1.15 means sparse, ignore it):" % (spb2 * 250))
    print("  " + "  ".join("%d:%+.0f(%.2f)" % r for r in rows))
    # Snap the estimator's bar line onto the refined 16th grid before asking about phrases.
    nov = beat_novelty(d, spb2, t0)
    bars4 = [nov[q::4].mean() for q in range(4)]
    print("change per beat position, estimator's bar 1 at %.3f s: %s  (the highest is where bars really start, 0 = estimator is right)"
          % (t0, " ".join("%d:%.2f" % (q, v) for q, v in enumerate(bars4))))
    top = sorted(range(32), key=lambda q: -nov[q::32].mean())[:6]
    print("strongest phrase positions, in beats mod 32 from that bar 1: %s" % ", ".join("%d(%.2f)" % (q, nov[q::32].mean()) for q in top))
    big = np.argsort(-nov)[:24]
    print("biggest single changes (time, beat from bar 1, beat mod 4): %s"
          % "; ".join("%.1fs b%d m%d" % (t0 + k * spb2, k, k % 4) for k in sorted(big)))
    print("suggested next: grid.py fold with --spb %.6f --anchor %.3f, decide the bar line, then grid.py write" % (spb2, t0))


def cmd_fold(a):
    d = env_of(a.track)
    holds = parse_holds(a.holds)
    t0 = a.anchor % (4 * a.spb)
    nb = int((float(d["dur"]) - t0) / (4 * a.spb))
    spans = ([tuple(int(x) for x in s.split("-")) for s in a.spans.split(",")] if a.spans
             else [(b, min(b + 16, nb)) for b in range(0, nb, 16)])
    print("bar 0 at %.3f s, %.3f BPM, %d bars" % (t0, 60 / a.spb, nb))
    for lo, hi in spans:
        fold_print(d, a.spb, t0, holds, lo, hi)


def cmd_write(a):
    mp3 = os.path.join("shows", a.base + ".mp3")
    d = env_of(mp3)
    holds = sorted(parse_holds(a.holds))
    t0 = a.anchor % (4 * a.spb)
    dur = float(d["dur"])
    n = int((dur - t0 + sum(s for _, s in holds)) / a.spb) + 1
    ts = []
    for k in range(n):
        t = t0 + k * a.spb
        for at, s in holds:
            if t >= at - 1e-9:
                t += s
        if t < dur:
            ts.append(t)
    p = os.path.join("shows", "scenes", a.base + ".beats")
    with open(p, "w") as f:
        f.write("".join("%.6f\n" % t for t in ts))
    print("wrote %s: %d beats, %d bars, bar 0 at %.3f s, %.3f BPM" % (p, len(ts), len(ts) // 4, t0, 60 / a.spb))
    npz = os.path.join("shows", a.base + ".analysis.npz")
    if os.path.exists(npz):
        os.remove(npz)
    subprocess.run([sys.executable, "mau5show.py", "build", mp3], check=True)


def cmd_check(a):
    show = json.load(open(os.path.join("shows", a.base + ".json")))
    d = env_of(os.path.join("shows", a.base + ".mp3"))
    z = np.load(os.path.join("shows", a.base + ".analysis.npz"))
    beats = z["beats"]
    bars = z["bars"]
    diffs = np.diff(beats)
    spb = float(np.median(diffs))
    late = diffs - spb
    holds = [(float(beats[i + 1]), float(late[i])) for i in np.flatnonzero(late > 0.005)]
    rows, t0 = phase_table(d, spb, float(bars[0]), holds)
    print("%s: %.3f BPM, %d bars, bar 0 at %.3f s, holds %s" % (a.base, 60 / spb, len(bars), bars[0], holds))
    print("music against the grid per 8 bars, ms (contrast): " + "  ".join("%d:%+.0f(%.2f)" % r for r in rows))
    good = [abs(r[1]) for r in rows if r[2] >= 1.15]
    print("worst %.0f ms where the music is clear enough to say, mean %+.1f ms" % (max(good) if good else 0, np.mean([r[1] for r in rows if r[2] >= 1.15]) if good else 0))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("scan"); s.add_argument("track")
    f = sub.add_parser("fold"); f.add_argument("track"); f.add_argument("--spb", type=float, required=True)
    f.add_argument("--anchor", type=float, required=True); f.add_argument("--holds", default=""); f.add_argument("--spans", default="")
    w = sub.add_parser("write"); w.add_argument("base"); w.add_argument("--spb", type=float, required=True)
    w.add_argument("--anchor", type=float, required=True); w.add_argument("--holds", default="")
    c = sub.add_parser("check"); c.add_argument("base")
    a = ap.parse_args()
    {"scan": cmd_scan, "fold": cmd_fold, "write": cmd_write, "check": cmd_check}[a.cmd](a)


if __name__ == "__main__":
    main()
