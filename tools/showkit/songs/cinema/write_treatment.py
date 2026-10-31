import sys, os
KIT="tools/showkit"
sys.path.insert(0, KIT)
from fmt import save
SPB=0.46875
BAR=4*SPB
BASE="deadmau5 - Strobe (Special Features Remix)"

def stops(n, table):
    """A palette that is black or flat where it needs to be: `table` is [(pos, rgb), ...]; n even stops."""
    out=[]
    for i in range(n):
        c=i/(n-1)
        for (a,ca),(b,cb) in zip(table,table[1:]):
            if a<=c<=b:
                f=(c-a)/(b-a) if b>a else 0
                out.append([int(round(x+(y-x)*f)) for x,y in zip(ca,cb)])
                break
    return out

K=[0,0,0]
pal={
 "silver":[K,[22,24,28],[85,90,100],[185,190,200],[245,248,255]],
 "sepia":[K,[42,18,4],[125,70,22],[210,150,80],[255,226,170]],
 # the clock hand on the leader: bright at the hand itself, gone by a third of the way round
 "hand":stops(13,[(0,[235,238,245]),(0.06,[120,124,135]),(0.34,[20,21,24]),(0.55,K),(1,K)]),
 # sprocket holes: hard bright holes in black film
 "holes":stops(9,[(0,K),(0.45,K),(0.7,[230,232,240]),(1,[255,255,255])]),
 "holesgold":stops(9,[(0,K),(0.45,K),(0.7,[255,170,30]),(1,[255,225,120])]),
 # a frame line rolling through the picture
 "frame":stops(11,[(0,K),(0.2,K),(0.32,[120,70,22]),(0.7,[200,140,75]),(1,[255,215,150])]),
 # the burn: black in the hole, white hot at its edge, then scorched brown, then the frame itself
 "burn":stops(41,[(0,K),(0.42,K),(0.47,[120,10,0]),(0.5,[255,230,180]),(0.53,[255,140,20]),(0.6,[110,40,5]),(0.66,[120,70,22]),(1,[210,150,80])]),
 "lamp":[K,[70,44,20],[210,150,85],[255,235,195]],
 # technicolor
 "dye":{"stops":[[235,0,35],[255,120,0],[255,205,0],[0,190,60],[0,70,230],[175,0,165]],"wrap":True},
 "velvet":{"stops":[[35,0,5],[150,0,20],[255,15,30],[150,0,20]],"wrap":True},
 "petal":{"stops":[[255,175,0],[255,30,80],[150,0,170],[10,0,40],[150,0,170],[255,30,80]],"wrap":True},
 "ruby":[K,[80,0,10],[215,0,35],[255,70,60]],
 "gold":[K,[110,50,0],[240,150,0],[255,220,70]],
 "emerald":[K,[0,60,25],[0,180,70],[110,255,140]],
 "cobalt":[K,[0,8,50],[0,35,150],[30,100,255]],
 "rose":[K,[90,0,40],[240,30,110],[255,150,190]],
 "red":stops(9,[(0,K),(0.3,K),(1,[255,0,20])]),
 "green":stops(9,[(0,K),(0.3,K),(1,[0,255,40])]),
 "blue":stops(9,[(0,K),(0.3,K),(1,[20,40,255])]),
 # the hand tints of a silent picture
 "amber":[K,[60,26,0],[180,95,0],[255,180,50]],
 "tintblue":[K,[0,18,50],[20,75,150],[150,195,250]],
 "white":[[255,200,120],[255,235,190],[255,255,255]],
}

DIGIT={"y_lo":54,"y_hi":164,"x_half":80}
FIG={"y_lo":54,"y_hi":164,"x_half":64}
BULB={"y_lo":-112,"y_hi":170,"x_half":172}
CLAP={"y_lo":54,"y_hi":164,"x_half":160}
HORSE={"y_lo":54,"y_hi":164,"x_half":110}
TRAIN={"y_lo":54,"y_hi":164,"x_half":372}
LINE={"y_lo":54,"y_hi":150,"x_half":150}
MOON={"y_lo":54,"y_hi":164,"x_half":62}
WALK="cinema_walk1|cinema_walk2|cinema_walk3|cinema_walk4"
LEGS=2/SPB    # a new leg position every 8th note

