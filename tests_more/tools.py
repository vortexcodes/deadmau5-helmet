"""The laptop-side tools: doctor, offline config/check/standby, mau5ctl,
the control page, the web simulator and the Spotify sign-in.

Nothing here touches the helmet or the network.  Controllers are stubs
that record what would have been sent; the one HTTP server is mau5ctl's
own handler on 127.0.0.1, so the JSON-only rule is tested the way a
browser meets it.
"""

import io
import json
import os
import sys
import threading
import time
import types
import contextlib

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from test_mau5 import ok, eq, note, HERE  # noqa: E402

import numpy as np  # noqa: E402


def _power():
    return json.load(open(os.path.join(HERE, "data", "cal", "power.json")))


# ----------------------------------------------------------------------
# WLED's own limiter
# ----------------------------------------------------------------------
def t_limiter_covers_the_sustained_case():
    """WLED's limiter gets what the helmet can hold indefinitely.

    It is a per-frame clamp with no bucket, so whatever it allows it
    allows for ever -- and it is the only clamp on standby, boot and
    the hand-back.  Checked in WLED's own arithmetic: the LED current a
    bus cap permits is the cap less 100 mA for the board and 1 mA per
    LED on the bus.  And it may never be above what it was before.
    """
    import mau5offline, mau5power, mau5wled
    p = _power()
    th = p["thermal"]
    sustained_led = (th["sustained_w"] - th["standby_w"]) / 12.0 * 1000.0
    old = p["budget_ma"] + p["count"] * mau5power.MA_PER_LED_STANDBY
    cap = mau5offline.limiter_ma(p)
    ok(cap <= old, "the limiter went up: %d > %d" % (cap, old))
    for bus_len in (p["count"], p["count"] + 1):
        buses = [{"start": 0, "len": bus_len, "maxpwr": 1621, "ledma": 19}]
        ins = mau5offline.wanted_cfg(p, buses=buses)["hw"]["led"]["ins"]
        allowed = ins[0]["maxpwr"] - mau5wled.WLED.MA_FOR_ESP - bus_len
        ok(allowed <= sustained_led + 1e-6,
           "a %d-LED bus would allow %d mA of LED current indefinitely, "
           "against %.0f sustained" % (bus_len, allowed, sustained_led))
        ok(allowed >= sustained_led - 5,
           "pointlessly far under the sustained figure: %d" % allowed)
        eq(ins[0]["ledma"], 19, "ledma")
    # several buses share it and still sum to no more
    two = [{"start": 0, "len": 400}, {"start": 400, "len": 222}]
    ins = mau5offline.wanted_cfg(p, buses=two)["hw"]["led"]["ins"]
    ok(sum(b["maxpwr"] for b in ins) <= cap + 1, "split buses exceed the cap")
    # no thermal model: exactly the old figure, never more
    q = dict(p)
    q.pop("thermal")
    eq(mau5offline.limiter_ma(q), int(round(old)), "no-thermal limiter")
    # a profile that sustains more than the budget cannot lift it either
    hot = dict(p, thermal=dict(th, sustained_w=60.0))
    eq(mau5offline.limiter_ma(hot), int(round(old)), "limiter above budget")


# ----------------------------------------------------------------------
# a controller that is not there
# ----------------------------------------------------------------------
def _stub_wled(count=622, maxpwr=None, ledma=19, ssid="mau5head-AP", segs=(0,)):
    import mau5offline, mau5wled
    p = _power()
    if maxpwr is None:
        maxpwr = mau5offline.limiter_ma(p)

    class W(mau5wled.WLED):
        def __init__(self):
            mau5wled.WLED.__init__(self, "127.0.0.1:9")    # never contacted
            self.posts = []
            self._cfg = {"ap": {"behav": 2, "ssid": ssid, "pskl": 10},
                         "hw": {"led": {"maxpwr": 1621, "ledma": 0,
                                        "ins": [{"start": 0, "len": count,
                                                 "pin": [16], "maxpwr": maxpwr,
                                                 "ledma": ledma}]}}}

        def info(self, refresh=False):
            return {"name": "stub", "ver": "0.15.4", "ip": "192.0.2.1",
                    "leds": {"count": count}, "uptime": 1}

        def cfg(self):
            return self._cfg

        def state(self):
            return {"seg": [{"id": i} for i in segs]}

        def _get(self, path):
            raise AssertionError("tried to read %s from the network" % path)

        def _post(self, path, obj):
            self.posts.append((path, obj))
            return {"success": True}
    return W()


