p="tools/showkit/work/chords/gen.py"
s=open(p).read()
def rep(a,b,count=1):
    global s
    assert a in s, a
    s=s.replace(a,b) if count==0 else s.replace(a,b,count)
# --- the opening: the pipes have to be seen
rep('''S("root", 4, 8, [pedal(4, 8, 0.3), pipe(0, 4, 8, [0.12, 0.3])])
S("third", 8, 12, [pedal(8, 12, 0.32), pipe(0, 8, 12, 0.3), pipe(1, 8, 12, [0.12, 0.3])])
S("fifth", 12, 16, [pedal(12, 16, 0.34), pipe(0, 12, 16, 0.32), pipe(1, 12, 16, 0.32), pipe(2, 12, 16, [0.12, 0.32])])''',
'''S("root", 4, 8, [pedal(4, 8, 0.3), pipe(0, 4, 8, [0.3, 0.42], floor=0.4)])
S("third", 8, 12, [pedal(8, 12, 0.32), pipe(0, 8, 12, 0.42, floor=0.4), pipe(1, 8, 12, [0.3, 0.42], floor=0.4)])
S("fifth", 12, 16, [pedal(12, 16, 0.34), pipe(0, 12, 16, 0.42, floor=0.4), pipe(1, 12, 16, 0.42, floor=0.4), pipe(2, 12, 16, [0.3, 0.42], floor=0.4)])''')
rep('layers = [pedal(a, b, 0.34, on="jaw+rims"), glass(a, b, g)] + pipes(a, b, 0.34) + [lead(m)]','layers = [pedal(a, b, 0.34, on="jaw+rims"), glass(a, b, g)] + pipes(a, b, 0.4) + [lead(m)]')
# --- each pane flares as it goes in
rep('''# --- all of it, with the beat under it''','''for a, m in [(16, "chords_ruby1"), (20, "chords_blue"), (24, "chords_gold"), (28, "chords_p06")]:
    H("PANE", a, 3, [{"fx": "preset", "name": "sprite", "on": "shell", "params": dict(SPR, sprite=m, color="glass@%g" % chi(GM)), "gain": [1.0, 0.0]}])
# --- all of it, with the beat under it''')
# --- the hold: dark at first, the light climbing the window, the pipes firing faster and faster
rep('''    return [{"fx": "sweep", "on": "face", "axis": "y", "shape": "p", "mode": "fill", "soft": 0.25, "from": -0.2, "to": 1.2, "c": chi(GP), "gain": [0.1, 0.3]},
            {"fx": "fill", "on": "face", "c": clo(GP), "gain": [0.3, 0.12]},
            {"fx": "fill", "on": "jaw", "c": cmain(GP), "gain": [0.3, 0.1]},
            {"fx": "blades", "seq": ["012"], "step": {num(a): 2, num(a + 2): 1, num(a + 3): 0.5}, "rise": 0.7, "keep": 0.2, "rim": 0.8, "c": cmain(GP), "ctip": chi(GP), "gain": [0.3, 0.7]},
            lead()]''',
'''    return [{"fx": "sweep", "on": "face", "axis": "y", "shape": "p", "mode": "fill", "soft": 0.2, "from": -0.15, "to": 1.15, "c": cmain(GP), "gain": [0.22, 0.34]},
            {"fx": "sweep", "on": "face", "axis": "y", "shape": "p", "mode": "band", "width": 0.14, "from": -0.05, "to": 1.2, "c": chi(GP), "gain": [0.3, 0.6]},
            {"fx": "fill", "on": "face", "c": clo(GP), "gain": 0.07},
            {"fx": "fill", "on": "jaw", "c": cmain(GP), "gain": [0.4, 0.12]},
            {"fx": "blades", "seq": ["012"], "step": {num(a): 2, num(a + 2): 1, num(a + 3): 0.5, num(a + 3.5): 0.25}, "rise": 0.7, "keep": 0.15, "rim": 0.8, "c": cmain(GP), "ctip": chi(GP), "gain": [0.3, 0.55]},
            lead()]''')
