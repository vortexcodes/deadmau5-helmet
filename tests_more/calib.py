"""Calibration tools: the chain each pose was measured on, files that must
not be overwritten, the camera's own lag, and corrections that stay where
they were aimed.  All offline -- nothing here talks to the helmet."""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from test_mau5 import ok, eq, note, HERE

import copy
import csv
import hashlib
import io
import json
import shutil
import tempfile
import threading
import time

import numpy as np


def _tmpdir():
    return tempfile.mkdtemp(prefix="mau5calib-")


def _write_pose(path, rows, chain=None):
    """A pose file as mau5locate writes it, stamped or not."""
    fields = ["index", "cx", "cy", "peak", "px_count", "w", "h", "level"]
    if chain is not None:
        fields.append("chain")
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for i in sorted(rows):
            r = dict(rows[i], index=i)
            if chain is not None:
                r["chain"] = chain
            w.writerow(r)


def _raw(path):
    return {int(r["index"]): r for r in csv.DictReader(open(path))}


def _sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def t_cut_follows_each_pose_file():
    """CUT re-keys a pose measured before the cut, and only that one.

    The same physical LEDs measured after the cut are already keyed by
    the chain as it is; re-keying them again put every ear LED one
    place low.  So: a post-cut copy of the front pose must load to the
    very same centroids as the pre-cut original.
    """
    import mau5slots as S
    for k, p in S.POSES.items():
        eq(S.pose_chain(p), S.BEFORE_CUT, "%s pose was measured before the cut" % k)
        m, c = S.load_pose(p)
        eq(m, S.after_cut(S.load_centroids(p)), "%s pose re-keyed as before" % k)
    d = _tmpdir()
    try:
        old = _raw(S.POSES["front"])
        # the same LEDs, keyed by the chain as it is now: 492 gone,
        # everything after one lower, 621 lighting nothing
        new = {}
        for i, r in old.items():
            if i in S.CUT:
                continue
            new[i - sum(1 for c in S.CUT if c < i)] = r
        after = os.path.join(d, "after.csv")
        _write_pose(after, new, chain=S.TOTAL_N)
        eq(S.pose_chain(after), S.TOTAL_N, "a stamped post-cut file")
        m_new, _ = S.load_pose(after)
        m_old, _ = S.load_pose(S.POSES["front"])
        eq(m_new, m_old, "the same LEDs measured after the cut must not be re-keyed")
        ok(m_new[492] == (float(old[493]["cx"]), float(old[493]["cy"])),
           "new 492 is old 493")

        # unstamped, nothing at 621, centroids past the cut: either chain
        amb = os.path.join(d, "ambiguous.csv")
        _write_pose(amb, {i: r for i, r in old.items() if i < 600})
        try:
            S.pose_chain(amb)
            raise AssertionError("guessed the chain of a file that does not say")
        except SystemExit as e:
            ok("chain" in str(e), "the refusal should say how to fix it")
        # unstamped and wholly before the cut: reads the same either way
        shell = os.path.join(d, "shell.csv")
        _write_pose(shell, {i: r for i, r in old.items() if i < 398})
        eq(S.pose_chain(shell), S.TOTAL_N, "a shell-only file needs no re-keying")
        # rows from two chains in one file
        mixed = os.path.join(d, "mixed.csv")
        _write_pose(mixed, new, chain=S.TOTAL_N)
        rows = list(csv.DictReader(open(mixed)))
        rows[-1]["chain"] = str(S.BEFORE_CUT)
        with open(mixed, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0]))
            w.writeheader(); w.writerows(rows)
        try:
            S.pose_chain(mixed)
            raise AssertionError("accepted a file that mixes two chains")
        except SystemExit:
            pass
    finally:
        shutil.rmtree(d, ignore_errors=True)


