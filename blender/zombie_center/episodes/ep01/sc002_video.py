"""EP01 · CH01_SC002 — the video on Arin's phone: Nika films herself in the white room (rendered separately,
540x960 vertical, then mapped onto the phone screen in the SC002 shots and shown full-frame in shots 2–6).

    blender/cast/bpy.sh blender/zombie_center/episodes/ep01/sc002_video.py layout    # 4 stills
    blender/cast/bpy.sh blender/zombie_center/episodes/ep01/sc002_video.py preview   # every 2nd frame, 270x480
    blender/cast/bpy.sh blender/zombie_center/episodes/ep01/sc002_video.py final     # 540x960 (use PREV_START/PREV_END)

Video timeline (24 fps, video frame 1 = 0.0 s) — voices are the ElevenLabs takes in ../audio/voice:
   14– 302  N1 «آرین... اگه اینو می‌بینی ... همه‌ی این سال‌ها زنده بودم.»  (brave smile on «زنده‌م»)
  312– 345  first glance at the door
  346– 442  pushes her sleeve back and turns the LEFT wrist to the lens: dark veins, red-thread bracelet, cannula
  451– 509  N2 «اونا می‌گن دارم خوب می‌شم... دروغ می‌گن.»   (chin trembles)
  535– 705  N3 «مرکز... زیر تپه، آخر جاده‌ی معدن. بیا دنبالم. خواهش می‌کنم.»
  720       a lock clacks outside — she snaps round to the door (720–758), wide eyes
  750– 763  leans in very close to the lens
  763– 828  N4 «به هیچ‌کس اعتماد نکن... حتی به —»   -> the video cuts to black at 828 (length 00:34)
"""
import bpy, sys, os, math, random
HERE = os.path.dirname(os.path.abspath(__file__))
ZC = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path[:0] = [ZC, os.path.join(ZC, "sets")]
import nika_room, zc_cast, zc_look, mocap, perform as A, lipsync
import props as P
from mathutils import Vector, Matrix

MODE = sys.argv[-1] if sys.argv[-1] in ("layout", "preview", "final") else "layout"
MOCAP = os.path.join(ZC, "..", "mocap")
VOICE = os.path.join(HERE, "audio", "voice")
FPS = 24
N_FR = 828
LINES = [("sc002_nika_01", 14), ("sc002_nika_02", 451), ("sc002_nika_03", 535), ("sc002_nika_04", 763)]

sc = bpy.context.scene
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)
sc.render.fps = FPS
sc.frame_start, sc.frame_end = 1, N_FR
R = nika_room.build()

# ---------------------------------------------------------------- Nika on the edge of the bed, facing the lens (-Y)
nika = zc_cast.spawn("zc_nika")
zc_look.veins(nika, "l")
for o in nika.parts["Eyes"]:            # the white room is bright all round: a glossy eye mirrors it and the iris
    for ms in o.material_slots:         # washes out to grey -> keep only a soft highlight
        b = ms.material.node_tree.nodes.get("Principled BSDF")
        b.inputs["Specular IOR Level"].default_value = 0.12; b.inputs["Roughness"].default_value = 0.35
sit = mocap.load(os.path.join(MOCAP, "sitting_idle.fbx"))
SEAT = Vector(R["bed_seat"])
mocap.apply(nika, sit, start=1, length=N_FR, offset=(SEAT.x, SEAT.y, 0), facing=180, in_place=True, loop=True)
# sit ON the mattress: lift the rig so the lowest point of the thighs/buttocks rests on the mattress top
sc.frame_set(1)
dg = bpy.context.evaluated_depsgraph_get()
ev = nika.body.evaluated_get(dg); me = ev.to_mesh()
pel = nika.rig.matrix_world @ nika.rig.pose.bones["pelvis"].head
seat_z = min((nika.body.matrix_world @ v.co).z for v in me.vertices
             if abs((nika.body.matrix_world @ v.co).x - pel.x) < 0.16 and abs((nika.body.matrix_world @ v.co).y - pel.y) < 0.16)
ev.to_mesh_clear()
lift = SEAT.z - seat_z + 0.005
nika.rig.location.z += lift
for f in range(1, N_FR + 1, 24):
    nika.rig.keyframe_insert("location", index=2, frame=f)
print("NIKA seat lift", round(lift, 3))