motifs={
 # the two ears are the projector's two reels, and both turn clockwise, as they do
 "reel":{"fx":"grad","on":"tubes","axis":"a","scale":3,"speed":0.125,"lo":0,"hi":1,"pal":"silver","gain":0.14},
 # sprocket holes running round the rims like film through the gate
 "sprocket":{"fx":"grad","on":"rims","axis":"a","scale":6,"speed":0.5,"pal":"holes","gain":0.45},
 # the same holes carrying the kick
 "sprokick":{"fx":"grad","on":"rims","axis":"a","scale":6,"speed":1,"pal":"holes","gain":0.6,"gate":{"pat":"x","step":1,"decay":0.7,"floor":0.35}},
 # the picture: a vignette that weaves a little in the gate
 "vignette":{"fx":"orb","on":"shell","x":0,"y":125,"rad":215,"soft":175,"wx":5,"wy":4,"xf":0.5,"yf":0.75,"c":0.75,"gain":0.08},
 "grain":{"fx":"twinkle","on":"shell","rate":2,"sharp":7,"dens":0.55,"spread":0.25,"c":0.7,"seed":5,"gain":0.12},
 "scratch":{"fx":"sweep","on":"face","axis":"x","shape":"tri","mode":"band","speed":0.37,"from":0.2,"to":0.8,"width":0.022,"c":0.9,"gain":0.5},
 "hairline":{"fx":"sweep","on":"face","axis":"x","shape":"saw","mode":"band","speed":0.23,"from":0.75,"to":0.28,"width":0.016,"c":0.8,"gain":0.3},
 "snare":{"fx":"blades","on":"tubes","seq":["012"],"step":1,"rise":0.12,"keep":0,"c":0.6,"ctip":1,"gain":0.26,"gate":{"pat":".x.x","step":1,"decay":0.75}},
 # the leader
 "hand":{"fx":"grad","on":"shell","axis":"a","wave":"saw","speed":0.25,"ofs":0.75,"pal":"hand","gain":0.13},
 # the premiere: searchlights crossing from the bottom of the dome, as in the fanfare
 "beamA":{"fx":"sweep","on":"shell","axis":"a","shape":"tri","mode":"band","speed":0.0625,"from":0.06,"to":0.44,"width":0.05,"c":0.9,"gain":0.4},
 "beamB":{"fx":"sweep","on":"shell","axis":"a","shape":"tri","mode":"band","speed":0.0625,"from":0.44,"to":0.06,"width":0.05,"c":0.9,"gain":0.4},
 "ring":{"fx":"sweep","on":"shell","axis":"r","shape":"p","mode":"band","from":0,"to":1.2,"width":0.25},
 "cue":{"fx":"orb","on":"shell","x":112,"y":132,"rad":24,"soft":12,"c":1,"pal":"silver","gain":0.8},
 "iris":{"fx":"orb","on":"shell","x":0,"y":112,"soft":26,"c":0.75},
 # the three strips of technicolor, sliding in and out of register
 "strip":{"fx":"grad","on":"shell","axis":"x","axis2":"y","scale":3,"lo":0,"hi":1,"gain":0.14},
 # busby berkeley
 "kalei":{"fx":"grad","on":"shell","axis":"a","axis2":"r","wave":"saw","scale":10,"speed":0.125,"warp":0.3,"wscale":0.9,"wspeed":0.0625,"pal":"petal","gain":0.14},
 "kaleiear":{"fx":"grad","on":"tubes","axis":"a","axis2":"r","wave":"saw","scale":4,"speed":-0.25,"warp":0.25,"wscale":0.8,"wspeed":0.0625,"pal":"petal","gain":0.2,"env":{"in":2}},
 "dye":{"fx":"grad","on":"shell","axis":"x","axis2":"y","wave":"saw","scale":0.55,"speed":0.03125,"warp":0.12,"wscale":1.1,"wspeed":0.0625,"pal":"dye","gain":0.14},
 "stars":{"fx":"twinkle","on":"shell","rate":1,"sharp":14,"dens":0.5,"c":0.95,"pal":"gold","seed":21,"gain":0.4},
 "curtainL":{"fx":"sweep","on":"left","axis":"x","shape":"p","mode":"fill","soft":0.03,"pal":"velvet","c":0,"cgrad":9,"mix":"over","gain":0.16},
 "curtainR":{"fx":"sweep","on":"right","axis":"x","shape":"p","mode":"fill","soft":-0.03,"pal":"velvet","c":0,"cgrad":9,"mix":"over","gain":0.16},
 "filmstrip":{"fx":"grad","on":"jaw","axis":"a","scale":28,"speed":0.5,"pal":"holes","gain":0.16},
 "lift":{"fx":"blades","on":"tubes","seq":["0","1","2","012"],"rise":0.2,"keep":0.2,"c":0.4,"ctip":0.95},
}
FLICK={"pat":"x.xox.ox","step":0.5,"decay":0.6,"floor":0.72}
PUMP={"pat":"x...","step":0.25,"depth":0.2,"decay":0.5}
HARD=dict(PUMP,depth=0.3)

marks={"lamp":4,"count":8,"last":15,"film":16,"horse":24,"swell":30,"walk":32,"walk2":40,"climb":46,"slam":48,"black":50,"beams":56,"beams2":60,"cue1":62,
 "drop":64,"open":66,"kalei":72,"gap1":79,"night":80,"gap2":87,"strips":88,"gap3":95,"fall":96,"alone":98,"train":104,"tint":112,"moon":120,
 "run":128,"run2":136,"run3":140,"count2":141,"drop2":144,"kalei2":152,"gap4":159,"night2":160,"gap5":167,"all":168,"peak":175,
 "drain":176,"drain2":184,"out":192,"away":196,"burn":204,"gone":208}

scenes=[]; S=scenes.append
def sprite(params,gain,color=None,**kw):
    d={"fx":"preset","name":"sprite","on":"shell","mix":"over","params":dict(params,color=color) if color else params,"gain":gain}
    d.update(kw)
    return d
