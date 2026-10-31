import sys, numpy as np, os
KIT=sys.argv[1]; sys.path.insert(0,KIT); sys.path.insert(0,os.getcwd())
import grid
d=grid.env_of("shows/deadmau5 - Raise Your Weapon.mp3")
od=grid.onsets(d); tt=d["tt"]; dt=tt[1]-tt[0]
dur=float(d["dur"])
print("dur",dur,"dt",dt)
win=30.0
cands=np.arange(60,190,0.25)
for t in np.arange(0,dur-win,15.0):
    a=int(t/dt); b=int((t+win)/dt)
    x=od[a:b]; x=x-x.mean()
    # comb score per tempo using autocorrelation
    ac=np.correlate(x,x,'full')[len(x)-1:]
    ac=ac/ max(ac[0],1e-9)
    sc=[]
    for bpm in cands:
        lag=60/bpm/dt
        v=0
        for k in (1,2,4):
            i=lag*k
            i0=int(i)
            if i0+1<len(ac):
                v+=ac[i0]*(1-(i-i0))+ac[i0+1]*(i-i0)
        sc.append(v)
    sc=np.array(sc)
    top=np.argsort(-sc)[:40]
    # peak pick
    picks=[]
    for j in top:
        if all(abs(cands[j]-p[0])>2 for p in picks):
            picks.append((cands[j],sc[j]))
        if len(picks)>=4:break
    print("%6.1f "%t+"  ".join("%6.2f(%.2f)"%p for p in picks))
