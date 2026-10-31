# The ramp's own test: the vocal at bars 112-127 repeats the vocal at bars 32-47. Warp bars 32-47 onto the new grid and measure what is left.
import sys, numpy as np, os, subprocess
BASE="deadmau5 - Raise Your Weapon"
beats=np.loadtxt("shows/scenes/%s.beats"%BASE)
raw=subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-i","shows/%s.mp3"%BASE,"-ac","1","-ar","11025","-f","f32le","-"],capture_output=True,check=True).stdout
m=np.frombuffer(raw,dtype=np.float32); SR=11025; N=1024; H=64; dt=H/SR
def stft(a,b):
    x=m[int(a*SR):int(b*SR)]; n=(len(x)-N)//H; win=np.hanning(N)
    F=np.abs(np.fft.rfft(np.stack([x[i*H:i*H+N]*win for i in range(n)]),axis=1))
    f=np.fft.rfftfreq(N,1/SR); e=np.geomspace(100,5000,48)
    return np.log1p(np.stack([F[:,(f>=p)&(f<q)].sum(1) for p,q in zip(e,e[1:])],1)*0.1)
for b in range(0,62,4):
    # beat b of the phrase: first vocal at beats[128+b], second at beats[448+b]
    a0=beats[128+b]; a1=beats[128+b+4]; c0=beats[448+b]
    A=stft(a0,a1); Am=A-A.mean(0)
    B=stft(c0-0.2,c0+(a1-a0)+0.2)
    res=[]
    for s in range(0,len(B)-len(A),1):
        C=B[s:s+len(A)]; Cm=C-C.mean(0)
        res.append(((Am*Cm).sum()/np.sqrt((Am*Am).sum()*(Cm*Cm).sum()+1e-9),-0.2+s*dt))
    res.sort(reverse=True)
    print("phrase beat %2d (t=%.2f): residual %+.0f ms corr %.2f"%(b,c0,1000*res[0][1],res[0][0]))
