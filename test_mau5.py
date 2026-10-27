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
    eq(len(rows), 622, "led count")
    eq([r["index"] for r in rows], list(range(622)), "indices contiguous")
    for r in rows:
        for k in ("x", "y", "z"):
            ok(math.isfinite(r[k]), "non-finite %s at %d" % (k, r["index"]))
        ok(0.0 <= r["u"] <= 1.0, "u out of range at %d" % r["index"])

    shell = [r for r in rows if r["region"] == "shell"]
    eq(len(shell), 399, "shell count")
    for r in shell:
        rad = math.sqrt(r["x"] ** 2 + r["y"] ** 2 + r["z"] ** 2)
        ok(abs(rad - 173.04) < 0.5, "shell led %d off the sphere (%.2f)"
           % (r["index"], rad))

    # the swap flag must mark exactly the measured span
    sw = [r["index"] for r in rows if r["swap_rg"]]
    eq((min(sw), max(sw), len(sw)), (492, 527, 36), "swap span")

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
    import mau5wled
    p = mau5wled.Pixels("127.0.0.1", 622)
    ident = np.array([0, 1, 2])
    swapped = np.array([1, 0, 2])
    for i in (0, 398, 491, 528, 621):
        ok((p.perm[i] == ident).all(), "led %d should be identity" % i)
    for i in (492, 500, 527):
        ok((p.perm[i] == swapped).all(), "led %d should be R/G swapped" % i)
    buf = np.zeros((622, 3), np.uint8)
    buf[500] = (200, 0, 0)
    buf[400] = (200, 0, 0)
    out = p.apply_order(buf)
    eq(tuple(out[500]), (0, 200, 0), "rim red must leave as green")
    eq(tuple(out[400]), (200, 0, 0), "tube red must leave unchanged")


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
    for t in range(0, 300, 1):                 # run it into the ground
        out, rep = g.apply(buf, now=float(t))
    ok(rep["thermal"]["full_pct"] > 95, "the bucket should be empty by now")

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
    for st in strips["strips"]:
        eq((st["start"], st["start"] + st["count"] - 1), (rim_lo, rim_hi),
           "strips.json does not cover exactly the mapped rims")


def t_show_player():
    import mau5show
    f = [x for x in os.listdir(mau5show.SHOWS) if x.endswith(".json")]
    ok(f, "no shows to play")
    show = json.load(open(os.path.join(mau5show.SHOWS, sorted(f)[0])))
    pl = mau5show.Player(show)
    for t in (0.0, show["duration"] * 0.5, show["duration"] - 0.1):
        out = pl.frame(t)
        eq(out.shape, (622, 3), "player frame shape")
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
    """
    import mau5power as P
    g = P.load()
    ok(g.thermal is not None, "no thermal budget configured")
    th = g.thermal
    buf = np.full((g.count, 3), 255, np.uint8)
    dark = np.zeros((g.count, 3), np.uint8)
    t, first, settled = 0.0, None, None
    for step in range(400):
        out, rep = g.apply(buf, now=t); t += 1.0
        led = rep["watts"] - th.standby_w
        if first is None:
            first = led
        settled = led
    ok(first > settled * 2.5,
       "it never eased off: %.1f W at the start, %.1f W after 400 s"
       % (first, settled))
    ok(abs((settled + th.standby_w) - th.sustained_w) < 1.0,
       "settled at %.1f W total, expected about %.1f"
       % (settled + th.standby_w, th.sustained_w))
    # and quiet must give the headroom back
    for step in range(900):
        g.apply(dark, now=t); t += 1.0
    out, rep = g.apply(buf, now=t)
    ok(rep["watts"] - th.standby_w > first * 0.95,
       "a burst after a long rest should be full brightness again, got %.1f W"
       % (rep["watts"] - th.standby_w))
    ok(th.level >= 0 and th.level <= th.burst_j + 1e-6, "bucket left out of range")


def t_thermal_never_exceeds():
    """Whatever the content, sustained delivery must stay at or under
    the configured ceiling."""
    import mau5power as P
    g = P.load()
    th = g.thermal
    rng = np.random.default_rng(11)
    t, total_j = 0.0, 0.0
    DUR = 1200
    for step in range(DUR):
        buf = rng.integers(150, 256, (g.count, 3), dtype=np.uint8)
        out, rep = g.apply(buf, now=t)
        total_j += rep["watts"] * 1.0
        t += 1.0
    avg = total_j / DUR
    ok(avg <= th.sustained_w + 1.5,
       "20 minutes of bright content averaged %.1f W, ceiling is %.1f"
       % (avg, th.sustained_w))



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


GROUPS = {
    "map": [t_map, t_frame, t_masks, t_strip_orientation, t_ears_match],
    "presets": [t_presets, t_preset_params, t_text_bitmap, t_accepts],
    "power": [t_power_budget, t_power_board_limit, t_guard_in_send,
              t_thermal, t_thermal_never_exceeds, t_power_regions,
              t_floor_holds_the_shape],
    "colour": [t_colour_correction],
    "shows": [t_shows, t_show_player, t_crossfade, t_beat_helpers,
              t_analysis_cache],
    "wire": [t_ddp_packet, t_lan_ip],
    "camera": [t_eye_after],
    "audio": [t_tempo_truth, t_beat_alignment],
}

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
