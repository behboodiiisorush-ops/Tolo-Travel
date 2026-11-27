"""«زنگ آخر ۴ — زره‌پوش»: the same night. The soldier behind the storeroom window tells them about an armoured car
in the yard behind the hall and pushes its keys under the door. Kazemi drives, «من» opens the yard gate, two of
them come out of the dark, they get away -- and on the road the car's radio plays the same voice: "son?...".
Realistic look (EEVEE) on the permanent cast, bodies driven by Mixamo clips, walks along real paths around things.

    ../cast/bpy.sh scene.py --still 40,120,...      -> test/real_XXXX.png
    ../cast/bpy.sh scene.py --save                  -> armored.blend (render.py renders from it)
Shots (seconds): see SHOTS below (A hall .. O inside the car on the road).
"""
import bpy, sys, os, math, random
from mathutils import Vector, Matrix
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "studio"))
sys.path.insert(0, os.path.join(HERE, "..", "cast"))
sys.path.insert(0, HERE)              # first: our captions.py, not studio/captions.py
bpy.ops.wm.read_factory_settings(use_empty=True)
import cast, mocap, anim  # noqa: E402
import props as P         # noqa: E402
from captions import LINES, END, speaking  # noqa: E402

LOOK = "real"
cast.STYLE = None
FPS = 24
N = int(END * FPS)
sc = bpy.context.scene
sc.render.fps = FPS
sc.frame_start, sc.frame_end = 1, N
MOC = os.path.join(HERE, "..", "mocap")
SPEED = 1.2            # default playback speed of the mocap clips


def fr(t):
    return int(round(t * FPS)) + 1


def seg(t, a, b):
    if t <= a:
        return 0.0
    if t >= b:
        return 1.0
    u = (t - a) / (b - a)
    return u * u * (3 - 2 * u)


def fcurves_of(owner):
    ad = owner.animation_data
    if not ad or not ad.action:
        return []
    act_ = ad.action
    if hasattr(act_, "fcurves") and len(act_.fcurves):
        return list(act_.fcurves)
    out = []
    for layer in getattr(act_, "layers", []):
        for strip in layer.strips:
            for cb in getattr(strip, "channelbags", []):
                out += list(cb.fcurves)
    return out


def key_vis(o, pts):
    """pts: [(seconds, visible)] constant keys on hide_render."""
    for t, v in pts:
        o.hide_render = not v
        o.keyframe_insert("hide_render", frame=max(1, fr(t)) if t > 0 else 1)
    for fc in fcurves_of(o):
        if fc.data_path == "hide_render":
            for k in fc.keyframe_points:
                k.interpolation = "CONSTANT"


def show(objs, spans):
    for o in objs:
        pts = [(0, False)]
        for a, b in spans:
            pts += [(a, True), (b, False)]
        key_vis(o, pts)


def mats():
    return dict(
        floor=P.mat("Gym floor", (0.78, 0.55, 0.32), 0.6), line=P.mat("Court line", (0.95, 0.95, 0.9), 0.6),
        wall_lo=P.mat("Wall low", (0.42, 0.56, 0.5), 0.8), wall_hi=P.mat("Wall high", (0.86, 0.84, 0.76), 0.9),
        ceil=P.mat("Ceiling", (0.62, 0.62, 0.6), 0.9), beam=P.mat("Beam", (0.45, 0.45, 0.47), 0.6, metal=0.5),
        night=P.mat("Night glass", (0.08, 0.12, 0.25), 0.1, emit=(0.08, 0.12, 0.3), strength=0.6),
        tube=P.mat("Light tube", (1, 1, 1), 0.3, emit=(0.95, 0.98, 1.0), strength=6.0),
        door=P.mat("Metal door", (0.32, 0.42, 0.55), 0.4, metal=0.4), bar=P.mat("Push bar", (0.75, 0.76, 0.78), 0.3, metal=0.8),
        sdoor=P.mat("Store door", (0.55, 0.56, 0.5), 0.5, metal=0.3), frame=P.mat("Door frame", (0.25, 0.25, 0.27), 0.5),
        canvas=P.mat("Cot canvas", (0.36, 0.42, 0.24), 0.9), steel=P.mat("Cot steel", (0.5, 0.5, 0.52), 0.4, metal=0.7),
        blanket=P.mat("Blanket", (0.55, 0.2, 0.18), 0.9), table=P.mat("Folding table", (0.85, 0.85, 0.82), 0.5),
        radio=P.mat("Radio", (0.18, 0.2, 0.16), 0.5), led=P.mat("Radio LED", (0.2, 1.0, 0.3), 0.3, emit=(0.2, 1.0, 0.3), strength=8),
        mat=P.mat("Gym mat", (0.2, 0.32, 0.6), 0.8), vault=P.mat("Vault box", (0.6, 0.42, 0.25), 0.7),
        store=P.mat("Store wall", (0.3, 0.3, 0.32), 0.9), shelf=P.mat("Shelf", (0.4, 0.38, 0.34), 0.7),
        crate=P.mat("Crate", (0.45, 0.4, 0.22), 0.8), blood=P.mat("Blood drop", (0.38, 0.02, 0.03), 0.3),
        key=P.mat("Key", (0.8, 0.72, 0.35), 0.3, metal=0.9), wire=P.mat("Window wire", (0.1, 0.1, 0.1), 0.5),
        bag=P.mat("Bag", (0.3, 0.32, 0.22), 0.8), dark=P.mat("Dark", (0.03, 0.03, 0.04), 0.9),
    )


M_ = mats()
SET = []


def box(loc, size, m, name="Set", rot=(0, 0, 0)):
    o = P.box(loc, size, M_[m] if isinstance(m, str) else m, name)
    o.rotation_euler = rot
    SET.append(o)
    return o


# ------------------------------------------------------------------ set: gym hall X 0..14, Y 0..9, H 4.6
W, D, H = 14.0, 9.0, 4.6
WT = 0.2
box((W / 2, D / 2, -0.05), (W, D, 0.1), "floor", "Floor")
box((W / 2, D / 2, H + 0.05), (W, D, 0.1), "ceil", "Ceiling")
for x in (2.0, 5.5, 9.0, 12.5):                       # roof beams
    box((x, D / 2, H - 0.15), (0.2, D, 0.3), "beam", "Beam")
# court lines (plain, no markings)
for (x, y, sx, sy) in ((W / 2, 0.8, W - 1.6, 0.06), (W / 2, D - 0.8, W - 1.6, 0.06), (0.8, D / 2, 0.06, D - 1.6),
                       (W - 0.8, D / 2, 0.06, D - 1.6), (W / 2, D / 2, 0.06, D - 1.6)):
    box((x, y, 0.003), (sx, sy, 0.006), "line", "Court line")
bpy.ops.mesh.primitive_torus_add(location=(W / 2, D / 2, 0.003), major_radius=1.6, minor_radius=0.03)
ring = bpy.context.object
ring.scale = (1, 1, 0.1)
ring.data.materials.append(M_["line"])
ring.name = "Court circle"
SET.append(ring)


def wall_x(x, y0, y1, holes=(), name="Wall"):
    """Wall across Y at x from y0 to y1; holes: [(ya, yb, za, zb)]. Two-tone (low green, high cream)."""
    cuts = sorted(holes)
    spans, y = [], y0
    for ya, yb, za, zb in cuts:
        spans.append((y, ya, 0, H))
        spans.append((ya, yb, zb, H))
        if za > 0:
            spans.append((ya, yb, 0, za))
        y = yb
    spans.append((y, y1, 0, H))
    for a, b, za, zb in spans:
        if b - a < 1e-3:
            continue
        lo_top = min(zb, 1.6)
        if lo_top > za:
            box((x, (a + b) / 2, (za + lo_top) / 2), (WT, b - a, lo_top - za), "wall_lo", name)
        hi_bot = max(za, 1.6)
        if zb > hi_bot:
            box((x, (a + b) / 2, (hi_bot + zb) / 2), (WT, b - a, zb - hi_bot), "wall_hi", name)


def wall_y(y, x0, x1, holes=(), name="Wall"):
    cuts = sorted(holes)
    spans, x = [], x0
    for xa, xb, za, zb in cuts:
        spans.append((x, xa, 0, H))
        spans.append((xa, xb, zb, H))
        if za > 0:
            spans.append((xa, xb, 0, za))
        x = xb
    spans.append((x, x1, 0, H))
    for a, b, za, zb in spans:
        if b - a < 1e-3:
            continue
        lo_top = min(zb, 1.6)
        if lo_top > za:
            box(((a + b) / 2, y, (za + lo_top) / 2), (b - a, WT, lo_top - za), "wall_lo", name)
        hi_bot = max(za, 1.6)
        if zb > hi_bot:
            box(((a + b) / 2, y, (hi_bot + zb) / 2), (b - a, WT, zb - hi_bot), "wall_hi", name)


# back wall (y = D): high night windows + the storeroom door at x 10.85..11.75
STORE_X0, STORE_X1 = 10.85, 11.75
wins = [(1.0, 2.6, 3.0, 4.0), (3.3, 4.9, 3.0, 4.0), (7.9, 9.5, 3.0, 4.0), (12.2, 13.6, 3.0, 4.0)]
EX0, EX1 = 5.9, 6.8                                   # the fire exit to the yard
wall_y(D + WT / 2, -WT, W + WT, holes=sorted(wins + [(STORE_X0, STORE_X1, 0, 2.1), (EX0, EX1, 0, 2.1)]), name="Back wall")
for xa, xb, za, zb in wins:
    box(((xa + xb) / 2, D + 0.1, (za + zb) / 2), (xb - xa, 0.02, zb - za), "night", "Night window")
    box(((xa + xb) / 2, D + 0.05, (za + zb) / 2), (0.04, 0.06, zb - za), "frame", "Window bar")
