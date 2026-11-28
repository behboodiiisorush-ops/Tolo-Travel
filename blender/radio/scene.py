"""«زنگ آخر ۵ — صدای رادیو» — the armoured car runs out of fuel; the radio calls with Mom's voice; the kids sneak
to the old house and find only a tape recorder... and Mom's shoes. Comic look (EEVEE cel shading + ink outlines)
on the realistic cast, bodies driven by Mixamo motion capture (blender/mocap).

    ../cast/bpy.sh scene.py --still 40,120,...      -> test/s_XXXX.png
    ../cast/bpy.sh scene.py --save                  -> radio.blend (render.py renders from it)
Shots (seconds):
  1  0.0- 5.5  inside the car: stopped, dark; me (voice-over)
  2  5.5- 8.5  the radio blinks: Mom's voice;   2b 8.5-11.0 Kian lifts his head
  3 11.0-14.0  Kian stands up: "it's Mom!"
  4 14.0-20.0  Kazemi turns in the driver's seat: "it's a trap"
  5 20.0-25.0  later: Kazemi asleep, the kids sneak out of the back door
  6 25.0-33.0  the dark road, the house with a lit window far ahead
  7 33.0-38.0  me opens the front door
  8 38.0-39.6  inside;  8b 39.6-42.4 the tape recorder speaks;  8c 42.4-45.0 faces
  9 45.0-49.0  "it's only a tape recorder"
 10 49.0-54.0  Mahsa points: Mom's shoes
 11 54.0-59.0  Kian kneels by the shoes: "still warm"
 12 59.0-64.5  the back door creaks open on darkness
"""
import bpy, sys, os, math
from mathutils import Vector, Matrix
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "studio"))
sys.path.insert(0, os.path.join(HERE, "..", "cast"))
sys.path.insert(0, HERE)
bpy.ops.wm.read_factory_settings(use_empty=True)
import cast, mocap, anim, lipsync  # noqa: E402
import props as P         # noqa: E402
import toon_look as T     # noqa: E402
from captions import LINES, END, FILES, VOICEOVER  # noqa: E402

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


def mats():
    """(Re)create the set materials (building the cast purges unused datablocks)."""
    return dict(
        olive=P.mat("APC wall", (0.27, 0.31, 0.22), 0.6, metal=0.3), steel=P.mat("Steel", (0.32, 0.34, 0.36), 0.4, metal=0.6),
        bench=P.mat("Bench", (0.2, 0.22, 0.2), 0.8), seat=P.mat("Seat", (0.15, 0.12, 0.1), 0.7),
        dash=P.mat("Dash", (0.1, 0.1, 0.11), 0.6), slit=P.mat("Slit glass", (0.05, 0.08, 0.14), 0.1),
        night=P.mat("Night", (0.02, 0.03, 0.06), 1.0),
        ground=P.mat("Ground", (0.16, 0.18, 0.14), 1.0), road=P.mat("Road", (0.1, 0.1, 0.11), 0.9),
        line=P.mat("Road line", (0.75, 0.72, 0.6), 0.8), tree=P.mat("Tree", (0.06, 0.1, 0.07), 1.0),
        trunk=P.mat("Trunk", (0.12, 0.09, 0.07), 1.0),
        hwall=P.mat("House wall", (0.62, 0.55, 0.45), 0.9), roof=P.mat("Roof", (0.3, 0.16, 0.13), 0.9),
        iwall=P.mat("Room wall", (0.78, 0.7, 0.56), 0.9), floor=P.mat("Room floor", (0.45, 0.3, 0.19), 0.7),
        ceil=P.mat("Room ceiling", (0.7, 0.68, 0.62), 0.9), door=P.mat("Door", (0.42, 0.26, 0.15), 0.6),
        frame=P.mat("Door frame", (0.85, 0.82, 0.74), 0.5), wood=P.mat("Wood", (0.36, 0.23, 0.13), 0.6),
        sofa=P.mat("Sofa", (0.3, 0.38, 0.3), 0.9), rug=P.mat("Rug", (0.5, 0.18, 0.16), 1.0),
        plastic=P.mat("Recorder", (0.12, 0.12, 0.13), 0.4), silver=P.mat("Silver", (0.7, 0.7, 0.72), 0.3, metal=0.8),
        cassette=P.mat("Cassette", (0.85, 0.83, 0.75), 0.5), shoe=P.mat("Shoe", (0.45, 0.08, 0.12), 0.4),
        sole=P.mat("Sole", (0.08, 0.06, 0.05), 0.6), shade=P.mat("Lamp shade", (0.95, 0.85, 0.6), 0.8),
        red=P.mat("LED red", (1.0, 0.05, 0.03), 0.3, emit=(1.0, 0.05, 0.03), strength=12.0),
        green=P.mat("LED green", (0.1, 1.0, 0.2), 0.3, emit=(0.1, 1.0, 0.2), strength=10.0),
        warm=P.mat("Window light", (1.0, 0.75, 0.4), 0.5, emit=(1.0, 0.72, 0.38), strength=6.0),
        dark=P.mat("Dark", (0.01, 0.01, 0.012), 1.0),
    )


