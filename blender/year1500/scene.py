"""«سال ۱۵۰۰» — a new city, ruined and empty. Two brothers wake up alone under the broken glass vault; a big
screen crackles on and shows mom with little Kian; Kian cries; they set off to look for life.
Comic look (EEVEE cel shading + ink, blender/studio/toon_look.py) on the cartoon cast, Mixamo motion.

    ../cast/bpy.sh scene.py --still 40,120,...      -> test/s_XXXX.png
    ../cast/bpy.sh scene.py --save                  -> year1500.blend (render.py renders from it)
Shots (seconds):
  1   0.0- 6.0  aerial drift over the ruined city (title)
  2   6.0- 9.5  low angle: two bodies on the floor of the arcade
  3   9.5-17.0  FLASHBACK, my eyes: walking with mom and Kian through the crowded new city
  4  17.0-20.6  the fall: screens glitch, lights die, people cower and drop, white flash
  5  20.6-22.0  black
  6  22.0-28.0  Kian wakes up, then me
  7  28.0-33.0  standing, looking around; camera tilts up at the broken vault and the ivy
  8  33.0-37.0  the big screen crackles on
  9  37.0-45.0  mom and little Kian on the screen
  10 45.0-51.0  close on Kian: a tear
  11 51.0-56.0  'we'll look ourselves'
  12 56.0-66.0  they walk off down the street under the broken glass
  13 66.0-72.0  the camera rises: two people in the whole city
"""
import bpy, sys, os, math, random
from mathutils import Vector, Matrix
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "cast"))
sys.path.insert(0, os.path.join(HERE, "..", "studio"))
sys.path.insert(0, HERE)                  # (studio/ has its own captions.py)
bpy.ops.wm.read_factory_settings(use_empty=True)
import cast, mocap, anim  # noqa: E402
import props as P         # noqa: E402
import toon_look as T     # noqa: E402
import city               # noqa: E402
from captions import LINES, END, speaking, FLASHBACK  # noqa: E402

cast.STYLE = cast.CARTOON
FPS = 24
N = int(END * FPS)
sc = bpy.context.scene
sc.render.fps = FPS
sc.frame_start, sc.frame_end = 1, N
MOC = os.path.join(HERE, "..", "mocap")
SCR = os.path.join(HERE, "screen")
FB0, FB1 = FLASHBACK
FALL = 17.0


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
        f = max(1, fr(t)) if t > 0 else 1
        o.hide_render = not v
        o.keyframe_insert("hide_render", frame=f)
    for fc in fcurves_of(o):
        if fc.data_path == "hide_render":
            for k in fc.keyframe_points:
                k.interpolation = "CONSTANT"


# ------------------------------------------------------------------ the screen material (image sequence)
scr_m = bpy.data.materials.new("Big screen")
scr_m.use_nodes = True
nt = scr_m.node_tree
nt.nodes.clear()
o_ = nt.nodes.new("ShaderNodeOutputMaterial")
e_ = nt.nodes.new("ShaderNodeEmission")
tx = nt.nodes.new("ShaderNodeTexImage")
first = os.path.join(SCR, "s_0001.png")
if os.path.exists(first):
    img = bpy.data.images.load(first)
    img.source = "SEQUENCE"
    tx.image = img
    tx.image_user.frame_duration = N
    tx.image_user.frame_start = 1
    tx.image_user.frame_offset = 0
    tx.image_user.use_auto_refresh = True
else:
    print("NO SCREEN FRAMES YET (run screen_frames.py)")
nt.links.new(tx.outputs[0], e_.inputs[0])
e_.inputs["Strength"].default_value = 1.5
nt.links.new(e_.outputs[0], o_.inputs[0])

C = city.build(scr_m)
# the two states of the city
for o in C["INTACT"]:
    key_vis(o, [(0, False), (FB0, True), (FB1, False)])
for o in C["RUIN"]:
    key_vis(o, [(0, True), (FB0, False), (FB1, True)])
sun = C["SUN"]
for t, e in ((0, 2.6), (FALL + 0.6, 2.6), (FALL + 0.9, 1.0), (FALL + 1.1, 2.4), (FALL + 1.5, 0.8), (FB1, 2.6)):
    sun.data.energy = e
    sun.data.keyframe_insert("energy", frame=fr(t))
