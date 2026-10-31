import subprocess, sys, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
mp3="shows/Kaskade feat. deadmau5 - I Remember.mp3"
SR=22050
raw=subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-i",mp3,"-ac","2","-ar",str(SR),"-f","f32le","-"],capture_output=True,check=True).stdout
st=np.frombuffer(raw,dtype=np.float32).reshape(-1,2)
M=(st[:,0]+st[:,1])*0.5
t0=1.590; spb=0.46875
lo,hi,out=int(sys.argv[1]),int(sys.argv[2]),sys.argv[3]
a=t0+lo*4*spb;b=t0+hi*4*spb
seg=M[int(max(a,0)*SR):int(b*SR)]
N=4096;H=220
win=np.hanning(N)
nf=(len(seg)-N)//H
S=np.abs(np.array([np.fft.rfft(seg[i*H:i*H+N]*win) for i in range(nf)])).T
f=np.fft.rfftfreq(N,1/SR)
Y=np.arange(52,90,0.25)
fr=440*2**((Y-69)/12)
idx=np.interp(fr,f,np.arange(len(f)))
i0=np.floor(idx).astype(int);w=idx-i0
L=S[i0]*(1-w)[:,None]+S[i0+1]*w[:,None]
L=np.log1p(L*0.25)
# local contrast by note row: emphasise what moves
fig,ax=plt.subplots(figsize=(19,6.4))
ax.imshow(L,origin="lower",aspect="auto",extent=[a,b,52,90],cmap="magma",vmax=np.percentile(L,99.7))
NOTES="C C# D D# E F F# G G# A A# B".split()
for m in range(52,90):
    if m%12 in (11,2,6,9):
        ax.axhline(m,color="c",lw=0.2,alpha=0.35)
        ax.text(a,m,NOTES[m%12]+str(m//12-1),color="c",fontsize=7)
for bar in range(lo,hi):
    tt=t0+bar*4*spb
    ax.axvline(tt,color="w",lw=0.7,alpha=0.75)
    ax.text(tt,88.5,str(bar),color="w",fontsize=9)
    for k in (1,2,3):
        ax.axvline(tt+k*spb,color="w",lw=0.2,alpha=0.25)
fig.tight_layout(); fig.savefig(out,dpi=78); print(out)
