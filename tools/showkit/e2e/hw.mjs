// Play Music on the real helmet from a fresh browser, the way a new device gets it: the page from the
// controller, the songs from the laptop, a real tap. Leaves without a word if anybody else starts streaming.
const HOST = 'http://192.168.10.172', DBG = 'http://127.0.0.1:9343', ME = '192.168.10.225';
const SECS = +(process.argv[2] || 150);
const sleep = (ms) => new Promise(r => setTimeout(r, ms));
const info = async () => { try { const d = await (await fetch(HOST + '/json/info', { signal: AbortSignal.timeout(4000) })).json(); return { up: d.uptime, live: d.live, ws: d.ws, pwr: d.leds.pwr, heap: d.freeheap, lip: d.lip, rssi: d.wifi.rssi }; } catch (e) { return { err: String(e.message) }; } };
const state = async () => { try { const s = await (await fetch(HOST + '/json/state', { signal: AbortSignal.timeout(4000) })).json(); return s.on + '/' + s.bri + ' nl ' + s.nl.on; } catch (e) { return 'err'; } };
const first = await info();
console.log('helmet before', JSON.stringify(first));
if (first.live) { console.log('somebody is streaming, not touching it'); process.exit(0); }
const tabs = await (await fetch(DBG + '/json')).json();
const ws = new WebSocket(tabs.find(t => t.type === 'page').webSocketDebuggerUrl);
await new Promise(r => ws.addEventListener('open', r));
let id = 0; const pending = new Map(); const errors = [];
ws.addEventListener('message', (ev) => { const m = JSON.parse(ev.data);
  if (m.method === 'Runtime.exceptionThrown') errors.push((m.params.exceptionDetails.exception ? m.params.exceptionDetails.exception.description : m.params.exceptionDetails.text).slice(0, 300));
  if (m.method === 'Runtime.consoleAPICalled' && (m.params.type === 'error' || m.params.type === 'warning')) errors.push(m.params.args.map(a => a.value || a.description).join(' ').slice(0, 300));
  if (pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); } });
const call = (method, params = {}) => new Promise(r => { const k = ++id; pending.set(k, r); ws.send(JSON.stringify({ id: k, method, params })); });
const ev = async (e) => { const m = await call('Runtime.evaluate', { expression: e, awaitPromise: true, returnByValue: true }); if (m.result && m.result.exceptionDetails) throw new Error(JSON.stringify(m.result.exceptionDetails).slice(0, 400)); return m.result.result.value; };
await call('Runtime.enable'); await call('Page.enable');
await call('Page.addScriptToEvaluateOnNewDocument', { source: `(() => { window.__audio = []; const A = window.Audio; window.Audio = function (...a) { const e = new A(...a); window.__audio.push(e); return e; }; window.Audio.prototype = A.prototype; })();` });
const t00 = Date.now();
await call('Page.navigate', { url: HOST + '/mau5.htm' });
await call('Page.bringToFront'); await call('Emulation.setFocusEmulationEnabled', { enabled: true });
await sleep(4000);
const txt = (i) => ev(`document.getElementById('${i}').textContent`);
console.log('page up in %.1f s:', (Date.now() - t00) / 1000, await txt('conn'), '| built', await txt('built'));
const tf = Date.now();
for (;;) { await sleep(3000); const s = await txt('songsat'); if (/^16 of 16/.test(s) || Date.now() - tf > 150000) { console.log('songs after %d s:', (Date.now() - tf) / 1000, s.slice(0, 80)); break; } }
console.log('prompt:', (await txt('offat')).slice(0, 110), '| button:', await txt('offsave'));
const r = await ev(`(() => { const e = document.getElementById('playall'); e.scrollIntoView({block:'center'}); const b = e.getBoundingClientRect(); return { x: b.x + b.width / 2, y: b.y + b.height / 2 }; })()`);
await call('Input.dispatchMouseEvent', { type: 'mousePressed', x: r.x, y: r.y, button: 'left', clickCount: 1 });
await call('Input.dispatchMouseEvent', { type: 'mouseReleased', x: r.x, y: r.y, button: 'left', clickCount: 1 });
await sleep(3000);
const st = () => ev(`(() => { const a = window.__audio[window.__audio.length - 1]; return { list: document.getElementById('listat').textContent.slice(0, 60), t: a ? +a.currentTime.toFixed(1) : -1, dur: a ? +(a.duration || 0).toFixed(0) : 0, paused: a ? a.paused : null, sent: MAU5_LINK.sent, lost: MAU5_LINK.lost, rtt: +MAU5_LINK.rtt.toFixed(0), closes: MAU5_LINK.quietCloses, relay: MAU5_LINK.relayouts || 0, revived: MAU5_LINK.revived, conn: document.getElementById('conn').textContent.slice(-38), go: document.getElementById('go').textContent, ma: document.getElementById('ma').textContent, heat: document.getElementById('therm').textContent, now: document.getElementById('showat').textContent.slice(0, 44), els: window.__audio.length }; })()`);
let last = await st(), lastT = Date.now();
console.log('playing', JSON.stringify(last));
const t0 = Date.now(); let nextSkip = t0 + 25000, up0 = first.up, restarts = 0, minFps = 99, fpsSum = 0, fpsN = 0;
while (Date.now() - t0 < SECS * 1000) {
  await sleep(5000);
  const s = await st(); const now = Date.now(); const i = await info(); const on = await state();
  const fps = (s.sent - last.sent) * 1000 / (now - lastT);
  fpsSum += fps; fpsN++; minFps = Math.min(minFps, fps);
  if (i.up !== undefined && i.up < up0) { restarts++; console.log('  !! CONTROLLER RESTARTED'); }
  if (i.up !== undefined) up0 = i.up;
  console.log(' %s t=%s/%s %s fps lag %s lost %s mA %s heat %s | %s | up %s heap %s pwr %s live %s on %s rssi %s ws %s closes %s', s.list.slice(0, 26).padEnd(26), s.t, s.dur, fps.toFixed(1), s.rtt, s.lost, s.ma, s.heat, s.now.slice(0, 26), i.up, i.heap, i.pwr, i.live, on, i.rssi, i.ws, s.closes);
  last = s; lastT = now;
  if (i.lip && i.lip !== ME) { console.log('ANOTHER WRITER', i.lip, '-- leaving without a word'); process.exit(0); }
  if (now > nextSkip) { await ev(`(() => { const a = window.__audio[0]; a.currentTime = Math.max(0, a.duration - 3); })()`); console.log('  ... jumping to the last 3 s of this song'); nextSkip = now + 25000; }
}
console.log('mean %.1f fps, worst 5 s %.1f, restarts %d', fpsSum / fpsN, minFps, restarts);
console.log('warn:', (await txt('warn')).slice(0, 300));
const rr = await ev(`(() => { const e = document.getElementById('playall'); e.scrollIntoView({block:'center'}); const b = e.getBoundingClientRect(); return { x: b.x + b.width / 2, y: b.y + b.height / 2 }; })()`);
await call('Input.dispatchMouseEvent', { type: 'mousePressed', x: rr.x, y: rr.y, button: 'left', clickCount: 1 });
await call('Input.dispatchMouseEvent', { type: 'mouseReleased', x: rr.x, y: rr.y, button: 'left', clickCount: 1 });
await sleep(2500);
console.log('stopped', JSON.stringify(await st()));
console.log('helmet after', JSON.stringify(await info()), await state());
console.log('page errors:', errors.length ? errors.slice(0, 8) : 'none');
ws.close();
