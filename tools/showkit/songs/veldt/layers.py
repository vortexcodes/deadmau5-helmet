import numpy as np, subprocess, sys
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
mp3="shows/deadmau5 - The Veldt.mp3"; SR=22050
raw=subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-i",mp3,"-ac","2","-ar",str(SR),"-f","f32le","-"],capture_output=True,check=True).stdout
x=np.frombuffer(raw,dtype=np.float32).reshape(-1,2).copy()
mid=(x[:,0]+x[:,1])/2; side=(x[:,0]-x[:,1])/2
spb=0.468725; t0=0.0425
N=2048;H=256;win=np.hanning(N)
f=np.fft.rfftfreq(N,1/SR)
edges=np.geomspace(40,11000,41)
def bs(y,ts):
    out=[]
    for t in ts:
        a=int(t*SR)
        s=y[a:a+N]
        if len(s)<N: s=np.pad(s,(0,N-len(s)))
        A=np.abs(np.fft.rfft(s*win))**2
        out.append([A[(f>=edges[i])&(f<edges[i+1])].sum() for i in range(40)])
    return np.array(out)
# beat-synchronous: the eighth-note offbeats only (kick and clap have decayed by 0.5 beat... sample 0.35 to 0.95 of each beat)
nb=int((len(mid)/SR-t0)/spb)
M=np.zeros((40,nb));S=np.zeros((40,nb))
for b in range(nb):
    ts=t0+(b+np.linspace(0.3,0.9,6))*spb
    M[:,b]=bs(mid,ts).mean(0); S[:,b]=bs(side,ts).mean(0)
np.savez(sys.argv[1]+".npz",M=M,S=S,edges=edges)
fig,ax=plt.subplots(2,1,figsize=(19,8),sharex=True)
for A,L,nm in ((ax[0],M,"mid"),(ax[1],S,"side")):
    A.imshow(np.log1p(L*0.5),origin="lower",aspect="auto",extent=[0,nb/4,0,40],cmap="magma",interpolation="nearest")
    for bb in range(0,int(nb/4)+1,8):
        A.axvline(bb,color="w",lw=0.8)
    for bb in range(0,int(nb/4)+1,1):
        A.axvline(bb,color="w",lw=0.2,alpha=0.4)
    A.set_xticks(range(0,int(nb/4)+1,4)); A.set_ylabel(nm+" 40-11k")
fig.tight_layout();fig.savefig(sys.argv[1],dpi=75);print(sys.argv[1])
