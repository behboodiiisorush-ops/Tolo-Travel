"""
«پناهگاه ۴ — چراغ‌های جاده» — vertical POV short, straight on from the end of episode 3.

The bus stands broken in the forest at night.  The beast walks up to it; the car behind it blasts its horn and a
roof floodlight blazes on — the beast screams and runs into the trees, the dogs after it.  The car rolls up; two
figures in white suits with dark glass visors get out and talk at the bus door, then go back to their car.  On our
walkie-talkie we overhear them («نمونه‌ها»); in a cage on their roof rack something with glowing eyes moves.  Lena is
gone from her seat — she is outside holding a stranger's hand, walking to the car.  The floodlight goes out and eyes
light up all round the forest.

    ../cast/bpy.sh scene4.py --save            -> scene4.blend
    ../cast/bpy.sh scene4.py --still 101,1201   -> test/s4_XXXX.png
"""
import math
import os
import random
import sys

import bpy
from mathutils import Euler, Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from world import *  # noqa: F401,F403,E402
from world import W, X_STOP, ROAD_Y, BUS_Y, BUS_HW, FLOOR, EYE, N, FPS  # noqa: E402
from pcommon import *  # noqa: F401,F403,E402
from captions import END, KEY_OF  # noqa: E402

random.seed(4)


def at(k, i=0):
    return KEY_OF[k][i]


def yaw_to(d):
    return math.degrees(math.atan2(-d.x, d.y)) % 360


def look(pos, target):
    d = Vector(target) - pos
    return yaw_to(d), math.degrees(math.atan2(d.z, d.xy.length))


def lerp_yaw(a, b, u):
    return a + ((b - a + 180) % 360 - 180) * u


def win(t, a, b, ramp=0.4):
    """0..1 envelope: up over `ramp` before a, down over `ramp` after b"""
    return seg(t, a - ramp, a) * (1 - seg(t, b, b + ramp))


# ================================================================== story times
T_HORN = at("lena1", 1) + 0.5           # the car blasts its horn
T_FLOOD = T_HORN + 0.5                  # the roof floodlight blazes on; the beast screams and runs
T_CAR0, T_CAR1 = at("n3") - 2.4, at("n3") + 0.2       # the car rolls up to the bus and stops
T_OUT_CAR = at("n3") + 0.6              # the two strangers get out
T_AT_DOOR = at("str1a") - 0.2           # they stand at the bus door
T_DOOR = at("str1a") - 1.0              # the rescuer folds the door open
T_BACK0, T_BACK1 = at("n4") - 1.4, at("n4") + 2.2     # they walk back to their car
T_LENA_GO = at("me4") - 0.5             # Lena slips out (we are looking at the cage)
T_WALK0, T_WALK1 = at("n6") - 0.6, END  # Lena and stranger 1, hand in hand, to the car
T_DARK = at("n7") + 0.3                 # floodlight off, eyes all round the forest

CAR_X0, CAR_X1 = X_STOP - 30.0, X_STOP - 12.5   # car front-to-bus distance before / after it rolls up
CAR_Y = ROAD_Y - 2.0


def car_x(t):
    return lerp(CAR_X0, CAR_X1, seg(t, T_CAR0, T_CAR1))


DOOR_OUT = W(0.9, BUS_HW + 1.0, 0)          # outside the bus door
ROW = lambda k: 3.0 + 1.05 * k               # noqa: E731
S_LENA, S_MOM, S_OLD = (ROW(2), 0.38), (ROW(2), -0.55), (ROW(1), 0.6)
S_PAX = [(ROW(4), 0.6), (ROW(4), -0.6), (ROW(5), 0.6), (ROW(6), -0.6), (ROW(3), -0.6)]


def sit_world(s, dz=0.0):
    return W(s[0], s[1], FLOOR - 0.05 + dz)


