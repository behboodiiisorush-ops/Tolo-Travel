"""Stylized 3D look (EEVEE) — like a stylized 3D car / toy render: smooth soft shading, rounded (bevelled)
edges, clean saturated colours, soft shadows and ambient occlusion, no ink outlines.

    import toon_look as T, stylized_look as S
    T.register(ch, key, realistic=True)        # the flat colour table for clothes / skin (same as the comic look)
    S.stylize(sc)                              # every material -> soft principled, colour management, AO, shadows
    S.round_edges(objs, width=0.06)            # bevel + smooth normals on hard-surface props (buildings, cars...)
"""
import bpy, colorsys
import toon_look as T

SAT = 1.15          # colour richness (1 = as built)
ROUGH = 0.55        # soft plastic / clay
CLEAR = ("car", "lamp", "iron", "bars")
PALETTE = {}        # material name -> linear rgb, overrides the built colour (a film's own bright toy palette)   # material names that get a glossy clear coat (painted metal)


def _rgb(mat):
    sock, rgba = T._base_colour(mat)
    if sock is not None:
        for n in mat.node_tree.nodes:
            if n.type == "BSDF_PRINCIPLED":
                return T._eval(n.inputs["Base Color"])
        return T._eval(sock)
    return tuple(rgba[:3])


def soft(mat, flat=None, keep_tex=False):
    """One material -> a single Principled BSDF with a flat rich colour (or its texture for eyes)."""
    if not mat.use_nodes or T._is_emissive(mat):
        return
    nt = mat.node_tree
    sock, _ = T._base_colour(mat)
    alpha = None
    for n in nt.nodes:
        if n.type == "BSDF_PRINCIPLED" and n.inputs["Alpha"].is_linked:
            alpha = n.inputs["Alpha"].links[0].from_socket
    if mat.name in PALETTE:
        rgb = PALETTE[mat.name]
    else:
        rgb = tuple(flat) if flat is not None else _rgb(mat)
        h, s, v = colorsys.rgb_to_hsv(*[max(0.0, min(1.0, c)) for c in rgb])
        rgb = colorsys.hsv_to_rgb(h, min(1.0, s * SAT), v)
    keep = set()
    if alpha is not None:
        keep.add(alpha.node)
    if keep_tex and sock is not None and flat is None:
        keep.add(sock.node)
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
    b = N.new("ShaderNodeBsdfPrincipled")
    if keep_tex and sock is not None and flat is None:
        L.new(sock, b.inputs["Base Color"])
    else:
        b.inputs["Base Color"].default_value = tuple(rgb) + (1.0,)
    name = mat.name.lower()
    b.inputs["Roughness"].default_value = ROUGH
    b.inputs["Specular IOR Level"].default_value = 0.35
    if any(k in name for k in CLEAR):
        b.inputs["Roughness"].default_value = 0.35
        b.inputs["Coat Weight"].default_value = 0.6
        b.inputs["Coat Roughness"].default_value = 0.12
    if "glass" in name or "pane" in name or "win" in name:
        b.inputs["Roughness"].default_value = 0.15
        b.inputs["Specular IOR Level"].default_value = 0.6
    if "body" in name or "skin" in name or "ears" in name or "lips" in name:
        b.inputs["Subsurface Weight"].default_value = 0.08
        b.inputs["Roughness"].default_value = 0.6
    if "eye" in name and "brow" not in name and "lash" not in name:
        b.inputs["Roughness"].default_value = 0.12
        b.inputs["Coat Weight"].default_value = 1.0
    if alpha is not None:
        L.new(alpha, b.inputs["Alpha"])
    L.new(b.outputs[0], out.inputs[0])


def stylize(sc, samples=8):
    sc.render.engine = "BLENDER_EEVEE"
    sc.eevee.taa_render_samples = samples
    sc.eevee.use_shadows = True
    sc.eevee.shadow_resolution_scale = 0.5
    sc.eevee.use_fast_gi = True                     # soft ambient occlusion in the corners
    sc.eevee.fast_gi_method = "GLOBAL_ILLUMINATION"
    sc.eevee.fast_gi_distance = 1.5
    sc.view_settings.view_transform = "Standard"     # AgX/Filmic wash the toy colours out
    sc.view_settings.look = "None"
    sc.view_settings.exposure = 0.0
    for m in bpy.data.materials:
        if m.name.startswith("Ink"):
            continue
        n = m.name.lower()
        imgs = [x.image.name.lower() for x in m.node_tree.nodes if x.type == "TEX_IMAGE" and x.image] if m.use_nodes else []
        eyes = (("eye" in n and "brow" not in n and "lash" not in n) or "teeth" in n
                or any(i.endswith("_eye.png") for i in imgs))
        flat = T._flat_for(m)
        soft(m, flat=flat, keep_tex=eyes and flat is None)


def round_edges(objs, width=0.06, segments=3):
    """Toy-like rounded edges: bevel modifier (by angle) + smooth shading with hardened normals."""
    for o in objs:
        if o.type != "MESH" or not o.data.polygons:
            continue
        if any(m.type == "BEVEL" for m in o.modifiers):
            continue
        w = min(width, 0.25 * min(d for d in o.dimensions if d > 1e-4) if any(d > 1e-4 for d in o.dimensions) else width)
        m = o.modifiers.new("Round", "BEVEL")
        m.width = max(0.004, w)
        m.segments = segments
        m.limit_method = "ANGLE"
        m.harden_normals = True
        m.use_clamp_overlap = True
        for p in o.data.polygons:
            p.use_smooth = True
