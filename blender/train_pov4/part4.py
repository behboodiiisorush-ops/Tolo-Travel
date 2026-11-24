"""
«واگن آخر ۴ — چراغای روشن» — night.  One set: our train stopped on the track behind the border,
the last wagon on a siding further back (windows still lit), and the border camp.

    A  by our train: the shawl, Rahim in the doorway, Lena; the torch clicks on
    B  walking along the rails in the dark, the torch on the gravel; Lena sees the lights
    C  inside the last wagon: sleeping passengers, the torch finds Jalal
    D  meanwhile, beyond the border (third person): grandma finds mum
    E  back in the wagon; the torch into the empty dark

All beats follow times.py (the recorded voices).  Rendered on twos; post.py doubles the frames.

    python part4.py --still 49,361
    python part4.py --render --range 1 2000
"""

import math
import os
import random
import sys

import bpy
from mathutils import Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403,E402
from captions import END, KEY_OF  # noqa: E402

random.seed(44)
ODOOR = -11.3
FZ = FLOOR_Z
PLAT_Z = 0.6
KNEEL = 0.55
T = KEY_OF
STOP_Y = -95.0                      # where our train stands (from episode 3)
LX, LY = -7.0, -150.0               # the last wagon on its siding
LDOOR = LY + 4.0                    # its open door, on the side facing our track
EYE = 1.55


def at(key, k=0):
    return T[key][k]


# ================================================================ world

def build_world():
    dirt = toon("Field dirt", (0.42, 0.33, 0.27), 0.15)
    box((0, -40, -0.05), (400, 500, 0.1), dirt, "Ground")
    rails(0, -260, 80, 0)
    concrete = toon("Platform", (0.62, 0.6, 0.58), 0.15)
    edge = toon("Platform edge", (0.95, 0.8, 0.15), 0.35)
    box((-3.9, -35, PLAT_Z / 2), (4.3, 110, PLAT_Z), concrete, "Platform", bevel=0.03)
    box((-1.85, -35, PLAT_Z + 0.005), (0.12, 110, 0.01), edge, "Platform edge line")
    for y in range(-88, 20, 3):  # paving joints
        box((-3.9, y, PLAT_Z + 0.004), (4.3, 0.04, 0.01), toon("Joint", (0.5, 0.48, 0.47), 0.1), "Joint")
    # the border: fence, floodlights, barrier, hut, people behind the fence
    fence = toon("Fence", (0.55, 0.6, 0.62), 0.15)
    for k in range(-30, 12):
        rod((-8, k * 2.5, 0), (-8, k * 2.5, 2.9), 0.06, fence, "Fence post")
    for z in (1.0, 1.7, 2.4, 2.85):
        box((-8, -45, z), (0.03, 105, 0.03), fence, "Fence wire")
    lamp = glow_mat("Flood", (1.0, 0.95, 0.75), 9.0)
    for k in (-84, -60, -36, -12, 12):
        rod((-12, k, 0), (-12, k, 9.3), 0.2, fence, "Light tower")
        box((-11.6, k, 9.3), (0.6, 1.4, 0.7), lamp, "Floodlight")
    red_w = [toon("Barrier red", (0.9, 0.12, 0.1), 0.2), toon("Barrier white", (0.97, 0.97, 0.95), 0.3)]
    for k in range(8):
        box((-8.3, -14 + k * 0.6, 1.1), (0.25, 0.6, 0.25), red_w[k % 2], "Barrier")
    hut = toon("Hut", (0.35, 0.5, 0.3), 0.15)
    box((-15, -4, 1.5), (3, 3, 3), hut, "Guard hut")
    box((-15, -4, 3.15), (3.6, 3.6, 0.3), toon("Hut roof", (0.85, 0.3, 0.2), 0.15), "Hut roof")
    box((-13.48, -4, 1.9), (0.06, 1.4, 0.8), glow_mat("Hut window", (0.95, 0.85, 0.4), 2.0), "Hut window")
    crowd_c = [(0.85, 0.2, 0.2), (0.2, 0.45, 0.85), (0.95, 0.7, 0.1), (0.3, 0.65, 0.3), (0.6, 0.3, 0.7)]
    for k in range(30):
        c = crowd_c[k % 5]
        x, y = random.uniform(-22, -11), random.uniform(-30, 12)
        if abs(x + 15) < 2.5 and abs(y + 4) < 2.5:
            continue
        if -23 < x < -12 and -15 < y < -2:  # keep the border shot (mum and grandma) clear
            continue
        box((x, y, 0.6), (0.4, 0.3, 1.2), toon(f"Crowd {c}", c), "Crowd body", bevel=0.1)
        ball((x, y, 1.4), 0.2, toon("Crowd skin", (0.85, 0.62, 0.48)), "Crowd head")
    # far smoke and the glow of the burning city behind us (down the track)
    smoke = [toon("Smoke", (0.2, 0.19, 0.21), 0.1), toon("Smoke light", (0.32, 0.3, 0.32), 0.1)]
    fire = glow_mat("Fire", (1.0, 0.45, 0.08), 6.0)
    for (x, y) in [(-30, -150), (25, -170), (-55, -120), (40, -110)]:
        ball((x, y, 1.0), 2.5, fire, "Far fire", scale=(1.6, 1.6, 0.8))
        for k in range(11):
            ball((x + k * 1.2, y, 3 + k * 4.0), 2.4 + k * 0.8, random.choice(smoke), "Smoke puff", seg=14)
    pole_m = toon("Pole", (0.3, 0.22, 0.16), 0.12)
    for y in range(-190, 60, 25):
        rod((5, y, 0), (5, y, 8.3), 0.15, pole_m, "Power pole")
        box((5, y, 7.8), (1.6, 0.12, 0.12), pole_m, "Pole arm")
    leaf = [toon("Tree a", (0.2, 0.35, 0.22), 0.12), toon("Tree dead", (0.2, 0.16, 0.14), 0.1)]
    for i in range(40):
        x = random.choice([-1, 1]) * random.uniform(14, 60)
        y = random.uniform(-200, 40)
        if -25 < x < -7 and -32 < y < 14:
            continue
        rod((x, y, 0), (x, y, 2.6), 0.22, pole_m, "Trunk")
        ball((x, y, 4.2), random.uniform(1.6, 2.6), random.choice(leaf), "Crown")



