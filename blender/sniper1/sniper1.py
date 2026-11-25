"""
«تک‌تیرانداز ۱ — نقطهٔ قرمز» — dusk.  A city of very tall towers around a square with a fountain.
We lie on the roof of the tallest tower; through the scope we watch the crowd, find the man in the
red jacket, and never fire.

Two camera modes: the POV on the roof (12 mm, hands on the rifle) and the scope (very long lens,
the round mask and crosshair are drawn by post.py; SCOPE in captions is read from here).

    python sniper1.py --still 49,361
    python sniper1.py --render --range 1 1300
"""

import math
import os
import random
import sys

import bpy
from mathutils import Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403,E402
from captions import END, KEY_OF, scope_windows  # noqa: E402

random.seed(11)
T = KEY_OF
ROOF_Z = 232.0
NEST = Vector((74.0, -150.0, ROOF_Z))      # where we lie on the roof
FOUNTAIN = Vector((0.0, 0.0, 0.0))
MAN = Vector((3.2, -2.6, 0.0))


def at(key, k=0):
    return T[key][k]


def yaw_to(d):
    return math.degrees(math.atan2(-d.x, d.y)) % 360


def pitch_to(d):
    return math.degrees(math.atan2(d.z, d.xy.length))


def lerp_yaw(a, b, u):
    d = (b - a + 180) % 360 - 180
    return a + d * u


# ================================================================ city


