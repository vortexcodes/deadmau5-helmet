#!/usr/bin/env python3
"""mau5build -- turn a show into the three files FPP wants, then put them there.

    ./mau5build.py build  --name intro --audio intro.mp3 --effect myfx.py:show
    ./mau5build.py build  --name intro --audio intro.mp3 --fseq from_xlights.fseq
    ./mau5build.py check  shows/intro.fseq
    ./mau5build.py upload --name intro
    ./mau5build.py deploy --name intro --audio intro.mp3 --effect myfx.py:show
    ./mau5build.py status | playlists | start intro | stop | volume 70

``build`` writes ``shows/<name>.fseq``, copies the audio next to it, and writes
``shows/<name>.json`` -- the FPP playlist.  ``upload`` pushes all three to the
Pi and creates the playlist, so the FPP web UI never has to be opened.

Nothing uploads if the sequence does not match the helmet.  A show built for
the wrong LED count is the failure mode that costs you a set, so the check is
not optional -- ``--force`` exists but says loudly what it is overriding.
"""

from __future__ import annotations

import argparse
import json
import mimetypes
import os
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import wave

import mau5cfg
import mau5fseq

TIMEOUT = 20


# --------------------------------------------------------------------------
# FPP REST client
# --------------------------------------------------------------------------

_SUPERSEDED = """
  ------------------------------------------------------------------
  mau5build packages shows for FPP on a Raspberry Pi, against the
  helmet as it was CAD'd: a full sphere of 1185 pixels on two chains.

  The helmet that exists is 622 WS2815 on ONE chain: 398 on the front
  shell, 224 across the two ears, straight into WLED over DDP.
  Nothing on the current path reads this file.

  Use instead:
      data/cal/pixel_map.csv   the real geometry   (mau5map.py)
      data/cal/power.json      the thermal limits  (mau5power.py)
      mau5engine.py            presets
      mau5preview.py           the simulator
      mau5ctl.py               the controller
      mau5doctor.py            check everything at once
  ------------------------------------------------------------------
"""


def _warn_superseded():
    import sys
    print(_SUPERSEDED, file=sys.stderr)


class FPP:
    """Falcon Player's HTTP API.

    FPP has moved its file-upload endpoint around between releases, so the
    upload path is a list of candidates tried in order and the one that works
    is reported.  Pin it in helmet.toml under [player] upload_paths if your
    build only speaks one of them.
    """

    UPLOAD_CANDIDATES = [
        ("POST", "/api/file/{dir}", "myfile"),
        ("POST", "/api/file/upload/{dir}", "myfile"),
        ("POST", "/jqupload.php?path={dir}", "myfile"),
    ]

    def __init__(self, host, timeout=TIMEOUT, dry_run=False, upload_paths=None):
        host = host if "://" in host else "http://" + host
        self.base = host.rstrip("/")
        self.timeout = timeout
        self.dry_run = dry_run
        self.upload_paths = upload_paths
        self._upload_ok = None

    # -- transport --------------------------------------------------------
    def _open(self, req):
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as r:
                body = r.read()
                return r.status, body
        except urllib.error.HTTPError as e:
            return e.code, e.read()
        except urllib.error.URLError as e:
            raise SystemExit("cannot reach %s: %s\n"
                             "  is the phone/laptop on the Pi's hotspot?"
                             % (self.base, e.reason))

    def get(self, path, parse=True):
        st, body = self._open(urllib.request.Request(self.base + path))
        if parse:
            try:
                return json.loads(body or b"null")
            except ValueError:
                return body.decode("utf-8", "replace")
        return st, body

    def post_json(self, path, obj):
        if self.dry_run:
            print("  [dry-run] POST %s%s  (%d bytes)"
                  % (self.base, path, len(json.dumps(obj))))
            return {"dry_run": True}
        data = json.dumps(obj).encode()
        req = urllib.request.Request(self.base + path, data=data, method="POST",
                                     headers={"Content-Type": "application/json"})
        st, body = self._open(req)
        if st >= 400:
            raise SystemExit("POST %s failed (%d): %s"
                             % (path, st, body[:300].decode("utf-8", "replace")))
        try:
            return json.loads(body or b"null")
        except ValueError:
            return body.decode("utf-8", "replace")

    # -- files ------------------------------------------------------------
    def upload(self, path, directory):
        """Upload one file into an FPP media directory (sequences / music)."""
        name = os.path.basename(path)
        size = os.path.getsize(path)
        if self.dry_run:
            print("  [dry-run] upload %s -> %s/ (%.2f MB)"
                  % (name, directory, size / 1e6))
            return True
        with open(path, "rb") as fh:
            payload = fh.read()
        candidates = ([(m, p, f) for m, p, f in self.UPLOAD_CANDIDATES]
                      if not self.upload_paths else
                      [("POST", p, "myfile") for p in self.upload_paths])
        if self._upload_ok:
            candidates = [self._upload_ok] + [c for c in candidates
                                              if c != self._upload_ok]
        errors = []
        for method, tmpl, field in candidates:
            url = self.base + tmpl.format(dir=directory)
            body, ctype = _multipart({field: (name, payload)})
            req = urllib.request.Request(url, data=body, method=method,
                                         headers={"Content-Type": ctype,
                                                  "X-Filename": name})
            st, resp = self._open(req)
            if st < 400:
                self._upload_ok = (method, tmpl, field)
                print("  uploaded %-28s %7.2f MB via %s" % (name, size / 1e6, tmpl))
                return True
            errors.append("%s -> %d" % (tmpl, st))
        raise SystemExit(
            "upload of %s failed on every known endpoint (%s).\n"
            "  Your FPP build uses a different path. Either set\n"
            "      [player] upload_paths = [\"/your/path/{dir}\"]\n"
            "  in helmet.toml, or copy the files yourself:\n"
            "      scp %s fpp@%s:/home/fpp/media/%s/"
            % (name, ", ".join(errors), path,
               urllib.parse.urlparse(self.base).hostname, directory))

    # -- playlists --------------------------------------------------------
    def playlists(self):
        r = self.get("/api/playlists")
        return r if isinstance(r, list) else []

    def save_playlist(self, name, obj):
        return self.post_json("/api/playlist/%s" % urllib.parse.quote(name), obj)

    def start(self, name, repeat=False):
        return self.get("/api/playlist/%s/start%s"
                        % (urllib.parse.quote(name), "?repeat=1" if repeat else ""))

    def stop(self, graceful=False):
        return self.get("/api/playlists/stop" + ("gracefully" if graceful else ""))

    def status(self):
        r = self.get("/api/system/status")
        if isinstance(r, dict) and r:
            return r
        return self.get("/api/fppd/status")

    def volume(self, level=None):
        if level is None:
            r = self.get("/api/system/volume")
            return r.get("volume") if isinstance(r, dict) else r
        return self.post_json("/api/system/volume", {"volume": int(level)})


