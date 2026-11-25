"""Comic look on the realistic cast (real head + neck proportions): sheets/faces_toon2.png."""
import bpy, sys, os, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "cast"))
bpy.ops.wm.read_factory_settings(use_empty=True)
import cast
cast.STYLE = cast.CARTOON      # bigger eyes, smaller nose, rounder younger face
import props as P
import toon_look as T
sc = bpy.context.scene
cast_list = [("mahsa", -0.75, dict(worry=0.4, look=(0, 0))),
             ("arian", 0.0, dict(worry=1.6, look=(0, 0))),
             ("me", 0.75, dict(worry=0.8, look=(0, 0)))]
chars = []
for k, x, st in cast_list:
    ch = cast.spawn(k)
    ch.animate(1, 0.3, (x, 0, 0), 180, **st)
    ch.flush()
    T.register(ch, k, realistic=True)
    chars.append(ch)
sc.frame_set(1)
wall = P.box((0, 1.2, 1.5), (6, 0.1, 3), P.mat("Back wall", (0.3, 0.42, 0.5), 0.8), "Wall")
floor = P.box((0, 0, -0.05), (6, 4, 0.1), P.mat("Floor", (0.45, 0.33, 0.24), 0.8), "Floor")
w = bpy.data.worlds.new("W"); sc.world = w; w.color = (0.4, 0.42, 0.45)
sun = bpy.data.objects.new("Sun", bpy.data.lights.new("Sun", "SUN")); sc.collection.objects.link(sun)
sun.data.energy = 2.2; sun.rotation_euler = (math.radians(60), 0, math.radians(-35))
T.toonify(sc)
T.ink([o for o in bpy.data.objects if o.type == "MESH" and o.name not in ("Wall", "Floor")
       and not any(k in o.name.lower() for k in ("eye", "lash", "brow", "teeth", "tongue", "hair"))], 0.004)
cam = bpy.data.objects.new("C", bpy.data.cameras.new("C")); sc.collection.objects.link(cam); sc.camera = cam
sc.render.resolution_x, sc.render.resolution_y = 1600, 700
top = max(c.rig.matrix_world @ c.rig.pose.bones["head"].tail for c in chars).z if False else 1.5
cam.location = (0, -5.2, 1.45); cam.data.lens = 72; cam.rotation_euler = (math.radians(90), 0, 0)
sc.render.filepath = os.path.join(HERE, "sheets", "faces_toon2.png")
bpy.ops.render.render(write_still=True)
# close-up of Arian's face
sc.render.resolution_x, sc.render.resolution_y = 900, 900
hb = chars[1].rig.matrix_world @ chars[1].rig.pose.bones["head"].head
cam.location = (hb.x, -2.2, hb.z + 0.1); cam.data.lens = 85
sc.render.filepath = os.path.join(HERE, "sheets", "face_toon2_arian.png")
bpy.ops.render.render(write_still=True)
