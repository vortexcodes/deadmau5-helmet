import json, os, sys, math
KIT=os.environ["KIT"]; sys.path.insert(0,KIT)
from fmt import save
BASE="deadmau5 - Raise Your Weapon"

# ---- the two worlds -------------------------------------------------------------------
PAL={
 "candle":[[0,0,0],[60,14,0],[190,70,6],[255,140,30],[255,205,110],[255,240,190]],
 "moon":[[0,0,0],[6,14,40],[30,70,130],[120,175,235],[225,240,255]],
 "spear":[[0,0,0],[0,0,0],[8,20,50],[40,90,160],[150,200,250]],
 "steel":[[0,0,0],[24,34,50],[90,120,155],[190,210,235],[255,255,255]],
 "crimson":[[0,0,0],[50,0,2],[150,0,8],[235,8,14],[255,60,30]],
 "army":[[0,0,0],[0,0,0],[60,0,3],[220,4,10],[255,70,30]],
 "hot":[[90,0,0],[230,30,5],[255,110,30],[255,200,120],[255,255,235]],
 "cut":[[0,0,0],[120,8,4],[255,150,70],[255,255,235],[255,150,70],[120,8,4],[0,0,0]],
 "white":[[255,120,40],[255,210,150],[255,255,255]],
}
SWORDS={"sprite":"weapon_swords","y_lo":44,"y_hi":172,"x_half":120}
BANNERS={"sprite":"weapon_banner1|weapon_banner2|weapon_banner1|weapon_banner3","rate":3.0,"y_lo":52,"y_hi":170,"x_half":135,"wx":7,"wy":0,"wf":0.29}
SWORD={"sprite":"weapon_sword","y_lo":48,"y_hi":172,"x_half":62}
LINE={"sprite":"weapon_line","y_lo":54,"y_hi":70,"x_half":172}
SPB=60/140.
def secs(beats): return beats*SPB     # a preset's clock runs on grid beats, whatever the music's tempo is

MARKS={"voice":16,"voice2":32,"long":42.5,"slide":46,"kick":48,"groove":64,"groove2":80,"draw":96,"climb":112,"title":122,
 "quiet":128,"drop":130,"unfurl":138,"p2":146,"p2b":154,"stop":161,"p3":162,"p4":178,"long1":189,"after1":191,"p5":194,"p5b":202,"p6":210,"long2":221,"after2":223,"p7":226,"p7b":234,"crash":242,
 "ash":246,"sheathe":250,"gutter":268,"end":276}

