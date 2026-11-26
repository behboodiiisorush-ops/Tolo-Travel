"""Render frames A..B of spark.blend (skips frames already on disk).  ../cast/bpy.sh render.py A B"""
import bpy, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
a, b = int(sys.argv[-2]), int(sys.argv[-1])
bpy.ops.wm.open_mainfile(filepath=os.path.join(HERE, "spark.blend"))
sc = bpy.context.scene
sc.eevee.taa_render_samples = int(os.environ.get("SAMPLES", "24"))
b = min(b, sc.frame_end)
os.makedirs(os.path.join(HERE, "frames"), exist_ok=True)
for f in range(a, b + 1):
    p = os.path.join(HERE, "frames", f"f_{f:04d}.png")
    if os.path.exists(p):
        continue
    sc.frame_set(f)
    sc.render.filepath = p
    bpy.ops.render.render(write_still=True)
