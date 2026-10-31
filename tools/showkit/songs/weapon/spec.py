#!/usr/bin/env python3
# spec.py out.png t0 t1 [--grid "anchor:spb:every[,anchor:spb:every]"]  -- spectrogram over seconds, with grid lines
import sys, subprocess, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
out=sys.argv[1]; t0=float(sys.argv[2]); t1=float(sys.argv[3])
grids=[]
if len(sys.argv)>4:
    for g in sys.argv[4].split(","):
        a,s,e=g.split(":"); grids.append((float(a),float(s),int(e)))
mp3="shows/deadmau5 - Raise Your Weapon.mp3"
raw=subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-ss",str(t0),"-t",str(t1-t0),"-i",mp3,"-ac","1","-ar","22050","-f","f32le","-"],capture_output=True,check=True).stdout
m=np.frombuffer(raw,dtype=np.float32)
N,H=2048,256 if (t1-t0)<80 else 512
nf=max(1,(len(m)-N)//H)
step=max(1,nf//3200)
win=np.hanning(N)
S=np.array([np.abs(np.fft.rfft(m[i*H:i*H+N]*win)) for i in range(0,nf,step)]).T
f=np.fft.rfftfreq(N,1/22050)
edges=np.geomspace(30,11000,100)
L=np.array([S[(f>=a)&(f<b)].sum(0) if ((f>=a)&(f<b)).any() else np.zeros(S.shape[1]) for a,b in zip(edges,edges[1:])])
L=np.log1p(L*0.05)
fig,ax=plt.subplots(1,1,figsize=(20,6))
ax.imshow(L,origin="lower",aspect="auto",extent=[t0,t1,0,99],cmap="magma")
for a,s,e in grids:
    k0=int(np.ceil((t0-a)/s)); k1=int((t1-a)/s)
    for k in range(k0,k1+1):
        t=a+k*s
        if k%e==0:
            ax.axvline(t,color="w",lw=0.6,alpha=0.75)
            ax.text(t,95,str(k//4 if s<1 else k),color="w",fontsize=7)
ax.set_xlim(t0,t1)
fig.tight_layout(); fig.savefig(out,dpi=70); print(out)
