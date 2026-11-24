"""Hand-built stylized cartoon people (no MakeHuman): smooth skin-modifier bodies, simple cartoon heads
(big white eyes with black pupils, bold brows, small nose, line mouth), cap hair, flat-colour clothes.

The armature uses the same bone names / rest pose (A-pose, facing -Y) as the MPFB game_engine rig,
so anim.pose_spec() and the whole animation library work unchanged.

    import toon_people as T
    arian = T.spawn("arian")
    arian.animate(frame, t, pos, facing, walk=1, phase=..., arms="rest", worry=1.2, talking=0.5)
    arian.flush()
"""
import bpy, math
from mathutils import Vector, Matrix
import anim
import props as P

X, Y, Z = (1, 0, 0), (0, 1, 0), (0, 0, 1)

# ------------------------------------------------------------------ looks (sRGB colours)
LOOKS = {
    "me":     dict(h=1.66, skin=(0.86, 0.66, 0.52), hair=(0.09, 0.07, 0.06), hair_style="side",
                   top=(0.18, 0.24, 0.4), pants=(0.2, 0.22, 0.28), shoes=(0.9, 0.9, 0.88), hood=True),
    "arian":  dict(h=1.72, skin=(0.84, 0.64, 0.5), hair=(0.07, 0.06, 0.05), hair_style="messy",
                   top=(0.3, 0.38, 0.55), pants=(0.15, 0.18, 0.26), shoes=(0.92, 0.92, 0.9), collar=True),
    "mahsa":  dict(h=1.6, skin=(0.9, 0.72, 0.6), hair=(0.06, 0.05, 0.05), hair_style="ponytail", female=True,
                   top=(0.14, 0.17, 0.32), pants=(0.3, 0.3, 0.34), shoes=(0.55, 0.12, 0.15), glasses=(0.6, 0.1, 0.12)),
    "kian":   dict(h=1.5, skin=(0.92, 0.75, 0.62), hair=(0.3, 0.18, 0.1), hair_style="messy",
                   top=(0.42, 0.6, 0.75), pants=(0.2, 0.25, 0.36), shoes=(0.9, 0.9, 0.88), hood=True),
    "mom":    dict(h=1.62, skin=(0.86, 0.68, 0.55), hair=(0.16, 0.09, 0.06), hair_style="bun", female=True,
                   top=(0.42, 0.15, 0.17), pants=(0.1, 0.1, 0.12), shoes=(0.08, 0.08, 0.08)),
    "kazemi": dict(h=1.74, skin=(0.82, 0.62, 0.48), hair=(0.42, 0.4, 0.38), hair_style="short", adult=True,
                   top=(0.38, 0.27, 0.18), pants=(0.3, 0.27, 0.24), shoes=(0.15, 0.1, 0.07), glasses=(0.05, 0.05, 0.05)),
    "rezaei": dict(h=1.72, skin=(0.8, 0.62, 0.48), hair=(0.58, 0.57, 0.56), hair_style="short", adult=True,
                   top=(0.22, 0.34, 0.58), pants=(0.22, 0.34, 0.58), shoes=(0.12, 0.1, 0.08)),
    "soldier": dict(h=1.8, skin=(0.82, 0.63, 0.5), hair=(0.07, 0.06, 0.05), hair_style="short", adult=True,
                    top=(0.28, 0.32, 0.2), pants=(0.28, 0.32, 0.2), shoes=(0.1, 0.1, 0.08), helmet=(0.26, 0.3, 0.18)),
}
ZOMBIE_SKIN = (0.58, 0.66, 0.55)


def _mat(name, rgb, rough=0.6, folds=False):
    m = P.mat(name, rgb, rough)
    if folds:   # soft fabric folds: stretched noise as bump (reads as creases under cel shading)
        nt = m.node_tree
        b = nt.nodes["Principled BSDF"]
        tc = nt.nodes.new("ShaderNodeTexCoord")
        mp = nt.nodes.new("ShaderNodeMapping")
        mp.inputs["Scale"].default_value = (9.0, 9.0, 3.0)
        nt.links.new(tc.outputs["Object"], mp.inputs["Vector"])
        nz = nt.nodes.new("ShaderNodeTexNoise")
        nz.inputs["Scale"].default_value = 2.5
        nz.inputs["Detail"].default_value = 3
        nt.links.new(mp.outputs[0], nz.inputs["Vector"])
        bp = nt.nodes.new("ShaderNodeBump")
        bp.inputs["Strength"].default_value = 0.35
        nt.links.new(nz.outputs["Fac"], bp.inputs["Height"])
        nt.links.new(bp.outputs["Normal"], b.inputs["Normal"])
    return m


