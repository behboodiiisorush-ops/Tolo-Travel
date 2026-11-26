"""«هشدار» — a sparrow's eyes are the camera. Comic look (EEVEE cel shading + ink outlines) on the realistic cast,
bodies driven by Mixamo motion capture (same pipeline as blender/wall).

    ../cast/bpy.sh scene.py --still 40,120,...      -> test/s_XXXX.png
    ../cast/bpy.sh scene.py --save                  -> bird.blend (render.py renders from it)
Story (seconds, one continuous flight):
  0.0- 5.8  perched on the roof across the street; Kian comes out on his balcony with bread and calls
  5.8- 8.8  flies across, lands on the balcony rail;  8.8-13.8 pecks the crumbs; mom calls Kian in
 13.6-17.4  a voice down the street: "Mr Rezaei?"; the bird flies to a lamp post
 17.4-22.5  Rezaei turns and attacks the passer-by;  22.5-25.5 the bird flees back to the balcony
 25.5-33.0  hops to the balcony door: Kian on the sofa, mom in the kitchen
 33.0-41.0  back on the rail: Rezaei crosses the street to the building and bangs the entrance door; the buzzer
 41.0-49.0  in the doorway: Kian goes to the intercom, mom says open it
 49.0-53.5  the bird flies into Kian's face (he flinches);  53.5-61 the rail: Kian follows, looks down, Rezaei screams up
"""
import bpy, bmesh, sys, os, math, random
from mathutils import Vector, Matrix, Quaternion
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


def fr(t):
    return int(round(t * FPS)) + 1


def seg(t, a, b):
    if t <= a:
        return 0.0
    if t >= b:
        return 1.0
    u = (t - a) / (b - a)
    return u * u * (3 - 2 * u)


# ------------------------------------------------------------------ materials (re-made after the cast is built)
COLS = dict(
    asphalt=((0.2, 0.2, 0.22), 0.9), line=((0.92, 0.92, 0.88), 0.8), walk=((0.62, 0.6, 0.56), 0.9),
    curb=((0.74, 0.72, 0.68), 0.9), kianb=((0.86, 0.76, 0.6), 0.9), opp=((0.66, 0.72, 0.74), 0.9),
    b1=((0.78, 0.62, 0.52), 0.9), b2=((0.7, 0.7, 0.62), 0.9), b3=((0.6, 0.66, 0.72), 0.9), b4=((0.82, 0.78, 0.7), 0.9),
    b5=((0.64, 0.56, 0.6), 0.9), glass=((0.22, 0.3, 0.38), 0.2), wframe=((0.93, 0.93, 0.9), 0.6),
    roof=((0.45, 0.42, 0.4), 0.9), door=((0.42, 0.3, 0.22), 0.6), rail=((0.2, 0.22, 0.24), 0.4),
    slab=((0.8, 0.78, 0.74), 0.9), inwall=((0.66, 0.76, 0.66), 0.9), infloor=((0.55, 0.4, 0.28), 0.6),
    ceil=((0.9, 0.9, 0.88), 0.9), sofa=((0.3, 0.42, 0.55), 0.9), wood=((0.5, 0.36, 0.24), 0.6),
    counter=((0.9, 0.9, 0.86), 0.4), cab=((0.75, 0.6, 0.42), 0.6), fridge=((0.9, 0.92, 0.92), 0.3),
    rug=((0.62, 0.28, 0.24), 0.95), trunk=((0.36, 0.26, 0.18), 0.9), leaf=((0.36, 0.52, 0.28), 0.9),
    leaf2=((0.42, 0.58, 0.3), 0.9), pole=((0.32, 0.34, 0.36), 0.5), lamp=((0.95, 0.92, 0.8), 0.4),
    car1=((0.62, 0.2, 0.18), 0.4), car2=((0.85, 0.85, 0.82), 0.4), car3=((0.25, 0.32, 0.45), 0.4),
    car4=((0.52, 0.5, 0.46), 0.4), tyre=((0.08, 0.08, 0.08), 0.8), intercom=((0.92, 0.92, 0.88), 0.5),
    btn=((0.15, 0.15, 0.17), 0.5), bread=((0.86, 0.68, 0.4), 0.9), pot=((0.66, 0.36, 0.24), 0.9),
    beak=((0.86, 0.64, 0.25), 0.5), wing=((0.48, 0.34, 0.22), 0.9), wing2=((0.3, 0.22, 0.15), 0.9),
    wingw=((0.85, 0.8, 0.7), 0.9), blood=((0.45, 0.04, 0.04), 0.5), plant=((0.3, 0.5, 0.26), 0.9),
)
M_ = {}


def mats():
    for k, (c, r) in COLS.items():
        M_[k] = P.mat("M " + k, c, r)


mats()
SET = []
_boxes = {}           # material -> [(loc, size, rotz)]  merged into one mesh per material (fast)


def box(loc, size, m, rotz=0.0):
    _boxes.setdefault(m, []).append((Vector(loc), Vector(size), rotz))


def build_boxes():
    for m, items in _boxes.items():
        bm = bmesh.new()
        for loc, size, rz in items:
            mat_ = Matrix.Translation(loc) @ Matrix.Rotation(rz, 4, "Z") @ Matrix.Diagonal((*size, 1))
            bmesh.ops.create_cube(bm, size=1.0, matrix=mat_)
        me = bpy.data.meshes.new("Set " + m)
        bm.to_mesh(me)
        bm.free()
        o = bpy.data.objects.new("Set " + m, me)
        sc.collection.objects.link(o)
        me.materials.append(M_[m])
        SET.append(o)


def cylm(a, b, r, m, name, verts=12):
    o = P.cyl(a, b, r, M_[m], name, verts)
    SET.append(o)
    return o


def sph(loc, r, m, name, scale=(1, 1, 1)):
    o = P.sphere(loc, r, M_[m], name, scale)
    SET.append(o)
    return o


