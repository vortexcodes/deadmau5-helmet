#!/usr/bin/env python3
"""test_mau5 -- invariants that must hold, checked rather than assumed.

Written against the things that actually went wrong while building
this: a frame grabbed before the LEDs changed and read as dead pixels,
a guard that let `False` through where it meant `None`, a colour-order
correction silently applied to the wrong span, and glyphs laid out on
an axis that turned out not to be up.  Each of those is cheap to test
and expensive to rediscover.

    python3 test_mau5.py           # all of it
    python3 test_mau5.py power     # one group
"""

from __future__ import annotations

import csv
import json
import math
import os
import sys
import traceback

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))

PASS, FAIL = [], []


def check(group, name, fn):
    try:
        fn()
        PASS.append((group, name))
    except BaseException as e:      # SystemExit included: a failing test
                                    # must not take the whole run with it
        FAIL.append((group, name, "%s: %s" % (type(e).__name__, e),
                     traceback.format_exc()))


def eq(a, b, msg=""):
    if a != b:
        raise AssertionError("%s expected %r got %r" % (msg, b, a))


def ok(cond, msg):
    if not cond:
        raise AssertionError(msg)


NOTES = []


def note(msg):
    """Something worth printing that is not a pass or a fail.

    Chiefly for checks whose scope depends on what is on the machine --
    a clone without the music can still verify every show, but it should
    say how much of the show suite it actually reached.
    """
    NOTES.append(msg)


# ----------------------------------------------------------------------
def t_map():
    import mau5map
    rows = mau5map.load()
    # 621 since a rim segment was cut off on 2026-10-29 (mau5slots.CUT)
    eq(len(rows), 621, "led count")
    eq([r["index"] for r in rows], list(range(621)), "indices contiguous")
    for r in rows:
        for k in ("x", "y", "z"):
            ok(math.isfinite(r[k]), "non-finite %s at %d" % (k, r["index"]))
        ok(0.0 <= r["u"] <= 1.0, "u out of range at %d" % r["index"])

    shell = [r for r in rows if r["region"] == "shell"]
    eq(len(shell), 398, "shell count")
    eq([r["index"] for r in shell], list(range(398)), "shell is not 0..397")

    # Every shell LED sits exactly in a CAD slot, and no two share one.
    # Positions come from the CAD and only the choice of slot from the
    # cameras; an LED between slots is somewhere no LED can be.
    cad = [(float(r["x"]), float(r["y"]), float(r["z"]))
           for r in csv.DictReader(open(os.path.join(HERE, "data", "cad",
                                                     "pixel_map_cad.csv")))]
    C = np.array(cad)
    taken = set()
    for r in shell:
        d = np.linalg.norm(C - np.array([r["x"], r["y"], r["z"]]), axis=1)
        k = int(d.argmin())
        ok(d[k] < 0.01, "shell led %d is %.1f mm from the nearest CAD slot"
           % (r["index"], d[k]))
        ok(k not in taken, "shell led %d shares a CAD slot" % r["index"])
        taken.add(k)

    # the swap flag must mark exactly the span the output path corrects
    sw = [r["index"] for r in rows if r["swap_rg"]]
    st = json.load(open(os.path.join(HERE, "data", "cal", "strips.json")))
    want = sorted(i for s in st["strips"] if s["order"] == "GRB"
                  for i in range(s["start"], s["start"] + s["count"]))
    eq(sw, want, "swap span differs from strips.json")

    # The chain is mostly continuous.  The exact set of jumps is not
    # fixed -- strip orientation comes from the camera now, and the
    # wiring is not a tidy snake -- so this checks the shape of the
    # distribution rather than memorising indices that move.
    pts = [(r["x"], r["y"], r["z"]) for r in shell]
    hops = [math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]
    big = [i for i, d in enumerate(hops) if d > 60]
    ok(np.median(hops) < 20, "median hop too large: %.1f" % np.median(hops))
    ok(len(big) <= 14, "%d discontinuities over 60 mm is too many" % len(big))
    ok(93 in big, "the long jumper from the chin band to the upper front "
                  "should still be there")
    ok(max(hops) < 400, "a %.0f mm jump is longer than the helmet" % max(hops))


def t_map_matches_walk():
    """The cameras and the hand walk found the same strips.

    Two instruments that share nothing -- an eye on the first night, two
    calibrated views a day later -- put 67 of 68 shell strip boundaries
    in the same place; the odd one is one LED at the chin.  A change to
    the map that loses that agreement has broken something.
    """
    import mau5map
    walk = json.load(open(os.path.join(HERE, "data", "cal", "walk_session.json")))
    rows = mau5map.load()
    shell = [r for r in rows if r["region"] == "shell"]
    starts = {0} | {i for i in range(1, len(shell))
                    if shell[i]["group"] != shell[i - 1]["group"]}
    walked = {0} | {s["start"] for s in walk["sections"] if s["start"] < len(shell)}
    eq(len(starts), 68, "shell strips")
    ok(len(starts & walked) >= 66, "only %d of %d strip boundaries match the walk"
       % (len(starts & walked), len(starts)))


def t_frame():
    """The CAD frame is not the obvious one: +z is up and the face
    looks along -y.  Assuming +y was up once put every glyph on its
    side, so this checks the actual formulas rather than a proxy."""
    import mau5engine as E
    h = E.Helmet()
    s = h.shell
    x, y, z = h.xyz[s].T
    az = np.degrees(np.arctan2(x, -y)) % 360.0
    el = np.degrees(np.arctan2(z, np.hypot(x, y)))
    ok(np.abs(((az - h.az[s] + 180) % 360) - 180).max() < 0.05,
       "az is not atan2(x, -y)")
    ok(np.abs(el - h.el[s]).max() < 0.05, "elev is not atan2(z, hypot(x,y))")
    # screen axes follow from that
    ok(np.allclose(h.px, h.xyz[:, 0]), "px must be x")
    ok(np.allclose(h.py, h.xyz[:, 2]), "py must be z")
    ok(np.allclose(h.depth, -h.xyz[:, 1]), "depth must be -y")
    # the face really does point at -y, at every elevation
    front = np.abs(h.fa[s]) < 20
    ok((h.xyz[s][front][:, 1] < 0).all(), "front-facing leds are not at -y")
    ok(h.py[s].max() - h.py[s].min() > 200, "py has no vertical extent")
    ok(h.py[h.ear1].mean() > h.py[s].mean(), "ear1 not above the shell")
    ok(h.px[h.ear1].mean() < -100 and h.px[h.ear2].mean() > 100, "ears not splayed")


def t_masks():
    import mau5engine as E
    h = E.Helmet()
    eq(int((h.shell | h.ears).sum()), h.n, "shell+ears must cover everything")
    ok(not (h.shell & h.ears).any(), "shell and ears overlap")
    ok(not (h.ear1 & h.ear2).any(), "ears overlap")
    eq(int((h.tubes | h.rims).sum()), int(h.ears.sum()), "ears = tubes+rims")
    ok(not (h.tubes & h.rims).any(), "tubes and rims overlap")
    for a in (h.nfa, h.nel, h.nx, h.ny, h.u):
        ok(np.isfinite(a).all(), "non-finite normalised coord")
        ok((a >= -1e-9).all() and (a <= 1 + 1e-9).all(), "normalised coord out of 0..1")


def t_presets():
    import mau5engine as E
    h = E.Helmet()
    ok(len(E.REGISTRY) >= 20, "expected at least 20 presets")
    for name, cls in sorted(E.REGISTRY.items()):
        p = cls()
        seen_any = False
        for t in (0.0, 0.37, 1.0, 2.5, 7.3, 61.0, 3600.5):
            out = p.render(h, t)
            eq(out.shape, (h.n, 3), "%s shape" % name)
            ok(np.isfinite(out).all(), "%s produced non-finite at t=%s" % (name, t))
            ok(out.min() >= -1e-6, "%s produced negative at t=%s" % (name, t))
            ok(out.max() <= 255 + 1e-6, "%s exceeded 255 at t=%s (%.1f)"
               % (name, t, out.max()))
            if out.max() > 4:
                seen_any = True
        ok(seen_any, "%s never lit anything across seven sample times" % name)


def t_preset_params():
    """Unknown parameters must be rejected, not silently ignored."""
    import mau5engine as E
    try:
        E.make("solid", nonsense=1)
    except ValueError:
        return
    raise AssertionError("an unknown parameter was accepted")


