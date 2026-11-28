"""«پارک» — a bright modern children's cartoon, ~60 s, no dialogue (music + sound effects).

Three kids and their puppy play ball in the park; the ball lands in the pond, the mother duck pushes it back,
everyone marches behind the ducks, and at the end a butterfly makes the puppy sneeze the ball out.

    ../cast/bpy.sh scene.py --check                 # build + motion report (feet sliding, pops)
    ../cast/bpy.sh scene.py --preview               # low-res EEVEE preview of every 2nd frame -> preview/
    ../cast/bpy.sh scene.py --still 300,700         # full-quality stills -> test/
    ../cast/bpy.sh scene.py --render A B            # final frames A..B -> frames/ (skips existing)
"""
import bpy, math, os, sys, json, random
from mathutils import Vector, Matrix, Euler

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lib as L
import set as S
import chars as C

FPS, T = 24, 60.0
NF = int(T * FPS)
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]

for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)
sc = bpy.context.scene
L.COL = sc.collection
sc.render.engine = "BLENDER_EEVEE"
sc.eevee.taa_render_samples = 12
sc.render.resolution_x, sc.render.resolution_y = 720, 1280
sc.render.fps = FPS
sc.view_settings.view_transform = "Standard"
sc.view_settings.look = "None"
sc.render.image_settings.file_format = "PNG"

S.build()
sun = bpy.data.lights.new("sun", "SUN")
sun.energy = 3.2
sun.use_shadow = False
so = bpy.data.objects.new("sun", sun)
sc.collection.objects.link(so)
so.rotation_euler = (Vector((0, 0, 0)) - Vector((-1.2, -1.6, 2.0))).to_track_quat("-Z", "Y").to_euler()

# ======================================================================================  cast
girl = C.Kid("girl", (10.5, -3.0), math.radians(-90), k=1.0, skin="#ffd8b8", shirt="#ffc93c", hair="#7a3e1d",
             style="pigtails", dress=True, shoes="#ff5fa2", sock="#ffffff")
boy = C.Kid("boy", (11.3, -3.6), math.radians(-90), k=1.06, skin="#f1c19a", shirt="#3fa7ff", pants="#ff6b4a",
            hair="#2b211c", style="short", shoes="#ffffff", sock="#ffd23f")
small = C.Kid("small", (12.0, -2.6), math.radians(-90), k=0.86, skin="#c98d63", shirt="#5fd068", pants="#355fcc",
              hair="#2a1a12", style="curly", shoes="#ff4b4b", sock="#ffffff")
dog = C.Dog("dog", (11.8, -3.9), math.radians(-90))
mom = C.Duck("mom", (1.3, 6.9), 0.0, k=1.0, pond=lambda p: S.in_pond(p))
babies = [C.Duck("baby%d" % i, (1.3, 6.9), 0.0, k=0.48, baby=True, pond=lambda p: S.in_pond(p)) for i in range(3)]
KIDS = [girl, boy, small]

# ---------------------------------------------------------------- spots
G_SPOT, B_SPOT, S_SPOT = Vector((-1.5, 0.5, 0)), Vector((1.8, 1.2, 0)), Vector((0.3, -1.2, 0))
D_SPOT = Vector((2.7, -0.6, 0))
BALL_IN = Vector((-0.8, 4.9, 0))
EDGE = {"girl": (-2.1, 2.9), "boy": (0.95, 3.0), "small": (0.0, 2.55)}
SIT = {"girl": (1.2, 0.95), "boy": (0.25, 1.3), "small": (-0.7, 0.95), "dog": (0.25, 0.5)}
CAM_END = (0.25, -3.0)

# ---------------------------------------------------------------- 1. run in (5 - 11.4 s)
girl.act.move(5.0, 10.6, (10.5, -3.0), (6.0, -3.3), (2.5, -1.8), G_SPOT)
boy.act.move(5.2, 11.0, (11.3, -3.6), (7.0, -3.8), (4.0, -2.4), B_SPOT)
small.act.move(5.5, 11.4, (12.0, -2.6), (8.0, -2.8), (4.5, -1.6), S_SPOT)
dog.act.move(5.3, 11.2, (11.8, -3.9), (8.0, -4.2), (5.0, -3.0), (3.4, -1.4), D_SPOT)
for k in KIDS:
    k.arms = [(0.0, "swing")]
