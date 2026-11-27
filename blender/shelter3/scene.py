"""«پناهگاه ۳ — اتوبوس نجات» (16:9, long). Comic look (EEVEE cel shading + ink outlines) on the cast, bodies
driven by Mixamo clips. All times come from captions.py (times.py, written by layout.py from the voices).

    ../cast/bpy.sh scene.py --still 40,120,...      -> test/s_XXXX.png
    ../cast/bpy.sh scene.py --save                  -> shelter3.blend (render.py renders from it)

The bus never moves: once it leaves, the whole outside world (MOVER) slides past it along -X, so the people
inside can sit with ordinary mocap and the dogs can run beside the wheels in bus coordinates.
  shelter (warm, colourful)  ->  street: the bus arrives in the fog, they get on  ->  the dead city (lamps,
  fires, lit windows)  ->  dusk, the radio  ->  the forest at night: eyes, dogs, a tyre bursts  ->  far headlights
"""
import bpy, sys, os, math, random
from mathutils import Vector, Matrix
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "studio"))
sys.path.insert(0, os.path.join(HERE, "..", "cast"))
sys.path.insert(0, HERE)
bpy.ops.wm.read_factory_settings(use_empty=True)
import cast, mocap, anim   # noqa: E402
import props as P          # noqa: E402
import toon_look as T      # noqa: E402
import look as LK          # noqa: E402
import mocap2 as MC        # noqa: E402
from captions import LINES, END, at, end_of, speaking, TITLE, CAST_KEY  # noqa: E402

cast.STYLE = LK.STYLE
FPS = 24
N = int(END * FPS)
sc = bpy.context.scene
sc.render.fps = FPS
sc.frame_start, sc.frame_end = 1, N
sc.frame_step = 2              # rendered on twos; post.py holds each drawing for two frames
MOC = os.path.join(HERE, "..", "mocap")
SPEED = 1.15
R = random.Random(7)
CLIP = {}
for _c in ("sitting_idle", "nervously_look_around", "breathing_idle", "walking", "opening_door_inwards",
           "talking_phone_pacing", "male_action_pose", "hands_forward_gesture", "terrified", "thinking",
           "pushing_2", "head_nod_yes", "dismissing_gesture"):
    CLIP[_c] = MC.load(os.path.join(MOC, _c + ".fbx"))


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


def interp(owner, kind="LINEAR", path=None):
    for fc in fcurves_of(owner):
        if path is None or fc.data_path == path:
            for k in fc.keyframe_points:
                k.interpolation = kind


def key_vis(o, pts):
    for t, v in pts:
        o.hide_render = not v
        o.keyframe_insert("hide_render", frame=max(1, fr(t)) if t > 0 else 1)
    interp(o, "CONSTANT", "hide_render")


def show(objs, spans):
    for o in objs:
        pts = [(0, False)]
        for a, b in spans:
            pts += [(a, True), (b, False)]
        key_vis(o, pts)


# ================================================================== story times
T_LOUD = at("resc1") - 1.4          # loudspeaker crackle
T_DOOR = end_of("me2") + 0.2        # the steel door opens
T_OUT = at("n3")                    # outside
T_BOARD = at("resc3") + 1.0         # they walk to the bus
T_IN = at("old1") - 0.6             # inside the bus
T_GO = at("resc4") + 0.6            # the bus pulls away
T_DUSK0, T_DUSK1 = at("old2"), at("radio1")
T_FOREST = at("n5") - 0.4
T_EYES = at("lena5") - 0.8
T_DOGS = at("resc6") - 2.0
T_BANG = at("resc7") - 1.4
T_STOP = at("n6") - 0.2
T_LIGHTS = at("n7") + 2.2           # far headlights come on
V = 10.0                            # cruise speed (m/s)


def speed(t):
    if t < T_GO:
        return 0.0
    v = V * seg(t, T_GO, T_GO + 4.0)
    if t > T_FOREST - 2:
        v = V * (1 - 0.2 * seg(t, T_FOREST - 2, T_FOREST + 2))
    if T_DOGS < t < T_BANG:
        v = V * (0.8 + 0.35 * seg(t, T_DOGS + 0.5, T_DOGS + 2.5))        # "گاز میدم"
    if t >= T_BANG:
        v0 = V * 1.15
        v = v0 * (1 - seg(t, T_BANG, T_STOP))
    return v


_D = [0.0]
for f in range(1, N + 2):
    _D.append(_D[-1] + speed((f - 1) / FPS) / FPS)


def travelled(t):
    return _D[max(0, min(len(_D) - 1, int(t * FPS)))]


X_SCHOOL = travelled(at("mom3") + 0.8) + 1.0
X_FOREST = travelled(T_FOREST) + 6.0            # world x where the trees begin (bus front at x = 5.5)
X_END = travelled(END) + 160.0
print("TRAVEL", round(travelled(T_FOREST), 1), round(travelled(END), 1))

# ================================================================== materials


def mats():
    return dict(
        # shelter
        sh_wall=P.mat("Shelter wall", (0.86, 0.62, 0.38), 0.9), sh_wall2=P.mat("Shelter wall low", (0.32, 0.55, 0.52), 0.9),
        sh_floor=P.mat("Shelter floor", (0.5, 0.32, 0.2), 0.8), sh_ceil=P.mat("Shelter ceiling", (0.72, 0.58, 0.42), 0.9),
        steel=P.mat("Steel door", (0.42, 0.48, 0.52), 0.35, metal=0.6), rivet=P.mat("Rivet", (0.3, 0.32, 0.34), 0.3, metal=0.6),
        rug=P.mat("Rug red", (0.72, 0.16, 0.14), 0.9), rug2=P.mat("Rug gold", (0.95, 0.7, 0.2), 0.9),
        rug3=P.mat("Rug blue", (0.16, 0.3, 0.6), 0.9),
        blanket1=P.mat("Blanket orange", (0.95, 0.45, 0.12), 0.9), blanket2=P.mat("Blanket purple", (0.5, 0.25, 0.65), 0.9),
        blanket3=P.mat("Blanket teal", (0.12, 0.55, 0.55), 0.9), pillow=P.mat("Pillow", (0.95, 0.9, 0.75), 0.9),
        bunk=P.mat("Bunk frame", (0.25, 0.4, 0.62), 0.5, metal=0.3), wood=P.mat("Wood", (0.55, 0.35, 0.18), 0.6),
        crate=P.mat("Crate", (0.62, 0.45, 0.22), 0.8), can=P.mat("Tin can", (0.75, 0.75, 0.72), 0.3, metal=0.7),
        can2=P.mat("Tin label red", (0.8, 0.2, 0.15), 0.6), can3=P.mat("Tin label green", (0.25, 0.6, 0.25), 0.6),
        water=P.mat("Water bottle", (0.35, 0.65, 0.95), 0.2), radio=P.mat("Radio", (0.16, 0.18, 0.15), 0.5),
        led=P.mat("Radio LED", (0.2, 1.0, 0.3), 0.3, emit=(0.2, 1.0, 0.3), strength=8),
        lamp_red=P.mat("Status red", (1.0, 0.1, 0.08), 0.3, emit=(1.0, 0.08, 0.05), strength=10),
        lamp_green=P.mat("Status green", (0.1, 1.0, 0.25), 0.3, emit=(0.1, 1.0, 0.25), strength=10),
        lamp_off=P.mat("Status off", (0.15, 0.15, 0.15), 0.4),
        bulb=P.mat("Warm bulb", (1.0, 0.8, 0.45), 0.3, emit=(1.0, 0.75, 0.4), strength=12),
        wire=P.mat("Wire", (0.08, 0.08, 0.08), 0.5),
        drawing1=P.mat("Drawing 1", (0.98, 0.95, 0.85), 0.9), sun_d=P.mat("Drawing sun", (1.0, 0.8, 0.1), 0.9),
        house_d=P.mat("Drawing house", (0.85, 0.25, 0.2), 0.9), grass_d=P.mat("Drawing grass", (0.3, 0.75, 0.3), 0.9),
        hardhat=P.mat("Hard hat", (0.98, 0.82, 0.12), 0.4),
        # outside
        asphalt=P.mat("Asphalt", (0.22, 0.22, 0.23), 0.9), kerb=P.mat("Kerb", (0.5, 0.5, 0.5), 0.9),
        pave=P.mat("Pavement", (0.45, 0.44, 0.42), 0.9), line=P.mat("Road line", (0.85, 0.82, 0.6), 0.8),
        concrete=P.mat("Concrete", (0.52, 0.52, 0.5), 0.95), concrete2=P.mat("Concrete dark", (0.36, 0.36, 0.36), 0.95),
        concrete3=P.mat("Concrete warm", (0.55, 0.48, 0.4), 0.95), brick=P.mat("Brick", (0.5, 0.3, 0.24), 0.9),
        rubble=P.mat("Rubble", (0.45, 0.43, 0.4), 0.95), soot=P.mat("Soot", (0.1, 0.1, 0.1), 0.95),
        car1=P.mat("Car blue", (0.2, 0.3, 0.45), 0.5), car2=P.mat("Car red", (0.45, 0.15, 0.12), 0.5),
        burnt=P.mat("Burnt car", (0.15, 0.13, 0.12), 0.8), tyre=P.mat("Tyre", (0.05, 0.05, 0.05), 0.9),
        pole=P.mat("Lamp pole", (0.3, 0.32, 0.34), 0.5, metal=0.6),
        sodium=P.mat("Street lamp lit", (1.0, 0.7, 0.3), 0.3, emit=(1.0, 0.62, 0.25), strength=25),
        lamp_dead=P.mat("Street lamp dead", (0.4, 0.4, 0.38), 0.4),
        win_lit=P.mat("Window lit", (1.0, 0.8, 0.45), 0.3, emit=(1.0, 0.72, 0.35), strength=6),
        win_dark=P.mat("Window dark", (0.08, 0.09, 0.1), 0.4),
        fire=P.mat("Fire", (1.0, 0.45, 0.1), 0.3, emit=(1.0, 0.4, 0.08), strength=20),
        fire2=P.mat("Fire core", (1.0, 0.85, 0.3), 0.3, emit=(1.0, 0.8, 0.3), strength=30),
        school=P.mat("School wall", (0.92, 0.75, 0.3), 0.9), school2=P.mat("School trim", (0.85, 0.3, 0.2), 0.8),
        swing=P.mat("Swing frame", (0.2, 0.5, 0.75), 0.5, metal=0.4), fence=P.mat("Fence", (0.3, 0.32, 0.3), 0.5, metal=0.5),
        # forest
        ground=P.mat("Forest ground", (0.18, 0.2, 0.12), 0.95), trunk=P.mat("Trunk", (0.22, 0.15, 0.1), 0.9),
        pine1=P.mat("Pine", (0.1, 0.25, 0.16), 0.9), pine2=P.mat("Pine dark", (0.07, 0.18, 0.12), 0.9),
        eyes=P.mat("Glowing eyes", (1.0, 0.85, 0.2), 0.3, emit=(1.0, 0.8, 0.15), strength=30),
        far_light=P.mat("Far headlight", (1.0, 1.0, 0.9), 0.2, emit=(1.0, 0.98, 0.85), strength=60),
        # bus
        bus_body=P.mat("Bus cream", (0.93, 0.88, 0.72), 0.5), bus_stripe=P.mat("Bus stripe", (0.9, 0.42, 0.1), 0.5),
        bus_skirt=P.mat("Bus skirt", (0.25, 0.27, 0.3), 0.6), bus_frame=P.mat("Bus window frame", (0.08, 0.08, 0.09), 0.4),
        bus_roof=P.mat("Bus roof", (0.8, 0.78, 0.7), 0.6), rust=P.mat("Rust", (0.5, 0.25, 0.1), 0.9),
        rim=P.mat("Rim", (0.7, 0.7, 0.72), 0.3, metal=0.8), seat=P.mat("Bus seat", (0.15, 0.3, 0.6), 0.8),
        seat2=P.mat("Bus seat trim", (0.75, 0.2, 0.15), 0.8), bus_floor=P.mat("Bus floor", (0.32, 0.3, 0.28), 0.8),
        bus_inner=P.mat("Bus inner wall", (0.85, 0.8, 0.68), 0.8), bus_ceil=P.mat("Bus ceiling", (0.9, 0.87, 0.78), 0.8),
        poleY=P.mat("Bus pole", (0.95, 0.75, 0.1), 0.3, metal=0.6),
        strip=P.mat("Bus ceiling light", (1.0, 0.92, 0.75), 0.3, emit=(1.0, 0.9, 0.7), strength=6),
        head=P.mat("Headlight", (1.0, 1.0, 0.9), 0.2, emit=(1.0, 0.97, 0.85), strength=40),
        tail=P.mat("Tail light", (1.0, 0.1, 0.05), 0.2, emit=(1.0, 0.08, 0.04), strength=15),
        horn=P.mat("Loudspeaker", (0.85, 0.85, 0.82), 0.4, metal=0.3), dash=P.mat("Dashboard", (0.12, 0.12, 0.13), 0.6),
        luggage=P.mat("Luggage", (0.55, 0.3, 0.15), 0.8), luggage2=P.mat("Luggage blue", (0.2, 0.35, 0.55), 0.8),
        # dogs
        fur=P.mat("Dog fur", (0.2, 0.19, 0.18), 0.9), fur2=P.mat("Dog fur patch", (0.4, 0.33, 0.28), 0.9),
        teeth=P.mat("Dog teeth", (0.95, 0.92, 0.8), 0.4), gum=P.mat("Dog mouth", (0.45, 0.08, 0.1), 0.6),
        dog_eye=P.mat("Dog eye", (1.0, 0.3, 0.1), 0.3, emit=(1.0, 0.35, 0.1), strength=25),
        dark=P.mat("Dark", (0.03, 0.03, 0.04), 0.9),
    )


M_ = mats()
SET = []
MOVER = P.empty("MOVER")


def box(loc, size, m, name="Set", rot=(0, 0, 0), move=True, parent=None):
    o = P.box(loc, size, M_[m] if isinstance(m, str) else m, name)
    o.data.transform(Matrix.Translation(-Vector(loc)))     # P.box bakes the position: put the origin back at loc
    o.location = loc
    o.rotation_euler = rot
    if parent is not None:
        o.parent = parent
    elif move:
        o.parent = MOVER
    SET.append(o)
    return o


def cyl(a, b, r, m, name="Cyl", verts=16, move=True, parent=None):
    o = P.cyl(a, b, r, M_[m] if isinstance(m, str) else m, name, verts=verts)
    o.parent = parent if parent is not None else (MOVER if move else None)
    SET.append(o)
    return o


