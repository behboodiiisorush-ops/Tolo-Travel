"""«دیوار ۲» (wagon style, «واگن آخر» puppets) — the next episode of «دیوار». Same three flats, both walls already
broken open. It starts where episode 1 ended: Rezaei on the bed in flat C, Kian's face in the hole of the far wall.

    ../cast/bpy.sh scene.py --still 40,120,...      -> test/s_XXXX.png
    ../cast/bpy.sh scene.py --save                  -> wall2.blend (render.py renders from it)
Shots (seconds):
  1   0.0- 4.2  Kian whispers through the hole behind me: back away, don't look into his eyes
  2   4.2- 8.8  Rezaei on the bed: "why are you afraid? I'm only... hungry"
  3   8.8-11.6  he screams and gets up; mom: "kids! go back!"
  4  11.6-19.2  everyone runs back through both holes into flat A; Rezaei lurches after us
  5  19.2-24.6  Kazemi: "the sofa! help me!" — we push the sofa against the hole
  6  24.6-34.0  Rezaei beats on the sofa from the other side, his head above it; the light flickers
  7  34.0-39.4  he gives up and lurches away into the dark; silence
  8  39.4-49.6  Arian's phone: signal! a message: the doors open at 6 am, only if nobody is infected
  9  49.6-54.0  mom, relieved: "not long now... we're all fine"
 10  54.0-58.4  Mahsa: "your hand... why is it bleeding?" — a red scratch on the back of my hand
 11  58.4-64.5  me: "it's... from the wall. I think." Everyone stares at me.
"""
import bpy, sys, os, math, random
from mathutils import Vector, Matrix
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "cast"))
sys.path.insert(0, os.path.join(HERE, "..", "studio"))
sys.path.insert(0, os.path.join(HERE, "..", "puppets"))
bpy.ops.wm.read_factory_settings(use_empty=True)
import cast, mocap, anim  # noqa: E402,F401
import props as P         # noqa: E402
import toon_look as T     # noqa: E402,F401
import puppets as PP      # noqa: E402
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


# ------------------------------------------------------------------ set: three flats along +X (as in episode 1)
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
    sofa=P.mat("Sofa", (0.4, 0.42, 0.45), 0.9), wood=P.mat("Wood", (0.42, 0.36, 0.3), 0.6),
    counter=P.mat("Counter", (0.9, 0.9, 0.88), 0.4), cab=P.mat("Cabinet", (0.55, 0.56, 0.54), 0.6),
    metal=P.mat("Metal", (0.7, 0.72, 0.74), 0.3, metal=0.8), bed=P.mat("Bed sheet", (0.85, 0.85, 0.8), 0.9),
    blanket=P.mat("Blanket", (0.45, 0.42, 0.44), 0.9), rubble=P.mat("Rubble", (0.8, 0.76, 0.68), 0.95),
    brick=P.mat("Brick", (0.62, 0.36, 0.28), 0.9), dark=P.mat("Dark", (0.05, 0.05, 0.06), 0.9),
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


def wall_with_hole(x, hy, hw, hz0, hz1, m, name):
    """Wall across X at x (y 0..D) with an open hole."""
    parts = [box((x, (hy - hw / 2) / 2, H / 2), (WT, hy - hw / 2, H), m, name),
             box((x, (hy + hw / 2 + D) / 2, H / 2), (WT, D - hy - hw / 2, H), m, name),
             box((x, hy, (hz1 + H) / 2), (WT, hw, H - hz1), m, name)]
    if hz0 > 0:
        parts.append(box((x, hy, hz0 / 2), (WT, hw, hz0), m, name))
    return parts


def rubble(x, hy, seed):
    """Bricks and plaster lying on the floor on both sides of a broken wall (left from episode 1)."""
    r = random.Random(seed)
    for j in range(26):
        side = 1 if j % 3 else -1
        sz = (r.uniform(0.07, 0.2), r.uniform(0.06, 0.12), r.uniform(0.05, 0.1))
        p = (x + side * r.uniform(0.25, 1.6), hy + r.uniform(-0.9, 0.9), sz[2] / 2)
        b = box(p, sz, "rubble" if j % 3 else "brick", "Rubble")
        b.data.transform(Matrix.Translation(-Vector(p)))
        b.location = p
        b.rotation_euler = (0, 0, r.uniform(0, 3.1))


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
    box(loc, (sx, 0.05, 0.015) if axis == "y" else (0.05, sx, 0.015), "rivet", name + " seam")
    return p


