import sys, os
sys.path.insert(0, os.getcwd())
import numpy as np, mau5engine as E
h = E.Helmet()
s = h.shell
print("n", h.n, "shell", s.sum(), "px", h.px[s].min(), h.px[s].max(), "py", h.py[s].min(), h.py[s].max())
print("ears px", h.px[h.ears].min(), h.px[h.ears].max(), "py", h.py[h.ears].min(), h.py[h.ears].max())
# ascii map at 16 mm
xs = np.arange(-176, 177, 16); ys = np.arange(176, -113, -16)
for y in ys:
    row = ""
    for x in xs:
        n = ((h.px[s] >= x) & (h.px[s] < x+16) & (h.py[s] < y) & (h.py[s] >= y-16)).sum()
        row += "%2s" % (n if n else ".")
    print("%5d %s" % (y, row))