# ---- red-thread bracelet + cannula on the LEFT hand (made in the rest pose, parented to the bones)
rig = nika.rig
rig.data.pose_position = "REST"; bpy.context.view_layer.update()
B = lambda n: rig.data.bones[n]
W = lambda v: rig.matrix_world @ v
wrist = W(B("lowerarm_l").tail_local); elbow = W(B("lowerarm_l").head_local)
fdir = (W(B("middle_01_l").head_local) - wrist).normalized()
tdir = (W(B("thumb_01_l").head_local) - wrist).normalized()
back = -(fdir.cross(tdir)).normalized()                       # back of the LEFT hand (palm-down rest: thumb fwd)
adir = (elbow - wrist).normalized()


def bone_parent(o, bone):
    """parent o to a bone keeping its rest-pose world placement (uses the REST bone matrix, not the pose)."""
    bm = rig.matrix_world @ B(bone).matrix_local @ Matrix.Translation((0, B(bone).length, 0))
    mw = o.matrix_world.copy()
    o.parent = rig; o.parent_type = "BONE"; o.parent_bone = bone
    o.matrix_parent_inverse = bm.inverted()
    o.matrix_basis = mw


red = P.mat("MAT_RedThread", (0.55, 0.04, 0.04), rough=0.8)
for k, (off, r) in enumerate(((0.02, 0.0215), (0.028, 0.0225))):
    bpy.ops.mesh.primitive_torus_add(major_radius=r, minor_radius=0.0012, major_segments=48, minor_segments=6,
                                     location=wrist + adir * off)
    t = bpy.context.object; t.name = f"PROP_BRACELET_RED_THREAD_{k}"
    t.rotation_euler = adir.to_track_quat("Z", "Y").to_euler()
    t.data.materials.append(red)
    bpy.context.view_layer.update()
    bone_parent(t, "lowerarm_l")
tape = P.mat("MAT_Tape", (0.92, 0.9, 0.85), rough=0.7)
hmid = wrist + fdir * 0.045
cn = P.box(hmid + back * 0.014, (0.028, 0.02, 0.003), tape, "PROP_CANNULA_tape")
cn.rotation_euler = back.to_track_quat("Z", "Y").to_euler()
tube = P.cyl(hmid + back * 0.017 - fdir * 0.01, hmid + back * 0.02 - fdir * 0.05, 0.0022,
             P.mat("MAT_Tube", (0.85, 0.9, 0.92), rough=0.2, alpha=0.7), "PROP_CANNULA_tube")
for o in (cn, tube):
    bpy.context.view_layer.update()
    bone_parent(o, "hand_l")
rig.data.pose_position = "POSE"; bpy.context.view_layer.update()

# ---------------------------------------------------------------- the selfie camera (= her phone, in her right hand)
sc.frame_set(100)
head = rig.matrix_world @ rig.pose.bones["head"].head
eyes = nika.parts["Eyes"][0]
dg = bpy.context.evaluated_depsgraph_get(); _e = eyes.evaluated_get(dg).to_mesh()
eyec = sum((eyes.matrix_world @ v.co for v in _e.vertices), Vector()) / len(_e.vertices)
eyes.evaluated_get(dg).to_mesh_clear()
fwd = Vector((0, -1, 0)); right = Vector((-1, 0, 0)); up = Vector((0, 0, 1))      # her right is -X (she faces -Y)
rnd = random.Random(2)


def shake(f, amp):
    """smooth hand-held wobble: sum of slow sines with random phases."""
    return sum(math.sin(f * w + p) * a for w, p, a in ((0.07, rnd.random() * 6, 1.0), (0.19, rnd.random() * 6, 0.45),
                                                       (0.41, rnd.random() * 6, 0.2))) * amp


cd = bpy.data.cameras.new("CAM_SELFIE"); cd.lens = 22; cd.sensor_width = 36; cd.sensor_fit = "VERTICAL"
cam = bpy.data.objects.new("CAM_SELFIE", cd); sc.collection.objects.link(cam); sc.camera = cam
cd.dof.use_dof = True; cd.dof.aperture_fstop = 11.0     # a phone lens: almost everything sharp
ph_shake = [random.Random(9).random() * 6 for _ in range(6)]


def cam_pos(f):
    d = 0.46
    if f >= 750:                                   # leans in to the lens
        d = 0.46 - 0.17 * min(1.0, (f - 750) / 13.0)
    if 346 <= f <= 442:                            # holds the phone a bit further to fit the wrist in
        d += 0.06 * math.sin(math.pi * (f - 346) / 96)
    return eyec + fwd * d + up * 0.07 + right * 0.06


