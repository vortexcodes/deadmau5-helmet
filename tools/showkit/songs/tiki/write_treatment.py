import json
KICK="x.......x......."
idolp={"sprite":"tiki","y_lo":-108,"y_hi":166,"x_half":171}
tr={"v":1,"show":"TIKI TIKI - Slowed",
"about":"Bars of a measured grid, shows/scenes/TIKI TIKI - Slowed.beats: bar b starts at 1.796 + 1.739 b seconds (137.98 BPM), 183 bars, and at bar 119.5 the track is spliced, so the music comes back 197 ms late and the grid holds still for it. Everything from there is the song's opening again, bar for bar. The bar line is where the phrases turn, with the kick on 1 and 3 and the clap on 2 and 4 with a flick on the and of 2. A night on the island. Torches get lit one tube at a time; the hooks are fire climbing the shell with the ears burning as torches, the kick on the rims and the clap up the tubes. Every breakdown goes out to the lagoon, cold water and moon glints, with one stopped bar of almost nothing, and the title crosses the face once, in the first. The verses are bamboo: upright stalks swaying on the face, the two sides stomping in turn. The big sections wake the idol, a carved mask drawn to fit the LEDs that exist: brow and eyes on the dome, teeth along the jaw, since the middle of the face has no LEDs. It burns in torch colours the first time, at sunset the second, and half fire, half water the third, swapping sides. The song then starts over, so the show does too, and the last big section has everything, with white once. At the end the torches go out one tube at a time and the idol is last to go. Shell layers are kept near the shell's 300 mA and nothing on it pulses faster than a beat.",
"lead":0,
"marks":{"hush":2,"light":3,"hook":5,"hookb":9,"dip":13,"climb":14,"hook2":15,"burn":21,
 "water":25,"stop":26,"still":27,"swell":30,"verse":31,"vlow":37,"vrise":38,"big":39,"bigb":47,"burn2":57,
 "water2":61,"stop2":62,"still2":63,"swell2":66,"verse2":67,"vlow2":73,"vrise2":74,"big2":75,"big2b":83,"burn3":89,
 "water3":93,"stop3":94,"still3":95,"swell3":98,"verse3":99,"vlow3":105,"vrise3":106,"big3":107,"big3b":113,"big3c":117,
 "seam":119.5,"hook3":123,"dip2":127,"climb2":128,"hook4":129,"burn4":135,
 "water4":139,"stop4":140,"still4":141,"swell4":144,"verse4":145,"vlow4":151,"vrise4":152,"final":153,"final2":161,
 "wind":169,"out1":173,"out2":176,"out3":178,"end":181},
"palettes":{
 "ember":[[0,0,0],[40,3,0],[140,18,0],[255,70,0]],
 "torch":[[0,0,0],[70,6,0],[220,40,0],[255,120,10],[255,190,60]],
 "lagoon":[[0,0,0],[0,20,30],[0,90,110],[0,190,170],[110,240,200]],
 "moon":[[0,0,0],[20,40,70],[120,170,210],[225,240,255]],
 "bamboo":[[0,0,0],[24,30,0],[110,130,0],[200,210,30]],
 "dusk":[[0,0,0],[50,0,60],[200,0,110],[255,50,60],[255,150,30]],
 "white":[[255,90,0],[255,190,80],[255,255,255]]},
"motifs":{
 "flame":{"fx":"grad","on":"shell","axis":"y","axis2":"x","scale":1.6,"speed":-0.25,"warp":0.22,"wscale":1.4,"wspeed":0.125,"lo":0,"hi":0.85,"gain":0.22},
 "torch":{"fx":"grad","on":"tubes","axis":"al","axis2":"al","scale":1.2,"speed":-0.5,"warp":0.15,"wscale":2,"wspeed":0.25,"lo":0.1,"hi":0.95,"gain":0.3},
 "kick":{"fx":"fill","on":"rims","c":0.8,"gain":0.6,"gate":{"pat":KICK,"step":0.25,"decay":0.6}},
 "clap":{"fx":"blades","on":"tubes","seq":["012"],"step":1,"rise":0.12,"keep":0,"c":0.6,"ctip":1,"gain":0.42,"gate":{"pat":".x.x","step":1,"decay":0.75}},
 "flick":{"fx":"fill","on":"tube1","c":0.9,"gain":0.35,"gate":{"pat":"......x.........","step":0.25,"decay":0.25}},
 "idol":{"fx":"preset","name":"sprite","on":"shell","mix":"over","params":dict(idolp,color="torch@0.75"),"gain":0.24,"gate":{"pat":KICK,"step":0.25,"decay":1.5,"floor":0.5}},
 "embers":{"fx":"sparks","on":"all","rate":2,"life":0.5,"c":0.9,"gain":{"band":"high","lo":0,"hi":0.7}},
 "water":{"fx":"grad","on":"shell","axis":"x","axis2":"y","speed":0.0625,"warp":0.2,"wspeed":0.03125,"lo":0,"hi":0.6,"pal":"lagoon","gain":0.14},
 "glint":{"fx":"sparks","on":"shell","rate":0.5,"life":3,"loop":6,"seed":11,"nbr":0.6,"pal":"moon","c":0.85,"spread":0.1,"gain":0.5},
 "tide":[{"fx":"sweep","on":"ear1","axis":"al","shape":"tri","mode":"fill","speed":0.125,"from":-0.15,"to":1.15,"soft":0.2,"pal":"lagoon","c":0.4,"cgrad":0.45,"gain":0.24},
         {"fx":"sweep","on":"ear2","axis":"al","shape":"tri","mode":"fill","speed":0.125,"from":1.15,"to":-0.15,"soft":0.2,"pal":"lagoon","c":0.4,"cgrad":0.45,"gain":0.24}],
 "stalks":{"fx":"grad","on":"shell","axis":"x","axis2":"y","scale":3.5,"warp":0.06,"wscale":0.8,"wspeed":0.125,"lo":0,"hi":0.8,"pal":"bamboo","gain":0.2,"gate":{"pat":"x","step":1,"decay":0.8,"floor":0.5}},
 "stompL":{"fx":"fill","on":"ear1","pal":"bamboo","c":0.75,"gain":0.35,"gate":{"pat":"x.x.","step":1,"decay":0.7}},
 "stompR":{"fx":"fill","on":"ear2","pal":"bamboo","c":0.75,"gain":0.35,"gate":{"pat":".x.x","step":1,"decay":0.7}},
 "stomps":[{"use":"stompL"},{"use":"stompR"}],
 "rise":{"fx":"sweep","on":"shell","axis":"y","shape":"p","mode":"fill","soft":0.15,"from":-0.1,"to":1.05},
 "front":{"fx":"sweep","on":"shell","axis":"y","shape":"p","mode":"band","width":0.12,"from":-0.1,"to":1.05},
 "drain":{"fx":"sweep","on":"shell","axis":"y","shape":"p","mode":"fill","soft":0.2,"from":1.1,"to":-0.15},
 "ring":{"fx":"sweep","on":"shell","axis":"r","shape":"p","mode":"band","from":0,"to":1.2,"width":0.25},
 "blow":{"fx":"fill","on":"ears","c":0.8,"gain":[0.28,0]},
 "lit":[{"use":"flame"},{"use":"torch"},{"use":"kick"},{"use":"clap"}],
 "lift":{"fx":"blades","seq":["0","1","2","012"],"rise":0.2,"c":0.4,"ctip":0.95}},
"scenes":[]}
S=tr["scenes"].append
PUMP={"pat":KICK,"step":0.25,"depth":0.2,"decay":0.5}
HARD=dict(PUMP,depth=0.3)
# --- the torches get lit
S({"name":"embers","from":-0.75,"to":"hush","pal":"ember","layers":[
  {"fx":"sparks","on":"shell","rate":0.5,"life":3,"loop":7,"seed":3,"nbr":0.6,"c":0.7,"spread":0.25,"gain":[0.2,0.55],"env":{"in":4}},
  {"use":"torch","pal":"ember","hi":0.4,"speed":-0.125,"gain":0.25,"env":{"in":6}}]})
