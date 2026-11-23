"""10-second realistic zombie test: Arian in a dark school corridor.

python scene.py --still 40,120,180,225   -> test/still_####.png
python scene.py --render                  -> frames/f_####.png (skips existing)
"""
import bpy, sys, os, math, random
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
bpy.ops.wm.read_factory_settings(use_empty=True)
import chars as C
from chars import X, Y, Z

FPS, N = 24, 240
random.seed(7)


def T(f):
    return (f - 1) / FPS


def sm(a, b, t):
    x = min(1.0, max(0.0, (t - a) / (b - a)))
    return x * x * (3 - 2 * x)


sc = bpy.context.scene
col = sc.collection


# ------------------------------------------------------------------ materials
def mat(name, color, rough=0.5, metal=0.0, emit=None, strength=0.0):
    m = bpy.data.materials.new(name)
    nt = m.node_tree
    p = nt.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = color + (1,)
    p.inputs["Roughness"].default_value = rough
    p.inputs["Metallic"].default_value = metal
    if emit:
        p.inputs["Emission Color"].default_value = emit + (1,)
        p.inputs["Emission Strength"].default_value = strength
    return m


def grime(m, scale=4.0, dark=0.6, rough_var=0.25):
    nt = m.node_tree
    p = nt.nodes["Principled BSDF"]
    base = p.inputs["Base Color"].default_value[:]
    n = nt.nodes.new("ShaderNodeTexNoise")
    n.inputs["Scale"].default_value = scale
    n.inputs["Detail"].default_value = 8
    r = nt.nodes.new("ShaderNodeMapRange")
    r.inputs["From Min"].default_value = 0.35
    r.inputs["From Max"].default_value = 0.75
    nt.links.new(n.outputs["Fac"], r.inputs["Value"])
    mx = nt.nodes.new("ShaderNodeMix")
    mx.data_type = "RGBA"
    mx.inputs[6].default_value = base
    mx.inputs[7].default_value = tuple(c * dark for c in base[:3]) + (1,)
    nt.links.new(r.outputs["Result"], mx.inputs[0])
    nt.links.new(mx.outputs[2], p.inputs["Base Color"])
    rr = nt.nodes.new("ShaderNodeMapRange")
    rr.inputs["To Min"].default_value = p.inputs["Roughness"].default_value - rough_var
    rr.inputs["To Max"].default_value = p.inputs["Roughness"].default_value + rough_var
    nt.links.new(n.outputs["Fac"], rr.inputs["Value"])
    nt.links.new(rr.outputs["Result"], p.inputs["Roughness"])
    b = nt.nodes.new("ShaderNodeBump")
    b.inputs["Strength"].default_value = 0.08
    nt.links.new(n.outputs["Fac"], b.inputs["Height"])
    nt.links.new(b.outputs["Normal"], p.inputs["Normal"])
    return m


def floor_mat():
    m = mat("Floor", (0.5, 0.48, 0.44), 0.3)
    nt = m.node_tree
    p = nt.nodes["Principled BSDF"]
    tc = nt.nodes.new("ShaderNodeTexCoord")
    br = nt.nodes.new("ShaderNodeTexBrick")
    br.offset = 0.0
    br.inputs["Color1"].default_value = (0.52, 0.5, 0.46, 1)
    br.inputs["Color2"].default_value = (0.4, 0.39, 0.37, 1)
    br.inputs["Mortar"].default_value = (0.18, 0.17, 0.16, 1)
    br.inputs["Scale"].default_value = 1.0
    br.inputs["Mortar Size"].default_value = 0.008
    br.inputs["Brick Width"].default_value = 0.4
    br.inputs["Row Height"].default_value = 0.4
    nt.links.new(tc.outputs["Object"], br.inputs["Vector"])
    nz = nt.nodes.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 2.5
    nz.inputs["Detail"].default_value = 8
    mx = nt.nodes.new("ShaderNodeMix")
    mx.data_type = "RGBA"
    mx.blend_type = "MULTIPLY"
    mx.inputs[0].default_value = 0.6
    nt.links.new(br.outputs["Color"], mx.inputs[6])
    nt.links.new(nz.outputs["Color"], mx.inputs[7])
    nt.links.new(mx.outputs[2], p.inputs["Base Color"])
    rr = nt.nodes.new("ShaderNodeMapRange")
    rr.inputs["To Min"].default_value = 0.12
    rr.inputs["To Max"].default_value = 0.55
    nt.links.new(nz.outputs["Fac"], rr.inputs["Value"])
    nt.links.new(rr.outputs["Result"], p.inputs["Roughness"])
    bp = nt.nodes.new("ShaderNodeBump")
    bp.inputs["Strength"].default_value = 0.15
    nt.links.new(br.outputs["Fac"], bp.inputs["Height"])
    nt.links.new(bp.outputs["Normal"], p.inputs["Normal"])
    return m