# ------------------------------------------------------------------ skeleton (A-pose, facing -Y)
def skeleton(h, female=False):
    k = h / 1.7
    sh = 0.165 if not female else 0.15
    hip = 0.09 if not female else 0.095
    J = {
        "pelvis": (0, 0, 0.95), "spine_01": (0, 0, 1.03), "spine_02": (0, 0, 1.16), "spine_03": (0, 0, 1.3),
        "neck_01": (0, 0, 1.44), "head": (0, 0, 1.5), "head_top": (0, 0, 1.76),
        "clavicle_l": (0.03, 0, 1.4), "upperarm_l": (sh, 0.0, 1.4), "lowerarm_l": (sh + 0.22, 0.0, 1.235),
        "hand_l": (sh + 0.42, -0.01, 1.085), "hand_tip_l": (sh + 0.49, -0.015, 1.035),
        "thigh_l": (hip, 0, 0.93), "calf_l": (hip + 0.01, 0, 0.5), "foot_l": (hip + 0.01, 0.02, 0.09),
        "toe_l": (hip + 0.01, -0.12, 0.02),
    }
    for key in list(J):
        if key.endswith("_l"):
            x, y, z = J[key]
            J[key[:-2] + "_r"] = (-x, y, z)
    return {n: Vector(v) * k for n, v in J.items()}


BONES = [  # name, head joint, tail joint, parent
    ("pelvis", "pelvis", "spine_01", None), ("spine_01", "spine_01", "spine_02", "pelvis"),
    ("spine_02", "spine_02", "spine_03", "spine_01"), ("spine_03", "spine_03", "neck_01", "spine_02"),
    ("neck_01", "neck_01", "head", "spine_03"), ("head", "head", "head_top", "neck_01"),
]
for s in ("l", "r"):
    BONES += [(f"clavicle_{s}", f"clavicle_{s}", f"upperarm_{s}", "spine_03"),
              (f"upperarm_{s}", f"upperarm_{s}", f"lowerarm_{s}", f"clavicle_{s}"),
              (f"lowerarm_{s}", f"lowerarm_{s}", f"hand_{s}", f"upperarm_{s}"),
              (f"hand_{s}", f"hand_{s}", f"hand_tip_{s}", f"lowerarm_{s}"),
              (f"thigh_{s}", f"thigh_{s}", f"calf_{s}", "pelvis"),
              (f"calf_{s}", f"calf_{s}", f"foot_{s}", f"thigh_{s}"),
              (f"foot_{s}", f"foot_{s}", f"toe_{s}", f"calf_{s}")]


def build_rig(name, J):
    arm = bpy.data.armatures.new(name + "_arm")
    rig = bpy.data.objects.new(name + "_rig", arm)
    bpy.context.scene.collection.objects.link(rig)
    bpy.context.view_layer.objects.active = rig
    bpy.ops.object.mode_set(mode="EDIT")
    eb = {}
    for n, a, b, par in BONES:
        e = arm.edit_bones.new(n)
        e.head, e.tail = J[a], J[b]
        if par:
            e.parent = eb[par]
            e.use_connect = False
        eb[n] = e
    bpy.ops.object.mode_set(mode="OBJECT")
    return rig


# ------------------------------------------------------------------ meshes
def skin_mesh(name, pts, edges, radii, mat, levels=2):
    """Organic tube mesh from a joint graph (skin modifier), returned as a real mesh."""
    me = bpy.data.meshes.new(name)
    me.from_pydata([tuple(p) for p in pts], edges, [])
    o = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(o)
    o.modifiers.new("skin", "SKIN")
    for i, r in enumerate(radii):
        sv = me.skin_vertices[0].data[i]
        sv.radius = r if isinstance(r, tuple) else (r, r)
    me.skin_vertices[0].data[0].use_root = True
    sub = o.modifiers.new("sub", "SUBSURF")
    sub.levels = sub.render_levels = levels
    bpy.context.view_layer.objects.active = o
    for ob in bpy.context.selected_objects:
        ob.select_set(False)
    o.select_set(True)
    bpy.ops.object.convert(target="MESH")
    o = bpy.context.object
    o.data.materials.append(mat)
    bpy.ops.object.shade_smooth()
    return o


