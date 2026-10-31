import sys, numpy as np, os, subprocess
mp3="shows/deadmau5 - Raise Your Weapon.mp3"
raw=subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-i",mp3,"-ac","1","-ar","11025","-f","f32le","-"],capture_output=True,check=True).stdout
m=np.frombuffer(raw,dtype=np.float32)
SR=11025; N=1024; H=64
def stft(a,b):
    x=m[int(a*SR):int(b*SR)]
    n=(len(x)-N)//H
    win=np.hanning(N)
    F=np.abs(np.fft.rfft(np.stack([x[i*H:i*H+N]*win for i in range(n)]),axis=1))
    # 40 log bands
    f=np.fft.rfftfreq(N,1/SR)
    edges=np.geomspace(100,5000,48)
    L=np.stack([F[:,(f>=p)&(f<q)].sum(1) for p,q in zip(edges,edges[1:])],1)
    return np.log1p(L*0.1)
dt=H/SR
print("dt",dt)
for a in np.arange(58,90,2.0):
    A=stft(a,a+3)
    Am=A-A.mean(0)
    best=None
    B=stft(a+145,a+3+155)
    res=[]
    for s in range(0,len(B)-len(A),2):
        C=B[s:s+len(A)]; Cm=C-C.mean(0)
        r=(Am*Cm).sum()/np.sqrt((Am*Am).sum()*(Cm*Cm).sum()+1e-9)
        res.append((r,145+s*dt))
    res.sort(reverse=True)
    print("t=%5.1f  best lag %.3f (corr %.2f)   next %.3f (%.2f)"%(a,res[0][1],res[0][0],res[5][1],res[5][0]))
