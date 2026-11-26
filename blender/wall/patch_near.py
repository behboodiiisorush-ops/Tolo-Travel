"""«دیوار» POV: Kazemi climbs through the hole right in front of me (frames ~630-642) and the camera went
through his head. Pull the camera back (horizontally, away from him) so it stays >= KEEP from his head/chest."""
import bpy, os
from mathutils import Vector
HERE = os.path.dirname(os.path.abspath(__file__))
bpy.ops.wm.open_mainfile(filepath=os.path.join(HERE, "wall.blend"))
sc = bpy.context.scene; cam = sc.camera
kz = bpy.data.objects["Kazemi_rig"]
KEEP, A, B = 0.5, 615, 660
push = {}
for f in range(A, B + 1):
    sc.frame_set(f)
    c = cam.location.copy()
    pts = [kz.matrix_world @ kz.pose.bones[b].head for b in ("head", "spine_03")]
    p = min(pts, key=lambda v: (v - c).length)
    away = Vector((c.x - p.x, c.y - p.y, 0))
    d = (c - p).length
    push[f] = (max(0.0, KEEP - d), away.normalized() if away.length > 1e-4 else Vector((-1, 0, 0)))
# smooth the push amount so the move is gentle
fs = sorted(push)
amt = {f: max(push[g][0] * max(0, 1 - abs(g - f) / 8) for g in fs) for f in fs}
n = 0
for f in fs:
    if amt[f] < 1e-3:
        continue
    sc.frame_set(f)
    cam.location = cam.location + push[f][1] * amt[f] * 1.1
    cam.keyframe_insert("location", frame=f)
    n += 1; print("PUSH", f, round(amt[f], 2))
print("N", n)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(HERE, "wall_fix2.blend"))
