"""mau5ctl's audio ranges and request parsing, and mau5peek's step.

Nothing here touches the helmet or the network.  The one server is
mau5ctl's own handler on 127.0.0.1, serving a track from a temporary
directory; mau5peek's WebSocket and controller are stubs.
"""

import contextlib
import http.client
import io
import json
import os
import shutil
import sys
import tempfile
import threading

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from test_mau5 import ok, eq  # noqa: E402


def t_ctl_byte_range():
    """Range headers as RFC 9110 reads them, and nothing raises.

    The suffix form used to come back as the start of the file, a start
    past the end as a negative length, and anything unexpected as an
    exception out of the handler.
    """
    import mau5ctl as C
    U = C.UNSATISFIABLE
    size = 1000
    for header, want in (
            (None, None), ("", None),
            ("bytes=0-", (0, 999)),
            ("bytes=0-99", (0, 99)),
            ("bytes=10-19", (10, 19)),
            ("bytes=990-5000", (990, 999)),     # an end past the file is trimmed
            ("bytes=-128", (872, 999)),         # the last 128 -- an ID3v1 probe
            ("bytes=-5000", (0, 999)),          # more than there is: all of it
            ("Bytes=0-9", (0, 9)),              # the unit is case-insensitive
            (" bytes=0-9 ", (0, 9)),
            ("bytes=999-", (999, 999)),
            ("bytes=1000-", U),                 # wholly past the end
            ("bytes=5000-6000", U),
            ("bytes=-0", U),
            ("bytes=20-10", None),              # backwards: not a range at all
            ("bytes=abc-", None),
            ("bytes=-", None),
            ("bytes=0-1,5-6", None),            # several: send the whole file
            ("items=0-9", None),
            ("bytes=1_0-20", None),             # int() would take this
            ("bytes=\u0661-9", None)):          # and this, an Arabic-Indic one
        eq(C.byte_range(header, size), want, "Range %r" % (header,))
    eq(C.byte_range("bytes=0-", 0), U, "any range of an empty file")
    eq(C.byte_range("bytes=-10", 0), U, "a suffix of an empty file")


@contextlib.contextmanager
def _ctl_server(blob):
    """mau5ctl's handler on 127.0.0.1, with HERE pointing at a track."""
    import mau5ctl
    from http.server import ThreadingHTTPServer

    class Ctl:
        def state(self):
            return {"mode": "off"}

        def off(self):
            pass

    tmp = tempfile.mkdtemp(prefix="mau5ctl-test-")
    with open(os.path.join(tmp, "track.mp3"), "wb") as f:
        f.write(blob)
    keep = mau5ctl.HERE
    mau5ctl.HERE = tmp
    srv = ThreadingHTTPServer(("127.0.0.1", 0), mau5ctl.make_handler(Ctl()))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    try:
        yield srv.server_address[1]
    finally:
        srv.shutdown()
        srv.server_close()
        mau5ctl.HERE = keep
        shutil.rmtree(tmp, ignore_errors=True)


def _ask(port, method, path, headers=(), body=None):
    c = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
    try:
        c.putrequest(method, path)
        for k, v in headers:
            c.putheader(k, v)
        c.endheaders(body)
        r = c.getresponse()
        return r.status, dict(r.getheaders()), r.read()
    finally:
        c.close()


def t_ctl_audio_ranges_over_http():
    """Each kind of Range gets an answer, and the right bytes.

    A malformed one used to raise out of the handler, so the phone's
    request got no reply at all.
    """
    blob = bytes(range(256)) * 8                   # 2048 bytes, each one known
    size = len(blob)
    with _ctl_server(blob) as port:
        def get(rng=None, method="GET"):
            return _ask(port, method, "/audio/track.mp3",
                        [("Range", rng)] if rng is not None else [])

        # The bytes are compared, not printed: 2 kB in a failure
        # message buries the status that says what went wrong.
        st, h, b = get()
        eq((st, b == blob), (200, True), "no Range")

        st, h, b = get("bytes=0-")
        eq((st, b == blob, h.get("Content-Range")),
           (206, True, "bytes 0-%d/%d" % (size - 1, size)), "bytes=0-")

        st, h, b = get("bytes=100-199")
        eq((st, b == blob[100:200], h.get("Content-Range")),
           (206, True, "bytes 100-199/%d" % size), "a middle range")

        st, h, b = get("bytes=-128")
        eq((st, b == blob[-128:], h.get("Content-Range")),
           (206, True, "bytes %d-%d/%d" % (size - 128, size - 1, size)),
           "the last 128 bytes")

        st, h, b = get("bytes=%d-" % size)
        eq((st, len(b), h.get("Content-Range")), (416, 0, "bytes */%d" % size),
           "a start past the end")

        for junk in ("bytes=abc-", "bytes=0-1,5-6", "bytes=20-10"):
            st, h, b = get(junk)
            eq((st, b == blob), (200, True), "Range %r" % junk)

        st, h, b = get("bytes=-128", method="HEAD")
        eq((st, b, h.get("Content-Length")), (206, b"", "128"), "HEAD with a range")


def t_ctl_bad_content_length_is_answered():
    """A POST whose length is not a length gets a 400, not silence."""
    with _ctl_server(b"x") as port:
        for cl in ("abc", "-5"):
            st, h, b = _ask(port, "POST", "/api/off",
                            [("Content-Type", "application/json"),
                             ("Content-Length", cl)])
            eq(st, 400, "Content-Length %r" % cl)
            ok(b"Content-Length" in b, "no reason given: %r" % b)
        st, h, b = _ask(port, "POST", "/api/off",
                        [("Content-Type", "application/json"),
                         ("Content-Length", "2")], b"{}")
        eq(st, 200, "a good POST after them")


def t_peek_reports_the_step():
    """--watch says how far apart the samples are, from the bus length.

    It always said "every 1th LED": main() never passed the LED count,
    and live() divided the samples by themselves.
    """
    import mau5peek
    import mau5wled

    class FakePeek(mau5peek.Peek):
        # The real live(), fed a version-1 preview frame of 207 samples.
        def open(self):
            pass

        def close(self):
            pass

        def send_text(self, s):
            pass

        def _frame(self):
            return 0x02, b"L\x01" + bytes([9, 0, 0]) * 207

    def stub_wled(count):
        class W:
            def __init__(self, host, timeout=4.0):
                self.base = "http://" + host

            @property
            def count(self):
                if count is None:
                    raise mau5wled.WLEDError("cannot reach the stub")
                return count
        return W

    keep = (mau5peek.Peek, mau5wled.WLED)
    try:
        mau5peek.Peek = FakePeek
        for count, want in ((622, "every 3th LED"), (207, "every 1th LED"),
                            (None, "every ?th LED")):
            mau5wled.WLED = stub_wled(count)
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc = mau5peek.main(["--host", "stub"])
            out = buf.getvalue()
            eq(rc, 0, "peek with %s LEDs" % count)
            ok(want in out and "207 sampled" in out,
               "with %s LEDs on the bus, wanted %r:\n%s" % (count, want, out))
        mau5wled.WLED = stub_wled(622)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            mau5peek.main(["--host", "stub", "--json"])
        eq(json.loads(buf.getvalue())["every"], 3, "--json step")
    finally:
        mau5peek.Peek, mau5wled.WLED = keep


GROUP = [
    t_ctl_byte_range,
    t_ctl_audio_ranges_over_http,
    t_ctl_bad_content_length_is_answered,
    t_peek_reports_the_step,
]