# glow of the screen on the people in front of it (keyed with the screen picture, see screen_frames.py)
glow = P.area_light((30.0, 0.0, 7.0), (10.0, 0.0, 1.2), 0, 10.0, (0.75, 0.85, 1.0), size_y=6.0, name="Screen glow")
import screen_frames as SF  # noqa: E402
for f in range(1, N + 1, 2):
    glow.data.energy = 9000 * SF.brightness((f - 1) / FPS)
    glow.data.keyframe_insert("energy", frame=f)

# ------------------------------------------------------------------ cast
CH = {}
for k in ("me", "kian", "mom"):
    ch = cast.spawn(k)
    T.register(ch, k, realistic=True)
    CH[k] = ch
skin, clothes = T.SKIN[CH["mom"].name]            # cream sweater reads as skin in the flat look
clothes = dict(clothes)
for kk in list(clothes):
    if "sweater" in kk:
        clothes[kk] = (0.55, 0.16, 0.22)
T.SKIN[CH["mom"].name] = (skin, clothes)
EXTRAS = []
for i in range(6):
    ch = cast.spawn_extra("passerby", i + 1)
    T.SKIN[ch.name] = (tuple(c * 0.78 for c in ch.d.get("skin_tint", cast.WARM)),
                       {k: v for k, v in ch.d.get("clothes", {}).items() if v})
    key = f"x{i}"
    CH[key] = ch
    EXTRAS.append(key)
CLIP = {}


def clip(name):
    if name not in CLIP:
        CLIP[name] = mocap.load(os.path.join(MOC, name + ".fbx"))
    return CLIP[name]


