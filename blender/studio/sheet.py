"""Character sheet for the studio cast: sheets/lineup.png (full body) + sheets/faces.png."""
import bpy, sys, os, math
from mathutils import Vector
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
bpy.ops.wm.read_factory_settings(use_empty=True)
import characters as C
import props as P
sc = bpy.context.scene
keys = ["nina", "arian", "mom", "kian", "kazemi"]
poses = [dict(brows="neutral"), dict(brows="worried", hands="point_r", arm_r=(80, 10)), dict(mouth=dict(smile=0.8)),
         dict(brows="surprised", mouth=dict(o=0.8)), dict(brows="angry", suspicious=True)]
chars = []
for i, k in enumerate(keys):
    ch = C.spawn(k)
    x = (i - 2) * 0.85
    st = dict(poses[i])
    hands = st.pop("hands", "relaxed")
    ch.animate(1, 0.3, (x, 0, 0), 180, arms="rest", hands=hands, look_at=(x * 0.3, -3.0, 1.5), **st)
    ch.flush()
    chars.append((ch, x))
P.enable_outlines(sc, 1.2)
w = bpy.data.worlds.new("W"); sc.world = w; w.color = (0.22, 0.25, 0.3)
P.area_light((2, -4, 4), (0, 0, 1), 700, 4, (1.0, 0.96, 0.9))
P.area_light((-3, -3, 2), (0, 0, 1), 220, 4, (0.8, 0.88, 1.0))
P.area_light((0, 3, 3), (0, 0, 1.5), 300, 3)
sc.render.engine = "CYCLES"; sc.cycles.samples = 20; sc.cycles.use_denoising = True
sc.view_settings.view_transform = "AgX"; sc.view_settings.look = "AgX - Medium Low Contrast"
cam = bpy.data.objects.new("C", bpy.data.cameras.new("C")); sc.collection.objects.link(cam); sc.camera = cam
sc.frame_set(1)
os.makedirs(os.path.join(HERE, "sheets"), exist_ok=True)
sc.render.resolution_x, sc.render.resolution_y = 1600, 900
cam.location = (0, -6.2, 1.0); cam.data.lens = 45; cam.rotation_euler = (math.radians(88), 0, 0)
sc.render.filepath = os.path.join(HERE, "sheets", "lineup.png"); bpy.ops.render.render(write_still=True)
sc.render.resolution_x, sc.render.resolution_y = 1600, 420
cam.location = (0, -7.5, 1.55); cam.data.lens = 85; cam.rotation_euler = (math.radians(90), 0, 0)
sc.render.filepath = os.path.join(HERE, "sheets", "faces.png"); bpy.ops.render.render(write_still=True)
