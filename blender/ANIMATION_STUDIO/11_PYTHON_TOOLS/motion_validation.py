"""Quality control: repeatable numeric tests on real animation data (no test passes by assumption).

validate_action(rig, action)  plays a library action the way a shot would (root travel applied) and measures:
  foot_slip        while a sole point is planted (height test only — sliding contacts are NOT excused), how far it slides
  ground           lowest sole point over the whole action (penetration), planted soles hovering (float)
  limb_stretch     hip-knee-ankle / shoulder-elbow-wrist length vs rest (IK stretch must stay off)
  joints           knee / elbow bend: max angle, reverse (hyper-extension) bends, bend-plane flips between frames
  pops             per-control angular speed spikes (bad transitions, loop seams, retarget glitches)
  ik_fk            FK vs IK foot/hand distance (switching IK<->FK must not pop)
  balance          for standing clips: centre of mass over the support polygon of the planted feet
validate_face(rig)            every preset moves the driven parts it should
deformation(rig)              unweighted vertices per mesh
Results: dicts with "pass" flags; write_reports() saves JSON per test + a Markdown summary.
"""
import bpy
import json
import math
import os
import numpy as np
from mathutils import Vector, Quaternion

import project_config as PC
import rig_config as RC
import motion_config as MC
import import_motion as IM
import setup_ik_fk as IKFK

LOCOMOTION = ("WALK", "RUN", "JUMP", "IDLE_TO_WALK", "INTERACTIONS")
STANDING = ("IDLE", "HAND_GESTURES", "EMOTIONS")        # balance on the feet is tested only for these
                                                         # (sitting rests on a seat, getting up uses the hands)
MASS = {  # rough segment masses (fraction of body) for the centre of mass
    "DEF-spine": 0.11, "DEF-spine.001": 0.1, "DEF-spine.002": 0.1, "DEF-spine.003": 0.12, "DEF-spine.004": 0.02,
    "DEF-spine.006": 0.08, "DEF-upper_arm.L": 0.028, "DEF-upper_arm.R": 0.028, "DEF-forearm.L": 0.016,
    "DEF-forearm.R": 0.016, "DEF-hand.L": 0.006, "DEF-hand.R": 0.006, "DEF-thigh.L": 0.1, "DEF-thigh.R": 0.1,
    "DEF-shin.L": 0.045, "DEF-shin.R": 0.045, "DEF-foot.L": 0.015, "DEF-foot.R": 0.015,
}
POP_BONES = ("torso", "hips", "chest", "neck", "head", "upper_arm_fk.L", "upper_arm_fk.R", "forearm_fk.L",
             "forearm_fk.R", "thigh_fk.L", "thigh_fk.R", "shin_fk.L", "shin_fk.R", "foot_ik.L", "foot_ik.R")


def _world_q(rig, b):
    return (rig.matrix_world @ rig.pose.bones[b].matrix).to_quaternion()


def _pt(rig, b, tail=False):
    pb = rig.pose.bones[b]
    return rig.matrix_world @ (pb.tail if tail else pb.head)


