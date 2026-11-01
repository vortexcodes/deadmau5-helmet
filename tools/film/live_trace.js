// live_trace.js -- run the page's real live analyser over a track, without a browser.
//
// audio.js only ever talks to two AnalyserNodes and a clock, so this stands in for
// those and nothing else. livefilm.py works out what each node would return at every
// 20 ms tick, following the Web Audio spec, and writes it to disk; here that gets fed
// to the same Analyser and LiveMusic the phone runs, then to the same presets and guard.
//
// node live_trace.js job.json     (see livefilm.py for the fields)
'use strict';

const fs = require('fs');
const path = require('path');
const OFF = path.join(__dirname, '..', '..', 'remote', 'offline');
const E = require(path.join(OFF, 'engine.js'));
const G = require(path.join(OFF, 'guard.js'));
const A = require(path.join(OFF, 'audio.js'));

const job = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const d = job.data;

function decode(b64, Ctor) {
  const buf = Buffer.from(b64, 'base64');
  return new Ctor(buf.buffer, buf.byteOffset, buf.byteLength / Ctor.BYTES_PER_ELEMENT);
}
const o = { n: d.n, regions: d.regions };
for (const k of Object.keys(d.f32)) o[k] = decode(d.f32[k], Float32Array);
for (const k of Object.keys(d.i16)) o[k] = decode(d.i16[k], Int16Array);
const h = E.makeHelmet(o);

function floats(p) {
  const b = fs.readFileSync(p);
  return new Float32Array(b.buffer, b.byteOffset, b.byteLength / 4);
}
const fastDb = floats(job.fast_db), slowByte = floats(job.slow_byte), timeByte = floats(job.time_byte);
const NF = job.fast_bins, NS = job.slow_bins, NT = job.time_len, ticks = job.ticks;

let tick = 0;
const an = new A.Analyser();
an.ctx = { sampleRate: job.sr, currentTime: 0, state: 'running' };
an.node = {
  minDecibels: -100, maxDecibels: -30,
  getFloatFrequencyData(a) { a.set(fastDb.subarray(tick * NF, (tick + 1) * NF)); },
  getByteTimeDomainData(a) { a.set(timeByte.subarray(tick * NT, (tick + 1) * NT)); },
};
an.slow = { getByteFrequencyData(a) { a.set(slowByte.subarray(tick * NS, (tick + 1) * NS)); } };
an.freq = new Uint8Array(NF);
an.db = new Float32Array(NF);
an.sfreq = new Uint8Array(NS);
an.time = new Uint8Array(NT);
an.timer = 1;
const music = A.LiveMusic(an);

const trace = [];
const frames = fs.openSync(job.frames_out, 'w');
const out = new Float32Array(h.n * 3);
const res = new Float32Array(h.n * 3);
const guard = new G.PowerGuard(d.power);
const inst = {};
let cue = 0;
let nextFrame = 0;
for (tick = 0; tick < ticks; tick++) {
  const now = tick * 0.02;
  an.ctx.currentTime = now;
  const before = an.onsets;
  an.sample();
  // the same threshold _beats just used
  const hist = an._fluxHist, n = Math.min(an._fluxI, hist.length);
  let mean = 0, sd = 0;
  for (let i = 0; i < n; i++) mean += hist[i];
  mean /= Math.max(n, 1);
  for (let i = 0; i < n; i++) sd += (hist[i] - mean) * (hist[i] - mean);
  sd = Math.sqrt(sd / Math.max(n, 1));
  trace.push({
    t: now, level: an.level, rawDb: an.rawDb, lo: an._gain.lo, hi: an._gain.hi, flux: an.flux,
    thr: Math.max(mean + 1.4 * sd, 0.4), onset: an.onsets > before, bpm: an.bpm,
    pitch: an.pitch, centroid: an.centroid, b: Object.assign({}, an.b3), p: Object.assign({}, an.p3),
    phase: music.beatPhase(now),
  });
  // frames at 30 fps; the preset schedule comes from livefilm.py
  while (nextFrame / job.fps <= now) {
    const t = nextFrame / job.fps;
    while (cue + 1 < job.presets.length && job.presets[cue + 1].at <= t) cue++;
    const P = job.presets[cue];
    const k = P.name;
    if (!inst[k]) inst[k] = E.make(P.name, P.params || {}, h, d.fonts);
    out.fill(0);
    inst[k].render(h, t, music, out);
    guard.apply(out, res, t);
    fs.writeSync(frames, Buffer.from(res.buffer, res.byteOffset, res.byteLength));
    nextFrame++;
  }
}
fs.closeSync(frames);
fs.writeFileSync(job.trace_out, JSON.stringify(trace));
console.log('ticks', ticks, 'frames', nextFrame, 'onsets', an.onsets, 'bpm', an.bpm.toFixed(2));
