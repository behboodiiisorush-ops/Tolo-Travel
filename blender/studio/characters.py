"""Studio characters: MakeHuman bodies (real anatomy, fingers, clothes with folds) + a hand-built
cartoon head with a full face rig, matching the user's 5-character design sheet.

Face rig (extra bones added to the game_engine rig):
  eye_l / eye_r  : eyeballs; Damped-Track to the character's look target  (eye tracking)
  lid_l / lid_r  : upper lids (blink / suspicious squint / wide surprise)
  brow_l / brow_r: eyebrows (raise, lower, angry, worried/confused tilt)
  mouth shape keys: open, smile, frown, wide, o
Fingers: grip / point / relaxed curls on all finger bones.

    import characters as C
    girl = C.spawn("nina")
    girl.animate(f, t, pos, facing, walk=1, phase=..., arms="rest", look_at=(x, y, z),
                 brows="worried", mouth=dict(open=0.4), hands="point_r", talking=0.6)
    girl.flush()
"""
import bpy, math, os, sys
from mathutils import Vector, Matrix, Quaternion

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "cast"))
import mpfb_tools as M   # noqa: E402
import cast              # noqa: E402
import anim              # noqa: E402
import props as P        # noqa: E402

# ------------------------------------------------------------------ the five characters of the sheet
SHEET = {
    "nina":  dict(fa="نینا", desc="girl 15, brown bob, navy sweater, charcoal trousers, white sneakers",
                  gender=0.0, age=0.4, height=0.42, weight=0.42, skin=(0.86, 0.68, 0.55),
                  hair=("bob", (0.33, 0.2, 0.12)),
                  clothes={"mindfront_knitted_sweater_02": (0.13, 0.16, 0.27), "toigo_wool_pants": (0.15, 0.15, 0.17),
                           "culturalibre_sneakers": (0.92, 0.92, 0.9)}),
    "arian": dict(fa="آرین", desc="boy 16, messy black hair, olive jacket over black tee, black cargo pants, boots",
                  gender=1.0, age=0.42, height=0.6, weight=0.45, skin=(0.8, 0.6, 0.45),
                  hair=("messy", (0.06, 0.05, 0.05)),
                  clothes={"elvs_crude_t-shirt_male": (0.08, 0.08, 0.09), "elvs_hooded_sweat_jacket1": (0.29, 0.32, 0.2),
                           "punkduck_male_classic_jeans": (0.09, 0.09, 0.1), "culturalibre_male_boots": (0.12, 0.12, 0.12)}),
    "mom":   dict(fa="مامان", desc="woman 45, dark hair in a low bun, maroon cardigan, black trousers, black flats",
                  gender=0.0, age=0.62, height=0.42, weight=0.55, skin=(0.84, 0.66, 0.52),
                  hair=("bun", (0.08, 0.06, 0.05)),
                  clothes={"janexx_old_female_sweater": (0.35, 0.12, 0.13), "toigo_wool_pants": (0.07, 0.07, 0.08),
                           "elvs_flatshoe_plain1": (0.06, 0.06, 0.06)}),
    "kian":  dict(fa="کیان", desc="boy 15, wavy brown hair, light blue shirt (rolled sleeves), dark jeans, white sneakers",
                  gender=1.0, age=0.4, height=0.5, weight=0.42, skin=(0.88, 0.7, 0.56),
                  hair=("wavy", (0.27, 0.17, 0.1)),
                  clothes={"elvs_male_shirt_untucked_bd1": (0.45, 0.55, 0.72), "punkduck_male_classic_jeans": (0.13, 0.16, 0.26),
                           "culturalibre_sneakers": (0.92, 0.92, 0.9)}),
    "kazemi": dict(fa="آقای کاظمی", desc="man 55, grey hair, stubble, black coat, dark grey shirt, brown trousers",
                   gender=1.0, age=0.8, height=0.58, weight=0.6, skin=(0.8, 0.62, 0.48),
                   hair=("short", (0.42, 0.42, 0.42)),
                   clothes={"male_elegantsuit01": (0.08, 0.08, 0.09), "culturalibre_male_boots": (0.07, 0.06, 0.06)}),
}
SHEET["me"] = dict(fa="من", desc="POV boy 15, dark curly hair, grey hoodie, jeans, white sneakers",
                   gender=1.0, age=0.4, height=0.55, weight=0.45, skin=(0.84, 0.65, 0.5), hair=("messy", (0.07, 0.05, 0.05)),
                   clothes={"elvs_hooded_sweat_jacket1": (0.42, 0.43, 0.45), "punkduck_male_classic_jeans": (0.14, 0.17, 0.26),
                            "culturalibre_sneakers": (0.92, 0.92, 0.9)})
