"""«در رو باز نکن» — graphic-noir style (new): the «واگن آخر» puppets with ink outlines, hard light and deep black
shadows, rendered in Cycles; post turns everything black-and-white except one colour: red.
POV through «من» (fisheye in post), plus the door's peephole (round fisheye in post).

    ../cast/bpy.sh scene.py --still 40,120,...      -> test/s_XXXX.png
    ../cast/bpy.sh scene.py --save                  -> door.blend (render.py renders from it)
Story (seconds): 0 a voice message from «من»: "don't open the door, that's not mom" · 4.4 knocks · 6.2 "mom" behind
the door · 10.6 I walk to the door · 14.2 peephole: mom in red, smiling, too still · 17.7 the phone: mom is calling,
she is in traffic · 26.6 peephole: her head tilts, "why don't you open the door?" · 29.3 real mom: "don't open it!"
· 33 the corridor light dies: nobody there · 36.8 a whisper behind me · 38.7 I turn: she is inside · 40.2 black ·
41 I hide in the closet and record the same message to «من» · 45 delivered «دیروز ۲۳:۵۸».
"""
import bpy, sys, os, math, json, random
from mathutils import Vector, Matrix, Quaternion
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
for p in ("cast", "studio", "puppets"):
    sys.path.insert(0, os.path.join(HERE, "..", p))
bpy.ops.wm.read_factory_settings(use_empty=True)
import cast, mocap, lipsync  # noqa: E402
import props as P            # noqa: E402
import puppets as PP         # noqa: E402
from lines import LINES, END, FPS, PEEP, BLACK, fr, peep  # noqa: E402

cast.STYLE = cast.CARTOON
N = int(END * FPS)
sc = bpy.context.scene
sc.render.fps = FPS
sc.frame_start, sc.frame_end = 1, N
MOC = os.path.join(HERE, "..", "mocap")
TEX = os.path.join(HERE, "textures")


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
    """pts: [(seconds, visible)] constant keys on hide_render."""
    for t, v in pts:
        o.hide_render = not v
        o.keyframe_insert("hide_render", frame=max(1, fr(t)) if t > 0 else 1)
    for fc in fcurves_of(o):
        if fc.data_path == "hide_render":
            for k in fc.keyframe_points:
                k.interpolation = "CONSTANT"


def show(o, spans):
    pts = [(0, False)]
    for a, b in spans:
        pts += [(a, True), (b, False)]
    key_vis(o, pts)


# ------------------------------------------------------------------ set
H, WT = 2.6, 0.12
M = dict(
    wall=P.mat("Wall", (0.78, 0.76, 0.72), 0.9), wall2=P.mat("Wall corridor", (0.5, 0.52, 0.5), 0.9),
    floor=P.mat("Floor", (0.42, 0.33, 0.26), 0.6), tiles=P.mat("Corridor floor", (0.38, 0.38, 0.37), 0.5),
    ceil=P.mat("Ceiling", (0.8, 0.8, 0.78), 0.9), door=P.mat("Door", (0.36, 0.25, 0.18), 0.6),
    frame=P.mat("Frame", (0.85, 0.83, 0.8), 0.5), metal=P.mat("Metal", (0.75, 0.75, 0.75), 0.3, metal=0.8),
    sofa=P.mat("Sofa", (0.3, 0.3, 0.33), 0.9), wood=P.mat("Wood", (0.3, 0.22, 0.16), 0.6),
    blind=P.mat("Blind", (0.85, 0.85, 0.82), 0.6), dark=P.mat("Dark", (0.03, 0.03, 0.03), 0.9),
    coat=P.mat("Coat", (0.22, 0.22, 0.24), 0.9), rug=P.mat("Rug", (0.5, 0.48, 0.45), 0.9),
    picture=P.mat("Picture", (0.6, 0.6, 0.62), 0.6), shelf=P.mat("Closet wood", (0.45, 0.38, 0.3), 0.7),
    clothes=P.mat("Hanging clothes", (0.35, 0.34, 0.36), 0.9),
)
SET = []


def box(loc, size, m, name="Set"):
    o = P.box(loc, size, M[m] if isinstance(m, str) else m, name)
    SET.append(o)
    return o


