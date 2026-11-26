"""«سال ۱۵۰۰» — seen through my eyes (POV, the «واگن آخر» way): a new city, ruined and empty. My brother Kian and
I wake up alone under the broken glass vault; a big screen crackles on and shows mom with little Kian; Kian cries;
we set off to look for life.  Bright cartoon colours + Freestyle ink (like «واگن آخر»), the cast's natural
cartoon faces, Mixamo motion. The POV camera sits in my head, so walking and looking around move it for real.

    ../cast/bpy.sh scene.py --still 40,120,...      -> test/s_XXXX.png
    ../cast/bpy.sh scene.py --save                  -> year1500.blend (render.py renders from it)
Shots (seconds):
  A   0.0- 7.0  drone over the ruined city (title)
  B   7.0-15.0  FLASHBACK, my eyes: walking with mom and Kian through the crowded new city
  C  15.0-18.6  the fall: screens glitch, lights die, people cower and drop, white flash
  -  18.6-20.0  black
  E  20.0-26.0  I open my eyes on the floor: broken glass above; Kian next to me gets up
  F  26.0-31.0  standing, looking around; Kian shouts for mom
  G  31.0-35.0  the big screen crackles on; we walk towards it
  H  35.0-43.0  mom and little Kian on the screen
  I  43.0-49.0  I turn to Kian: he's crying; my hand on his shoulder
  J  49.0-54.0  'we'll look ourselves'; he nods
  K  54.0-65.0  we walk off down the street under the broken glass
  L  65.0-72.0  the drone rises: two people in the whole city
"""
import bpy, sys, os, math, random
from mathutils import Vector, Matrix
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "cast"))
sys.path.insert(0, os.path.join(HERE, "..", "studio"))
sys.path.insert(0, HERE)                  # (studio/ has its own captions.py)
bpy.ops.wm.read_factory_settings(use_empty=True)
import cast, mocap, anim  # noqa: E402
import props as P         # noqa: E402
import toon_look as T     # noqa: E402
import city               # noqa: E402
import screen_frames as SF  # noqa: E402
from captions import END, speaking, FLASHBACK, FALL, WAKE  # noqa: E402

cast.STYLE = cast.CARTOON
FPS = 24
N = int(END * FPS)
sc = bpy.context.scene
sc.render.fps = FPS
sc.frame_start, sc.frame_end = 1, N
MOC = os.path.join(HERE, "..", "mocap")
SCR = os.path.join(HERE, "screen")
FB0, FB1 = FLASHBACK


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
for o in C["INTACT"]:
    key_vis(o, [(0, False), (FB0, True), (FB1, False)])
for o in C["RUIN"]:
    key_vis(o, [(0, True), (FB0, False), (FB1, True)])
sun = C["SUN"]
for t, e in ((0, 3.2), (FALL + 0.6, 3.2), (FALL + 0.9, 1.0), (FALL + 1.1, 2.8), (FALL + 1.5, 0.8), (FB1, 3.2)):
    sun.data.energy = e
    sun.data.keyframe_insert("energy", frame=fr(t))
glow = P.area_light((30.0, 0.0, 7.0), (10.0, 0.0, 1.2), 0, 10.0, (0.75, 0.85, 1.0), size_y=6.0, name="Screen glow")
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
T.SKIN[CH["mom"].name] = (skin, {k: ((0.55, 0.16, 0.22) if "sweater" in k else v) for k, v in clothes.items()})
EXTRAS = []
for i in range(6):
    ch = cast.spawn_extra("passerby", i + 1)
    T.SKIN[ch.name] = (tuple(c * 0.78 for c in ch.d.get("skin_tint", cast.WARM)),
                       {k: v for k, v in ch.d.get("clothes", {}).items() if v})
    CH[f"x{i}"] = ch
    EXTRAS.append(f"x{i}")
HEADPARTS = ("hair", "brow", "lash", "eye", "teeth", "tongue")
CLIP = {}


def clip(name):
    if name not in CLIP:
        CLIP[name] = mocap.load(os.path.join(MOC, name + ".fbx"))
    return CLIP[name]


