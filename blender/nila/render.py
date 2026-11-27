"""Render frames of nila.blend (built by scene.py --save):  ../cast/bpy.sh render.py 1 264 [pct] [samples]"""
import bpy, sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
a, b = int(sys.argv[1]), int(sys.argv[2])
pct = int(sys.argv[3]) if len(sys.argv) > 3 else 67
smp = int(sys.argv[4]) if len(sys.argv) > 4 else 16
TAG = "_toon" if os.environ.get("LOOK") == "toon" else ""     # LOOK=toon -> the comic version
bpy.ops.wm.open_mainfile(filepath=os.path.join(HERE, f"nila{TAG}.blend"))
sc = bpy.context.scene
sc.render.resolution_percentage = pct
if TAG:
    sc.eevee.taa_render_samples = smp
else:
    sc.cycles.samples = smp
d = os.path.join(HERE, "frames" + TAG)
os.makedirs(d, exist_ok=True)
for f in range(a, b + 1):
    p = os.path.join(d, f"f_{f:04d}.png")
    if os.path.exists(p) and os.path.getsize(p) > 0:
        continue
    sc.frame_set(f)
    sc.render.filepath = p
    bpy.ops.render.render(write_still=True)