def sph(loc, r, m, name="Sph", scale=(1, 1, 1), move=True, parent=None):
    o = P.sphere(loc, r, M_[m] if isinstance(m, str) else m, name, scale=scale)
    o.parent = parent if parent is not None else (MOVER if move else None)
    SET.append(o)
    return o


def cone(loc, r1, r2, h, m, name="Cone", rot=(0, 0, 0), verts=12, move=True, parent=None):
    bpy.ops.mesh.primitive_cone_add(vertices=verts, radius1=r1, radius2=r2, depth=h, location=loc, rotation=rot)
    o = bpy.context.object
    o.name = name
    o.data.materials.append(M_[m] if isinstance(m, str) else m)
    o.parent = parent if parent is not None else (MOVER if move else None)
    SET.append(o)
    return o


def linked(src, loc, rot=(0, 0, 0), scale=(1, 1, 1), name=None):
    o = bpy.data.objects.new(name or src.name + ".i", src.data)
    sc.collection.objects.link(o)
    o.location, o.rotation_euler, o.scale = loc, rot, scale
    o.parent = MOVER
    SET.append(o)
    return o


# ================================================================== the shelter (x -2..6, y -11.5..-5.5)
SX0, SX1, SY0, SY1, SH = -2.0, 6.0, -11.5, -5.5, 2.8
DOOR_X = 2.0
box(((SX0 + SX1) / 2, (SY0 + SY1) / 2, -0.05), (SX1 - SX0, SY1 - SY0, 0.1), "sh_floor", "Shelter floor")
box(((SX0 + SX1) / 2, (SY0 + SY1) / 2, SH + 0.05), (SX1 - SX0, SY1 - SY0, 0.1), "sh_ceil", "Shelter ceiling")
for x in (SX0 - 0.1, SX1 + 0.1):
    box((x, (SY0 + SY1) / 2, SH / 2), (0.2, SY1 - SY0, SH), "sh_wall", "Shelter wall side")
    box((x + (0.11 if x < 0 else -0.11), (SY0 + SY1) / 2, 0.5), (0.02, SY1 - SY0, 1.0), "sh_wall2", "Wall band")
box(((SX0 + SX1) / 2, SY0 - 0.1, SH / 2), (SX1 - SX0, 0.2, SH), "sh_wall", "Shelter back wall")
box(((SX0 + SX1) / 2, SY0 + 0.01, 0.5), (SX1 - SX0, 0.02, 1.0), "sh_wall2", "Wall band back")
# front wall with the door hole (1.1 x 2.1)
box(((SX0 + DOOR_X - 0.55) / 2, SY1 + 0.1, SH / 2), (DOOR_X - 0.55 - SX0, 0.2, SH), "sh_wall", "Front wall L")
box(((DOOR_X + 0.55 + SX1) / 2, SY1 + 0.1, SH / 2), (SX1 - DOOR_X - 0.55, 0.2, SH), "sh_wall", "Front wall R")
box((DOOR_X, SY1 + 0.1, (2.1 + SH) / 2), (1.1, 0.2, SH - 2.1), "sh_wall", "Front wall top")
box(((SX0 + SX1) / 2, SY1 - 0.01, 0.5), (SX1 - SX0, 0.02, 1.0), "sh_wall2", "Wall band front")
# the steel door, hinged at its left edge, opens inwards (-Y)
HINGE = P.empty("Door hinge", (DOOR_X - 0.52, SY1 + 0.04, 0))
HINGE.parent = MOVER
door = box((0.52, 0, 1.03), (1.04, 0.08, 2.06), "steel", "Steel door", parent=HINGE)
for zz in (0.3, 1.0, 1.75):
    box((0.52, -0.05, zz), (0.96, 0.03, 0.08), "rivet", "Door bar", parent=HINGE)
box((0.9, -0.08, 1.0), (0.06, 0.05, 0.25), "rivet", "Door handle", parent=HINGE)
# status light above the door (inside): red, then green from the start
lamp_box = box((DOOR_X, SY1 - 0.08, 2.32), (0.36, 0.14, 0.2), "dark", "Status housing")
lamp_g = sph((DOOR_X + 0.08, SY1 - 0.16, 2.32), 0.07, "lamp_green", "Status green")
lamp_r = sph((DOOR_X - 0.08, SY1 - 0.16, 2.32), 0.07, "lamp_off", "Status red off")
# bunk bed against the left wall
BX = SX0 + 0.55
for z in (0.42, 1.45):
    box((BX, -9.2, z), (0.95, 2.0, 0.08), "bunk", "Bunk")
    box((BX, -9.2, z + 0.1), (0.9, 1.95, 0.14), "pillow" if z > 1 else "blanket3", "Mattress")
    box((BX + 0.03, -9.55, z + 0.2), (0.92, 1.2, 0.06), "blanket1" if z < 1 else "blanket2", "Blanket")
    box((BX, -10.0, z + 0.25), (0.6, 0.3, 0.12), "pillow", "Pillow")
for (dx, dy) in ((-0.45, -1.0), (0.45, -1.0), (-0.45, 1.0), (0.45, 1.0)):
    cyl((BX + dx, -9.2 + dy, 0), (BX + dx, -9.2 + dy, 2.0), 0.035, "bunk", "Bunk post", 8)
# a second low bed (mattress on the floor) by the back wall
box((4.6, -10.6, 0.1), (2.0, 1.1, 0.2), "blanket2", "Floor mattress")
box((4.6, -10.4, 0.22), (1.8, 0.7, 0.05), "blanket1", "Floor blanket")
box((3.8, -10.85, 0.28), (0.45, 0.3, 0.12), "pillow", "Pillow 2")
# rug
box((1.6, -8.4, 0.005), (3.2, 2.2, 0.01), "rug", "Rug")
box((1.6, -8.4, 0.012), (2.6, 1.6, 0.01), "rug2", "Rug inner")
box((1.6, -8.4, 0.019), (2.0, 1.0, 0.01), "rug3", "Rug centre")
# table with the radio, a lantern and cups
TABLE = (1.0, -8.0)
box((TABLE[0], TABLE[1], 0.74), (1.3, 0.8, 0.05), "wood", "Table top")
for (dx, dy) in ((-0.58, -0.34), (0.58, -0.34), (-0.58, 0.34), (0.58, 0.34)):
    box((TABLE[0] + dx, TABLE[1] + dy, 0.36), (0.05, 0.05, 0.72), "wood", "Table leg")
RADIO_T = (TABLE[0] + 0.25, TABLE[1] - 0.1, 0.84)
lantern = cyl((TABLE[0] - 0.4, TABLE[1] + 0.15, 0.77), (TABLE[0] - 0.4, TABLE[1] + 0.15, 1.0), 0.07, "bulb", "Lantern glass")
cyl((TABLE[0] - 0.4, TABLE[1] + 0.15, 1.0), (TABLE[0] - 0.4, TABLE[1] + 0.15, 1.05), 0.08, "dark", "Lantern cap")
for i, c in enumerate(("can2", "can3")):
    cyl((TABLE[0] - 0.05 + i * 0.15, TABLE[1] + 0.2, 0.77), (TABLE[0] - 0.05 + i * 0.15, TABLE[1] + 0.2, 0.87), 0.035, c, "Cup")
# crates as seats
CRATES = {"me": (1.0, -8.85), "guard": (3.3, -6.6)}
for k, (x, y) in CRATES.items():
    box((x, y, 0.2), (0.5, 0.45, 0.4), "crate", "Crate seat")
box((4.9, -6.4, 0.25), (0.7, 0.6, 0.5), "crate", "Crate stack")
box((4.9, -6.4, 0.75), (0.6, 0.5, 0.5), "crate", "Crate stack")
# shelves on the back wall: tins and only a few bottles of water
for z in (0.4, 0.95, 1.5):
    box((0.4, SY0 + 0.25, z), (2.6, 0.4, 0.04), "wood", "Shelf")
for (dx) in (-1.25, 1.25):
    box((0.4 + dx, SY0 + 0.25, 0.95), (0.05, 0.4, 1.9), "wood", "Shelf side")
for j in range(9):
    x = -0.7 + j * 0.25
    if R.random() < 0.75:
        cyl((x, SY0 + 0.3, 0.97), (x, SY0 + 0.3, 1.1), 0.05, R.choice(["can2", "can3", "can"]), "Tin")
for x in (-0.6, -0.35):
    cyl((x, SY0 + 0.3, 0.42), (x, SY0 + 0.3, 0.72), 0.06, "water", "Water bottle")
for j in range(5):
    x = 0.2 + j * 0.28
    cyl((x, SY0 + 0.3, 1.52), (x, SY0 + 0.3, 1.64), 0.05, R.choice(["can2", "can3"]), "Tin")
# Lena's drawings on the wall (no words)
for i, (x, z) in enumerate(((3.2, 1.6), (4.1, 1.5), (5.0, 1.65))):
    box((x, SY0 + 0.02, z), (0.6, 0.02, 0.45), "drawing1", "Drawing")
    sph((x - 0.15, SY0 + 0.04, z + 0.1), 0.07, "sun_d", "Drawing sun", scale=(1, 0.2, 1))
    box((x + 0.08, SY0 + 0.04, z - 0.08), (0.2, 0.01, 0.16), "house_d", "Drawing house")
    box((x, SY0 + 0.04, z - 0.18), (0.56, 0.01, 0.05), "grass_d", "Drawing grass")
# string of warm bulbs under the ceiling
for i in range(14):
    u = i / 13
    x = SX0 + 0.4 + u * (SX1 - SX0 - 0.8)
    y = -8.5 + 0.6 * math.sin(u * math.pi * 3)
    sph((x, y, SH - 0.22 - 0.08 * math.sin(u * math.pi * 7) ** 2), 0.05, "bulb", "String bulb")
cyl((SX0 + 0.4, -8.5, SH - 0.17), (SX1 - 0.4, -8.5, SH - 0.17), 0.006, "wire", "String wire", 6)
SH_LIGHTS = []
for (x, y, e) in ((0.0, -8.3, 140), (3.8, -8.3, 140), (1.0, -8.0, 60)):
    l_ = bpy.data.lights.new("Shelter warm", "POINT")
    l_.energy, l_.color, l_.shadow_soft_size = e, (1.0, 0.72, 0.45), 0.4
    lo = bpy.data.objects.new("Shelter warm", l_)
    sc.collection.objects.link(lo)
    lo.location = (x, y, 2.2 if e > 100 else 1.1)
    lo.parent = MOVER
    SH_LIGHTS.append(lo)

SEC_SHELTER = list(SET)
# ================================================================== street and the dead city
ROAD_W = 9.0
X0 = -70.0
box(((X0 + X_END) / 2, 0, -0.03), (X_END - X0, ROAD_W, 0.06), "asphalt", "Road")
for j in range(int((X_END - X0) / 6)):
    x = X0 + 3 + j * 6
    box((x, 0, 0.002), (2.6, 0.14, 0.01), "line", "Road line")
CITY_END = X_FOREST - 10
for s_ in (-1, 1):
    box(((X0 + CITY_END) / 2, s_ * (ROAD_W / 2 + 0.5), 0.08), (CITY_END - X0, 0.95, 0.16), "pave", "Pavement")
    box(((X0 + CITY_END) / 2, s_ * (ROAD_W / 2 + 0.05), 0.09), (CITY_END - X0, 0.12, 0.18), "kerb", "Kerb")
# shelter building facade on the -Y side around the door (x -6..10)
box(((SX0 + SX1) / 2, SY1 + 0.25, 1.4), (SX1 - SX0 + 0.4, 0.1, 2.8), "concrete", "Facade low", )
box(((SX0 + SX1) / 2, -8.5, 4.6), (SX1 - SX0 + 0.4, 6.4, 3.6), "concrete2", "Shelter block upper")
for x in (SX0 - 3.5, SX1 + 3.5):
    box((x, -9.0, 3.5), (6.6, 7.0, 7.0), "concrete", "Neighbour block")
# window texture for the towers: brick pattern on object coordinates


def tower_mat(name, wall, lit_ratio, seed):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs["Object"], sep.inputs[0])
    add = nt.nodes.new("ShaderNodeMath")
    add.operation = "ADD"
    nt.links.new(sep.outputs[0], add.inputs[0])
    nt.links.new(sep.outputs[1], add.inputs[1])
    comb = nt.nodes.new("ShaderNodeCombineXYZ")
    nt.links.new(add.outputs[0], comb.inputs[0])
    nt.links.new(sep.outputs[2], comb.inputs[1])
    br = nt.nodes.new("ShaderNodeTexBrick")
    br.offset = 0.0
    br.inputs["Scale"].default_value = 1.0
    br.inputs["Brick Width"].default_value = 1.6
    br.inputs["Row Height"].default_value = 3.0
    br.inputs["Mortar Size"].default_value = 0.45
    br.inputs["Color1"].default_value = (0.06, 0.07, 0.08, 1)
    br.inputs["Color2"].default_value = (0.06, 0.07, 0.08, 1)
    br.inputs["Mortar"].default_value = tuple(wall) + (1,)
    nt.links.new(comb.outputs[0], br.inputs["Vector"])
    bsdf.inputs["Base Color"].default_value = tuple(wall) + (1,)
    m["tower_wall"] = tuple(wall)
    m["tower_lit"] = lit_ratio
    m["tower_seed"] = seed
    return m


TOWER_MATS = [tower_mat(f"Tower {i}", w, lr, i) for i, (w, lr) in enumerate((
    ((0.55, 0.53, 0.5), 0.04), ((0.45, 0.42, 0.4), 0.06), ((0.6, 0.5, 0.42), 0.03), ((0.38, 0.4, 0.42), 0.05)))]


