"""shows -- the beat on the phone, the lock, the bar shapes, the caches,
and the live bands.

Each of these was a defect found by reading the code against the
hardware it runs on: a beat pulse shorter than two phone frames, a phone
that never beat-locked a show the laptop locks, bar shapes taken from a
single 25 ms sample, an analysis cache that outlived its track, a file
player that left the microphone wired to the speaker, and live bands
that took the log of a value already in dB.
"""

import contextlib
import io
import json
import math
import os
import shutil
import subprocess
import sys
import tempfile

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from test_mau5 import ok, eq, note, HERE  # noqa: E402

# A note made here should reach the run's own list, not a second copy of
# the module that nobody prints.
note = getattr(sys.modules.get("__main__"), "note", note)


def _node_js(script, job):
    """Run a node snippet with `job` on stdin, or None without node."""
    if not shutil.which("node"):
        return None
    p = subprocess.run(["node", "-e", script], input=json.dumps(job),
                       capture_output=True, text=True, cwd=HERE, timeout=300)
    if p.returncode:
        raise AssertionError("node failed:\n%s" % p.stderr[-2000:])
    return json.loads(p.stdout)


class _Grid:
    """A track with a perfectly steady beat grid, and nothing else."""
    bands = True
    lock_conf = float("nan")

    def __init__(self, bpm, n=600, t0=0.25):
        self.bpm = float(bpm)
        self.beats = t0 + (60.0 / self.bpm) * np.arange(n)
        self.bars = self.beats[::4]

    def beat_phase(self, t):
        b = self.beats
        i = int(np.searchsorted(b, t) - 1)
        if i < 0 or i + 1 >= len(b):
            return 0.0
        return float((t - b[i]) / (b[i + 1] - b[i]))

    def beat_index(self, t):
        return float((t - self.beats[0]) * self.bpm / 60.0)

    def is_downbeat(self, t, window=0.08):
        d = self.bars
        i = int(np.searchsorted(d, t + window) - 1)
        return bool(0 <= i < len(d) and abs(t - d[i]) < window)

    def level_at(self, t):
        return 0.7

    def band_at(self, t, name="bass", punch=False):
        return 0.7

    def pitch_at(self, t):
        return 0.3

    def centroid_at(self, t):
        return 0.5

    def bands_at(self, t, n):
        return np.full(n, 0.5)


def _phone_times(seconds, seed=7):
    """Frame times the way the phone sends them: 40-70 ms apart, irregular.

    The finding simulated 55 +- 15 ms, the controller's own pace with a
    WiFi round trip in it.
    """
    rng = np.random.default_rng(seed)
    gaps = rng.uniform(0.040, 0.070, int(seconds / 0.040) + 10)
    t = 1.0 + np.cumsum(gaps)
    return t[t < 1.0 + seconds]


def _one_cue_show(level=2, accent=True, preset="solid", params=None):
    return {"cues": [{"start": 0.0, "end": 1000.0, "preset": preset,
                      "params": params or {}, "level": level}],
            "fade": 0.0, "accent": accent, "pulse": 0.40, "duration": 1000.0}


def t_pulse_survives_phone_frame_rate():
    """Every beat has a frame at the full pulse, at the phone's frame rate.

    The old pulse lasted a third of a beat, 115 ms at 174 bpm, and the
    phone caught it at whatever height the nearest frame happened to
    land on.  Checked against that curve too, so this test can tell the
    two apart.
    """
    import mau5show
    for bpm in (128.0, 174.0):
        m = _grid = _Grid(bpm)
        pl = mau5show.Player(_one_cue_show(level=2), music=m)
        ts = _phone_times(40.0)
        gains = []
        for t in ts:
            pl.frame(float(t))
            gains.append(pl.gain)
        gains = np.array(gains)
        amp = 0.40 * (0.4 + 0.3 * 2)
        old = np.array([(1 + amp * max(0.0, 1 - 3 * _grid.beat_phase(float(t))) ** 2)
                        / (1 + amp) for t in ts])
        b = _grid.beats
        peaks, old_peaks = [], []
        for i in range(len(b) - 1):
            if b[i] < ts[0] or b[i + 1] > ts[-1]:
                continue                          # only beats wholly sampled
            sel = (ts >= b[i]) & (ts < b[i + 1])
            if sel.any():
                peaks.append(gains[sel].max())
                old_peaks.append(old[sel].max())
        ok(len(peaks) > 50, "too few beats sampled at %.0f bpm" % bpm)
        ok(min(peaks) > 0.999,
           "at %.0f bpm a beat reached only %.3f of its pulse on the phone"
           % (bpm, min(peaks)))
        ok(min(old_peaks) < 0.95,
           "the old curve should have shown the spread this test is for "
           "(%.3f at %.0f bpm)" % (min(old_peaks), bpm))
        ok(gains.max() <= 1.0 + 1e-12, "the pulse lifted a frame above the guard's")