def walker(col="sepia@0.9",dx=210,vx=-28,sp=WALK,gain=0.55,rate=LEGS,flick=True):
    return sprite(dict(FIG,sprite=sp,rate=rate,dx=dx,vx=vx,color=col),gain,**({"gate":FLICK} if flick else {}))
def horse(gain=0.6):
    return sprite(dict(HORSE,sprite="cinema_horse1|cinema_horse2|cinema_horse3|cinema_horse4",rate=LEGS,color="silver@1"),gain,gate=FLICK)
def moonface(col,gain,sp="cinema_moon"):
    return sprite(dict(MOON,sprite=sp,color=col),gain)
# ------------------------------------------------------------- the lamp warms, with the tick of the sound as the film's own
S({"name":"ticks","from":0,"to":"lamp","pal":"silver","layers":[
 {"use":"sprocket","speed":0.25,"gain":[0.25,0.5],"gate":{"pat":"x","step":1,"decay":0.45}},
 {"fx":"orb","on":"shell","x":0,"y":112,"rad":34,"soft":26,"pal":"lamp","c":0.8,"gain":[0,0.3],"gate":{"pat":"x","step":1,"decay":0.9,"floor":0.55}}]})
S({"name":"lamp","from":"lamp","to":"count","pal":"silver","layers":[
 {"use":"sprocket","speed":0.25,"gate":{"pat":"x","step":1,"decay":0.45}},
 {"use":"reel","gain":[0,0.16]},
 {"fx":"orb","on":"shell","x":0,"y":112,"rad":[34,210],"soft":[26,120],"pal":"lamp","c":0.7,"gain":[0.3,0.2],"gate":FLICK},
 {"use":"grain","gain":[0,0.2]}]})
# ------------------------------------------------------------- the leader: eight to one, a turn of the hand a bar
S({"name":"leader","from":"count","to":"last","pal":"silver","layers":[
 {"use":"hand"},
 sprite(dict(DIGIT,sprite="|".join("cinema_d%d"%d for d in (8,7,6,5,4,3,2)),rate=1/BAR,color="silver@1"),0.32,gate=FLICK),
 {"use":"sprocket","speed":0.25,"gate":{"pat":"x","step":1,"decay":0.45}},
 {"use":"reel","gain":0.12},
 {"use":"grain","gain":0.1}]})
S({"name":"one","from":"last","to":"film","pal":"silver","out":0.5,"layers":[
 {"use":"hand"},
 sprite(dict(DIGIT,sprite="cinema_d1",color="silver@1"),0.36),
 {"use":"sprocket","speed":1,"gain":0.6},
 {"use":"reel","speed":0.5,"gain":[0.14,0.26]},
 {"fx":"sweep","on":"jaw","axis":"y","shape":"p","mode":"fill","soft":0.1,"from":-0.05,"to":0.45,"c":[0.3,0.7],"gain":0.14}]})
# ------------------------------------------------------------- the picture starts: silver, grain, a scratch.  The title crosses once.
FILM=[{"use":"vignette","pal":"silver","gain":0.05,"gate":FLICK},{"use":"grain","pal":"silver","gain":0.1},{"use":"scratch","pal":"silver"},{"use":"sprocket"},{"use":"reel","env":{"in":2}},{"use":"filmstrip"}]
S({"name":"film","from":"film","to":"horse","pal":"silver","layers":FILM})
# the first film there ever was: a galloping horse, standing still in the frame
S({"name":"horse","from":"horse","to":"swell","pal":"silver","layers":[
 {"use":"vignette","pal":"silver","gain":0.04,"gate":FLICK},{"use":"grain","pal":"silver","gain":0.1},{"use":"filmstrip"},horse(0.3),{"use":"sprocket","speed":1},{"use":"reel"}]})
S({"name":"swell","from":"swell","to":"walk","pal":"silver","layers":[
 {"use":"vignette","pal":"silver","gain":[0.04,0.1],"gate":FLICK},
 {"use":"grain","pal":"silver","gain":[0.1,0.16]},
 horse(0.3),
 {"use":"sprocket","speed":1},
 {"use":"reel","speed":0.25,"gain":[0.14,0.22]},
 {"use":"lift","pal":"silver","step":{"swell":1,"31":0.5},"gain":[0.12,0.28]}]})
# ------------------------------------------------------------- the kick arrives, and with it somebody: a very small mau5 walks across the silent screen
WALKING=[{"use":"vignette","pal":"sepia","gain":0.06,"gate":FLICK},{"use":"grain","pal":"sepia","gain":0.1},walker(gain=0.36),{"use":"sprokick"},{"use":"reel","pal":"sepia","speed":0.25,"gain":0.14,"env":{"in":2}},{"use":"snare","pal":"sepia"}]
S({"name":"walk","from":"walk","to":"walk2","pal":"sepia","pump":PUMP,"layers":WALKING})
S({"name":"walk2","from":"walk2","to":"climb","like":"walk","patch":{"2":{"params":dict(FIG,sprite=WALK,rate=LEGS,dx=-210,vx=36,color="sepia@0.9")}}})
S({"name":"climb","from":"climb","to":"slam","pal":"silver","layers":[
 {"use":"vignette","pal":"silver","gain":[0.06,0.02],"gate":FLICK},
 sprite(dict(CLAP,sprite="cinema_clap_h|cinema_clap_o",rate=1/BAR,color="silver@1"),[0.2,0.3]),
 {"use":"sprocket","speed":{"climb":1,"47":2},"gain":0.6},
 {"use":"reel","speed":{"climb":0.25,"47":0.5},"gain":[0.1,0.16]},
 {"use":"lift","pal":"silver","step":{"climb":0.5,"47":0.25},"gain":[0.1,0.2]}]})
