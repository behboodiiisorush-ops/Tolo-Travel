"""
«پناهگاه ۱ — نُه دقیقه» — night, the emergency alert.  One scene with three places:

    house   (around the origin): the phone alert, mum packing, Lena on the sofa
    street  (x ≈ 100): sirens, people running, the park, the bunker entrance
    bunker  (inside the concrete block in the park): the heavy door, the flash, the dark,
            the torch, the radio, knocking on the door

All beats follow times.py (the recorded voices).  Rendered on twos; post.py doubles the frames
and draws the countdown, the captions, the flash and the question card.

    python shelter1.py --still 49,361
    python shelter1.py --render --range 1 1900
"""

import math
import os
import random
import sys

import bpy
from mathutils import Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403,E402
from captions import END, FLASH_AFTER, KEY_OF  # noqa: E402

random.seed(7)
T = KEY_OF
EYE = 1.55
SX = 100.0                       # the street runs along Y at x = SX
DOOR_Y = 97.0                    # the bunker's front wall (door opening at x = SX + 4)
BX = SX + 4.0


def at(key, k=0):
    return T[key][k]


def yaw_to(d):
    return math.degrees(math.atan2(-d.x, d.y)) % 360


def pitch_to(d):
    return math.degrees(math.atan2(d.z, d.xy.length))


def look(pos, target):
    d = Vector(target) - pos
    return yaw_to(d), pitch_to(d)


def lerp_yaw(a, b, u):
    d = (b - a + 180) % 360 - 180
    return a + d * u


# ================================================================ places


def build_house():
    wall = toon("House wall", (0.85, 0.78, 0.65), 0.12)
    floor_m = toon("House floor", (0.55, 0.38, 0.25), 0.1)
    rug = toon("Rug", (0.6, 0.15, 0.2), 0.1)
    box((0, 0, -0.05), (6.2, 5.2, 0.1), floor_m, "Floor")
    box((0, 0.3, 0.005), (2.6, 2.0, 0.01), rug, "Rug")
    box((0, 0, 2.75), (6.2, 5.2, 0.1), toon("Ceiling", (0.92, 0.9, 0.85), 0.1), "Ceiling")
    box((-3.05, 0, 1.35), (0.1, 5.2, 2.7), wall, "Wall left")
    box((3.05, 0, 1.35), (0.1, 5.2, 2.7), wall, "Wall right")
    box((0, -2.55, 1.35), (6.2, 0.1, 2.7), wall, "Wall back")
    box((0, -2.5, 1.05), (0.95, 0.04, 2.1), toon("House door", (0.45, 0.28, 0.18), 0.1), "Door")
    # front wall with a window: the night sky outside glows red
    for (x0, x1) in ((-3.1, 0.6), (2.4, 3.1)):
        box(((x0 + x1) / 2, 2.55, 1.35), (x1 - x0, 0.1, 2.7), wall, "Wall front")
    box((1.5, 2.55, 0.5), (1.8, 0.1, 1.0), wall, "Wall under window")
    box((1.5, 2.55, 2.35), (1.8, 0.1, 0.8), wall, "Wall over window")
    box((1.5, 2.62, 1.5), (1.8, 0.02, 1.0), glow_mat("Night sky", (0.6, 0.15, 0.1), 0.8), "Window sky")
    box((1.5, 2.5, 1.5), (0.05, 0.05, 1.0), toon("Window frame", (0.95, 0.95, 0.95), 0.2), "Window bar")
    # sofa, coffee table, TV, dining table with the bag
    sofa = toon("Sofa", (0.2, 0.45, 0.55), 0.12)
    box((-1.8, 1.6, 0.25), (1.9, 0.8, 0.5), sofa, "Sofa seat", bevel=0.08)
    box((-1.8, 2.0, 0.65), (1.9, 0.25, 0.8), sofa, "Sofa back", bevel=0.08)
    for sx in (-1, 1):
        box((-1.8 + sx * 0.95, 1.6, 0.45), (0.2, 0.8, 0.5), sofa, "Sofa arm", bevel=0.06)
    box((-1.8, 0.5, 0.22), (1.0, 0.55, 0.06), toon("Wood", (0.6, 0.42, 0.25), 0.12), "Coffee table", bevel=0.02)
    box((-2.95, -0.2, 1.3), (0.08, 1.3, 0.8), toon("TV frame", (0.08, 0.08, 0.09), 0.05), "TV")
    tv = box((-2.9, -0.2, 1.3), (0.02, 1.15, 0.66), glow_mat("TV snow", (0.75, 0.78, 0.8), 1.2), "TV screen")
    box((1.6, 0.6, 0.75), (1.4, 0.9, 0.05), toon("Wood", (0.6, 0.42, 0.25), 0.12), "Table", bevel=0.02)
    for dx in (-0.6, 0.6):
        for dy in (-0.35, 0.35):
            box((1.6 + dx, 0.6 + dy, 0.37), (0.06, 0.06, 0.74), toon("Wood", (0.6, 0.42, 0.25), 0.12), "Leg")
    box((1.3, 0.55, 0.95), (0.5, 0.25, 0.35), toon("Mom bag", (0.85, 0.55, 0.15)), "Bag", bevel=0.04)
    for k in range(3):
        rod((1.9 + k * 0.12, 0.7, 0.78), (1.9 + k * 0.12, 0.7, 1.05), 0.035,
            toon("Bottle", (0.55, 0.8, 0.95), 0.3), "Bottle")
    bpy.ops.object.light_add(type="AREA", location=(0.0, 0.2, 2.6))
    lt = no_cam(bpy.context.object)
    lt.data.energy = 120
    lt.data.size = 2.0
    lt.data.color = (1.0, 0.88, 0.7)
    return tv