def t_pulse_spends_no_more_than_before():
    """A longer flash, the same current: the mean over a beat is the old one.

    The gain multiplies the frame after the guard, so its mean over a
    beat is the share of the guarded frame a song actually draws.  It
    must never exceed what the old (1 - 3ph)^2 curve gave, and at the
    depths the shows use it should equal it.  The peak may never pass 1.
    """
    import mau5show
    ph = (np.arange(20000) + 0.5) / 20000.0
    worst = 0.0
    for bpm in (60.0, 90.0, 128.0, 140.0, 174.0, 200.0, 260.0):
        for lvl in (1, 2, 3):
            for pulse in (0.22, 0.40, 1.0, 3.0):
                amp = pulse * (0.4 + 0.3 * lvl)
                g = np.array([mau5show.beat_gain(float(p), bpm, amp) for p in ph])
                old = (1 + amp * np.maximum(0.0, 1 - 3 * ph) ** 2) / (1 + amp)
                ok(g.max() <= 1.0 + 1e-12 and g.min() >= 0.0,
                   "pulse gain out of 0..1 at %.0f bpm" % bpm)
                d = float(g.mean() - old.mean())
                ok(d <= 1e-4, "the pulse spends %.4f more of the frame than "
                   "before at %.0f bpm, level %d, pulse %.2f" % (d, bpm, lvl, pulse))
                if pulse <= 1.0:
                    worst = max(worst, abs(d))
    ok(worst < 1e-3, "the pulse should spend what it did, and is %.4f out" % worst)


def t_accent_lands_every_downbeat_with_the_same_light():
    """The downbeat accent: the same strength every bar, the same total.

    Rendered on black so the frame is the accent and nothing else.
    """
    import mau5show
    for bpm in (128.0, 174.0):
        g = _Grid(bpm)
        show = _one_cue_show(level=2, params={"color": [0, 0, 0]})
        pl = mau5show.Player(show, music=g)
        want = mau5show.accent_level(bpm) * 255.0
        ts = _phone_times(40.0, seed=11)
        seen = {}
        for t in ts:
            f = pl.frame(float(t))
            v = float(f.max())
            if v > 0:
                i = int(np.searchsorted(g.bars, t) - 1)
                seen.setdefault(i, []).append(v)
        bars = [i for i, b in enumerate(g.bars) if ts[0] <= b < ts[-1] - 0.1]
        missed = [i for i in bars if i not in seen]
        eq(missed, [], "downbeats with no accent at %.0f bpm" % bpm)
        heights = [h for v in seen.values() for h in v]
        ok(max(heights) - min(heights) < 1e-6 and abs(heights[0] - want) < 1e-6,
           "accent heights vary at %.0f bpm: %.2f..%.2f" % (bpm, min(heights), max(heights)))
        # the same light as the old ramp, 0.45 * (1 - 6ph), over the 80 ms
        spb = 60.0 / bpm
        x = (np.arange(10000) + 0.5) / 10000.0 * (0.08 / spb)
        old = 0.45 * np.maximum(0.0, 1 - 6 * x).mean() * 0.08
        new = mau5show.accent_level(bpm) * 0.08
        ok(abs(new - old) < 1e-3 * old,
           "the accent adds %.5f, the old one %.5f" % (new, old))


