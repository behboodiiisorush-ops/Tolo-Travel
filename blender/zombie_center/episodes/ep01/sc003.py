"""EP01 · CH01_SC003 — EXT. AVENUE → SIDE STREET B — NIGHT · 22:44 · the chase, in real time (33 s, frames 2685–3476)

    blender/cast/bpy.sh blender/zombie_center/episodes/ep01/sc003.py layout | preview | final

Geography (city set): Arin kneels behind the fallen bus (SC002 end). The Driver stood ~30 m up the avenue (+Y).
Arin runs for the mouth of side street B (+X at y = 22) — the Driver races for the same corner — bumps a parked car
(alarm), vaults a car that blocks the mouth of B, swerves round a toppled trolley, catches a fallen cable and goes down;
the Driver clears the same bonnet on all fours and drops onto him.
Real time (the screenplay's 65 s was an estimate; a real sprint over ~20 m takes seconds — no padded running).

 1  0.0– 3.0  CU 50: Arin's head snaps up at the footsteps
 2  3.0– 5.5  wide 24 from the bus: Arin bolts; the Driver sprinting down the avenue in deep background
 3  5.5– 8.0  POV 24 (head-mounted, damped): running between the cars to the corner
 4  8.0– 9.5  medium 35 side: he bumps the parked car — alarm lights, he staggers on
 5  9.5–11.2  medium 35: he vaults the car blocking side street B
 6 11.2–13.0  low 24: the Driver clears the same bonnet on all fours, toward the lens
 7 13.0–15.0  POV 24: side street, swerve round the trolley
 8 15.0–16.5  POV whip back over the shoulder: the Driver closing
 9 16.5–18.5  low 35 at foot level: the cable catches his boot; he goes down; the phone skids into the lens
10 18.5–23.0  top-down 28: he rolls onto his back; the Driver drops onto him
11 23.0–33.0  ECU 85 two-shot profile: faces a hand-width apart; «نه... نه!»; hold
"""
import bpy, sys, os, math
HERE = os.path.dirname(os.path.abspath(__file__))
ZC = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path[:0] = [ZC, os.path.join(ZC, "sets")]
import env_city, phone, zc_cast, mocap, motion_qc as Q, footlock, perform as A, lipsync
import props as P
from mathutils import Vector

MODE = sys.argv[-1] if sys.argv[-1] in ("layout", "preview", "final", "debug") else "layout"
MOCAP = os.path.join(ZC, "..", "mocap")
VOICE = os.path.join(HERE, "audio", "voice")
FPS = 24
F0 = 2685
T = lambda s: F0 + int(round(s * FPS))                 # scene seconds -> frame
F1 = T(33.0) - 1                                        # provisional; trimmed to the events below (PIN + hold)

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


bus.location.z -= min(p.z for p in _verts(bus.children_recursive))
bpy.context.view_layer.update()
bv = list(_verts(bus.children_recursive))
xmax = max(p.x for p in bv)
roof_y = max(p.y for p in bv if p.z < 1.45)
K = Vector((xmax - 1.4, roof_y + 0.22, 0.0))          # where SC002 left him kneeling

# ---------------------------------------------------------------- extra props for the chase
CAR_BUMP = Vector((7.3, 15.6, 0.0))
CAR_VAULT = Vector((12.6, 21.7, 0.0))
car_b = env_city.car(tuple(CAR_BUMP), 172, (0.32, 0.34, 0.36), "PROP_CAR_ALARM", damaged=True)
car_v = env_city.car(tuple(CAR_VAULT), 78, (0.42, 0.12, 0.1), "PROP_CAR_VAULT", damaged=True)
# alarm: indicator lamps blink amber while it wails (8.3–9.9 s), then die
amber = P.mat("MAT_AlarmBlink", (1.0, 0.6, 0.15), rough=0.3, emit=(1.0, 0.55, 0.1), strength=0.0)
for sx in (-0.8, 0.8):
    for sy in (-2.2, 2.2):
        b = P.box((0, 0, 0), (0.12, 0.05, 0.08), amber, "PROP_CAR_ALARM_blinker")
        b.location = (sx, sy, 0.72); b.parent = car_b
bs = amber.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
for i, f in enumerate(range(T(8.3), T(9.9), 6)):
    bs.default_value = 14.0 if i % 2 == 0 else 0.0; bs.keyframe_insert("default_value", frame=f)