M={}
# ---- the candle, the moon, the singer -----------------------------------------------------
M["flame"]={"fx":"orb","on":"shell","pal":"candle","x":0,"y":112,"rad":50,"soft":38,"wx":4,"wy":6,"xf":0.31,"yf":0.53,"c":0.72,"cgrad":-0.6,"gain":0.62}
M["core"]={"fx":"orb","on":"shell","pal":"candle","x":0,"y":106,"rad":24,"soft":20,"wx":3,"wy":10,"xf":0.77,"yf":1.13,"c":0.95,"gain":0.5}
M["candle"]=[{"use":"flame"},{"use":"core"}]
M["glints"]={"fx":"twinkle","on":"shell","rate":0.2,"sharp":14,"dens":0.3,"spread":0.12,"pal":"moon","c":0.8,"gain":0.42,"seed":7}
M["moondisc"]={"fx":"orb","on":"tubes","pal":"moon","x":[-310,310],"y":235,"rad":85,"soft":60,"c":0.9,"cgrad":-0.3,"gain":0.5}
M["night"]={"fx":"grad","on":"shell","axis":"y","axis2":"x","scale":0.5,"speed":0,"warp":0.05,"wscale":1,"wspeed":0.02,"lo":0.05,"hi":0.45,"pal":"moon","gain":0.2}
# ---- the march: ranks along the jaw, spears on the dome, shields struck -----------------------
M["ranks"]={"fx":"grad","on":"jaw","axis":"x","axis2":"y","scale":6,"speed":-0.25,"lo":0,"hi":0.9,"pal":"spear","gain":0.6,"gate":{"pat":"x","step":1,"decay":0.9,"floor":0.35}}
M["spears"]={"fx":"grad","on":"face","axis":"x","axis2":"y","scale":5,"speed":0.02,"warp":0.03,"wscale":0.8,"wspeed":0.0625,"lo":0,"hi":0.9,"pal":"spear","gain":0.2,"gate":{"pat":"x","step":1,"decay":0.9,"floor":0.5}}
M["shield"]={"fx":"fill","on":"rims","pal":"steel","c":0.78,"gain":0.6,"gate":{"pat":"x","step":1,"decay":0.5}}
M["ripple"]={"fx":"sweep","on":"tubes","axis":"r","shape":"saw","speed":1,"mode":"band","from":-0.1,"to":1.9,"width":0.3,"pal":"steel","c":0.72,"gain":0.5,"gate":{"pat":"x","step":1,"decay":0.8}}
M["hats"]={"fx":"twinkle","on":"shell","rate":0.5,"sharp":10,"dens":0.35,"spread":0.1,"pal":"moon","c":0.85,"gain":{"band":"high","lo":0,"hi":0.5},"seed":21}
# ---- the blade being drawn ----------------------------------------------------------------
def blade(col="steel@0.9",gain=0.5,**kw):
    p=dict(LINE,color=col); p.update(kw)
    return {"fx":"preset","name":"sprite","on":"shell","mix":"max","params":p,"gain":gain}
M["halo"]={"fx":"sweep","on":"face","axis":"y","shape":"p","mode":"band","from":0.525,"to":0.525,"width":0.06,"pal":"steel","c":0.6,"gain":0.25}
# ---- the drop: slashes, banners, shields -----------------------------------------------------
X0,X1=0.03,0.97
def slash(right,beat,cycle=8,cross=0.34,width=0.13,gain=0.85,axis="x",a=None,b=None,on="shell",c=0.95,pal="hot"):
    """One band across the shell in `cross` beats, starting at `beat` of a `cycle`-beat repeat of the scene."""
    a=(X0 if right else X1) if a is None else a
    b=(X1 if right else X0) if b is None else b
    f0=beat/float(cycle); df=cross/float(cycle)
    slope=(b-a)/df
    v0=a-slope*f0; v1=v0+slope
    return {"fx":"sweep","on":on,"axis":axis,"shape":"saw","mode":"band","speed":1.0/cycle,"from":round(v0,4),"to":round(v1,4),"width":width,"pal":pal,"c":c,"gain":gain}
def slant(right,beat,lean,cycle=8,cross=0.5,width=0.14,gain=0.9):
    """A slash on a leaning line, as a grad: a band of the palette 'cut' on a saw. B here is absolute,
    and every bar from 128 on is whole, so beat 0 of the 8-beat cycle is any even bar."""
    span=(X1-X0)+abs(lean)*0.5
    scale=(cross/float(cycle))/span
    speed=(-1.0 if right else 1.0)/cycle
    wscale=0.125
    # the line's x moves by lean per unit of y: warp/scale*2*pi*wscale*cos(..) ~ warp/scale*0.707 across 0..1
    warp=lean*scale/0.707
    y0=0.75; x0=(X0-abs(lean)*0.25) if right else (X1+abs(lean)*0.25)
    ofs=(0.5-x0*scale-(beat*speed)-warp*math.sin(2*math.pi*y0*wscale))%1.0
    Q=1.0/(width*scale)
    return {"fx":"grad","on":"shell","axis":"x","axis2":"y","wave":"saw","scale":round(scale,6),"speed":speed,"ofs":round(ofs,6),"warp":round(warp,6),"wscale":wscale,"wspeed":0,
            "lo":round(0.5-Q/2,3),"hi":round(0.5+Q/2,3),"pal":"cut","gain":gain}
