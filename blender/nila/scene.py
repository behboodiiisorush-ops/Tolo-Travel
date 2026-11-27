"""«نیلا» — a stylised 3D girl in the look of a Pixar-like character study (big eyes, round soft face,
freckles, messy top bun with loose strands, brown tee, layered necklaces), with natural motion:
Mixamo motion capture cross-faded at full frame rate, plus procedural life on top (blinks, small eye
darts, head follows a look target with holds, breathing, a smile that grows).

    ../cast/bpy.sh scene.py --still 1,100 [--face]      -> out/still_<f>.png  (look checks)
    ../cast/bpy.sh scene.py --anim 1 240                -> frames/f_0001.png ...
    ../cast/bpy.sh scene.py --save                      -> nila.blend
Built only from code in Blender (MPFB human base + shape targets, no hand sculpting).
"""
import bpy, sys, os, math, random
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "cast"))
sys.path.append(os.path.join(HERE, "..", "shelter3"))
import cast, anim  # noqa: E402
import mpfb_tools as M  # noqa: E402
import mocap2 as MC  # noqa: E402,F401
import motion as MO  # noqa: E402
import props as P  # noqa: E402

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]


def arg(name, n=1, default=None):
    if name in argv:
        i = argv.index(name)
        return argv[i + 1] if n == 1 else argv[i + 1:i + 1 + n]
    return default


STILL = arg("--still")
ANIM = arg("--anim", 2)
FACE = "--face" in argv
FPS, N = 24, 264
MOCAP = os.path.join(HERE, "..", "mocap")

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.fps = FPS

CL = MO.load(["breathing_idle", "thinking", "head_nod_yes", "hands_forward_gesture"])

# ------------------------------------------------------------------ the character
STYLE = dict(cast.CARTOON)
STYLE.update({
    "l-eye-scale-incr": 2.4, "r-eye-scale-incr": 2.4,
    "l-eye-height2-incr": 0.9, "r-eye-height2-incr": 0.9, "l-eye-height1-incr": 0.4, "r-eye-height1-incr": 0.4,
    "l-eye-bag-decr": 0.8, "r-eye-bag-decr": 0.8, "l-eye-trans-out": 0.3, "r-eye-trans-out": 0.3,
    "head-round": 0.7, "head-scale-vert-incr": 0.2, "head-scale-horiz-incr": 0.25, "head-fat-incr": 0.4,
    "head-age-decr": 1.0, "forehead-scale-vert-incr": 0.6, "chin-height-decr": 0.5, "chin-width-decr": 0.3, "chin-prominent-decr": 0.4,
    "nose-scale-horiz-decr": 0.5, "nose-scale-vert-decr": 0.6, "nose-scale-depth-decr": 0.4,
    "nose-point-width-incr": 0.6, "nose-flaring-decr": 0.4,
    "mouth-scale-horiz-decr": 0.35, "mouth-lowerlip-volume-incr": 0.8, "mouth-upperlip-volume-incr": 0.6,
    "mouth-cupidsbow-incr": 0.5, "mouth-trans-forward": 0.3,
    "l-cheek-volume-incr": 0.6, "r-cheek-volume-incr": 0.6, "l-cheek-bones-decr": 0.5, "r-cheek-bones-decr": 0.5,
    "l-ear-scale-incr": 0.3, "r-ear-scale-incr": 0.3, "neck-scale-horiz-decr": 0.25,
})
cast.STYLE = STYLE
_load = M.TargetService.load_target


def _load_big(obj, path, *, weight=0.0, name=None):     # MPFB clamps weights to 1: allow more (bigger eyes)
    r = _load(obj, path, weight=min(weight, 1.0), name=name)
    if weight > 1.0:
        kb = obj.data.shape_keys.key_blocks[name]
        kb.slider_max = weight
        kb.value = weight
    return r


M.TargetService.load_target = staticmethod(_load_big)
cast.CAST["nila"] = dict(
    fa="نیلا", role="Stylised character study, 16.",
    gender=0.0, age=0.38, height=0.4, weight=0.42, muscle=0.35, skin="young_caucasian_female",
    skin_tint=(1.0, 0.62, 0.42), hair="culturalibre_hair_13", hair_col=(0.72, 0.62, 0.56), brow="eyebrow010",
    clothes={"joepal_crude_t-shirt_female": (0.2, 0.11, 0.07), "toigo_wool_pants": (0.1, 0.12, 0.18),
             "culturalibre_sneakers": None})
