"""
«پناهگاه ۳ — اتوبوس نجات» in the series' own form: vertical, through «من»'s eyes (green sleeves), with the
characters of episodes 1-2 (Lena with the red beanie and her bunny, Mom in the plum coat and teal scarf, the
guard in orange with the hard hat) plus the new ones built the same way (the rescuer in an orange suit, the old
man, the passengers).  Soft cinematic shading (pcommon.toon), no outlines.  The air is still radioactive, so
everyone on the bus wears a mask (we put ours on when we board).

Story beats follow times.py (the ElevenLabs lines) and the event times written to out/events.json.
Rendered on twos (odd frames); post.py doubles them.

    ../cast/bpy.sh pov.py --still 100,700        (global frame numbers)
    ../cast/bpy.sh pov.py --save                 (pov.blend for render.py / chain.sh)
"""
import json
import math
import os
import random
import sys

import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from pcommon import *  # noqa: F401,F403,E402
from pcommon import REST  # noqa: E402
from captions import END, KEY_OF  # noqa: E402

random.seed(8)
T = KEY_OF
N = int(END * FPS)
WIDE = os.environ.get("WIDE", "") == "1"      # 16:9 long-form version (1280x720)


def at(key, k=0):
    return T[key][k]


def yaw_to(d):
    return math.degrees(math.atan2(-d.x, d.y)) % 360


def pitch_to(d):
    return math.degrees(math.atan2(d.z, d.xy.length))


def look(pos, target):
    d = Vector(target) - pos
    return yaw_to(d), pitch_to(d)


def lerp_yaw(a, b, u):
    d = (b - a + 180) % 360 - 180
    return a + d * u


def mix(a, b, u):
    return tuple(x + (y - x) * u for x, y in zip(a, b))


# ================================================================== story times
T_LOUD = at("resc1") - 1.4
T_GREEN = at("guard3") - 0.3                 # «چراغ سبزه...»
T_DOOR = at("me2", 1) + 0.2                  # the steel door grinds open
T_OUT = at("n3") - 0.4                       # we step out into the fog
T_IN = at("old1") - 0.6                      # inside the bus
T_GO = at("resc4", 1) - 1.0                  # doors shut, the bus pulls away
T_DUSK0, T_DUSK1 = at("old2"), at("radio1")
T_FOREST = at("n5") - 0.4
T_EYES = at("lena5") - 0.8
T_DOGS = at("resc6") - 2.0
T_BANG = at("resc7") - 1.4
T_STOP = at("n6") - 0.2
T_LIGHTS = at("n7") + 2.2
T_ARRIVE = (at("resc2") - 1.2, at("resc2") + 3.0)   # the bus rolls in and stops outside the door
EV = {"T_BANG": T_BANG, "T_LOUD": T_LOUD, "T_GO": T_GO, "T_DOOR": T_DOOR, "T_DOGS": T_DOGS, "T_STOP": T_STOP,
      "T_ARRIVE": list(T_ARRIVE), "T_FOREST": T_FOREST, "T_LIGHTS": T_LIGHTS, "T_IN": T_IN, "T_OUT": T_OUT}
os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
json.dump(EV, open(os.path.join(HERE, "out", "events.json"), "w"), indent=1)   # el_mix.py reads the same times

# ================================================================== layout
# The bunker (episodes 1-2): door in its front wall at y = DOOR_Y facing -Y, the room behind it (+Y).
BX, DOOR_Y = 0.0, 0.0
EYE = 1.55
ROAD_Y = DOOR_Y - 9.0                        # the road runs along X in front of the bunker
# The bus drives towards -X with its door side (+Y) to the bunker.  Bus local: u = metres back from the front,
# v = metres to the right (+Y in the world), z = up from the ground.
BUS_X0 = BX + 6.0                            # world x of the bus front while it waits
BUS_Y = ROAD_Y + 2.0                         # centre line of the bus
BUS_LEN, BUS_HW, FLOOR = 11.0, 1.25, 0.9


def travelled(t):
    """metres the bus has driven by time t (it accelerates, cruises, speeds up from the dogs, stops)."""
    def v(tt):
        if tt < T_GO:
            return 0.0
        u = min(1.0, (tt - T_GO) / 5.0)
        vv = 11.0 * u * u * (3 - 2 * u)
        if tt > T_DOGS + 0.5:
            vv += 4.0 * seg(tt, T_DOGS + 0.5, T_DOGS + 2.5)
        if tt > T_BANG:
            vv *= max(0.0, 1 - (tt - T_BANG) / (T_STOP - T_BANG))
        return vv
    d, tt, dt = 0.0, T_GO, 1 / 48
    while tt < min(t, T_STOP):
        d += v(tt) * dt
        tt += dt
    return d


DIST = [travelled((f - 1) / FPS) for f in range(N + 2)]


def dist(t):
    f = max(0, min(N, int(t * FPS)))
    return DIST[f]


def bus_origin(t):
    """world position of bus-local (0, 0, 0) at time t (+ a swerve after the burst)."""
    sw = 0.0
    if T_BANG < t < T_STOP + 0.5:
        sw = 0.6 * math.sin((t - T_BANG) * 5.0) * (1 - seg(t, T_BANG, T_STOP))
    a0, a1 = EV["T_ARRIVE"]
    arrive = 60.0 * (1 - seg(t, a0 - 6, a1))          # it drives in from +X and stops by the bunker
    return Vector((BUS_X0 - dist(t) + arrive, BUS_Y + sw, 0.0))


def W(t, u, v, z):
    """bus-local -> world at time t (local u = back from the front = world +X, v = world +Y)"""
    return bus_origin(t) + Vector((u, v, z))


X_STOP = BUS_X0 - dist(T_STOP)
X_FOREST = BUS_X0 - dist(T_FOREST) - 30.0     # where the trees start
X_CITY_END = X_FOREST + 60.0
X_SCHOOL = BUS_X0 - dist(at("mom3") + 0.4) - 4.0


# ================================================================== the world
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


