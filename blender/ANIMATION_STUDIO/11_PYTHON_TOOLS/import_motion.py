"""Motion import + human motion engine pieces that work on real data:

  import_action()   Mixamo FBX -> <CHAR>_MOTION_SRC -> baked Rigify action (FK + IK), with
                    * root motion split off the body ("feet": speed recovered from the planted foot of an in-place clip,
                      "clip": the clip's own hip travel, smoothed; the pelvis keeps its natural sway/bob),
                    * foot contacts found from the real sole geometry (heel, ball, toe tip),
                    * foot locking: while a foot is planted, the point it stands on (heel at heel-strike, ball/toe during
                      toe-roll) is pinned to the ground; the IK foot is translated, never rotated, so heel strike and
                      toe roll stay as captured; locks ease in/out over a few frames,
                    * loops baked with padding on both sides so contacts across the loop seam are handled.
  foot_lock_deltas() the same lock computed on any evaluated animation (NLA stacks) -> used for the additive
                    FOOTLOCK track of episodes.

Root curve convention: the action stores root_x / root_y (metres, world, character facing -Y) per frame from its
first frame; the body inside the action stays in place.
"""
import bpy
import math
import types
import numpy as np
from mathutils import Vector

import project_config as PC
import rig_config as RC
import motion_config as MC
import setup_ik_fk as IKFK


class MotionError(RuntimeError):
    pass


SIDES = ("L", "R")
POINTS = ("heel", "ball", "tip")


# ------------------------------------------------------------------ soles
def store_soles(rig):
    """Measure the sole contact points once (rest pose, puppet proportions applied) and keep them on the rig."""
    import generate_rig as G
    sc = bpy.context.scene
    if rig.animation_data:
        rig.animation_data.action = None
    for pb in rig.pose.bones:
        pb.location = (0, 0, 0)
        pb.rotation_quaternion = (1, 0, 0, 0)
        pb.rotation_euler = (0, 0, 0)
    sc.frame_set(sc.frame_current)
    data = {}
    for s in SIDES:
        sp = G.sole_points(rig, s)
        data[s] = {k: [sp[k][0], list(sp[k][1])] for k in POINTS}
        data["zmin"] = sp["zmin"]
    rig["uhas_soles"] = data
    return data


def soles(rig):
    d = rig.get("uhas_soles")
    if not d:
        raise MotionError("rig has no measured soles: run store_soles(rig) after building it")
    return d.to_dict() if hasattr(d, "to_dict") else d


def sample_points(rig, f0, f1, root=None):
    """World positions of heel/ball/tip for both feet, frames f0..f1 -> {side: {point: np.array (n,3)}}.
    z is measured from the character's floor (its object's height). root(f) -> (x, y) is added (the root travel
    the body will get in a shot)."""
    sc = bpy.context.scene
    so = soles(rig)
    out = {s: {k: [] for k in POINTS} for s in SIDES}
    mw = rig.matrix_world
    ground = Vector((0, 0, mw.translation.z))       # the floor the character stands on = its object's base
    for f in range(f0, f1 + 1):
        sc.frame_set(f)
        off = Vector((*root(f), 0.0)) - ground if root else -ground
        for s in SIDES:
            for k in POINTS:
                bone, loc = so[s][k]
                p = mw @ rig.pose.bones[bone].matrix @ Vector(loc) + off
                out[s][k].append(tuple(p))
    return {s: {k: np.array(v) for k, v in d.items()} for s, d in out.items()}


