p="tools/showkit/work/chords/gen.py"
s=open(p).read()
# the jaw is the bass: it has to stand out from the dome on the kick
s=s.replace('S("%d" % a, a, b, [dome, bass(a, b, 0.5), lead()] + extra, pump=pump)','S("%d" % a, a, b, [dome, bass(a, b, 0.75, floor=0.12), lead()] + extra, pump=pump)')
s=s.replace('def flood(a, b, extra, gate_floor=0.5, g=0.3, pump=PUMP):','def flood(a, b, extra, gate_floor=0.5, g=0.24, pump=PUMP):')
s=s.replace('S(name, a, b, [glass(a, b, 0.3, gate={"pat": BASS, "step": 0.25, "decay": 0.75, "floor": 0.5}), bass(a, b, 0.5), lead(), ears, ruby, gold], pump=pump)',
            'S(name, a, b, [glass(a, b, 0.24, gate={"pat": BASS, "step": 0.25, "decay": 0.75, "floor": 0.5}), bass(a, b, 0.75, floor=0.12), lead(), ears, ruby, gold], pump=pump)')
s=s.replace('[glass(a, b, 0.28, gate={"pat": BASS, "step": 0.25, "decay": 0.75, "floor": 0.5}), bass(a, b, 0.45, floor=0.2), lead(m), organ(a, b, 0.42)]','[glass(a, b, 0.24, gate={"pat": BASS, "step": 0.25, "decay": 0.75, "floor": 0.5}), bass(a, b, 0.7, floor=0.12), lead(m), organ(a, b, 0.42)]')
# the rising plucks: the triad on the beat, all three pipes firing up on every off-beat, gold at the tip
s=s.replace('''def chirp(lo, hi, gain=0.6, tip=None):
    """The off-beat rising plucks: a tube fires up on each, the triad in order, then all three."""
    return {"fx": "blades", "seq": ["0", "0", "1", "1", "2", "2", "012", "012"], "step": 0.5, "rise": 0.45, "keep": 0.6,
            "c": K(lo, hi, cmain), "ctip": tip if tip is not None else cmain(FS), "gain": gain,
            "gate": {"pat": ".x", "step": 0.5, "decay": 0.45}}''','''def chirp(lo, hi, gain=0.45):
    """The off-beat rising plucks: the triad on the beat, and all three pipes firing up on every off-beat, gold at the tip."""
    return {"fx": "blades", "pal": "spark", "seq": ["0", "012", "1", "012", "2", "012", "1", "012"], "step": 0.5, "rise": 0.5, "keep": 0.2,
            "c": 0, "ctip": 1, "gain": gain}''')
s=s.replace('''                   "white": [[255, 255, 255], [255, 255, 255]]},''','''                   "white": [[255, 255, 255], [255, 255, 255]],
                   "spark": [[0, 55, 255], [40, 125, 255], [255, 170, 30]]},''')
open(p,"w").write(s)