def ruined_block(x, y, w, d, h, m, seed, side):
    r = random.Random(seed)
    o = box((x, y, h / 2), (w, d, h), m, "Ruin")
    # broken top: a few uneven chunks and a missing corner
    for k in range(r.randint(2, 4)):
        cw, cd = r.uniform(0.2, 0.5) * w, r.uniform(0.3, 0.7) * d
        ch = r.uniform(0.8, 3.0)
        box((x + r.uniform(-0.3, 0.3) * w, y + r.uniform(-0.2, 0.2) * d, h + ch / 2), (cw, cd, ch), m, "Ruin top",
            rot=(r.uniform(-0.15, 0.15), r.uniform(-0.15, 0.15), 0))
    # soot streaks and a burnt hole facing the road
    fy = y - side * (d / 2 + 0.02)
    for k in range(r.randint(1, 3)):
        box((x + r.uniform(-0.35, 0.35) * w, fy, r.uniform(0.3, 0.8) * h), (r.uniform(1.5, 3.0), 0.04, r.uniform(2, 5)),
            "soot", "Soot")
    # rubble heap at its foot
    for k in range(r.randint(3, 6)):
        s_ = r.uniform(0.5, 1.6)
        box((x + r.uniform(-0.5, 0.5) * w, y - side * (d / 2 + r.uniform(0.3, 1.8)), s_ * 0.3), (s_, s_ * 0.8, s_ * 0.6),
            "rubble", "Rubble", rot=(r.uniform(0, 0.6), r.uniform(0, 0.6), r.uniform(0, 3)))
    return o


XS = {-1: 14.0, 1: 8.0}
k = 0
for s_ in (-1, 1):
    x = XS[s_]
    while x < CITY_END - 8:
        r = random.Random(k * 13 + (s_ + 1))
        w, d = r.uniform(9, 16), r.uniform(9, 14)
        h = r.uniform(8, 26) if r.random() < 0.8 else r.uniform(3, 6)
        if not (s_ < 0 and abs(x + w / 2 - X_SCHOOL) < 14):
            ruined_block(x + w / 2, s_ * (ROAD_W / 2 + 3.4 + d / 2), w, d, h, TOWER_MATS[r.randrange(4)], k * 7 + s_, s_)
        x += w + r.uniform(1.5, 5)
        k += 1
for s_ in (-1, 1):            # behind the shelter, back towards -X
    for j in range(4):
        ruined_block(-14 - j * 14, s_ * (ROAD_W / 2 + 9), 11, 10, 9 + j * 4, TOWER_MATS[j % 4], 900 + j * 3 + s_, s_)

# the school (seen from the window when Mom says «اون... مدرسه‌ت بود») on the -Y side
SCH_Y = -(ROAD_W / 2 + 9.0)
box((X_SCHOOL, SCH_Y - 4, 3.0), (18, 8, 6), "school", "School")
box((X_SCHOOL, SCH_Y - 4, 6.2), (18.4, 8.4, 0.4), "school2", "School roof edge")
for j in range(6):
    box((X_SCHOOL - 7.5 + j * 3, SCH_Y + 0.02, 3.9), (1.6, 0.06, 1.3), "win_dark", "School window")
    box((X_SCHOOL - 7.5 + j * 3, SCH_Y + 0.02, 1.6), (1.6, 0.06, 1.3), "win_dark", "School window")
box((X_SCHOOL + 6, SCH_Y - 1, 6.5), (6, 6, 1.5), "rubble", "School broken corner", rot=(0.3, 0.2, 0.4))
for j in range(10):          # the playground fence and a swing
    cyl((X_SCHOOL - 9 + j * 2, SCH_Y + 4.2, 0), (X_SCHOOL - 9 + j * 2, SCH_Y + 4.2, 1.2), 0.04, "fence", "Fence post", 6)
cyl((X_SCHOOL - 9, SCH_Y + 4.2, 1.15), (X_SCHOOL + 9, SCH_Y + 4.2, 1.15), 0.03, "fence", "Fence rail", 6)
for dx in (-1.2, 1.2):
    cyl((X_SCHOOL - 3 + dx, SCH_Y + 2.0, 0), (X_SCHOOL - 3 + dx * 0.7, SCH_Y + 2.0, 2.4), 0.05, "swing", "Swing leg", 8)
cyl((X_SCHOOL - 4.3, SCH_Y + 2.0, 2.4), (X_SCHOOL - 1.7, SCH_Y + 2.0, 2.4), 0.05, "swing", "Swing bar", 8)
SWING = P.empty("Swing pivot", (X_SCHOOL - 3, SCH_Y + 2.0, 2.4))
SWING.parent = MOVER
for dx in (-0.2, 0.2):
    cyl((dx, 0, 0), (dx, 0, -1.8), 0.01, "wire", "Swing rope", 6, parent=SWING)
box((0, 0, -1.82), (0.5, 0.2, 0.04), "seat2", "Swing seat", parent=SWING)

# cars: abandoned and burnt, some burning


def car(x, y, m, rot, burning=False):
    o = box((x, y, 0.55), (4.2, 1.8, 0.7), m, "Car body", rot=(0, 0, rot))
    box((x - 0.2 * math.cos(rot), y - 0.2 * math.sin(rot), 1.15), (2.2, 1.6, 0.55), m, "Car cabin", rot=(0, 0, rot))
    for (dx, dy) in ((-1.3, -0.85), (1.3, -0.85), (-1.3, 0.85), (1.3, 0.85)):
        c, s2 = math.cos(rot), math.sin(rot)
        wx, wy = x + dx * c - dy * s2, y + dx * s2 + dy * c
        cyl((wx + 0.12 * s2, wy - 0.12 * c, 0.35), (wx - 0.12 * s2, wy + 0.12 * c, 0.35), 0.35, "tyre", "Wheel", 12)
    if burning:
        FIRES.append((x, y, 1.5))
    return o


FIRES = []
for j, xx in enumerate(range(20, int(CITY_END) - 20, 37)):
    r = random.Random(500 + j)
    s_ = r.choice((-1, 1))
    car(xx + r.uniform(-5, 5), s_ * r.uniform(2.6, 3.8), r.choice(["burnt", "burnt", "car1", "car2"]),
        r.uniform(-0.5, 0.5) + (math.pi if r.random() < 0.5 else 0), burning=r.random() < 0.45)
car(-9.0, 3.0, "burnt", 0.3, burning=True)          # near the shelter
car(14.0, -3.2, "car1", -0.2)
FIRE_OBJ = []
for (x, y, z) in FIRES:
    for k in range(3):
        f_ = cone((x + R.uniform(-0.5, 0.5), y + R.uniform(-0.4, 0.4), z + 0.2), 0.45 - k * 0.1, 0.0, 1.2 - k * 0.25,
                  "fire" if k < 2 else "fire2", "Fire flame")
        FIRE_OBJ.append(f_)
    l_ = bpy.data.lights.new("Fire light", "POINT")
    l_.energy, l_.color = 900, (1.0, 0.5, 0.15)
    lo = bpy.data.objects.new("Fire light", l_)
    sc.collection.objects.link(lo)
    lo.location = (x, y, z + 1.5)
    lo.parent = MOVER
    FIRE_OBJ.append(lo)
# street lamps: both sides every ~24 m; lit (warm sodium), dead, or flickering
LAMPS = []
for j, xx in enumerate(range(-30, int(CITY_END), 24)):
    for s_ in (-1, 1):
        r = random.Random(700 + j * 2 + s_)
        y = s_ * (ROAD_W / 2 + 0.7)
        bent = r.random() < 0.15
        cyl((xx, y, 0), (xx, y, 6.5), 0.09, "pole", "Lamp pole", 8).rotation_euler = (s_ * (0.35 if bent else 0), 0, 0)
        if bent:
            continue
        cyl((xx, y, 6.5), (xx, y - s_ * 1.4, 6.7), 0.06, "pole", "Lamp arm", 8)
        state = r.choice(["lit", "lit", "flicker", "dead"])
        head_ = box((xx, y - s_ * 1.5, 6.6), (0.6, 0.3, 0.14), "sodium" if state != "dead" else "lamp_dead", "Lamp head")
        if state != "dead":
            l_ = bpy.data.lights.new("Street lamp", "SPOT")
            l_.energy, l_.color, l_.spot_size, l_.spot_blend = 1500, (1.0, 0.65, 0.3), 1.6, 0.6
            lo = bpy.data.objects.new("Street lamp", l_)
            sc.collection.objects.link(lo)
            lo.location = (xx, y - s_ * 1.5, 6.45)
            lo.parent = MOVER
            LAMPS.append((head_, lo, state, r.random() * 10))
# lit windows here and there: small warm squares on the road side of some towers (people still alive?)
for j in range(40):
    r = random.Random(1200 + j)
    s_ = r.choice((-1, 1))
    xx = r.uniform(10, CITY_END - 10)
    box((xx, s_ * (ROAD_W / 2 + 3.35), r.uniform(4, 14)), (1.0, 0.05, 1.2), "win_lit", "Lit window")

SEC_CITY = [o for o in SET if o not in set(SEC_SHELTER)]
# ================================================================== the forest (from X_FOREST on, at night)
box(((X_FOREST - 10 + X_END) / 2, 0, -0.06), (X_END - X_FOREST + 10, 160, 0.1), "ground", "Forest ground")
TREE = {}
for kind in ("a", "b"):
    tr = cyl((0, 0, 0), (0, 0, 3.0), 0.22, "trunk", f"Trunk {kind}", 8, move=False)
    tr.parent = None
    parts = [tr]
    for k in range(3):
        c_ = cone((0, 0, 2.6 + k * 1.9), 2.4 - k * 0.6, 0.0, 3.2 - k * 0.4, "pine1" if kind == "a" else "pine2",
                  f"Pine {kind}", move=False)
        c_.parent = None
        parts.append(c_)
    bpy.ops.object.select_all(action="DESELECT")
    for p_ in parts:
        p_.select_set(True)
        SET.remove(p_)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.object.join()
    TREE[kind] = bpy.context.object
    TREE[kind].hide_render = True
    TREE[kind].location = (0, 0, -100)
for j in range(520):
    r = random.Random(3000 + j)
    xx = r.uniform(X_FOREST, X_END)
    s_ = r.choice((-1, 1))
    yy = s_ * (ROAD_W / 2 + 1.5 + r.expovariate(1 / 9.0))
    sc_ = r.uniform(0.8, 1.6)
    linked(TREE[r.choice("ab")], (xx, yy, 0), (0, 0, r.uniform(0, 6)), (sc_, sc_, sc_ * r.uniform(0.9, 1.4)), "Tree")
# glowing eyes between the trees (on from T_EYES)
EYES = []
for j in range(14):
    r = random.Random(4000 + j)
    xx = travelled(T_EYES + 1.5) + r.uniform(-4, 40)
    yy = -(ROAD_W / 2 + r.uniform(4, 14))
    zz = r.uniform(0.5, 0.8)
    for dx in (-0.09, 0.09):
        e_ = sph((xx + dx, yy, zz), 0.045, "eyes", "Eyes in the trees")
        EYES.append((e_, r.uniform(0, 1.5)))
# far headlights at the end of the road (the unknown car), on at T_LIGHTS
XL = travelled(END) + 45
FAR = []
for dy in (-0.8, 0.8):
    FAR.append(sph((XL, dy - 0.5, 0.8), 0.28, "far_light", "Far headlight"))
l_ = bpy.data.lights.new("Far lights", "SPOT")
l_.energy, l_.spot_size, l_.color = 30000, 0.9, (1.0, 0.97, 0.85)
far_lamp = bpy.data.objects.new("Far lights", l_)
sc.collection.objects.link(far_lamp)
far_lamp.location = (XL, -0.5, 1.2)
far_lamp.rotation_euler = (math.pi / 2, 0, math.pi / 2)
far_lamp.parent = MOVER
FAR.append(far_lamp)
show(FAR, [(T_LIGHTS, END + 1)])

_seen = set(SEC_SHELTER) | set(SEC_CITY)
SEC_FOREST = [o for o in SET if o not in _seen]
# ================================================================== the bus (fixed; front at +X)
BUS = P.empty("BUS")
BL, BW = 11.0, 2.5
BY = -0.2                       # centre line
YR, YL = BY - BW / 2, BY + BW / 2   # right side (door, -Y) / left side (driver, +Y)
FLOOR = 0.55
BUS_X0, BUS_X1 = -BL / 2, BL / 2


def bbox_(loc, size, m, name="Bus", rot=(0, 0, 0)):
    return box(loc, size, m, name, rot=rot, parent=BUS)


bbox_((0, BY, FLOOR - 0.05), (BL - 0.1, BW - 0.1, 0.1), "bus_floor", "Bus floor")
bbox_((0, BY, 0.42), (BL, BW, 0.16), "bus_skirt", "Bus chassis")
DOOR0, DOOR1 = 3.25, 4.3
WIN0, WIN1 = 1.35, 2.45
for side, y in (("R", YR), ("L", YL)):
    yo = y + (0.03 if side == "L" else -0.03)
    segs_ = [(BUS_X0, DOOR0), (DOOR1, BUS_X1)] if side == "R" else [(BUS_X0, BUS_X1)]
    for a, b in segs_:
        bbox_(((a + b) / 2, y, (FLOOR + WIN0) / 2 - 0.05), (b - a, 0.06, WIN0 - FLOOR + 0.3), "bus_body", "Bus side low")
        bbox_(((a + b) / 2, yo, 0.62), (b - a, 0.02, 0.22), "bus_skirt", "Bus skirt")
        bbox_(((a + b) / 2, yo, 1.12), (b - a, 0.02, 0.14), "bus_stripe", "Bus stripe")
        bbox_(((a + b) / 2, y - (0.035 if side == "R" else -0.035), (FLOOR + WIN0) / 2), (b - a, 0.01, WIN0 - FLOOR),
              "bus_inner", "Bus inner wall")
    bbox_((0, y, (WIN1 + 2.95) / 2), (BL, 0.06, 2.95 - WIN1), "bus_body", "Bus side high")
    bbox_((0, yo, 2.62), (BL, 0.02, 0.1), "bus_stripe", "Bus stripe high")
    # window pillars
    xs = [BUS_X0 + 0.15 + j * 1.06 for j in range(11)]
    for xx in xs:
        if side == "R" and DOOR0 - 0.05 < xx < DOOR1 + 0.05:
            continue
        bbox_((xx, y, (WIN0 + WIN1) / 2), (0.12, 0.08, WIN1 - WIN0), "bus_frame", "Window pillar")
    bbox_((0, y, WIN0 + 0.02), (BL, 0.1, 0.05), "bus_frame", "Window sill")
    bbox_((0, y, WIN1 - 0.02), (BL, 0.1, 0.05), "bus_frame", "Window top")
# door: two folding leaves (open at the start), frame
bbox_((DOOR0, YR, 1.7), (0.08, 0.1, 2.6), "bus_frame", "Door frame")
bbox_((DOOR1, YR, 1.7), (0.08, 0.1, 2.6), "bus_frame", "Door frame")
DOOR_LEAF = []
for j, xx in enumerate((DOOR0 + 0.27, DOOR1 - 0.27)):
    piv = P.empty("Bus door leaf", (DOOR0 + 0.02 if j == 0 else DOOR1 - 0.02, YR - 0.02, 0.5))
    piv.parent = BUS
    bbox_((0.25 if j == 0 else -0.25, 0, 1.2), (0.5, 0.04, 2.3), "bus_frame", "Door leaf").parent = piv
    o = bbox_((0.25 if j == 0 else -0.25, -0.03, 1.55), (0.36, 0.02, 1.2), "dark", "Door glass")
    o.parent = piv
    DOOR_LEAF.append((piv, j))
