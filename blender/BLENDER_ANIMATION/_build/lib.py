"""Shared helpers for BLENDER_ANIMATION: paths, the «واگن آخر» toon look, props, the two sets, characters, saving.

Every .blend in BLENDER_ANIMATION/ is built by a script in this folder (see build_all.sh), so a file can always be
rebuilt from scratch:   ../../cast/bpy.sh build_characters.py
"""
import bpy, os, sys, math, random
from mathutils import Vector

BUILD = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BUILD)                          # .../BLENDER_ANIMATION
BL = os.path.dirname(ROOT)                             # .../blender
for p in ("cast", "studio", "puppets"):
    sys.path.insert(0, os.path.join(BL, p))
MOC = os.path.join(BL, "mocap")
FPS = 24


def path(*a):
    return os.path.join(ROOT, *a)


def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.fps = FPS
    return sc


# ------------------------------------------------------------------ look
def tm(name, rgb, glow=0.22):
    import puppets as PP
    return PP.toon_mat(name, rgb, glow)


def hull():
    import characters as C
    return C._hull_mat()


def outline(o, t=0.012):
    if o.type != "MESH":
        return
    o.data.materials.append(hull())
    sd = o.modifiers.new("Outline", "SOLIDIFY")
    sd.thickness = t
    sd.offset = 1.0
    sd.use_flip_normals = True
    sd.use_rim = False
    sd.material_offset = sd.material_offset_rim = len(o.data.materials) - 1


def look(sc, res=(540, 960), samples=10, sky=(0.62, 0.7, 0.8), sun=3.0, sun_rot=(50, 0, -30)):
    """Cycles toon render (the approved puppet look): flat sky, one soft sun, Standard view."""
    w = bpy.data.worlds.get("World") or bpy.data.worlds.new("World")
    sc.world = w
    w.color = sky
    w.use_nodes = True
    bg = next(n for n in w.node_tree.nodes if n.type == "BACKGROUND")
    bg.inputs["Color"].default_value = (*[c ** 2.2 for c in sky], 1)
    bg.inputs["Strength"].default_value = 1.0
    if "Sun" not in bpy.data.objects:
        s = bpy.data.objects.new("Sun", bpy.data.lights.new("Sun", "SUN"))
        sc.collection.objects.link(s)
        s.data.energy = sun
        s.data.angle = math.radians(8)
        s.rotation_euler = tuple(math.radians(a) for a in sun_rot)
    sc.render.engine = "CYCLES"
    sc.cycles.samples = samples
    sc.cycles.use_denoising = True
    sc.cycles.max_bounces = 3
    sc.view_settings.view_transform = "Standard"
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.image_settings.file_format = "PNG"


def camera(sc, loc, target, lens=35, name="Camera"):
    cam = bpy.data.objects.new(name, bpy.data.cameras.new(name))
    sc.collection.objects.link(cam)
    cam.location = loc
    cam.data.lens = lens
    d = Vector(target) - Vector(loc)
    cam.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    sc.camera = cam
    return cam


# ------------------------------------------------------------------ geometry (every part parented to a root empty)
def coll(name, parent=None):
    c = bpy.data.collections.get(name) or bpy.data.collections.new(name)
    if c.name not in (parent or bpy.context.scene.collection).children:
        (parent or bpy.context.scene.collection).children.link(c)
    return c


def _link(o, c):
    for u in list(o.users_collection):
        u.objects.unlink(o)
    c.objects.link(o)


def root(name, c):
    e = bpy.data.objects.new(name, None)
    e.empty_display_type = "PLAIN_AXES"
    c.objects.link(e)
    return e


def _part(o, r, mat, name, line):
    o.name = f"{r.name} {name}"
    o.data.materials.append(mat)
    _link(o, r.users_collection[0])
    o.parent = r
    if line:
        outline(o, line)
    return o


def B(r, loc, size, mat, name="box", bevel=0.0, rot=(0, 0, 0), line=0.01):
    bpy.ops.mesh.primitive_cube_add(location=loc, rotation=rot)
    o = bpy.context.object
    o.scale = (size[0] / 2, size[1] / 2, size[2] / 2)
    bpy.ops.object.transform_apply(scale=True)
    if bevel:
        b = o.modifiers.new("Bevel", "BEVEL")
        b.width, b.segments = bevel, 2
    return _part(o, r, mat, name, line)


