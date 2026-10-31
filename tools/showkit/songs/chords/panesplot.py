import os,sys,math
sys.path.insert(0,os.getcwd())
import numpy as np, mau5engine as E
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
h=E.Helmet(); s=np.asarray(h.shell,bool); X,Y=h.px[s],h.py[s]
W=os.path.dirname(os.path.abspath(__file__))
def pane(x,y,HUB=(0,30),NW=7,LEAD=6.5):
    if y<=28:
        for cut in (-20.0,-75.0):
            if abs(y-cut)<7: return -1
        return 10
    r=math.hypot(x-HUB[0],y-HUB[1]); th=max(0,min(180,math.degrees(math.atan2(y-HUB[1],x-HUB[0]))))
    k=th/(180.0/NW); i=min(NW-1,int(k))
    d=min(k-i,i+1-k)*math.radians(180.0/NW)*r
    if d<LEAD and 0<round(k)<NW: return -1
    return i
P=np.array([pane(a,b) for a,b in zip(X,Y)])
print({int(k):int((P==k).sum()) for k in np.unique(P)})
fig,ax=plt.subplots(figsize=(12,9))
c=np.where(P==-1,-3,P)
ax.scatter(X,Y,c=c,cmap="tab20",s=70)
ax.set_aspect("equal")
for x,y,p in zip(X,Y,P):
    ax.text(x,y,str(p),fontsize=6,ha="center",va="center")
fig.tight_layout(); fig.savefig(os.path.join(W,"panes.png"),dpi=70)
