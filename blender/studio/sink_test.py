import bpy, sys, os
from mathutils import Vector
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "cast"))
bpy.ops.wm.read_factory_settings(use_empty=True)
import house as H, props as P, characters as C
h = H.build()
n = C.spawn("nina")
for f, t in ((1, 0.0), (2, 0.4)):
    n.animate(f, t, (-2.0, 2.6, 0), 0, walk=1.0 if f == 2 else 0.0, phase=1.2, arms="rest")
n.flush()
sc = bpy.context.scene
sc.render.engine = "CYCLES"; sc.cycles.samples = 16; sc.cycles.use_denoising = True
sc.view_settings.view_transform = "AgX"; sc.view_settings.look = "AgX - Medium Low Contrast"
sc.render.resolution_x, sc.render.resolution_y = 540, 960
P.enable_outlines(sc, 1.0)
cam = bpy.data.objects.new("C", bpy.data.cameras.new("C")); sc.collection.objects.link(cam); sc.camera = cam
cam.data.lens = 16
for f, nm, loc, tgt in ((1, "arms", (-1.6, 3.85, 1.2), (-2.0, 2.6, 0.95)),
                        (2, "walk", (-1.6, 3.85, 1.2), (-2.0, 2.6, 0.95))):
    sc.frame_set(f)
    cam.location = loc
    cam.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    sc.render.filepath = os.path.join(HERE, "test", f"{nm}.png")
    bpy.ops.render.render(write_still=True)
