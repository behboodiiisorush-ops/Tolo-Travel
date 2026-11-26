"""«واگن آخر»-style puppets, better built: MakeHuman body + rig (so every Mixamo clip in blender/mocap works),
the studio cartoon head with a face rig (eyes, lids, brows, mouth keys), puppet proportions (big head, big hands),
bright flat toon colours and black outlines — the look of blender/train_pov, rendered in Cycles.

    import puppets as PP
    ch = PP.spawn("mom")                 # keys: PP.CAST
    mocap.apply(ch, clip, ...)           # body motion
    PP.finish(ch)                        # call after all animation: puppet proportions, toon colours, outlines
"""
import bpy, os, sys, colorsys, math
from mathutils import Vector
HERE = os.path.dirname(os.path.abspath(__file__))
for p in ("studio", "cast"):
    sys.path.insert(0, os.path.join(HERE, "..", p))
import characters as C   # noqa: E402

HEAD, HANDS, FEET = 1.38, 1.2, 1.12          # puppet proportions
# wagon palette: saturated, a little pastel; one strong colour per person
CAST = {
    "me":     dict(fa="من", gender=1.0, age=0.4, height=0.55, weight=0.45, skin=(0.93, 0.74, 0.58),
                   hair=("messy", (0.1, 0.07, 0.06)),
                   clothes={"elvs_hooded_sweat_jacket1": (0.95, 0.62, 0.15), "punkduck_male_classic_jeans": (0.2, 0.3, 0.62),
                            "culturalibre_sneakers": (0.95, 0.95, 0.92)}),
    "mom":    dict(fa="مامان", gender=0.0, age=0.62, height=0.42, weight=0.55, skin=(0.92, 0.72, 0.58),
                   hair=("bun", (0.12, 0.08, 0.06)),
                   clothes={"janexx_old_female_sweater": (0.82, 0.2, 0.42), "toigo_wool_pants": (0.2, 0.18, 0.32),
                            "elvs_flatshoe_plain1": (0.45, 0.2, 0.12)}),
    "kazemi": dict(fa="آقای کاظمی", gender=1.0, age=0.8, height=0.58, weight=0.62, skin=(0.88, 0.66, 0.5),
                   hair=("short", (0.62, 0.6, 0.58)),
                   clothes={"male_elegantsuit01": (0.25, 0.36, 0.62), "culturalibre_male_boots": (0.32, 0.18, 0.1)},
                   glasses=(0.12, 0.1, 0.1), moustache=True),
    "arian":  dict(fa="آرین", gender=1.0, age=0.42, height=0.6, weight=0.45, skin=(0.86, 0.64, 0.48),
                   hair=("short", (0.08, 0.06, 0.05)),
                   clothes={"elvs_crude_t-shirt_male": (0.95, 0.95, 0.9), "elvs_hooded_sweat_jacket1": (0.3, 0.62, 0.3),
                            "punkduck_male_classic_jeans": (0.18, 0.2, 0.3), "culturalibre_male_boots": (0.3, 0.2, 0.12)}),
    "mahsa":  dict(fa="مهسا", gender=0.0, age=0.4, height=0.44, weight=0.42, skin=(0.92, 0.73, 0.6),
                   hair=("bun", (0.07, 0.05, 0.05)),
                   clothes={"mindfront_knitted_sweater_02": (0.15, 0.62, 0.68), "toigo_wool_pants": (0.55, 0.55, 0.6),
                            "elvs_flatshoe_plain1": (0.85, 0.15, 0.15)},
                   glasses=(0.88, 0.12, 0.12)),
    "kian":   dict(fa="کیان", gender=1.0, age=0.4, height=0.5, weight=0.42, skin=(0.94, 0.76, 0.62),
                   hair=("messy", (0.42, 0.25, 0.12)),
                   clothes={"elvs_male_shirt_untucked_bd1": (0.45, 0.7, 0.95), "punkduck_male_classic_jeans": (0.16, 0.2, 0.4),
                            "culturalibre_sneakers": (0.95, 0.95, 0.92)}),
    "rezaei": dict(fa="آقای رضایی", gender=1.0, age=0.85, height=0.52, weight=0.7, skin=(0.88, 0.64, 0.5),
                   hair=("short", (0.7, 0.7, 0.68)),
                   clothes={"elvs_crude_t-shirt_male": (0.92, 0.85, 0.55), "punkduck_male_classic_jeans": (0.15, 0.35, 0.75),
                            "culturalibre_male_boots": (0.25, 0.16, 0.1)}, moustache=True),
    "anchor": dict(fa="گوینده اخبار", gender=1.0, age=0.62, height=0.6, weight=0.55, skin=(0.9, 0.7, 0.56),
                   hair=("short", (0.15, 0.12, 0.1)),
                   clothes={"male_elegantsuit01": (0.12, 0.14, 0.22), "culturalibre_male_boots": (0.1, 0.1, 0.1)}),
}
for k, d in CAST.items():
    d.setdefault("desc", d["fa"])
    C.SHEET["pp_" + k] = d


def _ring(name, c, r, t, mat):
    bpy.ops.mesh.primitive_torus_add(major_radius=r, minor_radius=t, major_segments=32, minor_segments=8,
                                     location=c, rotation=(math.pi / 2, 0, 0))
    o = bpy.context.object
    o.name = name
    o.data.materials.append(mat)
    bpy.ops.object.shade_smooth()
    return o


