"""Secondary motion as a separate, non-destructive NLA layer (blend type COMBINE: quaternions multiply).

  follow_through(rig, bones, f0, f1)  overlapping action: each bone's world rotation is passed through a damped
                                      spring (it lags behind fast moves and settles with a small overshoot), the
                                      difference is keyed as a local delta rotation.
  stabilize_head(rig, f0, f1)         head stabilisation: high-frequency wobble of the head's world rotation (mocap
                                      jitter, step impacts) is filtered out, the slow look direction is kept.
Both measure the *evaluated* animation (all tracks below), so they work on library previews and full episodes.
Impacts stay sharp where they matter: the spring only acts on the bones you pass (default hands + head).
"""
import bpy
import math
import numpy as np
from mathutils import Quaternion

import project_config as PC


def _world_rot(rig, bone, f0, f1, local=None):
    """World rotations of a bone, f0..f1 (and, if local is a list, its local rotation values in its own mode)."""
    sc = bpy.context.scene
    out = []
    pb = rig.pose.bones[bone]
    for f in range(f0, f1 + 1):
        sc.frame_set(f)
        out.append((rig.matrix_world @ pb.matrix).to_quaternion())
        if local is not None:
            local.append(pb.rotation_quaternion.copy() if pb.rotation_mode == "QUATERNION" else pb.rotation_euler.copy())
    return out


def _as_array(qs):
    a = np.array([tuple(q) for q in qs])
    for i in range(1, len(a)):                    # keep one hemisphere (no sign flips)
        if np.dot(a[i], a[i - 1]) < 0:
            a[i] = -a[i]
    return a


def _spring(a, stiffness=0.32, damping=0.62):
    """Second-order follower on the quaternion components (renormalised): lag + small overshoot."""
    y = a[0].copy()
    v = np.zeros_like(y)
    out = [y.copy()]
    for x in a[1:]:
        v = damping * v + stiffness * (x - y)
        y = y + v
        out.append(y / np.linalg.norm(y))
    return np.array(out)


def _lowpass(a, width=5):
    k = np.exp(-0.5 * (np.arange(-2 * width, 2 * width + 1) / width) ** 2)
    k /= k.sum()
    pad = np.pad(a, ((2 * width, 2 * width), (0, 0)), mode="edge")
    out = np.stack([np.convolve(pad[:, c], k, mode="valid") for c in range(4)], axis=1)
    return out / np.linalg.norm(out, axis=1, keepdims=True)


def _write_layer(rig, track, action_name, per_bone, f0, locals_=None):
    """per_bone: {bone: [(world_now, world_wanted)]} -> COMBINE strip that turns the evaluated rotation into the
    wanted one. Quaternion bones: local delta multiplied on (exact). Euler bones (Rigify hands are ZXY): COMBINE adds
    angles, so the exact target Euler (compatible with the current one) minus the current Euler is keyed."""
    ad = rig.animation_data or rig.animation_data_create()
    act = bpy.data.actions.get(action_name) or bpy.data.actions.new(action_name)
    keep = ad.action
    ad.action = act
    for bone, seq in per_bone.items():
        pb = rig.pose.bones[bone]
        loc = (locals_ or {}).get(bone)
        for i, (now, want) in enumerate(seq):
            f = f0 + i
            d_local = Quaternion(now).inverted() @ Quaternion(want)       # world' = world @ d
            if pb.rotation_mode == "QUATERNION":
                pb.rotation_quaternion = d_local
                pb.keyframe_insert("rotation_quaternion", frame=f, group=f"secondary {bone}")
            else:
                if loc is None:
                    raise ValueError(f"{bone} is Euler: pass its local rotations")
                cur = loc[i]
                tgt = (cur.to_quaternion() @ d_local).to_euler(pb.rotation_mode, cur)
                pb.rotation_euler = (tgt.x - cur.x, tgt.y - cur.y, tgt.z - cur.z)
                pb.keyframe_insert("rotation_euler", frame=f, group=f"secondary {bone}")
    ad.action = keep
    tr = ad.nla_tracks.get(track) or ad.nla_tracks.new()
    tr.name = track
    for s_ in list(tr.strips):
        tr.strips.remove(s_)
    st = tr.strips.new(act.name, f0, act)
    st.blend_type = "COMBINE"
    st.extrapolation = "NOTHING"
    return act


def follow_through(rig, f0, f1, bones=("hand_fk.L", "hand_fk.R"), prefix="SECONDARY", stiffness=0.32, damping=0.62,
                   amount=0.5):
    """amount: how much of the spring's lag is used (1.0 lagged the wrists up to 20° in a walk — too floppy)."""
    per, locs = {}, {}
    for b in bones:
        locs[b] = []
        now = _as_array(_world_rot(rig, b, f0, f1, locs[b]))
        spring = _spring(now, stiffness, damping)
        want = [tuple(Quaternion(a).slerp(Quaternion(w), amount)) for a, w in zip(now, spring)]
        per[b] = list(zip(now, want))
    _write_layer(rig, "SECONDARY", f"{prefix}_FOLLOW", per, f0, locs)
    return {b: [w for _, w in seq] for b, seq in per.items()}


def stabilize_head(rig, f0, f1, amount=0.6, width=4, prefix="SECONDARY"):
    loc = []
    now = _as_array(_world_rot(rig, "head", f0, f1, loc))
    smooth = _lowpass(now, width)
    want = []
    for a, b in zip(now, smooth):
        qa, qb = Quaternion(a), Quaternion(b)
        want.append(tuple(qa.slerp(qb, amount)))
    return _write_layer(rig, "HEAD_STABILIZE", f"{prefix}_HEAD", {"head": list(zip(now, want))}, f0, {"head": loc})


def check(rig, bone, f0, f1, wanted):
    """Max angle (deg) between the evaluated world rotation and the wanted one — proves the layer does what it says."""
    got = _as_array(_world_rot(rig, bone, f0, f1))
    worst = 0.0
    for g, w in zip(got, wanted):
        a = math.degrees(Quaternion(g).rotation_difference(Quaternion(w)).angle)
        worst = max(worst, min(a, 360.0 - a))           # q and -q are the same rotation
    return worst
