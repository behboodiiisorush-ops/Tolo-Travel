"""«صدای مامان» — puppet style («واگن آخر»), POV through my eyes, Mixamo motion, Cycles toon look.
Night. I sit on the sofa. Mom calls: she is stuck in traffic. From the dark kitchen her voice calls us to dinner.
Arian comes out of the kitchen, terrified. On the phone mom asks why I am silent. Mom stands in the doorway, smiling.

    ../cast/bpy.sh scene.py --still 40,200,...   -> test/s_XXXX.png
    ../cast/bpy.sh scene.py --save               -> mom_voice.blend (render.py renders from it)
"""
import bpy, sys, os, math, json, random
from mathutils import Vector, Matrix
HERE = os.path.dirname(os.path.abspath(__file__))
for d in ("", "../cast", "../studio", "../puppets"):
    sys.path.insert(0, os.path.join(HERE, d))
bpy.ops.wm.read_factory_settings(use_empty=True)
import cast, mocap      # noqa: E402
import props as P       # noqa: E402
import puppets as PP    # noqa: E402
from captions import END  # noqa: E402

cast.STYLE = cast.CARTOON
FPS = 24
N = int(END * FPS)
sc = bpy.context.scene
sc.render.fps = FPS
sc.frame_start, sc.frame_end = 1, N
MOC = os.path.join(HERE, "..", "mocap")
LEV = json.load(open(os.path.join(HERE, "out", "levels.json")))


def fr(t):
    return int(round(t * FPS)) + 1


def seg(t, a, b):
    if t <= a:
        return 0.0
    if t >= b:
        return 1.0
    u = (t - a) / (b - a)
    return u * u * (3 - 2 * u)


def level(who, t):
    for a, r in LEV.get(who, []):
        k = int((t - a) * FPS)
        if 0 <= k < len(r):
            return r[k]
    return 0.0


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
    for t, v in pts:
        o.hide_render = not v
        o.keyframe_insert("hide_render", frame=max(1, fr(t)) if t > 0 else 1)
    for fc in fcurves_of(o):
        if fc.data_path == "hide_render":
            for k in fc.keyframe_points:
                k.interpolation = "CONSTANT"


def const(owner):
    for fc in fcurves_of(owner):
        for k in fc.keyframe_points:
            k.interpolation = "CONSTANT"


# ------------------------------------------------------------------ set: living room (x 0..5, y 0..4.5), kitchen at y<0
H, WT, W, D = 2.7, 0.14, 5.0, 4.5
M_ = dict(
    wall=P.mat("Wall", (0.72, 0.66, 0.56), 0.9), wall2=P.mat("Wall 2", (0.36, 0.41, 0.45), 0.9),
    floor=P.mat("Floor", (0.42, 0.3, 0.22), 0.6), ceil=P.mat("Ceiling", (0.75, 0.74, 0.7), 0.9),
    rug=P.mat("Rug", (0.32, 0.17, 0.16), 0.95), sofa=P.mat("Sofa", (0.28, 0.36, 0.48), 0.9),
    wood=P.mat("Wood", (0.45, 0.32, 0.22), 0.6), frame=P.mat("Frame", (0.92, 0.92, 0.9), 0.5),
    tile=P.mat("Kitchen tiles", (0.4, 0.43, 0.44), 0.4), cab=P.mat("Cabinet", (0.6, 0.65, 0.6), 0.6),
    counter=P.mat("Counter", (0.88, 0.88, 0.85), 0.4), metal=P.mat("Metal", (0.7, 0.72, 0.74), 0.3, metal=0.8),
    phone=P.mat("Phone", (0.06, 0.06, 0.08), 0.3), shade=P.mat("Lamp shade", (0.95, 0.85, 0.6), 0.8),
    plant=P.mat("Plant", (0.25, 0.5, 0.25), 0.8), pot=P.mat("Pot", (0.7, 0.4, 0.25), 0.7),
    pot2=P.mat("Pot 2", (0.75, 0.75, 0.78), 0.4, metal=0.5), night=P.mat("Night sky", (0.05, 0.08, 0.18), 0.9),
    curtain=P.mat("Curtain", (0.82, 0.74, 0.5), 0.9), book=P.mat("Book", (0.7, 0.25, 0.2), 0.8),
    book2=P.mat("Book 2", (0.2, 0.4, 0.6), 0.8),
)


def box(loc, size, m, name="Set"):
    return P.box(loc, size, M_[m] if isinstance(m, str) else m, name)


