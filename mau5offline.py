#!/usr/bin/env python3
"""mau5offline -- the helmet with no network, no laptop and no router.

At a show there is no house WiFi worth trusting and no reason to carry
the laptop, so the helmet has to be its own network and its own server:
the phone joins the controller's access point, opens one page, and the
animations run.  That is what this builds, installs and checks.

Where the page has to live is forced, not chosen.  A browser cannot
send UDP, so DDP is out and the pixels have to go over the controller's
own HTTP API.  An https:// page cannot talk to a plain-http 192.168
address, so it cannot be hosted anywhere with a certificate, which
rules out GitHub Pages and with it the whole installable-PWA route.  A
plain-http page is not a secure context, so no service worker will
cache it -- the laptop cannot serve it either.  Exactly one HTTP server
is present on that network with nothing else running: the controller.
So the player is uploaded to the controller's own filesystem, where it
is same-origin with the API it drives and there is nothing to install
on the phone at all.  Any phone, any time, for as long as the helmet
boots.

    python3 mau5offline.py build            # make the page
    python3 mau5offline.py serve            # drive it against a fake helmet
    python3 mau5offline.py deploy --host X  # upload it, then read it back
    python3 mau5offline.py config --host X  # AP on, power limiter set
    python3 mau5offline.py check  --host X  # is offline mode actually there

`build` and `serve` need no hardware.  `deploy`, `config` and `check`
need to be on a network with the controller -- including its own.
"""

from __future__ import annotations

import argparse
import base64
import gzip
import io
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "remote", "offline")
OUT = os.path.join(HERE, "data", "offline")
CAL = os.path.join(HERE, "data", "cal")

PAGE = "mau5.htm"            # what it is called on the controller


# ----------------------------------------------------------------------
# the data bundle
# ----------------------------------------------------------------------
def _b64(a, dtype):
    return base64.b64encode(np.ascontiguousarray(a, dtype).tobytes()).decode()


def bundle():
    """Everything the page needs that is not code.

    The geometry is exported *derived* -- nfa, nel and the rest, as
    Helmet computes them -- rather than re-derived in JavaScript.  A
    second implementation of the map is a second thing to be wrong
    about the ears, and this one would be wrong on a phone at a show
    where nobody can debug it.  Ported code can disagree about colour;
    it cannot disagree about where an LED is.
    """
    import mau5engine as E
    from mau5fx import FONT5x7, SPRITES

    h = E.Helmet()
    runs = []
    for i, r in enumerate(h.region):
        if runs and runs[-1][2] == r:
            runs[-1][1] = i
        else:
            runs.append([i, i, str(r)])

    d = {
        "n": int(h.n),
        "f32": {k: _b64(v, "<f4") for k, v in {
            "px": h.px, "py": h.py, "depth": h.depth, "nx": h.nx, "ny": h.ny,
            "nfa": h.nfa, "nel": h.nel, "u": h.u, "fa": h.fa,
            "ea": h.ea, "er": h.er,
            "xyz": h.xyz.reshape(-1),
        }.items()},
        "i16": {"group": _b64(h.group, "<i2")},
        "regions": runs,
        "fonts": {
            "font": {k: list(v) for k, v in FONT5x7.items()},
            "digit3x5": {k: list(v) for k, v in E.DIGIT3x5.items()},
            "sprites": {k: list(v) for k, v in SPRITES.items()},
        },
        "power": json.load(open(os.path.join(CAL, "power.json"))),
        "strips": json.load(open(os.path.join(CAL, "strips.json")))["strips"],
        "presets": _preset_specs(),
        "built": time.strftime("%Y-%m-%d"),
    }
    return d


def _preset_specs():
    """Name, defaults and parameter kinds, so the page can build controls.

    Taken from the Python registry rather than written out again, so a
    preset that gains a parameter gains a slider without anyone
    remembering to add one.
    """
    import mau5engine as E
    out = {}
    for name in sorted(E.REGISTRY):
        cls = E.REGISTRY[name]
        out[name] = {"params": {k: (list(v) if isinstance(v, tuple) else v)
                                for k, v in cls.params.items()},
                     "spec": cls.spec()}
    return out


