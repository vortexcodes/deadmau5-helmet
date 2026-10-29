#!/usr/bin/env python3
"""mau5fake -- a controller that is not there, so the phone page can be.

The offline player talks to WLED and nothing else: same origin, JSON
API, WebSocket if there is one.  That is the right design and it has
one cost -- without a helmet on the desk there is nothing to develop
it against, and "it will probably work at the show" is not a state to
leave it in.

So this answers like the controller does.  It serves the built page at
the path the real one will serve it from, implements the parts of the
JSON API the player uses, speaks enough WebSocket to take frames, and
keeps the pixel buffer it was sent.  `/fake/view` draws that buffer,
which is the closest thing to looking at the helmet.

It is deliberately strict where the firmware is strict.  Individual
LED writes are refused unless the segment is frozen, because WLED
only keeps them in that state; a message over `--max-json` is dropped
silently, because an ESP32 whose buffer is too small does exactly
that and a player that never finds out would be tuned wrong.

    python3 mau5fake.py                       # http://127.0.0.1:8770/mau5.htm
    python3 mau5fake.py --lag 25 --max-json 4096
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import socket
import struct
import threading
import time
import urllib.request
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "data", "offline")

WS_GUID = b"258EAFA5-E914-47DA-95CA-C5AB0DC85B11"


class Fake:
    """What the controller believes about itself."""

    # A WebSocket message that does not fit in one TCP segment is
    # dropped by the firmware without a word: 1428 bytes lands, 1448
    # does not, and the MSS is 1436.  HTTP has no such limit -- a whole
    # 622-LED frame arrives in one 6.2 kB POST.
    WS_SEGMENT = 1436

    def __init__(self, count=622, lag_ms=0.0, max_json=8192, ws_echo=True,
                 ws=True, can_freeze=True):
        self.count = count
        self.can_freeze = can_freeze
        self.ws_echo = ws_echo
        self.ws = ws
        self.lag = lag_ms / 1000.0
        self.max_json = max_json
        self.lock = threading.Lock()
        self.px = np.zeros((count, 3), np.uint8)
        self.on = False
        self.bri = 128
        self.frozen = False
        self.nl = {"on": False, "dur": 60, "mode": 1, "tbri": 0}
        self.nl_armed_at = None
        self.stats = {"messages": 0, "pixels": 0, "dropped": 0,
                      "fragmented": 0, "refused": 0, "biggest": 0}
        self.rejects = []
        self.started = time.time()

    # -- the bit that matters --------------------------------------------
    def apply_state(self, d):
        """deserializeState, as far as the player exercises it."""
        with self.lock:
            if "on" in d:
                self.on = bool(d["on"])
                if not self.on:
                    self.px[:] = 0
            if "bri" in d:
                self.bri = int(d["bri"])
            if "nl" in d:
                self.nl.update(d["nl"])
                self.nl_armed_at = time.time() if self.nl.get("on") else None
            segs = d.get("seg")
            if segs is None:
                return
            for s in (segs if isinstance(segs, list) else [segs]):
                if "frz" in s and self.can_freeze:
                    self.frozen = bool(s["frz"])
                    if self.frozen:
                        # WLED blanks the segment as it freezes it
                        self.px[:] = 0
                arr = s.get("i")
                if arr is None:
                    continue
                if not self.frozen and self.can_freeze:
                    # The firmware freezes on the first `i`; so does this,
                    # and it blanks at the same moment, which is why a
                    # player that assumes otherwise sees a black frame.
                    self.frozen = True
                    self.px[:] = 0
                self._set_i(arr)

    def _set_i(self, arr):
        """Apply one `i` write the way the real firmware does.

        Including the part that was wrong here for a week: WLED 0.15.4
        **blanks the rest of the segment** first.  Measured on the
        helmet by writing LEDs 0-99, then 100-199, and reading the
        strip back -- only the second hundred was lit.  While this
        class accumulated instead, a player that split a frame across
        messages, or sent deltas, passed every test here and showed
        roughly a fifth of each frame on the helmet.
        """
        self.px[:] = 0
        i = 0
        at = 0
        while i < len(arr):
            v = arr[i]
            if isinstance(v, (int, float)):
                nxt = arr[i + 1] if i + 1 < len(arr) else None
                if isinstance(nxt, (int, float)):
                    col = self._col(arr[i + 2]) if i + 2 < len(arr) else None
                    if col is None:
                        return
                    a, b = int(v), int(nxt)
                    a = max(0, min(self.count, a)); b = max(a, min(self.count, b))
                    self.px[a:b] = col
                    self.stats["pixels"] += b - a
                    at = b
                    i += 3
                    continue
                at = int(v)
                i += 1
                continue
            col = self._col(v)
            if col is not None and 0 <= at < self.count:
                self.px[at] = col
                self.stats["pixels"] += 1
            at += 1
            i += 1

    def _reject(self, why, body):
        """Keep why, because a controller that drops messages in
        silence is exactly what makes this class worth having."""
        if len(self.rejects) < 20:
            self.rejects.append({"why": why,
                                 "head": body[:120].decode("utf-8", "replace")})

    @staticmethod
    def _col(v):
        if isinstance(v, str):
            s = v.lstrip("#")
            if len(s) == 6:
                return (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16))
            return None
        if isinstance(v, list) and len(v) >= 3:
            return tuple(int(x) & 255 for x in v[:3])
        return None

    def take(self, body):
        """One JSON message, with the firmware's limits in front of it."""
        self.stats["messages"] += 1
        self.stats["biggest"] = max(self.stats["biggest"], len(body))
        if len(body) > self.max_json:
            self.stats["dropped"] += 1
            self._reject("too big (%d bytes)" % len(body), body)
            return False
        try:
            d = json.loads(body)
        except ValueError as e:
            self.stats["dropped"] += 1
            self._reject("unparseable (%s)" % e, body)
            return False
        if self.lag:
            time.sleep(self.lag)
        self.apply_state(d)
        return True

    # -- what it says about itself ---------------------------------------
    def info(self):
        return {"ver": "0.14.4-fake", "vid": 2405090, "leds": {
            "count": self.count, "pwr": int(self.px.sum() / 765.0 * 19),
            "fps": 30, "maxpwr": 1622, "maxseg": 16},
            "name": "mau5head-fake", "arch": "esp32", "ip": "127.0.0.1",
            "uptime": int(time.time() - self.started), "fs": {"u": 40, "t": 983},
            "live": False}

    def state(self):
        return {"on": self.on, "bri": self.bri, "transition": 0,
                "nl": dict(self.nl),
                "seg": [{"id": 0, "start": 0, "stop": self.count, "len": self.count,
                         "fx": 0, "frz": self.frozen, "on": True, "bri": 255}]}

    def cfg(self):
        return {"ap": {"ssid": "mau5head-AP", "pskl": 10, "behav": 2, "chan": 1},
                "hw": {"led": {"total": self.count, "maxpwr": 1622, "ledma": 19}}}

    def expire_nightlight(self):
        """The dead man, on the firmware's side of the wire."""
        with self.lock:
            if self.nl.get("on") and self.nl_armed_at is not None:
                if time.time() - self.nl_armed_at > self.nl["dur"] * 60:
                    self.on = False
                    self.px[:] = 0
                    self.nl["on"] = False
                    self.nl_armed_at = None


