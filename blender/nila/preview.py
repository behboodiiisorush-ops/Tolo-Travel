"""Fast preview of every frame (Workbench, solid, studio light) for motion review before the final render.
    ../cast/bpy.sh preview.py [pct]   -> preview/p_0001.png ... + preview.mp4"""
import bpy, sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
pct = int(sys.argv[1]) if len(sys.argv) > 1 else 30
bpy.ops.wm.open_mainfile(filepath=os.path.join(HERE, "nila.blend"))
sc = bpy.context.scene
sc.render.engine = "BLENDER_WORKBENCH"
sh = sc.display.shading
sh.light, sh.color_type = "STUDIO", "MATERIAL"
sh.show_cavity = True
sc.render.resolution_percentage = pct
sc.render.use_simplify = True
sc.render.simplify_subdivision_render = 0
sc.display.render_aa = "OFF" if len(sys.argv) > 2 else "FXAA"
import time
d = os.path.join(HERE, "preview")
os.makedirs(d, exist_ok=True)
for f in range(sc.frame_start, sc.frame_end + 1):
    sc.frame_set(f)
    sc.render.filepath = os.path.join(d, f"p_{f:04d}.png")
    p = os.path.join(d, f"p_{f:04d}.png")
    if os.path.exists(p) and os.path.getsize(p) > 0:
        continue
    t = time.time()
    bpy.ops.render.render(write_still=True)
    print("PV", f, round(time.time() - t, 1), flush=True)