M_ = mats()


def box(loc, size, m, name="Set"):
    return P.box(loc, size, M_[m] if isinstance(m, str) else m, name)


def hinge_door(name, hinge, width, height, m, keys, sign=1):
    """Door leaf from the hinge along -X (sign=1) or +X (sign=-1); keys [(t, deg)] around Z."""
    h = P.empty(name + " hinge", hinge)
    leaf = box((hinge[0] - sign * width / 2, hinge[1], hinge[2] + height / 2), (width, 0.05, height), m, name)
    knob = P.sphere((hinge[0] - sign * (width - 0.08), hinge[1] - 0.05, hinge[2] + 1.0), 0.03, M_["silver"], name + " knob")
    knob2 = P.sphere((hinge[0] - sign * (width - 0.08), hinge[1] + 0.05, hinge[2] + 1.0), 0.03, M_["silver"], name + " knob")
    for o in (leaf, knob, knob2):
        o.parent = h
        o.matrix_parent_inverse = h.matrix_world.inverted()
    for t, a in keys:
        h.rotation_euler = (0, 0, math.radians(a))
        h.keyframe_insert("rotation_euler", index=2, frame=fr(t))
    return h


# ------------------------------------------------------------------ set A: inside the armoured car (origin)
CW, CL, CH_ = 2.4, 5.2, 1.95
box((0, CL / 2, -0.05), (CW, CL, 0.1), "steel", "APC floor")
box((0, CL / 2, CH_ + 0.05), (CW, CL, 0.1), "olive", "APC roof")
for s in (-1, 1):
    box((s * (CW / 2 + 0.05), CL / 2, CH_ / 2), (0.1, CL, CH_), "olive", "APC side")
    box((s * 0.95, 2.0, 0.22), (0.45, 2.9, 0.44), "bench", "Bench")
    box((s * 0.95, 2.0, 0.46), (0.47, 2.92, 0.05), "seat", "Bench top")
    for y in (0.9, 1.9, 2.9):                                   # grab straps / rivets on the walls
        P.sphere((s * 1.14, y, 1.5), 0.03, M_["steel"], "APC rivet")
