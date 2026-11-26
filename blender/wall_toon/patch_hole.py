"""The dark block behind the far-wall hole swallowed Kian's body (only his big puppet head stuck out).
Make it a hollow dark pocket instead: back plate + side and top plates around him."""
import bpy, os
HERE = os.path.dirname(os.path.abspath(__file__))
F = os.path.join(HERE, "wall_toon.blend")
bpy.ops.wm.open_mainfile(filepath=F)
b = bpy.data.objects["Behind hole"]
bpy.context.view_layer.update()
xs = [(b.matrix_world @ v.co).x for v in b.data.vertices]
print("BEFORE", min(xs), max(xs))
def plate(dx, sx, dy, sy, dz, sz, name):
    o = b.copy(); o.data = b.data.copy(); o.name = name
    for c in b.users_collection:
        c.objects.link(o)
    for v in o.data.vertices:
        v.co.x = v.co.x * sx + dx; v.co.y = v.co.y * sy + dy; v.co.z = v.co.z * sz + dz
    return o
# original box: 0.6 x 1.4 x 1.4 centred at (15.9, 1.5, 1.35) in object coords
plate(0.38, 0.12, 0, 1.0, 0, 1.0, "Behind hole back")
plate(0.05, 1.2, -0.68, 0.04, 0, 1.0, "Behind hole side a")
plate(0.05, 1.2, 0.68, 0.04, 0, 1.0, "Behind hole side b")
plate(0.05, 1.2, 0, 1.0, 0.68, 0.04, "Behind hole top")
bpy.data.objects.remove(b)
bpy.ops.wm.save_as_mainfile(filepath=F)
print("PATCHED")
