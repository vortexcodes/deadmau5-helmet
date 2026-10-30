"""scenes -- the choreographed shows, held to the same frame on both devices.

A scene show is the one thing here written by hand for a song, and the
one thing whose look depends on two renderers agreeing about arithmetic
nobody can eyeball: mau5scene.Scenes on the laptop and Scenes in
show.js on the phone.  So every test below either compares the two
frame for frame, or makes sure that when the choreography is absent,
switched off or broken, what plays is exactly the cue list that played
before it existed.
"""

import contextlib
import io
import json
import os
import shutil
import subprocess
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from test_mau5 import ok, eq, note, HERE, _node, _ShowDrive  # noqa: E402

# A note made here should reach the run's own list, not a second copy of
# the module that nobody prints.
note = getattr(sys.modules.get("__main__"), "note", note)


class _SceneDrive(_ShowDrive):
    """test_mau5's drive, marked as an analysis: band values read its curves."""
    analysed = True


def _scene_times(spec, duration, even=40):
    """Where a scene show is most likely to disagree with itself.

    Just inside every edge, the middle of everything, inside the peak
    hold of every hit, the middle of every dark beat before a drop, a
    spread across the song, and one moment either side of it.
    """
    g = spec["grid"]
    t0, spb, lead = g["t0"], g["spb"], g.get("lead", 0.0)

    def at(bar):
        return t0 + 4.0 * bar * spb - lead

    ts = []
    for s in spec["scenes"]:
        a, b = at(s["from"]), at(s["to"])
        ts += [a + 0.001, (a + b) / 2.0, b - 0.001]
        if s["out"] > 0:
            ts.append(b - s["out"] * spb / 2.0)
    for x in spec["hits"]:
        a = at(x["at"])
        ts += [a + 0.001, a + 0.05, a + x["beats"] * spb / 2.0]
    ts += list(np.linspace(0.0, duration, even))
    ts += [at(-1) - 0.5, at(spec["bars"]) + 0.5]
    return sorted({round(float(t), 6) for t in ts})


def _compare(name, show, times, res, music, h):
    """Worst difference in counts, and the first label that disagrees."""
    import mau5show
    py = mau5show.Player(show, helmet=h, music=music)
    ok(py.scenes is not None, "%s: the laptop is not playing its scenes" % name)
    ok(res["scenes"], "%s: the phone is not playing its scenes" % name)
    worst, where = 0.0, ""
    for k, t in enumerate(times):
        a = np.asarray(py.frame(t), float)
        b = np.asarray(res["frames"][k], float).reshape(-1, 3)
        d = max(float(np.abs(a - b).max()), abs(py.gain - res["gains"][k]) * 255.0)
        if d > worst:
            worst, where = d, "%s at t=%.3f (%s)" % (name, t, py.label)
        eq(res["labels"][k], py.label, "%s at t=%.3f: the label" % (name, t))
    return worst, where


def _scene_shows(data):
    return [n for n in sorted(data["shows"]) if data["shows"][n].get("scenes")]


def t_scene_shows_match_phone():
    """Each scene show, at every edge and hit, the same on both devices.

    Twice: with an analysed drive, so the band-driven values read the
    curves, and with a plain one, where both sides must take the
    midpoint.  Both sides must also say they are playing scenes, so a
    silent fall back to the cue list cannot pass as agreement.
    """
    import mau5engine as E
    import mau5offline
    data = mau5offline.bundle()
    names = _scene_shows(data)
    ok(names, "no bundled show carries scenes")
    h = E.Helmet()
    worst, where, n = 0.0, "", 0
    for name in names:
        show = data["shows"][name]
        times = _scene_times(show["scenes"], show["duration"])
        for analysed, music in ((True, _SceneDrive()), (False, _ShowDrive())):
            res = _node("showtest.js", {"data": data, "shows": [name], "times": times,
                                        "analysed": analysed})
            if res is None:
                return note("scenes: node not installed, the phone went unchecked")
            w, at = _compare(name, show, times, res[name], music, h)
            n += len(times)
            if w > worst:
                worst, where = w, at
    ok(worst < 0.01, "the phone's scenes differ by %.4f counts (%s)" % (worst, where))
    note("scenes: %d shows, %d frames, worst %.5f counts (%s)"
         % (len(names), n, worst, where or "exact"))


