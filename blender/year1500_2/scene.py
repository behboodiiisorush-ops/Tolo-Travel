"""«سال ۱۵۰۰ — قسمت دوم» — through my eyes again. Two days without food; Kian and I walk down the empty arcade:
every shop is open, lit and full of food, nobody anywhere. Strange sounds. We go into a shop and take bread and a
can; the shop's loudspeaker crackles, laughs: «خوش اومدی... به دنیای فانی». We run out — and far down the
arcade a man walks to a house door, opens it and goes in.  Same city, cast, stylized look and Mixamo motion as
part 1 (blender/year1500), lips from the ElevenLabs takes (lips.py).

    ../cast/bpy.sh scene.py --still 100,500     -> test/s_XXXX.png
    ../cast/bpy.sh scene.py --save              -> year1500_2.blend (render.py renders from it)
Shots (seconds):
  A   0.0- 7.0  drone: the empty city, two small figures walking under the glass vault (title)
  B   7.0-19.0  my eyes: walking west down the arcade, shops open on both sides
  C  19.0-30.0  strange sounds; we stop and look around; a can rolls across by itself
  D  30.0-50.0  into a shop: Kian picks bread from a crate, I take a can from the shelf
  E  50.0-59.0  the loudspeaker: a laugh, «welcome to the mortal world»
  F  59.0-67.0  we run out
  G  67.0-73.0  far down the arcade a man walks to a door ...
  H  73.0-79.6  (close) he opens the door and goes in; the door shuts
  I  79.6-86.0  my eyes: Kian, the closed door
"""
import bpy, sys, os, math, random
from mathutils import Vector
HERE = os.path.dirname(os.path.abspath(__file__))
P1 = os.path.join(HERE, "..", "year1500")
sys.path.insert(0, os.path.join(HERE, "..", "cast"))
sys.path.insert(0, os.path.join(HERE, "..", "studio"))
sys.path.insert(0, HERE)                  # this episode's captions.py first
sys.path.append(P1)                       # city.py of part 1
bpy.ops.wm.read_factory_settings(use_empty=True)
import cast, mocap, anim  # noqa: E402
import props as P         # noqa: E402
import toon_look as T     # noqa: E402
import city               # noqa: E402
import shops              # noqa: E402
import lips               # noqa: E402
from captions import END  # noqa: E402

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
    for t, v in pts:
        o.hide_render = not v
        o.keyframe_insert("hide_render", frame=max(1, fr(t)) if t > 0 else 1)
    for fc in fcurves_of(o):
        if fc.data_path == "hide_render":
            for k in fc.keyframe_points:
                k.interpolation = "CONSTANT"


def facing_to(a, b):
    d = Vector(b) - Vector(a)
    return math.degrees(math.atan2(-d.x, d.y))


# ------------------------------------------------------------------ city (ruined, dead screen) + shops
scr_m = P.mat("Big screen", (0.02, 0.02, 0.02), 0.3)
dead = os.path.join(P1, "screen", "s_1728.png")
if os.path.exists(dead):
    scr_m = P.image("Big screen dead", dead, strength=0.6)
C = city.build(scr_m)
for o in C["INTACT"]:
    o.hide_render = True
    o.hide_viewport = True
S = shops.build(city.M)
C["SUN"].data.energy = 3.2 * 1.6

# ------------------------------------------------------------------ cast
CH = {}
for k in ("me", "kian"):
    ch = cast.spawn(k)
    T.register(ch, k, realistic=True)
    CH[k] = ch
st_ = cast.spawn_extra("passerby", 2)
T.SKIN[st_.name] = (tuple(c * 0.78 for c in st_.d.get("skin_tint", cast.WARM)),
                    {k: v for k, v in st_.d.get("clothes", {}).items() if v})
CH["man"] = st_
HEADPARTS = ("hair", "brow", "lash", "eye", "teeth", "tongue")
CLIP = {}


def clip(name):
    if name not in CLIP:
        CLIP[name] = mocap.load(os.path.join(MOC, name + ".fbx"))
    return CLIP[name]


