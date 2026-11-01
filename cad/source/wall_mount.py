"""
mau5head wall mount — holds the helmet two ways at once:
  RIM:    a 4-arm cradle ("spider") whose felt-lined pads cup the outside of the shell just above the neck cut
  CENTRE: a post rising through the neck opening to a head-form dome that the hard hat's suspension sits on
          (the same way it sits on your head), so the helmet can't tip or twist off the pads.

Frame = the helmet frame used by mau5head_hat.py: sphere centre at the origin, +Z up, -Y is the FRONT (face),
+Y the back.  On the wall the face looks out into the room, so the wall is behind the helmet at +Y.

Parts (all print on a Prusa XL, PETG, 4+ perimeters, 30%+ infill):
  wallmount_bracket.step   wall plate + arm + gusset   print on its side (the big flat Y-Z face down)
  wallmount_cradle.step    hub + post socket + 4 arms + 4 pads   print flat, pads up
  wallmount_post.step      Ø40 tube, adjustment holes every 10 mm   print standing
  wallmount_dome.step      head-form dome with a socket underneath  print dome-up on its flat base
Hardware: 3 × #10 × 2½" wood screws into a stud · 2 × 10-32 × 1" + 2 heat-set inserts (cradle → arm)
          1 × 1/4"-20 × 2½" bolt + nut (post height pin) · self-adhesive felt for the pads
"""
import math, os, sys
import cadquery as cq

OUT = sys.argv[1] if len(sys.argv) > 1 else "out/"
os.makedirs(OUT, exist_ok=True)

# ── helmet (from mau5head_hat.py) ──
R_O      = 177.17          # shell outer radius
NECK_Z   = -143.3          # flat neck cut (CAD). Pads also work if the neck was trimmed up to ~ -130
CONN_AZ  = 68.0            # GX16 power jack on the back-right, lat -45: keep pads and arms away from it
PIX_LOW_Z = -117.5         # bottom edge of the lowest LED row: pads stay below it

# ── layout ──
WALL_GAP   = 28.0          # helmet back to wall
WALL_Y     = R_O + WALL_GAP            # wall plane
PAD_R0, PAD_R1 = 105.0, 131.0          # pad contact band, radius from the vertical axis  (z = -142.7 .. -119.3)
PAD_W      = 32.0                      # pad width (tangential)
PAD_AZ     = (0.0, 90.0, 180.0, 270.0) # +x side, back (over the arm), -x side, front
FELT       = 1.0                       # felt thickness: pad face sits this far off the shell
ARM_TOP_Z  = -170.0                    # top of the bracket arm = underside of the cradle
CR_T       = 14.0                      # cradle arm thickness
HUB_D      = 70.0
POST_D, POST_WALL = 40.0, 4.0
SOCKET_H   = 60.0
PIN_D      = 6.6                       # 1/4" bolt
HEAD_TOP_Z = 90.0                      # top of the wearer's head: ~30 mm under the hat's inside crown, as on the Pyramex the shell was sized for
DOME_A, DOME_B, DOME_H, DOME_T = 70.0, 87.5, 65.0, 3.0   # head form: 140 x 175 base (passes the 165 x 195 neck hole)
ADJ_STEPS  = 5                         # post holes: nominal ±20 mm in 10 mm steps

def sph_z(r):           # z of the shell's outer surface (lower half) at radius r from the axis
    return -math.sqrt(R_O**2 - r**2)

# ═══ cradle (spider) ═══
z0 = ARM_TOP_Z
SOCKET_H = 60.0
# what the helmet occupies: everything inside the shell's outer skin (+ felt) above the neck cut, except the neck hole itself
NECK_A, NECK_B = 80.0, 95.0           # a little inside the 165 x 195 neck hole
envelope = (cq.Workplane("XY").sphere(R_O + FELT)
            .intersect(cq.Workplane("XY").workplane(offset=NECK_Z - 0.5).rect(600, 600).extrude(400))
            .cut(cq.Workplane("XY").workplane(offset=NECK_Z - 5).ellipse(NECK_A, NECK_B).extrude(400)))
