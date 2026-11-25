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
    wallA=P.mat("Wall A", (0.8, 0.76, 0.68), 0.9), wallB=P.mat("Wall B", (0.62, 0.64, 0.6), 0.9),
    wallC=P.mat("Wall C", (0.58, 0.58, 0.6), 0.9), floor=P.mat("Floor", (0.46, 0.42, 0.38), 0.7),
    tileB=P.mat("Kitchen floor", (0.78, 0.78, 0.74), 0.5), ceil=P.mat("Ceiling", (0.7, 0.7, 0.68), 0.9),
    steel=P.mat("Steel", (0.42, 0.46, 0.5), 0.35, metal=0.6), rivet=P.mat("Rivet", (0.3, 0.33, 0.36), 0.3, metal=0.6),
    door=P.mat("Door", (0.5, 0.44, 0.38), 0.6), frame=P.mat("Frame", (0.95, 0.95, 0.93), 0.5),
    glass=P.mat("Window glass", (0.55, 0.62, 0.68), 0.1), curtain=P.mat("Curtain", (0.62, 0.18, 0.2), 0.9),
    sofa=P.mat("Sofa", (0.4, 0.42, 0.45), 0.9), wood=P.mat("Wood", (0.42, 0.36, 0.3), 0.6),
    counter=P.mat("Counter", (0.9, 0.9, 0.88), 0.4), cab=P.mat("Cabinet", (0.55, 0.56, 0.54), 0.6),
    metal=P.mat("Metal", (0.7, 0.72, 0.74), 0.3, metal=0.8), bed=P.mat("Bed sheet", (0.85, 0.85, 0.8), 0.9),
    blanket=P.mat("Blanket", (0.45, 0.42, 0.44), 0.9), rubble=P.mat("Rubble", (0.8, 0.76, 0.68), 0.95),
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
        # the wall bursts: bricks and plaster chunks fly out of the hole and land on the floor (most of them on
        # the far side, away from the hammer), bounce once and come to rest
        import random
        r = random.Random(int(x * 10))
        g = 9.8
        for j in range(34):
            side = 1 if j % 4 else -1
            sz = (r.uniform(0.07, 0.2), r.uniform(0.06, 0.12), r.uniform(0.05, 0.1))
            p0 = Vector((x + side * 0.02, hy + r.uniform(-hw / 2 + 0.05, hw / 2 - 0.05), r.uniform(hz0 + 0.1, hz1 - 0.05)))
            v = Vector((side * r.uniform(0.8, 2.6), r.uniform(-0.6, 0.6), r.uniform(-0.2, 1.4)))
            spin = Vector((r.uniform(-12, 12), r.uniform(-12, 12), r.uniform(-8, 8)))
            t0 = plug_until + r.uniform(0.0, 0.25)
            b = box(tuple(p0), sz, "rubble" if j % 3 else "brick", name + " debris")
            b.data.transform(Matrix.Translation(-b.matrix_world.translation - p0))   # (P.box bakes the
            b.location = p0                                                           # location: spin about its centre)
            key_vis(b, [(0, False), (t0, True)])
            rest_z = sz[2] / 2
            tf = (v.z + math.sqrt(v.z ** 2 + 2 * g * (p0.z - rest_z))) / g
            pts = []
            k = 0.0
            while k < tf:
                pts.append((k, p0 + v * k + Vector((0, 0, -0.5 * g * k * k)), spin * k))
                k += 1.0 / FPS
            land = p0 + v * tf + Vector((0, 0, -0.5 * g * tf * tf))
            land.z = rest_z
            bounce = land + Vector((v.x * 0.12, v.y * 0.12, 0))
            pts += [(tf, land, spin * tf), (tf + 0.12, (land + bounce) / 2 + Vector((0, 0, 0.05)), spin * (tf + 0.06)),
                    (tf + 0.24, bounce, spin * tf * 1.05), (tf + 0.5, bounce + Vector((v.x * 0.03, 0, 0)), spin * tf * 1.05)]
            for dt, pos, rot in pts:
                b.location = pos
                b.rotation_euler = tuple(rot)
                b.keyframe_insert("location", frame=fr(t0 + dt))
                b.keyframe_insert("rotation_euler", frame=fr(t0 + dt))
        # plaster dust puff: pale spheres that grow and shrink away
        for j in range(8):
            d = put(P.sphere((x + r.uniform(0.1, 0.5), hy + r.uniform(-0.4, 0.4), r.uniform(hz0, hz1)), 0.2,
                             M_["rubble"], name + " dust"))
            key_vis(d, [(0, False), (plug_until, True), (plug_until + 1.6, False)])
            for dt, sc_ in ((0.0, 0.1), (0.4, 0.75), (1.2, 0.0)):
                d.scale = (sc_,) * 3
                d.keyframe_insert("scale", frame=fr(plug_until + dt))
    return parts