def _multipart(fields):
    boundary = "----mau5build%d" % int(time.time() * 1000)
    out = []
    for key, val in fields.items():
        name, payload = val
        ctype = mimetypes.guess_type(name)[0] or "application/octet-stream"
        out.append(("--%s\r\nContent-Disposition: form-data; name=\"%s\"; "
                    "filename=\"%s\"\r\nContent-Type: %s\r\n\r\n"
                    % (boundary, key, name, ctype)).encode())
        out.append(payload)
        out.append(b"\r\n")
    out.append(("--%s--\r\n" % boundary).encode())
    return b"".join(out), "multipart/form-data; boundary=%s" % boundary


# --------------------------------------------------------------------------
# audio
# --------------------------------------------------------------------------
def audio_duration(path):
    """Seconds, or None if we cannot tell without pulling in a codec library."""
    if path.lower().endswith(".wav"):
        try:
            with wave.open(path, "rb") as w:
                return w.getnframes() / float(w.getframerate())
        except Exception:
            return None
    af = shutil.which("afinfo")
    if af:
        try:
            out = subprocess.run([af, path], capture_output=True, text=True,
                                 timeout=20).stdout
            for line in out.splitlines():
                if "estimated duration" in line:
                    return float(line.split(":")[1].strip().split()[0])
        except Exception:
            pass
    ff = shutil.which("ffprobe")
    if ff:
        try:
            out = subprocess.run([ff, "-v", "quiet", "-show_entries",
                                  "format=duration", "-of",
                                  "default=nw=1:nk=1", path],
                                 capture_output=True, text=True, timeout=20)
            return float(out.stdout.strip())
        except Exception:
            return None
    return None


