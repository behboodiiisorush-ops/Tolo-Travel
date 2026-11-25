"""
«واگن آخر ۵ — شهر خاموش» — dawn.  The train runs away from the border, through a grey dead city;
the people left in it walk slowly, like zombies.  Inside our car (the episode-1 car): Lena at the
window, Jalal across the aisle, Rahim with his radio.  A bus lies across the track; the train stops;
the figures outside start walking towards it.

    python part5.py --still 49,361
    python part5.py --render --range 1 1700
"""

import math
import os
import random
import sys

import bpy
from mathutils import Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403,E402
from captions import END, KEY_OF  # noqa: E402

random.seed(55)
T = KEY_OF
GROUND = -1.3
SEAT_CAM = Vector((-0.62, 0.72, 1.22))


def at(key, k=0):
    return T[key][k]


def yaw_to(d):
    return math.degrees(math.atan2(-d.x, d.y)) % 360


def pitch_to(d):
    return math.degrees(math.atan2(d.z, d.xy.length))


def lerp_yaw(a, b, u):
    d = (b - a + 180) % 360 - 180
    return a + d * u


def speed(t):
    """m/s: cruising, slowing past the figures, braking hard for the bus."""
    v = 8.0
    v = lerp(v, 5.0, seg(t, at("n2") - 1.0, at("n2") + 1.0))
    v = v * (1 - seg(t, at("rahim2") - 0.3, at("rahim2") + 2.2))
    v = v + 7.5 * seg(t, at("rahim4") + 0.4, at("rahim4") + 4.5)    # the track is clear: go
    return v


_S = [0.0]
for _f in range(1, int(END * FPS) + 4):
    _S.append(_S[-1] + speed((_f - 1) / FPS) / FPS)


def travelled(t):
    return _S[max(0, min(len(_S) - 1, int(round(t * FPS))))]


S_STOP = travelled(at("rahim2") + 2.3)
BUS_Y = S_STOP + 10.0   # outside coordinates: the bus lies across the track ahead of us
TRACTOR0 = Vector((-9.5, BUS_Y - 7.5, GROUND))   # the old tractor, left of the track (outside coordinates)
TRACTOR1 = Vector((-6.8, BUS_Y - 3.0, GROUND))   # where it ends up, shoving the bus off the rails


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



def give_radio(rahim):
    radio = box((0, 0, 0), (0.07, 0.05, 0.16), toon("Radio", (0.12, 0.12, 0.13)), "Radio", bevel=0.01)
    led = ball((0, 0, 0), 0.012, glow_mat("Radio LED", (0.2, 1.0, 0.3), 4.0), "Radio LED")
    ant = rod((0, 0, 0), (0, 0, 0.14), 0.006, toon("Radio", (0.12, 0.12, 0.13)), "Radio antenna")
    hp = rahim.hand_world("L")
    for o, d in ((radio, Vector((0, 0.05, 0.02))), (led, Vector((0.02, 0.08, 0.08))), (ant, Vector((0.02, 0.05, 0.1)))):
        o.location = hp + d
        parent_keep(o, rahim.p["elbowL"])
    return led