# ----------------------------------------------------------------------
# build
# ----------------------------------------------------------------------
def _read(name):
    with open(os.path.join(SRC, name)) as f:
        return f.read()


def build(verbose=True):
    os.makedirs(OUT, exist_ok=True)
    data = bundle()
    data_js = ("globalThis.MAU5_DATA = %s;\n"
               % json.dumps(data, separators=(",", ":")))
    with open(os.path.join(OUT, "data.js"), "w") as f:
        f.write(data_js)

    html = _read("player.html")
    parts = {"DATA": data_js}
    for js in ("engine.js", "guard.js", "wire.js", "audio.js", "ui.js"):
        parts[js.split(".")[0].upper()] = _read(js)
    missing = [k for k in re.findall(r"<!--@(\w+)-->", html) if k not in parts]
    if missing:
        raise SystemExit("player.html wants %s and the build has no such part"
                         % ", ".join(missing))
    page = re.sub(r"<!--@(\w+)-->", lambda m: parts[m.group(1)], html)

    # A page that reaches out to a CDN is a page that is blank at a
    # show.  Nothing may load from anywhere but the controller.
    for url in re.findall(r"""["'(](https?:)?//[^"')\s]+""", page):
        raise SystemExit("offline page references %s -- it must be self "
                         "contained" % url)

    plain = os.path.join(OUT, PAGE)
    with open(plain, "w") as f:
        f.write(page)
    raw = page.encode()
    # mtime 0: the same inputs must give the same bytes, or every build
    # looks like a change worth uploading.
    buf = io.BytesIO()
    with gzip.GzipFile(fileobj=buf, mode="wb", compresslevel=9, mtime=0) as g:
        g.write(raw)
    gz = buf.getvalue()
    with open(plain + ".gz", "wb") as f:
        f.write(gz)
    if verbose:
        print("%s   %6.1f kB" % (plain, len(raw) / 1024.0))
        print("%s   %6.1f kB  (what goes on the controller)"
              % (plain + ".gz", len(gz) / 1024.0))
        print("  %d presets, %d LEDs, budget %.0f mA"
              % (len(data["presets"]), data["n"], data["power"]["budget_ma"]))
    return plain, raw, gz


# ----------------------------------------------------------------------
# the controller
# ----------------------------------------------------------------------
def _find(host):
    import mau5wled
    if host:
        return mau5wled.WLED(host)
    found = mau5wled.scan_subnet()
    if not found:
        raise SystemExit(
            "no controller found.\n"
            "  On the house network it is found by scanning; on the helmet's\n"
            "  own access point it is at 4.3.2.1, so pass --host 4.3.2.1.")
    return found[0]


def _upload(w, path, data, ctype="text/html"):
    """WLED's own file manager: a multipart POST, path in the filename.

    Tries /upload and then /edit, because which of the two the file
    manager is mounted on has moved between releases and there is no
    way to tell from outside which build this is.
    """
    b = b"----mau5%d" % int(time.time())
    body = (b"--" + b + b"\r\nContent-Disposition: form-data; name=\"data\"; "
            b"filename=\"" + path.encode() + b"\"\r\n"
            b"Content-Type: " + ctype.encode() + b"\r\n\r\n" + data +
            b"\r\n--" + b + b"--\r\n")
    last = None
    for route in ("/upload", "/edit"):
        req = urllib.request.Request(
            w.base + route, data=body, method="POST",
            headers={"Content-Type":
                     "multipart/form-data; boundary=" + b.decode(),
                     "Content-Length": str(len(body))})
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.status
        except urllib.error.URLError as e:
            last = e
    raise SystemExit("neither /upload nor /edit accepted the file: %s\n"
                     "  If this build has no filesystem the page cannot live "
                     "on the controller;\n  `mau5fake.py --host <ip>` will "
                     "serve it from here instead, laptop and all." % last)


def _delete(w, path):
    """Remove a file, so a fallback does not leave a stale one behind."""
    body = ("path=" + path).encode()
    req = urllib.request.Request(
        w.base + "/edit", data=body, method="DELETE",
        headers={"Content-Type": "application/x-www-form-urlencoded"})
    try:
        urllib.request.urlopen(req, timeout=10)
    except urllib.error.URLError:
        pass


