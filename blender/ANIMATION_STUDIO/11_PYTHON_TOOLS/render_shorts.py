"""Cameras (9:16 and test framings), lighting, render engines and output for tests and shorts.

  engine "VIEWPORT"  Workbench (solid, outlines, object colours): what the animator sees in the viewport. Fast:
                     used for every motion test.
  engine "CYCLES"    the approved puppet look (Toon BSDF + outlines), 10 samples + denoise.
  engine "EEVEE"     BLENDER_EEVEE (needs a GPU/OpenGL context; falls back to Cycles in a headless container).
Frames go to <out>_####.png, then ffmpeg makes <out>.mp4. Already rendered frames are skipped (resumable).
"""
import bpy
import os
import subprocess
from mathutils import Vector

import project_config as PC


def stage(sc, ground=True, sky=(0.66, 0.76, 0.86), sun=3.0, grid=True):
    """Light grey studio floor with a 0.5 m grid (foot sliding is visible against it), sky colour, one sun."""
    import puppets as PP
    w = bpy.data.worlds.get("UHAS world") or bpy.data.worlds.new("UHAS world")
    sc.world = w
    w.use_nodes = True
    bg = w.node_tree.nodes.get("Background")
    bg.inputs["Color"].default_value = (*[c ** 2.2 for c in sky], 1)
    if "UHAS sun" not in bpy.data.objects:
        s = bpy.data.objects.new("UHAS sun", bpy.data.lights.new("UHAS sun", "SUN"))
        sc.collection.objects.link(s)
        s.data.energy = sun
        s.data.angle = 0.14
        s.rotation_euler = (0.87, 0.0, -0.52)
    if ground and "UHAS floor" not in bpy.data.objects:
        bpy.ops.mesh.primitive_plane_add(size=60, location=(0, 0, 0))
        fl = bpy.context.object
        fl.name = "UHAS floor"
        fl.data.materials.append(PP.toon_mat("uhas floor", (0.9, 0.9, 0.88), 0.25))
        if grid:
            for i in range(-30, 31):
                for axis in (0, 1):
                    bpy.ops.mesh.primitive_cube_add(size=1)
                    ln = bpy.context.object
                    ln.name = "UHAS grid"
                    ln.scale = (30, 0.004, 0.001) if axis == 0 else (0.004, 30, 0.001)
                    ln.location = (0, i * 0.5, 0.001) if axis == 0 else (i * 0.5, 0, 0.001)
                    ln.data.materials.append(PP.toon_mat("uhas grid", (0.55, 0.58, 0.62), 0.1))
            bpy.ops.object.select_all(action="DESELECT")
            for o in bpy.data.objects:
                if o.name.startswith("UHAS grid"):
                    o.select_set(True)
            bpy.context.view_layer.objects.active = next(o for o in bpy.data.objects if o.name.startswith("UHAS grid"))
            bpy.ops.object.join()
            bpy.context.object.name = "UHAS grid"


def camera(sc, name="UHAS cam", lens=35, sensor_fit="AUTO"):
    cam = bpy.data.objects.get(name)
    if cam is None:
        cam = bpy.data.objects.new(name, bpy.data.cameras.new(name))
        sc.collection.objects.link(cam)
    cam.data.lens = lens
    cam.data.sensor_fit = sensor_fit
    sc.camera = cam
    return cam


def aim(cam, loc, target, frame=None):
    cam.location = loc
    d = Vector(target) - Vector(loc)
    cam.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    if frame is not None:
        cam.keyframe_insert("location", frame=frame)
        cam.keyframe_insert("rotation_euler", frame=frame)


def follow(cam, rig, f0, f1, offset=(3.2, 0.0, 0.3), look_h=0.85, bone="torso", smooth=6):
    """Side/three-quarter camera that tracks the character (smoothed so it doesn't jitter with the steps)."""
    sc = bpy.context.scene
    pos = []
    for f in range(f0, f1 + 1):
        sc.frame_set(f)
        pos.append(rig.matrix_world @ rig.pose.bones[bone].head)
    for i, f in enumerate(range(f0, f1 + 1)):
        a, b = max(0, i - smooth), min(len(pos) - 1, i + smooth)
        p = sum(pos[a:b + 1], Vector()) / (b - a + 1)
        t = Vector((p.x, p.y, look_h))
        aim(cam, t + Vector(offset), t, frame=f)


def setup_engine(sc, engine="VIEWPORT", res=(540, 960), samples=PC.CYCLES_SAMPLES):
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.resolution_percentage = 100
    sc.view_settings.view_transform = "Standard"
    if engine == "VIEWPORT":
        sc.render.engine = "BLENDER_WORKBENCH"
        sh = sc.display.shading
        sh.light = "STUDIO"
        sh.color_type = "MATERIAL"
        sh.show_object_outline = True
        sh.show_cavity = True
        sc.display.render_aa = "8"
    elif engine == "EEVEE":
        try:
            sc.render.engine = "BLENDER_EEVEE"
        except TypeError:
            sc.render.engine = "BLENDER_EEVEE_NEXT"
    else:
        sc.render.engine = "CYCLES"
        sc.cycles.samples = samples
        sc.cycles.use_denoising = True
        sc.cycles.max_bounces = 3
    sc.render.image_settings.file_format = "PNG"


def render(sc, out, f0, f1, step=1, overlay=None):
    """Render frames f0..f1 to out_####.png (skip existing) and make out.mp4 (fps = scene fps / step).
    overlay(frame) -> text: burnt into the frame by ffmpeg drawtext is avoided; we keep frames clean."""
    os.makedirs(os.path.dirname(out), exist_ok=True)
    frames = list(range(f0, f1 + 1, step))
    for f in frames:
        p = f"{out}_{f:04d}.png"
        if os.path.exists(p):
            continue
        sc.frame_set(f)
        sc.render.filepath = p
        try:
            bpy.ops.render.render(write_still=True)
        except RuntimeError as e:
            if sc.render.engine.startswith("BLENDER_EEVEE"):
                print("EEVEE unavailable here, falling back to Cycles:", e)
                setup_engine(sc, "CYCLES", (sc.render.resolution_x, sc.render.resolution_y))
                bpy.ops.render.render(write_still=True)
            else:
                raise
    return to_mp4(out, frames, max(1, round(PC.FPS / step)))


def to_mp4(out, frames, fps):
    lst = out + "_list.txt"
    with open(lst, "w") as fh:
        for f in frames:
            fh.write(f"file '{os.path.basename(out)}_{f:04d}.png'\nduration {1 / fps:.5f}\n")
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst,
                    "-vf", "pad=ceil(iw/2)*2:ceil(ih/2)*2", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18",
                    "-r", str(fps), out + ".mp4"], check=True, cwd=os.path.dirname(out))
    os.remove(lst)
    return out + ".mp4"


def clean_frames(out):
    d, b = os.path.dirname(out), os.path.basename(out)
    for fn in os.listdir(d):
        if fn.startswith(b + "_") and fn.endswith(".png"):
            os.remove(os.path.join(d, fn))
