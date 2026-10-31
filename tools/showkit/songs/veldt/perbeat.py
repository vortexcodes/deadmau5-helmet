import numpy as np, subprocess
from numpy.fft import rfft, irfft, rfftfreq
mp3="shows/deadmau5 - The Veldt.mp3"; SR=22050
raw=subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-i",mp3,"-ac","2","-ar",str(SR),"-f","f32le","-"],capture_output=True,check=True).stdout
x=np.frombuffer(raw,dtype=np.float32).reshape(-1,2).copy()
m=x.mean(1); sd=(x[:,0]-x[:,1])/2
f=rfftfreq(len(m),1/SR); X=rfft(m); Xs=rfft(sd)
def band(X,a,b):
    Y=X.copy(); Y[(f<a)|(f>=b)]=0; return irfft(Y,len(m))
sub=band(X,30,100); low=band(X,120,350); mid=band(X,350,2000); pres=band(X,2000,5000); air=band(X,6000,11000)
sideh=band(Xs,500,800)
spb=0.468725; t0=0.0425
def rms(y,a,b):
    a=int(a*SR); b=int(b*SR)
    return np.sqrt(np.mean(y[a:b]**2)) if b>a else 0
def lev(v,lo,hi):
    return min(9,max(0,int((np.log10(max(v,1e-5))-lo)/(hi-lo)*9.99)))
print("bar: kick(sub first 100ms) per beat | hats offbeat (air, 8th) per beat | clap (air 0-60ms on 2,4) | mid per beat | E5 side")
for b in range(0,91):
    k=[];h=[];c=[];mm=[];lw=[];s=[]
    for q in range(4):
        T=t0+(b*4+q)*spb
        k.append(lev(rms(sub,T,T+0.1),-2,0.2))
        h.append(lev(rms(air,T+spb*0.45,T+spb*0.6),-3,-0.8))
        c.append(lev(rms(air,T-0.01,T+0.06),-3,-0.3))
        mm.append(lev(rms(mid,T+0.1,T+spb),-1.5,-0.1))
        lw.append(lev(rms(low,T+0.1,T+spb),-1.5,-0.1))
        s.append(lev(rms(sideh,T,T+spb),-2.2,-0.8))
    print("%3d %6.1f  k%s  h%s  c%s  m%s  l%s  s%s"%(b,t0+b*4*spb,"".join(map(str,k)),"".join(map(str,h)),"".join(map(str,c)),"".join(map(str,mm)),"".join(map(str,lw)),"".join(map(str,s))))