for u, wm, fm in (("A", "wallA", "floor"), ("B", "wallB", "tileB"), ("C", "wallC", "floor")):
    room(u, wm, fm)
# front wall of A (y=0) with the door at x 0.75..1.65 and the window at x 2.9..4.3 (both steel behind)
box((0.375, -WT / 2, H / 2), (0.75, WT, H), "wallA", "A front")
box((1.2, -WT / 2, 2.4), (0.9, WT, 0.6), "wallA", "A front")
box((2.275, -WT / 2, H / 2), (1.25, WT, H), "wallA", "A front")
box((3.6, -WT / 2, 0.375), (1.4, WT, 0.75), "wallA", "A front")
box((3.6, -WT / 2, 2.4), (1.4, WT, 0.6), "wallA", "A front")
box((4.65, -WT / 2, H / 2), (0.7, WT, H), "wallA", "A front")
for s in (0.71, 1.69):
    box((s, -0.01, 1.05), (0.08, WT + 0.04, 2.1), "frame", "Door frame")
box((1.2, -0.01, 2.13), (1.06, WT + 0.04, 0.08), "frame", "Door frame")
steel_plate((1.2, -0.12, 1.05), (0.9, 2.1), "y", "Door steel")
box((3.6, 0.03, 1.425), (0.04, 0.04, 1.35), "frame", "Window bar")
steel_plate((3.6, -0.12, 1.425), (1.4, 1.35), "y", "Window steel")
# the front door stands open (mom opened it in episode 1)
hinge = P.empty("A door hinge", (0.75, 0.0, 0))
leaf = box((1.2, 0.0, 1.03), (0.88, 0.05, 2.05), "door", "A door")
knob = put(P.sphere((1.55, 0.06, 0.86), 0.035, M_["metal"], "A door knob"))
for o in (leaf, knob):
    o.parent = hinge
    o.matrix_parent_inverse = hinge.matrix_world.inverted()
hinge.rotation_euler = (0, 0, math.radians(80))
box((-WT / 2, D / 2, H / 2), (WT, D, H), "wallA", "A left")
steel_plate((0.12, 2.6, 1.05), (0.85, 2.1), "x", "Balcony steel")
box((0.04, 2.6, 2.13), (0.06, 1.0, 0.08), "frame", "Balcony frame")
# far wall of C with the small hole where Kian looks through, and a dark niche behind it (open at the hole side)
wall_with_hole(15.4, 1.5, 0.42, 1.12, 1.6, M_["wallC"], "C far wall")
box((16.28, 1.5, 1.35), (0.08, 1.4, 1.4), "dark", "Behind hole back")
box((15.95, 0.82, 1.35), (0.72, 0.056, 1.4), "dark", "Behind hole side a")
box((15.95, 2.18, 1.35), (0.72, 0.056, 1.4), "dark", "Behind hole side b")
box((15.95, 1.5, 2.03), (0.72, 1.4, 0.056), "dark", "Behind hole top")
# the two broken walls
wall_with_hole(5.08, 2.2, 1.0, 0.25, 1.75, M_["wallA"], "AB wall")
wall_with_hole(10.24, 2.0, 1.0, 0.25, 1.75, M_["wallB"], "BC wall")
rubble(5.08, 2.2, 51)
rubble(10.24, 2.0, 102)
for u, wm in (("B", "wallB"), ("C", "wallC")):
    x0, x1 = UNITS[u]
    cx = (x0 + x1) / 2
    box((cx, -WT / 2, H / 2), (x1 - x0, WT, H), wm, f"{u} front")
    steel_plate((cx, 0.1, 1.5), (1.3, 1.1), "y", f"{u} window steel")
# furniture A: the sofa (moves: pushed against the hole), coffee table pushed aside, sink counter
sofa_pivot = P.empty("Sofa pivot", (3.4, 3.95, 0))
for o in (box((3.4, 3.95, 0.25), (2.0, 0.85, 0.5), "sofa", "Sofa"),
          box((3.4, 4.3, 0.65), (2.0, 0.2, 0.8), "sofa", "Sofa back"),
          box((2.45, 3.95, 0.4), (0.12, 0.85, 0.3), "sofa", "Sofa arm"),
          box((4.35, 3.95, 0.4), (0.12, 0.85, 0.3), "sofa", "Sofa arm")):
    o.parent = sofa_pivot
    o.matrix_parent_inverse = sofa_pivot.matrix_world.inverted()