M["slashes"]=[slash(True,2),slash(False,6)]
M["arcs"]=[slash(True,2,axis="a",a=0.56,b=-0.06,width=0.05,cross=0.5),slash(False,6,axis="a",a=-0.06,b=0.56,width=0.05,cross=0.5)]
M["cross"]=[slant(True,2,0.7),slant(False,6,0.7)]
M["clash"]=[slash(True,2,cycle=4,cross=0.5,gain=0.6),slash(False,2,cycle=4,cross=0.5,gain=0.6)]
M["wake"]={"fx":"fill","on":"shell","pal":"crimson","c":0.72,"gain":0.2,"gate":{"pat":"..x.","step":1,"decay":1.4}}
M["army"]={"fx":"grad","on":"jaw","axis":"x","axis2":"y","scale":6,"speed":-0.25,"lo":0,"hi":0.95,"pal":"army","gain":0.5,"gate":{"pat":"x...","step":1,"decay":2.5,"floor":0.25}}
M["blood"]={"fx":"fill","on":"shell","pal":"crimson","c":0.55,"gain":{"band":"bass","lo":0,"hi":0.3}}
M["banners"]={"fx":"preset","name":"sprite","on":"shell","params":dict(BANNERS,color="crimson@0.8"),"gain":0.42,"gate":{"pat":"x...","step":1,"decay":3.2,"floor":0.55}}
M["swords"]={"fx":"preset","name":"sprite","on":"shell","mix":"over","params":dict(SWORDS,color="hot@0.72"),"gain":0.8,"gate":{"pat":"x.x.","step":1,"decay":1.6,"floor":0.6}}
M["flash"]={"fx":"orb","on":"shell","pal":"hot","x":0,"y":105,"rad":60,"soft":45,"c":0.55,"gain":0.7,"gate":{"pat":"..x.","step":1,"decay":0.6}}

def raised(gain=(0.25,0.9),col="hot@0.95",beats=8):
    """The sword comes up from the jaw over the long note."""
    p=dict(SWORD,color=col,dy=-124,vy=round(124/secs(beats),3))
    return {"fx":"preset","name":"sprite","on":"shell","mix":"over","params":p,"gain":list(gain)}

S=[]
A=S.append
# ---- the candle ------------------------------------------------------------------------
A({"name":"candle","from":0,"to":"voice","pal":"candle","layers":[
  {"use":"flame","gain":{"band":"bass","lo":0.35,"hi":0.8},"env":{"in":8}},
  {"use":"core","gain":{"band":"bass","lo":0.2,"hi":0.6},"env":{"in":8}},
  {"use":"moondisc","x":-330,"y":[-40,235],"gain":[0,0.5]}]})
# ---- the singer, under the moon, which crosses from ear to ear -------------------------------------
MOON=lambda a,b,g:{"use":"moondisc","x":[a,b],"gain":g}
A({"name":"moonrise","from":"voice","to":"voice2","pal":"moon","layers":[
  {"use":"candle"},{"use":"glints"},MOON(-330,-20,0.5),{"use":"night","gain":[0,0.14]}]})
A({"name":"moonlit","from":"voice2","to":"kick","pal":"moon","out":1,"layers":[
  {"use":"candle"},{"use":"glints","gain":0.5},MOON(-20,330,0.5),{"use":"night","gain":[0.14,0.26]},
  {"fx":"fill","on":"rims","pal":"moon","c":0.6,"gain":{"voice2":0,"38":0.12,"46":0.25}}]})
# ---- the march ------------------------------------------------------------------------
A({"name":"march","from":"kick","to":"groove","pal":"steel","pump":{"pat":"x","step":1,"depth":0.15,"decay":0.8},"layers":[
  {"use":"flame","gain":0.4},{"use":"core","gain":0.3},{"use":"ranks"},{"use":"shield"},{"use":"ripple"},{"use":"glints","gain":0.25}]})
