"""«زنگ آخر ۳ — انباری»: the same gym hall, the middle of the night. The soldier, locked in the storeroom and not
yet fully turned, taps on the door and warns them about the voices behind the hall doors. Realistic look (EEVEE,
real materials and soft shadows) on the cast, bodies driven by Mixamo clips, walks along real paths.

    ../cast/bpy.sh scene.py --still 40,120,...      -> test/real_XXXX.png
    ../cast/bpy.sh scene.py --save                  -> storeroom.blend (render.py renders from it)
Shots (seconds):
  A  0.0- 5.0 wide: the dark hall, everyone asleep                B  5.0- 8.0 the storeroom door: tap, tap
  C  8.0-10.5 I wake up                                           D 10.5-16.0 I cross the hall to the door
  E 16.0-19.0 a face in the window; I step back                   F 19.0-23.5 the soldier: "don't be scared"
  G 23.5-27.6 Mahsa comes over                                    H 27.6-30.2 Mahsa: "what do you want?"
  I 30.2-37.0 the soldier: "they're not people any more"          J 37.0-41.0 I look back at the hall doors
  K 41.0-49.0 the hall doors; mum's voice                         L 49.0-53.0 Kian wakes and goes to the doors
  M 53.0-56.0 the soldier: "don't open it!"                       N 56.0-59.2 Kian at the chain; Arian pulls him back
  O 59.2-62.5 Arian: "who do we believe?"                         P 62.5-67.5 Kazemi gets up
  Q 67.5-70.0 the window is dark                                  R 70.0-74.0 the same voice, the same words
  S 74.0-76.5 me, between the two doors
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
wins = [(1.0 + 2.3 * i, 2.6 + 2.3 * i, 3.0, 4.0) for i in range(4)] + [(12.2, 13.6, 3.0, 4.0)]
wall_y(D + WT / 2, -WT, W + WT, holes=wins + [(STORE_X0, STORE_X1, 0, 2.1)], name="Back wall")
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
box(((STORE_X0 + STORE_X1) / 2, D + 2.2, 1.5), (2.6, 0.15, 3.0), "store", "Store back")
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
for t0_, t1_, amp in ((5.2, 7.6, 0.6), (53.6, 55.6, 1.4)):
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
    for a_, b_ in ((44.4, 48.6), (69.8, 74.0)):
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
COTS = {"arian": 3.0, "me": 5.2, "kian": 7.4, "mahsa": 9.6}
COT_Y = 3.6
for who, cx in COTS.items():
    box((cx, COT_Y, 0.52), (1.9, 0.72, 0.08), "canvas", "Cot")
    for dx in (-0.85, 0.85):
        for dy in (-0.3, 0.3):
            box((cx + dx, COT_Y + dy, 0.25), (0.04, 0.04, 0.5), "steel", "Cot leg")
    box((cx + 0.55, COT_Y + 0.05, 0.6), (0.7, 0.6, 0.06), "blanket", "Folded blanket")
box((12.6, 3.3, 0.52), (1.9, 0.72, 0.08), "canvas", "Cot")                 # the soldier's cot (empty)
for dx in (-0.85, 0.85):
    for dy in (-0.3, 0.3):
        box((12.6 + dx, 3.3 + dy, 0.25), (0.04, 0.04, 0.5), "steel", "Cot leg")
box((13.2, 3.5, 0.68), (0.5, 0.35, 0.25), "bag", "Kit bag")
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


flicker(2, 67.5, 70.0, 5)
# the storeroom lamp (seen through the window) goes out when he's gone
for t, v in ((0, 1.0), (59.5, 1.0), (59.6, 0.0), (END, 0.0)):
    store_lamp.data.energy = 18 * v
    store_lamp.data.keyframe_insert("energy", frame=fr(t))
for fc in fcurves_of(store_lamp.data):
    for k in fc.keyframe_points:
        k.interpolation = "CONSTANT"
led.hide_render = True

# ------------------------------------------------------------------ cast
KEYS = ["me", "arian", "mahsa", "kian", "kazemi"]
CH = {}
for k in KEYS:
    CH[k] = cast.spawn(k)
# the soldier behind the storeroom window: pale, veins, but still himself
CH["soldierZ"] = cast.spawn("soldier", zombie=0.35, name="SoldierZ", seed=4)
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


def walk(who, t0, t1, pts, clipname="walking", back=False, end_face=None, turn=0.35):
    """`who` walks along the polyline pts (first point None = from where he stands) from t0 to t1.
    Feet keep their real stride: the clip speed follows the path speed. back=True: steps backwards,
    facing against the direction of travel. Turns smoothly into the path and (end_face) at the end."""
    pts = list(pts)
    if pts[0] is None:
        pts[0] = pos_at(who, t0 - 1.0 / FPS)
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


# ------------------------------------------------------------------ blocking
SIT = {k: (x - 0.25, COT_Y - 0.3, 0.0) for k, x in COTS.items()}
KZ_SIT = (KZ_SEAT[0], KZ_SEAT[1] - 0.3, 0.0)
WINDOW = (11.38, 9.0)                         # the storeroom door's window (x, y)
HALL = (0.0, 4.9)                             # the hall doors
ME_DOOR = (11.05, 8.1)
ME_BACK = (10.85, 7.55, 0)
MAHSA_DOOR = (11.85, 7.55, 0)
KIAN_CHAIN = (0.6, 4.95, 0)
ARIAN_GRAB = (1.4, 4.3, 0)
KZ_MID = (6.2, 6.0, 0)
WAKE = {"me": 5.6, "mahsa": 20.0, "kian": 49.0, "arian": 54.5, "kazemi": 62.0}   # eyes open from


def asleep(who, t):
    return who in WAKE and t < WAKE[who]


# everyone dozes on the cots (Kazemi on his crate) until they get up
UP = {"me": 10.5, "mahsa": 20.5, "kian": 49.5, "arian": 55.5, "kazemi": 62.5}
for k, off in (("arian", 0.0), ("me", 1.3), ("kian", 2.6), ("mahsa", 3.1)):
    act(k, "sitting_idle", 0.0, UP[k], SIT[k], 180, loop=True, src_from=off, speed=0.55)
act("kazemi", "sitting_idle", 0.0, UP["kazemi"], KZ_SIT, 180, loop=True, src_from=2.0, speed=0.5)
# ---- me: across the dark hall to the storeroom door
walk("me", 10.5, 16.0, [SIT["me"][:2], (7.2, 4.6), (9.6, 6.6), ME_DOOR], end_face=0)
act("me", "breathing_idle", 16.0, 17.2, ME_DOOR + (0,), 0, speed=1.0)
walk("me", 17.2, 17.9, [ME_DOOR, ME_BACK[:2]], back=True)
act("me", "nervously_look_around", 17.9, 30.2, ME_BACK, face(ME_BACK, WINDOW), loop=True, speed=0.9)
act("me", "breathing_idle", 30.2, 37.0, ME_BACK, face(ME_BACK, WINDOW), loop=True)
act("me", "breathing_idle", 37.0, 53.0, ME_BACK, face(ME_BACK, HALL), loop=True, src_from=2.0)
act("me", "nervously_look_around", 53.0, 74.0, ME_BACK, face(ME_BACK, (6.0, 5.6)), loop=True)
act("me", "nervously_look_around", 74.0, END, ME_BACK, face(ME_BACK, (6.0, 5.6)), src_from=1.5, speed=1.2)
# ---- Mahsa comes over while he talks
walk("mahsa", 20.5, 25.5, [SIT["mahsa"][:2], (10.6, 5.2), MAHSA_DOOR[:2]], end_face=face(MAHSA_DOOR, WINDOW))
act("mahsa", "breathing_idle", 25.5, 37.0, MAHSA_DOOR, face(MAHSA_DOOR, WINDOW), loop=True)
act("mahsa", "nervously_look_around", 37.0, END, MAHSA_DOOR, face(MAHSA_DOOR, HALL), loop=True, src_from=2.0)
# ---- Kian: "mum?" -- straight to the chained hall doors; his hands must really be on the chain
def hands_mid(who, t0, t1):
    rig = CH[who].rig
    ps = []
    for k in range(8):
        sc.frame_set(fr(t0 + (t1 - t0) * (k + 0.5) / 8))
        ps.append((rig.matrix_world @ rig.pose.bones["hand_r"].head + rig.matrix_world @ rig.pose.bones["hand_l"].head) / 2)
    return sum(ps, Vector()) / len(ps)


for _ in range(2):                         # stand him where the clip's hands meet the chain
    act("kian", "reloading", 55.0, 58.4, KIAN_CHAIN, 90, speed=1.0)
    hm = hands_mid("kian", 55.3, 58.2)
    KIAN_CHAIN = (KIAN_CHAIN[0] + CHAIN_AT[0] + 0.03 - hm.x, KIAN_CHAIN[1] + CHAIN_AT[1] - hm.y, 0)
act("kian", "reloading", 55.0, 58.4, KIAN_CHAIN, 90, speed=1.0)          # pulls at the chain
print("KIAN AT CHAIN", [round(v, 3) for v in KIAN_CHAIN], "hands", [round(v, 3) for v in hands_mid("kian", 55.3, 58.2)])
walk("kian", 49.5, 55.0, [SIT["kian"][:2], (5.0, 4.4), KIAN_CHAIN[:2]], end_face=90)
rc = random.Random(5)
t = 55.0
CHAIN_RIG.keyframe_insert("location", frame=fr(t))
while t < 58.3:                            # the chain jerks with his pulls
    t += rc.uniform(0.25, 0.45)
    CHAIN_RIG.location = (CHAIN_AT[0] + rc.uniform(0.01, 0.035), CHAIN_AT[1] + rc.uniform(-0.03, 0.03), CHAIN_AT[2] + rc.uniform(-0.02, 0.02))
    CHAIN_RIG.keyframe_insert("location", frame=fr(t))
CHAIN_RIG.location = CHAIN_AT
CHAIN_RIG.keyframe_insert("location", frame=fr(58.6))
walk("kian", 58.4, 59.2, [None, (1.25, 4.75)], back=True)
act("kian", "terrified", 59.2, END, (1.25, 4.75, 0), face((1.25, 4.75), HALL), src_from=2.0, speed=1.0)
# ---- Arian wakes and pulls him back
walk("arian", 55.5, 57.9, [SIT["arian"][:2], ARIAN_GRAB[:2]], end_face=face(ARIAN_GRAB, KIAN_CHAIN))
act("arian", "hands_forward_gesture", 57.9, 59.4, ARIAN_GRAB, face(ARIAN_GRAB, KIAN_CHAIN), speed=1.3)
act("arian", "thinking", 59.4, 62.5, ARIAN_GRAB, face(ARIAN_GRAB, (1.25, 4.75)), speed=1.0)
act("arian", "nervously_look_around", 62.5, END, ARIAN_GRAB, face(ARIAN_GRAB, (6.0, 6.0)), loop=True)
# ---- Kazemi gets up and stands between the two doors
walk("kazemi", 62.5, 64.2, [KZ_SIT[:2], KZ_MID[:2]], end_face=face(KZ_MID, (2.0, 4.6)))
act("kazemi", "hands_forward_gesture", 64.2, 67.0, KZ_MID, face(KZ_MID, (2.0, 4.6)), speed=1.0)
act("kazemi", "breathing_idle", 67.0, END, KZ_MID, face(KZ_MID, (2.0, 4.6)), loop=True)
# ---- the soldier behind the window
S_WIN = (WINDOW[0] + 0.02, D + 0.5, 0)
act("soldierZ", "breathing_idle", 16.8, 30.2, S_WIN, 180, loop=True, speed=0.8)
act("soldierZ", "thinking", 30.2, 37.0, S_WIN, 180, loop=True, speed=0.9)
act("soldierZ", "breathing_idle", 37.0, 53.0, S_WIN, 180, loop=True, speed=1.2, src_from=3.0)
act("soldierZ", "zombie_scream", 53.0, 56.0, S_WIN, 180, speed=1.0)
act("soldierZ", "zombie_idle", 56.0, 60.0, (S_WIN[0], S_WIN[1] + 0.5, 0), 180, loop=True)

PRESENT = {k: [(0, END)] for k in KEYS}
PRESENT["soldierZ"] = [(16.8, 59.5)]
WORRY = {"me": [(0, 0.0), (5.6, 1.0), (16.8, 2.0), (23.0, 1.4), (30.2, 1.8), (44.6, 2.0)],
         "mahsa": [(0, 0.0), (20.0, 1.2), (30.2, 1.8), (44.6, 2.0)],
         "kian": [(0, 0.0), (49.0, 0.6), (54.2, 2.0)],
         "arian": [(0, 0.0), (54.5, 1.6), (59.6, 2.0)],
         "kazemi": [(0, 0.0), (62.0, 1.4), (70.0, 2.0)],
         "soldierZ": [(0, 1.0), (30.2, 1.6), (53.0, 2.0)]}


def worry(who, t):
    pts = WORRY[who]
    v = pts[0][1]
    for (a, va), (b, vb) in zip(pts, pts[1:] + [(999, pts[-1][1])]):
        if a <= t < b:
            v = va + (vb - va) * seg(t, a, min(b, a + 0.8))
    return v


def present(who, t):
    return any(a <= t < b for a, b in PRESENT[who])


hs2 = P.box((TABLE[0] + 0.12, TABLE[1] - 0.05, 0.8), (0.06, 0.17, 0.04), M_["radio"], "Handset on table")

# ------------------------------------------------------------------ camera: (t0, t1, cam0, cam1, aim0, aim1, lens)
SHOTS = [
    (0.0, 5.0, (1.2, 0.45, 2.4), (1.5, 0.6, 2.3), (8.5, 5.6, 0.9), (8.7, 5.9, 1.0), 18),
    (5.0, 8.0, (11.3, 6.4, 1.45), (11.3, 7.0, 1.5), (11.3, 9.0, 1.35), (11.3, 9.0, 1.4), 30),
    (8.0, 10.5, (5.15, 1.75, 0.85), (5.1, 1.85, 0.86), (4.95, 3.3, 1.02), (4.95, 3.3, 1.05), 30),
    (10.5, 16.0, (4.3, 1.6, 1.7), (7.6, 4.4, 1.7), (6.6, 4.2, 1.1), (11.0, 8.4, 1.3), 24),
    (16.0, 19.0, (9.5, 7.1, 1.5), (9.6, 7.2, 1.5), (11.2, 8.6, 1.45), (11.2, 8.6, 1.45), 28),
    (19.0, 23.5, (11.22, 7.75, 1.58), (11.26, 8.05, 1.6), (11.38, 9.4, 1.62), (11.38, 9.4, 1.62), 34),
    (23.5, 27.6, (9.3, 6.0, 1.55), (9.45, 6.2, 1.55), (11.3, 8.0, 1.35), (11.35, 7.9, 1.35), 26),
    (27.6, 30.2, (11.55, 8.55, 1.5), (11.55, 8.5, 1.5), (11.85, 7.55, 1.45), (11.85, 7.55, 1.45), 34),
    (30.2, 37.0, (11.25, 7.55, 1.56), (11.28, 8.15, 1.6), (11.38, 9.45, 1.6), (11.38, 9.45, 1.62), 32),
    (37.0, 41.0, (11.45, 8.35, 1.62), (11.4, 8.3, 1.62), (0.0, 4.9, 1.2), (0.0, 4.9, 1.2), 30),
    (41.0, 49.0, (2.9, 5.9, 1.45), (1.9, 5.3, 1.5), (0.0, 4.9, 1.2), (0.0, 4.9, 1.2), 24),
    (49.0, 53.0, (4.3, 1.3, 1.5), (4.0, 1.4, 1.5), (6.6, 3.9, 1.0), (3.4, 4.6, 1.1), 22),
    (53.0, 56.0, (11.24, 7.9, 1.58), (11.3, 8.2, 1.6), (11.38, 9.45, 1.6), (11.38, 9.45, 1.6), 30),
    (56.0, 59.2, (2.7, 2.5, 1.5), (2.6, 2.6, 1.5), (0.8, 4.7, 1.0), (0.9, 4.6, 1.05), 24),
    (59.2, 62.5, (0.45, 5.75, 1.45), (0.5, 5.7, 1.45), (1.35, 4.4, 1.25), (1.35, 4.4, 1.25), 26),
    (62.5, 67.5, (4.6, 3.7, 1.6), (4.8, 3.9, 1.6), (7.2, 7.0, 1.2), (6.2, 6.0, 1.45), 26),
    (67.5, 70.0, (11.3, 6.4, 1.45), (11.3, 6.9, 1.5), (11.3, 9.0, 1.4), (11.3, 9.0, 1.42), 28),
    (70.0, 74.0, (3.2, 3.1, 1.45), (2.3, 3.7, 1.5), (0.0, 4.9, 1.2), (0.0, 4.9, 1.2), 24),
    (74.0, END, (9.55, 6.75, 1.45), (9.65, 6.8, 1.45), (10.85, 7.55, 1.35), (10.85, 7.55, 1.38), 30),
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
        st = dict(t=t, seed=ch.seed, worry=worry(who, t), talking=speaking(who, t), zombie=ch.zombie)
        if who == "soldierZ":                # pale and veined, but the face is still his own
            st["zombie"] = 0.0
            st["scream"] = 0.7 * seg(t, 53.6, 54.2) * (1 - seg(t, 55.6, 56.2))
        sk = ch.body.data.shape_keys
        fv = anim.face(st)
        if asleep(who, t):
            fv["eye-left-closure"] = fv["eye-right-closure"] = 1.0
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
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(HERE, os.environ.get("SAVE_AS", "storeroom.blend")))
