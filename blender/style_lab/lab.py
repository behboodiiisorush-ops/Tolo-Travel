"""Style lab: the same 5-second scene (mom walks into the living room, Kian turns to her and gestures)
rendered in different looks, with smooth full-rate Mixamo motion (every frame, clips cross-faded).

    ../cast/bpy.sh lab.py --style real  --still 70          -> out/real_still.png
    ../cast/bpy.sh lab.py --style pixar --anim 1 120        -> frames/pixar/f_0001.png ...
styles: real (cinematic realistic), pixar (soft stylised 3D), clay (stop-motion clay), paint (painted)
"""
import bpy, sys, os, math
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "cast"))
sys.path.append(os.path.join(HERE, "..", "shelter3"))
sys.path.append(os.path.join(HERE, "..", "studio"))
import cast, anim  # noqa: E402
import mocap2 as MC  # noqa: E402
import props as P  # noqa: E402
import look as LK  # noqa: E402

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
def arg(name, n=1, default=None):
    if name in argv:
        i = argv.index(name)
        return argv[i + 1] if n == 1 else argv[i + 1:i + 1 + n]
    return default
STYLE = arg("--style", default="real")
STILL = arg("--still")
ANIM = arg("--anim", 2)
FPS, N = 24, 120
MOCAP = os.path.join(HERE, "..", "mocap")

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.fps = FPS

# ------------------------------------------------------------------ clips (before the heavy scene)
CL = {k: MC.load(os.path.join(MOCAP, k + ".fbx")) for k in
      ("start_walking", "walking", "breathing_idle", "thinking", "hands_forward_gesture", "head_nod_yes")}

# ------------------------------------------------------------------ cast
if STYLE != "real":
    cast.STYLE = LK.STYLE
for k, h in LK.HAIR.items():
    cast.CAST[k] = dict(cast.CAST[k], hair=h)
mom = cast.spawn("mom")
kian = cast.spawn("kian")
CH = {"mom": mom, "kian": kian}
if STYLE != "real":
    for ch in CH.values():
        cast.cartoon_face(ch)

# ------------------------------------------------------------------ room (x -3..3, y -2.6..2.6, h 2.7)
W = {
    "real": dict(wall=(0.78, 0.72, 0.62), accent=(0.42, 0.5, 0.46), sofa=(0.36, 0.42, 0.5), rug=(0.55, 0.25, 0.2)),
    "pixar": dict(wall=(0.95, 0.8, 0.6), accent=(0.35, 0.62, 0.66), sofa=(0.85, 0.42, 0.3), rug=(0.3, 0.45, 0.75)),
    "clay": dict(wall=(0.9, 0.78, 0.62), accent=(0.55, 0.72, 0.6), sofa=(0.8, 0.5, 0.35), rug=(0.45, 0.55, 0.8)),
    "paint": dict(wall=(0.92, 0.78, 0.58), accent=(0.4, 0.58, 0.62), sofa=(0.78, 0.38, 0.3), rug=(0.3, 0.42, 0.7)),
}[STYLE]
m_wall = P.mat("Wall", W["wall"], 0.85)
m_acc = P.mat("Accent wall", W["accent"], 0.85)
m_floor = P.wood("Floor", (0.5, 0.33, 0.2), planks=True)
m_sofa = P.mat("Sofa", W["sofa"], 0.9)
m_rug = P.mat("Rug", W["rug"], 0.95)
m_wood = P.wood("Table wood", (0.45, 0.28, 0.16), planks=False)
m_white = P.mat("White", (0.9, 0.9, 0.88), 0.5)
m_plant = P.mat("Leaves", (0.2, 0.45, 0.18), 0.7)
m_pot = P.mat("Pot", (0.7, 0.4, 0.28), 0.6)
m_lamp = P.emit("Lampshade", (1.0, 0.8, 0.55), 6.0)
m_sky = P.emit("Sky", (0.75, 0.85, 1.0), 2.5)

