"""
«واگن آخر ۲ — برگشت» — sequences 3-4, 27-56 s, outside: we jump down from our train,
run to the lone wagon on its siding, open the stuck door, find grandma, and bring her back.

Same world coordinates as part_wagon.py at the moment the train stands still, but with the
ground at z=0 (our car's floor is at z=1.3).  Our train leaves again at 52.5 s.

    python part_field.py --still 700,900
    python part_field.py --render --range 649 1344
"""

import math
import os
import random
import sys

import bpy
from mathutils import Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403,E402
from part_wagon import S_STOP, travelled  # noqa: E402

T0, T1 = 27.0, 56.0
F0, F1 = int(T0 * FPS) + 1, int(T1 * FPS)
random.seed(31)

LX = -9.0          # lone wagon track
LY = -14.0         # lone wagon centre
LDOOR = LY + 2.0   # its door (y)
ODOOR = -11.3      # our car's door (y), on the -X side
FZ = FLOOR_Z       # wagon floor height
EYE = 1.55


def train_y(t):
    return travelled(t) - S_STOP


# ================================================================ world


def build_world():
    dirt = toon("Field dirt", (0.5, 0.38, 0.27), 0.18)
    box((0, 0, -0.05), (400, 400, 0.1), dirt, "Ground")
    cols = [toon("Burnt a", (0.28, 0.22, 0.18), 0.12), toon("Field b", (0.8, 0.68, 0.3), 0.18),
            toon("Burnt b", (0.2, 0.17, 0.15), 0.1), toon("Field c", (0.45, 0.55, 0.25), 0.18)]
    for k in range(-6, 8):
        for sx, x in ((-1, -48), (1, 45)):
            box((x, k * 16, 0.01), (70, 15, 0.06), cols[(k + (sx > 0)) % 4], "Field strip")
    for p in rails(0, -60, 90, 0) + rails(LX, -60, 30, 0, "Siding"):
        pass
    # burnt grass tufts between the tracks
    tuft = [toon("Tuft", (0.42, 0.38, 0.22), 0.15), toon("Tuft dark", (0.25, 0.2, 0.15), 0.1)]
    for i in range(70):
        x = random.uniform(-20, 12)
        if abs(x) < 2.2 or abs(x - LX) < 2.2:
            continue
        box((x, random.uniform(-30, 20), 0.08), (random.uniform(0.3, 0.8), random.uniform(0.3, 0.8), 0.16),
            random.choice(tuft), "Tuft", bevel=0.05)
    pole_m = toon("Pole", (0.32, 0.22, 0.15), 0.15)
    leaf = [toon("Tree a", (0.25, 0.45, 0.22), 0.15), toon("Tree dead", (0.22, 0.18, 0.15), 0.1)]
    for y in range(-60, 100, 24):
        rod((6, y, 0), (6, y, 8.3), 0.15, pole_m, "Power pole")
        box((6, y, 7.8), (1.6, 0.12, 0.12), pole_m, "Pole arm")
    for i in range(40):
        x = random.choice([-1, 1]) * random.uniform(16, 70)
        y = random.uniform(-80, 80)
        rod((x, y, 0), (x, y, 2.6), 0.22, pole_m, "Trunk")
        ball((x, y, 4.2), random.uniform(1.6, 2.6), random.choice(leaf), "Crown")
    fire = glow_mat("Fire", (1.0, 0.45, 0.08), 6.0)
    smoke = [toon("Smoke", (0.22, 0.21, 0.22), 0.12), toon("Smoke light", (0.36, 0.34, 0.34), 0.12)]
    for (x, y) in [(-45, -30), (-60, 20), (40, -45), (-35, 50), (55, 30), (-25, -70)]:
        ball((x, y, 0.5), 1.4, fire, "Field fire", scale=(1.6, 1.6, 0.7))
        for k in range(11):
            ball((x + k * 0.9, y + random.uniform(-1, 1), 2 + k * 3.0), 1.6 + k * 0.6, random.choice(smoke),
                 "Smoke puff", seg=14)
    # distant hills against the dusk sky
    hill = toon("Hill", (0.45, 0.32, 0.38), 0.25)
    for k in range(12):
        a = D(k * 30)
        ball((math.cos(a) * 160, math.sin(a) * 160, -10), random.uniform(25, 40), hill, "Hill",
             scale=(1.6, 1.6, 0.6), seg=16)


