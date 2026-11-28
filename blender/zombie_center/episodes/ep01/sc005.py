"""EP01 · CH01_SC005 — INT. PHARMACY — NIGHT · 22:52–23:00 · 80 s (scene frames 1–1920, its own timeline)

    blender/cast/bpy.sh blender/zombie_center/episodes/ep01/sc005.py layout | preview | final

 1  0–8    POV 24: shoulder through the broken door, drag a shelf across it
 2  8–14   medium 50: the TV card on the wall; Arin's silhouette passes in front
 3  14–24  medium 35 behind the counter: disinfectant, a hiss of breath, gauze round the LEFT palm
 4  24–27  flash insert, overexposed: a child's hand holding a smaller hand in a white corridor (lullaby hum)
 5  27–34  CU 50: he rubs his eyes, dials Nika — «خاموش است»
 6  34–39  insert: the phone rings — «شماره‌ی ناشناس»
 7  39–77  CU 85, slow push-in over the call (Mark is never seen; his voice is band-passed in the mix)
 8  77–80  medium 35: the call-back fails; two heavy hits on the door; he freezes
Voices (../audio/voice): mark_01 @40.0, arin_06 @43.4, mark_02 @46.4, arin_07 @55.4, mark_03 @58.6.
"""
import bpy, sys, os, math
HERE = os.path.dirname(os.path.abspath(__file__))
ZC = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path[:0] = [ZC, os.path.join(ZC, "sets")]
import pharmacy, phone, zc_cast, mocap, motion_qc as Q, perform as A, lipsync
import props as P
from mathutils import Vector

MODE = sys.argv[-1] if sys.argv[-1] in ("layout", "preview", "final") else "layout"
MOCAP = os.path.join(ZC, "..", "mocap")
VOICE = os.path.join(HERE, "audio", "voice")
TEX = os.path.join(HERE, "tex")
FPS = 24
T = lambda s: 1 + int(round(s * FPS))
F0, F1 = 1, T(80) - 1
SHOT_T = [0, 8, 14, 24, 27, 34, 39, 77, 80]
SHOTS = [(T(a), T(b) - 1) for a, b in zip(SHOT_T, SHOT_T[1:])]
LINES = [("arin", "sc005_arin_06", 43.4), ("arin", "sc005_arin_07", 55.4),
         ("mark", "sc005_mark_01", 40.0), ("mark", "sc005_mark_02", 46.4), ("mark", "sc005_mark_03", 58.6)]

sc = bpy.context.scene
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)
sc.render.fps = FPS
sc.frame_start, sc.frame_end = F0, F1
R = pharmacy.build(TEX)
DOOR = Vector(R["door"]); CB = Vector(R["counter_back"]); TV = Vector(R["tv"])

# ---------------------------------------------------------------- the shelf he drags across the door (0–8 s)
shelf = R["shelf_drag"]
s0 = shelf.location.copy()
shelf.keyframe_insert("location", frame=T(3.0)); shelf.keyframe_insert("rotation_euler", frame=T(3.0))
shelf.location = Vector((DOOR.x + 0.2, DOOR.y + 0.45, 0)); shelf.rotation_euler = (0, 0, 0)
shelf.keyframe_insert("location", frame=T(7.0)); shelf.keyframe_insert("rotation_euler", frame=T(7.0))

# ---------------------------------------------------------------- Arin
arin = zc_cast.spawn("zc_arin")
walk = mocap.load(os.path.join(MOCAP, "walking.fbx"))
kneel = mocap.load(os.path.join(MOCAP, "kneeling_idle.fbx"))
pace = mocap.load(os.path.join(MOCAP, "talking_phone_pacing.fbx"))
# 8–14: walks from the door past the TV to the counter end (left to right in shot 2)
W0 = Vector((DOOR.x + 0.3, DOOR.y + 1.0, 0)); W1 = Vector((-1.6, 0.4, 0)); W2 = Vector((CB.x - 1.2, CB.y, 0))


def walk_place(j, n=T(14) - T(8)):
    u = j / n
    p = W0.lerp(W1, min(1, u * 2)) if u < 0.5 else W1.lerp(W2, (u - 0.5) * 2)
    v = (W1 - W0) if u < 0.5 else (W2 - W1)
    return ((p.x, p.y, 0.0), math.degrees(math.atan2(-v.x, v.y)))