bs.default_value = 0.0; bs.keyframe_insert("default_value", frame=T(9.9))
al = bpy.data.lights.new("LGT_Alarm", "POINT"); al.energy = 0; al.color = (1.0, 0.55, 0.1)
alo = bpy.data.objects.new("LGT_Alarm", al); sc.collection.objects.link(alo); alo.location = CAR_BUMP + Vector((0, 0, 1.3))
for i, f in enumerate(range(T(8.3), T(9.9), 6)):
    al.energy = 160 if i % 2 == 0 else 0; al.keyframe_insert("energy", frame=f)
al.energy = 0; al.keyframe_insert("energy", frame=T(9.9))
# toppled shopping trolley (plain metal, no logo)
steel = P.mat("MAT_Trolley", (0.6, 0.62, 0.62), rough=0.35, metal=0.9)
TROLLEY = Vector((17.6, 20.9, 0.0))
troot = P.empty("PROP_SHOPPING_TROLLEY", (0, 0, 0))
for (a, b) in (((-0.3, -0.45, 0.25), (0.3, -0.45, 0.25)), ((-0.3, 0.45, 0.25), (0.3, 0.45, 0.25)),
               ((-0.3, -0.45, 0.25), (-0.3, 0.45, 0.25)), ((0.3, -0.45, 0.25), (0.3, 0.45, 0.25)),
               ((-0.3, -0.45, 0.8), (0.3, -0.45, 0.8)), ((-0.3, 0.45, 0.8), (0.3, 0.45, 0.8)),
               ((-0.3, -0.45, 0.8), (-0.3, 0.45, 0.8)), ((0.3, -0.45, 0.8), (0.3, 0.45, 0.8)),
               ((-0.3, -0.45, 0.25), (-0.3, -0.45, 0.8)), ((0.3, -0.45, 0.25), (0.3, -0.45, 0.8)),
               ((-0.3, 0.45, 0.25), (-0.3, 0.45, 0.8)), ((0.3, 0.45, 0.25), (0.3, 0.45, 0.8)),
               ((-0.3, -0.45, 0.95), (0.3, -0.45, 0.95)), ((-0.3, -0.45, 0.8), (-0.3, -0.6, 0.95)),
               ((0.3, -0.45, 0.8), (0.3, -0.6, 0.95))):
    c = P.cyl(a, b, 0.008, steel, "PROP_TROLLEY_bar", 6); c.parent = troot
for k in range(1, 6):                                          # side mesh wires
    for x in (-0.3, 0.3):
        c = P.cyl((x, -0.45 + k * 0.15, 0.25), (x, -0.45 + k * 0.15, 0.8), 0.004, steel, "PROP_TROLLEY_wire", 4); c.parent = troot
for x in (-0.25, 0.25):
    for y in (-0.4, 0.4):
        c = P.cyl((x, y, 0.05), (x, y, 0.25), 0.01, steel, "PROP_TROLLEY_leg", 6); c.parent = troot
        w = P.cyl((x - 0.02, y, 0.05), (x + 0.02, y, 0.05), 0.05, P.mat("MAT_TrolleyWheel", (0.05, 0.05, 0.05), 0.7), "PROP_TROLLEY_wheel", 12)
        w.parent = troot
troot.location = TROLLEY + Vector((0, 0, 0.32)); troot.rotation_euler = (0, math.radians(88), math.radians(30))   # on its side
# fallen cable across the street (from a toppled pole at the kerb)
CABLE_X = 22.6
cab_m = P.mat("MAT_Cable", (0.02, 0.02, 0.02), rough=0.5)
pts = [Vector((CABLE_X + 0.3 * math.sin(i * 0.7), 18.6 + i * 0.5, 0.03 + 0.06 * max(0.0, 1 - abs(i - 7) / 3))) for i in range(15)]
for a, b in zip(pts, pts[1:]):
    P.cyl(a, b, 0.012, cab_m, "PROP_CABLE_FALLEN", 8)
pole = P.cyl((CABLE_X + 0.2, 18.2, 0.12), (CABLE_X - 3.2, 17.0, 1.0), 0.09, bpy.data.materials.get("MAT_Pole") or steel, "PROP_POLE_FALLEN", 12)

