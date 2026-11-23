"""
«زنگ آخر» — 75 s first-person cartoon film (+5 s question card added in post.py).

Sets live side by side in one scene and the POV camera cuts between them:
    house (x≈0) -> street + school gate (x≈60) -> classroom on the 2nd floor with the
    schoolyard below (x≈120) -> stairwell + roof with the helicopter (x≈200).
No flags, emblems, logos or place names anywhere (on purpose).

    blender -b --python scene.py -- --still 300,900
    blender -b --python scene.py -- --render [--range 1 600]
"""

import math
import os
import random
import sys

import bpy
from mathutils import Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403,E402

SECONDS = 75
FRAMES = FPS * SECONDS
random.seed(13)
TEX = os.path.join(HERE, "textures")

HX, SX, CX, RX = 0.0, 60.0, 120.0, 200.0  # set origins along X

# ================================================================ helpers


def image_mat(name, path, strength=1.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = bpy.data.images.load(path)
    e = nt.nodes.new("ShaderNodeEmission")
    e.inputs["Strength"].default_value = strength
    nt.links.new(tex.outputs["Color"], e.inputs["Color"])
    nt.links.new(e.outputs[0], out.inputs["Surface"])
    return m


def plane(loc, size, rot, m, name="Plane"):
    bpy.ops.mesh.primitive_plane_add(size=1, location=loc, rotation=rot)
    o = bpy.context.object
    o.scale = (size[0], size[1], 1)
    bpy.ops.object.transform_apply(scale=True)
    return finish(o, m, name)


def show(o, f, visible, size=1.0):
    o.scale = (size,) * 3 if visible else (0.001,) * 3
    o.keyframe_insert("scale", frame=f)


def walls_room(c, w, d, h, wall_m, floor_m, ceil_m=None, skip=()):
    """Box room centred at c (x, y) with floor at z=c.z.  skip: walls to leave out."""
    x, y, z = c
    box((x, y, z - 0.05), (w, d, 0.1), floor_m, "Floor")
    if ceil_m:
        box((x, y, z + h + 0.05), (w, d, 0.1), ceil_m, "Ceiling")
    for key, loc, size in (("N", (x, y + d / 2, z + h / 2), (w, 0.12, h)),
                           ("S", (x, y - d / 2, z + h / 2), (w, 0.12, h)),
                           ("W", (x - w / 2, y, z + h / 2), (0.12, d, h)),
                           ("E", (x + w / 2, y, z + h / 2), (0.12, d, h))):
        if key not in skip:
            box(loc, size, wall_m, f"Wall {key}")


# ================================================================ characters


def kid(name, look, s=0.7, R=0.17):
    look = dict(look)
    look.setdefault("iris", (0.3, 0.2, 0.1))
    return Person(name, s, R, look)


def make_mom():
    p = Person("Mom", 0.98, 0.2, dict(skin=(0.93, 0.72, 0.58), top=(0.95, 0.88, 0.7), pants=(0.25, 0.3, 0.45),
                                      shoes=(0.85, 0.4, 0.45), hair=(0.4, 0.22, 0.1), iris=(0.3, 0.45, 0.25),
                                      lashes=True, lips=(0.8, 0.35, 0.38), blush=(0.95, 0.6, 0.6), lid=0.3,
                                      buttons=(0.6, 0.4, 0.2), collar=(0.95, 0.88, 0.7)))
    hair = (0.4, 0.22, 0.1)
    hair_cap(p, hair, off=(0, -0.1, 0.12), r=1.06)
    p.add(ball(p.head_c + Vector((0, -1.0 * p.R, 0.05 * p.R)), 0.45 * p.R, toon("Mom hair", hair), "bun"),
          p.p["head"])
    p.add(ball(p.head_c + Vector((0, -1.15 * p.R, -0.5 * p.R)), 0.3 * p.R, toon("Mom hair", hair), "ponytail",
               scale=(0.8, 0.8, 1.8)), p.p["head"])
    hp = p.p["handR"].matrix_world.translation
    mug = rod(hp + Vector((0, 0.06, -0.05)), hp + Vector((0, 0.06, 0.07)), 0.045, toon("Mug", (0.9, 0.3, 0.25)), "mug")
    p.add(mug, p.p["elbowR"])
    return p


def make_anchor():
    p = Person("Anchor", 0.33, 0.075, dict(skin=(0.88, 0.66, 0.5), top=(0.12, 0.15, 0.28), pants=(0.12, 0.15, 0.28),
                                            shoes=(0.05, 0.05, 0.05), hair=(0.15, 0.1, 0.07), collar=(0.97, 0.97, 0.97),
                                            iris=(0.25, 0.18, 0.1), brow=1.2))
    hair_cap(p, (0.15, 0.1, 0.07), off=(0, -0.15, 0.25), r=1.02, scale=(1, 0.95, 0.85))
    p.add(box((0, 0.045, p.torso_z + 0.03), (0.022, 0.01, 0.13), toon("Tie", (0.85, 0.1, 0.1)), "tie"),
          p.p["torso"])
    return p


def make_kazemi():
    p = Person("Kazemi", 1.0, 0.2, dict(skin=(0.85, 0.63, 0.48), top=(0.5, 0.33, 0.2), pants=(0.3, 0.3, 0.32),
                                         shoes=(0.2, 0.12, 0.08), hair=(0.25, 0.22, 0.2), iris=(0.3, 0.2, 0.1),
                                         collar=(0.92, 0.92, 0.95), buttons=(0.85, 0.7, 0.4), belly=0.6, brow=1.2,
                                         nose=(1.2, 1.15, 1.1)))
    hair_cap(p, (0.25, 0.22, 0.2), off=(0, -0.3, 0.0), r=1.02, scale=(1.05, 0.9, 0.8))
    glasses(p, (0.1, 0.1, 0.1))
    p.add(ball(p.head_c + Vector((0, 0.92 * p.R, -0.35 * p.R)), 0.25 * p.R, toon("Kazemi hair", (0.25, 0.22, 0.2)),
               "mustache", scale=(1.7, 0.6, 0.5)), p.p["head"])
    hp = p.p["handR"].matrix_world.translation
    p.add(rod(hp + Vector((0, 0.05, -0.04)), hp + Vector((0, 0.05, 0.06)), 0.012, toon("Chalk", (0.98, 0.98, 0.95), 0.5),
              "chalk"), p.p["elbowR"])
    return p


def make_arian():
    p = kid("Arian", dict(skin=(0.9, 0.68, 0.52), top=(0.98, 0.5, 0.1), pants=(0.2, 0.25, 0.45), shoes=(0.95, 0.95, 0.95),
                          hair=(0.1, 0.07, 0.05), blush=(0.95, 0.55, 0.5), eye=1.15, buttons=None,
                          collar=(0.98, 0.5, 0.1)))
    hair_cap(p, (0.1, 0.07, 0.05), off=(0, -0.1, 0.15))
    for k in range(7):  # spiky hair
        a = D(-80 + k * 27)
        tip = p.head_c + Vector((math.sin(a) * 0.6 * p.R, -0.1 * p.R + math.cos(a) * 0.3 * p.R, 1.2 * p.R))
        bpy.ops.mesh.primitive_cone_add(radius1=0.22 * p.R, depth=0.55 * p.R, location=tip, vertices=10,
                                        rotation=(D(-20) * math.cos(a), D(25) * math.sin(a), 0))
        p.add(finish(bpy.context.object, toon("Arian hair", (0.1, 0.07, 0.05)), "spike", True), p.p["head"])
    return p


def make_mahsa():
    p = kid("Mahsa", dict(skin=(0.95, 0.76, 0.62), top=(0.15, 0.2, 0.42), pants=(0.3, 0.3, 0.35), shoes=(0.9, 0.25, 0.3),
                          hair=(0.05, 0.04, 0.04), lashes=True, blush=(0.95, 0.55, 0.6), iris=(0.2, 0.3, 0.5),
                          collar=(0.98, 0.98, 0.98)), s=0.72)
    hair_cap(p, (0.05, 0.04, 0.04), off=(0, -0.1, 0.12), r=1.06)
    p.add(ball(p.head_c + Vector((0, -1.05 * p.R, 0.2 * p.R)), 0.16 * p.R, toon("Hair tie red", (0.9, 0.1, 0.12)),
               "hair tie"), p.p["head"])
    p.add(ball(p.head_c + Vector((0, -1.25 * p.R, -0.35 * p.R)), 0.3 * p.R, toon("Mahsa hair", (0.05, 0.04, 0.04)),
               "ponytail", scale=(0.8, 0.8, 2.0)), p.p["head"])
    glasses(p, (0.6, 0.2, 0.5))
    return p


def make_kian():
    p = kid("Kian", dict(skin=(0.97, 0.8, 0.66), top=(0.35, 0.6, 0.85), pants=(0.45, 0.32, 0.2), shoes=(0.95, 0.75, 0.1),
                         hair=(0.55, 0.32, 0.12), eye=1.25, blush=(0.98, 0.55, 0.55), iris=(0.25, 0.5, 0.3)),
            s=0.6, R=0.165)
    hair_cap(p, (0.55, 0.32, 0.12), off=(0, -0.05, 0.12), r=1.07)
    bag = toon("Dino bag", (0.3, 0.7, 0.25))
    p.add(box((0, -0.17, 0.75 * p.s + 0.25), (0.28, 0.14, 0.32), bag, "dino bag", bevel=0.04), p.p["torso"])
    for k in range(4):
        bpy.ops.mesh.primitive_cone_add(radius1=0.035, depth=0.07, location=(0, -0.25, 0.62 + k * 0.08),
                                        rotation=(D(-90), 0, 0), vertices=8)
        p.add(finish(bpy.context.object, toon("Dino spikes", (0.98, 0.8, 0.2)), "dino spike", True), p.p["torso"])
    return p


JANITOR = dict(top=(0.2, 0.35, 0.65), pants=(0.2, 0.35, 0.65), shoes=(0.15, 0.1, 0.08), hair=(0.6, 0.6, 0.6),
               brow=1.3, belt=(0.15, 0.1, 0.05), buttons=(0.9, 0.85, 0.5), nose=(1.3, 1.2, 1.2))


def make_rezaei(zombie=False):
    L = dict(JANITOR)
    if zombie:
        L.update(skin=(0.58, 0.66, 0.52), iris=(0.86, 0.88, 0.82), pupil=(0.78, 0.8, 0.75), lid=0.45)
    else:
        L.update(skin=(0.82, 0.6, 0.45), iris=(0.3, 0.2, 0.1), lid=0.3)
    p = Person("RezaeiZ" if zombie else "Rezaei", 1.0, 0.2, L)
    hair_cap(p, L["hair"], off=(0, -0.3, 0.0), r=1.02, scale=(1.05, 0.9, 0.75))
    p.add(ball(p.head_c + Vector((0, 0.92 * p.R, -0.35 * p.R)), 0.28 * p.R, toon(f"{p.name} hair", L["hair"]),
               "mustache", scale=(1.8, 0.6, 0.55)), p.p["head"])
    keys = toon("Keys", (0.95, 0.8, 0.2), 0.4)
    bpy.ops.mesh.primitive_torus_add(location=(0.2, 0.12, 0.88), major_radius=0.04, minor_radius=0.008,
                                     rotation=(D(90), 0, 0))
    p.add(finish(bpy.context.object, keys, "key ring", True), p.p["hips"])
    return p


ZOMBIE_CLOTHES = [(0.75, 0.25, 0.2), (0.25, 0.4, 0.6), (0.55, 0.5, 0.25), (0.4, 0.3, 0.45), (0.3, 0.5, 0.35),
                  (0.7, 0.6, 0.5), (0.45, 0.45, 0.45)]


def make_zombie(i, s=None):
    c = ZOMBIE_CLOTHES[i % len(ZOMBIE_CLOTHES)]
    L = dict(skin=random.choice([(0.58, 0.66, 0.52), (0.55, 0.6, 0.58), (0.62, 0.64, 0.5)]), top=c,
             pants=tuple(v * 0.6 for v in c), shoes=(0.12, 0.1, 0.08), hair=random.choice([(0.1, 0.08, 0.06),
                                                                                         (0.35, 0.3, 0.25)]),
             iris=(0.86, 0.88, 0.82), pupil=(0.78, 0.8, 0.75), lid=0.5, brow_col=(0.1, 0.1, 0.1))
    p = Person(f"Zombie{i}", s or random.uniform(0.92, 1.05), 0.2, L)
    hair_cap(p, L["hair"], off=(0.1, -0.2, 0.1), r=1.0, scale=(1, 0.95, 0.85))
    for k in range(2):  # torn dark patches on clothes
        p.add(box((random.uniform(-0.12, 0.12), 0.135, p.torso_z + random.uniform(-0.15, 0.15)), (0.1, 0.01, 0.07),
                  toon("Torn", (0.15, 0.12, 0.1)), "tear"), p.p["torso"])
    return p


def make_soldier():
    L = dict(skin=(0.75, 0.72, 0.62), top=(0.3, 0.38, 0.24), pants=(0.3, 0.38, 0.24), shoes=(0.08, 0.08, 0.08),
             hair=(0.1, 0.08, 0.06), iris=(0.86, 0.88, 0.82), pupil=(0.78, 0.8, 0.75), lid=0.4,
             gloves=(0.08, 0.08, 0.08), belt=(0.15, 0.13, 0.1), cuff=(0.75, 0.72, 0.62))
    p = Person("Soldier", 1.05, 0.2, L)
    R, hc, head = p.R, p.head_c, p.p["head"]
    p.add(ball(hc + Vector((0, 0, 0.4 * R)), 1.12 * R, toon("Helmet", (0.27, 0.34, 0.22)), "helmet",
               scale=(1, 1.05, 0.7)), head)
    mask = [p.add(box(hc + Vector((0, 0.85 * R, -0.45 * R)), (1.1 * R, 0.5 * R, 0.6 * R),
                      toon("Mask", (0.35, 0.35, 0.37)), "mask", bevel=0.03), head),
            p.add(box(hc + Vector((0, 0.95 * R, 0.12 * R)), (1.2 * R, 0.25 * R, 0.4 * R),
                      toon("Goggles", (0.06, 0.07, 0.08)), "goggles", bevel=0.03), head),
            p.add(ball(hc + Vector((0, 1.1 * R, -0.5 * R)), 0.18 * R, toon("Filter", (0.2, 0.2, 0.22)), "filter",
                       scale=(1, 0.6, 1)), head)]
    for o in mask:
        o.name = "Soldier mask part"
    # bite mark just above the right glove
    hp = p.p["handR"].matrix_world.translation
    bite = p.add(ball(hp + Vector((0, 0.05, 0.12)), 0.035, toon("Bite", (0.55, 0.05, 0.08), 0.3), "bite",
                      scale=(1.2, 0.5, 0.8)), p.p["elbowR"])
    return p, mask, bite


def make_student(i):
    looks = [dict(top=(0.95, 0.35, 0.45), hair=(0.1, 0.06, 0.04), lashes=True),
             dict(top=(0.3, 0.75, 0.4), hair=(0.25, 0.15, 0.08)),
             dict(top=(0.98, 0.8, 0.2), hair=(0.05, 0.04, 0.03)),
             dict(top=(0.55, 0.35, 0.8), hair=(0.4, 0.25, 0.1), lashes=True),
             dict(top=(0.2, 0.7, 0.75), hair=(0.1, 0.06, 0.04)),
             dict(top=(0.85, 0.45, 0.2), hair=(0.6, 0.4, 0.15), lashes=True),
             dict(top=(0.4, 0.55, 0.9), hair=(0.12, 0.08, 0.05))]
    L = dict(looks[i % len(looks)])
    L.update(skin=random.choice([(0.95, 0.76, 0.62), (0.82, 0.6, 0.45), (0.7, 0.5, 0.36)]), pants=(0.25, 0.25, 0.32),
             shoes=(0.9, 0.9, 0.9), iris=(0.3, 0.2, 0.1), blush=(0.95, 0.55, 0.55))
    p = kid(f"Student{i}", L, s=random.uniform(0.62, 0.74))
    hair_cap(p, L["hair"], off=(0, -0.1, 0.12), r=1.05)
    return p


# ================================================================ sets


def build_house():
    floor_m = toon("House floor", (0.62, 0.42, 0.26))
    wall_m = toon("House wall", (0.96, 0.85, 0.72), 0.15)
    walls_room((HX, 0, 0), 8, 9, 5.6, wall_m, floor_m, toon("House ceiling", (0.98, 0.95, 0.9), 0.15), skip=("S",))
    # front wall with the street door
    box((HX - 1.2, -4.5, 2.8), (5.6, 0.12, 5.6), wall_m, "Front wall")
    box((HX + 3.4, -4.5, 2.8), (1.2, 0.12, 5.6), wall_m, "Front wall")
    box((HX + 2.0, -4.5, 3.9), (1.6, 0.12, 3.4), wall_m, "Above door")
    door = empty("Front door hinge", (HX + 1.55, -4.48, 0))
    d = box((HX + 2.0, -4.48, 1.1), (0.9, 0.08, 2.2), toon("Front door", (0.5, 0.28, 0.15)), "Front door")
    parent_keep(d, door)
    door.rotation_mode = "XYZ"
    # outside the door: bright morning
    plane((HX + 2.0, -5.5, 1.2), (3, 3), (D(90), 0, 0), glow_mat("Outside light", (0.95, 0.97, 1.0), 2.0), "Daylight")
    # stairs down along the west wall (top at the back)
    wood = toon("Stairs", (0.55, 0.33, 0.18))
    for k in range(12):
        y = 3.3 - k * 0.3
        z = 2.8 - (k + 1) * 0.233
        box((HX - 3.3, y, z / 2), (1.2, 0.3, z), wood, "Step")
    box((HX - 3.3, 4.0, 1.4), (1.2, 1.0, 2.8), wood, "Landing")
    rail_m = toon("Rail", (0.4, 0.22, 0.1))
    for k in range(0, 12, 2):
        y = 3.3 - k * 0.3
        z = 2.8 - (k + 1) * 0.233
        rod((HX - 2.72, y, z), (HX - 2.72, y, z + 0.9), 0.025, rail_m, "Baluster")
    rod((HX - 2.72, 3.4, 3.7), (HX - 2.72, -0.3, 1.1), 0.04, rail_m, "Handrail")
    # living room
    sofa = toon("Sofa", (0.15, 0.55, 0.55))
    box((HX - 0.6, -0.6, 0.25), (2.1, 0.9, 0.5), sofa, "Sofa seat", bevel=0.08)
    box((HX - 0.6, -0.12, 0.65), (2.1, 0.25, 0.85), sofa, "Sofa back", bevel=0.08)
    for x in (-1.6, 0.4):
        box((HX + x, -0.6, 0.45), (0.25, 0.9, 0.5), sofa, "Sofa arm", bevel=0.08)
    for x, c in ((-1.1, (0.98, 0.7, 0.2)), (-0.1, (0.95, 0.4, 0.45))):
        box((HX + x, -0.35, 0.65), (0.4, 0.15, 0.35), toon(f"Cushion {c}", c), "Cushion", bevel=0.06)
    bpy.ops.mesh.primitive_cylinder_add(radius=1.4, depth=0.02, location=(HX - 0.6, -2.0, 0.01), vertices=48)
    finish(bpy.context.object, toon("Rug", (0.85, 0.3, 0.3)), "Rug")
    bpy.ops.mesh.primitive_cylinder_add(radius=0.9, depth=0.025, location=(HX - 0.6, -2.0, 0.02), vertices=48)
    finish(bpy.context.object, toon("Rug inner", (0.98, 0.8, 0.35)), "Rug inner")
    box((HX - 0.6, -1.9, 0.22), (1.0, 0.55, 0.06), toon("Table", (0.75, 0.55, 0.35)), "Coffee table")
    for dx in (-0.4, 0.4):
        for dy in (-0.2, 0.2):
            box((HX - 0.6 + dx, -1.9 + dy, 0.1), (0.05, 0.05, 0.2), toon("Table", (0.75, 0.55, 0.35)), "Table leg")
    # TV with a tiny news studio inside (the anchor is a real 3D character)
    tv = toon("TV", (0.08, 0.08, 0.09))
    tvc = Vector((HX - 0.6, -4.25, 1.35))
    box(tvc + Vector((0, 0, -0.62)), (1.9, 0.4, 0.5), toon("TV stand", (0.35, 0.25, 0.2)), "TV stand", bevel=0.03)
    box(tvc + Vector((0, 0.08, 0.53)), (1.7, 0.1, 0.06), tv, "TV top")
    box(tvc + Vector((0, 0.08, -0.53)), (1.7, 0.1, 0.06), tv, "TV bottom")
    for sx in (-1, 1):
        box(tvc + Vector((sx * 0.82, 0.08, 0)), (0.06, 0.1, 1.12), tv, "TV side")
    box(tvc + Vector((0, -0.12, 0)), (1.6, 0.04, 1.0), toon("Studio", (0.2, 0.45, 0.85), 0.8), "Studio wall")
    for k in range(5):
        box(tvc + Vector((-0.6 + k * 0.3, -0.09, 0.15)), (0.12, 0.01, 0.6), toon("Studio stripe", (0.35, 0.6, 0.95), 0.8),
            "Studio stripe")
    box(tvc + Vector((0, 0.0, -0.33)), (0.9, 0.12, 0.25), toon("News desk", (0.9, 0.9, 0.95), 0.6), "News desk")
    plane(tvc + Vector((0, 0.07, -0.42)), (1.6, 0.17), (D(90), 0, 0), image_mat("Banner", os.path.join(TEX, "tv_banner.png"),
                                                                              1.2), "Banner")
    # window, plant, shelf, frames with abstract art (no faces, no symbols)
    plane((HX + 3.93, 0.5, 1.8), (2.0, 1.4), (D(90), 0, D(90)), glow_mat("Window", (0.85, 0.92, 1.0), 2.5), "Window")
    box((HX + 3.9, 0.5, 1.8), (0.08, 2.1, 0.08), toon("Frame", (0.98, 0.98, 0.98)), "Window bar")
    rod((HX + 3.0, -3.6, 0.0), (HX + 3.0, -3.6, 0.5), 0.2, toon("Pot", (0.8, 0.4, 0.2)), "Pot")
    for k in range(4):
        ball((HX + 3.0 + random.uniform(-0.2, 0.2), -3.6 + random.uniform(-0.2, 0.2), 0.75 + k * 0.15), 0.25,
             toon("Plant", (0.25, 0.6, 0.3)), "Leaves")
    for k, c in enumerate([(0.98, 0.75, 0.2), (0.3, 0.6, 0.9), (0.9, 0.35, 0.4)]):
        box((HX + 1.0 + k * 0.7, 4.44, 1.8 + (k % 2) * 0.3), (0.5, 0.04, 0.4), toon("Frame", (0.98, 0.98, 0.98)), "Frame")
        box((HX + 1.0 + k * 0.7, 4.41, 1.8 + (k % 2) * 0.3), (0.4, 0.02, 0.3), toon(f"Art {k}", c, 0.3), "Art")
    bpy.ops.object.light_add(type="AREA", location=(HX + 2.5, 0.5, 2.0), rotation=(0, D(-90), 0))
    lamp = bpy.context.object
    lamp.data.energy = 250
    lamp.data.size = 2.0
    lamp.data.color = (1.0, 0.95, 0.85)
    bpy.ops.object.light_add(type="POINT", location=(HX - 0.6, -1.5, 3.5))
    bpy.context.object.data.energy = 60
    return door


def build_street():
    asphalt = toon("Asphalt", (0.25, 0.26, 0.28))
    pave = toon("Pavement", (0.7, 0.68, 0.64))
    box((SX + 4.0, 15, -0.05), (40, 80, 0.1), toon("Ground", (0.5, 0.62, 0.35)), "Street ground")
    box((SX + 1.2, 10, 0.06), (2.6, 60, 0.12), pave, "Sidewalk")
    box((SX + 6.0, 10, 0.0), (7.0, 60, 0.05), asphalt, "Road")
    for y in range(-18, 40, 5):
        box((SX + 6.0, y, 0.03), (0.15, 2.0, 0.02), toon("Lane", (0.95, 0.95, 0.9), 0.4), "Lane dash")
    cols = [(0.95, 0.7, 0.55), (0.75, 0.85, 0.95), (0.95, 0.9, 0.6), (0.8, 0.95, 0.8), (0.95, 0.75, 0.8)]
    for k, y in enumerate(range(-16, 16, 6)):
        c = cols[k % len(cols)]
        h = random.uniform(4.5, 7.5)
        box((SX - 3.5, y, h / 2), (4.5, 5.6, h), toon(f"House {c}", c, 0.15), "Row house")
        box((SX - 3.5, y, h + 0.3), (4.8, 5.9, 0.6), toon("Roof edge", (0.75, 0.35, 0.25)), "Roof edge")
        for wz in (1.4, 3.6):
            for wy in (-1.4, 1.4):
                box((SX - 1.23, y + wy, wz), (0.06, 1.0, 1.1), toon("House window", (0.4, 0.6, 0.75), 0.3), "Window")
        box((SX - 1.23, y, 1.0), (0.06, 0.9, 2.0), toon("House door", (0.55, 0.3, 0.2)), "Door")
    for y in range(-14, 18, 7):
        rod((SX + 2.35, y, 0), (SX + 2.35, y, 1.8), 0.12, toon("Trunk", (0.45, 0.3, 0.2)), "Tree trunk")
        ball((SX + 2.35, y, 2.6), 1.1, toon("Tree", (0.3, 0.62, 0.3)), "Tree")
    # school wall and gate ahead
    sw = toon("School wall", (0.92, 0.82, 0.62), 0.15)
    box((SX - 2.5, 18.0, 1.2), (6.6, 0.4, 2.4), sw, "School wall")
    box((SX + 3.6, 18.0, 1.2), (3.6, 0.4, 2.4), sw, "School wall")
    for k in range(9):
        rod((SX + 0.0 + k * 0.22, 18.0, 0), (SX + 0.0 + k * 0.22, 18.0, 2.0), 0.02, toon("Gate", (0.2, 0.35, 0.3)), "Gate bar")
    box((SX + 4.0, 26, 4.0), (16, 10, 8), toon("School", (0.98, 0.88, 0.6), 0.15), "School building")
    for wx in range(-3, 4):
        for wz in (2.0, 5.2):
            box((SX + 4.0 + wx * 2.0, 20.95, wz), (1.2, 0.1, 1.4), toon("School window", (0.4, 0.6, 0.75), 0.3), "Window")
    # plain army truck (no markings)
    olive = toon("Truck", (0.33, 0.4, 0.25))
    truck = empty("Truck", (SX + 4.5, -25, 0))
    parts = [box((SX + 4.5, -25 + 2.3, 1.3), (2.2, 1.6, 1.6), olive, "Truck cab", bevel=0.1),
             box((SX + 4.5, -25 + 2.9, 1.6), (2.0, 0.1, 0.6), toon("Truck glass", (0.2, 0.3, 0.35)), "Windscreen"),
             box((SX + 4.5, -25 - 0.8, 1.7), (2.3, 4.2, 2.0), toon("Canvas", (0.38, 0.42, 0.3)), "Canvas", bevel=0.2)]
    for dy in (-2.0, -0.3, 2.3):
        for dx in (-1.0, 1.0):
            bpy.ops.mesh.primitive_cylinder_add(radius=0.48, depth=0.35, location=(SX + 4.5 + dx, -25 + dy, 0.48),
                                                rotation=(0, D(90), 0), vertices=20)
            parts.append(finish(bpy.context.object, toon("Tyre", (0.08, 0.08, 0.08)), "Tyre", True))
    for p in parts:
        parent_keep(p, truck)
    return truck


def build_classroom():
    wall = toon("Class wall", (0.95, 0.9, 0.75), 0.15)
    lower = toon("Class wall lower", (0.55, 0.75, 0.7), 0.15)
    floor_m = toon("Class floor", (0.7, 0.55, 0.38))
    box((CX, 0, -0.05), (8, 9, 0.1), floor_m, "Class floor")
    box((CX, 0, 3.25), (8, 9, 0.1), toon("Class ceiling", (0.97, 0.96, 0.92), 0.15), "Class ceiling")
    box((CX, 4.5, 1.6), (8, 0.12, 3.2), wall, "Front wall")
    box((CX, -4.5, 1.6), (8, 0.12, 3.2), wall, "Back wall")
    # east wall with the corridor door (glass panel at the top)
    box((CX + 4.0, -1.0, 1.6), (0.12, 7.0, 3.2), wall, "East wall")
    box((CX + 4.0, 4.0, 1.6), (0.12, 1.0, 3.2), wall, "East wall")
    box((CX + 4.0, 3.0, 2.85), (0.12, 1.0, 0.7), wall, "Above door")
    door_m = toon("Class door", (0.6, 0.35, 0.2))
    box((CX + 4.0, 3.0, 0.55), (0.08, 1.0, 1.1), door_m, "Door low")
    box((CX + 4.0, 3.0, 2.3), (0.08, 1.0, 0.4), door_m, "Door top")
    for dy in (-0.42, 0.42):
        box((CX + 4.0, 3.0 + dy, 1.7), (0.08, 0.16, 0.9), door_m, "Door side")
    door_glass = box((CX + 4.0, 3.0, 1.7), (0.03, 0.68, 0.85), toon("Door glass", (0.7, 0.85, 0.9), 0.5), "Door glass")
    box((CX + 5.5, 3.0, 1.6), (3.0, 3.0, 3.2), toon("Corridor", (0.3, 0.3, 0.33), 0.05), "Corridor back")
    # west wall with three big windows over the yard
    for y0, y1 in ((-4.5, -3.4), (-1.6, -0.9), (0.9, 1.6), (3.4, 4.5)):
        box((CX - 4.0, (y0 + y1) / 2, 1.6), (0.12, y1 - y0, 3.2), wall, "West pillar")
    box((CX - 4.0, 0, 0.5), (0.12, 9, 1.0), wall, "Under windows")
    box((CX - 4.0, 0, 2.95), (0.12, 9, 0.5), wall, "Over windows")
    box((CX - 3.92, 0, 1.02), (0.2, 9, 0.06), toon("Sill", (0.98, 0.98, 0.98)), "Sill")
    for x in (-3.9, 3.9):
        box((CX + x, 0, 0.35), (0.06, 9, 0.7), lower, "Lower paint")
    # blackboard, clock, loudspeaker, poster, drawings
    plane((CX, 4.43, 1.75), (3.6, 1.45), (D(90), 0, D(180)), image_mat("Chalkboard", os.path.join(TEX, "chalkboard.png"),
                                                                     0.9), "Blackboard")
    box((CX, 4.42, 1.75), (3.8, 0.03, 1.6), toon("Board frame", (0.5, 0.3, 0.15)), "Board frame")
    box((CX, 4.3, 0.95), (3.6, 0.15, 0.04), toon("Chalk tray", (0.5, 0.3, 0.15)), "Chalk tray")
    bpy.ops.mesh.primitive_cylinder_add(radius=0.28, depth=0.05, location=(CX - 2.6, 4.42, 2.65), rotation=(D(90), 0, 0),
                                        vertices=32)
    finish(bpy.context.object, toon("Clock", (0.98, 0.98, 0.95), 0.6), "Clock")
    hands = []
    for L, w in ((0.2, 0.025), (0.14, 0.035)):
        h = empty("Clock hand", (CX - 2.6, 4.38, 2.65))
        b = box((CX - 2.6, 4.38, 2.65 + L / 2), (w, 0.01, L), toon("Ink", (0.03, 0.03, 0.03), 0.0), "Clock hand")
        parent_keep(b, h)
        h.rotation_mode = "XYZ"
        hands.append(h)
    speaker = box((CX + 2.6, 4.35, 2.8), (0.5, 0.2, 0.35), toon("Speaker", (0.85, 0.85, 0.82)), "Loudspeaker", bevel=0.04)
    for k in range(4):
        box((CX + 2.6, 4.24, 2.7 + k * 0.06), (0.36, 0.01, 0.02), toon("Ink", (0.03, 0.03, 0.03), 0.0), "Grille")
    plane((CX + 3.93, -1.2, 1.9), (1.6, 1.0), (D(90), 0, D(90)), toon("Poster", (0.08, 0.1, 0.25), 0.4), "Space poster")
    for k, (c, r) in enumerate([((0.98, 0.8, 0.2), 0.12), ((0.6, 0.6, 0.6), 0.03), ((0.95, 0.7, 0.4), 0.04),
                                ((0.3, 0.6, 0.95), 0.045), ((0.9, 0.35, 0.2), 0.035), ((0.85, 0.65, 0.45), 0.08)]):
        ball((CX + 3.9, -1.85 + k * 0.25 + (0.05 if k else 0), 1.9), r, toon(f"Planet {k}", c, 0.5), "Planet",
             scale=(0.3, 1, 1))
    for k, c in enumerate([(0.98, 0.6, 0.6), (0.6, 0.85, 0.6), (0.6, 0.75, 0.98), (0.98, 0.9, 0.5), (0.85, 0.6, 0.95)]):
        box((CX - 2.6 + k * 1.2, -4.42, 1.9 + (k % 2) * 0.25), (0.6, 0.02, 0.45), toon(f"Drawing {k}", c, 0.4), "Drawing")
        ball((CX - 2.6 + k * 1.2, -4.41, 1.9 + (k % 2) * 0.25), 0.1, toon(f"Sun {k}", (0.98, 0.8, 0.2), 0.5), "Doodle",
             scale=(1, 0.2, 1))
    # desks + chairs: 3 columns x 4 rows of two-seat desks facing the board (+Y)
    desk_m = toon("Desk", (0.82, 0.62, 0.38))
    leg_m = toon("Desk leg", (0.25, 0.45, 0.6))
    chair_m = toon("Chair", (0.2, 0.55, 0.7))
    moving = None
    for col in (-2.1, 0.0, 2.1):
        for row in (1.4, 0.0, -1.4, -2.8):
            d = empty("Desk", (CX + col, row + 0.35, 0))
            parts = [box((CX + col, row + 0.35, 0.72), (1.3, 0.5, 0.05), desk_m, "Desk top", bevel=0.015)]
            for dx in (-0.6, 0.6):
                parts.append(box((CX + col + dx, row + 0.35, 0.36), (0.05, 0.45, 0.7), leg_m, "Desk leg"))
            for dx in (-0.32, 0.32):
                parts.append(box((CX + col + dx, row - 0.12, 0.42), (0.42, 0.4, 0.05), chair_m, "Chair seat"))
                parts.append(box((CX + col + dx, row - 0.33, 0.72), (0.42, 0.04, 0.55), chair_m, "Chair back"))
                parts.append(box((CX + col + dx + random.uniform(-0.1, 0.1), row + 0.38, 0.755), (0.3, 0.22, 0.015),
                                 toon("Notebook", random.choice([(0.95, 0.4, 0.4), (0.4, 0.6, 0.95), (0.95, 0.85, 0.3)])),
                                 "Notebook"))
            for p in parts:
                parent_keep(p, d)
            if col == 2.1 and row == 1.4:
                moving = d
    # ceiling lights (switched off when the power cuts)
    lights = []
    for x in (-2, 2):
        for y in (-2, 2):
            lights.append(box((CX + x, y, 3.18), (1.2, 0.4, 0.04), glow_mat("Panel", (1, 0.98, 0.92), 2.0), "Light panel"))
    bpy.ops.object.light_add(type="AREA", location=(CX, 0, 3.0))
    room_light = bpy.context.object
    room_light.data.energy = 220
    room_light.data.size = 5
    return door_glass, moving, lights, room_light, hands, speaker


def build_yard():
    """Schoolyard below the classroom window, the gate and the street beyond."""
    gz = -5.0
    box((CX - 22, 0, gz - 0.05), (36, 40, 0.1), toon("Yard", (0.68, 0.64, 0.58)), "Yard")
    box((CX - 22, 0, gz + 0.005), (14, 8, 0.01), toon("Court", (0.85, 0.45, 0.35)), "Court")
    for y in (-3.8, 3.8):
        box((CX - 22, y, gz + 0.02), (14, 0.08, 0.01), toon("Court line", (0.98, 0.98, 0.95), 0.4), "Court line")
    box((CX - 3.0, 0, gz / 2), (2, 40, -gz), toon("School facade", (0.98, 0.88, 0.6), 0.15), "Facade")
    sw = toon("Yard wall", (0.92, 0.82, 0.62), 0.15)
    box((CX - 32, -9, gz + 1.2), (0.4, 18, 2.4), sw, "Yard wall")
    box((CX - 32, 11, gz + 1.2), (0.4, 14, 2.4), sw, "Yard wall")
    for k in range(11):
        rod((CX - 32, -1.2 + k * 0.22, gz), (CX - 32, -1.2 + k * 0.22, gz + 2.2), 0.025, toon("Gate", (0.2, 0.35, 0.3)),
            "Gate bar")
    box((CX - 32, 0, gz + 2.2), (0.08, 2.6, 0.08), toon("Gate", (0.2, 0.35, 0.3)), "Gate top")
    box((CX - 40, 0, gz - 0.04), (14, 60, 0.1), toon("Street", (0.25, 0.26, 0.28)), "Street")
    for k in range(6):  # houses across the street
        c = random.choice([(0.95, 0.7, 0.55), (0.75, 0.85, 0.95), (0.95, 0.9, 0.6), (0.95, 0.75, 0.8)])
        h = random.uniform(5, 9)
        box((CX - 50, -15 + k * 6, gz + h / 2), (6, 5.4, h), toon(f"House {c}", c, 0.15), "House")
    for y in (-6, 7):
        rod((CX - 26, y, gz), (CX - 26, y, gz + 2.2), 0.15, toon("Trunk", (0.45, 0.3, 0.2)), "Tree trunk")
        ball((CX - 26, y, gz + 3.2), 1.5, toon("Tree", (0.3, 0.62, 0.3)), "Tree")
    return gz


def build_heli():
    body_m = toon("Heli", (0.3, 0.36, 0.28), 0.15)
    heli = empty("Helicopter", (0, 0, 0))
    parts = [ball((0, 0, 0), 1.3, body_m, "Heli body", scale=(1.0, 1.9, 1.0)),
             ball((0, 1.5, 0.1), 0.9, toon("Heli glass", (0.15, 0.22, 0.28), 0.1), "Heli glass", scale=(1.0, 0.8, 0.8)),
             rod((0, -1.5, 0.3), (0, -5.5, 0.6), 0.25, body_m, "Tail boom"),
             box((0, -5.5, 1.0), (0.1, 0.6, 1.0), body_m, "Tail fin"),
             rod((-0.8, -1.2, -1.4), (-0.8, 1.5, -1.4), 0.06, body_m, "Skid"),
             rod((0.8, -1.2, -1.4), (0.8, 1.5, -1.4), 0.06, body_m, "Skid")]
    for p in parts:
        parent_keep(p, heli)
    rotor = empty("Rotor", (0, 0, 1.45))
    parent_keep(rotor, heli)
    for a in (0, 90):
        b = box((0, 0, 1.45), (0.25, 9.0, 0.05), toon("Rotor", (0.12, 0.12, 0.12)), "Blade")
        b.rotation_euler = (0, 0, D(a))
        parent_keep(b, rotor)
    rotor.rotation_mode = "XYZ"
    bpy.ops.object.light_add(type="SPOT", location=(0, 1.0, -1.0))
    spot = bpy.context.object
    spot.data.spot_size = D(40)
    spot.data.energy = 0
    parent_keep(spot, heli)
    return heli, rotor, spot


def build_stairs_roof():
    wall = toon("Stair wall", (0.55, 0.58, 0.6), 0.08)
    step_m = toon("Stair step", (0.45, 0.45, 0.48), 0.08)
    for k in range(24):
        y = 0.3 * k
        z = 0.2 * (k + 1)
        box((RX + 0.55, y + 0.15, z / 2), (1.3, 0.3, z), step_m, "Step")
    box((RX + 0.55, 7.8, 2.4), (1.3, 0.8, 4.8), step_m, "Top landing")
    box((RX + 1.3, 3.8, 3.0), (0.15, 9, 6.0), wall, "Stair wall")
    box((RX - 1.5, 3.8, 1.0), (0.15, 9, 6.0), wall, "Shaft wall")
    box((RX - 0.5, -0.4, 1.0), (4, 0.15, 6.0), wall, "Stair back")
    rail = toon("Stair rail", (0.75, 0.2, 0.15))
    for k in range(0, 24, 2):
        y = 0.3 * k + 0.15
        z = 0.2 * (k + 1)
        rod((RX - 0.12, y, z), (RX - 0.12, y, z + 0.85), 0.02, rail, "Railing post")
    rod((RX - 0.12, 0.1, 1.1), (RX - 0.12, 7.4, 5.7), 0.035, rail, "Railing")
    box((RX - 0.7, 3.8, -1.6), (1.6, 9, 0.1), toon("Shaft floor", (0.2, 0.2, 0.22)), "Shaft floor")
    bpy.ops.object.light_add(type="POINT", location=(RX + 0.6, 3.5, 3.5))
    emer = bpy.context.object
    emer.data.energy = 40
    emer.data.color = (1.0, 0.35, 0.25)
    # roof
    rz = 4.8
    box((RX, 20, rz - 0.1), (24, 24, 0.2), toon("Roof", (0.6, 0.58, 0.55), 0.12), "Roof")
    box((RX + 0.55, 8.25, rz + 1.2), (2.2, 0.15, 2.4), wall, "Roof hut front")
    for sx in (-1, 1):
        box((RX + 0.55 + sx * 1.1, 8.25, rz + 1.2), (0.15, 0.2, 2.4), wall, "Door frame")
    for sx, sy, w, d in ((0, 32, 24, 0.3), (0, 8.1, 24, 0.3), (-12, 20, 0.3, 24), (12, 20, 0.3, 24)):
        box((RX + sx, sy, rz + 0.45), (w, d, 0.9), toon("Parapet", (0.85, 0.82, 0.75), 0.12), "Parapet")
    for k in range(4):
        box((RX - 8 + k * 5, 26, rz + 0.6), (1.2, 1.2, 1.2), toon("AC unit", (0.75, 0.75, 0.78), 0.12), "AC unit")
    return rz


# ================================================================ main


def build():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.fps = FPS
    scene.frame_start, scene.frame_end = 1, FRAMES

    house_door = build_house()
    truck = build_street()
    door_glass, push_desk, panels, room_light, clock_hands, speaker = build_classroom()
    gz = build_yard()
    heli, rotor, spot = build_heli()
    rz = build_stairs_roof()

    mom, anchor = make_mom(), make_anchor()
    kazemi, arian, mahsa, kian = make_kazemi(), make_arian(), make_mahsa(), make_kian()
    rezaei, rezaei_z = make_rezaei(), make_rezaei(zombie=True)
    soldier, mask, bite = make_soldier()
    zombies = [make_zombie(i) for i in range(7)]
    students = [make_student(i) for i in range(7)]
    seats = [(CX - 2.42, 1.4), (CX - 1.78, -1.4), (CX + 1.78, 1.4), (CX + 2.42, 0.0), (CX - 0.32, -1.4),
             (CX + 0.32, -2.8), (CX + 1.78, -1.4)]

    cam = make_camera(scene)
    arms = POVArms(cam, sleeve_col=(0.22, 0.36, 0.72), cuff_col=(0.97, 0.97, 0.97))
    phone = empty("Phone")
    parent_local(phone, cam)
    pbody = box((0, 0, 0), (0.08, 0.16, 0.012), toon("Phone case", (0.15, 0.15, 0.18), 0.2), "Phone body", bevel=0.008)
    parent_keep(pbody, phone)
    screens = {}
    for key in ("voice", "failed"):
        sc_ = plane((0, 0, 0.0065), (0.07, 0.145), (0, 0, 0), image_mat(f"Screen {key}", os.path.join(TEX, f"phone_{key}.png")),
                    f"Screen {key}")
        parent_keep(sc_, phone)
        screens[key] = sc_
    phone.rotation_mode = "XYZ"
    sun = None

    rnd = random.Random(4)
    shake = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(-1, 1)) for _ in range(FRAMES + 3)]
    POV_SEAT = Vector((CX - 0.32, -0.15, 1.08))
    far = Vector((-500, -500, -50))

    for f in range(1, FRAMES + 1):
        t = (f - 1) / FPS
        yaw, pitch, roll, amp = 180.0, 0.0, 0.0, 0.25
        hand_l, hand_r = (-0.28, -0.45, -0.46), (0.28, -0.45, -0.46)
        phone_on, phone_screen = False, "voice"

        # ============ HOUSE 0-11 s
        if t < 11.0:
            if t < 6.0:
                u = seg(t, 3.0, 6.0)
                pos = Vector((HX - 3.3, lerp(3.9, -0.5, u), lerp(4.3, 1.5, u)))
                pos.z += 0.05 * abs(math.sin(math.pi * t * 2.4)) * (0 < u < 1)
                pitch = lerp(-22, -10, u)
                hand_l = (-0.32, -0.42, -0.5)
                hand_r = (0.3, -0.36 + 0.03 * math.sin(t * 6), -0.55)  # on the handrail
            else:
                u = seg(t, 6.0, 9.4)
                pa, pb, pc = Vector((HX - 3.3, -0.5, 1.5)), Vector((HX + 0.9, -1.9, 1.5)), Vector((HX + 1.9, -3.6, 1.5))
                pos = pa.lerp(pb, min(1, u * 1.6)) if u < 0.625 else pb.lerp(pc, (u - 0.625) / 0.375)
                pos.z += 0.04 * abs(math.sin(math.pi * t * 2.2))
                yaw = lerp(215, 205, seg(t, 6, 8.5))
                pitch = -8
                yaw = lerp(yaw, 35, seg(t, 9.0, 9.5) * (1 - seg(t, 10.0, 10.4)))
                if t > 10.4:
                    pos = pos.lerp(Vector((HX + 2.0, -4.9, 1.5)), seg(t, 10.5, 11.0))
            house_door.rotation_euler = (0, 0, D(-100) * seg(t, 10.3, 10.8))
            house_door.keyframe_insert("rotation_euler", frame=f)
        # ============ STREET 11-15 s
        elif t < 15.0:
            u = (t - 11.0) / 4.0
            pos = Vector((SX + 1.1, lerp(3.0, 16.6, u), 1.5 + 0.04 * abs(math.sin(math.pi * t * 2.4))))
            yaw = lerp(0, -45, seg(t, 11.5, 11.9) * (1 - seg(t, 12.6, 13.0)))
            pitch = -4
            hand_r = (0.3, -0.5 + 0.04 * math.sin(t * 7), -0.4)
            hand_l = (-0.3, -0.5 - 0.04 * math.sin(t * 7), -0.4)
        # ============ CLASSROOM 15-63 s
        elif t < 63.0:
            pos = POV_SEAT.copy()
            yaw, pitch = 0, 2
            hand_l, hand_r = (-0.18, -0.36, -0.5), (0.2, -0.38, -0.48)
            yaw = lerp(yaw, -60, seg(t, 17.1, 17.4) * (1 - seg(t, 18.5, 18.8)))
            if 21.0 <= t < 28.0:  # phone under the desk
                pitch = lerp(2, -50, seg(t, 21.0, 21.5)) if t < 27.6 else lerp(-50, 2, seg(t, 27.6, 28.0))
                phone_on, phone_screen = True, ("voice" if t < 25.6 else "failed")
                hand_r = (0.08, -0.33, -0.44)
                hand_l = (-0.22, -0.42, -0.46)
            if 28.0 <= t < 33.0:  # show it to Arian, laugh
                yaw = lerp(0, -55, seg(t, 28.0, 28.4)) if t < 31.3 else lerp(-55, 0, seg(t, 31.3, 31.7))
                pitch = -12 if t < 31.3 else 2
                phone_on, phone_screen = t < 31.3, "failed"
                hand_r = (0.22, -0.3, -0.42)
                pos = pos + Vector((0, 0, 0.03 * math.sin(t * 20) * (29.0 < t < 31.0)))  # laughing
            if 33.0 <= t < 39.0:  # loudspeaker
                yaw = lerp(0, -18, seg(t, 33.3, 33.7))
                pitch = lerp(2, 20, seg(t, 33.3, 33.7))
                yaw = lerp(yaw, 30, seg(t, 37.8, 38.3))
                pitch = lerp(pitch, 14, seg(t, 37.8, 38.3))
            if 39.0 <= t < 45.0:  # at the window, looking down at the yard
                u = seg(t, 39.0, 39.9)
                pos = POV_SEAT.lerp(Vector((CX - 3.35, 0.0, 1.55)), u)
                yaw = lerp(30, 90, u)
                pitch = lerp(14, -38, u)
                amp = 0.4
            if 45.0 <= t < 51.0:  # door: zombie behind the glass, push a desk against it
                u = seg(t, 45.0, 46.2)
                pos = Vector((CX - 3.35, 0.0, 1.55)).lerp(Vector((CX + 1.6, 1.0, 1.5)), u)
                yaw = lerp(90, -60, seg(t, 45.0, 45.6))
                pitch = lerp(-38, 4, seg(t, 45.0, 45.6))
                if t > 47.4:
                    d = push_desk.location
                    pos = Vector((d.x - 0.75, d.y - 0.75, 1.45))
                    pitch = -24
                    hand_l, hand_r = (-0.2, -0.38, -0.5), (0.2, -0.38, -0.5)
                amp = 0.5
            if 51.0 <= t < 57.0:  # dark: Kian in the corner, no signal
                pos = Vector((CX + 2.3, 1.7, 1.5)).lerp(Vector((CX - 1.6, -2.0, 1.3)), seg(t, 51.0, 52.4))
                yaw = lerp(-60, 135, seg(t, 51.0, 52.4))
                pitch = lerp(4, -24, seg(t, 51.0, 52.4))
                if t > 54.8:
                    pitch = lerp(-24, -50, seg(t, 54.8, 55.1))
                    phone_on, phone_screen = True, "failed"
                    hand_r = (0.08, -0.33, -0.44)
            if 57.0 <= t < 63.0:  # helicopter at the window
                pos = Vector((CX - 1.6, -2.0, 1.3)).lerp(Vector((CX - 2.6, -0.4, 1.5)), seg(t, 57.0, 57.8))
                yaw = lerp(135, 92, seg(t, 57.2, 57.8))
                pitch = lerp(-24, 8, seg(t, 57.2, 57.8))
                yaw = lerp(yaw, 20, seg(t, 61.6, 62.0))
                pitch = lerp(pitch, 0, seg(t, 61.6, 62.0))
                amp = 0.5
        # ============ STAIRS 63-69 s, ROOF 69-75 s
        elif t < 69.0:
            u = (t - 63.0) / 6.0
            y = lerp(0.2, 7.6, u)
            pos = Vector((RX + 0.55, y, 0.2 * (y / 0.3) + 1.45 + 0.06 * abs(math.sin(math.pi * t * 3.2))))
            yaw, pitch = 0, 14
            yaw = lerp(yaw, 165, seg(t, 64.0, 64.4) * (1 - seg(t, 65.4, 65.8)))
            pitch = lerp(pitch, -25, seg(t, 64.0, 64.4) * (1 - seg(t, 65.4, 65.8)))
            amp = 1.0
            hand_l = (-0.3, -0.45 + 0.05 * math.sin(t * 9), -0.45)
        else:
            u = seg(t, 69.0, 70.4)
            pos = Vector((RX + 0.55, lerp(7.9, 9.3, u), rz + 1.35))
            yaw, pitch = 0, lerp(4, 0, u)
            amp = 0.8
            if t > 71.8:  # look at the wrist, then up at the face
                pos = pos + Vector((0, 0.25, -0.1)) * seg(t, 71.8, 72.4)
                pitch = lerp(0, -32, seg(t, 71.8, 72.4))
                pitch = lerp(pitch, 12, seg(t, 73.0, 73.6))
                amp = 0.2

        sx_, sy_, sz_ = shake[f]
        for te, k in ((37.2, 2.0), (43.4, 1.5), (45.6, 3.0), (51.0, 1.0), (73.0, 1.5)):
            if te <= t < te + 0.6:
                amp += k * (1 - (t - te) / 0.6)
        cam.location = pos
        cam.rotation_euler = (D(90 + pitch + sx_ * amp), D(roll + sy_ * amp * 0.6), D(yaw + sz_ * amp))
        cam.keyframe_insert("location", frame=f)
        cam.keyframe_insert("rotation_euler", frame=f)

        # ---------------- people
        # home
        mom.pose(f, t, Vector((HX - 0.6, -0.65, 0)), facing=180, sit=1, seat_h=0.48,
                 look=(lerp(0, -70, seg(t, 9.9, 10.2)), -5), reach=(55, 0), worry=1.4, lean=0)
        anchor.pose(f, t, Vector((HX - 0.6, -4.27, 1.0)), facing=0, look=(0, 0), worry=0.8)
        # street
        rezaei.pose(f, t, Vector((SX + 0.9, 17.4, 0)), facing=180, look=(0, 5),
                    wave=seg(t, 13.5, 13.7) * (1 - seg(t, 14.8, 15.0)))
        truck.location = (SX + 4.5, lerp(-25, 60, seg(t, 11.2, 13.4)), 0)
        truck.keyframe_insert("location", frame=f)

        # class + stairs + roof: the kids and the teacher
        if t < 63.0:
            # teacher at the board
            writing = t < 15.4 or (16.9 < t < 18.6)
            k_pos = Vector((CX + 0.6, 3.55, 0))
            k_face = 0 if writing else 180
            k_reach = (160, -10) if writing else None
            if 45.0 <= t < 51.0:
                k_pos = Vector((CX + 2.6, 2.3, 0))
                k_face, k_reach = -60, (90, 10)
            if 51.0 <= t < 57.0:
                k_pos, k_face, k_reach = Vector((CX + 1.0, 2.0, 0)), 150, None
            if 57.0 <= t < 63.0:
                k_pos, k_face, k_reach = Vector((CX + 2.8, 2.6, 0)), 135, ((150, 20) if t > 61.6 else None)
            kazemi.pose(f, t, k_pos, facing=k_face, reach=k_reach, look=(0, 3), lean=0,
                        worry=0.9 if t < 33 else 1.6, wave=seg(t, 61.7, 61.9) if t > 61.6 else 0)
            # Arian next to me
            a_sit = 1.0 if t < 39.0 else 0.0
            a_pos = Vector((CX + 0.32, -0.15, 0))
            a_look = (lerp(0, 60, seg(t, 17.0, 17.3) * (1 - seg(t, 18.6, 18.9))), 0)
            if 28.0 <= t < 33.0:
                a_look = (65, -10)
            if 39.0 <= t < 45.0:
                a_pos, a_look = Vector((CX - 3.3, -0.9, 0)), (0, -30)
            if 45.0 <= t < 51.0:
                a_pos = Vector((CX + 2.2, 2.0, 0)) if t < 47.4 else push_desk.location + Vector((0.35, -0.75, -0.0))
                a_pos.z = 0
                a_look = (0, 0)
            if 51.0 <= t < 57.0:
                a_pos, a_look = Vector((CX + 0.5, -1.0, 0)), (40, 0)
            if 57.0 <= t < 63.0:
                a_pos, a_look = Vector((CX - 3.3, -1.1, 0)), (-90, 10)
            arian.pose(f, t, a_pos, facing=0 if t < 39 else (90 if 39 <= t < 45 or 57 <= t < 63 else -45 if t < 51 else 150),
                       sit=a_sit, seat_h=0.42, look=a_look, lean=0, worry=0.8 if t < 33 else 1.5,
                       reach=(90, 0) if 47.4 < t < 51 else ((160, -20) if t > 60.2 else None),
                       reach2=(90, 0) if 47.4 < t < 51 else ((160, 20) if t > 60.2 else None))
            # Mahsa (front left) and Kian (by the window)
            m_pos, m_face, m_sit = Vector((CX - 1.78, 1.25, 0)), 0, 1.0
            if 39.0 <= t < 51.0:
                m_pos, m_face, m_sit = Vector((CX - 3.25, 0.85, 0)), 100, 0.0
            if t >= 51.0:
                m_pos, m_face, m_sit = Vector((CX - 0.8, -1.0, 0)), 160, 0.0
            mahsa.pose(f, t, m_pos, facing=m_face, sit=m_sit, seat_h=0.42, look=(lerp(0, 150, seg(t, 28.5, 29) * (
                1 - seg(t, 31, 31.4))) if t < 33 else 0, -25 if 39 <= t < 45 else 0), lean=0,
                worry=1.6 if t > 33 else 0.6)
            kc = seg(t, 51.0, 51.6)
            k_pos2 = Vector((CX - 2.42, -0.15, 0)) if t < 39 else Vector((CX - 3.25, -0.75, 0))
            if t >= 51.0:
                k_pos2 = Vector((CX - 3.3, -3.9, 0))
            kian.pose(f, t, k_pos2, facing=0 if t < 39 else (95 if t < 51 else 45), sit=1.0 if t < 39 else 0.0, seat_h=0.42,
                      crouch=kc, hug=kc, look=(0, -30 if 39 <= t < 45 else 10), lean=0, worry=1.8 if t > 33 else 1.0)
            for i, s in enumerate(students):
                sx, sy = seats[i]
                hide = t >= 39.0
                cower = seg(t, 37.5, 38.2)
                pos_s = Vector((sx, sy - 0.15, 0)) if not hide else Vector((CX - 1.0 + 0.5 * i, -3.6 + 0.15 * (i % 2), 0))
                s.pose(f, t, pos_s, facing=0 if not hide else 160, sit=0 if hide else 1, seat_h=0.42,
                       crouch=0.6 if hide else 0, look=((20 * math.sin(i + t * 0.3)) if t < 33 else (-15, 25)[i % 2], 0),
                       lean=0, worry=1.6 if t > 33 else 0.7, hug=cower if not hide else 0.5)
        else:
            # stairs: teacher, Mahsa, Arian ahead; Kian behind holding my hand
            y_me = lerp(0.2, 7.6, min(1, (t - 63.0) / 6.0))
            if t < 69.0:
                for p, dy, dx in ((kazemi, 2.4, 0.2), (mahsa, 1.6, -0.0), (arian, 0.9, 0.3)):
                    yy = min(7.7, y_me + dy)
                    p.pose(f, t, Vector((RX + 0.55 + dx, yy, 0.2 * (yy / 0.3))), facing=0, run=1, run_rate=1.7,
                           lean=-18, worry=1.8)
                yk = max(0.0, y_me - 0.9)
                kian.pose(f, t, Vector((RX + 0.6, yk, 0.2 * (yk / 0.3))), facing=0, run=1, run_rate=2.0, lean=-15,
                          reach=(70, 15), look=(0, 15), worry=2.0)
            else:
                v = seg(t, 69.0, 72.0)
                for p, x0, y0 in ((kazemi, -1.5, 13.0), (mahsa, -0.6, 12.0), (arian, 0.6, 12.5), (kian, -0.2, 9.9)):
                    p.pose(f, t, Vector((RX + x0, y0 + (3.0 * v if p is not kian else 0.4 * v), rz)), facing=0,
                           run=1 if p is not kian else 0.3, run_rate=1.6, lean=-12, worry=1.8,
                           look=(0, 0) if p is not kian else (0, 20))
        # rezaei the zombie, in the yard below the window
        turn = seg(t, 42.9, 43.4)
        rezaei_z.pose(f, t, Vector((CX - 28.5, 0.4, gz)), facing=lerp(90, -90, turn), look=(0, lerp(0, 35, turn)),
                      reach=(lerp(60, 85, turn), 5), reach2=(lerp(60, 85, turn), -5), worry=0.0, lean=0)
        # zombies at the gate / behind the door / under the stair railing
        for i, z in enumerate(zombies):
            wob = 6 * math.sin(t * 2.2 + i)
            if i < 5:  # pushing the yard gate
                zp = Vector((CX - 33.0 - 0.3 * (i % 2), -1.6 + i * 0.8, gz))
                z.pose(f, t, zp, facing=-90 + wob, reach=(85 + wob, 5), reach2=(80 - wob, -5),
                       look=(0, 10 + wob), worry=0.0, lean=0)
            elif i == 5:  # corridor, then at the stairs
                if t < 63.0:
                    appear = seg(t, 44.8, 45.2)
                    zp = Vector((CX + 4.6 - 0.15 * appear, 3.0, 0))
                    z.pose(f, t, zp, facing=90, reach=(100 + 15 * math.sin(t * 9), 0), reach2=(95, 0),
                           look=(0, 0), worry=0.0, lean=0, z=-2.0 * (1 - appear))
                else:
                    z.pose(f, t, Vector((RX - 0.65, 2.0 + 0.4 * math.sin(t), -0.2 + 0.4 * (t - 63))),
                           facing=90, reach=(170, 10), reach2=(165, -10), look=(0, 40), worry=0.0, lean=0)
            else:
                z.pose(f, t, Vector((RX - 0.7, 4.0, 0.8 + 0.3 * math.sin(t))), facing=90, reach=(170, -10),
                       reach2=(160, 10), look=(0, 40), worry=0.0, lean=0)
        # soldier on the roof
        sp = Vector((RX + 0.35, 10.3, rz))
        soldier.pose(f, t, sp, facing=180, reach=(lerp(60, 95, seg(t, 69.8, 70.3)), 10), look=(0, -8 + 12 * seg(t, 73, 73.4)),
                     worry=0.0, lean=0)
        for o in mask:
            show(o, f, t < 72.9)

        # ---------------- devices, lights, helicopter, clock
        rotor.rotation_euler = (0, 0, t * 28.0)
        rotor.keyframe_insert("rotation_euler", frame=f)
        if t < 63.0:
            hp = Vector((CX - 30, 40, 10)).lerp(Vector((CX - 9.0, -1.0, 2.0)), seg(t, 56.8, 59.0))
            heli.rotation_euler = (D(-6), D(4 * math.sin(t)), D(lerp(160, 90, seg(t, 56.8, 59.0))))
        else:
            hp = Vector((RX + 0.5, 19.0, rz + 1.6 + 0.15 * math.sin(t * 2)))
            heli.rotation_euler = (0, 0, D(180))
        heli.location = hp
        heli.keyframe_insert("location", frame=f)
        heli.keyframe_insert("rotation_euler", frame=f)
        spot.data.energy = 3000 * seg(t, 57.5, 58.5) if t < 63 else 0
        spot.data.keyframe_insert("energy", frame=f)
        lit = not (51.0 <= t < 63.0)
        for o in panels:
            show(o, f, lit)
        room_light.data.energy = 220 if lit else 0
        room_light.data.keyframe_insert("energy", frame=f)
        show(door_glass, f, t < 45.6)
        push_desk.location = Vector((CX + 2.1, 1.75, 0)).lerp(Vector((CX + 3.25, 3.0, 0)), seg(t, 47.5, 50.5))
        push_desk.keyframe_insert("location", frame=f)
        clock_hands[0].rotation_euler = (0, D(90 + t * 6), 0)
        clock_hands[1].rotation_euler = (0, D(200 + t * 0.5), 0)
        for h in clock_hands:
            h.keyframe_insert("rotation_euler", frame=f)

        show(phone, f, phone_on)
        show(screens["voice"], f, phone_screen == "voice")
        show(screens["failed"], f, phone_screen == "failed")
        phone.location = (0.06, -0.21, -0.46) if not (28.0 <= t < 33.0) else (0.2, -0.16, -0.42)
        phone.rotation_euler = (D(-25), 0, D(-4) if not (28.0 <= t < 33.0) else D(-35))
        phone.keyframe_insert("location", frame=f)
        phone.keyframe_insert("rotation_euler", frame=f)

        # ---------------- POV hands
        if 63.0 <= t < 69.0:
            hand_r = world_to_cam(cam, kian.hand_world("R"))
        if 70.6 <= t < 72.9:
            hand_r = world_to_cam(cam, soldier.hand_world("R"))
        if phone_on:
            hand_r = (0.1, -0.33, -0.45) if not (28.0 <= t < 33.0) else (0.24, -0.27, -0.42)
        arms.set(f, "L", hand_l)
        arms.set(f, "R", hand_r)

    bpy.ops.object.light_add(type="SUN", rotation=(D(55), D(20), D(-40)))
    sun = bpy.context.object
    sun.data.color = (1.0, 0.93, 0.82)
    sun.data.angle = D(3)
    for fr, e in ((1, 2.6), (FPS * 50 + 1, 2.6), (FPS * 51 + 1, 0.9), (FPS * 63 + 1, 0.9), (FPS * 63 + 2, 1.6)):
        sun.data.energy = e
        sun.data.keyframe_insert("energy", frame=fr)
    setup_render(scene, sky=(0.75, 0.82, 0.9), sky_strength=0.85)
    bg = scene.world.node_tree.nodes["Background"]
    for fr, c, s in ((1, (0.75, 0.82, 0.9), 0.85), (FPS * 51 + 1, (0.6, 0.62, 0.66), 0.35), (FPS * 63 + 1, (0.6, 0.62, 0.66), 0.35),
                     (FPS * 63 + 2, (0.62, 0.65, 0.7), 0.6)):
        bg.inputs["Color"].default_value = (*c, 1)
        bg.inputs["Strength"].default_value = s
        bg.inputs["Color"].keyframe_insert("default_value", frame=fr)
        bg.inputs["Strength"].keyframe_insert("default_value", frame=fr)
    scene.frame_set(1)
    return scene


if __name__ == "__main__":
    run_cli(build(), "school_pov.blend")
