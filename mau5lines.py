#!/usr/bin/env python3
"""mau5lines -- walk the map one line at a time and correct it by eye.

The camera settled where 622 LEDs are, and it is right about nearly
all of them.  What it cannot settle is the handful it never saw
properly: a strip crossing a gap edge-on, a run with LEDs cut out
around a visor magnet, a disc whose tilt one pose cannot measure.
Those are invisible to a solver and obvious to somebody standing in
front of the helmet, so this is the tool for that person.

It lights one line at a time -- a vertical band across the face by
default -- and shows, next to it, where the map thinks those LEDs
are.  Two pictures of the same claim: one on the helmet and one on
the phone.  When they disagree, the disagreement is the finding, and
the same page writes it down.

Four corrections, which between them cover everything that has
actually been wrong here:

  move     the span sits somewhere else: nudge it in millimetres
  shift    LEDs were cut out of this run, so everything after the
           cut is one or more pitches further along than the map
           believes -- the chain does not skip, the geometry does
  reverse  the strip is wired the other way round
  region   this run is not on the surface it was filed under

They go to data/cal/adjust.json, which mau5map.load applies on top of
the measured map.  Nothing here edits pixel_map.csv: re-running the
localisation must not silently throw away what somebody saw, and what
was measured should stay told apart from what was judged.

    python3 mau5lines.py                 # serve, open the printed URL
    python3 mau5lines.py --port 8762
"""

from __future__ import annotations

import argparse
import json
import os
import threading
import time
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler

import numpy as np

import mau5engine as E
import mau5map
import mau5wled

HERE = os.path.dirname(os.path.abspath(__file__))
ADJUST = mau5map.ADJUST
MARKS = os.path.join(HERE, "data", "cal", "line_marks.json")

# The axes worth walking.  "x" is the one the helmet is usually wrong
# about, because a vertical line is the only view in which a strip
# that has slipped along its own length shows up as a kink.
AXES = ("x", "y", "z", "strip", "run")


def runs_of(rows):
    """Contiguous chain runs: same strip, consecutive index."""
    out, cur = [], None
    for r in rows:
        if cur and r["group"] == cur["group"] and r["index"] == cur["hi"] + 1:
            cur["hi"] = r["index"]
        else:
            cur = {"group": r["group"], "lo": r["index"], "hi": r["index"]}
            out.append(cur)
    return out