P.box((0, 0, -0.05), (6, 5.2, 0.1), m_floor, "Floor")
P.box((0, 2.65, 1.35), (6, 0.1, 2.7), m_wall, "Back wall")
P.box((-3.05, 0, 1.35), (0.1, 5.2, 2.7), m_acc, "Left wall")
P.box((3.05, 0, 1.35), (0.1, 5.2, 2.7), m_wall, "Right wall")
P.box((0, 0, 2.75), (6, 5.2, 0.1), m_white, "Ceiling")
P.window((0.9, 2.6, 1.5), 1.5, 1.3, "y", m_sky, m_white)
P.box((0.2, 0.6, 0.006), (3.2, 2.2, 0.012), m_rug, "Rug")
# sofa against the back wall, coffee table, plant, standing lamp, picture frames
P.box((-1.2, 2.15, 0.22), (2.0, 0.8, 0.44), m_sofa, "Sofa seat")
P.box((-1.2, 2.5, 0.6), (2.0, 0.2, 0.75), m_sofa, "Sofa back")
for sx in (-2.25, -0.15):
    P.box((sx, 2.15, 0.35), (0.2, 0.8, 0.7), m_sofa, "Sofa arm")
P.box((-0.9, 1.15, 0.42), (1.1, 0.55, 0.05), m_wood, "Table top")
for dx in (-0.48, 0.48):
    for dy in (-0.22, 0.22):
        P.box((-0.9 + dx, 1.15 + dy, 0.2), (0.05, 0.05, 0.4), m_wood, "Table leg")
P.cyl((2.4, 2.2, 0), (2.4, 2.2, 0.45), 0.22, m_pot, "Pot")
for i, (dx, dy, z, r) in enumerate(((0, 0, 0.75, 0.38), (0.15, -0.1, 1.05, 0.28), (-0.12, 0.05, 1.2, 0.24))):
    P.sphere((2.4 + dx, 2.2 + dy, z), r, m_plant, f"Leaves{i}")
P.cyl((-2.6, 1.9, 0), (-2.6, 1.9, 1.5), 0.02, m_wood, "Lamp pole")
P.cyl((-2.6, 1.9, 1.45), (-2.6, 1.9, 1.75), 0.2, m_lamp, "Lamp shade")
for x in (-1.7, -0.7):
    P.box((x, 2.59, 1.55), (0.6, 0.03, 0.45), m_wood, "Frame")
    P.box((x, 2.575, 1.55), (0.5, 0.01, 0.35), P.mat(f"Picture{x}", (0.6, 0.7, 0.8) if x < -1 else (0.85, 0.6, 0.4), 0.6),
          "Picture")

# light: cool daylight through the window + warm lamp + soft fill
P.area_light((0.9, 2.4, 1.6), (0.0, 0.0, 1.0), 220, 1.6, (0.8, 0.88, 1.0), name="Window light")
lamp = bpy.data.lights.new("Lamp", "POINT")
lamp.energy, lamp.color, lamp.shadow_soft_size = 90, (1.0, 0.72, 0.45), 0.25
lo = bpy.data.objects.new("Lamp", lamp)
sc.collection.objects.link(lo)
lo.location = (-2.6, 1.9, 1.6)
P.area_light((0.5, -2.4, 2.4), (0, 0.8, 1.0), 120, 3.0, (1.0, 0.92, 0.85), name="Fill")
if STYLE in ("pixar", "paint"):
    P.area_light((2.2, 2.3, 2.2), (0.0, 0.5, 1.4), 160, 0.8, (1.0, 0.85, 0.65), name="Rim")
world = bpy.data.worlds.new("World")
sc.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs[0].default_value = (0.25, 0.22, 0.2, 1)
world.node_tree.nodes["Background"].inputs[1].default_value = 0.4

# ------------------------------------------------------------------ motion (full rate, cross-faded)
def smooth(u):
    u = max(0.0, min(1.0, u))
    return u * u * (3 - 2 * u)


def play(ch, clip, start, length, blend=0, **kw):
    """Apply a clip from `start`; the first `blend` frames cross-fade from what was there."""
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


# Mom: starts walking in from the left, settles into an idle, then "wait, listen" with both hands
M0 = Vector((-2.5, 0.15, 0))
play(mom, CL["start_walking"], 1, 62, offset=M0, facing=-90, in_place=False)
stop = pelvis_xy(mom, 62)
stop.y = M0.y
play(mom, CL["breathing_idle"], 52, 69, blend=14, offset=stop, facing=-90, in_place=True, loop=True)
play(mom, CL["hands_forward_gesture"], 76, 45, blend=10, offset=stop, facing=-90, in_place=True)
# Kian: idle, turns his head to mom as she comes in, thinks, nods
K0 = Vector((0.75, 0.25, 0))
play(kian, CL["breathing_idle"], 1, 50, offset=K0, facing=100, in_place=True, src_from=2.0, loop=True)
play(kian, CL["thinking"], 40, 62, blend=14, offset=K0, facing=100, in_place=True)
play(kian, CL["head_nod_yes"], 98, 23, blend=8, offset=K0, facing=100, in_place=True)
for ch in CH.values():
    MC.flush(ch)

