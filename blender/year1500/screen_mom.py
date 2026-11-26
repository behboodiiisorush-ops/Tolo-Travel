"""The picture on the big screen in «سال ۱۵۰۰»: an old home video — mom kneeling next to little Kian (about six),
he waves, she talks to the camera. Comic look. -> screen/mom_XXXX.png (480x270), film seconds 37..45.
    ../cast/bpy.sh screen_mom.py [--still]"""
import bpy, sys, os, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "cast"))
sys.path.insert(0, os.path.join(HERE, "..", "studio"))
sys.path.insert(0, HERE)                  # (studio/ has its own captions.py)
bpy.ops.wm.read_factory_settings(use_empty=True)
import cast, props as P, toon_look as T  # noqa: E402
from captions import LINES, SCREEN  # noqa: E402
cast.STYLE = cast.CARTOON
FPS = 24
T0, T1 = SCREEN["pic0"], SCREEN["pic1"]
sc = bpy.context.scene
mom = cast.spawn("mom")
kid = cast.spawn("kian")
T.register(mom, "mom", realistic=True)
T.register(kid, "kian", realistic=True)
skin, clothes = T.SKIN[mom.name]
clothes = {k: ((0.55, 0.16, 0.22) if "sweater" in k else v) for k, v in clothes.items()}
T.SKIN[mom.name] = (skin, clothes)
SPEAK = [(a, b) for a, b, w, _ in LINES if w == "mom" and a > 30]
n = int((T1 - T0) * FPS)
for f in range(1, n + 1):
    t = T0 + (f - 1) / FPS
    talk = any(a <= t <= b for a, b in SPEAK)
    mom.animate(f, t, (0.2, 0.05, 0), 195, crouch=0.75, arms="rest", smile=0.8 if not talk else 0.4, talking=talk,
                look=(-8 + 6 * math.sin(t * 0.8), 18))
    wave = 1.0 if (t - T0) % 5.0 < 2.6 else 0.0
    kid.animate(f, t, (-0.22, -0.1, 0), 170, scale=0.62, arms="wave" if wave else "rest", smile=1.0,
                look=(0, 4))
mom.flush()
kid.flush()
mats = dict(wall=P.mat("Room wall", (0.86, 0.74, 0.58), 0.9), floor=P.mat("Room floor", (0.55, 0.42, 0.32), 0.8),
            win=P.mat("Window sky", (0.95, 0.7, 0.5), 0.5), frame=P.mat("Window frame", (0.95, 0.95, 0.92), 0.5),
            sofa=P.mat("Sofa", (0.36, 0.5, 0.52), 0.9), plant=P.mat("Plant", (0.4, 0.62, 0.32), 0.9))
P.box((0, 1.2, 1.5), (6, 0.1, 3), mats["wall"], "Wall")
P.box((0, 0, -0.05), (6, 4, 0.1), mats["floor"], "Floor")
P.box((-1.1, 1.13, 1.55), (1.2, 0.04, 1.1), mats["frame"], "Window frame")
P.box((-1.1, 1.1, 1.55), (1.05, 0.04, 0.95), mats["win"], "Window")
P.box((1.25, 0.85, 0.3), (1.6, 0.6, 0.6), mats["sofa"], "Sofa")
P.box((1.25, 1.1, 0.7), (1.6, 0.2, 0.6), mats["sofa"], "Sofa back")
P.sphere((-1.9, 0.9, 0.9), 0.35, mats["plant"], "Plant")
P.cyl((-1.9, 0.9, 0), (-1.9, 0.9, 0.6), 0.16, mats["sofa"], "Pot")
w = bpy.data.worlds.new("W")
sc.world = w
w.color = (0.55, 0.5, 0.48)
sun = bpy.data.objects.new("Sun", bpy.data.lights.new("Sun", "SUN"))
sc.collection.objects.link(sun)
sun.data.energy = 2.6
sun.data.color = (1.0, 0.9, 0.8)
sun.rotation_euler = (math.radians(55), 0, math.radians(-30))
sc.frame_set(1)
T.SAT = 1.2
T.toonify(sc, samples=6)
T.ink([o for o in bpy.data.objects if o.type == "MESH" and o.name not in ("Wall", "Floor", "Window")
       and not any(k in o.name.lower() for k in ("high-poly", "lash", "brow", "teeth", "tongue"))], 0.004)
cam = bpy.data.objects.new("C", bpy.data.cameras.new("C"))
sc.collection.objects.link(cam)
sc.camera = cam
cam.data.lens = 32
for f in range(1, n + 1, 12):                 # handheld home-video drift
    t = f / FPS
    cam.location = (0.05 * math.sin(t * 0.9), -1.75 + 0.04 * math.sin(t * 0.6), 0.82 + 0.03 * math.sin(t * 1.3))
    cam.rotation_euler = (math.radians(93 + 0.8 * math.sin(t * 0.7)), 0, math.radians(0.8 * math.sin(t * 0.5)))
    cam.keyframe_insert("location", frame=f)
    cam.keyframe_insert("rotation_euler", frame=f)
sc.render.resolution_x, sc.render.resolution_y = 480, 270
out = os.path.join(HERE, "screen")
os.makedirs(out, exist_ok=True)
frames = [60] if "--still" in sys.argv else range(1, n + 1)
for f in frames:
    p = os.path.join(out, f"mom_{f:04d}.png")
    if os.path.exists(p) and "--still" not in sys.argv:
        continue
    sc.frame_set(f)
    sc.render.filepath = p
    bpy.ops.render.render(write_still=True)
