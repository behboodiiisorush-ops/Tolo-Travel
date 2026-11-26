"""Reference sheet for the cartoon cast: sheets_toon/<key>.png and lineup.png"""
import bpy, sys, os, math
from mathutils import Vector
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
bpy.ops.wm.read_factory_settings(use_empty=True)
import toon_people as T, props as P
keys = [a for a in sys.argv[1:] if not a.endswith(".py")] or list(T.LOOKS)
sc = bpy.context.scene
chars = []
for i, k in enumerate(keys):
    z = k.endswith("_z")
    ch = T.spawn(k[:-2] if z else k, zombie=1.0 if z else 0.0, name=k.capitalize())
    ch.animate(1, 0.0, ((i - (len(keys) - 1) / 2) * 0.75, 0, 0), 180, arms="rest", worry=0.3)
    ch.flush()
    chars.append(ch)
P.toonify(sat=0.85, lift=0.0, size=0.55, ambient=0.26)
faces = [o for ch in chars for o in ch.eyes + ch.pupils + [ch.mouth]]
brows = [o for ch in chars for o in ch.brows]
people = [o for ch in chars for o in ch.objects if o.type == "MESH" and o not in faces and o not in brows]
P.enable_outlines(sc, 2.2, exclude=faces, contour_only=people, bold=brows)
w = bpy.data.worlds.new("W"); sc.world = w; w.color = (0.2, 0.22, 0.26)
P.area_light((2, -4, 4), (0, 0, 1), 900, 4)
P.area_light((-3, -3, 2), (0, 0, 1), 250, 4)
sc.render.engine = "CYCLES"; sc.cycles.samples = 16; sc.cycles.use_denoising = True
sc.view_settings.view_transform = "Standard"
cam = bpy.data.objects.new("C", bpy.data.cameras.new("C")); sc.collection.objects.link(cam); sc.camera = cam
n = len(keys)
sc.render.resolution_x, sc.render.resolution_y = max(540, 300 * n), 960
cam.location = (0, -5.5, 1.0); cam.data.lens = 50 if n > 2 else 70
cam.rotation_euler = (math.radians(88), 0, 0)
sc.frame_set(1)
os.makedirs(os.path.join(HERE, "sheets_toon"), exist_ok=True)
sc.render.filepath = os.path.join(HERE, "sheets_toon", "lineup.png")
bpy.ops.render.render(write_still=True)