def deploy(host=None, gzipped=True, verbose=True):
    plain, raw, gz = build(verbose=False)
    w = _find(host)
    info = w.info(True)
    fs = info.get("fs") or {}
    body = gz if gzipped else raw
    name = "/" + PAGE + (".gz" if gzipped else "")
    free = (fs.get("t", 0) - fs.get("u", 0)) * 1024 if fs else None
    print("%s  WLED %s   filesystem %s"
          % (info.get("name", "?"), info.get("ver", "?"),
             "%d of %d kB used" % (fs.get("u", 0), fs.get("t", 0)) if fs
             else "not reported"))
    if free is not None and free < len(body) + 8192:
        raise SystemExit("only %.1f kB free on the controller and the page is "
                         "%.1f kB" % (free / 1024.0, len(body) / 1024.0))

    print("uploading %s  (%.1f kB)" % (name, len(body) / 1024.0))
    _upload(w, name, body)

    # Read it back.  Uploading is not the risky part -- whether the
    # controller serves a .gz under its plain name is, and that is a
    # property of the firmware build, not of anything here.  Better to
    # find out now than on the phone at a show.
    time.sleep(0.6)
    url = w.base + "/" + PAGE
    try:
        req = urllib.request.Request(url, headers={"Accept-Encoding": "gzip"})
        with urllib.request.urlopen(req, timeout=15) as r:
            got = r.read()
            enc = (r.headers.get("Content-Encoding") or "").lower()
    except urllib.error.URLError as e:
        raise SystemExit("uploaded, but %s does not answer: %s" % (url, e))
    if enc == "gzip":
        got = gzip.decompress(got)
    if got != raw:
        if gzipped:
            print("  the controller does not serve %s.gz under its plain name "
                  "-- falling back to the uncompressed page" % PAGE)
            _delete(w, "/" + PAGE + ".gz")
            return deploy(host, gzipped=False, verbose=verbose)
        raise SystemExit("read back %d bytes, expected %d -- the upload did "
                         "not land" % (len(got), len(raw)))
    print("verified: %s returns the %d-byte page" % (url, len(raw)))
    print("\n  on the helmet's access point that is  http://4.3.2.1/%s" % PAGE)
    return url


# ----------------------------------------------------------------------
# configuration: the two things offline mode needs that a show does not
# ----------------------------------------------------------------------
def bus_budgets(buses, total_ma, per_led_ma):
    """Spread one current budget over however many output buses there are.

    Measured on the helmet's own controller (WLED 0.15.4): the limiter
    that actually runs is the *per bus* one.  Writing the global
    ``hw.led.maxpwr`` changes ``info.leds.maxpwr`` and nothing else --
    asking for 1390 mA of white drew 1178 mA with the global set to
    700.  Moving the same number onto the bus clamps immediately and
    linearly, and the reported draw comes out at the cap less one
    milliamp per LED, which is WLED reserving the same standby figure
    ``mau5power`` uses.  So the cap to write is the budget *including*
    standby, and the firmware subtracts the standby itself.

    The global is written as well.  It is inert here but it is what
    older builds read, and a number that disagrees with the bus would
    be worse than one that is merely ignored.
    """
    out, n = [], sum(max(1, int(b.get("len") or 0)) for b in buses) or 1
    for b in buses:
        c = dict(b)
        c["maxpwr"] = int(round(total_ma * max(1, int(b.get("len") or 0)) / n))
        c["ledma"] = int(round(per_led_ma))
        out.append(c)
    return out


