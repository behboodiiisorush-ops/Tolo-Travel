"""
«واگن آخر» — sequences 1-3, 0-20 s (platform run, jump onto the moving train,
grandma separated into the last wagon).

First-person POV, cartoon 3D: puppet-like characters with round heads, hinged
jaws for talking, toon shading and black Freestyle outlines.  The viewer's
green sleeves are visible at the bottom of the frame.

Run in Blender (Scripting tab -> Run Script) or headless:
    blender -b --python part_station.py -- --save            # write train_pov.blend
    blender -b --python part_station.py -- --still 100       # one test frame
    blender -b --python part_station.py -- --render          # all frames -> frames/
Captions, fade and the fisheye look are added afterwards by post.py.
"""

import math
import os
import random
import sys

import bpy
from mathutils import Euler, Matrix, Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403,E402

SECONDS = 20
FRAMES = FPS * SECONDS
random.seed(3)

def train_offset(t):
    return 2.6 * t + 0.06 * t * t


def door_y(t):
    return 8.0 + train_offset(t)


# ================================================================ world


def build_station():
    concrete = toon("Platform", (0.62, 0.6, 0.57), 0.25)
    edge = toon("Platform edge", (0.85, 0.82, 0.7))
    yellow = toon("Safety line", (0.98, 0.8, 0.1), 0.4)
    gravel = toon("Gravel", (0.42, 0.38, 0.34))
    rail = toon("Rail", (0.35, 0.33, 0.32))
    sleeper = toon("Sleeper", (0.35, 0.25, 0.18))
    steel = toon("Steel", (0.3, 0.34, 0.4))
    ground = toon("Ground", (0.5, 0.45, 0.36), 0.2)

    box((30, 60, -0.05), (200, 400, 0.1), ground, "Ground")
    box((3.5, 40, 0.5), (7, 220, 1.0), concrete, "Platform")
    box((0.12, 40, 1.005), (0.24, 220, 0.02), edge, "Platform edge")
    box((0.5, 40, 1.012), (0.12, 220, 0.02), yellow, "Safety line")
    box((-1.6, 40, 0.05), (4.0, 400, 0.1), gravel, "Track bed")
    for x in (-2.32, -0.88):
        box((x, 40, 0.22), (0.08, 400, 0.12), rail, "Rail")
    for y in range(-60, 140, 1):
        box((-1.6, y, 0.12), (2.4, 0.22, 0.08), sleeper, "Sleeper")

    roof = glass_mat()
    for y in range(-30, 130, 9):
        bpy.ops.mesh.primitive_cylinder_add(radius=0.16, depth=6.0, location=(5.6, y, 4.0), vertices=12)
        finish(bpy.context.object, steel, "Column", smooth=True)
        box((2.5, y, 7.05), (13, 0.25, 0.3), steel, "Roof beam")
        box((5.6, y, 6.95), (0.6, 0.6, 0.15), steel, "Column cap")
        # benches and signs between columns
        if y % 18 == 0:
            box((4.2, y + 4.5, 1.45), (0.5, 1.8, 0.08), toon("Bench", (0.25, 0.45, 0.55)), "Bench")
            box((4.45, y + 4.5, 1.75), (0.06, 1.8, 0.5), toon("Bench", (0.25, 0.45, 0.55)), "Bench back")
        else:
            box((4.4, y + 4.5, 4.4), (0.1, 1.6, 0.6), toon("Sign", (0.1, 0.25, 0.55), 0.5), "Sign")
            box((4.36, y + 4.5, 4.4), (0.02, 1.3, 0.12), toon("Sign text", (0.95, 0.95, 0.95), 0.7), "Sign stripe")
    box((2.5, 40, 7.25), (13, 180, 0.06), roof, "Glass roof")
    for x in (-3.5, 0.5, 4.5, 8.5):
        box((x, 40, 7.2), (0.12, 180, 0.12), steel, "Roof purlin")
    # clock
    bpy.ops.mesh.primitive_cylinder_add(radius=0.35, depth=0.08, location=(5.6, 27, 5.2),
                                        rotation=(0, D(90), 0), vertices=32)
    finish(bpy.context.object, toon("Clock", (0.96, 0.96, 0.92), 0.5), "Clock")

    # dropped luggage on the platform
    for (x, y, c) in [(2.6, 14, (0.6, 0.15, 0.15)), (3.4, 25, (0.15, 0.3, 0.5)), (1.9, 33, (0.4, 0.4, 0.15)),
                      (2.9, 47, (0.3, 0.2, 0.4))]:
        box((x, y, 1.2), (0.5, 0.25, 0.4), toon("Suitcase", c), "Suitcase", bevel=0.04)


