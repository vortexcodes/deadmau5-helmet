#!/usr/bin/env python3
"""mau5eye -- borrow a camera through a browser, because the shell cannot have one.

Capturing straight from the webcam needs the macOS camera permission, and
that is a dialog somebody has to click.  A browser already holds that
permission, so this serves a page that opens the camera, pushes frames
back here, and leaves the newest one on disk where anything can read it.

It does not care whose browser.  The Mac's own browser sees the webcam
plugged into the Mac; a phone pointed at the helmet and propped up works
exactly as well, and needs no cable.

    python3 mau5eye.py                 # serve, then open the printed URL
    python3 mau5eye.py --shot out.jpg  # grab one frame from a running one
"""

from __future__ import annotations

import argparse
import json
import os
import ssl
import threading
import time
import urllib.request
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler

HERE = os.path.dirname(os.path.abspath(__file__))

PAGE = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>mau5eye</title>
<style>
 :root{--bg:#0d0d10;--fg:#e8e8ef;--dim:#8a8a99;--ok:#38d39f;--hot:#ff2d6f}
 *{box-sizing:border-box}
 html,body{margin:0;height:100%;background:var(--bg);color:var(--fg);
   font:15px/1.4 ui-sans-serif,system-ui,-apple-system,Roboto,sans-serif}
 body{display:flex;flex-direction:column}
 header{display:flex;gap:8px;align-items:center;padding:8px 12px;
   border-bottom:1px solid #2a2a35;flex:none}
 .dot{width:9px;height:9px;border-radius:50%;background:var(--dim)}
 .dot.on{background:var(--ok);box-shadow:0 0 8px var(--ok)}
 .dot.err{background:var(--hot)}
 #s{margin-left:auto;font-size:12px;color:var(--dim);font-variant-numeric:tabular-nums}
 #wrap{flex:1;position:relative;background:#000;min-height:0}
 video{width:100%;height:100%;object-fit:contain;display:block}
 #bar{padding:9px 12px;border-top:1px solid #2a2a35;flex:none;display:flex;
   gap:9px;align-items:center;flex-wrap:wrap}
 button,select{min-height:46px;border-radius:11px;border:1px solid #2a2a35;
   background:#20202a;color:var(--fg);font-size:15px;padding:0 13px}
 button.go{background:linear-gradient(180deg,#0097c4,#006c8c);border:none;
   color:#fff;font-weight:700;flex:1}
 .note{font-size:12px;color:var(--dim);width:100%}
</style></head><body>
<header><span class="dot" id="d"></span><b>mau5eye</b><span id="s">idle</span></header>
<div id="wrap"><video id="v" playsinline autoplay muted></video></div>
<div id="bar">
  <button class="go" id="go">START CAMERA</button>
  <select id="cam"></select>
  <div class="note">Leave this page open and the camera pointed at the helmet.
    Keep the screen from sleeping.</div>
</div>
<script>
let stream=null, timer=null, n=0, fails=0;
const v=document.getElementById('v'), d=document.getElementById('d'),
      s=document.getElementById('s'), sel=document.getElementById('cam');
const cv=document.createElement('canvas');

async function listCams(){
  try{
    const ds=await navigator.mediaDevices.enumerateDevices();
    sel.innerHTML='';
    ds.filter(x=>x.kind==='videoinput').forEach((x,i)=>{
      const o=document.createElement('option');
      o.value=x.deviceId; o.textContent=x.label||('camera '+(i+1));
      sel.appendChild(o);
    });
  }catch(e){}
}

async function start(){
  if(stream) stream.getTracks().forEach(t=>t.stop());
  const c={video:{width:{ideal:1920},height:{ideal:1080}}, audio:false};
  if(sel.value) c.video.deviceId={exact:sel.value};
  try{
    stream=await navigator.mediaDevices.getUserMedia(c);
  }catch(e){ d.className='dot err'; s.textContent='denied: '+e.name; return; }
  v.srcObject=stream; await v.play().catch(()=>{});
  await listCams();
  d.className='dot on';
  if(timer) clearInterval(timer);
  timer=setInterval(push, 400);
}

async function push(){
  if(!v.videoWidth) return;
  cv.width=v.videoWidth; cv.height=v.videoHeight;
  cv.getContext('2d').drawImage(v,0,0);
  const b=await new Promise(r=>cv.toBlob(r,'image/jpeg',0.86));
  if(!b) return;
  try{
    await fetch('/frame',{method:'POST',headers:{'Content-Type':'image/jpeg'},body:b});
    n++; fails=0; d.className='dot on';
    s.textContent=n+' frames · '+cv.width+'×'+cv.height;
  }catch(e){ fails++; if(fails>2) d.className='dot err'; }
}

document.getElementById('go').onclick=start;
sel.onchange=()=>{ if(stream) start(); };
navigator.mediaDevices?.addEventListener?.('devicechange', listCams);
listCams();
</script></body></html>
"""


class Eye:
    """Holds the newest frame pushed by whatever browser is looking."""

    def __init__(self, path):
        self.path = path
        self.lock = threading.Lock()
        self.frame = None
        self.at = 0.0
        self.n = 0

    def put(self, data):
        with self.lock:
            self.frame, self.at, self.n = data, time.time(), self.n + 1
        tmp = self.path + ".tmp"
        with open(tmp, "wb") as f:
            f.write(data)
        os.replace(tmp, self.path)

    def get(self):
        with self.lock:
            return self.frame, self.at, self.n


def make_handler(eye):
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
                return self._send(PAGE.encode("utf-8"), "text/html; charset=utf-8")
            if self.path.startswith("/latest"):
                f, at, n = eye.get()
                if not f:
                    return self._send({"error": "no frame yet"}, code=404)
                return self._send(f, "image/jpeg")
            if self.path.startswith("/api/status"):
                f, at, n = eye.get()
                return self._send({"have": bool(f), "frames": n,
                                   "bytes": len(f) if f else 0,
                                   "age": round(time.time() - at, 2) if f else None})
            self._send({"error": "no route"}, code=404)

        def do_POST(self):
            if self.path == "/frame":
                n = int(self.headers.get("Content-Length") or 0)
                eye.put(self.rfile.read(n))
                return self._send({"ok": True})
            self._send({"error": "no route"}, code=404)
    return H


def shot(out, host="127.0.0.1", port=8752, fresh=1.5, wait=15.0, tls=False,
         after=None):
    """Pull a frame from a running mau5eye.

    `after` is a wall-clock time the frame must postdate.  Freshness
    alone is not enough: the page pushes about once a second, so a frame
    only 0.9 s old can still predate the pattern you just lit.

    Nor is the push time enough on its own.  The browser grabs the
    video frame, JPEG-encodes it and uploads, so a frame *pushed* after
    the change may have been *captured* before it.  We therefore also
    discard the first push that arrives: by the second, the capture
    cannot predate the change.  Without this, blanked frames sail
    through the check and look exactly like dead LEDs.
    """
    base = "%s://%s:%d" % ("https" if tls else "http", host, port)
    ctx = ssl._create_unverified_context() if tls else None
    _open = (lambda u, timeout: urllib.request.urlopen(u, timeout=timeout, context=ctx)) \
        if tls else (lambda u, timeout: urllib.request.urlopen(u, timeout=timeout))
    end = time.time() + wait
    start_n = None
    while time.time() < end:
        try:
            st = json.load(_open(base + "/api/status", 4))
            ok = st.get("have") and st.get("age") is not None
            if ok and after is not None:
                if start_n is None:
                    start_n = st.get("frames", 0)
                ok = ((time.time() - st["age"]) > after
                      and st.get("frames", 0) >= start_n + 2)
            elif ok:
                ok = st["age"] <= fresh
            if ok:
                data = _open(base + "/latest.jpg", 8).read()
                with open(out, "wb") as f:
                    f.write(data)
                return out
        except Exception:
            pass
        time.sleep(0.3)
    raise SystemExit("no fresh frame from mau5eye at %s -- is the page open "
                     "with the camera started?" % base)


def main(argv=None):
    import mau5wled
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter,
                                 epilog=__doc__)
    ap.add_argument("--port", type=int, default=8752)
    ap.add_argument("--tls-port", type=int, default=8753,
                    help="https port as well, for a phone. A browser will not "
                         "give a page the camera over plain http to a LAN "
                         "address -- not a secure context -- but localhost is "
                         "exempt, so the Mac can use the plain port and skip "
                         "the certificate warning entirely")
    ap.add_argument("--no-tls", dest="tls", action="store_false", default=True)
    ap.add_argument("--cert", default=os.path.join(HERE, "data", "cal", "tls", "eye.crt"))
    ap.add_argument("--key", default=os.path.join(HERE, "data", "cal", "tls", "eye.key"))
    ap.add_argument("--out", default=os.path.join(HERE, "data", "cal", "eye.jpg"))
    ap.add_argument("--shot", help="grab one frame from a running server, then exit")
    a = ap.parse_args(argv)

    if a.shot:
        print(shot(a.shot, port=a.port))
        return

    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    eye = Eye(a.out)
    handler = make_handler(eye)
    srv = ThreadingHTTPServer(("0.0.0.0", a.port), handler)
    ip = mau5wled.lan_ip()

    tls_srv = None
    if a.tls and os.path.exists(a.cert) and os.path.exists(a.key):
        tls_srv = ThreadingHTTPServer(("0.0.0.0", a.tls_port), handler)
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ctx.load_cert_chain(a.cert, a.key)
        tls_srv.socket = ctx.wrap_socket(tls_srv.socket, server_side=True)
        threading.Thread(target=tls_srv.serve_forever, daemon=True).start()

    print("  ON THIS MAC:   http://localhost:%d/" % a.port)
    print("                 no warning -- localhost is a secure context. "
          "Click START CAMERA, then Allow.")
    if tls_srv:
        print("  FROM A PHONE:  https://%s:%d/" % (ip, a.tls_port))
        print("                 self-signed, so it warns once: "
              "Advanced -> Proceed, then START CAMERA, Allow.")
    print("  newest frame:  %s" % a.out)
    print("  ctrl-c to stop")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\n  stopped.")


if __name__ == "__main__":
    main()
