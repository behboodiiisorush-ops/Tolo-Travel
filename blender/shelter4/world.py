"""World pieces of «پناهگاه ۳» (copied from shelter3/pov.py) placed for episode 4: the bus stopped in the forest
at night (bus front at x = X_STOP, facing -X), the road along X, pines both sides, the beast, the far car, dogs."""
import math
import random

import bpy
from mathutils import Vector

from pcommon import *  # noqa: F401,F403
from captions import END

FPS = 24
N = int(END * FPS)
BX, DOOR_Y = 0.0, 0.0
EYE = 1.55
ROAD_Y = -9.0
BUS_Y = ROAD_Y + 2.0
BUS_LEN, BUS_HW, FLOOR = 11.0, 1.25, 0.9
X_STOP = 0.0
X_FOREST = 60.0
X_CITY_END = 400.0


def W(u, v, z):
    """bus-local -> world (the bus stands still: front at X_STOP, u = metres back = +X, v = +Y)"""
    return Vector((X_STOP + u, BUS_Y + v, z))


def ground_and_road():
    asphalt = toon("Asphalt", (0.25, 0.25, 0.27), 0.08)
    line = toon("Road line", (0.85, 0.82, 0.62), 0.3)
    x0, x1 = X_STOP - 260, BX + 60
    box(((x0 + x1) / 2, ROAD_Y, -0.04), (x1 - x0, 8, 0.08), asphalt, "Road")
    for x in range(int(x0), int(x1), 7):
        box((x, ROAD_Y, 0.002), (3.0, 0.16, 0.01), line, "Road line")
    box(((x0 + x1) / 2, ROAD_Y, -0.1), (x1 - x0, 400, 0.1), toon("Ash ground", (0.42, 0.4, 0.37), 0.08), "Ground")
    side = toon("Sidewalk", (0.48, 0.47, 0.45), 0.1)
    for sy in (-1, 1):
        box(((X_CITY_END + x1) / 2, ROAD_Y + sy * 5.5, 0.06), (x1 - X_CITY_END, 3, 0.12), side, "Sidewalk")


def forest():
    """pines on both sides, from the edge of the city to beyond where the bus stops, + the eyes in the trees."""
    rnd = random.Random(9)
    trunk = toon("Trunk", (0.22, 0.16, 0.12), 0.05)
    greens = [toon("Pine a", (0.12, 0.24, 0.16), 0.06), toon("Pine b", (0.16, 0.3, 0.2), 0.06),
              toon("Pine c", (0.1, 0.2, 0.15), 0.06)]
    tpl = []
    tpl.append(rod((0, 0, 0), (0, 0, 3.5), 0.22, trunk, "Trunk"))
    for k in range(3):
        bpy.ops.mesh.primitive_cone_add(radius1=10 * (0.28 - 0.06 * k), depth=4.5, location=(0, 0, 10 * (0.45 + 0.2 * k)),
                                        vertices=12)
        tpl.append(finish(bpy.context.object, greens[k], "Pine", True))
    bpy.ops.object.select_all(action="DESELECT")
    for o in tpl:
        o.select_set(True)
    bpy.context.view_layer.objects.active = tpl[0]
    bpy.ops.object.join()
    pine = bpy.context.object
    pine.name = "Pine"
    pine.location = (0, 0, -100)
    col = bpy.context.scene.collection
    x = X_FOREST + 10
    while x > X_STOP - 250:
        for sy in (-1, 1):
            for row in range(3):
                o = pine.copy()
                o.location = (x + rnd.uniform(-2.5, 2.5), ROAD_Y + sy * (6.5 + row * 4.5 + rnd.uniform(0, 3)), 0)
                sc_ = rnd.uniform(0.7, 1.3)
                o.scale = (sc_, sc_, sc_)
                o.rotation_euler = (0, 0, rnd.uniform(0, 6.28))
                col.objects.link(o)
        x -= rnd.uniform(3.0, 4.5)
    # eyes in the trees: pairs that open (scale up) from T_EYES
    eye_m = glow_mat("Eyes in trees", (1.0, 0.85, 0.25), 6.0)
    eyes = []
    for k in range(9):
        ex = X_STOP + 6 - k * 4.5 + rnd.uniform(-1, 1)
        ey = ROAD_Y + 8.5 + rnd.uniform(0, 5)
        ez = rnd.uniform(0.4, 0.8)
        for dx in (-0.09, 0.09):
            eyes.append(ball((ex, ey + dx, ez), 0.045, eye_m, "Eyes in trees", seg=8))
    return eyes


