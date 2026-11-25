"""Look test for the reference style: abandoned overgrown city, glass vault arcade, peach sky,
cel shading + thin ink, slow drone camera. ../cast/bpy.sh look_test.py --still 1,60,120"""
import bpy, sys, os, math, random, bmesh
from mathutils import Vector, Matrix
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "cast"))
sys.path.insert(0, os.path.join(HERE, "..", "studio"))
bpy.ops.wm.read_factory_settings(use_empty=True)
import props as P, toon_look as T
sc = bpy.context.scene
R = random.Random(7)
FPS = 24

M = dict(
    conc=P.mat("Concrete", (0.8, 0.76, 0.68), 0.9), conc2=P.mat("Concrete 2", (0.74, 0.69, 0.62), 0.9),
    win=P.mat("Window dark", (0.24, 0.22, 0.22), 0.9), wglass=P.mat("Window glass", (0.5, 0.52, 0.52), 0.9),
    ivy=P.mat("Ivy", (0.36, 0.62, 0.3), 0.9), ivy2=P.mat("Ivy mid", (0.3, 0.54, 0.26), 0.9),
    ivy3=P.mat("Ivy light", (0.44, 0.7, 0.34), 0.9),
    road=P.mat("Road", (0.44, 0.43, 0.43), 0.9), walk=P.mat("Pavement", (0.68, 0.63, 0.56), 0.9),
    paving=P.mat("Arcade floor", (0.66, 0.58, 0.5), 0.9), paving2=P.mat("Arcade floor 2", (0.63, 0.55, 0.48), 0.9),
    iron=P.mat("Iron", (0.2, 0.2, 0.21), 0.5), bars=P.mat("Glazing bars", (0.12, 0.12, 0.13), 0.5),
    pane=P.mat("Pane", (0.92, 0.92, 0.88), 0.2), pane2=P.mat("Pane grey", (0.66, 0.67, 0.66), 0.2),
    pane3=P.mat("Pane dark", (0.3, 0.31, 0.32), 0.2),
    trunk=P.mat("Trunk", (0.36, 0.26, 0.2), 0.9), leaf=P.mat("Leaf", (0.46, 0.68, 0.32), 0.9),
    leaf2=P.mat("Leaf 2", (0.38, 0.6, 0.28), 0.9),
    wall=P.mat("Low wall", (0.74, 0.66, 0.54), 0.9), wall2=P.mat("Low wall 2", (0.64, 0.56, 0.46), 0.9),
)
IVY = []
INK = []


def link(name, bm, mats):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    sc.collection.objects.link(o)
    for m in mats:
        me.materials.append(m)
    return o



def blob(bm, c, axis, r, thick=0.06):
    """Irregular flat leaf-blob (painted-ivy look) facing along axis 'x' or 'y'."""
    res = bmesh.ops.create_cone(bm, cap_ends=True, segments=11, radius1=1, radius2=1, depth=1)
    k = [R.uniform(0.7, 1.2) for _ in range(11)]
    for v in res["verts"]:
        a = math.atan2(v.co.y, v.co.x)
        i = int(round((a % (2 * math.pi)) / (2 * math.pi) * 11)) % 11
        v.co.x *= k[i]
        v.co.y *= k[i]
    rot = Matrix.Rotation(math.radians(90), 4, "X") if axis == "y" else Matrix.Rotation(math.radians(90), 4, "Y")
    m = Matrix.Translation(c) @ rot @ Matrix.Diagonal((r, r * R.uniform(1.1, 1.6), thick, 1)) if axis == "y" else \
        Matrix.Translation(c) @ rot @ Matrix.Diagonal((r * R.uniform(1.1, 1.6), r, thick, 1))
    bmesh.ops.transform(bm, matrix=m, verts=res["verts"])


FACES = ((0, -1), (0, 1), (-1, 0), (1, 0))