A({"name":"sung march","from":"groove","to":"groove2","pal":"steel","pump":{"pat":"x","step":1,"depth":0.18,"decay":0.8},"layers":[
  {"use":"flame","gain":0.4},{"use":"ranks"},{"use":"spears","gain":0.14},{"use":"shield"},{"use":"ripple"},{"use":"hats"}]})
A({"name":"full march","from":"groove2","to":"draw","pal":"steel","pump":{"pat":"x","step":1,"depth":0.2,"decay":0.8},"out":0.5,"layers":[
  {"use":"flame","gain":0.34},{"use":"ranks","gain":0.65},{"use":"spears","gain":[0.14,0.22]},{"use":"shield","gain":0.65},{"use":"ripple","gain":0.6},{"use":"hats","gain":{"band":"high","lo":0,"hi":0.6}}]})
# ---- the draw: the thin line grows across the brow while the top end comes back --------------------
A({"name":"the draw","from":"draw","to":"climb","pal":"steel","layers":[
  blade(gain=[0.3,0.75],dx=-344,vx=round(344/secs(4*16),4)),
  {"fx":"sweep","on":"tubes","axis":"al","shape":"p","mode":"fill","from":-0.1,"to":1.1,"soft":0.25,"pal":"moon","c":0.5,"cgrad":0.35,"gain":[0.12,0.34]},
  {"use":"shield","gain":[0.3,0.55]},
  {"use":"flame","gain":[0.2,0.04],"rad":[50,26]},
  {"use":"halo","gain":{"draw":0,"104":0,"110":0.14,"climb":0.3},"width":[0.03,0.09]}]})
# ---- the hold: the tempo climbs under the song, and the ticks climb with it -------------------------
A({"name":"on edge","from":"climb","to":"title","pal":"moon","layers":[
  blade(col="steel@0.8",gain=0.42),
  {"use":"flame","gain":0.42,"wx":[4,18],"wy":[6,20],"env":{"out":5}},
  {"use":"core","gain":0.34,"wx":[3,14],"wy":[10,22],"env":{"out":5}},
  {"use":"glints","gain":0.35},
  {"fx":"fill","on":"rims","pal":"steel","c":0.7,"gain":[0.25,0.55],"gate":{"pat":"x","step":1,"decay":0.35}},
  {"fx":"blades","on":"tubes","seq":["0","1","2"],"step":1,"rise":0.2,"keep":0,"pal":"moon","c":0.5,"ctip":0.9,"gain":[0.12,0.34]}]})
A({"name":"title","from":"title","to":"quiet","pal":"moon","layers":[
  blade(col="steel@0.7",gain=0.2),
  {"fx":"fill","on":"rims","pal":"steel","c":0.7,"gain":[0.4,0.6],"gate":{"pat":"x","step":1,"decay":0.3}},
  {"fx":"blades","on":"tubes","seq":["2","1","0"],"step":1,"rise":0.2,"keep":0,"pal":"moon","c":0.5,"ctip":0.9,"gain":[0.25,0.4]}]})
A({"name":"quiet","from":"quiet","to":"drop","pal":"steel","out":0.25,"layers":[
  blade(col="hot@0.9",gain=[0.3,0.95]),
  {"use":"halo","pal":"hot","c":0.5,"gain":{"quiet":0,"129":0.05,"129.5":0.3},"width":[0.03,0.12]}]})
# ---- THE DROP ----------------------------------------------------------------------------
PD={"pat":"x...............","step":0.25,"depth":0.25,"decay":0.9}
A({"name":"first blood","from":"drop","to":"unfurl","pal":"crimson","pump":PD,"out":0.25,"layers":[{"use":"blood"},{"use":"army"},{"use":"slashes"},{"use":"wake"}]})
A({"name":"banners","from":"unfurl","to":"p2","pal":"crimson","pump":PD,"out":0.25,"layers":[{"use":"banners","env":{"in":6}},{"use":"army"},{"use":"slashes"},{"use":"wake"}]})
A({"name":"arcs","from":"p2","to":"p2b","pal":"crimson","pump":PD,"out":0.25,"layers":[{"use":"banners","gain":0.3},{"use":"army"},{"use":"arcs"},{"use":"wake"}]})
A({"name":"crossed","from":"p2b","to":"stop","pal":"crimson","pump":PD,"layers":[{"use":"banners","gain":0.24},{"use":"swords"},{"use":"army"},{"use":"arcs"},{"use":"wake"}]})
A({"name":"stopped","from":"stop","to":"p3","pal":"steel","layers":[
  blade(col="steel@0.95",gain=0.5),
  {"fx":"fill","on":"rims","pal":"steel","c":0.5,"gain":0.12}]})