S({"name":"hush","from":"hush","to":"light","pal":"ember","layers":[
  {"fx":"sparks","on":"shell","rate":0.5,"life":3,"loop":7,"seed":3,"nbr":0.6,"c":0.7,"spread":0.25,"gain":[0.5,0.2]},
  {"use":"torch","pal":"ember","hi":0.4,"speed":-0.125,"gain":[0.25,0.08]}]})
S({"name":"lighting","from":"light","to":"hook","pal":"torch","out":0.5,"layers":[
  {"use":"lift","step":{"light":2,"4":1},"keep":0.45,"gain":[0.25,0.6]},
  {"use":"rise","c":[0.25,0.6],"gain":[0.02,0.1]},
  {"use":"front","c":[0.45,0.9],"gain":[0.1,0.35]}]})
# --- the hook: fire climbing, the ears as torches
S({"name":"hook","from":"hook","to":"hookb","pal":"torch","pump":PUMP,"layers":[{"use":"lit"},{"use":"flick"}]})
S({"name":"hookb","from":"hookb","to":"dip","like":"hook","add":[{"use":"idol","gain":{"hookb":0,"10":0.24},"env":{"in":4}}]})
S({"name":"dip","from":"dip","to":"climb","pal":"ember","layers":[
  {"use":"drain","c":[0.75,0.3],"gain":0.1},
  {"fx":"fill","on":"rims","c":0.85,"gain":{"band":"bass","punch":True,"lo":0.05,"hi":0.5}},
  {"use":"torch","pal":"ember","hi":0.5,"gain":[0.3,0.12]}]})
