"""«دیوار» — three flats in a row sealed with steel; the only way is through the walls. Comic look (EEVEE cel
shading + ink outlines) on the realistic cast, bodies driven by Mixamo motion capture.

    ../cast/bpy.sh scene.py --still 40,120,...      -> test/s_XXXX.png
    ../cast/bpy.sh scene.py --save                  -> wall.blend (render.py renders from it)
Shots (seconds):
  1  0.0- 5.0  mom opens the front door: a steel plate behind it
  1b 5.0- 7.4  Kazemi pulls the curtain: steel behind the glass
  2  7.4-12.4  phone: no signal; punches on the steel
  3  12.4-16.4 Kazemi knocks the wall (hollow); mom searches under the sink
  3b 16.4-19.0 mom stands up with a sledgehammer that isn't theirs
  4  19.0-24.5 Kazemi smashes the wall
  5  24.5-27.0 he jumps through into the dark kitchen next door
  5b 27.0-33.5 Arian and Mahsa under the table
  6  33.5-41.0 the next wall
  7  41.0-47.0 Rezaei sitting on a bed;   7b 47.0-51.0 the bite on his arm
  8  51.0-58.8 the TV news;   8b 58.8-62.0 everyone turns to Rezaei, lights flicker
  9  62.0-66.0 a knock in the far wall;  9b 66.0-72.0 Kian through the hole;  9c 72.0-75.5 Rezaei looks up
"""
import bpy, sys, os, math
from mathutils import Vector, Matrix
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "cast"))
sys.path.insert(0, os.path.join(HERE, "..", "studio"))
bpy.ops.wm.read_factory_settings(use_empty=True)
import cast, mocap, anim  # noqa: E402
import props as P         # noqa: E402
import toon_look as T     # noqa: E402
from captions import LINES, END, speaking  # noqa: E402

cast.STYLE = cast.CARTOON
FPS = 24
N = int(END * FPS)
sc = bpy.context.scene
sc.render.fps = FPS
sc.frame_start, sc.frame_end = 1, N
MOC = os.path.join(HERE, "..", "mocap")
TEX = os.path.join(HERE, "textures")


def fr(t):
    return int(round(t * FPS)) + 1


def seg(t, a, b):
    if t <= a:
        return 0.0
    if t >= b:
        return 1.0
    u = (t - a) / (b - a)
    return u * u * (3 - 2 * u)


# ------------------------------------------------------------------ set: three flats along +X
H = 2.7
WT = 0.16
UNITS = {"A": (0.0, 5.0), "B": (5.16, 10.16), "C": (10.32, 15.32)}
D = 4.5
M_ = dict(
    wallA=P.mat("Wall A", (0.8, 0.76, 0.68), 0.9), wallB=P.mat("Wall B", (0.42, 0.52, 0.48), 0.9),
    wallC=P.mat("Wall C", (0.4, 0.42, 0.52), 0.9), floor=P.mat("Floor", (0.55, 0.38, 0.24), 0.7),
    tileB=P.mat("Kitchen floor", (0.78, 0.78, 0.74), 0.5), ceil=P.mat("Ceiling", (0.7, 0.7, 0.68), 0.9),
    steel=P.mat("Steel", (0.42, 0.46, 0.5), 0.35, metal=0.6), rivet=P.mat("Rivet", (0.3, 0.33, 0.36), 0.3, metal=0.6),
    door=P.mat("Door", (0.62, 0.42, 0.26), 0.6), frame=P.mat("Frame", (0.95, 0.95, 0.93), 0.5),
    glass=P.mat("Window glass", (0.55, 0.62, 0.68), 0.1), curtain=P.mat("Curtain", (0.62, 0.18, 0.2), 0.9),
    sofa=P.mat("Sofa", (0.25, 0.4, 0.55), 0.9), wood=P.mat("Wood", (0.45, 0.3, 0.18), 0.6),
    counter=P.mat("Counter", (0.9, 0.9, 0.88), 0.4), cab=P.mat("Cabinet", (0.35, 0.5, 0.42), 0.6),
    metal=P.mat("Metal", (0.7, 0.72, 0.74), 0.3, metal=0.8), bed=P.mat("Bed sheet", (0.85, 0.85, 0.8), 0.9),
    blanket=P.mat("Blanket", (0.4, 0.32, 0.5), 0.9), rubble=P.mat("Rubble", (0.8, 0.76, 0.68), 0.95),
    brick=P.mat("Brick", (0.62, 0.36, 0.28), 0.9), dark=P.mat("Dark", (0.05, 0.05, 0.06), 0.9),
    handle=P.mat("Hammer handle", (0.55, 0.38, 0.2), 0.6), head=P.mat("Hammer head", (0.2, 0.2, 0.22), 0.4, metal=0.8),
    phone=P.mat("Phone body", (0.08, 0.08, 0.1), 0.3), fridge=P.mat("Fridge", (0.88, 0.9, 0.9), 0.3),
)
SET = []