# the singer comes back, a candle in the middle of it
A({"name":"sung war","from":"p3","to":"p4","pal":"crimson","pump":PD,"out":0.25,"layers":[{"use":"banners","gain":0.28},{"use":"flame","gain":0.7},{"use":"army","gain":0.42},{"use":"slashes","gain":0.6,"width":0.1},{"use":"wake","gain":0.15}]})
A({"name":"sung war 2","from":"p4","to":"long1","pal":"crimson","pump":PD,"layers":[{"use":"banners","gain":0.22},{"use":"swords","gain":0.65},{"use":"army","gain":0.42},{"use":"slashes","gain":0.6,"width":0.1},{"use":"wake","gain":0.15}]})
A({"name":"raised","from":"long1","to":"after1","pal":"crimson","pump":PD,"layers":[{"use":"banners","gain":0.1},raised(),{"use":"army","gain":0.3},{"use":"wake","gain":0.1}]})
A({"name":"lowered","from":"after1","to":"p5","pal":"crimson","pump":PD,"out":0.25,"layers":[{"use":"banners","gain":0.2},
  {"fx":"preset","name":"sprite","on":"shell","mix":"over","params":dict(SWORD,color="hot@0.95"),"gain":[0.9,0.2]},{"use":"army","gain":0.35},{"use":"slashes","gain":0.5,"width":0.09},{"use":"wake","gain":0.14}]})
HOTB={"color":"hot@0.42"}
def hotb(g=0.42): return {"use":"banners","params":dict(BANNERS,color="hot@0.42"),"gain":g}
A({"name":"white steel","from":"p5","to":"p5b","pal":"hot","pump":PD,"out":0.25,"layers":[hotb(),{"use":"army","pal":"hot","lo":-0.3,"gain":0.35},{"use":"cross"},{"use":"wake","pal":"hot","c":0.25,"gain":0.16}]})
A({"name":"white steel 2","from":"p5b","to":"p6","pal":"hot","pump":PD,"out":0.25,"layers":[hotb(0.3),{"use":"swords","params":dict(SWORDS,color="hot@0.95"),"gain":0.5},{"use":"army","pal":"hot","lo":-0.3,"gain":0.35},{"use":"cross"},{"use":"wake","pal":"hot","c":0.25,"gain":0.16}]})
A({"name":"clash","from":"p6","to":"long2","pal":"crimson","pump":PD,"layers":[{"use":"banners"},{"use":"army"},{"use":"clash"},{"use":"wake","gain":0.14},{"use":"flash"}]})
A({"name":"raised 2","from":"long2","to":"after2","pal":"crimson","pump":PD,"layers":[{"use":"banners","gain":0.12},raised(gain=(0.3,1.0)),{"use":"army","gain":0.35},{"use":"wake","gain":0.1}]})
A({"name":"lowered 2","from":"after2","to":"p7","pal":"crimson","pump":PD,"out":0.25,"layers":[{"use":"banners","gain":0.2},
  {"fx":"preset","name":"sprite","on":"shell","mix":"over","params":dict(SWORD,color="hot@0.95"),"gain":[1.0,0.2]},{"use":"army","gain":0.4},{"use":"clash","gain":0.5},{"use":"wake","gain":0.14}]})
