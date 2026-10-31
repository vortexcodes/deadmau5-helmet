import json, sys, os
sys.path.insert(0, os.getcwd())
import numpy as np, mau5engine as E
P="cinema_"
D={}
# ---- leader digits: bold, on the dome.  y_lo 54, y_hi 164, x_half 80: eight rows, six columns
digits={
"8":[".####.","##..##","##..##",".####.",".####.","##..##","##..##",".####."],
"7":["######","######","....##","...##.","...##.","..##..","..##..","..##.."],
"6":[".####.","##....","##....","#####.","##..##","##..##","##..##",".####."],
"5":["######","##....","##....","#####.","....##","....##","##..##",".####."],
"4":["...##.","..###.",".####.","##.##.","######","...##.","...##.","...##."],
"3":["#####.","....##","....##",".####.","....##","....##","....##","#####."],
"2":[".####.","##..##","....##","...##.","..##..",".##...","##....","######"],
"1":["..##..",".###..","..##..","..##..","..##..","..##..","..##..",".####."],
}
for k,v in digits.items():
    D[P+"d"+k]=v
# ---- the clapper: two striped sticks across the dome, the top one hinged at the left.
#      y_lo 54, y_hi 164, x_half 160: eight rows, 24 columns
def stripe(ofs, w=3):
    return "".join("#" if ((i+ofs)//w)%2==0 else "." for i in range(24))
lower=[stripe(0),stripe(1),stripe(2)]
def stick(rows, tilt):
    """the top stick: two rows thick, rising to the right by `tilt` rows over its length"""
    g=[["."]*24 for _ in range(rows)]
    for i in range(24):
        lift=int(round(tilt*i/23.0))
        for t in range(2):
            r=rows-1-lift-(1-t)
            if 0<=r<rows and ((i+t)//3)%2==0:
                g[r][i]="#"
    return ["".join(x) for x in g]
D[P+"clap_o"]=stick(5,3)+lower
D[P+"clap_h"]=stick(5,1.5)+lower
D[P+"clap_c"]=stick(5,0)+lower
# ---- the little mau5 who walks across the silent screen, a walking mau5head:
#      y_lo 54, y_hi 164, x_half 64, 8 rows, 8 cols
hd=["##....##","###..###",".######.",".#.##.#.",".######.","..####.."]
D[P+"walk1"]=hd+["..#..#..",".##..##."]
D[P+"walk2"]=hd+[".#....#.","##....##"]
D[P+"walk3"]=hd+["..#..#..","..#..#.."]
D[P+"walk4"]=hd+["...##...","...##..."]
# ... and smaller as he walks away down the road, at the same place on the same canvas
D[P+"far1"]=["........","........",".#....#.","..####..","..#..#..","..####..","..#..#..","........"]
D[P+"far2"]=["........","........",".#....#.","..####..","..#..#..","..####..","...##...","........"]
D[P+"far3"]=["........","........","........",".#....#.","..####..","..####..","...##...","........"]
D[P+"far4"]=["........","........","........","........","..#..#..","...##...","........","........"]
# ---- the first film: a galloping horse.  y_lo 54, y_hi 164, x_half 110: 8 rows, 18 cols
D[P+"horse1"]=[
"..............##..",
".............####.",
"....########.##.##",
".###############..",
".###############..",
"##.##########.....",
"#...##....###.....",
"....#.......##....",
]
D[P+"horse2"]=[
"..............##..",
".............####.",
".#..########.##.##",
"################..",
".###############..",
"...##########.....",
"...###...####.....",
"..##.......#.##...",
]
D[P+"horse3"]=[
"..............##..",
".............####.",
"#...########.##.##",
".###############..",
"..##############..",
"...##########.....",
"....##...###......",
"....##...###......",
]
D[P+"horse4"]=[
"..............##..",
".............####.",
"#...########.##.##",
".###############..",
"..##############..",
"...##########.....",
"..##.##..##.##....",
".##...##.##..##...",
]
# ---- the train that arrives on the rolling bass: y_lo 54, y_hi 164, 12 mm a column
def train(k):
    loco=[
"....##.......####...",
"....##.......####...",
"...####......####...",
"..##################",
"..##################",
".###################",
"####################",
]
    car=[
"....................",
"....................",
".##################.",
".#...#...#...#...##.",
".#...#...#...#...##.",
".##################.",
".##################.",
]
    rows=[loco[i]+"."+car[i]+"."+car[i] for i in range(7)]
    w=len(rows[0])
    wheel="".join(("#" if ((i+k)%4)<2 else ".") if ((i<20) or (i%21>2 and i%21<18)) else "." for i in range(w))
    return rows+[wheel]
D[P+"train1"]=train(0); D[P+"train2"]=train(1); D[P+"train3"]=train(2); D[P+"train4"]=train(3)
# ---- a chorus line of three smaller mau5s, kicking, kept inside the dome's shoulders:
#      y_lo 54, y_hi 150, x_half 165, 7 rows, 22 cols
def chorus(leg):
    fig=["#....#","##..##",".####.",".#..#.",".####.","..##.."]+[leg]
    return ["..".join([fig[r]]*3) for r in range(7)]
D[P+"line1"]=chorus(".#..#.")
D[P+"line2"]=chorus("##..##")
# ---- the moon, who is about to get a rocket in the eye: y_lo 54, y_hi 164, x_half 62: 8 rows, 9 cols
D[P+"moon"]=[
"..#####..",
".#######.",
"###.#.###",
"#########",
"#########",
"##.....##",
".#######.",
"..#####..",
]
D[P+"moonhit"]=[
"..#####..",
".#######.",
"###.#####",
"#####.###",
"####.####",
"###...###",
".#######.",
"..#####..",
]
# ---- marquee bulbs round the frame of the dome, three frames, sprite canvas = whole shell
h=E.Helmet()
s=np.where(h.shell)[0]
ylo,yhi,xh=-112.0,170.0,172.0
cell=8.0
rows=int((yhi-ylo)/cell); cols=int(2*xh/cell)
# the outer edge of the dome: for each LED, is it the outermost of its row?
dome=s[h.py[s]>26]
edge=[]
for y in np.unique(np.round(h.py[dome])):
    r=dome[np.round(h.py[dome])==y]
    edge += [r[np.argmin(h.px[r])], r[np.argmax(h.px[r])]]
top=dome[h.py[dome]>=145]
# add the top line of the dome by columns
for x in np.unique(np.round(h.px[top]/12.5)):
    c=top[np.round(h.px[top]/12.5)==x]
    edge.append(c[np.argmax(h.py[c])])
edge=np.unique(edge)
ang=np.arctan2(h.py[edge]-57,h.px[edge])
edge=edge[np.argsort(ang)]
frames=[]
for k in range(3):
    g=[["."]*cols for _ in range(rows)]
    for j,i in enumerate(edge):
        if j%3==k:
            r=int((yhi-h.py[i])/cell); c=int((h.px[i]+xh)/cell)
            g[min(r,rows-1)][min(c,cols-1)]="#"
    frames.append(["".join(x) for x in g])
    D[P+"bulb%d"%k]=frames[-1]
print("bulbs",len(edge),"canvas",rows,cols)
json.dump(D,open("shows/scenes/deadmau5 - Strobe (Special Features Remix).sprites.json","w"),indent=0)
print(len(D))