def far_car():
    """the car at the end of the road whose headlights come on (n7)"""
    x = X_STOP - 42
    body = toon("Far car", (0.12, 0.12, 0.13), 0.02)
    box((x, ROAD_Y - 1.5, 0.75), (4.4, 1.9, 1.0), body, "Far car body", bevel=0.15)
    box((x - 0.3, ROAD_Y - 1.5, 1.45), (2.2, 1.7, 0.6), body, "Far car cabin", bevel=0.12)
    lamp_m = glow_mat("Far headlights", (1.0, 0.95, 0.8), 400.0)
    heads = [ball((x + 2.22, ROAD_Y - 1.5 + dy, 0.8), 0.3, lamp_m, "Far headlight", scale=(0.4, 1, 0.7))
             for dy in (-0.62, 0.62)]
    bpy.ops.object.light_add(type="SPOT", location=(x + 2.4, ROAD_Y - 1.5, 0.9), rotation=(0, D(-88), 0))
    sp = bpy.context.object
    sp.data.energy = 0
    sp.data.spot_size = D(50)
    sp.data.color = (1.0, 0.95, 0.85)
    root = empty("Far car root", (x, ROAD_Y - 1.5, 0))
    for o in [o for o in bpy.data.objects if o.name.startswith("Far ")] + [sp]:
        if o is not root and o.parent is None:
            parent_keep(o, root)
    return heads, sp, root


