"""
3D stick figure eating with a spoon — Blender scene builder.

Use inside Blender:  Scripting tab -> Open this file -> Run Script.
Or from a terminal:   blender --background --python stick_figure_eating.py -- --render

It builds the whole scene (figure, chair, table, plate with food, glass,
lights, camera) and a 3-second looping animation of the figure scooping food
from the plate and eating it.  With "--render" it also renders a still image
and every animation frame next to this file.
"""

import math
import os
import sys

import bpy
from mathutils import Vector

FPS = 24
FRAMES = 72  # 3 second loop

# ---------------------------------------------------------------- helpers


def clear_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def material(name, color, rough=0.6, metal=0.0, transmission=0.0, alpha=1.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = metal
    if transmission:
        bsdf.inputs["Transmission Weight"].default_value = transmission
        bsdf.inputs["IOR"].default_value = 1.45
    if alpha < 1.0:
        bsdf.inputs["Alpha"].default_value = alpha
    return mat


def assign(obj, mat):
    obj.data.materials.clear()
    obj.data.materials.append(mat)
    return obj


def smooth(obj):
    for p in obj.data.polygons:
        p.use_smooth = True
    return obj


def sphere(name, loc, r, mat, scale=(1, 1, 1)):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=loc, segments=32, ring_count=16)
    o = bpy.context.object
    o.name = name
    o.scale = scale
    return smooth(assign(o, mat))


def box(name, loc, size, mat, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object
    o.name = name
    o.scale = size
    if bevel:
        bpy.ops.object.transform_apply(scale=True)
        m = o.modifiers.new("Bevel", "BEVEL")
        m.width = bevel
        m.segments = 3
    return assign(o, mat)


def rod(name, a, b, r, mat):
    """Cylinder from point a to point b."""
    a, b = Vector(a), Vector(b)
    d = b - a
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=d.length, location=(a + b) / 2, vertices=24)
    o = bpy.context.object
    o.name = name
    o.rotation_mode = "QUATERNION"
    o.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(d)
    return smooth(assign(o, mat))


def place_rod(o, a, b):
    a, b = Vector(a), Vector(b)
    o.location = (a + b) / 2
    o.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(b - a)