box((W / 2, D / 2, -0.05), (W, D, 0.1), "floor", "Floor")
box((W / 2, D / 2, H + 0.05), (W, D, 0.1), "ceil", "Ceiling")
box((W / 2, D + WT / 2, H / 2), (W, WT, H), "wall", "Back wall")
box((-WT / 2, D / 2, H / 2), (WT, D, H), "wall", "Left wall")
box((W + WT / 2, D / 2, H / 2), (WT, D, H), "wall", "Right wall")
# front wall with the kitchen doorway (x 3.75..4.65, up to 2.1 m)
DX0, DX1, DH = 3.75, 4.65, 2.1
box((DX0 / 2, -WT / 2, H / 2), (DX0, WT, H), "wall", "Front wall")
box(((DX1 + W) / 2, -WT / 2, H / 2), (W - DX1, WT, H), "wall", "Front wall")
box(((DX0 + DX1) / 2, -WT / 2, (DH + H) / 2), (DX1 - DX0, WT, H - DH), "wall", "Front wall")
for x in (DX0 - 0.03, DX1 + 0.03):
    box((x, -WT / 2, DH / 2), (0.06, WT + 0.04, DH), "frame", "Door frame")
box(((DX0 + DX1) / 2, -WT / 2, DH + 0.03), (DX1 - DX0 + 0.12, WT + 0.04, 0.06), "frame", "Door frame")
# window on the left wall: night outside, curtains open
box((0.02, 1.6, 1.5), (0.04, 1.3, 1.1), "night", "Window night")
for y in (0.95, 2.25):
    box((0.03, y, 1.5), (0.06, 0.06, 1.16), "frame", "Window frame")
for z in (0.95, 2.05, 1.5):
    box((0.03, 1.6, z), (0.06, 1.36, 0.05), "frame", "Window frame")
for y in (0.72, 2.48):
    box((0.08, y, 1.45), (0.06, 0.4, 1.9), "curtain", "Curtain")
# kitchen (y -3.2..0): tiled floor, counter, fridge, a pot on the stove
box((4.2, -1.6, -0.05), (3.0, 3.2, 0.1), "tile", "Kitchen floor")
box((4.2, -3.2 - WT / 2, H / 2), (3.0, WT, H), "wall2", "Kitchen back wall")
box((2.7 - WT / 2, -1.67, H / 2), (WT, 3.06, H), "wall2", "Kitchen wall")   # stops behind the front wall (no z-fight)
box((5.7 + WT / 2, -1.67, H / 2), (WT, 3.06, H), "wall2", "Kitchen wall")
box((4.2, -1.6, H + 0.05), (3.0, 3.2, 0.1), "ceil", "Kitchen ceiling")
box((4.2, -2.85, 0.45), (2.6, 0.6, 0.9), "cab", "Kitchen counter")
box((4.2, -2.85, 0.92), (2.7, 0.66, 0.05), "counter", "Counter top")
P.cyl((3.8, -2.85, 0.95), (3.8, -2.85, 1.12), 0.15, M_["pot2"], "Pot")
box((5.25, -2.1, 0.9), (0.6, 0.65, 1.8), "frame", "Fridge")
# living room: sofa (I sit on it), coffee table with the phone, floor lamp, TV stand, plant, rug
SX, SY = 2.4, 3.95
box((SX, SY, 0.25), (2.2, 0.85, 0.5), "sofa", "Sofa")
box((SX, SY + 0.37, 0.7), (2.2, 0.2, 0.9), "sofa", "Sofa back")
for dx in (-1.15, 1.15):
    box((SX + dx, SY, 0.42), (0.2, 0.85, 0.5), "sofa", "Sofa arm")
box((SX, 2.85, 0.4), (1.1, 0.6, 0.05), "wood", "Coffee table")
for dx in (-0.48, 0.48):
    for dy in (-0.24, 0.24):
        box((SX + dx, 2.85 + dy, 0.19), (0.05, 0.05, 0.38), "wood", "Table leg")