def put(o):
    SET.append(o)
    return o


def box(loc, size, m, name="Set"):
    return put(P.box(loc, size, M_[m] if isinstance(m, str) else m, name))


def room(u, wm, fm):
    x0, x1 = UNITS[u]
    cx = (x0 + x1) / 2
    box((cx, D / 2, -0.05), (x1 - x0, D, 0.1), fm, f"{u} floor")
    box((cx, D / 2, H + 0.05), (x1 - x0, D, 0.1), "ceil", f"{u} ceiling")
    box((cx, D + WT / 2, H / 2), (x1 - x0, WT, H), wm, f"{u} back wall")


def wall_with_hole(x, hy, hw, hz0, hz1, m, name, plug_until=None, cracks=()):
    """Wall across X at x (y 0..D) with a hole; the hole is plugged (intact wall) until `plug_until` seconds."""
    parts = [box((x, hy - hw / 2 - (hy - hw / 2) / 2, H / 2), (WT, hy - hw / 2, H), m, name),
             box((x, (hy + hw / 2 + D) / 2, H / 2), (WT, D - hy - hw / 2, H), m, name),
             box((x, hy, (hz1 + H) / 2), (WT, hw, H - hz1), m, name)]
    if hz0 > 0:
        parts.append(box((x, hy, hz0 / 2), (WT, hw, hz0), m, name))
    if plug_until is not None:
        plug = box((x, hy, (hz0 + hz1) / 2), (WT, hw, hz1 - hz0), m, name + " plug")
        key_vis(plug, [(0, True), (plug_until, False)])
        for k, (tc, s) in enumerate(cracks):           # dark cracks on both faces, growing with each blow
            for side in (-1, 1):
                for j in range(4):
                    ang = (j * 47 + k * 23) % 180
                    c = box((x + side * (WT / 2 + 0.004), hy + 0.1 * math.cos(ang), (hz0 + hz1) / 2 + 0.1 * math.sin(ang)),
                            (0.006, 0.02, 0.32 * s), "dark", name + " crack")
                    c.rotation_euler = (math.radians(ang), 0, 0)
                    key_vis(c, [(0, False), (tc, True), (plug_until, False)])
        # rubble on the floor (both sides) after the break
        import random
        r = random.Random(int(x * 10))
        for j in range(16):
            side = -1 if j % 2 else 1
            b = box((x + side * r.uniform(0.15, 0.9), hy + r.uniform(-0.6, 0.6), 0.05),
                    (r.uniform(0.08, 0.22),) * 2 + (r.uniform(0.05, 0.12),), "rubble" if j % 3 else "brick", name + " rubble")
            b.rotation_euler = (0, 0, r.uniform(0, 3))
            key_vis(b, [(0, False), (plug_until, True)])
    return parts


def key_vis(o, pts):
    """pts: [(seconds, visible)] constant keys on hide_render/hide_viewport."""
    for t, v in pts:
        f = max(1, fr(t)) if t > 0 else 1
        o.hide_render = not v
        o.hide_viewport = False
        o.keyframe_insert("hide_render", frame=f)
    ad = o.animation_data
    if ad and ad.action and hasattr(ad.action, "fcurves"):
        for fc in ad.action.fcurves:
            for k in fc.keyframe_points:
                k.interpolation = "CONSTANT"