# steps under the door
bbox_(((DOOR0 + DOOR1) / 2, YR + 0.3, 0.28), (DOOR1 - DOOR0 - 0.1, 0.5, 0.06), "bus_floor", "Step")
# roof (rounded edges)
bbox_((0, BY, 3.0), (BL, BW - 0.3, 0.12), "bus_roof", "Bus roof")
for y in (YR + 0.15, YL - 0.15):
    cyl((BUS_X0, y, 2.93), (BUS_X1, y, 2.93), 0.15, "bus_roof", "Roof edge", 12, parent=BUS)
bbox_((0, BY, 2.88), (BL - 0.2, BW - 0.2, 0.04), "bus_ceil", "Bus ceiling")
# front: low panel, a big windshield (open), header with a blank destination board, lights, bumper
bbox_((BUS_X1, BY, 0.9), (0.08, BW, 1.0), "bus_body", "Bus front low")
bbox_((BUS_X1 + 0.03, BY, 0.75), (0.02, BW - 0.2, 0.14), "bus_stripe", "Front stripe")
bbox_((BUS_X1, BY, 2.75), (0.08, BW, 0.45), "bus_body", "Bus front top")
bbox_((BUS_X1 + 0.03, BY, 2.72), (0.02, 1.4, 0.24), "dark", "Destination board")
for y in (YR + 0.05, BY, YL - 0.05):
    bbox_((BUS_X1, y, 1.95), (0.1, 0.09, 1.2), "bus_frame", "Windshield frame")
bbox_((BUS_X1, BY, 1.4), (0.1, BW, 0.06), "bus_frame", "Windshield sill")
bbox_((BUS_X1 + 0.1, BY, 0.45), (0.12, BW + 0.05, 0.22), "bus_skirt", "Bumper")
for y in (YR + 0.3, YL - 0.3):
    sph((BUS_X1 + 0.05, y, 0.78), 0.13, "head", "Headlight", scale=(0.4, 1, 1), parent=BUS)
# back: panel with a small rear window, red lights
bbox_((BUS_X0, BY, 1.7), (0.08, BW, 2.5), "bus_body", "Bus back")
bbox_((BUS_X0 - 0.03, BY, 2.15), (0.02, 1.6, 0.6), "dark", "Rear window")
bbox_((BUS_X0 - 0.03, BY, 1.12), (0.02, BW - 0.05, 0.14), "bus_stripe", "Back stripe")
for y in (YR + 0.2, YL - 0.2):
    bbox_((BUS_X0 - 0.05, y, 0.85), (0.04, 0.2, 0.3), "tail", "Tail light")
# wheels
WHEELS = []
for xx in (-3.4, 3.4):
    for y in (YR - 0.02, YL + 0.02):
        piv = P.empty("Wheel pivot", (xx, y, 0.5))
        piv.parent = BUS
        t_ = cyl((0, -0.16, 0), (0, 0.16, 0), 0.5, "tyre", "Bus tyre", 20, parent=piv)
        cyl((0, -0.18 if y < BY else 0.17, 0), (0, -0.17 if y < BY else 0.18, 0), 0.28, "rim", "Rim", 12, parent=piv)
        for k in range(5):
            a = k * 2 * math.pi / 5
            sph((0.16 * math.cos(a), -0.19 if y < BY else 0.19, 0.16 * math.sin(a)), 0.035, "dark", "Lug", parent=piv)
        WHEELS.append((piv, xx, y))
        bbox_((xx, y, 1.05), (1.3, 0.08, 0.12), "bus_skirt", "Wheel arch")
# roof: loudspeakers and a luggage rack
for y in (BY - 0.45, BY + 0.45):
    o = cone((BUS_X1 - 1.2, y, 3.3), 0.08, 0.28, 0.55, "horn", "Loudspeaker", rot=(0, math.pi / 2, 0), parent=BUS)
cyl((BUS_X1 - 1.4, BY, 3.06), (BUS_X1 - 1.4, BY, 3.3), 0.04, "pole", "Speaker mast", 8, parent=BUS)
cyl((BUS_X1 - 1.4, BY - 0.5, 3.3), (BUS_X1 - 1.4, BY + 0.5, 3.3), 0.03, "pole", "Speaker bar", 8, parent=BUS)
for xx in (-4, -1.5, 1.0):
    bbox_((xx, BY, 3.1), (1.6, BW - 0.6, 0.06), "pole", "Rack")
for (xx, yy, m) in ((-3.8, BY - 0.4, "luggage"), (-3.3, BY + 0.4, "luggage2"), (-1.2, BY, "luggage"), (0.6, BY - 0.3, "luggage2")):
    bbox_((xx, yy, 3.32), (0.9, 0.7, 0.4), m, "Luggage")
# rust and dirt patches
for j in range(10):
    r = random.Random(60 + j)
    xx = r.uniform(BUS_X0 + 0.5, BUS_X1 - 0.5)
    y = r.choice((YR - 0.04, YL + 0.04))
    bbox_((xx, y, r.uniform(0.6, 1.2)), (r.uniform(0.3, 0.9), 0.01, r.uniform(0.15, 0.4)), "rust", "Rust")
# interior: seats 2+2, poles, ceiling lights, the driver's place
AISLE_Y = BY - 0.1
SEAT_TOP = FLOOR + 0.34
ROWS = [BUS_X0 + 0.9 + j * 0.86 for j in range(9)]       # seat-back x of each row (people sit in front of it)
SEATS = {}
for i, xx in enumerate(ROWS):
    for side, (ya, yb) in (("R", (YR + 0.12, AISLE_Y - 0.33)), ("L", (AISLE_Y + 0.33, YL - 0.12))):
        if side == "R" and xx > DOOR0 - 0.7:
            continue
        cy = (ya + yb) / 2
        bbox_((xx + 0.24, cy, SEAT_TOP - 0.07), (0.48, yb - ya, 0.14), "seat", "Seat cushion")
        bbox_((xx - 0.02, cy, SEAT_TOP + 0.32), (0.1, yb - ya, 0.7), "seat", "Seat back")
        bbox_((xx - 0.02, cy, SEAT_TOP + 0.66), (0.12, yb - ya + 0.02, 0.08), "seat2", "Seat top")
        bbox_((xx + 0.24, cy, (FLOOR + SEAT_TOP) / 2 - 0.05), (0.06, yb - ya - 0.1, SEAT_TOP - FLOOR - 0.1), "pole",
              "Seat leg")
        SEATS[(i, side, "win")] = (xx + 0.2, ya + 0.22)
        SEATS[(i, side, "aisle")] = (xx + 0.2, yb - 0.22)
for xx in ROWS[1::2]:
    cyl((xx + 0.5, AISLE_Y - 0.34, FLOOR), (xx + 0.5, AISLE_Y - 0.34, 2.88), 0.025, "poleY", "Pole", 8, parent=BUS)
for y in (AISLE_Y - 0.45, AISLE_Y + 0.45):
    cyl((BUS_X0 + 0.4, y, 2.55), (BUS_X1 - 0.6, y, 2.55), 0.02, "poleY", "Hand rail", 8, parent=BUS)
for xx in (-4, -2, 0, 2):
    bbox_((xx, AISLE_Y, 2.85), (1.4, 0.18, 0.03), "strip", "Ceiling light")
BUS_LIGHTS = []
for xx in (-3.2, 0.0, 3.0):
    l_ = bpy.data.lights.new("Bus warm", "POINT")
    l_.energy, l_.color, l_.shadow_soft_size = 70, (1.0, 0.85, 0.65), 0.5
    lo = bpy.data.objects.new("Bus warm", l_)
    sc.collection.objects.link(lo)
    lo.location = (xx, AISLE_Y, 2.6)
    lo.parent = BUS
    BUS_LIGHTS.append(lo)
DRIVER = (BUS_X1 - 1.05, YL - 0.55)
bbox_((DRIVER[0] - 0.05, DRIVER[1], SEAT_TOP + 0.02), (0.5, 0.5, 0.12), "seat2", "Driver seat")
bbox_((DRIVER[0] - 0.3, DRIVER[1], SEAT_TOP + 0.4), (0.1, 0.5, 0.75), "seat2", "Driver back")
bbox_((BUS_X1 - 0.3, BY, 1.25), (0.45, BW - 0.15, 0.25), "dash", "Dashboard")
WHEEL_C = (DRIVER[0] + 0.5, DRIVER[1], SEAT_TOP + 0.5)
bpy.ops.mesh.primitive_torus_add(location=WHEEL_C, major_radius=0.22, minor_radius=0.025,
                                 rotation=(0, math.radians(60), 0))
sw = bpy.context.object
sw.name = "Steering wheel"
sw.data.materials.append(M_["dash"])
sw.parent = BUS
SET.append(sw)
cyl(WHEEL_C, (BUS_X1 - 0.35, DRIVER[1], 1.1), 0.03, "dash", "Steering column", 8, parent=BUS)
bbox_((BUS_X1 - 0.5, BY - 0.6, 2.5), (0.04, 0.3, 0.12), "rim", "Mirror")
# headlight beams (spots on the bus)
HEADL = []
for y in (YR + 0.3, YL - 0.3):
    l_ = bpy.data.lights.new("Bus headlight", "SPOT")
    l_.energy, l_.spot_size, l_.spot_blend, l_.color = 4000, 0.8, 0.4, (1.0, 0.96, 0.85)
    lo = bpy.data.objects.new("Bus headlight", l_)
    sc.collection.objects.link(lo)
    lo.location = (BUS_X1 + 0.2, y, 0.8)
    lo.rotation_euler = (math.radians(80), 0, math.radians(-90))
    lo.parent = BUS
    HEADL.append(lo)
# the bus drives in from -X before it stops at the shelter: BUS location keyed (the world only moves later)
BUS_STOP_X = DOOR_X - (DOOR0 + DOOR1) / 2 + 0.2      # its door opposite the shelter door
T_ARRIVE0, T_ARRIVE1 = at("resc2") - 1.2, at("resc2") + 3.0
for t, x_ in ((0, -60.0), (T_ARRIVE0, -40.0), (T_ARRIVE1, BUS_STOP_X)):
    BUS.location = (x_, 0, 0)
    BUS.keyframe_insert("location", index=0, frame=fr(t))
for fc in fcurves_of(BUS):
    for k_ in fc.keyframe_points:
        k_.interpolation = "BEZIER"
        k_.handle_left_type = k_.handle_right_type = "AUTO_CLAMPED"
# the bus doors: open when it stops, shut after boarding
DOOR_OPEN0, DOOR_SHUT = T_ARRIVE1 + 0.3, T_GO - 0.8
for piv, j in DOOR_LEAF:
    sgn = -1 if j == 0 else 1          # the leaves swing outwards, clear of the seats
    for t, a in ((0, 0.0), (DOOR_OPEN0, 0.0), (DOOR_OPEN0 + 0.6, 1.45), (DOOR_SHUT, 1.45), (DOOR_SHUT + 0.6, 0.0)):
        piv.rotation_euler = (0, 0, sgn * a)
        piv.keyframe_insert("rotation_euler", index=2, frame=fr(t))
# the world slides past the bus once it leaves (MOVER x = -distance) + the wheels roll
for f in range(1, N + 2, 2):
    t = (f - 1) / FPS
    MOVER.location.x = -travelled(t)
    MOVER.keyframe_insert("location", index=0, frame=f)
interp(MOVER, "LINEAR")


def bus_x(t):
    sc.frame_set(fr(t))
    return BUS.location.x


roll = 0.0
prev_x = None
for f in range(1, N + 2, 2):
    t = (f - 1) / FPS
    sc.frame_set(f)
    bx = BUS.location.x + travelled(t)
    if prev_x is not None:
        roll += (bx - prev_x) / 0.5
    prev_x = bx
    for piv, xx, y in WHEELS:
        piv.rotation_euler = (0, roll, 0)
        piv.keyframe_insert("rotation_euler", index=1, frame=f)
for piv, *_ in WHEELS:
    interp(piv, "LINEAR")
# tyre burst: the rear right wheel goes flat, the bus leans and shakes
FLAT = [w for w in WHEELS if w[1] < 0 and w[2] < BY][0][0]
for t, s_ in ((T_BANG, 1.0), (T_BANG + 0.2, 0.55)):
    FLAT.scale = (1, 1, s_)
    FLAT.keyframe_insert("scale", index=2, frame=fr(t))
for t, rx, rz in ((T_BANG, 0, 0), (T_BANG + 0.25, -0.05, 0.03), (T_BANG + 0.7, -0.03, -0.05),
                  (T_BANG + 1.2, -0.06, 0.04), (T_STOP, -0.055, 0.08), (END, -0.055, 0.08)):
    BUS.rotation_euler = (rx, 0, rz)
    BUS.keyframe_insert("rotation_euler", index=0, frame=fr(t))
    BUS.keyframe_insert("rotation_euler", index=2, frame=fr(t))
# engine shake on the bus while it drives (tiny, so the camera inside feels the road)
for f in range(fr(T_GO), fr(T_STOP), 3):
    t = (f - 1) / FPS
    if t < T_BANG:
        BUS.location.z = 0.012 * math.sin(t * 23) + 0.008 * math.sin(t * 37)
        BUS.keyframe_insert("location", index=2, frame=f)
BUS.location.z = 0
BUS.keyframe_insert("location", index=2, frame=fr(T_STOP))

# ================================================================== the dogs (procedural, bus coordinates = world)
DOGS = []