def t_locate_stamps_and_will_not_overwrite():
    """mau5locate stamps its rows, refuses to replace a file it was not
    told to, and will not resume a file from before the cut -- and all of
    that before anything is lit."""
    import mau5locate as L, mau5slots as S, mau5wled
    d = _tmpdir()
    real_find = mau5wled.find_one

    def no_helmet(*a, **k):
        raise AssertionError("tried to reach the helmet")
    try:
        mau5wled.find_one = no_helmet
        pre = os.path.join(d, "pre.csv")
        shutil.copy(S.POSES["front"], pre)
        before = _sha(pre)
        for argv in (["--out", pre], ["--out", pre, "--from", "398", "--to", "620"]):
            try:
                L.main(argv)
                raise AssertionError("ran over a file of measurements: %s" % argv)
            except SystemExit as e:
                ok("--overwrite" in str(e), "the refusal should name the way out")
        try:
            L.main(["--out", pre, "--resume"])
            raise AssertionError("resumed a file measured on the old chain")
        except SystemExit as e:
            ok("before the cut" in str(e), "should say why: %s" % e)
        eq(_sha(pre), before, "a refused run must leave the file as it was")
        eq(L.starting_rows(pre, False, True), {}, "--overwrite starts afresh")

        # a file of this chain resumes, and comes back stamped
        rows = {i: dict(r, chain=S.TOTAL_N) for i, r in L.load(pre).items() if i < 300}
        post = os.path.join(d, "post.csv")
        L.save(rows, post)
        back = L.load(post)
        eq(back[5]["chain"], S.TOTAL_N, "the chain survives a save and a load")
        eq(S.pose_chain(post), S.TOTAL_N, "and mau5slots reads it")
        got = L.starting_rows(post, True, False)
        eq(sorted(got), sorted(rows), "resume keeps every row")
        eq(L.load(pre)[5]["chain"], None, "a file from before the column reads as None")
        # an unstamped shell-only file is the same on both chains
        legacy = os.path.join(d, "legacy.csv")
        _write_pose(legacy, {i: r for i, r in _raw(pre).items() if i < 300})
        got = L.starting_rows(legacy, True, False)
        ok(all(r["chain"] == S.TOTAL_N for r in got.values()),
           "a resumed file is stamped with the chain it continues on")
    finally:
        mau5wled.find_one = real_find
        shutil.rmtree(d, ignore_errors=True)


class _Camera:
    """A fake mau5eye: the real server, fed by a camera that shows the
    helmet `lag` seconds late and pushes every `every` seconds."""

    def __init__(self, lag, every):
        import mau5eye
        from http.server import ThreadingHTTPServer
        from PIL import Image
        self.lag, self.every = lag, every
        self.dir = _tmpdir()
        self.eye = mau5eye.Eye(os.path.join(self.dir, "eye.jpg"))
        self.srv = ThreadingHTTPServer(("127.0.0.1", 0), mau5eye.make_handler(self.eye))
        self.port = self.srv.server_address[1]
        self.hist = [(0.0, False)]

        def jpeg(lit):
            a = np.zeros((48, 64), np.uint8)
            if lit:
                a[20:28, 28:36] = 200
            b = io.BytesIO()
            Image.fromarray(a).save(b, "JPEG", quality=90)
            return b.getvalue()
        self.frames = {False: jpeg(False), True: jpeg(True)}
        self.stop = threading.Event()
        threading.Thread(target=self.srv.serve_forever, daemon=True).start()
        threading.Thread(target=self._run, daemon=True).start()

    def set(self, lit):
        self.hist.append((time.time(), lit))

    def _run(self):
        while not self.stop.is_set():
            seen = time.time() - self.lag
            state = [s for t, s in self.hist if t <= seen][-1]
            self.eye.put(self.frames[state])
            time.sleep(self.every)

    def close(self):
        self.stop.set()
        self.srv.shutdown()
        shutil.rmtree(self.dir, ignore_errors=True)