def steel_plate(loc, size, axis, name):
    """Riveted steel plate; axis 'y' = plate in the XZ plane."""
    sx, sz = size
    p = box(loc, (sx, 0.04, sz) if axis == "y" else (0.04, sx, sz), "steel", name)
    for i in range(int(sx / 0.25) + 1):
        for z in (0.06, sz - 0.06):
            off = -sx / 2 + 0.06 + i * (sx - 0.12) / max(1, int(sx / 0.25))
            c = Vector(loc) + (Vector((off, 0, z - sz / 2)) if axis == "y" else Vector((0, off, z - sz / 2)))
            put(P.sphere(c + (Vector((0, 0.025, 0)) if axis == "y" else Vector((0.025, 0, 0))), 0.012, M_["rivet"], name + " rivet"))
    # weld seam across the middle
    box(loc, (sx, 0.05, 0.015) if axis == "y" else (0.05, sx, 0.015), "rivet", name + " seam")
    return p


for u, wm, fm in (("A", "wallA", "floor"), ("B", "wallB", "tileB"), ("C", "wallC", "floor")):
    room(u, wm, fm)
# front wall of A (y=0) with the door at x 0.75..1.65 and the window at x 2.9..4.3
box((0.375, -WT / 2, H / 2), (0.75, WT, H), "wallA", "A front")
box((1.2, -WT / 2, 2.4), (0.9, WT, 0.6), "wallA", "A front")
box((2.275, -WT / 2, H / 2), (1.25, WT, H), "wallA", "A front")
box((3.6, -WT / 2, 0.45), (1.4, WT, 0.9), "wallA", "A front")
box((3.6, -WT / 2, 2.4), (1.4, WT, 0.6), "wallA", "A front")
box((4.65, -WT / 2, H / 2), (0.7, WT, H), "wallA", "A front")
for x0, x1 in ((0.75, 1.65),):
    for s in (x0 - 0.04, x1 + 0.04):
        box((s, -0.01, 1.05), (0.08, WT + 0.04, 2.1), "frame", "Door frame")
    box(((x0 + x1) / 2, -0.01, 2.13), (x1 - x0 + 0.16, WT + 0.04, 0.08), "frame", "Door frame")
steel_plate((1.2, -0.12, 1.05), (0.9, 2.1), "y", "Door steel")
box((3.6, 0.03, 1.5), (0.04, 0.04, 1.2), "frame", "Window bar")
steel_plate((3.6, -0.12, 1.5), (1.4, 1.2), "y", "Window steel")
# door leaf (hinge at x=0.75, swings into the room)
hinge = P.empty("A door hinge", (0.75, 0.0, 0))
leaf = box((1.2, 0.0, 1.03), (0.88, 0.05, 2.05), "door", "A door")
knob = put(P.sphere((1.55, 0.06, 1.0), 0.035, M_["metal"], "A door knob"))
for o in (leaf, knob):
    o.parent = hinge
    o.matrix_parent_inverse = hinge.matrix_world.inverted()
for t, a in ((0.0, 0), (1.6, 0), (2.9, 78), (END, 78)):
    hinge.rotation_euler = (0, 0, math.radians(a))
    hinge.keyframe_insert("rotation_euler", index=2, frame=fr(t))
# other walls of A: left (x=0) solid with a steel-covered balcony door
box((-WT / 2, D / 2, H / 2), (WT, D, H), "wallA", "A left")
steel_plate((0.12, 2.6, 1.05), (0.85, 2.1), "x", "Balcony steel")
box((0.04, 2.6, 2.13), (0.06, 1.0, 0.08), "frame", "Balcony frame")
# A|B wall (x = 5.08) with the hole at y 2.2, plugged until 23.3
WALL_AB_T = 23.3
wall_with_hole(5.08, 2.2, 1.0, 0.25, 1.75, M_["wallA"], "AB wall", plug_until=WALL_AB_T,
               cracks=((20.6, 0.6), (21.9, 1.0)))
# B|C wall (x = 10.24) hole at y 2.0, plugged until 39.6
WALL_BC_T = 39.6
wall_with_hole(10.24, 2.0, 1.0, 0.25, 1.75, M_["wallB"], "BC wall", plug_until=WALL_BC_T,
               cracks=((35.5, 0.6), (37.0, 1.0)))
# far wall of C (x=15.4) with a small dark hole at y 1.5 where Kian looks through
wall_with_hole(15.4, 1.5, 0.42, 1.12, 1.6, M_["wallC"], "C far wall")
box((15.9, 1.5, 1.35), (0.6, 1.4, 1.4), "dark", "Behind hole")
# front walls of B, C with steel windows
for u, wm in (("B", "wallB"), ("C", "wallC")):
    x0, x1 = UNITS[u]
    cx = (x0 + x1) / 2
    box((cx, -WT / 2, H / 2), (x1 - x0, WT, H), wm, f"{u} front")
    steel_plate((cx, 0.1, 1.5), (1.3, 1.1), "y", f"{u} window steel")