def blob(name, loc, size, mat, segs=24):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=loc, segments=segs, ring_count=segs // 2)
    o = bpy.context.object
    o.name = name
    o.scale = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(mat)
    bpy.ops.object.shade_smooth()
    return o


def bone_parent(o, rig, bone):
    """Rigidly bind a part to one bone: full-weight vertex group + Armature modifier (object stays world-aligned,
    so its own scale/location animation works around its centre)."""
    vg = o.vertex_groups.new(name=bone)
    vg.add(list(range(len(o.data.vertices))), 1.0, "REPLACE")
    md = o.modifiers.new("Armature", "ARMATURE")
    md.object = rig
    o.parent = rig
    o.matrix_parent_inverse = rig.matrix_world.inverted()


def auto_skin(o, rig):
    for ob in bpy.context.selected_objects:
        ob.select_set(False)
    o.select_set(True)
    rig.select_set(True)
    bpy.context.view_layer.objects.active = rig
    bpy.ops.object.parent_set(type="ARMATURE_AUTO")


# ------------------------------------------------------------------ character
class ToonCharacter:
    def __init__(self, key, look, name=None, zombie=0.0):
        self.key = key
        self.name = name or key.capitalize()
        self.look = look
        self.zombie = zombie
        self.seed = sum(map(ord, self.name)) % 97
        self._rec = {}
        h = look["h"]
        J = skeleton(h, look.get("female"))
        self.J = J
        self.rig = rig = build_rig(self.name, J)
        skin_rgb = ZOMBIE_SKIN if zombie else look["skin"]
        m_skin = _mat(f"{self.name} skin", skin_rgb, 0.7)
        m_top = _mat(f"{self.name} top", look["top"], 0.85, folds=True)
        m_pants = _mat(f"{self.name} pants", look["pants"], 0.85, folds=True)
        m_shoes = _mat(f"{self.name} shoes", look["shoes"], 0.6)
        m_hair = _mat(f"{self.name} hair", look["hair"], 0.7)
        m_dark = _mat(f"{self.name} dark", (0.03, 0.025, 0.025), 0.5)
        m_white = _mat(f"{self.name} eye white", (0.96, 0.95, 0.92), 0.3)
        female = look.get("female")
        w = 1.0 if not female else 0.9
        # --- torso (top) + separate arm tubes, hips + separate leg tubes (no branch artefacts)
        cpos = [J["pelvis"], J["spine_01"], J["spine_02"], J["spine_03"],
                (J["spine_03"] + J["neck_01"]) / 2 + Vector((0, 0, 0.05))]
        self.top = skin_mesh(f"{self.name} top", cpos, [(0, 1), (1, 2), (2, 3), (3, 4)],
                             [(0.15 * w, 0.11), (0.145 * w, 0.105), (0.16 * w, 0.11), (0.172 * w, 0.115), (0.07, 0.065)], m_top)
        self.arms = []
        for sd in ("l", "r"):
            sh = J[f"upperarm_{sd}"] + Vector((-0.025 if sd == "l" else 0.025, 0, -0.02))
            self.arms.append(skin_mesh(f"{self.name} sleeve {sd}", [sh, J[f"lowerarm_{sd}"], J[f"hand_{sd}"]],
                                       [(0, 1), (1, 2)], [(0.07, 0.07), (0.058, 0.058), (0.046, 0.046)], m_top))
        self.legs = blob(f"{self.name} hips", J["pelvis"] + Vector((0, 0, -0.02)), (0.15 * w, 0.11, 0.12), m_pants)
        band = blob(f"{self.name} waistband", J["pelvis"] + Vector((0, 0, 0.07)), (0.152 * w, 0.112, 0.022),
                    _mat(f"{self.name} belt", tuple(c * 0.6 for c in look["pants"]), 0.6))
        bone_parent(band, rig, "pelvis")
        self.leg_tubes = []
        for sd in ("l", "r"):
            self.leg_tubes.append(skin_mesh(f"{self.name} leg {sd}", [J[f"thigh_{sd}"] + Vector((0, 0, 0.04)), J[f"calf_{sd}"],
                                                                      J[f"foot_{sd}"]], [(0, 1), (1, 2)],
                                            [(0.098, 0.098), (0.07, 0.07), (0.058, 0.058)], m_pants))
        for o in [self.top] + self.arms + self.leg_tubes:
            auto_skin(o, rig)
        bone_parent(self.legs, rig, "pelvis")
        self.objects = [rig, self.top, self.legs, band] + self.arms + self.leg_tubes
        # --- hands, shoes, neck
        for s in ("l", "r"):
            sx = 1 if s == "l" else -1
            hp = J[f"hand_{s}"] + (J[f"hand_tip_{s}"] - J[f"hand_{s}"]) * 0.5
            palm = blob(f"{self.name} hand {s}", hp, (0.038, 0.05, 0.062), m_skin)
            thumb = blob(f"{self.name} thumb {s}", hp + Vector((-0.012 * sx, -0.045, 0.025)), (0.017, 0.017, 0.036), m_skin)
            cuff = blob(f"{self.name} cuff {s}", J[f"hand_{s}"], (0.05, 0.05, 0.03), m_top)
            for o in (palm, thumb, cuff):
                bone_parent(o, rig, f"hand_{s}")
                self.objects.append(o)
            fc = (J[f"foot_{s}"] + J[f"toe_{s}"]) / 2
            sh = blob(f"{self.name} shoe {s}", fc + Vector((0, 0, 0.0)), (0.058, 0.13, 0.055), m_shoes)
            sole = blob(f"{self.name} sole {s}", fc + Vector((0, 0, -0.03)), (0.062, 0.135, 0.022),
                        _mat(f"{self.name} sole", (0.2, 0.2, 0.22), 0.7))
            for o in (sh, sole):
                bone_parent(o, rig, f"foot_{s}")
                self.objects.append(o)
        neck = blob(f"{self.name} neck", J["neck_01"] + Vector((0, 0, 0.03)), (0.05, 0.05, 0.07), m_skin)
        bone_parent(neck, rig, "neck_01")
        self.objects.append(neck)
        # --- head
        hc = J["head"] + Vector((0, -0.005, 0.135 * h / 1.7))
        R = 0.136 * h / 1.7
        head = blob(f"{self.name} head", hc, (R * 0.92, R * 0.98, R * 1.1), m_skin, 32)
        jaw = blob(f"{self.name} jaw", hc + Vector((0, -0.02, -0.06)), (R * 0.7, R * 0.72, R * 0.65), m_skin)
        nose = blob(f"{self.name} nose", hc + Vector((0, -R * 0.98, -R * 0.12)), (R * 0.12, R * 0.14, R * 0.16), m_skin)
        parts = [head, jaw, nose]
        for s in (1, -1):
            parts.append(blob(f"{self.name} ear", hc + Vector((s * R * 0.92, 0.0, -R * 0.08)), (R * 0.12, R * 0.08, R * 0.2), m_skin))
        # eyes: big whites + black pupils + tiny highlight
        self.eyes, self.pupils, self.brows = [], [], []
        m_glint = P.emit(f"{self.name} glint", (1, 1, 1), 2.0)
        for s in (1, -1):
            ec = hc + Vector((s * R * 0.36, -R * 0.86, R * 0.08))
            white = blob(f"{self.name} eye", ec, (R * 0.25, R * 0.12, R * 0.3), m_white)
            pupil = blob(f"{self.name} pupil", ec + Vector((0, -R * 0.1, -R * 0.02)), (R * 0.13, R * 0.05, R * 0.17),
                         m_white if zombie else m_dark)
            glint = blob(f"{self.name} glint", ec + Vector((s * R * 0.04, -R * 0.15, R * 0.06)), (R * 0.035,) * 3, m_glint, 8)
            brow = blob(f"{self.name} brow", ec + Vector((0, -R * 0.06, R * 0.38)), (R * 0.27, R * 0.06, R * 0.065),
                        _mat(f"{self.name} brow", look["hair"] if not look.get("adult") else (0.1, 0.09, 0.08), 0.6))
            brow.rotation_euler = (0, s * math.radians(4), 0)
            bpy.context.view_layer.objects.active = brow
            for ob in bpy.context.selected_objects:
                ob.select_set(False)
            brow.select_set(True)
            bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
            self.eyes.append(white)
            self.pupils.append(pupil)
            self.brows.append(brow)
            parts += [white, pupil, brow] + ([] if zombie else [glint])
            if zombie:
                bpy.data.objects.remove(glint)
        self.mouth = blob(f"{self.name} mouth", hc + Vector((0, -R * 0.9, -R * 0.5)), (R * 0.26, R * 0.05, R * 0.05),
                          _mat(f"{self.name} mouth", (0.25, 0.06, 0.07) if not zombie else (0.3, 0.02, 0.02), 0.5))
        parts.append(self.mouth)
        parts += self._hair(hc, R, m_hair)
        if look.get("glasses"):
            parts += self._glasses(hc, R, _mat(f"{self.name} frames", look["glasses"], 0.3))
        if look.get("helmet"):
            parts.append(blob(f"{self.name} helmet", hc + Vector((0, 0.01, R * 0.35)), (R * 1.15, R * 1.2, R * 0.85),
                              _mat(f"{self.name} helmet", look["helmet"], 0.6)))
        if look.get("collar"):
            parts.append(blob(f"{self.name} collar", J["neck_01"] + Vector((0, 0.0, -0.01)), (0.08, 0.075, 0.03), m_top))
        if look.get("hood"):
            parts.append(blob(f"{self.name} hood", J["spine_03"] + Vector((0, 0.08, 0.12)), (0.13, 0.07, 0.07), m_top))
        for o in parts:
            bone_parent(o, rig, "head" if o.name.split()[1] not in ("collar", "hood") else "spine_03")
        self.objects += parts
        self.face_parts = [o for o in parts if o not in (head, jaw)]
        if zombie:
            self._blood(m_top)
        pb = rig.pose.bones
        self.thigh_len = (pb["thigh_l"].bone.head_local - pb["calf_l"].bone.head_local).length
        self.calf_len = (pb["calf_l"].bone.head_local - pb["foot_l"].bone.head_local).length
        self.base = {o.name: (o.location.copy(), o.scale.copy(), o.rotation_euler.copy()) for o in
                     self.eyes + self.pupils + self.brows + [self.mouth]}

    # ---- pieces
    def _hair(self, hc, R, m):
        st = self.look["hair_style"]
        out = [blob(f"{self.name} hair", hc + Vector((0, R * 0.12, R * 0.2)), (R * 1.0, R * 1.02, R * 0.95), m, 32)]
        if st in ("messy", "side", "short"):
            n = {"messy": 9, "side": 6, "short": 4}[st]
            for i in range(n):
                a = -1.2 + 2.4 * i / max(1, n - 1)
                out.append(blob(f"{self.name} hair", hc + Vector((math.sin(a) * R * 0.6, -R * 0.55 + abs(a) * 0.02,
                                                                    R * (0.75 + 0.08 * math.cos(i * 2.3)))),
                                (R * 0.32, R * 0.3, R * 0.22), m, 16))
        if st == "side":
            out.append(blob(f"{self.name} hair", hc + Vector((R * 0.25, -R * 0.7, R * 0.55)), (R * 0.55, R * 0.25, R * 0.25), m))
        if st == "ponytail":
            out.append(blob(f"{self.name} hair", hc + Vector((0, R * 1.0, R * 0.1)), (R * 0.25, R * 0.25, R * 0.25), m))
            out.append(blob(f"{self.name} hair", hc + Vector((0, R * 1.15, -R * 0.45)), (R * 0.2, R * 0.2, R * 0.55), m))
            out.append(blob(f"{self.name} hair", hc + Vector((0, -R * 0.55, R * 0.72)), (R * 0.85, R * 0.35, R * 0.3), m))
        if st == "bun":
            out.append(blob(f"{self.name} hair", hc + Vector((0, R * 0.95, R * 0.05)), (R * 0.38, R * 0.32, R * 0.36), m))
            out.append(blob(f"{self.name} hair", hc + Vector((0, -R * 0.5, R * 0.72)), (R * 0.85, R * 0.35, R * 0.3), m))
        return out

    def _glasses(self, hc, R, m):
        out = []
        for s in (1, -1):
            ec = hc + Vector((s * R * 0.36, -R * 1.0, R * 0.08))
            bpy.ops.mesh.primitive_torus_add(location=ec, rotation=(math.pi / 2, 0, 0), major_radius=R * 0.28,
                                             minor_radius=R * 0.03)
            o = bpy.context.object
            o.name = f"{self.name} glasses"
            o.data.materials.append(m)
            out.append(o)
        return out

    def _blood(self, m_top):
        red = _mat(f"{self.name} blood", (0.35, 0.03, 0.03), 0.3)
        J = self.J
        for i, (off, sz) in enumerate((((0.04, -0.1, 1.28), (0.06, 0.02, 0.09)), ((-0.06, -0.11, 1.15), (0.05, 0.02, 0.05)),
                                       ((0.0, -0.105, 1.38), (0.07, 0.02, 0.04)))):
            o = blob(f"{self.name} blood", Vector(off) * (self.look["h"] / 1.7), sz, red, 12)
            bone_parent(o, self.rig, "spine_03")
            self.objects.append(o)

    # ---- animation (same interface as cast.Character)
    def _put(self, owner, path, idx, frame, value):
        self._rec.setdefault((owner.name, path, idx), (owner, []))[1].append((frame, value))

    def hide(self, frame, hidden):
        for o in self.objects:
            self._put(o, "hide_render", 0, frame, float(hidden))

    def head_world(self):
        return self.rig.matrix_world @ self.rig.pose.bones["head"].head

    def flush(self):
        import cast
        for (_, path, idx), (owner, pts) in self._rec.items():
            cast.write_fcurve(owner, path, idx, pts, constant=(path == "hide_render"))
        self._rec = {}


