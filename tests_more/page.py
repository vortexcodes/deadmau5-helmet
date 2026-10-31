"""tests_more/page.py -- the offline page itself, run under node.

The rest of the suite checks what the page computes: presets, guard,
encoder.  None of it ran the page, which is where the failures that
cost a show were: a render loop that died on the first exception and
left the helmet frozen and then dark with the page saying 'stop';
following Spotify undoing the stop button and the stop-when-hidden;
late pongs credited to newer frames until the helmet trailed the music
for good; and a dead man that, once it had fired, nothing turned back
on.  So here every script the build inlines is run in the build's
order against a fake DOM and a fake controller that records what it
was sent, and the link on a clock the test owns.

Nothing here talks to a network: fetch is replaced in both harnesses.
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from test_mau5 import ok, eq, note, HERE  # noqa: E402

try:                        # notes print from the suite that is running
    import __main__
    note = getattr(__main__, "note", note)
except Exception:
    pass

OFFLINE = os.path.join(HERE, "remote", "offline")

# The page, every script the build inlines, against a fake DOM and a
# fake controller.  Reads the data bundle on stdin; argv[2] is
# remote/offline.
PAGE_JS = r'''// The offline page run under node: every script the build inlines, in
// the build's order, against a fake DOM and a fake controller that
// records what it was sent.  Reads the data bundle on stdin; argv[2] is
// remote/offline.  Writes one JSON object of observations.
'use strict';
const fs = require('fs');
const path = require('path');
const vm = require('vm');
const DIR = process.argv[2];

let raw = '';
process.stdin.setEncoding('utf8');
process.stdin.on('data', c => { raw += c; });
process.stdin.on('end', () => { main(JSON.parse(raw)).catch(e => {
  process.stdout.write(JSON.stringify({ crashed: String(e && e.stack || e) }));
  process.exit(0);
}); });

const sleep = (ms) => new Promise(r => setTimeout(r, ms));

// A browser tab survives an exception in a timer; the loop that threw
// does not.  So here: note it and carry on, as the page would.
const uncaught = [];
process.on('uncaughtException', e => uncaught.push(String(e && e.message || e)));
process.on('unhandledRejection', e => uncaught.push(String(e && e.message || e)));

function classList() {
  const s = new Set();
  return { add: c => s.add(c), remove: c => s.delete(c), contains: c => s.has(c),
           toggle: (c, on) => { if (on === undefined) on = !s.has(c); if (on) s.add(c); else s.delete(c); } };
}
const ctx2d = new Proxy({}, { get: (t, k) => (k in t ? t[k] : () => {}),
                              set: (t, k, v) => { t[k] = v; return true; } });
function element(tag, id) {
  return {
    tagName: String(tag || 'div').toUpperCase(), id: id || '', textContent: '',
    innerHTML: '', value: '', checked: false, disabled: false, style: {},
    className: '', dataset: {}, children: [], options: [], attrs: {},
    classList: classList(), clientWidth: 360, width: 0, height: 0,
    appendChild(c) { this.children.push(c); if (c.tagName === 'OPTION') this.options.push(c); return c; },
    setAttribute(k, v) { this.attrs[k] = v; }, addEventListener() {},
    getContext() { return ctx2d; }, click() { if (this.onclick) this.onclick({ target: this }); },
    play() { this.playing = true; return Promise.resolve(); }, pause() { this.playing = false; },
  };
}

async function main(data) {
  const byId = {};
  const document = {
    visibilityState: 'visible',
    body: element('body'),
    getElementById: (id) => byId[id] || (byId[id] = element('div', id)),
    createElement: (tag) => element(tag),
    querySelectorAll: () => [],
  };
  const store = new Map();
  const handlers = {};
  // ------------------------------------------------------------------
  // the controller, and Spotify
  // ------------------------------------------------------------------
  const log = [];                 // every POST to /json/state, in order
  let segs = [];
  let slow = 0;                   // ms before the controller answers
  let spotify = null;             // what currently-playing returns
  const reply = (obj, status) => ({
    ok: (status || 200) < 300, status: status || 200,
    headers: { get: () => null },
    json: async () => obj, text: async () => JSON.stringify(obj),
    arrayBuffer: async () => new ArrayBuffer(0),
  });
  async function fakeFetch(url, init) {
    init = init || {};
    const u = String(url);
    if (u.indexOf('accounts.spotify.com') >= 0)
      return reply({ access_token: 'tok', expires_in: 3600 });
    if (u.indexOf('api.spotify.com') >= 0)
      return spotify ? reply(spotify) : reply(null, 204);
    if (slow) await sleep(slow);
    if (init.signal && init.signal.aborted) throw new Error('aborted');
    if (u.endsWith('/json/info'))
      return reply({ name: 'WLED', ver: '0.15.4', leds: { count: 622, maxpwr: 1000 } });
    if (u.endsWith('/presets.json')) return reply({ 0: {}, 1: { n: 'standby' } });
    if (u.endsWith('/json/state') && init.method === 'POST') {
      const body = JSON.parse(init.body);
      const kind = !Array.isArray(body.seg) ? (body.nl ? 'arm' : 'other')
        : body.seg.some(s => s.i) ? 'frame'
        : body.seg[0] && body.seg[0].frz === false ? 'release'
        : body.seg[0] && 'start' in body.seg[0] ? 'layout' : 'other';
      if (kind === 'layout') segs = body.seg;
      log.push({ kind: kind, t: Date.now(), body: kind === 'frame' ? null : body });
      return reply({ success: true });
    }
    if (u.endsWith('/json/state')) return reply({ seg: segs });
    return reply(null, 404);
  }
  const count = (kind, since) => log.filter(e => e.kind === kind && (!since || e.t >= since)).length;

  const g = {
    document, console, Promise, Math, JSON, Date,
    setTimeout, clearTimeout, setInterval, clearInterval,
    performance, atob, URLSearchParams, Blob, File, AbortController,
    fetch: fakeFetch, devicePixelRatio: 1,
    navigator: {},                  // plain http: no wakeLock, no sendBeacon
    location: { search: '', host: '4.3.2.1', origin: 'http://4.3.2.1',
                protocol: 'http:', hash: '', pathname: '/mau5.htm' },
    history: { replaceState() {} },
    localStorage: { getItem: k => (store.has(k) ? store.get(k) : null),
                    setItem: (k, v) => store.set(k, String(v)),
                    removeItem: k => store.delete(k) },
    addEventListener: (k, fn) => { handlers[k] = fn; },
    prompt: () => '    0123456789abcdef0123456789abcdef.AQDrefreshTOKEN\n',
    isSecureContext: false,
  };
  g.window = g; g.globalThis = g;
  vm.createContext(g);
  vm.runInContext('globalThis.MAU5_DATA = ' + JSON.stringify(data) + ';', g);
  for (const f of ['engine.js', 'guard.js', 'wire.js', 'audio.js', 'drive.js',
                   'spotify.js', 'show.js', 'ui.js'])
    vm.runInContext(fs.readFileSync(path.join(DIR, f), 'utf8'), g, { filename: f });
  const $ = document.getElementById;
  const out = {};
  const button = (name) => $('grid').children.find(b => b.dataset.name === name);
  const setCycle = (v) => { $('cycle').value = String(v); $('cycle').onchange({ target: $('cycle') }); };
  await sleep(100);

  // -- 1: cycling after a param was moved used to kill the loop ----------
  button('eyes').onclick();
  const row = $('params').children.find(r => r.children[0].textContent === 'color');
  const inp = row.children[row.children.length - 1];
  inp.value = '#ff2000'; inp.oninput();
  setCycle(0.12);
  $('go').onclick();
  const seen = new Set();
  const t1 = Date.now();
  while (Date.now() - t1 < 1600) { seen.add($('now').textContent); await sleep(20); }
  const late = Date.now() - 400;
  out.cycle = { presets: seen.size, running: $('go').textContent,
                framesLate: count('frame', late), released: count('release') };
  setCycle(0);

  // -- 2: a text value a preset cannot use is refused, not thrown --------
  button('sprite').onclick();
  const srow = $('params').children.find(r => r.children[0].textContent === 'sprite');
  const sin = srow.children[srow.children.length - 1];
  sin.value = 'no such sprite'; sin.onchange();
  await sleep(300);
  out.badText = { running: $('go').textContent, warn: $('warn').textContent,
                  framesLate: count('frame', Date.now() - 200) };

  // -- 3: a render that throws every frame stops the helmet cleanly ------
  g.MAU5.REGISTRY.solid.render = function () { throw new Error('boom'); };
  const before = count('release');
  button('solid').onclick();
  await sleep(800);
  out.throws = { running: $('go').textContent, warn: $('warn').textContent,
                 releases: count('release') - before,
                 framesAfter: count('frame', Date.now() - 400) };
  button('rainbow').onclick();

  // -- 4: never started from a hidden page -------------------------------
  document.visibilityState = 'hidden';
  const layouts = count('layout');
  $('go').onclick();
  await sleep(300);
  out.hiddenStart = { layouts: count('layout') - layouts, running: $('go').textContent };
  document.visibilityState = 'visible';

  // -- 5: stop pressed while the start is still talking to the controller -
  slow = 150;
  $('go').onclick();
  await sleep(200);
  out.cancelLabel = $('go').textContent;      // already says stop
  $('go').onclick();                          // ... and means it
  await sleep(2500);
  slow = 0;
  const tail = log.filter(e => e.kind === 'layout' || e.kind === 'release');
  out.cancel = { running: $('go').textContent,
                 last: tail.length ? tail[tail.length - 1].kind : null,
                 framesLate: count('frame', Date.now() - 1000) };

  // -- 6: Spotify following, and stop meaning stop -----------------------
  const SHOW = 'deadmau5 - Strobe (Dimension Remix)';
  spotify = { is_playing: true, progress_ms: 30000,
              item: { name: 'Strobe - Dimension Remix', artists: [{ name: 'deadmau5' }], id: '1' } };
  $('spbtn').onclick();
  await sleep(1500);
  out.follow = { running: $('go').textContent, show: $('showpick').value === SHOW,
                 button: $('spbtn').textContent };
  $('go').onclick();                          // stop
  const stoppedAt = Date.now();
  await sleep(2500);
  out.followStop = { running: $('go').textContent, button: $('spbtn').textContent,
                     layoutsAfter: count('layout', stoppedAt) };

  // hidden while following: stopped, not restarted in the background,
  // and picked up again once the page is back
  $('spbtn').onclick();
  await sleep(1500);
  const wasRunning = $('go').textContent;
  document.visibilityState = 'hidden';
  handlers.visibilitychange();
  const hidAt = Date.now();
  await sleep(2500);
  out.followHidden = { wasRunning: wasRunning, running: $('go').textContent,
                       layoutsWhileHidden: count('layout', hidAt) };
  document.visibilityState = 'visible';
  handlers.visibilitychange();
  await sleep(1800);
  out.followBack = { running: $('go').textContent, warn: $('warn').textContent };

  // paused: the show holds where the track is
  spotify = Object.assign({}, spotify, { is_playing: false, progress_ms: 42000 });
  await sleep(1500);
  const clocks = new Set();
  const t6 = Date.now();
  while (Date.now() - t6 < 2500) { clocks.add($('showat').textContent.split(' / ')[0]); await sleep(50); }
  out.paused = Array.from(clocks);
  out.pausedRunning = $('go').textContent;

  // a song with no show: the show stops, the presets carry on
  spotify = Object.assign({}, spotify, { is_playing: true,
    item: { name: 'Something Else Entirely', artists: [{ name: 'Nobody' }], id: '2' } });
  await sleep(2000);
  out.noShow = { showgo: $('showgo').textContent, running: $('go').textContent };

  out.uncaught = uncaught;
  out.spotify = { stored: store.get('mau5.spotify') };
  out.screen = $('scr').textContent;
  out.video = !!document.body.children.find(c => c.tagName === 'VIDEO' && c.id === 'awake');
  process.stdout.write(JSON.stringify(out));
  process.exit(0);
}
'''

# wire.js and spotify.js on a clock the harness owns.
WIRE_JS = r'''// wire.js and spotify.js on a clock this script owns.  argv[2] is
// remote/offline.  Writes one JSON object of observations.
'use strict';
const path = require('path');
const DIR = process.argv[2];
let T = 5, D = 1e12;
globalThis.performance = { now: () => T };
Date.now = () => D;
const W = require(path.join(DIR, 'wire.js'));
const S = require(path.join(DIR, 'spotify.js'));
const out = {};
const tick = () => new Promise(r => setImmediate(r));

function fakeWs(onSend) {
  return { readyState: 1, bufferedAmount: 0, send: onSend || (() => {}) };
}
const frameN = (n, k) => { const f = new Uint8Array(n * 3); f[0] = k & 255; f[1] = 1; return f; };

// -- a late pong is not credited to a newer frame ------------------------
// (with frames overlapping, which the page ships off -- DEPTH is 1 on
// WLED 0.15.4 -- but which a later firmware may allow: keep it right)
{
  const L = new W.Link({ count: 62, deadmanMins: 0, depth: 2 });
  L.ws = fakeWs();
  L.dirty();
  let ready = 0;
  L.onready = () => { ready++; };
  T = 0;    L.send(frameN(62, 1));
  T = 10;   L.send(frameN(62, 2));
  const full = L.busy(T);
  T = 1100;                                  // the controller has stalled
  const stalled = L.busy(T);
  const owed = L.owed;
  T = 1200; L._pong();                       // frame 1, late
  const stillBusy = L.busy(T);
  T = 1210; L._pong();                       // frame 2, late
  const freed = !L.busy(T);
  T = 1220; L.send(frameN(62, 3));
  const afterSend = L.unacked.length;
  T = 1290; L._pong();                       // frame 3's own
  out.late = { full, stalled, owed, stillBusy, freed, ready, afterSend,
               afterOwn: L.unacked.length, lost: L.lost };
  // a stray pong with nothing waiting changes nothing
  L._pong();
  out.late.stray = L.unacked.length;
}

// -- pongs that never come are given up on, and sending resumes ----------
{
  const L = new W.Link({ count: 62, deadmanMins: 0, depth: 2 });
  L.ws = fakeWs();
  T = 0;   L.send(frameN(62, 1));
  T = 10;  L.send(frameN(62, 2));
  T = 1100;
  const a = L.busy(T);
  T = 1100 + 1400;
  const b = L.busy(T);
  T = 1100 + 1600;
  const c = L.busy(T);
  out.lost = { during: a, quiet: b, after: c, owed: L.owed };
}

// -- the stall model: a controller parsing messages in order -------------
// The player paced as ui.js paces it (busy, onready, a 30 fps floor),
// against a controller that spends MS per padded message and stops for
// stallLen at 3 s.  Returns what was really queued against what the
// page believed, before the stall and well after it.
function stallModel(stallLen) {
  T = 5;
  const N = 621, MS = 12, END = 14000, STALL = 3000;
  const L = new W.Link({ count: N, deadmanMins: 0, depth: 2 });
  const events = []; let seq = 0;
  const at = (t, fn) => { events.push([t, seq++, fn]); events.sort((x, y) => x[0] - y[0] || x[1] - y[1]); };
  let free = 0, real = 0;
  const samples = [];
  L.ws = fakeWs((m) => {
    if (m.length > 1 && m.trim() === '') return;           // the filler
    let start = Math.max(T + 2, free);
    if (start >= STALL && start < STALL + stallLen) start = STALL + stallLen;
    free = start + (m === 'p' ? 0.2 : MS);
    if (m !== 'p') return;
    real++;
    samples.push([T, real, L.unacked.length + 1, free - T]);
    at(free + 2, () => { real--; L._pong(); });
  });
  L.dirty();
  const FLOOR = 1000 / 30;
  let last = 0, parked = false, timer = null, k = 0;
  const sched = (dt) => { const h = { dead: false }; timer = h; at(T + Math.max(dt, 1), () => { if (!h.dead) step(); }); };
  L.onready = () => { if (parked) { parked = false; if (timer) timer.dead = true; step(); } };
  function step() {
    if (L.busy(T)) { parked = true; sched(50); return; }
    parked = false;
    if (T - last < FLOOR) { sched(FLOOR - (T - last)); return; }
    last = T; k++;
    const f = new Uint8Array(N * 3);
    for (let i = 0; i < f.length; i++) f[i] = (i * 7 + k * 13) & 255;
    L.send(f);
    sched(FLOOR);
  }
  step();
  while (events.length && T < END) { const [t, , fn] = events.shift(); T = t; fn(); }
  const med = (a) => { const s = a.slice().sort((x, y) => x - y); return s[s.length >> 1]; };
  const win = (a, b) => samples.filter(s => s[0] >= a && s[0] < b);
  const before = win(1000, 3000), after = win(10000, 14000);
  return {
    before: { real: med(before.map(s => s[1])), thinks: med(before.map(s => s[2])),
              lag: Math.round(med(before.map(s => s[3]))) },
    after: { real: med(after.map(s => s[1])), thinks: med(after.map(s => s[2])),
             lag: Math.round(med(after.map(s => s[3]))) },
    worst: Math.max(...after.map(s => s[1] - s[2])),
  };
}
out.stall = { s1200: stallModel(1200), s2200: stallModel(2200) };

// -- the dead man, through a controller that records what it was sent ---
async function deadman() {
  const posts = [];
  let down = false, hang = null, layout = [];
  globalThis.fetch = async (url, init) => {
    init = init || {};
    if (hang) return hang(init);
    if (down) throw new Error('network down');
    let body = { seg: layout };              // a GET of /json/state
    if (init.method === 'POST') {
      const b = JSON.parse(init.body);
      posts.push(b);
      if (Array.isArray(b.seg) && b.seg[0] && 'start' in b.seg[0]) layout = b.seg;
      body = { success: true };
    }
    return { ok: true, status: 200, json: async () => body, text: async () => '{}' };
  };
  const L = new W.Link({ count: 621, deadmanMins: 1 });
  L.ws = fakeWs();
  await L.begin(180);
  const r = {};
  const first = posts[0];
  r.layoutArms = !!(first.nl && first.nl.on && first.nl.tbri === 0 && first.nl.dur === 1);
  r.layoutFrozen = first.seg.every(s => s.frz === true);
  r.beginPosts = posts.map(p => Object.keys(p).sort().join(','));
  // normal running: an arm every 20 s, nl only
  posts.length = 0;
  D += 21000; L.send(frameN(621, 1)); await tick(); await tick(); await tick();
  r.normal = posts.map(p => Object.keys(p).sort().join(','));
  // the phone loses the helmet: arms fail ...  (No pongs in this part,
  // so unacked is cleared by hand before each frame.)
  down = true;
  for (let s = 0; s < 6; s++) { D += 8000; T += 8000; L.unacked = []; L.send(frameN(621, s + 2)); await tick(); await tick(); }
  down = false;
  posts.length = 0;
  // ... and the first one through turns it back on, frozen, at its brightness
  D += 4000; T += 4000; L.unacked = []; L.send(frameN(621, 9)); await tick(); await tick(); await tick();
  const back = posts.find(p => p.on === true);
  r.revive = back ? { bri: back.bri, nl: !!(back.nl && back.nl.on),
                      frozen: back.seg.length === L.segs.length && back.seg.every(s => s.frz === true) } : null;
  r.revived = L.revived;
  r.wholeNext = L.last.every(x => x === null);
  // right after that, normal again
  posts.length = 0;
  D += 21000; T += 21000; L.unacked = []; L.send(frameN(621, 10)); await tick(); await tick(); await tick();
  r.normalAgain = posts.map(p => Object.keys(p).sort().join(','));
  // let go while an arm is on its way: it must not arm (or light) after
  let release;
  posts.length = 0;
  hang = (init) => new Promise(res => { release = () => res({ ok: true, status: 200, text: async () => '{}' }); posts.push(JSON.parse(init.body)); });
  D += 70000; T += 70000; L.unacked = []; L.send(frameN(621, 11)); await tick();
  hang = null;
  await L.release();
  release();
  await tick(); await tick(); await tick();
  r.afterRelease = posts.map(p => Object.keys(p).sort().join(','));
  return r;
}

// -- a controller that never answers ------------------------------------
async function timeouts() {
  globalThis.fetch = (url, init) => new Promise((res, rej) => {
    if (init && init.signal) init.signal.addEventListener('abort', () => rej(new Error('aborted')));
  });
  const L = new W.Link({ count: 62, deadmanMins: 1, reqTimeout: 30 });
  const t0 = process.hrtime.bigint();
  const r = {};
  try { await L.getJSON('/json/info'); r.get = 'answered'; } catch (e) { r.get = e.message; }
  try { await L.postJSON({ on: true }); r.post = 'answered'; } catch (e) { r.post = e.message; }
  try { await L.begin(100); r.begin = 'answered'; } catch (e) { r.begin = e.message; }
  r.ms = Number(process.hrtime.bigint() - t0) / 1e6;
  return r;
}

// -- Spotify ------------------------------------------------------------
async function spotify() {
  const r = {};
  const s = new S.Spotify();
  s.connect('    0123456789abcdef0123456789abcdef.AQDrefreshTOKENxyz\n');
  r.paste = [s.clientId, s.refresh];
  s.connect('0123456789abcdef0123456789abcdef.AQDrefr\neshTOKENxyz');
  r.wrapped = [s.clientId, s.refresh];
  try { s.connect('   x.y'); r.junk = 'accepted'; } catch (e) { r.junk = 'refused'; }
  s.access = 'tok'; s.expires = Date.now() + 3600e3;
  // a poll that takes 400 ms: the position is from the middle of it
  T = 10000;
  globalThis.fetch = async () => { T += 400; return { ok: true, status: 200,
    json: async () => ({ is_playing: true, progress_ms: 60000, item: { name: 'x', artists: [] } }) }; };
  await s.poll();
  r.at = s.at;
  r.pos = s.position();                      // T is 10400 now
  // a 429 says wait, and the next poll does not ask
  let asked = 0;
  globalThis.fetch = async () => { asked++; return { ok: false, status: 429,
    headers: { get: (k) => (k === 'Retry-After' ? '7' : null) } }; };
  try { await s.poll(); } catch (e) { r.limited = e.message; }
  r.wait = Math.round(s.waitMs());
  try { await s.poll(); } catch (e) { r.second = e.message; }
  r.asked = asked;
  T += 7100;
  r.waitAfter = s.waitMs();
  return r;
}

(async () => {
  globalThis.localStorage = { getItem: () => null, setItem: () => {}, removeItem: () => {} };
  out.deadman = await deadman();
  out.timeouts = await timeouts();
  out.spotify = await spotify();
  process.stdout.write(JSON.stringify(out));
})().catch(e => { process.stdout.write(JSON.stringify({ crashed: String(e && e.stack || e) })); });
'''


# The standby button and the offline prompt, each case on a fresh page.
# The same scaffold as above, with the page's clock sped up, because the
# button takes half a minute of real measuring.
STANDBY_JS = PAGE_JS[:PAGE_JS.index('async function main(data)')] + r'''
const FAST = 40;
const realPerf = performance;
const realTimeout = setTimeout;

// One page, on one address, in front of a controller whose current
// estimate is the case's pwr(state, nth reading).
async function open(data, c) {
  const byId = {};
  const made = [];
  const document = {
    visibilityState: 'visible', body: element('body'),
    getElementById: (id) => byId[id] || (byId[id] = element('div', id)),
    createElement: (tag) => { const e = element(tag); e.remove = () => {}; made.push(e); return e; },
    querySelectorAll: () => [],
  };
  const store = new Map(Object.entries(c.store || {}));
  const handlers = {};
  const ctl = { fx: -1, bri: 128, on: false, states: [], cfgs: [], presets: new Set(), hook: null,
                laptopAsked: 0, sockets: [], socketsDown: false };
  const reply = (obj, status) => ({
    ok: (status || 200) < 300, status: status || 200, headers: { get: () => null },
    json: async () => obj, text: async () => JSON.stringify(obj),
    arrayBuffer: async () => new ArrayBuffer(0),
  });
  async function fakeFetch(url, init) {
    init = init || {};
    const u = String(url);
    if (u.endsWith('/json/info')) {
      return reply({ name: 'WLED', ver: '16.0.1',
                     leds: { count: 622, maxpwr: 1622, pwr: c.pwr ? c.pwr(ctl) : 0 } });
    }
    if (u.endsWith('/json/eff')) {
      const fx = new Array(120).fill('x');
      fx[101] = 'Pacifica@!,Angle;;!;;pal=51';
      return reply(fx);
    }
    if (u.endsWith('/songs.json'))
      return c.pointer ? reply(c.pointer) : reply(null, 404);
    if (c.pointer && u.indexOf(c.pointer.from) === 0) {
      ctl.laptopAsked++;
      // An address nobody is at: nothing, until the page stops waiting.
      return new Promise((res, rej) => {
        if (init.signal) init.signal.addEventListener('abort', () => rej(new Error('aborted')));
      });
    }
    if (c.unreachable && c.unreachable(ctl)) throw new Error('no route');
    if (u.endsWith('/presets.json')) {
      const have = { 0: {} };
      ctl.presets.forEach(k => { have[k] = { n: 'saved' }; });
      return reply(have);
    }
    if (u.endsWith('/json/cfg') && init.method === 'POST') {
      ctl.cfgs.push(JSON.parse(init.body));
      return reply({ success: true });
    }
    if (u.endsWith('/json/state') && init.method === 'POST') {
      const b = JSON.parse(init.body);
      ctl.states.push(b);
      if (b.on !== undefined) ctl.on = b.on;
      if (b.bri !== undefined) ctl.bri = b.bri;
      const s0 = (b.seg || [])[0];
      if (s0 && s0.fx !== undefined) ctl.fx = s0.fx;
      if (b.psave) ctl.presets.add(b.psave);
      if (ctl.hook) ctl.hook(b);
      return reply({ success: true });
    }
    if (u.endsWith('/json/state'))
      return reply({ on: ctl.on, bri: ctl.bri, seg: [{ id: 0 }, { id: 3 }] });
    return reply(null, 404);
  }
  class FakeSocket {
    constructor() {
      this.readyState = 0;
      ctl.sockets.push(this);
      realTimeout(() => {
        if (ctl.socketsDown) {
          this.readyState = 3;
          if (this.onerror) this.onerror({});
          return;
        }
        this.readyState = 1;
        if (this.onopen) this.onopen({});
      }, 1);
    }
    send(m) {
      if (m === 'p' && !this.mute) realTimeout(() => { if (this.readyState === 1 && this.onmessage) this.onmessage({ data: 'pong' }); }, 1);
      this.got = (this.got || 0) + 1;
    }
    close() { this.drop(); }
    drop() {
      if (this.readyState === 3) return;
      this.readyState = 3;
      if (this.onclose) this.onclose({});
    }
  }
  class PageURL extends URL {
    static createObjectURL(f) { return 'blob:' + ((f && f.name) || 'x'); }
    static revokeObjectURL() {}
  }
  // Enough of an audio graph for the analyser to run on.
  ctl.audios = []; ctl.plays = []; ctl.workers = 0;
  class FakeAudio {
    constructor() { this.currentTime = 0; this.paused = true; this.ended = false; ctl.audios.push(this); }
    play() {
      if (c.refuse && c.refuse(this.src)) return Promise.reject(new Error('not allowed'));
      this.paused = false; ctl.plays.push(this.src);
      return Promise.resolve();
    }
    pause() { this.paused = true; }
  }
  const node = () => ({ fftSize: 1024, get frequencyBinCount() { return this.fftSize / 2; },
                        minDecibels: -100, maxDecibels: -30, smoothingTimeConstant: 0,
                        connect() {}, disconnect() {},
                        getFloatFrequencyData(a) { a.fill(-70); },
                        getByteTimeDomainData(a) { a.fill(128); },
                        getByteFrequencyData(a) { a.fill(10); } });
  class FakeContext {
    constructor() { this.state = c.ctxState || 'running'; this.sampleRate = 44100; this.currentTime = 0;
                    this.destination = {}; ctl.ctx = this; }
    createAnalyser() { return node(); }
    createMediaElementSource(el) { ctl.wired = (ctl.wired || 0) + 1; return node(); }
    resume() { this.state = 'running'; ctl.resumed = (ctl.resumed || 0) + 1; return Promise.resolve(); }
  }
  class FakeWorker {
    constructor() { ctl.workers++; }
    postMessage(m) {
      ctl.clockTicks = (ctl.clockTicks || 0) + 1;
      realTimeout(() => { if (this.onmessage) this.onmessage({ data: m.seq }); }, (m.ms || 0) / FAST);
    }
  }
  class PageDate extends Date {
    static now() { return Date.now() * FAST; }
  }
  const g = {
    document, console, Promise, Math, JSON, Date: PageDate,
    setTimeout: (f, ms) => realTimeout(f, (ms || 0) / FAST), clearTimeout,
    setInterval: (f, ms) => setInterval(f, (ms || 0) / FAST), clearInterval,
    performance: { now: () => realPerf.now() * FAST },
    atob, URL: PageURL, URLSearchParams, Blob, File, AbortController,
    fetch: fakeFetch, devicePixelRatio: 1, navigator: { maxTouchPoints: c.touch || 0 },
    Audio: FakeAudio, AudioContext: FakeContext, Worker: c.worker ? FakeWorker : undefined,
    WebSocket: c.sockets ? FakeSocket : undefined,
    location: { search: c.search || '', host: c.host, hostname: c.host,
                href: 'http://' + c.host + '/mau5.htm', origin: 'http://' + c.host,
                protocol: 'http:', hash: '', pathname: '/mau5.htm' },
    history: { replaceState() {} },
    localStorage: { getItem: k => (store.has(k) ? store.get(k) : null),
                    setItem: (k, v) => store.set(k, String(v)),
                    removeItem: k => store.delete(k) },
    addEventListener: (k, fn) => { handlers[k] = fn; },
    prompt: () => null, isSecureContext: false,
  };
  g.window = g; g.globalThis = g;
  vm.createContext(g);
  vm.runInContext('globalThis.MAU5_DATA = ' + JSON.stringify(data) + ';', g);
  for (const f of ['engine.js', 'guard.js', 'wire.js', 'audio.js', 'drive.js',
                   'spotify.js', 'show.js', 'ui.js']) {
    if (f === 'ui.js') {
      const have = (c.songs || []).map(n => [n, { name: n + '.mp3', size: 1000000 }]);
      const cached = new Map(have);
      g.MAU5.TrackCache = class {
        async keys() { return Array.from(cached.keys()); }
        async get(n) { return cached.get(n) || null; }
        async put(n, f) { cached.set(n, f); }
      };
    }
    vm.runInContext(fs.readFileSync(path.join(DIR, f), 'utf8'), g, { filename: f });
  }
  await sleep(60);
  return { g, $: document.getElementById, ctl, store, made, document, handlers };
}

const says = (p) => p.$('standbyat').textContent;
const saves = (p) => p.ctl.states.filter(b => 'psave' in b);
// Play, then stop: what the page lets go with.
async function letGo(p) {
  p.$('go').onclick();
  await sleep(100);
  p.$('go').onclick();
  await sleep(100);
  const gone = p.ctl.states.filter(b => 'live' in b && !('bri' in b));
  return gone[gone.length - 1] || null;
}
async function press(p) {
  p.$('standbysetup').onclick();
  for (let k = 0; k < 400 && p.$('standbysetup').disabled; k++) await sleep(10);
  const r = { says: says(p), saves: saves(p), cfgs: p.ctl.cfgs, bri: p.ctl.bri, on: p.ctl.on,
              segs: p.ctl.states[0] && p.ctl.states[0].seg };
  r.release = await letGo(p);
  return r;
}
const box = (p) => ({ shown: p.$('offbox').style.display, text: p.$('offat').innerHTML,
                      btn: p.$('offsave').textContent, disabled: p.$('offsave').disabled });
const AP = '4.3.2.1', HOME = '192.168.10.172';

async function main(data) {
  const out = {};
  const names = Object.keys(data.shows || {});
  const black = 722;                 // 622 mA of LED standby, 100 of board
  const lit = (mPerBri) => (ctl) => (ctl.fx === 101 && ctl.on ? black + mPerBri * ctl.bri : black);

  out.fits = await press(await open(data, { host: HOME, pwr: lit(7) }));
  out.firstTry = await press(await open(data, { host: HOME, pwr: lit(2) }));
  out.noEstimate = await press(await open(data, { host: HOME, pwr: () => 100 }));
  out.neverFits = await press(await open(data, { host: HOME,
    pwr: (ctl) => (ctl.fx === 101 && ctl.on ? black + 900 : black) }));

  // The first reading after black still carries the frame before it.
  let stale = true;
  const staleCase = await open(data, { host: HOME, pwr: (ctl) => {
    if (ctl.fx === 0 && ctl.bri === 128 && stale) { stale = false; return 1500; }
    return lit(7)(ctl);
  } });
  out.stale = await press(staleCase);

  const running = await open(data, { host: HOME, pwr: lit(7) });
  running.$('go').onclick();
  await sleep(60);
  const before = running.ctl.states.filter(b => 'psave' in b || (b.seg || []).some(s => s.fx === 101)).length;
  running.$('standbysetup').onclick();
  await sleep(100);
  out.running = { says: says(running), saves: saves(running), cfgs: running.ctl.cfgs,
                  glows: running.ctl.states.filter(b => (b.seg || []).some(s => s.fx === 101)).length - before };
  running.$('go').onclick();

  const interrupted = await open(data, { host: HOME, pwr: lit(7) });
  interrupted.ctl.hook = (b) => {
    if (b.bri === 96 && !interrupted.hit) { interrupted.hit = true; interrupted.$('go').onclick(); }
  };
  interrupted.$('standbysetup').onclick();
  for (let k = 0; k < 400 && interrupted.$('standbysetup').disabled; k++) await sleep(10);
  out.interrupted = { says: says(interrupted), saves: saves(interrupted), cfgs: interrupted.ctl.cfgs };
  interrupted.$('go').onclick();

  // -- the offline prompt ------------------------------------------------
  const ready = await open(data, { host: HOME, songs: names });
  out.homeReady = box(ready);
  ready.$('offsave').onclick();
  await sleep(names.length * 40 + 120);
  out.afterSave = { box: box(ready), later: ready.$('offlater').textContent,
                    files: ready.made.filter(e => e.download).map(e => e.download),
                    stored: ready.store.get('mau5saved') };
  ready.$('offlater').onclick();
  out.afterGotIt = box(ready).shown;
  out.homeSaved = box(await open(data, { host: HOME, songs: names,
                                         store: { mau5saved: ready.store.get('mau5saved') } }));
  out.homeWaiting = box(await open(data, { host: HOME, songs: names.slice(1) }));
  const oneNew = await open(data, { host: HOME, songs: names,
                                    store: { mau5saved: JSON.stringify({ names: names.slice(1) }) } });
  out.oneNew = { text: box(oneNew).text };
  oneNew.$('offsave').onclick();
  await sleep(120);
  out.oneNew.files = oneNew.made.filter(e => e.download).length;
  out.oneNew.stored = JSON.parse(oneNew.store.get('mau5saved')).names.length;
  const apMissing = await open(data, { host: AP });
  out.apMissing = box(apMissing);
  let picked = 0;
  apMissing.$('songpick').click = () => { picked++; };
  apMissing.$('offsave').onclick();
  out.apPicked = picked;
  out.apReady = box(await open(data, { host: AP, songs: names }));
  out.apiAP = box(await open(data, { host: '127.0.0.1:8794', search: '?api=http://4.3.2.1' }));
  // -- the songs, when the laptop the pointer names is not there ---------
  const STALE = { from: 'http://192.168.10.168:8799', since: 'x', songs: {} };
  for (const n of names) STALE.songs[n] = { path: '/songs/0.mp3', track: n + '.mp3', bytes: 1 };
  const apStale = await open(data, { host: AP, pointer: STALE });
  await sleep(150);
  out.apStale = { asked: apStale.ctl.laptopAsked, box: box(apStale),
                  line: apStale.$('songsat').textContent };
  const homeStale = await open(data, { host: HOME, pointer: STALE });
  await sleep(400);
  out.homeStale = { asked: homeStale.ctl.laptopAsked, box: box(homeStale),
                    line: homeStale.$('songsat').textContent };
  const apLaptop = await open(data, { host: AP,
    pointer: Object.assign({}, STALE, { from: 'http://4.3.2.5:8799' }) });
  await sleep(60);
  out.apLaptopAsked = apLaptop.ctl.laptopAsked;

  // -- a dropout under a running effect ----------------------------------
  const lastUp = () => drop.ctl.sockets[drop.ctl.sockets.length - 1];
  const drop = await open(data, { host: AP, sockets: true });
  drop.$('go').onclick();
  await sleep(120);
  out.dropRunning = drop.$('go').textContent;
  const laidFrom = drop.ctl.states.length;
  drop.ctl.socketsDown = true;
  lastUp().drop();
  await sleep(150);                  // 6 s of the page's time
  out.dropLost = { conn: drop.$('conn').textContent, cls: drop.$('conn').className,
                   running: drop.$('go').textContent };
  drop.ctl.socketsDown = false;
  await sleep(250);
  out.dropBack = { conn: drop.$('conn').textContent, cls: drop.$('conn').className,
                   running: drop.$('go').textContent,
                   relaid: drop.ctl.states.slice(laidFrom).filter(b => b.on === true && b.live === false).length };
  drop.$('go').onclick();

  // -- out of sight and back ---------------------------------------------
  const hide = async (p) => { p.document.visibilityState = 'hidden'; p.handlers.visibilitychange(); await sleep(60); };
  const show = async (p) => { p.document.visibilityState = 'visible'; p.handlers.visibilitychange(); await sleep(120); };
  const seen = await open(data, { host: AP, sockets: true });
  seen.$('go').onclick();
  await sleep(100);
  await hide(seen);
  out.hidden = seen.$('go').textContent;
  await show(seen);
  out.shown = { go: seen.$('go').textContent, warn: seen.$('warn').textContent };
  seen.$('go').onclick();           // stopped by hand
  await sleep(60);
  await hide(seen);
  await show(seen);
  out.pressedStop = seen.$('go').textContent;

  let noRoute = false;
  const flaky = await open(data, { host: AP, sockets: true, unreachable: () => noRoute });
  flaky.$('go').onclick();
  await sleep(100);
  await hide(flaky);
  noRoute = true;
  await show(flaky);
  out.backNoWifi = flaky.$('go').textContent;
  noRoute = false;
  await sleep(300);
  out.backWifi = flaky.$('go').textContent;
  flaky.$('go').onclick();

  // -- binary frames: no nightlight, and a helmet that went off comes back --
  const kept = await open(data, { host: HOME, sockets: true });
  kept.$('go').onclick();
  await sleep(250);                  // ten seconds of the page's time
  out.keptNl = kept.ctl.states.filter(b => b.nl && b.nl.on === true).length;
  out.keptOffNl = kept.ctl.states.filter(b => b.nl && b.nl.on === false).length;
  kept.ctl.on = false;
  kept.ctl.bri = 0;
  await sleep(250);
  out.keptBack = { on: kept.ctl.on, bri: kept.ctl.bri, warn: kept.$('warn').textContent };
  kept.$('go').onclick();
  await sleep(40);
  kept.ctl.on = false;
  await sleep(250);
  out.keptStopped = kept.ctl.on;

  out.names = names.length;
  out.uncaught = uncaught;
  process.stdout.write(JSON.stringify(out));
  process.exit(0);
}
'''


# Play Music, on the real page: the order, the one audio element a phone needs,
# skipping, and everything else that can happen to a set.
LIST_JS = STANDBY_JS[:STANDBY_JS.index('async function main(data)')] + r'''
async function main(data) {
  const out = {};
  const names = Object.keys(data.shows || {});
  const order = (data.playlist || []).filter(n => data.shows[n])
    .concat(names.filter(n => (data.playlist || []).indexOf(n) < 0));
  const src = (p) => p.ctl.audios[0].src;
  const song = (n) => 'blob:' + n + '.mp3';
  const wait = (ms) => sleep(ms || 120);

  const none = await open(data, { host: HOME, sockets: true });
  none.$('playall').onclick();
  await wait();
  out.none = { label: none.$('playall').textContent, says: none.$('listat').textContent,
               go: none.$('go').textContent, disabled: none.$('listnext').disabled };

  const p = await open(data, { host: HOME, sockets: true, songs: names });
  p.$('playall').onclick();
  // straight from the tap, before anything is awaited
  out.unlock = { made: p.ctl.audios.length, src: p.ctl.audios[0] && p.ctl.audios[0].src };
  await wait();
  out.first = { src: src(p), want: song(order[0]), label: p.$('playall').textContent,
                go: p.$('go').textContent, says: p.$('listat').textContent,
                picked: p.$('showpick').value, next: p.$('listnext').disabled };
  const walked = [src(p)];
  for (let k = 0; k < names.length; k++) {
    p.ctl.audios[0].onended();
    await wait();
    walked.push(src(p));
  }
  out.walked = walked; out.want = order.map(song).concat([song(order[0])]);
  out.elements = p.ctl.audios.length;
  out.wired = p.ctl.wired;
  out.stillGoing = p.$('go').textContent;
  p.$('listnext').onclick();
  await wait();
  out.afterNext = src(p);
  p.ctl.audios[0].currentTime = 30;
  p.$('listprev').onclick();
  await wait();
  out.prevRestart = { src: src(p), t: p.ctl.audios[0].currentTime };
  p.$('listprev').onclick();
  await wait();
  out.prevBack = src(p);
  p.$('showpick').value = order[3];
  p.$('showpick').onchange({ target: p.$('showpick') });
  await wait();
  out.jumped = { src: src(p), on: p.$('playall').textContent };
  p.ctl.audios[0].onerror();
  await wait(200);
  out.afterError = { src: src(p), warn: p.$('warn').textContent };
  p.$('playall').onclick();
  await wait();
  out.stopped = { label: p.$('playall').textContent, go: p.$('go').textContent,
                  paused: p.ctl.audios[0].paused, says: p.$('listat').textContent };
  p.$('go').onclick();
  await wait();
  out.startAfterSet = { go: p.$('go').textContent, paused: p.ctl.audios[0].paused };
  p.$('go').onclick();
  await wait();

  // the footer's stop means the song and the set too
  const foot = await open(data, { host: HOME, sockets: true, songs: names });
  foot.$('playall').onclick();
  await wait();
  foot.$('go').onclick();
  await wait();
  out.footer = { label: foot.$('playall').textContent, go: foot.$('go').textContent,
                 paused: foot.ctl.audios[0].paused };

  // and a song started from the show box stops with the footer as well
  const box1 = await open(data, { host: HOME, sockets: true, songs: names });
  box1.$('showpick').value = order[1];
  box1.$('showpick').onchange({ target: box1.$('showpick') });
  await wait();
  box1.$('showgo').onclick();
  await wait();
  const playing = !box1.ctl.audios[0].paused;
  box1.$('go').onclick();
  await wait();
  out.boxFooter = { playing, paused: box1.ctl.audios[0].paused, go: box1.$('go').textContent };

  // and a song already playing joins the set where it is
  const box2 = await open(data, { host: HOME, sockets: true, songs: names });
  box2.$('showpick').value = order[1];
  box2.$('showpick').onchange({ target: box2.$('showpick') });
  await wait();
  box2.$('showgo').onclick();
  await wait();
  box2.ctl.audios[0].currentTime = 42;
  const plays = box2.ctl.plays.length;
  box2.$('playall').onclick();
  await wait();
  out.joined = { t: box2.ctl.audios[0].currentTime, again: box2.ctl.plays.length - plays,
                 label: box2.$('playall').textContent, src: src(box2) };
  box2.ctl.audios[0].onended();
  await wait();
  out.joinedNext = { src: src(box2), want: song(order[2]) };
  box2.$('go').onclick();

  // a preset ends the set rather than sit over it
  const pre = await open(data, { host: HOME, sockets: true, songs: names });
  pre.$('playall').onclick();
  await wait();
  pre.$('grid').children[0].onclick();
  await wait();
  out.preset = { label: pre.$('playall').textContent, paused: pre.ctl.audios[0].paused };
  pre.$('go').onclick();

  // something else takes the song away
  const taken = await open(data, { host: HOME, sockets: true, songs: names });
  taken.$('playall').onclick();
  await wait();
  taken.$('aoff').onclick();
  await wait(200);
  out.taken = taken.$('playall').textContent;
  taken.$('go').onclick();

  // only what is here plays, what cannot play is skipped, and all failing ends it
  const some = await open(data, { host: HOME, sockets: true, songs: [order[2], order[4]] });
  some.$('playall').onclick();
  await wait();
  const sa = src(some);
  some.ctl.audios[0].onended();
  await wait();
  const sb = src(some);
  some.ctl.audios[0].onended();
  await wait();
  out.some = { walked: [sa, sb, src(some)], want: [song(order[2]), song(order[4]), song(order[2])],
               says: some.$('listat').textContent };
  some.$('go').onclick();

  const bad = song(order[1]);
  const skip = await open(data, { host: HOME, sockets: true, songs: names, refuse: (u) => u === bad });
  skip.$('playall').onclick();
  await wait();
  skip.ctl.audios[0].onended();
  await wait(200);
  out.skipped = { src: src(skip), want: song(order[2]) };
  skip.$('go').onclick();

  const dead = await open(data, { host: HOME, sockets: true, songs: names, refuse: (u) => /^blob/.test(u) });
  dead.$('playall').onclick();
  await wait(names.length * 40 + 300);
  out.dead = { label: dead.$('playall').textContent, says: dead.$('listat').textContent };
  dead.$('go').onclick();

  // a phone: hidden stops the lights, the set carries on, and they come back
  const hide = async (q) => { q.document.visibilityState = 'hidden'; q.handlers.visibilitychange(); await wait(60); };
  const show = async (q) => { q.document.visibilityState = 'visible'; q.handlers.visibilitychange(); await wait(160); };
  const phone = await open(data, { host: AP, sockets: true, songs: names, touch: 5, worker: true });
  phone.$('playall').onclick();
  await wait();
  out.phoneWorkers = phone.ctl.workers;
  await hide(phone);
  out.phoneHidden = { go: phone.$('go').textContent, paused: phone.ctl.audios[0].paused };
  phone.ctl.audios[0].onended();
  await wait();
  out.phoneNext = { src: src(phone), want: song(order[1]), go: phone.$('go').textContent };
  phone.ctl.audios[0].paused = true;      // the browser paused it
  phone.ctl.ctx.state = 'interrupted';
  await show(phone);
  out.phoneBack = { go: phone.$('go').textContent, paused: phone.ctl.audios[0].paused, ctx: phone.ctl.ctx.state };
  phone.$('showpp').onclick();            // somebody pauses it
  await hide(phone);
  await show(phone);
  out.phonePaused = phone.ctl.audios[0].paused;
  phone.$('go').onclick();

  // a laptop: covered or tabbed away, the helmet carries on, on the worker's clock
  const lap = await open(data, { host: HOME, sockets: true, songs: names, worker: true });
  lap.$('playall').onclick();
  await wait();
  out.lapWorkers = lap.ctl.workers;
  const framesBefore = lap.g.MAU5_LINK.sent;
  await hide(lap);
  const ticksBefore = lap.ctl.clockTicks || 0;
  await wait(200);
  out.lapHidden = { go: lap.$('go').textContent, paused: lap.ctl.audios[0].paused,
                    frames: lap.g.MAU5_LINK.sent - framesBefore,
                    ticks: (lap.ctl.clockTicks || 0) - ticksBefore, warn: lap.$('warn').textContent };
  await show(lap);
  const after = lap.g.MAU5_LINK.sent;
  await wait(120);
  out.lapShown = { go: lap.$('go').textContent, frames: lap.g.MAU5_LINK.sent - after };
  lap.$('go').onclick();

  // a laptop with a preset and no song does the same
  const lap2 = await open(data, { host: HOME, sockets: true, worker: true });
  lap2.$('go').onclick();
  await wait();
  await hide(lap2);
  await wait(100);
  out.lapPreset = lap2.$('go').textContent;
  lap2.$('go').onclick();

  // a link that dies without the socket being told: it stays "open", and says nothing
  const quiet = await open(data, { host: HOME, sockets: true });
  quiet.$('go').onclick();
  await wait();
  const opened = quiet.ctl.sockets.length;
  const first = quiet.ctl.sockets[opened - 1];
  first.mute = true;
  const posts = quiet.ctl.states.length;
  await wait(100);                        // 4 s of the page's time: it may just be slow
  out.quietPatient = { sockets: quiet.ctl.sockets.length - opened, closes: quiet.g.MAU5_LINK.quietCloses };
  await wait(250);
  const now = quiet.ctl.sockets[quiet.ctl.sockets.length - 1];
  const sent = now.got || 0;
  await wait(80);
  out.quiet = { sockets: quiet.ctl.sockets.length - opened, closes: quiet.g.MAU5_LINK.quietCloses,
                old: first.readyState, flowing: (now.got || 0) - sent, go: quiet.$('go').textContent,
                relaid: quiet.ctl.states.slice(posts).filter(b => b.on === true && b.live === false).length,
                framePosts: quiet.ctl.states.slice(posts).filter(b => b.seg && !('on' in b)).length };
  quiet.$('go').onclick();

  // and no worker to be had: as it always was
  const lap3 = await open(data, { host: HOME, sockets: true });
  lap3.$('go').onclick();
  await wait();
  await hide(lap3);
  out.lapNoWorker = lap3.$('go').textContent;

  out.uncaught = uncaught;
  process.stdout.write(JSON.stringify(out));
  process.exit(0);
}
'''


def _run(js, stdin=""):
    """Run one of the harnesses above, or None when there is no node."""
    if not shutil.which("node"):
        return None
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "harness.js")
        with open(path, "w") as f:
            f.write(js)
        p = subprocess.run(["node", path, OFFLINE], input=stdin,
                           capture_output=True, text=True, timeout=180)
    if p.returncode:
        raise AssertionError("harness failed:\n%s" % p.stderr[-2000:])
    res = json.loads(p.stdout)
    if "crashed" in res:
        raise AssertionError("harness crashed:\n%s" % res["crashed"][-2000:])
    return res


_CACHE = {}


def _page():
    """The page run once (about twenty seconds of it) for every test."""
    if "page" not in _CACHE:
        import mau5offline
        _CACHE["page"] = _run(PAGE_JS, json.dumps(mau5offline.bundle()))
    return _CACHE["page"]


def _standby():
    if "standby" not in _CACHE:
        import mau5offline
        _CACHE["standby"] = _run(STANDBY_JS, json.dumps(mau5offline.bundle()))
    return _CACHE["standby"]


def _list():
    if "list" not in _CACHE:
        import mau5offline
        _CACHE["list"] = _run(LIST_JS, json.dumps(mau5offline.bundle()))
    return _CACHE["list"]


def _wire():
    if "wire" not in _CACHE:
        _CACHE["wire"] = _run(WIRE_JS)
    return _CACHE["wire"]


def t_page_loop_survives():
    """The render loop never dies silently: it skips, or it lets go."""
    r = _page()
    if r is None:
        return note("page: node not installed, the page went unrun")
    eq(r["uncaught"], [], "an exception escaped the page")
    c = r["cycle"]
    ok(c["presets"] >= 4, "cycling after a colour change reached only %d presets"
       " -- the loop died carrying one preset's params into the next" % c["presets"])
    eq(c["running"], "stop", "the page stopped while cycling")
    ok(c["framesLate"] >= 3, "frames stopped while cycling (%d in the last 0.4 s)"
       % c["framesLate"])
    eq(c["released"], 0, "the helmet was let go while cycling")
    b = r["badText"]
    ok("cannot use sprite" in b["warn"], "a sprite this build lacks was not refused: %r"
       % b["warn"])
    ok(b["framesLate"] >= 2 and b["running"] == "stop",
       "a refused text value stopped the frames")
    t = r["throws"]
    eq(t["running"], "start", "a render that always throws must stop the player")
    ok(t["releases"] >= 1, "a render that always throws must hand the helmet back")
    eq(t["framesAfter"], 0, "frames went on after the player stopped")
    ok("kept failing" in t["warn"], "the page did not say why it stopped: %r" % t["warn"])


def t_page_start_and_stop():
    """Never started from a hidden page; stop cancels a start on its way."""
    r = _page()
    if r is None:
        return
    eq(r["hiddenStart"]["layouts"], 0, "a hidden page took the helmet")
    eq(r["cancelLabel"], "stop", "the button should say stop while starting")
    c = r["cancel"]
    eq(c["running"], "start", "stop during a start did not stop it")
    eq(c["last"], "release", "the last word to the controller after a cancelled "
       "start must be a release, or begin's layout latches the frame")
    eq(c["framesLate"], 0, "a cancelled start streamed anyway")


def t_page_follows_spotify_safely():
    """Following Spotify neither undoes a stop nor streams from the background."""
    r = _page()
    if r is None:
        return
    f = r["follow"]
    ok(f["running"] == "stop" and f["show"], "following did not start the matched show")
    s = r["followStop"]
    eq(s["running"], "start", "stop was undone by following")
    eq(s["layoutsAfter"], 0, "following started the helmet again after stop")
    eq(s["button"], "follow Spotify", "stop should end following")
    h = r["followHidden"]
    eq(h["wasRunning"], "stop", "following did not start again when asked")
    eq(h["running"], "start", "hiding the page did not stop the helmet")
    eq(h["layoutsWhileHidden"], 0, "following restarted the helmet from a hidden page")
    eq(r["followBack"]["running"], "stop", "following did not pick up once visible")
    ok("out of sight" in r["followBack"]["warn"],
       "the page did not say why the helmet had stopped")
    eq(r["pausedRunning"], "stop", "the player should run while Spotify is paused")
    eq(r["paused"], ["0:42"], "a paused track should hold the show where it is")
    eq(r["noShow"]["showgo"], "start", "a song with no show should stop the show")
    eq(r["noShow"]["running"], "stop", "and leave the presets running")
    eq(json.loads(r["spotify"]["stored"]),
       {"c": "0123456789abcdef0123456789abcdef", "r": "AQDrefreshTOKEN"},
       "the handoff line pasted with its indent")


def t_page_holds_the_screen():
    """No wake lock on plain http: the video holds the screen, and says so."""
    r = _page()
    if r is None:
        return
    ok(r["video"], "no video element was put up to hold the screen")
    eq(r["screen"], "video", "the page should say what holds the screen")


def t_page_late_pongs():
    """A late pong is not credited to a newer frame, so the queue stays known."""
    r = _wire()
    if r is None:
        return note("page: node not installed, the link went unchecked")
    L = r["late"]
    ok(L["full"] and L["stalled"] and L["stillBusy"],
       "nothing new may go out while given-up frames' pongs may still come")
    eq(L["owed"], 2, "both frames behind the stall are owed")
    ok(L["freed"] and L["ready"] >= 1, "the last late pong should free the player")
    eq(L["afterSend"], 1, "one frame on its way after the stall")
    eq(L["afterOwn"], 0, "its own pong is what acknowledges it")
    eq(L["stray"], 0, "a stray pong with nothing waiting changes nothing")
    lo = r["lost"]
    ok(lo["during"] and lo["quiet"] and not lo["after"],
       "pongs that never come must be given up on after the quiet time")
    for k, s in sorted(r["stall"].items()):
        eq(s["after"]["thinks"], s["after"]["real"],
           "%s: after the stall the page believes %d queued, really %d"
           % (k, s["after"]["thinks"], s["after"]["real"]))
        eq(s["worst"], 0, "%s: the page under-counted the queue" % k)
        ok(s["after"]["lag"] <= s["before"]["lag"] + 10,
           "%s: the helmet trails the music by %d ms after the stall, %d before"
           % (k, s["after"]["lag"], s["before"]["lag"]))
    note("page: after 1.2 and 2.2 s controller stalls the queue is known exactly, "
         "%d ms behind as before" % r["stall"]["s2200"]["after"]["lag"])


def t_page_deadman():
    """Armed with the layout, re-armed quietly, and lights the helmet again."""
    r = _wire()
    if r is None:
        return
    d = r["deadman"]
    ok(d["layoutArms"], "the layout POST must arm the dead man itself")
    ok(d["layoutFrozen"], "the layout freezes every segment")
    eq(d["normal"], ["nl", "nl"], "a normal re-arm touches only the nightlight")
    ok(d["revive"] is not None, "after a dropout nothing turned the helmet back on")
    eq(d["revive"]["bri"], 180, "the helmet comes back at the page's brightness")
    ok(d["revive"]["nl"], "and with the dead man armed in the same request")
    ok(d["revive"]["frozen"], "and every segment frozen in it, or WLED's "
       "turn-on unfreeze lets the effect paint over the frames")
    eq(d["revived"], 1, "the page should count the revival so it can say so")
    ok(d["wholeNext"], "the frame after a revival must go whole")
    eq(d["normalAgain"], ["nl", "nl"], "after the revival, arms are quiet again")
    # (live:false leaves realtime at once -- WLED 16's binary frames are
    # realtime -- and is harmless on 0.15.4)
    eq(d["afterRelease"][-1].split(","), ["live", "nl", "on", "seg"],
       "an arm on its way at release must not arm or light after it: %s"
       % d["afterRelease"])


def t_page_requests_time_out():
    """A controller that never answers fails a start rather than hanging it."""
    r = _wire()
    if r is None:
        return
    t = r["timeouts"]
    for k in ("get", "post", "begin"):
        ok("no answer" in t[k], "%s did not time out: %r" % (k, t[k]))
    ok(t["ms"] < 3000, "the timeouts took %.0f ms" % t["ms"])


def t_page_spotify_parsing():
    """The handoff line however it was copied; the clock from mid-request."""
    r = _wire()
    if r is None:
        return
    s = r["spotify"]
    want = ["0123456789abcdef0123456789abcdef", "AQDrefreshTOKENxyz"]
    eq(s["paste"], want, "pasted with its indent")
    eq(s["wrapped"], want, "pasted with a line break in it")
    eq(s["junk"], "refused", "a line with no client id should be refused")
    eq(s["at"], 10200, "the position should be stamped mid-request")
    ok(abs(s["pos"] - 60.2) < 1e-6, "position carried forward from mid-request: %r"
       % s["pos"])
    eq(s["wait"], 7000, "a 429 should wait as long as Retry-After says")
    eq(s["asked"], 1, "a poll inside the wait must not ask Spotify again")
    eq(s["waitAfter"], 0, "and the wait should end")


def t_page_standby_is_measured_and_fits():
    """The button turns pacifica down until it fits what can be sustained.

    It can run for hours, so the figure is the sustained one: 11 W less
    the LEDs' own standby is 296 mA, and a tenth in hand is 266.
    """
    r = _standby()
    if r is None:
        return note("no node: page not run")
    eq(r["uncaught"], [], "uncaught")
    f = r["fits"]
    eq(f["bri"], 36, "672 mA at 96 scales to this: %s" % f["says"])
    eq(len(f["saves"]), 1, "one preset saved")
    s = f["saves"][0]
    ok(s["ib"] is True and s["sb"] is True, "saved without brightness or bounds: %s" % s)
    eq(f["cfgs"], [{"def": {"ps": s["psave"], "on": True, "bri": 36}}], "boot preset")
    ok(f["on"] is True, "left dark after saving")
    eq(f["release"].get("ps"), s["psave"], "stopping must hand back to it: %s" % f["release"])
    ok("about 252 mA" in f["says"], f["says"])
    gone = [g for g in f["segs"] if g.get("stop") == 0]
    eq([g["id"] for g in gone], [3], "leftover segments must go")
    eq(r["firstTry"]["bri"], 96, "fits at the first brightness tried")
    eq(r["stale"]["bri"], 36, "a stale black reading must not hide the glow's current")


def t_page_standby_refuses_what_it_cannot_vouch_for():
    r = _standby()
    if r is None:
        return note("no node: page not run")
    n = r["noEstimate"]
    eq(n["bri"], 24, "an estimate that never moves is no measurement: %s" % n["says"])
    ok("no current estimate" in n["says"], n["says"])
    eq(len(n["saves"]), 1, "still saved, dim")
    b = r["neverFits"]
    eq((b["saves"], b["cfgs"]), ([], []), "over budget was saved")
    ok(b["on"] is False, "left glowing over budget")
    ok(b["release"].get("on") is False and "ps" not in b["release"],
       "hand-back to a preset that was never saved: %s" % b["release"])
    ok("nothing was saved" in b["says"], b["says"])
    x = r["running"]
    eq(x["glows"], 0, "touched the controller while the player runs")
    ok("stop the player" in x["says"], x["says"])
    i = r["interrupted"]
    eq((i["saves"], i["cfgs"]), ([], []), "saved the stream into the preset")
    ok("nothing was saved" in i["says"], i["says"])


def t_page_does_not_wait_on_a_laptop_that_is_gone():
    """The pointer on the controller can outlive the laptop's address."""
    r = _standby()
    if r is None:
        return note("no node: page not run")
    a = r["apStale"]
    eq(a["asked"], 0, "asked a house address from the helmet's Wi-Fi")
    eq(a["box"]["shown"], "block", "no prompt on the helmet's Wi-Fi")
    ok(a["box"]["btn"].startswith("load"), str(a["box"]))
    ok("getting" not in a["line"], a["line"])
    h = r["homeStale"]
    ok(h["asked"] >= 1, "never tried the laptop at the house")
    ok("nothing there answered" in h["line"], "hung on it: %s" % h["line"])
    ok(h["box"]["disabled"] is True and "laptop" in h["box"]["btn"], str(h["box"]))
    eq(r["apLaptopAsked"], 1, "a laptop on the helmet's Wi-Fi can answer")


