p="tools/showkit/work/chords/gen.py"
s=open(p).read()
def rep(a,b,count=1):
    global s
    assert a in s, a
    s=s.replace(a,b) if count==0 else s.replace(a,b,count)
# pipes: lower floors, so the attack shows and the intro costs less
rep('def pipe(t, lo, hi, gain, floor=0.4):','def pipe(t, lo, hi, gain, floor=0.28):')
rep('def pipes(lo, hi, gain, n=3, floor=0.4):','def pipes(lo, hi, gain, n=3, floor=0.28):')
rep('def tubes_all(lo, hi, gain, floor=0.35):','def tubes_all(lo, hi, gain, floor=0.25):')
# the ears step aside during a turnaround and at the drop, so the shell keeps its light
rep('''def organ(lo, hi, gain=0.55):
    """The triad in order on the 8ths; on the clap all three tubes at once."""
    seq = [("012" if i in (2, 12) else ["0", "1", "2", "1"][i % 4]) for i in range(16)]
    return {"fx": "blades", "seq": seq, "step": 0.5, "rise": 0.3, "keep": 0.3, "c": K(lo, hi, cmain), "ctip": K(lo, hi, chi), "gain": gain}''',
'''def organ(lo, hi, gain=0.55, enter=False):
    """The triad in order on the 8ths; on the clap all three tubes at once."""
    seq = [("012" if i in (2, 12) else ["0", "1", "2", "1"][i % 4]) for i in range(16)]
    g = TURN(lo, hi, gain, 0.25)
    if enter:
        g[num(lo)] = 0.15; g[num(lo + 0.5)] = gain
    return {"fx": "blades", "seq": seq, "step": 0.5, "rise": 0.3, "keep": 0.3, "c": K(lo, hi, cmain), "ctip": K(lo, hi, chi), "gain": g}''')
rep('''def arp(lo, hi, gain=0.35, step=0.5, seq=("0", "1", "2", "1")):
    return {"fx": "blades", "seq": list(seq), "step": step, "rise": 0.4, "keep": 0.25, "c": K(lo, hi, cmain), "ctip": K(lo, hi, chi), "gain": gain}''',
'''def arp(lo, hi, gain=0.35, step=0.5, seq=("0", "1", "2", "1")):
    return {"fx": "blades", "seq": list(seq), "step": step, "rise": 0.4, "keep": 0.25, "c": K(lo, hi, cmain), "ctip": K(lo, hi, chi), "gain": TURN(lo, hi, gain, 0.25)}''')
rep('''def chirp(lo, hi, gain=0.45):
    """The off-beat rising plucks: the triad on the beat, and all three pipes firing up on every off-beat, gold at the tip."""
    return {"fx": "blades", "pal": "spark", "seq": ["0", "012", "1", "012", "2", "012", "1", "012"], "step": 0.5, "rise": 0.5, "keep": 0.2,
            "c": 0, "ctip": 1, "gain": gain}''',
'''def chirp(lo, hi, gain=0.42, claps=False):
    """The off-beat rising plucks: the triad on the beat, and all three pipes firing up on every off-beat, gold at the tip."""
    seq = [("012" if i % 2 or (claps and i in (2, 12)) else ["0", "1", "2", "1"][(i // 2) % 4]) for i in range(16)]
    return {"fx": "blades", "pal": "spark", "seq": seq, "step": 0.5, "rise": 0.5, "keep": 0.2, "c": 0, "ctip": 1, "gain": TURN(lo, hi, gain, 0.2)}''')
rep('flood(52, 68, [organ(52, 68), beam(52, 68)])','flood(52, 68, [organ(52, 68, enter=True), beam(52, 68)])')
rep('flood(196, 212, [organ(196, 212), beam(196, 212)])','flood(196, 212, [organ(196, 212, enter=True), beam(196, 212)])')
rep('blaze("clapback", 172, 180, *stains(172, 180), chirp(172, 180, 0.7))','blaze("clapback", 172, 180, *stains(172, 180), chirp(172, 180, 0.46, claps=True))')
rep('blaze("tradeb", 188, 195, *stains(188, 195, BAR_RATE * 2), chirp(188, 195, 0.7))','blaze("tradeb", 188, 195, *stains(188, 195, BAR_RATE * 2), chirp(188, 195, 0.46, claps=True))')
# hits: a fired pipe rather than a whole-ear fill
rep('''def blow(c, gain=0.5, pal="glass"):
    return {"fx": "fill", "on": "ears", "pal": pal, "c": c, "gain": [gain, 0]}''',
'''def blow(c, gain=0.36, pal="glass"):
    return {"fx": "blades", "pal": pal, "seq": ["012"], "step": 2, "rise": 0.08, "keep": 0, "c": c, "ctip": c, "gain": gain}''')
rep('H("FLOOD", "flood", 2, [blow(chi(GM), 0.32), ring(chi(GM), 0.8)])','H("FLOOD", "flood", 2, [blow(chi(GM)), ring(chi(GM), 0.8)])')
rep('H("HOME", "home", 2, [blow(chi(GM), 0.3), ring(chi(GM), 0.8)])','H("HOME", "home", 2, [blow(chi(GM)), ring(chi(GM), 0.8)])')
rep('H("DAWN", "wash", 2, [ring(chi(GM), 0.7), blow(chi(GM), 0.25)])','H("DAWN", "wash", 2, [ring(chi(GM), 0.7), blow(chi(GM), 0.2)])')
rep('"gain": 0.34}])\n# --- only the ticks left','"gain": 0.2}])\n# --- only the ticks left')
# white, once: as much as the budget lets it be without dimming the shell
rep('H("WHITE", "blaze", 2, [{"fx": "fill", "on": "all", "pal": "white", "c": 0, "gain": [0.3, 0]}, ring(0.5, 0.6, pal="white")])',
    'H("WHITE", "blaze", 2, [blow(0.5, 0.2, pal="white"), ring(0.5, 0.9, pal="white"), {"fx": "fill", "on": "rims", "pal": "white", "c": 0, "gain": [0.3, 0]}])')
# the second time round the beat sits under less pipe
rep('tubes_all(148, 160, 0.48), lead()], pump=dict(SOFT, depth=0.18))','tubes_all(148, 160, 0.38), lead()], pump=dict(SOFT, depth=0.2))')
rep('glass(144, 148, 0.2), tubes_all(144, 148, 0.42), lead()])','glass(144, 148, 0.2), tubes_all(144, 148, 0.36), lead()])')
rep('tubes_all(136, 144, 0.38), lead()])','tubes_all(136, 144, 0.34), lead()])')
rep('{"fx": "fill", "on": "jaw", "c": K(195, 196, cmain), "gain": {"195": 0, "195.375": 0.4}},','{"fx": "fill", "on": "jaw", "c": K(195, 196, cmain), "gain": {"195": 0, "195.375": 0.6}},')
rep('"gain": {"195": 0, "195.375": 0.5}}])','"gain": {"195": 0, "195.375": 0.4}}])')
rep('pipes(32, 40, 0.42) + [lead()], pump=SOFT)','pipes(32, 40, 0.42) + [lead()], pump=dict(SOFT, depth=0.2))')
rep('pipes(40, 48, 0.48) + [lead()], pump=dict(SOFT, depth=0.18))','pipes(40, 48, 0.46) + [lead()], pump=dict(SOFT, depth=0.22))')
open(p,"w").write(s)
