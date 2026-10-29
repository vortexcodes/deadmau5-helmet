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
  music: null, show: null, showT0: null, drive: null, follow: false,
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

  if (state.show && (state.showT0 !== null || an.el)) {
    // The track, when there is one, IS the clock.  Reading the audio
    // element's own currentTime cannot drift from the sound the room
    // is hearing, which a wall clock started by hand always does --
    // and it makes pause, seek and volume somebody else's problem.
    const st = an.el ? an.el.currentTime : (now - state.showT0) / 1000;
    if (st >= state.show.duration && !an.el) {
      stopShow();
      frame.fill(0);
      state.inst.render(helmet, t, state.music, frame);
    } else {
      const cue = state.show.frame(st, state.drive || state.music, frame);
      showClock(st, cue);
    }
  } else {
    frame.fill(0);
    state.inst.render(helmet, t, state.music, frame);
  }
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
  e.target.value = '';
  if (!f) return;
  await playTrack(f);
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

function stopShow() {
  state.showT0 = null;
  $('showgo').textContent = 'start';
  $('showgo').classList.remove('on');
  if (state.show) {
    $('showat').textContent = 'ready — play the track, tap start on the first beat';
  }
}

async function pickShow(name) {
  state.show = name ? new M.ShowPlayer(D.shows[name], helmet, D) : null;
  state.drive = null;
  stopShow();
  if (!name) {
    $('showat').textContent = 'pick a show, play the track, tap start on the first beat';
    save();
    return;
  }
  // The track's own analysis if it was uploaded: a real beat grid
  // beats an estimate, and it needs no microphone, which is the one
  // thing this page cannot have.
  const file = (D.drive || {})[name];
  if (file) {
    $('showat').textContent = 'loading the track analysis…';
    try {
      state.drive = await M.loadDrive('', file);
      $('showat').textContent = 'ready · ' + Math.round(state.drive.duration)
        + 's, ' + state.drive.beats.length + ' beats, '
        + state.drive.bpm.toFixed(0) + ' bpm — tap start on the first beat';
    } catch (e) {
      $('showat').textContent = 'no analysis on the controller for this one; '
        + 'it will run off whatever the page can hear';
    }
  } else {
    $('showat').textContent = 'ready — play the track, tap start on the first beat';
  }
  save();
}

{
  const sel = $('showpick');
  for (const name of Object.keys(D.shows || {})) {
    const o = document.createElement('option');
    o.value = name;
    o.textContent = name.replace(/^deadmau5 - /, '');
    sel.appendChild(o);
  }
  sel.onchange = (e) => pickShow(e.target.value);
  $('showgo').onclick = () => {
    if (!state.show) return;
    if (state.showT0 === null) {
      state.showT0 = performance.now();
      $('showgo').textContent = 'stop';
      $('showgo').classList.add('on');
      if (!state.running) start();
    } else {
      stopShow();
    }
  };
}



// -- the track itself ---------------------------------------------------
// A show with no sound is half a show, and the page is the only thing
// at a gig that knows when the track started.  So it plays it: the
// audio element is the clock, the volume control and the scrub bar,
// and the carried analysis supplies the drive.
async function playTrack(file) {
  try {
    const el = await an.useFile(file);
    audioSource('file');
    an.setVolume(+$('vol').value / 100);
    el.onended = () => { an.stop(); audioSource('none'); stopShow(); showPP(); };
    // name the show after the file if one matches, so picking the mp3
    // is the whole interaction
    const hit = M.bestShow(file.name, [], D.shows);
    if (hit && $('showpick').value !== hit.name) {
      $('showpick').value = hit.name;
      await pickShow(hit.name);
    }
    if (state.show) {
      state.showT0 = performance.now();
      $('showgo').textContent = 'stop';
      $('showgo').classList.add('on');
    }
    if (!state.running) start();
    showPP();
    audioWhy('playing ' + file.name + ' out of this phone. The show follows '
             + 'the track, so pause and seek work.');
  } catch (err) {
    audioWhy('could not play that file: ' + (err.message || err));
  }
}

function showPP() {
  const on = !!an.el;
  $('showpp').disabled = !on;
  $('showpp').textContent = (on && an.el.paused) ? 'play' : 'pause';
}

$('showtrack').onclick = () => { $('apick').dataset.forShow = '1'; $('apick').click(); };
$('showpp').onclick = () => {
  if (!an.el) return;
  if (an.el.paused) an.el.play(); else an.el.pause();
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

async function spTick() {
  if (!state.follow) return;
  try {
    await sp.poll();
  } catch (e) {
    const why = String(e.message || e);
    if (why !== spSaidWhy) { spSaidWhy = why; spSay('Spotify: ' + why); }
    return;
  }
  spSaidWhy = '';
  const tr = sp.track;
  if (!tr) { spSay('Spotify: nothing playing'); return; }

  const hit = M.bestShow(tr.name, tr.artists, D.shows);
  if (!hit) {
    spSay('playing "' + tr.name + '" — no show for that one');
    return;
  }
  if (!state.show || $('showpick').value !== hit.name) {
    $('showpick').value = hit.name;
    await pickShow(hit.name);
  }
  const pos = sp.position();
  if (pos === null) return;
  // Snap when it is a long way out -- first lock, a seek, a skip --
  // and ease otherwise, because a poll a second against a frame
  // clock will always disagree by a few tens of milliseconds and
  // snapping on that makes the show stutter once a second.
  const want = performance.now() - pos * 1000;
  if (state.showT0 === null || Math.abs(state.showT0 - want) > 250) {
    state.showT0 = want;
  } else {
    state.showT0 += (want - state.showT0) * 0.15;
  }
  if (!state.running) start();
  $('showgo').textContent = 'stop';
  $('showgo').classList.add('on');
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
  state.follow = !state.follow;
  spButton();
  if (state.follow) {
    spSay('asking Spotify…');
    if (spTimer) clearInterval(spTimer);
    spTimer = setInterval(spTick, 1000);
    spTick();
  } else {
    if (spTimer) clearInterval(spTimer);
    spTimer = null;
    spSay('');
  }
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
  b.onclick = () => { if (state.show) { $('showpick').value = ''; pickShow(''); } choose(name); };
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
