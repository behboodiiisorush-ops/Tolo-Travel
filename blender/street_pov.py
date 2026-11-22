"""
10-second POV street scene — cartoon-style 3D with black outlines.

A cartoon character in a green hoodie walks down a residential street, seen
from a high, wide-angle (fisheye) camera that follows behind them.  Halfway
through, they glance back over their shoulder at the camera.  A car drives past.

Use inside Blender:  Scripting tab -> Open this file -> Run Script.
Or from a terminal:   blender --background --python street_pov.py -- --render

Flags (after "--"):  --save      save street_pov.blend next to this file
                     --render    render frames to render/street_frames/
                     --still N   render only frame N to render/street_still.png
"""

import math
import os
import random
import sys

import bpy
from mathutils import Vector

FPS = 24
SECONDS = 10
FRAMES = FPS * SECONDS
WALK_SPEED = 1.25  # metres per second
STEP_TIME = 1.0  # seconds per full stride (left + right)
random.seed(7)
# Outlines come from Freestyle (render setting).  The inverted-hull option is
# kept for EEVEE users but is off by default.
USE_HULL_OUTLINES = False

# ---------------------------------------------------------------- materials

_mats = {}


def mat(name, color, rough=0.9, emit=0.0):
    if name in _mats:
        return _mats[name]
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Specular IOR Level"].default_value = 0.1
    if emit:
        b.inputs["Emission Color"].default_value = (*color, 1)
        b.inputs["Emission Strength"].default_value = emit
    _mats[name] = m
    return m


def outline_mat():
    """Black on the far side of an inverted hull, invisible on the near side."""
    if "Outline" in _mats:
        return _mats["Outline"]
    m = bpy.data.materials.new("Outline")
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    black = nt.nodes.new("ShaderNodeEmission")
    black.inputs["Color"].default_value = (0.01, 0.01, 0.01, 1)
    clear = nt.nodes.new("ShaderNodeBsdfTransparent")
    mix = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(geo.outputs["Backfacing"], mix.inputs["Fac"])
    nt.links.new(clear.outputs["BSDF"], mix.inputs[1])
    nt.links.new(black.outputs["Emission"], mix.inputs[2])
    nt.links.new(mix.outputs["Shader"], out.inputs["Surface"])
    _mats["Outline"] = m
    return m


def finish(o, m, line=0.02, smooth=False):
    o.data.materials.append(m)
    if line and USE_HULL_OUTLINES:
        o.data.materials.append(outline_mat())
        s = o.modifiers.new("Outline", "SOLIDIFY")
        s.thickness = line
        s.offset = 1
        s.use_flip_normals = True
        s.use_rim = False
        s.material_offset = 1
    if smooth:
        for p in o.data.polygons:
            p.use_smooth = True
    return o


# ---------------------------------------------------------------- primitives


def cube(loc, size, m, line=0.03, rot=(0, 0, 0), name="Box"):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    o = bpy.context.object
    o.name = name
    o.scale = size
    bpy.ops.object.transform_apply(scale=True)
    return finish(o, m, line)


def cyl(loc, r, depth, m, line=0.02, rot=(0, 0, 0), verts=24, name="Cyl"):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=depth, location=loc, rotation=rot, vertices=verts)
    o = bpy.context.object
    o.name = name
    return finish(o, m, line, smooth=True)


def ball(loc, r, m, line=0.015, scale=(1, 1, 1), name="Ball"):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=loc, segments=24, ring_count=12)
    o = bpy.context.object
    o.name = name
    o.scale = scale
    bpy.ops.object.transform_apply(scale=True)
    return finish(o, m, line, smooth=True)


def roof(loc, width, depth, height, m):
    """Gable roof: triangular prism, ridge along Y."""
    bpy.ops.mesh.primitive_cylinder_add(vertices=3, radius=1, depth=depth, location=loc,
                                        rotation=(math.radians(90), 0, 0))
    o = bpy.context.object
    o.name = "Roof"
    o.rotation_euler = (math.radians(90), math.radians(-90), 0)
    o.scale = (height / 1.5, width / 1.732 * 1.0, 1)
    bpy.ops.object.transform_apply(rotation=True, scale=True)
    # move so the base sits at loc.z
    zmin = min((o.matrix_world @ v.co).z for v in o.data.vertices)
    o.location.z += loc[2] - zmin
    return finish(o, m, 0.04)


