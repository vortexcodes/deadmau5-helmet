import json, sys
KIT="tools/showkit"
sys.path.insert(0, KIT)
from fmt import save
BASE="deadmau5 - The Veldt"
SPB=0.468725
SP={"y_lo":-119,"y_hi":170,"x_half":171}
DARK=[6,3,0]          # brighter than 4, so "over" paints it: a true silhouette in front of whatever is behind
EYE=[255,50,0]        # a saturated amber: the guard's soft ceiling pushes colours toward yellow, so start red of where it should land
E8=round(2.0/SPB,5)   # flip-book frames a second for one frame an 8th note

# ---- the chord loop: 8 bars, always the same, measured from the bass line. One step per beat: which tube each new chord fires,
# low chord low tube, high chord high tube. "." is no new chord.
LOOP=[ "1","0",".",".",   "1","2",".",".",   "2","2",".","0",   ".",".",".",".",
       "1","2",".",".",   "1","1","2",".",   "2","2",".","0",   ".",".",".","." ]
def chords(bar, gain, c=0.45, ctip=0.95, pal=None, on="tubes", rise=0.22, keep=0.1, decay=1.2, rim=0.0, env=None):
    """Blades playing the chord changes, phase-locked to the song's 8-bar loop from a scene starting at `bar`."""
    k=int(round(bar*4))%32
    r=LOOP[k:]+LOOP[:k]
    seq=[x if x!="." else "1" for x in r]
    pat="".join("x" if x!="." else "." for x in r)
    L={"fx":"blades","on":on,"seq":seq,"step":1,"rise":rise,"keep":keep,"c":c,"ctip":ctip,"rim":rim,"gain":gain,
       "gate":{"pat":pat,"step":1,"decay":decay}}
    if pal: L["pal"]=pal
    if env: L["env"]=env
    return L
GR={"band":"mid","lo":0.03,"hi":0.24}
IN1={"in":1}          # ears dark on the first beat of a drop: that beat belongs to the shell