girl.arms = [(0.0, "hold")]

# ---------------------------------------------------------------- 2. throw, catch, kick (11.4 - 19 s)
girl.act.look(10.6, B_SPOT)
boy.act.look(11.0, G_SPOT)
small.act.look(11.4, B_SPOT)
dog.act.look(11.2, G_SPOT)
girl.arms += [(12.1, "wind"), (13.0, "throw"), (13.5, "rest"), (14.3, "clap"), (15.4, "rest")]
boy.arms += [(11.0, "rest"), (13.6, "catch"), (15.25, "rest")]
small.arms += [(11.4, "rest"), (17.75, "flail"), (19.0, "rest")]
boy.act.look(15.3, S_SPOT)
boy.kick += [(15.75, 0.0), (16.1, 1.0)]
boy.kick_w += [(15.6, 0.0), (15.8, 1.0), (16.2, 1.0), (16.5, 0.0)]
small.kick += [(17.35, 0.0), (17.75, 1.0)]
small.kick_w += [(17.2, 0.0), (17.4, 1.0), (17.8, 1.0), (17.95, 0.0)]
small.fall += [(17.85, 0.0), (18.15, 1.0), (19.0, 1.0), (19.5, 0.0)]
small.expr += [(17.3, (0.25, 0.0)), (17.9, (1.0, 0.0)), (19.0, (0.5, 0.0))]
girl.expr += [(13.0, (1.0, 0.0)), (14.2, (1.1, 1.0)), (15.2, (0.55, 0.0))]
boy.expr += [(14.2, (1.0, 1.0)), (15.0, (0.55, 0.0))]

# ---------------------------------------------------------------- ball (keyed by events, below)
# dog chases, ball bounces into the pond (18 - 24 s)
dog.act.move(18.0, 19.9, D_SPOT, (1.2, 1.4), (-0.6, 3.35))
girl.act.move(19.6, 21.6, G_SPOT, (-1.8, 1.9), EDGE["girl"])
boy.act.move(19.4, 21.3, B_SPOT, (1.2, 2.4), EDGE["boy"])
small.act.move(19.7, 21.8, S_SPOT, (-0.3, 0.9), EDGE["small"])
for k in KIDS:
    k.arms += [(19.4 + 0.2 * KIDS.index(k), "swing"), (21.6 + 0.2 * KIDS.index(k), "worry")]
    k.expr += [(21.0, (0.3, 0.0))]
    k.act.look(21.6, BALL_IN)
dog.act.look(19.9, BALL_IN)

# ---------------------------------------------------------------- 3. mother duck (0 - 31 s)
loop = [(S.POND.x + 1.7 * math.cos(a), S.POND.y + 1.1 * math.sin(a))
        for a in [math.radians(-50 + 30 * k) for k in range(14)]]
mom.act.move(-12.0, 23.5, *loop, accel=0.05)
p_end = mom.act.root_xy(23.5)
mom.act.move(23.6, 27.0, p_end, (p_end.x * 0.5 - 0.6, 5.6), (-0.76, 5.18))
mom.act.move(27.0, 30.4, (-0.76, 5.18), (-0.73, 4.0))
mom.quacks = [3.0, 9.5, 24.0, 27.2, 30.6, 34.0, 41.0, 52.5, 57.6]
for i, b in enumerate(babies):
    b.act.follow(mom.act, 0.36 + 0.27 * i)
    b.quacks = [q + 0.3 + 0.2 * i for q in mom.quacks[::2]]
for d in [mom] + babies:
    d.looks = [(0.0, None), (24.0, BALL_IN), (31.0, None)]

# ---------------------------------------------------------------- 4. dog takes the ball, cheering (30.4 - 35.5 s)
dog.bow = [(0.0, 0.0), (30.5, 0.0), (30.9, 1.0), (31.2, 1.0), (31.6, 0.0)]
dog.act.move(31.7, 32.7, (-0.6, 3.35), (0.0, 3.0), (0.45, 2.55))
dog.act.look(32.7, Vector((-0.4, 2.6, 0.5)))
for i, k in enumerate(KIDS):
    k.arms += [(31.1 + 0.1 * i, "up"), (33.2, "clap"), (35.0, "rest")]
    k.expr += [(31.0, (1.15, 1.0)), (33.5, (0.8, 0.0))]
    k.act.hop(31.25 + 0.08 * i, 31.75 + 0.08 * i, 0.16).hop(31.9 + 0.08 * i, 32.4 + 0.08 * i, 0.12)
    k.act.look(31.0, Vector((-0.3, 3.2, 0.3)))