_PULSE_JS = r"""
let raw = ''; process.stdin.setEncoding('utf8');
process.stdin.on('data', c => { raw += c; });
process.stdin.on('end', () => {
  const job = JSON.parse(raw);
  global.window = global;
  const S = require(job.here + '/remote/offline/show.js');
  process.stdout.write(JSON.stringify({
    gain: job.cases.map(c => S.beatGain(c[0], c[1], c[2])),
    accent: job.bpms.map(b => S.accentLevel(b)),
  }));
});
"""


def t_phone_pulse_matches_laptop_across_tempi():
    """The pulse and accent are one formula in two languages.

    The show parity test only reaches 128 bpm at five instants; the
    hold and the floor both depend on the tempo, so check across it.
    """
    import mau5show
    cases = [[ph, bpm, amp] for ph in (0.0, 0.01, 0.05, 0.12, 0.2, 0.33, 0.5, 0.9)
             for bpm in (0.0, 70.0, 126.4, 140.0, 174.02, 400.0)
             for amp in (0.112, 0.28, 0.4, 0.52, 3.9)]
    bpms = [0.0, 70.0, 100.0, 126.4, 128.0, 174.02, 400.0]
    res = _node_js(_PULSE_JS, {"here": HERE, "cases": cases, "bpms": bpms})
    if res is None:
        return note("shows: node not installed, the pulse went unchecked")
    worst = max(abs(mau5show.beat_gain(*c) - g) for c, g in zip(cases, res["gain"]))
    worst = max([worst] + [abs(mau5show.accent_level(b) - a)
                           for b, a in zip(bpms, res["accent"])])
    ok(worst < 1e-9, "the phone's pulse differs from the laptop's by %.2e" % worst)


_LOCK_JS = r"""
let raw = ''; process.stdin.setEncoding('utf8');
process.stdin.on('data', c => { raw += c; });
process.stdin.on('end', () => {
  const job = JSON.parse(raw);
  global.window = global;
  const E = require(job.here + '/remote/offline/engine.js');
  const S = require(job.here + '/remote/offline/show.js');
  const D = job.data;
  const dec = (b64, C) => {
    const bin = Buffer.from(b64, 'base64');
    return new C(bin.buffer, bin.byteOffset, bin.byteLength / C.BYTES_PER_ELEMENT);
  };
  const geo = { n: D.n, regions: D.regions };
  for (const k of Object.keys(D.f32)) geo[k] = dec(D.f32[k], Float32Array);
  for (const k of Object.keys(D.i16)) geo[k] = dec(D.i16[k], Int16Array);
  const h = E.makeHelmet(geo);
  const out = {};
  for (const analysed of [true, false]) {
    // test_mau5's _ShowDrive, with the mark a TrackDrive carries or not
    const music = {
      bands: true, bpm: 128.0, analysed: analysed,
      levelAt: t => 0.5 + 0.4 * Math.sin(t * 1.7),
      beatPhase: t => (t * 2.13) % 1,
      beatIndex: t => t * 2.13,
      isDownbeat: t => ((t * 0.53) % 1) < 0.05,
      pitchAt: t => (t * 0.11) % 1,
      centroidAt: t => 0.5 + 0.4 * Math.sin(t * 0.63),
      bandsAt: (t, n) => {
        const a = new Float64Array(n);
        for (let k = 0; k < n; k++) a[k] = 0.5 + 0.4 * Math.sin(t * 0.9 + k * 0.6);
        return a;
      },
      bandAt: (t, name, punch) => {
        const w = name === 'bass' ? 1.1 : (name === 'mid' ? 1.9 : 2.7);
        return 0.5 + 0.4 * Math.sin(t * w + (punch ? 0.3 : 0.0));
      },
    };
    const buf = new Float32Array(h.n * 3);
    const per = {};
    for (const name of job.shows) {
      const p = new S.ShowPlayer(D.shows[name], h, D);
      const frames = [], gains = [];
      for (const t of job.times[name]) {
        p.frame(t, music, buf);
        frames.push(Array.from(buf, v => Math.round(v * 1000) / 1000));
        gains.push(p.gain);
      }
      per[name] = { frames, gains };
    }
    out[analysed ? 'analysed' : 'live'] = per;
  }
  process.stdout.write(JSON.stringify(out));
});
"""