def fcurves_of(owner):
    ad = owner.animation_data
    if not ad or not ad.action:
        return []
    act = ad.action
    if hasattr(act, "fcurves") and len(act.fcurves):
        return list(act.fcurves)
    out = []
    for layer in getattr(act, "layers", []):
        for strip in layer.strips:
            for cb in getattr(strip, "channelbags", []):
                out += list(cb.fcurves)
    return out


def key_vis(o, pts):
    """pts: [(seconds, visible)] constant keys on hide_render/hide_viewport."""
    for t, v in pts:
        f = max(1, fr(t)) if t > 0 else 1
        o.hide_render = not v
        o.hide_viewport = False
        o.keyframe_insert("hide_render", frame=f)
    for fc in fcurves_of(o):
        if fc.data_path == "hide_render":
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
box((3.6, -WT / 2, 0.375), (1.4, WT, 0.75), "wallA", "A front")
box((3.6, -WT / 2, 2.4), (1.4, WT, 0.6), "wallA", "A front")
box((4.65, -WT / 2, H / 2), (0.7, WT, H), "wallA", "A front")
for x0, x1 in ((0.75, 1.65),):
    for s in (x0 - 0.04, x1 + 0.04):
        box((s, -0.01, 1.05), (0.08, WT + 0.04, 2.1), "frame", "Door frame")
    box(((x0 + x1) / 2, -0.01, 2.13), (x1 - x0 + 0.16, WT + 0.04, 0.08), "frame", "Door frame")
steel_plate((1.2, -0.12, 1.05), (0.9, 2.1), "y", "Door steel")
box((3.6, 0.03, 1.425), (0.04, 0.04, 1.35), "frame", "Window bar")
steel_plate((3.6, -0.12, 1.425), (1.4, 1.35), "y", "Window steel")
# door leaf (hinge at x=0.75, swings into the room)
KNOB_Z = 0.86
hinge = P.empty("A door hinge", (0.75, 0.0, 0))
leaf = box((1.2, 0.0, 1.03), (0.88, 0.05, 2.05), "door", "A door")
knob = put(P.sphere((1.55, 0.06, KNOB_Z), 0.035, M_["metal"], "A door knob"))
for o in (leaf, knob):
    o.parent = hinge
    o.matrix_parent_inverse = hinge.matrix_world.inverted()
# other walls of A: left (x=0) solid with a steel-covered balcony door
box((-WT / 2, D / 2, H / 2), (WT, D, H), "wallA", "A left")
steel_plate((0.12, 2.6, 1.05), (0.85, 2.1), "x", "Balcony steel")
box((0.04, 2.6, 2.13), (0.06, 1.0, 0.08), "frame", "Balcony frame")
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
# my hoodie hangs open: a dark t-shirt under it (seen when I look down)
cast.CAST["me"] = dict(cast.CAST["me"], clothes=dict(cast.CAST["me"]["clothes"], **{"toigo_basic_tucked_t-shirt": (0.22, 0.22, 0.25)}))
KEYS = ["mom", "kazemi", "arian", "mahsa", "rezaei", "kian", "me"]
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
skin, clothes = T.SKIN[CH["kazemi"].name]
clothes = dict(clothes)
for kk in list(clothes):
    if "casualsuit" in kk:
        clothes[kk] = (0.24, 0.26, 0.3)
T.SKIN[CH["kazemi"].name] = (skin, clothes)
CLIP = {}


def clip(name):
    if name not in CLIP:
        CLIP[name] = mocap.load(os.path.join(MOC, name + ".fbx"))
    return CLIP[name]


CUTS = {0.0}                  # POV film: one continuous look through my eyes, nobody jumps
LASTSEG = {}
HOLES = [(5.08, 2.2), (10.24, 2.0)]          # (wall x, hole centre y)


def face(p, q):
    """facing (degrees, 0 = +Y, 90 = -X) from p towards q."""
    return math.degrees(math.atan2(-(q[0] - p[0]), q[1] - p[1]))