# ------------------------------------------------------------------ the street (along X); road |y|<4, pavements 4..6
SW = 0.12            # pavement height
box((0, 0, -0.05), (100, 8, 0.1), "asphalt")
for x in range(-48, 49, 6):
    box((x, 0, 0.003), (3.0, 0.15, 0.01), "line")
for s in (1, -1):
    box((0, s * 5.0, SW / 2), (100, 2.0, SW), "walk")
    box((0, s * 4.05, SW / 2 + 0.01), (100, 0.12, SW + 0.02), "curb")


def ground(x, y):
    return SW if abs(y) > 4.05 else 0.0


def windows(x0, x1, y, z0, h, floors, face=-1, skip=()):
    """Window grid on a facade at y (face -1: the facade looks towards -Y)."""
    n = max(1, int((x1 - x0) / 2.8))
    for fl in range(floors):
        for i in range(n):
            x = x0 + (i + 0.5) * (x1 - x0) / n
            if (fl, i) in skip:
                continue
            z = z0 + fl * 3.2 + 1.0
            box((x, y + face * 0.02, z + 0.7), (1.2, 0.04, 1.4), "glass")
            box((x, y + face * 0.04, z + 0.7), (1.32, 0.03, 0.07), "wframe")
            box((x, y + face * 0.04, z), (1.4, 0.12, 0.07), "wframe")          # sill
            box((x, y + face * 0.04, z + 1.42), (1.32, 0.03, 0.07), "wframe")
            for dx in (-0.63, 0, 0.63):
                box((x + dx, y + face * 0.04, z + 0.7), (0.06, 0.03, 1.4), "wframe")


def block(x0, x1, y_face, height, m, side):
    """A building: facade at y_face, `side` +1 = the building extends towards +Y (north row)."""
    d = 12
    box(((x0 + x1) / 2, y_face + side * d / 2, height / 2), (x1 - x0 - 0.05, d, height), m)
    box(((x0 + x1) / 2, y_face + side * 0.05, height + 0.2), (x1 - x0 - 0.05, 0.3, 0.4), "roof")      # parapet
    box(((x0 + x1) / 2, y_face + side * d / 2, height + 0.02), (x1 - x0 - 0.3, d - 0.3, 0.04), "roof")
    windows(x0, x1, y_face, 0, 0, int(height / 3.2), face=-side)


for x0, x1, h, m in ((-48, -28, 15.0, "b1"), (-28, -17, 12.0, "b3"), (-17, -6.05, 10.5, "b4"),
                     (6.05, 16, 12.0, "b5"), (16, 27, 15.0, "b2"), (27, 48, 10.0, "b1")):
    block(x0, x1, 6.0, h, m, 1)
for x0, x1, h, m in ((-48, -25, 12.0, "b2"), (-25, -8, 13.5, "b5"), (-8, 8, 9.0, "opp"),
                     (8, 20, 11.0, "b4"), (20, 32, 14.0, "b3"), (32, 48, 10.0, "b1")):
    block(x0, x1, -6.0, h, m, -1)
for x in (-49, 49):                      # the street ends in buildings both ways
    box((x, 0, 8), (2, 40, 16), "b4")

# ---- Kian's building: x -6..6, facade y 6..6.2, floors 3.2 m, his flat on the first floor (z 3.2)
F = 3.2
KX0, KX1, KY = -6.0, 6.0, 6.0
DX0, DX1, DZ1 = -0.6, 0.6, F + 2.2              # balcony door hole
box((0, KY + 0.1, F / 2), (12, 0.2, F), "kianb")
box((0, KY + 0.1, (DZ1 + 9.6) / 2), (12, 0.2, 9.6 - DZ1), "kianb")
box(((KX0 + DX0) / 2, KY + 0.1, (F + DZ1) / 2), (DX0 - KX0, 0.2, DZ1 - F), "kianb")
box(((KX1 + DX1) / 2, KY + 0.1, (F + DZ1) / 2), (KX1 - DX1, 0.2, DZ1 - F), "kianb")
for s in (-1, 1):                                # side and back of the block (outside the flat)
    box((s * 5.1, KY + 6.1, 4.8), (1.8, 11.8, 9.6), "kianb")
box((0, KY + 11.5, 4.8), (8.4, 1.0, 9.6), "kianb")
box((0, KY + 3, 1.55), (8.4, 5.6, 3.1), "kianb")                 # ground floor (solid, the flat sits on top)
box((0, KY + 6.1, 7.9), (8.4, 11.8, 3.4), "kianb")               # upper floor
box((0, KY + 0.05, 9.8), (12, 0.3, 0.4), "roof")
box((0, KY + 6, 9.62), (11.7, 11.7, 0.04), "roof")
# facade windows (ground floor left of the entrance, first floor around the balcony, top floor)
for x in (-3.8, -0.4):
    box((x, KY - 0.02, 1.7), (1.2, 0.04, 1.4), "glass")
    box((x, KY - 0.04, 1.0), (1.4, 0.12, 0.07), "wframe")
    box((x, KY - 0.04, 2.42), (1.32, 0.03, 0.07), "wframe")
    for dx in (-0.63, 0, 0.63):
        box((x + dx, KY - 0.04, 1.7), (0.06, 0.03, 1.4), "wframe")
for x in (-3.6, 3.6):
    box((x, KY - 0.02, F + 1.6), (1.2, 0.04, 1.3), "glass")
    box((x, KY - 0.04, F + 0.9), (1.4, 0.12, 0.07), "wframe")
    for dx in (-0.63, 0, 0.63):
        box((x + dx, KY - 0.04, F + 1.6), (0.06, 0.03, 1.3), "wframe")
for x in (-3.6, 0, 3.6):
    box((x, KY - 0.02, 2 * F + 1.6), (1.2, 0.04, 1.3), "glass")
    box((x, KY - 0.04, 2 * F + 0.9), (1.4, 0.12, 0.07), "wframe")
    for dx in (-0.63, 0, 0.63):
        box((x + dx, KY - 0.04, 2 * F + 1.6), (0.06, 0.03, 1.3), "wframe")
