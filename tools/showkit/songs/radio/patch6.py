import os
p=os.environ["W"]+"/write_treatment.py"
s=open(p).read()
def rep(a,b):
    global s
    assert a in s, a[:70]
    s=s.replace(a,b,1)
# the needle drifts off the station while the interference rises
rep('''FALL1 = [(59.0, 0.25)''','''DRIFT1 = [(24.0, 0.25), (25.0, 0.25), (25.5, 0.20), (26.0, 0.20), (26.5, 0.30), (27.0, 0.30), (27.5, 0.13), (28.0, 0.13)]
DRIFT2 = [(88.0, 0.25), (89.0, 0.25), (89.5, 0.31), (90.0, 0.31), (90.5, 0.18), (91.0, 0.18), (91.5, 0.38), (92.0, 0.38)]
FALL1 = [(59.0, 0.25)''')
rep('''  WAVE("wave_t", [0.3, 0.0], [0.6, 0.2], wspeed=0.25),
  vu("tubes1", band("mid", -1.6, 1.0), [0.36, 0.12]),
  vu("tubes2", band("high", -1.0, 1.5), [0.36, 0.12])]})''','''  WAVE("wave_t", [0.3, 0.0], [0.6, 0.2], wspeed=0.25),
  dict(needle(DRIFT1, 24, 28, 0.75), env={"in": 4}),
  vu("tubes1", band("mid", -1.6, 1.0), [0.36, 0.12]),
  vu("tubes2", band("high", -1.0, 1.5), [0.36, 0.12])]})''')
rep('''S({"name": "interference2", "from": "fade2", "to": "drop2", "like": "interference", "out": 1})''','''S({"name": "interference2", "from": "fade2", "to": "drop2", "like": "interference", "out": 1, "patch": {"3": dict(needle(DRIFT2, 88, 92, 0.75), env={"in": 4})}})''')
open(p,"w").write(s)