# heads look at each other (on top of the mocap); blinks + mom talking on 76-110
looks = {}
for who, ch in CH.items():
    e = P.empty(f"Look {who}")
    looks[who] = e
    for bn, inf in (("head", 0.7), ("neck_01", 0.3)):
        c = ch.rig.pose.bones[bn].constraints.new("DAMPED_TRACK")
        c.target, c.track_axis, c.influence = e, "TRACK_Z", inf
for f in range(1, N + 1, 3):
    sc.frame_set(f)
    hm = mom.rig.matrix_world @ mom.rig.pose.bones["head"].head
    hk = kian.rig.matrix_world @ kian.rig.pose.bones["head"].head
    looks["mom"].location = hk + Vector((0, 0, 0.03)) if f > 20 else hm + Vector((2, -0.2, -0.1))
    looks["kian"].location = hm + Vector((0, 0, 0.03)) if f > 26 else hk + Vector((-0.3, -2, -0.15))
    for e in looks.values():
        e.keyframe_insert("location", frame=f)
for who, ch in CH.items():
    for f in range(1, N + 1):
        t = (f - 1) / FPS
        st = dict(t=t, seed=ch.seed, talking=(who == "mom" and 76 <= f <= 110), worry=0.3)
        sk = ch.body.data.shape_keys
        for k, v in anim.face(st).items():
            if k in ch.keys:
                ch._put(sk, f'key_blocks["{k}"].value', 0, f, max(0.0, min(1.0, v)))
    ch.flush()

# ------------------------------------------------------------------ camera: slow push-in, shallow focus
cam_d = bpy.data.cameras.new("Cam")
cam = bpy.data.objects.new("Cam", cam_d)
sc.collection.objects.link(cam)
sc.camera = cam
cam_d.lens = 32
aim = P.empty("Aim")
tc = cam.constraints.new("TRACK_TO")
tc.target, tc.track_axis, tc.up_axis = aim, "TRACK_NEGATIVE_Z", "UP_Y"
for f, loc, at in ((1, (-0.45, -3.4, 1.5), (-0.55, 0.6, 1.1)), (N, (-0.35, -2.75, 1.45), (-0.35, 0.4, 1.15))):
    cam.location = loc
    aim.location = at
    cam.keyframe_insert("location", frame=f)
    aim.keyframe_insert("location", frame=f)
cam_d.dof.use_dof = STYLE != "paint"
cam_d.dof.focus_object = kian.rig
cam_d.dof.focus_subtarget = "head" if hasattr(cam_d.dof, "focus_subtarget") else ""
cam_d.dof.aperture_fstop = 2.2 if STYLE == "clay" else 3.2

