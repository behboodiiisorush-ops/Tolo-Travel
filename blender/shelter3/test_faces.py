"""Face check for «پناهگاه ۳»: ../cast/bpy.sh test_faces.py me,mom,lena -> test/face_<key>.png (comic look)."""
import bpy, sys, os
from mathutils import Vector
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "studio"))
sys.path.insert(0, os.path.join(HERE, "..", "cast"))
bpy.ops.wm.read_factory_settings(use_empty=True)
import cast, anim  # noqa
sys.path.insert(0, HERE)
import look as LK  # noqa
import toon_look as T  # noqa
import props as P  # noqa
sys.path.insert(0, HERE)
import look as LK  # noqa
cast.STYLE = LK.STYLE
keys = sys.argv[-1].split(",")
sc = bpy.context.scene
chs = []
for i, k in enumerate(keys):
    if ":" in k:
        base, hair = k.split(":")
        cast.CAST[k] = dict(cast.CAST[base], hair=hair)
        LK.SKIN[k], LK.IRIS[k] = LK.SKIN[base], LK.IRIS[base]
        if base in LK.LIPS: LK.LIPS[k] = LK.LIPS[base]
        if base in LK.CLOTHES: LK.CLOTHES[k] = LK.CLOTHES[base]
    ch = cast.spawn(k)
    T.register(ch, k, realistic=True)
    LK.before(ch, k)
    ch.animate(1, 0.0, (i * 1.2, 0, 0), 180, worry=float(os.environ.get("WORRY", "0")), smile=float(os.environ.get("SMILE", "0")))
    ch.flush()
    chs.append((k, ch))
P.box((0, 3, 1.5), (30, 0.1, 6), P.mat("Back", (0.55, 0.5, 0.45), 0.9), "Backdrop")
P.area_light((3, -3, 3.2), (2, 0, 1.4), 900, 2.0)
P.area_light((-3, -1, 2.5), (0, 0, 1.4), 200, 3.0)
sc.world = bpy.data.worlds.new("W")
sc.world.color = (0.4, 0.4, 0.42)
sc.frame_set(1)
T.toonify(sc, samples=int(os.environ.get('SAMPLES', '8')))
LK.after()
T.ink([o for o in bpy.data.objects if o.type == "MESH" and not any(x in o.name.lower() for x in ("lash", "brow", "teeth", "tongue", "backdrop", "high-poly"))], 0.004)
cam = bpy.data.objects.new("Cam", bpy.data.cameras.new("Cam"))
sc.collection.objects.link(cam)
sc.camera = cam
cam.data.lens = 85
sc.render.resolution_x, sc.render.resolution_y = 500, 620
for k, ch in chs:
    h = ch.head_world() + Vector((0, 0, 0.09))
    cam.location = h + Vector((0.12, -1.05, 0.02))
    cam.rotation_euler = (h - cam.location).to_track_quat("-Z", "Y").to_euler()
    sc.render.filepath = os.path.join(HERE, "test", f"face_{k.replace(':', '_')}.png")
    bpy.ops.render.render(write_still=True)
    p = ch.bone("pelvis")
    cam.data.lens = 35
    cam.location = p + Vector((0.3, -3.3, 0.1))
    cam.rotation_euler = (p + Vector((0, 0, 0.0)) - cam.location).to_track_quat("-Z", "Y").to_euler()
    sc.render.filepath = os.path.join(HERE, "test", f"full_{k.replace(':', '_')}.png")
    bpy.ops.render.render(write_still=True)
    cam.data.lens = 85
