import sys, os
sys.path.insert(0, os.getcwd()); sys.path.insert(0, os.environ["KIT"])
import numpy as np, grid
d = grid.env_of("shows/deadmau5 - FN Pig.mp3")
m=np.load(os.environ["KIT"]+"/work/fnpig/mono.npy"); sr=22050
spb=0.46875; t0=0.490; tt=d["tt"]
# 1. which beats carry the backbeat: mean onset per beat position over the sparse groove, by band
def perbeat(lo,hi,nm):
    e=d[nm+"_od"]; o=np.zeros(4); 
    for b in range(lo,hi):
        for q in range(4):
            t=t0+(b+q/4)*4*spb; i=np.searchsorted(tt,t)
            o[q]+=e[max(0,i-2):i+4].max()
    return o/(hi-lo)
for (lo,hi) in ((118,125),(126,133),(134,141),(166,173),(266,273),(275,281)):
    print("bars %d-%d onset per beat position (1 2 3 4 of the current bar line)"%(lo,hi))
    for nm in ("sub","bass","lowmid","mid","pres","air"):
        v=perbeat(lo,hi,nm); print("   %-7s"%nm+" ".join("%5.2f"%x for x in v)+"   "+"strongest beat %d"%(v.argmax()+1))
# 2. burst shape: 1-11 kHz energy, 32nds, either side of each turnaround, averaged over the turnarounds
N=512;H=128;win=np.hanning(N);f=np.fft.rfftfreq(N,1/sr);mk=(f>2500)&(f<11000)
def hf(t):
    a=int(t*sr)-N//2; x=m[a:a+N]
    return np.log1p(np.abs(np.fft.rfft(x*win))[mk].sum()*0.05)
for B in ((126,134,142,150,158,174,182,190,198),(234,242,250,258)):
    prof=np.zeros(48)
    for b in B:
        for k in range(48):
            prof[k]+=hf(t0+(b-1+ (k-0)/32)*4*spb)
    prof/=len(B)
    print("HF level, last bar of a phrase then the next, per 16th (avg of %s..)"%B[0])
    print("  "+" ".join("%.1f"%prof[k:k+2].mean() for k in range(0,48,2)))
# 3. the low end at 16ths through each change, to see where it moves
def low(t,lo,hi):
    n=4096;a=int(t*sr)-n//2;x=m[max(a,0):a+n]
    F=np.fft.rfftfreq(len(x),1/sr);S=np.abs(np.fft.rfft(x*np.hanning(len(x))))
    k=(F>=lo)&(F<hi); return F[k][S[k].argmax()], np.log1p(S[k].sum()*.02)
for b in (125,133,165,173,205,233,265):
    print("bar %d last two beats + next bar two beats, sub-200Hz level at 8ths:"%b," ".join("%.1f"%low(t0+(b+.5+k/8)*4*spb,30,200)[1] for k in range(8)))
