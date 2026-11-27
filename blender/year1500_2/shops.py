"""Shops along the arcade of «سال ۱۵۰۰» (part 2): every shop is open, lit, full of food — and empty of people.
The solid arcade walls of city.py are rebuilt with openings; behind each opening a small shop (shelves, boxes, cans,
bottles, fruit crates, bread). One shop is the hero shop (bread in a crate for Kian, a can on the shelf for me,
a loudspeaker with a light). One opening in the south wall is a house door (a real hinged door).
    import shops; S = shops.build(city.M)  -> dict(HERO=..., BREAD=obj, CAN=obj, SPEAKER=obj, LED=mat, DOOR=obj, ...)
"""
import bpy, bmesh, math, random
from mathutils import Vector, Matrix
import props as P
import city

R = random.Random(21)
WALL_Y, DEPTH, H_OPEN, W_OPEN = 6.5, 4.0, 3.0, 2.2
NORTH = [-22.5, -16.5, -10.5, -4.5, 4.5, 10.5, 16.5, 22.5]
SOUTH = [-25.5, -13.5, -7.5, -1.5, 7.5, 13.5, 19.5]
HERO = (4.5, 1)                    # x, side (+1 north)
HOUSE = (-19.5, -1)
FOOD = {}


def mats():
    FOOD.update(
        wood=P.mat("Shelf wood", (0.62, 0.42, 0.26), 0.7), floor=P.mat("Shop floor", (0.85, 0.82, 0.76), 0.5),
        inner=P.mat("Shop wall", (0.95, 0.9, 0.8), 0.8), sign=P.mat("Shop sign", (0.95, 0.55, 0.2), 0.6),
        red=P.mat("Pack red", (0.85, 0.15, 0.12), 0.5), yellow=P.mat("Pack yellow", (0.98, 0.8, 0.15), 0.5),
        blue=P.mat("Pack blue", (0.15, 0.4, 0.85), 0.5), green=P.mat("Pack green", (0.2, 0.7, 0.3), 0.5),
        orange=P.mat("Pack orange", (0.98, 0.5, 0.1), 0.5), tin=P.mat("Tin", (0.75, 0.76, 0.78), 0.3, metal=0.6),
        water=P.mat("Bottle water", (0.6, 0.85, 1.0), 0.15), apple=P.mat("Apple", (0.85, 0.08, 0.08), 0.4),
        orangef=P.mat("Orange fruit", (1.0, 0.55, 0.05), 0.5), bread=P.mat("Bread", (0.78, 0.5, 0.22), 0.8),
        door=P.mat("House door", (0.45, 0.25, 0.14), 0.6), dark=P.mat("House dark", (0.05, 0.05, 0.06), 0.9),
        speaker=P.mat("Speaker", (0.12, 0.12, 0.13), 0.5), glassdoor=P.mat("Shop door glass", (0.7, 0.85, 0.95), 0.1),
    )
    FOOD["led"] = P.emit("Speaker light", (1.0, 0.15, 0.1), 1.0)


def walls(M):
    """Replace the solid arcade walls and the fake doors with walls that have real openings."""
    for o in [o for o in bpy.data.objects if o.name.startswith(("Arcade wall", "Arcade door"))]:
        bpy.data.objects.remove(o, do_unlink=True)
    x0, x1, h = -30.0, 30.0, 4.0
    for side, xs in ((1, NORTH), (-1, SOUTH)):
        y = side * WALL_Y
        bm = bmesh.new()
        cuts = sorted(xs)
        a = x0
        for cx in cuts:
            w = 1.2 if (cx, side) == HOUSE else W_OPEN
            hh = 2.25 if (cx, side) == HOUSE else H_OPEN
            city.cube(bm, ((a + cx - w / 2) / 2, y, h / 2), (cx - w / 2 - a, 0.6, h))
            city.cube(bm, (cx, y, (hh + h) / 2), (w, 0.6, h - hh))                 # lintel
            a = cx + w / 2
        city.cube(bm, ((a + x1) / 2, y, h / 2), (x1 - a, 0.6, h))
        city.INK.append(city.link("Arcade wall open", bm, [M["wall"]]))