def wanted_cfg(power, ap_ssid=None, ap_psk=None, buses=None):
    """The configuration changes offline mode depends on.

    Two of them, and neither is cosmetic.

    The access point has to come up whether or not a known network is
    in range, because at a show none is, and `ap.behav` 0 only starts
    it when the join fails -- which it does, but a minute later and
    not at all if some open network happens to answer.

    The brightness limiter has to be set from the same budget the
    software guard uses.  On the house network the guard in Pixels.send
    is the only thing between a preset and 11.8 A, and that is fine
    because every frame goes through it.  Offline the frames come from
    a phone, and a limiter a browser tab can skip is not a limiter.
    WLED's own one runs on the controller, below anything the page can
    reach, so it is set to the same number and left there.
    """
    # WLED's limiter is pure current arithmetic and never learns the
    # supply voltage, so feeding it milliamps measured at 12 V is
    # consistent as long as ledma is too -- which is why both numbers
    # come from the same place the software guard reads.
    import mau5power
    ma = int(round(power["budget_ma"] + power["count"]
                   * mau5power.MA_PER_LED_STANDBY))
    led = {"maxpwr": ma, "ledma": int(round(mau5power.MA_PER_LED_FULL_WHITE))}
    if buses:
        led["ins"] = bus_budgets(buses, ma, mau5power.MA_PER_LED_FULL_WHITE)
    cfg = {"ap": {"behav": 2},        # 2 = always on, not only when lost
           "hw": {"led": led}}
    if ap_ssid:
        cfg["ap"]["ssid"] = ap_ssid
    if ap_psk:
        cfg["ap"]["psk"] = ap_psk
    return cfg


def _flat(d, p=""):
    out = {}
    for k, v in d.items():
        if isinstance(v, dict):
            out.update(_flat(v, p + k + "."))
        else:
            out[p + k] = v
    return out


def config(host=None, apply=False, ap_ssid=None, ap_psk=None):
    w = _find(host)
    power = json.load(open(os.path.join(CAL, "power.json")))
    cur = w.cfg()
    buses = ((cur.get("hw") or {}).get("led") or {}).get("ins") or []
    want = wanted_cfg(power, ap_ssid, ap_psk, buses)
    changes = []
    for i, b in enumerate(want["hw"]["led"].get("ins") or []):
        have = buses[i] if i < len(buses) else {}
        for k in ("maxpwr", "ledma"):
            if have.get(k) != b[k]:
                changes.append(("bus %d %s" % (i, k), have.get(k), b[k]))
    for k, v in _flat(want).items():
        if k.endswith(".ins"):
            continue
        # 0.15 keeps no global ledma: it accepts the write, stores
        # nothing and reads back 0 for ever.  Reporting that as an
        # outstanding change would mean `config` never came up clean.
        if k == "hw.led.ledma" and buses:
            continue
        if k.endswith(".psk"):
            changes.append((k, "(unchanged or unset)", "(set)"))
            continue
        node = cur
        for part in k.split(".")[:-1]:
            node = (node or {}).get(part) or {}
        have = node.get(k.split(".")[-1])
        if have != v:
            changes.append((k, have, v))
    if not changes:
        print("already configured for offline use")
        return 0
    print("%-16s %-22s %s" % ("setting", "now", "wanted"))
    for k, a, b in changes:
        print("  %-14s %-22s %s" % (k, a, b))
    print("\n  maxpwr is the budget plus standby, in mA at 12 V -- the same\n"
          "  number data/cal/power.json gives the software guard.  The bus\n"
          "  figure is the one WLED 0.15 enforces; the global is for older\n"
          "  builds and is inert here.")
    if not apply:
        print("\nnothing changed.  Re-run with --apply.")
        return 0
    w._post("/json/cfg", want)
    print("\napplied.")
    return 0


