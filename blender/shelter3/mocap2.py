"""Fast Mixamo retarget for long films (same maths as cast/mocap.py, made cheap):
  * load() samples every clip once (world rotations of its bones per source frame) and deletes the FBX,
    so later no frame_set on a heavy scene is needed;
  * apply() keys every `step` frames into a buffer; flush(ch) writes the F-curves in one go.

    import mocap2 as MC
    clip = MC.load(path)                       # before the heavy scene is built
    MC.apply(ch, clip, start, length, speed, offset, facing, in_place, src_from, loop, place, step=2)
    MC.flush(ch)                               # before reading the pose back (pos_at, camera aims ...)
"""
import bpy, math
from mathutils import Matrix, Quaternion, Vector
from mocap import MAP, _src_name

BUF = {}


class Clip:
    def __init__(self, fps, first, last, rest, rots, hips, feet=None):
        self.fps, self.first, self.last, self.feet = fps, first, last, feet
        self.rest, self.rots, self.hips = rest, rots, hips    # rest: name -> Matrix; rots: name -> [Quaternion]

    @property
    def seconds(self):
        return (self.last - self.first) / self.fps


def load(path, fps=None):
    sc = bpy.context.scene
    before = set(bpy.data.objects)
    keep_fps = sc.render.fps
    bpy.ops.import_scene.fbx(filepath=path, automatic_bone_orientation=False)
    file_fps = sc.render.fps / sc.render.fps_base
    sc.render.fps = keep_fps
    new = [o for o in bpy.data.objects if o not in before]
    arm = next(o for o in new if o.type == "ARMATURE")
    act = arm.animation_data.action
    first, last = [int(round(v)) for v in act.frame_range]
    S0 = arm.matrix_world.copy()
    names = {s: _src_name(arm, s) for s in set(MAP.values())}
    names = {s: n for s, n in names.items() if n}
    rest = {s: S0 @ arm.pose.bones[n].bone.matrix_local for s, n in names.items()}
    rots = {s: [] for s in names}
    hips, feet = [], []
    keep_frame = sc.frame_current
    for f in range(first, last + 1):
        sc.frame_set(f)
        for s, n in names.items():
            rots[s].append((S0 @ arm.pose.bones[n].matrix).to_quaternion())
        hips.append((S0 @ arm.pose.bones[names["Hips"]].matrix).translation.copy())
        feet.append(((S0 @ arm.pose.bones[names["LeftFoot"]].matrix).translation.copy(),
                     (S0 @ arm.pose.bones[names["RightFoot"]].matrix).translation.copy()))
    sc.frame_set(keep_frame)
    for o in new:
        bpy.data.objects.remove(o, do_unlink=True)
    return Clip(fps or file_fps, first, last, rest, rots, hips, feet)


def _sample(clip, s, sf):
    i = sf - clip.first
    a = int(math.floor(i))
    u = i - a
    seq = clip.rots[s]
    a = max(0, min(len(seq) - 1, a))
    b = min(len(seq) - 1, a + 1)
    return seq[a].slerp(seq[b], u)


def _hips(clip, sf):
    i = sf - clip.first
    a = int(math.floor(i))
    u = i - a
    a = max(0, min(len(clip.hips) - 1, a))
    b = min(len(clip.hips) - 1, a + 1)
    return clip.hips[a].lerp(clip.hips[b], u)


def _put(rig, path, idx, f, v):
    BUF.setdefault(rig.name, {}).setdefault((path, idx), {})[f] = v


