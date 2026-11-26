"""Stage 6: 10-second test of the studio system (POV walk, door, switch, eye tracking, faces, hands).

    ../cast/bpy.sh episode_test.py --still 30,90,130,170,230
    ../cast/bpy.sh episode_test.py --render        -> frames/
"""
import bpy, sys, os, math
from mathutils import Vector
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "cast"))
bpy.ops.wm.read_factory_settings(use_empty=True)
import house as H      # noqa: E402
import characters as C  # noqa: E402
import pov             # noqa: E402
import props as P      # noqa: E402

FPS, N = 24, 240
sc = bpy.context.scene


def seg(t, a, b):
    x = min(1.0, max(0.0, (t - a) / (b - a)))
    return x * x * (3 - 2 * x)


def lerp(a, b, u):
    return a + (b - a) * u


h = H.build()
CH = h.C["CHARACTERS"]
me = pov.POV("arian", name="Me")
nina = C.spawn("nina")
mom = C.spawn("mom")
for ch in (me, nina, mom):
    for o in ch.objects:
        H.put(o, CH)

door = h.doors["living"]
door.swing(int(3.4 * FPS), int(4.6 * FPS), 0, 80)
door.press_handle(int(3.15 * FPS), hold=8)
SW = int(7.15 * FPS)
h.switches["living"].flip(1, True)
h.switches["living"].flip(SW, False)
h.switches["living"].flip(int(8.2 * FPS), True)
for li, e, _ in h.lights["living"]:          # a nervous flicker when it comes back
    for ff, v in ((int(8.2 * FPS) + 2, 0), (int(8.2 * FPS) + 4, e), (int(8.2 * FPS) + 7, 0.3 * e), (int(8.2 * FPS) + 9, e)):
        li.data.energy = v
        li.data.keyframe_insert("energy", frame=ff)

for f in range(1, N + 1):
    t = (f - 1) / FPS
    # ---- me (POV)
    walk1 = seg(t, 0.0, 0.3) * (1 - seg(t, 1.9, 2.2))
    walk2 = seg(t, 4.6, 4.8) * (1 - seg(t, 6.0, 6.3))
    x = lerp(0.05, 0.1, seg(t, 0, 2.1)) + 0.8 * seg(t, 4.6, 6.2)
    y = lerp(0.5, 1.85, seg(t, 0.0, 2.1)) + 0.12 * seg(t, 4.6, 6.2)
    facing = lerp(0, -80, seg(t, 2.0, 2.6))
    yaw = lerp(0, 40, seg(t, 0.7, 1.2)) * (1 - seg(t, 1.4, 1.9)) + lerp(0, -25, seg(t, 1.6, 2.0)) * (1 - seg(t, 2.0, 2.6))
    yaw += lerp(0, 35, seg(t, 4.8, 5.3)) * (1 - seg(t, 6.4, 6.8))            # towards Nina on the sofa
    yaw += lerp(0, 55, seg(t, 6.5, 6.9)) * (1 - seg(t, 7.6, 8.0))            # the switch on my left
    pitch = -12 * seg(t, 2.6, 3.0) * (1 - seg(t, 4.4, 4.8)) - 8 * seg(t, 6.5, 6.9) * (1 - seg(t, 7.6, 8.0))
    turn = seg(t, 8.9, 9.5)
    facing = lerp(facing, 100, turn)                                         # spin round to the hallway
    me.animate(f, t, (x, y, 0), facing, walk=max(walk1, walk2), phase=2 * math.pi * 0.95 * t, arms="rest",
               look=(yaw * (1 - turn), pitch), hands="relaxed")
    # ---- Nina on the sofa
    stand = seg(t, 8.2, 8.9)
    cam_pos = Vector((x, y, 1.6))
    nina.animate(f, t, (3.0, 4.42 - 0.25 * stand, 0), 180, sit=1 - stand, arms="rest" if t < 8.6 else "reach",
                 reach=85, look=(lerp(0, -45, seg(t, 4.8, 5.2)), 6), look_at=cam_pos if t > 4.8 else None,
                 brows="surprised" if 4.9 < t < 6.6 else ("worried" if t > 6.6 else "neutral"),
                 talking=(0.5 + 0.4 * abs(math.sin(t * 11))) if (5.3 < t < 6.3 or 8.6 < t < 9.4) else 0.0,
                 hands="point_r" if t > 8.6 else "relaxed", arm_r=(85, 8) if t > 8.6 else None, worry=1.4 if t > 6.6 else 0.3)
    # ---- Mom in the kitchen arch (revealed at the end)
    mom.hide(f, t < 8.8)
    mom.animate(f, t, (-0.85, 1.75, 0), -90, arms="rest", look_at=cam_pos, suspicious=True, brows="angry",
                mouth=dict(frown=0.5))
for ch in (me, nina, mom):
    ch.flush()
me.bind_camera(1)
sc.camera = me.cam
H.put(me.cam, h.C["CAMERAS"])
# hands: right hand to the door handle (rides it while the door opens), left hand to the switch
me.reach("r", int(2.75 * FPS), int(3.4 * FPS), door.handle, int(4.3 * FPS))
me.reach("l", int(6.75 * FPS), int(7.1 * FPS), h.switches["living"].rocker, int(7.5 * FPS))

# ---- look
sc.render.engine = "CYCLES"
sc.cycles.samples = 10
sc.cycles.use_denoising = True
sc.cycles.max_bounces = 4
sc.render.resolution_x, sc.render.resolution_y = 540, 960
sc.render.fps = FPS
sc.frame_start, sc.frame_end = 1, N
sc.render.use_persistent_data = True
sc.view_settings.view_transform = "AgX"
sc.view_settings.look = "AgX - Medium Low Contrast"
sc.view_settings.exposure = -0.1
for li, e, _ in h.lights["living"]:
    li.data.size = 2.0
P.area_light((3.0, 2.6, 2.5), (3.0, 4.4, 0.6), 120, 1.5, (1.0, 0.92, 0.8), name="Living fill")
P.enable_outlines(sc, 1.1)
args = sys.argv
if "--still" in args:
    os.makedirs(os.path.join(HERE, "test"), exist_ok=True)
    for f in [int(v) for v in args[args.index("--still") + 1].split(",")]:
        sc.frame_set(f)
        sc.render.filepath = os.path.join(HERE, "test", f"e_{f:04d}.png")
        bpy.ops.render.render(write_still=True)
if "--save" in args:
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(HERE, "studio_test.blend"))
if "--render" in args:
    os.makedirs(os.path.join(HERE, "frames"), exist_ok=True)
    sc.render.filepath = os.path.join(HERE, "frames", "f_")
    sc.render.use_overwrite = False
    bpy.ops.render.render(animation=True)
