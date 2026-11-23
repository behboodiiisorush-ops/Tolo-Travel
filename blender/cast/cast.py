"""The permanent cast of the Tolo Travel films (realistic, MPFB/MakeHuman based).

    import cast
    arian = cast.spawn("arian")                 # hero quality (SSS skin, subdivided clothes)
    z = cast.spawn("rezaei", zombie=1.0)        # any character can be turned into a zombie
    kid = cast.spawn_extra("student", 3)        # repeatable background people (seeded)
    arian.animate(frame, t, pos, facing_deg, walk=1, phase=..., look=(20, 0), worry=1.2, talking=True)

facing: 0 = looking along +Y, 90 = along -X (same as the POV camera yaw).
See CAST.md for who is who. Rules for every film: no hijab, no flags/emblems/logos.
"""
import bpy, math, random, zlib
from mathutils import Vector, Matrix
import mpfb_tools as M
import anim

# ---------------------------------------------------------------------------- the cast
# skin_tint multiplies the skin texture (warm olive = Iranian look); colours are linear RGB.
WARM = (0.86, 0.69, 0.54)
CAST = {
    "me": dict(
        fa="من", role="Narrator / POV hero, 15. Mostly unseen (camera = his eyes).",
        gender=1.0, age=0.4, height=0.55, weight=0.45, muscle=0.45, skin="young_caucasian_male", skin_tint=WARM,
        hair="short03", hair_col=(0.09, 0.06, 0.04), brow="eyebrow002",
        clothes={"elvs_hooded_sweat_jacket1": (0.12, 0.2, 0.42), "punkduck_male_classic_jeans": None,
                 "shoes01": None}),
    "arian": dict(
        fa="آرین", role="Best friend, 15, joker, tall and lanky.",
        gender=1.0, age=0.4, height=0.6, weight=0.45, muscle=0.45, skin="young_caucasian_male", skin_tint=WARM,
        hair="short02", hair_col=(0.1, 0.07, 0.05), brow="eyebrow001",
        clothes={"namuhekam_male_polo_shirt": (0.3, 0.38, 0.55), "punkduck_male_classic_jeans": None, "shoes01": None}),
    "mahsa": dict(
        fa="مهسا", role="Classmate, 15, sharp and brave, black ponytail, glasses.",
        gender=0.0, age=0.4, height=0.42, weight=0.42, muscle=0.4, skin="young_caucasian_female", skin_tint=WARM,
        hair="ponytail01", hair_col=(0.05, 0.04, 0.035), brow="eyebrow010",
        clothes={"toigo_basic_tucked_t-shirt": (0.12, 0.16, 0.36), "toigo_wool_pants": (0.32, 0.32, 0.36),
                 "toigo_flats": (0.6, 0.1, 0.14), "spamrakuen_sagerfrogs_glasses_01": None}),
    "kian": dict(
        fa="کیان", role="Youngest of the class, 13, small, scared, light-brown hair, green backpack.",
        gender=1.0, age=0.33, height=0.25, weight=0.42, muscle=0.35, skin="young_caucasian_male",
        skin_tint=(0.92, 0.76, 0.62), hair="short01", hair_col=(0.3, 0.17, 0.08), brow="eyebrow003",
        clothes={"elvs_hooded_sweat_jacket1": (0.35, 0.55, 0.75), "elvs_jeans_straight_leg": None, "shoes01": None},
        backpack=(0.18, 0.42, 0.16)),
    "mom": dict(
        fa="مامان", role="Mom, 42, warm and worried. At home: cream sweater, hair in a bun.",
        gender=0.0, age=0.62, height=0.45, weight=0.5, muscle=0.4, skin="middleage_caucasian_female", skin_tint=WARM,
        hair="elvs_braid_bun", hair_col=(0.16, 0.09, 0.05), brow="eyebrow011",
        clothes={"mindfront_knitted_sweater_01": (0.85, 0.78, 0.62), "toigo_wool_pants": (0.15, 0.18, 0.3),
                 "toigo_flats": (0.5, 0.25, 0.28)}),
    "anchor": dict(
        fa="گوینده اخبار", role="TV news anchor, 45, dark suit, neutral studio (no logos).",
        gender=1.0, age=0.65, height=0.55, weight=0.5, muscle=0.5, skin="middleage_caucasian_male", skin_tint=WARM,
        hair="short04", hair_col=(0.12, 0.1, 0.09), brow="eyebrow004",
        clothes={"male_elegantsuit01": None, "shoes03": (0.08, 0.08, 0.08)}),
    "kazemi": dict(
        fa="آقای کاظمی", role="Teacher, 50, strict but brave, glasses, brown jacket.",
        gender=1.0, age=0.72, height=0.5, weight=0.62, muscle=0.45, skin="middleage_caucasian_male", skin_tint=WARM,
        hair="elvs_grump_hair", hair_set=(0.42, 0.4, 0.38), brow="eyebrow005",
        clothes={"male_casualsuit02": (0.42, 0.3, 0.2), "shoes03": (0.2, 0.13, 0.08),
                 "frankyaye_glasses_library_male": None}),
    "rezaei": dict(
        fa="آقای رضایی", role="School janitor, 58, grey hair, blue overalls. Becomes the first zombie.",
        gender=1.0, age=0.8, height=0.5, weight=0.55, muscle=0.45, skin="old_caucasian_male", skin_tint=WARM,
        hair="short04", hair_set=(0.62, 0.61, 0.6), brow="eyebrow006",
        clothes={"male_worksuit01": (0.2, 0.33, 0.6), "shoes03": None}),
    "soldier": dict(
        fa="سرباز", role="Rescue soldier, 28, plain olive uniform (no insignia), helmet, gloves. Bitten just above the right elbow.",
        gender=1.0, age=0.52, height=0.5, weight=0.5, muscle=0.7, skin="young_caucasian_male", skin_tint=WARM,
        hair="short04", hair_col=(0.08, 0.06, 0.05), brow="eyebrow006",
        clothes={"male_worksuit01": (0.25, 0.3, 0.18), "shoes03": (0.15, 0.13, 0.1),
                 "mrgreaterthan_m1_helmet": (0.28, 0.32, 0.2), "toigo_gloves_short": (0.06, 0.06, 0.06)}),
}

