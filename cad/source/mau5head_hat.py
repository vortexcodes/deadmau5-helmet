"""
mau5head_hat.py  (v18)  —  the whole helmet as parametric CadQuery solids → STEP.

Run:   pip install cadquery numpy        then   python3 mau5head_hat.py          (everything, ~90 s)
                                                python3 mau5head_hat.py visor    (visor + ears + hat parts, ~25 s)
Out (in OUT):  shell.step, shell_half_TOP/BOTTOM.step (+ designed supports), ear_L/R.step, ear_half_top/bottom.step,
               visor.step (solid; perforate it with visor_perforate.py), pivot_cap.step, seam_plate.step,
               hat_crown_frame.step, hat_spacers.step, hat_drill_template.step, electronics_tray.step,
               hardhat_envelope_REFERENCE.step, mau5head_ASSEMBLY.step, pixel_map.csv

Frame: origin = sphere centre.  +Z up.  -Y = front (mouth).  ±X = visor pivot axis.  All mm.  Every number below is a knob.

History (details in docs/cad-design.md):
  v2–v10  shell, LED channel grid, ears on the original socket axis, internal visor, hard-hat mount
  v11     the version the shell was printed from (neck later trimmed by hand)
  v13     no LEDs on the visor: troughs and visor wire holes removed
  v14     even visor mesh out to the pivots; Ø40 pivot pad, Ø56 hub disc, edge rims; pivot cap that captures the pad
  v15–17  ear bottom half: JST-size wire path → open grooves in the hidden faces, thicker peg
  v18     crown FRAME for the 3M SecureFit hat (rides higher): spacer stacks set the height at assembly
"""
import math, csv, time, os
import numpy as np
import cadquery as cq

# ───────────────────────────── PARAMETERS ────────────────────────────────────
R_O   = 177.17          # outer radius (OD 354.3, measured from your file)
WALL  = 5.0             # 5.0 so the pixel window keeps a 2 mm skin (4-5 perimeters) over a 2 mm LED pocket
NECK_Z = -143.3         # flat neck cut below centre (measured)

# mouth wedge: apex on the X axis, opens toward -Y, angles about -Y
MOUTH_EL_TOP, MOUTH_EL_BOT = 10.0, -35.0
MOUTH_HALF_X = R_O + 10 # wedge runs through the poles: the grin comes to a point at each side, like the original

# LED matrix
LEDS_PER_M   = 60
LAT_MIN = -40.0
LAT_MAX_ALL, LAT_MAX_ALL2, LAT_MAX_EVEN, LAT_MAX_QUARTER = 45.0, 55.0, 65.0, 76.0   # tiers: full (9 mm pockets) / full (8 mm pockets) / even channels / every 4th
PIX_HI = 8.0                                                                          # pocket size above LAT_MAX_ALL (adjacent grooves nearly touch there)
GROOVE_W, GROOVE_D = 10.6, 1.0      # shallow: locates the strip; the LED stands proud into the pocket
PIX, SKIN = 9.0, 2.0                # 2 mm skin = 4-5 walls; MIN_T below is enforced

# ── visor (INTERNAL, like the original) ──
VISOR_R      = 165.0    # outer radius of the panel — the original's, sits 8 mm inside the wall
VISOR_T      = 2.0      # original thickness
VISOR_MARGIN     = 3.5   # bottom overlap past the mouth edge (deg)
VISOR_MARGIN_TOP = 6.0   # top overlap — deeper, so the hold-closed magnets have wall to mate with
OPEN_ANGLE   = 40.0      # visor up-swing; the grab lip hits the upper mouth lip just past this
LIP_HALF_X   = 60.0      # grab lip on the visor bottom: ± this wide, protrudes past the shell OD
LIP_PROUD    = 6.0
VISOR_LEDS  = False      # visor edge-light troughs + wire holes. False = plain perforated visor, no visor wiring
TUBE_D      = 6.0        # clear silicone/PVC tube OD, the light pipe along each visor edge
TUBE_CLR    = 0.4
LG_HALF_X   = 140.0      # light-guide troughs span ± this (same as the mesh)
VWIRE_X, VWIRE_EL = 150.0, -10.0 # visor wire exit hole (near the +X pivot, in the solid side band)
SWIRE_EL = 17.0                  # shell wire hole above the upper lip (pixel-free band), same x
EAR_WIRE_D = 8.0

MAG_D, MAG_T = 6.4, 3.1  # pockets for 6 x 3 mm neodymium discs (glue in; mind polarity)
MAG_X        = 80.0      # magnet pair at ± this along the pivot axis
MAG_EL       = 13.0      # visor magnets at this angle about -Y (inside the top overlap band)
VISOR_RIM    = 8.0      # solid border around the mesh
MESH_HOLES   = False    # B-rep perforation (hours, 240 MB STEP). Leave False and run visor_perforate.py instead (10 s, mesh)
MESH_D       = 2.0      # hole diameter   (original panel, re-measured: 2.0)
MESH_PITCH   = 3.6      # hex pitch       (original panel, re-measured: 3.5–3.75, uniform across the whole panel)
PIN_D        = 12.0     # pivot pin on the shell (Ø12 so a 10-32 insert fits in its end)
COLLAR_D     = 20.0
PAD_D        = 40.0     # pivot bearing pad (was 26)
PAD_INNER_X  = 157.0    # pad inner face; the pad now runs 10.7 mm from the collar face inward (was 5.2)
RIM_W        = 6.0      # solid rims along the visor's top & bottom edges (constant width, run into the hubs)
THICK_T      = 4.0      # rims and pivot hubs are this thick (thickened inward); the perforated panel stays VISOR_T
HUB_ARC      = 28.0     # solid, thickened hub: everything within this arc distance (mm) of each pivot pole
CAP_D, CAP_BASE, CAP_FLOAT = 30.0, 3.0, 0.3   # pivot cap: Ø30 disc, 3 mm base, 0.3 mm axial float on the pad
INSERT_HOLE  = 6.4      # 10-32 heat-set pilot
SCREW_CLR    = 5.2      # 10-32 clearance

# ── ears ──
EAR_W, EAR_H = 340.0, 355.0        # outline (≈ original). Halves must fit a Prusa XL: 340 wide < 360
EAR_T, EAR_RIM_T = 60.0, 26.0      # chunky: 60 at the centre, 26 at the rim (room for the LED channel + fillets)
EAR_FILLET = 6.0                   # rounds the rim edges; rim flat left = 26 - 2*6 = 14 ≥ strip width
EAR_LED_W, EAR_LED_D = 10.6, 1.6   # rim LED channel: standard 10 mm strip, 1/16" deep
WIRE_D = 7.0                       # wire holes (fits a 3-wire lead + JST)
DOWEL_D    = 25.4              # 1" OD x 3/4" ID clear polycarbonate tube — neopixel "blade" inside; stiffness ≈ the 5/8" hardwood dowel it replaces
DOWEL_CLR  = 0.5               # bore = tube + clearance
DOWEL_X    = 95.0              # side tubes at ±this; centre tube at 0
DOWEL_END  = 22.0              # bores stop this far short of the rim so ≥2 mm of clear wall remains around the tube
TUBE_ID    = 19.05
BLADE_WIRE_D = 7.0             # wire channel from each side tube's foot to the tenon
EAR_AZ_BACK, EAR_EL = 26.0, 41.5      # socket position (measured).  ear axis = surface normal here, as in the original
# ── ear mount: FLUSH — disc sits on the sphere, tenon 45 mm into a mortise boss, 4 × 10-32 bolts from inside ──
TENON_W, TENON_T, TENON_D, TENON_CLR = 60.0, 34.0, 32.0, 0.25   # 34 thick so the 1" tube passes through it with 4 mm walls; 32 deep clears the hard hat
DISC_SINK   = 30.0             # how far the disc outline sinks into the sphere before scalloping (sets saddle width)
BOSS_WALL   = 6.0
BOLT_X      = 20.0             # bolts at ±this (w direction), mid-tenon depth, through front and back boss walls
DOWEL_SEAT  = 8.0
SEAT_THRU_D = 20.0             # through-hole under the centre tube seat: the blade's wires exit into the helmet

