"""Check the soldier's sleeve / bite: ../cast/bpy.sh test_arm.py -> test/arm_*.png"""
import bpy, sys, os, math
from mathutils import Vector
HERE = os.path.dirname(os.path.abspath(__file__))
for p in (HERE, os.path.join(HERE, "..", "cast"), os.path.join(HERE, "..", "studio")):
    sys.path.insert(0, p)
bpy.ops.wm.read_factory_settings(use_empty=True)
import cast, mocap, props as P, toon_look as T, arm
cast.STYLE = cast.CARTOON
sc = bpy.context.scene
sc.render.fps = 24
ch = cast.spawn("soldier")
T.register(ch, "soldier", realistic=True)
A = arm.build(ch)
A.stain([(0, 0.5), (1.0, 1.0)])
A.reveal(2.0)
clip = mocap.load(os.path.join(HERE, "..", "mocap", "hands_forward_gesture.fbx"))
mocap.apply(ch, clip, start=1, length=80, offset=(0, 0, 0), facing=180)
P.box((0, 2, 1.5), (6, 0.1, 3), P.mat("Wall", (0.5, 0.55, 0.6), 0.9), "Wall")
P.box((0, 0, -0.05), (6, 6, 0.1), P.mat("Floor", (0.6, 0.45, 0.3), 0.9), "Floor")
w = bpy.data.worlds.new("W"); sc.world = w; w.color = (0.5, 0.5, 0.55)
sun = bpy.data.objects.new("Sun", bpy.data.lights.new("Sun", "SUN")); sc.collection.objects.link(sun)
sun.data.energy = 2.6; sun.rotation_euler = (math.radians(50), 0, math.radians(-35))
sc.frame_set(1)
T.toonify(sc, samples=8)
T.ink([o for o in bpy.data.objects if o.type == "MESH" and not any(k in o.name.lower() for k in
       ("high-poly", "lash", "brow", "teeth", "tongue", "wall", "floor", "bite", "stain", "vein"))], 0.004)
cam = bpy.data.objects.new("C", bpy.data.cameras.new("C")); sc.collection.objects.link(cam); sc.camera = cam
sc.render.resolution_x, sc.render.resolution_y = 540, 960
os.makedirs(os.path.join(HERE, "test"), exist_ok=True)
for f, name, close in ((20, "before_full", False), (30, "before_close", True), (70, "after_close", True), (70, "after_full", False)):
    sc.frame_set(f)
    rig = ch.rig
    ua = (rig.matrix_world @ rig.pose.bones["upperarm_r"].head).lerp(rig.matrix_world @ rig.pose.bones["lowerarm_r"].head, 0.75)
    if close:
        cam.location = ua + Vector((-0.5, -0.6, 0.15)); tgt = ua; cam.data.lens = 40
    else:
        cam.location = (0, -3.2, 1.3); tgt = Vector((0, 0, 1.0)); cam.data.lens = 30
    cam.rotation_euler = (tgt - cam.location).to_track_quat("-Z", "Y").to_euler()
    sc.render.filepath = os.path.join(HERE, "test", f"arm_{name}.png")
    bpy.ops.render.render(write_still=True)