def bus():
    """an old cream bus with an orange band; everything parented to BUS (keyed along the road)."""
    root = empty("BUS", (0, 0, 0))
    cream = toon("Bus cream", (0.9, 0.86, 0.74), 0.15)
    band = toon("Bus band", (0.92, 0.45, 0.12), 0.2)
    dark = toon("Bus dark", (0.1, 0.1, 0.11), 0.03)
    seat_m = toon("Bus seat", (0.22, 0.32, 0.6), 0.1)
    seat_top = toon("Bus seat top", (0.75, 0.2, 0.18), 0.12)
    floor_m = toon("Bus floor", (0.32, 0.3, 0.3), 0.06)
    pole_m = toon("Bus pole", (0.95, 0.78, 0.15), 0.25)
    glass = glass_mat()
    L, HW = BUS_LEN, BUS_HW
    parts = []
    B = lambda *a, **k: parts.append(box(*a, **k)) or parts[-1]          # noqa: E731
    B((L / 2, 0, FLOOR - 0.05), (L, 2 * HW, 0.1), floor_m, "Bus floor")
    B((L / 2, 0, 3.25), (L + 0.1, 2 * HW + 0.1, 0.12), cream, "Bus roof", bevel=0.05)
    B((L / 2, 0, 3.17), (L - 0.2, 2 * HW - 0.1, 0.02), toon("Bus ceiling", (0.95, 0.93, 0.86), 0.25), "Bus ceiling")
    for sv in (-1, 1):
        y = sv * HW
        B((L / 2, y, 0.95), (L, 0.08, 1.5), cream, "Bus side low")
        B((L / 2, y * 1.003, 1.55), (L, 0.09, 0.22), band, "Bus band")
        B((L / 2, y, 3.0), (L, 0.08, 0.4), cream, "Bus side top")
        for k in range(7):
            u = 1.0 + k * 1.6
            if sv > 0 and k == 0:
                continue                        # the door opening (front right)
            B((u, y, 2.3), (0.14, 0.09, 1.1), cream, "Bus pillar")
        B((L / 2, y * 0.995, 2.3), (L, 0.02, 1.0), glass, "Bus window")
    B((L, 0, 2.0), (0.08, 2 * HW, 2.5), cream, "Bus back")
    B((0, 0, 0.95), (0.1, 2 * HW, 1.5), cream, "Bus front low")
    B((-0.02, 0, 2.35), (0.03, 2 * HW - 0.1, 1.25), glass, "Bus windshield")
    B((0, 0, 3.05), (0.12, 2 * HW, 0.35), dark, "Bus sign")
    # the door leaves (fold open)
    leaves = []
    for j, u0 in enumerate((0.25, 0.85)):
        piv = empty(f"Bus door pivot {j}", (u0 if j == 0 else 1.45, HW, 0))
        leaf = box((u0 + 0.3 if j == 0 else 1.15, HW + 0.01, 1.8), (0.58, 0.05, 2.0), glass, "Bus door leaf")
        frame = box((u0 + 0.3 if j == 0 else 1.15, HW + 0.02, 1.8), (0.6, 0.03, 0.08), dark, "Bus door bar")
        parent_keep(leaf, piv)
        parent_keep(frame, piv)
        leaves.append((piv, j))
        parts.append(piv)
    B((1.0, HW - 0.4, 0.55), (0.9, 0.8, 0.3), floor_m, "Bus step")
    # seats: rows each side, aisle in the middle
    rows = [3.0 + 1.05 * k for k in range(8)]
    for u in rows:
        for v in (-0.78, 0.78):
            B((u, v, FLOOR + 0.42), (0.5, 0.95, 0.12), seat_m, "Bus seat", bevel=0.04)
            B((u + 0.28, v, FLOOR + 0.66), (0.1, 0.95, 0.5), seat_m, "Bus seat back", bevel=0.04)
            B((u + 0.28, v, FLOOR + 0.93), (0.14, 0.97, 0.08), seat_top, "Bus seat top", bevel=0.03)
    for u in rows[::2]:
        parts.append(rod((u + 0.4, 0.32, FLOOR), (u + 0.4, 0.32, 3.15), 0.025, pole_m, "Bus pole"))
    # driver: seat, wheel, dashboard
    B((1.3, -0.65, FLOOR + 0.45), (0.55, 0.6, 0.12), seat_m, "Driver seat")
    B((1.6, -0.65, FLOOR + 0.9), (0.1, 0.6, 0.8), seat_m, "Driver seat back")
    B((0.35, 0, FLOOR + 0.7), (0.5, 2 * HW - 0.2, 0.25), dark, "Dashboard")
    bpy.ops.mesh.primitive_torus_add(location=(0.75, -0.65, FLOOR + 1.0), rotation=(0, D(60), 0), major_radius=0.22,
                                     minor_radius=0.025, major_segments=20, minor_segments=6)
    parts.append(finish(bpy.context.object, dark, "Steering wheel", True))
    # wheels
    tyre = toon("Tyre", (0.07, 0.07, 0.07), 0.0)
    hub = toon("Hub", (0.6, 0.6, 0.62), 0.1)
    for u in (1.8, L - 2.2):
        for sv in (-1, 1):
            bpy.ops.mesh.primitive_cylinder_add(radius=0.5, depth=0.32, location=(u, sv * (HW - 0.05), 0.5),
                                                rotation=(D(90), 0, 0), vertices=20)
            parts.append(finish(bpy.context.object, tyre, "Bus tyre", True))
            bpy.ops.mesh.primitive_cylinder_add(radius=0.22, depth=0.34, location=(u, sv * (HW - 0.05), 0.5),
                                                rotation=(D(90), 0, 0), vertices=12)
            parts.append(finish(bpy.context.object, hub, "Bus hub", True))
    # headlights + interior lights
    hl = glow_mat("Bus headlight", (1.0, 0.95, 0.8), 12.0)
    for sv in (-1, 1):
        parts.append(ball((-0.02, sv * 0.85, 0.85), 0.13, hl, "Bus headlight", scale=(0.4, 1, 1)))
    lamp = glow_mat("Bus lamp", (1.0, 0.85, 0.6), 3.0)
    lights = []
    for u in (2.5, 5.5, 8.5):
        parts.append(box((u, 0, 3.13), (0.9, 0.25, 0.04), lamp, "Bus lamp"))
        bpy.ops.object.light_add(type="POINT", location=(u, 0, 2.8))
        lt = no_cam(bpy.context.object)
        lt.data.energy = 45
        lt.data.color = (1.0, 0.82, 0.6)
        lt.data.shadow_soft_size = 0.5
        parts.append(lt)
        lights.append(lt)
    for u in (3.0, 6.5):                       # light spilling out of the windows onto the road (keyed in build)
        bpy.ops.object.light_add(type="POINT", location=(u, BUS_HW + 2.0, 2.0))
        sp = no_cam(bpy.context.object)
        sp.name = "Bus spill"
        sp.data.energy = 0
        sp.data.color = (0.85, 0.88, 1.0)
        sp.data.shadow_soft_size = 1.0
        parts.append(sp)
        lights.append(sp)
    bpy.ops.object.light_add(type="SPOT", location=(-0.1, 0, 0.9), rotation=(0, D(90), 0))
    beam = bpy.context.object
    beam.data.energy = 0
    beam.data.spot_size = D(60)
    beam.data.color = (1.0, 0.95, 0.85)
    parts.append(beam)
    # bus local axes = world axes (its front at u = 0 points to -X, the way it drives); BUS is keyed along X
    for p in parts:
        if p.parent is None:
            p.parent = root
            p.matrix_parent_inverse = root.matrix_world.inverted()
    return root, leaves, lights, beam


