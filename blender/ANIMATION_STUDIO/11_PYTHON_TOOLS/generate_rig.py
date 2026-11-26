"""Rigify rig for a puppet character.

The puppet (blender/puppets) is built on MakeHuman's game_engine skeleton. This module:
  1. fits MPFB's Rigify meta-rig (rigify.human_toes) to the same body and generates the Rigify rig
     (DEF bones carry the weights, animators only touch the controls),
  2. re-weights every clothing item to the DEF bones through MPFB's own mhclo vertex mapping,
  3. moves the cartoon head and face parts onto the Rigify rig (head -> DEF-spine.006, eyes/lids/brows -> face bones),
  4. keeps the old skeleton as <CHAR>_MOTION_SRC (hidden, no longer deforms anything) — Mixamo clips land on it and
     are baked onto the Rigify controls by setup_ik_fk.py,
  5. applies the puppet proportions with Limit Scale constraints on DEF bones and sets IK/FK defaults.

Every step checks its result and raises RigBuildError with a clear message instead of continuing half-built.
"""
import bpy
import os
from mathutils import Vector

import project_config as PC
import rig_config as RC


class RigBuildError(RuntimeError):
    pass


def _need(cond, msg):
    if not cond:
        raise RigBuildError(msg)


def enable_addons():
    import addon_utils
    for mod in ("rigify", "bl_ext.user_default.mpfb"):
        addon_utils.enable(mod, default_set=True)
        _need(addon_utils.check(mod)[1], f"add-on {mod} could not be enabled (run blender/cast/setup.sh?)")


def register_puppets():
    """Add the studio's extra people to the puppet cast (same format as puppets.CAST)."""
    import puppets as PP
    import characters as C
    for k, d in PC.EXTRA_PUPPETS.items():
        if k not in PP.CAST:
            d = dict(d)
            d.setdefault("desc", d["fa"])
            PP.CAST[k] = d
            C.SHEET["pp_" + k] = d


