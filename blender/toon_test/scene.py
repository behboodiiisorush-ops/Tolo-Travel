"""8-second style test: cel-shaded comic POV (thick outlines, fisheye in post), phone rule notification.

    ../cast/bpy.sh scene.py --still 30,120,190      -> test/
    ../cast/bpy.sh scene.py --render                -> frames/
"""
import bpy, sys, os, math, random
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "cast"))
bpy.ops.wm.read_factory_settings(use_empty=True)
import cast  # noqa: E402
import props as P  # noqa: E402

FPS, N = 24, 192
sc = bpy.context.scene
random.seed(5)


def D(a):
    return math.radians(a)


def seg(t, a, b):
    x = min(1.0, max(0.0, (t - a) / (b - a)))
    return x * x * (3 - 2 * x)


def lerp(a, b, u):
    return a + (b - a) * u


# ------------------------------------------------------------ set: a classroom corner
wall = P.mat("Wall", (0.86, 0.84, 0.78), 0.8)
low = P.mat("Wall low", (0.55, 0.68, 0.7), 0.6)
P.box((0, 0, -0.05), (8, 9, 0.1), P.tiles("Floor", (0.75, 0.74, 0.7), (0.68, 0.67, 0.64), (0.5, 0.5, 0.5), 0.45, 0.4),
      "Floor")
P.box((0, 0, 3.25), (8, 9, 0.1), P.mat("Ceiling", (0.95, 0.95, 0.93), 0.9), "Ceiling")
for x in (-4, 4):
    P.box((x, 0, 1.6), (0.12, 9, 3.2), wall, "Wall")
P.box((0, -4.5, 1.6), (8, 0.12, 3.2), wall, "Back")
P.box((-2.5, 2.6, 1.6), (3.0, 0.12, 3.2), wall, "Front")
P.box((2.5, 2.6, 1.6), (3.0, 0.12, 3.2), wall, "Front")
P.box((0, 2.6, 2.75), (2.0, 0.12, 0.9), wall, "Above door")
for x in (-3.95, 3.95):
    P.box((x, 0, 0.5), (0.04, 9, 1.0), low, "Paint")
door = P.mat("Door", (0.55, 0.36, 0.22), 0.6)
P.box((0, 2.6, 0.6), (1.0, 0.06, 1.2), door, "Door low")
P.box((0, 2.6, 2.2), (1.0, 0.06, 0.2), door, "Door top")
for dx in (-0.42, 0.42):
    P.box((dx, 2.6, 1.65), (0.16, 0.06, 0.9), door, "Door side")
glass = P.box((0, 2.6, 1.65), (0.68, 0.015, 0.9), P.mat("Glass", (0.8, 0.88, 0.9), 0.05, alpha=0.06), "Glass")
P.box((0, 3.6, 1.6), (2.4, 0.1, 3.2), P.mat("Corridor", (0.45, 0.47, 0.5), 0.7), "Corridor")
P.area_light((0, 3.0, 2.4), (0, 2.6, 1.6), 150, 1.0, (0.85, 0.9, 1.0))
deskm, legm, chairm = P.mat("Desk", (0.85, 0.7, 0.5), 0.5), P.mat("Leg", (0.3, 0.33, 0.38), 0.4), P.mat("Chair", (0.3, 0.5, 0.7), 0.5)
for cx, cy in ((0, 0), (1.4, 0), (-1.4, 0), (1.5, 1.6), (-1.5, 1.6), (0, -1.5), (1.4, -1.5)):
    P.box((cx, cy, 0.73), (1.2, 0.55, 0.04), deskm, "Desk")
    for dx in (-0.55, 0.55):
        for dy in (-0.22, 0.22):
            P.box((cx + dx, cy + dy, 0.36), (0.035, 0.035, 0.72), legm, "Leg")
    P.box((cx + 0.25, cy - 0.5, 0.45), (0.4, 0.38, 0.03), chairm, "Chair")
    P.box((cx + 0.25, cy - 0.69, 0.7), (0.4, 0.03, 0.4), chairm, "Chair back")
P.box((-1.1, -0.1, 0.02), (0.3, 0.2, 0.04), P.mat("Bag", (0.6, 0.3, 0.3), 0.7), "Dropped bag")
for k in range(5):
    P.plane((random.uniform(-2, 2), random.uniform(-1, 3), 0.003), (0.21, 0.29), P.mat(f"Paper{k}", (0.95, 0.95, 0.9), 0.8),
            (0, 0, random.uniform(0, 6)), "Paper")
