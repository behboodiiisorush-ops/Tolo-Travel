"""«خیاط کوچولو» — style test: 1930s hand-drawn cartoon look (rubber-hose limbs, flat cel colours, black ink),
built in Blender. Renders only the character layer (transparent film); post.py puts it on the painted
background plate, adds line boil, film grain, gate weave and the captions.

    ../cast/bpy.sh scene.py               # render all drawings (on twos) into layer/
    ../cast/bpy.sh scene.py --still 70    # one drawing, for checking

Original character (not any studio's): a small tailor with a beret, curly moustache, bow tie and vest.
Story beat (Grimm folk tale): flies on his jam bread, one swat with the cloth he is sewing -> seven flies.
"""
import bpy, bmesh, math, json, os, sys
from mathutils import Vector, Matrix, Euler

HERE = os.path.dirname(os.path.abspath(__file__))
FPS, N = 24, 156
W, H = 720, 1280
ORTHO = 3.75
PITCH = 16.0                          # camera looks down a little so the table top reads
CAM_C = Vector((0.0, 0.0, 2.02))      # point at the centre of the frame
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]

# ---------------------------------------------------------------- scene
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)
sc = bpy.context.scene
sc.render.engine = "BLENDER_EEVEE"
sc.eevee.taa_render_samples = 16
sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = W, H, 100
sc.render.film_transparent = True
sc.render.fps = FPS
sc.view_settings.view_transform = "Standard"
sc.view_settings.look = "None"
sc.render.image_settings.file_format = "PNG"
sc.render.image_settings.color_mode = "RGBA"
world = bpy.data.worlds.new("w")
world.use_nodes = True
world.node_tree.nodes["Background"].inputs[0].default_value = (0, 0, 0, 1)
world.node_tree.nodes["Background"].inputs[1].default_value = 0.0
sc.world = world
COL = sc.collection


def lin(rgb):
    return tuple(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in rgb)


def toon(name, rgb, shade=(0.74, 0.70, 0.82)):
    """Flat colour with one hard shadow band (Shader to RGB -> constant ramp -> emission)."""
    rgb = lin(rgb)
    shade = lin(shade)
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    d = nt.nodes.new("ShaderNodeBsdfDiffuse")
    s2r = nt.nodes.new("ShaderNodeShaderToRGB")
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    em = nt.nodes.new("ShaderNodeEmission")
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    ramp.color_ramp.interpolation = "CONSTANT"
    e = ramp.color_ramp.elements
    e[0].position, e[1].position = 0.0, 0.16
    e[0].color = (rgb[0] * shade[0], rgb[1] * shade[1], rgb[2] * shade[2], 1)
    e[1].color = (rgb[0], rgb[1], rgb[2], 1)
    nt.links.new(d.outputs[0], s2r.inputs[0])
    nt.links.new(s2r.outputs[0], ramp.inputs[0])
    nt.links.new(ramp.outputs[0], em.inputs[0])
    nt.links.new(em.outputs[0], out.inputs[0])
    return m


def flat(name, rgb):
    rgb = lin(rgb)
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs[0].default_value = (*rgb, 1)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    nt.links.new(em.outputs[0], out.inputs[0])
    return m


