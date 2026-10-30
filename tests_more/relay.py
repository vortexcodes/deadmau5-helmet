"""The relay's door, the superseded builders' output, a too-short clip,
and the first camera tool's frames.

Nothing here touches the helmet or the network.  The one HTTP server is
the relay's own handler on 127.0.0.1 with no controller behind it; the
tunnels, the camera and the LEDs are stubs.
"""

import os
import shutil
import socket
import stat
import sys
import tempfile
import threading
import time
import types
import urllib.error
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from test_mau5 import ok, eq, note, HERE  # noqa: E402

import numpy as np  # noqa: E402


# ----------------------------------------------------------------------
# mau5relay
# ----------------------------------------------------------------------
def t_relay_door_opens_only_when_asked():
    """--allow-open lets everyone in; nothing else with no token does.

    And a token with anything outside ASCII in it, on either side, is
    an ordinary wrong (or right) key instead of an exception that drops
    the connection with no answer.
    """
    import mau5relay
    eq(mau5relay.Relay("", None).ok(""), False,
       "an empty token without --allow-open let a request in")
    eq(mau5relay.Relay("", None).ok("anything"), False,
       "an empty token without --allow-open let a request in")
    eq(mau5relay.Relay("", None, allow_open=True).ok(""), True,
       "--allow-open still refused everything")
    r = mau5relay.Relay("abc", None, allow_open=True)
    eq(r.ok("abd"), False, "a token given with --allow-open was not checked")
    eq(r.ok("abc"), True, "the right token was refused")
    r = mau5relay.Relay("abc", None)
    try:
        eq(r.ok("é"), False, "a non-ASCII guess got in")
        eq(r.ok("abc”"), False, "a smart-quoted guess got in")
    except TypeError as e:
        ok(False, "a non-ASCII guess raised: %s" % e)
    r = mau5relay.Relay("tøken’", None)
    eq(r.ok("tøken’"), True, "a non-ASCII token refused itself")
    eq(r.ok("token'"), False, "a non-ASCII token matched its ASCII look-alike")


def t_relay_answers_an_odd_token():
    """Over HTTP: a %C3%A9 token gets a 403, not a dropped connection,
    and open mode serves the page."""
    import mau5relay
    from http.server import ThreadingHTTPServer

    def get(port, path):
        try:
            with urllib.request.urlopen("http://127.0.0.1:%d%s" % (port, path),
                                        timeout=5) as r:
                return r.status
        except urllib.error.HTTPError as e:
            return e.code

    for relay, path, want, what in (
            (mau5relay.Relay("abc", None), "/?t=%C3%A9", 403, "a non-ASCII token"),
            (mau5relay.Relay("abc", None), "/?t=abc", 200, "the right token"),
            (mau5relay.Relay("", None, allow_open=True), "/", 200, "open mode"),
            (mau5relay.Relay("", None), "/", 403, "no token, not open")):
        srv = ThreadingHTTPServer(("127.0.0.1", 0), mau5relay.make_handler(relay))
        th = threading.Thread(target=srv.serve_forever, daemon=True)
        th.start()
        try:
            got = get(srv.server_address[1], path)
        except Exception as e:                      # dropped, timed out
            got = "%s: %s" % (type(e).__name__, e)
        finally:
            srv.shutdown()
            srv.server_close()
        eq(got, want, "%s on %s" % (what, path))


def t_relay_will_not_open_a_public_door():
    """--allow-open with --tunnel is refused before anything is started.

    Open mode used to serve nothing, so the pair was harmless by
    accident.  It is refused before the controller is looked for, so
    this test sends nothing anywhere.
    """
    import mau5relay
    called = []

    def server(*a, **k):
        called.append("server")
        raise SystemExit("stub server")

    real = (mau5relay.start_tunnel, mau5relay.mau5wled.find_one,
            mau5relay.ThreadingHTTPServer)
    mau5relay.start_tunnel = lambda *a, **k: called.append("tunnel")
    mau5relay.mau5wled.find_one = lambda *a, **k: called.append("find")
    mau5relay.ThreadingHTTPServer = server
    try:
        mau5relay.main(["--token", "", "--allow-open", "--tunnel",
                        "--host", "192.0.2.9"])
        ok(False, "--allow-open --tunnel started")
    except SystemExit as e:
        ok("--tunnel" in str(e), "refused, but said: %s" % e)
    finally:
        (mau5relay.start_tunnel, mau5relay.mau5wled.find_one,
         mau5relay.ThreadingHTTPServer) = real
    eq(called, [], "something was started before the refusal")