wall_y(-WT / 2, -WT, W + WT, holes=[(1.0 + 2.3 * i, 2.6 + 2.3 * i, 3.0, 4.0) for i in range(6)], name="Front wall")
for i in range(6):
    xa, xb = 1.0 + 2.3 * i, 2.6 + 2.3 * i
    box(((xa + xb) / 2, -0.1, 3.5), (xb - xa, 0.02, 1.0), "night", "Night window")
# left wall (x = 0): the hall's double doors at y 4.0..5.8
HALL_Y0, HALL_Y1 = 4.0, 5.8
wall_x(-WT / 2, 0, D, holes=[(HALL_Y0, HALL_Y1, 0, 2.3)], name="Left wall")
box((-0.4, (HALL_Y0 + HALL_Y1) / 2, 1.15), (0.1, HALL_Y1 - HALL_Y0 + 0.2, 2.4), "dark", "Behind hall doors")
wall_x(W + WT / 2, 0, D, name="Right wall")
HALL_LEAVES = []
for k, (hy, sgn) in enumerate(((HALL_Y0, 1), (HALL_Y1, -1))):
    hinge = P.empty(f"Hall hinge {k}", (0.02, hy, 0))
    leaf = P.box((0.02, hy + sgn * 0.45, 1.13), (0.05, 0.88, 2.24), M_["door"], f"Hall door {k}")
    bar = P.box((0.07, hy + sgn * 0.45, 1.0), (0.05, 0.7, 0.06), M_["bar"], f"Hall bar {k}")
    win = P.box((0.0, hy + sgn * 0.45, 1.7), (0.07, 0.25, 0.4), M_["dark"], f"Hall door window {k}")
    for o in (leaf, bar, win):
        o.parent = hinge
        o.matrix_parent_inverse = hinge.matrix_world.inverted()
        SET.append(o)
    HALL_LEAVES.append((hinge, sgn))
for s in (HALL_Y0 - 0.05, HALL_Y1 + 0.05):
    box((0.0, s, 1.15), (0.24, 0.1, 2.3), "frame", "Hall door frame")
box((0.0, (HALL_Y0 + HALL_Y1) / 2, 2.35), (0.24, HALL_Y1 - HALL_Y0 + 0.2, 0.1), "frame", "Hall door frame")
# a chain through the push bars (they barricaded the hall); CHAIN_RIG lets it jerk when Kian pulls at it
CHAIN_AT = (0.12, (HALL_Y0 + HALL_Y1) / 2, 1.0)
CHAIN_RIG = P.empty("Chain rig", CHAIN_AT)
for j in range(9):
    l = P.sphere((0.12, (HALL_Y0 + HALL_Y1) / 2 - 0.4 + j * 0.1, 1.0), 0.025, M_["bar"], "Chain", scale=(1, 1.6, 0.7))
    l.parent = CHAIN_RIG
    l.matrix_parent_inverse = CHAIN_RIG.matrix_world.inverted()
    SET.append(l)
# storeroom behind the back wall
SB_Y = D + 2.2
OW = (11.0, 11.6, 1.35, 1.9)                          # outer window (x0, x1, z0, z1)
for (x0_, x1_, z0_, z1_) in ((10.0, OW[0], 0, 3.0), (OW[1], 12.6, 0, 3.0), (OW[0], OW[1], 0, OW[2]), (OW[0], OW[1], OW[3], 3.0)):
    box(((x0_ + x1_) / 2, SB_Y, (z0_ + z1_) / 2), (x1_ - x0_, 0.15, z1_ - z0_), "store", "Store back")
for k in range(3):
    box((OW[0] + (k + 1) * (OW[1] - OW[0]) / 4, SB_Y, (OW[2] + OW[3]) / 2), (0.02, 0.03, OW[3] - OW[2]), "frame", "Window wire")
box((STORE_X0 - 0.85, D + 1.15, 1.5), (0.15, 2.1, 3.0), "store", "Store side")
box((STORE_X1 + 0.85, D + 1.15, 1.5), (0.15, 2.1, 3.0), "store", "Store side")
box(((STORE_X0 + STORE_X1) / 2, D + 1.15, 3.05), (2.6, 2.2, 0.1), "store", "Store ceiling")
box((STORE_X1 + 0.6, D + 1.6, 0.9), (0.4, 1.0, 1.8), "shelf", "Store shelf")
box((STORE_X0 - 0.55, D + 1.8, 0.3), (0.5, 0.5, 0.6), "crate", "Store crate")
store_lamp = P.area_light(((STORE_X0 + STORE_X1) / 2, D + 1.2, 2.9), ((STORE_X0 + STORE_X1) / 2, D + 1.2, 0), 18, 0.6,
                          (1.0, 0.45, 0.35), name="Store lamp")
for s in (STORE_X0 - 0.05, STORE_X1 + 0.05):
    box((s, D, 1.07), (0.1, 0.26, 2.14), "frame", "Store frame")
box(((STORE_X0 + STORE_X1) / 2, D, 2.15), (STORE_X1 - STORE_X0 + 0.2, 0.26, 0.1), "frame", "Store frame")
# storeroom door: hinge at STORE_X0, leaf with a small wired window (a real opening you see through)
s_hinge = P.empty("Store hinge", (STORE_X0, D - 0.06, 0))
lw = STORE_X1 - STORE_X0 - 0.02
wx0, wx1, wz0, wz1 = 0.28, 0.62, 1.32, 1.74          # window in leaf coords (x from hinge)
parts = [((lw / 2, 1.05), (lw, 0.04, 2.1 - 0.0))]
leaf_objs = []
for (cx, cz), sz in (((wx0 / 2, 1.05), (wx0, 0.05, 2.1)), (((wx1 + lw) / 2, 1.05), (lw - wx1, 0.05, 2.1)),
                     (((wx0 + wx1) / 2, wz0 / 2), (wx1 - wx0, 0.05, wz0)),
                     (((wx0 + wx1) / 2, (wz1 + 2.1) / 2), (wx1 - wx0, 0.05, 2.1 - wz1))):
    leaf_objs.append(P.box((STORE_X0 + cx, D - 0.06, cz), sz, M_["sdoor"], "Store door"))
for k in range(3):                                    # wire grid in the window
    leaf_objs.append(P.box((STORE_X0 + wx0 + (k + 1) * (wx1 - wx0) / 4, D - 0.06, (wz0 + wz1) / 2), (0.008, 0.01, wz1 - wz0),
                           M_["wire"], "Window wire"))
    leaf_objs.append(P.box((STORE_X0 + (wx0 + wx1) / 2, D - 0.06, wz0 + (k + 1) * (wz1 - wz0) / 4), (wx1 - wx0, 0.01, 0.008),
                           M_["wire"], "Window wire"))
leaf_objs.append(P.sphere((STORE_X0 + lw - 0.1, D - 0.11, 1.0), 0.03, M_["bar"], "Store knob"))
for o in leaf_objs:
    o.parent = s_hinge
    o.matrix_parent_inverse = s_hinge.matrix_world.inverted()
    SET.append(o)
# the storeroom door: shudders under the taps 5.2-7.6 and 53.6-55.6 (his fists)
pts = [(0, 0)]
for t0_, t1_, amp in ((3.3, 4.2, 0.5),):
    t = t0_
    while t < t1_:
        pts += [(t, 0), (t + 0.05, amp), (t + 0.12, 0)]
        t += 0.42 if amp < 1 else 0.22
pts.append((END, 0))
for t, a in pts:
    s_hinge.rotation_euler = (0, 0, math.radians(-a))
    s_hinge.keyframe_insert("rotation_euler", index=2, frame=fr(t))
# hall doors: a soft rattle while the voice speaks (someone leaning on them from outside)
rr = random.Random(3)
for hinge, sgn in HALL_LEAVES:
    pts = [(0, 0)]
    for a_, b_ in ():
        t = a_
        pts.append((t, 0))
        while t < b_:
            t += rr.uniform(0.5, 0.9)
            pts += [(t, sgn * rr.uniform(0.6, 1.2)), (t + 0.15, 0)]
    pts.append((END, 0))
    for t, a in pts:
        hinge.rotation_euler = (0, 0, math.radians(a))
        hinge.keyframe_insert("rotation_euler", index=2, frame=fr(t))

# camp beds: long along X, kids sit on the front edge facing -Y
COTS = {"arian": 2.6, "me": 5.2, "kian": 7.8, "mahsa": 10.4}   # 0.7 m gaps to walk through
COT_Y = 3.6
for who, cx in COTS.items():
    box((cx, COT_Y, 0.52), (1.9, 0.72, 0.08), "canvas", "Cot")
    for dx in (-0.85, 0.85):
        for dy in (-0.3, 0.3):
            box((cx + dx, COT_Y + dy, 0.25), (0.04, 0.04, 0.5), "steel", "Cot leg")
    box((cx + 0.55, COT_Y + 0.05, 0.6), (0.7, 0.6, 0.06), "blanket", "Folded blanket")
box((12.95, 3.3, 0.52), (1.9, 0.72, 0.08), "canvas", "Cot")                 # the soldier's cot (empty)
for dx in (-0.85, 0.85):
    for dy in (-0.3, 0.3):
        box((12.95 + dx, 3.3 + dy, 0.25), (0.04, 0.04, 0.5), "steel", "Cot leg")
box((13.2, 3.5, 0.68), (0.5, 0.35, 0.25), "bag", "Kit bag")
# Kian's green backpack on the floor by his cot
box((8.45, 2.95, 0.13), (0.32, 0.18, 0.26), P.mat("Kian backpack", (0.18, 0.42, 0.16), 0.7), "Backpack on floor")
# Kazemi's seat: an upturned crate by the radio table
KZ_SEAT = (7.6, 7.75)
box((KZ_SEAT[0], KZ_SEAT[1], 0.24), (0.55, 0.45, 0.48), "crate", "Seat crate")
# folding table with the radio (base unit) by the back wall
TABLE = (8.6, 8.35)
box((TABLE[0], TABLE[1], 0.74), (1.6, 0.7, 0.04), "table", "Table")
for dx in (-0.72, 0.72):
    box((TABLE[0] + dx, TABLE[1], 0.37), (0.04, 0.6, 0.74), "steel", "Table leg")