mocap.apply(arin, kneel, start=F0, length=T(8) - F0, offset=(W0.x, W0.y, 0), facing=0.0, in_place=True, loop=True)
mocap.apply(arin, walk, start=T(8), length=T(14) - T(8), in_place=True, loop=True, speed=0.9, place=walk_place, blend=8)
# 14–43.4: kneels in the narrow aisle behind the counter, side-on to it (facing +X, along the aisle)
mocap.apply(arin, kneel, start=T(14), length=T(43.4) - T(14), offset=(CB.x, CB.y, 0), facing=-90.0, in_place=True,
            loop=True, blend=14)
# 43.4–80: stands on «تو کی هستی؟», paces two steps with the phone at his ear
mocap.apply(arin, pace, start=T(43.4), length=F1 - T(43.4) + 1, offset=(CB.x, CB.y, 0), facing=-90.0,
            in_place=False, src_from=2.0, speed=0.8, blend=24)
Q.ground(arin, F0, F1)
sc.frame_set(T(18))
eyes = arin.parts["Eyes"][0]


def eyes_at(f):
    sc.frame_set(f)
    dg = bpy.context.evaluated_depsgraph_get(); me = eyes.evaluated_get(dg).to_mesh()
    c = sum((eyes.matrix_world @ v.co for v in me.vertices), Vector()) / len(me.vertices)
    eyes.evaluated_get(dg).to_mesh_clear()
    return c


ek = eyes_at(T(18))
fwd = Vector((1, 0, 0)); up = Vector((0, 0, 1)); right = fwd.cross(up)
# bandaging (14–24): left hand held out palm-up, right hand works over it; disinfectant bottle, then gauze
work = ek + fwd * 0.38 - up * 0.42
A.hand(arin, "l", [(T(14.5), None), (T(15.5), work - right * 0.04), (T(23.5), work - right * 0.04), (T(24.5), None)], ease=10)
A.hand(arin, "r", [(T(14.5), None), (T(15.5), work + right * 0.12 + up * 0.08),
                   (T(17.0), work + right * 0.02 + up * 0.06), (T(18.5), work + right * 0.08 + up * 0.02),
                   (T(20.0), work - right * 0.02 - up * 0.04), (T(21.5), work + right * 0.06 + up * 0.03),
                   (T(23.5), work + right * 0.02), (T(24.5), None)], ease=10)
# rubs his eyes (27–29.5) then dials (29.5–34): right hand to the eyes, then phone held low in both hands
A.hand(arin, "r", [(T(26.8), None), (T(27.4), ek + fwd * 0.05 - up * 0.01), (T(29.2), ek + fwd * 0.05), (T(29.8), None)], ease=8)
dis_m = P.mat("MAT_Disinfectant", (0.85, 0.9, 0.95), rough=0.2, alpha=0.8)
bottle = P.cyl((0, 0, 0), (0, 0, 0.16), 0.03, dis_m, "PROP_DISINFECTANT_BOTTLE", 16)
bottle.location = work + right * 0.25 - up * 0.3
sc.frame_set(T(15.5))
A.carry(bottle, arin, "r", T(15.5), T(18.5))
gauze_m = P.mat("MAT_Gauze", (0.95, 0.95, 0.93), rough=0.95)
bandage = P.box((0, 0, 0), (0.085, 0.06, 0.03), gauze_m, "PROP_GAUZE_ON_PALM")
bandage.parent = arin.rig; bandage.parent_type = "BONE"; bandage.parent_bone = "hand_l"; bandage.location = (0, 0.05, 0)
bandage.scale = (0.01, 0.01, 0.01); bandage.keyframe_insert("scale", frame=T(19.5))
bandage.scale = (1, 1, 1); bandage.keyframe_insert("scale", frame=T(23.0))

# ---------------------------------------------------------------- the phone: screens per state, in his right hand
st = {k: os.path.join(TEX, f"sc005_{k}.png") for k in ("dial", "off", "ring", "call", "fail")}
phone.screen_call(st["dial"], label="نیکا", sub="در حال شماره‌گیری…")
phone.screen_call(st["off"], label="نیکا", sub="خاموش است")
phone.screen_call(st["ring"], label="شماره‌ی ناشناس", sub="تماس ورودی…")
phone.screen_call(st["call"], label="شماره‌ی ناشناس", sub="در حال مکالمه")
phone.screen_call(st["fail"], label="شماره‌ی ناشناس", sub="تماس برقرار نشد")
ph = phone.build(st["dial"], strength=0.6)
img = bpy.data.materials[ph["screen_mat"]].node_tree.nodes[ph["screen_tex"]].image
PHASES = [(T(29.5), "dial"), (T(32.0), "off"), (T(34.0), "ring"), (T(39.6), "call"), (T(62.0), "fail")]