def build_dog(i):
    root = P.empty(f"Dog {i}")
    parts = []

    def add(o, parent):
        o.parent = parent
        parts.append(o)
        return o
    body = add(P.sphere((0, 0, 0), 0.4, M_["fur"], f"Dog {i} body", scale=(1.7, 0.75, 0.8)), root)
    add(P.sphere((0.45, 0, 0.08), 0.36, M_["fur2"], f"Dog {i} chest", scale=(1.0, 0.9, 1.05)), root)
    for k in range(6):                                   # spiky ridge on the back
        add(P.cyl((-0.45 + k * 0.17, 0, 0.27), (-0.5 + k * 0.17, 0, 0.45 + 0.05 * (k % 2)), 0.035, M_["fur"],
                  f"Dog {i} spike"), root)
    neck = P.empty(f"Dog {i} neck", (0.7, 0, 0.2))
    neck.parent = root
    add(P.sphere((0.25, 0, 0.05), 0.24, M_["fur"], f"Dog {i} head", scale=(1.25, 0.95, 0.9)), neck)
    add(P.sphere((0.52, 0, -0.02), 0.13, M_["fur2"], f"Dog {i} snout", scale=(1.5, 0.85, 0.7)), neck)
    for dy in (-0.11, 0.11):
        add(P.sphere((0.36, dy, 0.13), 0.045, M_["dog_eye"], f"Dog {i} eye"), neck)
        add(P.cyl((0.12, dy, 0.18), (0.05, dy * 1.3, 0.42), 0.05, M_["fur"], f"Dog {i} ear"), neck)
    jaw = P.empty(f"Dog {i} jaw", (0.32, 0, -0.08))
    jaw.parent = neck
    add(P.sphere((0.22, 0, -0.03), 0.11, M_["gum"], f"Dog {i} jaw mesh", scale=(1.6, 0.8, 0.45)), jaw)
    for k in range(4):
        for dy in (-0.06, 0.06):
            add(P.cyl((0.1 + k * 0.07, dy, 0.0), (0.1 + k * 0.07, dy, 0.07), 0.012, M_["teeth"], f"Dog {i} tooth"), jaw)
    tail = P.empty(f"Dog {i} tail", (-0.65, 0, 0.12))
    tail.parent = root
    add(P.cyl((0, 0, 0), (-0.45, 0, 0.2), 0.05, M_["fur"], f"Dog {i} tail mesh"), tail)
    legs = []
    for lx in (0.45, -0.45):
        for ly in (-0.17, 0.17):
            hip = P.empty(f"Dog {i} leg", (lx, ly, -0.1))
            hip.parent = root
            add(P.cyl((0, 0, 0), (0, 0, -0.32), 0.07, M_["fur"], f"Dog {i} thigh"), hip)
            knee = P.empty(f"Dog {i} knee", (0, 0, -0.32))
            knee.parent = hip
            add(P.cyl((0, 0, 0), (0, 0, -0.3), 0.045, M_["fur"], f"Dog {i} shin"), knee)
            add(P.sphere((0.04, 0, -0.31), 0.06, M_["fur2"], f"Dog {i} paw", scale=(1.4, 1, 0.6)), knee)
            legs.append((hip, knee, lx > 0, ly))
    root.scale = (1.05, 1.05, 1.05)
    return dict(root=root, neck=neck, jaw=jaw, tail=tail, legs=legs, parts=parts, body=body)


def dog_frame(d, f, pos, heading, gait, phase, bite=0.0, lunge=0.0):
    """gait: 0 stand .. 1 full gallop; heading in degrees (0 = +X)."""
    t = (f - 1) / FPS
    w = 2 * math.pi * 3.2 * t + phase
    bob = 0.08 * gait * abs(math.sin(w))
    r = d["root"]
    r.location = (pos[0], pos[1], 0.68 + bob + 0.15 * lunge)
    r.rotation_euler = (0, -0.12 * gait * math.sin(w) - 0.25 * lunge, math.radians(heading))
    r.keyframe_insert("location", frame=f)
    r.keyframe_insert("rotation_euler", frame=f)
    for hip, knee, front, ly in d["legs"]:
        ph = w + (0 if front else math.pi) + (0.35 if ly > 0 else 0)
        a = gait * 0.75 * math.sin(ph) - (0.4 * lunge if front else 0)
        hip.rotation_euler = (0, a, 0)
        knee.rotation_euler = (0, -gait * 0.6 * max(0.0, math.sin(ph + 1.2)) * (1 if front else -1), 0)
        hip.keyframe_insert("rotation_euler", index=1, frame=f)
        knee.keyframe_insert("rotation_euler", index=1, frame=f)
    snap = max(bite * (0.5 + 0.5 * math.sin(t * 22 + phase)), 0.25 * gait)
    d["jaw"].rotation_euler = (0, 0.55 * snap, 0)
    d["jaw"].keyframe_insert("rotation_euler", index=1, frame=f)
    d["neck"].rotation_euler = (0, -0.15 * gait * math.sin(w + 0.6) + 0.35 * bite * math.sin(t * 11 + phase), 0)
    d["neck"].keyframe_insert("rotation_euler", index=1, frame=f)
    d["tail"].rotation_euler = (0, 0.3 * math.sin(w), 0.4 * math.sin(w * 0.5))
    d["tail"].keyframe_insert("rotation_euler", frame=f)


WB = lambda x, y, z=0.0: (BUS_STOP_X + x, y, z)       # noqa: E731  bus local -> world (after it has stopped)
# six dogs: run beside the bus from T_DOGS; two of them at the right tyres (one bites the rear one before the bang)
DOG_PLAN = [  # (bus-local x, y, phase)
    (-3.4, YR - 0.9, 0.0), (3.0, YR - 1.0, 1.3), (-1.0, YR - 2.4, 2.1), (1.5, YL + 1.2, 0.7), (-4.5, YL + 1.6, 2.8),
    (5.5, YR - 2.8, 1.9)]
for i, (lx, ly, ph) in enumerate(DOG_PLAN):
    d = build_dog(i)
    DOGS.append(d)
    rr = random.Random(90 + i)
    for f in range(fr(T_DOGS - 1.0), N + 1, 2):
        t = (f - 1) / FPS
        come = seg(t, T_DOGS + i * 0.25, T_DOGS + 1.6 + i * 0.25)     # out of the trees towards the bus
        x = lx - (1 - come) * 6.0 + 0.6 * math.sin(t * 1.3 + ph)
        y = ly - (1 - come) * (8.0 if ly < BY else -8.0)
        gait = 1.0
        bite = lunge = 0.0
        if i == 0 and T_BANG - 2.2 < t < T_BANG:                      # at the rear right tyre
            bite = 1.0
            y = YR - 0.6 + 0.1 * math.sin(t * 9)
            x = -3.4 + 0.3
        if i == 1 and at("me5") - 0.3 < t < T_BANG:
            bite = 0.8
            y = YR - 0.75
            x = 3.4 + 0.5
        heading = 0.0
        if t > T_STOP:                                                 # circling the stopped bus, slowly
            u = (t - T_STOP) * 0.18 + i * 1.05
            rad = 3.2 + 0.4 * math.sin(i)
            x = 6.3 * math.cos(u) * 1.0
            y = BY + rad * math.sin(u) * 1.0
            heading = math.degrees(u) + 90
            gait = 0.45
            bite = 0.3 if i % 2 else 0.0
        elif t > T_BANG:
            gait = 1.0 - 0.4 * seg(t, T_BANG, T_STOP)
        wx, wy, _ = WB(x, y)
        dog_frame(d, f, (wx, wy), heading, gait, ph, bite, lunge)
    show([d["root"]] + d["parts"], [(T_DOGS - 1.0, END + 1)])
for d in DOGS:
    for o in [d["root"], d["neck"], d["jaw"], d["tail"]] + [h for h, *_ in d["legs"]] + [k for _, k, *_ in d["legs"]]:
        interp(o, "LINEAR")

# ================================================================== cast
KEYS = ["me", "mom", "lena", "guard", "oldman", "rescuer"]
CH = {}
for k in KEYS:
    ch = cast.spawn(k)
    T.register(ch, k, realistic=True)
    LK.before(ch, k)
    CH[k] = ch
PASSENGERS = []
for i in range(1, 6):
    ch = cast.spawn_extra("passerby", i, quality="extra")
    T.register(ch, "me", realistic=True)
    T.SKIN[ch.name] = ((0.72, 0.44, 0.3), {})
    CH[f"p{i}"] = ch
    PASSENGERS.append(f"p{i}")
M_ = mats()          # cast building purges unused materials: re-create for later props
DIRTY = set()


def clip(name):
    return CLIP[name]


def sync(who=None):
    for w in ([who] if who else list(DIRTY)):
        if w in DIRTY:
            MC.flush(CH[w])
            DIRTY.discard(w)


def act(who, name, t0, t1, pos, facing, speed=SPEED, **kw):
    n = fr(t1) - fr(t0)
    if n <= 0:
        return
    MC.apply(CH[who], clip(name), start=fr(t0), length=n, offset=pos, facing=facing, speed=speed, **kw)
    DIRTY.add(who)


SIT_REF = {}


def sit_dz(who):
    """offset z that puts this character's sitting pelvis on a seat surface at z = 0 (+ seat top)."""
    ch = CH[who]
    leg = ch.thigh_len + ch.calf_len
    return 0.075 - 0.394 * leg / 0.86


def sit(who, t0, t1, seat, facing, top, src_from=0.0, speed=1.0):
    act(who, "sitting_idle", t0, t1, (seat[0], seat[1], top + sit_dz(who)), facing, speed=speed, loop=True,
        src_from=src_from)


def pos_at(who, t):
    sync(who)
    sc.frame_set(fr(t))
    rig = CH[who].rig
    p = rig.matrix_world @ rig.pose.bones["pelvis"].head
    return (p.x, p.y)


def facing_at(who, t):
    sync(who)
    sc.frame_set(fr(t))
    return math.degrees(CH[who].rig.rotation_euler.z - math.pi)


NAT = {}


def natural_speed(who, clipname):
    key = (who, clipname)
    if key in NAT:
        return NAT[key]
    c = clip(clipname)
    src_leg = (c.rest["LeftUpLeg"].translation - c.rest["LeftFoot"].translation).length
    tr = CH[who].rig.data.bones
    tgt_leg = (tr["thigh_l"].matrix_local.translation - tr["foot_l"].matrix_local.translation).length
    hips, feet = c.hips, c.feet
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
    NAT[key] = v * tgt_leg / max(1e-6, src_leg)
    return NAT[key]


def walk(who, t0, t1, pts, z=0.0, clipname="walking", end_face=None, turn=0.35):
    """`who` walks along the polyline pts (feet keep their stride) from t0 to t1 at floor height z."""
    pts = list(pts)
    P_ = [Vector((p[0], p[1], z)) for p in pts]
    d0 = P_[1] - P_[0]
    f_prev = math.degrees(math.atan2(-d0.x, d0.y))
    if t0 > 0.05:
        f_prev = facing_at(who, t0 - 1.0 / FPS)
    L = [0.0]
    for a, b in zip(P_, P_[1:]):
        L.append(L[-1] + (b - a).length)
    total = max(1e-4, L[-1])
    n = fr(t1) - fr(t0)
    dur = n / FPS
    ease = min(0.25, dur * 0.2)
    vmax = total / (dur - ease)

    def dist(tt):
        if tt < ease:
            return 0.5 * vmax * tt * tt / ease
        if tt > dur - ease:
            r_ = dur - tt
            return total - 0.5 * vmax * r_ * r_ / ease
        return vmax * (tt - ease / 2)

    def at_(d):
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
        p = at_(d)
        q = at_(min(total, d + 0.35)) - at_(max(0.0, d - 0.05))
        if q.length < 1e-4:
            q = P_[-1] - P_[-2]
        fac = math.degrees(math.atan2(-q.x, q.y))
        if tt < turn:
            fac = f_prev + angdiff(f_prev, fac) * seg(tt, 0, turn)
        if end_face is not None and tt > dur - turn:
            fac = fac + angdiff(fac, end_face) * seg(tt, dur - turn, dur)
        return tuple(p), fac

    sp = vmax / natural_speed(who, clipname)
    sp = max(0.5, min(2.2, sp))
    MC.apply(CH[who], clip(clipname), start=fr(t0), length=n, offset=tuple(P_[0]), facing=f_prev,
             speed=sp, in_place=True, loop=True, place=place)
    DIRTY.add(who)


def face(a, b):
    return math.degrees(math.atan2(-(b[0] - a[0]), b[1] - a[1]))


FWD = -90.0                         # facing the front of the bus (+X)
A_, E_ = at, end_of
FL = FLOOR                          # bus floor height in the world
# ---- seats in the bus (world)
S = {k: WB(*SEATS[v]) for k, v in {
    "lena": (8, "R", "win"), "mom": (8, "R", "aisle"), "me": (8, "L", "aisle"), "guard": (8, "L", "win"),
    "oldman": (7, "L", "aisle"), "p1": (1, "L", "win"), "p2": (2, "R", "aisle"), "p3": (5, "L", "win"),
    "p4": (6, "R", "aisle"), "p5": (3, "L", "win")}.items()}
OLD_ST = WB(ROWS[7] + 0.35, AISLE_Y)          # the old man stands in the aisle, holding on
BUS_DOOR_OUT = WB((DOOR0 + DOOR1) / 2, YR - 0.7)
BUS_DOOR_IN = WB((DOOR0 + DOOR1) / 2 - 0.3, AISLE_Y)
SH_DOOR_IN = (DOOR_X, SY1 - 0.9)
SH_DOOR_OUT = (DOOR_X, SY1 + 1.2)
T_SIT = at("lena3") - 0.4
T_WALK_OUT = T_DOOR + 1.6

# ---- the people already on the bus: seated from the start
for i, p in enumerate(PASSENGERS):
    sit(p, 0, END, S[p][:2], FWD, SEAT_TOP, src_from=i * 0.7, speed=0.8)
act("oldman", "breathing_idle", 0, A_("old1") - 0.2, OLD_ST, FWD, loop=True, speed=0.8)
act("oldman", "head_nod_yes", A_("old1") - 0.2, E_("old1") + 0.4, OLD_ST, face(OLD_ST, BUS_DOOR_IN), speed=0.9)
act("oldman", "breathing_idle", E_("old1") + 0.4, A_("old2") - 0.2, OLD_ST, FWD, loop=True, speed=0.8)
act("oldman", "thinking", A_("old2") - 0.2, E_("old2") + 0.6, OLD_ST, FWD + 15, speed=0.9)
act("oldman", "breathing_idle", E_("old2") + 0.6, A_("old3") - 0.4, OLD_ST, FWD, loop=True, speed=0.8)
act("oldman", "nervously_look_around", A_("old3") - 0.4, T_BANG, OLD_ST, FWD - 30, speed=0.9, in_place=True)
act("oldman", "terrified", T_BANG, END, OLD_ST, FWD, speed=1.0, src_from=3.0, loop=True, in_place=True)

