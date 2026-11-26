"""IK/FK system: bake motion from the motion-source skeleton onto the Rigify controls, switch IK/FK, action helpers.

How the bake works: every control in rig_config.CONTROL_FROM_SOURCE gets a helper bone on the source skeleton
(child of its source bone, with the control's own rest matrix) and a temporary world-space Copy Transforms to it.
So the control moves exactly like a rigid part of the source bone (nested controls are not transformed twice). Then Blender's own bake (visual keying) writes plain keys and the constraints go.
FK and IK controls are both baked: the same action plays correctly whichever way the IK_FK sliders are set.
"""
import bpy
from mathutils import Matrix

import rig_config as RC

TAG = "UHAS bake"


class BakeError(RuntimeError):
    pass


# ------------------------------------------------------------------ action / f-curve helpers (Blender 5 slotted actions)
def fcurves(action):
    """All f-curves of an action (layered/slotted actions in Blender 4.4+, legacy otherwise)."""
    out = []
    if hasattr(action, "layers") and action.layers:
        for layer in action.layers:
            for strip in layer.strips:
                for bag in getattr(strip, "channelbags", []):
                    out.extend(bag.fcurves)
    elif hasattr(action, "fcurves"):
        out.extend(action.fcurves)
    return out


def drop_locations(action):
    """Remove location keys of rotation-only controls (see rig_config.LOCATION_CONTROLS)."""
    for layer in getattr(action, "layers", []):
        for strip in layer.strips:
            for bag in getattr(strip, "channelbags", []):
                for fc in list(bag.fcurves):
                    if fc.data_path.endswith(".location") and fc.data_path.startswith('pose.bones["'):
                        bone = fc.data_path.split('"')[1]
                        if bone not in RC.LOCATION_CONTROLS:
                            bag.fcurves.remove(fc)


def canonical_quaternions(action):
    """w >= 0 on every rotation_quaternion key. The NLA blends quaternions component by component: two actions
    holding the same rotation as q and -q blend through nonsense (100°/frame pops at walk->run cross-fades — QC).
    Local bone rotations stay well under 180°, so the canonical sign never flips inside an action."""
    by = {}
    for fc in fcurves(action):
        if fc.data_path.endswith("rotation_quaternion"):
            by.setdefault(fc.data_path, {})[fc.array_index] = fc
    flipped = 0
    for path, comps in by.items():
        if len(comps) != 4:
            continue
        w = comps[0]
        for i, kp in enumerate(w.keyframe_points):
            if kp.co.y < 0:
                for c in range(4):
                    k = comps[c].keyframe_points[i]
                    k.co.y = -k.co.y
                    k.handle_left.y = -k.handle_left.y
                    k.handle_right.y = -k.handle_right.y
                flipped += 1
        for c in comps.values():
            c.update()
    return flipped


def make_cyclic(action):
    for fc in fcurves(action):
        if not any(m.type == "CYCLES" for m in fc.modifiers):
            fc.modifiers.new("CYCLES")


def set_interpolation(action, kind="BEZIER", handles="AUTO_CLAMPED"):
    """Baked keys on every frame: Bezier with auto-clamped handles keeps the motion, avoids overshoot between frames."""
    for fc in fcurves(action):
        for kp in fc.keyframe_points:
            kp.interpolation = kind
            kp.handle_left_type = kp.handle_right_type = handles
        fc.update()


# ------------------------------------------------------------------ bake
def _rest(arm):
    if arm.animation_data:
        arm.animation_data.action = None
    for pb in arm.pose.bones:
        pb.location = (0, 0, 0)
        pb.rotation_quaternion = (1, 0, 0, 0)
        pb.rotation_euler = (0, 0, 0)
        pb.scale = (1, 1, 1)


HELPER = "UHAS_"


