"""Put Mixamo motion capture (FBX, "Without Skin") on a cast character's game_engine rig.

    import mocap
    clip = mocap.load("blender/mocap/jog_in_circle.fbx")          # imported armature + its fps
    mocap.apply(ch, clip, start=1, length=None, speed=1.0,          # keys ch.rig frames start..
                offset=(x, y, 0), facing=0.0, in_place=False)

Retargeting is done in world space: every mapped target bone gets the source bone's rotation change
from its rest pose, so differences in bone rolls / rest poses between Mixamo and MakeHuman don't matter.
The hips also carry the source's root motion, scaled to the character's leg length.
"""
import bpy, math
from mathutils import Matrix, Quaternion, Vector

MAP = {
    "pelvis": "Hips", "spine_01": "Spine", "spine_02": "Spine1", "spine_03": "Spine2",
    "neck_01": "Neck", "head": "Head",
    "clavicle_l": "LeftShoulder", "upperarm_l": "LeftArm", "lowerarm_l": "LeftForeArm", "hand_l": "LeftHand",
    "clavicle_r": "RightShoulder", "upperarm_r": "RightArm", "lowerarm_r": "RightForeArm", "hand_r": "RightHand",
    "thigh_l": "LeftUpLeg", "calf_l": "LeftLeg", "foot_l": "LeftFoot", "ball_l": "LeftToeBase",
    "thigh_r": "RightUpLeg", "calf_r": "RightLeg", "foot_r": "RightFoot", "ball_r": "RightToeBase",
}
for s, S in (("l", "Left"), ("r", "Right")):
    for f, F in (("thumb", "Thumb"), ("index", "Index"), ("middle", "Middle"), ("ring", "Ring"), ("pinky", "Pinky")):
        for i in (1, 2, 3):
            MAP[f"{f}_0{i}_{s}"] = f"{S}Hand{F}{i}"


class Clip:
    def __init__(self, arm, fps, first, last):
        self.arm, self.fps, self.first, self.last = arm, fps, first, last

    @property
    def seconds(self):
        return (self.last - self.first) / self.fps


def load(path, fps=None):
    before = set(bpy.data.objects)
    sc = bpy.context.scene
    keep_fps = sc.render.fps
    bpy.ops.import_scene.fbx(filepath=path, automatic_bone_orientation=False)
    file_fps = sc.render.fps / sc.render.fps_base
    sc.render.fps = keep_fps
    new = [o for o in bpy.data.objects if o not in before]
    arm = next(o for o in new if o.type == "ARMATURE")
    for o in new:
        o.hide_render = True
        pass                       # (hide_viewport would stop it from being evaluated)
    act = arm.animation_data.action
    first, last = act.frame_range
    return Clip(arm, fps or file_fps, first, last)


def _src_name(arm, short):
    for b in arm.pose.bones:
        if b.name.split(":")[-1] == short:
            return b.name
    return None


def apply(ch, clip, start=1, length=None, speed=1.0, offset=(0, 0, 0), facing=0.0, in_place=False,
          fps=24, put=None):
    """Key ch.rig for `length` frames from `start` (default: the whole clip). facing in degrees (0 = +Y)."""
    sc = bpy.context.scene
    src, tgt = clip.arm, ch.rig
    names = {t: _src_name(src, s) for t, s in MAP.items()}
    names = {t: s for t, s in names.items() if s and t in tgt.pose.bones}
    n = length or int(clip.seconds * fps / speed) + 1
    # target placement: rig object at offset, rotated to `facing`
    rz = math.radians(facing) + math.pi
    tgt.location = offset
    tgt.rotation_mode = "XYZ"
    tgt.rotation_euler = (0, 0, rz)
    for i in range(3):
        tgt.keyframe_insert("location", index=i, frame=start)
    tgt.keyframe_insert("rotation_euler", index=2, frame=start)
    bpy.context.view_layer.update()
    T = tgt.matrix_world.copy()
    Tq = T.to_quaternion()
    # rest data
    S0 = src.matrix_world.copy()
    srest = {b.name: S0 @ b.bone.matrix_local for b in src.pose.bones}
    trest_arm = {b.name: b.bone.matrix_local.copy() for b in tgt.pose.bones}
    hips_src_rest = srest[names["pelvis"]].translation.copy()
    src_leg = (srest[names["thigh_l"]].translation - srest[names["foot_l"]].translation).length
    tgt_leg = (trest_arm["thigh_l"].translation - trest_arm["foot_l"].translation).length
    k = tgt_leg / max(1e-6, src_leg)
    order = [b for b in tgt.pose.bones]          # data order is parent-before-child
    keys = []
    prevq = {}
    for j in range(n):
        f = start + j
        sf = clip.first + j * speed * clip.fps / fps
        sc.frame_set(int(sf), subframe=sf - int(sf))
        Rdes = {}                                    # desired armature-space rotation of each target bone
        for pb in order:
            b = pb.bone
            rest = trest_arm[pb.name]
            if pb.name in names:
                sn = names[pb.name]
                sw = (S0 @ src.pose.bones[sn].matrix).to_quaternion()
                delta = sw @ srest[sn].to_quaternion().inverted()          # world-space change from rest
                want = Tq.inverted() @ delta @ Tq @ rest.to_quaternion()
            else:
                pr = Rdes.get(b.parent.name) if b.parent else None
                if pr is None:
                    want = rest.to_quaternion()
                else:
                    want = pr @ (trest_arm[b.parent.name].to_quaternion().inverted() @ rest.to_quaternion())
            Rdes[pb.name] = want
            if b.parent:
                parent_now = Rdes[b.parent.name] @ trest_arm[b.parent.name].to_quaternion().inverted() \
                    @ rest.to_quaternion()
            else:
                parent_now = rest.to_quaternion()
            q = parent_now.inverted() @ want
            p0 = prevq.get(pb.name)
            if p0 is not None and p0.dot(q) < 0:
                q.negate()
            prevq[pb.name] = q
            keys.append((pb.name, "rotation_quaternion", f, tuple(q)))
        # hips: root motion
        hw = (S0 @ src.pose.bones[names["pelvis"]].matrix).translation
        d = (hw - hips_src_rest) * k
        if in_place:
            d.x = d.y = 0.0
        d_arm = T.inverted().to_3x3() @ d
        rest = trest_arm["pelvis"]
        par = trest_arm["Root"] if "Root" in trest_arm else Matrix()
        loc = rest.to_quaternion().inverted() @ d_arm
        keys.append(("pelvis", "location", f, tuple(loc)))
    # write all keys
    for name, path, f, val in keys:
        pb = tgt.pose.bones[name]
        if path == "rotation_quaternion":
            pb.rotation_mode = "QUATERNION"
            pb.rotation_quaternion = val
        else:
            pb.location = val
        pb.keyframe_insert(path, frame=f)
    return n
