"""«زنگ آخر» — realistic version (same story, timeline and dialogue as ../school_pov).

The film is rendered in four parts so each process only builds what it needs:
    house  0-11 s   (f 1-264)      street 11-15 s (f 265-360)
    class 15-63 s   (f 361-1512)   roof   63-75 s (f 1513-1800)

    ../cast/bpy.sh scene.py --part class --still 400,900      -> test/class_0400.png
    ../cast/bpy.sh scene.py --part class --render              -> frames/f_####.png (skips existing)
POV camera = "me". No hijab, no flags, emblems, logos or place names.
"""
import bpy, sys, os, math, random
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "cast"))
sys.path.insert(0, os.path.join(HERE, "..", "school_pov"))
bpy.ops.wm.read_factory_settings(use_empty=True)
import cast                      # noqa: E402
import props as P                # noqa: E402
from captions import CAPTIONS    # noqa: E402

FPS = 24
PARTS = {"house": (1, 264), "street": (265, 360), "class": (361, 1512), "roof": (1513, 1800)}
TEX = os.path.join(HERE, "..", "school_pov", "textures")
HX, SX, CX, RX = 0.0, 60.0, 120.0, 200.0
args = sys.argv
PART = args[args.index("--part") + 1]
F0, F1 = PARTS[PART]
random.seed(13)
sc = bpy.context.scene


def D(a):
    return math.radians(a)


def lerp(a, b, u):
    return a + (b - a) * u


def seg(t, a, b):
    x = min(1.0, max(0.0, (t - a) / (b - a)))
    return x * x * (3 - 2 * x)


SPEAKER_KEY = {"Mom": "mom", "Anchor": "anchor", "Rezaei": "rezaei", "Kazemi": "kazemi", "Arian": "arian",
               "Mahsa": "mahsa", "Kian": "kian", "Soldier": "soldier"}


def talking(key, t):
    for a, b, who, _ in CAPTIONS:
        if who and SPEAKER_KEY.get(who) == key and a - 0.05 <= t <= b:
            return True
    return False


# ==================================================================== materials
M_ = {}


def m(key):
    if key in M_:
        return M_[key]
    mk = {
        "plaster": lambda: P.grime(P.mat("Plaster", (0.86, 0.82, 0.74), 0.8), 1.5, 0.82, 0.1, 0.02),
        "plaster_w": lambda: P.grime(P.mat("Plaster warm", (0.9, 0.83, 0.7), 0.8), 1.5, 0.85, 0.1, 0.02),
        "ceiling": lambda: P.grime(P.mat("Ceiling", (0.92, 0.9, 0.86), 0.85), 1.0, 0.9, 0.05, 0.0),
        "parquet": lambda: P.wood("Parquet", (0.52, 0.34, 0.2), True, 0.3),
        "class_floor": lambda: P.tiles("Class floor", (0.62, 0.6, 0.55), (0.55, 0.53, 0.5), (0.35, 0.34, 0.32), 0.4, 0.35),
        "wall_low": lambda: P.grime(P.mat("Wall low", (0.38, 0.52, 0.5), 0.5), 3.0, 0.75, 0.15, 0.03),
        "wood": lambda: P.wood("Wood", (0.5, 0.32, 0.18), False, 0.4, 3.0),
        "desk": lambda: P.grime(P.mat("Desk top", (0.78, 0.64, 0.46), 0.35), 6.0, 0.85, 0.1, 0.01),
        "metal": lambda: P.mat("Metal", (0.3, 0.32, 0.35), 0.35, 0.8),
        "chair": lambda: P.mat("Chair plastic", (0.18, 0.35, 0.5), 0.35),
        "frame": lambda: P.mat("Frame white", (0.92, 0.92, 0.9), 0.4),
        "frame_dark": lambda: P.mat("Frame dark", (0.15, 0.15, 0.16), 0.4, 0.5),
        "sofa": lambda: P.grime(P.mat("Sofa fabric", (0.22, 0.38, 0.4), 0.9), 30.0, 0.85, 0.05, 0.15),
        "rug": lambda: P.grime(P.mat("Rug", (0.55, 0.2, 0.18), 0.95), 40.0, 0.7, 0.05, 0.2),
        "asphalt": lambda: P.grime(P.mat("Asphalt", (0.22, 0.22, 0.23), 0.85), 8.0, 0.75, 0.1, 0.1),
        "pavement": lambda: P.tiles("Pavement", (0.62, 0.6, 0.56), (0.55, 0.53, 0.5), (0.3, 0.3, 0.3), 0.5, 0.7, 0.01),
        "concrete": lambda: P.grime(P.mat("Concrete", (0.6, 0.59, 0.56), 0.85), 2.0, 0.75, 0.1, 0.05),
        "brick": lambda: P.tiles("Brick", (0.62, 0.38, 0.28), (0.55, 0.33, 0.25), (0.7, 0.68, 0.62), 0.07, 0.8, 0.012,
                                 width=0.22, offset=0.5, wall=True),
        "brick_y": lambda: P.tiles("Brick yellow", (0.8, 0.68, 0.5), (0.74, 0.62, 0.46), (0.82, 0.8, 0.75), 0.07, 0.8,
                                   0.012, width=0.22, offset=0.5, wall=True),
        "grass": lambda: P.grime(P.mat("Grass", (0.3, 0.42, 0.2), 0.9), 12.0, 0.6, 0.05, 0.1),
        "leaves": lambda: P.grime(P.mat("Leaves", (0.22, 0.38, 0.16), 0.7), 25.0, 0.55, 0.1, 0.4),
        "bark": lambda: P.grime(P.mat("Bark", (0.3, 0.22, 0.16), 0.9), 20.0, 0.6, 0.05, 0.3),
        "glass_dark": lambda: P.mat("Window glass", (0.08, 0.1, 0.12), 0.05, 0.0),
        "olive": lambda: P.grime(P.mat("Olive paint", (0.3, 0.34, 0.22), 0.55, 0.1), 4.0, 0.75, 0.15, 0.02),
        "canvas": lambda: P.grime(P.mat("Canvas", (0.38, 0.4, 0.3), 0.9), 6.0, 0.75, 0.05, 0.05),
        "tyre": lambda: P.mat("Tyre", (0.05, 0.05, 0.05), 0.8),
        "rail_red": lambda: P.grime(P.mat("Rail paint", (0.55, 0.12, 0.1), 0.45, 0.3), 6.0, 0.6, 0.15, 0.02),
        "stair": lambda: P.grime(P.mat("Stair stone", (0.55, 0.54, 0.52), 0.6), 6.0, 0.75, 0.15, 0.03),
        "board": lambda: P.image("Chalkboard", os.path.join(TEX, "chalkboard.png"), 0.0, 0.85),
        "banner": lambda: P.image("Banner", os.path.join(TEX, "tv_banner.png"), 1.5, 0.5),
        "studio": lambda: P.mat("Studio", (0.12, 0.25, 0.5), 0.6, emit=(0.15, 0.3, 0.6), strength=1.2),
        "tv": lambda: P.mat("TV black", (0.03, 0.03, 0.035), 0.25),
        "screen_glass": lambda: P.mat("Screen glass", (0.0, 0.0, 0.0), 0.05, alpha=0.15),
        "sky_day": lambda: P.emit("Day light", (0.88, 0.93, 1.0), 2.5),
        "plant_pot": lambda: P.mat("Pot", (0.6, 0.35, 0.22), 0.7),
        "paper": lambda: P.mat("Paper", (0.9, 0.89, 0.85), 0.8),
        "notebook": lambda: P.mat("Notebook", (0.25, 0.4, 0.65), 0.6),
        "speaker": lambda: P.mat("Speaker", (0.85, 0.85, 0.82), 0.5),
        "panel": lambda: P.emit("Ceiling panel", (1.0, 0.98, 0.94), 6.0),
        "heli_glass": lambda: P.mat("Heli glass", (0.05, 0.07, 0.08), 0.05, 0.2),
    }
    M_[key] = mk[key]()
    return M_[key]