box((0, CL + 0.05, CH_ / 2), (CW, 0.1, CH_), "olive", "APC front")
box((0, CL - 0.02, 1.45), (1.9, 0.04, 0.22), "slit", "APC slit")
# back wall with the rear door (x -0.45..0.45)
box((-0.85, -0.05, CH_ / 2), (0.7, 0.1, CH_), "olive", "APC back")
box((0.85, -0.05, CH_ / 2), (0.7, 0.1, CH_), "olive", "APC back")
box((0, -0.05, 1.85), (1.0, 0.1, 0.2), "olive", "APC back")
box((0, -2.5, 1.0), (6, 0.1, 4), "night", "Outside dark")
hinge_door("APC rear door", (0.45, -0.03, 0.0), 0.9, 1.75, "olive", [(0, 0), (19.0, 0), (20.0, 95), (END, 95)])
# driver: seat, dash, wheel, the radio with its LED
box((0.45, 4.35, 0.22), (0.5, 0.5, 0.44), "seat", "Driver seat")
box((0.45, 4.1, 0.75), (0.5, 0.08, 0.6), "seat", "Driver back")
box((0, 5.0, 0.85), (CW - 0.1, 0.35, 0.25), "dash", "Dash")
wheel = P.cyl((0.45, 4.78, 1.0), (0.45, 4.74, 1.06), 0.19, M_["dash"], "Wheel", verts=24)
P.cyl((0.45, 4.95, 0.95), (0.45, 4.78, 1.03), 0.025, M_["dash"], "Wheel column")
RADIO = Vector((-0.2, 4.86, 1.05))
box(tuple(RADIO), (0.32, 0.12, 0.14), "plastic", "Radio")
box(tuple(RADIO + Vector((0.04, -0.062, 0.01))), (0.16, 0.01, 0.06), "slit", "Radio dial")
led_r = P.sphere(tuple(RADIO + Vector((-0.11, -0.065, 0.03))), 0.012, M_["green"], "Radio LED")
blinks = [(0, False)]
t_ = 6.2
while t_ < 9.8:
    blinks += [(t_, True), (t_ + 0.25, False)]
    t_ += 0.5
key_vis(led_r, blinks)
cab_lamp = P.area_light((0, 2.4, 1.9), (0, 2.4, 0), 18, 0.8, (1.0, 0.6, 0.3), name="Cabin lamp")
dash_glow = P.area_light(tuple(RADIO + Vector((0, -0.4, 0.1))), tuple(RADIO), 2.5, 0.3, (0.3, 1.0, 0.4), name="Radio glow")
key_vis(dash_glow, [(0, False), (6.0, True), (10.0, False)])

# ------------------------------------------------------------------ set B: the road and the house (x = 100)
X0 = 100.0
box((X0, 20, -0.06), (80, 90, 0.1), "ground", "Ground")
box((X0, 20, -0.005), (3.6, 90, 0.01), "road", "Road")
for y in range(-20, 60, 4):
    box((X0, y, 0.002), (0.12, 1.8, 0.01), "line", "Road line")
box((X0 + 0.2, -1.5, 1.0), (2.5, 5.5, 2.0), "olive", "APC outside")
import random
rr = random.Random(5)
for k in range(26):
    side = -1 if k % 2 else 1
    x = X0 + side * rr.uniform(4.0, 14.0)
    y = rr.uniform(-5, 55)
    if abs(x - X0) < 6.5 and 26 < y < 38:
        continue
    h = rr.uniform(3.0, 6.0)
    P.cyl((x, y, 0), (x, y, h * 0.35), 0.12, M_["trunk"], "Trunk")
    tr = P.sphere((x, y, h * 0.62), h * 0.3, M_["tree"], "Tree", scale=(1, 1, 1.4))
# the house: room x 97.5..102.5, y 30..35, door in the front wall at x 99.55..100.45
HX0, HX1, HY0, HY1, HH = 97.5, 102.5, 30.0, 35.0, 2.6
box(((HX0 + HX1) / 2, (HY0 + HY1) / 2, -0.04), (HX1 - HX0, HY1 - HY0, 0.08), "floor", "Room floor")
box(((HX0 + HX1) / 2, (HY0 + HY1) / 2, HH + 0.05), (HX1 - HX0 + 0.3, HY1 - HY0 + 0.3, 0.1), "ceil", "Room ceiling")
for s in (-1, 1):                                                # gable roof
    r = box(((HX0 + HX1) / 2 + s * 1.35, (HY0 + HY1) / 2, HH + 0.75), (3.2, HY1 - HY0 + 0.6, 0.12), "roof", "Roof")
    r.rotation_euler = (0, math.radians(-s * 30), 0)
