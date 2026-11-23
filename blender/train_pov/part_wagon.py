"""
«واگن آخر» — sequences 4-10, 20-65 s, inside the passenger car.

The car stands still at the origin; the world outside the windows slides past
(burning city -> fields -> border).  Frame numbers are global (481..1560) so
the frames line up with part_station.py.

    blender -b --python part_wagon.py -- --still 600
    blender -b --python part_wagon.py -- --render [--range 481 1000]
"""

import math
import os
import random
import sys

import bpy
from mathutils import Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403,E402

T0, T1 = 20.0, 65.0
F0, F1 = int(T0 * FPS) + 1, int(T1 * FPS)
random.seed(21)

SPEED = 8.0


def travelled(t):
    """Distance the train has moved since T0 (it brakes to a stop at 57.5 s)."""
    t = max(T0, t)
    if t <= 55.5:
        return SPEED * (t - T0)
    u = min(t, 57.5) - 55.5
    return SPEED * 35.5 + SPEED * (u - u * u / 4.0)


STOP_S = travelled(60)
SEAT_FACE_NEG, SEAT_FACE_POS = 180, 0  # yaw for people facing -Y / +Y

# ================================================================ car interior


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
        # luggage rack + colourful bags
        box((sx * 1.18, 0, 1.98), (0.5, 26, 0.04), metal, "Rack")
        for y in range(-11, 12, 2):
            if random.random() < 0.7:
                c = random.choice([(0.85, 0.2, 0.2), (0.2, 0.45, 0.85), (0.95, 0.7, 0.1), (0.3, 0.65, 0.3),
                                   (0.6, 0.3, 0.7)])
                box((sx * 1.2, y + random.uniform(-0.3, 0.3), 2.12), (0.4, random.uniform(0.4, 0.7), 0.25),
                    toon(f"Bag {c}", c), "Bag", bevel=0.04)
    for ye, name in ((-12.9, "Back wall"), (12.9, "Front wall")):
        box((0, ye, 1.2), (3.0, 0.1, 2.4), wall, name)
        box((0, ye - math.copysign(0.03, ye), 1.05), (0.8, 0.04, 2.0), toon("Car door", (0.5, 0.55, 0.62)), "Door")

    # ceiling light strips (white) and alarm strips (red), toggled by scale
    white = glow_mat("Ceiling light", (1.0, 0.95, 0.85), 1.1)
    red = glow_mat("Alarm light", (1.0, 0.08, 0.05), 5.0)
    whites, reds = [], []
    for sx in (-1, 1):
        whites.append(box((sx * 0.55, 0, 2.39), (0.12, 25, 0.02), white, "Light strip"))
        reds.append(box((sx * 0.55, 0, 2.385), (0.14, 25, 0.03), red, "Alarm strip"))

    # seats: groups of four around a table on each side
    for c in (-9, -6, -3, 0, 3, 6, 9):
        for sx in (-1, 1):
            for x in (sx * 0.62, sx * 1.12):
                for side in (1, -1):  # side=1: seat at c+0.75 facing -Y
                    y = c + side * 0.75
                    back_y = y + side * 0.26
                    box((x, y, 0.44), (0.46, 0.5, 0.12), seat_m, "Seat cushion", bevel=0.04)
                    box((x, y, 0.2), (0.4, 0.4, 0.38), metal, "Seat base")
                    box((x, back_y, 0.85), (0.46, 0.12, 0.85), seat_m, "Seat back", bevel=0.04)
                    box((x, back_y - side * 0.065, 1.13), (0.36, 0.02, 0.22), random.choice(covers), "Head cover")
            box((sx * 0.87, c, 0.74), (0.95, 0.56, 0.05), table_m, "Table", bevel=0.02)
            box((sx * 1.3, c, 0.5), (0.06, 0.12, 0.48), metal, "Table leg")
    return whites, reds


# ================================================================ outside world


