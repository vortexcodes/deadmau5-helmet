import sys,os
KIT=os.environ["KIT"];sys.path.insert(0,KIT+"/work/radio")
from lab import *
P={"dial":[[0,0,0],[60,18,0],[200,90,8],[255,160,40],[255,215,130]],
   "r4":{"stops":[[0,0,0],[0,255,210],[0,0,0],[0,0,0]],"wrap":True},
   "r6":{"stops":[[0,0,0],[0,255,210],[0,30,25],[0,0,0],[0,0,0],[0,0,0]],"wrap":True},
   "r8":{"stops":[[0,0,0],[0,255,210],[0,60,50],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0]],"wrap":True},
   "m6":{"stops":[[0,0,0],[255,0,170],[60,0,40],[0,0,0],[0,0,0],[0,0,0]],"wrap":True},
   "beacon":[[255,0,60],[255,0,90],[255,60,130]],
   "vu":[[0,220,180],[0,235,120],[255,170,20],[255,30,60],[255,0,130]]}
def rg(pal,cg,beat,n=32,rad=440,soft=260,gain=.8,per=1,on="all",x=0,y=170):
    # scene 28..36; phase c0 so the bright stop leaves d=0 on the beat
    stops=len(P[pal]["stops"])
    c0=1.0/stops
    return {"fx":"orb","on":on,"x":x,"y":y,"rad":rad,"soft":soft,"pal":pal,"c":[c0,c0-n/per],"cgrad":cg,"gain":gain}
MAST={"fx":"sweep","on":"face","axis":"x","shape":"p","mode":"band","width":0.035,"from":0.5,"to":0.5,"pal":"dial","c":0.95,"gain":0.8}
BEAC={"fx":"orb","on":"shell","mix":"over","x":0,"y":166,"rad":24,"soft":12,"pal":"beacon","c":0.5,"gain":0.9}
T=[]
for name,pal,cg in [("r4 cg4","r4",4),("r6 cg4","r6",4),("r6 cg6","r6",6),("r8 cg6","r8",6),("r6 cg5","r6",5),("r8 cg8","r8",8)]:
    for ph in (0,0.25,0.5):
        T.append((name+" ph%.2f"%ph,30+ph/4.0,28,36,[rg(pal,cg,0),MAST,BEAC]))
# stereo transmitters from each ear
for ph in (0,0.25,0.5,0.75,1.0,1.5):
    T.append(("ears tx ph%.2f"%ph,30+ph/4.0,28,36,[rg("r6",5,0,n=16,per=1,x=-232,y=232,rad=460,soft=240),rg("m6",5,0,n=16,per=1,x=232,y=232,rad=460,soft=240)]))
sheet(T,P,KIT+"/work/radio/t2.png",cols=6)
