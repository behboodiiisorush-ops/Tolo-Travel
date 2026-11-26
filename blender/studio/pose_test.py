"""Pose test: crawl, boost, intruder mask, POV boy -> test/poses.png"""
import bpy, sys, os, math, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
bpy.ops.wm.read_factory_settings(use_empty=True)
import characters as C
import props as P
sc = bpy.context.scene
t0 = time.time()
a = C.spawn("arian"); a.animate(1, 0.3, (-1.6, 0, 0), 90, crawl=1, arms="crawl", phase=0.8, look=(0, 0))
b = C.spawn("intruder"); b.animate(1, 0.3, (0, 0, 0), 180, arms="reach", reach=70, hands="grip", brows="angry")
m = C.spawn("me"); m.animate(1, 0.3, (1.0, 0, 0), 180, arms="boost", hands="open", look=(0, 30))
n = C.spawn("nina"); n.animate(1, 0.3, (2.0, 0, 0), 180, mouth=dict(smile=0.45), suspicious=True)
for ch in (a, b, m, n):
    ch.flush()
print("spawn time", time.time() - t0)
P.enable_outlines(sc, 1.2)
w = bpy.data.worlds.new("W"); sc.world = w; w.color = (0.22, 0.25, 0.3)
P.area_light((2, -4, 4), (0, 0, 1), 700, 4, (1.0, 0.96, 0.9))
P.area_light((-3, -3, 2), (0, 0, 1), 220, 4, (0.8, 0.88, 1.0))
sc.render.engine = "CYCLES"; sc.cycles.samples = 12; sc.cycles.use_denoising = True
sc.view_settings.view_transform = "AgX"; sc.view_settings.look = "AgX - Medium Low Contrast"
cam = bpy.data.objects.new("C", bpy.data.cameras.new("C")); sc.collection.objects.link(cam); sc.camera = cam
sc.frame_set(1)
sc.render.resolution_x, sc.render.resolution_y = 1400, 700
cam.location = (0.2, -6.0, 1.0); cam.data.lens = 40; cam.rotation_euler = (math.radians(88), 0, 0)
os.makedirs(os.path.join(HERE, "test"), exist_ok=True)
sc.render.filepath = os.path.join(HERE, "test", "poses.png"); bpy.ops.render.render(write_still=True)
