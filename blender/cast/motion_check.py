"""Frame-by-frame motion QA for a cast character (run BEFORE the final render).

    ../cast/bpy.sh ../cast/motion_check.py film.blend [rig_name] [first last]   -> prints a report, writes
                                                                                  <film>_motion.txt next to the .blend
or from a scene script:   import motion_check; motion_check.check(rig, 1, 240)

Checks, on every frame (24 fps):
  POP      a bone's world position accelerates far more than its own usual motion (snap / blend error)
  SPIN     a bone turns more than 20 degrees in one frame (quaternion flip, broken cross-fade)
  JITTER   high-frequency back-and-forth (direction flips every frame) on hands, head, feet
  JUMP     a bone moves >3x further in one frame than in its neighbours (and >2 cm): a teleport inside a shot
  SLIDE    a planted foot (low and meant to be still) moves sideways faster than 6 cm/s
  FLOOR    a foot goes into the floor (more than 1 cm below its own standing height)
Zero findings is the delivery standard (see blender/STANDARD.md, «کنترل حرکت»).
"""
import bpy, sys, os, math
from mathutils import Vector

BONES = ["pelvis", "spine_03", "neck_01", "head", "upperarm_l", "upperarm_r", "lowerarm_l", "lowerarm_r",
         "hand_l", "hand_r", "thigh_l", "thigh_r", "calf_l", "calf_r", "foot_l", "foot_r", "ball_l", "ball_r"]
JITTER_BONES = ["head", "hand_l", "hand_r", "foot_l", "foot_r"]


def _sample(rig, a, b):
    sc = bpy.context.scene
    pos = {n: [] for n in BONES if n in rig.pose.bones}
    rot = {n: [] for n in pos}
    for f in range(a, b + 1):
        sc.frame_set(f)
        for n in pos:
            m = rig.matrix_world @ rig.pose.bones[n].matrix
            pos[n].append(m.translation.copy())
            rot[n].append(m.to_quaternion())
    return pos, rot


def _median(v):
    s = sorted(v)
    return s[len(s) // 2] if s else 0.0


def check(rig, a, b, fps=24, floor=0.0):
    pos, rot = _sample(rig, a, b)
    n = b - a + 1
    out = []
    # POP: a kink (velocity changes in one frame while the neighbours are smooth) or a one-frame spike
    # (acceleration flips direction frame to frame). Smooth fast moves — steps, gestures — are not pops.
    for name, P in pos.items():
        A = [(P[i + 1] - 2 * P[i] + P[i - 1]) * fps * fps for i in range(1, n - 1)]
        for j in range(1, len(A) - 1):
            g = A[j].length
            if g < 3.0:
                continue
            kink = g > 2.5 * max(A[j - 1].length, A[j + 1].length)
            spike = A[j].dot(A[j + 1]) < -0.5 * g * A[j + 1].length and A[j + 1].length > 3.0 \
                and A[j].dot(A[j - 1]) < -0.5 * g * A[j - 1].length
            if kink or spike:
                out.append((a + j + 1, "POP", name, f"{g:.1f} m/s² ({'kink' if kink else 'spike'})"))
    # JUMP: a bone moves much further in one frame than in the frames around it (a teleport inside a shot)
    for name, P in pos.items():
        d = [(P[i] - P[i - 1]).length for i in range(1, n)]
        for j in range(1, len(d) - 1):
            if d[j] > 0.02 and d[j] > 3 * max(d[j - 1], d[j + 1]):
                out.append((a + j + 1, "JUMP", name, f"{d[j] * 100:.1f} cm in one frame"))
    # SPIN: angular step per frame
    for name, R in rot.items():
        for i in range(1, n):
            d = math.degrees(R[i - 1].rotation_difference(R[i]).angle)
            d = min(d, 360 - d)
            if d > 20:
                out.append((a + i, "SPIN", name, f"{d:.0f}° in one frame"))
    # JITTER: velocity direction flips on consecutive frames with real amplitude
    for name in JITTER_BONES:
        if name not in pos:
            continue
        P = pos[name]
        v = [P[i + 1] - P[i] for i in range(n - 1)]
        run = 0
        for i in range(1, len(v)):
            flip = v[i].dot(v[i - 1]) < 0 and v[i].length * fps > 0.08 and v[i - 1].length * fps > 0.08
            run = run + 1 if flip else 0
            if run == 3:
                out.append((a + i, "JITTER", name, "direction flips 3 frames in a row"))
    # SLIDE / FLOOR for feet
    for side in ("l", "r"):
        ball, foot = f"ball_{side}", f"foot_{side}"
        if ball not in pos:
            continue
        Z = [p.z for p in pos[ball]]
        stand = sorted(Z)[max(0, len(Z) // 20)]          # its standing height (5th percentile)
        for i in range(1, n):
            p0, p1 = pos[ball][i - 1], pos[ball][i]
            q0, q1 = pos[foot][i - 1], pos[foot][i]
            planted = p1.z < stand + 0.008 and p0.z < stand + 0.008
            # sliding = neither floor contact (toes or heel) stays put; rolling over one of them is fine
            hv = min(Vector((p1.x - p0.x, p1.y - p0.y)).length, Vector((q1.x - q0.x, q1.y - q0.y)).length) * fps
            if planted and hv > 0.06 and q1.z < sorted(z.z for z in pos[foot])[len(Z) // 20] + 0.008:
                out.append((a + i, "SLIDE", f"foot {side}", f"{hv * 100:.0f} cm/s while planted"))
            if p1.z < stand - 0.01:
                out.append((a + i, "FLOOR", f"foot {side}", f"{(stand - p1.z) * 100:.1f} cm below standing height"))
    out.sort()
    return out


def report(findings, path=None):
    lines = []
    kinds = {}
    for f, k, b, msg in findings:
        kinds[k] = kinds.get(k, 0) + 1
        lines.append(f"f{f:04d}  {k:6s} {b:12s} {msg}")
    head = "motion check: " + (", ".join(f"{k} {v}" for k, v in sorted(kinds.items())) if kinds else "CLEAN")
    text = head + "\n" + "\n".join(lines)
    print(text)
    if path:
        open(path, "w").write(text + "\n")
    return text


if __name__ == "__main__":
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    blend = args[0]
    bpy.ops.wm.open_mainfile(filepath=os.path.abspath(blend))
    sc = bpy.context.scene
    rigs = [o for o in sc.objects if o.type == "ARMATURE" and "pelvis" in o.pose.bones]
    if len(args) > 1 and not args[1].isdigit():
        rigs = [sc.objects[args[1]]]
        args = args[:1] + args[2:]
    a, b = (int(args[1]), int(args[2])) if len(args) > 2 else (sc.frame_start, sc.frame_end)
    for rig in rigs:
        print(f"== {rig.name} {a}-{b}")
        report(check(rig, a, b), os.path.splitext(blend)[0] + f"_{rig.name}_motion.txt")
