"""Soften the POV look-down after the opening (crossing the holes looked into my own collar):
wall.blend -> wall_fix.blend, camera pitch clamped to >= LIM from frame F0 on. Prints the frames it changed."""
import bpy, os, math
from mathutils import Vector
HERE = os.path.dirname(os.path.abspath(__file__))
bpy.ops.wm.open_mainfile(filepath=os.path.join(HERE, "wall.blend"))
sc = bpy.context.scene
cam = sc.camera
LIM, F0 = -0.42, 300
changed = []
for f in range(F0, sc.frame_end + 1):
    sc.frame_set(f)
    q = cam.rotation_quaternion.copy()
    d = q @ Vector((0, 0, -1))
    if d.z >= LIM:
        continue
    up = q @ Vector((0, 1, 0))
    h = Vector((d.x, d.y, 0)).normalized() * math.sqrt(1 - LIM * LIM)
    q2 = Vector((h.x, h.y, LIM)).to_track_quat("-Z", "Y")
    cam.rotation_quaternion = q2
    cam.keyframe_insert("rotation_quaternion", frame=f)
    changed.append(f)
print("CHANGED", changed[:1], changed[-1:] if changed else None, len(changed))
print("LIST", ",".join(map(str, changed)))
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(HERE, "wall_fix.blend"))
