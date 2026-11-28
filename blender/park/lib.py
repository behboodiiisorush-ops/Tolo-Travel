"""Building blocks for the bright modern cartoon «پارک» (Blender 5, EEVEE): flat two-band colours, thin ink,
blob meshes with the size baked in, swept tubes for arms/legs/tails, merged meshes for scenery, easing tracks."""
import bpy, bmesh, math
from mathutils import Vector, Matrix, Euler

COL = None
LINE = 0.012


def lin(rgb):
    return tuple(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in rgb)


def hexc(h):
    return tuple(int(h[i:i + 2], 16) / 255 for i in (1, 3, 5))


_MATS = {}


def toon(name, rgb, shade=0.80, cool=(0.92, 0.94, 1.06), band=0.16):
    """Flat colour with one soft-edged shadow band (Shader to RGB -> ramp -> emission)."""
    if isinstance(rgb, str):
        rgb = hexc(rgb)
    if name in _MATS:
        return _MATS[name]
    base = lin(rgb)
    sh = lin(tuple(min(1, c * shade * k) for c, k in zip(rgb, cool)))
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    d = nt.nodes.new("ShaderNodeBsdfDiffuse")
    s2r = nt.nodes.new("ShaderNodeShaderToRGB")
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    em = nt.nodes.new("ShaderNodeEmission")
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    ramp.color_ramp.interpolation = "LINEAR"
    e = ramp.color_ramp.elements
    e[0].position, e[1].position = band - 0.015, band + 0.015
    e[0].color = (*sh, 1)
    e[1].color = (*base, 1)
    nt.links.new(d.outputs[0], s2r.inputs[0])
    nt.links.new(s2r.outputs[0], ramp.inputs[0])
    nt.links.new(ramp.outputs[0], em.inputs[0])
    nt.links.new(em.outputs[0], out.inputs[0])
    _MATS[name] = m
    return m


def flat(name, rgb):
    if isinstance(rgb, str):
        rgb = hexc(rgb)
    if name in _MATS:
        return _MATS[name]
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs[0].default_value = (*lin(rgb), 1)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    nt.links.new(em.outputs[0], out.inputs[0])
    _MATS[name] = m
    return m


def ink_mat():
    if "ink" in _MATS:
        return _MATS["ink"]
    m = bpy.data.materials.new("ink")
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    g = nt.nodes.new("ShaderNodeNewGeometry")
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs[0].default_value = (*lin((0.16, 0.11, 0.10)), 1)
    mix = nt.nodes.new("ShaderNodeMixShader")
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    nt.links.new(g.outputs["Backfacing"], mix.inputs[0])
    nt.links.new(em.outputs[0], mix.inputs[1])
    nt.links.new(tr.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs[0])
    _MATS["ink"] = m
    return m


def ink(o, t=None):
    t = LINE if t is None else t
    o.data.materials.append(ink_mat())
    sd = o.modifiers.new("Outline", "SOLIDIFY")
    sd.thickness = t
    sd.offset = 1.0
    sd.use_flip_normals = True
    sd.use_rim = False
    sd.material_offset = len(o.data.materials) - 1
    return o


def _link(o):
    COL.objects.link(o)
    return o


