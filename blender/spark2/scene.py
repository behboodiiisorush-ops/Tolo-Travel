"""«جرقه ۲» — the morning after: kitchen, hallway, courtyard; the street lamp; something stops in the sky.
    ../cast/bpy.sh scene.py --still 60,170 | --save   (render: chain.sh -> render.py, then sound.py, post.py)
"""
import bpy, sys, os, math, random
from mathutils import Vector, Matrix

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "cast"))
sys.path.append(os.path.join(HERE, "..", "shelter3"))
sys.path.append(os.path.join(HERE, "..", "studio"))
import cast, anim  # noqa: E402
import mocap2 as MC  # noqa: E402
import props as P  # noqa: E402
import mpfb_tools as MT  # noqa: E402
import look as LK  # noqa: E402
from captions import LINES, END, CLIPS  # noqa: E402
import lipsync  # noqa: E402

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
FPS = 24
N = int(END * FPS)
random.seed(7)

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.fps = FPS
CL = {k: MC.load(os.path.join(HERE, "..", "mocap", k + ".fbx")) for k in (
    "sitting_idle", "sitting_talking", "breathing_idle", "hands_forward_gesture", "walking_3", "pointing",
    "looking_around", "terrified")}


def T(t):
    return int(round(t * FPS)) + 1


def smooth(u):
    u = max(0.0, min(1.0, u))
    return u * u * (3 - 2 * u)


# ------------------------------------------------------------------ Arian (the look from the style board)
STYLE = dict(LK.STYLE)
for k_ in list(STYLE):
    if "eye-height" in k_:
        STYLE.pop(k_)
STYLE.update({"l-eye-scale-incr": 1.0, "r-eye-scale-incr": 1.0, "head-scale-vert-incr": 0.2,
              "nose-scale-horiz-decr": 0.7, "mouth-scale-horiz-decr": 0.2})
cast.STYLE = STYLE
cast.CAST["arian"] = dict(cast.CAST["arian"], age=0.42, height=0.55, weight=0.4, skin_tint=(0.86, 0.6, 0.46),
                          hair="culturalibre_hair_14", hair_col=(0.035, 0.025, 0.02), brow="eyebrow002",
                          clothes={"elvs_hooded_sweat_jacket1": (0.55, 0.06, 0.07),
                                   "cortu_cargo_pants": (0.07, 0.07, 0.08),
                                   "culturalibre_sneakers": (0.92, 0.9, 0.88)})
ar = cast.spawn("arian")
cast.cartoon_face(ar)
mom = cast.spawn("mom")
cast.cartoon_face(mom)
kian = cast.spawn("kian")
cast.cartoon_face(kian)

m_hp = P.mat("Headphones", (0.04, 0.04, 0.045), 0.35)
m_cush = P.mat("Cushion", (0.12, 0.12, 0.13), 0.8)
sc.frame_set(1)
bpy.context.view_layer.update()
neck = ar.rig.matrix_world @ ar.rig.pose.bones["neck_01"].head
hp = []
import bmesh  # noqa: E402
bpy.ops.mesh.primitive_torus_add(major_radius=0.1, minor_radius=0.014, location=neck + Vector((0, 0.01, -0.035)),
                                  major_segments=40)
band = bpy.context.object
band.scale = (1.05, 0.95, 1.0)
band.rotation_euler.x = math.radians(-18)
bm = bmesh.new()
bm.from_mesh(band.data)
bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.y < -0.035], context="VERTS")
bm.to_mesh(band.data)
bm.free()
band.data.materials.append(m_hp)
hp.append(band)
for sx in (-1, 1):
    a = neck + Vector((sx * 0.085, -0.075, -0.085))
    d = Vector((sx * 0.35, -1.0, 0.25)).normalized()
    hp.append(P.cyl(a - d * 0.02, a + d * 0.02, 0.05, m_hp, "Cup", 28))
    hp.append(P.cyl(a - d * 0.035, a - d * 0.02, 0.043, m_cush, "Cushion", 28))
for o in hp:
    MT.attach(o, ar.rig, "neck_01")

