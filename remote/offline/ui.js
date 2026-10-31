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

// Served by the controller, the page and the API share an origin and
// none of this applies.  Served through mau5relay -- which is how it
// is reached from anywhere that is not the house -- the API lives
// under /helmet and needs the relay's token.
const Q = new URLSearchParams(location.search);
const link = new M.Link({
  count: helmet.n, strips: D.strips, standby: D.standby || null,
  origin: Q.get('api') || '', token: Q.get('t') || '',
  ackDelay: Number(Q.get('ackdelay')) || 0,   // testing: act like a phone
});
// For a console, or a bench driving the page from outside: what the
// link has sent, skipped, and had refused.
globalThis.MAU5_LINK = link;

const $ = (id) => document.getElementById(id);
const state = {
  preset: null, inst: null, params: {}, running: false,
  t0: 0, bri: 255, fps: 0, cycle: 0, lastCycle: 0,
  music: null, show: null, showT0: null, drive: null, follow: false,
  handover: true,
  // Where a show is held while Spotify is paused, in seconds; null when
  // it runs.
  showHold: null,
};

// ----------------------------------------------------------------------
// preview
// ----------------------------------------------------------------------
const cv = $('view'), cx = cv.getContext('2d');
let dots = null, view = null;

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
  view = { x0: x0, y0: y0, s: s, pad: pad };
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
// and what is being paced here is a network send, not a repaint.
//
// The pace is the controller's.  A frame is drawn only once it has
// finished the last one (link.busy), which it says by answering the
// player's ping, so a frame always shows the moment it was drawn for
// rather than queueing behind others -- and never more often than 30
// times a second.  A frame of `solid` is a few dozen characters and a
// frame of `fire` several kilobytes, and this finds the rate for each
// without anybody having to guess it.
const NOT_IN_CYCLE = { alignbar: 1, stripid: 1, countdown: 1 };
const CYCLE_THROUGH = Object.keys(D.presets).filter(n => !NOT_IN_CYCLE[n]);

const FLOOR_MS = 1000 / 30;     // never ask for more than 30 fps
let frames = 0, lastReport = 0, lastDraw = 0, lastFrame = 0, timer = null;
let parked = false;             // waiting on the controller, not on a timer
let revivedSaid = 0;            // link.revived, as last reported
link.onready = () => {
  if (state.running && parked) { parked = false; clearTimeout(timer); tick(); }
};

// A laptop's window can be covered by another one, or its tab changed, and the
// helmet should not notice: browsers call that hidden, and it used to stop the
// helmet as if a phone had gone into a pocket.  A hidden page's timers run about
// once a second, but a worker's do not, so on a machine with no touch screen a
// little worker keeps the time while the page is out of sight.  A phone stays
// as it was: when it hides its timers stop altogether, whoever asks.
const POCKET = (navigator.maxTouchPoints || 0) > 0;
let clock = null, clockSeq = 0;
if (!POCKET && typeof Worker === 'function') {
  try {
    clock = new Worker(URL.createObjectURL(new Blob(
      ['onmessage=function(e){setTimeout(function(){postMessage(e.data.seq)},e.data.ms)}'],
      { type: 'text/javascript' })));
    clock.onmessage = (e) => { if (e.data === clockSeq) tick(); };
    // A wake-up owed by a worker that died never comes: the timers take over.
    clock.onerror = () => { clock = null; if (state.running) later(40); };
  } catch (e) { clock = null; }
}

// The next frame, and only one: an older wake-up still on its way is ignored.
function later(ms) {
  clearTimeout(timer);
  clockSeq++;
  if (clock && document.visibilityState === 'hidden') clock.postMessage({ seq: clockSeq, ms: ms });
  else timer = setTimeout(tick, ms);
}

// Does being out of sight stop the helmet here?
function hiddenStops() { return document.visibilityState === 'hidden' && !clock; }

// Nothing may leave the loop without either scheduling the next frame
// or letting go of the helmet.  An exception used to do neither:
// state.running stayed true with no timer pending, the frozen segments
// held the last frame, and the dead man -- re-armed only by sends --
// put the helmet out about a minute later while the page still said
// 'stop'.  Cycling after moving any slider did it every time.  Now a
// frame that throws is skipped, so the helmet keeps the last good one
// (which the guard passed), and a fault that repeats hands the helmet
// back and says why.
let tickFails = 0;
const TICK_FAILS_MAX = 3;

// The socket can go from under a running show, usually because the phone
// left the helmet's Wi-Fi.  link.send() keeps trying on its own and the
// show carries on when it is back, so all this does is say so: a helmet
// that went dark with a page still showing a frame rate looks like a
// crash, and a count of dropouts tells the phone's Wi-Fi from the show.
let lostAt = 0, dropouts = 0, linkLine = '', linkSaid = -1;

function watchLink(now) {
  if (link.ws && link.ws.readyState === 1) {
    if (lostAt) {
      say(linkLine + ' · back after ' + Math.round((now - lostAt) / 1000) + ' s, ' +
          dropouts + ' dropout' + (dropouts > 1 ? 's' : '') + ' so far', 'good');
      lostAt = 0;
    }
    return;
  }
  if (!linkLine) return;             // this controller never had a socket
  if (!lostAt) { lostAt = now; dropouts++; linkSaid = -1; }
  const s = Math.floor((now - lostAt) / 1000);
  if (s >= 2 && s !== linkSaid) {
    linkSaid = s;
    say('lost the helmet ' + s + ' s ago, still trying -- ' +
        (onAP ? 'check this phone is still on the helmet\'s Wi-Fi'
              : 'check this phone can still reach it'), 'bad');
  }
}

function tick() {
  if (!state.running) return;
  try {
    step();
  } catch (e) {
    clearTimeout(timer);
    const why = String((e && e.message) || e);
    if (++tickFails >= TICK_FAILS_MAX) {
      tickFails = 0;
      unfollow();               // or Spotify following starts it straight back
      stop();
      pageWarn('stopped: the animation kept failing (' + why + ')');
      return;
    }
    pageWarn('a frame failed and was skipped (' + why + ')');
    if (state.running) later(100);
  }
}

function step() {
  const now = performance.now();
  watchLink(now);
  if (link.busy(now)) {
    // woken by the pong; the timer only covers one that never comes
    parked = true;
    later(50);
    return;
  }
  parked = false;
  if (now - lastFrame < FLOOR_MS) {
    later(FLOOR_MS - (now - lastFrame));
    return;
  }
  lastFrame = now;
  const t = (now - state.t0) / 1000;

  if (state.cycle && t - state.lastCycle > state.cycle) {
    state.lastCycle = t;
    const names = CYCLE_THROUGH;
    const at = names.indexOf(state.preset);
    // Each preset starts from its own defaults: the params on hand are
    // the last preset's, and make() refuses a name it does not have
    // ('blades has no parameter floor').
    choose(names[(at + 1) % names.length]);
  }

  // A show's beat pulse is applied after the guard, which would flatten
  // it -- but only to a frame the show drew.  Read whenever a show was
  // picked, it went on dimming the plain presets after the show
  // stopped, by wherever in the beat its last frame fell (to 0.66).
  let gain = 1;
  if (state.show && (state.showT0 !== null || an.el)) {
    // The track, when there is one, IS the clock.  Reading the audio
    // element's own currentTime cannot drift from the sound the room
    // is hearing, which a wall clock started by hand always does --
    // and it makes pause, seek and volume somebody else's problem.
    const st = an.el ? an.el.currentTime
      : state.showHold !== null ? state.showHold
      : (now - state.showT0) / 1000;
    if (st >= state.show.duration && !an.el) {
      stopShow();
      frame.fill(0);
      state.inst.render(helmet, t, state.music, frame);
    } else {
      const cue = state.show.frame(st, state.drive || state.music, frame);
      showClock(st, cue);
      if (state.show.gain !== undefined) gain = state.show.gain;
    }
  } else {
    frame.fill(0);
    // Between two songs of the set: dark, not a burst of whatever preset
    // happened to be picked.
    if (!list.on) state.inst.render(helmet, t, state.music, frame);
  }
  const rep = guard.apply(frame, frame, now / 1000, gain);
  const sent = link.send(frame);

  // 0 is a frame the helmet was already showing: delivered, for free
  if (sent >= 0) frames++;

  // The preview is for the person holding the phone, not for the
  // helmet, so it does not need the frame rate the helmet gets.
  if (now - lastDraw > 80) { lastDraw = now; draw(); }

  if (now - lastReport > 500) {
    state.fps = frames * 1000 / (now - lastReport);
    frames = 0; lastReport = now;
    $('fps').textContent = state.fps.toFixed(0);
    // How long a frame takes to reach the strip.  With one frame in
    // flight this is also what caps the frame rate: a phone whose WiFi
    // dozes shows 100 ms or more here, a laptop about 20.
    $('lag').textContent = link.rtt ? link.rtt.toFixed(0) + ' ms' : '-';
    $('ma').textContent = rep.total_ma.toFixed(0);
    $('w').textContent = rep.watts.toFixed(1);
    $('therm').textContent = rep.thermal ? rep.thermal.full_pct.toFixed(0) + '%' : '-';
    // Minutes of a bright effect, then two minutes of it fading to a third:
    // meant, and it would look like a fault if nothing said so.
    if (rep.thermal && rep.thermal.allowance_w < rep.thermal.top_w - 0.01)
      pageWarn('the heat limit is dimming this to what the helmet can hold for '
               + 'hours, and light comes back as it cools -- that is not a fault');
    $('drop').textContent = link.failed + link.refused;
    $('bar').style.width = Math.min(100, rep.total_ma / 16.0) + '%';
    if (link.revived !== revivedSaid) {
      revivedSaid = link.revived;
      pageWarn('the helmet had gone dark while this page was running -- '
               + 'turned it back on');
    }
  }

  tickFails = 0;
  // measured from when this frame started, so drawing it is not added on
  later(Math.max(0, FLOOR_MS - (performance.now() - now)));
}

