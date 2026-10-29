// wire.js -- getting pixels from a phone into the controller.
//
// The Mac sends DDP: one UDP datagram, 1866 bytes, no reply, 40 fps.
// A browser cannot open a UDP socket, so none of that is available
// here and the frames have to go through WLED's own JSON API, which
// is a different animal in three ways worth knowing before reading
// the code.
//
//   It is text.  A frame is a list of "RRGGBB" strings, so the wire
//   cost depends on how much of the frame changed; only what changed
//   is sent, and runs of one colour collapse to a range.
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
// So: one message per frame, always whole, and the transport is
// chosen by how big the frame turned out.  Fifteen of the 37 presets
// encode small enough for the WebSocket, where frames apply
// correctly at 60 fps; the rest go by POST at about ten.  Quantising
// colour to force the rest under the limit was measured too -- it
// buys four presets at a visible cost, and was not taken.
const RUN_MIN = 3;            // below this a range costs more than it saves

// Measured boundary is 1428; the margin is for the index digits at
// the end of a long chain and for a firmware with a smaller MSS.
const WS_LIMIT = 1400;

function hexAt(buf, i) {
  return HEX[buf[i * 3]] + HEX[buf[i * 3 + 1]] + HEX[buf[i * 3 + 2]];
}

// Black is never sent.  The write blanks the segment first, so an
// LED nobody mentions is already off -- the firmware behaviour that
// made deltas impossible pays for itself here.  Worth 0 to 49% of a
// frame depending on how much of the helmet is dark, and it moves
// alignbar, eyes, pinwheel and text onto the websocket, where they
// run at 60 fps instead of ten.
// Black need not be sent: the write blanks the segment, so an LED
// nobody mentions is already off.  Worth up to half a frame, and it
// moves four more presets onto the websocket.
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