SHEET["intruder"] = dict(fa="نقاب‌دار", desc="masked intruder, black knit mask (eyes only), dark work clothes, boots",
                         gender=1.0, age=0.6, height=0.7, weight=0.62, skin=(0.07, 0.07, 0.08), hair=None, mask=(0.06, 0.06, 0.07),
                         clothes={"elvs_crude_t-shirt_male": (0.06, 0.06, 0.07), "elvs_hooded_sweat_jacket1": (0.07, 0.07, 0.08),
                                  "punkduck_male_classic_jeans": (0.08, 0.08, 0.09), "culturalibre_male_boots": (0.05, 0.05, 0.05)})
ZOMBIE_SKIN = (0.6, 0.66, 0.56)


# ------------------------------------------------------------------ helpers
def _sel(objs, active):
    for o in bpy.context.selected_objects:
        o.select_set(False)
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = active


def _weight_all(o, group):
    vg = o.vertex_groups.new(name=group)
    vg.add(list(range(len(o.data.vertices))), 1.0, "REPLACE")


def _bind(o, rig, group):
    """Rigid part: whole mesh weighted to one bone, deformed by the rig, origin kept."""
    _weight_all(o, group)
    md = o.modifiers.new("Armature", "ARMATURE")
    md.object = rig
    o.parent = rig
    o.matrix_parent_inverse = rig.matrix_world.inverted()


def _sphere(name, loc, r, mat, segs=32, scale=(1, 1, 1)):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=loc, segments=segs, ring_count=segs // 2)
    o = bpy.context.object
    o.name = name
    o.scale = scale
    _sel([o], o)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(mat)
    bpy.ops.object.shade_smooth()
    return o


def _mat(name, rgb, rough=0.75):
    return P.mat(name, rgb, rough)