# ------------------------------------------------------------------ build
def build(char_key):
    """Build the full puppet + Rigify rig for CHARACTERS[char_key]. Returns a dict of the important objects."""
    enable_addons()
    register_puppets()
    import puppets as PP
    from bl_ext.user_default.mpfb.services.humanservice import HumanService
    from bl_ext.user_default.mpfb.services.rigservice import RigService
    from bl_ext.user_default.mpfb.services.clothesservice import ClothesService
    from bl_ext.user_default.mpfb.entities.clothes.mhclo import Mhclo
    import mpfb_tools as MT

    info = PC.CHARACTERS[char_key]
    _need(info["puppet"] in PP.CAST, f"no puppet design '{info['puppet']}' for {char_key}")
    ch = PP.spawn(info["puppet"], name=char_key.capitalize())
    PP.finish(ch, smile=0)                         # toon materials + outlines (+ bone scales on the old rig)
    src = ch.rig
    for pb in src.pose.bones:                      # the old rig only feeds motion now: no puppet scales on it
        pb.scale = (1, 1, 1)
    body = ch.body

    # --- Rigify
    before = set(bpy.data.objects)
    meta = HumanService.add_builtin_rig(body, RC.METARIG, import_weights=True)
    if meta is None:
        meta = next((o for o in bpy.data.objects if o not in before and o.type == "ARMATURE"), None)
    _need(meta is not None, "MPFB did not add the Rigify meta-rig")
    rig = RigService.generate_rigify_rig(meta, name=char_key + RC.RIG_SUFFIX, meta_rig_action="delete")
    _need(rig is not None and "torso" in rig.pose.bones, "Rigify generation failed (meta-rig invalid?)")
    rig.name = rig.data.name = char_key + RC.RIG_SUFFIX
    _need(RC.HEAD_DEF in rig.data.bones, f"{RC.HEAD_DEF} missing in the generated rig")

    # --- face bones: same rest placement as on the old skeleton, children of the head deform bone
    bpy.context.view_layer.objects.active = src
    for o in bpy.context.selected_objects:
        o.select_set(False)
    src.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    rest = {n: (src.data.edit_bones[n].head.copy(), src.data.edit_bones[n].tail.copy(), src.data.edit_bones[n].roll)
            for n in RC.FACE_BONES}
    bpy.ops.object.mode_set(mode="OBJECT")
    _need(src.matrix_world == rig.matrix_world, "old and new rig objects are not aligned")
    src.select_set(False)
    rig.select_set(True)
    bpy.context.view_layer.objects.active = rig
    bpy.ops.object.mode_set(mode="EDIT")
    eb = rig.data.edit_bones
    face_coll = rig.data.collections.get("Face (Puppet)") or rig.data.collections.new("Face (Puppet)")
    for n, (h, t, roll) in rest.items():
        b = eb.new(n)
        b.head, b.tail, b.roll = h, t, roll
        b.parent = eb[RC.HEAD_DEF]
        b.use_deform = True
        face_coll.assign(b)
    bpy.ops.object.mode_set(mode="OBJECT")

    # --- move every mesh from the old skeleton to the Rigify rig
    clothes = {}
    for o in list(bpy.data.objects):
        if o.type != "MESH" or o == body:
            continue
        uses_src = any(m.type == "ARMATURE" and m.object == src for m in o.modifiers)
        if not uses_src:
            continue
        asset = o.name.split(".", 1)[1] if "." in o.name and o.name.startswith(body.name + ".") else None
        if asset and asset in ch.sheet["clothes"]:
            for g in list(o.vertex_groups):
                o.vertex_groups.remove(g)
            m = Mhclo()
            m.load(MT._mhclo("clothes", asset))
            ClothesService.interpolate_weights(body, o, rig, m)
            _need(any(g.name.startswith("DEF-") for g in o.vertex_groups), f"no DEF weights transferred to {o.name}")
            clothes[asset] = o
        else:
            g = o.vertex_groups.get("head")
            if g:
                g.name = RC.HEAD_DEF
            _need(all(g.name in rig.data.bones for g in o.vertex_groups), f"{o.name} has groups with no bone")
        for m in o.modifiers:
            if m.type == "ARMATURE" and m.object == src:
                m.object = rig
        mw = o.matrix_world.copy()
        o.parent = rig
        o.matrix_world = mw
    for m in body.modifiers:
        _need(not (m.type == "ARMATURE" and m.object == src), "body still deformed by the old skeleton")
    _need(len(clothes) == len(ch.sheet["clothes"]), f"clothes re-weighted {list(clothes)} != {list(ch.sheet['clothes'])}")

    # --- puppet proportions on the deform bones (forced local scale, last in the constraint stack)
    for bone, s in RC.PROPORTIONS.items():
        pb = rig.pose.bones[bone]
        c = pb.constraints.new("LIMIT_SCALE")
        c.name = "Puppet proportion"
        for ax in "xyz":
            setattr(c, f"use_min_{ax}", True)
            setattr(c, f"use_max_{ax}", True)
            setattr(c, f"min_{ax}", s)
            setattr(c, f"max_{ax}", s)
        c.owner_space = "LOCAL"

    # --- IK/FK defaults
    for part, bones in RC.LIMB_PARENTS.items():
        for b in bones:
            pb = rig.pose.bones[b]
            pb["IK_FK"] = RC.DEFAULT_IK_FK[part]
            pb["IK_Stretch"] = RC.IK_STRETCH
            pb["pole_vector"] = bool(RC.USE_POLE)
    if RC.IK_STRETCH == 0.0:                       # the IK solver may otherwise scale (shrink) the chain bones
        for pb in rig.pose.bones:
            if pb.ik_stretch > 0:
                pb.ik_stretch = 0.0
    for c in rig.data.collections_all:
        if c.name in RC.HIDDEN_COLLECTIONS:
            c.is_visible = False

    # --- the motion source: hidden, renamed, nothing parented to it any more
    src.name = src.data.name = char_key + RC.SRC_SUFFIX
    src.hide_render = True
    src.hide_viewport = True
    for n in ("eye_l", "eye_r"):                   # its eye look-at belongs to the face rig now
        for c in list(src.pose.bones[n].constraints):
            src.pose.bones[n].constraints.remove(c)
    _need(not [o for o in bpy.data.objects if o.parent == src], "objects still parented to the motion source")

    # --- names and collections
    body.name = char_key + "_BODY"
    for asset, o in clothes.items():
        o.name = f"{char_key}_CLOTH_{asset}"
    for o in rig.children:
        if o.type == "MESH" and o != body and not o.name.startswith(char_key + "_CLOTH"):
            o.name = f"{char_key}_FACE_" + o.name.split(" ", 1)[-1].replace(" ", "_")
    root_c = bpy.data.collections.new(char_key)
    bpy.context.scene.collection.children.link(root_c)
    cols = {k: bpy.data.collections.new(f"{char_key}_{k}") for k in ("GEO", "RIG", "HELPERS")}
    for c in cols.values():
        root_c.children.link(c)

    def put(o, c):
        for u in list(o.users_collection):
            u.objects.unlink(o)
        c.objects.link(o)
    put(rig, cols["RIG"])
    for o in rig.children:
        put(o, cols["GEO"])
    put(src, cols["HELPERS"])
    if ch.look_target is not None:
        bpy.data.objects.remove(ch.look_target)    # replaced by the EYES_TARGET bone (setup_face.py)
    cols["HELPERS"].hide_render = True
    for c in bpy.data.collections:
        if c.name.startswith("WGTS"):
            for o in c.objects:
                o.hide_render = True
    hide_under_layers(rig)
    rig["uhas_character"] = char_key
    rig["uhas_version"] = 1
    return dict(rig=rig, src=src, body=body, clothes=clothes, ch=ch, collection=root_c, cols=cols)