EXTRA_HAIR_M = ["short01", "short02", "short03", "short04", "o4saken_curly01", "elvs_short_side_do"]
EXTRA_HAIR_F = ["ponytail01", "bob01", "bob02", "braid01", "elvs_wavy_bob", "elvs_hazel_hair"]
EXTRA_TOPS = ["namuhekam_male_polo_shirt", "toigo_basic_tucked_t-shirt", "mindfront_knitted_sweater_02",
              "elvs_hooded_sweat_jacket1", "toigo_fisherman_sweater"]
EXTRA_PANTS = ["punkduck_male_classic_jeans", "cortu_cargo_pants", "elvs_jeans_straight_leg", "toigo_wool_pants"]
EXTRA_COLS = [(0.6, 0.12, 0.14), (0.15, 0.4, 0.2), (0.7, 0.55, 0.15), (0.3, 0.2, 0.45), (0.12, 0.4, 0.45),
              (0.55, 0.3, 0.12), (0.25, 0.3, 0.55), (0.35, 0.35, 0.35)]
SKIN_TINTS = [WARM, (0.92, 0.76, 0.62), (0.78, 0.6, 0.46), (0.7, 0.52, 0.4)]


def extra_def(kind, i):
    r = random.Random(zlib.crc32(kind.encode()) % 997 * 1000 + i)
    if kind == "student":
        g = r.choice([0.0, 1.0])
        return dict(fa=f"دانش‌آموز {i}", role="background student", gender=g, age=r.uniform(0.33, 0.42),
                    height=r.uniform(0.3, 0.6), weight=r.uniform(0.35, 0.6), muscle=0.4,
                    skin="young_caucasian_male" if g else "young_caucasian_female", skin_tint=r.choice(SKIN_TINTS),
                    hair=r.choice(EXTRA_HAIR_M if g else EXTRA_HAIR_F),
                    hair_col=r.choice([(0.05, 0.04, 0.035), (0.12, 0.08, 0.05), (0.25, 0.15, 0.08)]),
                    brow=f"eyebrow{r.randint(1, 12):03d}",
                    clothes={r.choice(EXTRA_TOPS): r.choice(EXTRA_COLS), r.choice(EXTRA_PANTS): None,
                             "shoes01": None})
    # adult passer-by (zombie fodder)
    g = r.choice([0.0, 1.0, 1.0])
    return dict(fa=f"رهگذر {i}", role="background adult", gender=g, age=r.uniform(0.5, 0.85),
                height=r.uniform(0.35, 0.65), weight=r.uniform(0.35, 0.75), muscle=0.45,
                skin=("middleage_caucasian_male" if g else "middleage_caucasian_female"), skin_tint=r.choice(SKIN_TINTS),
                hair=r.choice(EXTRA_HAIR_M if g else EXTRA_HAIR_F + ["long01"]),
                hair_col=r.choice([(0.05, 0.04, 0.035), (0.2, 0.14, 0.1), (0.4, 0.38, 0.36)]),
                brow=f"eyebrow{r.randint(1, 12):03d}",
                clothes={r.choice(["male_casualsuit01", "male_casualsuit03", "male_worksuit01", "toigo_fisherman_sweater",
                                   "namuhekam_male_polo_shirt"]): r.choice(EXTRA_COLS),
                         r.choice(EXTRA_PANTS): None, "shoes01": None})