# ------------------------------------------------------------------ contacts + locking
def contacts(pts, fps=PC.FPS, use_speed=True, height=None):
    """Planted intervals per side: [(i0, i1)] indices into the sampled frames.
    use_speed=False: by height only (stance on an in-place treadmill, where the planted foot slides)."""
    res = {}
    for s in SIDES:
        P = np.stack([pts[s][k] for k in POINTS])            # (3, n, 3)
        low_k = np.argmin(P[:, :, 2], axis=0)
        n = P.shape[1]
        idx = np.arange(n)
        low = P[low_k, idx]                                   # (n, 3) the lowest point each frame
        vel = np.zeros(n)
        for i in range(n):
            k = low_k[i]
            a, b = max(0, i - 1), min(n - 1, i + 1)
            if b > a:
                vel[i] = np.linalg.norm(P[k, b, :2] - P[k, a, :2]) / (b - a) * fps
        touching = low[:, 2] < MC.LOCK_TOUCH_CM / 100             # a touching / landing point never slides
        planted = (low[:, 2] < (height or MC.CONTACT_HEIGHT)) & ((vel < MC.CONTACT_SPEED) | touching | (not use_speed))
        iv, i = [], 0
        while i < n:
            if planted[i]:
                j = i
                while j + 1 < n and planted[j + 1]:
                    j += 1
                if j - i + 1 >= MC.MIN_CONTACT_FRAMES:
                    iv.append((i, j))
                i = j + 1
            else:
                i += 1
        res[s] = iv
    return res


def lock_offsets(pts, iv):
    """World translation per frame (n,3) per side that pins the active contact point while planted."""
    out = {}
    for s in SIDES:
        P = np.stack([pts[s][k] for k in POINTS])            # (3, n, 3)
        n = P.shape[1]
        D = np.zeros((n, 3))
        for (i0, i1) in iv[s]:
            k = int(np.argmin(P[:, i0, 2]))
            anchor = P[k, i0].copy()
            anchor[2] = 0.0
            prev = np.zeros(3)
            for i in range(i0, i1 + 1):
                kk = int(np.argmin(P[:, i, 2]))
                if kk != k and P[kk, i, 2] < P[k, i, 2] - 0.008:     # roll onto another point: pin that one
                    k = kk
                    anchor = P[k, i] + prev
                    anchor[2] = 0.0
                d = anchor - P[k, i]
                D[i] = d
                prev = d
        # ease in / out around every interval (no pops)
        B = MC.LOCK_BLEND
        E = D.copy()
        for (i0, i1) in iv[s]:
            for j in range(1, B + 1):
                u = 1.0 - j / (B + 1)
                u = u * u * (3 - 2 * u)
                if i0 - j >= 0 and not D[i0 - j].any():
                    E[i0 - j] = D[i0] * u
                if i1 + j < n and not D[i1 + j].any():
                    E[i1 + j] = D[i1] * u
        out[s] = E
    return out


def slip_report(pts, iv, touch=None):
    """Per contact: how far a sole point slides (cm) while it touches the ground, measured point by point
    (heel, ball and tip separately — a heel-to-ball roll is not a slide), and the height range of the contact."""
    touch = touch if touch is not None else MC.QC["touch_cm"] / 100
    out = []
    for s in SIDES:
        P = np.stack([pts[s][k] for k in POINTS])            # (3, n, 3)
        for (a, b) in iv[s]:
            worst = 0.0
            for k in range(len(POINTS)):
                seg = P[k, a:b + 1]
                on = seg[:, 2] < touch
                if on.sum() < 2:
                    continue
                q = seg[on]
                worst = max(worst, float(np.max(np.linalg.norm(q[:, :2] - q[0, :2], axis=1))))
            low = P[np.argmin(P[:, a:b + 1, 2], axis=0), np.arange(a, b + 1)]
            out.append(dict(side=s, i0=int(a), i1=int(b), slip_cm=100 * worst,
                            zmin_cm=float(100 * low[:, 2].min()), zmax_cm=float(100 * low[:, 2].max())))
    return dict(contacts=out, max_slip_cm=max([c["slip_cm"] for c in out], default=0.0))