def build_our_train():
    root = empty("Our train")
    for i, (y0, y1) in enumerate(((-13, 13), (13.6, 39.6), (40.2, 66.2))):
        parts, _ = wagon_exterior(f"Car{i}", 0, y0, y1, 0, -1, [ODOOR] if i == 0 else [y0 + 2.2, y1 - 2.2],
                                  panels=False)
        for p in parts:
            parent_keep(p, root)
    inner = toon("Train inside", (0.75, 0.62, 0.45), 0.1)
    pole_m = toon("Handrail", (0.95, 0.75, 0.1), 0.4)
    for py in (ODOOR - 0.95, ODOOR + 0.95):
        parent_keep(box((0, py, FZ + 1.3), (3.0, 0.08, 2.6), inner, "Partition"), root)
    parent_keep(box((0.2, ODOOR + 0.9, FZ + 1.05), (0.8, 0.04, 2.0), toon("Inner door", (0.42, 0.45, 0.5)),
                    "Inner door"), root)
    for py in (ODOOR - 0.57, ODOOR + 0.57):
        parent_keep(rod((-1.3, py, FZ + 0.1), (-1.3, py, FZ + 2.1), 0.03, pole_m, "Handrail"), root)
    # warm vestibule lamp: lights Lena's face from the door
    bpy.ops.object.light_add(type="POINT", location=(-0.6, ODOOR, FZ + 1.4))
    lamp = no_cam(bpy.context.object)
    lamp.data.energy = 45
    lamp.data.color = (1, 0.88, 0.7)
    parent_keep(lamp, root)
    return root




