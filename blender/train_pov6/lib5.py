"""Sets copied from episode 5 (part5.py) so the car, helicopter and fog look the same."""
import math
import random
import bpy
from mathutils import Vector
from common import *  # noqa


def build_car():
    wall = toon("Car wall", (0.9, 0.82, 0.62), 0.12)
    panel = toon("Car panel", (0.12, 0.5, 0.52), 0.12)
    ceiling = toon("Car ceiling", (0.95, 0.9, 0.78), 0.12)
    floor_m = toon("Car floor", (0.38, 0.36, 0.38), 0.1)
    carpet = toon("Carpet", (0.68, 0.1, 0.14), 0.1)
    seat_m = toon("Seat", (0.15, 0.22, 0.5), 0.12)
    covers = [toon("Cover a", (0.98, 0.55, 0.1), 0.15), toon("Cover b", (0.98, 0.82, 0.2), 0.15),
              toon("Cover c", (0.9, 0.3, 0.35), 0.15)]
    table_m = toon("Table", (0.78, 0.6, 0.38), 0.12)
    metal = toon("Car metal", (0.55, 0.58, 0.62), 0.12)
    curtain = toon("Curtain", (0.98, 0.75, 0.2), 0.15)
    frame_m = toon("Window frame", (0.35, 0.36, 0.4), 0.1)

    box((0, 0, -0.05), (3.0, 26, 0.1), floor_m, "Floor")
    box((0, 0, 0.005), (0.6, 26, 0.01), carpet, "Aisle carpet")
    box((0, 0, 2.45), (3.0, 26, 0.1), ceiling, "Ceiling")
    for sx in (-1, 1):
        x = sx * 1.47
        box((x, 0, 0.42), (0.08, 26, 0.84), panel, "Lower wall")
        box((x, 0, 2.2), (0.08, 26, 0.5), wall, "Upper wall")
        box((sx * 1.2, 0, 2.38), (0.6, 26, 0.12), wall, "Ceiling cove", bevel=0.05)
        for y in range(-12, 13, 2):
            box((x, y, 1.4), (0.08, 0.42, 1.12), wall, "Window pillar")
            box((x - sx * 0.02, y + 0.35, 1.42), (0.06, 0.25, 1.05), curtain, "Curtain")
        box((x - sx * 0.03, 0, 0.86), (0.06, 26, 0.06), frame_m, "Window sill")
        box((x - sx * 0.03, 0, 1.95), (0.06, 26, 0.06), frame_m, "Window top")
        box((sx * 1.18, 0, 1.98), (0.5, 26, 0.04), metal, "Rack")
        for y in range(-11, 12, 2):
            if random.random() < 0.55:
                c = random.choice([(0.85, 0.2, 0.2), (0.2, 0.45, 0.85), (0.95, 0.7, 0.1), (0.3, 0.65, 0.3),
                                   (0.6, 0.3, 0.7)])
                box((sx * 1.2, y + random.uniform(-0.3, 0.3), 2.12), (0.4, random.uniform(0.4, 0.7), 0.25),
                    toon(f"Bag {c}", c), "Bag", bevel=0.04)
    for ye, name in ((-12.9, "Back wall"), (12.9, "Front wall")):
        box((0, ye, 1.2), (3.0, 0.1, 2.4), wall, name)
        box((0, ye - math.copysign(0.03, ye), 1.05), (0.8, 0.04, 2.0), toon("Car door", (0.5, 0.55, 0.62)), "Door")

    white = glow_mat("Ceiling light", (1.0, 0.95, 0.85), 1.1)
    for sx in (-1, 1):
        box((sx * 0.55, 0, 2.39), (0.12, 25, 0.02), white, "Light strip")

    for c in (-9, -6, -3, 0, 3, 6, 9):
        for sx in (-1, 1):
            for x in (sx * 0.62, sx * 1.12):
                for side in (1, -1):
                    y = c + side * 0.75
                    back_y = y + side * 0.26
                    box((x, y, 0.44), (0.46, 0.5, 0.12), seat_m, "Seat cushion", bevel=0.04)
                    box((x, y, 0.2), (0.4, 0.4, 0.38), metal, "Seat base")
                    box((x, back_y, 0.85), (0.46, 0.12, 0.85), seat_m, "Seat back", bevel=0.04)
                    box((x, back_y - side * 0.065, 1.13), (0.36, 0.02, 0.22), random.choice(covers), "Head cover")
            box((sx * 0.87, c, 0.74), (0.95, 0.56, 0.05), table_m, "Table", bevel=0.02)
            box((sx * 1.3, c, 0.5), (0.06, 0.12, 0.48), metal, "Table leg")