# ---------------------------------------------------------------------------- character
class Character:
    def __init__(self, key, d, body, rig, parts, quality):
        self.key, self.d, self.body, self.rig, self.parts, self.quality = key, d, body, rig, parts, quality
        self.name = body.name
        self.seed = zlib.crc32(self.name.encode()) % 97
        self.keys = M.add_expr(body, anim.FACE_KEYS)
        pb = rig.pose.bones
        self.thigh_len = (pb["thigh_l"].bone.head_local - pb["calf_l"].bone.head_local).length
        self.calf_len = (pb["calf_l"].bone.head_local - pb["foot_l"].bone.head_local).length
        self.zombie = 0.0
        self.objects = [o for o in bpy.data.objects if o == rig or o.parent == rig or
                        (o.parent and o.parent.parent == rig)]

    # world positions
    def bone(self, name, tail=False):
        return M.bone_world(self.rig, name, tail)

    def hand_world(self, side="r"):
        return self.bone(f"hand_{side}")

    def head_world(self):
        return self.bone("head")

    def hide(self, frame, hidden):
        for o in self.objects:
            self._put(o, "hide_render", 0, frame, float(hidden))

    # ---- batched keyframes (much faster than keyframe_insert for long shots)
    def _put(self, owner, path, idx, frame, value):
        if not hasattr(self, "_rec"):
            self._rec = {}
        self._rec.setdefault((owner.name, type(owner).__name__, path, idx), (owner, []))[1].append((frame, value))

    def animate(self, frame, t, pos, facing=0.0, z_extra=0.0, scale=1.0, **st):
        st.setdefault("t", t)
        st.setdefault("seed", self.seed)
        spec = anim.pose_spec(st)
        ext = anim.leg_extent(spec, self.thigh_len, self.calf_len)
        drop = (ext - (self.thigh_len + self.calf_len)) * scale
        loc = Vector(pos) + Vector((0, 0, drop + z_extra))
        rz = math.radians(facing) + math.pi
        rig = self.rig
        for i in range(3):
            self._put(rig, "location", i, frame, loc[i])
        self._put(rig, "rotation_euler", 2, frame, rz)
        M.apply_spec(rig, spec)
        prev = getattr(self, "_prevq", {})
        for pb in rig.pose.bones:
            qq = pb.rotation_quaternion.copy()
            p0 = prev.get(pb.name)
            if p0 is not None and p0.dot(qq) < 0:
                qq.negate()
            prev[pb.name] = qq
            for i in range(4):
                self._put(rig, f'pose.bones["{pb.name}"].rotation_quaternion', i, frame, qq[i])
        self._prevq = prev
        fst = dict(st)
        fst.setdefault("zombie", self.zombie)
        sk = self.body.data.shape_keys
        for k, v in anim.face(fst).items():
            if k in self.keys:
                self._put(sk, f'key_blocks["{k}"].value', 0, frame, max(0.0, min(1.0, v)))
        if scale != 1.0:
            for i in range(3):
                self._put(rig, "scale", i, frame, scale)

    def flush(self):
        """Write all recorded keys as F-curves (call once after the frame loop)."""
        for (_, _, path, idx), (owner, pts) in getattr(self, "_rec", {}).items():
            write_fcurve(owner, path, idx, pts, constant=(path == "hide_render"))
        self._rec = {}


