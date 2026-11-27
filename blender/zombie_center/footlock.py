"""IK foot lock for mocap on the game_engine rig: while a foot is on the ground, cancel the measured drift of
its sole (IK on thigh+calf, knee kept on its animated direction with a pole), then bake and remove the IK.

    import footlock
    footlock.lock(ch, f0, f1)          # after mocap.apply(...) and motion_qc.ground(...)
"""
import bpy
from mathutils import Vector, Matrix
import motion_qc as Q

TOUCH = 0.012


def _drift(ch, f0, f1):
    """Per side and frame: accumulated horizontal drift of the touching sole points since the foot planted."""
    sc = bpy.context.scene
    objs = Q._foot_objects(ch)
    prev = None
    acc = {"l": Vector((0, 0, 0)), "r": Vector((0, 0, 0))}
    out = {"l": {}, "r": {}}
    planted = {"l": {}, "r": {}}
    lift = {"l": {}, "r": {}}
    prevc = {}
    for f in range(f0, f1 + 1):
        sc.frame_set(f)
        cur = Q._sole(ch, objs, bpy.context.evaluated_depsgraph_get())
        for s in ("l", "r"):
            pts = list(cur[s].values())
            minz = min(p.z for p in pts) if pts else 1.0
            c = sum(pts, Vector()) / len(pts) if pts else Vector()
            speed = (Vector((c.x - prevc[s].x, c.y - prevc[s].y, 0)).length if s in prevc else 0.0)
            prevc[s] = c
            touch = [k for k, p in cur[s].items() if p.z < TOUCH]
            # a foot still swinging fast (>3 cm/frame) that grazes the floor is a scrape, not a plant: lift it
            lift[s][f] = max(0.0, 0.02 - minz) if (speed > 0.03 and minz < 0.02) else 0.0
            if lift[s][f] > 0:
                touch = []
            planted[s][f] = bool(touch)
            if prev is not None and touch:
                both = [k for k in touch if k in prev[s] and prev[s][k].z < TOUCH]
                if len(both) >= 3:
                    d = sum(((cur[s][k] - prev[s][k]) for k in both), Vector()) / len(both)
                    acc[s] += Vector((d.x, d.y, 0))
            if not touch:
                acc[s] = acc[s] * 0.45          # foot in the air: release the correction over ~3 frames (invisible)
            out[s][f] = acc[s].copy()
        prev = cur
    # smooth the lifts (max over ±1 frame, then average over ±2) so the foot rises and lands without pops
    for s in ("l", "r"):
        fr = list(range(f0, f1 + 1))
        mx = {f: max(lift[s].get(g, 0.0) for g in (f - 1, f, f + 1)) for f in fr}
        lift[s] = {f: sum(mx.get(g, 0.0) for g in range(f - 2, f + 3)) / 5.0 * 1.6 for f in fr}
    return out, lift


def _plants(ch, f0, f1):
    """Classic plant detection on the animation itself (for runs): a foot is planted while its ball is low
    (within 4 cm of its lowest height) and nearly still in the world (< 5 cm/frame). Returns, per side and frame,
    the XY correction that pins the ankle to the mean ankle XY of that plant."""
    sc = bpy.context.scene
    rig = ch.rig
    ball, ank = {"l": {}, "r": {}}, {"l": {}, "r": {}}
    for f in range(f0, f1 + 1):
        sc.frame_set(f)
        for s in ("l", "r"):
            ball[s][f] = (rig.matrix_world @ rig.pose.bones[f"ball_{s}"].head).copy()
            ank[s][f] = (rig.matrix_world @ rig.pose.bones[f"foot_{s}"].head).copy()
    out = {"l": {}, "r": {}}
    for s in ("l", "r"):
        zmin = min(p.z for p in ball[s].values())
        fr = list(range(f0, f1 + 1))
        pl = {}
        for i, f in enumerate(fr):
            sp = (ball[s][f] - ball[s][fr[i - 1]]).xy.length if i else 0.0
            pl[f] = ball[s][f].z < zmin + 0.04 and sp < 0.05
        corr = {f: Vector((0, 0, 0)) for f in fr}
        i = 0
        while i < len(fr):
            if pl[fr[i]]:
                j = i
                while j + 1 < len(fr) and pl[fr[j + 1]]:
                    j += 1
                seg = fr[i:j + 1]
                anchor = sum((ank[s][f] for f in seg), Vector()) / len(seg)
                for f in seg:
                    d = anchor - ank[s][f]
                    corr[f] = Vector((d.x, d.y, 0))
                # ease in/out over 2 frames outside the plant (foot in the air)
                for k, w in ((1, 0.5), (2, 0.2)):
                    if i - k >= 0 and not pl[fr[i - k]]:
                        corr[fr[i - k]] = corr[seg[0]] * w
                    if j + k < len(fr) and not pl[fr[j + k]]:
                        corr[fr[j + k]] = corr[seg[-1]] * w
                i = j + 1
            else:
                i += 1
        out[s] = corr
        out.setdefault("_planted", {})[s] = pl
    return out