box((2.3, 2.1, 0.005), (2.4, 1.8, 0.01), "rug", "Rug")
box((1.4, 0.35, 0.3), (1.6, 0.4, 0.6), "wood", "TV stand")
box((1.4, 0.32, 0.95), (1.1, 0.06, 0.62), "phone", "TV (off)")
box((1.0, 0.35, 0.64), (0.2, 0.25, 0.08), "book", "Books")
box((1.25, 0.35, 0.66), (0.22, 0.24, 0.06), "book2", "Books")
P.cyl((4.55, 4.1, 0.0), (4.55, 4.1, 1.5), 0.02, M_["metal"], "Lamp pole")
P.cyl((4.55, 4.1, 1.45), (4.55, 4.1, 1.75), 0.2, M_["shade"], "Lamp shade")
P.cyl((0.45, 4.1, 0.0), (0.45, 4.1, 0.35), 0.18, M_["pot"], "Plant pot")
P.sphere((0.45, 4.1, 0.6), 0.32, M_["plant"], "Plant")
# the phone on the coffee table: its screen lights up when it rings and stays lit during the call
PX, PY, PZ = SX + 0.15, 2.78, 0.44
box((PX, PY, PZ), (0.08, 0.16, 0.012), "phone", "Phone")
scrm = P.emit("Phone screen", (0.6, 0.85, 1.0), 0.0)
scr = P.plane((PX, PY, PZ + 0.007), (0.07, 0.145), scrm, name="Phone screen")
em = [n for n in scrm.node_tree.nodes if n.type == "EMISSION"][0]
for t, s in [(0, 0.0), (1.2, 0.0), (1.25, 3.0), (26.4, 3.0), (26.5, 0.0)]:
    em.inputs["Strength"].default_value = s
    em.inputs["Strength"].keyframe_insert("default_value", frame=fr(t))
# lights: warm floor lamp (the room), cold dim kitchen light, moonlight through the window
world = bpy.data.worlds.new("W")
sc.world = world
world.color = (0.03, 0.035, 0.06)
lamp = P.area_light((4.4, 3.8, 1.9), (2.5, 2.0, 0.5), 60, 0.8, (1.0, 0.82, 0.6), name="Floor lamp")
fill = P.area_light((2.5, 2.0, 2.6), (2.5, 2.0, 0), 4, 3.5, (0.9, 0.85, 0.8), name="Room fill")
kit = P.area_light((4.2, -1.4, 2.55), (4.2, -1.4, 0), 2.5, 1.2, (0.7, 0.85, 1.0), name="Kitchen light")
moon = P.area_light((-0.6, 1.6, 1.6), (2.0, 1.8, 0.4), 15, 1.0, (0.5, 0.6, 1.0), name="Moon")
phone_glow = bpy.data.objects.new("Phone glow", bpy.data.lights.new("Phone glow", "POINT"))
sc.collection.objects.link(phone_glow)
phone_glow.location = (PX, PY, PZ + 0.12)
phone_glow.data.color = (0.6, 0.85, 1.0)
for t, e in [(0, 0.0), (1.2, 0.0), (1.25, 2.5), (26.4, 2.5), (26.5, 0.0)]:
    phone_glow.data.energy = e
    phone_glow.data.keyframe_insert("energy", frame=fr(t))
# the lights flicker while mom stands in the doorway, then the lamp dies (31.2)
FLICK = [0, 28.6, 28.75, 28.9, 29.0, 29.5, 29.6, 30.4, 30.5, 31.2]
for k, t in enumerate(FLICK):
    on = k % 2 == 0 and t < 31.2
    for L, e in ((lamp, 60), (fill, 4)):
        L.data.energy = e if on else (0.0 if t >= 31.2 else e * 0.08)
        L.data.keyframe_insert("energy", frame=fr(t))
for L in (lamp, fill, phone_glow):
    const(L.data)
const(scrm.node_tree)

# ------------------------------------------------------------------ cast
CH = {k: PP.spawn(k) for k in ("me", "arian", "mom")}
for ch in CH.values():
    ch.zombie = 0.0
CLIP = {}


def clip(name):
    if name not in CLIP:
        CLIP[name] = mocap.load(os.path.join(MOC, name + ".fbx"))
    return CLIP[name]


def face(p, q):
    return math.degrees(math.atan2(-(q[0] - p[0]), q[1] - p[1]))


def walk(who, t0, t1, pts, f_to):
    pts = [Vector(p) for p in pts]
    lens = [(b - a).length for a, b in zip(pts, pts[1:])]
    L = sum(lens)
    n = fr(t1) - fr(t0)

    def at(s):
        s = max(0.0, min(L, s))
        for (a, b), l in zip(zip(pts, pts[1:]), lens):
            if s <= l:
                return a.lerp(b, s / max(l, 1e-6))
            s -= l
        return pts[-1]

    def place(j):
        u = min(1.0, j / max(1, n - 1))
        uu = u * u * (3 - 2 * u) * 0.3 + u * 0.7
        p = at(uu * L)
        q = at(uu * L + 0.3)
        fw = face(p, q) if (q - p).length > 1e-3 else f_to
        k1 = seg(j / FPS, (t1 - t0) - 0.45, t1 - t0)
        d = (f_to - fw + 180) % 360 - 180
        return (p.x, p.y, 0.0), fw + d * k1
    mocap.apply(CH[who], clip("walking"), start=fr(t0), length=n, in_place=True, loop=True,
                speed=max(0.7, min(1.3, L / (t1 - t0) / 1.3)), place=place, blend=8)


