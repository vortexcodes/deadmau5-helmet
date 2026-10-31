import numpy as np, subprocess, sys
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
mp3="shows/deadmau5 - The Veldt.mp3"; SR=22050
raw=subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-i",mp3,"-ac","2","-ar",str(SR),"-f","f32le","-"],capture_output=True,check=True).stdout
x=np.frombuffer(raw,dtype=np.float32).reshape(-1,2).copy()
mid=(x[:,0]+x[:,1])/2; side=(x[:,0]-x[:,1])/2
spb=0.468725; t0=0.0425; bar=4*spb
N=4096;H=512;win=np.hanning(N)
def stft(y,a,b):
    a=int(a*SR); b=int(b*SR); y=y[a:b]
    n=(len(y)-N)//H
    return np.array([np.abs(np.fft.rfft(y[i*H:i*H+N]*win)) for i in range(n)]).T
f=np.fft.rfftfreq(N,1/SR)
lo,hi=int(sys.argv[2]),int(sys.argv[3])
a=t0+lo*bar;b=t0+hi*bar
Sm=stft(mid,a,b);Ss=stft(side,a,b)
sel=(f>=200)&(f<3500)
# log-frequency y by index mapping
fr=np.geomspace(200,3500,260)
idx=np.searchsorted(f,fr)
Lm=np.log1p(Sm[idx]*0.5); Ls=np.log1p(Ss[idx]*0.5)
fig,ax=plt.subplots(2,1,figsize=(19,9),sharex=True)
for A,L,nm in ((ax[0],Lm,"mid (L+R)"),(ax[1],Ls,"side (L-R)")):
    A.imshow(L,origin="lower",aspect="auto",extent=[lo,hi,0,260],cmap="magma")
    for bb in range(lo,hi):
        A.axvline(bb,color="w",lw=0.3 if bb%4 else 0.8,alpha=0.6)
    A.set_ylabel(nm)
    A.set_xticks(range(lo,hi))
fig.tight_layout();fig.savefig(sys.argv[1],dpi=75);print(sys.argv[1])