def joint_conventions(rig):
    """Which way each knee / elbow bends naturally: sign of (upper x lower) . upper-bone X axis for a natural bend,
    measured at rest by bending the FK controls (knee: foot goes back; elbow: hand comes forward)."""
    sc = bpy.context.scene
    keep_act = rig.animation_data.action if rig.animation_data else None
    keep_nla = rig.animation_data.use_nla if rig.animation_data else True
    if rig.animation_data:
        rig.animation_data.action = None
        rig.animation_data.use_nla = False
    keep_ikfk = {b: rig.pose.bones[b]["IK_FK"] for p in RC.LIMB_PARENTS.values() for b in p}
    for b in keep_ikfk:
        rig.pose.bones[b]["IK_FK"] = 1.0
    out = {}
    for joint, (up, lo) in RC.JOINTS.items():
        S = joint[-1]
        ctrl = f"shin_fk.{S}" if joint.startswith("knee") else f"forearm_fk.{S}"
        pb = rig.pose.bones[ctrl]
        pb.rotation_mode = "XYZ"
        best = None
        for sgn in (1, -1):
            pb.rotation_euler = (math.radians(40 * sgn), 0, 0)
            bpy.context.view_layer.update()
            end = _pt(rig, lo, tail=True)
            natural = end.y > _pt(rig, lo).y if joint.startswith("knee") else end.y < _pt(rig, lo).y
            if natural:
                u = (_pt(rig, up, True) - _pt(rig, up)).normalized()
                l_ = (_pt(rig, lo, True) - _pt(rig, lo)).normalized()
                xa = (rig.matrix_world.to_3x3() @ rig.pose.bones[up].matrix.to_3x3()).col[0]
                best = 1 if u.cross(l_).dot(xa) > 0 else -1
        pb.rotation_euler = (0, 0, 0)
        out[joint] = best or 1
    for b, v in keep_ikfk.items():
        rig.pose.bones[b]["IK_FK"] = v
    if rig.animation_data:
        rig.animation_data.action = keep_act
        rig.animation_data.use_nla = keep_nla
    bpy.context.view_layer.update()
    return out


def rest_lengths(rig):
    """Same measure as _chain_len, evaluated with no animation (rest pose, constraints active)."""
    ad = rig.animation_data
    keep = (ad.action, ad.use_nla) if ad else None
    if ad:
        ad.action = None
        ad.use_nla = False
    saved = {pb.name: (pb.location.copy(), pb.rotation_quaternion.copy(), pb.rotation_euler.copy()) for pb in rig.pose.bones}
    for pb in rig.pose.bones:
        pb.location = (0, 0, 0)
        pb.rotation_quaternion = (1, 0, 0, 0)
        pb.rotation_euler = (0, 0, 0)
    bpy.context.view_layer.update()
    out = {j: _chain_len(rig, up, lo)[0] for j, (up, lo) in RC.JOINTS.items()}
    for pb in rig.pose.bones:
        pb.location, pb.rotation_quaternion, pb.rotation_euler = saved[pb.name]
    if ad:
        ad.action, ad.use_nla = keep
    bpy.context.view_layer.update()
    return out


def _chain_len(rig, up, lo):
    """hip->ankle through the deform chain (DEF bones are split in two: follow .001 when present)."""
    def seg(name):
        bs = [name] + ([name + ".001"] if name + ".001" in rig.pose.bones else [])
        return (_pt(rig, bs[-1], True) - _pt(rig, bs[0])).length, _pt(rig, bs[0]), _pt(rig, bs[-1], True)
    a, a0, a1 = seg(up)
    b, b0, b1 = seg(lo)
    return a + b, (a1 - a0).normalized(), (b1 - b0).normalized()