def walk_speed(who, name="walking"):
    """Metres per second the in-place walk cycle really covers (foot speed while planted)."""
    ch = CH[who]
    rig = ch.rig
    s0 = 5000
    n = mocap.apply(ch, clip(name), start=s0, length=48, offset=(0, 0, 0), facing=0, in_place=True, loop=True)
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
    for fc in fcurves_of(_ch.rig):
        for kp in [kp for kp in fc.keyframe_points if kp.co.x >= 4999][::-1]:
            fc.keyframe_points.remove(kp)
mocap.LAST.clear()

CUTS = {0.0, 7.0, 18.6, 20.0, 26.0, 31.0, 43.0, 54.0, 65.0}
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
    in_shot = t0 not in CUTS and LASTSEG.get(who) == t0
    mocap.apply(CH[who], clip(name), start=fr(t0), length=n, speed=v / V[who], in_place=True, loop=True,
                place=lambda j: (tuple(Vector(p0) + d * v * j / FPS), facing), blend=8 if in_shot else 0, **kw)
    LASTSEG[who] = t1
    return Vector(p0) + d * v * (n - 1) / FPS


# ---- B/C FLASHBACK: I walk along the arcade, mom and Kian just ahead, the crowd around us
VW = 1.35
ME0 = Vector((-15.0, 0.15, 0))
me_end = walk("me", FB0, FALL, ME0, -90, VW)
mom_end = walk("mom", FB0, FALL, ME0 + Vector((2.6, 0.7, 0)), -90, VW)
kian_end = walk("kian", FB0, FALL, ME0 + Vector((2.0, -0.6, 0)), -90, VW)
act("me", "nervously_look_around", FALL, FB1, tuple(me_end), -90, src_from=0.5)
act("mom", "terrified", FALL, FB1, tuple(mom_end), 70, src_from=0.2)
act("kian", "terrified", FALL, FB1, tuple(kian_end), 110, src_from=0.6)
rnd = random.Random(3)
CROWD = [("x0", (0.0, 1.9, 0), 90, 0.9), ("x1", (4.0, -1.7, 0), 90, 1.0), ("x2", (-10.0, -2.4, 0), -90, 0.85),
         ("x3", (8.0, 0.9, 0), 90, 0.95), ("x4", (-7.5, 2.6, 0), -90, 0.8), ("x5", (12.0, -0.8, 0), 90, 1.05)]
for who, p, fac, k in CROWD:
    end = walk(who, FB0, FALL + rnd.uniform(0.0, 0.4), p, fac, V[who] * k)
    act(who, "terrified", LASTSEG[who], FALL + 1.6, tuple(end), fac + rnd.uniform(-40, 40), src_from=rnd.uniform(0, 1))
    act(who, "zombie_dying", FALL + 1.6, FB1, tuple(end), fac, speed=1.2)
# ---- E: on the floor. Kian next to me wakes and gets up
KI_E = (12.3, -0.55, 0)
act("kian", "zombie_dying", WAKE, 22.4, KI_E, 150, src_from=3.25, speed=0.01)
act("kian", "pushing", 22.4, 26.0, KI_E, 150, follow=False)
# ---- F..J standing
ME_S, KI_S = (11.0, 0.9, 0), (12.7, -0.4, 0)
act("me", "nervously_look_around", 26.0, 31.0, ME_S, -95, src_from=1.0)
act("kian", "nervously_look_around", 26.0, 31.0, KI_S, -75)
# G: we walk towards the screen, then stand and watch
ME_G1 = walk("me", 31.0, 34.4, ME_S, -90, 1.15)
KI_G1 = walk("kian", 31.0, 34.4, KI_S, -90, 1.15)
act("me", "breathing_idle", 34.4, 43.0, tuple(ME_G1), -90, src_from=2.0)
act("kian", "breathing_idle", 34.4, 43.0, tuple(KI_G1), -93, src_from=1.0)
# I/J: I turn to Kian, close; my right hand on his shoulder
KI_I = (16.0, -0.6, 0)
ME_I = (15.32, -0.26, 0)
to_k = Vector(KI_I) - Vector(ME_I)
FAC_ME = math.degrees(math.atan2(-to_k.x, to_k.y))
FAC_KI = math.degrees(math.atan2(to_k.x, -to_k.y))
act("me", "breathing_idle", 43.0, 54.0, ME_I, FAC_ME, src_from=3.0)
act("kian", "breathing_idle", 43.0, 52.6, KI_I, FAC_KI, src_from=3.0)
act("kian", "head_nod_yes", 52.6, 54.0, KI_I, FAC_KI)
# K/L: we walk off; Kian a little ahead on my right
WALK_V = 1.3
ME_W0, KI_W0 = Vector((15.0, 0.45, 0)), Vector((16.5, -0.45, 0))
walk("me", 54.0, END + 0.1, ME_W0, -90, WALK_V)
walk("kian", 54.0, END + 0.1, KI_W0, -90, WALK_V)