# furniture A: sofa, coffee table, sink counter with cabinet, phone
box((3.4, 3.95, 0.25), (2.0, 0.85, 0.5), "sofa", "Sofa")
box((3.4, 4.3, 0.65), (2.0, 0.2, 0.8), "sofa", "Sofa back")
box((3.4, 2.9, 0.22), (1.0, 0.55, 0.44), "wood", "Coffee table")
box((1.2, 4.2, 0.45), (1.6, 0.6, 0.9), "cab", "Sink cabinet")
box((1.2, 4.2, 0.92), (1.7, 0.66, 0.05), "counter", "Counter")
box((1.2, 4.15, 0.93), (0.5, 0.35, 0.03), "metal", "Sink")
put(P.cyl((1.2, 4.42, 0.94), (1.2, 4.42, 1.25), 0.015, M_["metal"], "Tap"))
sun = bpy.data.objects.new("Sun", bpy.data.lights.new("Sun", "SUN"))
sc.collection.objects.link(sun)
sun.data.energy = 2.6
sun.data.use_shadow = False
sun.rotation_euler = (math.radians(50), 0, math.radians(-35))
lamp_A = P.area_light((2.5, 2.2, 2.55), (2.5, 2.2, 0), 25, 3.0, (1.0, 0.88, 0.72), name="A lamp")
# B kitchen: table, counter, fridge (only the fridge light and the hole light it)
box((7.6, 2.4, 0.74), (1.5, 0.95, 0.05), "wood", "Kitchen table")
for dx in (-0.68, 0.68):
    for dy in (-0.4, 0.4):
        box((7.6 + dx, 2.4 + dy, 0.36), (0.05, 0.05, 0.72), "wood", "Table leg")
box((9.0, 4.2, 0.45), (2.0, 0.6, 0.9), "cab", "B counter")
box((9.0, 4.2, 0.92), (2.1, 0.66, 0.05), "counter", "B counter top")
box((5.7, 4.15, 0.9), (0.7, 0.65, 1.8), "fridge", "Fridge")
lamp_B = P.area_light((7.6, 2.2, 2.55), (7.6, 2.2, 0), 15, 3.0, (0.75, 0.85, 1.0), name="B lamp")
# C bedroom: bed, dresser with the TV, bedside lamp
box((13.0, 3.6, 0.25), (1.6, 1.8, 0.5), "wood", "Bed frame")
box((13.0, 3.6, 0.55), (1.55, 1.75, 0.12), "bed", "Mattress")
box((13.0, 3.3, 0.63), (1.56, 1.1, 0.05), "blanket", "Blanket")
box((11.2, 4.25, 0.4), (1.2, 0.45, 0.8), "wood", "Dresser")
box((11.2, 4.32, 1.12), (0.86, 0.05, 0.52), "phone", "TV body")
tvm = bpy.data.materials.new("TV screen")
tvm.use_nodes = True
nt = tvm.node_tree
nt.nodes.clear()
o_ = nt.nodes.new("ShaderNodeOutputMaterial")
e_ = nt.nodes.new("ShaderNodeEmission")
tx = nt.nodes.new("ShaderNodeTexImage")
tx.image = bpy.data.images.load(os.path.join(TEX, "tv.png"))
nt.links.new(tx.outputs[0], e_.inputs[0])
e_.inputs["Strength"].default_value = 1.6
nt.links.new(e_.outputs[0], o_.inputs[0])
scr = put(P.plane((11.2, 4.29, 1.12), (0.8, 0.46), tvm, rot=(math.radians(90), 0, 0), name="TV screen"))
lamp_C = P.area_light((13.0, 2.2, 2.55), (13.0, 2.2, 0), 15, 3.0, (1.0, 0.8, 0.6), name="C lamp")
tv_glow = P.area_light((11.2, 3.9, 1.2), (11.8, 2.4, 1.2), 30, 0.8, (0.6, 0.7, 1.0), name="TV glow")
# lights flicker 59.6-62 (C lamp)
for k, t in enumerate([0, 59.6, 59.8, 60.0, 60.15, 60.5, 60.7, 61.2, 61.4, 62.0]):
    lamp_C.data.energy = 15 if k % 2 == 0 else 0
    sun.data.energy = 2.6 if k % 2 == 0 else 1.2
    sun.data.keyframe_insert("energy", frame=fr(t))
    lamp_C.data.keyframe_insert("energy", frame=fr(t))