def _screen(scene, *_):
    f = scene.frame_current
    k = "dial"
    for f0, name in PHASES:
        if f >= f0:
            k = name
    if img.filepath != st[k]:
        img.filepath = st[k]; img.reload()


bpy.app.handlers.frame_change_pre.append(_screen)
sc.frame_set(T(29.6))
hold = ek + fwd * 0.28 - up * 0.2
ph.location = hold; ph.rotation_mode = "QUATERNION"; ph.rotation_quaternion = (ek - hold).normalized().to_track_quat("Z", "Y")
A.hand(arin, "r", [(T(29.6), None), (T(30.2), hold + right * 0.03), (T(39.4), hold + right * 0.03), (T(40.0), None)], ease=6)
A.carry(ph, arin, "r", T(30.2), F1)
ph.hide_render = True; ph.keyframe_insert("hide_render", frame=F0)
ph.hide_render = False; ph.keyframe_insert("hide_render", frame=T(29.6))

# ---------------------------------------------------------------- face, lips, look
LS = lipsync.Voices(fps=FPS)
for who, name, t0 in LINES:
    if who == "arin":
        LS.add("arin", os.path.join(VOICE, name + ".wav"), start=t0)
A.face(arin, F0, F1, lambda f, t: dict(worry=(1.2 if f < T(40) else (1.7 if f > T(55) else 1.4)),
                                         talking=LS.level("arin", t)))
A.look(arin, T(8.5), T(13.5), lambda f: TV + Vector((0, 0, -0.2)), weight=0.5)          # a glance at the TV
A.look(arin, T(77.2), F1 - 2, lambda f: DOOR + Vector((0, 0, 1.2)), weight=0.75)       # the hits on the door

# ---------------------------------------------------------------- memory flash: a white corridor far from the set
FL = Vector((200.0, 0.0, 0.0))
white = P.mat("MAT_FlashWhite", (0.95, 0.96, 0.97), rough=0.8, emit=(1, 1, 1), strength=1.5)
P.plane(FL, (3, 30), white, name="FL_Floor")
for sx in (-1.5, 1.5):
    P.box(FL + Vector((sx, 0, 1.5)), (0.1, 30, 3), white, "FL_Wall")
import cast as C
kid = C.spawn("kian")
kid.rig.location = FL + Vector((0.15, 0, 0)); kid.rig.rotation_euler = (0, 0, math.radians(180))
small = C.spawn("kian")
small.rig.location = FL + Vector((-0.35, 0.1, 0)); small.rig.rotation_euler = (0, 0, math.radians(180)); small.rig.scale = (0.8, 0.8, 0.8)
idle = mocap.load(os.path.join(MOCAP, "breathing_idle.fbx"))
for ch in (kid, small):
    mocap.apply(ch, idle, start=T(23), length=T(28) - T(23), offset=tuple(ch.rig.location), facing=180.0, in_place=True, loop=True)
bpy.context.view_layer.update()
sc.frame_set(T(25))
grip = (kid.rig.matrix_world @ kid.rig.pose.bones["hand_r"].head + small.rig.matrix_world @ small.rig.pose.bones["hand_l"].head) / 2
A.hand(kid, "r", [(T(23), grip), (T(28), grip)], ease=1)
A.hand(small, "l", [(T(23), grip + Vector((0, 0.03, 0))), (T(28), grip + Vector((0, 0.03, 0)))], ease=1)

# ---------------------------------------------------------------- cameras
def cam(name, loc, tgt, lens, f0, dof=None, keys=None):
    cd = bpy.data.cameras.new(name); cd.lens = lens; cd.sensor_width = 36
    c = bpy.data.objects.new(name, cd); sc.collection.objects.link(c)
    c.location = loc
    c.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    if dof:
        cd.dof.use_dof = True; cd.dof.focus_distance = dof[0]; cd.dof.aperture_fstop = dof[1]
    if keys:
        for f, l, tg in keys:
            c.location = l; c.rotation_euler = (Vector(tg) - Vector(l)).to_track_quat("-Z", "Y").to_euler()
            c.keyframe_insert("location", frame=f); c.keyframe_insert("rotation_euler", frame=f)
    m = sc.timeline_markers.new(name, frame=f0); m.camera = c
    return c