def build_lone_wagon():
    parts, doors = wagon_exterior("Lone", LX, LY - 9, LY + 9, 0, +1, [LDOOR], burnt=1.0)
    door, win = doors[0]
    inner_seat = toon("Seat", (0.15, 0.22, 0.5), 0.12)
    metal = toon("Car metal", (0.55, 0.58, 0.62), 0.12)
    # long bench against the far wall, a few seat rows, luggage on the floor
    box((LX - 0.95, LY, FZ + 0.44), (0.5, 14, 0.12), inner_seat, "Bench", bevel=0.04)
    box((LX - 0.95, LY, FZ + 0.2), (0.4, 14, 0.38), metal, "Bench base")
    box((LX - 1.3, LY, FZ + 0.85), (0.12, 14, 0.85), inner_seat, "Bench back", bevel=0.04)
    for c in (-6, -3, 3, 6):
        box((LX + 0.6, LY + c, FZ + 0.44), (0.9, 0.5, 0.12), inner_seat, "Seat", bevel=0.04)
        box((LX + 0.6, LY + c - 0.26, FZ + 0.85), (0.9, 0.12, 0.85), inner_seat, "Seat back", bevel=0.04)
    bag_c = [(0.85, 0.2, 0.2), (0.2, 0.45, 0.85), (0.95, 0.7, 0.1), (0.3, 0.65, 0.3), (0.6, 0.3, 0.7)]
    for k in range(7):
        c = bag_c[k % 5]
        b = box((LX + random.uniform(-0.6, 0.6), LY + random.uniform(-6, 6), FZ + 0.15),
                (0.45, random.uniform(0.3, 0.6), 0.3), toon(f"Bag {c}", c), "Bag", bevel=0.05)
        b.name = "Lone bag"
    # grandma's little lantern on the floor
    lantern = ball((LX - 0.55, LDOOR - 1.1, FZ + 0.15), 0.1, glow_mat("Lantern", (1.0, 0.75, 0.35), 6.0),
                   "Lantern", scale=(1, 1, 1.3))
    bpy.ops.object.light_add(type="POINT", location=(LX - 0.3, LDOOR - 0.8, FZ + 1.2))
    no_cam(bpy.context.object)
    bpy.context.object.data.energy = 70
    bpy.context.object.data.color = (1.0, 0.7, 0.4)
    bpy.context.object.data.shadow_soft_size = 0.4
    return door, win


def build_our_train():
    root = empty("Our train")
    for i, (y0, y1) in enumerate(((-13, 13), (13.6, 39.6), (40.2, 66.2))):
        parts, doors = wagon_exterior(f"Car{i}", 0, y0, y1, 0, -1, [ODOOR] if i == 0 else [y0 + 2.2, y1 - 2.2],
                                      panels=False)
        for p in parts:
            parent_keep(p, root)
    # the vestibule: partition with the inner door, handrails, warm lamp
    inner = toon("Train inside", (0.75, 0.62, 0.45), 0.1)
    pole_m = toon("Handrail", (0.95, 0.75, 0.1), 0.4)
    for py in (ODOOR - 0.95, ODOOR + 0.95):
        parent_keep(box((0, py, FZ + 1.3), (3.0, 0.08, 2.6), inner, "Partition"), root)
    parent_keep(box((0.2, ODOOR + 0.9, FZ + 1.05), (0.8, 0.04, 2.0), toon("Inner door", (0.42, 0.45, 0.5)),
                    "Inner door"), root)
    for py in (ODOOR - 0.57, ODOOR + 0.57):
        parent_keep(rod((-1.3, py, FZ + 0.1), (-1.3, py, FZ + 2.1), 0.03, pole_m, "Handrail"), root)
    bpy.ops.object.light_add(type="POINT", location=(0.2, ODOOR, FZ + 1.5))
    lamp = no_cam(bpy.context.object)
    lamp.data.energy = 20
    lamp.data.color = (1, 0.9, 0.75)
    parent_keep(lamp, root)
    return root


