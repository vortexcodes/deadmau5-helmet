import json
S={}
E17="."*17
def pad(rows):
    rows=list(rows)
    return rows+[E17]*(17-len(rows))
# 17 columns over x +-171; 17 rows from y_hi 170 to y_lo -119 (17 mm a row).
# The flat-topped acacia, solid, off centre: drawn dark in front of the sun.
TREE=[
E17,
".....XXXXXXXXX...",
"...XXXXXXXXXXXXX.",
".....XX.XXX.XX...",
".......X.X.......",
"........XX.......",
"........XX.......",
".......XXXX......",
]
S["veldt_acacia"]=pad(TREE)
# The lion's head from the front, dark: round ears on top, the mass of the mane, and two slanted holes that the sun shines through.
LION=[
"....XX.....XX....",
"...XXXX...XXXX...",
"...XXXXXXXXXXX...",
"..XX...XXX...XX..",
"..XXX...X...XXX..",
"...XXXXXXXXXXX...",
"....XXX...XXX....",
".....XXXXXXX.....",
"......XXXXX......",
]
S["veldt_lion"]=pad(LION)
# The same two eyes as light, where the holes are: they arrive lit, the head comes up around them.
S["veldt_eyes"]=pad([E17,E17,E17,"....XXX...XXX....",".....XXX.XXX....."])
S["veldt_eyes_half"]=pad([E17,E17,E17,E17,".....XXX.XXX....."])
S["veldt_eyes_shut"]=pad([E17])
BL=list(LION); BL[3]="..XXXXXXXXXXXXX.."; BL[4]="..XXXXXXXXXXXXX.."
S["veldt_lion_b"]=pad(BL)
BH=list(LION); BH[3]="..XXXXXXXXXXXXX.."
S["veldt_lion_h"]=pad(BH)
def shift(row,n):
    n%=len(row)
    return row[-n:]+row[:-n] if n else row
# The tree melting in the heat: its cells go a few at a time, from the bottom up.
import random
rng=random.Random(7)
cells=[(r,c) for r,row in enumerate(TREE) for c,ch in enumerate(row) if ch!="."]
cells.sort(key=lambda rc:(-rc[0]+rng.random()*2.5))
def without(k):
    rows=[list(x) for x in TREE]
    for r,c in cells[:k]:
        rows[r][c]="."
    return pad(["".join(x) for x in rows])
n=len(cells)
for i,f in enumerate((0.25,0.5,0.75,0.92)):
    S["veldt_melt%d"%i]=without(int(n*f))
# Two eyes low in the dark, cat's slits following the jaw's own curve; they grow as he comes closer.
def low(r14,r15,r16):
    rows=[E17]*14+[r14,r15,r16]
    return rows
S["veldt_low1"]=low(E17,E17,"....XXX...XXX....")
S["veldt_low2"]=low(E17,"...X.........X...","...XXXX...XXXX...")
S["veldt_low3"]=low("..X...........X..","..XX.........XX..","...XXXX...XXXX...")
S["veldt_low_shut"]=pad([E17])
# Torn frames: whole bands of the picture slip sideways, as a bad signal does.
def tear(rows,bands):
    out=list(rows)
    for lo,hi,n in bands:
        for r in range(lo,min(hi,len(out))):
            out[r]=shift(out[r],n)
    return pad(out)
S["veldt_lion_t1"]=tear(LION,[(3,5,5)])
S["veldt_lion_t2"]=tear(LION,[(0,3,-4),(5,8,6)])
S["veldt_lion_t3"]=tear(LION,[(1,2,7),(3,4,-5),(4,6,4),(6,8,-3)])
S["veldt_acacia_t1"]=tear(TREE,[(1,3,5)])
S["veldt_acacia_t2"]=tear(TREE,[(1,2,-4),(3,6,6)])
# Vultures: two birds wheeling, wings up and wings level. Dark on the noon sun.
S["veldt_vult_a"]=pad([E17,"..XX...XX........","...XX.XX.........",".....X...........",E17,"..........XX..XX.","...........XXXX..",E17])
S["veldt_vult_b"]=pad([E17,E17,"..XXXXXXX........",".....X...........",E17,E17,"..........XXXXXX.",E17])
# The morning flock crossing the top of the sky, wings up and wings down.
S["veldt_flock_a"]=pad(["..X.X.....X.X....","...X.......X.....",".......X.X.......","........X........"])
S["veldt_flock_b"]=pad([E17,"..XXX.....XXX....",E17,".......XXX......."])
# The picture goes off: a line at the height of the eyes that closes to a dot.
def line(a):
    return pad([E17,E17,E17,("."*a+"X"*(17-2*a)+"."*a)])
for i,a in enumerate((0,1,3,5,6,7,8,8)):
    S["veldt_off%d"%i]=line(a)
S["veldt_off8"]=pad([E17])
json.dump(S,open("shows/scenes/deadmau5 - The Veldt.sprites.json","w"),indent=0)
print({k:(len(v),len(v[0]),set(len(r) for r in v)) for k,v in S.items()})