# ------------------------------------------------------------- the iris closes, and almost nothing
S({"name":"iris","from":"slam","to":"black","pal":"silver","layers":[
 {"use":"iris","rad":[230,8],"gain":[0.1,0.26],"pal":"silver"},
 {"use":"sprocket","speed":0.5,"gain":[0.3,0.12]},
 {"use":"reel","speed":0.0625,"gain":[0.08,0.04]}]})
S({"name":"black","from":"black","to":"beams","pal":"silver","layers":[
 {"fx":"twinkle","on":"face","rate":0.5,"sharp":10,"dens":0.35,"c":0.75,"seed":9,"gain":[0.12,0.32]},
 {"use":"sprocket","speed":0.0625,"gain":0.1},
 {"use":"reel","speed":0.03125,"gain":0.05}]})
# ------------------------------------------------------------- the build: searchlights over a premiere, still in black and white
S({"name":"beams","from":"beams","to":"beams2","pal":"silver","layers":[
 {"use":"beamA","gain":[0.14,0.3],"env":{"in":4}},
 {"use":"beamB","gain":[0.14,0.3],"env":{"in":4}},
 {"fx":"twinkle","on":"face","rate":0.5,"sharp":10,"dens":0.35,"c":0.75,"seed":9,"gain":0.3},
 {"use":"sprocket","speed":0.25,"gain":[0.1,0.35]},
 {"use":"reel","speed":0.0625,"gain":[0.06,0.2]}]})
S({"name":"beams2","from":"beams2","to":"cue1","pal":"silver","layers":[
 {"use":"beamA","speed":0.125,"gain":[0.36,0.45]},
 {"use":"beamB","speed":0.125,"gain":[0.36,0.45]},
 {"fx":"twinkle","on":"face","rate":1,"sharp":8,"dens":0.4,"c":0.75,"seed":9,"gain":0.3},
 {"use":"sprocket","speed":0.5,"gain":[0.35,0.55]},
 {"use":"reel","speed":0.125,"gain":[0.14,0.2]},
 {"use":"lift","pal":"silver","step":1,"gain":[0.08,0.2]}]})
S({"name":"cue","from":"cue1","to":"drop","pal":"silver","out":0.5,"layers":[
 {"use":"beamA","speed":0.25,"width":[0.05,0.09],"gain":[0.45,0.5]},
 {"use":"beamB","speed":0.25,"width":[0.05,0.09],"gain":[0.45,0.5]},
 {"fx":"fill","on":"shell","c":0.6,"gain":[0,0.06]},
 {"use":"sprocket","speed":{"cue1":1,"63":2},"gain":0.6},
 {"use":"reel","speed":{"cue1":0.25,"63":0.5},"gain":[0.12,0.18]},
 {"use":"lift","pal":"silver","step":{"cue1":0.5,"63":0.25},"gain":[0.12,0.22]}]})
# ------------------------------------------------------------- THE DROP: colour, for the first time, and the curtains part
GOLDHOLES={"use":"sprokick","pal":"holesgold","speed":2}
S({"name":"parting","from":"drop","to":"open","pal":"gold","pump":HARD,"layers":[
 {"use":"dye"},
 {"use":"curtainL","from":0.5,"to":0.27},
 {"use":"curtainR","from":0.5,"to":0.73},
 GOLDHOLES,
 {"use":"reel","pal":"ruby","speed":0.25,"gain":0.2,"env":{"in":2}},
 {"use":"snare","pal":"gold"}]})
S({"name":"oz","from":"open","to":"kalei","pal":"gold","pump":HARD,"out":1,"layers":[
 {"use":"dye"},
 {"use":"curtainL","from":0.27,"to":0.27},
 {"use":"curtainR","from":0.73,"to":0.73},
 GOLDHOLES,
 {"use":"reel","pal":"ruby","speed":0.25,"gain":0.2,"env":{"in":2}},
 {"use":"snare","pal":"gold"}]})
# ------------------------------------------------------------- reel two: busby berkeley
BERKELEY=[{"use":"kalei"},{"use":"kaleiear"},GOLDHOLES,{"use":"snare","pal":"gold","gain":0.22}]
S({"name":"berkeley","from":"kalei","to":"gap1","pal":"petal","pump":HARD,"layers":BERKELEY})
def change(name,a,b,pal,ear):
    """The film runs out with the bass: black screen, the holes racing, the cue mark top right, and the
    changeover: the next reel spins up on the other projector."""
    return {"name":name,"from":a,"to":b,"pal":pal,"layers":[
     {"use":"sprocket","pal":"holes","speed":3,"gain":0.6},
     {"use":"reel","on":"tubes"+ear,"pal":pal,"speed":0.5,"gain":[0.1,0.55]},
     {"use":"grain","pal":"silver","rate":3,"gain":[0.1,0.3]}]}
