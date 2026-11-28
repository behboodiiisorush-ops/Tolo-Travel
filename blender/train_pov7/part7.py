"""
«واگن آخر ۷ — اون طرف آب» — straight on from episode 6.  The train has stopped just before the broken bridge.
On the ground by the locomotive, Lena holds the radio: Mom says they are landing on this side of the bridge to
pick us up.  Across the river the helicopter comes down; its door slides open — "oh my God" — the radio breaks
up and dies, the searchlight swings and goes out.  Lena calls and calls.  The rotor winds down; only the red
beacon blinks.  Then three knocks on the radio: grandma.  At the edge of the bridge Rahim ties the rope round
our waists and stays with the train.  Out on the two bare rails over the gap; a plank breaks and falls into the
river; Lena: "don't look down... look at me".  The train horn behind us — Rahim's warning — and on the far bank
a shadow gets up beside the dead helicopter and comes towards the bridge.  Black.

    ../cast/vendor/venv/bin/python part7.py --save
    ../cast/vendor/venv/bin/python part7.py --still 49,361
"""

import math
import os
import random
import sys

import bpy
from mathutils import Euler, Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403,E402
from captions import END, KEY_OF  # noqa: E402
from lib5 import build_fog, build_helicopter  # noqa: E402

random.seed(77)
T = KEY_OF
FPS = 24
GROUND = -1.3
EYE = 1.42                                   # my eye height above what I stand on
BR0 = 24.5                                   # bridge abutment (y); the locomotive nose is at 23
GAP0, GAP1 = BR0 + 5, BR0 + 35               # the missing span
BR1 = BR0 + 62                               # the far bank
RIVER_Z = GROUND - 5
SKID = 1.6 * 2.4                             # helicopter scaled x2.4: skids this far below its root
HELI_PAD = Vector((-13.0, BR1 + 8, GROUND + SKID))   # where it lands


def at(key, k=0):
    return T[key][k]


