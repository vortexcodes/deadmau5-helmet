import re
p="tools/showkit/work/chords/gen.py"
s=open(p).read()
s=s.replace('GLASS = [[0, 10, 80], [0, 40, 255], [40, 110, 255],','GLASS = [[0, 14, 90], [0, 55, 255], [40, 125, 255],')
# clap: fires on the beat grid, gated to the two-bar clap
s=s.replace('''def clap(lo, hi, gain=0.6):
    return {"fx": "blades", "seq": ["012"], "step": 0.25, "rise": 0.9, "keep": 0.5, "c": K(lo, hi, cmain), "ctip": K(lo, hi, chi), "gain": gain,
            "gate": {"pat": CLAPS, "step": 0.25, "decay": 0.9}}''','''def clap(lo, hi, gain=0.6):
    return {"fx": "blades", "seq": ["012"], "step": 1, "rise": 0.14, "keep": 0.25, "c": K(lo, hi, cmain), "ctip": K(lo, hi, chi), "gain": gain,
            "gate": {"pat": ".x....x.", "step": 1, "decay": 0.9}}''')
s=s.replace('''    return {"fx": "blades", "seq": ["0", "0", "1", "1", "2", "2", "012", "012"], "step": 0.5, "rise": 0.45, "keep": 0.2,
            "c": K(lo, hi, cmain), "ctip": tip if tip is not None else cmain(FS), "gain": gain,
            "gate": {"pat": ".x", "step": 0.5, "decay": 0.5}}''','''    return {"fx": "blades", "seq": ["0", "0", "1", "1", "2", "2", "012", "012"], "step": 0.5, "rise": 0.45, "keep": 0.6,
            "c": K(lo, hi, cmain), "ctip": tip if tip is not None else cmain(FS), "gain": gain,
            "gate": {"pat": ".x", "step": 0.5, "decay": 0.45}}''')
# the flood hit: light in the shell, not all in the ears
s=s.replace('H("FLOOD", "flood", 2, [blow(chi(GM), 0.55), ring(chi(GM), 0.7)])','H("FLOOD", "flood", 2, [blow(chi(GM), 0.32), ring(chi(GM), 0.8)])')
s=s.replace('H("HOME", "home", 2, [blow(chi(GM), 0.5), ring(chi(GM), 0.7)])','H("HOME", "home", 2, [blow(chi(GM), 0.3), ring(chi(GM), 0.8)])')
s=s.replace('H("DAWN", "wash", 2, [ring(chi(GM), 0.6), blow(chi(GM), 0.4)])','H("DAWN", "wash", 2, [ring(chi(GM), 0.7), blow(chi(GM), 0.25)])')
# the turnarounds in the ears, as hits
s=s.replace('''# --- only the ticks left''','''# --- every turnaround in the ears: gold, then ruby
for b in [b for b, c in TL if c == FS and (52 < b < 116 or 164 < b < 228) and b != 195.375]:
    H("TURN", b, 2.5, [{"fx": "grad", "on": "tubes", "axis": "al", "axis2": "al", "scale": 0.5, "lo": {num(b): clo(FS), num(b + 0.25): clo(EE)}, "hi": {num(b): chi(FS), num(b + 0.25): chi(EE)}, "gain": 0.34}])
# --- only the ticks left''')
s=s.replace('''S("ticks", 228, 236, [{"fx": "fill", "on": "rims", "c": cmain(GM), "gain": [0.5, 0.2], "gate": {"pat": "x...", "step": 0.25, "decay": 0.35}},
                      {"fx": "blades", "on": "tube0", "seq": ["0"], "step": 1, "rise": 0.2, "keep": 0, "c": clo(GM), "ctip": cmain(GM), "gain": [0.3, 0.08]}])''','''S("ticks", 228, 236, [glass(228, 236, [0.2, 0.0]), lead("chords_m1"),
                      {"fx": "fill", "on": "rims", "c": cmain(GM), "gain": [0.5, 0.15], "gate": {"pat": "x...", "step": 0.25, "decay": 0.35}},
                      {"fx": "blades", "seq": ["0"], "step": 1, "rise": 0.2, "keep": 0, "c": clo(GM), "ctip": cmain(GM), "gain": [0.3, 0.06]}])''')
open(p,"w").write(s)