S(change("change1","gap1","night","gold","2"))
# ------------------------------------------------------------- reel three: premiere night
NIGHT=[{"fx":"grad","on":"shell","axis":"y","axis2":"x","scale":0.5,"speed":0,"lo":0.1,"hi":0.55,"pal":"cobalt","gain":0.16},
 {"use":"beamA","pal":"gold","speed":0.25,"gain":0.45},
 {"use":"beamB","pal":"gold","speed":0.25,"gain":0.45},
 sprite(dict(BULB,sprite="cinema_bulb0|cinema_bulb1|cinema_bulb2",rate=LEGS,color="gold@0.9"),0.75),
 {"use":"reel","pal":"gold","speed":0.25,"gain":0.22,"env":{"in":2}},
 {"fx":"fill","on":"rims","pal":"gold","c":0.9,"gain":0.6,"gate":{"pat":"x","step":1,"decay":0.6}}]
S({"name":"night","from":"night","to":"gap2","pal":"gold","pump":HARD,"layers":NIGHT})
S(change("change2","gap2","strips","emerald","1"))
# ------------------------------------------------------------- reel four: the three strips
STRIPS=[{"use":"strip","pal":"red","speed":0.1875,"gain":0.2},
 {"use":"strip","pal":"green","speed":-0.125,"gain":0.16},
 {"use":"strip","pal":"blue","speed":0.0625,"ofs":0.33,"gain":0.24},
 {"use":"sprokick","speed":2},
 {"use":"reel","pal":"dye","speed":0.25,"gain":0.08,"env":{"in":2}},
 {"use":"snare","pal":"dye","c":[0,1],"ctip":0.3}]
S({"name":"strips","from":"strips","to":"gap3","pal":"gold","pump":HARD,"layers":STRIPS})
S(change("change3","gap3","fall","ruby","2"))
# ------------------------------------------------------------- colour falls away with the noise: the flashback, and he is alone in a spot
S({"name":"fall","from":"fall","to":"alone","pal":"gold","layers":[
 {"use":"iris","pal":"sepia","rad":[230,48],"gain":[0.1,0.14]},
 {"use":"dye","gain":[0.12,0],"env":{"out":4}},
 {"use":"sprocket","pal":"holes","speed":0.5,"gain":[0.4,0.1]},
 {"use":"reel","speed":0.125,"gain":[0.1,0.04]}]})
S({"name":"alone","from":"alone","to":"train","pal":"silver","layers":[
 {"use":"iris","pal":"silver","rad":52,"soft":36,"gain":0.06},
 walker("silver@1",0,0,"cinema_walk3",0.26,0),
 {"fx":"twinkle","on":"face","rate":0.5,"sharp":10,"dens":0.3,"c":0.7,"seed":14,"gain":0.2},
 {"use":"sprocket","speed":0.0625,"gain":0.1}]})
# ------------------------------------------------------------- the rolling bass is a train arriving, the way it was in 1896, and it takes him with it
S({"name":"train","from":"train","to":"tint","pal":"sepia","layers":[
 {"use":"vignette","gain":[0.03,0.05],"gate":FLICK},
 {"use":"grain","gain":0.1},
 dict(walker("silver@1",0,0,"cinema_walk3",1,0),gain={"train":0.26,"105.2":0}),
 sprite(dict(TRAIN,sprite="cinema_train1|cinema_train2|cinema_train3|cinema_train4",rate=2*LEGS,dx=547,vx=-1094/(8*BAR),color="sepia@0.75"),0.36),
 {"use":"sprocket","speed":{"train":0.5,"108":1},"gain":{"band":"bass","punch":True,"lo":0.15,"hi":0.6}},
 {"use":"reel","pal":"sepia","speed":0.125,"gain":[0.12,0.22]}]})
# ------------------------------------------------------------- the groove, in the hand tints of a silent film: a chorus line in amber ...
S({"name":"amber","from":"tint","to":"moon","pal":"amber","pump":PUMP,"layers":[
 {"use":"vignette","gain":0.06,"gate":FLICK},
 {"use":"grain","gain":0.1},
 sprite(dict(LINE,sprite="cinema_line1|cinema_line2",rate=1/SPB,color="amber@1"),0.36),
 {"use":"sprokick"},
 {"use":"reel","speed":0.25,"gain":0.16,"env":{"in":2}},
 {"use":"snare"}]})
# ... and the moon in night blue, with a rocket on its way to its eye, arriving as the riser starts
S({"name":"moon","from":"moon","to":"run","pal":"tintblue","pump":PUMP,"layers":[
 {"use":"vignette","gain":0.05,"gate":FLICK},
 moonface("tintblue@1",0.32),
 {"fx":"orb","on":"shell","x":[300,14],"y":[175,130],"rad":13,"soft":8,"pal":"gold","c":1,"mix":"over","gain":0.7},
 {"use":"sprokick"},
 {"use":"reel","speed":0.25,"gain":0.18,"env":{"in":2}},
 {"use":"snare"}]})
