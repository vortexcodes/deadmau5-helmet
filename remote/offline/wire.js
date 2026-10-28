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
// `prev` is the frame the controller is already showing; null means
// nothing is known about it and the whole frame goes.
//
// encode() returns entries rather than the flat array, because the
// flat array cannot be split safely without parsing it back -- and
// splitting it is not optional, since a message over the firmware's
// JSON buffer is dropped without a word.
const RUN_MIN = 3;            // below this a range costs more than it saves

function same(a, b, i) {
  return a[i * 3] === b[i * 3] && a[i * 3 + 1] === b[i * 3 + 1]
      && a[i * 3 + 2] === b[i * 3 + 2];
}

function hexAt(buf, i) {
  return HEX[buf[i * 3]] + HEX[buf[i * 3 + 1]] + HEX[buf[i * 3 + 2]];
}

function encode(cur, prev, count) {
  const out = [];
  let i = 0;
  while (i < count) {
    if (prev && same(cur, prev, i)) { i++; continue; }
    let end = i;
    while (end < count && !(prev && same(cur, prev, end))) end++;
    let j = i;
    let seq = null;                       // the run of singles being built
    while (j < end) {
      let k = j + 1;
      while (k < end && cur[k * 3] === cur[j * 3]
             && cur[k * 3 + 1] === cur[j * 3 + 1]
             && cur[k * 3 + 2] === cur[j * 3 + 2]) k++;
      if (k - j >= RUN_MIN) {
        seq = null;
        out.push({ a: j, b: k, c: hexAt(cur, j) });
      } else {
        if (!seq) { seq = { a: j, cols: [] }; out.push(seq); }
        for (let q = j; q < k; q++) seq.cols.push(hexAt(cur, q));
      }
      j = k;
    }
    i = end;
  }
  return out;
}

// What one entry costs inside the `i` array, counted exactly: every
// token carries its own comma, and the envelope is a known constant.
const ENVELOPE = '{"seg":{"id":0,"i":[]}}'.length;

function numCost(n) { return String(n).length + 1; }
const COL_COST = 9;                        // "RRGGBB" plus a comma

// Split entries into messages no longer than `maxBody` characters.
// Splitting is free: the segment is frozen, so the parts accumulate,
// and a range or a run of singles both divide cleanly on any index.
function pack(entries, maxBody) {
  const room = Math.max(64, maxBody - ENVELOPE);
  const out = [];
  let part = [], size = 0;
  const flush = () => { if (part.length) { out.push(part); part = []; size = 0; } };
  for (const e of entries) {
    if (e.cols) {
      let at = e.a, q = 0;
      while (q < e.cols.length) {
        const head = numCost(at);
        if (size + head + COL_COST > room) flush();
        let take = 0;
        let budget = room - size - head;
        while (q + take < e.cols.length && budget >= COL_COST) {
          budget -= COL_COST; take++;
        }
        part.push(at);
        for (let z = 0; z < take; z++) part.push(e.cols[q + z]);
        size += head + take * COL_COST;
        q += take; at += take;
        if (q < e.cols.length) flush();
      }
    } else {
      let a = e.a;
      while (a < e.b) {
        const cost = numCost(a) + numCost(e.b) + COL_COST;
        if (size + cost > room) {
          // a single range can outgrow an empty message only if the
          // room is absurd, so splitting it in half always terminates
          if (!part.length) {
            const mid = a + Math.max(1, Math.floor((e.b - a) / 2));
            part.push(a, mid, e.c);
            size += numCost(a) + numCost(mid) + COL_COST;
            a = mid;
            flush();
            continue;
          }
          flush();
          continue;
        }
        part.push(a, e.b, e.c);
        size += cost;
        a = e.b;
      }
    }
  }
  flush();
  return out;
}

// ----------------------------------------------------------------------
// the link
// ----------------------------------------------------------------------
class Link {
  constructor(opts) {
    opts = opts || {};
    this.origin = opts.origin || '';          // '' = same host as the page
    this.count = opts.count | 0;
    this.perm = makePerm(this.count, opts.strips);
    // WLED parses a message into one fixed buffer and ignores
    // anything that will not fit.  24 kB is the ESP32 figure and 10 kB
    // the ESP8266 one; 3 kB leaves room for both and for whatever a
    // future build decides, at the cost of an extra message on the
    // handful of frames that are bigger than that.
    this.maxBody = opts.maxBody || 3000;
    this.ws = null;
    this.prev = null;                          // what the controller shows
    this.inflight = 0;
    // A WebSocket gives no backpressure worth the name: bufferedAmount
    // only rises once the far end's TCP window closes, which is long
    // after an ESP32 has stopped keeping up.  WLED answers a state
    // message by broadcasting the new state back, so those arrivals
    // are an acknowledgement in everything but name, and counting
    // them paces the sender properly.  If none ever arrive -- a build
    // that does not echo -- the counter is abandoned and the timer
    // alone does the pacing.
    this.pending = 0;
    this.acks = 0;
    this.acked = null;                         // null = not yet known
    this.sent = 0; this.bytes = 0; this.failed = 0;
    this.rtt = 0;
    this.frozen = false;
    // Only what changed is sent, which means the player is carrying a
    // belief about what the controller is showing.  Nothing confirms
    // that belief: WLED answers an HTTP post before it has parsed the
    // body, and a WebSocket says nothing at all, so a message the
    // firmware dropped -- too big for its buffer, arrived fragmented,
    // lost in the air -- leaves a stale LED lit with no way to notice.
    // Sending the whole frame every couple of seconds costs one large
    // frame in fifty and makes every such divergence temporary.
    this.resyncMs = opts.resyncMs === undefined ? 2000 : opts.resyncMs;
    this._lastFull = 0;
    this.deadmanMins = opts.deadmanMins === undefined ? 1 : opts.deadmanMins;
    this._lastDeadman = 0;
    this.onstatus = opts.onstatus || function () {};
    this._opened = 0;
    this._tmp = new Uint8Array(this.count * 3);
  }