def t_page_rides_out_a_dropout():
    """Losing the socket says so, keeps going, and picks up by itself."""
    r = _standby()
    if r is None:
        return note("no node: page not run")
    eq(r["uncaught"], [], "uncaught")
    eq(r["dropRunning"], "stop", "never started")
    x = r["dropLost"]
    ok("lost the helmet" in x["conn"] and x["cls"] == "bad", str(x))
    eq(x["running"], "stop", "gave up on the show")
    b = r["dropBack"]
    ok("back after" in b["conn"] and "1 dropout " in b["conn"], str(b))
    eq(b["running"], "stop", "stopped by the reconnect")
    ok(b["relaid"] >= 1, "the helmet was not put back on after the dropout")


def t_page_comes_back_when_it_is_in_front_again():
    """Nobody pressed stop, so being in front again starts it again."""
    r = _standby()
    if r is None:
        return note("no node: page not run")
    eq(r["hidden"], "start", "kept the helmet from a hidden page")
    eq(r["shown"]["go"], "stop", "did not come back: %s" % r["shown"]["warn"])
    ok("out of sight" in r["shown"]["warn"], r["shown"]["warn"])
    eq(r["pressedStop"], "start", "came back after stop was pressed")
    eq(r["backNoWifi"], "start", "started with no way to the helmet")
    eq(r["backWifi"], "stop", "did not keep trying until the Wi-Fi was back")