def apply(ch, clip, start=1, length=None, speed=1.0, offset=(0, 0, 0), facing=0.0, in_place=False,
          fps=24, src_from=0.0, loop=False, place=None, step=2):
    tgt = ch.rig
    names = {t: s for t, s in MAP.items() if s in clip.rots and t in tgt.pose.bones}
    n = length or int(max(0.0, clip.seconds - src_from) * fps / speed) + 1
    trest = {b.name: b.bone.matrix_local.copy() for b in tgt.pose.bones}
    hips_src_rest = clip.rest["Hips"].translation.copy()
    src_leg = (clip.rest["LeftUpLeg"].translation - clip.rest["LeftFoot"].translation).length
    tgt_leg = (trest["thigh_l"].translation - trest["foot_l"].translation).length
    k = tgt_leg / max(1e-6, src_leg)
    off = {}
    for t, s in names.items():
        tdir = trest[t].to_quaternion() @ Vector((0, 1, 0))
        sdir = clip.rest[s].to_quaternion() @ Vector((0, 1, 0))
        off[t] = tdir.rotation_difference(sdir)
    srest_q = {s: clip.rest[s].to_quaternion() for s in clip.rest}
    order = list(tgt.pose.bones)
    js = list(range(0, n, step))
    if js[-1] != n - 1:
        js.append(n - 1)
    for j in js:
        f = start + j
        sf = clip.first + src_from * clip.fps + j * speed * clip.fps / fps
        if loop:
            span = clip.last - clip.first
            sf = clip.first + (sf - clip.first) % span
        sf = min(sf, clip.last)
        if place is not None:
            off_j, fac_j = place(j)
        else:
            off_j, fac_j = offset, facing
        for i in range(3):
            _put(tgt, "location", i, f, off_j[i])
        _put(tgt, "rotation_euler", 2, f, math.radians(fac_j) + math.pi)
        Rdes = {}
        for pb in order:
            b = pb.bone
            rest = trest[pb.name]
            rq = rest.to_quaternion()
            if pb.name in names:
                s = names[pb.name]
                delta = _sample(clip, s, sf) @ srest_q[s].inverted()
                want = delta @ off[pb.name] @ rq
            else:
                pr = Rdes.get(b.parent.name) if b.parent else None
                want = rq if pr is None else pr @ (trest[b.parent.name].to_quaternion().inverted() @ rq)
            Rdes[pb.name] = want
            if b.parent:
                parent_now = Rdes[b.parent.name] @ trest[b.parent.name].to_quaternion().inverted() @ rq
            else:
                parent_now = rq
            q = parent_now.inverted() @ want
            for i in range(4):
                _put(tgt, f'pose.bones["{pb.name}"].rotation_quaternion', i, f, q[i])
        d = (_hips(clip, sf) - hips_src_rest) * k
        if in_place:
            d.x = d.y = 0.0
        loc = trest["pelvis"].to_quaternion().inverted() @ d
        for i in range(3):
            _put(tgt, 'pose.bones["pelvis"].location', i, f, loc[i])
    return n


def flush(ch):
    rig = ch.rig
    buf = BUF.get(rig.name)
    if not buf:
        return
    for pb in rig.pose.bones:
        pb.rotation_mode = "QUATERNION"
    rig.rotation_mode = "XYZ"
    # quaternion sign continuity per bone
    bones = {}
    for (path, idx) in buf:
        if path.endswith("rotation_quaternion"):
            bones.setdefault(path, None)
    for path in bones:
        comps = [buf[(path, i)] for i in range(4)]
        prev = None
        for f in sorted(comps[0]):
            q = [c[f] for c in comps]
            if prev is not None and sum(a * b for a, b in zip(prev, q)) < 0:
                q = [-v for v in q]
                for i in range(4):
                    comps[i][f] = q[i]
            prev = q
    ad = rig.animation_data or rig.animation_data_create()
    if ad.action is None:
        ad.action = bpy.data.actions.new(f"{rig.name}_mocap")
    act = ad.action
    for (path, idx), pts in buf.items():
        if hasattr(act, "fcurve_ensure_for_datablock"):
            fc = act.fcurve_ensure_for_datablock(rig, path, index=idx)
        else:
            fc = act.fcurves.find(path, index=idx) or act.fcurves.new(path, index=idx)
        fc.keyframe_points.clear()
        fr_ = sorted(pts)
        fc.keyframe_points.add(len(fr_))
        co = []
        for f in fr_:
            co += [f, pts[f]]
        fc.keyframe_points.foreach_set("co", co)
        fc.keyframe_points.foreach_set("interpolation", [2] * len(fr_))   # LINEAR
        fc.update()