def write_fcurve(owner, path, idx, pts, constant=False):
    ad = owner.animation_data or owner.animation_data_create()
    if ad.action is None:
        ad.action = bpy.data.actions.new(f"{owner.name}_act")
    act = ad.action
    if hasattr(act, "fcurve_ensure_for_datablock"):
        fc = act.fcurve_ensure_for_datablock(owner, path, index=idx)
    else:
        fc = act.fcurves.find(path, index=idx) or act.fcurves.new(path, index=idx)
    pts = sorted(pts)
    n0 = len(fc.keyframe_points)
    fc.keyframe_points.add(len(pts))
    co = []
    for f, v in pts:
        co += [f, v]
    kp = fc.keyframe_points
    for i, (f, v) in enumerate(pts):
        k = kp[n0 + i]
        k.co = (f, v)
        k.interpolation = "CONSTANT" if constant else "LINEAR"
    fc.update()
    return fc


# ---------------------------------------------------------------------------- accessories
def _mat(name, col, rough=0.5, metal=0.0):
    m = bpy.data.materials.new(name)
    p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = col + (1,)
    p.inputs["Roughness"].default_value = rough
    p.inputs["Metallic"].default_value = metal
    return m


def _prim(kind, loc, scale, mat, name, rot=(0, 0, 0), **kw):
    getattr(bpy.ops.mesh, f"primitive_{kind}_add")(location=loc, rotation=rot, **kw)
    o = bpy.context.object
    o.scale = scale
    o.name = name
    o.data.materials.append(mat)
    bpy.ops.object.shade_smooth()
    return o


def add_gasmask(ch):
    h = ch.bone("head")
    up = ch.bone("head", tail=True) - h
    fwd = Vector((0, -1, 0))
    rub = _mat("Mask rubber", (0.06, 0.065, 0.06), 0.55)
    lens = _mat("Mask lens", (0.02, 0.025, 0.03), 0.05, 0.3)
    can = _mat("Mask filter", (0.22, 0.24, 0.2), 0.4, 0.4)
    c = h + up * 0.55 + fwd * 0.085
    parts = [_prim("uv_sphere", c + Vector((0, 0, -0.02)), (0.075, 0.05, 0.085), rub, "Gas mask", segments=24, ring_count=12),
             _prim("cylinder", c + fwd * 0.045 + Vector((0, 0, -0.055)), (0.032, 0.032, 0.03), can, "Mask filter",
                   rot=(math.pi / 2, 0, 0), vertices=20)]
    for sx in (-1, 1):
        parts.append(_prim("cylinder", c + Vector((sx * 0.032, -0.042, 0.03)), (0.024, 0.024, 0.01), lens, "Mask lens",
                           rot=(math.pi / 2, 0, 0), vertices=20))
    for o in parts:
        M.attach(o, ch.rig, "head")
    ch.objects += parts
    return parts


def add_backpack(ch, col):
    s3 = ch.bone("spine_03")
    m = _mat("Backpack", col, 0.7)
    o = _prim("cube", s3 + Vector((0, 0.16, -0.05)), (0.15, 0.08, 0.2), m, "Backpack")
    bev = o.modifiers.new("bevel", "BEVEL")
    bev.width = 0.04
    bev.segments = 3
    M.attach(o, ch.rig, "spine_03")
    ch.objects.append(o)
    return o


