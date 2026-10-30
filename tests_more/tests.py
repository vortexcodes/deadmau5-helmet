"""The checking tools themselves: mau5verify's lit patterns, the film's
reference photo, and what the suite counts as a pass.

Nothing here touches the helmet or the network.  mau5verify's checks
are built and read, never streamed; lan_ip and node are stood in for.
"""

import contextlib
import io
import json
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from test_mau5 import ok, eq, HERE  # noqa: E402


def _checks():
    import mau5verify
    session = json.load(open(os.path.join(HERE, "data", "cal", "walk_session.json")))
    return {c["id"]: c for c in mau5verify.build_checks(session)}


def t_verify_spans_sit_in_their_regions():
    """Every ear span lights the region it is labelled with, and no other.

    The colour-order check's 'first rim' was 470-480, on ear1's tubes
    since before the cut, so the rim strips.json says is wired
    differently was never lit by the check meant to find it; and the
    ear checks ran onto the far ear and past the end of the chain.
    """
    import mau5map
    rows = mau5map.load()
    region = {r["index"]: r["region"] for r in rows}
    C = _checks()
    for c in C.values():
        for lo, hi, _, lab in c["spans"]:
            ok(0 <= lo <= hi <= mau5map.TOTAL_N - 1,
               "%s: %d-%d is off the %d-LED chain" % (c["id"], lo, hi, mau5map.TOTAL_N))

    lit = set()
    for lo, hi, _, lab in C["colour-order"]["spans"]:
        want = lab.replace(" ", "_")
        got = {region[i] for i in range(lo, hi + 1)}
        eq(got, {want}, "colour-order's %r span %d-%d" % (lab, lo, hi))
        lit |= set(range(lo, hi + 1))
    eq({lab.replace(" ", "_") for _, _, _, lab in C["colour-order"]["spans"]},
       set(region.values()), "colour-order should light every region")
    strips = json.load(open(os.path.join(HERE, "data", "cal", "strips.json")))["strips"]
    for s in strips:
        span = set(range(s["start"], s["start"] + s["count"]))
        ok(span & lit, "colour-order lights nothing of %s (%d-%d)"
           % (s["name"], s["start"], s["start"] + s["count"] - 1))

    for cid, names in (("ears-a", ("ear1_tubes", "ear1_rim")),
                       ("ears-b", ("ear2_rim", "ear2_tubes"))):
        for (lo, hi, _, _), name in zip(C[cid]["spans"], names):
            idx = [r["index"] for r in rows if r["region"] == name]
            eq((lo, hi), (min(idx), max(idx)), "%s's %s span" % (cid, name))


def t_verify_stops_at_the_map():
    """The walk still ends at 622, so the map's end is the one checked."""
    import mau5map
    real = mau5map.TOTAL_N
    mau5map.TOTAL_N = 600            # the ear checks run to 620
    try:
        _checks()
        ok(False, "a span past the end of the map was let through")
    except SystemExit as e:
        ok("runs past the chain" in str(e), "wrong refusal: %s" % e)
    finally:
        mau5map.TOTAL_N = real


def t_film_photo_is_not_camera_scratch():
    """The ears scene's photo is its own file, and missing it is not fatal.

    It read eye.jpg, mau5eye's live output, which by the next camera
    session is a dark frame from another position -- the CAD outline
    then misses the ears the scene says it lands on.
    """
    import mau5film
    rel = os.path.relpath(mau5film.HIGH_PHOTO, HERE)
    scratch = [l.strip() for l in open(os.path.join(HERE, ".gitignore"))
               if l.strip() and not l.startswith("#")]
    ok(rel not in scratch, "%s is a file .gitignore calls scratch" % rel)
    ok(os.path.basename(rel) != "eye.jpg", "the film reads mau5eye's live frame")

    real = mau5film.HIGH_PHOTO
    mau5film.HIGH_PHOTO = os.path.join(HERE, "data", "cal", "no-such-photo.jpg")
    try:
        with contextlib.redirect_stdout(io.StringIO()) as said:
            frames = list(mau5film.s_ears(mau5film.Model(), 4))
    finally:
        mau5film.HIGH_PHOTO = real
    eq(len(frames), 4, "frames without the photo")
    ok("not drawn on a photo" in said.getvalue(), "the missing photo went unmentioned")


def t_missing_node_is_skipped_not_passed():
    """Without node the JS cross-checks skip, and the summary counts them."""
    import test_mau5 as T
    real = shutil.which
    shutil.which = lambda name, *a, **k: None if name == "node" else real(name, *a, **k)
    try:
        for fn in (T.t_offline_engine_matches_python, T.t_offline_guard_matches_python,
                   T.t_offline_encoder_roundtrip, T.t_offline_shows_match_python,
                   T.t_offline_drive_matches_the_analysis):
            try:
                fn()
            except T.Skip:
                continue
            ok(False, "%s passed with no node to run it" % fn.__name__)
    finally:
        shutil.which = real


def t_lan_ip_with_no_network():
    """No LAN up is a skip; a LAN up and loopback chosen is still a failure."""
    import mau5wled
    import test_mau5 as T
    real = mau5wled.local_nets, mau5wled.lan_ip
    try:
        mau5wled.local_nets, mau5wled.lan_ip = (lambda: []), (lambda: "127.0.0.1")
        try:
            T.t_lan_ip()
            ok(False, "no network at all should skip, not pass")
        except T.Skip:
            pass
        mau5wled.local_nets = lambda: [{"iface": "en0", "ip": "192.168.1.5", "bits": 24}]
        failed = False
        try:
            T.t_lan_ip()
        except AssertionError:
            failed = True
        ok(failed, "loopback with a LAN up must still fail")
    finally:
        mau5wled.local_nets, mau5wled.lan_ip = real


GROUP = [t_verify_spans_sit_in_their_regions,
         t_verify_stops_at_the_map,
         t_film_photo_is_not_camera_scratch,
         t_missing_node_is_skipped_not_passed,
         t_lan_ip_with_no_network]
