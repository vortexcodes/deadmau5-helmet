import sys, os, json
sys.path.insert(0, os.getcwd())
import numpy as np, mau5show
base="deadmau5 - Some Chords (Radio Edit)"
show=json.load(open("shows/%s.json"%base))
music=mau5show._music_for(show,"shows/%s.mp3"%base)
print("fps",music.fps)
def tof(bar):
    t=0.124+4*bar*0.46875
    return t+0.032 if t>=135.1 else t
secs=[(0,4),(4,8),(8,12),(12,16),(16,24),(24,27.75),(28,36),(36,44),(44,52),(52,59),(60,62),(62,64),(64,68),(68,72),(72,76),(76,84),(84,88),(88,91.75),(92,100),(100,107),(107,108),(108,110)]
for a,b in secs:
    ts=np.arange(tof(a),tof(b),1/60)
    row="%6.2f-%6.2f"%(a,b)
    for band in ("bass","mid","high"):
        for punch in (False,True):
            v=np.array([music.band_at(t,band,punch=punch) for t in ts])
            row+="  %s%s %s"%(band[0],"p" if punch else "e","/".join("%.2f"%x for x in np.percentile(v,[10,50,90,99])))
    print(row)