# Every primitive, every mix, every value form and every region, on a
# made-up grid, so a disagreement in a corner the shipped songs never
# reach still fails here.
SYNTHETIC = {
    "v": 1, "show": "synthetic", "lead": 0.0,
    "marks": {"go": 4, "blades": "go+12", "pre": 20, "title": 22, "boom": 30},
    "palettes": {
        "warm": [[0, 0, 0], [255, 40, 0], [255, 200, 40]],
        "loop": {"stops": [[255, 0, 0], [0, 255, 0], [0, 0, 255]], "wrap": True},
        "pure": [[0, 0, 255], [0, 255, 0], [255, 255, 255]],
    },
    "motifs": {
        "ring": {"fx": "sweep", "on": "all", "axis": "r", "shape": "p", "from": 0,
                 "to": 1.2, "width": 0.25, "pal": "pure", "c": 1},
        "pair": [{"fx": "fill", "on": "left", "c": 0.1,
                  "gate": ["x.......", 0.25, 0.75]},
                 {"fx": "fill", "on": "right", "c": 0.6,
                  "gate": {"pat": "....o...", "step": 0.25, "decay": 0.75, "floor": 0.1}}],
    },
    "scenes": [
        {"name": "fills", "from": -1, "to": "go", "pal": "warm", "layers": [
            {"fx": "fill", "on": "all", "c": [0.1, 0.9], "gain": 0.4},
            {"fx": "fill", "on": "shell", "mix": "max", "c": 0.7,
             "gate": ["x.o.", 0.25, 0.4, 0.2], "env": {"in": 4, "out": 2}},
            {"fx": "fill", "on": "ears", "mix": "over", "pal": "loop",
             "c": {"band": "bass", "lo": 0.1, "hi": 0.9, "punch": True},
             "gain": {"band": "high", "lo": 0.2, "hi": 1}}]},
        {"name": "grads", "from": "go", "to": 8, "pal": "loop", "pump": 0.3, "layers": [
            {"fx": "grad", "on": "shell", "axis": "y", "scale": 2, "speed": 0.25,
             "gain": 0.6},
            {"fx": "grad", "on": "all", "mix": "max", "axis": "a", "axis2": "x",
             "wave": "saw", "scale": 3, "speed": {"4": 0.25, "6": -0.5}, "warp": 0.3,
             "wscale": 1.5, "wspeed": 0.25, "lo": 0.1, "hi": 0.8},
            {"fx": "grad", "on": "ears", "mix": "over", "axis": "r", "axis2": "u",
             "ofs": [0, 1], "pal": "warm", "lo": 0.2, "hi": 1.0},
            {"fx": "grad", "on": "tube0+tube2", "axis": "al", "speed": 0.5,
             "pal": "warm"}]},
        {"name": "sweeps", "from": 8, "to": 12, "pal": "warm", "out": 1, "layers": [
            {"fx": "sweep", "on": "shell", "axis": "y", "shape": "p", "mode": "band",
             "width": 0.12, "from": -0.1, "to": 1.1, "c": 0.9, "gain": [0.2, 0.9]},
            {"fx": "sweep", "on": "all", "mix": "max", "axis": "x", "shape": "saw",
             "mode": "fill", "soft": 0.15, "speed": {"8": 0.25, "10": 0.5},
             "cgrad": 0.5, "c": 0.2},
            {"fx": "sweep", "on": "rims", "mix": "over", "axis": "u", "shape": "tri",
             "speed": 0.5, "width": 0.3, "pal": "loop"}]},
        {"name": "sparks", "from": 12, "to": "blades", "pal": "warm", "layers": [
            {"fx": "sparks", "on": "face", "rate": 2, "life": 1.5, "loop": 16,
             "seed": 3, "c": 0.75, "spread": 0.2, "gain": 0.8},
            {"fx": "sparks", "on": "all", "mix": "max", "rate": {"12": 1, "14": 4},
             "life": 0.5, "c": 1, "gain": {"band": "high", "lo": 0.2, "hi": 1}},
            {"fx": "sparks", "on": "ears", "mix": "over", "rate": 3, "life": 1,
             "seed": 9, "nbr": 0.6, "pal": "loop", "c": 0.3, "spread": 0.5}]},
        {"name": "blades", "from": "blades", "to": "pre", "pal": "pure", "layers": [
            {"fx": "blades", "seq": ["012"], "step": {"16": 1, "18": 0.5},
             "side": "alt", "rim": 0.6, "c": 0.25, "ctip": 0.75},
            {"fx": "blades", "on": "ear1", "mix": "max", "seq": ["0", "1", "2", "1"],
             "step": 0.5, "rise": 0.3, "keep": 0.2, "c": 0.6},
            {"fx": "blades", "on": "tubes", "mix": "over", "seq": [[0, 2], "1"],
             "side": "ear2", "step": 2, "rise": 1, "keep": 0.3, "c": 0}]},
        {"name": "presets", "from": "pre", "to": 26, "pal": "warm",
         "pump": {"pat": "x.......x.......", "step": 0.25, "depth": 0.3, "decay": 0.6},
         "layers": [
            {"fx": "preset", "name": "eyes", "on": "face",
             "params": {"color": "warm@0.66"}, "gate": ["x", 4, 4, 0.5]},
            {"fx": "preset", "name": "sprite", "on": "shell", "mix": "max",
             "params": {"sprite": "x_eyes", "color": [0, 120, 255]}, "gain": 0.6}]},
        {"name": "regions", "from": 26, "to": "boom", "pal": "loop", "layers": [
            {"use": "pair", "gain": 0.8},
            {"fx": "fill", "on": "ear2", "mix": "max", "c": 0.5, "gain": 0.5},
            {"fx": "fill", "on": "tube1", "mix": "over", "c": 0.9},
            {"fx": "grad", "on": "ears", "axis": "a", "scale": 4, "speed": 0.25,
             "gain": 0.3}]},
        {"name": "later", "from": 34, "to": 38, "like": "grads",
         "patch": {"0": {"gain": 0.3}}, "add": [{"use": "ring", "gain": 0.5}],
         "each": {"env": {"out": 4}}},
    ],
    "hits": [
        {"name": "TITLE", "at": "title", "beats": 8, "layers": [
            {"fx": "preset", "name": "text", "on": "face", "fit": True, "mix": "over",
             "env": {"in": 1, "out": 2}, "params": {"text": "SYN", "color": "warm@1"}}]},
        {"name": "BOOM", "at": "boom", "beats": 2, "layers": [
            {"fx": "fill", "on": "all", "pal": "pure", "c": 1, "gain": [1, 0]},
            {"use": "ring"}]},
        {"name": "echo", "at": "boom+0.25", "beats": 4, "layers": [
            {"fx": "blades", "seq": ["012"], "step": 4, "rise": 0.25, "keep": 0,
             "pal": "pure", "c": 0.5}]},
        {"name": "roll", "at": 11, "beats": 3.5, "layers": [
            {"fx": "fill", "on": "shell", "gate": ["x", 0.5, 0.4], "gain": 0.5}]},
    ],
}


