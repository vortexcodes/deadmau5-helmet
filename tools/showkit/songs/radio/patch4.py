import os
p=os.environ["W"]+"/write_treatment.py"
s=open(p).read()
def rep(a,b):
    global s
    assert a in s, a[:70]
    s=s.replace(a,b,1)
# 84-88: the sines tighten, as they did at bar 20, in place of the amber ring
rep('''S({"name": "two signals c", "from": "song2b", "to": "fade2", "like": "two signals b", "patch": {"0": dict(rings(16, 0.32, pal="rings_a", per=4, cg=1.5, gate=False))}})''',
    '''S({"name": "two signals c", "from": "song2b", "to": "fade2", "like": "two signals b", "patch": {"1": {"wspeed": 0.5, "wscale": 3}, "2": {"wspeed": 0.5, "wscale": 3}}})''')
# the kick's meter a little lower so the kick frames stay inside the budget and the shell keeps its light on the kick
rep('''VU_KICK = lambda on, gain=0.5: vu(on, band("bass", 0.02, 1.15, True), gain)''','''VU_KICK = lambda on, gain=0.45: vu(on, band("bass", 0.02, 1.15, True), gain)''')
rep('''def sign_scene(name, a, b, pump=PUMP, gain=0.62, kick=0.5, chords=EARG):''','''def sign_scene(name, a, b, pump=PUMP, gain=0.62, kick=0.45, chords=EARG):''')
rep('''  HITF("SONG", "song", 2, [RIMFLASH(0.7, c=0.0)]),''','''  HITF("SONG", "song", 2, [RIMFLASH(0.5, c=0.0)]),''')
rep('''  HITF("SONG 2", "song2", 2, [RIMFLASH(0.7, c=0.8)]),''','''  HITF("SONG 2", "song2", 2, [RIMFLASH(0.5, c=0.8)]),''')
rep('''air(rings2(28, 0.62), [PEAK(0.4)])''','''air(rings2(28, 0.62), [PEAK(0.3)])''')
open(p,"w").write(s)
