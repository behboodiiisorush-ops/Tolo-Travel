"""Realistic procedural materials and simple props for sets (shared by all films)."""
import bpy, math
from mathutils import Vector


def lin(rgb):
    return tuple(c ** 2.2 for c in rgb)


def mat(name, color, rough=0.5, metal=0.0, emit=None, strength=0.0, srgb=True, alpha=1.0, trans=0.0):
    m = bpy.data.materials.new(name)
    p = m.node_tree.nodes["Principled BSDF"]
    c = lin(color) if srgb else color
    p.inputs["Base Color"].default_value = c + (1,)
    p.inputs["Roughness"].default_value = rough
    p.inputs["Metallic"].default_value = metal
    if trans:
        p.inputs["Transmission Weight"].default_value = trans
    if alpha < 1:
        p.inputs["Alpha"].default_value = alpha
    if emit:
        p.inputs["Emission Color"].default_value = (lin(emit) if srgb else emit) + (1,)
        p.inputs["Emission Strength"].default_value = strength
    return m


def _bsdf(m):
    return m.node_tree.nodes["Principled BSDF"]


def grime(m, scale=4.0, dark=0.6, rough_var=0.2, bump=0.06, coords="Object"):
    nt = m.node_tree
    p = _bsdf(m)
    base = tuple(p.inputs["Base Color"].default_value)
    tc = nt.nodes.new("ShaderNodeTexCoord")
    n = nt.nodes.new("ShaderNodeTexNoise")
    n.inputs["Scale"].default_value = scale
    n.inputs["Detail"].default_value = 8
    nt.links.new(tc.outputs[coords], n.inputs["Vector"])
    r = nt.nodes.new("ShaderNodeMapRange")
    r.inputs["From Min"].default_value = 0.35
    r.inputs["From Max"].default_value = 0.75
    nt.links.new(n.outputs["Fac"], r.inputs["Value"])
    mx = nt.nodes.new("ShaderNodeMix")
    mx.data_type = "RGBA"
    mx.inputs[6].default_value = base
    mx.inputs[7].default_value = tuple(c * dark for c in base[:3]) + (1,)
    nt.links.new(r.outputs["Result"], mx.inputs[0])
    nt.links.new(mx.outputs[2], p.inputs["Base Color"])
    rr = nt.nodes.new("ShaderNodeMapRange")
    rv = p.inputs["Roughness"].default_value
    rr.inputs["To Min"].default_value = max(0.02, rv - rough_var)
    rr.inputs["To Max"].default_value = min(1.0, rv + rough_var)
    nt.links.new(n.outputs["Fac"], rr.inputs["Value"])
    nt.links.new(rr.outputs["Result"], p.inputs["Roughness"])
    if bump:
        b = nt.nodes.new("ShaderNodeBump")
        b.inputs["Strength"].default_value = bump
        nt.links.new(n.outputs["Fac"], b.inputs["Height"])
        nt.links.new(b.outputs["Normal"], p.inputs["Normal"])
    return m


def wall_coords(nt, src):
    """(x + y, z): runs along any vertical wall, whichever way it faces."""
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(src, sep.inputs[0])
    add = nt.nodes.new("ShaderNodeMath")
    nt.links.new(sep.outputs[0], add.inputs[0])
    nt.links.new(sep.outputs[1], add.inputs[1])
    cmb = nt.nodes.new("ShaderNodeCombineXYZ")
    nt.links.new(add.outputs[0], cmb.inputs[0])
    nt.links.new(sep.outputs[2], cmb.inputs[1])
    return cmb.outputs[0]