def _doctor(w):
    import mau5doctor
    del mau5doctor.RESULTS[:]
    mau5doctor._helmet(w, w.info())
    out = list(mau5doctor.RESULTS)
    del mau5doctor.RESULTS[:]
    return out


def t_doctor_takes_622_and_never_raises_the_limiter():
    """622 and 621 are both right, and no fix ever raises the limiter.

    The doctor wanted 623 and offered `--one-bus 623 --allow 0.3`, which
    also wrote a 4274 mA bus limiter: four times what the helmet can
    sustain, on the one clamp WLED's own effects have.
    """
    import mau5offline
    want = mau5offline.limiter_ma(_power())
    for n in (621, 622):
        res = _doctor(_stub_wled(count=n))
        bad = [r for r in res if r[0] != "ok"]
        eq(bad, [], "a correct %d-LED controller" % n)
    for n, cap, per, level in ((623, want, 19, "warn"),
                               (622, 1621, 19, "FAIL"),
                               (622, 4274, 19, "FAIL"),
                               (622, 0, 19, "FAIL"),
                               (622, want, 0, "FAIL"),
                               (622, want, 255, "FAIL"),
                               (622, want, 12, "FAIL"),
                               (622, 260, 55, "warn")):
        res = _doctor(_stub_wled(count=n, maxpwr=cap, ledma=per))
        levels = [r[0] for r in res]
        ok(level in levels, "%d LEDs, %d mA at %d: wanted a %s, got %s"
           % (n, cap, per, level, res))
        for lvl, area, msg, fix in res:
            if not fix:
                continue
            ok("--allow" not in fix and "--max-ma" not in fix
               and "--ma-per-led" not in fix,
               "the doctor wrote its own limiter: %s" % fix)
            ok("mau5offline.py config" in fix or "collapse" in fix,
               "a fix that is not the profile's own: %s" % fix)
    # tighter than the profile is safe, so it is not "fixed" upwards
    res = _doctor(_stub_wled(maxpwr=600))
    ok(all(not r[3] for r in res if "limiter" in r[2]),
       "offered to raise a limiter that was already tighter: %s" % res)


def t_doctor_sees_a_missing_profile():
    """A lost power.json is a failure, not "ok budget 300 mA"."""
    import mau5doctor, mau5power
    keep = mau5power.DEFAULT
    mau5power.DEFAULT = os.path.join(HERE, "data", "cal", "no-such-power.json")
    del mau5doctor.RESULTS[:]
    try:
        mau5doctor._power()
    finally:
        mau5power.DEFAULT = keep
    res = list(mau5doctor.RESULTS)
    del mau5doctor.RESULTS[:]
    ok(res and res[0][0] == "FAIL" and res[0][1] == "power",
       "a missing profile passed: %s" % res)
    # and the real one still passes
    mau5doctor._power()
    res = list(mau5doctor.RESULTS)
    del mau5doctor.RESULTS[:]
    ok(not any(r[0] == "FAIL" for r in res), "the real profile failed: %s" % res)


def t_doctor_colour_uses_the_map_count():
    import mau5doctor
    del mau5doctor.RESULTS[:]
    mau5doctor._colour()
    res = list(mau5doctor.RESULTS)
    del mau5doctor.RESULTS[:]
    ok(res and all(r[0] == "ok" for r in res), "colour check: %s" % res)


# ----------------------------------------------------------------------
# config, check, standby
# ----------------------------------------------------------------------
def t_ap_password_is_refused_before_sending():
    """A 1-7 character password leaves the ESP32 with no access point.

    WLED stores it and WiFi.softAP() then refuses it, so `config`
    printed "applied." over a helmet that would never broadcast again.
    """
    import mau5offline
    for psk in ("mau5", "x" * 7, "x" * 64, "cafécafé"):
        ok(mau5offline.ap_problem(psk=psk), "accepted %r" % psk)
    for psk in ("x" * 8, "x" * 63, "correct horse!"):
        eq(mau5offline.ap_problem(psk=psk), None, "refused %r" % psk)
    ok(mau5offline.ap_problem(ssid="x" * 33), "accepted a 33-byte SSID")
    ok(mau5offline.ap_problem(ssid=""), "accepted an empty SSID")
    eq(mau5offline.ap_problem(ssid="mau5head-AP"), None, "refused mau5head-AP")

    try:
        mau5offline.wanted_cfg(_power(), ap_psk="short")
        ok(False, "wanted_cfg took a 5-character password")
    except ValueError:
        pass

    keep = mau5offline._find
    def never(host):
        raise AssertionError("config went looking for the controller first")
    mau5offline._find = never
    try:
        try:
            mau5offline.config("192.0.2.1", apply=True, ap_psk="mau5")
            ok(False, "config accepted a 4-character password")
        except SystemExit as e:
            ok("8 to 63" in str(e), "unhelpful refusal: %s" % e)
    finally:
        mau5offline._find = keep


