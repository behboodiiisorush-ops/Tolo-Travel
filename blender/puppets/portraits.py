"""One portrait per puppet (head and shoulders, a Mixamo pose, an expression) -> sheets/p_<key>.png;
then python3 grid: sheets/portraits.png with Persian names."""
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
ROW = [("me", "breathing_idle", 0.5, dict(smile=0.5)), ("mom", "breathing_idle", 1.5, dict(frown=0.4)),
       ("kazemi", "thinking", 1.5, dict(frown=0.3)), ("arian", "breathing_idle", 2.0, dict(smile=0.6)),
       ("mahsa", "breathing_idle", 2.5, dict(smile=0.35, wide=0.2)), ("kian", "breathing_idle", 3.0, dict(o=0.35)),
       ("rezaei", "breathing_idle", 1.0, dict(smile=0.7)), ("anchor", "breathing_idle", 0.8, dict(open=0.25))]
BG = {"me": (0.98, 0.85, 0.55), "mom": (0.98, 0.72, 0.8), "kazemi": (0.68, 0.78, 0.95), "arian": (0.7, 0.9, 0.65),
      "mahsa": (0.62, 0.88, 0.9), "kian": (0.75, 0.85, 1.0), "rezaei": (0.98, 0.92, 0.65), "anchor": (0.8, 0.8, 0.86)}
clip = {}
chars = []
for i, (k, cn, at, face) in enumerate(ROW):
    if cn not in clip:
        clip[cn] = mocap.load(os.path.join(MOC, cn + ".fbx"))
    ch = PP.spawn(k)
    x = i * 4.0
    mocap.apply(ch, clip[cn], start=1, length=2, src_from=at, offset=(x, 0, 0), facing=180, in_place=True)
    chars.append((k, ch, x, face))
for c in clip.values():
    bpy.data.objects.remove(c.arm)
sc.frame_set(1)
for k, ch, x, face in chars:
    PP.finish(ch, look=(x, -3.0, 1.45), smile=0)
    kb = ch.face["mouth"].data.shape_keys.key_blocks
    for n, v in face.items():
        kb[n].value = v
    P.box((x, 1.2, 2), (3.2, 0.1, 4), PP.toon_mat(f"bg {k}", BG[k], 0.6), f"BG {k}")
floor = P.box((len(ROW) * 2, 0, -0.05), (60, 10, 0.1), PP.toon_mat("floor", (0.9, 0.86, 0.78), 0.25), "Floor")
w = bpy.data.worlds.new("W"); sc.world = w; w.color = (0.7, 0.72, 0.75)
sun = bpy.data.objects.new("Sun", bpy.data.lights.new("Sun", "SUN")); sc.collection.objects.link(sun)
sun.data.energy = 3.0; sun.rotation_euler = (math.radians(55), 0, math.radians(-28)); sun.data.angle = math.radians(8)
sc.render.engine = "CYCLES"; sc.cycles.samples = 32; sc.cycles.use_denoising = True
sc.view_settings.view_transform = "Standard"
cam = bpy.data.objects.new("C", bpy.data.cameras.new("C")); sc.collection.objects.link(cam); sc.camera = cam
sc.render.resolution_x, sc.render.resolution_y = 600, 760
os.makedirs(os.path.join(HERE, "sheets"), exist_ok=True)
for k, ch, x, face in chars:
    sc.frame_set(1)
    h = (ch.rig.matrix_world @ ch.rig.pose.bones["head"].head)
    cam.location = (h.x, h.y - 1.55, h.z + 0.02); cam.data.lens = 50
    cam.rotation_euler = (math.radians(92), 0, 0)
    sc.render.filepath = os.path.join(HERE, "sheets", f"p_{k}.png")
    bpy.ops.render.render(write_still=True)