def build_street():
    asphalt = toon("Asphalt", (0.22, 0.22, 0.25), 0.1)
    side = toon("Sidewalk", (0.5, 0.48, 0.46), 0.12)
    grass = toon("Park grass", (0.22, 0.35, 0.2), 0.1)
    line = toon("Road line", (0.95, 0.9, 0.6), 0.4)
    box((SX, 60, -0.05), (8, 120, 0.1), asphalt, "Road")
    for sx in (-1, 1):
        box((SX + sx * 5.5, 55, 0.05), (3, 90, 0.1), side, "Sidewalk")
    for y in range(4, 116, 6):
        box((SX, y, 0.005), (0.18, 2.5, 0.01), line, "Road line")
    box((SX + 4, 112, -0.04), (40, 34, 0.1), grass, "Park")
    box((SX, 40, -0.06), (300, 300, 0.1), toon("Ground", (0.3, 0.27, 0.24), 0.1), "Ground")
    # buildings, some windows lit
    cols = [(0.62, 0.5, 0.45), (0.5, 0.45, 0.55), (0.7, 0.62, 0.48), (0.45, 0.5, 0.55)]
    lit = glow_mat("Lit window", (1.0, 0.8, 0.45), 2.0)
    darkw = toon("Dark window", (0.08, 0.08, 0.1), 0.0)
    for sx in (-1, 1):
        y = 10
        while y < 92:
            w = random.uniform(8, 13)
            h = random.uniform(9, 22)
            x = SX + sx * 13
            box((x, y + w / 2, h / 2), (10, w - 0.6, h), toon(f"Building {y}", random.choice(cols)), "Building")
            for fl in range(int(h // 3.2)):
                for k in range(int(w // 3)):
                    wy = y + 1.5 + k * 3
                    box((x - sx * 5.02, wy, 1.8 + fl * 3.2), (0.05, 1.2, 1.4),
                        lit if random.random() < 0.35 else darkw, "Window")
            y += w
    # street lights
    pole = toon("Pole", (0.3, 0.3, 0.33), 0.1)
    head = glow_mat("Street lamp", (1.0, 0.85, 0.55), 6.0)
    for y in range(20, 100, 16):
        for sx in (-1, 1):
            rod((SX + sx * 4.3, y, 0), (SX + sx * 4.3, y, 6), 0.08, pole, "Lamp pole")
            box((SX + sx * 3.8, y, 6.0), (1.0, 0.35, 0.15), head, "Lamp head")
        bpy.ops.object.light_add(type="POINT", location=(SX, y, 5.5))
        lt = no_cam(bpy.context.object)
        lt.data.energy = 500
        lt.data.color = (1.0, 0.82, 0.55)
    # abandoned cars, doors open
    car_c = [(0.75, 0.15, 0.15), (0.2, 0.35, 0.7), (0.9, 0.85, 0.8), (0.25, 0.25, 0.27), (0.9, 0.65, 0.1)]
    for k, (cx, cy, rot) in enumerate([(SX - 2, 62, 0.2), (SX + 2, 70, -0.4), (SX - 1.5, 81, 1.3),
                                         (SX + 2.2, 52, 0.05), (SX - 2.3, 90, -0.2)]):
        root = empty(f"Car{k}", (cx, cy, 0))
        m = toon(f"Car {k}", car_c[k % 5], 0.15)
        parts = [box((cx, cy, 0.55), (1.8, 4.2, 0.7), m, "Car body", bevel=0.15),
                 box((cx, cy - 0.2, 1.15), (1.6, 2.2, 0.55), m, "Car cabin", bevel=0.12),
                 box((cx, cy - 0.2, 1.15), (1.62, 1.9, 0.4), toon("Car glass", (0.15, 0.2, 0.3), 0.05), "Car glass"),
                 box((cx + 0.95, cy + 0.2, 0.75), (0.06, 1.0, 0.7), m, "Car door open")]
        parts[-1].rotation_euler = (0, 0, -0.9)
        for wx in (-0.85, 0.85):
            for wy in (-1.3, 1.3):
                bpy.ops.mesh.primitive_cylinder_add(radius=0.33, depth=0.25, location=(cx + wx, cy + wy, 0.33),
                                                    rotation=(0, D(90), 0), vertices=16)
                parts.append(finish(bpy.context.object, toon("Tyre", (0.08, 0.08, 0.08)), "Tyre", True))
        for p in parts:
            parent_keep(p, root)
        root.rotation_euler = (0, 0, rot)
    # park trees
    trunk = toon("Trunk", (0.3, 0.22, 0.15), 0.1)
    leaf = [toon("Tree a", (0.2, 0.38, 0.2), 0.12), toon("Tree b", (0.28, 0.45, 0.22), 0.12)]
    for k in range(18):
        x = SX + random.uniform(-16, 22)
        y = random.uniform(96, 128)
        if abs(x - BX) < 5 and y < 113:
            continue
        rod((x, y, 0), (x, y, 2.4), 0.2, trunk, "Trunk")
        ball((x, y, 3.8), random.uniform(1.5, 2.3), random.choice(leaf), "Crown")


def build_bunker():
    """A low concrete block in the park: a door in its front wall, a corridor inside."""
    conc = toon("Concrete", (0.55, 0.55, 0.52), 0.12)
    inner = toon("Concrete inside", (0.48, 0.5, 0.48), 0.1)
    x0, x1, y0, y1, h = BX - 2.0, BX + 2.0, DOOR_Y, DOOR_Y + 14.0, 2.8
    box((BX, (y0 + y1) / 2, h + 0.2), (4.4, 14.4, 0.4), conc, "Bunker roof", bevel=0.05)
    box((BX, (y0 + y1) / 2, 0.02), (4.0, 14.0, 0.04), inner, "Bunker floor")
    for x in (x0, x1):
        box((x, (y0 + y1) / 2, h / 2), (0.4, 14.4, h), conc, "Bunker side")
    box((BX, y1, h / 2), (4.4, 0.4, h), conc, "Bunker back")
    for (a, b) in ((x0 - 0.2, BX - 0.7), (BX + 0.7, x1 + 0.2)):
        box(((a + b) / 2, y0, h / 2), (b - a, 0.4, h), conc, "Bunker front")
    box((BX, y0, 2.45), (1.4, 0.4, 0.7), conc, "Bunker lintel")
    # warning stripes around the door
    yel = toon("Stripe yellow", (0.95, 0.75, 0.1), 0.3)
    blk = toon("Stripe black", (0.06, 0.06, 0.06), 0.0)
    for k in range(10):
        box((BX - 0.9, y0 - 0.21, 0.15 + k * 0.23), (0.15, 0.02, 0.2), yel if k % 2 else blk, "Stripe")
        box((BX + 0.9, y0 - 0.21, 0.15 + k * 0.23), (0.15, 0.02, 0.2), yel if k % 2 else blk, "Stripe")
    # light strips round the door frame (inside): they blaze with the flash
    flash = glow_mat("Door flash", (1.0, 1.0, 0.95), 0.0)
    gaps = [box((BX, y0 + 0.21, 2.12), (1.4, 0.02, 0.04), flash, "Gap top"),
            box((BX - 0.72, y0 + 0.21, 1.05), (0.04, 0.02, 2.1), flash, "Gap left"),
            box((BX + 0.72, y0 + 0.21, 1.05), (0.04, 0.02, 2.1), flash, "Gap right")]
    # the heavy door, hinged on its right edge (seen from outside), opening inwards
    hinge = empty("Bunker door hinge", (BX + 0.7, y0 + 0.2, 0))
    steel = toon("Steel door", (0.42, 0.45, 0.48), 0.15)
    door_parts = [box((BX, y0 + 0.28, 1.05), (1.4, 0.16, 2.1), steel, "Bunker door", bevel=0.03)]
    for k in range(3):
        door_parts.append(box((BX, y0 + 0.37, 0.45 + k * 0.6), (1.2, 0.03, 0.08), steel, "Door rib"))
    bpy.ops.mesh.primitive_torus_add(location=(BX, y0 + 0.4, 1.1), rotation=(D(90), 0, 0), major_radius=0.2,
                                     minor_radius=0.03, major_segments=20, minor_segments=6)
    door_parts.append(finish(bpy.context.object, toon("Wheel", (0.75, 0.15, 0.1), 0.2), "Door wheel", True))
    for p in door_parts:
        parent_keep(p, hinge)
    hinge.rotation_mode = "XYZ"
    # benches with people, a crate with the radio, the ceiling lamp
    bench = toon("Bench", (0.45, 0.33, 0.22), 0.1)
    for sx in (-1, 1):
        box((BX + sx * 1.55, (y0 + y1) / 2 + 1.5, 0.45), (0.5, 9, 0.1), bench, "Bench", bevel=0.03)
    box((BX - 1.2, DOOR_Y + 5.5, 0.3), (0.7, 0.5, 0.6), toon("Crate", (0.5, 0.4, 0.22), 0.12), "Crate", bevel=0.03)
    radio = box((BX - 1.2, DOOR_Y + 5.5, 0.72), (0.4, 0.18, 0.24), toon("Radio", (0.2, 0.22, 0.2), 0.1), "Radio",
                bevel=0.02)
    rod((BX - 1.05, DOOR_Y + 5.5, 0.84), (BX - 0.95, DOOR_Y + 5.5, 1.2), 0.008, toon("Radio", (0.2, 0.22, 0.2)),
        "Radio antenna")
    led = ball((BX - 1.32, DOOR_Y + 5.41, 0.75), 0.02, glow_mat("Radio LED", (0.2, 1.0, 0.3), 5.0), "Radio LED")
    box((BX - 1.2, DOOR_Y + 5.41, 0.68), (0.2, 0.01, 0.1), glow_mat("Radio dial", (1.0, 0.7, 0.3), 1.5), "Radio dial")
    bpy.ops.object.light_add(type="POINT", location=(BX, DOOR_Y + 4.0, 2.4))
    lamp = no_cam(bpy.context.object)
    lamp.data.energy = 120
    lamp.data.color = (1.0, 0.9, 0.75)
    lamp_bulb = ball((BX, DOOR_Y + 4.0, 2.7), 0.12, glow_mat("Bunker bulb", (1.0, 0.9, 0.7), 5.0), "Bulb")
    bpy.ops.object.light_add(type="POINT", location=(BX, DOOR_Y + 1.0, 1.4))
    burst = no_cam(bpy.context.object)
    burst.data.energy = 0
    burst.data.color = (1.0, 1.0, 0.95)
    return hinge, gaps, flash, lamp, lamp_bulb, burst, led


def build_phone(cam):
    phone = empty("Phone")
    parent_local(phone, cam)
    body = box((0, 0, 0), (0.08, 0.16, 0.012), toon("Phone case", (0.12, 0.12, 0.14), 0.1), "Phone body",
               bevel=0.008)
    parent_keep(body, phone)
    m = bpy.data.materials.new("Phone alert")
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = bpy.data.images.load(os.path.join(HERE, "textures", "phone_alert.png"))
    e = nt.nodes.new("ShaderNodeEmission")
    e.inputs["Strength"].default_value = 1.2
    nt.links.new(tex.outputs["Color"], e.inputs["Color"])
    nt.links.new(e.outputs[0], out.inputs["Surface"])
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, 0.0065))
    sc = bpy.context.object
    sc.scale = (0.07, 0.145, 1)
    bpy.ops.object.transform_apply(scale=True)
    sc.name = "Phone screen"
    sc.data.materials.append(m)
    parent_keep(sc, phone)
    phone.rotation_mode = "XYZ"
    return phone


def build_torch(cam):
    root = empty("Torch")
    parent_local(root, cam)
    body = rod((0, 0, 0.0), (0, 0, -0.2), 0.022, toon("Torch body", (0.15, 0.15, 0.17), 0.1), "Torch body")
    head = rod((0, 0, -0.2), (0, 0, -0.25), 0.034, toon("Torch head", (0.75, 0.6, 0.1), 0.2), "Torch head")
    lens = ball((0, 0, -0.252), 0.03, glow_mat("Torch lens", (1.0, 0.97, 0.85), 8.0), "Torch lens",
                scale=(1, 1, 0.3))
    for o in (body, head, lens):
        parent_local(o, root)
    bpy.ops.object.light_add(type="SPOT", location=(0, 0, -0.26))
    spot = bpy.context.object
    spot.data.energy = 0
    spot.data.spot_size = D(40)
    spot.data.spot_blend = 0.35
    spot.data.color = (1.0, 0.95, 0.8)
    spot.data.shadow_soft_size = 0.02
    parent_local(spot, root)
    return root, spot


def darken_toon(k):
    for m in bpy.data.materials:
        if m.use_nodes and any(n.type == "BSDF_TOON" for n in m.node_tree.nodes):
            for n in m.node_tree.nodes:
                if n.type == "EMISSION":
                    n.inputs["Strength"].default_value *= k


def make_guard():
    g = Person("Guard", 1.04, 0.2, dict(skin=(0.82, 0.6, 0.46), top=(0.95, 0.5, 0.08), pants=(0.2, 0.22, 0.28),
                                        shoes=(0.08, 0.08, 0.08), hair=(0.1, 0.07, 0.05), belt=(0.15, 0.1, 0.05),
                                        iris=(0.25, 0.18, 0.1), brow=1.4, lid=0.3, gloves=(0.2, 0.2, 0.2)))
    g.add(ball(g.head_c + Vector((0, 0, 0.45 * g.R)), 1.08 * g.R, toon("Hard hat", (0.95, 0.85, 0.15), 0.2),
               "hard hat", scale=(1, 1.05, 0.62)), g.p["head"])
    z = 0.86 * g.s + 0.29 * g.s
    g.add(box((0, 0.17, z), (0.5, 0.02, 0.06), toon("Reflective", (0.92, 0.92, 0.92), 0.6), "vest stripe"),
          g.p["torso"])
    return g


# ================================================================ animation


def build():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.fps = FPS
    scene.frame_start, scene.frame_end = 1, int(END * FPS)
    scene.frame_step = 2

    tv = build_house()
    build_street()
    hinge, gaps, flash_m, lamp, bulb, burst, led = build_bunker()
    lena, mom, jalal, guard = make_lena(), make_mom(), make_jalal(), make_guard()
    cane = rod((0, 0, 0), (0, 0, -0.9), 0.02, toon("Cane", (0.35, 0.22, 0.12)), "Jalal cane")
    hp = jalal.hand_world("R")
    cane.location = hp + Vector((0, 0.05, -0.45))
    parent_keep(cane, jalal.p["elbowR"])
    bunny_parts = [o for o in bpy.data.objects if o.name.startswith("Lena bunny")]
    runners = [make_extra(i, 0.98) for i in range(6)]
    sitters = [make_extra(i + 1, 0.95) for i in range(5)]

    cam = make_camera(scene)
    arms = POVArms(cam)
    arms.reach = 1.2
    phone = build_phone(cam)
    torch, spot = build_torch(cam)

    rnd = random.Random(3)
    shake = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(-1, 1)) for _ in range(int(END * FPS) + 3)]

    street0 = at("mom2") - 1.4                 # cut from the house to the street
    arrive = at("guard1") - 0.4                # at the bunker door
    enter0, enter1 = at("jalal1") - 0.9, at("jalal1") - 0.1
    close0, close1 = at("guard2"), at("guard2", 1) + 0.2
    flash_t = at("n2", 1) + FLASH_AFTER
    dark_t = flash_t + 1.2
    torch_t = at("lena3") - 0.9
    knock0 = at("n3") - 2.4

    P0 = Vector((SX - 0.8, 58.0, EYE))
    P1 = Vector((BX - 0.2, DOOR_Y - 2.4, EYE))
    INSIDE = Vector((BX - 0.1, DOOR_Y + 2.2, EYE))
    lena_house = Vector((-1.8, 1.5, 0))
    mom_house = Vector((1.6, 1.25, 0))
    me_house = Vector((0.2, -1.2, EYE))
    bunny_drop = None

    for f in range(1, int(END * FPS) + 1):
        t = (f - 1) / FPS
        house = t < street0
        street = street0 <= t < enter1
        inside = t >= enter1

        # ---------------- the TV snow flickers, sirens light the window
        tv.scale = (1, 1, 1) if (int(t * 12) % 3) else (1, 1, 0.97)
        tv.keyframe_insert("scale", frame=f)

        # ---------------- camera position
        if house:
            pos = me_house.copy()
        elif t < arrive:
            u = (t - street0) / (arrive - street0)
            pos = P0.lerp(P1, u)
            pos.z += 0.07 * abs(math.sin(math.pi * t * 3.0))
        elif t < enter0:
            pos = P1.copy()
        else:
            u = seg(t, enter0, enter1)
            pos = P1.lerp(INSIDE, u)
        run_dir = (P1 - P0).normalized()

        # ---------------- where we look
        if house:
            yaw, pitch = 0, -55                                          # the phone
            k = seg(t, at("mom1") - 0.5, at("mom1"))
            ym, pm = look(pos, mom_house + Vector((0, 0, 1.3)))
            yaw = lerp_yaw(yaw, ym, k); pitch = lerp(pitch, pm, k)
            k = seg(t, at("lena1") - 0.4, at("lena1"))
            yl, pl = look(pos, lena_house + Vector((0, 0, 0.8)))
            yaw = lerp_yaw(yaw, yl, k); pitch = lerp(pitch, pl, k)
            k = seg(t, at("me1", 1), street0)                             # towards the door
            yaw = lerp_yaw(yaw, 180, k); pitch = lerp(pitch, -5, k)
        elif t < arrive:
            yaw, pitch = yaw_to(run_dir), -4
            k = seg(t, at("mom2") - 0.2, at("mom2") + 0.3) * (1 - seg(t, at("mom2", 1), at("mom2", 1) + 0.5))
            yaw = lerp_yaw(yaw, yaw_to(run_dir) + 20, k)
            k = seg(t, at("me2") - 0.2, at("me2") + 0.3) * (1 - seg(t, at("me2", 1), at("me2", 1) + 0.4))
            yaw = lerp_yaw(yaw, yaw_to(run_dir) - 35, k); pitch = lerp(pitch, -16, k)
            k = seg(t, at("lena2") - 0.1, at("lena2") + 0.4) * (1 - seg(t, at("lena2", 1) - 0.3, at("lena2", 1) + 0.3))
            yaw = lerp_yaw(yaw, yaw_to(run_dir) - 150, k); pitch = lerp(pitch, -25, k)   # the bunny on the road
        elif not inside:
            yaw, pitch = look(pos, Vector((BX - 0.3, DOOR_Y + 0.8, 1.7)))                 # the guard in the door
            k = seg(t, at("me3") - 0.2, at("me3") + 0.2)
            pitch = lerp(pitch, pitch + 6, k)
        else:
            # inside, turned back to the door; Jalal outside; the flash; the dark
            yaw, pitch = look(pos, Vector((BX, DOOR_Y - 6.0, 1.3)))
            k = seg(t, enter1, enter1 + 0.6)
            yaw = lerp_yaw(0, yaw, k)
            pitch = lerp(pitch, -8, seg(t, close1, close1 + 0.5))
            if t >= torch_t:
                yl, pl = look(pos, Vector((BX + 0.5, DOOR_Y + 1.6, 0.95)))                # Lena's face
                k = seg(t, at("lena3") - 0.4, at("lena3"))
                yaw = lerp_yaw(yaw, yl, k); pitch = lerp(pitch, pl, k)
                yr, pr = look(pos, Vector((BX - 1.2, DOOR_Y + 5.5, 0.75)))               # the radio
                k = seg(t, at("radio1") - 0.6, at("radio1"))
                yaw = lerp_yaw(yaw, yr, k); pitch = lerp(pitch, pr, k)
                yd, pd = look(pos, Vector((BX, DOOR_Y, 1.2)))                            # the door
                k = seg(t, knock0 - 0.2, knock0 + 0.4)
                yaw = lerp_yaw(yaw, yd, k); pitch = lerp(pitch, pd, k)
        amp = 0.05
        if street:
            amp = 0.3
        if flash_t <= t < flash_t + 2.0:
            amp += 4.0 * (1 - (t - flash_t) / 2.0)
        sx_, sy_, sz_ = shake[f]
        cam.location = pos
        cam.rotation_euler = (D(90 + pitch + sx_ * amp), D(sy_ * amp * 0.6), D(yaw + sz_ * amp))
        cam.keyframe_insert("location", frame=f)
        cam.keyframe_insert("rotation_euler", frame=f)

        # ---------------- the phone (in the house), the torch (in the dark)
        phone_on = t < at("mom1") - 0.4
        phone.scale = (1.5,) * 3 if phone_on else (0.001,) * 3
        phone.location = (0.0, -0.2, -0.42)
        phone.rotation_euler = (D(-20), 0, 0)
        for prop in ("scale", "location", "rotation_euler"):
            phone.keyframe_insert(prop, frame=f)
        on = t >= torch_t
        spot.data.energy = 900 if on else 0
        spot.data.keyframe_insert("energy", frame=f)
        torch.scale = (1,) * 3 if on else (0.001,) * 3
        torch.location = (0.2, -0.3, -0.42)
        torch.rotation_euler = (D(-8), D(-6), 0)
        for prop in ("scale", "location", "rotation_euler"):
            torch.keyframe_insert(prop, frame=f)

        # ---------------- bunker door, flash, lamps, radio LED
        swing = seg(t, close0, close1)
        hinge.rotation_euler = (0, 0, D(-95) * (1 - swing))
        hinge.keyframe_insert("rotation_euler", frame=f)
        fl = max(0.0, 1 - abs(t - flash_t - 0.2) / 0.7) if t >= flash_t - 0.1 else 0.0
        flash_m.node_tree.nodes["Emission"].inputs["Strength"].default_value = 60 * fl
        flash_m.node_tree.nodes["Emission"].inputs["Strength"].keyframe_insert("default_value", frame=f)
        burst.data.energy = 3000 * fl
        burst.data.keyframe_insert("energy", frame=f)
        lamp_on = t < flash_t + 0.3 or (flash_t + 0.6 < t < flash_t + 0.75)
        lamp.data.energy = 120 if lamp_on else 0
        lamp.data.keyframe_insert("energy", frame=f)
        bulb.scale = (1,) * 3 if lamp_on else (0.001,) * 3
        bulb.keyframe_insert("scale", frame=f)
        led.scale = (1,) * 3 if (t < dark_t or (at("radio1") - 0.6 < t and int(t * 4) % 2 == 0)) else (0.001,) * 3
        led.keyframe_insert("scale", frame=f)

        # ---------------- our hands
        bpy.context.view_layer.update()
        if phone_on:
            arms.set(f, "R", (0.06, -0.33, -0.43))
            arms.set(f, "L", (-0.08, -0.34, -0.44))
        elif house:
            arms.set(f, "L", (-0.3, -0.42, -0.46))
            target = world_to_cam(cam, lena.hand_world("L"))
            arms.set(f, "R", target if (t > at("me1") and target.z < -0.1) else Vector((0.28, -0.42, -0.46)))
        elif not inside:
            target = world_to_cam(cam, lena.hand_world("L"))
            arms.set(f, "R", target if target.z < -0.1 else Vector((0.28, -0.42, -0.46)))
            arms.set(f, "L", (-0.3, -0.42 + 0.06 * math.sin(t * 9), -0.46))
        else:
            arms.set(f, "R", (0.2, -0.3, -0.42) if on else (0.28, -0.42, -0.46))
            arms.set(f, "L", (-0.3, -0.42, -0.46))

        # ---------------- Lena
        if house:
            stand = seg(t, at("me1"), at("me1") + 0.8)
            lp = lena_house.lerp(Vector((-0.6, -0.4, 0)), seg(t, at("me1") + 0.4, street0))
            lena.pose(f, t, lp, facing=lerp(180, 160, stand), sit=1 - stand, seat_h=0.45, lean=0,
                      look=(0, 15), hug=0.5 * (1 - stand), worry=2.0, reach2=(lerp(40, 90, stand), -20))
            bunny_vis = True
        elif not inside:
            u = (min(t, arrive) - street0) / (arrive - street0)
            lp = P0.lerp(P1, u) + Vector((0.95, -0.2, -EYE))
            lena.pose(f, t, lp, facing=yaw_to(run_dir) + (0 if t < arrive else 0), run=1.0 if t < arrive else 0,
                      run_rate=2.2, lean=-8, look=(-20 if at("lena2") < t < at("lena2", 1) else 0, 10),
                      reach2=(70, 40), worry=2.0)
            bunny_vis = t < at("lena2")
        else:
            lp = Vector((BX + 0.55, DOOR_Y + 1.6, 0))
            lena.pose(f, t, lp, facing=lerp_yaw(0, 47, seg(t, enter1, enter1 + 1.0)), crouch=0.5 * seg(t, flash_t, dark_t),
                      hug=0.6 * seg(t, flash_t, dark_t), look=(0, lerp(20, 40, seg(t, flash_t, dark_t))),
                      worry=2.0, lean=0)
            bunny_vis = False
        if bunny_vis and not inside:
            show(bunny_parts, f, True)
        else:
            show(bunny_parts, f, False)
        # the bunny she dropped, lying on the road behind us
        if street and t >= at("lena2"):
            if bunny_drop is None:
                bunny_drop = Vector(lena.hand_world("R")); bunny_drop.z = 0.08
                drop = bunny(bunny_drop, empty("Dropped bunny", tuple(bunny_drop)), "Dropped bunny")
                for ff in range(1, f):
                    show(drop, ff, False)
            show(drop, f, True)
        elif bunny_drop is not None:
            show(drop, f, not inside or t < enter1)

        # ---------------- Mum
        if house:
            mom.pose(f, t, mom_house, facing=180, crouch=0.25, lean=0, look=(lerp(-20, 0, seg(t, at("mom1"), at("mom1") + 0.4)), 0),
                     reach=(70, 10), reach2=(65, -10), worry=1.8)
        elif not inside:
            u = (min(t, arrive) - street0) / (arrive - street0)
            mp = P0.lerp(P1, u) + Vector((-1.1, 2.4, -EYE))
            turn = seg(t, at("mom2") - 0.2, at("mom2") + 0.2) * (1 - seg(t, at("mom2", 1), at("mom2", 1) + 0.3))
            mom.pose(f, t, mp, facing=yaw_to(run_dir) + 160 * turn, run=1.0 if t < arrive else 0, run_rate=2.0,
                     lean=-8, reach=(lerp(10, 160, turn), 30) if turn > 0 else None, look=(0, 5), worry=2.0)
        else:
            mom.pose(f, t, Vector((BX + 1.1, DOOR_Y + 2.6, 0)), facing=200, crouch=0.4 * seg(t, flash_t, dark_t),
                     hug=0.5 * seg(t, flash_t, dark_t), look=(0, 10), worry=2.0, lean=0)

        # ---------------- the guard at the door
        aside = seg(t, enter0, enter1)
        gpos = Vector((BX - 0.1, DOOR_Y + 0.9, 0)).lerp(Vector((BX - 1.25, DOOR_Y + 0.9, 0)), aside)
        gpos = gpos.lerp(Vector((BX - 1.45, DOOR_Y + 3.4, 0)), seg(t, close1 + 0.4, close1 + 1.6))
        pushing = seg(t, close0 - 0.2, close0 + 0.2) * (1 - seg(t, close1 + 0.2, close1 + 0.6))
        guard.pose(f, t, gpos, facing=lerp_yaw(180, 140, aside), reach=(lerp(140 if at("guard1") < t < at("guard1", 1) else 30, 90, pushing), 10),
                   reach2=(lerp(20, 90, pushing), -10), look=(0, 0), worry=1.4, lean=0)

        # ---------------- Jalal, running late with his cane
        ju = seg(t, street0 + 3.0, close1 + 1.0)
        jp = Vector((SX - 2.5, 64.0, 0)).lerp(Vector((BX - 1.0, DOOR_Y - 7.0, 0)), ju)
        jalal.pose(f, t, jp, facing=yaw_to(Vector((BX, DOOR_Y, 0)) - jp), run=0.6 if ju < 1 else 0, run_rate=1.3,
                   lean=-10, reach2=(150, 20) if at("jalal1") - 0.3 < t < at("jalal1", 1) + 1.0 else (30, 0),
                   look=(0, 10), worry=2.0)

        # ---------------- people running past, people sitting inside
        for i, r in enumerate(runners):
            y = 52 + i * 6 + (t - street0) * (3.0 + 0.4 * i)
            x = SX + (-3.2 + (i % 3) * 3.0)
            rp = Vector((x, min(y, DOOR_Y - 3 - i * 0.8), 0))
            r.pose(f, t, rp, facing=0, run=1.0 if y < DOOR_Y - 3 - i * 0.8 else 0, run_rate=2.2 + 0.1 * i,
                   lean=-10, look=(0, 0), worry=1.8, reach=(150, 0) if i % 2 else None)
        for i, s in enumerate(sitters):
            sxp = BX + (-1.5 if i % 2 else 1.5)
            s.pose(f, t, Vector((sxp, DOOR_Y + 4.5 + i * 1.3, 0)), facing=90 if i % 2 == 0 else -90, sit=1,
                   seat_h=0.5, lean=0, crouch=0.3 * seg(t, flash_t, dark_t), hug=0.4 * seg(t, flash_t, dark_t),
                   look=(0, -15), worry=1.8)

    bpy.ops.object.light_add(type="SUN", rotation=(D(65), D(10), D(-30)))
    moon = bpy.context.object
    moon.data.energy = 0.35
    moon.data.color = (0.65, 0.65, 1.0)
    darken_toon(0.35)
    setup_render(scene, sky=(0.1, 0.06, 0.1), sky_strength=0.9)
    scene.frame_set(1)
    return scene


if __name__ == "__main__":
    run_cli(build(), "shelter1.blend")