def tower(cx, cy, w, d, h, floors_h=3.2, m="conc"):
    """Box tower: floor cornices, recessed windows (dark / glass with mullion), ivy hanging from the roof and
    climbing from the ground."""
    b = P.box((cx, cy, h / 2), (w, d, h), M[m], "Tower")
    INK.append(b)
    nf = int(h / floors_h)
    bm = bmesh.new()                                      # cornices: one thin band per floor
    for k in range(1, nf + 1):
        z = k * floors_h
        bmesh.ops.create_cube(bm, size=1, matrix=Matrix.Translation((cx, cy, z)) @ Matrix.Diagonal((w + 0.12, d + 0.12, 0.14, 1)))
    INK.append(link("Tower cornice", bm, [M[m]]))
    bmd, bmg = bmesh.new(), bmesh.new()
    for nx, ny in FACES:
        span = w if nx == 0 else d
        nc = max(2, int(span / 1.9))
        for i in range(nc):
            u = -span / 2 + (i + 0.5) * span / nc
            for k in range(0, nf):
                z = k * floors_h + 0.75
                px = cx + (u if nx == 0 else nx * (w / 2 + 0.005))
                py = cy + (u if ny == 0 else ny * (d / 2 + 0.005))
                sx, sy = (0.95, 0.03) if nx == 0 else (0.03, 0.95)
                glass = R.random() < 0.3
                bmesh.ops.create_cube(bmg if glass else bmd, size=1,
                                      matrix=Matrix.Translation((px, py, z + 0.8)) @ Matrix.Diagonal((sx, sy, 1.6, 1)))
    INK.append(link("Tower windows", bmd, [M["win"]]))
    INK.append(link("Tower windows glass", bmg, [M["wglass"]]))
    # ivy
    for shade in ("ivy", "ivy2", "ivy3"):
        bm = bmesh.new()
        for nx, ny in FACES:
            span = w if nx == 0 else d
            axis = "y" if nx == 0 else "x"
            for s in range(int(span / 1.5)):
                if R.random() < 0.35:
                    continue
                u = R.uniform(-span / 2 + 0.5, span / 2 - 0.5)
                if R.random() < 0.5:                       # climbing from the ground
                    z0, z1 = 0.0, R.uniform(0.15, 0.6) * h
                else:                                      # hanging from somewhere high
                    z1 = R.uniform(0.5, 1.0) * h
                    z0 = z1 - R.uniform(0.15, 0.4) * h
                z = z0
                while z < z1:
                    taper = 1.0 - 0.6 * (z - z0) / max(1, z1 - z0) if z0 == 0 else 0.5 + 0.5 * (z - z0) / max(1, z1 - z0)
                    r = R.uniform(0.35, 0.8) * taper + 0.2
                    u2 = u + R.uniform(-0.7, 0.7) * taper
                    off = 0.05 + {"ivy": 0.0, "ivy2": 0.04, "ivy3": 0.08}[shade]
                    px = cx + (u2 if nx == 0 else nx * (w / 2 + off))
                    py = cy + (u2 if ny == 0 else ny * (d / 2 + off))
                    if R.random() < 0.8:
                        blob(bm, (px, py, z), axis, r)
                    z += R.uniform(0.35, 0.9)
        IVY.append(link("Ivy " + shade, bm, [M[shade]]))
    for j in range(2):
        P.sphere((cx + R.uniform(-w / 3, w / 3), cy + R.uniform(-d / 3, d / 3), h + 0.6), R.uniform(1.0, 1.6), M["leaf"], "Roof tree",
                 scale=(1, 1, 0.8))
        INK.append(bpy.context.object)


