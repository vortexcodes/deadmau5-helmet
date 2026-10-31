import numpy as np, subprocess
mp3="/Users/jones/deadmau5 app/shows/deadmau5 - Moar Ghosts n Stuff.mp3"
raw=subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-i",mp3,"-ac","1","-ar","22050","-f","f32le","-"],capture_output=True,check=True).stdout
m=np.frombuffer(raw,dtype=np.float32); SR=22050
spb=0.468770; t0=0.045
def bandE(lo,hi,N=512,H=128):
    f=np.fft.rfftfreq(N,1/SR); mask=(f>=lo)&(f<hi); win=np.hanning(N)
    nf=(len(m)-N)//H; out=np.zeros(nf)
    for s in range(0,nf,4000):
        e=min(s+4000,nf)
        fr=np.stack([m[i*H:i*H+N] for i in range(s,e)])*win
        out[s:e]=(np.abs(np.fft.rfft(fr,axis=1))[:,mask]**2).sum(1)
    return out,(np.arange(nf)*H+N/2)/SR
for lo,hi,nm in ((40,120,"sub"),(1500,4000,"pres"),(5000,11000,"air")):
    e,tt=bandE(lo,hi)
    for a,b in ((26,40),(42,74),(76,92),(114,128),(130,143)):
        fold=np.zeros(32)
        for bar in range(a,b):
            for k in range(32):
                t=t0+(bar+k/32)*4*spb; t2=t+4*spb/32
                i,j=np.searchsorted(tt,[t,t2]); fold[k]+=e[i:j].mean()
        fold/=fold.max()
        print("%-5s %3d-%3d "%(nm,a,b)+"|".join("".join(" .:-=+*#%@"[min(9,int(v*9.99))] for v in fold[i:i+8]) for i in range(0,32,8)))