def give_radio(rahim):
    radio = box((0, 0, 0), (0.07, 0.05, 0.16), toon("Radio", (0.12, 0.12, 0.13)), "Radio", bevel=0.01)
    led = ball((0, 0, 0), 0.012, glow_mat("Radio LED", (0.2, 1.0, 0.3), 4.0), "Radio LED")
    ant = rod((0, 0, 0), (0, 0, 0.14), 0.006, toon("Radio", (0.12, 0.12, 0.13)), "Radio antenna")
    hp = rahim.hand_world("L")
    for o, d in ((radio, Vector((0, 0.05, 0.02))), (led, Vector((0.02, 0.08, 0.08))), (ant, Vector((0.02, 0.05, 0.1)))):
        o.location = hp + d
        parent_keep(o, rahim.p["elbowL"])
    return led


def build_helicopter():
    """A helicopter with a searchlight crossing the sky (car coordinates)."""
    root = empty("Helicopter")
    body_m = toon("Heli", (0.28, 0.32, 0.3), 0.15)
    dark = toon("Heli dark", (0.08, 0.08, 0.09), 0.05)
    glass = toon("Heli glass", (0.3, 0.45, 0.55), 0.3)
    parts = [ball((0, 0, 0), 1.6, body_m, "Heli body", scale=(1, 1.5, 0.9)),
             ball((0, 1.3, 0.2), 1.0, glass, "Heli canopy", scale=(1, 0.9, 0.7)),
             rod((0, -1.8, 0.2), (0, -6.5, 0.6), 0.25, body_m, "Heli tail"),
             box((0, -6.5, 1.2), (0.1, 0.8, 1.3), body_m, "Heli fin"),
             rod((-0.9, -1.2, -1.6), (-0.9, 1.8, -1.6), 0.06, dark, "Skid"),
             rod((0.9, -1.2, -1.6), (0.9, 1.8, -1.6), 0.06, dark, "Skid"),
             rod((0, 0, 1.3), (0, 0, 1.7), 0.12, dark, "Rotor mast")]
    for o in parts:
        parent_keep(o, root)
    rotor = empty("Rotor", (0, 0, 1.75))
    parent_keep(rotor, root)
    for a in (0, 90):
        b = box((0, 0, 1.75), (0.35, 12.0, 0.05), dark, "Blade")
        b.rotation_euler = (0, 0, D(a))
        parent_keep(b, rotor)
    rotor.rotation_mode = "XYZ"
    lamp = ball((0, 1.2, -1.2), 0.25, glow_mat("Searchlight", (1.0, 0.97, 0.85), 12.0), "Searchlight")
    parent_keep(lamp, root)
    bpy.ops.object.light_add(type="SPOT", location=(0, 1.2, -1.3))
    spot = bpy.context.object
    spot.data.energy = 60000
    spot.data.spot_size = D(18)
    spot.data.color = (1.0, 0.97, 0.88)
    parent_keep(spot, root)
    root.rotation_mode = "XYZ"
    root.scale = (1.5, 1.5, 1.5)
    return root, rotor


def build_fog():
    """Grey fog outside the windows: veils parallel to the train, kept out of the outlines."""
    col = bpy.data.collections.new("Fog")
    bpy.context.scene.collection.children.link(col)
    m = bpy.data.materials.new("Fog veil")
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    mix = nt.nodes.new("ShaderNodeMixShader")
    mix.inputs[0].default_value = 0.16
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = (0.7, 0.7, 0.72, 1)
    em.inputs["Strength"].default_value = 1.0
    nt.links.new(tr.outputs[0], mix.inputs[1])
    nt.links.new(em.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs["Surface"])
    for k, x in enumerate((-5.0, -8.5, -12.0, -16.0, -20.0, -25.0, 6.0, 10.0, 16.0)):
        bpy.ops.mesh.primitive_plane_add(size=1, location=(x, 0, 3.0), rotation=(0, D(90), 0))
        v = bpy.context.object
        v.scale = (9, 200, 1)
        v.name = "Fog veil"
        v.data.materials.append(m)
        v.visible_shadow = False
        v.visible_diffuse = False
        for c in list(v.users_collection):
            c.objects.unlink(v)
        col.objects.link(v)
    return col


