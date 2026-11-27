"""Motion test 1 — Arin walks 4 s (in-place Mixamo cycle moved at the clip's own stride speed),
then the QC measures foot slide / sinking frame by frame. Optional preview render.

    blender/cast/bpy.sh blender/zombie_center/tests/motion_walk_run.py [walk|run] [render]
"""
import bpy, sys, os, math, json
HERE = os.path.dirname(os.path.abspath(__file__))
ZC = os.path.dirname(HERE)
sys.path.insert(0, ZC)
import zc_cast, mocap, motion_qc as Q, footlock

mode = "walk" if "run" not in sys.argv else "run"
do_render = "render" in sys.argv
OUT = os.path.join(ZC, "test"); os.makedirs(OUT, exist_ok=True)
sc = bpy.context.scene
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)
sc.render.fps = 24
ch = zc_cast.spawn("zc_arin")
MOCAP = os.path.join(ZC, "..", "mocap")
N = 96

if mode == "walk":
    clip = mocap.load(os.path.join(MOCAP, "walking.fbx"))
    # 1) measure the clip's stride speed: play in place, track the planted foot's backward speed
    mocap.apply(ch, clip, start=1, length=48, offset=(0, 0, 0), facing=0, in_place=True, loop=True)
    probe = Q.feet(ch, 1, 48)
    vs = []
    for a, b in zip(probe["rows"], probe["rows"][1:]):
        for s in ("l", "r"):
            if a.get(s, {}).get("planted") and b.get(s, {}).get("planted") and b[s]["slide_cm"] is not None:
                vs.append(b[s]["slide_cm"])
    v = (sorted(vs)[len(vs) // 2] / 100.0) if vs else 0.05          # m per frame (median)
    print("STRIDE_SPEED m/frame", round(v, 4), "=", round(v * 24, 2), "m/s")
    ch.rig.animation_data_clear()
    for pb in ch.rig.pose.bones:
        pb.matrix_basis.identity()
    mocap.LAST.clear()
    # 2) the real take: same cycle, moved forward at exactly that speed
    mocap.apply(ch, clip, start=1, length=N, in_place=True, loop=True,
                place=lambda j: ((0, v * j, 0), 0.0))
else:
    clip = mocap.load(os.path.join(MOCAP, "jog_in_circle.fbx"))
    mocap.apply(ch, clip, start=1, length=N, offset=(0, 0, 0), facing=0, in_place=False)

lift = Q.ground(ch, 1, N)
print("LIFT_CM min/max", min(lift), max(lift))
pre = Q.feet(ch, 1, N)["summary"]
print("QC_BEFORE_LOCK", json.dumps({k: pre[k] for k in ("slide_max_cm", "slide_mean_cm", "sink_max_cm")}))
footlock.lock(ch, 1, N)
Q.ground(ch, 1, N)
rep = Q.feet(ch, 1, N)
summ = Q.write(rep, os.path.join(OUT, f"qc_{mode}.json"))
print("QC", json.dumps(summ))

if do_render:
    import mathutils
    if getattr(ch, "hair_strands", None):
        pass
    sc.render.engine = "BLENDER_EEVEE"; sc.eevee.taa_render_samples = 8
    sc.render.resolution_x, sc.render.resolution_y = 640, 360
    w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
    w.node_tree.nodes["Background"].inputs[0].default_value = (0.4, 0.42, 0.45, 1)
    bpy.ops.mesh.primitive_plane_add(size=60); fl = bpy.context.object
    m = bpy.data.materials.new("fl"); m.use_nodes = True
    bsdf = m.node_tree.nodes["Principled BSDF"]
    chk = m.node_tree.nodes.new("ShaderNodeTexChecker"); chk.inputs["Scale"].default_value = 60
    chk.inputs["Color1"].default_value = (0.35, 0.35, 0.36, 1); chk.inputs["Color2"].default_value = (0.25, 0.25, 0.26, 1)
    m.node_tree.links.new(chk.outputs[0], bsdf.inputs["Base Color"]); fl.data.materials.append(m)
    l = bpy.data.lights.new("sun", "SUN"); l.energy = 3; so = bpy.data.objects.new("sun", l)
    so.rotation_euler = (math.radians(50), 0, math.radians(30)); sc.collection.objects.link(so)
    cd = bpy.data.cameras.new("c"); cd.lens = 35; cam = bpy.data.objects.new("c", cd)
    sc.collection.objects.link(cam); sc.camera = cam
    # side-on tracking camera at hip height (shows feet/ground contact clearly)
    for f in range(1, N + 1):
        sc.frame_set(f)
        hip = ch.rig.matrix_world @ ch.rig.pose.bones["pelvis"].head
        cam.location = (4.2, hip.y, 0.75)
        cam.rotation_euler = (math.radians(90), 0, math.radians(90))
        cam.keyframe_insert("location", frame=f); cam.keyframe_insert("rotation_euler", frame=f)
    sc.frame_start, sc.frame_end = 1, N
    sc.render.filepath = os.path.join(OUT, f"prev_{mode}_")
    sc.render.image_settings.file_format = "PNG"
    bpy.ops.render.render(animation=True)
