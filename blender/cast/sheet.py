"""Render reference sheets for the cast: sheets/<key>.png (full body + face).
    blender/cast/bpy.sh blender/cast/sheet.py [key ...]
"""
import bpy, sys, os, math
from mathutils import Vector
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
bpy.ops.wm.read_factory_settings(use_empty=True)
import cast

ALL = list(cast.CAST) + ["rezaei_z", "student0", "student1", "student2", "passerby0_z"]
keys = [a for a in sys.argv[1:] if not a.endswith(".py")] or ALL
OUT = os.path.join(HERE, "sheets")
os.makedirs(OUT, exist_ok=True)

sc = bpy.context.scene
sc.render.engine = "CYCLES"
sc.cycles.samples = 24
sc.cycles.use_denoising = True
sc.view_settings.view_transform = "AgX"
w = bpy.data.worlds.new("W"); sc.world = w; w.color = (0.04, 0.04, 0.045)
bpy.ops.mesh.primitive_plane_add(size=200)
floor = bpy.context.object
m = bpy.data.materials.new("Floor"); m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.25, 0.25, 0.27, 1)
floor.data.materials.append(m)
cam = bpy.data.objects.new("Cam", bpy.data.cameras.new("Cam")); sc.collection.objects.link(cam); sc.camera = cam


def light(loc, target, e, size=2.0):
    bpy.ops.object.light_add(type="AREA", location=loc)
    l = bpy.context.object; l.data.energy = e; l.data.size = size
    l.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()


chars = {}
for i, k in enumerate(keys):
    if k.startswith("student"):
        ch = cast.spawn_extra("student", int(k[7:]))
    elif k.startswith("passerby"):
        ch = cast.spawn_extra("passerby", int(k[8]), zombie=1.0)
    elif k == "rezaei_z":
        ch = cast.spawn("rezaei", zombie=1.0, name="RezaeiZ")
    elif k == "soldier":
        ch = cast.spawn("soldier", bite=("lowerarm_r", (0, -0.03, 0.0)))
    else:
        ch = cast.spawn(k)
    x = i * 4.0
    ch.animate(1, 0.0, (x, 0, 0), facing=180, arms="rest")
    ch.flush()
    chars[k] = (ch, x)
    light((x + 2.0, -3.0, 3.0), (x, 0, 1.2), 160)
    light((x - 3.0, -2.0, 2.0), (x, 0, 1.2), 55)
    light((x, 3.0, 3.0), (x, 0, 1.5), 90)
sc.frame_set(1)


def shot(path, loc, tgt, lens, res):
    sc.render.resolution_x, sc.render.resolution_y = res
    cam.location = loc; cam.data.lens = lens
    cam.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)


for k, (ch, x) in chars.items():
    h = ch.head_world() + Vector((0, -0.06, 0.07))
    shot(f"{OUT}/{k}_full.png", (x + 0.6, -4.2, 1.0), (x, 0, 0.88), 42, (480, 720))
    shot(f"{OUT}/{k}_face.png", (x + 0.25, h.y - 0.85, h.z + 0.02), tuple(h), 75, (480, 720))
    print("SHEET", k, round(ch.rig.dimensions.z, 2))
