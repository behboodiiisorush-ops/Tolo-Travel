"""The soldier's right arm for «آستین»: a blood stain that soaks through the sleeve, the sleeve that gets rolled
up (a MASK on the uniform, keyed on), a cuff, and the bite (comic decals that survive the flat toon skin).

    import arm
    A = arm.build(ch, fps=24)                 # call with the rig in rest pose (before any animation)
    A.stain(times=[(t0, 0.2), (t1, 1.0)])     # growing wet patch on the sleeve
    A.reveal(t)                               # from t: sleeve rolled up, bite + veins visible
"""
import bpy, bmesh, math
from mathutils import Vector, Matrix
import props as P
import mpfb_tools as M

T_CUFF = 0.24          # along the upper arm (0 = shoulder, 1 = elbow) where the rolled sleeve ends
T_BITE = 0.80


def _seg_param(p, a, b):
    d = b - a
    t = max(0.0, min(1.0, (p - a).dot(d) / d.length_squared))
    return t, (p - (a + d * t)).length


def _disc(name, loc, normal, rx, ry, thick, m, up=None):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=16, v_segments=8, radius=1.0)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(o)
    me.materials.append(m)
    q = Vector(normal).to_track_quat("Z", "Y")
    if up is not None:                                 # long axis (x) along `up` projected on the surface
        n = Vector(normal).normalized()
        u = (Vector(up) - n * Vector(up).dot(n)).normalized()
        R = Matrix((u, n.cross(u), n)).transposed()
        q = R.to_quaternion()
    o.matrix_world = Matrix.Translation(loc) @ q.to_matrix().to_4x4() @ Matrix.Diagonal((rx, ry, thick, 1))
    for poly in me.polygons:
        poly.use_smooth = True
    return o


def _key_vis(o, pts, fps):
    for t, v in pts:
        f = max(1, int(round(t * fps)) + 1)
        o.hide_render = not v
        o.keyframe_insert("hide_render", frame=f)
    ad = o.animation_data
    for fc in _fcurves(o):
        for k in fc.keyframe_points:
            k.interpolation = "CONSTANT"


def _fcurves(o):
    ad = o.animation_data
    if not ad or not ad.action:
        return []
    act = ad.action
    if hasattr(act, "fcurves") and len(act.fcurves):
        return list(act.fcurves)
    out = []
    for layer in getattr(act, "layers", []):
        for strip in layer.strips:
            for cb in getattr(strip, "channelbags", []):
                out += list(cb.fcurves)
    return out