def build_outside():
    """Everything outside the car, parented to an empty that slides along -Y."""
    world = empty("Outside")
    parts = []
    grass = toon("Field green", (0.45, 0.62, 0.28), 0.18)
    dirt = toon("Field dirt", (0.62, 0.48, 0.3), 0.18)
    gravel = toon("Gravel", (0.45, 0.4, 0.36), 0.15)
    parts.append(box((0, 250, -1.35), (400, 900, 0.1), dirt, "Ground"))
    parts.append(box((0, 250, -1.28), (5, 900, 0.1), gravel, "Track bed"))
    # field strips
    cols = [toon("Field a", (0.55, 0.72, 0.3), 0.18), toon("Field b", (0.85, 0.75, 0.3), 0.18), grass,
            toon("Field c", (0.4, 0.55, 0.25), 0.18)]
    for k in range(14):
        y = 150 + k * 18
        for sx in (-1, 1):
            parts.append(box((sx * 40, y, -1.27), (70, 17, 0.06), cols[k % 4], "Field strip"))
    # burning city along the first stretch (both sides, mostly window side -X)
    ruin = [toon("Ruin a", (0.62, 0.5, 0.45), 0.15), toon("Ruin b", (0.5, 0.45, 0.5), 0.15),
            toon("Ruin c", (0.72, 0.6, 0.45), 0.15), toon("Ruin d", (0.55, 0.38, 0.32), 0.15)]
    win = toon("Ruin window", (0.1, 0.08, 0.08), 0.0)
    fire = glow_mat("Fire", (1.0, 0.45, 0.08), 6.0)
    for i in range(60):
        sx = -1 if i % 4 else 1
        x = sx * random.uniform(9, 45)
        y = random.uniform(-30, 140)
        w, d, h = random.uniform(5, 9), random.uniform(5, 9), random.uniform(5, 20)
        b = box((x, y, h / 2 - 1.3), (d, w, h), random.choice(ruin), "Building")
        b.rotation_euler = (random.uniform(-0.05, 0.05), random.uniform(-0.05, 0.05), random.uniform(-0.2, 0.2))
        parts.append(b)
        for k in range(int(h // 4)):
            parts.append(box((x - sx * (d / 2 + 0.02), y, 1.5 + k * 3.5), (0.1, w * 0.6, 1.1), win, "Windows"))
        if random.random() < 0.35:
            parts.append(ball((x - sx * d / 2, y, h - 1.3), 1.4, fire, "Fire", scale=(1, 1, 0.8)))
    smoke = [toon("Smoke", (0.22, 0.21, 0.22), 0.12), toon("Smoke light", (0.36, 0.34, 0.34), 0.12)]
    for (x, y) in [(-25, 40), (-35, 75), (-18, 105), (30, 60), (-40, 20)]:
        for k in range(10):
            parts.append(ball((x + k * 0.8, y + random.uniform(-1, 1), 2 + k * 3.0), 1.8 + k * 0.6,
                              random.choice(smoke), "Smoke puff", seg=14))
    # power poles and trees along the fields
    pole_m = toon("Pole", (0.4, 0.28, 0.18), 0.15)
    leaf = [toon("Tree a", (0.25, 0.55, 0.25), 0.15), toon("Tree b", (0.45, 0.68, 0.25), 0.15)]
    for y in range(140, 330, 22):
        parts.append(rod((-6, y, -1.3), (-6, y, 7), 0.15, pole_m, "Power pole"))
        parts.append(box((-6, y, 6.5), (1.6, 0.12, 0.12), pole_m, "Pole arm"))
    for i in range(40):
        x = random.choice([-1, 1]) * random.uniform(10, 50)
        y = random.uniform(130, 340)
        parts.append(rod((x, y, -1.3), (x, y, 1.5), 0.25, pole_m, "Trunk"))
        parts.append(ball((x, y, 3.0), random.uniform(1.8, 2.8), random.choice(leaf), "Crown"))

    # the border: fence, floodlights, barrier, guard hut (no flags or national symbols)
    by = STOP_S
    fence = toon("Fence", (0.55, 0.6, 0.62), 0.15)
    for k in range(-20, 21):
        y = by + k * 2.5
        parts.append(rod((-7, y, -1.3), (-7, y, 1.6), 0.06, fence, "Fence post"))
    for z in (-0.3, 0.4, 1.1, 1.55):
        parts.append(box((-7, by, z), (0.03, 100, 0.03), fence, "Fence wire"))
    lamp = glow_mat("Flood", (1.0, 0.95, 0.75), 8.0)
    for k in (-24, -8, 8, 24):
        parts.append(rod((-11, by + k, -1.3), (-11, by + k, 8), 0.2, fence, "Light tower"))
        parts.append(box((-10.6, by + k, 8), (0.6, 1.4, 0.7), lamp, "Floodlight"))
    red_w = [toon("Barrier red", (0.9, 0.12, 0.1), 0.2), toon("Barrier white", (0.97, 0.97, 0.95), 0.3)]
    for k in range(8):
        parts.append(box((-14, by - 6 + k * 0.6, 0.1), (0.25, 0.6, 0.25), red_w[k % 2], "Barrier"))
    hut = toon("Hut", (0.35, 0.5, 0.3), 0.15)
    parts.append(box((-16, by + 4, 0.2), (3, 3, 3), hut, "Guard hut"))
    parts.append(box((-16, by + 4, 1.85), (3.6, 3.6, 0.3), toon("Hut roof", (0.85, 0.3, 0.2), 0.15), "Hut roof"))
    parts.append(box((-14.48, by + 4, 0.6), (0.06, 1.4, 0.8), toon("Hut window", (0.95, 0.85, 0.4), 1.0), "Hut win"))
    for p in parts:
        parent_keep(p, world)
    guards = []
    for i in range(3):
        g = Person(f"Guard{i}", 1.0, 0.2, dict(skin=(0.85, 0.62, 0.48), top=(0.3, 0.38, 0.22), pants=(0.28, 0.33, 0.2),
                                               shoes=(0.08, 0.08, 0.08), hair=(0.1, 0.07, 0.05), belt=(0.15, 0.1, 0.05)))
        g.add(ball(g.head_c + Vector((0, 0, 0.45 * g.R)), 1.08 * g.R, toon("Helmet", (0.25, 0.33, 0.2)), "helmet",
                   scale=(1, 1.05, 0.65)), g.p["head"])
        guards.append(g)
    return world, guards


def build_jet():
    grey = toon("Jet", (0.45, 0.48, 0.52), 0.15)
    jet = empty("Jet")
    parts = [rod((0, -3, 0), (0, 3, 0), 0.6, grey, "Jet body"),
             ball((0, 3.1, 0), 0.6, grey, "Jet nose", scale=(1, 1.8, 1)),
             box((0, 0, 0), (7, 1.8, 0.15), grey, "Jet wing"),
             box((0, -2.6, 0.9), (0.15, 1.2, 1.6), grey, "Jet tail")]
    for p in parts:
        parent_keep(p, jet)
    return jet


# ================================================================ props


def phone_screen_mat(name, path):
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
    for key, fn in (("call", "phone_call.png"), ("voice", "phone_voice.png")):
        bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, 0.0065))
        sc = bpy.context.object
        sc.scale = (0.07, 0.145, 1)
        bpy.ops.object.transform_apply(scale=True)  # keep_scale() toggles scale later
        sc.name = f"Phone screen {key}"
        sc.data.materials.append(phone_screen_mat(f"Screen {key}", os.path.join(HERE, "textures", fn)))
        parent_keep(sc, phone)
        screens[key] = sc
    phone.rotation_mode = "XYZ"
    return phone, screens