def _basis_delta(rig, pb, world_delta):
    """Local (basis) location change that moves pose bone pb by world_delta at the current frame."""
    old = pb.matrix.copy()
    new = old.copy()
    new.translation = old.translation + rig.matrix_world.inverted().to_3x3() @ Vector(world_delta)
    a = rig.convert_space(pose_bone=pb, matrix=old, from_space="POSE", to_space="LOCAL")
    b = rig.convert_space(pose_bone=pb, matrix=new, from_space="POSE", to_space="LOCAL")
    return b.translation - a.translation


def foot_lock_deltas(rig, f0, f1, root=None):
    """Compute the lock for the animation as it evaluates now. -> ({side: {frame: basis delta}}, contacts, points)"""
    pts = sample_points(rig, f0, f1, root)
    iv = contacts(pts)
    off = lock_offsets(pts, iv)
    sc = bpy.context.scene
    res = {s: {} for s in SIDES}
    for i, f in enumerate(range(f0, f1 + 1)):
        if not any(off[s][i].any() for s in SIDES):
            continue
        sc.frame_set(f)
        for s in SIDES:
            if off[s][i].any():
                res[s][f] = _basis_delta(rig, rig.pose.bones[f"foot_ik.{s}"], off[s][i])
    return res, iv, pts


def toe_gap(rig, side):
    """Distance between the end of the foot and the start of the toe (m): > 0 means the IK target is out of reach."""
    return (rig.pose.bones[f"ORG-foot.{side}"].tail - rig.pose.bones[f"ORG-toe.{side}"].head).length


def apply_lock_absolute(rig, deltas, max_gap=0.002):
    """Add the deltas into the rig's current action (library bake). A lock never pulls the IK foot out of the
    leg's reach: if it would (toe gap), the delta is shortened (bisection) until the leg reaches again."""
    sc = bpy.context.scene
    shortened = 0
    for s, per in deltas.items():
        pb = rig.pose.bones[f"foot_ik.{s}"]
        for f, d in sorted(per.items()):
            sc.frame_set(f)
            base = pb.location.copy()
            pb.location = base + d
            bpy.context.view_layer.update()
            if toe_gap(rig, s) > max_gap:
                lo, hi = 0.0, 1.0
                for _ in range(7):
                    mid = (lo + hi) / 2
                    pb.location = base + d * mid
                    bpy.context.view_layer.update()
                    if toe_gap(rig, s) > max_gap:
                        hi = mid
                    else:
                        lo = mid
                pb.location = base + d * lo
                shortened += 1
            pb.keyframe_insert("location", frame=f)
    return shortened