// The eyes look where a finger points on the picture.  There is no motion
// sensor on the controller to steer them with, and a page on plain http gets
// none from the phone, so whoever is holding the phone does the looking.  Let
// go, and they carry on looking about by themselves.
let aimFree = null;

function aim(e) {
  if (state.preset !== 'eyes' || !view || !state.inst || state.showT0 !== null) return;
  const r = cv.getBoundingClientRect();
  const mmx = view.x0 + ((e.clientX - r.left) * cv.width / r.width - view.pad) / view.s;
  const mmy = view.y0 + (cv.height - view.pad - (e.clientY - r.top) * cv.height / r.height) / view.s;
  const p = state.inst.p;
  p.auto = 0;
  p.lx = Math.max(-70, Math.min(70, mmx * 0.5));
  p.ly = Math.max(-35, Math.min(45, (mmy - p.y) * 0.4));
  clearTimeout(aimFree);
}
let aiming = false;
cv.addEventListener('pointerdown', (e) => { aiming = true; aim(e); });
cv.addEventListener('pointermove', (e) => { if (aiming) aim(e); });
const letGo = () => {
  if (!aiming) return;
  aiming = false;
  clearTimeout(aimFree);
  aimFree = setTimeout(() => {
    if (state.preset === 'eyes' && state.inst) { state.inst.p.auto = 1; state.inst.p.lx = 0; state.inst.p.ly = 0; }
  }, 1500);
};
cv.addEventListener('pointerup', letGo);
cv.addEventListener('pointercancel', letGo);

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

// Only the params this preset has.  make() throws on any other, and
// params reach choose() from places written for something else: the
// last preset's, or localStorage after a build that renamed one --
// which used to throw at load, before connect(), and leave the page
// with no preset to render.
function ownParams(name, params) {
  const have = (D.presets[name] || {}).params || {};
  const out = {};
  for (const k of Object.keys(params || {})) if (k in have) out[k] = params[k];
  return out;
}

// A preset made and drawn once, off to one side, so a value it cannot
// use -- a sprite this build does not have, an axis it does not know,
// typed into a text box -- is refused here rather than thrown by the
// render loop at the helmet.
const scratch = new Float32Array(helmet.n * 3);
function tryMake(name, params) {
  const test = M.make(name, params, helmet, D.fonts);
  test.render(helmet, 0, state.music, scratch);
  return M.make(name, params, helmet, D.fonts);
}

function set(k, v) {
  const was = state.params;
  state.params = Object.assign({}, was, { [k]: v });
  try {
    state.inst = tryMake(state.preset, state.params);
  } catch (e) {
    state.params = was;
    pageWarn(state.preset + ' cannot use ' + k.replace(/_/g, ' ') + ' "' + v + '" ('
             + ((e && e.message) || e) + ')');
    return;
  }
  save();
}

function choose(name, keepParams) {
  state.preset = name;
  state.params = keepParams ? ownParams(name, state.params) : {};
  try {
    state.inst = tryMake(name, state.params);
  } catch (e) {
    // a saved value this build cannot use: its defaults instead
    state.params = {};
    state.inst = M.make(name, state.params, helmet, D.fonts);
  }
  for (const b of document.querySelectorAll('#grid button'))
    b.classList.toggle('on', b.dataset.name === name);
  // A finger on the picture steers the eyes, and must not scroll the page.
  cv.style.touchAction = name === 'eyes' ? 'none' : '';
  $('now').textContent = name;
  buildControls(name);
  save();
}

function save() {
  try {
    localStorage.setItem('mau5offline', JSON.stringify({
      preset: state.preset, params: state.params, bri: state.bri,
      cycle: state.cycle, handover: state.handover,
      show: $('showpick') ? $('showpick').value : '',
    }));
  } catch (e) {}
}