# --------------------------------------------------------------------------
# verification
# --------------------------------------------------------------------------
def verify(helmet, fseq_path, audio=None, strict=True):
    """Return a list of problems.  Empty list means it is safe to upload."""
    problems, notes = [], []
    with mau5fseq.FseqReader(fseq_path) as s:
        print(s.describe())
        want = helmet.channel_count
        if s.channel_count != want:
            problems.append(
                "channel count is %d, the helmet needs %d (%d LEDs x 3).\n"
                "    xLights models add up to a different total -- check the "
                "controller\n    layout, or rebuild with mau5build."
                % (s.channel_count, want, helmet.n_total))
        step = int(round(1000.0 / helmet.fps))
        if s.step_time_ms != step:
            problems.append("step time is %d ms (%.4g fps); helmet.toml says "
                            "%d ms (%d fps)"
                            % (s.step_time_ms, s.fps, step, helmet.fps))
        if s.frame_count == 0:
            problems.append("no frames")
        if s.compression == mau5fseq.COMP_ZSTD and mau5fseq._zstd() is None:
            notes.append("zstd compressed -- FPP reads it, but this machine "
                         "cannot preview it without `pip install zstandard`")
        seq_len = s.duration_s

    if audio:
        if not os.path.exists(audio):
            problems.append("audio file %s does not exist" % audio)
        else:
            d = audio_duration(audio)
            if d is None:
                notes.append("could not measure the audio length "
                             "(no ffprobe, not a wav) -- lengths unchecked")
            elif abs(d - seq_len) > 1.0:
                msg = ("audio is %.1f s, sequence is %.1f s (%.1f s apart)"
                       % (d, seq_len, abs(d - seq_len)))
                (problems if abs(d - seq_len) > 5.0 else notes).append(msg)

    for n in notes:
        print("  note: %s" % n)
    for p in problems:
        print("  PROBLEM: %s" % p, file=sys.stderr)
    return problems if strict else []


# --------------------------------------------------------------------------
# build
# --------------------------------------------------------------------------
def playlist_json(name, fseq_name, media_name, duration):
    """FPP playlist format (version 3), one 'both' entry."""
    entry = {
        "type": "both",
        "enabled": 1,
        "playOnce": 0,
        "sequenceName": fseq_name,
        "mediaName": media_name or "",
        "videoOut": "--Default--",
        "duration": round(duration, 3),
    }
    if not media_name:
        entry["type"] = "sequence"
        entry.pop("mediaName")
        entry.pop("videoOut")
    return {
        "name": name,
        "version": 3,
        "repeat": 0,
        "loopCount": 0,
        "empty": False,
        "desc": "built by mau5build",
        "random": 0,
        "leadIn": [],
        "mainPlaylist": [entry],
        "leadOut": [],
        "playlistInfo": {"total_duration": round(duration, 3), "total_items": 1},
    }


def build(helmet, name, audio=None, effect=None, fseq=None, seconds=None,
          compression="none", out_dir=None, timeline=None):
    base = os.path.dirname(os.path.abspath(helmet.path))
    out_dir = out_dir or os.path.join(base, helmet.cfg["show"].get("shows_dir", "shows"))
    os.makedirs(out_dir, exist_ok=True)
    fseq_out = os.path.join(out_dir, name + ".fseq")

    if fseq:
        if os.path.abspath(fseq) != os.path.abspath(fseq_out):
            shutil.copy2(fseq, fseq_out)
            print("copied %s -> %s" % (fseq, fseq_out))
    else:
        if timeline is not None:
            source = timeline
            dur = seconds or audio_duration(audio or "") or 30.0
        elif effect:
            import mau5sim
            dur = seconds or audio_duration(audio or "") or 30.0
            source = mau5sim.load_effect(effect, helmet, dur, helmet.fps)
        else:
            raise SystemExit("build needs either --fseq or --effect")
        n = source.n_frames or int(dur * helmet.fps)
        print("rendering %d frames (%.1f s at %d fps)%s"
              % (n, n / helmet.fps, helmet.fps,
                 " from %s" % effect if effect else ""))
        t0 = time.time()
        with mau5fseq.FseqWriter(fseq_out, helmet.channel_count, helmet.fps,
                                 media=audio, compression=compression) as w:
            for i in range(n):
                w.add(source.frame(i, i / helmet.fps))
                if i % 200 == 0:
                    sys.stdout.write("\r  %d/%d" % (i, n)); sys.stdout.flush()
        print("\r  %d/%d frames in %.1f s -> %s (%.2f MB)"
              % (n, n, time.time() - t0, fseq_out,
                 os.path.getsize(fseq_out) / 1e6))

    media_name = None
    if audio:
        media_name = os.path.basename(audio)
        dest = os.path.join(out_dir, media_name)
        if os.path.abspath(audio) != os.path.abspath(dest):
            shutil.copy2(audio, dest)

    with mau5fseq.FseqReader(fseq_out) as s:
        dur = s.duration_s
    pl = playlist_json(name, os.path.basename(fseq_out), media_name, dur)
    pl_out = os.path.join(out_dir, name + ".json")
    with open(pl_out, "w", encoding="utf-8") as fh:
        json.dump(pl, fh, indent=2)
    print("wrote %s" % pl_out)
    return fseq_out, (os.path.join(out_dir, media_name) if media_name else None), pl_out