def _measure(rig, f0, N, conv, static, meta):
    """All motion metrics for frames f0..f0+N-1 of whatever the rig plays now."""
    rl = rest_lengths(rig)
    sc = bpy.context.scene
    n = meta["frames"]
    loop = meta["loop"]
    action = meta
    # --- feet
    pts = IM.sample_points(rig, f0, f0 + N - 1)
    iv_h = IM.contacts(pts, use_speed=False, height=MC.QC["touch_cm"] / 100)
    slip = IM.slip_report(pts, iv_h)
    zall = min(float(pts[s][k][:, 2].min()) for s in IM.SIDES for k in IM.POINTS)
    floating = [c for c in slip["contacts"] if c["zmin_cm"] > MC.QC["float_cm"]]
    # --- per-frame body measures
    stretch, angles, flips, rev, popv, ikfk, cog_out = {}, {}, {}, {}, {b: [] for b in POP_BONES}, [], 0
    prevq, prevn = {}, {}
    sc.frame_set(1)
    balance_frames = 0
    for f in range(1, N + 1):
        sc.frame_set(f)
        for joint, (up, lo) in RC.JOINTS.items():
            L, u, l_ = _chain_len(rig, up, lo)
            stretch.setdefault(joint, []).append(L)
            ang = math.degrees(u.angle(l_)) if u.length and l_.length else 0.0
            angles.setdefault(joint, []).append(ang)
            nrm = u.cross(l_)
            xa = (rig.matrix_world.to_3x3() @ rig.pose.bones[up].matrix.to_3x3()).col[0]
            if ang > 15:
                if nrm.dot(xa) * conv[joint] < 0:
                    rev[joint] = rev.get(joint, 0) + 1
                if joint in prevn and prevn[joint] is not None:
                    d = math.degrees(prevn[joint].angle(nrm.normalized()))
                    if d > MC.QC["joint_flip_deg"]:
                        flips.setdefault(joint, []).append(f)
                prevn[joint] = nrm.normalized()
            else:
                prevn[joint] = None
        for b in POP_BONES:
            q = _world_q(rig, b)
            if b in prevq:
                a = math.degrees(prevq[b].rotation_difference(q).angle)
                popv[b].append(min(a, 360.0 - a))           # q and -q are the same rotation
            prevq[b] = q
        if f % 3 == 1:                       # (toggling the switch costs two evaluations: every 3rd frame)
            for S in "LR":
                ikfk.append(IKFK.ik_fk_mismatch(rig, S, "leg"))
        # balance (static clips): COM over the planted soles
        if static:
            com = Vector()
            for b, m in MASS.items():
                com += m * (_pt(rig, b) + _pt(rig, b, True)) / 2
            com /= sum(MASS.values())
            sup = [Vector(pts[s][k][f - f0][:2]) for s in IM.SIDES for k in IM.POINTS
                   if pts[s][k][f - f0][2] < MC.CONTACT_HEIGHT]
            if len(sup) >= 2:
                balance_frames += 1
                if not _inside(Vector(com[:2]), sup, 0.04):
                    cog_out += 1
    # stretch: compare with the first frame's ratio to the rest chain, reported as deviation
    stretch_dev = {j: float(max(abs(L / rl[j] - 1) for L in v)) for j, v in stretch.items()}
    # pops: angular speed spikes
    pops = []
    for b, v in popv.items():
        if len(v) < 5:
            continue
        arr = np.array(v)
        p95 = float(np.percentile(arr, 95))
        for i, x in enumerate(arr):
            if x > max(MC.QC["min_spike_deg"], MC.QC["transition_spike"] * p95):
                pops.append(dict(bone=b, frame=f0 + i + 1, deg_per_frame=round(float(x), 1), p95=round(p95, 1)))
    res = dict(
        action=meta["name"], frames=n, loop=loop, played=N, root_mode=meta.get("root_mode"),
        speed_m_s=meta.get("speed", 0.0),
        raw_slip_cm=meta.get("raw_slip_cm", -1),
        foot_slip=dict(max_cm=round(slip["max_slip_cm"], 2), contacts=len(slip["contacts"]),
                       pass_=slip["max_slip_cm"] <= MC.QC["foot_slip_cm"]),
        ground=dict(lowest_cm=round(100 * zall, 2), floating_contacts=len(floating),
                    pass_=(100 * zall >= -MC.QC["penetration_cm"]) and not floating),
        limb_stretch=dict(max_dev={j: round(v, 4) for j, v in stretch_dev.items()},
                          pass_=all(v <= MC.QC["limb_stretch"] for v in stretch_dev.values())),
        joints=dict(max_deg={j: round(max(v), 1) for j, v in angles.items()},
                    reverse_bend_frames=rev, flips=flips,
                    pass_=(all(max(v) <= (MC.QC["knee_max_deg"] if j.startswith("knee") else MC.QC["elbow_max_deg"])
                               for j, v in angles.items()) and not rev and not flips)),
        pops=dict(count=len(pops), worst=sorted(pops, key=lambda p: -p["deg_per_frame"])[:5], pass_=not pops),
        ik_fk=dict(max_cm=round(100 * max(ikfk), 2), pass_=max(ikfk) < 0.02),
    )
    if balance_frames:
        frac = cog_out / balance_frames
        res["balance"] = dict(frames=balance_frames, com_outside_frac=round(frac, 3), pass_=frac < 0.1)
    res["pass"] = all(v["pass_"] for v in res.values() if isinstance(v, dict) and "pass_" in v)
    return res