# ------------------------------------------------------------------ the cartoon head
def build_head(ch, skin_rgb, hair_style, hair_rgb, zombie=False):
    rig = ch.rig
    hb = rig.data.bones["head"]
    neck_top = rig.matrix_world @ hb.head_local
    k = 1.0
    R = 0.13                                    # head radius (cartoon: ~1.35x a real head)
    hc = neck_top + Vector((0, -0.005, 0.1))
    m_skin = _mat(f"{ch.name} face skin", skin_rgb, 0.7)
    # --- skull: sphere shaped into a soft cartoon head (round cranium, narrower jaw, small chin)
    head = _sphere(f"{ch.name} head", hc, R, m_skin, 48)
    for v in head.data.vertices:
        p = v.co
        zn = p.z / R
        jaw = 0.78 + 0.22 * min(1.0, max(0.0, (zn + 1.0) / 1.15))          # taper towards the chin
        p.x *= 0.9 * jaw
        p.y *= 0.95 * (0.86 + 0.14 * min(1.0, max(0.0, (zn + 1.0) / 1.2)))
        if zn < -0.55:
            p.z += (zn + 0.55) * R * 0.18                                  # longer chin
        if p.y < 0 and -0.45 < zn < 0.1:
            p.y -= 0.012 * (1 - abs(zn + 0.2) / 0.3) * (1 - min(1, abs(p.x) / (R * 0.7)))   # cheeks
    sub = head.modifiers.new("smooth", "SUBSURF")
    sub.levels = sub.render_levels = 1
    parts = [head]
    nose = _sphere(f"{ch.name} nose", hc + Vector((0, -R * 0.93, -R * 0.18)), R * 0.13, m_skin, 16, (0.8, 1.0, 1.1))
    parts.append(nose)
    for s in (1, -1):
        parts.append(_sphere(f"{ch.name} ear", hc + Vector((s * R * 0.86, 0.01, -R * 0.08)), R * 0.16, m_skin, 16,
                             (0.5, 0.8, 1.2)))
    for o in parts:
        _bind(o, rig, "head")
    # --- eyes (separate bones for tracking), lids, brows
    m_white = _mat(f"{ch.name} eye white", (0.95, 0.94, 0.9), 0.35)
    m_pupil = _mat(f"{ch.name} pupil", (0.03, 0.025, 0.03) if not zombie else (0.85, 0.84, 0.78), 0.25)
    m_brow = _mat(f"{ch.name} brow", tuple(c * 0.8 for c in hair_rgb) if hair_rgb[0] < 0.3 else (0.18, 0.17, 0.17), 0.7)
    re = R * 0.24
    eye_pos = {}
    for side, s in (("l", 1), ("r", -1)):
        ec = hc + Vector((s * R * 0.38, -R * 0.72, R * 0.02))
        eye_pos[side] = ec
        ball = _sphere(f"{ch.name} eye {side}", ec, re, m_white, 32, (1.0, 0.8, 1.15))
        pupil = _sphere(f"{ch.name} pupil {side}", ec + Vector((0, -re * 0.62, 0)), re * 0.62, m_pupil, 24, (1.0, 0.45, 1.2))
        glint = _sphere(f"{ch.name} glint {side}", ec + Vector((s * re * 0.25, -re * 0.92, re * 0.35)), re * 0.15,
                        P.emit(f"{ch.name} glint", (1, 1, 1), 1.5), 12)
        for o in (ball, pupil) + (() if zombie else (glint,)):
            _bind(o, rig, f"eye_{side}")
        if zombie:
            bpy.data.objects.remove(glint)
        # upper lid: a skin shell over the top of the eye, rotates down to blink
        lid = _sphere(f"{ch.name} lid {side}", ec, re * 1.12, m_skin, 32, (1.05, 0.88, 1.2))
        bm_keep = [v.index for v in lid.data.vertices if v.co.z > re * 0.62]
        drop = [v for v in lid.data.vertices if v.index not in bm_keep]
        import bmesh
        bm = bmesh.new()
        bm.from_mesh(lid.data)
        bm.verts.ensure_lookup_table()
        bmesh.ops.delete(bm, geom=[bm.verts[v.index] for v in drop], context="VERTS")
        bm.to_mesh(lid.data)
        bm.free()
        sol = lid.modifiers.new("thick", "SOLIDIFY")
        sol.thickness = 0.002
        _bind(lid, rig, f"lid_{side}")
        brow = _sphere(f"{ch.name} brow {side}", ec + Vector((0, -re * 0.25, re * 1.55)), re, m_brow, 24,
                       (1.25, 0.32, 0.3))
        for v in brow.data.vertices:          # gentle arch
            v.co.z -= (v.co.x / (re * 1.25)) ** 2 * re * 0.18
        _bind(brow, rig, f"brow_{side}")
        parts += [ball, pupil, lid, brow] + ([] if zombie else [glint])
        ch.face["eye_" + side] = ball
    # --- mouth with shape keys
    mouth = _mouth(ch, hc + Vector((0, -R * 0.86, -R * 0.5)), R, zombie)
    _bind(mouth, rig, "head")
    parts.append(mouth)
    ch.face["mouth"] = mouth
    # --- hair (metaball volumes -> mesh)
    hair = _hair(ch, hc, R, hair_style, _mat(f"{ch.name} hair", hair_rgb, 0.8))
    _bind(hair, rig, "head")
    parts.append(hair)
    ch.face_objects = parts
    ch.head_center = hc
    ch.eye_center = (eye_pos["l"] + eye_pos["r"]) / 2
    return parts


def _mouth(ch, c, R, zombie):
    """A flat dark lens on the face with shape keys: closed line -> open / smile / frown / wide / o."""
    w, h = R * 0.32, R * 0.03
    bpy.ops.mesh.primitive_circle_add(vertices=24, radius=1, fill_type="NGON", location=c, rotation=(math.pi / 2, 0, 0))
    o = bpy.context.object
    o.name = f"{ch.name} mouth"
    _sel([o], o)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
    for v in o.data.vertices:
        v.co.x *= w
        v.co.z *= h
        v.co.y -= abs(v.co.x / w) ** 2 * R * 0.05            # follows the curve of the face
    o.data.materials.append(_mat(f"{ch.name} mouth", (0.22, 0.05, 0.06) if not zombie else (0.3, 0.02, 0.02), 0.5))
    o.shape_key_add(name="Basis")
    def key(name, fn):
        kb = o.shape_key_add(name=name)
        for i, v in enumerate(o.data.vertices):
            x, z = v.co.x / w, v.co.z / h
            kb.data[i].co = Vector(fn(v.co.copy(), x, z))
    key("open", lambda p, x, z: (p.x * 0.85, p.y, p.z * 7.5 - (h * 2.5 if z < 0 else 0)))
    key("smile", lambda p, x, z: (p.x * 1.05, p.y, p.z + (x * x) * h * 2.5 - (h * 0.8 if z < 0 else 0)))
    key("frown", lambda p, x, z: (p.x, p.y, p.z - (x * x) * h * 2.5))
    key("wide", lambda p, x, z: (p.x * 1.25, p.y, p.z * 2.0))
    key("o", lambda p, x, z: (p.x * 0.45, p.y, p.z * 6.0))
    sol = o.modifiers.new("thick", "SOLIDIFY")
    sol.thickness = 0.002
    return o


