"""
«واگن آخر ۲» — the whole episode (0-52 s) in one set: the border at dusk.

We kneel in the open door of our train, holding Lena's hand; she stands on the low platform.
The train starts rolling back (towards the last wagon, whose lights are still on far down the
track) and Lena walks, then trots, beside the door.  Mum is behind the border fence.

Rendered "on twos" (every second frame, 12 drawings a second, like hand-drawn cartoons);
post.py doubles the frames back to 24 fps.

    python part_door.py --still 49,361
    python part_door.py --render --range 1 1248
"""

import math
import os
import random
import sys

import bpy
from mathutils import Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403,E402
from captions import END  # noqa: E402

random.seed(42)
ODOOR = -11.3          # our door (y, on the -X side of the train)
FZ = FLOOR_Z           # train floor height
PLAT_Z = 0.6           # low platform at the border
LAST_Y = -82.0         # the last wagon, far down the track
KNEEL = 0.55           # eye height above the floor (sitting on the door step)


def speed(t):
    """Train speed in m/s (negative = rolling back)."""
    if t < 2.0:
        return 0.0
    if t < 35.0:
        return -0.4 * seg(t, 2.0, 6.0)
    return -lerp(lerp(0.4, 1.05, seg(t, 35.0, 39.0)), 1.6, seg(t, 50.0, 53.0))


_S = [0.0]
for _f in range(1, int(END * FPS) + 4):
    _S.append(_S[-1] + speed((_f - 1) / FPS) / FPS)


def train_y(t):
    return _S[max(0, min(len(_S) - 1, int(round(t * FPS))))]


# ================================================================ world