# side street B needs light where the action is: two more working lamps (cold LED, like the avenue)
env_city.street_lamp((CABLE_X + 1.0, 18.3, 0.15), True, "PROP_STREET_LAMP_B2")
env_city.street_lamp((CAR_VAULT.x - 1.5, 25.6, 0.15), True, "PROP_STREET_LAMP_B3")

# ---------------------------------------------------------------- path helper (arc length -> position, heading)
def path_fn(pts, speed):
    """pts: waypoints (Vector); speed m/s -> fn(j frames since start) -> (pos, heading_deg, done)"""
    segs = [(a, b, (b - a).length) for a, b in zip(pts, pts[1:])]
    total = sum(l for _, _, l in segs)

    def at(j):
        d = min(total, j * speed / FPS)
        for a, b, l in segs:
            if d <= l or (a, b, l) == segs[-1]:
                u = d / l if l else 0.0
                p = a.lerp(b, min(1.0, u)); v = b - a
                return p, math.degrees(math.atan2(-v.x, v.y)), d >= total
            d -= l
    return at, total


def frames_for(total, speed):
    return int(math.ceil(total / speed * FPS))


# ---------------------------------------------------------------- Arin
arin = zc_cast.spawn("zc_arin")
kneel = mocap.load(os.path.join(MOCAP, "kneeling_idle.fbx"))
run = mocap.load(os.path.join(MOCAP, "jog_in_circle.fbx"))
jump = mocap.load(os.path.join(MOCAP, "jump.fbx"))
fall = mocap.load(os.path.join(MOCAP, "falling_down.fbx"))
lie = mocap.load(os.path.join(MOCAP, "laying_breathless.fbx"))
BOLT = T(3.6)
mocap.apply(arin, kneel, start=F0, length=BOLT - F0, offset=tuple(K), facing=0.0, in_place=True, loop=True)
VA = 4.6                                                    # m/s: a panicked sprint off a kneel
legA = [K, K + Vector((1.4, 1.6, 0)), CAR_BUMP + Vector((-1.25, -0.4, 0)), CAR_BUMP + Vector((-1.1, 1.6, 0)),
        CAR_VAULT + Vector((-1.6, -0.35, 0))]
fA, lenA = path_fn(legA, VA); nA = frames_for(lenA, VA)
bump_j = frames_for((legA[1] - legA[0]).length + (legA[2] - legA[1]).length, VA)


def placeA(j):
    p, h, _ = fA(j)
    if abs(j - bump_j) < 10:                              # the bump: shoulder into the car, a lurch sideways
        k = 1 - abs(j - bump_j) / 10.0
        p = p + Vector((-0.18 * k, 0, 0)); h += 14 * k
    return ((p.x, p.y, 0.0), h)


mocap.apply(arin, run, start=BOLT, length=nA, in_place=True, loop=True, speed=1.35, place=placeA, blend=6)
V0 = BOLT + nA                                              # the vault: one hand on the bonnet, over in ~1.1 s
vault_from, vault_to = legA[-1], CAR_VAULT + Vector((1.8, 0.35, 0))
NV = 26


def placeV(j):
    u = j / (NV - 1)
    p = vault_from.lerp(vault_to, u)
    z = 0.62 * math.sin(math.pi * min(1.0, max(0.0, (u - 0.1) / 0.8)))
    v = vault_to - vault_from
    return ((p.x, p.y, z), math.degrees(math.atan2(-v.x, v.y)))


mocap.apply(arin, jump, start=V0, length=NV, in_place=True, place=placeV, src_from=0.45, speed=1.25, blend=4)
VB = 4.3
legB = [vault_to, TROLLEY + Vector((-1.3, 1.25, 0)), TROLLEY + Vector((0.6, 1.35, 0)), Vector((CABLE_X - 0.35, 21.9, 0))]
fB, lenB = path_fn(legB, VB); nB = frames_for(lenB, VB)
R0 = V0 + NV
mocap.apply(arin, run, start=R0, length=nB, in_place=True, loop=True, speed=1.3,
            place=lambda j: (lambda p, h, d: ((p.x, p.y, 0.0), h))(*fB(j)), blend=5)
