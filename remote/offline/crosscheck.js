// crosscheck.js -- render presets under node, for test_mau5.py to diff
// against the Python.  Reads {data, jobs:[{preset, params, t}]} on
// stdin and writes the frames back as base64 float32, in order.
'use strict';

const E = require('./engine.js');
const G = require('./guard.js');

function decode(b64, Ctor) {
  const buf = Buffer.from(b64, 'base64');
  return new Ctor(buf.buffer, buf.byteOffset, buf.byteLength / Ctor.BYTES_PER_ELEMENT);
}

function helmetFrom(d) {
  const o = { n: d.n, regions: d.regions };
  for (const k of Object.keys(d.f32)) o[k] = decode(d.f32[k], Float32Array);
  for (const k of Object.keys(d.i16)) o[k] = decode(d.i16[k], Int16Array);
  return E.makeHelmet(o);
}

let raw = '';
process.stdin.setEncoding('utf8');
process.stdin.on('data', c => { raw += c; });
process.stdin.on('end', () => {
  const job = JSON.parse(raw);
  const h = helmetFrom(job.data);
  const fonts = job.data.fonts;
  const out = new Float32Array(h.n * 3);
  const res = [];
  let guard = null, inst = null, lastName = null, lastParams = null;
  for (const j of job.jobs) {
    if (j.reset || j.preset !== lastName ||
        JSON.stringify(j.params) !== lastParams) {
      inst = E.make(j.preset, j.params || {}, h, fonts);
      lastName = j.preset;
      lastParams = JSON.stringify(j.params);
    }
    out.fill(0);
    inst.render(h, j.t, null, out);
    let rep = null;
    if (j.guard) {
      if (!guard || j.reset) guard = new G.PowerGuard(job.data.power);
      rep = guard.apply(out, out, j.now === undefined ? j.t : j.now);
    }
    res.push({ f: Buffer.from(new Float32Array(out).buffer).toString('base64'),
               report: rep });
  }
  process.stdout.write(JSON.stringify(res));
});
