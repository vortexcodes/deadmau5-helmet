import sys, os
sys.path.insert(0, os.getcwd()); sys.path.insert(0, os.environ["KIT"])
import numpy as np, grid
d = grid.env_of("shows/deadmau5 - FN Pig.mp3")
tt=d["tt"]; dt=tt[1]-tt[0]
spb=.46875
for lo,hi in ((1,45),(47,90),(120,160)):
  for nm in ("sub","bass","lowmid","mid"):
    m=(tt>=lo)&(tt<hi)
    v=d[nm][m]; v=v-np.convolve(v,np.ones(400)/400,"same")
    ac=np.correlate(v,v,"full")[len(v)-1:]
    ac/=ac[0]
    # peaks up to 4 s
    from numpy import argmax
    pk=[(i*dt,ac[i]) for i in range(5,int(4/dt)) if ac[i]>ac[i-1] and ac[i]>=ac[i+1] and ac[i]>0.1]
    print(lo,hi,nm," ".join("%.3f(%.2f)[%.2fb]"%(p,a,p/spb) for p,a in pk[:12]))
# print local maxima of the sub level in the first 20 s
v=d["bass"]+d["sub"]
sm=np.convolve(v,np.ones(5)/5,"same")
m=np.where((tt>0)&(tt<30))[0]
pk=[i for i in m[1:-1] if sm[i]>sm[i-1] and sm[i]>=sm[i+1] and sm[i]>np.median(sm[m])+0.02 and sm[i]==sm[max(0,i-15):i+15].max()]
print("pulse peaks:"," ".join("%.2f"%tt[i] for i in pk))
print("in beats:"," ".join("%.2f"%((tt[i]-0.49)/spb) for i in pk))