box((TABLE[0] - 0.2, TABLE[1] + 0.05, 0.86), (0.42, 0.26, 0.2), "radio", "Radio")
SET.append(P.cyl((TABLE[0] - 0.36, TABLE[1] + 0.12, 0.96), (TABLE[0] - 0.36, TABLE[1] + 0.12, 1.45), 0.008, M_["radio"], "Antenna"))
led = P.sphere((TABLE[0] - 0.05, TABLE[1] - 0.085, 0.92), 0.015, M_["led"], "Radio LED")
SET.append(led)
box((TABLE[0] + 0.45, TABLE[1], 0.8), (0.35, 0.25, 0.08), "crate", "Ration box")
# stacked gym mats and a vaulting box along the right wall
for k in range(4):
    box((13.3, 6.5, 0.08 + k * 0.15), (1.0, 2.0, 0.14), "mat", "Gym mat")
box((13.2, 1.4, 0.45), (1.2, 0.5, 0.9), "vault", "Vault box")
# blood drops near where the soldier stands
DROPS = []
r = random.Random(11)
for k in range(7):
    p = (11.2 + r.uniform(-0.35, 0.3), 5.75 + r.uniform(-0.25, 0.3), 0.004)
    o = P.sphere(p, 0.03, M_["blood"], "Blood drop", scale=(r.uniform(0.6, 1.3), r.uniform(0.6, 1.3), 0.06))
    SET.append(o)
    DROPS.append(o)
show(DROPS, [(0, END)])     # dried drops from the day before

# ------------------------------------------------------------------ the yard behind the hall (y > D), the car, the road
YD = 23.2                                    # the far yard wall with the gate
GX0, GX1 = 5.0, 9.0                          # gate opening
for k_, v_ in dict(asphalt=P.mat("Asphalt", (0.15, 0.15, 0.16), 0.85), yardwall=P.mat("Yard wall", (0.5, 0.48, 0.44), 0.9),
                   olive=P.mat("Armour paint", (0.22, 0.25, 0.17), 0.7, metal=0.15),
                   olive_dk=P.mat("Armour dark", (0.09, 0.1, 0.08), 0.8, metal=0.1),
                   tyre=P.mat("Tyre", (0.035, 0.035, 0.035), 0.9), gate=P.mat("Gate steel", (0.3, 0.31, 0.32), 0.5, metal=0.6),
                   headl=P.mat("Headlight glass", (1, 0.95, 0.8), 0.2, emit=(1, 0.95, 0.8), strength=8.0),
                   barrel=P.mat("Barrel", (0.25, 0.3, 0.42), 0.6, metal=0.3), pole=P.mat("Pole", (0.35, 0.35, 0.36), 0.5, metal=0.6),
                   lampglow=P.mat("Lamp glow", (1, 0.8, 0.5), 0.3, emit=(1, 0.78, 0.5), strength=12.0),
                   roadline=P.mat("Road line", (0.85, 0.85, 0.8), 0.6), redled=P.mat("Red LED", (1, 0.1, 0.05), 0.3, emit=(1, 0.1, 0.05), strength=6)).items():
    M_[k_] = v_
box((7.0, (D + YD) / 2 + 0.1, -0.05), (15.2, YD - D, 0.1), "asphalt", "Yard ground")
box((7.0, YD + 20, -0.06), (80, 40, 0.1), "asphalt", "Street")
box((-0.35, (D + YD) / 2 + 0.1, 1.3), (0.2, YD - D, 2.6), "yardwall", "Yard wall")
box((14.35, (D + YD) / 2 + 0.1, 1.3), (0.2, YD - D, 2.6), "yardwall", "Yard wall")
box(((-0.45 + GX0) / 2, YD, 1.3), (GX0 + 0.45, 0.25, 2.6), "yardwall", "Yard wall")
box(((GX1 + 14.45) / 2, YD, 1.3), (14.45 - GX1, 0.25, 2.6), "yardwall", "Yard wall")
for gx in (GX0, GX1):
    box((gx, YD, 1.4), (0.3, 0.35, 2.8), "yardwall", "Gate post")
# the sliding gate (bars), slides +X behind the wall
GATE = P.empty("Gate rig", (0, 0, 0))
gy = YD - 0.25
gparts = [P.box(((GX0 + GX1) / 2, gy, 0.12), (GX1 - GX0, 0.06, 0.1), M_["gate"], "Gate"),
          P.box(((GX0 + GX1) / 2, gy, 2.15), (GX1 - GX0, 0.06, 0.1), M_["gate"], "Gate"),
          P.box(((GX0 + GX1) / 2, gy, 1.1), (GX1 - GX0, 0.05, 0.06), M_["gate"], "Gate")]
x_ = GX0 + 0.06
while x_ < GX1:
    gparts.append(P.box((x_, gy, 1.13), (0.05, 0.05, 2.1), M_["gate"], "Gate bar"))
    x_ += 0.22
for o in gparts:
    o.parent = GATE
    SET.append(o)
# yard clutter
for (bx, by) in ((0.8, 21.6), (1.45, 22.1), (13.4, 13.6), (0.9, 12.6)):
    SET.append(P.cyl((bx, by, 0), (bx, by, 0.9), 0.3, M_["barrel"], "Barrel"))
box((1.1, 15.5, 0.35), (1.0, 0.8, 0.7), "crate", "Yard crate")
box((13.2, 18.5, 0.4), (1.2, 1.0, 0.8), "crate", "Yard crate")
# the exit door leaf: hinge at EX0, opens outwards into the yard
EXH = P.empty("Exit hinge", (EX0, D + 0.12, 0))
for o in (P.box((EX0 + 0.45, D + 0.12, 1.05), (0.88, 0.05, 2.1), M_["door"], "Exit door"),
          P.box((EX0 + 0.45, D + 0.07, 1.0), (0.7, 0.05, 0.06), M_["bar"], "Exit bar")):
    o.parent = EXH
    o.matrix_parent_inverse = EXH.matrix_world.inverted()
    SET.append(o)
for s_ in (EX0 - 0.05, EX1 + 0.05):
    box((s_, D + 0.1, 1.07), (0.1, 0.26, 2.14), "frame", "Exit frame")
box(((EX0 + EX1) / 2, D + 0.1, 2.15), (EX1 - EX0 + 0.2, 0.26, 0.1), "frame", "Exit frame")
for t_, a_ in ((0, 0), (33.7, 0), (34.5, 104), (END, 104)):
    EXH.rotation_euler = (0, 0, math.radians(a_))
    EXH.keyframe_insert("rotation_euler", index=2, frame=fr(t_))


def spot(name, loc, target, energy, angle=60, color=(1, 1, 1), blend=0.4, soft=0.1):
    L_ = bpy.data.lights.new(name, "SPOT")
    L_.energy, L_.color, L_.spot_size, L_.spot_blend = energy, color, math.radians(angle), blend
    L_.shadow_soft_size = soft
    o = bpy.data.objects.new(name, L_)
    sc.collection.objects.link(o)
    o.location = loc
    o.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    return o


def point(name, loc, energy, color=(1.0, 0.8, 0.55), soft=0.15):
    L_ = bpy.data.lights.new(name, "POINT")
    L_.energy, L_.color, L_.shadow_soft_size = energy, color, soft
    o = bpy.data.objects.new(name, L_)
    sc.collection.objects.link(o)
    o.location = loc
    return o


# a floodlight on a pole at the storeroom corner, lighting the car
SET.append(P.cyl((12.85, 11.5, 0), (12.85, 11.5, 4.6), 0.07, M_["pole"], "Flood pole"))
box((12.7, 11.6, 4.5), (0.4, 0.25, 0.2), "pole", "Flood head")
spot("Floodlight", (12.6, 11.7, 4.4), (7.5, 16.0, 0.0), 2600, angle=75, color=(0.85, 0.92, 1.0), blend=0.6)
# a lamp over the exit door outside (lights the ramp)
point("Exit lamp", (6.35, 9.45, 2.7), 220, color=(1.0, 0.78, 0.5))
box((6.35, 9.27, 2.75), (0.35, 0.12, 0.12), "lampglow", "Exit lamp box")
# street lamps beyond the gate
for sx_ in (2.0, 12.0):
    SET.append(P.cyl((sx_, 27.0, 0), (sx_, 27.0, 5.0), 0.08, M_["pole"], "Street pole"))
    SET.append(P.sphere((sx_, 27.0, 5.0), 0.18, M_["lampglow"], "Street lamp"))
    point("Street lamp light", (sx_, 27.0, 4.8), 900)

# ---- the armoured car, built around its rear-centre floor point at the origin, nose to +Y; no markings at all
APC = P.empty("APC", (0, 0, 0))
AP = []


def ab(loc, size, m, name="APC hull", rot=(0, 0, 0)):
    o = P.box(loc, size, M_[m], name)
    o.rotation_euler = rot
    AP.append(o)
    return o


L_, Wd, ZF, ZR = 6.4, 2.5, 0.62, 2.55        # length, width, floor, roof
ab((0, L_ / 2, ZF - 0.06), (Wd, L_, 0.12), "olive")
ab((0, L_ / 2, 0.42), (Wd - 0.3, L_ - 0.6, 0.3), "olive_dk")
for sx in (-1, 1):
    ab((sx * (Wd / 2 - 0.05), L_ / 2, (ZF + ZR) / 2), (0.1, L_, ZR - ZF), "olive")
    ab((sx * (Wd / 2 + 0.06), 3.1, 1.25), (0.14, 1.4, 0.45), "olive", "APC stowage")
