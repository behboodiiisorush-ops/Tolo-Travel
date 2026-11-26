"""Mixamo test: Arian (comic look) jogging in a circle -> mocap/test/jog_XXXX.png"""
import bpy, sys, os, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "cast"))
sys.path.insert(0, os.path.join(HERE, "..", "studio"))
bpy.ops.wm.read_factory_settings(use_empty=True)
import cast, mocap, props as P, toon_look as T
cast.STYLE = cast.CARTOON
sc = bpy.context.scene
sc.render.fps = 24
ch = cast.spawn("arian")
T.register(ch, "arian", realistic=True)
clip = mocap.load(os.path.join(HERE, "jog_in_circle.fbx"))
print("CLIP fps", clip.fps, "frames", clip.first, clip.last, "sec", clip.seconds)
n = mocap.apply(ch, clip, start=1, offset=(0, 0, 0), facing=180)
sc.frame_start, sc.frame_end = 1, n
floor = P.box((0, 0, -0.05), (14, 14, 0.1), P.mat("Floor", (0.55, 0.45, 0.35), 0.8), "Floor")
wall = P.box((0, 5, 1.5), (14, 0.2, 3), P.mat("Back wall", (0.3, 0.42, 0.5), 0.8), "Wall")
w = bpy.data.worlds.new("W"); sc.world = w; w.color = (0.4, 0.42, 0.45)
sun = bpy.data.objects.new("Sun", bpy.data.lights.new("Sun", "SUN")); sc.collection.objects.link(sun)
sun.data.energy = 2.2; sun.rotation_euler = (math.radians(55), 0, math.radians(-35))
T.toonify(sc)
T.ink([o for o in bpy.data.objects if o.type == "MESH" and o.name not in ("Wall", "Floor") and not o.hide_render
       and not any(k in o.name.lower() for k in ("high-poly", "lash", "brow", "teeth", "tongue", "short"))], 0.004)
cam = bpy.data.objects.new("C", bpy.data.cameras.new("C")); sc.collection.objects.link(cam); sc.camera = cam
cam.location = (0, -7.5, 1.6); cam.data.lens = 28; cam.rotation_euler = (math.radians(86), 0, 0)
sc.render.resolution_x, sc.render.resolution_y = 540, 960
frames = [int(v) for v in sys.argv[sys.argv.index("--frames") + 1].split(",")] if "--frames" in sys.argv else range(1, n + 1)
track = bpy.data.objects.new("trk", None); sc.collection.objects.link(track)
for f in range(1, n + 1):
    sc.frame_set(f)
    track.location = ch.rig.matrix_world @ ch.rig.pose.bones["pelvis"].head
    track.location.z = 1.1
    track.keyframe_insert("location", frame=f)
con = cam.constraints.new("TRACK_TO"); con.target = track; con.track_axis = "TRACK_NEGATIVE_Z"; con.up_axis = "UP_Y"
cam.data.lens = 40
for f in frames:
    if os.path.exists(os.path.join(HERE, "test", f"jog_{f:04d}.png")):
        continue
    sc.frame_set(f)
    sc.render.filepath = os.path.join(HERE, "test", f"jog_{f:04d}.png")
    bpy.ops.render.render(write_still=True)