def vault(x0, x1, cy, radius, z0):
    """Glass barrel vault along X: heavy iron arches every ~3 m, purlins, a regular grid of small square panes
    (mostly pale, a few grey or dark, very few missing)."""
    bm = bmesh.new()
    na = int((x1 - x0) / 3.0) + 1
    nr = 24
    for i in range(na):
        x = x0 + i * (x1 - x0) / (na - 1)
        for k in range(nr):
            a0, a1 = math.pi * k / nr, math.pi * (k + 1) / nr
            p0 = Vector((x, cy + radius * math.cos(a0), z0 + radius * math.sin(a0)))
            p1 = Vector((x, cy + radius * math.cos(a1), z0 + radius * math.sin(a1)))
            d = p1 - p0
            bmesh.ops.create_cube(bm, size=1, matrix=Matrix.Translation((p0 + p1) / 2) @ d.to_track_quat("Z", "X").to_matrix().to_4x4()
                                  @ Matrix.Diagonal((0.16, 0.22, d.length + 0.02, 1)))
    io = link("Vault iron", bm, [M["iron"]])
    INK.append(io)
    nx = int((x1 - x0) / 0.5)
    ny = int(math.pi * radius / 0.5)
    bms = {k: bmesh.new() for k in ("pane", "pane2", "pane3")}
    bmb = bmesh.new()                                   # glazing bars (thin dark grid under the panes)
    for i in range(nx):
        x = x0 + (i + 0.5) * (x1 - x0) / nx
        for k in range(ny):
            a = math.pi * (k + 0.5) / ny
            n = Vector((0, math.cos(a), math.sin(a)))
            c = Vector((x, cy, z0)) + n * (radius + 0.03)
            q = n.to_track_quat("Z", "X").to_matrix().to_4x4()
            rr = R.random()
            if rr < 0.03:
                continue
            key = "pane3" if rr < 0.09 else "pane2" if rr < 0.2 else "pane"
            bmesh.ops.create_cube(bms[key], size=1, matrix=Matrix.Translation(c) @ q @ Matrix.Diagonal(
                ((x1 - x0) / nx * 0.86, math.pi * radius / ny * 0.86, 0.015, 1)))
    shell = bmesh.new()                                 # the dark bars show between panes
    bmesh.ops.create_cone(shell, cap_ends=False, segments=48, radius1=radius, radius2=radius, depth=x1 - x0,
                          matrix=Matrix.Translation(((x0 + x1) / 2, cy, z0)) @ Matrix.Rotation(math.radians(90), 4, "Y"))
    bmesh.ops.delete(shell, geom=[v for v in shell.verts if v.co.z < z0 - 0.01], context="VERTS")
    link("Vault bars", shell, [M["bars"]])
    M["bars"].use_backface_culling = True                # seen only from outside (between the panes)
    for key, b in bms.items():
        link("Vault " + key, b, [M[key]])
    for sy in (-1, 1):                                   # side walls with pillars
        y = cy + sy * radius
        INK.append(P.box(((x0 + x1) / 2, y, z0 / 2), (x1 - x0, 0.6, z0), M["wall"], "Arcade wall"))
        INK.append(P.box(((x0 + x1) / 2, y, z0 + 0.1), (x1 - x0, 0.8, 0.25), M["wall2"], "Arcade cornice"))
        for i in range(na):
            x = x0 + i * (x1 - x0) / (na - 1)
            INK.append(P.box((x, y, z0 + 0.8), (0.5, 0.7, 1.4), M["wall"], "Pillar"))
            INK.append(P.box((x, y - sy * 0.31, z0 / 2), (1.2, 0.04, z0 * 0.7), M["win"], "Arcade door"))


def tree(x, y, s=1.0):
    INK.append(P.cyl((x, y, 0), (x, y, 2.2 * s), 0.12 * s, M["trunk"], "Trunk"))
    for j in range(5):
        P.sphere((x + R.uniform(-0.8, 0.8) * s, y + R.uniform(-0.8, 0.8) * s, (2.6 + R.uniform(0, 1.2)) * s),
                 R.uniform(0.8, 1.2) * s, M["leaf" if j % 2 else "leaf2"], "Leaves")
        INK.append(bpy.context.object)


# ground: asphalt, pavements, curbs, tram rails, paved arcade floor
INK.append(P.box((0, 0, -0.1), (400, 400, 0.2), M["road"], "Ground"))
for y in (-8.5, 8.5, -17.5, 17.5):
    INK.append(P.box((0, y, 0.06), (200, 3.0, 0.12), M["walk"], "Pavement"))