# ------------------------------------------------------------- the film jumps its sprockets: the frame line rolls, faster and faster, up to the second drop
def frameroll(speed,gain):
    return {"fx":"grad","on":"shell","axis":"y","scale":2,"speed":-speed,"pal":"frame","gain":gain}
def rolling(a,b,speed,gain,name,sp,lamp):
    return {"name":name,"from":a,"to":b,"pal":"sepia","layers":[
     frameroll(speed,gain),
     {"use":"grain","gain":0.1},
     {"use":"sprocket","speed":sp,"gain":0.5},
     {"use":"reel","pal":"sepia","speed":speed,"gain":0.2,"env":{"in":2}},
     {"fx":"orb","on":"shell","x":0,"y":112,"rad":lamp[0],"soft":70,"pal":"lamp","c":1,"gain":lamp[1]},
     {"use":"lift","pal":"sepia","step":max(0.25,0.5/max(speed*4,0.5)),"gain":[0.1,0.22]}]}
S(rolling("run","run2",0.125,0.1,"slip",1,[[30,70],[0.0,0.06]]))
S(rolling("run2","run3",0.25,0.1,"slip 2",2,[[70,110],[0.06,0.09]]))
S(rolling("run3","count2",0.5,0.1,"slip 3",3,[[110,130],[0.09,0.1]]))
# ... and the leader comes back for it: three, two, one
S({"name":"recount","from":"count2","to":"drop2","pal":"sepia","out":0.5,"layers":[
 {"use":"hand","speed":0.5,"gain":0.09},
 dict(frameroll(1,0.14),on="jaw"),
 sprite(dict(DIGIT,sprite="cinema_d3|cinema_d2|cinema_d1",rate=1/BAR,color="white@0.6"),0.36),
 {"use":"sprocket","speed":4,"gain":0.55},
 {"use":"reel","pal":"sepia","speed":1,"gain":[0.2,0.32]},
 {"use":"lift","pal":"sepia","step":0.25,"gain":[0.08,0.16]}]})
# ------------------------------------------------------------- the second drop: no more curtains, and the mau5 himself in colour
S({"name":"oz 2","from":"drop2","to":"kalei2","pal":"gold","pump":HARD,"out":1,"layers":[
 {"use":"dye","scale":0.8,"speed":0.0625,"gain":0.09,"env":{"in":1.5}},
 {"use":"stars","env":{"in":2}},
 dict(walker("white@0.8",0,0,"cinema_walk1|cinema_walk2",0.3,1/SPB,False),env={"in":2}),
 GOLDHOLES,
 {"use":"reel","pal":"gold","speed":0.25,"gain":0.22,"env":{"in":2}},
 {"use":"snare","pal":"ruby"}]})
S({"name":"berkeley 2","from":"kalei2","to":"gap4","pal":"petal","pump":HARD,"layers":[
 {"use":"kalei","scale":14,"speed":0.25,"gain":0.08},
 {"use":"kaleiear"},
 sprite(dict(LINE,sprite="cinema_line1|cinema_line2",rate=1/SPB,color="gold@1"),0.3),
 GOLDHOLES,
 {"use":"snare","pal":"gold","gain":0.22}]})
S(change("change4","gap4","night2","ruby","2"))
S({"name":"night 2","from":"night2","to":"gap5","pal":"gold","pump":HARD,"layers":[
 NIGHT[0],
 {"use":"beamA","pal":"rose","speed":0.5,"gain":0.45},
 {"use":"beamB","pal":"rose","speed":0.5,"gain":0.45},
 NIGHT[3],
 moonface("tintblue@0.9",0.3),
 {"use":"reel","pal":"gold","speed":0.25,"gain":0.32,"gate":{"pat":"x","step":1,"decay":0.7,"floor":0.4}}]})
S(change("change5","gap5","all","cobalt","1"))
S({"name":"strips 2","from":"all","to":"peak","pal":"gold","pump":HARD,"layers":[
 STRIPS[0],STRIPS[1],STRIPS[2],
 {"use":"sprokick","speed":{"all":2,"172":3,"174":4}},
 {"use":"reel","pal":"dye","speed":{"all":0.25,"172":0.5},"gain":0.08},
 {"use":"lift","pal":"dye","c":[0,1],"ctip":0.3,"step":{"all":1,"172":0.5,"174":0.25},"gain":0.24}]})
# ------------------------------------------------------------- the very peak: the only real strobe in the film, on the ears alone, in the dark
S({"name":"strobe","from":"peak","to":"drain","pal":"white","layers":[
 {"fx":"fill","on":"ears","c":1,"gain":[0.16,0.24],"gate":{"pat":"x","step":0.25,"decay":0.06}},
 {"use":"grain","pal":"silver","rate":3,"gain":[0.08,0.2]}]})
# ------------------------------------------------------------- the colour drains back out of the picture, and he is back in sepia
S({"name":"drain","from":"drain","to":"drain2","pal":"sepia","pump":PUMP,"layers":[
 {"use":"dye","gain":[0.14,0]},
 {"use":"vignette","gain":[0,0.06],"gate":FLICK},
 {"use":"grain","gain":[0,0.1]},
 {"use":"sprokick","pal":"holesgold"},
 {"use":"reel","pal":"gold","speed":0.25,"gain":[0.22,0.1],"env":{"in":2}},
 {"use":"snare","pal":"sepia"}]})
