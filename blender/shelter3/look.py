"""Cleaner comic faces for «پناهگاه ۳» (on top of studio/toon_look.py):
warm peach skin, big clear eyes (white sclera, brown iris, black pupil, a white catch-light), dark bold brows,
pink lips for the women and Lena, and per-film clothes colours.

    import look as LK
    ch = cast.spawn("lena"); T.register(ch, "lena", realistic=True); LK.before(ch, "lena")
    ... T.toonify(sc) ...;  LK.after()
"""
import bpy
import cast

STYLE = dict(cast.CARTOON)
STYLE.update({"l-eye-height2-incr": 0.8, "r-eye-height2-incr": 0.8, "l-eye-height1-incr": 0.3, "r-eye-height1-incr": 0.3,
              "l-eye-bag-decr": 0.6, "r-eye-bag-decr": 0.6, "mouth-scale-horiz-decr": 0.45})
HAIR = {"mom": "elvs_hazel_hair", "me": "short02"}
for _k, _h in HAIR.items():          # this film only: Mom wears her hair down
    cast.CAST[_k] = dict(cast.CAST[_k], hair=_h)
import toon_look as T
import mpfb_tools as M

SKIN = {   # linear rgb, flat comic skin
    "me": (0.78, 0.47, 0.32), "mom": (0.8, 0.5, 0.36), "lena": (0.86, 0.56, 0.42), "guard": (0.66, 0.38, 0.25),
    "oldman": (0.76, 0.5, 0.38), "rescuer": (0.7, 0.42, 0.28),
}
LIPS = {"mom": (0.62, 0.16, 0.18), "lena": (0.8, 0.32, 0.34)}
IRIS = {"me": (0.16, 0.08, 0.03), "mom": (0.2, 0.1, 0.04), "lena": (0.18, 0.3, 0.08), "guard": (0.12, 0.07, 0.03),
        "oldman": (0.12, 0.18, 0.25), "rescuer": (0.1, 0.06, 0.03)}
CLOTHES = {   # override the cast colours to match the earlier «پناهگاه» episodes
    "me": {"elvs_hooded_sweat_jacket1": (0.2, 0.45, 0.22)},
    "mom": {"mindfront_knitted_sweater_01": (0.5, 0.08, 0.17)},
}
_EYES = {}


def before(ch, key):
    """Call after T.register(), before T.toonify()."""
    skin, clothes = T.SKIN[ch.name]
    clothes = dict(clothes)
    clothes.update(CLOTHES.get(key, {}))
    T.SKIN[ch.name] = (SKIN.get(key, skin), clothes)
    for asset, col in CLOTHES.get(key, {}).items():
        for o in ch.parts.get("by_asset", {}).get(asset, []):
            M.set_color(o, col)
    for o in ch.parts.get("Eyebrows", []) + ch.parts.get("Eyelashes", []):
        M.recolor_bsdf(o, lambda nt, bsdf, c: M.mix(nt, c, (0.03, 0.02, 0.015), 0.95))
    for o in ch.parts.get("Eyes", []):
        for m in o.data.materials:
            _EYES[m.name] = IRIS.get(key, (0.16, 0.08, 0.03))
    _LIPS[ch.name] = LIPS.get(key)


_LIPS = {}


def after():
    """Call after T.toonify(): eye colours and lips."""
    for name, iris in _EYES.items():
        m = bpy.data.materials.get(name)
        if not m:
            continue
        nt = m.node_tree
        mul = next((n for n in nt.nodes if n.type == "MIX" and n.blend_type == "MULTIPLY"), None)
        if mul is None or not mul.inputs[6].is_linked:
            continue
        src = mul.inputs[6].links[0].from_socket
        bw = nt.nodes.new("ShaderNodeRGBToBW")
        nt.links.new(src, bw.inputs[0])
        r = nt.nodes.new("ShaderNodeValToRGB")
        r.color_ramp.interpolation = "CONSTANT"
        e = r.color_ramp.elements
        e[0].position, e[0].color = 0.0, (0.01, 0.01, 0.012, 1)
        e[1].position, e[1].color = 0.12, tuple(iris) + (1,)
        w = e.new(0.42)
        w.color = (0.95, 0.95, 0.93, 1)
        nt.links.new(bw.outputs[0], r.inputs[0])
        nt.links.new(r.outputs[0], mul.inputs[6])
    for prefix, col in _LIPS.items():
        if not col:
            continue
        for m in bpy.data.materials:
            if m.name.startswith(prefix + ".lips") and m.use_nodes:
                mul = next((n for n in m.node_tree.nodes if n.type == "MIX" and n.blend_type == "MULTIPLY"), None)
                if mul is not None and not mul.inputs[6].is_linked:
                    mul.inputs[6].default_value = tuple(col) + (1,)