# balcony door frame (the door leaf stands open against the inside wall)
for x in (DX0, DX1):
    box((x, KY + 0.1, (F + DZ1) / 2), (0.08, 0.24, DZ1 - F), "wframe")
box((0, KY + 0.1, DZ1), (1.28, 0.24, 0.08), "wframe")
# entrance door (ground floor, x 3.0) + step + outside intercom panel
ENT = (3.0, KY)
box((3.0, KY - 0.01, SW + 1.15), (1.2, 0.06, 2.3), "door")
for x in (2.36, 3.64):
    box((x, KY - 0.04, SW + 1.2), (0.1, 0.1, 2.4), "wframe")
box((3.0, KY - 0.04, SW + 2.42), (1.38, 0.1, 0.1), "wframe")
box((3.0, KY - 0.25, SW + 0.06), (1.6, 0.5, 0.12), "slab")
box((3.45, KY - 0.03, SW + 1.05), (0.04, 0.03, 0.3), "rail")       # handle
box((4.0, KY - 0.03, SW + 1.35), (0.18, 0.04, 0.3), "intercom")
for k in range(4):
    box((4.0, KY - 0.055, SW + 1.25 + k * 0.06), (0.06, 0.01, 0.03), "btn")
# balcony: slab y 4.8..6, rail top at z 4.2
BY0 = 4.8
box((0, (BY0 + KY) / 2, F - 0.1), (3.0, KY - BY0, 0.2), "slab")
RAIL_Z = F + 1.0
box((0, BY0 + 0.05, RAIL_Z), (3.0, 0.06, 0.05), "rail")
for s in (-1, 1):
    box((s * 1.47, (BY0 + KY) / 2, RAIL_Z), (0.06, KY - BY0, 0.05), "rail")
for i in range(26):
    x = -1.47 + i * 2.94 / 25
    box((x, BY0 + 0.05, (F + RAIL_Z) / 2), (0.025, 0.025, 1.0), "rail")
for i in range(1, 10):
    y = BY0 + i * (KY - BY0) / 10
    for s in (-1, 1):
        box((s * 1.47, y, (F + RAIL_Z) / 2), (0.025, 0.025, 1.0), "rail")
box((-1.15, 5.7, F + 0.2), (0.4, 0.4, 0.4), "pot")
sph((-1.15, 5.7, F + 0.62), 0.32, "plant", "Balcony plant")
# ---- the flat behind the balcony door: x -4..4, y 6.2..11, z 3.2..6.1
IY0, IY1, IZ1 = KY + 0.2, 11.0, 6.1
box((0, (IY0 + IY1) / 2, F - 0.05), (8, IY1 - IY0, 0.1), "infloor")
box((0, (IY0 + IY1) / 2, IZ1 + 0.05), (8, IY1 - IY0, 0.1), "ceil")
for s in (-1, 1):
    box((s * 4.05, (IY0 + IY1) / 2, (F + IZ1) / 2), (0.1, IY1 - IY0, IZ1 - F), "inwall")
box((0, IY1 + 0.05, (F + IZ1) / 2), (8, 0.1, IZ1 - F), "inwall")
box((0, IY0 + 0.03, (F + IZ1) / 2), (7.9, 0.04, IZ1 - F), "inwall")    # inside face of the facade...
box((0, IY0 + 0.03, (F + DZ1) / 2), (1.3, 0.1, DZ1 - F), "door")      # ...cut back by the door (see below)
_boxes["inwall"].pop()
_boxes["door"].pop()
box(((-4 + DX0) / 2, IY0 + 0.03, (F + IZ1) / 2), (DX0 + 4, 0.04, IZ1 - F), "inwall")
box(((4 + DX1) / 2, IY0 + 0.03, (F + IZ1) / 2), (4 - DX1, 0.04, IZ1 - F), "inwall")
box((0, IY0 + 0.03, (DZ1 + IZ1) / 2), (1.2, 0.04, IZ1 - DZ1), "inwall")
# kitchen along the back wall (left), fridge, sofa + table + rug (right), a picture-less shelf
box((-2.3, 10.7, F + 0.45), (3.0, 0.6, 0.9), "cab")
box((-2.3, 10.7, F + 0.92), (3.1, 0.66, 0.05), "counter")
box((-3.55, 10.65, F + 0.95), (0.8, 0.7, 1.9), "fridge")
box((-2.3, 10.95, F + 1.9), (3.0, 0.3, 0.7), "cab")
box((2.1, 9.55, F + 0.22), (2.2, 0.85, 0.44), "sofa")
box((2.1, 9.95, F + 0.6), (2.2, 0.22, 0.85), "sofa")
for s in (-1, 1):
    box((2.1 + s * 1.15, 9.55, F + 0.35), (0.22, 0.85, 0.7), "sofa")
box((2.1, 8.3, F + 0.2), (1.1, 0.6, 0.4), "wood")
box((1.0, 8.6, F + 0.005), (3.4, 2.4, 0.01), "rug")
box((3.7, 8.0, F + 1.6), (0.3, 1.6, 0.06), "wood")
# intercom handset beside the balcony door, inside
ICOM = Vector((-1.7, IY0 + 0.08, F + 1.38))
box(tuple(ICOM), (0.14, 0.06, 0.24), "intercom")
box(tuple(ICOM + Vector((0, 0.035, -0.07))), (0.04, 0.02, 0.03), "btn")
# ---- trees, lamp posts, parked cars
for x, y in ((-8, 5.1), (8.5, 5.1), (17, 5.1), (-12, -5.1), (4.5, -5.1), (19, -5.1), (-22, 5.1), (-26, -5.1)):
    cylm((x, y, SW), (x, y, 3.0), 0.12, "trunk", "Tree trunk")
    r = random.Random(int(x * 7 + y))
    for k in range(4):
        sph((x + r.uniform(-0.6, 0.6), y + r.uniform(-0.6, 0.6), 3.4 + r.uniform(0, 1.0)), r.uniform(0.9, 1.3),
            "leaf" if k % 2 else "leaf2", "Tree leaves")