ab((0, L_ / 2, ZR + 0.05), (Wd, L_, 0.1), "olive")
ab((-0.95, 0.05, (ZF + ZR) / 2), (0.6, 0.1, ZR - ZF), "olive")
ab((0.95, 0.05, (ZF + ZR) / 2), (0.6, 0.1, ZR - ZF), "olive")
ab((0, 0.05, (2.3 + ZR) / 2), (1.3, 0.1, ZR - 2.3), "olive")
ab((0, L_ - 0.05, (ZF + 1.55) / 2), (Wd, 0.1, 1.55 - ZF), "olive")
ab((0, L_ - 0.05, (1.8 + ZR) / 2), (Wd, 0.1, ZR - 1.8), "olive")
for xa, xb in ((-1.25, -0.95), (-0.15, 0.15), (0.95, 1.25)):
    ab(((xa + xb) / 2, L_ - 0.05, 1.675), (xb - xa, 0.1, 0.25), "olive")
ab((0, L_ + 0.35, 0.6), (Wd - 0.2, 0.7, 0.55), "olive", "APC nose")
ab((0, L_ + 0.3, 1.15), (Wd, 0.85, 0.1), "olive", "APC nose", rot=(math.radians(-38), 0, 0))
for sx in (-1, 1):
    ab((sx * 0.85, L_ + 0.66, 0.85), (0.3, 0.05, 0.16), "headl", "APC headlight")
    for wy in (0.9, 2.3, 4.0, 5.4):
        w_ = P.cyl((sx * 1.16, wy, 0.5), (sx * 1.5, wy, 0.5), 0.5, M_["tyre"], "APC wheel", verts=24)
        AP.append(w_)
        AP.append(P.cyl((sx * 1.5, wy, 0.5), (sx * 1.53, wy, 0.5), 0.22, M_["olive_dk"], "APC hub"))
    ab((sx * 1.33, 3.15, 1.06), (0.42, 5.9, 0.06), "olive", "APC fender")
AP.append(P.cyl((0.5, 4.7, ZR + 0.1), (0.5, 4.7, ZR + 0.22), 0.36, M_["olive"], "APC hatch"))
AP.append(P.cyl((-1.0, 0.6, ZR + 0.1), (-1.0, 0.6, ZR + 1.9), 0.012, M_["olive_dk"], "APC antenna"))
# inside: two benches, partition, driver's seat, dashboard with the radio
for sx in (-1, 1):
    ab((sx * 0.88, 1.9, ZF + 0.52), (0.42, 3.2, 0.08), "olive_dk", "APC bench")
    ab((sx * 0.88, 1.9, ZF + 0.24), (0.36, 3.1, 0.48), "olive_dk", "APC bench")
    ab((sx * 0.78, 4.1, (ZF + 1.5) / 2), (0.85, 0.06, 1.5 - ZF), "olive_dk", "APC partition")
ab((0.45, 4.55, ZF + 0.52), (0.46, 0.46, 0.08), "olive_dk", "APC seat")
ab((0.45, 4.3, ZF + 0.85), (0.46, 0.08, 0.6), "olive_dk", "APC seat")
ab((-0.45, 4.55, ZF + 0.52), (0.46, 0.46, 0.08), "olive_dk", "APC seat")
ab((-0.45, 4.3, ZF + 0.85), (0.46, 0.08, 0.6), "olive_dk", "APC seat")
ab((0, 6.05, 1.32), (Wd - 0.3, 0.3, 0.14), "olive_dk", "APC dash")
AP.append(P.cyl((0.45, 5.66, 1.3), (0.45, 5.62, 1.36), 0.19, M_["tyre"], "APC wheel steer"))
ab((-0.35, 5.95, 1.48), (0.36, 0.16, 0.18), "radio", "APC radio")
RLED = P.sphere((-0.25, 5.86, 1.52), 0.012, M_["led"], "APC radio led")
AP.append(RLED)
AP.append(P.sphere((-0.45, 5.86, 1.52), 0.01, M_["redled"], "APC radio led"))
# the rear ramp: hinge at the floor's rear edge; down = 26.3 deg (touches the ground), up = -90 (closed)
RAMP = P.empty("Ramp hinge", (0, 0, ZF))
rp = P.box((0, -0.7, ZF - 0.04), (1.3, 1.4, 0.08), M_["olive"], "APC ramp")
rp.parent = RAMP
rp.matrix_parent_inverse = RAMP.matrix_world.inverted()
RAMP.parent = APC
for o in AP:
    o.parent = APC
HEAD = [o for o in AP if o.name.startswith("APC headlight")]
HL = [spot(f"Headlight {i}", (sx * 0.85, L_ + 0.7, 0.85), (sx * 0.6, L_ + 12, 0.0), 0, angle=55, color=(1, 0.93, 0.8))
      for i, sx in enumerate((-1, 1))]
CABIN = point("Cabin lamp", (0, 2.2, ZR - 0.15), 0, color=(1.0, 0.55, 0.3))
for o in HL + [CABIN]:
    o.parent = APC
YARD_AT = Vector((7.0, 11.9, 0.0))
R0 = Vector((60.0, 0.0, 0.0))                # where the car stands for the last shot (the world slides past)
RAMP_DOWN, RAMP_UP = math.radians(26.3), math.radians(-90)
RAMP_END_Y = YARD_AT.y - 1.4 * math.cos(RAMP_DOWN)
for t_, a_ in ((0, RAMP_DOWN), (56.6, RAMP_DOWN), (57.4, RAMP_UP), (END, RAMP_UP)):
    RAMP.rotation_euler = (a_, 0, 0)
    RAMP.keyframe_insert("rotation_euler", index=0, frame=fr(t_))
for t_, p_ in ((0, YARD_AT), (57.6, YARD_AT), (59.0, YARD_AT + Vector((0, 2.6, 0))), (61.2, YARD_AT + Vector((0, 13.0, 0))),
               (62.3, YARD_AT + Vector((0, 22.0, 0))), (62.4, R0), (END, R0)):
    APC.location = p_
    APC.keyframe_insert("location", frame=fr(t_))
for fc in fcurves_of(APC):
    for k in fc.keyframe_points:
        if abs(k.co.x - fr(62.3)) < 0.5:
            k.interpolation = "CONSTANT"
show(HEAD, [(46.0, END)])
for o, e_ in [(l_, 900) for l_ in HL] + [(CABIN, 0)]:
    for t_, v_ in ((0, 0), (46.0, 0), (46.1, e_), (END, e_)):
        o.data.energy = v_
        o.data.keyframe_insert("energy", frame=fr(t_))
for t_, v_ in ((0, 6), (62.3, 6), (62.4, 30), (END, 30)):   # dim red glow inside; brighter amber on the road
    CABIN.data.energy = v_
    CABIN.data.keyframe_insert("energy", frame=fr(t_))
for fc in fcurves_of(CABIN.data) + [f for l_ in HL for f in fcurves_of(l_.data)]:
    for k in fc.keyframe_points:
        k.interpolation = "CONSTANT"
# the radio LED blinks while the voice plays
for t_, v_ in ((0, 0.2),):
    pass
RLED.hide_render = True
RLED.keyframe_insert("hide_render", frame=1)
t_ = 64.0
while t_ < 68.1:
    for dt, h in ((0.0, False), (0.12, True)):
        RLED.hide_render = h
        RLED.keyframe_insert("hide_render", frame=fr(t_ + dt))
    t_ += 0.22
for fc in fcurves_of(RLED):
    for k in fc.keyframe_points:
        k.interpolation = "CONSTANT"
# the road for the last shot: lamp posts and dashes slide past the parked car
box((R0.x, 60, -0.06), (30, 260, 0.1), "asphalt", "Road")
ROAD = P.empty("Road rig", (0, 0, 0))
for j in range(9):
    yy = 8 + j * 22.0
    for sx in (-1, 1):
        for o in (P.cyl((R0.x + sx * 5.0, yy, 0), (R0.x + sx * 5.0, yy, 6.0), 0.09, M_["pole"], "Road pole"),
                  P.sphere((R0.x + sx * 4.4, yy, 6.0), 0.2, M_["lampglow"], "Road lamp")):
            o.parent = ROAD
            SET.append(o)
        if sx > 0 or j % 2 == 0:
            lt = point("Road light", (R0.x + sx * 4.4, yy, 5.7), 1500)
            lt.parent = ROAD
for j in range(40):
    o = P.box((R0.x, 4 + j * 5.0, 0.0), (0.14, 2.2, 0.02), M_["roadline"], "Road line")
    o.parent = ROAD
    SET.append(o)
for t_, y_ in ((0, 0.0), (62.4, 0.0), (END, -105.0)):
    ROAD.location = (0, y_, 0)
    ROAD.keyframe_insert("location", frame=fr(t_))
for fc in fcurves_of(ROAD):
    for k in fc.keyframe_points:
        k.interpolation = "LINEAR"
# the keys: pushed out under the storeroom door, then in Kazemi's hand
KEYS_FLOOR0, KEYS_FLOOR1 = (11.32, 9.05), (11.22, 8.45)
KEYOBJ = P.box((KEYS_FLOOR0[0], KEYS_FLOOR0[1], 0.008), (0.09, 0.05, 0.012), M_["key"], "Keys")
KEYOBJ.rotation_euler = (0, 0, 0.4)
for t_, p_ in ((0, KEYS_FLOOR0), (12.6, KEYS_FLOOR0), (13.4, KEYS_FLOOR1)):
    KEYOBJ.location = (p_[0], p_[1], 0.008)
    KEYOBJ.keyframe_insert("location", frame=fr(t_))

# ------------------------------------------------------------------ lights (night: most tubes off)
w = bpy.data.worlds.new("W")
sc.world = w
w.color = (0.03, 0.04, 0.07)
sun = bpy.data.objects.new("Moon", bpy.data.lights.new("Moon", "SUN"))
sc.collection.objects.link(sun)
sun.data.energy = 1.2
sun.data.color = (0.6, 0.72, 1.0)
sun.rotation_euler = (math.radians(55), 0, math.radians(-30))
LAMPS = []
NIGHT = {0: 0.0, 1: 0.0, 2: 1.0, 3: 0.0, 4: 0.75}          # which tubes stay on, how strong
for k, (x, y) in enumerate(((3.5, 3.0), (7.5, 3.0), (11.0, 3.2), (4.0, 6.8), (9.0, 6.8))):
    l = P.area_light((x, y, H - 0.4), (x, y, 0), 260 * NIGHT[k], 1.6, (0.92, 0.97, 1.0), size_y=0.25,
                     name=f"Tube light {k}")
    tube = P.box((x, y, H - 0.33), (1.6, 0.12, 0.06), M_["tube"] if NIGHT[k] else M_["beam"], f"Tube {k}")
    SET.append(tube)
    LAMPS.append((l, tube))