tr={"v":1,"show":BASE,"lead":0,
"about":"",
"marks":{"sunrise":4,"kick":8,"tree":16,"heat":24,"cool":28,"stalk":32,"open":45,"pride":48,"noon":56,"sunset":61,"night":64,"closer":68,"dawn":70,"gone":71,"day2":72,"flick":76,"gold":80,"tear":84,"title":85,"off":88},
"palettes":{
 "sun":[[0,0,0],[70,10,0],[190,55,0],[255,115,6],[255,165,20]],
 "hot":[[0,0,0],[90,8,0],[220,40,0],[255,80,0],[255,125,10]],
 "noon":[[0,0,0],[120,45,0],[255,145,25],[255,215,120]],
 "sky":[[255,130,20],[200,60,20],[110,16,50],[36,4,60]],
 "grass":[[0,0,0],[18,22,0],[70,90,0],[150,170,15],[225,230,70]],
 "mane":[[0,0,0],[90,20,0],[190,70,0],[245,130,8],[255,195,60]],
 "ray":[[0,0,0],[90,40,0],[230,130,10],[255,210,90]],
 "bird":[[255,190,110],[255,235,190],[255,255,255]],
 "night":[[0,0,0],[2,3,16],[6,10,44],[18,28,90]],
 "star":[[0,0,0],[110,130,200],[225,235,255]],
 "leo":[[0,0,0],[60,70,0],[170,205,20],[230,255,90]],
 "cyan":[[0,0,0],[0,50,70],[0,170,210],[120,255,255]],
 "scan":[[0,0,0],[0,0,0],[0,0,0],[0,30,44],[0,190,225]]},
"motifs":{
 "sun":{"fx":"orb","on":"shell","x":0,"y":108,"rad":200,"soft":70,"c":0.92,"cgrad":-0.5,"pal":"sun","gain":0.14},
 "sky":{"fx":"grad","on":"shell","axis":"y","axis2":"x","scale":0.5,"lo":0,"hi":1,"pal":"sky","gain":0.05},
 "tree":{"fx":"preset","name":"sprite","on":"shell","mix":"over","gain":1,"params":dict(SP,sprite="veldt_acacia",color=DARK)},
 "lion":{"fx":"preset","name":"sprite","on":"shell","mix":"over","gain":1,"params":dict(SP,sprite="veldt_lion",color=DARK)},
 "eyes":{"fx":"preset","name":"sprite","on":"shell","mix":"over","gain":0.9,"params":dict(SP,sprite="veldt_eyes",color=EYE)},
 "jawgrass":{"fx":"grad","on":"jaw","axis":"x","axis2":"y","scale":5,"speed":0.12,"warp":0.22,"wscale":2.5,"wspeed":0.2,"lo":0,"hi":0.85,"pal":"grass","gain":0.13},
 "grass":{"fx":"grad","on":"tubes","axis":"al","axis2":"x","scale":2.2,"speed":-0.3,"warp":0.45,"wscale":1.5,"wspeed":0.1,"lo":0,"hi":0.85,"pal":"grass","gain":GR},
 "roots":{"fx":"sweep","on":"tubes","axis":"al","shape":"p","mode":"fill","from":0.3,"to":0.3,"soft":0.28,"pal":"grass","c":0.8,"gain":0.2,"gate":{"pat":"x...","step":0.25,"decay":0.6}},
 "clap":{"fx":"fill","on":"rims","pal":"sun","c":0.85,"gain":0.5,"gate":{"pat":".x.x","step":1,"decay":0.5}},
 "birds":{"fx":"sparks","on":"rims","rate":1.5,"life":0.5,"nbr":0,"loop":24,"seed":5,"pal":"bird","c":0.3,"spread":0.6,"gain":0.8},
 "birdsf":{"fx":"sparks","on":"face","rate":0.75,"life":0.45,"nbr":0.15,"loop":16,"seed":9,"pal":"bird","c":0.3,"spread":0.6,"gain":0.5},
 "stars":{"fx":"twinkle","on":"face","rate":0.22,"sharp":8,"dens":0.5,"seed":3,"pal":"star","c":0.8,"spread":0.2,"gain":0.6},
 "starsr":{"fx":"twinkle","on":"rims","rate":0.18,"sharp":6,"dens":0.8,"seed":7,"pal":"star","c":0.8,"spread":0.2,"gain":0.5},
 "dark":{"fx":"grad","on":"face","axis":"y","axis2":"x","scale":0.5,"lo":0,"hi":1,"pal":"night","gain":0.06},
 "scan":{"fx":"grad","on":"shell","axis":"y","axis2":"x","scale":7,"speed":0.25,"wave":"saw","lo":0,"hi":1,"pal":"scan","gain":0.6},
 "line":{"fx":"sweep","on":"shell","axis":"y","shape":"p","mode":"band","from":0.42,"to":1.03,"width":0.07,"pal":"cyan","c":0.85,"gain":0.8},
 "burst":{"fx":"orb","on":"shell","x":0,"y":105,"rad":[60,420],"soft":110,"c":0.8,"cgrad":-0.25,"pal":"sun","gain":[0.45,0.1]},
 "wave":{"fx":"sweep","on":"tubes","axis":"al","shape":"p","mode":"band","from":-0.1,"to":1.25,"width":0.45,"pal":"sun","c":0.95,"gain":0.35},
 "fill":{"fx":"sweep","on":"tubes","axis":"al","shape":"p","mode":"fill","from":-0.1,"to":1.15,"soft":0.3,"pal":"mane","c":0.5,"cgrad":0.45,"gain":0.17}},
"scenes":[]}
S=tr["scenes"].append
PUMP={"pat":"x...","step":0.25,"depth":0.18,"decay":0.5}
HARD=dict(PUMP,depth=0.28)
BROKEN={"pat":"x..x..x.x.x..x..","step":0.25,"depth":0.3,"decay":0.3}

# ---- the nursery wakes
S({"name":"dawn","from":0,"to":"sunrise","pal":"sun","layers":[
  {"use":"sky","gain":[0.02,0.06]},
  {"use":"sun","y":[-225,-95],"rad":125,"soft":75,"c":[0.45,0.62],"cgrad":-0.2,"gain":[0.3,0.42]},
  {"use":"birds"},{"use":"birdsf"},
  chords(0,[0.05,0.14],pal="grass")]})