def t_eye_waits_out_the_lag():
    """shot(lag=) refuses frames pushed before after+lag, and
    measure_lag finds a camera's lag to within one push interval.

    The phone camera shows the world 1.1-1.5 s late, so a frame pushed
    0.4 s after a change is usually the LED before; mau5locate's rows
    came back one LED late with nothing to say so.
    """
    import mau5eye
    lag, every = 0.6, 0.1
    cam = _Camera(lag, every)
    try:
        time.sleep(0.3)
        # a live camera: fine with no lag, refused when the lag is not yet over
        ok(mau5eye.shot(os.devnull, port=cam.port, wait=3.0, after=time.time()),
           "rejected a fresh frame")
        try:
            mau5eye.shot(os.devnull, port=cam.port, wait=0.8,
                         after=time.time(), lag=5.0)
            raise AssertionError("took a frame pushed before the lag was over")
        except SystemExit:
            pass
        use, seen = mau5eye.measure_lag(lambda: cam.set(True), lambda: cam.set(False),
                                        port=cam.port, trials=2, wait=4.0,
                                        first_guess=1.0)
        eq(len(seen), 4, "timed on and off, twice each")
        ok(min(seen) >= lag - 0.05, "measured %.2f s, faster than the camera's "
                                    "own %.2f s" % (min(seen), lag))
        ok(max(seen) <= lag + 2 * every + 0.25, "measured %.2f s for a %.2f s "
                                                 "camera" % (max(seen), lag))
        ok(abs(use - (max(seen) + mau5eye.LAG_MARGIN)) < 1e-9,
           "the lag to wait is the worst seen plus the margin")
        # and with it, a frame taken after a change really shows the change
        t = time.time(); cam.set(True)
        out = os.path.join(cam.dir, "after.jpg")
        mau5eye.shot(out, port=cam.port, wait=5.0, after=t, lag=use)
        from PIL import Image
        ok(np.asarray(Image.open(out).convert("L")).max() > 100,
           "the frame shot() returned still showed the helmet before the change")
        # a pattern that never shows is an error, not a lag of zero
        try:
            mau5eye.measure_lag(lambda: None, lambda: None, port=cam.port,
                                trials=1, wait=0.8, first_guess=0.2)
            raise AssertionError("measured a lag for a pattern it never saw")
        except mau5eye.LagError:
            pass
    finally:
        cam.close()


def t_eye_uploads_cannot_cross():
    """Uploads at once must not share a temporary file, and the frame on
    disk must be the one in memory.  With one shared ".tmp", the second
    os.replace found nothing to move and that upload failed."""
    import mau5eye
    d = _tmpdir()
    try:
        eye = mau5eye.Eye(os.path.join(d, "eye.jpg"))
        errors = []

        def push(k):
            try:
                for j in range(40):
                    eye.put(b"frame %d %d " % (k, j) + b"x" * 20000)
            except Exception as e:
                errors.append(e)
        ts = [threading.Thread(target=push, args=(k,)) for k in range(6)]
        for t in ts:
            t.start()
        for t in ts:
            t.join()
        eq(errors, [], "an upload failed while another was being written")
        frame, at, n = eye.get()
        eq(n, 240, "frames counted")
        eq(open(os.path.join(d, "eye.jpg"), "rb").read(), frame,
           "the file on disk is not the newest frame")
        eq(sorted(os.listdir(d)), ["eye.jpg"], "temporary files left behind")
        ok("busy" in mau5eye.PAGE and "AbortController" in mau5eye.PAGE,
           "the page should send one frame at a time")
    finally:
        shutil.rmtree(d, ignore_errors=True)


