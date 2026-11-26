"""Test sheet for the comic look: sheets/faces_toon.png (Arian scared + sweating, Nina sly, me worried)."""
import bpy, sys, os, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
bpy.ops.wm.read_factory_settings(use_empty=True)
import characters as C
import props as P
import toon_look as T
sc = bpy.context.scene
cast = [("nina", -0.75, dict(brows="neutral", suspicious=True, mouth=dict(smile=0.35))),
        ("arian", 0.0, dict(brows="worried", worry=1.6, mouth=dict(o=0.45, frown=0.2))),
        ("me", 0.75, dict(brows="surprised", mouth=dict(open=0.3)))]
chars = []
for k, x, st in cast:
    ch = C.spawn(k)
    ch.animate(1, 0.3, (x, 0, 0), 180, arms="rest", hands="relaxed", look_at=(x * 0.4, -3.0, 1.5), **st)
    ch.flush()
    chars.append(ch)
    T.register(ch, k)
sc.frame_set(1)
T.sweat(chars[1], frames=(1, 1), n=5)
T.sweat(chars[2], frames=(1, 1), n=2, seed=4)
sc.frame_set(3)
# backdrop: wall + floor
wall = P.box((0, 1.2, 1.5), (6, 0.1, 3), P.mat("Back wall", (0.42, 0.55, 0.6), 0.8), "Wall")
floor = P.box((0, 0, -0.05), (6, 4, 0.1), P.mat("Floor", (0.45, 0.33, 0.24), 0.8), "Floor")
w = bpy.data.worlds.new("W"); sc.world = w; w.color = (0.35, 0.38, 0.42)
sun = bpy.data.objects.new("Sun", bpy.data.lights.new("Sun", "SUN")); sc.collection.objects.link(sun)
sun.data.energy = 2.2; sun.rotation_euler = (math.radians(60), 0, math.radians(-35))
T.toonify(sc)
T.ink([o for o in bpy.data.objects if o.type == "MESH" and o.name not in ("Wall", "Floor")], 0.005)
cam = bpy.data.objects.new("C", bpy.data.cameras.new("C")); sc.collection.objects.link(cam); sc.camera = cam
sc.render.resolution_x, sc.render.resolution_y = 1600, 700
cam.location = (0, -6.0, 1.48); cam.data.lens = 72; cam.rotation_euler = (math.radians(90), 0, 0)
os.makedirs(os.path.join(HERE, "sheets"), exist_ok=True)
sc.render.filepath = os.path.join(HERE, "sheets", "faces_toon.png")
bpy.ops.render.render(write_still=True)
