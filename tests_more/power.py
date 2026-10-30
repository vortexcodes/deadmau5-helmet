"""tests_more/power -- the guard cannot be switched off, and presets cannot be
made to ask it to.

Every one of these was a way through, found by reading rather than by
the helmet: a single NaN frame that turned off the phone guard's
governor and thermal ramp for the life of the page, a profile one LED
longer than the frame doing the same, a slider whose left end divided by
zero, a float frame wrapped by a uint8 cast before the guard ever saw
it.  And two that were not unsafe, only ugly, and are tested because the
fix has a safety property worth pinning: the soft ceiling never goes
above the hard one, and the governor's slow release never goes above the
budget.

Nothing here talks to a controller.  The JavaScript is run under node,
the network calls are caught before they leave.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from test_mau5 import ok, eq, note, HERE

import base64
import json
import math
import shutil
import subprocess
import threading

import numpy as np

POWER = os.path.join(HERE, "data", "cal", "power.json")
GUARD_JS = os.path.join(HERE, "remote", "offline", "guard.js")
ENGINE_JS = os.path.join(HERE, "remote", "offline", "engine.js")

# Runs frames through guard.js exactly as the phone does (one guard, its
# state carried from frame to frame, the frame buffer guarded in place)
# and hands back every report and frame.  The frames go over as float32
# bytes, so NaN and infinity arrive as themselves -- JSON has neither.
_GUARD_RUNNER = r"""
'use strict';
let raw = '';
process.stdin.setEncoding('utf8');
process.stdin.on('data', c => { raw += c; });
process.stdin.on('end', () => {
  const job = JSON.parse(raw);
  const G = require(job.guard);
  const g = new G.PowerGuard(job.power);
  const res = [];
  for (const f of job.frames) {
    const b = Buffer.from(f.data, 'base64');
    const buf = new Float32Array(new Uint8Array(b).buffer);   // a copy, so aligned
    const rep = g.apply(buf, buf, f.t, 1);
    res.push({ sent: rep.sent_ma, budget: rep.budget_ma,
               level: rep.thermal ? rep.thermal.level_j : null,
               scale: g._govS,
               f: Buffer.from(buf.buffer).toString('base64') });
  }
  process.stdout.write(JSON.stringify(res));
});
"""

_LISTS_RUNNER = r"""
const E = require(process.argv[1]);
process.stdout.write(JSON.stringify({ positive: [...E.POSITIVE].sort(),
                                      counts: [...E.COUNTS].sort() }));