def build_shawl():
    """Grandma's red shawl with the yellow / white flower dots (as in episode 1)."""
    red = toon("Grandma shawl", (0.85, 0.12, 0.15))
    root = empty("Shawl")
    parts = [ball((0, 0, 0), 0.3, red, "Shawl cloth", scale=(1.25, 0.95, 0.12)),
             ball((0.12, 0.08, 0.03), 0.18, red, "Shawl fold", scale=(1.2, 0.9, 0.25))]
    for k in range(10):
        a = D(k * 36)
        c = (0.98, 0.85, 0.2) if k % 2 else (0.98, 0.98, 0.95)
        parts.append(ball((math.cos(a) * 0.26, math.sin(a) * 0.19, 0.035), 0.03, toon("Flower", c, 0.4),
                          "Shawl flower", seg=8))
    for p in parts:
        parent_keep(p, root)
    return root




def build_last_wagon():
    """Grandma's wagon on a siding: lit windows outside, dark inside with one lantern."""
    parts, _ = wagon_exterior("Last", LX, LY - 9, LY + 9, 0, +1, [LDOOR], burnt=0.6, panels=False)
    warm = glow_mat("Lit window", (1.0, 0.78, 0.4), 2.2)
    for o in parts:
        if "window band" in o.name or "end window" in o.name:
            o.data.materials[0] = warm
    rails(LX, LY - 40, LY + 25, 0, "Siding")
    seat = toon("Seat", (0.15, 0.22, 0.5), 0.12)
    metal = toon("Car metal", (0.55, 0.58, 0.62), 0.12)
    box((LX - 0.95, LY, FZ + 0.44), (0.5, 14, 0.12), seat, "Bench", bevel=0.04)
    box((LX - 0.95, LY, FZ + 0.2), (0.4, 14, 0.38), metal, "Bench base")
    box((LX - 1.3, LY, FZ + 0.85), (0.12, 14, 0.85), seat, "Bench back", bevel=0.04)
    bag_c = [(0.85, 0.2, 0.2), (0.2, 0.45, 0.85), (0.95, 0.7, 0.1), (0.3, 0.65, 0.3), (0.6, 0.3, 0.7)]
    for k in range(7):
        c = bag_c[k % 5]
        box((LX + random.uniform(-0.6, 0.2), LY + random.uniform(-6, 2), FZ + 0.15),
            (0.45, random.uniform(0.3, 0.6), 0.3), toon(f"Bag {c}", c), "Bag", bevel=0.05)
    ball((LX - 0.55, LY - 6.5, FZ + 0.15), 0.1, glow_mat("Lantern", (1.0, 0.75, 0.35), 6.0), "Lantern",
         scale=(1, 1, 1.3))
    bpy.ops.object.light_add(type="POINT", location=(LX - 0.3, LY - 6.2, FZ + 1.0))
    lt = no_cam(bpy.context.object)
    lt.data.energy = 25
    lt.data.color = (1.0, 0.7, 0.4)


