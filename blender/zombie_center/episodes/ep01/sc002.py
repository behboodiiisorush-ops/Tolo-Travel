"""EP01 · CH01_SC002 — EXT. AVENUE, BEHIND THE FALLEN BUS — NIGHT · 22:42 · 66.8 s (scene frames 1081–2684)

    blender/cast/bpy.sh blender/zombie_center/episodes/ep01/sc002.py layout     # one still per shot
    blender/cast/bpy.sh blender/zombie_center/episodes/ep01/sc002.py preview    # every 2nd frame, 480x270
    blender/cast/bpy.sh blender/zombie_center/episodes/ep01/sc002.py final      # 1280x720 (PREV_START / PREV_END)

The phone screen plays a per-frame image sequence made by sc002_screen.py (Nika's video frames + player UI).
Shots (screenplay v1.0, timed to the real video length 34.5 s):
 1  1081–1248  medium 35 mm: Arin crawls round the bus end, kneels with his back to the bus roof, dims the phone
 2  1249–1497  POV 28 mm over the phone: the video plays — Nika's first line, first glance at the door (video 1–249)
 3  1498–1594  POV 50 mm, screen fills the frame: her wrist — veins, bracelet, cannula (video 250–346)
 4  1595–1678  POV 50 mm: «اونا می‌گن دارم خوب می‌شم... دروغ می‌گن.» (video 347–430)
 5  1679–1848  POV 50 mm: the Centre directions (video 431–600)
 6  1849–2012  POV 35 mm: the lock, she leans in, cut-off line, the screen goes black (video 601–716 + 48 black)
 7  2013–2228  CU 50 mm: Arin frozen; drags the scrubber back, replays the last second, pauses on her face
 8  2229–2420  wide 24 mm from behind Arin: far down the avenue the Driver has stopped; slowly turns his head to the glow
 9  2421–2684  CU 50 mm: «همه‌ی این سال‌ها... تو مُرده بودی.» — he swallows, eyes wet
"""
import bpy, sys, os, math
HERE = os.path.dirname(os.path.abspath(__file__))
ZC = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path[:0] = [ZC, os.path.join(ZC, "sets")]
import env_city, phone, zc_cast, mocap, motion_qc as Q, perform as A, lipsync
from mathutils import Vector

MODE = sys.argv[-1] if sys.argv[-1] in ("layout", "preview", "final", "debug") else "layout"
MOCAP = os.path.join(ZC, "..", "mocap")
VOICE = os.path.join(HERE, "audio", "voice")
FPS = 24
F0, F1 = 1081, 2684
SHOTS = [(1081, 1248), (1249, 1497), (1498, 1594), (1595, 1678), (1679, 1848), (1849, 2012),
         (2013, 2228), (2229, 2420), (2421, 2684)]
VIDEO_START = 1249                      # scene frame of video frame 1
ARIN_LINE = 2421 + 30                   # «همه‌ی این سال‌ها...»

sc = bpy.context.scene
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)
sc.render.fps = FPS
sc.frame_start, sc.frame_end = F0, F1
S = env_city.build()
bus = S["bus"]
bpy.context.view_layer.update()


def _verts(objs):
    dg = bpy.context.evaluated_depsgraph_get()
    for o in objs:
        if o.type != "MESH":
            continue
        ev = o.evaluated_get(dg); me = ev.to_mesh()
        for v in me.vertices:
            yield o.matrix_world @ v.co
        ev.to_mesh_clear()


bus.location.z -= min(p.z for p in _verts(bus.children_recursive))       # same grounding as SC001
bpy.context.view_layer.update()
bv = list(_verts(bus.children_recursive))
xmin, xmax = min(p.x for p in bv), max(p.x for p in bv)
roof_y = max(p.y for p in bv if p.z < 1.45)          # the roof leans out over the road: clear it up to head height
print("BUS x", round(xmin, 2), round(xmax, 2), "roof_y below 1.45 m", round(roof_y, 2))