def t_power_budget():
    import mau5power as P
    g = P.load()
    ok(g is not None, "no power profile on disk")
    rng = np.random.default_rng(7)
    for trial in range(40):
        if trial == 0:
            buf = np.full((g.count, 3), 255, np.uint8)
        elif trial == 1:
            buf = np.zeros((g.count, 3), np.uint8)
        else:
            buf = rng.integers(0, 256, (g.count, 3), dtype=np.uint8)
        out, rep = g.apply(buf)
        ok(rep["sent_ma"] <= g.budget_ma + 1.0,
           "global budget exceeded: %.1f > %.1f" % (rep["sent_ma"], g.budget_ma))
        ok(out.dtype == np.uint8 and out.shape == buf.shape, "bad output frame")
        # int, not uint8: buf + 1 would wrap 255 to 0 and fail on every
        # saturated pixel, which is a bug in the test rather than the guard
        ok((out.astype(int) <= buf.astype(int) + 1).all(),
           "guard brightened a pixel")
        for r in g.regions:
            seg = out[r.lo:r.hi + 1].astype(float)
            ok(seg.max(initial=0) <= r.ceiling + 1,
               "%s exceeded its ceiling" % r.name)
            ma = seg.sum() / (3 * 255.0) * P.MA_PER_LED_FULL_WHITE
            ok(ma <= r.budget_ma + 1.0, "%s over its own budget" % r.name)


def t_power_board_limit():
    """Worst case must stay inside the 5 A the board accepts."""
    import mau5power as P
    g = P.load()
    worst = g.budget_ma + g.standby_ma() + 100
    ok(worst < 5000, "worst case %.0f mA exceeds the board's 5 A" % worst)


def t_guard_in_send():
    """Every frame must pass the clamp -- that is the whole safety story."""
    import mau5wled
    p = mau5wled.Pixels("127.0.0.1", 622)
    ok(p.guard is not None, "default Pixels has no guard")
    p.send(np.full((622, 3), 255, np.uint8))
    ok(p.last_power["sent_ma"] <= p.guard.budget_ma + 1, "send did not clamp")
    q = mau5wled.Pixels("127.0.0.1", 622, guard=False)
    ok(q.guard is None, "guard=False did not disable it")
    q.send(np.full((622, 3), 255, np.uint8))        # must not raise