def box(loc, size, m, name="box", rot=0.0):
    bpy.ops.mesh.primitive_cube_add(location=loc)
    o = bpy.context.object
    o.name = name
    o.scale = (size[0] / 2, size[1] / 2, size[2] / 2)
    o.rotation_euler.z = rot
    o.data.materials.append(m)
    return o


def plane(loc, size, m, rot=(0, 0, 0), name="plane"):
    bpy.ops.mesh.primitive_plane_add(location=loc, rotation=rot)
    o = bpy.context.object
    o.name = name
    o.scale = (size[0] / 2, size[1] / 2, 1)
    o.data.materials.append(m)
    return o


# ------------------------------------------------------------------ corridor
W, Y0, Y1, H = 1.6, -4.0, 16.0, 3.0
L = Y1 - Y0
YC = (Y0 + Y1) / 2
box((0, YC, -0.05), (2 * W, L, 0.1), floor_mat(), "Floor")
ceil = grime(mat("Ceiling", (0.62, 0.6, 0.56), 0.8), 1.5, 0.75)
box((0, YC, H + 0.05), (2 * W, L, 0.1), ceil, "Ceiling")
low = grime(mat("Wall low", (0.14, 0.22, 0.21), 0.45), 3.0, 0.65)
up = grime(mat("Wall up", (0.62, 0.58, 0.5), 0.7), 2.0, 0.75)
rail = mat("Rail", (0.08, 0.1, 0.1), 0.4)
for s in (-1, 1):
    box((s * (W + 0.05), YC, 0.55), (0.1, L, 1.1), low, "Wall low")
    box((s * (W + 0.05), YC, 2.05), (0.1, L, 1.9), up, "Wall up")
    box((s * (W - 0.01), YC, 1.1), (0.03, L, 0.05), rail, "Rail")
box((0, Y0 - 0.05, H / 2), (2 * W, 0.1, H), up, "Back wall")
box((0, Y1 + 0.05, 0.55), (2 * W, 0.1, 1.1), low, "End low")
box((-1.05, Y1 + 0.05, 2.05), (1.1, 0.1, 1.9), up, "End up L")
box((1.05, Y1 + 0.05, 2.05), (1.1, 0.1, 1.9), up, "End up R")
box((0, Y1 + 0.05, 2.75), (1.0, 0.1, 0.5), up, "End up T")
night = mat("Night", (0, 0, 0), 1.0, emit=(0.18, 0.24, 0.36), strength=0.8)
plane((0, Y1 + 0.08, 1.8), (1.0, 1.4), night, (math.pi / 2, 0, 0), "Window")
frame = mat("Frame", (0.2, 0.2, 0.2), 0.5)
box((0, Y1, 1.8), (0.04, 0.06, 1.4), frame, "Mullion")
box((0, Y1, 1.8), (1.0, 0.06, 0.04), frame, "Transom")

# lockers on the right wall
lock = grime(mat("Locker", (0.2, 0.27, 0.36), 0.38, 0.55), 5.0, 0.6, 0.2)
vent = mat("Vent", (0.02, 0.02, 0.02), 0.8)
handle = mat("Handle", (0.5, 0.5, 0.5), 0.25, 1.0)
y = -1.0
while y < 12.5:
    box((W - 0.23, y, 0.95), (0.45, 0.43, 1.9), lock, "Locker")
    plane((W - 0.459, y, 1.68), (0.25, 0.12), vent, (math.pi / 2, 0, math.pi / 2), "Vent")
    box((W - 0.465, y + 0.13, 1.0), (0.02, 0.03, 0.12), handle, "Handle")
    y += 0.45
box((W - 0.23, 5.75, 1.92), (0.46, 13.6, 0.05), lock, "Locker top")