def t_review_waits_out_the_lag():
    """mau5review's frames are taken lag after their change, timed from
    before the change, not from after it."""
    import mau5eye, mau5review
    from PIL import Image
    d = _tmpdir()
    calls, events = [], []
    real = mau5eye.shot

    def fake_shot(path, **kw):
        calls.append(kw)
        Image.fromarray(np.zeros((8, 8, 3), np.uint8)).save(path)
        return path

    class Stream:
        def show(self, buf):
            events.append(("show", time.time()))

        def dark(self):
            events.append(("dark", time.time()))
    try:
        mau5eye.shot = fake_shot
        mau5review.lit_frame(Stream(), np.zeros((3, 3), np.uint8), 1, d, lag=1.8)
        eq(calls[-1]["lag"], 1.8, "lit frame lag")
        ok(calls[-1]["after"] <= events[-1][1], "timed from after the change")
        mau5review.dark_frame(Stream(), 1, d, lag=1.8)
        eq([c["lag"] for c in calls[-2:]], [1.8, 1.8], "dark frame lag")
        ok(all(c["after"] <= events[-1][1] for c in calls[-2:]),
           "dark reference timed from after the blank")
    finally:
        mau5eye.shot = real
        shutil.rmtree(d, ignore_errors=True)


def t_lines_correct_only_what_is_lit():
    """An across/up/depth line is LEDs from many strips; a correction
    covers every index from its lowest to its highest.  So it is refused
    there, and allowed on a run, which is unbroken."""
    import mau5engine as E, mau5lines, mau5map
    L = object.__new__(mau5lines.Lines)
    L.rows = mau5map.load()
    L.h = E.Helmet()
    L.n, L.steps, L.width = len(L.rows), 28, 26.0
    L.runs = mau5lines.runs_of(L.rows)
    L.groups = sorted(set(r["group"] for r in L.rows))
    L.adjust = {"spans": []}
    written = []
    L._write = lambda path, doc: written.append(path)
    L.reload = lambda: None
    L.axis, L.i = "x", 5
    lo, hi = L.span()
    ok(not L.whole(), "across-line 5 should be scattered (%d-%d)" % (lo, hi))
    try:
        L.add_adjust({"op": "reverse", "lo": lo, "hi": hi})
        raise AssertionError("accepted a correction over %d-%d for %d lit LEDs"
                             % (lo, hi, int(L.members().sum())))
    except ValueError:
        pass
    eq(written, [], "a refused correction must not be written")
    L.axis, L.i = "run", 3
    lo, hi = L.span()
    ok(L.whole(), "a run is one piece")
    try:
        L.add_adjust({"op": "move", "lo": lo, "hi": hi + 1, "dx": 1})
        raise AssertionError("accepted a range that is not the lit line")
    except ValueError:
        pass
    L.add_adjust({"op": "move", "lo": lo, "hi": hi, "dx": 1})
    eq(len(L.adjust["spans"]), 1, "the correction on a run was recorded")
    eq(written, [mau5lines.ADJUST], "and written")


def t_shift_stays_on_its_own_ear():
    """'shift' takes positions from further along the LED's own strip --
    on an ear, its own region.  Every ear row is group -1, and by group
    alone ear1's rim took ear2's rim positions."""
    import mau5map
    base = mau5map.load(adjust=False)
    pos = {r["index"]: (r["x"], r["y"], r["z"]) for r in base}
    region = {r["index"]: r["region"] for r in base}
    eq((region[492], region[509], region[510]), ("ear1_rim", "ear1_rim", "ear2_rim"),
       "rim spans")
    d = _tmpdir()
    try:
        path = os.path.join(d, "adjust.json")
        json.dump({"spans": [{"op": "shift", "lo": 500, "hi": 505, "by": 1},
                             {"op": "shift", "lo": 507, "hi": 509, "by": 3},
                             {"op": "shift", "lo": 526, "hi": 528, "by": 2}]},
                  open(path, "w"))
        rows, done = mau5map.apply_adjustments(copy.deepcopy(base), path=path)
        eq(len(done), 3, "all three applied")
        by = {r["index"]: (r["x"], r["y"], r["z"]) for r in rows}
        for i in range(500, 506):
            eq(by[i], pos[i + 1], "led %d should take %d's place" % (i, i + 1))
        for i in (507, 508, 509):
            eq(by[i], pos[509], "led %d runs off ear1's rim and stops at its end" % i)
        for i in (526, 527, 528):
            eq(by[i], pos[min(i + 2, 528)], "led %d must stay on ear2's rim" % i)
        for i in range(398, 621):
            if not (500 <= i <= 509 or 526 <= i <= 528):
                eq(by[i], pos[i], "led %d moved and nothing asked it to" % i)
    finally:
        shutil.rmtree(d, ignore_errors=True)