def empty(name, loc, parent=None):
    o = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(o)
    o.location = loc
    o.parent = parent
    return o


def parent_keep(child, parent):
    mw = child.matrix_world.copy()
    child.parent = parent
    child.matrix_parent_inverse = parent.matrix_world.inverted()
    child.matrix_world = mw


# ---------------------------------------------------------------- street


def build_street():
    asphalt = mat("Asphalt", (0.09, 0.095, 0.105))
    side = mat("Sidewalk", (0.55, 0.54, 0.5))
    curb = mat("Curb", (0.62, 0.62, 0.6))
    paint = mat("Road paint", (0.97, 0.97, 0.95))
    grass = mat("Grass", (0.42, 0.62, 0.3))

    y0, y1 = -30, 70
    length, mid = y1 - y0, (y0 + y1) / 2
    cube((0, mid, -0.05), (8, length, 0.1), asphalt, line=0, name="Road")
    for sx in (-1, 1):
        cube((sx * 5.25, mid, 0.08), (2.5, length, 0.16), side, line=0.02, name="Sidewalk")
        cube((sx * 4.05, mid, 0.09), (0.1, length, 0.18), curb, line=0.02, name="Curb")
        cube((sx * 9, mid, 0.02), (5, length, 0.04), grass, line=0, name="Front yard")
        # paving lines on the sidewalk
        for y in range(y0, y1, 2):
            cube((sx * 5.25, y, 0.161), (2.5, 0.03, 0.002), curb, line=0, name="Paving joint")
    for y in range(y0, y1, 6):
        cube((0, y, 0.001), (0.18, 3, 0.01), paint, line=0, name="Lane dash")
    # crossing
    for i in range(7):
        cube((-3.3 + i * 1.1, 24, 0.002), (0.6, 3, 0.01), paint, line=0, name="Zebra")


def build_house(x, y, facing):
    walls = random.choice([(0.96, 0.9, 0.8), (0.93, 0.85, 0.75), (0.98, 0.95, 0.9), (0.88, 0.9, 0.86)])
    wall = mat(f"Wall {walls}", walls)
    roof_m = mat("Roof tiles", (0.78, 0.33, 0.24))
    glass = mat("Window glass", (0.45, 0.6, 0.72), rough=0.2)
    frame = mat("Window frame", (0.97, 0.97, 0.97))
    door = mat("Door", (0.45, 0.25, 0.15))

    w, d, h = random.uniform(5.5, 7), random.uniform(5, 6.5), random.uniform(4.5, 6.5)
    cube((x, y, h / 2), (d, w, h), wall, line=0.05, name="House")
    roof((x, y, h), d + 0.5, w + 0.6, random.uniform(2, 3), roof_m)
    fx = x - facing * (d / 2 + 0.03)  # street-facing wall
    floors = 2 if h > 5 else 1
    for fl in range(floors):
        z = 1.6 + fl * 2.4
        for wy in (-w / 4, w / 4):
            if fl == 0 and wy < 0:
                continue
            cube((fx, y + wy, z), (0.12, 1.3, 1.2), frame, line=0.02, name="Window frame")
            cube((fx - facing * 0.03, y + wy, z), (0.1, 1.1, 1.0), glass, line=0, name="Window")
            cube((fx - facing * 0.07, y + wy, z), (0.04, 0.06, 1.0), frame, line=0, name="Mullion")
    cube((fx, y - w / 4, 1.05), (0.12, 1.0, 2.1), door, line=0.02, name="Door")
    # chimney
    cube((x + random.uniform(-1, 1), y + w / 3, h + 2.2), (0.6, 0.6, 1.6), roof_m, line=0.03, name="Chimney")


def build_tree(x, y):
    trunk = mat("Trunk", (0.42, 0.28, 0.17))
    leaf = mat("Leaves", (0.3, 0.55, 0.25))
    leaf2 = mat("Leaves light", (0.42, 0.65, 0.28))
    h = random.uniform(2.2, 3.0)
    cyl((x, y, h / 2), 0.14, h, trunk, line=0.02, name="Trunk")
    for i in range(3):
        ball((x + random.uniform(-0.5, 0.5), y + random.uniform(-0.5, 0.5), h + random.uniform(0, 0.9)),
             random.uniform(0.9, 1.25), random.choice([leaf, leaf2]), line=0.04, name="Foliage")