DW, DH = 0.9, 2.1                              # front door (in the wall y=0, x -0.45..0.45)
HW, HL = 0.75, 4.5                             # inside hallway x -0.75..0.75, y 0..4.5
LR = (-2.6, 2.6, 4.5, 8.6)                     # living room x0, x1, y0, y1
CO = (-1.4, 1.4, -2.8, 0.0)                    # corridor outside x0, x1, y0, y1
# front wall with the door hole
box((-(DW / 2 + 1.5) / 2 - DW / 4 - 0.0, 0, H / 2), (1.5 + 0.0, WT, H), "wall", "Front wall L")
for o in SET[-1:]:
    o.location.x = -DW / 2 - 0.75
box((DW / 2 + 0.75, 0, H / 2), (1.5, WT, H), "wall", "Front wall R")
box((0, 0, (DH + H) / 2), (DW, WT, H - DH), "wall", "Front wall top")
for s in (-1, 1):
    box((s * (DW / 2 + 0.03), 0.0, DH / 2), (0.06, WT + 0.05, DH), "frame", "Door frame")
box((0, 0.0, DH + 0.03), (DW + 0.12, WT + 0.05, 0.06), "frame", "Door frame")
door = box((0, 0.0, (DH + 0.03) / 2 + 0.015), (DW - 0.01, 0.05, DH - 0.03), "door", "Front door")   # 3 cm gap below
box((0.33, 0.045, 1.0), (0.12, 0.04, 0.03), "metal", "Door handle in")
box((0.33, -0.045, 1.0), (0.12, 0.04, 0.03), "metal", "Door handle out")
P.cyl((0, 0.02, 1.55), (0, 0.04, 1.55), 0.012, M["metal"], "Peephole ring")
P.cyl((0, 0.025, 1.55), (0, 0.045, 1.55), 0.006, M["dark"], "Peephole glass")
for k in range(3):                               # chain lock + bolt
    box((-0.3, 0.035, 1.25 - k * 0.025), (0.04, 0.012, 0.012), "metal", "Door chain")
# inside hallway
box((0, HL / 2, -0.05), (2 * HW, HL, 0.1), "floor", "Hall floor")
box((0, HL / 2, H + 0.05), (2 * HW, HL, 0.1), "ceil", "Hall ceiling")
for s in (-1, 1):
    box((s * (HW + WT / 2), HL / 2, H / 2), (WT, HL, H), "wall", "Hall wall")
box((0, 1.6, 0.003), (0.8, 1.8, 0.006), "rug", "Hall rug")
box((-HW + 0.18, 1.1, 0.4), (0.3, 0.7, 0.8), "wood", "Shoe cabinet")
box((HW - 0.05, 1.3, 1.7), (0.04, 0.5, 0.04), "wood", "Coat rack")
box((HW - 0.18, 1.3, 1.25), (0.25, 0.4, 0.85), "coat", "Coat")
box((-HW + 0.01, 2.8, 1.5), (0.02, 0.6, 0.45), "picture", "Picture")
# living room
x0, x1, y0, y1 = LR
box(((x0 + x1) / 2, (y0 + y1) / 2, -0.05), (x1 - x0, y1 - y0, 0.1), "floor", "Room floor")
box(((x0 + x1) / 2, (y0 + y1) / 2, H + 0.05), (x1 - x0, y1 - y0, 0.1), "ceil", "Room ceiling")
box(((x0 + x1) / 2, y1 + WT / 2, H / 2), (x1 - x0, WT, H), "wall", "Room back wall")
for s in (-1, 1):                                # front wall of the room on both sides of the hallway
    box((s * (HW + (x1 - HW) / 2), y0, H / 2), (x1 - HW, WT, H), "wall", "Room front wall")