nila = cast.spawn("nila")
rig, body = nila.rig, nila.body
SHIRT = nila.parts["by_asset"]["joepal_crude_t-shirt_female"][0]
bpy.context.view_layer.update()


def bw(name, tail=False):
    return M.bone_world(rig, name, tail)


eyes = nila.parts["Eyes"][0]
EYE_C = M.bbox_center(eyes)
EYE_W = M.bbox_size(eyes).x

# ------------------------------------------------------------------ skin: freckles + warm soft look
def freckle_fn(p, n):
    d = p - EYE_C
    side = abs(d.x)
    cheek = M.smooth(0.010, 0.022, side) * (1 - M.smooth(0.055, 0.07, side))
    height = M.smooth(-0.052, -0.035, d.z) * (1 - M.smooth(-0.012, 0.0, d.z))
    bridge = (1 - M.smooth(0.012, 0.02, side)) * M.smooth(-0.03, -0.02, d.z) * (1 - M.smooth(-0.012, -0.006, d.z))
    front = M.smooth(0.2, 0.6, -n.y)
    v = max(cheek * height, 0.7 * bridge) * front
    blush = M.smooth(0.012, 0.03, side) * (1 - M.smooth(0.05, 0.068, side)) * M.smooth(-0.06, -0.04, d.z) \
        * (1 - M.smooth(-0.02, -0.005, d.z)) * front
    return v, blush, 0.0


M.paint(body, "face_paint", freckle_fn)


def skin_build(nt, bsdf, c):
    sepo = M.attr(nt, "face_paint")
    uv = nt.nodes.new("ShaderNodeTexCoord")
    vor = nt.nodes.new("ShaderNodeTexVoronoi")
    vor.inputs["Scale"].default_value = 160.0
    vor.inputs["Randomness"].default_value = 1.0
    nt.links.new(uv.outputs["UV"], vor.inputs["Vector"])
    dots = nt.nodes.new("ShaderNodeMapRange")
    dots.inputs["From Min"].default_value = 0.24
    dots.inputs["From Max"].default_value = 0.13
    nt.links.new(vor.outputs["Distance"], dots.inputs["Value"])
    keep = nt.nodes.new("ShaderNodeMath")            # only some cells become freckles
    keep.operation = "GREATER_THAN"
    keep.inputs[1].default_value = 0.55
    nt.links.new(vor.outputs["Color"], keep.inputs[0])
    m1 = nt.nodes.new("ShaderNodeMath")
    m1.operation = "MULTIPLY"
    nt.links.new(dots.outputs[0], m1.inputs[0])
    nt.links.new(keep.outputs[0], m1.inputs[1])
    m2 = nt.nodes.new("ShaderNodeMath")
    m2.operation = "MULTIPLY"
    m2.use_clamp = True
    nt.links.new(m1.outputs[0], m2.inputs[0])
    nt.links.new(sepo[0], m2.inputs[1])
    warm = M.mix(nt, c, (1.0, 0.7, 0.62), sepo[1], mode="MULTIPLY")            # rosy cheeks
    bl = nt.nodes.new("ShaderNodeMath")
    bl.operation = "MULTIPLY"
    bl.inputs[1].default_value = 0.85
    nt.links.new(m2.outputs[0], bl.inputs[0])
    return M.mix(nt, warm, (0.17, 0.07, 0.035), bl.outputs[0])


