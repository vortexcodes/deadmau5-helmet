// Every show, end to end on the phone's own code, through the phone's own power guard, one after
// another as Play Music plays them: any exception, how long a frame takes, how hot the helmet gets.
'use strict';
const fs = require('fs'), path = require('path');
const DIR = '/Users/jones/deadmau5 app/remote/offline';
global.window = global;
const E = require(DIR + '/engine.js');
const G = require(DIR + '/guard.js');
const Dr = require(DIR + '/drive.js');
const S = require(DIR + '/show.js');
const D = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const FPS = +(process.argv[3] || 10);
const dec = (b64, C) => { const bin = Buffer.from(b64, 'base64'); return new C(bin.buffer.slice(bin.byteOffset, bin.byteOffset + bin.byteLength)); };
const geo = { n: D.n, regions: D.regions };
for (const k of Object.keys(D.f32)) geo[k] = dec(D.f32[k], Float32Array);
for (const k of Object.keys(D.i16)) geo[k] = dec(D.i16[k], Int16Array);
const h = E.makeHelmet(geo);
const guard = new G.PowerGuard(D.power);
const frame = new Float32Array(h.n * 3);
const order = (D.playlist || []).filter(n => D.shows[n]);
for (const n of Object.keys(D.shows)) if (order.indexOf(n) < 0) order.push(n);
let clock = 0, peakAll = 0, totalS = 0, fails = 0;
console.log('song                                           dur   mean W  peak mA  heat start>end  dimmed%  dark%  ms p50 p99  scenes');
for (const name of order) {
  const show = D.shows[name];
  const p = new S.ShowPlayer(show, h, D);
  let drive = null;
  const f = (D.drive[name] || '').split('?')[0];
  if (f) {
    const b = fs.readFileSync(path.join('/Users/jones/deadmau5 app/data/offline', f));
    drive = new Dr.TrackDrive(b.buffer.slice(b.byteOffset, b.byteOffset + b.byteLength));
  }
  const ms = [];
  let w = 0, peak = 0, dim = 0, dark = 0, n = 0, h0 = null, h1 = 0;
  const hadScenes = !!p.scenes;
  for (let t = 0; t < show.duration; t += 1 / FPS) {
    const t0 = process.hrtime.bigint();
    try {
      p.frame(t, drive, frame);
    } catch (e) { fails++; console.log('  EXCEPTION', name, t.toFixed(2), e.message); break; }
    const g = p.gain === undefined ? 1 : p.gain;
    const rep = guard.apply(frame, frame, clock, g);
    ms.push(Number(process.hrtime.bigint() - t0) / 1e6);
    clock += 1 / FPS;
    w += rep.watts; peak = Math.max(peak, rep.total_ma); n++;
    const th = rep.thermal;
    if (th) {
      if (h0 === null) h0 = th.full_pct;
      h1 = th.full_pct; peakAll = Math.max(peakAll, th.full_pct);
      if (th.allowance_w < th.top_w - 0.01) dim++;
    }
    let lit = 0; for (let i = 0; i < frame.length; i++) if (frame[i] > 8) { lit = 1; break; }
    if (!lit) dark++;
  }
  if (hadScenes && !p.scenes) { fails++; console.log('  FELL BACK TO CUES', name); }
  ms.sort((a, b) => a - b);
  totalS += show.duration;
  clock += 1;  // the dark moment between songs
  console.log(name.slice(0, 44).padEnd(44), String(Math.round(show.duration)).padStart(5), (w / n).toFixed(1).padStart(8), String(Math.round(peak)).padStart(8),
    (h0 || 0).toFixed(0).padStart(6) + '>' + h1.toFixed(0).padEnd(4), (100 * dim / n).toFixed(0).padStart(8), (100 * dark / n).toFixed(0).padStart(6), ms[ms.length >> 1].toFixed(2).padStart(7), ms[Math.floor(ms.length * 0.99)].toFixed(2).padStart(6), hadScenes ? 'scenes' : 'CUES ONLY');
}
console.log('total %d min; peak heat %d%%; failures %d', totalS / 60, peakAll, fails);
