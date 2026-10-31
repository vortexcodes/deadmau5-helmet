# Where is the voice: a mid-minus-side harmonic spectrogram with bar lines, 200 Hz - 4 kHz.
import subprocess, sys, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
def median_filter(A,size):
    k=size[1]
    P=np.pad(A,((0,0),(k//2,k//2)),mode='edge')
    V=np.lib.stride_tricks.sliding_window_view(P,k,axis=1)
    return np.median(V,axis=2)
mp3="shows/Kaskade feat. deadmau5 - I Remember.mp3"
SR=22050
raw=subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-i",mp3,"-ac","2","-ar",str(SR),"-f","f32le","-"],capture_output=True,check=True).stdout
st=np.frombuffer(raw,dtype=np.float32).reshape(-1,2)
t0=1.590; spb=0.46875
lo,hi=int(sys.argv[1]),int(sys.argv[2]); out=sys.argv[3]
a=t0+lo*4*spb; b=t0+hi*4*spb
seg=st[int(max(a,0)*SR):int(b*SR)]
M=(seg[:,0]+seg[:,1])*0.5; S=(seg[:,0]-seg[:,1])*0.5
N=2048;H=256
win=np.hanning(N)
nf=(len(M)-N)//H
SM=np.abs(np.array([np.fft.rfft(M[i*H:i*H+N]*win) for i in range(nf)])).T
SS=np.abs(np.array([np.fft.rfft(S[i*H:i*H+N]*win) for i in range(nf)])).T
f=np.fft.rfftfreq(N,1/SR)
# harmonic part: median across time (removes the kick and hats)
HM=median_filter(SM,size=(1,17))
C=np.maximum(0,HM-1.2*median_filter(SS,size=(1,17)))
keep=(f>=150)&(f<=4500)
edges=np.geomspace(150,4500,150)
L=np.array([C[(f>=x)&(f<y)].mean(0) if ((f>=x)&(f<y)).any() else np.zeros(C.shape[1]) for x,y in zip(edges,edges[1:])])
L=np.log1p(L*0.3)
fig,ax=plt.subplots(figsize=(19,6))
ax.imshow(L,origin="lower",aspect="auto",extent=[a,b,0,149],cmap="magma")
for bar in range(lo,hi):
    tt=t0+bar*4*spb
    ax.axvline(tt,color="w",lw=0.7,alpha=0.75)
    ax.text(tt,144,str(bar),color="w",fontsize=8)
    for k in (1,2,3):
        ax.axvline(tt+k*spb,color="w",lw=0.2,alpha=0.3)
fig.tight_layout(); fig.savefig(out,dpi=78); print(out)