def walk_path(p0, p1):
    """Straight line from p0 to p1, routed through the hole of every wall it crosses."""
    pts = [Vector((p0[0], p0[1]))]
    s = 1 if p1[0] > p0[0] else -1
    for wx, hy in sorted(HOLES, key=lambda h: s * h[0]):
        if (p0[0] - wx) * (p1[0] - wx) < 0:
            pts += [Vector((wx - s * 0.45, hy)), Vector((wx + s * 0.45, hy))]
    pts.append(Vector((p1[0], p1[1])))
    return pts


def bump(x, y):
    """Lift the body a little while stepping over the bottom of a hole."""
    for wx, hy in HOLES:
        d = abs(x - wx)
        if d < 0.35 and abs(y - hy) < 0.6:
            return 0.1 * (1 + math.cos(math.pi * d / 0.35)) / 2
    return 0.0


def walk(who, t0, t1, pts, f_from, f_to):
    """Walk along pts (walking cycle in place, the rig carried along the path), turning from f_from at the start
    and into f_to at the end."""
    lens = [(b - a).length for a, b in zip(pts, pts[1:])]
    L = max(1e-3, sum(lens))
    dur = t1 - t0
    n = fr(t1) - fr(t0)

    def at(s):
        s = max(0.0, min(L, s))
        for (a, b), l in zip(zip(pts, pts[1:]), lens):
            if s <= l or l == lens[-1]:
                return a.lerp(b, s / max(l, 1e-6)) if l > 0 else a
            s -= l
        return pts[-1]

    def place(j):
        u = min(1.0, j / max(1, n - 1))
        uu = u * u * (3 - 2 * u) * 0.35 + u * 0.65            # soft start and stop
        p = at(uu * L)
        q = at(uu * L + 0.35)
        if (q - p).length < 1e-3:
            q = p + (pts[-1] - pts[-2])
        fw = face(p, q)
        t = j / FPS
        k0, k1 = seg(t, 0.0, 0.45), seg(t, dur - 0.45, dur)

        def mix(a, b, k):
            d = (b - a + 180) % 360 - 180
            return a + d * k
        fac = mix(mix(f_from, fw, k0), f_to, k1)
        return (p.x, p.y, bump(p.x, p.y)), fac
    v = L / dur
    mocap.apply(CH[who], clip("walking"), start=fr(t0), length=n, in_place=True, loop=True,
                speed=max(0.6, min(1.4, v / 1.3)), place=place, blend=8)
    LASTSEG[who] = t1


def act(who, name, t0, t1, pos, facing, follow=None, turn=0.0, **kw):
    """Character `who` plays clip `name` from t0 to t1 (seconds) at pos/facing.
    When the segment follows on from the previous one the body eases out of the previous pose and the hips
    continue from where they were (no jump); if the new place is further away, the character first walks there
    (through the holes in the walls). turn: seconds to turn from the old facing."""
    rig = CH[who].rig
    in_shot = t0 not in CUTS and LASTSEG.get(who) == t0
    if follow is None:
        follow = in_shot
    if in_shot and not turn:
        turn = 0.5
    hips_prev = None
    if follow and in_shot:
        sc.frame_set(fr(t0) - 1)
        hips_prev = (rig.matrix_world @ rig.pose.bones["pelvis"].matrix).translation.copy()
        old_rz = rig.rotation_euler[2]
        dist = (Vector((pos[0], pos[1])) - hips_prev.xy).length
        if dist > 0.35:
            pts = walk_path(hips_prev.xy, pos)
            L = sum((b - a).length for a, b in zip(pts, pts[1:]))
            tw = min(max(0.7, L / 1.25), 0.75 * (t1 - t0))
            walk(who, t0, t0 + tw, pts, math.degrees(old_rz - math.pi), facing)
            return act(who, name, t0 + tw, t1, pos, facing, turn=0.3, **kw)
    n = fr(t1) - fr(t0)
    mocap.apply(CH[who], clip(name), start=fr(t0), length=n, offset=pos, facing=facing,
                blend=8 if in_shot else 0, **kw)
    if hips_prev is not None:
        sc.frame_set(fr(t0))
        now = (rig.matrix_world @ rig.pose.bones["pelvis"].matrix).translation
        pos = (pos[0] + hips_prev.x - now.x, pos[1] + hips_prev.y - now.y, pos[2])
        rig.location = pos
        rig.keyframe_insert("location", frame=fr(t0))
    rig.location = pos                       # hold the place until the last frame (then jump at the cut)
    rig.rotation_euler = (0, 0, math.radians(facing) + math.pi)
    rig.keyframe_insert("location", frame=fr(t1) - 1)
    rig.keyframe_insert("rotation_euler", index=2, frame=fr(t1) - 1)
    if turn and hips_prev is not None:
        rig.rotation_euler = (0, 0, old_rz)
        rig.keyframe_insert("rotation_euler", index=2, frame=fr(t0))
        rig.rotation_euler = (0, 0, math.radians(facing) + math.pi)
        rig.keyframe_insert("rotation_euler", index=2, frame=fr(t0 + turn))
    LASTSEG[who] = t1