def t_page_binary_frames_leave_the_nightlight_off():
    """WLED 16's realtime mode stalls the timer, and it fires on the first gap."""
    r = _standby()
    if r is None:
        return note("no node: page not run")
    eq(r["keptNl"], 0, "armed the nightlight on the binary path")
    ok(r["keptOffNl"] >= 1, "did not clear a nightlight left running")
    b = r["keptBack"]
    ok(b["on"] is True and b["bri"] > 0, "a helmet that went off stayed off: %s" % b)
    ok("gone dark" in b["warn"], "the page did not say so: %r" % b["warn"])
    eq(r["keptStopped"], False, "turned the helmet back on after stop")


def t_page_offers_the_songs_for_offline():
    """At the house it offers to save them; on the helmet's WiFi it asks."""
    r = _standby()
    if r is None:
        return note("no node: page not run")
    ok(r["names"] >= 1, "no shows in the bundle")
    h = r["homeReady"]
    eq(h["shown"], "block", "no prompt at the house")
    ok(h["disabled"] is False and h["btn"].startswith("save"), str(h))
    a = r["afterSave"]
    eq(len(a["files"]), r["names"], "every song downloaded")
    eq(len(json.loads(a["stored"])["names"]), r["names"], "remembered")
    eq(a["box"]["shown"], "block", "the instructions must stay up")
    ok("4.3.2.1" in a["box"]["text"], a["box"]["text"])
    eq(a["later"], "got it", "dismiss label")
    eq(r["afterGotIt"], "none", "dismiss")
    eq(r["homeSaved"]["shown"], "none", "asked again after saving")
    n = r["oneNew"]
    ok("Save the 1 show song" in n["text"], n["text"])
    eq(n["files"], 1, "a new song downloaded the ones already on the phone")
    eq(n["stored"], r["names"], "forgot the songs saved before")
    w = r["homeWaiting"]
    eq(w["shown"], "block", "silent while songs are missing")
    ok(w["disabled"] is True and "laptop" in w["btn"], str(w))
    p = r["apMissing"]
    eq(p["shown"], "block", "no prompt on the helmet's WiFi")
    ok(p["btn"].startswith("load"), str(p))
    eq(r["apPicked"], 1, "the button must open the file picker")
    eq(r["apReady"]["shown"], "none", "asked with every song here")
    eq(r["apiAP"]["shown"], "block", "?api= pointing at the helmet counts as the helmet")


