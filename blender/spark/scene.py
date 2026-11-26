"""«جرقه» — vertical (9:16) short. Arian (new look: red hoodie, headphones) alone in his room on a stormy night;
the power goes, a spark from the desk lamp jumps into his hand, and electricity starts obeying him.

    ../cast/bpy.sh scene.py --save                 -> spark.blend
    ../cast/bpy.sh scene.py --still 60,250,500     -> test/still_XXXX.png
Render with chain.sh (render.py on spark.blend), then sound.py, post.py.
Full-rate motion (every frame), Mixamo clips cross-faded; lip sync on the lines in captions.py.
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
from captions import LINES, END, speaking  # noqa: E402

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
FPS = 24
N = int(END * FPS)
random.seed(7)

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.fps = FPS
CL = {k: MC.load(os.path.join(HERE, "..", "mocap", k + ".fbx")) for k in (
    "sitting_idle", "breathing_idle", "reloading", "terrified", "nervously_look_around", "hands_forward_gesture",
    "start_walking", "thinking", "head_nod_yes")}


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
# the other kid across the street: a dark silhouette in a window
cast.STYLE = None
other = cast.spawn("kian", quality="extra")

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
for o in other.objects:            # silhouette: everything flat near-black
    if o.type == "MESH":
        o.data.materials.clear()
        o.data.materials.append(P.mat("Silhouette", (0.006, 0.006, 0.01), 0.9))

# ------------------------------------------------------------------ the room (x -2.5..2.5, y -2.5..2.5, h 2.8)
m_wall = P.mat("Wall", (0.42, 0.42, 0.62), 0.85)
m_floor = P.wood("Floor", (0.55, 0.36, 0.22), planks=True)
m_wood = P.wood("Wood", (0.6, 0.4, 0.24), planks=False)
m_navy = P.mat("Blanket", (0.08, 0.12, 0.32), 0.95)
m_sheet = P.mat("Sheet", (0.85, 0.85, 0.9), 0.9)
m_curt = P.mat("Curtain", (0.12, 0.25, 0.5), 0.95)
m_dark = P.mat("Dark", (0.03, 0.03, 0.035), 0.3)
m_rug = P.mat("Rug", (0.75, 0.55, 0.3), 0.95)
m_plant = P.mat("Leaf", (0.15, 0.45, 0.15), 0.7)
m_pot = P.mat("Pot", (0.85, 0.85, 0.82), 0.5)
m_frame = P.mat("Frame", (0.9, 0.9, 0.88), 0.5)
P.box((0, 0, -0.05), (5, 5, 0.1), m_floor, "Floor")
# back wall with a real window hole (x 0.15..1.65, z 0.85..2.25) so the street is visible
P.box((-1.175, 2.5, 1.4), (2.65, 0.1, 2.8), m_wall, "Back L")
P.box((2.075, 2.5, 1.4), (0.85, 0.1, 2.8), m_wall, "Back R")
P.box((0.9, 2.5, 0.425), (1.5, 0.1, 0.85), m_wall, "Back sill")
P.box((0.9, 2.5, 2.525), (1.5, 0.1, 0.55), m_wall, "Back top")
for dx in (-0.75, 0.75):
    P.box((0.9 + dx, 2.47, 1.55), (0.06, 0.08, 1.4), m_frame, "Win frame")
for dz in (-0.7, 0.7):
    P.box((0.9, 2.47, 1.55 + dz), (1.5, 0.08, 0.06), m_frame, "Win frame")
P.box((0.9, 2.47, 1.55), (0.04, 0.06, 1.4), m_frame, "Win bar")
P.box((-2.5, 0, 1.4), (0.1, 5, 2.8), m_wall, "Left")
P.box((2.5, 0, 1.4), (0.1, 5, 2.8), m_wall, "Right")
P.box((-0.7, -2.5, 1.4), (3.6, 0.1, 2.8), m_wall, "Front L")
P.box((2.25, -2.5, 1.4), (0.5, 0.1, 2.8), m_wall, "Front R")
P.box((1.55, -2.5, 2.45), (0.9, 0.1, 0.7), m_wall, "Lintel")
P.box((1.55, -2.49, 1.05), (0.9, 0.06, 2.1), P.wood("Door", (0.75, 0.55, 0.35), planks=False), "Door")  # closed
P.box((0, 0, 2.85), (5, 5, 0.1), P.mat("Ceil", (0.85, 0.82, 0.8), 0.9), "Ceil")
for x in (-0.05, 1.85):
    P.box((x, 2.38, 1.4), (0.35, 0.08, 2.6), m_curt, "Curtain")
# bed (left), shelves, toys
P.box((-1.5, 1.0, 0.13), (1.6, 2.6, 0.26), m_wood, "Bed base", bevel=0.02)
P.box((-1.5, 1.0, 0.36), (1.5, 2.5, 0.2), m_sheet, "Mattress", bevel=0.05)
P.box((-1.5, 0.6, 0.47), (1.62, 1.7, 0.05), m_navy, "Blanket", bevel=0.02)
P.box((-1.5, 2.05, 0.54), (0.9, 0.35, 0.18), m_sheet, "Pillow", bevel=0.07)
P.box((-1.5, 2.4, 0.9), (1.6, 0.08, 1.0), m_wood, "Headboard")
cols = [(0.9, 0.5, 0.15), (0.2, 0.6, 0.8), (0.85, 0.25, 0.3), (0.95, 0.8, 0.2), (0.4, 0.7, 0.35), (0.6, 0.4, 0.8)]
for z in (1.6, 2.05):
    P.box((-1.5, 2.33, z), (1.6, 0.25, 0.04), m_wood, "Shelf")
for i in range(10):
    x = -2.2 + i * 0.15
    z = 1.62 if i < 6 else 2.07
    P.box((x if i < 6 else x - 0.7, 2.33, z + 0.12), (0.07, 0.18, 0.24), P.mat(f"Book{i}", cols[i % 6], 0.7), "Book")
for i, (x, c) in enumerate(((-1.95, (0.85, 0.6, 0.35)), (-1.75, (0.5, 0.75, 0.9)))):
    mt = P.mat(f"Plush{i}", c, 0.95)
    P.sphere((x, 1.95, 0.62), 0.11, mt, "Plush body")
    P.sphere((x, 1.95, 0.8), 0.085, mt, "Plush head")
    for ex in (-0.05, 0.05):
        P.sphere((x + ex, 1.95, 0.88), 0.03, mt, "Plush ear")
# desk against the right wall: Arian sits facing +X
DESK = Vector((2.05, 0.2, 0))
P.box((DESK.x, DESK.y, 0.74), (0.7, 1.4, 0.05), m_wood, "Desk")
for dy in (-0.65, 0.65):
    P.box((DESK.x, DESK.y + dy, 0.37), (0.6, 0.05, 0.74), m_wood, "Desk leg")
P.box((2.3, DESK.y + 0.1, 1.06), (0.04, 0.62, 0.38), m_dark, "Monitor")
m_screen = P.emit("Screen", (0.35, 0.55, 0.9), 1.5)
P.box((2.275, DESK.y + 0.1, 1.06), (0.01, 0.58, 0.34), m_screen, "Screen")
P.cyl((2.3, DESK.y + 0.1, 0.77), (2.3, DESK.y + 0.1, 0.88), 0.02, m_dark, "Monitor stand")
P.box((1.9, DESK.y - 0.15, 0.775), (0.3, 0.42, 0.02), P.mat("Notebook", (0.95, 0.95, 0.9), 0.8), "Notebook")
P.cyl((1.95, DESK.y - 0.32, 0.77), (1.95, DESK.y - 0.32, 0.86), 0.035, P.mat("Mug", (0.85, 0.3, 0.25), 0.4), "Mug")
# desk lamp (the one that sparks): base, arm, shade
LAMP = Vector((2.2, DESK.y - 0.5, 1.12))
P.cyl((2.2, LAMP.y, 0.77), (2.2, LAMP.y, 0.79), 0.07, m_dark, "Lamp base")
P.cyl((2.2, LAMP.y, 0.79), (2.2, LAMP.y, 1.1), 0.012, m_dark, "Lamp arm")
m_lampshade = P.emit("Lampshade", (1.0, 0.75, 0.45), 8.0)
P.cyl((2.2, LAMP.y, 1.08), (2.12, LAMP.y, 1.16), 0.07, m_lampshade, "Desk lamp")
# chair
CHAIR = Vector((1.45, DESK.y - 0.05, 0))
P.box((CHAIR.x, CHAIR.y, 0.45), (0.48, 0.48, 0.06), m_dark, "Chair seat", bevel=0.02)
P.box((CHAIR.x - 0.26, CHAIR.y, 0.78), (0.06, 0.48, 0.6), m_dark, "Chair back", bevel=0.02)
P.cyl((CHAIR.x, CHAIR.y, 0.05), (CHAIR.x, CHAIR.y, 0.42), 0.03, m_dark, "Chair post")
# bedside lamp, string lights, plant, rug, posters, backpack
P.box((-0.45, 2.15, 0.25), (0.45, 0.4, 0.5), m_wood, "Bedside", bevel=0.01)
P.cyl((-0.45, 2.15, 0.5), (-0.45, 2.15, 0.75), 0.03, m_dark, "Bed lamp foot")
m_bedlamp = P.emit("Bed lamp shade", (1.0, 0.75, 0.45), 6.0)
P.cyl((-0.45, 2.15, 0.72), (-0.45, 2.15, 0.9), 0.11, m_bedlamp, "Bed lamp")
m_bulb = P.emit("Bulb", (1.0, 0.8, 0.45), 15.0)
for i in range(16):
    x = -2.3 + i * 0.13
    P.sphere((x, 2.43, 2.45 - 0.12 * math.sin(i / 15 * math.pi)), 0.018, m_bulb, "Bulb")
P.cyl((-2.1, -2.1, 0), (-2.1, -2.1, 0.35), 0.16, m_pot, "Pot")
for i, (dx, dz, r) in enumerate(((0, 0.6, 0.3), (0.1, 0.9, 0.22), (-0.1, 1.05, 0.18))):
    P.sphere((-2.1 + dx, -2.1, dz), r, m_plant, f"Plant{i}")
P.box((0.3, 0.0, 0.008), (1.8, 1.4, 0.016), m_rug, "Rug")
for y, c in ((-0.6, (0.85, 0.45, 0.2)), (1.2, (0.3, 0.5, 0.75))):
    P.box((2.44, y, 1.85), (0.01, 0.45, 0.6), P.mat(f"Poster{y}", c, 0.7), "Poster")
P.box((-0.2, -2.25, 0.22), (0.35, 0.2, 0.44), P.mat("Backpack", (0.1, 0.1, 0.12), 0.8), "Backpack", bevel=0.05)

# ------------------------------------------------------------------ outside: rainy street + the building across
m_night = P.mat("Building", (0.1, 0.1, 0.13), 0.9)
P.box((0.9, 9.0, 4.0), (16, 1.0, 14), m_night, "Building across")
P.box((0.9, 5.5, -2.95), (16, 8, 0.1), P.mat("Street", (0.05, 0.05, 0.06), 0.25), "Street")
win_dark = P.mat("Dark window", (0.02, 0.025, 0.04), 0.1)
win_warm = P.emit("Warm window", (1.0, 0.7, 0.4), 1.2)
OTHER_WIN = Vector((1.6, 8.48, 1.3))
for ix in range(-4, 6):
    for iz in range(-1, 4):
        x, z = 0.9 + ix * 1.6, 1.3 + iz * 2.2
        if abs(x - OTHER_WIN.x) < 0.1 and abs(z - OTHER_WIN.z) < 0.1:
            continue
        P.box((x, 8.49, z), (0.9, 0.02, 1.2), win_warm if (ix * 7 + iz * 3) % 5 == 0 else win_dark, "Window across")
P.box((OTHER_WIN.x, 8.47, OTHER_WIN.z), (0.9, 0.02, 1.2), P.emit("Room across", (0.16, 0.2, 0.35), 1.0),
      "Room across")
for dx in (-0.47, 0.47):
    P.box((OTHER_WIN.x + dx, 8.3, OTHER_WIN.z), (0.05, 0.06, 1.25), P.mat("Frame across", (0.2, 0.2, 0.22), 0.6),
          "Frame across")
sky = P.emit("Night sky", (0.05, 0.07, 0.12), 1.0)
P.plane((0.9, 14, 6), (40, 30), sky, (math.pi / 2, 0, 0), "Sky")
# rain: thin streak planes falling (a few hundred, looping)
m_rain = P.emit("Rain", (0.6, 0.7, 0.9), 0.6)
rain = []
for i in range(220):
    x, y = random.uniform(-3, 5), random.uniform(3.0, 8.3)
    me = bpy.data.meshes.new("drop")
    me.from_pydata([(0, 0, 0), (0.004, 0, 0), (0.004, 0, 0.25), (0, 0, 0.25)], [], [(0, 1, 2, 3)])
    o = bpy.data.objects.new("Drop", me)
    sc.collection.objects.link(o)
    o.data.materials.append(m_rain)
    o.location = (x, y, 0)
    o["z0"], o["v"] = random.uniform(-3, 7), random.uniform(7, 9)
    rain.append(o)
for o in rain:
    act = bpy.data.actions.new("rain")
    o.animation_data_create().action = act
    pts = []
    f = 1
    z = o["z0"]
    while f <= N:
        pts.append((f, z))
        z -= o["v"] / FPS * 6
        f += 6
        if z < -3:
            pts.append((f - 0.01, -3.2))
            z += 10
    cast.write_fcurve(o, "location", 2, pts)

# ------------------------------------------------------------------ lights + the power cut
BLACKOUT, POWER_BACK = 10.4, 38.4
FLASH = [(8.6, 1.0), (8.85, 0.6), (9.6, 1.0), (24.0, 0.5), (45.5, 0.8), (46.0, 0.5)]


def power(t):
    """1 = lamps on. flicker before the cut, flicker back on when Arian raises his hand."""
    if t < BLACKOUT - 1.0:
        return 1.0
    if t < BLACKOUT:
        return 1.0 if int(t * 13) % 3 else 0.15
    if t < POWER_BACK:
        return 0.0
    if t < POWER_BACK + 0.8:
        return 1.0 if int(t * 11) % 2 else 0.3
    return 1.0


def flash(t):
    return max([0.0] + [k * math.exp(-((t - a) / 0.07) ** 2) for a, k in FLASH])


def lamp(name, loc, energy, col, radius=0.15):
    l = bpy.data.lights.new(name, "POINT")
    l.energy, l.color, l.shadow_soft_size = energy, col, radius
    o = bpy.data.objects.new(name, l)
    sc.collection.objects.link(o)
    o.location = loc
    return l


L_desk = lamp("Desk lamp", LAMP + Vector((-0.08, 0, -0.05)), 45, (1.0, 0.72, 0.45))
L_bed = lamp("Bed lamp", (-0.45, 2.15, 0.95), 30, (1.0, 0.7, 0.42))
L_ceiling = P.area_light((0.3, 0.3, 2.7), (0.3, 0.3, 0), 140, 1.2, (1.0, 0.85, 0.7), name="Ceiling")
L_moon = P.area_light((0.9, 3.2, 2.0), (0.6, 0.0, 0.6), 420, 1.6, (0.55, 0.65, 1.0), name="Moon")
L_flash = P.area_light((0.9, 3.6, 2.6), (0.5, 0.0, 0.5), 0, 2.5, (0.8, 0.85, 1.0), name="Lightning")
L_screen = lamp("Screen glow", (2.15, DESK.y + 0.1, 1.06), 8, (0.4, 0.6, 1.0), 0.3)
emit_nodes = []
for m, k in ((m_lampshade, 8.0), (m_bedlamp, 6.0), (m_bulb, 15.0), (m_screen, 1.5)):
    n = next(n for n in m.node_tree.nodes if n.type in ("EMISSION", "BSDF_PRINCIPLED"))
    emit_nodes.append((n, k))
sky_em = next(n for n in sky.node_tree.nodes if n.type in ("EMISSION", "BSDF_PRINCIPLED"))
for f in range(1, N + 1):
    t = (f - 1) / FPS
    p = power(t)
    fl = flash(t)
    for l, e in ((L_desk, 45), (L_bed, 30), (L_screen, 8)):
        l.energy = e * p
        l.keyframe_insert("energy", frame=f)
    L_ceiling.data.energy = 140 * p
    L_ceiling.data.keyframe_insert("energy", frame=f)
    L_flash.data.energy = 3000 * fl
    L_flash.data.keyframe_insert("energy", frame=f)
    for n, k in emit_nodes:
        s = n.inputs["Strength"] if "Strength" in n.inputs else n.inputs["Emission Strength"]
        s.default_value = k * p
        s.keyframe_insert("default_value", frame=f)
    s = sky_em.inputs["Strength"] if "Strength" in sky_em.inputs else sky_em.inputs["Emission Strength"]
    s.default_value = 1.0 + 25 * fl
    s.keyframe_insert("default_value", frame=f)
world = bpy.data.worlds.new("Night")
sc.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs[0].default_value = (0.02, 0.025, 0.05, 1)
world.node_tree.nodes["Background"].inputs[1].default_value = 1.2

# ------------------------------------------------------------------ motion (full rate, cross-faded clips)
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


def pelvis_xy(ch, f):
    MC.flush(ch)
    sc.frame_set(f)
    p = ch.rig.matrix_world @ ch.rig.pose.bones["pelvis"].head
    return Vector((p.x, p.y, 0))


SIT = Vector((CHAIR.x + 0.02, CHAIR.y, 0.2))   # on the chair, facing the desk (+X)
STAND = Vector((1.2, DESK.y - 0.45, 0))       # standing beside the desk, by the lamp
# 0-15 s: sitting at the desk (studying, then the blackout)
play(ar, CL["sitting_idle"], 1, T(15.0), offset=SIT, facing=-90, in_place=True, loop=True)
# 15 s: (cut) standing by the desk, fiddling with the lamp switch
play(ar, CL["reloading"], T(15.0), T(19.1) - T(15.0) + 1, offset=STAND, facing=-80, in_place=True)
# 19.1 s: the spark: flinch, cower, look around
play(ar, CL["terrified"], T(19.1), T(26.5) - T(19.1) + 1, blend=5, offset=STAND, facing=-80, in_place=True,
     src_from=2.5)
# 26.5 s: mom at the door -> turns to the door, nervous
play(ar, CL["nervously_look_around"], T(26.5), T(35.0) - T(26.5) + 1, blend=12, offset=STAND, facing=180,
     in_place=True, loop=True)
# 35 s: raises his hand towards the lamp -> power comes back at 38.4
play(ar, CL["hands_forward_gesture"], T(35.0), T(39.0) - T(35.0) + 1, blend=12, offset=STAND, facing=-75,
     in_place=True, speed=0.8)
play(ar, CL["breathing_idle"], T(38.6), T(43.0) - T(38.6) + 1, blend=12, offset=STAND, facing=-75, in_place=True,
     loop=True)
# 43 s: walks to the window
play(ar, CL["start_walking"], T(43.0), T(46.0) - T(43.0) + 1, blend=10, offset=STAND, facing=20, in_place=False)
at_win = pelvis_xy(ar, T(46.0))
play(ar, CL["breathing_idle"], T(45.6), N - T(45.6) + 1, blend=12, offset=at_win, facing=5, in_place=True,
     loop=True)
MC.flush(ar)
# the kid across the street: still at the window, then raises a hand
OTH = Vector((OTHER_WIN.x, 8.38, OTHER_WIN.z - 1.3 + 0.0))
play(other, CL["breathing_idle"], 1, T(49.0), offset=OTH, facing=180, in_place=True, loop=True)
play(other, CL["hands_forward_gesture"], T(49.0), N - T(49.0) + 1, blend=12, offset=OTH, facing=180,
     in_place=True, speed=0.7)
MC.flush(other)

# visibility: Arian on the chair until 15 s (the chair cut), the other kid only appears at 48 s
other_vis = lambda t: t >= 48.0  # noqa: E731
for f in (1, T(48.0)):
    other.hide(f, not other_vis((f - 1) / FPS))
other.flush()

# heads: look at the notebook while studying, at the lamp/hand, the door, the window across
LOOK = P.empty("Look arian")
for bn, inf in (("head", 0.65), ("neck_01", 0.3)):
    c = ar.rig.pose.bones[bn].constraints.new("DAMPED_TRACK")
    c.target, c.track_axis, c.influence = LOOK, "TRACK_Z", inf
DOOR = Vector((1.55, -2.5, 1.5))
for f in range(1, N + 1, 2):
    t = (f - 1) / FPS
    sc.frame_set(f)
    hand = ar.rig.matrix_world @ ar.rig.pose.bones["hand_r"].head
    if t < 9.0:
        tgt = Vector((1.9, DESK.y - 0.15, 0.78))                    # notebook
    elif t < 10.4:
        tgt = Vector((1.0, 2.5, 1.6))                               # the window (lightning)
    elif t < 15.0:
        tgt = Vector((2.4, 0.9, 2.3))                               # up at the dead lights
    elif t < 19.0:
        tgt = LAMP
    elif t < 26.5:
        tgt = hand + Vector((0, 0, 0.05))                           # his own hand
    elif t < 34.0:
        tgt = DOOR
    elif t < 43.0:
        tgt = LAMP
    else:
        tgt = Vector((OTHER_WIN.x, 8.5, OTHER_WIN.z + 0.2))          # the window across
    LOOK.location = tgt
    LOOK.keyframe_insert("location", frame=f)

# faces: blinks, lip sync on his lines, fear after the spark, a small smile when the lamp obeys
for f in range(1, N + 1):
    t = (f - 1) / FPS
    worry = 0.3 if t < 19 else (1.6 if t < 34 else (0.6 if t < 47 else 1.0))
    st = dict(t=t, seed=ar.seed, talking=speaking("arian", t), worry=worry,
              smile=0.5 * smooth((t - 39.0) / 0.8) * (1 - smooth((t - 43) / 1.0)),
              scream=0.5 * smooth((t - 19.1) / 0.15) * (1 - smooth((t - 20.0) / 0.6)))
    for k, v in anim.face(st).items():
        if k in ar.keys:
            ar._put(ar.body.data.shape_keys, f'key_blocks["{k}"].value', 0, f, max(0.0, min(1.0, v)))
ar.flush()

# ------------------------------------------------------------------ the glow in his fingers + the spark
m_glow = P.emit("Hand glow", (0.35, 0.65, 1.0), 0.0)
glow_em = next(n for n in m_glow.node_tree.nodes if n.type in ("EMISSION", "BSDF_PRINCIPLED"))
tips = []
for fn in ("thumb_03_r", "index_03_r", "middle_03_r", "ring_03_r", "pinky_03_r"):
    if fn not in ar.rig.pose.bones:
        continue
    sc.frame_set(1)
    tip = ar.rig.matrix_world @ ar.rig.pose.bones[fn].tail
    s = P.sphere(tip, 0.02, m_glow, "Tip glow")
    MT.attach(s, ar.rig, fn)
    tips.append(s)
gl = bpy.data.lights.new("Hand light", "POINT")
gl.color, gl.shadow_soft_size = (0.35, 0.6, 1.0), 0.05
glo = bpy.data.objects.new("Hand light", gl)
sc.collection.objects.link(glo)
sc.frame_set(1)
glo.location = ar.rig.matrix_world @ ar.rig.pose.bones["hand_r"].tail
MT.attach(glo, ar.rig, "hand_r")


def glow(t):
    if t < 19.1:
        return 0.0
    g = smooth((t - 19.3) / 1.5)
    g *= 1 - 0.85 * smooth((t - 28.0) / 0.6) * (1 - smooth((t - 33.0) / 1.0))   # hides it while mom is there
    g *= 1 + 0.9 * math.exp(-((t - 38.4) / 0.3) ** 2)                          # surge when the lamp obeys
    return g * (0.85 + 0.15 * math.sin(t * 23) * math.sin(t * 7.1))


for f in range(1, N + 1):
    t = (f - 1) / FPS
    g = glow(t)
    s = glow_em.inputs["Strength"] if "Strength" in glow_em.inputs else glow_em.inputs["Emission Strength"]
    s.default_value = 90 * g
    s.keyframe_insert("default_value", frame=f)
    gl.energy = 90 * g
    gl.keyframe_insert("energy", frame=f)
# the spark arc from the lamp to his hand (19.1-19.5 s) and the surge back to the lamp (38.2-38.6 s)
m_arc = P.emit("Arc", (0.6, 0.85, 1.0), 60.0)


def arc(name, a, b, t0, t1, n=14):
    pts = []
    for i in range(n + 1):
        u = i / n
        p = a.lerp(b, u) + Vector((random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1, 1))) * \
            0.05 * math.sin(u * math.pi)
        pts.append(p)
    cu = bpy.data.curves.new(name, "CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth = 0.004
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
    return o


sc.frame_set(T(19.2))
hand_at_spark = ar.rig.matrix_world @ ar.rig.pose.bones["index_03_r"].tail
for k in range(3):
    arc(f"Spark{k}", LAMP + Vector((-0.06, 0, -0.03)), hand_at_spark, 19.05 + 0.1 * k, 19.2 + 0.1 * k)
sc.frame_set(T(38.4))
hand_at_surge = ar.rig.matrix_world @ ar.rig.pose.bones["index_03_r"].tail
for k in range(3):
    arc(f"Surge{k}", hand_at_surge, LAMP + Vector((-0.06, 0, -0.03)), 38.2 + 0.1 * k, 38.35 + 0.1 * k)
# the other kid's hand glows too
og = bpy.data.lights.new("Other glow", "POINT")
og.color, og.shadow_soft_size = (0.35, 0.6, 1.0), 0.05
ogo = bpy.data.objects.new("Other glow", og)
sc.collection.objects.link(ogo)
sc.frame_set(1)
ogo.location = other.rig.matrix_world @ other.rig.pose.bones["hand_r"].tail
MT.attach(ogo, other.rig, "hand_r")
osph = P.sphere(ogo.location, 0.05, m_glow, "Other glow ball")
MT.attach(osph, other.rig, "hand_r")
for f in range(1, N + 1):
    t = (f - 1) / FPS
    og.energy = 30 * smooth((t - 50.5) / 1.2) * (0.85 + 0.15 * math.sin(t * 19))
    og.keyframe_insert("energy", frame=f)
for f, v in ((1, 1), (T(50.5), 0)):
    osph.hide_render = bool(v)
    osph.keyframe_insert("hide_render", frame=f)

# ------------------------------------------------------------------ camera (vertical 9:16), cuts
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


def head(f):
    sc.frame_set(f)
    return ar.rig.matrix_world @ ar.rig.pose.bones["head"].head


def hand(f):
    sc.frame_set(f)
    return ar.rig.matrix_world @ ar.rig.pose.bones["hand_r"].head


# (t0, t1, lens, cam(t)->loc, aim(t)->loc)
SHOTS = [
    (0.0, 8.0, 24, lambda f, u: Vector((-0.2 + 0.35 * u, -1.6 + 0.3 * u, 1.75)), lambda f, u: head(f) - Vector((0, 0, 0.35))),
    (8.0, 10.4, 28, lambda f, u: Vector((1.0, 1.6, 1.45)), lambda f, u: Vector((0.9, 2.6, 1.5)) + (head(f) - Vector((0.9, 2.6, 1.5))) * 0.0),
    (10.4, 15.0, 45, lambda f, u: head(f) + Vector((0.7, 0.35, -0.05)), lambda f, u: head(f) + Vector((0, 0, 0.03))),
    (15.0, 19.0, 35, lambda f, u: Vector((0.6, -0.9, 1.4)), lambda f, u: (head(f) + LAMP) / 2),
    (19.0, 23.0, 28, lambda f, u: Vector((2.2, -1.7 + 0.1 * u, 1.55)), lambda f, u: head(f) - Vector((0.1, 0, 0.35))),
    (23.0, 27.0, 40, lambda f, u: hand(f) + Vector((0.05, -0.7, 0.25)), lambda f, u: (hand(f) * 2 + head(f)) / 3),
    (27.0, 34.0, 28, lambda f, u: Vector((0.3, 1.9, 1.5)), lambda f, u: head(f) + Vector((0, -0.4, -0.15))),
    (34.0, 40.0, 26, lambda f, u: Vector((0.2, -1.3 + 0.2 * u, 1.45)), lambda f, u: (head(f) + LAMP) / 2),
    (40.0, 43.0, 50, lambda f, u: head(f) + Vector((0.65, 0.3, 0.0)), lambda f, u: head(f) + Vector((0, 0, 0.03))),
    (43.0, 49.5, 26, lambda f, u: Vector((1.8, -1.6, 1.55)), lambda f, u: head(f) - Vector((0, 0, 0.2))),
    (49.5, 52.0, 60, lambda f, u: head(f) + Vector((-0.25, -0.45, 0.1)), lambda f, u: Vector((OTHER_WIN.x, 8.6, OTHER_WIN.z))),
    (52.0, 54.6, 45, lambda f, u: head(f) + Vector((0.35, 0.75, 0.0)), lambda f, u: head(f)),
    (54.6, END + 0.1, 30, lambda f, u: head(f) + Vector((0.15 - 0.3 * u, -1.1 - 0.4 * u, 0.25)), lambda f, u: Vector((OTHER_WIN.x, 8.0, OTHER_WIN.z - 0.2))),
]
for t0, t1, lens, cf, af in SHOTS:
    a, b = T(t0), min(N, T(t1) - 1)
    for f in list(range(a, b + 1, 2)) + [b]:
        u = (f - a) / max(1, b - a)
        loc, at = cf(f, u), af(f, u)
        cam.location, aim.location, cam_d.lens = loc, at, lens
        for o, path in ((cam, "location"), (aim, "location")):
            o.keyframe_insert(path, frame=f)
        cam_d.keyframe_insert("lens", frame=f)
# cuts must not interpolate between shots
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
    for t0, t1, *_ in SHOTS[1:]:
        for fc in fcs:
            for kp in fc.keyframe_points:
                if abs(kp.co.x - (T(t0) - 1)) < 0.01 or abs(kp.co.x - (T(t0) - 2)) < 0.01:
                    kp.interpolation = "CONSTANT"

# ------------------------------------------------------------------ render settings
sc.render.engine = "BLENDER_EEVEE"
ee = sc.eevee
ee.taa_render_samples = int(os.environ.get("SAMPLES", "24"))
for prop, v in (("use_raytracing", False), ("use_shadows", True), ("use_fast_gi", False)):
    if hasattr(ee, prop):
        setattr(ee, prop, v)
sc.view_settings.view_transform = "AgX"
sc.view_settings.exposure = 0.2
for f in range(1, N + 1, 6):        # brighter exposure in the dark part so faces still read
    t = (f - 1) / FPS
    sc.view_settings.exposure = 0.2 + 1.3 * (smooth((t - 10.4) / 0.6) - smooth((t - 38.4) / 0.6))
    sc.view_settings.keyframe_insert("exposure", frame=f)
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
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(HERE, "spark.blend"))
