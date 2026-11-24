"""Low-level helpers: build MPFB (MakeHuman) humans, recolour their materials,
paint masks (blood, bruises) and pose the game_engine rig.

Run scripts through blender/cast/bpy.sh so MPFB and the assets are found.
"""
import bpy, addon_utils, os, glob, math, random
from mathutils import Vector, Quaternion, Matrix

addon_utils.enable("bl_ext.user_default.mpfb", default_set=True)
import bl_ext.user_default.mpfb as _mpfb  # noqa: E402
from bl_ext.user_default.mpfb.services.humanservice import HumanService  # noqa: E402
from bl_ext.user_default.mpfb.services.targetservice import TargetService  # noqa: E402

A = os.environ["MPFB_ASSETS"]
EXPR = os.path.join(os.path.dirname(_mpfb.__file__), "data/targets/expression/units/caucasian")
X, Y, Z = (1, 0, 0), (0, 1, 0), (0, 0, 1)


# ================================================================ node helpers
def mix(nt, a, b, fac, mode="MIX"):
    m = nt.nodes.new("ShaderNodeMix")
    m.data_type = "RGBA"
    m.blend_type = mode
    if isinstance(fac, (int, float)):
        m.inputs[0].default_value = fac
    else:
        nt.links.new(fac, m.inputs[0])
    for i, v in ((6, a), (7, b)):
        if isinstance(v, tuple):
            m.inputs[i].default_value = v if len(v) == 4 else v + (1,)
        else:
            nt.links.new(v, m.inputs[i])
    return m.outputs[2]


def noise_mask(nt, scale, lo, hi, detail=6.0, coords=None, kind="noise"):
    if kind == "voronoi":
        t = nt.nodes.new("ShaderNodeTexVoronoi")
        t.inputs["Scale"].default_value = scale
        val = t.outputs["Distance"]
    elif kind == "edges":
        t = nt.nodes.new("ShaderNodeTexVoronoi")
        t.feature = "DISTANCE_TO_EDGE"
        t.inputs["Scale"].default_value = scale
        val = t.outputs["Distance"]
    elif kind == "wave":
        t = nt.nodes.new("ShaderNodeTexWave")
        t.inputs["Scale"].default_value = scale
        t.inputs["Distortion"].default_value = 12
        t.inputs["Detail"].default_value = 4
        val = t.outputs["Fac"]
    else:
        t = nt.nodes.new("ShaderNodeTexNoise")
        t.inputs["Scale"].default_value = scale
        t.inputs["Detail"].default_value = detail
        val = t.outputs["Fac"]
    if coords is not None:
        nt.links.new(coords, t.inputs["Vector"])
    r = nt.nodes.new("ShaderNodeMapRange")
    r.inputs["From Min"].default_value = lo
    r.inputs["From Max"].default_value = hi
    nt.links.new(val, r.inputs["Value"])
    return r.outputs["Result"]


def obj_coords(nt):
    tc = nt.nodes.new("ShaderNodeTexCoord")
    return tc.outputs["Object"]


def attr(nt, name):
    a = nt.nodes.new("ShaderNodeAttribute")
    a.attribute_name = name
    sep = nt.nodes.new("ShaderNodeSeparateColor")
    nt.links.new(a.outputs["Color"], sep.inputs["Color"])
    return sep.outputs


def _color_links(mat):
    nt = mat.node_tree if hasattr(mat, "node_tree") else mat
    out = []
    for n in nt.nodes:
        if n.type == "TEX_IMAGE" and n.image:
            nm = n.image.name.lower()
            if any(k in nm for k in ("normal", "bump", "_nm", "nrm", "norm", "rough", "spec", "displ", "sss", "_ao")):
                continue
            for l in list(nt.links):
                if l.from_node == n and l.from_socket.name == "Color" \
                        and l.to_node.type not in ("NORMAL_MAP", "BUMP") \
                        and l.to_socket.name not in ("Normal", "Roughness", "Metallic", "Alpha", "Specular IOR Level"):
                    out.append((n, l))
    return out


def recolor(obj, build):
    """build(nt, colour_socket) -> new colour socket, spliced after every colour texture."""
    done = set()
    for ms in obj.material_slots:
        m = ms.material
        if not m or not m.node_tree or ("M", m.name) in done:
            continue
        done.add(("M", m.name))
        trees = [m.node_tree] + [n.node_tree for n in m.node_tree.nodes
                                 if n.type == "GROUP" and n.node_tree and ("G", n.node_tree.name) not in done]
        for g in trees[1:]:
            done.add(("G", g.name))
            for n, l in _color_links(g):
                to = l.to_socket
                g.links.remove(l)
                g.links.new(build(g, n.outputs["Color"]), to)
        links = _color_links(m)
        if not links and len(trees) == 1:  # untextured material: tint the BSDF base colour
            for n in m.node_tree.nodes:
                if n.type == "BSDF_PRINCIPLED" and not n.inputs["Base Color"].is_linked:
                    c = tuple(n.inputs["Base Color"].default_value)
                    sock = mix(m.node_tree, c, c, 0.0)
                    m.node_tree.links.new(build(m.node_tree, sock), n.inputs["Base Color"])
        for n, l in links:
            to = l.to_socket
            nt = m.node_tree
            nt.links.remove(l)
            nt.links.new(build(nt, n.outputs["Color"]), to)