# ------------------------------------------------------------------ root curves
def _smooth(a, w):
    if len(a) < 3 or w < 2:
        return a
    k = np.ones(w) / w
    pad = np.pad(a, (w // 2, w - 1 - w // 2), mode="edge")
    return np.convolve(pad, k, mode="valid")


def _unwrap(xy):
    """A looped clip jumps back by one stride at the loop seam: remove those jumps from the hip track."""
    d = np.diff(xy, axis=0)
    step = np.linalg.norm(d, axis=1)
    med = np.median(step) + 1e-4
    bad = step > max(0.12, 6 * med)
    if bad.any() and (~bad).any():
        d[bad] = np.median(d[~bad], axis=0)
    return np.vstack([xy[:1], xy[:1] + np.cumsum(d, axis=0)])


def source_pelvis_xy(src, f0, f1):
    sc = bpy.context.scene
    out = []
    for f in range(f0, f1 + 1):
        sc.frame_set(f)
        p = src.matrix_world @ src.pose.bones["pelvis"].head
        out.append((p.x, p.y))
    return np.array(out)


def root_from_feet(pts, iv, loop, frames, fps=PC.FPS, k0=1):
    """Root curve from the planted feet of an in-place body: per frame, the root moves opposite to the planted
    (lowest) sole point; flight phases are bridged by interpolation; loops get one constant speed."""
    n = len(frames)
    vel = np.full((n, 2), np.nan)
    flat_h = 1.5 * MC.QC["touch_cm"] / 100
    for s in SIDES:
        P = np.stack([pts[s][k] for k in POINTS])
        for i in range(1, n):
            # only a FLAT foot (heel and ball both on the floor) shows the true treadmill speed: at heel strike and
            # toe-off the foot is still braking / pushing (that made the speed ~10 % too low — QC)
            if P[0, i, 2] < flat_h and P[1, i, 2] < flat_h and P[0, i - 1, 2] < flat_h and P[1, i - 1, 2] < flat_h:
                d = -((P[0, i, :2] - P[0, i - 1, :2]) + (P[1, i, :2] - P[1, i - 1, :2])) / 2
                vel[i] = d if np.isnan(vel[i, 0]) else (vel[i] + d) / 2
    ok = ~np.isnan(vel[:, 0])
    if ok.sum() < 3:
        return np.zeros(n), np.zeros(n), 0.0
    if loop:
        m = np.median(vel[ok], axis=0)
        vel[:] = m
    else:
        # non-looping clips (start walking, door, punch): the speed changes all the time and flat frames are rare —
        # per frame, the root follows the point that really touches the floor (no blur), flight is bridged
        touch = MC.QC["touch_cm"] * 1.5 / 100
        vel = np.full((n, 2), np.nan)
        for s in SIDES:
            P = np.stack([pts[s][k] for k in POINTS])
            for i in range(1, n):
                k = int(np.argmin(P[:, i, 2]))
                if P[k, i, 2] < touch and P[k, i - 1, 2] < touch:
                    d = -(P[k, i, :2] - P[k, i - 1, :2])
                    vel[i] = d if np.isnan(vel[i, 0]) else (vel[i] + d) / 2
        ok = ~np.isnan(vel[:, 0])
        if ok.sum() < 3:
            return np.zeros(n), np.zeros(n), 0.0
        idx = np.arange(n)
        for c in range(2):
            vel[:, c] = np.interp(idx, idx[ok], vel[ok, c])
    pos = np.vstack([[0.0, 0.0], np.cumsum(vel[1:], axis=0)])
    i1 = frames.index(k0)
    pos -= pos[i1]
    speed = float(np.linalg.norm(np.median(vel[ok], axis=0)) * fps)
    return pos[:, 0], pos[:, 1], speed


def feet_speed(pts, iv):
    """Speed of the in-place treadmill: how fast planted points move backwards (+Y) in the clip."""
    v = []
    for s in SIDES:
        P = np.stack([pts[s][k] for k in POINTS])
        for (i0, i1) in iv[s]:
            for i in range(i0 + 1, i1 + 1):
                k = int(np.argmin(P[:, i, 2]))
                v.append((P[k, i, 1] - P[k, i - 1, 1]) * PC.FPS)
    if len(v) < 4:
        raise MotionError("not enough planted frames to measure the walking speed")
    return float(np.median(v))


# ------------------------------------------------------------------ one library action
def import_action(rig, src, entry, char_key):
    """Import one MOTION_LIBRARY entry as an action on rig (see the module doc). The source skeleton is made
    evaluable for the duration (hidden objects are not evaluated by Blender) and hidden again afterwards."""
    hv = src.hide_viewport
    src.hide_viewport = False
    try:
        return _import_action(rig, src, entry, char_key)
    finally:
        src.hide_viewport = hv


def _import_action(rig, src, entry, char_key):
    import mocap
    sc = bpy.context.scene
    fps = PC.FPS
    clip = mocap.load(f"{PC.MOCAP_DIR}/{entry['clip']}.fbx")
    try:
        speed = 1.0
        if entry["loop"]:
            # a loop must close on whole frames: one clip period is time-scaled to exactly n frames, and a full cycle
            # of padding on each side lets contacts and locks across the seam come out identical every cycle
            period = clip.seconds * fps
            n = max(2, int(round(period)))
            speed = period / n
            pad = n
        else:
            secs = entry["len"] or (clip.seconds - entry["start"])
            n = max(2, int(round(secs * fps)))
            pad = 0
        K0 = 1 + pad
        # never negative frames: Blender clamps them (that broke the first padding cycle — QC). Frames
        # 1..pad and pad+n+1.. are padding, the kept range K0..K0+n-1 is shifted to 1..n at the end.
        f0, f1 = 1, n + 2 * pad
        K0 = 1 + pad
        if src.animation_data:
            src.animation_data.action = None
        src.location = (0, 0, 0)
        holder = types.SimpleNamespace(rig=src, name=src.name)
        mocap.LAST.pop(src.name, None)
        mocap.apply(holder, clip, start=f0, length=f1 - f0 + 1, src_from=entry["start"], facing=180.0,
                    in_place=False, loop=entry["loop"], speed=speed)
    finally:
        bpy.data.objects.remove(clip.arm)
        for a in list(bpy.data.armatures):
            if a.users == 0:
                bpy.data.armatures.remove(a)
    lift = -soles(rig)["zmin"]
    frames = list(range(f0, f1 + 1))
    # root from the clip's hip travel (smoothed), removed from the body
    mode = entry["root"]
    raw = source_pelvis_xy(src, f0, f1)
    xy = _unwrap(raw)
    travel = float(np.linalg.norm(xy[-1] - xy[0])) / max(1e-6, (f1 - f0) / fps)
    if mode == "auto":
        mode = "clip" if travel > 0.15 else "feet"
    entry = dict(entry, root=mode)
    if mode == "clip":
        w = int(fps * 0.6) | 1
        if entry["loop"]:                         # cyclic clip: the root goes at constant speed (no stride wobble)
            t = np.arange(len(frames))
            rx = np.polyval(np.polyfit(t, xy[:, 0], 1), t)
            ry = np.polyval(np.polyfit(t, xy[:, 1], 1), t)
        else:
            rx, ry = _smooth(xy[:, 0], w), _smooth(xy[:, 1], w)
        # removed from the body: the smooth travel plus the loop-seam jumps of the raw track (raw - unwrapped),
        # so the pelvis keeps only its natural sway / bob around the origin
        bx, by = rx + raw[:, 0] - xy[:, 0], ry + raw[:, 1] - xy[:, 1]
        i1 = frames.index(K0)
        rx, ry = rx - rx[i1], ry - ry[i1]          # relative: the root travel stored with the action
    else:
        rx = np.zeros(len(frames))
        ry = np.zeros(len(frames))
        bx = np.zeros(len(frames))
        by = np.zeros(len(frames))
    for i, f in enumerate(frames):
        src.location = (-bx[i], -by[i], lift)
        src.keyframe_insert("location", frame=f)
    act = IKFK.bake(rig, src, f0, f1, entry["name"])
    for b in RC.LIMB_PARENTS["leg"]:
        rig.pose.bones[b]["IK_FK"] = 0.0
    # travel: what the planted feet really push (the body is in place now). Hip travel is NOT used for the root:
    # Mixamo's hips and the retargeted leg angles disagree by ~20 % (different thigh/shin proportions), so a root
    # from the hips made the planted feet slide — measured by QC.
    if entry["root"] in ("feet", "clip"):
        pts = sample_points(rig, f0, f1)
        rx, ry, v = root_from_feet(pts, contacts(pts, use_speed=False), entry["loop"], frames, k0=K0)
        act["speed"] = v
    rootf = (lambda f: (rx[frames.index(f)], ry[frames.index(f)])) if entry["root"] != "none" else None
    info = {}
    _raw_pts = sample_points(rig, K0, K0 + n - 1, rootf)
    raw = slip_report(_raw_pts, contacts(_raw_pts))
    act["raw_slip_cm"] = raw["max_slip_cm"]
    if entry["lock"]:
        d, iv, _ = foot_lock_deltas(rig, f0, f1, rootf)
        act["lock_shortened_frames"] = apply_lock_absolute(rig, d)
        IKFK.fk_from_ik(rig, f0, f1, "leg")          # FK legs match the locked IK legs (no pop when switching)
        info["contacts"] = {s: [(frames[a] - pad, frames[b] - pad) for a, b in iv[s]] for s in SIDES}
    # trim the padding, finish the action
    for fc in IKFK.fcurves(act):
        for i in range(len(fc.keyframe_points) - 1, -1, -1):
            x = fc.keyframe_points[i].co.x
            if x < K0 or x > K0 + n - 1:
                fc.keyframe_points.remove(fc.keyframe_points[i], fast=True)
        for kp in fc.keyframe_points:                 # kept cycle -> frames 1..n
            kp.co.x -= pad
            kp.handle_left.x -= pad
            kp.handle_right.x -= pad
        fc.update()
    IKFK.set_interpolation(act)
    if entry["loop"]:
        IKFK.make_cyclic(act)
    i1 = frames.index(K0)
    act["root_x"] = [float(x) for x in rx[i1:i1 + n]]
    act["root_y"] = [float(y) for y in ry[i1:i1 + n]]
    act["loop"] = bool(entry["loop"])
    act["frames"] = n
    act["fps"] = fps
    act["source_clip"] = entry["clip"]
    act["root_mode"] = entry["root"]
    act["character"] = char_key
    act["folder"] = entry["folder"]
    if "contacts" in info:
        act["contacts"] = str(info["contacts"])
    # a cyclic action spans n+1 frames (frame n+1 == frame 1 through the Cycles modifiers): an NLA strip of 1..n
    # would repeat every n-1 frames and lose one frame of travel per cycle (8 cm per walk cycle — found by QC)
    act.frame_range = (1, n + 1) if entry["loop"] else (1, n)
    act.use_frame_range = True
    act.use_cyclic = bool(entry["loop"])
    act.use_fake_user = True
    try:
        act.asset_mark()
        act.asset_data.description = f"{entry['clip']} ({entry['folder']}) root={entry['root']}"
        act.asset_data.tags.new(entry["folder"].lower())
    except Exception:
        pass
    src.animation_data.action = None
    return act


def root_fn(action, offset=(0.0, 0.0)):
    """root(f) for an action played from frame 1 (loops continue the travel)."""
    rx, ry = list(action["root_x"]), list(action["root_y"])
    n = len(rx)
    loop = bool(action.get("loop"))
    stepx = (rx[-1] - rx[0]) * n / max(1, n - 1)
    stepy = (ry[-1] - ry[0]) * n / max(1, n - 1)

    def f(fr):
        i = fr - 1
        if loop:
            c, j = divmod(i, n)
            return (offset[0] + rx[j] + c * stepx, offset[1] + ry[j] + c * stepy)
        j = min(max(i, 0), n - 1)
        return (offset[0] + rx[j], offset[1] + ry[j])
    return f


def key_root(rig, f0, f1, rootfn, action_name):
    """Key the `root` bone along rootfn(f) -> (x, y): metres in the character's own frame (rest: facing -Y), into
    its own action (episode-specific). Turn / place the whole character with the rig object's transform."""
    if rig.animation_data is None:
        rig.animation_data_create()
    act = bpy.data.actions.get(action_name) or bpy.data.actions.new(action_name)
    keep = rig.animation_data.action
    rig.animation_data.action = act
    pb = rig.pose.bones["root"]
    inv = pb.bone.matrix_local.to_3x3().inverted()
    for f in range(f0, f1 + 1):
        x, y = rootfn(f)
        pb.location = inv @ Vector((x, y, 0.0))
        pb.keyframe_insert("location", frame=f, group="root")
    rig.animation_data.action = keep
    return act


def nla_strip(rig, track_name, action, start, repeat=1.0, blend_in=0, blend_out=0, blend_type="REPLACE"):
    """Put an action on an NLA track (created if missing) as a strip starting at `start`."""
    ad = rig.animation_data or rig.animation_data_create()
    tr = ad.nla_tracks.get(track_name) or ad.nla_tracks.new()
    tr.name = track_name
    st = tr.strips.new(action.name, int(start), action)
    if action.get("loop"):
        st.action_frame_start, st.action_frame_end = 1, int(action["frames"]) + 1
    st.repeat = repeat
    st.blend_in, st.blend_out = blend_in, blend_out
    st.blend_type = blend_type
    st.extrapolation = "NOTHING"
    st.use_auto_blend = False
    return st


def foot_pitch(rig, f0, f1):
    """Mean sole pitch (degrees, + = toe-down) per side over frames f0..f1, relative to the rest pose."""
    import math
    rest_d = {}
    so = soles(rig)
    for s in SIDES:                                  # rest: heel/ball height difference of the measured points
        rest_d[s] = (so[s]["heel"][1], so[s]["ball"][1])
    pts = sample_points(rig, f0, f1)
    out = {}
    for s in SIDES:
        h, b = pts[s]["heel"], pts[s]["ball"]
        dz = float(np.mean(h[:, 2] - b[:, 2]))
        dy = float(np.mean(np.linalg.norm(h[:, :2] - b[:, :2], axis=1)))
        out[s] = math.degrees(math.atan2(dz, dy))
    return out


def calibrate_feet(rig, src, clip="breathing_idle", seconds=4.0):
    """Mixamo's foot and the MakeHuman foot have different rest orientations: retargeted feet stood ~13-15° toe-down
    (found by QC: soles never flat, locks out of reach). Measured on a standing clip (both soles must be flat) in FK,
    relative to the rest pose; stored as rig["uhas_foot_pitch_deg"]; setup_ik_fk.correct_feet() removes it from every
    bake. The function then re-bakes the clip and returns (measured, remaining) — remaining must be ~0."""
    import setup_ik_fk as K
    entry = dict(name="UHAS_CALIBRATION", clip=clip, start=0.0, len=seconds, loop=False, root="none", lock=False,
                 folder="IDLE")
    hv = src.hide_viewport
    src.hide_viewport = False
    try:
        rig["uhas_foot_pitch_deg"] = {"L": 0.0, "R": 0.0}
        rest = _pitch_at_rest(rig)
        res = []
        for _ in range(2):
            act = _import_action(rig, src, entry, "CAL")
            for b in RC.LIMB_PARENTS["leg"]:
                rig.pose.bones[b]["IK_FK"] = 1.0
            n = int(act["frames"])
            p = foot_pitch(rig, 1, n)
            for b in RC.LIMB_PARENTS["leg"]:
                rig.pose.bones[b]["IK_FK"] = 0.0
            bpy.data.actions.remove(act)
            delta = {s: p[s] - rest[s] for s in SIDES}
            res.append(delta)
            if not res[1:]:
                # the retarget error is a property of the two skeletons: the same on both feet. The flatter foot
                # shows it; the other one adds the actor's own stance (weight on one leg), which is kept.
                sym = min(delta.values(), key=abs)
                rig["uhas_foot_pitch_deg"] = {s: float(sym) for s in SIDES}
        return res[0], res[1]
    finally:
        src.hide_viewport = hv


def _pitch_at_rest(rig):
    ad = rig.animation_data
    keep = ad.action if ad else None
    if ad:
        ad.action = None
    for pb in rig.pose.bones:
        pb.location = (0, 0, 0)
        pb.rotation_quaternion = (1, 0, 0, 0)
        pb.rotation_euler = (0, 0, 0)
    bpy.context.view_layer.update()
    p = foot_pitch(rig, bpy.context.scene.frame_current, bpy.context.scene.frame_current)
    if ad:
        ad.action = keep
    return p
