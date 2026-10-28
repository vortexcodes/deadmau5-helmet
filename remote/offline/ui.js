// ui.js -- the page: pick an animation, watch it, stop it.
//
// Written for one situation: standing in a dark room holding a phone,
// wearing or looking at the helmet, with no laptop and no network.
// So: big targets, no menus, the stop button always reachable, and
// every number that matters on screen rather than in a console nobody
// can open.
//
// The preview is not decoration.  When the link is slow it is the only
// way to tell "the phone has stopped rendering" from "the controller
// has stopped listening", and those have different fixes.

'use strict';

(function () {

const D = globalThis.MAU5_DATA;
const M = globalThis.MAU5;

function dec(b64, C) {
  const bin = atob(b64);
  const buf = new ArrayBuffer(bin.length);
  const v = new Uint8Array(buf);
  for (let i = 0; i < bin.length; i++) v[i] = bin.charCodeAt(i);
  return new C(buf);
}

const geo = { n: D.n, regions: D.regions };
for (const k of Object.keys(D.f32)) geo[k] = dec(D.f32[k], Float32Array);
for (const k of Object.keys(D.i16)) geo[k] = dec(D.i16[k], Int16Array);

const helmet = M.makeHelmet(geo);
const guard = new M.PowerGuard(D.power);
const frame = new Float32Array(helmet.n * 3);

const link = new M.Link({ count: helmet.n, strips: D.strips });

const $ = (id) => document.getElementById(id);
const state = {
  preset: null, inst: null, params: {}, running: false,
  t0: 0, bri: 255, fps: 0, cycle: 0, lastCycle: 0, interval: 40,
};

// ----------------------------------------------------------------------
// preview
// ----------------------------------------------------------------------
const cv = $('view'), cx = cv.getContext('2d');
let dots = null;

function layout() {
  const w = cv.clientWidth, h = Math.round(cv.clientWidth * 0.62);
  cv.width = w * devicePixelRatio; cv.height = h * devicePixelRatio;
  cv.style.height = h + 'px';
  let x0 = Infinity, x1 = -Infinity, y0 = Infinity, y1 = -Infinity;
  for (let i = 0; i < helmet.n; i++) {
    x0 = Math.min(x0, helmet.px[i]); x1 = Math.max(x1, helmet.px[i]);
    y0 = Math.min(y0, helmet.py[i]); y1 = Math.max(y1, helmet.py[i]);
  }
  const pad = 10 * devicePixelRatio;
  const s = Math.min((cv.width - 2 * pad) / (x1 - x0), (cv.height - 2 * pad) / (y1 - y0));
  dots = new Float32Array(helmet.n * 2);
  for (let i = 0; i < helmet.n; i++) {
    dots[i * 2] = pad + (helmet.px[i] - x0) * s;
    dots[i * 2 + 1] = cv.height - pad - (helmet.py[i] - y0) * s;
  }
  dots.r = Math.max(1.6, 5.2 * s / 3.2);
}

function draw() {
  if (!dots) layout();
  cx.fillStyle = '#07070a';
  cx.fillRect(0, 0, cv.width, cv.height);
  const r = dots.r;
  for (let i = 0; i < helmet.n; i++) {
    const v = Math.max(frame[i * 3], Math.max(frame[i * 3 + 1], frame[i * 3 + 2]));
    if (v < 1) {
      cx.fillStyle = '#17171d';
    } else {
      // the strips are diffused, so a dot that is merely the raw value
      // reads far darker than the helmet does -- lift it like the
      // diffusion does
      const g = 0.45;
      cx.fillStyle = 'rgb(' + Math.round(255 * Math.pow(frame[i * 3] / 255, g))
        + ',' + Math.round(255 * Math.pow(frame[i * 3 + 1] / 255, g))
        + ',' + Math.round(255 * Math.pow(frame[i * 3 + 2] / 255, g)) + ')';
    }
    cx.beginPath();
    cx.arc(dots[i * 2], dots[i * 2 + 1], r, 0, 6.2832);
    cx.fill();
  }
}

// ----------------------------------------------------------------------
// the loop
// ----------------------------------------------------------------------
// Not requestAnimationFrame.  rAF is a drawing clock: the browser
// throttles it when the page is not composited -- a backgrounded tab
// gets 1 Hz, and some embedded views give about 5 Hz even in front --
// and what is being paced here is a network send, not a repaint.  A
// timer whose interval moves with what the controller will actually
// take is both honest about the bottleneck and immune to that.
//
// The interval is found rather than declared, because the limit is an
// ESP32 parsing JSON and it depends on the preset: a frame of `solid`
// is 88 characters and a frame of `fire` is nearly four thousand.
// Backing off on refusal and creeping back up on success finds the
// edge for whatever is playing, in a second or two, with no number
// anybody has to guess.
// alignbar and stripid exist to find a misplaced LED, and countdown
// counts down; none of them is something to walk into at a party.
const NOT_IN_CYCLE = { alignbar: 1, stripid: 1, countdown: 1 };
const CYCLE_THROUGH = Object.keys(D.presets).filter(n => !NOT_IN_CYCLE[n]);

const FLOOR_MS = 1000 / 30;     // never ask for more than 30 fps
const ROOF_MS = 250;            // never give up entirely
let frames = 0, lastReport = 0, lastDraw = 0, timer = null;

function tick() {
  if (!state.running) return;
  const now = performance.now();
  const t = (now - state.t0) / 1000;

  if (state.cycle && t - state.lastCycle > state.cycle) {
    state.lastCycle = t;
    const names = CYCLE_THROUGH;
    const at = names.indexOf(state.preset);
    choose(names[(at + 1) % names.length], true);
  }

  frame.fill(0);
  state.inst.render(helmet, t, null, frame);
  const rep = guard.apply(frame, frame, now / 1000);
  const sent = link.send(frame);

  if (sent < 0) state.interval = Math.min(ROOF_MS, state.interval * 1.15);
  else state.interval = Math.max(FLOOR_MS, state.interval * 0.97);
  if (sent > 0) frames++;

  // The preview is for the person holding the phone, not for the
  // helmet, so it does not need the frame rate the helmet gets.
  if (now - lastDraw > 80) { lastDraw = now; draw(); }

  if (now - lastReport > 500) {
    state.fps = frames * 1000 / (now - lastReport);
    frames = 0; lastReport = now;
    $('fps').textContent = state.fps.toFixed(0);
    $('ma').textContent = rep.total_ma.toFixed(0);
    $('w').textContent = rep.watts.toFixed(1);
    $('therm').textContent = rep.thermal ? rep.thermal.full_pct.toFixed(0) + '%' : '-';
    $('drop').textContent = link.failed;
    $('bar').style.width = Math.min(100, rep.total_ma / 16.0) + '%';
  }

  const spent = performance.now() - now;
  timer = setTimeout(tick, Math.max(2, state.interval - spent));
}

// ----------------------------------------------------------------------
// controls
// ----------------------------------------------------------------------
function rgbHex(c) {
  return '#' + c.map(v => Math.round(v).toString(16).padStart(2, '0')).join('');
}
function hexRgb(s) {
  return [parseInt(s.slice(1, 3), 16), parseInt(s.slice(3, 5), 16),
          parseInt(s.slice(5, 7), 16)];
}

function buildControls(name) {
  const box = $('params');
  box.innerHTML = '';
  for (const s of D.presets[name].spec) {
    const row = document.createElement('label');
    row.className = 'row';
    const tag = document.createElement('span');
    tag.textContent = s.name.replace(/_/g, ' ');
    row.appendChild(tag);
    let el;
    if (s.kind === 'color') {
      el = document.createElement('input');
      el.type = 'color'; el.value = rgbHex(state.params[s.name] || s.value);
      el.oninput = () => set(s.name, hexRgb(el.value));
    } else if (s.kind === 'bool') {
      el = document.createElement('input');
      el.type = 'checkbox'; el.checked = !!(state.params[s.name] ?? s.value);
      el.onchange = () => set(s.name, el.checked);
    } else if (s.kind === 'number') {
      el = document.createElement('input');
      el.type = 'range'; el.min = s.min; el.max = s.max; el.step = s.step;
      el.value = state.params[s.name] ?? s.value;
      const out = document.createElement('b');
      out.textContent = (+el.value).toFixed(2).replace(/\.?0+$/, '');
      el.oninput = () => {
        out.textContent = (+el.value).toFixed(2).replace(/\.?0+$/, '');
        set(s.name, +el.value);
      };
      row.appendChild(out);
    } else {
      el = document.createElement('input');
      el.type = 'text'; el.value = state.params[s.name] ?? s.value;
      el.onchange = () => set(s.name, el.value);
    }
    row.appendChild(el);
    box.appendChild(row);
  }
}

function set(k, v) {
  state.params[k] = v;
  state.inst = M.make(state.preset, state.params, helmet, D.fonts);
  save();
}

function choose(name, keepParams) {
  state.preset = name;
  if (!keepParams) state.params = {};
  state.inst = M.make(name, state.params, helmet, D.fonts);
  for (const b of document.querySelectorAll('#grid button'))
    b.classList.toggle('on', b.dataset.name === name);
  $('now').textContent = name;
  buildControls(name);
  save();
}

function save() {
  try {
    localStorage.setItem('mau5offline', JSON.stringify({
      preset: state.preset, params: state.params, bri: state.bri,
      cycle: state.cycle,
    }));
  } catch (e) {}
}

function restore() {
  try {
    const s = JSON.parse(localStorage.getItem('mau5offline') || '{}');
    if (s.preset && D.presets[s.preset]) {
      state.params = s.params || {};
      state.cycle = s.cycle || 0;
      state.bri = s.bri || 255;
      return s.preset;
    }
  } catch (e) {}
  return null;
}

// ----------------------------------------------------------------------
// connection
// ----------------------------------------------------------------------
function say(msg, cls) {
  const el = $('conn');
  el.textContent = msg;
  el.className = cls || '';
}

async function connect() {
  say('looking for the controller...');
  let hi;
  try {
    hi = await link.hello();
  } catch (e) {
    say('no controller at ' + (location.host || 'this address') +
        ' -- is the phone on the helmet\'s WiFi?', 'bad');
    return false;
  }
  const bits = [hi.name || 'WLED', 'v' + (hi.ver || '?'),
                hi.count + ' LEDs', hi.ws ? 'websocket' : 'http'];
  say(bits.join(' · '), 'good');
  const warn = [];
  if (hi.count !== helmet.n)
    warn.push('controller says ' + hi.count + ' LEDs, the map has ' + helmet.n);
  if (!hi.covers)
    warn.push('segment 0 covers ' + hi.segStart + '..' + hi.segStop +
              ', not the whole chain');
  if (!hi.maxpwr)
    warn.push('no brightness limiter set on the controller -- ' +
              'run mau5offline.py config --apply');
  $('warn').textContent = warn.join('. ');
  $('warn').style.display = warn.length ? 'block' : 'none';
  return true;
}

// The screen going off is the end of the show: a backgrounded tab
// gets its timers throttled to roughly nothing, the last frame
// latches, and the dead man puts the helmet out a minute later.
// Holding a wake lock is the fix, and stopping cleanly when the page
// is hidden anyway is the honest fallback -- a helmet that goes dark
// when you pocket the phone is better than one that freezes on
// whatever frame it happened to be showing.
let wake = null;

async function holdScreen() {
  try {
    if (navigator.wakeLock && !wake) {
      wake = await navigator.wakeLock.request('screen');
      wake.addEventListener('release', () => { wake = null; });
    }
  } catch (e) { wake = null; }
}

function releaseScreen() {
  if (wake) { try { wake.release(); } catch (e) {} wake = null; }
}

async function start() {
  if (state.running) return;
  if (!await connect()) return;
  const frozen = await link.begin(state.bri);
  if (!frozen) {
    const w = $('warn');
    w.textContent = (w.textContent ? w.textContent + '. ' : '') +
      'this build did not freeze the segment, so its own effect will ' +
      'paint over the animation every third of a second';
    w.style.display = 'block';
  }
  state.running = true;
  holdScreen();
  state.t0 = performance.now();
  state.lastCycle = 0;
  state.interval = 40;
  lastReport = performance.now();
  $('go').textContent = 'stop';
  $('go').classList.add('stop');
  tick();
}

async function stop() {
  state.running = false;
  clearTimeout(timer);
  releaseScreen();
  $('go').textContent = 'start';
  $('go').classList.remove('stop');
  await link.release();
  // The helmet is dark now, so the preview must be too -- a preview
  // still showing the last frame is a preview that is lying.
  frame.fill(0);
  draw();
  $('fps').textContent = '0';
  $('ma').textContent = '0';
  $('w').textContent = '0';
  $('bar').style.width = '0%';
}

// ----------------------------------------------------------------------
// wiring up
// ----------------------------------------------------------------------
const grid = $('grid');
for (const name of Object.keys(D.presets)) {
  const b = document.createElement('button');
  b.textContent = name;
  b.dataset.name = name;
  b.onclick = () => choose(name);
  grid.appendChild(b);
}

$('go').onclick = () => (state.running ? stop() : start());
$('bri').oninput = (e) => {
  state.bri = +e.target.value;
  $('brival').textContent = state.bri;
  if (state.running) link.postJSON({ bri: state.bri }).catch(() => {});
  save();
};
$('cycle').onchange = (e) => { state.cycle = +e.target.value; save(); };

// Leaving must put the helmet out.  The segment is frozen, so without
// this the last frame stays lit until somebody pulls the plug.
addEventListener('pagehide', () => { if (state.running) link.release(); });
addEventListener('visibilitychange', () => {
  if (document.visibilityState === 'hidden' && state.running) stop();
});
addEventListener('resize', () => { dots = null; draw(); });

choose(restore() || 'rainbow', true);
$('bri').value = state.bri;
$('brival').textContent = state.bri;
$('cycle').value = state.cycle;
$('leds').textContent = helmet.n;
$('budget').textContent = D.power.budget_ma;
$('built').textContent = D.built;
layout(); draw();
connect();

})();