def mid_walk(t):
    return (ME_W0 + KI_W0) / 2 + Vector((WALK_V * (t - 54.0), 0, 0))


PRESENT = {"me": [(FB0, FB1), (26.0, END + 1)], "kian": [(FB0, FB1), (WAKE, END + 1)], "mom": [(FB0, FB1)]}
for k in EXTRAS:
    PRESENT[k] = [(FB0, FB1)]

# ---- my right hand goes to Kian's shoulder (IK on the arm, target follows his shoulder)
rig_me, rig_k = CH["me"].rig, CH["kian"].rig
hand_t = P.empty("Me hand target")
ikc = rig_me.pose.bones["lowerarm_r"].constraints.new("IK")
ikc.target = hand_t
ikc.chain_count = 2
H0, H1, H2, H3 = 44.6, 45.6, 53.0, 53.9
for f in range(fr(H0) - 1, fr(H3) + 2):
    sc.frame_set(f)
    sh = (rig_k.matrix_world @ rig_k.pose.bones["upperarm_l"].head).copy()
    nk = (rig_k.matrix_world @ rig_k.pose.bones["neck_01"].head).copy()
    hand_t.location = sh.lerp(nk, 0.25) + Vector((0, 0, 0.03))
    hand_t.keyframe_insert("location", frame=f)
for t, v in ((0, 0.0), (H0, 0.0), (H1, 1.0), (H2, 1.0), (H3, 0.0)):
    ikc.influence = v
    ikc.keyframe_insert("influence", frame=fr(t))
sc.frame_set(fr(H2))
print("HAND TO SHOULDER", round(((rig_me.matrix_world @ rig_me.pose.bones["hand_r"].tail)
                                 - hand_t.matrix_world.translation).length, 3))

# ---- faces
WORRY = {"kian": [(0, 0.8), (FB0, 0.0), (FALL, 2.0), (WAKE, 1.5), (26, 2.0), (35, 0.6), (38, 1.4), (43, 2.0), (49, 1.5),
                  (54, 1.0)],
         "mom": [(0, 0.0), (FALL, 2.0)]}
SMILE = {"mom": [(FB0, 0.7), (FALL, 0.0)], "kian": [(FB0, 0.6), (FALL, 0.0), (52.6, 0.25)]}


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
        if who == "kian" and WAKE <= t < 21.6:          # eyes still shut on the floor
            st["blink"] = 1.0
        sk = ch.body.data.shape_keys
        for k, v in anim.face(st).items():
            if k in ch.keys:
                ch._put(sk, f'key_blocks["{k}"].value', 0, f, max(0.0, min(1.0, v)))
        if f == 1 or present(who, t) != present(who, t - 1 / FPS):
            ch.hide(f, not present(who, t))
    ch.flush()
HEAD_OBJS = [o for k in ("Eyes", "Eyebrows", "Eyelashes", "Hair", "Teeth", "Tongue") for o in CH["me"].parts.get(k, [])]
print("MY HEAD PARTS", [o.name for o in HEAD_OBJS])
for o in CH["me"].objects:            # my own head is never seen (the camera is in it)
    if o.type == "MESH" and (o in HEAD_OBJS or any(k in o.name.lower() for k in HEADPARTS)):
        if o.animation_data:
            o.animation_data_clear()
        o.hide_render = True


# ------------------------------------------------------------------ Kian's tears (shot I)
def eye_points(ch):
    eyes = ch.parts.get("Eyes", [])
    inv = ch.rig.matrix_world.inverted()
    return [inv @ (o.matrix_world @ v.co) for o in eyes for v in o.data.vertices]