for o in ar.parts.get("Eyes", []):
    for slot in o.material_slots:
        b = next((n for n in slot.material.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None)
        if b:
            b.inputs["Roughness"].default_value = 0.04
            b.inputs["Coat Weight"].default_value = 1.0
            b.inputs["Coat Roughness"].default_value = 0.02
for kb in ar.keys.values():
    kb.slider_max = 2.0


def warm_skin(nt, col=(0.9, 0.62, 0.47, 1)):
    for n in list(nt.nodes):
        if n.type == "GROUP" and n.node_tree and not n.node_tree.get("warm"):
            n.node_tree["warm"] = 1
            warm_skin(n.node_tree, col)
        if n.type in ("BSDF_PRINCIPLED", "SUBSURFACE_SCATTERING", "BSDF_DIFFUSE"):
            key = "Base Color" if "Base Color" in n.inputs else "Color"
            s_ = n.inputs[key]
            mul = nt.nodes.new("ShaderNodeMix")
            mul.data_type, mul.blend_type = "RGBA", "MULTIPLY"
            mul.inputs["Factor"].default_value = 1.0
            mul.inputs["B"].default_value = col
            if s_.is_linked:
                nt.links.new(s_.links[0].from_socket, mul.inputs["A"])
            else:
                mul.inputs["A"].default_value = tuple(s_.default_value)
            nt.links.new(mul.outputs["Result"], s_)


warm_skin(ar.body.material_slots[0].material.node_tree)
for o in ar.parts.get("Eyebrows", []):
    for slot in o.material_slots:
        nt = slot.material.node_tree
        b = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
        al = b.inputs["Alpha"]
        if al.is_linked:
            m_ = nt.nodes.new("ShaderNodeMath")
            m_.operation, m_.use_clamp = "MULTIPLY", True
            m_.inputs[1].default_value = 3.0
            nt.links.new(al.links[0].from_socket, m_.inputs[0])
            nt.links.new(m_.outputs[0], al)

# ================================================================== sets (far apart, the camera cuts between them)
KX, HX, CX = 0.0, 20.0, 40.0          # kitchen, hallway, courtyard (x origin of each set)
SUNNY = (1.0, 0.95, 0.88)


def lamp(name, loc, energy, col, radius=0.15):
    l = bpy.data.lights.new(name, "POINT")
    l.energy, l.color, l.shadow_soft_size = energy, col, radius
    o = bpy.data.objects.new(name, l)
    sc.collection.objects.link(o)
    o.location = loc
    return l


def strength(mat):
    n = next(n for n in mat.node_tree.nodes if n.type in ("EMISSION", "BSDF_PRINCIPLED"))
    return n.inputs["Strength"] if "Strength" in n.inputs else n.inputs["Emission Strength"]


# ---------------- kitchen (morning): table in the middle, Arian (south side) faces +Y, mom (north) faces -Y
m_kwall = P.mat("Kitchen wall", (0.85, 0.78, 0.62), 0.85)
m_tile = P.wood("Kitchen floor", (0.6, 0.45, 0.32), planks=True)
m_wood = P.wood("Wood", (0.6, 0.4, 0.24), planks=False)
m_cab = P.mat("Cabinet", (0.35, 0.55, 0.5), 0.6)
m_top = P.mat("Counter", (0.9, 0.9, 0.88), 0.35)
m_dark = P.mat("Dark", (0.05, 0.05, 0.06), 0.4)
P.box((KX, 0, -0.05), (5, 5, 0.1), m_tile, "K floor")
P.box((KX, 0, 2.85), (5, 5, 0.1), P.mat("K ceil", (0.92, 0.9, 0.86), 0.9), "K ceil")
P.box((KX, 2.5, 1.4), (5, 0.1, 2.8), m_kwall, "K back")
P.box((KX + 2.5, 0, 1.4), (0.1, 5, 2.8), m_kwall, "K right")
P.box((KX, -2.5, 1.4), (5, 0.1, 2.8), m_kwall, "K front")
# left wall with a sunny window (x = -2.5, y -0.6..0.9, z 0.9..2.2)
P.box((KX - 2.5, -1.55, 1.4), (0.1, 1.9, 2.8), m_kwall, "K left a")
P.box((KX - 2.5, 1.7, 1.4), (0.1, 1.6, 2.8), m_kwall, "K left b")
P.box((KX - 2.5, 0.15, 0.45), (0.1, 1.5, 0.9), m_kwall, "K sill")
P.box((KX - 2.5, 0.15, 2.5), (0.1, 1.5, 0.6), m_kwall, "K lintel")
P.plane((KX - 4.0, 0.15, 1.5), (6, 4), P.emit("K outside", (0.75, 0.85, 1.0), 2.0), (math.pi / 2, 0, math.pi / 2),
        "K outside")
# cabinets + counter along the back wall, fridge
P.box((KX + 0.6, 2.15, 0.45), (2.8, 0.6, 0.9), m_cab, "Cabinets", bevel=0.01)
P.box((KX + 0.6, 2.15, 0.92), (2.85, 0.65, 0.04), m_top, "Counter")
P.box((KX + 0.6, 2.3, 1.85), (2.8, 0.35, 0.7), m_cab, "Wall cabinets", bevel=0.01)
P.box((KX + 2.1, 1.9, 0.95), (0.7, 0.7, 1.9), P.mat("Fridge", (0.92, 0.92, 0.93), 0.3), "Fridge", bevel=0.03)
P.cyl((KX - 0.5, 2.2, 0.94), (KX - 0.5, 2.2, 1.12), 0.09, P.mat("Kettle", (0.8, 0.2, 0.15), 0.3), "Kettle")
# table, chairs, breakfast
TABLE = Vector((KX, 0.2, 0))
P.box((TABLE.x, TABLE.y, 0.74), (1.3, 0.85, 0.05), m_wood, "Table")
for dx in (-0.58, 0.58):
    for dy in (-0.35, 0.35):
        P.box((TABLE.x + dx, TABLE.y + dy, 0.37), (0.05, 0.05, 0.74), m_wood, "Table leg")
for cy, back in ((-0.45, -0.7), (0.85, 1.1)):
    P.box((KX, cy, 0.45), (0.46, 0.46, 0.05), m_wood, "K chair seat", bevel=0.01)
    P.box((KX, back, 0.8), (0.46, 0.05, 0.65), m_wood, "K chair back", bevel=0.01)
m_plate = P.mat("Plate", (0.95, 0.95, 0.93), 0.3)
for py in (-0.05, 0.45):
    P.cyl((KX, py, 0.765), (KX, py, 0.78), 0.12, m_plate, "Plate")
P.box((KX - 0.02, -0.05, 0.79), (0.12, 0.08, 0.02), P.mat("Bread", (0.85, 0.6, 0.3), 0.8), "Bread")
GLASS = Vector((KX + 0.22, -0.05, 0.77))
m_glass = P.mat("Glass", (0.8, 0.9, 1.0), 0.05)
P.cyl(GLASS, GLASS + Vector((0, 0, 0.13)), 0.035, m_glass, "Glass")
P.cyl(GLASS, GLASS + Vector((0, 0, 0.09)), 0.032, P.mat("Juice", (1.0, 0.55, 0.1), 0.2), "Juice")
P.cyl((KX - 0.3, 0.55, 0.77), (KX - 0.3, 0.55, 0.88), 0.04, P.mat("Cup", (0.3, 0.5, 0.8), 0.4), "Mom cup")
# the pendant lamp over the table (it flickers when Arian touches the glass)
PEND = Vector((KX, 0.2, 2.1))
P.cyl(PEND + Vector((0, 0, 0.1)), (KX, 0.2, 2.8), 0.006, m_dark, "Pendant cord")
m_pend = P.emit("Pendant", (1.0, 0.82, 0.55), 6.0)
P.cyl(PEND, PEND + Vector((0, 0, 0.12)), 0.18, m_pend, "Pendant shade")
L_pend = lamp("Pendant light", PEND - Vector((0, 0, 0.08)), 70, (1.0, 0.8, 0.55), 0.2)
P.area_light((KX - 2.2, 0.15, 1.6), (0, -math.pi / 2, 0), 260, 1.4, (1.0, 0.92, 0.8), name="K window")
P.area_light((KX + 0.5, -1.0, 2.7), (0, 0, 0), 60, 2.0, (1.0, 0.95, 0.9), name="K fill")

# ---------------- hallway / stairwell landing: a corridor along Y with wall lamps
m_hwall = P.mat("Hall wall", (0.7, 0.72, 0.66), 0.85)
P.box((HX, 0, -0.05), (2.0, 14, 0.1), P.mat("Hall floor", (0.45, 0.42, 0.4), 0.6), "H floor")
P.box((HX, 0, 2.75), (2.0, 14, 0.1), P.mat("Hall ceil", (0.85, 0.85, 0.82), 0.9), "H ceil")
for sx in (-1, 1):
    P.box((HX + sx * 0.85, 0, 1.4), (0.1, 14, 2.8), m_hwall, "H wall")
    P.box((HX + sx * 0.79, 0, 0.5), (0.02, 14, 1.0), P.mat("Hall dado", (0.35, 0.4, 0.45), 0.6), "H dado")
P.box((HX, 7.0, 1.4), (2.0, 0.1, 2.8), m_hwall, "H end")
for k in range(4):                                       # apartment doors
    P.box((HX + (0.79 if k % 2 else -0.79), 4.0 - k * 2.6, 1.05), (0.06, 0.95, 2.1),
          P.wood(f"Apt door{k}", (0.5, 0.33, 0.2), planks=False), "Apt door")
HALL_LAMPS = []
for k, y in enumerate((5.0, 3.0, 1.0, -1.0, -3.0, -5.0)):
    sx = -1 if k % 2 else 1
    me = P.emit(f"Wall lamp{k}", (1.0, 0.85, 0.6), 3.0)
    P.sphere((HX + sx * 0.76, y, 2.05), 0.09, me, "Wall lamp")
    HALL_LAMPS.append((y, lamp(f"Hall light{k}", (HX + sx * 0.6, y, 2.0), 25, (1.0, 0.82, 0.55), 0.1), me))

# ---------------- courtyard between the two buildings (day)
m_ground = P.mat("Courtyard", (0.42, 0.4, 0.38), 0.85)
P.box((CX, 0, -0.05), (40, 40, 0.1), m_ground, "Ground")
m_fac_a = P.mat("Facade A", (0.78, 0.62, 0.5), 0.9)
m_fac_b = P.mat("Facade B", (0.6, 0.66, 0.72), 0.9)
P.box((CX, -6.5, 7), (20, 1, 14), m_fac_a, "Building A")
P.box((CX, 9.0, 7), (20, 1, 14), m_fac_b, "Building B")
win = P.mat("Window", (0.15, 0.2, 0.28), 0.1)
for ix in range(-5, 6):
    for iz in range(1, 5):
        P.box((CX + ix * 1.7, -5.99, iz * 3.0), (0.9, 0.02, 1.3), win, "Win A")
        P.box((CX + ix * 1.7, 8.49, iz * 3.0), (0.9, 0.02, 1.3), win, "Win B")
P.box((CX, -5.98, 1.05), (1.0, 0.04, 2.1), P.wood("Entrance door", (0.45, 0.3, 0.18), planks=False), "Entrance")
for k in range(5):                                       # a few planters + a bench
    P.box((CX - 6 + k * 3.2, 7.6, 0.3), (1.2, 0.6, 0.6), P.mat(f"Planter{k}", (0.5, 0.5, 0.48), 0.8), "Planter")
    P.sphere((CX - 6 + k * 3.2, 7.6, 0.85), 0.45, P.mat(f"Bush{k}", (0.2, 0.45, 0.18), 0.8), "Bush")
P.box((CX - 3.2, -4.6, 0.25), (1.6, 0.45, 0.06), m_wood, "Bench")
# the dead street lamp (lights up when their fingertips touch)
POLE = Vector((CX + 0.35, -1.7, 0))
P.cyl(POLE, POLE + Vector((0, 0, 3.4)), 0.05, m_dark, "Lamp pole")
P.cyl(POLE + Vector((0, 0, 3.4)), POLE + Vector((0, 0.35, 3.45)), 0.03, m_dark, "Lamp arm")
LAMP_HEAD = POLE + Vector((0, 0.42, 3.32))
m_street = P.emit("Street lamp", (1.0, 0.9, 0.65), 0.0)
P.cyl(LAMP_HEAD, LAMP_HEAD + Vector((0, 0, 0.12)), 0.13, m_street, "Street lamp head")
L_street = lamp("Street light", LAMP_HEAD - Vector((0, 0, 0.1)), 0, (1.0, 0.85, 0.6), 0.2)
sun = bpy.data.lights.new("Sun", "SUN")
sun.energy, sun.color, sun.angle = 3.2, SUNNY, math.radians(2)
so = bpy.data.objects.new("Sun", sun)
sc.collection.objects.link(so)
so.rotation_euler = (math.radians(50), math.radians(10), math.radians(-35))
world = bpy.data.worlds.new("Day")
sc.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs[0].default_value = (0.45, 0.6, 0.9, 1)
world.node_tree.nodes["Background"].inputs[1].default_value = 1.0
# far sky backdrop behind building A's roofline so the object in the sky reads clearly
P.plane((CX, -40, 20), (120, 60), P.emit("Sky", (0.5, 0.65, 0.95), 1.0), (math.pi / 2, 0, 0), "Sky")

# ---------------- the thing in the sky: a streak like a meteor that slows down and stops (only a hint)
m_star = P.emit("Visitor", (0.75, 0.9, 1.0), 80.0)
star = P.sphere((0, 0, 0), 0.6, m_star, "Visitor")
m_trail = P.emit("Trail", (1.0, 0.85, 0.6), 25.0)
trail = P.cyl((0, 0, 0), (0, 0, 1), 0.25, m_trail, "Trail")
STAR_A, STAR_B = Vector((CX - 40, -36, 32)), Vector((CX + 3, -30, 17))
STAR_T0, STAR_T1 = 36.0, 40.0


def star_pos(t):
    u = smooth((t - STAR_T0) / (STAR_T1 - STAR_T0)) if t < STAR_T1 else 1.0
    u = 1 - (1 - u) ** 2
    hover = Vector((0, 0, 0.4 * math.sin((t - STAR_T1) * 2.0))) if t > STAR_T1 else Vector()
    return STAR_A.lerp(STAR_B, u) + hover


# ================================================================== lip sync from the real voices
LS = lipsync.Voices(fps=FPS)
for (a, b, who, _), name in zip(LINES, CLIPS):
    LS.add(who, os.path.join(HERE, "voices", "clips", name + ".wav"), a)


# ================================================================== motion (full rate, cross-faded clips)
def play(ch, clip, start, length, blend=0, **kw):
    old = MC.BUF.pop(ch.rig.name, {})
    MC.apply(ch, clip, start=start, length=length, step=1, **kw)
    new = MC.BUF[ch.rig.name]
    merged = {k: dict(v) for k, v in old.items()}
    quat = {}
    for (path, idx), pts in new.items():
        if path.endswith("rotation_quaternion"):
            quat.setdefault(path, {})[idx] = pts
            continue
        dst = merged.setdefault((path, idx), {})
        for f, v in pts.items():
            w = smooth((f - start) / blend) if blend and f in dst else 1.0
            dst[f] = dst.get(f, v) * (1 - w) + v * w
    for path, comps in quat.items():
        olds = [merged.setdefault((path, i), {}) for i in range(4)]
        for f in comps[0]:
            qn = [comps[i][f] for i in range(4)]
            if blend and f in olds[0] and f < start + blend:
                qo = [olds[i][f] for i in range(4)]
                if sum(a * b for a, b in zip(qo, qn)) < 0:
                    qn = [-v for v in qn]
                w = smooth((f - start) / blend)
                q = [a * (1 - w) + b * w for a, b in zip(qo, qn)]
                n = math.sqrt(sum(v * v for v in q)) or 1.0
                qn = [v / n for v in q]
            for i in range(4):
                olds[i][f] = qn[i]
    MC.BUF[ch.rig.name] = merged


def span(t0, t1):
    return T(t1) - T(t0) + 1


A_SIT = Vector((KX, -0.45, 0.2))               # Arian on his chair, facing the table (+Y)
M_SIT = Vector((KX, 0.85, 0.2))                # mom across, facing -Y
H_Y0, H_SPEED = 5.2, 1.15                      # hallway walk (towards -Y)
A_END = Vector((CX - 0.45, -0.3, 0))           # courtyard: Arian faces +X, Kian faces -X
K_POS = Vector((CX + 0.45, -0.3, 0))
A_START = Vector((CX - 0.45, -4.6, 0))
WALK_T0, WALK_T1 = 17.0, 20.6

# Arian: breakfast -> (cut) hallway walk -> courtyard walk-in -> talk -> fingertips -> looks up
play(ar, CL["sitting_idle"], 1, span(0, 10.0), offset=A_SIT, facing=0, in_place=True, loop=True)
play(ar, CL["walking_3"], T(10.0), span(10.0, 17.0), in_place=True, loop=True,
     place=lambda j: (Vector((HX, H_Y0 - H_SPEED * j / FPS, 0)), 180))
wl = (A_END - A_START).length / (WALK_T1 - WALK_T0)
play(ar, CL["walking_3"], T(WALK_T0), span(WALK_T0, WALK_T1), in_place=True, loop=True,
     place=lambda j: (A_START + (A_END - A_START).normalized() * min((A_END - A_START).length, wl * j / FPS), 0))
play(ar, CL["breathing_idle"], T(WALK_T1), span(WALK_T1, 30.5), blend=10, offset=A_END, facing=-90, in_place=True,
     loop=True)
play(ar, CL["hands_forward_gesture"], T(30.5), span(30.5, 34.5), blend=10, offset=A_END, facing=-90, in_place=True,
     speed=0.8)
play(ar, CL["breathing_idle"], T(34.3), span(34.3, END), blend=12, offset=A_END, facing=-90, in_place=True, loop=True)
MC.flush(ar)

# mom: sits and talks with her hands (legs crossed under the table)
play(mom, CL["sitting_talking"], 1, span(0, 10.0), offset=M_SIT, facing=180, in_place=True, src_from=4.0)
MC.flush(mom)

# Kian: waits, scans around, talks, points at the lamp, fingertips, then stares at the sky
play(kian, CL["looking_around"], T(17.0), span(17.0, 20.0), offset=K_POS, facing=90, in_place=True)
play(kian, CL["breathing_idle"], T(19.8), span(19.8, 27.0), blend=10, offset=K_POS, facing=90, in_place=True,
     loop=True)
play(kian, CL["pointing"], T(27.0), span(27.0, 30.0), blend=8, offset=K_POS, facing=90, in_place=True)
play(kian, CL["hands_forward_gesture"], T(30.5), span(30.5, 34.5), blend=10, offset=K_POS, facing=90,
     in_place=True, speed=0.8)
play(kian, CL["breathing_idle"], T(34.3), span(34.3, END), blend=12, offset=K_POS, facing=90, in_place=True,
     loop=True)
MC.flush(kian)

# who is in which set when
for f, v in ((1, False), (T(10.0), True)):
    mom.hide(f, v)
for f, v in ((1, True), (T(17.0), False)):
    kian.hide(f, v)
mom.flush()
kian.flush()


# Arian reaches for his glass (IK on top of the sitting clip)
REACH = P.empty("Reach glass")
REACH.location = GLASS + Vector((-0.06, -0.03, 0.08))
ik = ar.rig.pose.bones["hand_r"].constraints.new("IK")
ik.target, ik.chain_count, ik.use_tail = REACH, 3, True
for t_, v_ in ((0, 0), (6.2, 0), (6.9, 1), (7.7, 1), (8.4, 0)):
    ik.influence = v_
    ik.keyframe_insert("influence", frame=T(t_))


def bone(ch, name, f, tail=False):
    sc.frame_set(f)
    b = ch.rig.pose.bones[name]
    return ch.rig.matrix_world @ (b.tail if tail else b.head)


# ================================================================== heads look at things
def look_rig(ch, name):
    e = P.empty("Look " + name)
    for bn, inf in (("head", 0.65), ("neck_01", 0.3)):
        c = ch.rig.pose.bones[bn].constraints.new("DAMPED_TRACK")
        c.target, c.track_axis, c.influence = e, "TRACK_Z", inf
    return e


LA, LM, LK_ = look_rig(ar, "arian"), look_rig(mom, "mom"), look_rig(kian, "kian")
for f in range(1, N + 1, 2):
    t = (f - 1) / FPS
    mh = bone(mom, "head", f)
    ah = bone(ar, "head", f)
    kh = bone(kian, "head", f)
    sky = star_pos(max(t, STAR_T0))
    # Arian
    if t < 4.6:
        tgt = mh                                           # listening to mom
    elif t < 6.8:
        tgt = GLASS + Vector((0, 0.3, 0.1))                # avoids her eyes
    elif t < 7.6:
        tgt = GLASS
    elif t < 10.0:
        tgt = PEND                                         # the flicker
    elif t < 17.0:
        tgt = ah + Vector((0, -3.0, -0.3))                 # down the corridor
    elif t < WALK_T1:
        tgt = kh
    elif t < 30.5:
        tgt = kh if not (27.2 < t < 30.0) else LAMP_HEAD
    elif t < 32.6:
        tgt = (bone(ar, "hand_r", f) + bone(kian, "hand_r", f)) / 2
    elif t < 36.0:
        tgt = LAMP_HEAD
    else:
        tgt = sky
    LA.location = tgt
    LA.keyframe_insert("location", frame=f)
    # mom
    LM.location = PEND if 7.2 < t < 10.0 else ah
    LM.keyframe_insert("location", frame=f)
    # Kian
    if t < 20.0:
        tgt = ah if t > 18.6 else kh + Vector((-2, -3, -0.2))
    elif t < 27.0:
        tgt = ah
    elif t < 30.5:
        tgt = LAMP_HEAD if t < 29.0 else ah
    elif t < 32.6:
        tgt = (bone(ar, "hand_r", f) + bone(kian, "hand_r", f)) / 2
    elif t < 36.0:
        tgt = LAMP_HEAD
    else:
        tgt = sky
    LK_.location = tgt
    LK_.keyframe_insert("location", frame=f)

# ================================================================== faces: blinks, lips from the voices, feelings
for f in range(1, N + 1):
    t = (f - 1) / FPS
    for ch, who, st in (
            (ar, "arian", dict(worry=0.9 if t < 10 else (0.5 if t < 32 else (0.2 if t < 36 else 1.4)),
                               smile=0.6 * smooth((t - 32.4) / 0.5) * (1 - smooth((t - 36.5) / 0.8)),
                               scream=0.4 * smooth((t - 32.0) / 0.1) * (1 - smooth((t - 32.7) / 0.4)))),
            (mom, "mom", dict(worry=0.2 if t < 7.4 else 0.6, smile=0.3 if t < 4.5 else 0.0)),
            (kian, "kian", dict(worry=0.6 if t < 32 else (0.2 if t < 36 else 1.3),
                                smile=0.6 * smooth((t - 32.4) / 0.5) * (1 - smooth((t - 36.5) / 0.8))))):
        st.update(t=t, seed=ch.seed, talking=LS.level(who, t))
        for k, v in anim.face(st).items():
            if k in ch.keys:
                ch._put(ch.body.data.shape_keys, f'key_blocks["{k}"].value', 0, f, max(0.0, min(1.0, v)))
for ch in (ar, mom, kian):
    ch.flush()

# ================================================================== light + spark animation
SPARK_GLASS, SPARK_TOUCH, LAMP_ON = 7.0, 32.0, 32.25


def pend(t):
    """kitchen pendant: steady, stutters when Arian touches the glass"""
    if SPARK_GLASS <= t < SPARK_GLASS + 0.9:
        return 0.15 if int((t - SPARK_GLASS) * 14) % 2 else 1.8
    return 1.0


m_glow = P.emit("Fingertip glow", (0.35, 0.65, 1.0), 0.0)
glow_s = strength(m_glow)


def tip_glow(ch):
    out = []
    for fn in ("index_03_r", "middle_03_r", "thumb_03_r"):
        if fn in ch.rig.pose.bones:
            s = P.sphere(bone(ch, fn, 1, tail=True), 0.017, m_glow, "Tip glow")
            MT.attach(s, ch.rig, fn)
            out.append(s)
    l = bpy.data.lights.new("Hand light " + ch.rig.name, "POINT")
    l.color, l.shadow_soft_size = (0.35, 0.6, 1.0), 0.05
    o = bpy.data.objects.new(l.name, l)
    sc.collection.objects.link(o)
    o.location = bone(ch, "hand_r", 1, tail=True)
    MT.attach(o, ch.rig, "hand_r")
    return l


HL_A, HL_K = tip_glow(ar), tip_glow(kian)


def glow(t):
    g = math.exp(-((t - SPARK_GLASS) / 0.25) ** 2)                       # the glass
    g += smooth((t - 30.6) / 1.2) * (1 - smooth((t - 33.5) / 1.0)) * 0.8  # reaching for each other
    g += 1.6 * math.exp(-((t - SPARK_TOUCH) / 0.2) ** 2)                 # the touch
    return g


pend_s, street_s = strength(m_pend), strength(m_street)
for f in range(1, N + 1):
    t = (f - 1) / FPS
    p = pend(t)
    L_pend.energy = 70 * p
    L_pend.keyframe_insert("energy", frame=f)
    pend_s.default_value = 6.0 * p
    pend_s.keyframe_insert("default_value", frame=f)
    on = smooth((t - LAMP_ON) / 0.15)
    on *= 1.0 if t > LAMP_ON + 0.6 else (0.4 + 0.6 * (int(t * 17) % 2))
    L_street.energy = 220 * on
    L_street.keyframe_insert("energy", frame=f)
    street_s.default_value = 40 * on
    street_s.keyframe_insert("default_value", frame=f)
    g = glow(t)
    glow_s.default_value = 70 * g
    glow_s.keyframe_insert("default_value", frame=f)
    for l in (HL_A, HL_K):
        l.energy = 40 * g
        l.keyframe_insert("energy", frame=f)
    # hallway lamps flare as Arian walks past
    ay = H_Y0 - H_SPEED * max(0.0, t - 10.0)
    for y, l, me in HALL_LAMPS:
        k = 1.0 + (3.0 * math.exp(-((ay - y) / 0.5) ** 2) if 10.0 <= t < 17.0 else 0.0)
        l.energy = 25 * k
        l.keyframe_insert("energy", frame=f)
        s_ = strength(me)
        s_.default_value = 3.0 * k
        s_.keyframe_insert("default_value", frame=f)
    # the visitor in the sky
    vis = t >= STAR_T0
    pos = star_pos(t) if vis else Vector((0, 0, -50))
    star.location = pos
    star.keyframe_insert("location", frame=f)
    if vis:
        v = star_pos(t) - star_pos(t - 0.15)
        ln = v.length * 6
    else:
        v, ln = Vector((1, 0, 0)), 0.0
    trail.location = pos
    trail.rotation_euler = (-v).to_track_quat("Z", "Y").to_euler()
    trail.scale = (1, 1, max(0.001, ln))
    for path in ("location", "rotation_euler", "scale"):
        trail.keyframe_insert(path, frame=f)
    st_s = strength(m_star)
    st_s.default_value = 80 * (1 + 0.3 * math.sin(t * 9)) if vis else 0.0
    st_s.keyframe_insert("default_value", frame=f)

m_arc = P.emit("Arc", (0.6, 0.85, 1.0), 60.0)


def arc(name, a, b, t0, t1, n=14, jit=0.05):
    pts = [a.lerp(b, i / n) + Vector([random.uniform(-1, 1) for _ in range(3)]) * jit * math.sin(i / n * math.pi)
           for i in range(n + 1)]
    cu = bpy.data.curves.new(name, "CURVE")
    cu.dimensions, cu.bevel_depth = "3D", 0.004
    sp = cu.splines.new("POLY")
    sp.points.add(len(pts) - 1)
    for i, p in enumerate(pts):
        sp.points[i].co = (p.x, p.y, p.z, 1)
    o = bpy.data.objects.new(name, cu)
    sc.collection.objects.link(o)
    o.data.materials.append(m_arc)
    for f, v in ((1, 1), (T(t0), 0), (T(t1), 1)):
        o.hide_render = bool(v)
        o.keyframe_insert("hide_render", frame=f)


tip = bone(ar, "index_03_r", T(SPARK_GLASS), tail=True)
for k in range(2):
    arc(f"Glass spark{k}", tip, GLASS + Vector((0, 0, 0.1)), SPARK_GLASS + 0.08 * k, SPARK_GLASS + 0.12 + 0.08 * k,
        n=6, jit=0.02)
ta, tk = bone(ar, "index_03_r", T(SPARK_TOUCH), tail=True), bone(kian, "index_03_r", T(SPARK_TOUCH), tail=True)
mid = (ta + tk) / 2
for k in range(3):
    arc(f"Touch spark{k}", ta, tk, SPARK_TOUCH + 0.07 * k, SPARK_TOUCH + 0.15 + 0.07 * k, n=8, jit=0.03)
    arc(f"Lamp bolt{k}", mid, LAMP_HEAD, SPARK_TOUCH + 0.1 + 0.06 * k, SPARK_TOUCH + 0.25 + 0.06 * k, n=18,
        jit=0.25)

# ================================================================== camera (vertical 9:16) and cuts
cam_d = bpy.data.cameras.new("Cam")
cam = bpy.data.objects.new("Cam", cam_d)
sc.collection.objects.link(cam)
sc.camera = cam
aim = P.empty("Aim")
tc = cam.constraints.new("TRACK_TO")
tc.target, tc.track_axis, tc.up_axis = aim, "TRACK_NEGATIVE_Z", "UP_Y"
cam_d.dof.use_dof = True
cam_d.dof.focus_object = aim
cam_d.dof.aperture_fstop = 2.8
cam_d.clip_end = 300


def H(ch, f):
    return bone(ch, "head", f)


def hands(f):
    return (bone(ar, "hand_r", f) + bone(kian, "hand_r", f)) / 2


SHOTS = [
    (0.0, 4.4, 24, lambda f, u: Vector((KX + 1.7 - 0.2 * u, -1.5, 1.55)), lambda f, u: Vector((KX, 0.2, 0.95))),
    (4.4, 6.7, 45, lambda f, u: H(ar, f) + Vector((0.22, 0.8, 0.2)), lambda f, u: H(ar, f) + Vector((0, 0, 0.1))),
    (6.7, 8.1, 40, lambda f, u: GLASS + Vector((0.45, -0.45, 0.3)), lambda f, u: GLASS + Vector((-0.05, 0, 0.08))),
    (8.1, 10.0, 38, lambda f, u: H(mom, f) + Vector((0.3, -0.85, 0.12)), lambda f, u: H(mom, f) + Vector((0, 0, 0.1))),
    (10.0, 17.0, 30, lambda f, u: Vector((HX + 0.3, H_Y0 - H_SPEED * (10.0 + 7.0 * u - 10.0) - 2.6, 1.55)),
     lambda f, u: H(ar, f) - Vector((0, 0, 0.25))),
    (17.0, 20.8, 24, lambda f, u: Vector((CX + 2.4, -4.2, 1.6)), lambda f, u: (H(ar, f) + H(kian, f)) / 2 - Vector((0, 0, 0.3))),
    (20.8, 23.6, 35, lambda f, u: H(ar, f) + Vector((-0.65, -0.4, 0.08)), lambda f, u: H(kian, f)),
    (23.6, 26.6, 35, lambda f, u: H(kian, f) + Vector((0.65, 0.4, 0.08)), lambda f, u: H(ar, f)),
    (26.6, 30.4, 24, lambda f, u: Vector((CX + 0.1, 2.6, 1.5)), lambda f, u: Vector((CX + 0.2, -1.0, 1.8))),
    (30.4, 32.9, 38, lambda f, u: hands(f) + Vector((0.0, 1.0, 0.2)), lambda f, u: hands(f)),
    (32.9, 36.0, 26, lambda f, u: Vector((CX - 0.2, 1.6, 0.7)), lambda f, u: (LAMP_HEAD + H(ar, f)) / 2),
    (36.0, 40.5, 22, lambda f, u: Vector((CX + 0.1, 2.4, 1.3)), lambda f, u: star_pos(max((f - 1) / FPS, STAR_T0)) * 0.5 + Vector((CX, -1, 1.6)) * 0.5),
    (40.5, 43.2, 40, lambda f, u: H(kian, f) + Vector((-0.3, -0.75, -0.2)), lambda f, u: H(kian, f)),
    (43.2, END + 0.1, 38, lambda f, u: H(ar, f) + Vector((0.3, -0.8 - 0.2 * u, -0.22)), lambda f, u: H(ar, f) + Vector((0, 0, 0.04))),
]
for t0, t1, lens, cf, af in SHOTS:
    a, b = T(t0), min(N, T(t1) - 1)
    for f in list(range(a, b + 1, 2)) + [b]:
        u = (f - a) / max(1, b - a)
        cam.location, aim.location, cam_d.lens = cf(f, u), af(f, u), lens
        for o in (cam, aim):
            o.keyframe_insert("location", frame=f)
        cam_d.keyframe_insert("lens", frame=f)
for o in (cam, aim, cam_d):
    ad = o.animation_data
    act = ad.action if ad else None
    if act is None:
        continue
    try:
        fcs = act.fcurves
    except AttributeError:
        fcs = [fc for layer in act.layers for strip in layer.strips for bag in strip.channelbags for fc in bag.fcurves]
    for fc in fcs:
        for kp in fc.keyframe_points:
            kp.interpolation = "LINEAR"
    for t0, *_ in SHOTS[1:]:
        for fc in fcs:
            for kp in fc.keyframe_points:
                if abs(kp.co.x - (T(t0) - 1)) < 0.01 or abs(kp.co.x - (T(t0) - 2)) < 0.01:
                    kp.interpolation = "CONSTANT"

# ================================================================== render settings
sc.render.engine = "BLENDER_EEVEE"
ee = sc.eevee
ee.taa_render_samples = int(os.environ.get("SAMPLES", "24"))
for prop, v in (("use_raytracing", False), ("use_shadows", True), ("use_fast_gi", False)):
    if hasattr(ee, prop):
        setattr(ee, prop, v)
sc.view_settings.view_transform = "AgX"
sc.view_settings.exposure = 0.0
sc.render.resolution_x, sc.render.resolution_y = 540, 960
sc.render.resolution_percentage = 100
sc.render.image_settings.file_format = "PNG"
sc.frame_start, sc.frame_end = 1, N
sc.render.filepath = os.path.join(HERE, "frames", "f_")

if "--still" in argv:
    os.makedirs(os.path.join(HERE, "test"), exist_ok=True)
    for f in [int(v) for v in argv[argv.index("--still") + 1].split(",")]:
        sc.frame_set(f)
        sc.render.filepath = os.path.join(HERE, "test", f"still_{f:04d}.png")
        bpy.ops.render.render(write_still=True)
if "--save" in argv:
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(HERE, "spark2.blend"))