for x, m in ((HX0 - 0.08, "Left"), (HX1 + 0.08, "Right")):
    box((x, (HY0 + HY1) / 2, HH / 2), (0.16, HY1 - HY0 + 0.16, HH), "hwall", "House " + m)
    box((x + (0.09 if x < X0 else -0.09), (HY0 + HY1) / 2, HH / 2), (0.01, HY1 - HY0, HH), "iwall", "Room wall")
# front wall: window x 98.2..99.2 (z 1.0..1.9), door x 99.55..100.45 (z 0..2.1)
FW = HY0 - 0.08
for x0, x1, z0, z1 in ((HX0 - 0.16, 98.2, 0, HH), (98.2, 99.2, 0, 1.0), (98.2, 99.2, 1.9, HH), (99.2, 99.55, 0, HH),
                       (99.55, 100.45, 2.1, HH), (100.45, HX1 + 0.16, 0, HH)):
    box(((x0 + x1) / 2, FW, (z0 + z1) / 2), (x1 - x0, 0.16, z1 - z0), "hwall", "House front")
    box(((x0 + x1) / 2, HY0 + 0.005, (z0 + z1) / 2), (x1 - x0, 0.01, z1 - z0), "iwall", "Room wall")
box((98.7, FW, 1.45), (1.0, 0.02, 0.9), "warm", "Window light")
for s in (99.51, 100.49):
    box((s, FW - 0.02, 1.05), (0.07, 0.2, 2.1), "frame", "Door frame")
box((X0, FW - 0.02, 2.14), (1.0, 0.2, 0.07), "frame", "Door frame")
front_door = hinge_door("Front door", (100.45, FW - 0.1, 0.0), 0.9, 2.08, "door", [(0, 0), (34.6, 0), (35.9, 100), (END, 100)])
# back wall with the back door (x 98.55..99.45); darkness behind it
BW = HY1 + 0.08
for x0, x1, z0, z1 in ((HX0 - 0.16, 98.55, 0, HH), (98.55, 99.45, 2.1, HH), (99.45, HX1 + 0.16, 0, HH)):
    box(((x0 + x1) / 2, BW, (z0 + z1) / 2), (x1 - x0, 0.16, z1 - z0), "hwall", "House back")
    box(((x0 + x1) / 2, HY1 - 0.005, (z0 + z1) / 2), (x1 - x0, 0.01, z1 - z0), "iwall", "Room wall")
for s in (98.51, 99.49):
    box((s, HY1 - 0.02, 1.05), (0.07, 0.12, 2.1), "frame", "Door frame")
box((99.0, BW + 0.9, 1.2), (1.6, 1.6, 2.6), "dark", "Back darkness")
back_door = hinge_door("Back door", (98.55, HY1 - 0.06, 0.0), 0.9, 2.08, "door",
                       [(0, 0), (59.6, 0), (60.4, -8), (61.0, -10), (62.4, -48), (END, -55)], sign=-1)
# furniture: sofa, rug, small table with the tape recorder, Mom's shoes, floor lamp
box((97.95, 32.6, 0.25), (0.8, 2.0, 0.5), "sofa", "Sofa")
box((97.7, 32.6, 0.65), (0.25, 2.0, 0.8), "sofa", "Sofa back")
box((100.0, 32.4, 0.005), (2.4, 1.8, 0.01), "rug", "Rug")
TABLE = Vector((100.6, 33.25, 0.0))
box(tuple(TABLE + Vector((0, 0, 0.5))), (0.7, 0.5, 0.05), "wood", "Small table")
for dx in (-0.3, 0.3):
    for dy in (-0.2, 0.2):
        box(tuple(TABLE + Vector((dx, dy, 0.25))), (0.04, 0.04, 0.5), "wood", "Table leg")