def tiles(name, c1, c2, mortar, size=0.4, rough=0.3, gap=0.006, width=None, offset=0.0, coords="Object", wall=False):
    m = mat(name, c1, rough)
    nt = m.node_tree
    p = _bsdf(m)
    tc0 = nt.nodes.new("ShaderNodeTexCoord")

    class _TC:
        outputs = {coords: wall_coords(nt, tc0.outputs[coords]) if wall else tc0.outputs[coords]}
    tc = _TC
    br = nt.nodes.new("ShaderNodeTexBrick")
    br.offset = offset
    br.inputs["Color1"].default_value = lin(c1) + (1,)
    br.inputs["Color2"].default_value = lin(c2) + (1,)
    br.inputs["Mortar"].default_value = lin(mortar) + (1,)
    br.inputs["Scale"].default_value = 1.0
    br.inputs["Mortar Size"].default_value = gap
    br.inputs["Brick Width"].default_value = width or size
    br.inputs["Row Height"].default_value = size
    nt.links.new(tc.outputs[coords], br.inputs["Vector"])
    nz = nt.nodes.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 3.0
    nz.inputs["Detail"].default_value = 8
    nt.links.new(tc.outputs[coords], nz.inputs["Vector"])
    mx = nt.nodes.new("ShaderNodeMix")
    mx.data_type = "RGBA"
    mx.blend_type = "MULTIPLY"
    mx.inputs[0].default_value = 0.45
    nt.links.new(br.outputs["Color"], mx.inputs[6])
    nt.links.new(nz.outputs["Color"], mx.inputs[7])
    nt.links.new(mx.outputs[2], p.inputs["Base Color"])
    rr = nt.nodes.new("ShaderNodeMapRange")
    rr.inputs["To Min"].default_value = max(0.05, rough - 0.15)
    rr.inputs["To Max"].default_value = min(1, rough + 0.25)
    nt.links.new(nz.outputs["Fac"], rr.inputs["Value"])
    nt.links.new(rr.outputs["Result"], p.inputs["Roughness"])
    bp = nt.nodes.new("ShaderNodeBump")
    bp.inputs["Strength"].default_value = 0.2
    nt.links.new(br.outputs["Fac"], bp.inputs["Height"])
    nt.links.new(bp.outputs["Normal"], p.inputs["Normal"])
    return m


def wood(name, color=(0.55, 0.36, 0.2), planks=True, rough=0.35, scale=1.0):
    """Wooden floor planks (planks=True) or plain wood grain."""
    m = mat(name, color, rough)
    nt = m.node_tree
    p = _bsdf(m)
    tc = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (scale * 0.4, scale * 12, scale)
    nt.links.new(tc.outputs["Object"], mp.inputs["Vector"])
    wv = nt.nodes.new("ShaderNodeTexNoise")
    wv.inputs["Scale"].default_value = 3
    wv.inputs["Detail"].default_value = 6
    nt.links.new(mp.outputs[0], wv.inputs["Vector"])
    base = lin(color)
    mx = nt.nodes.new("ShaderNodeMix")
    mx.data_type = "RGBA"
    mx.inputs[6].default_value = base + (1,)
    mx.inputs[7].default_value = tuple(c * 0.55 for c in base) + (1,)
    nt.links.new(wv.outputs["Fac"], mx.inputs[0])
    out = mx.outputs[2]
    if planks:
        br = nt.nodes.new("ShaderNodeTexBrick")
        br.inputs["Scale"].default_value = 1.0
        br.inputs["Brick Width"].default_value = 1.2
        br.inputs["Row Height"].default_value = 0.15
        br.inputs["Mortar Size"].default_value = 0.002
        br.inputs["Color1"].default_value = (1, 1, 1, 1)
        br.inputs["Color2"].default_value = (0.78, 0.74, 0.7, 1)
        br.inputs["Mortar"].default_value = (0.2, 0.2, 0.2, 1)
        nt.links.new(tc.outputs["Object"], br.inputs["Vector"])
        m2 = nt.nodes.new("ShaderNodeMix")
        m2.data_type = "RGBA"
        m2.blend_type = "MULTIPLY"
        m2.inputs[0].default_value = 1.0
        nt.links.new(out, m2.inputs[6])
        nt.links.new(br.outputs["Color"], m2.inputs[7])
        out = m2.outputs[2]
        bp = nt.nodes.new("ShaderNodeBump")
        bp.inputs["Strength"].default_value = 0.15
        nt.links.new(br.outputs["Fac"], bp.inputs["Height"])
        nt.links.new(bp.outputs["Normal"], p.inputs["Normal"])
    nt.links.new(out, p.inputs["Base Color"])
    return m


def glass(name="Glass", tint=(0.9, 0.95, 1.0), rough=0.02):
    m = mat(name, tint, rough)
    p = _bsdf(m)
    p.inputs["Transmission Weight"].default_value = 1.0
    p.inputs["IOR"].default_value = 1.45
    return m


def emit(name, color, strength):
    m = bpy.data.materials.new(name)
    nt = m.node_tree
    nt.nodes.clear()
    o = nt.nodes.new("ShaderNodeOutputMaterial")
    e = nt.nodes.new("ShaderNodeEmission")
    e.inputs["Color"].default_value = lin(color) + (1,)
    e.inputs["Strength"].default_value = strength
    nt.links.new(e.outputs[0], o.inputs["Surface"])
    return m