A({"name":"last stand","from":"p7","to":"p7b","pal":"crimson","pump":dict(PD,depth=0.3),"out":0.25,"layers":[{"use":"banners","gain":0.5},{"use":"army","gain":0.6},{"use":"slashes"},{"use":"wake","gain":0.24},{"use":"swords","gain":0.6}]})
A({"name":"last stand 2","from":"p7b","to":"crash","pal":"crimson","pump":dict(PD,depth=0.35),"out":0.25,"layers":[{"use":"banners","gain":0.5},{"use":"army","gain":0.7},{"use":"clash"},{"use":"wake","gain":0.26},{"use":"swords","gain":0.8}]})
# ---- after --------------------------------------------------------------------------------
A({"name":"fall","from":"crash","to":"ash","pal":"crimson","layers":[
  {"fx":"sweep","on":"shell","axis":"y","shape":"p","mode":"fill","from":1.1,"to":-0.15,"soft":0.3,"pal":"crimson","c":[0.85,0.3],"gain":[0.3,0.04]},
  blade(col="hot@0.9",gain=[0.7,0.3]),
  {"fx":"sweep","on":"tubes","axis":"r","shape":"saw","speed":0.5,"mode":"band","from":-0.1,"to":1.9,"width":0.3,"pal":"crimson","c":0.7,"gain":[0.5,0.1],"gate":{"pat":"x...","step":0.5,"decay":1.0}},
  {"fx":"fill","on":"rims","pal":"crimson","c":0.7,"gain":[0.5,0.08],"gate":{"pat":"x...","step":0.5,"decay":1.0}},
  {"fx":"fill","on":"tubes","pal":"crimson","c":0.5,"gain":[0.25,0]}]})
A({"name":"relit","from":"ash","to":"sheathe","pal":"moon","layers":[
  blade(col="steel@0.6",gain=0.3),
  {"use":"candle","gain":[0,0.5]},
  {"use":"glints","gain":[0.1,0.35]},
  {"fx":"fill","on":"rims","pal":"crimson","c":0.5,"gain":[0.15,0],"gate":{"pat":"x...","step":0.5,"decay":1.0}}]})
A({"name":"sheathed","from":"sheathe","to":"gutter","pal":"moon","layers":[
  blade(col="steel@0.6",gain=[0.3,0.15],dx=0,vx=round(-344/secs(4*(268-250)),4)),
  {"use":"flame","gain":{"band":"bass","lo":0.3,"hi":0.75}},
  {"use":"core","gain":{"band":"bass","lo":0.2,"hi":0.55}},
  MOON(-330,140,0.42),
  {"use":"glints","gain":0.35},
  {"use":"night","gain":[0.14,0.06]}]})
A({"name":"gutter","from":"gutter","to":"end","pal":"candle","layers":[
  {"use":"flame","gain":[0.5,0],"rad":[50,16],"y":[112,92]},
  {"use":"core","gain":[0.45,0],"rad":[24,8],"y":[106,88]},
  MOON(140,330,[0.42,0]),
  {"use":"glints","gain":[0.3,0]}]})

# ---- moments -----------------------------------------------------------------------------
H=[]
def sing(at,beats=16,y0=-110,y1=178,hi=0.6,pal="moon",c=0.95,gain=None,tube=None):
    H.append({"name":"sing %g"%at,"at":at,"beats":beats,"pal":pal,"layers":[
      {"fx":"orb","on":"shell","x":0,"y":[y0,y1],"rad":62,"soft":48,"wx":14,"xf":0.125,"c":c,"cgrad":-0.55,"gain":gain if gain is not None else {"band":"mid","lo":0.12,"hi":hi}},
      {"fx":"sweep","on":"tubes","axis":"al","shape":"p","mode":"band","width":0.3,"from":-0.15,"to":1.15,"c":c-0.1,"gain":tube if tube is not None else {"band":"mid","lo":0.06,"hi":0.4}}]})