REC = TABLE + Vector((0, 0, 0.62))
box(tuple(REC), (0.36, 0.12, 0.2), "plastic", "Recorder")
box(tuple(REC + Vector((0.07, -0.062, 0.02))), (0.14, 0.01, 0.08), "cassette", "Cassette")
for dx in (0.035, 0.105):
    P.cyl(tuple(REC + Vector((dx, -0.07, 0.02))), tuple(REC + Vector((dx, -0.064, 0.02))), 0.018, M_["plastic"], "Reel")
P.cyl(tuple(REC + Vector((-0.09, -0.07, 0.0))), tuple(REC + Vector((-0.09, -0.06, 0.0))), 0.055, M_["silver"], "Speaker")
P.cyl(tuple(REC + Vector((0.12, 0, 0.1))), tuple(REC + Vector((0.12, 0, 0.32))), 0.006, M_["silver"], "Antenna")
rec_led = P.sphere(tuple(REC + Vector((-0.15, -0.065, 0.07))), 0.01, M_["red"], "Recorder LED")
key_vis(rec_led, [(0, True)])
SHOES = Vector((100.2, 32.95, 0.0))
for dx, ang in ((-0.08, 8), (0.09, -12)):
    s_ = box(tuple(SHOES + Vector((dx, 0, 0.035))), (0.085, 0.24, 0.07), "shoe", "Mom shoe")
    s_.rotation_euler = (0, 0, math.radians(ang))
    h_ = box(tuple(SHOES + Vector((dx, 0.1, 0.012))), (0.09, 0.25, 0.024), "sole", "Mom shoe sole")
    h_.rotation_euler = (0, 0, math.radians(ang))
P.cyl((102.0, 34.5, 0), (102.0, 34.5, 1.5), 0.02, M_["silver"], "Lamp pole")
P.cyl((102.0, 34.5, 1.45), (102.0, 34.5, 1.75), 0.2, M_["shade"], "Lamp shade")
room_lamp = P.area_light((100.0, 32.5, 2.5), (100.0, 32.5, 0), 70, 2.0, (1.0, 0.78, 0.5), name="Room lamp")
lamp_glow = P.area_light((102.0, 34.4, 1.6), (101.0, 33.0, 0.8), 25, 0.4, (1.0, 0.7, 0.4), name="Floor lamp glow")
win_glow = P.area_light((98.7, FW - 0.4, 1.5), (98.7, FW - 3.0, 0.5), 40, 1.0, (1.0, 0.72, 0.4), name="Window glow")
porch = P.area_light((X0, FW - 1.4, 2.4), (X0, FW - 1.0, 0), 25, 1.2, (1.0, 0.72, 0.45), name="Door spill")
key_vis(porch, [(0, False), (35.0, True)])
# lights flicker when the back door opens
for k, t in enumerate([0, 59.6, 59.75, 59.9, 60.2, 60.35, 61.6, 61.75]):
    room_lamp.data.energy = 70 if k % 2 == 0 else 20
    room_lamp.data.keyframe_insert("energy", frame=fr(t))

sun = bpy.data.objects.new("Moon", bpy.data.lights.new("Moon", "SUN"))
sc.collection.objects.link(sun)
sun.data.energy = 1.6
sun.data.color = (0.7, 0.78, 1.0)
sun.data.use_shadow = False
sun.rotation_euler = (math.radians(55), 0, math.radians(-30))
w = bpy.data.worlds.new("Night")
sc.world = w
w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.012, 0.018, 0.04, 1)
w.node_tree.nodes["Background"].inputs[1].default_value = 1.0

# ------------------------------------------------------------------ cast
KEYS = ["me", "arian", "mahsa", "kian", "kazemi"]
CH = {}
for k in KEYS:
    CH[k] = cast.spawn(k)
    T.register(CH[k], k, realistic=True)
M_ = mats()
CLIP = {}


def clip(name):
    if name not in CLIP:
        CLIP[name] = mocap.load(os.path.join(MOC, name + ".fbx"))
    return CLIP[name]