def t_relay_url_file_carries_the_shell():
    """relay_url.txt gets the SSH host as well as the URL.

    It was written before the SSH tunnel existed, so the shell host --
    the one thing the far end cannot find out any other way -- never
    reached it.  Tunnels, server and the port-22 probe are stubs.
    """
    import mau5relay
    d = tempfile.mkdtemp(prefix="mau5relay")
    path = os.path.join(d, "relay_url.txt")

    class Proc:
        def terminate(self):
            pass

    def tunnel(port, timeout=45, scheme="http"):
        return Proc(), ("https://shell-words.trycloudflare.com" if scheme == "ssh"
                        else "https://page-words.trycloudflare.com")

    class Srv:
        def __init__(self, *a, **k):
            pass

        def serve_forever(self):
            raise KeyboardInterrupt

    class Probe:
        def __init__(self, *a, **k):
            pass

        def settimeout(self, t):
            pass

        def connect_ex(self, addr):
            return 0                                # "Remote Login is on"

        def close(self):
            pass

    real = (mau5relay.start_tunnel, mau5relay.ThreadingHTTPServer,
            mau5relay.tailnet_ip, mau5relay.mau5wled.lan_ip, socket.socket)
    import io
    import contextlib
    try:
        mau5relay.start_tunnel = tunnel
        mau5relay.ThreadingHTTPServer = Srv
        mau5relay.tailnet_ip = lambda: None
        mau5relay.mau5wled.lan_ip = lambda: "192.0.2.1"
        socket.socket = Probe
        with contextlib.redirect_stdout(io.StringIO()):
            mau5relay.main(["--token", "k3y", "--host", "192.0.2.9",
                            "--tunnel", "--ssh", "--url-file", path])
        socket.socket = real[4]
        text = open(path).read()
        ok("https://page-words.trycloudflare.com/?t=k3y" in text,
           "the relay URL is missing: %r" % text)
        ok("ssh host: https://shell-words.trycloudflare.com" in text,
           "the SSH host never reached the file: %r" % text)
        eq(stat.S_IMODE(os.stat(path).st_mode), 0o600,
           "the file holds the token and is readable by others")

        # the shell on its own still gets written down
        os.remove(path)
        mau5relay.write_url_file(path, None, "k3y", "https://only-shell.example")
        eq(open(path).read(), "ssh host: https://only-shell.example\n",
           "the SSH host alone")
    finally:
        (mau5relay.start_tunnel, mau5relay.ThreadingHTTPServer,
         mau5relay.tailnet_ip, mau5relay.mau5wled.lan_ip, socket.socket) = real
        shutil.rmtree(d, ignore_errors=True)


# ----------------------------------------------------------------------
# mau5build / mau5song: the superseded builders
# ----------------------------------------------------------------------
def t_superseded_build_keeps_out_of_the_shows():
    """build() leaves shows/ alone: its playlist goes to shows/superseded.

    Everything that lists the shows takes every *.json at the top of
    shows/ for one, and an FPP playlist there would not load, stopped
    mau5doctor, and under a show's name replaced its cue list.
    """
    import mau5build
    import mau5cfg
    import mau5fseq
    h = mau5cfg.load(mau5cfg.DEFAULT_CONFIG, quiet=True)
    eq(mau5build.out_dir_for(h), os.path.join(HERE, "shows", "superseded"),
       "where the real config sends the superseded output")

    d = tempfile.mkdtemp(prefix="mau5build")
    try:
        shows = os.path.join(d, "shows")
        os.makedirs(shows)
        live = os.path.join(shows, "intro.json")
        with open(live, "w") as f:
            f.write('{"track": "intro.mp3", "cues": []}')
        src = os.path.join(d, "src.fseq")
        with mau5fseq.FseqWriter(src, 12, 40) as w:
            for _ in range(8):
                w.add(np.zeros(12, np.uint8))
        fake = types.SimpleNamespace(path=os.path.join(d, "helmet.toml"),
                                     cfg={"show": {"shows_dir": "shows"}})
        import io
        import contextlib
        with contextlib.redirect_stdout(io.StringIO()):
            f, _m, pl = mau5build.build(fake, "intro", fseq=src)
        eq(open(live).read(), '{"track": "intro.mp3", "cues": []}',
           "build overwrote a show's cue list")
        eq(os.path.dirname(pl), os.path.join(shows, "superseded"),
           "the playlist landed beside the shows")
        eq(sorted(os.listdir(shows)), ["intro.json", "superseded"],
           "build left files at the top of shows/")
    finally:
        shutil.rmtree(d, ignore_errors=True)