function bodyFor(entries) {
  return JSON.stringify({ seg: { id: 0, i: flatten(entries) } });
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
    // WLED parses a message into one fixed buffer and ignores
    // anything that will not fit.  24 kB is the ESP32 figure and 10 kB
    // the ESP8266 one; 3 kB leaves room for both and for whatever a
    // future build decides, at the cost of an extra message on the
    // handful of frames that are bigger than that.
    this.wsLimit = opts.wsLimit || WS_LIMIT;
    this.ws = null;
    this.inflight = 0;
    // Measured on the helmet: 7.3 whole frames a second over one
    // connection, 9.7 over two, 10.3 over three and worse after that.
    // Two is most of the gain, and since every frame is whole the
    // worst a reordering can do is leave one 100 ms stale.
    this.maxInflight = opts.maxInflight || 2;
    this.path = '-';
    // Which WLED preset to hand back to when the page lets go.  0 or
    // null means switch off instead.
    this.standby = opts.standby === undefined ? null : opts.standby;
    // A WebSocket gives no backpressure worth the name: bufferedAmount
    // only rises once the far end's TCP window closes, which is long
    // after an ESP32 has stopped keeping up.  Where a build answers
    // every message, those arrivals are an acknowledgement in
    // everything but name and counting them paces the sender
    // properly.
    //
    // Whether this build is one of those is decided by counting, not
    // by seeing one arrive.  WLED answers a plain state post with the
    // whole new state, which is where the idea came from, and answers
    // an `i` write with nothing: measured on the helmet's own
    // controller, 665 pixel messages drew 4 kB back, about six bytes
    // each.  Treating that trickle as a credit window left two
    // messages permanently outstanding and pinned the player at 4 fps
    // against a controller that swallows 165 messages a second.  So
    // the ratio has to hold up before the window is believed.
    this.pending = 0;
    this.acks = 0;
    this.sent = 0; this.bytes = 0; this.failed = 0;
    this.rtt = 0;
    this.frozen = false;
    // No resync timer any more, and nothing to resync.  Every frame
    // carries the whole helmet, so a message the firmware drops costs
    // one frame and the next one is correct again -- there is no
    // belief about the controller's state left to go stale.
    this.deadmanMins = opts.deadmanMins === undefined ? 1 : opts.deadmanMins;
    this._lastDeadman = 0;
    this.onstatus = opts.onstatus || function () {};
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
        ws.onmessage = () => {
          this.acks++;
          if (this.pending > 0) this.pending--;
        };
        ws.onclose = () => { if (this.ws === ws) this.ws = null; };
        ws.onerror = () => { if (this.ws === ws) this.ws = null; };
        resolve(true);
      };
      ws.onerror = () => { clearTimeout(giveUp); resolve(false); };
    });
  }

  async hello() {
    const info = await this.getJSON('/json/info');
    const state = await this.getJSON('/json/state');
    const leds = (info.leds || {});
    const seg = (state.seg || []).find(s => s.id === 0) || (state.seg || [])[0];
    const covered = seg ? (seg.stop - seg.start) : 0;
    return {
      name: info.name, ver: info.ver, arch: info.arch,
      count: leds.count | 0, maxpwr: leds.maxpwr,
      segStart: seg ? seg.start : null, segStop: seg ? seg.stop : null,
      covers: covered >= (leds.count | 0) && (seg ? seg.start === 0 : false),
      ws: await this.openSocket(),
    };
  }

  // Take the segment: solid effect, no transition, frozen so nothing
  // the controller runs on its own overwrites what we send.
  // Is this build answering often enough for its answers to be a
  // credit window?  Below half a reply per message it is not, and
  // `pending` is cleared so a trickle of late replies cannot leave
  // the sender permanently blocked.
  paceByAcks() {
    if (this.sent < 12) return false;
    if (this.acks > this.sent * 0.5) return true;
    this.pending = 0;
    return false;
  }

  async begin(bri) {
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
      seg: [{ id: 0, fx: 0, sx: 0, ix: 0, frz: true }],
    });
    await this.armDeadman(true);
    // Freeze is what stops the running effect painting over the
    // frames, and it arrived in WLED 0.13.  An older build takes the
    // pixels and then overwrites them a third of a second later,
    // which looks like a flicker nobody can explain, so the state is
    // read back and the answer reported rather than assumed.
    try {
      const st = await this.getJSON('/json/state');
      const seg = (st.seg || []).find(s => s.id === 0) || (st.seg || [])[0];
      this.frozen = !!(seg && seg.frz);
    } catch (e) {
      this.frozen = false;
    }
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

  // Hand the segment back and leave the helmet dark.  Called on stop,
  // on pagehide and on the way out of an error -- cheap, idempotent,
  // and the difference between "it went off" and "it stayed on all
  // night at a show".
  async release() {
    this.frozen = false;
    // Two ways to let go, and the default is not "off".
    //
    // Off was the original, and it is what made people think the
    // helmet had broken: close the page, or lock the phone, and the
    // thing goes dark.  Handing back to one of WLED's own presets
    // instead leaves it lit and animating with nothing driving it --
    // no phone, no laptop, no network -- and the brightness limiter
    // does cover that path, unlike the player's.
    const body = JSON.stringify(
      this.standby
        ? { ps: this.standby, nl: { on: false }, seg: [{ id: 0, frz: false }] }
        : { on: false, nl: { on: false }, seg: [{ id: 0, frz: false }] });
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

  send(frame) {
    const n = this.count, perm = this.perm, tmp = this._tmp;
    for (let i = 0; i < n; i++) {
      const b = i * 3;
      tmp[b] = frame[b + perm[b]];
      tmp[b + 1] = frame[b + perm[b + 1]];
      tmp[b + 2] = frame[b + perm[b + 2]];
    }
    const items = encode(tmp, n);
    // A frame with nothing lit encodes to nothing, and an empty `i`
    // is a no-op that would leave the last frame burning.  One range
    // says "all of it, off".
    const body = items.length ? bodyFor(items)
      : JSON.stringify({ seg: { id: 0, i: [0, n, '000000'] } });
    const now = performance.now();

    if (this.ws && this.ws.readyState === 1 && body.length <= this.wsLimit) {
      if (this.ws.bufferedAmount > this.wsLimit * 2) { this.failed++; return -1; }
      // Two messages outstanding is one in the controller and one on
      // its way; a third would only add latency nobody asked for.
      if (this.paceByAcks() && this.pending >= 2) { this.failed++; return -1; }
      this.ws.send(body);
      this.pending++;
      this.path = 'ws';
      this.sent++; this.bytes += body.length;
      this.rtt = this.rtt * 0.8 + (performance.now() - now) * 0.2;
      this.armDeadman(false);
      return body.length;
    }

    // Too big for a WebSocket message, or there is no socket.  One
    // POST, the whole frame, one at a time: a second request in
    // flight could land out of order, and since every frame is whole
    // that would show an older one.
    if (this.inflight >= this.maxInflight) { this.failed++; return -1; }
    this.inflight++;
    this.path = 'http';
    (async () => {
      try {
        await fetch(this.url('/json/state'), {
          method: 'POST', cache: 'no-store',
          headers: this.hdrs({ 'Content-Type': 'application/json' }),
          body: body,
        });
        this.sent++; this.bytes += body.length;
        this.rtt = this.rtt * 0.8 + (performance.now() - now) * 0.2;
        this.armDeadman(false);
      } catch (e) {
        this.failed++;
        this.onstatus({ error: String(e.message || e) });
      } finally {
        this.inflight--;
      }
    })();
    return body.length;
  }
}

const api = { Link, encode, flatten, bodyFor, makePerm, ORDERS, WS_LIMIT };
root.MAU5 = Object.assign(root.MAU5 || {}, api);
if (typeof module !== 'undefined' && module.exports) module.exports = api;

})(typeof globalThis !== 'undefined' ? globalThis : this);