box((x1 + WT / 2, (y0 + y1) / 2, H / 2), (WT, y1 - y0, H), "wall", "Room right wall")
# left wall with the window (y 5.6..7.4, z 0.9..2.3) and blinds: the moonlight comes through in stripes
WY0, WY1, WZ0, WZ1 = 5.6, 7.4, 0.9, 2.3
box((x0 - WT / 2, (y0 + WY0) / 2, H / 2), (WT, WY0 - y0, H), "wall", "Room left wall")
box((x0 - WT / 2, (WY1 + y1) / 2, H / 2), (WT, y1 - WY1, H), "wall", "Room left wall")
box((x0 - WT / 2, (WY0 + WY1) / 2, WZ0 / 2), (WT, WY1 - WY0, WZ0), "wall", "Room left wall")
box((x0 - WT / 2, (WY0 + WY1) / 2, (WZ1 + H) / 2), (WT, WY1 - WY0, H - WZ1), "wall", "Room left wall")
z = WZ0 + 0.04
while z < WZ1:
    sl = box((x0 + 0.05, (WY0 + WY1) / 2, z), (0.07, WY1 - WY0, 0.012), "blind", "Blind slat")
    sl.rotation_euler = (math.radians(25), 0, 0)
    z += 0.075
box((0.9, 7.9, 0.25), (2.2, 0.85, 0.5), "sofa", "Sofa")
box((0.9, 8.3, 0.65), (2.2, 0.2, 0.8), "sofa", "Sofa back")
box((0.9, 6.7, 0.22), (1.0, 0.55, 0.44), "wood", "Coffee table")
box((2.3, 5.0, 0.4), (0.5, 0.5, 0.8), "wood", "Side table")
# corridor outside (the neighbours' door opposite, a fluorescent tube on the ceiling)
cx0, cx1, cy0, cy1 = CO
box(((cx0 + cx1) / 2, (cy0 + cy1) / 2, -0.05), (cx1 - cx0, cy1 - cy0, 0.1), "tiles", "Corridor floor")
box(((cx0 + cx1) / 2, (cy0 + cy1) / 2, H + 0.05), (cx1 - cx0, cy1 - cy0, 0.1), "ceil", "Corridor ceiling")
box(((cx0 + cx1) / 2, cy0 - WT / 2, H / 2), (cx1 - cx0, WT, H), "wall2", "Corridor far wall")
for s in (-1, 1):
    box((s * (cx1 + WT / 2), (cy0 + cy1) / 2, H / 2), (WT, cy1 - cy0, H), "wall2", "Corridor side wall")
box((0.2, cy0 + 0.04, DH / 2), (0.9, 0.04, DH), "door", "Neighbour door")
box((-0.2, cy0 + 0.08, 1.0), (0.12, 0.04, 0.03), "metal", "Neighbour handle")
tube_m = P.emit("Tube", (1.0, 1.0, 0.95), 6.0)
tube = P.box((0, -1.5, H - 0.04), (1.1, 0.08, 0.04), tube_m, "Tube")
tube_l = P.area_light((0, -1.5, H - 0.08), (0, -1.5, 0), 120, 1.1, (0.92, 0.96, 1.0), size_y=0.12, name="Tube light")
# the closet I hide in at the end (far away at x 8): slatted door in front (+Y), light beyond the slats
CX = 8.0
box((CX, 0.45, -0.05), (1.2, 1.1, 0.1), "shelf", "Closet floor")
box((CX, 0.45, H + 0.05), (1.2, 1.1, 0.1), "shelf", "Closet top")
box((CX, -0.1, H / 2), (1.2, WT, H), "shelf", "Closet back")
for s in (-1, 1):
    box((CX + s * 0.6, 0.45, H / 2), (WT, 1.1, H), "shelf", "Closet side")
z = 0.05
while z < 2.2:
    sl = box((CX, 1.0, z), (1.1, 0.02, 0.05), "shelf", "Closet slat")
    sl.rotation_euler = (math.radians(-35), 0, 0)
    z += 0.085
box((CX, 1.0, 2.35), (1.1, 0.04, 0.5), "shelf", "Closet door top")
for k in range(5):
    box((CX - 0.4 + k * 0.2, 0.0, 1.6 - (k % 2) * 0.15), (0.12, 0.2, 0.75), "clothes", "Hanging clothes")
box((CX, 0.05, 2.05), (1.1, 0.02, 0.02), "metal", "Closet rail")
box((CX, 3.0, -0.05), (3.0, 3.0, 0.1), "floor", "Bedroom floor")
P.area_light((CX + 0.3, 2.2, 1.9), (CX, 1.0, 1.0), 25, 0.6, (0.75, 0.82, 1.0), name="Bedroom moon")

