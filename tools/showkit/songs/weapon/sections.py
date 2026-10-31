import sys, numpy as np, os
KIT=sys.argv[1]; sys.path.insert(0,KIT); sys.path.insert(0,os.getcwd())
import grid
d=grid.env_of("shows/deadmau5 - Raise Your Weapon.mp3")
def rf(lo,hi,bpm,w=0.01,steps=201):
    b=grid.refine(d,60/bpm,lo,hi,width=w,steps=steps)
    return b
for lo,hi,bpm in [(0,90,128),(30,90,128),(90,210,128),(90,150,128),(150,210,128),(225,470,140),(225,340,140),(340,470,140),(420,470,140),(225,300,140)]:
    sc,s,p=rf(lo,hi,bpm)
    print("%4d-%4d: spb %.6f BPM %.3f  phase16 %.3f  score %.3f"%(lo,hi,s,60/s,p,sc))
