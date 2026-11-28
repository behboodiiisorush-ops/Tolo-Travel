"""Quick look at Nina + the masked man in the comic look:  ../cast/bpy.sh test_cast.py -> test/cast.png"""
import bpy, sys, os, math
from mathutils import Vector
HERE = os.path.dirname(os.path.abspath(__file__))
for p in (HERE, os.path.join(HERE, "..", "cast"), os.path.join(HERE, "..", "studio")):
    sys.path.insert(0, p)
bpy.ops.wm.read_factory_settings(use_empty=True)
import cast, mocap, props as P, toon_look as T  # noqa
cast.STYLE = cast.CARTOON
sc = bpy.context.scene
xs = {"nina": -0.5, "masked": 0.5}
for k, x in xs.items():
    ch = cast.spawn(k)
    T.register(ch, k, realistic=True)
    mocap.apply(ch, mocap.load(os.path.join(HERE, "..", "mocap", "breathing_idle.fbx")), start=1, length=10,
                offset=(x, 0, 0), facing=180)
P.box((0, 0, -0.05), (6, 6, 0.1), P.mat("floor", (0.4, 0.4, 0.4), 0.8), "floor")
P.box((0, 1.5, 1.5), (6, 0.1, 3), P.mat("wall", (0.7, 0.68, 0.62), 0.8), "wall")
sun = bpy.data.objects.new("Sun", bpy.data.lights.new("Sun", "SUN")); sc.collection.objects.link(sun)
sun.data.energy = 3; sun.rotation_euler = (math.radians(50), 0, math.radians(-30))
cam = bpy.data.objects.new("Cam", bpy.data.cameras.new("Cam")); sc.collection.objects.link(cam); sc.camera = cam
cam.location = (0.5, -1.4, 1.6); cam.rotation_euler = (Vector((0.5, 0, 1.6)) - cam.location).to_track_quat("-Z", "Y").to_euler()
cam.data.lens = 45
w = bpy.data.worlds.new("W"); sc.world = w; w.color = (0.1, 0.1, 0.12)
sc.frame_set(5)
T.SAT = 0.6
T.toonify(sc, samples=8)
T.ink([o for o in bpy.data.objects if o.type == "MESH" and not any(s in o.name.lower() for s in ("lash", "brow", "teeth", "tongue", "floor"))], 0.005)
sc.render.resolution_x, sc.render.resolution_y = 540, 960
sc.render.filepath = os.path.join(HERE, "test", "cast.png")
bpy.ops.render.render(write_still=True)