FALL = R0 + nB                                              # catches the cable -> down, rolls onto his back
fall_dir = (legB[-1] - legB[-2]).normalized()
FALL_AT = legB[-1] + fall_dir * 0.2
NF = int(fall.seconds * FPS) - 4
mocap.apply(arin, fall, start=FALL, length=NF, offset=(FALL_AT.x, FALL_AT.y, 0.0),
            facing=math.degrees(math.atan2(-fall_dir.x, fall_dir.y)), in_place=True, blend=3)
LIE = FALL + NF
mocap.apply(arin, lie, start=LIE, length=F1 - LIE + 1, offset=(FALL_AT.x, FALL_AT.y, 0.0),
            facing=math.degrees(math.atan2(-fall_dir.x, fall_dir.y)), in_place=True, loop=True, blend=10)
Q.ground(arin, F0, F1, keep_flight=True)
footlock.lock(arin, BOLT, V0 - 1, mode="plant")
footlock.lock(arin, R0, FALL - 1, mode="plant")
print("ARIN bolt", BOLT, "vault", V0, "run2", R0, "fall", FALL, "lie", LIE, "end", F1)
# where is he lying? crouch over his chest, facing his head (measured on the body, not guessed)
sc.frame_set(LIE + 8)
a_head = arin.rig.matrix_world @ arin.rig.pose.bones["head"].head
a_pel = arin.rig.matrix_world @ arin.rig.pose.bones["pelvis"].head
body_dir = Vector(((a_head - a_pel).x, (a_head - a_pel).y, 0)).normalized()
chest_at = a_pel + body_dir * 0.15

# ---------------------------------------------------------------- the Driver (Z6, fresh: sprints)
drv = zc_cast.spawn("zc_z6_driver")
zrun = mocap.load(os.path.join(MOCAP, "zombie_run.fbx"))
zcrawl = mocap.load(os.path.join(MOCAP, "zombie_running_crawl.fbx"))
zbite = mocap.load(os.path.join(MOCAP, "zombie_biting_2.fbx"))
zidle = mocap.load(os.path.join(MOCAP, "breathing_idle.fbx"))
DP = Vector((K.x + 1.8, K.y + 30.0, 0.0))
VD = 6.2
legD = [DP, Vector((9.6, 26.0, 0)), CAR_VAULT + Vector((-1.4, 0.9, 0))]
fD, lenD = path_fn(legD, VD); nD = frames_for(lenD, VD)
D_ARRIVE = V0 + 30                                           # reaches the car ~1.25 s after Arin went over it
D_START = D_ARRIVE - nD
mocap.apply(drv, zidle, start=F0, length=D_START - F0, offset=tuple(DP), facing=200.0, in_place=True, loop=True)
mocap.apply(drv, zrun, start=D_START, length=nD, in_place=True, loop=True, speed=1.2,
            place=lambda j: (lambda p, h, d: ((p.x, p.y, 0.0), h))(*fD(j)), blend=4)
ND = 22                                                      # over the bonnet on hands and feet


def placeD(j):
    u = j / (ND - 1)
    a, b = legD[-1], CAR_VAULT + Vector((1.7, 0.2, 0))
    p = a.lerp(b, u); v = b - a
    return ((p.x, p.y, 0.85 * math.sin(math.pi * u)), math.degrees(math.atan2(-v.x, v.y)))


mocap.apply(drv, zcrawl, start=D_ARRIVE, length=ND, in_place=True, loop=True, place=placeD, blend=3)
legD2 = [CAR_VAULT + Vector((1.7, 0.2, 0)), TROLLEY + Vector((-1.2, 1.4, 0)), TROLLEY + Vector((0.7, 1.5, 0)),
         chest_at - body_dir * 0.9]
fD2, lenD2 = path_fn(legD2, VD); nD2 = frames_for(lenD2, VD)
D2 = D_ARRIVE + ND
mocap.apply(drv, zrun, start=D2, length=nD2, in_place=True, loop=True, speed=1.2,
            place=lambda j: (lambda p, h, d: ((p.x, p.y, 0.0), h))(*fD2(j)), blend=3)
PIN = max(D2 + nD2, LIE - 6)                                 # drops onto him: crouched over his chest
if PIN > D2 + nD2:
    mocap.apply(drv, zrun, start=D2 + nD2, length=PIN - (D2 + nD2), in_place=True, loop=True, speed=0.6,
                place=lambda j: ((legD2[-1].x, legD2[-1].y, 0.0), math.degrees(math.atan2(-fall_dir.x, fall_dir.y))), blend=3)