def puppet_mask(p, kind="resp"):
    """a mask over nose and mouth on the head pivot (no logos)."""
    R, hc, head = p.R, p.head_c, p.p["head"]
    m = toon("Respirator", (0.16, 0.18, 0.2), 0.05) if kind == "resp" else toon("Dust mask", (0.9, 0.93, 0.95), 0.25)
    flt = toon("Respirator filter", (0.42, 0.48, 0.32), 0.12)
    objs = [p.add(ball(hc + Vector((0, 0.8 * R, -0.36 * R)), 0.5 * R, m, "mask cup", scale=(1.12, 0.78, 0.98)), head)]
    if kind == "resp":
        for sx in (-1, 1):
            o = rod(hc + Vector((sx * 0.36 * R, 0.98 * R, -0.5 * R)), hc + Vector((sx * 0.44 * R, 1.16 * R, -0.62 * R)),
                    0.16 * R, flt, "mask filter")
            objs.append(p.add(o, head))
        objs.append(p.add(rod(hc + Vector((0, 1.15 * R, -0.45 * R)), hc + Vector((0, 1.26 * R, -0.5 * R)), 0.1 * R,
                              flt, "mask valve"), head))
    bpy.ops.mesh.primitive_torus_add(location=hc + Vector((0, 0.05 * R, -0.12 * R)), major_radius=1.0 * R,
                                     minor_radius=0.05 * R, major_segments=28, minor_segments=6)
    st = finish(bpy.context.object, toon("Mask strap", (0.15, 0.15, 0.16), 0.05), "mask strap", True)
    st.rotation_euler = (D(-15), 0, 0)
    objs.append(p.add(st, head))
    return objs


