"""10-second style test: cartoon comic POV (bright cel-shading, thick outlines, fisheye in post),
smooth motion, phone 'rule' notification.

    ../cast/bpy.sh scene.py --still 20,140,220      -> test/
    ../cast/bpy.sh scene.py --render                -> frames/
"""
import bpy, sys, os, math, random
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "cast"))
bpy.ops.wm.read_factory_settings(use_empty=True)
import cast  # noqa: E402
import props as P  # noqa: E402

FPS, N = 24, 240
sc = bpy.context.scene
random.seed(5)


def D(a):
    return math.radians(a)


def seg(t, a, b):
    x = min(1.0, max(0.0, (t - a) / (b - a)))
    return x * x * (3 - 2 * x)


def lerp(a, b, u):
    return a + (b - a) * u


def wobble(t, k):
    """Smooth hand-held drift (no per-frame jitter)."""
    return math.sin(t * 1.7 + k) * 0.6 + math.sin(t * 3.1 + 2 * k) * 0.3 + math.sin(t * 5.3 + 3 * k) * 0.1


# ------------------------------------------------------------ set: a cartoon classroom
wall = P.mat("Wall", (0.95, 0.9, 0.78), 0.8)
low = P.mat("Wall low", (0.45, 0.72, 0.72), 0.6)
P.box((0, 0, -0.05), (8, 9, 0.1), P.tiles("Floor", (0.86, 0.84, 0.76), (0.78, 0.76, 0.7), (0.55, 0.55, 0.55), 0.5, 0.4),
      "Floor")
P.box((0, 0, 3.25), (8, 9, 0.1), P.mat("Ceiling", (0.98, 0.98, 0.96), 0.9), "Ceiling")
P.box((4, 0, 1.6), (0.12, 9, 3.2), wall, "Wall E")
P.box((0, -4.5, 1.6), (8, 0.12, 3.2), wall, "Back")
for x in (-2.5, 2.5):
    P.box((x, 2.6, 1.6), (3.0, 0.12, 3.2), wall, "Front")
    P.box((x, 2.54, 0.5), (3.0, 0.04, 1.0), low, "Paint")
P.box((0, 2.6, 2.75), (2.0, 0.12, 0.9), wall, "Above door")
P.box((3.95, 0, 0.5), (0.04, 9, 1.0), low, "Paint")
P.box((0, -4.44, 0.5), (8, 0.04, 1.0), low, "Paint")
# west wall: big windows with a blue sky
sky = P.emit("Sky", (0.62, 0.8, 0.98), 1.6)
white = P.mat("Frame", (0.98, 0.98, 0.98), 0.4)
P.box((-4, 0, 0.5), (0.12, 9, 1.0), wall, "Under windows")
P.box((-4, 0, 2.95), (0.12, 9, 0.5), wall, "Over windows")
for y0, y1 in ((-4.5, -3.0), (-1.0, -0.4), (1.6, 2.6)):
    P.box((-4, (y0 + y1) / 2, 1.6), (0.12, y1 - y0, 3.2), wall, "Pillar")
for yc in (-2.0, 0.6):
    P.plane((-4.1, yc, 1.85), (2.0, 1.7), sky, (D(90), 0, D(90)), "Sky")
    for dz in (1.0, 2.7):
        P.box((-3.97, yc, dz), (0.08, 2.0, 0.06), white, "Window frame")
    P.box((-3.97, yc, 1.85), (0.08, 0.05, 1.7), white, "Window bar")
P.area_light((-3.6, -0.7, 1.9), (0, -0.7, 0.6), 420, 6.0, (0.92, 0.96, 1.0), 1.8)
# door to the corridor
door = P.mat("Door", (0.85, 0.5, 0.28), 0.6)
P.box((0, 2.6, 0.6), (1.0, 0.06, 1.2), door, "Door low")
P.box((0, 2.6, 2.2), (1.0, 0.06, 0.2), door, "Door top")
for dx in (-0.42, 0.42):
    P.box((dx, 2.6, 1.65), (0.16, 0.06, 0.9), door, "Door side")
