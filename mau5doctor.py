#!/usr/bin/env python3
"""mau5doctor -- check the whole rig in one command.

Answers the question you actually have before a show: is this going to
work, and if not, which part is wrong.  Checks the things that have
bitten before -- a power profile that went missing, a colour correction
pointing at the wrong span, a show whose track got renamed, a VPN
hiding the controller -- and says plainly which it is.

    python3 mau5doctor.py              # everything, including the helmet
    python3 mau5doctor.py --offline    # skip anything needing the network
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))

OK, WARN, BAD = "ok", "warn", "FAIL"
RESULTS = []


def say(level, area, msg, fix=None):
    RESULTS.append((level, area, msg, fix))


def _env():
    import numpy
    say(OK if sys.version_info >= (3, 8) else BAD, "python",
        "%d.%d.%d, numpy %s" % (sys.version_info[:3] + (numpy.__version__,)))
    import shutil
    for tool, why in (("ffmpeg", "previews and time-lapses"),
                      ("afconvert", "decoding mp3 for analysis")):
        if shutil.which(tool):
            say(OK, "tools", "%s present" % tool)
        else:
            say(WARN, "tools", "%s missing (%s)" % (tool, why))


def _map():
    import mau5map
    try:
        rows = mau5map.load()
    except Exception as e:
        return say(BAD, "map", "cannot load pixel map: %s" % e,
                   "python3 mau5map.py")
    n = len(rows)
    import collections
    src = collections.Counter(r["source"] for r in rows)
    say(OK if n == mau5map.TOTAL_N else BAD, "map",
        "%d LEDs: %s" % (n, ", ".join("%d %s" % (v, k) for k, v in sorted(src.items()))))
    other = {k: v for k, v in src.items() if k not in ("cad-slot", "cad-ear")}
    if other:
        say(WARN, "map", "%d LEDs not placed from the CAD (%s)"
            % (sum(other.values()), ", ".join(sorted(other))),
            "python3 mau5locate.py && python3 mau5slots.py")
    sw = [r["index"] for r in rows if r["swap_rg"]]
    if sw:
        say(OK, "map", "colour swap marked on %d..%d (%d LEDs)"
            % (min(sw), max(sw), len(sw)))
    else:
        say(WARN, "map", "no colour swap marked -- the ear rims will read green")


def _power():
    import mau5power as P
    # Asked of the file, not of load(): load() now answers a missing
    # profile with a deliberately timid guard rather than None, so the
    # old `g is None` test could never fire and a lost power.json
    # passed here as "ok budget 300 mA" -- a dull helmet with nothing
    # saying why.
    if not os.path.exists(P.DEFAULT):
        return say(BAD, "power", "no profile at data/cal/power.json -- every "
                   "tool is on the timid fallback (ceiling 32/255, 300 mA)",
                   "git checkout -- data/cal/power.json")
    g = P.load()
    worst = g.budget_ma + g.standby_ma() + 100
    say(OK if worst < 5000 else BAD, "power",
        "budget %.0f mA + %.0f standby -> %.2f A worst case (board takes 5 A)"
        % (g.budget_ma, g.standby_ma(), worst / 1000.0))
    th = getattr(g, "thermal", None)
    if th is None:
        say(WARN, "power", "no thermal budget -- brightness is capped per "
                           "frame but not rationed over time")
    else:
        burst = th.burst_j / max((th.max_w or 0) - th.sustained_w, 0.1)
        say(OK, "power", "thermal: %.1f W sustained, bursts to %.1f W for "
            "about %.0f s, bucket %.0f%% full"
            % (th.sustained_w, th.max_w or 0, burst, th.state()["full_pct"]))
    say(WARN, "power",
        "standby alone is %.1f W and no setting reduces it"
        % (g.standby_ma() * 12 / 1000.0),
        "it is the WS2815 ICs, live whenever 12 V is -- a switch on the "
        "strip's 12 V gated by GPIO 18 is the only thing that removes it")
    import numpy as np
    out, rep = g.apply(np.full((g.count, 3), 255, np.uint8))
    say(OK if rep["sent_ma"] <= g.budget_ma + 1 else BAD, "power",
        "all-white clamps %.0f -> %.0f mA" % (rep["asked_ma"], rep["sent_ma"]))


def _colour():
    import mau5map, mau5wled, numpy as np
    n = mau5map.TOTAL_N
    p = mau5wled.Pixels("127.0.0.1", n)
    sw = np.flatnonzero(p.perm[:, 0] == 1)
    if not len(sw):
        return say(WARN, "colour", "no correction loaded")
    say(OK, "colour", "R/G swap on %d..%d (%d LEDs)" % (sw.min(), sw.max(), len(sw)))
    buf = np.zeros((n, 3), np.uint8); buf[sw[0]] = (200, 0, 0)
    got = tuple(int(v) for v in p.apply_order(buf)[sw[0]])
    say(OK if got == (0, 200, 0) else BAD, "colour",
        "red into a rim leaves as %s" % (got,))


def _presets():
    import mau5engine as E
    h = E.Helmet()
    bad = []
    for name, cls in E.REGISTRY.items():
        try:
            out = cls().render(h, 1.7)
            import numpy as np
            if not np.isfinite(out).all() or out.max() > 255.001 or out.min() < -1e-6:
                bad.append(name)
        except Exception as e:
            bad.append("%s (%s)" % (name, type(e).__name__))
    say(OK if not bad else BAD, "presets",
        "%d presets, %d broken %s" % (len(E.REGISTRY), len(bad), bad or ""))


def _shows():
    import mau5show
    if not os.path.isdir(mau5show.SHOWS):
        return say(WARN, "shows", "no shows directory")
    js = [f for f in os.listdir(mau5show.SHOWS) if f.endswith(".json")]
    if not js:
        return say(WARN, "shows", "no shows built",
                   'python3 mau5show.py build "your track.mp3"')
    import mau5engine as E
    for f in sorted(js):
        s = json.load(open(os.path.join(mau5show.SHOWS, f)))
        probs = []
        if not os.path.exists(os.path.join(HERE, s["track"])):
            probs.append("track %r missing" % s["track"])
        unknown = sorted({c["preset"] for c in s["cues"]} - set(E.REGISTRY))
        if unknown:
            probs.append("unknown presets %s" % unknown)
        cache = s.get("analysis")
        if cache and not os.path.exists(os.path.join(mau5show.SHOWS, cache)):
            probs.append("analysis cache missing (will re-analyse, ~2 s)")
        lvl = OK if not probs else (WARN if "cache" in str(probs) else BAD)
        say(lvl, "shows", "%s: %.0f s, %.0f bpm, %d cues%s"
            % (f[:38], s["duration"], s["bpm"], len(s["cues"]),
               "  -- " + "; ".join(probs) if probs else ""))


def _network(timeout):
    import mau5wled
    nets = mau5wled.local_nets()
    if not nets:
        return say(BAD, "network", "no LAN interface found")
    say(OK, "network", "on %s via %s (lan_ip %s)"
        % (".".join(nets[0]["ip"].split(".")[:3]) + ".0/24",
           nets[0]["iface"], mau5wled.lan_ip()))
    try:
        import subprocess
        out = subprocess.run(["ifconfig"], capture_output=True, text=True,
                             timeout=4).stdout
        tun = [l.split(":")[0] for l in out.splitlines()
               if l[:1] not in (" ", "\t") and ":" in l
               and l.split(":")[0].startswith(("utun", "ppp", "tun"))
               and "RUNNING" in l]
        if tun:
            say(WARN, "network", "VPN tunnels up (%s)" % ", ".join(tun[:3]),
                "harmless now, but it is why discovery once scanned the wrong subnet")
    except Exception:
        pass

    t0 = time.time()
    try:
        w = mau5wled.find_one(verbose=False)
    except Exception as e:
        return say(WARN, "helmet", "not found in %.0f s (%s)"
                   % (time.time() - t0, type(e).__name__),
                   "power it on, or it is simply unplugged")
    info = w.info()
    say(OK, "helmet", "%s at %s, WLED %s, uptime %ds"
        % (info.get("name"), info.get("ip"), info.get("ver"),
           info.get("uptime", 0)))
    _helmet(w, info)


def _helmet(w, info):
    """The controller's own settings: LED count, buses, limiter."""
    import mau5map, mau5offline
    ip = info.get("ip")
    # The map has 621 and the controller is left driving 622 on
    # purpose (mau5map.TOTAL_N).  This used to want 623 and offer
    # `mau5wled.py --one-bus 623 --allow 0.3`, which also rewrote the
    # bus limiter to 4274 mA -- the only clamp on WLED's own effects,
    # at four times what the helmet can sustain.  So the fix offered
    # here only lays out the bus, and the limiter always comes from
    # mau5offline, which takes it from data/cal/power.json.
    n = w.count
    say(OK if mau5offline.count_agrees(n, mau5map.TOTAL_N) else WARN, "helmet",
        "%d LEDs configured (map has %d)" % (n, mau5map.TOTAL_N),
        None if mau5offline.count_agrees(n, mau5map.TOTAL_N) else
        "python3 mau5wled.py %s --one-bus %d --pin 16, then "
        "python3 mau5offline.py config --host %s --apply"
        % (ip, mau5map.TOTAL_N, ip))
    buses = w.buses()
    say(OK if len(buses) == 1 else WARN, "helmet",
        "%d output bus%s" % (len(buses), "" if len(buses) == 1 else "es"),
        None if len(buses) == 1 else "collapse to one, or addresses go to empty pins")
    _limiter(w, ip)