def shop(bm, cx, side, hero=False):
    """One small shop behind the opening at x=cx (side +1 north, -1 south). Food goes into bm[material]."""
    s = side
    y0, y1 = s * (WALL_Y + 0.3), s * (WALL_Y + 0.3 + DEPTH)
    yc = (y0 + y1) / 2
    w = 5.2
    city.cube(bm["floor"], (cx, yc, 0.02), (w, DEPTH, 0.04))
    city.cube(bm["inner"], (cx, y1 + s * 0.05, 1.8), (w, 0.1, 3.6))
    for dx in (-w / 2, w / 2):
        city.cube(bm["inner"], (cx + dx, yc, 1.8), (0.1, DEPTH, 3.6))
    city.cube(bm["inner"], (cx, yc, 3.6), (w, DEPTH, 0.1))
    city.cube(bm["sign"], (cx, s * (WALL_Y - 0.32), 3.45), (2.4, 0.06, 0.5))          # a plain sign, no letters
    # back shelves: 4 boards, full of packs, cans, bottles
    for k, z in enumerate((0.35, 0.8, 1.25, 1.7)):
        yb = y1 - s * 0.25
        city.cube(bm["wood"], (cx, yb, z), (w - 0.4, 0.45, 0.04))
        x = cx - w / 2 + 0.35
        while x < cx + w / 2 - 0.35:
            kind = R.random()
            if kind < 0.45:
                m = R.choice(("red", "yellow", "blue", "green", "orange"))
                hh = R.uniform(0.2, 0.3)
                city.cube(bm[m], (x, yb, z + 0.02 + hh / 2), (0.16, 0.08, hh))
                x += 0.19
            elif kind < 0.75:
                for j in range(2):
                    bmesh.ops.create_cone(bm["tin"], cap_ends=True, segments=10, radius1=0.045, radius2=0.045, depth=0.11,
                                          matrix=Matrix.Translation((x, yb + s * (j * 0.1 - 0.05), z + 0.075)))
                x += 0.11
            else:
                bmesh.ops.create_cone(bm["water"], cap_ends=True, segments=10, radius1=0.038, radius2=0.038, depth=0.26,
                                      matrix=Matrix.Translation((x, yb, z + 0.15)))
                x += 0.09
    # side shelves (two boards each side)
    for dx in (-w / 2 + 0.3, w / 2 - 0.3):
        for z in (0.5, 1.1):
            city.cube(bm["wood"], (cx + dx, yc + s * 0.4, z), (0.45, DEPTH - 1.6, 0.04))
            for j in range(9):
                m = R.choice(("red", "yellow", "blue", "green", "orange", "tin"))
                city.cube(bm[m], (cx + dx, yc + s * (0.4 - 1.0 + j * 0.24), z + 0.13), (0.12, 0.17, 0.22))
    # fruit crates on the floor by the door
    for dx in (-1.6, 1.6):
        cc = Vector((cx + dx, y0 + s * 0.8, 0.2))
        city.cube(bm["wood"], cc, (0.7, 0.5, 0.36))
        fm = "apple" if dx < 0 else "orangef"
        for i in range(10):
            p = cc + Vector((R.uniform(-0.27, 0.27), R.uniform(-0.17, 0.17), 0.2 + R.uniform(0, 0.05)))
            bmesh.ops.create_uvsphere(bm[fm], u_segments=10, v_segments=7, radius=0.06, matrix=Matrix.Translation(p))
    if not hero:                                     # a bread crate in every shop (the hero one gets a real loaf)
        cc = Vector((cx, y1 - s * 0.9, 0.18))
        city.cube(bm["wood"], cc, (0.6, 0.4, 0.3))
        for i in range(4):
            bmesh.ops.create_uvsphere(bm["bread"], u_segments=10, v_segments=7, radius=0.1,
                                      matrix=Matrix.Translation(cc + Vector((-0.2 + i * 0.13, 0, 0.17)))
                                      @ Matrix.Diagonal((0.6, 1.6, 0.55, 1)))
    # the glass door swung open against the inside wall
    bmesh.ops.create_cube(bm["glassdoor"], size=1, matrix=Matrix.Translation((cx - W_OPEN / 2 + 0.05, s * (WALL_Y + 0.75), 1.3))
                          @ Matrix.Diagonal((0.04, 0.9, 2.5, 1)))


