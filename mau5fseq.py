#!/usr/bin/env python3
"""mau5fseq -- how pixel data moves: FSEQ v2 files and the DDP wire protocol.

Two things live here because both the simulator and the packager need both:

    seq = FseqReader("show.fseq")        # what FPP plays / xLights exports
    frame = seq.frame(120)               # uint8 channel data for frame 120

    with FseqWriter("show.fseq", channel_count=4218, fps=40,
                    media="show.mp3") as w:
        for i in range(n):
            w.add(frame_bytes)

    tx = DDPSender("192.168.4.50")       # push a frame at the controller
    tx.send(frame_bytes)

    rx = DDPReceiver(port=4048)          # or catch what xLights/WLED is sending
    rx.start(); data = rx.latest()

FSEQ v2 layout, from FPP's src/fseq/FSEQFile.cpp (v2.x).  Offsets in bytes:

    0    4  magic 'PSEQ'
    4    2  uint16  offset of the first frame's channel data
    6    1  minor version
    7    1  major version (2)
    8    2  uint16  length of this fixed header (32)
    10   4  uint32  channel count per frame
    14   4  uint32  number of frames
    18   1  uint8   step time, milliseconds
    19   1  uint8   flags (reserved, 0)
    20   1  uint8   low nibble = compression type, high nibble = block count 8..11
    21   1  uint8   compressed block count, low 8 bits
    22   1  uint8   sparse range count
    23   1  uint8   flags2 (reserved, 0)
    24   8  uint64  unique id (creation time in microseconds)
    32   .  compression block index: n * (uint32 firstFrame, uint32 byteLength)
         .  sparse range index:      n * (uint24 startChannel, uint24 count)
         .  variable headers: uint16 length (incl. these 4 bytes), 2 ascii code, data
         .  zero padding up to the channel data offset

Compression type 0 = none, 1 = zstd, 2 = zlib.  Blocks are compressed
independently so a player can seek; the block index says which frame each
block starts at.
"""

from __future__ import annotations

import os
import socket
import struct
import threading
import time
import zlib

import numpy as np

MAGIC = b"PSEQ"
COMP_NONE, COMP_ZSTD, COMP_ZLIB = 0, 1, 2
DDP_PORT = 4048
DDP_MAX_DATA = 1440          # 480 RGB pixels, stays inside one ethernet frame


def _zstd():
    try:
        import zstandard
        return zstandard
    except ImportError:
        return None