@contextlib.contextmanager
def _offline_patched(w, page=None):
    """mau5offline talking to a stub, with no sleeps and no sockets."""
    import mau5offline
    import urllib.request
    keep = (mau5offline._find, mau5offline.time, urllib.request.urlopen)

    class R(io.BytesIO):
        headers = {}
        status = 200

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

    def urlopen(url, timeout=None):
        u = url if isinstance(url, str) else url.full_url
        if page is not None and u.endswith("/" + mau5offline.PAGE):
            return R(page)
        raise AssertionError("fetched %s" % u)

    mau5offline._find = lambda host: w
    mau5offline.time = types.SimpleNamespace(
        sleep=lambda s: None, strftime=time.strftime, time=time.time)
    urllib.request.urlopen = urlopen
    try:
        yield
    finally:
        mau5offline._find, mau5offline.time, urllib.request.urlopen = keep


def t_check_survives_a_new_day_and_622():
    """The page built yesterday is still current; 622 LEDs is correct.

    check compared the deployed page byte for byte with a fresh build,
    and the build carries the date, so every morning it said the page
    was out of date.  It also wanted the controller to report exactly
    the map's 621, which this one deliberately does not.
    """
    import mau5offline
    plain, raw, gz = mau5offline.build(verbose=False)
    today = mau5offline._built_on(raw)
    ok(today != "?", "no build stamp found in the page")
    yesterday = raw.replace(('"built":"%s"' % today).encode(),
                            b'"built":"1999-12-31"')
    ok(yesterday != raw, "could not make yesterday's page")
    eq(mau5offline._unstamped(yesterday), mau5offline._unstamped(raw),
       "a page differing only by its date")
    changed = yesterday.replace(b"MAU5_DATA", b"MAU5_DATB", 1)
    ok(mau5offline._unstamped(changed) != mau5offline._unstamped(raw),
       "a real change hidden by the stamp comparison")

    w = _stub_wled(count=622)
    buf = io.StringIO()
    with _offline_patched(w, page=yesterday), contextlib.redirect_stdout(buf):
        rc = mau5offline.check("stub")
    out = buf.getvalue()
    eq(rc, 0, "check on a ready controller:\n" + out)
    ok("'mau5head-AP'" in out, "check did not say which network to join:\n" + out)
    ok("1999-12-31" in out, "check did not show the deployed build date")

    # an old, burst-level limiter is not ready, and says why
    w = _stub_wled(count=622, maxpwr=1621)
    buf = io.StringIO()
    with _offline_patched(w, page=raw), contextlib.redirect_stdout(buf):
        rc = mau5offline.check("stub")
    out = buf.getvalue()
    eq(rc, 1, "check passed a 1621 mA limiter:\n" + out)
    ok("above what the helmet can sustain" in out, out)

    for n, want in ((621, True), (622, True), (623, False), (600, False)):
        eq(mau5offline.count_agrees(n, 621), want, "count %d" % n)


def t_standby_preset_keeps_its_brightness():
    """The standby preset is saved with ib and sb, as one plain segment.

    Without ib WLED saves no brightness, and the hand-back -- {ps: 1}
    alone -- ran at the phone's 255 instead of 96.
    """
    import mau5offline
    w = _stub_wled(count=622, segs=(0, 1, 2, 9))
    buf = io.StringIO()
    with _offline_patched(w), contextlib.redirect_stdout(buf):
        mau5offline.standby("stub", fx="pacifica", bri=96, boot=True, apply=True)
    states = [o for p, o in w.posts if p == "/json/state"]
    save = [o for o in states if "psave" in o]
    eq(len(save), 1, "one preset save")
    ok(save[0].get("ib") is True and save[0].get("sb") is True,
       "saved without brightness or bounds: %s" % save[0])
    setup = [o for o in states if "seg" in o][0]
    eq(setup["bri"], 96, "standby brightness")
    seg0 = [s for s in setup["seg"] if s["id"] == 0][0]
    eq((seg0["start"], seg0["stop"], seg0["frz"]), (0, 622, False), "segment 0")
    gone = sorted(s["id"] for s in setup["seg"] if s.get("stop") == 0)
    eq(gone, [1, 2, 9], "leftover segments must go, frozen ones above all")
    ok(states.index(setup) < states.index(save[0]), "saved before it was set up")
    boot = [o for p, o in w.posts if p == "/json/cfg"]
    eq(boot[0]["def"]["bri"], 96, "boot brightness")