def add_prop(ch, kind):
    hr = ch.bone("hand_r", tail=True)
    if kind == "mug":
        o = _prim("cylinder", hr + Vector((0, -0.03, 0.02)), (0.04, 0.04, 0.05), _mat("Mug", (0.75, 0.2, 0.15), 0.3),
                  "Mug", vertices=24)
    else:  # chalk
        o = _prim("cylinder", hr + Vector((0, -0.02, 0.0)), (0.006, 0.006, 0.04), _mat("Chalk", (0.95, 0.95, 0.92), 0.9),
                  "Chalk", vertices=8)
    M.attach(o, ch.rig, "hand_r")
    ch.objects.append(o)
    return o


# ---------------------------------------------------------------------------- zombies
def zombify(ch, level=1.0, seed=0, bite=None):
    """Grey, bruised, blood-soaked skin, dead eyes, torn bloody clothes. level 0..1.
    bite: (bone, offset) to put one fresh bite wound somewhere (e.g. the soldier's wrist) without the rest."""
    r = random.Random(seed)
    body = ch.body
    teeth = ch.parts["Teeth"][0]
    eyes = ch.parts["Eyes"][0]
    mouth = M.bbox_center(teeth) + Vector((0, -0.035, -0.022))   # front of the lips
    ec, es = M.bbox_center(eyes), M.bbox_size(eyes)
    eyeL, eyeR = ec + Vector((es.x * 0.3, 0, 0)), ec - Vector((es.x * 0.3, 0, 0))
    hands = [ch.bone("hand_l", True), ch.bone("hand_r", True)]
    pts, _ = M.rest_positions(body)
    wounds = [(pts[r.randrange(len(pts))], r.uniform(0.025, 0.07)) for _ in range(int(9 * level))]
    neck = ch.bone("neck_01") + Vector((r.choice([-1, 1]) * 0.05, -0.02, 0.02))
    if level > 0.3:
        wounds.append((neck, 0.055))
    bite_pt = None
    if bite:
        bite_pt = ch.bone(bite[0]).lerp(ch.bone(bite[0], True), bite[2] if len(bite) > 2 else 0.5) + Vector(bite[1])

    def body_fn(p, n):
        b = 0.0
        if level > 0:
            d = (p - mouth).length
            b = M.smooth(0.045, 0.012, d)
            dz = mouth.z - p.z
            if 0 < dz < 0.32 and p.y < mouth.y + 0.07:
                stripe = (0.5 + 0.5 * math.sin(p.x * 140 + 3.1 * math.sin(p.x * 37))) ** 2
                b = max(b, M.smooth(0.075 + 0.03 * stripe, 0.0, abs(p.x - mouth.x)) * M.smooth(0.32 * stripe + 0.05, 0.0, dz))
            for w, rad in wounds:
                b = max(b, M.smooth(rad, rad * 0.4, (p - w).length))
            for h in hands:
                hd = (p - h).length
                b = max(b, 0.85 * M.smooth(0.14, 0.05, hd) * (0.5 + 0.5 * math.sin(p.z * 90 + p.x * 60)))
            b *= level
        g = level * max(M.smooth(0.04, 0.012, (p - eyeL).length), M.smooth(0.04, 0.012, (p - eyeR).length))
        if bite_pt is not None:
            b = max(b, M.smooth(0.13, 0.06, (p - bite_pt).length) * (0.65 + 0.35 * math.sin(p.z * 160 + p.x * 90)))
        return b, g, 0.0

    M.paint(body, "zblood", body_fn)

    def skin(nt, c):
        co = M.obj_coords(nt)
        if level > 0:
            c = M.mix(nt, c, (0.62, 0.6, 0.55), 0.85 * level, "SATURATION")
            c = M.mix(nt, c, (0.5, 0.54, 0.45), level, "MULTIPLY")
            bruise = M.noise_mask(nt, 5.0, 0.5, 0.78, 6.0, co)
            c = M.mix(nt, c, (0.25, 0.2, 0.28), M._scale(nt, bruise, 0.6 * level))
        return c

    def final(nt, bsdf, c):
        co = M.obj_coords(nt)
        a = M.attr(nt, "zblood")
        if level > 0:
            veins = M.noise_mask(nt, 9.0, 0.035, 0.0, 0, co, kind="edges")
            where = M.noise_mask(nt, 2.5, 0.45, 0.7, 4.0, co)
            vm = nt.nodes.new("ShaderNodeMath"); vm.operation = "MULTIPLY"
            nt.links.new(veins, vm.inputs[0]); nt.links.new(where, vm.inputs[1])
            c = M.mix(nt, c, (0.14, 0.1, 0.2), M._scale(nt, vm.outputs[0], 0.55 * level))
            spat = M.noise_mask(nt, 16.0, 0.6, 0.66, 10.0, co)
            c = M.mix(nt, c, (0.09, 0.005, 0.005), M._scale(nt, spat, level))
            c = M.mix(nt, c, (0.05, 0.025, 0.04), a[1])
        fresh = M.noise_mask(nt, 25.0, 0.3, 0.7, 4.0, co)
        blood = M.mix(nt, (0.14, 0.0, 0.0), (0.035, 0.0, 0.0), fresh)
        rough = M.float_input(nt, bsdf, "Roughness")
        nt.links.new(M.fmix(nt, rough, 0.12, a[0]), bsdf.inputs["Roughness"])
        sw = bsdf.inputs.get("Subsurface Weight")
        if sw is not None:
            ssw = M.float_input(nt, bsdf, "Subsurface Weight")
            nt.links.new(M.fmix(nt, ssw, 0.0, a[0]), sw)
        return M.mix(nt, c, blood, a[0])

    M.recolor(body, skin)
    M.recolor_bsdf(body, final)
    if level > 0:
        for md in list(body.modifiers):  # keep skin under torn clothes (but keep the helper mask)
            if md.type == "MASK" and md.name.startswith("Delete."):
                body.modifiers.remove(md)
        for o in ch.parts.get("Eyes", []):
            M.recolor(o, lambda nt, c: M.mix(nt, c, (0.85, 0.82, 0.74), 0.9 * level))
        for o in ch.parts.get("Teeth", []):
            M.recolor(o, lambda nt, c: M.mix(nt, M.mix(nt, c, (0.7, 0.58, 0.38), 0.8, "MULTIPLY"), (0.2, 0.01, 0.01),
                                              0.35 * level))
        for o in ch.parts.get("Hair", []):
            M.tint(o, (0.55, 0.5, 0.45), 0.6 * level)
        for o in ch.parts.get("Clothes", []):
            _zombie_cloth(o, mouth, level, r)
    ch.zombie = level