box((2.3, 3.2, 0.22), (1.0, 0.55, 0.44), "wood", "Coffee table")
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
# B kitchen
box((7.6, 2.4, 0.74), (1.5, 0.95, 0.05), "wood", "Kitchen table")
for dx in (-0.68, 0.68):
    for dy in (-0.4, 0.4):
        box((7.6 + dx, 2.4 + dy, 0.36), (0.05, 0.05, 0.72), "wood", "Table leg")
box((9.0, 4.2, 0.45), (2.0, 0.6, 0.9), "cab", "B counter")
box((9.0, 4.2, 0.92), (2.1, 0.66, 0.05), "counter", "B counter top")
box((5.7, 4.15, 0.9), (0.7, 0.65, 1.8), "fridge", "Fridge")
lamp_B = P.area_light((7.6, 2.2, 2.55), (7.6, 2.2, 0), 15, 3.0, (0.75, 0.85, 1.0), name="B lamp")
# C bedroom: bed, dresser with the TV (still showing the news), bedside lamp
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
put(P.plane((11.2, 4.29, 1.12), (0.8, 0.46), tvm, rot=(math.radians(90), 0, 0), name="TV screen"))
lamp_C = P.area_light((13.0, 2.2, 2.55), (13.0, 2.2, 0), 15, 3.0, (1.0, 0.8, 0.6), name="C lamp")
P.area_light((11.2, 3.9, 1.2), (11.8, 2.4, 1.2), 30, 0.8, (0.6, 0.7, 1.0), name="TV glow")
# the lamp in A flickers while Rezaei beats on the sofa (28-31 s)
for k, t in enumerate([0, 28.0, 28.2, 28.45, 28.6, 29.3, 29.5, 30.4, 30.55, 31.0]):
    lamp_A.data.energy = 25 if k % 2 == 0 else 2
    sun.data.energy = 2.6 if k % 2 == 0 else 1.2
    sun.data.keyframe_insert("energy", frame=fr(t))
    lamp_A.data.keyframe_insert("energy", frame=fr(t))
w = bpy.data.worlds.new("W")
sc.world = w
w.color = (0.08, 0.08, 0.1)

# ------------------------------------------------------------------ cast
PP.CAST["me"]["clothes"]["toigo_basic_tucked_t-shirt"] = (0.95, 0.95, 0.92)
KEYS = ["mom", "kazemi", "arian", "mahsa", "rezaei", "kian", "me"]
CH = {}
for k in KEYS:
    ch = PP.spawn(k)
    ch.zombie = 0.0
    CH[k] = ch
import characters as _C  # noqa: E402


def mark(who, b0, b1, frac, off, scale, name, rgb=(0.75, 0.05, 0.08)):
    """A small red mark bound to a bone of `who` (a bite, a scratch)."""
    r = CH[who].rig
    p = (r.matrix_world @ r.data.bones[b0].head_local).lerp(r.matrix_world @ r.data.bones[b1].head_local, frac)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1, segments=16, ring_count=8, location=p + Vector(off))
    o = bpy.context.object
    o.name = name
    o.scale = scale
    o.data.materials.append(PP.toon_mat(name, rgb, 0.3))
    _C._sel([o], o)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    _C._bind(o, r, b0)
    CH[who].objects.append(o)
    return o


mark("rezaei", "upperarm_r", "lowerarm_r", 0.6, (0, -0.035, 0), (0.035, 0.012, 0.025), "Rezaei bite")
# the scratch on the back of my right hand: two thin red streaks
_scr = [mark("me", "hand_r", "middle_01_r", 0.45 + 0.18 * i, (0, 0, 0.022 - 0.004 * i), (0.032, 0.006, 0.004),
             f"My scratch {i}") for i in range(2)]
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


def walk(who, t0, t1, pts, f_from, f_to, wclip="walking", face_fixed=None):
    """Walk along pts (a cycle in place, the rig carried along the path), turning from f_from at the start
    and into f_to at the end (face_fixed: keep that facing all the way, e.g. while pushing)."""
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
        fw = face(p, q) if face_fixed is None else face_fixed
        t = j / FPS
        k0, k1 = seg(t, 0.0, 0.45), seg(t, dur - 0.45, dur)

        def mix(a, b, k):
            d = (b - a + 180) % 360 - 180
            return a + d * k
        fac = mix(mix(f_from, fw, k0), f_to, k1)
        return (p.x, p.y, bump(p.x, p.y)), fac
    v = L / dur
    base = 1.3 if wclip == "walking" else 0.9
    mocap.apply(CH[who], clip(wclip), start=fr(t0), length=n, in_place=True, loop=True,
                speed=max(0.6, min(1.45, v / base)), place=place, blend=8)
    LASTSEG[who] = t1


