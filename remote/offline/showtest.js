// showtest.js -- render shows under node so test_mau5.py can compare
// them with mau5show.Player.  Reads {data, shows:[name], times:[t]}
// and writes, per show per time, the frame as a flat array.
'use strict';
const path = require('path');
global.window = global;
const E = require('./engine.js');
const S = require('./show.js');

let raw = '';
process.stdin.setEncoding('utf8');
process.stdin.on('data', c => { raw += c; });
process.stdin.on('end', () => {
  const job = JSON.parse(raw);
  const D = job.data;
  const dec = (b64, C) => {
    const bin = Buffer.from(b64, 'base64');
    return new C(bin.buffer, bin.byteOffset, bin.byteLength / C.BYTES_PER_ELEMENT);
  };
  const geo = { n: D.n, regions: D.regions };
  for (const k of Object.keys(D.f32)) geo[k] = dec(D.f32[k], Float32Array);
  for (const k of Object.keys(D.i16)) geo[k] = dec(D.i16[k], Int16Array);
  const h = E.makeHelmet(geo);

  // The same drive the Python side uses, written as pure functions of
  // t so neither implementation can have state the other does not.
  const music = {
    bands: true, bpm: 128.0, lock_conf: NaN,
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

  const out = {};
  const buf = new Float32Array(h.n * 3);
  for (const name of job.shows) {
    const p = new S.ShowPlayer(D.shows[name], h, D);
    const frames = [];
    for (const t of job.times) {
      p.frame(t, music, buf);
      frames.push(Array.from(buf, v => Math.round(v * 1000) / 1000));
    }
    out[name] = frames;
  }
  process.stdout.write(JSON.stringify(out));
});