# --------------------------------------------------------------------------
# reading
# --------------------------------------------------------------------------
class FseqReader:
    """Random-access reader for FSEQ v1 and v2, compressed or not."""

    def __init__(self, path):
        self.path = path
        self.fh = open(path, "rb")
        head = self.fh.read(32)
        if head[:4] != MAGIC:
            raise ValueError("%s: not an FSEQ file (magic %r)" % (path, head[:4]))
        (self.data_offset, self.minor, self.major, self.header_len,
         self.channel_count, self.frame_count, self.step_time_ms,
         self.flags) = struct.unpack_from("<HBBHIIBB", head, 4)

        self.sparse_ranges = []
        self.blocks = []
        self.variable = {}

        if self.major >= 2:
            comp, nblocks_lo, nsparse, _f2 = struct.unpack_from("<BBBB", head, 20)
            self.compression = comp & 0x0F
            nblocks = ((comp & 0xF0) << 4) | nblocks_lo
            self.unique_id, = struct.unpack_from("<Q", head, 24)
            pos = 32
            raw = self._read_at(pos, self.data_offset - pos)
            for i in range(nblocks):
                first, length = struct.unpack_from("<II", raw, i * 8)
                self.blocks.append((first, length))
            pos = nblocks * 8
            for i in range(nsparse):
                s = raw[pos:pos + 6]
                start = s[0] | s[1] << 8 | s[2] << 16
                count = s[3] | s[4] << 8 | s[5] << 16
                self.sparse_ranges.append((start, count))
                pos += 6
            while pos + 4 <= len(raw):
                ln, = struct.unpack_from("<H", raw, pos)
                if ln < 4:
                    break
                code = raw[pos + 2:pos + 4].decode("ascii", "replace")
                self.variable[code] = raw[pos + 4:pos + ln].rstrip(b"\x00")
                pos += ln
        else:
            self.compression = COMP_NONE
            self.unique_id = 0

        # width of one stored frame: sparse files store only the listed ranges
        self.stored_width = (sum(c for _s, c in self.sparse_ranges)
                             if self.sparse_ranges else self.channel_count)
        self._cache_idx = -1
        self._cache = None

        if self.compression != COMP_NONE and not self.blocks:
            raise ValueError("%s: compressed but has no block index" % path)

    # -- properties -------------------------------------------------------
    @property
    def fps(self):
        return round(1000.0 / self.step_time_ms, 3) if self.step_time_ms else 0.0

    @property
    def duration_s(self):
        return self.frame_count * self.step_time_ms / 1000.0

    @property
    def media(self):
        v = self.variable.get("mf")
        return v.decode("utf-8", "replace") if v else None

    def close(self):
        self.fh.close()

    def __enter__(self):
        return self

    def __exit__(self, *a):
        self.close()

    def __len__(self):
        return self.frame_count

    def describe(self):
        comp = {0: "none", 1: "zstd", 2: "zlib"}.get(self.compression, "?")
        return ("%s: v%d.%d  %d channels  %d frames  %d ms/frame (%.4g fps)\n"
                "  %.1f s  compression=%s blocks=%d sparse=%d media=%s"
                % (os.path.basename(self.path), self.major, self.minor,
                   self.channel_count, self.frame_count, self.step_time_ms,
                   self.fps, self.duration_s, comp, len(self.blocks),
                   len(self.sparse_ranges), self.media))

    # -- frames -----------------------------------------------------------
    def _read_at(self, offset, length):
        self.fh.seek(offset)
        return self.fh.read(length)

    def _block_for(self, frame):
        for i in range(len(self.blocks) - 1, -1, -1):
            if self.blocks[i][0] <= frame:
                return i
        return 0

    def _load_block(self, i):
        if self._cache_idx == i:
            return self._cache
        offset = self.data_offset + sum(b[1] for b in self.blocks[:i])
        length = self.blocks[i][1]
        if length == 0:                      # some writers mean "to end of file"
            length = os.path.getsize(self.path) - offset
        raw = self._read_at(offset, length)
        if self.compression == COMP_ZLIB:
            raw = zlib.decompress(raw)
        elif self.compression == COMP_ZSTD:
            z = _zstd()
            if z is None:
                raise RuntimeError(
                    "%s is zstd-compressed; `pip install zstandard` to read it, "
                    "or re-export it uncompressed from xLights." % self.path)
            raw = z.ZstdDecompressor().decompressobj().decompress(raw)
        self._cache_idx, self._cache = i, raw
        return raw

    def frame(self, i):
        """Full channel data for frame ``i`` as a uint8 array of channel_count."""
        if not 0 <= i < self.frame_count:
            raise IndexError(i)
        w = self.stored_width
        if self.compression == COMP_NONE:
            raw = self._read_at(self.data_offset + i * w, w)
        else:
            b = self._block_for(i)
            raw = self._load_block(b)
            off = (i - self.blocks[b][0]) * w
            raw = raw[off:off + w]
        if len(raw) < w:
            raw = raw + b"\x00" * (w - len(raw))
        buf = np.frombuffer(raw, np.uint8)
        if not self.sparse_ranges:
            return buf
        out = np.zeros(self.channel_count, np.uint8)
        pos = 0
        for start, count in self.sparse_ranges:
            out[start:start + count] = buf[pos:pos + count]
            pos += count
        return out

    def frames(self):
        for i in range(self.frame_count):
            yield self.frame(i)

    def pixels(self, i):
        """Frame ``i`` reshaped to (n_leds, 3)."""
        f = self.frame(i)
        n = len(f) // 3
        return f[:n * 3].reshape(n, 3)


