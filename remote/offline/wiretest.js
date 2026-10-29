// wiretest.js -- encode frames under node so test_mau5.py can decode
// them with the controller's own parser and compare.  Reads
// {count, strips, frames:[base64 uint8 rgb]} and writes, for each
// frame, the single JSON body the player would send.
'use strict';
const W = require('./wire.js');

let raw = '';
process.stdin.setEncoding('utf8');
process.stdin.on('data', c => { raw += c; });
process.stdin.on('end', () => {
  const job = JSON.parse(raw);
  const n = job.count;
  const link = new W.Link({ count: n, strips: job.strips || [] });
  const out = [];
  for (const b64 of job.frames) {
    const cur = new Uint8Array(Buffer.from(b64, 'base64'));
    const permed = new Uint8Array(n * 3);
    for (let i = 0; i < n; i++) {
      const b = i * 3;
      permed[b] = cur[b + link.perm[b]];
      permed[b + 1] = cur[b + link.perm[b + 1]];
      permed[b + 2] = cur[b + link.perm[b + 2]];
    }
    out.push(W.bodyFor(W.encode(permed, n)));
  }
  process.stdout.write(JSON.stringify({ bodies: out, wsLimit: W.WS_LIMIT }));
});