def spawn(key, name=None):
    """Build the puppet (call before any animation: extras are made in the rest pose)."""
    ch = C.spawn("pp_" + key, name=name or key.capitalize())
    ch.pp_key = key
    d = ch.sheet
    rig = ch.rig
    # the MakeHuman tongue sticks out of the big cartoon head
    for o in list(ch.objects):
        if any(k in o.name.lower() for k in ("tongue", "teeth")):
            ch.objects.remove(o)
            bpy.data.objects.remove(o)
    mo = ch.face.get("mouth")
    if mo is not None and mo.data.shape_keys:               # new shape keys start at 1: close the mouth
        for kb in mo.data.shape_keys.key_blocks[1:]:
            kb.value = 0.0
    hc, R = ch.head_center, 0.13
    re = R * 0.24
    if d.get("glasses"):
        m = toon_mat(f"{ch.name} glasses", d["glasses"], 0.1)
        parts = []
        for s in (1, -1):
            ec = hc + Vector((s * R * 0.38, -R * 0.72, R * 0.02))
            parts.append(_ring(f"{ch.name} glasses {s}", ec + Vector((0, -re * 1.05, 0)), re * 1.25, re * 0.1, m))
            bpy.ops.mesh.primitive_cylinder_add(radius=re * 0.12, depth=R * 0.75,
                                                location=hc + Vector((s * R * 0.74, -R * 0.35, R * 0.06)),
                                                rotation=(math.pi / 2, 0, 0))
            arm = bpy.context.object; arm.data.materials.append(m); parts.append(arm)
        bpy.ops.mesh.primitive_cylinder_add(radius=re * 0.12, depth=R * 0.22,
                                            location=hc + Vector((0, -R * 0.98, R * 0.05)), rotation=(0, math.pi / 2, 0))
        br = bpy.context.object; br.data.materials.append(m); parts.append(br)
        for o in parts:
            C._bind(o, rig, "head"); ch.objects.append(o)
    if d.get("moustache"):
        hair = d["hair"][1]
        m = toon_mat(f"{ch.name} moustache", tuple(c * 0.9 for c in hair), 0.12)
        for s in (1, -1):
            bpy.ops.mesh.primitive_uv_sphere_add(radius=1, segments=16, ring_count=8,
                                                 location=hc + Vector((s * R * 0.14, -R * 0.93, -R * 0.36)))
            o = bpy.context.object
            o.scale = (R * 0.2, R * 0.07, R * 0.07); o.rotation_euler = (0, s * 0.35, 0)
            o.data.materials.append(m); bpy.ops.object.shade_smooth()
            C._sel([o], o); bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
            C._bind(o, rig, "head"); ch.objects.append(o)
    return ch


def _sat(rgb, s=1.12, v=1.0):
    h, ss, vv = colorsys.rgb_to_hsv(*rgb)
    return colorsys.hsv_to_rgb(h, min(1, ss * s), min(1, vv * v))


def toon_mat(name, rgb, glow=0.18):
    m = bpy.data.materials.get("PP " + name)
    if m:
        return m
    m = bpy.data.materials.new("PP " + name)
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    t = nt.nodes.new("ShaderNodeBsdfToon")
    lin = tuple(c ** 2.2 for c in rgb)
    t.inputs["Color"].default_value = (*lin, 1)
    t.inputs["Size"].default_value = 0.62
    t.inputs["Smooth"].default_value = 0.06
    e = nt.nodes.new("ShaderNodeEmission")
    e.inputs["Color"].default_value = (*lin, 1)
    e.inputs["Strength"].default_value = glow
    add = nt.nodes.new("ShaderNodeAddShader")
    nt.links.new(t.outputs[0], add.inputs[0])
    nt.links.new(e.outputs[0], add.inputs[1])
    nt.links.new(add.outputs[0], out.inputs["Surface"])
    return m


def _base(m):
    if not m or not m.node_tree:
        return None
    for n in m.node_tree.nodes:
        if n.type == "BSDF_PRINCIPLED":
            c = n.inputs["Base Color"].default_value
            return tuple(max(0, x) ** (1 / 2.2) for x in c[:3])
        if n.type == "EMISSION":
            return None
    return None


def finish(ch, outline=0.0055, look=None, smile=0.25):
    """After all animation: puppet proportions, eye target, toon colours, outlines."""
    d = ch.sheet
    rig = ch.rig
    if look is not None:
        ch.look_target.location = look
    mo = ch.face.get("mouth")
    if mo is not None and mo.data.shape_keys and smile:
        kb = mo.data.shape_keys.key_blocks["smile"]
        if kb.value == 0.0 and not (mo.data.shape_keys.animation_data and mo.data.shape_keys.animation_data.action):
            kb.value = smile
    for b, s in (("head", HEAD), ("hand_l", HANDS), ("hand_r", HANDS), ("foot_l", FEET), ("foot_r", FEET)):
        rig.pose.bones[b].scale = (s, s, s)
    for o in ch.objects:
        if o.type != "MESH":
            continue
        n = o.name.lower()
        rgb = None
        for ck, col in d["clothes"].items():
            if ck.lower() in n:
                rgb = col
        if rgb is None and o == ch.body:
            rgb = d["skin"]
        for i, slot in enumerate(o.material_slots):
            m = slot.material
            if m and (m.name.startswith("Hull") or m.name.startswith("PP ")):
                continue
            nm = (m.name if m else "x").lower()
            c = rgb
            if c is None:
                if "glint" in nm:
                    continue
                c = _base(m)
                if c is None:
                    continue
            glow = 0.35 if ("skin" in nm or o == ch.body) else 0.18
            slot.material = toon_mat(f"{ch.name} {nm[:30]}", _sat(c), glow)
    # (a suit's open collar shows the outline shell inside it: no shell on suits)
    C.hull_outlines(ch, thickness=outline, skip=("pupil", "glint", "lid", "mouth", "brow", "elegantsuit", "glasses"))