LAMP = (12.3, -4.6)
for x, y in (LAMP, (-6.0, -4.6), (-20, 4.6), (24, 4.6)):
    s = 1 if y > 0 else -1
    cylm((x, y, SW), (x, y, 5.0), 0.07, "pole", "Lamp pole")
    cylm((x, y, 5.0), (x, y - s * 0.7, 5.0), 0.05, "pole", "Lamp arm")
    box((x, y - s * 0.75, 4.97), (0.25, 0.45, 0.1), "pole")
    box((x, y - s * 0.75, 4.91), (0.2, 0.38, 0.03), "lamp")
LAMP_TOP = Vector((LAMP[0], LAMP[1] + 0.75, 5.02))


def car(x, y, m, rz=0.0):
    box((x, y, 0.55), (4.0, 1.75, 0.6), m)
    box((x - 0.2, y, 1.1), (2.2, 1.6, 0.55), m)
    box((x - 0.2, y, 1.1), (2.0, 1.64, 0.4), "glass")
    for dx in (-1.3, 1.3):
        for dy in (-0.88, 0.88):
            cylm((x + dx, y + dy - 0.1, 0.33), (x + dx, y + dy + 0.1, 0.33), 0.32, "tyre", "Tyre", 14)


for x, y, m in ((-9.5, 3.0, "car1"), (13.0, 3.0, "car3"), (21.5, 3.0, "car2"), (-17, 3.0, "car4"),
                (-6.0, -3.0, "car2"), (-15, -3.0, "car3"), (5.5, -3.0, "car4"), (22, -3.0, "car1")):
    car(x, y, m)
build_boxes()

# crumbs on the rail (they vanish when they are pecked)
CRUMBS = [Vector((0.42 + 0.07 * k, BY0 + 0.05 + 0.01 * (k % 2 - 0.5), RAIL_Z + 0.03)) for k in range(5)]
crumb_objs = [sph(tuple(c), 0.006 + 0.002 * (k % 2), "bread", f"Crumb {k}") for k, c in enumerate(CRUMBS)]

# light: low morning sun, sky, the flat's ceiling lamp
sun = bpy.data.objects.new("Sun", bpy.data.lights.new("Sun", "SUN"))
sc.collection.objects.link(sun)
sun.data.energy = 3.2
sun.data.use_shadow = True
sun.rotation_euler = (math.radians(55), 0, math.radians(-150))
lamp_in = P.area_light((0, 8.6, IZ1 - 0.05), (0, 8.6, 0), 60, 3.0, (1.0, 0.9, 0.75), name="Flat lamp")
w = bpy.data.worlds.new("W")
sc.world = w
w.color = (0.55, 0.72, 0.92)
w.use_nodes = True
_bg = [n for n in w.node_tree.nodes if n.type == "BACKGROUND"][0]
_bg.inputs[0].default_value = (0.42, 0.62, 0.88, 1)
_bg.inputs[1].default_value = 1.0

# ------------------------------------------------------------------ cast
KEYS = ["kian", "mom", "rezaei"]
CH = {}
for k in KEYS:
    ch = cast.spawn(k, zombie=1.0) if k == "rezaei" else cast.spawn(k)
    if k != "rezaei":                        # Rezaei keeps his zombie textures (veins, blood) under the cel bands
        T.register(ch, k, realistic=True)
    CH[k] = ch
pb_def = cast.extra_def("passerby", 2)
pb = cast.spawn_extra("passerby", 2)
CH["passerby"] = pb
T.SKIN[pb.name] = (tuple(c * 0.78 for c in pb_def.get("skin_tint", cast.WARM)),
                   {k: v for k, v in pb_def.get("clothes", {}).items() if v})
skin, clothes = T.SKIN[CH["mom"].name]
clothes = dict(clothes)
for kk in list(clothes):
    if "sweater" in kk:
        clothes[kk] = (0.55, 0.16, 0.22)          # cream reads as bare skin in the flat look
T.SKIN[CH["mom"].name] = (skin, clothes)
_cel = T.cel


def _cel_keep(m, shine=0.0, flat=None, keep_tex=False):
    if m.name.startswith(CH["rezaei"].name + ".") and flat is None:
        keep_tex = True
    return _cel(m, shine=shine, flat=flat, keep_tex=keep_tex)


T.cel = _cel_keep
mats()                                         # building the cast purged unused datablocks
CLIP = {}


def clip(name):
    if name not in CLIP:
        CLIP[name] = mocap.load(os.path.join(MOC, name + ".fbx"))
    return CLIP[name]


LASTSEG = {}


def face(p, q):
    """facing (degrees, 0 = +Y, 90 = -X) from p towards q."""
    return math.degrees(math.atan2(-(q[0] - p[0]), q[1] - p[1]))


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


def walk(who, t0, t1, pts, f_from, f_to, z=None, cyc="walking", spd=1.3):
    """Walk along pts (cycle in place, the rig carried along the path), turning from f_from into f_to."""
    pts = [Vector((p[0], p[1])) for p in pts]
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
        uu = u * u * (3 - 2 * u) * 0.35 + u * 0.65
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
        return (p.x, p.y, ground(p.x, p.y) if z is None else z), fac
    v = L / dur
    mocap.apply(CH[who], clip(cyc), start=fr(t0), length=n, in_place=True, loop=True,
                speed=max(0.5, min(1.5, v / spd)), place=place, blend=8)
    LASTSEG[who] = t1


