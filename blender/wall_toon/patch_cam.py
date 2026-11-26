"""The two camera fixes of the first «دیوار» (wall/patch_look.py + wall/patch_near.py) for the wagon-style blend:
gentler look-down after the opening (pitch >= -0.42 from frame 300), and Kazemi hidden for the frames the camera
passes through him at the first hole (found by distance)."""
import bpy, os, math
from mathutils import Vector
HERE = os.path.dirname(os.path.abspath(__file__))
F = os.path.join(HERE, "wall_toon.blend")
bpy.ops.wm.open_mainfile(filepath=F)
sc = bpy.context.scene
cam = sc.camera
LIM, F0 = -0.42, 300
n = 0
for f in range(F0, sc.frame_end + 1):
    sc.frame_set(f)
    q = cam.rotation_quaternion.copy()
    d = q @ Vector((0, 0, -1))
    if d.z >= LIM:
        continue
    h = Vector((d.x, d.y, 0)).normalized() * math.sqrt(1 - LIM * LIM)
    cam.rotation_quaternion = Vector((h.x, h.y, LIM)).to_track_quat("-Z", "Y")
    cam.keyframe_insert("rotation_quaternion", frame=f)
    n += 1
print("LOOK clamped", n)
kz = bpy.data.objects["Kazemi_rig"]
near = []
for f in range(560, 1300):
    sc.frame_set(f)
    c = cam.matrix_world.translation
    d = min((c - kz.matrix_world @ kz.pose.bones[b].head).length for b in ("head", "spine_03"))
    if d < 0.32:
        near.append(f)
print("NEAR", near)
objs = [o for o in bpy.data.objects if o.parent == kz]
if near:
    spans, a = [], near[0]
    for p, q in zip(near, near[1:] + [None]):
        if q != p + 1:
            spans.append((a, p)); a = q
    for o in objs:
        for a, b in spans:
            for f, hdn in ((a - 1, False), (a, True), (b, True), (b + 1, False)):
                o.hide_render = hdn
                o.keyframe_insert("hide_render", frame=f)
    print("HIDE", spans, len(objs))
bpy.ops.wm.save_as_mainfile(filepath=F)