# a character holds his place for the whole segment and jumps (at the cut) to the next one
for _ch in CH.values():
    fcs = [fc for fc in fcurves_of(_ch.rig) if fc.data_path in ("location", "rotation_euler")]
    print("PLACE KEYS", _ch.name, len(fcs))
    for fc in fcs:
        for kp in fc.keyframe_points:
            kp.interpolation = "CONSTANT"

# who is in which set (hidden otherwise, saves render time)
PRESENT = {
    "mom": [(0, 75.5)], "kazemi": [(0, 75.5)], "arian": [(24.5, 75.5)], "mahsa": [(24.5, 75.5)],
    "rezaei": [(41.0, 75.5)], "kian": [(62.0, 75.5)], "me": [(0, 75.5)],
}
# ---- mom
GRAB, PULL = 2.0, 2.9                    # hand on the knob / door let go
act("mom", "opening_door_inwards", 0.0, GRAB, (1.80, 1.05, 0), 180, src_from=0.8, speed=1.15)
act("mom", "opening_door_inwards", GRAB, PULL, (1.80, 1.05, 0), 180, src_from=3.1, speed=-1.1, follow=False)
act("mom", "nervously_look_around", PULL, 7.4, (1.8, 1.3, 0), 180)
act("mom", "breathing_idle", 7.4, 10.0, (1.6, 1.45, 0), 200, src_from=1.0)
act("mom", "punching_bag", 10.0, 12.4, (1.0, 0.62, 0), 180)
act("mom", "opening_a_filing_cabinet", 12.4, 16.4, (1.2, 3.45, 0), 0, src_from=1.4, speed=0.7)
act("mom", "pushing", 16.4, 19.0, (1.2, 3.45, 0), 180, src_from=2.0, speed=0.75)
act("mom", "breathing_idle", 19.0, 27.4, (2.9, 3.0, 0), -60)
act("mom", "nervously_look_around", 27.4, 33.5, (6.0, 3.4, 0), -70)
act("mom", "breathing_idle", 33.5, 45.0, (8.6, 3.0, 0), -100)
act("mom", "nervously_look_around", 45.0, 51.0, (11.6, 3.5, 0), -60)
act("mom", "breathing_idle", 51.0, 59.4, (11.0, 2.6, 0), 10)
act("mom", "nervously_look_around", 59.4, 75.5, (11.0, 2.6, 0), -55, loop=True)
# ---- Kazemi
act("kazemi", "breathing_idle", 0.0, 5.0, (3.9, 1.6, 0), 200)
act("kazemi", "nervously_look_around", 5.0, 7.4, (3.75, 0.8, 0), 180, src_from=0.5)
act("kazemi", "cross_punch", 7.4, 9.6, (3.6, 0.72, 0), 180)
act("kazemi", "nervously_look_around", 9.6, 12.4, (3.6, 0.95, 0), 190)
act("kazemi", "punching_bag", 12.4, 13.9, (4.45, 2.2, 0), -90)
act("kazemi", "thinking", 13.9, 19.0, (4.3, 2.0, 0), -110)
act("kazemi", "double_dagger_stab", 19.0, 22.1, (4.45, 2.2, 0), -90)
act("kazemi", "double_dagger_stab", 22.1, 24.5, (4.45, 2.2, 0), -90, src_from=0.4)
act("kazemi", "jump", 24.5, 27.0, (4.35, 2.2, 0), -90)
act("kazemi", "breathing_idle", 27.0, 33.5, (8.6, 3.3, 0), -60)
act("kazemi", "double_dagger_stab", 33.5, 36.6, (9.6, 2.0, 0), -90)
act("kazemi", "double_dagger_stab", 36.6, 41.0, (9.6, 2.0, 0), -90, src_from=0.4, speed=0.85)
act("kazemi", "breathing_idle", 41.0, 51.0, (11.7, 2.8, 0), -70)
act("kazemi", "breathing_idle", 51.0, 59.4, (10.6, 3.4, 0), 5, src_from=3.0)
act("kazemi", "nervously_look_around", 59.4, 75.5, (10.6, 3.4, 0), -60, src_from=1.0, loop=True)
# ---- Arian and Mahsa under the table
act("arian", "pushing", 24.5, 27.0, (7.3, 1.9, 0), 180, speed=0.05)
act("arian", "pushing", 27.0, 29.5, (7.3, 1.75, 0), 180, src_from=0.2, speed=1.0)
act("arian", "nervously_look_around", 29.5, 33.5, (7.3, 1.6, 0), 160)
act("arian", "nervously_look_around", 33.5, 44.0, (8.9, 3.3, 0), -70, src_from=2.0)
act("arian", "breathing_idle", 44.0, 51.0, (11.1, 3.0, 0), -70)
act("arian", "breathing_idle", 51.0, 59.4, (10.7, 2.0, 0), 0, src_from=4.0)
act("arian", "terrified", 59.4, 75.5, (10.7, 2.0, 0), -50, src_from=1.0)
act("mahsa", "pushing", 24.5, 33.5, (7.9, 2.45, 0), 200, speed=0.04)
act("mahsa", "nervously_look_around", 33.5, 44.5, (8.1, 2.7, 0), -80)
act("mahsa", "nervously_look_around", 44.5, 51.0, (10.7, 3.6, 0), -60, src_from=3.0)
act("mahsa", "breathing_idle", 51.0, 59.4, (11.0, 3.5, 0), 0, src_from=6.0)
act("mahsa", "nervously_look_around", 59.4, 75.5, (11.0, 3.5, 0), -50, loop=True)
# ---- Rezaei on the bed
act("rezaei", "sitting_idle", 41.0, 75.5, (13.0, 3.0, 0.02), 180, loop=True)
# ---- Kian behind the far wall (only his face shows through the hole)
act("kian", "breathing_idle", 62.0, 75.5, (15.75, 1.5, 0), 90, loop=True)
# ---- me (the camera is my eyes; the head is hidden, the hands and feet show when I use them or look down)
DOOR, WIN = (1.2, 0.0), (3.6, 0.0)
ME = [
    ("breathing_idle", 0.0, 5.0, (2.35, 2.05), face((2.35, 2.05), DOOR), {}),
    ("nervously_look_around", 5.0, 7.4, (2.35, 2.05), face((2.35, 2.05), WIN), {}),
    ("breathing_idle", 7.4, 10.0, (2.35, 2.05), face((2.35, 2.05), (1.6, 1.45)), {}),
    ("punching_bag", 10.0, 12.4, (1.45, 0.62), 180, {}),                         # fists on the steel door
    ("nervously_look_around", 12.4, 16.4, (2.5, 1.25), face((2.5, 1.25), (4.45, 2.2)), {}),
    ("breathing_idle", 16.4, 19.0, (2.5, 1.25), face((2.5, 1.25), (1.2, 3.45)), {}),
    ("breathing_idle", 19.0, 25.3, (3.3, 1.3), face((3.3, 1.3), (5.08, 2.2)), {}),
    ("nervously_look_around", 25.3, 33.5, (6.1, 1.4), face((6.1, 1.4), (7.5, 2.1)), {}),   # through the hole
    ("breathing_idle", 33.5, 42.0, (7.9, 1.2), face((7.9, 1.2), (10.24, 2.0)), {}),
    ("nervously_look_around", 42.0, 47.0, (11.9, 1.4), face((11.9, 1.4), (13.0, 3.0)), {}),
    ("breathing_idle", 47.0, 51.0, (12.5, 2.1), face((12.5, 2.1), (13.0, 3.0)), {}),
    ("nervously_look_around", 51.0, 58.8, (12.5, 2.1), face((12.5, 2.1), (11.2, 4.3)), {}),
    ("breathing_idle", 58.8, 62.0, (12.2, 1.5), face((12.2, 1.5), (13.0, 3.0)), {}),
    ("breathing_idle", 62.0, 63.2, (12.2, 1.5), -90, {}),
    ("nervously_look_around", 63.2, 66.0, (14.6, 1.5), -90, {}),
    ("hands_forward_gesture", 66.0, 69.1, (14.75, 1.5), -90, {}),               # reaching to the hole
    ("breathing_idle", 69.1, 72.0, (14.75, 1.5), -90, {}),
    ("nervously_look_around", 72.0, 75.5, (14.75, 1.5), face((14.75, 1.5), (13.0, 3.0)), dict(turn=0.8)),
]
for nm, a_, b_, p_, f_, kw_ in ME:
    act("me", nm, a_, b_, (p_[0], p_[1], 0), f_, **kw_)