def _synthetic_spec():
    import mau5scene
    tr = json.loads(json.dumps(SYNTHETIC))
    return mau5scene.compile_treatment(tr, {"t0": 0.5, "spb": 0.5}, 40)


def t_scene_every_primitive():
    """A synthetic song touching everything a scene can do, on both devices."""
    import mau5engine as E
    import mau5offline
    import mau5scene
    spec = _synthetic_spec()
    errs, _ = mau5scene.lint(spec, E.Helmet())
    eq(errs, [], "the synthetic treatment's lint")
    used = {(L["fx"], L["mix"]) for s in spec["scenes"] + spec["hits"] for L in s["layers"]}
    for fx in mau5scene.FX:
        for mix in mau5scene.MIX:
            ok((fx, mix) in used, "the synthetic show never mixes %s with %s" % (fx, mix))
    regions = set()
    for s in spec["scenes"] + spec["hits"]:
        for L in s["layers"]:
            regions |= set(L["on"].split("+"))
    eq(sorted(set(mau5scene.REGIONS) - regions), [], "regions the synthetic show missed")

    data = mau5offline.bundle()
    data["shows"] = {"synthetic": {"duration": 20.0, "cues": [], "scenes": spec}}
    show = data["shows"]["synthetic"]
    times = _scene_times(spec, 20.0, even=80)
    h = E.Helmet()
    worst, where = 0.0, ""
    for analysed, music in ((True, _SceneDrive()), (False, _ShowDrive())):
        res = _node("showtest.js", {"data": data, "shows": ["synthetic"], "times": times,
                                    "analysed": analysed})
        if res is None:
            return note("scenes: node not installed, the primitives went unchecked")
        w, at = _compare("synthetic", show, times, res["synthetic"], music, h)
        if w > worst:
            worst, where = w, at
        # and the frames are not all dark, or agreement means nothing
        lit = sum(1 for f in res["synthetic"]["frames"] if max(f) > 1)
        ok(lit > len(times) * 0.7, "the synthetic show is dark in %d of %d frames"
           % (len(times) - lit, len(times)))
    ok(worst < 0.01, "a scene primitive differs by %.4f counts (%s)" % (worst, where))
    note("scenes: every primitive over %d frames, worst %.5f counts" % (2 * len(times), worst))