# ------------------------------------------------------------------ looks
def principled(m):
    return next((n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None) if m.use_nodes else None


def mean_col(m):
    b = principled(m)
    if not b:
        return (0.6, 0.6, 0.6)
    s = b.inputs["Base Color"]
    if s.is_linked:
        n = s.links[0].from_node
        seen = [n]
        while seen:
            n = seen.pop()
            if n.type == "TEX_IMAGE" and n.image:
                return P._mean_color(n.image)
            seen += [l.from_node for i in n.inputs for l in i.links]
        return (0.6, 0.5, 0.45)
    return tuple(s.default_value)[:3]


if STYLE == "clay":
    keep = ("eye", "lamp", "sky")
    for o in bpy.data.objects:
        if o.type != "MESH":
            continue
        for slot in o.material_slots:
            m = slot.material
            if not m or any(k in m.name.lower() for k in keep) or m.get("clay"):
                continue
            col = mean_col(m)
            alpha_src = None
            b = principled(m)
            if b and b.inputs["Alpha"].is_linked:
                alpha_src = True
            nt = m.node_tree
            if not alpha_src:
                for n in list(nt.nodes):
                    nt.nodes.remove(n)
                out = nt.nodes.new("ShaderNodeOutputMaterial")
                b = nt.nodes.new("ShaderNodeBsdfPrincipled")
                nt.links.new(b.outputs[0], out.inputs["Surface"])
            else:
                for l in list(b.inputs["Base Color"].links):
                    nt.links.remove(l)
                for l in list(b.inputs["Normal"].links):
                    nt.links.remove(l)
            b.inputs["Base Color"].default_value = tuple(min(1, c * 1.15) for c in col[:3]) + (1,)
            b.inputs["Roughness"].default_value = 0.55
            b.inputs["Specular IOR Level"].default_value = 0.35
            tex = nt.nodes.new("ShaderNodeTexNoise")
            tex.inputs["Scale"].default_value = 60.0
            tex.inputs["Detail"].default_value = 6.0
            vor = nt.nodes.new("ShaderNodeTexVoronoi")
            vor.inputs["Scale"].default_value = 22.0
            add = nt.nodes.new("ShaderNodeMath")
            nt.links.new(tex.outputs[0], add.inputs[0])
            nt.links.new(vor.outputs[0], add.inputs[1])
            bump = nt.nodes.new("ShaderNodeBump")
            bump.inputs["Strength"].default_value = 0.18
            bump.inputs["Distance"].default_value = 0.004
            nt.links.new(add.outputs[0], bump.inputs["Height"])
            nt.links.new(bump.outputs[0], b.inputs["Normal"])
            m["clay"] = 1
if STYLE in ("pixar", "paint"):
    # cleaner, warmer, more saturated surfaces
    for m in bpy.data.materials:
        b = principled(m)
        if not b or "eye" in m.name.lower():
            continue
        s = b.inputs["Base Color"]
        if s.is_linked:
            hsv = m.node_tree.nodes.new("ShaderNodeHueSaturation")
            hsv.inputs["Saturation"].default_value = 1.25
            src = s.links[0].from_socket
            m.node_tree.links.new(src, hsv.inputs["Color"])
            m.node_tree.links.new(hsv.outputs[0], s)
        if "skin" in m.name.lower() or m.name.lower().startswith(("mom", "kian")):
            b.inputs["Roughness"].default_value = 0.55

# ------------------------------------------------------------------ render
sc.render.engine = "BLENDER_EEVEE"
ee = sc.eevee
ee.taa_render_samples = int(arg("--samples", default=32))
for prop, v in (("use_raytracing", True), ("use_shadows", True), ("shadow_ray_count", 2), ("shadow_step_count", 8)):
    if hasattr(ee, prop):
        setattr(ee, prop, v)
if hasattr(ee, "ray_tracing_options"):
    ee.ray_tracing_options.resolution_scale = "2"
if hasattr(ee, "fast_gi_method"):
    ee.use_fast_gi = True
sc.view_settings.view_transform = "AgX"
for look in (("AgX - Punchy" if STYLE in ("pixar", "clay") else "AgX - Base Contrast"),):
    try:
        sc.view_settings.look = look
    except TypeError:
        pass
sc.view_settings.exposure = {"real": 0.0, "pixar": 0.35, "clay": 0.25, "paint": 0.3}[STYLE]
sc.render.resolution_x, sc.render.resolution_y = 960, 540
sc.render.resolution_percentage = 100
sc.render.film_transparent = False
sc.render.image_settings.file_format = "PNG"
sc.frame_start, sc.frame_end = 1, N

if STYLE == "paint":
    g = bpy.data.node_groups.new("Comp", "CompositorNodeTree")
    sc.compositing_node_group = g
    g.interface.new_socket("Image", in_out="OUTPUT", socket_type="NodeSocketColor")
    rl = g.nodes.new("CompositorNodeRLayers")
    k = g.nodes.new("CompositorNodeKuwahara")
    k.inputs["Size"].default_value = 7
    try:
        k.inputs["Type"].default_value = "Anisotropic"
    except Exception:
        pass
    out = g.nodes.new("NodeGroupOutput")
    g.links.new(rl.outputs["Image"], k.inputs["Image"])
    g.links.new(k.outputs[0], out.inputs[0])

if STILL:
    os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
    for f in STILL.split(","):
        sc.frame_set(int(f))
        sc.render.filepath = os.path.join(HERE, "out", f"{STYLE}_{int(f):03d}.png")
        bpy.ops.render.render(write_still=True)
if ANIM:
    a, b = int(ANIM[0]), int(ANIM[1])
    d = os.path.join(HERE, "frames", STYLE)
    os.makedirs(d, exist_ok=True)
    for f in range(a, b + 1):
        p = os.path.join(d, f"f_{f:04d}.png")
        if os.path.exists(p):
            continue
        sc.frame_set(f)
        sc.render.filepath = p
        bpy.ops.render.render(write_still=True)
if "--save" in argv:
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(HERE, f"lab_{STYLE}.blend"))