def act(who, name, t0, t1, pos, facing, follow=None, turn=0.0, via=None, cyc="walking", spd=1.3, **kw):
    """`who` plays clip `name` from t0 to t1 at pos/facing; if he was somewhere else he first walks there
    (cycle `cyc`, through the points `via`)."""
    rig = CH[who].rig
    in_shot = LASTSEG.get(who) == t0
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
            pts = [hips_prev.xy] + [Vector(v) for v in (via or [])] + [Vector((pos[0], pos[1]))]
            L = sum((b - a).length for a, b in zip(pts, pts[1:]))
            tw = min(max(0.7, L / 1.25), 0.75 * (t1 - t0)) if "walk_t" not in kw else kw.pop("walk_t")
            walk(who, t0, t0 + tw, pts, math.degrees(old_rz - math.pi), facing, z=pos[2] if pos[2] > 1 else None,
                 cyc=cyc, spd=spd)
            return act(who, name, t0 + tw, t1, pos, facing, turn=0.3, **kw)
    kw.pop("walk_t", None)
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


# ---- Kian: out on the balcony with bread, back in to breakfast, to the intercom, then out to the rail
KB = (-0.25, 5.35, F)               # his place at the balcony rail
SOFA = (2.1, 9.25, F + 0.02)
KI = (-1.7, IY0 + 0.55, F)          # in front of the intercom
act("kian", "breathing_idle", 0.0, 0.6, (0.0, 7.6, F), 180)
act("kian", "reloading", 0.6, 3.0, KB, 175, walk_t=1.2)                   # crumbling the bread
act("kian", "hands_forward_gesture", 3.0, 6.0, KB, 185, src_from=0.2, speed=0.9)   # "come, little bird"
act("kian", "breathing_idle", 6.0, 12.8, KB, 215, src_from=2.0)
act("kian", "sitting_idle", 12.8, 41.4, SOFA, 180, via=[(0.0, 6.9), (2.1, 8.0)], walk_t=2.6, loop=True)
act("kian", "breathing_idle", 41.4, 48.8, KI, 180, via=[(1.0, 8.6), (-1.4, 7.4)], walk_t=2.4)
act("kian", "hands_forward_gesture", 48.8, 49.7, KI, 180, src_from=0.0, speed=1.0)  # reaching for the button
act("kian", "pushing_2", 49.7, 53.6, (KI[0] + 0.05, KI[1] + 0.3, F), 180, src_from=0.0, speed=0.7)
act("kian", "breathing_idle", 53.6, 61.0, (0.15, 5.32, F), 185, via=[(-0.4, 6.9), (0.0, 6.0)], walk_t=2.3)
# ---- mom in the kitchen (her back to the door; she turns to answer)
act("mom", "reloading", 0.0, 10.6, (-2.2, 10.15, F), 0, loop=True, in_place=True)
act("mom", "breathing_idle", 10.6, 12.8, (-2.2, 10.15, F), 150, turn=0.5)
act("mom", "reloading", 12.8, 46.6, (-2.2, 10.15, F), 0, loop=True, turn=0.5, in_place=True)
act("mom", "breathing_idle", 46.6, 50.0, (-2.2, 10.1, F), 165, turn=0.5)
act("mom", "reloading", 50.0, 61.0, (-2.2, 10.15, F), 0, loop=True, turn=0.6, in_place=True)
# ---- the passer-by walks up behind Rezaei, is knocked down
PB0 = (19.5, -5.0, SW)
act("passerby", "breathing_idle", 0.0, 12.0, PB0, 90)
act("passerby", "hands_forward_gesture", 12.0, 17.8, (15.2, -5.05, SW), 85, walk_t=3.0, src_from=0.0, speed=0.6)
act("passerby", "getting_smashed", 17.8, 61.0, (15.2, -5.05, SW), 90, follow=False)
# ---- Rezaei: hunched on the pavement, turns, attacks, eats, then crosses to Kian's building
RZ0 = (14.3, -5.1, SW)
act("rezaei", "zombie_idle", 0.0, 17.4, RZ0, 90, loop=True)
act("rezaei", "zombie_attack", 17.4, 20.0, RZ0, -90, turn=0.3, follow=False)
sc.frame_set(fr(20.0))
_pp = (CH["passerby"].rig.matrix_world @ CH["passerby"].rig.pose.bones["pelvis"].matrix).translation
print("PASSERBY DOWN AT", tuple(round(v, 2) for v in _pp))
act("rezaei", "zombie_biting", 20.0, 27.0, (_pp.x - 0.8, _pp.y, SW), -90, follow=False)
DOORP = (3.0, KY - 0.75, SW)
act("rezaei", "zombie_attack", 27.0, 42.0, DOORP, 0, cyc="zombie_walk", spd=0.9, via=[(9.5, -1.0)], walk_t=12.0,
    loop=True)
act("rezaei", "zombie_idle", 42.0, 54.0, DOORP, 0, loop=True)
RZE = (2.4, 3.1, 0.0)
act("rezaei", "zombie_idle", 54.0, 56.6, RZE, face(RZE, (0.0, 5.2)), cyc="zombie_walk", spd=0.9, walk_t=1.8)
act("rezaei", "zombie_scream", 56.6, 61.0, RZE, face(RZE, (0.0, 5.2)), speed=0.9)

for _ch in CH.values():
    for fc in fcurves_of(_ch.rig):
        if fc.data_path in ("location", "rotation_euler"):
            for kp in fc.keyframe_points:
                kp.interpolation = "CONSTANT"

for _t in (5, 15, 18, 22, 28, 34, 38, 43, 50, 58):
    sc.frame_set(fr(_t))
    print("POS", _t, {k: tuple(round(v, 2) for v in (c.rig.matrix_world @ c.rig.pose.bones["pelvis"].matrix).translation)
                     for k, c in CH.items()})
# who is where (hidden when the bird can't see them: saves render time)
PRESENT = {"kian": [(0, 61)], "mom": [(24.5, 61)], "rezaei": [(0, 61)], "passerby": [(0, 41.5)]}
WORRY = {"kian": [(0, 0.0), (13.6, 0.3), (44, 0.6), (49.7, 2.0), (55, 1.6), (56.5, 2.0)],
         "mom": [(0, 0.0)], "passerby": [(0, 0.2), (13.6, 0.6), (17.6, 2.0)], "rezaei": [(0, 0.0)]}