def upload(helmet, name, host=None, dry_run=False, force=False, out_dir=None):
    base = os.path.dirname(os.path.abspath(helmet.path))
    out_dir = out_dir or os.path.join(base, helmet.cfg["show"].get("shows_dir", "shows"))
    fseq_path = os.path.join(out_dir, name + ".fseq")
    pl_path = os.path.join(out_dir, name + ".json")
    if not os.path.exists(fseq_path):
        raise SystemExit("%s not found -- run `build` first" % fseq_path)
    with open(pl_path, encoding="utf-8") as fh:
        pl = json.load(fh)
    media = pl["mainPlaylist"][0].get("mediaName")
    media_path = os.path.join(out_dir, media) if media else None

    problems = verify(helmet, fseq_path, media_path, strict=True)
    if problems and not force:
        raise SystemExit("refusing to upload: %d problem(s) above.\n"
                         "  Fix them, or re-run with --force if you really "
                         "mean it." % len(problems))
    if problems:
        print("--force given: uploading anyway despite %d problem(s)"
              % len(problems), file=sys.stderr)

    p = helmet.cfg.get("player", {})
    fpp = FPP(host or p.get("host", "192.168.4.1"), dry_run=dry_run,
              upload_paths=p.get("upload_paths"))
    print("uploading to %s" % fpp.base)
    fpp.upload(fseq_path, "sequences")
    if media_path and os.path.exists(media_path):
        fpp.upload(media_path, "music")
    fpp.save_playlist(name, pl)
    print("  playlist %r saved" % name)
    if not dry_run:
        names = fpp.playlists()
        print("  playlists on the Pi: %s" % (", ".join(names) if names else "(none listed)"))
    return True


# --------------------------------------------------------------------------
def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter,
                                 epilog=__doc__)
    ap.add_argument("--config", default=mau5cfg.DEFAULT_CONFIG)
    ap.add_argument("--host", help="override [player] host from helmet.toml")
    sub = ap.add_subparsers(dest="cmd", required=True)

    def add_build(p):
        p.add_argument("--name", required=True, help="show name (file stem)")
        p.add_argument("--audio")
        p.add_argument("--effect", metavar="FILE.py:NAME")
        p.add_argument("--fseq", help="use an existing FSEQ instead of rendering")
        p.add_argument("--seconds", type=float)
        p.add_argument("--compression", choices=["none", "zlib", "zstd"],
                       default="none")

    add_build(sub.add_parser("build", help="render / stage a show locally"))
    d = sub.add_parser("deploy", help="build then upload")
    add_build(d)
    d.add_argument("--dry-run", action="store_true")
    d.add_argument("--force", action="store_true")
    d.add_argument("--start", action="store_true", help="start it after upload")

    u = sub.add_parser("upload", help="push a built show to the Pi")
    u.add_argument("--name", required=True)
    u.add_argument("--dry-run", action="store_true")
    u.add_argument("--force", action="store_true")

    c = sub.add_parser("check", help="verify an FSEQ against helmet.toml")
    c.add_argument("fseq")
    c.add_argument("--audio")

    sub.add_parser("playlists", help="list playlists on the Pi")
    sub.add_parser("status", help="what the Pi is doing")
    st = sub.add_parser("start", help="start a playlist")
    st.add_argument("name")
    st.add_argument("--repeat", action="store_true")
    sp = sub.add_parser("stop", help="stop playback")
    sp.add_argument("--graceful", action="store_true")
    v = sub.add_parser("volume", help="get or set volume")
    v.add_argument("level", nargs="?", type=int)

    a = ap.parse_args(argv)
    helmet = mau5cfg.load(a.config, quiet=True)

    def client():
        p = helmet.cfg.get("player", {})
        return FPP(a.host or p.get("host", "192.168.4.1"),
                   upload_paths=p.get("upload_paths"))

    if a.cmd == "check":
        print(helmet.describe()); print()
        sys.exit(1 if verify(helmet, a.fseq, a.audio) else 0)

    if a.cmd == "build":
        print(helmet.describe()); print()
        f, _m, _p = build(helmet, a.name, a.audio, a.effect, a.fseq,
                          a.seconds, a.compression)
        print()
        verify(helmet, f, a.audio)

    elif a.cmd == "deploy":
        print(helmet.describe()); print()
        build(helmet, a.name, a.audio, a.effect, a.fseq, a.seconds, a.compression)
        print()
        upload(helmet, a.name, a.host, a.dry_run, a.force)
        if a.start and not a.dry_run:
            client().start(a.name)
            print("started %r" % a.name)

    elif a.cmd == "upload":
        upload(helmet, a.name, a.host, a.dry_run, a.force)

    elif a.cmd == "playlists":
        for n in client().playlists():
            print(n)

    elif a.cmd == "status":
        print(json.dumps(client().status(), indent=2))

    elif a.cmd == "start":
        print(client().start(a.name, a.repeat))

    elif a.cmd == "stop":
        print(client().stop(a.graceful))

    elif a.cmd == "volume":
        print(client().volume(a.level))


if __name__ == "__main__":
    _warn_superseded()
    main()