outside = Vector((DOOR.x, DOOR.y - 1.6, 1.6))
cam("CAM5_S1_POV", outside, DOOR + Vector((0.4, 2.0, 1.2)), 24, SHOTS[0][0],
    keys=[(T(0), outside, DOOR + Vector((0.6, 3.0, 1.4))), (T(2.5), DOOR + Vector((0, 0.35, 1.62)), DOOR + Vector((1.4, 3.2, 1.3))),
          (T(4.0), DOOR + Vector((0.3, 1.0, 1.6)), DOOR + Vector((1.6, 0.6, 0.9))),
          (T(7.5), DOOR + Vector((0.5, 1.4, 1.6)), DOOR + Vector((0.4, 0.3, 0.9)))])
cam("CAM5_S2_TV", Vector((0.8, -1.0, 1.55)), TV + Vector((0, 0, -0.15)), 50, SHOTS[1][0], (3.8, 2.8))
cam("CAM5_S3_counter", CB + Vector((2.3, 0.15, 1.15)), Vector((ek.x + 0.2, ek.y, ek.z - 0.35)), 35, SHOTS[2][0], (2.2, 2.8))
cam("CAM5_S4_flash", grip + Vector((0.12, -0.42, 0.06)), grip, 50, SHOTS[3][0], (0.44, 1.6))     # the two hands only
cam("CAM5_S5_CU", ek + fwd * 0.6 + right * 0.15 - up * 0.02, ek - up * 0.04, 50, SHOTS[4][0], (0.62, 2.0))
cam("CAM5_S6_phone", hold + fwd * 0.22 + up * 0.08, hold, 50, SHOTS[5][0], (0.24, 2.8))
e7 = eyes_at(T(50))
cam("CAM5_S7_CU", e7 + fwd * 1.3 - right * 0.2, e7, 85, SHOTS[6][0], (1.3, 2.0),
    keys=[(SHOTS[6][0], e7 + fwd * 1.35 - right * 0.22, e7 - up * 0.03), (SHOTS[6][1], e7 + fwd * 0.75 - right * 0.12, e7 - up * 0.02)])
cam("CAM5_S8_med", Vector((-1.2, -0.6, 1.45)), Vector((CB.x + 0.3, CB.y, 1.3)), 35, SHOTS[7][0], (2.6, 4.0))

# ---------------------------------------------------------------- render (the flash shot gets a blown-out exposure)
sc.render.engine = "BLENDER_EEVEE"
sc.view_settings.view_transform = "AgX"; sc.view_settings.look = "AgX - Base Contrast"
ex = sc.view_settings
ex.exposure = 1.6; ex.keyframe_insert("exposure", frame=SHOTS[3][0] - 1)
ex.exposure = 3.2; ex.keyframe_insert("exposure", frame=SHOTS[3][0])
ex.keyframe_insert("exposure", frame=SHOTS[3][1])
ex.exposure = 1.6; ex.keyframe_insert("exposure", frame=SHOTS[3][1] + 1)
try:
    sc.eevee.use_raytracing = True
except Exception:
    pass
OUT = os.path.join(HERE, "out", "sc005"); os.makedirs(OUT, exist_ok=True)
sc.render.image_settings.file_format = "PNG"
if MODE == "layout":
    sc.eevee.taa_render_samples = 8
    sc.render.resolution_x, sc.render.resolution_y = 640, 360
    frames = os.environ.get("LAYOUT_FRAMES")
    picks = [int(x) for x in frames.split(",")] if frames else [(a + b) // 2 for a, b in SHOTS]
    for f in picks:
        sc.frame_set(f)
        mk = max((m for m in sc.timeline_markers if m.frame <= f and m.camera), key=lambda m: m.frame, default=None)
        if mk:
            sc.camera = mk.camera
        sc.render.filepath = os.path.join(OUT, f"layout_f{f:04d}.png")
        bpy.ops.render.render(write_still=True)
if MODE in ("preview", "final"):
    sc.frame_start = int(os.environ.get("PREV_START", F0)); sc.frame_end = int(os.environ.get("PREV_END", F1))
    if MODE == "preview":
        sc.eevee.use_raytracing = False
        sc.eevee.taa_render_samples = 6; sc.frame_step = 2
        sc.render.resolution_x, sc.render.resolution_y = 480, 270
        sc.render.filepath = os.path.join(OUT, "prev_")
    else:
        sc.eevee.taa_render_samples = 48
        sc.render.resolution_x, sc.render.resolution_y = 1280, 720
        sc.render.filepath = os.path.join(OUT, "f_")
    bpy.ops.render.render(animation=True)