def act(who, name, t0, t1, pos, facing, blend=8, **kw):
    rig = CH[who].rig
    mocap.apply(CH[who], clip(name), start=fr(t0), length=fr(t1) - fr(t0), offset=pos, facing=facing,
                blend=blend, **kw)
    rig.location = pos
    rig.rotation_euler = (0, 0, math.radians(facing) + math.pi)
    rig.keyframe_insert("location", frame=fr(t1) - 1)
    rig.keyframe_insert("rotation_euler", index=2, frame=fr(t1) - 1)


# me: sitting on the sofa the whole film, facing the room (-Y)
act("me", "sitting_idle", 0.0, END, (SX - 0.25, SY - 0.05, 0.02), 180, blend=0, loop=True)
# Arian: in the kitchen (unseen), walks out through the doorway at 12.0, stops by the table, terrified
AP = (1.75, 2.3)          # beside the table, out of the line between me and the doorway
act("arian", "breathing_idle", 0.0, 12.0, (3.1, -1.3, 0.0), 0, blend=0, loop=True)   # hidden behind the wall
F_ME = face(AP, (SX - 0.25, SY))
F_PT = face(AP, ((DX0 + DX1) / 2, 0.0)) - 90           # the clip points to his left -> the arm aims at the kitchen
F_PT = F_ME + ((F_PT - F_ME + 180) % 360 - 180)
walk("arian", 12.0, 15.2, [(3.1, -1.3), (4.0, -0.7), (4.2, 0.2), (3.6, 1.4), AP], F_PT)


def turn_act(who, name, t0, t1, pos, f0, f1, secs, **kw):
    """Play a stationary clip while turning smoothly from f0 to f1 over `secs` (no snap)."""
    n = fr(t1) - fr(t0)
    mocap.apply(CH[who], clip(name), start=fr(t0), length=n, in_place=True, blend=8,
                place=lambda j: ((pos[0], pos[1], 0.0), f0 + (f1 - f0) * seg(j / FPS, 0.0, secs)), **kw)


turn_act("arian", "pointing", 15.2, 18.0, AP, F_PT, F_PT, 0.1)          # «مامان تو آشپزخونه‌ست...»
turn_act("arian", "breathing_idle", 18.0, 20.4, AP, F_PT, F_ME, 0.6, loop=True)   # «...پس تو داری با کی حرف می‌زنی؟»
turn_act("arian", "terrified", 20.4, END, AP, F_ME, F_ME, 0.1, loop=True)
# mom: only seen in the doorway from 25.6, standing still (a little too still), smiling
MP = ((DX0 + DX1) / 2, -0.35)
act("mom", "breathing_idle", 0.0, END, (MP[0], MP[1], 0.0), 0, blend=0, loop=True, speed=0.6)
for o in CH["mom"].objects:
    key_vis(o, [(0, False), (25.6, True)])