def _scale(nt, sock, k):
    m = nt.nodes.new("ShaderNodeMath")
    m.operation = "MULTIPLY"
    m.inputs[1].default_value = k
    nt.links.new(sock, m.inputs[0])
    return m.outputs[0]


M._scale = _scale


def _zombie_cloth(o, mouth, level, r):
    splats = [(Vector((mouth.x + r.uniform(-0.25, 0.25), mouth.y + r.uniform(-0.1, 0.2), mouth.z - r.uniform(0.2, 1.1))),
               r.uniform(0.04, 0.12)) for _ in range(int(7 * level))]

    def fn(p, n):
        b = 0.0
        dz = mouth.z - p.z
        if 0.05 < dz < 0.6 and p.y < mouth.y + 0.12:
            wob = 0.5 + 0.5 * math.sin(p.x * 50 + math.sin(p.z * 30) * 3)
            b = M.smooth(0.14 + 0.06 * wob, 0.02, abs(p.x - mouth.x)) * M.smooth(0.45 + 0.15 * wob, 0.1, dz)
        for c, rad in splats:
            b = max(b, M.smooth(rad, rad * 0.3, (p - c).length))
        return b * level, 0.0, 0.0

    M.paint(o, "zblood", fn)

    def col(nt, bsdf, c):
        co = M.obj_coords(nt)
        a = M.attr(nt, "zblood")
        c = M.mix(nt, c, (0.55, 0.5, 0.42), 0.5 * level, "SATURATION")
        dirt = M.noise_mask(nt, 3.0, 0.38, 0.72, 8.0, co)
        c = M.mix(nt, c, (0.1, 0.075, 0.05), M._scale(nt, dirt, 0.85 * level))
        grime = M.noise_mask(nt, 12.0, 0.45, 0.8, 8.0, co)
        c = M.mix(nt, c, (0.16, 0.13, 0.1), M._scale(nt, grime, 0.6 * level))
        spat = M.noise_mask(nt, 9.0, 0.6, 0.66, 10.0, co)
        sp = nt.nodes.new("ShaderNodeMath"); sp.operation = "MAXIMUM"
        nt.links.new(M._scale(nt, spat, level), sp.inputs[0]); nt.links.new(a[0], sp.inputs[1])
        rough = M.float_input(nt, bsdf, "Roughness")
        nt.links.new(M.fmix(nt, rough, 0.25, sp.outputs[0]), bsdf.inputs["Roughness"])
        return M.mix(nt, c, (0.07, 0.003, 0.003), sp.outputs[0])

    M.recolor_bsdf(o, col)

    def holes(nt, shader):
        co = M.obj_coords(nt)
        h = M.noise_mask(nt, 6.0, 0.66, 0.62, 12.0, co)
        tr = nt.nodes.new("ShaderNodeBsdfTransparent")
        mx = nt.nodes.new("ShaderNodeMixShader")
        f = nt.nodes.new("ShaderNodeMath")
        f.operation = "MAXIMUM"
        f.inputs[1].default_value = 1 - level
        nt.links.new(h, f.inputs[0])
        nt.links.new(f.outputs[0], mx.inputs[0])
        nt.links.new(tr.outputs[0], mx.inputs[1])
        nt.links.new(shader, mx.inputs[2])
        return mx.outputs[0]

    M.surface_wrap(o, holes)


