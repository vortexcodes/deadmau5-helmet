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
    eq(d["afterRelease"][-1].split(","), ["nl", "on", "seg"],
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


GROUP = [t_page_loop_survives, t_page_start_and_stop, t_page_follows_spotify_safely,
         t_page_holds_the_screen, t_page_late_pongs, t_page_deadman,
         t_page_requests_time_out, t_page_spotify_parsing]