SMILE = {"kian": [(0, 0.3), (3.0, 0.7), (6, 0.8), (12.8, 0.4), (44, 0.0)], "mom": [(0, 0.2)],
         "passerby": [(0, 0.0)], "rezaei": [(0, 0.0)]}


def curve(pts, t):
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
        st = dict(t=t, seed=ch.seed, worry=curve(WORRY[who], t), talking=speaking(who, t), zombie=ch.zombie,
                  smile=curve(SMILE[who], t))
        if who == "rezaei":
            st["scream"] = max(0.6 * seg(t, 17.4, 17.8) * (1 - seg(t, 19.5, 20.0)), seg(t, 56.8, 57.6))
        if who == "passerby":
            st["scream"] = 0.7 * seg(t, 17.9, 18.2) * (1 - seg(t, 20.0, 21.0))
        sk = ch.body.data.shape_keys
        for k, v in anim.face(st).items():
            if k in ch.keys:
                ch._put(sk, f'key_blocks["{k}"].value', 0, f, max(0.0, min(1.0, v)))
        if f == 1 or present(who, t) != present(who, t - 1 / FPS):
            ch.hide(f, not present(who, t))
    ch.flush()


def key_vis(o, pts):
    for t, v in pts:
        f = max(1, fr(t)) if t > 0 else 1
        o.hide_render = not v
        o.keyframe_insert("hide_render", frame=f)
    for fc in fcurves_of(o):
        if fc.data_path == "hide_render":
            for k in fc.keyframe_points:
                k.interpolation = "CONSTANT"


# bread in Kian's hands while he crumbles it
mats()
sc.frame_set(fr(1.6))
_kr = CH["kian"].rig
_hm = _kr.matrix_world @ _kr.pose.bones["hand_r"].matrix
bread = P.sphere(_hm.translation, 0.045, M_["bread"], "Bread", (1.4, 1.0, 0.8))
SET.append(bread)
con = bread.constraints.new("CHILD_OF")
con.target, con.subtarget = _kr, "hand_r"
con.inverse_matrix = _hm.inverted()
key_vis(bread, [(0, True), (6.0, False)])
key_vis(crumb_objs[0], [(0, False)])
for k, c in enumerate(crumb_objs):
    key_vis(c, [(0, False), (2.4, True)])

# ------------------------------------------------------------------ the bird: camera = its eyes
EYE_H = 0.07                     # eye above the feet
RAILP = Vector((0.85, BY0 - 0.03, RAIL_Z + 0.025 + EYE_H))
ROOFP = Vector((-1.0, -5.92, 9.4 + EYE_H))
LAMPP = LAMP_TOP + Vector((0.11, 0, EYE_H))
DOORS = Vector((0.0, IY0 + 0.12, F + EYE_H))          # on the door sill
KFACE = lambda: head_of("kian")  # noqa: E731


def head_of(who, t=None):
    rig = CH[who].rig
    return (rig.matrix_world @ rig.pose.bones["head"].matrix).translation + Vector((0, 0, 0.06))


def V(*a):
    return Vector(a)


# perches: (t0, t1, place, [(t, look target or ("head", who) or "crumb k"), ...], pecks [t])
# flights: (t0, t1, [points], look target or None (= along the flight))
PLAN = [
    ("perch", 0.0, 5.8, ROOFP, [(0.0, V(0.0, 5.0, 3.6)), (1.4, V(-0.3, 5.6, 4.3)), (2.6, V(3, 0, 0.5)),
                                (2.9, ("head", "kian")), (4.6, V(-0.3, 5.0, 3.8)), (5.3, V(0.4, 3.0, 4.6))], []),
    ("fly", 5.8, 8.8, [ROOFP, V(-0.6, -3.5, 8.2), V(0.2, 0.5, 6.0), V(0.7, 3.4, 4.7), RAILP], None),
    ("perch", 8.8, 13.9, RAILP, [(8.8, ("head", "kian")), (9.6, "crumb"), (11.0, ("head", "kian")),
                                 (11.6, V(-1.0, 9.0, 4.0)), (12.2, "crumb"), (13.0, ("head", "kian")),
                                 (13.75, V(14.5, -5.0, 1.0))], [9.7, 10.15, 10.55, 12.3, 12.7]),
    ("fly", 13.9, 17.4, [RAILP, V(2.5, 3.2, 5.2), V(6.5, -0.5, 6.3), V(9.6, -3.0, 5.6), LAMPP], V(14.3, -5.0, 1.0)),
    ("perch", 17.4, 22.6, LAMPP, [(17.4, ("head", "passerby")), (17.9, V(14.8, -5.0, 1.1)), (19.4, V(15.0, -5.0, 0.6)),
                                  (20.6, V(15.4, -5.0, 0.4)), (21.8, ("head", "rezaei"))], []),
    ("fly", 22.6, 25.6, [LAMPP, V(8.5, -2.6, 6.4), V(4.5, 1.0, 5.9), V(1.8, 3.6, 4.8), RAILP], None),
    ("perch", 25.6, 27.0, RAILP, [(25.6, V(-0.3, 5.3, 4.0)), (26.2, V(0.0, 7.5, 4.0)), (26.7, V(0.0, 6.5, 3.4))], []),
    ("fly", 27.0, 27.7, [RAILP, V(0.5, 5.4, 4.0), DOORS], V(0.3, 9.0, 3.6)),
    ("perch", 27.7, 33.0, DOORS, [(27.7, ("head", "kian")), (29.2, ("head", "mom")), (30.6, V(1.5, 8.2, 3.6)),
                                  (31.4, ("head", "kian")), (32.6, V(0.0, 4.0, 3.6))], []),
    ("fly", 33.0, 33.7, [DOORS, V(0.5, 5.4, 3.9), RAILP], V(4.0, 0.0, 2.0)),
    ("perch", 33.7, 41.0, RAILP, [(33.7, V(12.0, -4.5, 0.6)), (34.4, ("head", "rezaei")), (39.6, V(3.0, 5.6, 1.0)), (40.6, V(0.0, 7.0, 3.8))], []),
    ("fly", 41.0, 41.7, [RAILP, V(0.5, 5.4, 4.0), DOORS], V(-0.8, 9.0, 3.8)),
    ("perch", 41.7, 49.0, DOORS, [(41.7, ("head", "kian")), (44.0, ("head", "kian")), (45.8, ("head", "mom")),
                                  (47.0, ("head", "mom")), (48.4, ("head", "kian"))], []),
    ("fly", 49.0, 49.8, [DOORS, V(-0.7, 6.4, 3.8), V(-1.6, IY0 + 0.2, F + 1.15)], ("head", "kian")),
    ("hover", 49.8, 52.6, V(-1.62, IY0 + 0.2, F + 1.12), ("head", "kian")),
    ("fly", 52.6, 54.0, [V(-1.62, IY0 + 0.2, F + 1.12), V(-1.0, 7.0, 4.6), V(0.0, 6.0, 4.7), V(0.6, 5.2, 4.5), RAILP],
     None),
    ("perch", 54.0, 61.0, RAILP, [(54.0, V(0.0, 7.0, 4.2)), (55.0, ("head", "kian")), (56.4, ("head", "rezaei")),
                                  (58.6, ("head", "kian")), (59.6, ("head", "rezaei"))], []),
]