def hold(who, t1, pos, facing):
    rig = CH[who].rig
    rig.location = pos
    rig.rotation_euler = (0, 0, math.radians(facing) + math.pi)
    rig.keyframe_insert("location", frame=fr(t1) - 1)
    rig.keyframe_insert("rotation_euler", index=2, frame=fr(t1) - 1)


def act(who, name, t0, t1, pos, facing, **kw):
    """Character `who` plays clip `name` from t0 to t1 (seconds) at pos/facing."""
    n = fr(t1) - fr(t0)
    mocap.apply(CH[who], clip(name), start=fr(t0), length=n, offset=pos, facing=facing, **kw)
    hold(who, t1, pos, facing)


def walk(who, name, t0, t1, p0, p1, facing, speed=1.0):
    """In-place cycle `name` while the body moves in a straight line p0 -> p1."""
    n = fr(t1) - fr(t0)
    a, b = Vector(p0), Vector(p1)
    mocap.apply(CH[who], clip(name), start=fr(t0), length=n, facing=facing, in_place=True, loop=True, speed=speed,
                place=lambda j: (tuple(a.lerp(b, j / max(1, n - 1))), facing))
    hold(who, t1, tuple(b), facing)


L, R = -90, 90       # facing: +X is -90, -X is +90
PRESENT = {"me": [(0, END)], "arian": [(0, END)], "mahsa": [(0, END)], "kian": [(0, END)], "kazemi": [(0, 25.0)]}
# ---- shots 1-4: seated in the car
act("me", "sitting_idle", 0.0, 20.0, (-0.72, 2.9, 0), L, loop=True)
act("arian", "sitting_idle", 0.0, 20.0, (-0.72, 1.7, 0), L, loop=True, src_from=1.5)
act("mahsa", "sitting_idle", 0.0, 20.0, (0.72, 1.7, 0), R, loop=True, src_from=2.5)
act("kian", "sitting_idle", 0.0, 11.0, (0.72, 2.9, 0), R, loop=True, src_from=0.7, speed=0.6)
act("kian", "sit_to_stand", 11.0, 13.4, (0.72, 2.9, 0), R)
act("kian", "breathing_idle", 13.4, 20.0, (0.6, 2.95, 0), 60)
act("kazemi", "driving", 0.0, 5.5, (0.45, 4.42, 0), 0, speed=0.5)
act("kazemi", "sitting_idle", 5.5, 14.0, (0.45, 4.42, 0), 0, loop=True)
act("kazemi", "sitting_talking", 14.0, 20.0, (0.45, 4.42, 0), 150, src_from=4.0)
act("kazemi", "sitting_idle", 20.0, 25.0, (0.45, 4.42, 0), 0, loop=True, speed=0.15)
# ---- shot 5: the kids sneak to the open rear door (towards -Y)
walk("mahsa", "sneak_walk", 20.0, 25.0, (0.0, 1.2, 0), (0.0, -0.1, 0), 180, speed=0.8)
walk("me", "sneak_walk", 20.0, 25.0, (0.15, 2.2, 0), (0.1, 0.8, 0), 180, speed=0.8)
walk("kian", "sneak_walk", 20.0, 25.0, (-0.2, 2.9, 0), (-0.1, 1.6, 0), 180, speed=0.8)
walk("arian", "sneak_walk", 20.0, 25.0, (0.2, 3.5, 0), (0.1, 2.4, 0), 180, speed=0.8)
# ---- shot 6: walking the road towards the house (+Y)
walk("me", "walking", 25.0, 33.0, (X0, 6.0, 0), (X0, 17.0, 0), 0)
walk("mahsa", "walking_3", 25.0, 33.0, (X0 + 0.75, 5.4, 0), (X0 + 0.75, 16.4, 0), 0)
walk("kian", "walking", 25.0, 33.0, (X0 - 0.7, 5.6, 0), (X0 - 0.7, 16.6, 0), 0)
walk("arian", "walking_3", 25.0, 33.0, (X0 + 1.35, 4.8, 0), (X0 + 1.35, 15.8, 0), 0)
# ---- shot 7: the front door
act("me", "opening_door_inwards", 33.0, 38.0, (X0 + 0.05, FW - 0.95, 0), 0)
act("arian", "looking_around", 33.0, 38.0, (X0 - 0.75, FW - 1.9, 0), 0)
act("mahsa", "breathing_idle", 33.0, 38.0, (X0 + 0.85, FW - 1.75, 0), -10)
act("kian", "nervously_look_around", 33.0, 38.0, (X0 + 0.1, FW - 2.5, 0), 0)
# ---- shot 8: inside, the tape recorder plays
act("me", "looking_around", 38.0, 45.0, (99.95, 31.5, 0), 20)
act("arian", "nervously_look_around", 38.0, 59.0, (99.15, 31.1, 0), 10, loop=True)
act("mahsa", "breathing_idle", 38.0, 49.0, (100.75, 31.35, 0), 15)
act("kian", "looking_around", 38.0, 45.0, (100.2, 30.75, 0), 0, src_from=1.5)
# ---- shot 9: "it's only a tape recorder"
act("me", "thinking", 45.0, 49.0, (100.25, 32.45, 0), -20)
act("kian", "breathing_idle", 45.0, 54.0, (100.2, 31.6, 0), 0, src_from=2.0)
# ---- shot 10: Mahsa points at the shoes (the arm points to her left)
_d = SHOES - Vector((100.95, 32.15, 0))
_aim = math.degrees(math.atan2(-_d.x, _d.y))
act("mahsa", "pointing", 49.0, 54.0, (100.95, 32.15, 0), _aim - 90)
act("me", "breathing_idle", 49.0, 59.0, (99.7, 32.3, 0), 40)
# ---- shot 11: Kian kneels by the shoes
act("kian", "kneeling_idle", 54.0, 59.0, (100.2, 32.45, 0), 0, loop=True)
act("mahsa", "breathing_idle", 54.0, 59.0, (100.95, 32.15, 0), 20)
# ---- shot 12: the back door opens on darkness; everyone turns to it
for who, pos, clipn in (("me", (99.9, 32.2, 0), "terrified"), ("arian", (99.3, 31.6, 0), "nervously_look_around"),
                        ("mahsa", (100.75, 32.0, 0), "terrified"), ("kian", (100.25, 32.55, 0), "kneeling_idle")):
    d = Vector((98.95, 35.0, 0)) - Vector(pos)
    act(who, clipn, 59.0, END, pos, math.degrees(math.atan2(-d.x, d.y)), loop=True,
        src_from=1.0 if clipn == "terrified" else 0.0)