P.box((0.35, 2.55, 1.0), (0.12, 0.05, 0.04), P.mat("Handle", (0.7, 0.7, 0.72), 0.3, 1.0), "Handle")
P.box((0, 2.6, 1.65), (0.68, 0.015, 0.9), P.mat("Glass", (0.8, 0.88, 0.9), 0.05, alpha=0.06), "Glass")
P.box((0, 3.6, 1.6), (2.4, 0.1, 3.2), P.mat("Corridor", (0.55, 0.6, 0.66), 0.7), "Corridor")
P.area_light((0, 3.0, 2.4), (0, 2.6, 1.6), 150, 1.0, (0.85, 0.9, 1.0))
# board, clock, picture posters, shelf with books
P.box((2.6, 2.53, 1.7), (2.4, 0.04, 1.1), P.mat("Board", (0.2, 0.42, 0.32), 0.7), "Board")
P.box((2.6, 2.56, 1.7), (2.55, 0.03, 1.25), P.mat("Board frame", (0.7, 0.45, 0.25), 0.6), "Board frame")
bpy.ops.mesh.primitive_cylinder_add(radius=0.2, depth=0.04, location=(-2.2, 2.53, 2.6), rotation=(D(90), 0, 0), vertices=32)
bpy.context.object.data.materials.append(P.mat("Clock", (0.98, 0.98, 0.95), 0.4))
for k, (c1, c2) in enumerate([((0.98, 0.75, 0.3), (0.95, 0.4, 0.35)), ((0.5, 0.75, 0.95), (0.3, 0.6, 0.4))]):
    P.box((3.94, -1.5 + k * 1.6, 1.8), (0.02, 0.9, 1.1), P.mat(f"Poster {k}", c1, 0.8), "Poster")
    P.sphere((3.92, -1.5 + k * 1.6, 1.9), 0.25, P.mat(f"Poster art {k}", c2, 0.8), "Poster art", (0.1, 1, 1))
P.box((-2.0, -4.3, 1.0), (2.4, 0.35, 0.05), P.mat("Shelf", (0.7, 0.45, 0.25), 0.6), "Shelf")
for k in range(10):
    P.box((-3.0 + k * 0.22, -4.3, 1.17), (0.12, 0.25, 0.3),
          P.mat(f"Book {k}", [(0.9, 0.3, 0.3), (0.3, 0.5, 0.9), (0.95, 0.8, 0.3), (0.4, 0.75, 0.4)][k % 4], 0.6), "Book")
# desks and chairs
deskm, legm = P.mat("Desk", (0.92, 0.75, 0.5), 0.5), P.mat("Leg", (0.35, 0.4, 0.48), 0.4)
chairs = [P.mat("Chair r", (0.95, 0.45, 0.4), 0.5), P.mat("Chair b", (0.35, 0.6, 0.9), 0.5),
          P.mat("Chair g", (0.45, 0.8, 0.5), 0.5)]
for i, (cx, cy) in enumerate(((0, 0), (1.4, 0), (-1.4, 0), (1.5, 1.6), (-1.5, 1.6), (0, -1.5), (1.4, -1.5), (-1.4, -1.5))):
    P.box((cx, cy, 0.73), (1.2, 0.55, 0.05), deskm, "Desk", bevel=0.015)
    for dx in (-0.55, 0.55):
        for dy in (-0.22, 0.22):
            P.box((cx + dx, cy + dy, 0.36), (0.04, 0.04, 0.72), legm, "Leg")
    ch = chairs[i % 3]
    P.box((cx + 0.25, cy - 0.5, 0.45), (0.4, 0.38, 0.04), ch, "Chair", bevel=0.01)
    P.box((cx + 0.25, cy - 0.69, 0.7), (0.4, 0.04, 0.4), ch, "Chair back", bevel=0.01)
    for ex in (-0.17, 0.17):
        for ey in (-0.16, 0.16):
            P.box((cx + 0.25 + ex, cy - 0.5 + ey, 0.22), (0.025, 0.025, 0.44), legm, "Chair leg")
    P.box((cx - 0.2, cy + 0.05, 0.765), (0.25, 0.32, 0.02), P.mat(f"Notebook {i}", (0.98, 0.98, 0.95), 0.7), "Notebook")