# the front door follows mom's hand while she pulls it, then swings on by itself
_rig = CH["mom"].rig
HX, HY = 0.75, 0.0


def _hand_angle(f):
    sc.frame_set(f)
    w = (_rig.matrix_world @ _rig.pose.bones["hand_r"].matrix).translation
    return math.atan2(w.y - HY, w.x - HX)


_a0 = _hand_angle(fr(GRAB))
_a = 0.0
for f in range(1, fr(GRAB) + 1):
    hinge.rotation_euler = (0, 0, 0.0)
    hinge.keyframe_insert("rotation_euler", index=2, frame=f) if f in (1, fr(GRAB)) else None
for f in range(fr(GRAB) + 1, fr(PULL) + 1):
    _a = max(_a, _hand_angle(f) - _a0)
    hinge.rotation_euler = (0, 0, _a)
    hinge.keyframe_insert("rotation_euler", index=2, frame=f)
print("DOOR PULLED TO", round(math.degrees(_a), 1))
_rate = _a / (PULL - GRAB)                  # rad/s when she lets go; the swing slows down to 80 degrees
_tf = 2 * (math.radians(80) - _a) / max(_rate, 0.3)
for f in range(fr(PULL) + 1, fr(PULL + _tf) + 2):
    u = min(1.0, ((f - 1) / FPS - PULL) / _tf)
    hinge.rotation_euler = (0, 0, _a + (math.radians(80) - _a) * (1 - (1 - u) ** 2))
    hinge.keyframe_insert("rotation_euler", index=2, frame=f)