def act(who, name, t0, t1, pos, facing, follow=None, turn=0.0, wclip="walking", tw=None, face_fixed=None, **kw):
    """Character `who` plays clip `name` from t0 to t1 (seconds) at pos/facing. If the new place is further
    away than 0.35 m, the character first walks there (through the holes), in `tw` seconds if given."""
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
            tw_ = tw if tw else min(max(0.7, L / 1.25), 0.75 * (t1 - t0))
            walk(who, t0, t0 + tw_, pts, math.degrees(old_rz - math.pi), facing, wclip=wclip, face_fixed=face_fixed)
            return act(who, name, t0 + tw_, t1, pos, facing, turn=0.3, **kw)
    n = fr(t1) - fr(t0)
    mocap.apply(CH[who], clip(name), start=fr(t0), length=n, offset=pos, facing=facing,
                blend=8 if in_shot else 0, **kw)
    if hips_prev is not None:
        sc.frame_set(fr(t0))
        now = (rig.matrix_world @ rig.pose.bones["pelvis"].matrix).translation
        pos = (pos[0] + hips_prev.x - now.x, pos[1] + hips_prev.y - now.y, pos[2])
        rig.location = pos
        rig.keyframe_insert("location", frame=fr(t0))
    rig.location = pos
    rig.rotation_euler = (0, 0, math.radians(facing) + math.pi)
    rig.keyframe_insert("location", frame=fr(t1) - 1)
    rig.keyframe_insert("rotation_euler", index=2, frame=fr(t1) - 1)
    if turn and hips_prev is not None:
        rig.rotation_euler = (0, 0, old_rz)
        rig.keyframe_insert("rotation_euler", index=2, frame=fr(t0))
        rig.rotation_euler = (0, 0, math.radians(facing) + math.pi)
        rig.keyframe_insert("rotation_euler", index=2, frame=fr(t0 + turn))
    LASTSEG[who] = t1


# where everybody ends up in flat A
P_MOM, P_KAZ, P_ARI, P_MAH, P_ME = (1.3, 2.8), (3.35, 3.0), (1.55, 1.35), (2.95, 1.1), (2.2, 1.95)
P_PH = (2.35, 1.85)           # where I stand to read Arian's phone
REZ_AT = (5.72, 2.2)          # Rezaei behind the sofa, in B, at the hole
PRESENT = {
    "mom": [(0, END)], "kazemi": [(0, END)], "arian": [(0, END)], "mahsa": [(0, END)],
    "rezaei": [(0, 38.6)], "kian": [(0, 6.0)], "me": [(0, END)],
}
ME_START = (14.75, 1.5)
# ---- mom
act("mom", "nervously_look_around", 0.0, 9.3, (11.0, 2.6, 0), face((11.0, 2.6), (13.0, 3.0)))
act("mom", "hands_forward_gesture", 9.3, 11.2, (11.0, 2.4, 0), face((11.0, 2.4), (10.7, 2.0)))
act("mom", "terrified", 11.2, 39.4, (1.0, 3.25, 0), -100, src_from=4.0, loop=True)
act("mom", "breathing_idle", 39.4, 49.8, (1.15, 2.7, 0), face((1.15, 2.7), P_ARI))
act("mom", "thinking", 49.8, 54.0, (P_MOM[0], P_MOM[1], 0), face(P_MOM, P_ME))
act("mom", "nervously_look_around", 54.0, END, (P_MOM[0], P_MOM[1], 0), face(P_MOM, P_ME), loop=True)
# ---- Kazemi
act("kazemi", "nervously_look_around", 0.0, 11.5, (10.6, 3.4, 0), -60, loop=True)
act("kazemi", "breathing_idle", 11.5, 20.8, (2.2, 3.95, 0), -90)
act("kazemi", "pushing_2", 20.8, 34.0, (4.15, 3.55, 0), -125, wclip="pistol_walk", tw=3.7, face_fixed=-90,
    src_from=1.0, speed=0.2, loop=True)
