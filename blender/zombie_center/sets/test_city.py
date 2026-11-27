"""Look test for ENV_CITY_STREET: 3 cameras from EP01, 1280x720 EEVEE.
    blender/cast/bpy.sh blender/zombie_center/sets/test_city.py
"""
import bpy, sys, os, math, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.dirname(HERE))
import env_city
from mathutils import Vector

sc = bpy.context.scene
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)
t0 = time.time()
S = env_city.build()
if "nofog" in sys.argv:
    bpy.data.objects["FX_GroundFog"].hide_render = True
print("OBJS_NEAR_CAM_B", [o.name for o in bpy.data.objects if o.type == "MESH" and (o.matrix_world.translation - Vector((2, 4, 1))).length < 4][:20])
print("BUILD s", round(time.time() - t0, 1), "objects", len(bpy.data.objects))
sc.render.engine = "BLENDER_EEVEE"; sc.eevee.taa_render_samples = 16
sc.render.resolution_x, sc.render.resolution_y = 1280, 720
sc.view_settings.view_transform = "AgX"; sc.view_settings.look = "AgX - Medium High Contrast"; sc.view_settings.exposure = 2.0
try:
    sc.eevee.use_volumetric_shadows = True; sc.eevee.volumetric_tile_size = "4"
except Exception:
    pass
cd = bpy.data.cameras.new("cam"); cam = bpy.data.objects.new("cam", cd); sc.collection.objects.link(cam); sc.camera = cam
OUT = os.path.join(os.path.dirname(HERE), "test"); os.makedirs(OUT, exist_ok=True)
shots = {
    "A_wide_low": ((1.0, -16.0, 0.35), (0.5, 10.0, 1.0), 24),      # SC001 shot 2: low push along the avenue to the bus
    "B_bus": ((4.5, 0.5, 1.2), (0.0, 7.0, 1.0), 35),               # bus side, Arin's hiding place
    "C_sidestreet": ((4.0, 19.0, 1.6), (20.0, 23.0, 1.0), 28),     # side street B
    "D_top": ((0.5, 7.0, 30.0), (0.5, 7.01, 0.0), 30),              # check: bus placement from above
}
for tag, (loc, tgt, lens) in [(k, v) for k, v in shots.items() if ("nofog" not in sys.argv or k == "B_bus")]:
    cam.location = loc; cd.lens = lens
    cam.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    sc.render.filepath = os.path.join(OUT, f"city_{tag}.png")
    t = time.time(); bpy.ops.render.render(write_still=True); print("RENDER", tag, round(time.time() - t, 1))