def make_rescuer():
    """the rescuer: orange protective suit with a hood, grey gloves and boots, a respirator, a radio."""
    p = Person("Rescuer", 1.05, 0.21, dict(skin=(0.78, 0.56, 0.42), top=(0.95, 0.45, 0.1), pants=(0.95, 0.45, 0.1),
                                            shoes=(0.2, 0.2, 0.22), hair=(0.1, 0.08, 0.07), iris=(0.25, 0.15, 0.08),
                                            brow=1.3, lid=0.25, gloves=(0.35, 0.37, 0.38), belt=(0.2, 0.2, 0.22),
                                            width=1.08))
    R, hc, head = p.R, p.head_c, p.p["head"]
    hood = toon("Rescuer top", (0.95, 0.45, 0.1))
    p.add(ball(hc + Vector((0, -0.12 * R, 0.08 * R)), 1.12 * R, hood, "hood", scale=(1.05, 1.0, 1.08)), head)
    p.add(box((0, 0.17, 0.86 * p.s + 0.29 * p.s), (0.5, 0.02, 0.06), toon("Reflective", (0.92, 0.92, 0.92), 0.6),
              "suit stripe"), p.p["torso"])
    puppet_mask(p, "resp")
    return p


def make_oldman():
    """the old man on the bus: bald on top, white side hair and a short white beard, round glasses, brown cardigan."""
    L = dict(skin=(0.86, 0.66, 0.53), top=(0.5, 0.35, 0.22), pants=(0.3, 0.3, 0.33), shoes=(0.25, 0.15, 0.1),
             hair=(0.92, 0.92, 0.9), brow=1.3, brow_col=(0.93, 0.93, 0.9), iris=(0.3, 0.35, 0.45), lid=0.5,
             buttons=(0.85, 0.75, 0.5), nose=(1.25, 1.2, 1.2), width=1.0)
    p = Person("Old man", 0.95, 0.21, L)
    R, hc, head = p.R, p.head_c, p.p["head"]
    white = toon("Old man hair", L["hair"])
    for sx in (-1, 1):
        p.add(ball(hc + Vector((sx * 0.82 * R, -0.3 * R, 0.0)), 0.34 * R, white, "side hair"), head)
    p.add(ball(hc + Vector((0, 0.55 * R, -0.85 * R)), 0.42 * R, white, "beard", scale=(1.2, 0.8, 0.8)), head)
    glasses(p, (0.7, 0.55, 0.2))
    return p


def show_at(objs, spans):
    """objs visible only inside the (t0, t1) spans (scale trick, as in episodes 1-2): keyed on the frame before
    and on the frame of every change, so nothing grows or shrinks in between."""
    for o in objs:
        prev = None
        for f in range(1, N + 2):
            t = (f - 1) / FPS
            vis = any(a <= t < b for a, b in spans)
            if vis != prev:
                if prev is not None:
                    o.scale = (1, 1, 1) if prev else (0.001, 0.001, 0.001)
                    o.keyframe_insert("scale", frame=f - 1)
                o.scale = (1, 1, 1) if vis else (0.001, 0.001, 0.001)
                o.keyframe_insert("scale", frame=f)
                prev = vis