S({"name":"drain 2","from":"drain2","to":"out","pal":"sepia","pump":PUMP,"layers":WALKING})
# ------------------------------------------------------------- the film runs out: he walks away down the road, as they do, and the iris follows him
S({"name":"out","from":"out","to":"away","pal":"sepia","layers":[
 {"use":"vignette","gain":[0.05,0.04],"gate":FLICK},
 {"use":"grain","gain":0.08},
 walker("sepia@0.9",0,0,"cinema_far1|cinema_far2",0.36),
 {"use":"sprocket","speed":0.5,"gain":0.35,"gate":{"pat":"x","step":1,"decay":0.45}},
 {"use":"reel","pal":"sepia","speed":0.0625,"gain":0.14}]})
S({"name":"away","from":"away","to":"burn","pal":"silver","layers":[
 {"use":"iris","pal":"sepia","rad":[210,46],"soft":[120,36],"gain":[0.04,0.08],"gate":FLICK},
 {"use":"grain","pal":"sepia","gain":0.08},
 walker("sepia@0.9",0,0,"cinema_far3|cinema_far4",0.36,1/(4*BAR)),
 {"use":"hairline","pal":"sepia","gain":0.25},
 {"use":"sprocket","speed":0.25,"gain":0.3,"gate":{"pat":"x","step":1,"decay":0.45}},
 {"use":"reel","pal":"sepia","speed":0.03125,"gain":0.1}]})
# ------------------------------------------------------------- the film stops in the gate and burns out from the middle
S({"name":"burn","from":"burn","to":"gone","pal":"burn","layers":[
 {"fx":"grad","on":"shell","axis":"r","axis2":"a","wave":"saw","scale":0.5,"ofs":[0.5,-0.03],"warp":0.015,"wscale":5,"wspeed":0.0625,"pal":"burn","gain":[0.16,0.5],"env":{"in":1}},
 {"use":"sprocket","speed":0,"gain":[0.3,0.1],"gate":{"pat":"x","step":1,"decay":0.45}},
 {"fx":"fill","on":"rims","pal":"burn","c":0.53,"gain":{"204":0,"206":0.12,"207":0.3}}]})
S({"name":"tail","from":"gone","to":210,"pal":"silver","layers":[
 {"use":"sprocket","on":"rim2","speed":0.25,"gain":[0.25,0],"gate":{"pat":"x","step":1,"decay":0.3}}]})

def cue(at,name="cue",beats=0.75):
    return {"name":name,"at":at,"beats":beats,"layers":[{"use":"cue"}]}
EARG={"rose":0.13,"cobalt":0.2,"emerald":0.15,"gold":0.14,"amber":0.16,"tintblue":0.13,"ruby":0.2,"white":0.1}
def hit(name,at,ear,ring,beats=2,g=None,rg=0.4):
    g=g or EARG[ear]
    return {"name":name,"at":at,"beats":beats,"layers":[{"fx":"fill","on":"ears","pal":ear,"c":1,"gain":[g,0]},{"use":"ring","pal":ring,"c":1,"gain":rg}]}
