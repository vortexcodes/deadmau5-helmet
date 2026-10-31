import numpy as np, subprocess
# where do the kick transients really fall against the candidate grid, across the song? 800 Hz-11 kHz click of the kick is on beats 1,3 of a bar (the clap covers 2,4)
mp3="shows/deadmau5 - The Veldt.mp3"; SR=22050
raw=subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-i",mp3,"-ac","1","-ar",str(SR),"-f","f32le","-"],capture_output=True,check=True).stdout
m=np.frombuffer(raw,dtype=np.float32).copy()
from numpy.fft import rfft, irfft, rfftfreq
X=rfft(m); f=rfftfreq(len(m),1/SR); X[(f<30)|(f>=110)]=0; y=irfft(X,len(m))
X2=rfft(m); X2[(f<2000)|(f>=5000)]=0; y2=irfft(X2,len(m))
for spb in (0.468725,0.46875):
  for yy,name in ((y,"sub"),(y2,"pres")):
    out=[]
    for lo in list(range(8,64,8))+[72,80]:
        acc=np.zeros(60)
        for bar in range(lo,lo+8):
            for q in (0,2):
                T=0.040275+(bar*4+q)*spb
                for j in range(60):
                    s=int((T-0.04+j*0.002)*SR)
                    acc[j]+=np.sqrt(np.mean(yy[s:s+int(0.002*SR)+1]**2))
        pk=acc.max(); i=np.argmax(acc>0.5*pk)
        out.append("%d:%+d"%(lo,i*2-40))
    print("spb",spb,name,"half-rise ms by span (kick beats):"," ".join(out))