def t_phone_locks_like_the_laptop_on_an_analysed_grid():
    """Same frames on both devices when the grid is real, and when it is not.

    A TrackDrive carries the laptop's beat grid, and the show carries the
    laptop's verdict on it, so the phone has to lock exactly where the
    laptop does.  Music without that mark -- the live analyser -- must
    never be locked to.  Sampled inside the cues with a lockable preset,
    and checked to actually move a frame, so a lock that silently did
    nothing would fail here.
    """
    import mau5engine as E
    import mau5offline
    import mau5show
    from test_mau5 import _ShowDrive

    class Confident(_ShowDrive):
        lock_conf = 0.30
        # An analysis of the track, as mau5show.Music says it is and as
        # the JS twin below says with `analysed: true` -- so a scene
        # show's band-driven values read the curves on both sides.
        analysed = True

    data = mau5offline.bundle()
    if not data.get("shows"):
        return note("shows: no shows to check the lock against")
    names = sorted(data["shows"])
    times = {}
    for name in names:
        ts = []
        for c in data["shows"][name]["cues"]:
            if c["preset"] in E.LOCKABLE and len(ts) < 6:
                ts.append(round(c["start"] + 0.37 * (c["end"] - c["start"]), 3))
        times[name] = ts or [17.5]
    res = _node_js(_LOCK_JS, {"here": HERE, "data": data, "shows": names,
                              "times": times})
    if res is None:
        return note("shows: node not installed, the lock went unchecked")
    h = E.Helmet()
    worst, moved, locked = 0.0, 0.0, 0
    for name in names:
        show = dict(data["shows"][name])
        py_lock = mau5show.Player(show, helmet=h, music=Confident())
        py_free = mau5show.Player(show, helmet=h, music=_ShowDrive())
        eq(py_lock.lock, show.get("lock") is True,
           "%s: the laptop's lock disagrees with the verdict in the show" % name)
        ok(not py_free.lock, "%s locked to a grid with no confidence" % name)
        locked += int(py_lock.lock)
        for k, t in enumerate(times[name]):
            a = np.asarray(py_lock.frame(t), float)
            b = np.asarray(res["analysed"][name]["frames"][k], float).reshape(-1, 3)
            worst = max(worst, float(np.abs(a - b).max()),
                        abs(py_lock.gain - res["analysed"][name]["gains"][k]) * 255)
            f = np.asarray(py_free.frame(t), float)
            c = np.asarray(res["live"][name]["frames"][k], float).reshape(-1, 3)
            worst = max(worst, float(np.abs(f - c).max()))
            moved = max(moved, float(np.abs(a - f).max()))
    ok(worst < 0.01, "the phone and the laptop differ by %.3f counts with the "
       "lock in play" % worst)
    ok(locked >= 1, "no show locks, so this test checked nothing")
    ok(moved > 1.0, "locking never changed a frame, so this test checked nothing")


def t_shows_carry_the_lock_verdict():
    """Each show says whether its analysis was confident enough to lock.

    The phone never sees the analysis, only the cue list and a drive
    file, so the verdict has to travel in the show.
    """
    import mau5show
    n = 0
    for f in sorted(os.listdir(mau5show.SHOWS)):
        if not f.endswith(".json"):
            continue
        show = json.load(open(os.path.join(mau5show.SHOWS, f)))
        m = mau5show._music_for(show, os.path.join(HERE, show["track"]))
        if m is None:
            continue
        conf = float(getattr(m, "lock_conf", float("nan")))
        want = bool(conf == conf and conf >= mau5show.LOCK_MIN)
        ok("lock" in show, "%s carries no lock verdict" % f)
        eq(show["lock"], want, "%s lock verdict (confidence %.3f)" % (f, conf))
        n += 1
    ok(n, "no shows with an analysis to check")