# doors on the left wall
wood = grime(mat("Door", (0.3, 0.17, 0.08), 0.45), 6.0, 0.7)
glass = mat("Door glass", (0.02, 0.025, 0.03), 0.05)
for dy in (1.5, 7.5, 13.0):
    box((-W + 0.03, dy, 1.05), (0.06, 0.95, 2.1), wood, "Door")
    box((-W + 0.05, dy, 2.14), (0.08, 1.1, 0.08), frame, "Door head")
    for s in (-1, 1):
        box((-W + 0.05, dy + s * 0.51, 1.07), (0.08, 0.08, 2.15), frame, "Door jamb")
    plane((-W + 0.065, dy, 1.6), (0.35, 0.55), glass, (math.pi / 2, 0, -math.pi / 2), "Door window")
    box((-W + 0.08, dy - 0.36, 1.0), (0.04, 0.12, 0.03), handle, "Door handle")

# notice board with blank papers
cork = grime(mat("Cork", (0.42, 0.28, 0.16), 0.9), 20.0, 0.7)
box((-W + 0.02, 4.5, 1.55), (0.03, 1.6, 0.9), cork, "Board")
pap = [mat(f"Paper{i}", c, 0.8) for i, c in enumerate([(0.85, 0.84, 0.8), (0.86, 0.8, 0.5), (0.7, 0.8, 0.85)])]
for i in range(6):
    plane((-W + 0.04, 3.9 + 0.22 * i + random.uniform(-0.03, 0.03), 1.55 + random.uniform(-0.2, 0.2)),
          (0.18, 0.25), pap[i % 3], (math.pi / 2, random.uniform(-0.1, 0.1), -math.pi / 2), "Note")
# papers and a dropped bag on the floor
for i in range(14):
    plane((random.uniform(-1.1, 0.9), random.uniform(0.0, 13.0), 0.003 + i * 0.0003), (0.21, 0.29),
          pap[i % 3], (0, 0, random.uniform(0, 6.28)), "Floor paper")
bag = grime(mat("Bag", (0.12, 0.14, 0.2), 0.7), 8.0, 0.6)
box((0.7, 9.0, 0.12), (0.32, 0.45, 0.24), bag, "Bag", rot=0.5)

# ceiling lights (each gets its own emissive material so it can flicker)
PANELS = {}
for py in (-2.0, 1.0, 4.0, 7.0, 10.0, 13.0):
    m = mat(f"Panel{py}", (0.9, 0.9, 0.9), 0.4, emit=(0.85, 0.92, 1.0), strength=4.0)
    plane((0, py, H - 0.01), (0.35, 1.25), m, (math.pi, 0, 0), "Panel")
    bpy.ops.object.light_add(type="AREA", location=(0, py, H - 0.05))
    li = bpy.context.object
    li.data.shape = "RECTANGLE"
    li.data.size, li.data.size_y = 0.35, 1.25
    li.data.energy = 45
    li.data.color = (0.86, 0.93, 1.0)
    PANELS[py] = (li, m)
w = bpy.data.worlds.new("W")
sc.world = w
w.color = (0.01, 0.012, 0.016)


def flicker(py, pattern):
    """pattern: list of (t, level 0..1). Constant steps."""
    li, m = PANELS[py]
    p = m.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
    for t, lv in pattern:
        f = int(t * FPS) + 1
        li.data.energy = 45 * lv
        li.data.keyframe_insert("energy", frame=f)
        p.default_value = 4.0 * lv
        p.keyframe_insert("default_value", frame=f)
    for a in (li.data.animation_data.action, m.node_tree.animation_data.action):
        for fc in _fcurves(a):
            for k in fc.keyframe_points:
                k.interpolation = "CONSTANT"


def _fcurves(action):
    if hasattr(action, "fcurves") and len(action.fcurves):
        return list(action.fcurves)
    out = []
    for layer in getattr(action, "layers", []):
        for strip in layer.strips:
            for cb in strip.channelbags:
                out.extend(cb.fcurves)
    return out


def rand_flicker(t0, t1, on=1.0, seed=0):
    r = random.Random(seed)
    pts, t = [], t0
    while t < t1:
        pts.append((t, r.choice([0.0, 0.05, on * 0.4, on])))
        t += r.uniform(0.04, 0.22)
    return pts


