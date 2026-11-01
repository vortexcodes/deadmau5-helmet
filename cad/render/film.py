#!/usr/bin/env python3
"""film.py -- render the CAD walkthrough: drives walkthrough.html in Chrome and collects the frames.

    python3 film.py stills OUT_DIR t1,t2,...          # single frames, times in seconds
    python3 film.py check                             # every frame's labels, no pixels: overlaps, crossings, off screen
    python3 film.py video FRAMES_DIR [from_s to_s]    # all frames, or a span, as PNGs
    python3 film.py info                              # chapter start times and caption reading speed

BUILD (env MAU5_CAD_BUILD, default ./build) holds mesh/, scene.json and node_modules/three.
WebGL runs on the real GPU through ANGLE and Metal, with the Chrome installed on this Mac.
"""
import http.server
import json
import os
import shutil
import socketserver
import sys
import threading
import time
from urllib.parse import unquote

from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
BUILD = os.environ.get("MAU5_CAD_BUILD", os.path.join(HERE, "build"))
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
FPS = 30
PORT = 8791
FRAME_DIR = [HERE]


class Handler(http.server.SimpleHTTPRequestHandler):
    def translate_path(self, path):
        p = unquote(path.split("?")[0]).lstrip("/")
        if p.startswith("build/"):
            return os.path.join(BUILD, p[len("build/"):])
        return os.path.join(HERE, p)

    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0))
        data = self.rfile.read(n)
        name = os.path.basename(self.path)
        with open(os.path.join(FRAME_DIR[0], name), "wb") as fh:
            fh.write(data)
        self.send_response(204); self.end_headers()

    def log_message(self, *a):
        pass


class Server(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True
    allow_reuse_address = True


def session(fn):
    srv = Server(("127.0.0.1", PORT), Handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    try:
        with sync_playwright() as p:
            b = p.chromium.launch(executable_path=CHROME, headless=True,
                                  args=["--use-angle=metal", "--enable-gpu", "--ignore-gpu-blocklist"])
            pg = b.new_page(viewport={"width": 1920, "height": 1080})
            pg.on("console", lambda m: print("console:", m.text) if m.type in ("error",) else None)
            pg.on("pageerror", lambda e: print("pageerror:", e))
            pg.goto(f"http://127.0.0.1:{PORT}/walkthrough.html")
            pg.wait_for_function("window.__ready === true", timeout=300000)
            fn(pg)
            b.close()
    finally:
        srv.shutdown()


def main():
    mode = sys.argv[1]
    if mode == "stills":
        out = sys.argv[2]; os.makedirs(out, exist_ok=True); FRAME_DIR[0] = out
        ts = [float(x) for x in sys.argv[3].split(",")]

        def go(pg):
            print("gpu:", pg.evaluate("""()=>{const g=document.getElementById('gl').getContext('webgl2');const e=g.getExtension('WEBGL_debug_renderer_info');return g.getParameter(e.UNMASKED_RENDERER_WEBGL)}"""))
            print("duration", pg.evaluate("window.__duration"), "windows matched to the LED map:", pg.evaluate("window.__windowsMatched"))
            for t in ts:
                t0 = time.time()
                pg.evaluate(f"(async()=>{{renderAt({t}); await saveFrame('s_{t:07.2f}.png');}})()")
                print(f"{t:7.2f}  {time.time()-t0:.2f}s", flush=True)
            pr = pg.evaluate("window.__problems")
            for p in pr[:60]:
                print("problem:", p)
        session(go)
    elif mode == "verify":     # assembled, from every side and in section
        out = sys.argv[2]; os.makedirs(out, exist_ok=True); FRAME_DIR[0] = out
        views = [("front", 0, 0, 1900, 0, 0, 120, None), ("side", -90, 0, 1900, 0, 0, 120, None), ("back", 180, 8, 1900, 0, 0, 120, None),
                 ("top", 0, 89, 1900, 0, 0, 0, None), ("under", 0, -80, 1200, 0, 0, 0, None),
                 ("cut_x0", -90, 0, 1300, 0, 0, 20, [1, 0, 0, 0]), ("cut_y0", 180, 0, 1300, 0, 0, 20, [0, 1, 0, 0]), ("cut_z0", 0, 89, 1300, 0, 0, 0, [0, 0, -1, 0])]

        def go(pg):
            for v in views:
                n, az, el, d, x, y, z, sec = v
                pg.evaluate(f"debugView('{n}.png',{az},{el},{d},{x},{y},{z},{json.dumps(sec)})")
        session(go)
    elif mode == "check":
        def go(pg):
            dur = pg.evaluate("window.__duration")
            bad = pg.evaluate(f"""()=>{{window.__problems.length=0; const n=Math.round({dur}*{FPS}); for(let i=0;i<n;i++) renderLayout(i/{FPS}); return window.__problems}}""")
            print(f"{int(dur*FPS)} frames checked, {len(bad)} problems")
            seen = {}
            for p in bad:
                k = tuple(p[1:]); seen.setdefault(k, [p[0], p[0]]); seen[k][1] = p[0]
            for k, (a, b) in sorted(seen.items(), key=lambda kv: kv[1][0]):
                print(f"  {a:7.2f}-{b:7.2f}  {k}")
        session(go)
    elif mode == "info":
        def go(pg):
            for c in pg.evaluate("window.chapters()"):
                print(f"{c['start']:6.1f}  {c['dur']:5.1f}  {c['id']}")
                for a, b, s in c["caps"]:
                    print(f"        {c['start']+a:6.1f} {b-a:4.1f}s {len(s)/(b-a):5.1f} c/s  {s}")
        session(go)
    elif mode == "video":
        out = sys.argv[2]; os.makedirs(out, exist_ok=True); FRAME_DIR[0] = out
        span = [float(x) for x in sys.argv[3:5]] if len(sys.argv) > 4 else None

        def go(pg):
            dur = pg.evaluate("window.__duration")
            a, b = (0, int(round(dur * FPS))) if not span else (int(span[0] * FPS), int(span[1] * FPS))
            t0 = time.time()
            for i in range(a, b, 15):
                j = min(b, i + 15)
                pg.evaluate(f"""async()=>{{ for(let i={i};i<{j};i++){{ renderAt(i/{FPS}); await saveFrame(String(i).padStart(5,'0')+'.png'); }} }}""")
                el = time.time() - t0; done = j - a
                print(f"{done}/{b-a} frames  {el/done:.2f} s/frame  eta {(b-a-done)*el/done/60:.0f} min", flush=True)
        session(go)


if __name__ == "__main__":
    main()
