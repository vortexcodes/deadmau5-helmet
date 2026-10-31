#!/usr/bin/env python3
"""Raise Your Weapon's real grid: 128.000 BPM for 112 bars, a 16-bar accelerando that is linear in
beats from 128 to 140, then 140.000 BPM to the end. Written as a beat list with every beat at or
above the 140 beat length (the format's holds can only delay), so 140 is the line and everything
before it is one hold per beat. The last beats of the ramp have under 5 ms each to hold, which the
format would drop as noise and then refuse the sum, so those are collected until there is enough."""
import numpy as np, subprocess, sys, os
BASE="deadmau5 - Raise Your Weapon"
SA=0.46875; SC=60/140.
T0=0.0264            # bar 0, from 90-210 s against the 128 grid
DROP=242.1399        # bar 130, from 242-434 s against the 140 grid
RAMP_BARS=(112,128)
TA=T0+448*SA          # bar 112
TC=DROP-2*4*SC        # bar 128
model=320*np.log(140/128.)   # seconds a linear ramp in beats takes over 64 beats
scale=(TC-TA)/model
print("ramp: bar 112 at %.4f, bar 128 at %.4f, %.4f s, the linear ramp predicts %.4f s, scale %.6f"%(TA,TC,TC-TA,model,scale))
def true_beat(k):
    if k<=448: return T0+k*SA
    if k<512:
        b=k-448
        return TA+scale*320*np.log((128+0.1875*b)/128)
    return TC+(k-512)*SC
dur=502.9365986
ks=[]; k=0
while true_beat(k)<dur-0.01:
    ks.append(k); k+=1
true=np.array([true_beat(k) for k in ks])
w=np.zeros_like(true); w[0]=true[0]
MIN=0.0056
for i in range(1,len(true)):
    h=true[i]-w[i-1]-SC
    if h<MIN: h=0.0
    w[i]=w[i-1]+SC+h
# what is still owed at bar 128 goes onto the last hold, so the 140 section starts exactly on its anchor
r=true[512]-w[512]
last=max(i for i in range(1,513) if (w[i]-w[i-1]-SC)>0.001)
w[last:]+=r
print("residual at bar 128 was %.2f ms, moved onto beat %d"%(r*1000,last))
print("written vs true: worst %.2f ms; last ramp holds:"%(1000*np.abs(w-true).max()), np.round(1000*(np.diff(w)-SC)[440:515],1).tolist())
p=os.path.join("shows","scenes",BASE+".beats")
open(p,"w").write("".join("%.6f\n"%t for t in w))
print("wrote",p,len(w),"beats",len(w)//4,"bars")
npz=os.path.join("shows",BASE+".analysis.npz")
if os.path.exists(npz): os.remove(npz)
subprocess.run([sys.executable,"mau5show.py","build",os.path.join("shows",BASE+".mp3")],check=True)