# ---------------------------------------------------------------- 5. parade (35.5 - 50 s)
mom.act.move(35.5, 46.0, (-0.73, 4.0), (-0.9, 2.9), (-2.0, 1.4), (-1.2, -0.2), (0.6, -0.3), (1.5, 1.0), (0.8, 2.3))
LOOPK = [(-1.6, 2.3), (-2.25, 1.1), (-1.45, -0.4), (0.3, -0.7), (1.4, 0.15)]
for i, (k, t0, dur) in enumerate(((girl, 38.8, 8.5), (boy, 39.6, 8.5), (small, 41.6, 8.0))):
    k.act.move(t0, t0 + dur, EDGE[k.name], *LOOPK, SIT[k.name])
    k.arms += [(t0 - 0.1, "march"), (t0 + dur + 0.1, "rest")]
    k.act.lift_scale = [(0, 1.0), (t0, 1.0), (t0 + 0.4, 2.2), (t0 + dur - 0.5, 2.2), (t0 + dur, 1.0)]
    k.expr += [(t0, (0.9, 0.0))]
    k.act.look(t0 + dur, Vector((CAM_END[0], CAM_END[1], 0)))
    k.sit = [(0.0, 0.0), (t0 + dur + 0.3, 0.0), (t0 + dur + 0.9, 1.0)]
    k.arms += [(t0 + dur + 0.5, "sit")]
dog.act.move(42.6, 50.2, (0.45, 2.55), *LOOPK, SIT["dog"])
dog.act.look(50.2, Vector((0.25, -2.0, 0)))
dog.sit = [(0.0, 0.0), (50.3, 0.0), (50.7, 1.0)]
DROP = 50.9                       # puts the ball down between his paws
dog.bow += [(DROP - 0.3, 0.0), (DROP, 0.6), (DROP + 0.3, 0.0)]
for k in KIDS:
    k.act.look(35.5, lambda t: mom.act.root_xy(t))

# ---------------------------------------------------------------- 6. butterfly, sneeze, laugh, wave (50 - 60 s)
SNEEZE = 54.2
dog.sneeze = [SNEEZE]
dog.cross = [(0.0, 0.0), (51.6, 0.0), (51.9, 1.0), (SNEEZE - 0.1, 1.0), (SNEEZE + 0.2, 0.0)]
for i, k in enumerate(KIDS):
    k.act.look(50.5, Vector((0.25, 0.3, 0.3)))
girl.arms += [(SNEEZE + 0.2, "catch"), (SNEEZE + 1.0, "hold"), (56.0, "laugh"), (57.6, "wave")]
boy.arms += [(SNEEZE + 0.5, "laugh"), (57.7, "wave")]
small.arms += [(SNEEZE + 0.5, "laugh"), (57.8, "wave")]
for k in KIDS:
    k.laugh = [(0.0, 0.0), (SNEEZE + 0.6, 0.0), (SNEEZE + 0.9, 1.0), (57.2, 1.0), (57.6, 0.0)]
    k.expr += [(SNEEZE + 0.5, (1.2, 1.0)), (57.4, (0.9, 0.0))]
    k.act.look(SNEEZE + 0.2, Vector((0.25, 0.2, 0.4)))
    k.act.look(57.4, Vector((0.25, -4.0, 0.9)))
dog.act.look(57.4, Vector((0.25, -4.0, 0.6)))
dog.tail = [(0.0, 1.0), (51.6, 1.0), (52.0, 0.2), (SNEEZE + 0.3, 1.4)]

# ======================================================================================  precompute motion
CUR = [0]
mom.act.precompute(T).build_trail(-12.0, T)
for a in [girl, boy, small, dog] + babies:
    a.act.precompute(T)

