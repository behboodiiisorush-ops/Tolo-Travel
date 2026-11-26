import bpy, sys, os, math
from mathutils import Vector
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "cast"))
bpy.ops.wm.read_factory_settings(use_empty=True)
import house as H, props as P
h = H.build()
h.doors["living"].swing(1, 2, 0, 70)
h.doors["bedroom"].swing(1, 2, 0, 35)
sc = bpy.context.scene
sc.render.engine = "CYCLES"; sc.cycles.samples = 16; sc.cycles.use_denoising = True
sc.view_settings.view_transform = "AgX"; sc.view_settings.look = "AgX - Medium Low Contrast"
sc.render.resolution_x, sc.render.resolution_y = 540, 960
P.enable_outlines(sc, 1.0)
cam = bpy.data.objects.new("C", bpy.data.cameras.new("C")); sc.collection.objects.link(cam); sc.camera = cam
cam.data.lens = 16
sc.frame_set(2)
for nm, loc, tgt in (("hall", (0.1, 0.5, 1.6), (-0.3, 4.0, 1.4)), ("arch", (0.3, 1.0, 1.6), (-2.5, 1.2, 1.1)),
                     ("kitchen", (-1.2, 2.8, 1.6), (-2.6, 0.3, 1.0)), ("living", (1.2, 1.0, 1.6), (4.0, 4.0, 0.8))):
    cam.location = loc
    cam.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    sc.render.filepath = os.path.join(HERE, "sheets", f"house_{nm}.png")
    bpy.ops.render.render(write_still=True)