P.box((-1.0, -0.2, 0.12), (0.32, 0.18, 0.24), P.mat("Bag", (0.9, 0.35, 0.35), 0.7), "Dropped bag", bevel=0.05)
for k in range(6):
    P.plane((random.uniform(-2, 2), random.uniform(-1.2, 2.2), 0.003), (0.21, 0.29),
            P.mat(f"Paper{k}", (0.98, 0.98, 0.95), 0.8), (0, 0, random.uniform(0, 6)), "Paper")
for x in (-1.6, 1.6):
    P.box((x, 0, 3.18), (1.2, 0.5, 0.04), P.emit("Lamp", (1, 1, 0.95), 4.0), "Lamp")
P.area_light((0, 0, 3.1), (0, 0, 0), 300, 5.0, (1, 0.98, 0.94), 6.0)
w = bpy.data.worlds.new("W")
sc.world = w
w.color = (0.7, 0.72, 0.76)

# ------------------------------------------------------------ people
arian = cast.spawn("arian")
zomb = cast.spawn("rezaei", zombie=1.0, name="RezaeiZ", quality="extra")


def talk(t, a, b):
    return 0.35 + 0.5 * abs(math.sin(t * 12)) if a <= t <= b else 0.0


cam = bpy.data.objects.new("POV", bpy.data.cameras.new("POV"))
sc.collection.objects.link(cam)
sc.camera = cam
cam.data.lens = 18
cam.data.sensor_width = 36
cam.data.clip_start = 0.03
for f in range(1, N + 1):
    t = (f - 1) / FPS
    yaw = lerp(-86, -20, seg(t, 2.0, 2.5))                        # Arian -> my phone
    pitch = lerp(-6, -14, seg(t, 2.0, 2.5))
    yaw = lerp(yaw, 2, seg(t, 4.6, 5.1))                          # up at the door
    pitch = lerp(pitch, 12, seg(t, 4.6, 5.1))
    yaw = lerp(yaw, -80, seg(t, 6.8, 7.3))                        # back to Arian
    pitch = lerp(pitch, -4, seg(t, 6.8, 7.3))
    yaw = lerp(yaw, -175, seg(t, 8.1, 8.7))                       # crawl away towards the back
    pitch = lerp(pitch, -12, seg(t, 8.1, 8.7))
    jolt = 2.2 * math.exp(-max(0.0, t - 5.25) * 6) * (t > 5.25)
    amp = 0.7 + jolt + 0.8 * seg(t, 8.0, 8.4)
    crawl = seg(t, 8.2, 10.0)
    pos = Vector((0.5 * crawl, -0.15 + 0.35 * seg(t, 4.6, 5.1) * (1 - seg(t, 6.8, 7.3)) - 1.6 * crawl,
                  0.55 - 0.12 * crawl + 0.02 * math.sin(t * 9) * (t > 8.2)))
    cam.location = pos
    cam.rotation_euler = (D(90 + pitch + wobble(t, 0) * amp), D(wobble(t, 4) * amp * 0.6), D(yaw + wobble(t, 9) * amp))
    cam.keyframe_insert("location", frame=f)
    cam.keyframe_insert("rotation_euler", frame=f)
    grab = seg(t, 6.9, 7.2) * (1 - seg(t, 8.0, 8.3))
    go = seg(t, 8.0, 8.4)
    a_pos = Vector((1.35 - 0.9 * seg(t, 8.0, 9.0), 0.05 - 1.4 * seg(t, 8.3, 10.0), 0))
    arian.animate(f, t, a_pos, lerp(88, 180, go), crouch=1 - 0.4 * go, z_extra=-0.12 - 0.1 * go, lean=4 + 30 * go,
                  arms=("hug" if grab < 0.5 and go < 0.5 else ("shamble" if go > 0.5 else "rest")),
                  arm_r=(lerp(50, 85, grab), lerp(110, 15, grab)) if grab > 0 else None,
                  walk=go, phase=2 * math.pi * 1.6 * t,
                  look=(lerp(5, -40, seg(t, 4.7, 5.1)) if t < 6.8 else 0, 12), worry=1.8,
                  talking=talk(t, 0.4, 1.9) or talk(t, 5.3, 6.6) or talk(t, 7.0, 7.9) or talk(t, 8.2, 9.2))
    zomb.hide(f, t < 4.75)
    zomb.animate(f, t, (0.0, 3.1 - 0.12 * seg(t, 4.9, 5.2), 0), 180, arms="bang",
                 z_extra=-2.0 * (1 - seg(t, 4.8, 5.1)), scream=1.0)