# ================================================================== new pieces
def make_stranger(name, s=1.05):
    """white protective suit, white gloves and boots, a round white helmet with a dark glass visor: no face."""
    p = Person(name, s, 0.21, dict(skin=(0.85, 0.65, 0.5), top=(0.93, 0.94, 0.95), pants=(0.93, 0.94, 0.95),
                                   shoes=(0.85, 0.86, 0.88), hair=(0.9, 0.9, 0.9), iris=(0.2, 0.2, 0.2), brow=1.0,
                                   lid=0.3, gloves=(0.97, 0.97, 0.98), belt=(0.6, 0.62, 0.65), width=1.08))
    R, hc, head = p.R, p.head_c, p.p["head"]
    helm = toon(f"{name} helmet", (0.95, 0.95, 0.96), 0.15)
    visor = bpy.data.materials.new(f"{name} visor")
    visor.use_nodes = True
    bsdf = visor.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.01, 0.012, 0.02, 1)
    bsdf.inputs["Roughness"].default_value = 0.05
    for key in ("Specular IOR Level", "Specular"):
        if key in bsdf.inputs:
            bsdf.inputs[key].default_value = 1.0
    p.add(ball(hc + Vector((0, -0.05 * R, 0.08 * R)), 1.32 * R, helm, "helmet", scale=(1.02, 1.02, 1.05)), head)
    p.add(ball(hc + Vector((0, 0.66 * R, -0.02 * R)), 1.0 * R, visor, "visor", scale=(1.0, 0.75, 0.8)), head)
    p.add(box((0, 0.17, 0.86 * p.s + 0.29 * p.s), (0.5, 0.02, 0.06), toon("Reflective", (0.7, 0.72, 0.75), 0.4),
              "suit stripe"), p.p["torso"])
    return p


def car_extras(root):
    """a roof rack with a bar floodlight and a wire cage with something alive in it."""
    x0, y0 = root.location.x, root.location.y          # built round the car's rest position, then keyed
    dark = toon("Rack", (0.08, 0.08, 0.09), 0.02)
    flood_m = glow_mat("Floodlight", (1.0, 0.98, 0.92), 0.0)
    parts = [box((x0 - 0.3, y0, 2.0), (2.0, 1.6, 0.06), dark, "Roof rack")]
    for dy in (-0.45, 0.0, 0.45):
        parts.append(box((x0 + 0.6, y0 + dy, 2.18), (0.1, 0.36, 0.26), flood_m, "Floodlight lamp"))
    parts.append(box((x0 + 0.55, y0, 2.18), (0.08, 1.4, 0.34), dark, "Floodlight bar"))
    bpy.ops.object.light_add(type="SPOT", location=(x0 + 0.8, y0, 2.2), rotation=(0, D(-84), 0))
    flood = bpy.context.object
    flood.data.energy = 0
    flood.data.spot_size = D(55)
    flood.data.spot_blend = 0.3
    flood.data.color = (1.0, 0.97, 0.9)
    flood.data.shadow_soft_size = 0.2
    parts.append(flood)
    # the cage on the back of the rack
    bars = toon("Cage bars", (0.35, 0.36, 0.38), 0.1)
    cx, cz, s = x0 - 0.9, 2.03, 1.0
    for dx in (-0.45, 0.45):
        for dy in (-0.55, 0.55):
            parts.append(rod((cx + dx, y0 + dy, cz), (cx + dx, y0 + dy, cz + s), 0.03, bars, "Cage post"))
    for k in range(7):
        y = y0 - 0.55 + k * 0.183
        parts.append(rod((cx + 0.45, y, cz), (cx + 0.45, y, cz + s), 0.015, bars, "Cage bar"))
        parts.append(rod((cx - 0.45, y, cz), (cx - 0.45, y, cz + s), 0.015, bars, "Cage bar"))
    parts.append(box((cx, y0, cz + s), (0.95, 1.15, 0.04), bars, "Cage top"))
    fur = toon("Caged fur", (0.03, 0.025, 0.03), 0.0)
    thing = empty("Caged thing", (cx, y0, cz + 0.35))
    body = ball((cx, y0, cz + 0.35), 0.35, fur, "Caged body", scale=(1.0, 1.2, 0.9))
    eye_m = glow_mat("Caged eyes", (1.0, 0.96, 0.9), 0.0)
    eyes = [ball((cx + 0.36, y0 + dy, cz + 0.52), 0.08, eye_m, "Caged eye", seg=10) for dy in (-0.14, 0.14)]
    for o in [body] + eyes:
        parent_keep(o, thing)
    parts.append(thing)
    for o in parts:
        if o.parent is None:
            parent_keep(o, root)
    return flood, flood_m, eye_m, thing


