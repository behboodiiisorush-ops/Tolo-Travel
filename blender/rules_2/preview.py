"""Fast motion check: ../cast/bpy.sh preview.py -> test/preview.mp4 (Workbench, 270x480, every 2nd frame)."""
import bpy, os, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
bpy.ops.wm.open_mainfile(filepath=os.path.join(HERE, "rules_2.blend"))
sc = bpy.context.scene
sc.render.engine = "BLENDER_WORKBENCH"
sc.display.shading.light = "STUDIO"
sc.display.shading.color_type = "MATERIAL"
sc.render.resolution_x, sc.render.resolution_y = 270, 480
d = os.path.join(HERE, "test", "pv")
os.makedirs(d, exist_ok=True)
for i, f in enumerate(range(1, sc.frame_end + 1, 2)):
    sc.frame_set(f)
    sc.render.filepath = os.path.join(d, f"p_{i:04d}.png")
    bpy.ops.render.render(write_still=True)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", "12", "-i", os.path.join(d, "p_%04d.png"),
                "-c:v", "libx264", "-pix_fmt", "yuv420p", os.path.join(HERE, "test", "preview.mp4")], check=True)