def ring(at,pal,c=0.8,beats=2,ears=0.4,gain=0.7):
    H.append({"name":"ring %s"%at,"at":at,"beats":beats,"pal":pal,"layers":[{"fx":"fill","on":"ears","c":c,"gain":[ears,0]},{"fx":"sweep","on":"shell","axis":"r","shape":"p","mode":"band","from":0,"to":1.2,"width":0.25,"c":c,"gain":gain}]})
for b in (16,20,24,28,32,36,40): sing(b)
sing(44,8,178,120)      # the long note holds high
sing(46,8,178,-40)      # the slide down
ring("kick","steel",0.75,ears=0.3,gain=0.5)
for b in (64,68,72,76,80,84,88,92): sing(b,hi=0.5)
ring(96,"steel",0.8,4,ears=0.25,gain=0)
H.append({"name":"SHING","at":"climb","beats":2,"pal":"steel","layers":[
  {"fx":"preset","name":"sprite","on":"shell","mix":"max","params":dict(LINE,color="steel@1"),"gain":[1,0.3]},
  {"fx":"sweep","on":"tubes","axis":"al","shape":"p","mode":"band","from":-0.1,"to":1.2,"width":0.4,"c":0.85,"gain":[0.5,0.2]}]})
sing(112.5,14)
sing(116)
sing(120,8)
H.append({"name":"RAISE YOUR WEAPON","at":"title","beats":4*(129.5-122),"layers":[{"fx":"preset","name":"text","on":"face","fit":True,"mix":"over","env":{"in":1,"out":1},"params":{"text":"RAISE YOUR WEAPON","color":"moon@0.92"}}]})
# the three hits that lead in
for b,w in ((129.5,0.5),(129.75,0.25),(129.875,0.25)):
    H.append({"name":"pickup","at":b,"beats":w,"pal":"hot","layers":[{"fx":"fill","on":"ears","c":0.9,"gain":[0.55,0.1]},{"fx":"fill","on":"shell","c":0.3,"gain":[0.2,0]}]})
# the song's one white
H.append({"name":"DROP","at":"drop","beats":2,"layers":[{"fx":"fill","on":"ears","pal":"white","c":1,"gain":[0.5,0]},{"fx":"fill","on":"shell","pal":"white","c":1,"gain":[0.45,0]},{"fx":"sweep","on":"shell","axis":"r","shape":"p","mode":"band","from":0,"to":1.2,"width":0.25,"pal":"hot","c":0.95,"gain":0.8}]})

# ---- the shields: long hits under the whole drop, three layers each ------------------------------------
BP=lambda off:{off+0:"o",off+3:"o",off+4:"o",off+6:"o"}
def shields(at,to,pal="hot",c=0.5,g=0.42,tube=0.6,cross=0.34):
    """Each slash strikes the far ear: its whole shield flares as the blade arrives. The bass plays on the rims."""
    n=4*(to-at)
    # 32 16ths = two bars. Slash left to right at beat 2 lands on ear2, right to left at beat 6 lands on ear1.
    e2=["."]*32; e1=["."]*32
    for k,ch in BP(0).items(): e2[k]=ch; e1[k]=ch
    for k,ch in BP(16).items(): e2[k]=ch; e1[k]=ch
    e2[9]="x"; e1[25]="x"
    H.append({"name":"shields %g"%at,"at":at,"beats":n,"pal":pal,"layers":[
      {"fx":"fill","on":"ear2","c":c,"gain":g,"gate":{"pat":"".join(e2),"step":0.25,"decay":0.55,"floor":0.14}},
      {"fx":"fill","on":"ear1","c":c,"gain":g,"gate":{"pat":"".join(e1),"step":0.25,"decay":0.55,"floor":0.14}},
      {"fx":"blades","on":"tubes","seq":["012","012"],"step":2,"rise":0.12,"keep":0.0,"c":0.3,"ctip":0.95,"gain":tube,"gate":{"pat":"..x.","step":1,"decay":1.1,"floor":0.18}}]})
for a,b in ((130.5,146),(146,162),(162,178),(178,194),(194,210),(210,226),(226,242)):
    pass