def tear(ch, t0, t1, side, size=1.0):
    """A drop wells up under the eye, slides down the cheek and drops off. Follows the head."""
    sc.frame_set(fr(t0))
    sel = [p for p in eye_points(ch) if (p.x < 0) == (side < 0)]
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
    tm = bpy.data.materials.get("Tear") or bpy.data.materials.new("Tear")
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
    for dt, s, down, out in [(0.0, 0.0, 0.0, 0.0), (0.4, 0.6, 0.0, 0.0), (1.4, 1.0, 0.004, 0.0),
                             (t1 - t0 - 0.6, 1.0, 0.05, 0.006), (t1 - t0 - 0.3, 1.0, 0.07, 0.012), (t1 - t0, 0.0, 0.09, 0.015)]:
        d.scale = (s, s * 0.7, s * (1 + 0.6 * min(1, down * 20)))
        d.keyframe_insert("scale", frame=fr(t0 + dt))
        d.location = base + Vector((0, 0, -down)) + fwd * out
        d.keyframe_insert("location", frame=fr(t0 + dt))
    key_vis(d, [(0, False), (t0, True), (t1 + 0.05, False)])
    return d


TEARS = [tear(CH["kian"], 43.6, 47.8, -1, 1.0), tear(CH["kian"], 45.0, 48.6, 1, 0.8)]

# ------------------------------------------------------------------ cameras
# POV: the camera is at my eyes and turns with my head, but stays level (no roll, smoothed): clean, balanced
hb = rig_me.pose.bones["head"]
sc.frame_set(fr(30.0))
pts = eye_points(CH["me"])
eye_rest = sum(pts, Vector()) / max(1, len(pts))
eye_rest.y = min(p.y for p in pts) - 0.02                       # just in front of the eyes (rig space, rest)
pov = bpy.data.objects.new("POV", bpy.data.cameras.new("POV"))
sc.collection.objects.link(pov)
pov.data.lens = 16
pov.data.sensor_fit = "VERTICAL"
pov.data.sensor_height = 36
pov.data.clip_start = 0.06
pov.data.clip_end = 800
pov.rotation_mode = "XYZ"
LOOK = [  # (t, pitch up deg, yaw left deg) — where I look, on top of where my head points
    (FB0, 2, 0), (12.0, 2, 6), (14.0, 0, -4), (FALL, -4, 0), (26.0, 2, -14), (28.6, 4, -16), (29.8, 16, 6),
    (31.0, 4, -14), (34.4, 10, -6), (43.0, -24, 0), (54.0, 0, -12), (58.0, 0, -6), (61.0, 4, 6), (63.0, 2, -4)]


def look(t):
    for (a, pa, ya), (b, pb, yb) in zip(LOOK, LOOK[1:] + [(999, LOOK[-1][1], LOOK[-1][2])]):
        if a <= t < b:
            u = seg(t, a, min(b, a + 1.2))
            return pa + (pb - pa) * u, ya + (yb - ya) * u
    return LOOK[0][1], LOOK[0][2]


raw = {}
for a_, b_ in ((FB0, FB1), (26.0, 65.0)):
    for f in range(fr(a_), fr(b_) + 1):
        sc.frame_set(f)
        W_ = rig_me.matrix_world
        to_pose = W_ @ hb.matrix @ hb.bone.matrix_local.inverted()      # rest (rig space) -> posed world
        p = to_pose @ eye_rest
        fw = to_pose.to_3x3() @ Vector((0, -1, 0))
        yaw = math.atan2(-fw.x, fw.y)
        pitch = math.asin(max(-1, min(1, fw.normalized().z)))
        raw[f] = (p, yaw, pitch)