def room(c, w, d, h, wall, floor, ceil=None, skip=()):
    x, y, z = c
    P.box((x, y, z - 0.05), (w, d, 0.1), floor, "Floor")
    if ceil:
        P.box((x, y, z + h + 0.05), (w, d, 0.1), ceil, "Ceiling")
    for k, loc, size in (("N", (x, y + d / 2, z + h / 2), (w, 0.12, h)), ("S", (x, y - d / 2, z + h / 2), (w, 0.12, h)),
                         ("W", (x - w / 2, y, z + h / 2), (0.12, d, h)), ("E", (x + w / 2, y, z + h / 2), (0.12, d, h))):
        if k not in skip:
            P.box(loc, size, wall, f"Wall {k}")


def tree(loc, h=2.2, r=1.4):
    x, y, z = loc
    P.cyl((x, y, z), (x, y, z + h), 0.13, m("bark"), "Trunk", 10)
    rr = random.Random(int(x * 7 + y * 13))
    for k in range(6):
        P.sphere((x + rr.uniform(-0.6, 0.6), y + rr.uniform(-0.6, 0.6), z + h + rr.uniform(0.2, 1.2)),
                 r * rr.uniform(0.55, 0.8), m("leaves"), "Foliage")


# ==================================================================== sets
def build_house():
    room((HX, 0, 0), 8, 9, 5.6, m("plaster_w"), m("parquet"), m("ceiling"), skip=("S",))
    w = m("plaster_w")
    P.box((HX - 1.2, -4.5, 2.8), (5.6, 0.12, 5.6), w, "Front wall")
    P.box((HX + 3.4, -4.5, 2.8), (1.2, 0.12, 5.6), w, "Front wall")
    P.box((HX + 2.0, -4.5, 3.9), (1.6, 0.12, 3.4), w, "Above door")
    hinge = P.empty("Front door hinge", (HX + 1.55, -4.48, 0))
    door = P.box((HX + 2.0, -4.48, 1.1), (0.9, 0.06, 2.2), m("wood"), "Front door", bevel=0.01)
    P.parent_keep(door, hinge)
    P.plane((HX + 2.0, -6.0, 1.3), (4, 3.2), m("sky_day"), (D(90), 0, 0), "Outside light")
    for k in range(12):  # stairs down the west wall
        y = 3.3 - k * 0.3
        z = 2.8 - (k + 1) * 0.233
        P.box((HX - 3.3, y, z / 2), (1.2, 0.3, z), m("wood"), "Step")
    P.box((HX - 3.3, 4.0, 1.4), (1.2, 1.0, 2.8), m("wood"), "Landing")
    for k in range(0, 12, 2):
        y = 3.3 - k * 0.3
        z = 2.8 - (k + 1) * 0.233
        P.cyl((HX - 2.72, y, z), (HX - 2.72, y, z + 0.9), 0.02, m("frame_dark"), "Baluster", 8)
    P.cyl((HX - 2.72, 3.4, 3.7), (HX - 2.72, -0.3, 1.1), 0.035, m("wood"), "Handrail")
    # living room
    P.box((HX - 0.6, -0.6, 0.22), (2.1, 0.9, 0.44), m("sofa"), "Sofa seat", bevel=0.06)
    P.box((HX - 0.6, -0.12, 0.62), (2.1, 0.22, 0.8), m("sofa"), "Sofa back", bevel=0.06)
    for x in (-1.6, 0.4):
        P.box((HX + x, -0.6, 0.4), (0.22, 0.9, 0.5), m("sofa"), "Sofa arm", bevel=0.06)
    for x in (-1.1, -0.1):
        P.box((HX + x, -0.32, 0.6), (0.42, 0.14, 0.36), m("rug"), "Cushion", bevel=0.05)
    P.box((HX - 0.6, -2.0, 0.006), (2.6, 1.8, 0.012), m("rug"), "Rug")
    P.box((HX - 0.6, -1.9, 0.42), (1.0, 0.55, 0.04), m("wood"), "Coffee table")
    for dx in (-0.45, 0.45):
        for dy in (-0.22, 0.22):
            P.box((HX - 0.6 + dx, -1.9 + dy, 0.2), (0.04, 0.04, 0.4), m("wood"), "Table leg")
    P.cyl((HX - 0.75, -1.85, 0.44), (HX - 0.75, -1.85, 0.54), 0.04, P.mat("Cup", (0.9, 0.9, 0.88), 0.2), "Cup")
    # TV: flat panel with a small news studio set into it (the anchor is a real character)
    tvc = Vector((HX - 0.6, -4.25, 1.35))
    P.box(tvc + Vector((0, 0.05, -0.75)), (1.9, 0.42, 0.45), m("wood"), "TV unit", bevel=0.01)
    for sx in (-1, 1):
        P.box(tvc + Vector((sx * 0.83, 0.08, 0)), (0.04, 0.06, 0.98), m("tv"), "TV bezel")
    for sz in (-1, 1):
        P.box(tvc + Vector((0, 0.08, sz * 0.49)), (1.7, 0.06, 0.04), m("tv"), "TV bezel")
    P.box(tvc + Vector((0, -0.12, 0)), (1.62, 0.04, 0.96), m("studio"), "Studio wall")
    P.box(tvc + Vector((0, 0.0, -0.33)), (0.9, 0.12, 0.25), P.mat("News desk", (0.85, 0.86, 0.9), 0.3, emit=(0.4, 0.45, 0.55),
                                                                  strength=0.6), "News desk")
    P.plane(tvc + Vector((0, 0.07, -0.42)), (1.6, 0.16), m("banner"), (D(90), 0, 0), "Banner")
    P.plane(tvc + Vector((0, 0.11, 0)), (1.62, 0.96), m("screen_glass"), (D(90), 0, 0), "Screen glass")
    P.area_light(tvc + Vector((0, 0.05, 0.3)), tvc + Vector((0, -0.2, 0)), 8, 1.0, (0.8, 0.88, 1.0), name="TV studio light")
    P.area_light(tvc + Vector((0, 0.4, 0)), tvc + Vector((0, 3, 0)), 25, 1.6, (0.6, 0.75, 1.0), name="TV glow")
    # window, plant, frames
    P.window((HX + 3.94, 0.5, 1.8), 2.0, 1.4, "x", m("sky_day"), m("frame"))
    P.area_light((HX + 3.6, 0.5, 1.9), (HX, 0.5, 1.0), 400, 2.0, (1.0, 0.97, 0.92), 1.4, "Window light")
    P.cyl((HX + 3.0, -3.6, 0.0), (HX + 3.0, -3.6, 0.45), 0.2, m("plant_pot"), "Pot")
    for k in range(7):
        P.sphere((HX + 3.0 + random.uniform(-0.25, 0.25), -3.6 + random.uniform(-0.25, 0.25), 0.7 + k * 0.12), 0.22,
                 m("leaves"), "Plant")
    for k in range(3):
        P.box((HX + 1.0 + k * 0.7, 4.43, 1.8 + (k % 2) * 0.3), (0.5, 0.03, 0.4), m("frame"), "Frame")
        P.box((HX + 1.0 + k * 0.7, 4.41, 1.8 + (k % 2) * 0.3), (0.42, 0.02, 0.32),
              P.grime(P.mat(f"Art {k}", [(0.7, 0.55, 0.3), (0.35, 0.5, 0.6), (0.6, 0.35, 0.35)][k], 0.8), 3, 0.5), "Art")
    P.area_light((HX - 0.6, -1.0, 5.4), (HX - 0.6, -1.0, 0), 300, 3.0, (1.0, 0.93, 0.82), name="Ceiling light")
    return hinge


