"""Comic / cel-shaded look for the studio (EEVEE): flat colours in 3 light bands, black ink outlines on
everything, and sweat drops for scared faces.

    import toon_look as T
    T.toonify(scene)                       # every material -> 3-band cel shader, engine -> EEVEE
    T.ink(objs, thickness=0.004)           # inverted-hull outlines (backface culled, works in EEVEE)
    T.sweat(ch, frames=(f0, f1), n=4)      # drops appear on forehead/temples and slide down
"""
import bpy, math, random
from mathutils import Vector

BANDS = ((0.0, 0.5), (0.12, 0.78), (0.45, 1.0))     # (light level where the band starts, brightness)


def _base_colour(mat):
    """(socket_to_link or None, rgba) of a material's base colour."""
    nt = mat.node_tree
    for n in nt.nodes:
        if n.type == "BSDF_PRINCIPLED":
            s = n.inputs["Base Color"]
            if s.is_linked:
                return s.links[0].from_socket, None
            return None, tuple(s.default_value)
        if n.type in ("BSDF_DIFFUSE", "BSDF_GLOSSY"):
            s = n.inputs["Color"]
            return (s.links[0].from_socket, None) if s.is_linked else (None, tuple(s.default_value))
    return None, tuple(list(mat.diffuse_color))


def _is_emissive(mat):
    nt = mat.node_tree
    out = [n for n in nt.nodes if n.type == "OUTPUT_MATERIAL"]
    if not out or not out[0].inputs["Surface"].is_linked:
        return False
    src = out[0].inputs["Surface"].links[0].from_node
    return src.type in ("EMISSION", "BSDF_TRANSPARENT", "MIX_SHADER", "ADD_SHADER")


def cel(mat, shine=0.0, flat=None):
    """Turn one material into flat colour * 3 light bands (+ optional hard white highlight).
    flat=(r,g,b) drops the texture and uses one flat colour (comic look)."""
    if not mat.use_nodes or _is_emissive(mat):
        return
    nt = mat.node_tree
    sock, rgba = _base_colour(mat)
    if flat is not None:
        sock, rgba = None, tuple(flat) + (1.0,)
    keep = {sock.node} if sock else set()
    # keep the whole texture chain feeding the colour
    stack = list(keep)
    while stack:
        n = stack.pop()
        for i in n.inputs:
            for l in i.links:
                if l.from_node not in keep:
                    keep.add(l.from_node)
                    stack.append(l.from_node)
    for n in list(nt.nodes):
        if n not in keep:
            nt.nodes.remove(n)
    N, L = nt.nodes, nt.links
    out = N.new("ShaderNodeOutputMaterial")
    dif = N.new("ShaderNodeBsdfDiffuse")
    s2r = N.new("ShaderNodeShaderToRGB")
    ramp = N.new("ShaderNodeValToRGB")
    ramp.color_ramp.interpolation = "CONSTANT"
    els = ramp.color_ramp.elements
    els[0].position, els[0].color = BANDS[0][0], (BANDS[0][1],) * 3 + (1,)
    els[1].position, els[1].color = BANDS[1][0], (BANDS[1][1],) * 3 + (1,)
    e = els.new(BANDS[2][0])
    e.color = (BANDS[2][1],) * 3 + (1,)
    bw = N.new("ShaderNodeRGBToBW")
    mul = N.new("ShaderNodeMix")
    mul.data_type, mul.blend_type = "RGBA", "MULTIPLY"
    mul.inputs[0].default_value = 1.0
    if sock:
        L.new(sock, mul.inputs[6])
    else:
        mul.inputs[6].default_value = rgba
    em = N.new("ShaderNodeEmission")
    L.new(dif.outputs[0], s2r.inputs[0])
    L.new(s2r.outputs[0], bw.inputs[0])
    L.new(bw.outputs[0], ramp.inputs[0])
    L.new(ramp.outputs[0], mul.inputs[7])
    col = mul.outputs[2]
    if shine > 0:                                   # hard specular dot (eyes, sweat, wet skin)
        gl = N.new("ShaderNodeBsdfGlossy")
        gl.inputs["Roughness"].default_value = 0.15
        s2 = N.new("ShaderNodeShaderToRGB")
        bw2 = N.new("ShaderNodeRGBToBW")
        st = N.new("ShaderNodeMath"); st.operation = "GREATER_THAN"; st.inputs[1].default_value = 1.0 - shine
        add = N.new("ShaderNodeMix"); add.data_type, add.blend_type = "RGBA", "MIX"
        L.new(gl.outputs[0], s2.inputs[0]); L.new(s2.outputs[0], bw2.inputs[0]); L.new(bw2.outputs[0], st.inputs[0])
        L.new(st.outputs[0], add.inputs[0]); L.new(col, add.inputs[6]); add.inputs[7].default_value = (1, 1, 1, 1)
        col = add.outputs[2]
    L.new(col, em.inputs[0])
    L.new(em.outputs[0], out.inputs[0])


