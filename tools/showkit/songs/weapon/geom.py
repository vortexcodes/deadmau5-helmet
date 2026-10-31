import sys,os; sys.path.insert(0,os.getcwd())
import numpy as np, mau5engine as E, mau5scene as S
h=E.Helmet()
print("n",h.n,"shell",h.shell.sum(),"ears",h.ears.sum())
s=h.shell
print("px",h.px[s].min(),h.px[s].max(),"py",h.py[s].min(),h.py[s].max())
print("nfa",h.nfa[s].min(),h.nfa[s].max(),"nel",h.nel[s].min(),h.nel[s].max())
print("er",h.er[s].min(),h.er[s].max(),"ea",h.ea[s].min(),h.ea[s].max())
# Histogram of LEDs by row in 16 mm rows
for y0 in range(176,-120,-16):
    m=s&(h.py>=y0-8)&(h.py<y0+8)
    if m.any():
        print("y %4d  n %3d  x %6.0f..%6.0f  nel %.2f..%.2f  nfa %.2f..%.2f  er %.2f..%.2f ea %.2f..%.2f"%(y0,m.sum(),h.px[m].min(),h.px[m].max(),h.nel[m].min(),h.nel[m].max(),h.nfa[m].min(),h.nfa[m].max(),h.er[m].min(),h.er[m].max(),h.ea[m].min(),h.ea[m].max()))
    else: print("y %4d  none"%y0)
for r in ("face","jaw","left","right","rims","tubes","rim1","rim2"):
    m=S._region_mask(h,r); print(r,m.sum(),"px %.0f..%.0f py %.0f..%.0f"%(h.px[m].min(),h.px[m].max(),h.py[m].min(),h.py[m].max()))
# ear positions
for nm,m in (("ear1",h.ear1),("ear2",h.ear2)):
    print(nm,"px %.0f..%.0f py %.0f..%.0f"%(h.px[m].min(),h.px[m].max(),h.py[m].min(),h.py[m].max()))
# ascii plot of LEDs on the shell, 8 mm cells
W=np.arange(-180,184,10); Hh=np.arange(176,-116,-12)
for y in Hh:
    row=""
    for x in W:
        c=(s&(np.abs(h.px-x)<5)&(np.abs(h.py-y)<6)).sum()
        row+=str(min(c,9)) if c else "."
    print("%5d %s"%(y,row))
