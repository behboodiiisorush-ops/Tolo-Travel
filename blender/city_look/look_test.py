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
    conc=P.mat("Concrete", (0.74, 0.7, 0.62), 0.9), conc2=P.mat("Concrete 2", (0.66, 0.6, 0.54), 0.9),
    win=P.mat("Window dark", (0.2, 0.19, 0.2), 0.9), ivy=P.mat("Ivy", (0.3, 0.52, 0.24), 0.9),
    ivy2=P.mat("Ivy dark", (0.22, 0.4, 0.2), 0.9), road=P.mat("Road", (0.52, 0.48, 0.44), 0.9),
    walk=P.mat("Pavement", (0.66, 0.6, 0.52), 0.9), iron=P.mat("Iron", (0.16, 0.16, 0.17), 0.5),
    pane=P.mat("Pane", (0.86, 0.88, 0.86), 0.2), pane2=P.mat("Pane dark", (0.42, 0.44, 0.44), 0.2),
    trunk=P.mat("Trunk", (0.36, 0.26, 0.2), 0.9), leaf=P.mat("Leaf", (0.42, 0.62, 0.3), 0.9),
    brick=P.mat("Brick", (0.5, 0.3, 0.26), 0.9), wall=P.mat("Low wall", (0.7, 0.62, 0.5), 0.9),
)
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


def tower(cx, cy, w, d, h, floors_h=3.2, m="conc"):
    """Box tower, dark window recesses on all four faces (one mesh), ivy blobs climbing from the ground."""
    b = P.box((cx, cy, h / 2), (w, d, h), M[m], "Tower")
    INK.append(b)
    bm = bmesh.new()
    nf = int(h / floors_h)
    for face, (nx, ny) in enumerate(((0, -1), (0, 1), (-1, 0), (1, 0))):
        span = w if nx == 0 else d
        nc = max(2, int(span / 2.0))
        for i in range(nc):
            u = -span / 2 + (i + 0.5) * span / nc
            for k in range(1, nf):
                if R.random() < 0.03:
                    continue
                z = k * floors_h + 0.3
                px = cx + (u if nx == 0 else nx * (w / 2 + 0.01))
                py = cy + (u if ny == 0 else ny * (d / 2 + 0.01))
                sx, sy = (1.0, 0.04) if nx == 0 else (0.04, 1.0)
                bmesh.ops.create_cube(bm, size=1, matrix=Matrix.Translation((px, py, z + 0.75)) @ Matrix.Diagonal((sx, sy, 1.5, 1)))
    wo = link("Tower windows", bm, [M["win"]])
    INK.append(wo)
    # ivy: vertical streaks of flattened blobs from the ground up the faces
    bm = bmesh.new()
    for face, (nx, ny) in enumerate(((0, -1), (0, 1), (-1, 0), (1, 0))):
        span = w if nx == 0 else d
        for s in range(int(span * 0.9)):
            u = R.uniform(-span / 2, span / 2)
            top = R.uniform(0.2, 0.75) * h
            z = 0.0
            while z < top:
                r = R.uniform(0.45, 1.1) * (1.0 - 0.5 * z / h)
                u2 = u + R.uniform(-0.6, 0.6)
                px = cx + (u2 if nx == 0 else nx * (w / 2 + 0.06))
                py = cy + (u2 if ny == 0 else ny * (d / 2 + 0.06))
                sc_ = (r, 0.12, r * 1.4) if nx == 0 else (0.12, r, r * 1.4)
                bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1, matrix=Matrix.Translation((px, py, z)) @ Matrix.Diagonal(sc_ + (1,)))
                z += R.uniform(0.6, 1.6)
    iv = link("Ivy", bm, [M["ivy"] if R.random() < 0.6 else M["ivy2"]])
    INK.append(iv)
    # roof garden
    for j in range(3):
        P.sphere((cx + R.uniform(-w / 3, w / 3), cy + R.uniform(-d / 3, d / 3), h + 0.8), R.uniform(1.0, 1.8), M["leaf"], "Roof tree")
        INK.append(bpy.context.object)