def build_world():
    dirt = toon("Field dirt", (0.42, 0.33, 0.27), 0.15)
    box((0, -40, -0.05), (400, 500, 0.1), dirt, "Ground")
    rails(0, -200, 80, 0)
    concrete = toon("Platform", (0.62, 0.6, 0.58), 0.15)
    edge = toon("Platform edge", (0.95, 0.8, 0.15), 0.35)
    box((-3.9, -35, PLAT_Z / 2), (4.3, 110, PLAT_Z), concrete, "Platform", bevel=0.03)
    box((-1.85, -35, PLAT_Z + 0.005), (0.12, 110, 0.01), edge, "Platform edge line")
    for y in range(-88, 20, 3):  # paving joints
        box((-3.9, y, PLAT_Z + 0.004), (4.3, 0.04, 0.01), toon("Joint", (0.5, 0.48, 0.47), 0.1), "Joint")
    # the border: fence, floodlights, barrier, hut, people behind the fence
    fence = toon("Fence", (0.55, 0.6, 0.62), 0.15)
    for k in range(-30, 12):
        rod((-8, k * 2.5, 0), (-8, k * 2.5, 2.9), 0.06, fence, "Fence post")
    for z in (1.0, 1.7, 2.4, 2.85):
        box((-8, -45, z), (0.03, 105, 0.03), fence, "Fence wire")
    lamp = glow_mat("Flood", (1.0, 0.95, 0.75), 9.0)
    for k in (-84, -60, -36, -12, 12):
        rod((-12, k, 0), (-12, k, 9.3), 0.2, fence, "Light tower")
        box((-11.6, k, 9.3), (0.6, 1.4, 0.7), lamp, "Floodlight")
    red_w = [toon("Barrier red", (0.9, 0.12, 0.1), 0.2), toon("Barrier white", (0.97, 0.97, 0.95), 0.3)]
    for k in range(8):
        box((-8.3, -14 + k * 0.6, 1.1), (0.25, 0.6, 0.25), red_w[k % 2], "Barrier")
    hut = toon("Hut", (0.35, 0.5, 0.3), 0.15)
    box((-15, -4, 1.5), (3, 3, 3), hut, "Guard hut")
    box((-15, -4, 3.15), (3.6, 3.6, 0.3), toon("Hut roof", (0.85, 0.3, 0.2), 0.15), "Hut roof")
    box((-13.48, -4, 1.9), (0.06, 1.4, 0.8), glow_mat("Hut window", (0.95, 0.85, 0.4), 2.0), "Hut window")
    crowd_c = [(0.85, 0.2, 0.2), (0.2, 0.45, 0.85), (0.95, 0.7, 0.1), (0.3, 0.65, 0.3), (0.6, 0.3, 0.7)]
    for k in range(30):
        c = crowd_c[k % 5]
        x, y = random.uniform(-22, -11), random.uniform(-30, 12)
        if abs(x + 15) < 2.5 and abs(y + 4) < 2.5:
            continue
        box((x, y, 0.6), (0.4, 0.3, 1.2), toon(f"Crowd {c}", c), "Crowd body", bevel=0.1)
        ball((x, y, 1.4), 0.2, toon("Crowd skin", (0.85, 0.62, 0.48)), "Crowd head")
    # far smoke and the glow of the burning city behind us (down the track)
    smoke = [toon("Smoke", (0.2, 0.19, 0.21), 0.1), toon("Smoke light", (0.32, 0.3, 0.32), 0.1)]
    fire = glow_mat("Fire", (1.0, 0.45, 0.08), 6.0)
    for (x, y) in [(-30, -150), (25, -170), (-55, -120), (40, -110)]:
        ball((x, y, 1.0), 2.5, fire, "Far fire", scale=(1.6, 1.6, 0.8))
        for k in range(11):
            ball((x + k * 1.2, y, 3 + k * 4.0), 2.4 + k * 0.8, random.choice(smoke), "Smoke puff", seg=14)
    pole_m = toon("Pole", (0.3, 0.22, 0.16), 0.12)
    for y in range(-190, 60, 25):
        rod((5, y, 0), (5, y, 8.3), 0.15, pole_m, "Power pole")
        box((5, y, 7.8), (1.6, 0.12, 0.12), pole_m, "Pole arm")
    leaf = [toon("Tree a", (0.2, 0.35, 0.22), 0.12), toon("Tree dead", (0.2, 0.16, 0.14), 0.1)]
    for i in range(40):
        x = random.choice([-1, 1]) * random.uniform(14, 60)
        y = random.uniform(-200, 40)
        if -25 < x < -7 and -32 < y < 14:
            continue
        rod((x, y, 0), (x, y, 2.6), 0.22, pole_m, "Trunk")
        ball((x, y, 4.2), random.uniform(1.6, 2.6), random.choice(leaf), "Crown")


def build_last_wagon():
    """Grandma's wagon, alone on the track, its windows still lit."""
    parts, doors = wagon_exterior("Last", 0, LAST_Y - 9, LAST_Y + 9, 0, -1, [LAST_Y + 6.5], burnt=0.6)
    warm = glow_mat("Lit window", (1.0, 0.78, 0.4), 3.0)
    for o in parts + [d for pair in doors for d in pair]:
        if "window" in o.name:
            o.data.materials[0] = warm
    bpy.ops.object.light_add(type="POINT", location=(0, LAST_Y + 9.6, 2.6))
    lamp = no_cam(bpy.context.object)
    lamp.data.energy = 600
    lamp.data.color = (1.0, 0.75, 0.4)