def t_colour_correction():
    """The permutation must match strips.json exactly, at the edges too.

    Hardcoding which indices are swapped is what let this drift: the
    span was re-measured two LEDs longer and the test still asserted
    the old boundary, so it failed on the correct answer.  Read the
    boundaries from the file and check either side of each one.
    """
    import mau5wled
    p = mau5wled.Pixels("127.0.0.1", 622)
    ident = np.array([0, 1, 2])
    swapped = np.array([1, 0, 2])
    spans = json.load(open(os.path.join(HERE, "data", "cal", "strips.json")))["strips"]
    ok(spans, "no colour-order spans configured")
    inside = set()
    for st in spans:
        eq(st["order"], "GRB", "only a GRB swap is modelled here")
        lo, hi = st["start"], st["start"] + st["count"] - 1
        inside |= set(range(lo, hi + 1))
        for i in (lo, (lo + hi) // 2, hi):
            ok((p.perm[i] == swapped).all(), "led %d is inside %d..%d and "
               "should be R/G swapped" % (i, lo, hi))
        for i in (lo - 1, hi + 1):            # just outside, both ends
            if 0 <= i < 622 and i not in inside:
                ok((p.perm[i] == ident).all(),
                   "led %d is outside %d..%d and should be untouched" % (i, lo, hi))
    for i in (0, 398, 621):
        ok(i in inside or (p.perm[i] == ident).all(),
           "led %d should be identity" % i)
    buf = np.zeros((622, 3), np.uint8)
    rim = sorted(inside)[len(inside) // 2]
    buf[rim] = (200, 0, 0)
    buf[400] = (200, 0, 0)
    out = p.apply_order(buf)
    eq(tuple(out[rim]), (0, 200, 0), "rim red must leave as green")
    eq(tuple(out[400]), (200, 0, 0), "tube red must leave unchanged")


def t_lockable_presets():
    """Re-derive the beat-lock table instead of trusting it.

    A preset may only be phase-locked if it is exactly periodic in its
    cycle parameter -- one carrying state across the boundary would
    stutter every time the phase wrapped.  So check that each listed
    preset really does repeat, and that no preset with a cycle
    parameter was left off the list by accident without a reason.
    """
    import mau5engine as E
    h = E.Helmet()

    def repeats(name, params=None):
        per = E.cycle_seconds(name, params or E.REGISTRY[name].params)
        if per is None or per <= 0:
            return None
        p = E.make(name, **(params or {}))
        worst = 0.0
        for t0 in (0.13, 0.57, 1.11, 2.9):
            a = np.asarray(p.render(h, t0, None), float)
            b = np.asarray(p.render(h, t0 + per, None), float)
            worst = max(worst, float(np.abs(a - b).max()))
        return worst

    for name in E.LOCKABLE:
        ok(name in E.REGISTRY, "LOCKABLE names %r, which does not exist" % name)
        w = repeats(name)
        ok(w is not None, "%s is listed as lockable but has no cycle" % name)
        ok(w < 1.0, "%s is listed as lockable but render(t) != render(t+period) "
                    "(worst %.1f)" % (name, w))

    # anything with a cycle-shaped parameter that is NOT listed should
    # be genuinely non-periodic, or it is an oversight
    known_unlocked = {"eyes", "lightning", "gradient"}
    for name, cls in E.REGISTRY.items():
        if name in E.LOCKABLE:
            continue
        if not any(k in cls.params for k in ("period", "hz", "bpm", "cycle", "every")):
            continue
        ok(name in known_unlocked,
           "%s has a cycle parameter but is neither lockable nor "
           "listed as deliberately unlocked" % name)


def t_beat_lock_lands_on_the_grid():
    """A locked preset must repeat on beats, not on seconds."""
    import mau5engine as E, mau5show
    f = sorted(x for x in os.listdir(mau5show.SHOWS) if x.endswith(".json"))
    show = json.load(open(os.path.join(mau5show.SHOWS, f[0])))
    m = mau5show._music_for(show, os.path.join(HERE, show["track"]))
    ok(m is not None, "no analysis to lock against")
    for name in ("scanner", "wipe", "strobe"):
        params = E.REGISTRY[name].params
        t0 = float(m.bars[4]) if len(m.bars) > 4 else 10.0
        te0, beats = E.lock_time(m, name, params, t0)
        ok(beats in E.DIVISIONS, "%s snapped to %r, not a division" % (name, beats))
        # one whole cycle later on the beat grid, the phase must return
        spb = 60.0 / m.bpm
        te1, _ = E.lock_time(m, name, params, t0 + beats * spb)
        per = E.cycle_seconds(name, params)
        d = abs(te1 - te0) % per
        ok(min(d, per - d) < per * 0.06,
           "%s drifted %.3f of a cycle over one lock period" % (name, min(d, per-d)/per))


def t_shows():
    """Every show is structurally sound, cue to cue.

    The track itself is checked only when it is actually on disk.  The
    music is not distributed with the source, so a fresh clone has the
    show files and none of the audio, and failing there would report a
    missing mp3 as a broken show.  A track that *is* present still has
    to match the name the show was built against.
    """
    import mau5show
    tracks = 0
    for f in sorted(os.listdir(mau5show.SHOWS)):
        if not f.endswith(".json"):
            continue
        s = json.load(open(os.path.join(mau5show.SHOWS, f)))
        ok(s["cues"], "%s has no cues" % f)
        ok(s.get("track"), "%s names no track" % f)
        here = os.path.join(HERE, s["track"])
        beside = os.path.join(mau5show.SHOWS, os.path.basename(s["track"]))
        if os.path.exists(here) or os.path.exists(beside):
            tracks += 1
        prev = None
        for c in s["cues"]:
            ok(c["end"] > c["start"], "%s cue not forward" % f)
            ok(c["preset"], "%s cue has no preset" % f)
            if prev is not None:
                ok(abs(c["start"] - prev) < 0.01,
                   "%s has a gap or overlap at %.2f" % (f, c["start"]))
            prev = c["end"]
        ok(prev <= s["duration"] + 1.0, "%s runs past the track" % f)
    note("%d of the show tracks are on this machine" % tracks)


def t_floor_holds_the_shape():
    """A helmet left running must still look like a helmet.

    Weighted shedding gets the priority right and the endpoint wrong:
    the shell has shed 6, so it reaches zero long before the tubes
    give up, and anything driven for more than about a minute settles
    into two glowing stripes.  Each region now has a floor it is not
    shed below.  Three things have to hold at once: the floor is
    reached, the thermal budget is still not exceeded, and an LED the
    preset wanted dark stays dark.
    """
    import mau5power, mau5engine as E
    h = E.Helmet()
    g = mau5power.load(count=h.n)
    floors = {r.name: r.floor for r in g.regions}
    ok(any(v > 0 for v in floors.values()), "no floors configured")

    buf = np.clip(E.make("rainbow").render(h, 1.0, None), 0, 255)
    out = rep = None
    # Run it into the ground -- for as long as this bucket takes, not
    # for a number that happened to suit the bucket of the day.
    th = g.thermal
    span = th.burst_j / max((th.max_w or th.sustained_w) - th.sustained_w, 0.1)
    t = 0.0
    for _ in range(int(span / 2.0) * 3 + 200):
        out, rep = g.apply(buf, now=t)
        t += 2.0
        if rep["thermal"]["full_pct"] > 99:
            break
    ok(rep["thermal"]["full_pct"] > 95, "the bucket should be full by now, "
       "it is %.0f%%" % rep["thermal"]["full_pct"])
    # A full bucket is not a settled one: the allowance eases towards
    # sustained rather than stepping to it, so give it a minute to
    # arrive before asking what it settled at.
    for _ in range(60):
        out, rep = g.apply(buf, now=t)
        t += 2.0

    for r in g.regions:
        if r.floor <= 0:
            continue
        seg = out[r.lo:r.hi + 1].max(1)
        askseg = buf[r.lo:r.hi + 1].max(1)
        want = askseg > 0
        if not want.any():
            continue
        ok(seg[want].min() >= r.floor - 1.0,
           "%s fell to %.1f, below its floor of %.1f"
           % (r.name, float(seg[want].min()), r.floor))

    ok(rep["watts"] <= 11.0 + 0.4,
       "sustained draw %.1f W is over the 11 W ceiling" % rep["watts"])

    # a floor must never light something the preset wanted dark
    dark = np.zeros((h.n, 3))
    dark[h.tubes] = 255
    for t in range(300, 340):
        out, rep = g.apply(dark, now=float(t))
    eq(int(out[~h.tubes].max()), 0, "the floor lit LEDs the preset wanted dark")


def t_off_does_not_stream_black():
    """"Off" must hand the helmet back, not paint it black.

    A helmet being sent black at forty frames a second looks exactly
    like one with a dead supply, and it overrides whatever the
    controller would otherwise show -- including across a reboot.  It
    cost an evening of pulling wiring apart, so it gets a test.
    """
    import mau5ctl
    src = open(os.path.join(HERE, "mau5ctl.py")).read()
    ok("_set_output" in src, "the output switch is gone")
    ok("def _set_output" in src, "no _set_output method")
    # the frame loop must skip sending entirely when off
    body = src[src.index("def _run(self"):]
    body = body[:body.index("def _watchdog")]
    ok("if not live:" in body and "continue" in body,
       "the frame loop still renders while off")
    ok("soft_start" in src, "no soft start on the way out of dark")


def t_connector_limit():
    """The budget must respect the weakest connector, standby included.

    The thermal budget is about heat in the helmet and headroom at the
    supply.  Neither is the real ceiling when the current has to cross
    a contact that cannot carry it, and the first sign that it cannot
    is a melted housing rather than anything tripping.
    """
    import mau5power, mau5engine as E
    h = E.Helmet()
    g = mau5power.load(count=h.n)
    eq(g.link_limit_ma(), None, "no limit configured should mean no limit")

    buf = np.full((h.n, 3), 255.0)
    g.link_ma = 1000.0
    out, rep = g.apply(buf, now=0.0)
    ok(rep["total_ma"] <= 1000.0 + 1.0,
       "drew %.0f mA across a 1000 mA connector" % rep["total_ma"])
    ok(rep["sent_ma"] <= g.link_limit_ma() + 1.0,
       "LED current ignored the connector rating")

    # and it must not be the binding limit when the wiring is ample
    g2 = mau5power.load(count=h.n)
    g2.link_ma = 8000.0
    out2, rep2 = g2.apply(buf, now=0.0)
    ok(rep2["sent_ma"] > rep["sent_ma"],
       "a generous connector should not hold the frame back")


def t_power_failsafe():
    """No profile must never mean no limit.

    It did: load() returned None for a missing file, and every caller
    took None as "unguarded", so deleting one JSON file gave a helmet
    with nothing between a white frame and 11.8 A.  A missing profile
    is now timid, a broken one is an error, and save() round-trips
    every field the guard reads.
    """
    import contextlib, io, tempfile, mau5power
    with contextlib.redirect_stderr(io.StringIO()):
        g = mau5power.load(os.path.join(tempfile.mkdtemp(), "none.json"), count=622)
    ok(g is not None, "a missing profile gave no guard at all")
    _, rep = g.apply(np.full((622, 3), 255, np.uint8))
    ok(rep["sent_ma"] <= 300.5, "the timid guard let %.0f mA through" % rep["sent_ma"])
    bad = os.path.join(tempfile.mkdtemp(), "bad.json")
    open(bad, "w").write("{not json")
    try:
        mau5power.load(bad)
        ok(False, "a broken profile loaded silently")
    except ValueError:
        pass
    real = mau5power.load()
    rt = os.path.join(tempfile.mkdtemp(), "rt.json")
    mau5power.save(real, rt)
    back = mau5power.load(rt)
    eq([r.floor for r in back.regions], [r.floor for r in real.regions], "floors lost in a save")
    eq(back.link_ma, real.link_ma, "link_ma lost in a save")


def t_power_regions():
    """The power profile's regions must be the map's regions.

    They drifted once: power.json put the ear tube/rim boundary thirty
    LEDs early at both ears, so sixty tube LEDs were capped at the rim
    ceiling and charged against the rim budget.  Nothing failed, the
    tubes were simply dimmer than intended, which is invisible unless
    you go looking.  The map is the authority -- the measured
    colour-order swap lands exactly on its rim span, and a strip
    boundary is a physical fact.
    """
    import itertools, mau5map, mau5power
    rows = mau5map.load()
    spans = {}
    for k, g in itertools.groupby(enumerate(rows), key=lambda t: t[1]["region"]):
        g = list(g)
        ok(k not in spans, "region %r is not contiguous in the map" % k)
        spans[k] = (g[0][0], g[-1][0])
    g = mau5power.load(count=len(rows))
    got = {r.name: (r.lo, r.hi) for r in g.regions}
    eq(sorted(got), sorted(spans), "power.json names different regions")
    for name, (lo, hi) in spans.items():
        eq(got[name], (lo, hi), "power.json region %r" % name)

    # and the colour-order correction has to agree about the rims too
    strips = json.load(open(os.path.join(HERE, "data", "cal", "strips.json")))
    rim_lo = min(spans[k][0] for k in spans if k.endswith("rim"))
    rim_hi = max(spans[k][1] for k in spans if k.endswith("rim"))
    # The colour-order span and the mapped rims are the same physical
    # strip, so they must start together, and since the walk put the
    # second rim's end at 529 they end together too.  The check allows
    # a little overrun because the measurement is the wiring and wins.
    for st in strips["strips"]:
        eq(st["start"], rim_lo, "strips.json starts away from the mapped rims")
        ok(st["start"] + st["count"] - 1 >= rim_hi,
           "strips.json stops short of the mapped rims")
        ok(st["start"] + st["count"] - 1 <= rim_hi + 4,
           "strips.json runs well past the rims, which would recolour tubes")


def t_show_player():
    import mau5show
    f = [x for x in os.listdir(mau5show.SHOWS) if x.endswith(".json")]
    ok(f, "no shows to play")
    show = json.load(open(os.path.join(mau5show.SHOWS, sorted(f)[0])))
    pl = mau5show.Player(show)
    for t in (0.0, show["duration"] * 0.5, show["duration"] - 0.1):
        out = pl.frame(t)
        eq(out.shape, (621, 3), "player frame shape")
        ok(np.isfinite(out).all(), "player produced non-finite at t=%.1f" % t)
    ok(np.abs(pl.frame(show["duration"] + 50)).max() == 0, "past the end must be dark")


def t_ddp_packet():
    """The wire format: 10-byte header, PUSH only on the last chunk."""
    import struct, mau5wled
    sent = []
    p = mau5wled.Pixels("127.0.0.1", 622)
    p.sock = type("S", (), {"sendto": lambda self, d, a: sent.append(d)})()
    p.send(np.zeros((622, 3), np.uint8))
    ok(len(sent) >= 2, "622 leds should not fit one DDP packet")
    total = 0
    for i, pkt in enumerate(sent):
        flags, seq, cfg, dest, off, ln = struct.unpack(">BBBBIH", pkt[:10])
        eq(len(pkt) - 10, ln, "declared length mismatch")
        eq(off, total, "offset not contiguous")
        total += ln
        last = i == len(sent) - 1
        eq(bool(flags & p.PUSH), last, "PUSH flag on the wrong packet")
    eq(total, 622 * 3, "wrong number of channels sent")


def t_eye_after():
    """shot(after=) must reject a frame captured before the change.

    Freshness alone is not enough and neither is the push time: the
    browser grabs, encodes and uploads with its own lag, so the first
    push after a change can still show the previous state.  That failure
    looks exactly like dead LEDs, which is how it was found.
    """
    import mau5eye
    import http.server, threading, json as J, time

    state = {"frames": 0, "age": 0.05, "have": True, "tick": True}

    class H(http.server.BaseHTTPRequestHandler):
        def log_message(self, *a): pass
        def do_GET(self):
            if self.path.startswith("/api/status"):
                if state["tick"]:
                    state["frames"] += 1          # a live camera keeps pushing
                b = J.dumps({k: state[k] for k in ("frames", "age", "have")}).encode()
            else:
                b = b"\xff\xd8\xff\xd9"
            self.send_response(200)
            self.send_header("Content-Length", str(len(b)))
            self.end_headers(); self.wfile.write(b)

    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), H)
    port = srv.server_address[1]
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    try:
        # a stale frame: pushed ten seconds ago, so captured before `after`
        state.update(age=10.0)
        try:
            mau5eye.shot(os.devnull, port=port, wait=1.2,
                         after=time.time(), tls=False)
            raise AssertionError("accepted a frame pushed before the change")
        except SystemExit:
            pass
        # a live camera: recent pushes, counter advancing
        state.update(age=0.05)
        out = mau5eye.shot(os.devnull, port=port, wait=4.0,
                           after=time.time() - 1.0, tls=False)
        ok(out, "rejected a genuinely fresh frame")
        # and it really does wait for a second push rather than the first
        state.update(tick=False)
        try:
            mau5eye.shot(os.devnull, port=port, wait=1.2,
                         after=time.time() - 1.0, tls=False)
            raise AssertionError("accepted without a second push")
        except SystemExit:
            pass
    finally:
        srv.shutdown()