flicker(13.0, [(0, 0.0)])
flicker(10.0, [(0, 0.0)] + rand_flicker(2.2, 3.4, 1.0, 1) + [(3.4, 0.35)] + rand_flicker(6.0, 8.4, 0.8, 2) + [(8.4, 0.0)])
flicker(7.0, [(0, 1.0)] + rand_flicker(6.4, 8.5, 1.0, 3) + [(8.5, 0.6)])
flicker(4.0, [(0, 1.0), (8.5, 1.0)] + rand_flicker(8.6, 9.7, 1.0, 4) + [(9.7, 0.0)])

# ------------------------------------------------------------------ characters
ar, arig, ap = C.build("Arian", gender=1.0, age=0.4, height=0.6, skin="young_caucasian_male", hair="short02",
                       brow="eyebrow001", clothes=["namuhekam_male_polo_shirt", "cortu_cargo_pants", "shoes01"])
C.tint(ar, (0.86, 0.69, 0.54))
for o in ap.get("Hair", []) + ap.get("Eyebrows", []):
    C.tint(o, (0.1, 0.07, 0.05))
for o in ap.get("Clothes", []):
    if "polo" in o.name:
        C.tint(o, (0.3, 0.38, 0.55))
ak = C.add_expr(ar, ["eyebrows-left-inner-up", "eyebrows-right-inner-up", "eye-left-opened-up",
                     "eye-right-opened-up", "mouth-open", "mouth-depression"])

zb, zrig, zp = C.build("Zombie", gender=1.0, age=0.62, weight=0.3, muscle=0.3, skin="middleage_caucasian_male",
                       hair="short04", brow="eyebrow006", clothes=["male_worksuit01", "shoes03"])
C.zombie_skin(zb)
for o in zp.get("Hair", []):
    C.tint(o, (0.09, 0.08, 0.07))
for o in zp.get("Eyes", []):
    C.dead_eyes(o)
for o in zp.get("Clothes", []):
    C.dirty_cloth(o, (0.22, 0.2, 0.16))
zk = C.add_expr(zb, ["mouth-open", "mouth-retraction", "eyebrows-left-down", "eyebrows-right-down",
                     "eye-left-opened-up", "eye-right-opened-up", "nose-left-elevation", "nose-right-elevation"])


def arian_at(t):
    if t < 6.0:
        yy = 6.6 - min(t, 3.2) - 0.2 * sm(3.2, 3.7, t)
        return Vector((0.05, yy, 0)), 0.0
    return Vector((0.05, 3.2 - 0.25 * sm(6.2, 8.4, t), 0)), math.pi


def arian_spec(t):
    a = 1 - sm(3.2, 3.7, t)
    ph = 2 * math.pi * 0.9 * t
    s, c = math.sin(ph), math.cos(ph)
    scared = sm(4.8, 5.6, t)
    br = math.sin(2 * math.pi * (0.3 + 0.5 * scared) * t) * (1 + 1.5 * scared)
    turn = sm(4.5, 5.2, t) if t < 6.0 else 0.0
    back = sm(6.2, 8.4, t) if t >= 6.0 else 0.0
    bs = math.sin(2 * math.pi * 0.9 * t) * back
    return {
        "thigh_l": [(X, -20 * a * s - 8 * max(0, bs))],
        "thigh_r": [(X, 20 * a * s - 8 * max(0, -bs))],
        "calf_l": [(X, 4 + 35 * a * max(0, c) + 12 * max(0, bs))],
        "calf_r": [(X, 4 + 35 * a * max(0, -c) + 12 * max(0, -bs))],
        "upperarm_l": [(Y, 44 - 12 * scared * (t >= 6)), (X, 14 * a * s - 10 * scared * (t >= 6))],
        "upperarm_r": [(Y, -44 + 12 * scared * (t >= 6)), (X, -14 * a * s - 10 * scared * (t >= 6))],
        "lowerarm_l": [(X, -6 - 25 * scared * (t >= 6))],
        "lowerarm_r": [(X, -6 - 25 * scared * (t >= 6))],
        "pelvis": [(Z, 4 * a * s)],
        "spine_01": [(Z, -3 * a * s)],
        "spine_02": [(X, 1.5 * br - 6 * back)],
        "spine_03": [(X, 1.0 * br), (Z, -14 * turn)],
        "neck_01": [(Z, -16 * turn), (X, 4 * (1 - scared))],
        "head": [(Z, -34 * turn), (X, 6 * a + 3 * (1 - scared))],
    }


