import os
p=os.environ["W"]+"/write_treatment.py"
s=open(p).read()
a='''"c": [c0 + n, c0] if inward else [c0, c0 - n]'''
assert s.count(a)==2
s=s.replace(a,'''"c": [c0, c0 + n] if inward else [c0, c0 - n]''')
open(p,"w").write(s)