# lights: moon through the blinds, a faint cold fill in the hall, the light under the door, the phone
moon = bpy.data.objects.new("Moon", bpy.data.lights.new("Moon", "SPOT"))
sc.collection.objects.link(moon)
moon.location = (x0 - 3.2, 6.5, 3.6)
moon.data.energy = 9000
moon.data.color = (0.8, 0.86, 1.0)
moon.data.spot_size = math.radians(40)
moon.data.shadow_soft_size = 0.02
moon.rotation_euler = (Vector((0.4, 6.3, 0.0)) - moon.location).to_track_quat("-Z", "Y").to_euler()
fill = P.area_light((0, 3.0, H - 0.1), (0, 3.0, 0), 1.2, 1.0, (0.7, 0.78, 1.0), name="Hall fill")
w = bpy.data.worlds.new("W")
sc.world = w
w.color = (0.004, 0.004, 0.006)
# the corridor light flickers and dies 33.0-35.0
FLICK = [(0, 1), (33.0, 0), (33.15, 1), (33.4, 0), (33.6, 1), (33.75, 0), (34.3, 0.6), (34.4, 0), (34.9, 1), (35.0, 0)]
for t, v in FLICK:
    f = max(1, fr(t))
    tube_l.data.energy = 55 * v
    tube_l.data.keyframe_insert("energy", frame=f)
    tube_m.node_tree.nodes["Emission"].inputs["Strength"].default_value = 6.0 * v
    tube_m.node_tree.nodes["Emission"].inputs["Strength"].keyframe_insert("default_value", frame=f)
for owner in (tube_l.data, tube_m.node_tree):
    for fc in fcurves_of(owner):
        for k in fc.keyframe_points:
            k.interpolation = "CONSTANT"

# ------------------------------------------------------------------ cast
PP.CAST["me"]["clothes"]["toigo_basic_tucked_t-shirt"] = (0.95, 0.95, 0.92)
PP.CAST["me"]["clothes"]["elvs_hooded_sweat_jacket1"] = (0.2, 0.2, 0.23)     # noir: a black hoodie
PP.CAST["me"]["clothes"]["punkduck_male_classic_jeans"] = (0.25, 0.27, 0.32)
PP.CAST["mom"]["clothes"]["janexx_old_female_sweater"] = (0.86, 0.04, 0.06)      # the only colour in the film
ME = PP.spawn("me")
FAKE = PP.spawn("mom", name="Fake")
CLIP = {}


def clip(name):
    if name not in CLIP:
        CLIP[name] = mocap.load(os.path.join(MOC, name + ".fbx"))
    return CLIP[name]


def face(p, q):
    """facing (degrees, 0 = +Y) from p towards q."""
    return math.degrees(math.atan2(-(q[0] - p[0]), q[1] - p[1]))


def hold(ch, name, t0, t1, pos, facing, **kw):
    mocap.apply(ch, clip(name), start=fr(t0), length=fr(t1) - fr(t0), offset=pos, facing=facing, **kw)


def walk(ch, t0, t1, p0, p1, facing):
    n = fr(t1) - fr(t0)
    a, b = Vector(p0), Vector(p1)

    def place(j):
        u = min(1.0, j / max(1, n - 1))
        uu = u * u * (3 - 2 * u) * 0.35 + u * 0.65
        p = a.lerp(b, uu)
        return (p.x, p.y, 0.0), facing
    v = (b - a).length / (t1 - t0)
    mocap.apply(ch, clip("walking"), start=fr(t0), length=n, in_place=True, loop=True,
                speed=max(0.6, min(1.3, v / 1.3)), place=place, blend=6)


