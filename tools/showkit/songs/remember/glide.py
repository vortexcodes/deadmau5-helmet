# Voice finder: a sung line glides and wobbles off the semitone grid, a synth does not.
# For each 8th, the share of the 350-1800 Hz energy (centre channel) that sits more than 28 cents off the song's tuning,
# then a zoom picture with a pitch axis so glides can be seen.
import subprocess, sys, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
mp3="shows/Kaskade feat. deadmau5 - I Remember.mp3"
SR=22050
raw=subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-i",mp3,"-ac","2","-ar",str(SR),"-f","f32le","-"],capture_output=True,check=True).stdout
st=np.frombuffer(raw,dtype=np.float32).reshape(-1,2)
M=(st[:,0]+st[:,1])*0.5
t0=1.590; spb=0.46875
N=6144
win=np.hanning(N)
f=np.fft.rfftfreq(N,1/SR)
keep=(f>=350)&(f<1800)
midi=69+12*np.log2(f[keep]/440.0)
H=256
times=[];rows=[]
for i in range(0,len(M)-N,H*4):
    S=np.abs(np.fft.rfft(M[i:i+N]*win))[keep]**2
    rows.append(S); times.append((i+N/2)/SR)
A=np.array(rows); T=np.array(times)
# tuning: energy-weighted circular mean of the cents
cents=(midi-np.round(midi))
ang=np.exp(2j*np.pi*(midi%1))
tune=np.angle((A.sum(0)*ang).sum())/(2*np.pi)
print("tuning offset (semitones)",round(tune,3))
dev=np.abs(((midi-tune+0.5)%1)-0.5)  # 0..0.5
off=(dev>0.28)
share=A[:,off].sum(1)/np.maximum(A.sum(1),1e-9)
loud=A.sum(1)
# per beat
bars=[];vals=[]
nb=int((T[-1]-t0)/spb)
out=[]
for b in range(nb):
    a=t0+b*spb; c=a+spb
    m=(T>=a)&(T<c)
    out.append(share[m].mean() if m.any() else 0)
out=np.array(out)
med=np.median(out)
print("median",med)
line=""
for bar in range(nb//4):
    v=out[bar*4:bar*4+4]
    print("%3d %5.1fs  "%(bar,t0+bar*4*spb)+" ".join("%4.2f"%x for x in v)+"  "+"#"*int(v.mean()*60))
