"""Shared building blocks for the POV films (copied from train_pov for «زنگ آخر»): materials, primitives, puppet characters,
POV arms, dialogue timing and render settings."""

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

    def __init__(self, cam, sleeve_col=(0.16, 0.42, 0.2), cuff_col=(0.92, 0.86, 0.66)):
        self.cam = cam
        sleeve = toon("POV sleeve", sleeve_col, 0.3)
        cuff = toon("POV cuff", cuff_col, 0.35)
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
            pupil_m = toon(f"{name} pupil", L["pupil"], 0.3) if L.get("pupil") else ink
            self.add(ball(ec + Vector((0, 0.15 * R, -0.02 * R)), 0.085 * R * eye_sz, pupil_m, f"pupil {side}",
                          scale=(1, 0.5, 1.2), seg=12), head)
            if not L.get("pupil"):
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
