"""Quick pose check (Workbench) of mocap clips on Arian: test/clips_<name>.png (6 moments per clip)."""
import bpy, sys, os, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "cast"))
bpy.ops.wm.read_factory_settings(use_empty=True)
import cast, mocap
sc = bpy.context.scene; sc.render.fps = 24
ch = cast.spawn("arian")
names = sys.argv[sys.argv.index("--clips") + 1].split(",")
sc.render.engine = "BLENDER_WORKBENCH"
sc.display.shading.light = "STUDIO"; sc.display.shading.color_type = "MATERIAL"
sc.display.shading.show_cavity = True
cam = bpy.data.objects.new("C", bpy.data.cameras.new("C")); sc.collection.objects.link(cam); sc.camera = cam
sc.render.resolution_x, sc.render.resolution_y = 400, 600
start = 1
for nm in names:
    clip = mocap.load(os.path.join(HERE, nm + ".fbx"))
    n = mocap.apply(ch, clip, start=start, facing=200)
    print("CLIP", nm, clip.fps, clip.seconds, n)
    tiles = []
    K = int(os.environ.get('K', '6'))
    for k in range(K):
        f = start + int(k * (n - 1) / max(1, K - 1))
        sc.frame_set(f)
        c = ch.rig.matrix_world @ ch.rig.pose.bones["spine_02"].head
        cam.location = (c.x + 0.6, c.y - 3.2, c.z + 0.3)
        d = c - cam.location
        cam.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
        cam.data.lens = 35
        sc.render.filepath = os.path.join(HERE, "test", f"clips_{nm}_{k}.png")
        bpy.ops.render.render(write_still=True)
    start += n + 10