def build_our_train():
    root = empty("Our train")
    for i, (y0, y1) in enumerate(((-13, 13), (13.6, 39.6), (40.2, 66.2))):
        parts, _ = wagon_exterior(f"Car{i}", 0, y0, y1, 0, -1, [ODOOR] if i == 0 else [y0 + 2.2, y1 - 2.2],
                                  panels=False)
        for p in parts:
            parent_keep(p, root)
    inner = toon("Train inside", (0.75, 0.62, 0.45), 0.1)
    pole_m = toon("Handrail", (0.95, 0.75, 0.1), 0.4)
    for py in (ODOOR - 0.95, ODOOR + 0.95):
        parent_keep(box((0, py, FZ + 1.3), (3.0, 0.08, 2.6), inner, "Partition"), root)
    parent_keep(box((0.2, ODOOR + 0.9, FZ + 1.05), (0.8, 0.04, 2.0), toon("Inner door", (0.42, 0.45, 0.5)),
                    "Inner door"), root)
    for py in (ODOOR - 0.57, ODOOR + 0.57):
        parent_keep(rod((-1.3, py, FZ + 0.1), (-1.3, py, FZ + 2.1), 0.03, pole_m, "Handrail"), root)
    # warm vestibule lamp: lights Lena's face from the door
    bpy.ops.object.light_add(type="POINT", location=(-0.6, ODOOR, FZ + 1.4))
    lamp = no_cam(bpy.context.object)
    lamp.data.energy = 45
    lamp.data.color = (1, 0.88, 0.7)
    parent_keep(lamp, root)
    return root


# ================================================================ animation