def hide_under_layers(rig, margin=0.04):
    """Clothes layering: trouser / shirt vertices that sit under a jacket (higher than the jacket's lowest hem point
    by `margin`, inside its reach) are masked, so they can never poke through it when the body bends (the jeans'
    waistband showed through the hoodie at the hip in walk tests)."""
    outer = [o for o in rig.children if o.type == "MESH" and any(k in o.name for k in ("jacket", "sweater", "hoodie"))]
    inner = [o for o in rig.children if o.type == "MESH" and any(k in o.name for k in ("jeans", "pants", "trousers"))
             and o not in outer]
    done = []
    for top in outer:
        hem = min((top.matrix_world @ v.co).z for v in top.data.vertices)
        for o in inner:
            vg = o.vertex_groups.get("UHAS_under_jacket") or o.vertex_groups.new(name="UHAS_under_jacket")
            idx = [v.index for v in o.data.vertices if (o.matrix_world @ v.co).z > hem + margin]
            if not idx:
                continue
            vg.add(idx, 1.0, "REPLACE")
            if not any(m.type == "MASK" and m.vertex_group == vg.name for m in o.modifiers):
                m = o.modifiers.new("Under jacket", "MASK")
                m.vertex_group = vg.name
                m.invert_vertex_group = True
                while o.modifiers.find(m.name) > 0:   # mask first (before armature / outline) — cheapest, cleanest
                    o.modifiers.move(o.modifiers.find(m.name), o.modifiers.find(m.name) - 1)
            done.append((o.name, len(idx)))
    return done


# ------------------------------------------------------------------ checks used by QC and after building
def sole_points(rig, side):
    """Heel and toe-tip contact points of the shoe (from the evaluated meshes at the current pose), each given in its
    deform bone's space so they can be followed through any animation: {"heel": (bone, local), "ball":..., "tip":...}"""
    S = side.upper()
    dg = bpy.context.evaluated_depsgraph_get()
    pts = []
    for o in rig.children:
        if o.type != "MESH":
            continue
        n = o.name.lower()
        if "cloth" not in n and "body" not in n:
            continue
        ev = o.evaluated_get(dg)
        me = ev.to_mesh()
        mw = o.matrix_world
        for v in me.vertices:
            w = mw @ v.co
            if (w.x > 0) == (S == "L") and w.z < 0.2:
                pts.append(w.copy())
        ev.to_mesh_clear()
    _need(len(pts) > 30, f"no foot geometry found for side {S}")
    zmin = min(p.z for p in pts)
    low = [p for p in pts if p.z < zmin + 0.012]
    heel = max(low, key=lambda p: p.y)                   # characters face -Y: the heel is the +Y end
    tip = min(low, key=lambda p: p.y)
    toe_b = rig.pose.bones[f"DEF-toe.{S}"]
    ball_w = rig.matrix_world @ toe_b.head
    ball = Vector((ball_w.x, ball_w.y, zmin))
    foot_m = rig.matrix_world @ rig.pose.bones[f"DEF-foot.{S}"].matrix
    toe_m = rig.matrix_world @ toe_b.matrix
    return {"heel": (f"DEF-foot.{S}", foot_m.inverted() @ heel), "ball": (f"DEF-toe.{S}", toe_m.inverted() @ ball),
            "tip": (f"DEF-toe.{S}", toe_m.inverted() @ tip), "zmin": zmin}


def point_world(rig, bone, local):
    return rig.matrix_world @ rig.pose.bones[bone].matrix @ local


def weight_report(rig):
    """Every vertex of every deforming mesh must be weighted to at least one DEF bone (or a face bone)."""
    names = {b.name for b in rig.data.bones if b.use_deform}
    out = {}
    for o in rig.children:
        if o.type != "MESH":
            continue
        idx = {g.index for g in o.vertex_groups if g.name in names}
        bad = sum(1 for v in o.data.vertices if not any(g.group in idx and g.weight > 1e-4 for g in v.groups))
        out[o.name] = dict(verts=len(o.data.vertices), unweighted=bad)
    return out