def image(name, path, strength=0.0, rough=0.8):
    """Image on a surface; strength > 0 makes it glow (screens)."""
    m = bpy.data.materials.new(name)
    nt = m.node_tree
    p = _bsdf(m)
    t = nt.nodes.new("ShaderNodeTexImage")
    t.image = bpy.data.images.load(path, check_existing=True)
    nt.links.new(t.outputs["Color"], p.inputs["Base Color"])
    p.inputs["Roughness"].default_value = rough
    if strength:
        nt.links.new(t.outputs["Color"], p.inputs["Emission Color"])
        p.inputs["Emission Strength"].default_value = strength
    return m


# ------------------------------------------------------------------ geometry
def box(loc, size, m, name="box", rot=(0, 0, 0), bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(location=loc, rotation=rot)
    o = bpy.context.object
    o.name = name
    o.scale = (size[0] / 2, size[1] / 2, size[2] / 2)
    bpy.ops.object.transform_apply(scale=True)
    if bevel:
        b = o.modifiers.new("bevel", "BEVEL")
        b.width = bevel
        b.segments = 2
    o.data.materials.append(m)
    return o


def plane(loc, size, m, rot=(0, 0, 0), name="plane"):
    bpy.ops.mesh.primitive_plane_add(location=loc, rotation=rot)
    o = bpy.context.object
    o.name = name
    o.scale = (size[0] / 2, size[1] / 2, 1)
    bpy.ops.object.transform_apply(scale=True)
    o.data.materials.append(m)
    return o


def cyl(a, b, r, m, name="cyl", verts=16):
    a, b = Vector(a), Vector(b)
    d = b - a
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=d.length, location=(a + b) / 2, vertices=verts)
    o = bpy.context.object
    o.rotation_euler = d.to_track_quat("Z", "Y").to_euler()
    o.name = name
    o.data.materials.append(m)
    bpy.ops.object.shade_smooth()
    return o


def sphere(loc, r, m, name="sphere", scale=(1, 1, 1)):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=loc, segments=24, ring_count=12)
    o = bpy.context.object
    o.scale = scale
    o.name = name
    o.data.materials.append(m)
    bpy.ops.object.shade_smooth()
    return o


def empty(name, loc=(0, 0, 0)):
    e = bpy.data.objects.new(name, None)
    bpy.context.scene.collection.objects.link(e)
    e.location = loc
    return e


def parent_keep(child, parent):
    bpy.context.view_layer.update()
    mw = child.matrix_world.copy()
    child.parent = parent
    child.matrix_world = mw


def area_light(loc, target, energy, size=1.0, color=(1, 1, 1), size_y=None, name="Area"):
    bpy.ops.object.light_add(type="AREA", location=loc)
    l = bpy.context.object
    l.name = name
    l.data.energy = energy
    l.data.color = color
    if size_y:
        l.data.shape = "RECTANGLE"
        l.data.size, l.data.size_y = size, size_y
    else:
        l.data.size = size
    l.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    return l


def window(center, width, height, axis, sky, frame_m, depth=0.06, bars=2):
    """A window in a wall: glowing sky plane + frame. axis 'x' = wall facing ±X, 'y' = facing ±Y."""
    cx, cy, cz = center
    if axis == "x":
        plane((cx, cy, cz), (width, height), sky, (math.pi / 2, 0, math.pi / 2), "Window sky")
        for dy in (-width / 2, width / 2):
            box((cx, cy + dy, cz), (depth, 0.06, height), frame_m, "Window frame")
        for dz in (-height / 2, height / 2):
            box((cx, cy, cz + dz), (depth, width, 0.06), frame_m, "Window frame")
        for k in range(1, bars):
            box((cx, cy - width / 2 + k * width / bars, cz), (depth, 0.04, height), frame_m, "Window bar")
    else:
        plane((cx, cy, cz), (width, height), sky, (math.pi / 2, 0, 0), "Window sky")
        for dx in (-width / 2, width / 2):
            box((cx + dx, cy, cz), (0.06, depth, height), frame_m, "Window frame")
        for dz in (-height / 2, height / 2):
            box((cx, cy, cz + dz), (width, depth, 0.06), frame_m, "Window frame")
        for k in range(1, bars):
            box((cx - width / 2 + k * width / bars, cy, cz), (0.04, depth, height), frame_m, "Window bar")