S({"name":"sunrise","from":"sunrise","to":"kick","pal":"sun","out":0.5,"layers":[
  {"use":"sky","gain":[0.06,0.08]},
  {"use":"sun","y":[-95,60],"rad":[125,140],"soft":75,"c":[0.62,0.88],"cgrad":-0.25,"gain":[0.42,0.26]},
  {"use":"birds","gain":[0.8,0.5]},
  {"fx":"preset","name":"sprite","on":"shell","mix":"over","gain":0.4,"env":{"in":2,"out":2},"params":dict(SP,sprite="veldt_flock_a|veldt_flock_b",rate=E8,color=[255,225,150],dx=-240,vx=68)},
  {"use":"grass","hi":[0.25,0.7],"gain":[0.03,0.15]},
  chords(4,[0.14,0.28],pal="grass")]})
# ---- the kick: the plain by day. A disc of sun, grass in the jaw and the ears, and the ears play the chord changes.
PLAINSUN={"use":"sun","y":112,"rad":118,"soft":46,"c":0.97,"cgrad":-0.5,"gain":0.2}
S({"name":"plain","from":"kick","to":"tree","pal":"sun","pump":PUMP,"layers":[
  PLAINSUN,{"use":"jawgrass"},dict({"use":"grass"},env=IN1),dict({"use":"roots"},env=IN1),chords(8,0.3,pal="grass",env=IN1)]})
# ---- the acacia against the sun
S({"name":"acacia","from":"tree","to":"heat","pal":"sun","pump":PUMP,"layers":[
  {"use":"sun"},{"use":"tree"},{"use":"jawgrass","gain":0.1},{"use":"grass"},{"use":"roots"},chords(16,0.3,pal="grass")]})
# ---- the long note: heat. The tree wavers, then melts into the light; the ears fill and drain with the note.
HAZE={"fx":"grad","on":"face","axis":"y","axis2":"x","scale":3.5,"speed":-0.18,"warp":0.25,"wscale":2.2,"wspeed":0.33,"lo":0,"hi":0.9,"pal":"hot"}
MELT="|".join(["veldt_acacia"]*3+["veldt_melt0","veldt_melt1","veldt_melt2","veldt_melt3","veldt_off8"])
S({"name":"heatup","from":"heat","to":"cool","pal":"hot","pump":PUMP,"layers":[
  {"use":"sun","pal":"hot","rad":[200,290],"gain":[0.14,0.09]},
  dict(HAZE,gain=[0.01,0.08]),
  {"use":"tree","params":dict(SP,sprite=MELT,rate=round(E8/4,5),color=DARK,wx=14,wy=3,wf=1.4)},
  {"use":"fill"},{"use":"roots","pal":"mane","gain":0.16},{"use":"clap","pal":"hot"}]})
S({"name":"heat","from":"cool","to":"stalk","pal":"hot","pump":PUMP,"layers":[
  {"use":"sun","pal":"hot","rad":[290,200],"gain":[0.09,0.14]},
  dict(HAZE,gain=[0.08,0.01]),
  {"use":"jawgrass","gain":[0,0.1]},
  {"use":"fill","from":1.15,"to":-0.1},{"use":"roots","pal":"mane","gain":0.16},{"use":"clap","pal":"hot"}]})
# ---- something rises out of the grass: the head comes up in front of the sun, a row every two bars, and the grass goes still
VY=120.0/(13*4*SPB)
S({"name":"stalk","from":"stalk","to":"open","pal":"sun","pump":PUMP,"layers":[
  {"use":"sun","y":105,"rad":230,"soft":90,"c":[0.92,0.78],"cgrad":-0.45,"gain":[0.12,0.16]},
  {"use":"lion","params":dict(SP,sprite="veldt_lion",color=DARK,dy=-120,vy=round(VY,4))},
  {"use":"jawgrass","gain":[0.12,0.07]},{"use":"grass","hi":[0.85,0.6],"gain":{"band":"mid","lo":0.02,"hi":0.16}},{"use":"roots","gain":0.15},chords(32,[0.28,0.16],pal="grass")]})
