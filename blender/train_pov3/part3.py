"""
«واگن آخر ۳ — در بسته شد» — the whole episode in one set (the border at dusk, the track behind it).

    0-5 s    we pull Lena up into the train, the door slides shut, mum screams behind the fence
    5-29 s   the train rolls back; Lena and us in the vestibule
    29-51 s  it stops where the last wagon stood: the track is empty, grandma's shawl lies on the rail
    51-62 s  meanwhile at the border (third person): soldiers send mum away from the fence
    62-73 s  back with us, the shawl in our hand; everyone is apart

All times come from times.py (the recorded voices), so the beats follow the lines.
Rendered on twos like episode 2; post.py doubles the frames.

    python part3.py --still 49,361
    python part3.py --render --range 1 1766
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

random.seed(42)
ODOOR = -11.3
FZ = FLOOR_Z
PLAT_Z = 0.6
KNEEL = 0.55
T = KEY_OF  # line key -> (start, end)


def at(key, k=0):
    return T[key][k]


STOP_T = at("rahim1") - 1.0     # the train has stopped
START_Y = -40.0                 # where episode 2 ended
STOP_Y = -95.0                  # where it stops (the last wagon stood just behind our rear end)
SHAWL_Y = -13.0 + STOP_Y - 3.2  # on the rail, 3 m behind our last car


def train_y(t):
    """Rolling back from where episode 2 ended, slowing down to a stop at STOP_T."""
    k = min(1.0, max(0.0, t / STOP_T))
    return lerp(START_Y, STOP_Y, 1 - (1 - k) ** 1.6)


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
        if -15.5 < x < -10.5 and -19.5 < y < -12.0:  # the third-person border shot
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
    lamp.data.energy = 14
    lamp.data.color = (1, 0.88, 0.7)
    parent_keep(lamp, root)
    return root




def build_door_panel(train):
    m = toon("Sliding door", (0.85, 0.85, 0.83), 0.25)
    dark = toon("Door glass", (0.1, 0.12, 0.16), 0.05)
    door = empty("Door panel")
    parent_keep(door, train)
    parts = [box((-HALF_W - 0.09, ODOOR, FZ + 1.1), (0.06, 1.3, 2.3), m, "Door slab", bevel=0.02),
             box((-HALF_W - 0.12, ODOOR, FZ + 1.6), (0.02, 0.75, 0.6), dark, "Door window outer"),
             box((-HALF_W - 0.06, ODOOR, FZ + 1.6), (0.02, 0.75, 0.6), dark, "Door window inner")]
    for p in parts:
        parent_keep(p, door)
    # the glass itself must let us see out: replace the two dark panes by a see-through one
    for p in parts[1:]:
        p.data.materials[0] = glass_mat()
    return door


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


def make_soldier(name):
    g = Person(name, 1.02, 0.2, dict(skin=(0.85, 0.62, 0.48), top=(0.3, 0.38, 0.22), pants=(0.28, 0.33, 0.2),
                                     shoes=(0.08, 0.08, 0.08), hair=(0.1, 0.07, 0.05), belt=(0.15, 0.1, 0.05),
                                     iris=(0.25, 0.18, 0.1), brow=1.3, lid=0.25))
    g.add(ball(g.head_c + Vector((0, 0, 0.45 * g.R)), 1.08 * g.R, toon("Helmet", (0.25, 0.33, 0.2)), "helmet",
               scale=(1, 1.05, 0.65)), g.p["head"])
    return g


# ================================================================ animation


def build():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.fps = FPS
    scene.frame_start, scene.frame_end = 1, int(END * FPS)
    scene.frame_step = 2

    build_world()
    train = build_our_train()
    door = build_door_panel(train)
    shawl = build_shawl()
    lena, mom, rahim = make_lena(), make_mom(), make_rahim()
    sol1, sol2 = make_soldier("Soldier1"), make_soldier("Soldier2")

    cam = make_camera(scene)
    arms = POVArms(cam)
    arms.reach = 1.2

    rnd = random.Random(11)
    shake = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(-1, 1)) for _ in range(int(END * FPS) + 3)]
    mom_fence = Vector((-10.0, ODOOR + 1.5, 0))
    shawl_rest = Vector((-1.5, SHAWL_Y, 0.2))
    lena_in = Vector((-0.75, ODOOR - 0.5, FZ))   # inside the vestibule (train space)
    border0, border1 = at("sol1") - 1.3, at("lena3") - 0.9   # the third-person cut
    pick0, pick1 = at("n6") + 0.4, at("n6") + 1.6

    for f in range(1, int(END * FPS) + 1):
        t = (f - 1) / FPS
        ty = train_y(t)
        tv = Vector((0, ty, 0))
        train.location.y = ty
        train.keyframe_insert("location", frame=f)
        moving = t < STOP_T
        third = border0 <= t < border1

        # ---------------- the sliding door: open, shut at 2.2-3.2, open again when we stop
        shut = seg(t, 2.1, 3.1) * (1 - seg(t, at("n5") - 0.6, at("n5") + 0.4))
        door.location = Vector((0, (1 - shut) * 1.35, 0))
        door.keyframe_insert("location", frame=f)

        # ---------------- Lena: jumps up into the train, stays in the vestibule; later in the doorway
        if t < 1.8:
            u = seg(t, 0.4, 1.6)
            plat = Vector((-2.35, ODOOR + 0.1, PLAT_Z)) + tv
            lp = plat.lerp(lena_in + tv, u)
            lp.z += 0.35 * math.sin(math.pi * u)
            lena.pose(f, t, lp, facing=-90, crouch=0.3 * math.sin(math.pi * u), reach2=(110, -10),
                      look=(0, 15), worry=1.8, lean=0)
        elif t < at("n5"):
            hold = seg(t, at("n4") - 2.0, at("n4") - 1.4)        # leans on us in the silence
            lena.pose(f, t, lena_in + tv + Vector((0.15 * hold, 0.25 * hold, 0)), facing=lerp(-30, -10, hold),
                      look=(lerp(-20, 0, seg(t, 3.0, 4.0)), lerp(5, 22, hold)), hug=0.4 * hold,
                      reach2=(lerp(40, 70, hold), -20), worry=1.7, lean=0)
        else:
            # standing in the open doorway, looking down at the track
            lena.pose(f, t, Vector((-1.78, ODOOR - 0.35, FZ - 0.12)) + tv, facing=125,
                      look=(0, lerp(-25, -10, seg(t, at("lena2") - 0.3, at("lena2")))),
                      reach2=(60, -15), worry=1.8, lean=0)

        # ---------------- Mum at the fence, then sent away by the soldiers
        away = seg(t, at("sol2", 1) - 0.2, border1)
        mp = mom_fence + Vector((-6.0 * away, -1.2 * away, 0))
        turn = seg(t, at("mom2") - 0.5, at("mom2"))
        mom.pose(f, t, mp, facing=lerp(-90, 90, turn) if away < 0.05 else lerp(90, 60, away),
                 run=0.6 * away, run_rate=1.2, lean=0,
                 reach=(lerp(150, 60, turn), 20) if t < at("sol2", 1) else (40, 0),
                 reach2=(lerp(150, 60, turn), -20), look=(lerp(0, 30, away) if away else 0, 10),
                 worry=2.0, wave=0.0)
        # ---------------- soldiers walk up behind her
        for i, s in enumerate((sol1, sol2)):
            u = seg(t, border0 - 0.2, at("sol1") + 0.3 + 0.6 * i)
            p0 = Vector((-17.0 - i, ODOOR - 1.5 + 2.4 * i, 0))
            p1 = mom_fence + Vector((-0.9 - 0.2 * i, -0.6 + 1.2 * i, 0))
            sp = p0.lerp(p1, u) + Vector((-6.0 * away, -1.2 * away, 0))
            s.pose(f, t, sp, facing=-90 if away < 0.05 else 90, run=(u < 0.98) * 0.6 + 0.6 * away, run_rate=1.3,
                   reach=(lerp(10, 70, seg(t, at("sol1"), at("sol1") + 0.5)), 10 - 20 * i),
                   reach2=(60, -10) if away else None, look=(0, 0), worry=0.8, lean=0)

        # ---------------- Rahim comes through the inner door when the train stops
        rin = seg(t, STOP_T + 0.2, at("rahim1") + 0.2)
        if t > STOP_T:
            rahim.pose(f, t, Vector((0.25, ODOOR + 0.6 - 0.3 * rin, FZ)) + tv, facing=lerp(180, 120, rin),
                       look=(30, -5), reach=(90, 30) if at("rahim1") < t < at("rahim1", 1) else None,
                       worry=1.8, lean=0)
        else:
            rahim.pose(f, t, Vector((0.25, ODOOR + 8, FZ)) + tv, facing=180)

        # ---------------- the shawl: on the rail, then in our left hand
        picked = t >= pick1
        if t < pick1:
            lift = seg(t, pick0, pick1)
            hand = Vector((-2.35, SHAWL_Y + 0.7, 0.9))
            shawl.location = shawl_rest.lerp(hand, lift)
            shawl.rotation_euler = (D(70) * lift, 0, 0)
        # (after pick1 it follows the camera; see below)

        # ---------------- camera
        if third:
            # meanwhile at the border: a still, slightly low third-person shot over the fence
            pos = mom_fence + Vector((-1.1, -3.9, 1.45))
            look_at = mom_fence + Vector((0.6, 0.9, 1.15))
            d = look_at - pos
            yaw = math.degrees(math.atan2(-d.x, d.y)); pitch = math.degrees(math.atan2(d.z, d.xy.length))
            yaw += 6 * seg(t, at("sol2", 1) - 0.3, border1)          # follow her as she is led away
            cam.data.lens = 24
            amp = 0.03
        else:
            cam.data.lens = 12
            if t < at("n5") - 0.6:
                # inside the vestibule, at Lena's height
                pos = Vector((-0.55, ODOOR + 0.55, FZ + 1.05)) + tv
                pos = pos.lerp(Vector((-0.95, ODOOR + 0.2, FZ + 0.9)) + tv, 1 - seg(t, 1.6, 2.6))
                yaw, pitch = 172, -8                                   # Lena, inside with us
                # 0-1.8: out of the door at Lena on the platform, pulling her up
                yaw = lerp(100, yaw, seg(t, 1.6, 2.4)); pitch = lerp(-28, pitch, seg(t, 1.6, 2.4))
                # 3.4-5.8: the door window, mum far behind at the fence
                k = seg(t, 3.3, 3.8) * (1 - seg(t, 5.5, 6.1))
                yaw = lerp(yaw, 72, k); pitch = lerp(pitch, 3, k)
                # n3: out of the door window at the dark fields sliding past
                k = seg(t, at("n3") - 0.2, at("n3") + 0.4) * (1 - seg(t, at("n3", 1) - 0.2, at("n3", 1) + 0.4))
                yaw = lerp(yaw, 85, k); pitch = lerp(pitch, 4, k)
                # silence + n4: close on Lena leaning on us
                k = seg(t, at("n3", 1) + 0.2, at("n4") - 1.6)
                pitch = lerp(pitch, -14, k)
                # the train stops, Rahim comes in
                k = seg(t, at("rahim1") - 0.4, at("rahim1"))
                yaw = lerp(yaw, 250, k); pitch = lerp(pitch, 4, k)
                amp = (0.15 if moving else 0.03)
                for te, kk in ((3.1, 1.2), (STOP_T, 1.8)):
                    if te <= t < te + 0.6:
                        amp += kk * (1 - (t - te) / 0.6)
            elif t < pick0 - 0.6:
                # the door opens: lean out, look down the empty track, then at the shawl
                u = seg(t, at("n5") - 0.6, at("n5") + 0.4)
                pos = (Vector((-0.55, ODOOR + 0.55, FZ + 1.05)).lerp(Vector((-1.9, ODOOR - 0.2, FZ + 1.3)), u)) + tv
                to_track = Vector((0, STOP_Y - 13 - 25, 1.5)) - pos
                yaw = lerp(250, math.degrees(math.atan2(-to_track.x, to_track.y)) % 360, u)
                pitch = lerp(4, 0, u)
                cam.data.lens = 12 + 10 * seg(t, at("n5") + 1.0, at("n5") + 3.5) * (1 - seg(t, at("n5", 1), pick0 - 1.6))
                to_shawl = shawl_rest - pos
                k = seg(t, at("n5", 1) - 0.4, pick0 - 1.6)
                yaw = lerp(yaw, math.degrees(math.atan2(-to_shawl.x, to_shawl.y)) % 360, k)
                pitch = lerp(pitch, math.degrees(math.atan2(to_shawl.z, to_shawl.xy.length)), k)
                amp = 0.03
            else:
                # down on the ground by the rail: pick up the shawl, look up at Lena, then the empty track
                u = seg(t, pick0 - 0.6, pick0)
                p_door = Vector((-1.9, ODOOR - 0.2, FZ + 1.3)) + tv
                p_ground = Vector((-2.7, SHAWL_Y + 0.9, 1.1))
                pos = p_door.lerp(p_ground, u)
                to_shawl = shawl_rest - p_ground
                yaw = math.degrees(math.atan2(-to_shawl.x, to_shawl.y)) % 360
                pitch = math.degrees(math.atan2(to_shawl.z, to_shawl.xy.length))
                pitch = lerp(pitch, -20, seg(t, pick1 - 0.2, pick1 + 0.4))
                # Lena in the doorway above
                to_lena = Vector((-1.78, ODOOR - 0.35 + STOP_Y, FZ + 0.75)) - pos
                k = seg(t, at("lena2") - 0.4, at("lena2")) * (1 - seg(t, at("me2") + 1.5, at("me2") + 2.2))
                k = max(k, seg(t, at("lena3") - 0.5, at("lena3")) * (1 - seg(t, at("n7") + 0.5, at("n7") + 1.2)))
                yaw = lerp(yaw, math.degrees(math.atan2(-to_lena.x, to_lena.y)) % 360, k)
                pitch = lerp(pitch, math.degrees(math.atan2(to_lena.z, to_lena.xy.length)), k)
                # the empty dark track ahead (where the wagon was), and at the end the far border lights
                k = seg(t, at("me2") + 2.2, at("me2") + 3.0) * (1 - seg(t, border0 - 0.4, border0))
                k = max(k, seg(t, at("n7") + 3.0, at("n7") + 4.0))
                yaw = lerp(yaw, 180, k); pitch = lerp(pitch, 1, k)
                k = seg(t, at("n7") + 5.5, at("n7") + 6.8)          # back towards the border, where mum is
                yaw = lerp(yaw, 355, k); pitch = lerp(pitch, 2, k)
                amp = 0.025
        sx_, sy_, sz_ = shake[f]
        cam.location = pos
        cam.rotation_euler = (D(90 + pitch + sx_ * amp), D(sy_ * amp * 0.6), D(yaw + sz_ * amp))
        cam.keyframe_insert("location", frame=f)
        cam.keyframe_insert("rotation_euler", frame=f)
        cam.data.keyframe_insert("lens", frame=f)

        # the shawl in our hand: placed in camera space once picked up
        bpy.context.view_layer.update()
        if picked and not third:
            hand_c = Vector((-0.16, -0.36, -0.62))
            shawl.location = cam.matrix_world @ hand_c
            shawl.rotation_euler = (cam.rotation_euler.x - D(35), 0, cam.rotation_euler.z)
        elif third:
            shawl.location = Vector((0, 0, -50))
        shawl.scale = (0.55,) * 3 if picked else (1.0,) * 3
        shawl.keyframe_insert("scale", frame=f)
        shawl.keyframe_insert("location", frame=f)
        shawl.keyframe_insert("rotation_euler", frame=f)

        # ---------------- our hands (hidden far below in the third-person shot)
        if third:
            arms.set(f, "L", (-0.3, -3.0, 0.5))
            arms.set(f, "R", (0.3, -3.0, 0.5))
        elif t < 1.8:
            arms.set(f, "R", world_to_cam(cam, lena.hand_world("L")))
            arms.set(f, "L", (-0.3, -0.42, -0.46))
        elif t < at("n5") - 0.6:
            arms.set(f, "R", world_to_cam(cam, lena.hand_world("L")) if t < at("n4", 1) else (0.25, -0.42, -0.46))
            arms.set(f, "L", (-0.3, -0.42, -0.46))
        elif pick0 - 0.4 <= t < pick1:
            arms.set(f, "L", world_to_cam(cam, shawl.location))
            arms.set(f, "R", (0.28, -0.42, -0.46))
        elif t >= pick1:
            arms.set(f, "L", (-0.16, -0.4, -0.6))
            arms.set(f, "R", (0.28, -0.42, -0.46))
        else:
            arms.set(f, "L", (-0.3, -0.42, -0.46))
            arms.set(f, "R", (0.25, -0.45, -0.3))

    bpy.ops.object.light_add(type="SUN", rotation=(D(75), D(10), D(-40)))
    sun = bpy.context.object
    sun.data.energy = 1.0
    sun.data.color = (0.72, 0.68, 0.95)
    for k in (-36, -12, 12):
        bpy.ops.object.light_add(type="POINT", location=(-9, k, 7))
        lt = no_cam(bpy.context.object)
        lt.data.energy = 1200
        lt.data.color = (1.0, 0.95, 0.8)
    # a cold lamp over the empty stretch of track
    bpy.ops.object.light_add(type="POINT", location=(-3.0, SHAWL_Y + 1.0, 4.0))
    lt = no_cam(bpy.context.object)
    lt.data.energy = 350
    lt.data.color = (0.8, 0.85, 1.0)
    setup_render(scene, sky=(0.36, 0.3, 0.44), sky_strength=0.65)
    scene.frame_set(1)
    return scene


if __name__ == "__main__":
    run_cli(build(), "train_door3.blend")