def _treatments():
    import mau5scene
    d = mau5scene.SCENES
    if not os.path.isdir(d):
        return []
    return sorted(f[:-len(".scene.json")] for f in os.listdir(d)
                  if f.endswith(".scene.json"))


def t_scenes_compiled_fresh():
    """The scenes in each show are what its treatment compiles to today.

    A treatment edited without recompiling would leave the helmet doing
    the old choreography with nothing to say so.
    """
    import mau5scene
    bases = _treatments()
    ok(bases, "no treatments in shows/scenes")
    for base in bases:
        show, music, _ = mau5scene._show_and_music(base)
        ok("scenes" in show, "%s has a treatment and no scenes compiled in" % base)
        fresh = json.loads(json.dumps(mau5scene.compile_for(base, music)))
        ok(fresh == show["scenes"], "%s: the compiled scenes are stale -- run "
           "mau5scene.py compile" % base)


def t_scene_lint():
    """Both shipped treatments pass the lint the compiler enforces."""
    import mau5scene
    for base in _treatments():
        with contextlib.redirect_stdout(io.StringIO()):
            spec = mau5scene.compile_show(base)
        errs, _ = mau5scene.lint(spec)
        eq(errs, [], "%s lint" % base)


def t_cue_shows_unchanged():
    """No treatment, no scenes; and every way of switching them off is the cue list.

    Removing `scenes`, `mode: "cues"` and MAU5_CUES=1 must each give
    exactly the frames the cue list gave before scenes existed -- on
    the laptop, and with ?cues on the phone.  A renderer that throws
    falls back to the same frames on both devices.
    """
    import mau5engine as E
    import mau5offline
    import mau5show
    data = mau5offline.bundle()
    have = set(_treatments())
    for name, sh in data["shows"].items():
        if name not in have:
            ok("scenes" not in sh, "%s has scenes but no treatment" % name)
    names = _scene_shows(data)
    ok(names, "no scene shows to switch off")
    h = E.Helmet()
    drive = _ShowDrive()
    for name in names:
        show = data["shows"][name]
        bare = {k: v for k, v in show.items() if k != "scenes"}
        times = list(np.linspace(1.0, show["duration"] - 1.0, 20))
        want = [np.asarray(mau5show.Player(bare, helmet=h, music=drive).frame(t), float)
                for t in times]
        a = mau5show.Player(dict(show, mode="cues"), helmet=h, music=drive)
        ok(a.scenes is None, "mode cues still built the scenes")
        old = os.environ.get("MAU5_CUES")
        os.environ["MAU5_CUES"] = "1"
        try:
            b = mau5show.Player(show, helmet=h, music=drive)
        finally:
            if old is None:
                os.environ.pop("MAU5_CUES", None)
            else:
                os.environ["MAU5_CUES"] = old
        ok(b.scenes is None, "MAU5_CUES=1 still built the scenes")
        broken = mau5show.Player(show, helmet=h, music=drive)
        ok(broken.scenes is not None, "%s did not build its scenes" % name)

        def boom(*a, **k):
            raise RuntimeError("a deliberately broken renderer")
        broken.scenes.frame = boom
        quiet = io.StringIO()
        with contextlib.redirect_stdout(quiet):
            got_broken = [np.asarray(broken.frame(t), float) for t in times]
        ok("playing the cue list" in quiet.getvalue(), "a broken renderer fell back silently")
        for k, t in enumerate(times):
            for who, f in (("mode cues", a.frame(t)), ("MAU5_CUES", b.frame(t)),
                           ("a broken renderer", got_broken[k])):
                d = float(np.abs(np.asarray(f, float) - want[k]).max())
                ok(d == 0.0, "%s: %s differs from the cue list by %.3f at t=%.1f"
                   % (name, who, d, t))

    if not shutil.which("node"):
        return note("scenes: node not installed, ?cues went unchecked")
    js = r"""
let raw = ''; process.stdin.setEncoding('utf8');
process.stdin.on('data', c => { raw += c; });
process.stdin.on('end', () => {
  const job = JSON.parse(raw);
  global.window = global;
  const E = require(job.here + '/remote/offline/engine.js');
  const S = require(job.here + '/remote/offline/show.js');
  const D = job.data;
  const dec = (b64, C) => {
    const bin = Buffer.from(b64, 'base64');
    return new C(bin.buffer, bin.byteOffset, bin.byteLength / C.BYTES_PER_ELEMENT);
  };
  const geo = { n: D.n, regions: D.regions };
  for (const k of Object.keys(D.f32)) geo[k] = dec(D.f32[k], Float32Array);
  for (const k of Object.keys(D.i16)) geo[k] = dec(D.i16[k], Int16Array);
  const h = E.makeHelmet(geo);
  const music = {
    bands: true, bpm: 128.0,
    levelAt: t => 0.5 + 0.4 * Math.sin(t * 1.7),
    beatPhase: t => (t * 2.13) % 1, beatIndex: t => t * 2.13,
    isDownbeat: t => ((t * 0.53) % 1) < 0.05,
    pitchAt: t => (t * 0.11) % 1, centroidAt: t => 0.5 + 0.4 * Math.sin(t * 0.63),
    bandsAt: (t, n) => { const a = new Float64Array(n);
      for (let k = 0; k < n; k++) a[k] = 0.5 + 0.4 * Math.sin(t * 0.9 + k * 0.6); return a; },
    bandAt: (t, name, punch) => 0.5,
  };
  const out = {};
  const buf = new Float32Array(h.n * 3);
  const run = (show, times) => {
    const p = new S.ShowPlayer(show, h, D);
    const fr = times.map(t => { p.frame(t, music, buf); return Array.from(buf); });
    return { scenes: !!p.scenes, frames: fr };
  };
  for (const name of job.shows) {
    const show = D.shows[name];
    const bare = Object.assign({}, show); delete bare.scenes;
    const broken = Object.assign({}, show, { scenes: Object.assign({}, show.scenes, {
      scenes: show.scenes.scenes.map(s => Object.assign({}, s, {
        layers: s.layers.map(L => Object.assign({}, L, { fx: 'nonsense' })) })) }) });
    const r = { bare: run(bare, job.times) };
    global.location = { search: '?x=1&cues' };
    r.query = run(show, job.times);
    global.location = { search: '' };
    r.mode = run(Object.assign({}, show, { mode: 'cues' }), job.times);
    const warn = console.warn; console.warn = () => {};
    r.broken = run(broken, job.times);
    console.warn = warn;
    r.on = run(show, job.times);
    out[name] = r;
  }
  process.stdout.write(JSON.stringify(out));
});
"""
    times = [5.0, 61.0, 133.3, 250.0]
    p = subprocess.run(["node", "-e", js], input=json.dumps(
        {"here": HERE, "data": data, "shows": names, "times": times}),
        capture_output=True, text=True, cwd=HERE, timeout=300)
    ok(p.returncode == 0, "node failed:\n%s" % p.stderr[-2000:])
    res = json.loads(p.stdout)
    for name in names:
        r = res[name]
        ok(r["on"]["scenes"], "%s: the phone did not build its scenes" % name)
        for who in ("query", "mode", "broken"):
            ok(not r[who]["scenes"], "%s: %s still plays scenes on the phone" % (name, who))
            ok(r[who]["frames"] == r["bare"]["frames"],
               "%s: %s on the phone is not the cue list" % (name, who))


