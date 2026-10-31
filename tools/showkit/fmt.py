"""from fmt import save; save(tr, path) -- writes a treatment one thing per line, so it can be edited by hand."""
import json
def block(items):
    return "[\n" + ",\n".join("  " + json.dumps(x) for x in items) + "\n ]"
def table(d):
    return "{\n" + ",\n".join("  %s: %s" % (json.dumps(k), json.dumps(v)) for k, v in d.items()) + "\n }"
def save(tr, path):
    out = ['{', '"v":1,', '"show":' + json.dumps(tr["show"]) + ',', '"about":' + json.dumps(tr.get("about", "")) + ',', '"lead":%s,' % json.dumps(tr.get("lead", 0)),
           '"marks":' + json.dumps(tr["marks"]) + ',', '"palettes":' + table(tr["palettes"]) + ',', '"motifs":' + table(tr.get("motifs", {})) + ',',
           '"scenes":' + block(tr["scenes"]) + ',', '"hits":' + block(tr.get("hits", [])), '}']
    open(path, "w").write("\n".join(out) + "\n")
    json.load(open(path))
    print("wrote", path, "scenes", len(tr["scenes"]), "hits", len(tr.get("hits", [])))
