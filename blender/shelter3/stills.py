"""Render test stills from shelter3.blend:  ../cast/bpy.sh stills.py 12.5,30,...  (seconds) -> test/t_<sec>.png"""
import bpy, sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
bpy.ops.wm.open_mainfile(filepath=os.path.join(HERE, "shelter3.blend"))
sc = bpy.context.scene
for v in sys.argv[-1].split(","):
    f = int(round(float(v) * 24)) + 1
    sc.frame_set(f)
    sc.render.filepath = os.path.join(HERE, "test", f"t_{float(v):06.1f}.png")
    bpy.ops.render.render(write_still=True)