def make_dog(i):
    rnd = random.Random(30 + i)
    fur = toon(f"Dog fur {i % 3}", [(0.2, 0.18, 0.16), (0.3, 0.25, 0.2), (0.15, 0.14, 0.14)][i % 3], 0.05)
    eye = glow_mat("Dog eyes", (1.0, 0.8, 0.2), 8.0)
    tooth = toon("Dog teeth", (0.95, 0.93, 0.85), 0.3)
    root = empty(f"Dog{i}")
    body = ball((0, 0, 0.55), 0.32, fur, "Dog body", scale=(1.6, 0.75, 0.75))
    head = ball((0.55, 0, 0.75), 0.18, fur, "Dog head", scale=(1.2, 0.95, 0.9))
    snout = ball((0.74, 0, 0.7), 0.09, fur, "Dog snout", scale=(1.4, 0.9, 0.7))
    parts = [body, head, snout]
    for dy in (-0.07, 0.07):
        parts.append(ball((0.66, dy, 0.8), 0.045, eye, "Dog eye", seg=8))
        e = bpy.ops.mesh.primitive_cone_add(radius1=0.06, depth=0.14, location=(0.5, dy * 1.3, 0.92), vertices=8)
        parts.append(finish(bpy.context.object, fur, "Dog ear"))
        bpy.ops.mesh.primitive_cone_add(radius1=0.015, depth=0.05, location=(0.8, dy * 0.6, 0.64),
                                        rotation=(D(180), 0, 0), vertices=6)
        parts.append(finish(bpy.context.object, tooth, "Dog tooth"))
    for o in parts:
        parent_keep(o, root)
    legs = []
    for lx in (0.32, -0.32):
        for ly in (-0.13, 0.13):
            piv = empty(f"Dog{i} leg", (lx, ly, 0.5))
            parent_keep(piv, root)
            leg = rod((lx, ly, 0.5), (lx, ly, 0.03), 0.05, fur, "Dog leg")
            parent_keep(leg, piv)
            piv.rotation_mode = "XYZ"
            legs.append((piv, lx, ly))
    tail = rod((-0.5, 0, 0.62), (-0.8, 0, 0.75), 0.03, fur, "Dog tail")
    parent_keep(tail, root)
    root.rotation_mode = "XYZ"
    root.scale = (1.35, 1.35, 1.35)
    return root, legs, rnd.uniform(0, 6.28)


