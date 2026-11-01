"""Electrical chain plan for the mau5head shell. Reads pixel_map.csv, returns ordered segments + node map.
Output 1 (chain A): back half, channels 0→33, serpentine starting at the +X pole bottom.
Output 2 (chain B): front UPPER band 67→34 (+X→−X), one jumper at the −X pole, front LOWER band 34→67 (−X→+X), then ER, VT, VB, EL."""
import csv, math, collections, numpy as np
N_CH=68; DAZ=360.0/N_CH; LAT_MIN=-40.0; DLAT=None
def dirv(az,el):
    a,e=math.radians(az),math.radians(el); return np.array([math.cos(e)*math.cos(a),math.cos(e)*math.sin(a),math.sin(e)])
def load(path):
    rows=list(csv.DictReader(open(path))); by=collections.defaultdict(dict)
    for r in rows: by[int(r["channel"])][int(r["row"])]=r
    global DLAT
    lats=sorted(set(float(r["elevation_deg"]) for r in rows)); DLAT=lats[1]-lats[0]
    return by
def runs_of(ks):
    ks=sorted(ks); out=[]; cur=[]
    for k in ks:
        if cur and k!=cur[-1]+1: out.append(cur); cur=[]
        cur.append(k)
    if cur: out.append(cur)
    return out
def band_of(r):
    y,z=float(r["y"]),float(r["z"])
    if y>=0: return "back"
    e=math.degrees(math.atan2(z,-y)); return "upper" if e>10 else "lower"
def plan(path, R_pt=170.0):
    by=load(path); segs=[]
    def add(chain,band,j,run,direction):
        segs.append(dict(chain=chain,band=band,channel=j,rows=run if direction=="up" else run[::-1],direction=direction))
    # chain A: back half 0→33
    for i,j in enumerate(range(0,34)):
        direction="up" if i%2==0 else "down"
        rr=runs_of(by[j].keys()); rr=rr if direction=="up" else rr[::-1]
        for run in rr: add("A","back",j,run,direction)
    # chain B: upper band 67→34 (start at the mouth edge going up), then lower band 34→67 (start at the mouth edge going down)
    for i,j in enumerate(range(67,33,-1)):
        direction="up" if i%2==0 else "down"
        ks=[k for k,r in by[j].items() if band_of(r)=="upper"]
        rr=runs_of(ks); rr=rr if direction=="up" else rr[::-1]
        for run in rr: add("B","upper",j,run,direction)
    for i,j in enumerate(range(34,68)):
        direction="down" if i%2==0 else "up"
        ks=[k for k,r in by[j].items() if band_of(r)=="lower"]
        rr=runs_of(ks); rr=rr if direction=="up" else rr[::-1]
        for run in rr: add("B","lower",j,run,direction)
    # numbering
    node={}; n=0; idx=collections.Counter()
    for s in segs:
        idx[s["chain"]]+=1; s["id"]=f'{s["chain"]}{idx[s["chain"]]:02d}'
        s["led_first"]=n+1
        for k in s["rows"]: n+=1; node[(s["channel"],k)]=n
        s["led_last"]=n; s["n"]=len(s["rows"])
        az=(s["channel"]+0.5)*DAZ
        s["p_in"]=dirv(az,LAT_MIN+s["rows"][0]*DLAT)*R_pt; s["p_out"]=dirv(az,LAT_MIN+s["rows"][-1]*DLAT)*R_pt
        s["az"]=round(az,1)
    for i,s in enumerate(segs):
        s["prev"]=segs[i-1]["id"] if i>0 and segs[i-1]["chain"]==s["chain"] else f'WLED output {1 if s["chain"]=="A" else 2}'
        s["next"]=segs[i+1]["id"] if i<len(segs)-1 and segs[i+1]["chain"]==s["chain"] else None
    nA=sum(s["n"] for s in segs if s["chain"]=="A"); nB=n-nA
    return segs,node,nA,nB,by
if __name__=="__main__":
    import sys
    segs,node,nA,nB,by=plan(sys.argv[1] if len(sys.argv)>1 else "out_hat9/pixel_map.csv")
    print(f"A: {sum(1 for s in segs if s['chain']=='A')} segs / {nA} LEDs   B: {sum(1 for s in segs if s['chain']=='B')} segs / {nB} LEDs  (upper {sum(s['n'] for s in segs if s['band']=='upper')}, lower {sum(s['n'] for s in segs if s['band']=='lower')})")
    # jumper lengths
    L=[np.linalg.norm(segs[i+1]["p_in"]-segs[i]["p_out"]) for i in range(len(segs)-1) if segs[i]["chain"]==segs[i+1]["chain"]]
    print(f"jumpers: {len(L)}, longest {max(L):.0f} mm, >60 mm: {sum(1 for x in L if x>60)}")
    # any jumper crossing the mouth opening? (both ends front, one upper one lower)
    cross=[(segs[i]['id'],segs[i+1]['id']) for i in range(len(segs)-1) if {segs[i]['band'],segs[i+1]['band']}=={'upper','lower'}]
    print("upper↔lower jumpers (should be exactly the one at the pole):", cross)
