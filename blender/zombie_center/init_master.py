"""PHASE 4 — create THE_ZOMBIE_CENTER_MASTER.blend (project structure + test scene) and render one test frame.

    blender/cast/bpy.sh blender/zombie_center/init_master.py

Writes:
  blend/THE_ZOMBIE_CENTER_MASTER.blend        (current master)
  blend/versions/THE_ZOMBIE_CENTER_MASTER_v001.blend   (preserved version)
  test/phase4_test_frame.png
Never overwrites an existing version file.
"""
import bpy, os, sys, math, json, time
import mpfb_tools as M

HERE = os.path.dirname(os.path.abspath(__file__))
BLEND = os.path.join(HERE, "blend")
os.makedirs(os.path.join(BLEND, "versions"), exist_ok=True)
os.makedirs(os.path.join(HERE, "test"), exist_ok=True)

COLLECTIONS = ["00_MASTER", "01_CHARACTERS", "02_ZOMBIES", "03_ENVIRONMENTS", "04_PROPS", "05_LIGHTS",
               "06_CAMERAS", "07_FX", "08_AUDIO", "09_REFERENCE", "10_RENDER"]
SETTINGS = dict(title="THE ZOMBIE CENTER — PATIENT ZERO", company="AGETOBUDI", res=[1920, 1080], fps=24,
                aspect="16:9", engine="CYCLES", units="METRIC, 1 BU = 1 m", runtime="60:00 (86,400 frames)",
                chapters="8 x 7:30 (10,800 frames each)", view_transform="AgX", color="sRGB")

# ---- 1. inspect + clean the default scene -------------------------------------------------------
sc = bpy.context.scene
print("INSPECT before:", [o.name for o in bpy.data.objects])
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)
for c in list(bpy.data.collections):
    bpy.data.collections.remove(c)
sc.name = "ZC_TEST"

# ---- 2. collections ----------------------------------------------------------------------------
col = {}
for n in COLLECTIONS:
    c = bpy.data.collections.new(n)
    sc.collection.children.link(c)
    col[n] = c


def put(o, cname):
    for c in list(o.users_collection):
        c.objects.unlink(o)
    col[cname].objects.link(o)
    return o


# ---- 3. project parameters ---------------------------------------------------------------------
r = sc.render
r.resolution_x, r.resolution_y, r.resolution_percentage = 1920, 1080, 100
r.pixel_aspect_x = r.pixel_aspect_y = 1.0
r.fps, r.fps_base = 24, 1.0
r.engine = "CYCLES"
sc.cycles.device = "CPU"
sc.cycles.samples = 64
sc.cycles.use_denoising = True
sc.cycles.max_bounces = 8
sc.view_settings.view_transform = "AgX"
sc.unit_settings.system = "METRIC"
sc.unit_settings.scale_length = 1.0
sc.frame_start, sc.frame_end = 1, 48
r.image_settings.file_format = "PNG"

# ---- 4. test scene -----------------------------------------------------------------------------
def mat(name, rgb, rough=0.5, metal=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*rgb, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    return m


bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, 0))
g = put(bpy.context.object, "09_REFERENCE"); g.name = "REF_GroundPlane"
g.data.materials.append(mat("MAT_REF_Ground", (0.18, 0.18, 0.18), 0.8))

bpy.ops.mesh.primitive_uv_sphere_add(radius=0.25, segments=64, ring_count=32, location=(-0.9, 0.2, 0.25))
s = put(bpy.context.object, "09_REFERENCE"); s.name = "REF_NeutralSphere"
bpy.ops.object.shade_smooth()
s.data.materials.append(mat("MAT_REF_Neutral18", (0.18, 0.18, 0.18), 0.45))

# measurement reference: 2 m ruler with 10 cm ticks + labels every 50 cm
ruler_m = mat("MAT_REF_Ruler", (0.9, 0.75, 0.1), 0.4)
tick_m = mat("MAT_REF_Tick", (0.02, 0.02, 0.02), 0.6)
bpy.ops.mesh.primitive_cube_add(size=1, location=(0.9, 0.2, 1.0))
rl = put(bpy.context.object, "09_REFERENCE"); rl.name = "REF_Ruler_2m"
rl.scale = (0.04, 0.02, 2.0); rl.data.materials.append(ruler_m)
for i in range(21):
    z = i * 0.1
    w = 0.12 if i % 5 == 0 else 0.07
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0.9 - 0.02 - w / 2, 0.2, z))
    t = put(bpy.context.object, "09_REFERENCE"); t.name = f"REF_Ruler_tick_{i * 10:03d}cm"
    t.scale = (w, 0.022, 0.008); t.data.materials.append(tick_m)
    if i % 5 == 0:
        bpy.ops.object.text_add(location=(0.96, 0.18, z - 0.03))
        tx = put(bpy.context.object, "09_REFERENCE"); tx.name = f"REF_Ruler_label_{i * 10:03d}cm"
        tx.data.body = f"{z:.1f} m"; tx.data.size = 0.07
        tx.rotation_euler = (math.radians(90), 0, 0); tx.data.materials.append(tick_m)