# a small night lamp by the hall doors so the doors read in the dark
door_lamp = P.area_light((1.2, 4.9, 3.0), (0.0, 4.9, 1.2), 60, 0.8, (1.0, 0.85, 0.65), name="Door lamp")


def flicker(lamp_idx, t0, t1, seed):
    l, tube = LAMPS[lamp_idx]
    rr_ = random.Random(seed)
    pts = [(0, 1.0), (t0, 1.0)]
    t = t0
    while t < t1:
        t += rr_.uniform(0.06, 0.4)
        pts.append((t, rr_.choice([0.0, 0.15, 1.0, 0.4])))
    pts += [(t1, 1.0)]
    base = l.data.energy
    for t, v in pts:
        l.data.energy = base * v
        l.data.keyframe_insert("energy", frame=fr(t))
        tube.hide_render = v < 0.3
        tube.keyframe_insert("hide_render", frame=fr(t))
    for fc in fcurves_of(l.data) + fcurves_of(tube):
        for k in fc.keyframe_points:
            k.interpolation = "CONSTANT"


led.hide_render = True

# ------------------------------------------------------------------ cast
KEYS = ["me", "arian", "mahsa", "kian", "kazemi"]
CH = {}
for k in KEYS:
    CH[k] = cast.spawn(k)
# night in the shelter: Kian's backpack is off (it lies by his cot)
for o in [o for o in CH["kian"].objects if o.name.startswith("Backpack")]:
    CH["kian"].objects.remove(o)
    bpy.data.objects.remove(o, do_unlink=True)
# the soldier behind the storeroom window: pale, veins, but still himself
CH["soldierZ"] = cast.spawn("soldier", zombie=0.35, name="SoldierZ", seed=4)
CH["z1"] = cast.spawn_extra("passerby", 1, zombie=1.0)
CH["z2"] = cast.spawn_extra("passerby", 2, zombie=1.0)
M_ = mats()                                # cast building purges unused materials: re-create for later props
CLIP = {}


def clip(name):
    if name not in CLIP:
        CLIP[name] = mocap.load(os.path.join(MOC, name + ".fbx"))
    return CLIP[name]


def act(who, name, t0, t1, pos, facing, speed=SPEED, **kw):
    """Character `who` plays clip `name` from t0 to t1 (seconds) at pos/facing."""
    n = fr(t1) - fr(t0)
    mocap.apply(CH[who], clip(name), start=fr(t0), length=n, offset=pos, facing=facing, speed=speed, **kw)
    rig = CH[who].rig
    if "place" in kw:
        return
    rig.location = pos
    rig.rotation_euler = (0, 0, math.radians(facing) + math.pi)
    rig.keyframe_insert("location", frame=fr(t1) - 1)
    rig.keyframe_insert("rotation_euler", index=2, frame=fr(t1) - 1)


NAT = {}


