#!/usr/bin/env python3
"""mau5peek -- read back what the strip is actually showing.

Everything else in here is open loop: a frame is sent and whether it
arrived is a matter of belief, or of pointing a camera at the helmet
and hoping the room is dark.  WLED will tell you directly.  Its web UI
has a live preview, fed by a WebSocket that answers ``{"lv":true}``
with the colour of every LED as the strip is driving it, and that is
the one measurement in this project that needs neither a camera nor a
dark room nor anything to be calibrated.

Two things it settles that nothing else can:

  Did the pixels land?  A frozen segment painted through ``seg.i`` is
  the route the phone player uses, and ``/json/info`` reports no
  current for it at all -- the estimate only counts segments it
  rendered itself.  The preview counts what is on the wire.

  Is the brightness limiter in the path?  Compare the colours asked
  for with the colours read back.

The preview subsamples: the firmware serves at most a couple of
hundred LEDs per frame, every n'th one, so `n` comes back with the
data and the indices are 0, n, 2n ...  That is plenty to measure a
level and to see which end of the chain is lit, and it is not a
substitute for the camera when the question is *where* an LED is.

    python3 mau5peek.py --host 192.168.10.172
    python3 mau5peek.py --watch 10
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import select
import socket
import struct
import sys
import time


class PeekError(RuntimeError):
    pass


class Peek:
    """A WebSocket client just big enough for WLED's live preview.

    Hand-rolled rather than pulled in: the handshake is four lines,
    server-to-client frames are never masked, and the alternative is a
    dependency on a laptop that has to work at a show.
    """

    def __init__(self, host, port=80, timeout=6.0):
        self.host, self.port, self.timeout = host, port, timeout
        self.sock = None
        self.buf = b""

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, *a):
        self.close()

    def open(self):
        key = base64.b64encode(os.urandom(16)).decode()
        s = socket.create_connection((self.host, self.port), self.timeout)
        s.settimeout(self.timeout)
        s.sendall(("GET /ws HTTP/1.1\r\nHost: %s\r\nUpgrade: websocket\r\n"
                   "Connection: Upgrade\r\nSec-WebSocket-Key: %s\r\n"
                   "Sec-WebSocket-Version: 13\r\n\r\n"
                   % (self.host, key)).encode())
        head = b""
        while b"\r\n\r\n" not in head:
            chunk = s.recv(4096)
            if not chunk:
                raise PeekError("controller closed the connection during the "
                                "WebSocket handshake")
            head += chunk
        if b"101" not in head.split(b"\r\n", 1)[0]:
            raise PeekError("controller refused the WebSocket: %s"
                            % head.split(b"\r\n", 1)[0].decode("latin1"))
        self.sock, self.buf = s, head.split(b"\r\n\r\n", 1)[1]

    def close(self):
        if self.sock:
            try:
                self.sock.close()
            finally:
                self.sock = None

    # -- frames ---------------------------------------------------------
    def _need(self, n):
        while len(self.buf) < n:
            chunk = self.sock.recv(65536)
            if not chunk:
                raise PeekError("controller closed the connection")
            self.buf += chunk

    def _frame(self):
        self._need(2)
        b0, b1 = self.buf[0], self.buf[1]
        op, ln, off = b0 & 0x0F, b1 & 0x7F, 2
        if ln == 126:
            self._need(4); ln = struct.unpack(">H", self.buf[2:4])[0]; off = 4
        elif ln == 127:
            self._need(10); ln = struct.unpack(">Q", self.buf[2:10])[0]; off = 10
        self._need(off + ln)
        payload = self.buf[off:off + ln]
        self.buf = self.buf[off + ln:]
        return op, payload

    def drain(self):
        """Throw away whatever is already on the socket.

        The preview is a queue, not a question.  Asking for a frame
        and reading the next binary one that arrives returns whatever
        was already in flight -- which is the state *before* the thing
        you just changed, and reads as a change that did not happen.
        Everything pending is discarded first, so the frame that comes
        back was composed after the request.
        """
        self.buf = b""
        while select.select([self.sock], [], [], 0)[0]:
            if not self.sock.recv(65536):
                break

    def send_text(self, s):
        data = s.encode()
        # client frames must be masked, says the RFC, and WLED checks
        mask = os.urandom(4)
        body = bytes(c ^ mask[i % 4] for i, c in enumerate(data))
        n = len(data)
        if n < 126:
            head = bytes([0x80 | n])
        elif n < 65536:
            head = b"\xfe" + struct.pack(">H", n)
        else:
            head = b"\xff" + struct.pack(">Q", n)
        self.sock.sendall(b"\x81" + head + mask + body)

    # -- the preview ----------------------------------------------------
    def live(self, total=None, deadline=4.0):
        """One preview frame: (step, [(r, g, b), ...]) for LEDs 0, step, 2*step...

        `lv` has to be asked for again and again: the firmware serves
        the preview for a while and then stops, so a tab left open
        does not cost the strip a copy of itself forty times a second.

        Every write to /json/state also broadcasts the new state to
        every WebSocket client, so the socket is usually carrying a
        backlog of text frames when this is called.  Reading until a
        binary one turns up -- rather than giving each request one
        frame to be the right one -- is the difference between this
        working and this timing out whenever anything else is talking
        to the controller.
        """
        self.drain()
        end, last = time.time() + deadline, 0.0
        while time.time() < end:
            if time.time() - last > 0.8:
                self.send_text('{"lv":true}')
                last = time.time()
            op, p = self._frame()
            if op == 0x08:
                raise PeekError("controller closed the WebSocket")
            if op != 0x02 or len(p) < 5 or p[0:1] != b"L":
                continue
            body = p[2:]
            rgb = [tuple(body[i:i + 3]) for i in range(0, len(body) - 2, 3)]
            step = max(1, int(round((total or len(rgb)) / float(len(rgb)))))
            return step, rgb
        raise PeekError("no live frame in %.0fs -- is this build compiled "
                        "with the web UI?" % deadline)


def summarise(rgb):
    n = len(rgb)
    lit = [c for c in rgb if max(c) > 2]
    mx = max((max(c) for c in rgb), default=0)
    mean = sum(sum(c) for c in rgb) / (3.0 * n) if n else 0.0
    return {"sampled": n, "lit": len(lit), "max": mx, "mean": round(mean, 1)}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--host", default=None)
    ap.add_argument("--watch", type=float, default=0.0,
                    help="keep reading for this many seconds")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)

    host = a.host
    if not host:
        import mau5wled
        w = (mau5wled.scan_subnet() or [None])[0]
        if w is None:
            raise SystemExit("no controller found")
        host = w.base.split("//", 1)[-1]

    with Peek(host) as p:
        t0 = time.time()
        while True:
            step, rgb = p.live()
            s = summarise(rgb)
            s["every"] = step
            if a.json:
                print(json.dumps(s))
            else:
                print("  every %dth LED · %d sampled · %d lit · max %d · mean %.1f"
                      % (step, s["sampled"], s["lit"], s["max"], s["mean"]))
            if time.time() - t0 >= a.watch:
                break
            time.sleep(0.4)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