def t_text_bitmap():
    import mau5engine as E
    bm = E._text_bitmap("A")
    eq(bm.shape[0], 7, "glyph height")
    ok(bm.any(), "'A' rendered blank")
    ok(not E._text_bitmap(" ").any(), "space should be blank")
    h = E.Helmet()
    lit = E.make("text", text="8").render(h, 0.0).max(1) > 8
    ok(lit.sum() > 0, "text lit nothing")
    ok(not lit[~h.shell].any(), "text leaked onto the ears")


def t_lan_ip():
    """Must prefer a real LAN over a VPN tunnel -- this cost an hour once."""
    import mau5wled
    nets = mau5wled.local_nets()
    ip = mau5wled.lan_ip()
    ok(ip and not ip.startswith("127."), "lan_ip returned loopback")
    if nets:
        eq(ip, nets[0]["ip"], "lan_ip disagrees with local_nets")
        for n in nets:
            ok(n["bits"] <= 32 and n["ip"].count(".") == 3, "malformed net")



def t_accepts():
    """The HTTP boundary must be lenient where the Python API is strict."""
    import mau5engine as E
    for name, cls in E.REGISTRY.items():
        kw = cls.accepts({"color": [1, 2, 3], "utter_nonsense": 9})
        ok("utter_nonsense" not in kw, "%s kept an unknown key" % name)
        E.make(name, **kw)                     # must construct
    eq(E.REGISTRY["wipe"].accepts({"color": [1, 2, 3]}), {"a": (1, 2, 3)},
       "wipe should take a colour as 'a'")
    eq(E.REGISTRY["eq"].accepts({"color": [1, 2, 3]}), {"lo": (1, 2, 3)},
       "eq should take a colour as 'lo'")
    ok(E.REGISTRY["plasma"].accepts({"color": [1, 2, 3]}) == {},
       "plasma has no colour to redirect to")
    try:
        E.make("solid", utter_nonsense=1)
        raise AssertionError("the Python API should still reject unknown keys")
    except ValueError:
        pass


def t_crossfade():
    """A cut between two full-face effects reads as a glitch; the fade
    exists to stop that, so check it actually reduces the step."""
    import mau5show
    f = sorted(x for x in os.listdir(mau5show.SHOWS) if x.endswith(".json"))
    ok(f, "no shows")
    show = json.load(open(os.path.join(mau5show.SHOWS, f[0])))
    ok(len(show["cues"]) > 2, "need a few cues to test a boundary")
    music = mau5show._music_for(show, os.path.join(HERE, show["track"]))
    b = show["cues"][2]["start"]
    faded = mau5show.Player(show, music=music)
    hard = dict(show); hard["fade"] = 0.0
    cut = mau5show.Player(hard, music=music)
    step_f = float(np.abs(faded.frame(b + 0.05) - faded.frame(b - 0.05)).mean())
    step_c = float(np.abs(cut.frame(b + 0.05) - cut.frame(b - 0.05)).mean())
    ok(step_f < step_c * 0.75,
       "fade did not soften the boundary (%.1f vs %.1f)" % (step_f, step_c))


def t_beat_helpers():
    import mau5show
    f = sorted(x for x in os.listdir(mau5show.SHOWS) if x.endswith(".json"))
    show = json.load(open(os.path.join(mau5show.SHOWS, f[0])))
    m = mau5show._music_for(show, os.path.join(HERE, show["track"]))
    ok(m is not None, "no music")
    ts = np.arange(30.0, 62.0, 1 / 40.0)
    on = np.array([m.is_downbeat(t) for t in ts])
    rises = int((np.diff(on.astype(int)) == 1).sum())
    want = 32 * m.bpm / 60.0 / 4.0
    ok(abs(rises - want) <= 2,
       "downbeats off: %d in 32 s, expected about %.0f" % (rises, want))
    for t in ts[::37]:
        ph = m.beat_phase(float(t))
        ok(0.0 <= ph <= 1.0, "beat phase out of range: %s" % ph)


def t_analysis_cache():
    """The cache must reproduce the analysis, not approximate it."""
    import mau5show
    f = sorted(x for x in os.listdir(mau5show.SHOWS) if x.endswith(".json"))
    show = json.load(open(os.path.join(mau5show.SHOWS, f[0])))
    cache = os.path.join(mau5show.SHOWS, show["analysis"])
    ok(os.path.exists(cache), "no analysis cache beside the show")
    import time
    t0 = time.time()
    m = mau5show._music_for(show, os.path.join(HERE, show["track"]))
    ok(time.time() - t0 < 1.0, "cached load took over a second")
    eq(round(m.bpm, 2), show["bpm"], "cached bpm disagrees with the show")
    eq(len(m.energy), len(m.onset), "curve lengths differ")
    ok(np.isfinite(m.energy).all(), "cached energy has non-finite values")