arms = None
for az in PAD_AZ:
    arm = (cq.Workplane("XY").workplane(offset=z0).rect(PAD_R1 + 4, 26.0, centered=(False, True)).extrude(CR_T)
           .edges("|Z").fillet(3.0).rotate((0, 0, 0), (0, 0, 1), az))
    pr = (PAD_R0 + PAD_R1) / 2
    pad = (cq.Workplane("XY").workplane(offset=z0).center(pr, 0)
           .rect(PAD_R1 - PAD_R0 + 6, PAD_W).extrude(PIX_LOW_Z - 2.0 - z0)
           .edges("|Z").fillet(5.0).rotate((0, 0, 0), (0, 0, 1), az))
    piece = arm.union(pad)
    arms = piece if arms is None else arms.union(piece)
cradle = arms.cut(envelope)                                            # concave felt seats, each the shape of the shell
cradle = cradle.union(cq.Workplane("XY").workplane(offset=z0).circle(HUB_D/2).extrude(CR_T))
cradle = cradle.union(cq.Workplane("XY").workplane(offset=z0).circle(POST_D/2 + 6.0).extrude(SOCKET_H))
cradle = cradle.cut(cq.Workplane("XY").workplane(offset=z0 - 1).circle(POST_D/2 + 0.3).extrude(SOCKET_H + 2))
pin_z = z0 + SOCKET_H - 8.0
cradle = cradle.cut(cq.Workplane("YZ").workplane(offset=-60).center(0, pin_z).circle(PIN_D/2).extrude(120))
BOLT_YS = (55.0, 85.0)                  # two 10-32 down through the back arm into inserts in the bracket arm
for by in BOLT_YS:
    cradle = cradle.cut(cq.Workplane("XY").workplane(offset=z0 - 1).center(0, by).circle(5.2/2).extrude(CR_T + 2))
    cradle = cradle.cut(cq.Workplane("XY").workplane(offset=z0 + CR_T - 5.5).center(0, by).circle(9.5/2).extrude(10))
# keep the back pad clear of the GX16 plug (az 68): check below
cradle_s = cradle.val()

# ═══ bracket: wall plate + arm + gusset, one Y-Z profile extruded ±BR_W/2 in X ═══
BR_W   = 50.0
PLATE_T = 10.0
ARM_H  = 30.0
ARM_Y0 = 30.0                 # arm reaches from the wall to here (under the cradle's back arm, clear of the post)
PL_TOP, PL_BOT = ARM_TOP_Z + 66.0, ARM_TOP_Z - ARM_H - 140.0
y_w = WALL_Y
prof = (cq.Workplane("YZ")
        .moveTo(y_w + PLATE_T, PL_TOP)
        .lineTo(y_w, PL_TOP)
        .lineTo(y_w, ARM_TOP_Z)                      # front face of the plate up top, then the arm's top surface
        .lineTo(ARM_Y0, ARM_TOP_Z)
        .lineTo(ARM_Y0, ARM_TOP_Z - ARM_H)
        .lineTo(y_w - 120.0, ARM_TOP_Z - ARM_H)      # arm underside, then the gusset diagonal down to the plate
        .lineTo(y_w, PL_BOT + 30.0)
        .lineTo(y_w, PL_BOT)
        .lineTo(y_w + PLATE_T, PL_BOT)
        .close())
bracket = prof.extrude(BR_W/2, both=True)
# the plate is wider than the arm: extra plate wings for 3 screws
plate = cq.Workplane("XZ").workplane(offset=-(y_w + PLATE_T)).center(0, (PL_TOP + PL_BOT)/2).rect(BR_W, PL_TOP - PL_BOT).extrude(PLATE_T)
bracket = bracket.union(plate)
# lighten the gusset web (keeps 8 mm flanges)
web = (cq.Workplane("YZ").moveTo(y_w - 12, ARM_TOP_Z - ARM_H - 10).lineTo(y_w - 92, ARM_TOP_Z - ARM_H - 10)
       .lineTo(y_w - 12, PL_BOT + 52).close().extrude(BR_W/2 - 8, both=True))