def ease(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def lerp(a, b, t):
    return a + (b - a) * t


def two_bone_ik(s, p, len_a, len_b, pole):
    """Elbow position for shoulder s, hand p, bone lengths and a pole direction."""
    d_vec = p - s
    d = max(abs(len_a - len_b) + 1e-4, min(len_a + len_b - 1e-4, d_vec.length))
    u = d_vec.normalized()
    along = (len_a * len_a - len_b * len_b + d * d) / (2 * d)
    h = math.sqrt(max(0.0, len_a * len_a - along * along))
    w = pole - u * pole.dot(u)
    w.normalize()
    return s + u * along + w * h


# ---------------------------------------------------------------- scene


def build():
    clear_scene()
    scene = bpy.context.scene
    scene.render.fps = FPS
    scene.frame_start = 1
    scene.frame_end = FRAMES

    # materials
    body = material("Stick figure", (0.05, 0.06, 0.09), rough=0.45)
    eye_white = material("Eye white", (0.95, 0.95, 0.95), rough=0.3)
    mouth_m = material("Mouth", (0.45, 0.06, 0.06), rough=0.5)
    wood = material("Wood", (0.42, 0.24, 0.12), rough=0.55)
    wood_dark = material("Wood dark", (0.25, 0.14, 0.07), rough=0.6)
    cloth = material("Table cloth", (0.86, 0.32, 0.27), rough=0.8)
    plate_m = material("Plate", (0.96, 0.96, 0.94), rough=0.25)
    steel = material("Steel", (0.8, 0.8, 0.82), rough=0.2, metal=1.0)
    rice = material("Rice", (0.97, 0.93, 0.8), rough=0.7)
    carrot = material("Carrot", (0.95, 0.42, 0.06), rough=0.5)
    pea = material("Pea", (0.25, 0.62, 0.15), rough=0.45)
    tomato = material("Tomato", (0.85, 0.12, 0.08), rough=0.3)
    glass = material("Glass", (0.95, 0.97, 1.0), rough=0.02, transmission=1.0)
    juice = material("Juice", (1.0, 0.55, 0.05), rough=0.1, transmission=0.6)
    floor_m = material("Floor", (0.62, 0.45, 0.32), rough=0.9)
    wall_m = material("Wall", (0.98, 0.94, 0.86), rough=0.95)

    # room
    bpy.ops.mesh.primitive_plane_add(size=40, location=(0, 0, 0))
    assign(bpy.context.object, floor_m).name = "Floor"
    bpy.ops.mesh.primitive_plane_add(size=40, location=(-1.6, 0, 6), rotation=(0, math.radians(90), 0))
    assign(bpy.context.object, wall_m).name = "Wall"

    # chair
    box("Chair seat", (0, 0, 0.48), (0.5, 0.5, 0.05), wood, bevel=0.015)
    box("Chair back", (-0.24, 0, 0.85), (0.04, 0.5, 0.45), wood, bevel=0.015)
    for x in (-0.22, 0.22):
        for y in (-0.22, 0.22):
            box("Chair leg", (x, y, 0.23), (0.04, 0.04, 0.46), wood_dark)

    # table
    tx = 0.78
    box("Table top", (tx, 0, 0.8), (0.75, 1.1, 0.05), wood, bevel=0.02)
    box("Table cloth", (tx, -0.12, 0.83), (0.42, 0.5, 0.005), cloth)
    for x in (tx - 0.32, tx + 0.32):
        for y in (-0.5, 0.5):
            box("Table leg", (x, y, 0.39), (0.05, 0.05, 0.78), wood_dark)

    # plate + food
    plate_c = Vector((0.62, -0.12, 0.84))
    bpy.ops.mesh.primitive_cylinder_add(radius=0.15, depth=0.015, location=plate_c, vertices=48)
    plate = smooth(assign(bpy.context.object, plate_m))
    plate.name = "Plate"
    bev = plate.modifiers.new("Bevel", "BEVEL")
    bev.width = 0.006
    bev.segments = 3
    sphere("Rice", plate_c + Vector((0.03, 0.03, 0.01)), 0.075, rice, scale=(1, 1, 0.45))
    for i, (dx, dy) in enumerate([(-0.07, 0.05), (-0.05, 0.08), (-0.08, 0.02), (-0.03, 0.1)]):
        sphere(f"Pea {i}", plate_c + Vector((dx, dy, 0.02)), 0.014, pea)
    for i, (dx, dy) in enumerate([(0.07, -0.07), (0.09, -0.03), (0.04, -0.09)]):
        bpy.ops.mesh.primitive_cylinder_add(radius=0.012, depth=0.05, location=plate_c + Vector((dx, dy, 0.02)),
                                            rotation=(math.radians(90), 0, math.radians(30 * i)))
        smooth(assign(bpy.context.object, carrot)).name = f"Carrot {i}"
    sphere("Tomato", plate_c + Vector((-0.06, -0.07, 0.03)), 0.03, tomato)

    # glass of juice
    gpos = Vector((0.72, 0.25, 0.83))
    bpy.ops.mesh.primitive_cylinder_add(radius=0.045, depth=0.15, location=gpos + Vector((0, 0, 0.075)), vertices=32)
    g = smooth(assign(bpy.context.object, glass))
    g.name = "Glass"
    sol = g.modifiers.new("Solidify", "SOLIDIFY")
    sol.thickness = 0.004
    bpy.ops.mesh.primitive_cylinder_add(radius=0.04, depth=0.1, location=gpos + Vector((0, 0, 0.055)), vertices=32)
    smooth(assign(bpy.context.object, juice)).name = "Juice"

    # ---------------- stick figure (sitting, facing +X)
    r = 0.028  # limb thickness
    hip = Vector((0, 0, 0.56))
    neck = Vector((0, 0, 1.17))
    head_c = Vector((0, 0, 1.36))
    sphere("Head", head_c, 0.16, body)
    sphere("Eye L", head_c + Vector((0.135, 0.055, 0.04)), 0.028, eye_white)
    sphere("Eye R", head_c + Vector((0.135, -0.055, 0.04)), 0.028, eye_white)
    sphere("Pupil L", head_c + Vector((0.158, 0.055, 0.04)), 0.012, body)
    sphere("Pupil R", head_c + Vector((0.158, -0.055, 0.04)), 0.012, body)
    mouth = sphere("Mouth", head_c + Vector((0.148, 0, -0.06)), 0.035, mouth_m, scale=(0.4, 1.0, 0.25))

    rod("Spine", hip, neck, r, body)
    sphere("Hip joint", hip, r * 1.2, body)
    sphere("Neck joint", neck, r * 1.2, body)

    for side, y in (("L", 0.09), ("R", -0.09)):
        h = Vector((0, y, 0.56))
        knee = Vector((0.42, y, 0.56))
        ankle = Vector((0.44, y, 0.05))
        rod(f"Thigh {side}", h, knee, r, body)
        rod(f"Shin {side}", knee, ankle, r, body)
        sphere(f"Knee {side}", knee, r * 1.15, body)
        sphere(f"Foot {side}", ankle + Vector((0.05, 0, -0.01)), 0.045, body, scale=(1.6, 0.8, 0.5))

    shoulder_l = Vector((0, 0.16, 1.1))
    shoulder_r = Vector((0, -0.16, 1.1))
    rod("Shoulders", shoulder_l, shoulder_r, r, body)

    # left arm resting on the table
    elbow_l = Vector((0.18, 0.28, 0.86))
    hand_l = Vector((0.45, 0.2, 0.86))
    rod("Upper arm L", shoulder_l, elbow_l, r, body)
    rod("Forearm L", elbow_l, hand_l, r, body)
    sphere("Elbow L", elbow_l, r * 1.15, body)
    sphere("Hand L", hand_l, 0.035, body)

    # right arm + spoon (animated)
    upper_len, fore_len, spoon_len = 0.32, 0.3, 0.2
    upper = rod("Upper arm R", shoulder_r, shoulder_r + Vector((0, 0, -upper_len)), r, body)
    fore = rod("Forearm R", Vector((0, 0, 0)), Vector((0, 0, fore_len)), r, body)
    sphere("Shoulder R", shoulder_r, r * 1.15, body)
    elbow_o = sphere("Elbow R", (0, 0, 0), r * 1.15, body)
    hand_o = sphere("Hand R", (0, 0, 0), 0.035, body)
    handle = rod("Spoon handle", Vector((0, 0, 0)), Vector((0, 0, spoon_len - 0.04)), 0.01, steel)
    bowl = sphere("Spoon bowl", (0, 0, 0), 0.04, steel, scale=(1.4, 0.95, 0.35))
    bowl.rotation_mode = "QUATERNION"
    bite = sphere("Bite of rice", (0, 0, 0), 0.028, rice, scale=(1.2, 1, 0.7))

    # key poses: spoon tip position and spoon direction (hand -> tip)
    mouth_pt = head_c + Vector((0.17, 0, -0.06))
    tip_plate = plate_c + Vector((0.02, 0.02, 0.025))
    dir_plate = Vector((0.75, 0.25, -0.6)).normalized()
    tip_mouth = mouth_pt + Vector((0.02, 0, 0))
    dir_mouth = Vector((-0.85, 0.45, 0.1)).normalized()
    pole = Vector((-0.2, -0.7, -0.7))
    head = bpy.data.objects["Head"]
    face = [bpy.data.objects[n] for n in ("Eye L", "Eye R", "Pupil L", "Pupil R")] + [mouth]
    face_rest = {o.name: o.location.copy() for o in face}

    for f in range(1, FRAMES + 1):
        # 1-12 scoop, 12-34 lift, 34-46 eat, 46-72 return
        if f <= 12:
            t = 0.0
        elif f <= 34:
            t = ease((f - 12) / 22)
        elif f <= 46:
            t = 1.0
        else:
            t = 1.0 - ease((f - 46) / 26)

        tip = tip_plate.lerp(tip_mouth, t) + Vector((0, 0, 0.12 * math.sin(math.pi * t)))
        if f <= 12:  # little scooping wiggle
            tip += Vector((0.02 * math.sin(f / 12 * math.pi), 0, -0.008 * math.sin(f / 12 * math.pi)))
        d = dir_plate.lerp(dir_mouth, t).normalized()
        hand = tip - d * spoon_len
        elbow = two_bone_ik(shoulder_r, hand, upper_len, fore_len, pole)

        place_rod(upper, shoulder_r, elbow)
        place_rod(fore, elbow, hand)
        elbow_o.location = elbow
        hand_o.location = hand
        handle.location = hand + d * (spoon_len - 0.04) / 2
        handle.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(d)
        bowl.location = tip - d * 0.01
        bowl.rotation_quaternion = Vector((1, 0, 0)).rotation_difference(d)

        # food on the spoon from scoop until it is eaten
        bite.location = tip - d * 0.01 + Vector((0, 0, 0.012))
        has_food = 10 <= f <= 38
        bite.scale = (1.2, 1, 0.7) if has_food else (0.001, 0.001, 0.001)

        # mouth opens as the spoon arrives, chews after
        if 26 <= f <= 38:
            m_open = ease((f - 26) / 8)
        elif 38 < f <= 60:
            m_open = 0.35 + 0.35 * abs(math.sin((f - 38) / 22 * 3 * math.pi))  # chewing
        else:
            m_open = 0.0
        mouth.scale = (0.4, 1.0 - 0.15 * m_open, 0.25 + 0.9 * m_open)

        # small head lean towards the spoon
        lean = Vector((0.025 * t, 0, -0.01 * t))
        head.location = head_c + lean
        for o in face:
            o.location = face_rest[o.name] + lean

        for o in (upper, fore, handle, bowl):
            o.keyframe_insert("location", frame=f)
            o.keyframe_insert("rotation_quaternion", frame=f)
        for o in (elbow_o, hand_o, head, *face):
            o.keyframe_insert("location", frame=f)
        bite.keyframe_insert("location", frame=f)
        bite.keyframe_insert("scale", frame=f)
        mouth.keyframe_insert("scale", frame=f)

    for o in (bite, mouth):
        for fc in o.animation_data.action.fcurves if hasattr(o.animation_data.action, "fcurves") else []:
            if fc.data_path == "scale":
                for kp in fc.keyframe_points:
                    kp.interpolation = "CONSTANT" if o is bite else "BEZIER"

    # ---------------- lights + camera
    bpy.ops.object.light_add(type="SUN", location=(3, -3, 5), rotation=(math.radians(45), 0, math.radians(40)))
    sun = bpy.context.object
    sun.data.energy = 3.0
    sun.data.angle = math.radians(8)
    bpy.ops.object.light_add(type="AREA", location=(1.5, -2.2, 2.4))
    key = bpy.context.object
    key.data.energy = 250
    key.data.size = 2.0
    key.rotation_euler = (Vector((0.4, 0, 0.9)) - key.location).to_track_quat("-Z", "Y").to_euler()

    world = bpy.data.worlds.new("World")
    scene.world = world
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.9, 0.82, 0.7, 1)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.6

    bpy.ops.object.camera_add(location=(2.3, -2.4, 1.55))
    cam = bpy.context.object
    cam.data.lens = 58
    target = Vector((0.36, 0, 0.9))
    cam.rotation_euler = (target - cam.location).to_track_quat("-Z", "Y").to_euler()
    scene.camera = cam

    # ---------------- render settings
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = 48
    scene.cycles.use_denoising = True
    scene.render.resolution_x = 900
    scene.render.resolution_y = 900
    scene.view_settings.view_transform = "AgX"
    scene.view_settings.look = "AgX - Punchy"
    scene.frame_set(1)
    return scene


def render(scene, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    scene.frame_set(40)
    scene.render.filepath = os.path.join(out_dir, "eating_still.png")
    bpy.ops.render.render(write_still=True)
    if "--still-only" in sys.argv:
        return
    scene.cycles.samples = 24
    scene.render.resolution_x = scene.render.resolution_y = 600
    scene.render.filepath = os.path.join(out_dir, "frames", "frame_")
    scene.render.image_settings.file_format = "PNG"
    bpy.ops.render.render(animation=True)


if __name__ == "__main__":
    sc = build()
    here = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else os.getcwd()
    if "--save" in sys.argv:
        bpy.ops.wm.save_as_mainfile(filepath=os.path.join(here, "stick_figure_eating.blend"))
    if "--render" in sys.argv:
        render(sc, os.path.join(here, "render"))