ROOM_P, DOOR_P, CLOSET_P = (0.0, 4.7, 0), (0.0, 0.55, 0), (CX, 0.35, 0)
hold(ME, "breathing_idle", 0.0, 10.6, ROOM_P, 180)                  # (the arms hold the phone by IK, see below)
walk(ME, 10.6, 14.2, ROOM_P[:2], DOOR_P[:2], 180)
hold(ME, "breathing_idle", 14.2, 26.6, DOOR_P, 180, blend=8)
hold(ME, "breathing_idle", 26.6, 38.7, DOOR_P, 180, src_from=4.0, blend=8)
TURN = (38.7, 39.25)
hold(ME, "breathing_idle", 38.7, 41.0, DOOR_P, 0, blend=4, src_from=5.0)
hold(ME, "kneeling_idle", 41.0, END + 0.1, CLOSET_P, 0, speed=0.6)
# the fake mom: in the corridor, facing the door (+Y), until she is gone; then inside, between me and the room
FAKE_C, FAKE_IN = (0.0, -0.62, 0), (0.0, 1.3, 0)
hold(FAKE, "breathing_idle", 0.0, 9.9, FAKE_C, 0, speed=0.6)
hold(FAKE, "breathing_idle", 9.9, 19.8, FAKE_C, 0, speed=0.6, src_from=0.2, blend=10)
hold(FAKE, "breathing_idle", 19.8, 33.5, FAKE_C, 0, speed=0.5, src_from=0.4, blend=10)
hold(FAKE, "breathing_idle", 36.0, 41.0, FAKE_IN, 180, speed=0.5)
for ch in (ME, FAKE):                                # every segment holds its place (jumps only at cuts)
    for fc in fcurves_of(ch.rig):
        if fc.data_path in ("location", "rotation_euler"):
            for kp in fc.keyframe_points:
                kp.interpolation = "CONSTANT"
# my turn around (38.7-39.25): rotate the rig per frame from 180 to 0 degrees
for f in range(fr(TURN[0]), fr(TURN[1]) + 1):
    u = seg((f - 1) / FPS, *TURN)
    ME.rig.rotation_euler = (0, 0, math.radians(180 + 180 * u) + math.pi)
    ME.rig.keyframe_insert("rotation_euler", index=2, frame=f)


def tilt_head(ch, spans):
    """Add a slow sideways tilt of the head (degrees) over the mocap: spans [(t0, t1, deg0, deg1)]."""
    rig = ch.rig
    pb = rig.pose.bones["head"]
    fcs = {fc.array_index: fc for fc in fcurves_of(rig) if fc.data_path == 'pose.bones["head"].rotation_quaternion'}
    for t0, t1, d0, d1 in spans:
        for f in range(fr(t0), fr(t1) + 1):
            q = Quaternion([fcs[i].evaluate(f) for i in range(4)])
            deg = d0 + (d1 - d0) * seg((f - 1) / FPS, t0, t0 + min(1.6, t1 - t0))
            q = q @ Quaternion((0, 0, 1), math.radians(deg))
            for i in range(4):
                fcs[i].keyframe_points.insert(f, q[i], options={"FAST"})
    for fc in fcs.values():
        fc.update()


tilt_head(FAKE, [(26.6, 33.5, 0.0, 24.0), (36.0, 41.0, 28.0, 30.0)])

# who is where (hidden otherwise)
PRESENT = {"me": [(0, END + 1)], "fake": [(0, 33.4), (36.0, 40.3)]}

# ------------------------------------------------------------------ the phone (follows my hands, faces my eyes)
scr_m = {}
for nm in ("msg", "incoming", "call", "ended", "record", "sent"):
    m = bpy.data.materials.new("Phone " + nm)
    nt = m.node_tree
    nt.nodes.clear()
    o_ = nt.nodes.new("ShaderNodeOutputMaterial")
    e_ = nt.nodes.new("ShaderNodeEmission")
    tx = nt.nodes.new("ShaderNodeTexImage")
    tx.image = bpy.data.images.load(os.path.join(TEX, f"phone_{nm}.png"))
    nt.links.new(tx.outputs[0], e_.inputs[0])
    e_.inputs["Strength"].default_value = 1.4
    nt.links.new(e_.outputs[0], o_.inputs[0])
    scr_m[nm] = m
SCREENS = {"msg": [(0.0, 3.6)], "incoming": [(17.7, 19.0)], "call": [(19.0, 33.2)], "ended": [(33.2, BLACK[0])],
           "record": [(41.0, 45.0)], "sent": [(45.0, END + 1)]}
