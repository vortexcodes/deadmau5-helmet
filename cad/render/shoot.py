import sys, os, subprocess, time
from playwright.sync_api import sync_playwright
mode = sys.argv[1]            # "stills" or "video"
srv = subprocess.Popen([sys.executable, "-m", "http.server", "8765"], cwd=os.path.dirname(os.path.abspath(__file__)), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(1.0)
SCENES = {"turntable": 10.0, "exploded": 13.0, "visor": 8.0, "wallmount": 9.0}
try:
    with sync_playwright() as p:
        b = p.chromium.launch(args=["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"])
        pg = b.new_page(viewport={"width": 1280, "height": 720})
        pg.on("console", lambda m: print("console:", m.text) if m.type in ("error", "warning") else None)
        pg.goto("http://localhost:8765/index.html")
        pg.wait_for_function("window.__ready === true", timeout=180000)
        if mode == "stills":
            os.makedirs("stills", exist_ok=True)
            for sc, ts in [(s.split(":")[0], [float(x) for x in s.split(":")[1].split(",")]) for s in sys.argv[2:]]:
                for t in ts:
                    t0 = time.time(); pg.evaluate(f"renderFrame('{sc}', {t})")
                    pg.screenshot(path=f"stills/{sc}_{t:05.2f}.jpg", type="jpeg", quality=92)
                    print(sc, t, f"{time.time()-t0:.2f}s")
        else:
            for sc in sys.argv[2:]:
                dur = SCENES[sc]; n = int(round(dur * 30)); d = f"frames_{sc}"; os.makedirs(d, exist_ok=True)
                t0 = time.time()
                for i in range(n):
                    pg.evaluate(f"renderFrame('{sc}', {i/30.0})")
                    pg.screenshot(path=f"{d}/{i:05d}.jpg", type="jpeg", quality=92)
                print(sc, n, "frames", f"{time.time()-t0:.0f}s")
        b.close()
finally:
    srv.terminate()
