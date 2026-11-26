"""Puppet cast sheet: sheets/lineup.png (full bodies, each in a Mixamo pose) + sheets/faces.png."""
import bpy, os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "cast"))
bpy.ops.wm.read_factory_settings(use_empty=True)
import puppets as PP  # noqa: E402
import mocap          # noqa: E402
import props as P     # noqa: E402
sc = bpy.context.scene
MOC = os.path.join(HERE, "..", "mocap")
ROW = [("rezaei", "breathing_idle", 1.0), ("kazemi", "thinking", 1.5), ("mom", "terrified", 1.0),
       ("me", "breathing_idle", 0.5), ("arian", "nervously_look_around", 1.0), ("mahsa", "hands_forward_gesture", 1.2),
       ("kian", "head_nod_yes", 0.6), ("anchor", "dismissing_gesture", 0.8)]
only = sys.argv[sys.argv.index("--only") + 1].split(",") if "--only" in sys.argv else None
if only:
    ROW = [r for r in ROW if r[0] in only]
clips = {}
chars = []
n = len(ROW)
for i, (k, clip, at) in enumerate(ROW):
    if clip not in clips:
        clips[clip] = mocap.load(os.path.join(MOC, clip + ".fbx"))
    ch = PP.spawn(k)
    x = (i - (n - 1) / 2) * 0.78
    mocap.apply(ch, clips[clip], start=1, length=2, src_from=at, offset=(x, 0, 0), facing=180, in_place=True)
    chars.append(ch)
for c in clips.values():
    bpy.data.objects.remove(c.arm)
sc.frame_set(1)
W = 0.78 * n
for ch in chars:
    PP.finish(ch, look=(ch.rig.location.x * 0.4, -W * 1.35 - 1.5, 1.4))
floor = P.box((0, 0, -0.05), (20, 20, 0.1), PP.toon_mat("floor", (0.9, 0.86, 0.78), 0.25), "Floor")
back = P.box((0, 3.0, 3), (20, 0.1, 6), PP.toon_mat("back", (0.55, 0.78, 0.86), 0.3), "Back")
w = bpy.data.worlds.new("W"); sc.world = w; w.color = (0.7, 0.72, 0.75)
sun = bpy.data.objects.new("Sun", bpy.data.lights.new("Sun", "SUN")); sc.collection.objects.link(sun)
sun.data.energy = 3.2; sun.rotation_euler = (math.radians(50), 0, math.radians(-30)); sun.data.angle = math.radians(8)
sc.render.engine = "CYCLES"; sc.cycles.samples = 24; sc.cycles.use_denoising = True
sc.view_settings.view_transform = "Standard"
cam = bpy.data.objects.new("C", bpy.data.cameras.new("C")); sc.collection.objects.link(cam); sc.camera = cam
sc.frame_set(1)
os.makedirs(os.path.join(HERE, "sheets"), exist_ok=True)
W = 0.78 * n
sc.render.resolution_x, sc.render.resolution_y = 1800, 900
cam.location = (0, -W * 1.35 - 1.5, 1.0); cam.data.lens = 50; cam.rotation_euler = (math.radians(89), 0, 0)
sc.render.filepath = os.path.join(HERE, "sheets", "lineup.png"); bpy.ops.render.render(write_still=True)
sc.render.resolution_x, sc.render.resolution_y = 1800, 380
cam.location = (0, -W * 1.6 - 1.5, 1.62); cam.data.lens = 80; cam.rotation_euler = (math.radians(90), 0, 0)
sc.render.filepath = os.path.join(HERE, "sheets", "faces.png"); bpy.ops.render.render(write_still=True)
