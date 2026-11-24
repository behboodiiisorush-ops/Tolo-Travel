"""
«واگن آخر ۲ — برگشت» — inside our car: the goodbye at the border and the ride back
(0-27 s), and the ride towards the border again with grandma (56-66 s).

The car stands still at the origin; the world outside the windows slides past.
Frame numbers are global, so they line up with part_field.py (27-56 s).

    python part_wagon.py --still 100,400
    python part_wagon.py --render --range 1 648
    python part_wagon.py --render --range 1345 1584
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

random.seed(22)
GROUND = -1.3   # the interior floor is z=0, the ground outside is 1.3 m lower
LONE_X = -9.0   # the detached wagon stands on a siding left of our track


def _speed(t):
    if t < 16.0:
        return 0.0
    if t < 18.5:
        return -9.0 * seg(t, 16.0, 18.5)
    if t < 24.8:
        return -9.0
    if t < 27.0:
        return -9.0 * (1 - seg(t, 24.8, 26.6))
    # (the field set covers 27-56; the train leaves again at 52.5)
    return 8.0 * seg(t, 52.5, 56.0) if t < 56.0 else 8.0


_S = [0.0]
for _f in range(1, 66 * FPS + 4):
    _S.append(_S[-1] + _speed((_f - 1) / FPS) / FPS)


def travelled(t):
    """Position of the car along the track (negative = backwards from the border)."""
    f = max(0, min(len(_S) - 1, int(round(t * FPS))))
    return _S[f]


S_STOP = travelled(40.0)          # where the train stands next to the lone wagon
LONE_Y = S_STOP - 14.0            # lone wagon centre (outside coordinates): 14 m ahead of us when stopped

# ================================================================ car interior (same as episode 1)


def build_car():
    wall = toon("Car wall", (0.9, 0.82, 0.62), 0.12)
    panel = toon("Car panel", (0.12, 0.5, 0.52), 0.12)
    ceiling = toon("Car ceiling", (0.95, 0.9, 0.78), 0.12)
    floor_m = toon("Car floor", (0.38, 0.36, 0.38), 0.1)
    carpet = toon("Carpet", (0.68, 0.1, 0.14), 0.1)
    seat_m = toon("Seat", (0.15, 0.22, 0.5), 0.12)
    covers = [toon("Cover a", (0.98, 0.55, 0.1), 0.15), toon("Cover b", (0.98, 0.82, 0.2), 0.15),
              toon("Cover c", (0.9, 0.3, 0.35), 0.15)]
    table_m = toon("Table", (0.78, 0.6, 0.38), 0.12)
    metal = toon("Car metal", (0.55, 0.58, 0.62), 0.12)
    curtain = toon("Curtain", (0.98, 0.75, 0.2), 0.15)
    frame_m = toon("Window frame", (0.35, 0.36, 0.4), 0.1)

    box((0, 0, -0.05), (3.0, 26, 0.1), floor_m, "Floor")
    box((0, 0, 0.005), (0.6, 26, 0.01), carpet, "Aisle carpet")
    box((0, 0, 2.45), (3.0, 26, 0.1), ceiling, "Ceiling")
    for sx in (-1, 1):
        x = sx * 1.47
        box((x, 0, 0.42), (0.08, 26, 0.84), panel, "Lower wall")
        box((x, 0, 2.2), (0.08, 26, 0.5), wall, "Upper wall")
        box((sx * 1.2, 0, 2.38), (0.6, 26, 0.12), wall, "Ceiling cove", bevel=0.05)
        for y in range(-12, 13, 2):
            box((x, y, 1.4), (0.08, 0.42, 1.12), wall, "Window pillar")
            box((x - sx * 0.02, y + 0.35, 1.42), (0.06, 0.25, 1.05), curtain, "Curtain")
        box((x - sx * 0.03, 0, 0.86), (0.06, 26, 0.06), frame_m, "Window sill")
        box((x - sx * 0.03, 0, 1.95), (0.06, 26, 0.06), frame_m, "Window top")
        box((sx * 1.18, 0, 1.98), (0.5, 26, 0.04), metal, "Rack")
        for y in range(-11, 12, 2):
            if random.random() < 0.55:
                c = random.choice([(0.85, 0.2, 0.2), (0.2, 0.45, 0.85), (0.95, 0.7, 0.1), (0.3, 0.65, 0.3),
                                   (0.6, 0.3, 0.7)])
                box((sx * 1.2, y + random.uniform(-0.3, 0.3), 2.12), (0.4, random.uniform(0.4, 0.7), 0.25),
                    toon(f"Bag {c}", c), "Bag", bevel=0.04)
    for ye, name in ((-12.9, "Back wall"), (12.9, "Front wall")):
        box((0, ye, 1.2), (3.0, 0.1, 2.4), wall, name)
        box((0, ye - math.copysign(0.03, ye), 1.05), (0.8, 0.04, 2.0), toon("Car door", (0.5, 0.55, 0.62)), "Door")

    white = glow_mat("Ceiling light", (1.0, 0.95, 0.85), 1.1)
    for sx in (-1, 1):
        box((sx * 0.55, 0, 2.39), (0.12, 25, 0.02), white, "Light strip")

    for c in (-9, -6, -3, 0, 3, 6, 9):
        for sx in (-1, 1):
            for x in (sx * 0.62, sx * 1.12):
                for side in (1, -1):
                    y = c + side * 0.75
                    back_y = y + side * 0.26
                    box((x, y, 0.44), (0.46, 0.5, 0.12), seat_m, "Seat cushion", bevel=0.04)
                    box((x, y, 0.2), (0.4, 0.4, 0.38), metal, "Seat base")
                    box((x, back_y, 0.85), (0.46, 0.12, 0.85), seat_m, "Seat back", bevel=0.04)
                    box((x, back_y - side * 0.065, 1.13), (0.36, 0.02, 0.22), random.choice(covers), "Head cover")
            box((sx * 0.87, c, 0.74), (0.95, 0.56, 0.05), table_m, "Table", bevel=0.02)
            box((sx * 1.3, c, 0.5), (0.06, 0.12, 0.48), metal, "Table leg")


# ================================================================ outside world


def build_outside():
    """Border at the start, then scorched fields, smoke, and the lone wagon on its siding."""
    world = empty("Outside")
    parts = []
    dirt = toon("Field dirt", (0.5, 0.38, 0.27), 0.18)
    gravel = toon("Gravel", (0.45, 0.4, 0.36), 0.15)
    parts.append(box((0, -150, GROUND - 0.05), (400, 900, 0.1), dirt, "Ground"))
    parts.append(box((0, -150, GROUND + 0.02), (5, 900, 0.1), gravel, "Track bed"))
    parts.append(box((LONE_X, LONE_Y - 120, GROUND + 0.02), (5, 300, 0.1), gravel, "Siding bed"))
    cols = [toon("Burnt a", (0.28, 0.22, 0.18), 0.12), toon("Field b", (0.8, 0.68, 0.3), 0.18),
            toon("Burnt b", (0.2, 0.17, 0.15), 0.1), toon("Field c", (0.45, 0.55, 0.25), 0.18)]
    for k in range(26):
        y = 20 - k * 16
        for sx in (-1, 1):
            parts.append(box((sx * 45, y, GROUND + 0.01), (70, 15, 0.06), cols[(k + (sx > 0)) % 4], "Field strip"))
    # dead / living trees, power poles, scattered small fires and smoke columns
    pole_m = toon("Pole", (0.32, 0.22, 0.15), 0.15)
    leaf = [toon("Tree a", (0.25, 0.45, 0.22), 0.15), toon("Tree dead", (0.22, 0.18, 0.15), 0.1)]
    for y in range(10, -300, -24):
        parts.append(rod((6, y, GROUND), (6, y, 7), 0.15, pole_m, "Power pole"))
        parts.append(box((6, y, 6.5), (1.6, 0.12, 0.12), pole_m, "Pole arm"))
    for i in range(45):
        x = random.choice([-1, 1]) * random.uniform(14, 55)
        y = random.uniform(-320, 20)
        parts.append(rod((x, y, GROUND), (x, y, GROUND + 2.6), 0.22, pole_m, "Trunk"))
        parts.append(ball((x, y, GROUND + 4.2), random.uniform(1.6, 2.6), random.choice(leaf), "Crown"))
    fire = glow_mat("Fire", (1.0, 0.45, 0.08), 6.0)
    smoke = [toon("Smoke", (0.22, 0.21, 0.22), 0.12), toon("Smoke light", (0.36, 0.34, 0.34), 0.12)]
    for (x, y) in [(-30, -40), (-45, -110), (-22, -170), (35, -70), (-38, -230), (28, -150)]:
        parts.append(ball((x, y, GROUND + 0.5), 1.2, fire, "Field fire", scale=(1.6, 1.6, 0.7)))
        for k in range(10):
            parts.append(ball((x + k * 0.9, y + random.uniform(-1, 1), GROUND + 2 + k * 3.0), 1.6 + k * 0.6,
                              random.choice(smoke), "Smoke puff", seg=14))
    # the border (fence, floodlights, barrier, hut) right outside the window at the start
    fence = toon("Fence", (0.55, 0.6, 0.62), 0.15)
    for k in range(-20, 21):
        parts.append(rod((-7, k * 2.5, GROUND), (-7, k * 2.5, GROUND + 2.9), 0.06, fence, "Fence post"))
    for z in (1.0, 1.7, 2.4, 2.85):
        parts.append(box((-7, 0, GROUND + z), (0.03, 100, 0.03), fence, "Fence wire"))
    lamp = glow_mat("Flood", (1.0, 0.95, 0.75), 8.0)
    for k in (-24, -8, 8, 24):
        parts.append(rod((-11, k, GROUND), (-11, k, GROUND + 9.3), 0.2, fence, "Light tower"))
        parts.append(box((-10.6, k, GROUND + 9.3), (0.6, 1.4, 0.7), lamp, "Floodlight"))
    red_w = [toon("Barrier red", (0.9, 0.12, 0.1), 0.2), toon("Barrier white", (0.97, 0.97, 0.95), 0.3)]
    for k in range(8):
        parts.append(box((-14, -6 + k * 0.6, GROUND + 1.4), (0.25, 0.6, 0.25), red_w[k % 2], "Barrier"))
    hut = toon("Hut", (0.35, 0.5, 0.3), 0.15)
    parts.append(box((-16, 4, GROUND + 1.5), (3, 3, 3), hut, "Guard hut"))
    parts.append(box((-16, 4, GROUND + 3.15), (3.6, 3.6, 0.3), toon("Hut roof", (0.85, 0.3, 0.2), 0.15), "Hut roof"))
    # people waiting on the far side of the fence (tiny, far away)
    crowd_c = [(0.85, 0.2, 0.2), (0.2, 0.45, 0.85), (0.95, 0.7, 0.1), (0.3, 0.65, 0.3), (0.6, 0.3, 0.7)]
    for k in range(18):
        c = crowd_c[k % 5]
        y = random.uniform(-15, 15)
        x = random.uniform(-20, -13)
        parts.append(box((x, y, GROUND + 0.6), (0.4, 0.3, 1.2), toon(f"Crowd {c}", c), "Crowd body", bevel=0.1))
        parts.append(ball((x, y, GROUND + 1.4), 0.2, toon("Crowd skin", (0.85, 0.62, 0.48)), "Crowd head"))
    # the lone wagon (the one grandma is in), sooty, door facing our track
    wp, _ = wagon_exterior("Lone", LONE_X, LONE_Y - 9, LONE_Y + 9, GROUND, +1, [LONE_Y + 2.0], burnt=1.0)
    parts += wp
    for p in parts:
        parent_keep(p, world)
    return world


# ================================================================ props


def screen_mat(name, path):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = bpy.data.images.load(path)
    e = nt.nodes.new("ShaderNodeEmission")
    e.inputs["Strength"].default_value = 1.0
    nt.links.new(tex.outputs["Color"], e.inputs["Color"])
    nt.links.new(e.outputs[0], out.inputs["Surface"])
    return m


def build_phone(cam):
    phone = empty("Phone")
    parent_local(phone, cam)
    body = box((0, 0, 0), (0.08, 0.16, 0.012), toon("Phone case", (0.9, 0.3, 0.45), 0.2), "Phone body",
               bevel=0.008)
    parent_keep(body, phone)
    screens = {}
    for key, fn in (("call", "phone_call.png"), ("mom", "phone_mom.png")):
        bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, 0.0065))
        sc = bpy.context.object
        sc.scale = (0.07, 0.145, 1)
        bpy.ops.object.transform_apply(scale=True)
        sc.name = f"Phone screen {key}"
        sc.data.materials.append(screen_mat(f"Screen {key}", os.path.join(HERE, "textures", fn)))
        parent_keep(sc, phone)
        screens[key] = sc
    phone.rotation_mode = "XYZ"
    return phone, screens


def keep_scale(o, f, visible, size=1.0):
    o.scale = (size, size, size) if visible else (0.001, 0.001, 0.001)
    o.keyframe_insert("scale", frame=f)


def give_radio(rahim):
    radio = box((0, 0, 0), (0.07, 0.05, 0.16), toon("Radio", (0.12, 0.12, 0.13)), "Radio", bevel=0.01)
    led = ball((0, 0, 0), 0.012, glow_mat("Radio LED", (0.2, 1.0, 0.3), 4.0), "Radio LED")
    ant = rod((0, 0, 0), (0, 0, 0.14), 0.006, toon("Radio", (0.12, 0.12, 0.13)), "Radio antenna")
    hp = rahim.p["handL"].matrix_world.translation.copy()
    for o, d in ((radio, Vector((0, 0.05, 0.02))), (led, Vector((0.02, 0.08, 0.08))), (ant, Vector((0.02, 0.05, 0.1)))):
        o.location = hp + d
        parent_keep(o, rahim.p["elbowL"])
    return led


# ================================================================ animation

SEAT_CAM = Vector((-0.62, 0.72, 1.22))
AWAY = Vector((0.1, 40, 0))  # where people wait when they are not in the shot


def build():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.fps = FPS
    scene.frame_start, scene.frame_end = 1, int(END * FPS)

    build_car()
    outside = build_outside()

    lena, mom, rahim, jalal, grandma = make_lena(), make_mom(), make_rahim(), make_jalal(), make_grandma()
    lena_bunny = [o for o in bpy.data.objects if o.name.startswith("Lena bunny")]
    gm_bunny = bunny(grandma.hand_world("R") + Vector((0.0, 0.08, 0.06)), grandma.p["elbowR"], "Grandma bunny")
    led = give_radio(rahim)

    seated = []
    spots = [(-0.62, -3.75, 0), (-1.12, -3.75, 0), (0.62, -3.75, 0), (1.12, -6.75, 0), (-0.62, -6.75, 0),
             (1.12, 3.75, 0)]
    for i, (sx, sy, fac) in enumerate(spots):
        seated.append((make_extra(i, 0.95), Vector((sx, sy, 0)), fac))

    cam = make_camera(scene)
    arms = POVArms(cam)
    phone, screens = build_phone(cam)
    pb_root = pov_bunny(cam)
    pb_parts = [o for o in bpy.data.objects if o.name.startswith("POV bunny ")]

    rnd = random.Random(5)
    shake = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(-1, 1)) for _ in range(int(END * FPS) + 3)]

    for f in range(1, int(END * FPS) + 1):
        t = (f - 1) / FPS
        second = t >= 56.0  # the ride with grandma
        s_now = travelled(t)
        outside.location.y = -s_now
        outside.keyframe_insert("location", frame=f)
        v = abs(_speed(t))

        # ---------------- camera (always in our seat)
        pos = SEAT_CAM.copy()
        if not second:
            yaw, pitch = 98, 0                                    # hook: the border outside the window
            yaw = lerp(yaw, 206, seg(t, 3.2, 3.6)); pitch = lerp(pitch, 19, seg(t, 3.2, 3.6))   # mum
            yaw = lerp(yaw, 193, seg(t, 6.1, 6.4)); pitch = lerp(pitch, -2, seg(t, 6.1, 6.4))   # Lena
            pitch = lerp(pitch, -14, seg(t, 9.2, 9.6))                                          # bunny
            yaw = lerp(yaw, 203, seg(t, 11.0, 11.4)); pitch = lerp(pitch, 6, seg(t, 11.0, 11.4))  # Rahim
            yaw = lerp(yaw, 186, seg(t, 12.6, 13.2)); pitch = lerp(pitch, 2, seg(t, 12.6, 13.2))  # they leave
            yaw = lerp(yaw, 222, seg(t, 14.7, 15.1)); pitch = lerp(pitch, 0, seg(t, 14.7, 15.1))  # Jalal
            yaw = lerp(yaw, 200, seg(t, 16.8, 17.2)); pitch = lerp(pitch, 6, seg(t, 16.8, 17.2))  # Rahim + radio
            yaw = lerp(yaw, 182, seg(t, 20.6, 21.0)); pitch = lerp(pitch, -48, seg(t, 20.6, 21.0))  # phone
            yaw = lerp(yaw, 222, seg(t, 22.5, 22.9)); pitch = lerp(pitch, 0, seg(t, 22.5, 22.9))  # Jalal points
            yaw = lerp(yaw, 166, seg(t, 23.4, 23.9)); pitch = lerp(pitch, 2, seg(t, 23.4, 23.9))  # window
            yaw = lerp(yaw, 150, seg(t, 24.0, 26.6))                                             # tracking it
            pos = pos.lerp(Vector((-1.02, 0.15, 1.32)), seg(t, 23.3, 24.0))                       # lean to the glass
        else:
            yaw, pitch = 180, -2                                  # grandma across the table
            yaw = lerp(yaw, 182, seg(t, 59.5, 59.9)); pitch = lerp(pitch, -48, seg(t, 59.5, 59.9))  # phone
            pitch = lerp(pitch, -2, seg(t, 61.9, 62.3))                                           # grandma
            yaw = lerp(yaw, 203, seg(t, 62.6, 63.0)); pitch = lerp(pitch, 6, seg(t, 62.6, 63.0))  # Rahim
        amp = 0.1 * min(1.0, v / 8.0)
        for te, k in ((16.0, 1.6), (25.0, 1.0), (26.4, 1.8)):
            if te <= t < te + 0.6:
                amp += k * (1 - (t - te) / 0.6)
        sx_, sy_, sz_ = shake[f]
        cam.location = pos
        cam.rotation_euler = (D(90 + pitch + sx_ * amp), D(sy_ * amp * 0.6), D(yaw + sz_ * amp))
        cam.keyframe_insert("location", frame=f)
        cam.keyframe_insert("rotation_euler", frame=f)

        # ---------------- Mom and Lena (first part only)
        if not second and t < 17.5:
            # mum: stands in the aisle, backs away while she blesses us, then walks to the back door
            back = seg(t, 12.4, 13.9)
            walk = seg(t, 13.9, 17.4)
            turn = seg(t, 13.7, 14.2)
            mpos = Vector((lerp(0.05, 0.05, back), lerp(-0.7, -1.5, back) - 10.4 * walk, 0))
            mom.pose(f, t, mpos, facing=lerp(30, 180, turn), run=0.5 * turn, run_rate=1.2, lean=0,
                     look=(lerp(0, 25, seg(t, 6.1, 6.5) * (1 - seg(t, 8.9, 9.3))), 15 * (1 - turn)),
                     reach2=(40, -25) if t < 12.4 else None, worry=1.5)
            # Lena: next to mum, reaches out with the bunny, then leaves first and waves at the door
            lt = seg(t, 12.6, 13.2)
            lwalk = seg(t, 13.2, 16.6)
            wave_back = seg(t, 15.4, 15.7) * (1 - seg(t, 16.6, 16.9))
            lpos = Vector((lerp(-0.45, -0.05, lt), lerp(-0.05, -0.9, lt) - 10.0 * lwalk, 0))
            hand_out = seg(t, 9.3, 9.8) * (1 - seg(t, 10.9, 11.3))
            lena.pose(f, t, lpos, facing=lerp(lerp(15, 180, lt), 0, wave_back), run=0.8 * lt * (1 - wave_back),
                      run_rate=1.4, lean=0, look=(0, 25 * (1 - lt)),
                      reach=(lerp(10, 80, hand_out), -15) if hand_out > 0 else None,
                      reach2=(150, 10) if 6.3 <= t < 7.6 else None, wave=wave_back, worry=1.6)
            lena_has = t < 10.6
        else:
            mom.pose(f, t, AWAY, facing=0)
            lena.pose(f, t, AWAY + Vector((1, 0, 0)), facing=0)
            lena_has = False
        show(lena_bunny, f, lena_has)
        show(pb_parts, f, (not second) and t >= 10.6)

        # ---------------- Grandma (second part only): sits across the table, bunny in her lap
        if second:
            grandma.pose(f, t, Vector((-0.62, -0.75, 0)), facing=0, sit=1, seat_h=0.5, lean=0,
                         look=(lerp(0, -8, seg(t, 62.5, 63.0)), 6), reach=(55, 0), worry=1.0 if t < 63 else 1.5)
        else:
            grandma.pose(f, t, AWAY + Vector((2, 0, 0)), facing=0)
        show(gm_bunny, f, second)

        # ---------------- Jalal (across the aisle, facing us)
        point = seg(t, 22.6, 23.0) * (1 - seg(t, 24.4, 24.8)) if not second else 0.0
        jalal.pose(f, t, Vector((0.62, -0.75, 0)), facing=0, sit=1, seat_h=0.5, lean=0,
                   reach2=(lerp(20, 95, point), lerp(0, 115, point)) if point > 0 else None,
                   look=(lerp(30, 70, point), 8), worry=1.3 if not second else 0.9)

        # ---------------- Rahim: aisle at 11-12.6, back with the radio 16.6-27, and again at 62.6-66
        if not second:
            if 10.4 <= t < 13.6:
                u = seg(t, 10.4, 11.1)
                rpos = Vector((0.1, lerp(-6.0, -1.9, u) - 3.0 * seg(t, 12.7, 13.6), 0))
                rahim.pose(f, t, rpos, facing=0 if t < 12.7 else 180, run=(1 - u) + seg(t, 12.7, 13.0),
                           run_rate=1.6, reach=(140, 20) if 11.2 < t < 12.7 else None, look=(0, 8), worry=1.6)
            elif 16.4 <= t < 27.0:
                u = seg(t, 16.4, 17.2)
                rpos = Vector((0.1, lerp(-6.0, -1.6, u), 0))
                rahim.pose(f, t, rpos, facing=0, run=1 - u, run_rate=1.6,
                           reach2=(105, 10) if 16.9 < t < 18.4 else (20, 0),
                           look=(lerp(0, 60, seg(t, 23.5, 24.0)), 8), worry=1.6,
                           reach=(80, 60) if t > 24.4 else None)
            else:
                rahim.pose(f, t, Vector((0.1, -30, 0)), facing=0)
            led_on = 16.9 <= t <= 18.3 and int(t * 6) % 2 == 0
        else:
            if t >= 62.4:
                u = seg(t, 62.4, 63.0)
                rahim.pose(f, t, Vector((0.1, lerp(-6.0, -1.6, u), 0)), facing=0, run=1 - u, run_rate=1.4,
                           reach2=(105, 10) if t < 64.5 else (20, 0), look=(0, 8), worry=1.8)
            else:
                rahim.pose(f, t, Vector((0.1, -30, 0)), facing=0)
            led_on = 63.0 <= t <= 64.4 and int(t * 6) % 2 == 0
        keep_scale(led, f, led_on or not (16.9 <= t <= 18.3 or 63.0 <= t <= 64.4))

        for i, (e, p0, fac) in enumerate(seated):
            e.pose(f, t, p0, facing=fac, sit=1, seat_h=0.5, look=(10 * math.sin(i + t * 0.3), 0), worry=1.3, lean=0)

        # ---------------- POV hands and props
        phone_vis = (20.7 <= t < 22.6) or (59.6 <= t < 62.2)
        keep_scale(phone, f, phone_vis, size=1.4)
        keep_scale(screens["call"], f, not second)
        keep_scale(screens["mom"], f, second)
        phone.location = (0.06, -0.21, -0.46)
        phone.rotation_euler = (D(-25), 0, D(-4))
        phone.keyframe_insert("location", frame=f)
        phone.keyframe_insert("rotation_euler", frame=f)
        bunny_hand = (-0.2, -0.34, -0.42)
        if phone_vis:
            arms.set(f, "R", (0.1, -0.33, -0.45))
            arms.set(f, "L", (-0.26, -0.42, -0.46))
        elif 9.6 <= t < 10.9:  # reach for the bunny in Lena's hand
            target = world_to_cam(cam, lena.hand_world("R"))
            k = seg(t, 9.6, 10.3)
            arms.set(f, "L", Vector((-0.28, -0.42, -0.46)).lerp(target, k))
            arms.set(f, "R", (0.28, -0.42, -0.46))
        elif (not second) and t >= 10.9:
            arms.set(f, "L", Vector(bunny_hand) + Vector((0, 0, -0.07)))
            arms.set(f, "R", (0.28, -0.42, -0.46))
        else:
            arms.set(f, "L", (-0.28, -0.42, -0.46))
            arms.set(f, "R", (0.28, -0.42, -0.46))
        if (not second) and t >= 10.6:
            bl = world_to_cam(cam, lena.hand_world("R")) if t < 10.9 else Vector(bunny_hand)
            if 10.9 <= t < 11.3:
                bl = world_to_cam(cam, lena.hand_world("R")).lerp(Vector(bunny_hand), seg(t, 10.9, 11.3))
            pb_root.location = bl
            pb_root.keyframe_insert("location", frame=f)

    bpy.ops.object.light_add(type="SUN", rotation=(D(70), D(15), D(60)))
    sun = bpy.context.object
    sun.data.energy = 1.8
    sun.data.color = (1.0, 0.72, 0.5)
    bpy.ops.object.light_add(type="POINT", location=(-0.3, -0.4, 1.5))
    no_cam(bpy.context.object)
    bpy.context.object.data.energy = 25
    bpy.context.object.data.color = (1.0, 0.92, 0.8)
    setup_render(scene, sky=(0.86, 0.52, 0.4), sky_strength=0.6)
    scene.frame_set(1)
    return scene


if __name__ == "__main__":
    run_cli(build(), "train_wagon2.blend")