cam.rotation_mode = "XYZ"
for f in range(1, N_FR + 1):
    p = cam_pos(f)
    j = Vector((shake(f, 0.004), shake(f + 50, 0.003), shake(f + 90, 0.004)))
    cam.location = p + j
    look = (eyec + up * 0.01) - cam.location
    e = look.to_track_quat("-Z", "Y").to_euler()
    e.x += math.radians(shake(f + 30, 0.6)); e.y += math.radians(shake(f + 70, 1.2)); e.z += math.radians(shake(f + 10, 0.6))
    cam.rotation_euler = e
    cam.keyframe_insert("location", frame=f); cam.keyframe_insert("rotation_euler", frame=f)
    cd.dof.focus_distance = (cam.location - eyec).length
    cd.dof.keyframe_insert("focus_distance", frame=f)

# right hand holds the phone: just below/behind the lens (the forearm enters the corner of the frame)
A.hand(nika, "r", [(1, cam_pos(1) - up * 0.05 + fwd * 0.03)] +
       [(f, cam_pos(f) - up * 0.09 + fwd * 0.03 + right * 0.04) for f in range(12, N_FR + 1, 12)], ease=1, pole_offset=(0.0, -0.3, -0.4))
# left wrist turned to the lens (346–442): hand rises in front of the chest, fingers up, inner wrist to camera
WR = lambda f: cam_pos(f) - fwd * 0.2 - up * 0.11 + right * 0.03     # forearm across the frame below her chin
A.hand(nika, "l", [(330, None), (356, WR(356)), (432, WR(432)), (450, None)], ease=10)
A.aim_hand(nika, "l", 358, 430, WR(390) + right * 0.5 + up * 0.05, ease=8, palm_to=cam_pos(390))   # fingers to her right: inner wrist up
# head: on the lens, two glances at the door
door = Vector(R["door"])


def look_target(f):
    def win(a, b, e=6):
        if f < a - e or f > b + e:
            return 0.0
        if f < a:
            return (f - (a - e)) / e
        if f > b:
            return 1 - (f - b) / e
        return 1.0
    w = max(win(312, 340), win(722, 756, 4))
    if 356 <= f <= 432:
        return cam_pos(f).lerp(WR(f), 0.5)            # glances down at her own wrist while showing it
    return cam_pos(f).lerp(door, w)


A.look(nika, 2, N_FR - 1, look_target, weight=0.75)
# face: lips from the real voice, fear levels per beat
LS = lipsync.Voices(fps=FPS)
for name, f0 in LINES:
    LS.add("nika", os.path.join(VOICE, name + ".wav"), start=(f0 - 1) / FPS)


def face_state(f, t):
    w = 1.25
    smile = 0.0
    if 160 <= f <= 225:
        smile = 0.35                                   # brave smile on «من زنده‌م»
    if 451 <= f <= 520:
        w = 1.6                                        # chin trembles on «دروغ می‌گن»
    if f >= 720:
        w = 1.9                                        # the lock: wide-eyed
    return dict(worry=w, smile=smile, talking=LS.level("nika", t))


A.face(nika, 1, N_FR, face_state)

# ---------------------------------------------------------------- render
sc.render.engine = "BLENDER_EEVEE"
sc.view_settings.view_transform = "AgX"; sc.view_settings.look = "AgX - Base Contrast"; sc.view_settings.exposure = 0.6
sc.render.resolution_x, sc.render.resolution_y = 540, 960
OUT = os.path.join(HERE, "out", "sc002_video"); os.makedirs(OUT, exist_ok=True)
sc.render.image_settings.file_format = "PNG"
if MODE == "layout":
    sc.eevee.taa_render_samples = 12
    for f in [int(x) for x in os.environ.get("LAYOUT_FRAMES", "150,400,600,760").split(",")]:
        sc.frame_set(f); sc.render.filepath = os.path.join(OUT, f"layout_f{f:04d}.png")
        bpy.ops.render.render(write_still=True)
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "sc002_video.blend"))
if MODE in ("preview", "final"):
    sc.frame_start = int(os.environ.get("PREV_START", 1)); sc.frame_end = int(os.environ.get("PREV_END", N_FR))
    if MODE == "preview":
        sc.render.resolution_x, sc.render.resolution_y = 270, 480
        sc.frame_step = 2; sc.eevee.taa_render_samples = 6
        sc.render.filepath = os.path.join(OUT, "prev_")
    else:
        sc.eevee.taa_render_samples = 24
        sc.render.filepath = os.path.join(OUT, "f_")
    bpy.ops.render.render(animation=True)