def lock(ch, f0, f1, mode="drift"):
    sc = bpy.context.scene
    rig = ch.rig
    if mode == "plant":
        P = _plants(ch, f0, f1)
        drift = {s: {f: -v for f, v in P[s].items()} for s in ("l", "r")}
        _, lift = _drift(ch, f0, f1)          # swing clearance: a fast-moving foot never skims the floor
        for s in ("l", "r"):                  # ...but a planted foot is never lifted (no floating)
            for f in lift[s]:
                if P["_planted"][s].get(f):
                    lift[s][f] = 0.0
    else:
        drift, lift = _drift(ch, f0, f1)
    tg, pole = {}, {}
    for s in ("l", "r"):
        t = bpy.data.objects.new(f"ZC_IK_{rig.name}_{s}", None); sc.collection.objects.link(t)
        p = bpy.data.objects.new(f"ZC_POLE_{rig.name}_{s}", None); sc.collection.objects.link(p)
        tg[s], pole[s] = t, p
    # key targets = animated foot matrix minus the drift; pole = knee pushed forward along the leg plane
    for f in range(f0, f1 + 1):
        sc.frame_set(f)
        for s in ("l", "r"):
            fm = rig.matrix_world @ rig.pose.bones[f"foot_{s}"].matrix
            m = Matrix.Translation(-drift[s][f] + Vector((0, 0, lift[s][f]))) @ fm
            tg[s].matrix_world = m
            tg[s].keyframe_insert("location", frame=f)
            tg[s].keyframe_insert("rotation_euler", frame=f)
            hip = rig.matrix_world @ rig.pose.bones[f"thigh_{s}"].head
            knee = rig.matrix_world @ rig.pose.bones[f"calf_{s}"].head
            ank = fm.translation
            mid = (hip + ank) / 2
            pole[s].location = knee + (knee - mid).normalized() * 0.5 if (knee - mid).length > 1e-4 else knee + Vector((0, -0.5, 0))
            pole[s].keyframe_insert("location", frame=f)
    for s in ("l", "r"):
        pb = rig.pose.bones[f"calf_{s}"]
        c = pb.constraints.new("IK"); c.name = "ZC_FootLock"
        c.target = tg[s]; c.pole_target = pole[s]; c.chain_count = 2; c.use_tail = True
        c.pole_angle = 0.0
        # IK solves the calf tail to the target's origin: put origin at the ankle (foot head == calf tail)
        fpb = rig.pose.bones[f"foot_{s}"]
        cr = fpb.constraints.new("COPY_ROTATION"); cr.name = "ZC_FootRot"; cr.target = tg[s]
    # find the pole angle that reproduces the animated knee (measured at f0 on the left leg)
    _fit_pole_angle(ch, f0)
    _bake(rig, f0, f1)
    for s in ("l", "r"):
        bpy.data.objects.remove(tg[s], do_unlink=True)
        bpy.data.objects.remove(pole[s], do_unlink=True)


def _fit_pole_angle(ch, f):
    import math
    sc = bpy.context.scene
    rig = ch.rig
    best = None
    for s in ("l", "r"):
        c = rig.pose.bones[f"calf_{s}"].constraints["ZC_FootLock"]
        # reference: knee position without IK
        c.influence = 0.0; sc.frame_set(f); bpy.context.view_layer.update()
        ref = (rig.matrix_world @ rig.pose.bones[f"calf_{s}"].head).copy()
        c.influence = 1.0
        best = None
        for a in range(-180, 180, 5):
            c.pole_angle = math.radians(a); sc.frame_set(f); bpy.context.view_layer.update()
            d = ((rig.matrix_world @ rig.pose.bones[f"calf_{s}"].head) - ref).length
            if best is None or d < best[0]:
                best = (d, a)
        for a in [best[1] + x * 0.5 for x in range(-10, 11)]:
            c.pole_angle = math.radians(a); sc.frame_set(f); bpy.context.view_layer.update()
            d = ((rig.matrix_world @ rig.pose.bones[f"calf_{s}"].head) - ref).length
            if d < best[0]:
                best = (d, a)
        c.pole_angle = math.radians(best[1])
        print(f"POLE {s} angle {best[1]:.1f} knee err {best[0]*100:.2f} cm")


def _bake(rig, f0, f1):
    bpy.context.view_layer.objects.active = rig
    for o in bpy.context.view_layer.objects:
        o.select_set(o == rig)
    bpy.ops.object.mode_set(mode="POSE")
    for pb in rig.pose.bones:
        want = pb.name.split("_")[0] in ("thigh", "calf", "foot", "ball")
        if hasattr(pb, "select"):
            pb.select = want
        else:
            pb.bone.select = want
    bpy.ops.nla.bake(frame_start=f0, frame_end=f1, only_selected=True, visual_keying=True,
                     clear_constraints=True, use_current_action=True, bake_types={"POSE"})
    bpy.ops.object.mode_set(mode="OBJECT")