S({"name":"climb","from":"climb","to":"hook2","pal":"torch","layers":[
  {"use":"rise","c":[0.2,0.6],"gain":[0.02,0.09]},
  {"use":"front","c":[0.45,0.9],"gain":[0.1,0.4]},
  {"use":"lift","step":{"climb":1,"14.5":0.5},"gain":[0.25,0.6]},
  {"use":"kick","gain":0.4}]})
S({"name":"hook2","from":"hook2","to":"burn","pal":"torch","pump":PUMP,"layers":[{"use":"lit"},{"use":"idol"},{"use":"embers"}]})
S({"name":"burn","from":"burn","to":"water","pal":"torch","layers":[
  {"use":"flame","gain":[0.2,0.03],"hi":[0.85,0.5]},
  {"use":"torch","gain":[0.3,0.06],"hi":[0.95,0.5]},
  {"use":"kick","gain":{"burn":0.5,"23":0.3,"24.5":0}},
  {"use":"clap","gain":{"burn":0.4,"23":0}},
  {"use":"embers","gain":{"band":"high","lo":0,"hi":0.5},"rate":1}]})
# --- the lagoon, and the title
LAGOON=[{"use":"water"},{"use":"glint"},{"use":"tide"}]
S({"name":"lagoon","from":"water","to":"stop","pal":"lagoon","layers":[{"use":"water","env":{"in":3}},{"use":"glint","env":{"in":2}},{"use":"tide","env":{"in":3}}]})
S({"name":"stop","from":"stop","to":"still","pal":"moon","layers":[{"use":"glint"},{"use":"water","gain":[0.14,0.04],"hi":0.35}]})
S({"name":"still","from":"still","to":"swell","pal":"lagoon","layers":LAGOON})
S({"name":"swell","from":"swell","to":"verse","pal":"lagoon","out":0.25,"layers":[
  {"use":"rise","c":[0.25,0.55],"gain":[0.02,0.08]},{"use":"front","c":[0.5,0.95],"gain":[0.1,0.35]},{"use":"tide","gain":[0.3,0.5]}]})
# --- the verse: bamboo and stomping
S({"name":"verse","from":"verse","to":"vlow","pal":"bamboo","pump":{"pat":"x...","step":0.25,"depth":0.12,"decay":0.5},"layers":[{"use":"stalks"},{"use":"stomps"},{"use":"clap","gain":0.3},{"use":"glint","pal":"bamboo","gain":{"band":"mid","punch":True,"lo":0.1,"hi":0.6}}]})
S({"name":"vlow","from":"vlow","to":"vrise","pal":"bamboo","layers":[{"use":"stalks","gain":[0.2,0.08]},{"use":"stomps","gain":0.25}]})
S({"name":"vrise","from":"vrise","to":"big","pal":"torch","out":0.5,"layers":[
  {"use":"rise","c":[0.2,0.6],"gain":[0.02,0.09]},{"use":"front","c":[0.45,0.9],"gain":[0.1,0.4]},
  {"use":"lift","step":{"vrise":1,"38.5":0.5},"gain":[0.25,0.6]}]})