  url(path) { return this.origin + path; }

  async getJSON(path) {
    const r = await fetch(this.url(path), { cache: 'no-store' });
    if (!r.ok) throw new Error(path + ' -> ' + r.status);
    return r.json();
  }

  async postJSON(obj) {
    const r = await fetch(this.url('/json/state'), {
      method: 'POST', cache: 'no-store',
      headers: { 'Content-Type': 'application/json' },
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
          this.acked = true;
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
  async begin(bri) {
    await this.postJSON({
      on: true, bri: bri === undefined ? 255 : bri,
      transition: 0, tt: 0,
      seg: [{ id: 0, fx: 0, sx: 0, ix: 0, frz: true }],
    });
    this.prev = null;
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
    this.prev = null;
    const body = JSON.stringify({ on: false, nl: { on: false },
                                  seg: [{ id: 0, frz: false }] });
    // sendBeacon survives the page going away, which fetch does not.
    if (navigator.sendBeacon) {
      try {
        navigator.sendBeacon(this.url('/json/state'),
                             new Blob([body], { type: 'application/json' }));
        return;
      } catch (e) { /* fall through */ }
    }
    try { await this.postJSON(JSON.parse(body)); } catch (e) {}
  }

  // `frame` is the guard's output in true RGB.  Returns the number of
  // characters sent, or -1 if the link was too busy to take it.
  send(frame) {
    const n = this.count, perm = this.perm, tmp = this._tmp;
    for (let i = 0; i < n; i++) {
      const b = i * 3;
      tmp[b] = frame[b + perm[b]];
      tmp[b + 1] = frame[b + perm[b + 1]];
      tmp[b + 2] = frame[b + perm[b + 2]];
    }
    const now = performance.now();
    if (this.resyncMs && now - this._lastFull > this.resyncMs) {
      this._lastFull = now;
      this.prev = null;
    }
    const items = encode(tmp, this.prev, n);
    if (!items.length) return 0;
    const parts = pack(items, this.maxBody);
    const t0 = now;

    if (this.ws && this.ws.readyState === 1) {
      if (this.ws.bufferedAmount > this.maxBody * 2) { this.failed++; return -1; }
      // Two messages outstanding is one in the controller and one on
      // its way; a third would only add latency nobody asked for.
      if (this.acked && this.pending >= 2) { this.failed++; return -1; }
      let chars = 0;
      for (const p of parts) {
        const s = JSON.stringify({ seg: { id: 0, i: p } });
        this.ws.send(s);
        chars += s.length;
        this.pending++;
      }
      // Give a quiet build a second to prove it never echoes, then
      // stop waiting for acknowledgements that are not coming.
      if (this.acked === null && now - this._opened > 1000) this.acked = false;
      this._keep(tmp);
      this.sent++; this.bytes += chars;
      this.rtt = this.rtt * 0.8 + (performance.now() - t0) * 0.2;
      this.armDeadman(false);
      return chars;
    }

    if (this.inflight) { this.failed++; return -1; }
    this.inflight = 1;
    let chars = 0;
    const bodies = parts.map(p => JSON.stringify({ seg: { id: 0, i: p } }));
    for (const b of bodies) chars += b.length;
    (async () => {
      try {
        for (const b of bodies) {
          await fetch(this.url('/json/state'), {
            method: 'POST', cache: 'no-store',
            headers: { 'Content-Type': 'application/json' }, body: b,
          });
        }
        this._keep(tmp);
        this.sent++; this.bytes += chars;
        this.rtt = this.rtt * 0.8 + (performance.now() - t0) * 0.2;
        this.armDeadman(false);
      } catch (e) {
        this.failed++;
        this.prev = null;             // resync: assume it shows nothing
        this.onstatus({ error: String(e.message || e) });
      } finally {
        this.inflight = 0;
      }
    })();
    return chars;
  }

  _keep(tmp) {
    if (!this.prev || this.prev.length !== tmp.length) this.prev = new Uint8Array(tmp.length);
    this.prev.set(tmp);
  }
}

const api = { Link, encode, pack, makePerm, ORDERS, ENVELOPE };
root.MAU5 = Object.assign(root.MAU5 || {}, api);
if (typeof module !== 'undefined' && module.exports) module.exports = api;

})(typeof globalThis !== 'undefined' ? globalThis : this);
