"""The park: lawn, pond with lily pads and reeds, path, trees, bushes, flowers, bench, lamp, hills, clouds, sky.
Pond centre POND (rx, ry); lawn where the kids play is south of it (around the origin)."""
import bpy, math, random
from mathutils import Vector
import lib as L

POND = Vector((0.0, 6.0, 0.0))
PRX, PRY = 3.3, 2.3
WATER_Z = 0.02
GRASS = "#7ccf4e"


def in_pond(p, margin=0.0):
    return ((p.x - POND.x) / (PRX + margin)) ** 2 + ((p.y - POND.y) / (PRY + margin)) ** 2 < 1.0


def ellipse_mesh(name, c, rx, ry, z, mat, n=72, line=True, lw=None):
    import bmesh
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    vs = [bm.verts.new((c.x + rx * math.cos(2 * math.pi * k / n), c.y + ry * math.sin(2 * math.pi * k / n), z))
          for k in range(n)]
    bm.faces.new(vs)
    bmesh.ops.solidify(bm, geom=bm.faces[:], thickness=0.01)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bm.to_mesh(me)
    bm.free()
    o = L._link(bpy.data.objects.new(name, me))
    o.data.materials.append(mat)
    if line:
        L.ink(o, lw)
    return o


def sky_world():
    w = bpy.data.worlds.new("sky")
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
    e = ramp.color_ramp.elements
    e[0].position, e[1].position = 0.0, 0.45
    e[0].color = (*L.lin(L.hexc("#d8f1ff")), 1)
    e[1].color = (*L.lin(L.hexc("#5fb4f2")), 1)
    nt.links.new(tc.outputs["Window"], sep.inputs[0])
    nt.links.new(sep.outputs[1], ramp.inputs[0])
    nt.links.new(ramp.outputs[0], bg.inputs[0])
    amb.inputs[0].default_value = (0.25, 0.25, 0.25, 1)
    amb.inputs[1].default_value = 1.0
    nt.links.new(lp.outputs["Is Camera Ray"], mix.inputs[0])
    nt.links.new(amb.outputs[0], mix.inputs[1])
    nt.links.new(bg.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs[0])
    return w


