#!/usr/bin/env python3
"""mau5wled -- talk to the WLED controller directly, with no player in between.

The helmet is now one chain on one WLED output, and the show host streams DDP
straight at it.  This module is the whole controller side:

    w = WLED("4.3.2.1")
    print(w.info()["leds"]["count"])
    w.realtime(True)                 # make sure live input is accepted

    out = Pixels(w)                  # DDP sender sized from the controller
    out.one(37, (255, 0, 0))         # light LED 37 red, everything else off
    out.send(frame)                  # (n, 3) uint8

Colour order is handled here rather than on the controller.  The shell strip
and the outer ear strips are wired in different orders, so a single bus-wide
setting in WLED cannot be right for both -- send orange and the ears come out
green.  ``Pixels`` applies a per-LED channel permutation before transmitting,
so one DDP stream drives mixed strips correctly.  mau5cal measures those
permutations from a camera; they live in helmet.toml under [[strip]].
"""

from __future__ import annotations

import json
import os
import socket
import subprocess
import struct
import threading
import sys
import time
import urllib.error
import urllib.request

import numpy as np

DDP_PORT = 4048
DDP_MAX_DATA = 1440                      # 480 RGB pixels, one ethernet frame

# name -> the channel each sent slot ends up driving on the physical strip
ORDER_NAMES = {0: "GRB", 1: "RGB", 2: "BRG", 3: "RBG", 4: "BGR", 5: "GBR"}

ORDERS = {
    "RGB": (0, 1, 2), "RBG": (0, 2, 1), "GRB": (1, 0, 2),
    "GBR": (1, 2, 0), "BRG": (2, 0, 1), "BGR": (2, 1, 0),
}
ORDER_NAME = {v: k for k, v in ORDERS.items()}


class WLEDError(RuntimeError):
    pass