M.recolor_bsdf(body, skin_build)
for m in body.data.materials:
    b = next((n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None) if m.use_nodes else None
    if b:
        if not b.inputs["Roughness"].is_linked:
            b.inputs["Roughness"].default_value = 0.5
        if "Subsurface Weight" in b.inputs and not b.inputs["Subsurface Weight"].is_linked:
            b.inputs["Subsurface Weight"].default_value = max(0.25, b.inputs["Subsurface Weight"].default_value)

# eyes: dark-brown iris, black pupil, clean white, glossy
def eye_build(nt, bsdf, c):
    g = nt.nodes.new("ShaderNodeRGBToBW")
    nt.links.new(c, g.inputs[0])
    r = nt.nodes.new("ShaderNodeValToRGB")
    e = r.color_ramp.elements
    e[0].position, e[0].color = 0.12, (0.005, 0.004, 0.004, 1)
    e[1].position, e[1].color = 0.62, (0.92, 0.9, 0.87, 1)
    for pos, col in ((0.17, (0.05, 0.018, 0.008)), (0.35, (0.2, 0.08, 0.025)), (0.54, (0.32, 0.15, 0.05))):
        el = e.new(pos)
        el.color = col + (1,)
    nt.links.new(g.outputs[0], r.inputs[0])
    return r.outputs[0]


for o in nila.parts["Eyes"]:
    M.recolor_bsdf(o, eye_build)
    for m in o.data.materials:
        b = next((n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None)
        if b:
            b.inputs["Roughness"].default_value = 0.05
            if "Coat Weight" in b.inputs:
                b.inputs["Coat Weight"].default_value = 1.0
                b.inputs["Coat Roughness"].default_value = 0.02
for o in nila.parts.get("Eyebrows", []) + nila.parts.get("Eyelashes", []):
    M.recolor_bsdf(o, lambda nt, bsdf, c: M.mix(nt, c, (0.06, 0.035, 0.02), 0.9))

HEM = min((SHIRT.matrix_world @ v.co).z for v in SHIRT.data.vertices)
import bmesh  # noqa: E402
mw, mi = SHIRT.matrix_world, SHIRT.matrix_world.inverted()
for v in SHIRT.data.vertices:          # the tee's lower part a little looser, so the pants' pockets stay under it
    p = mw @ v.co
    f = M.smooth(HEM + 0.14, HEM + 0.01, p.z)
    if f > 0:
        v.co = mi @ (p + (mw.to_3x3() @ v.normal).normalized() * 0.011 * f)

# hair: part the fringe off the eyes (centre parting, locks pushed to the sides like the reference)
for o in nila.parts.get("Hair", []):
    mw, mi = o.matrix_world, o.matrix_world.inverted()
    for v in o.data.vertices:
        p = mw @ v.co
        d = p - EYE_C
        if d.y > 0.035 or d.z > 0.11:
            continue
        ax = abs(d.x)
        f = M.smooth(0.11, 0.02, d.z) * (1 - M.smooth(0.05, 0.085, ax)) * (1 - M.smooth(0.0, 0.035, d.y))
        if f <= 0:
            continue
        sx = 1.0 if d.x >= 0 else -1.0
        p.x += sx * 0.04 * f
        p.z += 0.045 * f
        p.y += 0.03 * f
        v.co = mi @ p
# hair: soft, a little sheen, with loose strands added as curves around the face
for o in nila.parts.get("Hair", []):
    for m in o.data.materials:
        b = next((n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None)
        if b:
            b.inputs["Roughness"].default_value = 0.45


def strand_mat():
    m = bpy.data.materials.new("Loose strands")
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (0.3, 0.18, 0.1, 1)
    b.inputs["Roughness"].default_value = 0.4
    return m


# ------------------------------------------------------------------ layered necklaces (cord + heart)
neck = bw("neck_01")
cord = bpy.data.materials.new("Cord")
cord.use_nodes = True
cb = cord.node_tree.nodes["Principled BSDF"]
cb.inputs["Base Color"].default_value = (0.03, 0.03, 0.035, 1)
cb.inputs["Roughness"].default_value = 0.35
silver = bpy.data.materials.new("Silver")
silver.use_nodes = True
sb = silver.node_tree.nodes["Principled BSDF"]
sb.inputs["Base Color"].default_value = (0.8, 0.8, 0.82, 1)
sb.inputs["Metallic"].default_value = 1.0
sb.inputs["Roughness"].default_value = 0.25
from mathutils.bvhtree import BVHTree  # noqa: E402
_dg = bpy.context.evaluated_depsgraph_get()


def world_tree(o):
    ev = o.evaluated_get(_dg)
    me = ev.to_mesh()
    t = BVHTree.FromPolygons([o.matrix_world @ v.co for v in me.vertices], [list(q.vertices) for q in me.polygons])
    ev.to_mesh_clear()
    return t


TREES = [world_tree(o) for o in (body, SHIRT)]
AX = Vector((EYE_C.x, neck.y, 0))            # vertical axis through the neck


def surface(z, a):
    """Outermost body/shirt surface point at height z in direction a (0 = front, -Y)."""
    d = Vector((math.sin(a), -math.cos(a), 0))
    o = Vector((AX.x, AX.y, z)) + d * 0.4
    best = None
    for t in TREES:
        hit = t.ray_cast(o, -d, 0.4)[0]
        if hit is not None and (best is None or (hit - o).length < (best - o).length):
            best = hit
    return best, d


NZ = neck.z - 0.035
for k, drop in enumerate((0.025, 0.055, 0.09)):
    cu = bpy.data.curves.new(f"Necklace{k}", "CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth = 0.0022
    cu.bevel_resolution = 2
    sp = cu.splines.new("NURBS")
    n = 32
    sp.points.add(n - 1)
    low = None
    for i in range(n):
        a = 2 * math.pi * i / n
        front = max(0.0, math.cos(a))                  # 1 at the front
        z = neck.z + 0.02 + 0.006 * k - (0.045 + drop) * front ** 1.6
        p, d = surface(z, a)
        if p is None or (p - Vector((AX.x, AX.y, z))).length > 0.11:
            p = Vector((AX.x, AX.y, z)) + d * 0.07
        p = p + d * (0.0028 + 0.0012 * k)
        sp.points[i].co = (p.x, p.y, p.z, 1)
        if i == 0:
            low = p
    sp.use_cyclic_u = True
    sp.order_u = 4
    ob = bpy.data.objects.new(cu.name, cu)
    sc.collection.objects.link(ob)
    ob.data.materials.append(cord)
    M.attach(ob, rig, "spine_03")
    if k == 1:   # small heart pendant
        hc = low + Vector((0, -0.006, -0.011))
        parts = []
        for dx in (-0.0045, 0.0045):
            bpy.ops.mesh.primitive_uv_sphere_add(radius=0.0055, location=hc + Vector((dx, 0, 0.002)))
            parts.append(bpy.context.object)
        bpy.ops.mesh.primitive_cone_add(radius1=0.0098, depth=0.012, vertices=24,
                                        location=hc + Vector((0, 0, -0.0045)), rotation=(math.pi, 0, 0))
        parts.append(bpy.context.object)
        for o in parts:
            o.scale.y = 0.45
        bpy.ops.object.select_all(action="DESELECT")
        for o in parts:
            o.select_set(True)
        bpy.context.view_layer.objects.active = parts[0]
        bpy.ops.object.join()
        heart = bpy.context.object
        heart.name = "Heart"
        heart.data.materials.append(silver)
        bpy.ops.object.shade_smooth()
        M.attach(heart, rig, "spine_03")

# ------------------------------------------------------------------ studio
for o in list(sc.collection.objects):
    pass
m_bg = bpy.data.materials.new("Backdrop")
m_bg.use_nodes = True
bb = m_bg.node_tree.nodes["Principled BSDF"]
bb.inputs["Base Color"].default_value = (0.055, 0.055, 0.06, 1)
bb.inputs["Roughness"].default_value = 0.8
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, 0))
bg = bpy.context.object
bg.name = "Cyclorama"
bme = bg.data
# curved backdrop: floor -> wall with a soft bend
import bmesh  # noqa: E402
bm = bmesh.new()
prof = []
for i in range(9):
    prof.append((0.0, -4 + i * 0.5, 0.0))
for i in range(1, 9):
    a = (math.pi / 2) * i / 8
    prof.append((0.0, 0.0 + 1.0 * math.sin(a), 1.0 - 1.0 * math.cos(a)))
for i in range(1, 7):
    prof.append((0.0, 1.0, 1.0 + i * 0.6))
rows = []
for x in (-5, 5):
    rows.append([bm.verts.new((x, y + 2.0, z)) for _, y, z in prof])
for i in range(len(prof) - 1):
    bm.faces.new((rows[0][i], rows[1][i], rows[1][i + 1], rows[0][i + 1]))
bm.to_mesh(bme)
bm.free()
bg.data.materials.append(m_bg)
for poly in bg.data.polygons:
    poly.use_smooth = True

# key (soft, warm, from front-left above), fill (cool, right), rim x2 (behind), small eye-light
P.area_light((-1.4, -1.8, 2.3), (0, 0, 1.4), 260, 1.6, (1.0, 0.9, 0.8), name="Key")
P.area_light((1.8, -1.6, 1.5), (0, 0, 1.35), 90, 2.2, (0.75, 0.85, 1.0), name="Fill")
P.area_light((-1.2, 1.4, 2.0), (0, 0, 1.4), 220, 0.9, (1.0, 0.85, 0.7), name="Rim L")
P.area_light((1.3, 1.3, 1.9), (0, 0, 1.4), 180, 0.9, (0.85, 0.9, 1.0), name="Rim R")
world = bpy.data.worlds.new("World")
sc.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs[0].default_value = (0.05, 0.05, 0.055, 1)
world.node_tree.nodes["Background"].inputs[1].default_value = 0.6

# ------------------------------------------------------------------ motion: the standard motion system
# (cast/motion.py) — full-rate mocap, overlapping smootherstep cross-fades entered at the best-matching pose,
# light smoothing, then IK foot planting. Root motion is kept so weight shifts move the hips, not the feet.
O = Vector((0, 0, 0))
FACING = 180          # looks along -Y, at the camera
# 0-4 s calm breathing, glances away and back; ~3.3-7.3 s thinking (hand to chest, weight shift);
# ~6.8-8.5 s nods "yes"; ~8.1-11 s both hands forward "listen…", then settles.
smooth = MO.smooth
tl = MO.Timeline(nila, FPS)
tl.add(CL["breathing_idle"], 1, 100, offset=O, facing=FACING, in_place=False, src_from=1.0)
tl.add(CL["thinking"], 74, 104, blend=30, match=0.6, offset=O, facing=FACING, in_place=False, speed=0.85)
tl.add(CL["head_nod_yes"], 162, 46, blend=16, match=0.4, offset=O, facing=FACING, in_place=False)
tl.add(CL["hands_forward_gesture"], 194, 71, blend=18, match=0.4, offset=O, facing=FACING, in_place=False)
tl.build()

# head/eyes follow a look target that moves in quick darts with holds (how people really look)
look = P.empty("Look")
for bn, inf in (("head", 0.45), ("neck_01", 0.2)):
    c = rig.pose.bones[bn].constraints.new("DAMPED_TRACK")
    c.target, c.track_axis, c.influence = look, "TRACK_Z", inf
cam_pos = Vector((0, -2.2, 1.45))
HEADP = bw("head")
targets = [  # (frame, offset from camera in metres) : at camera, side glance, back, down while thinking...
    (1, (0, 0, 0)), (30, (0, 0, 0)), (36, (-0.9, 0, 0.25)), (58, (-0.9, 0, 0.25)), (64, (0.1, 0, 0.05)),
    (92, (0.1, 0, 0.05)), (100, (0.5, 0, -0.55)), (140, (0.6, 0, -0.45)), (150, (0.2, 0, 0.35)),
    (166, (0, 0, 0)), (264, (0, 0, 0))]
for f, d in targets:
    look.location = cam_pos + Vector(d)
    look.keyframe_insert("location", frame=f)
for fc in look.animation_data.action.fcurves if hasattr(look.animation_data.action, "fcurves") else []:
    for kp in fc.keyframe_points:
        kp.interpolation = "BEZIER"

# face: blinks (some on head turns), a smile building from the nod, slight talking with the gesture
sk = body.data.shape_keys
glance = {36, 64, 100, 150}
for f in range(1, N + 1):
    t = (f - 1) / FPS
    smile = 0.15 + 0.55 * smooth((f - 160) / 30) - 0.25 * smooth((f - 205) / 15) + 0.2 * smooth((f - 240) / 20)
    st = dict(t=t, seed=nila.seed, talking=(208 <= f <= 236), worry=0.0, smile=smile)
    vals = anim.face(st)
    for g in glance:        # people blink as their eyes jump to a new place
        u = (f - g) / 3.0
        if -1 <= u <= 1:
            vals["eye-left-closure"] = vals["eye-right-closure"] = max(vals["eye-left-closure"], 1 - abs(u))
    if 100 <= f <= 150:     # thinking: brows up a little
        vals["eyebrows-left-inner-up"] = vals["eyebrows-right-inner-up"] = 0.35
    for k, v in vals.items():
        if k in nila.keys:
            nila._put(sk, f'key_blocks["{k}"].value', 0, f, max(0.0, min(1.0, v)))
nila.flush()
MO.foot_lock(nila, 1, N, free=tl.transitions)
FINDINGS = MO.check(nila, 1, N, os.path.join(HERE, "motion_report.txt"))

# ------------------------------------------------------------------ camera: full body -> bust, slow
cam_d = bpy.data.cameras.new("Cam")
cam = bpy.data.objects.new("Cam", cam_d)
sc.collection.objects.link(cam)
sc.camera = cam
aim = P.empty("Aim")
tc = cam.constraints.new("TRACK_TO")
tc.target, tc.track_axis, tc.up_axis = aim, "TRACK_NEGATIVE_Z", "UP_Y"
top = HEADP.z + 0.15
if FACE:
    keys = [(1, (0.2, -1.15, top - 0.1), (0, 0, top - 0.1), 85), (N, (0.2, -1.15, top - 0.1), (0, 0, top - 0.1), 85)]
else:
    keys = [(1, (0.35, -4.4, 1.05), (0, 0, 0.85), 50), (90, (0.3, -3.6, 1.15), (0, 0, 0.95), 50),
            (190, (0.2, -1.9, 1.38), (0, 0, top - 0.32), 50), (N, (0.15, -1.6, 1.42), (0, 0, top - 0.26), 50)]
for f, loc, at, lens in keys:
    cam.location, aim.location, cam_d.lens = loc, at, lens
    cam.keyframe_insert("location", frame=f)
    aim.keyframe_insert("location", frame=f)
    cam_d.keyframe_insert("lens", frame=f)
cam_d.dof.use_dof = True
eyefocus = P.empty("Eye focus", EYE_C + Vector((0, -0.03, 0)))
M.attach(eyefocus, rig, "head")
cam_d.dof.focus_object = eyefocus
if FACE:
    tc.target = eyefocus
cam_d.dof.aperture_fstop = 2.8

# ------------------------------------------------------------------ render
if "--cycles" in argv or ANIM or "--save" in argv:
    sc.render.engine = "CYCLES"
    cy = sc.cycles
    cy.device, cy.samples, cy.use_adaptive_sampling = "CPU", int(arg("--samples", default=16)), True
    cy.use_denoising, cy.denoiser = True, "OPENIMAGEDENOISE"
    cy.max_bounces, cy.transparent_max_bounces = 4, 24
else:
    sc.render.engine = "BLENDER_EEVEE"
ee = sc.eevee
ee.taa_render_samples = int(arg("--samples", default=32))
for prop, v in (("use_raytracing", True), ("use_shadows", True), ("shadow_ray_count", 2), ("shadow_step_count", 8)):
    if hasattr(ee, prop):
        setattr(ee, prop, v)
if hasattr(ee, "use_fast_gi"):
    ee.use_fast_gi = True
sc.view_settings.view_transform = "AgX"
try:
    sc.view_settings.look = "AgX - Punchy"
except TypeError:
    pass
sc.view_settings.exposure = 0.3
pct = int(arg("--pct", default=100))
sc.render.resolution_x, sc.render.resolution_y = 1080, 1920
sc.render.resolution_percentage = pct
sc.render.image_settings.file_format = "PNG"
sc.frame_start, sc.frame_end = 1, N

if STILL:
    os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
    for f in STILL.split(","):
        sc.frame_set(int(f))
        sc.render.filepath = os.path.join(HERE, "out", f"{'face' if FACE else 'still'}_{int(f):03d}.png")
        bpy.ops.render.render(write_still=True)
if ANIM:
    a, b = int(ANIM[0]), int(ANIM[1])
    d = os.path.join(HERE, "frames")
    os.makedirs(d, exist_ok=True)
    for f in range(a, b + 1):
        p = os.path.join(d, f"f_{f:04d}.png")
        if os.path.exists(p) and os.path.getsize(p) > 0:
            continue
        sc.frame_set(f)
        sc.render.filepath = p
        bpy.ops.render.render(write_still=True)
if "--save" in argv:
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(HERE, "nila.blend"))