# ---- faces: lips follow the real voices, worry, visibility
LS = lipsync.Voices(fps=FPS)
for i, ((a, b, who, _), fn) in enumerate(zip(LINES, FILES)):
    if who in CH and i not in VOICEOVER:
        LS.add(who, os.path.join(HERE, "voices", fn + ".mp3"), a)
WORRY = {"me": [(0, 0.6), (6, 1.2), (20, 1.4), (38, 1.5), (49, 1.8), (59.5, 2.0)],
         "arian": [(0, 0.8), (20, 1.5), (38, 1.7), (59.5, 2.0)],
         "mahsa": [(0, 0.8), (6, 1.3), (20, 1.5), (49, 1.8), (59.5, 2.0)],
         "kian": [(0, 1.0), (6, 0.4), (14, 1.2), (38, 1.0), (54, 1.9), (59.5, 2.0)],
         "kazemi": [(0, 0.8), (14, 1.2)]}


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
        st = dict(t=t, seed=ch.seed, worry=worry(who, t), talking=LS.level(who, t), zombie=0.0)
        if who == "kazemi" and 20.0 <= t < 25.0:
            st["worry"] = 0.0
        sk = ch.body.data.shape_keys
        for k, v in anim.face(st).items():
            if k in ch.keys:
                ch._put(sk, f'key_blocks["{k}"].value', 0, f, max(0.0, min(1.0, v)))
        if f == 1 or present(who, t) != present(who, t - 1 / FPS):
            ch.hide(f, not present(who, t))
    ch.flush()

