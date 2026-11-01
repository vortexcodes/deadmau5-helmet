"""check_placement.py BUILD ASSEMBLY_STEP -- proves the film's placements against the CAD.

Ear halves against assembly/ear_L, ear_R; seam plates against mau5head_ASSEMBLY.step (unzip it first);
then the volume every placed part shares with its neighbours, in mm^3, and the LED map against the ears.
"""
import cadquery as cq, json, numpy as np, os, sys, math
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); B,ASM=sys.argv[1],sys.argv[2]
D=json.load(open(B+"/scene.json"))
def L(p): return cq.Compound.makeCompound(cq.importers.importStep(p).vals())
def mv(sh,m):
    M=np.array(m).reshape(4,4).T
    return sh.transformGeometry(cq.Matrix([list(M[0]),list(M[1]),list(M[2]),list(M[3])]))
def bb(s):
    b=s.BoundingBox(); return np.array([b.xmin,b.xmax,b.ymin,b.ymax,b.zmin,b.zmax])
def vol(a,b):
    try: return a.intersect(b).Volume()
    except Exception as e: return f"ERR {e}"
top=L(R+"/parts/shell_half_TOP.step"); bot=L(R+"/parts/shell_half_BOTTOM.step"); visor=L(R+"/parts/visor.step"); crown=L(R+"/parts/hat_crown_frame.step"); tray=L(R+"/parts/electronics_tray.step")
et=L(R+"/parts/ear_half_top.step"); eb=L(R+"/parts/ear_half_bottom.step"); cap=L(R+"/parts/pivot_cap.step"); plate=L(R+"/parts/seam_plate.step")
print("-- ears against assembly/ear_L, ear_R")
for i,nm in enumerate(["ear_L","ear_R"]):
    a=L(R+f"/assembly/{nm}.step"); 
    mine=cq.Compound.makeCompound([mv(et,D['ears'][i]['m']),mv(eb,D['ears'][i]['m'])])
    print(nm,"bbox diff (mm)",np.round(bb(mine)-bb(a),2),"vol",round(mine.Volume()),round(a.Volume()))
print("-- plates against ASSEMBLY step")
small=[s for s in cq.importers.importStep(ASM).val().Solids() if s.Volume()<3000]
for j,p in enumerate(D['plates']):
    mine=mv(plate,p['m']); c=mine.Center()
    print(" plate",j,"nearest assembly plate centre",round(min((s.Center()-c).Length for s in small),3),"mm")
print("-- intersections, mm^3 (zero means it fits)")
for i,c in enumerate(D['caps']):
    k=mv(cap,c['m']); print(" cap",i,"vs shell top",round(vol(k,top),2),"vs visor",round(vol(k,visor),2),"bbox x",np.round(bb(k)[:2],2))
for j,p in enumerate(D['plates']):
    k=mv(plate,p['m']); print(" plate",j,"vs top",round(vol(k,top),2),"vs bottom",round(vol(k,bot),2))
print(" frame vs top",round(vol(crown,top),2)," tray vs bottom",round(vol(tray,bot),2)," visor vs top",round(vol(visor,top),2), " visor vs bottom",round(vol(visor,bot),2))
for i in range(2):
    m=np.array(D['ears'][i]['m']).reshape(4,4).T
    for t in D['tubes_ear']:
        cyl=cq.Workplane("XY").circle(25.4/2).circle(19.05/2).extrude(t['L']).val()
        M=m@np.array([[1,0,0,t['x']],[0,1,0,0],[0,0,1,t['z0']],[0,0,0,1]])
        cy=cyl.transformGeometry(cq.Matrix([list(M[0]),list(M[1]),list(M[2]),list(M[3])]))
        print(f" ear{i} {t['kind']} x={t['x']:.0f} vs ear halves",round(vol(cy,mv(et,D['ears'][i]['m'])),2),round(vol(cy,mv(eb,D['ears'][i]['m'])),2)," vs shell top",round(vol(cy,top),2))
    print(f" ear{i} halves vs shell top",round(vol(mv(et,D['ears'][i]['m']),top),2),round(vol(mv(eb,D['ears'][i]['m']),top),2))
sp=[(D['hat_pts'][i]) for i in range(4)]
for p in sp:
    z=p['z']
    c=cq.Workplane("XY").workplane(offset=z-30).center(p['x'],p['y']).circle(10).extrude(30).val()
    print(f" stack at ({p['x']},{p['y']}) pad z {p['z']} vs frame",round(vol(c,crown),2),"vs hat envelope",round(vol(c,L(R+'/assembly/hardhat_envelope_REFERENCE.step')),2))
print("-- LED map against the CAD (as-built map, data/cal/pixel_map.csv)")
leds=D['leds']
for reg,ei in (('ear2',0),('ear1',1)):
    e=D['ears'][ei]; u,w,n=map(np.array,(e['u'],e['w'],e['n'])); O=np.array(e['S'])-32*u
    ps=[np.array(l[:3]) for l in leds if l[3]==reg+'_tubes']
    ds=[abs((p-O)@n) for p in ps]; xs=[(p-O)@w for p in ps]
    print(reg,"tube LEDs: off ear plane mean",round(np.mean(ds),1),"max",round(max(ds),1),"x across ear",round(min(xs)),round(max(xs)))
    rs=[np.array(l[:3]) for l in leds if l[3]==reg+'_rim']
    q=[math.hypot(((p-O)@w)/170,((p-O)@u-D['ear_zc'])/177.5) for p in rs]
    print(reg,"rim LEDs: on ellipse radius ratio",round(min(q),3),round(max(q),3))
