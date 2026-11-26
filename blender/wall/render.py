"""Render frames of wall.blend: ../cast/bpy.sh render.py a-b  -> frames/f_XXXX.png (skips frames on disk)."""
import bpy, sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
bpy.ops.wm.open_mainfile(filepath=os.path.join(HERE, "wall.blend"))
sc = bpy.context.scene
a, b = [int(v) for v in sys.argv[-1].split("-")]
b = min(b, sc.frame_end)
os.makedirs(os.path.join(HERE, "frames"), exist_ok=True)
for f in range(a | 1, b + 1, 2):          # on twos: odd frames only
    out = os.path.join(HERE, "frames", f"f_{f:04d}.png")
    if os.path.exists(out) and os.path.getsize(out) > 0:
        continue
    sc.frame_set(f)
    sc.render.filepath = out
    bpy.ops.render.render(write_still=True)