# ---- the eyes ignite, and the ears fill with the long note
def lionflip(tears,n=32,blink=True):
    """Parallel flip books, one 8th a frame: the dark head, and the eyes lit in its holes. A slow blink every 4 bars; a torn frame loses its eyes."""
    a=["veldt_lion"]*n; b=["veldt_eyes"]*n
    if blink:
        a[10],b[10]="veldt_lion_h","veldt_eyes_half"
        a[11],b[11]="veldt_lion_b","veldt_eyes_shut"
        a[12],b[12]="veldt_lion_h","veldt_eyes_half"
    for i,t in tears.items():
        a[i],b[i]=t,"veldt_eyes_shut"
    return "|".join(a),"|".join(b)
def lion(tears=None,blink=True,eyeg=0.9,color=EYE):
    a,b=lionflip(tears or {},blink=blink)
    return [{"use":"lion","params":dict(SP,sprite=a,rate=E8,color=DARK)},{"use":"eyes","gain":eyeg,"params":dict(SP,sprite=b,rate=E8,color=color)}]
S({"name":"open","from":"open","to":"pride","pal":"sun","pump":PUMP,"out":0.25,"layers":[
  {"use":"sun","rad":[220,280],"soft":90,"gain":[0.16,0.2]},
  {"use":"lion"},{"use":"eyes","gain":[0.12,0.9]},{"use":"jawgrass","gain":[0.07,0.12]},
  {"use":"fill"},{"use":"roots","pal":"mane","gain":0.16}]})
# ---- the pride: the lion in front of the sun, his mane in the ears
MANE={"use":"grass","pal":"mane","hi":0.95,"scale":1.6,"speed":-0.5,"gain":0.2,"env":IN1}
BLADE={"fx":"blades","on":"tubes","seq":["012"],"step":1,"rise":0.12,"keep":0,"pal":"mane","c":0.6,"ctip":1,"rim":0.7,"gain":0.3,"gate":{"pat":".x.x","step":1,"decay":0.75},"env":IN1}
S({"name":"pride","from":"pride","to":"noon","pal":"sun","pump":HARD,"layers":[
  {"use":"sun","rad":270,"soft":90,"gain":0.19}]+lion()+[{"use":"jawgrass","gain":0.14},MANE,BLADE]})
# ---- noon: a small white sun at the top of the sky, and the vultures wheeling in front of it. The ears are its rays.
S({"name":"noon","from":"noon","to":"sunset","pal":"noon","pump":HARD,"layers":[
  {"fx":"orb","on":"shell","x":0,"y":120,"rad":92,"soft":30,"c":0.92,"cgrad":-0.5,"pal":"noon","gain":0.24},
  {"fx":"preset","name":"sprite","on":"shell","mix":"over","gain":1,"params":dict(SP,sprite="veldt_vult_a|veldt_vult_b",rate=round(E8/2,5),color=DARK,dy=-5,wx=46,wy=12,wf=0.21)},
  {"use":"jawgrass","gain":0.08},
  {"fx":"grad","on":"tubes","axis":"al","axis2":"x","scale":1.3,"speed":-0.5,"lo":0,"hi":1,"pal":"ray","gain":0.18},
  chords(56,0.34,pal="noon",c=0.5,ctip=1),{"use":"clap","pal":"noon","c":1,"gain":0.5}]})
# ---- sundown: the swell into the breakdown, the sun sinking behind him
S({"name":"sundown","from":"sunset","to":"night","pal":"sun","pump":PUMP,"layers":[
  {"use":"sky","gain":[0.03,0.08],"lo":0.3,"hi":1},
  {"use":"sun","y":[110,-165],"rad":[220,130],"soft":90,"c":[0.95,0.5],"cgrad":-0.3,"gain":[0.2,0.3]},
  {"use":"lion","gain":{"sunset":1,"62.5":0}},
  {"use":"fill","from":1.15,"to":-0.1},
  {"use":"roots","pal":"mane","gain":[0.2,0.06]},{"use":"clap","gain":[0.5,0.08]}]})