def strikes(who, t0, t1, toward_x=True):
    """Moments the sledgehammer hits: local maxima of the right hand's reach towards +X."""
    rig = CH[who].rig
    xs = []
    for f in range(fr(t0), fr(t1)):
        sc.frame_set(f)
        xs.append(((rig.matrix_world @ rig.pose.bones["hand_r"].matrix).translation.x, f))
    hits = []
    lo = min(v for v, _ in xs)
    hi = max(v for v, _ in xs)
    for i in range(2, len(xs) - 2):
        v, f = xs[i]
        if v >= max(x for x, _ in xs[i - 2:i + 3]) and v > lo + 0.6 * (hi - lo):
            if not hits or f - hits[-1] > 8:
                hits.append(f)
    return [(f - 1) / FPS for f in hits]


for _k, _c in (("rubble", (0.8, 0.76, 0.68)), ("brick", (0.62, 0.36, 0.28)), ("dark", (0.05, 0.05, 0.06))):
    M_[_k] = P.mat(_k.capitalize() + " 2", _c, 0.9)       # re-create: building the cast purged unused materials
HITS_AB = strikes("kazemi", 19.0, 24.5)
HITS_BC = strikes("kazemi", 33.5, 41.0)
print("HITS", [round(v, 2) for v in HITS_AB], [round(v, 2) for v in HITS_BC])
import json
os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
json.dump({"ab": HITS_AB, "bc": HITS_BC}, open(os.path.join(HERE, "out", "hits.json"), "w"))
WALL_AB_T = HITS_AB[-1] if HITS_AB else 23.3
WALL_BC_T = HITS_BC[-1] if HITS_BC else 39.6
wall_with_hole(5.08, 2.2, 1.0, 0.25, 1.75, M_["wallA"], "AB wall", plug_until=WALL_AB_T,
               cracks=[(h, 0.5 + 0.5 * i / max(1, len(HITS_AB) - 1)) for i, h in enumerate(HITS_AB[:-1])])
wall_with_hole(10.24, 2.0, 1.0, 0.25, 1.75, M_["wallB"], "BC wall", plug_until=WALL_BC_T,
               cracks=[(h, 0.5 + 0.5 * i / max(1, len(HITS_BC) - 1)) for i, h in enumerate(HITS_BC[:-1])])

# ---- faces (shape keys) and visibility
WORRY = {"mom": [(0, 0.2), (2.6, 1.8), (19, 1.2), (52, 1.6), (59, 2.0)],
         "kazemi": [(0, 0.3), (6.4, 1.4), (13, 0.6), (19, 1.0), (52, 1.5), (59, 1.9)],
         "arian": [(24.5, 2.0), (33, 1.4), (52, 1.6), (59, 2.0)], "mahsa": [(24.5, 2.0), (52, 1.6), (59, 2.0)],
         "rezaei": [(41, 0.0)], "kian": [(62, 2.0)], "me": [(0, 0.5)]}


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