def resolve(tg):
    if isinstance(tg, tuple) and tg and tg[0] == "head":
        return head_of(tg[1])
    return Vector(tg)


def catmull(pts, u):
    n = len(pts) - 1
    s = min(n - 1e-6, max(0.0, u * n))
    i = int(s)
    f = s - i
    p0 = pts[max(0, i - 1)]
    p1, p2 = pts[i], pts[i + 1]
    p3 = pts[min(n, i + 2)]
    return 0.5 * ((2 * p1) + (-p0 + p2) * f + (2 * p0 - 5 * p1 + 4 * p2 - p3) * f * f + (-p0 + 3 * p1 - 3 * p2 + p3) * f ** 3)


def state(t):
    """(position, look target or None, flap 0..1) of the bird at time t."""
    for s in PLAN:
        if s[1] <= t < s[2] or (s is PLAN[-1] and t >= s[1]):
            break
    kind = s[0]
    if kind == "perch":
        _, t0, t1, pos, looks, pecks = s
        lk = [l for l in looks if l[0] <= t]
        tg = lk[-1][1] if lk else looks[0][1]
        p = pos.copy()
        peck = 0.0
        for tp in pecks:
            if tp <= t < tp + 0.32:
                peck = math.sin(math.pi * (t - tp) / 0.32)
        if tg == "crumb" or peck > 0:
            c = [c for k, c in enumerate(CRUMBS) if not crumb_gone(k, t)]
            tg = c[0] if c else CRUMBS[-1]
        p += Vector((0, 0, -0.04 * peck))
        if peck > 0:
            p = p.lerp(Vector(tg) + Vector((0, 0, 0.03)), 0.35 * peck)
        return p, ("snap", resolve(tg) if tg != "crumb" else Vector(tg)), 0.0
    if kind == "hover":
        _, t0, t1, pos, tg = s
        r = random.Random(int(t * 24))
        j = Vector((r.uniform(-1, 1), r.uniform(-0.4, 0.4), r.uniform(-1, 1))) * 0.03
        return pos + j + Vector((0.06 * math.sin(t * 9), 0, 0.05 * math.sin(t * 13))), ("snap", resolve(tg)), 1.4
    _, t0, t1, pts, tg = s
    u = (t - t0) / (t1 - t0)
    ue = u * u * (3 - 2 * u) * 0.5 + u * 0.5
    p = catmull(pts, ue)
    flap = 1.0 if u < 0.35 or u > 0.75 else 0.45            # flap on take-off and landing, glide in between
    if tg is None:
        q = catmull(pts, min(1.0, ue + 0.06))
        if u > 0.85:                                         # landing: look where it is landing
            q = pts[-1] + (pts[-1] - pts[-2]).normalized() * 0.6
            q.z = pts[-1].z - 0.1
        return p, ("fly", q), flap
    return p, ("fly", resolve(tg)), flap


PECKED = {}                                   # crumb k -> time it is eaten


def crumb_gone(k, t):
    return k in PECKED and t >= PECKED[k]


for i, tp in enumerate(PLAN[2][5]):
    PECKED[i] = tp + 0.16

cam = bpy.data.objects.new("Camera", bpy.data.cameras.new("Camera"))
sc.collection.objects.link(cam)
sc.camera = cam
cam.data.clip_start = 0.01
cam.data.lens = 14
cam.data.sensor_width = 36
cam.rotation_mode = "QUATERNION"
d_prev = None
p_prev = None
yaw_prev = None
roll_s = 0.0
FLAP = {}
rng = random.Random(3)
for f in range(1, N + 1):
    t = (f - 1) / FPS
    sc.frame_set(f)
    p, (mode, tg), flap = state(t)
    FLAP[f] = flap
    d = (tg - p)
    if d.length < 1e-4:
        d = Vector((0, 1, 0))
    d.normalize()
    if d_prev is None:
        d_prev = d
    k = 0.55 if mode == "snap" else 0.25        # birds snap their heads; in flight the look follows smoothly
    d_prev = d_prev.lerp(d, k).normalized()
    yaw = math.atan2(d_prev.y, d_prev.x)
    if yaw_prev is not None and mode == "fly":
        dy = (yaw - yaw_prev + math.pi) % (2 * math.pi) - math.pi
        roll_s = roll_s * 0.85 + max(-0.6, min(0.6, -dy * 9)) * 0.15        # bank into the turn
    else:
        roll_s *= 0.8
    yaw_prev = yaw
    q = d_prev.to_track_quat("-Z", "Y")
    q = q @ Quaternion((0, 0, 1), roll_s)
    bob = Vector((0, 0, 0.025 * flap * math.sin(2 * math.pi * 5.0 * t)))
    cam.location = p + bob
    cam.rotation_quaternion = q
    cam.keyframe_insert("location", frame=f)
    cam.keyframe_insert("rotation_quaternion", frame=f)