def toonify(sc, samples=16):
    sc.render.engine = "BLENDER_EEVEE"
    sc.eevee.taa_render_samples = samples
    sc.view_settings.view_transform = "Standard"
    sc.view_settings.look = "None"
    for m in bpy.data.materials:
        if m.name.startswith("Ink"):
            continue
        n = m.name.lower()
        flat = _flat_for(m)
        cel(m, shine=0.06 if ("eye white" in n or "pupil" in n or "sweat" in n) else 0.0, flat=flat)


SKIN = {}      # character object name prefix -> skin rgb (filled by register())


def register(ch, key):
    import characters as C
    d = C.SHEET[key]
    SKIN[ch.name] = (d["skin"], d.get("clothes", {}))


def _flat_for(m):
    for prefix, (skin, clothes) in SKIN.items():
        if not m.name.startswith(prefix + "."):
            continue
        rest = m.name[len(prefix) + 1:]
        for cl, rgb in clothes.items():
            if rest.startswith(cl):
                return rgb
        if rest.split(".")[0] in ("body", "ears", "lips", "nipple", "fingernails", "toenails", "genitals"):
            return tuple(c * (0.85 if rest.startswith("lips") else 1.0) for c in skin)
    return None


def _ink_mat():
    m = bpy.data.materials.get("Ink")
    if m:
        return m
    m = bpy.data.materials.new("Ink")
    m.use_nodes = True
    m.use_backface_culling = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    e = nt.nodes.new("ShaderNodeEmission")
    e.inputs[0].default_value = (0.02, 0.015, 0.02, 1)
    o = nt.nodes.new("ShaderNodeOutputMaterial")
    nt.links.new(e.outputs[0], o.inputs[0])
    return m


def ink(objs, thickness=0.004, skip=("pupil", "glint", "lid", "mouth")):
    m = _ink_mat()
    for o in objs:
        if o.type != "MESH" or any(k in o.name.lower() for k in skip) or "Outline" in o.modifiers:
            continue
        o.data.materials.append(m)
        sd = o.modifiers.new("Outline", "SOLIDIFY")
        sd.thickness = thickness / max(1e-6, o.matrix_world.to_scale().x)
        sd.offset = 1.0
        sd.use_flip_normals = True
        sd.use_rim = False
        sd.material_offset = len(o.data.materials) - 1


def _sweat_mat():
    m = bpy.data.materials.get("Sweat")
    if not m:
        m = bpy.data.materials.new("Sweat")
        m.use_nodes = True
        m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.75, 0.9, 1.0, 1)
    return m


def sweat(ch, frames=(1, 1), n=4, seed=1, fps=24):
    """Drops on the forehead / temples: pop in, slide down the skin, fade (scale) out. Returns the drops."""
    rnd = random.Random(seed)
    hc = ch.head_center
    R = 0.13
    hb = ch.rig.pose.bones["head"]
    drops = []
    spots = [(0.62, 0.42), (-0.66, 0.38), (0.8, 0.05), (-0.82, 0.0), (0.3, 0.55), (-0.35, 0.52)]
    f0, f1 = frames
    for i in range(n):
        sx, sz = spots[i % len(spots)]
        # point on the front of the head surface
        y = -math.sqrt(max(0.0, 1 - sx * sx * 0.81 - sz * sz)) * R * 1.0 - R * 0.06
        p = hc + Vector((sx * R * 0.9, y, sz * R))
        bpy.context.scene.frame_set(f0)
        pb_m = ch.rig.matrix_world @ hb.matrix
        rest_m = ch.rig.matrix_world @ hb.bone.matrix_local
        p = pb_m @ (rest_m.inverted() @ p)          # rest-pose point -> where the head is now
        bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=10, radius=R * 0.13, location=p)
        d = bpy.context.object
        d.name = f"{ch.name} sweat {i}"
        for v in d.data.vertices:                # teardrop: pointed top
            if v.co.z > 0:
                k = v.co.z / (R * 0.13)
                v.co.x *= (1 - 0.8 * k)
                v.co.y *= (1 - 0.8 * k)
                v.co.z *= 1.9
        d.scale = (1.0, 0.55, 1.0)
        d.data.materials.append(_sweat_mat())
        con = d.constraints.new("CHILD_OF")       # follows the head
        con.target, con.subtarget = ch.rig, "head"
        con.inverse_matrix = pb_m.inverted()
        start = f0 + int(rnd.uniform(0, max(1, (f1 - f0) * 0.4)))
        slide = int(rnd.uniform(1.2, 2.2) * fps)
        base = d.location.copy()
        down = Vector((0, 0, -R * 0.35))
        for f, s, off in ((start - 1, 0.0, 0.0), (start + 4, 1.0, 0.0), (start + slide, 0.9, 1.0),
                          (start + slide + 5, 0.0, 1.1)):
            d.scale = (s, s * 0.55, s)
            d.keyframe_insert("scale", frame=f)
            d.location = base + down * off
            d.keyframe_insert("location", frame=f)
        drops.append(d)
    return drops