"""


def _have_node():
    return shutil.which("node") is not None


def _node(script, job=None, args=()):
    p = subprocess.run(["node", "-e", script] + list(args),
                       input=json.dumps(job) if job is not None else "",
                       capture_output=True, text=True, cwd=HERE, timeout=300)
    if p.returncode:
        raise AssertionError("node failed:\n%s" % p.stderr[-2000:])
    return json.loads(p.stdout)


def _b64(frame):
    return base64.b64encode(np.ascontiguousarray(frame, "<f4").tobytes()).decode()


def _js_guard(frames, power=None):
    """[(frame, now)] through guard.js -> list of reports, or None."""
    if not _have_node():
        return None
    power = power or json.load(open(POWER))
    job = {"guard": GUARD_JS, "power": power,
           "frames": [{"data": _b64(f), "t": float(t)} for f, t in frames]}
    return _node(_GUARD_RUNNER, job)


def _f32(b64):
    return np.frombuffer(base64.b64decode(b64), "<f4")


def _helmet():
    import mau5engine as E
    return E.Helmet()


# ----------------------------------------------------------------------
def t_nan_frame_cannot_switch_the_guard_off():
    """One NaN frame used to disable the phone's governor for good.

    clamp() passed NaN, the frame's current came out NaN, no budget
    compares greater than NaN, and the thermal level went NaN and stayed
    there.  Reproduced in node on the real bundle: ten minutes of full
    white after one rainbow frame at period 0 sent 1940 mA against a
    1000 mA budget, where a fresh guard sent 290.  Both guards, the same
    frames, the same answers, and every frame inside the budget.
    """
    import mau5power
    h = _helmet()
    n = h.n
    white = np.full((n, 3), 255.0, np.float32)
    nan = white.copy()
    nan[::3, 1] = np.nan
    nan[5] = (np.inf, -np.inf, np.nan)
    frames = [(white, 0.0), (nan, 0.04),
              (np.full((n, 3), np.nan, np.float32), 0.08)]
    t = 0.12
    while t < 600.0:                       # ten minutes of white, two frames a second
        frames.append((white, t))
        t += 0.5
    g = mau5power.load(count=n)
    py = []
    for f, now in frames:
        out, rep = g.apply(f, now=now)
        py.append((out, rep))
        ok(math.isfinite(g.thermal.level),
           "the Python thermal level went %r" % g.thermal.level)
        ok(rep["sent_ma"] <= rep["budget_ma"] + 0.5, "Python sent %.0f mA against %.0f "
           "at t=%.2f" % (rep["sent_ma"], rep["budget_ma"], now))
    ok(py[-1][1]["sent_ma"] < 500, "after ten minutes of white the Python guard still "
       "sends %.0f mA: the thermal ramp is not working" % py[-1][1]["sent_ma"])
    js = _js_guard(frames)
    if js is None:
        return note("power: node not installed, the JS guard's NaN handling went unchecked")
    worst = 0.0
    for (out, rep), r, (f, now) in zip(py, js, frames):
        ok(r["level"] is not None and math.isfinite(r["level"]),
           "the JS thermal level went %r at t=%.2f" % (r["level"], now))
        ok(r["budget"] is not None and r["sent"] <= r["budget"] + 0.5,
           "JS sent %r mA against %r at t=%.2f" % (r["sent"], r["budget"], now))
        worst = max(worst, abs(r["sent"] - rep["sent_ma"]))
        ok(np.abs(_f32(r["f"]).reshape(-1, 3) - out).max() <= 1.0,
           "the two guards disagree about a NaN frame's LEDs at t=%.2f" % now)
    ok(worst <= 0.1, "the two guards disagree by %.2f mA on frames with NaN in" % worst)
    ok(js[-1]["sent"] < 500, "after ten minutes of white the JS guard still sends "
       "%.0f mA" % js[-1]["sent"])


def t_profile_longer_than_the_frame():
    """A power.json counting more LEDs than the frame must still limit it.

    The phone guard read past the frame's end into undefined -- NaN in
    the governor's sum, which then never found the frame over budget:
    1950 mA on full white against 1000, with count 622 and a 621-LED map.
    The Python raised on the same mismatch instead.  And the other way
    round, an LED the profile does not describe goes out dark rather
    than unguarded.
    """
    import mau5power
    h = _helmet()
    n = h.n
    white = np.full((n, 3), 255.0, np.float32)
    power = json.load(open(POWER))
    longer = dict(power, count=n + 1)
    g = mau5power.PowerGuard(n + 1, mau5power.load(count=n).regions, power["budget_ma"],
                             thermal=None)
    out, rep = g.apply(white, now=0.0)
    eq(out.shape, (n, 3), "the Python guard's frame")
    ok(rep["sent_ma"] <= power["budget_ma"] + 0.5,
       "Python sent %.0f mA with a profile one LED longer than the frame"
       % rep["sent_ma"])
    js = _js_guard([(white, 0.0)], power=longer)
    if js is None:
        return note("power: node not installed, the JS frame-length check went unchecked")
    ok(js[0]["sent"] <= power["budget_ma"] + 0.5,
       "JS sent %.0f mA with a profile one LED longer than the frame" % js[0]["sent"])
    shorter = dict(power, count=n - 1)
    js = _js_guard([(white, 0.0)], power=shorter)
    eq(float(_f32(js[0]["f"]).reshape(-1, 3)[n - 1].max()), 0.0,
       "an LED the profile does not cover went out lit")


def t_soft_ceiling_stays_under_the_hard_one():
    """The knee only ever takes current away.

    Every input level on every region: never above the ceiling, never
    above what was asked, never darker for asking more, the tubes (which
    have no ceiling below full) untouched, and full drive within 2% of
    the ceiling it was tuned to.  Then the reason for it: the eyes keep
    a gradient instead of becoming two flat discs.
    """
    import mau5power, mau5engine as E
    h = _helmet()
    g = mau5power.load(count=h.n)
    levels = np.arange(256, dtype=np.float32)
    for r in g.regions:
        frame = np.zeros((h.n, 3), np.float32)
        out = []
        for v in levels:
            frame[r.lo] = (v, v, v)
            o = mau5power.PowerGuard(h.n, g.regions, 1e9, g.default_ceiling)
            got, _ = o.apply(frame, now=0.0)
            out.append(int(got[r.lo, 0]))
        out = np.array(out)
        ok(out.max() <= r.ceiling, "%s went to %d over its ceiling %d"
           % (r.name, out.max(), r.ceiling))
        ok((out <= levels.astype(int)).all(), "%s brightened an LED" % r.name)
        ok((np.diff(out) >= 0).all(), "%s got darker for asking more" % r.name)
        ok(out[255] >= r.ceiling * 0.98 - 1, "%s at full drive gives %d, well short "
           "of its ceiling %d" % (r.name, out[255], r.ceiling))
        if r.ceiling >= 255:
            ok((out == levels.astype(int)).all(), "%s has no ceiling to bend to "
               "and was bent anyway" % r.name)

    raw = np.asarray(E.make("eyes").render(h, 1.3), float)
    out, _ = g.apply(raw, now=0.0)
    v = out[h.shell].max(1).astype(float)
    lit = v > 0
    flat = float((v[lit] >= 0.9 * v.max()).mean())
    ok(flat < 0.6, "%.0f%% of the eyes' lit LEDs are within 10%% of the brightest: "
       "still flat discs" % (100 * flat))
    note("power: the eyes keep %.0f%% of their lit LEDs in the top tenth (80%% "
         "under a hard ceiling)" % (100 * flat))


def _bright_dim(h):
    bright = np.full((h.n, 3), 255.0, np.float32)
    dim = np.zeros((h.n, 3), np.float32)
    dim[h.shell] = (40, 0, 60)
    dim[h.tubes] = (0, 60, 90)
    return bright, dim


def t_governor_gives_light_back_slowly():
    """Down at once, up gently, and never over budget either way.

    A full-white frame is governed hard; the dim frames after it are
    under budget on their own and used to snap straight back, which on
    content that alternates is the shell pumping six times as hard as
    the ears.  Now the scale climbs at most GOV_RISE e-folds a second,
    a brighter frame is still cut on the frame it arrives, and a caller
    that holds the clock still -- mau5ctl's preview does, to keep the
    bucket full -- still gets its light back.
    """
    import mau5power
    h = _helmet()
    bright, dim = _bright_dim(h)
    g = mau5power.load(count=h.n)
    _, free = mau5power.PowerGuard(h.n, g.regions, 1e9, g.default_ceiling).apply(dim, now=0.0)
    dt = 1 / 25.0
    t, scales, sent = 0.0, [], []
    out, rep = g.apply(bright, now=t)
    ok(rep["governor_hit"] and g._gov_s < 0.9, "full white should be governed")
    s0 = g._gov_s
    for k in range(1, 200):
        t += dt
        out, rep = g.apply(dim, now=t)
        ok(rep["sent_ma"] <= rep["budget_ma"] + 0.5, "over budget while climbing back")
        scales.append(g._gov_s)
        sent.append(rep["sent_ma"])
    prev = s0
    for s in scales:
        ok(s <= min(1.0, max(prev, mau5power.GOV_FROM)
                    * math.exp(mau5power.GOV_RISE * dt)) + 1e-9,
           "the scale jumped from %.3f to %.3f in one frame" % (prev, s))
        prev = s
    ok(sent[0] < free["sent_ma"] - 1.0, "the first dim frame snapped straight back")
    ok(scales[-1] == 1.0 and abs(sent[-1] - free["sent_ma"]) < 0.5,
       "eight seconds on, the dim frame is still held down (scale %.3f)" % scales[-1])

    # a brighter frame is cut on the frame it arrives
    out, rep = g.apply(bright, now=t + dt)
    ok(rep["sent_ma"] <= rep["budget_ma"] + 0.5,
       "a bright frame after a dim one went %.0f mA over" % (rep["sent_ma"] - rep["budget_ma"]))

    # the clock held still: it still climbs, a frame at a time
    g2 = mau5power.load(count=h.n)
    g2.apply(bright, now=5.0)
    for _ in range(400):
        g2.apply(dim, now=5.0)
    eq(g2._gov_s, 1.0, "with the clock held still the governor never let go")


def t_governor_ramp_matches_python():
    """The phone's governor releases exactly as the laptop's does.

    The existing cross-check runs frames half a second apart, where the
    ramp hardly binds.  These are 25 a second, bright and dim in turn,
    with NaN frames among them.
    """
    import mau5power
    h = _helmet()
    bright, dim = _bright_dim(h)
    rng = np.random.default_rng(5)
    frames, t = [], 0.0
    for k in range(150):
        if k % 17 == 3:
            f = rng.uniform(0, 255, (h.n, 3)).astype(np.float32)
            f[rng.integers(0, h.n, 40), 1] = np.nan
        elif (k // 6) % 2:
            f = bright * rng.uniform(0.3, 1.0)
        else:
            f = dim
        frames.append((f.astype(np.float32), t))
        t += 0.04
    g = mau5power.load(count=h.n)
    py, scales = [], []
    for f, now in frames:
        py.append(g.apply(f, now=now))
        scales.append(g._gov_s)
    js = _js_guard(frames)
    if js is None:
        return note("power: node not installed, the JS governor ramp went unchecked")
    worst_ma = worst_led = worst_s = 0.0
    held = 0
    for (out, rep), r in zip(py, js):
        worst_ma = max(worst_ma, abs(rep["sent_ma"] - r["sent"]))
        worst_led = max(worst_led, float(np.abs(_f32(r["f"]).reshape(-1, 3) - out).max()))
        ok(r["sent"] <= r["budget"] + 0.5, "the JS guard went over budget")
    for s, r in zip(scales, js):
        worst_s = max(worst_s, abs(s - r["scale"]))
        held += r["scale"] < 1.0 and r["sent"] < r["budget"] - 1.0
    ok(held > 10, "the ramp hardly bound (%d frames); the test is not testing it" % held)
    ok(worst_ma <= 0.1, "the governors disagree by %.2f mA" % worst_ma)
    ok(worst_led <= 1.0, "the governors disagree by %.1f counts on an LED" % worst_led)
    ok(worst_s <= 1e-4, "the governors' scales disagree by %.2g" % worst_s)


# ----------------------------------------------------------------------
def _extremes(spec):
    """The values a slider end, a Randomise, a saved setting or a typo give."""
    out = []
    for s in spec:
        if s["kind"] != "number":
            continue
        v = s["value"]
        vals = [0, -1, s["min"], s["max"], round(s["min"] + 0.48 * s["step"], 4)]
        if isinstance(v, int):
            vals.append(v + 0.48)
        out.append((s["name"], vals))
    return out


def t_slider_ends_render():
    """Every numeric parameter, at every end a user can reach, renders.

    rainbow's period at 0 was a ZeroDivisionError here and NaN on every
    pixel on the phone; eq's bands one notch along was 12.48, an
    IndexError here and a RangeError there.  Finite and in step with
    the port, for every preset.
    """
    import mau5engine as E
    import mau5offline
    h = _helmet()
    jobs = []
    for name in sorted(E.REGISTRY):
        for k, vals in _extremes(E.REGISTRY[name].spec()):
            for v in vals:
                for t in (0.37, 2.5):
                    jobs.append({"preset": name, "params": {k: v}, "t": t, "reset": True})
    py = []
    for j in jobs:
        try:
            f = np.asarray(E.make(j["preset"], **j["params"]).render(h, j["t"]), float)
        except Exception as e:
            raise AssertionError("%s %s raised %s: %s" % (j["preset"], j["params"],
                                                         type(e).__name__, e))
        ok(np.isfinite(f).all(), "%s %s rendered non-finite" % (j["preset"], j["params"]))
        py.append(f)
    for name in sorted(E.REGISTRY):
        for k, d in E.REGISTRY[name].params.items():
            if isinstance(d, (int, float)) and not isinstance(d, bool):
                for bad in (float("nan"), float("inf"), None, "x"):
                    f = np.asarray(E.make(name, **{k: bad}).render(h, 1.0), float)
                    ok(np.isfinite(f).all(), "%s %s=%r rendered non-finite" % (name, k, bad))
    if not _have_node():
        return note("power: node not installed, the JS slider ends went unchecked")
    # JSON carries None as null, which is what a saved NaN comes back as
    for name in sorted(E.REGISTRY):
        for k, d in E.REGISTRY[name].params.items():
            if isinstance(d, (int, float)) and not isinstance(d, bool):
                jobs.append({"preset": name, "params": {k: None}, "t": 1.0, "reset": True})
                py.append(np.asarray(E.make(name, **{k: None}).render(h, 1.0), float))
    data = mau5offline.bundle()
    p = subprocess.run(["node", os.path.join(HERE, "remote", "offline", "crosscheck.js")],
                       input=json.dumps({"data": data, "jobs": jobs}),
                       capture_output=True, text=True, cwd=HERE, timeout=600)
    if p.returncode:
        raise AssertionError("crosscheck.js failed:\n%s" % p.stderr[-2000:])
    res = json.loads(p.stdout)
    worst, where = 0.0, ""
    for j, a, r in zip(jobs, py, res):
        b = _f32(r["f"]).reshape(-1, 3).astype(float)
        ok(np.isfinite(b).all(), "the phone's %s %s rendered non-finite"
           % (j["preset"], j["params"]))
        d = float(np.abs(np.clip(a, 0, 255) - np.clip(b, 0, 255)).max())
        if d > worst:
            worst, where = d, "%s %s" % (j["preset"], j["params"])
    ok(worst <= 0.51, "at a slider's end the port differs by %.3f counts (%s)"
       % (worst, where))
    note("power: %d slider ends rendered in both languages, worst %.4f counts"
         % (len(jobs), worst))


def t_spec_never_offers_a_bad_value():
    """The UI cannot ask for what make() would have to correct."""
    import mau5engine as E
    for name, cls in sorted(E.REGISTRY.items()):
        for s in cls.spec():
            if s["kind"] != "number":
                continue
            k, v = s["name"], s["value"]
            if isinstance(v, int):
                eq(s["step"], 1, "%s.%s is a count and should step by one" % (name, k))
            if k in E.POSITIVE and v > 0:
                ok(s["min"] > 0, "%s.%s offers zero, which it divides by" % (name, k))
            if k in E.UNIT:
                ok(s["max"] <= 1.0, "%s.%s offers %.2f, beyond full" % (name, k, s["max"]))
            got = E.make(name, **{k: s["min"]}).p[k]
            ok(abs(got - s["min"]) <= 0.0006, "%s.%s at its slider's end is moved by "
               "make() from %r to %r" % (name, k, s["min"], got))


def t_engine_lists_match():
    """engine.js names the same divisors and counts as the Python."""
    import mau5engine as E
    counts = sorted({k for c in E.REGISTRY.values() for k, v in c.params.items()
                     if isinstance(v, int) and not isinstance(v, bool)})
    if not _have_node():
        return note("power: node not installed, engine.js's lists went unchecked")
    got = _node(_LISTS_RUNNER, args=[ENGINE_JS])
    eq(got["positive"], sorted(E.POSITIVE), "engine.js POSITIVE")
    eq(got["counts"], counts, "engine.js COUNTS")


def t_unknown_preset_is_an_ordinary_error():
    """A typo in a cue must not kill the frame loop in silence.

    make() raised SystemExit, which `except Exception` does not catch,
    and a thread that dies of it prints nothing.
    """
    import mau5engine as E
    caught = []

    def loop():
        try:
            E.make("sparkles")
        except Exception as e:
            caught.append(e)

    th = threading.Thread(target=loop)
    th.start()
    th.join()
    eq(len(caught), 1, "a frame loop's `except Exception` did not see the bad name")
    ok(isinstance(caught[0], ValueError), "expected ValueError, got %r" % caught[0])


# ----------------------------------------------------------------------
def _quiet_pixels(count, guard):
    """A Pixels whose datagrams are caught instead of sent."""
    import mau5wled
    p = mau5wled.Pixels("127.0.0.1", count, guard=guard, strips=False)
    p.sock.close()
    sent = []

    class _Sock:
        def sendto(self, data, addr):
            sent.append(data)

        def close(self):
            pass

    p.sock = _Sock()
    return p, sent


def t_send_clips_before_it_casts():
    """A float frame out of 0..255 is clipped, not wrapped.

    np.asarray(buf, np.uint8) first, guard second: -1 went out as 255,
    256 as 0, 300 as 44, so plasma with sat 3 lit pastels where the
    simulator showed colour and breathe's peak flickered to black.
    """
    import mau5power
    h = _helmet()
    frame = np.zeros((h.n, 3), float)
    frame[0] = (-1.0, 256.0, 300.0)
    frame[1] = (-714.0, np.nan, np.inf)
    tube = int(np.flatnonzero(h.tubes)[0])
    frame[tube] = (300.0, -5.0, 255.5)
    p, sent = _quiet_pixels(h.n, False)
    p.send(frame)
    eq(tuple(int(x) for x in p.last_sent[0]), (0, 255, 255), "unguarded LED 0")
    eq(tuple(int(x) for x in p.last_sent[1]), (0, 0, 255), "unguarded LED 1")
    ok(len(sent) > 0, "nothing was sent")
    g = mau5power.load(count=h.n)
    q, _ = _quiet_pixels(h.n, g)
    q.send(frame)
    eq(int(q.last_sent[0, 0]), 0, "a negative channel came out lit through the guard")
    ok(int(q.last_sent[0, 1]) > 50 and int(q.last_sent[0, 2]) > 50,
       "256 and 300 should be near the shell's ceiling, not wrapped to dark: %s"
       % (q.last_sent[0],))
    eq(int(q.last_sent[1, 0]), 0, "-714 came out lit")
    eq(int(q.last_sent[1, 1]), 0, "NaN came out lit")
    eq(tuple(int(x) for x in q.last_sent[tube]), (255, 0, 255), "a tube LED out of range")
    ok(q.last_power["sent_ma"] <= g.budget_ma + 0.5, "send did not hold the budget")


class _Recorder:
    def __init__(self, cfg=None):
        self.posts, self._cfg = [], cfg

    def post(self, path, obj):
        self.posts.append((path, json.loads(json.dumps(obj))))
        return {}

    def cfg(self):
        return json.loads(json.dumps(self._cfg))


def t_realtime_disarms_the_dead_man():
    """Taking over from the phone switches its nightlight off.

    Left armed, it fired a minute into mau5ctl's stream, set brightness
    0, and the helmet went black under a running preset.
    """
    import mau5wled
    w = mau5wled.WLED("127.0.0.1:9")
    rec = _Recorder()
    w._post = rec.post
    w.realtime(True, brightness=255)
    eq(len(rec.posts), 1, "one POST")
    path, body = rec.posts[0]
    eq(path, "/json/state", "where the hand-over goes")
    eq(body.get("nl"), {"on": False}, "the dead man must be disarmed")
    eq(body.get("lor"), 0, "a live override must be cleared")
    eq((body.get("on"), body.get("live"), body.get("bri")), (True, True, 255),
       "the hand-over itself")


def t_one_bus_keeps_the_limiter():
    """Collapsing to one bus must not reset the per-bus limiter."""
    import mau5wled
    old = {"start": 0, "len": 600, "pin": [16], "order": 0, "type": 22,
           "ref": False, "rev": True, "skip": 2, "rgbwm": 0, "freq": 0,
           "maxpwr": 1621, "ledma": 19}
    w = mau5wled.WLED("127.0.0.1:9")
    rec = _Recorder({"hw": {"led": {"ins": [old, dict(old, start=600, len=30, pin=[2])]}}})
    w._post, w.cfg = rec.post, rec.cfg
    bus = w.one_bus(622)                  # sleeps 1.5 s for the bus manager
    path, body = rec.posts[-1]
    got = body["hw"]["led"]["ins"]
    eq(len(got), 1, "one bus")
    eq(got[0], bus, "what was posted is what was returned")
    eq((got[0]["maxpwr"], got[0]["ledma"]), (1621, 19), "the bus's limiter")
    eq((got[0]["start"], got[0]["len"], got[0]["pin"], got[0]["rev"], got[0]["skip"]),
       (0, 622, [16], False, 0), "the new layout")
    eq(body["hw"]["led"]["total"], 622, "total")


def _main_suite_power():
    """The main suite's own power tests, so they keep running.

    test_mau5 files a tests_more module under the module's name, and
    this one's name is a group the main suite already has: GROUPS["power"]
    is replaced by this file's GROUP, and the ten tests that were there --
    the budget, the board limit, the thermal bucket -- stopped running
    without a word.  So they are carried along.  The running script's
    own functions are preferred, so their notes still print, and only
    functions from that module are taken, so a second load of this file
    cannot double them up.
    """
    import __main__
    for mod in (__main__, sys.modules.get("test_mau5")):
        groups = getattr(mod, "GROUPS", None)
        if groups and "power" in groups:
            return [f for f in groups["power"]
                    if getattr(f, "__module__", None) == mod.__name__]
    return []


GROUP = _main_suite_power() + [
         t_nan_frame_cannot_switch_the_guard_off,
         t_profile_longer_than_the_frame,
         t_soft_ceiling_stays_under_the_hard_one,
         t_governor_gives_light_back_slowly,
         t_governor_ramp_matches_python,
         t_slider_ends_render,
         t_spec_never_offers_a_bad_value,
         t_engine_lists_match,
         t_unknown_preset_is_an_ordinary_error,
         t_send_clips_before_it_casts,
         t_realtime_disarms_the_dead_man,
         t_one_bus_keeps_the_limiter]
