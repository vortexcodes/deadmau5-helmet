p="tools/showkit/work/chords/gen.py"
s=open(p).read()
s=s.replace('def clo(ch): return round((3 * ch) / 11.0, 5)','def clo(ch): return round((3 * ch + 0.45) / 11.0, 5)')
# one blades layer for the arpeggio and the clap
s=s.replace('''def chirp(lo, hi, gain=0.6, tip=None):''','''def organ(lo, hi, gain=0.55):
    """The triad in order on the 8ths; on the clap all three tubes at once."""
    seq = [("012" if i in (2, 12) else ["0", "1", "2", "1"][i % 4]) for i in range(16)]
    return {"fx": "blades", "seq": seq, "step": 0.5, "rise": 0.3, "keep": 0.3, "c": K(lo, hi, cmain), "ctip": K(lo, hi, chi), "gain": gain}
def beam(lo, hi, gain=0.3, speed=0.125):
    """A bar of light sliding across behind the glass."""
    return {"fx": "sweep", "on": "face", "axis": "x", "shape": "tri", "mode": "band", "speed": speed, "from": 0.1, "to": 0.9, "width": 0.16, "c": K(lo, hi, chi), "gain": gain}
def chirp(lo, hi, gain=0.6, tip=None):''')
s=s.replace('flood(52, 68, [clap(52, 68), arp(52, 68, 0.3)])','flood(52, 68, [organ(52, 68), beam(52, 68)])')
s=s.replace('flood(68, 84, [clap(68, 84), stain("chords_ruby1", EE, 68, 84, 0.3), hats()])','flood(68, 84, [organ(68, 84), stain("chords_ruby1", EE, 68, 84, 0.3), hats()])')
s=s.replace('flood(196, 212, [clap(196, 212), arp(196, 212, 0.3)])','flood(196, 212, [organ(196, 212), beam(196, 212)])')
s=s.replace('lead(m), clap(a, b, 0.45)], pump=PUMP)','lead(m), organ(a, b, 0.42)], pump=PUMP)')
s=s.replace('def flood(a, b, extra, gate_floor=0.6, g=0.3, pump=PUMP):','def flood(a, b, extra, gate_floor=0.5, g=0.3, pump=PUMP):')
s=s.replace('PUMP = {"pat": BASS, "step": 0.25, "depth": 0.22, "decay": 0.6}','PUMP = {"pat": BASS, "step": 0.25, "depth": 0.3, "decay": 0.6}')
s=s.replace('{"pat": BASS, "step": 0.25, "decay": 0.75, "floor": 0.6}','{"pat": BASS, "step": 0.25, "decay": 0.75, "floor": 0.5}')
s=s.replace('flood(100, 116, [arp(100, 116, 0.45, step=0.25),','flood(100, 116, [arp(100, 116, 0.5, step=0.25),')
open(p,"w").write(s)