VIEW = """<!doctype html><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>fake helmet</title>
<style>html,body{margin:0;background:#08080b;color:#8a8a99;
font:13px -apple-system,sans-serif}canvas{display:block;width:100vw;height:auto}
#s{position:fixed;left:8px;bottom:6px}</style>
<canvas id=c></canvas><div id=s></div><script>
let geo=null,cv=c,cx=c.getContext('2d'),dots=null;
async function boot(){geo=await (await fetch('/fake/geo')).json();size();loop();}
function size(){const w=innerWidth,dp=devicePixelRatio||1;
 let x0=1e9,x1=-1e9,y0=1e9,y1=-1e9;
 for(let i=0;i<geo.n;i++){x0=Math.min(x0,geo.px[i]);x1=Math.max(x1,geo.px[i]);
  y0=Math.min(y0,geo.py[i]);y1=Math.max(y1,geo.py[i]);}
 const h=Math.round(w*(y1-y0)/(x1-x0));cv.width=w*dp;cv.height=h*dp;cv.style.height=h+'px';
 const p=12*dp,s=Math.min((cv.width-2*p)/(x1-x0),(cv.height-2*p)/(y1-y0));
 dots=[];for(let i=0;i<geo.n;i++)dots.push([p+(geo.px[i]-x0)*s,cv.height-p-(geo.py[i]-y0)*s]);
 dots.r=Math.max(2,6*s/3.2);}
async function loop(){
 try{const b=new Uint8Array(await (await fetch('/fake/pixels',{cache:'no-store'})).arrayBuffer());
 cx.fillStyle='#08080b';cx.fillRect(0,0,cv.width,cv.height);
 let lit=0;for(let i=0;i<geo.n;i++){const r=b[i*3],g=b[i*3+1],bl=b[i*3+2];
  if(r+g+bl>3)lit++;
  cx.fillStyle=r+g+bl<3?'#15151b':'rgb('+Math.round(255*Math.pow(r/255,.45))+','
   +Math.round(255*Math.pow(g/255,.45))+','+Math.round(255*Math.pow(bl/255,.45))+')';
  cx.beginPath();cx.arc(dots[i][0],dots[i][1],dots.r,0,6.3);cx.fill();}
 s.textContent=lit+' of '+geo.n+' lit';}catch(e){s.textContent=e;}
 setTimeout(loop,100);}
addEventListener('resize',size);boot();
</script>"""