def CY(r, loc, rad, depth, mat, name="cyl", rot=(0, 0, 0), verts=20, line=0.01):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=rad, depth=depth, location=loc, rotation=rot)
    o = bpy.context.object
    bpy.ops.object.shade_smooth()
    return _part(o, r, mat, name, line)


def SP(r, loc, rad, mat, name="ball", scale=(1, 1, 1), line=0.01):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=rad, location=loc, segments=20, ring_count=12)
    o = bpy.context.object
    o.scale = scale
    bpy.ops.object.transform_apply(scale=True)
    bpy.ops.object.shade_smooth()
    return _part(o, r, mat, name, line)


def place(r, loc=(0, 0, 0), rz=0.0):
    r.location = loc
    r.rotation_euler = (0, 0, math.radians(rz))
    return r


# ------------------------------------------------------------------ palette (bright, a little pastel; no logos, no text)
PAL = dict(
    wood=(0.78, 0.52, 0.3), wood_dark=(0.52, 0.32, 0.2), sheet=(0.96, 0.95, 0.9), blanket=(0.3, 0.55, 0.85),
    pillow=(0.98, 0.9, 0.55), rug=(0.9, 0.42, 0.35), wall_bed=(0.98, 0.86, 0.62), floor_bed=(0.72, 0.5, 0.34),
    ceil=(0.97, 0.96, 0.92), lamp=(1.0, 0.86, 0.4), metal=(0.62, 0.66, 0.7), dark=(0.12, 0.12, 0.14),
    glass=(0.62, 0.84, 0.95), curtain=(0.35, 0.75, 0.55), book1=(0.9, 0.3, 0.3), book2=(0.3, 0.6, 0.9),
    book3=(0.95, 0.75, 0.25), road=(0.32, 0.33, 0.36), walk=(0.75, 0.74, 0.7), curb=(0.88, 0.87, 0.84),
    line=(0.98, 0.95, 0.85), grass=(0.42, 0.75, 0.35), leaf=(0.3, 0.68, 0.32), trunk=(0.5, 0.33, 0.2),
    house1=(0.98, 0.7, 0.55), house2=(0.6, 0.8, 0.95), house3=(0.98, 0.88, 0.5), house4=(0.75, 0.9, 0.7),
    roof=(0.75, 0.32, 0.28), car=(0.92, 0.25, 0.25), tyre=(0.1, 0.1, 0.11), white=(0.97, 0.97, 0.95),
)


def M(key, glow=0.22):
    return tm("set " + key, PAL[key], glow)


# ------------------------------------------------------------------ props (each one a root empty + parts)
def bed(c, name="Bed"):
    r = root(name, c)
    B(r, (0, 0, 0.2), (1.0, 2.0, 0.24), M("wood"), "frame", 0.02)
    B(r, (0, 0, 0.38), (0.94, 1.94, 0.14), M("sheet"), "mattress", 0.04)
    B(r, (0, -0.25, 0.47), (0.98, 1.4, 0.06), M("blanket"), "blanket", 0.03)
    B(r, (0, 0.75, 0.5), (0.6, 0.3, 0.12), M("pillow"), "pillow", 0.05)
    B(r, (0, 1.02, 0.5), (1.04, 0.06, 0.8), M("wood_dark"), "headboard", 0.02)
    for x in (-0.45, 0.45):
        for y in (-0.95, 0.95):
            B(r, (x, y, 0.05), (0.07, 0.07, 0.1), M("wood_dark"), "leg", line=0)
    return r


def desk(c, name="Desk"):
    r = root(name, c)
    B(r, (0, 0, 0.74), (1.2, 0.6, 0.05), M("wood"), "top", 0.01)
    for x in (-0.56, 0.56):
        for y in (-0.26, 0.26):
            B(r, (x, y, 0.36), (0.05, 0.05, 0.72), M("wood_dark"), "leg")
    B(r, (0.35, 0, 0.6), (0.4, 0.55, 0.22), M("wood_dark"), "drawer", 0.01)
    B(r, (-0.2, 0.08, 0.95), (0.42, 0.04, 0.3), M("dark"), "screen", 0.01)        # a blank screen, no logo
    B(r, (-0.2, 0.12, 0.79), (0.06, 0.06, 0.06), M("dark"), "stand")
    for i, k in enumerate(("book1", "book2", "book3")):
        B(r, (0.4, -0.12 + i * 0.07, 0.78), (0.22, 0.06, 0.03), M(k), f"book{i}")
    return r


