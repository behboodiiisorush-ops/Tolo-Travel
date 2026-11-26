"""The city of «سال ۱۵۰۰» (same look as blender/city_look): towers with floor cornices, a glass barrel vault over
the main street, a big screen at the end of the street. Built once, in two states keyed by visibility:
  INTACT  only in the flashback (clean towers, light strips, all panes, parked cars, upright lamps)
  RUIN    only in the present (ivy everywhere, broken panes on the floor, wrecked cars, bent lamps, rubble)
Everything else is shared.  import city; C = city.build()  -> dict with M, INK, IVY, INTACT, RUIN, SCREEN ...
"""
import bpy, math, random, bmesh
from mathutils import Vector, Matrix
import props as P

R = random.Random(7)
FACES = ((0, -1), (0, 1), (-1, 0), (1, 0))
M, INK, IVY, INTACT, RUIN = {}, [], [], [], []
VAULT = dict(x0=-30, x1=30, cy=0, radius=6.5, z0=4.0)
SCREEN_C, SCREEN_W, SCREEN_H = (35.75, 0.0, 7.6), 12.0, 6.75      # on the west face of the tower at (42, 0)


def mats():
    M.update(
        conc=P.mat("Concrete", (0.8, 0.76, 0.68), 0.9), conc2=P.mat("Concrete 2", (0.74, 0.69, 0.62), 0.9),
        win=P.mat("Window dark", (0.24, 0.22, 0.22), 0.9), wglass=P.mat("Window glass", (0.5, 0.52, 0.52), 0.9),
        ivy=P.mat("Ivy", (0.36, 0.62, 0.3), 0.9), ivy2=P.mat("Ivy mid", (0.3, 0.54, 0.26), 0.9),
        ivy3=P.mat("Ivy light", (0.44, 0.7, 0.34), 0.9),
        road=P.mat("Road", (0.44, 0.43, 0.43), 0.9), walk=P.mat("Pavement", (0.68, 0.63, 0.56), 0.9),
        paving=P.mat("Arcade floor", (0.66, 0.58, 0.5), 0.9), paving2=P.mat("Arcade floor 2", (0.63, 0.55, 0.48), 0.9),
        iron=P.mat("Iron", (0.2, 0.2, 0.21), 0.5), bars=P.mat("Glazing bars", (0.12, 0.12, 0.13), 0.5),
        pane=P.mat("Pane", (0.92, 0.92, 0.88), 0.2), pane2=P.mat("Pane grey", (0.66, 0.67, 0.66), 0.2),
        pane3=P.mat("Pane dark", (0.3, 0.31, 0.32), 0.2), shard=P.mat("Shard", (0.85, 0.87, 0.85), 0.2),
        trunk=P.mat("Trunk", (0.36, 0.26, 0.2), 0.9), leaf=P.mat("Leaf", (0.46, 0.68, 0.32), 0.9),
        leaf2=P.mat("Leaf 2", (0.38, 0.6, 0.28), 0.9),
        wall=P.mat("Low wall", (0.74, 0.66, 0.54), 0.9), wall2=P.mat("Low wall 2", (0.64, 0.56, 0.46), 0.9),
        rubble=P.mat("Rubble", (0.7, 0.66, 0.6), 0.95), soot=P.mat("Soot", (0.16, 0.15, 0.15), 0.95),
        car1=P.mat("Car pale", (0.78, 0.8, 0.8), 0.4), car2=P.mat("Car teal", (0.3, 0.5, 0.52), 0.4),
        car3=P.mat("Car rust", (0.6, 0.36, 0.26), 0.4), cglass=P.mat("Car glass", (0.2, 0.24, 0.27), 0.2),
        tyre=P.mat("Tyre", (0.08, 0.08, 0.09), 0.9), frame=P.mat("Screen frame", (0.1, 0.1, 0.11), 0.5),
    )
    for name, col, s in (("strip", (0.45, 0.95, 1.0), 6.0), ("strip_dead", (0.15, 0.17, 0.18), 0.0)):
        m = bpy.data.materials.new("Light " + name)
        m.use_nodes = True
        nt = m.node_tree
        nt.nodes.clear()
        e = nt.nodes.new("ShaderNodeEmission")
        e.inputs[0].default_value = (*col, 1)
        e.inputs[1].default_value = s
        o = nt.nodes.new("ShaderNodeOutputMaterial")
        nt.links.new(e.outputs[0], o.inputs[0])
        M[name] = m