# ---- night: stars, and two eyes low in the dark that come closer: they brighten, grow and spread along the jaw
def blink(base,steps,at):
    """Gain keys: base steps at the given bars, and a short shut at each bar in `at`."""
    k={str(b):v for b,v in steps}
    def val(x):
        v=None
        for b,g in steps:
            if b<=x: v=g
        return v
    for a in at:
        k[str(a)]=0
        k[str(round(a+0.06,3))]=val(a+0.06)
    return k
def eye(side,rad,gain,x,y=-104,c=0.72):
    xr=[side*x[0],side*x[1]]
    return {"fx":"orb","on":"jaw","x":xr,"y":y,"rad":rad,"soft":round(rad*0.6,1),"wx":7,"xf":0.0625,"c":c,"cgrad":-0.3,"pal":"leo","gain":gain}
G1=blink(0,[(64,0),(65,0.3),(66,0.45),(67,0.6)],[66.75,67.25])
G2=blink(0,[(68,0.75),(69,0.95)],[69.5])
G3=blink(0,[(70,1.0)],[70.5])
S({"name":"night","from":"night","to":"closer","pal":"night","layers":[
  {"use":"dark"},{"use":"stars","env":{"in":2}},{"use":"starsr","env":{"in":3}},
  eye(-1,36,G1,(80,88)),eye(1,36,G1,(80,88))]})
S({"name":"closer","from":"closer","to":"dawn","pal":"night","layers":[
  {"use":"dark"},{"use":"stars"},{"use":"starsr"},
  eye(-1,44,G2,(88,108),c=0.82),eye(1,44,G2,(88,108),c=0.82),
  {"use":"grass","pal":"night","hi":1,"gain":0.3,"speed":-0.15}]})
S({"name":"prowl","from":"dawn","to":"gone","pal":"night","layers":[
  {"use":"dark","gain":[0.06,0.03]},{"use":"stars","gain":[0.6,0.3]},
  eye(-1,50,G3,(108,132),-88,0.95),eye(1,50,G3,(108,132),-88,0.95),
  {"fx":"blades","seq":["0","1","2","012"],"step":1,"rise":0.25,"keep":0.3,"pal":"leo","c":0.3,"ctip":0.8,"gain":[0.08,0.24]}]})
S({"name":"gone","from":"gone","to":"day2","pal":"night","out":0.25,"layers":[
  {"use":"stars","gain":[0.3,0.12]},
  {"fx":"sweep","on":"tubes","axis":"al","shape":"p","mode":"fill","from":-0.1,"to":1.1,"soft":0.15,"pal":"leo","c":0.3,"cgrad":0.5,"gain":[0.08,0.28]}]})
# ---- day again, too bright: the sun floods, and he is standing there when it clears
S({"name":"day2","from":"day2","to":"flick","pal":"sun","pump":HARD,"layers":[
  {"use":"sun","pal":"hot","rad":270,"soft":90,"gain":0.21}]+lion()+[{"use":"jawgrass","gain":0.14},MANE,BLADE]})
# ---- something is wrong with the sun
JUMPX={"76":0,"76.5":70,"76.625":0,"77.5":-90,"77.75":0,"78.25":60,"78.375":-40,"78.5":0,"79":90,"79.25":-70,"79.5":30,"79.75":0}
def flip(base,tears,n):
    """n frames of an 8th each: the plain sprite, except the torn ones at the given positions."""
    return "|".join(tears.get(i,base) for i in range(n))
TREEFLIP=flip("veldt_acacia",{9:"veldt_acacia_t1",17:"veldt_acacia_t1",18:"veldt_acacia_t2",25:"veldt_acacia_t2",26:"veldt_acacia_t1",27:"veldt_acacia_t2",30:"veldt_acacia_t1"},32)
S({"name":"flicker","from":"flick","to":"gold","pal":"sun","pump":PUMP,"layers":[
  {"use":"sun","x":JUMPX},
  {"use":"tree","params":dict(SP,sprite=TREEFLIP,rate=E8,color=DARK)},
  {"use":"jawgrass","gain":0.1},{"use":"grass"},{"use":"roots"},chords(76,0.3,pal="grass")]})
