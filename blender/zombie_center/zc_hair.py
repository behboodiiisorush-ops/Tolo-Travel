"""Procedural strand hair (Blender hair curves) — used where no MakeHuman asset matches the canon.

centre_part_hair(ch): Arin's black centre-parted hair. Strands grow from the scalp, part along the head's
mid-line, fall to each side (curtain fringe that stays above the eyes), short at the sides and nape.
The curves object is parented to the head bone, so it follows every head move.
"""
import bpy, bmesh, math, random
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree


def _eval_mesh_world(obj):
    dg = bpy.context.evaluated_depsgraph_get()
    ev = obj.evaluated_get(dg)
    me = ev.to_mesh()
    bm = bmesh.new(); bm.from_mesh(me)
    bm.transform(obj.matrix_world)
    bm.normal_update()
    ev.to_mesh_clear()
    return bm


def _head_frame(rig):
    pb = rig.pose.bones["head"]
    m = rig.matrix_world @ pb.matrix
    head = m.translation.copy()
    tail = rig.matrix_world @ pb.tail
    return head, tail


def _darken_scalp(body, on_scalp, rgb=(0.012, 0.01, 0.01)):
    """Paint the scalp under the strands dark so skin never shows through the part or the hairline."""
    import mpfb_tools as M
    mw = body.matrix_world
    M.paint(body, "zc_scalp", lambda p, n: (1.0, 0, 0) if on_scalp(mw @ p) else (0.0, 0, 0))
    M.recolor(body, lambda nt, c: M.mix(nt, c, rgb, M.attr(nt, "zc_scalp")[0]))