def vault(x0, x1, cy, radius, z0):
    """Glass barrel vault along X: iron arches + purlins (one mesh) + panes, some broken (dark/missing)."""
    bm = bmesh.new()
    na, nr = int((x1 - x0) / 2.2) + 1, 14
    for i in range(na):
        x = x0 + i * (x1 - x0) / (na - 1)
        for k in range(nr):
            a0, a1 = math.pi * k / nr, math.pi * (k + 1) / nr
            p0 = Vector((x, cy + radius * math.cos(a0), z0 + radius * math.sin(a0)))
            p1 = Vector((x, cy + radius * math.cos(a1), z0 + radius * math.sin(a1)))
            d = p1 - p0
            bmesh.ops.create_cube(bm, size=1, matrix=Matrix.Translation((p0 + p1) / 2) @ d.to_track_quat("Z", "X").to_matrix().to_4x4()
                                  @ Matrix.Diagonal((0.12, 0.12, d.length + 0.1, 1)))
    for k in range(nr + 1):
        a = math.pi * k / nr
        y, z = cy + radius * math.cos(a), z0 + radius * math.sin(a)
        bmesh.ops.create_cube(bm, size=1, matrix=Matrix.Translation(((x0 + x1) / 2, y, z)) @ Matrix.Diagonal((x1 - x0, 0.06, 0.06, 1)))
    io = link("Vault iron", bm, [M["iron"]])
    INK.append(io)
    bm = bmesh.new()
    bm2 = bmesh.new()
    nx = int((x1 - x0) / 0.55)
    for i in range(nx):
        x = x0 + (i + 0.5) * (x1 - x0) / nx
        for k in range(nr * 3):
            if R.random() < 0.12:
                continue
            a = math.pi * (k + 0.5) / (nr * 3)
            c = Vector((x, cy + (radius - 0.02) * math.cos(a), z0 + (radius - 0.02) * math.sin(a)))
            n = Vector((0, math.cos(a), math.sin(a)))
            q = n.to_track_quat("Z", "X").to_matrix().to_4x4()
            tgt = bm2 if R.random() < 0.18 else bm
            bmesh.ops.create_cube(bm if tgt is bm else bm2, size=1,
                                  matrix=Matrix.Translation(c) @ q @ Matrix.Diagonal(((x1 - x0) / nx * 0.88, math.pi * radius / (nr * 3) * 0.88, 0.02, 1)))
    po = link("Vault panes", bm, [M["pane"]])
    po2 = link("Vault panes dark", bm2, [M["pane2"]])
    INK.extend([po, po2])
    # side walls: low wall with pillars
    for sy in (-1, 1):
        y = cy + sy * radius
        P.box(((x0 + x1) / 2, y, z0 / 2), (x1 - x0, 0.5, z0), M["wall"], "Arcade wall")
        INK.append(bpy.context.object)
        for i in range(0, na, 2):
            x = x0 + i * (x1 - x0) / (na - 1)
            P.box((x, y, z0 + 0.6), (0.5, 0.6, 1.2), M["wall"], "Pillar")
            INK.append(bpy.context.object)


def tree(x, y, s=1.0):
    t = P.cyl((x, y, 0), (x, y, 2.2 * s), 0.12 * s, M["trunk"], "Trunk")
    INK.append(t)
    for j in range(5):
        P.sphere((x + R.uniform(-0.8, 0.8) * s, y + R.uniform(-0.8, 0.8) * s, (2.6 + R.uniform(0, 1.2)) * s),
                 R.uniform(0.8, 1.2) * s, M["leaf"], "Leaves")
        INK.append(bpy.context.object)


# ground
P.box((0, 0, -0.1), (400, 400, 0.2), M["road"], "Ground")
P.box((0, 9, 0.05), (200, 4, 0.1), M["walk"], "Pavement")
P.box((0, -9, 0.05), (200, 4, 0.1), M["walk"], "Pavement 2")
# the arcade (street under a glass vault) running along X
vault(-30, 30, 0, 6.5, 4.0)
# towers around
for cx, cy, w, d, h, m in ((-18, 22, 14, 12, 62, "conc"), (6, 26, 12, 12, 48, "conc2"), (24, 20, 14, 10, 70, "conc"),
                           (-14, -22, 12, 12, 54, "conc2"), (14, -24, 16, 12, 40, "conc"), (40, 0, 12, 14, 58, "conc2"),
                           (-42, 4, 12, 16, 44, "conc"), (2, 50, 18, 14, 80, "conc"), (-30, 48, 14, 14, 36, "conc2")):
    tower(cx, cy, w, d, h, m=m)