def _ensure_helpers(rig, src, mapping):
    """One helper bone per control on the source skeleton: child of the source bone, with exactly the control's
    rest matrix. A world-space Copy Transforms to it then makes the control move as a rigid part of the source
    bone, whatever the control's own parents do (no double transforms)."""
    need = [c for c in mapping if HELPER + c not in src.data.bones]
    if not need:
        return
    mode_obj = bpy.context.view_layer.objects.active
    for o in bpy.context.view_layer.objects:
        o.select_set(False)
    hv = src.hide_viewport
    src.hide_viewport = False
    bpy.context.view_layer.objects.active = src
    src.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    eb = src.data.edit_bones
    # both skeletons are fitted to the same body: their armature spaces coincide (object transforms are motion only)
    for c in need:
        bone = rig.data.bones[c]
        h = eb.new(HELPER + c)
        h.head = (0, 0, 0)
        h.tail = (0, max(bone.length, 0.02), 0)
        h.matrix = bone.matrix_local
        h.parent = eb[mapping[c]]
        h.use_connect = False
        h.use_deform = False
    bpy.ops.object.mode_set(mode="OBJECT")
    src.select_set(False)
    src.hide_viewport = hv
    bpy.context.view_layer.objects.active = mode_obj


def attach(rig, src, mapping=None):
    """Copy Transforms (world) from every mapped control to its helper bone on the source skeleton."""
    mapping = mapping or RC.CONTROL_FROM_SOURCE
    missing = [c for c, s in mapping.items() if c not in rig.pose.bones or s not in src.pose.bones]
    if missing:
        raise BakeError(f"bones missing for the bake: {missing[:8]}")
    _ensure_helpers(rig, src, mapping)
    for ctrl in mapping:
        pb = rig.pose.bones[ctrl]
        c = pb.constraints.new("COPY_TRANSFORMS")
        c.name = TAG
        c.target, c.subtarget = src, HELPER + ctrl
        c.owner_space = c.target_space = "WORLD"
    return list(mapping)


def detach(rig):
    for pb in rig.pose.bones:
        for c in list(pb.constraints):
            if c.name == TAG:
                pb.constraints.remove(c)


def bake(rig, src, f0, f1, action_name, mapping=None):
    """Bake the source motion (frames f0..f1) onto the controls into a new action called action_name."""
    sc = bpy.context.scene
    bones = attach(rig, src, mapping)
    was_hidden = src.hide_viewport
    src.hide_viewport = False                     # hidden objects are not evaluated
    for o in bpy.context.view_layer.objects:
        o.select_set(False)
    bpy.context.view_layer.objects.active = rig
    rig.select_set(True)
    rig.hide_viewport = False
    if rig.animation_data is None:
        rig.animation_data_create()
    act = bpy.data.actions.new(action_name)
    rig.animation_data.action = act
    try:
        bpy.ops.object.mode_set(mode="POSE")
        for pb in rig.pose.bones:
            pb.select = pb.name in bones
        with bpy.context.temp_override(active_object=rig, object=rig, selected_objects=[rig]):
            bpy.ops.nla.bake(frame_start=f0, frame_end=f1, step=1, only_selected=True, visual_keying=True,
                             clear_constraints=False, clear_parents=False, use_current_action=True,
                             clean_curves=False, bake_types={"POSE"}, channel_types={"LOCATION", "ROTATION"})
        bpy.ops.object.mode_set(mode="OBJECT")
    finally:
        detach(rig)
        src.hide_viewport = was_hidden
    act = rig.animation_data.action
    if act is None or not fcurves(act):
        raise BakeError(f"the bake of {action_name} wrote no keys")
    correct_feet(rig, f0, f1)
    ik_from_fk(rig, f0, f1)
    drop_locations(act)
    canonical_quaternions(act)
    act.name = action_name
    sc.frame_set(f0)
    return act


# ------------------------------------------------------------------ IK / FK
def set_ik_fk(rig, limb, value, frame=None):
    """limb: 'arm' or 'leg' (both sides) or a single parent bone name. value 0 = IK, 1 = FK. Keys it if frame given."""
    bones = RC.LIMB_PARENTS.get(limb, (limb,))
    for b in bones:
        pb = rig.pose.bones[b]
        pb["IK_FK"] = float(value)
        if frame is not None:
            pb.keyframe_insert('["IK_FK"]', frame=frame)


def ik_fk_mismatch(rig, side="L", limb="leg"):
    """How far the foot / hand jumps (m) when this limb is switched IK <-> FK at the current frame (measured by
    really toggling the switch and comparing the deformed end bone)."""
    parent = f"{'thigh' if limb == 'leg' else 'upper_arm'}_parent.{side}"
    end = f"DEF-{'foot' if limb == 'leg' else 'hand'}.{side}"
    pb = rig.pose.bones[parent]
    keep = pb["IK_FK"]
    pos = []
    for v in (0.0, 1.0):
        pb["IK_FK"] = v
        rig.update_tag()
        bpy.context.view_layer.update()
        e = rig.pose.bones[end]
        pos.append(rig.matrix_world @ e.tail)
    pb["IK_FK"] = keep
    rig.update_tag()
    bpy.context.view_layer.update()
    return (pos[0] - pos[1]).length


