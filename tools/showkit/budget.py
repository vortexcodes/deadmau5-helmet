"""budget.py -- keep a treatment inside the long set's power budget without changing any limit.

The guard caps the shell near 300 mA (mean about 8 of 255 sent). A shell asked for far more than that is
thrown away by the guard, and a shell sitting at its cap all song costs most of an 11.5 W budget on its own.
So a generator can scale each scene's shell layers until the shell asks for about what the guard would send
anyway, which leaves the picture nearly as it was, and dim the ears by one factor for the whole song.

    sys.path.insert(0, KIT); from budget import fit
    fit(tr, shell_in={"scene": 23.5, ...}, ask=6.0, ears=0.8, keep=lambda L: ...)

`shell_in` is each scene's mean shell level before the guard, as the treatment stood before scaling (measure it
with a per-scene meter over the compiled show); scenes not named are left alone. Hits are always left as
written: they are the moments. `keep(layer)` returning True leaves a layer unscaled, for occluders that hide
by painting dark with mix "over" and would stop painting if dimmed. Run from the repo root."""
import copy, os, sys
sys.path.insert(0, os.getcwd())
from mau5scene import _merge, DEFAULT_ON

SHELL = {"shell", "face", "jaw", "left", "right", "shell+rims"}
EARS = {"ears", "ear1", "ear2", "tubes", "rims", "tube0", "tube1", "tube2", "tubes1", "tubes2", "rim1", "rim2",
        "tube0+tube1", "tube0+tube1+tube2"}


def scaled(v, k):
    """A layer value times k: a number, a ramp, steps at bars, or a band's lo and hi."""
    if isinstance(v, (int, float)):
        return round(v * k, 3)
    if isinstance(v, list):
        return [scaled(x, k) for x in v]
    if isinstance(v, dict) and "band" in v:
        return dict(v, lo=scaled(v.get("lo", 0.0), k), hi=scaled(v.get("hi", 1.0), k))
    if isinstance(v, dict):
        return {b: scaled(x, k) for b, x in v.items()}
    return v


def flatten(tr):
    """Every scene as plain layers, resolved as mau5scene compiles them: like, patch, add, motifs, each."""
    motifs = tr.get("motifs") or {}

    def expand(layers):
        out = []
        for L in layers or []:
            if "use" in L:
                mot = motifs[L["use"]]
                over = {k: v for k, v in L.items() if k != "use"}
                for m in (mot if isinstance(mot, list) else [mot]):
                    out += [_merge(sub, over) for sub in expand([m])]
            else:
                out.append(dict(L))
        return out

    authored, scenes = {}, []
    for i, s in enumerate(tr["scenes"]):
        if "like" in s:
            base = authored[s["like"]]
            layers, pump, pal = copy.deepcopy(base["layers"]), copy.deepcopy(base["pump"]), base["pal"]
        else:
            layers, pump, pal = [], None, None
        if "layers" in s:
            layers = copy.deepcopy(s["layers"])
        for k, v in (s.get("patch") or {}).items():
            layers[int(k)] = _merge(layers[int(k)], v)
        layers = layers + copy.deepcopy(s.get("add") or [])
        if "pump" in s:
            pump = s["pump"]
        pal = s.get("pal", pal)
        authored[s.get("name") or "scene %d" % i] = {"layers": layers, "pump": pump, "pal": pal}
        each = s.get("each") or {}
        out = {k: v for k, v in s.items() if k not in ("like", "patch", "add", "each", "layers", "pump", "pal")}
        out["layers"] = [_merge(L, each) for L in expand(layers)]
        if pump is not None:
            out["pump"] = pump
        if pal is not None:
            out["pal"] = pal
        scenes.append(out)
    return scenes


def fit(tr, shell_in, ask=6.0, ears=1.0, keep=None):
    """Flatten tr's scenes, then scale each named scene's shell layers by ask / shell_in (never up) and every
    scene's ear layers by `ears`. Changes tr in place."""
    tr["scenes"] = flatten(tr)
    for sc in tr["scenes"]:
        k = min(1.0, ask / shell_in[sc["name"]]) if sc["name"] in shell_in else 1.0
        for L in sc["layers"]:
            if keep and keep(L):
                continue
            on = L.get("on") or DEFAULT_ON[L["fx"]]
            f = k if on in SHELL else ears if on in EARS else 1.0
            if f != 1.0:
                L["gain"] = scaled(L.get("gain", 1.0), f)
    return tr


def tidy(v, places=4):
    """Every float in a treatment rounded to `places` decimals. The page carries every show compiled, and a
    value like 0.4156427751014326 costs it bytes that do not compress; 4 places of a bar is 0.2 ms."""
    if isinstance(v, float):
        return round(v, places)
    if isinstance(v, list):
        return [tidy(x, places) for x in v]
    if isinstance(v, dict):
        return {k: tidy(x, places) for k, x in v.items()}
    return v