# ======================================================================================  ball
BR = 0.1
ball = L.empty("ball")
L.blob("ball_a", (0, 0, 0), (BR, BR, BR), L.toon("ball_r", "#ff3b3b"), parent=ball, lw=0.008, half=True)
L.blob("ball_b", (0, 0, 0), (BR, BR, BR), L.toon("ball_w", "#ffffff"), parent=ball, rot=(math.pi, 0, 0),
       half=True, lw=0.008)
L.blob("ball_band", (0, 0, 0), (BR * 1.01, BR * 1.01, 0.012), L.toon("ball_y", "#ffd23f"), parent=ball,
       line=False)
ball_sh = L.blob("ball_shadow", (0, 0, 0), (0.09, 0.09, 0.003), L.flat("shadow", "#5aa63a"), line=False, seg=20)
splash = [L.blob("drop%d" % i, (0, 0, -5), (0.03, 0.03, 0.04), L.toon("drop", "#bfe9ff"), lw=0.006, seg=12)
          for i in range(10)]
splash_ring = [L.ring("splash_ring%d" % i, L.flat("ripple", "#c9eeff")) for i in range(2)]


def arc(a, b, u, h):
    p = a.lerp(b, u)
    p.z += 4 * h * u * (1 - u)
    return p


def frame_of(t):
    return max(0, min(NF, int(round(t * FPS))))


def kid_front(k, f, d=0.24):
    a = k.act
    return a.pos[f] + L.fwd(a.yaw[f]) * d * k.k + Vector((0, 0, BR))


def ball_state(t):
    """World position of the ball + whether it rolls (for spin)."""
    f = frame_of(t)
    hands = lambda k: (k.hand_world[1] + k.hand_world[-1]) * 0.5 + L.fwd(k.act.yaw[f]) * 0.05 * k.k
    if t < 13.0:
        return hands(girl), False
    if t < 14.2:
        a = Vector(BALL_KEY["release"])
        b = Vector(BALL_KEY["catch"])
        return arc(a, b, (t - 13.0) / 1.2, 0.9), False
    if t < 15.35:
        return hands(boy), False
    p_drop = kid_front(boy, frame_of(15.6), 0.26)
    if t < 15.6:
        a = Vector(BALL_KEY["boy_hold"])
        u = (t - 15.35) / 0.25
        return a.lerp(p_drop, u) + Vector((0, 0, -0.0 * u)), False
    p_s = kid_front(small, frame_of(16.95), 0.27)
    if t < 16.05:
        return p_drop, False
    if t < 16.95:
        u = L.ease((t - 16.05) / 0.9) * 0.6 + 0.4 * (t - 16.05) / 0.9
        return p_drop.lerp(p_s, u) + Vector((0, 0, 0.05 * abs(math.sin(u * math.pi * 2)))), True
    if t < 17.75:
        return p_s, False
    land1, land2 = Vector((-0.5, 2.8, BR)), Vector((-0.7, 4.0, BR))
    if t < 19.0:
        return arc(p_s, land1, (t - 17.75) / 1.25, 2.1), True
    if t < 19.6:
        return arc(land1, land2, (t - 19.0) / 0.6, 0.45), True
    wat = Vector((BALL_IN.x, BALL_IN.y, 0.06))
    if t < 20.2:
        return arc(land2, wat, (t - 19.6) / 0.6, 0.22), True
    if t < 27.0:
        return wat + Vector((0, 0, 0.012 * math.sin(t * 3.1))), False
    if t < 30.4:
        fm = frame_of(t)
        return mom.act.pos[fm] + L.fwd(mom.act.yaw[fm]) * 0.3 + Vector((0, 0, 0.06 + 0.01 * math.sin(t * 3))), True
    p_shore = BALL_KEY["shore"]
    if t < 30.95:
        return Vector(p_shore), False
    if t < DROP:
        return dog.mouth_world.copy(), False
    fd = frame_of(DROP + 0.4)
    paws = dog.act.pos[fd] + L.fwd(dog.act.yaw[fd]) * 0.3 + Vector((0, 0, BR))
    if t < DROP + 0.4:
        return Vector(BALL_KEY["drop"]).lerp(paws, L.ease((t - DROP) / 0.4)), False
    if t < SNEEZE + 0.05:
        return paws, False
    if t < SNEEZE + 0.75:
        return arc(paws, Vector(BALL_KEY["girl_sit"]), (t - SNEEZE - 0.05) / 0.7, 0.7), True
    return hands(girl), False