# ------------------------------------------------------------------ camera: shots (t0, t1, cam0, cam1, aim0, aim1, lens)
KH = Vector((0.72, 2.9, 1.05))
SHOTS = [
    (0.0, 5.5, (0.0, 0.3, 1.45), (0.0, 0.75, 1.42), (0.0, 4.5, 0.9), (0.0, 4.5, 0.92), 16),
    (5.5, 8.5, (0.08, 4.25, 1.22), (0.02, 4.4, 1.18), tuple(RADIO), tuple(RADIO), 30),
    (8.5, 11.0, (-0.1, 2.75, 1.05), (-0.05, 2.8, 1.05), tuple(KH), tuple(KH), 28),
    (11.0, 14.0, (-0.65, 1.2, 1.2), (-0.6, 1.35, 1.25), (0.7, 2.9, 1.05), (0.65, 2.95, 1.35), 20),
    (14.0, 20.0, (-0.25, 2.5, 1.35), (-0.2, 2.75, 1.33), (0.45, 4.45, 1.0), (0.45, 4.45, 1.0), 24),
    (20.0, 25.0, (0.95, 4.0, 1.62), (0.95, 3.9, 1.62), (0.0, 0.8, 0.7), (0.0, 0.3, 0.7), 17),
    (25.0, 33.0, (X0 + 1.6, 2.6, 1.25), (X0 + 1.4, 10.8, 1.3), (X0 + 0.2, 32.0, 1.4), (X0 + 0.1, 32.0, 1.4), 24),
    (33.0, 38.0, (X0 - 1.5, FW - 2.7, 1.45), (X0 - 1.3, FW - 2.4, 1.45), (X0 + 0.1, FW, 1.2), (X0 + 0.1, FW + 0.6, 1.2), 22),
    (38.0, 39.6, (102.1, 34.4, 1.75), (102.0, 34.3, 1.72), (100.0, 31.3, 0.95), (100.0, 31.3, 0.95), 18),
    (39.6, 42.4, (100.95, 32.72, 0.92), (100.9, 32.8, 0.9), tuple(REC), tuple(REC), 30),
    (42.4, 45.0, (100.45, 33.7, 1.4), (100.4, 33.6, 1.38), (100.0, 31.2, 1.25), (100.0, 31.2, 1.25), 22),
    (45.0, 49.0, (99.35, 33.5, 1.3), (99.4, 33.4, 1.28), (100.25, 32.45, 1.22), (100.25, 32.45, 1.22), 26),
    (49.0, 54.0, (101.9, 31.1, 1.35), (101.8, 31.25, 1.3), (100.55, 32.6, 0.7), (100.5, 32.7, 0.55), 20),
    (54.0, 59.0, (100.65, 33.75, 0.55), (100.6, 33.65, 0.55), (100.2, 32.65, 0.7), (100.2, 32.75, 0.65), 28),
    (59.0, END, (100.85, 31.0, 1.45), (100.75, 31.4, 1.42), (98.95, 35.0, 1.1), (98.95, 35.0, 1.1), 20),
]
cam = bpy.data.objects.new("Camera", bpy.data.cameras.new("Camera"))
sc.collection.objects.link(cam)
sc.camera = cam
cam.data.clip_start = 0.03
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
import json
os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
json.dump([s[0] for s in SHOTS[1:]], open(os.path.join(HERE, "out", "cuts.json"), "w"))

# ------------------------------------------------------------------ look
sc.frame_set(1)
T.toonify(sc, samples=int(os.environ.get("SAMPLES", "8")))
inked = [o for o in bpy.data.objects if o.type == "MESH" and not any(
    k in o.name.lower() for k in ("high-poly", "lash", "brow", "teeth", "tongue", "rivet", "led", "light", "ground",
                                  "road", "floor", "ceiling", "night", "dark", "rug", "slit", "dial"))]
T.ink(inked, 0.005)
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
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(HERE, "radio.blend"))