bracket = bracket.cut(web)
# wall screws: 3 in a vertical line (one stud), countersunk on the room side, clear of the arm and gusset
for z in (PL_TOP - 12.0, PL_TOP - 38.0, PL_BOT + 14.0):     # two above the arm, one below the gusset: every head reachable
    hole = cq.Workplane("XZ").workplane(offset=-(y_w + PLATE_T + 1)).center(0, z).circle(2.6).extrude(PLATE_T + 2)
    cs = (cq.Workplane("XZ").workplane(offset=-(y_w + 0.01)).center(0, z).circle(5.0)
          .workplane(offset=-4.2).circle(2.6).loft())     # 82° countersink for a #10 wood screw, head flush on the helmet side
    bracket = bracket.cut(hole).cut(cs)
# insert pilots for the cradle bolts (from the arm's top face)
for by in BOLT_YS:
    bracket = bracket.cut(cq.Workplane("XY").workplane(offset=ARM_TOP_Z - 9.0).center(0, by).circle(6.4/2).extrude(10))
bracket = bracket.edges("|X").fillet(2.0)
bracket_s = bracket.val()

# ═══ post: Ø40 tube. Pin positions raise it 0/10/20/30/40 mm off the arm; nominal = +20 puts the dome top at HEAD_TOP_Z ═══
dome_base_z = HEAD_TOP_Z - DOME_H
RAISES = [0.0, 10.0, 20.0, 30.0, 40.0]
NOM = 20.0
POST_L = (dome_base_z + 30.0) - (z0 + NOM)          # 30 mm of the post sits inside the dome's socket
post = cq.Workplane("XY").circle(POST_D/2).circle(POST_D/2 - POST_WALL).extrude(POST_L)
for r in RAISES:
    zz = pin_z - (z0 + r)                           # pin height in post coordinates for this raise
    post = post.cut(cq.Workplane("YZ").workplane(offset=-30).center(0, zz).circle(PIN_D/2).extrude(60))
post_s = post.val()
post_bot = z0 + NOM

# ═══ dome: solid head form (print it with ~10% infill and 3 walls) + Ø40 socket from underneath ═══
wp = cq.Workplane("XY")
_prev = 0.0
for i, t in enumerate((0, 15, 30, 45, 58, 70, 80, 87)):
    tr = math.radians(t); z = DOME_H*math.sin(tr)
    wp = (wp.ellipse(DOME_A*math.cos(tr), DOME_B*math.cos(tr)) if i == 0
          else wp.workplane(offset=z - _prev).ellipse(DOME_A*math.cos(tr), DOME_B*math.cos(tr)))
    _prev = z
dome = wp.loft(ruled=False).val()
dome = dome.cut(cq.Workplane("XY").workplane(offset=-1).circle(POST_D/2 + 0.3).extrude(31).val()).clean()
dome_s = dome.translate(cq.Vector(0, 0, dome_base_z))

# ═══ export ═══
for nm, s in (("wallmount_bracket", bracket_s), ("wallmount_cradle", cradle_s), ("wallmount_post", post_s), ("wallmount_dome", dome_s)):
    cq.exporters.export(cq.Workplane("XY").newObject([s]), OUT + nm + ".step")
    cq.exporters.export(cq.Workplane("XY").newObject([s]), OUT + nm + ".stl", tolerance=0.05, angularTolerance=0.1)
    bb = s.BoundingBox()
    print(f"{nm:20s} valid={s.isValid()} solids={len(s.Solids())} vol={s.Volume()/1000:6.1f} cm3  size {bb.xlen:.0f} x {bb.ylen:.0f} x {bb.zlen:.0f} mm")
post_placed = post_s.translate(cq.Vector(0, 0, post_bot))   # nominal: middle pin hole
asm = cq.Assembly()
for nm, s, c in (("bracket", bracket_s, (0.3, 0.3, 0.35)), ("cradle", cradle_s, (0.3, 0.3, 0.35)),
                 ("post", post_placed, (0.55, 0.55, 0.6)), ("dome", dome_s, (0.55, 0.55, 0.6))):
    asm.add(cq.Workplane("XY").newObject([s]), name=nm, color=cq.Color(*c))
asm.save(OUT + "wallmount_ASSEMBLY.step")
print("pin hole z (cradle):", pin_z, " dome top nominal:", HEAD_TOP_Z, " wall plane y:", WALL_Y)
