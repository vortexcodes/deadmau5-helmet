import sys, os, subprocess
sys.path.insert(0, os.getcwd()); sys.path.insert(0, os.environ["KIT"])
import numpy as np
raw = subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-i","shows/deadmau5 - FN Pig.mp3","-ac","1","-ar","22050","-f","f32le","-"],capture_output=True,check=True).stdout
m=np.frombuffer(raw,dtype=np.float32)
sr=22050
np.save(os.environ["KIT"]+"/work/fnpig/mono.npy",m)
# band envelope by short FFT with small hop
N=2048;H=110
win=np.hanning(N)
f=np.fft.rfftfreq(N,1/sr)
def env(t0,t1,lo,hi):
    a=int(t0*sr);b=int(t1*sr)
    x=m[a:b]
    n=(len(x)-N)//H
    out=np.zeros(n)
    mask=(f>=lo)&(f<hi)
    for s in range(0,n,2000):
        e=min(n,s+2000)
        fr=np.stack([x[i*H:i*H+N] for i in range(s,e)])*win
        out[s:e]=np.abs(np.fft.rfft(fr,axis=1))[:,mask].sum(1)
    return t0+(np.arange(n)*H+N/2)/sr,out
tt,e=env(0,110,40,400)
e=np.log1p(e)
sm=np.convolve(e,np.ones(15)/15,"same")
w=int(0.12*sr/H)
pk=[i for i in range(w,len(sm)-w) if sm[i]==sm[i-w:i+w].max() and sm[i]>sm[i-w:i+w].mean()+0.15]
T=tt[pk]
prev=None
print("t, gap, beats since 0.49")
line=[]
for a,b in zip(T,np.diff(T)):
    line.append("%.2f(%.2f)"%(a,b))
for i in range(0,len(line),12):
    print(" ".join(line[i:i+12]))
