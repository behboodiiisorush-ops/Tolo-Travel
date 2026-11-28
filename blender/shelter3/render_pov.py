"""Render the odd frames a..b of pov.blend (on twos):  ../cast/bpy.sh render_pov.py a-b  -> frames/f_XXXX.png
Skips frames already on disk, so it can be restarted any time."""
import bpy, sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
WIDE = os.environ.get("WIDE", "") == "1"
FR = "frames_wide" if WIDE else "frames"
bpy.ops.wm.open_mainfile(filepath=os.path.join(HERE, "pov_wide.blend" if WIDE else "pov.blend"))
sc = bpy.context.scene
sc.cycles.samples = int(os.environ.get("SAMPLES", "12"))
a, b = [int(v) for v in sys.argv[-1].split("-")]
b = min(b, sc.frame_end)
os.makedirs(os.path.join(HERE, FR), exist_ok=True)
for f in range(a | 1, b + 1, 2):
    out = os.path.join(HERE, FR, f"f_{f:04d}.png")
    if os.path.exists(out) and os.path.getsize(out) > 0:
        continue
    sc.frame_set(f)
    sc.render.filepath = out
    bpy.ops.render.render(write_still=True)
