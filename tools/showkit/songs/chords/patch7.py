p="tools/showkit/work/chords/gen.py"
s=open(p).read()
def rep(a,b,count=1):
    global s
    assert a in s, a
    s=s.replace(a,b) if count==0 else s.replace(a,b,count)
rep('return {"fx": "orb", "on": "face", "x": xs, "y": ys, "rad": rad, "soft": 40, "c": K(lo, hi, cmain), "cgrad": 0.0, "gain": gain}',
    'return {"fx": "orb", "on": "face", "x": xs, "y": ys, "rad": rad, "soft": 40, "c": K(lo, hi, chi), "cgrad": -0.0909, "gain": gain}')
rep('def hats(gain=0.35):','def hats(gain=0.8):')
rep('"rate": 0.5, "sharp": 2, "dens": 0.5, "seed": 3,','"rate": 0.5, "sharp": 2, "dens": 0.4, "seed": 3,')
rep('[bass(32, 40, 0.42, pat=BEAT, floor=0.25), glass(32, 40, 0.24)]','[bass(32, 40, 0.6, pat=BEAT, floor=0.15), glass(32, 40, 0.24)]')
rep('[bass(40, 48, 0.45, pat=BEAT, floor=0.25), glass(40, 48, 0.26)]','[bass(40, 48, 0.65, pat=BEAT, floor=0.15), glass(40, 48, 0.25)]')
rep('[bass(148, 160, 0.45, pat=BEAT, floor=0.25), glass(148, 160, 0.24),','[bass(148, 160, 0.65, pat=BEAT, floor=0.15), glass(148, 160, 0.22),')
rep('''H("SOME CHORDS", "cut", 22,''','''H("WHOLE", 32, 2, [ring(chi(GM), 0.5)])
H("BEAT", 148, 2, [ring(chi(GM), 0.5)])
H("SOME CHORDS", "cut", 22,''')
open(p,"w").write(s)
