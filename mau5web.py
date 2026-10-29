#!/usr/bin/env python3
"""mau5web -- the simulator, as files a static site can serve.

The helmet is one object in one room.  Everything about the software
that is worth showing somebody -- what the effects look like, how
they answer a track, what the power guard does to them over ten
minutes -- can be shown without it, because all of that already runs
in a browser: the engine, the guard, the show player and the audio
analyser were ported for the phone and are checked against the
Python on every commit.

So this assembles them into a page anybody can open.  Same code, same
map, same `power.json`, and the visitor's own music.

    python3 mau5web.py                      # build into data/web
    python3 mau5web.py --serve              # and look at it
    python3 mau5web.py --into ../site       # drop it in the website repo
"""

from __future__ import annotations

import argparse
import json
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
SRC_OFFLINE = os.path.join(HERE, "remote", "offline")
SRC_WEB = os.path.join(HERE, "remote", "web")
OUT = os.path.join(HERE, "data", "web")

# What the simulator needs.  Not wire.js: there is no controller here,
# and not drive.js: the point of the page is the visitor's own track,
# analysed live, rather than ours analysed earlier.
PARTS = ("engine.js", "guard.js", "audio.js", "show.js")
MESH = "helmet.glb"


def write_mesh(path):
    """The CAD backdrop, repacked for a web page.

    The same 57,000 triangles, with 16-bit indices instead of 32 -- the
    mesh has 28,698 vertices, so nothing needs more -- which takes it
    from a megabyte to 0.7 MB without touching the geometry.  The
    simulator draws it so a visitor can see each LED sitting in the
    slot or tube it was mapped to.
    """
    import struct
    import mau5slots
    V, F = mau5slots.load_mesh()
    if len(V) >= 65536:
        raise SystemExit("mesh too large for 16-bit indices")
    pos = V.astype("<f4").tobytes()
    idx = F.astype("<u2").tobytes()
    pad = (-len(idx)) % 4
    blob = idx + b"\0" * pad + pos
    doc = {
        "asset": {"version": "2.0", "generator": "mau5web.py"},
        "scene": 0, "scenes": [{"nodes": [0]}],
        "nodes": [{"mesh": 0, "name": "mau5head"}],
        "meshes": [{"primitives": [{"attributes": {"POSITION": 1}, "indices": 0}]}],
        "buffers": [{"byteLength": len(blob)}],
        "bufferViews": [
            {"buffer": 0, "byteOffset": 0, "byteLength": len(idx), "target": 34963},
            {"buffer": 0, "byteOffset": len(idx) + pad, "byteLength": len(pos),
             "target": 34962}],
        "accessors": [
            {"bufferView": 0, "componentType": 5123, "count": int(F.size), "type": "SCALAR"},
            {"bufferView": 1, "componentType": 5126, "count": len(V), "type": "VEC3",
             "min": V.min(0).astype(float).tolist(), "max": V.max(0).astype(float).tolist()}],
    }
    js = json.dumps(doc, separators=(",", ":")).encode()
    js += b" " * ((-len(js)) % 4)
    with open(path, "wb") as f:
        f.write(struct.pack("<III", 0x46546C67, 2, 12 + 8 + len(js) + 8 + len(blob)))
        f.write(struct.pack("<II", len(js), 0x4E4F534A) + js)
        f.write(struct.pack("<II", len(blob), 0x004E4942) + blob)
    return os.path.getsize(path)


def bundle():
    """The same export the phone gets, minus what only a wire needs."""
    import mau5offline
    d = mau5offline.bundle()
    for k in ("strips", "standby", "drive"):
        d.pop(k, None)
    return d


def build(out=OUT, verbose=True):
    os.makedirs(os.path.join(out, "mau5"), exist_ok=True)
    data = bundle()
    js = "globalThis.MAU5_DATA = %s;\n" % json.dumps(data, separators=(",", ":"))
    with open(os.path.join(out, "mau5", "data.js"), "w") as f:
        f.write(js)
    total = len(js)
    for p in PARTS:
        src = os.path.join(SRC_OFFLINE, p)
        shutil.copyfile(src, os.path.join(out, "mau5", p))
        total += os.path.getsize(src)
    total += write_mesh(os.path.join(out, "mau5", MESH))
    shutil.copyfile(os.path.join(SRC_WEB, "simulator.js"),
                    os.path.join(out, "mau5-simulator.js"))
    shutil.copyfile(os.path.join(SRC_WEB, "simulator.html"),
                    os.path.join(out, "mau5-simulator.html"))
    # The page is styled by the website's own stylesheet.  Served from
    # here there is no website, so stand in for it with the live one;
    # --into never copies this, because the site has the real thing.
    with open(os.path.join(out, "site.css"), "w") as f:
        f.write('@import url("https://vortex1.dev/site.css");\n')
    total += os.path.getsize(os.path.join(SRC_WEB, "simulator.js"))
    if verbose:
        print("  %s" % out)
        print("    mau5/data.js          %7.1f kB  (%d presets, %d shows, %d LEDs)"
              % (len(js) / 1024.0, len(data["presets"]), len(data.get("shows", {})),
                 data["n"]))
        for p in PARTS:
            print("    mau5/%-16s %7.1f kB"
                  % (p, os.path.getsize(os.path.join(SRC_OFFLINE, p)) / 1024.0))
        print("    mau5/%-16s %7.1f kB  (the CAD, for the helmet around the LEDs)"
              % (MESH, os.path.getsize(os.path.join(out, "mau5", MESH)) / 1024.0))
        print("    mau5-simulator.js     %7.1f kB"
              % (os.path.getsize(os.path.join(SRC_WEB, "simulator.js")) / 1024.0))
        print("    mau5-simulator.html   %7.1f kB"
              % (os.path.getsize(os.path.join(SRC_WEB, "simulator.html")) / 1024.0))
        print("    %.0f kB in all, before the server gzips it" % (total / 1024.0))
    return out


def serve(port=8790):
    import http.server
    import socketserver
    build()
    os.chdir(OUT)

    class H(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a):
            pass

    socketserver.TCPServer.allow_reuse_address = True
    srv = socketserver.TCPServer(("127.0.0.1", port), H)
    print("\n  http://127.0.0.1:%d/mau5-simulator.html" % port)
    print("  ctrl-c to stop")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--serve", action="store_true")
    ap.add_argument("--port", type=int, default=8790)
    ap.add_argument("--into", default=None,
                    help="a checkout of the website to copy the built files into")
    a = ap.parse_args(argv)
    if a.serve:
        return serve(a.port)
    build()
    if a.into:
        dest = os.path.abspath(a.into)
        if not os.path.isdir(dest):
            raise SystemExit("no such directory: %s" % dest)
        os.makedirs(os.path.join(dest, "mau5"), exist_ok=True)
        for rel in ["mau5-simulator.html", "mau5-simulator.js"] + \
                   [os.path.join("mau5", p) for p in ("data.js", MESH) + PARTS]:
            shutil.copyfile(os.path.join(OUT, rel), os.path.join(dest, rel))
        print("\n  copied into %s" % dest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