PHONE_ON = [(0.0, 3.6), (17.7, BLACK[0]), (BLACK[1], END + 1)]
phone = P.empty("Phone")
body = P.box((0, 0, -0.005), (0.075, 0.155, 0.008), P.mat("Phone body", (0.05, 0.05, 0.06), 0.3), "Phone body")
body.parent = phone
show(body, PHONE_ON)
for nm, spans in SCREENS.items():
    s = P.plane((0, 0, 0.0002), (0.068, 0.147), scr_m[nm], name="Phone screen " + nm)
    s.parent = phone
    show(s, spans)
plight = bpy.data.objects.new("Phone light", bpy.data.lights.new("Phone light", "POINT"))
sc.collection.objects.link(plight)
plight.data.energy = 0.7
plight.data.color = (0.85, 0.9, 1.0)
plight.data.shadow_soft_size = 0.05
plight.parent = phone
plight.location = (0, 0, 0.05)
show(plight, PHONE_ON)

# ------------------------------------------------------------------ camera: my eyes (POV); the peephole camera
mrig = ME.rig
hb = mrig.pose.bones["head"]
hb.scale = (0.001, 0.001, 0.001)
hb.keyframe_insert("scale", frame=1)
nb = mrig.pose.bones["neck_01"]
nb.scale = (0.2, 0.2, 0.2)
nb.keyframe_insert("scale", frame=1)
PHONE_T = "phone"
FAKE_FACE = (FAKE_IN[0], FAKE_IN[1], 1.48)
LOOK = [  # (t, where I look, seconds to turn there)
    (0.0, PHONE_T, 0.0),
    (3.0, (0.0, 0.0, 1.0), 0.9),             # up at the door: a strip of light under it
    (10.6, (0.0, 0.0, 1.35), 0.6),
    (17.7, PHONE_T, 0.4),
    (23.2, (0.0, 0.0, 1.45), 0.6),            # up at the door while mom talks on the phone
    (25.4, PHONE_T, 0.5),
    (29.2, PHONE_T, 0.3),
    (31.6, (0.0, 0.0, 1.5), 0.5),
    (36.0, PHONE_T, 0.4),
    (36.9, (0.3, 0.0, 1.35), 0.5),            # the whisper: a half turn of the head
    (38.7, FAKE_FACE, 0.55),                  # she is inside
    (41.0, PHONE_T, 0.0),
]


def hands_mid(f):
    sc.frame_set(f)
    a = (mrig.matrix_world @ mrig.pose.bones["hand_r"].matrix).translation
    b = (mrig.matrix_world @ mrig.pose.bones["hand_l"].matrix).translation
    return (a + b) / 2


def phone_inf(t):
    """1 while I hold the phone up (ramps of 0.25 s), else 0."""
    v = 0.0
    for a_, b_ in PHONE_ON:
        v = max(v, min(1.0, (t - a_ + 0.25) / 0.25, (b_ - t) / 0.25))
    return max(0.0, min(1.0, v))


IK = {}
for side in ("r", "l"):
    tg, po = P.empty(f"IK target {side}"), P.empty(f"IK pole {side}")
    c = mrig.pose.bones[f"lowerarm_{side}"].constraints.new("IK")
    c.target, c.pole_target, c.chain_count, c.use_tail = tg, po, 2, True
    IK[side] = (c, tg, po)
# pick the pole angle that bends the elbows towards the pole (down and out)
sc.frame_set(fr(1.0))
_rz = mrig.rotation_euler[2] - math.pi
_fw = Vector((-math.sin(_rz), math.cos(_rz), 0))
_rt = Vector((_fw.y, -_fw.x, 0))
for side, s_ in (("r", 1), ("l", -1)):
    c, tg, po = IK[side]
    sh = mrig.matrix_world @ mrig.pose.bones[f"upperarm_{side}"].head
    tg.location = sh + _fw * 0.33 - _rt * s_ * 0.12 + Vector((0, 0, -0.2))
    po.location = sh + _rt * s_ * 0.3 + Vector((0, 0, -0.5)) - _fw * 0.2
    best = None
    for ang in (0, 90, -90, 180):
        c.pole_angle = math.radians(ang)
        bpy.context.view_layer.update()
        el = mrig.matrix_world @ mrig.pose.bones[f"lowerarm_{side}"].head
        d = (el - po.location).length
        if best is None or d < best[0]:
            best = (d, ang)
    c.pole_angle = math.radians(best[1])
    print("POLE", side, best)