def t_bar_shapes_use_the_whole_bar():
    """A missing kick on the one is not a drop.

    shape_of was handed one 25 ms frame per bar.  A bar whose downbeat
    frame dips -- a fill, a missing kick -- then read as a collapse and
    the next as a drop, and a whole phrase took the drop pool.
    """
    import mau5show
    import mau5song
    m = object.__new__(mau5show.Music)
    m.fps, m.duration = 40, 80.0
    m.bars = np.arange(0.0, 76.0, 1.875)
    m.energy = np.full(int(m.duration * m.fps), 0.8, np.float32)
    i = int(m.bars[20] * m.fps)
    m.energy[i:i + 2] = 0.2                       # the one, without its kick
    single = mau5song.shape_of(np.array([m.level_at(float(t)) for t in m.bars]))
    whole = mau5song.shape_of(m._bar_levels())
    ok(set(single) != {"steady"}, "the single-sample shapes should show the defect")
    eq([s for s in whole if s != "steady"], [], "shapes from the bar means")
    # And on the real thing: Strobe's soft intro is no drop.  The single
    # samples called bar 13 one, and the shipped show put a strobe on it.
    path = os.path.join(mau5show.SHOWS, "deadmau5 - Strobe.analysis.npz")
    if os.path.exists(path):
        s = mau5show.Music("deadmau5 - Strobe.mp3", fps=40, cache=path)
        old = mau5song.shape_of(np.array([s.level_at(float(t)) for t in s.bars]))
        ok(old[13] == "drop", "the single samples should find bar 13's false drop")
        eq([k for k in range(17) if s.shape[k] == "drop"], [],
           "drops in Strobe's first 17 bars")


def t_changed_track_is_analysed_again():
    """A cache is of one track; a different track by the same name is new.

    The content stamp catches a replacement whatever its file time.  A
    cache from before the stamp falls back to the file times, and with
    no track on the machine the cache is all there is and is used.
    """
    import mau5show
    import mau5song
    from test_mau5 import _click_wav
    d = tempfile.mkdtemp(prefix="mau5stamp")
    real = mau5song.analyse
    calls = []

    def counting(*a, **kw):
        calls.append(a[0])
        return real(*a, **kw)

    try:
        mau5song.analyse = counting
        track = os.path.join(d, "song.wav")
        cache = os.path.join(d, "song.analysis.npz")
        quiet = io.StringIO()
        with contextlib.redirect_stdout(quiet):
            _click_wav(track, 128.0, seconds=20.0)
            a = mau5show.Music(track, cache=cache)
            eq(len(calls), 1, "first load should analyse")
            mau5show.Music(track, cache=cache)
            eq(len(calls), 1, "an unchanged track was analysed again")

            # the same name, another edit, and an *older* file time
            _click_wav(track, 100.0, seconds=20.0)
            os.utime(track, (1e9, 1e9))
            b = mau5show.Music(track, cache=cache)
            eq(len(calls), 2, "a replaced track kept its old analysis")
            ok(abs(b.bpm - 100.0) < 1.5 and abs(a.bpm - 128.0) < 1.5,
               "re-analysis gave %.1f, wanted 100" % b.bpm)

            # no track here: the cache is used, whatever it says
            os.rename(track, track + ".gone")
            c = mau5show.Music(track, cache=cache)
            eq(len(calls), 2, "with no track the cache must be trusted")
            eq(round(c.bpm, 3), round(b.bpm, 3), "cache without its track")
            os.rename(track + ".gone", track)

            # a cache from before stamps: file times decide
            z = dict(np.load(cache))
            z.pop("src")
            np.savez_compressed(cache, **z)
            os.utime(track, (1e9, 1e9))
            mau5show.Music(track, cache=cache)
            eq(len(calls), 2, "an unstamped cache newer than its track")
            os.utime(cache, (1e9, 1e9))
            os.utime(track, None)
            mau5show.Music(track, cache=cache)
            eq(len(calls), 3, "an unstamped cache older than its track")
        ok("has changed since it was analysed" in quiet.getvalue(),
           "a changed track should say so")
    finally:
        mau5song.analyse = real
        shutil.rmtree(d, ignore_errors=True)


