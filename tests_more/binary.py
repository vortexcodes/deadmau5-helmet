"""Binary frames for WLED 16, and nothing changes for 0.15.4.

WLED 16 takes DDP over the page's WebSocket (first byte 2), with no JSON
to parse and no reply per message -- the two things 0.15.4 could not keep
up with.  The page switches only when the controller says it is 16 or
later, so a helmet still on 0.15.4 keeps the path that was soak-tested.
"""
import json
import os
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from test_mau5 import ok, eq, note, HERE  # noqa: E402

JS = r"""
const W = require(process.argv[1]);
const out = { vers: {} };
for (const v of ['0.15.4', '0.15.0', '16.0.1', '16.1.0', '0.16.0-b1', '17.0.0', '', 'x'])
  out.vers[v] = W.takesBinary(v);
const n = 621;
const strips = [{ start: 492, count: 37, order: 'GRB' }];
const L = new W.Link({ count: n, strips, deadmanMins: 0 });
L.binary = true; L._setDepth(W.DEPTH_BINARY);
const sent = [];
L.ws = { readyState: 1, bufferedAmount: 0, send: (m) => sent.push(m) };
const f = new Uint8Array(n * 3);
for (let i = 0; i < n * 3; i++) f[i] = (i * 37 + 11) & 255;
out.ret = L.send(f);
out.msgs = sent.map(m => typeof m === 'string' ? { text: m.length > 9 ? 'filler' + m.length : m }
                                                  : { bin: Array.from(m) });
// decode the DDP packets back into one frame
const got = new Array(n * 3).fill(-1);
let pushes = 0;
for (const m of sent) {
  if (typeof m === 'string') continue;
  const off = (m[5] << 24) | (m[6] << 16) | (m[7] << 8) | m[8], len = (m[9] << 8) | m[10];
  if (m[1] & 1) pushes++;
  for (let k = 0; k < len; k++) got[off + k] = m[11 + k];
}
const want = [];
for (let i = 0; i < n; i++) { const b = i * 3; for (let c = 0; c < 3; c++) want.push(f[b + L.perm[b + c]]); }
out.exact = got.every((v, i) => v === want[i]);
out.pushes = pushes;
out.lastIsPush = !!(sent.filter(m => typeof m !== 'string').slice(-1)[0][1] & 1);
out.sizes = sent.filter(m => typeof m !== 'string').map(m => m.length);
out.first = sent.filter(m => typeof m !== 'string').map(m => m[0]);
// the same frame again: nothing sent
L._pong(); sent.length = 0; out.again = L.send(f); out.againMsgs = sent.length;
// a 0.15.4 link stays on JSON
const J = new W.Link({ count: n, deadmanMins: 0 });
const js = []; J.ws = { readyState: 1, bufferedAmount: 0, send: (m) => js.push(m) };
J.send(f); out.jsonFirst = typeof js[0] === 'string' && js[0].startsWith('{"seg"');
out.jsonDepth = J.depth;
out.pad = W.PAD;
process.stdout.write(JSON.stringify(out));
"""


def t_binary_frames_for_wled16():
    if not shutil.which("node"):
        return note("binary: node not installed")
    wire = os.path.join(HERE, "remote", "offline", "wire.js")
    p = subprocess.run(["node", "-e", JS, wire], capture_output=True, text=True, timeout=60)
    ok(p.returncode == 0, p.stderr[-800:])
    r = json.loads(p.stdout)
    v = r["vers"]
    ok(not v["0.15.4"] and not v["0.15.0"], "0.15 must keep the JSON path")
    ok(v["16.0.1"] and v["16.1.0"] and v["0.16.0-b1"] and v["17.0.0"], "16 and later take binary")
    ok(not v[""] and not v["x"], "an unknown version must not switch")
    ok(r["exact"], "the DDP packets must carry exactly the colour-corrected frame")
    eq(r["pushes"], 1, "one push per frame")
    ok(r["lastIsPush"], "the push is on the last packet")
    ok(all(sz == r["pad"] for sz in r["sizes"]), "every packet exactly one segment: %s" % r["sizes"])
    ok(all(b == 2 for b in r["first"]), "first byte 2 means DDP to WLED's socket")
    texts = [m["text"] for m in r["msgs"] if "text" in m]
    eq(texts[0], "p", "each frame ends with its ping")
    eq(r["again"], 0, "an unchanged frame is not sent again")
    eq(r["againMsgs"], 0, "and nothing goes out for it")
    ok(r["jsonFirst"], "a link that has not seen WLED 16 keeps sending JSON")
    eq(r["jsonDepth"], 1, "and keeps one frame in flight")


GROUP = [t_binary_frames_for_wled16]