rs = random.Random(11)
frames = sorted(raw)
for f in frames:
    nb = [raw[g] for g in range(f - 3, f + 4) if g in raw and abs(g - f) <= 3 and (g < fr(FB1) + 1) == (f < fr(FB1) + 1)]
    p = sum((q[0] for q in nb), Vector()) / len(nb)
    y0 = raw[f][1]
    yaw = y0 + sum(math.atan2(math.sin(q[1] - y0), math.cos(q[1] - y0)) for q in nb) / len(nb)
    pitch = 0.35 * sum(q[2] for q in nb) / len(nb)                        # a little of the head's nod
    t = (f - 1) / FPS
    lp, ly = look(t)
    if FALL <= t < FB1:                                                      # shake in the fall
        k = 0.012 * seg(t, FALL + 0.5, FALL + 1.0)
        p = p + Vector((rs.uniform(-k, k), rs.uniform(-k, k), rs.uniform(-k, k)))
        lp += rs.uniform(-1.5, 1.5) * seg(t, FALL + 0.5, FALL + 1.0)
    pov.location = p
    pov.rotation_euler = (math.radians(90 + lp) + pitch, 0, yaw + math.radians(ly))
    pov.keyframe_insert("location", frame=f)
    pov.keyframe_insert("rotation_euler", frame=f)
# drone / floor camera
cam = bpy.data.objects.new("Drone", bpy.data.cameras.new("Drone"))
sc.collection.objects.link(cam)
cam.data.clip_start = 0.05
cam.data.clip_end = 800
cam.data.sensor_fit = "VERTICAL"
cam.data.sensor_height = 36
KEYS = []
KEYS += [(fr(0.0), Vector((-48, -12, 44)), Vector((0, 3, 3)), 22), (fr(7.0) - 1, Vector((-40, -18, 40)), Vector((6, 2, 3)), 22)]
# E: my eyes on the floor: broken glass above, then I turn my head to Kian and sit up
FL = Vector((11.0, 0.9, 0.16))
k_head = Vector(KI_E) + Vector((0.2, 0.3, 0.15))
for t, c, a in ((WAKE, FL, FL + Vector((1.2, 0.6, 6))), (21.8, FL, FL + Vector((1.8, 0.3, 6))),
                (22.8, FL + Vector((0, 0, 0.04)), k_head + Vector((0, 0, 0.4))),
                (24.4, FL + Vector((0.1, -0.1, 0.32)), k_head + Vector((0, 0, 0.9))),
                (25.96, FL + Vector((0.2, -0.15, 0.7)), Vector(KI_E) + Vector((0, 0, 1.2)))):
    KEYS.append((fr(t), c, a, 14))
for t in [65.0 + 0.5 * i for i in range(15)]:            # rise up: two people in the whole city
    m = mid_walk(t)
    u = seg(t, 65.0, END)
    c = m + Vector((-6 - 22 * u, -5 - 26 * u, 4 + 34 * u))
    KEYS.append((min(fr(t), N), c, m + Vector((4 * u, 0, 0.8 * (1 - u))), 18))
KEYS.sort(key=lambda k: k[0])
for f, c, a, lens in KEYS:
    cam.location = c
    q = (a - c).to_track_quat("-Z", "Y")
    cam.rotation_euler = q.to_euler()
    cam.keyframe_insert("location", frame=f)
    cam.keyframe_insert("rotation_euler", frame=f)
    cam.data.lens = lens
    cam.data.keyframe_insert("lens", frame=f)
for owner in (cam, cam.data):
    for fc in fcurves_of(owner):
        for k in fc.keyframe_points:
            k.interpolation = "LINEAR"
for t, c in ((0.0, cam), (FB0, pov), (FB1, cam), (26.0, pov), (65.0, cam)):
    m = sc.timeline_markers.new(f"cam {t}", frame=fr(t))
    m.camera = c
sc.camera = cam
# ------------------------------------------------------------------ look: bright cartoon + Freestyle ink
sc.frame_set(1)
T.SAT = 1.3
T.toonify(sc, samples=int(os.environ.get("SAMPLES", "8")))
city.ivy_ink()
# black ink outlines (inverted hull: cheap in memory, unlike Freestyle on a whole city)
people = [o for c_ in CH.values() for o in c_.objects if o.type == "MESH" and o not in HEAD_OBJS and not any(
    k in o.name.lower() for k in ("high-poly", "lash", "brow", "teeth", "tongue", "tear"))]
T.ink(people, 0.006)
T.ink([o for o in C["INK"] if o.type == "MESH"], 0.04)
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