act("kazemi", "breathing_idle", 34.0, 54.0, (P_KAZ[0], P_KAZ[1], 0), face(P_KAZ, P_ARI))
act("kazemi", "nervously_look_around", 54.0, END, (P_KAZ[0], P_KAZ[1], 0), face(P_KAZ, P_ME), loop=True)
# ---- Arian (with the phone from 39.4)
act("arian", "terrified", 0.0, 10.8, (10.7, 2.0, 0), -50, src_from=6.0, loop=True)
act("arian", "terrified", 10.8, 39.4, (1.5, 1.4, 0), -80, src_from=2.0, loop=True)
act("arian", "reloading", 39.4, 49.6, (P_ARI[0], P_ARI[1], 0), face(P_ARI, P_ME), src_from=0.3, speed=0.35, loop=True, in_place=True)
act("arian", "nervously_look_around", 49.6, END, (P_ARI[0], P_ARI[1], 0), face(P_ARI, P_ME), loop=True)
# ---- Mahsa
act("mahsa", "nervously_look_around", 0.0, 10.8, (11.0, 3.5, 0), -50, loop=True)
act("mahsa", "terrified", 10.8, 37.6, (0.75, 2.2, 0), -90, loop=True)
act("mahsa", "breathing_idle", 37.6, 54.0, (P_MAH[0], P_MAH[1], 0), face(P_MAH, P_ARI))
act("mahsa", "hands_forward_gesture", 54.0, 57.6, (P_MAH[0], P_MAH[1], 0), face(P_MAH, P_ME), speed=0.9)
act("mahsa", "terrified", 57.6, END, (P_MAH[0], P_MAH[1], 0), face(P_MAH, P_ME))
# ---- Rezaei: on the bed, screams, gets up, follows us, beats on the sofa, gives up
act("rezaei", "sitting_idle", 0.0, 8.8, (13.0, 3.0, 0.02), 180, loop=True)
act("rezaei", "zombie_scream", 8.8, 11.6, (13.0, 2.55, 0), face((13.0, 2.55), ME_START), follow=False)
act("rezaei", "zombie_idle", 11.6, 13.0, (13.0, 2.55, 0), face((13.0, 2.55), (10.24, 2.0)), loop=True)
act("rezaei", "zombie_attack", 13.0, 34.0, (REZ_AT[0], REZ_AT[1], 0), 90, wclip="zombie_walk", tw=11.4, loop=True)
act("rezaei", "zombie_idle", 34.0, 38.6, (8.9, 3.3, 0), 60, wclip="zombie_walk", tw=4.0, loop=True)
# ---- Kian behind the far wall (only his face in the hole)
act("kian", "breathing_idle", 0.0, 6.0, (15.75, 1.5, 0), 90, loop=True)
# ---- me (the camera is my eyes)
ME = [
    ("breathing_idle", 0.0, 1.0, ME_START, face(ME_START, (13.0, 3.0)), {}),
    ("nervously_look_around", 1.0, 4.2, ME_START, -95, dict(turn=0.8)),                  # Kian behind me
    ("nervously_look_around", 4.2, 11.2, (14.55, 1.35), face((14.55, 1.35), (13.0, 2.8)), {}),
    ("breathing_idle", 11.2, 20.6, (3.0, 3.05), face((3.0, 3.05), (2.2, 3.95)), dict(tw=6.8)),   # run back to A
    ("hands_forward_gesture", 20.6, 34.0, (3.72, 2.05), -90,                                # pushing the sofa
     dict(wclip="pistol_walk", tw=3.9, face_fixed=-60, src_from=1.15, speed=0.03)),
    ("breathing_idle", 34.0, 39.4, (3.6, 2.05), -90, {}),
    ("nervously_look_around", 39.4, 43.0, P_PH, face(P_PH, P_ARI), {}),
    ("breathing_idle", 43.0, 49.6, P_PH, face(P_PH, P_ARI), {}),
    ("breathing_idle", 49.6, 55.6, P_ME, face(P_ME, P_MOM), {}),
    ("hands_forward_gesture", 55.6, 59.8, P_ME, face(P_ME, (2.2, 3.0)), dict(src_from=0.4, speed=0.45)),
    ("breathing_idle", 59.8, END, P_ME, face(P_ME, (2.2, 3.0)), {}),
]
for nm, a_, b_, p_, f_, kw_ in ME:
    act("me", nm, a_, b_, (p_[0], p_[1], 0), f_, **kw_)
for _ch in CH.values():
    for fc in [fc for fc in fcurves_of(_ch.rig) if fc.data_path in ("location", "rotation_euler")]:
        for kp in fc.keyframe_points:
            kp.interpolation = "CONSTANT"