# ----------------------------------------------------------------------
# check
# ----------------------------------------------------------------------
def check(host=None):
    """Would the helmet work on its own, right now, with no laptop?"""
    plain, raw, gz = build(verbose=False)
    w = _find(host)
    info, cfg = w.info(True), w.cfg()
    power = json.load(open(os.path.join(CAL, "power.json")))
    buses = ((cfg.get("hw") or {}).get("led") or {}).get("ins") or []
    want = wanted_cfg(power, buses=buses)
    rows, bad = [], 0

    def row(ok, what, detail):
        nonlocal bad
        rows.append(("ok " if ok else "NO ", what, detail))
        if not ok:
            bad += 1

    ap = cfg.get("ap", {})
    row(ap.get("behav") == 2, "access point always on",
        "ap.behav = %s" % ap.get("behav"))
    row(bool(ap.get("ssid")), "access point has a name",
        "ap.ssid = %r" % ap.get("ssid"))
    # Only the length comes back, never the password, so this cannot
    # tell a chosen one from WLED's own default -- which is also eight
    # characters.  It catches an open access point and nothing else.
    row(int(ap.get("pskl") or 0) >= 8, "access point has a password",
        "%s characters (length only; set yours with --ap-psk)"
        % (ap.get("pskl") or 0))

    # The bus is what 0.15 enforces -- see bus_budgets.  Checking the
    # global instead passed on a helmet whose real limiter was 1800.
    wl = want["hw"]["led"]
    wb = wl.get("ins") or []
    cap = sum(int(b.get("maxpwr") or 0) for b in buses)
    # Measured, not assumed: WLED's estimator does not count pixels
    # painted into a frozen segment, so the limiter it drives does not
    # clamp them either -- /json/info reports a flat idle 120 mA while
    # the page is painting a full rainbow.  The cap is still worth
    # setting, because it does cover everything the controller renders
    # itself, which is what a stray tap in WLED's own UI produces.  It
    # is not what keeps the phone honest; the guard in the page is.
    row(bool(wb) and all(buses[i].get("maxpwr") == b["maxpwr"]
                         for i, b in enumerate(wb)),
        "limiter set, for WLED's own effects",
        "bus caps total %s mA, wanted %s" % (cap, wl["maxpwr"]))
    row(bool(wb) and all(int(buses[i].get("ledma") or 0) == b["ledma"]
                         for i, b in enumerate(wb)),
        "limiter knows the per-LED current",
        "ledma %s mA, wanted %s"
        % ([b.get("ledma") for b in buses], wl["ledma"]))

    try:
        with urllib.request.urlopen(w.base + "/" + PAGE, timeout=10) as r:
            got = r.read()
            if (r.headers.get("Content-Encoding") or "").lower() == "gzip":
                got = gzip.decompress(got)
    except urllib.error.URLError:
        got = b""
    row(got == raw, "player page installed and current",
        "%d bytes on the controller, %d built" % (len(got), len(raw)))

    row(int(info.get("leds", {}).get("count") or 0) == power["count"],
        "controller agrees about the LED count",
        "%s, map has %d" % (info.get("leds", {}).get("count"), power["count"]))

    print("%s  WLED %s\n" % (info.get("name", "?"), info.get("ver", "?")))
    for ok, what, detail in rows:
        print("  %s %-38s %s" % (ok, what, detail))
    if bad:
        print("\n%d of %d not ready.  `config --apply` fixes the settings, "
              "`deploy` the page." % (bad, len(rows)))
    else:
        print("\noffline mode is ready: join the access point and open\n"
              "  http://4.3.2.1/%s" % PAGE)
    return 1 if bad else 0


# ----------------------------------------------------------------------
def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd")

    sub.add_parser("build", help="write the page, no hardware needed")

    s = sub.add_parser("serve", help="serve it against a fake controller")
    s.add_argument("--port", type=int, default=8770)
    s.add_argument("--host", default=None,
                   help="forward the JSON API to a real controller instead "
                        "of the fake one, for a dress rehearsal")

    s = sub.add_parser("deploy", help="upload the page to the controller")
    s.add_argument("--host", default=None)
    s.add_argument("--no-gzip", dest="gzip", action="store_false", default=True)

    s = sub.add_parser("config", help="AP and power limiter")
    s.add_argument("--host", default=None)
    s.add_argument("--apply", action="store_true")
    s.add_argument("--ap-ssid", default=None)
    s.add_argument("--ap-psk", default=None,
                   help="at least 8 characters; not stored in this repo")

    s = sub.add_parser("check", help="is offline mode actually ready")
    s.add_argument("--host", default=None)

    a = ap.parse_args(argv)
    if a.cmd in (None, "build"):
        build()
        return 0
    if a.cmd == "serve":
        import mau5fake
        return mau5fake.serve(port=a.port, host=a.host)
    # Being away from the helmet is the normal case for most of this
    # work, not an exception, so it reads as a sentence rather than a
    # traceback.
    import mau5wled
    try:
        if a.cmd == "deploy":
            deploy(a.host, gzipped=a.gzip)
            return 0
        if a.cmd == "config":
            return config(a.host, a.apply, a.ap_ssid, a.ap_psk)
        if a.cmd == "check":
            return check(a.host)
    except mau5wled.WLEDError as e:
        print(e)
        print("\n  `python3 mau5offline.py build` and `serve` need no helmet; "
              "this does.")
        return 1
    ap.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
