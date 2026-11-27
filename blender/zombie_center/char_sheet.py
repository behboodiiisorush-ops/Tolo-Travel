"""Reference sheet for one ZC character: front / side / back full body + face close-up (EEVEE).

    blender/cast/bpy.sh blender/zombie_center/char_sheet.py zc_arin
Writes 01_CHARACTERS/sheets/<key>_sheet.png and reports measured height.
"""
import bpy, sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import zc_cast
from PIL import Image, ImageDraw, ImageFont

key = sys.argv[-1]
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "01_CHARACTERS", "sheets"); os.makedirs(OUT, exist_ok=True)
sc = bpy.context.scene
for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)
ch = zc_cast.spawn(key)
bpy.context.view_layer.update()
import mpfb_tools as M
_pts, _ = M.rest_positions(ch.body)
H = max(p.z for p in _pts) - min(p.z for p in _pts)

w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.32, 0.33, 0.35, 1)
w.node_tree.nodes["Background"].inputs[1].default_value = 0.6
def area(n, loc, e, s):
    d = bpy.data.lights.new(n, "AREA"); d.energy = e; d.size = s
    o = bpy.data.objects.new(n, d); o.location = loc; sc.collection.objects.link(o)
    c = o.constraints.new("TRACK_TO"); c.target = ch.rig; return o
area("key", (2.0, -3.0, 2.6), 300, 2.0); area("fill", (-2.5, -2.0, 1.6), 100, 3.0); area("rim", (0.5, 3.0, 2.4), 220, 1.5)
bpy.ops.mesh.primitive_plane_add(size=30); fl = bpy.context.object
m = bpy.data.materials.new("fl"); m.use_nodes = True
m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.25, 0.25, 0.26, 1); fl.data.materials.append(m)

cd = bpy.data.cameras.new("c"); cam = bpy.data.objects.new("c", cd); sc.collection.objects.link(cam); sc.camera = cam
sc.render.engine = "BLENDER_EEVEE"; sc.eevee.taa_render_samples = 32
sc.view_settings.view_transform = "AgX"
shots = []
def shot(tag, yaw, dist, z, lens, aim_z, rx, ry):
    sc.render.resolution_x, sc.render.resolution_y = rx, ry
    cd.lens = lens
    a = math.radians(yaw)
    cam.location = (math.sin(a) * dist, -math.cos(a) * dist, z)
    d = (0 - cam.location.x, 0 - cam.location.y, aim_z - z)
    cam.rotation_euler = (math.atan2(math.hypot(d[0], d[1]), -d[2]), 0, math.atan2(d[0], -d[1]) * -1 + 0)
    import mathutils
    cam.rotation_euler = mathutils.Vector(d).to_track_quat("-Z", "Y").to_euler()
    p = os.path.join(OUT, f"_{key}_{tag}.png"); sc.render.filepath = p
    bpy.ops.render.render(write_still=True); shots.append(p)
shot("front", 0, 4.6, 1.0, 50, H * 0.52, 480, 860)
shot("side", 90, 4.6, 1.0, 50, H * 0.52, 480, 860)
shot("back", 180, 4.6, 1.0, 50, H * 0.52, 480, 860)
shot("face", 12, 0.75, H - 0.1, 85, H - 0.12, 600, 860)

ims = [Image.open(p).convert("RGB") for p in shots]
sheet = Image.new("RGB", (480 * 3 + 600, 860 + 70), (20, 20, 22))
x = 0
for im in ims:
    sheet.paste(im, (x, 70)); x += im.width
font = ImageFont.truetype(os.path.join(HERE, "..", "fonts", "Vazirmatn-FD-ExtraBold.ttf"), 30)
d = ImageDraw.Draw(sheet)
d.text((16, 16), f"{key}  ·  height {H:.2f} m  ·  front / side / back / face", fill=(230, 230, 230), font=font)
sheet.save(os.path.join(OUT, f"{key}_sheet.png"))
for p in shots: os.remove(p)
print("SHEET", key, f"{H:.3f}")