BALL_KEY = {}
EVENTS = []
_spin = [0.0, Vector()]


def prepass():
    """Positions where the ball changes hands (from the posed rigs) and the rolling spin of every frame."""
    keys = (("release", 13.0, lambda: (girl.hand_world[1] + girl.hand_world[-1]) * 0.5),
            ("catch", 14.2, lambda: (boy.hand_world[1] + boy.hand_world[-1]) * 0.5),
            ("boy_hold", 15.35, lambda: (boy.hand_world[1] + boy.hand_world[-1]) * 0.5),
            ("drop", DROP, lambda: dog.mouth_world.copy()),
            ("girl_sit", SNEEZE + 0.75, lambda: (girl.hand_world[1] + girl.hand_world[-1]) * 0.5))
    for key, tt, fn in keys:
        f = frame_of(tt)
        for k in KIDS:
            k.pose(f)
        dog.pose(f)
        bpy.context.view_layer.update()
        BALL_KEY[key] = tuple(fn())
    fm = frame_of(30.4)
    BALL_KEY["shore"] = tuple(mom.act.pos[fm] + L.fwd(mom.act.yaw[fm]) * 0.3 + Vector((0, 0, 0.06)))
    spin, prev = 0.0, None
    for f in range(NF + 1):
        p, rolling = ball_state(f / FPS)
        if rolling and prev is not None:
            spin += (p - prev).length / BR
        prev = p
        SPIN.append(spin)


SPIN = []


def pose_all(f):
    CUR[0] = f
    t = f / FPS
    for k in KIDS:
        k.pose(f)
    dog.pose(f)
    mom.pose(f)
    for b in babies:
        b.pose(f)
    bpy.context.view_layer.update()
    p, rolling = ball_state(t)
    ball.location = p
    ball.rotation_euler = (SPIN[f] if f < len(SPIN) else 0.0, 0.3, 0.2)
    over_water = S.in_pond(p)
    ball_sh.hide_render = over_water or p.z > 1.5
    ball_sh.location = (p.x, p.y, 0.005)
    s = max(0.3, 1 - (p.z - BR) * 0.6)
    ball_sh.scale = (s, s, 1)
    # splash at 20.2 s
    for i, dr in enumerate(splash):
        u = (t - 20.2) / 0.7
        if 0 <= u < 1:
            a = 2 * math.pi * i / len(splash)
            r = 0.1 + 0.35 * u
            dr.location = (BALL_IN.x + r * math.cos(a), BALL_IN.y + r * math.sin(a) * 0.8,
                           0.03 + 1.4 * u * (1 - u) * (0.7 + 0.3 * (i % 3)))
            dr.hide_render = False
        else:
            dr.hide_render = True
    for i, rg in enumerate(splash_ring):
        u = (t - 20.2 - 0.25 * i) / 1.6
        rg.hide_render = not (0 <= u < 1)
        rg.location = (BALL_IN.x, BALL_IN.y, 0.022)
        rr = 0.15 + 0.9 * u
        rg.scale = (rr, rr, 1)


# ======================================================================================  butterflies
FLY = []
for i, col in enumerate(("#ff7ad9", "#ffb13b", "#8f7bff")):
    root = L.empty("bfly%d" % i)
    L.blob("bfly_b%d" % i, (0, 0, 0), (0.01, 0.035, 0.01), L.flat("eyeblack", "#2a1d1a"), parent=root, line=False)
    wings = []
    for s in (-1, 1):
        piv = L.empty("bfly_p%d%d" % (i, s), root)
        L.blob("bfly_w%d%d" % (i, s), (s * 0.045, -0.01, 0), (0.045, 0.035, 0.004), L.toon("bw%d" % i, col),
               parent=piv, lw=0.004)
        L.blob("bfly_v%d%d" % (i, s), (s * 0.035, 0.03, 0), (0.03, 0.025, 0.004), L.toon("bw%d" % i, col),
               parent=piv, lw=0.004)
        wings.append((s, piv))
    FLY.append((root, wings))


