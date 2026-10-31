# Bars 112-127 sing what bars 32-47 sang, accelerated. Stretch each 4 beats of the first singing onto the same 4 beats of the second and measure the lag that remains.
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
out=[]
for b in range(0,60,4):
    a0,a1=beats[128+b],beats[128+b+4]; c0,c1=beats[448+b],beats[448+b+4]
    A=stft(a0,a1)
    B=stft(c0-0.1,c1+0.1)
    nA=int((c1-c0-N/SR)/dt)
    idx=np.linspace(0,len(A)-1,nA)
    A2=np.stack([np.interp(idx,np.arange(len(A)),A[:,k]) for k in range(A.shape[1])],1); A2m=A2-A2.mean(0)
    res=[]
    for s in range(0,len(B)-len(A2)):
        C=B[s:s+len(A2)]; Cm=C-C.mean(0)
        res.append(((A2m*Cm).sum()/np.sqrt((A2m*A2m).sum()*(Cm*Cm).sum()+1e-9),-0.1+s*dt))
    res.sort(reverse=True)
    out.append((b,res[0][1]*1000,res[0][0]))
    print("phrase beat %2d t=%.2f: left over %+.0f ms, corr %.2f"%(b,c0,res[0][1]*1000,res[0][0]))
g=[o for o in out if o[2]>0.75]
print("where corr>0.75: mean %+.1f ms, worst %.0f ms, %d windows"%(np.mean([o[1] for o in g]),max(abs(o[1]) for o in g),len(g)))