# ---- me: at the table with the radio; to the door; out; on the bus
CR = CRATES["me"]
sit("me", 0, T_LOUD, CR, 0, 0.4)
act("me", "nervously_look_around", T_LOUD, at("lena2") + 0.2, (CR[0] - 0.2, CR[1] - 0.1, 0), 20, speed=1.0)
act("me", "breathing_idle", at("lena2") + 0.2, end_of("guard3"), (CR[0] + 0.3, CR[1] + 0.4, 0), face(CR, SH_DOOR_IN))
ME_DOOR = (DOOR_X + 0.75, SY1 - 0.8)
walk("me", end_of("guard3"), at("me2") + 0.2, [(CR[0] + 0.3, CR[1] + 0.4), ME_DOOR], end_face=0)
act("me", "opening_door_inwards", at("me2") + 0.2, T_WALK_OUT, ME_DOOR + (0,), 0, speed=1.3, in_place=True)
walk("me", T_WALK_OUT, T_BOARD + 2.4, [(DOOR_X + 0.3, SY1 - 0.4), (DOOR_X + 0.3, SY1 + 1.4),
                                       BUS_DOOR_OUT[:2]], end_face=0)
walk("me", T_IN, T_SIT, [BUS_DOOR_IN[:2], (S["me"][0] + 0.1, AISLE_Y)], z=FL, end_face=FWD)
sit("me", T_SIT, at("me4") - 0.2, S["me"][:2], FWD, SEAT_TOP)
ME_AISLE = WB(ROWS[8] + 1.25, AISLE_Y + 0.05, FL)
act("me", "talking_phone_pacing", at("me4") - 0.2, at("resc5") + 0.3, ME_AISLE, 90,
    speed=1.0, src_from=8.0, in_place=True)
sit("me", at("resc5") + 0.3, at("me5") - 0.6, S["me"][:2], FWD, SEAT_TOP)
act("me", "nervously_look_around", at("me5") - 0.6, T_STOP, ME_AISLE, FWD - 70, speed=1.2, in_place=True)
act("me", "male_action_pose", T_STOP, at("radio2") + 0.5, ME_AISLE, FWD + 60)
act("me", "talking_phone_pacing", at("radio2") + 0.5, END, ME_AISLE, 90, speed=0.9, src_from=8.0, in_place=True)

# ---- Lena: on the bottom bunk; up; holding on to Mom; on the bus by the window
BUNK_SEAT = (BX + 0.4, -9.0)
sit("lena", 0, at("lena2") - 0.4, BUNK_SEAT, -90, 0.59)
act("lena", "hands_forward_gesture", at("lena2") - 0.4, end_of("lena2") + 0.4, (BUNK_SEAT[0] + 0.45, -8.9, 0), -70,
    speed=1.2)
act("lena", "breathing_idle", end_of("lena2") + 0.4, T_WALK_OUT + 0.6, (BUNK_SEAT[0] + 0.5, -8.6, 0),
    face((BUNK_SEAT[0] + 0.5, -8.6), SH_DOOR_IN))
walk("lena", T_WALK_OUT + 0.6, T_BOARD + 3.0, [(BUNK_SEAT[0] + 0.5, -8.6), (-0.3, -7.0), (DOOR_X - 0.1, SY1 - 0.6),
                                                (DOOR_X - 0.1, SY1 + 1.3), (BUS_DOOR_OUT[0] - 0.6, BUS_DOOR_OUT[1] - 0.4)],
     end_face=0)
walk("lena", T_IN + 0.4, T_SIT, [BUS_DOOR_IN[:2], (S["lena"][0] + 0.1, AISLE_Y - 0.1)], z=FL)
sit("lena", T_SIT, at("lena5") - 0.2, S["lena"][:2], FWD, SEAT_TOP)
act("lena", "nervously_look_around", at("lena5") - 0.2, T_BANG, (S["lena"][0] + 0.15, S["lena"][1] + 0.2, FL), FWD - 80,
    speed=1.0)
act("lena", "terrified", T_BANG, END, (S["mom"][0] - 0.05, AISLE_Y, FL), FWD, speed=1.1, src_from=5.0,
    loop=True, in_place=True)

# ---- Mom: by the shelves; to the guard; out; on the bus next to Lena
MS = (-0.2, -10.7)
act("mom", "breathing_idle", 0, at("mom1") - 0.3, MS + (0,), 180)
act("mom", "thinking", at("mom1") - 0.3, T_LOUD, MS + (0,), face(MS, CR), speed=1.0)
act("mom", "nervously_look_around", T_LOUD, at("guard2"), MS + (0,), face(MS, SH_DOOR_IN), speed=1.0)
walk("mom", at("guard2"), at("mom2") + 0.1, [MS, (2.4, -9.9), (2.4, -7.6)], end_face=face((2.4, -7.6), (2.9, -6.4)))
act("mom", "thinking", at("mom2") + 0.1, T_WALK_OUT + 0.4, (2.4, -7.6, 0), face((2.4, -7.6), (2.9, -6.4)), speed=1.1)
walk("mom", T_WALK_OUT + 0.4, T_BOARD + 2.9, [(2.4, -7.6), (DOOR_X + 0.15, SY1 - 0.5), (DOOR_X + 0.15, SY1 + 1.2),
                                              (BUS_DOOR_OUT[0] - 1.1, BUS_DOOR_OUT[1] - 0.6)], end_face=0)
walk("mom", T_IN + 0.8, T_SIT, [BUS_DOOR_IN[:2], (S["mom"][0] + 0.2, AISLE_Y + 0.05)], z=FL)
sit("mom", T_SIT, at("mom5") - 0.4, S["mom"][:2], FWD, SEAT_TOP)
act("mom", "pushing_2", at("mom5") - 0.4, END, (S["mom"][0] + 0.5, AISLE_Y + 0.05, FL), 90, speed=0.9,
    loop=True, in_place=True)

# ---- the guard: on a crate by the door, then on his feet
GC = CRATES["guard"]
sit("guard", 0, T_LOUD + 0.3, GC, 200, 0.4)
act("guard", "breathing_idle", T_LOUD + 0.3, at("guard2") - 0.2, (GC[0] - 0.5, GC[1] + 0.1, 0), face(GC, SH_DOOR_IN))
GS = (DOOR_X + 0.6, SY1 - 0.65)
walk("guard", at("guard2") - 0.2, at("guard2") + 0.6, [(GC[0] - 0.5, GC[1] + 0.1), GS], end_face=180)
act("guard", "hands_forward_gesture", at("guard2") + 0.6, end_of("resc2"), GS + (0,), 200, speed=1.0)
act("guard", "head_nod_yes", at("guard3") - 0.2, end_of("guard3") + 0.3, GS + (0,), 10, speed=1.0)
act("guard", "breathing_idle", end_of("guard3") + 0.3, T_WALK_OUT + 1.0, GS + (0,), 10)
walk("guard", T_WALK_OUT + 1.0, T_BOARD + 3.3, [GS, (DOOR_X, SY1 - 0.4), (DOOR_X, SY1 + 1.6),
                                                (BUS_DOOR_OUT[0] + 0.9, BUS_DOOR_OUT[1] - 0.8)], end_face=10)
walk("guard", T_IN + 1.2, T_SIT, [BUS_DOOR_IN[:2], (S["guard"][0] + 0.3, AISLE_Y + 0.05)], z=FL)
sit("guard", T_SIT, T_BANG, S["guard"][:2], FWD, SEAT_TOP)
act("guard", "male_action_pose", T_BANG, END, WB(ROWS[8] + 1.95, AISLE_Y - 0.1, FL), 180)
# his hand trembles (n2, lena1): noise on the right forearm and hand while he sits
_trem = [(at("n2") - 0.3, end_of("guard1") + 0.3)]

# ---- the rescuer: driving; at the bus door; driving again
DS = WB(*DRIVER)
sit("rescuer", 0, at("resc3") - 1.4, DS[:2], FWD, SEAT_TOP + 0.05)
RD = (BUS_DOOR_OUT[0] + 0.5, BUS_DOOR_OUT[1] - 0.3)
act("rescuer", "hands_forward_gesture", at("resc3") - 1.4, at("resc3") + 1.6, RD + (0,), 180, speed=1.0)
act("rescuer", "dismissing_gesture", at("resc3") + 1.6, T_BOARD + 3.5, RD + (0,), 200, speed=0.9, loop=True)
sit("rescuer", T_IN - 0.2, END, DS[:2], FWD, SEAT_TOP + 0.05)

PRESENT = {k: [(0, END)] for k in CH}
for k in PASSENGERS + ["oldman", "rescuer"]:          # nobody floats in the air while the bus drives in
    PRESENT[k] = [(T_ARRIVE1, END)]
# the steel door opens inwards while I pull it
for t, a in ((0, 0.0), (T_DOOR, 0.0), (T_DOOR + 1.1, -1.65)):
    HINGE.rotation_euler = (0, 0, a)
    HINGE.keyframe_insert("rotation_euler", index=2, frame=fr(t))

WORRY = {"me": [(0, 0.9), (at("resc1"), 0.5), (at("guard2"), 1.2), (at("n3"), 0.8), (at("radio1"), 1.3), (T_DOGS, 2.0)],
         "mom": [(0, 1.2), (at("lena2"), 0.6), (at("guard2"), 1.4), (at("n4"), 1.0), (at("mom4"), 0.8), (T_DOGS, 2.0)],
         "lena": [(0, 0.6), (at("lena2"), 0.0), (at("n3"), 0.8), (at("lena4"), 1.0), (at("lena5"), 1.6), (T_DOGS, 2.0)],
         "guard": [(0, 1.0), (at("guard2"), 1.6), (at("guard3"), 0.8), (T_DOGS, 1.5)],
         "oldman": [(0, 0.8), (at("old3"), 1.6), (T_DOGS, 2.0)], "rescuer": [(0, 0.5), (at("resc5"), 1.2), (T_DOGS, 1.8)]}
for p in PASSENGERS:
    WORRY[p] = [(0, 0.9), (T_DOGS, 2.0)]


def worry(who, t):
    pts = WORRY[who]
    v = pts[0][1]
    for (a, va), (b, vb) in zip(pts, pts[1:] + [(999, pts[-1][1])]):
        if a <= t < b:
            v = va + (vb - va) * seg(t, a, min(b, a + 0.8))
    return v


# ================================================================== props in hands
def in_hand(obj, who, bone, t_ref):
    sync(who)
    rig = CH[who].rig
    sc.frame_set(fr(t_ref))
    hm = rig.matrix_world @ rig.pose.bones[bone].matrix
    con = obj.constraints.new("CHILD_OF")
    con.target, con.subtarget = rig, bone
    con.inverse_matrix = hm.inverted()


def radio_mesh(name):
    b = P.box((0, 0, 0), (0.07, 0.04, 0.2), M_["radio"], name)
    a = P.cyl((0.02, 0, 0.1), (0.02, 0, 0.3), 0.006, M_["radio"], name + " antenna")
    a.parent = b
    l_ = P.sphere((-0.02, -0.022, 0.07), 0.008, M_["led"], name + " led")
    l_.parent = b
    return [b, a, l_]


# the radio on the shelter table, then in my hand from the moment I get up
rt = radio_mesh("Radio table")
rt[0].location = RADIO_T
rt[0].rotation_euler = (math.radians(80), 0, 0.4)
rt[0].parent = MOVER
show(rt, [(0, at("lena2") + 0.2)])
rh = radio_mesh("Radio hand")
sync()
sc.frame_set(fr(at("me2") - 0.5))
rig_ = CH["me"].rig
hm = rig_.matrix_world @ rig_.pose.bones["hand_l"].matrix
_l, _r, _s = hm.decompose()
rh[0].matrix_world = Matrix.LocRotScale(_l + _r @ Vector((0, 0.09, 0.03)), _r, (1, 1, 1))
in_hand(rh[0], "me", "hand_l", at("me2") - 0.5)
show(rh, [(at("lena2") + 0.2, END)])
# the guard's hard hat
hat = P.sphere((0, 0, 0), 0.135, M_["hardhat"], "Hard hat", scale=(1.05, 1.15, 0.7))
brim = P.cyl((0, 0, -0.03), (0, 0, -0.01), 0.17, M_["hardhat"], "Hard hat brim")
brim.parent = hat
sc.frame_set(1)
gh = CH["guard"].rig.matrix_world @ CH["guard"].rig.pose.bones["head"].matrix
_l, _r, _s = gh.decompose()
hat.matrix_world = Matrix.LocRotScale(_l + _r @ Vector((0, 0.2, 0.01)), _r @ Matrix.Rotation(-math.pi / 2, 4, "X").to_quaternion(), (1, 1, 1))
in_hand(hat, "guard", "head", 0.0)
# radiation masks (the user: the air is still radioactive, so everyone on the rescue bus wears one).
# The rescuer, the old man and the passengers wear theirs all the time; we put ours on when we board.
import masks as MK  # noqa: E402
MKM = MK.materials()
for who in ["rescuer", "oldman"] + PASSENGERS + ["me", "mom", "lena", "guard"]:
    kind = "dust" if who in ("p2", "p4") else "resp"
    on = 1 if who in ["rescuer", "oldman"] + PASSENGERS else fr(T_IN)
    MK.follow(MK.mask(CH[who].rig, kind, MKM, who), CH[who].body, on)
# driver's hands on the steering wheel (IK) while he drives
WHL = {}
for side, dy in (("l", 0.16), ("r", -0.16)):
    e_ = P.empty(f"Wheel grip {side}", (WHEEL_C[0] + BUS_STOP_X - 0.02, WHEEL_C[1] + dy, WHEEL_C[2] + 0.03))
    e_.parent = None
    WHL[side] = e_
    ik = CH["rescuer"].rig.pose.bones[f"lowerarm_{side}"].constraints.new("IK")
    ik.target = e_
    ik.chain_count = 2
    ik.influence = 1.0
    ik.keyframe_insert("influence", frame=1)
    for t, v in ((at("resc3") - 1.5, 1.0), (at("resc3") - 1.4, 0.0), (T_IN - 0.2, 0.0), (T_IN - 0.1, 1.0)):
        ik.influence = v
        ik.keyframe_insert("influence", frame=fr(t))
# steering wheel and grips turn when the tyre bursts
STEER = P.empty("Steer", (WHEEL_C[0] + BUS_STOP_X, WHEEL_C[1], WHEEL_C[2]))
sw.parent = None
sw.location = (WHEEL_C[0] + BUS_STOP_X, WHEEL_C[1], WHEEL_C[2])
for o in (sw, WHL["l"], WHL["r"]):
    mw = o.matrix_world.copy()
    o.parent = STEER
    o.matrix_world = mw