def _apply_spec(rig, spec):
    from mathutils import Quaternion
    for pb in rig.pose.bones:
        pb.rotation_mode = "QUATERNION"
        d = spec.get(pb.name)
        r = Quaternion()
        if d:
            for a in ("y", "x", "z"):
                v = d.get(a, 0.0)
                if v:
                    M = pb.bone.matrix_local.to_3x3().inverted()
                    r = Quaternion((M @ Vector({"x": X, "y": Y, "z": Z}[a])).normalized(), math.radians(v)) @ r
        pb.rotation_quaternion = r


def _animate(self, frame, t, pos, facing=0.0, z_extra=0.0, scale=1.0, **st):
    st.setdefault("t", t)
    st.setdefault("seed", self.seed)
    spec = anim.pose_spec(st)
    ext = anim.leg_extent(spec, self.thigh_len, self.calf_len)
    drop = ext - (self.thigh_len + self.calf_len)
    loc = Vector(pos) + Vector((0, 0, drop + z_extra))
    for i in range(3):
        self._put(self.rig, "location", i, frame, loc[i])
    self._put(self.rig, "rotation_euler", 2, frame, math.radians(facing) + math.pi)
    _apply_spec(self.rig, spec)
    prev = getattr(self, "_prevq", {})
    for pb in self.rig.pose.bones:
        qq = pb.rotation_quaternion.copy()
        p0 = prev.get(pb.name)
        if p0 is not None and p0.dot(qq) < 0:
            qq.negate()
        prev[pb.name] = qq
        for i in range(4):
            self._put(self.rig, f'pose.bones["{pb.name}"].rotation_quaternion', i, frame, qq[i])
    self._prevq = prev
    # cartoon face: mouth opens, eyes blink / widen, brows lift
    fst = dict(st)
    fst.setdefault("zombie", self.zombie)
    fv = anim.face(fst)
    mouth = fv["mouth-open"]
    blink = fv["eye-left-closure"]
    wide = fv["eye-left-opened-up"]
    up = fv["eyebrows-left-inner-up"]
    down = fv["eyebrows-left-down"]
    loc0, sc0, rot0 = self.base[self.mouth.name]
    self._put(self.mouth, "scale", 2, frame, sc0[2] * (1 + 5.5 * mouth))
    self._put(self.mouth, "scale", 0, frame, sc0[0] * (1 - 0.25 * mouth))
    for o in self.eyes + self.pupils:
        l0, s0, r0 = self.base[o.name]
        self._put(o, "scale", 2, frame, s0[2] * max(0.08, (1 - blink)) * (1 + 0.18 * wide))
    for k, o in enumerate(self.brows):
        l0, s0, r0 = self.base[o.name]
        s = 1 if k == 0 else -1
        self._put(o, "location", 2, frame, l0[2] + 0.012 * up - 0.008 * down)
        self._put(o, "delta_rotation_euler", 1, frame, s * math.radians(-20 * up + 18 * down))


ToonCharacter.animate = _animate


def spawn(key, zombie=0.0, name=None):
    return ToonCharacter(key, LOOKS[key], name=name, zombie=zombie)
