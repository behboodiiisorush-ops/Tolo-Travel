"""Realistic characters built with MPFB (MakeHuman) for the zombie test.

Needs env: BLENDER_USER_EXTENSIONS (with user_default/mpfb) and MPFB_ASSETS
(unpacked CC0 asset packs). See ../humans/README.md.
"""
import bpy, addon_utils, os, glob, math
from mathutils import Vector, Quaternion

addon_utils.enable("bl_ext.user_default.mpfb", default_set=True)
import bl_ext.user_default.mpfb as _mpfb
from bl_ext.user_default.mpfb.services.humanservice import HumanService
from bl_ext.user_default.mpfb.services.targetservice import TargetService

A = os.environ["MPFB_ASSETS"]
EXPR = os.path.join(os.path.dirname(_mpfb.__file__), "data/targets/expression/units/caucasian")


# ---------------------------------------------------------------- materials
def _tex_color_links(mat):
    nt = mat.node_tree
    out = []
    for n in nt.nodes:
        if n.type == "TEX_IMAGE" and n.image and "normal" not in n.image.name.lower() \
                and "bump" not in n.image.name.lower():
            for l in list(nt.links):
                if l.from_node == n and l.from_socket.name == "Color":
                    out.append((n, l))
    return out


def recolor(obj, build):
    """build(nt, color_socket) -> new color socket; spliced after every colour texture."""
    for ms in obj.material_slots:
        m = ms.material
        if not m or not m.node_tree:
            continue
        for n, l in _tex_color_links(m):
            to = l.to_socket
            nt = m.node_tree
            nt.links.remove(l)
            nt.links.new(build(nt, n.outputs["Color"]), to)


def mix(nt, a, b, fac, mode="MIX"):
    m = nt.nodes.new("ShaderNodeMix")
    m.data_type = "RGBA"
    m.blend_type = mode
    if isinstance(fac, float):
        m.inputs[0].default_value = fac
    else:
        nt.links.new(fac, m.inputs[0])
    for i, v in ((6, a), (7, b)):
        if isinstance(v, tuple):
            m.inputs[i].default_value = v
        else:
            nt.links.new(v, m.inputs[i])
    return m.outputs[2]


def noise_mask(nt, scale, lo, hi, detail=6.0, kind="noise"):
    if kind == "voronoi":
        t = nt.nodes.new("ShaderNodeTexVoronoi")
        t.inputs["Scale"].default_value = scale
        val = t.outputs["Distance"]
    else:
        t = nt.nodes.new("ShaderNodeTexNoise")
        t.inputs["Scale"].default_value = scale
        t.inputs["Detail"].default_value = detail
        val = t.outputs["Fac"]
    r = nt.nodes.new("ShaderNodeMapRange")
    r.inputs["From Min"].default_value = lo
    r.inputs["From Max"].default_value = hi
    nt.links.new(val, r.inputs["Value"])
    return r.outputs["Result"]


def tint(obj, rgb, amount=1.0):
    recolor(obj, lambda nt, c: mix(nt, c, rgb + (1,), amount, "MULTIPLY"))


def zombie_skin(obj):
    def b(nt, c):
        c = mix(nt, c, (0.62, 0.6, 0.55, 1), 0.8, "SATURATION")       # washed out
        c = mix(nt, c, (0.5, 0.56, 0.46, 1), 1.0, "MULTIPLY")         # grey-green
        bruise = noise_mask(nt, 6.0, 0.5, 0.75)
        c = mix(nt, c, (0.22, 0.2, 0.28, 1), bruise)                  # bruises
        blood = noise_mask(nt, 14.0, 0.58, 0.66, 10.0)
        c = mix(nt, c, (0.16, 0.01, 0.01, 1), blood)                  # dried blood
        return c
    recolor(obj, b)


def dirty_cloth(obj, base):
    def b(nt, c):
        c = mix(nt, c, base + (1,), 0.7)
        dirt = noise_mask(nt, 3.0, 0.4, 0.7)
        c = mix(nt, c, (0.12, 0.09, 0.06, 1), dirt)
        blood = noise_mask(nt, 9.0, 0.64, 0.7, 10.0)
        c = mix(nt, c, (0.13, 0.01, 0.01, 1), blood)
        return c
    recolor(obj, b)


def dead_eyes(obj):
    recolor(obj, lambda nt, c: mix(nt, c, (0.82, 0.8, 0.72, 1), 0.88))


# ---------------------------------------------------------------- humans
def _mhclo(kind, name):
    d = os.path.join(A, kind, name)
    return glob.glob(os.path.join(d, "*.mhclo"))[0]


def build(name, *, gender, age, height=0.5, weight=0.45, muscle=0.45,
          skin, hair, brow, clothes, race=(0.15, 0.65, 0.2)):
    m = TargetService.get_default_macro_info_dict()
    m.update(gender=gender, age=age, height=height, weight=weight, muscle=muscle)
    m["race"] = {"asian": race[0], "caucasian": race[1], "african": race[2]}
    body = HumanService.create_human(macro_detail_dict=m)
    body.name = name
    rig = HumanService.add_builtin_rig(body, "game_engine")
    rig.name = name + "_rig"
    HumanService.set_character_skin(f"{A}/skins/{skin}/{skin}.mhmat", body, skin_type="ENHANCED_SSS")
    parts = {}

    def add(kind, asset, t):
        before = set(bpy.data.objects)
        HumanService.add_mhclo_asset(_mhclo(kind, asset), body, asset_type=t,
                                     subdiv_levels=1, material_type="MAKESKIN")
        parts.setdefault(t, []).extend(o for o in bpy.data.objects if o not in before)

    add("eyes", "high-poly", "Eyes")
    add("eyebrows", brow, "Eyebrows")
    add("eyelashes", "eyelashes01", "Eyelashes")
    add("teeth", "teeth_base", "Teeth")
    if hair:
        add("hair", hair, "Hair")
    for c in clothes:
        add("clothes", c, "Clothes")
    return body, rig, parts


def add_expr(body, names):
    keys = {}
    for n in names:
        TargetService.load_target(body, os.path.join(EXPR, n + ".target.gz"), weight=0.0, name=n)
        keys[n] = body.data.shape_keys.key_blocks[n]
    return keys


# ---------------------------------------------------------------- posing
def q(pb, axis, deg):
    """Rotation about an armature-space axis, expressed in the bone's rest space."""
    M = pb.bone.matrix_local.to_3x3().inverted()
    return Quaternion((M @ Vector(axis)).normalized(), math.radians(deg))


X, Y, Z = (1, 0, 0), (0, 1, 0), (0, 0, 1)


def pose(rig, spec):
    """spec: bone -> list of (axis, deg). Sets rotation_quaternion."""
    for pb in rig.pose.bones:
        pb.rotation_mode = "QUATERNION"
    for b, rots in spec.items():
        pb = rig.pose.bones.get(b)
        if pb is None:
            continue
        r = Quaternion()
        for ax, d in rots:
            r = q(pb, ax, d) @ r
        pb.rotation_quaternion = r


def key_pose(rig, frame):
    for pb in rig.pose.bones:
        pb.keyframe_insert("rotation_quaternion", frame=frame)