def build_lamp(x, y, facing):
    pole = mat("Lamp pole", (0.2, 0.22, 0.25), rough=0.5)
    light = mat("Lamp glass", (1.0, 0.95, 0.75), emit=0.5)
    cyl((x, y, 2.4), 0.07, 4.8, pole, line=0.015, name="Lamp pole")
    cube((x - facing * 0.45, y, 4.75), (0.9, 0.12, 0.1), pole, line=0.015, name="Lamp arm")
    cube((x - facing * 0.85, y, 4.65), (0.45, 0.3, 0.15), light, line=0.015, name="Lamp head")


def build_car(x, y, color, heading=0.0, name="Car"):
    body = mat(f"Car {color}", color, rough=0.4)
    glass = mat("Car glass", (0.25, 0.35, 0.45), rough=0.15)
    tyre = mat("Tyre", (0.08, 0.08, 0.08))
    root = empty(name, (x, y, 0))
    root.rotation_euler = (0, 0, heading)
    parts = [
        cube((x, y, 0.65), (1.8, 4.2, 0.7), body, line=0.03, name=f"{name} body"),
        cube((x, y - 0.2, 1.25), (1.6, 2.2, 0.6), glass, line=0.03, name=f"{name} cabin"),
        cube((x, y - 0.2, 1.57), (1.6, 2.0, 0.06), body, line=0.02, name=f"{name} roof"),
    ]
    for dx in (-0.85, 0.85):
        for dy in (-1.35, 1.35):
            parts.append(cyl((x + dx, y + dy, 0.35), 0.35, 0.3, tyre, line=0.02,
                             rot=(0, math.radians(90), 0), name=f"{name} wheel"))
    bpy.context.view_layer.update()
    for p in parts:
        parent_keep(p, root)
    return root


def build_neighbourhood():
    for side in (-1, 1):
        y = -26
        while y < 66:
            build_house(side * 13, y + random.uniform(-0.5, 0.5), side)
            y += random.uniform(8.5, 10.5)
        for ty in range(-24, 66, 9):
            build_tree(side * 8.2, ty + random.uniform(-1, 1))
        for ly in range(-20, 66, 14):
            build_lamp(side * 4.4, ly, side)
        # low fences between yards and sidewalk
        fence = mat("Fence", (0.97, 0.97, 0.95))
        for fy in range(-28, 68, 4):
            cube((side * 6.7, fy, 0.45), (0.08, 3.6, 0.08), fence, line=0.01, name="Fence rail")
            cube((side * 6.7, fy - 1.8, 0.35), (0.12, 0.12, 0.7), fence, line=0.01, name="Fence post")

    colors = [(0.75, 0.15, 0.12), (0.15, 0.3, 0.6), (0.92, 0.92, 0.9), (0.2, 0.2, 0.22), (0.95, 0.7, 0.15)]
    for i, py in enumerate([-12, -2, 12, 30, 41, 55]):
        build_car(3.0, py, colors[i % len(colors)], heading=math.radians(180) if i % 2 else 0, name=f"Parked car {i}")
    for i, py in enumerate([-6, 18, 36, 60]):
        build_car(-3.0, py, colors[(i + 2) % len(colors)], name=f"Parked car L{i}")

    # mailbox and bins on the walker's sidewalk
    red = mat("Mailbox red", (0.8, 0.2, 0.15))
    cube((6.2, 9, 0.75), (0.5, 0.4, 0.8), red, line=0.02, name="Mailbox")
    cyl((6.2, 9, 0.2), 0.06, 0.4, mat("Lamp pole", (0.2, 0.22, 0.25)), line=0.01, name="Mailbox post")
    bin_m = mat("Bin", (0.25, 0.4, 0.3))
    for by in (15.5, 16.3):
        cube((6.3, by, 0.6), (0.6, 0.65, 0.9), bin_m, line=0.02, name="Bin")

    # moving car on the far lane
    mover = build_car(-1.9, 70, (0.2, 0.45, 0.75), heading=math.radians(180), name="Passing car")
    mover.keyframe_insert("location", frame=1)
    mover.location.y = -40
    mover.keyframe_insert("location", frame=FRAMES)
    for fc in _fcurves(mover):
        for k in fc.keyframe_points:
            k.interpolation = "LINEAR"


