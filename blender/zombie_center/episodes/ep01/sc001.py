"""EP01 · CH01_SC001 — EXT. ABANDONED CITY AVENUE — NIGHT · 22:40 · 45 s (frames 1–1080)

    blender/cast/bpy.sh blender/zombie_center/episodes/ep01/sc001.py layout     # one still per shot (layout check)
    blender/cast/bpy.sh blender/zombie_center/episodes/ep01/sc001.py preview    # low-res animated preview

Shots (screenplay v1.0):
 1  1–144    ECU 100 mm phone face-down in a puddle, buzzing; rack focus to the swaying figure far down the road
 2  145–288  wide 24 mm road level, slow push along the avenue to the fallen bus
 3  289–408  insert 50 mm: a hand slides out from under the bus and pulls the phone in
 4  409–504  CU 35 mm under the bus: Arin, hand clamped over his mouth
 5  505–888  low tracking 35 mm: the shambler's dragging feet pass 3 m away, stop, she sniffs, moves on
 6  889–1008 POV 28 mm: he turns the phone over — lock screen «نیکا — ۱ ویدیوی جدید»
 7  1009–1080 CU 50 mm: his face lit blue by the screen; whisper «نیکا؟...»
"""
import bpy, sys, os, math
HERE = os.path.dirname(os.path.abspath(__file__))
ZC = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path[:0] = [ZC, os.path.join(ZC, "sets")]
import env_city, phone, zc_cast, mocap, motion_qc as Q, footlock
from mathutils import Vector, Euler

MODE = sys.argv[-1] if sys.argv[-1] in ("layout", "preview", "final") else "layout"
MOCAP = os.path.join(ZC, "..", "mocap")
FPS = 24
SHOTS = [(1, 144), (145, 288), (289, 408), (409, 504), (505, 888), (889, 1008), (1009, 1080)]

sc = bpy.context.scene
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)
sc.render.fps = FPS
sc.frame_start, sc.frame_end = 1, 1080
S = env_city.build()
bus = S["bus"]
bpy.context.view_layer.update()

# ---- where is the raised edge of the bus? (lowest -Y face of the bus, measured)
pts = []
for o in bus.children_recursive:
    if o.type == "MESH":
        for c in o.bound_box:
            pts.append(o.matrix_world @ Vector(c))
edge_y = min(p.y for p in pts)
print("BUS edge_y", round(edge_y, 2), "x range", round(min(p.x for p in pts), 2), round(max(p.x for p in pts), 2))

# ---- Arin: on his back in the gap under the raised edge, head towards the avenue (-Y)
arin = zc_cast.spawn("zc_arin")
ARIN_POS = (1.0, edge_y + 1.05, 0.0)
lay = mocap.load(os.path.join(MOCAP, "laying_breathless.fbx"))
mocap.apply(arin, lay, start=1, length=1080, offset=ARIN_POS, facing=180, loop=True, in_place=True)

# ---- the phone, face down in a puddle within arm's reach of his head
tex = os.path.join(HERE, "tex")
ph = phone.build(os.path.join(tex, "lock_nika.png"))
PHONE_POS = (ARIN_POS[0] + 0.55, edge_y - 0.35, 0.0)
ph.location = PHONE_POS
ph.rotation_euler = (math.pi, 0, math.radians(20))        # face down
ph.location.z = 0.009

# ---- the shambler (Z1): comes down the road, stops 3 m from Arin, sniffs, moves on
z1 = zc_cast.spawn("zc_z1_office")
walk = mocap.load(os.path.join(MOCAP, "zombie_walk.fbx"))
mocap.apply(z1, walk, start=1, length=1080, offset=(3.6, -26.0, 0), facing=0, loop=True, in_place=True,
            place=lambda j: ((3.6, -26.0 + min(j, 760) * 0.035, 0), 0.0))

# ---- cameras (one per shot), bound to markers
def cam(name, loc, tgt, lens, f0, dof=None):
    cd = bpy.data.cameras.new(name); cd.lens = lens; cd.sensor_width = 36
    c = bpy.data.objects.new(name, cd); sc.collection.objects.link(c)
    c.location = loc
    c.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    if dof:
        cd.dof.use_dof = True; cd.dof.focus_distance = dof[0]; cd.dof.aperture_fstop = dof[1]
    m = sc.timeline_markers.new(name, frame=f0); m.camera = c
    return c

pv = Vector(PHONE_POS)
c1 = cam("CAM_S01_ECU_phone", pv + Vector((0.05, -0.32, 0.05)), pv + Vector((0, 0, 0.0)), 100, 1, (0.33, 2.0))
c2 = cam("CAM_S02_wide", (1.2, -16.0, 0.32), (0.8, edge_y + 2, 0.9), 24, 145)
c3 = cam("CAM_S03_insert", pv + Vector((0.6, -0.55, 0.25)), pv + Vector((-0.2, 0.25, 0.02)), 50, 289)
head = arin.rig.matrix_world @ arin.rig.pose.bones["head"].head
c4 = cam("CAM_S04_CU", Vector((head.x + 0.45, edge_y - 0.6, 0.18)), head, 35, 409)
c5 = cam("CAM_S05_track", Vector((ARIN_POS[0] + 0.3, edge_y - 0.2, 0.12)), Vector((3.6, edge_y - 1.0, 0.3)), 35, 505)
c6 = cam("CAM_S06_POV", head + Vector((0, -0.05, 0.08)), pv, 28, 889)
c7 = cam("CAM_S07_CU", head + Vector((0.35, -0.5, 0.12)), head, 50, 1009)

# ---- render settings
sc.render.engine = "BLENDER_EEVEE"
sc.view_settings.view_transform = "AgX"; sc.view_settings.look = "AgX - Base Contrast"; sc.view_settings.exposure = 2.0
try:
    sc.eevee.use_raytracing = True
except Exception:
    pass
OUT = os.path.join(HERE, "out", "sc001"); os.makedirs(OUT, exist_ok=True)
if MODE == "layout":
    sc.eevee.taa_render_samples = 8
    sc.render.resolution_x, sc.render.resolution_y = 640, 360
    for i, (a, b) in enumerate(SHOTS):
        f = (a + b) // 2
        sc.frame_set(f)
        sc.render.filepath = os.path.join(OUT, f"layout_s{i + 1:02d}_f{f:04d}.png")
        bpy.ops.render.render(write_still=True)
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "CH01_SC001_layout.blend"))
