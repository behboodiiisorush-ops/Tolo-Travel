"""Render frames of train_bridge6.blend (frames on twos: odd numbers only).
    ../cast/vendor/venv/bin/python render.py 1-2023        -> frames/f_XXXX.png (skips frames on disk)
    ../cast/vendor/venv/bin/python render.py still 49,361  -> test/still_XXXX.png"""
import os, sys
import bpy
HERE = os.path.dirname(os.path.abspath(__file__))
bpy.ops.wm.open_mainfile(filepath=os.path.join(HERE, "train_bridge6.blend"))
sc = bpy.context.scene
if sys.argv[-2] == "still":
    todo = [(int(v), os.path.join(HERE, "test", f"still_{int(v):04d}.png")) for v in sys.argv[-1].split(",")]
else:
    a, b = [int(v) for v in sys.argv[-1].split("-")]
    os.makedirs(os.path.join(HERE, "frames"), exist_ok=True)
    todo = [(f, os.path.join(HERE, "frames", f"f_{f:04d}.png")) for f in range(a, b + 1) if f % 2 == 1]
for f, out in todo:
    if os.path.exists(out) and os.path.getsize(out) > 0 and "frames" in out:
        continue
    sc.frame_set(f)
    sc.render.filepath = out
    bpy.ops.render.render(write_still=True)
