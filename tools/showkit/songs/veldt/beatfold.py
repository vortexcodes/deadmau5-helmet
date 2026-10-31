import sys, numpy as np, subprocess
# Beat-resolved energy per band for a span: one row per bar, one cell per 16th: see where the kick and claps fall and when things start.
mp3="shows/deadmau5 - The Veldt.mp3"; SR=22050
raw=subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-i",mp3,"-ac","1","-ar",str(SR),"-f","f32le","-"],capture_output=True,check=True).stdout
m=np.frombuffer(raw,dtype=np.float32).copy()
N,H=1024,128
win=np.hanning(N)
nf=(len(m)-N)//H
F=np.fft.rfftfreq(N,1/SR)
bands={"sub":(30,110),"low":(110,300),"mid":(300,2000),"pres":(2000,6000),"air":(6000,11000)}
E={k:np.zeros(nf) for k in bands}
for s in range(0,nf,4000):
    e=min(s+4000,nf)
    fr=np.stack([m[i*H:i*H+N] for i in range(s,e)])*win
    A=np.abs(np.fft.rfft(fr,axis=1))**2
    for k,(a,b) in bands.items():
        E[k][s:e]=A[:,(F>=a)&(F<b)].sum(1)
tt=(np.arange(nf)*H+N/2)/SR
np.savez(sys.argv[1],tt=tt,**E)
