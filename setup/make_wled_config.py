#!/usr/bin/env python3
"""Generate the WLED config JSON for the mau5head's controller.

    ./setup/make_wled_config.py                 # writes setup/wled_config.json
    ./setup/make_wled_config.py --print         # just show it
    ./setup/make_wled_config.py --push          # POST it straight to the ESP32

Import the file by hand at:  http://<controller>/settings/sec  ->  Restore.
WLED merges what it finds, so the keys not listed here keep their current
values.  Re-running is safe: the output depends only on helmet.toml.

Everything comes from helmet.toml -- LED counts, GPIO pins, the static IP,
the ABL limit -- so this file and the sequences can never disagree.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import mau5cfg                                             # noqa: E402

# WLED enum values, from wled00/const.h
COLOR_ORDER = {"GRB": 0, "RGB": 1, "BRG": 2, "RBG": 3, "BGR": 4, "GBR": 5}
TYPE_WS281X = 22            # WS2812 / WS2813 / WS2815 all speak the same protocol
WS281X_US_PER_LED = 30.0    # 24 bits at 800 kHz


def ip(s):
    return [int(p) for p in str(s).split(".")]


def build(helmet):
    cfg = helmet.cfg
    c = cfg["controller"]
    p = cfg["player"]
    order = COLOR_ORDER[cfg["show"].get("color_order", "GRB").upper()]

    ins = []
    for o in helmet.outputs:
        ins.append({
            "start": o.start,
            "len": o.count,
            "pin": [o.gpio],
            "order": order,
            "rev": False,
            "skip": 0,
            "type": TYPE_WS281X,
            "ref": False,
            "rgbwm": 0,
            "freq": 0,
        })

    return {
        "id": {"mdns": c.get("name", "mau5head-wled"),
               "name": c.get("name", "mau5head"),
               "inv": "mau5head"},
        "nw": {"ins": [{
            "ssid": p.get("ssid", "mau5head"),
            "pskl": 0,
            "ip": ip(c["ip"]),
            "gw": ip(c.get("gateway", p.get("host", "192.168.4.1"))),
            "sn": ip(c.get("netmask", "255.255.255.0")),
        }]},
        "ap": {"ssid": "mau5head-AP", "pskl": 8, "chan": 1, "hide": 0,
               "behav": 2, "ip": [4, 3, 2, 1]},          # behav 2 = never
        "wifi": {"sleep": False},                        # latency over power
        "hw": {"led": {
            "total": helmet.n_total,
            "maxpwr": int(float(c.get("abl_amps", 8.0)) * 1000),   # mA
            "ledma": 0,                                  # estimate per LED
            "cct": False,
            "ins": ins,
        }},
        "light": {
            "scale-bri": 100,
            "pal-mode": 0,
            "gc": {"bri": 1.0, "col": 1.0},              # no gamma: shows are authored
            "aseg": False,
        },
        "def": {"bri": int(c.get("brightness", 255)), "on": True, "ps": -1},
        "if": {
            "live": {
                "en": True,          # realtime in: E1.31 / ArtNet / DDP (UDP 4048)
                "mso": False,
                "port": 5568,
                "mc": False,
                "dmx": {"uni": 1, "seqskip": False, "e131prio": 0,
                        "addr": 1, "dss": 0, "mode": 4},
                "timeout": 100,      # x100 ms before falling back to an effect
                "maxbri": False,
                "no-gc": True,       # do not gamma-correct live pixels
                "offset": 0,
            },
            "va": {"alexa": False},
            "sync": {"port0": 21324, "port1": 65506,
                     "recv": {"bri": False, "col": False, "fx": False},
                     "send": {"dir": False, "btn": False, "va": False,
                              "hue": False, "macro": False, "twice": False}},
        },
        "ol": {"clock": 0, "cntdwn": False},
        "timers": {"cntdwn": {"goal": [20, 1, 1, 0, 0, 0], "macro": 0}, "ins": []},
    }


def refresh_report(helmet):
    """Say plainly whether each output can keep up with the show's frame rate."""
    budget_ms = 1000.0 / helmet.fps
    lines = ["refresh budget at %d fps is %.1f ms per frame:" % (helmet.fps, budget_ms)]
    bad = False
    for o in helmet.outputs:
        need = o.count * WS281X_US_PER_LED / 1000.0
        ok = need <= budget_ms
        bad |= not ok
        lines.append("  output %-2s %4d LEDs -> %5.1f ms  %s"
                     % (o.name, o.count, need,
                        "ok" if ok else "OVER BUDGET, will refresh slower than the show"))
    amps = helmet.n_total * 0.0192           # WS2815 full white, 12 V, per LED
    limit = float(helmet.cfg["controller"].get("abl_amps", 8.0))
    lines.append("full-white draw would be ~%.1f A at %s V; ABL caps it at %.1f A, "
                 "so global brightness tops out near %d%%"
                 % (amps, helmet.cfg["controller"].get("psu_volts", 12), limit,
                    min(100, int(100 * limit / max(amps, 1e-6)))))
    return "\n".join(lines), bad


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter,
                                 epilog=__doc__)
    ap.add_argument("--config", default=mau5cfg.DEFAULT_CONFIG)
    ap.add_argument("--out", default=os.path.join(os.path.dirname(
        os.path.abspath(__file__)), "wled_config.json"))
    ap.add_argument("--print", dest="show", action="store_true")
    ap.add_argument("--push", action="store_true",
                    help="POST to http://<controller>/json/cfg")
    a = ap.parse_args()

    helmet = mau5cfg.load(a.config, quiet=True)
    cfg = build(helmet)
    text = json.dumps(cfg, indent=2)

    if a.show:
        print(text)
    else:
        with open(a.out, "w", encoding="utf-8") as fh:
            fh.write(text + "\n")
        print("wrote %s" % a.out)

    print()
    print(helmet.describe())
    print()
    report, bad = refresh_report(helmet)
    print(report)
    if bad:
        print("  -> see the commented third output in helmet.toml", file=sys.stderr)

    print()
    print("matching FPP setup, run on the Pi:")
    print("  sudo bash fpp_setup.sh --apply \\\n"
          "    --ssid %s --controller-ip %s --channels %d --fps %d"
          % (helmet.cfg["player"].get("ssid", "mau5head"),
             helmet.cfg["controller"]["ip"], helmet.channel_count, helmet.fps))

    if a.push:
        url = "http://%s/json/cfg" % helmet.cfg["controller"]["ip"]
        req = urllib.request.Request(url, data=text.encode(), method="POST",
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=15) as r:
            print("\nPOST %s -> %d %s" % (url, r.status,
                                          r.read()[:200].decode("utf-8", "replace")))
        print("the controller reboots after a config change; give it ~10 s")


if __name__ == "__main__":
    main()