def ease(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def seg(t, a, b):
    return ease((t - a) / (b - a))


def yaw_to(d):
    return math.degrees(math.atan2(-d.x, d.y)) % 360


def pitch_to(d):
    return math.degrees(math.atan2(d.z, d.xy.length))


def lerp_yaw(a, b, u):
    d = (b - a + 180) % 360 - 180
    return a + d * u


# ---------------------------------------------------------------- story beats (seconds)
LAND1 = at("n1") - 0.3                     # skids on the ground
DOOR_T = at("mom3") - 1.4                  # the door slides open (over the radio)
DEAD_T = at("mom3", 1) + 0.25              # the radio breaks up and dies
LIGHT_OFF = DEAD_T + 0.6                   # the searchlight swings away and goes out
WIND0 = at("lena4") - 2.2                  # the rotor winds down
KNOCK0 = at("lena5") - 3.4                 # the knock clip starts (knocks at +0.4, +1.4, +2.4)
KNOCKS = [KNOCK0 + d for d in (0.4, 1.4, 2.4)]
CUT2 = at("rahim2") - 1.6                  # cut: the edge of the bridge
TIE0, TIE1 = at("rahim3") + 0.2, at("rahim4") - 0.1    # the rope round our waists
WALK0 = at("n6") - 2.4                     # out on the rails
PLANK_T = at("lena8") - 1.8                # a plank breaks under my foot
WALK1 = at("lena9") - 3.4                  # stopped in the middle
HORN_T = at("lena9") - 3.2                 # the train horn behind us
SHADOW0 = at("lena9") - 2.1                # a shadow gets up by the helicopter
BLACK_T = at("n9", 1) + 0.4


def rail_z(y):
    """the two bare rails sag over the gap"""
    if y <= GAP0 or y >= GAP1:
        return GROUND
    u = (y - GAP0) / (GAP1 - GAP0)
    return GROUND - 0.7 * math.sin(math.pi * u)


def my_y(t):
    """where I stand along the track"""
    if t < CUT2:
        return 19.8
    if t < WALK0:
        return 28.4
    y = 28.4 + (34.2 - 28.4) * seg(t, WALK0, PLANK_T - 0.2)
    y += (44.0 - 34.2) * seg(t, PLANK_T + 1.6, WALK1)
    return y


def my_x(t):
    return -7.0 if t < CUT2 else (-0.35 if t < WALK0 + 0.8 else lerp(-0.35, -0.72, seg(t, WALK0, WALK0 + 1.2)))


def cam_pos(t):
    y = my_y(t)
    return Vector((my_x(t), y, rail_z(y) + EYE))


# ================================================================ sets


def build_outside():
    parts = []
    rr = random.Random(4)
    ground_m = toon("Ash ground", (0.44, 0.45, 0.41), 0.1)
    cliff = toon("Cliff", (0.36, 0.34, 0.32), 0.08)
    parts.append(box((0, (BR0 - 2 - 150) / 2, GROUND - 0.05), (500, BR0 - 2 + 150, 0.1), ground_m, "Ground"))
    parts.append(box((0, BR0 - 2, (GROUND + RIVER_Z) / 2), (500, 0.6, GROUND - RIVER_Z), cliff, "Near bank"))
    parts.append(box((0, BR1 + 2 + 250, GROUND - 0.05), (500, 500, 0.1), ground_m, "Far ground"))
    parts.append(box((0, BR1 + 2, (GROUND + RIVER_Z) / 2), (500, 0.6, GROUND - RIVER_Z), cliff, "Far bank"))
    parts.append(box((0, (BR0 + BR1) / 2, RIVER_Z), (500, BR1 - BR0 + 4, 0.2), toon("River", (0.16, 0.3, 0.44), 0.3), "River"))
    for p in rails(0, -150, GAP0, GROUND, "Track"):
        parts.append(p)
    for p in rails(0, GAP1, BR1 + 200, GROUND, "Far track"):
        parts.append(p)
    # dead trees and poles on the fields
    bark = toon("Dead tree", (0.22, 0.19, 0.17), 0.05)
    for k in range(40):
        y = rr.uniform(-120, BR0 - 10)
        x = rr.choice((-1, 1)) * rr.uniform(9, 70)
        h = rr.uniform(3, 7)
        parts.append(rod((x, y, GROUND), (x, y, GROUND + h), 0.12, bark, "Tree"))
        for b in range(3):
            a = rr.uniform(0, 6.28)
            z0 = GROUND + h * rr.uniform(0.5, 0.9)
            parts.append(rod((x, y, z0), (x + math.cos(a) * 1.4, y + math.sin(a) * 1.4, z0 + 1.2), 0.05, bark, "Branch"))
    for k in range(18):
        y = rr.uniform(BR1 + 30, BR1 + 120)
        x = rr.choice((-1, 1)) * rr.uniform(14, 70)
        h = rr.uniform(3, 7)
        parts.append(rod((x, y, GROUND), (x, y, GROUND + h), 0.12, bark, "Far tree"))
    # the bridge: deck, piers, truss girders; the middle span is gone
    iron = toon("Bridge iron", (0.42, 0.18, 0.1), 0.15)
    rust = toon("Bridge rust", (0.55, 0.26, 0.12), 0.15)
    deck_m = toon("Bridge deck", (0.4, 0.38, 0.36), 0.08)
    for a, b in ((BR0 - 2, GAP0), (GAP1, BR1 + 2)):
        parts.append(box((0, (a + b) / 2, GROUND - 0.7), (6.0, b - a, 1.2), deck_m, "Deck"))
        for sx in (-3.2, 3.2):
            parts.append(box((sx, (a + b) / 2, GROUND + 9.0), (0.7, b - a, 0.8), iron, "Top chord"))
            parts.append(box((sx, (a + b) / 2, GROUND + 0.2), (0.7, b - a, 0.8), iron, "Bottom chord"))
            y = a
            while y <= b - 0.1:
                parts.append(rod((sx, y, GROUND), (sx, y, GROUND + 9.0), 0.3, iron, "Vertical"))
                if y + 7 <= b:
                    parts.append(rod((sx, y, GROUND), (sx, y + 7, GROUND + 9.0), 0.22, rust, "Diagonal"))
                y += 7
    pier = toon("Pier", (0.5, 0.48, 0.45), 0.1)
    for py in (BR0 + 3, GAP1 + 8, GAP1 + 30, GAP1 + 52):
        parts.append(box((0, py, (GROUND - 1.3 + RIVER_Z) / 2), (4.0, 3.0, GROUND - 1.3 - RIVER_Z), pier, "Pier"))
    slab = box((0, GAP0 + 5, GROUND - 4.5), (5.4, 11, 0.9), deck_m, "Fallen slab")
    slab.rotation_euler = (D(-42), D(6), 0)
    parts.append(slab)
    slab2 = box((0.5, GAP1 - 4, GROUND - 3.2), (5.4, 8, 0.9), deck_m, "Fallen slab 2")
    slab2.rotation_euler = (D(36), D(-8), 0)
    parts.append(slab2)
    for sx in (-3.2, 3.2):
        parts.append(rod((sx, GAP0, GROUND + 9.0), (sx * 1.15, GAP0 + 8, GROUND + 3.0), 0.3, rust, "Bent girder"))
        parts.append(rod((sx, GAP1, GROUND + 9.0), (sx * 0.9, GAP1 - 7, GROUND + 4.0), 0.3, rust, "Bent girder"))
    # the two rails still hanging over the gap, a few sleepers left on them
    steel = toon("Rail steel", (0.55, 0.55, 0.6), 0.25)
    wood = toon("Sleeper", (0.42, 0.3, 0.2), 0.08)
    n = 40
    for sx in (-0.72, 0.72):
        for k in range(n):
            y0 = GAP0 + (GAP1 - GAP0) * k / n
            y1 = GAP0 + (GAP1 - GAP0) * (k + 1) / n
            parts.append(rod((sx, y0, rail_z(y0) + 0.08), (sx, y1, rail_z(y1) + 0.08), 0.045, steel, "Hanging rail"))
    sleepers = []
    y = GAP0 + 0.4
    while y < GAP1 - 0.3:
        if rr.random() < 0.55 or abs(y - 34.6) < 0.31:
            s = box((0, y, rail_z(y) + 0.02), (2.0, 0.24, 0.12), wood, "Sleeper")
            s.rotation_euler = (0, D(rr.uniform(-6, 6)), D(rr.uniform(-4, 4)))
            sleepers.append(s)
        y += 0.6
    # the camp on the far bank: tents and warm lamps in the fog
    tent_m = [toon("Tent a", (0.95, 0.55, 0.15), 0.3), toon("Tent b", (0.92, 0.9, 0.85), 0.3)]
    lamp = glow_mat("Camp lamp", (1.0, 0.75, 0.35), 25.0)
    for k in range(12):
        x = -45 + k * 5.5 + rr.uniform(-1, 1)
        yy = BR1 + 35 + rr.uniform(0, 30)
        bpy.ops.mesh.primitive_cone_add(radius1=2.0, depth=2.6, location=(x, yy, GROUND + 1.3), vertices=6)
        parts.append(finish(bpy.context.object, tent_m[k % 2], "Tent"))
        if k % 3 == 0:
            parts.append(ball((x + 1.5, yy - 2, GROUND + 2.6), 0.8, lamp, "Camp light", seg=10))
    foam_m = toon("Foam", (0.85, 0.9, 0.92), 0.4)
    foam = []
    for k in range(34):
        fo = box((rr.uniform(-120, 120), rr.uniform(BR0 + 2, BR1 - 2), RIVER_Z + 0.12), (rr.uniform(4, 12), 0.25, 0.05),
                 foam_m, "Foam")
        foam.append((fo, fo.location.x))
    return foam, sleepers


def build_train():
    """our car and the locomotive, standing before the bridge"""
    wagon_exterior("Our car", 0, -13.0, 13.0, GROUND, -1, [8.0], burnt=0.2)
    wagon_exterior("Loco", 0, 13.3, 23.0, GROUND, 1, [], burnt=0.3)
    red = toon("Train red", (0.78, 0.1, 0.08), 0.3)
    box((0, 23.1, GROUND + 2.2), (3.1, 0.12, 1.6), red, "Loco nose")
    head = glow_mat("Headlight", (1.0, 0.95, 0.8), 6.0)
    for sx in (-0.9, 0.9):
        ball((sx, 23.2, GROUND + 1.9), 0.18, head, "Headlight", seg=12)
    bpy.ops.object.light_add(type="SPOT", location=(0, 23.4, GROUND + 1.9), rotation=(D(-84), 0, 0))
    hl = no_cam(bpy.context.object)
    hl.data.energy = 900
    hl.data.spot_size = D(40)
    hl.data.color = (1.0, 0.95, 0.85)


def build_radio():
    root = empty("Radio root")
    black = toon("Rescue radio", (0.1, 0.1, 0.11), 0.15)
    for o in (box((0, 0, 0), (0.075, 0.045, 0.15), black, "Radio body", bevel=0.01),
              rod((0.022, 0, 0.07), (0.022, 0, 0.19), 0.006, black, "Radio antenna"),
              box((0, 0.024, -0.02), (0.055, 0.004, 0.05), toon("Radio grille", (0.3, 0.3, 0.32), 0.1), "Radio grille"),
              box((0, 0.024, 0.045), (0.05, 0.004, 0.02), toon("Radio screen", (0.5, 0.75, 0.45), 0.8), "Radio screen")):
        parent_keep(o, root)
    led = ball((-0.025, 0.026, 0.065), 0.008, glow_mat("Radio LED on", (1.0, 0.25, 0.15), 8.0), "Radio LED")
    parent_keep(led, root)
    root.rotation_mode = "XYZ"
    return root, led


def build_rope():
    m = toon("Rope", (0.85, 0.8, 0.6), 0.2)
    return [rod((0, 0, 0), (0, 0, 1), 0.018, m, f"Rope {k}") for k in range(3)]


def blacken(person):
    ink = toon("Shadow figure", (0.05, 0.05, 0.06), 0.0)
    for o in bpy.data.objects:
        if o.name.startswith(person.name + " ") and o.type == "MESH":
            o.data.materials.clear()
            o.data.materials.append(ink)


# ================================================================ animation


def heli_pos(t):
    hi = HELI_PAD + Vector((-10, 22, 32))
    p = hi.lerp(HELI_PAD + Vector((0, 0, 6)), seg(t, 0.0, LAND1 - 2.2))
    p = p.lerp(HELI_PAD, seg(t, LAND1 - 2.2, LAND1))
    sway = 1 - seg(t, LAND1 - 0.6, LAND1)
    return p + Vector((0.5 * math.sin(t * 0.7), 0.6 * math.sin(t * 0.43), 0.3 * math.sin(t * 0.9))) * sway


def rotor_speed(t):
    return 25.0 * (1 - seg(t, WIND0, WIND0 + 9.0))


def cam_beats(lena_head, rahim_head, shadow_head):
    """(start, blend seconds, fn(t) -> (yaw, pitch))"""
    def look(p, t):
        d = p - cam_pos(t)
        return yaw_to(d), max(-60, min(35, pitch_to(d)))

    heli = lambda t: look(heli_pos(t) + Vector((0, 0, -1.0)), t)              # noqa: E731
    lena = lambda t: look(lena_head(t), t)                                    # noqa: E731
    rahim = lambda t: look(rahim_head(t), t)                                  # noqa: E731
    radio = lambda t: look(lena_head(t) + Vector((0.15, 0.1, -0.45)), t)      # noqa: E731
    gap = lambda t: (2.0, -38.0)                                              # noqa: E731
    ahead = lambda t: (1.0 + 1.5 * math.sin(t * 0.5), -12.0)                  # noqa: E731
    down = lambda t: (6.0, -62.0)                                             # noqa: E731
    back_lena = lambda t: look(lena_head(t), t)                               # noqa: E731
    train = lambda t: look(Vector((0, 22.0, GROUND + 2.6)), t)                # noqa: E731
    shadow = lambda t: look(shadow_head(t), t)                                # noqa: E731
    far = lambda t: look(HELI_PAD + Vector((-3, -4, -SKID + 1.0)), t)                # noqa: E731
    return [
        (0.0, 0.0, heli),
        (at("mom2") - 0.2, 0.6, radio),
        (at("lena1") - 0.15, 0.4, lena),
        (at("lena1", 1) + 0.1, 0.8, heli),
        (DOOR_T - 0.3, 0.5, radio),
        (DEAD_T + 0.1, 0.4, heli),
        (at("lena2") + 0.2, 0.5, lena),
        (at("rahim1") - 0.2, 0.4, rahim),
        (at("lena4") - 1.6, 0.9, far),
        (at("lena4") - 0.2, 0.6, lena),
        (at("n2") + 0.4, 1.2, far),
        (KNOCK0, 0.5, radio),
        (at("lena5") - 0.1, 0.4, lena),
        (at("n4") + 0.2, 0.8, far),
        (CUT2, 0.0, gap),
        (at("rahim2") + 0.1, 0.5, rahim),
        (at("n5"), 0.8, far),
        (at("rahim3") - 0.2, 0.5, rahim),
        (TIE0 + 0.4, 0.5, lambda t: (330.0, -55.0)),
        (at("rahim4") - 0.1, 0.5, rahim),
        (at("lena7") - 0.15, 0.4, lena),
        (at("rahim5") - 0.15, 0.4, rahim),
        (WALK0, 0.6, ahead),
        (PLANK_T - 0.3, 0.3, down),
        (at("lena8") - 0.3, 0.7, back_lena),
        (at("n7") + 0.5, 0.8, ahead),
        (HORN_T + 0.1, 0.6, train),
        (SHADOW0 + 0.3, 0.7, shadow),
        (at("lena9") + 0.2, 0.5, back_lena),
        (at("n8") - 0.1, 0.8, shadow),
    ]


def cam_at(t, beats):
    cur = 0
    for i, b in enumerate(beats):
        if b[0] <= t:
            cur = i
    y1, p1 = beats[cur][2](t)
    if cur == 0 or beats[cur][1] <= 0:
        return y1, p1
    y0, p0 = beats[cur - 1][2](t)
    u = seg(t, beats[cur][0], beats[cur][0] + beats[cur][1])
    return lerp_yaw(y0, y1, u), lerp(p0, p1, u)


def lena_pos(t):
    if t < CUT2:
        return Vector((-6.2, 21.0, GROUND))
    if t < WALK0 + 0.6:
        return Vector((-1.2, 27.6, GROUND))
    y = my_y(t - 1.3) - 1.25
    return Vector((-0.72, y, rail_z(y)))


def rahim_pos(t):
    if t < CUT2:
        return Vector((-5.0, 21.7, GROUND))
    if t < at("rahim5", 1) + 1.0:
        return Vector((0.9, 27.4, GROUND))
    return Vector((0.9, 27.4, GROUND)).lerp(Vector((1.8, 22.6, GROUND)), seg(t, at("rahim5", 1) + 1.0, at("rahim5", 1) + 4.5))


def shadow_pos(t):
    p0 = HELI_PAD + Vector((3.5, -3.0, -SKID))
    p1 = Vector((-1.0, BR1 + 2.0, GROUND))            # to the far end of the bridge...
    p2 = Vector((-0.6, GAP1 + 2.5, GROUND))           # ...and out along the far deck towards us
    u = (t - SHADOW0 - 1.2) / 9.0
    return p0.lerp(p1, ease(u * 2)) if u < 0.5 else p1.lerp(p2, ease((u - 0.5) * 2))


def build():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.fps = FPS
    n_frames = int(END * FPS)
    scene.frame_start, scene.frame_end = 1, n_frames
    scene.frame_step = 2

    foam, sleepers = build_outside()
    build_train()
    heli, rotor = build_helicopter()
    heli.scale = (2.4, 2.4, 2.4)
    spot = [o for o in heli.children if o.type == "LIGHT"][0]
    lamp_on = [o for o in heli.children if o.name.startswith("Searchlight")]
    beacon = ball((0, -6.4, 2.0), 0.22, glow_mat("Beacon", (1.0, 0.1, 0.05), 40.0), "Heli beacon")
    parent_keep(beacon, heli)
    door = box((1.55, 0.3, -0.2), (0.08, 1.4, 1.2), toon("Heli door", (0.22, 0.25, 0.24), 0.1), "Heli door")
    parent_keep(door, heli)
    fog_col = build_fog()
    for v in list(fog_col.objects):                     # no grey walls right beside us out here
        if abs(v.location.x) < 9:
            bpy.data.objects.remove(v, do_unlink=True)
    lena, rahim = make_lena(), make_rahim()
    shadow = make_extra(2, 1.15)
    blacken(shadow)
    radio, led = build_radio()
    ropes = build_rope()
    cam = make_camera(scene)
    cam.data.lens = 16
    arms = POVArms(cam)

    def lena_head(t):
        return lena_pos(t) + Vector((0, 0, 1.05))

    def rahim_head(t):
        return rahim_pos(t) + Vector((0, 0, 1.75))

    def shadow_head(t):
        return shadow_pos(t) + Vector((0, 0, 1.0 + 0.6 * seg(t, SHADOW0, SHADOW0 + 1.2)))

    beats = cam_beats(lena_head, rahim_head, shadow_head)
    rs = random.Random(5)
    shake = [(rs.uniform(-1, 1), rs.uniform(-1, 1), rs.uniform(-1, 1)) for _ in range(n_frames + 3)]
    plank = min(sleepers, key=lambda s: abs(s.location.y - 34.6))
    plank_rest = plank.location.copy()

    for f in range(1, n_frames + 1):
        t = (f - 1) / FPS
        for fo, x0 in foam:
            fo.location.x = x0 + ((t * 3.0) % 20) - 10
            fo.keyframe_insert("location", frame=f)

        # ---------------- the helicopter on the far bank
        hp = heli_pos(t)
        heli.location = hp
        heli.rotation_euler = (D(-4 * (1 - seg(t, LAND1 - 1, LAND1))), D(2 * math.sin(t * 0.6) * (1 - seg(t, LAND1 - 1, LAND1))),
                               D(lerp(-150, -120, seg(t, 0, LAND1))))
        heli.keyframe_insert("location", frame=f)
        heli.keyframe_insert("rotation_euler", frame=f)
        rotor.rotation_euler = (0, 0, rotor.rotation_euler[2] + rotor_speed(t) / FPS)
        rotor.keyframe_insert("rotation_euler", frame=f)
        lit = t < LIGHT_OFF
        swing = seg(t, DEAD_T, LIGHT_OFF)
        spot.data.energy = 30000 * (1 - swing) if lit else 0.0
        spot.data.keyframe_insert("energy", frame=f)
        spot.rotation_euler = (D(-20 - 50 * swing), D(35 * swing), 0)
        spot.keyframe_insert("rotation_euler", frame=f)
        show(lamp_on, f, lit)
        show([beacon], f, int(t * 1.6) % 2 == 0)
        door.location.y = 0.3 - 1.2 * seg(t, DOOR_T, DOOR_T + 0.6)
        door.keyframe_insert("location", frame=f)

        # ---------------- the plank that breaks
        if t < PLANK_T:
            plank.location = plank_rest
            plank.rotation_euler = (0, 0, 0)
        else:
            dt = t - PLANK_T
            plank.location = plank_rest + Vector((0.3 * dt, 0.4 * dt, -4.9 * dt * dt))
            plank.location.z = max(plank.location.z, RIVER_Z + 0.1)
            plank.rotation_euler = (D(70 * dt), D(110 * dt), 0)
        plank.keyframe_insert("location", frame=f)
        plank.keyframe_insert("rotation_euler", frame=f)

        # ---------------- camera
        yaw, pitch = cam_at(t, beats)
        pos = cam_pos(t)
        walking = WALK0 + 0.4 <= t < WALK1 and not (PLANK_T - 0.3 <= t < PLANK_T + 1.6)
        amp = 0.15 + (0.6 if walking else 0.0)
        if PLANK_T <= t < PLANK_T + 0.6:
            amp += 3.0 * (1 - (t - PLANK_T) / 0.6)
        if DEAD_T <= t < DEAD_T + 0.5:
            amp += 0.8
        sx_, sy_, sz_ = shake[f]
        bob = 0.03 * math.sin(2 * math.pi * t * 1.6) if walking else 0.0
        if PLANK_T <= t < PLANK_T + 0.5:
            bob -= 0.15 * math.sin(math.pi * (t - PLANK_T) / 0.5)
        cam.location = pos + Vector((0, 0, bob))
        cam.rotation_euler = (D(90 + pitch + sx_ * amp), D(sy_ * amp * 0.6), D(yaw + sz_ * amp))
        cam.keyframe_insert("location", frame=f)
        cam.keyframe_insert("rotation_euler", frame=f)

        # ---------------- my hands
        L, R = (-0.3, -0.42, -0.46), (0.28, -0.42, -0.46)
        if TIE0 <= t < TIE1:                                    # tying the rope at my waist
            w = math.sin(t * 9)
            L, R = (-0.1 + 0.03 * w, -0.45, -0.55), (0.1 - 0.03 * w, -0.43, -0.55)
        if t >= WALK0:                                          # arms out for balance on the rail
            u = seg(t, WALK0, WALK0 + 0.8)
            wob = 0.05 * math.sin(t * 2.3)
            L = tuple(lerp(a, b, u) for a, b in zip(L, (-0.55, -0.25 + wob, -0.55)))
            R = tuple(lerp(a, b, u) for a, b in zip(R, (0.55, -0.25 - wob, -0.55)))
        if PLANK_T <= t < PLANK_T + 1.2:                         # grab at the air
            k = 1 - seg(t, PLANK_T + 0.4, PLANK_T + 1.2)
            L = (L[0] - 0.1 * k, L[1] + 0.15 * k, L[2] + 0.1 * k)
            R = (R[0] + 0.1 * k, R[1] + 0.15 * k, R[2] + 0.1 * k)
        arms.set(f, "L", L)
        arms.set(f, "R", R)

        # ---------------- Lena: radio in her hands; calls, cries, hopes; follows me on the rail
        lp = lena_pos(t)
        hold = t < CUT2
        cry = seg(t, at("lena2") - 0.2, at("lena2") + 0.3) * (1 - seg(t, KNOCKS[0], KNOCKS[0] + 0.4))
        joy = seg(t, KNOCKS[0], KNOCKS[0] + 0.4) * (1 - seg(t, at("n4", 1), at("n4", 1) + 1.0))
        scared = seg(t, PLANK_T, PLANK_T + 0.3) * (1 - seg(t, at("lena8") - 0.2, at("lena8") + 0.4))
        fear = seg(t, HORN_T, HORN_T + 0.4)
        on_rail = t >= WALK0 + 0.6
        if t < CUT2:
            face = lerp(-25, 205, cry) if t < at("lena5") - 0.3 else lerp(205, 160, seg(t, at("lena5") - 0.3, at("lena5")))
        elif not on_rail:
            face = lerp(-20, 0, seg(t, at("lena7") - 0.4, at("lena7")))
        else:
            face = 0
        look_y = 0
        look_p = lerp(lerp(6, -25, cry), 10, joy)
        if on_rail and t >= at("lena8") - 0.4:
            look_p = 8
        lena.pose(f, t, lp, facing=face, run=0.25 if (on_rail and walking) else 0.0, run_rate=1.6, lean=-4,
                  look=(look_y, look_p), hug=max(0.45 * cry, 0.6 * scared, 0.4 * fear),
                  worry=lerp(lerp(1.3, 2.4, max(cry, scared, fear)), 0.2, joy),
                  reach=(75, -8) if hold else ((120, 40) if on_rail else None),
                  reach2=(75, 8) if hold else ((120, -40) if on_rail else None))
        bpy.context.view_layer.update()
        if hold:
            hw = lena.hand_world("R")
            radio.location = hw + Vector((-0.05, 0.06, 0.04))
            radio.rotation_euler = (D(-10), 0, D(-10))
        else:
            radio.location = cam.matrix_world @ Vector((0.0, -0.2, 3.0))    # in my bag, out of sight
        radio.keyframe_insert("location", frame=f)
        radio.keyframe_insert("rotation_euler", frame=f)
        talking_radio = any(at(k) - 0.3 <= t <= at(k, 1) + 0.2 for k in ("mom1", "mom2", "mom3"))
        knock = any(k_ <= t < k_ + 0.25 for k_ in KNOCKS)
        show([led], f, (t < DEAD_T and (talking_radio or int(t * 2) % 2 == 0)) or knock)

        # ---------------- Rahim
        rp = rahim_pos(t)
        going = at("rahim5", 1) + 1.0 <= t < at("rahim5", 1) + 4.5
        r_face = -150 if going else ((lerp(-10, 120, seg(t, at("rahim1") - 0.4, at("rahim1"))) if t < CUT2 else -60))
        rahim.pose(f, t, rp, facing=r_face, run=0.6 if going else 0.0, run_rate=1.4,
                   look=(lerp(0, 25, seg(t, at("lena4") - 1.6, at("lena4"))) if t < CUT2 else 10, 4),
                   reach=(95, 5) if TIE0 <= t < TIE1 else None,
                   reach2=(95, -5) if TIE0 <= t < TIE1 else None, worry=1.9)

        # ---------------- the rope: loco coupler -> Lena's waist -> my waist (once tied)
        tied = t >= TIE0 + 0.6
        my_waist = pos + Vector((0, 0, -0.62 - EYE + 1.42))
        lw = lp + Vector((0, 0, 0.55))
        anchor = Vector((0.0, 22.9, GROUND + 0.9))
        for rope, (a, b) in zip(ropes, ((anchor, lw), (lw, my_waist), (my_waist, my_waist + Vector((0, 0.01, -0.3))))):
            place_rod(rope, a, b)
            rope.scale = (1, 1, max(0.001, (b - a).length)) if tied else (0.001, 0.001, 0.001)
            rope.keyframe_insert("location", frame=f)
            rope.keyframe_insert("rotation_quaternion", frame=f)
            rope.keyframe_insert("scale", frame=f)

        # ---------------- the shadow on the far bank
        sp = shadow_pos(t)
        up = seg(t, SHADOW0, SHADOW0 + 1.2)
        shadow.pose(f, t, sp if t >= SHADOW0 - 0.5 else Vector((0, -400, 0)), facing=180,
                    crouch=1 - up, run=0.2 * seg(t, SHADOW0 + 1.2, SHADOW0 + 2.0), run_rate=0.7, lean=8,
                    look=(0, -10), worry=0, talk=False)

    # black at the very end
    bpy.ops.object.light_add(type="SUN", rotation=(D(60), D(10), D(70)))
    sun = bpy.context.object
    sun.data.energy = 1.0
    sun.data.color = (0.82, 0.84, 0.92)
    setup_render(scene, sky=(0.6, 0.61, 0.65), sky_strength=1.0)
    bg = scene.world.node_tree.nodes["Background"]
    for tt, k in ((0.0, 1.0), (BLACK_T - 0.05, 1.0), (BLACK_T + 0.6, 0.0)):
        bg.inputs["Strength"].default_value = k
        bg.inputs["Strength"].keyframe_insert("default_value", frame=int(tt * FPS) + 1)
        sun.data.energy = 1.0 * k
        sun.data.keyframe_insert("energy", frame=int(tt * FPS) + 1)
    scene.view_settings.exposure = 0
    for tt, ev in ((0.0, 0.0), (BLACK_T - 0.05, 0.0), (BLACK_T + 0.6, -10.0)):
        scene.view_settings.exposure = ev
        scene.view_settings.keyframe_insert("exposure", frame=int(tt * FPS) + 1)
    ls = scene.view_layers[0].freestyle_settings.linesets[0]
    ls.select_by_collection = True
    ls.collection = fog_col
    ls.collection_negation = "EXCLUSIVE"
    fade = ls.linestyle.alpha_modifiers.new("Fog fade", "DISTANCE_FROM_CAMERA")
    fade.range_min, fade.range_max = 6.0, 90.0
    fade.invert = True
    scene.frame_set(1)
    return scene


if __name__ == "__main__":
    run_cli(build(), "train_bridge7.blend")