def build_street():
    P.box((SX + 4.0, 15, -0.06), (60, 90, 0.1), m("grass"), "Ground")
    P.box((SX + 1.2, 10, 0.06), (2.6, 60, 0.12), m("pavement"), "Sidewalk")
    P.box((SX + 6.0, 10, 0.0), (7.0, 60, 0.05), m("asphalt"), "Road")
    P.box((SX + 2.55, 10, 0.08), (0.15, 60, 0.16), m("concrete"), "Kerb")
    lane = P.mat("Lane paint", (0.85, 0.85, 0.8), 0.6)
    for y in range(-18, 40, 5):
        P.box((SX + 6.0, y, 0.03), (0.12, 2.0, 0.01), lane, "Lane")
    cols = [(0.82, 0.74, 0.62), (0.75, 0.72, 0.68), (0.85, 0.8, 0.66), (0.7, 0.62, 0.55), (0.8, 0.76, 0.72)]
    for k, y in enumerate(range(-16, 16, 6)):
        h = random.uniform(5.5, 8.5)
        mm = m("brick") if k % 2 else P.grime(P.mat(f"House {k}", cols[k], 0.85), 2.0, 0.8, 0.1, 0.03)
        P.box((SX - 3.5, y, h / 2), (4.5, 5.6, h), mm, "Row house")
        P.box((SX - 3.5, y, h + 0.1), (4.7, 5.8, 0.2), m("concrete"), "Roof edge")
        for wz in (1.5, 3.9) + ((6.3,) if h > 7.5 else ()):
            for wy in (-1.4, 1.4):
                P.box((SX - 1.23, y + wy, wz), (0.05, 1.0, 1.2), m("glass_dark"), "Window")
                P.box((SX - 1.2, y + wy, wz - 0.65), (0.12, 1.15, 0.08), m("concrete"), "Sill")
        P.box((SX - 1.22, y, 1.05), (0.06, 0.95, 2.1), m("wood"), "Door")
    for k, y in enumerate(range(-16, 16, 6)):  # houses across the road
        h = random.uniform(6, 9)
        mm = m("brick") if k % 2 == 0 else P.grime(P.mat(f"East house {k}", cols[(k + 2) % 5], 0.85), 2.0, 0.8, 0.1, 0.03)
        P.box((SX + 12.5, y, h / 2), (5, 5.6, h), mm, "East house")
        for wz in (1.5, 3.9, 6.3):
            if wz < h - 1:
                for wy in (-1.4, 1.4):
                    P.box((SX + 9.97, y + wy, wz), (0.05, 1.0, 1.2), m("glass_dark"), "Window")
    P.box((SX + 10.3, 10, 0.06), (2.6, 60, 0.12), m("pavement"), "Sidewalk east")
    for y in range(-14, 18, 7):
        tree((SX + 2.35, y, 0.1), 2.0, 1.3)
    P.box((SX - 2.5, 18.0, 1.2), (6.6, 0.4, 2.4), m("brick_y"), "School wall")
    P.box((SX + 3.6, 18.0, 1.2), (3.6, 0.4, 2.4), m("brick_y"), "School wall")
    gate = P.mat("Gate paint", (0.2, 0.3, 0.28), 0.4, 0.6)
    for k in range(9):
        P.cyl((SX + k * 0.22, 18.0, 0), (SX + k * 0.22, 18.0, 2.0), 0.018, gate, "Gate bar", 8)
    P.box((SX + 0.9, 18.0, 2.0), (2.0, 0.05, 0.06), gate, "Gate top")
    P.box((SX + 4.0, 26, 4.0), (16, 10, 8), m("brick_y"), "School building")
    for wx in range(-3, 4):
        for wz in (2.0, 5.2):
            P.box((SX + 4.0 + wx * 2.0, 20.97, wz), (1.2, 0.08, 1.4), m("glass_dark"), "Window")
    # plain olive army truck, no markings
    truck = P.empty("Truck", (SX + 4.5, -25, 0))
    parts = [P.box((SX + 4.5, -25 + 2.3, 1.3), (2.2, 1.6, 1.6), m("olive"), "Cab", bevel=0.08),
             P.box((SX + 4.5, -25 + 3.05, 1.65), (1.9, 0.08, 0.6), m("glass_dark"), "Windscreen"),
             P.box((SX + 4.5, -25 - 0.8, 1.75), (2.3, 4.2, 2.0), m("canvas"), "Canvas", bevel=0.15),
             P.box((SX + 4.5, -25 + 0.3, 0.75), (2.0, 6.4, 0.3), m("olive"), "Chassis")]
    for dy in (-2.0, -0.6, 2.3):
        for dx in (-1.0, 1.0):
            bpy.ops.mesh.primitive_cylinder_add(radius=0.48, depth=0.35, location=(SX + 4.5 + dx, -25 + dy, 0.48),
                                                rotation=(0, D(90), 0), vertices=24)
            o = bpy.context.object
            o.data.materials.append(m("tyre"))
            bpy.ops.object.shade_smooth()
            parts.append(o)
    for p in parts:
        P.parent_keep(p, truck)
    return truck