def build_torch(cam):
    """The torch in our right hand: body, glowing lens, a spot light and a faint drawn beam."""
    root = empty("Torch")
    parent_local(root, cam)
    body = rod((0, 0, 0.0), (0, 0, -0.2), 0.022, toon("Torch body", (0.15, 0.15, 0.17), 0.1), "Torch body")
    head = rod((0, 0, -0.2), (0, 0, -0.25), 0.034, toon("Torch head", (0.75, 0.6, 0.1), 0.2), "Torch head")
    lens = ball((0, 0, -0.252), 0.03, glow_mat("Torch lens", (1.0, 0.97, 0.85), 8.0), "Torch lens",
                scale=(1, 1, 0.3))
    beam_m = bpy.data.materials.new("Torch beam")
    beam_m.use_nodes = True
    nt = beam_m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = (1.0, 0.95, 0.75, 1)
    em.inputs["Strength"].default_value = 0.06
    add = nt.nodes.new("ShaderNodeAddShader")
    nt.links.new(tr.outputs[0], add.inputs[0])
    nt.links.new(em.outputs[0], add.inputs[1])
    nt.links.new(add.outputs[0], out.inputs["Surface"])
    bpy.ops.mesh.primitive_cone_add(radius1=0.03, radius2=0.9, depth=3.5, location=(0, 0, -0.25 - 1.75),
                                    vertices=24, end_fill_type="NOTHING")
    beam = finish(bpy.context.object, beam_m, "Torch beam", smooth=True)
    beam.rotation_euler = (D(180), 0, 0)
    beam.visible_shadow = False
    for o in (body, head, lens, beam):
        o.name = o.name
        parent_local(o, root)
    bpy.ops.object.light_add(type="SPOT", location=(0, 0, -0.26))
    spot = bpy.context.object
    spot.data.energy = 900
    spot.data.spot_size = D(38)
    spot.data.spot_blend = 0.35
    spot.data.color = (1.0, 0.95, 0.8)
    spot.data.shadow_soft_size = 0.02
    parent_local(spot, root)
    return root, spot, beam


def darken_toon(k=0.25):
    """Night: toon materials glow less by themselves, so the torch and the lamps do the lighting."""
    for m in bpy.data.materials:
        if not m.use_nodes:
            continue
        nodes = m.node_tree.nodes
        if any(n.type == "BSDF_TOON" for n in nodes):
            for n in nodes:
                if n.type == "EMISSION":
                    n.inputs["Strength"].default_value *= k


# ================================================================ animation


def yaw_to(d):
    return math.degrees(math.atan2(-d.x, d.y)) % 360


def pitch_to(d):
    return math.degrees(math.atan2(d.z, d.xy.length))


