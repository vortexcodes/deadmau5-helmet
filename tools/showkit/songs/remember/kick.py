import subprocess, numpy as np
mp3="shows/Kaskade feat. deadmau5 - I Remember.mp3"
SR=22050
raw=subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-i",mp3,"-ac","1","-ar",str(SR),"-f","f32le","-"],capture_output=True,check=True).stdout
m=np.frombuffer(raw,dtype=np.float32)
t0=1.590; spb=0.46875
N=1024;H=128
win=np.hanning(N)
nf=(len(m)-N)//H
f=np.fft.rfftfreq(N,1/SR)
ml=(f>=30)&(f<110); mh=(f>=5000)&(f<11000); mm=(f>=300)&(f<2500)
E=np.zeros((nf,3))
for s in range(0,nf,5000):
    e=min(nf,s+5000)
    F=np.abs(np.fft.rfft(np.stack([m[i*H:i*H+N] for i in range(s,e)])*win,axis=1))
    E[s:e,0]=F[:,ml].sum(1);E[s:e,1]=F[:,mm].sum(1);E[s:e,2]=F[:,mh].sum(1)
tt=(np.arange(nf)*H+N/2)/SR
def at(t,w=0.03,col=0):
    a=np.searchsorted(tt,t);b=np.searchsorted(tt,t+w)
    return E[a:b,col].mean() if b>a else 0
print("bar: per beat, kick = low energy right after the beat over low energy just before; digit is (ratio-1)*3 capped 9; '.' no kick")
print("     then high-hat row on offbeats, then mid level")
for bar in range(0,147):
    s="";h="";
    for k in range(4):
        t=t0+(bar*4+k)*spb
        a=at(t+0.01,0.05);b=at(t-0.06,0.05)
        r=a/max(b,1e-3)
        s+= "." if r<1.25 else str(min(9,int((r-1)*3)))
        hh=at(t+spb/2,0.05,2)/(at(t+spb/2-0.08,0.05,2)+1e-3)
        h+= "." if hh<1.3 else "o"
    print("%3d %6.1f  %s  %s  low %5.0f mid %5.0f high %5.1f"%(bar,t0+bar*4*spb,s,h,E[np.searchsorted(tt,t0+bar*4*spb):np.searchsorted(tt,t0+(bar+1)*4*spb),0].mean(),E[np.searchsorted(tt,t0+bar*4*spb):np.searchsorted(tt,t0+(bar+1)*4*spb),1].mean(),E[np.searchsorted(tt,t0+bar*4*spb):np.searchsorted(tt,t0+(bar+1)*4*spb),2].mean()))