def t_scene_cost():
    """A scene frame costs the phone almost nothing beside the cue lists.

    Timed under node on this machine, which is several times a phone:
    under half a millisecond a frame on average, and under two even
    while a title scrolls, leaves the phone's few milliseconds a frame
    for the guard and the wire.
    """
    import mau5offline
    data = mau5offline.bundle()
    names = _scene_shows(data)
    ok(names, "no scene shows to time")
    worst_mean, worst_max, where = 0.0, 0.0, ""
    for name in names:
        show = data["shows"][name]
        times = sorted(set(list(np.linspace(0.0, show["duration"], 600))
                           + _scene_times(show["scenes"], show["duration"])))
        res = _node("showtest.js", {"data": data, "shows": [name], "times": times})
        if res is None:
            return note("scenes: node not installed, the cost went unchecked")
        ms = np.asarray(res[name]["ms"], float)
        # One stray scheduling hiccup is not the renderer: the slowest
        # frame is judged by the next slowest.
        mx = float(np.sort(ms)[-2])
        worst_mean = max(worst_mean, float(ms.mean()))
        if mx > worst_max:
            worst_max, where = mx, name
    ok(worst_mean < 0.5, "a scene frame averages %.3f ms under node" % worst_mean)
    ok(worst_max < 2.0, "the slowest scene frames take %.3f ms (%s)" % (worst_max, where))
    note("scenes: %.3f ms a frame on average, %.3f at worst, under node"
         % (worst_mean, worst_max))


GROUP = [t_scene_every_primitive, t_scene_shows_match_phone, t_scenes_compiled_fresh,
         t_scene_lint, t_cue_shows_unchanged, t_scene_cost]