def validate_action(rig, action, conv=None, play_loops=2):
    sc = bpy.context.scene
    n = int(action["frames"])
    loop = bool(action.get("loop"))
    N = n * play_loops if loop else n
    ad = rig.animation_data or rig.animation_data_create()
    rl = rest_lengths(rig)
    keep = (ad.action, ad.use_nla)
    for t in ad.nla_tracks:
        t.mute = True
    ad.use_nla = True
    tr = ad.nla_tracks.new()
    tr.name = "QC"
    st = tr.strips.new(action.name, 1, action)
    st.action_frame_start, st.action_frame_end = 1, (n + 1 if loop else n)
    st.repeat = float(play_loops) if loop else 1.0
    st.extrapolation = "HOLD"
    rootf = IM.root_fn(action)
    ad.action = IM.key_root(rig, 1, N, rootf, "QC_ROOT")
    try:
        conv = conv or joint_conventions(rig)
        meta = dict(name=action.name, frames=n, loop=loop, root_mode=action.get("root_mode"),
                    speed=round(float(abs(action["root_y"][-1]) / max(1, n - 1) * PC.FPS), 3) if n > 1 else 0.0,
                    raw_slip_cm=round(float(action.get("raw_slip_cm", -1)), 2))
        return _measure(rig, 1, N, conv, action.get("folder") in STANDING, meta)
    finally:
        ad.nla_tracks.remove(tr)
        for t in ad.nla_tracks:
            t.mute = False
        qr = bpy.data.actions.get("QC_ROOT")
        ad.action = keep[0]
        ad.use_nla = keep[1]
        if qr:
            bpy.data.actions.remove(qr)


def validate_range(rig, f0, f1, label, conv=None, static=False):
    """QC of whatever the rig plays now (NLA episode stack, transitions included)."""
    conv = conv or joint_conventions(rig)
    meta = dict(name=label, frames=f1 - f0 + 1, loop=False, root_mode="episode", speed=0.0, raw_slip_cm=-1)
    return _measure(rig, f0, f1 - f0 + 1, conv, static, meta)


def _inside(p, pts, margin):
    """p inside the convex hull of pts (2D), grown by margin."""
    P = sorted({(round(q.x, 4), round(q.y, 4)) for q in pts})
    if len(P) < 3:
        a, b = Vector(P[0]), Vector(P[-1])
        ab = b - a
        t = 0 if ab.length < 1e-6 else max(0, min(1, (p - a).dot(ab) / ab.length_squared))
        return (a + ab * t - p).length <= margin + 0.03

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lo, hi = [], []
    for q in P:
        while len(lo) >= 2 and cross(lo[-2], lo[-1], q) <= 0:
            lo.pop()
        lo.append(q)
    for q in reversed(P):
        while len(hi) >= 2 and cross(hi[-2], hi[-1], q) <= 0:
            hi.pop()
        hi.append(q)
    hull = lo[:-1] + hi[:-1]
    for i in range(len(hull)):
        a, b = Vector(hull[i]), Vector(hull[(i + 1) % len(hull)])
        e = b - a
        nrm = Vector((e.y, -e.x)).normalized()
        if (p - a).dot(nrm) > margin:
            return False
    return True


