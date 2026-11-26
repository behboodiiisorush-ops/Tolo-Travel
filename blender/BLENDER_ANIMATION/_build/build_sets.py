"""ENVIRONMENTS/Bedroom.blend, ENVIRONMENTS/Street.blend and the ASSETS library:
ASSETS/Props/Props.blend (every prop, marked as an asset), ASSETS/Materials/Toon_Materials.blend (the palette),
ASSETS/Effects/Effects.blend (rain, dust motes, comic impact star, speed lines)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib  # noqa: E402
import bpy, math  # noqa: E402

ONLY = sys.argv[sys.argv.index("--only") + 1].split(",") if "--only" in sys.argv else None


def want(k):
    return not ONLY or k in ONLY


# ------------------------------------------------------------------ environments
if want("bedroom"):
    sc = lib.reset()
    c = lib.coll("Bedroom")
    lib.bedroom(c)
    lib.look(sc, sky=(0.75, 0.88, 1.0), sun=2.2, sun_rot=(60, 0, 160))
    li = bpy.data.objects.new("Room light", bpy.data.lights.new("Room light", "AREA"))
    li.data.energy, li.data.size = 70, 2.5
    li.location = (0, 0, 2.6)
    c.objects.link(li)
    lib.camera(sc, (-0.2, -1.95, 1.55), (0.2, 1.2, 0.8), lens=16)
    lib.save("ENVIRONMENTS/Bedroom.blend", still=1)

if want("street"):
    sc = lib.reset()
    c = lib.coll("Street")
    lib.street(c)
    lib.look(sc, sky=(0.6, 0.8, 1.0), sun=3.2, sun_rot=(50, 0, -40))
    lib.camera(sc, (-4.0, -4.6, 1.7), (3.0, 4.5, 2.4), lens=20)
    lib.save("ENVIRONMENTS/Street.blend", still=1)

# ------------------------------------------------------------------ assets
if want("props"):
    sc = lib.reset()
    c = lib.coll("Props")
    makers = [lib.bed, lib.desk, lib.chair, lib.lamp, lib.shelf, lib.rug, lib.bench, lib.street_lamp,
              lambda cc, name: lib.tree(cc, name), lambda cc, name: lib.car(cc, name)]
    names = ["Bed", "Desk", "Chair", "Lamp", "Shelf", "Rug", "Bench", "Street lamp", "Tree", "Car"]
    x = 0.0
    for mk, nm in zip(makers, names):
        sub = lib.coll("Prop " + nm, c)
        r = mk(sub, nm)
        w = {"Car": 2.4, "Tree": 2.0, "Bench": 1.9, "Street lamp": 1.3}.get(nm, 1.6)
        lib.place(r, (x + w / 2, 0, 0))
        x += w + 0.3
        sub.asset_mark()
        sub.asset_data.description = f"Tolo Travel toon prop: {nm}"
        sub.asset_data.tags.new("tolo")
    lib.B(lib.root("Ground", lib.coll("Ground")), (x / 2, 0, -0.05), (x + 4, 8, 0.1), lib.M("walk"), "ground", line=0)
    lib.look(sc, res=(1600, 700))
    lib.camera(sc, (x / 2, -17.0, 3.2), (x / 2, 0, 1.1), lens=26)
    lib.save("ASSETS/Props/Props.blend", still=1)

if want("materials"):
    sc = lib.reset()
    c = lib.coll("Materials")
    r = lib.root("Swatches", c)
    keys = list(lib.PAL)
    cols = 8
    for i, k in enumerate(keys):
        m = lib.M(k)
        m.asset_mark()
        m.asset_data.description = f"toon colour '{k}' (Toon BSDF + a little emission, use with outlines)"
        lib.SP(r, ((i % cols) * 0.7, 0, -(i // cols) * 0.7), 0.28, m, k)
    lib.hull().use_fake_user = True
    lib.look(sc, res=(1400, 600), sky=(0.92, 0.92, 0.9))
    lib.camera(sc, ((cols - 1) * 0.35, -9.5, -1.05), ((cols - 1) * 0.35, 0, -1.05), lens=40)
    lib.save("ASSETS/Materials/Toon_Materials.blend", still=1)

if want("effects"):
    sc = lib.reset()
    import random
    rnd = random.Random(7)
    # 1) rain: Geometry Nodes, 1200 streaks in a 6 x 6 x 5 m box (scale the object for more) falling 9 m/s, loops forever (no simulation)
    c = lib.coll("FX Rain")
    me = bpy.data.meshes.new("rain")
    rain = bpy.data.objects.new("Rain", me)
    c.objects.link(rain)
    gn = bpy.data.node_groups.new("Rain GN", "GeometryNodeTree")
    gn.interface.new_socket("Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
    N_ = gn.nodes
    Lk = gn.links.new
    out = N_.new("NodeGroupOutput")
    pts = N_.new("GeometryNodePoints"); pts.inputs["Count"].default_value = 1200
    rv = N_.new("FunctionNodeRandomValue"); rv.data_type = "FLOAT_VECTOR"
    rv.inputs["Min"].default_value = (-3, -3, 0); rv.inputs["Max"].default_value = (3, 3, 5)
    Lk(rv.outputs["Value"], pts.inputs["Position"])
    tm_ = N_.new("GeometryNodeInputSceneTime")
    sep = N_.new("ShaderNodeSeparateXYZ")
    pos = N_.new("GeometryNodeInputPosition"); Lk(pos.outputs[0], sep.inputs[0])
    mul = N_.new("ShaderNodeMath"); mul.operation = "MULTIPLY"; mul.inputs[1].default_value = 9.0
    Lk(tm_.outputs["Seconds"], mul.inputs[0])
    sub = N_.new("ShaderNodeMath"); sub.operation = "SUBTRACT"
    Lk(sep.outputs["Z"], sub.inputs[0]); Lk(mul.outputs[0], sub.inputs[1])
    mod = N_.new("ShaderNodeMath"); mod.operation = "FLOORED_MODULO"; mod.inputs[1].default_value = 5.0
    Lk(sub.outputs[0], mod.inputs[0])
    com = N_.new("ShaderNodeCombineXYZ")
    Lk(sep.outputs["X"], com.inputs["X"]); Lk(sep.outputs["Y"], com.inputs["Y"]); Lk(mod.outputs[0], com.inputs["Z"])
    setp = N_.new("GeometryNodeSetPosition")
    Lk(pts.outputs[0], setp.inputs["Geometry"]); Lk(com.outputs[0], setp.inputs["Position"])
    cyl = N_.new("GeometryNodeMeshCylinder"); cyl.inputs["Vertices"].default_value = 5
    cyl.inputs["Radius"].default_value = 0.004; cyl.inputs["Depth"].default_value = 0.4
    inst = N_.new("GeometryNodeInstanceOnPoints")
    Lk(setp.outputs[0], inst.inputs["Points"]); Lk(cyl.outputs["Mesh"], inst.inputs["Instance"])
    real = N_.new("GeometryNodeRealizeInstances"); Lk(inst.outputs[0], real.inputs[0])
    sm = N_.new("GeometryNodeSetMaterial"); sm.inputs["Material"].default_value = lib.tm("fx rain", (0.8, 0.9, 1.0), 0.6)
    Lk(real.outputs[0], sm.inputs["Geometry"]); Lk(sm.outputs[0], out.inputs[0])
    rain.modifiers.new("Rain", "NODES").node_group = gn
    c.asset_mark()
    # 2) dust motes floating in a sunbeam
    c = lib.coll("FX Dust")
    dust = lib.root("Dust", c)
    for i in range(70):
        s = lib.SP(dust, (rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(0.3, 2.2)), rnd.uniform(0.006, 0.014),
                   lib.tm("fx dust", (1.0, 0.95, 0.75), 2.0), "mote", line=0)
        for f in (1, 120, 240):
            s.location.z += rnd.uniform(-0.15, 0.15)
            s.location.x += rnd.uniform(-0.1, 0.1)
            s.keyframe_insert("location", frame=f)
    lib.place(dust, (-4, 0, 0))
    c.asset_mark()
    # 3) comic impact star (pops in over 4 frames, gone after 10): put it where a hit lands
    c = lib.coll("FX Impact")
    st = lib.root("Impact star", c)
    pts = []
    for i in range(24):
        rr = 0.5 if i % 2 == 0 else 0.22
        a = i * math.pi / 12
        pts.append((rr * math.cos(a), 0, rr * math.sin(a)))
    me = bpy.data.meshes.new("star")
    me.from_pydata([(0, 0, 0)] + pts, [], [(0, i + 1, (i + 1) % 24 + 1) for i in range(24)])
    o = bpy.data.objects.new("Impact star shape", me)
    c.objects.link(o)
    o.parent = st
    o.data.materials.append(lib.tm("fx star", (1.0, 0.85, 0.2), 1.5))
    sl = o.modifiers.new("thick", "SOLIDIFY")
    sl.thickness = 0.02
    lib.outline(o, 0.02)
    for f, s in ((1, 0.01), (4, 1.2), (6, 1.0), (10, 0.01)):
        st.scale = (s, s, s)
        st.keyframe_insert("scale", frame=f)
    lib.place(st, (4, 0, 1.2))
    c.asset_mark()
    # 4) speed lines (behind a running character)
    c = lib.coll("FX Speed lines")
    sp = lib.root("Speed lines", c)
    for i in range(9):
        b = lib.B(sp, (0, 0, 0.3 + i * 0.2), (rnd.uniform(0.6, 1.4), 0.015, 0.015), lib.tm("fx line", (1, 1, 1), 1.0), "line", line=0.004)
        b.location.x = rnd.uniform(-0.3, 0.3)
        for f in range(1, 241, 6):
            b.location.x = rnd.uniform(-0.3, 0.3)
            b.keyframe_insert("location", index=0, frame=f)
    lib.place(sp, (8, 0, 0))
    c.asset_mark()
    lib.B(lib.root("Ground", lib.coll("Ground")), (2, 0, -0.05), (24, 12, 0.1), lib.M("road"), "ground", line=0)
    sc.frame_start, sc.frame_end = 1, 240
    lib.look(sc, res=(1600, 700), sky=(0.35, 0.4, 0.5))
    lib.camera(sc, (2, -11, 1.6), (2, 0, 1.2), lens=35)
    lib.save("ASSETS/Effects/Effects.blend", still=40)