# ---- all of it, once more, and the picture has started to tear. This time the first beat belongs to the ears.
S({"name":"gold","from":"gold","to":"tear","pal":"sun","pump":HARD,"layers":[
  {"use":"sun","rad":{"band":"bass","punch":True,"lo":240,"hi":300},"soft":90,"gain":0.22,"env":IN1}]+lion({13:"veldt_lion_t1",21:"veldt_lion_t2",22:"veldt_lion_t1",28:"veldt_lion_t3",29:"veldt_lion_t2",30:"veldt_lion_t3",31:"veldt_lion_t1"},blink=False)+[{"use":"jawgrass","gain":0.16,"env":IN1},dict(MANE,gain=0.24),dict(BLADE,gain=0.36)]})
# ---- it was never real
JUMP2={}
for i in range(32):
    JUMP2[str(84+i/8.0)]=[0,120,-80,40,-140,90,-30,150][(i*5)%8]
STUTTER={"pat":"x..x..x.x.x..x..","step":0.25,"decay":0.2}
TORN=flip("veldt_lion_t1",{1:"veldt_lion_t3",2:"veldt_lion_t2",4:"veldt_lion_t3",5:"veldt_lion",6:"veldt_lion_t2",7:"veldt_lion_t3"},8)
CBL={"fx":"blades","seq":["0","1","2"],"step":0.5,"side":"alt","rise":0.3,"keep":0,"pal":"cyan","c":0.6,"ctip":1}
RIMN={"fx":"twinkle","on":"rims","rate":1,"sharp":3,"dens":0.8,"pal":"cyan","c":0.8,"gain":0.5}
S({"name":"tear","from":"tear","to":"title","pal":"cyan","pump":BROKEN,"layers":[
  {"use":"sun","x":JUMP2,"gain":0.2,"rad":170,"soft":60},
  {"use":"lion","params":dict(SP,sprite=TORN,rate=E8,color=DARK)},
  {"use":"scan","gain":0.28},
  {"use":"grass","gain":0.2,"gate":STUTTER},
  dict(CBL,gain=0.3),RIMN]})
S({"name":"static","from":"title","to":"off","pal":"cyan","pump":BROKEN,"layers":[
  {"use":"sun","on":"face","x":JUMP2,"gain":{"85":0.12,"86":0.08,"87":0.04},"rad":110,"soft":40},
  {"use":"scan","on":"jaw","gain":[0.5,0.9]},
  {"use":"scan","on":"face","gain":[0.05,0.12]},
  {"use":"grass","gain":{"85":0.2,"86":0.1,"87":0},"gate":STUTTER},
  dict(CBL,gain=[0.34,0.7]),RIMN]})
BURST=lambda name,at,gain=0.45,pal="sun":{"name":name,"at":at,"beats":2,"pal":pal,"layers":[{"use":"burst","pal":pal,"gain":[gain,0.08]}]}
WAVE=lambda name,at,g=0.35,pal="sun":{"name":name,"at":at,"beats":1.5,"layers":[{"use":"wave","pal":pal,"gain":g}]}
LINE=lambda name,at,beats=1,gain=0.8:{"name":name,"at":at,"beats":beats,"layers":[{"use":"line","gain":gain}]}
OFF="|".join("veldt_off%d"%i for i in range(9))
HITS=[BURST("KICK","kick"),WAVE("KICK2",8.25),
 LINE("flaw",40.75,1,0.22),
 BURST("PRIDE","pride"),WAVE("PRIDE2",48.25),
 {"name":"SWITCH","at":"night","beats":2,"layers":[{"fx":"preset","name":"sprite","on":"shell","gain":[0.35,0.15],"params":dict(SP,sprite="veldt_off0|veldt_off2|veldt_off4|veldt_off8",rate=E8,color=[120,255,255])}]},
 {"name":"LEAP","at":71.5,"beats":1.75,"layers":[{"fx":"preset","name":"sprite","on":"shell","gain":[0.5,1.0],"params":dict(SP,sprite="veldt_eyes",color=[170,255,0])}]},
 BURST("DAY2","day2",0.6,"hot"),WAVE("DAY22",72.25,0.45,"hot"),
 LINE("flaw2",76.5,1,0.5),LINE("flaw3",77.5,1,0.5),LINE("flaw4",78.25,0.5,0.6),LINE("flaw5",79,0.5,0.6),LINE("flaw6",79.5,0.5,0.7),
 # the top of the song: the ears blaze on the first beat and the shell waits for them
 {"name":"GOLD","at":"gold","beats":2,"layers":[{"fx":"fill","on":"tubes","pal":"sun","c":1,"gain":[0.75,0]},{"fx":"fill","on":"rims","pal":"sun","c":1,"gain":[0.9,0]}]},
 LINE("flaw7",81.5,0.5,0.7),LINE("flaw8",83,0.5,0.7),LINE("flaw9",83.5,0.5,0.8),
 {"name":"THE VELDT","at":"tear","beats":16,"layers":[{"fx":"preset","name":"text","on":"face","fit":True,"mix":"over","params":{"text":"THE VELDT","color":[70,235,255]}}]},
 {"name":"OFF","at":"off","beats":4.5,"layers":[{"fx":"preset","name":"sprite","on":"shell","gain":[1.0,0.6],"params":dict(SP,sprite=OFF,rate=E8,color=[150,255,255])}]}]
