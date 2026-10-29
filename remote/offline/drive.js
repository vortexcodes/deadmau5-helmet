// ----------------------------------------------------------------------
// drive.js -- a track's own analysis, read off the controller.
//
// The live analyser hears the room, which is the right answer when
// nobody knows what is playing.  When the track *is* known, the
// laptop's analysis of it is better in every way: it has the real
// beat grid rather than an estimate, it knows where the bars are, it
// is not confused by a crowd, and it does not need a microphone --
// which matters because the page the controller serves cannot have
// one.
//
// mau5drive.py writes it: envelopes at 20 Hz quantised to a byte, the
// beat and bar grids as float32, and a chroma vector per bar.  Thirty
// to eighty kilobytes a track, fetched when a show is picked.
//
// Same Music interface as everything else, so a show cannot tell
// which of the three drives it is running on.
// ----------------------------------------------------------------------

(function (root) {
'use strict';

const MAGIC = 'MAU5DRV1';

function clamp(v, lo, hi) { return v < lo ? lo : (v > hi ? hi : v); }

class TrackDrive {
  constructor(buf) {
    const dv = new DataView(buf);
    let p = 0;
    const magic = new TextDecoder().decode(new Uint8Array(buf, 0, 8));
    if (magic !== MAGIC) throw new Error('not a drive file');
    p = 8;
    this.fps = dv.getUint16(p, true); p += 2;
    this.n = dv.getUint32(p, true); p += 4;
    const ncurve = dv.getUint8(p); p += 1;
    const nbeats = dv.getUint32(p, true); p += 4;
    const nbars = dv.getUint32(p, true); p += 4;
    this.duration = dv.getFloat64(p, true); p += 8;

    const names = [];
    for (let i = 0; i < ncurve; i++) {
      const raw = new Uint8Array(buf, p, 12); p += 12;
      let end = raw.indexOf(0);
      if (end < 0) end = 12;
      names.push(new TextDecoder().decode(raw.subarray(0, end)));
    }
    this.curve = {};
    for (const nm of names) {
      this.curve[nm] = new Uint8Array(buf, p, this.n);
      p += this.n;
    }
    this.beats = new Float32Array(buf.slice(p, p + nbeats * 4)); p += nbeats * 4;
    this.bars = new Float32Array(buf.slice(p, p + nbars * 4)); p += nbars * 4;
    this.chroma = new Uint8Array(buf, p, nbars * 12);

    this.bands = true;
    this.bpm = this.beats.length > 1
      ? 60 / ((this.beats[this.beats.length - 1] - this.beats[0])
              / (this.beats.length - 1))
      : 120;
    this._pitch = new Float64Array(nbars);
    this._pitchDone = new Uint8Array(nbars);
  }

  _at(name, t) {
    const c = this.curve[name];
    if (!c) return 0;
    let i = Math.round(t * this.fps);
    if (i < 0) i = 0; else if (i >= this.n) i = this.n - 1;
    return c[i] / 255;
  }

  levelAt(t) { return this._at('energy', t); }

  bandAt(t, name, punch) {
    return this._at('b_' + name + '_' + (punch ? 'p' : 'e'), t);
  }

  // mau5show.Music.bands_at: the energy curve smeared across bands
  // with a per-band lag.  It looks like a spectrum analyser without
  // pretending to be one, and the point of porting it exactly is that
  // `eq` should look the same here as it does on the laptop.  The lag
  // is in seconds, not samples, because this file is 20 Hz and the
  // laptop's analysis was 40.
  bandsAt(t, n) {
    const out = new Float64Array(n);
    for (let b = 0; b < n; b++) {
      const v = this._at('energy', t - b * 0.05);
      out[b] = clamp(v * (1.15 - 0.5 * b / n), 0, 1);
    }
    return out;
  }

  // Interpolated between measured beats rather than computed from the
  // tempo, so it follows a track that drifts instead of walking away
  // from it over four minutes.
  beatIndex(t) {
    const b = this.beats;
    if (b.length < 2) return t * this.bpm / 60;
    let i = this._before(b, t);
    if (i < 0) return (t - b[0]) / Math.max(b[1] - b[0], 1e-6);
    if (i + 1 >= b.length) {
      const spb = Math.max(b[b.length - 1] - b[b.length - 2], 1e-6);
      return b.length - 1 + (t - b[b.length - 1]) / spb;
    }
    return i + (t - b[i]) / Math.max(b[i + 1] - b[i], 1e-6);
  }

  beatPhase(t) {
    const b = this.beats;
    if (b.length < 2) return 0;
    const i = this._before(b, t);
    if (i < 0 || i + 1 >= b.length) return 0;
    return (t - b[i]) / Math.max(b[i + 1] - b[i], 1e-6);
  }

  isDownbeat(t, window) {
    const w = window === undefined ? 0.08 : window;
    const d = this.bars;
    if (!d.length) return false;
    const i = this._before(d, t + w);
    return i >= 0 && i < d.length && Math.abs(t - d[i]) < w;
  }

  // A circular mean of the bar's pitch-class profile, cached: one
  // turn of hue is one octave, so a track that modulates moves the
  // whole palette and a bassline walking octaves does not.
  pitchAt(t) {
    const d = this.bars;
    if (!d.length) return 0;
    let i = this._before(d, t);
    if (i < 0) i = 0;
    if (i >= d.length) i = d.length - 1;
    if (!this._pitchDone[i]) {
      let x = 0, y = 0;
      for (let k = 0; k < 12; k++) {
        const w = this.chroma[i * 12 + k] / 255;
        const a = 2 * Math.PI * k / 12;
        x += w * Math.cos(a); y += w * Math.sin(a);
      }
      let v = Math.atan2(y, x) / (2 * Math.PI);
      this._pitch[i] = v - Math.floor(v);
      this._pitchDone[i] = 1;
    }
    return this._pitch[i];
  }

  centroidAt(t) {
    const lo = this.bandAt(t, 'bass', false);
    const mid = this.bandAt(t, 'mid', false);
    const hi = this.bandAt(t, 'high', false);
    const tot = lo + mid + hi;
    return tot > 1e-6 ? clamp((0.5 * mid + hi) / tot, 0, 1) : 0.5;
  }

  // index of the last entry <= t, or -1
  _before(arr, t) {
    let lo = 0, hi = arr.length;
    while (lo < hi) {
      const m = (lo + hi) >> 1;
      if (arr[m] <= t) lo = m + 1; else hi = m;
    }
    return lo - 1;
  }
}

async function loadDrive(origin, file) {
  const r = await fetch((origin || '') + '/' + file, { cache: 'force-cache' });
  if (!r.ok) throw new Error('no drive file (' + r.status + ')');
  return new TrackDrive(await r.arrayBuffer());
}

const api = { TrackDrive, loadDrive };
root.MAU5 = Object.assign(root.MAU5 || {}, api);
if (typeof module !== 'undefined' && module.exports) module.exports = api;

})(typeof globalThis !== 'undefined' ? globalThis : this);