def build_classroom():
    wall, low = m("plaster"), m("wall_low")
    P.box((CX, 0, -0.05), (8, 9, 0.1), m("class_floor"), "Class floor")
    P.box((CX, 0, 3.25), (8, 9, 0.1), m("ceiling"), "Class ceiling")
    P.box((CX, 4.5, 1.6), (8, 0.12, 3.2), wall, "Front wall")
    P.box((CX, -4.5, 1.6), (8, 0.12, 3.2), wall, "Back wall")
    P.box((CX + 4.0, -1.0, 1.6), (0.12, 7.0, 3.2), wall, "East wall")
    P.box((CX + 4.0, 4.0, 1.6), (0.12, 1.0, 3.2), wall, "East wall")
    P.box((CX + 4.0, 3.0, 2.75), (0.12, 1.0, 0.9), wall, "Above door")
    dm = m("wood")
    P.box((CX + 4.0, 3.0, 0.6), (0.06, 0.96, 1.2), dm, "Door low")
    P.box((CX + 4.0, 3.0, 2.2), (0.06, 0.96, 0.2), dm, "Door top")
    for dy in (-0.4, 0.4):
        P.box((CX + 4.0, 3.0 + dy, 1.65), (0.06, 0.16, 0.9), dm, "Door side")
    door_glass = P.box((CX + 4.0, 3.0, 1.65), (0.015, 0.64, 0.9), P.mat("Door glass", (0.75, 0.82, 0.85), 0.05,
                                                                        alpha=0.25), "Door glass")
    P.box((CX + 4.03, 2.68, 1.0), (0.05, 0.04, 0.14), m("metal"), "Door handle")
    corr = P.grime(P.mat("Corridor", (0.45, 0.47, 0.5), 0.6), 2.0, 0.7)
    P.box((CX + 6.6, 3.0, 1.6), (0.12, 3.0, 3.2), corr, "Corridor back")
    for cy in (1.5, 4.5):
        P.box((CX + 5.3, cy, 1.6), (2.6, 0.12, 3.2), corr, "Corridor side")
    P.box((CX + 5.3, 3.0, 3.2), (2.6, 3.0, 0.1), corr, "Corridor ceiling")
    P.box((CX + 5.3, 3.0, -0.05), (2.6, 3.0, 0.1), m("class_floor"), "Corridor floor")
    P.area_light((CX + 5.6, 3.0, 3.1), (CX + 5.6, 3.0, 0), 120, 1.0, (0.8, 0.88, 1.0), name="Corridor light")
    # west wall: three big windows over the yard (open frames, no glass, so the yard reads clearly)
    for y0, y1 in ((-4.5, -3.4), (-1.6, -0.9), (0.9, 1.6), (3.4, 4.5)):
        P.box((CX - 4.0, (y0 + y1) / 2, 1.6), (0.25, y1 - y0, 3.2), wall, "West pillar")
    P.box((CX - 4.0, 0, 0.5), (0.25, 9, 1.0), wall, "Under windows")
    P.box((CX - 4.0, 0, 2.95), (0.25, 9, 0.5), wall, "Over windows")
    P.box((CX - 3.88, 0, 1.02), (0.12, 9, 0.04), m("frame"), "Sill")
    for yc in (-2.5, 0.0, 2.5):
        for dz in (1.04, 2.7):
            P.box((CX - 4.0, yc, dz), (0.08, 1.8, 0.05), m("frame"), "Window frame")
        for dy in (-0.9, 0.0, 0.9):
            P.box((CX - 4.0, yc + dy, 1.87), (0.08, 0.05, 1.7), m("frame"), "Window frame")
    for x in (-3.9, 3.9):
        P.box((CX + x, 0, 0.5), (0.05, 9, 1.0), low, "Lower paint")
    P.box((CX, 4.42, 0.5), (8, 0.05, 1.0), low, "Lower paint")
    P.box((CX, -4.42, 0.5), (8, 0.05, 1.0), low, "Lower paint")
    # board, clock, loudspeaker, map-free poster, drawings
    P.plane((CX, 4.42, 1.75), (3.6, 1.45), m("board"), (D(90), 0, D(180)), "Blackboard")
    P.box((CX, 4.44, 1.75), (3.8, 0.03, 1.6), m("wood"), "Board frame")
    P.box((CX, 4.36, 0.98), (3.6, 0.1, 0.03), m("wood"), "Chalk tray")
    bpy.ops.mesh.primitive_cylinder_add(radius=0.18, depth=0.04, location=(CX - 2.6, 4.42, 2.6), rotation=(D(90), 0, 0),
                                        vertices=32)
    clock = bpy.context.object
    clock.data.materials.append(P.mat("Clock face", (0.95, 0.95, 0.92), 0.3))
    hands = []
    ink = P.mat("Ink", (0.03, 0.03, 0.03), 0.5)
    for L, w in ((0.14, 0.012), (0.1, 0.018)):
        h = P.empty("Clock hand", (CX - 2.6, 4.39, 2.6))
        b = P.box((CX - 2.6, 4.39, 2.6 + L / 2), (w, 0.008, L), ink, "Clock hand")
        P.parent_keep(b, h)
        h.rotation_mode = "XYZ"
        hands.append(h)
    P.box((CX + 2.6, 4.36, 2.8), (0.45, 0.16, 0.3), m("speaker"), "Loudspeaker", bevel=0.02)
    for k in range(4):
        P.box((CX + 2.6, 4.275, 2.72 + k * 0.05), (0.32, 0.005, 0.015), ink, "Grille")
    for k in range(5):
        P.box((CX - 2.6 + k * 1.2, -4.42, 1.9 + (k % 2) * 0.25), (0.5, 0.01, 0.38),
              P.grime(P.mat(f"Drawing {k}", [(0.9, 0.75, 0.6), (0.7, 0.8, 0.65), (0.65, 0.72, 0.85), (0.9, 0.85, 0.6),
                                             (0.8, 0.7, 0.85)][k], 0.9), 6, 0.6), "Drawing")
    # desks + chairs
    moving = None
    for col in (-2.1, 0.0, 2.1):
        for row in (1.4, 0.0, -1.4, -2.8):
            d = P.empty("Desk", (CX + col, row + 0.35, 0))
            parts = [P.box((CX + col, row + 0.35, 0.73), (1.3, 0.5, 0.035), m("desk"), "Desk top", bevel=0.008)]
            for dx in (-0.6, 0.6):
                for dy in (-0.2, 0.2):
                    parts.append(P.box((CX + col + dx, row + 0.35 + dy, 0.36), (0.03, 0.03, 0.72), m("metal"), "Desk leg"))
            for dx in (-0.32, 0.32):
                parts.append(P.box((CX + col + dx, row - 0.12, 0.45), (0.4, 0.38, 0.03), m("chair"), "Chair seat"))
                parts.append(P.box((CX + col + dx, row - 0.31, 0.72), (0.4, 0.03, 0.4), m("chair"), "Chair back"))
                for ex in (-0.17, 0.17):
                    for ey in (-0.16, 0.16):
                        parts.append(P.box((CX + col + dx + ex, row - 0.12 + ey, 0.22), (0.02, 0.02, 0.44), m("metal"),
                                           "Chair leg"))
                parts.append(P.box((CX + col + dx + random.uniform(-0.1, 0.1), row + 0.38, 0.752), (0.21, 0.29, 0.008),
                                   m("notebook") if random.random() < 0.5 else m("paper"), "Notebook"))
            for p in parts:
                P.parent_keep(p, d)
            if col == 2.1 and row == 1.4:
                moving = d
    panels = []
    for x in (-2, 2):
        for y in (-2, 2):
            panels.append(P.box((CX + x, y, 3.19), (1.2, 0.6, 0.03), m("panel"), "Light panel"))
    room_light = P.area_light((CX, 0, 3.1), (CX, 0, 0), 450, 5.0, (1.0, 0.97, 0.92), 6.0, "Room light")
    win_light = P.area_light((CX - 3.7, 0, 1.9), (CX, 0, 0.8), 350, 7.0, (0.9, 0.95, 1.0), 1.8, "Window fill")
    return door_glass, moving, panels, room_light, win_light, hands


def build_yard():
    gz = -5.0
    P.box((CX - 14, 0, gz - 0.05), (22, 40, 0.1), m("pavement"), "Yard")
    P.box((CX - 12, 0, gz + 0.004), (10, 8, 0.008), P.grime(P.mat("Court", (0.55, 0.32, 0.26), 0.7), 5, 0.8), "Court")
    lines = P.mat("Court line", (0.9, 0.9, 0.88), 0.6)
    for y in (-3.8, 3.8):
        P.box((CX - 12, y, gz + 0.01), (10, 0.06, 0.004), lines, "Court line")
    P.box((CX - 3.0, 0, gz / 2), (2, 40, -gz), m("brick_y"), "Facade")
    P.box((CX - 21, -9, gz + 1.2), (0.4, 18, 2.4), m("brick_y"), "Yard wall")
    P.box((CX - 21, 11, gz + 1.2), (0.4, 14, 2.4), m("brick_y"), "Yard wall")
    gate = P.mat("Gate paint", (0.2, 0.3, 0.28), 0.4, 0.6)
    for k in range(11):
        P.cyl((CX - 21, -1.2 + k * 0.22, gz), (CX - 21, -1.2 + k * 0.22, gz + 2.2), 0.02, gate, "Gate bar", 8)
    P.box((CX - 21, 0, gz + 2.2), (0.06, 2.6, 0.06), gate, "Gate top")
    P.box((CX - 29, 0, gz - 0.04), (14, 60, 0.1), m("asphalt"), "Street")
    cols = [(0.82, 0.74, 0.62), (0.75, 0.72, 0.68), (0.85, 0.8, 0.66), (0.7, 0.62, 0.55)]
    for k in range(6):
        h = random.uniform(6, 10)
        mm = m("brick") if k % 2 else P.grime(P.mat(f"Yard house {k}", cols[k % 4], 0.85), 2.0, 0.8)
        P.box((CX - 38, -15 + k * 6, gz + h / 2), (6, 5.4, h), mm, "House")
        for wz in (1.6, 4.2, 6.8):
            if wz < h - 1:
                for wy in (-1.4, 1.4):
                    P.box((CX - 34.97, -15 + k * 6 + wy, gz + wz), (0.05, 1.0, 1.2), m("glass_dark"), "Window")
    for y in (-6, 7):
        tree((CX - 17, y, gz), 2.4, 1.6)
    return gz