def chair(c, name="Chair"):
    r = root(name, c)
    B(r, (0, 0, 0.45), (0.45, 0.45, 0.05), M("wood"), "seat", 0.01)
    B(r, (0, 0.21, 0.72), (0.45, 0.04, 0.5), M("wood"), "back", 0.01)
    for x in (-0.2, 0.2):
        for y in (-0.2, 0.2):
            B(r, (x, y, 0.22), (0.04, 0.04, 0.44), M("wood_dark"), "leg")
    return r


def lamp(c, name="Lamp"):
    r = root(name, c)
    CY(r, (0, 0, 0.015), 0.1, 0.03, M("dark"), "base")
    CY(r, (0, 0, 0.22), 0.012, 0.4, M("metal"), "pole", line=0)
    CY(r, (0, 0, 0.45), 0.11, 0.14, M("lamp", 1.2), "shade", verts=16)
    li = bpy.data.objects.new(name + " light", bpy.data.lights.new(name + " light", "POINT"))
    li.data.energy, li.data.color, li.data.shadow_soft_size = 25, (1, 0.85, 0.6), 0.1
    li.location = (0, 0, 0.42)
    c.objects.link(li)
    li.parent = r
    return r


def shelf(c, name="Shelf"):
    r = root(name, c)
    for z in (0.0, 0.35, 0.7):
        B(r, (0, 0, z + 0.02), (0.9, 0.25, 0.03), M("wood"), "board")
    for x in (-0.45, 0.45):
        B(r, (x, 0, 0.36), (0.03, 0.25, 0.74), M("wood_dark"), "side")
    rnd = random.Random(3)
    for z in (0.04, 0.39):
        x = -0.4
        while x < 0.35:
            w = rnd.uniform(0.03, 0.06)
            h = rnd.uniform(0.2, 0.28)
            B(r, (x + w / 2, 0, z + h / 2), (w, 0.18, h), M(rnd.choice(("book1", "book2", "book3"))), "book", line=0.005)
            x += w + 0.008
    return r


def rug(c, name="Rug"):
    r = root(name, c)
    CY(r, (0, 0, 0.006), 0.8, 0.012, M("rug"), "rug", verts=32, line=0)
    CY(r, (0, 0, 0.008), 0.55, 0.012, M("pillow"), "ring", verts=32, line=0)
    return r


def tree(c, name="Tree", s=1.0):
    r = root(name, c)
    CY(r, (0, 0, 1.0 * s), 0.12 * s, 2.0 * s, M("trunk"), "trunk", verts=10)
    for i, (x, y, z, rr) in enumerate(((0, 0, 2.3, 0.8), (0.4, 0.2, 2.0, 0.55), (-0.35, -0.2, 2.1, 0.6), (0, 0.1, 2.8, 0.5))):
        SP(r, (x * s, y * s, z * s), rr * s, M("leaf"), f"leaves{i}")
    return r


def street_lamp(c, name="Street lamp"):
    r = root(name, c)
    CY(r, (0, 0, 2.0), 0.06, 4.0, M("dark"), "pole", verts=12)
    B(r, (0.35, 0, 3.95), (0.8, 0.08, 0.06), M("dark"), "arm")
    B(r, (0.7, 0, 3.86), (0.3, 0.18, 0.1), M("lamp", 0.8), "head", 0.02)
    return r


def bench(c, name="Bench"):
    r = root(name, c)
    for i in range(3):
        B(r, (0, -0.12 + i * 0.12, 0.45), (1.6, 0.1, 0.04), M("wood"), "slat")
    for i in range(2):
        B(r, (0, 0.24, 0.6 + i * 0.13), (1.6, 0.04, 0.1), M("wood"), "back")
    for x in (-0.7, 0.7):
        B(r, (x, 0.05, 0.22), (0.06, 0.45, 0.44), M("dark"), "leg")
    return r


def car(c, name="Car", col="car"):
    r = root(name, c)
    B(r, (0, 0, 0.55), (1.8, 4.0, 0.6), M(col), "body", 0.12)
    B(r, (0, -0.2, 1.08), (1.6, 2.1, 0.55), M(col), "cabin", 0.15)
    B(r, (0, -0.2, 1.1), (1.62, 1.7, 0.4), M("glass", 0.4), "windows", 0.1, line=0)
    for x in (-0.9, 0.9):
        for y in (-1.3, 1.3):
            CY(r, (x, y, 0.35), 0.35, 0.25, M("tyre"), "wheel", rot=(0, math.pi / 2, 0))
    for x in (-0.6, 0.6):
        B(r, (x, -2.0, 0.65), (0.3, 0.04, 0.14), M("lamp", 1.0), "headlight", line=0)
    return r