def ink_mat(name, black_when_backfacing):
    """Inverted-hull ink: black on one side of the hull, transparent on the other."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    g = nt.nodes.new("ShaderNodeNewGeometry")
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs[0].default_value = (0.035, 0.03, 0.03, 1)
    mix = nt.nodes.new("ShaderNodeMixShader")
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    nt.links.new(g.outputs["Backfacing"], mix.inputs[0])
    if black_when_backfacing:
        nt.links.new(tr.outputs[0], mix.inputs[1]); nt.links.new(em.outputs[0], mix.inputs[2])
    else:
        nt.links.new(em.outputs[0], mix.inputs[1]); nt.links.new(tr.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs[0])
    return m


INK_MESH = ink_mat("ink_mesh", False)     # solidify with flipped normals
INK_CURVE = ink_mat("ink_curve", True)     # plain fatter copy of a tube
LINE = 0.016                               # ~4.5 px


def ink(o, t=LINE):
    o.data.materials.append(INK_MESH)
    sd = o.modifiers.new("Outline", "SOLIDIFY")
    sd.thickness = t
    sd.offset = 1.0
    sd.use_flip_normals = True
    sd.use_rim = False
    sd.material_offset = len(o.data.materials) - 1


def blob(name, loc, size, mat, parent=None, rot=(0, 0, 0), half=False, lw=LINE, line=True, seg=40):
    """Ellipsoid with the size baked into the mesh (so the ink stays even)."""
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=seg // 2, radius=1.0)
    for v in bm.verts:
        if half and v.co.z > 0:
            v.co.z = 0.0
        v.co = Vector((v.co.x * size[0], v.co.y * size[1], v.co.z * size[2]))
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = True
    o = bpy.data.objects.new(name, me)
    COL.objects.link(o)
    o.data.materials.append(mat)
    o.parent = parent
    o.location = loc
    o.rotation_euler = rot
    if line:
        ink(o, lw)
    return o


def box(name, loc, size, mat, r=0.04, parent=None, line=True):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co = Vector((v.co.x * size[0], v.co.y * size[1], v.co.z * size[2]))
    bmesh.ops.bevel(bm, geom=bm.edges[:] + bm.verts[:], offset=r, segments=4, affect="EDGES")
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    COL.objects.link(o)
    o.data.materials.append(mat)
    o.parent = parent
    o.location = loc
    if line:
        ink(o)
    return o


def empty(name, parent=None, loc=(0, 0, 0)):
    e = bpy.data.objects.new(name, None)
    COL.objects.link(e)
    e.parent = parent
    e.location = loc
    return e


def tube(name, mat, radius):
    """Rubber-hose limb: a mesh tube rebuilt every drawing (set_tube), inked like every other mesh."""
    me = bpy.data.meshes.new(name)
    o = bpy.data.objects.new(name, me)
    COL.objects.link(o)
    me.materials.append(mat)
    o["radius"] = radius
    ink(o)
    return [o]


def set_tube(o, ctrl, ring=14, samples=20):
    """Sweep a circle along a smooth curve through the control points (Catmull-Rom)."""
    r = o["radius"]
    P = [ctrl[0]] + list(ctrl) + [ctrl[-1]]
    pts = []
    for i in range(1, len(P) - 2):
        for k in range(samples // (len(P) - 3) + 1):
            t = k / (samples // (len(P) - 3) + 1)
            p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
            pts.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t
                              + (-p0 + 3 * p1 - 3 * p2 + p3) * t * t * t))
    pts.append(ctrl[-1])
    bm = bmesh.new()
    rings = []
    up = Vector((0, 1, 0))
    for i, p in enumerate(pts):
        tg = (pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]).normalized()
        a = tg.cross(up)
        if a.length < 1e-3:
            a = tg.cross(Vector((1, 0, 0)))
        a.normalize()
        b = tg.cross(a).normalized()
        rings.append([bm.verts.new(p + (a * math.cos(2 * math.pi * j / ring) + b * math.sin(2 * math.pi * j / ring)) * r)
                      for j in range(ring)])
    for r0, r1 in zip(rings, rings[1:]):
        for j in range(ring):
            bm.faces.new((r0[j], r0[(j + 1) % ring], r1[(j + 1) % ring], r1[j]))
    for rr, flip in ((rings[0], True), (rings[-1], False)):
        f = bm.faces.new(rr[::-1] if flip else rr)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    o.data.clear_geometry()
    bm.to_mesh(o.data)
    bm.free()
    for p in o.data.polygons:
        p.use_smooth = True


# ---------------------------------------------------------------- palette (warm 1930s colour)
SKIN = toon("skin", (1.0, 0.80, 0.62))
VEST = toon("vest", (0.20, 0.50, 0.33))
SHIRT = toon("shirt", (0.98, 0.95, 0.86))
BERET = toon("beret", (0.72, 0.13, 0.12))
HAIR = toon("hair", (0.16, 0.10, 0.07))
NOSE = toon("nose", (0.95, 0.50, 0.42))
MOUTH = flat("mouth", (0.38, 0.05, 0.06))
TONGUE = toon("tongue", (0.95, 0.45, 0.45))
WHITE = toon("eyewhite", (1.0, 0.99, 0.95), shade=(0.9, 0.9, 0.95))
BLACK = flat("pupil", (0.03, 0.025, 0.025))
BOW = toon("bow", (0.85, 0.20, 0.18))
GLOVE = toon("glove", (1.0, 0.99, 0.95), shade=(0.82, 0.82, 0.9))
WOOD = toon("wood", (0.62, 0.36, 0.18))
WOOD_D = toon("wood_d", (0.45, 0.24, 0.11))
BREAD = toon("bread", (0.90, 0.64, 0.33))
CRUMB = toon("crumb", (0.98, 0.86, 0.60))
JAM = toon("jam", (0.78, 0.07, 0.13))
JAR = toon("jar", (0.80, 0.30, 0.35))
LID = toon("lid", (0.92, 0.75, 0.25))
CLOTH = toon("cloth", (0.22, 0.38, 0.80))
STEEL = toon("steel", (0.80, 0.82, 0.86))
WING = toon("wing", (0.80, 0.90, 1.0), shade=(0.85, 0.88, 0.95))
FLYC = toon("flyc", (0.22, 0.24, 0.30))
DUST = toon("dust", (1.0, 0.97, 0.88), shade=(0.88, 0.85, 0.80))
THREAD = flat("thread", (0.85, 0.15, 0.15))

# ---------------------------------------------------------------- light + camera
sun = bpy.data.lights.new("sun", "SUN")
sun.energy = 3.0
sun.use_shadow = False
so = bpy.data.objects.new("sun", sun)
COL.objects.link(so)
so.rotation_euler = Vector((-1.0, -1.4, 1.6)).to_track_quat("-Z", "Y").to_euler()
so.rotation_euler = (Vector((0, 0, 0)) - Vector((-1.0, -1.4, 1.6))).to_track_quat("-Z", "Y").to_euler()

cam = bpy.data.cameras.new("cam")
cam.type = "ORTHO"
cam.ortho_scale = ORTHO
co = bpy.data.objects.new("cam", cam)
COL.objects.link(co)
sc.camera = co
p = math.radians(PITCH)
co.location = CAM_C + Vector((0, -12 * math.cos(p), 12 * math.sin(p)))
co.rotation_euler = (math.radians(90 - PITCH), 0, 0)
cam.clip_end = 40

# ---------------------------------------------------------------- table + props
TABLE_Z = 1.0
box("table_top", (0, -0.05, TABLE_Z - 0.06), (3.4, 1.2, 0.12), WOOD, r=0.03)
box("table_front", (0, -0.62, 0.45), (3.3, 0.06, 1.0), WOOD_D, r=0.02)
BREAD_C = Vector((0.56, -0.02, TABLE_Z))
box("bread", BREAD_C + Vector((0, 0, 0.05)), (0.40, 0.30, 0.10), BREAD, r=0.045)
box("bread_in", BREAD_C + Vector((0, 0, 0.088)), (0.34, 0.24, 0.03), CRUMB, r=0.012, line=False)
blob("jam", BREAD_C + Vector((0.02, 0.0, 0.104)), (0.14, 0.10, 0.028), JAM, lw=0.01)
jar = blob("jar", (1.02, 0.18, TABLE_Z + 0.16), (0.13, 0.13, 0.17), JAR)
blob("lid", (1.02, 0.18, TABLE_Z + 0.33), (0.135, 0.135, 0.04), LID, lw=0.012)
blob("spool", (-0.95, 0.15, TABLE_Z + 0.08), (0.07, 0.07, 0.09), THREAD, lw=0.012)
blob("scissor_a", (-1.0, -0.2, TABLE_Z + 0.015), (0.18, 0.03, 0.012), STEEL, rot=(0, 0, 0.4), lw=0.01)
blob("scissor_b", (-1.0, -0.2, TABLE_Z + 0.015), (0.18, 0.03, 0.012), STEEL, rot=(0, 0, -0.4), lw=0.01)

# ---------------------------------------------------------------- the tailor
BODY_REST = Vector((0, 0.78, 1.36))
body = empty("body", loc=BODY_REST)
blob("torso", (0, 0, 0), (0.48, 0.38, 0.62), VEST, parent=body)
blob("shirt_front", (0, -0.07, 0.06), (0.24, 0.34, 0.52), SHIRT, parent=body, lw=0.012)
for sx in (-1, 1):
    blob("bow_%d" % sx, (sx * 0.075, -0.36, 0.50), (0.08, 0.04, 0.055), BOW, parent=body,
         rot=(0, sx * 0.25, 0), lw=0.012)
    for i, z in enumerate((0.30, 0.12, -0.06)):
        blob("button_%d_%d" % (sx, i), (sx * 0.20, -0.35, z), (0.025, 0.012, 0.025), LID, parent=body,
             lw=0.008)
blob("bow_knot", (0, -0.38, 0.50), (0.03, 0.03, 0.035), BOW, parent=body, lw=0.01)

head = empty("head", parent=body, loc=(0, 0, 0.95))
blob("skull", (0, 0, 0), (0.5, 0.47, 0.48), SKIN, parent=head)
for sx in (-1, 1):
    blob("ear_%d" % sx, (sx * 0.47, 0.02, 0.02), (0.09, 0.06, 0.13), SKIN, parent=head)
    blob("hair_%d" % sx, (sx * 0.40, 0.12, 0.17), (0.12, 0.17, 0.12), HAIR, parent=head, rot=(0, sx * 0.5, 0))
blob("beret", (0.05, 0.02, 0.40), (0.44, 0.42, 0.13), BERET, parent=head, rot=(0, 0.2, 0))
blob("beret_stem", (0.09, 0.02, 0.535), (0.04, 0.04, 0.06), BERET, parent=head, lw=0.01)
nose = blob("nose", (0, -0.49, -0.05), (0.105, 0.09, 0.085), NOSE, parent=head)
EYES, PUPILS, BROWS, STACHE = [], [], [], []
for sx in (-1, 1):
    e = blob("eye_%d" % sx, (sx * 0.15, -0.43, 0.11), (0.115, 0.07, 0.165), WHITE, parent=head, lw=0.012)
    EYES.append(e)
    pp = blob("pupil_%d" % sx, (sx * 0.13, -0.50, 0.08), (0.05, 0.02, 0.07), BLACK, parent=head, line=False)
    blob("glint_%d" % sx, (0.018, -0.012, 0.03), (0.014, 0.008, 0.018), flat("glint", (1, 1, 1)), parent=pp,
         line=False)
    PUPILS.append(pp)
    BROWS.append(blob("brow_%d" % sx, (sx * 0.15, -0.44, 0.33), (0.10, 0.03, 0.026), HAIR, parent=head,
                      line=False))
    STACHE.append(blob("stache_%d" % sx, (sx * 0.11, -0.49, -0.15), (0.12, 0.04, 0.045), HAIR, parent=head,
                       rot=(0, sx * 0.35, 0), lw=0.01))
    blob("curl_%d" % sx, (sx * 0.22, -0.46, -0.10), (0.035, 0.03, 0.035), HAIR, parent=head, lw=0.008)
mouth = blob("mouth", (0, -0.45, -0.21), (0.13, 0.05, 0.10), MOUTH, parent=head, half=True, lw=0.012)
blob("tongue", (0, -0.03, -0.06), (0.07, 0.03, 0.035), TONGUE, parent=mouth, line=False)

SHOULDER = {+1: Vector((0.33, -0.04, 0.30)), -1: Vector((-0.33, -0.04, 0.30))}
ARM = {s: tube("arm_%d" % s, SHIRT, 0.062) for s in (-1, 1)}
for s in (-1, 1):                                  # puffed sleeve where the hose arm leaves the body
    blob("sleeve_%d" % s, SHOULDER[s] + Vector((s * 0.04, -0.03, 0.02)), (0.12, 0.11, 0.12), SHIRT, parent=body)
HAND = {}
for s in (-1, 1):
    h = empty("hand_%d" % s)
    blob("palm_%d" % s, (0.07, 0, 0), (0.11, 0.085, 0.10), GLOVE, parent=h)
    blob("thumb_%d" % s, (0.06, -0.05, 0.08), (0.04, 0.035, 0.06), GLOVE, parent=h, rot=(0.3, 0, 0.3))
    blob("cuff_%d" % s, (-0.03, 0, 0), (0.05, 0.11, 0.11), GLOVE, parent=h)
    HAND[s] = h

# needle + thread (while sewing), the blue cloth he is sewing
needle = blob("needle", (0.10, 0, 0.06), (0.012, 0.012, 0.09), STEEL, rot=(0.0, -0.5, 0), lw=0.008)
needle.parent = HAND[-1]
th_cu = bpy.data.curves.new("thread", "CURVE")
th_cu.dimensions = "3D"; th_cu.bevel_depth = 0.006
th_sp = th_cu.splines.new("POLY"); th_sp.points.add(1)
thread = bpy.data.objects.new("thread", th_cu); COL.objects.link(thread); th_cu.materials.append(THREAD)
cloth = box("cloth", (0, 0, 0), (0.62, 0.44, 0.035), CLOTH, r=0.015)
box("cloth_hem", (0, -0.0, 0.012), (0.50, 0.32, 0.02), toon("hem", (0.34, 0.52, 0.95)), r=0.01,
    parent=cloth, line=False)
CLOTH_REST = Vector((-0.42, -0.05, TABLE_Z + 0.04))

# flies
FLY = []
for i in range(7):
    f = empty("fly_%d" % i)
    blob("fly_body_%d" % i, (0, 0, 0), (0.075, 0.055, 0.05), FLYC, parent=f, lw=0.008)
    blob("fly_head_%d" % i, (0.075, 0, 0.012), (0.04, 0.04, 0.038), BLACK, parent=f, lw=0.008)
    for ey in (-1, 1):
        blob("fly_eye_%d_%d" % (i, ey), (0.095, ey * 0.022, 0.03), (0.018, 0.018, 0.018), BOW, parent=f,
             line=False)
    wl = blob("fly_wl_%d" % i, (-0.01, 0.035, 0.05), (0.05, 0.016, 0.028), WING, parent=f, lw=0.007)
    wr = blob("fly_wr_%d" % i, (-0.01, -0.035, 0.05), (0.05, 0.016, 0.028), WING, parent=f, lw=0.007)
    FLY.append((f, wl, wr))

# dust puffs at the impact
PUFF = [blob("puff_%d" % i, (0, 0, -5), (1, 1, 0.8), DUST, lw=0.012) for i in range(6)]


# ---------------------------------------------------------------- animation helpers
def ease(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def track(keys, f):
    """keys: [(frame, value)], value float or tuple; eased between keys, held outside."""
    if f <= keys[0][0]:
        return keys[0][1]
    for (f0, v0), (f1, v1) in zip(keys, keys[1:]):
        if f <= f1:
            u = ease((f - f0) / max(1e-6, f1 - f0))
            if isinstance(v0, tuple):
                return tuple(a + (b - a) * u for a, b in zip(v0, v1))
            return v0 + (v1 - v0) * u
    return keys[-1][1]


def V(t):
    return Vector(t)


# hand B (screen left) sews, then swats; hand A (screen right) waits by the bread, then thumbs at chest
def hand_b(f):
    if f < 30:
        u = (f % 12) / 12.0
        lift = math.sin(u * math.pi) ** 2
        return V((-0.40 + 0.10 * lift, -0.02, TABLE_Z + 0.08 + 0.42 * lift))
    return V(track([(30, (-0.34, -0.02, TABLE_Z + 0.50)), (44, (-0.34, -0.02, TABLE_Z + 0.50)),
                    (54, (-0.40, -0.05, TABLE_Z + 0.10)), (64, (0.30, 0.30, 3.50)), (67, (0.36, 0.36, 3.62)),
                    (68, (0.50, 0.10, 2.25)), (70, (0.56, -0.02, TABLE_Z + 0.16)),
                    (90, (0.56, -0.02, TABLE_Z + 0.16)), (98, (0.30, -0.05, 1.95)),
                    (106, (-0.42, -0.05, TABLE_Z + 0.10)), (156, (-0.42, -0.05, TABLE_Z + 0.10))], f))


def hand_a(f):
    return V(track([(0, (0.98, -0.12, TABLE_Z + 0.09)), (54, (0.98, -0.12, TABLE_Z + 0.09)),
                    (62, (0.90, -0.10, TABLE_Z + 0.10)), (128, (0.90, -0.10, TABLE_Z + 0.10)),
                    (136, (0.16, 0.36, 1.52)), (156, (0.16, 0.36, 1.52))], f))


BODY = [  # frame, (dx, dz, lean_side, pitch, sx, sy, sz)
    (0, (0, 0, 0, 0.05, 1, 1, 1)), (30, (0, 0, 0, 0.03, 1, 1, 1)), (44, (0, 0, 0, 0.0, 1, 1, 1)),
    (54, (0.04, 0, 0.08, 0.06, 1, 1, 1)), (64, (0.02, 0.06, 0.14, -0.16, 0.94, 0.95, 1.12)),
    (67, (0.02, 0.07, 0.15, -0.18, 0.93, 0.94, 1.14)), (68, (0.05, 0.02, 0.08, 0.20, 0.98, 1.0, 1.06)),
    (70, (0.06, -0.07, 0.06, 0.26, 1.12, 1.08, 0.84)), (76, (0.05, -0.02, 0.05, 0.16, 1.03, 1.02, 0.97)),
    (88, (0.05, 0, 0.05, 0.12, 1, 1, 1)), (100, (0.06, 0, 0.10, 0.14, 1, 1, 1)),
    (104, (0.04, 0.06, 0.04, 0.0, 0.95, 0.95, 1.10)), (110, (0.04, 0.0, 0.05, 0.08, 1, 1, 1)),
    (128, (0.04, 0.0, 0.05, 0.08, 1, 1, 1)), (138, (0, 0.05, -0.04, -0.13, 1.08, 1.16, 1.06)),
    (156, (0, 0.05, -0.04, -0.13, 1.08, 1.16, 1.06))]

HEAD = [  # frame, (yaw, pitch, roll)
    (0, (-0.30, 0.22, 0.05)), (30, (-0.25, 0.20, 0.0)), (36, (0.0, 0.0, 0.0)), (44, (0.0, 0.0, 0.0)),
    (52, (0.45, 0.18, -0.05)), (58, (0.30, -0.10, 0)), (66, (0.25, -0.30, 0.05)), (70, (0.35, 0.30, 0)),
    (90, (0.40, 0.30, 0)), (100, (0.45, 0.34, -0.06)), (126, (0.45, 0.34, -0.06)),
    (136, (-0.10, -0.25, 0.10)), (156, (-0.10, -0.25, 0.10))]

FACE = [  # frame, (eye_open, gaze_x, gaze_z, cross, brow_angle, brow_h, mouth_w, mouth_open, pupil_s)
    (0, (1.0, -0.03, -0.05, 0, 0, 0, 0.9, 0.45, 1)), (12, (1.0, -0.03, -0.05, 0, 0, 0, 0.9, 0.45, 1)),
    (14, (0.1, -0.03, -0.05, 0, 0, 0, 0.9, 0.45, 1)), (16, (1.0, -0.03, -0.05, 0, 0, 0, 0.9, 0.45, 1)),
    (30, (1.0, -0.02, -0.05, 0, 0, 0, 0.9, 0.40, 1)),
    (34, (1.12, 0.0, -0.06, 1.0, -0.30, 0.04, 0.5, 0.30, 0.9)),
    (44, (1.12, 0.0, -0.06, 1.0, -0.30, 0.04, 0.5, 0.30, 0.9)),
    (50, (0.62, 0.04, -0.04, 0, 0.45, -0.03, 0.9, 0.15, 1)),
    (64, (0.55, 0.03, 0.05, 0, 0.50, -0.03, 1.0, 0.18, 1)),
    (68, (0.20, 0.03, 0.0, 0, 0.55, -0.03, 0.8, 0.12, 1)),
    (70, (0.06, 0.0, 0.0, 0, 0.55, -0.03, 0.7, 0.10, 1)), (88, (0.06, 0.0, 0.0, 0, 0.5, -0.03, 0.7, 0.1, 1)),
    (94, (0.50, 0.03, -0.06, 0, -0.20, 0.03, 0.6, 0.20, 1)),
    (102, (1.35, 0.03, -0.06, 0, -0.32, 0.08, 0.55, 1.30, 0.72)),
    (126, (1.35, 0.03, -0.06, 0, -0.32, 0.08, 0.55, 1.30, 0.72)),
    (134, (0.14, 0.0, 0.0, 0, -0.15, 0.05, 1.25, 1.0, 1)), (156, (0.14, 0.0, 0.0, 0, -0.15, 0.05, 1.25, 1.0, 1))]

# seven landing spots under the cloth (on the bread and next to it)
SPOT = [V((0.42, -0.10, 1.125)), V((0.56, 0.06, 1.125)), V((0.68, -0.08, 1.125)), V((0.47, 0.08, 1.125)),
        V((0.73, 0.09, 1.125)), V((0.33, 0.02, 1.02)), V((0.82, -0.06, 1.02))]
LAND = [52, 34, 40, 46, 56, 50, 58]                   # landing frame of each fly
HOME = [V((0.1, -0.1, 2.0)), V((0.7, -0.1, 1.6)), V((0.95, -0.1, 2.3)), V((0.45, -0.1, 2.7)),
        V((1.1, -0.1, 1.8)), V((-0.3, -0.1, 2.6)), V((0.8, -0.1, 3.0))]
ENTER = [None, None, None, 6, 12, 18, 24]             # flies that come in from off-screen
NOSE_TOP = V((0, 0.25, 2.36))


def buzz(i, f):
    c = HOME[i]
    a = f * (0.42 + 0.05 * i) + i * 1.7
    p = c + V((0.28 * math.sin(a), 0.1 * math.cos(a * 0.7), 0.18 * math.sin(a * 1.9 + i)))
    p += V((0.03 * math.sin(f * 2.3 + i * 5), 0, 0.03 * math.cos(f * 2.9 + i)))   # zig-zag
    if ENTER[i] is not None:
        k = ease((f - ENTER[i] + 12) / 12.0)
        p = V((1.9, -0.1, 3.4)).lerp(p, k)
    return p


def fly_state(i, f):
    """position, heading, flying?, dead?"""
    if f >= 70:
        return SPOT[i], 0.6 * i, False, True
    if i == 0:                                   # the cheeky one lands on his nose first
        if f < 22:
            return buzz(0, f), 0.0, True, False
        if f < 30:
            return buzz(0, f).lerp(NOSE_TOP, ease((f - 22) / 8.0)), 0.0, True, False
        if f < 42:
            return NOSE_TOP, math.pi, False, False
        if f < LAND[0]:
            return NOSE_TOP.lerp(SPOT[0], ease((f - 42) / (LAND[0] - 42))) + V((0, 0, 0.25 * math.sin(
                math.pi * (f - 42) / (LAND[0] - 42)))), 0.0, True, False
        return SPOT[0], 2.0, False, False
    if f < LAND[i] - 10:
        return buzz(i, f), 0.0, True, False
    if f < LAND[i]:
        return buzz(i, LAND[i] - 10).lerp(SPOT[i], ease((f - LAND[i] + 10) / 10.0)), 0.0, True, False
    return SPOT[i], 0.9 * i, False, False


def arm_points(S, Hd, s, rest=0.95):
    d = (Hd - S).length
    side = V((s, 0, -0.6)).normalized()
    axis = (Hd - S).normalized() if d > 1e-4 else V((0, 0, -1))
    perp = (side - axis * side.dot(axis))
    perp = perp.normalized() if perp.length > 1e-4 else V((s, 0, 0))
    bow = 0.5 * math.sqrt(max(0.0, rest * rest - d * d)) + 0.06
    C = (S + Hd) * 0.5 + perp * bow
    pts = []
    for k in range(7):
        t = k / 6.0
        pts.append(S * (1 - t) ** 2 + C * (2 * (1 - t) * t) + Hd * t * t)
    return pts


# ---------------------------------------------------------------- pose one drawing
def pose(f):
    bx = track(BODY, f)
    bob = 0.015 * math.sin(f / 12.0 * 2 * math.pi) if f < 30 else 0.0
    body.location = BODY_REST + V((bx[0], 0, bx[1] + bob))
    body.rotation_euler = (bx[3], bx[2], 0)
    body.scale = (bx[4], bx[5], bx[6])
    hy = track(HEAD, f)
    nod = 0.0
    if 104 <= f < 132:                            # counting the flies: seven small nods
        nod = 0.09 * math.sin(math.pi * ((f - 104) % 4) / 4.0)
    head.rotation_euler = Euler((hy[1] + nod, hy[2], hy[0]), "ZXY")

    fc = track(FACE, f)
    eo, gx, gz, cross, ba, bh, mw, mo, ps = fc
    for k, s in enumerate((-1, 1)):
        EYES[k].scale = (1, 1, max(0.06, eo))
        EYES[k].location = (s * 0.15, -0.43, 0.11 - (1 - min(1, eo)) * 0.03)
        PUPILS[k].location = (s * 0.13 + gx - s * cross * 0.06, -0.50 - 0.01 * max(0, eo - 1), 0.08 + gz)
        PUPILS[k].scale = (ps, 1, ps * min(1.0, eo / 0.8))
        PUPILS[k].hide_render = eo < 0.25
        BROWS[k].rotation_euler = (0, -s * ba, 0)
        BROWS[k].location = (s * 0.15, -0.44, 0.33 + bh + 0.05 * max(0, eo - 1))
    mouth.scale = (mw, 1, mo)
    bpy.context.view_layer.update()

    # arms: shoulders follow the body; hands are world targets
    for s, tgt in ((-1, hand_b(f)), (1, hand_a(f))):
        S = body.matrix_world @ SHOULDER[s]
        pts = arm_points(S, tgt, s)
        for o in ARM[s]:
            set_tube(o, pts)
        h = HAND[s]
        d = (pts[-1] - pts[-2]).normalized()
        h.location = tgt
        h.rotation_euler = d.to_track_quat("X", "Z").to_euler()

    # cloth: lies on the table, then in hand B (54..106), smeared on the fast drawing
    held = 54 <= f < 106
    if held:
        hb = HAND[-1]
        cloth.location = hb.location + V((0.08, 0, -0.06))
        cloth.rotation_euler = (0.0, 0.0, 0.0)
        cloth.scale = (1, 1, 1)
        if f == 68:
            cloth.scale = (1.0, 1.0, 1.0)
            cloth.rotation_euler = (0.0, -1.2, 0.0)
            cloth.scale = (2.4, 0.9, 1.0)
        if 64 <= f < 68:
            cloth.rotation_euler = (-1.1, 0.3, 0.2)
        if 70 <= f < 92:
            cloth.location = BREAD_C + V((0.02, -0.02, 0.15))
            cloth.scale = (1.25, 1.2, 0.9)
    else:
        cloth.location = CLOTH_REST if f < 54 else V((-0.42, -0.05, TABLE_Z + 0.04))
        cloth.rotation_euler = (0, 0, 0.1 if f >= 106 else 0)
        cloth.scale = (1, 1, 1)

    # needle + thread while sewing
    needle.hide_render = f >= 54
    thread.hide_render = f >= 54
    if f < 54:
        bpy.context.view_layer.update()
        a = needle.matrix_world.translation
        th_sp.points[0].co = (*CLOTH_REST + V((0.05, -0.05, 0.03)), 1)
        th_sp.points[1].co = (*a, 1)

    # flies
    for i, (o, wl, wr) in enumerate(FLY):
        p, hd, flying, dead = fly_state(i, f)
        o.location = p + V((0, 0, 0.03))
        o.hide_render = False
        if 68 <= f < 92 and not dead:
            o.hide_render = True
        if dead:
            o.hide_render = f < 92                            # under the cloth until he lifts it
            o.rotation_euler = (math.pi, 0, hd)              # legs up
            o.scale = (1.15, 1.15, 0.55)                     # splat
            wl.rotation_euler = (0.9, 0, 0); wr.rotation_euler = (-0.9, 0, 0)
            continue
        o.scale = (1, 1, 1)
        o.rotation_euler = (0, 0, hd + (0.25 * math.sin(f) if flying else 0))
        flap = (0.9 if (f // 2) % 2 == 0 else -0.3) if flying else 0.15
        wl.rotation_euler = (-flap, 0, 0.2)
        wr.rotation_euler = (flap, 0, -0.2)

    # dust puffs
    for k, pf in enumerate(PUFF):
        if 70 <= f < 84:
            u = (f - 70) / 14.0
            ang = k / len(PUFF) * 2 * math.pi + 0.3
            r = 0.34 + 0.35 * ease(u)
            pf.location = BREAD_C + V((math.cos(ang) * r * 1.3, math.sin(ang) * r * 0.5, 0.08 + 0.12 * u))
            sz = (0.07 + 0.11 * math.sin(math.pi * min(1, u * 1.4))) * (1.0 if u < 0.7 else (1 - u) / 0.3)
            pf.scale = (max(0.01, sz),) * 3
            pf.hide_render = sz < 0.012
        else:
            pf.hide_render = True
    bpy.context.view_layer.update()


def screen(p):
    from bpy_extras.object_utils import world_to_camera_view
    v = world_to_camera_view(sc, co, p)
    return [round(v.x * W, 1), round((1 - v.y) * H, 1)]


# ---------------------------------------------------------------- render
OUT = os.path.join(HERE, "layer")
os.makedirs(OUT, exist_ok=True)
if "--still" in argv:
    frames = [int(x) for x in argv[argv.index("--still") + 1].split(",")]
    OUT = os.path.join(HERE, "test")
    os.makedirs(OUT, exist_ok=True)
else:
    frames = list(range(0, N, 2))           # animated on twos, like hand-drawn cartoons
marks = {}
for f in frames:
    pose(f)
    marks[f] = {"head": screen(head.matrix_world.translation), "impact": screen(BREAD_C + V((0, 0, 0.15)))}
    path = os.path.join(OUT, "d_%04d.png" % f)
    if os.path.exists(path) and "--still" not in argv:
        continue
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)
    print("DRAWING", f, flush=True)
if "--still" not in argv:
    json.dump(marks, open(os.path.join(HERE, "marks.json"), "w"))
print("DONE", flush=True)
