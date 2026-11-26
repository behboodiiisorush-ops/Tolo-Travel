"""Test board for the "stylized realistic" look the user sent (Arian: red hoodie, headphones round the neck,
dark messy hair, big expressive eyes; a cosy teenager's bedroom). No logos anywhere.

    ../cast/bpy.sh arian_board.py --part char     -> out/board_turn_*.png, out/board_face_*.png
    ../cast/bpy.sh arian_board.py --part room     -> out/board_room.png
"""
import bpy, sys, os, math
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "cast"))
sys.path.append(os.path.join(HERE, "..", "shelter3"))
sys.path.append(os.path.join(HERE, "..", "studio"))
import cast  # noqa: E402
import mocap2 as MC  # noqa: E402
import props as P  # noqa: E402
import mpfb_tools as MT  # noqa: E402
import look as LK  # noqa: E402

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
PART = argv[argv.index("--part") + 1] if "--part" in argv else "char"
OUT = os.path.join(HERE, "out")
os.makedirs(OUT, exist_ok=True)

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
idle = MC.load(os.path.join(HERE, "..", "mocap", "breathing_idle.fbx"))
sit = MC.load(os.path.join(HERE, "..", "mocap", "sitting_idle.fbx")) if PART == "room" else None
CL = {k: MC.load(os.path.join(HERE, "..", "mocap", k + ".fbx"))
      for k in ("start_walking", "hands_forward_gesture", "nervously_look_around")} if PART == "anim" else {}

# ------------------------------------------------------------------ the new Arian
STYLE = dict(LK.STYLE)
for k_ in list(STYLE):
    if "eye-height" in k_:
        STYLE.pop(k_)          # lids not pulled wide open: less "staring"
STYLE.update({"l-eye-scale-incr": 1.0, "r-eye-scale-incr": 1.0, "head-scale-vert-incr": 0.2,
              "nose-scale-horiz-decr": 0.7, "mouth-scale-horiz-decr": 0.2})
cast.STYLE = STYLE
cast.CAST["arian"] = dict(cast.CAST["arian"], age=0.42, height=0.55, weight=0.4,
                          skin_tint=(0.86, 0.6, 0.46), hair="culturalibre_hair_14", hair_col=(0.035, 0.025, 0.02), brow="eyebrow002",
                          clothes={"elvs_hooded_sweat_jacket1": (0.55, 0.06, 0.07),
                                   "cortu_cargo_pants": (0.07, 0.07, 0.08),
                                   "culturalibre_sneakers": (0.92, 0.9, 0.88)})
ar = cast.spawn("arian")
cast.cartoon_face(ar)

# headphones round the neck: a band behind the neck, two cups on the collarbones
m_hp = P.mat("Headphones", (0.04, 0.04, 0.045), 0.35)
m_cush = P.mat("Cushion", (0.12, 0.12, 0.13), 0.8)
sc.frame_set(1)
bpy.context.view_layer.update()
neck = ar.rig.matrix_world @ ar.rig.pose.bones["neck_01"].head
parts = []
bpy.ops.mesh.primitive_torus_add(major_radius=0.1, minor_radius=0.014, location=neck + Vector((0, 0.01, -0.035)),
                                  major_segments=40)
band = bpy.context.object
band.scale = (1.05, 0.95, 1.0)
band.rotation_euler.x = math.radians(-18)       # dips towards the chest at the front, sits high on the nape
import bmesh
bm = bmesh.new()
bm.from_mesh(band.data)
bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.y < -0.035], context="VERTS")   # open at the front
bm.to_mesh(band.data)
bm.free()
band.data.materials.append(m_hp)
parts.append(band)
for sx in (-1, 1):   # cups hang at the front of the neck, facing forward/out
    a = neck + Vector((sx * 0.085, -0.075, -0.085))
    d = Vector((sx * 0.35, -1.0, 0.25)).normalized()
    parts.append(P.cyl(a - d * 0.02, a + d * 0.02, 0.05, m_hp, "Cup", 28))
    parts.append(P.cyl(a - d * 0.035, a - d * 0.02, 0.043, m_cush, "Cushion", 28))