def two_hand_hammer(name, who, spans):
    """Sledgehammer held in both hands: every frame the handle runs from the right hand through the left."""
    rig = CH[who].rig
    o = hammer_mesh(name)
    o.rotation_mode = "QUATERNION"
    d_prev = Vector((1, 0, 0))
    for a_, b_ in spans:
        for f in range(fr(a_), fr(b_) + 1):
            sc.frame_set(f)
            hr = (rig.matrix_world @ rig.pose.bones["hand_r"].matrix).translation
            hl = (rig.matrix_world @ rig.pose.bones["hand_l"].matrix).translation
            d = hl - hr
            if 0.04 < d.length < 0.4:
                d.normalize()
                d_prev = d_prev.lerp(d, 0.7).normalized()
            o.location = hr - d_prev * 0.08
            o.rotation_quaternion = d_prev.to_track_quat("Y", "Z")
            o.keyframe_insert("location", frame=f)
            o.keyframe_insert("rotation_quaternion", frame=f)
    return o, [o]


ham_k, ham_k_parts = two_hand_hammer("Hammer Kazemi", "kazemi", [(19.0, 24.5), (33.5, 41.0)])
show(ham_k_parts, [(19.0, 24.5), (33.5, 41.0)])
ham_m, ham_m_parts = holder("Hammer Mom", "mom", 17.6, both=False)
show(ham_m_parts, [(16.4, 19.0)])
hf = hammer_mesh("Hammer floor")
hf.matrix_world = Matrix.Translation((0.75, 4.2, 0.06)) @ Matrix.Rotation(math.radians(-80), 4, "Z")
floor_h = [hf]
show(floor_h, [(12.4, 16.4)])
# ------------------------------------------------------------------ camera: my eyes (POV), fisheye added in post
me = CH["me"]
mrig = me.rig
hb = mrig.pose.bones["head"]                 # my head is hidden (scaled to nothing): the camera sits there
hb.scale = (0.001, 0.001, 0.001)
hb.keyframe_insert("scale", frame=1)
nb = mrig.pose.bones["neck_01"]
nb.scale = (0.2, 0.2, 0.2)
nb.keyframe_insert("scale", frame=1)
sc.frame_set(fr(49))
_r = CH["rezaei"].rig
_ua = (_r.matrix_world @ _r.pose.bones["upperarm_r"].head).lerp(_r.matrix_world @ _r.pose.bones["lowerarm_r"].head, 0.6)
HANDS = "hands"
# (t, where I look, seconds to turn there)
LOOK = [
    (0.0, (1.7, 0.7, 0.0), 0.0),            # waking up: my feet
    (1.1, (1.2, 0.0, 1.1), 0.9),             # mom at the front door
    (5.0, (3.6, 0.0, 1.4), 0.6),             # Kazemi at the window
    (7.4, (1.55, 1.25, 1.05), 0.6),          # mom's phone: no signal
    (10.0, (1.3, 0.0, 1.15), 0.5),           # the steel door, my fists
    (12.4, (4.6, 2.2, 1.3), 0.7),            # Kazemi knocks on the wall
    (16.4, (1.2, 3.45, 1.0), 0.6),           # mom with the sledgehammer
    (19.0, (5.0, 2.2, 1.1), 0.6),            # the wall breaks
    (25.3, (4.7, 2.2, 0.8), 0.5),
    (26.1, (5.9, 2.2, 0.0), 0.5),            # my feet over the rubble
    (27.6, (7.5, 2.1, 0.45), 0.8),           # Arian and Mahsa under the table
    (33.5, (10.1, 2.0, 1.1), 0.6),           # the next wall
    (42.0, (10.0, 2.0, 0.9), 0.5),
    (43.0, (11.0, 2.0, 0.0), 0.5),           # stepping through
    (44.8, (13.0, 3.0, 1.0), 0.8),           # Rezaei on the bed
    (47.0, tuple(_ua), 0.8),                 # the bite on his arm
    (51.0, (11.2, 4.3, 1.12), 0.7),          # the TV
    (58.8, (13.0, 3.0, 1.15), 0.4),          # everyone turns to Rezaei
    (62.0, (15.4, 1.5, 1.35), 0.5),          # a knock in the far wall
    (66.0, (15.4, 1.5, 1.37), 0.3),          # Kian's face in the hole
    (72.0, (13.0, 3.0, 1.2), 0.8),           # Rezaei looks up
]


