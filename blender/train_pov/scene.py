"""
«واگن آخر» — sequence 1+2 (platform run + jump onto the moving train).

First-person POV, cartoon 3D: puppet-like characters with round heads, hinged
jaws for talking, toon shading and black Freestyle outlines.  The viewer's
green sleeves are visible at the bottom of the frame.

Run in Blender (Scripting tab -> Run Script) or headless:
    blender -b --python scene.py -- --save            # write train_pov.blend
    blender -b --python scene.py -- --still 100       # one test frame
    blender -b --python scene.py -- --render          # all frames -> frames/
Captions, fade and the fisheye look are added afterwards by post.py.
"""

import math
import os
import random
import sys

import bpy
from mathutils import Euler, Matrix, Vector

FPS = 24
SECONDS = 14
FRAMES = FPS * SECONDS
random.seed(3)
D = math.radians

# ================================================================ timing


def ease(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def seg(t, a, b):
    """0 before a, eased 0..1 between a and b, 1 after b."""
    return ease((t - a) / (b - a))


def lerp(a, b, u):
    return a + (b - a) * u


def train_offset(t):
    return 2.6 * t + 0.06 * t * t


def door_y(t):
    return 8.0 + train_offset(t)


# who talks when (seconds) -> used for jaw animation; captions live in post.py
TALK = {
    "Mom": [(3.6, 5.0)],
    "Lena": [(5.1, 6.4)],
    "Rahim": [(8.0, 9.4), (12.9, 14.0)],
}

# ================================================================ materials

_mats = {}


def toon(name, color, glow=0.28):
    """Flat cartoon material: toon diffuse + a little self light."""
    key = (name, color)
    if key in _mats:
        return _mats[key]
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    t = nt.nodes.new("ShaderNodeBsdfToon")
    t.inputs["Color"].default_value = (*color, 1)
    t.inputs["Size"].default_value = 0.6
    t.inputs["Smooth"].default_value = 0.04
    e = nt.nodes.new("ShaderNodeEmission")
    e.inputs["Color"].default_value = (*color, 1)
    e.inputs["Strength"].default_value = glow
    add = nt.nodes.new("ShaderNodeAddShader")
    nt.links.new(t.outputs[0], add.inputs[0])
    nt.links.new(e.outputs[0], add.inputs[1])
    nt.links.new(add.outputs[0], out.inputs["Surface"])
    _mats[key] = m
    return m


def glow_mat(name, color, strength):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    e = nt.nodes.new("ShaderNodeEmission")
    e.inputs["Color"].default_value = (*color, 1)
    e.inputs["Strength"].default_value = strength
    nt.links.new(e.outputs[0], out.inputs["Surface"])
    return m


def glass_mat():
    if "glass" in _mats:
        return _mats["glass"]
    m = bpy.data.materials.new("Roof glass")
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    tr.inputs[0].default_value = (0.8, 0.88, 0.92, 1)
    e = nt.nodes.new("ShaderNodeEmission")
    e.inputs["Color"].default_value = (0.7, 0.8, 0.85, 1)
    e.inputs["Strength"].default_value = 0.15
    add = nt.nodes.new("ShaderNodeAddShader")
    nt.links.new(tr.outputs[0], add.inputs[0])
    nt.links.new(e.outputs[0], add.inputs[1])
    nt.links.new(add.outputs[0], out.inputs["Surface"])
    _mats["glass"] = m
    return m


# ================================================================ primitives


def _finish(o, m, name, smooth=False):
    o.name = name
    o.data.materials.append(m)
    if smooth:
        for p in o.data.polygons:
            p.use_smooth = True
    return o


def box(loc, size, m, name="Box", bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object
    o.scale = size
    bpy.ops.object.transform_apply(scale=True)
    if bevel:
        b = o.modifiers.new("Bevel", "BEVEL")
        b.width = bevel
        b.segments = 2
    return _finish(o, m, name)


def ball(loc, r, m, name="Ball", scale=(1, 1, 1), seg=20):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=loc, segments=seg, ring_count=max(8, seg // 2))
    o = bpy.context.object
    o.scale = scale
    bpy.ops.object.transform_apply(scale=True)
    return _finish(o, m, name, smooth=True)


def rod(a, b, r, m, name="Rod", verts=16):
    a, b = Vector(a), Vector(b)
    d = b - a
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=d.length, location=(a + b) / 2, vertices=verts)
    o = bpy.context.object
    o.rotation_mode = "QUATERNION"
    o.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(d)
    return _finish(o, m, name, smooth=True)


def place_rod(o, a, b):
    a, b = Vector(a), Vector(b)
    o.location = (a + b) / 2
    o.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(b - a)


def empty(name, loc=(0, 0, 0)):
    o = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(o)
    o.location = loc
    o.empty_display_size = 0.1
    return o


def parent_keep(child, parent):
    bpy.context.view_layer.update()
    mw = child.matrix_world.copy()
    child.parent = parent
    child.matrix_parent_inverse = parent.matrix_world.inverted()
    child.matrix_world = mw


def parent_local(child, parent):
    child.parent = parent
    child.matrix_parent_inverse = Matrix.Identity(4)


# ================================================================ characters


class Person:
    """Puppet-like character built at the origin facing +Y, then driven by root."""

    def __init__(self, name, s, head_r, skin, top, pants, shoes, sleeve=None):
        self.name = name
        self.s = s
        self.R = head_r
        self.p = {}
        sleeve = sleeve or top
        self.m_skin = toon(f"{name} skin", skin)
        m_top, m_pants, m_shoes = toon(f"{name} top", top), toon(f"{name} pants", pants), toon(f"{name} shoes", shoes)
        m_sleeve = toon(f"{name} sleeve", sleeve)
        m_white, m_black = toon("Eye white", (0.98, 0.98, 0.96), 0.6), toon("Ink", (0.03, 0.03, 0.03), 0.0)
        m_mouth = toon("Mouth inside", (0.25, 0.04, 0.05), 0.1)

        hip_z = 0.86 * s
        sh_z = hip_z + 0.55 * s
        neck_z = sh_z + 0.05 * s
        hc = Vector((0, 0, neck_z + head_r * 1.05))
        self.head_c = hc
        limb = 0.065 * s ** 0.5

        root = self.p["root"] = empty(f"{name}")
        hips = self.pivot("hips", (0, 0, hip_z), root)
        torso = self.pivot("torso", (0, 0, hip_z), hips)
        self.add(box((0, 0, hip_z + 0.29 * s), (0.42 * s, 0.26 * s, 0.6 * s), m_top, "torso", bevel=0.06 * s), torso)
        self.add(ball((0, 0, hip_z + 0.02 * s), 0.2 * s, m_pants, "pelvis", scale=(1.1, 0.75, 0.6)), hips)

        neck = self.pivot("neck", (0, 0, neck_z), torso)
        self.add(rod((0, 0, sh_z - 0.02), (0, 0, neck_z + 0.08 * s), 0.055 * s, self.m_skin, "neck"), neck)
        head = self.pivot("head", tuple(hc), neck)
        self.add(ball(hc, head_r, self.m_skin, "head", scale=(1.0, 0.95, 1.06), seg=28), head)
        # eyes
        for side, sx in (("L", -1), ("R", 1)):
            ec = hc + Vector((sx * 0.38 * head_r, 0.8 * head_r, 0.12 * head_r))
            self.add(ball(ec, 0.27 * head_r, m_white, f"eye {side}", scale=(1, 0.55, 1.15)), head)
            self.p[f"pupil{side}"] = self.add(
                ball(ec + Vector((0, 0.15 * head_r, -0.02 * head_r)), 0.11 * head_r, m_black, f"pupil {side}",
                     scale=(1, 0.6, 1.25), seg=12), head)
            self.p[f"brow{side}"] = self.add(
                box(ec + Vector((0, 0.07 * head_r, 0.36 * head_r)), (0.34 * head_r, 0.06 * head_r, 0.07 * head_r),
                    m_black, f"brow {side}"), head)
        self.add(ball(hc + Vector((0, 0.98 * head_r, -0.12 * head_r)), 0.17 * head_r, self.m_skin, "nose",
                      scale=(1, 0.9, 0.85), seg=14), head)
        # puppet mouth: dark inside + hinged jaw
        self.add(ball(hc + Vector((0, 0.7 * head_r, -0.5 * head_r)), 0.3 * head_r, m_mouth, "mouth inside",
                      scale=(1.25, 0.6, 0.55), seg=14), head)
        jaw = self.pivot("jaw", tuple(hc + Vector((0, 0.1 * head_r, -0.42 * head_r))), head)
        self.add(ball(hc + Vector((0, 0.38 * head_r, -0.66 * head_r)), 0.52 * head_r, self.m_skin, "jaw",
                      scale=(1.3, 1.15, 0.6), seg=20), jaw)

        for side, sx in (("L", -1), ("R", 1)):
            shp = Vector((sx * 0.27 * s, 0, sh_z - 0.04 * s))
            sh = self.pivot(f"shoulder{side}", tuple(shp), torso)
            self.add(ball(shp, limb * 1.5, m_top, f"shoulder ball {side}"), sh)
            elp = shp + Vector((0, 0, -0.29 * s))
            self.add(rod(shp, elp, limb, m_sleeve, f"upper arm {side}"), sh)
            el = self.pivot(f"elbow{side}", tuple(elp), sh)
            self.add(ball(elp, limb * 1.1, m_sleeve, f"elbow {side}", seg=12), el)
            hp = elp + Vector((0, 0, -0.26 * s))
            self.add(rod(elp, hp, limb * 0.95, m_sleeve, f"forearm {side}"), el)
            self.p[f"hand{side}"] = self.add(ball(hp + Vector((0, 0, -0.04 * s)), limb * 1.35, self.m_skin,
                                                  f"hand {side}", scale=(0.9, 0.8, 1.15), seg=14), el)

            hpp = Vector((sx * 0.11 * s, 0, hip_z))
            th = self.pivot(f"thigh{side}", tuple(hpp), hips)
            kp = hpp + Vector((0, 0, -0.42 * s))
            self.add(rod(hpp, kp, limb * 1.25, m_pants, f"thigh {side}"), th)
            kn = self.pivot(f"knee{side}", tuple(kp), th)
            self.add(ball(kp, limb * 1.3, m_pants, f"knee {side}", seg=12), kn)
            ap = kp + Vector((0, 0, -0.38 * s))
            self.add(rod(kp, ap, limb * 1.1, m_pants, f"shin {side}"), kn)
            self.add(box(ap + Vector((0, 0.06 * s, -0.04 * s)), (0.14 * s, 0.28 * s, 0.1 * s), m_shoes,
                         f"shoe {side}", bevel=0.03 * s), kn)

        for o in self.p.values():
            o.rotation_mode = "XYZ"

    def pivot(self, key, loc, parent):
        e = empty(f"{self.name} {key}", loc)
        parent_keep(e, parent)
        self.p[key] = e
        return e

    def add(self, obj, parent):
        obj.name = f"{self.name} {obj.name}"
        parent_keep(obj, parent)
        return obj

    # --------------------------------------------------- posing

    def pose(self, f, t, pos, facing, run=0.0, run_rate=1.5, lean=-12, look=(0, 0), talk=False,
             reach=None, reach2=None, worry=1.0, z=0.0, crouch=0.0):
        """Set every pivot for this frame and keyframe it.

        facing: yaw in degrees (0 = +Y).  look: (yaw, pitch) of the head.
        reach / reach2: (shoulder X, shoulder Z) degrees for the right / left arm.
        """
        p = self.p
        ph = 2 * math.pi * t * run_rate + sum(map(ord, self.name)) % 7
        a = D(38) * run
        p["root"].location = (pos[0], pos[1], pos[2] + z)
        p["root"].rotation_euler = (0, 0, D(facing))
        p["hips"].location = (0, 0, 0.86 * self.s + 0.05 * self.s * abs(math.sin(ph)) * run - 0.25 * self.s * crouch)
        p["torso"].rotation_euler = (D(lean) * run + D(-20) * crouch, 0, D(6) * math.sin(ph) * run)
        for side, sgn in (("L", 1), ("R", -1)):
            sw = sgn * math.sin(ph)
            p[f"thigh{side}"].rotation_euler = (a * sw + D(50) * crouch, 0, 0)
            p[f"knee{side}"].rotation_euler = (-D(15 + 60 * max(0.0, -sw)) * run - D(80) * crouch, 0, 0)
            p[f"shoulder{side}"].rotation_euler = (-a * 0.9 * sw, 0, sgn * D(-8))
            p[f"elbow{side}"].rotation_euler = (D(75) * run + D(15), 0, 0)
        if reach is not None:
            p["shoulderR"].rotation_euler = (D(reach[0]), 0, D(reach[1]))
            p["elbowR"].rotation_euler = (D(10), 0, 0)
        if reach2 is not None:
            p["shoulderL"].rotation_euler = (D(reach2[0]), 0, D(reach2[1]))
            p["elbowL"].rotation_euler = (D(10), 0, 0)
        p["neck"].rotation_euler = (D(look[1]) * 0.4, 0, D(look[0]) * 0.4)
        p["head"].rotation_euler = (D(look[1]) * 0.6, 0, D(look[0]) * 0.6)
        jaw = 0.0
        if talk:
            jaw = 0.5 + 0.5 * math.sin(2 * math.pi * t * 5.5)
        p["jaw"].rotation_euler = (-D(4) - D(24) * jaw, 0, 0)
        for side, sgn in (("L", -1), ("R", 1)):
            p[f"brow{side}"].rotation_euler = (0, D(18) * worry * sgn, 0)
        for k in ("root",):
            p[k].keyframe_insert("location", frame=f)
            p[k].keyframe_insert("rotation_euler", frame=f)
        p["hips"].keyframe_insert("location", frame=f)
        for k, o in p.items():
            if isinstance(o, bpy.types.Object) and o.type == "EMPTY" and k not in ("root",):
                o.keyframe_insert("rotation_euler", frame=f)
        for side in ("L", "R"):
            p[f"brow{side}"].keyframe_insert("rotation_euler", frame=f)

    def hand_world(self, side):
        bpy.context.view_layer.update()
        return self.p[f"hand{side}"].matrix_world.translation.copy()


def talking(name, t):
    return any(a <= t <= b for a, b in TALK.get(name, []))


def dress_lena(lena):
    R, hc = lena.R, lena.head_c
    hair = toon("Lena hair", (0.22, 0.13, 0.08))
    hat = toon("Lena beanie", (0.82, 0.16, 0.14))
    head = lena.p["head"]
    lena.add(ball(hc + Vector((0, -0.12 * R, 0.1 * R)), 1.04 * R, hair, "hair", scale=(1, 0.95, 1.0)), head)
    for sx in (-1, 1):
        lena.add(ball(hc + Vector((sx * 1.0 * R, -0.25 * R, -0.25 * R)), 0.38 * R, hair, "pigtail",
                      scale=(0.8, 0.8, 1.3)), head)
    lena.add(ball(hc + Vector((0, -0.05 * R, 0.38 * R)), 1.1 * R, hat, "beanie", scale=(1, 1, 0.72)), head)
    bpy.ops.mesh.primitive_torus_add(location=hc + Vector((0, -0.02 * R, 0.28 * R)), major_radius=1.02 * R,
                                     minor_radius=0.14 * R, major_segments=32, minor_segments=8)
    rim = _finish(bpy.context.object, toon("Beanie rim", (0.95, 0.92, 0.85)), "beanie rim", smooth=True)
    rim.rotation_euler = (D(-12), 0, 0)
    lena.add(rim, head)
    lena.add(ball(hc + Vector((0, 0, 1.25 * R)), 0.28 * R, toon("Beanie rim", (0.95, 0.92, 0.85)), "pompom"), head)
    # bunny plush in the right hand
    white = toon("Bunny", (0.95, 0.93, 0.92))
    hp = lena.p["handR"].matrix_world.translation
    b = lena.add(ball(hp + Vector((0.02, 0.06, -0.12)), 0.08, white, "bunny body"), lena.p["elbowR"])
    lena.add(ball(hp + Vector((0.02, 0.06, 0.0)), 0.06, white, "bunny head"), lena.p["elbowR"])
    for ex in (-0.025, 0.025):
        lena.add(ball(hp + Vector((0.02 + ex, 0.06, 0.09)), 0.02, white, "bunny ear", scale=(1, 0.6, 3)),
                 lena.p["elbowR"])


def dress_mom(mom):
    R, hc = mom.R, mom.head_c
    scarf = toon("Mom scarf", (0.12, 0.25, 0.55))
    head = mom.p["head"]
    mom.add(ball(hc + Vector((0, -0.2 * R, 0.08 * R)), 1.12 * R, scarf, "scarf", scale=(1.02, 1, 1.05)), head)
    mom.add(ball(hc + Vector((0, -0.25 * R, -1.0 * R)), 0.75 * R, scarf, "scarf drape", scale=(1.3, 0.9, 1.1)), head)
    # long coat skirt
    coat = toon("Mom top", (0.5, 0.52, 0.55))
    bpy.ops.mesh.primitive_cone_add(radius1=0.3, radius2=0.22, depth=0.45, location=(0, 0, 0.66), vertices=24)
    sk = _finish(bpy.context.object, coat, "coat skirt", smooth=True)
    mom.add(sk, mom.p["hips"])
    bag = toon("Mom bag", (0.55, 0.32, 0.18))
    mom.add(box((-0.3, -0.05, 1.0), (0.12, 0.35, 0.3), bag, "bag", bevel=0.03), mom.p["torso"])


def dress_rahim(rah):
    R, hc = rah.R, rah.head_c
    head = rah.p["head"]
    ink = toon("Rahim hair", (0.1, 0.08, 0.07))
    rah.add(ball(hc + Vector((0, 0.95 * R, -0.33 * R)), 0.3 * R, ink, "mustache", scale=(1.7, 0.6, 0.55)), head)
    cap = toon("Rahim cap", (0.12, 0.15, 0.3))
    bpy.ops.mesh.primitive_cylinder_add(radius=1.0 * R, depth=0.45 * R, location=hc + Vector((0, 0, 0.75 * R)),
                                        vertices=28)
    rah.add(_finish(bpy.context.object, cap, "cap", smooth=True), head)
    rah.add(box(hc + Vector((0, 0.95 * R, 0.55 * R)), (1.3 * R, 0.7 * R, 0.08 * R), cap, "cap visor"), head)
    rah.add(box(hc + Vector((0, 0.98 * R, 0.78 * R)), (0.35 * R, 0.05 * R, 0.2 * R),
                toon("Badge", (0.95, 0.78, 0.2)), "cap badge"), head)
    for b in ("browL", "browR"):
        rah.p[b].scale = (1.3, 1, 1.8)
    vest = toon("Rahim vest", (0.95, 0.45, 0.08))
    torso = rah.p["torso"]
    z = 0.86 + 0.29
    rah.add(box((0, 0, z), (0.46, 0.3, 0.5), vest, "vest", bevel=0.05), torso)
    rah.add(box((0, 0.155, z), (0.47, 0.02, 0.06), toon("Reflective", (0.9, 0.9, 0.9), 0.5), "vest stripe"), torso)


def dress_extra(person, hair_col, hat=None):
    R, hc = person.R, person.head_c
    head = person.p["head"]
    person.add(ball(hc + Vector((0, -0.15 * R, 0.18 * R)), 1.03 * R, toon(f"{person.name} hair", hair_col),
                    "hair", scale=(1, 0.95, 0.9)), head)
    if hat:
        person.add(ball(hc + Vector((0, -0.05 * R, 0.45 * R)), 1.06 * R, toon(f"{person.name} hat", hat), "hat",
                        scale=(1, 1, 0.6)), head)


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
        _finish(bpy.context.object, steel, "Column", smooth=True)
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
    _finish(bpy.context.object, toon("Clock", (0.96, 0.96, 0.92), 0.5), "Clock")

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
    inner = toon("Train inside", (0.78, 0.78, 0.76), 0.35)
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
                parts.append(_finish(bpy.context.object, under, "Wheel", smooth=True))
        if w == 4:  # front cab
            parts.append(ball((cx, y1 + 1.5, 2.3), 1.6, white, "Nose", scale=(1, 1.5, 1.05)))
            parts.append(ball((cx, y1 + 1.9, 2.9), 1.2, dark, "Windscreen", scale=(1.1, 1.3, 0.5)))
        for p in parts:
            parent_keep(p, train)
    # warm light in our vestibule
    bpy.ops.object.light_add(type="POINT", location=(-1.5, y_rear + WAGON + GAP + DOOR_LOCAL_Y, 3.2))
    lamp = bpy.context.object
    lamp.data.energy = 120
    lamp.data.color = (1, 0.9, 0.75)
    parent_keep(lamp, train)
    for f in range(1, FRAMES + 1):
        train.location.y = train_offset((f - 1) / FPS)
        train.keyframe_insert("location", frame=f)
    return train


# ================================================================ POV body


class POVArms:
    """Green sleeves + hands parented to the camera, posed in camera space."""

    def __init__(self, cam):
        self.cam = cam
        sleeve = toon("POV sleeve", (0.16, 0.42, 0.2), 0.3)
        cuff = toon("POV cuff", (0.92, 0.86, 0.66), 0.35)
        skin = toon("POV skin", (0.93, 0.7, 0.52), 0.35)
        self.parts = {}
        for side in ("L", "R"):
            s = rod((0, 0, 0), (0, 0, 0.5), 0.07, sleeve, f"POV sleeve {side}")
            c = rod((0, 0, 0), (0, 0, 0.07), 0.078, cuff, f"POV cuff {side}")
            h = ball((0, 0, 0), 0.07, skin, f"POV hand {side}", scale=(0.9, 1.0, 1.3))
            th = ball((0, 0, 0), 0.03, skin, f"POV thumb {side}")
            for o in (s, c, h, th):
                o.rotation_mode = "QUATERNION"
                parent_local(o, cam)
            self.parts[side] = (s, c, h, th)

    def set(self, f, side, hand_local):
        s, c, h, th = self.parts[side]
        sx = -1 if side == "L" else 1
        shoulder = Vector((sx * 0.22, -0.5, 0.15))
        hand = Vector(hand_local)
        d = hand - shoulder
        if d.length > 0.8:  # arm can't stretch further than this
            hand = shoulder + d.normalized() * 0.8
            d = hand - shoulder
        if d.length < 0.05:
            d = Vector((0, 0, -0.1))
        u = d.normalized()
        wrist = hand - u * 0.07
        place_rod(s, shoulder, wrist - u * 0.03)
        # keep sleeve length sane when the hand is far away
        s.scale = (1, 1, (wrist - u * 0.03 - shoulder).length / 0.5)
        place_rod(c, wrist - u * 0.06, wrist)
        h.location = hand
        h.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(u)
        th.location = hand + Vector((-sx * 0.05, 0.02, 0.0))
        for o in (s, c, h, th):
            o.keyframe_insert("location", frame=f)
            o.keyframe_insert("rotation_quaternion", frame=f)
        s.keyframe_insert("scale", frame=f)


def world_to_cam(cam, p):
    bpy.context.view_layer.update()
    return cam.matrix_world.inverted() @ Vector(p)


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
    build_train()

    lena = Person("Lena", 0.62, 0.17, (0.96, 0.76, 0.6), (0.45, 0.72, 0.92), (0.15, 0.2, 0.38), (0.9, 0.45, 0.6))
    dress_lena(lena)
    mom = Person("Mom", 0.98, 0.2, (0.9, 0.68, 0.52), (0.5, 0.52, 0.55), (0.25, 0.25, 0.3), (0.2, 0.15, 0.12))
    dress_mom(mom)
    rahim = Person("Rahim", 1.05, 0.21, (0.82, 0.6, 0.45), (0.2, 0.24, 0.4), (0.22, 0.22, 0.25), (0.1, 0.1, 0.1))
    dress_rahim(rahim)
    extras = []
    looks = [((0.7, 0.3, 0.2), (0.3, 0.3, 0.35), (0.15, 0.1, 0.05), None),
             ((0.3, 0.5, 0.3), (0.2, 0.2, 0.25), (0.5, 0.35, 0.2), (0.6, 0.6, 0.2)),
             ((0.55, 0.25, 0.45), (0.4, 0.35, 0.3), (0.05, 0.05, 0.05), None),
             ((0.85, 0.75, 0.3), (0.2, 0.3, 0.45), (0.8, 0.7, 0.4), None),
             ((0.35, 0.35, 0.6), (0.3, 0.25, 0.2), (0.6, 0.6, 0.6), (0.3, 0.3, 0.3))]
    for i, (top, pants, hair, hat) in enumerate(looks):
        e = Person(f"Passenger{i}", random.uniform(0.92, 1.05), 0.2,
                   random.choice([(0.95, 0.75, 0.6), (0.75, 0.55, 0.4), (0.6, 0.42, 0.3)]),
                   top, pants, (0.12, 0.12, 0.12))
        dress_extra(e, hair, hat)
        extras.append(e)

    cam_data = bpy.data.cameras.new("POV")
    cam_data.lens = 12
    cam_data.sensor_fit = "VERTICAL"
    cam_data.sensor_height = 36
    cam_data.clip_start = 0.05
    cam = bpy.data.objects.new("POV camera", cam_data)
    bpy.context.collection.objects.link(cam)
    scene.camera = cam
    cam.rotation_mode = "XYZ"
    arms = POVArms(cam)

    rnd = random.Random(11)
    shake = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(-1, 1)) for _ in range(FRAMES + 2)]

    for f in range(1, FRAMES + 1):
        t = (f - 1) / FPS
        dy = door_y(t)
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
            y = dy - lerp(0.35 + 0.0, -0.05, u)
            z = lerp(2.55, 2.75, u) + 0.45 * math.sin(math.pi * u)
        else:
            x = lerp(-1.15, -1.35, seg(t, 10.4, 11.2))
            y = dy + 0.05
            z = 2.78 - 0.4 * math.sin(math.pi * min(1, (t - 10.4) / 0.6))
        # yaw (+ = left / towards the train), pitch (+ = up)
        yaw, pitch = -38.0, -27.0
        yaw = lerp(yaw, 0, seg(t, 3.0, 3.6)); pitch = lerp(pitch, -6, seg(t, 3.0, 3.6))
        yaw = lerp(yaw, -38, seg(t, 5.0, 5.4)); pitch = lerp(pitch, -30, seg(t, 5.0, 5.4))
        yaw = lerp(yaw, 0, seg(t, 6.5, 7.0)); pitch = lerp(pitch, -6, seg(t, 6.5, 7.0))
        yaw = lerp(yaw, 22, seg(t, 7.6, 8.3)); pitch = lerp(pitch, 2, seg(t, 7.6, 8.3))
        yaw = lerp(yaw, -8, seg(t, 9.6, 10.3)); pitch = lerp(pitch, -28, seg(t, 9.8, 10.5))
        yaw = lerp(yaw, -90, seg(t, 10.6, 11.3)); pitch = lerp(pitch, -20, seg(t, 10.6, 11.3))
        pitch = lerp(pitch, -8, seg(t, 12.8, 13.3))
        # shake: running jitter, explosions, jump impact
        amp = 0.8 if t < 9.6 else 0.35
        for te, k in ((4.25, 3.0), (7.85, 3.5), (10.4, 4.0)):
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
                      talk=talking("Lena", t),
                      reach2=(130, 35), worry=1.2)
        elif t < 12.0:
            lpos = Vector((lerp(1.2, 0.65, seg(t, 9.6, 11.0)), dy - lerp(0.9, 0.25, seg(t, 9.6, 11.4)), 1.0))
            lena.pose(f, t, lpos, facing=lerp(0, 50, seg(t, 10.5, 11.5)), run=1.0, run_rate=1.9,
                      look=(25, 20), reach2=(150, 20), worry=1.3)
        else:
            u = seg(t, 12.0, 12.6)
            lpos = Vector((lerp(0.65, -0.75, u), dy - 0.25 + 0.6 * seg(t, 12.7, 13.2), lerp(1.0, 1.25, u)))
            lena.pose(f, t, lpos, facing=lerp(50, 90, u), run=1.0 - u, run_rate=1.9, look=(0, 25),
                      reach2=(150, 20), z=0.35 * math.sin(math.pi * u), worry=1.3)

        # ---------------- Mom
        if t < 9.6:
            ahead = lerp(2.6, -1.6, seg(t, 7.2, 9.6))
            mpos = Vector((lerp(1.9, 1.5, seg(t, 7.0, 9.0)), y + ahead, 1.0))
            look_back = seg(t, 3.4, 3.8) * (1 - seg(t, 5.0, 5.5))
            mom.pose(f, t, mpos, facing=0, run=1.0, run_rate=1.6, look=(150 * look_back, 0),
                     talk=talking("Mom", t))
        elif t < 13.0:
            mpos = Vector((lerp(1.5, 0.9, seg(t, 9.6, 11.0)), dy - lerp(1.3, 1.15, seg(t, 10, 12)), 1.0))
            mom.pose(f, t, mpos, facing=lerp(0, 40, seg(t, 11.5, 12.5)), run=1.0, run_rate=1.6, look=(10, 10))
        else:
            u = seg(t, 13.0, 13.6)
            mpos = Vector((lerp(0.9, -0.55, u), dy - lerp(1.15, 0.45, u), lerp(1.0, 1.25, u)))
            mom.pose(f, t, mpos, facing=lerp(40, 90, u), run=1.0 - u, run_rate=1.6, look=(0, 15),
                     reach=(120, 10), z=0.4 * math.sin(math.pi * u))

        # ---------------- Rahim (inside the door, rides with the train)
        if t < 9.6:
            rpos = Vector((-0.35, dy + 0.35, 1.25))
            rahim.pose(f, t, rpos, facing=-150, look=(0, -5), talk=talking("Rahim", t),
                       reach=(lerp(60, 95, seg(t, 7.5, 8.5)), 25), reach2=(150, -40), lean=0)
        else:
            u = seg(t, 9.6, 10.1)
            rpos = Vector((lerp(-0.35, -0.6, u), dy + lerp(0.35, 0.8, u), 1.25))
            face_cam = seg(t, 12.8, 13.1)
            rahim.pose(f, t, rpos, facing=lerp(-150, -95, u), look=(lerp(-20, -110, face_cam), -10),
                       talk=talking("Rahim", t), reach=(lerp(95, 70, seg(t, 12.6, 13.0)), 30),
                       reach2=(150, -40), lean=0)

        # ---------------- background passengers on the platform
        for i, e in enumerate(extras):
            if i < 3:  # running ahead
                epos = Vector((1.6 + i * 0.9, y + 5 + i * 3.2 + 0.4 * t * (i - 1), 1.0))
                e.pose(f, t, epos, facing=0, run=1.0, run_rate=1.5 + 0.1 * i)
            else:  # standing, frozen, staring at the smoke
                epos = Vector((3.2 + (i - 3) * 0.7, 24 + (i - 3) * 14, 1.0))
                e.pose(f, t, epos, facing=-70 + i * 10, look=(20, 10), worry=1.5,
                       reach=(20, 0) if i == 3 else None)

        # ---------------- POV hands
        if t < 9.6:
            arms.set(f, "R", world_to_cam(cam, lena.hand_world("L")))
            if t < 8.6:
                bob = 0.05 * math.sin(run_ph)
                arms.set(f, "L", (-0.3, -0.42 + bob, -0.5))
            else:
                arms.set(f, "L", world_to_cam(cam, rahim.hand_world("R")))
        elif t < 10.6:
            arms.set(f, "L", world_to_cam(cam, rahim.hand_world("R")) if t < 10.0 else (-0.35, -0.5, -0.45))
            arms.set(f, "R", (0.32, -0.48, -0.45))
        else:
            arms.set(f, "L", (-0.32, -0.45, -0.5))
            if 11.2 <= t < 12.7:
                arms.set(f, "R", world_to_cam(cam, lena.hand_world("L")))
            else:
                arms.set(f, "R", (0.3, -0.45, -0.5))

    # ---------------- light, sky, render settings
    bpy.ops.object.light_add(type="SUN", rotation=(D(50), D(-20), D(-60)))
    sun = bpy.context.object
    sun.data.energy = 2.6
    sun.data.color = (1.0, 0.88, 0.75)
    sun.data.angle = D(2)
    world = bpy.data.worlds.new("Sky")
    scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (0.78, 0.62, 0.5, 1)
    bg.inputs["Strength"].default_value = 0.9

    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = 10
    scene.cycles.use_denoising = True
    scene.cycles.max_bounces = 4
    scene.cycles.diffuse_bounces = 1
    scene.cycles.glossy_bounces = 0
    scene.cycles.transparent_max_bounces = 4
    scene.render.resolution_x = 540
    scene.render.resolution_y = 960
    scene.view_settings.view_transform = "Standard"
    scene.render.use_freestyle = True
    scene.render.line_thickness_mode = "ABSOLUTE"
    ls = scene.view_layers[0].freestyle_settings.linesets[0]
    ls.select_silhouette = ls.select_border = ls.select_crease = True
    if ls.linestyle is None:
        ls.linestyle = bpy.data.linestyles.new("Ink")
    ls.linestyle.color = (0.02, 0.02, 0.02)
    ls.linestyle.thickness = 1.7
    scene.frame_set(1)
    return scene


def arg(flag):
    if flag in sys.argv:
        i = sys.argv.index(flag)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else True
    return None


if __name__ == "__main__":
    sc = build()
    here = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else os.getcwd()
    if arg("--save"):
        bpy.ops.wm.save_as_mainfile(filepath=os.path.join(here, "train_pov.blend"))
    if arg("--still"):
        for fr in str(arg("--still")).split(","):
            sc.frame_set(int(fr))
            sc.render.filepath = os.path.join(here, "test", f"still_{int(fr):03d}.png")
            bpy.ops.render.render(write_still=True)
    if arg("--render"):
        sc.render.filepath = os.path.join(here, "frames", "f_")
        sc.render.image_settings.file_format = "PNG"
        bpy.ops.render.render(animation=True)