def build_heli():
    heli = P.empty("Helicopter")
    b = m("olive")
    parts = [P.sphere((0, 0, 0), 1.3, b, "Heli body", (0.95, 2.0, 0.9)),
             P.sphere((0, 1.55, 0.1), 0.95, m("heli_glass"), "Heli canopy", (0.9, 0.8, 0.75)),
             P.cyl((0, -1.6, 0.35), (0, -6.0, 0.7), 0.22, b, "Tail boom"),
             P.box((0, -6.0, 1.1), (0.08, 0.7, 1.1), b, "Tail fin", bevel=0.02),
             P.cyl((-0.85, -1.3, -1.35), (-0.85, 1.6, -1.35), 0.05, m("metal"), "Skid"),
             P.cyl((0.85, -1.3, -1.35), (0.85, 1.6, -1.35), 0.05, m("metal"), "Skid"),
             P.box((0, -0.2, 1.2), (0.9, 1.6, 0.4), b, "Engine", bevel=0.1)]
    for sx in (-0.85, 0.85):
        for sy in (-0.6, 0.9):
            parts.append(P.cyl((sx, sy, -1.35), (sx * 0.7, sy, -0.7), 0.04, m("metal"), "Strut"))
    for p in parts:
        P.parent_keep(p, heli)
    rotor = P.empty("Rotor", (0, 0, 1.5))
    P.parent_keep(rotor, heli)
    for a in (0, 90):
        bl = P.box((0, 0, 1.5), (0.22, 9.5, 0.04), m("tyre"), "Blade")
        bl.rotation_euler = (0, 0, D(a))
        P.parent_keep(bl, rotor)
    rotor.rotation_mode = "XYZ"
    bpy.ops.object.light_add(type="SPOT", location=(0, 1.2, -1.0))
    spot = bpy.context.object
    spot.data.spot_size = D(40)
    spot.data.energy = 0
    spot.data.color = (1.0, 0.97, 0.9)
    P.parent_keep(spot, heli)
    return heli, rotor, spot


def build_stairs_roof():
    wall, step = m("concrete"), m("stair")
    for k in range(24):
        y = 0.3 * k
        z = 0.2 * (k + 1)
        P.box((RX + 0.55, y + 0.15, z / 2), (1.3, 0.3, z), step, "Step")
    P.box((RX + 0.55, 7.8, 2.4), (1.3, 0.8, 4.8), step, "Top landing")
    P.box((RX + 1.3, 3.8, 3.0), (0.15, 9, 6.0), wall, "Stair wall")
    P.box((RX - 1.5, 3.8, 1.0), (0.15, 9, 6.0), wall, "Shaft wall")
    P.box((RX - 0.5, -0.4, 1.0), (4, 0.15, 6.0), wall, "Stair back")
    P.box((RX - 0.1, 3.8, 6.0), (3.0, 9, 0.15), m("ceiling"), "Stair ceiling")
    for k in range(0, 24, 2):
        y = 0.3 * k + 0.15
        z = 0.2 * (k + 1)
        P.cyl((RX - 0.12, y, z), (RX - 0.12, y, z + 0.9), 0.015, m("rail_red"), "Railing post", 8)
    P.cyl((RX - 0.12, 0.1, 1.1), (RX - 0.12, 7.4, 5.7), 0.03, m("rail_red"), "Railing")
    P.box((RX - 0.7, 3.8, -1.6), (1.6, 9, 0.1), m("concrete"), "Shaft floor")
    for py in (1.5, 5.0):
        P.area_light((RX + 0.55, py, 5.8), (RX + 0.55, py, 0), 60, 0.6, (1.0, 0.45, 0.35), name="Emergency light")
    rz = 4.8
    P.box((RX, 20, rz - 0.1), (24, 24, 0.2), m("concrete"), "Roof")
    P.box((RX + 0.55, 8.25, rz + 2.2), (2.2, 0.15, 0.4), wall, "Roof hut lintel")
    for sx in (-1, 1):
        P.box((RX + 0.55 + sx * 1.1, 8.25, rz + 1.2), (0.15, 0.2, 2.4), wall, "Door frame")
    for sx, sy, w, d in ((0, 32, 24, 0.3), (0, 8.1, 24, 0.3), (-12, 20, 0.3, 24), (12, 20, 0.3, 24)):
        P.box((RX + sx, sy, rz + 0.5), (w, d, 1.0), wall, "Parapet")
    ac = P.mat("AC unit", (0.75, 0.75, 0.76), 0.4, 0.3)
    for k in range(4):
        P.box((RX - 8 + k * 5, 26, rz + 0.6), (1.2, 1.0, 1.2), ac, "AC unit", bevel=0.03)
    return rz


