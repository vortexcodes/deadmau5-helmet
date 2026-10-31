import sys, os
KIT=os.environ.get("KIT")
sys.path.insert(0, KIT); sys.path.insert(0, os.getcwd())
import numpy as np, grid as G
mp3="shows/deadmau5 - Some Chords (Radio Edit).mp3"
d=G.env_of(mp3)
print("dur",float(d["dur"]))
for spb,anchor in [(0.46875,0.115),(0.468860,0.115)]:
    for span in (2,4):
        rows,t0=G.phase_table(d,spb,anchor,span_bars=span)
        print("spb",spb,"span",span)
        print("  "+"  ".join("%d:%+.0f(%.2f)"%r for r in rows))
# fine refine of 128 assumption, first and second halves separately using bass-side too
for lo,hi in [(0,30),(30,60),(60,90),(90,120),(120,150),(150,180),(180,210)]:
    r=G.refine(d,0.46875,lo,hi,width=0.002,steps=81)
    print(lo,hi,"bpm %.3f spb %.6f"%(60/r[1],r[1]),"phase",r[2])
