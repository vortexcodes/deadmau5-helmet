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
import tempfile
import subprocess
import re
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
  <div class="note" id="note">Leave this page open and the camera pointed at the
    helmet. Keep the screen from sleeping.</div>
</div>
<script>
// A browser only hands over a camera on a secure page, and makes the
// point by deleting navigator.mediaDevices rather than refusing the
// call -- so from any machine that is not this one, the plain http
// page fails with "undefined is not an object" and no hint at all.
// localhost is the one exception, which is why it works here and
// nowhere else.  Say so, and offer the link that does work.
const SECURE = window.isSecureContext && navigator.mediaDevices;
let stream=null, timer=null, n=0, fails=0, busy=false;
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

// One upload at a time.  On a phone, encoding and sending a 1080p frame
// can take longer than the 400 ms tick, and overlapping uploads can land
// out of order: an older capture arriving last becomes the newest frame,
// and shot() hands back the previous LED.  A tick that finds one still
// in flight is skipped, and a send that hangs is abandoned after 5 s so
// it cannot stop the camera for good.
async function push(){
  if(!v.videoWidth || busy) return;
  busy=true;
  const ac=new AbortController(), give=setTimeout(()=>ac.abort(), 5000);
  try{
    cv.width=v.videoWidth; cv.height=v.videoHeight;
    cv.getContext('2d').drawImage(v,0,0);
    const b=await new Promise(r=>cv.toBlob(r,'image/jpeg',0.86));
    if(!b) return;
    await fetch('/frame',{method:'POST',headers:{'Content-Type':'image/jpeg'},
                          body:b,signal:ac.signal});
    n++; fails=0; d.className='dot on';
    s.textContent=n+' frames · '+cv.width+'×'+cv.height;
  }catch(e){ fails++; if(fails>2) d.className='dot err'; }
  finally{ clearTimeout(give); busy=false; }
}

