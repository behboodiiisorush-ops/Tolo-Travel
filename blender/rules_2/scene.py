"""«قانون‌ها — قسمت دوم» («قانون ۶»): the night goes on in Arian's house. Comic look (EEVEE cel shading + ink
outlines, blender/studio/toon_look.py) on the realistic cast, bodies driven by the Mixamo clips (blender/mocap).

    ../cast/bpy.sh scene.py --still 40,120,...      -> test/s_XXXX.png
    ../cast/bpy.sh scene.py --spy                   -> textures/spy.png (the photo on my phone in shot K)
    ../cast/bpy.sh scene.py --save                  -> rules_2.blend (render.py renders from it)
Shots (seconds):
  A  0.0- 6.0  living room, police lights through the window; a megaphone calls Arian by name
  B  6.0-11.5  Arian heads for the front door, I stop him (rule 2)
  C 11.5-18.5  Nina's laptop: the front-door camera - masked men, not police
  D 18.5-24.5  my phone: rule 6 (Nina will take out her phone in ten seconds)
  E 24.5-33.0  Nina stands up and takes out her phone; "who are you calling?"
  F 33.0-38.0  banging on the front door, a masked man at the window; "the back door!"
  G 38.0-43.0  Nina opens the back door (the door follows her hand)
  H 43.0-50.0  the backyard at night, we sneak to the shed
  I 50.0-55.0  Arian opens the shed door, we slip in
  J 55.0-62.0  inside the shed, kneeling in the dark; "nobody knows this place"
  K 62.0-68.0  my phone: rule 7 "don't turn around" + a photo of the three of us from behind
  L 68.0-75.5  a red camera light blinks in the dark behind us... and two eyes
"""
import bpy, sys, os, math, random
from mathutils import Vector, Matrix
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "cast"))
sys.path.insert(0, os.path.join(HERE, "..", "studio"))
bpy.ops.wm.read_factory_settings(use_empty=True)
import cast, mocap, anim  # noqa: E402
import props as P         # noqa: E402
import toon_look as T     # noqa: E402
from captions import END, speaking  # noqa: E402

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


def facing_to(a, b):
    d = Vector(b) - Vector(a)
    return math.degrees(math.atan2(-d.x, d.y))


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


def show(objs, spans):
    for o in objs:
        pts = [(0, False)]
        for a, b in spans:
            pts += [(a, True), (b, False)]
        key_vis(o, pts)


# ------------------------------------------------------------------ cast (first: building it purges unused data)
CH = {}
for k, q in (("me", "hero"), ("arian", "hero"), ("nina", "hero"), ("masked", "extra"), ("masked", "hero")):
    ch = cast.spawn(k, quality=q)
    key = k if k not in CH else "masked2"
    if key == "masked" and "masked" in CH:
        key = "masked2"
    T.register(ch, "masked" if key.startswith("masked") else k, realistic=True)
    cast.comic_eyes(ch)
    CH[key] = ch
print("CAST", {k: c.name for k, c in CH.items()})
# three teenagers in near-identical blues read as one blob in the flat look: give each a colour of their own
for who, cols in (("arian", {"namuhekam_male_polo_shirt": (0.36, 0.42, 0.18)}),
                  ("nina", {"mindfront_knitted_sweater_02": (0.55, 0.13, 0.19)}),
                  ("me", {"elvs_hooded_sweat_jacket1": (0.1, 0.17, 0.4)})):
    skin, clothes = T.SKIN[CH[who].name]
    clothes = dict(clothes)
    clothes.update(cols)
    T.SKIN[CH[who].name] = (skin, clothes)
CLIP = {}


def clip(name):
    if name not in CLIP:
        CLIP[name] = mocap.load(os.path.join(MOC, name + ".fbx"))
    return CLIP[name]