for fc in fcurves_of(cam):
    for kp in fc.keyframe_points:
        kp.interpolation = "LINEAR"
for k, c in enumerate(crumb_objs):
    key_vis(c, [(0, False), (2.4, True), (PECKED.get(k, 999), False)])

# beak (bottom centre of the view) and wings (sweep into the lower corners on every downstroke)
mats()
bm = bmesh.new()
bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=0.0035, radius2=0.0, depth=0.016,
                      matrix=Matrix.Translation((0, 0, -0.008)) @ Matrix.Rotation(math.pi, 4, "X"))
me_ = bpy.data.meshes.new("Beak")
bm.to_mesh(me_)
bm.free()
beak = bpy.data.objects.new("Beak", me_)
sc.collection.objects.link(beak)
me_.materials.append(M_["beak"])
beak.parent = cam
beak.location = (0, -0.0215, -0.011)
beak.rotation_euler = (math.radians(-12), 0, 0)


def wing_mesh(side):
    """Flat wing in the camera's XZ plane going out along side*X: covert feathers + long primaries."""
    bm = bmesh.new()
    outline = [(0.0, 0.03), (0.06, 0.05), (0.15, 0.04), (0.24, 0.0), (0.3, -0.05), (0.22, -0.07),
               (0.12, -0.09), (0.03, -0.08), (0.0, -0.04)]
    vs = [bm.verts.new((side * x, 0.0, -z - 0.02)) for x, z in outline]
    bm.faces.new(vs if side > 0 else vs[::-1])
    for k in range(5):                                            # primaries (darker), splayed at the tip
        a = math.radians(-25 + k * 12)
        base = Vector((0.2 + 0.015 * k, 0, -0.03 - 0.012 * k))
        tip = base + Vector((math.cos(a), 0, -math.sin(a) - 0.4)) * 0.11
        v = [bm.verts.new((side * base.x, 0.001, base.z + 0.012)), bm.verts.new((side * tip.x, 0.001, tip.z)),
             bm.verts.new((side * (base.x + 0.01), 0.001, base.z - 0.012))]
        bm.faces.new(v if side > 0 else v[::-1])
    me = bpy.data.meshes.new("Wing")
    bm.to_mesh(me)
    bm.free()
    me.materials.append(M_["wing"])
    me.materials.append(M_["wing2"])
    for poly in me.polygons:
        poly.material_index = 1 if poly.index > 0 else 0
    o = bpy.data.objects.new("Wing " + ("R" if side > 0 else "L"), me)
    sc.collection.objects.link(o)
    o.parent = cam
    o.location = (side * 0.035, -0.035, -0.01)
    o.rotation_mode = "XYZ"
    sd = o.modifiers.new("thick", "SOLIDIFY")
    sd.thickness = 0.0012
    return o


wings = [wing_mesh(1), wing_mesh(-1)]
ph = 0.0
for f in range(1, N + 1):
    t = (f - 1) / FPS
    fl = FLAP[f]
    ph += 2 * math.pi * (4.0 + 2.0 * (fl > 1.2)) / FPS
    s = math.sin(ph)
    for side, o in zip((1, -1), wings):
        if fl <= 0:
            o.rotation_euler = (0, side * math.radians(-100), 0)       # folded back, out of view
        else:
            up = fl * (0.35 + 0.75 * s)                                 # + up / - down
            sweep = 0.25 + 0.35 * max(0.0, -s) * min(1.0, fl)          # forward on the downstroke
            o.rotation_euler = (0, side * sweep, side * up)
        o.keyframe_insert("rotation_euler", frame=f)
for o in wings:
    for fc in fcurves_of(o):
        for kp in fc.keyframe_points:
            kp.interpolation = "LINEAR"

# ------------------------------------------------------------------ look
sc.frame_set(1)
T.SAT = 0.75
T.toonify(sc, samples=int(os.environ.get("SAMPLES", "8")))
inked = [o for o in bpy.data.objects if o.type == "MESH" and not any(
    k in o.name.lower() for k in ("high-poly", "lash", "brow", "teeth", "tongue", "crumb", "wing", "beak",
                                  "set glass", "set line", "set asphalt", "set walk"))]
T.ink(inked, 0.012)
T.ink([o for o in bpy.data.objects if o.name.startswith(("Wing", "Beak"))], 0.0008)
for o in bpy.data.objects:                      # people get finer lines than buildings
    if o.type == "MESH" and any(o.name.startswith(c.name) or o.parent == c.rig for c in CH.values()):
        md = o.modifiers.get("Outline")
        if md:
            md.thickness = 0.004 / max(1e-6, o.matrix_world.to_scale().x)
sc.render.resolution_x, sc.render.resolution_y = 540, 960
sc.render.film_transparent = False

args = sys.argv
if "--still" in args:
    from bpy_extras.object_utils import world_to_camera_view
    for f in [int(v) for v in args[args.index("--still") + 1].split(",")]:
        sc.frame_set(f)
        _r = CH["kian"].rig
        _fb = _r.pose.bones["foot_l"]
        _d = (_r.matrix_world @ _fb.tail) - (_r.matrix_world @ _fb.head)
        print("KIANFOOT", f, round(math.degrees(math.atan2(-_d.x, _d.y)), 1), round(math.degrees(_r.rotation_euler[2]), 1))
        print("PROJ", f, {k: tuple(round(v, 2) for v in world_to_camera_view(sc, cam, head_of(k))) for k in CH})
    os.makedirs(os.path.join(HERE, "test"), exist_ok=True)
    for f in [int(v) for v in args[args.index("--still") + 1].split(",")]:
        sc.frame_set(f)
        sc.render.filepath = os.path.join(HERE, "test", f"s_{f:04d}.png")
        bpy.ops.render.render(write_still=True)
if "--save" in args:
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(HERE, "bird.blend"))