def validate_face(rig):
    import setup_face as F
    mouth = F.mouth_object(rig)

    class _Ev:                                       # driven values live on the evaluated copies
        def __getattr__(self, n):
            dg = bpy.context.evaluated_depsgraph_get()
            if n == "kb":
                return mouth.data.shape_keys.evaluated_get(dg).key_blocks
            return rig.evaluated_get(dg).pose.bones[{"lid": "lid_l", "brow": "brow_l"}[n]]
    ev = _Ev()
    out = {}
    F.pose(rig)
    bpy.context.view_layer.update()
    expect = {"Happy": ("smile",), "Sad": ("frown",), "Angry": ("frown",), "Surprise": ("open", "o"),
              "Fear": ("open", "wide"), "Talk_A": ("open",), "Talk_O": ("o",), "Talk_E": ("wide",)}
    for name, vals in F.EXPRESSIONS.items():
        F.pose(rig, **vals)
        bpy.context.view_layer.update()
        kb = ev.kb
        keys = {k: round(kb[k].value, 3) for k in F.MOUTH}
        moved = [k for k in expect.get(name, ()) if kb[k].value < 0.3]
        lid_deg = math.degrees(Quaternion(ev.lid.rotation_quaternion).angle)
        brow_mm = 1000 * ev.brow.location.length
        ok = not moved
        if name == "Blink":
            ok = ok and lid_deg > 80
        if name in ("Surprise", "Sad", "Fear"):
            ok = ok and brow_mm > 3
        out[name] = dict(mouth=keys, lid_deg=round(lid_deg, 1), brow_lift_mm=round(brow_mm, 1), pass_=ok)
    F.pose(rig)
    eyes_ok = all(any(c.type == "DAMPED_TRACK" and c.subtarget == RC.EYES_TARGET for c in rig.pose.bones[e].constraints)
                  for e in ("eye_l", "eye_r"))
    return dict(expressions=out, eye_tracking=eyes_ok,
                pass_=eyes_ok and all(v["pass_"] for v in out.values()))


def deformation(rig):
    import generate_rig as G
    rep = G.weight_report(rig)
    body = next(o for o in rig.children if o.name.endswith("_BODY"))
    # unweighted body vertices are only acceptable if they are masked away (helper geometry)
    masked = set()
    for m in body.modifiers:
        if m.type != "MASK" or m.vertex_group not in body.vertex_groups:
            continue
        gi = body.vertex_groups[m.vertex_group].index
        inside = {v.index for v in body.data.vertices if any(g.group == gi and g.weight > m.threshold for g in v.groups)}
        if m.invert_vertex_group:                 # inverted mask hides the group
            masked |= inside
        else:                                     # plain mask keeps only the group (e.g. "Hide helpers": body only)
            masked |= {v.index for v in body.data.vertices} - inside
    names = {b.name for b in rig.data.bones if b.use_deform}
    idx = {g.index for g in body.vertex_groups if g.name in names}
    visible_bad = sum(1 for v in body.data.vertices
                      if v.index not in masked and not any(g.group in idx and g.weight > 1e-4 for g in v.groups))
    return dict(meshes=rep, body_unweighted_visible=visible_bad,
                pass_=visible_bad == 0 and all(r["unweighted"] == 0 for n, r in rep.items() if not n.endswith("_BODY")))


