"""
«واگن آخر ۶ — سیگنال» — straight on from episode 5.  The helicopter flies beside the train.  Rahim orders the
curtains shut; Lena thinks Mom sent it.  I take out the torch (episode 4) and blink at it three times; its
searchlight floods our car; it comes down and lowers an orange bag on a rope to our window.  Inside: a radio,
and Mom's voice — the bridge is broken, stop before the bridge.  Rahim runs to the front, the brakes scream,
we stop just before the broken bridge over a wide river in the fog.  Mom: "on the other side of the river...
I'm waiting for you" — and the radio goes dead.  Lights of a camp on the far bank.

    python part6.py --still 49,361
    python part6.py --render --range 1 2000
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
from lib5 import build_car, build_fog, build_helicopter, give_radio  # noqa: E402

random.seed(66)
T = KEY_OF
GROUND = -1.3
SEAT_CAM = Vector((-0.62, 0.72, 1.22))
WIN_IN = Vector((-1.2, 0.72, 1.42))       # leaning to the open window
HEAD_OUT = Vector((-2.25, 1.05, 1.5))   # head out of the window, looking along the train
HANG = Vector((-2.15, 1.0, 1.55))        # where the bag hangs outside our window
TABLE = Vector((-0.86, 0.12, 0.86))      # the bag on our table


def at(key, k=0):
    return T[key][k]


def yaw_to(d):
    return math.degrees(math.atan2(-d.x, d.y)) % 360


def pitch_to(d):
    return math.degrees(math.atan2(d.z, d.xy.length))


def lerp_yaw(a, b, u):
    d = (b - a + 180) % 360 - 180
    return a + d * u


def lerpv(a, b, u):
    return a.lerp(b, u)


from part6_times import *  # noqa: F401,F403,E402  (story beats, speed, bridge position)


# ================================================================ sets


def build_curtains():
    """Curtain panels over every window; animated shut / open (car coordinates)."""
    m = toon("Curtain shut", (0.98, 0.72, 0.18), 0.12)
    panels = []
    for sx in (-1, 1):
        for yc in range(-11, 12, 2):
            p = box((sx * 1.41, yc, 1.42), (0.04, 1.6, 1.04), m, "Curtain panel")
            panels.append((p, yc, sx))
    return panels


def curtain_state(p, yc, f, u):
    """u = 1 shut, 0 bunched at the pillar."""
    w = lerp(0.14, 1.0, u)
    p.scale = (1, w, 1)
    p.location.y = yc - 0.8 + 0.8 * w      # bunched against the pillar when open
    p.keyframe_insert("scale", frame=f)
    p.keyframe_insert("location", frame=f)


def build_outside():
    """Grey outskirts, then a wide river with a broken iron bridge (outside coordinates)."""
    world = empty("Outside")
    parts = []
    ground_m = toon("Ash ground", (0.44, 0.45, 0.41), 0.1)
    parts.append(box((0, (BR0 - 2 - 150) / 2, GROUND - 0.05), (500, BR0 - 2 + 150, 0.1), ground_m, "Ground"))
    parts.append(box((0, BR0 - 2, (GROUND + RIVER_Z) / 2), (500, 0.6, GROUND - RIVER_Z), toon("Cliff", (0.36, 0.34, 0.32), 0.08), "Near bank"))
    parts.append(box((0, BR1 + 2 + 250, GROUND - 0.05), (500, 500, 0.1), ground_m, "Far ground"))
    parts.append(box((0, BR1 + 2, (GROUND + RIVER_Z) / 2), (500, 0.6, GROUND - RIVER_Z), toon("Cliff", (0.36, 0.34, 0.32), 0.08), "Far bank"))
    parts.append(box((0, (BR0 + BR1) / 2, RIVER_Z), (500, BR1 - BR0 + 4, 0.2), toon("River", (0.16, 0.3, 0.44), 0.3), "River"))
    for p in rails(0, -150, BR0 + GAP0 - BR0, GROUND, "Track"):
        parts.append(p)
    for p in rails(0, GAP1, BR1 + 200, GROUND, "Far track"):
        parts.append(p)
    # dead trees, poles, a few ruined houses on the fields
    bark = toon("Dead tree", (0.22, 0.19, 0.17), 0.05)
    rr = random.Random(4)
    for k in range(60):
        y = rr.uniform(-120, BR0 - 10)
        x = rr.choice((-1, 1)) * rr.uniform(9, 70)
        h = rr.uniform(3, 7)
        parts.append(rod((x, y, GROUND), (x, y, GROUND + h), 0.12, bark, "Tree"))
        for b in range(3):
            a = rr.uniform(0, 6.28)
            z0 = GROUND + h * rr.uniform(0.5, 0.9)
            parts.append(rod((x, y, z0), (x + math.cos(a) * 1.4, y + math.sin(a) * 1.4, z0 + 1.2), 0.05, bark, "Branch"))
    pole = toon("Dead pole", (0.25, 0.22, 0.2), 0.08)
    for y in range(-120, int(BR0 - 4), 22):
        parts.append(rod((4.5, y, GROUND), (4.5, y, GROUND + 7), 0.13, pole, "Pole"))
    grey = [toon(f"Ruin {k}", c, 0.1) for k, c in enumerate([(0.55, 0.55, 0.56), (0.48, 0.47, 0.46), (0.6, 0.57, 0.52)])]
    dark = toon("Dead window", (0.08, 0.08, 0.09), 0.0)
    for k in range(14):
        y = rr.uniform(-100, BR0 - 20)
        x = -rr.uniform(25, 60) if k % 3 else rr.uniform(25, 60)
        w, h = rr.uniform(5, 9), rr.uniform(3, 6)
        parts.append(box((x, y, GROUND + h / 2), (6, w, h), rr.choice(grey), "Ruin"))
        parts.append(box((x + math.copysign(3.02, -x), y, GROUND + h * 0.6), (0.05, 1.2, 1.2), dark, "Ruin window"))
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
        for yy in range(int(BR0 + 10), int(GAP0), 22):
            pass
    for py in (BR0 + 3, GAP1 + 8, GAP1 + 30, GAP1 + 52):
        parts.append(box((0, py, (GROUND - 1.3 + RIVER_Z) / 2), (4.0, 3.0, GROUND - 1.3 - RIVER_Z), toon("Pier", (0.5, 0.48, 0.45), 0.1), "Pier"))
    # broken ends: torn deck slabs hanging into the river, bent girders
    slab = box((0, GAP0 + 5, GROUND - 4.5), (5.4, 11, 0.9), deck_m, "Fallen slab")
    slab.rotation_euler = (D(-42), D(6), 0)
    parts.append(slab)
    slab2 = box((0.5, GAP1 - 4, GROUND - 3.2), (5.4, 8, 0.9), deck_m, "Fallen slab 2")
    slab2.rotation_euler = (D(36), D(-8), 0)
    parts.append(slab2)
    for sx in (-3.2, 3.2):
        parts.append(rod((sx, GAP0, GROUND + 9.0), (sx * 1.15, GAP0 + 8, GROUND + 3.0), 0.3, rust, "Bent girder"))
        parts.append(rod((sx, GAP1, GROUND + 9.0), (sx * 0.9, GAP1 - 7, GROUND + 4.0), 0.3, rust, "Bent girder"))
    steel = toon("Rail steel", (0.55, 0.55, 0.6), 0.25)
    for sx in (-0.72, 0.72):
        parts.append(rod((sx, GAP0 - 0.5, GROUND + 0.2), (sx * 1.6, GAP0 + 3.5, GROUND - 2.5), 0.05, steel, "Bent rail"))
    # the camp on the far bank: tents and warm lamps in the fog
    tent_m = [toon("Tent a", (0.95, 0.55, 0.15), 0.3), toon("Tent b", (0.92, 0.9, 0.85), 0.3)]
    lamp = glow_mat("Camp lamp", (1.0, 0.75, 0.35), 25.0)
    for k in range(16):
        x = -40 + k * 5.5 + rr.uniform(-1, 1)
        y = BR1 + 25 + rr.uniform(0, 30)
        bpy.ops.mesh.primitive_cone_add(radius1=2.0, depth=2.6, location=(x, y, GROUND + 1.3), vertices=6)
        parts.append(finish(bpy.context.object, tent_m[k % 2], "Tent"))
        if k % 2 == 0:
            parts.append(ball((x + 1.5, y - 2, GROUND + 2.6), 0.8, lamp, "Camp light", seg=10))
    parts.append(ball((0, BR1 + 18, GROUND + 1.0), 1.0, glow_mat("Camp fire", (1.0, 0.5, 0.15), 30.0), "Camp fire", seg=12))
    for p in parts:
        parent_keep(p, world)
    # foam streaks on the river, drifting
    foam_m = toon("Foam", (0.85, 0.9, 0.92), 0.4)
    foam = []
    for k in range(30):
        fo = box((rr.uniform(-120, 120), rr.uniform(BR0 + 2, BR1 - 2), RIVER_Z + 0.12), (rr.uniform(4, 12), 0.25, 0.05), foam_m, "Foam")
        parent_keep(fo, world)
        foam.append((fo, fo.location.x))
    return world, foam


def build_train_ahead():
    """The car and the locomotive ahead of ours (car coordinates), seen when I put my head out."""
    parts, _ = wagon_exterior("Loco", 0, 13.3, 23.0, GROUND, 1, [], burnt=0.3)
    red = toon("Train red", (0.78, 0.1, 0.08), 0.3)
    box((0, 23.1, GROUND + 2.2), (3.1, 0.12, 1.6), red, "Loco nose")
    head = glow_mat("Headlight", (1.0, 0.95, 0.8), 6.0)
    for sx in (-0.9, 0.9):
        ball((sx, 23.2, GROUND + 1.9), 0.18, head, "Headlight", seg=12)


def build_searchbeam(fog_col):
    """A soft visible cone from the searchlight to our window, and the white light it throws inside."""
    bpy.ops.mesh.primitive_cone_add(radius1=1.3, radius2=0.25, depth=1.0, location=(0, 0, -0.5), vertices=24)
    c = bpy.context.object
    bpy.ops.object.transform_apply(location=True)
    c.name = "Search beam"
    m = bpy.data.materials.new("Search beam")
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    mix = nt.nodes.new("ShaderNodeMixShader")
    mix.inputs[0].default_value = 0.1
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = (1.0, 0.97, 0.85, 1)
    em.inputs["Strength"].default_value = 2.0
    nt.links.new(tr.outputs[0], mix.inputs[1])
    nt.links.new(em.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs["Surface"])
    c.data.materials.append(m)
    c.visible_shadow = False
    c.rotation_mode = "QUATERNION"
    for col in list(c.users_collection):
        col.objects.unlink(c)
    fog_col.objects.link(c)
    bpy.ops.object.light_add(type="POINT", location=(-1.0, 0.9, 1.5))
    fill = no_cam(bpy.context.object)
    fill.data.energy = 0
    fill.data.color = (1.0, 0.97, 0.9)
    return c, fill


def build_bag():
    orange = toon("Rescue bag", (0.98, 0.45, 0.05), 0.35)
    strap = toon("Bag strap", (0.15, 0.15, 0.16), 0.1)
    root = empty("Bag")
    for o in (box((0, 0, 0), (0.42, 0.26, 0.3), orange, "Bag body", bevel=0.05),
              box((0, 0, 0.16), (0.44, 0.06, 0.03), strap, "Bag band"),
              box((0, 0.135, 0.0), (0.3, 0.01, 0.05), toon("Reflective", (0.92, 0.92, 0.92), 0.6), "Bag stripe"),
              rod((-0.12, 0, 0.16), (0.12, 0, 0.16), 0.02, strap, "Bag handle")):
        parent_keep(o, root)
    root.rotation_mode = "XYZ"
    rope = rod((0, 0, 0), (0, 0, 1), 0.02, toon("Rope", (0.85, 0.8, 0.6), 0.2), "Rope")
    return root, rope


def build_flashlight(cam):
    body = toon("Torch", (0.95, 0.75, 0.1), 0.35)
    root = empty("Torch root")
    parts = [rod((0, 0, 0.02), (0, 0, -0.2), 0.026, body, "Torch body"),
             rod((0, 0, -0.17), (0, 0, -0.215), 0.034, body, "Torch head")]
    lens_off = ball((0, 0, -0.215), 0.03, toon("Torch lens", (0.75, 0.75, 0.7), 0.4), "Torch lens off", scale=(1, 1, 0.3))
    lens_on = ball((0, 0, -0.218), 0.032, glow_mat("Torch lens on", (1.0, 0.97, 0.85), 30.0), "Torch lens on", scale=(1, 1, 0.3))
    for o in parts + [lens_off, lens_on]:
        parent_keep(o, root)
    bpy.ops.object.light_add(type="SPOT", location=(0, 0, -0.23))
    beam = no_cam(bpy.context.object)
    beam.data.energy = 0
    beam.data.spot_size = D(28)
    beam.data.color = (1.0, 0.95, 0.85)
    parent_keep(beam, root)
    parent_local(root, cam)
    return root, lens_on, lens_off, beam


def build_radio(cam):
    root = empty("Radio root")
    black = toon("Rescue radio", (0.1, 0.1, 0.11), 0.15)
    parts = [box((0, 0, 0), (0.075, 0.15, 0.045), black, "Radio body", bevel=0.01),
             rod((0.022, 0.07, 0), (0.022, 0.19, 0), 0.006, black, "Radio antenna"),
             box((0, -0.02, 0.024), (0.055, 0.05, 0.004), toon("Radio grille", (0.3, 0.3, 0.32), 0.1), "Radio grille"),
             box((0, 0.045, 0.024), (0.05, 0.02, 0.004), toon("Radio screen", (0.5, 0.75, 0.45), 0.8), "Radio screen")]
    led = ball((-0.025, 0.065, 0.026), 0.007, glow_mat("Radio LED on", (1.0, 0.25, 0.15), 8.0), "Radio LED")
    for o in parts + [led]:
        parent_keep(o, root)
    parent_local(root, cam)
    return root, led


# ================================================================ animation


def heli_pos(t):
    p = Vector((-34, -18, 10)).lerp(Vector((-19, 4, 8.5)), seg(t, 0.0, 3.2))
    p = p + Vector((0.6 * math.sin(t * 0.7), 0.8 * math.sin(t * 0.43), 0.5 * math.sin(t * 0.9)))
    p = p.lerp(Vector((-7.5, 2.0, 8.4)) + Vector((0.2 * math.sin(t), 0.3 * math.sin(t * 0.8), 0.2 * math.sin(t * 1.3))),
               seg(t, DESC0, DESC1))
    p = p.lerp(Vector((-35, 170, 48)), seg(t, LEAVE_T, LEAVE_T + 9.0))
    return p


def cam_beats():
    """(start, blend seconds, fn(t) -> (yaw, pitch, pos))"""
    def look(p, pos):
        d = p - pos
        return yaw_to(d), max(-50, min(32, pitch_to(d)))

    def heli_look(t, pos=SEAT_CAM):
        y, p = look(heli_pos(t), pos)
        return y, min(p, 14 if pos is SEAT_CAM else 30), pos
    rahim = lambda t: (197, 8, SEAT_CAM)                    # noqa: E731
    lena = lambda t: (163, -6, SEAT_CAM)                    # noqa: E731
    window = lambda t: (112, 2, SEAT_CAM)                   # noqa: E731
    hands = lambda t: (140, -38, SEAT_CAM)                  # noqa: E731
    table = lambda t: (156, -34, SEAT_CAM)                  # noqa: E731
    radio = lambda t: (148, -14, SEAT_CAM)                  # noqa: E731
    bridge = lambda t: (17 + 2 * math.sin(t * 0.3), -1, HEAD_OUT)     # noqa: E731
    camp = lambda t: (lerp(17, 10, seg(t, at("n3"), at("n3", 1))), 0, HEAD_OUT + Vector((0, 0.15, 0.05)))  # noqa: E731

    def bag_look(t):
        y, p = look(bag_world_cache.get("p", HANG), WIN_IN)
        return y, p, WIN_IN

    def blink_look(t):
        y, p = look(heli_pos(t), WIN_IN)
        return y, min(p, 22), WIN_IN

    def rahim_run(t):
        rp = rahim_pos(t) + Vector((0, 0, 1.5))
        y, p = look(rp, SEAT_CAM)
        return y, p, SEAT_CAM

    return [
        (0.0, 0.0, lambda t: heli_look(t, WIN_IN)),
        (at("rahim1") - 0.4, 0.5, rahim),
        (CURTAIN0 - 0.3, 0.4, window),
        (at("lena1") - 0.2, 0.4, lena),
        (at("rahim2") - 0.3, 0.4, rahim),
        (at("n2") - 0.2, 0.6, hands),
        (OPEN0 - 0.2, 0.6, window),
        (BLINKS[0] - 0.5, 0.5, blink_look),
        (at("lena2") - 0.2, 0.35, lena),
        (at("rahim3") - 0.2, 0.35, rahim),
        (at("rahim3") + 1.1, 0.7, lambda t: heli_look(t, WIN_IN)),
        (LOWER1 - 0.6, 0.6, bag_look),
        (TABLE_T - 0.6, 0.6, table),
        (RADIO_T - 0.3, 0.6, radio),
        (at("lena3") - 0.15, 0.3, lena),
        (at("mom2") - 0.2, 0.4, radio),
        (at("rahim4") - 0.3, 0.35, rahim),
        (RUN0, 0.3, rahim_run),
        (BRAKE0 - 0.3, 0.8, bridge),
        (at("lena4") - 0.3, 0.5, lena),
        (at("n3") - 0.8, 1.2, camp),
    ]


bag_world_cache = {}


def rahim_pos(t):
    return Vector((0.1, -1.7, 0)).lerp(Vector((0.1, 13.5, 0)), seg(t, RUN0, RUN0 + 2.6))


def cam_at(t, beats):
    cur = 0
    for i, b in enumerate(beats):
        if b[0] <= t:
            cur = i
    y1, p1, pos1 = beats[cur][2](t)
    if cur == 0:
        return y1, p1, pos1
    y0, p0, pos0 = beats[cur - 1][2](t)
    u = seg(t, beats[cur][0], beats[cur][0] + max(0.01, beats[cur][1]))
    return lerp_yaw(y0, y1, u), lerp(p0, p1, u), lerpv(pos0, pos1, u)


def cam_matrix(loc, rot):
    return loc, Euler(rot, "XYZ").to_matrix()


def build():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.fps = FPS
    scene.frame_start, scene.frame_end = 1, int(END * FPS)
    scene.frame_step = 2

    build_car()
    panels = build_curtains()
    outside, foam = build_outside()
    build_train_ahead()
    heli, rotor = build_helicopter()
    spot = [o for o in heli.children if o.type == "LIGHT"][0]
    spot.data.energy = 0
    target = empty("Search target", (-1.3, 0.9, 1.3))
    con = spot.constraints.new("TRACK_TO")
    con.target = target
    con.track_axis = "TRACK_NEGATIVE_Z"
    con.up_axis = "UP_Y"
    lamp_on = [o for o in heli.children if o.name.startswith("Searchlight")]
    bag, rope = build_bag()
    fog_col = build_fog()
    beam_cone, fill = build_searchbeam(fog_col)
    lena, rahim = make_lena(), make_rahim()
    give_radio(rahim)
    passengers = [make_extra(i, 0.95) for i in (1, 3, 6)]
    cam = make_camera(scene)
    arms = POVArms(cam)
    torch, lens_on, lens_off, beam = build_flashlight(cam)
    radio, led = build_radio(cam)
    beats = cam_beats()
    rs = random.Random(5)
    shake = [(rs.uniform(-1, 1), rs.uniform(-1, 1), rs.uniform(-1, 1)) for _ in range(int(END * FPS) + 3)]

    # curtains: keys only where they change
    for p, yc, sx in panels:
        ours = (sx == -1 and yc == 1)
        for tt, u in ((0, 0.0), (CURTAIN0, 0.0), (CURTAIN0 + 0.8 + 0.05 * abs(yc), 1.0)):
            curtain_state(p, yc, max(1, int(tt * FPS) + 1), u)
        if ours:
            curtain_state(p, yc, int(OPEN0 * FPS) + 1, 1.0)
            curtain_state(p, yc, int((OPEN0 + 0.7) * FPS) + 1, 0.0)

    for f in range(1, int(END * FPS) + 1):
        t = (f - 1) / FPS
        s_now = travelled(t)
        outside.location.y = -s_now
        outside.keyframe_insert("location", frame=f)
        v = speed(t)
        for fo, x0 in foam:
            fo.location.x = x0 + ((t * 2.5) % 20) - 10
            fo.keyframe_insert("location", frame=f)

        # ---------------- helicopter, searchlight
        hp = heli_pos(t)
        heli.location = hp
        bank = D(-8) * seg(t, LEAVE_T, LEAVE_T + 2)
        heli.rotation_euler = (D(-5 + 2 * math.sin(t * 0.8)), D(3 * math.sin(t * 0.6)) + bank,
                               D(lerp(0, -25, seg(t, DESC0, DESC1)) * (1 - seg(t, LEAVE_T, LEAVE_T + 3))))
        heli.keyframe_insert("location", frame=f)
        heli.keyframe_insert("rotation_euler", frame=f)
        rotor.rotation_euler = (0, 0, t * 25.0)
        rotor.keyframe_insert("rotation_euler", frame=f)
        lit = SEARCH_T <= t < DESC0 + 1.0
        spot.data.energy = (15000 * min(1.0, (t - SEARCH_T) / 0.15)) if lit else 0.0
        spot.data.keyframe_insert("energy", frame=f)
        show(lamp_on, f, True)
        k_lit = min(1.0, (t - SEARCH_T) / 0.15) if lit else 0.0
        k_lit *= 1 - 0.35 * seg(t, SEARCH_T + 0.4, SEARCH_T + 1.5)
        lamp_w = hp + Vector((0, 0, -1.6))
        dvec = Vector((-1.3, 0.9, 1.3)) - lamp_w
        beam_cone.location = lamp_w
        beam_cone.rotation_quaternion = Vector((0, 0, -1)).rotation_difference(dvec)
        beam_cone.scale = (1, 1, dvec.length) if k_lit > 0 else (0.001, 0.001, 0.001)
        beam_cone.keyframe_insert("location", frame=f)
        beam_cone.keyframe_insert("rotation_quaternion", frame=f)
        beam_cone.keyframe_insert("scale", frame=f)
        fill.data.energy = 120 * k_lit
        fill.data.keyframe_insert("energy", frame=f)

        # ---------------- the bag on the rope
        belly = hp + Vector((0, 0, -2.4))
        if t < LOWER0:
            bp = belly + Vector((0, 0, -0.3))
        elif t < GRAB_T:
            hang = belly.lerp(HANG, seg(t, LOWER0, LOWER1))
            sw = 0.25 * math.sin(t * 2.6) * (1 - 0.6 * seg(t, LOWER1, GRAB_T))
            bp = hang + Vector((sw * 0.4, sw, 0))
        else:
            bp = None   # set from the hands below
        bag_world_cache["p"] = bp if bp is not None else bag_world_cache.get("p", HANG)

        # ---------------- camera
        yaw, pitch, pos = cam_at(t, beats)
        amp = 0.05 + 0.08 * min(1.0, v / 9.0)
        if SEARCH_T <= t < SEARCH_T + 0.6:
            amp += 0.8 * (1 - (t - SEARCH_T) / 0.6)
        if BRAKE0 <= t < BRAKE1:
            amp += 2.2 * math.sin(math.pi * (t - BRAKE0) / (BRAKE1 - BRAKE0))
        if BRAKE1 <= t < BRAKE1 + 0.8:
            amp += 1.8 * (1 - (t - BRAKE1) / 0.8)
        if DESC0 <= t < LEAVE_T:
            amp += 0.25                                     # rotor wash
        sx_, sy_, sz_ = shake[f]
        rot = (D(90 + pitch + sx_ * amp), D(sy_ * amp * 0.6), D(yaw + sz_ * amp))
        cam.location = pos
        cam.rotation_euler = rot
        cam.keyframe_insert("location", frame=f)
        cam.keyframe_insert("rotation_euler", frame=f)
        M = Euler(rot, "XYZ").to_matrix()

        # ---------------- my hands: torch, curtain, the bag, the radio
        L, R = (-0.3, -0.42, -0.46), (0.28, -0.42, -0.46)
        if OPEN0 - 0.2 <= t < OPEN0 + 0.9:                  # pull the curtain aside
            u = seg(t, OPEN0, OPEN0 + 0.7)
            L = (lerp(-0.05, -0.38, u), -0.02, -0.62)
        torch_vis = at("n2") + 0.4 <= t < SEARCH_T + 1.2
        if torch_vis:
            up = seg(t, at("n2") + 0.4, at("n2") + 1.4)
            out = seg(t, OPEN0 + 0.5, BLINKS[0] - 0.2)
            R = tuple(lerp(a, b, up) for a, b in zip((0.25, -0.5, -0.4), (0.1, -0.22, -0.45)))
            R = tuple(lerp(a, b, out) for a, b in zip(R, (0.12, -0.08, -0.62)))
        if LOWER1 - 0.4 <= t < TABLE_T + 0.4:               # reach out, grab, pull in
            reach = seg(t, LOWER1 - 0.4, GRAB_T)
            pull = seg(t, GRAB_T + 0.1, TABLE_T)
            hz = lerp(-0.72, -0.5, pull)
            L = (lerp(L[0], -0.14, reach), lerp(L[1], -0.08, reach) - 0.15 * pull, lerp(L[2], hz, reach))
            R = (lerp(R[0], 0.14, reach), lerp(R[1], -0.08, reach) - 0.15 * pull, lerp(R[2], hz, reach))
        if TABLE_T + 0.4 <= t < RADIO_T + 0.3:              # hands in the bag
            L, R = (-0.15, -0.35, -0.5), (0.12, -0.33, -0.5)
        if t >= RADIO_T - 0.2:
            lift = seg(t, RADIO_T - 0.2, RADIO_T + 0.6)
            low = seg(t, at("lena3") - 0.2, at("lena3")) * (1 - seg(t, at("mom2") - 0.3, at("mom2")))
            low = max(low, seg(t, BRAKE0 - 0.4, BRAKE0 + 0.4))
            Rr = (lerp(0.05, 0.18, low), lerp(-0.12, -0.32, low), lerp(-0.42, -0.5, low))
            R = tuple(lerp(a, b, lift) for a, b in zip((0.12, -0.33, -0.5), Rr))
        if t >= BRAKE0 - 0.4:                                # bracing on the window sill
            L = (-0.32, -0.38, -0.45)
        arms.set(f, "L", L)
        arms.set(f, "R", R)

        # torch in the right hand, beam on in three blinks
        torch.location = Vector(R) + Vector((0, 0.02, -0.05))
        torch.keyframe_insert("location", frame=f)
        show([torch], f, torch_vis)
        on = any(b <= t < b + 0.42 for b in BLINKS)
        show([lens_on], f, torch_vis and on)
        beam.data.energy = 40.0 if (torch_vis and on) else 0.0
        beam.data.keyframe_insert("energy", frame=f)
        # radio in the right hand
        radio_vis = t >= RADIO_T
        radio.location = Vector(R) + Vector((0, 0.07, -0.04))
        radio.keyframe_insert("location", frame=f)
        show([radio], f, radio_vis)
        talking_radio = any(at(k) - 0.6 <= t <= at(k, 1) + 0.3 for k in ("mom1", "mom2", "mom3"))
        show([led], f, radio_vis and t < DEAD_T and (talking_radio or int(t * 2) % 2 == 0))

        # the bag follows my hands once grabbed, then sits on the table
        if bp is None:
            hands_mid = Vector(((L[0] + R[0]) / 2, (L[1] + R[1]) / 2 - 0.12, (L[2] + R[2]) / 2 - 0.08))
            bw = pos + M @ hands_mid
            if t >= TABLE_T:
                bw = bw.lerp(TABLE, seg(t, TABLE_T, TABLE_T + 0.4))
            bp = bw
            bag_world_cache["p"] = bp
        bag.location = bp
        bag.rotation_euler = (0, 0, D(10 * math.sin(t * 1.7)) if t < GRAB_T else D(20))
        bag.keyframe_insert("location", frame=f)
        bag.keyframe_insert("rotation_euler", frame=f)
        # rope: belly -> bag while it hangs; let go just after the grab and pulled up
        top = belly
        low_end = bp + Vector((0, 0, 0.17)) if t < GRAB_T + 0.5 else bp.lerp(belly, seg(t, GRAB_T + 0.5, GRAB_T + 2.2))
        rope_vis = LOWER0 - 0.2 <= t < GRAB_T + 2.2
        place_rod(rope, top, low_end)
        rope.scale = (1, 1, max(0.001, (low_end - top).length)) if rope_vis else (0.001, 0.001, 0.001)
        rope.keyframe_insert("location", frame=f)
        rope.keyframe_insert("rotation_quaternion", frame=f)
        rope.keyframe_insert("scale", frame=f)

        # ---------------- Lena across the table
        win = seg(t, at("lena1") - 0.4, at("lena1")) * (1 - seg(t, at("rahim2"), at("rahim2") + 0.6))
        joy = seg(t, at("lena2") - 0.4, at("lena2")) * (1 - seg(t, at("rahim3") + 0.5, at("rahim3") + 1.2))
        grab_r = seg(t, at("lena3") - 0.3, at("lena3")) * (1 - seg(t, at("mom2") + 0.5, at("mom2") + 1.2))
        cry = seg(t, at("lena4") - 0.3, at("lena4"))
        scared = seg(t, BRAKE0 - 0.3, BRAKE0 + 0.3) * (1 - seg(t, BRAKE1, BRAKE1 + 1.0))
        out = seg(t, at("n3") - 0.5, at("n3") + 1.0)
        lk_yaw = lerp(lerp(lerp(0, 60, win), 70, joy), 5, grab_r)
        lk_yaw = lerp(lk_yaw, 70, out)
        lk_pitch = lerp(lerp(lerp(2, 18, win), 30, joy), -18, grab_r)
        lk_pitch = lerp(lerp(lk_pitch, -18, cry), 5, out)
        lena.pose(f, t, Vector((-1.12, -0.75, 0)), facing=0, sit=1, seat_h=0.5, lean=0,
                  look=(lk_yaw, lk_pitch), hug=max(0.5 * cry, 0.6 * scared) * (1 - out),
                  worry=lerp(lerp(1.4, 0.3, max(joy, grab_r)), 2.2, max(cry, scared)),
                  reach=(150, -20) if joy > 0.2 else ((70 + 15 * grab_r, -5) if grab_r > 0.2 else None),
                  reach2=(150, 20) if joy > 0.2 else ((75, 5) if grab_r > 0.4 else None))
        # ---------------- Rahim in the aisle; runs to the front
        rp = rahim_pos(t)
        present = at("rahim1") - 1.0 <= t < RUN0 + 2.7
        if present:
            running = seg(t, RUN0, RUN0 + 0.3)
            rahim.pose(f, t, rp, facing=lerp(0, 0, running) if running < 0.5 else 0, run=running, run_rate=1.8,
                       reach=(140, 25) if at("rahim1") <= t < at("rahim1", 1) else
                       ((95, 5) if at("rahim2") <= t < at("rahim2", 1) else
                        ((130, 15) if at("rahim3") <= t < at("rahim3", 1) else None)),
                       reach2=(105, 10) if running < 0.5 else None,
                       look=(lerp(0, -35, seg(t, at("rahim3"), at("rahim3") + 0.5) * (1 - seg(t, at("rahim3", 1), at("rahim3", 1) + 0.5))), 8),
                       worry=1.8)
        else:
            rahim.pose(f, t, Vector((0.1, -40, 0)), facing=0)
        for i, (e, p0) in enumerate(zip(passengers, (Vector((-0.62, -3.75, 0)), Vector((0.62, -3.75, 0)),
                                                       Vector((1.12, 3.75, 0))))):
            e.pose(f, t, p0, facing=0, sit=1, seat_h=0.5, lean=0,
                   look=(15 * math.sin(i + t * 0.2) + (40 if lit else 0), -5 + (15 if lit else 0)),
                   worry=1.6, hug=0.4 * scared)

    # the near fog sheets would stand like a grey wall in the head-out shots: drop them there
    cut = int((BRAKE0 - 0.6) * FPS) + 1
    for v_ in fog_col.objects:
        if v_.name.startswith("Fog veil") and abs(v_.location.x) <= 12:
            sc0 = v_.scale.copy()
            v_.keyframe_insert("scale", frame=cut - 1)
            v_.scale = (0.001, 0.001, 0.001)
            v_.keyframe_insert("scale", frame=cut)
            v_.scale = sc0
            v_.keyframe_insert("scale", frame=1)
    bpy.ops.object.light_add(type="SUN", rotation=(D(60), D(10), D(70)))
    sun = bpy.context.object
    sun.data.energy = 1.2
    sun.data.color = (0.85, 0.86, 0.92)
    bpy.ops.object.light_add(type="POINT", location=(-0.3, -0.4, 1.5))
    no_cam(bpy.context.object).data.energy = 25
    setup_render(scene, sky=(0.66, 0.66, 0.68), sky_strength=1.0)
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
    run_cli(build(), "train_bridge6.blend")
