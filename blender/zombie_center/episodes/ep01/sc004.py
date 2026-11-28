"""EP01 · CH01_SC004 — EXT. SIDE STREET B — NIGHT · 22:46 · 45 s, continues SC003 without a cut.

    blender/cast/bpy.sh blender/zombie_center/episodes/ep01/sc004.py layout | preview | final

Builds SC003 first (same file, ZC_MODE=build) so every position carries over exactly, then continues:
 1  0–6    ECU 85: the Driver's nose moves along Arin's neck to his cheek
 2  6–14   CU 50: it lifts its head, tilts it, a low sound in the chest — and climbs off him
 3  14–19  wide 28 low from Arin: it stands, looks round, sprints away down the street after a barking dog
 4  19–30  top-down 35: Arin alone, shaking, breath fogging; «چرا... ولم کرد؟»
 5  30–34  insert 50 low: he crawls to the phone — a hand shoots out from under the parked car and grabs his ankle
 6  34–37  medium 35: he kicks free, scrambles back on his hands
 7  37–39  insert ECU 85: his LEFT palm comes down on a broken bottle; blood; «آخ —!»
 8  39–40  medium 35: he grabs the phone, gets up, runs
 9  40–45  wide 35 locked: the crawler drags after him, slows, stops in the light of the shop window, watching
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
MODE4 = sys.argv[-1] if sys.argv[-1] in ("layout", "preview", "final") else "layout"
os.environ["ZC_MODE"] = "build"
_ns = {"__file__": os.path.join(HERE, "sc003.py"), "__name__": "sc003"}
exec(compile(open(os.path.join(HERE, "sc003.py")).read(), "sc003.py", "exec"), _ns)
globals().update({k: v for k, v in _ns.items() if not k.startswith("__")})
import bpy, math
from mathutils import Vector

F3_END = F1
G0 = F3_END + 1                                   # SC004 starts on the next frame
U = lambda s: G0 + int(round(s * FPS))
G1 = U(45.0) - 1
for m in list(sc.timeline_markers):               # SC003's cameras are not used here
    sc.timeline_markers.remove(m)
sc.frame_start, sc.frame_end = G0, G1

# ---------------------------------------------------------------- the Driver: sniffs, recoils, climbs off, runs
zb_full = mocap.load(os.path.join(MOCAP, "zombie_biting.fbx"))
zid = mocap.load(os.path.join(MOCAP, "zombie_idle.fbx"))
face_dir = math.degrees(math.atan2(-body_dir.x, body_dir.y))
mocap.apply(drv, zbite, start=G0, length=U(10) - G0, offset=(chest_at.x, chest_at.y, 0.0), facing=face_dir,
            in_place=True, loop=True)
mocap.apply(drv, zb_full, start=U(10), length=U(14) - U(10), offset=(chest_at.x, chest_at.y, 0.0), facing=face_dir,
            in_place=True, src_from=4.6, speed=0.6, blend=10)                       # the getting-up part, slowed
mocap.apply(drv, zid, start=U(14), length=U(16) - U(14), offset=(chest_at.x + 0.6, chest_at.y, 0.0), facing=-90.0,
            in_place=True, loop=True, blend=8)
AWAY = [chest_at + Vector((0.6, 0, 0)), Vector((34.0, 22.6, 0)), Vector((44.0, 23.0, 0))]
fW, lenW = path_fn(AWAY, 6.4)
mocap.apply(drv, zrun, start=U(16), length=G1 - U(16) + 1, in_place=True, loop=True, speed=1.2,
            place=lambda j: (lambda p, h, d: ((p.x, p.y, 0.0), h))(*fW(j)), blend=4)
Q.ground_body(drv, G0, U(16) - 1)
Q.ground(drv, U(16), G1, keep_flight=True)
neck = a_head + Vector((0, 0, -0.05)) - body_dir * 0.12
cheek = a_head + Vector((0, 0, 0.04))
A.look(drv, G0 + 2, U(10), lambda f: neck.lerp(cheek, min(1.0, max(0.0, (f - G0) / (6 * FPS)))), weight=0.85)
A.look(drv, U(14), U(16), lambda f: Vector((36.0, 23.0, 1.0)), weight=0.7)            # hears the dog
A.face(drv, G0, G1, lambda f, t: dict(scream=(0.35 if U(7) <= f < U(9) else 0.0)))

# ---------------------------------------------------------------- Arin: rigid, shaking, crawls to the phone, ankle, glass, runs
lie2 = mocap.load(os.path.join(MOCAP, "laying_breathless.fbx"))
crawl = mocap.load(os.path.join(MOCAP, "crawling.fbx"))
push = mocap.load(os.path.join(MOCAP, "pushing.fbx"))
lie_face = math.degrees(math.atan2(-fall_dir.x, fall_dir.y))
mocap.apply(arin, lie2, start=G0, length=U(30) - G0, offset=(FALL_AT.x, FALL_AT.y, 0.0), facing=lie_face,
            in_place=True, loop=True, speed=1.6)                                    # fast shallow breathing = shaking
C_TO = SKID_TO - fall_dir * 0.75
fC, lenC = path_fn([Vector((a_pel.x, a_pel.y, 0)), Vector((C_TO.x, C_TO.y, 0))], 0.55)
mocap.apply(arin, crawl, start=U(30), length=U(34) - U(30), in_place=True, loop=True,
            place=lambda j: (lambda p, h, d: ((p.x, p.y, 0.0), h))(*fC(j)), blend=12)
mocap.apply(arin, push, start=U(34), length=U(39.2) - U(34), offset=(C_TO.x, C_TO.y, 0.0),
            facing=math.degrees(math.atan2(-fall_dir.x, fall_dir.y)) + 180, in_place=True, speed=0.95, blend=6)
RUN_TO = [C_TO + Vector((-0.4, -0.3, 0)), Vector((19.0, 18.8, 0)), Vector((15.6, 18.4, 0)), Vector((13.5, 17.2, 0))]
fR, lenR = path_fn(RUN_TO, 4.2)
mocap.apply(arin, run, start=U(39.2), length=G1 - U(39.2) + 1, in_place=True, loop=True, speed=1.3,
            place=lambda j: (lambda p, h, d: ((p.x, p.y, 0.0), h))(*fR(j)), blend=5)
Q.ground_body(arin, G0, U(39.2) - 1)
Q.ground(arin, U(39.2), G1)
footlock.lock(arin, U(39.2), G1, mode="plant")
LS4 = lipsync.Voices(fps=FPS)
LS4.add("arin", os.path.join(VOICE, "sc004_arin_04.wav"), start=(U(24) - 1) / FPS)
LS4.add("arin", os.path.join(VOICE, "sc004_arin_05.wav"), start=(U(37.6) - 1) / FPS)
A.face(arin, G0, G1, lambda f, t: dict(worry=(2.0 if f < U(19) else 1.6), talking=LS4.level("arin", t)))
A.look(arin, G0 + 4, U(14), lambda f: Vector((a_head.x, a_head.y, 0)) - body_dir * 1.0 + Vector((0, 0, 0)), weight=0.5)   # chin turned away

# ---------------------------------------------------------------- the phone: picked up in his right hand at 39.0 s
sc.frame_set(U(39.0))
A.carry(ph, arin, "r", U(39.0), G1)

# ---------------------------------------------------------------- the crawler (Z3) under the parked car
crawler = zc_cast.spawn("zc_z3_crawler")
zcr = mocap.load(os.path.join(MOCAP, "zombie_crawl.fbx"))
CAR = Vector(S["side_car"].location)
HIDE = Vector((CAR.x - 0.2, CAR.y - 0.2, 0.0))
sc.frame_set(U(33.0))
ankle = arin.rig.matrix_world @ arin.rig.pose.bones["foot_l"].head
out_dir = Vector(((ankle - HIDE).x, (ankle - HIDE).y, 0)).normalized()
GRAB_AT = ankle - out_dir * 0.75
fZ, lenZ = path_fn([HIDE, Vector((GRAB_AT.x, GRAB_AT.y, 0))], 1.6)
mocap.apply(crawler, zcr, start=G0, length=U(32.6) - G0, offset=tuple(HIDE), facing=math.degrees(math.atan2(-out_dir.x, out_dir.y)),
            in_place=True, loop=True, speed=0.05)                                   # waits under the car, barely moving
mocap.apply(crawler, zrun_c := mocap.load(os.path.join(MOCAP, "zombie_running_crawl.fbx")), start=U(32.6),
            length=U(34.5) - U(32.6), in_place=True, loop=True,
            place=lambda j: (lambda p, h, d: ((p.x, p.y, 0.0), h))(*fZ(j)), blend=3)
A.hand(crawler, "r", [(U(32.9), None), (U(33.2), ankle), (U(35.2), ankle), (U(35.6), None)], ease=3)
SHOP = Vector((20.0, 16.7, 0.0))
fS, lenS = path_fn([Vector((GRAB_AT.x, GRAB_AT.y, 0)), Vector((21.2, 19.0, 0)), SHOP], 0.65)
mocap.apply(crawler, zcr, start=U(35.6), length=G1 - U(35.6) + 1, in_place=True, loop=True, speed=1.1,
            place=lambda j: (lambda p, h, d: ((p.x, p.y, 0.0), h))(*fS(j)), blend=6)
Q.ground_body(crawler, G0, G1)
A.face(crawler, G0, G1, lambda f, t: dict())

# ---------------------------------------------------------------- the broken bottle + the cut
sc.frame_set(U(37.6))
palm = arin.rig.matrix_world @ arin.rig.pose.bones["hand_l"].head
green = P.glass("MAT_BottleGreen", tint=(0.25, 0.55, 0.3), rough=0.08)
neck_b = P.cyl((palm.x - 0.05, palm.y, 0.03), (palm.x + 0.08, palm.y + 0.02, 0.05), 0.016, green, "PROP_BOTTLE_BROKEN")
for k in range(7):
    sh = P.box((palm.x + 0.1 * math.cos(k), palm.y + 0.1 * math.sin(k * 1.7), 0.003), (0.03, 0.02, 0.004), green, "PROP_BOTTLE_shard")
    sh.rotation_euler.z = k
blood = P.mat("MAT_Blood", (0.35, 0.02, 0.02), rough=0.3)
cut = P.box((0, 0, 0), (0.045, 0.012, 0.002), blood, "FX_PALM_CUT")
cut.parent = arin.rig; cut.parent_type = "BONE"; cut.parent_bone = "hand_l"; cut.location = (0.0, 0.05, -0.012)
cut.hide_render = True; cut.keyframe_insert("hide_render", frame=G0)
cut.hide_render = False; cut.keyframe_insert("hide_render", frame=U(37.7))

# ---------------------------------------------------------------- cameras
EV4 = [G0, U(6), U(14), U(19), U(30), U(34), U(37), U(39), U(40), G1 + 1]
SHOTS4 = [(a, b - 1) for a, b in zip(EV4, EV4[1:])]
Z = Vector((0, 0, 1))


def side_of(a, b):                                  # horizontal direction perpendicular to a->b
    v = Vector(((b - a).x, (b - a).y, 0)).normalized()
    return v.cross(Z).normalized()


hd0 = head(drv, U(3)); ah = head(arin, U(3))
sd = side_of(ah, hd0)
mid = (hd0 + ah) / 2
c1 = mid + sd * 0.6 + Z * 1.0                      # above them: his nose along Arin's neck
cam("CAM4_S1_ECU", c1, mid, 85, SHOTS4[0][0], ((c1 - mid).length, 2.2))
hd1 = head(drv, U(10.5))
c2 = hd1 + sd * 1.7 + Z * 0.15
cam("CAM4_S2_CU", c2, hd1 - Z * 0.15, 50, SHOTS4[1][0], ((c2 - hd1).length, 2.4))
cam("CAM4_S3_wide", Vector((ah.x, ah.y, 0.12)) + sd * 0.7 - Vector(((30.0 - ah.x), 0, 0)).normalized() * 0.5,
    Vector((30.0, 22.6, 1.1)), 28, SHOTS4[2][0], (6.0, 5.6))                       # low beside his head, past it
cam("CAM4_S4_top", (a_head + a_pel) / 2 + Vector((0.15, 0.1, 2.8)), (a_head + a_pel) / 2, 35, SHOTS4[3][0], (2.6, 2.8))
cam("CAM4_S5_ins", ankle + Vector((0.2, -1.6, 0.35)), ankle + Vector((0.4, 0.4, 0.1)), 50, SHOTS4[4][0], (1.7, 2.8))
cam("CAM4_S6_med", C_TO + Vector((0.5, -3.2, 1.0)), C_TO + Vector((0.3, 0.6, 0.4)), 35, SHOTS4[5][0], (3.3, 4.0))
c7 = palm + Vector((-0.1, -0.35, 0.45))
cam("CAM4_S7_ECU", c7, palm, 85, SHOTS4[6][0], ((c7 - palm).length, 2.8))
a8 = head(arin, U(39.5))
cam("CAM4_S8_med", a8 + Vector((0.6, -3.0, -0.3)), a8 - Z * 0.4, 35, SHOTS4[7][0], (3.1, 4.0))
c9 = Vector((24.5, 21.0, 1.5))                     # locked wide over the crawler's whole path to the shop light
cam("CAM4_S9_wide", c9, Vector((20.8, 17.6, 0.2)), 28, SHOTS4[8][0], (5.0, 5.6))
print("CRAWLER head at 43 s", tuple(round(v, 2) for v in head(crawler, U(43.0))))

# ---------------------------------------------------------------- render
OUT4 = os.path.join(HERE, "out", "sc004"); os.makedirs(OUT4, exist_ok=True)
if MODE4 == "layout":
    sc.eevee.taa_render_samples = 8
    sc.render.resolution_x, sc.render.resolution_y = 640, 360
    frames = os.environ.get("LAYOUT_FRAMES")
    picks = [int(x) for x in frames.split(",")] if frames else [(a + b) // 2 for a, b in SHOTS4]
    for f in picks:
        sc.frame_set(f)
        mk = max((m for m in sc.timeline_markers if m.frame <= f and m.camera), key=lambda m: m.frame, default=None)
        if mk:
            sc.camera = mk.camera
        sc.render.filepath = os.path.join(OUT4, f"layout_f{f:04d}.png")
        bpy.ops.render.render(write_still=True)
if MODE4 in ("preview", "final"):
    sc.frame_start = int(os.environ.get("PREV_START", G0)); sc.frame_end = int(os.environ.get("PREV_END", G1))
    if MODE4 == "preview":
        sc.eevee.use_raytracing = False; sc.eevee.volumetric_samples = 16
        sc.eevee.taa_render_samples = 6; sc.frame_step = 2
        sc.render.resolution_x, sc.render.resolution_y = 480, 270
        sc.render.filepath = os.path.join(OUT4, "prev_")
    else:
        sc.eevee.taa_render_samples = int(os.environ.get("FINAL_SAMPLES", 32))
        sc.render.resolution_x, sc.render.resolution_y = 1280, 720
        sc.render.filepath = os.path.join(OUT4, "f_")
    bpy.ops.render.render(animation=True)