class WLED:
    """The controller's JSON API.  Everything here is plain HTTP."""

    def __init__(self, host, timeout=4.0):
        host = host if "://" in host else "http://" + host
        self.base = host.rstrip("/")
        self.timeout = timeout
        self._info = None

    # -- transport --------------------------------------------------------
    def _get(self, path):
        try:
            with urllib.request.urlopen(self.base + path, timeout=self.timeout) as r:
                return json.loads(r.read() or b"null")
        except urllib.error.URLError as e:
            raise WLEDError("cannot reach %s%s: %s\n"
                            "  Is the controller powered and on the same network?"
                            % (self.base, path, e.reason))

    def _post(self, path, obj):
        data = json.dumps(obj).encode()
        req = urllib.request.Request(self.base + path, data=data, method="POST",
                                     headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as r:
                body = r.read()
                try:
                    return json.loads(body or b"null")
                except ValueError:
                    return body.decode("utf-8", "replace")
        except urllib.error.URLError as e:
            raise WLEDError("POST %s failed: %s" % (path, e.reason))

    # -- reads ------------------------------------------------------------
    def info(self, refresh=False):
        if self._info is None or refresh:
            self._info = self._get("/json/info")
        return self._info

    def state(self):
        return self._get("/json/state")

    def cfg(self):
        return self._get("/json/cfg")

    @property
    def count(self):
        return int(self.info().get("leds", {}).get("count", 0))

    def describe(self):
        i = self.info(True)
        leds = i.get("leds", {})
        return ("%s  WLED %s on %s\n"
                "  %d LEDs, %s mA limit, %s fps reported\n"
                "  ip %s  mac %s  uptime %ss"
                % (i.get("name", "?"), i.get("ver", "?"), i.get("arch", "?"),
                   leds.get("count", 0), leds.get("maxpwr", "?"), leds.get("fps", "?"),
                   i.get("ip", "?"), i.get("mac", "?"), i.get("uptime", "?")))

    # -- writes -----------------------------------------------------------
    def buses(self):
        """The configured LED outputs, as (start, len, pin, order) tuples."""
        ins = self.cfg().get("hw", {}).get("led", {}).get("ins", [])
        return [(b.get("start"), b.get("len"),
                 (b.get("pin") or [None])[0], b.get("order")) for b in ins]

    def one_bus(self, count, pin=None, order=None, kind=None):
        """Collapse every LED output into a single bus of `count` LEDs.

        A stock Gledopto ships as 600+30+30+30 across four pins.  The
        helmet is one chain on one pin, so three of those are phantom:
        they eat addresses off the end of the stream and send them to
        pins with nothing attached.  Worse, a chain *longer* than the
        first bus runs off the end of it and looks like it just stops --
        which would quietly truncate a walk of the chain.

        Defaults for pin, colour order and LED type come from the bus
        that is already there, so this only changes the layout.
        """
        ins = self.cfg().get("hw", {}).get("led", {}).get("ins", [])
        b0 = ins[0] if ins else {}
        bus = {"start": 0, "len": int(count),
               "pin": [int(pin) if pin is not None else (b0.get("pin") or [16])[0]],
               "order": int(order) if order is not None else b0.get("order", 0),
               "type": int(kind) if kind is not None else b0.get("type", 22),
               "rev": False, "skip": 0, "ref": b0.get("ref", False)}
        self._post("/json/cfg", {"hw": {"led": {"total": int(count),
                                                "ins": [bus]}}})
        time.sleep(1.5)                       # the bus manager restarts
        self._info = None
        return bus

    MA_FOR_ESP = 100          # what WLED reserves for the board itself

    def power_limit(self, max_ma=None, ma_per_led=None):
        """Set the automatic brightness limiter on every output.

        WLED 0.15 keeps these per bus.  The top-level hw.led.maxpwr and
        hw.led.ledma are legacy and read 0 here, which looks like "no
        limit" but is not -- each bus carries its own pair, and the
        Gledopto ships with 260 mA at 55 mA/LED.  55 is the 5 V WS2812B
        figure, wrong for a 12 V WS2815, and 260 mA is about three LEDs
        of full white before the limiter starts scaling the whole frame.

        The limiter works off an *estimate*, not a measurement, so it is
        only as honest as ma_per_led.  It also charges 1 mA per declared
        LED of idle current before any light is produced, so declaring a
        longer chain than you have spends real budget.  ``headroom``
        does that arithmetic.
        """
        ins = self.cfg().get("hw", {}).get("led", {}).get("ins", [])
        out = []
        for b in ins:
            nb = dict(b)
            if max_ma is not None:
                nb["maxpwr"] = int(max_ma)
            if ma_per_led is not None:
                nb["ledma"] = int(ma_per_led)
            out.append(nb)
        self._post("/json/cfg", {"hw": {"led": {"ins": out}}})
        time.sleep(0.8)
        self._info = None
        return out

    def headroom(self):
        """How much light the limiter will actually allow, per bus.

        Returns one dict per bus with the budget after the board and
        idle-current deductions, and what that buys in LEDs of full
        white.  If `full_white_leds` is far below the bus length the
        limiter is the thing setting your brightness, not you.
        """
        ins = self.cfg().get("hw", {}).get("led", {}).get("ins", [])
        rows = []
        for b in ins:
            n = b.get("len", 0) or 0
            cap = b.get("maxpwr", 0) or 0
            per = b.get("ledma", 0) or 0
            budget = max(0, cap - self.MA_FOR_ESP // max(1, len(ins)))
            budget = max(0, budget - n)            # 1 mA/LED idle
            rows.append({
                "pin": (b.get("pin") or [None])[0], "len": n,
                "max_ma": cap, "ma_per_led": per,
                "usable_ma": budget,
                "full_white_leds": int(budget / per) if per else None,
                "fraction": (budget / (n * per)) if (n and per) else None,
            })
        return rows

    def realtime(self, on=True, brightness=None):
        """Make the controller accept and show live DDP, at full brightness.

        Without this a stream can arrive and be ignored, or be scaled down by
        whatever preset was last running -- which looks exactly like bad wiring.
        """
        body = {"on": True, "live": bool(on)}
        if brightness is not None:
            body["bri"] = int(brightness)
        return self._post("/json/state", body)

    def off(self):
        return self._post("/json/state", {"on": False})

    def set_brightness(self, b):
        return self._post("/json/state", {"bri": int(b)})


# --------------------------------------------------------------------------
class Pixels:
    """DDP output, with per-LED colour-order correction."""

    VER, PUSH = 0x40, 0x01

    def __init__(self, target, count=None, port=DDP_PORT, dest_id=1,
                 strips=None, guard=None):
        if isinstance(target, WLED):
            self.host = target.base.split("//", 1)[-1].split("/")[0].split(":")[0]
            count = count or target.count
        else:
            self.host = target
        if not count:
            raise WLEDError("LED count unknown -- pass count=, or let the "
                            "controller report it")
        self.count = int(count)
        self.addr = (self.host, int(port))
        self.dest_id = dest_id
        self.max_data = DDP_MAX_DATA - DDP_MAX_DATA % 3
        self.seq = 0
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.perm = np.tile(np.arange(3), (self.count, 1))     # identity
        if strips is False:                 # explicit opt-out
            pass
        elif strips:
            self.set_strips(strips)
        else:
            # Measured colour-order corrections, loaded here for the same
            # reason as the power guard: every frame goes through send(),
            # and a tool that forgot would render both ear rims green.
            _p = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                              "data", "cal", "strips.json")
            if os.path.exists(_p):
                try:
                    import json as _json
                    self.set_strips(_json.load(open(_p))["strips"])
                except (ValueError, KeyError, TypeError, WLEDError) as e:
                    # Say so: the symptom is green where red was asked
                    # for, which looks like a wiring fault, not a file.
                    import sys
                    print("mau5wled: %s could not be applied (%s) -- the ear "
                          "rims will show the wrong colours" % (_p, e),
                          file=sys.stderr)
        # Thermal clamp.  Loaded here rather than left to each caller,
        # because every frame reaching the helmet goes through send()
        # and a tool that forgot to apply it would melt hot glue.
        # A broken profile raises from here on purpose.  It used to be
        # caught and turned into "no guard", which is the one outcome
        # this exists to prevent.
        if guard is False:                  # explicit opt-out
            self.guard = None
        elif guard is not None:
            self.guard = guard
        else:
            import mau5power
            self.guard = mau5power.load(count=self.count)
        self.last_power = None
        self.last_sent = np.zeros((self.count, 3), np.uint8)

    # -- colour order -----------------------------------------------------
    def set_strips(self, strips):
        """strips: [{'start': i, 'count': n, 'order': 'RGB'}, ...]

        'order' is what the physical strip actually is, relative to whatever
        the WLED bus is configured as.  Leave a section out and it is assumed
        to match the bus.
        """
        self.perm = np.tile(np.arange(3), (self.count, 1))
        for s in strips:
            name = str(s.get("order", "RGB")).upper()
            if name not in ORDERS:
                raise WLEDError("unknown colour order %r" % name)
            a = int(s["start"])
            b = min(a + int(s["count"]), self.count)
            self.perm[a:b] = ORDERS[name]

    def apply_order(self, buf):
        return np.take_along_axis(np.asarray(buf, np.uint8), self.perm, axis=1)

    # -- sending ----------------------------------------------------------
    def send(self, buf, correct=True, gain=1.0):
        """buf: (count, 3) uint8 in true RGB.  Sent as one DDP frame.

        `gain` (at most 1) dims the frame after the guard -- a show's beat
        pulse, which the guard would otherwise flatten.
        """
        a = np.asarray(buf, np.uint8)
        if a.ndim == 1:
            a = a.reshape(-1, 3)
        if len(a) < self.count:
            a = np.vstack([a, np.zeros((self.count - len(a), 3), np.uint8)])
        a = a[:self.count]
        if self.guard is not None:
            a, self.last_power = self.guard.apply(a, gain=gain)
        elif gain < 1.0:
            a = (a * max(float(gain), 0.0)).astype(np.uint8)
        # What the helmet is actually showing, in true RGB -- after the
        # guard has had its say but before the per-strip colour-order
        # permutation, which is a property of the wiring and not of the
        # picture.  Anything drawing a preview wants this, not the frame
        # that was asked for.
        self.last_sent = a
        data = (self.apply_order(a) if correct else a).tobytes()

        self.seq = self.seq % 15 + 1
        off = 0
        while off < len(data):
            chunk = data[off:off + self.max_data]
            last = off + len(chunk) >= len(data)
            hdr = struct.pack(">BBBBIH", self.VER | (self.PUSH if last else 0),
                              self.seq, 0, self.dest_id, off, len(chunk))
            self.sock.sendto(hdr + chunk, self.addr)
            off += len(chunk)

    def blank(self):
        return np.zeros((self.count, 3), np.uint8)

    def clear(self):
        self.send(self.blank())

    def one(self, i, color=(255, 255, 255), correct=True):
        buf = self.blank()
        if 0 <= i < self.count:
            buf[i] = color
        self.send(buf, correct)

    def some(self, idx, color=(255, 255, 255), correct=True):
        buf = self.blank()
        idx = np.asarray(list(idx), int)
        if len(idx):
            buf[idx[(idx >= 0) & (idx < self.count)]] = color
        self.send(buf, correct)

    def all(self, color=(255, 255, 255), correct=True):
        buf = self.blank()
        buf[:] = color
        self.send(buf, correct)

    def hold(self, buf, seconds, fps=40, correct=True):
        """Keep sending a frame -- WLED drops back to its effect after ~2.5 s
        of silence, so a 'static' test pattern still has to be streamed."""
        end = time.monotonic() + seconds
        while time.monotonic() < end:
            self.send(buf, correct)
            time.sleep(1.0 / fps)

    def close(self):
        self.sock.close()



class Streamer:
    """Keeps retransmitting the current frame until told otherwise.

    WLED falls back to its own effect after about 2.5 s of DDP silence,
    so a "static" test pattern is not static -- it has to be sent the
    whole time it is meant to be on screen.  Any code that lights a
    pattern and then goes off to do something slow, such as waiting for
    a camera frame, photographs the fallback instead of the pattern and
    concludes the LEDs are dead.  That is a confusing failure, so the
    retransmit belongs in a thread rather than in each caller's loop.
    """

    def __init__(self, pix, fps=20):
        self.pix = pix
        self.period = 1.0 / float(fps)
        self._buf = np.zeros((pix.count, 3), np.uint8)
        self._lock = threading.Lock()
        self._stop = False
        self.last_power = None
        # A send that fails keeps failing quietly in a background thread,
        # and the helmet just goes back to its own effect.  So the last
        # failure is kept, counted, and reported the first time.
        self.errors = 0
        self.last_error = None
        self._t = threading.Thread(target=self._run, daemon=True)
        self._t.start()

    def show(self, buf):
        with self._lock:
            self._buf = np.asarray(buf, np.uint8).reshape(-1, 3).copy()

    def dark(self):
        self.show(np.zeros((self.pix.count, 3), np.uint8))

    def _run(self):
        while not self._stop:
            with self._lock:
                b = self._buf
            try:
                self.pix.send(b)
                self.last_power = self.pix.last_power
            except OSError as e:          # the network, not the program
                if not self.errors:
                    import sys
                    print("mau5wled: sending to %s failed (%s); still trying"
                          % (self.pix.host, e), file=sys.stderr)
                self.errors += 1
                self.last_error = e
            time.sleep(self.period)

    def stop(self):
        self._stop = True
        self._t.join(timeout=1.0)
        try:
            self.pix.clear()
            time.sleep(0.1)
            self.pix.clear()
        except Exception:
            pass


# --------------------------------------------------------------------------
def discover(timeout=2.0, hosts=("wled.local", "mau5head-wled.local",
                                 "mau5head.local")):
    """Try the usual mDNS names.  Returns every one that answers."""
    found = []
    for h in hosts:
        try:
            w = WLED(h, timeout=timeout)
            w.info()
            found.append(w)
        except Exception:
            pass
    return found


def _mask_bits(tok):
    """netmask as written by ifconfig (0xffffff00) or ip (/24) -> bit count."""
    tok = tok.strip()
    if tok.startswith("/"):
        tok = tok[1:]
    if tok.startswith("0x"):
        v = int(tok, 16)
    elif "." in tok:
        p = [int(x) for x in tok.split(".")]
        v = (p[0] << 24) | (p[1] << 16) | (p[2] << 8) | p[3]
    else:
        try:
            return int(tok)
        except ValueError:
            return None
    return bin(v).count("1")


def _default_iface():
    """Name of the interface carrying the default route, or None."""
    for cmd, pat in ((["route", "-n", "get", "default"], "interface:"),
                     (["ip", "route", "get", "8.8.8.8"], " dev ")):
        try:
            out = subprocess.run(cmd, capture_output=True, text=True,
                                 timeout=3).stdout
        except Exception:
            continue
        if pat == "interface:":
            for line in out.splitlines():
                if "interface:" in line:
                    return line.split(":", 1)[1].strip()
        else:
            parts = out.split()
            if "dev" in parts:
                return parts[parts.index("dev") + 1]
    return None


def local_nets():
    """Every IPv4 LAN this machine is really on, default route first.

    We do NOT ask the kernel which address it would use to reach the
    internet.  With a full-tunnel VPN up that answer is the tunnel -- a
    point-to-point /32 with no neighbours on it -- and both the subnet
    scan and the URL we hand the phone would be pointed into the void.

    A real LAN has a broadcast address; a tunnel does not.  That is the
    whole test.  Each entry is {"iface", "ip", "bits"}.
    """
    nets = []
    try:
        out = subprocess.run(["ifconfig"], capture_output=True, text=True,
                             timeout=5).stdout
    except Exception:
        out = ""
    iface = None
    for line in out.splitlines():
        if line[:1] not in (" ", "\t") and ":" in line:
            iface = line.split(":", 1)[0]
        f = line.split()
        if len(f) >= 2 and f[0] == "inet" and "broadcast" in f:
            bits = _mask_bits(f[f.index("netmask") + 1]) if "netmask" in f else 24
            nets.append({"iface": iface, "ip": f[1], "bits": bits or 24})
    if not nets:                                   # linux without ifconfig
        try:
            out = subprocess.run(["ip", "-4", "-o", "addr"], capture_output=True,
                                 text=True, timeout=5).stdout
        except Exception:
            out = ""
        for line in out.splitlines():
            f = line.split()
            if "inet" in f and "brd" in f:
                ip, _, m = f[f.index("inet") + 1].partition("/")
                nets.append({"iface": f[1], "ip": ip, "bits": _mask_bits(m) or 24})
    nets = [n for n in nets if not n["ip"].startswith("127.")]
    d = _default_iface()
    nets.sort(key=lambda n: (n["iface"] != d, n["ip"]))
    return nets


def lan_ip():
    """This machine's address on the LAN -- the one a phone can reach."""
    nets = local_nets()
    if nets:
        return nets[0]["ip"]
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"
    finally:
        s.close()


def _vpn_note():
    """A line about tunnels, for when a scan comes up empty."""
    try:
        out = subprocess.run(["ifconfig"], capture_output=True, text=True,
                             timeout=5).stdout
    except Exception:
        return ""
    tun = [l.split(":", 1)[0] for l in out.splitlines()
           if l[:1] not in (" ", "\t") and ":" in l
           and l.split(":", 1)[0].startswith(("utun", "ipsec", "ppp", "tun"))
           and "RUNNING" in l]
    if not tun:
        return ""
    return ("\n  A VPN looks active (%s).  Some VPNs route everything through\n"
            "  the tunnel and cut you off from your own LAN -- if the\n"
            "  controller is on wifi, try disconnecting the VPN."
            % ", ".join(tun[:3]))


def scan_subnet(timeout=0.9, workers=64, prefix=None, verbose=True):
    """Knock on every address of each LAN we are on and see who says WLED.

    Slower than mDNS but it works when mDNS does not, which on a phone
    hotspot is most of the time.
    """
    import concurrent.futures as cf
    if prefix is not None:
        prefixes = [prefix]
    else:
        prefixes = []
        for n in local_nets():
            p = ".".join(n["ip"].split(".")[:3])
            if p not in prefixes:
                prefixes.append(p)
            if n["bits"] < 24 and verbose:
                print("  (%s is a /%d -- only scanning %s.0/24)"
                      % (n["iface"], n["bits"], p))
        if not prefixes:
            return []

    def probe(host):
        try:
            w = WLED(host, timeout=timeout)
            i = w.info()
            if isinstance(i, dict) and "leds" in i:
                return w
        except Exception:
            pass
        return None

    found = []
    for p in prefixes:
        if verbose:
            print("scanning %s.1-254 for a controller ..." % p)
        hosts = ["%s.%d" % (p, n) for n in range(1, 255)]
        with cf.ThreadPoolExecutor(max_workers=workers) as ex:
            for r in ex.map(probe, hosts):
                if r is not None:
                    found.append(r)
                    if verbose:
                        print("  found %s" % r.describe().splitlines()[0])
        if found:
            break
    return found


def find_one(host=None, verbose=True):
    """Resolve a controller: given host, else mDNS, else a subnet scan."""
    if host:
        w = WLED(host)
        w.info()
        return w
    for w in discover():
        return w
    for w in scan_subnet(verbose=verbose):
        return w
    raise WLEDError(
        "no controller found.\n"
        "  Check that the ESP32 is powered and on the same network as this\n"
        "  machine, then pass its address explicitly:  --host 4.3.2.1\n"
        "  (the WLED app, or your router's client list, will show it)"
        + _vpn_note())


def _limit(w, a):
    """Apply --max-ma / --allow / --ma-per-led and report what it buys."""
    per = a.ma_per_led
    if per is None:
        ins = w.cfg().get("hw", {}).get("led", {}).get("ins", [])
        per = (ins[0].get("ledma") if ins else None) or 55
    if a.allow is not None:
        n = w.count or 0
        budget = int(n * per * a.allow) + n + w.MA_FOR_ESP
        print("allowing %.0f%% of full white across %d LEDs at %d mA/LED"
              % (a.allow * 100, n, per))
    else:
        budget = a.max_ma
    w.power_limit(max_ma=budget, ma_per_led=per)
    for r in w.headroom():
        print("  pin %s  %d LEDs  cap %d mA -> %d mA usable = %d LEDs of full "
              "white (%.0f%% of everything)"
              % (r["pin"], r["len"], r["max_ma"], r["usable_ma"],
                 r["full_white_leds"], r["fraction"] * 100))


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="poke the WLED controller")
    ap.add_argument("host", nargs="?", help="ip or hostname (default: try mDNS)")
    ap.add_argument("--count", type=int)
    ap.add_argument("--all", metavar="R,G,B", help="light every LED this colour")
    ap.add_argument("--one", type=int, metavar="N", help="light only LED N")
    ap.add_argument("--range", metavar="LO-HI",
                    help="light only LEDs LO..HI, for walking up to the "
                         "helmet and seeing which ones they are")
    ap.add_argument("--color", default="255,255,255")
    ap.add_argument("--seconds", type=float, default=5.0)
    ap.add_argument("--off", action="store_true")
    ap.add_argument("--one-bus", type=int, metavar="N",
                    help="reconfigure the controller as ONE output of N LEDs")
    ap.add_argument("--pin", type=int, help="data pin for --one-bus")
    ap.add_argument("--max-ma", type=int, metavar="MA",
                    help="automatic brightness limiter budget, in mA")
    ap.add_argument("--ma-per-led", type=int, metavar="MA",
                    help="per-LED current at full white the limiter assumes")
    ap.add_argument("--allow", type=float, metavar="F",
                    help="instead of --max-ma, allow this FRACTION of full "
                         "white (0-1) and work the budget out from the chain "
                         "length -- independent of whether --ma-per-led is "
                         "exactly right")
    a = ap.parse_args()

    w = find_one(a.host)
    print(w.describe())
    for st, ln, pin, order in w.buses():
        print("  bus: %4d..%-4d on pin %s, order %s"
              % (st, st + (ln or 0) - 1, pin, ORDER_NAMES.get(order, order)))

    if a.one_bus:
        print("\ncollapsing to a single bus of %d on pin %s ..."
              % (a.one_bus, a.pin if a.pin is not None else "(unchanged)"))
        w.one_bus(a.one_bus, a.pin)
        print(w.describe())
        for st, ln, pin, order in w.buses():
            print("  bus: %4d..%-4d on pin %s, order %s"
                  % (st, st + (ln or 0) - 1, pin, ORDER_NAMES.get(order, order)))
        if a.max_ma or a.allow or a.ma_per_led:
            _limit(w, a)
        sys.exit(0)

    if a.max_ma or a.allow or a.ma_per_led:
        _limit(w, a)
        sys.exit(0)

    if a.off:
        w.off()
        sys.exit(0)
    col = tuple(int(x) for x in a.color.split(","))
    if a.all or a.one is not None or a.range:
        w.realtime(True)
        p = Pixels(w, a.count)
        buf = p.blank()
        if a.range:
            lo, _, hi = a.range.partition("-")
            lo, hi = int(lo), int(hi or lo)
            if not 0 <= lo <= hi < p.count:
                sys.exit("--range must be inside 0..%d" % (p.count - 1))
            buf[lo:hi + 1] = col
            print("LEDs %d..%d -> %s for %.0f s" % (lo, hi, col, a.seconds))
        elif a.one is not None:
            buf[a.one] = col
            print("LED %d -> %s for %.0f s" % (a.one, col, a.seconds))
        else:
            buf[:] = tuple(int(x) for x in a.all.split(","))
            print("all %d LEDs -> %s for %.0f s" % (p.count, buf[0], a.seconds))
        p.hold(buf, a.seconds)
        p.clear()