# --- the idol wakes
S({"name":"big","from":"big","to":"bigb","pal":"torch","pump":HARD,"layers":[{"use":"lit"},{"use":"idol"},{"use":"flick"}]})
S({"name":"bigb","from":"bigb","to":"burn2","pal":"torch","pump":HARD,"layers":[{"use":"lit"},{"use":"idol"},{"use":"embers"}]})
S({"name":"burn2","from":"burn2","to":"water2","like":"burn"})
# --- the second lagoon: the idol is still there
S({"name":"lagoon2","from":"water2","to":"stop2","like":"lagoon"})
S({"name":"stop2","from":"stop2","to":"still2","like":"stop"})
S({"name":"watched","from":"still2","to":"swell2","pal":"lagoon","layers":[{"use":"water","gain":0.08},{"use":"tide"},{"use":"idol","params":dict(idolp,color="moon@0.7"),"gain":[0,0.16],"gate":None}]})
S({"name":"swell2","from":"swell2","to":"verse2","like":"swell"})
S({"name":"verse2","from":"verse2","to":"vlow2","like":"verse"})
S({"name":"vlow2","from":"vlow2","to":"vrise2","like":"vlow"})
S({"name":"vrise2","from":"vrise2","to":"big2","like":"vrise","pal":"dusk","patch":{"2":{"step":{"vrise2":1,"74.5":0.5}}}})
# --- sunset
SUN={"flame":{"use":"flame","pal":"dusk","hi":0.95},"torch":{"use":"torch","pal":"dusk"},"idol":{"use":"idol","params":dict(idolp,color="dusk@0.95")}}
S({"name":"sunset","from":"big2","to":"big2b","pal":"dusk","pump":HARD,"layers":[SUN["flame"],SUN["torch"],{"use":"kick"},{"use":"clap"},SUN["idol"],{"use":"flick"}]})
S({"name":"sunsetb","from":"big2b","to":"burn3","pal":"dusk","pump":HARD,"layers":[SUN["flame"],SUN["torch"],{"use":"kick"},{"use":"clap"},SUN["idol"],{"use":"embers"}]})
S({"name":"burn3","from":"burn3","to":"water3","like":"burn","pal":"dusk"})
# --- the third lagoon: faster water, more moon
S({"name":"lagoon3","from":"water3","to":"stop3","like":"lagoon"})
S({"name":"stop3","from":"stop3","to":"still3","like":"stop"})
S({"name":"moonlit","from":"still3","to":"swell3","pal":"lagoon","layers":[{"use":"water","speed":0.125},{"use":"glint","rate":1,"life":2.5,"gain":0.6},{"use":"tide"}]})
S({"name":"swell3","from":"swell3","to":"verse3","like":"swell"})
S({"name":"verse3","from":"verse3","to":"vlow3","like":"verse"})
S({"name":"vlow3","from":"vlow3","to":"vrise3","like":"vlow"})
S({"name":"vrise3","from":"vrise3","to":"big3","like":"vrise","patch":{"2":{"step":{"vrise3":1,"106.5":0.5}}}})
# --- fire and water, swapping sides, then the song starts over
def duel(a,b):
    return [{"use":"flame","on":a[0]},{"use":"torch","on":a[1]},{"use":"water","on":b[0],"hi":0.8,"speed":0.125},
            {"fx":"grad","on":b[1],"axis":"al","axis2":"al","scale":1.2,"speed":0.25,"warp":0.1,"wscale":2,"wspeed":0.25,"lo":0.1,"hi":0.95,"pal":"lagoon","gain":0.3},
            {"use":"kick"},{"use":"clap","pal":"white","c":0.3,"gain":0.36}]