def _fcurves(obj):
    act = obj.animation_data.action
    if hasattr(act, "fcurves"):
        return list(act.fcurves)
    out = []  # Blender 5 layered actions
    for layer in act.layers:
        for strip in layer.strips:
            for bag in strip.channelbags:
                out.extend(bag.fcurves)
    return out


# ---------------------------------------------------------------- character


def build_walker(start):
    skin = mat("Skin", (0.95, 0.72, 0.55))
    hoodie = mat("Hoodie", (0.2, 0.55, 0.35))
    jeans = mat("Jeans", (0.28, 0.36, 0.55))
    shoe = mat("Shoes", (0.95, 0.95, 0.95))
    hair = mat("Hair", (0.12, 0.08, 0.06))
    eye = mat("Eye white", (1, 1, 1))
    pupil = mat("Pupil", (0.05, 0.05, 0.05))
    bag_m = mat("Backpack", (0.85, 0.45, 0.15))

    root = empty("Walker", start)
    body = empty("Body", (0, 0, 0), root)  # bobs up and down

    def add(o, par):
        bpy.context.view_layer.update()
        parent_keep(o, par)
        return o

    sx, sy, sz = start
    # torso + backpack
    add(cyl((sx, sy, 1.12), 0.24, 0.6, hoodie, line=0.02, name="Torso"), body)
    add(ball((sx, sy, 1.42), 0.24, hoodie, line=0.02, scale=(1, 0.85, 0.45), name="Shoulders"), body)
    add(ball((sx, sy, 0.84), 0.24, jeans, line=0.02, scale=(1, 0.9, 0.45), name="Hips"), body)
    add(cube((sx, sy - 0.3, 1.15), (0.42, 0.18, 0.5), bag_m, line=0.02, name="Backpack"), body)
    # head (separate pivot so it can turn)
    neck = add(empty("Neck", (sx, sy, 1.5)), body)
    add(cyl((sx, sy, 1.55), 0.08, 0.12, skin, line=0.01, name="Neck"), neck)
    add(ball((sx, sy, 1.78), 0.21, skin, line=0.02, name="Head"), neck)
    add(ball((sx, sy - 0.03, 1.86), 0.225, hair, line=0.02, scale=(1, 1, 0.8), name="Hair"), neck)
    for ex in (-0.075, 0.075):
        add(ball((sx + ex, sy + 0.18, 1.8), 0.045, eye, line=0.006, name="Eye"), neck)
        add(ball((sx + ex, sy + 0.215, 1.8), 0.02, pupil, line=0, name="Pupil"), neck)
    add(ball((sx, sy + 0.21, 1.72), 0.025, skin, line=0.004, name="Nose"), neck)

    limbs = {}
    for name, x in (("L", 0.12), ("R", -0.12)):
        hip = add(empty(f"Hip {name}", (sx + x, sy, 0.85)), body)
        add(cyl((sx + x, sy, 0.5), 0.09, 0.72, jeans, line=0.015, name=f"Leg {name}"), hip)
        add(cube((sx + x, sy + 0.06, 0.1), (0.15, 0.3, 0.12), shoe, line=0.015, name=f"Shoe {name}"), hip)
        limbs[f"leg{name}"] = hip
    for name, x in (("L", 0.3), ("R", -0.3)):
        sh = add(empty(f"Shoulder {name}", (sx + x, sy, 1.4)), body)
        add(cyl((sx + x, sy, 1.13), 0.07, 0.55, hoodie, line=0.015, name=f"Arm {name}"), sh)
        add(ball((sx + x, sy, 0.83), 0.07, skin, line=0.01, name=f"Hand {name}"), sh)
        limbs[f"arm{name}"] = sh
    return root, body, neck, limbs


