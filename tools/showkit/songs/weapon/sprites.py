import json, math
import numpy as np
S={}
S["weapon_swords"]=[
"##...........##",
"###.........###",
".###.......###.",
"..###.....###..",
"...###...###...",
".....#####.....",
"......###......",
".....#####.....",
"..#####.#####..",
".####.....####.",
"###.........###"]
S["weapon_line"]=["#"*40]
S["weapon_off"]=["."]
S["weapon_sword"]=["...#...","...#...","...#...","...#...","...#...","...#...","...#...","...#...","#######"]
S["weapon_banner1"]=["###..#####..###","###..#####..###","###..#####..###","###..#####..###","###..#####..###","###..#####..###","#.#..##.##..#.#","#.#..#...#..#.#"]
S["weapon_banner2"]=["###..#####..###","###..#####..###","###..#####..###","###..#####..###","###..#####..###","##...####...##.","#.#.##.##..#.#.",".#...#.#....#.."]
S["weapon_banner3"]=["###..#####..###","###..#####..###","###..#####..###","###..#####..###","###..#####..###",".##...####...##",".#.#..##.##.#.#","..#....#.#....#"]
# The slash: a blade swung up from the jaw, round the cheek and across the dome into the far ear.
# Drawn in millimetres on the real shell, on a 20 by 20 sheet over y_lo -108, y_hi 170, x_half 171.
ROWS,COLS=20,20; YH,YL,XH=170.0,-108.0,171.0
cx=-XH+(np.arange(COLS)+.5)*2*XH/COLS; cy=YH-(np.arange(ROWS)+.5)*(YH-YL)/ROWS
def raster(pts,rad):
    g=np.zeros((ROWS,COLS),bool)
    for (x,y) in pts:
        for r in range(ROWS):
            for c in range(COLS):
                if math.hypot(cx[c]-x,cy[r]-y)<rad: g[r,c]=True
    return ["".join("#" if v else "." for v in row) for row in g]
def path(wp,n=400):
    wp=np.array(wp,float); seg=np.hypot(*np.diff(wp,axis=0).T); d=np.r_[0,np.cumsum(seg)]
    u=np.linspace(0,d[-1],n)
    return np.c_[np.interp(u,d,wp[:,0]),np.interp(u,d,wp[:,1])],d
CHEEK=[(-112,-112),(-150,-80),(-168,-30),(-170,20)]
DOME=[(-170,20),(-166,54),(112,168)]
def seg(wp,a,b,n=120):
    P,d=path(wp,600); k=np.linspace(0,d[-1],600)
    return P[(k>=a*d[-1])&(k<=b*d[-1])]
def mirror(rows): return [r[::-1] for r in rows]
# comet: two frames up the cheek before the snare, then across the dome from the snare on
Afr=[raster(seg(CHEEK,0,.55),22),raster(seg(CHEEK,.35,1),20),
     raster(seg(DOME,0,.28),24),raster(seg(DOME,.1,.52),24),raster(seg(DOME,.32,.76),24),raster(seg(DOME,.56,1),24),raster(seg(DOME,.82,1),20)]
for i,f in enumerate(Afr):
    S["weapon_a%d"%i]=f; S["weapon_b%d"%i]=mirror(f)
# the scar it leaves: the line across the dome, growing with the comet, then hanging
Sfr=[raster(seg(DOME,.05,.28),13),raster(seg(DOME,.05,.52),13),raster(seg(DOME,.05,.76),13),raster(seg(DOME,.05,1),13)]
for i,f in enumerate(Sfr):
    S["weapon_sa%d"%i]=f; S["weapon_sb%d"%i]=mirror(f)
# the clash: both blades at once
for i in range(7):
    S["weapon_x%d"%i]=["".join("#" if (p=="#" or q=="#") else "." for p,q in zip(a,b)) for a,b in zip(Afr[i],mirror(Afr[i]))]
for i in range(4):
    S["weapon_sx%d"%i]=["".join("#" if (p=="#" or q=="#") else "." for p,q in zip(a,b)) for a,b in zip(Sfr[i],mirror(Sfr[i]))]
for k,v in S.items():
    assert len({len(r) for r in v})==1,k
open("shows/scenes/deadmau5 - Raise Your Weapon.sprites.json","w").write(json.dumps(S,indent=0))
print(len(S),"sprites")
print("\n".join(S["weapon_sa3"]))