S({"name":"duel","from":"big3","to":"big3b","pal":"torch","pump":HARD,"layers":duel(("left","ear1"),("right","ear2"))})
S({"name":"duel2","from":"big3b","to":"big3c","pal":"torch","pump":HARD,"layers":duel(("right","ear2"),("left","ear1"))})
S({"name":"duel3","from":"big3c","to":"seam","pal":"torch","pump":HARD,"layers":duel(("left","ear1"),("right","ear2"))})
S({"name":"hook3","from":"seam","to":"hook3","pal":"torch","pump":PUMP,"layers":[{"use":"lit"},{"use":"idol","gain":0.16},{"use":"flick"}]})
S({"name":"hook3b","from":"hook3","to":"dip2","like":"hook3","patch":{"1":{"gain":0.24}}})
S({"name":"dip2","from":"dip2","to":"climb2","like":"dip"})
S({"name":"climb2","from":"climb2","to":"hook4","like":"climb","patch":{"2":{"step":{"climb2":1,"128.5":0.5}}}})
S({"name":"hook4","from":"hook4","to":"burn4","like":"hook2"})
S({"name":"burn4","from":"burn4","to":"water4","like":"burn"})
# --- the last lagoon
S({"name":"lagoon4","from":"water4","to":"stop4","like":"lagoon"})
S({"name":"stop4","from":"stop4","to":"still4","like":"stop"})
S({"name":"still4","from":"still4","to":"swell4","pal":"lagoon","layers":[{"use":"water"},{"use":"glint"},{"use":"tide"},{"use":"idol","params":dict(idolp,color="lagoon@0.8"),"gain":[0,0.14],"gate":None}]})
S({"name":"swell4","from":"swell4","to":"verse4","like":"swell"})
S({"name":"verse4","from":"verse4","to":"vlow4","like":"verse"})
S({"name":"vlow4","from":"vlow4","to":"vrise4","like":"vlow"})
S({"name":"vrise4","from":"vrise4","to":"final","like":"vrise","patch":{"2":{"step":{"vrise4":1,"152.5":0.5}}}})
# --- everything
S({"name":"final","from":"final","to":"final2","pal":"torch","pump":dict(PUMP,depth=0.35),"layers":[{"use":"flame","hi":0.95},{"use":"torch","gain":0.34},{"use":"kick","c":0.95,"gain":0.7},{"use":"clap","rim":0.5},{"use":"idol","params":dict(idolp,color="torch@0.95")},{"use":"embers"}]})
S({"name":"final2","from":"final2","to":"wind","like":"final","patch":{"0":{"pal":"dusk"},"1":{"pal":"dusk"},"4":{"params":dict(idolp,color="dusk@0.95")},"5":{"rate":4,"life":0.6}}})
# --- the torches go out
S({"name":"wind","from":"wind","to":"out1","pal":"torch","layers":[{"use":"flame","gain":[0.14,0.04],"hi":[0.85,0.5]},{"use":"torch","gain":[0.28,0.2]},{"use":"kick","gain":[0.45,0.1]},{"use":"idol","gain":[0.18,0.1],"gate":None}]})
S({"name":"out","from":"out1","to":"end","pal":"ember","layers":[
  {"use":"torch","on":"tube0","gain":{"out1":0.22,"out2":0}},
  {"use":"torch","on":"tube1","gain":{"out1":0.22,"out3":0}},
  {"use":"torch","on":"tube2","gain":{"out1":0.22,"out3":0.2,"179":0.2,"180":0}},
  {"use":"idol","params":dict(idolp,color="ember@0.8"),"gain":{"out1":0.1,"out3":0.09,"end":0},"gate":None}]})
HIT=lambda name,at,pal,c=0.8,beats=2:{"name":name,"at":at,"beats":beats,"pal":pal,"layers":[{"use":"blow","c":c},{"use":"ring","c":c,"gain":0.7}]}
tr["hits"]=[HIT("LIT","hook","torch"),HIT("HOOK 2","hook2","torch"),
 {"name":"TIKI TIKI","at":26.5,"beats":18,"layers":[{"fx":"preset","name":"text","on":"face","fit":True,"mix":"over","env":{"in":2,"out":3},"params":{"text":"TIKI TIKI","color":"moon@0.75"}}]},
 HIT("VERSE","verse","bamboo"),HIT("IDOL","big","torch",0.95),
 HIT("VERSE 2","verse2","bamboo"),HIT("SUNSET","big2","dusk",0.95),
 HIT("VERSE 3","verse3","bamboo"),HIT("DUEL","big3","torch",0.95),
 HIT("SWAP","big3b","lagoon",0.9,1),HIT("SWAP 2","big3c","torch",0.9,1),
 HIT("OVER","seam","torch",0.95),HIT("HOOK 4","hook4","torch"),
 HIT("VERSE 4","verse4","bamboo"),
 {"name":"FINAL","at":"final","beats":2,"layers":[{"fx":"fill","on":"ears","pal":"white","c":1,"gain":[0.22,0]},{"fx":"fill","on":"shell","pal":"white","c":1,"gain":[0.25,0]},{"use":"ring","pal":"white","c":1}]}]
# one thing per line, so it can be edited by hand
def block(items,key=None):
    return "[\n"+",\n".join("  "+json.dumps(x) for x in items)+"\n ]"
out=['{','"v":1,','"show":'+json.dumps(tr["show"])+',','"about":'+json.dumps(tr["about"])+',','"lead":0,','"marks":'+json.dumps(tr["marks"])+',']
out.append('"palettes":{\n'+",\n".join("  %s: %s"%(json.dumps(k),json.dumps(v)) for k,v in tr["palettes"].items())+'\n },')
out.append('"motifs":{\n'+",\n".join("  %s: %s"%(json.dumps(k),json.dumps(v)) for k,v in tr["motifs"].items())+'\n },')
out.append('"scenes":'+block(tr["scenes"])+',')
out.append('"hits":'+block(tr["hits"]))
out.append('}')
open('shows/scenes/TIKI TIKI - Slowed.scene.json','w').write("\n".join(out)+"\n")
json.load(open('shows/scenes/TIKI TIKI - Slowed.scene.json'))
print('scenes',len(tr["scenes"]),'hits',len(tr["hits"]))