def t_decoded_audio_follows_the_track():
    """decode's wav is of the track that is there now, not the last one.

    The case that beat the old rule: the replacement keeps an old file
    time, as a Finder copy does, and looks older than the decoded wav.
    """
    import mau5song
    from test_mau5 import _click_wav
    if not shutil.which("afconvert"):
        return note("shows: no afconvert, decode's cache went unchecked")
    d = tempfile.mkdtemp(prefix="mau5decode")
    try:
        src = os.path.join(d, "src.wav")
        # AIFF, which decodes to plain PCM as an mp3 does (an AAC source
        # comes back as extensible WAVE, which the stdlib cannot read)
        track = os.path.join(d, "song.aif")

        def encode(bpm):
            _click_wav(src, bpm, seconds=8.0)
            subprocess.run(["afconvert", "-f", "AIFF", "-d", "BEI16", src, track],
                           check=True, capture_output=True)

        encode(128.0)
        w1 = mau5song.decode(track, cache_dir=d)
        a1, _ = mau5song.load_wav(w1)
        before = os.path.getmtime(w1)
        eq(mau5song.decode(track, cache_dir=d), w1, "decode moved its cache")
        eq(os.path.getmtime(w1), before, "an unchanged track was decoded again")
        encode(90.0)
        os.utime(track, (1e9, 1e9))
        a2, _ = mau5song.load_wav(mau5song.decode(track, cache_dir=d))
        n = min(len(a1), len(a2))
        ok(float(np.abs(a1[:n] - a2[:n]).max()) > 0.1,
           "a replaced track decoded as the one it replaced")
    finally:
        shutil.rmtree(d, ignore_errors=True)


_AUDIO_JS = r"""
let raw = ''; process.stdin.setEncoding('utf8');
process.stdin.on('data', c => { raw += c; });
process.stdin.on('end', async () => {
  const job = JSON.parse(raw);
  global.window = global;
  // A Web Audio graph that only records its wiring.
  let SR = 48000;
  const mk = kind => ({ kind, outs: new Set(),
    connect(d) { this.outs.add(d); return d; },
    disconnect(d) { if (d === undefined) this.outs.clear(); else this.outs.delete(d); } });
  class Ctx {
    constructor() { this.state = 'running'; this.sampleRate = SR; this.currentTime = 0;
                    this.destination = mk('speaker'); }
    createAnalyser() {
      const n = mk('analyser');
      n.fftSize = 2048; n.minDecibels = -100; n.maxDecibels = -30;
      Object.defineProperty(n, 'frequencyBinCount', { get() { return this.fftSize / 2; } });
      n.getFloatFrequencyData = a => { a.fill(-60); a[0] = -Infinity; a[3] = -10; };
      n.getByteFrequencyData = a => a.fill(0);
      n.getByteTimeDomainData = a => a.fill(128);
      return n;
    }
    createMediaElementSource() { return mk('file'); }
    createMediaStreamSource() { return mk('stream'); }
    resume() {}
  }
  global.AudioContext = Ctx;
  global.Audio = class { constructor() { this.volume = 1; this.paused = true; }
                         play() { this.paused = false; return Promise.resolve(); }
                         pause() { this.paused = true; } };
  URL.createObjectURL = () => 'blob:song'; URL.revokeObjectURL = () => {};
  const track = { getTracks: () => [], getAudioTracks: () => [], getVideoTracks: () => [] };
  Object.defineProperty(globalThis, 'navigator', { configurable: true, writable: true,
    value: { mediaDevices: { getUserMedia: async () => track } } });
  global.isSecureContext = true;
  const A = require(job.here + '/remote/offline/audio.js');
  const reach = (a, b, seen = new Set()) => {
    if (a === b) return true;
    if (seen.has(a)) return false;
    seen.add(a);
    for (const o of a.outs) if (reach(o, b, seen)) return true;
    return false;
  };
  const out = {};
  const an = new A.Analyser();
  await an.useFile({ name: 'song.mp3' });
  out.fileHeard = reach(an.src, an.ctx.destination);
  out.fileAnalysed = reach(an.src, an.node);
  an.sample();
  out.bytes = [an.freq[0], an.freq[1], an.freq[3]];
  an.stop();
  await an.useMic();
  out.micHeard = reach(an.src, an.ctx.destination);
  out.micAnalysed = reach(an.src, an.node);
  out.analyserHeard = reach(an.node, an.ctx.destination);
  an.stop();

  // bands: real dB, unclipped, and no two bands on one bin
  an.db.fill(-140); an.db[1] = -40; an.db[2] = -50; an.db[5] = -10;
  an.db[6] = -40; an.db[7] = -50;
  out.dbOne = an._bandDb(1, 2);
  out.dbLoud = an._bandDb(5, 6);
  out.dbMix = an._bandDb(6, 8);
  out.edges = {};
  for (const sr of [44100, 48000]) {
    SR = sr;
    const b = new A.Analyser();
    b._ctx();
    for (const nb of [12, 24]) {
      b._bands(nb);
      out.edges[sr + '/' + nb] = Array.from(b._bandCache[nb]);
    }
  }
  process.stdout.write(JSON.stringify(out));
});
"""