def link(name, bm, ms, group=None):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(o)
    for m in ms:
        me.materials.append(m)
    if group is not None:
        group.append(o)
    return o


def cube(bm, c, size, rot=None):
    m = Matrix.Translation(c)
    if rot is not None:
        m = m @ rot
    bmesh.ops.create_cube(bm, size=1, matrix=m @ Matrix.Diagonal((*size, 1)))


def quad(bm, c, sx, sy, rot):
    """One-sided quad (normal = rot's +Z), seen only from that side with backface culling."""
    vs = [bm.verts.new(c + rot.to_3x3() @ Vector((dx * sx / 2, dy * sy / 2, 0)))
          for dx, dy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    bm.faces.new(vs)


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


def tower(cx, cy, w, d, h, floors_h=3.2, m="conc", strips=False):
    b = P.box((cx, cy, h / 2), (w, d, h), M[m], "Tower")
    INK.append(b)
    nf = int(h / floors_h)
    bm = bmesh.new()
    for k in range(1, nf + 1):
        cube(bm, (cx, cy, k * floors_h), (w + 0.12, d + 0.12, 0.14))
    INK.append(link("Tower cornice", bm, [M[m]]))
    bmd, bmg, bmb = bmesh.new(), bmesh.new(), bmesh.new()      # dark / glass / broken (present only, sooty)
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
                cube(bmg if glass else bmd, (px, py, z + 0.8), (sx, sy, 1.6))
                if R.random() < 0.12:                       # burnt-out window: soot above it
                    cube(bmb, (px + nx * 0.01, py + ny * 0.01, z + 2.0), (sx * 1.1 + 0.01, sy * 1.1 + 0.01, 0.9))
    INK.append(link("Tower windows", bmd, [M["win"]]))
    INK.append(link("Tower windows glass", bmg, [M["wglass"]]))
    link("Tower soot", bmb, [M["soot"]], RUIN)
    if strips:                                             # the new city: thin light strips up the corners
        bm = bmesh.new()
        for sx in (-1, 1):
            for sy in (-1, 1):
                cube(bm, (cx + sx * (w / 2 + 0.05), cy + sy * (d / 2 + 0.05), h / 2), (0.12, 0.12, h))
        link("Light strips", bm, [M["strip"]], INTACT)
        bm = bmesh.new()
        for sx in (-1, 1):
            for sy in (-1, 1):
                cube(bm, (cx + sx * (w / 2 + 0.05), cy + sy * (d / 2 + 0.05), h / 2), (0.12, 0.12, h))
        INK.append(link("Dead strips", bm, [M["strip_dead"]], RUIN))
    for shade in ("ivy", "ivy2", "ivy3"):                  # ivy: only after the fall
        bm = bmesh.new()
        for nx, ny in FACES:
            span = w if nx == 0 else d
            axis = "y" if nx == 0 else "x"
            for s in range(int(span / 1.5)):
                if R.random() < 0.35:
                    continue
                u = R.uniform(-span / 2 + 0.5, span / 2 - 0.5)
                if R.random() < 0.5:
                    z0, z1 = 0.0, R.uniform(0.15, 0.6) * h
                else:
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
                    # keep the big screen clear
                    if not (abs(px - SCREEN_C[0]) < 1.0 and abs(py) < SCREEN_W / 2 + 0.6 and
                            abs(z - SCREEN_C[2]) < SCREEN_H / 2 + 0.6) and R.random() < 0.8:
                        blob(bm, (px, py, z), axis, r)
                    z += R.uniform(0.35, 0.9)
        o = link("Ivy " + shade, bm, [M[shade]], RUIN)
        IVY.append(o)
    for j in range(2):
        INK.append(P.sphere((cx + R.uniform(-w / 3, w / 3), cy + R.uniform(-d / 3, d / 3), h + 0.6), R.uniform(1.0, 1.6),
                            M["leaf"], "Roof tree", scale=(1, 1, 0.8)))
        RUIN.append(INK[-1])


def vault(x0, x1, cy, radius, z0):
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
            cube(bm, (p0 + p1) / 2, (0.16, 0.22, d.length + 0.02), d.to_track_quat("Z", "X").to_matrix().to_4x4())
    INK.append(link("Vault iron", bm, [M["iron"]]))
    nx = int((x1 - x0) / 0.5)
    ny = int(math.pi * radius / 0.5)
    keep = {k: bmesh.new() for k in ("pane", "pane2", "pane3")}       # panes that survive
    lost = {k: bmesh.new() for k in ("pane", "pane2", "pane3")}       # panes that break in the fall
    shards = bmesh.new()
    shell_keep, shell_lost = bmesh.new(), bmesh.new()   # dark backing between the panes, cell by cell
    for i in range(nx):
        x = x0 + (i + 0.5) * (x1 - x0) / nx
        # broken glass comes in patches (holes), more towards the far end
        for k in range(ny):
            a = math.pi * (k + 0.5) / ny
            n = Vector((0, math.cos(a), math.sin(a)))
            c = Vector((x, cy, z0)) + n * (radius + 0.03)
            q = n.to_track_quat("Z", "X").to_matrix().to_4x4()
            rr = R.random()
            key = "pane3" if rr < 0.06 else "pane2" if rr < 0.17 else "pane"
            hole = (math.sin(x * 0.45 + 1.3) * math.cos(a * 3.1 + x * 0.2) > 0.35) or R.random() < 0.08
            cube((lost if hole else keep)[key], c, ((x1 - x0) / nx * 0.86, math.pi * radius / ny * 0.86, 0.015), q)
            quad(shell_lost if hole else shell_keep, Vector((x, cy, z0)) + n * (radius - 0.01),
                 (x1 - x0) / nx * 1.02, math.pi * radius / ny * 1.02, q)
            if hole and R.random() < 0.5:                # its pieces on the floor below
                p = Vector((x + R.uniform(-0.6, 0.6), c.y * 0.9 + R.uniform(-0.6, 0.6), 0.05))
                if abs(p.y - cy) < radius - 0.6:
                    for s in range(3):
                        cube(shards, p + Vector((R.uniform(-0.3, 0.3), R.uniform(-0.3, 0.3), 0)),
                             (R.uniform(0.08, 0.3), R.uniform(0.06, 0.25), 0.012),
                             Matrix.Rotation(R.uniform(0, 6.3), 4, "Z") @ Matrix.Rotation(R.uniform(-0.2, 0.2), 4, "X"))
    link("Vault bars", shell_keep, [M["bars"]])
    link("Vault bars lost", shell_lost, [M["bars"]], INTACT)
    M["bars"].use_backface_culling = True
    for key in keep:
        link("Vault " + key, keep[key], [M[key]])
        link("Vault lost " + key, lost[key], [M[key]], INTACT)
    link("Glass shards", shards, [M["shard"]], RUIN)
    for sy in (-1, 1):
        y = cy + sy * radius
        INK.append(P.box(((x0 + x1) / 2, y, z0 / 2), (x1 - x0, 0.6, z0), M["wall"], "Arcade wall"))
        INK.append(P.box(((x0 + x1) / 2, y, z0 + 0.1), (x1 - x0, 0.8, 0.25), M["wall2"], "Arcade cornice"))
        for i in range(na):
            x = x0 + i * (x1 - x0) / (na - 1)
            INK.append(P.box((x, y, z0 + 0.8), (0.5, 0.7, 1.4), M["wall"], "Pillar"))
            INK.append(P.box((x, y - sy * 0.31, z0 / 2), (1.2, 0.04, z0 * 0.7), M["win"], "Arcade door"))
        # new city: a light line along the cornice
        INTACT.append(P.box(((x0 + x1) / 2, y - sy * 0.42, z0 - 0.15), (x1 - x0, 0.06, 0.08), M["strip"], "Arcade light"))


def tree(x, y, s=1.0):
    INK.append(P.cyl((x, y, 0), (x, y, 2.2 * s), 0.12 * s, M["trunk"], "Trunk"))
    for j in range(5):
        INK.append(P.sphere((x + R.uniform(-0.8, 0.8) * s, y + R.uniform(-0.8, 0.8) * s, (2.6 + R.uniform(0, 1.2)) * s),
                            R.uniform(0.8, 1.2) * s, M["leaf" if j % 2 else "leaf2"], "Leaves"))


def car(x, y, rz, m, group, wreck=False):
    """Low rounded city car: body + cabin + 4 wheels in one mesh. wreck: tilted, sooty, no glass."""
    bm = bmesh.new()
    cube(bm, (0, 0, 0.55), (4.0, 1.8, 0.6))
    cube(bm, (-0.2, 0, 1.1), (2.2, 1.6, 0.55))
    for wx in (-1.3, 1.3):
        for wy in (-0.85, 0.85):
            bmesh.ops.create_cone(bm, cap_ends=True, segments=12, radius1=0.36, radius2=0.36, depth=0.25,
                                  matrix=Matrix.Translation((wx, wy, 0.36)) @ Matrix.Rotation(math.radians(90), 4, "X"))
    o = link("Car" + (" wreck" if wreck else ""), bm, [M[m], M["tyre"], M["cglass"]], group)
    for p in o.data.polygons:
        if p.center.z < 0.75 and (abs(p.center.x) > 1.0 and abs(p.center.y) > 0.7):
            p.material_index = 1
        elif p.center.z > 0.85 and not wreck and abs(p.normal.z) < 0.5:
            p.material_index = 2
    if wreck:
        o.data.materials[0] = M["soot"] if R.random() < 0.5 else M[m]
    o.location = (x, y, 0)
    o.rotation_euler = (R.uniform(-0.12, 0.12) if wreck else 0, R.uniform(-0.15, 0.15) if wreck else 0, rz)
    INK.append(o)
    return o


def screen(mat):
    """Big screen on the tower face at the end of the street (facing -X, down the arcade)."""
    x, y, z = SCREEN_C
    INK.append(P.box((x + 0.15, y, z), (0.3, SCREEN_W + 0.6, SCREEN_H + 0.6), M["frame"], "Screen frame"))
    s = P.plane((x - 0.02, y, z), (SCREEN_W, SCREEN_H), mat, rot=(math.radians(90), 0, math.radians(-90)),
                name="Big screen")
    return s


def build(screen_mat):
    sc = bpy.context.scene
    mats()
    INK.append(P.box((0, 0, -0.1), (400, 400, 0.2), M["road"], "Ground"))
    for y in (-8.5, 8.5, -17.5, 17.5):
        INK.append(P.box((0, y, 0.06), (200, 3.0, 0.12), M["walk"], "Pavement"))
    for y in (-12.6, -11.4, 11.4, 12.6):
        P.box((0, y, 0.01), (200, 0.08, 0.02), M["iron"], "Rail")
    bmp = {k: bmesh.new() for k in ("paving", "paving2")}
    for i in range(-30, 30):
        cube(bmp["paving" if i % 2 else "paving2"], (i + 0.5, 0, 0.02), (0.96, 13, 0.04))
    for k, b in bmp.items():
        link("Arcade paving", b, [M[k]])
    vault(**VAULT)
    towers = [(-18, 27, 14, 12, 62, "conc"), (6, 29, 12, 12, 48, "conc2"), (24, 26, 14, 10, 70, "conc"),
              (-14, -27, 12, 12, 54, "conc2"), (14, -28, 16, 12, 40, "conc"), (42, 0, 12, 14, 58, "conc2"),
              (-44, 4, 12, 16, 44, "conc"), (2, 54, 18, 14, 80, "conc"), (-32, 52, 14, 14, 36, "conc2"),
              (34, -30, 12, 12, 64, "conc2"), (-40, -30, 14, 12, 50, "conc")]
    for t in towers:
        tower(*t[:5], m=t[5], strips=True)
    for gx in range(-90, 91, 15):
        for gy in range(-90, 91, 15):
            x, y = gx + R.uniform(-2, 2), gy + R.uniform(-2, 2)
            if abs(y) < 22 or any(abs(x - t[0]) < 12 and abs(y - t[1]) < 12 for t in towers):
                continue
            tower(x, y, R.uniform(8, 11), R.uniform(8, 11), R.uniform(12, 26), m=R.choice(("conc", "conc2")))
    for x in range(-26, 27, 6):
        tree(x, 3.4 if (x // 6) % 2 else -3.4, R.uniform(0.8, 1.1))
    for x in range(-28, 29, 6):                            # lamp posts: upright before, bent after
        INTACT.append(P.cyl((x, -5.0, 0), (x, -5.0, 4.0), 0.07, M["iron"], "Lamp post"))
        INTACT.append(P.sphere((x, -5.0, 4.1), 0.18, M["strip"], "Lamp"))
        a = R.uniform(0.15, 0.5) * R.choice((-1, 1))
        top = Vector((x + 4.0 * math.sin(a) * 0.4, -5.0 + 4.0 * math.sin(a), 4.0 * math.cos(a)))
        RUIN.append(P.cyl((x, -5.0, 0), tuple(top), 0.07, M["iron"], "Lamp post bent"))
        RUIN.append(P.sphere(tuple(top), 0.18, M["iron"], "Lamp dead"))
        INK.extend(INTACT[-2:-1] + RUIN[-2:])
    for k, (x, y, rz, m) in enumerate([(-22, 12, 0, "car1"), (-9, -12, 3.14, "car2"), (3, 12, 0, "car3"),
                                       (17, -12, 3.14, "car1"), (29, 12, 0.0, "car2"), (-35, -12, 3.14, "car3")]):
        car(x, y, rz, m, INTACT)
        car(x + R.uniform(-2, 2), y + R.uniform(-1.5, 1.5), rz + R.uniform(-0.8, 0.8), m, RUIN, wreck=True)
    car(-4.0, -4.2, 0.4, "car2", RUIN, wreck=True)          # wrecks inside the arcade
    car(19.0, 4.1, -0.3, "car1", RUIN, wreck=True)
    bm = bmesh.new()                                       # rubble heaps along the arcade walls
    for k in range(70):
        x = R.uniform(-29, 29)
        y = R.choice((-1, 1)) * R.uniform(4.6, 6.0)
        cube(bm, (x, y, R.uniform(0.05, 0.35)), (R.uniform(0.2, 0.9), R.uniform(0.2, 0.7), R.uniform(0.15, 0.5)),
             Matrix.Rotation(R.uniform(0, 6.3), 4, "Z") @ Matrix.Rotation(R.uniform(-0.4, 0.4), 4, "X"))
    INK.append(link("Rubble", bm, [M["rubble"]], RUIN))
    scr = screen(screen_mat)
    world(sc)
    sun = bpy.data.objects.new("Sun", bpy.data.lights.new("Sun", "SUN"))
    sc.collection.objects.link(sun)
    sun.data.energy = 2.6
    sun.data.color = (1.0, 0.9, 0.78)
    sun.data.angle = 0.02
    sun.rotation_euler = (math.radians(55), 0, math.radians(-120))
    return dict(M=M, INK=INK, IVY=IVY, INTACT=INTACT, RUIN=RUIN, SCREEN=scr, SUN=sun)


def world(sc):
    """The camera sees a peach gradient; the scene is lit by a neutral grey ambient + a warm low sun."""
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


def ivy_ink():
    """Ivy gets its own dark-green outline (the reference draws leaves with darker green, not black)."""
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