for y in (-12.6, -11.4, 11.4, 12.6):
    P.box((0, y, 0.01), (200, 0.08, 0.02), M["iron"], "Rail")
for i in range(-30, 30):
    P.box((i + 0.5, 0, 0.02), (0.96, 13, 0.04), M["paving" if i % 2 else "paving2"], "Arcade paving")
vault(-30, 30, 0, 6.5, 4.0)
TOWERS = [(-18, 27), (6, 29), (24, 26), (-14, -27), (14, -28), (42, 0), (-44, 4), (2, 54), (-32, 52), (34, -30), (-40, -30)]
for cx, cy, w, d, h, m in ((-18, 27, 14, 12, 62, "conc"), (6, 29, 12, 12, 48, "conc2"), (24, 26, 14, 10, 70, "conc"),
                           (-14, -27, 12, 12, 54, "conc2"), (14, -28, 16, 12, 40, "conc"), (42, 0, 12, 14, 58, "conc2"),
                           (-44, 4, 12, 16, 44, "conc"), (2, 54, 18, 14, 80, "conc"), (-32, 52, 14, 14, 36, "conc2"),
                           (34, -30, 12, 12, 64, "conc2"), (-40, -30, 14, 12, 50, "conc")):
    tower(cx, cy, w, d, h, m=m)
# low blocks filling the gaps between the towers (roofs seen from the drone)
for gx in range(-90, 91, 15):
    for gy in range(-90, 91, 15):
        x, y = gx + R.uniform(-2, 2), gy + R.uniform(-2, 2)
        if abs(y) < 22 or any(abs(x - tx) < 12 and abs(y - ty) < 12 for tx, ty in TOWERS):
            continue
        tower(x, y, R.uniform(8, 11), R.uniform(8, 11), R.uniform(12, 26), m=R.choice(("conc", "conc2")))