# ---------------------------------------------------------------- Arin: crawls round the bus end, kneels against the roof
arin = zc_cast.spawn("zc_arin")
K = Vector((xmax - 1.4, roof_y + 0.22, 0.0))         # kneeling under the overhang, back to the bus, facing +Y
crawl = mocap.load(os.path.join(MOCAP, "crawling.fbx"))
kneel = mocap.load(os.path.join(MOCAP, "kneeling_idle.fbx"))
C0 = Vector((xmax + 0.35, roof_y + 0.55, 0.0))       # comes round the end of the bus
N_CRAWL = 80
CV = (K - C0) / N_CRAWL
heading = math.degrees(math.atan2(-CV.x, CV.y))      # facing: 0 = +Y, positive = towards -X


def crawl_place(j, flip=0.0):
    p = C0 + CV * j
    return ((p.x, p.y, 0.0), heading + flip)


mocap.apply(arin, crawl, start=F0, length=N_CRAWL, in_place=True, loop=True, place=crawl_place)
# check the crawl faces its direction of travel (head ahead of the pelvis); flip once if not
sc.frame_set(F0 + 40)
hd = arin.rig.matrix_world @ arin.rig.pose.bones["head"].head
pv = arin.rig.matrix_world @ arin.rig.pose.bones["pelvis"].head
if (hd - pv).dot(CV) < 0:
    mocap.apply(arin, crawl, start=F0, length=N_CRAWL, in_place=True, loop=True, place=lambda j: crawl_place(j, 180.0))
    print("CRAWL flipped")
mocap.apply(arin, kneel, start=F0 + N_CRAWL, length=F1 - F0 - N_CRAWL + 1, offset=tuple(K), facing=0.0,
            in_place=True, loop=True, blend=14)
sc.frame_set(F0 + 200)
hd = arin.rig.matrix_world @ arin.rig.pose.bones["head"].head
pv = arin.rig.matrix_world @ arin.rig.pose.bones["pelvis"].head
nose = arin.rig.matrix_world @ arin.rig.pose.bones["head"].tail
Q.ground(arin, F0, F1)

# ---------------------------------------------------------------- the phone, held in both hands in front of his chest
screen_dir = os.path.join(HERE, "out", "sc002_screen")
first = os.path.join(screen_dir, f"s_{F0:04d}.png")
if not os.path.exists(first):
    import subprocess
    subprocess.run([sys.executable,
                    os.path.join(HERE, "sc002_screen.py")], check=False)
if not os.path.exists(first):                                 # no screen frames yet: grey placeholder
    os.makedirs(screen_dir, exist_ok=True)
    phone.screen_off(first)
ph = phone.build(first, strength=0.55)
img = bpy.data.images[bpy.data.materials[ph["screen_mat"]].node_tree.nodes[ph["screen_tex"]].image.name]
# one screen image per frame, swapped by a frame-change handler (image sequences don't refresh on still renders)
def _screen(scene, *_):
    f = min(F1, max(F0, scene.frame_current))
    path = os.path.join(screen_dir, f"s_{f:04d}.png")
    if os.path.exists(path) and bpy.path.abspath(img.filepath) != path:
        img.filepath = path; img.reload()
bpy.app.handlers.frame_change_pre.append(_screen)

sc.frame_set(F0 + 200)
eyes = arin.parts["Eyes"][0]
dg = bpy.context.evaluated_depsgraph_get(); _e = eyes.evaluated_get(dg).to_mesh()
eyec = sum((eyes.matrix_world @ v.co for v in _e.vertices), Vector()) / len(_e.vertices)
eyes.evaluated_get(dg).to_mesh_clear()
head = arin.rig.matrix_world @ arin.rig.pose.bones["head"].head
fwd = Vector(((eyec - head).x, (eyec - head).y, 0)).normalized()
up = Vector((0, 0, 1)); right = fwd.cross(up).normalized()
print("DBG eyec", tuple(round(v, 2) for v in eyec), "head", tuple(round(v, 2) for v in head), "fwd", tuple(round(v, 2) for v in fwd),
      "K", tuple(round(v, 2) for v in K), "pelvis", tuple(round(v, 2) for v in arin.rig.matrix_world @ arin.rig.pose.bones["pelvis"].head))