def make_beast():
    """Tall hunched beast: black shaggy fur, long arms with claws reaching the ground, glowing white eyes,
    a wide mouth glowing red inside with rows of teeth. Faces +X (towards the bus). ~2.6 m tall."""
    fur = toon("Beast fur", (0.025, 0.02, 0.025), 0.0)
    claw_m = toon("Beast claws", (0.12, 0.1, 0.09), 0.05)
    eye_m = glow_mat("Beast eyes", (1.0, 0.97, 0.92), 60.0)
    mouth_m = glow_mat("Beast mouth", (1.0, 0.08, 0.04), 18.0)
    tooth_m = toon("Beast teeth", (0.92, 0.88, 0.8), 0.25)
    root = empty("Beast")
    parts = []
    torso = ball((0, 0, 1.55), 0.62, fur, "Beast torso", scale=(1.0, 1.15, 1.25))
    torso.rotation_euler = (0, D(35), 0)                     # hunched forward
    belly = ball((0.05, 0, 1.05), 0.48, fur, "Beast hips", scale=(0.95, 1.05, 0.9))
    head_piv = empty("Beast head pivot", (0.55, 0, 2.05))
    head = ball((0.78, 0, 2.05), 0.36, fur, "Beast head", scale=(1.05, 1.0, 0.95))
    jaw = ball((0.92, 0, 1.86), 0.27, fur, "Beast jaw", scale=(1.0, 1.05, 0.55))
    mouth = ball((1.06, 0, 1.95), 0.25, mouth_m, "Beast mouth", scale=(0.45, 1.35, 0.62))
    hp = [head, jaw, mouth]
    for dy in (-0.15, 0.15):
        hp.append(ball((1.07, dy, 2.16), 0.055, eye_m, "Beast eye", seg=10))
        bpy.ops.mesh.primitive_cone_add(radius1=0.1, depth=0.35, location=(0.62, dy * 1.5, 2.36),
                                        rotation=(D(-25 if dy < 0 else 25), D(-25), 0), vertices=8)
        hp.append(finish(bpy.context.object, fur, "Beast ear"))
    for k in range(9):                                        # teeth, upper and lower rows
        y = -0.2 + 0.05 * k
        for z, rot in ((2.03, 180), (1.87, 0)):
            bpy.ops.mesh.primitive_cone_add(radius1=0.018, depth=0.09, location=(1.12, y, z),
                                            rotation=(D(rot), 0, 0), vertices=6)
            hp.append(finish(bpy.context.object, tooth_m, "Beast tooth"))
    for o in hp:
        parent_keep(o, head_piv)
    parent_keep(head_piv, root)
    rnd = random.Random(77)
    for _ in range(90):                                       # shaggy tufts over back and shoulders
        a, b = rnd.uniform(-1.2, 1.2), rnd.uniform(-0.2, 1.4)
        c = Vector((0.6 * math.cos(b) * 0.8 - 0.1, 0.7 * math.sin(a), 1.4 + 0.6 * math.sin(b)))
        bpy.ops.mesh.primitive_cone_add(radius1=0.1, depth=0.42, location=c, vertices=6,
                                        rotation=(rnd.uniform(-0.6, 0.6), D(-60) + rnd.uniform(-0.4, 0.4), 0))
        parts.append(finish(bpy.context.object, fur, "Beast tuft"))
    parts += [torso, belly]
    for o in parts:
        parent_keep(o, root)
    limbs = []
    for side in (-1, 1):                                      # long arms reaching to the ground, claws
        sh = empty("Beast shoulder", (0.45, side * 0.62, 1.85))
        parent_keep(sh, root)
        up = rod((0.45, side * 0.62, 1.85), (0.75, side * 0.78, 1.0), 0.12, fur, "Beast arm")
        lo = rod((0.75, side * 0.78, 1.0), (0.95, side * 0.8, 0.12), 0.1, fur, "Beast forearm")
        hand = ball((1.0, side * 0.8, 0.1), 0.14, fur, "Beast hand", scale=(1.3, 1.1, 0.5))
        for o in (up, lo, hand):
            parent_keep(o, sh)
        for q in range(9):                                    # shaggy fur hanging off the arm
            u_ = q / 8
            c = Vector((0.45 + 0.4 * u_, side * (0.62 + 0.2 * u_ + 0.08), 1.85 - 1.3 * u_))
            bpy.ops.mesh.primitive_cone_add(radius1=0.09, depth=0.34, location=c, vertices=6,
                                            rotation=(D(side * 70) + rnd.uniform(-0.3, 0.3), D(20), 0))
            parent_keep(finish(bpy.context.object, fur, "Beast arm tuft"), sh)
        for c in range(4):
            bpy.ops.mesh.primitive_cone_add(radius1=0.03, depth=0.26, location=(1.18, side * (0.68 + 0.08 * c), 0.07),
                                            rotation=(0, D(100), 0), vertices=6)
            parent_keep(finish(bpy.context.object, claw_m, "Beast claw"), sh)
        sh.rotation_mode = "XYZ"
        hip = empty("Beast hip", (-0.05, side * 0.35, 0.95))
        parent_keep(hip, root)
        th = rod((-0.05, side * 0.35, 0.95), (0.25, side * 0.4, 0.5), 0.15, fur, "Beast thigh")
        sn = rod((0.25, side * 0.4, 0.5), (-0.05, side * 0.4, 0.08), 0.11, fur, "Beast shin")
        ft = ball((0.08, side * 0.4, 0.06), 0.13, fur, "Beast foot", scale=(1.6, 0.9, 0.45))
        for o in (th, sn, ft):
            parent_keep(o, hip)
        hip.rotation_mode = "XYZ"
        limbs.append((sh, hip, side))
    bpy.ops.object.light_add(type="POINT", location=(1.3, 0, 2.0))      # red glow from the mouth and eyes
    glow = bpy.context.object
    glow.data.energy = 60
    glow.data.color = (1.0, 0.12, 0.06)
    glow.data.shadow_soft_size = 0.3
    parent_keep(glow, root)
    root.rotation_mode = "XYZ"
    root.scale = (1.25, 1.25, 1.25)
    head_piv.rotation_mode = "XYZ"
    return root, head_piv, limbs, glow