arian.flush()
zomb.flush()

# ------------------------------------------------------------ my hand + phone (POV, cartoon)
PHONE = (2.0, 4.7)   # seconds the phone is up
grip = P.empty("Phone grip")
grip.parent = cam
skin = P.mat("My skin", (0.93, 0.74, 0.6), 0.6)
sleeve = P.mat("My sleeve", (0.16, 0.25, 0.5), 0.8)
phone_m = P.mat("Phone", (0.1, 0.1, 0.12), 0.3)
parts = [P.box((0, 0, 0), (0.076, 0.156, 0.01), phone_m, "Phone body", bevel=0.007),
         P.plane((0, 0, 0.0056), (0.069, 0.146), P.image("Phone screen", os.path.join(HERE, "textures", "phone_rule.png"), 1.8),
                 name="Phone screen"),
         P.box((-0.006, -0.055, -0.024), (0.07, 0.085, 0.03), skin, "Palm", bevel=0.012),          # behind the phone
         P.cyl((-0.043, -0.07, -0.008), (-0.047, 0.005, 0.006), 0.011, skin, "Thumb"),            # along the left edge
         P.cyl((-0.02, -0.11, -0.03), (-0.03, -0.17, -0.045), 0.032, skin, "Wrist"),
         P.cyl((-0.026, -0.15, -0.04), (-0.09, -0.75, -0.26), 0.05, sleeve, "Sleeve")]
for k in range(4):   # finger tips curling round the right edge
    parts.append(P.sphere((0.041, -0.045 + k * 0.024, -0.006), 0.011, skin, "Finger tip", (1.0, 1.2, 1.0)))
for o in parts:
    o.parent = grip
grip.rotation_euler = (math.radians(-10), math.radians(6), 0)
for f in range(1, N + 1):
    t = (f - 1) / FPS
    up = seg(t, PHONE[0], PHONE[0] + 0.45) * (1 - seg(t, PHONE[1] - 0.35, PHONE[1]))
    breathe = 0.004 * math.sin(t * 2.3)
    grip.location = (0.01 + 0.004 * math.sin(t * 1.3), lerp(-0.42, -0.05, up) + breathe, -0.2)
    grip.keyframe_insert("location", frame=f)
for ch in (arian, zomb):
    ch.rig.pose.bones["head"].scale = (1.12, 1.12, 1.12)   # bigger heads = more cartoon

# ------------------------------------------------------------ cartoon look
P.toonify(sat=0.95, lift=0.12, size=0.6, ambient=0.34)
face_bits = [o for ch in (arian, zomb) for k in ("Eyes", "Eyelashes", "Eyebrows", "Teeth") for o in ch.parts.get(k, [])]
people = [o for ch in (arian, zomb) for o in ch.objects if o.type == "MESH" and o not in face_bits]
P.enable_outlines(sc, 2.5, exclude=face_bits, contour_only=people)
P.area_light((1.0, -0.35, 0.55), (1.35, 0.05, 0.85), 10, 0.25, (1.0, 0.95, 0.9), name="Face fill")   # soft light on faces
sc.render.engine = "CYCLES"
sc.cycles.samples = 10
sc.cycles.use_denoising = True
sc.cycles.max_bounces = 3
sc.render.resolution_x, sc.render.resolution_y = 540, 960
sc.render.fps = FPS
sc.frame_start, sc.frame_end = 1, N
sc.render.use_persistent_data = True
sc.render.use_motion_blur = True
sc.render.motion_blur_shutter = 0.12
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