mocap.apply(drv, zbite, start=PIN, length=F1 - PIN + 1, offset=(chest_at.x, chest_at.y, 0.0),
            facing=math.degrees(math.atan2(-body_dir.x, body_dir.y)), in_place=True, loop=True, blend=8)
print("LYING head", tuple(round(v, 2) for v in a_head), "pelvis", tuple(round(v, 2) for v in a_pel))
Q.ground(drv, F0, F1, keep_flight=True)
footlock.lock(drv, D_START, D_ARRIVE - 1, mode="plant")
print("DRIVER start", D_START, "bonnet", D_ARRIVE, "pin", PIN)

# ---------------------------------------------------------------- the phone skids into the lens
ph = phone.build(phone.screen_off(os.path.join(HERE, "tex", "off.png")))
SKID_TO = FALL_AT + fall_dir * 2.6 + Vector((0, 0.25, 0))
ph.rotation_mode = "XYZ"
ph.hide_render = True; ph.keyframe_insert("hide_render", frame=F0)
ph.hide_render = False; ph.keyframe_insert("hide_render", frame=FALL + 6)
for f, p, rz in ((FALL + 6, FALL_AT + fall_dir * 0.5, 0.0), (FALL + 16, FALL_AT + fall_dir * 1.8, 2.2),
                 (FALL + 30, SKID_TO, 3.1)):
    ph.location = (p.x, p.y, 0.006); ph.rotation_euler = (0, 0, rz)
    ph.keyframe_insert("location", frame=f); ph.keyframe_insert("rotation_euler", frame=f)

# ---------------------------------------------------------------- faces and looks
LS = lipsync.Voices(fps=FPS)
LS.add("arin", os.path.join(VOICE, "sc003_arin_03.wav"), start=(PIN + 64 - 1) / FPS)
A.face(arin, F0, F1, lambda f, t: dict(worry=(1.4 if f < BOLT else 1.9), talking=LS.level("arin", t)))
A.face(drv, F0, PIN + 40 + 8 * FPS, lambda f, t: dict(scream=(0.6 if PIN <= f < PIN + 60 else 0.0)))
A.look(arin, F0 + 6, BOLT + 10, lambda f: DP + Vector((0, 0, 1.6)), weight=0.6)


def head(ch, f):
    sc.frame_set(f)
    return ch.rig.matrix_world @ ch.rig.pose.bones["head"].head


# ---------------------------------------------------------------- cameras
def cam(name, loc, tgt, lens, f0, dof=None, keys=None):
    cd = bpy.data.cameras.new(name); cd.lens = lens; cd.sensor_width = 36
    c = bpy.data.objects.new(name, cd); sc.collection.objects.link(c)
    c.location = loc
    c.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    if dof:
        cd.dof.use_dof = True; cd.dof.focus_distance = dof[0]; cd.dof.aperture_fstop = dof[1]
    if keys:                                                  # moving camera: [(frame, loc, target)]
        for f, l, tg in keys:
            c.location = l; c.rotation_euler = (Vector(tg) - Vector(l)).to_track_quat("-Z", "Y").to_euler()
            c.keyframe_insert("location", frame=f); c.keyframe_insert("rotation_euler", frame=f)
    m = sc.timeline_markers.new(name, frame=f0); m.camera = c
    return c


BUMP = BOLT + bump_j
HOLD = 8 * FPS                                          # the face-to-face hold after the pin
F1 = PIN + 40 + HOLD
sc.frame_end = F1
NO_LINE_F = PIN + 64
EV = [F0, BOLT - 6, BOLT + 30, BUMP - 12, V0 - 4, V0 + NV + 6, D_ARRIVE + ND + 4, FALL - 34, FALL - 12, FALL + 40, PIN + 40, F1 + 1]
SHOTS = [(a, b - 1) for a, b in zip(EV, EV[1:])]
print("SHOTS", SHOTS)


def eyes_at(ch, f):
    sc.frame_set(f)
    e = ch.parts["Eyes"][0]
    dg = bpy.context.evaluated_depsgraph_get(); me = e.evaluated_get(dg).to_mesh()
    c = sum((e.matrix_world @ v.co for v in me.vertices), Vector()) / len(me.vertices)
    e.evaluated_get(dg).to_mesh_clear()
    return c