w = bpy.data.worlds.new("W")
sc.world = w
w.color = (0.08, 0.08, 0.1)

# ------------------------------------------------------------------ cast
KEYS = ["mom", "kazemi", "arian", "mahsa", "rezaei", "kian"]
CH = {}
for k in KEYS:
    if k == "rezaei":
        ch = cast.spawn(k, zombie=0.35, bite=("upperarm_r", (0, -0.03, 0), 0.6))
    else:
        ch = cast.spawn(k)
    T.register(ch, k, realistic=True)
    CH[k] = ch
# mom's cream sweater reads as bare skin in the flat look: make it maroon
skin, clothes = T.SKIN[CH["mom"].name]
clothes = dict(clothes)
for kk in list(clothes):
    if "sweater" in kk:
        clothes[kk] = (0.55, 0.16, 0.22)
T.SKIN[CH["mom"].name] = (skin, clothes)
CLIP = {}


def clip(name):
    if name not in CLIP:
        CLIP[name] = mocap.load(os.path.join(MOC, name + ".fbx"))
    return CLIP[name]


def act(who, name, t0, t1, pos, facing, **kw):
    """Character `who` plays clip `name` from t0 to t1 (seconds) at pos/facing."""
    n = fr(t1) - fr(t0) + 1
    mocap.apply(CH[who], clip(name), start=fr(t0), length=n, offset=pos, facing=facing, **kw)


# who is in which set (hidden otherwise, saves render time)
PRESENT = {
    "mom": [(0, 19.0), (26.6, 75.5)], "kazemi": [(0, 75.5)], "arian": [(24.5, 75.5)], "mahsa": [(24.5, 75.5)],
    "rezaei": [(41.0, 75.5)], "kian": [(62.0, 75.5)],
}
# ---- mom
act("mom", "opening_door_inwards", 0.0, 3.4, (1.25, 1.35, 0), 180)
act("mom", "nervously_look_around", 3.4, 7.4, (1.35, 1.25, 0), 160)
act("mom", "breathing_idle", 7.4, 10.0, (1.6, 1.45, 0), 200, src_from=1.0)
act("mom", "punching_bag", 10.0, 12.4, (1.2, 0.62, 0), 180)
act("mom", "opening_a_filing_cabinet", 12.4, 16.4, (1.2, 3.45, 0), 0, src_from=1.4, speed=0.7)
act("mom", "pushing", 16.4, 19.0, (1.2, 3.45, 0), 180, src_from=2.0, speed=0.75)
act("mom", "nervously_look_around", 24.5, 33.5, (5.7, 3.0, 0), -70)
act("mom", "breathing_idle", 33.5, 41.0, (8.6, 3.0, 0), -100)
act("mom", "nervously_look_around", 41.0, 51.0, (11.3, 2.7, 0), -60)
act("mom", "breathing_idle", 51.0, 59.4, (11.7, 2.6, 0), 10)
act("mom", "nervously_look_around", 59.4, 75.5, (11.7, 2.6, 0), -55, loop=True)
# ---- Kazemi
act("kazemi", "breathing_idle", 0.0, 5.0, (3.9, 1.6, 0), 200)
act("kazemi", "opening_door_inwards", 5.0, 7.4, (3.55, 0.75, 0), 180)
act("kazemi", "cross_punch", 7.4, 9.6, (3.6, 0.72, 0), 180)
act("kazemi", "nervously_look_around", 9.6, 12.4, (3.6, 0.95, 0), 190)
act("kazemi", "punching_bag", 12.4, 13.4, (4.45, 2.2, 0), -90)
act("kazemi", "thinking", 13.4, 19.0, (4.3, 2.0, 0), -110)
act("kazemi", "double_dagger_stab", 19.0, 22.1, (4.45, 2.2, 0), -90)
act("kazemi", "double_dagger_stab", 22.1, 24.5, (4.45, 2.2, 0), -90, src_from=0.4)
act("kazemi", "jump", 24.5, 27.0, (4.35, 2.2, 0), -90)
act("kazemi", "breathing_idle", 27.0, 33.5, (6.5, 2.0, 0), -60)
act("kazemi", "double_dagger_stab", 33.5, 36.6, (9.6, 2.0, 0), -90)
act("kazemi", "double_dagger_stab", 36.6, 41.0, (9.6, 2.0, 0), -90, src_from=0.4, speed=0.85)
act("kazemi", "breathing_idle", 41.0, 51.0, (11.0, 2.3, 0), -70)
act("kazemi", "breathing_idle", 51.0, 59.4, (12.1, 2.3, 0), 5, src_from=3.0)
act("kazemi", "nervously_look_around", 59.4, 75.5, (12.1, 2.3, 0), -60, src_from=1.0, loop=True)
# ---- Arian and Mahsa under the table
act("arian", "pushing", 24.5, 27.0, (7.3, 1.9, 0), 180, speed=0.05)
act("arian", "pushing", 27.0, 29.5, (7.3, 1.75, 0), 180, src_from=0.2, speed=1.0)
act("arian", "nervously_look_around", 29.5, 33.5, (7.3, 1.6, 0), 160)
act("arian", "nervously_look_around", 33.5, 41.0, (8.4, 1.4, 0), -70, src_from=2.0)
act("arian", "breathing_idle", 41.0, 51.0, (11.0, 2.1, 0), -70)
act("arian", "breathing_idle", 51.0, 59.4, (11.3, 2.25, 0), 0, src_from=4.0)
act("arian", "terrified", 59.4, 75.5, (11.3, 2.25, 0), -50, src_from=1.0)
act("mahsa", "pushing", 24.5, 33.5, (7.9, 2.45, 0), 200, speed=0.04)
act("mahsa", "nervously_look_around", 33.5, 41.0, (8.1, 2.7, 0), -80)
act("mahsa", "nervously_look_around", 41.0, 51.0, (10.9, 2.9, 0), -60, src_from=3.0)
act("mahsa", "breathing_idle", 51.0, 59.4, (12.3, 2.85, 0), 0, src_from=6.0)
act("mahsa", "nervously_look_around", 59.4, 75.5, (12.3, 2.85, 0), -50, loop=True)
# ---- Rezaei on the bed
act("rezaei", "sitting_idle", 41.0, 75.5, (13.0, 3.0, 0.02), 180, loop=True)
# ---- Kian behind the far wall (only his face shows through the hole)
act("kian", "breathing_idle", 62.0, 75.5, (15.75, 1.5, 0), 90, loop=True)