# hair = a cap that follows the skull down to a hairline + style volumes (metaball tufts)
HAIR = {   # cap: (front hairline z, side z, back z, thickness) in head radii;  tufts: (x, y, z, size)
    "messy": dict(cap=(0.3, -0.05, -0.45, 1.08), tufts=[(0.3, -0.55, 0.75, 0.42), (-0.25, -0.6, 0.72, 0.42), (0.0, -0.68, 0.6, 0.36),
                  (0.55, -0.3, 0.68, 0.4), (-0.55, -0.25, 0.7, 0.4), (0.2, 0.2, 1.0, 0.45), (-0.3, 0.1, 0.98, 0.45),
                  (0.62, 0.3, 0.6, 0.38), (-0.62, 0.35, 0.55, 0.38), (0.0, -0.3, 0.98, 0.45)]),
    "wavy":  dict(cap=(0.25, -0.2, -0.55, 1.1), tufts=[(0.72, -0.15, 0.3, 0.45), (-0.72, -0.15, 0.32, 0.45), (0.35, -0.62, 0.62, 0.42),
                  (-0.3, -0.64, 0.66, 0.42), (0.0, 0.0, 1.02, 0.5), (0.65, 0.35, 0.2, 0.4), (-0.65, 0.35, 0.2, 0.4)]),
    "bob":   dict(cap=(0.22, -0.85, -0.85, 1.12), tufts=[(0.0, -0.72, 0.55, 0.5), (0.4, -0.66, 0.5, 0.4), (-0.4, -0.66, 0.5, 0.4),
                  (0.78, 0.0, -0.55, 0.42), (-0.78, 0.0, -0.55, 0.42)]),
    "bun":   dict(cap=(0.4, -0.2, -0.6, 1.05), tufts=[(0.0, 0.98, 0.05, 0.55), (0.32, -0.62, 0.6, 0.3), (-0.32, -0.62, 0.6, 0.3)]),
    "short": dict(cap=(0.5, 0.05, -0.4, 1.05), tufts=[(0.0, 0.1, 1.0, 0.4), (0.4, 0.0, 0.9, 0.32), (-0.4, 0.0, 0.9, 0.32)]),
}


def _hair(ch, hc, R, style, mat):
    import bmesh
    H = HAIR[style]
    fz, sz, bz, th = H["cap"]
    cap = _sphere(f"{ch.name} hair", hc, R * th, mat, 48)
    for v in cap.data.vertices:      # same skull shaping as the head, a bit fuller
        p = v.co
        zn = p.z / (R * th)
        p.x *= 0.93
        p.y *= 0.98
    bm = bmesh.new()
    bm.from_mesh(cap.data)
    kill = []
    for v in bm.verts:
        x, y, z = v.co.x / R, v.co.y / R, v.co.z / R
        front = max(0.0, min(1.0, (-y - 0.1) / 0.6))          # 1 at the face, 0 at the sides/back
        back = max(0.0, min(1.0, (y - 0.1) / 0.6))
        line = fz * front + bz * back + sz * (1 - front - back)
        if z < line:
            kill.append(v)
    bmesh.ops.delete(bm, geom=kill, context="VERTS")
    bm.to_mesh(cap.data)
    bm.free()
    sol = cap.modifiers.new("thick", "SOLIDIFY")
    sol.thickness = R * 0.05
    sub = cap.modifiers.new("smooth", "SUBSURF")
    sub.levels = sub.render_levels = 1
    mb = bpy.data.metaballs.new(f"{ch.name} tufts")
    mb.resolution = mb.render_resolution = 0.01
    o = bpy.data.objects.new(f"{ch.name} tufts", mb)
    bpy.context.scene.collection.objects.link(o)
    o.location = hc
    for x, y, z, r in H["tufts"]:
        e = mb.elements.new()
        e.co = (x * R, y * R, z * R)
        e.radius = r * R * 1.6
    _sel([o], o)
    bpy.ops.object.convert(target="MESH")
    t = bpy.context.object
    t.name = f"{ch.name} hair tufts"
    t.data.materials.clear()
    t.data.materials.append(mat)
    bpy.ops.object.shade_smooth()
    _sel([cap, t], cap)
    for m in list(cap.modifiers):
        bpy.ops.object.modifier_apply(modifier=m.name)
    bpy.ops.object.join()
    return cap