# The track's own bird cries: the high flurries in its first half. Each one is a bright spark darting across the top of the sky, with a flutter on the rims.
CRIES=[8.5,9,9.25,9.5,9.875,10,10.25, 12.25,12.5,12.75, 14.125,14.75, 16.375,16.5,17,18,18.75, 21,21.25,21.625,22,23.75,
       33,33.25,34,34.25,34.75, 36.25,36.5,37,37.25,38,38.25,38.5,38.75, 40.375,41,41.25,42,42.25,42.625,42.75,43.125, 44.5,45,45.25,45.625,46,47.75]
def cry(at,i):
    a,b=(-150,150) if i%2 else (150,-150)
    return {"name":"cry","at":at,"beats":0.75,"layers":[
      {"fx":"orb","on":"shell","x":[a,b],"y":150,"rad":26,"soft":16,"pal":"bird","c":0.7,"gain":[1.0,0.4]},
      {"fx":"sparks","on":"rims","rate":10,"life":0.4,"nbr":0,"seed":round(at*7,3),"pal":"bird","c":0.5,"gain":0.8}]}
HITS+=[cry(a,i) for i,a in enumerate(CRIES)]
# The noise accent that comes round every four bars: a shock up the ears and a flash of the rims.
def flare(at,pal="sun",g=0.2):
    return {"name":"flare","at":at,"beats":1,"pal":pal,"layers":[{"use":"wave","pal":pal,"gain":g,"width":0.3},{"fx":"fill","on":"rims","pal":pal,"c":0.95,"gain":[0.7,0]}]}
for b in (26,30): HITS+=[flare(b+0.25,"hot"),flare(b+1,"hot")]
for b in (50,54,62): HITS+=[flare(b+0.25),flare(b+1)]
HITS+=[flare(58.25,"noon"),flare(59,"noon")]
HITS+=[flare(74.25,"hot"),flare(75,"hot"),flare(82.25)]
HITS+=[flare(86.25,"cyan",0.35),flare(87,"cyan",0.35)]
# The roar: once in the first big section, once in the last. The mouth opens along the jaw and the eyes go white-hot.
def roar(at):
    return {"name":"ROAR","at":at,"beats":4,"pal":"hot","layers":[
      {"fx":"orb","on":"jaw","mix":"over","x":0,"y":-112,"rad":[20,200],"soft":50,"pal":"hot","c":0.8,"cgrad":-0.5,"gain":[0.5,0.2]},
      {"fx":"preset","name":"sprite","on":"shell","mix":"over","gain":[1.0,0.5],"params":dict(SP,sprite="veldt_eyes",color=[255,170,60])}]}
HITS+=[roar(55),roar(83)]
tr["hits"]=HITS
tr["about"]=open(KIT+"/work/veldt/about.txt").read().strip()
save(tr, "shows/scenes/%s.scene.json"%BASE)
