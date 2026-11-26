"""TV picture for «دیوار»: the news anchor (comic look) -> textures/anchor.png, then textures/tv.png with a plain
red 'urgent' band (no logos, no place names)."""
import bpy, sys, os, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "cast"))
sys.path.insert(0, os.path.join(HERE, "..", "studio"))
bpy.ops.wm.read_factory_settings(use_empty=True)
import cast, props as P, toon_look as T
cast.STYLE = cast.CARTOON
sc = bpy.context.scene
ch = cast.spawn("anchor")
ch.animate(1, 0.5, (0, 0, 0), 180, worry=0.3)
ch.flush()
T.register(ch, "anchor", realistic=True)
P.box((0, 1.0, 1.5), (4, 0.1, 3), P.mat("Studio wall", (0.12, 0.2, 0.38), 0.8), "Wall")
P.box((0, -0.35, 0.95), (1.6, 0.7, 0.06), P.mat("Desk", (0.85, 0.86, 0.88), 0.4), "Desk")
w = bpy.data.worlds.new("W"); sc.world = w; w.color = (0.5, 0.5, 0.55)
sun = bpy.data.objects.new("Sun", bpy.data.lights.new("Sun", "SUN")); sc.collection.objects.link(sun)
sun.data.energy = 2.4; sun.rotation_euler = (math.radians(55), 0, math.radians(-25))
sc.frame_set(1)
T.toonify(sc)
T.ink([o for o in bpy.data.objects if o.type == "MESH" and o.name not in ("Wall",)
       and not any(k in o.name.lower() for k in ("high-poly", "lash", "brow", "teeth", "tongue"))], 0.003)
cam = bpy.data.objects.new("C", bpy.data.cameras.new("C")); sc.collection.objects.link(cam); sc.camera = cam
hb = ch.rig.matrix_world @ ch.rig.pose.bones["head"].head
cam.location = (0, -2.6, hb.z - 0.05); cam.data.lens = 55; cam.rotation_euler = (math.radians(90), 0, 0)
sc.render.resolution_x, sc.render.resolution_y = 800, 450
os.makedirs(os.path.join(HERE, "textures"), exist_ok=True)
sc.render.filepath = os.path.join(HERE, "textures", "anchor.png")
bpy.ops.render.render(write_still=True)