# ---- faces (shape keys) and visibility
WORRY = {"mom": [(0, 0.2), (2.6, 1.8), (19, 1.2), (52, 1.6), (59, 2.0)],
         "kazemi": [(0, 0.3), (6.4, 1.4), (13, 0.6), (19, 1.0), (52, 1.5), (59, 1.9)],
         "arian": [(24.5, 2.0), (33, 1.4), (52, 1.6), (59, 2.0)], "mahsa": [(24.5, 2.0), (52, 1.6), (59, 2.0)],
         "rezaei": [(41, 0.0)], "kian": [(62, 2.0)]}


def worry(who, t):
    pts = WORRY[who]
    v = pts[0][1]
    for (a, va), (b, vb) in zip(pts, pts[1:] + [(999, pts[-1][1])]):
        if a <= t < b:
            v = va + (vb - va) * seg(t, a, min(b, a + 0.8))
    return v


def present(who, t):
    return any(a <= t < b for a, b in PRESENT[who])


for who, ch in CH.items():
    for f in range(1, N + 1):
        t = (f - 1) / FPS
        st = dict(t=t, seed=ch.seed, worry=worry(who, t), talking=speaking(who, t), zombie=ch.zombie)
        if who == "rezaei" and t > 72.0:
            st["scream"] = 0.4 * seg(t, 72.5, 74.0)
        sk = ch.body.data.shape_keys
        for k, v in anim.face(st).items():
            if k in ch.keys:
                ch._put(sk, f'key_blocks["{k}"].value', 0, f, max(0.0, min(1.0, v)))
        if f == 1 or present(who, t) != present(who, t - 1 / FPS):
            ch.hide(f, not present(who, t))
    ch.flush()

