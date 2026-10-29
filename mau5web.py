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
    shutil.copyfile(os.path.join(SRC_WEB, "simulator.js"),
                    os.path.join(out, "mau5-simulator.js"))
    shutil.copyfile(os.path.join(SRC_WEB, "simulator.html"),
                    os.path.join(out, "mau5-simulator.html"))
    total += os.path.getsize(os.path.join(SRC_WEB, "simulator.js"))
    if verbose:
        print("  %s" % out)
        print("    mau5/data.js          %7.1f kB  (%d presets, %d shows, %d LEDs)"
              % (len(js) / 1024.0, len(data["presets"]), len(data.get("shows", {})),
                 data["n"]))
        for p in PARTS:
            print("    mau5/%-16s %7.1f kB"
                  % (p, os.path.getsize(os.path.join(SRC_OFFLINE, p)) / 1024.0))
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
                   [os.path.join("mau5", p) for p in ("data.js",) + PARTS]:
            shutil.copyfile(os.path.join(OUT, rel), os.path.join(dest, rel))
        print("\n  copied into %s" % dest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