class Lines:
    def __init__(self, host=None, steps=28, width=26.0, level=90):
        self.rows = mau5map.load()
        self.h = E.Helmet()
        self.n = len(self.rows)
        self.steps, self.width, self.level = steps, width, level
        self.axis, self.i = "x", 0
        self.colour = [255, 255, 255]
        self.runs = runs_of(self.rows)
        self.groups = sorted(set(r["group"] for r in self.rows))
        self.lock = threading.Lock()
        self.note = ""
        self.marks = self._read(MARKS, {})
        self.adjust = self._read(ADJUST, {"spans": []})
        self.wled = mau5wled.find_one(host)
        self.wled.realtime(True, brightness=255)
        self.pix = mau5wled.Pixels(self.wled, count=self.n)
        self.stream = mau5wled.Streamer(self.pix, fps=15)
        self.on = False
        self.show()

    # -- persistence ----------------------------------------------------
    @staticmethod
    def _read(path, dflt):
        try:
            with open(path) as f:
                return json.load(f)
        except Exception:
            return dflt

    def _write(self, path, doc):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        tmp = path + ".tmp"
        with open(tmp, "w") as f:
            json.dump(doc, f, indent=1)
        os.replace(tmp, path)

    # -- which LEDs is this line? ---------------------------------------
    def count_for(self, axis):
        if axis == "strip":
            return len(self.groups)
        if axis == "run":
            return len(self.runs)
        return self.steps

    def members(self, axis=None, i=None):
        axis = axis or self.axis
        i = self.i if i is None else i
        i = max(0, min(self.count_for(axis) - 1, i))
        if axis == "strip":
            g = self.groups[i]
            return np.array([r["group"] == g for r in self.rows])
        if axis == "run":
            rn = self.runs[i]
            idx = np.arange(self.n)
            return (idx >= rn["lo"]) & (idx <= rn["hi"])
        v = {"x": self.h.px, "y": self.h.py, "z": self.h.depth}[axis]
        lo, hi = float(v.min()), float(v.max())
        at = lo + (hi - lo) * i / max(self.count_for(axis) - 1, 1)
        return np.abs(v - at) <= self.width / 2.0

    def label(self, axis=None, i=None):
        axis = axis or self.axis
        i = self.i if i is None else i
        if axis == "strip":
            g = self.groups[max(0, min(len(self.groups) - 1, i))]
            same = [r for r in self.rows if r["group"] == g]
            return "strip %d  (%s, %d leds, %d-%d)" % (
                g, same[0]["region"], len(same), same[0]["index"], same[-1]["index"])
        if axis == "run":
            rn = self.runs[max(0, min(len(self.runs) - 1, i))]
            return "run %d-%d  (strip %d, %d leds)" % (
                rn["lo"], rn["hi"], rn["group"], rn["hi"] - rn["lo"] + 1)
        v = {"x": self.h.px, "y": self.h.py, "z": self.h.depth}[axis]
        lo, hi = float(v.min()), float(v.max())
        at = lo + (hi - lo) * i / max(self.count_for(axis) - 1, 1)
        nm = {"x": "across", "y": "up", "z": "depth"}[axis]
        return "%s = %+.0f mm" % (nm, at)

    def span(self):
        """The index range this line covers, for an adjustment."""
        m = np.where(self.members())[0]
        return (int(m[0]), int(m[-1])) if len(m) else (0, 0)

    # -- output ---------------------------------------------------------
    def show(self):
        buf = np.zeros((self.n, 3), np.uint8)
        m = self.members()
        if m.any():
            buf[m] = [int(c * self.level / 255.0) for c in self.colour]
        self.stream.show(buf)
        self.on = True

    def off(self):
        self.stream.dark()
        self.on = False

    def stop(self):
        try:
            self.stream.stop()
            self.wled.off()
        except Exception:
            pass

    # -- what the page sees ----------------------------------------------
    def state(self):
        m = self.members()
        idx = [int(v) for v in np.where(m)[0]]
        lo, hi = self.span()
        key = "%s:%d" % (self.axis, self.i)
        return {
            "axis": self.axis, "i": self.i, "count": self.count_for(self.axis),
            "label": self.label(), "lit": len(idx),
            "indices": idx[:400], "lo": lo, "hi": hi,
            "width": self.width, "level": self.level, "colour": self.colour,
            "on": self.on, "mark": self.marks.get(key),
            "marks": {"good": sum(1 for v in self.marks.values() if v.get("verdict") == "good"),
                      "bad": sum(1 for v in self.marks.values() if v.get("verdict") == "bad")},
            "adjust": self.adjust.get("spans", []),
            "helmet": self.wled.base,
        }

    def geometry(self):
        """The map as the page draws it: screen x, screen y, region."""
        return {"n": self.n,
                "px": [round(float(v), 1) for v in self.h.px],
                "py": [round(float(v), 1) for v in self.h.py],
                "region": [str(r) for r in self.h.region]}

    # -- edits ------------------------------------------------------------
    def mark(self, verdict, note=""):
        key = "%s:%d" % (self.axis, self.i)
        lo, hi = self.span()
        self.marks[key] = {"verdict": verdict, "note": note, "lo": lo, "hi": hi,
                           "label": self.label(),
                           "when": time.strftime("%Y-%m-%dT%H:%M:%S")}
        self._write(MARKS, self.marks)

    def add_adjust(self, a):
        a = dict(a)
        a.setdefault("when", time.strftime("%Y-%m-%dT%H:%M:%S"))
        self.adjust.setdefault("spans", []).append(a)
        self._write(ADJUST, self.adjust)
        self.reload()

    def undo(self):
        if self.adjust.get("spans"):
            self.adjust["spans"].pop()
            self._write(ADJUST, self.adjust)
            self.reload()

    def reload(self):
        """Re-read the map so the next line is lit through the new fix."""
        self.rows = mau5map.load()
        self.h = E.Helmet()
        self.runs = runs_of(self.rows)
        self.show()