# ---- the sofa: Kazemi and I push it from its place against the hole (20.8-24.6), then it shakes with every blow
S0, S1 = (3.4, 3.95, 0.0), (4.55, 2.2, -90.0)
PUSH0, PUSH1 = 21.1, 24.5
for f in range(fr(PUSH0) - 1, fr(PUSH1) + 1):
    u = seg((f - 1) / FPS, PUSH0, PUSH1)
    sofa_pivot.location = (S0[0] + (S1[0] - S0[0]) * u, S0[1] + (S1[1] - S0[1]) * u, 0)
    sofa_pivot.rotation_euler = (0, 0, math.radians(S1[2] * u))
    sofa_pivot.keyframe_insert("location", frame=f)
    sofa_pivot.keyframe_insert("rotation_euler", frame=f)
# blows: the moments Rezaei's hands reach furthest towards -X
_rr = CH["rezaei"].rig
xs = []
for f in range(fr(24.6), fr(34.0)):
    sc.frame_set(f)
    xs.append((min((_rr.matrix_world @ _rr.pose.bones[b].matrix).translation.x for b in ("hand_r", "hand_l")), f))
BLOWS = []
for i in range(2, len(xs) - 2):
    v, f = xs[i]
    if v <= min(x for x, _ in xs[i - 2:i + 3]) and v < 5.5 and (not BLOWS or f - BLOWS[-1] > 10):
        BLOWS.append(f)
print("BLOWS", [round((f - 1) / FPS, 2) for f in BLOWS])
for f in BLOWS:
    for df, dx in ((-1, 0.0), (0, -0.045), (2, -0.02), (5, 0.0)):
        sofa_pivot.location = (S1[0] + dx, S1[1], 0)
        sofa_pivot.rotation_euler = (0, 0, math.radians(S1[2] + dx * 30))
        sofa_pivot.keyframe_insert("location", frame=f + df)
        sofa_pivot.keyframe_insert("rotation_euler", frame=f + df)
import json  # noqa: E402
os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
json.dump({"blows": [(f - 1) / FPS for f in BLOWS], "push": [PUSH0, PUSH1]}, open(os.path.join(HERE, "out", "hits.json"), "w"))

# ---- faces (shape keys) and visibility
WORRY = {"mom": [(0, 1.8), (9.3, 2.0), (34, 1.6), (39.4, 1.0), (49.8, 0.2), (55, 1.8)],
         "kazemi": [(0, 1.7), (19, 1.9), (34, 1.4), (39.4, 0.9), (49.8, 0.3), (55, 1.8)],
         "arian": [(0, 2.0), (39.4, 1.2), (49.6, 0.4), (55, 1.9)], "mahsa": [(0, 2.0), (39.4, 1.0), (49.8, 0.4), (54, 2.0)],
         "rezaei": [(0, 0.0)], "kian": [(0, 2.0)], "me": [(0, 0.5)]}


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
        if f == 1 or present(who, t) != present(who, t - 1 / FPS):
            ch.hide(f, not present(who, t))
    ch.flush()
# the scratch shows from the moment we ran back (nobody saw how it happened)
key_vis_list = _scr
for o in key_vis_list:
    key_vis(o, [(0, False), (12.0, True)])

# ------------------------------------------------------------------ Arian's phone (screen lit)
M_["phone"] = P.mat("Phone body", (0.08, 0.08, 0.1), 0.3)
scrm = P.mat("Phone screen", (0.75, 0.85, 1.0), 0.3, emit=(0.75, 0.85, 1.0), strength=2.5)
sc.frame_set(fr(44.0))
_ar = CH["arian"].rig
pm = _ar.matrix_world @ _ar.pose.bones["hand_r"].matrix
ph = put(P.box(pm.translation + pm.to_3x3() @ Vector((0, 0.09, -0.02)), (0.075, 0.15, 0.01), M_["phone"], "Arian phone"))
pscr = put(P.box(pm.translation + pm.to_3x3() @ Vector((0, 0.09, -0.027)), (0.066, 0.135, 0.004), scrm, "Arian phone screen"))
for o in (ph, pscr):
    o.rotation_euler = (0, 0, 0)
    con = o.constraints.new("CHILD_OF")
    con.target, con.subtarget = _ar, "hand_r"
    con.inverse_matrix = pm.inverted()
    key_vis(o, [(0, False), (39.4, True), (49.6, False)])