def walk_speed(who, name="walking"):
    """Metres per second the in-place walk cycle really covers (foot speed while planted)."""
    ch = CH[who]
    rig = ch.rig
    c = clip(name)
    s0 = 5000
    n = mocap.apply(ch, c, start=s0, length=48, offset=(0, 0, 0), facing=0, in_place=True, loop=True)
    pts = []
    for f in range(s0, s0 + n):
        sc.frame_set(f)
        for side in ("l", "r"):
            p = (rig.matrix_world @ rig.pose.bones[f"foot_{side}"].matrix).translation
            pts.append((side, f, p.y, p.z))
    v = []
    for side in ("l", "r"):
        s = [(f, y, z) for sd, f, y, z in pts if sd == side]
        zmin = min(z for _, _, z in s)
        for (f0, y0, z0), (f1, y1, z1) in zip(s, s[1:]):
            if z0 < zmin + 0.025 and z1 < zmin + 0.025:
                v.append(abs(y1 - y0) * FPS)
    v.sort()
    sp = v[len(v) // 2] if v else 1.2
    print("WALK SPEED", who, round(sp, 3))
    return sp


V = {k: walk_speed(k) for k in ["me", "kian", "mom", "x0"]}
for k in EXTRAS[1:]:
    V[k] = V["x0"]
for _ch in CH.values():                   # clear the measuring keys
    ad = _ch.rig.animation_data
    if ad and ad.action:
        for fc in fcurves_of(_ch.rig):
            for kp in [kp for kp in fc.keyframe_points if kp.co.x >= 4999][::-1]:
                fc.keyframe_points.remove(kp)
mocap.LAST.clear()

CUTS = {0.0, 6.0, 9.5, 20.6, 22.0, 28.0, 33.0, 37.0, 45.0, 51.0, 56.0, 66.0}
LASTSEG = {}


def act(who, name, t0, t1, pos, facing, follow=None, turn=0.0, **kw):
    """Character `who` plays clip `name` from t0 to t1 at pos/facing (wall's act(): inside a shot the body eases
    out of the previous pose; follow=True continues the hips from where the previous segment left them)."""
    rig = CH[who].rig
    n = fr(t1) - fr(t0)
    in_shot = t0 not in CUTS and LASTSEG.get(who) == t0
    if follow is None:
        follow = in_shot
    if in_shot and not turn:
        turn = 0.5
    hips_prev = None
    if follow and in_shot:
        sc.frame_set(fr(t0) - 1)
        hips_prev = (rig.matrix_world @ rig.pose.bones["pelvis"].matrix).translation.copy()
        old_rz = rig.rotation_euler[2]
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
    return pos


def walk(who, t0, t1, p0, facing, v, name="walking", **kw):
    """Walk cycle along a straight line at v m/s; the clip plays at the rate that makes the feet stick."""
    d = Vector((-math.sin(math.radians(facing)), math.cos(math.radians(facing)), 0))
    n = fr(t1) - fr(t0)
    rate = v / V[who]
    in_shot = t0 not in CUTS and LASTSEG.get(who) == t0
    mocap.apply(CH[who], clip(name), start=fr(t0), length=n, speed=rate, in_place=True, loop=True,
                place=lambda j: (tuple(Vector(p0) + d * v * j / FPS), facing), blend=8 if in_shot else 0, **kw)
    LASTSEG[who] = t1
    return Vector(p0) + d * v * (n - 1) / FPS


# ---- FLASHBACK: I walk along the arcade (camera), mom and Kian just ahead, the crowd around us
VW = V["mom"] * 0.95                       # our walking speed (m/s)
CAM0 = Vector((-15.0, 0.15, 1.62))
mom_end = walk("mom", FB0, FALL, CAM0 + Vector((2.5, 0.75, -1.62)), -90, VW)
kian_end = walk("kian", FB0, FALL, CAM0 + Vector((1.9, -0.55, -1.62)), -90, VW)
CAM_FALL = CAM0 + Vector((VW * (FALL - FB0), 0, 0))
act("mom", "terrified", FALL, FB1, tuple(mom_end), 70, src_from=0.2)
act("kian", "terrified", FALL, FB1, tuple(kian_end), 110, src_from=0.6)
rnd = random.Random(3)
CROWD = [  # (who, start pos, facing, speed factor)
    ("x0", (2.0, 1.9, 0), 90, 0.9), ("x1", (6.0, -1.6, 0), 90, 1.0), ("x2", (-9.0, -2.4, 0), -90, 0.9),
    ("x3", (10.0, 0.6, 0), 90, 0.95), ("x4", (-6.5, 2.6, 0), -90, 0.8), ("x5", (14.0, -0.6, 0), 90, 1.05),
]
for who, p, fac, k in CROWD:
    end = walk(who, FB0, FALL + rnd.uniform(0.0, 0.4), p, fac, V[who] * k)
    t_mid = LASTSEG[who]
    act(who, "terrified", t_mid, FALL + 1.6, tuple(end), fac + rnd.uniform(-40, 40), src_from=rnd.uniform(0, 1))
    act(who, "zombie_dying", FALL + 1.6, FB1, tuple(end), fac, speed=1.2)
# ---- PRESENT
ME_P, KI_P = (11.0, 0.9, 0), (11.8, -0.45, 0)
act("kian", "zombie_dying", 22.0, 23.2, KI_P, -120, src_from=3.25, speed=0.01)
act("kian", "pushing", 23.2, 26.6, KI_P, -120, follow=False)
act("kian", "nervously_look_around", 26.6, 28.0, KI_P, -110)
act("me", "zombie_dying", 22.0, 24.6, ME_P, -60, src_from=3.25, speed=0.01)
act("me", "pushing", 24.6, 28.0, ME_P, -60, follow=False)
# before that (shot 2) the same two bodies on the floor
act("kian", "zombie_dying", 6.0, 9.5, KI_P, -120, src_from=3.25, speed=0.01)
act("me", "zombie_dying", 6.0, 9.5, ME_P, -60, src_from=3.25, speed=0.01)
ME_S, KI_S = (11.0, 0.9, 0), (11.85, -0.45, 0)
act("kian", "nervously_look_around", 28.0, 33.0, KI_S, -100)
act("me", "nervously_look_around", 28.0, 33.0, ME_S, -80, src_from=2.0)
act("kian", "breathing_idle", 33.0, 37.0, KI_S, -95)
act("me", "breathing_idle", 33.0, 37.0, ME_S, -88, src_from=2.0)
act("kian", "breathing_idle", 37.0, 45.0, KI_S, -92, src_from=1.0)
act("me", "breathing_idle", 37.0, 45.0, ME_S, -86, src_from=4.0)
act("kian", "breathing_idle", 45.0, 51.0, KI_S, -92, src_from=3.0)
act("me", "breathing_idle", 45.0, 51.0, ME_S, -86, src_from=6.0)
to_k = Vector(KI_S) - Vector(ME_S)
FAC_ME = math.degrees(math.atan2(-to_k.x, to_k.y))
FAC_KI = math.degrees(math.atan2(to_k.x, -to_k.y))
act("me", "thinking", 51.0, 56.0, ME_S, FAC_ME)
act("kian", "breathing_idle", 51.0, 54.4, KI_S, FAC_KI, src_from=5.0)
act("kian", "head_nod_yes", 54.4, 56.0, KI_S, FAC_KI)
WALK_V = V["me"] * 0.9
ME_W0, KI_W0 = Vector((11.6, 0.55, 0)), Vector((12.0, -0.5, 0))
me_w = walk("me", 56.0, END + 0.1, ME_W0, -90, WALK_V)
ki_w = walk("kian", 56.0, END + 0.1, KI_W0, -90, WALK_V)


def mid_walk(t):
    return (ME_W0 + KI_W0) / 2 + Vector((WALK_V * (t - 56.0), 0, 0))


# who is on screen when (hidden otherwise, saves render time)
PRESENT = {"me": [(6.0, 9.5), (22.0, END + 1)], "kian": [(6.0, 9.5), (FB0, FB1), (22.0, END + 1)],
           "mom": [(FB0, FB1)]}
for k in EXTRAS:
    PRESENT[k] = [(FB0, FB1)]
# a character holds his place for the whole segment and jumps (at the cut) to the next one
for _ch in CH.values():
    for fc in fcurves_of(_ch.rig):
        if fc.data_path in ("location", "rotation_euler") and len(fc.keyframe_points) < 200:
            for kp in fc.keyframe_points:
                kp.interpolation = "CONSTANT"

# ---- faces
WORRY = {"me": [(0, 0.6), (22, 1.2), (29, 1.5), (38, 1.0), (46, 1.6), (51, 1.0), (56, 0.6)],
         "kian": [(0, 0.8), (FB0, 0.0), (FALL, 2.0), (22, 1.5), (28, 2.0), (37, 0.6), (40, 1.4), (45, 2.0), (51, 1.5),
                  (56, 1.0)],
         "mom": [(0, 0.0), (FALL, 2.0)]}
SMILE = {"mom": [(FB0, 0.7), (FALL, 0.0)], "kian": [(FB0, 0.6), (FALL, 0.0)]}


def curve(pts, t, default=0.0):
    if not pts:
        return default
    v = pts[0][1] if t >= pts[0][0] else default
    for (a, va), (b, vb) in zip(pts, pts[1:] + [(999, pts[-1][1])]):
        if a <= t < b:
            v = va + (vb - va) * seg(t, a, min(b, a + 0.8))
    return v


def present(who, t):
    return any(a <= t < b for a, b in PRESENT[who])


for who, ch in CH.items():
    for f in range(1, N + 1):
        t = (f - 1) / FPS
        st = dict(t=t, seed=ch.seed, worry=curve(WORRY.get(who, [(0, 0.3), (FALL, 2.0)]), t),
                  talking=speaking(who, t), zombie=0.0)
        sm = curve(SMILE.get(who, []), t)
        if sm:
            st["smile"] = sm
        if who in EXTRAS and t < FALL:
            st["smile"] = 0.3
        if FALL < t < FB1 and who != "me":
            st["scream"] = 0.5 * seg(t, FALL + 0.3, FALL + 0.8)
        sk = ch.body.data.shape_keys
        for k, v in anim.face(st).items():
            if k in ch.keys:
                ch._put(sk, f'key_blocks["{k}"].value', 0, f, max(0.0, min(1.0, v)))
        if f == 1 or present(who, t) != present(who, t - 1 / FPS):
            ch.hide(f, not present(who, t))
    ch.flush()


# ------------------------------------------------------------------ Kian's tear (shot 10)
def tear(ch, t0, t1, side, size=1.0):
    """A drop wells up under the eye, slides down the cheek and drops off. Follows the head."""
    sc.frame_set(fr(t0))
    eyes = ch.parts.get("Eyes", [])
    inv = ch.rig.matrix_world.inverted()
    pts = [inv @ (o.matrix_world @ v.co) for o in eyes for v in o.data.vertices]     # rig-local rest points
    sel = [p for p in pts if (p.x < 0) == (side < 0)]
    if not sel:
        print("NO EYES FOUND")
        return None
    c = sum(sel, Vector()) / len(sel)
    front = min(p.y for p in sel)
    p_rest = ch.rig.matrix_world @ Vector((c.x + side * 0.004, front - 0.004, c.z - 0.016))
    hb = ch.rig.pose.bones["head"]
    pb_m = ch.rig.matrix_world @ hb.matrix
    rest_m = ch.rig.matrix_world @ hb.bone.matrix_local
    p = pb_m @ (rest_m.inverted() @ p_rest)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=14, ring_count=9, radius=0.0055 * size, location=p)
    d = bpy.context.object
    d.name = f"{ch.name} tear {side}"
    for v in d.data.vertices:
        if v.co.z > 0:
            k = v.co.z / (0.0055 * size)
            v.co.x *= (1 - 0.75 * k)
            v.co.y *= (1 - 0.75 * k)
            v.co.z *= 1.8
    tm = bpy.data.materials.new("Tear")
    tm.use_nodes = True
    bs = tm.node_tree.nodes["Principled BSDF"]
    bs.inputs["Base Color"].default_value = (0.8, 0.93, 1.0, 1)
    bs.inputs["Emission Color"].default_value = (0.8, 0.93, 1.0, 1)
    bs.inputs["Emission Strength"].default_value = 0.6
    d.data.materials.append(tm)
    con = d.constraints.new("CHILD_OF")
    con.target, con.subtarget = ch.rig, "head"
    con.inverse_matrix = pb_m.inverted()
    base = d.location.copy()
    fwd = (pb_m.to_3x3() @ (rest_m.to_3x3().inverted() @ Vector((0, -1, 0)))).normalized()
    path = [(0.0, 0.0, 0.0, 0.0), (0.4, 0.6, 0.0, 0.0), (1.4, 1.0, 0.004, 0.0), (t1 - t0 - 0.6, 1.0, 0.05, 0.006),
            (t1 - t0 - 0.3, 1.0, 0.07, 0.012), (t1 - t0, 0.0, 0.09, 0.015)]
    for dt, s, down, out in path:
        d.scale = (s, s * 0.7, s * (1 + 0.6 * min(1, down * 20)))
        d.keyframe_insert("scale", frame=fr(t0 + dt))
        d.location = base + Vector((0, 0, -down)) + fwd * out
        d.keyframe_insert("location", frame=fr(t0 + dt))
    key_vis(d, [(0, False), (t0, True), (t1 + 0.05, False)])
    return d


