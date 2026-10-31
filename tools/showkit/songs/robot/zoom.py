#!/usr/bin/env python3
# zoom.py out.png from_bar to_bar [flo fhi] : high-res log-frequency spectrogram with 16th grid
import sys, subprocess
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
out=sys.argv[1]; lo=float(sys.argv[2]); hi=float(sys.argv[3]); flo=float(sys.argv[4]) if len(sys.argv)>4 else 150; fhi=float(sys.argv[5]) if len(sys.argv)>5 else 6000
spb=0.468761; t0=0.003
ta=t0+lo*4*spb; tb=t0+hi*4*spb
mp3="shows/deadmau5 - Harder Better Faster Stronger.mp3"
SR=22050
raw=subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-ss",str(ta),"-t",str(tb-ta),"-i",mp3,"-ac","1","-ar",str(SR),"-f","f32le","-"],capture_output=True,check=True).stdout
m=np.frombuffer(raw,dtype=np.float32)
N,H=4096,128
win=np.hanning(N)
nf=(len(m)-N)//H
S=np.array([np.abs(np.fft.rfft(m[i*H:i*H+N]*win)) for i in range(0,nf)]).T
f=np.fft.rfftfreq(N,1/SR)
edges=np.geomspace(flo,fhi,220)
L=np.array([S[(f>=a)&(f<b)].mean(0) if ((f>=a)&(f<b)).any() else np.zeros(S.shape[1]) for a,b in zip(edges,edges[1:])])
L=np.log1p(L*0.5)
fig,ax=plt.subplots(1,1,figsize=(20,8))
ext=[lo,lo+(nf*H+N/2)/SR/(4*spb),np.log2(flo),np.log2(fhi)]
ax.imshow(L,origin="lower",aspect="auto",extent=ext,cmap="magma")
for b in np.arange(lo,hi+1e-6,0.25):
    ax.axvline(b,color="w",lw=(0.8 if abs(b-round(b))<1e-6 else 0.25),alpha=0.8 if abs(b-round(b))<1e-6 else 0.4)
    if abs(b-round(b))<1e-6: ax.text(b+0.01,np.log2(fhi)-0.15,str(int(b)),color="w",fontsize=10)
yt=[200,400,800,1600,3200]
ax.set_yticks(np.log2(yt)); ax.set_yticklabels(yt)
fig.tight_layout(); fig.savefig(out,dpi=70); print(out)