# ------------------------------------------------------------------ camera: my eyes (POV), fisheye added in post
me = CH["me"]
mrig = me.rig
hb = mrig.pose.bones["head"]                 # my head is hidden (scaled to nothing): the camera sits there
hb.scale = (0.001, 0.001, 0.001)
hb.keyframe_insert("scale", frame=1)
nb = mrig.pose.bones["neck_01"]
nb.scale = (0.2, 0.2, 0.2)
nb.keyframe_insert("scale", frame=1)
RHAND, PHONE, REZ = "rhand", "phone", "rezaei"
# (t, where I look, seconds to turn there)
LOOK = [
    (0.0, (13.0, 3.0, 1.05), 0.0),           # Rezaei on the bed (where episode 1 ended)
    (1.0, (15.4, 1.5, 1.37), 0.8),           # Kian's face in the hole behind me
    (4.0, (13.0, 3.0, 1.0), 0.7),            # Rezaei talks
    (8.6, REZ, 0.4),                         # he screams and gets up
    (10.9, (10.4, 2.0, 1.2), 0.5),           # run: the hole to B
    (13.2, REZ, 0.4),                        # a look back: he follows
    (14.2, (5.08, 2.2, 1.1), 0.5),           # the hole to A
    (17.4, (2.6, 3.2, 1.0), 0.6),            # flat A
    (19.0, (2.2, 3.95, 1.4), 0.4),           # Kazemi at the sofa
    (20.9, (4.6, 2.4, 0.55), 0.6),           # pushing: the sofa, my hands
    (24.4, (5.2, 2.2, 1.35), 0.4),           # Rezaei's head above the sofa
    (29.6, (1.0, 2.7, 1.0), 0.7),            # the others, terrified
    (31.6, (5.3, 2.2, 1.35), 0.5),           # the hole again
    (34.2, REZ, 0.8),                        # he lurches away
    (37.8, (1.3, 2.2, 1.1), 0.9),            # silence; the others
    (39.4, PHONE, 0.7),                      # Arian's phone
    (49.6, (1.3, 2.8, 1.5), 0.6),            # mom
    (53.8, (2.75, 1.3, 1.45), 0.5),          # Mahsa
    (55.9, RHAND, 0.7),                      # my hand: the scratch
    (59.6, (1.6, 2.3, 1.45), 0.8),           # their faces
    (62.2, (3.35, 3.0, 1.6), 0.7),           # Kazemi
]


def bone_w(rig, b):
    return (rig.matrix_world @ rig.pose.bones[b].matrix).translation


cam = bpy.data.objects.new("Camera", bpy.data.cameras.new("Camera"))
sc.collection.objects.link(cam)
sc.camera = cam
cam.data.clip_start = 0.03
cam.data.lens = 15
cam.data.sensor_width = 36
cam.rotation_mode = "QUATERNION"
_rnd = random.Random(7)
eye_s = None
d_prev = None
EYE = {}
tg_s = {}
for f in range(1, N + 1):
    t = (f - 1) / FPS
    sc.frame_set(f)
    hw = mrig.matrix_world @ nb.matrix          # neck base (head and neck are shrunk)
    fwd = Vector((-math.sin(mrig.rotation_euler[2] - math.pi), math.cos(mrig.rotation_euler[2] - math.pi), 0))
    eye = hw.translation + Vector((0, 0, 0.23)) + fwd * 0.13
    eye_s = eye if eye_s is None else eye_s.lerp(eye, 0.45)

    def target(k):
        v = LOOK[k][1]
        if v == RHAND:
            p = bone_w(mrig, "hand_r")
        elif v == PHONE:
            p = bone_w(CH["arian"].rig, "hand_r") + Vector((0, 0, 0.06)) if t >= 39.4 else bone_w(CH["arian"].rig, "head")
        elif v == REZ:
            p = bone_w(CH["rezaei"].rig, "head") - Vector((0, 0, 0.1))
        else:
            return Vector(v)
        tg_s[k] = p if k not in tg_s else tg_s[k].lerp(p, 0.3)
        return tg_s[k]
    k = max(i for i, l in enumerate(LOOK) if l[0] <= t)
    d1 = (target(k) - eye_s).normalized()
    if k > 0:
        d0 = (target(k - 1) - eye_s).normalized()
        d = d0.lerp(d1, seg(t, LOOK[k][0], LOOK[k][0] + LOOK[k][2])).normalized()
    else:
        d = d1
    d_prev = d if d_prev is None else d_prev.lerp(d, 0.5).normalized()
    lim = -0.62 if 55.5 < t < 60.0 or 20.5 < t < 24.6 else -0.42      # steeper only for my hands
    dz = max(d_prev.z, lim)
    hz = Vector((d_prev.x, d_prev.y, 0)).normalized() * math.sqrt(1 - dz * dz)
    q = Vector((hz.x, hz.y, dz)).to_track_quat("-Z", "Y")
    q.rotate(Matrix.Rotation(0.004 * _rnd.uniform(-1, 1), 4, "X"))
    cam.location = eye_s
    cam.rotation_quaternion = q
    cam.keyframe_insert("location", frame=f)
    cam.keyframe_insert("rotation_quaternion", frame=f)
    EYE[f] = eye_s.copy()