shields(130,146); shields(146,161,c=0.45)
ring("p2","hot",0.85,2)
H.append({"name":"riser","at":161.55,"beats":1.8,"pal":"hot","layers":[{"fx":"sweep","on":"shell","axis":"y","shape":"p","mode":"band","from":-0.15,"to":1.1,"width":0.14,"c":0.8,"gain":0.6},{"fx":"sweep","on":"tubes","axis":"al","shape":"p","mode":"band","from":-0.1,"to":1.1,"width":0.3,"c":0.7,"gain":0.5}]})
shields(162,178,g=0.3,tube=0.45); shields(178,194,g=0.3,tube=0.45)
for b in (162.5,166,170,174,178.5,182,186): 
    n=16 if b in (166,170,174,182) else (14 if b%1 else 12)
    sing(b,n,pal="candle",c=0.98,gain=0.75,tube=0.32)
shields(194,210,c=0.6); shields(210,226); shields(226,242,g=0.5,tube=0.7)
ring("p5","hot",0.9,1.5,ears=0)  # the shields hit carries the ears here
def wash(at,right=True,pal="crimson",c=0.8):
    a,b=(-0.2,1.25) if right else (1.25,-0.2)
    # mode fill lights what is below the front: for a wash that travels left to right the front runs up the axis
    H.append({"name":"wash %g"%at,"at":at,"beats":1.5,"pal":pal,"layers":[
      {"fx":"sweep","on":"shell","axis":"x","shape":"p","mode":"band","from":a,"to":b,"width":0.42,"c":c,"gain":0.5},
      {"fx":"sweep","on":"tubes","axis":"al","shape":"p","mode":"band","from":-0.1,"to":1.2,"width":0.35,"c":c,"gain":0.45}]})
for b in (137.5,145.5,153.5): wash(b)
for b in (201.5,209.5): wash(b,pal="hot",c=0.45)
for b in (217.5,233.5,241.5): wash(b)
for b,pl in (("unfurl","crimson"),("p3","crimson"),("p4","crimson"),("p6","hot"),("p7","hot")):
    ring(b,pl,0.8,2,ears=0,gain=0.6)
H.append({"name":"CRASH","at":"crash","beats":3,"layers":[{"fx":"fill","on":"ears","pal":"hot","c":0.7,"gain":[0.55,0]},{"fx":"sweep","on":"shell","axis":"r","shape":"p","mode":"band","from":0,"to":1.3,"width":0.3,"pal":"hot","c":0.85,"gain":0.7}]})

about=("Bars of a measured grid, shows/scenes/%s.beats. This song really changes speed: 112 bars at 128.000 BPM, then a 16-bar accelerando, linear in beats, from 128 to 140, "
 "then 140.000 BPM to the end; the format can only delay a beat, so 140 is the line and every earlier beat carries a hold. Bar 0 is at 0.026 s, the drop is bar 130 at 242.14 s, kick on 1, snare on 3. "
 "Eight minutes in two worlds. A single candle in the dark while the moon crosses from ear to ear; the singer is a pale light that rises through the helmet with each phrase and brightens the flame as it passes. At the kick an army marches along the jaw and the ears are shields being struck. "
 "As the top end returns a blade is drawn: one thin line grows across the brow over sixteen bars. Then the bass leaves and the tempo climbs, the shields ticking faster with it, and the title crosses once, in the quiet. "
 "The drop is crimson and white-hot steel: one slash across the shell on every snare, left then right, and the far ear flares as the blade lands on it. Banners unfurl, the blade swings overhead in arcs, crossed swords stand on the dome. The singer comes back as a flame in the middle of the war, and on each long note a single sword is raised from the jaw. "
 "At the crash it all falls, the candle is lit again, the moon crosses again and the blade slides back into its scabbard before the flame gutters out.")%BASE
tr={"v":1,"show":BASE,"about":about,"lead":0,"marks":MARKS,"palettes":PAL,"motifs":M,"scenes":S,"hits":H}
save(tr,"shows/scenes/%s.scene.json"%BASE)