def build_jet():
    grey = toon("Jet", (0.45, 0.48, 0.52), 0.15)
    jet = empty("Jet")
    for p in [rod((0, -3, 0), (0, 3, 0), 0.6, grey, "Jet body"), ball((0, 3.1, 0), 0.6, grey, "Jet nose",
                                                                       scale=(1, 1.8, 1)),
              box((0, 0, 0), (7, 1.8, 0.15), grey, "Jet wing"), box((0, -2.6, 0.9), (0.15, 1.2, 1.6), grey, "Jet tail")]:
        parent_keep(p, jet)
    return jet


# ================================================================ animation


def walk_path(t):
    """Where the three of us walk back (46.4-49.0): along the line lone door -> our door."""
    a = Vector((-6.4, LDOOR - 0.4, 0))
    b = Vector((-2.6, ODOOR + 0.3, 0))
    return a.lerp(b, seg(t, 46.4, 49.0)), (b - a).normalized()


def yaw_of(d):
    """Camera / body yaw (degrees, 0 = +Y) that looks along direction d."""
    return math.degrees(math.atan2(-d.x, d.y))


def build():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.fps = FPS
    scene.frame_start, scene.frame_end = F0, F1

    build_world()
    door, door_win = build_lone_wagon()
    train = build_our_train()
    jet = build_jet()
    blast = ball((30, -40, 9), 1.0, glow_mat("Blast", (1.0, 0.55, 0.12), 14.0), "Blast")
    blast_smoke = ball((30, -40, 12), 1.0, toon("Blast smoke", (0.25, 0.23, 0.24), 0.1), "Blast smoke")

    rahim, jalal, grandma = make_rahim(), make_jalal(), make_grandma()
    gm_bunny = bunny(grandma.hand_world("R") + Vector((0.0, 0.08, 0.06)), grandma.p["elbowR"], "Grandma bunny")

    cam = make_camera(scene)
    arms = POVArms(cam)
    pb_root = pov_bunny(cam)
    pb_parts = [o for o in bpy.data.objects if o.name.startswith("POV bunny ")]

    rnd = random.Random(9)
    shake = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(-1, 1)) for _ in range(F1 + 3)]
    door_rest = door.location.copy()
    win_rest = door_win.location.copy()
    vest = Vector((-0.85, ODOOR, FZ + EYE))       # standing in our vestibule
    gm_seat = Vector((LX - 0.75, LDOOR - 0.4, FZ))

    for f in range(F0, F1 + 1):
        t = (f - 1) / FPS
        ty = train_y(t)
        train.location.y = ty
        train.keyframe_insert("location", frame=f)
        tv = Vector((0, ty, 0))

        # ---------------- lone wagon door: stuck, then slides open (towards -Y)
        k = seg(t, 33.0, 33.8)
        jam = 0.03 * math.sin(t * 40) * (31.9 < t < 33.0)
        door.location = door_rest + Vector((0, -1.3 * k + jam, 0))
        door_win.location = win_rest + Vector((0, -1.3 * k + jam, 0))
        for o in (door, door_win):
            o.keyframe_insert("location", frame=f)

        # ---------------- jet and the far explosion
        jt = seg(t, 46.7, 47.5)
        jet.location = (lerp(-90, 90, jt), lerp(-30, -50, jt), 26 - 4 * jt) if t > 46.3 else (0, 0, -50)
        jet.rotation_euler = (0, D(-20), D(-95))
        jet.keyframe_insert("location", frame=f)
        jet.keyframe_insert("rotation_euler", frame=f)
        bf = max(0.0, 1 - abs(t - 47.7) / 0.6)
        blast.scale = (0.001 + 9 * bf,) * 3
        blast.keyframe_insert("scale", frame=f)
        sm = seg(t, 47.6, 50.0)
        blast_smoke.scale = (0.001 + 8 * sm, 0.001 + 8 * sm, 0.001 + 12 * sm)
        blast_smoke.location = (30, -40, 9 + 10 * sm)
        blast_smoke.keyframe_insert("scale", frame=f)
        blast_smoke.keyframe_insert("location", frame=f)

        # ---------------- camera path
        bob = 0.0
        if t < 27.6:                                   # in the doorway, looking down at the gravel
            pos, yaw, pitch = Vector((-1.15, ODOOR - 0.1, FZ + EYE)), 90, -22
        elif t < 28.0:                                 # jump down
            u = seg(t, 27.6, 28.0)
            a, b = Vector((-1.15, ODOOR - 0.1, FZ + EYE)), Vector((-2.4, ODOOR + 0.3, EYE))
            pos = a.lerp(b, u) + Vector((0, 0, 0.35 * math.sin(math.pi * u)))
            yaw, pitch = lerp(90, 84, u), lerp(-22, -5, u)
        elif t < 30.0:                                 # run to the lone wagon
            u = seg(t, 28.0, 29.9)
            a, b = Vector((-2.4, ODOOR + 0.3, EYE)), Vector((-5.9, LDOOR, EYE))
            pos = a.lerp(b, u)
            bob = 0.06 * abs(math.sin(math.pi * t * 3.2)) * (1 - seg(t, 29.6, 30.0))
            yaw, pitch = lerp(84, 90, seg(t, 29.3, 30.0)), lerp(-2, 16, seg(t, 29.3, 30.0))
        elif t < 33.8:                                 # at the door, knocking, then pulling it open
            pos = Vector((-5.9, LDOOR, EYE))
            yaw, pitch = 90, 18
            yaw = lerp(yaw, 125, seg(t, 31.9, 32.3) * (1 - seg(t, 32.6, 32.9)))   # Jalal arrives (left)
            pitch = lerp(pitch, 6, seg(t, 33.0, 33.6))
        elif t < 34.5:                                 # climb in
            u = seg(t, 33.8, 34.5)
            pos = Vector((-5.9, LDOOR, EYE)).lerp(Vector((-8.05, LDOOR, FZ + EYE)), u)
            pos.z += 0.15 * math.sin(math.pi * u)
            yaw, pitch = 90, lerp(6, -16, u)
        elif t < 45.6:                                 # inside with grandma
            pos = Vector((-8.05, LDOOR, FZ + EYE))
            yaw, pitch = 96, -16
            back = seg(t, 39.5, 39.9) * (1 - seg(t, 41.1, 41.5))   # turn round to the door / Rahim
            yaw = lerp(yaw, 262, back); pitch = lerp(pitch, 2, back)
            pitch = lerp(pitch, -26, seg(t, 41.7, 42.1) * (1 - seg(t, 42.9, 43.2)))   # her leg
            pitch = lerp(pitch, -2, seg(t, 44.7, 45.5))                              # she stands up
        elif t < 46.4:                                 # step down after her
            u = seg(t, 45.6, 46.4)
            p_out, d = walk_path(46.4)
            pos = Vector((-8.05, LDOOR, FZ + EYE)).lerp(Vector((-6.1, LDOOR + 0.3, EYE)), u)
            yaw, pitch = lerp(96, 150, u), lerp(-2, -8, u)
        elif t < 49.0:                                 # walk back to our train, grandma in front-left
            p, d = walk_path(t)
            right = Vector((d.y, -d.x, 0))
            pos = Vector((p.x, p.y, EYE)) - d * 0.9 + right * 0.35
            bob = 0.03 * abs(math.sin(math.pi * t * 2.0))
            yaw, pitch = yaw_of(d) - 8, -8
            look_up = seg(t, 46.6, 46.9) * (1 - seg(t, 47.9, 48.3))
            yaw = lerp(yaw, yaw_of(d) - 35, look_up); pitch = lerp(pitch, 18, look_up)
        elif t < 50.6:                                 # Rahim pulls grandma up
            pos = Vector((-2.75, ODOOR + 0.6, EYE))
            yaw, pitch = 262, 14
        elif t < 51.3:                                 # we climb up
            u = seg(t, 50.6, 51.3)
            pos = Vector((-2.75, ODOOR + 0.6, EYE)).lerp(Vector((-1.2, ODOOR + 0.35, FZ + EYE)), u)
            pos.z += 0.12 * math.sin(math.pi * u)
            yaw, pitch = 262, lerp(14, -4, u)
        else:                                          # inside the vestibule, looking out of the door
            pos = Vector((-1.2, ODOOR + 0.35, FZ + EYE)) + tv
            yaw, pitch = lerp(262, 95, seg(t, 51.4, 52.2)), -4
            yaw = lerp(yaw, 128, seg(t, 53.3, 55.0))
        pos = pos + Vector((0, 0, bob))
        amp = 0.15 if 28.0 <= t < 29.9 else 0.04
        for te, kk in ((28.0, 3.0), (33.0, 1.2), (47.7, 2.2), (52.5, 1.0)):
            if te <= t < te + 0.5:
                amp += kk * (1 - (t - te) / 0.5)
        if t > 52.5:
            amp += 0.12 * seg(t, 52.5, 54)
        sx_, sy_, sz_ = shake[f]
        cam.location = pos
        cam.rotation_euler = (D(90 + pitch + sx_ * amp), D(sy_ * amp * 0.6), D(yaw + sz_ * amp))
        cam.keyframe_insert("location", frame=f)
        cam.keyframe_insert("rotation_euler", frame=f)

        # ---------------- Grandma
        if t < 44.8:
            hold = seg(t, 38.0, 38.4)
            leg = seg(t, 41.6, 41.9) * (1 - seg(t, 43.0, 43.3))
            take = seg(t, 36.8, 37.3) * (1 - seg(t, 37.5, 37.9))
            grandma.pose(f, t, gm_seat, facing=-90, sit=1, seat_h=0.5, lean=0,
                         look=(lerp(5, 0, hold) + 10 * leg, lerp(18, -5, hold) - 15 * leg),
                         reach=(lerp(lerp(30, 70, take), 50, hold), lerp(0, -15, hold)),
                         reach2=(lerp(25, 60, leg), -10) if leg > 0 else (lerp(20, 45, hold), 0),
                         hug=0.35 * hold * (1 - leg), worry=lerp(0.6, 1.4, leg))
        elif t < 46.4:
            u = seg(t, 45.0, 45.9)
            u2 = seg(t, 45.9, 46.4)
            gp = gm_seat.lerp(Vector((-7.6, LDOOR, FZ)), u).lerp(Vector((-5.6, LDOOR - 0.5, 0)), u2)
            grandma.pose(f, t, gp, facing=lerp(-90, -140, u), sit=1 - seg(t, 44.8, 45.5), seat_h=0.5,
                         run=0.3 * u, run_rate=1.0, lean=0, look=(0, -5), reach=(60, -20), worry=1.3)
        elif t < 49.3:
            p, d = walk_path(t)
            gp = p - Vector((d.y, -d.x, 0)) * 0.15
            grandma.pose(f, t, gp, facing=yaw_of(d), run=0.35 * (t < 48.9), run_rate=0.9, lean=-8,
                         look=(0, -5), reach=(30, -10), worry=1.4)
        elif t < 50.8:
            u = seg(t, 49.4, 50.4)
            gp = Vector((-2.0, ODOOR, 0)).lerp(Vector((-0.6, ODOOR - 0.2, FZ)), u)
            gp.z += 0.25 * math.sin(math.pi * u)
            grandma.pose(f, t, gp, facing=lerp(-90, 90, seg(t, 50.2, 50.6)), crouch=0.4 * math.sin(math.pi * u),
                         lean=0, reach=(120, 20), reach2=(100, -10), look=(0, 10), worry=1.4)
        else:
            grandma.pose(f, t, Vector((0.4, ODOOR + 3, FZ)) + tv, facing=0)
        show(gm_bunny, f, t >= 37.45)

        # ---------------- Jalal
        if t < 28.6:
            jalal.pose(f, t, Vector((0.5, ODOOR + 3, FZ)), facing=0)
        elif t < 32.2:
            u = seg(t, 28.6, 32.0)
            jp = Vector((-2.4, ODOOR - 0.4, 0)).lerp(Vector((-6.7, LDOOR + 0.75, 0)), u)
            jalal.pose(f, t, jp, facing=lerp(42, 90, seg(t, 31.5, 32.1)), run=1 - seg(t, 31.6, 32.1),
                       run_rate=1.6, look=(0, 10), worry=1.4)
        elif t < 45.5:
            pull = seg(t, 32.5, 32.9) * (1 - seg(t, 33.8, 34.2))
            sky = seg(t, 39.8, 40.3) * (1 - seg(t, 41.3, 41.8))
            jalal.pose(f, t, Vector((-6.7, LDOOR + 0.75, 0)), facing=lerp(90, 150, sky),
                       reach=(lerp(20, 100, pull), 0) if pull > 0 else None,
                       reach2=(lerp(20, 100, pull), 0) if pull > 0 else None,
                       look=(0, lerp(lerp(25, 0, pull), 30, sky)), worry=1.3 + 0.4 * sky, lean=0)
        elif t < 46.4:
            jalal.pose(f, t, Vector((-6.5, LDOOR - 0.4, 0)), facing=-150, reach=(100, 20), reach2=(100, -20),
                       look=(0, 15), worry=1.2)
        elif t < 51.3:
            p, d = walk_path(min(t, 49.0))
            jp = p - Vector((d.y, -d.x, 0)) * 0.75 - d * 0.2
            jalal.pose(f, t, jp, facing=yaw_of(d) if t < 49.0 else 270 - 360,
                       run=0.35 * (t < 48.9), run_rate=0.9, reach2=(60, -40), look=(0, 0), worry=1.3,
                       lean=0)
        elif t < 52.2:
            u = seg(t, 51.3, 52.1)
            jp = Vector((-2.4, ODOOR - 0.3, 0)).lerp(Vector((-0.7, ODOOR - 0.5, FZ)), u)
            jp.z += 0.2 * math.sin(math.pi * u)
            jalal.pose(f, t, jp + tv, facing=-90, crouch=0.4 * math.sin(math.pi * u), reach=(110, 0), look=(0, 5))
        else:
            jalal.pose(f, t, Vector((-0.5, ODOOR - 0.55, FZ)) + tv, facing=-120, look=(20, 0), worry=1.4,
                       reach2=(140, 0) if t < 53.5 else None)

        # ---------------- Rahim: in the doorway of our car
        rpos = Vector((-0.75, ODOOR + 0.6, FZ))
        if t < 51.4:
            lift = seg(t, 49.0, 49.4) * (1 - seg(t, 50.4, 50.8))
            rahim.pose(f, t, rpos, facing=90, look=(0, -10 + 25 * (39.6 < t < 41.4)),
                       wave=seg(t, 39.7, 39.9) * (1 - seg(t, 41.2, 41.4)),
                       reach=(lerp(20, 80, lift), 10) if lift > 0 else (lerp(20, 80, seg(t, 50.6, 50.9)), 10),
                       reach2=(lerp(20, 80, lift), -10) if lift > 0 else None, crouch=0.35 * lift,
                       worry=1.6, lean=0)
        else:
            rahim.pose(f, t, rpos + Vector((0.2, 0.15, 0)) + tv, facing=lerp(90, 130, seg(t, 51.4, 52.0)),
                       look=(0, 5), reach=(150, 10) if t < 52.5 else None, worry=1.3)

        # ---------------- POV hands and the bunny
        rest_L, rest_R = Vector((-0.28, -0.42, -0.46)), Vector((0.28, -0.42, -0.46))
        bunny_hand = Vector((-0.2, -0.34, -0.42))
        if t < 37.45:
            if 36.3 <= t:
                bl = bunny_hand.lerp(world_to_cam(cam, grandma.hand_world("R")) + Vector((0, 0, 0.06)),
                                     seg(t, 36.3, 37.2))
            else:
                bl = bunny_hand
            pb_root.location = bl
            pb_root.keyframe_insert("location", frame=f)
        show(pb_parts, f, t < 37.45)
        if t < 28.0:
            arms.set(f, "L", bunny_hand + Vector((0, 0, -0.07)))
            arms.set(f, "R", (0.3, -0.35, -0.38))                 # holding the handrail
        elif t < 30.0:
            sw = 0.09 * math.sin(2 * math.pi * t * 1.6)
            arms.set(f, "L", bunny_hand + Vector((0, sw, -0.07)))
            arms.set(f, "R", (0.3, -0.45 - sw, -0.42))
        elif t < 33.8:
            knock = abs(math.sin(math.pi * t * 4)) if (30.0 < t < 30.9 or 31.8 < t < 32.2) else 0
            pull = seg(t, 32.4, 32.8)
            r = Vector((0.18, -0.5 + 0.08 * knock, -0.05))
            r = r.lerp(Vector((-0.05, -0.55, -0.12)) + Vector((-0.5 * seg(t, 33.0, 33.8), 0.2 * seg(t, 33.0, 33.8), 0)), pull)
            arms.set(f, "R", r)
            arms.set(f, "L", bunny_hand + Vector((0, 0, -0.07)))
        elif t < 37.45:
            give = seg(t, 36.3, 37.2)
            arms.set(f, "L", (bunny_hand.lerp(world_to_cam(cam, grandma.hand_world("R")), give)
                              + Vector((0, 0, -0.07 * (1 - give)))))
            arms.set(f, "R", rest_R if t > 34.5 else (0.3, -0.35, -0.3))
        elif 44.6 <= t < 46.4:                          # help her up
            hw = world_to_cam(cam, grandma.hand_world("L"))
            arms.set(f, "R", Vector((0.25, -0.5, -0.3)).lerp(hw, seg(t, 44.6, 45.0)))
            arms.set(f, "L", rest_L)
        elif 46.4 <= t < 49.0:
            hw = world_to_cam(cam, grandma.p["shoulderR"].matrix_world.translation)
            arms.set(f, "L", hw + Vector((0.05, 0.05, 0)))
            arms.set(f, "R", rest_R)
        elif 50.6 <= t < 51.3:                          # grab the handrail and climb
            arms.set(f, "R", (0.2, -0.55, 0.0))
            arms.set(f, "L", (-0.1, -0.55, 0.05))
        else:
            arms.set(f, "L", rest_L)
            arms.set(f, "R", rest_R)

    bpy.ops.object.light_add(type="SUN", rotation=(D(72), D(10), D(-60)))
    sun = bpy.context.object
    sun.data.energy = 2.0
    sun.data.color = (1.0, 0.66, 0.45)
    setup_render(scene, sky=(0.86, 0.52, 0.4), sky_strength=0.7)
    scene.frame_set(F0)
    return scene


if __name__ == "__main__":
    run_cli(build(), "train_field.blend")