def t_page_play_music():
    """One tap: every song in the set's order, on one audio element, round and round."""
    r = _list()
    if r is None:
        return note("no node: page not run")
    eq(r["uncaught"], [], "uncaught errors")
    n = r["none"]
    ok("Play Music" in n["label"] and n["go"] != "stop", str(n))
    ok("no songs" in n["says"], n["says"])
    u = r["unlock"]
    eq(u["made"], 1, "the tap must make the element at once")
    ok(u["src"].startswith("data:audio"), "the tap must start it at once: %s" % u["src"])
    f = r["first"]
    eq(f["src"], f["want"], "the first song")
    ok("Stop" in f["label"] and f["go"] == "stop", str(f))
    ok(f["says"].startswith("1 of "), f["says"])
    eq(f["next"], False, "skip stays off during a set")
    eq(r["walked"], r["want"], "the order, and round again")
    eq(r["elements"], 1, "a phone only lets one element play without a tap")
    eq(r["wired"], 1, "an element can only go into the graph once")
    eq(r["stillGoing"], "stop", "the helmet stops between songs")
    eq(r["prevRestart"]["t"], 0, "back starts the song again first")
    ok(r["prevBack"] != r["prevRestart"]["src"], "back at the start goes to the song before")
    ok("Stop" in r["jumped"]["on"], "picking a song ended the set")
    ok(r["afterError"]["src"] != r["jumped"]["src"], "a song that broke was not skipped")
    ok("could not go on playing" in r["afterError"]["warn"], r["afterError"]["warn"])
    s = r["stopped"]
    ok("Play Music" in s["label"] and s["go"] == "start" and s["paused"], str(s))
    eq(r["startAfterSet"]["go"], "stop", "start after the set")
    ok(r["startAfterSet"]["paused"], "start after the set played a song")
    ok(r["footer"]["paused"] and "Play Music" in r["footer"]["label"], str(r["footer"]))
    ok(r["boxFooter"]["playing"] and r["boxFooter"]["paused"], str(r["boxFooter"]))
    ok(r["joined"]["t"] == 42 and r["joined"]["again"] == 0 and "Stop" in r["joined"]["label"],
       "Play Music restarted the song already playing: %s" % r["joined"])
    eq(r["joinedNext"]["src"], r["joinedNext"]["want"], "the set did not carry on from it")
    ok("Play Music" in r["preset"]["label"] and r["preset"]["paused"], str(r["preset"]))
    ok("Play Music" in r["taken"], "silence left the set waiting: %s" % r["taken"])
    eq(r["some"]["walked"], r["some"]["want"], "only the songs here, round again")
    ok("more not on this device" in r["some"]["says"], r["some"]["says"])
    eq(r["skipped"]["src"], r["skipped"]["want"], "a song that will not play is skipped")
    ok("Play Music" in r["dead"]["label"] and "none of the songs" in r["dead"]["says"], str(r["dead"]))