def build(M):
    mats()
    walls(M)
    bm = {k: bmesh.new() for k in FOOD if k not in ("led", "door", "dark", "speaker")}
    lights = []
    for side, xs in ((1, NORTH), (-1, SOUTH)):
        for cx in xs:
            if (cx, side) == HOUSE:
                continue
            shop(bm, cx, side, hero=(cx, side) == HERO)
            yc = side * (WALL_Y + 0.3 + DEPTH / 2)
            l = bpy.data.objects.new(f"Shop light {cx}", bpy.data.lights.new(f"Shop light {cx}", "POINT"))
            bpy.context.scene.collection.objects.link(l)
            l.location = (cx, yc, 3.0)
            l.data.energy, l.data.color, l.data.use_shadow = 180, (1.0, 0.86, 0.65), False
            l.data.shadow_soft_size = 0.8
            lights.append(l)
    for k, b in bm.items():
        city.link("Shop " + k, b, [FOOD[k]])
    out = dict(LIGHTS=lights)
    # ---- hero shop
    hx, s = HERO
    y1 = s * (WALL_Y + 0.3 + DEPTH)
    crate = Vector((hx - 0.9, y1 - s * 1.1, 0.18))
    P.box(tuple(crate), (0.6, 0.4, 0.3), FOOD["wood"], "Hero bread crate")
    for i in range(3):
        P.sphere(tuple(crate + Vector((-0.2 + i * 0.2, 0, 0.17))), 0.1, FOOD["bread"], "Hero crate loaf",
                 scale=(0.6, 1.6, 0.55))
    out["BREAD"] = P.sphere(tuple(crate + Vector((0.0, 0.05, 0.3))), 0.1, FOOD["bread"], "Kian bread", scale=(0.6, 1.8, 0.6))
    can_p = Vector((hx + 0.9, y1 - s * 0.25, 1.25 + 0.02 + 0.06))         # on the 3rd board, front edge
    out["CAN"] = P.cyl(tuple(can_p - Vector((0, 0, 0.055))), tuple(can_p + Vector((0, 0, 0.055))), 0.045, FOOD["red"], "My can")
    out["CAN_AT"] = can_p
    out["CRATE"] = crate
    sp = Vector((hx - 2.45, s * (WALL_Y + 1.4), 3.1))                    # loudspeaker high on the left wall
    out["SPEAKER"] = P.box(tuple(sp), (0.12, 0.34, 0.24), FOOD["speaker"], "Speaker")
    P.cyl(tuple(sp + Vector((0.07, 0, 0))), tuple(sp + Vector((0.075, 0, 0))), 0.09, FOOD["tin"], "Speaker grille")
    out["LED"] = P.sphere(tuple(sp + Vector((0.07, 0.13, -0.08))), 0.018, FOOD["led"], "Speaker light")
    out["SPEAKER_AT"] = sp
    out["HERO_LIGHT"] = [l for l in lights if l.name == f"Shop light {hx}"][0]
    # ---- the house door (south wall): a dark room behind, a wooden door hinged on its left edge
    dx, s2 = HOUSE
    y = s2 * WALL_Y
    rb = bmesh.new()                                   # a hollow dark room, so the door can swing into it
    ry = s2 * (WALL_Y + 0.3 + 1.8)
    city.cube(rb, (dx, s2 * (WALL_Y + 0.3 + 3.6), 1.5), (3.0, 0.1, 3.0))
    for ex in (-1.5, 1.5):
        city.cube(rb, (dx + ex, ry, 1.5), (0.1, 3.6, 3.0))
    city.cube(rb, (dx, ry, 3.0), (3.0, 3.6, 0.1))
    city.cube(rb, (dx, ry, 0.0), (3.0, 3.6, 0.04))
    city.link("House room", rb, [FOOD["dark"]])
    hinge = bpy.data.objects.new("House door hinge", None)
    bpy.context.scene.collection.objects.link(hinge)
    hinge.location = (dx + 0.55, y + s2 * 0.05, 0)
    door = P.box((0, 0, 0), (1.08, 0.06, 2.2), FOOD["door"], "House door")
    door.parent = hinge
    door.location = (-0.54, 0, 1.1)
    handle = P.sphere((0, 0, 0), 0.035, FOOD["tin"], "House door handle")
    handle.parent = door
    handle.location = (-0.42, -s2 * 0.06, -0.08)
    out.update(DOOR=door, HINGE=hinge, HANDLE=handle, HOUSE_AT=Vector((dx, y, 0)))
    return out
