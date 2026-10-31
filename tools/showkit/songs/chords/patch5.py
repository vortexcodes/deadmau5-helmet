p="tools/showkit/work/chords/gen.py"
s=open(p).read()
def rep(a,b,count=1):
    global s
    assert a in s, a
    s=s.replace(a,b) if count==0 else s.replace(a,b,count)
rep('"gain": TURN(lo, hi, gain, 0.2)}','"gain": TURN(lo, hi, gain, 0.0)}')
rep('def blow(c, gain=0.36, pal="glass"):','def blow(c, gain=0.27, pal="glass"):')
rep('def beam(lo, hi, gain=0.3, speed=0.125):','def beam(lo, hi, gain=0.42, speed=0.125):')
open(p,"w").write(s)