def fly_pos(i, t):
    if i == 0:
        nose = dog.nose_world + Vector((0, 0.0, 0.02))
        wander = Vector((0.9 + 0.5 * math.sin(t * 0.9), -0.4 + 0.4 * math.sin(t * 1.3), 0.9 + 0.2 * math.sin(t * 2)))
        if t < 50.0:
            return Vector((-3 + 0.8 * math.sin(t * 0.7), 3 + 0.6 * math.cos(t * 0.5), 1.0 + 0.3 * math.sin(t * 1.7))), True
        if t < 51.5:
            u = L.ease((t - 50.0) / 1.5)
            a = Vector((-3 + 0.8 * math.sin(50 * 0.7), 3 + 0.6 * math.cos(25), 1.0)) .lerp(nose + Vector((0.3, -0.3, 0.3)), u)
            return a, True
        if t < 51.9:
            return (nose + Vector((0.3, -0.3, 0.3))).lerp(nose, L.ease((t - 51.5) / 0.4)), True
        if t < SNEEZE:
            return nose, False
        u = (t - SNEEZE) / 2.5
        return nose + Vector((1.5 * u, -0.6 * u, 1.6 * u + 0.2 * math.sin(u * 12))), True
    c = [Vector((-4, 4, 1.2)), Vector((3.5, 3, 1.0)), Vector((-2.5, -1.5, 1.1))][i]
    return c + Vector((1.2 * math.sin(t * 0.6 + i), 0.9 * math.cos(t * 0.45 + i * 2), 0.3 * math.sin(t * 1.9 + i))), True


def pose_flies(f):
    t = f / FPS
    for i, (root, wings) in enumerate(FLY):
        p, flying = fly_pos(i, t)
        p2, _ = fly_pos(i, t + 0.05)
        root.location = p
        d = p2 - p
        if d.length > 1e-4:
            root.rotation_euler = (0, 0, L.yaw_of(d) + math.pi)
        flap = 0.9 * math.sin(t * 40 + i) if flying else 0.5 + 0.2 * math.sin(t * 4)
        for s, piv in wings:
            piv.rotation_euler = (0, s * flap, 0)


# ======================================================================================  cameras
cam = bpy.data.cameras.new("cam")
cam.clip_end = 200
cam.clip_start = 0.05
co = bpy.data.objects.new("cam", cam)
sc.collection.objects.link(co)
sc.camera = co

SHOTS = [  # (t0, t1, [from keys], [look keys], lens)
    (0.0, 5.0, [(-5.6, -2.2, 2.4), (-4.6, -1.6, 2.1)], [(0.0, 5.6, 0.2), (0.4, 5.4, 0.3)], 24),
    (5.0, 11.4, [(8.8, -7.6, 1.3), (2.2, -6.6, 1.4)], [(9.3, -3.0, 0.55), (0.6, -0.4, 0.55)], 26),
    (11.4, 16.3, [(-0.2, -4.1, 1.25), (-0.1, -4.0, 1.25)], [(0.2, 0.4, 0.55), (0.3, 0.3, 0.55)], 24),
    (16.3, 19.0, [(-1.9, -3.4, 0.6), (-1.7, -3.2, 0.85)], [(0.3, -0.9, 0.4), (0.0, 1.2, 1.3)], 22),
    (19.0, 24.0, [(-2.4, 6.9, 1.1), (-2.2, 6.7, 1.1)], [(-0.6, 3.4, 0.45), (-0.6, 3.3, 0.45)], 22),
    (24.0, 30.4, [(2.3, 5.7, 0.85), (2.0, 5.3, 0.8)], [(-0.7, 4.9, 0.3), (-0.7, 4.0, 0.3)], 24),
    (30.4, 35.5, [(-0.4, 7.9, 1.6), (-0.3, 7.7, 1.55)], [(-0.5, 2.8, 0.5), (-0.4, 2.7, 0.5)], 20),
    (35.5, 47.0, [(0.3, -6.6, 4.2), (3.5, -5.2, 3.6)], [(-0.3, 1.2, 0.2), (0.0, 1.0, 0.3)], 20),
    (47.0, 55.0, [(0.25, -2.6, 0.8), (0.25, -2.45, 0.78)], [(0.25, 0.8, 0.45), (0.25, 0.8, 0.42)], 24),
    (55.0, 60.0, [(0.25, -2.8, 0.9), (0.25, -6.0, 2.4)], [(0.25, 0.9, 0.5), (0.25, 0.9, 0.5)], 24),
]