class Arm:
    def __init__(self, ch, fps):
        self.ch, self.fps = ch, fps
        rig = ch.rig
        a = M.bone_world(rig, "upperarm_r")
        e = M.bone_world(rig, "lowerarm_r")
        w = M.bone_world(rig, "hand_r")
        self.a, self.e, self.w = a, e, w
        clothes = [o for o in ch.parts.get("Clothes", []) if "worksuit" in o.name.lower()]
        self.suit = clothes
        # --- the rolled-up part of the sleeve: everything on the right arm past T_CUFF
        self.masks = []
        for o in clothes:
            pts, _ = M.rest_positions(o)
            ends = [_seg_param(p, a, e)[0] for p in pts if _seg_param(p, a, e)[1] < 0.085 and _seg_param(p, e, w)[0] == 0.0]
            self.sleeve_end = max(ends) if ends else 1.0
            print("SLEEVE END", round(self.sleeve_end, 3), len(pts))
            vg = o.vertex_groups.new(name="rolled_sleeve")
            idx = []
            for i, p in enumerate(pts):
                t1, d1 = _seg_param(p, a, e)
                t2, d2 = _seg_param(p, e, w)
                if (d1 < 0.085 and t1 > T_CUFF) or d2 < 0.08:
                    if p.x < a.x + 0.04 if a.x < 0 else p.x > a.x - 0.04:
                        idx.append(i)
            vg.add(idx, 1.0, "REPLACE")
            md = o.modifiers.new("Rolled", "MASK")
            md.vertex_group = "rolled_sleeve"
            md.invert_vertex_group = True
            md.show_render = md.show_viewport = False
            # put the mask before the armature so indices match the rest mesh
            while o.modifiers.find("Rolled") > 0:
                bpy.context.view_layer.objects.active = o
                with bpy.context.temp_override(object=o):
                    bpy.ops.object.modifier_move_up(modifier="Rolled")
            self.masks.append(md)
        # --- the skin under the sleeve must exist: drop the arm from the body's "delete under clothes" groups
        body = ch.body
        pts, nrm = M.rest_positions(body)
        arm_idx = []
        self.skin = []
        for i, p in enumerate(pts):
            t1, d1 = _seg_param(p, a, e)
            t2, d2 = _seg_param(p, e, w)
            if (d1 < 0.09 and t1 > T_CUFF - 0.08) or d2 < 0.085:
                arm_idx.append(i)
            if d1 < 0.07:
                self.skin.append((t1, p, nrm[i]))
        for md in body.modifiers:
            if md.type == "MASK" and md.vertex_group and md.invert_vertex_group:
                vg = body.vertex_groups.get(md.vertex_group)
                if vg:
                    vg.remove(arm_idx)
        self.objs_reveal, self.objs_stain = [], []
        mats = dict(
            cuff=P.mat("Sleeve cuff", (0.25, 0.3, 0.18), 0.9),
            stain=P.mat("Sleeve blood", (0.32, 0.03, 0.04), 0.4),
            wound=P.mat("Bite wound", (0.55, 0.04, 0.05), 0.3),
            dark=P.mat("Bite dark", (0.12, 0.01, 0.02), 0.5),
            vein=P.mat("Bite veins", (0.2, 0.12, 0.28), 0.6),
            bruise=P.mat("Bite bruise", (0.42, 0.3, 0.42), 0.8),
        )
        self.mats = mats
        axis = (e - a).normalized()
        # cuff: a short thick ring of rolled cloth
        cp = a.lerp(e, T_CUFF)
        rad = self._radius(T_CUFF) + 0.004
        bpy.ops.mesh.primitive_torus_add(major_radius=rad, minor_radius=0.011, major_segments=24, minor_segments=8)
        cuff = bpy.context.object
        cuff.name = "Soldier cuff"
        cuff.data.materials.append(mats["cuff"])
        cuff.matrix_world = Matrix.Translation(cp) @ axis.to_track_quat("Z", "Y").to_matrix().to_4x4()
        self.objs_reveal.append(cuff)
        # bite: on the outer side of the arm, just above the elbow
        out = Vector((-1.0 if a.x < 0 else 1.0, 0.35, 0.25)).normalized()
        tb = min(T_BITE, getattr(self, "sleeve_end", 1.0) - 0.1)
        cand = [(t, p, n) for t, p, n in self.skin if abs(t - tb) < 0.06]
        t, p, n = max(cand, key=lambda c: c[2].dot(out))
        self.bite_pt, self.bite_n = p, n
        up = axis
        self.objs_reveal.append(_disc("Bite bruise", p - n * 0.001, n, 0.05, 0.036, 0.004, mats["bruise"], up))
        self.objs_reveal.append(_disc("Bite wound", p + n * 0.0015, n, 0.026, 0.017, 0.004, mats["wound"], up))
        side = n.cross(up).normalized()
        for k in range(10):                     # two arcs of teeth marks
            ang = math.radians(-70 + 140 * (k % 5) / 4)
            arc = 1 if k < 5 else -1
            q = p + up * (0.026 * math.sin(ang)) + side * (arc * 0.019 * math.cos(ang) * 0.9) + n * 0.003
            self.objs_reveal.append(_disc(f"Bite tooth {k}", q, n, 0.0055, 0.0042, 0.002, mats["dark"], up))
        for k in range(7):                      # dark veins creeping out from the bite
            ang = 2 * math.pi * k / 7 + 0.4
            d = (up * math.cos(ang) + side * math.sin(ang) * 0.7).normalized()
            L = 0.045 + 0.02 * (k % 3)
            mid = p + d * (0.03 + L / 2)
            # push onto the skin
            near = min(self.skin, key=lambda c: (c[1] - mid).length)
            self.objs_reveal.append(_disc(f"Bite vein {k}", near[1] + near[2] * 0.0015, near[2], L / 2, 0.0028, 0.0015,
                                          mats["vein"], d))
        # blood soaking through the sleeve (on the cloth, a bit further out than the skin)
        sp = p + n * (self._cloth_gap() + 0.004)
        self.stain_obj = _disc("Sleeve stain", sp, n, 0.045, 0.034, 0.004, mats["stain"], up)
        self.objs_stain.append(self.stain_obj)
        for o in self.objs_reveal + self.objs_stain:
            M.attach(o, rig, "upperarm_r")
            o.hide_render = False

    def _radius(self, t):
        ds = [_seg_param(p, self.a, self.e)[1] for tt, p, _ in self.skin if abs(tt - t) < 0.05]
        return max(ds) if ds else 0.045

    def _cloth_gap(self):
        if not self.suit:
            return 0.0
        pts, _ = M.rest_positions(self.suit[0])
        best = min(pts, key=lambda q: (q - self.bite_pt).length)
        return max(0.004, (best - self.bite_pt).dot(self.bite_n))

    def stain(self, times):
        """times: [(seconds, size 0..1)] -> the patch grows (scale keys); hidden at 0."""
        o = self.stain_obj
        s0 = o.scale.copy()
        for t, s in times:
            o.scale = s0 * max(0.001, s)
            o.keyframe_insert("scale", frame=int(round(t * self.fps)) + 1)

    def reveal(self, t, end=999.0):
        for md in self.masks:
            for v in (False, True):
                md.show_render = md.show_viewport = v
                fr = int(round(t * self.fps)) + (1 if v else 0)
                md.keyframe_insert("show_render", frame=fr)
                md.keyframe_insert("show_viewport", frame=fr)
        for o in self.objs_reveal:
            _key_vis(o, [(0, False), (t, True)], self.fps)
        for o in self.objs_stain:
            _key_vis(o, [(0, True), (t, False)], self.fps)
        for o in self.suit:
            for fc in _fcurves(o):
                for k in fc.keyframe_points:
                    k.interpolation = "CONSTANT"

    def veins_grow(self, times):
        """times: [(seconds, scale)] for the veins (they spread while he turns)."""
        for o in self.objs_reveal:
            if "vein" in o.name or "bruise" in o.name:
                s0 = o.scale.copy()
                for t, s in times:
                    o.scale = s0 * s
                    o.keyframe_insert("scale", frame=int(round(t * self.fps)) + 1)
                o.scale = s0


def build(ch, fps=24):
    return Arm(ch, fps)