# ------------------------------------------------------------------ props in hands
# (cast building purges unused datablocks: re-create the materials the hand props use)
M_["handle"] = P.mat("Hammer handle", (0.55, 0.38, 0.2), 0.6)
M_["head"] = P.mat("Hammer head", (0.2, 0.2, 0.22), 0.4, metal=0.8)
M_["phone"] = P.mat("Phone body", (0.08, 0.08, 0.1), 0.3)
def hammer_mesh(name, length=0.95):
    """One mesh, origin at the grip, handle along local +Y, head at the end."""
    import bmesh
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=12, radius1=0.018, radius2=0.018, depth=length + 0.12,
                          matrix=Matrix.Translation((0, (length - 0.12) / 2, 0)) @ Matrix.Rotation(math.radians(90), 4, "X"))
    hm = Matrix.Translation((0, length, 0)) @ Matrix.Diagonal((0.1, 0.1, 0.26, 1))
    bmesh.ops.create_cube(bm, size=1.0, matrix=hm)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    sc.collection.objects.link(o)
    me.materials.append(M_["handle"])
    me.materials.append(M_["head"])
    for poly in me.polygons:
        if poly.center.y > length - 0.2 and abs(poly.center.z) > 0.03 or poly.center.y > length + 0.04:
            poly.material_index = 1
    put(o)
    return o


def holder(name, who, t_ref, both=True):
    """Sledgehammer in `who`'s right hand, the handle pointing at the left hand at t_ref."""
    ch = CH[who]
    sc.frame_set(fr(t_ref))
    rig = ch.rig
    hm = rig.matrix_world @ rig.pose.bones["hand_r"].matrix
    pr = hm.translation
    pl = (rig.matrix_world @ rig.pose.bones["hand_l"].matrix).translation
    d = (pl - pr) if both and (pl - pr).length > 0.03 else Vector((0, 0, -1))
    d.normalize()
    o = hammer_mesh(name)
    o.matrix_world = Matrix.Translation(pr) @ d.to_track_quat("Y", "Z").to_matrix().to_4x4()
    con = o.constraints.new("CHILD_OF")
    con.target, con.subtarget = rig, "hand_r"
    con.inverse_matrix = hm.inverted()
    return o, [o]


def show(objs, spans):
    for o in objs:
        pts = [(0, False)]
        for a, b in spans:
            pts += [(a, True), (b, False)]
        key_vis(o, pts)


ham_k, ham_k_parts = holder("Hammer Kazemi", "kazemi", 19.05)
show(ham_k_parts, [(19.0, 24.5), (33.5, 41.0)])
ham_m, ham_m_parts = holder("Hammer Mom", "mom", 17.6, both=False)
show(ham_m_parts, [(16.4, 19.0)])
hf = hammer_mesh("Hammer floor")
hf.matrix_world = Matrix.Translation((0.75, 4.2, 0.06)) @ Matrix.Rotation(math.radians(-80), 4, "Z")
floor_h = [hf]
show(floor_h, [(12.4, 16.4)])
# mom's phone in her right hand 7.4-10 (screen: dark grey + 'no signal' bars are in the caption)
sc.frame_set(fr(8.5))
pm = CH["mom"].rig.matrix_world @ CH["mom"].rig.pose.bones["hand_r"].matrix
ph = put(P.box(pm.translation + pm.to_3x3() @ Vector((0, 0.09, -0.02)), (0.075, 0.15, 0.01), M_["phone"], "Mom phone"))
ph.rotation_euler = pm.to_euler()
con = ph.constraints.new("CHILD_OF")
con.target, con.subtarget = CH["mom"].rig, "hand_r"
con.inverse_matrix = pm.inverted()
show([ph], [(7.4, 10.0)])

