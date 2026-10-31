# Writes the page's data bundle to a JSON file for the node sweeps.
import json, os, sys
os.chdir("/Users/jones/deadmau5 app"); sys.path.insert(0, ".")
import mau5drive, mau5offline
mau5drive.build(verbose=False)
d = mau5offline.bundle()
json.dump(d, open(sys.argv[1], "w"))
print(len(d["shows"]), "shows", len(json.dumps(d)) // 1024, "kB")
print("drive kB", sum(v["gz"] for v in json.load(open("data/offline/drive.json")).values()) // 1024)
