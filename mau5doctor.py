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
    g = P.load()
    if g is None:
        return say(BAD, "power", "no profile at data/cal/power.json",
                   "the helmet overheats without one; every tool refuses to run")
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
    import mau5wled, numpy as np
    p = mau5wled.Pixels("127.0.0.1", 623)
    sw = np.flatnonzero(p.perm[:, 0] == 1)
    if not len(sw):
        return say(WARN, "colour", "no correction loaded")
    say(OK, "colour", "R/G swap on %d..%d (%d LEDs)" % (sw.min(), sw.max(), len(sw)))
    buf = np.zeros((623, 3), np.uint8); buf[sw[0]] = (200, 0, 0)
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
    n = w.count
    say(OK if n == 623 else WARN, "helmet", "%d LEDs configured" % n,
        None if n == 623 else
        "python3 mau5wled.py %s --one-bus 623 --pin 16 --allow 0.3 --ma-per-led 19"
        % info.get("ip"))
    buses = w.buses()
    say(OK if len(buses) == 1 else WARN, "helmet",
        "%d output bus%s" % (len(buses), "" if len(buses) == 1 else "es"),
        None if len(buses) == 1 else "collapse to one, or addresses go to empty pins")
    for r in w.headroom():
        lvl = OK if (r["fraction"] or 0) < 0.6 and r["usable_ma"] > 0 else WARN
        say(lvl, "helmet", "limiter: %d mA at %d mA/LED -> %d%% of full white"
            % (r["max_ma"], r["ma_per_led"], (r["fraction"] or 0) * 100))


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
