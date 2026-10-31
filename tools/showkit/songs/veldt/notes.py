import numpy as np, subprocess
mp3="shows/deadmau5 - The Veldt.mp3"; SR=22050
raw=subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-i",mp3,"-ac","1","-ar",str(SR),"-f","f32le","-"],capture_output=True,check=True).stdout
m=np.frombuffer(raw,dtype=np.float32).copy()
spb=0.468725; t0=0.0425
NOTES="C C# D D# E F F# G G# A A# B".split()
N=8192
win=np.hanning(N)
f=np.fft.rfftfreq(N,1/SR)
def spec(t):
    c=int(t*SR); a=c-N//2
    x=m[max(a,0):a+N]
    if len(x)<N: x=np.pad(x,(N-len(x),0))
    return np.abs(np.fft.rfft(x*win))
def midi(fr): return 69+12*np.log2(fr/440)
mm=np.where(f>20,midi(np.maximum(f,1)),-1)
rows=[]
print("per bar, 8 half-beats. low note (50-180 Hz, measured just after each 8th so kick matters less), then upper chroma top-2 400-2000")
for bar in range(0,88):
    lows=[];tops=[]
    for q in range(4):
        # between kicks: the 3/4 of a beat is the off-beat tail, kick has decayed
        t=t0+(bar*4+q+0.6)*spb
        S=spec(t)
        sel=(f>=45)&(f<180)
        k=np.argmax(S*sel)
        lows.append(NOTES[int(round(mm[k]))%12]+str(int(round(mm[k]))//12-1))
        sel2=(f>=300)&(f<2000)
        ch=np.zeros(12)
        np.add.at(ch,np.round(mm[sel2]).astype(int)%12,S[sel2]**2)
        o=np.argsort(-ch)[:2]
        tops.append(NOTES[o[0]]+"/"+NOTES[o[1]])
    print("%3d %6.1f  "%(bar,t0+bar*4*spb)+" ".join("%-4s"%x for x in lows)+"   "+" ".join("%-6s"%x for x in tops))