# ------------------------------------------------------------------ camera: shots (t0, t1, cam0, cam1, aim0, aim1, lens)
SHOTS = [
    (0.0, 5.0, (2.0, 3.3, 1.6), (1.8, 2.7, 1.55), (1.15, 0.2, 1.15), (1.15, 0.0, 1.2), 22),
    (5.0, 7.4, (4.7, 2.6, 1.5), (4.6, 2.3, 1.5), (3.5, 0.2, 1.45), (3.55, 0.1, 1.5), 22),
    (7.4, 12.4, (3.4, 3.4, 1.75), (3.3, 3.2, 1.7), (2.3, 0.6, 1.15), (2.2, 0.6, 1.15), 18),
    (12.4, 16.4, (2.6, 0.6, 1.5), (2.7, 0.7, 1.5), (4.6, 2.4, 1.3), (4.5, 2.5, 1.3), 20),
    (16.4, 19.0, (2.5, 1.7, 1.35), (2.4, 1.85, 1.35), (1.2, 3.45, 0.95), (1.2, 3.45, 1.1), 22),
    (19.0, 24.5, (3.2, 0.5, 1.35), (3.35, 0.55, 1.35), (4.95, 2.4, 1.2), (4.95, 2.35, 1.1), 20),
    (24.5, 27.0, (7.4, 0.55, 1.3), (7.3, 0.6, 1.3), (5.1, 2.2, 1.0), (5.3, 2.2, 1.0), 20),
    (27.0, 33.5, (9.2, 0.45, 1.05), (9.1, 0.5, 1.1), (7.2, 2.1, 0.6), (7.2, 2.0, 0.8), 19),
    (33.5, 41.0, (7.3, 0.45, 1.6), (7.5, 0.5, 1.55), (9.9, 2.2, 1.15), (10.1, 2.1, 1.1), 18),
    (41.0, 47.0, (11.7, 0.5, 1.55), (11.9, 0.8, 1.45), (13.0, 3.0, 1.0), (13.0, 3.0, 1.05), 24),
    (47.0, 51.0, (12.25, 2.1, 1.15), (12.35, 2.25, 1.15), (12.85, 3.1, 0.95), (12.85, 3.1, 0.95), 32),
    (51.0, 58.8, (12.2, 0.55, 1.6), (12.0, 0.8, 1.55), (11.2, 4.3, 1.1), (11.2, 4.3, 1.12), 22),
    (58.8, 62.0, (11.7, 4.0, 1.45), (11.75, 3.9, 1.45), (11.9, 2.4, 1.45), (11.9, 2.4, 1.45), 20),
    (62.0, 66.0, (12.6, 0.8, 1.4), (12.9, 1.0, 1.4), (15.4, 1.55, 1.3), (15.4, 1.5, 1.35), 22),
    (66.0, 72.0, (14.45, 1.5, 1.37), (14.75, 1.5, 1.37), (15.6, 1.5, 1.37), (15.6, 1.5, 1.37), 30),
    (72.0, 75.5, (13.1, 1.6, 1.0), (13.05, 2.2, 1.05), (13.0, 3.0, 1.18), (13.0, 3.0, 1.2), 28),
]
sc.frame_set(fr(49))
_r = CH["rezaei"].rig
_ua = (_r.matrix_world @ _r.pose.bones["upperarm_r"].head).lerp(_r.matrix_world @ _r.pose.bones["lowerarm_r"].head, 0.6)
SHOTS[10] = (47.0, 51.0, tuple(_ua + Vector((-0.45, -0.75, 0.2))), tuple(_ua + Vector((-0.38, -0.62, 0.18))),
             tuple(_ua), tuple(_ua), 30)
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
    ad = owner.animation_data
    if ad and ad.action and hasattr(ad.action, "fcurves"):
        for fc in ad.action.fcurves:
            for k in fc.keyframe_points:
                k.interpolation = "LINEAR"
# camera shake on the hammer blows / door reveal
# (small, keyed on top: handled in post with a short shake filter)

# ------------------------------------------------------------------ look
sc.frame_set(1)
T.toonify(sc, samples=int(os.environ.get("SAMPLES", "8")))
inked = [o for o in bpy.data.objects if o.type == "MESH" and not any(
    k in o.name.lower() for k in ("high-poly", "lash", "brow", "teeth", "tongue", "rivet", "crack", "screen", "glass",
                                  "floor", "ceiling"))]
T.ink(inked, 0.005)
sc.render.resolution_x, sc.render.resolution_y = 540, 960
sc.render.film_transparent = False
sc.eevee.use_shadows = True if hasattr(sc.eevee, "use_shadows") else None

args = sys.argv
if "--still" in args:
    os.makedirs(os.path.join(HERE, "test"), exist_ok=True)
    for f in [int(v) for v in args[args.index("--still") + 1].split(",")]:
        sc.frame_set(f)
        sc.render.filepath = os.path.join(HERE, "test", f"s_{f:04d}.png")
        bpy.ops.render.render(write_still=True)
if "--save" in args:
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(HERE, "wall.blend"))