for fc in fcurves_of(cam):
    for kp in fc.keyframe_points:
        kp.interpolation = "LINEAR"
# anybody the camera would pass through (running through the holes) is hidden for those frames
for who, ch in CH.items():
    if who == "me":
        continue
    rig = ch.rig
    near = []
    for f in range(1, N + 1):
        if not present(who, (f - 1) / FPS):
            continue
        sc.frame_set(f)
        c = EYE[f]
        if min((c - bone_w(rig, b)).length for b in ("head", "spine_03", "spine_01")) < 0.34:
            near.append(f)
    if near:
        spans, a = [], near[0]
        for p, q_ in zip(near, near[1:] + [None]):
            if q_ != p + 1:
                spans.append((a - 1, p + 1))
                a = q_
        print("NEAR", who, spans)
        for a, b in spans:
            ch.hide(a, True)
            ch.hide(b + 1, False)
        ch.flush()

# ------------------------------------------------------------------ look
sc.frame_set(1)
for who, ch in CH.items():
    if who == "me":
        continue
    rig = ch.rig
    for f in range(1, N + 1):
        t = (f - 1) / FPS
        if not present(who, t):
            continue
        sc.frame_set(f)
        hw = rig.matrix_world @ rig.pose.bones["head"].head
        fwd = (rig.matrix_world.to_3x3() @ rig.pose.bones["head"].matrix.to_3x3() @ Vector((0, 0, 1))).normalized()
        fwd2 = (rig.matrix_world.to_3x3() @ Vector((0, -1, 0))).normalized()
        if fwd.dot(fwd2) < 0.3:
            fwd = fwd2
        to_me = EYE[f] - hw
        la = EYE[f] if to_me.normalized().dot(fwd) > 0.45 else hw + Vector((0, 0, 0.1)) + fwd * 2.0
        if 55.6 < t < 64.5 and who != "rezaei":         # everybody stares at my hand, then at me
            la = bone_w(mrig, "hand_r") if t < 58.4 else EYE[f]
        st = dict(t=t, seed=ch.seed, worry=worry(who, t), talking=speaking(who, t), look_at=la)
        if who == "rezaei":
            st["brows"] = "angry"
            st["scream"] = (0.25 * seg(t, 7.0, 8.6) + 0.75 * seg(t, 8.8, 9.3) - 0.45 * seg(t, 11.0, 11.8)
                            if t < 24.6 else 0.55)
            if speaking("rezaei", t):
                st["scream"] = 0.15
        ch.face_pose(f, t, st)
    ch.flush()
sc.frame_set(1)
for who, ch in CH.items():
    PP.finish(ch, outline=0.0016 if who == "me" else 0.0055, smile=0, keep_head=(who == "me"))
import colorsys  # noqa: E402
for o in list(bpy.data.objects):
    if o.type != "MESH" or any(o in c.objects for c in CH.values()):
        continue
    for slot in o.material_slots:
        m = slot.material
        if not m or m.name.startswith(("PP ", "Hull")) or not m.node_tree:
            continue
        if any(n.type in ("TEX_IMAGE", "EMISSION") for n in m.node_tree.nodes):
            continue
        c = PP._base(m)
        if c is None:
            continue
        h, sa, v = colorsys.rgb_to_hsv(*c)
        c2 = colorsys.hsv_to_rgb(h, min(1, sa * 1.5 + 0.08), min(1, v * 1.15 + 0.05))
        slot.material = PP.toon_mat(f"set {m.name}", c2, 0.22)
sc.render.engine = "CYCLES"
sc.cycles.samples = int(os.environ.get("SAMPLES", "10"))
sc.cycles.use_denoising = True
sc.cycles.max_bounces = 3
sc.view_settings.view_transform = "Standard"
sc.view_settings.look = "None"
w.color = (0.25, 0.25, 0.3)
sc.render.resolution_x, sc.render.resolution_y = 540, 960
sc.render.film_transparent = False

args = sys.argv
if "--still" in args:
    os.makedirs(os.path.join(HERE, "test"), exist_ok=True)
    for f in [int(v) for v in args[args.index("--still") + 1].split(",")]:
        sc.frame_set(f)
        sc.render.filepath = os.path.join(HERE, "test", f"s_{f:04d}.png")
        bpy.ops.render.render(write_still=True)
if "--save" in args:
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(HERE, "wall2.blend"))