# ------------------------------------------------------------------ cel-shaded comic look (Cycles)
def toonify(sat=0.55, lift=0.08, size=0.75, ambient=0.28):
    """Turn every material in the file into a flat cel-shaded paint (Toon BSDF + soft ambient),
    muted towards grey; keeps alpha (hair cards). Pair it with enable_outlines()."""
    done = set()
    trees = []
    for m in bpy.data.materials:
        if m.node_tree:
            trees.append(m.node_tree)
    for g in bpy.data.node_groups:
        if g.type == "SHADER":
            trees.append(g)
    for nt in trees:
        if nt.name in done:
            continue
        done.add(nt.name)
        for b in [n for n in nt.nodes if n.type == "BSDF_PRINCIPLED"]:
            outs = [l for l in nt.links if l.from_node == b]
            if not outs:
                continue
            bc = b.inputs["Base Color"]
            if bc.is_linked:
                col = bc.links[0].from_socket
            else:
                rgb = nt.nodes.new("ShaderNodeRGB")
                rgb.outputs[0].default_value = bc.default_value
                col = rgb.outputs[0]
            hsv = nt.nodes.new("ShaderNodeHueSaturation")
            hsv.inputs["Saturation"].default_value = sat
            hsv.inputs["Value"].default_value = 1.0 + lift
            nt.links.new(col, hsv.inputs["Color"])
            toon = nt.nodes.new("ShaderNodeBsdfToon")
            toon.component = "DIFFUSE"
            toon.inputs["Size"].default_value = size
            toon.inputs["Smooth"].default_value = 0.04
            nt.links.new(hsv.outputs[0], toon.inputs["Color"])
            em = nt.nodes.new("ShaderNodeEmission")
            em.inputs["Strength"].default_value = ambient
            nt.links.new(hsv.outputs[0], em.inputs["Color"])
            add = nt.nodes.new("ShaderNodeAddShader")
            nt.links.new(toon.outputs[0], add.inputs[0])
            nt.links.new(em.outputs[0], add.inputs[1])
            out = add.outputs[0]
            al = b.inputs["Alpha"]
            if al.is_linked or al.default_value < 1:
                tr = nt.nodes.new("ShaderNodeBsdfTransparent")
                mx = nt.nodes.new("ShaderNodeMixShader")
                if al.is_linked:
                    nt.links.new(al.links[0].from_socket, mx.inputs[0])
                else:
                    mx.inputs[0].default_value = al.default_value
                nt.links.new(tr.outputs[0], mx.inputs[1])
                nt.links.new(out, mx.inputs[2])
                out = mx.outputs[0]
            for l in outs:
                to = l.to_socket
                nt.links.remove(l)
                nt.links.new(out, to)


def enable_outlines(scene, thickness=1.6, exclude=(), contour_only=()):
    """Thick black comic outlines (Freestyle). exclude: objects that get no lines (eyes, lashes...).
    contour_only: objects (characters) that only get their outer outline, so faces stay clean."""
    scene.render.use_freestyle = True
    scene.render.line_thickness_mode = "ABSOLUTE"
    scene.render.line_thickness = thickness
    vl = scene.view_layers[0]
    vl.use_freestyle = True
    fs = vl.freestyle_settings
    fs.crease_angle = math.radians(125)
    ls = fs.linesets[0] if fs.linesets else fs.linesets.new("Lines")
    ls.select_by_visibility = True
    ls.select_silhouette = ls.select_border = True
    ls.select_crease = False
    if exclude or contour_only:
        col = bpy.data.collections.new("No outline")
        scene.collection.children.link(col)
        for o in list(exclude) + list(contour_only):
            if col not in o.users_collection:
                col.objects.link(o)
        ls.select_by_collection = True
        ls.collection = col
        ls.collection_negation = "EXCLUSIVE"
    if ls.linestyle is None:
        ls.linestyle = bpy.data.linestyles.new("Comic")
    ls.linestyle.color = (0.02, 0.02, 0.02)
    ls.linestyle.thickness = thickness
    if contour_only:
        cc = bpy.data.collections.new("Contour only")
        scene.collection.children.link(cc)
        for o in contour_only:
            cc.objects.link(o)
        l2 = fs.linesets.new("Characters")
        l2.select_by_visibility = True
        l2.select_silhouette = True
        l2.select_border = l2.select_crease = False
        l2.select_by_collection = True
        l2.collection = cc
        l2.linestyle = bpy.data.linestyles.new("People lines")
        l2.linestyle.color = (0.03, 0.02, 0.02)
        l2.linestyle.thickness = thickness * 0.55     # thinner on people so faces stay clean
