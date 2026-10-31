import numpy as np, subprocess
mp3="shows/deadmau5 - The Veldt.mp3"; SR=22050
raw=subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-i",mp3,"-ac","1","-ar",str(SR),"-f","f32le","-"],capture_output=True,check=True).stdout
m=np.frombuffer(raw,dtype=np.float32).copy()
spb=0.468725; t0=0.0425
NOTES="C C# D D# E F F# G G# A A# B".split()
N=4096; win=np.hanning(N); f=np.fft.rfftfreq(N,1/SR)
def midi(fr): return 69+12*np.log2(fr/440)
mm=np.where(f>20,midi(np.maximum(f,1)),-1)
def spec(t):
    a=int(t*SR)-N//2
    x=m[max(a,0):a+N]
    if len(x)<N: x=np.pad(x,(N-len(x),0))
    return np.abs(np.fft.rfft(x*win))
for bar in list(range(0,8)):
    row=[]
    for k in range(16):
        t=t0+(bar+ (k+0.5)/16)*4*spb
        S=spec(t)
        # chroma over 100-1000 Hz
        sel=(f>=60)&(f<500)
        ch=np.zeros(12); np.add.at(ch,np.round(mm[sel]).astype(int)%12,S[sel]**2)
        o=np.argsort(-ch)[:1]
        row.append("%-2s"%NOTES[o[0]])
    print("%2d "%bar+" ".join(row[:4])+" | "+" ".join(row[4:8])+" | "+" ".join(row[8:12])+" | "+" ".join(row[12:16]))