HOLD = eyec + fwd * 0.25 - up * 0.22                          # low in front of his face, screen tilted to his eyes
q_face = (eyec - HOLD).normalized().to_track_quat("Z", "Y")
A.place(ph, F0, HOLD + Vector((0, 0, -0.5)), q_face)       # (in his jacket pocket during the crawl: hidden)
ph.hide_render = True; ph.keyframe_insert("hide_render", frame=F0)
ph.hide_render = False; ph.keyframe_insert("hide_render", frame=F0 + N_CRAWL + 18)
A.place(ph, F0 + N_CRAWL + 18, HOLD, q_face)
A.place(ph, F1, HOLD, q_face)
for side, s in (("l", -1), ("r", 1)):
    grip = HOLD + right * (0.085 * s) - up * 0.035 - (HOLD - eyec).normalized() * 0.01   # wrists at the phone's sides, a little below
    sh = arin.rig.matrix_world @ arin.rig.pose.bones[f"upperarm_{side}"].head
    elbow_aim = sh - up * 0.55 + right * (0.32 * s) - fwd * 0.05          # elbows down and a little out
    A.hand(arin, side, [(F0 + N_CRAWL, None), (F0 + N_CRAWL + 18, grip), (F1, grip)], ease=14, pole_at=elbow_aim)

# ---------------------------------------------------------------- the Driver (Z6): stopped far down the avenue
drv = zc_cast.spawn("zc_z6_driver")
idle = mocap.load(os.path.join(MOCAP, "breathing_idle.fbx"))
DP = Vector((K.x + 1.8, K.y + 30.0, 0.0))
mocap.apply(drv, idle, start=F0, length=F1 - F0 + 1, offset=tuple(DP), facing=200.0, in_place=True, loop=True)
Q.ground(drv, F0, F1)
A.look(drv, 2268, F1 - 10, lambda f: HOLD.lerp(DP + Vector((-6, 0, 1.6)), max(0.0, min(1.0, (2358 - f) / 90.0))), weight=0.8)
A.face(drv, F0, F1, lambda f, t: dict())

# ---------------------------------------------------------------- Arin's face + head
LS = lipsync.Voices(fps=FPS)
LS.add("arin", os.path.join(VOICE, "sc002_arin_02.wav"), start=(ARIN_LINE - 1) / FPS)


def arin_face(f, t):
    w = 1.3
    if f >= 1940:
        w = 1.7                          # the cut-off, the black screen: shock
    if f >= ARIN_LINE + 80:
        w = 1.5
    return dict(worry=w, talking=LS.level("arin", t))


A.face(arin, F0, F1, arin_face)
A.look(arin, F0 + N_CRAWL + 20, F1 - 5, lambda f: HOLD, weight=0.55)

# ---------------------------------------------------------------- cameras
def cam(name, loc, tgt, lens, f0, dof=None):
    cd = bpy.data.cameras.new(name); cd.lens = lens; cd.sensor_width = 36
    c = bpy.data.objects.new(name, cd); sc.collection.objects.link(c)
    c.location = loc
    c.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    if dof:
        cd.dof.use_dof = True; cd.dof.focus_distance = dof[0]; cd.dof.aperture_fstop = dof[1]
    m = sc.timeline_markers.new(name, frame=f0); m.camera = c
    return c


pov = eyec + fwd * 0.02
scr = HOLD + (eyec - HOLD).normalized() * 0.01
cam("CAM_S01_medium", K + fwd * 3.2 + right * 1.4 + up * 0.9, K + up * 0.55, 35, SHOTS[0][0], (3.4, 4.0))
cam("CAM_S02_POV", pov, scr - up * 0.03, 28, SHOTS[1][0], ((scr - pov).length, 2.8))
for i in (2, 3, 4):
    cam(f"CAM_S0{i + 1}_screen", scr + (pov - scr).normalized() * 0.2, scr, 50, SHOTS[i][0], (0.2, 5.6))
