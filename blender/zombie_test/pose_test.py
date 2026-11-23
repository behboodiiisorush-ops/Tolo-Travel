import bpy, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
bpy.ops.wm.read_factory_settings(use_empty=True)
import chars as C
from mathutils import Vector
out = sys.argv[-1]
ar, arig, ap = C.build("Arian", gender=1.0, age=0.4, height=0.6, skin="young_caucasian_male", hair="short02",
                       brow="eyebrow001", clothes=["elvs_crude_t-shirt_male", "cortu_cargo_pants", "shoes01"])
C.tint(ar, (0.93, 0.78, 0.64))
for o in ap.get("Hair", []) + ap.get("Eyebrows", []): C.tint(o, (0.12, 0.08, 0.06))
zb, zrig, zp = C.build("Zombie", gender=1.0, age=0.6, weight=0.3, muscle=0.35, skin="middleage_caucasian_male",
                       hair="long01", brow="eyebrow006", clothes=["male_worksuit01", "shoes03"])
C.zombie_skin(zb)
for o in zp.get("Hair", []): C.tint(o, (0.15, 0.13, 0.12))
for o in zp.get("Eyes", []): C.dead_eyes(o)
for o in zp.get("Clothes", []): C.dirty_cloth(o, (0.3, 0.28, 0.22))
zk = C.add_expr(zb, ["mouth-open", "mouth-retraction", "eyebrows-left-down", "eyebrows-right-down", "eye-left-opened-up", "eye-right-opened-up"])
for k, v in zk.items(): v.value = 0.9
arig.location.x = -0.6; zrig.location.x = 0.6
C.pose(arig, {"thigh_l": [(C.X, -30)], "upperarm_l": [(C.Y, 40)], "upperarm_r": [(C.Y, 40)], "head": [(C.Z, 40)]})
C.pose(zrig, {"upperarm_l": [(C.X, -70)], "upperarm_r": [(C.X, -60)], "spine_02": [(C.X, -15)], "head": [(C.Y, 15)]})
for o in bpy.data.objects:
    if o.type == "MESH": print("OBJ", o.name, o.parent and o.parent.name, [m.type for m in o.modifiers])
sc = bpy.context.scene
sc.render.engine = "CYCLES"; sc.cycles.samples = 32; sc.cycles.use_denoising = True
sc.render.resolution_x, sc.render.resolution_y = 960, 960
w = bpy.data.worlds.new("W"); sc.world = w
w.color = (0.5, 0.5, 0.55)
for loc, e in (((2, -3, 3), 500), ((-3, -2, 2), 200)):
    bpy.ops.object.light_add(type="AREA", location=loc); l = bpy.context.object; l.data.energy = e; l.data.size = 2
    l.rotation_euler = (Vector((0, 0, 1.2)) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
bpy.ops.mesh.primitive_plane_add(size=20)
cam = bpy.data.objects.new("Cam", bpy.data.cameras.new("Cam")); sc.collection.objects.link(cam); sc.camera = cam
for nm, loc, tg, lens in (("front", (0, -4.5, 1.0), (0, 0, 0.9), 40), ("side", (4.5, -0.5, 1.0), (0, 0, 0.9), 40),
                          ("zface", (0.75, -0.8, 1.6), (0.6, 0, 1.5), 60)):
    cam.location = loc; cam.data.lens = lens
    cam.rotation_euler = (Vector(tg) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    sc.render.filepath = f"{out}/{nm}.png"; bpy.ops.render.render(write_still=True)
