"""Episode animation from the reusable library, organised in the NLA editor.

sequence(rig, items, prefix) builds, bottom to top:
  BODY_00, 01, ...  library strips, one track each, stacked upwards so each one cross-fades (blend_in) over the
                    previous one — transitions between compatible actions without hand-made in-betweens
  ROOT              episode action on the `root` bone: the travel of every strip, weighted by the same cross-fades
                    and integrated, turned by the heading of each item (so a walk that blends into a run speeds up
                    smoothly instead of jumping)
  FOOTLOCK          additive action on foot_ik.L/R computed on the *evaluated* stack (transitions included): planted
                    soles are pinned exactly like in the library bake
  FACE              facial action (expressions, blinks, lip sync) on FACE_CTRL
items: [dict(action="UHS_WALK_Natural", loops=2, blend=8, heading=0, frames=None)]
"""
import bpy
import math
import numpy as np
from mathutils import Vector, Matrix

import project_config as PC
import import_motion as IM
import setup_ik_fk as IKFK


class SequenceError(RuntimeError):
    pass


def _ease(u):
    u = min(1.0, max(0.0, u))
    return u * u * (3 - 2 * u)


def sequence(rig, items, prefix, start=1, heading0=0.0):
    ad = rig.animation_data or rig.animation_data_create()
    for t in list(ad.nla_tracks):
        ad.nla_tracks.remove(t)
    ad.action = None
    spans = []                       # (start, end, blend_in, action, length_one_cycle, loop, heading)
    f = start
    for i, it in enumerate(items):
        act = bpy.data.actions.get(it["action"])
        if act is None or "frames" not in act:
            raise SequenceError(f"library action {it['action']} missing (build the library first)")
        n = int(act["frames"])
        loop = bool(act.get("loop"))
        length = it.get("frames") or (n * it.get("loops", 1) if loop else n - 1)
        if not loop:
            length = min(length, n - 1)
        blend = it.get("blend", 8) if i else 0
        s = f - blend if i else f
        # one track per strip, each above the previous: a strip can only fade in over what lies BELOW it (two
        # alternating tracks put every other strip underneath -> a hard cut where the upper one ended — QC pops)
        tr = ad.nla_tracks.new()
        tr.name = f"BODY_{i:02d}"
        st = tr.strips.new(f"{i:02d}_{act.name}", int(s), act)
        st.action_frame_start, st.action_frame_end = 1, (n + 1 if loop else n)
        st.repeat = length / n if loop else 1.0
        st.use_auto_blend = False                 # first: switching auto-blend off afterwards zeroes blend_in
        st.blend_type = "REPLACE"
        st.extrapolation = "NOTHING"
        st.blend_in = blend
        if blend and abs(st.blend_in - blend) > 1e-6:
            raise SequenceError(f"strip {st.name}: blend_in did not stick ({st.blend_in} != {blend})")
        spans.append(dict(s=s, e=s + length, blend=blend, act=act, n=n, loop=loop,
                          heading=math.radians(it.get("heading", 0.0)) + heading0))
        f = s + length
    end = int(f)
    # weights per frame: later strips fade in over earlier ones (Replace blending)
    frames = list(range(start, end + 1))
    W = np.zeros((len(spans), len(frames)))
    for i, sp in enumerate(spans):
        for j, fr in enumerate(frames):
            if sp["s"] <= fr < sp["e"]:
                W[i, j] = 1.0 if not sp["blend"] else _ease((fr - sp["s"]) / sp["blend"])
    for j in range(len(frames)):                 # Replace: what a strip covers is taken from the ones below
        rest = 1.0
        for i in reversed(range(len(spans))):
            w = W[i, j] * rest
            rest -= w
            W[i, j] = w
    # root: blended per-frame travel of every strip
    pos = Vector((0.0, 0.0))
    path = {}
    for j, fr in enumerate(frames):
        path[fr] = (pos.x, pos.y)
        step = Vector((0.0, 0.0))
        for i, sp in enumerate(spans):
            if W[i, j] <= 0:
                continue
            r = IM.root_fn(sp["act"])
            local = fr - sp["s"] + 1
            a, b = Vector(r(local)), Vector(r(local + 1))
            d = b - a
            c, s_ = math.cos(sp["heading"]), math.sin(sp["heading"])
            step += float(W[i, j]) * Vector((c * d.x - s_ * d.y, s_ * d.x + c * d.y))
        pos = pos + step
    root_act = IM.key_root(rig, start, end, lambda fr: path[fr], f"{prefix}_ROOT")
    # heading: rotate the root bone too (same weights)
    pb = rig.pose.bones["root"]
    keep = ad.action
    ad.action = root_act
    pb.rotation_mode = "XYZ"
    for j, fr in enumerate(frames):
        h = float(sum(W[i, j] * sp["heading"] for i, sp in enumerate(spans)))
        R = pb.bone.matrix_local.to_3x3().inverted() @ Matrix.Rotation(h, 3, "Z") @ pb.bone.matrix_local.to_3x3()
        pb.rotation_euler = R.to_euler("XYZ")
        pb.keyframe_insert("rotation_euler", frame=fr, group="root")
    ad.action = keep
    rt = ad.nla_tracks.new()
    rt.name = "ROOT"
    s = rt.strips.new(root_act.name, start, root_act)
    s.blend_type = "REPLACE"
    s.extrapolation = "HOLD"
    return dict(start=start, end=end, weights=W, spans=spans)


def footlock_track(rig, f0, f1, prefix, name="FOOTLOCK"):
    """Additive foot-lock correction on top of the evaluated stack (call it last: it measures what plays now).
    A second call adds a second layer that catches what the first could not (reach limits, overlapping contacts)."""
    ad = rig.animation_data
    ad.use_nla = True
    deltas, iv, pts = IM.foot_lock_deltas(rig, f0, f1, None)
    act = bpy.data.actions.new(f"{prefix}_{name}")
    keep = ad.action
    ad.action = act
    for s in IM.SIDES:
        pb = rig.pose.bones[f"foot_ik.{s}"]
        for fr in range(f0, f1 + 1):
            pb.location = deltas[s].get(fr, Vector())
            pb.keyframe_insert("location", frame=fr, group=f"footlock {s}")
    ad.action = keep
    tr = ad.nla_tracks.new()
    tr.name = name
    st = tr.strips.new(act.name, f0, act)
    st.use_auto_blend = False
    st.blend_type = "ADD"
    st.influence = 1.0
    st.extrapolation = "NOTHING"
    IKFK.set_interpolation(act)
    return act, iv


def face_track(rig, face_action):
    ad = rig.animation_data
    tr = ad.nla_tracks.new()
    tr.name = "FACE"
    st = tr.strips.new(face_action.name, int(face_action.frame_range[0]), face_action)
    st.blend_type = "REPLACE"
    st.extrapolation = "HOLD"
    return st
