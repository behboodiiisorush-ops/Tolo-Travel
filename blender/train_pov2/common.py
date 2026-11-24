"""Shared building blocks for «واگن آخر ۲ — برگشت» (copied from ../train_pov/common.py so the
characters look the same): materials, primitives, puppet characters, POV arms, dialogue timing
and render settings.  Change from episode 1: nobody wears a headscarf or hijab (user rule)."""

import math
import os
import random
import sys

import bpy
from mathutils import Matrix, Vector

FPS = 24
D = math.radians
HERE = os.path.dirname(os.path.abspath(__file__))

# ================================================================ timing


def ease(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def seg(t, a, b):
    """0 before a, eased 0..1 between a and b, 1 after b."""
    return ease((t - a) / (b - a))


def lerp(a, b, u):
    return a + (b - a) * u

# ================================================================ materials

_mats = {}


def toon(name, color, glow=0.2):
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


def finish(o, m, name, smooth=False):
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
    return finish(o, m, name)


def ball(loc, r, m, name="Ball", scale=(1, 1, 1), seg=20):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=loc, segments=seg, ring_count=max(8, seg // 2))
    o = bpy.context.object
    o.scale = scale
    bpy.ops.object.transform_apply(scale=True)
    return finish(o, m, name, smooth=True)


def rod(a, b, r, m, name="Rod", verts=16):
    a, b = Vector(a), Vector(b)
    d = b - a
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=d.length, location=(a + b) / 2, vertices=verts)
    o = bpy.context.object
    o.rotation_mode = "QUATERNION"
    o.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(d)
    return finish(o, m, name, smooth=True)


def place_rod(o, a, b):
    a, b = Vector(a), Vector(b)
    o.location = (a + b) / 2
    o.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(b - a)


REST = {}  # rest-pose world position of every empty we create (they are never rotated at build time)


def empty(name, loc=(0, 0, 0)):
    o = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(o)
    o.location = loc
    o.empty_display_size = 0.1
    REST[o.name] = Vector(loc)
    return o


def parent_keep(child, parent):
    """Parent without moving the child (fast path for our unrotated empties)."""
    if parent.name in REST and child.parent is None:
        child.parent = parent
        child.matrix_parent_inverse = Matrix.Translation(-REST[parent.name])
        return
    bpy.context.view_layer.update()
    mw = child.matrix_world.copy()
    child.parent = parent
    child.matrix_parent_inverse = parent.matrix_world.inverted()
    child.matrix_world = mw


def parent_local(child, parent):
    child.parent = parent
    child.matrix_parent_inverse = Matrix.Identity(4)

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




# ================================================================ dialogue

from captions import CAPTIONS  # noqa: E402


def talking(name, t):
    return any(s <= t <= e for s, e, who, _ in CAPTIONS if who == name)


# ================================================================ characters


class Person:
    """Puppet-like character built at the origin facing +Y, then driven by its root.

    look: dict of shape/colour options, see the character recipes below.
    """

    def __init__(self, name, s, R, look):
        self.name, self.s, self.R, self.p = name, s, R, {}
        L = look
        sk = self.m_skin = toon(f"{name} skin", L["skin"])
        m_top = toon(f"{name} top", L["top"])
        m_sleeve = toon(f"{name} sleeve", L.get("sleeve", L["top"]))
        m_pants = toon(f"{name} pants", L["pants"])
        m_shoes = toon(f"{name} shoes", L["shoes"])
        hair_c = L.get("hair", (0.15, 0.1, 0.07))
        m_hair = self.m_hair = toon(f"{name} hair", hair_c)
        white = toon("Eye white", (0.99, 0.99, 0.97), 0.55)
        ink = toon("Ink", (0.03, 0.03, 0.03), 0.0)
        iris = toon(f"{name} iris", L.get("iris", (0.35, 0.22, 0.12)), 0.3)
        shine = toon("Eye shine", (1, 1, 1), 1.0)
        mouth_m = toon("Mouth inside", (0.3, 0.05, 0.07), 0.05)
        tongue = toon("Tongue", (0.85, 0.35, 0.38), 0.2)

        hip_z = 0.86 * s
        sh_z = hip_z + 0.55 * s
        neck_z = sh_z + 0.05 * s
        hc = self.head_c = Vector((0, 0, neck_z + R * 1.02))
        limb = 0.065 * s ** 0.5
        width = L.get("width", 1.0)

        root = self.p["root"] = empty(name)
        hips = self.pivot("hips", (0, 0, hip_z), root)
        torso = self.pivot("torso", (0, 0, hip_z), hips)
        self.torso_z = hip_z + 0.29 * s
        self.add(box((0, 0, hip_z + 0.29 * s), (0.42 * s * width, 0.26 * s * width ** 0.5, 0.6 * s), m_top,
                     "torso", bevel=0.07 * s), torso)
        if L.get("belly"):
            self.add(ball((0, 0.1 * s, hip_z + 0.2 * s), 0.22 * s * L["belly"], m_top, "belly",
                          scale=(1.1, 0.9, 1.0)), torso)
        if L.get("buttons"):
            for k in range(3):
                self.add(ball((0, 0.135 * s * width ** 0.5 + (0.06 * s if L.get("belly") else 0),
                               hip_z + (0.15 + 0.13 * k) * s), 0.018 * s, toon(f"{name} buttons", L["buttons"]),
                              "button", seg=10), torso)
        self.add(ball((0, 0, hip_z + 0.02 * s), 0.2 * s * width, m_pants, "pelvis", scale=(1.1, 0.75, 0.6)), hips)
        if L.get("belt"):
            self.add(box((0, 0, hip_z + 0.03 * s), (0.44 * s * width, 0.28 * s * width ** 0.5, 0.05 * s),
                         toon(f"{name} belt", L["belt"]), "belt"), torso)

        neck = self.pivot("neck", (0, 0, neck_z), torso)
        self.add(rod((0, 0, sh_z - 0.02), (0, 0, neck_z + 0.08 * s), 0.055 * s, sk, "neck"), neck)
        if L.get("collar"):
            bpy.ops.mesh.primitive_torus_add(location=(0, 0, sh_z + 0.01), major_radius=0.085 * s,
                                             minor_radius=0.03 * s, major_segments=24, minor_segments=8)
            self.add(finish(bpy.context.object, toon(f"{name} collar", L["collar"]), "collar", True), neck)
        head = self.pivot("head", tuple(hc), neck)
        self.add(ball(hc, R, sk, "head", scale=L.get("head_shape", (1.0, 0.95, 1.06)), seg=28), head)
        # ears
        for sx in (-1, 1):
            self.add(ball(hc + Vector((sx * 0.97 * R, -0.05 * R, -0.05 * R)), 0.22 * R, sk, "ear",
                          scale=(0.45, 0.7, 1.0), seg=12), head)
        # eyes: white, coloured iris, pupil, shine; eyelid; lashes; brows
        eye_sz = L.get("eye", 1.0)
        for side, sx in (("L", -1), ("R", 1)):
            ec = hc + Vector((sx * 0.37 * R, 0.8 * R, 0.1 * R))
            er = 0.26 * R * eye_sz
            self.add(ball(ec, er, white, f"eye {side}", scale=(1, 0.55, 1.15)), head)
            self.add(ball(ec + Vector((0, 0.11 * R, -0.02 * R)), 0.15 * R * eye_sz, iris, f"iris {side}",
                          scale=(1, 0.5, 1.2), seg=14), head)
            self.add(ball(ec + Vector((0, 0.15 * R, -0.02 * R)), 0.085 * R * eye_sz, ink, f"pupil {side}",
                          scale=(1, 0.5, 1.2), seg=12), head)
            self.add(ball(ec + Vector((sx * -0.04 * R, 0.19 * R, 0.05 * R)), 0.03 * R, shine, f"shine {side}",
                          seg=8), head)
            lid = L.get("lid", 0.0)
            if lid:
                self.add(ball(ec + Vector((0, 0.02 * R, (0.2 - 0.12 * lid) * R)), er * 1.08, sk, f"lid {side}",
                              scale=(1.05, 0.62, 0.7), seg=14), head)
            if L.get("lashes"):
                for k in range(3):
                    lb = box(ec + Vector((sx * (0.12 + 0.07 * k) * R, 0.05 * R, (0.27 - 0.03 * k) * R)),
                             (0.03 * R, 0.02 * R, 0.11 * R), ink, "lash")
                    lb.rotation_euler = (0, sx * D(25 + 15 * k), 0)
                    self.add(lb, head)
            bw = L.get("brow", 1.0)
            self.p[f"brow{side}"] = self.add(
                box(ec + Vector((0, 0.07 * R, 0.37 * R)), (0.36 * R * bw, 0.06 * R, 0.08 * R * bw),
                    toon(f"{name} brows", L.get("brow_col", hair_c)), f"brow {side}", bevel=0.02 * R), head)
        nose = L.get("nose", (1, 1, 1))
        self.add(ball(hc + Vector((0, 0.97 * R, -0.12 * R)), 0.17 * R, sk, "nose",
                      scale=(nose[0], 0.9 * nose[1], 0.85 * nose[2]), seg=14), head)
        if L.get("blush"):
            for sx in (-1, 1):
                self.add(ball(hc + Vector((sx * 0.55 * R, 0.76 * R, -0.25 * R)), 0.13 * R,
                              toon("Blush", L["blush"], 0.3), "blush", scale=(1, 0.3, 0.6), seg=10), head)
        # puppet mouth: dark inside + tongue + hinged jaw (with lip colour edge)
        self.add(ball(hc + Vector((0, 0.68 * R, -0.5 * R)), 0.3 * R, mouth_m, "mouth inside",
                      scale=(1.25, 0.6, 0.55), seg=14), head)
        jaw = self.pivot("jaw", tuple(hc + Vector((0, 0.1 * R, -0.42 * R))), head)
        self.add(ball(hc + Vector((0, 0.66 * R, -0.6 * R)), 0.2 * R, tongue, "tongue", scale=(1.2, 0.8, 0.4),
                      seg=10), jaw)
        self.add(ball(hc + Vector((0, 0.38 * R, -0.66 * R)), 0.52 * R, sk, "jaw", scale=(1.3, 1.15, 0.6), seg=20),
                 jaw)
        if L.get("lips"):
            self.add(box(hc + Vector((0, 0.86 * R, -0.5 * R)), (0.34 * R, 0.05 * R, 0.05 * R),
                         toon(f"{name} lips", L["lips"], 0.3), "lips", bevel=0.02 * R), jaw)

        for side, sx in (("L", -1), ("R", 1)):
            shp = Vector((sx * 0.27 * s * width, 0, sh_z - 0.04 * s))
            sh = self.pivot(f"shoulder{side}", tuple(shp), torso)
            self.add(ball(shp, limb * 1.55, m_top, f"shoulder ball {side}"), sh)
            elp = shp + Vector((0, 0, -0.29 * s))
            self.add(rod(shp, elp, limb, m_sleeve, f"upper arm {side}"), sh)
            el = self.pivot(f"elbow{side}", tuple(elp), sh)
            self.add(ball(elp, limb * 1.1, m_sleeve, f"elbow {side}", seg=12), el)
            hp = elp + Vector((0, 0, -0.26 * s))
            self.add(rod(elp, hp, limb * 0.95, m_sleeve, f"forearm {side}"), el)
            if L.get("cuff"):
                self.add(rod(hp + Vector((0, 0, 0.05 * s)), hp, limb * 1.12, toon(f"{name} cuff", L["cuff"]),
                             "cuff"), el)
            hand_m = toon(f"{name} gloves", L["gloves"]) if L.get("gloves") else sk
            self.p[f"hand{side}"] = self.add(ball(hp + Vector((0, 0, -0.04 * s)), limb * 1.35, hand_m, f"hand {side}",
                                                  scale=(0.9, 0.8, 1.15), seg=14), el)
            self.add(ball(hp + Vector((-sx * 0.045 * s, 0.03 * s, -0.02 * s)), limb * 0.5, hand_m, "thumb", seg=8), el)

            hpp = Vector((sx * 0.11 * s * width, 0, hip_z))
            th = self.pivot(f"thigh{side}", tuple(hpp), hips)
            kp = hpp + Vector((0, 0, -0.42 * s))
            self.add(rod(hpp, kp, limb * 1.25 * width, m_pants, f"thigh {side}"), th)
            kn = self.pivot(f"knee{side}", tuple(kp), th)
            self.add(ball(kp, limb * 1.3 * width, m_pants, f"knee {side}", seg=12), kn)
            ap = kp + Vector((0, 0, -0.38 * s))
            self.add(rod(kp, ap, limb * 1.1, toon(f"{name} socks", L["socks"]) if L.get("socks") else m_pants,
                         f"shin {side}"), kn)
            self.add(box(ap + Vector((0, 0.06 * s, -0.04 * s)), (0.14 * s, 0.28 * s, 0.1 * s), m_shoes,
                         f"shoe {side}", bevel=0.035 * s), kn)

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

    def pose(self, f, t, pos, facing, run=0.0, run_rate=1.5, lean=-12, look=(0, 0), talk=None,
             reach=None, reach2=None, worry=1.0, z=0.0, crouch=0.0, sit=0.0, seat_h=0.5, wave=0.0, hug=0.0):
        """Pose every pivot for frame f and keyframe it.

        facing: body yaw in degrees (0 = +Y).  look: (yaw, pitch) of the head.
        reach / reach2: (shoulder X, shoulder Z) degrees for the right / left arm.
        """
        p = self.p
        if talk is None:
            talk = talking(self.name, t)
        ph = 2 * math.pi * t * run_rate + sum(map(ord, self.name)) % 7
        a = D(38) * run
        p["root"].location = (pos[0], pos[1], pos[2] + z)
        p["root"].rotation_euler = (0, 0, D(facing))
        stand_h = 0.86 * self.s + 0.05 * self.s * abs(math.sin(ph)) * run - 0.25 * self.s * crouch
        p["hips"].location = (0, 0, lerp(stand_h, seat_h, sit))
        breathe = 0.02 * math.sin(2 * math.pi * t * 0.4 + len(self.name))
        p["torso"].rotation_euler = (D(lean) * run + D(-20) * crouch + D(-35) * hug + breathe, 0,
                                     D(6) * math.sin(ph) * run)
        for side, sgn in (("L", 1), ("R", -1)):
            sw = sgn * math.sin(ph)
            p[f"thigh{side}"].rotation_euler = (a * sw + D(50) * crouch + D(88) * sit, 0, D(sgn * -4) * sit)
            p[f"knee{side}"].rotation_euler = (-D(15 + 60 * max(0.0, -sw)) * run - D(80) * crouch - D(88) * sit,
                                               0, 0)
            p[f"shoulder{side}"].rotation_euler = (-a * 0.9 * sw + D(25) * sit + D(70) * hug, 0,
                                                   sgn * D(-8) + sgn * D(25) * hug)
            p[f"elbow{side}"].rotation_euler = (D(75) * run + D(15) + D(45) * sit + D(60) * hug, 0, 0)
        if reach is not None:
            p["shoulderR"].rotation_euler = (D(reach[0]), 0, D(reach[1]))
            p["elbowR"].rotation_euler = (D(10), 0, 0)
        if reach2 is not None:
            p["shoulderL"].rotation_euler = (D(reach2[0]), 0, D(reach2[1]))
            p["elbowL"].rotation_euler = (D(10), 0, 0)
        if wave:
            p["shoulderR"].rotation_euler = (D(150), 0, D(-25 + 20 * math.sin(2 * math.pi * t * 2.5)) * wave)
            p["elbowR"].rotation_euler = (D(20), 0, 0)
        p["neck"].rotation_euler = (D(look[1]) * 0.4, 0, D(look[0]) * 0.4)
        p["head"].rotation_euler = (D(look[1]) * 0.6, 0, D(look[0]) * 0.6)
        jaw = 0.5 + 0.5 * math.sin(2 * math.pi * t * 5.5) if talk else 0.0
        p["jaw"].rotation_euler = (-D(4) - D(26) * jaw, 0, 0)
        for side, sgn in (("L", -1), ("R", 1)):
            p[f"brow{side}"].rotation_euler = (0, D(18) * worry * sgn, 0)
        p["root"].keyframe_insert("location", frame=f)
        p["root"].keyframe_insert("rotation_euler", frame=f)
        p["hips"].keyframe_insert("location", frame=f)
        for k, o in p.items():
            if o.type == "EMPTY" and k != "root":
                o.keyframe_insert("rotation_euler", frame=f)
        for side in ("L", "R"):
            p[f"brow{side}"].keyframe_insert("rotation_euler", frame=f)

    def hand_world(self, side):
        bpy.context.view_layer.update()
        return self.p[f"hand{side}"].matrix_world.translation.copy()


# ---------------------------------------------------------------- hair & accessories


def hair_cap(person, color, scale=(1, 0.95, 1.0), off=(0, -0.12, 0.1), r=1.04):
    R, hc = person.R, person.head_c
    return person.add(ball(hc + Vector(off) * R, r * R, toon(f"{person.name} hair", color), "hair", scale=scale),
                      person.p["head"])


def glasses(person, color=(0.15, 0.1, 0.08)):
    R, hc = person.R, person.head_c
    m = toon(f"{person.name} glasses", color)
    for sx in (-1, 1):
        bpy.ops.mesh.primitive_torus_add(location=hc + Vector((sx * 0.37 * R, 0.98 * R, 0.1 * R)),
                                         rotation=(D(90), 0, 0), major_radius=0.27 * R, minor_radius=0.035 * R,
                                         major_segments=24, minor_segments=6)
        person.add(finish(bpy.context.object, m, "glasses rim", True), person.p["head"])
    person.add(box(hc + Vector((0, 1.0 * R, 0.12 * R)), (0.22 * R, 0.03 * R, 0.03 * R), m, "glasses bridge"),
               person.p["head"])


def scarf_wrap(person, color):
    s = person.s
    bpy.ops.mesh.primitive_torus_add(location=(0, 0, 0.86 * s + 0.55 * s + 0.02), major_radius=0.12 * s,
                                     minor_radius=0.055 * s, major_segments=24, minor_segments=10)
    person.add(finish(bpy.context.object, toon(f"{person.name} scarf", color), "neck scarf", True),
               person.p["torso"])
    person.add(box((0.07 * s, 0.14 * s, 0.86 * s + 0.35 * s), (0.08 * s, 0.03 * s, 0.32 * s),
                   toon(f"{person.name} scarf", color), "scarf tail", bevel=0.02 * s), person.p["torso"])


LOOKS = {
    "Lena": dict(skin=(0.97, 0.78, 0.63), top=(0.4, 0.72, 0.95), pants=(0.55, 0.25, 0.65), shoes=(0.95, 0.45, 0.62),
                 hair=(0.35, 0.18, 0.09), iris=(0.3, 0.55, 0.25), eye=1.2, lashes=True, blush=(0.98, 0.5, 0.55),
                 cuff=(0.98, 0.85, 0.3), collar=(0.98, 0.85, 0.3), buttons=(0.98, 0.85, 0.3), lid=0.0,
                 head_shape=(1.0, 0.95, 1.0)),
    "Mom": dict(skin=(0.9, 0.66, 0.5), top=(0.62, 0.16, 0.3), pants=(0.15, 0.2, 0.35), shoes=(0.3, 0.18, 0.1),
                hair=(0.12, 0.07, 0.05), iris=(0.35, 0.2, 0.1), lashes=True, lips=(0.75, 0.25, 0.3),
                buttons=(0.95, 0.8, 0.3), belt=(0.3, 0.18, 0.1), lid=0.35, width=0.95,
                head_shape=(0.95, 0.95, 1.1)),
    "Grandma": dict(skin=(0.9, 0.7, 0.58), top=(0.5, 0.3, 0.18), pants=(0.2, 0.42, 0.3), shoes=(0.15, 0.12, 0.1),
                    hair=(0.85, 0.85, 0.85), iris=(0.3, 0.3, 0.35), lid=0.6, blush=(0.95, 0.55, 0.55),
                    buttons=(0.95, 0.9, 0.7), width=1.1, belly=0.7, nose=(1.2, 1.1, 1.1), brow_col=(0.8, 0.8, 0.8)),
    "Rahim": dict(skin=(0.8, 0.57, 0.42), top=(0.2, 0.25, 0.45), pants=(0.25, 0.25, 0.3), shoes=(0.1, 0.1, 0.1),
                  hair=(0.1, 0.08, 0.07), iris=(0.25, 0.15, 0.08), brow=1.4, belly=1.0, width=1.12,
                  nose=(1.35, 1.25, 1.2), lid=0.3, gloves=(0.95, 0.95, 0.9)),
    "Jalal": dict(skin=(0.86, 0.64, 0.5), top=(0.55, 0.12, 0.15), pants=(0.42, 0.35, 0.25), shoes=(0.35, 0.2, 0.1),
                  hair=(0.93, 0.93, 0.9), brow=1.5, brow_col=(0.95, 0.95, 0.92), iris=(0.25, 0.35, 0.5), lid=0.5,
                  buttons=(0.85, 0.7, 0.3), nose=(1.3, 1.3, 1.25), collar=(0.92, 0.85, 0.65)),
    "Sara": dict(skin=(0.93, 0.72, 0.56), top=(0.1, 0.6, 0.62), pants=(0.1, 0.5, 0.55), shoes=(0.98, 0.98, 0.98),
                 hair=(0.08, 0.05, 0.04), iris=(0.2, 0.15, 0.1), lashes=True, lips=(0.85, 0.35, 0.4),
                 blush=(0.95, 0.55, 0.55), collar=(0.95, 0.95, 0.95)),
}


def make_lena():
    p = Person("Lena", 0.62, 0.17, LOOKS["Lena"])
    R, hc, head = p.R, p.head_c, p.p["head"]
    hair = LOOKS["Lena"]["hair"]
    hair_cap(p, hair)
    for sx in (-1, 1):
        p.add(ball(hc + Vector((sx * 1.0 * R, -0.25 * R, -0.25 * R)), 0.38 * R, toon("Lena hair", hair), "pigtail",
                   scale=(0.8, 0.8, 1.3)), head)
        p.add(ball(hc + Vector((sx * 0.9 * R, -0.2 * R, 0.05 * R)), 0.13 * R, toon("Hair tie", (0.98, 0.85, 0.3)),
                   "hair tie"), head)
    hat = toon("Lena beanie", (0.85, 0.15, 0.15))
    p.add(ball(hc + Vector((0, -0.05 * R, 0.38 * R)), 1.1 * R, hat, "beanie", scale=(1, 1, 0.72)), head)
    bpy.ops.mesh.primitive_torus_add(location=hc + Vector((0, -0.02 * R, 0.28 * R)), major_radius=1.02 * R,
                                     minor_radius=0.14 * R, major_segments=32, minor_segments=8)
    rim = finish(bpy.context.object, toon("Beanie rim", (0.97, 0.95, 0.88)), "beanie rim", smooth=True)
    rim.rotation_euler = (D(-12), 0, 0)
    p.add(rim, head)
    p.add(ball(hc + Vector((0, 0, 1.25 * R)), 0.28 * R, toon("Beanie rim", (0.97, 0.95, 0.88)), "pompom"), head)
    scarf_wrap(p, (0.98, 0.5, 0.65))
    white = toon("Bunny", (0.97, 0.95, 0.94))
    pink = toon("Bunny pink", (0.98, 0.6, 0.7))
    hp = p.p["handR"].matrix_world.translation
    el = p.p["elbowR"]
    p.add(ball(hp + Vector((0.02, 0.06, -0.12)), 0.08, white, "bunny body"), el)
    p.add(ball(hp + Vector((0.02, 0.06, 0.0)), 0.06, white, "bunny head"), el)
    for ex in (-0.025, 0.025):
        p.add(ball(hp + Vector((0.02 + ex, 0.06, 0.09)), 0.02, white, "bunny ear", scale=(1, 0.6, 3)), el)
        p.add(ball(hp + Vector((0.02 + ex, 0.08, 0.09)), 0.01, pink, "bunny ear in", scale=(1, 0.6, 3)), el)
    return p


def make_mom():
    p = Person("Mom", 0.98, 0.2, LOOKS["Mom"])
    R, hc, head = p.R, p.head_c, p.p["head"]
    hair = LOOKS["Mom"]["hair"]
    hair_cap(p, hair, off=(0, -0.14, 0.14))
    p.add(ball(hc + Vector((0, -0.95 * R, 0.2 * R)), 0.45 * R, toon("Mom hair", hair), "bun"), head)
    p.add(ball(hc + Vector((0, -0.62 * R, 0.45 * R)), 0.16 * R, toon("Mom clip", (0.05, 0.55, 0.6)), "hair clip",
               scale=(2.0, 0.8, 0.8)), head)
    for sx in (-1, 1):  # side locks framing the face
        p.add(ball(hc + Vector((sx * 0.88 * R, 0.1 * R, -0.25 * R)), 0.22 * R, toon("Mom hair", hair), "lock",
                   scale=(0.5, 0.7, 1.6)), head)
    scarf_wrap(p, (0.05, 0.55, 0.6))  # the teal scarf from episode 1, now around the neck
    bpy.ops.mesh.primitive_cone_add(radius1=0.3, radius2=0.22, depth=0.45, location=(0, 0, 0.66), vertices=24)
    p.add(finish(bpy.context.object, toon("Mom top", LOOKS["Mom"]["top"]), "coat skirt", True), p.p["hips"])
    p.add(box((-0.3, -0.05, 1.0), (0.12, 0.35, 0.3), toon("Mom bag", (0.85, 0.55, 0.15)), "bag", bevel=0.03),
          p.p["torso"])
    return p


def make_grandma():
    p = Person("Grandma", 0.9, 0.2, LOOKS["Grandma"])
    R, hc, head = p.R, p.head_c, p.p["head"]
    hair_cap(p, LOOKS["Grandma"]["hair"], off=(0, -0.15, 0.15))
    p.add(ball(hc + Vector((0, -0.9 * R, 0.55 * R)), 0.42 * R, toon("Grandma hair", LOOKS["Grandma"]["hair"]),
               "bun"), head)
    glasses(p, (0.6, 0.45, 0.15))
    shawl = toon("Grandma shawl", (0.85, 0.12, 0.15))
    s = p.s
    p.add(ball((0, -0.02, 0.86 * s + 0.48 * s), 0.3 * s, shawl, "shawl", scale=(1.25, 0.95, 0.55)), p.p["torso"])
    for k in range(10):  # floral dots
        a = D(k * 36)
        p.add(ball((math.cos(a) * 0.3 * s, math.sin(a) * 0.22 * s - 0.02, 0.86 * s + 0.52 * s), 0.025 * s,
                   toon("Flower", (0.98, 0.85, 0.2) if k % 2 else (0.98, 0.98, 0.95), 0.4), "flower", seg=8),
              p.p["torso"])
    bpy.ops.mesh.primitive_cone_add(radius1=0.32 * s, radius2=0.22 * s, depth=0.5 * s, location=(0, 0, 0.62 * s),
                                    vertices=24)
    p.add(finish(bpy.context.object, toon("Grandma skirt", (0.2, 0.42, 0.3)), "skirt", True), p.p["hips"])
    return p


def make_rahim():
    p = Person("Rahim", 1.05, 0.21, LOOKS["Rahim"])
    R, hc, head = p.R, p.head_c, p.p["head"]
    ink = toon("Rahim hair", (0.1, 0.08, 0.07))
    p.add(ball(hc + Vector((0, 0.95 * R, -0.33 * R)), 0.3 * R, ink, "mustache", scale=(1.8, 0.6, 0.6)), head)
    for sx in (-1, 1):
        p.add(ball(hc + Vector((sx * 0.85 * R, 0.2 * R, -0.1 * R)), 0.2 * R, ink, "sideburn", scale=(0.5, 0.8, 1.6)),
              head)
    cap = toon("Rahim cap", (0.12, 0.15, 0.32))
    bpy.ops.mesh.primitive_cylinder_add(radius=1.0 * R, depth=0.45 * R, location=hc + Vector((0, 0, 0.75 * R)),
                                        vertices=28)
    p.add(finish(bpy.context.object, cap, "cap", smooth=True), head)
    p.add(box(hc + Vector((0, 0.95 * R, 0.55 * R)), (1.3 * R, 0.7 * R, 0.08 * R), cap, "cap visor"), head)
    p.add(box(hc + Vector((0, 0.98 * R, 0.78 * R)), (0.35 * R, 0.05 * R, 0.2 * R), toon("Badge", (0.98, 0.8, 0.2), 0.5),
              "cap badge"), head)
    vest = toon("Rahim vest", (0.98, 0.45, 0.05))
    z = 0.86 * p.s + 0.29 * p.s
    p.add(box((0, 0.02, z), (0.5, 0.36, 0.5), vest, "vest", bevel=0.06), p.p["torso"])
    p.add(box((0, 0.2, z), (0.51, 0.02, 0.06), toon("Reflective", (0.92, 0.92, 0.92), 0.6), "vest stripe"),
          p.p["torso"])
    p.add(box((-0.12, 0.2, z + 0.12), (0.1, 0.03, 0.14), toon("Radio", (0.12, 0.12, 0.12)), "radio clip"),
          p.p["torso"])
    return p


def make_jalal():
    p = Person("Jalal", 0.95, 0.21, LOOKS["Jalal"])
    R, hc, head = p.R, p.head_c, p.p["head"]
    white = toon("Jalal hair", LOOKS["Jalal"]["hair"])
    for sx in (-1, 1):
        p.add(ball(hc + Vector((sx * 0.8 * R, -0.25 * R, 0.1 * R)), 0.38 * R, white, "side hair"), head)
    for k, (dx, dz, r) in enumerate([(0, -0.75, 0.55), (-0.35, -0.6, 0.38), (0.35, -0.6, 0.38), (0, -1.05, 0.4)]):
        p.add(ball(hc + Vector((dx * R, 0.6 * R, dz * R)), r * R, white, "beard", scale=(1.1, 0.8, 1.0)), head)
    p.add(ball(hc + Vector((0, 0.93 * R, -0.33 * R)), 0.28 * R, white, "mustache", scale=(1.8, 0.6, 0.55)), head)
    cap = toon("Jalal cap", (0.85, 0.75, 0.5))
    p.add(ball(hc + Vector((0, 0.05 * R, 0.55 * R)), 0.95 * R, cap, "flat cap", scale=(1.08, 1.15, 0.45)), head)
    p.add(box(hc + Vector((0, 0.95 * R, 0.5 * R)), (1.2 * R, 0.5 * R, 0.07 * R), cap, "cap brim", bevel=0.02), head)
    glasses(p, (0.2, 0.2, 0.22))
    return p


EXTRA_LOOKS = [
    dict(skin=(0.95, 0.75, 0.6), top=(0.98, 0.8, 0.1), pants=(0.2, 0.3, 0.5), shoes=(0.9, 0.2, 0.2),
         hair=(0.15, 0.08, 0.04), hat=(0.98, 0.8, 0.1)),
    dict(skin=(0.72, 0.5, 0.36), top=(0.95, 0.4, 0.55), pants=(0.15, 0.15, 0.18), shoes=(0.95, 0.95, 0.95),
         hair=(0.05, 0.04, 0.03), lashes=True, lips=(0.7, 0.2, 0.3)),
    dict(skin=(0.6, 0.42, 0.3), top=(0.2, 0.55, 0.85), pants=(0.6, 0.5, 0.3), shoes=(0.3, 0.2, 0.1),
         hair=(0.1, 0.06, 0.04), hat=(0.9, 0.3, 0.1)),
    dict(skin=(0.96, 0.78, 0.65), top=(0.45, 0.75, 0.3), pants=(0.4, 0.25, 0.15), shoes=(0.1, 0.1, 0.1),
         hair=(0.8, 0.55, 0.2)),
    dict(skin=(0.85, 0.62, 0.48), top=(0.95, 0.55, 0.15), pants=(0.25, 0.25, 0.6), shoes=(0.98, 0.98, 0.98),
         hair=(0.2, 0.1, 0.05), lashes=True, lips=(0.8, 0.3, 0.35), hat=(0.3, 0.75, 0.75)),
    dict(skin=(0.78, 0.56, 0.42), top=(0.5, 0.3, 0.7), pants=(0.2, 0.2, 0.2), shoes=(0.6, 0.3, 0.1),
         hair=(0.3, 0.3, 0.3), belly=0.9, width=1.1),
    dict(skin=(0.95, 0.74, 0.6), top=(0.85, 0.2, 0.2), pants=(0.15, 0.25, 0.4), shoes=(0.2, 0.2, 0.2),
         hair=(0.9, 0.75, 0.4), lashes=True),
]


def make_extra(i, s=None):
    L = dict(EXTRA_LOOKS[i % len(EXTRA_LOOKS)])
    L.setdefault("iris", (0.3, 0.2, 0.1))
    p = Person(f"Passenger{i}", s or (0.95 + 0.05 * (i % 3)), 0.2, L)
    hair_cap(p, L["hair"], scale=(1, 0.95, 0.9), off=(0, -0.15, 0.18), r=1.03)
    if L.get("hat"):
        p.add(ball(p.head_c + Vector((0, -0.05 * p.R, 0.45 * p.R)), 1.06 * p.R, toon(f"Passenger{i} hat", L["hat"]),
                   "hat", scale=(1, 1, 0.6)), p.p["head"])
    return p


def bunny(loc, parent, name="Bunny", k=1.0):
    """Lena's toy bunny (the same shape she carries) parented to `parent`; returns its parts."""
    white = toon("Bunny", (0.97, 0.95, 0.94))
    pink = toon("Bunny pink", (0.98, 0.6, 0.7))
    loc = Vector(loc)
    parts = [ball(loc + Vector((0, 0, -0.12)) * k, 0.08 * k, white, f"{name} body"),
             ball(loc, 0.06 * k, white, f"{name} head")]
    for ex in (-0.025, 0.025):
        parts.append(ball(loc + Vector((ex, 0, 0.09)) * k, 0.02 * k, white, f"{name} ear", scale=(1, 0.6, 3)))
        parts.append(ball(loc + Vector((ex, 0.02, 0.09)) * k, 0.01 * k, pink, f"{name} ear in", scale=(1, 0.6, 3)))
    for o in parts:
        parent_keep(o, parent) if parent.name in REST else parent_local(o, parent)
    return parts


def pov_bunny(cam, k=0.8):
    """The bunny in our own (POV) hand: a root empty parented to the camera, rotated so the
    bunny stands upright on screen.  Animate root.location in camera space."""
    root = empty("POV bunny root")
    bunny((0, 0, 0), root, "POV bunny", k)
    parent_local(root, cam)
    root.rotation_mode = "XYZ"
    root.rotation_euler = (D(-90), D(-10), 0)
    return root


def no_cam(light_obj):
    """Lights must not show up as bright discs in the shot."""
    light_obj.visible_camera = False
    light_obj.data.shadow_soft_size = 0.0
    return light_obj


def show(objs, f, visible):
    for o in objs:
        o.scale = (1, 1, 1) if visible else (0.001, 0.001, 0.001)
        o.keyframe_insert("scale", frame=f)


# ================================================================ wagon exterior

HALF_W = 1.55   # half width of a wagon shell
FLOOR_Z = 1.3   # floor top above the ground (the interior set has its floor at z=0)


def wagon_exterior(name, cx, y0, y1, z0, door_side, door_ys, burnt=0.0, panels=True):
    """White/red cartoon wagon shell along Y (same look as the train in episode 1).

    cx: centre x, y0..y1 its length, z0 the ground under it, door_side +1/-1: which long side has
    the doors, door_ys: centres of the door openings (1.3 m wide).  Returns (parts, door panels)."""
    white = toon("Train white", (0.93, 0.93, 0.91), 0.3)
    sooty = toon("Train sooty", (0.6, 0.58, 0.56), 0.2)
    red = toon("Train red", (0.78, 0.1, 0.08), 0.3)
    dark = toon("Train windows", (0.1, 0.12, 0.16), 0.05)
    under = toon("Undercarriage", (0.18, 0.18, 0.2))
    inner = toon("Train inside", (0.75, 0.62, 0.45), 0.1)
    floor_m = toon("Train floor", (0.35, 0.35, 0.38))
    door_m = toon("Sliding door", (0.85, 0.85, 0.83), 0.25)
    shell = sooty if burnt else white
    L = y1 - y0
    yc = (y0 + y1) / 2
    z = z0
    xd = cx + door_side * HALF_W
    xf = cx - door_side * HALF_W
    parts = [box((cx, yc, z + 0.75), (3.0, L - 0.4, 0.5), under, f"{name} undercarriage"),
             box((cx, yc, z + 1.23), (3.1, L, 0.14), floor_m, f"{name} floor"),
             box((cx, yc, z + 4.05), (3.1, L, 0.35), shell, f"{name} roof", bevel=0.12),
             box((xf, yc, z + 2.65), (0.1, L, 2.8), shell, f"{name} far wall"),
             box((xf - door_side * 0.03, yc, z + 1.77), (0.04, L, 0.16), red, f"{name} red stripe"),
             box((xf - door_side * 0.03, yc, z + 2.65), (0.04, L - 1.2, 0.75), dark, f"{name} window band")]
    for ye in (y0, y1):
        parts.append(box((cx, ye, z + 2.65), (3.1, 0.1, 2.8), shell, f"{name} end wall"))
        out = 1 if ye == y1 else -1
        parts.append(box((cx, ye + out * 0.06, z + 1.77), (3.1, 0.04, 0.16), red, f"{name} end stripe"))
        parts.append(box((cx, ye + out * 0.06, z + 2.65), (1.0, 0.04, 0.8), dark, f"{name} end window"))
        for bx in (-1.0, 1.0):
            bpy.ops.mesh.primitive_cylinder_add(radius=0.16, depth=0.35, location=(cx + bx, ye + out * 0.2, z + 1.0),
                                                rotation=(D(90), 0, 0), vertices=14)
            parts.append(finish(bpy.context.object, under, f"{name} buffer", smooth=True))
        parts.append(box((cx, ye + (0.12 if ye == y0 else -0.12), z + 2.65), (3.0, 0.1, 2.75), inner,
                         f"{name} end lining"))
    cuts = sorted((d - 0.65, d + 0.65) for d in door_ys)
    ys = [y0] + [v for c in cuts for v in c] + [y1]
    for a, b in zip(ys[0::2], ys[1::2]):
        parts.append(box((xd, (a + b) / 2, z + 2.65), (0.1, b - a, 2.8), shell, f"{name} side wall"))
        parts.append(box((xd + door_side * 0.03, (a + b) / 2, z + 1.77), (0.04, b - a, 0.16), red, f"{name} stripe"))
        if b - a > 2.5:
            parts.append(box((xd + door_side * 0.03, (a + b) / 2, z + 2.65), (0.04, b - a - 1.0, 0.75), dark,
                             f"{name} window band"))
    # inner lining so the inside reads warm, not white
    parts.append(box((xd - door_side * 0.07, yc, z + 3.75), (0.04, L - 0.3, 0.5), inner, f"{name} lining top"))
    parts.append(box((xf + door_side * 0.07, yc, z + 2.65), (0.04, L - 0.3, 2.7), inner, f"{name} lining far"))
    parts.append(box((cx, yc, z + 3.85), (3.0, L - 0.3, 0.04), inner, f"{name} ceiling"))
    doors = []
    for a, b in cuts:
        parts.append(box((xd, (a + b) / 2, z + 3.7), (0.1, b - a, 0.5), shell, f"{name} above door"))
        parts.append(box((xd + door_side * 0.04, (a + b) / 2, z + 1.15), (0.22, b - a, 0.08), under, f"{name} step"))
        if panels:
            d = box((xd + door_side * 0.09, (a + b) / 2, z + 2.4), (0.06, b - a, 2.3), door_m, f"{name} door",
                    bevel=0.02)
            win = box((xd + door_side * 0.125, (a + b) / 2, z + 2.9), (0.02, (b - a) * 0.6, 0.6), dark,
                      f"{name} door window")
            doors.append((d, win))
    for wy in (y0 + 2.5, y1 - 2.5):
        for wx in (cx - 1.1, cx + 1.1):
            bpy.ops.mesh.primitive_cylinder_add(radius=0.42, depth=0.2, location=(wx, wy, z + 0.42),
                                                rotation=(0, D(90), 0), vertices=20)
            parts.append(finish(bpy.context.object, under, f"{name} wheel", smooth=True))
    if burnt:
        soot = toon("Soot", (0.12, 0.11, 0.11), 0.05)
        rnd = random.Random(int(abs(y0) * 7))
        for k in range(int(6 * burnt)):
            parts.append(ball((xd + door_side * 0.05, rnd.uniform(y0 + 1, y1 - 1), z + rnd.uniform(1.6, 3.8)),
                              rnd.uniform(0.3, 0.7), soot, f"{name} soot", scale=(0.15, 1.6, 1.0)))
    return parts, doors


def rails(x, y0, y1, z0, name="Rails"):
    gravel = toon("Gravel", (0.45, 0.4, 0.36), 0.15)
    steel = toon("Rail steel", (0.55, 0.55, 0.6), 0.25)
    wood = toon("Sleeper", (0.35, 0.24, 0.16), 0.12)
    parts = [box((x, (y0 + y1) / 2, z0 + 0.03), (3.6, y1 - y0, 0.12), gravel, f"{name} bed")]
    for sx in (-0.72, 0.72):
        parts.append(box((x + sx, (y0 + y1) / 2, z0 + 0.17), (0.08, y1 - y0, 0.12), steel, f"{name} rail"))
    y = y0
    while y < y1:
        parts.append(box((x, y, z0 + 0.1), (2.4, 0.22, 0.06), wood, f"{name} sleeper"))
        y += 0.9
    return parts


# ================================================================ render


def setup_render(scene, samples=8, res=(450, 800), sky=(0.78, 0.62, 0.5), sky_strength=0.85):
    world = bpy.data.worlds.new("Sky")
    scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (*sky, 1)
    bg.inputs["Strength"].default_value = sky_strength
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = samples
    scene.cycles.use_denoising = True
    scene.cycles.max_bounces = 4
    scene.cycles.diffuse_bounces = 1
    scene.cycles.glossy_bounces = 0
    scene.cycles.transparent_max_bounces = 4
    scene.render.resolution_x, scene.render.resolution_y = res
    scene.view_settings.view_transform = "Standard"
    scene.render.use_freestyle = True
    scene.render.line_thickness_mode = "ABSOLUTE"
    ls = scene.view_layers[0].freestyle_settings.linesets[0]
    ls.select_silhouette = ls.select_border = ls.select_crease = True
    if ls.linestyle is None:
        ls.linestyle = bpy.data.linestyles.new("Ink")
    ls.linestyle.color = (0.02, 0.02, 0.02)
    ls.linestyle.thickness = 1.5


def make_camera(scene):
    cam_data = bpy.data.cameras.new("POV")
    cam_data.lens = 12
    cam_data.sensor_fit = "VERTICAL"
    cam_data.sensor_height = 36
    cam_data.clip_start = 0.05
    cam = bpy.data.objects.new("POV camera", cam_data)
    bpy.context.collection.objects.link(cam)
    scene.camera = cam
    cam.rotation_mode = "XYZ"
    return cam


def arg(flag):
    if flag in sys.argv:
        i = sys.argv.index(flag)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) and not sys.argv[i + 1].startswith("--") else True
    return None


def run_cli(scene, blend_name):
    """--save, --still a,b,c (global frame numbers), --render [--range a b]"""
    if arg("--save"):
        bpy.ops.wm.save_as_mainfile(filepath=os.path.join(HERE, blend_name))
    if arg("--still"):
        for fr in str(arg("--still")).split(","):
            scene.frame_set(int(fr))
            scene.render.filepath = os.path.join(HERE, "test", f"still_{int(fr):04d}.png")
            bpy.ops.render.render(write_still=True)
    if arg("--render"):
        if arg("--range"):
            i = sys.argv.index("--range")
            scene.frame_start, scene.frame_end = int(sys.argv[i + 1]), int(sys.argv[i + 2])
        scene.render.filepath = os.path.join(HERE, "frames", "f_")
        scene.render.image_settings.file_format = "PNG"
        scene.render.use_overwrite = False  # resume where a previous run stopped
        bpy.ops.render.render(animation=True)