def build():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.fps = FPS
    scene.frame_start, scene.frame_end = 1, int(END * FPS)
    scene.frame_step = 2

    build_world()
    train = build_our_train()
    train.location.y = STOP_Y
    build_last_wagon()
    shawl = build_shawl()
    lena, rahim, jalal = make_lena(), make_rahim(), make_jalal()
    mom, grandma = make_mom(), make_grandma()
    show([o for o in bpy.data.objects if o.name.startswith("Grandma") and ("shawl" in o.name or "flower" in o.name)],
         1, False)  # her shawl is with us
    sleepers = [make_extra(i, 0.95) for i in (0, 3, 5)]

    cam = make_camera(scene)
    arms = POVArms(cam)
    arms.reach = 1.2
    torch, spot, beam = build_torch(cam)

    rnd = random.Random(12)
    shake = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(-1, 1)) for _ in range(int(END * FPS) + 3)]

    rear = -13.0 + STOP_Y                              # rear end of our train
    start = Vector((-2.6, rear - 1.0, EYE))            # standing on the gravel by the rear
    door_out = Vector((LX + 2.2, LDOOR + 0.3, EYE))    # outside the last wagon's door
    inside = Vector((LX + 0.75, LDOOR + 0.1, FZ + EYE))
    walk0, walk1 = at("n2") - 0.3, at("me2") - 1.6
    climb1 = at("me2") - 0.2
    border0, border1 = at("mom1") - 1.6, at("lena4") - 1.0
    torch_on = at("me1") + 0.4
    jalal_seat = Vector((LX - 0.75, LDOOR - 1.7, FZ))   # on the bench, near the door
    mom_pos = Vector((-18.0, -9.5, 0))

    for f in range(1, int(END * FPS) + 1):
        t = (f - 1) / FPS
        third = border0 <= t < border1
        walking = walk0 <= t < walk1

        # ---------------- where we are
        if t < walk0:
            pos = start.copy()
        elif t < walk1:
            u = (t - walk0) / (walk1 - walk0)
            pos = start.lerp(door_out, u)
            pos.z += 0.035 * abs(math.sin(math.pi * t * 1.9))
        elif t < climb1:
            u = seg(t, walk1, climb1)
            pos = door_out.lerp(inside, u)
            pos.z += 0.25 * math.sin(math.pi * u)
        elif t < at("n5") + 2.5:
            pos = inside.copy()
        else:  # back to the door, looking out into the dark
            pos = inside.lerp(Vector((LX + 1.35, LDOOR, FZ + EYE)), seg(t, at("n5") + 2.5, at("n5") + 3.5))
        path_dir = (door_out - start).normalized()

        # ---------------- where we look
        lena_p = None
        if t < walk0:
            lena_now = start + Vector((-0.9, 0.4, -EYE))
            yaw, pitch = yaw_to(Vector((0, -1, 0))), -30          # the shawl in our hand, the dark track
            k = seg(t, at("rahim1") - 0.5, at("rahim1")) * (1 - seg(t, at("lena1") - 0.5, at("lena1")))
            to_r = Vector((-1.78, ODOOR - 0.35 + STOP_Y, FZ + 1.2)) - start
            yaw = lerp(yaw, yaw_to(to_r), k); pitch = lerp(pitch, pitch_to(to_r), k)
            k = seg(t, at("lena1") - 0.5, at("lena1"))
            to_l = lena_now + Vector((0, 0, 0.95)) - start
            yaw = lerp(yaw, yaw_to(to_l), k); pitch = lerp(pitch, pitch_to(to_l), k)
            k = seg(t, torch_on + 1.2, torch_on + 2.2)                    # the torch onto the track ahead
            yaw = lerp(yaw, yaw_to(path_dir) - 10, k); pitch = lerp(pitch, -22, k)
        elif t < walk1:
            yaw, pitch = yaw_to(path_dir) - 8 + 6 * math.sin(t * 0.9), -24
            k = seg(t, at("lena2") - 0.2, at("lena2") + 0.4)               # Lena points: the lit wagon
            to_w = Vector((LX, LY + 9, 2.4)) - pos
            yaw = lerp(yaw, yaw_to(to_w), k); pitch = lerp(pitch, pitch_to(to_w), k)
            cam_lens = 12 + 8 * seg(t, at("n3") + 0.5, at("n3") + 3.0) * (1 - seg(t, at("n3", 1) - 0.5, walk1))
        elif t < climb1:
            yaw, pitch = lerp(yaw_to(path_dir), 95, seg(t, walk1, climb1)), lerp(0, -10, seg(t, walk1, climb1))
        elif third:
            pass
        else:
            # inside: the torch sweeps the dark wagon, finds Jalal, then Lena, the shawl, the door
            yaw, pitch = 140 + 25 * math.sin((t - climb1) * 0.8), -12
            to_j = jalal_seat + Vector((0, 0, 1.15)) - pos
            k = seg(t, at("jalal1") - 0.6, at("jalal1"))
            yaw = lerp(yaw, yaw_to(to_j), k); pitch = lerp(pitch, pitch_to(to_j), k)
            lena_in = Vector((LX + 0.25, LDOOR + 0.6, FZ))
            to_l = lena_in + Vector((0, 0, 0.95)) - pos
            k = seg(t, at("lena3") - 0.3, at("lena3")) * (1 - seg(t, at("me3") - 0.2, at("me3") + 0.2))
            k = max(k, seg(t, at("lena4") - 0.3, at("lena4")) * (1 - seg(t, at("n5") + 1.0, at("n5") + 1.8)))
            yaw = lerp(yaw, yaw_to(to_l), k); pitch = lerp(pitch, pitch_to(to_l), k)
            k = seg(t, at("n4") - 0.3, at("n4") + 0.3) * (1 - seg(t, at("n4", 1) - 0.3, at("n4", 1) + 0.6))
            pitch = lerp(pitch, -45, k)                                   # the shawl in our hand
            k = seg(t, at("n5") + 2.5, at("n5") + 3.5)                    # out of the door into the dark
            yaw = lerp(yaw, 270, k); pitch = lerp(pitch, -6, k)

        # ---------------- third person at the border
        if third:
            pos = mom_pos + Vector((2.4, -2.6, 1.25))
            look = mom_pos + Vector((-0.2, 0.2, 0.75))
            d = look - pos
            yaw, pitch = yaw_to(d), pitch_to(d)
            yaw += 5 * seg(t, at("mom2") - 0.4, at("mom2") + 0.6)
        lens = 24 if third else (cam_lens if walking else 12)
        cam.data.lens = lens
        cam.data.keyframe_insert("lens", frame=f)
        amp = 0.03 if third else (0.16 if walking else 0.05)
        sx_, sy_, sz_ = shake[f]
        cam.location = pos
        cam.rotation_euler = (D(90 + pitch + sx_ * amp), D(sy_ * amp * 0.6), D(yaw + sz_ * amp))
        cam.keyframe_insert("location", frame=f)
        cam.keyframe_insert("rotation_euler", frame=f)

        # ---------------- the torch
        on = (t >= torch_on) and not third
        spot.data.energy = 900 if on else 0.0
        spot.data.keyframe_insert("energy", frame=f)
        beam.scale = (1, 1, 1) if on else (0.001, 0.001, 0.001)
        beam.keyframe_insert("scale", frame=f)
        hand_r = Vector((0.2, -0.3, -0.42)) if not third else Vector((0.3, -3.0, 0.5))
        torch.location = hand_r + Vector((0, 0.03, -0.02))
        torch.rotation_euler = (D(-8), D(-6), 0)
        torch.keyframe_insert("location", frame=f)
        torch.keyframe_insert("rotation_euler", frame=f)
        if t < torch_on - 0.6:
            arms.set(f, "R", (0.3, -0.42, -0.46))
            torch.location = Vector((0.3, -0.42, -0.46)) + Vector((0, 0.03, -0.02))
            torch.keyframe_insert("location", frame=f)
        else:
            arms.set(f, "R", hand_r)

        # ---------------- the shawl in our left hand (not in the border shot)
        bpy.context.view_layer.update()
        if third:
            shawl.location = Vector((0, 0, -50))
            arms.set(f, "L", (-0.3, -3.0, 0.5))
        else:
            shawl.location = cam.matrix_world @ Vector((-0.16, -0.36, -0.62))
            shawl.rotation_euler = (cam.rotation_euler.x - D(35), 0, cam.rotation_euler.z)
            arms.set(f, "L", (-0.16, -0.4, -0.6))
        shawl.scale = (0.55,) * 3
        for prop in ("location", "rotation_euler", "scale"):
            shawl.keyframe_insert(prop, frame=f)

        # ---------------- Lena: beside us outside, walking with us, then inside the wagon
        if t < walk0:
            lena.pose(f, t, start + Vector((-0.9, 0.4, -EYE)), facing=-60, look=(0, 18), worry=1.8, lean=0,
                      hug=0.3 if t < at("me1") else 0.0, reach2=(40, -20))
        elif t < walk1 + 0.6:
            u = min(1.0, (t - walk0) / (walk1 - walk0))
            lp = start.lerp(door_out, u) + Vector((-0.85, 0.5, -EYE))
            point = seg(t, at("lena2") - 0.2, at("lena2") + 0.2) * (1 - seg(t, at("lena2", 1) + 0.6, at("lena2", 1) + 1.0))
            lena.pose(f, t, lp, facing=yaw_to(path_dir) if point < 0.5 else yaw_to(path_dir) + 30,
                      run=0.6, run_rate=1.8, lean=0, look=(0, 8),
                      reach=(lerp(10, 150, point), lerp(0, 40, point)) if point > 0 else None, worry=1.7)
        else:
            u = seg(t, walk1 + 0.6, climb1 + 0.6)
            lp = (door_out + Vector((-0.85, 0.5, -EYE))).lerp(Vector((LX + 0.25, LDOOR + 0.6, FZ)), u)
            lp.z += 0.4 * math.sin(math.pi * u)
            happy = seg(t, at("lena3") - 0.2, at("lena3")) * (1 - seg(t, at("lena3", 1), at("lena3", 1) + 0.5))
            lena.pose(f, t, lp, facing=lerp(-90, 200, seg(t, climb1, climb1 + 0.8)), look=(0, 12), lean=0,
                      worry=lerp(1.6, 0.6, happy), reach2=(lerp(30, 120, happy), 0))

        # ---------------- Rahim in the doorway of our train (then he stays behind)
        rahim.pose(f, t, Vector((-1.78, ODOOR - 0.35 + STOP_Y, FZ - 0.12)), facing=125,
                   reach=(150, 20) if at("rahim1") < t < at("rahim1", 1) else (30, 10), look=(0, -12),
                   worry=1.6, lean=0)

        # ---------------- Jalal, half asleep on a seat, wakes when the torch finds him
        wake = seg(t, at("jalal1") - 0.6, at("jalal1"))
        jalal.pose(f, t, jalal_seat, facing=lerp(-90, -60, wake), sit=1, seat_h=0.5, lean=0,
                   look=(lerp(0, 20, wake), lerp(-30, 6, wake)), worry=1.2,
                   reach=(lerp(20, 80, seg(t, at("jalal1"), at("jalal1") + 0.4)), 30) if t > at("jalal1") else None)
        for i, (s, dy) in enumerate(zip(sleepers, (-4.5, 2.5, 4.0))):
            s.pose(f, t, Vector((LX - 0.75, LDOOR + dy, FZ)), facing=-90, sit=1, seat_h=0.5, lean=0,
                   look=(15 * (-1) ** i, -32), worry=0.3)

        # ---------------- the border: mum sitting in the crowd, grandma finds her
        up = seg(t, at("mom2") - 0.2, at("mom2") + 0.6)
        turn = seg(t, at("gm1"), at("mom2"))
        mom.pose(f, t, mom_pos, facing=lerp(-60, 37, turn), sit=1 - up, seat_h=0.28, crouch=0.3 * (1 - up),
                 look=(0, lerp(-25, 10, turn)), worry=2.0, hug=0.6 * up, lean=0,
                 reach=(lerp(40, 70, up), 0), reach2=(lerp(40, 70, up), 0))
        g_in = seg(t, border0, at("gm1") - 0.2)
        gp = Vector((-21.5, -4.0, 0)).lerp(mom_pos + Vector((-0.6, 0.8, 0)), g_in)
        grandma.pose(f, t, gp, facing=yaw_to(mom_pos - gp) if g_in < 0.99 else 217, run=0.3 * (g_in < 0.99),
                     run_rate=0.9, lean=0, look=(0, -12 + 20 * up), worry=lerp(1.5, 0.5, up), hug=0.6 * up,
                     reach=(lerp(20, 75, seg(t, at("gm1") - 0.4, at("gm1"))), 10))

    bpy.ops.object.light_add(type="SUN", rotation=(D(70), D(10), D(-40)))
    moon = bpy.context.object
    moon.data.energy = 0.25
    moon.data.color = (0.6, 0.65, 1.0)
    for k in (-36, -12, 12):
        bpy.ops.object.light_add(type="POINT", location=(-9, k, 7))
        lt = no_cam(bpy.context.object)
        lt.data.energy = 1500
        lt.data.color = (1.0, 0.95, 0.8)
    bpy.ops.object.light_add(type="POINT", location=(-16.5, -11.0, 2.4))   # a camp lamp over mum
    lt = no_cam(bpy.context.object)
    lt.data.energy = 120
    lt.data.color = (1.0, 0.8, 0.55)
    darken_toon(0.25)
    setup_render(scene, sky=(0.06, 0.06, 0.12), sky_strength=0.8)
    scene.frame_set(1)
    return scene


if __name__ == "__main__":
    run_cli(build(), "train_night4.blend")