def t_live_audio_wiring_and_bands():
    """The file plays through the speaker and the microphone never does;
    the live bands are in real dB, each on bins of its own.

    After a file, 'listen' used to play the microphone out of the phone:
    the analyser had been wired to the speaker and stop() never unwired
    it.  And the bands took 20*log10 of the byte spectrum, which is
    already dB, with the two lowest eq bars both reading bin 1.
    """
    res = _node_js(_AUDIO_JS, {"here": HERE})
    if res is None:
        return note("shows: node not installed, the live audio went unchecked")
    ok(res["fileHeard"] and res["fileAnalysed"], "the file must play and be analysed")
    ok(res["micAnalysed"], "the microphone must reach the analyser")
    ok(not res["micHeard"], "after a file, the microphone plays out of the speaker")
    ok(not res["analyserHeard"], "the analyser is still wired to the speaker")
    # the onset detector's bytes, made by the spec's own formula
    eq(res["bytes"], [0, int(math.floor(255 / 70.0 * 40.0)), 255], "derived bytes")
    ok(abs(res["dbOne"] + 40.0) < 1e-9, "one bin at -40 dB read %.3f" % res["dbOne"])
    ok(abs(res["dbLoud"] + 10.0) < 1e-9,
       "a bin at -10 dB, past the byte range, read %.3f" % res["dbLoud"])
    want = 10 * math.log10((1e-4 + 1e-5) / 2 + 1e-14)
    ok(abs(res["dbMix"] - want) < 1e-9, "a band is the mean power of its bins")
    for k, e in res["edges"].items():
        ok(all(b > a for a, b in zip(e, e[1:])), "bands %s share a bin: %s" % (k, e[:8]))
        ok(e[-1] <= 511, "bands %s run past the spectrum" % k)


NEW = [t_pulse_survives_phone_frame_rate,
       t_pulse_spends_no_more_than_before,
       t_accent_lands_every_downbeat_with_the_same_light,
       t_phone_pulse_matches_laptop_across_tempi,
       t_phone_locks_like_the_laptop_on_an_analysed_grid,
       t_shows_carry_the_lock_verdict,
       t_bar_shapes_use_the_whole_bar,
       t_changed_track_is_analysed_again,
       t_decoded_audio_follows_the_track,
       t_live_audio_wiring_and_bands]


def _group():
    """test_mau5 files this module's GROUP under the name "shows", which
    is already a group there -- replacing it would quietly stop t_shows
    and the rest of the suite's show checks running.  So they come along.
    """
    have = getattr(sys.modules.get("__main__"), "GROUPS", None)
    if not isinstance(have, dict) or "shows" not in have:
        import test_mau5
        have = test_mau5.GROUPS
    mine = {f.__name__ for f in NEW}
    return [f for f in have.get("shows", []) if f.__name__ not in mine] + NEW


GROUP = _group()
