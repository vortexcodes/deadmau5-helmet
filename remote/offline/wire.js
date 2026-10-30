// wire.js -- getting pixels from a phone into the controller.
//
// The Mac sends DDP: one UDP datagram, 1866 bytes, no reply, 40 fps.
// A browser cannot open a UDP socket, so none of that is available
// here and the frames have to go through WLED's own JSON API, which
// is a different animal in three ways worth knowing before reading
// the code.
//
//   It is text.  A frame is a list of "RRGGBB" strings, so the wire
//   cost depends on what the frame looks like: runs of one colour
//   collapse to a range, black is not sent at all, and a stretch of
//   the chain that has not changed is not sent either.
//
//   It latches.  Sending `i` puts the segment in WLED's freeze state,
//   where the running effect stops overwriting the pixels -- which is
//   what makes streaming possible at all, and also means the last
//   frame stays lit forever if the phone goes away.  Hence stop(),
//   the pagehide handler and the dead man below.
//
//   It can say no.  An ESP32 parsing JSON is the slow part of this
//   system, not the air or the phone, and the only honest way to find
//   out how fast it is is to watch how fast it answers.  So the rate
//   adapts instead of being declared.

'use strict';

(function (root) {

const HEX = [];
for (let i = 0; i < 256; i++) HEX.push(i.toString(16).toUpperCase().padStart(2, '0'));

// ----------------------------------------------------------------------
// colour order
// ----------------------------------------------------------------------
// The ear rims are wired in a different order from the shell, and WLED
// has one bus setting for the whole chain, so the permutation happens
// here -- exactly as mau5wled.Pixels.apply_order does it on the Mac.
// Leave it out and the rims light green when asked for orange.
const ORDERS = {
  RGB: [0, 1, 2], RBG: [0, 2, 1], GRB: [1, 0, 2],
  GBR: [1, 2, 0], BRG: [2, 0, 1], BGR: [2, 1, 0],
};

function makePerm(count, strips) {
  const perm = new Uint8Array(count * 3);
  for (let i = 0; i < count; i++) { perm[i * 3] = 0; perm[i * 3 + 1] = 1; perm[i * 3 + 2] = 2; }
  for (const s of strips || []) {
    const o = ORDERS[String(s.order || 'RGB').toUpperCase()];
    if (!o) continue;
    const a = s.start | 0, b = Math.min(a + (s.count | 0), count);
    for (let i = a; i < b; i++) { perm[i * 3] = o[0]; perm[i * 3 + 1] = o[1]; perm[i * 3 + 2] = o[2]; }
  }
  return perm;
}

// ----------------------------------------------------------------------
// encoding
// ----------------------------------------------------------------------
// WLED's individual-LED syntax, used for everything it is worth:
//   [n, "RRGGBB"]            one LED
//   [n, "AABBCC", "DDEEFF"]  n and n+1, the index implied
//   [n, m, "RRGGBB"]         n up to but not including m
// so a changed stretch costs one index and six characters per LED,
// and a flat stretch costs two indices and six characters however
// long it is.
//
// There used to be a `prev` here, and deltas against it, and a
// packer that split a frame across as many messages as it needed.
// All three were wrong about this firmware, and none of it showed up
// against the simulator.  Measured on WLED 0.15.4, reading the strip
// back with mau5peek rather than trusting the send:
//
//   An `i` write BLANKS the rest of the segment.  Send LEDs 0-99 and
//   then 100-199 and only the second hundred is lit.  So a delta is
//   not an optimisation, it is a frame with the rest of the helmet
//   switched off, and splitting a frame across messages shows only
//   whichever part arrived last.
//
//   A WebSocket message over one TCP segment is dropped in silence.
//   1428 bytes lands, 1448 does not, and 1436 is the MSS.  Nothing is
//   reported: the send succeeds and the pixels never change.
//
//   An HTTP POST has no such limit -- a whole 622-LED frame goes in
//   one 6.2 kB request and arrives exactly -- but costs a round trip,
//   and the controller manages about 7 a second on one connection,
//   10 with three.
//
// So a frame cannot be one message.  Three more measurements on this
// controller decide what it is instead.
//
//   The blanking is per *segment*, not per strip.  With the chain cut
//   into segments, a write to segment 0 left segment 1 exactly as it
//   was, read back through the live preview.  So the chain is cut into
//   ten segments of about 62 LEDs -- short enough that two of them,
//   every LED a different colour, still fit one message -- and a frame
//   is as many messages as its segments need, several segments to a
//   message where they fit.  A segment that has not changed is not
//   sent at all: it keeps what it has, the one kind of delta this
//   firmware allows.
//
//   A message split across two TCP packets is refused ({"error":9}),
//   and back-to-back messages do get split: the ESP32 only opens its
//   window once it has parsed what it has, the backlog is repacked
//   into full segments, and a fifth of all messages straddled a
//   boundary.  Spacing them out did not help.  Padding every message
//   to exactly one segment did -- 1428 bytes and the 8-byte frame
//   header are the 1436-byte MSS, so however the stream is repacked
//   the boundaries fall between messages.  0 refused in 740.
//
//   And a socket hides a controller that has fallen behind.  It
//   digests about 120 kB of pixel JSON a second; the operating system
//   takes a hundred kilobytes more before bufferedAmount moves, so a
//   player sending 30 fps of whole frames had the helmet 3.4 seconds
//   behind the music without dropping a frame.  What paces it instead
//   is the firmware's own heartbeat: 'p' after the last message of a
//   frame, and nothing more until 'pong'.  Messages are handled in
//   order, so the pong means the frame is on the strip -- and sent
//   last, the short 'p' cannot break the padding.
//
// Measured on the helmet, against 8-13 fps by POST for 20 of the 35
// presets: frames that change the whole helmet run at about 15 fps,
// each on the strip about 60 ms after it was drawn, and frames that
// change two segments of five at 28, with nothing queueing behind
// them.  What is left is the JSON itself -- the controller takes 190
// messages a second it can discard but only 80 it must parse -- and
// binary frames would close that: WLED 16 takes DDP over this socket.
const RUN_MIN = 3;            // below this a range costs more than it saves

// Two worst-case segments must fit one padded message: nine
// characters an LED (six hex, two quotes, a comma) and about thirty
// for each segment's wrapper.  64 is 1180 at most for the pair.
const SEG_MAX = 64;

// Every websocket message is padded to this, so that with its frame
// header it is exactly one 1436-byte TCP segment.  It is also the
// largest message measured to land: 1428 bytes arrives, 1448 never does.
const PAD = 1428;

// How often every segment is sent whether it changed or not.
const KEYFRAME_MS = 1000;

// Frames allowed on their way at once.  One was the obvious choice and
// it tied the frame rate to the round trip: a laptop gets its pong in
// 20 ms, but a phone on WiFi dozes between packets and takes 100 or
// more, and with a 100 ms return path one frame in flight gave plasma
// 5 fps and eyes 7.5.  Three gave 15.5 and 20.5, and 30 for eyes at
// laptop speed, with the queue still no deeper than three frames.
const DEPTH = 2;

// Sent with each ping, so that the ping and this together are exactly
// one 1436-byte segment (7 bytes for 'p', 8 of header and 1421 of
// spaces for this) and the padding of whatever follows them survives.
// The firmware parses it as JSON, fails on the first character it
// cannot use and answers nothing.
const FILLER = ' '.repeat(1421);

// A frame whose pong has not come back by now is given up on, and the
// next frame goes whole.  With three in flight a lost pong only holds
// one of the three slots, so this can afford to be patient.
const PONG_TIMEOUT_MS = 1000;

// A POST that has not come back by now is not coming back.  Without a
// limit, two requests the controller never answered pinned the player
// at its in-flight ceiling and the helmet froze for good -- seen after
// about ninety seconds of a preset sweep, when the controller had also
// closed the websocket.
const POST_TIMEOUT_MS = 2500;
const REOPEN_MS = 3000;

// The chain cut into equal segments of at most SEG_MAX.
function layout(count, segMax) {
  const n = Math.max(1, Math.ceil(count / (segMax || SEG_MAX)));
  const out = [];
  for (let s = 0; s < n; s++) out.push([Math.round(s * count / n), Math.round((s + 1) * count / n)]);
  return out;
}

function hexAt(buf, i) {
  return HEX[buf[i * 3]] + HEX[buf[i * 3 + 1]] + HEX[buf[i * 3 + 2]];
}

// Black is never sent.  The write blanks the segment first, so an
// LED nobody mentions is already off -- the firmware behaviour that
// made whole-strip deltas impossible pays for itself here.  Worth 0
// to 49% of a frame depending on how much of the helmet is dark.
//
// Verified rather than assumed: four real show frames, from 24 to
// 565 entries, read back off the strip at 622 of 622 exact both
// with this on and with it off.
//
// It spent an hour switched off on the strength of measurements
// that were all wrong in the same way -- a browser tab left open on
// the player, quietly streaming its own show over every test write.
// Two independent "findings" came out of that, and both evaporated
// once the tab was closed.  The lesson is in mau5peek: check what
// else is talking to the controller before believing it.
const SKIP_BLACK = true;

function encode(cur, count) {
  const out = [];
  let j = 0, seq = null;
  while (j < count) {
    let k = j + 1;
    while (k < count && cur[k * 3] === cur[j * 3]
           && cur[k * 3 + 1] === cur[j * 3 + 1]
           && cur[k * 3 + 2] === cur[j * 3 + 2]) k++;
    if (SKIP_BLACK && cur[j * 3] === 0 && cur[j * 3 + 1] === 0
        && cur[j * 3 + 2] === 0) {
      seq = null;
      j = k;
      continue;
    }
    if (k - j >= RUN_MIN) {
      seq = null;
      out.push({ a: j, b: k, c: hexAt(cur, j) });
    } else {
      if (!seq) { seq = { a: j, cols: [] }; out.push(seq); }
      for (let q = j; q < k; q++) seq.cols.push(hexAt(cur, q));
    }
    j = k;
  }
  return out;
}

// The flat `i` array for one whole frame.
function flatten(entries) {
  const arr = [];
  for (const e of entries) {
    if (e.cols) { arr.push(e.a); for (const c of e.cols) arr.push(c); }
    else arr.push(e.a, e.b, e.c);
  }
  return arr;
}

// One segment's write: `{"id":s,"i":[...]}`.  A segment with nothing
// lit still has to be written, or it would keep its last frame, and a
// range of black says so in one entry.
function fragFor(id, entries, len) {
  return JSON.stringify({ id: id, i: entries.length ? flatten(entries) : [0, len, '000000'] });
}

// Segment writes into websocket messages: as many to a message as fit,
// every message padded to exactly `pad` bytes.
function pack(frags, pad) {
  const out = [];
  let cur = [];
  const close = () => {
    const m = '{"seg":[' + cur.join(',') + ']}';
    out.push(m + ' '.repeat(Math.max(0, pad - m.length)));
    cur = [];
  };
  let size = 0;
  for (const f of frags) {
    // the wrapper is 10 characters, and a comma between fragments
    if (cur.length && 10 + size + cur.length + f.length > pad) { close(); size = 0; }
    cur.push(f);
    size += f.length;
  }
  if (cur.length) close();
  return out;
}

function bodyFor(entries, id) {
  return JSON.stringify({ seg: { id: id | 0, i: flatten(entries) } });
}

// ----------------------------------------------------------------------
// the link
// ----------------------------------------------------------------------
class Link {
  constructor(opts) {
    opts = opts || {};
    // '' means the same host as the page, which is the normal case:
    // the controller serves the page.  Through mau5relay it is
    // '/helmet', and every request carries the relay's token, because
    // the relay is the only thing standing in front of a controller
    // that has no authentication of its own.
    this.origin = opts.origin || '';
    this.token = opts.token || '';
    this.headers = this.token ? { 'X-Mau5-Token': this.token } : {};
    this.count = opts.count | 0;
    this.perm = makePerm(this.count, opts.strips);
    this.pad = opts.pad || PAD;
    this.segs = layout(this.count, opts.segMax || SEG_MAX);
    // The last write sent for each segment, to skip the ones that
    // have not changed.  null means "unknown, send it".
    this.last = this.segs.map(() => null);
    this._keyAt = 0;
    this.ws = null;
    this.inflight = 0;
    // Measured on the helmet: 7.3 whole frames a second over one
    // connection, 9.7 over two, 10.3 over three and worse after that.
    // Two is most of the gain, and since every POST is a whole frame
    // the worst a reordering can do is leave one 100 ms stale.
    this.maxInflight = opts.maxInflight || 2;
    this.path = '-';
    // Which WLED preset to hand back to when the page lets go.  0 or
    // null means switch off instead.
    this.standby = opts.standby === undefined ? null : opts.standby;
    // How many LEDs the controller drives, which can be more than the
    // map has: one with nothing behind it is harmless.  Learnt in hello().
    this.ledCount = this.count;
    // The presets the controller has, learnt in hello().  Asking WLED to
    // load one that is not there does nothing at all.
    this.presets = new Set();
    this.streaming = false;
    this._reopenAt = 0;
    this._opening = false;
    // When each unacknowledged frame's 'p' went, oldest first.
    this.unacked = [];
    this.depth = opts.depth || DEPTH;
    // For testing a phone from a laptop: hold every pong this long.
    this.ackDelay = opts.ackDelay || 0;
    // How often the controller has been finishing frames, smoothed; the
    // player spaces its frames by this so they arrive evenly rather
    // than in bursts whenever a slot frees.
    this.paceMs = 0;
    this._lastPong = 0;
    this.sent = 0; this.bytes = 0; this.failed = 0; this.refused = 0;
    this.lost = 0; this.messages = 0;
    // How long a frame takes to reach the strip: send to pong, or a
    // POST's round trip.
    this.rtt = 0;
    this.frozen = false;
    this.deadmanMins = opts.deadmanMins === undefined ? 1 : opts.deadmanMins;
    this._lastDeadman = 0;
    this.onstatus = opts.onstatus || function () {};
    // Called when the controller has finished a frame, so a player
    // waiting on busy() can draw the next one at once, not at its next
    // timer tick.
    this.onready = opts.onready || function () {};
    this._opened = 0;
    this._tmp = new Uint8Array(this.count * 3);
  }

  url(path, withToken) {
    const u = this.origin + path;
    // sendBeacon cannot carry a header, and the release beacon is the
    // one request that absolutely must get through -- it is what
    // stops the helmet holding a frame for ever.  So that one puts
    // the token in the query, which the relay also accepts.
    if (withToken && this.token) {
      return u + (u.indexOf('?') < 0 ? '?' : '&') + 't='
        + encodeURIComponent(this.token);
    }
    return u;
  }

  hdrs(extra) { return Object.assign({}, this.headers, extra || {}); }

  async getJSON(path) {
    const r = await fetch(this.url(path),
                          { cache: 'no-store', headers: this.hdrs() });
    if (!r.ok) throw new Error(path + ' -> ' + r.status);
    return r.json();
  }

  async postJSON(obj) {
    const r = await fetch(this.url('/json/state'), {
      method: 'POST', cache: 'no-store',
      headers: this.hdrs({ 'Content-Type': 'application/json' }),
      body: JSON.stringify(obj),
    });
    if (!r.ok) throw new Error('state -> ' + r.status);
    return r.text();
  }

  // Forget what the controller is showing, so the next frame is sent
  // whole.  After a reconnect, a refusal, or a new layout.
  dirty() {
    this.last.fill(null);
    this._keyAt = 0;
  }

  // Open the WebSocket if the firmware has one.  It is worth the
  // trouble: an HTTP POST costs a request line, headers and a reply
  // the player throws away, every frame, and the ESP32 pays for all
  // of it.  Failure here is not an error -- it falls back.
  openSocket(timeoutMs) {
    // connect() runs at load and again on every start, and each call
    // used to leave another socket behind.
    if (this.ws && this.ws.readyState === 1) return Promise.resolve(true);
    return new Promise((resolve) => {
      let ws;
      try {
        const base = this.origin || (location.protocol + '//' + location.host);
        ws = new WebSocket(base.replace(/^http/, 'ws') + '/ws');
      } catch (e) { return resolve(false); }
      const giveUp = setTimeout(() => { try { ws.close(); } catch (e) {} resolve(false); },
                                timeoutMs || 2500);
      ws.onopen = () => {
        clearTimeout(giveUp);
        this.ws = ws;
        this._opened = performance.now();
        this.dirty();
        // A pixel write draws no answer.  What does arrive is the
        // state, now and then, and an error object when the firmware
        // could not take a message -- after which nobody knows what
        // that segment shows, so everything goes again.
        ws.onmessage = (e) => {
          this.messages++;
          if (e.data === 'pong') {
            if (this.ackDelay) setTimeout(() => this._pong(), this.ackDelay);
            else this._pong();
          } else if (typeof e.data === 'string' && e.data.length < 64
                     && e.data.indexOf('"error"') >= 0) {
            this.refused++;
            this.dirty();
          }
        };
        const gone = () => {
          if (this.ws === ws) { this.ws = null; this.unacked = []; this.dirty(); }
        };
        ws.onclose = gone;
        ws.onerror = gone;
        resolve(true);
      };
      ws.onerror = () => { clearTimeout(giveUp); resolve(false); };
    });
  }

  // A frame is on the strip: messages are handled in order, so the
  // pong answers the oldest frame still waiting.
  _pong() {
    if (!this.unacked.length) return;
    const now = performance.now();
    this.rtt = this.rtt * 0.8 + (now - this.unacked.shift()) * 0.2;
    if (this._lastPong) {
      const gap = Math.min(now - this._lastPong, 250);
      this.paceMs = this.paceMs ? this.paceMs * 0.85 + gap * 0.15 : gap;
    }
    this._lastPong = now;
    this.onready();
  }

  // The controller closes the socket now and then -- seen during a
  // long preset sweep -- and a player that never reopens it is a
  // player on HTTP at a third of the frame rate until it is reloaded.
  reopen(now) {
    if (!this.streaming || this._opening || now < this._reopenAt) return;
    this._reopenAt = now + REOPEN_MS;
    this._opening = true;
    this.openSocket(1500).then(() => { this._opening = false; },
                               () => { this._opening = false; });
  }

  async hello() {
    const info = await this.getJSON('/json/info');
    const state = await this.getJSON('/json/state');
    const leds = (info.leds || {});
    this.ledCount = Math.max(leds.count | 0, this.count);
    const segs = (state.seg || []).slice().sort((x, y) => x.start - y.start);
    // Do the segments between them reach every LED?  Whatever layout a
    // preset, or the last session, left behind, begin() replaces it --
    // this only reports what is there now.
    let reach = 0;
    for (const s of segs) if (s.start <= reach) reach = Math.max(reach, s.stop);
    try {
      const ps = await this.getJSON('/presets.json');
      this.presets = new Set(Object.keys(ps || {}).filter(k => k !== '0'
                                                          && Object.keys(ps[k] || {}).length));
    } catch (e) { this.presets = new Set(); }
    return {
      name: info.name, ver: info.ver, arch: info.arch,
      count: leds.count | 0, maxpwr: leds.maxpwr,
      segments: segs.length, reach: reach,
      covers: reach >= Math.min(leds.count | 0, this.count),
      presets: Array.from(this.presets),
      ws: await this.openSocket(),
    };
  }

  // Take the chain: one frozen segment per stretch of SEG_MAX, solid
  // effect, no transition, no grouping or mirroring left over from a
  // preset -- any of those would put every pixel somewhere else.
  segLayout(extraIds) {
    const seg = this.segs.map(([a, b], id) => ({
      id: id, start: a, stop: b, grp: 1, spc: 0, of: 0, rev: false, mi: false,
      fx: 0, sx: 0, ix: 0, frz: true, on: true, bri: 255,
    }));
    for (const id of extraIds || []) if (id >= this.segs.length) seg.push({ id: id, stop: 0 });
    return seg;
  }

  async begin(bri) {
    let ids = [];
    try { ids = ((await this.getJSON('/json/state')).seg || []).map(s => s.id); } catch (e) {}
    await this.postJSON({
      // live:false releases a realtime lock.  Posting live:true to
      // WLED locks realtime for 65 s, and the laptop's streamer does
      // exactly that -- so a helmet last driven over DDP ignores
      // every pixel this page sends for a minute after the laptop
      // goes away, which is precisely the moment somebody switches
      // to the phone and concludes offline mode is broken.
      on: true, live: false,
      bri: bri === undefined ? 255 : bri,
      transition: 0, tt: 0,
      seg: this.segLayout(ids),
    });
    await this.armDeadman(true);
    // Freeze is what stops the running effect painting over the
    // frames, and it arrived in WLED 0.13.  An older build takes the
    // pixels and then overwrites them a third of a second later,
    // which looks like a flicker nobody can explain -- and a build
    // that refused the layout would show each frame in the wrong
    // place.  So the state is read back and both are checked.
    try {
      const got = (await this.getJSON('/json/state')).seg || [];
      this.frozen = this.segs.every(([a, b], id) =>
        got.some(s => s.id === id && s.start === a && s.stop === b && s.frz));
    } catch (e) {
      this.frozen = false;
    }
    this.streaming = true;
    this.dirty();
    return this.frozen;
  }

  // The dead man.  Freeze latches, so a phone that is dropped, locked
  // or simply out of battery leaves the last frame lit indefinitely --
  // and the thermal budget assumes frames keep arriving to be rationed.
  // WLED's nightlight in "instant" mode holds brightness and then
  // switches off when it expires, so re-arming it a few times a minute
  // turns it into a dead man's handle: the helmet goes dark about a
  // minute after the phone stops talking, and never while it is.
  async armDeadman(force) {
    if (!this.deadmanMins) return;
    const now = Date.now();
    if (!force && now - this._lastDeadman < 20000) return;
    this._lastDeadman = now;
    try {
      await this.postJSON({ nl: { on: false } });
      await this.postJSON({ nl: { on: true, mode: 0, dur: this.deadmanMins, tbri: 0 } });
    } catch (e) { /* older firmware: the pagehide handler still covers it */ }
  }

  // Hand the chain back as one unfrozen segment and leave the helmet
  // dark.  Called on stop, on pagehide and on the way out of an error
  // -- cheap, idempotent, and the difference between "it went off"
  // and "it stayed on all night at a show".
  // Is there a preset to hand back to?
  canHandBack() {
    return !!this.standby && this.presets.has(String(this.standby));
  }

  async release() {
    this.frozen = false;
    this.streaming = false;
    const seg = [{ id: 0, start: 0, stop: this.ledCount, frz: false }]
      .concat(this.segs.slice(1).map((_, k) => ({ id: k + 1, stop: 0 })));
    // Two ways to let go, and the default is not "off".
    //
    // Off was the original, and it is what made people think the
    // helmet had broken: close the page, or lock the phone, and the
    // thing goes dark.  Handing back to one of WLED's own presets
    // instead leaves it lit and animating with nothing driving it --
    // no phone, no laptop, no network -- and the brightness limiter
    // does cover that path, unlike the player's.  The preset brings
    // its own segments if it saved any; if not, the one put back here.
    //
    // Only a preset that exists, though.  Loading a missing one is a
    // no-op, and the helmet then stayed on in whatever its segment last
    // held -- found on this controller, with no presets saved at all,
    // as solid orange at full brightness for as long as nobody noticed.
    const body = JSON.stringify(
      this.canHandBack()
        ? { ps: this.standby, nl: { on: false }, seg: seg }
        : { on: false, nl: { on: false }, seg: seg });
    // sendBeacon survives the page going away, which fetch does not.
    if (navigator.sendBeacon) {
      try {
        navigator.sendBeacon(this.url('/json/state', true),
                             new Blob([body], { type: 'application/json' }));
        return true;
      } catch (e) {}
    }
    try {
      await fetch(this.url('/json/state'), {
        method: 'POST', keepalive: true,
        headers: this.hdrs({ 'Content-Type': 'application/json' }),
        body: body,
      });
    } catch (e) {}
    return true;
  }

  // The writes one frame needs: [segment, fragment] for every segment
  // that differs from what was last sent, or every segment if `whole`.
  frags(frame, whole) {
    const n = this.count, perm = this.perm, tmp = this._tmp;
    for (let i = 0; i < n; i++) {
      const b = i * 3;
      tmp[b] = frame[b + perm[b]];
      tmp[b + 1] = frame[b + perm[b + 1]];
      tmp[b + 2] = frame[b + perm[b + 2]];
    }
    const out = [];
    for (let s = 0; s < this.segs.length; s++) {
      const [a, b] = this.segs[s];
      const f = fragFor(s, encode(tmp.subarray(a * 3, b * 3), b - a), b - a);
      if (whole || f !== this.last[s]) out.push([s, f]);
    }
    return out;
  }

  // Is the controller still busy with the last frame?  The player
  // draws nothing until it is not: a frame drawn now would only be
  // shown late.
  busy(now) {
    if (this.ws && this.ws.readyState === 1) {
      while (this.unacked.length && now - this.unacked[0] > PONG_TIMEOUT_MS) {
        this.unacked.shift();       // that pong never came: start again whole
        this.lost++;
        this.dirty();
      }
      return this.unacked.length >= this.depth;
    }
    return this.inflight >= this.maxInflight;
  }

  // Bytes sent; 0 when the helmet already shows this frame; -1 when
  // the controller was still busy and the frame was skipped.
  send(frame) {
    const now = performance.now();
    const ws = this.ws && this.ws.readyState === 1 ? this.ws : null;
    if (!ws) this.reopen(now);
    if (this.busy(now)) { this.failed++; return -1; }

    if (ws) {
      const key = now - this._keyAt >= KEYFRAME_MS;
      const todo = this.frags(frame, key);
      if (key) this._keyAt = now;
      if (!todo.length) return 0;
      let bytes = 0;
      for (const m of pack(todo.map(x => x[1]), this.pad)) {
        ws.send(m);
        bytes += m.length;
      }
      for (const [s, f] of todo) this.last[s] = f;
      ws.send('p');
      ws.send(FILLER);
      this.unacked.push(now);
      this.path = 'ws';
      this.sent++; this.bytes += bytes;
      this.armDeadman(false);
      return bytes;
    }

    // No socket.  One POST with every segment in it: two requests in
    // flight can land out of order, and a delta that overtook the
    // frame it was a delta of would leave its segment stale until it
    // next changed.  A whole frame overtaken costs one old frame.
    if (this.inflight >= this.maxInflight) { this.failed++; return -1; }
    const body = '{"seg":[' + this.frags(frame, true).map(x => x[1]).join(',') + ']}';
    this.inflight++;
    this.path = 'http';
    this.dirty();                 // the socket, when it is back, starts whole
    (async () => {
      const ctl = typeof AbortController === 'function' ? new AbortController() : null;
      const timer = ctl ? setTimeout(() => ctl.abort(), POST_TIMEOUT_MS) : null;
      try {
        await fetch(this.url('/json/state'), {
          method: 'POST', cache: 'no-store',
          headers: this.hdrs({ 'Content-Type': 'application/json' }),
          body: body, signal: ctl ? ctl.signal : undefined,
        });
        this.sent++; this.bytes += body.length;
        this.rtt = this.rtt * 0.8 + (performance.now() - now) * 0.2;
        this.armDeadman(false);
      } catch (e) {
        this.failed++;
        this.onstatus({ error: String(e.message || e) });
      } finally {
        if (timer) clearTimeout(timer);
        this.inflight--;
        this.onready();
      }
    })();
    return body.length;
  }
}

const api = { Link, encode, flatten, bodyFor, fragFor, pack, layout, makePerm, ORDERS,
              PAD, SEG_MAX, KEYFRAME_MS, DEPTH, FILLER };
root.MAU5 = Object.assign(root.MAU5 || {}, api);
if (typeof module !== 'undefined' && module.exports) module.exports = api;

})(typeof globalThis !== 'undefined' ? globalThis : this);