# ------------------------------------------------------------------ camera: my eyes
me = CH["me"]
mrig = me.rig
hb = mrig.pose.bones["head"]
hb.scale = (0.001, 0.001, 0.001)
hb.keyframe_insert("scale", frame=1)
nb = mrig.pose.bones["neck_01"]
nb.scale = (0.2, 0.2, 0.2)
nb.keyframe_insert("scale", frame=1)
DOOR = Vector(((DX0 + DX1) / 2, -0.2, 1.2))
LOOK = [  # (t, target, seconds to turn)
    (0.0, (2.0, 0.0, 1.1), 0.0),            # the quiet room, the dark TV
    (1.4, (PX, PY, PZ), 0.8),               # the phone lights up on the table
    (8.7, tuple(DOOR), 0.5),                # the voice from the kitchen
    (12.3, (4.1, 0.4, 1.3), 0.6),           # Arian comes out
    (13.8, (2.6, 1.9, 1.35), 0.9),
    (15.2, (AP[0], AP[1], 1.35), 0.6),      # his face
    (19.5, (PX, PY, PZ), 0.6),              # the phone again
    (25.9, (MP[0], MP[1], 1.5), 0.7),       # mom in the doorway
]
cam = bpy.data.objects.new("Camera", bpy.data.cameras.new("Camera"))
sc.collection.objects.link(cam)
sc.camera = cam
cam.data.clip_start = 0.03
cam.data.lens = 15
cam.data.sensor_width = 36
cam.rotation_mode = "QUATERNION"
_rnd = random.Random(5)
eye_s = d_prev = None
EYE = {}
for f in range(1, N + 1):
    t = (f - 1) / FPS
    sc.frame_set(f)
    hw = mrig.matrix_world @ nb.matrix
    fwd = Vector((-math.sin(mrig.rotation_euler[2] - math.pi), math.cos(mrig.rotation_euler[2] - math.pi), 0))
    eye = hw.translation + Vector((0, 0, 0.23)) + fwd * 0.13
    eye_s = eye if eye_s is None else eye_s.lerp(eye, 0.45)
    k = max(i for i, l in enumerate(LOOK) if l[0] <= t)
    d1 = (Vector(LOOK[k][1]) - eye_s).normalized()
    if k > 0:
        d0 = (Vector(LOOK[k - 1][1]) - eye_s).normalized()
        d = d0.lerp(d1, seg(t, LOOK[k][0], LOOK[k][0] + LOOK[k][2])).normalized()
    else:
        d = d1
    d_prev = d if d_prev is None else d_prev.lerp(d, 0.5).normalized()
    dz = max(d_prev.z, -0.72)
    hz = Vector((d_prev.x, d_prev.y, 0)).normalized() * math.sqrt(1 - dz * dz)
    q = Vector((hz.x, hz.y, dz)).to_track_quat("-Z", "Y")
    amp = 0.004 + (0.006 if 26.0 < t < 31 else 0.0)        # breathing gets shaky when I see her
    q.rotate(Matrix.Rotation(amp * _rnd.uniform(-1, 1), 4, "X"))
    cam.location = eye_s
    cam.rotation_quaternion = q
    cam.keyframe_insert("location", frame=f)
    cam.keyframe_insert("rotation_quaternion", frame=f)
    cam.data.lens = 15 + 9 * seg(t, 26.2, 30.5) ** 1.5     # slow push-in on her face
    cam.data.keyframe_insert("lens", frame=f)
    EYE[f] = eye_s.copy()
for fc in fcurves_of(cam):
    for kp in fc.keyframe_points:
        kp.interpolation = "LINEAR"

# ------------------------------------------------------------------ faces: lips from the real voices, blinks
for who, ch in CH.items():
    if who == "me":
        continue
    rig = ch.rig
    for f in range(1, N + 1):
        t = (f - 1) / FPS
        sc.frame_set(f)
        hw = rig.matrix_world @ rig.pose.bones["head"].head
        st = dict(t=t, seed=ch.seed, look_at=EYE[f])
        if who == "arian":
            st["worry"] = 1.6 if t > 13.0 else 0.0
            st["talking"] = level("arian", t)
        else:
            st["talking"] = level("mom", t)
            st["smile"] = 0.9                   # the same warm smile, never changing
        ch.face_pose(f, t, st)
    ch.flush()
sc.frame_set(1)
for who, ch in CH.items():
    PP.finish(ch, outline=0.0016 if who == "me" else 0.0055, smile=0, keep_head=(who == "me"))
import colorsys
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
        c2 = colorsys.hsv_to_rgb(h, min(1, sa * 1.4 + 0.06), min(1, v * 1.1 + 0.04))
        slot.material = PP.toon_mat(f"set {m.name}", c2, 0.18)
sc.render.engine = "CYCLES"
sc.cycles.samples = int(os.environ.get("SAMPLES", "12"))
sc.cycles.use_denoising = True
sc.cycles.max_bounces = 3
sc.view_settings.view_transform = "Standard"
sc.render.resolution_x, sc.render.resolution_y = 540, 960

args = sys.argv
if "--still" in args:
    os.makedirs(os.path.join(HERE, "test"), exist_ok=True)
    for f in [int(v) for v in args[args.index("--still") + 1].split(",")]:
        sc.frame_set(f)
        sc.render.filepath = os.path.join(HERE, "test", f"s_{f:04d}.png")
        bpy.ops.render.render(write_still=True)
if "--save" in args:
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(HERE, "mom_voice.blend"))
