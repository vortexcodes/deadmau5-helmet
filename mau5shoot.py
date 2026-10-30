#!/usr/bin/env python3
"""mau5shoot -- light each check, photograph it, move on.

Pairs mau5verify's checks with mau5eye's borrowed camera so the whole
verification runs without anybody holding a phone and tapping.  It also
takes a dark frame first and saves a difference image for each check,
because what matters is which LEDs changed, and a difference says that
far more plainly than a photograph of a lit helmet does.

The helmet is thermally fragile, so it is dark between shots and the
run is as short as it can be.

    python3 mau5shoot.py                 # all checks
    python3 mau5shoot.py --only 0 1 7    # just these
"""

from __future__ import annotations

import argparse
import json
import os
import time

import numpy as np

import mau5eye
import mau5verify
import mau5wled

HERE = os.path.dirname(os.path.abspath(__file__))


def settle_and_grab(out, eye_port, settle, changed_at):
    """Wait out the camera's auto-exposure, then take a frame that is
    definitely of the current pattern -- captured after `changed_at`,
    not merely recent."""
    time.sleep(settle)
    return mau5eye.shot(out, port=eye_port, wait=25.0,
                        after=changed_at + settle * 0.5)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter,
                                 epilog=__doc__)
    ap.add_argument("--host", default=None)
    ap.add_argument("--count", type=int, default=621)
    ap.add_argument("--eye-port", type=int, default=8752)
    ap.add_argument("--out", default=os.path.join(HERE, "data", "cal", "shots"))
    ap.add_argument("--session", default=os.path.join(HERE, "data", "cal",
                                                      "walk_session.json"))
    ap.add_argument("--settle", type=float, default=1.4,
                    help="seconds lit before the frame is taken")
    ap.add_argument("--only", type=int, nargs="*", help="check indices")
    ap.add_argument("--level", type=float, default=1.0,
                    help="scale every check colour by this before sending. "
                         "The camera saturates long before the power guard "
                         "does, and a blown-out photo locates nothing.")
    a = ap.parse_args(argv)

    os.makedirs(a.out, exist_ok=True)
    checks = mau5verify.build_checks(json.load(open(a.session)))
    want = a.only if a.only else list(range(len(checks)))

    w = mau5wled.find_one(a.host)
    print(w.describe())
    w.realtime(True, brightness=255)
    pix = mau5wled.Pixels(w, a.count)
    if pix.guard is None:
        raise SystemExit("refusing to run: no power profile loaded, and this "
                         "helmet overheats.  Create data/cal/power.json first.")
    print("power guard: %.0f mA global budget\n" % pix.guard.budget_ma)

    # A thread holds the pattern up while we wait on the camera; without
    # it WLED times out mid-grab and we photograph its fallback effect.
    st = mau5wled.Streamer(pix, fps=20)

    manifest = []
    try:
        for i in want:
            c = checks[i]
            buf = np.zeros((a.count, 3), np.uint8)
            for lo, hi, col, _ in c["spans"]:
                v = tuple(int(round(x * a.level)) for x in col)
                buf[max(0, lo):min(a.count - 1, hi) + 1] = v

            # Paired dark/lit, taken seconds apart rather than once at
            # the start.  The camera's auto-exposure chases the LEDs, so
            # a single reference from the top of the run subtracts the
            # wrong exposure from every later shot.
            t = time.time(); st.dark()
            dpath = os.path.join(a.out, "%02d_%s_dark.jpg" % (i + 1, c["id"]))
            settle_and_grab(dpath, a.eye_port, a.settle, t)

            t = time.time(); st.show(buf)
            path = os.path.join(a.out, "%02d_%s.jpg" % (i + 1, c["id"]))
            settle_and_grab(path, a.eye_port, a.settle, t)
            r = st.last_power or {"amps": 0}
            st.dark()
            time.sleep(0.2)
            lit = int((buf.max(1) > 0).sum())
            print("  %2d  %-26s %3d leds  %.2f A  -> %s"
                  % (i + 1, c["id"], lit, r["amps"], os.path.basename(path)))
            manifest.append({"i": i, "id": c["id"], "title": c["title"],
                             "file": os.path.basename(path),
                             "dark": os.path.basename(dpath), "lit": lit,
                             "amps": r["amps"], "level": a.level,
                             "spans": [{"lo": sp[0], "hi": sp[1],
                                        "color": list(sp[2]), "label": sp[3]}
                                       for sp in c["spans"]]})
    finally:
        st.stop()
        print("\nblanked.")

    mf = os.path.join(a.out, "manifest.json")
    json.dump(manifest, open(mf, "w"), indent=1)
    print("manifest: %s" % mf)


if __name__ == "__main__":
    main()