cam = bpy.data.objects.new("Camera", bpy.data.cameras.new("Camera"))
sc.collection.objects.link(cam)
sc.camera = cam
cam.data.clip_start = 0.03
cam.data.lens = 15
cam.data.sensor_width = 36
cam.rotation_mode = "QUATERNION"
peepcam = bpy.data.objects.new("Peephole", bpy.data.cameras.new("Peephole"))
sc.collection.objects.link(peepcam)
peepcam.data.clip_start = 0.02
peepcam.data.lens = 9
peepcam.data.sensor_width = 36
peepcam.location = (0, -0.04, 1.55)
peepcam.rotation_euler = (math.radians(84), 0, math.radians(180))
_rnd = random.Random(7)
eye_s = hand_s = d_prev = None
EYE = {}
phone.rotation_mode = "QUATERNION"
for f in range(1, N + 1):
    t = (f - 1) / FPS
    sc.frame_set(f)
    hw = mrig.matrix_world @ nb.matrix
    rz = mrig.rotation_euler[2] - math.pi
    fwd = Vector((-math.sin(rz), math.cos(rz), 0))
    eye = hw.translation + Vector((0, 0, 0.23)) + fwd * 0.13
    jump = eye_s is not None and (eye - eye_s).length > 1.0
    eye_s = eye if (eye_s is None or jump) else eye_s.lerp(eye, 0.45)
    # the phone in both hands in front of my chest, screen towards my eyes (it shakes a little while it rings,
    # and my hands tremble); the arms reach it by IK
    right = Vector((fwd.y, -fwd.x, 0))
    pp = eye_s + fwd * 0.27 + Vector((0, 0, -0.22)) + right * 0.02
    pp = pp + Vector((math.sin(t * 7.1), math.sin(t * 5.3 + 1), math.sin(t * 6.2 + 2))) * 0.0025
    if 17.7 <= t < 19.0:
        pp = pp + Vector((_rnd.uniform(-1, 1), _rnd.uniform(-1, 1), 0)) * 0.003
    phone.location = pp
    phone.rotation_quaternion = (eye_s - pp).to_track_quat("Z", "Y")
    phone.keyframe_insert("location", frame=f)
    phone.keyframe_insert("rotation_quaternion", frame=f)
    nrm = (eye_s - pp).normalized()
    up_s = phone.rotation_quaternion @ Vector((0, 1, 0))
    inf = phone_inf(t)
    for side, s_ in (("r", 1), ("l", -1)):
        c, tg, po = IK[side]
        tg.location = pp + right * s_ * 0.05 - up_s * 0.125 - nrm * 0.015      # the bottom corners of the phone
        sh = (mrig.matrix_world @ mrig.pose.bones[f"upperarm_{side}"].head)
        po.location = sh + right * s_ * 0.3 + Vector((0, 0, -0.5)) - fwd * 0.2
        tg.keyframe_insert("location", frame=f)
        po.keyframe_insert("location", frame=f)
        c.influence = inf
        c.keyframe_insert("influence", frame=f)
    ME.hands_pose(f, "grip" if inf > 0.5 else "relaxed")

    def target(k):
        v = LOOK[k][1]
        return pp if v == PHONE_T else Vector(v)
    k = max(i for i, l in enumerate(LOOK) if l[0] <= t)
    d1 = (target(k) - eye_s).normalized()
    if k > 0 and LOOK[k][2] > 0:
        d0 = (target(k - 1) - eye_s).normalized()
        d = d0.lerp(d1, seg(t, LOOK[k][0], LOOK[k][0] + LOOK[k][2])).normalized()
    else:
        d = d1
    d_prev = d if (d_prev is None or jump or LOOK[k][2] == 0 and abs(t - LOOK[k][0]) < 0.01) else d_prev.lerp(d, 0.5).normalized()
    dz = max(d_prev.z, -0.75)
    hz = Vector((d_prev.x, d_prev.y, 0)).normalized() * math.sqrt(1 - dz * dz)
    q = Vector((hz.x, hz.y, dz)).to_track_quat("-Z", "Y")
    q.rotate(Matrix.Rotation(0.004 * _rnd.uniform(-1, 1), 4, "X"))
    cam.location = eye_s
    cam.rotation_quaternion = q
    cam.keyframe_insert("location", frame=f)
    cam.keyframe_insert("rotation_quaternion", frame=f)
    EYE[f] = eye_s.copy()