STEER.rotation_mode = "XYZ"
for t, a in ((0, 0), (T_BANG, 0), (T_BANG + 0.3, 0.9), (T_BANG + 0.7, -0.7), (T_BANG + 1.1, 0.6), (T_STOP, 0.3)):
    STEER.rotation_euler = (a * 0.5, 0, 0)
    STEER.keyframe_insert("rotation_euler", index=0, frame=fr(t))
# the guard's trembling hand: noise on top of the mocap
for fc in fcurves_of(CH["guard"].rig):
    if 'hand_r' in fc.data_path and "rotation_quaternion" in fc.data_path and fc.array_index in (1, 3):
        md = fc.modifiers.new("NOISE")
        md.scale, md.strength = 1.2, 0.25
        md.use_restricted_range = True
        md.frame_start, md.frame_end = fr(_trem[0][0]), fr(_trem[0][1])
        md.blend_in = md.blend_out = 4

# ================================================================== camera
def H(who, t, dz=0.06):
    sync(who)
    sc.frame_set(fr(t))
    r_ = CH[who].rig
    return tuple(r_.matrix_world @ r_.pose.bones["head"].head + Vector((0, 0, dz)))


def hand(who, t, side="l"):
    sync(who)
    sc.frame_set(fr(t))
    r_ = CH[who].rig
    return tuple(r_.matrix_world @ r_.pose.bones[f"hand_{side}"].head)


def mid(a, b):
    return tuple((Vector(a) + Vector(b)) / 2)


def add(a, d):
    return tuple(Vector(a) + Vector(d))


sync()
SM, SL, SO, SG = S["me"], S["lena"], S["oldman"], S["mom"]
SHOTS = []


def shot(t0, t1, c0, a0, lens, c1=None, a1=None):
    SHOTS.append((t0, t1, tuple(c0), tuple(c1 or c0), tuple(a0), tuple(a1 or a0), lens))


A = at
shot(0, A("n2") - 0.2, (5.6, -11.1, 2.25), (0.6, -7.6, 0.8), 18, c1=(5.2, -10.6, 2.0))
shot(A("n2") - 0.2, A("lena1") - 0.2, (GC[0] - 0.55, GC[1] - 1.25, 0.85), (GC[0] - 0.1, GC[1] - 0.15, 0.6), 38,
     c1=(GC[0] - 0.45, GC[1] - 1.1, 0.8))
shot(A("lena1") - 0.2, A("guard1") - 0.1, (0.25, -9.3, 0.85), H("lena", A("lena1")), 40, c1=(0.1, -9.25, 0.85))
shot(A("guard1") - 0.1, A("mom1") - 0.2, (2.75, -7.75, 1.05), H("guard", A("guard1")), 40)
shot(A("mom1") - 0.2, A("me1") - 0.2, (1.0, -9.9, 1.45), H("mom", A("mom1") + 0.5), 34, c1=(0.85, -9.95, 1.45))
shot(A("me1") - 0.2, T_LOUD, (1.75, -9.55, 1.35), RADIO_T, 32, c1=(1.6, -9.4, 1.3))
shot(T_LOUD, A("lena2") - 0.4, (0.3, -10.95, 1.7), (2.0, -5.7, 1.5), 20)
shot(A("lena2") - 0.4, A("guard2") - 0.2, (0.9, -8.2, 1.0), H("lena", A("lena2") + 0.3), 30)
shot(A("guard2") - 0.2, A("resc2") - 0.2, (1.3, -8.3, 1.5), H("guard", A("guard2") + 0.8), 28,
     c1=(1.45, -8.1, 1.5))
shot(A("resc2") - 0.2, A("mom2") - 0.1, (7.0, -4.2, 0.7), (-14, 0.5, 1.8), 24, a1=(-2.0, 0.0, 1.6))
shot(A("mom2") - 0.1, A("guard3") - 0.2, (3.9, -8.7, 1.5), mid(H("mom", A("mom2")), H("guard", A("mom2"))), 28)
shot(A("guard3") - 0.2, A("me2") - 0.2, (2.95, -7.45, 0.95), (2.0, -5.7, 2.2), 24)
shot(A("me2") - 0.2, T_OUT, (3.7, -7.9, 1.6), (2.2, -5.6, 1.25), 24)
shot(T_OUT, A("resc3") - 0.2, (DOOR_X + 9.0, 3.6, 1.8), (DOOR_X, -5.2, 1.2), 22, c1=(DOOR_X + 8.0, 3.2, 1.7))
shot(A("resc3") - 0.2, T_IN, (BUS_DOOR_OUT[0] + 5.0, -4.85, 1.6), H("rescuer", A("resc3")), 26,
     a1=add(BUS_DOOR_OUT, (-0.3, 0, 1.2)))
shot(T_IN, A("lena3") - 0.2, (OLD_ST[0] + 1.3, YL - 0.35, FL + 1.65), H("oldman", T_IN + 1.0), 26,
     a1=H("oldman", A("lena3") - 1))
shot(A("lena3") - 0.2, A("resc4") - 0.2, (SL[0] + 1.0, (SL[1] + SG[1]) / 2, FL + 1.2), H("lena", A("lena3")), 32)
shot(A("resc4") - 0.2, T_GO + 0.4, WB(BUS_X1 - 2.5, AISLE_Y - 0.35, FL + 1.35), H("rescuer", A("resc4")), 26)
shot(T_GO + 0.4, A("n4") + 1.6, WB(16, -5.5, 3.5), WB(0, 0, 1.4), 22, c1=WB(11, -7.0, 2.6))
shot(A("n4") + 1.6, A("mom3") - 0.2, WB(-9, YR - 3.2, 1.2), WB(2, BY, 1.6), 22, c1=WB(-7.5, YR - 3.4, 1.4))
shot(A("mom3") - 0.2, A("me3") - 0.1, (SG[0] + 0.3, AISLE_Y + 0.15, FL + 1.3), (SG[0] - 3.0, YR - 9.0, 2.6), 26)
shot(A("me3") - 0.1, A("old2") - 0.2, (SM[0] + 1.1, SM[1] - 0.1, FL + 1.22), H("me", A("me3")), 32)
shot(A("old2") - 0.2, A("lena4") - 0.2, (OLD_ST[0] + 1.6, AISLE_Y + 0.05, FL + 1.6), H("oldman", A("old2")), 32)
shot(A("lena4") - 0.2, A("mom4") - 0.1, (SL[0] + 1.0, (SL[1] + SG[1]) / 2, FL + 1.2), H("lena", A("lena4")), 32)
shot(A("mom4") - 0.1, A("radio1") - 2.9, (SG[0] + 1.25, (SG[1] + SL[1]) / 2, FL + 1.25), mid(H("mom", A("mom4")), H("lena", A("mom4"))), 28)
shot(A("radio1") - 2.9, A("radio1") - 0.3, WB(-14, YL + 3.5, 4.5), WB(0, BY, 1.4), 24, c1=WB(-11, YL + 4.5, 3.5))
shot(A("radio1") - 0.3, A("me4") - 0.2, (SM[0] + 0.7, AISLE_Y - 0.25, FL + 1.35), hand("me", A("radio1")), 34)
shot(A("me4") - 0.2, A("resc5") - 0.1, (ME_AISLE[0] - 1.0, AISLE_Y - 0.05, FL + 1.55), H("me", A("me4") + 0.5), 28)
shot(A("resc5") - 0.1, T_FOREST, WB(BUS_X1 - 2.9, AISLE_Y + 0.2, FL + 1.4), WB(BUS_X1 + 12, BY, 1.0), 24)
shot(T_FOREST, A("lena5") - 0.2, WB(26, 4.5, 3.4), WB(0, BY, 1.3), 24, c1=WB(18, 3.6, 2.2))
shot(A("lena5") - 0.2, A("old3") - 0.3, (SL[0] + 0.45, AISLE_Y, FL + 1.35), (SL[0] + 4.0, YR - 9.0, 0.7), 28)
shot(A("old3") - 0.3, T_DOGS, (OLD_ST[0] + 1.6, AISLE_Y + 0.05, FL + 1.6), H("oldman", A("old3")), 32)
shot(T_DOGS, A("resc6"), WB(-9.5, YR - 6.5, 1.0), WB(-1.0, YR - 1.0, 0.8), 22)
shot(A("resc6"), A("me5") - 0.2, WB(BUS_X1 - 0.45, AISLE_Y - 0.6, FL + 1.45), H("rescuer", A("resc6")), 26)
shot(A("me5") - 0.2, T_BANG, WB(-0.6, YR - 2.3, 0.45), WB(-3.4, YR - 0.4, 0.55), 22)
shot(T_BANG, A("mom5") - 0.2, WB(ROWS[5], AISLE_Y - 0.1, FL + 1.75), WB(BUS_X1, AISLE_Y, FL + 1.0), 22)
shot(A("mom5") - 0.2, T_STOP + 0.3, (SG[0] + 1.2, YL - 0.5, FL + 1.9), mid(H("mom", A("mom5")), H("lena", A("mom5"))), 24)
shot(T_STOP + 0.3, A("radio2") - 0.3, WB(17, 2.0, 5.5), WB(0, BY, 0.8), 22, c1=WB(15, 1.6, 4.6))
shot(A("radio2") - 0.3, A("me6") - 0.2, (ME_AISLE[0] - 0.7, AISLE_Y - 0.3, FL + 1.55), H("me", A("radio2")), 40)
shot(A("me6") - 0.2, A("n7") - 0.2, (ME_AISLE[0] - 1.0, AISLE_Y - 0.05, FL + 1.55), H("me", A("me6")), 28)
shot(A("n7") - 0.2, END, WB(BUS_X1 - 2.3, AISLE_Y + 0.35, FL + 1.5), WB(BUS_X1 + 60, BY - 0.5, 1.0), 30,
     c1=WB(BUS_X1 - 1.7, AISLE_Y + 0.3, FL + 1.45))

cam = bpy.data.objects.new("Camera", bpy.data.cameras.new("Camera"))
sc.collection.objects.link(cam)
sc.camera = cam
cam.data.clip_start = 0.05
cam.data.clip_end = 400
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
    interp(owner, "LINEAR")
# shots that follow a moving thing: re-aim every 2 frames (the bus driving in, the people walking to the bus)
FOLLOW = {9: lambda t: (BUS.location.x + 2.0, BY, 1.6),
          13: lambda t: mid(H("me", t, 0), H("lena", t, 0)),
          14: lambda t: mid(H("rescuer", t, -0.1), H("mom", t, -0.1)),
          15: lambda t: mid(H("oldman", t), H("me", t))}
for i, fn in FOLLOW.items():
    t0, t1, c0, c1, *_ = SHOTS[i]
    for f in range(fr(t0), fr(t1), 2):
        t = (f - 1) / FPS
        sc.frame_set(f)
        u = (f - fr(t0)) / max(1, fr(t1) - fr(t0))
        c = Vector(c0).lerp(Vector(c1), u)
        cam.location = c
        cam.rotation_euler = (Vector(fn(t)) - c).to_track_quat("-Z", "Y").to_euler()
        cam.keyframe_insert("location", frame=f)
        cam.keyframe_insert("rotation_euler", frame=f)
interp(cam, "LINEAR")

# ---- per shot: keep only the characters the camera can see
from bpy_extras.object_utils import world_to_camera_view  # noqa: E402
BONES = ("head", "pelvis", "hand_r", "hand_l", "foot_r", "foot_l", "spine_03")
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
                if 0 < v.z < 80 and -0.3 < v.x < 1.3 and -0.3 < v.y < 1.3:
                    seen.add(who)
                    break
    for who in seen:
        VIS[who].append((t0, t1))
print("VISIBLE", {k: [(round(a, 1), round(b, 1)) for a, b in v] for k, v in VIS.items()})
PRESENT = {k: [(max(a, c), min(b, d)) for a, b in VIS[k] for c, d in PRESENT[k] if max(a, c) < min(b, d)] for k in CH}


def present(who, t):
    return any(a <= t < b for a, b in PRESENT[who])


# ---- heads turn to whoever is talking (else: straight ahead, level), on top of the mocap
sync()
LOOK = {}
for who, ch in CH.items():
    e_ = P.empty(f"Look {who}")
    LOOK[who] = e_
    for bn, inf in (("head", 0.75), ("neck_01", 0.3)):
        c_ = ch.rig.pose.bones[bn].constraints.new("DAMPED_TRACK")
        c_.target, c_.track_axis, c_.influence = e_, "TRACK_Z", inf
SPEAKER_KEY = {k: CAST_KEY.get(w) for k, w, _ in LINES}
DOOR_LOOK = (DOOR_X, SY1, 2.0)
for f in range(1, N + 1, 4):
    t = (f - 1) / FPS
    sc.frame_set(f)
    heads = {w: c.rig.matrix_world @ c.rig.pose.bones["head"].head for w, c in CH.items()}
    spk = [SPEAKER_KEY[k] for k, *_ in LINES if at(k) - 0.2 <= t <= end_of(k) + 0.3 and SPEAKER_KEY.get(k)]
    for who, ch in CH.items():
        h = heads[who]
        fz = ch.rig.rotation_euler.z - math.pi
        fwd = Vector((-math.sin(fz), math.cos(fz), 0))
        tgt = h + fwd * 2.0 + Vector((0, 0, 0.08))
        if T_LOUD <= t < at("lena2") - 0.4 and who in ("me", "mom", "lena", "guard"):
            tgt = Vector(DOOR_LOOK)
        else:
            for sp in spk:
                if sp and sp != who and sp in heads and (heads[sp] - h).length < 6.0 and fwd.dot(heads[sp] - h) > -0.2:
                    tgt = heads[sp] + Vector((0, 0, 0.05))
                    break
        LOOK[who].location = tgt
        LOOK[who].keyframe_insert("location", frame=f)
for e_ in LOOK.values():
    interp(e_, "LINEAR")