def _click_wav(path, bpm, seconds=26.0, offset=0.0, seed=5):
    """A click track with a known tempo and phase, so the analyser can
    be checked against ground truth instead of against itself."""
    import wave, math
    sr = 22050
    rng = np.random.default_rng(seed)
    n = int(seconds * sr)
    a = rng.normal(0, 0.004, n)
    k = 0
    while True:
        i = int((offset + k * 60.0 / bpm) * sr)
        if i >= n:
            break
        dur = min(int(0.09 * sr), n - i)
        env = np.exp(-np.arange(dur) / (0.020 * sr))
        a[i:i + dur] += 0.85 * env * np.sin(2 * math.pi * 60 * np.arange(dur) / sr)
        k += 1
    a = np.clip(a, -1, 1)
    with wave.open(path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes((a * 32000).astype("<i2").tobytes())
    return path


def t_tempo_truth():
    """Tempo must come back right, not merely self-consistent."""
    import tempfile, mau5song
    d = tempfile.mkdtemp(prefix="mau5tempo")
    try:
        for bpm, off in ((100.0, 0.0), (128.0, 0.137), (174.0, 0.061)):
            p = _click_wav(os.path.join(d, "c%d.wav" % bpm), bpm, offset=off)
            an = mau5song.analyse(p, verbose=False)
            err = abs(an["bpm"] / bpm - 1) * 100
            ok(err < 1.0, "tempo %.0f came back %.2f (%.2f%% out)"
               % (bpm, an["bpm"], err))
    finally:
        for f in os.listdir(d):
            os.remove(os.path.join(d, f))
        os.rmdir(d)


def t_beat_alignment():
    """The grid must land ON the clicks.  A constant offset here is the
    difference between lights that hit and lights that nearly hit, and
    it was -13.2 ms until it was measured and removed."""
    import tempfile, mau5song
    d = tempfile.mkdtemp(prefix="mau5align")
    try:
        errs = []
        for bpm, off in ((100.0, 0.0), (128.0, 0.137), (174.0, 0.061)):
            p = _click_wav(os.path.join(d, "a%d.wav" % bpm), bpm, offset=off)
            an = mau5song.analyse(p, verbose=False)
            got = np.asarray(an["beats"])
            want = np.arange(off, 24.0, 60.0 / bpm)[2:-2]
            errs.extend(got[np.argmin(np.abs(got - w))] - w for w in want)
        errs = np.array(errs)
        ok(abs(errs.mean()) < 0.004,
           "beat grid is biased by %+.1f ms" % (errs.mean() * 1000))
        ok(errs.std() < 0.006,
           "beat grid jitters by %.1f ms" % (errs.std() * 1000))
    finally:
        for f in os.listdir(d):
            os.remove(os.path.join(d, f))
        os.rmdir(d)



def t_thermal():
    """Brightness must be rationed over time, not only per frame.

    The per-frame guard cannot tell a bright chorus from a bright half
    hour, and it is the half hour that melts hot glue.

    How long that takes is a property of the configured bucket, not a
    constant to write down here: this used to drive 400 seconds and
    assert the allowance had fallen, which was true of a 900 J bucket
    and quietly false the moment the bucket was resized.  So it runs
    until the bucket is actually full, and gives up only if that never
    happens.
    """
    import mau5power as P
    g = P.load()
    ok(g.thermal is not None, "no thermal budget configured")
    th = g.thermal
    buf = np.full((g.count, 3), 255, np.uint8)
    dark = np.zeros((g.count, 3), np.uint8)
    step = 5.0                      # the largest dt the bucket will honour
    cap = int(th.burst_j / max(th.max_w - th.sustained_w, 0.1) / step) * 6 + 200

    t, first, settled = 0.0, None, None
    for _ in range(cap):
        out, rep = g.apply(buf, now=t)
        t += step
        led = rep["watts"] - th.standby_w
        if first is None:
            first = led
        settled = led
        if th.level >= th.burst_j * 0.999:
            break
    ok(th.level >= th.burst_j * 0.999,
       "the bucket never filled in %.0f s of full white -- it cannot ration"
       % (cap * step))
    ok(first > settled * 2.5,
       "it never eased off: %.1f W at the start, %.1f W once the bucket "
       "was full" % (first, settled))
    ok(abs((settled + th.standby_w) - th.sustained_w) < 1.0,
       "settled at %.1f W total, expected about %.1f"
       % (settled + th.standby_w, th.sustained_w))

    # and quiet must give the headroom back
    drained = int(th.burst_j / max(th.sustained_w - th.standby_w, 0.1) / step) + 400
    for _ in range(drained):
        g.apply(dark, now=t)
        t += step
        if th.level <= 1e-6:
            break
    ok(th.level <= 1e-6, "a long rest did not drain the bucket: %.0f J left"
       % th.level)
    out, rep = g.apply(buf, now=t)
    ok(rep["watts"] - th.standby_w > first * 0.95,
       "a burst after a long rest should be full brightness again, got %.1f W"
       % (rep["watts"] - th.standby_w))
    ok(th.level >= 0 and th.level <= th.burst_j + 1e-6, "bucket left out of range")
    note("power: the bucket fills in %.0f s of full white and drains in %.0f s"
         % (t and 0 or 0, 0) if False else
         "power: %.0f J bucket, %.1f min of 19.5 W before it rations"
         % (th.burst_j, th.burst_j / max(19.5 - th.sustained_w, 0.1) / 60))


def t_thermal_never_exceeds():
    """Whatever the content, the helmet cannot cook itself.

    The rule this encodes is Jones's: power may go up for effects and
    shows, as long as it is not sustained for ten minutes or more.
    That is exactly a leaky bucket, so the invariant is stated as
    energy rather than as an average over some window -- an average
    was what the old version checked, and resizing the bucket made it
    fail while the helmet was behaving exactly as asked.

    Over any run, delivered energy cannot exceed what the helmet can
    shed for that long, plus one bucketful.  That holds for any
    bucket size, so it cannot rot the way a hard-coded twenty minutes
    did.
    """
    import mau5power as P
    g = P.load()
    th = g.thermal
    rng = np.random.default_rng(11)
    t, total_j, hot_s = 0.0, 0.0, 0.0
    DUR, STEP = 3600, 2.0
    for _ in range(int(DUR / STEP)):
        buf = rng.integers(150, 256, (g.count, 3), dtype=np.uint8)
        out, rep = g.apply(buf, now=t)
        total_j += rep["watts"] * STEP
        if rep["watts"] > th.sustained_w + 0.5:
            hot_s += STEP
        t += STEP

    budget_j = th.sustained_w * DUR + th.burst_j
    ok(total_j <= budget_j * 1.02,
       "an hour of bright content delivered %.0f kJ; the helmet can shed "
       "%.0f kJ in that time plus %.0f J of bucket"
       % (total_j / 1000, th.sustained_w * DUR / 1000, th.burst_j))

    # The other half of the rule, and the half an energy budget cannot
    # state: it must not still be up there at ten minutes.  Measuring
    # "time above sustained" instead does not work -- the allowance
    # eases down towards sustained rather than stepping, so it lingers
    # a hair above for ever and any such bound is arbitrary.
    g2 = P.load()
    t = 0.0
    at_ten = None
    for _ in range(int(660 / STEP)):
        buf = rng.integers(150, 256, (g2.count, 3), dtype=np.uint8)
        out, rep = g2.apply(buf, now=t)
        t += STEP
        if at_ten is None and t >= 600.0:
            at_ten = rep["watts"]
    ok(at_ten is not None and at_ten <= th.sustained_w + 1.5,
       "after ten minutes of full-bright it was still drawing %.1f W; the "
       "rule is that nothing stays raised for ten minutes or more"
       % (at_ten or 0.0))
    note("power: %.0f J bucket -> %.1f W at ten minutes of full-bright, "
         "settling to %.0f" % (th.burst_j, at_ten, th.sustained_w))


def t_strip_orientation():
    """Every shell strip must run the way the camera saw it run.

    Twenty-seven of them did not: the map guessed each strip's
    direction by continuity, which agreed with the camera on 19% of
    strips, while the CAD's stored order managed 48%.  Neither is a
    wiring diagram.  The camera decides now, and this keeps it that way.
    """
    import mau5engine as E, mau5locate
    meas = mau5locate.load()
    if len(meas) < 400:
        return                       # nothing measured yet; nothing to check
    h = E.Helmet()
    agree = tot = 0
    bad = []
    for g in sorted(set(h.group[h.shell])):
        idx = np.flatnonzero((h.group == g) & h.shell)
        if len(idx) < 3 or not all(int(i) in meas for i in idx):
            continue
        k = np.arange(len(idx))
        ms = np.polyfit(k, h.py[idx], 1)[0]
        cs = np.polyfit(k, np.array([meas[int(i)]["cy"] for i in idx]), 1)[0]
        tot += 1
        if ms * cs < 0:
            agree += 1
        else:
            bad.append(int(g))
    ok(tot >= 20, "only %d strips testable" % tot)
    ok(agree == tot, "%d of %d strips run against the camera: %s"
       % (tot - agree, tot, bad[:10]))


def t_ears_match():
    """The two ears are the same physical part, so the map should make
    them the same size.  Nothing in the fit enforces this, which is
    what makes it worth checking: it caught a reflection being
    measured as LED 498 and stretching one ear by 40%."""
    import mau5engine as E
    h = E.Helmet()
    w1, w2 = float(np.ptp(h.xyz[h.ear1, 0])), float(np.ptp(h.xyz[h.ear2, 0]))
    ok(min(w1, w2) > 100, "an ear is implausibly small: %.0f / %.0f mm" % (w1, w2))
    ok(abs(w1 - w2) / max(w1, w2) < 0.15,
       "the ears differ in width by %.0f%% (%.0f vs %.0f mm)"
       % (100 * abs(w1 - w2) / max(w1, w2), w1, w2))


# ----------------------------------------------------------------------
# Offline mode.
#
# At a show the phone talks to the controller and nothing else, so the
# preset engine and the power guard both run in JavaScript on the
# phone.  Two implementations of the same thing is a standing invitation
# to drift, and the drift would show up on a helmet at a party with
# nobody able to debug it.  These are what make the port a port: the
# same presets, the same guard and the same colour correction, driven
# in both languages and compared.
# ----------------------------------------------------------------------
import base64
import shutil
import subprocess

OFFLINE_TIMES = (0.0, 0.37, 1.234, 2.5, 3.9, 7.77, 11.1)


def _node(script, job):
    """Run one of remote/offline's node helpers, or say why not."""
    if not shutil.which("node"):
        return None
    p = subprocess.run(["node", os.path.join(HERE, "remote", "offline", script)],
                       input=json.dumps(job), capture_output=True, text=True,
                       cwd=HERE, timeout=300)
    if p.returncode:
        raise AssertionError("%s failed:\n%s" % (script, p.stderr[-2000:]))
    return json.loads(p.stdout)


def _f32(b64):
    return np.frombuffer(base64.b64decode(b64), "<f4")


def t_offline_engine_matches_python():
    """Every preset, both languages, same answer.

    The tolerance is half a count out of 255, which the float32
    geometry in the bundle alone can use up; in practice the worst
    preset lands three orders of magnitude inside it.
    """
    import mau5engine as E
    import mau5offline
    data = mau5offline.bundle()
    names = sorted(E.REGISTRY)
    jobs = [{"preset": nm, "params": {}, "t": t, "reset": (t == OFFLINE_TIMES[0])}
            for nm in names for t in OFFLINE_TIMES]
    res = _node("crosscheck.js", {"data": data, "jobs": jobs})
    if res is None:
        return note("offline: node not installed, the JS port went unchecked")
    h = E.Helmet()
    worst, where = 0.0, ""
    k = 0
    for nm in names:
        inst = E.make(nm)
        for t in OFFLINE_TIMES:
            py = np.clip(np.asarray(inst.render(h, t), float), 0, 255)
            js = np.clip(_f32(res[k]["f"]).reshape(-1, 3), 0, 255)
            k += 1
            d = float(np.abs(py - js).max())
            if d > worst:
                worst, where = d, "%s at t=%.3f" % (nm, t)
    ok(worst <= 0.51, "the JS port differs from the Python by %.3f counts (%s)"
       % (worst, where))
    note("offline: %d presets match the Python to %.4f counts"
         % (len(names), worst))


def t_offline_guard_matches_python():
    """The guard the phone runs is the guard the laptop runs.

    Equality is on the current, which is the number that matters and
    which comes out identical.  Individual LEDs are allowed one count:
    the governor bisects on a sum of 622 terms, numpy adds them
    pairwise and JavaScript adds them in order, and the last bit of
    that sum can put a channel either side of a truncation boundary.
    """
    import mau5engine as E
    import mau5offline
    import mau5power
    data = mau5offline.bundle()
    seq = [("solid", 0.0), ("solid", 0.5), ("rainbow", 1.0), ("fire", 1.5),
           ("plasma", 2.0), ("twinkle", 2.5), ("strobe", 3.0), ("eq", 3.5),
           ("solid", 4.0), ("solid", 120.0)]
    jobs = [{"preset": nm, "params": {}, "t": t, "now": t, "guard": True,
             "reset": (i == 0)} for i, (nm, t) in enumerate(seq)]
    res = _node("crosscheck.js", {"data": data, "jobs": jobs})
    if res is None:
        return note("offline: node not installed, the JS guard went unchecked")
    h = E.Helmet()
    g = mau5power.load(count=h.n)
    worst_ma, worst_led = 0.0, 0.0
    for i, (nm, t) in enumerate(seq):
        py, rep = g.apply(np.asarray(E.make(nm).render(h, t), float), now=t)
        js = _f32(res[i]["f"]).reshape(-1, 3)
        worst_ma = max(worst_ma, abs(rep["sent_ma"] - res[i]["report"]["sent_ma"]))
        worst_led = max(worst_led, float(np.abs(py.astype(float) - js).max()))
    ok(worst_ma <= 0.1, "the two guards disagree by %.2f mA" % worst_ma)
    ok(worst_led <= 1.0, "the two guards disagree by %.1f counts on an LED"
       % worst_led)
    note("offline: the JS guard tracks the Python to %.2f mA" % worst_ma)


def t_offline_encoder_roundtrip():
    """What the phone sends is what the controller will show.

    Decoded here by mau5fake's parser, which is written against WLED's
    `i` syntax rather than against the encoder -- so this is two
    independent readings of the same spec, not a function and its
    inverse.  Includes the colour-order permutation, because an
    encoder that quietly dropped it would light the ear rims green and
    every other test would still pass.

    The frames go to one controller, one after another, exactly as the
    player sent them: a segment that did not change is not sent, so
    the only way to check that is to keep the controller's state
    between frames, the way the helmet does.
    """
    import mau5engine as E
    import mau5fake
    import mau5power
    import mau5wled
    h = E.Helmet()
    g = mau5power.load(count=h.n)
    strips = json.load(open(os.path.join(HERE, "data", "cal", "strips.json")))["strips"]
    frames = []
    for nm, t in (("solid", 0.0), ("rainbow", 0.1), ("rainbow", 0.15),
                  ("fire", 1.0), ("scanner", 1.2), ("strobe", 2.0),
                  ("solid", 2.5), ("solid", 2.5)):
        f, _ = g.apply(np.asarray(E.make(nm).render(h, t), float), now=t)
        frames.append(f.astype(np.uint8))
    # one LED changed: one segment's message, and only that one
    one = frames[-1].copy()
    one[450] = (9, 99, 199)
    frames.append(one)
    pix = mau5wled.Pixels("0.0.0.0", count=h.n, strips=strips, guard=False)
    job = {"count": h.n, "strips": strips,
           "frames": [base64.b64encode(f.tobytes()).decode() for f in frames]}
    res = _node("wiretest.js", job)
    if res is None:
        return note("offline: node not installed, the encoder went unchecked")
    sent, pad = res["frames"], res["pad"]
    eq(len(sent), len(frames), "one result per frame")

    fake = mau5fake.Fake(count=h.n)
    fake.apply_state({"seg": res["layout"]})
    eq(len(fake.segs), len(res["layout"]), "the controller took the layout")
    ok(all(g["frz"] for g in fake.segs), "every segment frozen")
    fake.px[:] = 255                          # prove the writes blank first
    msgs = []
    for f, out in zip(frames, sent):
        want = pix.apply_order(f)
        ws = out["ws"]
        if ws:
            # every frame that sends anything ends with the ping that
            # paces the player and the filler that keeps the two of them
            # exactly one TCP segment: 7 + 8 + 1421 = 1436 bytes
            eq(ws[-2], "p", "a frame must end with its ping")
            eq(ws[-1], " " * res["filler"], "and the filler after it")
            eq(len("p") + 6 + res["filler"] + 8, 1436, "ping and filler fill one segment")
            ws = ws[:-2]
        for m in ws:
            # exactly one TCP segment each, or a repacked stream splits
            # them and the firmware refuses half
            eq(len(m), pad, "padded message length")
            ok(m.encode() == m.encode("ascii", "strict"), "padding must be plain bytes")
            fake.apply_state(json.loads(m))
        ok(np.array_equal(fake.px, want),
           "the controller would show %d LEDs wrong"
           % int((fake.px != want).any(1).sum()))
        msgs.append(len(ws))
        # and the POST the player falls back on, alone, onto a scrambled strip
        other = mau5fake.Fake(count=h.n)
        other.apply_state({"seg": res["layout"]})
        other.px[:] = 255
        other.apply_state(json.loads(out["http"]))
        ok(np.array_equal(other.px, want), "a whole-frame POST shows %d LEDs wrong"
           % int((other.px != want).any(1).sum()))
    first = {g["id"] for m in sent[0]["ws"][:-2] for g in json.loads(m)["seg"]}
    eq(first, set(range(len(res["layout"]))), "the first frame goes whole")
    eq(msgs[-2], 0, "a repeated frame should send nothing")
    eq(sent[-2]["ret"], 0, "and say so, so it still counts as shown")
    eq(msgs[-1], 1, "one changed LED should send one segment")
    dp = res["depth"]
    lim = res["depthLimit"]
    ok(all(not x["busy"] for x in dp[:lim]), "the link refused a frame before %d were in flight" % lim)
    ok(dp[lim]["busy"] and dp[lim]["ret"] == -1, "a frame beyond %d in flight must wait" % lim)
    hb = res["handBack"]
    ok(not hb["missing"], "handing back to a preset that is not there leaves the helmet lit")
    ok(hb["present"], "a standby preset that exists should be handed back to")
    ok(not hb["notWanted"], "no standby wanted means switching off")
    note("offline: %d frames through one controller, decoded exactly: %d "
         "segments, %s padded messages a frame"
         % (len(frames), len(res["layout"]), "/".join(str(m) for m in msgs)))


def t_offline_oversize_is_caught():
    """The limit is the firmware's, not ours, so measure against it."""
    import mau5fake
    f = mau5fake.Fake(count=622)
    f.frozen = True
    ok(mau5fake.Fake.WS_SEGMENT == 1436,
       "the measured TCP segment size is 1436; anything else needs re-measuring")
    # Blanking, the behaviour that invalidated deltas.
    f.apply_state({"seg": {"id": 0, "i": [0, 100, "FF0000"]}})
    eq(int((f.px.max(1) > 0).sum()), 100, "a range write lights its range")
    f.apply_state({"seg": {"id": 0, "i": [100, 200, "00FF00"]}})
    eq(int((f.px.max(1) > 0).sum()), 100,
       "a second write blanks the first, as WLED 0.15.4 does")
    ok(f.px[0].max() == 0, "LED 0 should have gone dark")
    # ...but only within its own segment, which is what the player's
    # five segments rely on.  Measured on the helmet, read back through
    # the live preview: a write to segment 0 left segment 1 as it was.
    f.apply_state({"seg": [{"id": 0, "start": 0, "stop": 300, "frz": True},
                           {"id": 1, "start": 300, "stop": 622, "frz": True}]})
    f.apply_state({"seg": {"id": 1, "i": [0, 10, "0000FF"]}})
    f.apply_state({"seg": {"id": 0, "i": [0, 5, "FF0000"]}})
    eq(int((f.px[300:310, 2] == 255).sum()), 10, "segment 1 survives a write to 0")
    eq(int((f.px[:300].max(1) > 0).sum()), 5, "segment 0 shows only its own write")


def t_map_adjustments():
    """Hand corrections reach the map, and undo really undoes.

    The point of keeping them in their own file is that re-running
    the localisation must not discard them, so the thing to check is
    that load() applies them and that removing one puts the map back
    exactly -- not approximately, because a nudge that half survives
    is worse than one that never applied.
    """
    import copy
    import mau5map
    base = mau5map.load(adjust=False)
    raw = {r["index"]: (r["x"], r["z"]) for r in base}
    want = {r["index"]: (round(r["x"], 4), round(r["z"], 4), r["region"])
            for r in base}

    rows = copy.deepcopy(base)
    rows, done = mau5map.apply_adjustments(rows, path=os.devnull)
    eq(len(done), 0, "a missing adjustments file should change nothing")

    import tempfile
    spans = {"spans": [
        {"op": "move", "lo": 10, "hi": 12, "dx": 5.0, "dz": -2.0},
        {"op": "region", "lo": 399, "hi": 406, "to": "ear1_cross"},
        {"op": "reverse", "lo": 20, "hi": 25},
        {"op": "shift", "lo": 30, "hi": 35, "by": 1},
    ]}
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(spans, f)
        path = f.name
    try:
        rows = copy.deepcopy(base)
        rows, done = mau5map.apply_adjustments(rows, path=path)
        eq(len(done), 4, "all four corrections should have applied")
        by = {r["index"]: r for r in rows}
        ok(abs(by[10]["x"] - (raw[10][0] + 5.0)) < 1e-6, "move did not shift x")
        ok(abs(by[10]["z"] - (raw[10][1] - 2.0)) < 1e-6, "move did not shift z")
        eq(by[399]["region"], "ear1_cross", "region relabel did not apply")
        ok(abs(by[20]["x"] - raw[25][0]) < 1e-6, "reverse did not swap the ends")
        ok(abs(by[25]["x"] - raw[20][0]) < 1e-6, "reverse did not swap the ends")
        ok(by[30]["x"] != raw[30][0], "shift left the span where it was")
        # Everything outside the named spans must be untouched.
        for i, w in want.items():
            if 10 <= i <= 12 or 20 <= i <= 25 or 30 <= i <= 35 or 399 <= i <= 406:
                continue
            eq((round(by[i]["x"], 4), round(by[i]["z"], 4), by[i]["region"]), w,
               "led %d moved and nothing asked it to" % i)
    finally:
        os.unlink(path)


class _ShowDrive:
    """A music drive that is a pure function of t in both languages.

    The shows are the one thing here with no simulator to check
    against -- a cue list is 44 changes of effect over ten minutes and
    nobody is going to eyeball that twice.  So the Python player and
    the ported one are driven by the same arithmetic and compared
    frame for frame.

    lock_conf is NaN deliberately: offline there is no confident beat
    grid to quantise to, so both sides must decide not to lock.
    """
    bands = True
    bpm = 128.0
    lock_conf = float("nan")

    def level_at(self, t):
        return 0.5 + 0.4 * math.sin(t * 1.7)

    def beat_phase(self, t):
        return (t * 2.13) % 1.0

    def beat_index(self, t):
        return t * 2.13

    def is_downbeat(self, t):
        return ((t * 0.53) % 1.0) < 0.05

    def pitch_at(self, t):
        return (t * 0.11) % 1.0

    def centroid_at(self, t):
        return 0.5 + 0.4 * math.sin(t * 0.63)

    def bands_at(self, t, n):
        return np.array([0.5 + 0.4 * math.sin(t * 0.9 + k * 0.6) for k in range(n)])

    def band_at(self, t, name="bass", punch=False):
        w = 1.1 if name == "bass" else (1.9 if name == "mid" else 2.7)
        return 0.5 + 0.4 * math.sin(t * w + (0.3 if punch else 0.0))


def t_offline_shows_match_python():
    """The cue lists run the same on the phone as on the laptop."""
    import mau5engine as E
    import mau5offline
    import mau5show
    data = mau5offline.bundle()
    if not data.get("shows"):
        return note("offline: no shows to check")
    h = E.Helmet()
    drive = _ShowDrive()
    times = [3.0, 17.5, 41.25, 88.0, 150.5]
    names = sorted(data["shows"])
    res = _node("showtest.js", {"data": data, "shows": names, "times": times})
    if res is None:
        return note("offline: node not installed, the shows went unchecked")
    worst, where = 0.0, ""
    for name in names:
        show = dict(data["shows"][name])
        show["cues"] = show["cues"]
        py = mau5show.Player(show, helmet=h, music=drive)
        ok(not py.lock, "with no confident grid the laptop should not lock")
        for k, t in enumerate(times):
            a = np.asarray(py.frame(t), float)
            b = np.asarray(res[name]["frames"][k], float).reshape(-1, 3)
            d = float(np.abs(a - b).max())
            # the beat pulse travels beside the frame now, so it has to
            # agree too -- scaled to counts so one bar covers both
            d = max(d, abs(py.gain - res[name]["gains"][k]) * 255.0)
            if d > worst:
                worst, where = d, "%s at t=%.1f" % (name, t)
    ok(worst < 0.01, "the ported show player differs by %.3f counts (%s)"
       % (worst, where))
    note("offline: %d shows, %d frames each, worst %.4f counts out of 255 (%s)"
         % (len(names), len(times), worst, where or "exact"))


def t_offline_drive_matches_the_analysis():
    """The carried-over analysis is the laptop's, to a byte of quantising.

    mau5drive writes the envelopes at 20 Hz in eight bits, so this
    cannot be exact and should not be: what it has to be is close
    enough that a show driven by the file looks like the same show
    driven by the analysis.  A byte is 1/255 and the curves are
    multiplied into the frame, so the bar is a few counts.

    The beat grid is not quantised at all -- it is the same float
    times -- so beat_phase has to agree closely, and a drifting grid
    would show up here before it showed up as a show that lands late.
    """
    import mau5drive
    import mau5show
    made = mau5drive.build(verbose=False)
    if not made:
        return note("offline: no analyses to carry over")
    worst_lvl = worst_ph = 0.0
    checked = 0
    for name, info in sorted(made.items()):
        show = json.load(open(os.path.join(HERE, "shows", name + ".json")))
        npz = os.path.join(HERE, "shows", show["analysis"])
        music = mau5show.Music(show.get("track", ""), fps=show.get("fps", 40),
                               cache=npz)
        path = os.path.join(HERE, "data", "offline", info["file"])
        times = [t for t in (5.0, 30.0, 61.5, 120.0, 180.0)
                 if t < music.duration - 1]
        res = _node("drivetest.js", {"file": path, "times": times})
        if res is None:
            return note("offline: node not installed, the drive went unchecked")
        eq(res["beats"], len(music.beats), "%s lost beats in packing" % name)
        eq(res["bars"], len(music.bars), "%s lost bars in packing" % name)
        for row in res["rows"]:
            t = row["t"]
            worst_lvl = max(worst_lvl, abs(row["level"] - music.level_at(t)))
            worst_ph = max(worst_ph, abs(row["phase"] - music.beat_phase(t)))
            eq(row["down"], bool(music.is_downbeat(t)),
               "%s disagrees about a downbeat at %.1fs" % (name, t))
            checked += 1
    ok(worst_lvl < 0.03, "the carried level is %.3f off the analysis" % worst_lvl)
    ok(worst_ph < 0.02, "the carried beat phase is %.3f off" % worst_ph)
    note("offline: %d drive samples over %d tracks, level within %.3f, "
         "beat phase within %.3f" % (checked, len(made), worst_lvl, worst_ph))


def t_offline_page_is_self_contained():
    """A page that fetches anything is a page that is blank at a show."""
    import mau5offline
    path, raw, gz = mau5offline.build(verbose=False)
    text = raw.decode()
    for part in ("MAU5_DATA", "makeHelmet", "PowerGuard", "class Link"):
        ok(part in text, "the built page is missing %s" % part)
    ok("<!--@" not in text, "a template placeholder survived the build")
    # Nothing the page needs to *render* may come from off the
    # controller.  Calling an API when the user asks is a different
    # thing, and the page has to work with no internet at all, which
    # is what the host list below is checked against.
    import re as _re
    loads = _re.findall(r"""(?:src|href)\s*=\s*["']\s*(?:https?:)?//[^"']+"""
                        r"""|@import[^;]*//[^;]*"""
                        r"""|url\(\s*["']?(?:https?:)?//[^)]*""", text)
    eq(loads, [], "the built page loads something from off the controller")
    ok("integrity=" not in text, "the built page has a subresource hash")
    hosts = sorted(set(_re.findall(r"https://([a-z0-9.-]+)/", text)))
    eq(hosts, ["accounts.spotify.com", "api.spotify.com"],
       "the page reaches hosts it did not before: %s" % hosts)
    # Room on the controller is the constraint: WLED's filesystem is
    # around 700 kB on the smaller partition layouts.
    ok(len(gz) < 200 * 1024, "the page is %.0f kB gzipped, too big to be sure "
       "it fits" % (len(gz) / 1024.0))
    note("offline: the page is %.0f kB, %.0f kB gzipped"
         % (len(raw) / 1024.0, len(gz) / 1024.0))


def t_offline_limiter_matches_the_budget():
    """The controller's own limiter is set from the same power model.

    Offline there is no Pixels.send between a preset and the strips,
    so WLED's automatic brightness limiter is the only clamp a bug in
    the page cannot get past.  It has to be set, and it has to be set
    to the number the rest of the suite believes in.
    """
    import mau5offline
    import mau5power
    power = json.load(open(os.path.join(HERE, "data", "cal", "power.json")))
    cfg = mau5offline.wanted_cfg(power)
    led = cfg["hw"]["led"]
    want = power["budget_ma"] + power["count"] * mau5power.MA_PER_LED_STANDBY
    eq(led["maxpwr"], int(round(want)), "maxpwr")
    eq(led["ledma"], int(round(mau5power.MA_PER_LED_FULL_WHITE)), "ledma")
    eq(cfg["ap"]["behav"], 2, "the access point must come up unconditionally")
    ok("psk" not in cfg["ap"], "a default access point password must not ship "
                               "in a public repository")


GROUPS = {
    "map": [t_map, t_map_matches_walk, t_frame, t_masks, t_strip_orientation, t_ears_match,
            t_map_adjustments],
    "presets": [t_presets, t_preset_params, t_text_bitmap, t_accepts],
    "power": [t_power_budget, t_power_board_limit, t_guard_in_send,
              t_thermal, t_thermal_never_exceeds, t_power_regions, t_power_failsafe,
              t_floor_holds_the_shape, t_connector_limit,
              t_off_does_not_stream_black],
    "colour": [t_colour_correction],
    "shows": [t_lockable_presets, t_beat_lock_lands_on_the_grid, t_shows, t_show_player, t_crossfade, t_beat_helpers,
              t_analysis_cache],
    "wire": [t_ddp_packet, t_lan_ip],
    "offline": [t_offline_engine_matches_python,
                t_offline_guard_matches_python,
                t_offline_encoder_roundtrip,
                t_offline_oversize_is_caught,
                t_offline_shows_match_python,
                t_offline_drive_matches_the_analysis,
                t_offline_page_is_self_contained,
                t_offline_limiter_matches_the_budget],
    "camera": [t_eye_after],
    "audio": [t_tempo_truth, t_beat_alignment],
}

# More tests can live in tests_more/<name>.py, each defining GROUP, a
# list of t_ functions run under the module's name -- so several changes
# can add tests without all editing the table above.
def _more():
    import importlib.util
    d = os.path.join(HERE, "tests_more")
    if not os.path.isdir(d):
        return
    # One copy of this module, so `from test_mau5 import note` in a
    # tests_more file reaches the NOTES that get printed.
    sys.modules.setdefault("test_mau5", sys.modules[__name__])
    for fn in sorted(os.listdir(d)):
        if not fn.endswith(".py") or fn.startswith("_"):
            continue
        spec = importlib.util.spec_from_file_location("tests_more_" + fn[:-3],
                                                      os.path.join(d, fn))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        # Added to a group of the same name, never instead of it: a file
        # called shows.py once silently dropped the main show tests.
        have = GROUPS.setdefault(fn[:-3], [])
        names = {f.__name__ for f in have}
        have.extend(f for f in getattr(mod, "GROUP", []) if f.__name__ not in names)


_more()

if __name__ == "__main__":
    want = sys.argv[1:] or sorted(GROUPS)
    for g in want:
        if g not in GROUPS:
            raise SystemExit("no group %r.  Have: %s" % (g, ", ".join(sorted(GROUPS))))
        for fn in GROUPS[g]:
            check(g, fn.__name__[2:], fn)      # strip the "t_" prefix only
    for g, n in PASS:
        print("  ok    %-9s %s" % (g, n))
    for g, n, msg, tb in FAIL:
        print("  FAIL  %-9s %s\n          %s" % (g, n, msg))
    for m in NOTES:
        print("  note: %s" % m)
    print("\n%d passed, %d failed" % (len(PASS), len(FAIL)))
    if FAIL:
        print("\n--- first traceback ---\n%s" % FAIL[0][3])
    sys.exit(1 if FAIL else 0)