for x in range(-26, 27, 6):
    tree(x, 3.4 if (x // 6) % 2 else -3.4, R.uniform(0.8, 1.1))
for x in range(-28, 29, 6):
    INK.append(P.cyl((x, -5.0, 0), (x, -5.0, 4.0), 0.07, M["iron"], "Lamp post"))
    INK.append(P.sphere((x, -5.0, 4.1), 0.18, M["iron"], "Lamp"))
# sky: the camera sees a peach gradient; the scene is lit by a neutral grey ambient + a warm low sun
w = bpy.data.worlds.new("Sky")
sc.world = w
w.use_nodes = True
nt = w.node_tree
nt.nodes.clear()
tc = nt.nodes.new("ShaderNodeTexCoord")
sep = nt.nodes.new("ShaderNodeSeparateXYZ")
ramp = nt.nodes.new("ShaderNodeValToRGB")
bg = nt.nodes.new("ShaderNodeBackground")
amb = nt.nodes.new("ShaderNodeBackground")
lp = nt.nodes.new("ShaderNodeLightPath")
mix = nt.nodes.new("ShaderNodeMixShader")
out = nt.nodes.new("ShaderNodeOutputWorld")
nt.links.new(tc.outputs["Generated"], sep.inputs[0])
nt.links.new(sep.outputs["Z"], ramp.inputs[0])
ramp.color_ramp.elements[0].position, ramp.color_ramp.elements[0].color = 0.5, (0.9, 0.52, 0.34, 1)
ramp.color_ramp.elements[1].position, ramp.color_ramp.elements[1].color = 0.85, (0.78, 0.42, 0.28, 1)
nt.links.new(ramp.outputs[0], bg.inputs[0])
amb.inputs[0].default_value = (0.42, 0.42, 0.45, 1)
nt.links.new(lp.outputs["Is Camera Ray"], mix.inputs[0])
nt.links.new(amb.outputs[0], mix.inputs[1])
nt.links.new(bg.outputs[0], mix.inputs[2])
nt.links.new(mix.outputs[0], out.inputs[0])
sun = bpy.data.objects.new("Sun", bpy.data.lights.new("Sun", "SUN"))
sc.collection.objects.link(sun)
sun.data.energy = 2.6
sun.data.color = (1.0, 0.9, 0.78)
sun.data.angle = 0.02
sun.rotation_euler = (math.radians(55), 0, math.radians(-120))

# camera (reference moves): A high aerial drift over the vault between towers, B low angle up at a tower and the
# vault's side with a slow pan, C slow push along the street under the glass

N = 14 * FPS
cam = bpy.data.objects.new("Camera", bpy.data.cameras.new("Camera"))
sc.collection.objects.link(cam)
sc.camera = cam
cam.data.clip_end = 800
KEYS = [(0.0, (-48, -12, 44), (0, 3, 3), 30), (4.96, (-42, -17, 41), (4, 2, 3), 30),
        (5.0, (-10, -14, 1.6), (2, 16, 30), 22), (8.96, (-7, -14.5, 1.6), (8, 16, 32), 22),
        (9.0, (-27, 0.5, 1.7), (20, 0, 8.5), 20), (14.0, (-17, 0.5, 1.7), (30, 0, 8.5), 20)]
for t, c, a_, lens in KEYS:
    f = int(round(t * FPS)) + 1
    cam.location = c
    cam.rotation_euler = (Vector(a_) - Vector(c)).to_track_quat("-Z", "Y").to_euler()
    cam.keyframe_insert("location", frame=f)
    cam.keyframe_insert("rotation_euler", frame=f)
    cam.data.lens = lens
    cam.data.keyframe_insert("lens", frame=f)
def fcurves_of(owner):
    act = owner.animation_data.action
    if hasattr(act, "fcurves") and len(act.fcurves):
        return list(act.fcurves)
    return [fc for l in act.layers for st in l.strips for cb in st.channelbags for fc in cb.fcurves]


for owner in (cam, cam.data):
    for fc in fcurves_of(owner):
        for k in fc.keyframe_points:
            k.interpolation = "LINEAR"
sc.frame_start, sc.frame_end = 1, N

T.SAT = 0.6
T.toonify(sc, samples=8)
T.ink(INK, 0.035)
# ivy: its own dark-green outline (the reference draws the leaves with a darker green, not black)
im = bpy.data.materials.new("Ink ivy")
im.use_nodes = True
im.use_backface_culling = True
for n in list(im.node_tree.nodes):
    im.node_tree.nodes.remove(n)
e = im.node_tree.nodes.new("ShaderNodeEmission")
e.inputs[0].default_value = (0.03, 0.08, 0.03, 1)
o_ = im.node_tree.nodes.new("ShaderNodeOutputMaterial")
im.node_tree.links.new(e.outputs[0], o_.inputs[0])
for o in IVY:
    o.data.materials.append(im)
    sd = o.modifiers.new("Outline", "SOLIDIFY")
    sd.thickness, sd.offset, sd.use_flip_normals, sd.use_rim = 0.05, 1.0, True, False
    sd.material_offset = len(o.data.materials) - 1
sc.render.resolution_x, sc.render.resolution_y = 540, 960
sc.render.fps = FPS
args = sys.argv
if "--frames" in args:                     # preview: every frame -> test/p_XXXX.png (skips existing)
    a, b = [int(v) for v in args[args.index("--frames") + 1].split("-")]
    os.makedirs(os.path.join(HERE, "test"), exist_ok=True)
    for f in range(a, b + 1):
        p = os.path.join(HERE, "test", f"p_{f:04d}.png")
        if os.path.exists(p):
            continue
        sc.frame_set(f)
        sc.render.filepath = p
        bpy.ops.render.render(write_still=True)
if "--still" in args:
    os.makedirs(os.path.join(HERE, "test"), exist_ok=True)
    for f in [int(v) for v in args[args.index("--still") + 1].split(",")]:
        sc.frame_set(f)
        sc.render.filepath = os.path.join(HERE, "test", f"look_{f:04d}.png")
        bpy.ops.render.render(write_still=True)
