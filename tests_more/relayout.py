"""A controller that restarts mid-show comes back lit, without a tap.

Measured tonight: under load WLED 0.15.4 restarted several times, and a
restarted controller comes up off with one unfrozen segment.  The page
reconnected but sent frames to segments that no longer existed, so the
helmet stayed dark until somebody pressed stop and start.
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
const posts = [];
global.fetch = async (url, init) => {
  if (init && init.body) posts.push(JSON.parse(init.body));
  return { ok: true, json: async () => ({ seg: [{ id: 0 }] }), text: async () => '' };
};
let opened = 0;
global.location = { protocol: 'http:', host: '192.168.10.172' };
global.WebSocket = class {
  constructor(u) { this.readyState = 0; this.sent = []; opened++;
                   setTimeout(() => { this.readyState = 1; this.onopen && this.onopen(); }, 5); }
  send(m) { this.sent.push(m); }
  close() { this.readyState = 3; this.onclose && this.onclose(); }
};

(async () => {
  const L = new W.Link({ count: 621, deadmanMins: 1 });
  L.streaming = true;                       // as after begin()
  L.bri = 180;
  // the socket dies -- a restarted controller
  L.ws = null;
  L.reopen(performance.now());
  await new Promise(r => setTimeout(r, 60));
  const lay = posts.find(p => p.seg && p.seg.length >= L.segs.length && p.seg[0].start === 0);
  const out = {
    opened, relayouts: L.relayouts || 0,
    on: lay ? lay.on : null, bri: lay ? lay.bri : null,
    nl: lay && lay.nl ? lay.nl.on : null,
    segs: lay ? lay.seg.filter(s => s.frz && s.stop > s.start).length : 0,
    want: L.segs.length,
    whole: L.last.every(x => x === null),
  };
  // and nothing of the sort when the page is not streaming
  posts.length = 0;
  const M = new W.Link({ count: 621, deadmanMins: 1 });
  M.streaming = false; M.ws = null; M.reopen(performance.now());
  await new Promise(r => setTimeout(r, 60));
  out.idlePosts = posts.length;
  process.stdout.write(JSON.stringify(out));
})();
"""


def t_reconnect_relays_out():
    if not shutil.which("node"):
        return note("relayout: node not installed")
    wire = os.path.join(HERE, "remote", "offline", "wire.js")
    p = subprocess.run(["node", "-e", JS, wire], capture_output=True, text=True, timeout=60)
    ok(p.returncode == 0, p.stderr[-800:])
    r = json.loads(p.stdout)
    eq(r["opened"], 1, "one socket opened on reconnect")
    eq(r["relayouts"], 1, "the layout must be sent again after a reconnect")
    ok(r["on"] is True, "the helmet must be turned back on")
    eq(r["bri"], 180, "at the page's brightness")
    ok(r["nl"] is True, "with the dead man armed in the same request")
    eq(r["segs"], r["want"], "every segment laid out and frozen again")
    ok(r["whole"], "the next frame must go whole")
    eq(r["idlePosts"], 0, "a page that is not streaming must not light the helmet")


GROUP = [t_reconnect_relays_out]