# ----------------------------------------------------------------------
# mau5ctl
# ----------------------------------------------------------------------
class _Pix:
    """Records what would go out over DDP, through the real guard."""

    def __init__(self, n):
        import mau5power
        self.count = n
        self.guard = mau5power.load(count=n)
        self.sent = []
        self.last_power = None
        self.last_sent = np.zeros((n, 3), np.uint8)

    def send(self, buf, gain=1.0):
        a = np.asarray(np.clip(buf, 0, 255), np.uint8)
        a, self.last_power = self.guard.apply(a, gain=gain)
        self.last_sent = a
        self.sent.append((time.monotonic(), int(a.max())))


class _Boom:
    def render(self, h, t, music=None):
        return 1.0 / 0.0 * np.ones((h.n, 3))


class _Exit:
    def render(self, h, t, music=None):
        raise SystemExit("no preset 'sparkles'")


def t_ctl_render_error_keeps_the_stream():
    """A preset that throws must not hand the helmet to WLED at 255.

    Sending nothing let WLED leave realtime 2.5 s later and run its own
    effect, unguarded, at the brightness mau5ctl had set.  It has to
    keep streaming -- black -- and a preset that would throw has to be
    refused before it replaces the one playing.
    """
    import mau5ctl, mau5engine as E
    h = E.Helmet()
    pix = _Pix(h.n)
    ctl = mau5ctl.Controller(pix, fps=50, wled=None)
    try:
        ctl.set_preset("rainbow")
        # A slider at its end used to be refused here because it threw;
        # the engine now holds such values at the slider's floor, so they
        # are taken and render finite -- which is what matters.
        for name, kw in (("rainbow", {"period": 0.0}), ("breathe", {"period": 0.0}),
                         ("eq", {"bands": 0}), ("confetti", {"fade": 0.0})):
            ctl.set_preset(name, **kw)
            f = np.asarray(ctl.preset.render(h, 1.234), float)
            ok(np.isfinite(f).all(), "%s %s renders non-finite" % (name, kw))
        time.sleep(0.2)
        # Now one that fails anyway, mid-run.
        with ctl.lock:
            ctl.preset, ctl.preset_name, ctl.mode = _Boom(), "boom", "preset"
        time.sleep(0.1)
        n0 = len(pix.sent)
        time.sleep(0.5)
        during = pix.sent[n0:]
        ok(ctl.error and "ZeroDivisionError" in ctl.error,
           "no render error reported: %r" % ctl.error)
        ok(len(during) >= 10, "the stream stopped: %d frames in 0.5 s"
           % len(during))
        ok(all(m == 0 for _, m in during), "the failing frames were not black")
        eq(int(ctl.last_frame.max()), 0, "the preview should show black")
        # SystemExit, which make() raises for an unknown preset name,
        # must not end the frame loop either
        with ctl.lock:
            ctl.preset = _Exit()
        time.sleep(0.15)
        n1 = len(pix.sent)
        time.sleep(0.3)
        ok(len(pix.sent) - n1 >= 6, "SystemExit stopped the frame loop")
        ok(ctl.error and "SystemExit" in ctl.error, "SystemExit not reported")
        # and it recovers, climbing back in
        ctl.set_preset("rainbow")
        time.sleep(0.3)
        ok(ctl.error is None, "the error outlived the preset: %r" % ctl.error)
        ok(pix.sent[-1][1] > 0, "rendering did not resume")
    finally:
        ctl.stop = True
        time.sleep(0.05)


