// Play Music in real Chrome against the fake 16: real audio element, real gesture, real hiding.
const BASE = 'http://127.0.0.1:8770', DBG = 'http://127.0.0.1:9341';
const sleep = (ms) => new Promise(r => setTimeout(r, ms));
async function attach(t) {
  const ws = new WebSocket(t.webSocketDebuggerUrl);
  await new Promise(r => ws.addEventListener('open', r));
  let id = 0; const pending = new Map(); const errors = [];
  ws.addEventListener('message', (ev) => { const m = JSON.parse(ev.data);
    if (m.method === 'Runtime.exceptionThrown') errors.push((m.params.exceptionDetails.exception ? m.params.exceptionDetails.exception.description : m.params.exceptionDetails.text).slice(0, 300));
    if (m.method === 'Runtime.consoleAPICalled' && (m.params.type === 'error' || m.params.type === 'warning')) errors.push(m.params.args.map(a => a.value || a.description).join(' ').slice(0, 300));
    if (pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); } });
  const call = (method, params = {}) => new Promise(r => { const k = ++id; pending.set(k, r); ws.send(JSON.stringify({ id: k, method, params })); });
  const ev = async (e) => { const m = await call('Runtime.evaluate', { expression: e, awaitPromise: true, returnByValue: true });
    if (m.result && m.result.exceptionDetails) throw new Error(JSON.stringify(m.result.exceptionDetails).slice(0, 400));
    return m.result && m.result.result ? m.result.result.value : m; };
  return { ws, call, ev, errors };
}
const tabs = await (await fetch(DBG + '/json')).json();
const P = await attach(tabs.find(t => t.type === 'page'));
await P.call('Runtime.enable'); await P.call('Page.enable');
await P.call('Page.addScriptToEvaluateOnNewDocument', { source: `(() => { window.__audio = []; const A = window.Audio; window.Audio = function (...a) { const e = new A(...a); window.__audio.push(e); return e; }; window.Audio.prototype = A.prototype; })();` });
await P.call('Page.navigate', { url: BASE + '/mau5.htm' });
await P.call('Page.bringToFront');
await sleep(3000);
console.log('conn:', await P.ev(`document.getElementById('conn').textContent`));
const songs = [['Fred again.. & Baby Keem - leavemealone', 0], ['TIKI TIKI - Slowed', 1], ['beneath (with raxaj)', 2]];
for (const [n, k] of songs) {
  console.log('storing', n, await P.ev(`(async () => { const b = await (await fetch('http://127.0.0.1:8799/songs/${k}.mp3')).blob(); const c = new MAU5.TrackCache(); return await c.put(${JSON.stringify(n)}, new File([b], ${JSON.stringify(n)} + '.mp3', { type: 'audio/mpeg' })) ; })()`));
}
const click = async (id) => {
  const r = await P.ev(`(() => { const e = document.getElementById('${id}'); e.scrollIntoView({block:'center'}); const b = e.getBoundingClientRect(); return { x: b.x + b.width / 2, y: b.y + b.height / 2 }; })()`);
  await P.call('Input.dispatchMouseEvent', { type: 'mousePressed', x: r.x, y: r.y, button: 'left', clickCount: 1 });
  await P.call('Input.dispatchMouseEvent', { type: 'mouseReleased', x: r.x, y: r.y, button: 'left', clickCount: 1 });
};
const look = () => P.ev(`(() => { const a = window.__audio[window.__audio.length - 1]; return { list: document.getElementById('listat').textContent.slice(0, 90), btn: document.getElementById('playall').textContent, go: document.getElementById('go').textContent, n: window.__audio.length, t: a ? +a.currentTime.toFixed(1) : -1, dur: a ? +(a.duration || 0).toFixed(1) : -1, paused: a ? a.paused : null, sent: MAU5_LINK.sent, show: document.getElementById('showpick').value, vis: document.visibilityState, warn: document.getElementById('warn').textContent.slice(-120), fps: document.getElementById('fps').textContent, drive: 0 }; })()`);
await click('playall');
await sleep(2500);
console.log('after tap', JSON.stringify(await look()));
await sleep(3000);
const a = await look(); console.log('3 s on   ', JSON.stringify(a));
for (let k = 0; k < 4; k++) {
  await P.ev(`(() => { const a = window.__audio[window.__audio.length - 1]; a.currentTime = a.duration - 2.5; })()`);
  const before = await look();
  for (let w = 0; w < 14; w++) { await sleep(500); const l = await look(); if (l.show !== before.show) break; }
  await sleep(1500);
  console.log('song ' + (k + 1) + ' ended ->', JSON.stringify(await look()));
}
// hide it behind another tab
const s0 = await look();
const nt = await (await fetch(DBG + '/json/new?about:blank', { method: 'PUT' })).json();
await fetch(DBG + '/json/activate/' + nt.id);
await sleep(1500);
const h1 = await look(); console.log('hidden   ', JSON.stringify(h1));
await sleep(10000);
const h2 = await look(); console.log('hidden+10', JSON.stringify(h2));
console.log('frames while hidden: %.1f a second; song moved %.1f s', (h2.sent - h1.sent) / 10, h2.t - h1.t);
const tb = tabs.find(t => t.type === 'page');
await fetch(DBG + '/json/activate/' + tb.id);
await sleep(1500);
const v1 = await look(); console.log('front    ', JSON.stringify(v1));
await sleep(4000);
const v2 = await look(); console.log('frames in front: %.1f a second', (v2.sent - v1.sent) / 4);
await fetch(DBG + '/json/close/' + nt.id);
await click('listnext');
await sleep(2000);
console.log('next btn ', JSON.stringify(await look()));
await click('playall');
await sleep(1500);
console.log('stopped  ', JSON.stringify(await look()));
console.log('page errors:', P.errors.length ? P.errors.slice(0, 8) : 'none');
P.ws.close();