def correct_feet(rig, f0, f1, pitch=None):
    """Remove the retarget's constant foot pitch (Mixamo vs MakeHuman foot rest orientation) from the FK foot keys:
    each frame the FK foot gets a fixed extra rotation around its own lateral axis (rig["uhas_foot_pitch_deg"],
    measured by import_motion.calibrate_feet; positive = the capture stands toe-down)."""
    import math
    from mathutils import Quaternion, Vector
    pitch = pitch if pitch is not None else rig.get("uhas_foot_pitch_deg")
    if not pitch:
        return
    sc = bpy.context.scene
    corr = {}
    for S in ("L", "R"):
        pb = rig.pose.bones[f"foot_fk.{S}"]
        ax = (pb.bone.matrix_local.to_3x3().inverted() @ Vector((1, 0, 0))).normalized()
        corr[S] = Quaternion(ax, -math.radians(float(pitch[S])))
    for f in range(f0, f1 + 1):
        sc.frame_set(f)
        for S in ("L", "R"):
            pb = rig.pose.bones[f"foot_fk.{S}"]
            pb.rotation_mode = "QUATERNION"
            pb.rotation_quaternion = pb.rotation_quaternion @ corr[S]
            pb.keyframe_insert("rotation_quaternion", frame=f)


def ik_from_fk(rig, f0, f1, mapping=None):
    """Snap: key the IK controls to where the FK chain puts the limb ends (and knee/elbow poles), every frame.
    Uses rest-relative transforms: ctrl = ORG(now) @ ORG(rest)^-1 @ ctrl(rest), in armature space."""
    mapping = mapping or RC.IK_FROM_FK
    sc = bpy.context.scene
    keep = {b: rig.pose.bones[b]["IK_FK"] for p in RC.LIMB_PARENTS.values() for b in p}
    for b in keep:
        rig.pose.bones[b]["IK_FK"] = 1.0              # evaluate the FK chains
    rel = {c: rig.data.bones[o].matrix_local.inverted() @ rig.data.bones[c].matrix_local for c, o in mapping.items()}
    want = {}
    for f in range(f0, f1 + 1):
        sc.frame_set(f)
        want[f] = {c: rig.pose.bones[o].matrix @ rel[c] for c, o in mapping.items()}
    for b, v in keep.items():
        rig.pose.bones[b]["IK_FK"] = v
    order = sorted(mapping, key=lambda c: len(rig.pose.bones[c].parent_recursive))
    for f in range(f0, f1 + 1):
        sc.frame_set(f)
        for c in order:
            pb = rig.pose.bones[c]
            pb.matrix = want[f][c]
            bpy.context.view_layer.update()
            pb.keyframe_insert("location", frame=f)
            pb.keyframe_insert("rotation_quaternion" if pb.rotation_mode == "QUATERNION" else "rotation_euler", frame=f)


def fk_from_ik(rig, f0, f1, limb="leg", sides=("L", "R")):
    """Snap: key the FK controls so FK gives exactly what IK gives, every frame (after foot locking moved the IK
    feet). Uses the ORG bones (they follow the active chain) and the FK controls' identical rest alignment."""
    sc = bpy.context.scene
    chain = ("thigh", "shin", "foot", "toe") if limb == "leg" else ("upper_arm", "forearm", "hand")
    parent = "thigh_parent" if limb == "leg" else "upper_arm_parent"
    for S in sides:
        rig.pose.bones[f"{parent}.{S}"]["IK_FK"] = 0.0
    for f in range(f0, f1 + 1):
        sc.frame_set(f)
        want = {}
        for S in sides:
            for c in chain:
                org = rig.pose.bones[f"ORG-{c}.{S}"]
                want[(S, c)] = org.matrix.copy()
        for S in sides:
            for c in chain:
                pb = rig.pose.bones[f"{c}_fk.{S}"]
                pb.matrix = want[(S, c)]
                bpy.context.view_layer.update()
                pb.keyframe_insert("rotation_quaternion" if pb.rotation_mode == "QUATERNION" else "rotation_euler",
                                   frame=f)