def pov(fn, f0, f1, first, look_fn):
    keys = []
    for f in range(f0, f1 + 2, 3):
        ec = eyes_at(arin, f); tg = look_fn(f)
        d = (tg - ec).normalized()
        keys.append((f, ec + d * 0.16 + Vector((0, 0, 0.02)), tg))   # just in front of the eyes: no hair, no head
    return keys


hk = head(arin, (SHOTS[0][0] + SHOTS[0][1]) // 2)
cam("CAM_S01_CU", hk + Vector((0.35, 0.45, 0.02)), hk, 50, SHOTS[0][0], (0.57, 2.2))
cam("CAM_S02_wide", K + Vector((-2.6, -1.2, 0.9)), K + Vector((3.0, 9.0, 1.0)), 24, SHOTS[1][0], (6.0, 5.6))
k3 = pov(fA, SHOTS[2][0], SHOTS[2][1], BOLT, lambda f: (lambda p: Vector((p[0].x, p[0].y, 1.35)))(fA(max(0, f - BOLT + 14))))
cam("CAM_S03_POV", k3[0][1], k3[0][2], 24, SHOTS[2][0], keys=k3)
cam("CAM_S04_side", CAR_BUMP + Vector((-4.2, -0.8, 1.1)), CAR_BUMP + Vector((-0.9, 0.3, 1.0)), 35, SHOTS[3][0], (3.4, 4.0))
cam("CAM_S05_vault", CAR_VAULT + Vector((0.4, -4.4, 1.0)), CAR_VAULT + Vector((0.0, 0.2, 0.9)), 35, SHOTS[4][0], (4.4, 4.0))
cam("CAM_S06_low", CAR_VAULT + Vector((3.2, 0.9, 0.35)), CAR_VAULT + Vector((0, 0.4, 1.0)), 24, SHOTS[5][0], (3.2, 4.0))
k7 = pov(fB, SHOTS[6][0], SHOTS[6][1], R0, lambda f: (lambda p: Vector((p[0].x, p[0].y, 1.3)))(fB(max(0, f - R0 + 14))))
cam("CAM_S07_POV", k7[0][1], k7[0][2], 24, SHOTS[6][0], keys=k7)
k8 = pov(fB, SHOTS[7][0], SHOTS[7][1], R0, lambda f: head(drv, f))
cam("CAM_S08_back", k8[0][1], k8[0][2], 24, SHOTS[7][0], keys=k8)
cam("CAM_S09_low", SKID_TO + fall_dir * 0.5 + Vector((0, 0, 0.15)), FALL_AT - fall_dir * 0.6 + Vector((0, 0, 0.45)), 35, SHOTS[8][0], (2.6, 2.8))
cam("CAM_S10_top", FALL_AT + fall_dir * 0.5 + Vector((0.4, 0.3, 4.4)), FALL_AT + fall_dir * 0.5, 28, SHOTS[9][0], (4.3, 4.0))
hf = head(arin, PIN + 90); hz = head(drv, PIN + 90)
mid = (hf + hz) / 2
side = (hz - hf).cross(Vector((0, 0, 1))).normalized()
cam("CAM_S11_ECU", mid + side * 0.8 + Vector((0, 0, 0.05)), mid, 85, SHOTS[10][0], (0.8, 2.0))

# ---------------------------------------------------------------- render
sc.render.engine = "BLENDER_EEVEE"
sc.view_settings.view_transform = "AgX"; sc.view_settings.look = "AgX - Base Contrast"; sc.view_settings.exposure = 2.0
try:
    sc.eevee.use_raytracing = True
except Exception:
    pass
OUT = os.path.join(HERE, "out", "sc003"); os.makedirs(OUT, exist_ok=True)
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
        sc.eevee.use_raytracing = False; sc.eevee.volumetric_samples = 16
        sc.eevee.taa_render_samples = 6; sc.frame_step = 2
        sc.render.resolution_x, sc.render.resolution_y = 480, 270
        sc.render.filepath = os.path.join(OUT, "prev_")
    else:
        sc.eevee.taa_render_samples = 48
        sc.render.resolution_x, sc.render.resolution_y = 1280, 720
        sc.render.filepath = os.path.join(OUT, "f_")
    bpy.ops.render.render(animation=True)