def zombie_at(t):
    base = 12.5 - 0.9 * min(max(t - 2.0, 0), 6.5)
    lunge = 2.75 * sm(8.5, 9.6, t)
    x = 0.4 - 0.3 * sm(8.5, 9.6, t)
    return Vector((x, base - lunge, 0)), 0.0


def zombie_spec(t):
    lg = sm(8.5, 9.1, t)
    ph = 2 * math.pi * (0.55 * t + 0.6 * max(0, t - 8.5))
    s, c = math.sin(ph), math.cos(ph)
    jerk = 1.0 if (int(t * 3.1) % 7 == 3) else 0.0
    reach = 72 + 22 * lg
    return {
        "thigh_l": [(X, -18 * s - 15 * lg)],
        "thigh_r": [(X, 10 * s + 6 * lg)],
        "calf_l": [(X, 8 + 30 * max(0, c))],
        "calf_r": [(X, 14 + 10 * max(0, -c))],
        "pelvis": [(Z, 7 * s), (Y, 4 * c)],
        "spine_01": [(X, 10 + 8 * lg)],
        "spine_02": [(X, 9 + 10 * lg), (Y, 5 * s)],
        "spine_03": [(Y, -4 * s)],
        "neck_01": [(X, -6), (Y, 9 * (1 - lg))],
        "head": [(Y, 15 * (1 - lg) + 4 * math.sin(1.7 * t) + 12 * jerk), (X, -14 - 12 * lg), (Z, 6 * math.sin(0.8 * t))],
        "upperarm_l": [(Y, 45 - 15 * lg), (X, -reach + 7 * s)],
        "upperarm_r": [(Y, -45 + 15 * lg), (X, -(reach - 12) - 7 * s)],
        "lowerarm_l": [(X, -18 + 10 * lg)],
        "lowerarm_r": [(X, -10 + 8 * lg)],
        "hand_l": [(X, 15)],
        "hand_r": [(X, 20)],
    }


def zombie_keys(t):
    lg = sm(8.5, 9.0, t)
    g = 0.5 + 0.25 * math.sin(2.3 * t) + 0.15 * math.sin(5.1 * t)
    return {"mouth-open": max(g, lg), "mouth-retraction": 0.6 + 0.4 * lg, "eyebrows-left-down": 0.9,
            "eyebrows-right-down": 0.9, "eye-left-opened-up": 0.5 + 0.5 * lg, "eye-right-opened-up": 0.5 + 0.5 * lg,
            "nose-left-elevation": 0.5 + 0.5 * lg, "nose-right-elevation": 0.5 + 0.5 * lg}


def arian_keys(t):
    s = sm(4.8, 5.6, t)
    return {"eyebrows-left-inner-up": s, "eyebrows-right-inner-up": s, "eye-left-opened-up": s,
            "eye-right-opened-up": s, "mouth-open": 0.25 * s + 0.08 * s * math.sin(9 * t),
            "mouth-depression": 0.4 * s}


# ------------------------------------------------------------------ camera
cam = bpy.data.objects.new("Cam", bpy.data.cameras.new("Cam"))
col.objects.link(cam)
sc.camera = cam
cam.data.dof.use_dof = True
cam.data.sensor_width = 24


def head_pos(rig):
    return rig.matrix_world @ rig.pose.bones["head"].head


def shot(t):
    if t < 3.5:            # A: wide, Arian walks toward us; zombie appears far behind
        k = t / 3.5
        return (0.45, 0.9 - 0.3 * k, 1.42), (0.0, 8.0, 1.25), 32, 4.0, "arian"
    if t < 6.0:            # B: close on Arian's face, he hears it and turns
        h = head_pos(arig) + Vector((-0.09 * sm(4.5, 5.2, t), -0.07, 0.06))
        return tuple(h + Vector((-0.3, -0.75, 0.01))), tuple(h), 50, 2.0, "arian"
    if t < 8.5:            # C: over his shoulder, zombie shambles closer
        k = (t - 6.0) / 2.5
        return (-0.32, 2.45 - 0.2 * k, 1.6), (0.25, 8.5, 1.35), 38 + 6 * k, 2.8, "zombie"
    k = (t - 8.5) / 1.5    # D: his eyes, it lunges
    j = 0.012 + 0.03 * sm(8.9, 9.5, t)
    sh = Vector((random.uniform(-j, j), 0, random.uniform(-j, j)))
    return tuple(Vector((0.0, 3.25, 1.52)) + sh), (0.1, 6.0, 1.45), 26, 2.2, "zombie"