def forest_eyes(n=40):
    """pairs of eyes deep among the trees on both sides and far down the road (they light up at the end)."""
    rnd = random.Random(44)
    m = glow_mat("Forest eyes", (1.0, 0.85, 0.3), 0.0)
    out = []
    for k in range(n):
        side = 1 if k % 2 else -1
        x = X_STOP - 6 - rnd.uniform(0, 34) if k % 4 else X_STOP - 22 - rnd.uniform(0, 20)
        y = ROAD_Y + side * rnd.uniform(5.0, 11.0) if k % 4 else ROAD_Y + rnd.uniform(-3.5, 3.5)
        z = rnd.uniform(0.4, 1.2)
        for dx in (-0.1, 0.1):
            out.append(ball((x, y + dx * 1.6, z), 0.085, m, "Forest eye", seg=8))
    return m


# ================================================================== build
def build():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.fps = FPS
    scene.frame_start, scene.frame_end = 1, N
    scene.frame_step = 2

    print("build: people + bus", flush=True)
    lena, mom = make_lena(), make_mom()
    resc, old = make_rescuer(), make_oldman()
    s1, s2 = make_stranger("Stranger 1", 1.06), make_stranger("Stranger 2", 1.0)
    pax = [make_extra(i, 0.95) for i in (0, 1, 4, 6, 2)]
    puppet_mask(lena)
    puppet_mask(mom)
    puppet_mask(old)
    for i, pp in enumerate(pax):
        puppet_mask(pp, "dust" if i % 2 else "resp")
    BUSR, leaves, bus_lights, beam = bus()
    BUSR.location = (X_STOP, BUS_Y, 0)
    print("build: world", flush=True)
    ground_and_road()
    heads, far_spot, far_root = far_car()
    flood, flood_m, cage_eye_m, caged = car_extras(far_root)
    beast = make_beast()
    forest()
    feye_m = forest_eyes()
    dogs = [make_dog(i) for i in range(6)]

    print("build: animation", flush=True)
    cam = make_camera(scene)
    cam.data.lens = 13
    arms = POVArms(cam)
    arms.reach = 1.1
    radio_root = empty("POV radio")
    parent_local(radio_root, cam)
    rmat = toon("Radio", (0.18, 0.2, 0.18), 0.1)
    rparts = [box((0, 0, 0), (0.11, 0.05, 0.24), rmat, "POV radio body", bevel=0.01),
              rod((0.035, 0, 0.1), (0.035, 0, 0.3), 0.008, rmat, "POV radio antenna"),
              ball((-0.03, 0.028, 0.09), 0.01, glow_mat("Radio LED", (0.2, 1.0, 0.3), 6.0), "POV radio led", seg=8)]
    for o in rparts:
        parent_local(o, radio_root)
    radio_root.rotation_mode = "XYZ"
    radio_root.rotation_euler = (D(-70), 0, D(10))
    radio_root.location = (0.05, -0.32, -0.42)
    RADIO = [(at("n4") - 0.6, at("me3", 1) + 0.4)]
    show_at(rparts, RADIO)
    flt = toon("Respirator filter", (0.42, 0.48, 0.32), 0.12)
    for sx in (-1, 1):                      # our own mask's filters low in the view
        parent_local(rod((sx * 0.2, -0.55, -0.3), (sx * 0.27, -0.62, -0.26), 0.07, flt, "POV mask filter"), cam)

    rnd = random.Random(3)
    shake = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(-1, 1)) for _ in range(N + 3)]
    broot, bhead, blimbs, bglow = beast
    front = W(1.5, 0.35, FLOOR + EYE + 0.05)                  # standing just behind the windshield
    duck = W(1.7, 0.3, FLOOR + 0.95)                          # crouched behind the dashboard
    aisle = W(2.3, 0.05, FLOOR + EYE)                         # in the aisle by the door
    at_door = W(1.0, BUS_HW - 0.45, FLOOR + EYE - 0.05)       # at the open door
    seat_me = W(ROW(2) - 0.05, 0.8, FLOOR + 1.12)

    for f in range(1, N + 1, 2):
        t = (f - 1) / FPS
        cx = car_x(t)
        # ---------------- the car, its floodlight, the cage
        far_root.location = (cx, CAR_Y, 0)
        far_root.keyframe_insert("location", frame=f)
        lit = T_FLOOD <= t < T_DARK
        far_spot.data.energy = 0 if t >= T_DARK else 2500
        far_spot.data.keyframe_insert("energy", frame=f)
        show(heads, f, t < T_DARK)
        k = seg(t, T_FLOOD, T_FLOOD + 0.15) if lit else 0.0
        flood.data.energy = 250000 * k
        flood.data.keyframe_insert("energy", frame=f)
        flood_m.node_tree.nodes["Emission"].inputs["Strength"].default_value = 2500 * k
        flood_m.node_tree.nodes["Emission"].inputs["Strength"].keyframe_insert("default_value", frame=f)
        cage_eye_m.node_tree.nodes["Emission"].inputs["Strength"].default_value = \
            120 * seg(t, at("str1d") - 0.5, at("str1d")) * (0.6 + 0.4 * abs(math.sin(t * 1.7)))
        cage_eye_m.node_tree.nodes["Emission"].inputs["Strength"].keyframe_insert("default_value", frame=f)
        caged.rotation_euler = (D(8) * math.sin(t * 3.1), D(6) * math.sin(t * 2.3), D(25) * math.sin(t * 1.3))
        caged.keyframe_insert("rotation_euler", frame=f)
        feye_m.node_tree.nodes["Emission"].inputs["Strength"].default_value = 90 * seg(t, T_DARK + 0.3, T_DARK + 2.0)
        feye_m.node_tree.nodes["Emission"].inputs["Strength"].keyframe_insert("default_value", frame=f)
        beam.data.energy = 900
        beam.data.keyframe_insert("energy", frame=f)
        # ---------------- the bus door (the rescuer folds it open for the strangers)
        door_open = seg(t, T_DOOR, T_DOOR + 0.6)
        for piv, j in leaves:
            piv.rotation_euler = (0, 0, (-1 if j == 0 else 1) * D(80) * door_open)
            piv.keyframe_insert("rotation_euler", frame=f)

        # ---------------- the beast: walks up, screams in the light, runs into the trees
        if t < T_FLOOD + 0.4:
            u = seg(t, 0, T_FLOOD)
            bx, by = X_STOP - 9.0 + 3.0 * u, ROAD_Y + 2.6
            yaw_b, run = 0.0, 1.0
            rear = seg(t, T_FLOOD, T_FLOOD + 0.3)
        else:
            u = seg(t, T_FLOOD + 0.4, T_FLOOD + 2.2)
            bx, by = X_STOP - 6.0 - 10.0 * u, ROAD_Y + 2.6 + 14.0 * u
            yaw_b, run, rear = 120.0 * seg(t, T_FLOOD + 0.4, T_FLOOD + 0.8), 2.2, 0.0
        gone = t > T_FLOOD + 2.4
        show([broot], f, not gone)
        step = t * 2.6 * run
        broot.location = (bx, by, 0.06 * abs(math.sin(step * math.pi)))
        broot.rotation_euler = (D(3) * math.sin(step * math.pi), D(-25) * rear, D(yaw_b) + D(6) * math.sin(step * .5))
        broot.keyframe_insert("location", frame=f)
        broot.keyframe_insert("rotation_euler", frame=f)
        for sh, hip, side in blimbs:
            ph = step * math.pi + (0 if side < 0 else math.pi)
            sh.rotation_euler = (0, D(25) * math.sin(ph) - D(60) * rear, 0)
            hip.rotation_euler = (0, D(-22) * math.sin(ph + math.pi), 0)
            sh.keyframe_insert("rotation_euler", frame=f)
            hip.keyframe_insert("rotation_euler", frame=f)
        bhead.rotation_euler = (D(8) * math.sin(step * 0.7), D(-10) - D(35) * rear, 0)
        bhead.keyframe_insert("rotation_euler", frame=f)
        bglow.data.energy = 0 if gone else 60 + 25 * math.sin(t * 7.0) + 120 * rear
        bglow.data.keyframe_insert("energy", frame=f)
        # ---------------- the dogs: round the bus, then off into the trees with the beast
        for i, (root, legs, ph0) in enumerate(dogs):
            ang = ph0 + i * 1.05
            home = Vector((X_STOP + 2 + 1.6 * i, BUS_Y + (1 if i % 2 else -1) * (BUS_HW + 2.0 + 0.5 * (i % 3)), 0))
            flee = seg(t, T_FLOOD + 0.2 + 0.1 * i, T_FLOOD + 2.0 + 0.1 * i)
            away = Vector((home.x - 8 - 2 * i, home.y + (1 if i % 2 else -1) * 16, 0))
            p = home.lerp(away, flee)
            p.z = 0.0 if flee > 0 else 0.25 * max(0.0, math.sin(t * 5 + ang))
            root.location = p if flee < 0.98 else Vector((0, 0, -50))
            root.rotation_euler = (0, 0, D(180 + (30 if i % 2 else -30) * flee) + 0.3 * math.sin(t + ang)
                                   if flee > 0 else D(90 if i % 2 else 270))
            root.keyframe_insert("location", frame=f)
            root.keyframe_insert("rotation_euler", frame=f)
            for piv, lx, ly in legs:
                piv.rotation_euler = (0, D(35) * math.sin(t * 14 + ang + (lx > 0) * math.pi + (ly > 0)), 0)
                piv.keyframe_insert("rotation_euler", frame=f)

        # ---------------- the strangers
        car_door = Vector((cx + 0.2, CAR_Y + 1.3, 0))
        for who, st in enumerate((s1, s2)):
            stand = DOOR_OUT + Vector((-0.4 - 0.3 * who, 0.25 + 0.7 * who, 0))
            by_car = Vector((cx - 1.2 - 0.6 * who, CAR_Y + 1.4 + 0.5 * who, 0))
            spawn = car_door + Vector((0.0, 0.9 * who, 0))
            if t < T_OUT_CAR:
                st.pose(f, t, Vector((cx, CAR_Y, -10)), facing=270, talk=False)
            elif t < T_AT_DOOR:                                   # out of the car, up to the bus door
                u = seg(t, T_OUT_CAR, T_AT_DOOR)
                pp = spawn.lerp(stand, u)
                st.pose(f, t, pp, facing=yaw_to(stand - spawn) if u < 0.98 else 180, run=0.4 * (u < 0.98),
                        run_rate=1.2, lean=-4)
            elif t < T_BACK0:                                     # talking at the door
                turn = win(t, at("str2a"), at("str2a", 1)) if who == 1 else 0.0
                st.pose(f, t, stand, facing=lerp_yaw(200 - 20 * who, 180, turn), look=(0, 8), worry=0.0,
                        reach=(lerp(10, 70, win(t, at("str1c"), at("str1c", 1))), 0) if who == 0 else None)
            elif who == 1 or t < at("me4"):                       # back to the car, waiting by it
                u = seg(t, T_BACK0, T_BACK1)
                pp = stand.lerp(by_car, u)
                st.pose(f, t, pp, facing=yaw_to(by_car - stand) if u < 0.98 else 90, run=0.4 * (u < 0.98),
                        run_rate=1.2, lean=-4)
            elif t < T_WALK0:                                     # stranger 1 comes back for Lena
                u = seg(t, at("me4"), T_WALK0)
                pp = by_car.lerp(stand, u)
                st.pose(f, t, pp, facing=yaw_to(stand - by_car) if u < 0.98 else 200, run=0.4 * (u < 0.98),
                        run_rate=1.2, reach2=(35, -20) if u > 0.9 else None)
            else:                                                 # and walks her, hand in hand, to the car
                u = seg(t, T_WALK0, T_WALK1 + 4)
                pp = stand.lerp(car_door + Vector((0.6, 0.3, 0)), u)
                turn_head = win(t, at("str1e"), END, 0.4)
                st.pose(f, t, pp, facing=yaw_to(car_door - stand), run=0.35, run_rate=1.1,
                        look=(lerp(0, 120, turn_head), 0), reach2=(35, -20))
        # ---------------- inside: Lena, Mom, the rescuer, the old man, passengers
        ducking = win(t, at("resc1"), at("n2", 1) - 1.2, 0.3)
        # Lena: on her seat; slips out to the stranger while we look at the cage; walks with him to the car
        if t < T_LENA_GO:
            lena.pose(f, t, sit_world(S_LENA), facing=90 + lerp(0, 60, win(t, at("lena2"), at("lena2", 1))),
                      sit=1, seat_h=0.5, lean=0, crouch=0.7 * ducking, hug=0.6 * ducking + 0.4,
                      look=(lerp(0, 60, win(t, at("mom1"), at("lena2", 1))), 0), worry=1.8)
        elif t < T_WALK0:
            u = seg(t, T_LENA_GO, T_WALK0)
            path = [sit_world(S_LENA, 0.05), W(1.4, 0.2, FLOOR - 0.05), DOOR_OUT]
            pp = path[0].lerp(path[1], min(1, 2 * u)) if u < 0.5 else path[1].lerp(path[2], 2 * u - 1)
            pp.z = max(0.0, pp.z)
            lena.pose(f, t, pp, facing=270 if u < 0.5 else 0, run=0.5, run_rate=1.8, worry=1.2)
        else:
            u = seg(t, T_WALK0, T_WALK1 + 4)
            start = DOOR_OUT + Vector((-0.4, 0.75, 0))
            pp = start.lerp(car_door + Vector((0.6, 0.85, 0)), u)
            lena.pose(f, t, pp, facing=yaw_to(car_door - start), run=0.4, run_rate=1.6, reach=(40, 20),
                      look=(0, 15), worry=0.8)
        # Mom: next to Lena; begs her to go (mom1), then can't find her (mom2)
        up = win(t, at("mom2") - 0.3, END, 0.4)
        mom.pose(f, t, sit_world(S_MOM).lerp(W(ROW(2) - 0.6, 0.0, 0), up), facing=lerp_yaw(90 + 60 * win(
            t, at("mom1"), at("lena2", 1)), 30, up), sit=1 - up, seat_h=0.5, lean=0, crouch=0.6 * ducking,
            hug=0.6 * ducking, worry=1.7 + up, look=(lerp(0, 50, up) * math.sin(t * 3), 0),
            reach=(80, 20) if win(t, at("mom1"), at("mom1", 1)) > 0.5 else ((120, -30) if up > 0.5 else None))
        # the rescuer in the driver's seat: turns to us for his lines, opens the door
        turn = max(win(t, at("resc2"), at("resc2", 1)), win(t, at("resc3"), at("resc3", 1)))
        resc.pose(f, t, W(1.3, -0.65, FLOOR - 0.05), facing=90 + 110 * turn, sit=1, seat_h=0.45, lean=0,
                  crouch=0.8 * ducking, reach=(60, -5) if turn < 0.5 else (20, 0), reach2=(60, 5),
                  look=(lerp(0, 30, turn), 0), worry=1.2 + ducking)
        # the old man (front row) turns round to talk
        tt = max(win(t, at("old1"), at("old1", 1)), win(t, at("old2"), at("old3", 1)))
        old.pose(f, t, sit_world(S_OLD), facing=90 + 140 * tt, sit=1, seat_h=0.5, lean=0, crouch=0.7 * ducking,
                 look=(lerp(0, 20, tt), 0), worry=1.2)
        for i, (pp, s) in enumerate(zip(pax, S_PAX)):
            pp.pose(f, t, sit_world(s), facing=90 + 12 * math.sin(i + t * 0.3), sit=1, seat_h=0.5, lean=0,
                    crouch=0.7 * ducking, hug=0.5 * ducking, look=(20 * math.sin(i * 2 + t * 0.4), -5),
                    worry=1.3, talk=False)

        # ---------------- camera (my eyes)
        beast_head = Vector((bx, by, 2.4))
        car_view = Vector((cx, CAR_Y, 1.4))
        cage_view = Vector((cx - 0.9, CAR_Y, 2.5))
        lena_out = lena.p["root"].location.copy() + Vector((0, 0, 1.0))
        pos = front.copy()
        yaw, pitch = look(pos, beast_head)
        # duck behind the dashboard, peek over it
        pos = pos.lerp(duck, ducking)
        y_, p_ = look(pos, beast_head if t < T_FLOOD + 1.2 else car_view)
        yaw, pitch = lerp_yaw(yaw, y_, 1.0), p_
        shots = [  # (key or (t0, t1), position, target)
            ("old1", aisle, sit_world(S_OLD, 1.35)),
            ("me1", front, car_view),
            ("n3", front, car_view + Vector((4, 2, 0))),
            ((at("str1a") - 1.2, at("str1c", 1)), aisle, DOOR_OUT + Vector((-0.3, 0.3, 1.75))),
            ("resc2", aisle, W(1.3, -0.65, FLOOR + 1.3)),
            ((at("mom1"), at("lena2", 1)), W(ROW(1) - 0.35, 0.0, FLOOR + EYE - 0.05), W(ROW(2), -0.08, FLOOR + 1.05)),
            ("resc3", aisle, W(1.3, -0.65, FLOOR + 1.3)),
            ((at("old2"), at("old3", 1)), aisle, sit_world(S_OLD, 1.35)),
            ("me2", aisle, sit_world(S_OLD, 1.35)),
            ((at("n4") - 0.6, at("n4", 1)), front, car_view + Vector((5, 3, 0))),
            ((at("str2b"), at("str1d", 1)), front, None),          # down at the radio
            ("me3", front, car_view),
            ((at("n5"), at("me4", 1)), W(0.9, 0.2, FLOOR + EYE + 0.05), cage_view),
            ("mom2", aisle, W(ROW(2), 0.2, FLOOR + 0.9)),
            ((at("n6"), END + 1), at_door, None),                 # Lena outside, walking to the car
        ]
        for key, p0, tgt in shots:
            a, b = (at(key), at(key, 1)) if isinstance(key, str) else key
            k = win(t, a, b, 0.5)
            if k <= 0:
                continue
            pos = pos.lerp(p0, k)
            if tgt is None and a == at("str2b"):
                y_, p_ = yaw + 5, -42
            elif tgt is None:
                y_, p_ = look(pos, lena_out)
            else:
                y_, p_ = look(pos, tgt)
            yaw, pitch = lerp_yaw(yaw, y_, k), lerp(pitch, p_, k)
        lunge = win(t, at("me5"), at("me5", 1) + 0.6, 0.2)
        pos = pos + Vector((0, 0.25 * lunge, -0.1 * lunge))
        amp = 0.05 + 0.5 * win(t, at("resc1"), at("lena1", 1), 0.2) + 0.9 * win(t, T_HORN, T_FLOOD + 0.8, 0.1) \
            + 0.6 * lunge + 0.3 * win(t, at("mom2"), at("mom2", 1), 0.2)
        sx_, sy_, sz_ = shake[f]
        cam.data.lens = 13 + 17 * win(t, at("n5") + 0.4, at("me4", 1), 0.8)
        cam.data.keyframe_insert("lens", frame=f)
        cam.location = pos
        cam.rotation_euler = (D(90 + pitch + sx_ * amp), D(sy_ * amp * 0.6), D(yaw + sz_ * amp))
        cam.keyframe_insert("location", frame=f)
        cam.keyframe_insert("rotation_euler", frame=f)
        # my hands: holding the radio, reaching out to Lena, or low on the dashboard
        if any(a0 <= t < b0 for a0, b0 in RADIO):
            arms.set(f, "R", (0.12, -0.3, -0.5))
            arms.set(f, "L", (-0.02, -0.32, -0.52))
        elif lunge > 0.3:
            arms.set(f, "R", (0.15, 0.05, -0.85))
            arms.set(f, "L", (-0.2, -0.1, -0.8))
        elif ducking > 0.3:
            arms.set(f, "R", (0.3, -0.55, -0.5))
            arms.set(f, "L", (-0.32, -0.55, -0.5))
        else:
            arms.set(f, "R", (0.28, -0.5, -0.45))
            arms.set(f, "L", (-0.3, -0.5, -0.45))

    # ---------------- night: sky, moon, fog veils
    bpy.ops.object.light_add(type="SUN", rotation=(D(55), D(15), D(-30)))
    sun = bpy.context.object
    sun.data.angle = D(10)
    sun.data.energy = 0.06
    sun.data.color = (0.55, 0.6, 0.9)
    NIGHT = (0.03, 0.04, 0.08)
    setup_render(scene, samples=int(os.environ.get("SAMPLES", "12")), res=(540, 960), sky=NIGHT, sky_strength=1.0)
    scene.cycles.max_bounces = 3
    scene.cycles.transparent_max_bounces = 16
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
    mxs.inputs[0].default_value = 0.06
    em.inputs["Color"].default_value = (*NIGHT, 1)
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
    scene.frame_set(1)
    return scene


if __name__ == "__main__":
    sc = build()
    if arg("--save"):
        bpy.ops.wm.save_as_mainfile(filepath=os.path.join(HERE, "scene4.blend"))
    if arg("--still"):
        os.makedirs(os.path.join(HERE, "test"), exist_ok=True)
        for fr_ in str(arg("--still")).split(","):
            sc.frame_set(int(fr_))
            sc.render.filepath = os.path.join(HERE, "test", f"s4_{int(fr_):04d}.png")
            bpy.ops.render.render(write_still=True)
