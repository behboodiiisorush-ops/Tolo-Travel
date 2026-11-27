"""Look helpers for the ZC cast: centre-parted hair from a side-swept asset, dark eyes, olive skin race mix."""
import bpy, bmesh
import mpfb_tools as M


def centre_part(hair, keep="neg", lift=0.0):
    """Cut a side-swept hair mesh at x=0, keep one half and mirror it -> symmetric centre part.
    keep: 'neg' keeps x<0 (the character's right side), 'pos' keeps x>0."""
    me = hair.data
    bm = bmesh.new(); bm.from_mesh(me)
    geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
    bmesh.ops.bisect_plane(bm, geom=geom, plane_co=(0, 0, 0), plane_no=(1, 0, 0),
                           clear_outer=(keep == "neg"), clear_inner=(keep == "pos"))
    if lift:   # sweep the front fringe up and out to the side (curtain style), clear of the eyes
        zs = [v.co.z for v in bm.verts]; top = max(zs)
        ys = [v.co.y for v in bm.verts]; front = min(ys)
        brow = top - 0.075
        for v in bm.verts:
            if v.co.y < front + 0.07 and v.co.z < brow:
                k = min(1.0, (brow - v.co.z) / 0.06)
                v.co.z += (brow - v.co.z) * 0.85 * k + 0.004
                v.co.x += (-1 if v.co.x < 0 else 1) * 0.02 * k
                v.co.y += 0.012 * k
    bm.to_mesh(me); bm.free()
    mods = list(hair.modifiers)
    mi = hair.modifiers.new("CentrePart", "MIRROR")
    mi.use_axis[0] = True; mi.use_clip = True; mi.use_mirror_merge = True; mi.merge_threshold = 0.002
    # mirror before deformation (rest pose space): move it to the top of the stack
    with bpy.context.temp_override(object=hair):
        bpy.ops.object.modifier_move_to_index(modifier="CentrePart", index=0)


def dark_eyes(ch, iris=(0.05, 0.028, 0.016), strength=0.85):
    """Darken only the iris (the saturated part of the eye texture) to a dark brown; the white sclera stays."""
    def b(nt, c):
        hsv = nt.nodes.new("ShaderNodeSeparateColor"); hsv.mode = "HSV"; nt.links.new(c, hsv.inputs[0])
        mr = nt.nodes.new("ShaderNodeMapRange")
        mr.inputs["From Min"].default_value = 0.12; mr.inputs["From Max"].default_value = 0.3
        mr.inputs["To Max"].default_value = strength
        nt.links.new(hsv.outputs[1], mr.inputs["Value"])
        # pale grey/blue irises have little saturation: also take the darker-than-sclera part (value < ~0.6)
        mv = nt.nodes.new("ShaderNodeMapRange")
        mv.inputs["From Min"].default_value = 0.62; mv.inputs["From Max"].default_value = 0.45
        mv.inputs["To Max"].default_value = strength
        nt.links.new(hsv.outputs[2], mv.inputs["Value"])
        mx = nt.nodes.new("ShaderNodeMath"); mx.operation = "MAXIMUM"
        nt.links.new(mr.outputs[0], mx.inputs[0]); nt.links.new(mv.outputs[0], mx.inputs[1])
        dark = M.mix(nt, c, iris, 0.75)                       # keep a little of the iris texture detail
        return M.mix(nt, c, dark, mx.outputs[0])
    for o in ch.parts.get("Eyes", []):
        M.recolor(o, b)


def brow_scar(ch, side=+1):
    """Arin's old scar: a thin pale line crossing the outer brow (side=+1: the character's LEFT, +X),
    with a 2 mm gap cut into the eyebrow hairs."""
    from mathutils import Vector
    from mathutils.geometry import intersect_point_line
    body = ch.body
    pts, nrm = M.rest_positions(body)
    g = body.vertex_groups["body"].index           # real skin only, not MakeHuman's hidden helper geometry
    real = [pts[v.index] for v in body.data.vertices if any(e.group == g and e.weight > 0.5 for e in v.groups)]
    top = max(p.z for p in real)
    head = [p for p in real if p.z > top - 0.13]
    front = min(p.y for p in head)
    cx = sum(p.x for p in head) / len(head)
    bz = top - 0.105
    a = Vector((cx + side * 0.036, front, bz + 0.011))
    b = Vector((cx + side * 0.03, front, bz - 0.007))

    def dist(p):
        q, f = intersect_point_line(Vector((p.x, front, p.z)), a, b)
        f = min(1.0, max(0.0, f))
        q = a + (b - a) * f
        return Vector((p.x - q.x, 0, p.z - q.z)).length if p.y < front + 0.03 else 1.0
    M.paint(body, "zc_scar", lambda p, n: (M.smooth(0.0042, 0.0016, dist(p)), 0, 0))
    M.recolor(body, lambda nt, c: M.mix(nt, c, (0.78, 0.6, 0.55), M.attr(nt, "zc_scar")[0]))
    import bmesh
    for o in ch.parts.get("Eyebrows", []):
        bm = bmesh.new(); bm.from_mesh(o.data)
        kill = [v for v in bm.verts if dist(o.matrix_world @ v.co) < 0.0022]
        bmesh.ops.delete(bm, geom=kill, context="VERTS")
        bm.to_mesh(o.data); bm.free()