def recolor_bsdf(obj, build):
    """build(nt, bsdf, colour_socket) -> new colour socket for every Principled BSDF's Base Color
    (main trees and node groups). build may also rewire other bsdf inputs (roughness...)."""
    done = set()
    for ms in obj.material_slots:
        m = ms.material
        if not m or not m.node_tree or ("M", m.name) in done:
            continue
        done.add(("M", m.name))
        trees = [m.node_tree] + [n.node_tree for n in m.node_tree.nodes
                                 if n.type == "GROUP" and n.node_tree and ("G", n.node_tree.name) not in done]
        for nt in trees:
            done.add(("G", nt.name))
            for bsdf in [n for n in nt.nodes if n.type == "BSDF_PRINCIPLED"]:
                inp = bsdf.inputs["Base Color"]
                if inp.is_linked:
                    l = inp.links[0]
                    src = l.from_socket
                    nt.links.remove(l)
                else:
                    src = mix(nt, tuple(inp.default_value), tuple(inp.default_value), 0.0)
                nt.links.new(build(nt, bsdf, src), inp)


def float_input(nt, bsdf, name):
    """Current value of a BSDF float input as a socket (unlinking it)."""
    inp = bsdf.inputs[name]
    if inp.is_linked:
        l = inp.links[0]
        src = l.from_socket
        nt.links.remove(l)
        return src
    v = nt.nodes.new("ShaderNodeValue")
    v.outputs[0].default_value = inp.default_value
    return v.outputs[0]


def fmix(nt, a, b, fac):
    m = nt.nodes.new("ShaderNodeMix")
    m.data_type = "FLOAT"
    for i, v in ((2, a), (3, b)):
        if isinstance(v, (int, float)):
            m.inputs[i].default_value = v
        else:
            nt.links.new(v, m.inputs[i])
    nt.links.new(fac, m.inputs[0])
    return m.outputs[0]


def tint(obj, rgb, amount=1.0, mode="MULTIPLY"):
    recolor(obj, lambda nt, c: mix(nt, c, rgb, amount, mode))


def lin(rgb):
    """sRGB (as picked on screen) -> linear."""
    return tuple(c ** 2.2 for c in rgb)


def set_color(obj, rgb, keep=0.35):
    """Recolour (rgb given in sRGB) keeping some of the texture's light/dark detail."""
    rgb = lin(rgb)
    def b(nt, c):
        bw = nt.nodes.new("ShaderNodeRGBToBW")
        nt.links.new(c, bw.inputs["Color"])
        r = nt.nodes.new("ShaderNodeMapRange")
        r.inputs["To Min"].default_value = 1 - keep
        r.inputs["To Max"].default_value = 1 + keep * 0.4
        nt.links.new(bw.outputs["Val"], r.inputs["Value"])
        g = mix(nt, (1, 1, 1), (1, 1, 1), 0.0)
        mm = nt.nodes.new("ShaderNodeMix")
        mm.data_type = "RGBA"
        mm.blend_type = "MULTIPLY"
        mm.inputs[0].default_value = 1.0
        mm.inputs[6].default_value = rgb + (1,)
        cc = nt.nodes.new("ShaderNodeCombineColor")
        for i in range(3):
            nt.links.new(r.outputs["Result"], cc.inputs[i])
        nt.links.new(cc.outputs["Color"], mm.inputs[7])
        return mm.outputs[2]
    recolor(obj, b)


def surface_wrap(obj, build):
    """build(nt, shader_socket) -> new shader socket placed before the material output."""
    done = set()
    for ms in obj.material_slots:
        m = ms.material
        if not m or not m.node_tree or m.name in done:
            continue
        done.add(m.name)
        nt = m.node_tree
        outn = [n for n in nt.nodes if n.type == "OUTPUT_MATERIAL"]
        if not outn or not outn[0].inputs["Surface"].is_linked:
            continue
        l = outn[0].inputs["Surface"].links[0]
        src = l.from_socket
        nt.links.remove(l)
        nt.links.new(build(nt, src), outn[0].inputs["Surface"])


# ================================================================ mesh masks
def rest_positions(obj):
    """World positions of obj's vertices with shape keys but without modifiers (index-stable)."""
    saved = [(m, m.show_viewport) for m in obj.modifiers]
    for m, _ in saved:
        m.show_viewport = False
    dg = bpy.context.evaluated_depsgraph_get()
    dg.update()
    ev = obj.evaluated_get(dg)
    me = ev.to_mesh()
    mw = obj.matrix_world
    pts = [mw @ v.co for v in me.vertices]
    nrm = [(mw.to_3x3() @ v.normal).normalized() for v in me.vertices]
    ev.to_mesh_clear()
    for m, s in saved:
        m.show_viewport = s
    return pts, nrm


