import numpy as np, sys
z=np.load(sys.argv[1]); spb=0.468725; t0=0.040275
tt=z["tt"]
bar=4*spb
lo,hi=int(sys.argv[2]),int(sys.argv[3])
CH=" .:-=+*#%@"
for k in ["sub","low","mid","pres","air"]:
    e=np.log1p(z[k]*0.2)
    P=np.zeros(48)
    for b in range(lo,hi):
        ts=t0+(b+np.arange(48)/48)*bar
        i=np.clip(np.searchsorted(tt,ts),0,len(tt)-1)
        P+=e[i]
    P/=max(hi-lo,1)
    v=(P-P.min())/(P.max()-P.min()+1e-9)
    print("%-5s "%k+"|".join("".join(CH[min(9,int(a*9.99))] for a in v[i:i+12]) for i in range(0,48,12)))