P.area_light((0, 0, 3.15), (0, 0, 0), 320, 5.0, (1, 0.98, 0.94), 6.0)
P.area_light((-3.8, 0, 1.9), (0, 0, 0.8), 300, 7.0, (0.9, 0.95, 1.0), 1.8)
w = bpy.data.worlds.new("W")
sc.world = w
w.color = (0.6, 0.62, 0.66)

# ------------------------------------------------------------ people
arian = cast.spawn("arian")
zomb = cast.spawn("rezaei", zombie=1.0, name="RezaeiZ", quality="extra")


def talk_win(t, a, b):
    return 0.35 + 0.5 * abs(math.sin(t * 13)) if a <= t <= b else 0.0


cam = bpy.data.objects.new("POV", bpy.data.cameras.new("POV"))
sc.collection.objects.link(cam)
sc.camera = cam
cam.data.lens = 18
cam.data.sensor_width = 36
cam.data.clip_start = 0.03
rnd = random.Random(2)
for f in range(1, N + 1):
    t = (f - 1) / FPS
    # camera: crouched under the middle desk
    yaw = -86                                          # Arian
    yaw = lerp(yaw, 10, seg(t, 2.0, 2.4))              # down at the phone (overlay)
    pitch = lerp(-8, -35, seg(t, 2.0, 2.4)) if t < 4.6 else -35
    yaw = lerp(yaw, 2, seg(t, 4.6, 5.0))               # up at the door
    pitch = lerp(pitch, 12, seg(t, 4.6, 5.0))
    yaw = lerp(yaw, -70, seg(t, 6.8, 7.1))              # back to Arian grabbing me
    pitch = lerp(pitch, -5, seg(t, 6.8, 7.1))
    amp = 0.6 + (2.5 if 5.2 < t < 5.6 else 0) + (1.5 if 6.8 < t < 7.2 else 0)
    pos = Vector((0.0, -0.15 + 0.35 * seg(t, 4.6, 5.0) * (1 - seg(t, 6.8, 7.1)), 0.55 + 0.01 * math.sin(t * 9)))
    cam.location = pos
    cam.rotation_euler = (D(90 + pitch + rnd.uniform(-1, 1) * amp), D(rnd.uniform(-1, 1) * amp * 0.5),
                          D(yaw + rnd.uniform(-1, 1) * amp))
    cam.keyframe_insert("location", frame=f)
    cam.keyframe_insert("rotation_euler", frame=f)
    grab = seg(t, 6.9, 7.2)
    arian.animate(f, t, (1.35, 0.05, 0), 88, crouch=1, z_extra=-0.12, lean=4, arms="hug" if grab < 0.5 else "rest",
                  arm_r=(lerp(50, 85, grab), lerp(110, 15, grab)) if grab > 0 else None,
                  look=(lerp(5, -40, seg(t, 4.7, 5.1)) if t < 6.8 else 0, 12), worry=1.8,
                  talking=talk_win(t, 0.4, 1.8) or talk_win(t, 7.0, 7.9))
    zomb.animate(f, t, (0.0, 3.1 - 0.12 * seg(t, 4.9, 5.2), 0), 0 + 180, arms="bang",
                 z_extra=-2.0 * (1 - seg(t, 4.8, 5.1)), scream=1.0)
arian.flush()
zomb.flush()

P.toonify()
P.enable_outlines(sc, 2.2)
sc.render.engine = "CYCLES"
sc.cycles.samples = 10
sc.cycles.use_denoising = True
sc.cycles.max_bounces = 3
sc.render.resolution_x, sc.render.resolution_y = 540, 960
sc.render.fps = FPS
sc.frame_start, sc.frame_end = 1, N
sc.render.use_persistent_data = True
sc.view_settings.view_transform = "Standard"
args = sys.argv
if "--still" in args:
    os.makedirs(os.path.join(HERE, "test"), exist_ok=True)
    for f in [int(x) for x in args[args.index("--still") + 1].split(",")]:
        sc.frame_set(f)
        sc.render.filepath = os.path.join(HERE, "test", f"t_{f:04d}.png")
        bpy.ops.render.render(write_still=True)
if "--render" in args:
    os.makedirs(os.path.join(HERE, "frames"), exist_ok=True)
    sc.render.filepath = os.path.join(HERE, "frames", "f_")
    sc.render.use_overwrite = False
    bpy.ops.render.render(animation=True)
