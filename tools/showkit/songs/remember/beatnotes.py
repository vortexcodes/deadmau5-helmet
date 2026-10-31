import subprocess, sys, numpy as np
mp3="shows/Kaskade feat. deadmau5 - I Remember.mp3"
SR=22050
raw=subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-i",mp3,"-ac","1","-ar",str(SR),"-f","f32le","-"],capture_output=True,check=True).stdout
m=np.frombuffer(raw,dtype=np.float32)
t0=1.590; spb=0.46875
N=8192
f=np.fft.rfftfreq(N,1/SR)
win=np.hanning(N)
NOTES="C C# D D# E F F# G G# A A# B".split()
def midi(fr): return 69+12*np.log2(fr/440.0)
def spec(t):
    i=int(t*SR); seg=m[max(0,i-N//2):i+N//2]
    if len(seg)<N: seg=np.pad(seg,(0,N-len(seg)))
    return np.abs(np.fft.rfft(seg*win))
def top(S,lo,hi,k=1):
    mask=(f>=lo)&(f<hi)
    F=f[mask]; A=S[mask]
    pc=np.zeros(128)
    for fr,a in zip(F,A):
        if fr>0:
            pc[int(round(midi(fr)))]+=a**2
    idx=np.argsort(-pc)[:k]
    return " ".join("%s%d"%(NOTES[j%12],j//12-1) for j in idx)
lo=int(sys.argv[1]);hi=int(sys.argv[2])
print("bar.beat  time  bass(40-160)  mid-top(200-1000) high(1000-3000) rmsDb")
for b in range(lo*4,hi*4):
    # sample mid-beat so the kick transient does not dominate
    t=t0+(b+0.5)*spb
    S=spec(t)
    i=int(t*SR); rms=np.sqrt(np.mean(m[max(0,i-2000):i+2000]**2))+1e-9
    print("%3d.%d %7.2f  %-6s  %-22s %-14s %5.0f"%(b//4,b%4+1,t0+b*spb,top(S,40,160),top(S,200,1000,3),top(S,1000,3000,2),20*np.log10(rms)))
