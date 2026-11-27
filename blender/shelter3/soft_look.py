"""Soft cinematic look for «پناهگاه ۳» (the user's choice, 27 Nov): no ink outlines; every cel material becomes a
real (Principled) surface with the same colours, so light falls off softly, with soft shadows, ambient occlusion,
warm skin with a little subsurface, AgX colour with a gentle contrast.  The distance fog and the glowing things
(lamps, headlights, eyes in the trees) stay as they were.

    import soft_look; soft_look.apply(bpy.context.scene)      # end of scene.py (or on a saved shelter3.blend)
"""
import bpy

SKIN_PARTS = ("body", "ears", "lips")


def _from(sock):
    return sock.links[0].from_socket if sock.is_linked else None


def _convert(m):
    nt = m.node_tree
    N, L = nt.nodes, nt.links
    mul = next((n for n in N if n.type == "MIX" and n.blend_type == "MULTIPLY" and n.data_type == "RGBA"), None)
    em = next((n for n in N if n.type == "EMISSION"), None)
    if mul is None or em is None:
        return False
    # albedo: what fed the cel multiply (flat colour, texture, iris ramp, window bricks)
    alb = _from(mul.inputs[6])
    fogmix = em.inputs[0].links[0].from_node if em.inputs[0].is_linked else None
    fog_fac = fog_col = None
    if fogmix is not None and fogmix.type == "MIX" and fogmix.data_type == "RGBA" and fogmix.blend_type == "MIX":
        fog_fac, fog_col = _from(fogmix.inputs[0]), _from(fogmix.inputs[7])
    shine = any(n.type == "BSDF_GLOSSY" for n in N)
    p = N.new("ShaderNodeBsdfPrincipled")
    if alb is not None:
        L.new(alb, p.inputs["Base Color"])
    else:
        p.inputs["Base Color"].default_value = mul.inputs[6].default_value
    p.inputs["Roughness"].default_value = 0.25 if shine else 0.62
    for k in ("Specular IOR Level", "Specular"):
        if k in p.inputs:
            p.inputs[k].default_value = 0.35 if shine else 0.18
            break
    nm = m.name.lower()
    rest = nm.split(".", 1)[1] if "." in nm else ""
    if rest.startswith(SKIN_PARTS):
        for k, v in (("Subsurface Weight", 0.12), ("Subsurface Scale", 0.02)):
            if k in p.inputs:
                p.inputs[k].default_value = v
        if "Subsurface Radius" in p.inputs:
            p.inputs["Subsurface Radius"].default_value = (1.0, 0.35, 0.2)
    shader = p.outputs[0]
    if fog_fac is not None:
        fe = N.new("ShaderNodeEmission")
        if fog_col is not None:
            L.new(fog_col, fe.inputs[0])
        ms = N.new("ShaderNodeMixShader")
        L.new(fog_fac, ms.inputs[0])
        L.new(shader, ms.inputs[1])
        L.new(fe.outputs[0], ms.inputs[2])
        shader = ms.outputs[0]
    # rewire whatever used the emission (the output, or the alpha cut-out mix)
    for lk in list(em.outputs[0].links):
        L.new(shader, lk.to_socket)
    return True


def apply(sc):
    n_mat = sum(1 for m in bpy.data.materials if m.use_nodes and not m.name.startswith("Ink") and _convert(m))
    n_out = 0
    for o in bpy.data.objects:
        for md in list(o.modifiers):
            if md.type == "SOLIDIFY" and md.name.startswith("Outline"):
                o.modifiers.remove(md)
                n_out += 1
    for o in bpy.data.objects:
        if o.type == "LIGHT":
            o.data.shadow_soft_size = max(o.data.shadow_soft_size, 0.35)
            if o.data.type == "SUN":
                o.data.angle = max(o.data.angle, 0.12)
                o.data.use_shadow = True
    ee = sc.eevee
    for attr, v in (("shadow_ray_count", 2), ("shadow_step_count", 4), ("use_gtao", True), ("gtao_distance", 0.8),
                    ("use_shadows", True), ("use_fast_gi", True), ("fast_gi_distance", 0.8)):
        if hasattr(ee, attr):
            setattr(ee, attr, v)
    vs = sc.view_settings
    try:
        vs.view_transform = "AgX"
        vs.look = "AgX - Punchy"
    except TypeError:
        pass
    vs.exposure = float(__import__("os").environ.get("SOFT_EXPOSURE", "0.0"))
    print("soft look:", n_mat, "materials,", n_out, "outlines removed")