def pose_cam(f):
    t = f / FPS
    for t0, t1, fr, lk, lens in SHOTS:
        if t0 <= t < t1 or (t >= t1 and t1 == SHOTS[-1][1]):
            u = (t - t0) / (t1 - t0)
            a = Vector(L.track([(0, fr[0]), (1, fr[-1])], u, fn=lambda x: L.ease(x) * 0.5 + x * 0.5))
            b = Vector(L.track([(0, lk[0]), (1, lk[-1])], u, fn=lambda x: L.ease(x) * 0.5 + x * 0.5))
            co.location = a
            co.rotation_euler = (b - a).to_track_quat("-Z", "Y").to_euler()
            cam.lens = lens
            return


def shot_cuts():
    return [int(round(s[0] * FPS)) for s in SHOTS[1:]]


def pose(f):
    pose_all(f)
    pose_flies(f)
    pose_cam(f)
    bpy.context.view_layer.update()


# ======================================================================================  run
def check():
    bad = []
    for a in [girl, boy, small, dog, mom] + babies:
        bad += a.act.check_feet()
    pops = []
    cuts = set(shot_cuts())
    for a in [girl, boy, small, dog, mom] + babies:
        for f in range(1, len(a.act.pos)):
            if (a.act.pos[f] - a.act.pos[f - 1]).length > 0.25:
                pops.append((a.name, f))
            if abs(L.wrap(a.act.yaw[f] - a.act.yaw[f - 1])) > 0.5:
                pops.append((a.name + "_yaw", f))
    print("FEET_SLIDE", len(bad), bad[:20])
    print("POPS", len(pops), pops[:20])
    print("CLEAN" if not bad and not pops else "NOT CLEAN")


def render_frames(frames, outdir, res=100, samples=12, skip=True):
    os.makedirs(outdir, exist_ok=True)
    sc.render.resolution_percentage = res
    sc.eevee.taa_render_samples = samples
    for f in frames:
        path = os.path.join(outdir, "f_%04d.png" % f)
        if skip and os.path.exists(path) and os.path.getsize(path) > 0:
            continue
        pose(f)
        sc.render.filepath = path
        bpy.ops.render.render(write_still=True)
        print("FRAME", f, flush=True)


def dump_events():
    """Foot landings (for patter sounds) + timed story sounds -> events.json (read by sound.py)."""
    ev = {"steps": [], "SNEEZE": SNEEZE, "DROP": DROP, "quacks": [], "barks": []}
    for a, kind in [(girl, "kid"), (boy, "kid"), (small, "kid"), (dog, "dog"), (mom, "duck")] + \
                   [(b, "baby") for b in babies]:
        for j in range(len(a.act.feet)):
            lf = a.act.footlift[j]
            for f in range(1, len(lf)):
                if lf[f - 1] > 0.004 and lf[f] <= 0.002:
                    p = a.act.footp[j][f]
                    if kind in ("duck", "baby") and S.in_pond(p):
                        continue
                    ev["steps"].append((round(f / FPS, 3), kind, a.name))
    ev["quacks"] = [(q, "mom") for q in mom.quacks] + [(q, b.name) for b in babies for q in b.quacks]
    json.dump(ev, open(os.path.join(HERE, "events.json"), "w"))
    print("EVENTS", len(ev["steps"]))


prepass()
if "--check" in argv:
    check()
    dump_events()
elif "--preview" in argv:
    step = int(argv[argv.index("--preview") + 1]) if len(argv) > argv.index("--preview") + 1 else 2
    render_frames(list(range(0, NF, step)), os.path.join(HERE, "preview"), res=34, samples=1)
elif "--still" in argv:
    fr = [int(x) for x in argv[argv.index("--still") + 1].split(",")]
    render_frames(fr, os.path.join(HERE, "test"), res=100, samples=12, skip=False)
elif "--render" in argv:
    i = argv.index("--render")
    a, b = int(argv[i + 1]), int(argv[i + 2])
    render_frames(list(range(a, b + 1)), os.path.join(HERE, "frames"))
print("DONE", flush=True)