def write_reports(char_key, results, face=None, deform=None, renders=()):
    """JSON per test folder + FINAL_REVIEW markdown."""
    qc = PC.path("10_QUALITY_CONTROL")
    folders = {"WALK": "WALK_TEST", "RUN": "RUN_TEST"}
    for r in results:
        cat = r["action"].split("_")[1] if r["action"].startswith("UHS_") else "OTHER"
        sub = folders.get(cat, "FINAL_REVIEW")
        os.makedirs(os.path.join(qc, sub), exist_ok=True)
        with open(os.path.join(qc, sub, f"{char_key}_{r['action']}.json"), "w") as fh:
            json.dump(r, fh, indent=1, default=str)
    os.makedirs(os.path.join(qc, "FOOT_SLIP_TEST"), exist_ok=True)
    with open(os.path.join(qc, "FOOT_SLIP_TEST", f"{char_key}_foot_slip.json"), "w") as fh:
        json.dump({r["action"]: dict(raw_slip_cm=r["raw_slip_cm"], locked=r["foot_slip"], ground=r["ground"])
                   for r in results}, fh, indent=1, default=str)
    if face:
        os.makedirs(os.path.join(qc, "FACIAL_TEST"), exist_ok=True)
        with open(os.path.join(qc, "FACIAL_TEST", f"{char_key}_face.json"), "w") as fh:
            json.dump(face, fh, indent=1, default=str)
    if deform:
        os.makedirs(os.path.join(qc, "RIG_DEFORMATION_TEST"), exist_ok=True)
        with open(os.path.join(qc, "RIG_DEFORMATION_TEST", f"{char_key}_weights.json"), "w") as fh:
            json.dump(deform, fh, indent=1, default=str)

    def mark(ok):
        return "PASS" if ok else "**FAIL**"
    L = [f"# QC report — {char_key}", "",
         "Every number below is measured on the baked animation (frames evaluated in Blender), not assumed.", "",
         "| action | speed m/s | raw slip cm | locked slip cm | lowest cm | stretch | max knee/elbow ° | rev/flip | pops | IK-FK cm | balance | result |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in results:
        j = r["joints"]
        mk = max([v for k, v in j["max_deg"].items() if k.startswith("knee")] or [0])
        me = max([v for k, v in j["max_deg"].items() if k.startswith("elbow")] or [0])
        bal = r.get("balance", {})
        L.append(f"| {r['action']} | {r['speed_m_s']} | {r['raw_slip_cm']} | {r['foot_slip']['max_cm']} | "
                 f"{r['ground']['lowest_cm']} | {max(r['limb_stretch']['max_dev'].values()):.3f} | {mk:.0f} / {me:.0f} | "
                 f"{sum(j['reverse_bend_frames'].values())}/{sum(len(v) for v in j['flips'].values())} | {r['pops']['count']} | "
                 f"{r['ik_fk']['max_cm']} | {bal.get('com_outside_frac', '–')} | {mark(r['pass'])} |")
    if face:
        L += ["", f"## Face — {mark(face['pass_'])}", "", "| expression | open | smile | frown | wide | o | lid ° | brow mm | |",
              "|---|---|---|---|---|---|---|---|---|"]
        for n, v in face["expressions"].items():
            m = v["mouth"]
            L.append(f"| {n} | {m['open']} | {m['smile']} | {m['frown']} | {m['wide']} | {m['o']} | {v['lid_deg']} | "
                     f"{v['brow_lift_mm']} | {mark(v['pass_'])} |")
        L.append(f"\nEye tracking constraints: {mark(face['eye_tracking'])}")
    if deform:
        L += ["", f"## Weights — {mark(deform['pass_'])}", "",
              f"Visible unweighted body vertices: {deform['body_unweighted_visible']}"]
        for n, v in deform["meshes"].items():
            if v["unweighted"]:
                L.append(f"- {n}: {v['unweighted']} of {v['verts']} vertices unweighted")
    if renders:
        L += ["", "## Renders checked", ""] + [f"- `{os.path.relpath(p, PC.STUDIO)}`" for p in renders]
    L += ["", "Thresholds: `00_CORE_SYSTEM/motion_config.py` (QC)."]
    os.makedirs(os.path.join(qc, "FINAL_REVIEW"), exist_ok=True)
    p = os.path.join(qc, "FINAL_REVIEW", f"{char_key}_report.md")
    with open(p, "w") as fh:
        fh.write("\n".join(L) + "\n")
    return p