# ── shell split (left/right on the YZ plane) + seam joinery ──
SPLIT_LAT   = -5.0                          # horizontal split, between pixel rows -7.0° and -1.4°
SEAM_PADS   = [20.0, 45.0, 70.0, 110.0, 135.0, 160.0]   # back arc; each snaps to the nearest channel and the strip runs through a slot in it
PAD_LEN, PAD_ACROSS, PAD_T = 34.0, 24.0, 7.0
STUB_D, STUB_DEPTH = 2.0, 8.0               # 1.75 filament stubs align the halves
PLATE_T, PLATE_HOLE_SEP = 3.0, 12.0

# ── hard hat + electronics ──
HAT_L, HAT_W, HAT_DOME_H = 280.0, 220.0, 128.0   # Pyramex Ridgeline cap: 28 x 22 x 15.2 cm overall; dome ≈ 128 above the brim line
HAT_Z   = 124.0           # hat apex above the sphere centre. Clears the ear bosses at TENON_D 32; eyes land ~50 mm below centre, mid-mouth
HAT_Y   = 15.0            # hat centre sits this far behind the sphere centre
R_HAT   = 110.0           # crown curvature at the apex (measure yours; ±10 mm barely matters over a 60 mm bolt square)
CROWN_BOLT = 30.0         # crown bolts at (±30, ±30): a 60 mm square, inside the pixel-free cap (lat > 70°)
CROWN_PLATE = 90.0
STANDOFF_D  = 16.0
TRAY_AZ, TRAY_LAT, TRAY_W, TRAY_H = 90.0, -45.5, 80.0, 36.0   # electronics tray: back, pixel-free band, above the neck baffle
TRAY_BOLT_AZ = 16.0       # tray feet at az ± this
CONN_AZ, CONN_LAT, CONN_D = 68.0, -45.4, 16.0                  # GX16 panel jack: fits the 16.5 mm clear band between the groove ends and the baffle
# ── neck light baffle: 45° conical lip around the bottom opening (blocks glow in/out) ──
LIP_JUNC_Z  = -134.0        # where the baffle meets the inner wall (below the tray/connector band)
LIP_T2      = 2.5           # baffle wall thickness (≥ MIN_T)
NECK_HOLE_X, NECK_HOLE_Y = 165.0, 195.0   # elliptical head opening (side-to-side, front-to-back)

EYE_RECESS = False;  EYE_D, EYE_DEPTH, EYE_AZ, EYE_EL = 150.0, 6.0, 33.0, 37.0
OUT = "out/"
import sys
STAGE = sys.argv[1] if len(sys.argv) > 1 else "all"   # all | visor
# ─────────────────────────────────────────────────────────────────────────────

R_I = R_O - WALL
MIN_T = 2.0
assert WALL - GROOVE_D >= MIN_T and SKIN >= MIN_T and (WALL - GROOVE_D - SKIN) >= 1.8, 'wall / groove / skin do not satisfy the 2 mm minimum + 1.8 mm LED pocket'
assert WALL >= GROOVE_D + SKIN + 1.0
assert VISOR_R + 1.5 < R_I, "visor must clear the strips on the inner wall"
PITCH = 1000.0 / LEDS_PER_M
R_STRIP = R_I + GROOVE_D
DLAT = math.degrees(PITCH / R_STRIP)
N_CH = int(round(2*math.pi*R_O / PITCH / 4)) * 4
DAZ = 360.0 / N_CH
t0 = time.time()
def log(s): print(f"[{time.time()-t0:6.1f}s] {s}", flush=True)
def sph(r): return cq.Workplane("XY").sphere(r)
def dirv(az, el):
    a, e = math.radians(az), math.radians(el)
    return np.array([math.cos(e)*math.cos(a), math.cos(e)*math.sin(a), math.sin(e)])
def plane_at(p, normal, xdir): return cq.Plane(origin=tuple(p), xDir=tuple(xdir), normal=tuple(normal))
def wedge_prism(el_top, el_bot, half_x, L=600):
    pts = [(0, 0), (-L, L*math.tan(math.radians(el_top))), (-L, L*math.tan(math.radians(el_bot)))]
    return cq.Workplane("YZ").polyline(pts).close().extrude(half_x, both=True)

# ═════════════════════════════ SHELL ══════════════════════════════════════════
log("shell base")
shell = sph(R_O).cut(sph(R_I))
shell = shell.cut(cq.Workplane("XY").box(600, 600, 400).translate((0, 0, NECK_Z-200)))
# neck baffle: 45° cone from the inner wall down to the neck plane, elliptical head hole
_rw = math.sqrt(R_I**2 - LIP_JUNC_Z**2) + 1.2
_rn = _rw - (LIP_JUNC_Z - NECK_Z)
_t  = LIP_T2*1.415
_of = (cq.Workplane("XY").workplane(offset=LIP_JUNC_Z).circle(_rw).workplane(offset=NECK_Z-LIP_JUNC_Z).circle(_rn).loft())
_if = (cq.Workplane("XY").workplane(offset=LIP_JUNC_Z+3).circle(_rw-_t+3).workplane(offset=NECK_Z-LIP_JUNC_Z-4).circle(_rn-_t-1).loft())
baffle = (_of.cut(_if)
          .cut(cq.Workplane("XY").workplane(offset=NECK_Z-2).ellipse(NECK_HOLE_X/2, NECK_HOLE_Y/2).extrude(LIP_JUNC_Z-NECK_Z+6))
          .cut(cq.Workplane("XY").box(600,600,100).translate((0,0,NECK_Z-50))))
shell = shell.union(baffle)

shell = shell.cut(wedge_prism(MOUTH_EL_TOP, MOUTH_EL_BOT, MOUTH_HALF_X))

# internal visor pivots: collar + pin growing INWARD from the inner wall at the ±X poles
X_COLLAR_END = R_I - 4.5                 # visor pad bears on this face
X_PIN_END    = R_I - 18.0
for s in (1, -1):
    collar = cq.Workplane("YZ").workplane(offset=s*(R_O-1.5)).circle(COLLAR_D/2).extrude(-s*((R_O-1.5)-X_COLLAR_END))
    shell = shell.union(collar)
shell = shell.cut(wedge_prism(MOUTH_EL_TOP, MOUTH_EL_BOT, MOUTH_HALF_X))          # notch the collars so the grin tip stays a point
for s in (1, -1):
    pin    = cq.Workplane("YZ").workplane(offset=s*X_COLLAR_END).circle(PIN_D/2).extrude(-s*(X_COLLAR_END-X_PIN_END))
    shell = shell.union(pin)                                                       # pin stays full-round (bearing)
    shell = shell.cut(cq.Workplane("YZ").workplane(offset=s*(X_PIN_END-1)).circle(INSERT_HOLE/2).extrude(s*10))

