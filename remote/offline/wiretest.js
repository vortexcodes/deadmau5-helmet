// wiretest.js -- send frames under node so test_mau5.py can decode them
// with the controller's own parser and compare.  Reads
// {count, strips, frames:[base64 uint8 rgb]} and writes the segment
// layout the player asks for, then for each frame the websocket
// messages the player actually sent -- in order, deltas and all, the
// way one controller receives them, with each frame's pong answered
// before the next -- and the whole-frame POST body it would send
// instead if there were no socket.
'use strict';
const W = require('./wire.js');

let raw = '';
process.stdin.setEncoding('utf8');
process.stdin.on('data', c => { raw += c; });
process.stdin.on('end', () => {
  const job = JSON.parse(raw);
  const link = new W.Link({ count: job.count, strips: job.strips || [], deadmanMins: 0 });
  const sent = [];
  link.ws = { readyState: 1, bufferedAmount: 0, send: (m) => sent.push(m) };
  link.dirty();
  const frames = [];
  for (const b64 of job.frames) {
    const cur = new Uint8Array(Buffer.from(b64, 'base64'));
    sent.length = 0;
    const busyBefore = link.busy(performance.now());
    const r = link.send(cur);
    const busyAfter = link.busy(performance.now());
    link._pong();                             // the controller's pong
    const http = '{"seg":[' + link.frags(cur, true).map(x => x[1]).join(',') + ']}';
    frames.push({ ws: sent.slice(), ret: r, http: http, busyBefore: busyBefore, busyAfter: busyAfter });
  }
  // Three frames may be on their way at once, and no more.
  const d = new W.Link({ count: job.count, strips: job.strips || [], deadmanMins: 0 });
  d.ws = { readyState: 1, bufferedAmount: 0, send: () => {} };
  const depth = [];
  for (const b64 of job.frames.slice(0, 4)) {
    const cur = new Uint8Array(Buffer.from(b64, 'base64'));
    cur[0] ^= 1;                              // make every frame differ
    depth.push({ busy: d.busy(performance.now()), ret: d.send(cur) });
  }
  // Hand back only to a preset the controller has: loading a missing
  // one is a no-op that leaves the helmet lit.
  const hand = {};
  link.standby = 1;
  link.presets = new Set();
  hand.missing = link.canHandBack();
  link.presets = new Set(['1']);
  hand.present = link.canHandBack();
  link.standby = null;
  hand.notWanted = link.canHandBack();
  process.stdout.write(JSON.stringify({
    layout: link.segLayout(), frames: frames, pad: W.PAD, handBack: hand,
    depth: depth, depthLimit: W.DEPTH, filler: W.FILLER.length,
  }));
});