def hands_mid(f):
    sc.frame_set(f)
    a = (mrig.matrix_world @ mrig.pose.bones["hand_r"].matrix).translation
    b = (mrig.matrix_world @ mrig.pose.bones["hand_l"].matrix).translation
    return (a + b) / 2


cam = bpy.data.objects.new("Camera", bpy.data.cameras.new("Camera"))
sc.collection.objects.link(cam)
sc.camera = cam
cam.data.clip_start = 0.03
cam.data.lens = 15
cam.data.sensor_width = 36
cam.rotation_mode = "QUATERNION"
import random
_rnd = random.Random(7)
eye_s = None
hand_s = None
d_prev = None
EYE = {}
for f in range(1, N + 1):
    t = (f - 1) / FPS
    sc.frame_set(f)
    hw = mrig.matrix_world @ nb.matrix          # neck base (head and neck are shrunk)
    fwd = Vector((-math.sin(mrig.rotation_euler[2] - math.pi), math.cos(mrig.rotation_euler[2] - math.pi), 0))
    eye = hw.translation + Vector((0, 0, 0.23)) + fwd * 0.13
    eye_s = eye if eye_s is None else eye_s.lerp(eye, 0.45)
    hm = hands_mid(f)
    hand_s = hm if hand_s is None else hand_s.lerp(hm, 0.3)
    sc.frame_set(f)

    def target(k):
        v = LOOK[k][1]
        return hand_s if v == HANDS else Vector(v)
    k = max(i for i, l in enumerate(LOOK) if l[0] <= t)
    d1 = (target(k) - eye_s).normalized()
    if k > 0:
        d0 = (target(k - 1) - eye_s).normalized()
        d = d0.lerp(d1, seg(t, LOOK[k][0], LOOK[k][0] + LOOK[k][2])).normalized()
    else:
        d = d1
    d_prev = d if d_prev is None else d_prev.lerp(d, 0.5).normalized()
    dz = max(d_prev.z, -0.72)                # never steeper than ~46 degrees down (the shrunk neck would show)
    hz = Vector((d_prev.x, d_prev.y, 0)).normalized() * math.sqrt(1 - dz * dz)
    q = Vector((hz.x, hz.y, dz)).to_track_quat("-Z", "Y")
    amp = 0.004
    q.rotate(Matrix.Rotation(amp * _rnd.uniform(-1, 1), 4, "X"))
    cam.location = eye_s
    cam.rotation_quaternion = q
    cam.keyframe_insert("location", frame=f)
    cam.keyframe_insert("rotation_quaternion", frame=f)
    EYE[f] = eye_s.copy()
for owner in (cam,):
    for fc in fcurves_of(owner):
        for kp in fc.keyframe_points:
            kp.interpolation = "LINEAR"
# mom's phone in her right hand 7.4-10
M_["phone"] = P.mat("Phone body", (0.08, 0.08, 0.1), 0.3)
sc.frame_set(fr(8.5))
pm = CH["mom"].rig.matrix_world @ CH["mom"].rig.pose.bones["hand_r"].matrix
ph = put(P.box(pm.translation + pm.to_3x3() @ Vector((0, 0.09, -0.02)), (0.075, 0.15, 0.01), M_["phone"], "Mom phone"))
ph.rotation_euler = pm.to_euler()
con = ph.constraints.new("CHILD_OF")
con.target, con.subtarget = CH["mom"].rig, "hand_r"
con.inverse_matrix = pm.inverted()
show([ph], [(7.4, 10.0)])

# ------------------------------------------------------------------ look
sc.frame_set(1)
T.SAT = 0.6                                # fewer, quieter colours (the user asked)
T.toonify(sc, samples=int(os.environ.get("SAMPLES", "8")))
inked = [o for o in bpy.data.objects if o.type == "MESH" and not any(
    k in o.name.lower() for k in ("high-poly", "lash", "brow", "teeth", "tongue", "rivet", "crack", "screen", "glass", "dust",
                                  "floor", "ceiling"))]
me_objs = {o for o in bpy.data.objects if o.type == "MESH" and o.parent == CH["me"].rig}
me_objs.add(CH["me"].body)
T.ink([o for o in inked if o not in me_objs], 0.005)
T.ink([o for o in inked if o in me_objs], 0.0015)
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