def build_outside():
    """The dead city along the track (outside coordinates; the empty slides past the car)."""
    world = empty("Outside")
    parts = []
    grey = [toon(f"Dead wall {k}", c, 0.12) for k, c in enumerate(
        [(0.55, 0.55, 0.56), (0.45, 0.46, 0.48), (0.62, 0.6, 0.58), (0.38, 0.39, 0.41)])]
    dark = toon("Dead window", (0.08, 0.08, 0.09), 0.0)
    broken = toon("Broken window", (0.22, 0.22, 0.24), 0.05)
    parts.append(box((0, 200, GROUND - 0.05), (400, 900, 0.1), toon("Ash ground", (0.42, 0.41, 0.4), 0.1), "Ground"))
    parts.append(box((0, 200, GROUND + 0.02), (5, 900, 0.1), toon("Gravel", (0.4, 0.38, 0.36), 0.1), "Track bed"))
    parts.append(box((-14, 200, GROUND + 0.01), (10, 900, 0.06), toon("Dead road", (0.3, 0.3, 0.32), 0.1), "Road"))
    for sx in (-1, 1):
        y = -60.0
        while y < S_STOP + 120:
            w = random.uniform(10, 18)
            h = random.uniform(10, 34)
            x = sx * random.uniform(24, 30)
            parts.append(box((x, y + w / 2, GROUND + h / 2), (14, w - 1, h), random.choice(grey), "Dead building"))
            for fl in range(int(h // 3.2)):
                for k in range(int(w // 3)):
                    wm = dark if random.random() < 0.7 else broken
                    parts.append(box((x - sx * 7.02, y + 1.5 + k * 3, GROUND + 1.8 + fl * 3.2), (0.05, 1.2, 1.4), wm,
                                     "Dead window"))
            y += w
    # wrecked cars on the road, a burnt-out bus across the track ahead
    for k in range(18):
        cy = random.uniform(-40, S_STOP + 80)
        m = toon(f"Wreck {k}", (0.3, 0.3, 0.32), 0.08)
        b = box((-14 + random.uniform(-3, 3), cy, GROUND + 0.6), (1.9, 4.2, 0.8), m, "Wreck", bevel=0.12)
        b.rotation_euler = (0, 0, random.uniform(-0.7, 0.7))
        parts.append(b)
    bus_root = empty("Bus root", (-4.5, BUS_Y, GROUND))
    bus_m = toon("Bus", (0.95, 0.72, 0.1), 0.2)
    bus = box((-4.5, BUS_Y, GROUND + 1.3), (13, 3.0, 2.6), bus_m, "Bus", bevel=0.15)
    bus.rotation_euler = (D(85), 0, D(-14))   # on its side, across the track and out to our side
    parent_keep(bus, bus_root)
    for k in range(5):
        w = box((-4.5 - 4.8 + k * 2.4, BUS_Y - 1.4, GROUND + 1.3), (1.7, 0.05, 1.1), dark, "Bus window")
        parent_keep(w, bus_root)
    parent_keep(bus_root, world)
    bus_root.rotation_mode = "XYZ"
    # poles, dead trees, smoke
    pole = toon("Dead pole", (0.25, 0.22, 0.2), 0.08)
    for y in range(-50, int(S_STOP + 100), 22):
        parts.append(rod((5, y, GROUND), (5, y, GROUND + 8), 0.14, pole, "Pole"))
    smoke = toon("Smoke", (0.3, 0.3, 0.32), 0.1)
    for (x, y) in [(-40, 60), (-55, 160), (38, 120), (-45, S_STOP + 30)]:
        for k in range(10):
            parts.append(ball((x + k * 0.8, y, GROUND + 3 + k * 3.5), 2 + k * 0.6, smoke, "Smoke", seg=12))
    for p in parts:
        parent_keep(p, world)
    return world, bus_root


def build_tractor(world):
    """An old orange tractor with a front blade (outside coordinates, parented to the world)."""
    root = empty("Tractor", tuple(TRACTOR0))
    orange = toon("Tractor", (0.95, 0.45, 0.1), 0.2)
    black = toon("Tyre", (0.08, 0.08, 0.08), 0.05)
    grey = toon("Tractor metal", (0.45, 0.45, 0.48), 0.12)
    x, y, z = TRACTOR0
    parts = [box((x, y, z + 1.0), (1.4, 3.0, 1.0), orange, "Tractor body", bevel=0.1),
             box((x, y - 0.6, z + 1.75), (1.3, 1.2, 0.08), orange, "Tractor seat deck"),
             box((x, y + 2.0, z + 0.7), (2.6, 0.2, 1.2), grey, "Tractor blade", bevel=0.05),
             rod((x + 0.4, y + 0.9, z + 1.5), (x + 0.4, y + 0.9, z + 2.6), 0.07, black, "Exhaust"),
             box((x, y - 0.75, z + 2.0), (0.5, 0.5, 0.15), black, "Tractor seat")]
    for sx, sy, r in ((-0.95, -0.9, 0.75), (0.95, -0.9, 0.75), (-0.8, 1.0, 0.45), (0.8, 1.0, 0.45)):
        bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=0.4, location=(x + sx, y + sy, z + r),
                                            rotation=(0, D(90), 0), vertices=18)
        parts.append(finish(bpy.context.object, black, "Tractor wheel", True))
    for o in parts:
        parent_keep(o, root)
    puffs = []
    sm = toon("Exhaust smoke", (0.12, 0.12, 0.13), 0.05)
    for k in range(6):
        b = ball((x + 0.4, y + 0.9, z + 2.8), 0.25, sm, "Exhaust puff", seg=10)
        parent_keep(b, root)
        puffs.append(b)
    parent_keep(root, world)
    return root, puffs


def build_helicopter():
    """A helicopter with a searchlight crossing the sky (car coordinates)."""
    root = empty("Helicopter")
    body_m = toon("Heli", (0.28, 0.32, 0.3), 0.15)
    dark = toon("Heli dark", (0.08, 0.08, 0.09), 0.05)
    glass = toon("Heli glass", (0.3, 0.45, 0.55), 0.3)
    parts = [ball((0, 0, 0), 1.6, body_m, "Heli body", scale=(1, 1.5, 0.9)),
             ball((0, 1.3, 0.2), 1.0, glass, "Heli canopy", scale=(1, 0.9, 0.7)),
             rod((0, -1.8, 0.2), (0, -6.5, 0.6), 0.25, body_m, "Heli tail"),
             box((0, -6.5, 1.2), (0.1, 0.8, 1.3), body_m, "Heli fin"),
             rod((-0.9, -1.2, -1.6), (-0.9, 1.8, -1.6), 0.06, dark, "Skid"),
             rod((0.9, -1.2, -1.6), (0.9, 1.8, -1.6), 0.06, dark, "Skid"),
             rod((0, 0, 1.3), (0, 0, 1.7), 0.12, dark, "Rotor mast")]
    for o in parts:
        parent_keep(o, root)
    rotor = empty("Rotor", (0, 0, 1.75))
    parent_keep(rotor, root)
    for a in (0, 90):
        b = box((0, 0, 1.75), (0.35, 12.0, 0.05), dark, "Blade")
        b.rotation_euler = (0, 0, D(a))
        parent_keep(b, rotor)
    rotor.rotation_mode = "XYZ"
    lamp = ball((0, 1.2, -1.2), 0.25, glow_mat("Searchlight", (1.0, 0.97, 0.85), 12.0), "Searchlight")
    parent_keep(lamp, root)
    bpy.ops.object.light_add(type="SPOT", location=(0, 1.2, -1.3))
    spot = bpy.context.object
    spot.data.energy = 60000
    spot.data.spot_size = D(18)
    spot.data.color = (1.0, 0.97, 0.88)
    parent_keep(spot, root)
    root.rotation_mode = "XYZ"
    root.scale = (1.5, 1.5, 1.5)
    return root, rotor


def make_runner(i):
    """A cheap far-away figure for the crowd that chases the train: grey body, head, glowing eyes."""
    root = empty(f"Runner{i}")
    col = random.choice([(0.4, 0.4, 0.42), (0.35, 0.32, 0.3), (0.3, 0.33, 0.38)])
    parts = [rod((0, 0, 0.1), (0, 0, 1.0), 0.13, toon(f"Runner legs {i}", (0.2, 0.2, 0.22), 0.05), "Legs"),
             box((0, 0, 1.3), (0.42, 0.26, 0.62), toon(f"Runner top {i}", col, 0.08), "Body", bevel=0.08),
             ball((0, 0, 1.78), 0.18, toon("Runner skin", (0.52, 0.6, 0.47), 0.1), "Head")]
    eyes = glow_mat("Runner eyes", (0.85, 0.95, 0.7), 3.0)
    for sx in (-0.06, 0.06):
        parts.append(ball((sx, 0.16, 1.8), 0.03, eyes, "Eye", seg=6))
    for sx in (-0.26, 0.26):
        parts.append(rod((sx, 0, 1.55), (sx, 0.55, 1.45), 0.06, toon(f"Runner top {i}", col, 0.08), "Arm"))
    for o in parts:
        parent_keep(o, root)
    root.rotation_mode = "XYZ"
    return root


def build_fog():
    """Grey fog outside the windows: veils parallel to the train, kept out of the outlines."""
    col = bpy.data.collections.new("Fog")
    bpy.context.scene.collection.children.link(col)
    m = bpy.data.materials.new("Fog veil")
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    mix = nt.nodes.new("ShaderNodeMixShader")
    mix.inputs[0].default_value = 0.16
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = (0.7, 0.7, 0.72, 1)
    em.inputs["Strength"].default_value = 1.0
    nt.links.new(tr.outputs[0], mix.inputs[1])
    nt.links.new(em.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs["Surface"])
    for k, x in enumerate((-5.0, -8.5, -12.0, -16.0, -20.0, -25.0, 6.0, 10.0, 16.0)):
        bpy.ops.mesh.primitive_plane_add(size=1, location=(x, 0, 3.0), rotation=(0, D(90), 0))
        v = bpy.context.object
        v.scale = (9, 200, 1)
        v.name = "Fog veil"
        v.data.materials.append(m)
        v.visible_shadow = False
        v.visible_diffuse = False
        for c in list(v.users_collection):
            c.objects.unlink(v)
        col.objects.link(v)
    return col


def make_walker(i):
    """A grey, slow figure: one of the people left in the city."""
    looks = [((0.55, 0.62, 0.5), (0.35, 0.32, 0.3), (0.25, 0.25, 0.3)), ((0.6, 0.62, 0.52), (0.4, 0.3, 0.3), (0.3, 0.28, 0.26)),
             ((0.5, 0.58, 0.48), (0.3, 0.35, 0.4), (0.2, 0.2, 0.22)), ((0.58, 0.6, 0.5), (0.45, 0.42, 0.35), (0.28, 0.3, 0.3))]
    skin, top, pants = looks[i % len(looks)]
    p = Person(f"Walker{i}", random.uniform(0.92, 1.03), 0.2,
               dict(skin=skin, top=top, pants=pants, shoes=(0.12, 0.1, 0.09), hair=(0.2, 0.18, 0.16),
                    iris=(0.85, 0.95, 0.7), lid=0.4, brow=1.1))
    hair_cap(p, (0.2, 0.18, 0.16), scale=(1, 0.95, 0.9), off=(0, -0.15, 0.18), r=1.03)
    for m in bpy.data.materials:
        if m.name.startswith(f"Walker{i} iris") and m.use_nodes:
            for n in m.node_tree.nodes:
                if n.type == "EMISSION":
                    n.inputs["Strength"].default_value = 3.0
    return p


def make_zombie_jalal():
    """Jalal as he came back: grey-green skin, pale glowing eyes, dirty clothes (no blood, no gore)."""
    z = make_jalal()
    for m in bpy.data.materials:
        if not m.use_nodes:
            continue
        if m.name.startswith("Jalal skin"):
            col, glow = (0.52, 0.6, 0.45), None
        elif m.name.startswith("Jalal iris"):
            col, glow = (0.85, 0.95, 0.7), 3.0
        elif m.name.startswith(("Jalal top", "Jalal pants", "Jalal cap")):
            col, glow = None, None
            for n in m.node_tree.nodes:
                if n.type in ("BSDF_TOON", "EMISSION"):
                    c = n.inputs["Color"].default_value
                    n.inputs["Color"].default_value = (c[0] * 0.5 + 0.1, c[1] * 0.5 + 0.1, c[2] * 0.5 + 0.1, 1)
            continue
        else:
            continue
        for n in m.node_tree.nodes:
            if n.type in ("BSDF_TOON", "EMISSION"):
                n.inputs["Color"].default_value = (*col, 1)
            if glow and n.type == "EMISSION":
                n.inputs["Strength"].default_value = glow
    # torn sleeves: a few dark rips
    rip = toon("Rip", (0.1, 0.09, 0.08), 0.0)
    for side in ("L", "R"):
        z.add(box(z.hand_world(side) + Vector((0, 0, 0.25)), (0.09, 0.02, 0.04), rip, "rip"), z.p[f"elbow{side}"])
    return z


# ================================================================ animation


def build():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.fps = FPS
    scene.frame_start, scene.frame_end = 1, int(END * FPS)
    scene.frame_step = 2

    build_car()
    outside, bus_root = build_outside()
    tractor, puffs = build_tractor(outside)
    heli, rotor = build_helicopter()
    runners = [make_runner(i) for i in range(18)]
    rr = random.Random(21)
    runner_home = [Vector((-rr.uniform(9, 26), S_STOP + rr.uniform(-25, 25), GROUND)) for _ in runners]
    runner_pos = [h.copy() for h in runner_home]
    cap = [ball((0, 0, 0), 0.16, toon("Jalal cap", (0.85, 0.75, 0.5)), "Fallen cap", scale=(1.1, 1.2, 0.45))]
    fog_col = build_fog()
    lena, rahim, jalal = make_lena(), make_rahim(), make_jalal()
    led = give_radio(rahim)
    walkers = [make_walker(i) for i in range(20)]
    rnd = random.Random(8)
    w_home = []
    look_ts = [at("n2") + 0.5 * k for k in range(7)] + [at("lena2") + 0.3, 1.0, 2.0, 3.0]
    for i in range(len(walkers)):
        near = i < 8   # these are near where the train will stop
        if near:
            y = S_STOP + rnd.uniform(-14, 18)
            x = -rnd.uniform(5, 14)
        else:          # along the line, placed where they pass our window while we look out
            tt_ = look_ts[(i - 8) % len(look_ts)]
            y = travelled(tt_) + rnd.uniform(-6, 2)
            x = -rnd.uniform(3.5, 8)
        w_home.append((Vector((x, y, GROUND)), rnd.uniform(0, 6.28), rnd.uniform(0.3, 0.6), near))
    passengers = [make_extra(i, 0.95) for i in (1, 3, 6)]
    cam = make_camera(scene)
    arms = POVArms(cam)
    rs = random.Random(5)
    shake = [(rs.uniform(-1, 1), rs.uniform(-1, 1), rs.uniform(-1, 1)) for _ in range(int(END * FPS) + 3)]
    stop_t = at("rahim2") + 2.2
    approach0 = at("me1") - 1.6
    t_out0 = at("jalal2", 1) + 0.8          # Jalal is outside
    seat_t = t_out0 + 3.0                    # on the tractor
    push0, push1 = seat_t + 0.5, at("jalal3") + 0.4
    gone_t = at("lena4") + 1.0               # the crowd has swallowed him
    chase0 = at("rahim4") + 0.4
    heli0 = at("lena5") - 1.6
    wpos = [None] * 20

    for f in range(1, int(END * FPS) + 1):
        t = (f - 1) / FPS
        s_now = travelled(t)
        outside.location.y = -s_now
        outside.keyframe_insert("location", frame=f)
        v = speed(t)

        # ---------------- the tractor drives up and shoves the bus off the track; exhaust puffs
        push = seg(t, push0, push1)
        tractor_now = TRACTOR0.lerp(TRACTOR1, seg(t, seat_t + 0.1, push0 + 0.3))
        tractor_now = tractor_now + Vector((-2.2 * push, 0.4 * push, 0))
        tractor.location = tractor_now
        tractor.rotation_euler = (0, 0, D(-6) * push)
        tractor.keyframe_insert("location", frame=f)
        tractor.keyframe_insert("rotation_euler", frame=f)
        bus_root.location = Vector((-4.5, BUS_Y, GROUND)) + Vector((-8.5 * push, 1.2 * push, 0))
        bus_root.rotation_euler = (0, 0, D(28) * push)
        bus_root.keyframe_insert("location", frame=f)
        bus_root.keyframe_insert("rotation_euler", frame=f)
        running = seat_t <= t
        for k, b in enumerate(puffs):
            ph = ((t * 1.6 + k / len(puffs)) % 1.0)
            b.location = TRACTOR0 + Vector((0.4, 0.9, 2.8 + 2.5 * ph))
            b.scale = ((0.6 + 2.2 * ph) if running else 0.001,) * 3
            b.keyframe_insert("location", frame=f)
            b.keyframe_insert("scale", frame=f)
        # ---------------- the helicopter crosses the sky over the city
        hu = seg(t, heli0, END + 6)
        heli.location = Vector((-48, 18, 24)).lerp(Vector((-22, 95, 26)), hu)
        heli.rotation_euler = (D(-6), D(4 * math.sin(t)), D(-35))
        heli.keyframe_insert("location", frame=f)
        heli.keyframe_insert("rotation_euler", frame=f)
        rotor.rotation_euler = (0, 0, t * 25.0)
        rotor.keyframe_insert("rotation_euler", frame=f)

        # ---------------- camera, sitting in our seat
        pos = SEAT_CAM.copy()
        yaw, pitch = 112, 0                                                          # the window
        k = seg(t, at("rahim1") - 0.5, at("rahim1")) * (1 - seg(t, at("rahim1", 1), at("rahim1", 1) + 0.5))
        yaw = lerp_yaw(yaw, 203, k); pitch = lerp(pitch, 6, k)                       # Rahim in the aisle
        k = seg(t, at("lena1") - 0.5, at("lena1")) * (1 - seg(t, at("jalal1") - 0.3, at("jalal1")))
        yaw = lerp_yaw(yaw, 186, k); pitch = lerp(pitch, -4, k)                      # Lena at the window
        k = seg(t, at("jalal1") - 0.3, at("jalal1")) * (1 - seg(t, at("jalal1", 1), at("jalal1", 1) + 0.5))
        yaw = lerp_yaw(yaw, 220, k); pitch = lerp(pitch, -2, k)                      # Jalal
        k = seg(t, at("rahim2") - 0.2, at("rahim2") + 0.2) * (1 - seg(t, at("rahim2", 1), at("rahim2", 1) + 0.6))
        yaw = lerp_yaw(yaw, 200, k); pitch = lerp(pitch, 6, k)                       # Rahim shouting
        k = seg(t, at("rahim3") - 1.4, at("rahim3") - 0.6) * (1 - seg(t, at("rahim3", 1) - 0.4, at("rahim3", 1)))
        yaw = lerp_yaw(yaw, 24, k); pitch = lerp(pitch, -4, k)                       # the bus ahead
        lean = k
        k = seg(t, at("jalal2") - 0.4, at("jalal2")) * (1 - seg(t, at("jalal2", 1), at("jalal2", 1) + 0.4))
        yaw = lerp_yaw(yaw, 212, k); pitch = lerp(pitch, 14, k)                      # Jalal standing up
        k = seg(t, at("lena3") - 0.3, at("lena3")) * (1 - seg(t, at("lena3", 1), at("lena3", 1) + 0.4))
        yaw = lerp_yaw(yaw, 186, k); pitch = lerp(pitch, -4, k)                      # Lena crying
        # out of the window: Jalal, the tractor, the bus, the swarm
        tw = tractor_now + Vector((0, -s_now, 1.5))
        window = seg(t, at("jalal2", 1) + 0.3, at("jalal2", 1) + 1.0) * (1 - seg(t, at("rahim4") - 0.5, at("rahim4")))
        yt, pt = yaw_to(tw - Vector((-1.0, 1.15, 1.3))), pitch_to(tw - Vector((-1.0, 1.15, 1.3)))
        yaw = lerp_yaw(yaw, yt, window); pitch = lerp(pitch, pt, window)
        k = seg(t, at("lena4") - 0.3, at("lena4")) * (1 - seg(t, at("lena4", 1), at("lena4", 1) + 0.3))
        yaw = lerp_yaw(yaw, 186, k); pitch = lerp(pitch, -2, k)                      # Lena screams
        inside_look = k
        k = seg(t, at("rahim4") - 0.5, at("rahim4")) * (1 - seg(t, at("rahim4", 1), at("rahim4", 1) + 0.4))
        yaw = lerp_yaw(yaw, 200, k); pitch = lerp(pitch, 6, k)                       # Rahim: go!
        inside_look = max(inside_look, k)
        back = seg(t, at("rahim4", 1) + 0.2, at("rahim4", 1) + 0.8) * (1 - seg(t, at("lena5") - 0.4, at("lena5")))
        yaw = lerp_yaw(yaw, 132, back); pitch = lerp(pitch, -8, back)                # the crowd running after us
        k = seg(t, at("lena5") - 0.4, at("lena5")) * (1 - seg(t, at("lena5", 1) - 0.2, at("lena5", 1) + 0.2))
        yaw = lerp_yaw(yaw, 190, k); pitch = lerp(pitch, 4, k)                       # Lena points up
        inside_look = max(inside_look, k)
        hw = heli.location - Vector((-1.0, 1.15, 1.3))
        up = seg(t, at("lena5", 1) - 0.2, at("lena5", 1) + 0.6)
        yaw = lerp_yaw(yaw, yaw_to(hw), up); pitch = lerp(pitch, min(30, pitch_to(hw)), up)   # the helicopter
        win_pos = max(lean, window, back, up) * (1 - inside_look)   # lean to the glass only when looking out
        pos = pos.lerp(Vector((-1.2, 1.25, 1.3)), win_pos * 0.9)
        amp = 0.06 + 0.1 * min(1.0, v / 8.0)
        for te, kk in ((at("rahim2") - 0.2, 2.6), (stop_t - 0.3, 1.6), (chase0, 1.4)):
            if te <= t < te + 0.8:
                amp += kk * (1 - (t - te) / 0.8)
        sx_, sy_, sz_ = shake[f]
        cam.location = pos
        cam.rotation_euler = (D(90 + pitch + sx_ * amp), D(sy_ * amp * 0.6), D(yaw + sz_ * amp))
        cam.keyframe_insert("location", frame=f)
        cam.keyframe_insert("rotation_euler", frame=f)

        # ---------------- Lena at the window seat across the table
        win = seg(t, 0.5, 1.5) * (1 - seg(t, at("jalal1") - 0.2, at("jalal1") + 0.3))
        win = max(win, seg(t, at("lena2") - 0.6, at("lena2")) * (1 - seg(t, at("rahim2"), at("rahim2") + 0.5)))
        cry = seg(t, at("lena3") - 0.3, at("lena3")) * (1 - seg(t, at("jalal2"), at("jalal2") + 0.5))
        win = max(win, seg(t, at("jalal3") - 0.6, at("jalal3")) * (1 - seg(t, at("rahim4"), at("rahim4") + 0.5)))
        point = seg(t, at("lena5") - 0.3, at("lena5") + 0.2)
        lena.pose(f, t, Vector((-1.12, -0.75, 0)), facing=0, sit=1, seat_h=0.5, lean=0,
                  look=(lerp(lerp(0, 75, win), 60, point), lerp(lerp(5, -10, cry), 35, point)),
                  hug=0.4 * cry, worry=lerp(1.4, 2.0, max(cry, win)),
                  reach2=(160, 35) if point > 0.1 else ((lerp(40, 85, win), -10) if win > 0.1 else None))
        # ---------------- Jalal across the aisle; stands up at the end
        stand = seg(t, at("jalal2") - 0.5, at("jalal2") + 0.3)
        lean_in = seg(t, at("jalal1") - 0.3, at("jalal1")) * (1 - seg(t, at("jalal1", 1), at("jalal1", 1) + 0.5))
        if t < t_out0:
            jpos = Vector((0.62, -0.75, 0)).lerp(Vector((0.2, -0.3, 0)), stand)
            jpos = jpos.lerp(Vector((0.1, -8.0, 0)), seg(t, at("jalal2", 1), t_out0))     # down the aisle, out
            jalal.pose(f, t, jpos, facing=lerp(lerp(0, 30, lean_in), 20, stand) if t < at("jalal2", 1) else 180,
                       sit=1 - stand, seat_h=0.5, lean=0, run=0.6 * seg(t, at("jalal2", 1), t_out0),
                       reach=(lerp(30, 85, lean_in), lerp(0, 35, lean_in)) if lean_in > 0 else None,
                       look=(lerp(30, 0, stand), lerp(5, 18, stand)), worry=lerp(1.2, 0.4, stand))
        elif t < gone_t:
            seat = tractor_now + Vector((0, -0.75, 1.2))
            run_out = seg(t, t_out0, seat_t)
            op = Vector((-2.6, S_STOP - 3.0, GROUND)).lerp(seat, run_out)
            op.z = lerp(GROUND, seat.z, seg(t, seat_t - 0.5, seat_t))
            down = seg(t, at("lena4"), gone_t)
            wp = op + Vector((0, -s_now, -0.8 * down))
            jalal.pose(f, t, wp, facing=yaw_to(seat - Vector((-2.6, S_STOP - 3.0, GROUND))) if t < seat_t else 0,
                       run=1.0 if t < seat_t else 0.0, run_rate=1.6, sit=seg(t, seat_t - 0.3, seat_t) * (1 - down),
                       seat_h=0.5, crouch=0.8 * down, lean=-6,
                       reach=(90, 10) if t >= seat_t else None, reach2=(90, -10) if t >= seat_t else None,
                       look=(lerp(0, 70, seg(t, at("jalal3") - 0.3, at("jalal3"))) if t < at("lena4") else 0, 10),
                       worry=lerp(0.5, 2.0, seg(t, at("jalal3") - 1.0, at("jalal3"))))
        else:
            jalal.pose(f, t, Vector((0, -300, -50)), facing=0)
        cap_vis = t >= gone_t
        cap[0].location = tractor_now + Vector((1.2, -1.4, 0.08)) + Vector((0, -s_now, 0))
        cap[0].keyframe_insert("location", frame=f)
        show(cap, f, cap_vis)
        # ---------------- Rahim: in the aisle with the radio, then at the front
        if at("rahim1") - 1.0 <= t < at("rahim1", 1) + 1.0 or at("rahim2") - 0.8 <= t < at("rahim3", 1) + 0.8 \
                or at("rahim4") - 0.8 <= t < at("rahim4", 1) + 0.8:
            u = seg(t, at("rahim1") - 1.0, at("rahim1") - 0.3)
            rahim.pose(f, t, Vector((0.1, -1.7, 0)), facing=0, reach2=(105, 10), look=(0, 8), worry=1.7,
                       reach=(130, 20) if (at("rahim2") < t < at("rahim2", 1) or at("rahim4") < t < at("rahim4", 1)) else None)
        else:
            rahim.pose(f, t, Vector((0.1, -30, 0)), facing=0)
        led.scale = (1,) * 3
        led.keyframe_insert("scale", frame=f)
        for i, (e, p0) in enumerate(zip(passengers, (Vector((-0.62, -3.75, 0)), Vector((0.62, -3.75, 0)),
                                                       Vector((1.12, 3.75, 0))))):
            e.pose(f, t, p0, facing=0, sit=1, seat_h=0.5, lean=0, look=(15 * math.sin(i + t * 0.2), -5), worry=1.6)

        # ---------------- the walkers outside: drifting slowly; after the stop the near ones come for us
        train_out = Vector((-2.4, s_now + 1.0, GROUND))       # our car, in outside coordinates
        jalal_out = tractor_now + Vector((0, 0, 0))
        dt = 1.0 / FPS
        for i, (w, (home, ph, sp, near)) in enumerate(zip(walkers, w_home)):
            if wpos[i] is None:
                wpos[i] = home.copy()
            if t >= chase0 and (near or abs(wpos[i].y - s_now) < 40):
                target, spd = train_out + Vector((-0.4 * (i % 3), -3.0 - i * 0.7, 0)), 4.2 + 0.2 * (i % 4)
            elif near and t >= t_out0 + 1.0:
                ang = i * 0.8
                target, spd = jalal_out + Vector((math.cos(ang) * 1.1, math.sin(ang) * 1.1, 0)), 1.6
            elif near and t >= approach0:
                target, spd = Vector((-2.6, wpos[i].y, GROUND)), 0.8
            else:
                target = home + Vector((math.sin(ph + t * 0.05) * 3, math.cos(ph * 1.3 + t * 0.04) * 3, 0))
                spd = 0.4
            d = target - wpos[i]
            step = min(d.length, spd * dt)
            if d.length > 1e-4:
                wpos[i] = wpos[i] + d.normalized() * step
            moving = d.length > 0.15
            world_p = wpos[i] + Vector((0, -s_now, 0))
            chasing = t >= chase0 or (near and t >= approach0)
            turn_head = seg(t, at("lena2") - 0.5, at("lena2") + 0.3) if near and i == 0 else 0.0
            w.pose(f, t, world_p, facing=(yaw_to(d) if moving else yaw_to(jalal_out - wpos[i])) + 8 * math.sin(t * 1.7 + i),
                   run=(0.35 if spd < 1 else 0.9) if moving else 0.0, run_rate=0.7 + 0.12 * spd, lean=-14,
                   reach=(90, 8) if chasing else (10, 0), reach2=(85, -8) if chasing else None,
                   look=(lerp(0, 70, turn_head), -8 + 10 * turn_head), worry=0.0, talk=False)
        # the crowd from the side streets joins the chase
        for i, r in enumerate(runners):
            if t >= at("lena4") - 0.5:
                target = train_out + Vector((-1.0 - (i % 4) * 0.8, -2.0 - i * 1.1, 0))
                d = target - runner_pos[i]
                if d.length > 1e-4:
                    runner_pos[i] = runner_pos[i] + d.normalized() * min(d.length, (4.6 + 0.2 * (i % 5)) * dt)
            rp = runner_pos[i] + Vector((0, -s_now, 0.06 * abs(math.sin(t * 9 + i))))
            r.location = rp
            r.rotation_euler = (D(-12), 0, D(yaw_to(train_out - runner_pos[i])))
            r.keyframe_insert("location", frame=f)
            r.keyframe_insert("rotation_euler", frame=f)

        # ---------------- our hands on the table, or on the window when we lean
        arms.set(f, "L", (-0.3, -0.42, -0.46) if lean < 0.3 else (-0.35, -0.3, -0.5))
        arms.set(f, "R", (0.28, -0.42, -0.46))

    bpy.ops.object.light_add(type="SUN", rotation=(D(60), D(10), D(70)))
    sun = bpy.context.object
    sun.data.energy = 1.2
    sun.data.color = (0.85, 0.86, 0.92)
    bpy.ops.object.light_add(type="POINT", location=(-0.3, -0.4, 1.5))
    lt = no_cam(bpy.context.object)
    lt.data.energy = 25
    setup_render(scene, sky=(0.66, 0.66, 0.68), sky_strength=1.0)
    ls = scene.view_layers[0].freestyle_settings.linesets[0]
    ls.select_by_collection = True
    ls.collection = fog_col
    ls.collection_negation = "EXCLUSIVE"
    fade = ls.linestyle.alpha_modifiers.new("Fog fade", "DISTANCE_FROM_CAMERA")
    fade.range_min, fade.range_max = 6.0, 30.0
    fade.invert = True
    scene.frame_set(1)
    return scene


if __name__ == "__main__":
    run_cli(build(), "train_city5.blend")
