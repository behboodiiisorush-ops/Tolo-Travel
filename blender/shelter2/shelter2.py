"""
«پناهگاه ۲ — چراغ سبز» — three days later.  Inside the bunker by the steel door with its status light
(red: outside is not safe, green: the door may open), and outside: the park, grey and dead.

    dark, red light, three knocks  →  waiting  →  beep, green  →  the door grinds open  →  grey silence
    →  Lena runs for her bunny  →  a growl: Jalal, a zombie now  →  the guard and we push the door shut
    →  bangs on the steel, the light back to red

All beats follow times.py (the recorded voices).  Rendered on twos; post.py doubles the frames.

    python shelter2.py --still 49,361
    python shelter2.py --render --range 1 1900
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

random.seed(8)
T = KEY_OF
EYE = 1.55
SX = 100.0
DOOR_Y = 97.0
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




def ruin_the_world():
    """Three days after the bomb: no lights, burnt trees, grey grass, sooty cars, dust."""
    recolor = {"Tree a": (0.22, 0.2, 0.18), "Tree b": (0.3, 0.27, 0.24), "Park grass": (0.42, 0.4, 0.36),
               "Ground": (0.45, 0.42, 0.38), "Trunk": (0.12, 0.1, 0.09)}
    for m in bpy.data.materials:
        for name, col in recolor.items():
            if m.name.startswith(name) and m.use_nodes:
                for n in m.node_tree.nodes:
                    if n.type in ("BSDF_TOON", "EMISSION"):
                        n.inputs["Color"].default_value = (*col, 1)
        if m.name.startswith("Car ") and m.use_nodes:
            for n in m.node_tree.nodes:
                if n.type in ("BSDF_TOON", "EMISSION"):
                    c = n.inputs["Color"].default_value
                    n.inputs["Color"].default_value = (c[0] * 0.35, c[1] * 0.35, c[2] * 0.35, 1)
        if m.name.startswith(("Lit window", "Street lamp")) and m.use_nodes:
            for n in m.node_tree.nodes:
                if n.type == "EMISSION":
                    n.inputs["Color"].default_value = (0.08, 0.08, 0.09, 1)
                    n.inputs["Strength"].default_value = 0.2
    for m in bpy.data.materials:  # the whole city washed grey by the ash
        if m.name.startswith(("Building", "Asphalt", "Sidewalk", "Road line", "Pole", "Dark window", "Car ",
                              "Car glass", "Tyre")) and m.use_nodes:
            for n in m.node_tree.nodes:
                if n.type in ("BSDF_TOON", "EMISSION"):
                    c = n.inputs["Color"].default_value
                    g = 0.3 * c[0] + 0.55 * c[1] + 0.15 * c[2]
                    g = 0.25 + 0.5 * g
                    n.inputs["Color"].default_value = (g, g, g * 1.02, 1)
    for o in list(bpy.data.objects):
        if o.type == "LIGHT" and o.data.type == "POINT" and abs(o.location.x - SX) < 1 and o.location.z > 5:
            bpy.data.objects.remove(o)        # the street lamps are dead
    # ash heaps and fallen branches in the park
    ash = toon("Ash", (0.35, 0.33, 0.31), 0.1)
    for k in range(25):
        x, y = SX + random.uniform(-10, 14), random.uniform(78, 96)
        b = ball((x, y, 0.0), random.uniform(0.3, 0.9), ash, "Ash heap", scale=(1.6, 1.2, 0.35))
    stick = toon("Branch", (0.15, 0.12, 0.1), 0.05)
    for k in range(14):
        x, y = SX + random.uniform(-8, 12), random.uniform(80, 96)
        rod((x, y, 0.05), (x + random.uniform(-1.5, 1.5), y + random.uniform(-1.5, 1.5), 0.08), 0.05, stick, "Branch")


def build_dust():
    """Grey dust hanging in the air outside the door, drifting slowly."""
    m = toon("Dust", (0.7, 0.67, 0.62), 0.3)
    motes = []
    rnd = random.Random(5)
    for k in range(70):
        p = Vector((BX + rnd.uniform(-7, 7), DOOR_Y - rnd.uniform(1.5, 22), rnd.uniform(0.3, 4.0)))
        o = ball(tuple(p), rnd.uniform(0.02, 0.06), m, "Dust mote", seg=6)
        motes.append((o, p, Vector((rnd.uniform(-0.2, 0.2), rnd.uniform(-0.1, 0.1), rnd.uniform(-0.05, 0.05)))))
    haze = []
    hm = bpy.data.materials.new("Haze")
    hm.use_nodes = True
    nt = hm.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    mix = nt.nodes.new("ShaderNodeMixShader")
    mix.inputs[0].default_value = 0.25
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = (0.72, 0.68, 0.62, 1)
    em.inputs["Strength"].default_value = 1.0
    nt.links.new(tr.outputs[0], mix.inputs[1])
    nt.links.new(em.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs["Surface"])
    for k, d in enumerate(()):  # (veils dropped: their outlines read as glass)
        bpy.ops.mesh.primitive_plane_add(size=1, location=(BX, DOOR_Y - d, 2.5), rotation=(D(90), 0, 0))
        v = bpy.context.object
        v.scale = (40, 6, 1)
        v.name = "Dust veil"
        v.data.materials.append(hm)
        v.visible_shadow = False
        haze.append(v)
    return motes


def build_fog():
    """Grey fog outside: many faint veils one behind another, so far things fade away.
    The veils sit in their own collection, which the Freestyle outlines ignore."""
    fog_col = bpy.data.collections.new("Fog")
    bpy.context.scene.collection.children.link(fog_col)
    m = bpy.data.materials.new("Fog veil")
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    mix = nt.nodes.new("ShaderNodeMixShader")
    mix.inputs[0].default_value = 0.14
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = (0.72, 0.72, 0.73, 1)
    em.inputs["Strength"].default_value = 1.0
    nt.links.new(tr.outputs[0], mix.inputs[1])
    nt.links.new(em.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs["Surface"])
    for k in range(18):
        y = DOOR_Y - 2.2 - k * 2.6
        bpy.ops.mesh.primitive_plane_add(size=1, location=(BX, y, 6), rotation=(D(90), 0, 0))
        v = bpy.context.object
        v.scale = (120, 12, 1)
        v.name = "Fog veil"
        v.data.materials.append(m)
        v.visible_shadow = False
        v.visible_diffuse = False
        for c in list(v.users_collection):
            c.objects.unlink(v)
        fog_col.objects.link(v)
    return fog_col


def build_status_lights():
    """The lamp above the door (inside and outside): red, or green when it is safe to open."""
    red = glow_mat("Status red", (1.0, 0.08, 0.05), 6.0)
    green = glow_mat("Status green", (0.1, 1.0, 0.25), 6.0)
    housing = toon("Lamp housing", (0.15, 0.15, 0.16), 0.05)
    reds, greens = [], []
    for side in (1, -1):  # inside, outside
        y = DOOR_Y + side * 0.24
        box((BX, y, 2.42), (0.5, 0.1, 0.22), housing, "Status housing", bevel=0.02)
        reds.append(ball((BX - 0.11, y + side * 0.05, 2.42), 0.07, red, "Status red", scale=(1, 0.5, 1)))
        greens.append(ball((BX + 0.11, y + side * 0.05, 2.42), 0.07, green, "Status green", scale=(1, 0.5, 1)))
    bpy.ops.object.light_add(type="POINT", location=(BX, DOOR_Y + 0.6, 2.2))
    glow = no_cam(bpy.context.object)
    glow.data.energy = 18
    return reds, greens, glow


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

    build_street()
    hinge, gaps, flash_m, lamp, bulb, burst, led = build_bunker()
    ruin_the_world()
    motes = build_dust()
    reds, greens, status = build_status_lights()
    fog_col = build_fog()
    lena, mom, guard, zombie = make_lena(), make_mom(), make_guard(), make_zombie_jalal()
    sitters = [make_extra(i + 1, 0.95) for i in range(5)]
    cam = make_camera(scene)
    arms = POVArms(cam)
    arms.reach = 1.2

    rnd = random.Random(3)
    shake = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(-1, 1)) for _ in range(int(END * FPS) + 3)]

    green0 = at("mom1") - 1.4                     # beep: the light turns green
    open0, open1 = at("guard2", 1) - 0.2, at("n3") + 1.4
    to_door0, to_door1 = at("n3") - 0.6, at("n3") + 1.6
    growl0 = at("me2") - 2.0
    lunge0 = at("guard3") - 0.5
    close0, close1 = at("guard3") + 0.4, at("lena3") - 1.4
    red_again = close1 + 0.6
    seat = Vector((BX + 0.4, DOOR_Y + 3.2, 1.1))
    stand = Vector((BX - 0.05, DOOR_Y + 2.1, EYE))
    doorway = Vector((BX - 0.05, DOOR_Y + 0.55, EYE))
    push = Vector((BX + 0.15, DOOR_Y + 1.05, EYE))
    zpath = [Vector((BX - 3.5, DOOR_Y - 18, 0)), Vector((BX - 0.6, DOOR_Y - 3.0, 0)), Vector((BX - 0.1, DOOR_Y - 0.3, 0))]

    for f in range(1, int(END * FPS) + 1):
        t = (f - 1) / FPS
        green = green0 <= t < red_again
        for o in reds:
            show([o], f, not green)
        for o in greens:
            show([o], f, green)
        status.data.color = (0.1, 1.0, 0.3) if green else (1.0, 0.1, 0.05)
        status.data.keyframe_insert("color", frame=f)
        lamp.data.energy = 35
        lamp.data.keyframe_insert("energy", frame=f)
        led.scale = (0.001,) * 3
        led.keyframe_insert("scale", frame=f)

        # ---------------- the door: grinds open on green, pushed shut against the zombie
        op = seg(t, open0, open1) * (1 - seg(t, close0, close1))
        jam = 0.03 * math.sin(t * 30) * (close0 + 0.4 < t < close1 - 0.2)
        hinge.rotation_euler = (0, 0, D(-95) * op + jam)
        hinge.keyframe_insert("rotation_euler", frame=f)

        # ---------------- dust drifting
        for o, p0, v in motes:
            o.location = p0 + v * t
            o.keyframe_insert("location", frame=f)

        # ---------------- camera
        if t < at("mom1") - 0.3:
            pos = seat.copy()
        elif t < to_door0:
            pos = seat.lerp(stand, seg(t, at("mom1") - 0.3, at("mom1") + 0.6))
        elif t < lunge0:
            pos = stand.lerp(doorway, seg(t, to_door0, to_door1))
        else:
            pos = doorway.lerp(push, seg(t, lunge0, close0 + 0.2))
            pos = pos.lerp(stand, seg(t, close1 + 1.0, close1 + 2.5))
        d_door = Vector((BX, DOOR_Y, 1.9)) - pos
        yaw, pitch = yaw_to(d_door), pitch_to(d_door)                            # the door and its red light
        k = seg(t, at("n2") - 0.2, at("n2") + 0.8) * (1 - seg(t, at("n2", 1) - 0.6, at("n2", 1)))
        yaw = lerp_yaw(yaw, 260, k); pitch = lerp(pitch, -12, k)                 # the people on the benches
        lena_now = None
        ylf, plf = look(pos, Vector((BX + 1.45, DOOR_Y + 3.0, 0.95)))
        k = seg(t, at("lena1") - 0.4, at("lena1")) * (1 - seg(t, at("guard1") - 0.3, at("guard1")))
        yaw = lerp_yaw(yaw, ylf, k); pitch = lerp(pitch, plf, k)
        ym, pm = look(pos, Vector((BX - 1.4, DOOR_Y + 3.4, 1.5)))
        k = seg(t, at("mom1") - 0.3, at("mom1")) * (1 - seg(t, at("mom1", 1), at("mom1", 1) + 0.4))
        yaw = lerp_yaw(yaw, ym, k); pitch = lerp(pitch, pm, k)
        if t >= to_door0 and t < lunge0:
            yo, po = look(pos, Vector((BX - 0.8, DOOR_Y - 12, 1.4)))            # out over the grey park
            yaw = lerp_yaw(yaw, yo, seg(t, to_door0, to_door1)); pitch = lerp(pitch, po, seg(t, to_door0, to_door1))
            yl, pl = look(pos, Vector((BX + 0.2, DOOR_Y - 1.0, 0.9)))
            k = seg(t, at("lena2") - 0.2, at("lena2") + 0.3) * (1 - seg(t, at("me1", 1), at("me1", 1) + 0.4))
            yaw = lerp_yaw(yaw, yl, k); pitch = lerp(pitch, pl, k)
        if growl0 <= t < close1:
            zu = seg(t, growl0, lunge0)
            zp = zpath[0].lerp(zpath[1], zu)
            yz, pz = look(pos, zp + Vector((0, 0, 1.5)))
            k = seg(t, growl0, growl0 + 0.6)
            yaw = lerp_yaw(yaw, yz, k); pitch = lerp(pitch, pz, k)
        if t >= close1:
            ylf2, plf2 = look(pos, Vector((BX + 0.8, DOOR_Y + 2.3, 1.0)))       # Lena in mum's arms
            k = seg(t, at("lena3") - 0.4, at("lena3")) * (1 - seg(t, at("guard4") - 0.3, at("guard4")))
            yaw = lerp_yaw(yaw, ylf2, k); pitch = lerp(pitch, plf2, k)
            yg, pg = look(pos, Vector((BX - 1.0, DOOR_Y + 1.4, 1.7)))
            k = seg(t, at("guard4") - 0.3, at("guard4")) * (1 - seg(t, at("mom2") - 0.3, at("mom2")))
            yaw = lerp_yaw(yaw, yg, k); pitch = lerp(pitch, pg, k)
            k = seg(t, at("mom2") - 0.3, at("mom2")) * (1 - seg(t, at("n4") - 0.2, at("n4") + 0.4))
            yaw = lerp_yaw(yaw, ylf2, k); pitch = lerp(pitch, plf2 + 6, k)
            yr, pr = look(pos, Vector((BX, DOOR_Y + 0.25, 2.42)))              # the red light again
            k = seg(t, at("n4") + 0.4, at("n4") + 1.6)
            yaw = lerp_yaw(yaw, yr, k); pitch = lerp(pitch, pr, k)
        amp = 0.05
        if lunge0 <= t < close1 + 0.5:
            amp = 0.5
        for tb in (close1, close1 + 0.9, close1 + 1.6, close1 + 2.6):           # bangs on the door
            if tb <= t < tb + 0.4:
                amp += 1.6 * (1 - (t - tb) / 0.4)
        sx_, sy_, sz_ = shake[f]
        cam.location = pos
        cam.rotation_euler = (D(90 + pitch + sx_ * amp), D(sy_ * amp * 0.6), D(yaw + sz_ * amp))
        cam.keyframe_insert("location", frame=f)
        cam.keyframe_insert("rotation_euler", frame=f)

        # ---------------- Lena: on the bench, runs out for her bunny, pulled back, in mum's arms
        if t < at("lena2") - 0.2:
            lena.pose(f, t, Vector((BX + 1.45, DOOR_Y + 3.0, 0)), facing=95, sit=1, seat_h=0.5, lean=0,
                      look=(0, 10), worry=1.8, hug=0.3)
        elif t < close0:
            out = seg(t, at("lena2") - 0.3, at("lena2") + 1.1)
            back = seg(t, lunge0, close0)
            lp = Vector((BX + 1.0, DOOR_Y + 1.6, 0)).lerp(Vector((BX + 0.25, DOOR_Y - 0.9, 0)), out)
            lp = lp.lerp(Vector((BX + 0.7, DOOR_Y + 1.9, 0)), back)
            lena.pose(f, t, lp, facing=180 if back < 0.5 else 0, run=1.0 if (out < 0.98 or 0.02 < back < 0.98) else 0,
                      run_rate=2.2, lean=-6, look=(lerp(0, 35, seg(t, at("me1"), at("me1") + 0.3)), 5),
                      reach=(140, 20) if at("lena2") < t < at("lena2", 1) else None, worry=1.6 + 0.4 * back)
        else:
            lena.pose(f, t, Vector((BX + 0.75, DOOR_Y + 2.2, 0)), facing=30, crouch=0.3, hug=0.6, look=(0, 25),
                      worry=2.0, lean=0)

        # ---------------- Mum: on the bench, up at green, holding Lena at the end
        up = seg(t, at("mom1") - 0.6, at("mom1"))
        mpos = Vector((BX - 1.45, DOOR_Y + 3.4, 0)).lerp(Vector((BX - 0.6, DOOR_Y + 3.0, 0)), up)
        mpos = mpos.lerp(Vector((BX + 1.0, DOOR_Y + 2.7, 0)), seg(t, close1, close1 + 1.2))
        mom.pose(f, t, mpos, facing=lerp_yaw(-90, 200, up) if t < close1 else 200, sit=1 - up, seat_h=0.5, lean=0,
                 reach=(lerp(30, 150, seg(t, at("mom1"), at("mom1") + 0.3) * (1 - seg(t, at("mom1", 1), at("mom1", 1) + 0.4))), 20),
                 hug=0.6 * seg(t, close1, close1 + 1.2), look=(0, 10), worry=1.5 + 0.5 * seg(t, lunge0, close1))

        # ---------------- the guard: by the door, opens it, pushes it shut with us
        gpush = seg(t, lunge0, close0)
        gp = Vector((BX - 1.0, DOOR_Y + 1.0, 0)).lerp(Vector((BX + 0.75, DOOR_Y + 1.15, 0)), gpush)
        gp = gp.lerp(Vector((BX - 1.2, DOOR_Y + 1.5, 0)), seg(t, close1 + 0.6, close1 + 1.6))
        turn_wheel = seg(t, at("guard2") - 0.4, open0) * (1 - seg(t, open0, open0 + 0.3))
        guard.pose(f, t, gp, facing=180 if gpush < 0.5 or t > close1 + 1.0 else 150,
                   reach=(lerp(lerp(30, 95, turn_wheel), 100, gpush), 10), reach2=(lerp(20, 100, gpush), -10),
                   lean=-15 * gpush * (t < close1), look=(0, 0), worry=1.2 + 0.8 * gpush)

        # ---------------- Jalal: a figure in the dust, limping closer, then the lunge
        if t < growl0:
            zp = Vector((BX - 3.5, DOOR_Y - 40, 0))
            zrun = 0.0
        elif t < lunge0:
            zp = zpath[0].lerp(zpath[1], seg(t, growl0, lunge0))
            zrun = 0.45
        else:
            zp = zpath[1].lerp(zpath[2], seg(t, lunge0, close0 + 0.3))
            zrun = 1.0 if t < close0 + 0.3 else 0.0
        if t > close1 + 0.2:
            zp = Vector((BX - 0.1, DOOR_Y - 0.6, 0))
        lurch = 8 * math.sin(t * 2.3)
        zombie.pose(f, t, zp, facing=yaw_to(Vector((BX, DOOR_Y, 0)) - zp) + lurch, run=zrun, run_rate=1.1 + zrun,
                    lean=-14, reach=(95 + 10 * math.sin(t * 3), 8), reach2=(90 + 10 * math.cos(t * 3), -8),
                    look=(lurch, -10 + 6 * math.sin(t * 1.7)), worry=0.0, talk=False)

        for i, s in enumerate(sitters):
            sxp = BX + (-1.5 if i % 2 else 1.5)
            stand_up = seg(t, at("mom1"), at("mom1") + 0.8) * (1 - seg(t, close1, close1 + 1.0))
            s.pose(f, t, Vector((sxp, DOOR_Y + 4.5 + i * 1.3, 0)), facing=90 if i % 2 == 0 else -90,
                   sit=1 - stand_up, seat_h=0.5, lean=0, look=(0, -15 + 15 * stand_up), worry=1.8,
                   hug=0.4 * seg(t, close1, close1 + 1.0))

        # ---------------- our hands: on our knees, the door, Lena's shoulder
        bpy.context.view_layer.update()
        if at("me1") - 0.2 <= t < lunge0:
            target = world_to_cam(cam, lena.p["shoulderR"].matrix_world.translation)
            arms.set(f, "R", target if target.z < -0.1 else Vector((0.28, -0.42, -0.46)))
            arms.set(f, "L", (-0.3, -0.42, -0.46))
        elif close0 - 0.3 <= t < close1 + 0.4:
            dp = hinge.matrix_world @ Vector((-0.5, 0.12, 1.3))
            dq = hinge.matrix_world @ Vector((-1.0, 0.12, 1.0))
            arms.set(f, "R", world_to_cam(cam, dp))
            arms.set(f, "L", world_to_cam(cam, dq))
        else:
            arms.set(f, "R", (0.28, -0.42, -0.46))
            arms.set(f, "L", (-0.3, -0.42, -0.46))

    bpy.ops.object.light_add(type="SUN", rotation=(D(55), D(15), D(-30)))
    sun = bpy.context.object
    sun.data.energy = 1.0
    sun.data.color = (0.85, 0.86, 0.9)
    darken_toon(0.6)
    setup_render(scene, sky=(0.66, 0.66, 0.67), sky_strength=1.0)
    ls = scene.view_layers[0].freestyle_settings.linesets[0]
    ls.select_by_collection = True
    ls.collection = fog_col
    ls.collection_negation = "EXCLUSIVE"
    fade = ls.linestyle.alpha_modifiers.new("Fog fade", "DISTANCE_FROM_CAMERA")  # outlines vanish in the fog
    fade.range_min, fade.range_max = 5.0, 24.0
    fade.invert = True
    scene.frame_set(1)
    return scene


if __name__ == "__main__":
    run_cli(build(), "shelter2.blend")