def house(c, name, col, w=6.0, h=7.0, d=6.0, door_at=0.0):
    """A plain facade facing -Y: windows and a door, no signs or numbers."""
    r = root(name, c)
    B(r, (0, d / 2, h / 2), (w, d, h), M(col), "block")
    B(r, (0, d / 2, h + 0.15), (w + 0.3, d + 0.3, 0.3), M("roof"), "cornice")
    for fl in range(int(h // 2.4)):
        z = 1.4 + fl * 2.4 if fl else None
        for k in range(int(w // 1.8)):
            x = -w / 2 + 0.9 + k * 1.8 + (w - int(w // 1.8) * 1.8) / 2
            if fl == 0 and abs(x - door_at) < 0.9:
                continue
            zz = 1.6 if fl == 0 else z + 0.4
            B(r, (x, -0.01, zz), (0.9, 0.04, 1.2), M("glass", 0.35), "window", line=0.006)
            B(r, (x, -0.04, zz - 0.62), (1.05, 0.12, 0.08), M("white"), "sill", line=0.006)
    B(r, (door_at, -0.02, 1.05), (1.0, 0.06, 2.1), M("wood_dark"), "door", line=0.006)
    B(r, (door_at, -0.3, 0.06), (1.4, 0.6, 0.12), M("curb"), "step")
    return r


# ------------------------------------------------------------------ the two sets
def bedroom(c):
    """My bedroom: 4.4 x 4.0 m, open towards -Y (the camera side), window in the back wall."""
    r = root("Bedroom", c)
    W_, D_, H_ = 4.4, 4.0, 2.7
    B(r, (0, 0, -0.05), (W_, D_, 0.1), M("floor_bed"), "floor", line=0)
    B(r, (0, D_ / 2 + 0.08, H_ / 2), (W_, 0.16, H_), M("wall_bed"), "back wall", line=0)
    B(r, (-W_ / 2 - 0.08, 0, H_ / 2), (0.16, D_, H_), M("wall_bed"), "left wall", line=0)
    B(r, (W_ / 2 + 0.08, 0, H_ / 2), (0.16, D_, H_), M("wall_bed"), "right wall", line=0)
    B(r, (0, 0, H_ + 0.05), (W_, D_, 0.1), M("ceil"), "ceiling", line=0)
    # window with curtains (sky behind)
    B(r, (0.6, D_ / 2, 1.55), (1.3, 0.18, 1.1), M("glass", 0.9), "window", line=0.008)
    B(r, (0.6, D_ / 2 - 0.1, 1.55), (1.4, 0.05, 0.06), M("white"), "window bar", line=0.006)
    B(r, (0.6, D_ / 2 - 0.1, 1.55), (0.05, 0.05, 1.2), M("white"), "window bar", line=0.006)
    for x in (-0.25, 1.45):
        B(r, (x, D_ / 2 - 0.14, 1.45), (0.35, 0.06, 1.6), M("curtain"), "curtain", 0.02)
    # door in the left wall
    B(r, (-W_ / 2 + 0.01, 0.45, 1.0), (0.06, 0.9, 2.0), M("wood"), "door", line=0.008)
    SP(r, (-W_ / 2 + 0.06, 0.8, 1.0), 0.04, M("metal"), "door knob")
    for o, at, rz in ((bed(c), (1.45, 0.7, 0), 0), (desk(c), (-1.4, 1.62, 0), 0), (chair(c), (-1.3, 1.05, 0), 180),
                      (lamp(c), (-1.75, 1.7, 0.765), 0), (shelf(c), (-2.05, -0.9, 1.3), 90), (rug(c), (-0.1, -0.2, 0), 0)):
        place(o, at, rz)
        o.parent = r
    return r


def street(c):
    """A quiet street along X: road, two sidewalks, houses on the far side, trees, lamps, a parked car."""
    r = root("Street", c)
    L = 40.0
    B(r, (0, 0, -0.05), (L, 7.0, 0.1), M("road"), "road", line=0)
    for i in range(14):
        B(r, (-L / 2 + 1.5 + i * 3.0, 0, 0.003), (1.5, 0.15, 0.01), M("line"), "lane mark", line=0)
    for s in (-1, 1):
        B(r, (0, s * 5.0, 0.07), (L, 3.0, 0.14), M("walk"), "sidewalk", line=0)
        B(r, (0, s * 3.55, 0.08), (L, 0.15, 0.16), M("curb"), "curb", line=0.006)
    B(r, (0, -12.0, -0.04), (L, 11.0, 0.08), M("grass"), "grass near", line=0)
    cols = ("house1", "house2", "house3", "house4")
    x = -L / 2 + 4
    i = 0
    while x < L / 2 - 3:
        w = (6.0, 7.5, 5.5, 6.5)[i % 4]
        hh = (7.0, 9.4, 4.8, 7.0)[i % 4]
        hs = house(c, f"House {i + 1}", cols[i % 4], w=w, h=hh, door_at=(-1.2, 1.0, 0.0, 1.5)[i % 4])
        place(hs, (x + w / 2, 6.6, 0)).parent = r
        x += w + 0.4
        i += 1
    for k, xx in enumerate(range(-16, 18, 8)):
        place(tree(c, f"Tree {k + 1}", 1.0 + 0.1 * (k % 2)), (xx, 4.0 + 1.6, 0.1)).parent = r
        place(street_lamp(c, f"Street lamp {k + 1}"), (xx + 4, 3.85, 0.1), 270).parent = r
    place(car(c, "Parked car"), (6.0, 2.4, 0), 90).parent = r
    place(bench(c, "Bench"), (-6.0, 6.0, 0.14), 180).parent = r
    return r


# ------------------------------------------------------------------ characters
def character(key, name=None):
    import puppets as PP
    return PP.spawn(key, name=name)


def clip(name):
    import mocap
    return mocap.load(os.path.join(MOC, name + ".fbx"))


def faces(ch, f0, f1, state=lambda t: {}):
    """Per-frame face keys (blinks, brows, mouth) for frames f0..f1; state(t) adds worry/smile/talking/look_at."""
    sc = bpy.context.scene
    for f in range(f0, f1 + 1):
        t = (f - 1) / FPS
        sc.frame_set(f)
        st = dict(t=t, seed=getattr(ch, "seed", 0))
        st.update(state(t))
        ch.face_pose(f, t, st)
    ch.flush()


def drop_clips():
    for o in list(bpy.data.objects):
        if o.type == "ARMATURE" and o.name.startswith(("Armature", "mixamo")) and not o.children:
            bpy.data.objects.remove(o)


def into(c, objs):
    for o in objs:
        _link(o, c)


def char_objects(ch):
    objs = [ch.rig] + [o for o in ch.objects if o != ch.rig]
    for extra in ("look_target",):
        if getattr(ch, extra, None) is not None:
            objs.append(getattr(ch, extra))
    seen, out = set(), []
    for o in objs:
        if o.name not in seen:
            seen.add(o.name)
            out.append(o)
    for o in bpy.data.objects:                       # anything else parented to the rig (eyes, hair, props)
        if o.parent in out and o.name not in seen:
            seen.add(o.name)
            out.append(o)
    return out


# ------------------------------------------------------------------ files
def append(blend, collection):
    """Append a collection from another file of the project (Environments, Assets) into this scene."""
    with bpy.data.libraries.load(blend, link=False) as (src, dst):
        dst.collections = [collection]
    c = dst.collections[0]
    bpy.context.scene.collection.children.link(c)
    return c


def save(rel, still=None):
    p = path(rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    try:
        bpy.ops.file.pack_all()
    except Exception:
        pass
    bpy.context.preferences.filepaths.save_version = 0      # no .blend1 backups
    bpy.ops.wm.save_as_mainfile(filepath=p, compress=True)
    print("saved", p, os.path.getsize(p) // 1024, "KB")
    if still is not None:
        sc = bpy.context.scene
        os.makedirs(path("_preview"), exist_ok=True)
        for f in (still if isinstance(still, (list, tuple)) else [still]):
            for g in range(sc.frame_start, f + 1):      # step there (particles simulate frame by frame)
                sc.frame_set(g)
            sc.render.filepath = path("_preview", os.path.basename(rel).replace(".blend", f"_{f:04d}.png"))
            bpy.ops.render.render(write_still=True)