def natural_speed(who, clipname):
    """metres per second the clip's feet really travel, on this character (for foot-locked walking)."""
    key = (who, clipname)
    if key in NAT:
        return NAT[key]
    c = clip(clipname)
    a = c.arm
    Mw = a.matrix_world
    b = {s: a.pose.bones[mocap._src_name(a, s)] for s in ("Hips", "LeftFoot", "RightFoot", "LeftUpLeg")}
    rest = {s: Mw @ pb.bone.matrix_local for s, pb in b.items()}
    src_leg = (rest["LeftUpLeg"].translation - rest["LeftFoot"].translation).length
    tr = CH[who].rig.data.bones
    tgt_leg = (tr["thigh_l"].matrix_local.translation - tr["foot_l"].matrix_local.translation).length
    hips, feet = [], []
    f = int(c.first)
    while f <= c.last:
        sc.frame_set(f)
        hips.append((Mw @ b["Hips"].head).copy())
        feet.append(((Mw @ b["LeftFoot"].head).copy(), (Mw @ b["RightFoot"].head).copy()))
        f += 1
    root = (hips[-1] - hips[0])
    root.z = 0
    sp = []
    for i in range(1, len(hips)):
        low = min(feet[i][0].z, feet[i][1].z)
        for s_ in (0, 1):
            if feet[i][s_].z < low + 0.02:
                v = (feet[i][s_] - hips[i]) - (feet[i - 1][s_] - hips[i - 1])
                v.z = 0
                sp.append(v.length * c.fps)
    sp.sort()
    v = sp[len(sp) // 2] if sp else 1.0
    if root.length > 0.5:                      # clip with real root motion: use it
        v = root.length / c.seconds
    NAT[key] = v * tgt_leg / max(1e-6, src_leg)
    print("NATURAL SPEED", who, clipname, round(NAT[key], 3))
    return NAT[key]


def pos_at(who, t):
    """where `who` stands (pelvis on the floor) at time t, from the motion keyed so far."""
    sc.frame_set(fr(t))
    rig = CH[who].rig
    p = rig.matrix_world @ rig.pose.bones["pelvis"].head
    return (p.x, p.y)


def facing_at(who, t):
    sc.frame_set(fr(t))
    return math.degrees(CH[who].rig.rotation_euler.z - math.pi)


def walk(who, t0, t1, pts, clipname="walking", back=False, end_face=None, turn=0.35, avoid=True, zfn=None):
    """`who` walks along the polyline pts (first point None = from where he stands) from t0 to t1.
    Feet keep their real stride: the clip speed follows the path speed. back=True: steps backwards,
    facing against the direction of travel. Turns smoothly into the path and (end_face) at the end."""
    pts = list(pts)
    if pts[0] is None:
        pts[0] = pos_at(who, t0 - 1.0 / FPS)
    if avoid and not back:
        pts = route(who, t0, t1, pts[0], pts[-1])
    P_ = [Vector((p[0], p[1], 0.0)) for p in pts]
    d0 = P_[1] - P_[0]
    f_prev = math.degrees(math.atan2(-d0.x, d0.y)) + (180 if back else 0)
    if t0 > 0.05:
        f_prev = facing_at(who, t0 - 1.0 / FPS)
    L = [0.0]
    for a, b in zip(P_, P_[1:]):
        L.append(L[-1] + (b - a).length)
    total = max(1e-4, L[-1])
    n = fr(t1) - fr(t0)
    dur = n / FPS
    ease = min(0.25, dur * 0.2)                    # accelerate / slow down over `ease` seconds
    vmax = total / (dur - ease)

    def dist(tt):                                  # distance along the path at tt seconds into the walk
        if tt < ease:
            return 0.5 * vmax * tt * tt / ease
        if tt > dur - ease:
            r = dur - tt
            return total - 0.5 * vmax * r * r / ease
        return vmax * (tt - ease / 2)

    def at(d):
        d = max(0.0, min(total, d))
        for i in range(len(P_) - 1):
            if d <= L[i + 1] or i == len(P_) - 2:
                u = (d - L[i]) / max(1e-6, L[i + 1] - L[i])
                return P_[i].lerp(P_[i + 1], max(0.0, min(1.0, u)))

    def angdiff(a, b):
        return (b - a + 180) % 360 - 180

    def place(j):
        tt = j / FPS
        d = dist(tt)
        p = at(d)
        q = at(min(total, d + 0.35)) - at(max(0.0, d - 0.05))
        if q.length < 1e-4:
            q = P_[-1] - P_[-2]
        fac = math.degrees(math.atan2(-q.x, q.y)) + (180 if back else 0)
        if tt < turn:
            fac = f_prev + angdiff(f_prev, fac) * seg(tt, 0, turn)
        if end_face is not None and tt > dur - turn:
            fac = fac + angdiff(fac, end_face) * seg(tt, dur - turn, dur)
        if zfn:
            p = Vector((p.x, p.y, zfn(p)))
        return tuple(p), fac

    sp = vmax / natural_speed(who, clipname)
    sp = max(0.5, min(2.2, sp))
    mocap.apply(CH[who], clip(clipname), start=fr(t0), length=n, offset=tuple(P_[0]), facing=f_prev,
                speed=-sp if back else sp, in_place=True, loop=True, place=place)
    return tuple(P_[-1])


def pace(who, name, t0, t1, pieces, start, facing, speed=1.0, center=True):
    """Root-motion clip played as a chain of short pieces [(src_a, src_b), ...] (repeated until t1), each one
    picking up exactly where the last one stopped, so he really walks to and fro without leaving the area.
    center: the whole walk is shifted so that its average position is `start`."""
    _pace(who, name, t0, t1, pieces, start, facing, speed)
    if center:
        ps = [Vector(pos_at(who, t0 + (t1 - t0) * k / 20) + (0.0,)) for k in range(20)]
        mid = sum(ps, Vector()) / len(ps)
        st = Vector((start[0], start[1], 0.0)) + (Vector((start[0], start[1], 0.0)) - mid)
        _pace(who, name, t0, t1, pieces, tuple(st), facing, speed)


def _pace(who, name, t0, t1, pieces, start, facing, speed):
    t, i = t0, 0
    want = Vector((start[0], start[1], 0.0))
    while t < t1 - 0.05:
        a, b = pieces[i % len(pieces)]
        te = min(t1, t + (b - a) / speed)
        off = Vector(want)
        for _ in range(2):                         # place the piece so that its first frame lands on `want`
            act(who, name, t, te, tuple(off), facing, speed=speed, src_from=a)
            got = Vector(pos_at(who, t) + (0.0,))
            off += want - got
        act(who, name, t, te, tuple(off), facing, speed=speed, src_from=a)
        want = Vector(pos_at(who, te - 1.0 / FPS) + (0.0,))
        t, i = te, i + 1


def face(a, b):
    """facing (deg) from point a towards point b (0 = +Y, 90 = -X)."""
    return math.degrees(math.atan2(-(b[0] - a[0]), b[1] - a[1]))


# ------------------------------------------------------------------ obstacles: people walk AROUND things
OBST_NAMES = ("Cot", "Table", "Seat crate", "Gym mat", "Backpack on floor", "APC hull", "APC wheel", "APC nose",
              "Store back", "Store side", "Barrel", "Yard crate", "Flood pole")
REGIONS = [(0.25, 0.25, W - 0.25, D - 0.25), (EX0 + 0.1, D - 0.6, EX1 - 0.1, D + 0.8), (0.1, D + 0.45, 14.0, YD - 0.45)]
BODY_R = 0.3                                  # half a body width + a little room
GRID = 0.05


def obstacle_boxes(who, t0, t1):
    """floor rectangles (x0, y0, x1, y1) nobody may walk through: furniture, plus anyone else standing or
    sitting still during this walk (seated people with their knees out in front)."""
    bs = []
    for o in bpy.data.objects:
        if o.type != "MESH" or not o.name.startswith(OBST_NAMES) or "leg" in o.name.lower() or o.hide_render:
            continue
        cs = [o.matrix_world @ Vector(c) for c in o.bound_box]
        if min(c.z for c in cs) > 1.2 or max(c.z for c in cs) < 0.02:
            continue
        bs.append((min(c.x for c in cs), min(c.y for c in cs), max(c.x for c in cs), max(c.y for c in cs)))
    for k in CH:
        if k == who or k in ("soldierZ", "z1", "z2"):
            continue
        a, b = Vector(pos_at(k, t0) + (0.0,)), Vector(pos_at(k, t1) + (0.0,))
        if (a - b).length > 0.1:
            continue                             # moving too: not a fixed obstacle
        r = 0.22
        sit = k in UP and t1 <= UP[k] + 0.05
        bs.append((a.x - r, a.y - (0.5 if sit else r), a.x + r, a.y + r))
    return bs


def _free(p, bs, R=BODY_R):
    if not any(x0 <= p.x <= x1 and y0 <= p.y <= y1 for x0, y0, x1, y1 in REGIONS):
        return False
    return not any(x0 - R < p.x < x1 + R and y0 - R < p.y < y1 + R for x0, y0, x1, y1 in bs)


def _clear(a, b, bs):
    n = max(2, int((b - a).length / 0.04))
    return all(_free(a.lerp(b, i / n), bs) for i in range(n + 1))


def route(who, t0, t1, a, b):
    """shortest smooth path from a to b around the obstacles (A* on a 5 cm grid, then pulled tight
    and rounded at the corners). If a is inside an obstacle's margin (sitting on a cot) he first steps
    straight out the way he faces."""
    import heapq
    bs = obstacle_boxes(who, t0, t1)
    a, b = Vector((a[0], a[1], 0)), Vector((b[0], b[1], 0))
    head = [a]
    if not _free(a, bs):
        f = math.radians(facing_at(who, max(0.0, t0 - 1.0 / FPS)))
        fw = Vector((-math.sin(f), math.cos(f), 0))
        for i in range(1, 40):
            q = a + fw * (0.05 * i)
            if _free(q, bs):
                head.append(q + fw * 0.08)
                break
    s = head[-1]
    tail = [b]
    if not _free(b, bs):                         # the goal itself is tight (e.g. at a wall): allow it
        bs_goal = [bb for bb in bs if not (bb[0] - BODY_R < b.x < bb[2] + BODY_R and bb[1] - BODY_R < b.y < bb[3] + BODY_R)]
        bs = bs_goal
    cell = lambda p: (int(round(p.x / GRID)), int(round(p.y / GRID)))
    pt = lambda c: Vector((c[0] * GRID, c[1] * GRID, 0))
    free_c = {}

    def ok(c):
        if c not in free_c:
            free_c[c] = _free(pt(c), bs)
        return free_c[c]
    cs, cg = cell(s), cell(b)
    openq = [(0.0, cs)]
    g = {cs: 0.0}
    came = {}
    nb = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    while openq:
        _, c = heapq.heappop(openq)
        if c == cg:
            break
        for dx, dy in nb:
            n_ = (c[0] + dx, c[1] + dy)
            if n_ != cg and not ok(n_):
                continue
            ng = g[c] + math.hypot(dx, dy)
            if ng < g.get(n_, 1e9):
                g[n_] = ng
                came[n_] = c
                heapq.heappush(openq, (ng + math.hypot(cg[0] - n_[0], cg[1] - n_[1]), n_))
    path = [b]
    c = cg
    while c in came:
        c = came[c]
        path.append(pt(c))
    path[-1] = s
    path.reverse()
    tight = [path[0]]                            # string pulling: keep only the corners
    i = 0
    while i < len(path) - 1:
        j = len(path) - 1
        while j > i + 1 and not _clear(path[i], path[j], bs):
            j -= 1
        tight.append(path[j])
        i = j
    pts = tight
    for _ in range(3):                           # round the corners (Chaikin), only where it stays clear
        if len(pts) < 3:
            break
        new = [pts[0]]
        for p, q in zip(pts, pts[1:]):
            new += [p.lerp(q, 0.25), p.lerp(q, 0.75)]
        new.append(pts[-1])
        new = [new[0]] + new[2:-2] + [new[-1]] if len(new) > 4 else new
        if all(_clear(u, v, bs) for u, v in zip(new, new[1:])):
            pts = new
        else:
            break
    full = head[:-1] + pts
    print("ROUTE", who, t0, "len %.2f" % sum((v - u).length for u, v in zip(full, full[1:])),
          [(round(p.x, 2), round(p.y, 2)) for p in tight], flush=True)
    return [(p.x, p.y) for p in full]


def stand_up(who, t, dur=0.6):
    """smooth sit -> stand: the body pose blends from the last seated frame into the walk over `dur` s."""
    rig = CH[who].rig
    f0, n = fr(t) - 1, max(2, int(dur * FPS))
    by = {}
    for fc in fcurves_of(rig):
        if fc.data_path.startswith("pose.bones"):
            by.setdefault(fc.data_path, {})[fc.array_index] = fc
    for path, comps in by.items():
        kp = {}
        for i, fc in comps.items():
            kp[i] = {int(round(k.co.x)): k for k in fc.keyframe_points}
        if any(f0 not in kp[i] for i in kp):
            continue
        base = {i: kp[i][f0].co.y for i in kp}
        for j in range(1, n + 1):
            f = f0 + j
            if any(f not in kp[i] for i in kp):
                continue
            w = smooth(j / n) if "smooth" in globals() else (j / n) ** 2 * (3 - 2 * j / n)
            cur = {i: kp[i][f].co.y for i in kp}
            sgn = 1.0
            if path.endswith("rotation_quaternion") and sum(base[i] * cur[i] for i in kp) < 0:
                sgn = -1.0
            for i in kp:
                k = kp[i][f]
                k.co.y = base[i] * sgn * (1 - w) + cur[i] * w
                k.handle_left.y = k.handle_right.y = k.co.y
    for fc in fcurves_of(rig):
        fc.update()


# ------------------------------------------------------------------ blocking
UP = {}
WAKE = {}
WHISPER = {}


def asleep(who, t):
    return False


import lipsync  # noqa: E402
LS = lipsync.Voices(fps=FPS)
VO = os.path.join(HERE, "voices")
for who_, f_, t_, af_ in (("me", "01_me", 0.6, None), ("soldierZ", "02_soldier", 4.4, "atempo=1.12"),
                          ("kazemi", "03_kazemi", 9.9, None), ("soldierZ", "04_soldier", 13.2, None),
                          ("mahsa", "05_mahsa", 16.9, None), ("soldierZ", "06_soldier", 20.0, None),
                          ("me", "07_me", 26.8, None), ("kazemi", "08_kazemi", 29.2, None),
                          ("mahsa", "09_mahsa", 50.2, None), ("kian", "11_kian", 68.6, None)):
    LS.add(who_, os.path.join(VO, f_ + ".mp3"), t_, af=af_)


def lips(who, t):
    """mouth follows the real ElevenLabs voice (loudness); the narrator's first line is a voice-over."""
    if who == "me" and t < 5.0:
        return 0.0
    return LS.level(who, t)


WINDOW = (11.38, 9.0)                         # the storeroom door's window (x, y)
S_WIN = (WINDOW[0] + 0.02, D + 0.5, 0)
P0 = {"me": (10.45, 7.75, 0), "mahsa": (11.9, 7.6, 0), "kazemi": (11.0, 7.15, 0), "arian": (10.15, 6.95, 0),
      "kian": (11.55, 6.7, 0)}


def F0(k):
    return face(P0[k], WINDOW)


def ramp_z(p):
    """standing height on the lowered ramp / inside the car while it is parked in the yard."""
    if abs(p.x - YARD_AT.x) > 0.75 or p.y <= RAMP_END_Y:
        return 0.0
    if p.y < YARD_AT.y:
        return (p.y - RAMP_END_Y) / (YARD_AT.y - RAMP_END_Y) * ZF
    return ZF


DOOR_IN, DOOR_OUT = (6.35, 8.45), (6.35, 9.75)
# ---- the start: all of them round the storeroom door, the soldier behind its window
for k in ("arian", "kian"):
    act(k, "nervously_look_around", 0.0, 29.8 if k == "arian" else 30.4, P0[k], F0(k), loop=True,
        src_from=1.3 if k == "kian" else 0.0, speed=0.8)
act("me", "breathing_idle", 0.0, 26.5, P0["me"], F0("me"), loop=True, speed=1.0)
act("me", "thinking", 26.5, 29.8, P0["me"], F0("me"), speed=1.0)
act("mahsa", "breathing_idle", 0.0, 16.7, P0["mahsa"], F0("mahsa"), loop=True, src_from=2.0)
act("mahsa", "hands_forward_gesture", 16.7, 19.0, P0["mahsa"], F0("mahsa"), speed=1.3)
act("mahsa", "nervously_look_around", 19.0, 31.0, P0["mahsa"], F0("mahsa"), loop=True, speed=0.8)
# ---- Kazemi: "where are the keys?" -> picks them up from under the door
act("kazemi", "breathing_idle", 0.0, 9.0, P0["kazemi"], F0("kazemi"), loop=True, src_from=4.0)
act("kazemi", "thinking", 9.0, 12.0, P0["kazemi"], F0("kazemi"), speed=1.2)
PICK = (11.22, 7.9, 0)
PICK_SP = 2.5
for _ in range(2):                              # stand him so that his hands reach the keys at the lowest point
    act("kazemi", "picking_up", 13.5, 17.4, PICK, 0, speed=PICK_SP)
    lo, lo_t = None, 13.5
    for f in range(fr(13.5), fr(17.4)):
        sc.frame_set(f)
        rig = CH["kazemi"].rig
        hm = (rig.matrix_world @ rig.pose.bones["hand_r"].head + rig.matrix_world @ rig.pose.bones["hand_l"].head) / 2
        if lo is None or hm.z < lo.z:
            lo, lo_t = hm.copy(), (f - 1) / FPS
    PICK = (PICK[0] + KEYS_FLOOR1[0] - lo.x, PICK[1] + KEYS_FLOOR1[1] - lo.y, 0)
act("kazemi", "picking_up", 13.5, 17.4, PICK, 0, speed=PICK_SP)
GRAB_T = lo_t
print("KAZEMI PICK", [round(v, 3) for v in PICK], "grab at", round(GRAB_T, 2), "hands z", round(lo.z, 3))
walk("kazemi", 12.0, 13.5, [P0["kazemi"][:2], PICK[:2]], end_face=0)
walk("kazemi", 17.4, 18.4, [PICK[:2], (10.95, 7.2)], back=True)
act("kazemi", "breathing_idle", 18.4, 29.2, (10.95, 7.2, 0), face((10.95, 7.2), WINDOW), loop=True)
show([KEYOBJ], [(0, GRAB_T)])
KH = P.box((0, 0, 0), (0.09, 0.05, 0.012), M_["key"], "Keys in hand")
KH.parent = CH["kazemi"].rig
KH.parent_type = "BONE"
KH.parent_bone = "hand_r"
KH.location = (0.0, -0.02, 0.0)
show([KH], [(GRAB_T, 40.2)])
# ---- across the hall to the fire exit, Kazemi first
walk("kazemi", 29.2, 33.2, [(10.95, 7.2), DOOR_IN], end_face=0)
act("kazemi", "hands_forward_gesture", 33.2, 34.6, DOOR_IN + (0,), 0, speed=1.4)
walk("kazemi", 34.6, 39.6, [DOOR_IN, DOOR_OUT, (8.95, 16.2)], end_face=270)
act("kazemi", "breathing_idle", 39.6, 40.2, (8.95, 16.2, 0), 270)
QUEUE = {"arian": (6.3, 7.75), "kian": (6.95, 7.5), "mahsa": (5.8, 7.45), "me": (6.0, 8.05)}
walk("arian", 29.8, 35.0, [P0["arian"][:2], QUEUE["arian"]], end_face=0)
walk("kian", 30.4, 35.4, [P0["kian"][:2], QUEUE["kian"]], end_face=0)
walk("mahsa", 31.0, 35.8, [P0["mahsa"][:2], QUEUE["mahsa"]], end_face=0)
walk("me", 29.8, 35.6, [P0["me"][:2], QUEUE["me"]], end_face=0)
for k, t0_, t1_ in (("arian", 35.0, 35.6), ("kian", 35.4, 36.2), ("mahsa", 35.8, 36.8), ("me", 35.6, 36.6)):
    act(k, "breathing_idle", t0_, t1_, QUEUE[k] + (0,), 0)
# ---- out to the car and up the ramp
walk("arian", 35.6, 39.0, [QUEUE["arian"], DOOR_IN, DOOR_OUT, (6.75, 10.3), (6.75, 11.9), (6.75, 12.9)], avoid=False, zfn=ramp_z)
walk("kian", 36.2, 39.6, [QUEUE["kian"], DOOR_IN, DOOR_OUT, (7.25, 10.3), (7.25, 11.9), (7.25, 12.8)], avoid=False, zfn=ramp_z)
walk("mahsa", 36.8, 40.0, [QUEUE["mahsa"], DOOR_IN, DOOR_OUT, (7.0, 10.3), (7.0, 11.95)], avoid=False, zfn=ramp_z,
     end_face=180)
act("arian", "breathing_idle", 39.0, 40.2, (6.75, 12.9, ZF), 0)
act("kian", "breathing_idle", 39.6, 40.2, (7.25, 12.8, ZF), 0)
MA_TOP = (7.0, 11.95, ZF)
act("mahsa", "breathing_idle", 40.0, 46.6, MA_TOP, 180, loop=True)
MA_LOW = (7.35, 10.35)
walk("mahsa", 46.6, 47.8, [MA_TOP[:2], MA_LOW], avoid=False, zfn=ramp_z, end_face=face(MA_LOW, (9.2, 20.0)))
act("mahsa", "nervously_look_around", 47.8, 49.6, MA_LOW + (0,), face(MA_LOW, (9.2, 20.0)), speed=1.0)
act("mahsa", "hands_forward_gesture", 49.6, 51.6, MA_LOW + (0,), face(MA_LOW, (9.2, 20.0)), speed=1.2)
act("mahsa", "nervously_look_around", 51.6, 55.0, MA_LOW + (0,), face(MA_LOW, (9.2, 20.0)), speed=1.2, src_from=2.0)
walk("mahsa", 55.0, 56.4, [MA_LOW, (7.0, 12.4)], back=True, avoid=False, zfn=ramp_z)
act("mahsa", "breathing_idle", 56.4, 57.4, (7.0, 12.4, ZF), 0)
# ---- «من»: out, round the car, the gate
walk("me", 36.6, 38.2, [QUEUE["me"], DOOR_IN, DOOR_OUT, (5.3, 10.6)], avoid=False)
walk("me", 38.2, 43.0, [(5.3, 10.6), (4.75, 13.0), (4.7, 20.5), (4.6, 22.45)], end_face=270, avoid=False)
GATE_P = 4.6
walk("me", 43.0, 48.0, [(GATE_P, 22.45), (GATE_P + 4.0, 22.45)], clipname="pistol_walk", end_face=270, avoid=False)
ME_G = (GATE_P + 4.0, 22.45)
act("me", "nervously_look_around", 48.0, 49.3, ME_G + (0,), face(ME_G, (13.5, 20.5)), speed=1.3)
walk("me", 49.3, 56.4, [ME_G, (9.35, 19.8), (9.25, 12.5), (7.8, 10.1), (7.0, 10.35), (7.0, 11.9), (7.0, 12.8)],
     avoid=False, zfn=ramp_z, end_face=0)
act("me", "breathing_idle", 56.4, 57.4, (7.0, 12.8, ZF), 0)
for t_, x_ in ((0, 0.0), (43.3, 0.0), (47.8, 4.0), (END, 4.0)):
    GATE.location = (x_, 0, 0)
    GATE.keyframe_insert("location", index=0, frame=fr(t_))
# ---- two of them out of the dark corner, after him
for k, path in (("z1", [(13.6, 21.4), (10.6, 19.2), (9.8, 12.3), (8.05, 10.0)]),
                ("z2", [(13.4, 22.5), (11.2, 20.2), (10.4, 12.8), (8.75, 10.45)])):
    act(k, "zombie_idle", 0.0, 48.8, path[0] + (0,), face(path[0], ME_G), loop=True)
    walk(k, 48.8, 56.9 if k == "z1" else 57.3, path, clipname="zombie_run", avoid=False, end_face=0)
    act(k, "zombie_attack", 56.9 if k == "z1" else 57.3, 58.6, path[-1] + (0,), 0, speed=1.1)
    walk(k, 58.6, 60.0, [path[-1], (path[-1][0] - 0.2, path[-1][1] + 2.2)], clipname="zombie_walk", avoid=False, end_face=0)
# ---- the soldier: behind the door window, later at the storeroom's outer window as they drive away
act("soldierZ", "breathing_idle", 0.0, 4.4, S_WIN, 180, loop=True, speed=0.8)
act("soldierZ", "thinking", 4.4, 9.0, S_WIN, 180, speed=1.0)
act("soldierZ", "breathing_idle", 9.0, 20.4, S_WIN, 180, loop=True, speed=0.9, src_from=3.0)
act("soldierZ", "shaking_head_no", 20.4, 22.4, S_WIN, 180, speed=0.9)
act("soldierZ", "thinking", 22.4, 29.5, S_WIN, 180, speed=0.8, src_from=1.0)
S_OUT = (11.3, SB_Y - 0.45, 0)
act("soldierZ", "breathing_idle", 59.8, 62.4, S_OUT, 0, loop=True, speed=0.8)
# ---- on the road (the car parked at R0, the world slides past)
SEATS = {"me": ((-0.58, 1.1), 270), "arian": ((-0.58, 2.4), 270), "mahsa": ((0.58, 1.35), 90), "kian": ((0.58, 2.55), 90)}
for k, ((sx, sy), fac) in SEATS.items():
    act(k, "sitting_idle", 62.4, END, (R0.x + sx, R0.y + sy, ZF), fac, loop=True, speed=0.6,
        src_from={"me": 0.0, "arian": 1.2, "mahsa": 2.3, "kian": 3.1}[k])
act("kazemi", "driving", 62.4, END, (R0.x + 0.45, R0.y + 4.85, ZF), 0, loop=True, speed=1.0)

PRESENT = {k: [(0, END)] for k in CH}
PRESENT["kazemi"] = [(0, 40.2), (62.4, END)]
PRESENT["arian"] = [(0, 40.2), (62.4, END)]
PRESENT["kian"] = [(0, 40.2), (62.4, END)]
PRESENT["mahsa"] = [(0, 57.4), (62.4, END)]
PRESENT["me"] = [(0, 57.4), (62.4, END)]
PRESENT["soldierZ"] = [(0, 29.5), (59.8, 62.4)]
PRESENT["z1"] = PRESENT["z2"] = [(48.8, 60.0)]
WORRY = {"me": [(0, 1.4), (26.5, 0.6), (38.0, 1.4), (48.0, 2.0), (57.0, 1.6), (64.0, 2.0)],
         "mahsa": [(0, 1.6), (16.7, 2.0), (31.0, 1.4), (48.0, 2.0), (62.4, 1.2), (64.0, 2.0)],
         "kian": [(0, 1.6), (62.4, 1.0), (64.0, 2.0)],
         "arian": [(0, 1.4), (62.4, 0.8), (64.0, 2.0)],
         "kazemi": [(0, 1.2), (29.0, 1.6), (62.4, 1.0), (64.5, 1.8)],
         "soldierZ": [(0, 1.4), (20.4, 2.0), (59.8, 1.2)],
         "z1": [(0, 0.0)], "z2": [(0, 0.0)]}


def worry(who, t):
    pts = WORRY[who]
    v = pts[0][1]
    for (a, va), (b, vb) in zip(pts, pts[1:] + [(999, pts[-1][1])]):
        if a <= t < b:
            v = va + (vb - va) * seg(t, a, min(b, a + 0.8))
    return v


def present(who, t):
    return any(a <= t < b for a, b in PRESENT[who])


# ------------------------------------------------------------------ camera: (t0, t1, cam0, cam1, aim0, aim1, lens)
SHOTS = [
    (0.0, 4.0, (7.6, 4.2, 1.7), (7.9, 4.5, 1.7), (10.9, 7.4, 1.2), (10.9, 7.4, 1.25), 24),
    (4.0, 9.0, (11.22, 7.75, 1.58), (11.26, 8.05, 1.6), (11.38, 9.4, 1.62), (11.38, 9.4, 1.62), 34),
    (9.0, 12.2, (11.95, 8.5, 1.62), (11.9, 8.45, 1.62), (11.0, 7.15, 1.55), (11.1, 7.4, 1.5), 30),
    (12.2, 16.5, (10.95, 7.85, 0.16), (10.97, 7.88, 0.17), (11.3, 8.95, 0.06), (11.28, 8.7, 0.18), 24),
    (16.5, 20.0, (11.05, 8.45, 1.5), (11.05, 8.4, 1.5), (11.9, 7.6, 1.45), (11.9, 7.6, 1.45), 34),
    (20.0, 25.5, (11.24, 7.8, 1.58), (11.3, 8.2, 1.6), (11.38, 9.45, 1.6), (11.38, 9.45, 1.62), 32),
    (25.5, 29.0, (11.3, 8.6, 1.55), (11.28, 8.55, 1.55), (10.45, 7.75, 1.5), (10.45, 7.75, 1.5), 30),
    (29.0, 33.0, (9.8, 4.6, 1.6), (8.6, 5.0, 1.6), (7.5, 8.0, 1.2), (6.6, 8.6, 1.3), 22),
    (33.0, 36.0, (5.0, 7.0, 1.7), (5.1, 7.2, 1.7), (6.35, 9.6, 1.3), (6.5, 10.8, 1.1), 24),
    (36.0, 40.2, (1.2, 10.2, 3.6), (1.4, 10.6, 3.5), (7.0, 13.0, 0.8), (7.2, 14.5, 0.8), 20),
    (40.2, 43.0, (3.0, 15.0, 1.6), (3.4, 17.5, 1.6), (4.6, 19.5, 1.2), (4.8, 22.5, 1.2), 24),
    (43.0, 49.0, (5.8, 19.2, 1.6), (6.3, 19.4, 1.6), (6.3, 22.6, 1.2), (8.2, 22.6, 1.2), 26),
    (49.0, 52.5, (6.2, 18.0, 1.5), (6.4, 17.6, 1.5), (11.5, 21.0, 1.2), (10.0, 17.0, 1.1), 24),
    (52.5, 56.8, (4.4, 9.8, 1.5), (4.5, 9.9, 1.5), (8.4, 13.5, 1.2), (7.4, 11.0, 1.2), 22),
    (56.8, 59.8, (3.0, 9.8, 1.5), (3.2, 10.2, 1.5), (7.0, 12.5, 1.3), (7.0, 22.0, 1.5), 22),
    (59.8, 62.4, (11.3, 12.55, 1.65), (11.3, 12.45, 1.65), (11.3, 11.2, 1.62), (11.3, 11.2, 1.62), 30),
    (62.4, END, (60.0, 0.35, 1.55), (60.0, 0.35, 1.55), (60.0, 4.8, 1.3), (60.0, 4.8, 1.3), 18),
]
cam = bpy.data.objects.new("Camera", bpy.data.cameras.new("Camera"))
sc.collection.objects.link(cam)
sc.camera = cam
cam.data.clip_start = 0.05
for t0, t1, c0, c1, a0, a1, lens in SHOTS:
    f0, f1 = fr(t0), fr(t1) - 1
    for f, c, a in ((f0, c0, a0), (f1, c1, a1)):
        cam.location = c
        cam.rotation_euler = (Vector(a) - Vector(c)).to_track_quat("-Z", "Y").to_euler()
        cam.keyframe_insert("location", frame=f)
        cam.keyframe_insert("rotation_euler", frame=f)
        cam.data.lens = lens
        cam.data.keyframe_insert("lens", frame=f)
rs = random.Random(9)                       # the road: the camera rides the bumps
base = Vector(SHOTS[-1][2])
for f in range(fr(62.4) + 2, fr(END) - 1, 2):
    cam.location = base + Vector((rs.uniform(-0.012, 0.012), rs.uniform(-0.01, 0.01), rs.uniform(-0.02, 0.02)))
    cam.keyframe_insert("location", frame=f)
for owner in (cam, cam.data):
    for fc in fcurves_of(owner):
        for k in fc.keyframe_points:
            k.interpolation = "LINEAR"
# ---- per shot: keep only the characters the camera can see (sampled every 4 frames, generous margins)
from bpy_extras.object_utils import world_to_camera_view
BONES = ("head", "pelvis", "hand_r", "hand_l", "foot_r", "foot_l", "spine_03", "lowerarm_r", "lowerarm_l", "calf_l", "calf_r")
VIS = {k: [] for k in CH}
for t0, t1, *_ in SHOTS:
    seen = set()
    for f in range(fr(t0), fr(t1), 4):
        sc.frame_set(f)
        for who, ch in CH.items():
            if who in seen or not any(a <= (f - 1) / FPS < b for a, b in PRESENT[who]):
                continue
            for bn in BONES:
                p = ch.rig.matrix_world @ ch.rig.pose.bones[bn].head
                v = world_to_camera_view(sc, cam, p)
                if v.z > 0 and -0.25 < v.x < 1.25 and -0.25 < v.y < 1.25:
                    seen.add(who)
                    break
    for who in seen:
        VIS[who].append((t0, t1))
print("VISIBLE", {k: [(round(a, 1), round(b, 1)) for a, b in v] for k, v in VIS.items()})
PRESENT = {k: [(max(a, c), min(b, d)) for a, b in VIS[k] for c, d in PRESENT[k] if max(a, c) < min(b, d)] for k in CH}
for who, ch in CH.items():
    for f in range(1, N + 1):
        t = (f - 1) / FPS
        st = dict(t=t, seed=ch.seed, worry=worry(who, t), talking=lips(who, t), zombie=ch.zombie)
        if who == "soldierZ":                # pale and veined, but the face is still his own
            st["zombie"] = 0.0
        sk = ch.body.data.shape_keys
        fv = anim.face(st)
        for k, v in fv.items():
            if k in ch.keys:
                ch._put(sk, f'key_blocks["{k}"].value', 0, f, max(0.0, min(1.0, v)))
        if f == 1 or present(who, t) != present(who, t - 1 / FPS):
            ch.hide(f, not present(who, t))
    ch.flush()
import json
os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
json.dump({"cuts": [s[0] for s in SHOTS]}, open(os.path.join(HERE, "out", "cuts.json"), "w"))

# ------------------------------------------------------------------ look: realistic, tuned for speed
# (raytracing off + subdivision off: 26 s a frame instead of 87 s, almost the same picture)
sc.frame_set(1)
sc.render.engine = "BLENDER_EEVEE"
sc.eevee.taa_render_samples = int(os.environ.get("SAMPLES", "8"))
for attr, v in (("use_gtao", True), ("use_shadows", True), ("use_raytracing", False)):
    if hasattr(sc.eevee, attr):
        setattr(sc.eevee, attr, v)
try:
    sc.view_settings.view_transform = "AgX"
    sc.view_settings.look = "AgX - Punchy"
except TypeError:
    sc.view_settings.view_transform = "Filmic"
sc.view_settings.exposure = float(os.environ.get("EXPOSURE", "1.15"))
for o in bpy.data.objects:
    for md in o.modifiers:
        if md.type == "SUBSURF":
            md.render_levels = 0
sc.render.resolution_x, sc.render.resolution_y = 540, 960
sc.render.film_transparent = False

args = sys.argv
if "--still" in args:
    os.makedirs(os.path.join(HERE, "test"), exist_ok=True)
    for f in [int(v) for v in args[args.index("--still") + 1].split(",")]:
        sc.frame_set(f)
        sc.render.filepath = os.path.join(HERE, "test", f"{LOOK}_{f:04d}.png")
        bpy.ops.render.render(write_still=True)
if "--save" in args:
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(HERE, os.environ.get("SAVE_AS", "armored.blend")))