def t_song_refuses_a_stinger():
    """A clip too short to hold three bars is refused in so many words.

    It used to fall over inside the arithmetic: a broadcast error under
    half a second, "v cannot be empty" around a second, and three
    levels for one bar after that.  A full-length clip is unaffected.
    """
    import mau5song
    from test_mau5 import _click_wav
    d = tempfile.mkdtemp(prefix="mau5short")
    try:
        import warnings
        for s in (0.3, 1.5, 4.0):
            p = _click_wav(os.path.join(d, "c%s.wav" % s), 128.0, seconds=s)
            try:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    mau5song.analyse(p, verbose=False)
                ok(False, "a %.1f s clip was analysed" % s)
            except ValueError as e:
                ok("needs at least" in str(e),
                   "%.1f s refused, but obscurely: %s" % (s, e))
        p = _click_wav(os.path.join(d, "full.wav"), 128.0, seconds=8.0)
        an = mau5song.analyse(p, verbose=False)
        eq(len(an["levels"]), len(an["bars"]) - 1,
           "one level per whole bar on a clip that is long enough")
    finally:
        shutil.rmtree(d, ignore_errors=True)


# ----------------------------------------------------------------------
# mau5cal: the first camera tool
# ----------------------------------------------------------------------
def t_cal_grab_will_not_hand_back_a_stale_frame():
    """No new frame in time is None, not the last frame again.

    Once ffmpeg died, every later grab returned the same frame and a
    scan put every later LED where the last one had been.
    """
    import mau5cal
    cam = mau5cal.Camera()
    cam._frame = np.zeros((2, 2, 3), np.uint8)
    cam._count = 5
    t0 = time.monotonic()
    eq(cam.grab(fresh=1, timeout=0.2), None, "a stale frame came back")
    ok(time.monotonic() - t0 < 2.0, "grab overran its timeout")

    def pump():
        for _ in range(3):
            time.sleep(0.02)
            with cam._lock:
                cam._frame = np.full((2, 2, 3), 7, np.uint8)
                cam._count += 1
                cam._lock.notify_all()
    th = threading.Thread(target=pump)
    th.start()
    f = cam.grab(fresh=2, timeout=3.0)
    th.join()
    ok(f is not None and int(f[0, 0, 0]) == 7, "a fresh frame was not returned")

    try:
        cam.dark(n=2, fresh=1)
        ok(False, "a dark reference was taken from no frames")
    except SystemExit as e:
        ok("stopped sending" in str(e), "refused, but said: %s" % e)


class _SlowCamera:
    """Shows what the LEDs were doing `lag` frames ago."""

    def __init__(self, pix, lag, sees=True):
        self.pix, self.lag, self.sees, self.n = pix, lag, sees, 0

    def grab(self, fresh=2, timeout=5.0):
        self.n += max(1, fresh)
        lit = self.sees and self.pix.lit_at(self.n - self.lag)
        return np.full((4, 4, 3), 200 if lit else 10, np.uint8)


class _Pix:
    def __init__(self):
        self.cam = None
        self.history = [(-10 ** 9, False)]

    def _set(self, lit):
        self.history.append((self.cam.n, lit))

    def clear(self):
        self._set(False)

    def all(self, color=(255, 255, 255)):
        self._set(True)

    def lit_at(self, frame):
        state = False
        for at, lit in self.history:
            if at <= frame:
                state = lit
        return state


def t_cal_latency_follows_a_slow_camera():
    """A camera 20 frames behind is measured at 20-odd, not clamped to 6.

    And one that never sees the flash stops the run instead of guessing
    3: a scan on a guessed latency reads every LED from the wrong frame.
    """
    import mau5cal
    real = mau5cal.time
    mau5cal.time = types.SimpleNamespace(sleep=lambda s: None,
                                         monotonic=time.monotonic)
    try:
        for lag in (3, 9, 20):
            pix = _Pix()
            cam = _SlowCamera(pix, lag)
            pix.cam = cam
            got = mau5cal.measure_latency(cam, pix, tries=3)
            ok(got >= lag, "a camera %d frames behind measured as %d" % (lag, got))
            ok(got <= lag + 2, "a camera %d frames behind measured as %d" % (lag, got))
        pix = _Pix()
        cam = _SlowCamera(pix, 5, sees=False)
        pix.cam = cam
        try:
            mau5cal.measure_latency(cam, pix, tries=2, watch=0.05)
            ok(False, "no flash was ever seen and a latency came back")
        except SystemExit as e:
            ok("never saw" in str(e), "refused, but said: %s" % e)
        eq(pix.history[-1][1], False, "the helmet was left lit")
    finally:
        mau5cal.time = real


GROUP = [t_relay_door_opens_only_when_asked, t_relay_answers_an_odd_token,
         t_relay_will_not_open_a_public_door, t_relay_url_file_carries_the_shell,
         t_superseded_build_keeps_out_of_the_shows, t_song_refuses_a_stinger,
         t_cal_grab_will_not_hand_back_a_stale_frame,
         t_cal_latency_follows_a_slow_camera]
