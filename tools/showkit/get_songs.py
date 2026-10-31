#!/usr/bin/env python3
"""get_songs.py [http://server:8799] [--dest shows] -- fetch the show songs from the machine running
`mau5offline.py songs`, on the same network, into shows/ for the tools. Run from the repo root. Skips
what is already here at the right size. The MP3s are ignored by git: never commit them or host them."""
import argparse, json, os, urllib.request
ap = argparse.ArgumentParser(description=__doc__)
ap.add_argument("server", nargs="?", default="http://192.168.10.225:8799")
ap.add_argument("--dest", default="shows")
a = ap.parse_args()
base = a.server.rstrip("/")
songs = json.load(urllib.request.urlopen(base + "/songs.json", timeout=10))["songs"]
os.makedirs(a.dest, exist_ok=True)
for name, s in sorted(songs.items()):
    path = os.path.join(a.dest, s["track"])
    if os.path.exists(path) and os.path.getsize(path) == s["bytes"]:
        print("have", s["track"])
        continue
    got = 0
    with urllib.request.urlopen(base + s["path"], timeout=30) as r, open(path + ".part", "wb") as f:
        while True:
            b = r.read(1 << 16)
            if not b:
                break
            f.write(b)
            got += len(b)
    if got != s["bytes"]:
        raise SystemExit("only %d of %d bytes of %s arrived" % (got, s["bytes"], s["track"]))
    os.replace(path + ".part", path)
    print("got ", s["track"], got // 1000000, "MB")
print(len(songs), "songs in", a.dest)