# ear mortises — tenon axis u = surface normal at the socket (original ear angle)
ear_frames = []
for s_ in (1, -1):
    u = dirv(EAR_AZ_BACK if s_ > 0 else 180-EAR_AZ_BACK, EAR_EL)
    n = np.array([0, 1.0, 0]) - u*u[1]; n /= np.linalg.norm(n)
    w = np.cross(n, u)
    S = u*R_O
    ear_frames.append((S, u, n, w))
    boss = (cq.Workplane(plane_at(S, u, w)).rect(TENON_W+2*BOSS_WALL, TENON_T+2*BOSS_WALL).extrude(-(TENON_D+DOWEL_SEAT+3))
            .intersect(sph(R_O-1.0)))
    shell = shell.union(boss)
    shell = shell.cut(cq.Workplane(plane_at(S+15*u, u, w)).rect(TENON_W+TENON_CLR, TENON_T+TENON_CLR).extrude(-(TENON_D+15)))   # pocket
    floor = S - TENON_D*u
    shell = shell.cut(cq.Workplane(plane_at(floor+0.5*u, u, w)).circle((DOWEL_D+DOWEL_CLR)/2).extrude(-(DOWEL_SEAT+0.5)))     # tube seat
    shell = shell.cut(cq.Workplane(plane_at(floor+0.5*u, u, w)).circle(SEAT_THRU_D/2).extrude(-(DOWEL_SEAT+10)))              # blade wires out the bottom
    for sx in (1, -1):                                                                                                    # wire holes through the floor
        shell = shell.cut(cq.Workplane(plane_at(floor+0.5*u + w*sx*21.5, u, w)).circle(WIRE_D/2).extrude(-(DOWEL_SEAT+6)))
    for sx in (1, -1):                                                                                                    # bolt clearance through both boss walls
        c = S - (TENON_D/2)*u + w*sx*BOLT_X
        shell = shell.cut(cq.Workplane(plane_at(c + n*40, n, w)).circle(SCREW_CLR/2).extrude(-80))

# seam pads on the inner wall, straddling the horizontal split plane — each centred on a channel, strip runs through a slot
SPLIT_Z = R_O*math.sin(math.radians(SPLIT_LAT))
pad_centres = []; pad_channels = []
for az_req in SEAM_PADS:
    j = int(round(az_req/DAZ - 0.5)); az = (j+0.5)*DAZ; pad_channels.append(j)
    d = dirv(az, SPLIT_LAT); east = np.array([-math.sin(math.radians(az)), math.cos(math.radians(az)), 0.0])
    pad_centres.append(d*(R_I-PAD_T))
    pad = cq.Workplane(plane_at(d*(R_I+1.0), d, east)).rect(PAD_LEN, PAD_ACROSS).extrude(-(PAD_T+1.0))
    shell = shell.union(pad)
    shell = shell.cut(cq.Workplane(plane_at(d*(R_I-PAD_T-1), d, east)).rect(GROOVE_W+0.4, PAD_ACROSS+2).extrude(PAD_T+0.5))   # strip slot through the pad
    for (se, sz) in ((-1, 1), (1, -1)):                                                     # diagonal pilots, one per half
        c = d*(R_I-PAD_T-1) + east*se*12.5 + np.array([0, 0, sz*6.0])
        shell = shell.cut(cq.Workplane(plane_at(c, d, east)).circle(INSERT_HOLE/2).extrude(7.5+1))
    for se in (1, -1):                                                                       # filament-stub alignment holes across the seam
        c = d*(R_I-PAD_T/2) + east*se*7.5
        shell = shell.cut(cq.Workplane("XY").workplane(offset=SPLIT_Z-STUB_DEPTH).center(c[0], c[1]).circle(STUB_D/2).extrude(2*STUB_DEPTH))


# crown mount bosses (inserts) + electronics tray bosses + connector hole
crown_pts = [np.array([sx*CROWN_BOLT, sy*CROWN_BOLT, 0.0]) for sx in (1,-1) for sy in (1,-1)]
for q in crown_pts:
    q[2] = math.sqrt(R_I**2 - q[0]**2 - q[1]**2); d = q/np.linalg.norm(q)
    boss = cq.Workplane(plane_at(d*(R_I+1.5), d, np.cross([0,0,1], d))).circle(STANDOFF_D/2).extrude(-(1.5+6.0)).intersect(sph(R_O-1.5))
    skirt = (cq.Workplane(plane_at(d*(R_I-6.0), d, np.cross([0,0,1], d))).circle(STANDOFF_D/2)
             .workplane(offset=6.0+1.5).circle(STANDOFF_D/2+7.5).loft()).intersect(sph(R_O-1.5))          # 45° cone: prints in any orientation
    shell = shell.union(boss).union(skirt)
    shell = shell.cut(cq.Workplane(plane_at(d*(R_I-6.0-0.5), d, np.cross([0,0,1], d))).circle(INSERT_HOLE/2).extrude(7.5+0.5))
tray_pts = []
for daz in (TRAY_BOLT_AZ, -TRAY_BOLT_AZ):
    d = dirv(TRAY_AZ+daz, TRAY_LAT); tray_pts.append(d)
    boss = cq.Workplane(plane_at(d*(R_I+1.5), d, np.cross([0,0,1], d))).circle(STANDOFF_D/2).extrude(-(1.5+6.0)).intersect(sph(R_O-1.5))
    skirt = (cq.Workplane(plane_at(d*(R_I-6.0), d, np.cross([0,0,1], d))).circle(STANDOFF_D/2)
             .workplane(offset=6.0+1.5).circle(STANDOFF_D/2+7.5).loft()).intersect(sph(R_O-1.5))
    shell = shell.union(boss).union(skirt)
    shell = shell.cut(cq.Workplane(plane_at(d*(R_I-6.0-0.5), d, np.cross([0,0,1], d))).circle(INSERT_HOLE/2).extrude(7.5+0.5))
d = dirv(CONN_AZ, CONN_LAT)
shell = shell.cut(cq.Workplane(plane_at(d*(R_O+2), d, np.cross([0,0,1], d))).circle(CONN_D/2).extrude(-(WALL+4)))

def mouth_pt(el_m, x_, r=None):
    """point at cylindrical angle el_m about the X axis (measured from -Y), axial position x_"""
    r = R_O if r is None else r
    rho = math.sqrt(max(r*r - x_*x_, 1.0))
    return np.array([x_, -rho*math.cos(math.radians(el_m)), rho*math.sin(math.radians(el_m))])

mag_shell = []
for el_m in (MAG_EL, MAG_EL + OPEN_ANGLE):          # hold-closed pair and hold-open pair
    for sx in (1, -1):
        p = mouth_pt(el_m, sx*MAG_X, R_I); d = p/np.linalg.norm(p)
        mag_shell.append(p)
        boss = (cq.Workplane(plane_at(d*(R_I-3.2), d, np.cross([0,0,1], d))).circle(7.0)
                .workplane(offset=3.2+1.5).circle(7.0+4.7).loft()).intersect(sph(R_O-1.5))
        shell = shell.union(boss)
        shell = shell.cut(cq.Workplane(plane_at(d*(R_I-3.2-0.1), d, np.cross([0,0,1], d))).circle(MAG_D/2).extrude(MAG_T+0.1))



# ear rim-strip wire holes: where the rim channel meets the saddle, hidden under the disc edge
ear_wire_pts = []
_zb = TENON_D - DISC_SINK; _zc = _zb + EAR_H/2; _a = EAR_W/2 - EAR_LED_D/2 - 0.8; _b = EAR_H/2 - EAR_LED_D/2 - 0.8
for (S, u, n, w) in ear_frames:
    for sx in (1, -1):
        lo, hi = 0.02, math.pi/2
        for _ in range(48):                                      # bisect: rim point on the head sphere
            mid = 0.5*(lo+hi)
            P = (S - TENON_D*u) + w*(sx*_a*math.sin(mid)) + u*(_zc - _b*math.cos(mid))
            if np.linalg.norm(P) < R_O + 0.5: lo = mid
            else: hi = mid
        P = (S - TENON_D*u) + w*(sx*_a*math.sin(lo)) + u*(_zc - _b*math.cos(lo))
        hp = P - 6.0*( (P/np.linalg.norm(P) - u*((P/np.linalg.norm(P))@u)) / max(np.linalg.norm(P/np.linalg.norm(P) - u*((P/np.linalg.norm(P))@u)), 1e-6) )*0  # keep at the rim end
        d_ = P/np.linalg.norm(P)
        ear_wire_pts.append(P)
        shell = shell.cut(cq.Workplane(plane_at(d_*(R_O+2), d_, np.cross([0,0,1], d_))).circle(EAR_WIRE_D/2).extrude(-(WALL+6)))