PAGE = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>mau5lines</title>
<style>
 :root{--bg:#0c0c10;--fg:#e9e9f0;--dim:#8b8b99;--line:#24242e;--ok:#2f9e63;--bad:#c2344d;--go:#1b4fd8}
 *{box-sizing:border-box}
 body{margin:0;background:var(--bg);color:var(--fg);padding:12px 12px 120px;
   font:15px/1.45 ui-sans-serif,system-ui,-apple-system,Roboto,sans-serif}
 h1{font-size:17px;margin:0 0 2px}
 .dim{color:var(--dim);font-size:12px}
 canvas{width:100%;background:#000;border:1px solid var(--line);border-radius:10px;display:block;margin:10px 0}
 .row{display:flex;gap:8px;align-items:center;margin:8px 0;flex-wrap:wrap}
 button{min-height:46px;border-radius:10px;border:1px solid var(--line);
   background:#1a1a22;color:var(--fg);font:500 15px/1 inherit;padding:0 14px;flex:1}
 button.on{background:var(--go);border-color:var(--go);color:#fff}
 button.good{background:var(--ok);border-color:var(--ok);color:#fff}
 button.bad{background:var(--bad);border-color:var(--bad);color:#fff}
 button.wide{flex:2}
 input[type=range]{flex:1}
 input[type=text],input[type=number]{background:#15151c;color:var(--fg);
   border:1px solid var(--line);border-radius:8px;padding:10px;font:inherit;min-width:0}
 .panel{border:1px solid var(--line);border-radius:12px;padding:10px;margin:10px 0}
 .big{font-size:19px;font-weight:600}
 ul{margin:6px 0;padding-left:18px;font-size:12px;color:var(--dim)}
 footer{position:fixed;left:0;right:0;bottom:0;background:#0b0b10f2;padding:10px 12px
   calc(10px + env(safe-area-inset-bottom));border-top:1px solid var(--line);display:flex;gap:8px}
</style></head><body>
<h1>mau5lines</h1>
<div class="dim" id="helmet">…</div>
<canvas id="map" height="300"></canvas>
<div class="big" id="label">…</div>
<div class="dim" id="sub">…</div>

<div class="row" id="axes"></div>
<div class="row">
  <span class="dim">width</span><input id="w" type="range" min="8" max="90" step="2">
  <span class="dim">level</span><input id="lv" type="range" min="10" max="200" step="5">
</div>

<div class="panel">
  <div class="row">
    <button id="good" class="wide">looks right</button>
    <button id="bad" class="wide">wrong here</button>
  </div>
  <input id="note" type="text" placeholder="what looks wrong (optional)" style="width:100%">
</div>

<div class="panel">
  <div class="dim">correct leds <b id="span">0-0</b></div>
  <div class="row">
    <span class="dim">move mm</span>
    <input id="dx" type="number" value="0" step="2" style="width:70px">
    <input id="dy" type="number" value="0" step="2" style="width:70px">
    <input id="dz" type="number" value="0" step="2" style="width:70px">
    <button id="move">move</button>
  </div>
  <div class="row">
    <span class="dim">cut</span>
    <input id="by" type="number" value="1" step="1" style="width:70px">
    <button id="shift">leds missing here</button>
    <button id="rev">reverse</button>
  </div>
  <div class="row">
    <input id="rg" type="text" placeholder="region name" style="flex:1">
    <button id="region">relabel</button>
  </div>
  <ul id="hist"></ul>
  <div class="row"><button id="undo">undo the last correction</button></div>
</div>

<footer>
  <button id="prev">‹ prev</button>
  <button id="light" class="wide on">lights on</button>
  <button id="next">next ›</button>
</footer>

<script>
const $ = id => document.getElementById(id);
let S = null, G = null;

async function api(path, body) {
  const r = await fetch(path, body ? {method:'POST',
    headers:{'Content-Type':'application/json'}, body: JSON.stringify(body)} : {});
  return r.json();
}

function draw() {
  if (!G || !S) return;
  const cv = $('map'), cx = cv.getContext('2d');
  const w = cv.clientWidth * devicePixelRatio, h = 300 * devicePixelRatio;
  if (cv.width !== w) { cv.width = w; cv.height = h; }
  cx.clearRect(0, 0, w, h);
  const x0 = Math.min(...G.px), x1 = Math.max(...G.px);
  const y0 = Math.min(...G.py), y1 = Math.max(...G.py);
  const pad = 12 * devicePixelRatio;
  const s = Math.min((w - 2*pad) / (x1 - x0), (h - 2*pad) / (y1 - y0));
  const ox = (w - (x1 - x0) * s) / 2, oy = (h - (y1 - y0) * s) / 2;
  const lit = new Set(S.indices);
  const r = Math.max(1.6, 2.2 * devicePixelRatio);
  for (let i = 0; i < G.n; i++) {
    const X = ox + (G.px[i] - x0) * s, Y = h - (oy + (G.py[i] - y0) * s);
    cx.beginPath();
    cx.arc(X, Y, lit.has(i) ? r * 2 : r, 0, 7);
    cx.fillStyle = lit.has(i) ? '#fff' : (G.region[i] === 'shell' ? '#26263a' : '#2e2440');
    cx.fill();
  }
}

function render() {
  $('label').textContent = S.label;
  $('sub').textContent = S.lit + ' leds, ' + S.lo + '–' + S.hi
    + ' · line ' + (S.i + 1) + ' of ' + S.count
    + ' · ' + S.marks.good + ' ok, ' + S.marks.bad + ' flagged';
  $('span').textContent = S.lo + '-' + S.hi;
  $('helmet').textContent = S.helmet;
  $('good').className = 'wide' + (S.mark && S.mark.verdict === 'good' ? ' good' : '');
  $('bad').className  = 'wide' + (S.mark && S.mark.verdict === 'bad'  ? ' bad'  : '');
  $('note').value = (S.mark && S.mark.note) || '';
  $('light').textContent = S.on ? 'lights on' : 'lights off';
  $('light').className = 'wide' + (S.on ? ' on' : '');
  $('w').value = S.width; $('lv').value = S.level;
  $('axes').innerHTML = '';
  for (const a of ['x','y','z','strip','run']) {
    const b = document.createElement('button');
    b.textContent = {x:'across', y:'up', z:'depth', strip:'strips', run:'runs'}[a];
    if (a === S.axis) b.className = 'on';
    b.onclick = () => go({axis: a, i: 0});
    $('axes').appendChild(b);
  }
  $('hist').innerHTML = '';
  for (const a of S.adjust.slice(-6)) {
    const li = document.createElement('li');
    li.textContent = a.op + ' ' + a.lo + '-' + a.hi + ' '
      + (a.op === 'move' ? `(${a.dx||0},${a.dy||0},${a.dz||0}) mm`
         : a.op === 'shift' ? 'by ' + a.by
         : a.op === 'region' ? '→ ' + a.to : '');
    $('hist').appendChild(li);
  }
  draw();
}

async function go(body) { S = await api('/api/show', body); render(); }

(async () => {
  G = await api('/api/geometry');
  S = await api('/api/state');
  render();
  $('prev').onclick = () => go({i: S.i - 1});
  $('next').onclick = () => go({i: S.i + 1});
  $('light').onclick = () => go({on: !S.on});
  $('w').oninput = e => go({width: +e.target.value});
  $('lv').oninput = e => go({level: +e.target.value});
  $('good').onclick = async () => { S = await api('/api/mark',
    {verdict:'good', note:$('note').value}); render(); go({i: S.i + 1}); };
  $('bad').onclick = async () => { S = await api('/api/mark',
    {verdict:'bad', note:$('note').value}); render(); };
  $('move').onclick = () => adj({op:'move', dx:+$('dx').value, dy:+$('dy').value, dz:+$('dz').value});
  $('shift').onclick = () => adj({op:'shift', by:+$('by').value});
  $('rev').onclick = () => adj({op:'reverse'});
  $('region').onclick = () => adj({op:'region', to:$('rg').value});
  $('undo').onclick = async () => { S = await api('/api/undo', {}); render(); };
  addEventListener('resize', draw);
  addEventListener('keydown', e => {
    if (e.key === 'ArrowRight') go({i: S.i + 1});
    if (e.key === 'ArrowLeft') go({i: S.i - 1});
  });
})();

async function adj(a) {
  a.lo = S.lo; a.hi = S.hi;
  S = await api('/api/adjust', a);
  G = await api('/api/geometry');          // the map moved
  render();
}
</script></body></html>
"""


def make_handler(L):
    class H(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"

        def log_message(self, *a):
            pass

        def _send(self, body, ctype="application/json", code=200):
            if not isinstance(body, bytes):
                body = json.dumps(body).encode()
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            if self.path in ("/", "/index.html"):
                return self._send(PAGE.encode(), "text/html; charset=utf-8")
            if self.path == "/api/state":
                return self._send(L.state())
            if self.path == "/api/geometry":
                return self._send(L.geometry())
            return self._send({"error": "no route"}, code=404)

        def do_POST(self):
            n = int(self.headers.get("Content-Length") or 0)
            body = json.loads(self.rfile.read(n) or b"{}")
            with L.lock:
                try:
                    if self.path == "/api/show":
                        if "axis" in body and body["axis"] in AXES:
                            L.axis = body["axis"]
                        if "i" in body:
                            L.i = max(0, min(L.count_for(L.axis) - 1, int(body["i"])))
                        if "width" in body:
                            L.width = float(body["width"])
                        if "level" in body:
                            L.level = int(body["level"])
                        if "colour" in body:
                            L.colour = [int(v) for v in body["colour"]][:3]
                        if body.get("on") is False:
                            L.off()
                        else:
                            L.show()
                    elif self.path == "/api/mark":
                        L.mark(body.get("verdict", "good"), body.get("note", ""))
                    elif self.path == "/api/adjust":
                        L.add_adjust(body)
                    elif self.path == "/api/undo":
                        L.undo()
                    else:
                        return self._send({"error": "no route"}, code=404)
                except Exception as e:
                    return self._send({"error": "%s: %s" % (type(e).__name__, e)},
                                      code=400)
            return self._send(L.state())
    return H


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--host", default=None, help="controller address")
    ap.add_argument("--port", type=int, default=8762)
    ap.add_argument("--steps", type=int, default=28,
                    help="how many lines the across/up/depth sweeps have")
    ap.add_argument("--width", type=float, default=26.0, help="line thickness, mm")
    ap.add_argument("--level", type=int, default=90)
    a = ap.parse_args(argv)

    try:
        L = Lines(a.host, a.steps, a.width, a.level)
    except mau5wled.WLEDError as e:
        print(e)
        return 1
    srv = ThreadingHTTPServer(("0.0.0.0", a.port), make_handler(L))
    # mau5wled's version skips the tunnel interfaces, which is the
    # difference between an address the phone can open and one it
    # cannot -- this machine has a VPN up most of the time.
    print("mau5lines on http://%s:%d   (helmet %s)"
          % (mau5wled.lan_ip(), a.port, L.wled.base))
    print("  corrections go to %s" % ADJUST)
    print("  verdicts go to    %s" % MARKS)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        L.stop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