cam("CAM_S06_POV", pov, scr, 35, SHOTS[5][0], ((scr - pov).length, 2.8))
cam("CAM_S07_CU", eyec + fwd * 0.55 + right * 0.18 - up * 0.08, eyec - up * 0.04, 50, SHOTS[6][0], (0.57, 2.0))
# behind Arin's right shoulder: his head and the phone glow at frame left, the avenue and the Driver deep in frame
c8 = K + right * 0.55 - fwd * 0.12 + up * 1.15
cam("CAM_S08_wide", c8, (DP + up * 1.0).lerp(eyec, 0.04) + right * -0.9, 28, SHOTS[7][0], (30.0, 4.0))
# the Driver stands under a dying street lamp: a hard top light that makes him a silhouette with a lit outline
ld = bpy.data.lights.new("LAMP_Driver", "SPOT"); ld.energy = 900; ld.spot_size = math.radians(55); ld.color = (1.0, 0.72, 0.42)
lo = bpy.data.objects.new("LAMP_Driver", ld); sc.collection.objects.link(lo)
lo.location = DP + Vector((0.6, 1.8, 5.5)); lo.rotation_euler = (DP - lo.location).to_track_quat("-Z", "Y").to_euler()
cam("CAM_S09_CU", eyec + fwd * 0.5 - right * 0.16 - up * 0.06, eyec - up * 0.03, 50, SHOTS[8][0], (0.52, 2.0))

# ---------------------------------------------------------------- render
sc.render.engine = "BLENDER_EEVEE"
sc.view_settings.view_transform = "AgX"; sc.view_settings.look = "AgX - Base Contrast"; sc.view_settings.exposure = 2.0
try:
    sc.eevee.use_raytracing = True
except Exception:
    pass
OUT = os.path.join(HERE, "out", "sc002"); os.makedirs(OUT, exist_ok=True)
sc.render.image_settings.file_format = "PNG"
if MODE == "debug":       # third-person check of the kneel + phone hold
    sc.timeline_markers.clear(); f = int(os.environ.get("DBG_F", 1400)); sc.frame_set(f)
    print("DBG phone", tuple(round(v, 2) for v in ph.matrix_world.translation),
          "hand_l", tuple(round(v, 2) for v in arin.rig.matrix_world @ arin.rig.pose.bones["hand_l"].head))
    cd0 = bpy.data.cameras.new("DBG"); cd0.type = "ORTHO"; cd0.ortho_scale = 3.0
    c = bpy.data.objects.new("DBG", cd0); sc.collection.objects.link(c); sc.camera = c
    c.location = K + Vector((4.0, 0.3, 0.7)); c.rotation_euler = (math.radians(90), 0, math.radians(90))   # side view from +X
    if sc.world:
        for l in list(sc.world.node_tree.links):
            if l.to_socket.name == "Volume":
                sc.world.node_tree.links.remove(l)
    sl = bpy.data.lights.new("dbg_sun", "SUN"); sl.energy = 4; so = bpy.data.objects.new("dbg_sun", sl)
    so.rotation_euler = (math.radians(50), 0, math.radians(150)); sc.collection.objects.link(so)
    for o in bpy.data.objects:
        if o.name.startswith("FX_") or o.name.startswith("ENV_Building"):
            o.hide_render = True
    if sc.world:
        sc.world.node_tree.nodes["Background"].inputs["Strength"].default_value = 8.0
    sc.eevee.taa_render_samples = 4; sc.render.resolution_x, sc.render.resolution_y = 640, 360
    sc.render.filepath = os.path.join(OUT, "debug.png"); bpy.ops.render.render(write_still=True)
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
        sc.eevee.use_raytracing = False; sc.eevee.volumetric_samples = 16
        sc.eevee.taa_render_samples = 6; sc.frame_step = 2
        sc.render.resolution_x, sc.render.resolution_y = 480, 270
        sc.render.filepath = os.path.join(OUT, "prev_")
    else:
        sc.eevee.taa_render_samples = int(os.environ.get("FINAL_SAMPLES", 32))
        sc.render.resolution_x, sc.render.resolution_y = 1280, 720
        sc.render.filepath = os.path.join(OUT, "f_")
    bpy.ops.render.render(animation=True)