def walk_speed(who, name="walking"):
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
    return v[len(v) // 2] if v else 1.2


V = {k: walk_speed(k) for k in CH}
for _ch in CH.values():
    for fc in fcurves_of(_ch.rig):
        for kp in [kp for kp in fc.keyframe_points if kp.co.x >= 4999][::-1]:
            fc.keyframe_points.remove(kp)
mocap.LAST.clear()
print("WALK SPEEDS", V)

CUTS = {0.0, 7.0, 73.0, 81.4}
LASTSEG = {}


def act(who, name, t0, t1, pos, facing, follow=None, **kw):
    rig = CH[who].rig
    n = fr(t1) - fr(t0)
    in_shot = t0 not in CUTS and LASTSEG.get(who) == t0
    if follow is None:
        follow = in_shot
    hips_prev = None
    if follow and in_shot:
        sc.frame_set(fr(t0) - 1)
        hips_prev = (rig.matrix_world @ rig.pose.bones["pelvis"].matrix).translation.copy()
        old_rz = rig.rotation_euler[2]
    mocap.apply(CH[who], clip(name), start=fr(t0), length=n, offset=pos, facing=facing, blend=8 if in_shot else 0, **kw)
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
    if hips_prev is not None:
        rig.rotation_euler = (0, 0, old_rz)
        rig.keyframe_insert("rotation_euler", index=2, frame=fr(t0))
        rig.rotation_euler = (0, 0, math.radians(facing) + math.pi)
        rig.keyframe_insert("rotation_euler", index=2, frame=fr(t0 + 0.5))
    LASTSEG[who] = t1
    return Vector(pos)


def walk(who, t0, t1, p0, p1, name="walking"):
    """Straight walk from p0 to p1 between t0 and t1; the cycle plays at the rate that makes the feet stick."""
    p0, p1 = Vector(p0), Vector(p1)
    facing = facing_to(p0, p1)
    v = (p1 - p0).length / (t1 - t0)
    d = (p1 - p0).normalized()
    n = fr(t1) - fr(t0)
    in_shot = t0 not in CUTS and LASTSEG.get(who) == t0
    mocap.apply(CH[who], clip(name), start=fr(t0), length=n, speed=v / V[who], in_place=True, loop=True,
                place=lambda j: (tuple(p0 + d * v * j / FPS), facing), blend=8 if in_shot else 0)
    LASTSEG[who] = t1
    return p1


HX, HS = shops.HERO                               # hero shop: x, north side
# ---- A/B: walking west down the arcade (from the screen end)
ME0, KI0 = Vector((31.0, 0.7, 0)), Vector((29.6, -0.7, 0))
ME_C = walk("me", 0.0, 19.0, ME0, ME0 + Vector((-22.8, 0, 0)))
KI_C = walk("kian", 0.0, 19.0, KI0, KI0 + Vector((-22.8, 0, 0)))
# ---- C: strange sounds: stop, look around
act("me", "looking_around", 19.0, 25.0, tuple(ME_C), 90)
act("me", "breathing_idle", 25.0, 30.0, tuple(ME_C), 105, src_from=1.0)
act("kian", "looking_around", 19.0, 25.5, tuple(KI_C), 80, src_from=1.5)
act("kian", "nervously_look_around", 25.5, 30.0, tuple(KI_C), 60)
# ---- D: into the hero shop
ME_D0, ME_D = Vector((HX + 0.8, 5.9, 0)), Vector((HX + 0.75, 9.72, 0))
KI_D0, KI_D = Vector((HX - 0.6, 5.7, 0)), Vector((HX - 0.9, 9.25, 0))
walk("me", 30.0, 35.0, ME_C, ME_D0)
walk("me", 35.0, 37.8, ME_D0, ME_D)
act("me", "breathing_idle", 37.8, 50.2, tuple(ME_D), 0, src_from=2.0)
walk("kian", 30.0, 34.4, KI_C, KI_D0)
walk("kian", 34.4, 36.6, KI_D0, KI_D)
act("kian", "breathing_idle", 36.6, 38.0, tuple(KI_D), 0, src_from=1.0)
act("kian", "picking_up", 38.0, 47.6, tuple(KI_D), 0)
act("kian", "breathing_idle", 47.6, 52.0, tuple(KI_D), 20, src_from=3.0)
# ---- E: the loudspeaker: fear
act("me", "breathing_idle", 50.2, 59.0, tuple(ME_D), facing_to(ME_D, S["SPEAKER_AT"]), src_from=5.0)   # (terrified puts my own hands over the camera)
act("kian", "terrified", 52.0, 59.0, tuple(KI_D), -40, src_from=0.6)
# ---- F: run out
ME_F1, ME_F2 = Vector((HX + 0.4, 5.6, 0)), Vector((1.0, 0.8, 0))
KI_F1, KI_F2 = Vector((HX - 0.5, 5.4, 0)), Vector((-0.2, -0.5, 0))
walk("kian", 59.0, 61.0, KI_D, KI_F1)
walk("kian", 61.0, 64.0, KI_F1, KI_F2)
walk("me", 59.4, 61.6, ME_D, ME_F1)
walk("me", 61.6, 64.6, ME_F1, ME_F2)
act("kian", "breathing_idle", 64.0, 70.0, tuple(KI_F2), 90, src_from=2.5)
act("me", "breathing_idle", 64.6, 86.1, tuple(ME_F2), 90, src_from=4.0)
# ---- G: Kian points down the arcade at the man (the clip points to the character's left: face north)
act("kian", "pointing", 70.0, 72.8, tuple(KI_F2), 0)
act("kian", "breathing_idle", 72.8, 80.0, tuple(KI_F2), 90, src_from=1.0)
act("kian", "breathing_idle", 80.0, 86.1, tuple(KI_F2), facing_to(KI_F2, ME_F2) - 30, src_from=5.0)
# ---- the man: walks to the house door, opens it, goes in
HOUSE = S["HOUSE_AT"]
MAN0, MAN1 = Vector((-11.5, -2.6, 0)), Vector((HOUSE.x, -5.55, 0))
walk("man", 67.0, 73.6, MAN0, MAN1 + Vector((0.4, 0.9, 0)))
act("man", "opening_door_inwards", 73.6, 80.0, tuple(MAN1), 180)
PRESENT = {"me": [(0, END + 1)], "kian": [(0, END + 1)], "man": [(67.0, 79.9)]}

# ---- the door follows the man's hand: find when a hand reaches the handle, then the door swings with it
rig_m = CH["man"].rig
hpos = S["HANDLE"].matrix_world.translation.copy()
best = None
for f in range(fr(73.6), fr(76.6)):
    sc.frame_set(f)
    for side in ("l", "r"):
        p = rig_m.matrix_world @ rig_m.pose.bones[f"hand_{side}"].tail
        d = (p - hpos).length
        if best is None or d < best[0]:
            best = (d, f, side)
print("MAN HAND TO HANDLE", round(best[0], 3), best[1], best[2])
# move him so his reaching hand really meets the handle (the clip's own reach), then measure again
sc.frame_set(best[1])
miss = hpos - (rig_m.matrix_world @ rig_m.pose.bones[f"hand_{best[2]}"].tail)
MAN1 = MAN1 + Vector((miss.x, miss.y, 0))
LASTSEG["man"] = 73.6
walk("man", 67.0, 73.6, MAN0, MAN1 + Vector((0.4, 0.9, 0)))
act("man", "opening_door_inwards", 73.6, 80.0, tuple(MAN1), 180, follow=False)
best = None
for f in range(fr(73.6), fr(76.6)):
    sc.frame_set(f)
    for side in ("l", "r"):
        p = rig_m.matrix_world @ rig_m.pose.bones[f"hand_{side}"].tail
        d = (p - hpos).length
        if best is None or d < best[0]:
            best = (d, f, side)
print("MAN HAND TO HANDLE (moved)", round(best[0], 3), best[1], best[2])
with open(os.path.join(HERE, "timing.txt"), "w") as fh:
    fh.write(f"door_touch {(best[1] - 1) / FPS:.3f}\ndoor_slam 81.15\n")
T_TOUCH = (best[1] - 1) / FPS
SIDE = best[2]
hinge = S["HINGE"]
for t, ang in ((0, 0), (T_TOUCH + 0.15, 0), (T_TOUCH + 1.6, 78), (80.2, 78), (81.15, 0)):
    hinge.rotation_euler = (0, 0, math.radians(ang))
    hinge.keyframe_insert("rotation_euler", index=2, frame=fr(t))
for fc in fcurves_of(hinge):
    kps = fc.keyframe_points
    kps[-1].interpolation = "LINEAR"
    if len(kps) > 1:
        kps[-2].interpolation = "QUAD"          # the door swings shut and bangs
ht = P.empty("Man hand target")
ikm = rig_m.pose.bones[f"lowerarm_{SIDE}"].constraints.new("IK")
ikm.target, ikm.chain_count = ht, 2
for f in range(fr(T_TOUCH - 0.5), fr(T_TOUCH + 1.9)):
    sc.frame_set(f)
    ht.location = S["HANDLE"].matrix_world.translation
    ht.keyframe_insert("location", frame=f)
for t, v in ((0, 0.0), (T_TOUCH - 0.35, 0.0), (T_TOUCH, 1.0), (T_TOUCH + 1.5, 1.0), (T_TOUCH + 1.85, 0.0)):
    ikm.influence = v
    ikm.keyframe_insert("influence", frame=fr(t))

# ---- Kian's bread: in the crate until his hands close on it, then held between both hands
rig_k = CH["kian"].rig


def hands_mid(rig):
    a = rig.matrix_world @ rig.pose.bones["hand_l"].tail
    b = rig.matrix_world @ rig.pose.bones["hand_r"].tail
    return (a + b) / 2


best = None
for f in range(fr(39.0), fr(46.0)):
    sc.frame_set(f)
    m = hands_mid(rig_k)
    d = (m - S["BREAD"].location).length
    if best is None or d < best[0]:
        best = (d, f)
print("KIAN HANDS TO BREAD", round(best[0], 3), best[1])
with open(os.path.join(HERE, "timing.txt"), "a") as fh:
    fh.write(f"bread_grab {(best[1] - 1) / FPS:.3f}\n")
bread = S["BREAD"]
bread.keyframe_insert("location", frame=1)
bread.keyframe_insert("location", frame=best[1] - 1)
for f in range(best[1], N + 1):
    sc.frame_set(f)
    bread.location = hands_mid(rig_k) + Vector((0, 0, -0.02))
    bread.keyframe_insert("location", frame=f)
# ---- my can: my right hand reaches the shelf (IK), closes on it, then it stays in my hand
rig_me = CH["me"].rig
can = S["CAN"]
ct = P.empty("My hand target")
ct.location = S["CAN_AT"] + Vector((0, -0.05, 0))
ik = rig_me.pose.bones["lowerarm_r"].constraints.new("IK")
ik.target, ik.chain_count = ct, 2
G0, G1, G2 = 42.0, 43.3, 44.6
for t, v in ((0, 0.0), (G0, 0.0), (G1, 1.0), (G1 + 0.2, 1.0), (G2, 0.0)):
    ik.influence = v
    ik.keyframe_insert("influence", frame=fr(t))
sc.frame_set(fr(G1))
hand = rig_me.matrix_world @ rig_me.pose.bones["hand_r"].tail
print("MY HAND TO CAN", round((hand - S["CAN_AT"]).length, 3))
can_off = None
can.keyframe_insert("location", frame=1)
can.keyframe_insert("location", frame=fr(G1) - 1)
for f in range(fr(G1), N + 1):
    sc.frame_set(f)
    hb_ = rig_me.pose.bones["hand_r"]
    hw = rig_me.matrix_world @ hb_.matrix
    if can_off is None:
        can_off = hw.inverted() @ can.matrix_world.translation
    can.location = hw @ can_off
    can.keyframe_insert("location", frame=f)
# ---- the can that rolls across the arcade by itself (strange)
roll = P.cyl((0, -0.045, 0), (0, 0.045, 0), 0.045, shops.FOOD["tin"], "Rolling can")
for t, x, y in ((0, 4.2, -4.6), (22.4, 4.2, -4.6), (25.2, 4.9, 3.4), (END, 4.9, 3.4)):
    roll.location = (x, y, 0.045)
    roll.keyframe_insert("location", frame=fr(t))
    roll.rotation_euler = (math.radians(90), (y + 4.6) / 0.045, 0)
    roll.keyframe_insert("rotation_euler", frame=fr(t))
key_vis(roll, [(0, False), (22.3, True)])
# ---- the speaker: its light and the shop light flicker with the voice
led = shops.FOOD["led"]
em = [n for n in led.node_tree.nodes if n.type == "EMISSION"][0].inputs["Strength"]
hl = S["HERO_LIGHT"].data
for f in range(1, N + 1, 1):
    t = (f - 1) / FPS
    v = lips.level("voice", t)
    em.default_value = 25.0 * v if 50.0 <= t < 57.6 else (4.0 if 50.0 <= t < 57.6 else 0.0)
    em.keyframe_insert("default_value", frame=f)
    if 49.5 <= t < 58.5 and f % 2 == 0:
        rr = random.Random(f).random()
        hl.energy = 180 * (0.35 + 0.65 * v) if rr > 0.15 else 30
        hl.keyframe_insert("energy", frame=f)
    elif f in (fr(49.4), fr(58.6)):
        hl.energy = 180
        hl.keyframe_insert("energy", frame=f)

# ---- faces
WORRY = {"kian": [(0, 1.0), (9.0, 0.3), (19.5, 1.6), (34.0, 0.4), (50.2, 2.0), (66.0, 1.4), (69.5, 1.8)],
         "me": [(0, 0.8)], "man": [(0, 0.2)]}
SMILE = {"kian": [(0, 0.0), (9.4, 0.6), (13.8, 0.0), (36.2, 0.8), (49.8, 0.0)]}


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
        st = dict(t=t, seed=ch.seed, worry=curve(WORRY.get(who, []), t), talking=lips.level(who, t), zombie=0.0)
        sm = curve(SMILE.get(who, []), t)
        if sm:
            st["smile"] = sm
        if who == "kian" and 50.6 < t < 52.5:
            st["scream"] = 0.35 * seg(t, 50.6, 51.0)
        sk = ch.body.data.shape_keys
        for k, v in anim.face(st).items():
            if k in ch.keys:
                ch._put(sk, f'key_blocks["{k}"].value', 0, f, max(0.0, min(1.0, v)))
        if f == 1 or present(who, t) != present(who, t - 1 / FPS):
            ch.hide(f, not present(who, t))
    ch.flush()


def eye_points(ch):
    eyes = ch.parts.get("Eyes", [])
    inv = ch.rig.matrix_world.inverted()
    return [inv @ (o.matrix_world @ v.co) for o in eyes for v in o.data.vertices]


HEAD_OBJS = [o for k in ("Eyes", "Eyebrows", "Eyelashes", "Hair", "Teeth", "Tongue") for o in CH["me"].parts.get(k, [])]
sc.frame_set(fr(30.0))
pts = eye_points(CH["me"])
eye_rest = sum(pts, Vector()) / max(1, len(pts))
eye_rest.y = min(p.y for p in pts) - 0.02
for o in CH["me"].objects:
    if o.type == "MESH" and (o in HEAD_OBJS or any(k in o.name.lower() for k in HEADPARTS)):
        if o.animation_data:
            o.animation_data_clear()
        o.hide_render = True

# ------------------------------------------------------------------ cameras
hb = rig_me.pose.bones["head"]
pov = bpy.data.objects.new("POV", bpy.data.cameras.new("POV"))
sc.collection.objects.link(pov)
pov.data.lens = 16
pov.data.sensor_fit = "VERTICAL"
pov.data.sensor_height = 36
pov.data.clip_start = 0.06
pov.data.clip_end = 800
LOOK = [  # (t, pitch up deg, yaw left deg) on top of where my head points
    (7.0, 2, 0), (9.6, 2, -22), (12.0, 4, 24), (14.2, 2, 0), (19.0, 2, 0), (22.3, -10, 0), (25.0, -12, 30),
    (26.5, 0, 34), (30.0, 0, 0), (36.6, -4, 20), (39.0, -26, 40), (41.6, -8, -6), (44.6, -10, 0), (46.5, -22, 34),
    (50.2, 24, 0), (57.4, 22, 0), (58.2, 0, -50), (59.4, 0, 0), (64.6, 0, 0), (68.6, 1, 8), (81.4, 1, 10),
    (82.0, -6, 42), (84.4, 1, 10)]


def look(t):
    for (a, pa, ya), (b, pb, yb) in zip(LOOK, LOOK[1:] + [(999, LOOK[-1][1], LOOK[-1][2])]):
        if a <= t < b:
            u = seg(t, max(a, b - 1.0), b)
            return pa + (pb - pa) * u, ya + (yb - ya) * u
    return LOOK[0][1], LOOK[0][2]


raw = {}
for f in range(fr(7.0), N + 1):
    sc.frame_set(f)
    to_pose = rig_me.matrix_world @ hb.matrix @ hb.bone.matrix_local.inverted()
    p = to_pose @ eye_rest
    fw = to_pose.to_3x3() @ Vector((0, -1, 0))
    raw[f] = (p, math.atan2(-fw.x, fw.y), math.asin(max(-1, min(1, fw.normalized().z))))
for f in sorted(raw):
    nb = [raw[g] for g in range(f - 3, f + 4) if g in raw]
    p = sum((q[0] for q in nb), Vector()) / len(nb)
    y0 = raw[f][1]
    yaw = y0 + sum(math.atan2(math.sin(q[1] - y0), math.cos(q[1] - y0)) for q in nb) / len(nb)
    pitch = 0.35 * sum(q[2] for q in nb) / len(nb)
    lp, ly = look((f - 1) / FPS)
    pov.location = p
    pov.rotation_euler = (math.radians(90 + lp) + pitch, 0, yaw + math.radians(ly))
    pov.keyframe_insert("location", frame=f)
    pov.keyframe_insert("rotation_euler", frame=f)
cam = bpy.data.objects.new("Drone", bpy.data.cameras.new("Drone"))
sc.collection.objects.link(cam)
cam.data.clip_start, cam.data.clip_end = 0.05, 800
cam.data.sensor_fit, cam.data.sensor_height = "VERTICAL", 36
mid0 = (ME0 + KI0) / 2
KEYS = [(fr(0.0), Vector((22, -3.2, 9.5)), mid0 + Vector((0, 0, 0.8)), 32),        # inside the vault, high,
        (fr(7.0) - 1, Vector((16, -2.6, 5.5)), mid0 + Vector((-8.4, 0, 0.9)), 30),    # they walk towards us
        (fr(73.0), Vector((-18.6, -1.4, 1.6)), HOUSE + Vector((0.1, 0, 1.2)), 36),
        (fr(81.4) - 1, Vector((-18.9, -2.4, 1.5)), HOUSE + Vector((0.1, 0, 1.15)), 40)]
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
for t, c in ((0.0, cam), (7.0, pov), (73.0, cam), (81.4, pov)):
    m = sc.timeline_markers.new(f"cam {t}", frame=fr(t))
    m.camera = c
sc.camera = cam
# ------------------------------------------------------------------ look (stylized, as part 1)
import stylized_look as STY  # noqa: E402
STY.SAT = 1.35
STY.PALETTE.update({
    "Concrete": (0.92, 0.5, 0.3), "Concrete 2": (0.42, 0.68, 0.86), "Window dark": (0.05, 0.1, 0.2),
    "Window glass": (0.18, 0.45, 0.8), "Road": (0.12, 0.12, 0.15), "Pavement": (0.8, 0.7, 0.55),
    "Arcade floor": (0.82, 0.5, 0.32), "Arcade floor 2": (0.74, 0.43, 0.27), "Iron": (0.04, 0.22, 0.3),
    "Glazing bars": (0.03, 0.18, 0.25), "Pane": (0.8, 0.93, 1.0), "Pane grey": (0.55, 0.78, 0.92),
    "Pane dark": (0.2, 0.42, 0.6), "Shard": (0.75, 0.9, 1.0), "Trunk": (0.35, 0.18, 0.08), "Leaf": (0.22, 0.65, 0.1),
    "Leaf 2": (0.14, 0.5, 0.07), "Ivy": (0.16, 0.55, 0.1), "Ivy mid": (0.12, 0.45, 0.08), "Ivy light": (0.26, 0.68, 0.14),
    "Low wall": (0.95, 0.78, 0.5), "Low wall 2": (0.85, 0.58, 0.36), "Rubble": (0.72, 0.6, 0.48),
    "Car pale": (1.0, 0.66, 0.05), "Car teal": (0.02, 0.5, 0.62), "Car rust": (0.85, 0.08, 0.05),
    "Car glass": (0.04, 0.08, 0.14), "Tyre": (0.03, 0.03, 0.035),
})
wn = sc.world.node_tree.nodes
for n in wn:
    if n.type == "VALTORGB":
        n.color_ramp.elements[0].position, n.color_ramp.elements[0].color = 0.5, (0.75, 0.86, 1.0, 1)
        n.color_ramp.elements[1].position, n.color_ramp.elements[1].color = 0.8, (0.22, 0.5, 0.95, 1)
for n in wn:
    if n.type == "BACKGROUND" and not n.inputs[0].is_linked:
        n.inputs[0].default_value = (0.22, 0.25, 0.3, 1)
fill = bpy.data.objects.new("Fill", bpy.data.lights.new("Fill", "SUN"))
sc.collection.objects.link(fill)
fill.data.energy, fill.data.color, fill.data.use_shadow = 1.1, (0.75, 0.85, 1.0), False
fill.rotation_euler = (math.radians(70), 0, math.radians(60))
import colorsys  # noqa: E402
for k_, (skin, clothes) in list(T.SKIN.items()):
    h_, s_, v_ = colorsys.rgb_to_hsv(*skin)
    T.SKIN[k_] = (colorsys.hsv_to_rgb(h_, min(1.0, s_ * 1.5), v_), clothes)
STY.stylize(sc, samples=int(os.environ.get("SAMPLES", "6")))
STY.round_edges([o for o in sc.objects if o.type == "MESH" and not o.parent and o not in C["IVY"]
                 and "Vault" not in o.name and "Glass" not in o.name and o.name not in ("Ground",)
                 and "Screen" not in o.name and not o.name.startswith(("Shop ", "Hero", "Kian", "My", "Rolling", "Speaker"))],
                width=0.08)
C["SUN"].data.angle = 0.09
sc.render.resolution_x, sc.render.resolution_y = 540, 960
sc.render.film_transparent = False

args = sys.argv
if "--still" in args:
    os.makedirs(os.path.join(HERE, "test"), exist_ok=True)
    for f in [int(v) for v in args[args.index("--still") + 1].split(",")]:
        sc.frame_set(f)
        sc.camera = max((m for m in sc.timeline_markers if m.frame <= f), key=lambda m: m.frame).camera
        sc.render.filepath = os.path.join(HERE, "test", f"s_{f:04d}.png")
        bpy.ops.render.render(write_still=True)
if "--save" in args:
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(HERE, "year1500_2.blend"))