def dead_city():
    """grey, burnt-out blocks along both sides of the road, the cars left where they stopped."""
    cols = [(0.55, 0.52, 0.5), (0.47, 0.46, 0.5), (0.6, 0.56, 0.5), (0.44, 0.47, 0.5), (0.52, 0.47, 0.44)]
    dark = toon("Dark window", (0.07, 0.07, 0.08), 0.0)
    soot = toon("Soot", (0.16, 0.15, 0.14), 0.02)
    rnd = random.Random(4)
    for sy in (-1, 1):
        x = BX - 14 if sy > 0 else BX + 30
        while x > X_CITY_END:
            w = rnd.uniform(9, 16)
            h = rnd.uniform(8, 26) if sy < 0 or x < BX - 30 else rnd.uniform(6, 12)
            if sy > 0 and abs((x - w / 2) - X_SCHOOL) < 18:     # the school's yard on our side
                x -= w
                continue
            y = ROAD_Y + sy * (12 + rnd.uniform(0, 3))
            box((x - w / 2, y, h / 2), (w - 0.8, 9, h), toon(f"Building {len(cols)}", rnd.choice(cols), 0.1),
                "Building")
            if rnd.random() < 0.4:                                  # a collapsed corner
                box((x - w * 0.3, y - sy * 4.6, 0.6), (w * 0.4, 2.5, 1.2), toon("Rubble", (0.4, 0.38, 0.35), 0.08),
                    "Rubble", bevel=0.2)
            for fl in range(int(h // 3.2)):
                box((x - w / 2, y - sy * 4.52, 1.8 + fl * 3.2), (w - 2.4, 0.05, 1.3),
                    soot if rnd.random() < 0.15 else dark, "Window band")
            x -= w
    # abandoned cars, doors open, on the road edges
    car_c = [(0.55, 0.2, 0.2), (0.25, 0.32, 0.5), (0.7, 0.68, 0.64), (0.25, 0.25, 0.27), (0.6, 0.48, 0.2)]
    for k in range(14):
        cx = BX - 40 - k * (abs(X_CITY_END - BX) / 15) + rnd.uniform(-5, 5)
        cy = ROAD_Y + rnd.choice((-1, 1)) * 3.3
        m = toon(f"Car {k}", car_c[k % 5], 0.1)
        root = empty(f"Car{k}", (cx, cy, 0))
        parts = [box((cx, cy, 0.55), (4.2, 1.8, 0.7), m, "Car body", bevel=0.15),
                 box((cx + 0.2, cy, 1.15), (2.2, 1.6, 0.55), m, "Car cabin", bevel=0.12),
                 box((cx + 0.2, cy, 1.15), (1.9, 1.62, 0.4), toon("Car glass", (0.12, 0.15, 0.2), 0.03), "Car glass")]
        for o in parts:
            parent_keep(o, root)
        root.rotation_euler = (0, 0, rnd.uniform(-0.3, 0.3))
    # fallen lamp posts and debris
    pole = toon("Pole", (0.3, 0.3, 0.32), 0.05)
    for k in range(16):
        x = BX - 20 - k * (abs(X_CITY_END - BX) / 17)
        y = ROAD_Y + rnd.choice((-1, 1)) * 4.6
        rod((x, y, 0), (x + rnd.uniform(-2, 2), y + rnd.uniform(-1, 1), rnd.uniform(3, 6)), 0.08, pole, "Lamp pole")
        for j in range(3):
            box((x + rnd.uniform(-6, 6), ROAD_Y + rnd.uniform(-4.5, 4.5), 0.1), (rnd.uniform(0.3, 1.2),) * 2 + (0.2,),
                toon("Debris", (0.38, 0.36, 0.33), 0.05), "Debris", bevel=0.05)


def school():
    """Our school (mom: «اون... مدرسه‌ت بود»): a long two-storey block behind a yard with a broken fence,
    a slide and a basketball hoop.  No signs, no flags."""
    x, y = X_SCHOOL, ROAD_Y + 20.0
    wall = toon("School wall", (0.78, 0.62, 0.45), 0.12)
    trim = toon("School trim", (0.35, 0.5, 0.62), 0.12)
    box((x, y, 4.0), (26, 8, 8), wall, "School")
    box((x, y - 4.05, 4.0), (26.2, 0.1, 0.35), trim, "School band")
    box((x + 13.5, y + 2.0, 3.0), (6, 6, 6.0), toon("School wall broken", (0.5, 0.42, 0.34), 0.08), "School ruin",
        bevel=0.4)
    for fl in range(2):
        for k in range(8):
            box((x - 11 + k * 3.0, y - 4.05, 1.9 + fl * 3.4), (1.6, 0.06, 1.6),
                toon("Dark window", (0.07, 0.07, 0.08), 0.0), "School window")
    yard = toon("Yard", (0.5, 0.46, 0.4), 0.08)
    box((x, ROAD_Y + 11, 0.02), (28, 13, 0.04), yard, "School yard")
    fence = toon("Fence", (0.25, 0.4, 0.3), 0.08)
    for k in range(28):
        if k in (9, 10, 17):
            continue
        tilt = 0.4 if k in (11, 12, 18) else 0.0
        o = rod((x - 14 + k, ROAD_Y + 6.5, 0), (x - 14 + k, ROAD_Y + 6.5 + tilt, 1.6), 0.03, fence, "Fence bar")
    box((x, ROAD_Y + 6.5, 1.5), (28, 0.05, 0.06), fence, "Fence rail")
    red = toon("Slide", (0.85, 0.25, 0.18), 0.15)
    s0 = Vector((x - 6, ROAD_Y + 12, 0))
    box(tuple(s0 + Vector((0, 0, 1.0))), (0.8, 0.8, 0.1), red, "Slide top")
    o = box(tuple(s0 + Vector((1.4, 0, 0.55))), (2.8, 0.6, 0.06), red, "Slide chute")
    o.rotation_euler = (0, D(22), 0)
    for dx in (-0.35, 0.35):
        rod(tuple(s0 + Vector((dx, -0.35, 0))), tuple(s0 + Vector((dx, -0.35, 1.0))), 0.04, fence, "Slide leg")
    rod((x + 6, ROAD_Y + 12, 0), (x + 6, ROAD_Y + 12, 3.0), 0.06, fence, "Hoop pole")
    box((x + 6, ROAD_Y + 11.7, 3.1), (1.2, 0.05, 0.8), toon("Board", (0.9, 0.9, 0.88), 0.2), "Hoop board")


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
        ex = BUS_X0 - dist(at("lena5") + 0.5) - 8 - k * 4.5 + rnd.uniform(-1, 1)
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


# ================================================================== the bunker (as in episodes 1-2)
def bunker():
    conc = toon("Concrete", (0.55, 0.55, 0.52), 0.12)
    inner = toon("Concrete inside", (0.48, 0.5, 0.48), 0.1)
    x0, x1, y0, y1, h = BX - 2.0, BX + 2.0, DOOR_Y, DOOR_Y + 14.0, 2.8
    box((BX, (y0 + y1) / 2, h + 0.2), (4.4, 14.4, 0.4), conc, "Bunker roof", bevel=0.05)
    box((BX, (y0 + y1) / 2, 0.02), (4.0, 14.0, 0.04), inner, "Bunker floor")
    for x in (x0, x1):
        box((x, (y0 + y1) / 2, h / 2), (0.4, 14.4, h), conc, "Bunker side")
    box((BX, y1, h / 2), (4.4, 0.4, h), conc, "Bunker back")
    for (a, b) in ((x0 - 0.2, BX - 0.7), (BX + 0.7, x1 + 0.2)):
        box(((a + b) / 2, y0, h / 2), (b - a, 0.4, h), conc, "Bunker front")
    box((BX, y0, 2.45), (1.4, 0.4, 0.7), conc, "Bunker lintel")
    yel = toon("Stripe yellow", (0.95, 0.75, 0.1), 0.3)
    blk = toon("Stripe black", (0.06, 0.06, 0.06), 0.0)
    for k in range(10):
        for sx in (-0.9, 0.9):
            box((BX + sx, y0 - 0.21, 0.15 + k * 0.23), (0.15, 0.02, 0.2), yel if k % 2 else blk, "Stripe")
    hinge = empty("Bunker door hinge", (BX + 0.7, y0 + 0.2, 0))
    steel = toon("Steel door", (0.42, 0.45, 0.48), 0.15)
    parts = [box((BX, y0 + 0.28, 1.05), (1.4, 0.16, 2.1), steel, "Bunker door", bevel=0.03)]
    for k in range(3):
        parts.append(box((BX, y0 + 0.37, 0.45 + k * 0.6), (1.2, 0.03, 0.08), steel, "Door rib"))
    bpy.ops.mesh.primitive_torus_add(location=(BX, y0 + 0.4, 1.1), rotation=(D(90), 0, 0), major_radius=0.2,
                                     minor_radius=0.03, major_segments=20, minor_segments=6)
    parts.append(finish(bpy.context.object, toon("Wheel", (0.75, 0.15, 0.1), 0.2), "Door wheel", True))
    for p in parts:
        parent_keep(p, hinge)
    hinge.rotation_mode = "XYZ"
    # inside, as the family left it in episode 2: cream paint, teal band, benches, blankets, the drawing
    xa, xb, ya, yb = BX - 1.78, BX + 1.78, DOOR_Y + 0.25, DOOR_Y + 13.8
    cream = toon("Bunker paint", (0.93, 0.86, 0.7), 0.18)
    teal = toon("Bunker band", (0.12, 0.55, 0.58), 0.18)
    stripe = toon("Bunker stripe", (0.95, 0.72, 0.15), 0.25)
    for x, s in ((xa, 1), (xb, -1)):
        box((x, (ya + yb) / 2, 1.85), (0.03, yb - ya, 1.9), cream, "Wall paint")
        box((x + s * 0.005, (ya + yb) / 2, 0.5), (0.035, yb - ya, 1.0), teal, "Wall band")
        box((x + s * 0.01, (ya + yb) / 2, 1.02), (0.04, yb - ya, 0.06), stripe, "Wall stripe")
    box((BX, yb, 1.4), (xb - xa, 0.03, 2.8), cream, "Back paint")
    box((BX, (ya + yb) / 2, 2.77), (xb - xa, yb - ya, 0.03), toon("Bunker ceiling", (0.97, 0.93, 0.82), 0.2), "Ceiling")
    box((BX, (ya + yb) / 2, 0.045), (1.2, yb - ya - 1, 0.01), toon("Runner", (0.75, 0.2, 0.22), 0.15), "Runner")
    bench = toon("Bench", (0.45, 0.33, 0.22), 0.1)
    for sx in (-1, 1):
        box((BX + sx * 1.55, (ya + yb) / 2 + 1.5, 0.45), (0.5, 9, 0.1), bench, "Bench", bevel=0.03)
    cols = [(0.85, 0.2, 0.25), (0.2, 0.45, 0.85), (0.95, 0.7, 0.12), (0.3, 0.65, 0.35), (0.6, 0.3, 0.75)]
    for k in range(9):
        sx = -1 if k % 2 else 1
        yy = DOOR_Y + 3.6 + k * 1.05
        if sx > 0 and yy < DOOR_Y + 4.5:
            continue
        box((BX + sx * 1.55, yy, 0.53), (0.45, 0.55, 0.06), toon(f"Blanket {k}", cols[k % 5], 0.2), "Blanket",
            bevel=0.02)
    for k in range(3):        # only a few bottles left: water for two days
        rod((BX - 1.2 + k * 0.45, yb - 0.3, 0.05), (BX - 1.2 + k * 0.45, yb - 0.3, 0.32), 0.05,
            toon("Bottle", (0.45, 0.75, 0.95), 0.35), "Bottle")
    dx = xb - 0.03
    box((dx, DOOR_Y + 5.0, 1.55), (0.01, 0.55, 0.42), toon("Paper", (0.98, 0.97, 0.92), 0.4), "Drawing")
    ball((dx - 0.01, DOOR_Y + 5.15, 1.68), 0.05, toon("Sun", (1.0, 0.8, 0.1), 0.5), "Drawn sun", scale=(0.2, 1, 1))
    box((dx - 0.01, DOOR_Y + 4.9, 1.45), (0.005, 0.18, 0.14), toon("Drawn house", (0.9, 0.3, 0.25), 0.4), "Drawn house")
    bulb = glow_mat("Warm bulb", (1.0, 0.75, 0.35), 4.0)
    for k in range(10):
        ball((BX + 0.6 * math.sin(k), DOOR_Y + 2.5 + k * 1.1, 2.6), 0.045, bulb, "Bulb string", seg=8)
    for yy in (DOOR_Y + 2.5, DOOR_Y + 5, DOOR_Y + 9):
        bpy.ops.object.light_add(type="POINT", location=(BX, yy, 2.0))
        lt = no_cam(bpy.context.object)
        lt.data.energy = 70
        lt.data.color = (1.0, 0.8, 0.58)
        lt.data.shadow_soft_size = 0.6
    # status lights above the door, inside and outside
    red = glow_mat("Status red", (1.0, 0.08, 0.05), 6.0)
    green = glow_mat("Status green", (0.1, 1.0, 0.25), 6.0)
    housing = toon("Lamp housing", (0.15, 0.15, 0.16), 0.05)
    reds, greens = [], []
    for side in (1, -1):
        y = DOOR_Y + side * 0.24
        box((BX, y, 2.42), (0.5, 0.1, 0.22), housing, "Status housing", bevel=0.02)
        reds.append(ball((BX - 0.11, y + side * 0.05, 2.42), 0.07, red, "Status red", scale=(1, 0.5, 1)))
        greens.append(ball((BX + 0.11, y + side * 0.05, 2.42), 0.07, green, "Status green", scale=(1, 0.5, 1)))
    bpy.ops.object.light_add(type="POINT", location=(BX, DOOR_Y + 0.6, 2.2))
    st = no_cam(bpy.context.object)
    st.data.energy = 18
    return hinge, reds, greens, st


# ================================================================== the bus
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


# ================================================================== people (episode 1-2 look)
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


def make_guard():
    """the shelter guard, exactly as in episode 2 (orange top, hard hat, reflective stripe)."""
    g = Person("Guard", 1.04, 0.2, dict(skin=(0.82, 0.6, 0.46), top=(0.95, 0.5, 0.08), pants=(0.2, 0.22, 0.28),
                                        shoes=(0.08, 0.08, 0.08), hair=(0.1, 0.07, 0.05), belt=(0.15, 0.1, 0.05),
                                        iris=(0.25, 0.18, 0.1), brow=1.4, lid=0.3, gloves=(0.2, 0.2, 0.2)))
    hat_m = toon("Hard hat", (0.95, 0.85, 0.15), 0.2)
    g.add(ball(g.head_c + Vector((0, 0, 0.45 * g.R)), 1.08 * g.R, hat_m, "hard hat", scale=(1, 1.05, 0.62)),
          g.p["head"])
    g.add(ball(g.head_c + Vector((0, 0.12 * g.R, 0.32 * g.R)), 1.28 * g.R, hat_m, "hard hat brim",
               scale=(1.0, 1.08, 0.08)), g.p["head"])
    g.add(box(g.head_c + Vector((0, 0, 0.98 * g.R)), (0.18 * g.R, 1.9 * g.R, 0.14 * g.R), hat_m, "hard hat ridge",
              bevel=0.05 * g.R), g.p["head"])
    z = 0.86 * g.s + 0.29 * g.s
    g.add(box((0, 0.17, z), (0.5, 0.02, 0.06), toon("Reflective", (0.92, 0.92, 0.92), 0.6), "vest stripe"),
          g.p["torso"])
    return g


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


# ================================================================== dogs (procedural, puppet-like)
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


# ================================================================== the creature from the wall (end of the film)
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


# ================================================================== build
def build():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.fps = FPS
    scene.frame_start, scene.frame_end = 1, N
    scene.frame_step = 2

    print("build: people + bus", flush=True)
    lena, mom, guard = make_lena(), make_mom(), make_guard()
    resc, old = make_rescuer(), make_oldman()
    pax = [make_extra(i, 0.95) for i in (0, 1, 4, 6, 2, 3)]
    masks_late = puppet_mask(lena) + puppet_mask(mom) + puppet_mask(guard)
    puppet_mask(old)
    for i, pp in enumerate(pax):
        puppet_mask(pp, "dust" if i % 2 else "resp")
    hinge, reds, greens, status = bunker()
    BUSR, leaves, bus_lights, beam = bus()
    print("build: world", flush=True)
    ground_and_road()
    school()
    heads, far_spot, far_root = far_car()
    beast = make_beast()
    dead_city()
    eyes = forest()
    print("build: animation", flush=True)
    show_at(masks_late, [(T_IN, END + 20)])
    cam = make_camera(scene)
    cam.data.lens = 17 if WIDE else 13
    arms = POVArms(cam)
    arms.reach = 1.1
    # the radio in our hands (POV) and our own mask's filters at the bottom of the view once we board
    radio_root = empty("POV radio")
    parent_local(radio_root, cam)
    rbody = box((0, 0, 0), (0.11, 0.05, 0.24), toon("Radio", (0.18, 0.2, 0.18), 0.1), "POV radio body", bevel=0.01)
    rant = rod((0.035, 0, 0.1), (0.035, 0, 0.3), 0.008, toon("Radio", (0.18, 0.2, 0.18), 0.1), "POV radio antenna")
    rled = ball((-0.03, 0.028, 0.09), 0.01, glow_mat("Radio LED", (0.2, 1.0, 0.3), 6.0), "POV radio led", seg=8)
    for o in (rbody, rant, rled):
        parent_local(o, radio_root)
    radio_root.rotation_mode = "XYZ"
    radio_root.rotation_euler = (D(-70), 0, D(10))
    radio_root.location = (0.05, -0.32, -0.42)
    radio_spans = [(0, at("lena2")), (at("radio1") - 1.0, at("resc5")), (at("radio2") - 1.0, at("me6", 1) + 0.5)]
    show_at([rbody, rant, rled], radio_spans)
    my_filters = []
    flt = toon("Respirator filter", (0.42, 0.48, 0.32), 0.12)
    for sx in (-1, 1):
        o = rod((sx * 0.2, -0.55, -0.3), (sx * 0.27, -0.62, -0.26), 0.07, flt, "POV mask filter")
        parent_local(o, cam)
        my_filters.append(o)
    show_at(my_filters, [(T_IN + 1.0, END + 20)])
    dogs = [make_dog(i) for i in range(7)]

    rnd = random.Random(3)
    shake = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(-1, 1)) for _ in range(N + 3)]

    # fixed spots
    seat_me = Vector((BX + 1.45, DOOR_Y + 3.6, 1.1))            # on the right bench, as in episode 2
    lena_seat = Vector((BX + 1.45, DOOR_Y + 4.5, 0))
    mom_seat = Vector((BX - 1.45, DOOR_Y + 4.0, 0))
    guard_spot = Vector((BX - 0.9, DOOR_Y + 1.1, 0))
    stand_door = Vector((BX - 0.05, DOOR_Y + 1.15, EYE))
    out_step = Vector((BX - 0.05, DOOR_Y - 1.2, EYE))
    bus_door_out = W(T_OUT, 1.0, BUS_HW + 1.0, 0)                  # in front of the bus door (world, before it leaves)
    # seats on the bus (local u, v); we sit by the right window in row 3
    ROW = lambda k: 3.0 + 1.05 * k                              # noqa: E731
    S_ME = (ROW(2) - 0.05, 0.8)
    S_LENA = (ROW(2), 0.38)
    S_MOM = (ROW(2), -0.55)
    S_GUARD = (ROW(3), -0.95)
    S_OLD = (ROW(1), 0.6)
    S_PAX = [(ROW(5), 0.6), (ROW(0), 0.6), (ROW(4), 0.6), (ROW(5), -0.6), (ROW(6), 0.6), (ROW(7), -0.6)]

    def sit_world(t, s, dz=0.0):
        return W(t, s[0], s[1], FLOOR - 0.05 + dz)

    boarding = [  # (who, start walking out, reach the bus door)
        ("lena", T_OUT + 0.6, at("resc3") + 1.2), ("mom", T_OUT + 0.9, at("resc3") + 1.6),
        ("guard", T_OUT + 2.0, at("resc3", 1) + 1.0)]

    for f in range(1, N + 1, 2):
        t = (f - 1) / FPS
        # ---------------- the status light: red, green from guard3
        g = t >= T_GREEN
        for o in reds:
            show([o], f, not g)
        for o in greens:
            show([o], f, g)
        status.data.color = (0.1, 1.0, 0.3) if g else (1.0, 0.1, 0.05)
        status.data.keyframe_insert("color", frame=f)
        # ---------------- the steel door: I turn the wheel (me2), it grinds open
        op = seg(t, T_DOOR, T_DOOR + 2.2)
        hinge.rotation_euler = (0, 0, D(-95) * op)
        hinge.keyframe_insert("rotation_euler", frame=f)
        # ---------------- the bus: drives in (arrive), waits, leaves
        a0, a1 = EV["T_ARRIVE"]
        arrive = 1 - seg(t, a0 - 6, a1)
        o = bus_origin(t) + Vector((60 * arrive, 0, 0))
        BUSR.location = o
        BUSR.keyframe_insert("location", frame=f)
        door_open = seg(t, a1 + 0.3, a1 + 0.9) * (1 - seg(t, T_GO - 0.8, T_GO - 0.2))
        for piv, j in leaves:
            piv.rotation_euler = (0, 0, (-1 if j == 0 else 1) * D(80) * door_open)
            piv.keyframe_insert("rotation_euler", frame=f)
        night = seg(t, T_DUSK1 - 3, T_FOREST)
        beam.data.energy = 900 * night
        beam.data.keyframe_insert("energy", frame=f)
        for lt in bus_lights:
            if lt.name.startswith("Bus spill"):
                lt.data.energy = 260 * seg(t, T_DOGS - 1, T_DOGS)
                lt.data.keyframe_insert("energy", frame=f)
        if T_LIGHTS <= t:
            far_spot.data.energy = 2500 * seg(t, T_LIGHTS, T_LIGHTS + 0.4)
        far_spot.data.keyframe_insert("energy", frame=f)
        show(heads, f, t >= T_LIGHTS)
        show(eyes, f, T_EYES <= t < T_DOGS + 1.0)

        # ---------------- camera (my eyes)
        if t < at("me2") - 0.6:
            pos = seat_me.copy()
            yaw, pitch = look(pos, (BX - 0.2, DOOR_Y + 1.5, 1.4))
            # n1/n2: look over the people; lena1: Lena; guard1: the guard; mom1: Mom; me1: the radio
            for k0, k1, tgt, dp in (("n1", "n2", (BX - 1.4, DOOR_Y + 6.0, 1.0), 0),
                                    ("lena1", "lena1", (lena_seat.x, lena_seat.y, 1.0), 0),
                                    ("guard1", "guard1", (guard_spot.x, guard_spot.y, 1.6), 0),
                                    ("mom1", "mom1", (mom_seat.x, mom_seat.y, 1.05), 0)):
                y_, p_ = look(pos, tgt)
                k = seg(t, at(k0) - 0.4, at(k0)) * (1 - seg(t, at(k1, 1), at(k1, 1) + 0.5))
                yaw = lerp_yaw(yaw, y_, k)
                pitch = lerp(pitch, p_ + dp, k)
            k = seg(t, at("me1") - 0.3, at("me1")) * (1 - seg(t, T_LOUD - 0.3, T_LOUD + 0.3))
            pitch = lerp(pitch, -42, k)
            yaw = lerp_yaw(yaw, look(pos, (BX - 0.2, DOOR_Y + 1.5, 1.4))[0] + 70, k)
            y_, p_ = look(pos, (lena_seat.x - 0.3, lena_seat.y - 0.6, 1.2))
            k = seg(t, at("lena2") - 0.3, at("lena2")) * (1 - seg(t, at("lena2", 1), at("lena2", 1) + 0.5))
            yaw = lerp_yaw(yaw, y_, k)
            pitch = lerp(pitch, p_, k)
            y_, p_ = look(pos, (mom_seat.x + 0.6, mom_seat.y - 1.0, 1.6))
            k = seg(t, at("mom2") - 0.3, at("mom2")) * (1 - seg(t, at("mom2", 1), at("mom2", 1) + 0.4))
            yaw = lerp_yaw(yaw, y_, k)
            pitch = lerp(pitch, p_, k)
        elif t < T_OUT:
            pos = seat_me.lerp(stand_door, seg(t, at("me2") - 0.6, at("me2") + 0.8))
            yaw, pitch = look(pos, (BX, DOOR_Y, 1.3))
            yo, po = look(pos, (BX - 2, DOOR_Y - 12, 1.6))
            k = seg(t, T_DOOR + 0.8, T_OUT)
            yaw = lerp_yaw(yaw, yo, k)
            pitch = lerp(pitch, po, k)
        elif t < T_IN:
            # out through the door, along the bus to its door, up the step
            p0 = stand_door.lerp(out_step, seg(t, T_OUT, T_OUT + 1.5))
            u = seg(t, T_OUT + 1.5, at("resc3") + 2.2)
            p1 = p0.lerp(Vector((bus_door_out.x + 2.6, bus_door_out.y + 1.6, EYE)), u)
            pos = p1.lerp(Vector((bus_door_out.x, bus_door_out.y - 1.4, EYE + 0.55)), seg(t, T_IN - 1.6, T_IN))
            yaw, pitch = look(pos, W(t, 0.5, 0.2, 2.0))
            yb, pb = look(pos, (bus_door_out.x - 0.9, bus_door_out.y + 0.1, 1.5))  # the rescuer by the door
            k = seg(t, at("resc3") - 0.5, at("resc3")) * (1 - seg(t, at("resc3", 1), at("resc3", 1) + 0.5))
            yaw = lerp_yaw(yaw, yb, k)
            pitch = lerp(pitch, pb, k)
            yf, pf = look(pos, (BX - 25, ROAD_Y + 8, 3))                       # n3: the grey city in the fog
            k = seg(t, at("n3"), at("n3") + 0.8) * (1 - seg(t, at("n3", 1) - 0.5, at("n3", 1)))
            yaw = lerp_yaw(yaw, yf, k)
            pitch = lerp(pitch, pf, k)
        else:
            # inside: walk down the aisle to our seat, then sit by the right window
            board = seg(t, T_IN, T_IN + 2.4)
            aisle = W(t, 1.5, 0.0, FLOOR + EYE).lerp(W(t, S_ME[0] - 0.3, 0.2, FLOOR + EYE), board)
            seated = W(t, S_ME[0], S_ME[1], FLOOR + 1.22)
            pos = aisle.lerp(seated, seg(t, T_IN + 2.2, T_IN + 3.0))
            # me5 / n6: lean to the window to see the dogs below it
            lean_w = max(seg(t, at("me5") - 0.4, at("me5")) * (1 - seg(t, at("me5", 1), at("me5", 1) + 0.5)),
                         seg(t, at("n6") - 0.4, at("n6")) * (1 - seg(t, at("n6", 1), at("n6", 1) + 0.5)))
            pos = pos.lerp(W(t, S_ME[0] - 0.2, 1.08, FLOOR + 1.45), lean_w)
            # n7: I stand up in the aisle to look through the windshield at the far lights
            pos = pos.lerp(W(t, S_ME[0] - 0.5, 0.12, FLOOR + EYE + 0.05), seg(t, at("n7") - 1.2, at("n7")))
            # ... and walk up the aisle to just behind the windshield: the beast and the car fill the glass
            pos = pos.lerp(W(t, 1.5, 0.35, FLOOR + EYE + 0.05), seg(t, at("n7") + 0.3, at("n7") + 2.6))
            fwd = W(t, -5.0, 0.0, FLOOR + 1.0)
            yaw, pitch = look(pos, fwd)
            targets = [
                ("old1", W(t, S_OLD[0], S_OLD[1], FLOOR + 1.35), 0.4),
                ("lena3", W(t, S_LENA[0], S_LENA[1] - 0.1, FLOOR + 1.05), 0.3),
                ("resc4", W(t, 1.3, -0.6, FLOOR + 1.45), 0.3),
                ("n4", W(t, S_ME[0] - 4.0, 12.0, 3.5), 0.6),
                ("mom3", W(t, S_ME[0] - 1.0, 10.0, 3.0), 0.5),
                ("me3", W(t, S_ME[0] + 3.0, 14.0, 3.0), 0.5),
                ("old2", W(t, S_OLD[0], S_OLD[1], FLOOR + 1.35), 0.4),
                ("lena4", W(t, S_LENA[0], S_LENA[1] - 0.1, FLOOR + 1.05), 0.3),
                ("mom4", W(t, S_MOM[0], S_MOM[1] + 0.3, FLOOR + 1.1), 0.3),
                ("radio1", None, 0.4), ("me4", None, 0.3),
                ("resc5", W(t, 1.3, -0.6, FLOOR + 1.45), 0.3),
                ("n5", W(t, S_ME[0] - 6.0, 8.0, 2.5), 0.6),
                ("lena5", W(t, S_ME[0] - 3.0, 9.0, 0.8), 0.4),
                ("old3", W(t, S_OLD[0], S_OLD[1], FLOOR + 1.35), 0.4),
                ("resc6", W(t, -3.0, 0.0, FLOOR + 1.0), 0.3),
                ("me5", W(t, S_ME[0] - 1.5, 4.0, 0.4), 0.3),
                ("resc7", W(t, -6.0, 0.4, FLOOR + 1.0), 0.3),
                ("mom5", W(t, S_MOM[0], S_MOM[1] + 0.4, FLOOR + 0.9), 0.3),
                ("n6", W(t, S_ME[0] - 0.4, 3.0, 2.2), 0.6),
                ("radio2", None, 0.3), ("me6", None, 0.3),
                ("n7", W(t, -60.0, 0.0, 1.4), 0.8)]
            for key, tgt, ramp in targets:
                if tgt is None:                     # look down at the radio in our hands
                    y_, p_ = yaw + 8, -40
                else:
                    y_, p_ = look(pos, tgt)
                k = seg(t, at(key) - ramp, at(key)) * (1 - seg(t, at(key, 1) + 0.2, at(key, 1) + 0.2 + ramp))
                if key == "n7":
                    k = seg(t, at(key) - ramp, at(key))
                yaw = lerp_yaw(yaw, y_, k)
                pitch = lerp(pitch, p_, k)
            # between lines, while driving: glance out of the window
            if T_GO + 2 < t < at("n4") - 0.6:
                yw, pw = look(pos, W(t, S_ME[0] - 2.0, 12.0, 2.5))
                yaw = lerp_yaw(yaw, yw, 0.6 * seg(t, T_GO + 2, T_GO + 3.5))
        amp = 0.04
        if t >= T_GO:
            amp = 0.12 + 0.25 * seg(t, T_FOREST, T_FOREST + 2)
        if T_DOGS < t < T_BANG:
            amp = 0.6
        if T_BANG <= t < T_STOP + 0.3:
            amp = 1.6 * (1 - 0.6 * seg(t, T_BANG, T_STOP))
        for tb in (T_STOP + 1.0, T_STOP + 2.1, T_STOP + 3.5, T_STOP + 4.4):    # claws / bumps on the bus
            if tb <= t < tb + 0.35:
                amp += 1.2 * (1 - (t - tb) / 0.35)
        sx_, sy_, sz_ = shake[f]
        cam.location = pos
        cam.rotation_euler = (D(90 + pitch + sx_ * amp), D(sy_ * amp * 0.6), D(yaw + sz_ * amp))
        cam.keyframe_insert("location", frame=f)
        cam.keyframe_insert("rotation_euler", frame=f)

        # ---------------- people
        def board_pos(who, t0, t1, seat, dz):
            """from the bunker door to the bus door, then inside to the seat"""
            if t < t0:
                return None
            p_door = Vector((BX - 0.05, DOOR_Y - 1.0, 0))
            p_bus = Vector((bus_door_out.x, bus_door_out.y, 0))
            if t < t1:
                return p_door.lerp(p_bus, seg(t, t0, t1)), True
            u = seg(t, t1, t1 + 2.0)
            if u < 1:
                inside = W(t, 1.4, 0.2, FLOOR - 0.05).lerp(W(t, seat[0] - 0.4, 0.0, FLOOR - 0.05), u)
                return inside, True
            return sit_world(t, seat, dz), False

        def face_bus_fwd():
            return 90.0                                     # facing -X (the bus drives to -X)

        # Lena
        bp = board_pos("lena", *boarding[0][1:], S_LENA, 0.0)
        if bp is None:
            stood = seg(t, at("lena2") - 0.2, at("lena2") + 0.3)
            lp = lena_seat.lerp(Vector((BX + 0.9, DOOR_Y + 3.2, 0)), stood)
            if t > T_DOOR:
                lp = lp.lerp(Vector((BX + 0.2, DOOR_Y + 1.6, 0)), seg(t, T_DOOR, T_OUT))
            lena.pose(f, t, lp, facing=lerp_yaw(95, 180, stood), sit=1 - stood, seat_h=0.5, lean=0,
                      look=(lerp(-60, 0, seg(t, at("lena1") - 0.3, at("lena1"))), 10), worry=1.8 - 0.8 * stood,
                      hug=0.4 * (1 - stood), run=0.6 if T_DOOR < t < T_OUT else 0.0)
        else:
            lp, walking = bp
            if walking:
                lena.pose(f, t, lp, facing=yaw_to(Vector((bus_door_out.x, bus_door_out.y, 0)) - lp) if t < boarding[0][2]
                          else 270, run=0.7, run_rate=2.0, lean=-6, worry=1.4)
            else:
                sleepy = seg(t, at("mom4"), at("mom4", 1))
                fear = seg(t, T_EYES, T_EYES + 0.5)
                down = seg(t, at("mom5"), at("mom5") + 0.6)
                lena.pose(f, t, lp, facing=face_bus_fwd() + lerp(0, -40, sleepy * (1 - fear)), sit=1, seat_h=0.5,
                          lean=0, look=(lerp(-25, 0, sleepy), lerp(5, -25, sleepy) + 20 * fear), worry=1.5 + fear,
                          hug=0.5 * sleepy + 0.5 * fear, crouch=0.6 * down,
                          reach=(150, 20) if at("lena5") < t < at("lena5", 1) else None)
        # Mom
        bp = board_pos("mom", *boarding[1][1:], S_MOM, 0.0)
        if bp is None:
            up = seg(t, at("mom2") - 0.5, at("mom2"))
            mp = mom_seat.lerp(Vector((BX - 0.7, DOOR_Y + 3.0, 0)), up)
            if t > T_DOOR:
                mp = mp.lerp(Vector((BX - 0.5, DOOR_Y + 1.6, 0)), seg(t, T_DOOR, T_OUT))
            mom.pose(f, t, mp, facing=lerp_yaw(-90, 160, up), sit=1 - up, seat_h=0.5, lean=0,
                     look=(0, 10), worry=1.6, reach=(70, 15) if at("mom1") < t < at("mom1", 1) else None,
                     run=0.5 if T_DOOR < t < T_OUT else 0.0)
        else:
            mp, walking = bp
            if walking:
                mom.pose(f, t, mp, facing=yaw_to(Vector((bus_door_out.x, bus_door_out.y, 0)) - mp)
                         if t < boarding[1][2] else 270, run=0.6, run_rate=1.8, lean=-5, worry=1.5)
            else:
                to_lena = seg(t, at("mom4") - 0.4, at("mom4"))
                pull = seg(t, at("mom5") - 0.2, at("mom5") + 0.4)
                mom.pose(f, t, mp, facing=face_bus_fwd() + lerp(0, 50, max(to_lena, pull)), sit=1, seat_h=0.5,
                         lean=0, look=(lerp(0, 30, to_lena), 0), worry=1.5 + 0.6 * pull, hug=0.6 * max(to_lena, pull),
                         reach=(lerp(40, 110, seg(t, at("mom3"), at("mom3") + 0.3) *
                                     (1 - seg(t, at("mom3", 1), at("mom3", 1) + 0.3))), -30)
                         if at("mom3") - 0.2 < t < at("mom3", 1) + 0.4 else None)
        # the guard: by the door (hand trembling), opens it with me, comes last
        bp = board_pos("guard", *boarding[2][1:], S_GUARD, 0.0)
        if bp is None:
            gp = guard_spot.lerp(Vector((BX - 1.2, DOOR_Y + 1.6, 0)), seg(t, T_DOOR - 0.5, T_DOOR + 0.5))
            tremble = 6 * math.sin(t * 31) if t < at("guard2") else 0.0
            stop_hand = seg(t, at("guard2") - 0.2, at("guard2")) * (1 - seg(t, at("guard2", 1), at("guard2", 1) + 0.4))
            guard.pose(f, t, gp, facing=lerp_yaw(150, 180, seg(t, at("guard3"), at("guard3") + 0.5)),
                       reach=(lerp(25 + tremble, 100, stop_hand), 10), look=(0, 5), worry=1.4)
        else:
            gp, walking = bp
            if walking:
                guard.pose(f, t, gp, facing=yaw_to(Vector((bus_door_out.x, bus_door_out.y, 0)) - gp)
                           if t < boarding[2][2] else 270, run=0.5, run_rate=1.6, worry=1.2)
            else:
                guard.pose(f, t, gp, facing=face_bus_fwd(), sit=1, seat_h=0.5, lean=0, look=(15, 0), worry=1.3)
        # the rescuer: outside by the bus door (waves), then the driver
        if t < T_IN + 0.4:
            rp = Vector((bus_door_out.x - 0.9, bus_door_out.y + 0.1, 0))
            if t < EV["T_ARRIVE"][1] + 0.8:
                rp = W(t, 1.3, -0.65, FLOOR - 0.05)
                resc.pose(f, t, rp, facing=face_bus_fwd(), sit=1, seat_h=0.45, lean=0, reach=(60, -5), reach2=(60, 5))
            else:
                resc.pose(f, t, rp, facing=yaw_to(Vector((BX, DOOR_Y, 0)) - rp), wave=1.0 if t < at("resc3", 1) else 0.0,
                          look=(0, 5), worry=0.6)
        else:
            rp = W(t, 1.3, -0.65, FLOOR - 0.05)
            turn = 0.0
            for key in ("resc4", "resc5"):
                turn = max(turn, seg(t, at(key) - 0.3, at(key)) * (1 - seg(t, at(key, 1), at(key, 1) + 0.4)))
            resc.pose(f, t, rp, facing=face_bus_fwd(), sit=1, seat_h=0.45, lean=0, reach=(60, -5), reach2=(60, 5),
                      look=(lerp(0, 70, turn), 0), worry=0.8 + 0.8 * seg(t, T_DOGS, T_DOGS + 1))
        # the old man (front row, turns round to talk)
        talkturn = 0.0
        for key in ("old1", "old2", "old3"):
            talkturn = max(talkturn, seg(t, at(key) - 0.4, at(key)) * (1 - seg(t, at(key, 1), at(key, 1) + 0.5)))
        old.pose(f, t, sit_world(t, S_OLD), facing=face_bus_fwd() + 150 * talkturn, sit=1, seat_h=0.5, lean=0,
                 look=(lerp(0, 20, talkturn), 0), worry=1.0)
        # passengers
        for i, (pp, s) in enumerate(zip(pax, S_PAX)):
            fear = seg(t, T_DOGS, T_DOGS + 1.0)
            pp.pose(f, t, sit_world(t, s), facing=face_bus_fwd() + 15 * math.sin(i + t * 0.3), sit=1, seat_h=0.5,
                    lean=0, look=(lerp(0, 60 * (1 if s[1] > 0 else -1), fear), lerp(-10, 0, fear)), worry=1.2 + fear,
                    hug=0.4 * fear * (i % 2), talk=False)
        # dogs: running beside the bus, at the tyres, then all round the stopped bus
        for i, (root, legs, ph) in enumerate(dogs):
            if t < T_DOGS - 0.5:
                root.location = (0, 0, -50)
            else:
                side = 1 if i % 3 else -1                 # most of them on our side
                lag = 2.0 + 1.5 * i
                v = side * (BUS_HW + 2.6 + 0.8 * (i % 3))
                du = -1.0 + 1.6 * i - lag * (1 - seg(t, T_DOGS, T_DOGS + 2.5))
                z, pitch_ = 0.0, 0.0
                if t > T_STOP:                          # all round the stopped bus, jumping up at the windows
                    du = 0.5 + 1.5 * i + 0.4 * math.sin(t * 2 + i)
                    v = side * (BUS_HW + 0.55 + 0.15 * math.sin(t * 3 + i))
                    jump = abs(math.sin(t * 2.6 + i * 1.7))
                    z, pitch_ = 0.9 + 0.7 * jump, -55 - 15 * jump
                root.location = W(t, du, v, z)
                yawd = 180 if t < T_STOP + 0.5 else (90 if side < 0 else 270)
                root.rotation_euler = (0, D(pitch_), D(yawd))          # nose up while jumping
                run = 1.0 if t < T_STOP + 0.5 else 0.35
                for piv, lx, ly in legs:
                    s_ = (1 if lx > 0 else -1) * (1 if ly > 0 else 0.8)
                    piv.rotation_euler = (0, D(45) * run * math.sin(t * 14 + ph + s_ * 1.5), 0)
                    piv.keyframe_insert("rotation_euler", frame=f)
            root.keyframe_insert("location", frame=f)
            root.keyframe_insert("rotation_euler", frame=f)

        # ---------------- our hands: on the radio, the door wheel, the seat in front
        if f % 240 == 1:
            print("frame", f, "of", N, flush=True)
        holding = any(a <= t < b for a, b in radio_spans)
        if holding:
            arms.set(f, "R", (0.12, -0.3, -0.5))
            arms.set(f, "L", (-0.02, -0.32, -0.52))
        elif at("me2") - 0.3 <= t < T_DOOR + 1.6:
            ang = D(-95) * op
            wl = Vector((-0.7, 0.25, 0.0))
            wp = Vector((BX + 0.7, DOOR_Y + 0.2, 1.1)) + Vector((wl.x * math.cos(ang) - wl.y * math.sin(ang),
                                                                 wl.x * math.sin(ang) + wl.y * math.cos(ang), 0))
            cm = cam.matrix_world.copy()
            from mathutils import Euler, Matrix as _M
            cm = _M.Translation(cam.location) @ Euler(cam.rotation_euler).to_matrix().to_4x4()
            arms.set(f, "R", cm.inverted() @ (wp + Vector((0.15, 0, 0))))
            arms.set(f, "L", cm.inverted() @ (wp - Vector((0.15, 0, 0))))
        elif T_BANG <= t < T_STOP + 1.5:
            arms.set(f, "R", (0.3, -0.25, -0.75))
            arms.set(f, "L", (-0.3, -0.25, -0.75))
        elif t >= T_IN + 2.5:                       # seated on the bus: hands on our knees, low in the view
            arms.set(f, "R", (0.24, -0.55, -0.32))
            arms.set(f, "L", (-0.26, -0.55, -0.32))
        else:
            arms.set(f, "R", (0.28, -0.45, -0.5))
            arms.set(f, "L", (-0.3, -0.45, -0.5))

    # ---------------- the end: the beast walks up the road towards the bus, the car comes on behind it
    broot, bhead, blimbs, bglow = beast
    B_IN = at("radio2") - 0.5                                 # it steps out of the dark onto the road
    for f in range(1, N + 1, 2):
        t = (f - 1) / FPS
        vis = t >= B_IN
        show([broot], f, vis)
        u = seg(t, B_IN, END)
        x = X_STOP - 20 + 13 * u                              # 20 m ahead of the bus front -> 7 m
        step = (t - B_IN) * 2.6
        broot.location = (x, ROAD_Y + 2.6 + 0.3 * math.sin(step * 0.5), 0.06 * abs(math.sin(step * math.pi)))
        broot.rotation_euler = (D(3) * math.sin(step * math.pi), 0, D(6) * math.sin(step * 0.5))
        broot.keyframe_insert("location", frame=f)
        broot.keyframe_insert("rotation_euler", frame=f)
        for sh, hip, side in blimbs:
            ph = step * math.pi + (0 if side < 0 else math.pi)
            sh.rotation_euler = (0, D(25) * math.sin(ph), 0)
            hip.rotation_euler = (0, D(-22) * math.sin(ph + math.pi), 0)
            sh.keyframe_insert("rotation_euler", frame=f)
            hip.keyframe_insert("rotation_euler", frame=f)
        bhead.rotation_euler = (D(8) * math.sin(step * 0.7), D(-10) + D(5) * math.sin(step * 1.3), 0)
        bhead.keyframe_insert("rotation_euler", frame=f)
        bglow.data.energy = (60 + 25 * math.sin(t * 7.0)) if vis else 0.0
        bglow.data.keyframe_insert("energy", frame=f)
        cu = seg(t, T_LIGHTS, END + 4)                         # the car rolls slowly towards us, lights on
        far_root.location = (X_STOP - 42 + 10 * cu, ROAD_Y - 2.5, 0)
        far_root.keyframe_insert("location", frame=f)

    # ---------------- light & sky: grey day -> dusk -> night (keyed)
    bpy.ops.object.light_add(type="SUN", rotation=(D(55), D(15), D(-30)))
    sun = bpy.context.object
    sun.data.angle = D(10)
    setup_render(scene, samples=int(os.environ.get("SAMPLES", "12")), res=((1280, 720) if WIDE else (540, 960)), sky=(0.66, 0.66, 0.67),
                 sky_strength=1.0)
    scene.cycles.max_bounces = 3
    scene.cycles.transparent_max_bounces = 16
    bg = scene.world.node_tree.nodes["Background"]
    DAY, DUSK, NIGHT = (0.62, 0.62, 0.64), (0.42, 0.34, 0.42), (0.03, 0.04, 0.08)
    for f in range(1, N + 1, 2):
        t = (f - 1) / FPS
        if t < T_DUSK0:
            sky, se = DAY, 1.2
        elif t < T_DUSK1:
            u = seg(t, T_DUSK0, T_DUSK1)
            sky, se = mix(DAY, DUSK, u), lerp(1.2, 0.5, u)
        else:
            u = seg(t, T_DUSK1, T_FOREST + 1)
            sky, se = mix(DUSK, NIGHT, u), lerp(0.5, 0.06, u)
        bg.inputs["Color"].default_value = (*sky, 1)
        bg.inputs["Color"].keyframe_insert("default_value", frame=f)
        sun.data.energy = se
        sun.data.color = mix((0.88, 0.88, 0.92), (0.55, 0.6, 0.9), seg(t, T_DUSK0, T_FOREST))
        sun.data.keyframe_insert("energy", frame=f)
        sun.data.keyframe_insert("color", frame=f)
    # fog: soft veils in front of the camera at growing distance (day grey, night blue-black)
    fog_m = bpy.data.materials.new("Fog veil")
    fog_m.use_nodes = True
    nt = fog_m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    mxs = nt.nodes.new("ShaderNodeMixShader")
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    em = nt.nodes.new("ShaderNodeEmission")
    nt.links.new(tr.outputs[0], mxs.inputs[1])
    nt.links.new(em.outputs[0], mxs.inputs[2])
    nt.links.new(mxs.outputs[0], out.inputs["Surface"])
    for k in range(10):
        d = 9.0 + k * 5.0
        bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, -d))
        v = bpy.context.object
        v.scale = (d * 2.2, d * 3.6, 1)
        v.name = "Fog veil"
        v.data.materials.append(fog_m)
        v.visible_shadow = False
        v.visible_diffuse = False
        v.visible_glossy = False
        parent_local(v, cam)
    for f in range(1, N + 1, 2):
        t = (f - 1) / FPS
        inside_bunker = t < T_DOOR + 0.5
        dens = 0.0 if inside_bunker else (0.1 if t < T_FOREST else 0.07)
        sky = bg.inputs["Color"].default_value
        c = DAY if t < T_DUSK0 else (mix(DAY, DUSK, seg(t, T_DUSK0, T_DUSK1)) if t < T_DUSK1
                                     else mix(DUSK, NIGHT, seg(t, T_DUSK1, T_FOREST + 1)))
        mxs.inputs[0].default_value = dens
        em.inputs["Color"].default_value = (*c, 1)
        mxs.inputs[0].keyframe_insert("default_value", frame=f)
        em.inputs["Color"].keyframe_insert("default_value", frame=f)
    scene.frame_set(1)
    return scene


if __name__ == "__main__":
    sc = build()
    if arg("--save"):
        bpy.ops.wm.save_as_mainfile(filepath=os.path.join(HERE, "pov_wide.blend" if WIDE else "pov.blend"))
    if arg("--still"):
        os.makedirs(os.path.join(HERE, "test"), exist_ok=True)
        for fr_ in str(arg("--still")).split(","):
            sc.frame_set(int(fr_))
            sc.render.filepath = os.path.join(HERE, "test", f"pov_{int(fr_):04d}.png")
            bpy.ops.render.render(write_still=True)