function restore() {
  try {
    const s = JSON.parse(localStorage.getItem('mau5offline') || '{}');
    if (s.handover !== undefined) state.handover = !!s.handover;
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

// A line added to the warning box, which connect() clears on the next
// start.  Said once however often it happens: a frame failing ten
// times a second is one thing to know, not ten.
function pageWarn(msg) {
  const w = $('warn');
  if (w.textContent.indexOf(msg) >= 0) return;
  w.textContent = (w.textContent ? w.textContent + '. ' : '') + msg;
  w.style.display = 'block';
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
                hi.count + ' LEDs',
                hi.ws ? (hi.binary ? 'binary frames' : 'websocket') : 'http'];
  say(bits.join(' · '), 'good');
  linkLine = hi.ws ? bits.join(' · ') : '';
  const warn = [];
  // More LEDs on the controller than in the map is a dark one at the
  // end (the helmet has 621 and WLED still drives 622).  Fewer is not:
  // the end of the map would never light.
  if (hi.count < helmet.n)
    warn.push('controller drives ' + hi.count + ' LEDs, the map has ' + helmet.n);
  if (!hi.maxpwr)
    warn.push('no brightness limiter set on the controller -- ' +
              'run mau5offline.py config --apply');
  if (D.standby && state.handover && !link.presets.has(String(D.standby)))
    warn.push('no standby glow saved on the controller, so stopping switches ' +
              'the helmet off -- tap "set up" next to standby glow, below');
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
//
// But navigator.wakeLock only exists on a secure page, and this one is
// plain http from the controller -- the reason it has no microphone
// either -- so on the helmet's own network the lock was never there:
// holdScreen() did nothing, said nothing, and the phone's auto-lock
// stopped the show 30 s to 2 min in.  Where it is missing the screen is
// held the way NoSleep.js holds it, with a video playing: two seconds
// of black, muted, inline and looped, behind the page (64x64, under a
// kilobyte each as WebM and MP4).  That is a technique rather than an
// API and it has not been proven on the show phone, so the page says
// which it is using, and says plainly when the screen going off is
// what stopped the helmet.
const AWAKE_WEBM = 'data:video/webm;base64,GkXfo59ChoEBQveBAULygQRC84EIQoKEd2VibUKHgQJChYECGFOAZwEAAAAAAAKcEU2bdLpNu4tTq4QVSalmU6yBoU27i1OrhBZUrmtTrIHGTbuMU6uEElTDZ1OsggEiTbuMU6uEHFO7a1OsggKG7AEAAAAAAABZAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAVSalmoCrXsYMPQkBNgIRMYXZmV0GETGF2ZkSJiECfQAAAAAAAFlSua9euAQAAAAAAAE7XgQFzxYgAAAAAAAAAAZyBACK1nIN1bmSIgQCGhVZfVlA4g4EBI+ODhAvrwgDgkLCBQLqBQJqBAlWwhFW5gQFV7oEA7AEAAAAAAAACAAASVMNn0HNzzWPAi2PFiAAAAAAAAAABZ8iYRaOHRU5DT0RFUkSHi0xhdmMgbGlidnB4Z8ihRaOIRFVSQVRJT05Eh5MwMDowMDowMi4wMDAwMDAwMDAAH0O2dUEJ54EAo6yBAACA8AIAnQEqQABAAABHCIWFiIWEiAICAAZwPEJgCrIg9zAA/v+iPFh5AKOWgQDIANEBAAEQEAAYABhYL/QACI6AAKOWgQGQANEBAAEQEAAYABhYL/QACI6AAKOWgQJYANEBAAEQEAAYABhYL/QACI6AAKOWgQMgANEBAAEQEAAYABhYL/QACI6AAKOWgQPoANEBAAEQEAAYABhYL/QACI6AAKOWgQSwANEBAAEQEAAYABhYL/QACI6AAKOWgQV4ANEBAAEQEBRgAGFgv9AAIjoAAKOWgQZAANEBAAEQEAAYABhYL/QACI6AAKOWgQcIANEBAAEQEAAYABhYL/QACI6AABxTu2uRu4+zgQC3iveBAfGCAXfwgQM=';
const AWAKE_MP4 = 'data:video/mp4;base64,AAAAIGZ0eXBpc29tAAACAGlzb21pc28yYXZjMW1wNDEAAAMpbW9vdgAAAGxtdmhkAAAAAAAAAAAAAAAAAAAD6AAAB9AAAQAAAQAAAAAAAAAAAAAAAAEAAAAAAAAAAAAAAAAAAAABAAAAAAAAAAAAAAAAAABAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAgAAAnh0cmFrAAAAXHRraGQAAAADAAAAAAAAAAAAAAABAAAAAAAAB9AAAAAAAAAAAAAAAAAAAAAAAAEAAAAAAAAAAAAAAAAAAAABAAAAAAAAAAAAAAAAAABAAAAAAEAAAABAAAAAAAAkZWR0cwAAABxlbHN0AAAAAAAAAAEAAAfQAAAAAAABAAAAAAHwbWRpYQAAACBtZGhkAAAAAAAAAAAAAAAAAAAoAAAAUABVxAAAAAAALWhkbHIAAAAAAAAAAHZpZGUAAAAAAAAAAAAAAABWaWRlb0hhbmRsZXIAAAABm21pbmYAAAAUdm1oZAAAAAEAAAAAAAAAAAAAACRkaW5mAAAAHGRyZWYAAAAAAAAAAQAAAAx1cmwgAAAAAQAAAVtzdGJsAAAAu3N0c2QAAAAAAAAAAQAAAKthdmMxAAAAAAAAAAEAAAAAAAAAAAAAAAAAAAAAAEAAQABIAAAASAAAAAAAAAABDExhdmMgbGlieDI2NAAAAAAAAAAAAAAAAAAAAAAAAAAAGP//AAAAMWF2Y0MBQsAe/+EAGGdCwB6mERCbARAAAAMAEAAAAwCg8WLhGAEABmjIQgOSyAAAABBwYXNwAAAAAQAAAAEAAAAUYnRydAAAAAAAAAH0AAAAAAAAABhzdHRzAAAAAAAAAAEAAAAKAAAIAAAAABRzdHNzAAAAAAAAAAEAAAABAAAAHHN0c2MAAAAAAAAAAQAAAAEAAAAKAAAAAQAAADxzdHN6AAAAAAAAAAAAAAAKAAAAGwAAAAoAAAALAAAACwAAAAsAAAALAAAACwAAAAsAAAALAAAACwAAABRzdGNvAAAAAAAAAAEAAANZAAAAPXVkdGEAAAA1bWV0YQAAAAAAAAAhaGRscgAAAAAAAAAAbWRpcmFwcGwAAAAAAAAAAAAAAAAIaWxzdAAAAAhmcmVlAAAAhW1kYXQAAAAXZYiCAj4jFAAEVfV999dddddddddddeAAAAAGQZocBHwjAAAAB0GaKgEfCMAAAAAHQZo7AR8IwAAAAAdBmkkAR8IwAAAAB0GaWUBHwjAAAAAHQZppgEfCMAAAAAdBmnnAR8IwAAAAB0GaiIAQ8IwAAAAHQZqYkD/CMA==';
let wake = null, awakeVideo = null;

function awakeEl() {
  if (awakeVideo) return awakeVideo;
  const v = document.createElement('video');
  // attributes as well as properties: iOS goes by the attributes
  for (const a of ['muted', 'loop', 'playsinline', 'webkit-playsinline',
                   'disablepictureinpicture', 'disableremoteplayback'])
    v.setAttribute(a, '');
  v.setAttribute('aria-hidden', 'true');
  v.muted = true; v.loop = true; v.playsInline = true;
  v.id = 'awake';
  for (const [type, url] of [['video/webm', AWAKE_WEBM], ['video/mp4', AWAKE_MP4]]) {
    const s = document.createElement('source');
    s.type = type; s.src = url;
    v.appendChild(s);
  }
  document.body.appendChild(v);
  awakeVideo = v;
  return v;
}

// What is keeping the screen on: 'held' (a wake lock), 'video' or
// 'free' (nothing).  Called first thing in start(), inside the tap,
// which is when a browser will play a video for a page.
async function holdScreen() {
  if (navigator.wakeLock) {
    try {
      if (!wake) {
        wake = await navigator.wakeLock.request('screen');
        wake.addEventListener('release', () => { wake = null; });
      }
      return 'held';
    } catch (e) { wake = null; return 'free'; }
  }
  try {
    await awakeEl().play();
    return 'video';
  } catch (e) {
    return 'free';
  }
}

function releaseScreen() {
  if (wake) { try { wake.release(); } catch (e) {} wake = null; }
  if (awakeVideo) { try { awakeVideo.pause(); } catch (e) {} }
}

function screenSays(how) {
  $('scr').textContent = { held: 'held', video: 'video', free: 'may lock' }[how] || '-';
  if (how === 'free')
    pageWarn('nothing is keeping this phone\'s screen on -- set its auto-lock '
             + 'to Never, or the helmet stops when the screen goes off');
}

// Said when the page comes back after hiding stopped the helmet, and
// again after the start that follows, which clears the warning box.
let stopNote = '';

// The start on its way, if one is: a second tap, or Spotify following
// once a second, joins it instead of starting another alongside -- on a
// slow controller start() takes seconds, and each extra one used to
// mean another begin() and another render loop.  `runs` is bumped by
// stop(), so a start still waiting on the controller can tell it was
// cancelled, and let go of whatever it had already taken.
let starting = null, startingRun = 0, runs = 0;

function start() {
  if (state.running) return Promise.resolve();
  if (starting) {
    if (startingRun === runs) return starting;
    // stopped while starting: start again once that one has let go
    const want = runs;
    return starting.then(() => { if (runs === want) return start(); });
  }
  // Never from a hidden page.  Spotify following, a track chosen in a
  // file picker, 'lights only' -- anything that started the player
  // without a tap used to undo the stop that hiding does, and then
  // stream from the background on throttled timers, about one frame a
  // second, re-arming the dead man every time.
  if (hiddenStops()) return Promise.resolve();
  const run = startingRun = ++runs;
  const held = holdScreen();
  $('go').textContent = 'stop';
  $('go').classList.add('stop');
  const gone = () => run !== runs || hiddenStops();
  // Put the page back as it was -- unless stop() already has, and a
  // newer start may own the button and the screen by now.
  const quit = () => {
    if (run !== runs) return;
    releaseScreen();
    $('go').textContent = 'start';
    $('go').classList.remove('stop');
  };
  starting = (async () => {
    let begun = false;
    try {
      if (!await connect() || gone()) { quit(); return; }
      if (stopNote) pageWarn(stopNote);
      begun = true;
      const frozen = await link.begin(state.bri);
      if (gone()) {
        // Stopped, or hidden, while the controller was being set up:
        // whatever stop() sent may have landed before begin's layout,
        // so let go again now that the layout is in.
        link.release();
        quit();
        return;
      }
      if (!frozen)
        pageWarn('the controller did not take the frozen segments the player '
                 + 'asked for, so frames may land in the wrong place or be painted over');
      state.running = true;
      stopNote = '';
      tickFails = 0;
      state.t0 = performance.now();
      state.lastCycle = 0;
      lastFrame = 0;
      lastReport = performance.now();
      tick();
      const how = await held;
      if (run === runs) screenSays(how);
    } catch (e) {
      // A controller that stopped answering half way through begin():
      // the layout may be in, so let go rather than leave it frozen.
      if (begun) link.release();
      quit();
      say('could not start: ' + ((e && e.message) || e), 'bad');
    } finally {
      starting = null;
    }
  })();
  return starting;
}

async function stop() {
  runs++;
  state.running = false;
  clearTimeout(timer);
  clockSeq++;
  releaseScreen();
  lostAt = 0;
  $('go').textContent = 'start';
  $('go').classList.remove('stop');
  $('scr').textContent = '-';
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
// listening
// ----------------------------------------------------------------------
// The analyser runs on its own clock and this only reads it, so the
// numbers on screen stay right even when the link has dragged the
// render rate down to single figures.
const an = new M.Analyser();
const NOTES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'];

// Presets whose look is driven by the music.  Everything else runs the
// same with or without it, so turning sound on and seeing nothing
// change would be the obvious thing to misread as broken.
const REACTIVE = ['spectrum', 'pitchwheel', 'bloom', 'eq', 'vu',
                  'beatpulse', 'heartbeat', 'sparkle'];

function audioSource(kind) {
  state.music = kind === 'none' ? null : M.LiveMusic(an);
  for (const [id, k] of [['afile', 'file'], ['amic', 'mic'],
                         ['atab', 'tab'], ['aoff', 'none']]) {
    $(id).classList.toggle('on', kind === k);
  }
  $('asrc').textContent = { file: 'track', mic: 'microphone',
                            tab: 'shared audio', none: 'silent' }[kind];
  if (kind !== 'none' && REACTIVE.indexOf(state.preset) < 0) choose('spectrum');
}

function audioWhy(msg) { $('why').textContent = msg || ''; }

const spec = $('spec'), sx = spec.getContext('2d');

function drawSpectrum() {
  const w = spec.clientWidth, h = 46;
  if (spec.width !== w * devicePixelRatio) {
    spec.width = w * devicePixelRatio; spec.height = h * devicePixelRatio;
  }
  sx.clearRect(0, 0, spec.width, spec.height);
  if (!an.running) return;
  const nb = 24, v = an.bands(nb);
  const bw = spec.width / nb;
  for (let b = 0; b < nb; b++) {
    const k = Math.max(0.01, v[b]);
    const c = M.hsv((an.pitch + b / nb * 0.3) % 1, 1, 1);
    sx.fillStyle = 'rgb(' + c.map(Math.round).join(',') + ')';
    sx.fillRect(b * bw + 1, spec.height * (1 - k), bw - 2, spec.height * k);
  }
}

function audioReadout() {
  if (!an.running) {
    $('alvl').textContent = '—'; $('apitch').textContent = '—';
    $('abpm').textContent = '—';
  } else {
    $('alvl').textContent = (an.level * 100).toFixed(0) + '%';
    $('apitch').textContent = NOTES[Math.round(an.pitch * 12) % 12];
    $('abpm').textContent = an.bpm ? an.bpm.toFixed(0) : '—';
  }
  drawSpectrum();
}
setInterval(audioReadout, 150);

$('afile').onclick = () => $('apick').click();
$('apick').onchange = async (e) => {
  const f = e.target.files && e.target.files[0];
  const forShow = e.target.dataset.forShow || '';
  e.target.value = '';
  e.target.dataset.forShow = '';
  if (!f) return;
  await playTrack(f, forShow);
};

// There is no way for a web page to tap another app's audio on a
// phone -- no browser offers one, on Android or on iOS.  What works
// is the microphone hearing the speaker, and the microphone needs a
// secure page.  This page is plain http because the controller
// cannot serve anything else, so both are off until one of these is
// done.  Say exactly which, because "permission denied" sends people
// to the wrong settings screen.
const INSECURE_FIX =
  'A browser only gives a page a microphone on a secure origin, and '
  + 'this page is plain http from the controller, so the API is absent '
  + 'rather than refused. Two ways round it: on Android Chrome, put '
  + location.origin + ' into chrome://flags/#unsafely-treat-insecure-'
  + 'origin-as-secure once and restart Chrome — then Spotify out of the '
  + 'speaker drives the helmet. Or, with the laptop there, open the '
  + 'page it serves over https instead. Picking a track with the left '
  + 'button needs none of this.';

$('amic').onclick = async () => {
  try {
    await an.useMic();
    audioSource('mic');
    audioWhy('listening. Anything the phone can hear drives the helmet — '
             + 'including its own speaker, which is how you follow Spotify.');
  } catch (err) {
    audioSource('none');
    audioWhy(err.message + '. ' + INSECURE_FIX);
  }
};

$('atab').onclick = async () => {
  try {
    await an.useTab();
    audioSource('tab');
    audioWhy('following the audio you shared.');
  } catch (err) {
    audioSource('none');
    audioWhy(err.message + '. ' + INSECURE_FIX);
  }
};

$('aoff').onclick = () => { an.stop(); audioSource('none'); audioWhy(''); };

if (!M.Analyser.micPossible()) {
  $('amic').disabled = true;
  $('amic').textContent = 'listen (needs https)';
}
if (!M.Analyser.tabPossible()) {
  $('atab').disabled = true;
  $('atab').textContent = "what's playing (needs https)";
}
if (!M.Analyser.micPossible() && !M.Analyser.tabPossible()) audioWhy(INSECURE_FIX);
audioSource('none');


// ----------------------------------------------------------------------
// shows
// ----------------------------------------------------------------------
// Only the cue lists came over -- see show.js.  Nothing here knows
// where in the track you are, so the clock starts when you say so and
// the drive comes from whatever the phone can hear.
function mmss(v) {
  v = Math.max(0, Math.round(v));
  return Math.floor(v / 60) + ':' + String(v % 60).padStart(2, '0');
}

function showClock(st, cue) {
  if (!state.show) return;
  $('showat').textContent = mmss(st) + ' / ' + mmss(state.show.duration)
    + (cue ? ' · ' + cue.preset
        + (cue.overlay ? ' + ' + cue.overlay.preset : '') : ' · (gap)');
}

// The song for each show, kept on this phone after the first time it
// is chosen, so that "start" means the song plays.
const tracks = new M.TrackCache();

function stopShow() {
  state.showT0 = null;
  state.showHold = null;
  $('showgo').textContent = 'start';
  $('showgo').classList.remove('on');
}

function showRunning() {
  $('showgo').textContent = 'stop';
  $('showgo').classList.add('on');
}

// Which shows can start with no further questions.  Marked in the
// list, and counted, because "fully offline" is exactly this number
// reaching five -- and the copies are per address, so the helmet's own
// network (4.3.2.1) and the home network keep separate sets.
let songsMissing = 0;

async function refreshSongs() {
  const have = new Set(await tracks.keys());
  const names = Object.keys(D.shows || {});
  for (const o of $('showpick').options) {
    if (!o.value) continue;
    o.textContent = (have.has(o.value) ? '✓ ' : '') + o.value.replace(/^deadmau5 - /, '');
  }
  const missing = names.filter(n => !have.has(n));
  songsMissing = missing.length;
  if (songFetching) return;          // the progress line is more useful
  $('songsat').textContent = (names.length - missing.length) + ' of ' + names.length
    + ' songs on this phone for ' + location.host
    + (missing.length ? ' · missing: ' + missing.map(n => n.replace(/^deadmau5 - /, '')).join(', ')
                      : ' · every show will start with its song, no network needed');
  offlineSays(missing);
}

// ----------------------------------------------------------------------
// getting ready for the helmet's own Wi-Fi
// ----------------------------------------------------------------------
// A browser keeps what a page saves per address, so the songs this page
// keeps at the house address (192.168.x.x) are invisible to the same page
// at the helmet's own Wi-Fi address (4.3.2.1).  The page and the track
// analyses live on the helmet and are there either way; the songs are
// what has to be carried across.  So at the house the page offers to save
// them to the phone as files, and on the helmet's Wi-Fi it asks for them
// once from the phone's files, with no laptop and no internet.
const AP_HOST = '4.3.2.1';
const apiHost = (() => { try { return new URL(Q.get('api') || location.href).hostname; }
                         catch (e) { return location.hostname; } })();
const onAP = apiHost === AP_HOST;
const SAVED_KEY = 'mau5saved';
let offDismissed = false;

function savedNames() {
  try { return (JSON.parse(localStorage.getItem(SAVED_KEY) || '{}').names) || []; }
  catch (e) { return []; }
}

async function offlineSays(missing) {
  const box = $('offbox');
  if (!box || offDismissed) { if (box) box.style.display = 'none'; return; }
  const names = Object.keys(D.shows || {});
  if (!names.length) { box.style.display = 'none'; return; }
  if (onAP) {
    if (!missing.length) { box.style.display = 'none'; return; }
    $('offat').innerHTML = '<b>' + missing.length + ' of ' + names.length + ' songs are not on ' +
      'this page yet.</b> On the helmet\'s own Wi-Fi they come from your phone: tap ' +
      'below and pick the MP3s you saved at home (Files &rsaquo; Downloads), once.';
    $('offsave').textContent = 'load the songs from this phone';
    $('offsave').disabled = false;
    box.style.display = 'block';
    return;
  }
  const saved = new Set(savedNames());
  const unsaved = names.filter(n => !saved.has(n));
  if (!unsaved.length) { box.style.display = 'none'; return; }
  if (missing.length) {
    $('offat').innerHTML = '<b>Getting ready for offline:</b> ' + missing.length +
      ' song' + (missing.length > 1 ? 's' : '') + ' still to come from the laptop ' +
      '(it needs <code>python3 mau5offline.py songs</code> running). Then save them to ' +
      'this phone so shows work on the helmet\'s own Wi-Fi.';
    $('offsave').textContent = 'waiting for the laptop';
    $('offsave').disabled = true;
    box.style.display = 'block';
    return;
  }
  let bytes = 0;
  for (const n of unsaved) { const f = await tracks.get(n); if (f) bytes += f.size || 0; }
  $('offat').innerHTML = '<b>Going out with the helmet?</b> Save the ' + unsaved.length +
    ' show song' + (unsaved.length > 1 ? 's' : '') + ' (' + Math.round(bytes / 1e6) +
    ' MB) to this phone. On the helmet\'s own Wi-Fi, where there is no laptop and no ' +
    'internet, this page will ask for them once and every show will play with its song.';
  $('offsave').textContent = 'save the songs to this phone';
  $('offsave').disabled = false;
  box.style.display = 'block';
}

async function saveSongsToPhone() {
  // Only what is not on the phone yet, or a new song downloads the rest again.
  const saved = savedNames();
  const names = Object.keys(D.shows || {}).filter(n => saved.indexOf(n) < 0);
  const done = [];
  for (const n of names) {
    const f = await tracks.get(n);
    if (!f) continue;
    const url = URL.createObjectURL(f);
    const a = document.createElement('a');
    a.href = url;
    a.download = f.name || (n + '.mp3');
    document.body.appendChild(a);
    a.click();
    a.remove();
    setTimeout(() => URL.revokeObjectURL(url), 60000);
    done.push(n);
    // one at a time: a burst of downloads is what browsers block
    await new Promise(r => setTimeout(r, 900));
  }
  try {
    localStorage.setItem(SAVED_KEY, JSON.stringify({ names: saved.concat(done), at: new Date().toISOString() }));
  } catch (e) {}
  $('offat').innerHTML = '<b>Saved ' + done.length + ' songs to this phone.</b> On the ' +
    'helmet\'s Wi-Fi (' + AP_HOST + '), tap "load the songs from this phone" when asked ' +
    'and pick them from Files &rsaquo; Downloads.';
  // Left up until it is dismissed: this is the instruction for later.
  $('offsave').disabled = true;
  $('offlater').textContent = 'got it';
}

$('offsave').onclick = () => {
  if (onAP) $('songpick').click();      // the existing multi-song picker
  else saveSongsToPhone();
};
$('offlater').onclick = () => { offDismissed = true; $('offbox').style.display = 'none'; };

async function showReadyText(name) {
  const f = name ? await tracks.get(name) : null;
  if ($('showpick').value !== name) return;          // changed meanwhile
  $('showat').textContent = f
    ? 'ready · ' + f.name + ' is on this phone — tap start'
    : 'tap start and choose the song once; this phone keeps it';
}

async function pickShow(name) {
  if (state.show && an.el) an.stop();       // a different show, a different song
  state.show = name ? new M.ShowPlayer(D.shows[name], helmet, D) : null;
  state.drive = null;
  stopShow();
  if (!name) {
    $('showat').textContent = 'pick a show and tap start — its song plays and the lights follow';
    save();
    return;
  }
  // The track's own analysis if it was uploaded: a real beat grid
  // beats an estimate, and it needs no microphone, which is the one
  // thing this page cannot have.  Worth waiting a moment for and no more:
  // on a poor link it can take a long while to come, and a song cannot sit
  // there for it.  It takes over whenever it does arrive, and until then
  // the show runs off what the page hears.
  if ((D.drive || {})[name]) {
    $('showat').textContent = 'loading the track analysis…';
    const got = driveFor(name).then((d) => {
      if (d && $('showpick').value === name) state.drive = d;
    });
    await Promise.race([got, new Promise(r => setTimeout(r, DRIVE_WAIT_MS))]);
  }
  await showReadyText(name);
  save();
}

const DRIVE_WAIT_MS = 1500;
const drives = new Map();

function driveFor(name) {
  if (!drives.has(name)) {
    drives.set(name, M.loadDrive('', D.drive[name]).catch(() => {
      drives.delete(name);     // a later song, a better link: try again then
      return null;
    }));
  }
  return drives.get(name);
}

// Start means the song plays.  From this phone's copy if it has one;
// otherwise ask for the file, once, and keep it.
async function startShow() {
  const name = $('showpick').value;
  if (!name) return;
  const f = await tracks.get(name);
  if (f) { await playTrack(f, name, true); return; }
  $('apick').dataset.forShow = name;
  $('apick').click();
  $('showat').textContent = 'choose the song for this show — it stays on this phone';
}

{
  const sel = $('showpick');
  for (const name of Object.keys(D.shows || {})) {
    const o = document.createElement('option');
    o.value = name;
    o.textContent = name.replace(/^deadmau5 - /, '');
    sel.appendChild(o);
  }
  sel.onchange = (e) => {
    // Picked during the set: the set carries on from there.
    if (list.on && e.target.value) { an.unlock(); listJump(e.target.value); return; }
    if (list.on) listEnd();
    pickShow(e.target.value);
  };
  $('showgo').onclick = () => {
    if (!state.show) return;
    an.unlock();
    if (list.on) { listEnd(); return; }
    if (state.showT0 === null && !an.el) {
      startShow();
    } else {
      // stop is stop: the song as well as the lights -- and following
      // Spotify, which would start the show again within a second
      if (an.el) { an.stop(); audioSource('none'); }
      unfollow();
      stopShow();
      showPP();
      showReadyText($('showpick').value);
    }
  };
  // The one way to run a show silently, and it says so: for checking
  // the lights in a quiet room, not for a show.
  $('showsilent').onclick = () => {
    if (!state.show) return;
    if (an.el) { an.stop(); audioSource('none'); }
    state.showT0 = performance.now();
    state.showHold = null;
    showRunning();
    $('showat').textContent = 'lights only — no song; start plays it with sound';
    if (!state.running) start();
  };
}



// -- the track itself ---------------------------------------------------
// A show with no sound is half a show, and the page is the only thing
// at a gig that knows when the track started.  So it plays it: the
// audio element is the clock, the volume control and the scrub bar,
// and the carried analysis supplies the drive.
// `forShow` is the show this file was chosen for, when it was chosen
// from the show box; otherwise the file's own name picks the show, so
// choosing the mp3 is the whole interaction either way.
async function playTrack(file, forShow, kept) {
  try {
    const name = forShow || M.showForFile(file.name, D.shows);
    if (name && $('showpick').value !== name) {
      $('showpick').value = name;
      await pickShow(name);
    }
    const el = await an.useFile(file);
    audioSource('file');
    an.setVolume(+$('vol').value / 100);
    userPaused = false;
    el.onended = () => {
      if (list.on) { listSkip(1); return; }
      an.stop(); audioSource('none'); stopShow(); showPP();
      showReadyText($('showpick').value);
    };
    // A file that cannot be read any further ended the sound with nothing
    // said and left the show frozen on its last moment.
    el.onerror = () => {
      const why = 'could not go on playing ' + file.name + ' (' +
        ((el.error && el.error.message) || 'the file failed') + ')';
      pageWarn(why);
      if (list.on) { listFailed(name); return; }
      an.stop(); audioSource('none'); stopShow(); showPP();
      $('showat').textContent = why;
    };
    // A media key, headphones, a call: the song stops, the lights hold one
    // moment at a normal frame rate, and nothing used to say why.
    el.onpause = () => {
      if (an.el !== el || userPaused || el.ended) return;
      pageWarn('the song was paused from outside this page (a media key, headphones, '
               + 'a call or another app) -- tap pause/play to carry on');
      showPP();
    };
    if (state.show) {
      state.showT0 = performance.now();
      showRunning();
      if (name) {
        // From this phone's copy already: writing an 18 MB song back into the
        // store at the start of every play did nothing but cost memory.
        const put = kept || await tracks.put(name, file);
        $('showat').textContent = 'playing ' + file.name
          + (put ? (kept ? '' : ' — kept on this phone for next time') : '');
        if (!kept) refreshSongs();
      }
    }
    if (!state.running) start();
    showPP();
    audioWhy('playing ' + file.name + ' out of this phone. The show follows '
             + 'the track, so pause and seek work.');
    return true;
  } catch (err) {
    // A second tap replaced this start: the newer one owns the song now.
    if (err && err.name === 'AbortError') return false;
    audioWhy('could not play that file: ' + (err.message || err));
    if (list.on) pageWarn('could not play ' + file.name + ' (' + (err.message || err) + ')');
    // or the loop would go on reading the clock of a song that never started
    an.stop();
    audioSource('none');
    return false;
  }
}

// ----------------------------------------------------------------------
// play music: every song, one after another
// ----------------------------------------------------------------------
// One tap, and the songs on this device run in the set's order, each with
// its own show, round and round until somebody stops them.  It goes by what
// is here now, not what was here when it started, so a song still on its way
// from the laptop joins the set when it lands.
const LIST_KEY = 'mau5list';
const list = { on: false, order: [], at: -1, run: 0, fails: 0, shuffle: false };
try { list.shuffle = !!JSON.parse(localStorage.getItem(LIST_KEY) || '{}').shuffle; } catch (e) {}
$('listshuffle').checked = list.shuffle;

function listNames() {
  const out = (D.playlist || []).filter(n => (D.shows || {})[n]);
  for (const n of Object.keys(D.shows || {})) if (out.indexOf(n) < 0) out.push(n);
  return out;
}

function shuffled(names, notFirst) {
  const a = names.slice();
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  if (a.length > 1 && a[0] === notFirst) [a[0], a[1]] = [a[1], a[0]];
  return a;
}

function listButtons() {
  $('playall').textContent = list.on ? '■ Stop the music' : '▶ Play Music';
  $('playall').classList.toggle('on', list.on);
  $('listprev').disabled = $('listnext').disabled = !list.on;
}

function short(n) { return String(n).replace(/^deadmau5 (& Wolfgang Gartner )?- /, ''); }

// `name` and the song after it, as far as anybody can say yet.
async function listSays(name) {
  const have = new Set(await tracks.keys());
  const ready = list.order.filter(n => have.has(n));
  const i = list.order.indexOf(name);
  let next = '';
  for (let k = 1; k <= list.order.length; k++) {
    const n = list.order[(i + k) % list.order.length];
    if (have.has(n)) { next = n; break; }
  }
  $('listat').textContent = (ready.indexOf(name) + 1) + ' of ' + ready.length + ' · ' + short(name)
    + (next && next !== name ? ' · next: ' + short(next) : '')
    + (ready.length < list.order.length
       ? ' · ' + (list.order.length - ready.length) + ' more not on this device yet' : '');
}

// The one way a song of the set gets started.  A newer call wins, and a
// double tap on skip plays the last one asked for rather than both.
async function listPlay(name) {
  const run = ++list.run;
  list.at = list.order.indexOf(name);
  listBusyUntil = performance.now() + 20000;
  $('listat').textContent = 'next: ' + short(name);
  const f = await tracks.get(name);
  if (run !== list.run || !list.on) return;
  if (!f) { listFailed(name); return; }
  $('showpick').value = name;
  await pickShow(name);
  if (run !== list.run || !list.on) return;
  const ok = await playTrack(f, name, true);
  if (run !== list.run || !list.on) return;
  listBusyUntil = 0;
  if (!ok) { listFailed(name); return; }
  list.fails = 0;
  listSays(name);
}

// The next or previous song this device has, wrapping round.
async function listSkip(dir) {
  const have = new Set(await tracks.keys());
  const n = list.order.length;
  if (dir > 0 && list.shuffle && list.at + dir >= n) {
    list.order = shuffled(listNames(), list.order[list.at]);
    list.at = -1;
  }
  for (let k = 1; k <= n; k++) {
    const name = list.order[(list.at + dir * k + n * k) % n];
    if (have.has(name)) { await listPlay(name); return; }
  }
  listEnd();
  $('listat').textContent = 'no songs on this device yet';
}

// A song that will not play is skipped, once round at most.
function listFailed(name) {
  list.at = list.order.indexOf(name);
  listBusyUntil = performance.now() + 20000;
  if (++list.fails >= list.order.length) {
    listEnd();
    $('listat').textContent = 'stopped: none of the songs would play';
    return;
  }
  setTimeout(() => { if (list.on) listSkip(1); }, 800);
}

function listJump(name) {
  if (!list.on) return;
  listPlay(name);
}

async function listStart() {
  an.unlock();
  list.order = list.shuffle ? shuffled(listNames()) : listNames();
  const have = new Set(await tracks.keys());
  const picked = $('showpick').value;
  const first = have.has(picked) ? picked : list.order.find(n => have.has(n));
  if (!first) {
    $('listat').textContent = onAP
      ? 'no songs on this page yet: use "load the songs from this phone" above'
      : 'no songs on this device yet: they come from the laptop, or use "load all the songs"';
    return;
  }
  list.on = true;
  list.fails = 0;
  listButtons();
  unfollow();
  // A song already playing from the show box stays where it is, and the set
  // carries on from it.
  if (an.el && an.kind === 'file' && first === picked && state.show) {
    list.at = list.order.indexOf(first);
    listSays(first);
    return;
  }
  await listPlay(first);
}

// Ends the set and the song, and hands the loop back to the picked preset.
function listEnd() {
  list.on = false;
  list.run++;
  listButtons();
  $('listat').textContent = '';
  if (an.el) { an.stop(); audioSource('none'); }
  stopShow();
  showPP();
  showReadyText($('showpick').value);
}

$('playall').onclick = () => {
  an.unlock();
  if (list.on) { listEnd(); stopNote = ''; stop(); }
  else listStart();
};
$('listnext').onclick = () => { an.unlock(); if (list.on) listSkip(1); };
$('listprev').onclick = () => {
  an.unlock();
  if (!list.on) return;
  // As on any player: back goes to the start of this song, unless it has only just begun.
  if (an.el && an.el.currentTime > 4) { an.el.currentTime = 0; return; }
  listSkip(-1);
};
$('listshuffle').onchange = (e) => {
  list.shuffle = e.target.checked;
  try { localStorage.setItem(LIST_KEY, JSON.stringify({ shuffle: list.shuffle })); } catch (err) {}
  if (!list.on) return;
  const now = list.order[list.at];
  list.order = list.shuffle ? shuffled(listNames(), now) : listNames();
  list.at = list.order.indexOf(now);
  if (list.shuffle && now !== undefined) {
    // the song playing stays where it is, at the front of the new order
    list.order.splice(list.at, 1);
    list.order.unshift(now);
    list.at = 0;
  }
  if (now) listSays(now);
};
listButtons();

// Anything else that took the song away -- 'silence', 'listen', a track picked
// by hand -- ends the set, rather than leave it dark and waiting for an end
// that will never come.
setInterval(() => {
  if (list.on && !an.el && list.at >= 0 && !listBusy()) listEnd();
}, 1500);
function listBusy() { return listBusyUntil > performance.now(); }
let listBusyUntil = 0;

function showPP() {
  const on = !!an.el;
  $('showpp').disabled = !on;
  $('showpp').textContent = (on && an.el.paused) ? 'play' : 'pause';
}

// ----------------------------------------------------------------------
// songs from a laptop on the same network
// ----------------------------------------------------------------------
// The controller has room for the cue lists, not the songs, and the
// songs cannot be put anywhere public.  `mau5offline.py songs` serves
// them from a laptop and leaves /songs.json on the controller saying
// where; whatever this phone is missing is fetched once into its own
// storage.  After that the shows play with no laptop and no network,
// and nobody had to have the files to begin with.
let songFetching = false;

const SONG_ANSWER_MS = 8000;

async function fetchSongs() {
  if (songFetching) return;
  let ptr = null;
  try {
    const r = await fetch('/songs.json', { cache: 'no-store' });
    if (r.ok) ptr = await r.json();
  } catch (e) {}
  if (!ptr || !ptr.from || !ptr.songs) return;
  // A laptop at the house address cannot answer on the helmet's own Wi-Fi,
  // and asking leaves the song line saying 'getting' until the phone gives
  // up.  Only a laptop on this Wi-Fi can (mau5offline.py songs, run there).
  if (onAP && ptr.from.indexOf('//4.3.2.') < 0) return;
  // Not just the songs that are missing: a copy of the wrong size is one that
  // never all arrived, and it plays perfectly well until it stops halfway.
  const want = [];
  for (const n of Object.keys(ptr.songs)) {
    if (!D.shows[n]) continue;
    const f = await tracks.get(n);
    if (!f || (ptr.songs[n].bytes && f.size !== ptr.songs[n].bytes)) want.push(n);
  }
  if (!want.length) return;
  songFetching = true;
  const total = want.reduce((s, n) => s + (ptr.songs[n].bytes || 0), 0);
  let got = 0;
  const say = (m) => { $('songsat').textContent = m; };
  try {
    for (const name of want) {
      const s = ptr.songs[name];
      // The pointer outlives the laptop, and an address nobody is at can
      // take a phone over a minute to give up on.  This covers the answer
      // only: a song is allowed as long as it takes to arrive.
      const ctl = new AbortController();
      const late = setTimeout(() => ctl.abort(), SONG_ANSWER_MS);
      let r;
      try {
        r = await fetch(ptr.from + s.path, { signal: ctl.signal });
      } catch (e) {
        throw ctl.signal.aborted ? new Error('nothing there answered') : e;
      } finally {
        clearTimeout(late);
      }
      if (!r.ok) throw new Error('the laptop answered ' + r.status);
      const parts = [];
      let here = 0;
      const rd = r.body && r.body.getReader ? r.body.getReader() : null;
      if (rd) {
        for (;;) {
          const step = await rd.read();
          if (step.done) break;
          parts.push(step.value);
          here += step.value.length;
          got += step.value.length;
          say('getting the songs from the laptop · ' + Math.round(got / 1e6)
              + ' of ' + Math.round(total / 1e6) + ' MB');
        }
      } else {
        const b = await r.blob();
        parts.push(b);
        here = b.size;
        got += b.size;
      }
      if (s.bytes && here !== s.bytes) throw new Error('only part of ' + name + ' arrived');
      const f = new File(parts, s.track || name + '.mp3', { type: 'audio/mpeg' });
      if (!(await tracks.put(name, f))) throw new Error('this browser would not keep it');
    }
  } catch (e) {
    songFetching = false;
    say('could not get the songs from ' + ptr.from + ' (' + (e.message || e)
        + ') -- this phone has to be on the same Wi-Fi as the laptop');
    return;
  }
  songFetching = false;
  await refreshSongs();
  if ($('showpick').value) showReadyText($('showpick').value);
}
// The laptop may start serving after the page is open, so look again
// now and then -- only while something is missing, and it is one
// small file on the controller.
setInterval(() => { if (songsMissing > 0) fetchSongs(); }, 20000);

// All five at once: pick the mp3s together and each goes to the show
// its name matches, by the same word rule Spotify following uses.
$('songload').onclick = () => $('songpick').click();
$('songpick').onchange = async (e) => {
  const files = Array.from(e.target.files || []);
  e.target.value = '';
  if (!files.length) return;
  const kept = [], unmatched = [];
  for (const f of files) {
    const name = M.showForFile(f.name, D.shows);
    if (name && await tracks.put(name, f)) kept.push(name.replace(/^deadmau5 - /, ''));
    else unmatched.push(f.name);
  }
  await refreshSongs();
  $('showat').textContent = (kept.length ? 'kept ' + kept.join(', ') : 'nothing kept')
    + (unmatched.length ? ' · no show matches ' + unmatched.join(', ')
       + ' -- pick the show and use "choose the song" for it' : '');
  if ($('showpick').value) showReadyText($('showpick').value);
};

$('showtrack').onclick = () => {
  $('apick').dataset.forShow = $('showpick').value || '';
  $('apick').click();
};
// Whether a pause was somebody's tap.  Any other is the browser's, and undone.
let userPaused = false;
$('showpp').onclick = () => {
  if (!an.el) return;
  if (an.el.paused) { userPaused = false; an.el.play(); }
  else { userPaused = true; an.el.pause(); }
  showPP();
};
$('vol').oninput = (e) => {
  an.setVolume(+e.target.value / 100);
  $('volval').textContent = e.target.value;
};
setInterval(showPP, 700);

// ----------------------------------------------------------------------
// following Spotify
// ----------------------------------------------------------------------
// One number is wanted here and only one: progress_ms.  With it the
// show stops being something you start on a downbeat and becomes
// something that follows the track through a pause, a seek and a
// skip.  Everything else -- which effect, how loud, where the beats
// are -- is already on the controller.
const sp = new M.Spotify();
let spTimer = null, spSaidWhy = '';

function spSay(msg) { $('spat').textContent = msg; }

function spButton() {
  $('spbtn').textContent = state.follow ? 'following Spotify'
    : (sp.connected ? 'follow Spotify' : 'connect Spotify');
  $('spbtn').classList.toggle('on', state.follow);
}

// A link of the form .../mau5.htm#sp=<id>.<token>, which is what
// `mau5spotify.py handoff` prints.  The fragment is never sent to a
// server, so the token reaches this page's localStorage and nothing
// else -- not the controller, not the repository.  It is cleared
// from the address bar straight away.
(function takeHandoff() {
  const m = /[#&]sp=([^&]+)/.exec(location.hash || '');
  if (!m) return;
  try {
    sp.connect(decodeURIComponent(m[1]));
    history.replaceState(null, '', location.pathname);
    spSay('Spotify token stored on this phone.');
  } catch (e) {
    spSay(String(e.message || e));
  }
})();

// Turning following off, from its button or from anything that means
// stop.  It used to survive the stop button, so the page that had just
// handed the helmet back started it again within a second.
let spRun = 0;          // bumped on every toggle, so an old poll chain ends

function unfollow() {
  if (!state.follow) return;
  state.follow = false;
  spRun++;
  clearTimeout(spTimer);
  spTimer = null;
  spButton();
  spSay('stopped following Spotify');
}

// Spotify playing something with no show, or nothing: the show stops
// and the presets carry on, rather than the last show running on into
// a song it was not made for.
function spIdle() {
  if (state.showT0 !== null && !an.el) {
    stopShow();
    showReadyText($('showpick').value);
  }
}

// One poll, then the next a second after it is answered -- never on a
// fixed beat.  setInterval did not wait for the answer, so slow ones
// overlapped, and an older answer arriving last moved the clock back.
async function spTick() {
  if (!state.follow) return;
  const mine = spRun;
  try {
    await spPoll();
  } catch (e) {
    spSay('Spotify: ' + String((e && e.message) || e));
  } finally {
    if (state.follow && mine === spRun) {
      clearTimeout(spTimer);
      spTimer = setTimeout(spTick, Math.max(1000, sp.waitMs()));
    }
  }
}

async function spPoll() {
  try {
    await sp.poll();
  } catch (e) {
    let why = String(e.message || e);
    // A fetch that never reached anything is a network with no way out,
    // which is what the helmet's own WiFi always is.  "Failed to fetch"
    // (Chrome), "Load failed" (Safari) or "NetworkError" (Firefox) told
    // nobody that at a show.
    if (e instanceof TypeError || /failed to fetch|load failed|networkerror/i.test(why))
      why = 'no internet on this WiFi (the helmet\'s own never has any) -- ' +
            'turn mobile data on, or pick the show and play the song from the phone';
    if (why !== spSaidWhy) { spSaidWhy = why; spSay('Spotify: ' + why); }
    return;
  }
  if (!state.follow) return;      // turned off while the answer was coming
  spSaidWhy = '';
  const tr = sp.track;
  if (!tr) { spSay('Spotify: nothing playing'); spIdle(); return; }

  const hit = M.bestShow(tr.name, tr.artists, D.shows);
  if (!hit) {
    spSay('playing "' + tr.name + '" — no show for that one');
    spIdle();
    return;
  }
  if (!state.show || $('showpick').value !== hit.name) {
    $('showpick').value = hit.name;
    await pickShow(hit.name);
    if (!state.follow) return;
  }
  const pos = sp.position();
  if (pos === null) return;
  const want = performance.now() - pos * 1000;
  if (!sp.playing) {
    // Paused: hold the show where the track is.  Left on the frame
    // clock it played the second since the last poll and then snapped
    // back to the same place, a one-second loop for as long as the
    // pause lasted.
    state.showHold = pos;
    state.showT0 = want;
  } else if (state.showHold !== null || state.showT0 === null
             || Math.abs(state.showT0 - want) > 600) {
    // Snap when it is a long way out -- first lock, a seek, a skip,
    // the end of a pause -- and ease otherwise, because a poll a
    // second against a frame clock will always disagree by a few tens
    // of milliseconds and snapping on that makes the show stutter.
    // 600 ms, not 250: on school or phone WiFi the answer's own
    // latency wanders by more than 250 and every few polls jumped.
    state.showHold = null;
    state.showT0 = want;
  } else {
    state.showT0 += (want - state.showT0) * 0.15;
  }
  if (!state.running) start();
  showRunning();
  spSay((sp.playing ? '▶ ' : '❚❚ ') + tr.name + ' · '
        + hit.name.replace(/^deadmau5 - /, '') + ' · ' + mmss(pos));
}

$('spbtn').onclick = async () => {
  if (!sp.connected) {
    const blob = prompt('Paste the line `python3 mau5spotify.py handoff` '
                        + 'printed (client id, a dot, then the refresh token):');
    if (!blob) return;
    try { sp.connect(blob); } catch (e) { spSay(String(e.message || e)); return; }
  }
  if (state.follow) {
    unfollow();
    spSay('');
    return;
  }
  if (list.on) listEnd();
  state.follow = true;
  spRun++;
  spButton();
  spSay('asking Spotify…');
  clearTimeout(spTimer);
  spTimer = null;
  spTick();
};
spButton();

// ----------------------------------------------------------------------
// wiring up
// ----------------------------------------------------------------------
const grid = $('grid');
for (const name of Object.keys(D.presets)) {
  const b = document.createElement('button');
  b.textContent = name;
  b.dataset.name = name;
  if (REACTIVE.indexOf(name) >= 0) b.classList.add('reactive');
  b.onclick = () => {
    if (list.on) listEnd();
    if (state.show) { $('showpick').value = ''; pickShow(''); }
    choose(name);
  };
  grid.appendChild(b);
}

// While a start is on its way the button already says stop, and means
// it: the start is cancelled and lets go of whatever it had taken.
$('go').onclick = () => {
  if (state.running || (starting && startingRun === runs)) {
    // stop is stop: following Spotify would start it again within a second,
    // and a song left playing to a dark helmet looks like a crash
    unfollow();
    stopNote = '';
    if (list.on) listEnd();
    else if (an.el && an.kind === 'file') {
      an.stop(); audioSource('none'); stopShow(); showPP();
      showReadyText($('showpick').value);
    }
    stop();
  } else {
    start();
  }
};
$('hand').onchange = (e) => {
  state.handover = e.target.checked;
  link.standby = state.handover ? (D.standby || null) : null;
  save();
};
// One brightness POST at a time, the newest value sent when it is back.
// A drag fired one per input event: dozens of requests at a controller
// that restarts when pushed, landing in any order.
let briBusy = false, briWant = null;
function sendBri() {
  if (briBusy || briWant === null || !state.running) return;
  const v = briWant; briWant = null; briBusy = true;
  link.setBri(v).catch(() => {}).then(() => { briBusy = false; sendBri(); });
}
$('bri').oninput = (e) => {
  state.bri = +e.target.value;
  $('brival').textContent = state.bri;
  if (state.running) { briWant = state.bri; sendBri(); }
  save();
};
$('cycle').onchange = (e) => { state.cycle = +e.target.value; save(); };

// ----------------------------------------------------------------------
// standby glow
// ----------------------------------------------------------------------
// One of WLED's own effects, saved as the preset the page hands back to
// and the one the helmet boots into.  It can run for hours on a shelf, so
// it has to fit the *sustained* budget, not the burst one: power.json's
// sustained watts less the LEDs' own standby draw, about 296 mA of LED
// current.  The brightness is not guessed: WLED estimates the current of
// its own effects, so the page measures pacifica against a black frame
// and turns it down until it fits, with a tenth in hand.
async function setupStandby() {
  const say = (m) => { $('standbyat').textContent = m; };
  if (state.running || starting) { say('stop the player first'); return; }
  const btn = $('standbysetup');
  btn.disabled = true;
  const wait = (ms) => new Promise(r => setTimeout(r, ms));
  const th = (D.power && D.power.thermal) || {};
  const budget = 0.9 * Math.max(0, ((th.sustained_w || 0) - (th.standby_w || 0)) / 12 * 1000);
  async function readings(ms) {
    const out = [];
    const end = performance.now() + ms;
    while (performance.now() < end) {
      try {
        const v = ((await link.getJSON('/json/info')).leds || {}).pwr;
        if (typeof v === 'number') out.push(v);
      } catch (e) {}
      await wait(300);
    }
    return out;
  }
  // Tapping play mid-measure would put the stream's frames in the preset.
  const stillOurs = () => {
    if (state.running || starting) throw new Error('the player started, so nothing was saved');
  };
  try {
    if (!(budget > 0)) throw new Error('no sustained budget in power.json');
    let fx = 101;                                    // pacifica, as on 0.15
    try {
      const names = await link.getJSON('/json/eff');
      const i = names.findIndex(x => /^pacifica$/i.test(String(x).split('@')[0]));
      if (i >= 0) fx = i;
    } catch (e) {}
    let st = {};
    try { st = await link.getJSON('/json/state'); } catch (e) {}
    const extra = (st.seg || []).filter(g => g.id > 0).map(g => ({ id: g.id, stop: 0 }));
    say('measuring...');
    // black first, so WLED's own allowances (ESP, LED standby) drop out
    await link.postJSON({ on: true, bri: 128, transition: 0, live: false, nl: { on: false },
      seg: [{ id: 0, start: 0, stop: link.ledCount, frz: false, fx: 0,
              col: [[0, 0, 0], [0, 0, 0], [0, 0, 0]], on: true, bri: 255 }].concat(extra) });
    await wait(1200);
    // The least and, below, the most: a stale reading can only err dimmer.
    const blacks = await readings(1500);
    const base = blacks.length ? Math.min(...blacks) : null;
    const glow = (b) => link.postJSON({ on: true, bri: b, transition: 0,
      seg: [{ id: 0, fx: fx, sx: 110, ix: 128, pal: 0, frz: false, on: true, bri: 255 }] });
    let bri = 96, led = null, fits = false, measured = true;
    for (let round = 0; round < 6; round++) {
      stillOurs();
      await glow(bri);
      await wait(1500);
      const tops = await readings(4000);
      const top = tops.length ? Math.max(...tops) : null;
      // With WLED's limiter off the estimate never moves.  That is no
      // measurement, and reading it as 0 mA would save this brightness.
      if (top === null || base === null || top <= base) { measured = false; break; }
      led = top - base;
      say('pacifica at ' + bri + ': about ' + Math.round(led) + ' mA');
      if (led <= budget) { fits = true; break; }
      if (bri <= 8) break;
      bri = Math.max(8, Math.floor(bri * budget / led * 0.95));
    }
    if (!measured) {
      // No estimate from this firmware.  Dim enough to be safe by any
      // reasonable reckoning, and the message says it was not measured.
      bri = 24;
      await glow(bri);
    } else if (!fits) {
      // Never saved over budget: this can run for hours unattended.
      await link.postJSON({ on: false });
      throw new Error('it would not fit the ' + Math.round(budget / 0.9) +
                      ' mA the helmet can sustain, so nothing was saved');
    }
    stillOurs();
    await link.postJSON({ psave: D.standby || 1, n: 'mau5 standby', ib: true, sb: true });
    await wait(600);
    await link.postCfg({ def: { ps: D.standby || 1, on: true, bri: bri } });
    link.presets.add(String(D.standby || 1));
    say('saved: pacifica at brightness ' + bri +
        (!measured ? ' (this firmware gave no current estimate, so kept low)'
                      : ', about ' + Math.round(led) + ' mA, inside the ' +
                        Math.round(budget / 0.9) + ' mA it can sustain') +
        '. The helmet glows like this when the page lets go and when it powers on.');
    $('warn').style.display = 'none';
  } catch (e) {
    say('could not set it up: ' + (e.message || e));
  } finally {
    btn.disabled = false;
  }
}
$('standbysetup').onclick = setupStandby;

// Leaving must put the helmet out.  The segment is frozen, so without
// this the last frame stays lit until somebody pulls the plug.
// A start still on its way counts: its layout may land after this.
addEventListener('pagehide', () => { if (state.running || starting) link.release(); });
addEventListener('visibilitychange', () => {
  // Either way the loop has to move onto the other clock now, or wait for
  // whichever one it is on: the page's own could be a second from waking.
  if (state.running && !parked && clock) later(0);
  if (document.visibilityState === 'hidden') {
    if (hiddenStops() && (state.running || (starting && startingRun === runs))) {
      stopNote = 'the helmet went off while this page was out of sight (another '
        + 'app, a file picker, or the screen going off) and came back with it '
        + '-- keep it in front during a show, and if the screen locked by '
        + 'itself, set the phone\'s auto-lock to Never';
      stop();
    }
  } else {
    // A browser that paused the song to go behind something: not somebody's tap.
    if (an.ctx && an.ctx.state !== 'running') { try { an.ctx.resume(); } catch (e) {} }
    if (an.el && an.el.paused && !userPaused && !an.el.ended) {
      const p = an.el.play();
      if (p && p.catch) p.catch(() => {});
    }
    if (stopNote) {
      pageWarn(stopNote);
      comeBack();
    }
  }
});

// Nobody pressed stop, so being in front again starts it again, song or
// no song.  The phone may still be finding its Wi-Fi on the way back from
// whatever hid the page, so a start that cannot reach the helmet is tried
// again until one can, or somebody presses stop (which clears stopNote).
// Not while another device streams to the helmet, though: coming back would take it
// from them mid-song, so it waits until the helmet is free.
let comeBackTimer = null;
async function othersLive() {
  try { return !!(await link.getJSON('/json/info')).live; } catch (e) { return false; }
}
function comeBack() {
  clearTimeout(comeBackTimer);
  if (!stopNote || state.running || hiddenStops()) return;
  othersLive().then((busy) => {
    if (!stopNote || state.running || hiddenStops()) return;
    if (busy) { comeBackTimer = setTimeout(comeBack, 3000); return; }
    start().then(() => {
      if (stopNote && !state.running) comeBackTimer = setTimeout(comeBack, 3000);
    });
  });
}

// A button keeps the focus after a tap, and a space bar then presses it again,
// which on 'stop' stops the song.  Keyboard presses (detail 0) keep their focus.
addEventListener('click', (e) => {
  const b = e.target && e.target.closest ? e.target.closest('button') : null;
  if (b && e.detail > 0) b.blur();
});
addEventListener('resize', () => { dots = null; draw(); });

choose(restore() || 'rainbow', true);
refreshSongs().then(fetchSongs);
$('bri').value = state.bri;
$('brival').textContent = state.bri;
$('cycle').value = state.cycle;
$('hand').checked = state.handover;
link.standby = state.handover ? (D.standby || null) : null;
$('leds').textContent = helmet.n;
$('budget').textContent = D.power.budget_ma;
$('built').textContent = D.built;
layout(); draw();
connect();

})();
