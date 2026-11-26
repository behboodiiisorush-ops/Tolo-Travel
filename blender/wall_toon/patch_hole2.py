"""Fix for patch_hole.py: the box mesh has its vertices in world coordinates (origin at 0), so the plates were
scaled about the world origin and landed next to me in flat A. Rebuild them around the box centre."""
import bpy, os
HERE = os.path.dirname(os.path.abspath(__file__))
F = os.path.join(HERE, "wall_toon.blend")
bpy.ops.wm.open_mainfile(filepath=F)
C = (15.9, 1.5, 1.35)          # the original dark box: 0.6 x 1.4 x 1.4 around C
SPEC = {"Behind hole back": (0.38, 0.12, 0, 1.0, 0, 1.0), "Behind hole side a": (0.05, 1.2, -0.68, 0.04, 0, 1.0),
        "Behind hole side b": (0.05, 1.2, 0.68, 0.04, 0, 1.0), "Behind hole top": (0.05, 1.2, 0, 1.0, 0.68, 0.04)}
for name, (dx, sx, dy, sy, dz, sz) in SPEC.items():
    o = bpy.data.objects[name]
    mw = o.matrix_world
    xs = [(mw @ v.co).x for v in o.data.vertices]
    print("BEFORE", name, round(min(xs), 2), round(max(xs), 2))
    # undo the wrong transform (applied about the local origin), then apply it about the box centre
    for v in o.data.vertices:
        x, y, z = (v.co.x - dx) / sx, (v.co.y - dy) / sy, (v.co.z - dz) / sz       # original box vertex (local)
        w = mw @ __import__("mathutils").Vector((x, y, z))
        lx, ly, lz = (w.x - C[0]) * sx + dx + C[0], (w.y - C[1]) * sy + dy + C[1], (w.z - C[2]) * sz + dz + C[2]
        v.co = mw.inverted() @ __import__("mathutils").Vector((lx, ly, lz))
    xs = [(mw @ v.co).x for v in o.data.vertices]
    print("AFTER", name, round(min(xs), 2), round(max(xs), 2))
bpy.ops.wm.save_as_mainfile(filepath=F)