def veins(ch, side="l", length=0.15, strength=0.9):
    """Early infection: a web of dark veins under the skin of the forearm, densest at the wrist (Nika, CH01+).
    Painted as a mask attribute 'zc_veins' (wrist -> elbow fade) x thin Voronoi edge lines in the skin shader."""
    from mathutils import Vector
    from mathutils.geometry import intersect_point_line
    body = ch.body; rig = ch.rig
    b = rig.data.bones[f"lowerarm_{side}"]
    wrist = rig.matrix_world @ b.tail_local
    elbow = rig.matrix_world @ b.head_local
    d = (elbow - wrist).normalized()
    hb = rig.data.bones[f"hand_{side}"]
    palm = rig.matrix_world @ hb.tail_local

    def m(p, n):
        q, f = intersect_point_line(p, wrist, elbow)
        along = (p - wrist).dot(d)                       # 0 at the wrist, + toward the elbow, - onto the hand
        r = (p - q).length
        if r > 0.06 or along < -0.025 or along > length:
            return (0, 0, 0)
        w = 1.0 - M.smooth(0.0, length, along)            # strongest at the wrist
        w *= 1.0 - M.smooth(-0.01, -0.025, along) if along < 0 else 1.0
        return (w, 0, 0)
    M.paint(body, "zc_veins", m)

    def build(nt, c):
        tc = nt.nodes.new("ShaderNodeTexCoord")
        vo = nt.nodes.new("ShaderNodeTexVoronoi"); vo.feature = "DISTANCE_TO_EDGE"
        vo.inputs["Scale"].default_value = 55.0
        nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 18.0
        nt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
        mxv = nt.nodes.new("ShaderNodeMix"); mxv.data_type = "VECTOR"; mxv.inputs[0].default_value = 0.25
        nt.links.new(tc.outputs["Object"], mxv.inputs[4]); nt.links.new(nz.outputs["Color"], mxv.inputs[5])
        mp = nt.nodes.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (0.45, 1.0, 0.45)   # long cells along the arm (A-pose: arm runs in XZ)
        nt.links.new(mxv.outputs[1], mp.inputs["Vector"]); nt.links.new(mp.outputs["Vector"], vo.inputs["Vector"])
        line = nt.nodes.new("ShaderNodeMapRange")                     # thin lines: edge distance 0 -> 1, 0.05 -> 0
        line.inputs["From Min"].default_value = 0.0; line.inputs["From Max"].default_value = 0.09
        line.inputs["To Min"].default_value = 1.0; line.inputs["To Max"].default_value = 0.0
        nt.links.new(vo.outputs["Distance"], line.inputs["Value"])
        mul = nt.nodes.new("ShaderNodeMath"); mul.operation = "MULTIPLY"
        nt.links.new(line.outputs["Result"], mul.inputs[0]); nt.links.new(M.attr(nt, "zc_veins")[0], mul.inputs[1])
        k = nt.nodes.new("ShaderNodeMath"); k.operation = "MULTIPLY"; k.inputs[1].default_value = strength
        nt.links.new(mul.outputs[0], k.inputs[0])
        # a faint blue-grey bruise under the lines too
        mask = nt.nodes.new("ShaderNodeMath"); mask.operation = "MULTIPLY"; mask.inputs[1].default_value = 0.25
        nt.links.new(M.attr(nt, "zc_veins")[0], mask.inputs[0])
        c2 = M.mix(nt, c, (0.42, 0.4, 0.45), mask.outputs[0])
        return M.mix(nt, c2, (0.1, 0.07, 0.14), k.outputs[0])
    M.recolor(body, build)