# ---------------------------------------------------------------------------- spawn
def _build(key, d, quality):
    hero = quality == "hero"
    clothes = list(d["clothes"].keys())
    body, rig, parts = M.build_human(
        key.capitalize(), gender=d["gender"], age=d["age"], height=d["height"], weight=d["weight"],
        muscle=d["muscle"], skin=d["skin"], skin_type="ENHANCED_SSS" if hero else "MAKESKIN",
        hair=d.get("hair"), brow=d.get("brow", "eyebrow001"), clothes=clothes, subdiv=1 if hero else 0)
    ch = Character(key, d, body, rig, parts, quality)
    M.tint(body, d.get("skin_tint", WARM))
    for o in parts.get("Hair", []) + parts.get("Eyebrows", []):
        if d.get("hair_set"):          # light colours (grey) can't come from darkening: recolour
            M.set_color(o, d["hair_set"], keep=0.5)
        else:
            M.tint(o, d.get("hair_col", (0.1, 0.07, 0.05)))
    for asset, col in d["clothes"].items():
        if col is not None:
            for o in parts.get("by_asset", {}).get(asset, []):
                M.set_color(o, col)
    if d.get("gasmask"):
        ch.mask = add_gasmask(ch)
    if d.get("backpack"):
        add_backpack(ch, d["backpack"])
    return ch


_count = {}


def spawn(key, zombie=0.0, quality="hero", name=None, seed=0, bite=None):
    d = CAST[key]
    n = _count[key] = _count.get(key, 0) + 1
    ch = _build(key, d, quality)
    if name or n > 1:
        _rename(ch, name or f"{key.capitalize()}{n}")
    if zombie or bite:
        zombify(ch, zombie, seed, bite)
    return ch


def spawn_extra(kind, i, zombie=0.0, quality="extra"):
    d = extra_def(kind, i)
    ch = _build(kind, d, quality)
    _rename(ch, f"{kind.capitalize()}{i}{'Z' if zombie else ''}")
    if zombie:
        zombify(ch, zombie, i)
    return ch


def _rename(ch, new):
    old = ch.body.name
    for o in ch.objects:
        o.name = o.name.replace(old, new, 1) if o.name.startswith(old) else new + "." + o.name
    ch.name = new
    ch.seed = zlib.crc32(new.encode()) % 97