def t_baralign_reads_the_chain_as_it_is():
    """mau5baralign scores each LED against the map's height for it, so
    the centroids must be keyed by the same chain as the map."""
    import mau5baralign, mau5locate, mau5slots as S
    raw = mau5locate.load()
    meas = mau5baralign.measured()
    eq(S.pose_chain(mau5locate.OUT), S.BEFORE_CUT, "the front pose predates the cut")
    eq(meas[491]["cx"], raw[491]["cx"], "before the cut nothing moves")
    eq(meas[492]["cx"], raw[493]["cx"], "new 492 is old 493")
    eq(meas[620]["cx"], raw[621]["cx"], "new 620 is old 621")
    ok(max(meas) == S.TOTAL_N - 1, "nothing past the end of the chain")


def t_walk_leaves_the_reference_alone():
    """A walk session goes to its own file, and only once it holds
    something.  It used to replace data/cal/walk_session.json -- the
    first night's 78 sections, which the tests and three tools read --
    on every exit, with an empty session if nothing was walked."""
    import mau5walk
    import urllib.request
    from http.server import ThreadingHTTPServer
    ref = os.path.join(HERE, "data", "cal", mau5walk.REFERENCE)
    before = _sha(ref)

    class Pix:
        def send(self, frame, correct=False):
            pass

        def clear(self):
            pass
    d = _tmpdir()
    walk = mau5walk.Walk(Pix(), 621)
    srv = None
    try:
        path = mau5walk.session_path(d)
        ok(os.path.basename(path).startswith("walk_2"), "session file named by date")
        eq(mau5walk.save_session(walk, path), None, "an empty session wrote a file")
        eq(os.listdir(d), [], "an empty session wrote a file")
        try:
            walk.new_section("x")
            mau5walk.save_session(walk, os.path.join(d, mau5walk.REFERENCE))
            raise AssertionError("wrote over the reference walk")
        except ValueError:
            pass
        srv = ThreadingHTTPServer(("127.0.0.1", 0), mau5walk.make_handler(walk, path))
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        url = "http://127.0.0.1:%d/api/save" % srv.server_address[1]
        got = json.load(urllib.request.urlopen(url, timeout=5))
        eq(got["saved"], path, "GET /api/save")
        req = urllib.request.Request(url, data=b"{}", method="POST",
                                     headers={"Content-Type": "application/json"})
        eq(json.load(urllib.request.urlopen(req, timeout=5))["saved"], path,
           "POST /api/save")
        eq(len(json.load(open(path))["sections"]), 1, "the session's section")
        eq(sorted(os.listdir(d)), [os.path.basename(path)], "one file, this session's")
    finally:
        walk._stop.set()
        if srv:
            srv.shutdown()
        shutil.rmtree(d, ignore_errors=True)
    eq(_sha(ref), before, "the reference walk changed")


GROUP = [t_cut_follows_each_pose_file,
         t_locate_stamps_and_will_not_overwrite,
         t_eye_waits_out_the_lag,
         t_eye_uploads_cannot_cross,
         t_review_waits_out_the_lag,
         t_lines_correct_only_what_is_lit,
         t_shift_stays_on_its_own_ear,
         t_baralign_reads_the_chain_as_it_is,
         t_walk_leaves_the_reference_alone]