# ==================================================================== camera (same path as the cartoon)
def cam_at(t, push_desk_loc, rz):
    yaw, pitch, roll, amp = 180.0, 0.0, 0.0, 0.25
    E = 0.08  # realistic eye height correction
    if t < 11.0:
        if t < 6.0:
            u = seg(t, 3.0, 6.0)
            pos = Vector((HX - 3.3, lerp(3.9, -0.5, u), lerp(4.3, 1.5, u) + E))
            pos.z += 0.05 * abs(math.sin(math.pi * t * 2.4)) * (0 < u < 1)
            pitch = lerp(-22, -10, u)
        else:
            u = seg(t, 6.0, 9.4)
            pa, pb, pc = Vector((HX - 3.3, -0.5, 1.5 + E)), Vector((HX + 0.9, -1.9, 1.5 + E)), Vector((HX + 1.9, -3.6, 1.5 + E))
            pos = pa.lerp(pb, min(1, u * 1.6)) if u < 0.625 else pb.lerp(pc, (u - 0.625) / 0.375)
            pos.z += 0.04 * abs(math.sin(math.pi * t * 2.2))
            yaw = lerp(172, 212, seg(t, 6.0, 6.8))          # the TV while the news plays
            yaw = lerp(yaw, 46, seg(t, 7.9, 8.6))            # Mom on the sofa
            pitch = lerp(-8, -14, seg(t, 7.9, 8.6))
            yaw = lerp(yaw, 185, seg(t, 10.0, 10.5))         # the front door
            if t > 10.4:
                pos = pos.lerp(Vector((HX + 2.0, -4.9, 1.5 + E)), seg(t, 10.5, 11.0))
    elif t < 15.0:
        u = (t - 11.0) / 4.0
        pos = Vector((SX + 1.1, lerp(3.0, 16.6, u), 1.5 + E + 0.04 * abs(math.sin(math.pi * t * 2.4))))
        yaw = lerp(0, -55, seg(t, 11.5, 11.8) * (1 - seg(t, 12.4, 12.8)))
        pitch = -4
    elif t < 63.0:
        seat = Vector((CX - 0.32, -0.15, 1.18))
        pos = seat.copy()
        yaw, pitch = 0, 2
        yaw = lerp(yaw, -60, seg(t, 17.1, 17.4) * (1 - seg(t, 18.5, 18.8)))
        if 21.0 <= t < 28.0:
            pitch = lerp(2, -50, seg(t, 21.0, 21.5)) if t < 27.6 else lerp(-50, 2, seg(t, 27.6, 28.0))
        if 28.0 <= t < 33.0:
            yaw = lerp(0, -55, seg(t, 28.0, 28.4)) if t < 31.3 else lerp(-55, 0, seg(t, 31.3, 31.7))
            pitch = -12 if t < 31.3 else 2
            pos = pos + Vector((0, 0, 0.03 * math.sin(t * 20) * (29.0 < t < 31.0)))
        if 33.0 <= t < 39.0:
            yaw = lerp(0, -18, seg(t, 33.3, 33.7))
            pitch = lerp(2, 20, seg(t, 33.3, 33.7))
            yaw = lerp(yaw, 30, seg(t, 37.8, 38.3))
            pitch = lerp(pitch, 14, seg(t, 37.8, 38.3))
        if 39.0 <= t < 45.0:
            u = seg(t, 39.0, 39.9)
            pos = seat.lerp(Vector((CX - 3.62, 0.45, 1.62)), u)
            yaw = lerp(30, 90, u)
            pitch = lerp(14, -38, u)
            amp = 0.4
        if 45.0 <= t < 51.0:
            u = seg(t, 45.0, 46.2)
            pos = Vector((CX - 3.62, 0.45, 1.62)).lerp(Vector((CX + 1.6, 1.0, 1.55)), u)
            yaw = lerp(90, -60, seg(t, 45.0, 45.6))
            pitch = lerp(-38, 4, seg(t, 45.0, 45.6))
            if t > 47.4:
                d = push_desk_loc(t)
                pos = Vector((d.x - 0.75, d.y - 0.75, 1.5))
                pitch = -24
            amp = 0.5
        if 51.0 <= t < 57.0:
            pos = Vector((CX + 2.3, 1.7, 1.55)).lerp(Vector((CX - 1.6, -2.0, 1.3)), seg(t, 51.0, 52.4))
            yaw = lerp(-60, 135, seg(t, 51.0, 52.4))
            pitch = lerp(4, -24, seg(t, 51.0, 52.4))
            if t > 54.8:
                pitch = lerp(-24, -50, seg(t, 54.8, 55.1))
        if 57.0 <= t < 63.0:
            pos = Vector((CX - 1.6, -2.0, 1.3)).lerp(Vector((CX - 2.6, -0.4, 1.55)), seg(t, 57.0, 57.8))
            yaw = lerp(135, 92, seg(t, 57.2, 57.8))
            pitch = lerp(-24, 8, seg(t, 57.2, 57.8))
            yaw = lerp(yaw, 20, seg(t, 61.6, 62.0))
            pitch = lerp(pitch, 0, seg(t, 61.6, 62.0))
            amp = 0.5
    elif t < 69.0:
        u = (t - 63.0) / 6.0
        y = lerp(0.2, 7.6, u)
        pos = Vector((RX + 0.55, y, 0.2 * (y / 0.3) + 1.55 + 0.06 * abs(math.sin(math.pi * t * 3.2))))
        yaw, pitch = 0, 14
        yaw = lerp(yaw, 165, seg(t, 64.0, 64.4) * (1 - seg(t, 65.4, 65.8)))
        pitch = lerp(pitch, -25, seg(t, 64.0, 64.4) * (1 - seg(t, 65.4, 65.8)))
        amp = 1.0
    else:
        u = seg(t, 69.0, 70.4)
        pos = Vector((RX + 0.55, lerp(7.9, 9.3, u), rz + 1.52))
        yaw, pitch = 0, lerp(4, 0, u)
        amp = 0.8
        if t > 71.8:
            pos = pos + Vector((0, 0.25, -0.1)) * seg(t, 71.8, 72.4)
            pitch = lerp(0, -32, seg(t, 71.8, 72.4))
            pitch = lerp(pitch, 12, seg(t, 73.0, 73.6))
            amp = 0.2
    for te, k in ((37.2, 2.0), (43.4, 1.5), (45.6, 3.0), (51.0, 1.0), (73.0, 1.5)):
        if te <= t < te + 0.6:
            amp += k * (1 - (t - te) / 0.6)
    return pos, yaw, pitch, roll, amp


# ==================================================================== build this part
chars = []


def add(ch):
    chars.append(ch)
    return ch


house_door = truck = None
door_glass = push_desk = panels = room_light = win_light = clock_hands = None
heli = rotor = spot = None
gz, rz = -5.0, 4.8
if PART == "house":
    house_door = build_house()
    mom = add(cast.spawn("mom"))
    cast.add_prop(mom, "mug")
    anchor = add(cast.spawn("anchor"))
elif PART == "street":
    truck = build_street()
    rezaei = add(cast.spawn("rezaei"))
elif PART == "class":
    door_glass, push_desk, panels, room_light, win_light, clock_hands = build_classroom()
    gz = build_yard()
    heli, rotor, spot = build_heli()
    kazemi, arian, mahsa, kian = (add(cast.spawn(k)) for k in ("kazemi", "arian", "mahsa", "kian"))
    cast.add_prop(kazemi, "chalk")
    students = [add(cast.spawn_extra("student", i)) for i in range(7)]
    rezaei_z = add(cast.spawn("rezaei", zombie=1.0, name="RezaeiZ", quality="extra"))
    zombies = [add(cast.spawn_extra("passerby", i, zombie=1.0)) for i in range(6)]
else:
    rz = build_stairs_roof()
    heli, rotor, spot = build_heli()
    kazemi, arian, mahsa, kian = (add(cast.spawn(k)) for k in ("kazemi", "arian", "mahsa", "kian"))
    soldier = add(cast.spawn("soldier", bite=("lowerarm_r", (0, 0, 0), 0.22)))
    zombies = [add(cast.spawn_extra("passerby", i, zombie=1.0)) for i in (5, 6)]
    # the soldier's eyes turn: a second, dead pair of eyes swapped in at 72.9 s
    eyes = soldier.parts["Eyes"][0]
    dead = eyes.copy()
    dead.data = eyes.data.copy()
    dead.name = "Soldier dead eyes"
    for i, ms in enumerate(dead.material_slots):
        if ms.material:
            ms.material = ms.material.copy()
    sc.collection.objects.link(dead)
    cast.M.recolor(dead, lambda nt, c: cast.M.mix(nt, c, (0.85, 0.82, 0.74), 0.92))
    soldier_eyes = (eyes, dead)

SEATS = [(CX - 2.42, 1.4), (CX - 1.78, -1.4), (CX + 1.78, 1.4), (CX + 2.42, 0.0), (CX - 0.32, -1.4),
         (CX + 0.32, -2.8), (CX + 1.78, -1.4)]


def desk_loc(t):
    return Vector((CX + 2.1, 1.75, 0)).lerp(Vector((CX + 3.25, 3.0, 0)), seg(t, 47.5, 50.5))