def paint(obj, name, fn):
    """Store fn(p, n) -> (r, g, b) per vertex in a colour attribute."""
    pts, nrm = rest_positions(obj)
    me = obj.data
    if name in me.color_attributes:
        me.color_attributes.remove(me.color_attributes[name])
    at = me.color_attributes.new(name, "FLOAT_COLOR", "POINT")
    for i, (p, n) in enumerate(zip(pts, nrm)):
        r, g, b = fn(p, n)
        at.data[i].color = (min(1, max(0, r)), min(1, max(0, g)), min(1, max(0, b)), 1)


def smooth(a, b, x):
    if a == b:
        return 1.0 if x >= a else 0.0
    t = min(1.0, max(0.0, (x - a) / (b - a)))
    return t * t * (3 - 2 * t)


def bbox_center(o):
    return sum((o.matrix_world @ Vector(c) for c in o.bound_box), Vector()) / 8


def bbox_size(o):
    pts = [o.matrix_world @ Vector(c) for c in o.bound_box]
    return Vector([max(p[i] for p in pts) - min(p[i] for p in pts) for i in range(3)])


# ================================================================ humans
def _mhclo(kind, name):
    return glob.glob(os.path.join(A, kind, name, "*.mhclo"))[0]


def build_human(name, *, gender, age, height=0.5, weight=0.5, muscle=0.5, proportions=0.5,
                race=(0.15, 0.65, 0.2), skin="young_caucasian_male", skin_type="ENHANCED_SSS",
                hair=None, brow="eyebrow001", lashes="eyelashes01", clothes=(), subdiv=1, extra=(), style=None):
    m = TargetService.get_default_macro_info_dict()
    m.update(gender=gender, age=age, height=height, weight=weight, muscle=muscle, proportions=proportions)
    m["race"] = {"asian": race[0], "caucasian": race[1], "african": race[2]}
    body = HumanService.create_human(macro_detail_dict=m)
    body.name = name
    TDIR = os.path.join(os.path.dirname(_mpfb.__file__), "data", "targets")
    for tname, w in (style or {}).items():      # face/body shape targets (before the assets are fitted)
        hits = glob.glob(os.path.join(TDIR, "*", tname + ".target.gz"))
        if hits:
            TargetService.load_target(body, hits[0], weight=w, name=tname)
    rig = HumanService.add_builtin_rig(body, "game_engine")
    rig.name = name + "_rig"
    HumanService.set_character_skin(f"{A}/skins/{skin}/{skin}.mhmat", body, skin_type=skin_type)
    parts = {}

    def add(kind, asset, t):
        before = set(bpy.data.objects)
        HumanService.add_mhclo_asset(_mhclo(kind, asset), body, asset_type=t,
                                     subdiv_levels=subdiv, material_type="MAKESKIN")
        new = [o for o in bpy.data.objects if o not in before]
        for o in new:
            for md in o.modifiers:
                if md.type == "SUBSURF":
                    md.levels = 0
                    md.render_levels = subdiv
        parts.setdefault(t, []).extend(new)
        return new

    add("eyes", "high-poly", "Eyes")
    if brow:
        add("eyebrows", brow, "Eyebrows")
    if lashes:
        add("eyelashes", lashes, "Eyelashes")
    add("teeth", "teeth_base", "Teeth")
    if hair:
        add("hair", hair, "Hair")
    for c in list(clothes) + list(extra):
        parts.setdefault("by_asset", {})[c] = add("clothes", c, "Clothes")
    return body, rig, parts


def add_expr(body, names):
    keys = {}
    for n in names:
        p = os.path.join(EXPR, n + ".target.gz")
        if not os.path.exists(p):
            continue
        TargetService.load_target(body, p, weight=0.0, name=n)
        keys[n] = body.data.shape_keys.key_blocks[n]
    return keys


def attach(obj, rig, bone):
    """Parent obj to a bone of rig keeping its current world transform (rig in rest pose)."""
    bpy.context.view_layer.update()
    mw = obj.matrix_world.copy()
    obj.parent = rig
    obj.parent_type = "BONE"
    obj.parent_bone = bone
    bpy.context.view_layer.update()
    obj.matrix_world = mw
    return obj


def bone_world(rig, bone, tail=False):
    b = rig.pose.bones[bone]
    return rig.matrix_world @ (b.tail if tail else b.head)


# ================================================================ posing
def q(pb, axis, deg):
    """Rotation about an armature-space axis, in the bone's rest space."""
    M = pb.bone.matrix_local.to_3x3().inverted()
    return Quaternion((M @ Vector(axis)).normalized(), math.radians(deg))


ORDER = ("y", "x", "z")
AX = {"x": X, "y": Y, "z": Z}


def apply_spec(rig, spec):
    """spec: bone -> {"x": deg, "y": deg, "z": deg} (armature axes), applied in Y, X, Z order."""
    for pb in rig.pose.bones:
        pb.rotation_mode = "QUATERNION"
        d = spec.get(pb.name)
        r = Quaternion()
        if d:
            for a in ORDER:
                v = d.get(a, 0.0)
                if v:
                    r = q(pb, AX[a], v) @ r
        pb.rotation_quaternion = r


def key_pose(rig, frame):
    for pb in rig.pose.bones:
        pb.keyframe_insert("rotation_quaternion", frame=frame)
