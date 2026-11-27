"""Acting layers on top of mocap (game_engine rig): faces, hand IK reaches, props carried in a hand, head looks.

    import perform as A
    A.face(ch, f0, f1, lambda f, t: dict(worry=1.6, talking=False))     # shape keys only (blinks automatic)
    A.hand(ch, "r", [(f, target_world_pos_or_None), ...])               # IK reach, eased in/out
    A.carry(obj, ch, "r", f0, f1)                                       # prop follows the hand (keeps its grip)
"""
import bpy, math
from mathutils import Vector, Matrix
import anim

FPS = 24


def face(ch, f0, f1, state):
    sk = ch.body.data.shape_keys
    for f in range(f0, f1 + 1):
        t = f / FPS
        st = dict(state(f, t)); st.setdefault("t", t); st.setdefault("seed", ch.seed)
        st.setdefault("zombie", getattr(ch, "zombie", 0.0))
        for k, v in anim.face(st).items():
            if k in ch.keys:
                ch._put(sk, f'key_blocks["{k}"].value', 0, f, max(0.0, min(1.0, v)))
    ch.flush()


def hand(ch, side, keys, ease=6, pole_offset=(0.0, -0.4, -0.3)):
    """keys: [(frame, Vector world position or None)] — None = follow the mocap (IK off).
    The IK target moves smoothly between keyed positions; influence eases in/out over `ease` frames."""
    rig = ch.rig
    sc = bpy.context.scene
    name = f"ZC_HAND_{rig.name}_{side}"
    tg = bpy.data.objects.get(name) or bpy.data.objects.new(name, None)
    if tg.name not in sc.collection.objects:
        sc.collection.objects.link(tg)
    pole = bpy.data.objects.get(name + "_pole") or bpy.data.objects.new(name + "_pole", None)
    if pole.name not in sc.collection.objects:
        sc.collection.objects.link(pole)
    pb = rig.pose.bones[f"lowerarm_{side}"]
    c = pb.constraints.get("ZC_HandIK") or pb.constraints.new("IK")
    c.name = "ZC_HandIK"; c.target = tg; c.chain_count = 2; c.use_tail = True
    c.pole_target = pole; c.pole_angle = math.radians(-90)
    keys = sorted(keys, key=lambda k: k[0])
    on = [(f, p) for f, p in keys if p is not None]
    for f, p in keys:
        if p is None:
            c.influence = 0.0
        else:
            tg.location = Vector(p); tg.keyframe_insert("location", frame=f)
            c.influence = 1.0
        c.keyframe_insert("influence", frame=f)
    # ease the influence: an extra key `ease` frames before each first IK key and after each last one
    prev = None
    for f, p in keys:
        if p is not None and (prev is None or prev[1] is None):
            c.influence = 0.0; c.keyframe_insert("influence", frame=f - ease)
        if p is None and prev is not None and prev[1] is not None:
            c.influence = 1.0; c.keyframe_insert("influence", frame=prev[0])
        prev = (f, p)
    # elbow pole: below and behind the shoulder, follows the body. Placed with the offset in upper-arm space at a
    # frame where the IK is off, then re-parented to the CLAVICLE (outside the IK chain: parenting it to the
    # upper arm itself made a dependency cycle -> unstable elbow).
    sh = rig.pose.bones[f"upperarm_{side}"]
    f_ref = min(f for f, p in keys if p is not None) - ease - 1
    sc.frame_set(f_ref)
    m_sh = rig.matrix_world @ sh.matrix @ Matrix.Translation((0, sh.length, 0))
    world = m_sh @ Vector(pole_offset)
    cl = rig.pose.bones.get(f"clavicle_{side}") or sh.parent
    pole.parent = rig; pole.parent_type = "BONE"; pole.parent_bone = cl.name
    bpy.context.view_layer.update()
    pole.matrix_world = Matrix.Translation(world)
    return tg


def carry(obj, ch, side, f0, f1, grip=None):
    """Bake obj's world matrix so it moves rigidly with the hand bone from f0 to f1.
    grip: hand-local matrix of the object; default = its relation to the hand at f0."""
    sc = bpy.context.scene
    rig = ch.rig
    bone = rig.pose.bones[f"hand_{side}"]
    sc.frame_set(f0)
    hm = rig.matrix_world @ bone.matrix
    rel = grip if grip is not None else hm.inverted() @ obj.matrix_world
    obj.rotation_mode = "QUATERNION"
    for f in range(f0, f1 + 1):
        sc.frame_set(f)
        m = rig.matrix_world @ bone.matrix @ rel
        obj.matrix_world = m
        obj.keyframe_insert("location", frame=f)
        obj.keyframe_insert("rotation_quaternion", frame=f)


def place(obj, f, loc, quat):
    obj.rotation_mode = "QUATERNION"
    obj.location = loc; obj.rotation_quaternion = quat
    obj.keyframe_insert("location", frame=f); obj.keyframe_insert("rotation_quaternion", frame=f)


def look(ch, f0, f1, target_fn, weight=0.7):
    """Turn the head toward target_fn(f) (world point) by `weight` — a damped track layered on the mocap."""
    rig = ch.rig
    pb = rig.pose.bones["head"]
    name = f"ZC_LOOK_{rig.name}"
    tg = bpy.data.objects.get(name) or bpy.data.objects.new(name, None)
    if tg.name not in bpy.context.scene.collection.objects:
        bpy.context.scene.collection.objects.link(tg)
    c = pb.constraints.get("ZC_Look") or pb.constraints.new("DAMPED_TRACK")
    c.name = "ZC_Look"; c.target = tg; c.track_axis = "TRACK_Y"
    for f in range(f0, f1 + 1, 2):
        tg.location = Vector(target_fn(f)); tg.keyframe_insert("location", frame=f)
    c.influence = 0.0; c.keyframe_insert("influence", frame=f0 - 8)
    c.influence = weight; c.keyframe_insert("influence", frame=f0)
    c.keyframe_insert("influence", frame=f1)
    c.influence = 0.0; c.keyframe_insert("influence", frame=f1 + 8)


def aim_hand(ch, side, f0, f1, point, ease=8):
    """Point the fingers (hand bone +Y) at a world point between f0 and f1 (e.g. palm over the mouth)."""
    rig = ch.rig
    pb = rig.pose.bones[f"hand_{side}"]
    name = f"ZC_AIM_{rig.name}_{side}"
    tg = bpy.data.objects.get(name) or bpy.data.objects.new(name, None)
    if tg.name not in bpy.context.scene.collection.objects:
        bpy.context.scene.collection.objects.link(tg)
    tg.location = Vector(point)
    c = pb.constraints.get("ZC_Aim") or pb.constraints.new("DAMPED_TRACK")
    c.name = "ZC_Aim"; c.target = tg; c.track_axis = "TRACK_Y"
    for f, v in ((f0 - ease, 0.0), (f0, 1.0), (f1, 1.0), (f1 + ease, 0.0)):
        c.influence = v; c.keyframe_insert("influence", frame=f)