def _limiter(w, ip):
    """Is WLED's own limiter where data/cal/power.json puts it?

    Compared against exactly what `mau5offline.py config` would write,
    and never with a fix of its own: the only thing this ever suggests
    is that command, so it cannot recommend a higher limiter than the
    profile allows.  Above is a failure -- it is the one clamp on
    standby, boot and the hand-back, and WLED cannot ration over time.
    """
    import mau5offline
    path = os.path.join(HERE, "data", "cal", "power.json")
    if not os.path.exists(path):
        return say(WARN, "helmet", "limiter not checked: no power profile")
    power = json.load(open(path))
    ins = ((w.cfg().get("hw") or {}).get("led") or {}).get("ins") or []
    want = mau5offline.wanted_cfg(power, buses=ins)["hw"]["led"].get("ins") or []
    fix = "python3 mau5offline.py config --host %s --apply" % ip
    if not ins:
        return say(WARN, "helmet", "no output buses reported, so the limiter "
                   "could not be checked", fix)
    for r, b, wb in zip(w.headroom(), ins, want):
        cap, per = int(b.get("maxpwr") or 0), int(b.get("ledma") or 0)
        if per == 255:
            per = 12        # WLED's "WS2815 mode": it assumes 12 mA a LED
        what = ("limiter: %d mA at %d mA/LED -> %d%% of full white (profile "
                "wants %d mA at %d)" % (r["max_ma"], r["ma_per_led"],
                                         (r["fraction"] or 0) * 100,
                                         wb["maxpwr"], wb["ledma"]))
        # WLED skips the limiter entirely below its board reserve or at
        # 0 mA per LED -- that reads as a number and limits nothing.
        if cap < w.MA_FOR_ESP // max(1, len(ins)) or per <= 0:
            say(BAD, "helmet", what + " -- the limiter is OFF", fix)
        elif cap > wb["maxpwr"]:
            say(BAD, "helmet", what + " -- above what the helmet can sustain",
                fix)
        elif per < wb["ledma"]:
            # A smaller per-LED figure makes WLED underestimate the
            # current, which lets more through than the cap says.
            say(BAD, "helmet", what + " -- per-LED current set too low", fix)
        elif cap < wb["maxpwr"] or per != wb["ledma"]:
            # Safe, so no command: whether to loosen it is a decision,
            # not a fix.
            say(WARN, "helmet", what + " -- tighter than the profile; WLED's "
                "own effects will be dimmer than intended")
        else:
            say(OK, "helmet", what)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter,
                                 epilog=__doc__)
    ap.add_argument("--offline", action="store_true", help="skip the network")
    ap.add_argument("--timeout", type=float, default=8.0)
    a = ap.parse_args()

    for fn in (_env, _map, _power, _colour, _presets, _shows):
        try:
            fn()
        except Exception as e:
            say(BAD, fn.__name__.strip("_"), "check itself failed: %s: %s"
                % (type(e).__name__, e))
    if not a.offline:
        try:
            _network(a.timeout)
        except Exception as e:
            say(BAD, "network", "check failed: %s" % e)

    width = max(len(r[1]) for r in RESULTS)
    for lvl, area, msg, fix in RESULTS:
        mark = {OK: "  ok  ", WARN: " warn ", BAD: " FAIL "}[lvl]
        print("%s %-*s  %s" % (mark, width, area, msg))
        if fix:
            print("%s %-*s    -> %s" % ("      ", width, "", fix))
    n_bad = sum(1 for r in RESULTS if r[0] == BAD)
    n_warn = sum(1 for r in RESULTS if r[0] == WARN)
    print("\n%d checks, %d failed, %d warnings"
          % (len(RESULTS), n_bad, n_warn))
    sys.exit(1 if n_bad else 0)


if __name__ == "__main__":
    main()