# shell-side visor wire holes (only when the visor carries LEDs)
for sx in ((1, -1) if VISOR_LEDS else ()):
    p = mouth_pt(SWIRE_EL, sx*VWIRE_X); d_ = p/np.linalg.norm(p)
    shell = shell.cut(cq.Workplane(plane_at(d_*(R_O+2), d_, np.cross([0,0,1], d_))).circle(4.0).extrude(-(WALL+6)))


if EYE_RECESS:
    for s in (1, -1):
        d = dirv(-90+s*EYE_AZ, EYE_EL)
        shell = shell.cut(cq.Workplane(plane_at(d*(R_O-EYE_DEPTH), d, np.cross([0,0,1], d))).circle(EYE_D/2).extrude(30))
log(f"shell base done, valid={shell.val().isValid()}")

# ═════════════════════════ PIXEL GRID ════════════════════════════════════════
def excluded(az, lat):
    d = dirv(az, lat); p = d*R_O
    if p[1] < 0 and abs(p[0]) < MOUTH_HALF_X+10:
        e = math.degrees(math.atan2(p[2], -p[1]))
        if MOUTH_EL_BOT-VISOR_MARGIN-2 < e < MOUTH_EL_TOP+VISOR_MARGIN_TOP+2: return True
    for s in (1, -1):
        if math.degrees(math.acos(np.clip(d @ [s,0,0], -1, 1))) < 8.5: return True
    for (S, u, n, w) in ear_frames:
        if np.linalg.norm(p-S) < 55.0: return True
    for pw in ear_wire_pts:
        if np.linalg.norm(p - pw) < EAR_WIRE_D/2 + PIX: return True
    for p_m in mag_shell:
        if np.linalg.norm(p - p_m) < 7.0 + PIX: return True

    for q in crown_pts:
        if math.degrees(math.acos(np.clip(d @ (q/np.linalg.norm(q)), -1, 1))) < math.degrees((STANDOFF_D/2 + 7.5 + PIX)/R_O): return True
    if EYE_RECESS:
        for s in (1, -1):
            if math.degrees(math.acos(np.clip(d @ dirv(-90+s*EYE_AZ, EYE_EL), -1, 1))) < math.degrees((EYE_D/2+PIX)/R_O): return True
    return False

def tier_ok(j, lat):
    if lat <= LAT_MAX_ALL2: return True
    if j % 2 == 0 and lat <= LAT_MAX_EVEN: return True
    if j % 4 == 0 and lat <= LAT_MAX_QUARTER: return True
    return False
pixels = []
for j in range(N_CH):
    az = (j+0.5)*DAZ; k = 0
    while LAT_MIN + k*DLAT <= LAT_MAX_QUARTER:
        lat = LAT_MIN + k*DLAT
        if tier_ok(j, lat) and not excluded(az, lat): pixels.append((j, k, az, lat))
        k += 1

runs = {}
for j, k, az, lat in pixels: runs.setdefault(j, []).append(k)
groove_runs = []
for j, ks in runs.items():
    ks = sorted(ks); start = prev = ks[0]
    for k in ks[1:] + [None]:
        if k is None or k != prev+1:
            groove_runs.append((j, start, prev))
            if k is not None: start = k
        if k is not None: prev = k
log(f"channels={N_CH}  az pitch={2*math.pi*R_O/N_CH:.2f}  row pitch={PITCH:.2f} ({DLAT:.2f}°)  pixels={len(pixels)}  runs={len(groove_runs)}")

def groove_tool(j, k0, k1):
    az = (j+0.5)*DAZ
    a0 = math.radians(LAT_MIN+k0*DLAT-0.5*DLAT); a1 = math.radians(LAT_MIN+k1*DLAT+0.5*DLAT); am = 0.5*(a0+a1)
    ri, ro = R_I-0.6, R_I+GROOVE_D
    P = lambda r, a: (r*math.cos(a), r*math.sin(a))
    w = (cq.Workplane("XZ").moveTo(*P(ri, a0)).threePointArc(P(ri, am), P(ri, a1))
         .lineTo(*P(ro, a1)).threePointArc(P(ro, am), P(ro, a0)).close().extrude(GROOVE_W/2, both=True))
    return w.rotate((0,0,0), (0,0,1), az).val()
def pixel_tool(az, lat):
    d = dirv(az, lat); east = np.array([-math.sin(math.radians(az)), math.cos(math.radians(az)), 0])
    depth = (R_O-SKIN) - (R_I+GROOVE_D) + 0.4
    px = PIX if lat <= LAT_MAX_ALL else PIX_HI
    return cq.Workplane(plane_at(d*(R_O-SKIN), d, east)).rect(px, px).extrude(-depth).val()

body = shell.val()
if STAGE == "all":
    tools = [groove_tool(*g) for g in groove_runs] + [pixel_tool(az, lat) for (_, _, az, lat) in pixels]
    B = 150
    for i in range(0, len(tools), B):
        body = body.cut(*tools[i:i+B])
    del tools
else:
    body = None
if body is not None: log(f"shell with LEDs: valid={body.isValid()} faces={len(body.Faces())}")
shell = cq.Workplane("XY").newObject([body]) if body is not None else None
shell_halves = None
if body is not None:
    big = 1000
    hT = body.intersect(cq.Workplane("XY").box(big, big, big).translate((0, 0, SPLIT_Z + big/2)).val())   # top: crown up
    hB = body.intersect(cq.Workplane("XY").box(big, big, big).translate((0, 0, SPLIT_Z - big/2)).val())   # bottom: neck ring down
    shell_halves = (hB, hT)
    # designed breakaway supports for the TOP half (printed on its cut face, crown up)
    GAP, TW = 0.25, 0.9
    parts = []
    for q in crown_pts:                                    # crown-boss tubes: top follows the boss face sphere, 0.25 gap
        d = q/np.linalg.norm(q); c = d*(R_I-6.0)
        t = cq.Workplane("XY").workplane(offset=SPLIT_Z).center(c[0], c[1]).circle(STANDOFF_D/2).circle(STANDOFF_D/2-TW).extrude(300).val()
        parts.append(t.intersect(sph(R_I-6.0-GAP).val()))
    for (S, u, n, w) in ear_frames:                        # ear-boss columns: thin-wall prism, top cut by the boss end plane
        E = S - (TENON_D+DOWEL_SEAT+3)*u
        wf = np.array([w[0], w[1], 0.0]); wf /= np.linalg.norm(wf)
        base = cq.Plane(origin=(E[0], E[1], SPLIT_Z), xDir=tuple(wf), normal=(0,0,1))
        outer = cq.Workplane(base).rect(TENON_W+2*BOSS_WALL+2, TENON_T+2*BOSS_WALL+2).extrude(300)
        inner = cq.Workplane(base).rect(TENON_W+2*BOSS_WALL+2-2*TW, TENON_T+2*BOSS_WALL+2-2*TW).extrude(300)
        col = outer.cut(inner).val()
        below = cq.Workplane(plane_at(E - GAP*u, u, w)).rect(400, 400).extrude(-400).val()
        parts.append(col.intersect(below))
    for s_ in (1, -1):                                     # pivot stubs under the collar and the pin
        parts.append(cq.Workplane("XY").box((R_I-2.0)-X_COLLAR_END, 8.0, (-COLLAR_D/2-GAP)-SPLIT_Z).translate((s_*((R_I-2.0)+X_COLLAR_END)/2, 0, (SPLIT_Z + (-COLLAR_D/2-GAP))/2)).val())   # stops short of the wall
        parts.append(cq.Workplane("XY").box(X_COLLAR_END-X_PIN_END, 8.0, (-PIN_D/2-GAP)-SPLIT_Z).translate((s_*(X_COLLAR_END+X_PIN_END)/2, 0, (SPLIT_Z + (-PIN_D/2-GAP))/2)).val())
    sup = parts[0]
    for p_ in parts[1:]: sup = sup.fuse(p_)
    shell_supports = (None, sup)
    log(f"shell halves valid={[h.isValid() for h in shell_halves]} solids={[len(h.Solids()) for h in shell_halves]}")
