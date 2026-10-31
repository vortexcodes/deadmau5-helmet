import sys,os
sys.path.insert(0,os.getcwd())
import numpy as np, mau5engine as E, mau5preview as PV
h=E.Helmet(); sc=PV.Scene(h)
f=np.zeros((h.n,3))
f[h.rims]=(255,0,0)
for t,c in ((0,(0,255,0)),(1,(60,60,255)),(2,(255,255,0))):
    f[h.tube==t]=c
s=h.shell
f[s]=np.stack([h.nfa[s]*255, 40+0*h.nfa[s], h.nel[s]*255],1)
im=sc.frame(f)
im.save(sys.argv[1]); print(im.size)