def t_page_gets_past_a_silent_socket():
    """A link that dies without the socket being told, and comes back: not until a reload."""
    r = _list()
    if r is None:
        return note("no node: page not run")
    p = r["quietPatient"]
    eq(p["closes"], 0, "gave up on a socket that may only be slow")
    q = r["quiet"]
    eq(q["closes"], 1, "kept waiting on a socket that had gone silent")
    ok(q["sockets"] >= 1, "no new socket: %s" % q)
    eq(q["old"], 3, "the silent socket was left open")
    ok(q["flowing"] > 0, "frames did not move to the new socket: %s" % q)
    eq(q["go"], "stop", "a silent socket stopped the helmet")
    ok(q["relaid"] >= 1, "the layout was not sent again: %s" % q)
    eq(q["framePosts"], 0, "whole frames as JSON on a link already in trouble")


def t_page_out_of_sight():
    """A phone stops the lights when hidden; a laptop's window being covered does not."""
    r = _list()
    if r is None:
        return note("no node: page not run")
    eq(r["phoneWorkers"], 0, "a phone gets no worker clock")
    h = r["phoneHidden"]
    eq(h["go"], "start", "a hidden phone keeps streaming on no timers")
    eq(h["paused"], False, "hiding must not stop the song")
    eq(r["phoneNext"]["src"], r["phoneNext"]["want"], "the set stops with the screen off")
    b = r["phoneBack"]
    eq(b["go"], "stop", "the lights come back with the page")
    ok(not b["paused"] and b["ctx"] == "running", "a song the browser paused stays paused: %s" % b)
    eq(r["phonePaused"], True, "a pause somebody tapped was undone")
    eq(r["lapWorkers"], 1, "a laptop has no clock for when it is hidden")
    l = r["lapHidden"]
    eq(l["go"], "stop", "covering the window stopped the helmet")
    ok(l["frames"] > 3, "hidden, it stopped sending: %s" % l)
    ok(l["ticks"] > 3, "hidden, it is not on the worker's clock: %s" % l)
    eq(l["paused"], False, "hidden, the song stopped")
    ok("out of sight" not in l["warn"], "nothing went wrong, so nothing to say: %s" % l["warn"])
    ok(r["lapShown"]["frames"] > 2 and r["lapShown"]["go"] == "stop", str(r["lapShown"]))
    eq(r["lapPreset"], "stop", "a preset on a covered laptop stopped")
    eq(r["lapNoWorker"], "start", "no worker: a hidden page's timers cannot carry it")


GROUP = [t_page_play_music, t_page_out_of_sight, t_page_gets_past_a_silent_socket,
         t_page_loop_survives, t_page_start_and_stop, t_page_follows_spotify_safely,
         t_page_holds_the_screen, t_page_late_pongs, t_page_deadman,
         t_page_requests_time_out, t_page_spotify_parsing,
         t_page_standby_is_measured_and_fits,
         t_page_standby_refuses_what_it_cannot_vouch_for,
         t_page_offers_the_songs_for_offline,
         t_page_does_not_wait_on_a_laptop_that_is_gone,
         t_page_rides_out_a_dropout,
         t_page_comes_back_when_it_is_in_front_again,
         t_page_binary_frames_leave_the_nightlight_off]