if STAGE == "all": os.makedirs(OUT, exist_ok=True); body.exportBrep(OUT+"shell.brep")

# ═════════════════════════════ VISOR (internal) ══════════════════════════════
log("visor")
RV_O, RV_I = VISOR_R, VISOR_R - VISOR_T
annulus = sph(RV_O).cut(sph(RV_I))
cap  = annulus.intersect(wedge_prism(MOUTH_EL_TOP+VISOR_MARGIN_TOP, MOUTH_EL_BOT-VISOR_MARGIN, MOUTH_HALF_X+8))
visor = cap                      # the cap itself now reaches the poles (the grin does too); the pads join it there
lip = (sph(R_O + LIP_PROUD).cut(sph(RV_I))
       .intersect(wedge_prism(-31.5, -34.7, LIP_HALF_X)))
visor = visor.union(lip)
mag_visor = []
for sx in (1, -1):                                     # magnet pads on the visor's outer face
    p = mouth_pt(MAG_EL, sx*MAG_X, RV_O); d = p/np.linalg.norm(p)
    mag_visor.append(p)
    pad_m = cq.Workplane(plane_at(d*(RV_O+3.4), d, np.cross([0,0,1], d))).circle(6.0).extrude(-(3.4+VISOR_T))
    visor = visor.union(pad_m)
    visor = visor.cut(cq.Workplane(plane_at(d*(RV_O+3.4+0.1), d, np.cross([0,0,1], d))).circle(MAG_D/2).extrude(-(MAG_T+0.1)))

def _edge_slab(E, sgn, d0, d1):
    """constant-width band d0..d1 mm inside the visor edge at angle E (planes PARALLEL to the edge plane), front half only"""
    nE = sgn*np.array([0.0, math.sin(math.radians(E)), math.cos(math.radians(E))])
    v0, v1 = RV_O*math.sin(d0/RV_O), RV_O*math.sin(d1/RV_O); lo, hi = min(v0, v1), max(v0, v1)
    pl = cq.Plane(origin=tuple(nE*((lo+hi)/2)), xDir=(1,0,0), normal=tuple(nE))
    return (cq.Workplane(pl).rect(900, 900).extrude((hi-lo)/2, both=True)
            .intersect(cq.Workplane("XY").box(900, 900, 900).translate((0, -450, 0))))
E_TOP, E_BOT = MOUTH_EL_TOP + VISOR_MARGIN_TOP, MOUTH_EL_BOT - VISOR_MARGIN
panel_wedge = wedge_prism(E_TOP, E_BOT, MOUTH_HALF_X+8)
thick_shell = sph(RV_O).cut(sph(RV_O - THICK_T))
for E, sgn in ((E_TOP, +1), (E_BOT, -1)):        # rims: beams along both long edges, carry the load out to the pivots
    rim = thick_shell.intersect(_edge_slab(E, sgn, -RIM_W, 0.0)).intersect(panel_wedge)
    visor = cq.Workplane("XY").newObject([visor.val().fuse(rim.val()).clean()])
for s in (1, -1):                                # hubs: Ø56 x 4 mm thickened disc round each pivot — FULL disc (not just the panel's pointed tip);
    th = HUB_ARC / RV_O                          # it is symmetric about the pivot axis, so it never sweeps into anything when the visor swings
    ro, ri = RV_O, RV_O - THICK_T
    prof = (cq.Workplane("XY").moveTo(s*ro, 0)
            .threePointArc((s*ro*math.cos(th/2), ro*math.sin(th/2)), (s*ro*math.cos(th), ro*math.sin(th)))
            .lineTo(s*ri*math.cos(th), ri*math.sin(th))
            .threePointArc((s*ri*math.cos(th/2), ri*math.sin(th/2)), (s*ri, 0)).close())
    hub = prof.revolve(360, (0, 0, 0), (1, 0, 0))
    visor = cq.Workplane("XY").newObject([visor.val().fuse(hub.val()).clean()])
for s in (1, -1):                                # bearing pad: Ø40 x 10.7 mm, collar face inward
    pad = cq.Workplane("YZ").workplane(offset=s*X_COLLAR_END).circle(PAD_D/2).extrude(-s*(X_COLLAR_END-PAD_INNER_X))
    visor = cq.Workplane("XY").newObject([visor.val().fuse(pad.val()).clean()])
    visor = visor.cut(cq.Workplane("YZ").workplane(offset=s*(X_COLLAR_END+2)).circle(PIN_D/2+0.2).extrude(-s*(X_COLLAR_END+2-PAD_INNER_X+3)))
log(f"visor frame valid={visor.val().isValid()}")

if VISOR_LEDS:
    # light-pipe troughs along the visor's top and bottom edges — hooded; strip fires OUTWARD into a clear tube that sits on the panel edge.
    # Bounded by planes PARALLEL to the edge plane, so every band has constant width along its whole length (a real 10 mm strip fits end to end).
    # cross-section, mm from the panel edge (+ = away from the panel):  front wall -2.2..-0.2 | tube 0.2..6.2 | strip 0.1..10.7 | back wall 10.9..12.9
    R_TUBE_C  = RV_O - 1.0                                     # tube centre radius: straddles the panel (163..165)
    R_FLOOR   = R_TUBE_C - TUBE_D/2 - TUBE_CLR - 2.6           # strip PCB sits here; LED tips end 0.4 under the tube
    STRIP_C   = 0.1 + 5.3                                      # strip centre line from the edge (mm)
    TROUGH_OUT = 12.9
    def edge_normal(E, sgn):                                   # unit normal of the edge plane, pointing away from the panel
        return sgn*np.array([0.0, math.sin(math.radians(E)), math.cos(math.radians(E))])
    def edge_slab(nE, d0, d1, half_x=None):                    # region between the offset curves d0..d1 (mm from the edge), |x| ≤ half_x
        half_x = LG_HALF_X if half_x is None else half_x
        v0, v1 = RV_O*math.sin(d0/RV_O), RV_O*math.sin(d1/RV_O); lo, hi = min(v0, v1), max(v0, v1)
        pl = cq.Plane(origin=tuple(nE*((lo+hi)/2)), xDir=(1,0,0), normal=tuple(nE))
        return (cq.Workplane(pl).rect(2*half_x, 900).extrude((hi-lo)/2, both=True)
                .intersect(cq.Workplane("XY").box(900, 900, 900).translate((0, -450, 0))))   # front half only (the parallel plane also cuts the back of the sphere)
    def edge_band(nE, r_lo, r_hi, d0, d1, half_x=None):
        return sph(r_hi).cut(sph(r_lo)).intersect(edge_slab(nE, d0, d1, half_x))
    for E, sgn in ((MOUTH_EL_TOP + VISOR_MARGIN_TOP, +1), (MOUTH_EL_BOT - VISOR_MARGIN, -1)):
        nE = edge_normal(E, sgn)
        floor = edge_band(nE, R_FLOOR-3.0, R_FLOOR,                     -2.2, TROUGH_OUT)
        front = edge_band(nE, R_FLOOR-3.0, RV_I+1.0,                    -2.2, -0.2)          # 2 mm; fused into the panel; light dam toward the face
        back  = edge_band(nE, R_FLOOR-3.0, R_TUBE_C+TUBE_D/2+2.2,       10.9, TROUGH_OUT)    # 2 mm
        tlip  = edge_band(nE, R_TUBE_C+TUBE_D/2+0.2, R_TUBE_C+TUBE_D/2+2.2, 4.0, TROUGH_OUT) # 2 mm shelf over the tube: keeps it in
        trough = floor.union(front).union(back).union(tlip)
        trough = trough.cut(edge_band(nE, R_FLOOR-0.8, R_FLOOR+0.5, STRIP_C-5.3, STRIP_C+5.3, LG_HALF_X+2))   # 10.6 x 0.8 strip locating channel
        _base = visor.val(); _base = _base.Solids()[0] if len(_base.Solids()) == 1 else _base
        visor = cq.Workplane("XY").newObject([_base.fuse(trough.val()).clean()])
    p = mouth_pt(VWIRE_EL, VWIRE_X, RV_O); d_ = p/np.linalg.norm(p)
    visor = visor.cut(cq.Workplane(plane_at(d_*(RV_O+2), d_, np.cross([0,0,1], d_))).circle(3.5).extrude(-(VISOR_T+14)))