def sphere_bm(bm, center, size, rot=(0, 0, 0), half=False, seg=28, mat=0):
    tmp = bmesh.new()
    bmesh.ops.create_uvsphere(tmp, u_segments=seg, v_segments=max(8, seg // 2), radius=1.0)
    R = Euler(rot).to_matrix()
    for v in tmp.verts:
        if half and v.co.z > 0:
            v.co.z = 0.0
        v.co = R @ Vector((v.co.x * size[0], v.co.y * size[1], v.co.z * size[2])) + Vector(center)
    for f in tmp.faces:
        f.material_index = mat
        f.smooth = True
    me = bpy.data.meshes.new("_tmp")
    tmp.to_mesh(me)
    tmp.free()
    bm.from_mesh(me)
    bpy.data.meshes.remove(me)


def blob(name, loc, size, mat, parent=None, rot=(0, 0, 0), half=False, lw=None, line=True, seg=28):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    sphere_bm(bm, (0, 0, 0), size, half=half, seg=seg)
    bm.to_mesh(me)
    bm.free()
    o = _link(bpy.data.objects.new(name, me))
    o.data.materials.append(mat)
    o.parent = parent
    o.location = loc
    o.rotation_euler = rot
    if line:
        ink(o, lw)
    return o


def box(name, loc, size, mat, r=0.03, parent=None, line=True, lw=None, rot=(0, 0, 0)):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co = Vector((v.co.x * size[0], v.co.y * size[1], v.co.z * size[2]))
    if r > 0:
        bmesh.ops.bevel(bm, geom=bm.edges[:] + bm.verts[:], offset=r, segments=3, affect="EDGES")
    bm.to_mesh(me)
    bm.free()
    o = _link(bpy.data.objects.new(name, me))
    o.data.materials.append(mat)
    o.parent = parent
    o.location = loc
    o.rotation_euler = rot
    if line:
        ink(o, lw)
    return o


def merged(name, parts, mats, lw=None, line=True):
    """parts: [(center, size, rot, mat_index)] ellipsoids merged into ONE object (cheap scenery)."""
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    for c, s, r, mi in parts:
        sphere_bm(bm, c, s, r, mat=mi, seg=20)
    bm.to_mesh(me)
    bm.free()
    o = _link(bpy.data.objects.new(name, me))
    for m in mats:
        o.data.materials.append(m)
    if line:
        ink(o, lw)
    return o


def empty(name, parent=None, loc=(0, 0, 0)):
    e = _link(bpy.data.objects.new(name, None))
    e.parent = parent
    e.location = loc
    return e


def tube(name, mat, radius, lw=None, taper=1.0):
    me = bpy.data.meshes.new(name)
    o = _link(bpy.data.objects.new(name, me))
    me.materials.append(mat)
    o["radius"] = radius
    o["taper"] = taper
    ink(o, lw)
    return o


def catmull(ctrl, samples=18):
    P = [ctrl[0]] + list(ctrl) + [ctrl[-1]]
    seg = len(P) - 3
    per = max(2, samples // seg)
    pts = []
    for i in range(1, len(P) - 2):
        for k in range(per):
            t = k / per
            p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
            pts.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t
                              + (-p0 + 3 * p1 - 3 * p2 + p3) * t * t * t))
    pts.append(Vector(ctrl[-1]))
    return pts


def set_tube(o, ctrl, ring=12, samples=18):
    """World-space control points -> swept tube mesh (object must sit at the origin, unparented)."""
    r0 = o["radius"]
    tp = o["taper"]
    pts = catmull([Vector(c) for c in ctrl], samples)
    bm = bmesh.new()
    rings = []
    ref = Vector((0, 0, 1))
    for i, p in enumerate(pts):
        tg = pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]
        tg = tg.normalized() if tg.length > 1e-6 else Vector((0, 0, 1))
        a = tg.cross(ref)
        if a.length < 0.2:
            a = tg.cross(Vector((1, 0, 0)))
        a.normalize()
        b = tg.cross(a).normalized()
        r = r0 * (1 + (tp - 1) * i / max(1, len(pts) - 1))
        rings.append([bm.verts.new(p + (a * math.cos(2 * math.pi * j / ring) + b * math.sin(2 * math.pi * j / ring)) * r)
                      for j in range(ring)])
    for ra, rb in zip(rings, rings[1:]):
        for j in range(ring):
            bm.faces.new((ra[j], ra[(j + 1) % ring], rb[(j + 1) % ring], rb[j]))
    bm.faces.new(rings[0][::-1])
    bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    o.data.clear_geometry()
    bm.to_mesh(o.data)
    bm.free()
    for p in o.data.polygons:
        p.use_smooth = True


def limb(S, E, rest, bend_dir, n=6):
    """Bendy limb from S to E: bows towards bend_dir when shorter than its rest length."""
    d = (E - S).length
    axis = (E - S).normalized() if d > 1e-5 else Vector((0, 0, -1))
    perp = bend_dir - axis * bend_dir.dot(axis)
    perp = perp.normalized() if perp.length > 1e-5 else Vector((1, 0, 0))
    bow = 0.5 * math.sqrt(max(0.0, rest * rest - d * d))
    C = (S + E) * 0.5 + perp * bow
    return [S * (1 - t) ** 2 + C * (2 * (1 - t) * t) + E * t * t for t in (k / (n - 1) for k in range(n))]


def ease(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def ease2(x):
    x = min(1.0, max(0.0, x))
    return x * x * x * (x * (6 * x - 15) + 10)


def track(keys, t, fn=ease):
    """[(time, value)] eased between keys, held outside. value: float or tuple."""
    if t <= keys[0][0]:
        return keys[0][1]
    for (t0, v0), (t1, v1) in zip(keys, keys[1:]):
        if t <= t1:
            u = fn((t - t0) / max(1e-6, t1 - t0))
            if isinstance(v0, (tuple, list)):
                return tuple(a + (b - a) * u for a, b in zip(v0, v1))
            return v0 + (v1 - v0) * u
    return keys[-1][1]


def step_track(keys, t):
    """[(time, value)] held values (modes)."""
    v = keys[0][1]
    for tt, vv in keys:
        if t >= tt:
            v = vv
    return v


def yaw_of(d):
    """forward is local -Y; yaw so that R_z(yaw) @ (0,-1,0) points along d."""
    return math.atan2(d.x, -d.y)


def fwd(yaw):
    return Vector((math.sin(yaw), -math.cos(yaw), 0))


def wrap(a):
    return (a + math.pi) % (2 * math.pi) - math.pi


def ring(name, mat, inner=0.82, n=40):
    """Flat annulus (radius 1) for water ripples."""
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    a = [bm.verts.new((math.cos(2 * math.pi * k / n), math.sin(2 * math.pi * k / n), 0)) for k in range(n)]
    b = [bm.verts.new((inner * math.cos(2 * math.pi * k / n), inner * math.sin(2 * math.pi * k / n), 0)) for k in range(n)]
    for k in range(n):
        bm.faces.new((a[k], a[(k + 1) % n], b[(k + 1) % n], b[k]))
    bm.to_mesh(me)
    bm.free()
    o = _link(bpy.data.objects.new(name, me))
    o.data.materials.append(mat)
    return o