# ==================================================================== animate
cam = bpy.data.objects.new("POV", bpy.data.cameras.new("POV"))
sc.collection.objects.link(cam)
sc.camera = cam
cam.data.lens = 22
cam.data.sensor_width = 36
cam.data.clip_start = 0.05
rnd = random.Random(4)
shake = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(-1, 1)) for _ in range(1805)]


def key(o, path, f, constant=False):
    o.keyframe_insert(path, frame=f)


for f in range(F0, F1 + 1):
    t = (f - 1) / FPS
    pos, yaw, pitch, roll, amp = cam_at(t, desk_loc, rz)
    sx_, sy_, sz_ = shake[f]
    cam.location = pos
    cam.rotation_euler = (D(90 + pitch + sx_ * amp), D(roll + sy_ * amp * 0.6), D(yaw + sz_ * amp))
    key(cam, "location", f)
    key(cam, "rotation_euler", f)

    if PART == "house":
        mom.animate(f, t, (HX - 0.6, -0.6, 0), 180, sit=1, arms="mug", look=(lerp(0, -70, seg(t, 9.9, 10.2)), -5),
                    worry=1.4, talking=talking("mom", t))
        anchor.animate(f, t, (HX - 0.6, -4.29, 0.95), 0, scale=0.33, arms="desk", look=(0, 0), worry=0.8,
                       talking=talking("anchor", t))
        house_door.rotation_euler = (0, 0, D(-100) * seg(t, 10.3, 10.8))
        key(house_door, "rotation_euler", f)
    elif PART == "street":
        w = seg(t, 13.5, 13.7) * (1 - seg(t, 14.8, 15.0))
        rezaei.animate(f, t, (SX + 0.9, 17.4, 0), 180, arms="wave" if w > 0.5 else "rest", look=(0, 5),
                       talking=talking("rezaei", t), smile=0.5)
        truck.location = (SX + 4.5, lerp(-12, 45, seg(t, 11.2, 13.6)), 0)
        key(truck, "location", f)
    elif PART == "class":
        # teacher
        writing = t < 15.4 or (16.9 < t < 18.6)
        k_pos, k_face, k_arms = Vector((CX + 0.6, 3.55, 0)), (0 if writing else 180), ("write" if writing else "chalk")
        if 45.0 <= t < 51.0:
            k_pos, k_face, k_arms = Vector((CX + 1.2, 3.6, 0)), -60, "push"
        if 51.0 <= t < 57.0:
            k_pos, k_face, k_arms = Vector((CX + 1.0, 2.0, 0)), 150, "rest"
        if 57.0 <= t < 63.0:
            k_pos, k_face, k_arms = Vector((CX + 2.8, 2.6, 0)), 135, ("wave" if t > 61.6 else "rest")
        kazemi.animate(f, t, k_pos, k_face, arms=k_arms, look=(0, 3), worry=0.9 if t < 33 else 1.6,
                       talking=talking("kazemi", t))
        # Arian, next to me
        a_pos, a_sit, a_face = Vector((CX + 0.32, -0.12, 0)), 1.0 if t < 39 else 0.0, 0
        a_look = (lerp(0, 60, seg(t, 17.0, 17.3) * (1 - seg(t, 18.6, 18.9))), 0)
        a_arms = "desk"
        if 28.0 <= t < 33.0:
            a_look = (65, -10)
        if 39.0 <= t < 45.0:
            a_pos, a_look, a_face, a_arms = Vector((CX - 3.25, -2.5, 0)), (0, -30), 90, "rest"
        if 45.0 <= t < 51.0:
            a_pos = Vector((CX + 2.7, 1.2, 0)) if t < 47.4 else desk_loc(t) + Vector((0.35, -0.75, 0))
            a_look, a_face, a_arms = (0, 0), -45, ("push" if t > 47.4 else "rest")
        if 51.0 <= t < 57.0:
            a_pos, a_look, a_face, a_arms = Vector((CX + 0.4, -2.4, 0)), (40, 0), 150, "rest"
        if 57.0 <= t < 63.0:
            a_pos, a_look, a_face = Vector((CX - 3.2, -2.3, 0)), (-90, 10), 90
            a_arms = "wave" if t > 60.2 else "rest"
        arian.animate(f, t, a_pos, a_face, sit=a_sit, arms=a_arms, look=a_look, worry=0.8 if t < 33 else 1.5,
                      talking=talking("arian", t), smile=0.6 if 29 < t < 31.5 else 0.0)
        # Mahsa, Kian
        m_pos, m_face, m_sit = Vector((CX - 1.78, 1.28, 0)), 0, 1.0
        if 39.0 <= t < 51.0:
            m_pos, m_face, m_sit = Vector((CX - 3.2, 2.3, 0)), 100, 0.0
        if t >= 51.0:
            m_pos, m_face, m_sit = Vector((CX - 1.3, -3.4, 0)), 150, 0.0
        mahsa.animate(f, t, m_pos, m_face, sit=m_sit, arms="desk" if m_sit else "rest",
                      look=((lerp(0, 150, seg(t, 28.5, 29) * (1 - seg(t, 31, 31.4))) if t < 33 else 0),
                            -25 if 39 <= t < 45 else 0), worry=1.6 if t > 33 else 0.6, talking=talking("mahsa", t))
        kc = seg(t, 51.0, 51.6)
        k2 = Vector((CX - 2.42, -0.12, 0)) if t < 39 else Vector((CX - 3.2, -1.95, 0))
        if t >= 51.0:
            k2 = Vector((CX - 3.3, -3.9, 0))
        kian.animate(f, t, k2, 0 if t < 39 else (95 if t < 51 else 45), sit=1.0 if t < 39 else 0.0, crouch=kc,
                     arms=("desk" if t < 39 else ("hug" if kc > 0.5 else "rest")),
                     look=(0, -30 if 39 <= t < 45 else 10), worry=1.8 if t > 33 else 1.0, talking=talking("kian", t))
        for i, s in enumerate(students):
            sx, sy = SEATS[i]
            hide = t >= 39.0
            cower = seg(t, 37.5, 38.2)
            p = Vector((sx, sy - 0.12, 0)) if not hide else Vector((CX - 0.6 + 0.75 * (i % 4), -3.75 + 0.7 * (i // 4), 0))
            s.animate(f, t, p, 0 if not hide else 160, sit=0 if hide else 1, crouch=0.6 if hide else 0,
                      arms=("hug" if (hide or cower > 0.5) else "desk"),
                      look=((20 * math.sin(i + t * 0.3)) if t < 33 else (-15, 25)[i % 2], 0),
                      worry=1.6 if t > 33 else 0.7)
        turn = seg(t, 42.9, 43.4)
        rezaei_z.animate(f, t, (CX - 15.5, 0.4, gz), lerp(90, -90, turn), arms="reach", reach=lerp(60, 85, turn),
                         look=(0, lerp(0, 35, turn)), scream=turn * (1 - seg(t, 44.5, 45)))
        for i, z in enumerate(zombies):
            wob = 6 * math.sin(t * 2.2 + i)
            if i < 5:
                z.animate(f, t, (CX - 22.0 - 0.3 * (i % 2), -1.6 + i * 0.8, gz), -90 + wob, arms="bang",
                          look=(0, 10 + wob), seed=i)
            else:
                appear = seg(t, 44.8, 45.2)
                broke = t > 45.6
                z.animate(f, t, (CX + 4.75 - 0.25 * appear - 0.2 * broke, 3.0, 0), 90,
                          arms="reach" if broke else "bang", reach=100, z_extra=-2.0 * (1 - appear), scream=float(broke))
        door_glass.hide_render = t >= 45.6
        key(door_glass, "hide_render", f)
        push_desk.location = desk_loc(t)
        key(push_desk, "location", f)
        lit = not (51.0 <= t < 63.0)
        for o in panels:
            o.hide_render = not lit
            key(o, "hide_render", f)
        room_light.data.energy = 450 if lit else 0
        key(room_light.data, "energy", f)
        win_light.data.energy = 350 if lit else 90
        key(win_light.data, "energy", f)
        clock_hands[0].rotation_euler = (0, D(90 + t * 6), 0)
        clock_hands[1].rotation_euler = (0, D(200 + t * 0.5), 0)
        for h in clock_hands:
            key(h, "rotation_euler", f)
        hp = Vector((CX - 30, 40, 10)).lerp(Vector((CX - 15.0, -1.0, 2.5)), seg(t, 56.8, 59.0))
        heli.location = hp
        heli.rotation_euler = (D(-6), D(4 * math.sin(t)), D(lerp(160, 185, seg(t, 56.8, 59.0))))
        key(heli, "location", f)
        key(heli, "rotation_euler", f)
        spot.data.energy = 30000 * seg(t, 57.5, 58.5)
        key(spot.data, "energy", f)
        rotor.rotation_euler = (0, 0, t * 28.0)
        key(rotor, "rotation_euler", f)
    else:  # stairs + roof
        y_me = lerp(0.2, 7.6, min(1, (t - 63.0) / 6.0))
        if t < 69.0:
            for p, dy, dx in ((kazemi, 3.0, 0.25), (mahsa, 2.0, -0.2), (arian, 1.05, 0.35)):
                yy = y_me + dy
                p.animate(f, t, (RX + 0.55 + dx, yy, min(rz, 0.2 * (yy / 0.3))), 0, run=1, phase=2 * math.pi * 1.7 * t,
                          arms="run", lean=8, worry=1.8, talking=talking(p.key, t))
            yk = max(0.0, y_me - 0.9)
            kian.animate(f, t, (RX + 0.6, yk, 0.2 * (yk / 0.3)), 0, run=1, phase=2 * math.pi * 2.0 * t, arms="hold",
                         lean=15, look=(0, 15), worry=2.0, talking=talking("kian", t))
        else:
            v = seg(t, 69.0, 72.0)
            for p, x0, y0 in ((kazemi, -1.5, 13.0), (mahsa, -0.6, 12.0), (arian, 0.6, 12.5), (kian, -0.45, 9.9)):
                kid = p is kian
                p.animate(f, t, (RX + x0, y0 + (0.4 * v if kid else 3.0 * v), rz), 0, run=0.3 if kid else 1,
                          phase=2 * math.pi * 1.6 * t, arms="run", lean=12, worry=1.8, look=(0, 20) if kid else (0, 0))
        soldier.animate(f, t, (RX + 0.78, 10.3, rz), 180, arm_r=(lerp(lerp(60, 88, seg(t, 69.8, 70.3)), 40, seg(t, 71.5, 72.1)), lerp(8, 25, seg(t, 71.5, 72.1))),
                        look=(0, -14), talking=talking("soldier", t), worry=0.0,
                        zombie=0.7 * seg(t, 73.0, 73.5), scream=seg(t, 73.6, 74.2))
        eyes, dead = soldier_eyes
        eyes.hide_render = t >= 72.9
        dead.hide_render = t < 72.9
        key(eyes, "hide_render", f)
        key(dead, "hide_render", f)
        for i, z in enumerate(zombies):
            if i == 0:
                z.animate(f, t, (RX - 0.65, 2.0 + 0.4 * math.sin(t), -0.2 + 0.4 * (t - 63)), 90, arms="reach",
                          reach=165, look=(0, 40), scream=1.0)
            else:
                z.animate(f, t, (RX - 0.7, 4.0, 0.8 + 0.3 * math.sin(t)), 90, arms="reach", reach=160, look=(0, 40))
        heli.location = (RX + 0.5, 19.0, rz + 1.6 + 0.15 * math.sin(t * 2))
        heli.rotation_euler = (0, 0, D(180))
        key(heli, "location", f)
        key(heli, "rotation_euler", f)
        rotor.rotation_euler = (0, 0, t * 28.0)
        key(rotor, "rotation_euler", f)

for ch in chars:
    ch.flush()
if PART == "roof":  # the dead eyes follow the soldier's head through his armature
    eyes, dead = soldier_eyes
    dead.parent = eyes.parent
    dead.matrix_parent_inverse = eyes.matrix_parent_inverse.copy()
    for md in dead.modifiers:
        if md.type == "ARMATURE":
            md.object = soldier.rig

# ==================================================================== world + render
w = bpy.data.worlds.new("World")
sc.world = w
bg = w.node_tree.nodes["Background"]
if PART in ("street", "roof", "class"):
    bpy.ops.object.light_add(type="SUN", rotation=(D(50), D(15), D(-40)))
    sun = bpy.context.object
    sun.data.angle = D(2)
    sun.data.color = (1.0, 0.94, 0.86)
    sun.data.energy = 3.5 if PART != "roof" else 1.6
    bg.inputs["Color"].default_value = (0.5, 0.6, 0.78, 1) if PART != "roof" else (0.5, 0.53, 0.58, 1)
    bg.inputs["Strength"].default_value = 1.0 if PART != "roof" else 0.8
    if PART == "class":  # power cut + storm light 51-63 s
        for fr, e, s in ((F0, 3.5, 1.0), (FPS * 51, 3.5, 1.0), (FPS * 51 + 1, 0.8, 0.35), (F1, 0.8, 0.35)):
            sun.data.energy = e
            sun.data.keyframe_insert("energy", frame=fr)
            bg.inputs["Strength"].default_value = s
            bg.inputs["Strength"].keyframe_insert("default_value", frame=fr)
else:
    bg.inputs["Color"].default_value = (0.6, 0.65, 0.72, 1)
    bg.inputs["Strength"].default_value = 0.25

sc.render.engine = "CYCLES"
sc.cycles.samples = 12
sc.cycles.use_denoising = True
sc.cycles.max_bounces = 4
sc.cycles.diffuse_bounces = 2
sc.cycles.glossy_bounces = 2
sc.cycles.transmission_bounces = 2
sc.cycles.transparent_max_bounces = 12
sc.cycles.caustics_reflective = sc.cycles.caustics_refractive = False
sc.cycles.blur_glossy = 1.0
sc.render.resolution_x, sc.render.resolution_y = 540, 960
sc.render.fps = FPS
sc.frame_start, sc.frame_end = F0, F1
sc.render.use_persistent_data = True
sc.view_settings.view_transform = "AgX"
sc.view_settings.look = "AgX - Medium High Contrast"
sc.render.image_settings.file_format = "PNG"

if "--save" in args:
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(HERE, f"last_bell_{PART}.blend"))
if "--still" in args:
    os.makedirs(os.path.join(HERE, "test"), exist_ok=True)
    for f in [int(x) for x in args[args.index("--still") + 1].split(",")]:
        sc.frame_set(f)
        sc.render.filepath = os.path.join(HERE, "test", f"{PART}_{f:04d}.png")
        bpy.ops.render.render(write_still=True)
if "--render" in args:
    os.makedirs(os.path.join(HERE, "frames"), exist_ok=True)
    sc.render.filepath = os.path.join(HERE, "frames", "f_")
    sc.render.use_overwrite = False
    sc.render.use_placeholder = True
    bpy.ops.render.render(animation=True)
