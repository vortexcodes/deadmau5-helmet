// The page as a phone meets it on the helmet's own Wi-Fi: address 4.3.2.1 (mapped to the fake), no laptop,
// the songs picked from the phone's files under their real download names. Then Play Music, and eyes by finger.
import fs from 'fs';
const BASE = 'http://4.3.2.1:8770', DBG = 'http://127.0.0.1:9342';
const sleep = (ms) => new Promise(r => setTimeout(r, ms));
const tabs = await (await fetch(DBG + '/json')).json();
const ws = new WebSocket(tabs.find(t => t.type === 'page').webSocketDebuggerUrl);
await new Promise(r => ws.addEventListener('open', r));
let id = 0; const pending = new Map(); const errors = [];
ws.addEventListener('message', (ev) => { const m = JSON.parse(ev.data);
  if (m.method === 'Runtime.exceptionThrown') errors.push((m.params.exceptionDetails.exception ? m.params.exceptionDetails.exception.description : m.params.exceptionDetails.text).slice(0, 300));
  if (m.method === 'Runtime.consoleAPICalled' && (m.params.type === 'error')) errors.push(m.params.args.map(a => a.value || a.description).join(' ').slice(0, 300));
  if (pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); } });
const call = (method, params = {}) => new Promise(r => { const k = ++id; pending.set(k, r); ws.send(JSON.stringify({ id: k, method, params })); });
const ev = async (e) => { const m = await call('Runtime.evaluate', { expression: e, awaitPromise: true, returnByValue: true }); if (m.result && m.result.exceptionDetails) throw new Error(JSON.stringify(m.result.exceptionDetails).slice(0, 400)); return m.result.result.value; };
await call('Runtime.enable'); await call('Page.enable'); await call('DOM.enable');
await call('Page.addScriptToEvaluateOnNewDocument', { source: `(() => { window.__audio = []; const A = window.Audio; window.Audio = function (...a) { const e = new A(...a); window.__audio.push(e); return e; }; window.Audio.prototype = A.prototype; })();` });
await call('Page.navigate', { url: BASE + '/mau5.htm' });
await call('Page.bringToFront');
await sleep(3000);
const txt = (i) => ev(`document.getElementById('${i}').textContent`);
console.log('address', await ev('location.host'), '| conn:', await txt('conn'));
console.log('prompt:', (await ev(`document.getElementById('offbox').style.display`)), '|', (await txt('offat')).slice(0, 120), '| button:', await txt('offsave'));
console.log('songs line:', (await txt('songsat')).slice(0, 110));
// Pick the files as the phone's file picker would hand them over.
const files = process.argv.slice(2);
const doc = await call('DOM.getDocument');
const q = await call('DOM.querySelector', { nodeId: doc.result.root.nodeId, selector: '#songpick' });
await call('DOM.setFileInputFiles', { nodeId: q.result.nodeId, files });
await sleep(4000);
console.log('after picking %d files:', files.length, (await txt('showat')).slice(0, 300));
console.log('songs line:', (await txt('songsat')).slice(0, 110));
console.log('prompt now:', await ev(`document.getElementById('offbox').style.display`));
const r = await ev(`(() => { const e = document.getElementById('playall'); e.scrollIntoView({block:'center'}); const b = e.getBoundingClientRect(); return { x: b.x + b.width / 2, y: b.y + b.height / 2 }; })()`);
await call('Input.dispatchMouseEvent', { type: 'mousePressed', x: r.x, y: r.y, button: 'left', clickCount: 1 });
await call('Input.dispatchMouseEvent', { type: 'mouseReleased', x: r.x, y: r.y, button: 'left', clickCount: 1 });
await sleep(3000);
const st = () => ev(`(() => { const a = window.__audio[window.__audio.length - 1]; return { list: document.getElementById('listat').textContent.slice(0, 90), t: a ? +a.currentTime.toFixed(1) : -1, paused: a ? a.paused : null, sent: MAU5_LINK.sent, go: document.getElementById('go').textContent, fps: document.getElementById('fps').textContent, n: window.__audio.length }; })()`);
console.log('playing', JSON.stringify(await st()));
await ev(`(() => { const a = window.__audio[0]; a.currentTime = a.duration - 2; })()`);
await sleep(4500);
console.log('next   ', JSON.stringify(await st()));
// the eyes by finger
await ev(`document.getElementById('playall').click()`);
await sleep(1000);
await ev(`[...document.querySelectorAll('#grid button')].find(b => b.dataset.name === 'eyes').click()`);
await ev(`document.getElementById('go').click()`);
await sleep(1500);
const rc = await ev(`(() => { const e = document.getElementById('view'); e.scrollIntoView({block:'center'}); const b = e.getBoundingClientRect(); return { x: b.x, y: b.y, w: b.width, h: b.height, ta: e.style.touchAction }; })()`);
console.log('eyes preset, canvas', JSON.stringify(rc));
const lit = async () => (await (await fetch('http://127.0.0.1:8770/fake/stats')).json()).lit;
for (const [fx, fy] of [[0.15, 0.3], [0.85, 0.3], [0.5, 0.9]]) {
  await call('Input.dispatchMouseEvent', { type: 'mousePressed', x: rc.x + rc.w * fx, y: rc.y + rc.h * fy, button: 'left', clickCount: 1 });
  await sleep(500);
  const shot = await ev(`(async () => { const c = document.getElementById('view'); const x = c.getContext('2d'); const W = c.width, H = c.height; const d = x.getImageData(0, 0, W, H).data; let sx = 0, sy = 0, s = 0; for (let j = 0; j < H; j += 3) for (let i = 0; i < W; i += 3) { const v = d[(j * W + i) * 4 + 1]; if (v > 60) { sx += i * v; sy += j * v; s += v; } } return { cx: +(sx / s / W).toFixed(3), cy: +(sy / s / H).toFixed(3) }; })()`);
  console.log(' finger at', fx, fy, '-> lit centre', JSON.stringify(shot));
  await call('Input.dispatchMouseEvent', { type: 'mouseReleased', x: rc.x + rc.w * fx, y: rc.y + rc.h * fy, button: 'left', clickCount: 1 });
  await sleep(200);
}
await ev(`document.getElementById('go').click()`);
await sleep(500);
console.log('page errors:', errors.length ? errors.slice(0, 8) : 'none');
ws.close();
