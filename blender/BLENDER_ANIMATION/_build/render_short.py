"""Render a short into SHORTS/Renders/<name>_####.png (skips frames already there, so it can resume), then mp4.
    ../../cast/bpy.sh render_short.py Episode_01 [--full]      (--full = 1080x1920, default 540x960 preview)"""
import bpy, os, sys, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib  # noqa: E402
name = [a for a in sys.argv[1:] if a.startswith("Episode")][0]
bpy.ops.wm.open_mainfile(filepath=lib.path("SHORTS", name + ".blend"))
sc = bpy.context.scene
sc.render.resolution_percentage = 100 if "--full" in sys.argv else 50
out = lib.path("SHORTS", "Renders")
os.makedirs(out, exist_ok=True)
for f in range(sc.frame_start, sc.frame_end + 1):
    p = os.path.join(out, f"{name}_{f:04d}.png")
    if os.path.exists(p):
        continue
    sc.frame_set(f)
    sc.render.filepath = p
    bpy.ops.render.render(write_still=True)
subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-framerate", str(lib.FPS), "-start_number", str(sc.frame_start),
                "-i", os.path.join(out, f"{name}_%04d.png"), "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18",
                os.path.join(out, name + ".mp4")], check=True)
print("done", os.path.join(out, name + ".mp4"))