# --- the flood: what sits on the glass goes under the lead
rep('''def flood(a, b, extra, gate_floor=0.5, g=0.24, pump=PUMP):
    dome = glass(a, b, g, gate={"pat": BASS, "step": 0.25, "decay": 0.75, "floor": gate_floor})
    S("%d" % a, a, b, [dome, bass(a, b, 0.75, floor=0.12), lead()] + extra, pump=pump)''',
'''def flood(a, b, extra, under=(), gate_floor=0.5, g=0.24, pump=PUMP):
    dome = glass(a, b, g, gate={"pat": BASS, "step": 0.25, "decay": 0.75, "floor": gate_floor})
    S("%d" % a, a, b, [dome] + list(under) + [bass(a, b, 0.75, floor=0.12), lead()] + extra, pump=pump)''')
rep('flood(52, 68, [organ(52, 68, enter=True), beam(52, 68)])','flood(52, 68, [organ(52, 68, enter=True)], under=[beam(52, 68)])')
rep('flood(68, 84, [organ(68, 84), stain("chords_ruby1", EE, 68, 84, 0.3), hats()])','flood(68, 84, [organ(68, 84), stain("chords_ruby1", EE, 68, 84, 0.3)], under=[hats()])')
rep('flood(196, 212, [organ(196, 212, enter=True), beam(196, 212)])','flood(196, 212, [organ(196, 212, enter=True)], under=[beam(196, 212)])')
# --- the second drop trades its panes faster and faster until the bar that stops
rep('blaze("clapback", 172, 180, *stains(172, 180), chirp(172, 180, 0.46, claps=True))','blaze("clapback", 172, 180, *stains(172, 180, BAR_RATE), chirp(172, 180, 0.46, claps=True))')
rep('blaze("trade", 180, 188, *stains(180, 188, BAR_RATE), chirp(180, 188))','blaze("trade", 180, 188, *stains(180, 188, BAR_RATE * 2), chirp(180, 188))')
rep('blaze("tradeb", 188, 195, *stains(188, 195, BAR_RATE * 2), chirp(188, 195, 0.46, claps=True))','blaze("tradeb", 188, 195, *stains(188, 195, BAR_RATE * 4), chirp(188, 195, 0.46, claps=True))')
rep('BAR_RATE = 128.001 / 60.0 / 4.0','BAR_RATE = round(1.0 / (4 * 0.468747), 6)')
# --- white, once
rep('H("WHITE", "blaze", 2, [blow(0.5, 0.2, pal="white"), ring(0.5, 0.9, pal="white"), {"fx": "fill", "on": "rims", "pal": "white", "c": 0, "gain": [0.3, 0]}])',
    'H("WHITE", "blaze", 2, [blow(0.5, 0.16, pal="white"), ring(0.5, 1.0, pal="white"), {"fx": "fill", "on": "rims", "pal": "white", "c": 0, "gain": [0.25, 0]}])')
# --- the stopped bar has its crash too
rep('H("HOME", "home", 2,','H("CRASH 3", 195.75, 1, [{"fx": "fill", "on": "rims", "c": chi(EE), "gain": [0.6, 0]}])\nH("HOME", "home", 2,')
# --- the turnarounds are bigger where the ears are otherwise on the off-beat
rep('"gain": 0.2}])\n# --- only the ticks left','"gain": 0.3 if (84 < b < 100 or 164 < b < 195) else 0.2}])\n# --- only the ticks left')
open(p,"w").write(s)
p2="tools/showkit/work/chords/panes.py"
t=open(p2).read()
if "chords_p06" not in t:
    t=t.replace('sp["chords_blue"] = rows_for(lambda p: p in (2, 4))','sp["chords_blue"] = rows_for(lambda p: p in (2, 4))\nsp["chords_p06"] = rows_for(lambda p: p in (0, 6))')
    open(p2,"w").write(t)