def build():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.fps = FPS
    scene.frame_start, scene.frame_end = 1, int(END * FPS)
    scene.frame_step = 2  # "on twos"

    build_world()
    build_last_wagon()
    train = build_our_train()
    lena, mom = make_lena(), make_mom()

    cam = make_camera(scene)
    arms = POVArms(cam)
    arms.reach = 1.2  # cartoon arm: long enough to hold Lena's hand from the step

    rnd = random.Random(11)
    shake = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(-1, 1)) for _ in range(int(END * FPS) + 3)]
    kneel = Vector((-1.38, ODOOR + 0.15, FZ + KNEEL))
    mom_pos = Vector((-10.2, ODOOR + 1.5, 0))

    for f in range(1, int(END * FPS) + 1):
        t = (f - 1) / FPS
        ty = train_y(t)
        train.location.y = ty
        train.keyframe_insert("location", frame=f)
        v = abs(speed(t))

        # ---------------- Lena: on the platform beside the door, facing us, walking sideways
        trot = seg(t, 35.0, 39.0)
        sprint = seg(t, 50.0, 53.0)
        lpos = Vector((-2.35, ODOOR + ty + 0.1, PLAT_Z))
        looks_up = seg(t, 40.0, 40.6)
        lena.pose(f, t, lpos, facing=-90, run=min(1.0, v / 0.4) * lerp(0.45, 1.0, trot) if t > 2.2 else 0.0,
                  run_rate=lerp(1.0, 1.9, trot) + 0.7 * sprint, lean=-10 * sprint, look=(lerp(0, -8, looks_up), lerp(10, 18, looks_up)),
                  reach2=(lerp(92, 98, looks_up), -12), worry=lerp(1.4, 1.9, looks_up))

        # ---------------- Mum behind the fence, waving us to come
        mom.pose(f, t, mom_pos, facing=-70, wave=1.0 if (8 <= t < 20 or t >= 50) else 0.0,
                 reach=(130, 30) if not (8 <= t < 20 or t >= 50) else None, look=(0, 8), worry=1.6)

        # ---------------- camera: kneeling in the door, moving with the train
        lena_dir = (90, -20)
        yaw, pitch = lena_dir
        lean = 0.0
        # 12-17: up to mum behind the fence
        k = seg(t, 12.0, 12.8) * (1 - seg(t, 16.4, 17.2))
        yaw = lerp(yaw, 62, k); pitch = lerp(pitch, 4, k)
        # 30-35 shot 1: the last wagon's lights down the track (lean out of the door)
        k1 = seg(t, 30.0, 30.6) * (1 - seg(t, 34.6, 35.0))
        here = kneel + Vector((-0.6, 0, 0.35)) + Vector((0, ty, 0))
        to_last = Vector((0, LAST_Y + 9.0, 2.2)) - here
        last_yaw = math.degrees(math.atan2(-to_last.x, to_last.y)) % 360
        yaw = lerp(yaw, last_yaw, k1); pitch = lerp(pitch, 2, k1); lean = max(lean, k1)
        # 35-40 shot 2: the wheels and the gap, the train getting louder
        k2 = seg(t, 35.0, 35.4) * (1 - seg(t, 39.6, 40.0))
        yaw = lerp(yaw, 145, k2); pitch = lerp(pitch, -62, k2); lean = max(lean, 0.7 * k2)
        # 40-45 shot 3: Lena looks at us (closer)
        k3 = seg(t, 40.0, 40.3) * (1 - seg(t, 45.0, 45.4))
        pitch = lerp(pitch, -14, k3)
        # 45-50 the key line: from Lena to the last wagon and back, then Lena for the card
        k4 = seg(t, 47.2, 47.9) * (1 - seg(t, 49.6, 50.3))
        yaw = lerp(yaw, last_yaw, k4); pitch = lerp(pitch, 2, k4); lean = max(lean, k4)
        # the eyes "focus" on the last wagon: a slow zoom in
        cam.data.lens = 12 + 22 * max(seg(t, 30.6, 34.0) * (1 - seg(t, 34.6, 35.0)),
                                      seg(t, 47.9, 49.3) * (1 - seg(t, 49.6, 50.3)),
                                      seg(t, 56.4, 57.4) * (1 - seg(t, 57.9, 58.4)))
        cam.data.keyframe_insert("lens", frame=f)
        # 50-60: Lena running hard; a last quick look at the wagon (56-58), back to her
        k5 = seg(t, 56.0, 56.5) * (1 - seg(t, 57.9, 58.4))
        yaw = lerp(yaw, last_yaw, k5); pitch = lerp(pitch, 2, k5); lean = max(lean, k5)
        pos = kneel + Vector((-0.6 * lean, 0, 0.35 * lean)) + Vector((0, ty, 0))
        pos += Vector((-0.12, 0, -0.05)) * seg(t, 40.0, 40.6) * (1 - seg(t, 45.0, 45.4))  # lean towards her
        amp = 0.06 + 0.25 * min(1.0, v / 0.4) * (0.4 + 0.6 * trot) + 0.25 * sprint
        for te, kk in ((2.0, 2.2), (35.2, 1.2)):
            if te <= t < te + 0.6:
                amp += kk * (1 - (t - te) / 0.6)
        sx_, sy_, sz_ = shake[f]
        cam.location = pos
        cam.rotation_euler = (D(90 + pitch + sx_ * amp), D(sy_ * amp * 0.6), D(yaw + sz_ * amp))
        cam.keyframe_insert("location", frame=f)
        cam.keyframe_insert("rotation_euler", frame=f)

        # ---------------- our hands: right hand holds Lena's, left grips the handrail
        bpy.context.view_layer.update()
        target = world_to_cam(cam, lena.hand_world("L"))
        arms.set(f, "R", target + Vector((0.02, 0.03, 0.02)) if target.z < -0.05 else Vector((0.25, -0.45, -0.45)))
        rail = world_to_cam(cam, (-1.3, ODOOR + ty - 0.57, FZ + 1.0))
        arms.set(f, "L", rail if rail.z < -0.15 and abs(rail.x) < 0.6 else Vector((-0.3, -0.42, -0.46)))

    bpy.ops.object.light_add(type="SUN", rotation=(D(75), D(10), D(-40)))
    sun = bpy.context.object
    sun.data.energy = 1.1
    sun.data.color = (0.75, 0.7, 0.95)
    for k in (-36, -12, 12):  # floodlight spill on the platform
        bpy.ops.object.light_add(type="POINT", location=(-9, k, 7))
        lt = no_cam(bpy.context.object)
        lt.data.energy = 1200
        lt.data.color = (1.0, 0.95, 0.8)
    setup_render(scene, sky=(0.42, 0.34, 0.48), sky_strength=0.7)
    scene.frame_set(1)
    return scene


if __name__ == "__main__":
    run_cli(build(), "train_door.blend")
