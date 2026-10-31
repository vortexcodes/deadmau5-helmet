import numpy as np, subprocess
mp3="shows/deadmau5 - The Veldt.mp3"; SR=22050
raw=subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-i",mp3,"-ac","1","-ar",str(SR),"-f","f32le","-"],capture_output=True,check=True).stdout
m=np.frombuffer(raw,dtype=np.float32).copy()
spb=0.468725
# high-pass by differencing a few times + band-limited RMS in 2 ms steps around each beat, averaged over a span, per beat position on the 0.0403 grid
from numpy.fft import rfft, irfft, rfftfreq
def band(x,a,b):
    X=rfft(x); f=rfftfreq(len(x),1/SR); X[(f<a)|(f>=b)]=0; return irfft(X,len(x))
for name,(a,b) in {"sub 30-110":(30,110),"pres 2-5k":(2000,5000),"air 5-11k":(5000,11000)}.items():
    y=band(m,a,b)
    print(name)
    for lo,hi in ((16,24),(32,40),(72,80)):
        P=[]
        for q in range(4):
            acc=np.zeros(70)
            for bar in range(lo,hi):
                T=0.040275+(bar*4+q)*spb
                for j in range(70):
                    s=int((T-0.04+j*0.004)*SR)
                    acc[j]+=np.sqrt(np.mean(y[s:s+int(0.004*SR)]**2))
            P.append(acc/(hi-lo))
        P=np.array(P)
        print(" bars",lo,hi,"peak per beat position (rms) and time of the rise in ms from the beat:")
        for q in range(4):
            pk=P[q].max(); i=np.argmax(P[q]>0.5*pk)
            print("   beat %d (t=%.3f on bar line grid): peak %.3f at %+d ms; half-rise at %+d ms; before-beat level %.3f"%(q,0.040275+q*spb,pk,int(P[q].argmax()*4-40),int(i*4-40),P[q][:5].mean()))