def walk_speed(who, name):
    """Speed (m/s) at which the in-place cycle's planted foot does not slide."""
    ch = CH[who]
    rig = ch.rig
    s0 = 5000
    n = mocap.apply(ch, clip(name), start=s0, length=48, offset=(0, 0, 0), facing=0, in_place=True, loop=True)
    pts = []
    for f in range(s0, s0 + n):
        sc.frame_set(f)
        for side in ("l", "r"):
            p = (rig.matrix_world @ rig.pose.bones[f"foot_{side}"].matrix).translation
            pts.append((side, f, p.y, p.z))
    v = []
    for side in ("l", "r"):
        s = [(f, y, z) for sd, f, y, z in pts if sd == side]
        zmin = min(z for _, _, z in s)
        for (f0, y0, z0), (f1, y1, z1) in zip(s, s[1:]):
            if z0 < zmin + 0.025 and z1 < zmin + 0.025:
                v.append(abs(y1 - y0) * FPS)
    v.sort()
    return v[len(v) // 2] if v else 1.0


V = {}
for who in ("me", "arian", "nina"):
    for name in ("walking", "sneak_walk"):
        V[(who, name)] = walk_speed(who, name)
for _ch in CH.values():
    for fc in fcurves_of(_ch.rig):
        for kp in [kp for kp in fc.keyframe_points if kp.co.x >= 4999][::-1]:
            fc.keyframe_points.remove(kp)
mocap.LAST.clear()
print("WALK SPEEDS", {f"{a}/{b}": round(v, 2) for (a, b), v in V.items()})

CUTS = {0.0, 6.0, 11.5, 18.5, 24.5, 33.0, 38.0, 43.0, 50.0, 55.0, 62.0}
LASTSEG = {}


def act(who, name, t0, t1, pos, facing, follow=None, turn=0.0, **kw):
    """`who` plays clip `name` from t0 to t1 at pos/facing. Inside a shot the body eases out of the previous pose
    (blend) and, with follow, the hips continue from where they were; turn = seconds to turn from the old facing."""
    rig = CH[who].rig
    n = fr(t1) - fr(t0)
    in_shot = t0 not in CUTS and LASTSEG.get(who) == t0
    if follow is None:
        follow = in_shot
    if in_shot and not turn:
        turn = 0.5
    hips_prev = None
    if follow and in_shot:
        sc.frame_set(fr(t0) - 1)
        hips_prev = (rig.matrix_world @ rig.pose.bones["pelvis"].matrix).translation.copy()
    old_rz = None
    if in_shot:
        sc.frame_set(fr(t0) - 1)
        old_rz = rig.rotation_euler[2]
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
    if turn and old_rz is not None:
        new = math.radians(facing) + math.pi
        while new - old_rz > math.pi:
            new -= 2 * math.pi
        while new - old_rz < -math.pi:
            new += 2 * math.pi
        rig.rotation_euler = (0, 0, old_rz)
        rig.keyframe_insert("rotation_euler", index=2, frame=fr(t0))
        rig.rotation_euler = (0, 0, new)
        rig.keyframe_insert("rotation_euler", index=2, frame=fr(t0 + turn))
        rig.keyframe_insert("rotation_euler", index=2, frame=fr(t1) - 1)
    LASTSEG[who] = t1
    return Vector(pos)


def walk(who, t0, t1, p0, p1, name="walking"):
    """Straight walk from p0 to p1 between t0 and t1; the cycle plays at the rate that keeps the feet planted."""
    p0, p1 = Vector(p0), Vector(p1)
    facing = facing_to(p0, p1)
    v = (p1 - p0).length / (t1 - t0)
    d = (p1 - p0).normalized()
    n = fr(t1) - fr(t0)
    in_shot = t0 not in CUTS and LASTSEG.get(who) == t0
    mocap.apply(CH[who], clip(name), start=fr(t0), length=n, speed=v / V[(who, name)], in_place=True, loop=True,
                place=lambda j: (tuple(p0 + d * v * j / FPS), facing), blend=8 if in_shot else 0)
    LASTSEG[who] = t1
    return p1


# ------------------------------------------------------------------ set
H = 2.7
WT = 0.14
M_ = dict(
    wall=P.mat("Wall", (0.6, 0.55, 0.47), 0.9), wall2=P.mat("Wall back", (0.5, 0.52, 0.5), 0.9),
    floor=P.mat("Floor", (0.42, 0.34, 0.27), 0.7), ceil=P.mat("Ceiling", (0.72, 0.72, 0.7), 0.9),
    frame=P.mat("Frame", (0.92, 0.92, 0.9), 0.5), door=P.mat("Door", (0.46, 0.34, 0.24), 0.6),
    metal=P.mat("Metal", (0.7, 0.72, 0.74), 0.3, metal=0.8), sofa=P.mat("Sofa", (0.36, 0.4, 0.46), 0.9),
    wood=P.mat("Wood", (0.45, 0.33, 0.22), 0.6), dark=P.mat("Dark", (0.04, 0.04, 0.05), 0.9),
    rug=P.mat("Rug", (0.5, 0.22, 0.2), 0.95), lap=P.mat("Laptop", (0.2, 0.21, 0.23), 0.4, metal=0.3),
    phone=P.mat("Phone body", (0.06, 0.06, 0.07), 0.3), grass=P.mat("Grass", (0.2, 0.3, 0.17), 0.95),
    fence=P.mat("Fence", (0.4, 0.3, 0.22), 0.85), shed=P.mat("Shed boards", (0.5, 0.4, 0.3), 0.85),
    roof=P.mat("Shed roof", (0.25, 0.25, 0.27), 0.7), asph=P.mat("Street", (0.18, 0.18, 0.2), 0.9),
    houses=P.mat("Far houses", (0.12, 0.12, 0.16), 0.9), bark=P.mat("Bark", (0.25, 0.18, 0.12), 0.9),
    leaves=P.mat("Leaves", (0.12, 0.22, 0.14), 0.9), box=P.mat("Boxes", (0.62, 0.5, 0.34), 0.9),
    tool=P.mat("Tools", (0.35, 0.36, 0.38), 0.4, metal=0.6), lamp=P.mat("Lampshade", (0.9, 0.82, 0.6), 0.7),
)


def box(loc, size, m, name="Set"):
    return P.box(loc, size, M_[m] if isinstance(m, str) else m, name)


def centred(o, loc):
    """P.box / P.plane bake the location into the mesh: move the origin back to loc so the object rotates in place."""
    o.data.transform(Matrix.Translation(-Vector(loc)))
    o.location = loc
    return o


# living room: x 0..6, y 0..5
box((3, 2.5, -0.05), (6, 5, 0.1), "floor", "Room floor")
box((2.6, 2.6, 0.005), (2.6, 1.8, 0.01), "rug", "Rug")
# ceiling with the open vent (from part 1) at x 0.7..1.3, y 3.7..4.3
box((3.65, 2.5, H + 0.05), (4.7, 5, 0.1), "ceil", "Room ceiling")
box((0.35, 2.5, H + 0.05), (0.7, 5, 0.1), "ceil", "Room ceiling")
box((1.0, 1.85, H + 0.05), (0.6, 3.7, 0.1), "ceil", "Room ceiling")
box((1.0, 4.65, H + 0.05), (0.6, 0.7, 0.1), "ceil", "Room ceiling")
box((1.0, 4.0, H + 0.25), (0.8, 0.8, 0.05), "dark", "Vent duct")
grille = box((1.0, 3.72, H - 0.28), (0.6, 0.03, 0.56), "metal", "Vent grille (hanging open)")
box((1.0, 4.0, 0.45), (0.45, 0.45, 0.05), "wood", "Chair seat")
for dx in (-0.19, 0.19):
    for dy in (-0.19, 0.19):
        box((1.0 + dx, 4.0 + dy, 0.22), (0.04, 0.04, 0.44), "wood", "Chair leg")
box((1.0, 4.2, 0.72), (0.45, 0.04, 0.5), "wood", "Chair back")
# walls
box((-WT / 2, 2.5, H / 2), (WT, 5, H), "wall", "Left wall")
box((6 + WT / 2, 2.5, H / 2), (WT, 5, H), "wall", "Right wall")
# front wall y=0: door x 0.8..1.7, window x 3.4..5.0 (z 0.8..2.2)
box((0.4, -WT / 2, H / 2), (0.8, WT, H), "wall", "Front wall")
box((1.25, -WT / 2, 2.4), (0.9, WT, 0.6), "wall", "Front wall")
box((2.55, -WT / 2, H / 2), (1.7, WT, H), "wall", "Front wall")
box((4.2, -WT / 2, 0.4), (1.6, WT, 0.8), "wall", "Front wall")
box((4.2, -WT / 2, 2.45), (1.6, WT, 0.5), "wall", "Front wall")
box((5.5, -WT / 2, H / 2), (1.0, WT, H), "wall", "Front wall")
for s in (0.76, 1.74):
    box((s, -0.07, 1.05), (0.08, WT + 0.04, 2.1), "frame", "Door frame")
box((1.25, -0.07, 2.13), (1.06, WT + 0.04, 0.08), "frame", "Door frame")
for z in (0.78, 2.22):
    box((4.2, -0.07, z), (1.7, WT + 0.06, 0.06), "frame", "Window frame")
for x in (3.38, 4.2, 5.02):
    box((x, -0.07, 1.5), (0.06, WT + 0.06, 1.44), "frame", "Window frame")
# back wall y=5: back door x 4.2..5.1
box((2.1, 5 + WT / 2, H / 2), (4.2, WT, H), "wall2", "Back wall")
box((4.65, 5 + WT / 2, 2.4), (0.9, WT, 0.6), "wall2", "Back wall")
box((5.55, 5 + WT / 2, H / 2), (0.9, WT, H), "wall2", "Back wall")
for s in (4.16, 5.14):
    box((s, 5.0, 1.05), (0.08, WT + 0.04, 2.1), "frame", "Back door frame")
box((4.65, 5.0, 2.13), (1.06, WT + 0.04, 0.08), "frame", "Back door frame")


def door(name, hinge_at, width, handle_side_y, height=2.05, thick=0.045, mat="door"):
    """Door leaf along +X from the hinge; the handle near the free edge on the face at handle_side_y (+1/-1)."""
    hinge = P.empty(name + " hinge", hinge_at)
    leaf = box((hinge_at[0] + width / 2, hinge_at[1], hinge_at[2] + height / 2 + 0.01), (width - 0.02, thick, height),
               mat, name)
    knob = P.sphere((hinge_at[0] + width - 0.1, hinge_at[1] + handle_side_y * (thick / 2 + 0.035), hinge_at[2] + 0.95),
                    0.032, M_["metal"], name + " handle")
    for o in (leaf, knob):
        o.parent = hinge
        o.matrix_parent_inverse = hinge.matrix_world.inverted()
    return hinge, knob


FRONT_HINGE, _ = door("Front door", (0.8, -0.07, 0), 0.9, +1)
BACK_HINGE, BACK_KNOB = door("Back door", (4.2, 5.0, 0), 0.9, -1)
# furniture: sofa facing -Y, coffee table, laptop, floor lamp, shelf
box((2.6, 3.72, 0.22), (2.0, 0.8, 0.44), "sofa", "Sofa")
box((2.6, 4.08, 0.6), (2.0, 0.18, 0.75), "sofa", "Sofa back")
for sx in (1.55, 3.65):
    box((sx, 3.72, 0.32), (0.12, 0.8, 0.62), "sofa", "Sofa arm")
box((2.6, 2.75, 0.2), (1.1, 0.55, 0.4), "wood", "Coffee table")
box((2.6, 2.82, 0.41), (0.34, 0.24, 0.015), "lap", "Laptop base")
LAP_SCREEN_C = Vector((2.6, 2.7, 0.53))
centred(box(tuple(LAP_SCREEN_C), (0.34, 0.012, 0.22), "lap", "Laptop lid"), tuple(LAP_SCREEN_C)).rotation_euler = (math.radians(12), 0, 0)
lapm = P.image("Laptop screen", os.path.join(TEX, "doorcam.png"), strength=1.4)
lscr = centred(P.plane((0, 0, 0), (0.3, 0.19), lapm, name="Laptop screen"), tuple(LAP_SCREEN_C + Vector((0, 0.0075, 0.0016))))
_s, _c = math.sin(math.radians(12)), math.cos(math.radians(12))
_m = Matrix.Identity(3)
_m.col[0], _m.col[1], _m.col[2] = Vector((-1, 0, 0)), Vector((0, -_s, _c)), Vector((0, _c, _s))
lscr.rotation_euler = _m.to_euler()
P.cyl((5.4, 4.5, 0.0), (5.4, 4.5, 1.45), 0.02, M_["metal"], "Lamp pole")
P.cyl((5.4, 4.5, 1.4), (5.4, 4.5, 1.7), 0.18, M_["lamp"], "Lampshade", verts=20)
box((0.25, 1.9, 1.0), (0.3, 1.2, 2.0), "wood", "Bookshelf")
for z in (0.45, 0.95, 1.45):
    box((0.28, 1.9, z), (0.26, 1.1, 0.25), "box", "Books")
# outside the front: street, far houses (no signs), dark sky
box((3, -6, -0.06), (30, 12, 0.1), "asph", "Street")
for i, (x, w, h) in enumerate([(-4, 5, 4.5), (2, 4, 6), (7, 6, 5), (13, 5, 7)]):
    box((x, -11, h / 2), (w, 3, h), "houses", f"Far house {i}")
# backyard: y 5..14
box((5, 9.5, -0.06), (16, 9, 0.1), "grass", "Grass")
for x in [i * 0.5 - 2 for i in range(29)]:
    box((x, 14, 0.8), (0.42, 0.05, 1.6), "fence", "Fence board")
for y in [5.5 + i * 0.5 for i in range(17)]:
    for x in (-2.2, 12.2):
        box((x, y, 0.8), (0.05, 0.42, 1.6), "fence", "Fence board")
P.cyl((1.6, 10.5, 0), (1.6, 10.5, 2.4), 0.13, M_["bark"], "Tree trunk")
P.sphere((1.6, 10.5, 3.0), 1.2, M_["leaves"], "Tree crown")
box((5, 14.5, 2.5), (30, 0.2, 5), "houses", "Yard far wall")
# the shed: x 6.4..8.8, y 9.5..11.7, door on the south wall x 7.2..8.0
SX0, SX1, SY0, SY1, SH = 6.4, 8.8, 9.5, 11.7, 2.3
box(((SX0 + SX1) / 2, (SY0 + SY1) / 2, 0.02), (SX1 - SX0, SY1 - SY0, 0.04), "wood", "Shed floor")
box((SX0, (SY0 + SY1) / 2, SH / 2), (0.08, SY1 - SY0, SH), "shed", "Shed wall")
box((SX1, (SY0 + SY1) / 2, SH / 2), (0.08, SY1 - SY0, SH), "shed", "Shed wall")
box(((SX0 + SX1) / 2, SY1, SH / 2), (SX1 - SX0, 0.08, SH), "shed", "Shed wall")
box(((SX0 + 7.2) / 2, SY0, SH / 2), (7.2 - SX0, 0.08, SH), "shed", "Shed wall")
box(((8.0 + SX1) / 2, SY0, SH / 2), (SX1 - 8.0, 0.08, SH), "shed", "Shed wall")
box((7.6, SY0, (2.0 + SH) / 2), (0.8, 0.08, SH - 2.0), "shed", "Shed wall")
roof = box(((SX0 + SX1) / 2, (SY0 + SY1) / 2, SH + 0.12), (SX1 - SX0 + 0.4, SY1 - SY0 + 0.4, 0.08), "roof", "Shed roof")
SHED_HINGE, SHED_KNOB = door("Shed door", (7.2, SY0, 0.04), 0.8, -1, height=1.95, thick=0.04, mat="shed")
for z in (0.9, 1.55):
    box((7.6, SY1 - 0.2, z), (2.2, 0.3, 0.03), "wood", "Shed shelf")
box((6.9, SY1 - 0.2, 1.0), (0.4, 0.25, 0.18), "box", "Shed box")
box((8.1, SY1 - 0.2, 0.32), (0.5, 0.3, 0.6), "box", "Shed box")
box((7.3, SY1 - 0.22, 1.7), (0.3, 0.2, 0.25), "box", "Shed box")
P.cyl((8.6, 10.2, 0), (8.6, 10.3, 1.4), 0.015, M_["tool"], "Rake handle")
P.cyl((6.6, 10.6, 0), (6.55, 10.7, 1.2), 0.015, M_["tool"], "Shovel handle")
# the hidden camera on the top shelf: a small black box with a blinking red light
CAM_AT = Vector((8.35, SY1 - 0.2, 1.62))
box(tuple(CAM_AT), (0.08, 0.06, 0.06), "phone", "Spy camera")
led = P.sphere(tuple(CAM_AT + Vector((0, -0.035, 0.015))), 0.008, P.emit("Spy LED", (1.0, 0.05, 0.05), 30.0), "Spy LED")
key_vis(led, [(0, True)] + [(t, (k % 2) == 1) for k, t in enumerate([60 + 0.6 * i for i in range(27)])])

# ------------------------------------------------------------------ lights
moon = bpy.data.objects.new("Moon", bpy.data.lights.new("Moon", "SUN"))
sc.collection.objects.link(moon)
moon.data.energy = 1.2
moon.data.color = (0.6, 0.7, 1.0)
moon.rotation_euler = (math.radians(55), 0, math.radians(150))
room_lamp = P.area_light((5.4, 4.5, 1.9), (3.0, 2.5, 0.6), 80, 0.6, (1.0, 0.75, 0.45), name="Floor lamp light")
room_fill = P.area_light((3.0, 2.5, 2.6), (3.0, 2.5, 0), 6, 3.0, (1.0, 0.85, 0.7), name="Room fill")
red = P.area_light((3.5, -1.8, 1.7), (2.6, 3.0, 1.0), 0, 1.0, (1.0, 0.1, 0.08), name="Siren red")
blue = P.area_light((4.9, -1.8, 1.7), (2.6, 3.0, 1.0), 0, 1.0, (0.1, 0.25, 1.0), name="Siren blue")
for f in range(1, fr(43.0) + 1, 3):
    t = (f - 1) / FPS
    on = int(t / 0.3) % 2
    red.data.energy = 900 if on else 60
    blue.data.energy = 60 if on else 900
    red.data.keyframe_insert("energy", frame=f)
    blue.data.keyframe_insert("energy", frame=f)
for l_ in (red, blue):                       # off once we are outside (no red glints in the eyes later)
    l_.data.energy = 0
    l_.data.keyframe_insert("energy", frame=fr(43.0) + 1)
shed_dim = P.area_light((7.6, 10.4, 2.2), (7.6, 10.4, 0), 6, 1.6, (0.55, 0.65, 1.0), name="Shed dim")
yard_fill = P.area_light((5.0, 8.0, 4.0), (6.5, 9.5, 0), 70, 6.0, (0.5, 0.6, 0.9), name="Yard fill")
w = bpy.data.worlds.new("Night")
sc.world = w
w.color = (0.02, 0.025, 0.05)

# ------------------------------------------------------------------ action
ME0, AR0, NI_SOFA = Vector((1.25, 3.55, 0)), Vector((1.85, 3.1, 0)), Vector((2.6, 3.5, 0.0))
WIN = Vector((4.2, 0, 1.4))
# A: just down from the vent, the megaphone outside
act("me", "nervously_look_around", 0.0, 6.0, tuple(ME0), facing_to(ME0, WIN))
act("arian", "nervously_look_around", 0.0, 6.0, tuple(AR0), facing_to(AR0, WIN), src_from=1.5)
act("nina", "sitting_idle", 0.0, 11.5, tuple(NI_SOFA), 180, loop=True)
# B: Arian heads for the front door, I stop him
AR_B = Vector((1.5, 1.25, 0))
act("arian", "breathing_idle", 6.0, 6.5, tuple(AR0), facing_to(AR0, AR_B))
walk("arian", 6.5, 8.4, AR0, AR_B)
ME_B = Vector((1.75, 2.2, 0))
act("me", "breathing_idle", 6.0, 6.9, tuple(ME0), facing_to(ME0, ME_B))
walk("me", 6.9, 8.5, ME0, ME_B)
act("arian", "breathing_idle", 8.4, 11.5, tuple(AR_B), facing_to(AR_B, ME_B), src_from=2.0, turn=0.6)
act("me", "hands_forward_gesture", 8.5, 11.5, tuple(ME_B), facing_to(ME_B, AR_B))
# C: Nina's laptop, we stand behind the sofa
ME_C, AR_C = Vector((2.0, 4.45, 0)), Vector((3.25, 4.45, 0))
act("me", "breathing_idle", 11.5, 18.5, tuple(ME_C), 180)
act("arian", "nervously_look_around", 11.5, 18.5, tuple(AR_C), 190, src_from=2.0)
act("nina", "sitting_idle", 11.5, 24.5, tuple(NI_SOFA), 180, loop=True, src_from=1.0)
# D: my phone (rule 6) - I stand by the sofa end, looking down at it
ME_D = Vector((1.15, 3.2, 0))
act("me", "breathing_idle", 18.5, 24.5, tuple(ME_D), 150, src_from=3.0)
act("arian", "breathing_idle", 18.5, 24.5, tuple(AR_C), 200)
# E: Nina gets up and takes out her phone; I face her
NI_E = Vector((2.4, 3.15, 0))
act("nina", "sit_to_stand", 24.5, 26.8, tuple(NI_SOFA + Vector((0, -0.12, 0))), 180)
act("nina", "breathing_idle", 26.8, 33.0, tuple(NI_E), 200, src_from=2.0)
ME_E = Vector((1.55, 2.2, 0))
act("me", "breathing_idle", 24.5, 27.3, tuple(ME_E), facing_to(ME_E, NI_E))
act("me", "hands_forward_gesture", 27.3, 30.4, tuple(ME_E), facing_to(ME_E, NI_E))
act("me", "breathing_idle", 30.4, 33.0, tuple(ME_E), facing_to(ME_E, NI_E), src_from=1.0)
AR_E = Vector((1.1, 3.2, 0))
act("arian", "nervously_look_around", 24.5, 33.0, tuple(AR_E), facing_to(AR_E, NI_E))
# F: banging on the front door; a masked man at the window
FRONT = Vector((1.25, 0, 1.0))
ME_F, AR_F, NI_F = Vector((1.9, 2.8, 0)), Vector((3.0, 2.2, 0)), Vector((2.6, 3.3, 0))
act("me", "terrified", 33.0, 38.0, tuple(ME_F), facing_to(ME_F, FRONT), src_from=8.0)
act("arian", "nervously_look_around", 33.0, 38.0, tuple(AR_F), facing_to(AR_F, FRONT), src_from=0.5)
BACKDOOR = Vector((4.65, 5.0, 1.0))
act("nina", "nervously_look_around", 33.0, 34.2, tuple(NI_F), facing_to(NI_F, FRONT))
act("nina", "pointing", 34.2, 38.0, tuple(NI_F), facing_to(NI_F, BACKDOOR) + 55)
act("masked", "punching_bag", 33.0, 38.0, (4.2, -0.78, 0), 0, loop=True)
# shaking front door while he bangs
for k, t in enumerate([33.0 + 0.27 * i for i in range(19)]):
    FRONT_HINGE.rotation_euler = (0, 0, math.radians(0.0 if k % 2 == 0 else 1.6))
    FRONT_HINGE.keyframe_insert("rotation_euler", index=2, frame=fr(t))


def open_door(who, t0, t1, guess, facing, hinge, knob, sign, angle=80.0, src_from=0.5, speed=1.0):
    """`who` opens a door with the opening_door_inwards clip: moved so the reaching hand really meets the handle,
    the hand stays on the handle (IK) while the door swings with it. Returns the touch time."""
    rig = CH[who].rig
    hp = knob.matrix_world.translation.copy()
    last = LASTSEG.get(who)

    def best_touch():
        b = None
        for f in range(fr(t0), fr(min(t1, t0 + 3.0))):
            sc.frame_set(f)
            for side in ("l", "r"):
                p = rig.matrix_world @ rig.pose.bones[f"hand_{side}"].tail
                d = (p - hp).length
                if b is None or d < b[0]:
                    b = (d, f, side)
        return b
    pos = Vector(guess)
    for _ in range(3):
        LASTSEG[who] = last
        act(who, "opening_door_inwards", t0, t1, tuple(pos), facing, follow=False, src_from=src_from, speed=speed)
        b = best_touch()
        print("HAND TO HANDLE", who, round(b[0], 3), b[1], b[2])
        if b[0] < 0.03:
            break
        sc.frame_set(b[1])
        miss = hp - (rig.matrix_world @ rig.pose.bones[f"hand_{b[2]}"].tail)
        pos = pos + Vector((miss.x, miss.y, 0))
    t_touch = (b[1] - 1) / FPS
    for t, ang in ((0, 0), (t_touch + 0.15, 0), (t_touch + 1.6, angle), (END, angle)):
        hinge.rotation_euler = (0, 0, math.radians(sign * ang))
        hinge.keyframe_insert("rotation_euler", index=2, frame=fr(t))
    tgt = P.empty(f"{who} hand target {t0}")
    ik = rig.pose.bones[f"lowerarm_{b[2]}"].constraints.new("IK")
    ik.target, ik.chain_count = tgt, 2
    for f in range(fr(t_touch - 0.5), fr(t_touch + 1.9)):
        sc.frame_set(f)
        tgt.location = knob.matrix_world.translation
        tgt.keyframe_insert("location", frame=f)
    for t, v in ((0, 0.0), (t_touch - 0.35, 0.0), (t_touch, 1.0), (t_touch + 1.5, 1.0), (t_touch + 1.85, 0.0)):
        ik.influence = v
        ik.keyframe_insert("influence", frame=fr(t))
    return t_touch, pos


# G: Nina opens the back door (inwards, towards her), we go out
T_BACK, NI_G = open_door("nina", 38.0, 41.6, (4.95, 4.35, 0), 0, BACK_HINGE, BACK_KNOB, -1)
OUT1 = Vector((4.65, 6.4, 0))
walk("nina", 41.6, 43.0, NI_G, Vector((4.6, 5.6, 0)))
ME_G, AR_G = Vector((3.6, 3.7, 0)), Vector((3.2, 3.1, 0))
act("me", "nervously_look_around", 38.0, 41.0, tuple(ME_G), facing_to(ME_G, BACKDOOR))
walk("me", 41.0, 43.0, ME_G, Vector((4.3, 4.6, 0)))
act("arian", "breathing_idle", 38.0, 41.4, tuple(AR_G), facing_to(AR_G, BACKDOOR))
walk("arian", 41.4, 43.0, AR_G, Vector((3.9, 4.1, 0)))
# H: across the yard to the shed, sneaking
SHED_FRONT = Vector((7.6, SY0 - 0.6, 0))
walk("nina", 43.0, 49.6, Vector((4.6, 5.8, 0)), Vector((6.7, 8.7, 0)))
walk("me", 43.0, 49.8, Vector((4.4, 5.3, 0)), Vector((8.35, 8.55, 0)))
AR_H0 = Vector((4.9, 5.6, 0))
# I: Arian opens the shed door (outwards, towards him); the others wait, then we go in
act("nina", "nervously_look_around", 49.6, 52.6, (6.7, 8.7, 0), 20)
act("me", "nervously_look_around", 49.8, 52.9, (8.35, 8.55, 0), -20, src_from=2.0)
T_SHED, AR_I = open_door("arian", 50.0, 52.8, (7.95, 8.95, 0), 0, SHED_HINGE, SHED_KNOB, -1, angle=95)
walk("arian", 43.0, 49.9, AR_H0, AR_I)
LASTSEG["arian"] = 52.8
KN = {"nina": Vector((7.15, 10.35, 0)), "arian": Vector((7.75, 10.25, 0)), "me": Vector((8.3, 10.4, 0))}
walk("nina", 52.6, 55.0, Vector((6.7, 8.7, 0)), Vector((7.4, 9.9, 0)), name="sneak_walk")
walk("arian", 52.8, 55.0, AR_I, Vector((7.75, 9.95, 0)), name="sneak_walk")
walk("me", 52.9, 55.0, Vector((8.35, 8.55, 0)), Vector((7.9, 9.95, 0)), name="sneak_walk")
# J, K: kneeling in the shed, facing the door (the dark corner and its camera behind us)
for who in ("nina", "arian", "me"):
    act(who, "kneeling_idle", 55.0, 68.0, tuple(KN[who]), 180, loop=True, src_from={"nina": 0, "arian": 1.2, "me": 2.4}[who])
# L: I turn round slowly...; the masked man steps out of the dark corner
act("me", "kneeling_idle", 68.0, END, tuple(KN["me"]), 60, turn=4.5, loop=True, src_from=1.0)
act("arian", "kneeling_idle", 68.0, END, tuple(KN["arian"]), 180, loop=True)
act("nina", "kneeling_idle", 68.0, END, tuple(KN["nina"]), 180, loop=True)
M2 = Vector((6.85, 11.25, 0))
act("masked2", "breathing_idle", 0.0, END, tuple(M2), facing_to(M2, (7.8, 10.2, 0)), loop=True)

# who is visible when
PRESENT = {"me": [(0, END + 1)], "arian": [(0, END + 1)], "nina": [(0, END + 1)],
           "masked": [(33.0, 38.0)], "masked2": [(55.0, END + 1)]}

# ------------------------------------------------------------------ props in hands
M_["phone"] = P.mat("Phone body 2", (0.06, 0.06, 0.07), 0.3)
glow = P.emit("Phone glow", (0.75, 0.85, 1.0), 6.0)


def phone_mesh(name):
    o = box((0, 0, 0), (0.07, 0.008, 0.145), "phone", name)
    s = P.plane((0, -0.0045, 0), (0.062, 0.13), glow, rot=(math.radians(90), 0, 0), name=name + " screen")
    s.parent = o
    o.rotation_mode = "QUATERNION"
    return o, [o, s]


def held_in_front(who, spans, side="r", reach=0.3, drop=0.24):
    """`who` holds a phone in front of the chest, screen to the face: the hand is pulled there by IK every frame
    and the phone sits in the hand."""
    rig = CH[who].rig
    tgt = P.empty(f"{who} phone target")
    ik = rig.pose.bones[f"lowerarm_{side}"].constraints.new("IK")
    ik.target, ik.chain_count = tgt, 2
    ph, parts = phone_mesh(f"{who} phone")
    ik.influence = 0.0
    ik.keyframe_insert("influence", frame=1)
    for a, b in spans:
        for t, v in ((a, 0.0), (a + 0.5, 1.0), (b - 0.4, 1.0), (b, 0.0)):
            ik.influence = v
            ik.keyframe_insert("influence", frame=fr(t))
        for f in range(fr(a), fr(b) + 1):
            sc.frame_set(f)
            mw = rig.matrix_world
            chest = mw @ rig.pose.bones["spine_03"].matrix
            head = (mw @ rig.pose.bones["head"].matrix).translation
            rz = rig.matrix_world.to_euler().z
            fwd = Vector((-math.sin(rz - math.pi), math.cos(rz - math.pi), 0))   # where the rig faces
            p = head + fwd * reach + Vector((0, 0, -drop))
            tgt.location = p
            tgt.keyframe_insert("location", frame=f)
            d = (head - p).normalized()
            ph.location = p + Vector((0, 0, 0.03))
            ph.rotation_quaternion = d.to_track_quat("-Y", "Z")
            ph.keyframe_insert("location", frame=f)
            ph.keyframe_insert("rotation_quaternion", frame=f)
    show(parts, spans)
    return ph


MY_PHONE = held_in_front("me", [(18.5, 24.5), (62.0, 68.0)])
for _t in (21.0, 65.0):
    sc.frame_set(fr(_t))
    _r = CH["me"].rig
    print("PROBE", _t, "phone", tuple(round(v, 2) for v in MY_PHONE.matrix_world.translation),
          "hand", tuple(round(v, 2) for v in (_r.matrix_world @ _r.pose.bones["hand_r"].matrix).translation),
          "head", tuple(round(v, 2) for v in (_r.matrix_world @ _r.pose.bones["head"].matrix).translation))
# Nina's phone at her ear: her right hand is pulled beside her head by IK, the phone keyed into it
rig_n = CH["nina"].rig
nt_ = P.empty("Nina ear target")
ikn = rig_n.pose.bones["lowerarm_r"].constraints.new("IK")
ikn.target, ikn.chain_count = nt_, 2
nph, nparts = phone_mesh("Nina phone")
E0, E1 = 26.4, 33.2
for t, v in ((0, 0.0), (E0, 0.0), (E0 + 0.7, 1.0), (E1 - 0.3, 1.0), (E1, 0.0)):
    ikn.influence = v
    ikn.keyframe_insert("influence", frame=fr(t))
for f in range(fr(E0), fr(E1) + 1):
    sc.frame_set(f)
    hm_ = rig_n.matrix_world @ rig_n.pose.bones["head"].matrix
    hq = hm_.to_quaternion()
    up = hq @ Vector((0, 1, 0))
    rz = rig_n.matrix_world.to_euler().z
    fwd = Vector((-math.sin(rz - math.pi), math.cos(rz - math.pi), 0))
    right = fwd.cross(Vector((0, 0, 1))).normalized()
    ear = hm_.translation + up * 0.08 + right * 0.1
    u = seg((f - 1) / FPS, E0, E0 + 0.7)
    hand_rest = (rig_n.matrix_world @ rig_n.pose.bones["hand_r"].matrix).translation
    nt_.location = ear + fwd * 0.03 + Vector((0, 0, -0.06))
    nt_.keyframe_insert("location", frame=f)
    nph.location = ear + right * 0.01
    nph.rotation_quaternion = right.to_track_quat("Y", "Z") if False else (-right).to_track_quat("-Y", "Z")
    nph.keyframe_insert("location", frame=f)
    nph.keyframe_insert("rotation_quaternion", frame=f)
show(nparts, [(E0 + 0.6, E1 - 0.2)])
# phone light on my face while I read
ph_light = bpy.data.objects.new("Phone light", bpy.data.lights.new("Phone light", "POINT"))
sc.collection.objects.link(ph_light)
ph_light.data.color = (0.7, 0.8, 1.0)
ph_light.data.shadow_soft_size = 0.05
ph_light.parent = MY_PHONE
ph_light.location = (0, -0.12, 0)
for t, e in ((0, 0), (18.5, 0), (18.8, 6), (24.3, 6), (24.5, 0), (62.0, 0), (62.3, 9), (67.8, 9), (68.0, 0)):
    ph_light.data.energy = e
    ph_light.data.keyframe_insert("energy", frame=fr(t))

# ------------------------------------------------------------------ faces + visibility
WORRY = {"me": [(0, 1.4), (8.6, 1.0), (18.5, 1.6), (33.0, 2.0), (43, 1.4), (62.0, 1.8), (68.0, 2.0)],
         "arian": [(0, 1.6), (6.4, 0.4), (12.0, 1.6), (33.0, 2.0), (43, 1.4), (55, 1.2)],
         "nina": [(0, 0.5), (29.0, 0.9), (33.0, 1.2), (43, 0.8), (56.0, 0.2)],
         "masked": [(0, 0.0)], "masked2": [(0, 0.0)]}
SMILE = {"arian": [(6.4, 0.7), (8.4, 0.0)], "nina": [(56.0, 0.0), (58.9, 0.35), (61.0, 0.0)]}


def curve(pts, t, default=0.0):
    if not pts:
        return default
    v = pts[0][1] if t >= pts[0][0] else default
    for (a, va), (b, vb) in zip(pts, pts[1:] + [(999, pts[-1][1])]):
        if a <= t < b:
            v = va + (vb - va) * seg(t, a, min(b, a + 0.8))
    return v


def present(who, t):
    return any(a <= t < b for a, b in PRESENT[who])


for who, ch in CH.items():
    for f in range(1, N + 1):
        t = (f - 1) / FPS
        st = dict(t=t, seed=ch.seed, worry=curve(WORRY.get(who, []), t), talking=speaking(who, t), zombie=0.0)
        sm = curve(SMILE.get(who, []), t)
        if sm:
            st["smile"] = sm
        sk = ch.body.data.shape_keys
        for k, v in anim.face(st).items():
            if k in ch.keys:
                ch._put(sk, f'key_blocks["{k}"].value', 0, f, max(0.0, min(1.0, v)))
        if f == 1 or present(who, t) != present(who, t - 1 / FPS):
            ch.hide(f, not present(who, t))
    ch.flush()

# ------------------------------------------------------------------ camera: (t0, t1, cam0, cam1, aim0, aim1, lens0, lens1)
SHOTS = [
    (0.0, 6.0, (4.7, 1.0, 1.65), (4.55, 1.15, 1.6), (1.9, 3.4, 1.05), (1.8, 3.4, 1.1), 22, 24),
    (6.0, 11.5, (2.85, 0.45, 1.55), (2.75, 0.5, 1.5), (1.45, 2.4, 1.3), (1.6, 1.9, 1.35), 22, 24),
    (11.5, 18.5, (3.15, 3.85, 1.3), (3.08, 3.72, 1.22), (2.6, 2.7, 0.52), (2.6, 2.7, 0.52), 26, 34),
    (18.5, 24.5, (0.78, 2.42, 1.32), (0.8, 2.47, 1.3), (1.12, 3.0, 1.25), (1.12, 3.0, 1.25), 28, 32),
    (24.5, 33.0, (4.3, 1.1, 1.5), (4.2, 1.2, 1.5), (2.0, 2.8, 1.25), (2.0, 2.7, 1.25), 24, 26),
    (33.0, 38.0, (5.4, 3.9, 1.7), (5.3, 3.7, 1.65), (2.0, 0.2, 1.1), (2.1, 0.2, 1.15), 20, 21),
    (38.0, 43.0, (5.6, 2.6, 1.55), (5.55, 2.9, 1.55), (4.55, 4.9, 1.15), (4.6, 5.3, 1.15), 22, 22),
    (43.0, 50.0, (3.2, 8.2, 1.6), (4.6, 8.9, 1.6), (4.7, 6.0, 1.0), (7.4, 8.9, 1.0), 22, 22),
    (50.0, 55.0, (7.0, 6.4, 1.55), (7.2, 6.8, 1.5), (7.6, 9.6, 1.1), (7.6, 9.8, 1.0), 26, 28),
    (55.0, 62.0, (7.62, 9.2, 1.1), (7.62, 9.3, 1.08), (7.72, 10.4, 0.85), (7.72, 10.4, 0.85), 18, 19),
    (62.0, 68.0, (8.1, 9.68, 0.98), (8.12, 9.72, 0.98), (8.3, 10.3, 0.82), (8.3, 10.3, 0.82), 26, 30),
    (68.0, END, (8.12, 9.72, 0.98), (7.6, 10.35, 1.32), (8.3, 10.3, 0.82), (6.88, 11.22, 1.58), 30, 36),
]
cam = bpy.data.objects.new("Camera", bpy.data.cameras.new("Camera"))
sc.collection.objects.link(cam)
sc.camera = cam
cam.data.clip_start = 0.05
for t0, t1, c0, c1, a0, a1, l0, l1 in SHOTS:
    f0, f1 = fr(t0), fr(t1) - 1
    n = max(1, f1 - f0)
    for f in (list(range(f0, f1, 6)) + [f1]) if t0 == 68.0 else (f0, f1):
        u = (f - f0) / n
        if t0 == 68.0:
            u = seg(u, 0.0, 1.0) * 0.4 + 0.6 * seg(u, 0.35, 1.0)   # holds on us, then pushes to the corner
        c = Vector(c0).lerp(Vector(c1), u)
        a = Vector(a0).lerp(Vector(a1), u)
        cam.location = c
        cam.rotation_euler = (a - c).to_track_quat("-Z", "Y").to_euler()
        cam.keyframe_insert("location", frame=f)
        cam.keyframe_insert("rotation_euler", frame=f)
        cam.data.lens = l0 + (l1 - l0) * u
        cam.data.keyframe_insert("lens", frame=f)
for owner in (cam, cam.data):
    for fc in fcurves_of(owner):
        for k in fc.keyframe_points:
            k.interpolation = "LINEAR"

# ------------------------------------------------------------------ look
sc.frame_set(1)
T.SAT = 0.6                                # fewer, quieter colours (as in «دیوار»)
T.toonify(sc, samples=int(os.environ.get("SAMPLES", "8")))
for o in (led, ):                          # keep the spy LED a pure glowing red
    o.data.materials.clear()
    o.data.materials.append(P.emit("Spy LED 2", (1.0, 0.05, 0.05), 40.0))
# the cel pass flattens image / emission screens to one dull colour: give the screens their glow back
lscr.data.materials.clear()
lscr.data.materials.append(P.image("Laptop screen 2", os.path.join(TEX, "doorcam.png"), strength=1.6))
glow2 = P.emit("Phone glow 2", (0.75, 0.85, 1.0), 5.0)
for o in bpy.data.objects:
    if o.type == "MESH" and o.name.endswith("phone screen") or o.name == "Nina phone screen":
        o.data.materials.clear()
        o.data.materials.append(glow2)
inked = [o for o in bpy.data.objects if o.type == "MESH" and not any(
    k in o.name.lower() for k in ("high-poly", "lash", "brow", "teeth", "tongue", "screen", "led", "floor", "ceiling",
                                  "grass", "street", "rug", "far house", "yard far", "mask eye"))]
T.ink(inked, 0.005)
sc.render.resolution_x, sc.render.resolution_y = 540, 960
sc.render.film_transparent = False

args = sys.argv
if "--spy" in args:                        # the photo the hidden camera sends me: the three of us from behind
    sc.frame_set(fr(60.0))
    spy = bpy.data.objects.new("Spy cam", bpy.data.cameras.new("Spy cam"))
    sc.collection.objects.link(spy)
    spy.location = CAM_AT + Vector((0, -0.06, 0.0))
    spy.rotation_euler = (Vector((7.7, 9.6, 0.6)) - spy.location).to_track_quat("-Z", "Y").to_euler()
    spy.data.lens = 16
    sc.camera = spy
    sc.render.resolution_x, sc.render.resolution_y = 720, 540
    sc.render.filepath = os.path.join(TEX, "spy.png")
    bpy.ops.render.render(write_still=True)
    sc.camera = cam
    sc.render.resolution_x, sc.render.resolution_y = 540, 960
if "--still" in args:
    os.makedirs(os.path.join(HERE, "test"), exist_ok=True)
    for f in [int(v) for v in args[args.index("--still") + 1].split(",")]:
        sc.frame_set(f)
        sc.render.filepath = os.path.join(HERE, "test", f"s_{f:04d}.png")
        bpy.ops.render.render(write_still=True)
if "--save" in args:
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(HERE, "rules_2.blend"))