def animate_walker(root, body, neck, limbs, start):
    for o in (root, body, neck, *limbs.values()):
        o.rotation_mode = "XYZ"
    for f in range(1, FRAMES + 1):
        t = (f - 1) / FPS
        phase = 2 * math.pi * t / STEP_TIME
        # slow down and stop a moment while looking back (5.0s - 7.0s)
        look = 0.0
        if 4.8 <= t <= 7.4:
            look = math.sin(math.pi * (t - 4.8) / 2.6)
        stride = 1.0 - 0.6 * look
        root.location = (start[0], start[1] + WALK_SPEED * t - 0.6 * (1 - math.cos(math.pi * max(0, min(1, (t - 4.8) / 2.6)))) / 2, 0)
        root.keyframe_insert("location", frame=f)

        swing = math.radians(28) * math.sin(phase) * stride
        limbs["legL"].rotation_euler = (swing, 0, 0)
        limbs["legR"].rotation_euler = (-swing, 0, 0)
        limbs["armL"].rotation_euler = (-swing * 1.1, 0, math.radians(-4))
        limbs["armR"].rotation_euler = (swing * 1.1, 0, math.radians(4))
        body.location = (0, 0, 0.035 * abs(math.sin(phase)) * stride)
        # turn head back over the right shoulder, tilt up towards the camera
        neck.rotation_euler = (math.radians(28) * look, 0, math.radians(140) * look)
        for o in (limbs["legL"], limbs["legR"], limbs["armL"], limbs["armR"], neck):
            o.keyframe_insert("rotation_euler", frame=f)
        body.keyframe_insert("location", frame=f)


# ---------------------------------------------------------------- camera + light


def build_camera(root):
    cam_data = bpy.data.cameras.new("POV cam")
    cam = bpy.data.objects.new("POV cam", cam_data)
    bpy.context.collection.objects.link(cam)
    cam_data.lens = 15  # very wide, like a ceiling security camera
    cam_data.sensor_width = 36
    cam_data.sensor_fit = "VERTICAL"
    # follow from high up and behind, slightly to the road side
    cam.parent = root
    cam.location = (-1.1, -2.4, 4.4)
    look_at = Vector((0.3, 2.4, 0.4))
    cam.rotation_euler = (look_at - cam.location).to_track_quat("-Z", "Y").to_euler()
    bpy.context.scene.camera = cam
    return cam


def build_lights(scene):
    bpy.ops.object.light_add(type="SUN", rotation=(math.radians(40), math.radians(15), math.radians(30)))
    sun = bpy.context.object
    sun.data.energy = 3.2
    sun.data.angle = math.radians(3)
    world = bpy.data.worlds.new("Sky")
    scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (0.78, 0.84, 0.92, 1)
    bg.inputs["Strength"].default_value = 1.0


# ---------------------------------------------------------------- main


def build():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.fps = FPS
    scene.frame_start, scene.frame_end = 1, FRAMES

    build_street()
    build_neighbourhood()
    start = (5.4, -1.0, 0)
    root, body, neck, limbs = build_walker(start)
    animate_walker(root, body, neck, limbs, start)
    build_camera(root)
    build_lights(scene)

    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = 12
    scene.cycles.use_denoising = True
    scene.cycles.max_bounces = 8
    scene.cycles.diffuse_bounces = 1
    scene.cycles.glossy_bounces = 1
    scene.cycles.transmission_bounces = 0
    scene.cycles.transparent_max_bounces = 8
    scene.render.resolution_x = 540
    scene.render.resolution_y = 960
    # black cartoon outlines
    scene.render.use_freestyle = True
    scene.render.line_thickness_mode = "ABSOLUTE"
    scene.render.line_thickness = 1.6
    ls = scene.view_layers[0].freestyle_settings.linesets[0]
    ls.select_by_visibility = True
    ls.select_silhouette = ls.select_border = ls.select_crease = True
    if ls.linestyle is None:
        ls.linestyle = bpy.data.linestyles.new("Cartoon line")
    ls.linestyle.color = (0.02, 0.02, 0.02)
    ls.linestyle.thickness = 1.6
    scene.view_settings.view_transform = "Standard"
    scene.view_settings.look = "None"
    scene.frame_set(1)
    return scene


def arg_value(flag, default=None):
    if flag in sys.argv:
        i = sys.argv.index(flag)
        if i + 1 < len(sys.argv):
            return sys.argv[i + 1]
    return default


if __name__ == "__main__":
    sc = build()
    here = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else os.getcwd()
    out = os.path.join(here, "render")
    if "--save" in sys.argv:
        bpy.ops.wm.save_as_mainfile(filepath=os.path.join(here, "street_pov.blend"))
    still = arg_value("--still")
    if still:
        sc.frame_set(int(still))
        sc.render.filepath = os.path.join(out, f"street_still_{int(still):03d}.png")
        bpy.ops.render.render(write_still=True)
    if "--render" in sys.argv:
        sc.render.filepath = os.path.join(out, "street_frames", "frame_")
        sc.render.image_settings.file_format = "PNG"
        bpy.ops.render.render(animation=True)