def build_city():
    ruin = [toon("Ruin a", (0.55, 0.5, 0.48), 0.2), toon("Ruin b", (0.45, 0.42, 0.42), 0.2),
            toon("Ruin c", (0.62, 0.52, 0.42), 0.2)]
    win = toon("Ruin window", (0.12, 0.1, 0.1), 0.0)
    for i in range(46):
        x = random.uniform(14, 70)
        y = random.uniform(-40, 220)
        w, d, h = random.uniform(5, 10), random.uniform(5, 10), random.uniform(6, 26)
        b = box((x, y, h / 2), (d, w, h), random.choice(ruin), "Building")
        b.rotation_euler = (random.uniform(-0.04, 0.04), random.uniform(-0.04, 0.04), random.uniform(-0.2, 0.2))
        if random.random() < 0.6:  # broken top
            c = box((x, y, h + 1.0), (d * 0.6, w * 0.5, 2.0), b.data.materials[0], "Broken top")
            c.rotation_euler = (random.uniform(-0.4, 0.4), random.uniform(-0.4, 0.4), 0)
        for k in range(int(h // 4)):
            box((x - d / 2 - 0.02, y, 2.5 + k * 3.6), (0.1, w * 0.6, 1.2), win, "Dark windows")

    smoke = [toon("Smoke", (0.25, 0.24, 0.25), 0.15), toon("Smoke light", (0.38, 0.36, 0.36), 0.15)]
    fire = glow_mat("Fire", (1.0, 0.45, 0.08), 6.0)
    for (x, y) in [(28, 60), (45, 130), (22, 175), (55, 30), (35, 95)]:
        ball((x, y, 1.5), 2.5, fire, "Fire", scale=(1, 1, 0.7))
        for k in range(9):
            r = 2.0 + k * 0.7
            s = ball((x + random.uniform(-1, 1) + k * 0.6, y + random.uniform(-1, 1), 3 + k * 3.2), r,
                     random.choice(smoke), "Smoke puff", seg=14)
            s.keyframe_insert("location", frame=1)
            s.location.z += 4 + k
            s.location.x += 2
            s.keyframe_insert("location", frame=FRAMES)


def build_explosion(pos, t0):
    f0 = int(t0 * FPS)
    m = glow_mat("Blast", (1.0, 0.6, 0.15), 12.0)
    b = ball(pos, 1.0, m, "Blast", seg=20)
    for f, sc in ((f0 - 1, 0.001), (f0, 2.0), (f0 + 4, 9.0), (f0 + 12, 7.0), (f0 + 20, 0.001)):
        b.scale = (sc, sc, sc)
        b.keyframe_insert("scale", frame=max(1, f))
    sm = ball(pos + Vector((0, 0, 4)), 1.0, toon("Blast smoke", (0.2, 0.19, 0.19), 0.1), "Blast smoke", seg=16)
    for f, sc, dz in ((f0 + 3, 0.001, 0), (f0 + 10, 8, 3), (FRAMES, 13, 14)):
        sm.scale = (sc, sc, sc * 1.2)
        sm.location.z = pos[2] + 4 + dz
        sm.keyframe_insert("scale", frame=min(FRAMES, f))
        sm.keyframe_insert("location", frame=min(FRAMES, f))


DOOR_LOCAL_Y = 4.0  # door centre measured from each wagon's rear end
WAGON = 22.0
GAP = 1.0


def build_train():
    white = toon("Train white", (0.93, 0.93, 0.91), 0.3)
    red = toon("Train red", (0.78, 0.1, 0.08), 0.3)
    dark = toon("Train windows", (0.1, 0.12, 0.16), 0.05)
    under = toon("Undercarriage", (0.18, 0.18, 0.2))
    inner = toon("Train inside", (0.75, 0.62, 0.45), 0.1)
    floor_m = toon("Train floor", (0.35, 0.35, 0.38))
    pole_m = toon("Handrail", (0.95, 0.75, 0.1), 0.4)
    inner_door = toon("Inner door", (0.42, 0.45, 0.5))

    train = empty("Train", (0, 0, 0))
    y_rear = -19.0
    for w in range(5):
        y0 = y_rear + w * (WAGON + GAP)
        y1 = y0 + WAGON
        dy0, dy1 = y0 + DOOR_LOCAL_Y - 0.65, y0 + DOOR_LOCAL_Y + 0.65
        far_door = (y1 - DOOR_LOCAL_Y - 0.65, y1 - DOOR_LOCAL_Y + 0.65)
        parts = []
        cx = -1.6
        parts.append(box((cx, (y0 + y1) / 2, 0.75), (3.0, WAGON, 0.5), under, "Undercarriage"))
        parts.append(box((cx, (y0 + y1) / 2, 1.18), (3.1, WAGON, 0.14), floor_m, "Floor"))
        parts.append(box((cx, (y0 + y1) / 2, 4.0), (3.1, WAGON, 0.35), white, "Roof", bevel=0.12))
        parts.append(box((-3.1, (y0 + y1) / 2, 2.6), (0.1, WAGON, 2.8), white, "Far wall"))
        for ye in (y0, y1):
            parts.append(box((cx, ye, 2.6), (3.1, 0.1, 2.8), white, "End wall"))
        # platform-side wall with door openings
        cuts = sorted([(dy0, dy1), far_door])
        ys = [y0] + [v for c in cuts for v in c] + [y1]
        for a, b in zip(ys[0::2], ys[1::2]):
            parts.append(box((-0.1, (a + b) / 2, 2.6), (0.1, b - a, 2.8), white, "Side wall"))
            parts.append(box((-0.03, (a + b) / 2, 1.72), (0.04, b - a, 0.16), red, "Red stripe"))
            if b - a > 4:
                parts.append(box((-0.03, (a + b) / 2, 2.6), (0.04, b - a - 1.2, 0.75), dark, "Window band"))
        for a, b in cuts:
            parts.append(box((-0.1, (a + b) / 2, 3.65), (0.1, b - a, 0.5), white, "Above door"))
            parts.append(box((-0.06, (a + b) / 2, 1.12), (0.2, b - a, 0.08), under, "Door step"))
            # vestibule: partitions, poles, inner doors
            for py in (a - 0.25, b + 0.25):
                parts.append(box((-1.7, py, 2.4), (2.8, 0.08, 2.4), inner, "Partition"))
            parts.append(box((-1.7, a - 0.2, 2.15), (0.8, 0.04, 1.9), inner_door, "Inner door"))
            parts.append(box((-3.0, (a + b) / 2, 2.15), (0.04, b - a, 1.9), inner_door, "Opposite door"))
            for py in (a + 0.08, b - 0.08):
                parts.append(rod((-0.3, py, 1.3), (-0.3, py, 3.3), 0.03, pole_m, "Handrail"))
        for wy in (y0 + 3, y1 - 3):
            for wx in (-2.7, -0.5):
                bpy.ops.mesh.primitive_cylinder_add(radius=0.42, depth=0.2, location=(wx, wy, 0.42),
                                                    rotation=(0, D(90), 0), vertices=20)
                parts.append(finish(bpy.context.object, under, "Wheel", smooth=True))
        if w == 4:  # front cab
            parts.append(ball((cx, y1 + 1.5, 2.3), 1.6, white, "Nose", scale=(1, 1.5, 1.05)))
            parts.append(ball((cx, y1 + 1.9, 2.9), 1.2, dark, "Windscreen", scale=(1.1, 1.3, 0.5)))
        for p in parts:
            parent_keep(p, train)
    # warm light in our vestibule
    bpy.ops.object.light_add(type="POINT", location=(-1.5, y_rear + WAGON + GAP + DOOR_LOCAL_Y, 3.2))
    lamp = bpy.context.object
    lamp.data.energy = 18
    lamp.data.color = (1, 0.9, 0.75)
    parent_keep(lamp, train)
    for f in range(1, FRAMES + 1):
        train.location.y = train_offset((f - 1) / FPS)
        train.keyframe_insert("location", frame=f)
    return train


# ================================================================ animation


def build():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.fps = FPS
    scene.frame_start, scene.frame_end = 1, FRAMES

    build_station()
    build_city()
    build_explosion(Vector((60, 120, 8)), 4.2)
    build_explosion(Vector((30, 75, 6)), 7.8)
    build_explosion(Vector((45, 150, 6)), 16.3)
    build_train()

    lena, mom, rahim, grandma = make_lena(), make_mom(), make_rahim(), make_grandma()
    extras = [make_extra(i) for i in range(7)]

    cam = make_camera(scene)
    arms = POVArms(cam)
    rnd = random.Random(11)
    shake = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(-1, 1)) for _ in range(FRAMES + 2)]
    gd_local = -19.0 + WAGON - DOOR_LOCAL_Y  # last wagon's front door (train frame)

    for f in range(1, FRAMES + 1):
        t = (f - 1) / FPS
        dy = door_y(t)
        off = train_offset(t)
        run_ph = 2 * math.pi * t * 1.6

        # ---------------- camera path
        gap = 6.2 * (1 - ease(t / 9.4)) + 0.35
        if t < 9.6:
            x = lerp(1.45, 0.75, seg(t, 6.0, 8.8))
            y = dy - gap
            z = 2.55 + 0.045 * math.sin(2 * run_ph)
        elif t < 10.4:
            u = (t - 9.6) / 0.8
            x = lerp(0.75, -1.15, ease(u))
            y = dy - lerp(0.35, -0.05, u)
            z = lerp(2.55, 2.75, u) + 0.45 * math.sin(math.pi * u)
        else:
            x = lerp(-1.15, -1.35, seg(t, 10.4, 11.2))
            x = lerp(x, 0.12, seg(t, 14.0, 14.7))  # lean out of the door, look back
            x = lerp(x, -0.3, seg(t, 17.9, 18.5))
            y = dy + 0.05 + 0.25 * seg(t, 14.0, 14.7) - 0.7 * seg(t, 17.9, 18.5)
            z = 2.78 - 0.4 * math.sin(math.pi * min(1, (t - 10.4) / 0.6))
        yaw, pitch = -38.0, -27.0
        yaw = lerp(yaw, 0, seg(t, 3.0, 3.6)); pitch = lerp(pitch, -6, seg(t, 3.0, 3.6))
        yaw = lerp(yaw, -38, seg(t, 5.0, 5.4)); pitch = lerp(pitch, -30, seg(t, 5.0, 5.4))
        yaw = lerp(yaw, 0, seg(t, 6.5, 7.0)); pitch = lerp(pitch, -6, seg(t, 6.5, 7.0))
        yaw = lerp(yaw, 22, seg(t, 7.6, 8.3)); pitch = lerp(pitch, 2, seg(t, 7.6, 8.3))
        yaw = lerp(yaw, -8, seg(t, 9.6, 10.3)); pitch = lerp(pitch, -28, seg(t, 9.8, 10.5))
        yaw = lerp(yaw, -90, seg(t, 10.6, 11.3)); pitch = lerp(pitch, -20, seg(t, 10.6, 11.3))
        pitch = lerp(pitch, -8, seg(t, 12.8, 13.3))
        yaw = lerp(yaw, -172, seg(t, 14.0, 14.8)); pitch = lerp(pitch, -4, seg(t, 14.0, 14.8))
        yaw = lerp(yaw, -312, seg(t, 17.9, 18.5)); pitch = lerp(pitch, -3, seg(t, 17.9, 18.5))
        amp = 0.8 if t < 9.6 else 0.35
        for te, k in ((4.25, 3.0), (7.85, 3.5), (10.4, 4.0), (16.35, 2.5)):
            if te <= t < te + 0.5:
                amp += k * (1 - (t - te) / 0.5)
        sx_, sy_, sz_ = shake[f]
        cam.location = (x, y, z)
        cam.rotation_euler = (D(90 + pitch + sx_ * amp), D(sy_ * amp * 0.8), D(yaw + sz_ * amp))
        cam.keyframe_insert("location", frame=f)
        cam.keyframe_insert("rotation_euler", frame=f)
        pov_ground = Vector((x, y, 1.0 if t < 9.8 else 1.25))

        # ---------------- Lena
        if t < 9.6:
            lpos = pov_ground + Vector((0.55, 0.5, 0))
            lpos.z = 1.0
            face_back = max(1 - seg(t, 2.6, 3.2), seg(t, 4.9, 5.3) * (1 - seg(t, 6.4, 6.9)))
            lena.pose(f, t, lpos, facing=0, run=1.0, run_rate=1.9, look=(lerp(20, 135, face_back), 25),
                      reach2=(130, 35), worry=1.2)
        elif t < 12.0:
            lpos = Vector((lerp(1.2, 0.65, seg(t, 9.6, 11.0)), dy - lerp(0.9, 0.25, seg(t, 9.6, 11.4)), 1.0))
            lena.pose(f, t, lpos, facing=lerp(0, 50, seg(t, 10.5, 11.5)), run=1.0, run_rate=1.9,
                      look=(25, 20), reach2=(150, 20), worry=1.3)
        else:
            u = seg(t, 12.0, 12.6)
            lpos = Vector((lerp(0.65, -0.75, u), dy - 0.25 + 0.6 * seg(t, 12.7, 13.2), lerp(1.0, 1.25, u)))
            lpos.x = lerp(lpos.x, -1.0, seg(t, 13.6, 14.2))
            lpos.y = lerp(lpos.y, dy + 0.45, seg(t, 13.6, 14.2))
            lena.pose(f, t, lpos, facing=lerp(50, 90, u) + 90 * seg(t, 14, 14.5), run=1.0 - u, run_rate=1.9,
                      look=(lerp(0, -40, seg(t, 17.9, 18.4)), 15), reach2=(150, 20) if t < 13.6 else None,
                      z=0.35 * math.sin(math.pi * u), worry=1.4)

        # ---------------- Mom
        if t < 9.6:
            ahead = lerp(2.6, -1.6, seg(t, 7.2, 9.6))
            mpos = Vector((lerp(1.9, 1.5, seg(t, 7.0, 9.0)), y + ahead, 1.0))
            look_back = seg(t, 3.4, 3.8) * (1 - seg(t, 5.0, 5.5))
            mom.pose(f, t, mpos, facing=0, run=1.0, run_rate=1.6, look=(150 * look_back, 0))
        elif t < 13.0:
            mpos = Vector((lerp(1.5, 0.9, seg(t, 9.6, 11.0)), dy - lerp(1.3, 1.15, seg(t, 10, 12)), 1.0))
            mom.pose(f, t, mpos, facing=lerp(0, 40, seg(t, 11.5, 12.5)), run=1.0, run_rate=1.6, look=(10, 10))
        else:
            u = seg(t, 13.0, 13.6)
            mpos = Vector((lerp(0.9, -0.55, u), dy - lerp(1.15, 0.45, u), lerp(1.0, 1.25, u)))
            # then she steps to the door edge and searches the platform behind
            mpos.x = lerp(mpos.x, -0.5, seg(t, 13.8, 14.4))
            mpos.y = lerp(mpos.y, dy - 0.3, seg(t, 13.8, 14.4))
            mpos.x = lerp(mpos.x, -1.2, seg(t, 17.6, 18.2))
            mpos.y = lerp(mpos.y, dy - 0.6, seg(t, 17.6, 18.2))
            talk_look = seg(t, 14.2, 14.5) * (1 - seg(t, 15.4, 15.8))
            mom.pose(f, t, mpos, facing=lerp(lerp(40, 90, u), 200, seg(t, 13.8, 14.4)), run=1.0 - u, run_rate=1.6,
                     look=(lerp(-20, -110, talk_look), 5), reach=(120, 10) if t < 13.8 else (100, -20),
                     z=0.4 * math.sin(math.pi * u), worry=1.6)

        # ---------------- Rahim (inside the door, rides with the train)
        if t < 9.6:
            rpos = Vector((-0.35, dy + 0.35, 1.25))
            rahim.pose(f, t, rpos, facing=-150, look=(0, -5),
                       reach=(lerp(60, 95, seg(t, 7.5, 8.5)), 25), reach2=(150, -40), lean=0)
        else:
            u = seg(t, 9.6, 10.1)
            rpos = Vector((lerp(-0.35, -0.6, u), dy + lerp(0.35, 0.8, u), 1.25))
            rpos.x = lerp(rpos.x, -1.75, seg(t, 14.0, 14.8))
            rpos.y = lerp(rpos.y, dy + 0.55, seg(t, 14.0, 14.8))
            face_cam = seg(t, 12.8, 13.1) * (1 - seg(t, 14.0, 14.4))
            fac = lerp(lerp(-150, -95, u), -125, seg(t, 14.0, 14.8))
            rahim.pose(f, t, rpos, facing=fac, look=(lerp(-20, -110, face_cam), -10),
                       reach=(lerp(95, 70, seg(t, 12.6, 13.0)), 30) if t < 14 else (20, 0),
                       reach2=(150, -40) if t < 14 else (30, 0), lean=0)

        # ---------------- Grandma: on the platform by the last wagon, climbs in at ~17.3 s
        gy = gd_local + off
        if t < 17.2:
            gpos = Vector((lerp(2.2, 0.8, seg(t, 13.5, 16.8)), lerp(dy - 4.6, gy - 0.4, seg(t, 15.9, 17.1)), 1.0))
            grandma.pose(f, t, gpos, facing=lerp(0, 25, seg(t, 15.3, 15.6)) * (1 - seg(t, 16.8, 17.0)),
                         run=0.8, run_rate=1.2, look=(0, 15), wave=seg(t, 15.4, 15.6) * (1 - seg(t, 16.7, 16.9)),
                         worry=1.8)
        else:
            u = seg(t, 17.2, 17.7)
            gpos = Vector((lerp(0.8, -0.8, u), gy - 0.4, lerp(1.0, 1.25, u)))
            grandma.pose(f, t, gpos, facing=-90 * u, run=1 - u, z=0.25 * math.sin(math.pi * u), worry=1.8)

        # ---------------- passengers on the platform
        for i, e in enumerate(extras):
            if i < 3:
                epos = Vector((1.6 + i * 0.9, y + 5 + i * 3.2 + 0.4 * t * (i - 1), 1.0))
                e.pose(f, t, epos, facing=0, run=1.0, run_rate=1.5 + 0.1 * i)
            elif i < 5:  # pushing grandma towards the door
                epos = Vector((1.7 + (i - 3) * 0.6, gy - 1.2 - (i - 3) * 0.9, 1.0))
                e.pose(f, t, epos, facing=-20, run=0.9, run_rate=1.3, reach=(80, 10), worry=1.5)
            else:
                epos = Vector((3.2 + (i - 5) * 0.7, 24 + (i - 5) * 14, 1.0))
                e.pose(f, t, epos, facing=-70 + i * 10, look=(20, 10), worry=1.5)

        # ---------------- POV hands
        if t < 9.6:
            arms.set(f, "R", world_to_cam(cam, lena.hand_world("L")))
            if t < 8.6:
                arms.set(f, "L", (-0.3, -0.42 + 0.05 * math.sin(run_ph), -0.5))
            else:
                arms.set(f, "L", world_to_cam(cam, rahim.hand_world("R")))
        elif t < 10.6:
            arms.set(f, "L", world_to_cam(cam, rahim.hand_world("R")) if t < 10.0 else (-0.35, -0.5, -0.45))
            arms.set(f, "R", (0.32, -0.48, -0.45))
        elif t < 14.0:
            arms.set(f, "L", (-0.32, -0.45, -0.5))
            if 11.2 <= t < 12.7:
                arms.set(f, "R", world_to_cam(cam, lena.hand_world("L")))
            else:
                arms.set(f, "R", (0.3, -0.45, -0.5))
        else:  # holding the door frame, other hand reaching towards grandma
            arms.set(f, "L", (-0.3, -0.25 + 0.04 * math.sin(t * 9), -0.55))
            arms.set(f, "R", (0.35, -0.3 + 0.1 * seg(t, 16.6, 17.0), -0.62))

    bpy.ops.object.light_add(type="SUN", rotation=(D(50), D(-20), D(-60)))
    sun = bpy.context.object
    sun.data.energy = 2.4
    sun.data.color = (1.0, 0.86, 0.72)
    sun.data.angle = D(2)
    setup_render(scene, sky=(0.8, 0.6, 0.48), sky_strength=0.8)
    scene.frame_set(1)
    return scene


if __name__ == "__main__":
    run_cli(build(), "train_station.blend")