def keep_scale(o, f, visible, size=1.0):
    o.scale = (size, size, size) if visible else (0.001, 0.001, 0.001)
    o.keyframe_insert("scale", frame=f)


# ================================================================ animation


def build():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.fps = FPS
    scene.frame_start, scene.frame_end = F0, F1

    whites, reds = build_car()
    outside, guards = build_outside()
    jet = build_jet()
    blast = ball((-30, -10, 4), 1.0, glow_mat("Blast", (1.0, 0.55, 0.12), 14.0), "Blast")
    bpy.ops.object.light_add(type="POINT", location=(-2.5, 0.0, 1.6))
    flash = bpy.context.object
    flash.data.color = (1.0, 0.5, 0.15)

    lena, mom, rahim, jalal, sara = make_lena(), make_mom(), make_rahim(), make_jalal(), make_sara()
    radio = box((0, 0, 0), (0.07, 0.05, 0.16), toon("Radio", (0.12, 0.12, 0.13)), "Radio", bevel=0.01)
    radio_led = ball((0, 0, 0), 0.012, glow_mat("Radio LED", (0.2, 1.0, 0.3), 4.0), "Radio LED")
    ant = rod((0, 0, 0), (0, 0, 0.14), 0.006, toon("Radio", (0.12, 0.12, 0.13)), "Radio antenna")
    hp = rahim.p["handL"].matrix_world.translation.copy()
    for o, d in ((radio, Vector((0, 0.05, 0.02))), (radio_led, Vector((0.02, 0.08, 0.08))),
                 (ant, Vector((0.02, 0.05, 0.1)))):
        o.location = hp + d
        parent_keep(o, rahim.p["elbowL"])
    apple = ball((0, 0, 0), 0.055, toon("Apple", (0.88, 0.12, 0.1), 0.25), "Apple")
    stem = rod((0, 0, 0.05), (0, 0, 0.085), 0.006, toon("Stem", (0.35, 0.2, 0.1)), "Apple stem")
    leaf = ball((0.02, 0, 0.08), 0.02, toon("Leaf", (0.3, 0.65, 0.2), 0.25), "Apple leaf", scale=(1.6, 0.5, 0.4))
    for o in (stem, leaf):
        parent_keep(o, apple)

    seated = []  # background passengers sitting in other groups
    spots = [(-0.62, -3.75, 0), (-1.12, -3.75, 0), (0.62, -3.75, 0), (1.12, -6.75, 0), (-0.62, -6.75, 0),
             (0.62, 2.25, 180), (1.12, 3.75, 0)]
    for i, (sx, sy, fac) in enumerate(spots):
        seated.append((make_extra(i, 0.95), Vector((sx, sy, 0)), fac))
    standing = [make_extra(5, 1.0), make_extra(2, 0.98)]

    cam = make_camera(scene)
    arms = POVArms(cam)
    phone, screens = build_phone(cam)
    biscuit = box((0, 0, 0), (0.07, 0.05, 0.012), toon("Biscuit", (0.88, 0.68, 0.38), 0.25), "Biscuit")
    parent_local(biscuit, cam)

    rnd = random.Random(5)
    shake = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(-1, 1)) for _ in range(F1 + 3)]
    seat_cam = Vector((-0.62, 0.72, 1.22))
    biscuit_table = None

    for f in range(F0, F1 + 1):
        t = (f - 1) / FPS
        s_now = travelled(t)
        outside.location.y = -s_now
        outside.keyframe_insert("location", frame=f)
        moving = 1.0 - seg(t, 55.5, 57.5)

        # ---------------- lights
        alarm = 44.2 <= t < 50.0
        blink = alarm and int(t * 3) % 2 == 0
        for o in whites:
            keep_scale(o, f, not alarm)
        for o in reds:
            keep_scale(o, f, blink)
        jt = seg(t, 43.95, 44.5)
        jet.location = (-28, lerp(70, -90, jt), 14 - 3 * jt)
        jet.rotation_euler = (0, D(15), D(180))
        jet.keyframe_insert("location", frame=f)
        jet.keyframe_insert("rotation_euler", frame=f)
        bf = max(0.0, 1 - abs(t - 46.7) / 0.5)
        blast.scale = (0.001 + 12 * bf,) * 3
        blast.keyframe_insert("scale", frame=f)
        flash.data.energy = 900 * bf
        flash.data.keyframe_insert("energy", frame=f)

        # ---------------- camera
        if t < 23.2:  # walking in down the aisle
            u = seg(t, 20.0, 23.2)
            pos = Vector((0.0, lerp(7.5, 1.4, u), 1.55 + 0.03 * math.sin(2 * math.pi * t * 2.2)))
            yaw, pitch = 180, -8
        else:
            u = seg(t, 23.2, 24.2)
            pos = Vector((lerp(0.0, seat_cam.x, u), lerp(1.4, seat_cam.y, u), lerp(1.55, seat_cam.z, u)))
            yaw, pitch = 180, -12
        yaw = lerp(yaw, 188, seg(t, 20.4, 20.8) * (1 - seg(t, 21.9, 22.3)))  # Jalal waving (left)
        # window scene
        yaw = lerp(yaw, 128, seg(t, 26.0, 26.6)); pitch = lerp(pitch, -2, seg(t, 26.0, 26.6))
        yaw = lerp(yaw, 165, seg(t, 28.3, 28.7)); pitch = lerp(pitch, -14, seg(t, 28.3, 28.7))
        yaw = lerp(yaw, 222, seg(t, 29.8, 30.2))
        # phone
        yaw = lerp(yaw, 182, seg(t, 31.8, 32.2)); pitch = lerp(pitch, -48, seg(t, 31.8, 32.2))
        pitch = lerp(pitch, -14, seg(t, 35.2, 35.5)); pitch = lerp(pitch, -48, seg(t, 36.4, 36.7))
        # hunger
        pitch = lerp(pitch, -24, seg(t, 37.9, 38.3)); yaw = lerp(yaw, 172, seg(t, 37.9, 38.3))
        yaw = lerp(yaw, 205, seg(t, 41.0, 41.4)); yaw = lerp(yaw, 178, seg(t, 42.7, 43.0))
        # air raid: window (jet), aisle (Rahim), then duck under the table
        yaw = lerp(yaw, 100, seg(t, 44.0, 44.2)); pitch = lerp(pitch, 4, seg(t, 44.0, 44.2))
        yaw = lerp(yaw, 200, seg(t, 44.4, 44.65)); pitch = lerp(pitch, -4, seg(t, 44.4, 44.65))
        duck = seg(t, 45.9, 46.4) * (1 - seg(t, 50.0, 50.7))
        yaw = lerp(yaw, 180, seg(t, 45.9, 46.4)); pitch = lerp(pitch, -18, seg(t, 45.9, 46.4))
        # after: mum, Rahim with the radio in the aisle
        pitch = lerp(pitch, -8, seg(t, 50.0, 50.7))
        yaw = lerp(yaw, 205, seg(t, 51.4, 51.8)); pitch = lerp(pitch, 4, seg(t, 51.4, 51.8))
        yaw = lerp(yaw, 178, seg(t, 53.0, 53.3)); yaw = lerp(yaw, 205, seg(t, 54.4, 54.7))
        # border: window, Rahim, phone, mum + Lena standing, Jalal
        yaw = lerp(yaw, 98, seg(t, 56.0, 56.6)); pitch = lerp(pitch, 0, seg(t, 56.0, 56.6))
        yaw = lerp(yaw, 205, seg(t, 57.4, 57.8)); pitch = lerp(pitch, 6, seg(t, 57.4, 57.8))
        yaw = lerp(yaw, 182, seg(t, 60.0, 60.4)); pitch = lerp(pitch, -48, seg(t, 60.0, 60.4))
        yaw = lerp(yaw, 192, seg(t, 61.9, 62.3)); pitch = lerp(pitch, 8, seg(t, 61.9, 62.3))
        yaw = lerp(yaw, 222, seg(t, 64.0, 64.3))
        pos = pos + Vector((0.12 * duck, -0.2 * duck, -0.62 * duck))
        amp = 0.12 * moving + (0.25 if t < 23.2 else 0)
        for te, k in ((28.4, 2.0), (46.7, 4.5), (57.3, 1.5)):
            if te <= t < te + 0.6:
                amp += k * (1 - (t - te) / 0.6)
        sx_, sy_, sz_ = shake[f]
        cam.location = pos
        cam.rotation_euler = (D(90 + pitch + sx_ * amp), D(sy_ * amp * 0.6), D(yaw + sz_ * amp))
        cam.keyframe_insert("location", frame=f)
        cam.keyframe_insert("rotation_euler", frame=f)

        # ---------------- family
        # Lena: walks in ahead, sits at the window across the table
        if t < 22.4:
            u = seg(t, 20.0, 22.4)
            lpos = Vector((lerp(0.0, -1.12, seg(t, 21.8, 22.4)), lerp(6.4, -0.75, u), 0))
            lena.pose(f, t, lpos, facing=180 if t < 21.8 else lerp(180, 0, seg(t, 21.8, 22.4)), run=1 - seg(t, 21.8, 22.4),
                      run_rate=1.3, lean=0, sit=seg(t, 22.0, 22.4), seat_h=0.5, worry=1.3)
        else:
            look = (0, 0)
            reach2 = None
            win = seg(t, 26.2, 26.6) * (1 - seg(t, 28.5, 28.9))
            look = (lerp(0, 80, win), 5)
            if 38.0 <= t < 40.0:
                reach2 = (lerp(60, 95, seg(t, 38.0, 38.4)), -15)
            if 42.6 <= t < 44.0:
                reach2 = (70, 0)
            cower = seg(t, 45.8, 46.3) * (1 - seg(t, 50.0, 50.6))
            stand = seg(t, 61.4, 62.0)
            lpos = Vector((lerp(-1.12, -0.95, cower), lerp(-0.75, -0.2, cower), 0))
            lpos = lpos.lerp(Vector((-0.1, -0.35, 0)), stand)
            lena.pose(f, t, lpos, facing=lerp(0, 25, stand), sit=(1 - cower) * (1 - stand), seat_h=0.5,
                      crouch=cower * 1.0, look=look if not stand else (-15, 20), reach2=reach2,
                      reach=(110, -20) if stand else None, worry=1.5 if t > 44 else 1.1, lean=0)
        # Mom
        if t < 22.8:
            u = seg(t, 20.0, 22.8)
            mpos = Vector((lerp(0.0, -0.62, seg(t, 22.2, 22.8)), lerp(5.2, -0.75, u), 0))
            mom.pose(f, t, mpos, facing=180 if t < 22.2 else lerp(180, 0, seg(t, 22.2, 22.8)),
                     run=0.6 * (1 - seg(t, 22.2, 22.8)), run_rate=1.1, lean=0, sit=seg(t, 22.4, 22.8), seat_h=0.5)
        else:
            cower = seg(t, 45.8, 46.3) * (1 - seg(t, 50.0, 50.6))
            stand = seg(t, 61.2, 61.9)
            mpos = Vector((-0.62, lerp(-0.75, -0.35, cower), 0)).lerp(Vector((0.05, -0.15, 0)), stand)
            look = (lerp(0, -25, seg(t, 23.9, 24.1)), 0)
            if 53.0 < t < 55:
                look = (60, 5)  # towards the back of the train
            mom.pose(f, t, mpos, facing=lerp(0, 10, stand), sit=(1 - cower) * (1 - stand), seat_h=0.5,
                     crouch=cower * 0.8, hug=cower, look=look if not stand else (5, 15),
                     reach2=(40, -25) if stand else None, worry=1.6 if t > 44 else 1.2, lean=0)
        # Jalal (across the aisle, facing us)
        lean_in = seg(t, 41.0, 41.5) * (1 - seg(t, 42.8, 43.3))
        jc = seg(t, 45.8, 46.3) * (1 - seg(t, 50.0, 50.6))
        jalal.pose(f, t, Vector((0.62, -0.75, 0)), facing=lerp(0, 25, lean_in), sit=1 - jc * 0.6, seat_h=0.5,
                   crouch=jc * 0.6, wave=seg(t, 20.4, 20.7) * (1 - seg(t, 21.9, 22.2)),
                   reach=(lerp(30, 85, lean_in), lerp(0, 35, lean_in)) if lean_in > 0 else None,
                   look=(30, 8), lean=0, worry=1.3)
        # Sara (window seat beside Jalal)
        sc = seg(t, 45.8, 46.3) * (1 - seg(t, 50.0, 50.6))
        sara.pose(f, t, Vector((1.12, -0.75, 0)), facing=0, sit=1 - sc * 0.6, seat_h=0.5, crouch=sc * 0.6,
                  look=(lerp(30, 50, seg(t, 22.5, 22.8)), 5), reach=(150, 10) if sc > 0.5 else None, lean=0,
                  worry=1.2)
        # Rahim: runs down the aisle shouting (44-46), comes back with the radio (50.8-56), border (56-60)
        if t < 44.1:
            rpos = Vector((0.1, 30, 0))
            rahim.pose(f, t, rpos, facing=180)
        elif t < 46.6:
            u = seg(t, 44.1, 44.6)
            rpos = Vector((0.05, lerp(4.0, -1.6, u) - 6 * seg(t, 46.0, 46.6), 0))
            stop = seg(t, 44.6, 44.75)
            rahim.pose(f, t, rpos, facing=lerp(180, 0, stop) if t < 46.0 else 180, run=1 - stop * (t < 46.0),
                       run_rate=2.0, reach=(130, 20) if 44.6 < t < 46 else None, look=(0, 5))
        elif t < 50.6:
            rahim.pose(f, t, Vector((0.1, -30, 0)), facing=0)
        else:
            u = seg(t, 50.6, 51.4)
            rpos = Vector((0.1, lerp(-6.0, -1.5, u), 0))
            rahim.pose(f, t, rpos, facing=0, run=1 - u, run_rate=1.6,
                       reach2=(105, 10) if 51.5 < t < 56.5 else (20, 0), lean=-6,
                       wave=seg(t, 57.5, 57.7) * (1 - seg(t, 60.0, 60.3)), look=(0, 8), worry=1.6)
        led_on = 51.7 <= t <= 53.0 and int(t * 6) % 2 == 0
        keep_scale(radio_led, f, led_on or t < 51.7)

        # Apple: in Jalal's hand, then placed on our table
        if t < 42.6:
            apple.location = jalal.hand_world("R") + Vector((0, 0.04, 0.06))
            keep = 41.0 <= t
        else:
            apple.location = Vector((-0.8, -0.18, 0.82))
            keep = True
        apple.keyframe_insert("location", frame=f)
        keep_scale(apple, f, keep)

        # background passengers
        for i, (e, p0, fac) in enumerate(seated):
            c = seg(t, 45.9, 46.5) * (1 - seg(t, 50.0, 50.8))
            e.pose(f, t, p0, facing=fac, sit=1 - c * 0.6, seat_h=0.5, crouch=c * 0.6, look=(10 * math.sin(i), 0),
                   worry=1.3, lean=0)
        for i, e in enumerate(standing):
            c = seg(t, 45.9, 46.5) * (1 - seg(t, 50.0, 50.8))
            e.pose(f, t, Vector((0.05 + 0.1 * i, -4.8 - 1.3 * i, 0)), facing=0 if i else 180, crouch=c,
                   reach=(165, 0) if c < 0.5 else None, look=(30, 0), worry=1.4)
        for i, g in enumerate(guards):
            gp = Vector((-9.5 - i * 1.5, STOP_S - s_now + (i - 1) * 3.0, -1.3))
            g.pose(f, t, gp, facing=-90 + i * 20, look=(0, 0), worry=0.3)

        # ---------------- POV hands and props
        phone_vis = 31.9 <= t < 38.0 or 59.9 <= t < 62.4
        keep_scale(phone, f, phone_vis, size=1.4)  # a small phone in one hand
        keep_scale(screens["call"], f, t < 40)
        keep_scale(screens["voice"], f, t >= 40)
        phone.location = (0.06, -0.21, -0.46)
        phone.rotation_euler = (D(-25), 0, D(-4))
        phone.keyframe_insert("location", frame=f)
        phone.keyframe_insert("rotation_euler", frame=f)
        bis_vis = 39.6 <= t < 42.8
        keep_scale(biscuit, f, bis_vis)
        biscuit.location = (0.12, -0.3, -0.42)
        biscuit.keyframe_insert("location", frame=f)
        if t < 23.2:
            sw = 0.05 * math.sin(2 * math.pi * t * 1.1)
            arms.set(f, "L", (-0.3, -0.45 + sw, -0.45))
            arms.set(f, "R", (0.3, -0.45 - sw, -0.45))
        elif phone_vis:
            arms.set(f, "R", (0.1, -0.33, -0.45))
            arms.set(f, "L", (-0.26, -0.42, -0.46))
        elif bis_vis:
            arms.set(f, "R", (0.13, -0.32, -0.4))
            arms.set(f, "L", world_to_cam(cam, lena.hand_world("L")) if t < 40.0 else (-0.25, -0.4, -0.45))
        elif 38.0 <= t < 39.6:
            arms.set(f, "L", world_to_cam(cam, lena.hand_world("L")))
            arms.set(f, "R", (0.25, -0.4, -0.45))
        elif duck > 0.3 and 46.8 <= t < 50.0:
            arms.set(f, "L", (-0.15, -0.2, -0.5))
            arms.set(f, "R", (0.15, -0.22, -0.5))
        else:
            arms.set(f, "L", (-0.28, -0.42, -0.46))
            arms.set(f, "R", (0.28, -0.42, -0.46))

    bpy.ops.object.light_add(type="SUN", rotation=(D(55), D(25), D(70)))
    sun = bpy.context.object
    sun.data.energy = 2.2
    sun.data.color = (1.0, 0.88, 0.72)
    setup_render(scene, sky=(0.78, 0.66, 0.55), sky_strength=0.65)
    scene.frame_set(F0)
    return scene


if __name__ == "__main__":
    run_cli(build(), "train_wagon.blend")