def build():
    rnd = random.Random(3)
    grass = L.toon("grass", GRASS, shade=0.86)
    grass_d = L.toon("grass_d", "#69b944", shade=0.86)
    water = L.toon("water", "#4fb7ec", shade=0.9)
    water_l = L.flat("water_l", "#8fd8fb")
    sand = L.toon("sand", "#f2dc9b")
    path = L.toon("path", "#f5e2b0")
    bark = L.toon("bark", "#9a6235")
    leaves = [L.toon("leaf%d" % i, c) for i, c in enumerate(("#3fae4a", "#55c055", "#2f9a45", "#6ccf5a"))]
    bush = L.toon("bush", "#3da44d")
    pad = L.toon("pad", "#4caf50")
    reed = L.toon("reed", "#6a9e3a")
    cat = L.toon("cattail", "#8a5a2e")
    petals = [L.toon("pet%d" % i, c, shade=0.9) for i, c in
              enumerate(("#ff6b8b", "#ffd23f", "#ffffff", "#b77cff", "#ff9a3c"))]
    yel = L.toon("pet_c", "#ffcf33")
    wood = L.toon("bench", "#c47a3f")
    iron = L.toon("iron", "#4a5560")
    lampg = L.flat("lampglass", "#fff6c8")
    hill = [L.toon("hill%d" % i, c, shade=0.92) for i, c in enumerate(("#8fd66a", "#7cc85e", "#a5e07a"))]
    cloud = L.toon("cloud", "#ffffff", shade=0.93, cool=(0.94, 0.97, 1.04))

    # lawn
    ellipse_mesh("lawn", Vector((0, 4, 0)), 60, 60, -0.01, grass, n=96, line=False)
    for k in range(14):                                     # darker mown patches
        c = Vector((rnd.uniform(-14, 14), rnd.uniform(-8, 22), 0))
        if in_pond(c, 1.5):
            continue
        ellipse_mesh("patch%d" % k, c, rnd.uniform(1.2, 2.6), rnd.uniform(0.6, 1.4), -0.004, grass_d, line=False)
    # pond
    ink_c = L.flat("pond_ink", "#2d4a22")
    ellipse_mesh("shore_line", POND, PRX + 0.39, PRY + 0.36, -0.004, ink_c, line=False)
    ellipse_mesh("shore", POND, PRX + 0.35, PRY + 0.32, -0.002, sand, line=False)
    ellipse_mesh("water_line", POND, PRX + 0.03, PRY + 0.03, WATER_Z - 0.014, L.flat("water_ink", "#1f6d99"), line=False)
    ellipse_mesh("water", POND, PRX, PRY, WATER_Z - 0.012, water, line=False)
    for k, (dx, dy, rx, ry) in enumerate(((-1.2, 0.5, 0.9, 0.12), (1.0, -0.6, 0.7, 0.1), (0.3, 1.2, 0.6, 0.08))):
        ellipse_mesh("glint%d" % k, POND + Vector((dx, dy, 0)), rx, ry, WATER_Z - 0.0005, water_l, line=False)
    pads = []
    for k, (dx, dy) in enumerate(((2.1, 0.9), (2.5, 0.3), (2.0, -1.3), (1.6, 1.4))):
        pads.append(((POND.x + dx, POND.y + dy, WATER_Z), (0.28, 0.24, 0.012), (0, 0, k), 0))
    L.merged("pads", pads, [pad], lw=0.01)
    for k in range(16):                                    # reeds on the far bank
        a = math.radians(40 + k * 6.5)
        p = POND + Vector((math.cos(a) * (PRX + 0.15), math.sin(a) * (PRY + 0.15), 0))
        r = L.tube("reed%d" % k, reed, 0.018, lw=0.006, taper=0.5)
        h = rnd.uniform(0.7, 1.1)
        L.set_tube(r, [p, p + Vector((0.02, 0.01, h * 0.5)), p + Vector((0.05 * rnd.uniform(-1, 1), 0.03, h))])
        if k % 2 == 0:
            L.blob("cat%d" % k, p + Vector((0.05, 0.03, h - 0.02)), (0.03, 0.03, 0.09), cat, lw=0.006, seg=12)

    # path along the south of the lawn
    import bmesh
    me = bpy.data.meshes.new("path")
    bm = bmesh.new()
    prev = None
    for k in range(61):
        x = -24 + k * 0.8
        y = -3.4 + 0.5 * math.sin(x * 0.25)
        a = bm.verts.new((x, y - 0.8, 0.0))
        b = bm.verts.new((x, y + 0.8, 0.0))
        if prev:
            bm.faces.new((prev[0], a, b, prev[1]))
        prev = (a, b)
    bm.to_mesh(me)
    bm.free()
    po = L._link(bpy.data.objects.new("path", me))
    po.data.materials.append(path)

    # trees
    for k, (x, y, s) in enumerate(((-6.5, 8.5, 1.1), (6.8, 9.0, 1.2), (-8.5, 2.0, 1.0), (8.6, 3.2, 0.95),
                                   (-3.2, 13.0, 1.3), (4.2, 13.5, 1.15), (10.5, -1.2, 1.0), (-10.5, -4.5, 1.1),
                                   (-14, 9, 1.4), (14, 10, 1.3), (0.5, 18, 1.5), (-7, 18, 1.2), (8, 19, 1.3),
                                   (12, -7, 1.0), (-13, -9, 1.1))):
        base = Vector((x, y, 0))
        t = L.tube("trunk%d" % k, bark, 0.16 * s, lw=0.02, taper=0.6)
        L.set_tube(t, [base, base + Vector((0.05, 0, 1.0 * s)), base + Vector((0.1, 0.05, 1.9 * s))])
        parts = []
        top = base + Vector((0.1, 0.05, 2.4 * s))
        for j, (dx, dy, dz, r) in enumerate(((0, 0, 0.3, 1.0), (-0.7, 0.1, -0.15, 0.75), (0.7, -0.1, -0.1, 0.8),
                                             (0.1, 0.0, 0.9, 0.7), (0.0, -0.4, -0.25, 0.7))):
            parts.append(((top.x + dx * s, top.y + dy * s, top.z + dz * s), (r * s, r * s * 0.95, r * s * 0.9),
                          (0, 0, 0), (k + j) % 4))
        L.merged("canopy%d" % k, parts, leaves, lw=0.03)
    # bushes
    for k, (x, y) in enumerate(((-3.0, -5.6), (4.6, 0.2), (-5.5, 5.0), (5.6, 5.6), (-2.5, 9.6), (2.8, 10.0),
                                (9.5, 0.8), (-7.5, -1.0))):
        parts = [((x + dx, y + dy, r * 0.7), (r, r * 0.9, r * 0.8), (0, 0, 0), 0)
                 for dx, dy, r in ((0, 0, 0.6), (0.5, 0.1, 0.45), (-0.5, 0.05, 0.42), (0.1, 0.3, 0.4))]
        L.merged("bush%d" % k, parts, [bush], lw=0.02)
    # flowers (one merged mesh)
    parts = []
    for k in range(260):
        p = Vector((rnd.uniform(-12, 12), rnd.uniform(-6, 16), 0))
        if in_pond(p, 0.6) or abs(p.y + 3.4) < 1.0 or (abs(p.x) < 3.2 and -2.4 < p.y < 3.6):
            continue
        ci = rnd.randrange(5)
        for j in range(5):
            a = 2 * math.pi * j / 5
            parts.append(((p.x + 0.045 * math.cos(a), p.y + 0.045 * math.sin(a), 0.05), (0.04, 0.04, 0.012),
                          (0, 0, 0), ci))
        parts.append(((p.x, p.y, 0.058), (0.025, 0.025, 0.012), (0, 0, 0), 5))
    L.merged("flowers", parts, petals + [yel], line=False)
    # bench + lamp
    for k in range(3):
        L.box("plank%d" % k, (-5.3, -1.6 + k * 0.14, 0.45), (1.5, 0.11, 0.05), wood, r=0.015, lw=0.01)
    for k in range(2):
        L.box("back%d" % k, (-5.3, -1.30, 0.62 + k * 0.16), (1.5, 0.05, 0.1), wood, r=0.015, lw=0.01)
    for dx in (-0.65, 0.65):
        L.box("bleg%d" % (dx > 0), (-5.3 + dx, -1.45, 0.22), (0.07, 0.4, 0.45), iron, r=0.01, lw=0.01)
    LX, LY = -7.2, -2.0
    pole = L.tube("lamp_pole", iron, 0.05, lw=0.012)
    L.set_tube(pole, [Vector((LX, LY, 0)), Vector((LX, LY, 1.4)), Vector((LX, LY, 2.6))])
    L.blob("lamp", (LX, LY, 2.75), (0.17, 0.17, 0.2), lampg, lw=0.012)
    L.blob("lamp_cap", (LX, LY, 2.95), (0.2, 0.2, 0.06), iron, lw=0.012)
    # hills and clouds far away
    for k, (x, y, rx, rz) in enumerate(((-30, 45, 26, 9), (8, 52, 30, 11), (40, 44, 24, 8), (-55, 40, 22, 7))):
        L.blob("hill%d" % k, (x, y, -2), (rx, 10, rz), hill[k % 3], lw=0.06, seg=40)
    for k, (x, z, s) in enumerate(((-22, 17, 3.0), (-4, 20, 3.6), (16, 16, 2.8), (32, 21, 3.2), (-40, 22, 3.0))):
        parts = [((x + dx * s, 58, z + dz * s), (r * s, r * s * 0.6, r * s * 0.7), (0, 0, 0), 0)
                 for dx, dz, r in ((0, 0, 1.0), (1.0, -0.2, 0.75), (-1.0, -0.25, 0.7), (0.4, 0.45, 0.7))]
        L.merged("cloud%d" % k, parts, [cloud], lw=0.05)
    bpy.context.scene.world = sky_world()