TEARS = [tear(CH["kian"], 46.0, 50.2, -1, 1.0), tear(CH["kian"], 47.4, 50.8, 1, 0.8)]

# ------------------------------------------------------------------ camera
cam = bpy.data.objects.new("Camera", bpy.data.cameras.new("Camera"))
sc.collection.objects.link(cam)
sc.camera = cam
cam.data.clip_start = 0.05
cam.data.clip_end = 800
KEYS = []          # (frame, loc, aim, lens)


def shot(t0, t1, c0, c1, a0, a1, lens, lens1=None):
    KEYS.append((fr(t0), Vector(c0), Vector(a0), lens))
    KEYS.append((fr(t1) - 1, Vector(c1), Vector(a1), lens1 or lens))


def head(who, t):
    sc.frame_set(fr(t))
    r = CH[who].rig
    return (r.matrix_world @ r.pose.bones["head"].matrix).translation.copy()


shot(0.0, 6.0, (-48, -12, 44), (-41, -17.5, 40.5), (0, 3, 3), (5, 2, 3), 30)
shot(6.0, 9.5, (8.2, -2.3, 0.55), (8.45, -2.15, 0.7), (11.5, 0.3, 0.2), (11.5, 0.3, 0.75), 22)
# flashback POV: my eyes, a soft walking bob, looking a little at mom and Kian
for f in range(fr(FB0), fr(FALL)):
    t = (f - 1) / FPS
    c = CAM0 + Vector((VW * (t - FB0), 0.03 * math.sin(2 * math.pi * 0.9 * t), 0.025 * math.sin(2 * math.pi * 1.8 * t)))
    a = c + Vector((6, -0.2 + 0.6 * math.sin(t * 0.7), -0.35))
    KEYS.append((f, c, a, 22))