# ------------------------------------------------------------------ animate
arian_objs = [o for o in bpy.data.objects if o.name.startswith("Arian")]
for f in range(1, N + 1):
    t = T(f)
    p, r = arian_at(t)
    arig.location = p
    arig.location.z += 0.012 * (1 - sm(3.2, 3.7, t)) * abs(math.sin(2 * math.pi * 0.9 * t)) if t < 6 else 0
    arig.rotation_euler.z = r
    arig.keyframe_insert("location", frame=f)
    arig.keyframe_insert("rotation_euler", frame=f)
    C.pose(arig, arian_spec(t))
    C.key_pose(arig, f)
    for n, v in arian_keys(t).items():
        ak[n].value = v
        ak[n].keyframe_insert("value", frame=f)
    p, r = zombie_at(t)
    zrig.location = p
    zrig.location.z += 0.02 * abs(math.sin(2 * math.pi * 0.55 * t))
    zrig.rotation_euler.z = r
    zrig.keyframe_insert("location", frame=f)
    zrig.keyframe_insert("rotation_euler", frame=f)
    C.pose(zrig, zombie_spec(t))
    C.key_pose(zrig, f)
    for n, v in zombie_keys(t).items():
        zk[n].value = v
        zk[n].keyframe_insert("value", frame=f)
    sc.frame_set(f)
    loc, tgt, lens, fstop, focus = shot(t)
    cam.location = loc
    cam.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    cam.data.lens = lens
    cam.data.dof.aperture_fstop = fstop
    hp = head_pos(arig if focus == "arian" else zrig)
    cam.data.dof.focus_distance = max(0.3, (hp - Vector(loc)).length)
    cam.keyframe_insert("location", frame=f)
    cam.keyframe_insert("rotation_euler", frame=f)
    cam.data.keyframe_insert("lens", frame=f)
    cam.data.dof.keyframe_insert("aperture_fstop", frame=f)
    cam.data.dof.keyframe_insert("focus_distance", frame=f)
    for o in arian_objs:
        o.hide_render = t >= 8.5
        o.keyframe_insert("hide_render", frame=f)

# hard cuts: no interpolation on camera and character root
for ob in (cam, cam.data, arig, zrig):
    if ob.animation_data and ob.animation_data.action:
        for fc in _fcurves(ob.animation_data.action):
            if fc.data_path.startswith("pose."):
                continue
            for k in fc.keyframe_points:
                k.interpolation = "CONSTANT"

# ------------------------------------------------------------------ render
sc.render.engine = "CYCLES"
sc.cycles.samples = 20
sc.cycles.use_denoising = True
sc.cycles.max_bounces = 4
sc.cycles.caustics_reflective = sc.cycles.caustics_refractive = False
sc.render.resolution_x, sc.render.resolution_y = 576, 1024
sc.render.use_persistent_data = True
sc.render.fps = FPS
sc.frame_start, sc.frame_end = 1, N
sc.render.use_motion_blur = True
sc.render.motion_blur_position = "START"
sc.render.motion_blur_shutter = 0.4
sc.view_settings.view_transform = "AgX"
sc.view_settings.look = "AgX - Medium High Contrast"
sc.render.image_settings.file_format = "PNG"

args = sys.argv
if "--eevee" in args:
    sc.render.engine = "BLENDER_EEVEE"
    ee = sc.eevee
    ee.taa_render_samples = 32
    ee.use_raytracing = True
    ee.use_shadows = True
    ee.shadow_ray_count = 2
    ee.use_volumetric_shadows = False
    sc.render.resolution_x, sc.render.resolution_y = 720, 1280
if "--save" in args:
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(HERE, "zombie_test.blend"))
if "--still" in args:
    os.makedirs(os.path.join(HERE, "test"), exist_ok=True)
    for f in [int(x) for x in args[args.index("--still") + 1].split(",")]:
        sc.frame_set(f)
        sc.render.filepath = os.path.join(HERE, "test", f"still_{f:04d}.png")
        bpy.ops.render.render(write_still=True)
if "--render" in args:
    os.makedirs(os.path.join(HERE, "frames"), exist_ok=True)
    sc.render.filepath = os.path.join(HERE, "frames", "f_")
    sc.render.use_overwrite = False
    sc.render.use_placeholder = True
    bpy.ops.render.render(animation=True)