for owner in (cam, phone) + tuple(o for v in IK.values() for o in v[1:]):
    for fc in fcurves_of(owner):
        for kp in fc.keyframe_points:
            kp.interpolation = "LINEAR"
sc["peep"] = json.dumps(PEEP)

# ------------------------------------------------------------------ faces
LS = lipsync.Voices(fps=FPS)
for a, b, who, text, fn, how in LINES:
    if who == "fake":
        LS.add("fake", os.path.join(HERE, "voices", fn + ".mp3"), a)


def present(who, t):
    return any(a <= t < b for a, b in PRESENT[who])


for who, ch in (("me", ME), ("fake", FAKE)):
    for f in range(1, N + 1):
        t = (f - 1) / FPS
        if f == 1 or present(who, t) != present(who, t - 1 / FPS):
            ch.hide(f, not present(who, t))
rig = FAKE.rig
for f in range(1, N + 1):
    t = (f - 1) / FPS
    if not present("fake", t):
        continue
    sc.frame_set(f)
    la = peepcam.location if t < 34 else EYE[f]                 # she stares into the peephole, then at me
    lv = LS.level("fake", t)
    smile = 0.55 + 0.45 * seg(t, 26.6, 28.0) if t < 34 else 1.0
    st = dict(t=t, seed=FAKE.seed + 3, worry=0.0, talking=lv if lv > 0.05 else False, look_at=Vector(la),
              smile=smile, brows="neutral")
    if t > 26.6:
        st["mouth"] = {"wide": 0.2 * seg(t, 26.6, 28.0)}
    if t > 36.0:
        st["mouth"] = {"wide": 0.35}
    FAKE.face_pose(f, t, st)
FAKE.flush()
ME.flush()
sc.frame_set(1)
PP.finish(ME, outline=0.0016, smile=0, keep_head=True)
PP.finish(FAKE, outline=0.006, smile=0)
# noir: the toon materials only show what the light hits (low self-glow), the set is toon too
import colorsys
for o in list(bpy.data.objects):
    if o.type != "MESH":
        continue
    for slot in o.material_slots:
        m = slot.material
        if not m or not m.node_tree or m.name.startswith(("Hull", "Phone")) or m.name in ("Tube",):
            continue
        if m.name.startswith("PP "):
            e = m.node_tree.nodes.get("Emission")
            if e:
                e.inputs["Strength"].default_value = 0.05 if "skin" not in m.name.lower() else 0.08
            continue
        if any(n.type in ("TEX_IMAGE", "EMISSION") for n in m.node_tree.nodes):
            continue
        c = PP._base(m)
        if c is None:
            continue
        slot.material = PP.toon_mat(f"set {m.name}", c, 0.02)
sc.render.engine = "CYCLES"
sc.cycles.samples = int(os.environ.get("SAMPLES", "16"))
sc.cycles.use_denoising = True
sc.cycles.max_bounces = 4
sc.view_settings.view_transform = "Standard"
sc.view_settings.look = "None"
sc.render.resolution_x, sc.render.resolution_y = 540, 960

args = sys.argv
if "--still" in args:
    os.makedirs(os.path.join(HERE, "test"), exist_ok=True)
    for f in [int(v) for v in args[args.index("--still") + 1].split(",")]:
        sc.frame_set(f)
        sc.camera = peepcam if peep((f - 1) / FPS) else cam
        sc.render.filepath = os.path.join(HERE, "test", f"s_{f:04d}.png")
        bpy.ops.render.render(write_still=True)
if "--save" in args:
    sc.camera = cam
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(HERE, "door.blend"))