def t_ctl_clock_eases_instead_of_jumping():
    """The show clock follows the phone without stepping.

    Each report is late by its own network delay, so jumping to every
    one stepped the clock back and forth every 400 ms, and a report
    overtaken by a later one set it back a whole report.
    """
    import mau5ctl
    ctl = mau5ctl.Controller(None, fps=10, wled=None)
    try:
        ctl.mode = "off"
        mono = time.monotonic()
        ctl.clock(10.0, True, seq=1, sid="a", pt=(mono - 100.0) * 1000.0)
        ok(abs(ctl.now() - 10.0) < 0.01, "play did not snap: %.3f" % ctl.now())

        # a stale report (seq not newer) changes nothing
        before = ctl.now()
        ctl.clock(3.0, True, seq=1, sid="a", pt=(time.monotonic() - 100.0) * 1e3)
        ok(abs(ctl.now() - before) < 0.01, "a stale report moved the clock")

        # 40 ms ahead, arriving on time: eased in, not stepped
        time.sleep(0.05)
        mono = time.monotonic()
        cur = ctl.now()
        ctl.clock(cur + 0.04, True, seq=2, sid="a", pt=(mono - 100.0) * 1e3)
        step = ctl.now() - cur
        ok(step < 0.01, "a 40 ms report stepped the clock by %.0f ms" % (step * 1e3))
        time.sleep(ctl.EASE_S + 0.05)
        lead = ctl.now() - (cur + (time.monotonic() - mono))
        ok(0.015 < lead < 0.025, "eased %.1f ms of a 40 ms error, wanted half"
           % (lead * 1e3))

        # the same position arriving 100 ms late by the phone's clock is
        # not 100 ms behind: the delay is measured and added back
        mono = time.monotonic()
        cur = ctl.now()
        ctl.clock(cur - 0.1, True, seq=3, sid="a", pt=(mono - 100.1) * 1e3)
        time.sleep(ctl.EASE_S + 0.05)
        drift = ctl.now() - (cur + (time.monotonic() - mono))
        ok(abs(drift) < 0.01, "a late report pulled the clock %.0f ms" % (drift * 1e3))

        # a seek snaps, and a new page starts its own sequence
        ctl.clock(120.0, True, seq=1, sid="b", pt=time.monotonic() * 1e3)
        ok(abs(ctl.now() - 120.0) < 0.01, "a new page's seek was ignored")
        ctl.clock(121.0, False, seq=2, sid="b")
        t1 = ctl.now()
        time.sleep(0.05)
        eq(ctl.now(), t1, "a paused clock moved")
        ok(abs(t1 - 121.0) < 1e-9, "pause did not land on the reported position")

        # an old page with none of the new fields still works
        ctl.clock(50.0, True)
        ok(abs(ctl.now() - 50.0) < 0.01, "a plain report did not snap")
    finally:
        ctl.stop = True


def t_ctl_posts_must_be_json():
    """A text/plain POST is refused; JSON is not.

    mau5ctl listens on every interface with no login, and a text/plain
    POST is what any web page can send cross-site without the browser
    asking first.  That was enough to plant a favourite whose label ran
    script in the control page.
    """
    import mau5ctl
    import urllib.request, urllib.error
    from http.server import ThreadingHTTPServer

    calls = []

    class Ctl:
        def off(self):
            calls.append("off")

        def state(self):
            return {"mode": "off"}

    srv = ThreadingHTTPServer(("127.0.0.1", 0), mau5ctl.make_handler(Ctl()))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    base = "http://127.0.0.1:%d" % srv.server_address[1]
    try:
        def post(ctype, body=b"{}"):
            req = urllib.request.Request(base + "/api/off", data=body,
                                         method="POST")
            if ctype:
                req.add_header("Content-Type", ctype)
            try:
                with urllib.request.urlopen(req, timeout=5) as r:
                    return r.status
            except urllib.error.HTTPError as e:
                return e.code
        eq(post("text/plain"), 415, "text/plain")
        eq(post("application/x-www-form-urlencoded"), 415, "a form post")
        eq(calls, [], "a refused post still acted")
        eq(post("application/json"), 200, "application/json")
        eq(post("application/json; charset=utf-8"), 200, "json with a charset")
        eq(post("application/json", b"{not json"), 400, "malformed json")
        eq(calls, ["off", "off"], "json posts")
    finally:
        srv.shutdown()
        srv.server_close()


