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

MODE = sys.argv[-1] if sys.argv[-1] in ("layout", "preview", "final", "side") else "layout"
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

def _mesh_min_z(objs):
    dg = bpy.context.evaluated_depsgraph_get(); z = 1e9
    for o in objs:
        if o.type != "MESH":
            continue
        ev = o.evaluated_get(dg); me = ev.to_mesh()
        for v in me.vertices:
            z = min(z, (o.matrix_world @ v.co).z)
        ev.to_mesh_clear()
    return z

# rest the bus on the road (its lowest point on z = 0)
bus.location.z -= _mesh_min_z(bus.children_recursive)
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
ARIN_POS = (1.0, edge_y + 0.5, 0.0)
lay = mocap.load(os.path.join(MOCAP, "laying_breathless.fbx"))
mocap.apply(arin, lay, start=1, length=1080, offset=ARIN_POS, facing=90, loop=True, in_place=True)
# lying on the ground: lower the whole body until its lowest point (clothes or skin) touches the road
sc.frame_set(1)
low = _mesh_min_z([arin.body] + arin.parts.get("Clothes", []))
arin.rig.location.z -= low
for f in range(1, 1081, 24):
    arin.rig.keyframe_insert("location", index=2, frame=f)
print("ARIN lowered by", round(low, 3))

# ---- the phone, face down in a puddle within arm's reach of his head
tex = os.path.join(HERE, "tex")
ph = phone.build(os.path.join(tex, "lock_nika.png"))
sc.frame_set(1)
_hd = arin.rig.matrix_world @ arin.rig.pose.bones["head"].head
PHONE_POS = (_hd.x + 0.1, edge_y - 0.15, 0.0)
print("HEAD", tuple(round(v, 2) for v in _hd), "PHONE", tuple(round(v, 2) for v in PHONE_POS))
ph.location = PHONE_POS
ph.rotation_euler = (math.pi, 0, math.radians(20))        # face down
ph.location.z = 0.009

# ---- the shambler (Z1): drags down the road, stops ~3 m from Arin (f700–820), sniffs, then moves on round the bus end
z1 = zc_cast.spawn("zc_z1_office")
walk = mocap.load(os.path.join(MOCAP, "zombie_walk.fbx"))
idle = mocap.load(os.path.join(MOCAP, "zombie_idle.fbx"))
ZX, ZSTOP = 3.6, 4.0
V = 0.035                                    # m/frame ≈ 0.84 m/s: a dragging shambler
Y0 = ZSTOP - V * 699
mocap.apply(z1, walk, start=1, length=699, in_place=True, loop=True, place=lambda j: ((ZX, Y0 + V * j, 0), 0.0))
mocap.apply(z1, idle, start=700, length=120, offset=(ZX, ZSTOP, 0), facing=-25, in_place=True, loop=True, blend=8)
mocap.apply(z1, walk, start=820, length=261, in_place=True, loop=True, blend=8,
            place=lambda j: ((ZX + V * j * 0.9, ZSTOP + V * j * 0.45, 0), -63.0))
Q.ground(z1, 1, 1080)
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
sc.frame_set(456)
head = arin.rig.matrix_world @ arin.rig.pose.bones["head"].head
eyes = arin.parts["Eyes"][0]
dg = bpy.context.evaluated_depsgraph_get()
_e = eyes.evaluated_get(dg).to_mesh()
eyec = sum((eyes.matrix_world @ v.co for v in _e.vertices), Vector()) / len(_e.vertices)
eyes.evaluated_get(dg).to_mesh_clear()
fwd = (eyec - head).normalized()                      # where his face points (lying on his back: mostly up)
side = fwd.cross(Vector((0, 0, 1))).normalized() if abs(fwd.z) < 0.95 else Vector((1, 0, 0))
print("FACE fwd", tuple(round(v, 2) for v in fwd))
zfeet = Vector((ZX, ZSTOP, 0.15))
c1 = cam("CAM_S01_ECU_phone", pv + Vector((0.08, 0.5, 0.1)), pv + Vector((0, -1.0, 0.05)), 50, 1, (0.5, 1.4))
c2 = cam("CAM_S02_wide", (1.2, -16.0, 0.32), (0.4, edge_y + 0.8, 1.2), 24, 145)
c3 = cam("CAM_S03_insert", pv + Vector((0.5, -0.5, 0.22)), pv + Vector((-0.15, 0.3, 0.03)), 50, 289)
c4 = cam("CAM_S04_CU", eyec + fwd * 0.45 + Vector((0, -0.35, 0)), eyec, 35, 409)
c5 = cam("CAM_S05_track", head + Vector((0.05, -0.35, -0.3)), zfeet, 35, 505)
c6 = cam("CAM_S06_POV", eyec + fwd * 0.03, eyec + fwd * 0.4, 28, 889)
c7 = cam("CAM_S07_CU", eyec + fwd * 0.35 + Vector((0, -0.25, 0)), eyec, 50, 1009)
# shots 6–7: the phone is held above his face (hand IK comes in the animation pass)
ph.keyframe_insert("location", frame=888); ph.keyframe_insert("rotation_euler", frame=888)
ph.location = eyec + fwd * 0.32
ph.rotation_euler = (fwd.to_track_quat("Z", "Y").to_euler())
ph.keyframe_insert("location", frame=889); ph.keyframe_insert("rotation_euler", frame=889)
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

if MODE == "side":       # orthographic cross-section: is Arin really in the gap under the bus, on the ground?
    sc.timeline_markers.clear(); sc.frame_set(456)
    cd = bpy.data.cameras.new("dbg"); cd.type = "ORTHO"; cd.ortho_scale = 5
    c = bpy.data.objects.new("dbg", cd); sc.collection.objects.link(c); sc.camera = c
    c.location = (ARIN_POS[0] + 9, ARIN_POS[1], 1.0); c.rotation_euler = (math.radians(90), 0, math.radians(90))
    s = bpy.data.lights.new("s", "SUN"); s.energy = 5; so = bpy.data.objects.new("s", s)
    so.rotation_euler = (math.radians(60), 0, math.radians(60)); sc.collection.objects.link(so)
    for o in bpy.data.objects:
        if o.name.startswith("ENV_Building") or o.name.startswith("FX_"):
            o.hide_render = True
    sc.render.resolution_x = sc.render.resolution_y = 480; sc.eevee.taa_render_samples = 4
    sc.render.filepath = os.path.join(OUT, "side_check.png"); bpy.ops.render.render(write_still=True)