def _geo():
    import mau5engine as E
    h = E.Helmet()
    return {"n": int(h.n), "px": [round(float(v), 1) for v in h.px],
            "py": [round(float(v), 1) for v in h.py]}


def _proxy(host, path, body=None):
    url = "http://%s%s" % (host, path)
    req = urllib.request.Request(
        url, data=body, method="POST" if body is not None else "GET",
        headers={"Content-Type": "application/json"} if body is not None else {})
    with urllib.request.urlopen(req, timeout=5) as r:
        return r.read()


def make_handler(fake, geo, proxy=None):
    class H(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"

        def log_message(self, *a):
            pass

        def _send(self, body, ctype="application/json", code=200, extra=()):
            if isinstance(body, (dict, list)):
                body = json.dumps(body).encode()
            elif isinstance(body, str):
                body = body.encode()
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Cache-Control", "no-store")
            for k, v in extra:
                self.send_header(k, v)
            self.end_headers()
            self.wfile.write(body)

        def do_OPTIONS(self):
            self.send_response(204)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            self.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
            self.end_headers()

        def do_GET(self):
            p = self.path.split("?")[0]
            fake.expire_nightlight()
            if p in ("/", "/index.htm", "/index.html", "/mau5.htm"):
                f = os.path.join(OUT, "mau5.htm")
                if not os.path.exists(f):
                    return self._send("run: python3 mau5offline.py build",
                                      "text/plain", 404)
                return self._send(open(f, "rb").read(), "text/html; charset=utf-8")
            if p.startswith("/json") and proxy:
                try:
                    return self._send(_proxy(proxy, p), "application/json")
                except Exception as e:
                    return self._send({"error": str(e)}, code=502)
            if p == "/json/info":
                return self._send(fake.info())
            if p == "/json/state":
                return self._send(fake.state())
            if p == "/json/cfg":
                return self._send(fake.cfg())
            if p == "/json":
                return self._send({"state": fake.state(), "info": fake.info()})
            if p == "/fake/view":
                return self._send(VIEW, "text/html; charset=utf-8")
            if p == "/fake/geo":
                return self._send(geo)
            if p == "/fake/pixels":
                with fake.lock:
                    return self._send(fake.px.tobytes(), "application/octet-stream")
            if p == "/fake/stats":
                return self._send(dict(fake.stats, frozen=fake.frozen,
                                       on=fake.on, bri=fake.bri, nl=fake.nl,
                                       rejects=fake.rejects))
            if p == "/ws":
                if proxy:
                    # Proxying a websocket is a different job; over a
                    # LAN the posting path is fast enough to try the
                    # page against real hardware, which is the point.
                    return self._send({"error": "no websocket in proxy mode"},
                                      code=404)
                if not fake.ws:
                    # Some builds have the websocket compiled out, and
                    # the player has to fall back to posting.  That
                    # path needs exercising too.
                    return self._send({"error": "no websocket"}, code=404)
                return self._websocket()
            self._send({"error": "no route"}, code=404)

        def do_POST(self):
            p = self.path.split("?")[0]
            n = int(self.headers.get("Content-Length") or 0)
            body = self.rfile.read(n)
            if p.startswith("/json") and proxy:
                try:
                    return self._send(_proxy(proxy, p, body), "application/json")
                except Exception as e:
                    return self._send({"error": str(e)}, code=502)
            if p == "/json/state" or p == "/json":
                ok = fake.take(body)
                return self._send({"success": ok})
            if p == "/json/cfg":
                return self._send({"success": True})
            self._send({"error": "no route"}, code=404)

        # -- websocket ---------------------------------------------------
        def _websocket(self):
            key = self.headers.get("Sec-WebSocket-Key")
            if not key:
                return self._send({"error": "not a websocket"}, code=400)
            acc = base64.b64encode(
                hashlib.sha1(key.encode() + WS_GUID).digest()).decode()
            self.send_response(101)
            self.send_header("Upgrade", "websocket")
            self.send_header("Connection", "Upgrade")
            self.send_header("Sec-WebSocket-Accept", acc)
            self.end_headers()
            self.close_connection = True
            try:
                self._ws_loop()
            except (OSError, ConnectionError):
                pass

        def _ws_loop(self):
            sock = self.connection
            sock.settimeout(120)
            buf = b""
            parts = []
            while True:
                hdr = _recv(sock, 2)
                if not hdr:
                    return
                fin = hdr[0] & 0x80
                op = hdr[0] & 0x0F
                masked = hdr[1] & 0x80
                ln = hdr[1] & 0x7F
                if ln == 126:
                    ln = struct.unpack(">H", _recv(sock, 2))[0]
                elif ln == 127:
                    ln = struct.unpack(">Q", _recv(sock, 8))[0]
                mask = _recv(sock, 4) if masked else b"\0\0\0\0"
                data = _recv(sock, ln) if ln else b""
                if masked:
                    data = bytes(b ^ mask[i % 4] for i, b in enumerate(data))
                if op == 0x8:
                    return
                if op == 0x9:
                    sock.sendall(b"\x8a" + bytes([len(data)]) + data)
                    continue
                if op in (0x0, 0x1, 0x2):
                    parts.append(data)
                    if not fin:
                        # WLED only parses a message that arrives whole;
                        # counting these is the point of the exercise.
                        fake.stats["fragmented"] += 1
                        continue
                    buf = b"".join(parts)
                    parts = []
                    # The firmware drops a message that did not fit in
                    # one TCP segment, and says nothing.  Measured:
                    # 1428 bytes of payload lands, 1448 does not.
                    if len(buf) + 6 > fake.WS_SEGMENT:
                        fake.stats["oversize"] = fake.stats.get("oversize", 0) + 1
                        fake._reject("over one TCP segment (%d bytes)" % len(buf),
                                     buf)
                        continue
                    fake.take(buf)
                    # WLED answers some state messages by broadcasting
                    # the new state, and answers an `i` write with
                    # nothing at all -- measured, 665 pixel messages
                    # drew about six bytes each.  Echoing everything
                    # here is what let the player ship a credit window
                    # built on acknowledgements that never arrive.
                    quiet = b'"i"' in buf
                    if fake.ws_echo and not quiet:
                        out = json.dumps(fake.state()).encode()
                        hdr = b"\x81"
                        if len(out) < 126:
                            hdr += bytes([len(out)])
                        elif len(out) < 65536:
                            hdr += b"\x7e" + struct.pack(">H", len(out))
                        else:
                            hdr += b"\x7f" + struct.pack(">Q", len(out))
                        sock.sendall(hdr + out)

    return H


def _recv(sock, n):
    out = b""
    while len(out) < n:
        try:
            b = sock.recv(n - len(out))
        except socket.timeout:
            return b""
        if not b:
            return b""
        out += b
    return out


def serve(port=8770, host=None, lag_ms=0.0, max_json=8192, count=622,
          ws_echo=True, ws=True, bind="127.0.0.1", can_freeze=True,
          tls=False):
    """Serve the player, against the fake or against a real controller.

    With --host the JSON API is forwarded to the real thing instead of
    answered here, so the page can be tried on the helmet before it is
    uploaded to it.  That still needs the laptop, so it is a test
    rig and not offline mode; offline mode is `mau5offline.py deploy`.

    With --tls it is served over https, which is the only way the page
    gets a microphone.  A browser hands over a microphone on a secure
    origin and nowhere else, and the controller cannot be one -- WLED
    speaks plain http and that is that.  So for anything that has to
    listen, the laptop serves the page and forwards the pixels.  The
    certificate is self-signed and the phone will object once.
    """
    import mau5offline
    mau5offline.build(verbose=True)
    fake = Fake(count=count, lag_ms=lag_ms, max_json=max_json,
                ws_echo=ws_echo, ws=ws, can_freeze=can_freeze)
    if host:
        bind = "0.0.0.0"
    srv = ThreadingHTTPServer((bind, port), make_handler(fake, _geo(), host))
    scheme = "http"
    if tls:
        import ssl
        import mau5eye
        here = os.path.dirname(os.path.abspath(__file__))
        crt = os.path.join(here, "data", "cal", "tls", "eye.crt")
        key = os.path.join(here, "data", "cal", "tls", "eye.key")
        ip = _my_ip()
        try:
            mau5eye.ensure_cert(crt, key, [ip] if ip else [])
            ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            ctx.load_cert_chain(crt, key)
            srv.socket = ctx.wrap_socket(srv.socket, server_side=True)
            scheme = "https"
        except Exception as e:
            print("  could not start https (%s); serving plain http" % e)
    where = "127.0.0.1" if bind == "127.0.0.1" else _my_ip()
    print("\n  player     %s://%s:%d/mau5.htm" % (scheme, where, port))
    if scheme == "https":
        print("             self-signed, so it warns once: Advanced -> "
              "Proceed.\n             This is the build that can use the "
              "microphone.")
    if host:
        print("  the JSON API is forwarded to %s -- the real helmet" % host)
    else:
        print("  helmet     http://%s:%d/fake/view" % (where, port))
        print("  counters   http://%s:%d/fake/stats" % (where, port))
        print("\n  lag %.0f ms per message, json buffer %d bytes"
              % (lag_ms, max_json))
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
    print("\n%s" % json.dumps(fake.stats))
    return 0


def _my_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("10.255.255.255", 1))
        return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        s.close()


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--port", type=int, default=8770)
    ap.add_argument("--lag", type=float, default=0.0,
                    help="milliseconds the controller takes per message")
    ap.add_argument("--max-json", type=int, default=8192,
                    help="drop anything bigger, as a small buffer would")
    ap.add_argument("--count", type=int, default=622)
    ap.add_argument("--host", default=None,
                    help="forward the JSON API to a real controller, and "
                         "listen on every interface so a phone can reach it")
    ap.add_argument("--no-ws-echo", dest="ws_echo", action="store_false",
                    default=True, help="do not broadcast state back over the "
                                       "websocket, as a build that stays quiet")
    ap.add_argument("--no-ws", dest="ws", action="store_false", default=True,
                    help="refuse /ws, as a build with it compiled out")
    ap.add_argument("--no-freeze", dest="can_freeze", action="store_false",
                    default=True, help="ignore seg.frz, as a build older "
                                       "than 0.13 does")
    a = ap.parse_args(argv)
    return serve(a.port, a.host, a.lag, a.max_json, a.count, a.ws_echo,
                 a.ws, can_freeze=a.can_freeze)


if __name__ == "__main__":
    raise SystemExit(main())