# the fall: I stop, the picture shakes, I look at mom and Kian turning back to me
rs = random.Random(11)
for f in range(fr(FALL), fr(FB1)):
    t = (f - 1) / FPS
    k = 0.04 * seg(t, FALL + 0.5, FALL + 1.0) + 0.02 * seg(t, FALL + 2.4, FB1)
    c = CAM_FALL + Vector((0.25 * seg(t, FALL, FALL + 0.6), rs.uniform(-k, k), rs.uniform(-k, k)))
    a = CAM_FALL + Vector((3.0, 0.1, -0.45)) + Vector((0, rs.uniform(-k, k) * 3, rs.uniform(-k, k) * 3))
    KEYS.append((f, c, a, 22))
shot(20.6, 22.0, (9.3, -1.9, 0.45), (9.3, -1.9, 0.45), (11.4, 0.2, 0.25), (11.4, 0.2, 0.25), 24)
shot(22.0, 28.0, (9.3, -1.9, 0.45), (9.55, -1.7, 0.62), (11.4, 0.2, 0.25), (11.4, 0.2, 0.8), 24)
shot(28.0, 33.0, (8.4, -3.1, 0.9), (8.7, -2.9, 1.0), (11.4, 0.0, 1.3), (16.0, 3.0, 10.0), 20)
shot(33.0, 37.0, (7.3, 0.25, 1.75), (7.9, 0.22, 1.75), (35.75, 0, 7.0), (35.75, 0, 7.2), 26)
shot(37.0, 45.0, (9.7, 0.1, 1.55), (10.15, 0.1, 1.6), (35.75, 0, 7.3), (35.75, 0, 7.6), 42)
hk = head("kian", 47.0)
shot(45.0, 51.0, hk + Vector((0.9, -0.2, 0.0)), hk + Vector((0.68, -0.15, -0.01)), hk + Vector((0, 0, -0.02)),
     hk + Vector((0, 0, -0.025)), 48)