hits=[
 {"name":"START","at":"film","beats":2,"pal":"silver","layers":[{"fx":"fill","on":"ears","c":0.9,"gain":[0.1,0]},{"use":"ring","c":0.8,"gain":0.4}]},
 {"name":"STROBE","at":17,"beats":26,"layers":[{"fx":"preset","name":"text","on":"face","fit":True,"mix":"over","env":{"in":2,"out":2},"params":{"text":"STROBE","color":"sepia@1"},"gain":0.5}]},
 {"name":"KICK IN","at":"walk","beats":2,"pal":"sepia","layers":[{"fx":"fill","on":"ears","c":0.9,"gain":[0.16,0]},{"use":"ring","c":0.8,"gain":0.4}]},
 {"name":"CLAP","at":"slam","beats":1.5,"pal":"silver","layers":[
   sprite(dict(CLAP,sprite="cinema_clap_c",color="silver@1"),[0.5,0.1]),
   {"fx":"fill","on":"ears","c":0.9,"gain":[0.09,0]}]},
 cue(63), cue(63.5,"cue 2"),
 {"name":"COLOUR","at":"drop","beats":2,"layers":[{"fx":"fill","on":"ears","pal":"ruby","c":1,"gain":[0.16,0]},{"use":"ring","pal":"gold","c":1,"gain":0.4}]},
 cue(71.5,"cue",0.5), cue(71.75,"cue 2",0.75),
 hit("REEL 2","kalei","rose","rose"),
 cue("gap1"), cue(79.5,"cue 2"),
 hit("REEL 3","night","cobalt","gold"),
 cue("gap2"), cue(87.5,"cue 2"),
 hit("REEL 4","strips","emerald","emerald"),
 cue("gap3"), cue(95.5,"cue 2"),
 hit("LAST COLOUR","fall","ruby","gold"),
 hit("TINT","tint","amber","amber"),
 hit("TINT 2","moon","tintblue","tintblue"),
 {"name":"IMPACT","at":"run","beats":4,"pal":"tintblue","layers":[
   moonface("tintblue@1",[0.4,0],"cinema_moonhit"),
   {"fx":"orb","on":"shell","x":14,"y":130,"rad":[14,60],"soft":20,"pal":"gold","c":1,"gain":[0.5,0]},
   {"fx":"fill","on":"ears","pal":"gold","c":1,"gain":[0.14,0]}]},
 cue(142), cue(143,"cue 2"),
 {"name":"TAKE 2","at":"drop2","beats":1.5,"layers":[
   sprite(dict(CLAP,sprite="cinema_clap_c",color="white@1"),[0.6,0.15]),
   {"fx":"fill","on":"ears","pal":"white","c":1,"gain":[0.1,0]}]},
 cue(151.5,"cue",0.5), cue(151.75,"cue 2",0.75),
 hit("REEL 6","kalei2","rose","rose"),
 cue("gap4"), cue(159.5,"cue 2"),
 hit("REEL 7","night2","cobalt","gold"),
 cue("gap5"), cue(167.5,"cue 2"),
 hit("REEL 8","all","emerald","emerald"),
 hit("LAST REEL","drain","gold","gold"),
]
ABOUT=("Bars of a measured grid, shows/scenes/%s.beats: bar b starts at 0.136 + 1.875 b seconds (128.000 BPM), 210 bars, flat to 5 ms. The bar line is where the phrases turn, every 8 bars from bar 0, and every hole in the bass (71.5, 79, 87, 95, 151.5, 159, 167, 175) is on it. THE CINEMA. A remix called Special Features gets a film, and the song runs through the history of cinema. The ears are the projector's two reels, turning clockwise as reels do; their rims are the sprocket holes, and the tick that opens the track is the film going through the gate. The lamp warms, then the leader counts eight to one, a turn of the clock hand a bar. The picture starts in silver with grain, a scratch and a film strip running along the jaw, and the title crosses once. Then the first film there was: a galloping horse. The kick brings the only character, a very small mau5 walking across the silent screen in sepia. A clapper slams on the one hit at 48, the iris closes, and there is almost nothing but dust until searchlights swing up from the bottom of the dome for a premiere, still in black and white. The first drop goes to Technicolor, and nothing before it has had a colour in it. Red velvet parts on a moving dye picture; reel two is a Busby Berkeley kaleidoscope, reel three premiere night with marquee bulbs round the dome, reel four the three colour strips sliding in and out of register. Every hole in the bass is a reel change: black screen, holes racing, the cue mark blinking top right as it does in a real print, and the next reel spinning up on the other ear. The second breakdown is a flashback in silver, the mau5 alone. The rolling bass is the train arriving, as in 1896, and it takes him with it. The groove is hand-tinted silent film: a kick line of three mau5s in amber, then the moon in night blue with a rocket on its way to its eye, which lands exactly as the riser starts. In the long riser the film jumps its sprockets: the frame line rolls faster and faster, the lamp gets hotter, and the leader comes back to count three, two, one. A second clap, the one white moment, alone on a black dome, then the mau5 himself in colour with no more curtains; the kick line comes back gold over the kaleidoscope and the moon watches the second premiere. The only real strobe in the show is on the ears alone, in the dark, on the last riser, bar 175. Then the colour drains away, he walks off down the road getting smaller as an iris follows him, the film jams on a blank frame and burns out from the middle on the final riser. The ear flashes are kept where the power guard leaves the shell lit: over 1000 mA it sheds the shell at s^6, so each reel steps aside for the two beats of its hit, and the backgrounds are low so the characters have the shell's 300 mA to themselves. Nothing on the shell pulses faster than an 8th note."%BASE)
tr={"v":1,"show":BASE,"about":ABOUT,"lead":0,"marks":marks,"palettes":pal,"motifs":motifs,"scenes":scenes,"hits":hits}
# The long set's budget: each scene's shell asks for about what the guard sends (levels measured before the
# guard, as written above), the ears a little dimmer all song, the velvet curtains left dark enough to paint.
from budget import fit
SHELL_IN = {"lamp": 11.4, "leader": 17.2, "one": 15.8, "film": 26.1, "horse": 20.8, "swell": 18.7, "walk": 11.4, "walk2": 11.0,
            "climb": 16.2, "iris": 13.9, "beams2": 9.8, "cue": 15.9, "parting": 12.7, "oz": 11.1, "berkeley": 15.1, "night": 17.7,
            "strips": 21.5, "fall": 17.6, "alone": 8.6, "train": 16.0, "amber": 16.4, "moon": 13.5, "slip": 11.8, "slip 2": 13.7,
            "slip 3": 17.7, "recount": 19.0, "oz 2": 21.7, "berkeley 2": 19.6, "night 2": 22.9, "strips 2": 21.5, "drain": 10.7,
            "drain 2": 10.8, "out": 6.3, "burn": 18.8}
fit(tr, SHELL_IN, ask=6.0, ears=0.7, keep=lambda L: L.get("pal") == "velvet")
save(tr,"shows/scenes/%s.scene.json"%BASE)