def centre_part_hair(ch, n=20000, seed=1, colour=(0.012, 0.010, 0.010), name=None):
    rnd = random.Random(seed)
    body, rig = ch.body, ch.rig
    bpy.context.view_layer.update()
    bm = _eval_mesh_world(body)
    bvh = BVHTree.FromBMesh(bm)
    hb, ht = _head_frame(rig)
    up = (ht - hb).normalized()
    top_z = max(v.co.z for v in bm.verts)
    # face front = -Y (MPFB). Landmarks from the mesh itself.
    head_vs = [v for v in bm.verts if v.co.z > top_z - 0.26]
    front_y = min(v.co.y for v in head_vs if v.co.z > top_z - 0.12)
    back_y = max(v.co.y for v in head_vs)
    cy = (front_y + back_y) / 2
    cx = sum(v.co.x for v in head_vs) / len(head_vs)
    brow_z = top_z - 0.105                     # eyebrow height (MPFB adult head ~ 0.23 m)
    hairline_front = brow_z + 0.055            # forehead hairline
    ear_z = top_z - 0.16

    def on_scalp(p):
        if p.z < ear_z - 0.035:
            return False
        fy = (p.y - front_y) / max(1e-6, (back_y - front_y))      # 0 = face front, 1 = back of head
        side = abs(p.x - cx)
        if fy < 0.42:                                               # front half: above the hairline only
            hl = hairline_front - 0.03 * min(1.0, side / 0.07)      # hairline dips at the temples
            if side > 0.062 and fy < 0.25:                          # temples / sideburns stop above the ear
                hl = ear_z + 0.025
            return p.z > hl
        if side > 0.07 and p.z < ear_z + 0.02 and fy < 0.62:        # around the ear: no hair
            return False
        return p.z > ear_z - 0.035 - 0.05 * max(0.0, fy - 0.62)     # nape goes a bit lower

    faces = [f for f in bm.faces if on_scalp(f.calc_center_median())]
    _darken_scalp(body, on_scalp)
    areas = [f.calc_area() for f in faces]
    tot = sum(areas)
    roots = []
    for f, a in zip(faces, areas):
        k = a / tot * n
        cnt = int(k) + (1 if rnd.random() < k - int(k) else 0)
        vs = [v.co for v in f.verts]
        for _ in range(cnt):
            u, w = rnd.random(), rnd.random()
            if u + w > 1: u, w = 1 - u, 1 - w
            p = vs[0] + (vs[1] - vs[0]) * u + (vs[-1] - vs[0]) * w
            roots.append((p, f.normal.copy()))

    def push_out(p, off):
        loc, nor, idx, dist = bvh.find_nearest(p)
        if loc is None:
            return p
        d = p - loc
        if d.dot(nor) < off:
            p = loc + nor * off
        return p

    def surf(p):
        loc, nor, idx, dist = bvh.find_nearest(p)
        return loc, nor

    strands = []
    SEG = 12
    for p0, nrm in roots:
        fy = (p0.y - front_y) / (back_y - front_y)
        dx = p0.x - cx
        side = math.copysign(1.0, dx) if abs(dx) > 0.004 else rnd.choice((-1, 1))
        top_region = p0.z > ear_z + 0.06 and abs(dx) < 0.065
        if top_region and fy < 0.5:
            L = 0.095 + 0.02 * rnd.random()          # fringe / top: long, falls to the sides
        elif top_region:
            L = 0.07 + 0.015 * rnd.random()          # crown
        elif fy > 0.6:
            L = 0.04 + 0.01 * rnd.random()           # back / nape
        else:
            L = 0.022 + 0.008 * rnd.random()         # sides above the ears: short
        if fy < 0.35:
            comb = Vector((side * 0.75, -0.35, -0.55))
        elif fy > 0.55:
            comb = Vector((side * 0.15, 0.35, -1.0))
        else:
            comb = Vector((side * 0.9, 0.1, -0.6))
        comb.normalize()
        layer = (0.004 + 0.009 * rnd.random()) if top_region else (0.0025 + 0.004 * rnd.random())
        stop_z = (brow_z + 0.03 + 0.03 * rnd.random()) if fy < 0.35 else -9
        jit = 0.05 if top_region else 0.02
        step = L / (SEG - 1)
        p = p0 + nrm * 0.002
        pts = [p0.copy()]
        for i in range(1, SEG):
            loc, nor = surf(p)
            if nor is None:
                nor = nrm
            t_ = i / (SEG - 1)
            tang = comb - nor * comb.dot(nor)
            d = tang.normalized() * (0.75 + 0.5 * t_) + nor * (0.35 * (1 - t_) ** 3) + Vector((0, 0, -0.35 * t_))
            d += Vector((rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(-1, 1))) * jit
            p = p + d.normalized() * step
            loc, nor = surf(p)
            if loc is not None:                     # hug the head: stay a thin layer above the surface
                h = (p - loc).dot(nor)
                want = layer * min(1.0, 0.3 + t_)
                if h < want or h > want + 0.006:
                    p = loc + nor * (want if h < want else want + 0.006)
            if p.z < stop_z:                       # never below the brows (front) / ear tops (sides)
                p = pts[-1] + (p - pts[-1]) * 0.15
                step *= 0.3
            pts.append(p.copy())
        strands.append(pts)
    bm.free()

    # build the curves object
    cname = name or (body.name + "_HairStrands")
    cv = bpy.data.hair_curves.new(cname) if hasattr(bpy.data, "hair_curves") else bpy.data.curves_new(cname)
    cv.add_curves([SEG] * len(strands))
    flat = [c for s in strands for pt in s for c in pt]
    cv.attributes["position"].data.foreach_set("vector", flat)
    rad = cv.attributes.get("radius") or cv.attributes.new("radius", "FLOAT", "POINT")
    rv = []
    for s in strands:
        for i in range(SEG):
            rv.append(0.00016 * (1 - 0.7 * i / (SEG - 1)))
    rad.data.foreach_set("value", rv)
    ob = bpy.data.objects.new(cname, cv)
    for c in body.users_collection:
        c.objects.link(ob)
    m = bpy.data.materials.new(cname + "_mat"); m.use_nodes = True
    nt = m.node_tree; nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    pb = nt.nodes.new("ShaderNodeBsdfPrincipled")     # EEVEE renders the hair BSDF brown: use Principled
    pb.inputs["Base Color"].default_value = (*colour, 1)
    pb.inputs["Roughness"].default_value = 0.45
    pb.inputs["Specular IOR Level"].default_value = 0.35
    nt.links.new(pb.outputs[0], out.inputs["Surface"])
    cv.materials.append(m)
    # follow the head
    mw = ob.matrix_world.copy()
    ob.parent = rig; ob.parent_type = "BONE"; ob.parent_bone = "head"
    bpy.context.view_layer.update()
    ob.matrix_world = mw
    return ob