if MESH_HOLES:
    # hex grid in (θ about the X axis, ψ along the great circle) — the panel is a rectangle in these coords
    rim_deg = math.degrees(VISOR_RIM / RV_O)
    th_lo = MOUTH_EL_BOT - VISOR_MARGIN + rim_deg; th_hi = MOUTH_EL_TOP + VISOR_MARGIN_TOP - rim_deg
    row_dth = math.degrees(MESH_PITCH*0.8660 / RV_O); col_dps = MESH_PITCH / RV_O
    x_max = min(MOUTH_HALF_X + 8 - VISOR_RIM, 140.0)     # keep the last 25 mm before the pads solid (hinge strength)
    centres = []; row = 0; th = th_lo
    while th <= th_hi:
        k = 0
        while True:
            p_ = (k + (0.5 if row % 2 else 0.0)) * col_dps
            if p_ >= math.pi/2 or RV_O*math.sin(p_) > x_max: break
            for q in ([p_] if (k == 0 and row % 2 == 0) else [p_, -p_]):
                r_ = RV_O*math.cos(q)
                pt_h = np.array([RV_O*math.sin(q), -r_*math.cos(math.radians(th)), r_*math.sin(math.radians(th))])
                if min(np.linalg.norm(pt_h - m) for m in mag_visor) > 10.0:
                    centres.append(tuple(pt_h))
            k += 1
        th += row_dth; row += 1
    log(f"mesh holes: {len(centres)}")
    # memory-lean, resumable: cut in small batches, checkpoint to BREP
    os.makedirs(OUT, exist_ok=True); ck = OUT+"visor_holes.brep"; prog = OUT+"visor_holes.progress"
    vb = visor.val(); start = 0
    if os.path.exists(ck) and os.path.exists(prog):
        vb = cq.Shape.importBrep(ck); start = int(open(prog).read()); log(f"  resuming at hole {start}")
    B = 120
    for i in range(start, len(centres), B):
        tools = []
        for (x_, y_, z_) in centres[i:i+B]:
            d = np.array([x_, y_, z_]); d /= np.linalg.norm(d)
            tools.append(cq.Workplane(plane_at(d*(RV_O+1), d, np.cross([0,0,1], d))).circle(MESH_D/2).extrude(-(VISOR_T+2)).val())
        vb = vb.cut(*tools); del tools
        vb.exportBrep(ck); open(prog, "w").write(str(min(i+B, len(centres))))
        if (i//B) % 5 == 0: log(f"  holes {min(i+B,len(centres))}/{len(centres)}  faces={len(vb.Faces())}")
    visor = cq.Workplane("XY").newObject([vb])
    log(f"visor mesh done valid={vb.isValid()} faces={len(vb.Faces())}")

# ═════════════════════════════ EARS ═══════════════════════════════════════════
log("ears")
WIRE_SLOT_W  = 15.0     # width of the whole wire path through the ear's thickness (fits a JST-SM 3-pin on edge, 12 x 8)
PEG_GROOVE_D = 10.0     # groove depth into the peg's outer side face (JST lies flat in it); peg keeps 7 mm solid beside the centre bore
WIRE_FILLET  = 3.0      # rounds every inside corner of the wire path
BRIDGE_T     = 6.6      # material kept over the visible rim (incl. its 1.6 mm LED channel) where the window passes above it
def _head_z(x):         # ear underside where it sits on the head (hidden), ear frame
    return TENON_D - R_O + math.sqrt((R_O + 0.5)**2 - x*x)
def _rim_z(x):          # visible bottom rim of the ear (outline ellipse), ear frame
    zb = TENON_D - DISC_SINK; zc = zb + EAR_H/2
    return zc - (EAR_H/2)*math.sqrt(max(0.0, 1 - (x/(EAR_W/2))**2))
def jst_channel(s, z_foot):
    """One open wire path per side: a tall window from under the side tube down through the hidden underside of the ear,
    an open groove along that underside, and an open groove down the peg's outer face to its tip (over the socket floor
    hole).  Only a 6.6 mm bridge over the visible rim stays closed.  Built for +x and mirrored."""
    xg = TENON_W/2 - PEG_GROOVE_D                 # 20: groove floor in the peg
    xb = DOWEL_X - (DOWEL_D + DOWEL_CLR)/2        # inner edge of the side-tube bore
    xr = DOWEL_X + 2.0                            # opening reaches just past the tube centre
    bridge = [(x, _rim_z(x) + BRIDGE_T) for x in (xr, 92.0, 86.0, 80.0, 74.0, 69.0)]
    w = (cq.Workplane("XZ").moveTo(xg, -4.0)
         .lineTo(xg, 33.0)
         .threePointArc((xg + 8 - 8*math.cos(math.radians(45)), 33.0 + 8*math.sin(math.radians(45))), (xg + 8, 41.0))
         .spline([(45.0, 42.5), (65.0, 48.5), (xb, z_foot)], tangents=[(1, 0), (1, 0.42)], includeCurrent=True)
         .lineTo(xb + 2.0, z_foot + 3.0).lineTo(xr, z_foot + 3.0)
         .lineTo(*bridge[0])
         .spline(bridge[1:] + [(66.0, 20.5), (63.0, 13.0)], includeCurrent=True)
         .lineTo(60.0, 0.0).lineTo(36.0, -4.0).close())
    tool = w.extrude(WIRE_SLOT_W/2, both=True)
    try:
        tool = tool.faces("<Y or >Y").edges().fillet(WIRE_FILLET)
    except Exception as e:
        log(f"  wire-path fillet skipped ({e})")
    t = tool.val()
    return t if s > 0 else t.mirror("YZ")

def make_disc():
    """ear in its frame: X=width, Y=thickness, Z=up; tenon tip at z=0, sphere surface at z=TENON_D. Returns (whole, top, bottom)"""
    z_bottom = TENON_D - DISC_SINK
    zc = z_bottom + EAR_H/2
    outline = cq.Workplane("XZ").ellipse(EAR_W/2, EAR_H/2).extrude(EAR_T/2, both=True).translate((0, 0, zc))
    Rd = (EAR_H/2)**2 / (EAR_T-EAR_RIM_T)
    disc = (outline.intersect(cq.Workplane("XY").sphere(Rd).translate((0, -(Rd-EAR_T/2), zc)))
                   .intersect(cq.Workplane("XY").sphere(Rd).translate((0,  (Rd-EAR_T/2), zc))))
    if EAR_FILLET > 0:
        try: disc = disc.edges().fillet(EAR_FILLET)
        except Exception as e: log(f"  rim fillet failed ({e}); continuing without it")
    ring = (cq.Workplane("XZ").ellipse(EAR_W/2 + 1, EAR_H/2 + 1).ellipse(EAR_W/2 - EAR_LED_D, EAR_H/2 - EAR_LED_D)
            .extrude(EAR_LED_W/2, both=True).translate((0, 0, zc)))
    disc = disc.cut(ring)
    disc = disc.cut(cq.Workplane("XY").sphere(R_O + 0.5).translate((0, 0, TENON_D - R_O)))     # scallop to the head
    tenon = cq.Workplane("XY").box(TENON_W, TENON_T, TENON_D + 45).translate((0, 0, (TENON_D+45)/2))
    whole = disc.union(tenon)
    for sx in (1, -1):
        for sy in (1, -1):
            whole = whole.cut(cq.Workplane("XZ").workplane(offset=-sy*(TENON_T/2 + 1)).center(sx*BOLT_X, TENON_D/2).circle(INSERT_HOLE/2).extrude(sy*(7.5 + 1)))
    bore = DOWEL_D + DOWEL_CLR
    z_top_c = z_bottom + EAR_H - DOWEL_END
    hz = (EAR_H/2)*math.sqrt(max(0.0, 1-(DOWEL_X/(EAR_W/2))**2))
    z_side_lo, z_side_hi = zc - hz + DOWEL_END, zc + hz - DOWEL_END
    whole = whole.cut(cq.Workplane("XY").workplane(offset=-5).circle(bore/2).extrude(z_top_c+5))
    for sx in (DOWEL_X, -DOWEL_X):
        whole = whole.cut(cq.Workplane("XY").workplane(offset=z_side_lo).center(sx, 0).circle(bore/2).extrude(z_side_hi-z_side_lo))
        whole = whole.cut(cq.Workplane("XY").newObject([jst_channel(math.copysign(1.0, sx), z_side_lo)]))
    global DOWEL_CUTS
    DOWEL_CUTS = {"centre": z_top_c + DOWEL_SEAT, "side": z_side_hi - z_side_lo}; global TUBE_Z; TUBE_Z = (z_side_lo, z_side_hi, z_top_c)
    big = 1000
    top = whole.intersect(cq.Workplane("XY").box(big, big, big).translate((0, 0, zc + big/2)))
    bot = whole.intersect(cq.Workplane("XY").box(big, big, big).translate((0, 0, zc - big/2)))
    return whole.val(), top.val(), bot.val()

disc_p, ear_top_p, ear_bot_p = make_disc()
PIN_PROTRUDE = PAD_INNER_X - X_PIN_END            # pin stands this far proud of the pad's inner face
cap_pocket = PIN_PROTRUDE - CAP_FLOAT
pivot_cap_p = (cq.Workplane("XY").circle(CAP_D/2).extrude(CAP_BASE + cap_pocket)
               .cut(cq.Workplane("XY").workplane(offset=CAP_BASE).circle(PIN_D/2+0.2).extrude(cap_pocket+1))
               .cut(cq.Workplane("XY").workplane(offset=-1).circle(SCREW_CLR/2).extrude(CAP_BASE+2))).val()
# cap: pocket bottoms on the pin end and a 10-32 x 3/8" clamps it to the pin-end insert; the rim then sits 0.3 mm off the pad,
# so the pad is captured between the shell collar and the cap (old cap could not slip over the pin and captured nothing)

plate_p = (cq.Workplane("XY").rect(PAD_LEN-2, PAD_ACROSS-2).extrude(PLATE_T)
           .faces(">Z").workplane().pushPoints([(-12.5, 6.0), (12.5, -6.0)]).hole(SCREW_CLR)).val()   # bridges over the strip slot; diagonal 10-32s
ears = []
for (S, u, n, w) in ear_frames:
    ears.append(disc_p.moved(cq.Location(cq.Plane(origin=tuple(S - TENON_D*u), xDir=tuple(w), normal=tuple(u)))))
log(f"ears valid={[e.isValid() for e in ears]}")

# ═════════════════════════ HARD HAT MOUNT PARTS ═════════════════════════════
log("hat mount")
hat_c = np.array([0.0, HAT_Y, HAT_Z - HAT_DOME_H])                 # dome base centre
hat_env = (cq.Workplane("XY").sphere(1.0).val()
           .transformGeometry(cq.Matrix([[HAT_L/2,0,0,hat_c[0]],[0,HAT_W/2,0,hat_c[1]],[0,0,HAT_DOME_H,hat_c[2]],[0,0,0,1]])))
hat_env = hat_env.intersect(cq.Workplane("XY").box(600,600,600).translate((0,0,hat_c[2]+300)).val())   # upper half-ellipsoid = hat dome envelope
crown_sph_c = np.array([0.0, HAT_Y, HAT_Z - R_HAT])                # sphere approximating the crown near the apex

# ── crown FRAME (v18, for the 3M SecureFit H-700 that rides higher): bolts to the same 4 shell bosses; the hat hangs from 4
#    separate pads via stackable spacers, so the hat height is set at assembly — nothing to measure up front.
FRAME_T      = 5.0                      # curved frame thickness (R_I-6 .. R_I-11)
FRAME_X, FRAME_Y0, FRAME_Y1 = 58.0, -42.0, 72.0     # frame outline (helmet frame; centred on the hat, which sits HAT_Y behind)
FRAME_HOLE_D = 44.0                     # open centre: the hat crown can rise into it
HAT_PTS      = [(45.0, HAT_Y), (-45.0, HAT_Y), (0.0, HAT_Y + 45.0), (0.0, HAT_Y - 45.0)]   # diamond round the hat crown, 45 mm out
PAD_D2, PAD_DROP = 20.0, 6.0            # hat pads: Ø20, 6 mm below the frame; insert pilot 9 mm deep
SPACER_D, SPACER_HS = 20.0, (2.0, 4.0, 8.0, 16.0)
r_out, r_in = R_I - 6.0, R_I - 6.0 - FRAME_T
outline = (cq.Workplane("XY").center(0, (FRAME_Y0+FRAME_Y1)/2).rect(2*FRAME_X, FRAME_Y1-FRAME_Y0).extrude(400)
           .edges("|Z").fillet(18.0))
frame = sph(r_out).cut(sph(r_in)).intersect(outline)
frame = frame.cut(cq.Workplane("XY").center(0, HAT_Y).circle(FRAME_HOLE_D/2).extrude(400))
for (px, py) in HAT_PTS:                              # hat pads: vertical, flat bottoms, insert from below
    top = math.sqrt(r_out**2 - px*px - py*py)
    bot_z = math.sqrt(r_in**2 - px*px - py*py) - PAD_DROP
    pad = (cq.Workplane("XY").workplane(offset=bot_z).center(px, py).circle(PAD_D2/2).extrude(top - bot_z - 0.5)
           .intersect(sph(r_out)))
    cone = (cq.Workplane("XY").workplane(offset=bot_z + 2.0).center(px, py).circle(PAD_D2/2)
            .workplane(offset=5.0).circle(PAD_D2/2 + 5.0).loft().intersect(sph(r_out)))       # 45° fillet-cone into the frame
    frame = frame.union(pad).union(cone)
    frame = frame.cut(cq.Workplane("XY").workplane(offset=bot_z - 1).center(px, py).circle(INSERT_HOLE/2).extrude(1 + 9.0))
for q in crown_pts:                                   # shell-boss bolts: 10-32 from underneath, head recess in the frame
    d = q/np.linalg.norm(q)
    frame = frame.cut(cq.Workplane(plane_at(d*(r_out+2), d, np.cross([0,0,1], d))).circle(SCREW_CLR/2).extrude(-(FRAME_T+4)))
    frame = frame.cut(cq.Workplane(plane_at(d*(r_in+2.0), d, np.cross([0,0,1], d))).circle(5.6).extrude(-6))      # 3 mm thread-side web stays
crown_plate = frame.val()
hat_pad_z = {p: round(math.sqrt(r_in**2 - p[0]**2 - p[1]**2) - PAD_DROP, 1) for p in HAT_PTS}
standoff_h = [None]

# spacers: 4 each of 2/4/8/16 mm, Ø20 with a 10-32 clearance hole — stack them under each pad to suit the hat height
sp = None
for k, h in enumerate(SPACER_HS):
    for n in range(4):
        piece = cq.Workplane("XY").center(n*26.0, k*26.0).circle(SPACER_D/2).circle(SCREW_CLR/2 + 0.1).extrude(h)
        sp = piece if sp is None else sp.union(piece)
hat_spacers = sp.val()

# drill template: flat, flexes onto the hat. Centre hole on the hat's top centre, arrow to the FRONT; 4 Ø3 pilot marks.
tmpl = cq.Workplane("XY").rect(108, 16).extrude(1.2).union(cq.Workplane("XY").rect(16, 108).extrude(1.2))
tmpl = tmpl.union(cq.Workplane("XY").polyline([(-8, -54), (8, -54), (0, -66)]).close().extrude(1.2))   # arrow: front of the hat
for (px, py) in HAT_PTS:
    tmpl = tmpl.cut(cq.Workplane("XY").center(px, py - HAT_Y).circle(1.6).extrude(5))
tmpl = tmpl.cut(cq.Workplane("XY").circle(3.0).extrude(5))
drill_template = tmpl.val()

# electronics tray: flat platform tangent to the wall at the back, on two feet
dm = dirv(TRAY_AZ, TRAY_LAT); east = np.array([-math.sin(math.radians(TRAY_AZ)), math.cos(math.radians(TRAY_AZ)), 0]); north = np.cross(dm, east)
tray = cq.Workplane(plane_at(dm*(R_I-9.0), dm, east)).rect(TRAY_W, TRAY_H).extrude(-3.0)
tray = tray.faces("<Z").workplane().pushPoints([(x, y) for x in range(-30, 31, 10) for y in range(-10, 11, 10)]).hole(3.2)   # M3 / zip-tie grid
for d in tray_pts:
    foot = cq.Workplane(plane_at(d*(R_I-6.3), d, np.cross([0,0,1], d))).rect(20, 14).extrude(-3.2)   # 0.3 standoff; the bolt clamps it
    tray = tray.union(foot)
    web = cq.Workplane(plane_at(d*(R_I-6.3), d, np.cross([0,0,1], d))).rect(20, 14).extrude(-3.7)   # bridges foot to platform
    tray = tray.union(web)
    tray = tray.cut(cq.Workplane(plane_at(d*(R_I-4.0), d, np.cross([0,0,1], d))).circle(SCREW_CLR/2).extrude(-10))
for d in tray_pts:      # clearance for the boss skirts where the platform corners reach them
    tray = tray.cut((cq.Workplane(plane_at(d*(R_I-6.4), d, np.cross([0,0,1], d))).circle(7.8)
                     .workplane(offset=6.4+3.5).circle(7.8+6.4).loft()))
elec_tray = tray.val()
log(f"hat parts valid: plate={crown_plate.isValid()} template={drill_template.isValid()} tray={elec_tray.isValid()}")


# ═════════════════════════════ EXPORT ═════════════════════════════════════════
os.makedirs(OUT, exist_ok=True)
cq.exporters.export(visor, OUT+"visor.step")
if STAGE == "all":
    cq.exporters.export(shell, OUT+"shell.step")
    cq.exporters.export(cq.Workplane("XY").newObject([shell_halves[0]]), OUT+"shell_half_BOTTOM.step")
    cq.exporters.export(cq.Workplane("XY").newObject([shell_halves[1]]), OUT+"shell_half_TOP.step")
    cq.exporters.export(cq.Workplane("XY").newObject([shell_supports[1]]), OUT+"shell_half_TOP_supports.step")
    cq.exporters.export(cq.Workplane("XY").newObject([shell_halves[1], shell_supports[1]]), OUT+"shell_half_TOP_with_supports.step")
    cq.exporters.export(cq.Workplane("XY").newObject([plate_p]), OUT+"seam_plate.step")            # print 4
    cq.exporters.export(cq.Workplane("XY").newObject([pivot_cap_p]), OUT+"pivot_cap.step")   # print 2
    cq.exporters.export(cq.Workplane("XY").newObject([crown_plate]), OUT+"hat_crown_frame.step")
    cq.exporters.export(cq.Workplane("XY").newObject([hat_spacers]), OUT+"hat_spacers.step")
    cq.exporters.export(cq.Workplane("XY").newObject([drill_template]), OUT+"hat_drill_template.step")
    cq.exporters.export(cq.Workplane("XY").newObject([elec_tray]), OUT+"electronics_tray.step")
    cq.exporters.export(cq.Workplane("XY").newObject([hat_env]), OUT+"hardhat_envelope_REFERENCE.step")
    for nm, e in (("ear_L", ears[0]), ("ear_R", ears[1])): cq.exporters.export(cq.Workplane("XY").newObject([e]), OUT+f"{nm}.step")
    cq.exporters.export(cq.Workplane("XY").newObject([ear_top_p]), OUT+"ear_half_top.step")   # print 2, cut face down
    cq.exporters.export(cq.Workplane("XY").newObject([ear_bot_p]), OUT+"ear_half_bottom.step")# print 2, cut face down
    asm = cq.Assembly()
    asm.add(shell, name="shell", color=cq.Color(0.85, 0.85, 0.9)); asm.add(visor, name="visor", color=cq.Color(0.2, 0.2, 0.25))
    asm.add(cq.Workplane("XY").newObject([ears[0]]), name="ear_L", color=cq.Color(0.85, 0.85, 0.9))
    asm.add(cq.Workplane("XY").newObject([ears[1]]), name="ear_R", color=cq.Color(0.85, 0.85, 0.9))
    asm.add(cq.Workplane("XY").newObject([crown_plate]), name="hat_crown_plate", color=cq.Color(0.3,0.3,0.35))
    asm.add(cq.Workplane("XY").newObject([elec_tray]), name="electronics_tray", color=cq.Color(0.3,0.3,0.35))
    asm.add(cq.Workplane("XY").newObject([hat_env]), name="hardhat_envelope", color=cq.Color(0.9,0.8,0.2))
    for i, jp in enumerate(pad_channels):
        az = (jp+0.5)*DAZ; d = dirv(az, SPLIT_LAT); east = np.array([-math.sin(math.radians(az)), math.cos(math.radians(az)), 0.0])
        pl = cq.Plane(origin=tuple(d*(R_I-PAD_T-PLATE_T)), xDir=tuple(east), normal=tuple(d))
        asm.add(cq.Workplane("XY").newObject([plate_p.moved(cq.Location(pl))]), name=f"seam_plate_{i}", color=cq.Color(0.3,0.3,0.35))
    asm.save(OUT+"mau5head_ASSEMBLY.step")
if STAGE == "all":
  with open(OUT+"pixel_map.csv", "w", newline="") as f:
    wtr = csv.writer(f); wtr.writerow(["channel","row","azimuth_deg","elevation_deg","x","y","z","pocket_mm"])
    for j, k, az, lat in pixels:
        p = dirv(az, lat)*R_O; wtr.writerow([j, k, f"{az:.2f}", f"{lat:.2f}", f"{p[0]:.1f}", f"{p[1]:.1f}", f"{p[2]:.1f}", PIX if lat <= LAT_MAX_ALL else PIX_HI])
log(f"DONE  pixels={len(pixels)}  channels={N_CH}")
if STAGE == "all":
    print("TUBE CUT LIST (1\" OD x 3/4\" ID polycarbonate):  per ear — 1 × centre %.0f mm, 2 × side %.0f mm   (×2 ears)" % (DOWEL_CUTS["centre"], DOWEL_CUTS["side"]))