mid = (Vector(ME_S) + Vector(KI_S)) / 2 + Vector((0, 0, 1.35))
side = Vector((-to_k.y, to_k.x, 0)).normalized()
if side.x < 0:
    side = -side
shot(51.0, 56.0, mid + side * 2.7 + Vector((0, 0, 0.1)), mid + side * 2.4 + Vector((0, 0, 0.1)), mid, mid, 30)
for t in [56.0 + 0.5 * i for i in range(21)]:            # follow from behind, slowly closing in (push)
    m = mid_walk(t)
    u = seg(t, 56.0, 66.0)
    KEYS.append((min(fr(t), fr(66.0) - 1), m + Vector((-4.6 + 1.6 * u, 0.15, 1.55)), m + Vector((8, 0, 1.4)), 24))
for t in [66.0 + 0.5 * i for i in range(13)]:            # rise up: two people in the whole city
    m = mid_walk(t)
    u = seg(t, 66.0, END)
    c = m + Vector((-6 - 22 * u, -5 - 26 * u, 5 + 34 * u))
    KEYS.append((min(fr(t), N), c, m + Vector((4 * u, 0, 0.8 * (1 - u))), 26))
KEYS.sort(key=lambda k: k[0])
for f, c, a, lens in KEYS:
    cam.location = c
    cam.rotation_euler = (a - c).to_track_quat("-Z", "Y").to_euler()
    cam.keyframe_insert("location", frame=f)
    cam.keyframe_insert("rotation_euler", frame=f)
    cam.data.lens = lens
    cam.data.keyframe_insert("lens", frame=f)
for owner in (cam, cam.data):
    for fc in fcurves_of(owner):
        for k in fc.keyframe_points:
            k.interpolation = "LINEAR"

# ------------------------------------------------------------------ look
sc.frame_set(1)
T.SAT = 0.6
T.toonify(sc, samples=int(os.environ.get("SAMPLES", "8")))
people = [o for c_ in CH.values() for o in c_.objects if o.type == "MESH" and not any(
    k in o.name.lower() for k in ("high-poly", "lash", "brow", "teeth", "tongue", "tear"))]
T.ink(people, 0.005)
T.ink([o for o in C["INK"] if o.type == "MESH"], 0.035)
city.ivy_ink()
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
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(HERE, "year1500.blend"))