# human scale reference: MPFB human, measured
before = set(bpy.data.objects)
body, rig, parts = M.build_human("REF_Human", gender=1.0, age=0.5, height=0.5, skin="young_caucasian_male",
                                 skin_type="MAKESKIN", hair="short02",
                                 clothes=["toigo_basic_tucked_t-shirt", "punkduck_male_classic_jeans", "shoes01"],
                                 subdiv=0)
for o in set(bpy.data.objects) - before:
    put(o, "09_REFERENCE")
bpy.context.view_layer.update()
zs = [(body.matrix_world @ v.co).z for v in body.data.vertices]
human_h = max(zs) - min(zs)
rig.location = (0, 0.2, 0)
print(f"REF_Human height = {human_h:.3f} m")

# three-point lighting
def area(name, loc, rot, energy, size, rgb):
    d = bpy.data.lights.new(name, "AREA"); d.energy = energy; d.size = size; d.color = rgb
    o = bpy.data.objects.new(name, d); o.location = loc; o.rotation_euler = [math.radians(a) for a in rot]
    col["05_LIGHTS"].objects.link(o); return o

area("LGT_Key", (2.6, -2.6, 2.8), (55, 0, 45), 600, 1.2, (1.0, 0.93, 0.85))
area("LGT_Fill", (-3.0, -2.2, 1.8), (70, 0, -55), 150, 2.5, (0.8, 0.88, 1.0))
area("LGT_Rim", (-0.5, 3.2, 2.6), (-60, 0, 180), 500, 1.0, (0.85, 0.9, 1.0))
w = bpy.data.worlds.new("WORLD_ZC_Test"); sc.world = w; w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.02, 0.022, 0.026, 1)

camd = bpy.data.cameras.new("CAM_Test"); camd.lens = 40; camd.sensor_width = 36
cam = bpy.data.objects.new("CAM_Test", camd); col["06_CAMERAS"].objects.link(cam)
cam.location = (0, -5.2, 1.25); cam.rotation_euler = (math.radians(88), 0, 0)
sc.camera = cam

# project info: text object + JSON + custom props on the scene
info = dict(SETTINGS, created=time.strftime("%Y-%m-%d"), collections=COLLECTIONS,
            ref_human_height_m=round(human_h, 3), docs="blender/zombie_center/docs/")
bpy.ops.object.text_add(location=(-2.6, 0.6, 2.2))
it = put(bpy.context.object, "00_MASTER"); it.name = "INFO_ProjectSettings"
it.data.body = "\n".join(f"{k}: {v}" for k, v in SETTINGS.items())
it.data.size = 0.09; it.rotation_euler = (math.radians(90), 0, 0)
it.data.materials.append(mat("MAT_INFO_Text", (0.9, 0.9, 0.9), 0.5))
it.hide_render = True
tb = bpy.data.texts.new("PROJECT_INFO.json"); tb.write(json.dumps(info, ensure_ascii=False, indent=2))
sc["zc_project"] = json.dumps(info, ensure_ascii=False)
with open(os.path.join(HERE, "docs", "PROJECT_SETTINGS.json"), "w") as f:
    json.dump(info, f, ensure_ascii=False, indent=2)

# ---- 5. save (version first, never overwrite a version) ----------------------------------------
v = 1
while os.path.exists(os.path.join(BLEND, "versions", f"THE_ZOMBIE_CENTER_MASTER_v{v:03d}.blend")):
    v += 1
vpath = os.path.join(BLEND, "versions", f"THE_ZOMBIE_CENTER_MASTER_v{v:03d}.blend")
mpath = os.path.join(BLEND, "THE_ZOMBIE_CENTER_MASTER.blend")
bpy.ops.wm.save_as_mainfile(filepath=vpath, copy=True)
bpy.ops.wm.save_as_mainfile(filepath=mpath)

# ---- 6. render one test frame -------------------------------------------------------------------
sc.frame_set(1)
r.filepath = os.path.join(HERE, "test", "phase4_test_frame.png")
t0 = time.time()
bpy.ops.render.render(write_still=True)
dt = time.time() - t0

# ---- 7. inspect -------------------------------------------------------------------------------
report = dict(version_file=vpath, master_file=mpath, render=r.filepath, render_seconds=round(dt, 1),
              engine=r.engine, res=(r.resolution_x, r.resolution_y), fps=r.fps,
              collections={c.name: len(c.objects) for c in col.values()},
              camera=sc.camera.name, human_height=round(human_h, 3),
              files_exist=[os.path.exists(p) for p in (vpath, mpath, r.filepath)])
print("REPORT", json.dumps(report, ensure_ascii=False))