TALK_ON = {"rescuer": lambda t: speaking("rescuer", t) and (t > T_BOARD)}   # the loudspeaker lines: no lips
for who, ch in CH.items():
    for f in range(1, N + 1):
        t = (f - 1) / FPS
        talk = TALK_ON[who](t) if who in TALK_ON else speaking(who, t)
        if who == "rescuer" and at("resc3") - 0.3 <= t <= end_of("resc3"):
            talk = True
        st = dict(t=t, seed=ch.seed, worry=worry(who, t), talking=talk, zombie=0.0)
        if who == "lena" and at("lena2") - 0.3 <= t <= end_of("lena2") + 0.6:
            st["smile"] = 0.8
        if who == "oldman" and at("old1") <= t <= end_of("old1"):
            st["smile"] = 0.35
        if who in ("me", "mom", "lena", "guard", "rescuer") and T_BANG <= t <= T_STOP + 1.0:
            st["scream"] = 0.4
        sk = ch.body.data.shape_keys
        for k_, v in anim.face(st).items():
            if k_ in ch.keys:
                ch._put(sk, f'key_blocks["{k_}"].value', 0, f, max(0.0, min(1.0, v)))
        if f == 1 or present(who, t) != present(who, t - 1 / FPS):
            ch.hide(f, not present(who, t))
    ch.flush()
# hand props follow their owner's visibility (hat: the guard)
for f in range(1, N + 1):
    pass

# ================================================================== light, sky, fog (per shot)
sun = bpy.data.objects.new("Sun", bpy.data.lights.new("Sun", "SUN"))
sc.collection.objects.link(sun)
sun.rotation_euler = (math.radians(50), math.radians(10), math.radians(140))
sun.data.angle = math.radians(8)
world = bpy.data.worlds.new("Sky")
sc.world = world
world.use_nodes = True
bg = world.node_tree.nodes["Background"]
DAY, DUSK, NIGHT = (0.6, 0.61, 0.62), (0.36, 0.33, 0.4), (0.035, 0.045, 0.075)


def mix3(a, b, u):
    return tuple(x + (y - x) * u for x, y in zip(a, b))


def sky_at(t):
    if t < T_DUSK0:
        return DAY
    if t < T_DUSK1:
        return mix3(DAY, DUSK, seg(t, T_DUSK0, T_DUSK1))
    return mix3(DUSK, NIGHT, seg(t, T_DUSK1, T_FOREST + 1.0))


def fog_at(t):
    """(near, far, max) of the fog for the shot playing at t."""
    if t < A("resc2") - 0.2:
        return 14.0, 70.0, 0.6
    if t < A("mom2") - 0.1:
        return 4.0, 38.0, 0.95
    if t < A("me2") - 0.2:
        return 14.0, 70.0, 0.6
    if t < T_IN:
        return 5.0, 40.0, 0.95
    if t < T_FOREST:
        return 9.0, 85.0, 0.92
    return 6.0, 38.0, 0.97


sc["fog_near"], sc["fog_far"], sc["fog_max"] = 10.0, 80.0, 0.9
sc["fog_col"] = (0.6, 0.6, 0.6)
cuts = sorted({s_[0] for s_ in SHOTS})
for f in range(1, N + 2, 6):
    t = (f - 1) / FPS
    col = sky_at(t)
    bg.inputs[0].default_value = col + (1,)
    bg.inputs[1].default_value = 1.0
    bg.inputs[0].keyframe_insert("default_value", frame=f)
    sc["fog_col"] = col
    sc.keyframe_insert('["fog_col"]', frame=f)
    day = 1 - seg(t, T_DUSK0, T_FOREST)
    sun.data.energy = 0.25 + 2.6 * day
    sun.data.color = mix3((0.55, 0.65, 1.0), (1.0, 0.96, 0.9), day)
    sun.data.keyframe_insert("energy", frame=f)
    sun.data.keyframe_insert("color", frame=f)
for c in [0.0] + cuts:
    near, far, mx = fog_at(c + 0.01)
    f = fr(c) if c > 0 else 1
    for k_, v in (("fog_near", near), ("fog_far", far), ("fog_max", mx)):
        sc[k_] = v
        sc.keyframe_insert(f'["{k_}"]', frame=f)
interp(sc, "CONSTANT", None)
for fc in fcurves_of(sc):
    if "fog_col" in fc.data_path:
        for k_ in fc.keyframe_points:
            k_.interpolation = "LINEAR"
# headlights at night only, the bus inside lights always, fires and lamps flicker
for lo in HEADL:
    for t, e in ((0, 1500), (T_DUSK1, 1500), (T_FOREST, 5000)):
        lo.data.energy = e
        lo.data.keyframe_insert("energy", frame=fr(t))
for head_, lo, state, ph in LAMPS:
    if state == "flicker":
        for f in range(1, N + 1, 3):
            t = (f - 1) / FPS
            on = (math.sin(t * 7.3 + ph) + math.sin(t * 13.1 + ph * 2)) > -0.4
            lo.data.energy = 1500 if on else 0
            lo.data.keyframe_insert("energy", frame=f)
        interp(lo.data, "CONSTANT")
for o in FIRE_OBJ:
    if o.type == "LIGHT":
        ph = R.random() * 5
        for f in range(1, N + 1, 3):
            t = (f - 1) / FPS
            o.data.energy = 900 * (0.75 + 0.25 * math.sin(t * 9 + ph) * math.sin(t * 5.3 + ph))
            o.data.keyframe_insert("energy", frame=f)
# eyes in the trees: open (blink) from T_EYES
for e_, d_ in EYES:
    pts = [(0, False), (T_EYES + d_, True)]
    t = T_EYES + d_ + 1.5
    while t < T_DOGS:
        pts += [(t, False), (t + 0.15, True)]
        t += 1.7 + d_
    pts.append((T_DOGS + 0.5, False))
    key_vis(e_, pts)

# ---- speed: shadows only from the sun, the shelter, the bus and its headlights; lamps reach 30 m
KEEP_SHADOW = ("Sun", "Shelter warm", "Bus headlight", "Bus warm")
for o in bpy.data.objects:
    if o.type == "LIGHT":
        o.data.use_shadow = o.name.startswith(KEEP_SHADOW) and not o.name.startswith("Shelter warm.002")
        if o.data.type in ("POINT", "SPOT") and not o.name.startswith(("Far lights", "Bus headlight")):
            o.data.use_custom_distance = True
            o.data.cutoff_distance = 30.0
LIGHTS_CITY = [lo for _, lo, _, _ in LAMPS] + [o for o in FIRE_OBJ if o.type == "LIGHT"]


def sect_vis(objs, spans):
    for o in objs:
        pts = [(0, False)]
        for a, b in spans:
            pts += [(a, True), (b, False)]
        for t, v in pts:
            o.hide_render = not v
            o.keyframe_insert("hide_render", frame=max(1, fr(t)) if t > 0 else 1)
        interp(o, "CONSTANT", "hide_render")


OUT_SPANS = [(A("resc2") - 0.2, A("mom2") - 0.1), (T_DOOR - 0.3, T_FOREST + 3.0)]
sect_vis([o for o in SEC_CITY if not o.animation_data and not o.name.startswith("Road")] + LIGHTS_CITY, OUT_SPANS)
sect_vis([o for o in SEC_SHELTER if not o.animation_data] + SH_LIGHTS, [(0, T_IN)])
sect_vis([o for o in SEC_FOREST if not o.animation_data], [(A("radio1") - 3.0, END + 1)])

# ================================================================== look
sc.frame_set(1)
for m in list(bpy.data.materials):            # glowing materials: plain emission (the cel pass leaves them alone)
    if not m.use_nodes:
        continue
    pb = m.node_tree.nodes.get("Principled BSDF")
    if pb is None or pb.inputs["Emission Strength"].default_value <= 0:
        continue
    col = tuple(pb.inputs["Emission Color"].default_value)
    stren = pb.inputs["Emission Strength"].default_value
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs[0].default_value = col
    em.inputs[1].default_value = min(stren, 8.0) / 2.0 + 1.0
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    nt.links.new(em.outputs[0], out.inputs[0])
T.toonify(sc, samples=int(os.environ.get("SAMPLES", "4")))
LK.after()
for m in TOWER_MATS:          # the cel pass flattens textures: put the window grid back (a few windows lit)
    nt = m.node_tree
    mul = next((n for n in nt.nodes if n.type == "MIX" and n.blend_type == "MULTIPLY"), None)
    if mul is None:
        continue
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs["Object"], sep.inputs[0])
    ad_ = nt.nodes.new("ShaderNodeMath")
    ad_.operation = "ADD"
    nt.links.new(sep.outputs[0], ad_.inputs[0])
    nt.links.new(sep.outputs[1], ad_.inputs[1])
    cb = nt.nodes.new("ShaderNodeCombineXYZ")
    nt.links.new(ad_.outputs[0], cb.inputs[0])
    nt.links.new(sep.outputs[2], cb.inputs[1])
    br = nt.nodes.new("ShaderNodeTexBrick")
    br.offset = 0.0
    br.inputs["Scale"].default_value = 1.0
    br.inputs["Brick Width"].default_value = 1.6
    br.inputs["Row Height"].default_value = 3.0
    br.inputs["Mortar Size"].default_value = 0.5
    br.inputs["Bias"].default_value = -0.85
    br.inputs["Color1"].default_value = (0.05, 0.055, 0.065, 1)
    br.inputs["Color2"].default_value = (1.0, 0.7, 0.32, 1)
    wall_ = tuple(m["tower_wall"])
    br.inputs["Mortar"].default_value = tuple(c * 1.25 for c in wall_) + (1,)
    nt.links.new(cb.outputs[0], br.inputs["Vector"])
    nt.links.new(br.outputs["Color"], mul.inputs[6])
for o in bpy.data.objects:
    for md in o.modifiers:
        if md.type == "SUBSURF":
            md.render_levels = 0
# fog: every emission colour is mixed towards the sky colour by distance from the camera


def fogify(m, keep=0.0):
    nt = m.node_tree
    for em in [n for n in nt.nodes if n.type == "EMISSION"]:
        src = em.inputs[0].links[0].from_socket if em.inputs[0].is_linked else None
        cam_ = nt.nodes.new("ShaderNodeCameraData")
        mr = nt.nodes.new("ShaderNodeMapRange")
        a_n = nt.nodes.new("ShaderNodeAttribute")
        a_n.attribute_type, a_n.attribute_name = "VIEW_LAYER", "fog_near"
        a_f = nt.nodes.new("ShaderNodeAttribute")
        a_f.attribute_type, a_f.attribute_name = "VIEW_LAYER", "fog_far"
        a_m = nt.nodes.new("ShaderNodeAttribute")
        a_m.attribute_type, a_m.attribute_name = "VIEW_LAYER", "fog_max"
        a_c = nt.nodes.new("ShaderNodeAttribute")
        a_c.attribute_type, a_c.attribute_name = "VIEW_LAYER", "fog_col"
        nt.links.new(cam_.outputs["View Distance"], mr.inputs["Value"])
        nt.links.new(a_n.outputs["Fac"], mr.inputs["From Min"])
        nt.links.new(a_f.outputs["Fac"], mr.inputs["From Max"])
        mul = nt.nodes.new("ShaderNodeMath")
        mul.operation = "MULTIPLY"
        nt.links.new(mr.outputs["Result"], mul.inputs[0])
        nt.links.new(a_m.outputs["Fac"], mul.inputs[1])
        if keep:
            k2 = nt.nodes.new("ShaderNodeMath")
            k2.operation = "MULTIPLY"
            k2.inputs[1].default_value = 1 - keep
            nt.links.new(mul.outputs[0], k2.inputs[0])
            mul = k2
        mx = nt.nodes.new("ShaderNodeMix")
        mx.data_type = "RGBA"
        nt.links.new(mul.outputs[0], mx.inputs[0])
        if src is not None:
            nt.links.new(src, mx.inputs[6])
        else:
            mx.inputs[6].default_value = tuple(em.inputs[0].default_value)
        nt.links.new(a_c.outputs["Color"], mx.inputs[7])
        nt.links.new(mx.outputs[2], em.inputs[0])


for m in bpy.data.materials:
    if m.use_nodes:
        glow = any(n.type == "EMISSION" and n.inputs[1].default_value > 1.5 for n in m.node_tree.nodes)
        fogify(m, keep=0.6 if glow else 0.0)
# ink outlines: thin on people and props, thicker on buildings and the bus
ink = T._ink_mat()
SKIP = ("high-poly", "lash", "brow", "teeth", "tongue", "road line", "rug", "fire", "light", "glow", "eyes in",
        "headlight", "far ", "soot", "rust", "drawing", "stripe", "skirt", "led", "bulb", "wire", "inner wall", "lantern",
        "status", "lug", "spike", "tooth", "lit window", "destination", "rope")
for o in bpy.data.objects:
    if o.type != "MESH" or any(k in o.name.lower() for k in SKIP) or o.name.startswith(("Pine", "Trunk")):
        continue
    big = max(o.dimensions) if o.dimensions else 1
    th = 0.005 if any(o.name.startswith(c.name) for c in CH.values()) else (0.035 if big > 6 else 0.012)
    if ink.name not in [mm.name for mm in o.data.materials if mm]:
        o.data.materials.append(ink)
    sd = o.modifiers.new("Outline", "SOLIDIFY")
    sd.thickness = th / max(1e-6, o.matrix_world.to_scale().x)
    sd.offset = 1.0
    sd.use_flip_normals = True
    sd.use_rim = False
    sd.material_offset = len(o.data.materials) - 1
fogify(ink)
sc.render.resolution_x, sc.render.resolution_y = 960, 540
sc.render.dither_intensity = 0.0
for attr, v in (("use_raytracing", False), ("shadow_ray_count", 1), ("shadow_step_count", 2),
                ("light_threshold", 0.05), ("use_gtao", False), ("use_volumetric_shadows", False)):
    if hasattr(sc.eevee, attr):
        setattr(sc.eevee, attr, v)
sc.render.film_transparent = False
import json  # noqa: E402
os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
json.dump({"cuts": [s_[0] for s_ in SHOTS], "T_BANG": T_BANG, "T_LOUD": T_LOUD, "T_GO": T_GO, "T_DOOR": T_DOOR,
           "T_DOGS": T_DOGS, "T_STOP": T_STOP, "T_ARRIVE": [T_ARRIVE0, T_ARRIVE1], "T_FOREST": T_FOREST,
           "T_LIGHTS": T_LIGHTS, "T_IN": T_IN, "T_OUT": T_OUT},
          open(os.path.join(HERE, "out", "events.json"), "w"), indent=1)

args = sys.argv
if "--still" in args:
    os.makedirs(os.path.join(HERE, "test"), exist_ok=True)
    spec = args[args.index("--still") + 1]
    frames = [fr(float(v[1:])) if v.startswith("t") else int(v) for v in spec.split(",")]
    for f in frames:
        sc.frame_set(f)
        sc.render.filepath = os.path.join(HERE, "test", f"s_{f:04d}.png")
        bpy.ops.render.render(write_still=True)
if "--save" in args:
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(HERE, "shelter3.blend"))