for x in range(-26, 27, 8):
    tree(x, 3.2 if (x // 8) % 2 else -3.2, R.uniform(0.9, 1.2))
for x in range(-28, 29, 7):
    INK.append(P.cyl((x, -4.6, 0), (x, -4.6, 4.2), 0.07, M["iron"], "Lamp post"))
# sky: peach gradient, warm low sun
w = bpy.data.worlds.new("Sky")
sc.world = w
w.use_nodes = True
nt = w.node_tree
nt.nodes.clear()
tc = nt.nodes.new("ShaderNodeTexCoord")
sep = nt.nodes.new("ShaderNodeSeparateXYZ")
ramp = nt.nodes.new("ShaderNodeValToRGB")
bg = nt.nodes.new("ShaderNodeBackground")
out = nt.nodes.new("ShaderNodeOutputWorld")
nt.links.new(tc.outputs["Generated"], sep.inputs[0])
nt.links.new(sep.outputs["Z"], ramp.inputs[0])
ramp.color_ramp.elements[0].position, ramp.color_ramp.elements[0].color = 0.0, (0.72, 0.36, 0.22, 1)
ramp.color_ramp.elements[1].position, ramp.color_ramp.elements[1].color = 0.6, (0.62, 0.3, 0.18, 1)
nt.links.new(ramp.outputs[0], bg.inputs[0])
bg.inputs[1].default_value = 1.0
nt.links.new(bg.outputs[0], out.inputs[0])
sun = bpy.data.objects.new("Sun", bpy.data.lights.new("Sun", "SUN"))
sc.collection.objects.link(sun)
sun.data.energy = 3.2
sun.data.color = (1.0, 0.85, 0.7)
sun.data.angle = 0.02
sun.rotation_euler = (math.radians(62), 0, math.radians(-130))

# camera: drone descends between two towers and tilts up onto the vault (0-5 s), then a slow push
# along the street under the glass (5-10 s)
N = 10 * FPS
cam = bpy.data.objects.new("Camera", bpy.data.cameras.new("Camera"))
sc.collection.objects.link(cam)
sc.camera = cam
cam.data.clip_end = 600
KEYS = [(0.0, (-4, -2, 38), (8, 30, 22), 24), (4.9, (-6, -6, 14), (6, 14, 18), 22),
        (5.0, (-26, 0, 1.7), (10, 0, 7.5), 20), (10.0, (-14, 0, 1.7), (20, 0, 8.0), 20)]
for t, c, a, lens in KEYS:
    f = int(t * FPS) + 1
    cam.location = c
    cam.rotation_euler = (Vector(a) - Vector(c)).to_track_quat("-Z", "Y").to_euler()
    cam.keyframe_insert("location", frame=f)
    cam.keyframe_insert("rotation_euler", frame=f)
    cam.data.lens = lens
    cam.data.keyframe_insert("lens", frame=f)
sc.frame_start, sc.frame_end = 1, N

T.SAT = 0.6
T.toonify(sc, samples=8)
T.ink(INK, 0.04)
for o in bpy.data.objects:
    if "Outline" in o.modifiers and o.name.startswith(("Tower windows", "Vault panes", "Vault iron")):
        o.modifiers["Outline"].thickness = 0.03
sc.render.resolution_x, sc.render.resolution_y = 540, 960
sc.render.fps = FPS
args = sys.argv
if "--still" in args:
    os.makedirs(os.path.join(HERE, "test"), exist_ok=True)
    for f in [int(v) for v in args[args.index("--still") + 1].split(",")]:
        sc.frame_set(f)
        sc.render.filepath = os.path.join(HERE, "test", f"look_{f:04d}.png")
        bpy.ops.render.render(write_still=True)