def tower_mat(name, wall, glass, lit_ratio=0.35):
    """Toon façade with a grid of windows (procedural, so very tall towers stay cheap)."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    comb = nt.nodes.new("ShaderNodeCombineXYZ")
    add = nt.nodes.new("ShaderNodeMath")
    add.operation = "ADD"
    nt.links.new(tc.outputs["Object"], sep.inputs[0])
    nt.links.new(sep.outputs[0], add.inputs[0])
    nt.links.new(sep.outputs[1], add.inputs[1])
    nt.links.new(add.outputs[0], comb.inputs[0])
    nt.links.new(sep.outputs[2], comb.inputs[1])
    brick = nt.nodes.new("ShaderNodeTexBrick")
    brick.offset = 0.0
    brick.inputs["Scale"].default_value = 1.0
    brick.inputs["Brick Width"].default_value = 2.2
    brick.inputs["Row Height"].default_value = 3.4
    brick.inputs["Mortar Size"].default_value = 0.45
    brick.inputs["Bias"].default_value = 1.0 - 2 * lit_ratio
    brick.inputs["Color1"].default_value = (1.0, 0.8, 0.45, 1)       # lit window
    brick.inputs["Color2"].default_value = (*glass, 1)              # dark glass
    brick.inputs["Mortar"].default_value = (*wall, 1)
    nt.links.new(comb.outputs[0], brick.inputs["Vector"])
    toon_n = nt.nodes.new("ShaderNodeBsdfToon")
    toon_n.inputs["Size"].default_value = 0.6
    toon_n.inputs["Smooth"].default_value = 0.04
    nt.links.new(brick.outputs["Color"], toon_n.inputs["Color"])
    em = nt.nodes.new("ShaderNodeEmission")
    nt.links.new(brick.outputs["Color"], em.inputs["Color"])
    inv = nt.nodes.new("ShaderNodeMath")
    inv.operation = "SUBTRACT"
    inv.inputs[0].default_value = 1.0
    nt.links.new(brick.outputs["Fac"], inv.inputs[1])
    mul = nt.nodes.new("ShaderNodeMath")
    mul.operation = "MULTIPLY_ADD"
    mul.inputs[1].default_value = 0.9
    mul.inputs[2].default_value = 0.18
    nt.links.new(inv.outputs[0], mul.inputs[0])
    nt.links.new(mul.outputs[0], em.inputs["Strength"])
    addsh = nt.nodes.new("ShaderNodeAddShader")
    nt.links.new(toon_n.outputs[0], addsh.inputs[0])
    nt.links.new(em.outputs[0], addsh.inputs[1])
    nt.links.new(addsh.outputs[0], out.inputs["Surface"])
    return m


def build_city():
    palettes = [((0.62, 0.66, 0.72), (0.18, 0.28, 0.4)), ((0.85, 0.78, 0.62), (0.2, 0.25, 0.3)),
                ((0.55, 0.6, 0.6), (0.12, 0.3, 0.35)), ((0.9, 0.9, 0.88), (0.25, 0.35, 0.5)),
                ((0.35, 0.38, 0.42), (0.15, 0.2, 0.28)), ((0.75, 0.5, 0.4), (0.2, 0.22, 0.28))]
    mats = [tower_mat(f"Tower {k}", w, g, 0.25 + 0.05 * k) for k, (w, g) in enumerate(palettes)]
    roof = toon("Roof", (0.4, 0.4, 0.42), 0.1)
    asphalt = toon("Asphalt", (0.25, 0.25, 0.28), 0.1)
    side = toon("Sidewalk", (0.62, 0.6, 0.56), 0.15)
    box((0, 0, -0.05), (900, 900, 0.1), asphalt, "Streets")
    block, street = 46.0, 16.0
    for bx in range(-6, 7):
        for by in range(-6, 7):
            cx, cy = bx * (block + street), by * (block + street)
            box((cx, cy, 0.08), (block + 2, block + 2, 0.16), side, "Block pavement")
            if bx == 0 and by == 0:
                continue  # the square
            d = math.hypot(cx, cy)
            n = random.choice((1, 2, 2, 4))
            for k in range(n):
                if n == 1:
                    ox = oy = 0.0
                    w = random.uniform(26, 38)
                elif n == 2:
                    ox, oy = ((-11, 0), (11, 0))[k] if random.random() < 0.5 else ((0, -11), (0, 11))[k]
                    w = random.uniform(16, 20)
                else:
                    ox, oy = ((-11, -11), (11, -11), (-11, 11), (11, 11))[k]
                    w = random.uniform(14, 18)
                h = random.uniform(55, 130) + max(0.0, 320 - d * 0.55) * random.uniform(0.45, 1.0)
                tx, ty = cx + ox, cy + oy
                if (tx - NEST.x) ** 2 + (ty - NEST.y) ** 2 < 30 ** 2:
                    continue  # our tower is built separately
                # keep the line of sight from our roof down to the square clear
                sx_, sy_ = NEST.x, NEST.y
                u = max(0.0, min(1.0, ((tx - sx_) * (0 - sx_) + (ty - sy_) * (0 - sy_)) / (sx_ ** 2 + sy_ ** 2)))
                if math.hypot(tx - (sx_ + u * (0 - sx_)), ty - (sy_ + u * (0 - sy_))) < w * 0.75 + 12 and u > 0.08:
                    continue
                box((tx, ty, h / 2), (w, w * random.uniform(0.8, 1.2), h), random.choice(mats), "Tower")
                box((tx, ty, h + 0.4), (w * 0.9, w * 0.9, 0.8), roof, "Tower roof")
                if random.random() < 0.4:
                    rod((tx, ty, h + 0.8), (tx, ty, h + random.uniform(8, 20)), 0.3, roof, "Antenna")
                    ball((tx, ty, h + 21), 0.6, glow_mat("Beacon", (1.0, 0.1, 0.05), 5.0), "Beacon")
    # our tower (the tallest) and its roof
    box((NEST.x, NEST.y - 4, ROOF_Z / 2), (34, 34, ROOF_Z), mats[4], "Our tower")
    rf = toon("Roof floor", (0.48, 0.47, 0.45), 0.15)
    box((NEST.x, NEST.y - 4, ROOF_Z + 0.05), (34, 34, 0.1), rf, "Roof floor")
    par = toon("Parapet", (0.6, 0.58, 0.55), 0.15)
    box((NEST.x, NEST.y + 12.6, ROOF_Z + 0.55), (34, 0.5, 1.1), par, "Parapet", bevel=0.05)
    for x in (NEST.x - 17, NEST.x + 17):
        box((x, NEST.y - 4, ROOF_Z + 0.55), (0.5, 34, 1.1), par, "Parapet side", bevel=0.05)
    ac = toon("AC unit", (0.75, 0.76, 0.78), 0.15)
    for k, (dx, dy) in enumerate(((-9, -6), (-5, -14), (8, -10))):
        box((NEST.x + dx, NEST.y + dy, ROOF_Z + 0.9), (3, 2.2, 1.8), ac, "AC unit", bevel=0.08)
    rod((NEST.x + 12, NEST.y - 12, ROOF_Z), (NEST.x + 12, NEST.y - 12, ROOF_Z + 14), 0.25, ac, "Mast")
    # the square: paving, fountain, trees, benches, a balloon seller, lamps
    pave = toon("Square paving", (0.82, 0.74, 0.62), 0.18)
    bpy.ops.mesh.primitive_cylinder_add(radius=24, depth=0.2, location=(0, 0, 0.1), vertices=48)
    finish(bpy.context.object, pave, "Square", True)
    stone = toon("Fountain stone", (0.85, 0.82, 0.76), 0.2)
    water = glow_mat("Water", (0.45, 0.75, 0.95), 1.2)
    bpy.ops.mesh.primitive_cylinder_add(radius=4.2, depth=0.7, location=(0, 0, 0.45), vertices=40)
    finish(bpy.context.object, stone, "Basin", True)
    bpy.ops.mesh.primitive_cylinder_add(radius=3.8, depth=0.1, location=(0, 0, 0.78), vertices=40)
    finish(bpy.context.object, water, "Pool", True)
    rod((0, 0, 0.8), (0, 0, 2.6), 0.35, stone, "Fountain column")
    ball((0, 0, 2.8), 1.0, stone, "Fountain bowl", scale=(1, 1, 0.35))
    for k in range(12):
        a = k * math.pi / 6
        rod((0.3 * math.cos(a), 0.3 * math.sin(a), 2.9), (1.6 * math.cos(a), 1.6 * math.sin(a), 1.0), 0.05, water,
            "Water jet")
    trunk = toon("Trunk", (0.35, 0.25, 0.17), 0.12)
    leaf = [toon("Tree a", (0.3, 0.55, 0.28), 0.15), toon("Tree b", (0.45, 0.62, 0.25), 0.15)]
    for k in range(14):
        a = k * 2 * math.pi / 14
        x, y = 19 * math.cos(a), 19 * math.sin(a)
        rod((x, y, 0.2), (x, y, 3.0), 0.22, trunk, "Trunk")
        ball((x, y, 4.4), 2.0, random.choice(leaf), "Crown")
    bench = toon("Bench", (0.5, 0.32, 0.2), 0.12)
    for k in range(8):
        a = (k + 0.5) * math.pi / 4
        b = box((10 * math.cos(a), 10 * math.sin(a), 0.45), (2.2, 0.6, 0.12), bench, "Bench", bevel=0.03)
        b.rotation_euler = (0, 0, a + math.pi / 2)
    cols = [(0.95, 0.2, 0.25), (0.2, 0.5, 0.95), (1.0, 0.8, 0.1), (0.3, 0.8, 0.35), (0.85, 0.35, 0.85)]
    sx, sy = -8.5, 6.0  # the balloon seller's bunch
    for k in range(9):
        c = cols[k % 5]
        bx_, by_, bz = sx + random.uniform(-0.6, 0.6), sy + random.uniform(-0.6, 0.6), 3.0 + random.uniform(0, 1.2)
        ball((bx_, by_, bz), 0.32, toon(f"Balloon {c}", c, 0.35), "Balloon", scale=(1, 1, 1.15))
        rod((sx, sy, 1.3), (bx_, by_, bz - 0.35), 0.008, toon("String", (0.95, 0.95, 0.95)), "String", verts=6)
    lamp = glow_mat("Square lamp", (1.0, 0.85, 0.55), 6.0)
    for k in range(6):
        a = k * math.pi / 3 + 0.3
        x, y = 15 * math.cos(a), 15 * math.sin(a)
        rod((x, y, 0.2), (x, y, 4.2), 0.08, toon("Lamp pole", (0.15, 0.15, 0.17)), "Lamp pole")
        ball((x, y, 4.3), 0.3, lamp, "Lamp")
    # cars waiting at the lights around the square
    car_c = [(0.8, 0.15, 0.15), (0.2, 0.35, 0.75), (0.95, 0.95, 0.92), (0.15, 0.15, 0.17), (0.95, 0.7, 0.1)]
    cars = []
    for k in range(16):
        lane = random.choice((-1, 1))
        horiz = k % 2 == 0
        m = toon(f"Car {k}", car_c[k % 5], 0.2)
        root = empty(f"Car{k}")
        parts = [box((0, 0, 0.6), (1.9, 4.3, 0.7), m, "Car body", bevel=0.15),
                 box((0, -0.2, 1.15), (1.7, 2.2, 0.55), toon("Car glass", (0.15, 0.2, 0.3), 0.05), "Car cabin",
                     bevel=0.12)]
        for p in parts:
            parent_keep(p, root)
        cars.append((root, horiz, lane, random.uniform(0, 400), random.uniform(6, 11)))
    return cars


def make_man():
    p = Person("Man", 1.0, 0.2, dict(skin=(0.86, 0.64, 0.5), top=(0.85, 0.1, 0.12), pants=(0.15, 0.18, 0.28),
                                     shoes=(0.2, 0.12, 0.08), hair=(0.12, 0.08, 0.06), iris=(0.3, 0.2, 0.12),
                                     collar=(0.95, 0.95, 0.95), buttons=(0.9, 0.85, 0.7), brow=1.2, lid=0.25))
    hair_cap(p, (0.12, 0.08, 0.06), off=(0, -0.14, 0.16))
    bag = box(p.hand_world("L") + Vector((0, 0.02, -0.18)), (0.12, 0.35, 0.28), toon("Bag", (0.3, 0.2, 0.12), 0.1),
              "Man bag", bevel=0.03)
    p.add(bag, p.p["elbowL"])
    gift = [box((0, 0, 0), (0.24, 0.24, 0.2), toon("Gift", (0.2, 0.7, 0.95), 0.35), "Gift", bevel=0.01),
            box((0, 0, 0.0), (0.26, 0.05, 0.21), toon("Ribbon", (1.0, 0.85, 0.15), 0.4), "Ribbon a"),
            box((0, 0, 0.0), (0.05, 0.26, 0.21), toon("Ribbon", (1.0, 0.85, 0.15), 0.4), "Ribbon b"),
            ball((0, 0, 0.12), 0.06, toon("Ribbon", (1.0, 0.85, 0.15), 0.4), "Bow", scale=(1.6, 1, 0.8))]
    groot = empty("Gift root")
    for g in gift:
        parent_keep(g, groot)
    return p, bag, groot


def make_girl():
    p = Person("Girl", 0.6, 0.17, dict(skin=(0.95, 0.76, 0.62), top=(1.0, 0.82, 0.2), pants=(1.0, 0.82, 0.2),
                                       shoes=(0.95, 0.4, 0.55), hair=(0.25, 0.14, 0.08), iris=(0.3, 0.2, 0.1),
                                       eye=1.2, lashes=True, blush=(0.98, 0.5, 0.55), collar=(1.0, 1.0, 1.0)))
    R, hc, head = p.R, p.head_c, p.p["head"]
    hair_cap(p, (0.25, 0.14, 0.08))
    for sx in (-1, 1):
        p.add(ball(hc + Vector((sx * 1.05 * R, -0.2 * R, 0.0)), 0.35 * R, toon("Girl hair", (0.25, 0.14, 0.08)),
                   "bunch", scale=(0.8, 0.8, 1.2)), head)
    bpy.ops.mesh.primitive_cone_add(radius1=0.22, radius2=0.1, depth=0.3, location=(0, 0, 0.42), vertices=20)
    p.add(finish(bpy.context.object, toon("Girl top", (1.0, 0.82, 0.2)), "dress", True), p.p["hips"])
    return p


def build_rifle(cam):
    """The rifle across the bottom of the POV: barrel on the parapet, scope, our hands on it."""
    root = empty("Rifle")
    parent_local(root, cam)
    dark = toon("Rifle", (0.12, 0.13, 0.12), 0.08)
    olive = toon("Rifle stock", (0.32, 0.35, 0.25), 0.1)
    parts = [rod((0.05, -0.32, -0.25), (0.02, -0.18, -3.0), 0.025, dark, "Barrel"),
             box((0.05, -0.35, -0.55), (0.1, 0.16, 0.6), olive, "Stock", bevel=0.03),
             rod((0.05, -0.23, -0.35), (0.05, -0.22, -0.8), 0.045, dark, "Scope"),
             rod((0.05, -0.23, -0.33), (0.05, -0.23, -0.37), 0.06, dark, "Scope ring"),
             rod((0.05, -0.22, -0.78), (0.05, -0.22, -0.82), 0.06, dark, "Scope ring")]
    for p in parts:
        parent_local(p, root)
    return root


def build():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.fps = FPS
    scene.frame_start, scene.frame_end = 1, int(END * FPS)
    scene.frame_step = 2

    cars = build_city()
    man, bag, gift = make_man()
    girl = make_girl()
    walkers = [make_extra(i, random.uniform(0.92, 1.02)) for i in range(16)]
    paths = []
    rnd = random.Random(4)
    for i in range(len(walkers)):
        r0 = rnd.uniform(7, 20)
        a0 = rnd.uniform(0, 2 * math.pi)
        da = rnd.choice((-1, 1)) * rnd.uniform(0.04, 0.08)
        paths.append((r0, a0, da))
    dot = ball((0, 0, 0), 0.05, glow_mat("Laser dot", (1.0, 0.0, 0.0), 30.0), "Laser dot")

    cam = make_camera(scene)
    cam.data.clip_end = 3000
    arms = POVArms(cam)
    rifle = build_rifle(cam)
    shake = random.Random(9)
    sh = [(shake.uniform(-1, 1), shake.uniform(-1, 1)) for _ in range(int(END * FPS) + 3)]
    scopes = scope_windows()
    eye = NEST + Vector((0, 12.95, 1.45))    # leaning over the parapet, at the very edge

    for f in range(1, int(END * FPS) + 1):
        t = (f - 1) / FPS
        scoped = any(a <= t < b for a, b in scopes)

        # ---------------- the man: waits, checks his watch, opens the bag, the girl, the hug, looks up
        watch = seg(t, at("me2"), at("me2") + 0.5) * (1 - seg(t, at("me2", 1), at("me2", 1) + 0.4))
        opening = seg(t, at("me3") - 0.4, at("me3") + 0.6)
        hug = seg(t, at("man1"), at("man1") + 0.6)
        up = seg(t, at("n2") - 1.4, at("n2") - 0.6)
        to_girl = yaw_to(Vector((-12, 6, 0)) - MAN)
        face = lerp_yaw(lerp_yaw(200, 230 + 10 * math.sin(t * 0.8), seg(t, 0, 1)), to_girl, seg(t, at("girl1") - 0.3, at("girl1") + 0.3))
        face = lerp_yaw(face, yaw_to(Vector((NEST.x, NEST.y, 0)) - MAN), up)
        man.pose(f, t, MAN, facing=face, crouch=0.55 * hug * (1 - up * 0.6), lean=0,
                 look=(8 * math.sin(t * 1.3) * (1 - up), lerp(lerp(-8, -35, watch), 62, up)),
                 reach=(lerp(lerp(20, 75, watch), 70, opening), lerp(0, 40, watch)),
                 reach2=(lerp(25, 65, opening), -10), hug=0.5 * hug * (1 - up), worry=lerp(1.4, 0.4, hug))
        bpy.context.view_layer.update()
        show([bag], f, t < at("girl1") + 0.4)
        gpos = man.hand_world("R") + Vector((0, 0, 0.12))
        gift.location = gpos if opening > 0.3 else Vector((0, 0, -50))
        gift.keyframe_insert("location", frame=f)

        # ---------------- the girl runs to him
        run = seg(t, at("girl1") - 1.4, at("man1") - 0.2)
        gp0, gp1 = Vector((-12.0, 6.0, 0)), MAN + Vector((-0.9, 0.55, 0))
        gp = gp0.lerp(gp1, run)
        girl.pose(f, t, gp, facing=yaw_to(gp1 - gp0) if run < 0.98 else yaw_to(MAN - gp1), run=1.0 if run < 0.98 else 0,
                  run_rate=2.4, lean=-6, reach=(150, 10) if run > 0.7 else None, reach2=(150, -10) if run > 0.7 else None,
                  look=(0, 15), hug=0.5 * hug, worry=0.3)

        # ---------------- the red dot on his chest (from "three seconds" on)
        on_dot = at("cmd2") + 0.6 <= t
        # chest point in the torso pivot's own space (the pivot sits at the hips)
        chest = man.p["torso"].matrix_world @ Vector((0, 0.17, man.torso_z - 0.86 * man.s + 0.12))
        dot.location = chest + Vector((0.03 * math.sin(t * 7), 0, 0.03 * math.cos(t * 5)))
        dot.scale = (1,) * 3 if on_dot else (0.001,) * 3
        dot.keyframe_insert("location", frame=f)
        dot.keyframe_insert("scale", frame=f)

        # ---------------- crowd and cars
        for i, w in enumerate(walkers):
            r0, a0, da = paths[i]
            a = a0 + da * t
            p = Vector((r0 * math.cos(a), r0 * math.sin(a), 0))
            tang = Vector((-math.sin(a), math.cos(a), 0)) * (1 if da > 0 else -1)
            w.pose(f, t, p, facing=yaw_to(tang), run=0.45, run_rate=1.1 + 0.1 * (i % 3), lean=0, look=(0, 0),
                   worry=0.4, reach=(150, 10) if i % 5 == 0 else None)
        for root, horiz, lane, off, spd in cars:
            s = (off + spd * t) % 800 - 400
            road = 31.0 * lane
            root.location = (s, road + 2.5 * lane, 0) if horiz else (road + 2.5 * lane, s, 0)
            root.rotation_euler = (0, 0, -math.pi / 2 if horiz else 0)
            root.keyframe_insert("location", frame=f)
            root.keyframe_insert("rotation_euler", frame=f)

        # ---------------- camera: the scope or the roof
        if scoped:
            if t < at("cmd1") - 1.0:   # hook: drifting over the crowd
                aim = Vector((lerp(-14, 6, t / max(1, at("cmd1") - 1.0)), lerp(-8, 4, t / max(1, at("cmd1"))), 1.0))
                lens = 900
            else:
                search = seg(t, at("me1") - 1.2, at("me1") + 0.3)
                aim = Vector((-10, 10, 1.0)).lerp(MAN + Vector((0, 0, 1.2)), search)
                lens = lerp(700, 1500, search)
                lens = lerp(lens, 2600, seg(t, at("me2"), at("me2") + 1.0))                # the bag, the watch
                lens = lerp(lens, 2000, seg(t, at("me3"), at("me3") + 0.6))
                aim = aim.lerp(MAN.lerp(Vector((-12, 6, 0)), 0.25) + Vector((0, 0, 1.0)),
                               seg(t, at("girl1") - 1.2, at("girl1")) * (1 - seg(t, at("man1"), at("man1") + 0.6)))
                lens = lerp(lens, 1400, seg(t, at("girl1") - 1.2, at("girl1")) * (1 - seg(t, at("man1"), at("man1") + 0.6)))
                lens = lerp(lens, 3400, seg(t, at("n2") - 1.6, at("n2") - 0.4))           # his face, looking up
                aim = aim.lerp(MAN + Vector((0, 0, 1.55 - 0.3 * hug)), seg(t, at("n2") - 1.6, at("n2") - 0.4))
            d = aim - eye
            yaw, pitch = yaw_to(d), pitch_to(d)
            amp = 0.006 + 0.02 * seg(t, at("cmd3"), at("cmd3") + 0.3) * (1 - seg(t, at("me4", 1), at("me4", 1) + 0.6))
        else:
            # on the roof: wind, the whole city at dusk, the square far below
            lens = 12
            d = Vector((0, 0, 0)) - eye
            yaw, pitch = yaw_to(d) + 14, pitch_to(d) + 34     # the skyline, the square far below
            amp = 0.4
        cam.data.lens = lens
        cam.data.keyframe_insert("lens", frame=f)
        hx, hy = sh[f]
        cam.location = eye
        cam.rotation_euler = (D(90 + pitch + hx * amp), 0, D(yaw + hy * amp))
        cam.keyframe_insert("location", frame=f)
        cam.keyframe_insert("rotation_euler", frame=f)
        rifle.scale = (0.001,) * 3 if scoped else (1,) * 3
        rifle.keyframe_insert("scale", frame=f)
        if scoped:
            arms.set(f, "L", (-0.3, -3.0, 0.5))
            arms.set(f, "R", (0.3, -3.0, 0.5))
        else:
            arms.set(f, "L", (-0.02, -0.25, -0.75))   # under the barrel
            arms.set(f, "R", (0.12, -0.36, -0.42))    # on the grip

    bpy.ops.object.light_add(type="SUN", rotation=(D(78), D(5), D(-125)))
    sun = bpy.context.object
    sun.data.energy = 2.4
    sun.data.color = (1.0, 0.72, 0.48)
    setup_render(scene, sky=(0.95, 0.62, 0.45), sky_strength=0.8)
    scene.frame_set(1)
    return scene


if __name__ == "__main__":
    run_cli(build(), "sniper1.blend")