if(!SECURE){
  const tls = 'https://' + location.hostname + ':' + __TLSPORT__ + '/';
  const go = document.getElementById('go');
  go.disabled = true;
  go.textContent = 'NEEDS A SECURE PAGE';
  d.className = 'dot err';
  s.textContent = 'not a secure context';
  document.getElementById('note').innerHTML =
    'This page is plain http, so the browser deletes the camera API '
    + 'outright rather than asking you. Only localhost is exempt, which '
    + 'is why it works on the laptop running this and nowhere else. Open '
    + '<a href="' + tls + '" style="color:#38d39f">' + tls + '</a> and '
    + 'accept the warning once &mdash; the certificate is self-signed by '
    + 'the same laptop.';
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
        # Two uploads at once (two pages open, or an old page still
        # running) used to share one ".tmp" path: the file could end up
        # half of each, or the second os.replace found nothing to move
        # and that request failed.  Each write now has its own temporary
        # file, and the frame in memory and the one on disk are swapped
        # together, so they cannot disagree about which is newest.
        d = os.path.dirname(os.path.abspath(self.path))
        with self.lock:
            self.frame, self.at, self.n = data, time.time(), self.n + 1
            fd, tmp = tempfile.mkstemp(dir=d, prefix=".eye-", suffix=".tmp")
            try:
                with os.fdopen(fd, "wb") as f:
                    f.write(data)
                os.replace(tmp, self.path)
            except BaseException:
                try:
                    os.unlink(tmp)
                except OSError:
                    pass
                raise

    def get(self):
        with self.lock:
            return self.frame, self.at, self.n


def make_handler(eye, tls_port=8753):
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
                page = PAGE.replace("__TLSPORT__", str(tls_port))
                return self._send(page.encode("utf-8"), "text/html; charset=utf-8")
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


def _opener(tls):
    ctx = ssl._create_unverified_context() if tls else None
    return (lambda u, timeout: urllib.request.urlopen(u, timeout=timeout, context=ctx)) \
        if tls else (lambda u, timeout: urllib.request.urlopen(u, timeout=timeout))


def shot(out, host="127.0.0.1", port=8752, fresh=1.5, wait=15.0, tls=False,
         after=None, lag=0.0):
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

    Nor is the second push enough with a slow camera.  The page draws
    the <video> element as it is, and with the phone camera that
    picture is already 1.1-1.5 s old: measured 2026-10-30, a frame
    pushed 1.08-1.54 s after a change was the first to show it.  `lag`
    is that delay, margin included -- measure_lag() finds it -- and
    with it the frame must be pushed after `after + lag`.  0 keeps the
    old rule, which is only right for a camera with no lag of its own.
    """
    base = "%s://%s:%d" % ("https" if tls else "http", host, port)
    _open = _opener(tls)
    end = time.time() + wait
    start_n = None
    while time.time() < end:
        try:
            st = json.load(_open(base + "/api/status", 4))
            ok = st.get("have") and st.get("age") is not None
            if ok and after is not None:
                if start_n is None:
                    start_n = st.get("frames", 0)
                ok = ((time.time() - st["age"]) > after + lag
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


# Added to the worst delay measure_lag() sees.  The worst measured on
# the phone was 1.54 s, and waiting 1.8 s gave frames that all showed
# the LED just lit; the margin covers encode and upload times varying.
LAG_MARGIN = 0.3
# How long a blank is left before a frame of it is taken as the dark
# reference, before the lag is known: twice the phone's worst.
LAG_FIRST_GUESS = 3.0


class LagError(RuntimeError):
    """The pattern never showed in the camera, so no lag was measured."""


def _newest(base, _open):
    """The newest frame, its push time and its number -- all one frame.

    Status, the frame, then status again: if another push landed in
    between, the picture may be newer than the time, so go round again.
    """
    for _ in range(5):
        st = json.load(_open(base + "/api/status", 4))
        if not st.get("have") or st.get("age") is None:
            return None
        at = time.time() - st["age"]
        data = _open(base + "/latest.jpg", 8).read()
        if json.load(_open(base + "/api/status", 4)).get("frames") == st.get("frames"):
            return data, at, st.get("frames", 0)
    return None


def measure_lag(light, blank, host="127.0.0.1", port=8752, trials=3, wait=8.0,
                margin=LAG_MARGIN, floor=40.0, tls=False, poll=0.05,
                first_guess=LAG_FIRST_GUESS):
    """How long after a change the camera first shows it, worst of several.

    light() and blank() put a pattern on the helmet and take it off.
    Against a frame of the blank, a frame shows the pattern when its
    brightest difference reaches `floor` over at least four pixels (the
    rule mau5locate's centroid uses), and a change counts from the first
    frame that shows the new state *and is followed by one that does*,
    so a single noisy frame cannot pass for it.  It is timed both ways,
    on and off, `trials` times each.  Each delay is the camera's own lag
    plus up to one push interval, depending on where in the interval
    the change fell, so the worst of them covers the interval too.

    Returns (the lag to give shot(), the delays measured).  Raises
    LagError if the pattern never shows: out of view, or no camera.
    """
    import io
    import numpy as np
    from PIL import Image
    base = "%s://%s:%d" % ("https" if tls else "http", host, port)
    _open = _opener(tls)

    def newest():
        try:
            return _newest(base, _open)
        except Exception:
            return None

    def gray(data):
        return np.asarray(Image.open(io.BytesIO(data)).convert("L")).astype(np.float32)

    def shows(data, ref):
        g = gray(data)
        if g.shape != ref.shape:
            raise LagError("the camera changed resolution while being timed")
        d = np.clip(g - ref, 0, 255)
        pk = float(d.max())
        return pk >= floor and int((d > pk * 0.5).sum()) >= 4

    def first(t, state, ref):
        """Push time of the first frame after t that shows `state`, and
        whose next frame does too."""
        end = time.time() + wait
        seen = cand = None
        while time.time() < end:
            got = newest()
            if got and got[2] != seen:
                data, at, seen = got
                if at > t:
                    if shows(data, ref) == state:
                        if cand is not None:
                            return cand
                        cand = at
                    else:
                        cand = None
            time.sleep(poll)
        raise LagError("the pattern never %s within %.0f s"
                       % ("showed" if state else "went", wait))

    delays = []
    try:
        t = time.time(); blank()
        got, end = None, time.time() + first_guess + wait
        while time.time() < end:
            got = newest()
            if got and got[1] > t + first_guess:
                break
            got = None
            time.sleep(poll)
        if got is None:
            raise LagError("no fresh frame from mau5eye at %s -- is the page "
                           "open with the camera started?" % base)
        ref = gray(got[0])
        for _ in range(trials):
            t = time.time(); light()
            delays.append(first(t, True, ref) - t)
            t = time.time(); blank()
            delays.append(first(t, False, ref) - t)
    finally:
        blank()
    return max(delays) + margin, delays


def cert_ips(crt):
    """The addresses an existing certificate actually covers."""
    try:
        out = subprocess.run(["openssl", "x509", "-in", crt, "-noout", "-text"],
                             capture_output=True, text=True, timeout=10).stdout
    except Exception:
        return set()
    ips = set()
    for part in re.findall(r"IP Address:([0-9a-fA-F:.]+)", out):
        ips.add(part)
    return ips


def ensure_cert(crt, key, ips, days=365):
    """Make sure the certificate covers the address the phone will type.

    A self-signed certificate is the right tool here -- the page needs
    a secure context so getUserMedia will run, and nothing about the
    traffic is secret -- but the address still has to match.  A browser
    given an IP URL has no hostname to fall back on, so a SAN listing
    yesterday's DHCP lease is not a warning anybody can click through;
    it is a flat refusal, and it looks exactly like the server being
    down.  The lease moves, so check on every start.
    """
    want = set(ips) | {"127.0.0.1"}
    if os.path.exists(crt) and os.path.exists(key) and want <= cert_ips(crt):
        return False
    os.makedirs(os.path.dirname(crt) or ".", exist_ok=True)
    san = ",".join(["IP:" + i for i in sorted(want)] + ["DNS:localhost"])
    cfg = ("[req]\ndistinguished_name=dn\nx509_extensions=v3\nprompt=no\n"
           "[dn]\nCN=mau5eye\n[v3]\nsubjectAltName=" + san +
           "\nbasicConstraints=CA:FALSE\n")
    with tempfile.NamedTemporaryFile("w", suffix=".cnf", delete=False) as f:
        f.write(cfg)
        path = f.name
    try:
        # a config file rather than -addext: LibreSSL, which is what
        # macOS ships as openssl, does not take -addext
        subprocess.run(["openssl", "req", "-x509", "-newkey", "rsa:2048",
                        "-nodes", "-keyout", key, "-out", crt,
                        "-days", str(days), "-config", path],
                       check=True, capture_output=True, timeout=60)
    finally:
        os.unlink(path)
    return True


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
    handler = make_handler(eye, a.tls_port)
    srv = ThreadingHTTPServer(("0.0.0.0", a.port), handler)
    ip = mau5wled.lan_ip()

    if a.tls:
        try:
            if ensure_cert(a.cert, a.key, [ip] if ip else []):
                print("  certificate regenerated for %s" % ip)
        except Exception as e:
            print("  could not make a certificate (%s); https disabled" % e)

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
