import sys, os
sys.path.insert(0, os.getcwd())
import numpy as np
m=np.load(os.environ["KIT"]+"/work/fnpig/mono.npy")
sr=22050; spb=.46875; t0=.49
N=8192
win=np.hanning(N)
f=np.fft.rfftfreq(N,1/sr)
NOTES="C C# D D# E F F# G G# A A# B".split()
# chroma per beat
mask=(f>55)&(f<1500)
pc=(np.round(12*np.log2(f[mask]/440.0))+69).astype(int)%12
lo,hi=int(sys.argv[1]),int(sys.argv[2])
res=int(sys.argv[3]) if len(sys.argv)>3 else 1   # slices per beat
rows=[]
ts=[]
for b in range(lo*4*res,hi*4*res):
    t=t0+b*spb/res+spb/res/2
    a=int(t*sr)-N//2
    x=m[max(a,0):a+N]
    if len(x)<N: x=np.r_[x,np.zeros(N-len(x))]
    F=np.abs(np.fft.rfft(x*win))[mask]
    c=np.zeros(12); np.add.at(c,pc,F)
    rows.append(c/(np.linalg.norm(c)+1e-9)); ts.append(b/(4*res))
R=np.array(rows)
# distance: mean of next 2 beats vs mean of the previous 2 beats
w=2*res
d=np.zeros(len(R))
for i in range(w,len(R)-w):
    d[i]=1-np.dot(R[i-w:i].mean(0),R[i:i+w].mean(0))/(np.linalg.norm(R[i-w:i].mean(0))*np.linalg.norm(R[i:i+w].mean(0)))
cut=np.percentile(d,88)
pk=[i for i in range(1,len(d)-1) if d[i]>=d[i-1] and d[i]>=d[i+1] and d[i]>cut and d[i]==d[max(0,i-3*res):i+3*res+1].max()]
print("chord changes (bar, strength): "+"  ".join("%g(%.2f)"%(ts[i],d[i]) for i in pk))
# bar-beat fingerprint
for bar in range(lo,hi):
    s=[]
    for q in range(0,4):
        i=(bar-lo)*4*res+q*res
        c=R[i:i+res].mean(0)
        top=np.argsort(-c)[:3]
        s.append("/".join(NOTES[j] for j in top))
    print("%4d  %s"%(bar,"  ".join("%-9s"%x for x in s)))