for o in parts:
    bpy.ops.object.shade_smooth() if False else None
    MT.attach(o, ar.rig, "neck_01")

# ------------------------------------------------------------------ materials: warm, saturated, soft skin
for m in bpy.data.materials:
    b = next((n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None) if m.use_nodes else None
    if not b or "eye" in m.name.lower():
        continue
    s = b.inputs["Base Color"]
    if s.is_linked:
        h = m.node_tree.nodes.new("ShaderNodeHueSaturation")
        h.inputs["Saturation"].default_value = 1.2
        m.node_tree.links.new(s.links[0].from_socket, h.inputs["Color"])
        m.node_tree.links.new(h.outputs[0], s)

for o in ar.parts.get("Eyes", []):
    for slot in o.material_slots:
        b = next((n for n in slot.material.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None)
        if b:
            b.inputs["Roughness"].default_value = 0.04
            b.inputs["Coat Weight"].default_value = 1.0
            b.inputs["Coat Roughness"].default_value = 0.02
for kb in ar.keys.values():
    kb.slider_max = 2.0


def big_iris(m, k=1.45):
    """Scale the eye texture around each iris centre (the texture holds two eyes) so the iris looks bigger."""
    nt = m.node_tree
    tex = next((n for n in nt.nodes if n.type == "TEX_IMAGE"), None)
    if not tex or m.get("big_iris"):
        return
    m["big_iris"] = 1
    uv = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(uv.outputs["UV"], sep.inputs[0])
    gt = nt.nodes.new("ShaderNodeMath")
    gt.operation = "GREATER_THAN"
    gt.inputs[1].default_value = 0.5
    nt.links.new(sep.outputs[0], gt.inputs[0])
    mixc = nt.nodes.new("ShaderNodeMix")
    mixc.data_type = "VECTOR"
    mixc.inputs["A"].default_value = (0.293, 0.297, 0)
    mixc.inputs["B"].default_value = (0.703, 0.715, 0)
    nt.links.new(gt.outputs[0], mixc.inputs["Factor"])
    sub = nt.nodes.new("ShaderNodeVectorMath")
    sub.operation = "SUBTRACT"
    nt.links.new(uv.outputs["UV"], sub.inputs[0])
    nt.links.new(mixc.outputs["Result"], sub.inputs[1])
    sc_ = nt.nodes.new("ShaderNodeVectorMath")
    sc_.operation = "SCALE"
    sc_.inputs["Scale"].default_value = 1.0 / k
    nt.links.new(sub.outputs[0], sc_.inputs[0])
    add = nt.nodes.new("ShaderNodeVectorMath")
    add.operation = "ADD"
    nt.links.new(sc_.outputs[0], add.inputs[0])
    nt.links.new(mixc.outputs["Result"], add.inputs[1])
    nt.links.new(add.outputs[0], tex.inputs["Vector"])


# warmer, slightly darker skin (the MakeHuman skin sits inside a node group and reads pale under soft lights)
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
# bold, opaque brows
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

# ------------------------------------------------------------------ render setup
sc.render.engine = "BLENDER_EEVEE"
sc.eevee.taa_render_samples = 48
for prop, v in (("use_raytracing", True), ("use_shadows", True), ("use_fast_gi", True)):
    if hasattr(sc.eevee, prop):
        setattr(sc.eevee, prop, v)
sc.view_settings.view_transform = "AgX"
sc.view_settings.exposure = 0.1
sc.render.image_settings.file_format = "PNG"
world = bpy.data.worlds.new("W")
sc.world = world
world.use_nodes = True
cam_d = bpy.data.cameras.new("Cam")
cam = bpy.data.objects.new("Cam", cam_d)
sc.collection.objects.link(cam)
sc.camera = cam
aim = P.empty("Aim")
tc = cam.constraints.new("TRACK_TO")
tc.target, tc.track_axis, tc.up_axis = aim, "TRACK_NEGATIVE_Z", "UP_Y"


def shot(path, loc, at, lens, w, h):
    cam.location, aim.location, cam_d.lens = loc, at, lens
    sc.render.resolution_x, sc.render.resolution_y = w, h
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)


def keys(**v):
    for k, kb in ar.keys.items():
        kb.value = 0.0
    for k, val in v.items():
        k = k.replace("_", "-")
        for side in ("left", "right"):
            kk = k.replace("SIDE", side)
            if kk in ar.keys:
                ar.keys[kk].value = val


if PART == "char":
    MC.apply(ar, idle, start=1, length=40, offset=(0, 0, 0), facing=180, in_place=True, step=1)
    MC.flush(ar)
    sc.frame_set(20)
    world.node_tree.nodes["Background"].inputs[0].default_value = (0.09, 0.08, 0.11, 1)
    P.box((0, 0, -0.05), (20, 20, 0.1), P.mat("Floor", (0.16, 0.15, 0.18), 0.9), "Floor")
    P.area_light((-1.8, -2.2, 2.6), (0, 0, 1.0), 450, 1.6, (1.0, 0.9, 0.8), name="Key")
    P.area_light((2.4, -1.6, 1.6), (0, 0, 1.0), 160, 2.5, (0.8, 0.85, 1.0), name="Fill")
    P.area_light((0.5, 2.5, 2.4), (0, 0, 1.4), 420, 1.0, (1.0, 0.75, 0.5), name="Rim")
    head = ar.rig.matrix_world @ ar.rig.pose.bones["head"].head
    hz = head.z
    cam_d.dof.use_dof = False
    # turnaround: the character turns, the camera stays
    for i, ang in enumerate(() if "--faces" in argv else (0, 35, 90, 180)):
        ar.rig.rotation_euler.z = math.radians(ang)
        ar.rig.keyframe_insert("rotation_euler", index=2, frame=20)
        sc.frame_set(20)
        shot(os.path.join(OUT, f"board_turn_{i}.png"), (0, -3.6, hz * 0.6), (0, 0, hz * 0.52), 50, 540, 960)
    ar.rig.rotation_euler.z = math.radians(12)
    ar.rig.keyframe_insert("rotation_euler", index=2, frame=20)
    sc.frame_set(20)
    head = ar.rig.matrix_world @ ar.rig.pose.bones["head"].head + Vector((0, 0, 0.07))
    cam_d.dof.use_dof = False
    faces = {
        "happy": dict(mouth_corner_puller=1.6, mouth_elevation=0.4, mouth_open=0.25, eye_SIDE_slit=0.5,
                      eyebrows_SIDE_extern_up=0.6),
        "surprised": dict(mouth_open=1.3, eye_SIDE_opened_up=1.6, eyebrows_SIDE_up=1.8, eyebrows_SIDE_inner_up=0.6),
        "sad": dict(eyebrows_SIDE_inner_up=1.8, mouth_depression=1.5, eye_SIDE_slit=0.45, mouth_compression=0.4),
        "angry": dict(eyebrows_SIDE_down=1.9, mouth_compression=1.0, mouth_retraction=0.6, nose_SIDE_elevation=0.9,
                      eye_SIDE_slit=0.5),
        "scared": dict(eyebrows_SIDE_inner_up=1.8, eyebrows_SIDE_up=1.0, eye_SIDE_opened_up=1.6, mouth_open=0.7,
                       mouth_retraction=1.0),
    }
    for name, v in faces.items():
        keys(**v)
        shot(os.path.join(OUT, f"board_face_{name}.png"), head + Vector((0.1, -0.62, 0.0)), head + Vector((0, 0, -0.01)),
             85, 640, 640)

if PART in ("room", "anim"):
    # cosy bedroom: lilac-blue walls, wooden shelves with toys, desk with a monitor, bed with a navy blanket,
    # big window with blue curtains, warm lamps; Arian sits on the bed
    world.node_tree.nodes["Background"].inputs[0].default_value = (0.5, 0.6, 0.8, 1)
    m_wall = P.mat("Wall", (0.42, 0.42, 0.62), 0.85)
    m_floor = P.wood("Floor", (0.55, 0.36, 0.22), planks=True)
    m_wood = P.wood("Wood", (0.6, 0.4, 0.24), planks=False)
    m_navy = P.mat("Blanket", (0.08, 0.12, 0.32), 0.95)
    m_sheet = P.mat("Sheet", (0.85, 0.85, 0.9), 0.9)
    m_curt = P.mat("Curtain", (0.12, 0.25, 0.5), 0.95)
    m_sky = P.emit("Sky", (1.0, 0.62, 0.35), 4.0)
    m_dark = P.mat("Dark", (0.03, 0.03, 0.035), 0.3)
    m_screen = P.emit("Screen", (0.35, 0.55, 0.9), 1.5)
    m_rug = P.mat("Rug", (0.75, 0.55, 0.3), 0.95)
    m_plant = P.mat("Leaf", (0.15, 0.45, 0.15), 0.7)
    m_pot = P.mat("Pot", (0.85, 0.85, 0.82), 0.5)
    m_lamp = P.emit("Lamp", (1.0, 0.75, 0.45), 8.0)
    P.box((0, 0, -0.05), (5, 5, 0.1), m_floor, "Floor")
    P.box((0, 2.5, 1.4), (5, 0.1, 2.8), m_wall, "Back")
    P.box((-2.5, 0, 1.4), (0.1, 5, 2.8), m_wall, "Left")
    P.box((2.5, 0, 1.4), (0.1, 5, 2.8), m_wall, "Right")
    # front wall with the open doorway he walks in through (x 1.1..2.0)
    P.box((-0.7, -2.5, 1.4), (3.6, 0.1, 2.8), m_wall, "Front L")
    P.box((2.25, -2.5, 1.4), (0.5, 0.1, 2.8), m_wall, "Front R")
    P.box((1.55, -2.5, 2.45), (0.9, 0.1, 0.7), m_wall, "Lintel")
    P.box((1.12, -2.85, 1.05), (0.04, 0.82, 2.1), P.wood("Door", (0.75, 0.55, 0.35), planks=False), "Door")
    P.box((1.55, -3.3, 1.4), (1.2, 0.1, 2.8), P.mat("Hall", (0.8, 0.75, 0.68), 0.9), "Hall wall")
    P.box((-1.2, -2.44, 1.6), (0.7, 0.02, 0.9), P.mat("Poster3", (0.95, 0.75, 0.3), 0.7), "Poster")
    P.box((0, 0, 2.85), (5, 5, 0.1), P.mat("Ceil", (0.85, 0.82, 0.8), 0.9), "Ceil")
    P.window((0.9, 2.43, 1.55), 1.5, 1.4, "y", m_sky, P.mat("Frame", (0.9, 0.9, 0.88), 0.5))
    for x in (-0.05, 1.85):
        P.box((x, 2.35, 1.4), (0.35, 0.08, 2.6), m_curt, "Curtain")
    # bed along the left wall
    P.box((-1.5, 1.0, 0.13), (1.6, 2.6, 0.26), m_wood, "Bed base", bevel=0.02)
    P.box((-1.5, 1.0, 0.36), (1.5, 2.5, 0.2), m_sheet, "Mattress", bevel=0.05)
    P.box((-1.5, 0.6, 0.47), (1.62, 1.7, 0.05), m_navy, "Blanket", bevel=0.02)
    P.box((-1.5, 2.05, 0.54), (0.9, 0.35, 0.18), m_sheet, "Pillow", bevel=0.07)
    P.box((-1.5, 2.4, 0.9), (1.6, 0.08, 1.0), m_wood, "Headboard")
    # shelves with "toys" above the bed
    for z in (1.6, 2.05):
        P.box((-1.5, 2.33, z), (1.6, 0.25, 0.04), m_wood, "Shelf")
    cols = [(0.9, 0.5, 0.15), (0.2, 0.6, 0.8), (0.85, 0.25, 0.3), (0.95, 0.8, 0.2), (0.4, 0.7, 0.35), (0.6, 0.4, 0.8)]
    for i in range(10):
        x = -2.2 + i * 0.15
        z = 1.62 if i < 6 else 2.07
        P.box((x if i < 6 else x - 0.7, 2.33, z + 0.12), (0.07, 0.18, 0.24),
              P.mat(f"Book{i}", cols[i % 6], 0.7), "Book")
    P.sphere((-0.85, 2.33, 1.72), 0.08, P.mat("Toy", (0.95, 0.55, 0.15), 0.6), "Toy")
    P.sphere((-0.85, 2.33, 1.84), 0.06, P.mat("Toy2", (0.95, 0.55, 0.15), 0.6), "Toy head")
    # desk + monitor + lamp on the right
    P.box((1.6, 0.6, 0.74), (1.4, 0.65, 0.05), m_wood, "Desk")
    for dx in (-0.65, 0.65):
        P.box((1.6 + dx, 0.6, 0.37), (0.05, 0.6, 0.74), m_wood, "Desk leg")
    P.box((1.6, 0.75, 1.05), (0.6, 0.04, 0.36), m_dark, "Monitor")
    P.box((1.6, 0.725, 1.05), (0.56, 0.01, 0.32), m_screen, "Screen")
    P.cyl((2.15, 0.65, 0.77), (2.15, 0.65, 1.1), 0.012, m_dark, "Lamp arm")
    P.cyl((2.15, 0.65, 1.08), (2.15, 0.6, 1.16), 0.07, m_lamp, "Desk lamp")
    P.cyl((2.15, 2.1, 0), (2.15, 2.1, 0.35), 0.16, m_pot, "Pot")
    for i, (dx, dz, r) in enumerate(((0, 0.6, 0.3), (0.1, 0.9, 0.22), (-0.1, 1.05, 0.18))):
        P.sphere((2.15 + dx, 2.1, dz), r, m_plant, f"Plant{i}")
    P.box((0.2, 0.4, 0.008), (1.6, 1.2, 0.016), m_rug, "Rug")
    for x, c in ((0.1, (0.85, 0.45, 0.2)), (-0.2, (0.3, 0.5, 0.75))):
        P.box((x + 2.05, 2.44, 1.9), (0.4, 0.01, 0.55), P.mat(f"Poster{x}", c, 0.7), "Poster")
    # extra life: bedside table + lamp, desk chair, string lights, stuffed toys, backpack, books, hanging plant
    P.box((-0.45, 2.15, 0.25), (0.45, 0.4, 0.5), m_wood, "Bedside", bevel=0.01)
    P.cyl((-0.45, 2.15, 0.5), (-0.45, 2.15, 0.75), 0.03, m_dark, "Bed lamp foot")
    P.cyl((-0.45, 2.15, 0.72), (-0.45, 2.15, 0.9), 0.11, m_lamp, "Bed lamp")
    P.box((1.75, 0.95, 0.45), (0.5, 0.5, 0.06), m_dark, "Chair seat", bevel=0.02)
    P.box((1.75, 1.22, 0.75), (0.5, 0.06, 0.6), m_dark, "Chair back", bevel=0.02)
    P.cyl((1.75, 0.95, 0.05), (1.75, 0.95, 0.42), 0.03, m_dark, "Chair post")
    bulb = P.emit("Bulb", (1.0, 0.8, 0.45), 15.0)
    for i in range(16):
        x = -2.3 + i * 0.14
        P.sphere((x, 2.43, 2.45 - 0.12 * math.sin(i / 15 * math.pi)), 0.018, bulb, "Bulb")
    for i, (x, c) in enumerate(((-1.25, (0.85, 0.6, 0.35)), (-1.05, (0.5, 0.75, 0.9)))):
        mt = P.mat(f"Plush{i}", c, 0.95)
        P.sphere((x, 1.95, 0.62), 0.11, mt, "Plush body")
        P.sphere((x, 1.95, 0.8), 0.085, mt, "Plush head")
        for ex in (-0.05, 0.05):
            P.sphere((x + ex, 1.95, 0.88), 0.03, mt, "Plush ear")
    P.box((0.45, 1.9, 0.22), (0.35, 0.2, 0.44), P.mat("Backpack", (0.1, 0.1, 0.12), 0.8), "Backpack", bevel=0.05)
    for i in range(4):
        P.box((1.15 + i * 0.07, 0.45, 0.84), (0.05, 0.2, 0.15), P.mat(f"DBook{i}", cols[i], 0.7), "Desk book")
    for i in range(5):
        P.sphere((0.05 + 0.05 * math.sin(i), 2.3, 2.6 - 0.18 * i), 0.09 - 0.008 * i, m_plant, "Hanging leaf")
    # light: warm sunset through the window, lamps, cool fill
    P.area_light((0.9, 2.2, 1.6), (0, 0, 0.8), 260, 1.4, (1.0, 0.75, 0.5), name="Window")
    for loc, e in (((2.15, 0.6, 1.15), 25), ((-1.5, 2.1, 2.3), 35)):
        l = bpy.data.lights.new("Pt", "POINT")
        l.energy, l.color, l.shadow_soft_size = e, (1.0, 0.7, 0.42), 0.2
        o = bpy.data.objects.new("Pt", l)
        sc.collection.objects.link(o)
        o.location = loc
    P.area_light((0.5, -2.2, 2.3), (0, 1, 1), 110, 3.0, (0.75, 0.8, 1.0), name="Fill")
if PART == "room":
    MC.apply(ar, sit, start=1, length=40, offset=(-0.82, 0.6, 0.22), facing=-105, in_place=True, step=1)
    MC.flush(ar)
    sc.frame_set(20)
    cam_d.dof.use_dof = True
    cam_d.dof.focus_object = ar.rig
    cam_d.dof.aperture_fstop = 4.0
    shot(os.path.join(OUT, "board_room.png"), (1.3, -2.2, 1.55), (-0.4, 1.2, 1.0), 24, 1280, 720)

if PART == "anim":
    # Arian walks in from the door side, stops by the bed, looks around the room, then "listen..." with both hands
    import anim
    N = 150

    def smooth(u):
        u = max(0.0, min(1.0, u))
        return u * u * (3 - 2 * u)

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

    FACE = 49                                    # walking towards the back-left (the bed)
    A0 = Vector((1.55, -1.25, 0))
    play(ar, CL["start_walking"], 1, 72, offset=A0, facing=FACE, in_place=False)
    MC.flush(ar)
    sc.frame_set(72)
    p = ar.rig.matrix_world @ ar.rig.pose.bones["pelvis"].head
    stop = Vector((p.x, p.y, 0))
    play(ar, CL["nervously_look_around"], 62, 50, blend=14, offset=stop, facing=20, in_place=True)
    play(ar, CL["hands_forward_gesture"], 104, 47, blend=12, offset=stop, facing=-5, in_place=True)
    MC.flush(ar)
    for f in range(1, N + 1):
        t = (f - 1) / 24
        st = dict(t=t, seed=ar.seed, talking=(108 <= f <= 146), worry=0.4)
        for k, v in anim.face(st).items():
            if k in ar.keys:
                ar._put(ar.body.data.shape_keys, f'key_blocks["{k}"].value', 0, f, max(0.0, min(1.0, v)))
    ar.flush()
    # camera: from near the desk, follows his head with a slow drift
    sc.frame_start, sc.frame_end = 1, N
    sc.render.fps = 24
    cam_d.lens = 26
    cam_d.dof.use_dof = True
    cam_d.dof.focus_object = ar.rig
    cam_d.dof.aperture_fstop = 3.5
    for f in range(1, N + 1, 3):
        sc.frame_set(f)
        h = ar.rig.matrix_world @ ar.rig.pose.bones["head"].head
        aim.location = (h.x, h.y, h.z - 0.25)
        aim.keyframe_insert("location", frame=f)
        u = (f - 1) / (N - 1)
        cam.location = (0.35 - 0.15 * u, 2.1 - 0.25 * u, 1.55)
        cam.keyframe_insert("location", frame=f)
    sc.render.resolution_x, sc.render.resolution_y = 1280, 720
    sc.eevee.taa_render_samples = 24
    a, b = [int(v) for v in argv[argv.index("--frames") + 1:argv.index("--frames") + 3]] if "--frames" in argv else (1, N)
    d = os.path.join(HERE, "frames", "arian")
    os.makedirs(d, exist_ok=True)
    todo = [int(v) for v in argv[argv.index("--pick") + 1].split(",")] if "--pick" in argv else range(a, b + 1)
    for f in todo:
        pth = os.path.join(d, f"f_{f:04d}.png")
        if os.path.exists(pth) and "--still" not in argv:
            continue
        sc.frame_set(f)
        sc.render.filepath = pth
        bpy.ops.render.render(write_still=True)