# ------------------------------------------------------------------ the character
FACE_BONES = ["eye_l", "eye_r", "lid_l", "lid_r", "brow_l", "brow_r"]


class StudioCharacter(cast.Character):
    def __init__(self, key, zombie=0.0, name=None):
        d = SHEET[key]
        self.sheet = d
        body, rig, parts = M.build_human(
            name or key.capitalize(), gender=d["gender"], age=d["age"], height=d["height"], weight=d["weight"],
            skin="young_caucasian_female" if d["gender"] < 0.5 else "young_caucasian_male", skin_type="MAKESKIN",
            hair=None, brow=None, lashes=None, clothes=list(d["clothes"]), subdiv=1)
        for k in ("Eyes", "Teeth"):
            for o in parts.pop(k, []):
                bpy.data.objects.remove(o)
        super().__init__(key, d, body, rig, parts, "hero")
        self.face = {}
        skin = ZOMBIE_SKIN if zombie else d["skin"]
        # flat cartoon skin on the body, cloth colours
        M.recolor(body, lambda nt, c: M.mix(nt, c, P.lin(skin), 0.92))
        for asset, col in d["clothes"].items():
            for o in parts.get("by_asset", {}).get(asset, []):
                M.set_color(o, col, keep=0.3)
        # hide the MakeHuman head (keep the neck)
        md = body.modifiers.new("Hide head", "MASK")
        md.vertex_group = "head"
        md.invert_vertex_group = True
        md.threshold = 0.35
        self._add_face_bones()
        if d.get("mask"):
            build_head(self, d["mask"], "short", d["mask"], zombie=False)
            for o in self.face_objects:
                if any(k in o.name for k in ("hair", "mouth", "nose", "ear", "brow")):
                    o.hide_render = True
        else:
            build_head(self, skin, d["hair"][0], d["hair"][1], zombie=bool(zombie))
        self.objects = [o for o in bpy.data.objects if o == rig or o.parent == rig]
        # look target
        self.look_target = P.empty(f"{self.name} look")
        for side in ("l", "r"):
            c = rig.pose.bones[f"eye_{side}"].constraints.new("DAMPED_TRACK")
            c.target = self.look_target
            c.track_axis = "TRACK_Y"
        self.zombie = zombie

    def _add_face_bones(self):
        rig = self.rig
        hb = rig.data.bones["head"]
        neck_top = hb.head_local.copy()
        R = 0.13
        hc = neck_top + Vector((0, -0.005, 0.1))
        _sel([rig], rig)
        bpy.ops.object.mode_set(mode="EDIT")
        eb = rig.data.edit_bones
        for side, s in (("l", 1), ("r", -1)):
            ec = hc + Vector((s * R * 0.38, -R * 0.72, R * 0.02))
            for nm, off in ((f"eye_{side}", Vector()), (f"lid_{side}", Vector()),
                            (f"brow_{side}", Vector((0, 0, R * 0.24 * 1.55)))):
                b = eb.new(nm)
                b.head = ec + off
                b.tail = ec + off + Vector((0, -0.04, 0))
                b.parent = eb["head"]
        bpy.ops.object.mode_set(mode="OBJECT")

    # ---------------------------------------------------------- face + hands per frame
    def face_pose(self, frame, t, st):
        rig = self.rig
        fst = dict(st)
        fst.setdefault("zombie", self.zombie)
        fv = anim.face(fst)
        blink = fv["eye-left-closure"]
        wide = fv["eye-left-opened-up"]
        brows = st.get("brows", "worried" if fv["eyebrows-left-inner-up"] > 0.3 else ("angry" if self.zombie else "neutral"))
        squint = 0.35 if st.get("suspicious") else 0.0
        lid = max(blink * 95, squint * 45) - wide * 10
        tilt, lift = {"neutral": (0, 0), "up": (0, 1), "worried": (14, 0.6), "angry": (-18, -0.5),
                      "confused": (None, 0.3), "surprised": (4, 1.2)}.get(brows, (0, 0))
        for side, s in (("l", 1), ("r", -1)):
            pb = rig.pose.bones[f"lid_{side}"]
            pb.rotation_mode = "QUATERNION"
            pb.rotation_quaternion = M.q(pb, (1, 0, 0), lid)
            bb = rig.pose.bones[f"brow_{side}"]
            bb.rotation_mode = "QUATERNION"
            tl = tilt if tilt is not None else (16 if side == "l" else -10)
            bb.rotation_quaternion = M.q(bb, (0, 1, 0), s * tl)
            bb.location = bb.bone.matrix_local.to_3x3().inverted() @ Vector((0, 0, 0.009 * lift))
            for i in range(4):
                self._put(rig, f'pose.bones["lid_{side}"].rotation_quaternion', i, frame, pb.rotation_quaternion[i])
                self._put(rig, f'pose.bones["brow_{side}"].rotation_quaternion', i, frame, bb.rotation_quaternion[i])
            for i in range(3):
                self._put(rig, f'pose.bones["brow_{side}"].location', i, frame, bb.location[i])
        mouth = self.face["mouth"]
        mo = dict(open=fv["mouth-open"], smile=fv["mouth-corner-puller"], frown=fv["mouth-depression"] * 0.8)
        mo.update(st.get("mouth", {}))
        for k in ("open", "smile", "frown", "wide", "o"):
            kb = mouth.data.shape_keys.key_blocks[k]
            self._put(mouth.data.shape_keys, f'key_blocks["{k}"].value', 0, frame, max(0.0, min(1.0, mo.get(k, 0.0))))
        # eyes look at a point (default: straight ahead of the head)
        la = st.get("look_at")
        if la is None:
            hw = self.rig.matrix_world @ self.rig.pose.bones["head"].head
            fwd = self.rig.matrix_world.to_3x3() @ Vector((0, -1, 0))
            la = hw + Vector((0, 0, 0.12)) + fwd * 2.0
        for i in range(3):
            self._put(self.look_target, "location", i, frame, la[i])

    def hands_pose(self, frame, mode):
        """mode: relaxed | fist | grip | point_l | point_r | open"""
        rig = self.rig
        for side in ("l", "r"):
            m = mode
            if mode in ("point_l", "point_r"):
                m = "point" if mode.endswith(side) else "relaxed"
            curl = {"relaxed": 18, "open": 0, "fist": 80, "grip": 55, "point": 80}.get(m, 18)
            for fng in ("index", "middle", "ring", "pinky", "thumb"):
                c = curl
                if m == "point" and fng == "index":
                    c = 0
                if fng == "thumb":
                    c = curl * 0.5
                for j in (1, 2, 3):
                    pb = rig.pose.bones.get(f"{fng}_0{j}_{side}")
                    if pb is None:
                        continue
                    pb.rotation_mode = "QUATERNION"
                    q = Quaternion((1, 0, 0), math.radians(c * (0.7 if j == 1 else 1.0)))   # curl about the bone's own X
                    for i in range(4):
                        self._put(rig, f'pose.bones["{pb.name}"].rotation_quaternion', i, frame, q[i])

    def animate(self, frame, t, pos, facing=0.0, z_extra=0.0, scale=1.0, hands="relaxed", **st):
        super().animate(frame, t, pos, facing, z_extra, scale, **st)
        if st.get("look_at") is None:     # straight ahead of the face (+ head turn), from this frame's position
            yaw, pitch = st.get("look", (0.0, 0.0))
            a = math.radians(facing + yaw)
            fwd = Vector((-math.sin(a), math.cos(a), math.sin(math.radians(pitch))))
            eye_h = self.rig.pose.bones["head"].bone.head_local.z + 0.12
            st["look_at"] = Vector(pos) + Vector((0, 0, eye_h + z_extra)) + fwd * 2.5
        # the base class keys all pose bones; overwrite face + finger channels with our own values
        self.face_pose(frame, t, dict(st, t=t))
        self.hands_pose(frame, hands)

    def flush(self):
        # drop base-class keys for face/finger bones that we set ourselves (keep the last value per channel)
        seen = {}
        for key, (owner, pts) in list(getattr(self, "_rec", {}).items()):
            dd = {}
            for f, v in pts:
                dd[f] = v
            self._rec[key] = (owner, sorted(dd.items()))
        super().flush()


def spawn(key, zombie=0.0, name=None):
    return StudioCharacter(key, zombie=zombie, name=name)
