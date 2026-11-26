"""TV picture for «دیوار» (wagon style): the puppet news anchor -> textures/anchor_pp.png, then textures/tv.png
(run with bpy, then `python3 -c` the paste step in the comment below; the plain red 'urgent' band of the first version kept: no logos, no place names)."""
import bpy, os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "puppets"))
sys.path.insert(0, os.path.join(HERE, "..", "cast"))
bpy.ops.wm.read_factory_settings(use_empty=True)
import puppets as PP, mocap, props as P  # noqa: E402
sc = bpy.context.scene
ch = PP.spawn("anchor")
clip = mocap.load(os.path.join(HERE, "..", "mocap", "breathing_idle.fbx"))
mocap.apply(ch, clip, start=1, length=2, src_from=1.0, offset=(0, 0, 0), facing=180, in_place=True)
bpy.data.objects.remove(clip.arm)
sc.frame_set(1)
PP.finish(ch, look=(0, -3, 1.6), smile=0)
ch.face["mouth"].data.shape_keys.key_blocks["open"].value = 0.3
P.box((0, 1.0, 1.5), (4, 0.1, 3), PP.toon_mat("studio", (0.1, 0.2, 0.45), 0.5), "Wall")
P.box((0, -0.4, 0.95), (1.6, 0.6, 0.06), PP.toon_mat("desk", (0.9, 0.9, 0.92), 0.3), "Desk")
w = bpy.data.worlds.new("W"); sc.world = w; w.color = (0.6, 0.6, 0.65)
sun = bpy.data.objects.new("Sun", bpy.data.lights.new("Sun", "SUN")); sc.collection.objects.link(sun)
sun.data.energy = 3.0; sun.rotation_euler = (math.radians(55), 0, math.radians(-25))
sc.render.engine = "CYCLES"; sc.cycles.samples = 24; sc.cycles.use_denoising = True
sc.view_settings.view_transform = "Standard"
cam = bpy.data.objects.new("C", bpy.data.cameras.new("C")); sc.collection.objects.link(cam); sc.camera = cam
hb = ch.rig.matrix_world @ ch.rig.pose.bones["head"].head
cam.location = (0, -3.4, hb.z - 0.12); cam.data.lens = 42; cam.rotation_euler = (math.radians(90), 0, 0)
sc.render.resolution_x, sc.render.resolution_y = 800, 450
sc.render.filepath = os.path.join(HERE, "textures", "anchor_pp.png")
bpy.ops.render.render(write_still=True)
print("anchor rendered; band: python3 below")
# band (system python, Pillow):
# from PIL import Image; a = Image.open("textures/anchor_pp.png").convert("RGB")
# a.paste(Image.open("../wall/textures/tv.png").convert("RGB").crop((0, 360, 800, 450)), (0, 360)); a.save("textures/tv.png")