def t_control_page_escapes_and_reports_order():
    """What the server says is escaped before it reaches innerHTML."""
    src = open(os.path.join(HERE, "remote", "control.html")).read()
    for raw in ("${f.label}", 'data-p="${n}"', 'data-s="${n}"', "${d.name}"):
        ok(raw not in src, "unescaped in control.html: %s" % raw)
    ok("const esc" in src and "esc(f.label)" in src, "no escaping helper in use")
    ok("seq:" in src and "sid:" in src and "pt: performance.now()" in src,
       "clock reports carry no order or timing")
    ok("if(!r.ok)" in src, "a refused post would still replace the state")


def t_simulator_reads_kind():
    """The web simulator builds a control for every kind spec() emits."""
    import mau5engine as E
    src = open(os.path.join(HERE, "remote", "web", "simulator.js")).read()
    ok("s.type" not in src, "simulator.js still reads s.type")
    kinds = {d["kind"] for cls in E.REGISTRY.values() for d in cls.spec()}
    for k in kinds:
        ok("s.kind === '%s'" % k in src, "simulator.js ignores kind %r" % k)


# ----------------------------------------------------------------------
# Spotify
# ----------------------------------------------------------------------
def t_spotify_never_shares_a_rotating_token():
    """status keeps the rotated token, and the phone gets its own.

    Spotify rotates a PKCE refresh token on use.  One token in two
    places meant status on the laptop killed the phone's copy, and the
    phone's refresh left the laptop handing out dead ones.
    """
    import mau5spotify as S
    import urllib.request as UR
    import tempfile
    tmpdir = tempfile.mkdtemp(prefix="mau5spotify-test-")
    tmp = os.path.join(tmpdir, "spotify.json")
    keep = (S.STORE, S._post_form, S.urllib, S.login)
    spent = []

    def post_form(url, fields):
        spent.append(fields.get("refresh_token"))
        return {"access_token": "A", "refresh_token": "R%d" % len(spent)}

    class Resp(io.BytesIO):
        status = 204

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

    S.STORE = tmp
    S._post_form = post_form
    S.urllib = types.SimpleNamespace(
        parse=S.urllib.parse,
        request=types.SimpleNamespace(Request=UR.Request,
                                      urlopen=lambda req, timeout=None: Resp()))
    buf = io.StringIO()
    try:
        # a store from before: the token may be on a phone, so not spent
        S.write({"client_id": "cid", "refresh_token": "OLD", "scope": "x"})
        with contextlib.redirect_stdout(buf):
            eq(S.status(), 0, "status on an old store")
        eq(spent, [], "status spent a token that may be on a phone")
        # asked to: spent, and the rotated one kept
        with contextlib.redirect_stdout(buf):
            eq(S.status(spend=True), 0, "status --refresh")
        eq(spent, ["OLD"], "spent")
        d = S.read()
        eq((d["refresh_token"], d.get("laptop_only")), ("R1", True),
           "the rotated token was thrown away")
        # the laptop's own token: spent freely, and kept each time
        with contextlib.redirect_stdout(buf):
            S.status()
        eq(S.read()["refresh_token"], "R2", "second rotation kept")

        # handoff signs in separately and never gives out the stored one
        signed = []

        def login(cid, open_browser=True, store=True):
            signed.append((cid, store))
            return {"access_token": "A", "refresh_token": "PHONE"}
        S.login = login
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            eq(S.main(["handoff", "--no-browser"]), 0, "handoff")
        eq(signed, [("cid", False)], "handoff must sign in, and not store it")
        ok("cid.PHONE" in out.getvalue(), "the phone did not get its own token")
        ok("R2" not in out.getvalue(), "handoff gave out the laptop's token")
        eq(S.read()["refresh_token"], "R2", "handoff changed the laptop's token")
    finally:
        S.STORE, S._post_form, S.urllib, S.login = keep
        for p in (tmp, tmp + ".tmp"):
            if os.path.exists(p):
                os.remove(p)
        os.rmdir(tmpdir)


GROUP = [
    t_limiter_covers_the_sustained_case,
    t_doctor_takes_622_and_never_raises_the_limiter,
    t_doctor_sees_a_missing_profile,
    t_doctor_colour_uses_the_map_count,
    t_ap_password_is_refused_before_sending,
    t_check_survives_a_new_day_and_622,
    t_standby_preset_keeps_its_brightness,
    t_ctl_render_error_keeps_the_stream,
    t_ctl_clock_eases_instead_of_jumping,
    t_ctl_posts_must_be_json,
    t_control_page_escapes_and_reports_order,
    t_simulator_reads_kind,
    t_spotify_never_shares_a_rotating_token,
]