# --------------------------------------------------------------------------
# writing
# --------------------------------------------------------------------------
class FseqWriter:
    """Write an FSEQ v2.0 file one frame at a time.

    Uncompressed by default: FPP always reads it, it seeks instantly, and a
    three minute show of 4218 channels is only 1.2 MB.
    """

    def __init__(self, path, channel_count, fps=40, media=None,
                 compression="none", frames_per_block=None, unique_id=None):
        self.path = path
        self.channel_count = int(channel_count)
        # FSEQ stores the step time as a whole number of milliseconds, so a
        # frame rate that does not divide 1000 cannot be represented and the
        # file would play at a different speed than it was rendered at.
        if abs(1000.0 / fps - round(1000.0 / fps)) > 1e-9:
            raise ValueError(
                "%g fps needs a step time of %.4f ms, and FSEQ only stores whole "
                "milliseconds.\n  Use a rate that divides 1000 -- 20, 25, 40 or "
                "50 fps." % (fps, 1000.0 / fps))
        self.step_time_ms = int(round(1000.0 / fps))
        self.media = media
        self.frame_count = 0
        self.comp = {"none": COMP_NONE, "zstd": COMP_ZSTD,
                     "zlib": COMP_ZLIB}[compression]
        if self.comp == COMP_ZSTD and _zstd() is None:
            raise RuntimeError("zstd requested but the `zstandard` module is "
                               "not installed; use compression='zlib' or 'none'")
        # one block per ~1 MB of raw frames keeps the block index small
        self.fpb = frames_per_block or max(1, 1_000_000 // max(self.channel_count, 1))
        self.unique_id = unique_id if unique_id is not None else int(time.time() * 1e6)

        self.variable = []
        if media:
            self.variable.append(("mf", os.path.basename(media).encode() + b"\x00"))
        self.variable.append(("sp", b"mau5build\x00"))

        self._blocks = []          # (first_frame, byte_length)
        self._pending = []         # frames waiting in the current block
        self._pending_first = 0
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        self.fh = open(path, "wb")
        self._header_len = self._reserve_header()

    # -- header -----------------------------------------------------------
    def _var_bytes(self):
        out = b""
        for code, data in self.variable:
            ln = 4 + len(data)
            if ln % 4:
                data += b"\x00" * (4 - ln % 4)
                ln = 4 + len(data)
            out += struct.pack("<H", ln) + code.encode("ascii")[:2] + data
        return out

    def _max_blocks(self):
        return 0 if self.comp == COMP_NONE else 4095

    def _reserve_header(self):
        n = 0 if self.comp == COMP_NONE else self._max_blocks()
        size = 32 + n * 8 + len(self._var_bytes())
        size = (size + 3) & ~3
        self.fh.write(b"\x00" * size)
        return size

    def _write_header(self):
        vb = self._var_bytes()
        nblocks = len(self._blocks)
        head = bytearray(32)
        head[0:4] = MAGIC
        struct.pack_into("<HBBHIIBB", head, 4,
                         self._header_len, 0, 2, 32,
                         self.channel_count, self.frame_count,
                         self.step_time_ms, 0)
        head[20] = (self.comp & 0x0F) | ((nblocks >> 4) & 0xF0)
        head[21] = nblocks & 0xFF
        head[22] = 0
        head[23] = 0
        struct.pack_into("<Q", head, 24, self.unique_id & 0xFFFFFFFFFFFFFFFF)
        body = b"".join(struct.pack("<II", f, n) for f, n in self._blocks)
        pad = self._header_len - (32 + len(body) + len(vb))
        if pad < 0:
            raise RuntimeError("fseq header overflowed its reservation")
        self.fh.seek(0)
        self.fh.write(bytes(head) + body + vb + b"\x00" * pad)

    # -- frames -----------------------------------------------------------
    def add(self, frame):
        """Append one frame.  Accepts bytes, a uint8 array, or (n,3) pixels."""
        if isinstance(frame, np.ndarray):
            frame = np.ascontiguousarray(frame, np.uint8).reshape(-1).tobytes()
        elif not isinstance(frame, (bytes, bytearray)):
            frame = bytes(frame)
        if len(frame) < self.channel_count:
            frame = frame + b"\x00" * (self.channel_count - len(frame))
        elif len(frame) > self.channel_count:
            frame = frame[:self.channel_count]

        if self.comp == COMP_NONE:
            self.fh.write(frame)
        else:
            self._pending.append(frame)
            if len(self._pending) >= self.fpb:
                self._flush_block()
        self.frame_count += 1

    def _flush_block(self):
        if not self._pending:
            return
        raw = b"".join(self._pending)
        if self.comp == COMP_ZLIB:
            blob = zlib.compress(raw, 6)
        else:
            blob = _zstd().ZstdCompressor(level=10).compress(raw)
        self.fh.write(blob)
        self._blocks.append((self._pending_first, len(blob)))
        self._pending_first += len(self._pending)
        self._pending = []

    def close(self):
        if self.fh.closed:
            return
        self._flush_block()
        self._write_header()
        self.fh.close()

    def __enter__(self):
        return self

    def __exit__(self, *a):
        self.close()


def write_fseq(path, frames, channel_count, fps=40, media=None,
               compression="none"):
    """Convenience: write an iterable of frames in one call."""
    with FseqWriter(path, channel_count, fps, media, compression) as w:
        for f in frames:
            w.add(f)
    return path


# --------------------------------------------------------------------------
# DDP
# --------------------------------------------------------------------------
class DDPSender:
    """Push frames at a WLED controller (or the simulator) over DDP."""

    VER = 0x40
    PUSH = 0x01

    def __init__(self, host, port=DDP_PORT, dest_id=1, max_data=DDP_MAX_DATA):
        self.addr = (host, int(port))
        self.dest_id = dest_id
        self.max_data = max_data - (max_data % 3)
        self.seq = 0
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    def send(self, data):
        if isinstance(data, np.ndarray):
            data = np.ascontiguousarray(data, np.uint8).reshape(-1).tobytes()
        self.seq = self.seq % 15 + 1
        total = len(data)
        off = 0
        while off < total:
            chunk = data[off:off + self.max_data]
            last = off + len(chunk) >= total
            flags = self.VER | (self.PUSH if last else 0)
            hdr = struct.pack(">BBBBIH", flags, self.seq, 0, self.dest_id,
                              off, len(chunk))
            self.sock.sendto(hdr + chunk, self.addr)
            off += len(chunk)

    def close(self):
        self.sock.close()


class DDPReceiver:
    """Listen for DDP and hand back whole frames.

    Packets are accumulated into one buffer; a packet with the PUSH bit set
    ends the frame.  ``latest()`` returns the most recent complete frame, or
    pass ``on_frame`` to be called with each one.
    """

    def __init__(self, port=DDP_PORT, channel_count=None, bind="0.0.0.0",
                 on_frame=None):
        self.port = int(port)
        self.bind = bind
        self.channel_count = channel_count
        self.on_frame = on_frame
        self._buf = bytearray(channel_count or 0)
        self._latest = None
        self._lock = threading.Lock()
        self._stop = threading.Event()
        self._thread = None
        self.packets = 0
        self.frames = 0
        self.last_time = 0.0

    def start(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.settimeout(0.25)
        self.sock.bind((self.bind, self.port))
        self._thread = threading.Thread(target=self._run, daemon=True,
                                        name="ddp-rx")
        self._thread.start()
        return self

    def _run(self):
        while not self._stop.is_set():
            try:
                pkt, _addr = self.sock.recvfrom(65535)
            except socket.timeout:
                continue
            except OSError:
                break
            if len(pkt) < 10 or (pkt[0] & 0xC0) != 0x40:
                continue
            flags = pkt[0]
            hlen = 14 if flags & 0x10 else 10       # optional timecode
            off, ln = struct.unpack_from(">IH", pkt, 4)
            data = pkt[hlen:hlen + ln]
            self.packets += 1
            need = off + len(data)
            with self._lock:
                if need > len(self._buf):
                    if self.channel_count:
                        data = data[:max(0, self.channel_count - off)]
                        need = off + len(data)
                    if need > len(self._buf):
                        self._buf.extend(b"\x00" * (need - len(self._buf)))
                if data:
                    self._buf[off:off + len(data)] = data
                if flags & 0x01:                    # PUSH -> frame complete
                    self._latest = np.frombuffer(bytes(self._buf), np.uint8)
                    self.frames += 1
                    self.last_time = time.time()
                    cb, frame = self.on_frame, self._latest
            if flags & 0x01 and self.on_frame:
                cb(frame)

    def latest(self):
        with self._lock:
            return self._latest

    def stop(self):
        self._stop.set()
        try:
            self.sock.close()
        except Exception:
            pass


# --------------------------------------------------------------------------
if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="inspect or probe FSEQ / DDP")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("info", help="print an FSEQ header")
    p.add_argument("file")
    p.add_argument("--frame", type=int, help="also dump this frame's first pixels")
    p = sub.add_parser("listen", help="count DDP packets on a port")
    p.add_argument("--port", type=int, default=DDP_PORT)
    p.add_argument("--seconds", type=float, default=5.0)
    a = ap.parse_args()

    if a.cmd == "info":
        with FseqReader(a.file) as s:
            print(s.describe())
            if a.frame is not None:
                px = s.pixels(a.frame)
                print("frame %d, first 8 pixels:" % a.frame)
                for i, p3 in enumerate(px[:8]):
                    print("  %3d  %3d %3d %3d" % (i, p3[0], p3[1], p3[2]))
    else:
        rx = DDPReceiver(port=a.port).start()
        t0 = time.time()
        while time.time() - t0 < a.seconds:
            time.sleep(0.25)
            f = rx.latest()
            print("\r%5d packets  %4d frames  width %s" %
                  (rx.packets, rx.frames, len(f) if f is not None else "-"),
                  end="", flush=True)
        rx.stop()
        print()
