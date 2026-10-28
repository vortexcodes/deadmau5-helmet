#!/usr/bin/env python3
"""mau5psu -- find the current at which the helmet stops being stable.

The power budget was set from what the LEDs and the hot glue can take
and from the supply's nameplate.  Neither says anything about what the
wiring, the connectors and the supply actually manage together, and
that is the number that matters: the failure is not a trip, it is the
controller browning out and the helmet going dark mid-show.

So ask the helmet to draw more and more, in small steps, and watch for
the first step it cannot hold.  Three things count as a failure:

  the board stops answering          -- it reset, or the supply folded
  its uptime goes backwards          -- it reset and came back
  the camera gets darker, not lighter-- the LEDs browned out while the
                                        board stayed up, which is what
                                        "only the ears stayed on" is

Every step ramps rather than jumps.  Six hundred LEDs going from dark
to full in one frame is an inrush the supply sees as a fault, and the
test should measure the helmet's steady draw, not its step response.

    python3 mau5psu.py                      # ramp to the first failure
    python3 mau5psu.py --ceiling 1200 --hold 6
"""

from __future__ import annotations

import argparse
import json
import os
import time
import urllib.request

import numpy as np
from PIL import Image

import mau5eye
import mau5power
import mau5wled

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "data", "cal", "psu")

MA_PER_LED = mau5power.MA_PER_LED_FULL_WHITE
STANDBY_PER_LED = mau5power.MA_PER_LED_STANDBY


def level_for(ma, count):
    """Per-channel 0-255 white level that asks for about `ma` of LED current."""
    return int(round(np.clip(ma / (count * MA_PER_LED) * 255.0, 0, 255)))


class Watch:
    """Is the controller still there, and has it restarted?"""

    def __init__(self, host):
        self.host = host
        self.last_uptime = None
        self.resets = 0

    def poll(self):
        try:
            d = json.load(urllib.request.urlopen(
                "http://%s/json/info" % self.host, timeout=3))
        except Exception as e:
            return False, "unreachable (%s)" % type(e).__name__
        up = d.get("uptime")
        note = ""
        if self.last_uptime is not None and up is not None and up < self.last_uptime:
            self.resets += 1
            note = "RESET (uptime %s -> %s)" % (self.last_uptime, up)
        self.last_uptime = up
        return (note == ""), note


def brightness_of(path, dark):
    a = np.asarray(Image.open(path).convert("L"), np.float32)
    return float(np.clip(a - dark, 0, 255).mean())


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--host", default=None)
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--eye-port", type=int, default=8752)
    ap.add_argument("--start", type=float, default=100.0, help="mA of LED current")
    ap.add_argument("--step", type=float, default=100.0)
    ap.add_argument("--ceiling", type=float, default=1500.0,
                    help="never ask for more than this, whatever happens")
    ap.add_argument("--hold", type=float, default=5.0,
                    help="seconds at each step before judging it")
    ap.add_argument("--ramp", type=float, default=1.2,
                    help="seconds to climb into each step")
    ap.add_argument("--no-camera", action="store_true")
    ap.add_argument("--jump", action="store_true",
                    help="test the step instead of the steady draw: go from "
                         "dark straight to each level in one frame")
    a = ap.parse_args(argv)
    os.makedirs(a.out, exist_ok=True)

    w = mau5wled.WLED(a.host) if a.host else (mau5wled.scan_subnet() or [None])[0]
    if w is None:
        raise SystemExit("no controller found")
    host = w.base.split("//", 1)[-1]
    w.realtime(True, brightness=255)
    count = w.count or 622
    # The guard is deliberately out of the way: its whole job is to stop
    # the helmet reaching these levels, and the point here is to find
    # out where they actually are.  --ceiling is the hard stop instead.
    pix = mau5wled.Pixels(w, count, guard=False)
    stream = mau5wled.Streamer(pix, fps=30)
    watch = Watch(host)
    watch.poll()

    dark_mean = 0.0
    if not a.no_camera:
        stream.dark(); time.sleep(0.6)
        p = mau5eye.shot(os.path.join(a.out, "dark.jpg"), port=a.eye_port,
                         after=time.time())
        dark_mean = float(np.asarray(Image.open(p).convert("L"), np.float32).mean())

    rows, best, failed = [], 0.0, None
    cur = 0.0
    target = a.start
    try:
        while target <= a.ceiling:
            lvl = level_for(target, count)
            if a.jump:
                # dark, settle, then the whole load in a single frame --
                # which is what a power-on, or a cut to a bright preset,
                # actually does to the supply
                stream.dark()
                time.sleep(1.5)
                stream.show(np.full((count, 3), lvl, np.uint8))
            else:
                steps = max(1, int(a.ramp * 20))
                for i in range(steps):                # climb, do not jump
                    v = int(round(lvl * (i + 1) / steps))
                    stream.show(np.full((count, 3), v, np.uint8))
                    time.sleep(a.ramp / steps)
            t0 = time.time()
            time.sleep(a.hold)
            alive, note = watch.poll()
            seen = None
            if not a.no_camera:
                try:
                    p = mau5eye.shot(os.path.join(a.out, "s%04d.jpg" % int(target)),
                                     port=a.eye_port, after=t0, wait=12.0)
                    seen = brightness_of(p, dark_mean)
                except SystemExit:
                    seen = None
            est_total = target + count * STANDBY_PER_LED
            rows.append({"asked_ma": round(target, 1), "level": lvl,
                         "total_ma": round(est_total, 1),
                         "watts": round(est_total * 12 / 1000.0, 1),
                         "alive": alive, "note": note, "seen": seen})
            dim = (seen is not None and len(rows) > 1
                   and rows[-2]["seen"] is not None
                   and seen < rows[-2]["seen"] * 0.75)
            flag = note or ("BROWNED OUT (camera dimmer than the step below)"
                            if dim else "")
            print("  %6.0f mA LED  (%.1f W total)  level %3d  camera %s  %s"
                  % (target, est_total * 12 / 1000.0, lvl,
                     "%6.1f" % seen if seen is not None else "   -  ", flag))
            if not alive or dim:
                failed = target
                break
            best = target
            target += a.step
    finally:
        for v in (0.6, 0.3, 0.0):                     # ramp down too
            stream.show(np.full((count, 3), int(level_for(best or 100, count) * v),
                                np.uint8))
            time.sleep(0.25)
        stream.stop()
        try:
            w.off()
        except Exception:
            pass

    res = {"when": time.strftime("%Y-%m-%dT%H:%M:%S"), "count": count,
           "highest_stable_led_ma": best, "failed_at_led_ma": failed,
           "resets": watch.resets, "rows": rows}
    with open(os.path.join(a.out, "ramp.json"), "w") as f:
        json.dump(res, f, indent=1)
    print("\n  highest level it held: %.0f mA of LED current "
          "(%.1f W including standby)"
          % (best, (best + count * STANDBY_PER_LED) * 12 / 1000.0))
    if failed:
        print("  first failure at:      %.0f mA" % failed)
    print("  -> %s" % os.path.join(a.out, "ramp.json"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
