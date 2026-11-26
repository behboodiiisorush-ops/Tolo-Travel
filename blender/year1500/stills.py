"""Test stills from year1500.blend: ../cast/bpy.sh stills.py 73,193,...  -> test/s_XXXX.png (skips existing)."""
import bpy, sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
bpy.ops.wm.open_mainfile(filepath=os.path.join(HERE, "year1500.blend"))
sc = bpy.context.scene
os.makedirs(os.path.join(HERE, "test"), exist_ok=True)
for f in [int(v) for v in sys.argv[-1].split(",")]:
    p = os.path.join(HERE, "test", f"s_{f:04d}.png")
    if os.path.exists(p) and os.path.getsize(p) > 0:
        continue
    sc.frame_set(f)
    sc.render.filepath = p
    bpy.ops.render.render(write_still=True)
