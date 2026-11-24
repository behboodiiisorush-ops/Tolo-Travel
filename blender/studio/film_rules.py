"""«قانون‌ها» — a POV night thriller in Arian's house (studio cast + modular house).

    ../cast/bpy.sh film_rules.py --still 30,250,...        -> test/r_XXXX.png
    ../cast/bpy.sh film_rules.py --render [a-b]            -> frames/rules/f_XXXX.png (skips frames already there)
Shots (seconds):
  1  0.0- 6.3 kitchen table, Arian + sandwich, front door crash, intruder at the opening
  2  6.3-17.0 under the table, rule 1 on my phone, Arian asks
  3 17.0-28.0 boots in the kitchen, rule 2, Arian wants to answer, I grab his arm
  4 28.0-40.0 rule 3, crawl through the hallway past the intruder to the bedroom
  5 40.0-50.0 bedroom, I close the door, Arian: mom is a journalist with a file
  6 50.0-57.6 rule 4, Arian climbs into the ceiling vent, I follow
  7 57.6-61.0 the duct
  8 61.0-75.5 we drop into the living room, Nina + laptop cameras, police lights, rule 5, Nina smiles
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
from captions import LINES, speaking, END  # noqa: E402

FPS = 24
N = int(END * FPS)
sc = bpy.context.scene
TEX = os.path.join(HERE, "textures")


def fr(t):
    return int(round(t * FPS)) + 1


def seg(t, a, b):
    x = min(1.0, max(0.0, (t - a) / (b - a)))
    return x * x * (3 - 2 * x)


def lerp(a, b, u):
    return a + (b - a) * u


def lerpv(a, b, u):
    return tuple(lerp(x, y, u) for x, y in zip(a, b))


def facing_of(d):
    return math.degrees(math.atan2(-d[0], d[1]))


class Path:
    """Polyline with arc-length lookup: position + facing (from a look-ahead tangent)."""
    def __init__(self, pts):
        self.p = [Vector((x, y, 0)) for x, y in pts]
        self.s = [0.0]
        for a, b in zip(self.p, self.p[1:]):
            self.s.append(self.s[-1] + (b - a).length)
        self.L = self.s[-1]

    def at(self, s):
        s = min(max(s, 0.0), self.L)
        for i in range(len(self.p) - 1):
            if s <= self.s[i + 1] or i == len(self.p) - 2:
                u = (s - self.s[i]) / max(1e-6, self.s[i + 1] - self.s[i])
                return self.p[i].lerp(self.p[i + 1], min(1.0, u))

    def facing(self, s, ahead=0.45):
        a, b = self.at(max(0.0, s - 0.05)), self.at(min(self.L, s + ahead))
        if (b - a).length < 1e-4:
            a, b = self.at(self.L - 0.5), self.at(self.L)
        return facing_of(b - a)


def unwrap(a, ref):
    while a - ref > 180:
        a -= 360
    while a - ref < -180:
        a += 360
    return a


# ================================================================== set
h = H.build()
CH, PRC, LC = h.C["CHARACTERS"], h.C["PROPS"], h.C["LIGHTING"]
M = h.M

# ceiling vents: a hole in the bedroom ceiling (in front of the wardrobe) and one in the living room
VENT_B = Vector((-3.3, 4.45))
VENT_L = Vector((2.3, 1.6))
for ob in [o for o in bpy.data.objects if o.name.startswith("Ceiling")]:
    for v in (VENT_B, VENT_L):
        lo, hi = ob.bound_box[0], ob.bound_box[6]
        mw = ob.matrix_world
        a, b = mw @ Vector(lo), mw @ Vector(hi)
        if a.x < v.x < b.x and a.y < v.y < b.y:
            cut = P.box((v.x, v.y, H.H_WALL + 0.05), (0.62, 0.62, 0.4), M["metal"], "vent cut")
            cut.hide_render = cut.hide_viewport = True
            bo = ob.modifiers.new("vent", "BOOLEAN")
            bo.object = cut
            bo.operation = "DIFFERENCE"
duct_m = P.grime(P.mat("Duct metal", (0.5, 0.52, 0.54), 0.4, 0.7), 6, 0.75, 0.1, 0.02)
for v in (VENT_B, VENT_L):     # vent frame trims
    for dx, dy, w_, d_ in ((-0.33, 0, 0.05, 0.71), (0.33, 0, 0.05, 0.71), (0, -0.33, 0.71, 0.05), (0, 0.33, 0.71, 0.05)):
        H.put(P.box((v.x + dx, v.y + dy, H.H_WALL - 0.01), (w_, d_, 0.03), M["trim"], "Vent frame"), PRC)
# bedroom grille, hinged on its +y edge (swings down when Arian pushes it)
gh = H.put(P.empty("Vent hinge", (VENT_B.x, VENT_B.y + 0.3, H.H_WALL - 0.02)), h.C["RIGS"])
gh.rotation_mode = "XYZ"
grille = P.box((VENT_B.x, VENT_B.y, H.H_WALL - 0.02), (0.6, 0.6, 0.015), M["trim"], "Vent grille")
for k in range(-5, 6):
    sl = P.box((VENT_B.x, VENT_B.y + k * 0.05, H.H_WALL - 0.035), (0.56, 0.012, 0.02), M["dark"], "Grille slat")
    P.parent_keep(sl, grille)
P.parent_keep(grille, gh)
H.put(grille, PRC)
# living-room grille already on the floor (they kicked it out from above)
H.put(P.box((VENT_L.x - 0.4, VENT_L.y - 0.35, 0.01), (0.6, 0.6, 0.015), M["trim"], "Vent grille floor", rot=(0, 0, 0.4)), PRC)
# the duct above the ceiling: from the bedroom vent east over the hallway
DZ = H.H_WALL + 0.12
dx0, dx1, dy = VENT_B.x - 0.4, 2.6, VENT_B.y
dl = dx1 - dx0
dparts = [P.box(((dx0 + dx1) / 2, dy, DZ - 0.015), (dl, 0.8, 0.03), duct_m, "Duct floor"),
          P.box(((dx0 + dx1) / 2, dy, DZ + 0.8), (dl, 0.8, 0.03), duct_m, "Duct roof"),
          P.box(((dx0 + dx1) / 2, dy - 0.4, DZ + 0.4), (dl, 0.03, 0.82), duct_m, "Duct wall"),
          P.box(((dx0 + dx1) / 2, dy + 0.4, DZ + 0.4), (dl, 0.03, 0.82), duct_m, "Duct wall"),
          P.box((dx0, dy, DZ + 0.4), (0.03, 0.8, 0.82), duct_m, "Duct end")]
x = dx0 + 0.3
while x < dx1:                 # seams / ribs
    for (oy, oz, sw, sh) in ((-0.385, 0.4, 0.02, 0.82), (0.385, 0.4, 0.02, 0.82), (0, 0.785, 0.8, 0.02), (0, 0.0, 0.8, 0.012)):
        dparts.append(P.box((x, dy + oy, DZ + oz), (0.03, sw, sh), M["metal"], "Duct rib"))
    x += 0.6
cut = P.box((VENT_B.x, VENT_B.y, DZ), (0.62, 0.62, 0.2), M["metal"], "duct cut")
cut.hide_render = cut.hide_viewport = True
bo = dparts[0].modifiers.new("hole", "BOOLEAN")
bo.object = cut
bo.operation = "DIFFERENCE"
slit_m = P.emit("Slit light", (1.0, 0.85, 0.6), 6.0)
for sx in (-1.2, 0.8):         # light leaking up through grilles in the duct floor
    for k in range(5):
        dparts.append(P.box((sx, dy - 0.12 + k * 0.06, DZ + 0.002), (0.4, 0.02, 0.004), slit_m, "Duct slit"))
    li = P.area_light((sx, dy, DZ + 0.05), (sx, dy, DZ + 1.0), 6, 0.35, (1.0, 0.85, 0.6), name="Duct slit light")
    H.put(li, LC)
for o in dparts:
    H.put(o, h.C["ENVIRONMENT"])
# dark cap above the living-room hole
H.put(P.box((VENT_L.x, VENT_L.y, H.H_WALL + 0.5), (0.9, 0.9, 0.04), duct_m, "Vent box top"), h.C["ENVIRONMENT"])

# props: sandwich + plate, laptop, desk chair in the bedroom
bread = P.mat("Bread", (0.82, 0.62, 0.36), 0.8)
sandwich = P.empty("Sandwich", (-2.62, 2.12, 0.98))
for z, sz, m in ((-0.022, 0.024, bread), (0.0, 0.016, P.mat("Lettuce", (0.3, 0.6, 0.2), 0.7)),
                 (0.012, 0.012, P.mat("Cheese", (0.95, 0.75, 0.25), 0.6)), (0.03, 0.024, bread)):
    o = P.box((-2.62, 2.12, 0.98 + z), (0.13, 0.11, sz), m, "Sandwich layer", bevel=0.008)
    P.parent_keep(o, sandwich)
    H.put(o, PRC)
H.put(P.cyl((-2.62, 2.15, 0.775), (-2.62, 2.15, 0.785), 0.12, M["trim"], "Plate", 24), PRC)
lap = P.empty("Laptop", (3.0, 3.25, 0.405))
lap.rotation_mode = "XYZ"
lbase = P.box((3.0, 3.25, 0.415), (0.36, 0.25, 0.018), M["dark"], "Laptop base", bevel=0.004)
lscr = P.box((3.0, 3.25 - 0.125 - 0.004, 0.53), (0.36, 0.012, 0.235), M["dark"], "Laptop lid", rot=(math.radians(-12), 0, 0))
cam_m = P.image("Laptop cams", os.path.join(TEX, "laptop_cams.png"), strength=2.2)
lpix = P.plane((3.0, 3.25 - 0.125 - 0.012, 0.53), (0.33, 0.21), cam_m, (math.radians(90 - 12), 0, math.pi), "Laptop screen")
for o in (lbase, lscr, lpix):
    P.parent_keep(o, lap)
    H.put(o, PRC)
lap.rotation_euler.z = math.pi            # screen faces Nina first
lap_light = P.area_light((3.0, 3.1, 0.6), (3.0, 4.4, 0.9), 0, 0.3, (0.7, 1.0, 0.8), name="Laptop glow")
H.put(lap_light, LC)
H.put(P.box((-1.25, 4.85, 0.45), (0.42, 0.42, 0.04), M["furn"], "Desk chair seat"), h.C["FURNITURE"])
H.put(P.box((-1.25, 5.04, 0.72), (0.42, 0.04, 0.52), M["furn"], "Desk chair back"), h.C["FURNITURE"])

# ================================================================== cast
me = pov.POV("me", name="Me")
arian = C.spawn("arian")
nina = C.spawn("nina")
i1 = C.spawn("intruder", name="Intruder1")
i2 = C.spawn("intruder", name="Intruder2")
for ch in (me, arian, nina, i1, i2):
    for o in ch.objects:
        H.put(o, CH)

# doors
front, bed_door, liv_door = h.doors["front"], h.doors["bedroom"], h.doors["living"]
front.swing(fr(3.0), fr(3.0) + 4, 0, 105)                 # kicked in
bed_door.swing(1, 2, 75, 75)
bed_door.swing(fr(40.7), fr(41.9), 75, 0)                 # I close it
bed_door.press_handle(fr(41.9), hold=10)
gh.rotation_euler.x = 0
gh.keyframe_insert("rotation_euler", index=0, frame=fr(53.7))
gh.rotation_euler.x = math.radians(-105)
gh.keyframe_insert("rotation_euler", index=0, frame=fr(54.1))
lap.keyframe_insert("rotation_euler", index=2, frame=fr(62.6))
lap.rotation_euler.z = 0
lap.keyframe_insert("rotation_euler", index=2, frame=fr(63.5))
# sandwich: in my hand, dropped on the plate when the door crashes
for t_, p_ in ((0.0, (-2.62, 2.12, 0.98)), (1.4, (-2.6, 2.1, 1.02)), (2.6, (-2.62, 2.12, 0.99)), (3.1, (-2.62, 2.12, 0.99)),
               (3.35, (-2.62, 2.15, 0.81))):
    sandwich.location = p_
    sandwich.keyframe_insert("location", frame=fr(t_))

# paths
me_crawl = Path([(-3.2, 2.3), (-1.6, 2.0), (-0.45, 1.8), (0.0, 2.15), (0.0, 4.55), (-0.45, 5.0), (-1.3, 5.0)])
ar_crawl = Path([(-1.15, 2.65), (-0.9, 1.9), (-0.1, 1.85), (0.05, 2.4), (0.05, 4.6), (-0.5, 5.05), (-1.9, 5.25)])
i1_in = Path([(0.0, -0.4), (0.0, 1.7), (-0.4, 1.72)])
i1_kitchen = Path([(-0.2, 1.7), (-1.0, 1.5), (-1.55, 1.25)])
i1_out = Path([(-1.55, 1.25), (-0.9, 1.6), (-0.05, 1.3), (0.0, 0.55)])
duct_me = Path([(VENT_B.x + 0.25, dy), (0.3, dy)])
duct_ar = Path([(VENT_B.x + 1.3, dy), (2.0, dy)])

UPS = [(9.0, 11.8, "rule1"), (20.1, 22.4, "rule2"), (28.4, 30.8, "rule3"), (50.2, 52.6, "rule4"), (70.0, 72.8, "rule5")]


def phone_up(t):
    return max(seg(t, a - 0.45, a) * (1 - seg(t, b, b + 0.45)) for a, b, _ in UPS)


CAM_H = 1.62   # rough eye height when standing (for look_at targets)


def me_state(t):
    """-> (pos, facing, kwargs) of my body at time t."""
    if t < 6.3:                                                     # 1: at the table
        rise = seg(t, 5.5, 6.3)
        yaw = lerp(-24 + 3 * math.sin(t * 0.8), -82, seg(t, 3.0, 3.35)) * (1 - seg(t, 5.4, 5.9))
        pitch = lerp(-10, -2, seg(t, 3.0, 3.35)) * (1 - seg(t, 5.4, 5.9)) - 30 * seg(t, 5.5, 6.2)
        return (-2.8, 1.92, 0), 0, dict(sit=1 - 0.45 * rise, lean=25 * rise, arms="rest", look=(yaw, pitch))
    if t < 30.8:                                                    # 2-3: under the table
        ph = 0.3
        yaw, pitch = 22, 2                                          # Arian
        yaw = lerp(yaw, -40, seg(t, 16.9, 17.4))                    # the boots
        yaw = lerp(yaw, 22, seg(t, 22.4, 22.9))
        pitch = lerp(pitch, -4, seg(t, 16.9, 17.4) * (1 - seg(t, 22.4, 22.9)))
        if t < 7.2:
            yaw, pitch = lerp(-20, 22, seg(t, 6.3, 7.1)), lerp(-12, 2, seg(t, 6.3, 7.1))
        if phone_up(t) > 0:
            pitch = lerp(pitch, -6, phone_up(t))
        fw = 0.08 * seg(t, 24.3, 24.7) * (1 - seg(t, 26.8, 27.4))  # lean to grab Arian
        p = Vector((-3.2 + fw, 2.3, 0))
        return tuple(p), -90, dict(crawl=1, arms="crawl", phase=ph, look=(yaw, pitch))
    if t < 40.0:                                                    # 4: crawl
        s = me_crawl.L * seg(t, 30.9, 39.9) if t < 39.9 else me_crawl.L
        speed = 1 - abs(2 * seg(t, 30.9, 39.9) - 1) ** 6
        p = me_crawl.at(s)
        f = lerp(-90, unwrap(me_crawl.facing(s), -90), seg(t, 30.9, 31.5))
        yaw = -55 * seg(t, 32.6, 33.2) * (1 - seg(t, 34.4, 35.0))  # glance right at the man at the front door
        return tuple(p), f, dict(crawl=1, arms="crawl", phase=2 * math.pi * s / 0.62, look=(yaw, 10 + 4 * speed))
    if t < 50.0:                                                    # 5: bedroom
        turn = seg(t, 42.0, 42.9)
        f = lerp(-90, 59, turn)
        pitch = -8 if t < 42 else -4
        return (-1.25, 5.0, 0), f, dict(arms="rest", look=(0, pitch), walk=0.35 * (seg(t, 41.9, 42.2) - seg(t, 42.7, 43.0)),
                                       phase=2 * math.pi * 0.9 * t)
    if t < 57.6:                                                    # 6: wardrobe + vent
        u = seg(t, 52.5, 53.7)
        p = lerpv((-1.25, 5.0, 0), (-2.65, 4.62, 0), u)
        f = lerp(62, 108, seg(t, 52.4, 52.9))
        up = seg(t, 53.4, 53.9)
        pitch = lerp(-6, 42, up) + 12 * seg(t, 56.2, 56.8)
        walk = 1 - abs(2 * u - 1) ** 4 if 52.5 < t < 53.7 else 0
        st = dict(arms="boost" if 53.9 < t < 55.9 else "rest", look=(0, pitch), walk=walk, phase=2 * math.pi * 0.95 * t)
        z = 0.0
        if t > 56.6:                                                # I climb after him
            p = lerpv(p, (VENT_B.x + 0.3, VENT_B.y + 0.05, 0), seg(t, 56.6, 57.3))
            z = 0.9 * seg(t, 56.8, 57.6)
            st["arms"] = "boost"
        return p, f, dict(st, z_extra=z)
    if t < 61.0:                                                    # 7: duct
        s = duct_me.L * seg(t, 57.6, 61.2) * 0.85
        return (*duct_me.at(s).xy, DZ), -90, dict(crawl=1, arms="crawl", phase=2 * math.pi * s / 0.6, look=(0, 12), z0=True)
    # 8: living room
    land = seg(t, 61.0, 61.35)
    crouch = 0.75 * (1 - seg(t, 61.5, 62.3))
    u = seg(t, 62.3, 63.4)
    p = lerpv((2.3, 1.65, 0), (2.5, 2.2, 0), u)
    f = lerp(5, -12, u)
    yaw, pitch = lerp(-25, 0, seg(t, 61.6, 62.4)), lerp(-10, -28, seg(t, 62.0, 62.8)) + 10 * seg(t, 66.6, 67.2)
    if t > 67.1:   # police lights: look at the side window
        k = seg(t, 67.2, 67.8) * (1 - seg(t, 69.2, 69.8))
        f = lerp(f, -55, k)
        yaw, pitch = lerp(yaw, -55, k), lerp(pitch, 0, k)
    if t > 72.8:
        pitch = lerp(pitch, -13, seg(t, 72.8, 73.4))
    walk = 1 - abs(2 * u - 1) ** 4 if 62.3 < t < 63.4 else 0
    return p, f, dict(crouch=crouch, arms="rest", look=(yaw, pitch), walk=walk, phase=2 * math.pi * 0.95 * t,
                      z_extra=0.45 * (1 - land))


def cam_point(t):
    p, f, st = me_state(t)
    if st.get("crawl"):
        return Vector((p[0], p[1], p[2] + 0.6)) + Vector((-math.sin(math.radians(f)), math.cos(math.radians(f)), 0)) * 0.5
    return Vector((p[0], p[1], CAM_H * (0.72 if st.get("sit", 0) > 0.5 else 1.0) + st.get("z_extra", 0)))


def ar_state(t):
    if t < 6.3:
        stand = seg(t, 5.4, 6.3)
        look_at = cam_point(t) if t < 3.0 else Vector((-0.7, 1.7, 1.5))
        return (-2.3, 3.02, 0), 180, dict(sit=1 - 0.5 * stand, lean=20 * stand, arms="desk" if t < 3 else "rest", seed=3,
                                          look_at=look_at, brows="neutral" if t < 3 else "surprised",
                                          mouth=dict(smile=0.3, frown=0) if t < 3 else dict(o=0.5 * seg(t, 3.0, 3.3), frown=0.1),
                                          worry=0 if t < 3 else 1.5, talking=speaking("arian", t))
    if t < 30.7:
        lunge = 0.2 * seg(t, 22.9, 23.8) * (1 - seg(t, 25.2, 26.2))
        f = lerp(105, 70, seg(t, 22.9, 23.6) * (1 - seg(t, 25.0, 25.8)))
        la = cam_point(t)
        if 17.2 < t < 22.4:
            la = Vector((-1.4, 1.4, 0.4))
        return (-1.15 + lunge, 2.65, 0), f, dict(crawl=1, arms="crawl", phase=0.9, look_at=la, brows="worried", worry=1.5,
                                                talking=speaking("arian", t), look=(0, 15), mouth=dict(frown=0.1))
    if t < 40.0:
        s = ar_crawl.L * seg(t, 30.7, 39.0) if t < 39.0 else ar_crawl.L
        f = lerp(105, unwrap(ar_crawl.facing(s), 105), seg(t, 30.7, 31.3))
        return tuple(ar_crawl.at(s)), f, dict(crawl=1, arms="crawl", phase=2 * math.pi * s / 0.62,
                                                              look=(0, 12), brows="worried", worry=1.5)
    if t < 50.0:
        la = cam_point(t) + Vector((0, 0, 0.05))
        return (-2.4, 5.7, 0), 239, dict(arms="rest", look_at=la, brows="worried", worry=1.4, mouth=dict(frown=0.1),
                                         talking=speaking("arian", t))
    if t < 57.6:
        u = seg(t, 52.4, 53.6)
        p = lerpv((-2.4, 5.7, 0), (VENT_B.x, VENT_B.y, 0), u)
        f = lerp(239, 90, seg(t, 52.3, 52.7))
        walk = 1 - abs(2 * u - 1) ** 4 if 52.4 < t < 53.6 else 0
        rise = seg(t, 54.0, 56.3)
        st = dict(arms="boost" if t > 53.6 else "rest", walk=walk, phase=2 * math.pi * 0.95 * t, look=(0, 40 * seg(t, 53.4, 53.8)),
                  climb=0.8 * (seg(t, 54.0, 54.3) - seg(t, 56.0, 56.3)), brows="worried", worry=1.2)
        return p, f, dict(st, z_extra=2.0 * rise)
    if t < 61.0:
        s = duct_ar.L * seg(t, 57.0, 61.0) * 0.8
        return (*duct_ar.at(s).xy, DZ), -90, dict(crawl=1, arms="crawl", phase=2 * math.pi * s / 0.6, look=(0, 10), z0=True)
    la = Vector((3.0, 4.4, 1.0)) if t < 67.2 else (Vector((5.7, 2.5, 1.4)) if t < 69.6 else cam_point(t))
    return (1.85, 2.5, 0), 40, dict(arms="rest", look_at=la, brows="worried", worry=1.2)


def nina_state(t):
    la = Vector((3.0, 3.25, 0.5)) if t < 62.0 else cam_point(t)
    if 67.2 < t < 69.4:
        la = Vector((5.7, 2.5, 1.4))
    reach = seg(t, 62.3, 62.7) * (1 - seg(t, 63.5, 63.9))
    sm = 0.5 * seg(t, 73.6, 74.4)
    st = dict(sit=1, arms="reach" if reach > 0.01 else "rest", reach=lerp(10, 62, reach), look_at=la,
              brows="surprised" if 61.2 < t < 62.6 else ("neutral" if t > 73.2 else "worried"),
              talking=speaking("nina", t), worry=0.6 if t < 73 else 0.0, mouth=dict(smile=sm, frown=0.05), suspicious=t > 73.4,
              lean=18 * reach)
    return (3.0, 4.42, 0), 180, st


def i1_state(t):
    hid = t < 3.0 or 6.9 < t < 17.0 or t > 40.0
    if t < 4.3:
        s = i1_in.L * seg(t, 3.0, 4.3)
        p, f = i1_in.at(s), i1_in.facing(s)
        st = dict(walk=1 - seg(t, 4.0, 4.3), phase=2 * math.pi * 1.1 * t)
    elif t < 17.0:
        p, f = i1_in.at(i1_in.L), 90 + 15 * math.sin(t * 1.7)
        st = dict()
    elif t < 26.4:
        u = seg(t, 17.0, 18.6)
        s = i1_kitchen.L * u
        p = i1_kitchen.at(s)
        f = i1_kitchen.facing(s) if t < 18.6 else lerp(i1_kitchen.facing(i1_kitchen.L), 20, seg(t, 18.6, 19.4))
        f += 25 * math.sin(t * 0.9) * seg(t, 20, 21)
        st = dict(walk=1 - abs(2 * u - 1) ** 4 if t < 18.6 else 0, phase=2 * math.pi * 1.0 * t)
    elif t < 40.0:
        u = seg(t, 26.4, 29.2)
        s = i1_out.L * u
        p = i1_out.at(s)
        f = unwrap(i1_out.facing(s), 180) if t < 29.2 else 180 + 20 * math.sin(t * 0.8)
        st = dict(walk=1 - abs(2 * u - 1) ** 4 if t < 29.2 else 0, phase=2 * math.pi * 1.0 * t)
    else:
        p, f, st = Vector((0, -3, 0)), 0, {}
    st.update(arms="reach", reach=62, hands="grip", brows="angry", talking=speaking("intruder", t))
    return tuple(p), f, st, hid


def i2_state(t):
    hid = not (3.3 < t < 6.4)
    s = 7.0 * seg(t, 3.3, 6.4)
    p = Vector((0.12, -0.4 + s, 0))
    return tuple(p), 0, dict(walk=1, phase=2 * math.pi * 1.1 * t, arms="reach", reach=55, hands="grip"), hid


# ---------------------------------------------------------------- animate everything
for f in range(1, N + 1):
    t = (f - 1) / FPS
    p, fa, st = me_state(t)
    z0 = st.pop("z0", False)
    zx = st.pop("z_extra", 0.0)
    if z0:
        p, zx = (p[0], p[1], 0), p[2]
    hnd = "grip" if phone_up(t) > 0.3 else ("relaxed" if not st.get("crawl") else "open")
    me.animate(f, t, p, fa, z_extra=zx, hands=hnd, **st)
    p, fa, st = ar_state(t)
    z0 = st.pop("z0", False)
    zx = st.pop("z_extra", 0.0)
    if z0:
        p, zx = (p[0], p[1], 0), p[2]
    arian.hide(f, 56.4 < t < 57.6 or (t > 57.6 and t < 61.0 and False))
    arian.animate(f, t, p, fa, z_extra=zx, hands="open" if st.get("crawl") or st.get("arms") == "boost" else "relaxed", **st)
    nina.hide(f, t < 61.0)
    p, fa, st = nina_state(t)
    nina.animate(f, t, p, fa, hands="grip" if st["arms"] == "reach" else "relaxed", **st)
    for ch, fn in ((i1, i1_state), (i2, i2_state)):
        p, fa, st, hid = fn(t)
        hands = st.pop("hands", "grip")
        ch.hide(f, hid)
        ch.animate(f, t, p, fa, hands=hands, **st)
for ch in (me, arian, nina, i1, i2):
    ch.flush()
cam_keys = []
for f in range(1, N + 1):
    t = (f - 1) / FPS
    p, fa, st = me_state(t)
    yaw, pitch = st.get("look", (0, 0))
    ph = st.get("phase", 0)
    mv = st.get("walk", 0) + (0.6 if st.get("crawl") and 30.9 < t < 39.9 or 57.6 < t < 61 else 0)
    roll = 1.2 * math.sin(ph) * mv
    crawl = st.get("crawl", 0)
    cam_keys.append((f, fa + yaw, pitch, roll, 0.05 if crawl else 0.1, 0.16 if crawl else 0.09))
pov.drive_camera(me, cam_keys)
sc.camera = me.cam
for t_, L_ in ((0, 17), (73.3, 17), (75.4, 23)):
    me.cam.data.lens = L_
    me.cam.data.keyframe_insert("lens", frame=fr(t_))
H.put(me.cam, h.C["CAMERAS"])

# ---------------------------------------------------------------- flashlights (hand-held, aimed at keyed targets)
torch_m = P.mat("Torch", (0.05, 0.05, 0.06), 0.4, 0.6)
lens_m = P.emit("Torch lens", (1.0, 0.97, 0.9), 25)


def flashlight(ch, aims, name):
    bpy.context.scene.frame_set(1)
    bpy.context.view_layer.update()
    rig = ch.rig
    pb = rig.pose.bones["hand_r"]
    mw = rig.matrix_world @ pb.matrix
    base = mw.translation + mw.to_3x3() @ Vector((0, 0.08, 0))
    tip = base + mw.to_3x3() @ Vector((0, 0.2, 0))
    body = P.cyl(base, tip, 0.022, torch_m, f"{name} torch")
    lens = P.cyl(tip, tip + (tip - base).normalized() * 0.006, 0.026, lens_m, f"{name} lens")
    P.parent_keep(lens, body)
    c = body.constraints.new("CHILD_OF")
    c.target = rig
    c.subtarget = "hand_r"
    bpy.context.view_layer.update()
    c.inverse_matrix = mw.inverted()
    tgt = P.empty(f"{name} aim")
    for t_, loc in aims:
        tgt.location = loc
        tgt.keyframe_insert("location", frame=fr(t_))
    bpy.ops.object.light_add(type="SPOT", location=tip)
    sp = bpy.context.object
    sp.name = f"{name} beam"
    sp.data.energy = 260
    sp.data.spot_size = math.radians(32)
    sp.data.spot_blend = 0.35
    sp.data.shadow_soft_size = 0.02
    sp.data.color = (1.0, 0.95, 0.85)
    sp.parent = body
    sp.matrix_parent_inverse = body.matrix_world.inverted()
    tr = sp.constraints.new("TRACK_TO")
    tr.target = tgt
    tr.track_axis = "TRACK_NEGATIVE_Z"
    tr.up_axis = "UP_Y"
    for o in (body, lens):
        H.put(o, PRC)
    H.put(sp, LC)
    return sp


b1 = flashlight(i1, [(3.0, (0, 4, 1.0)), (4.3, (-2.0, 1.8, 0.8)), (5.2, (-2.6, 2.6, 0.9)), (6.2, (-2.2, 2.2, 0.4)),
                     (17.0, (-1.8, 1.6, 0.3)), (19.0, (-2.6, 2.0, 0.2)), (21.0, (-3.4, 1.2, 0.6)), (23.0, (-3.0, 3.4, 0.4)),
                     (25.0, (-2.0, 3.6, 0.3)), (26.4, (-0.5, 1.7, 0.6)), (29.2, (0.0, -3.0, 0.8)), (33.0, (-0.8, -3.0, 0.4)),
                     (37.0, (0.8, -3.0, 0.6)), (40.0, (0, -3, 0.5))], "I1")
b2 = flashlight(i2, [(3.3, (0, 3, 1.0)), (6.4, (0.3, 9, 0.6))], "I2")
for sp, fn in ((b1, i1_state), (b2, i2_state)):     # beams off while their owner is hidden
    last = None
    for f in range(1, N + 1):
        hid = fn((f - 1) / FPS)[3]
        if hid != last:
            if last is not None:
                sp.data.energy = 0 if last else 260
                sp.data.keyframe_insert("energy", frame=f - 1)
            sp.data.energy = 0 if hid else 260
            sp.data.keyframe_insert("energy", frame=f)
            last = hid

# ---------------------------------------------------------------- my phone (parented to the camera, right hand on it)
phone = P.empty("Phone")
phone.parent = me.cam
pb_m = P.mat("Phone body", (0.04, 0.04, 0.05), 0.3, 0.4)
pbody = P.box((0, 0, -0.005), (0.074, 0.152, 0.009), pb_m, "Phone body", bevel=0.006)
pbody.parent = phone
screens = {}
for key in ("rule1", "rule2", "rule3", "rule4", "rule5", "rule5_g1", "rule5_g2"):
    sm = P.image(f"Screen {key}", os.path.join(TEX, key + ".png"), strength=1.6, rough=0.3)
    sp_ = P.plane((0, 0, 0.0005), (0.068, 0.142), sm, (0, 0, 0), f"Phone screen {key}")
    sp_.parent = phone
    screens[key] = sp_
grip = P.empty("Phone grip", (0.045, -0.165, -0.02))
grip.parent = phone
for o in [pbody] + list(screens.values()):
    H.put(o, PRC)
phone.rotation_mode = "XYZ"
for f in range(1, N + 1):
    t = (f - 1) / FPS
    u = phone_up(t)
    sway = Vector((0.004 * math.sin(t * 1.7), 0.003 * math.sin(t * 2.3), 0))
    phone.location = Vector((0.0, -0.035, -0.235)).lerp(Vector((0.09, -0.32, -0.3)), 1 - u) + sway
    phone.rotation_euler = (math.radians(-8 + 50 * (1 - u)), math.radians(-6), math.radians(4 + 10 * (1 - u)))
    phone.keyframe_insert("location", frame=f)
    phone.keyframe_insert("rotation_euler", frame=f)
    cur = None
    for a, b, key in UPS:
        if a - 0.6 <= t <= b + 0.6:
            cur = key
            if key == "rule5" and t > 70.6:
                cyc = int(t * 24) % 9
                cur = "rule5_g1" if cyc in (0, 1) else ("rule5_g2" if cyc == 5 else "rule5")
    for key, o in screens.items():
        o.hide_render = key != cur
        o.keyframe_insert("hide_render", frame=f)
    pbody.hide_render = u < 0.01
    pbody.keyframe_insert("hide_render", frame=f)
for a, b, _ in UPS:
    me.reach("r", fr(a - 0.3), fr(a), grip, fr(b + 0.1))
# sandwich in my right hand at the start; my left hand grabs Arian's arm
me.reach("r", 1, 2, sandwich, fr(3.1))
arm_grab = P.empty("Arian arm grab")
c = arm_grab.constraints.new("CHILD_OF")
c.target = arian.rig
c.subtarget = "lowerarm_l"
c.inverse_matrix.identity()
me.reach("l", fr(24.5), fr(24.9), arm_grab, fr(27.0))
me.reach("l", fr(40.6), fr(41.0), bed_door.handle, fr(41.9))
# phone torch for the duct
bpy.ops.object.light_add(type="SPOT", location=(0, 0, 0))
torch = bpy.context.object
torch.name = "Phone torch"
torch.parent = me.cam
torch.location = (0.05, -0.12, 0)
torch.data.spot_size = math.radians(70)
torch.data.spot_blend = 0.5
torch.data.shadow_soft_size = 0.05
for t_, e in ((0, 0), (57.55, 0), (57.6, 22), (61.0, 22), (61.05, 0)):
    torch.data.energy = e
    torch.data.keyframe_insert("energy", frame=fr(t_))

# ---------------------------------------------------------------- night lighting
h.switches["hall"].flip(1, False)
for li, e, _ in h.lights["living"]:
    li.data.energy = 0
    li.data.keyframe_insert("energy", frame=1)
for li, e, _ in h.lights["bedroom"]:
    li.data.energy = 45
    li.data.color = (1.0, 0.82, 0.62)
for li, e, _ in h.lights["kitchen"]:
    li.data.energy = 110
    li.data.size = 1.6
H.put(P.area_light((-2.3, 2.4, 0.08), (-2.3, 2.4, 1.0), 0, 0.6, (1.0, 0.85, 0.65), name="Under table bounce"), LC)
ut = bpy.data.objects["Under table bounce"]
for t_, e in ((6.2, 0), (6.3, 10), (30.7, 10), (31.5, 0)):
    ut.data.energy = e
    ut.data.keyframe_insert("energy", frame=fr(t_))
H.put(P.area_light((-1.0, 5.0, 1.9), (-2.4, 5.7, 1.4), 22, 0.8, (1.0, 0.88, 0.75), name="Bedroom fill"), LC)
H.put(P.area_light((-1.4, 2.0, 1.9), (-2.3, 3.0, 1.1), 18, 0.8, (1.0, 0.9, 0.8), name="Kitchen fill"), LC)
lamp = P.area_light((5.1, 4.4, 1.5), (3.2, 3.5, 0.5), 45, 0.5, (1.0, 0.75, 0.5), name="Floor lamp light")
H.put(lamp, LC)
H.put(P.area_light((-0.3, 3.2, 2.55), (0, 3.2, 0), 14, 1.0, (0.55, 0.65, 0.95), name="Hall moonlight"), LC)
H.put(P.area_light((3.0, 2.2, 2.6), (3.0, 3.0, 0), 18, 2.0, (0.55, 0.62, 0.9), name="Living ambient"), LC)
for t_, e in ((0, 0), (61.0, 0), (61.05, 40), (75.5, 40)):
    lap_light.data.energy = e
    lap_light.data.keyframe_insert("energy", frame=fr(t_))
# police lights outside the living-room windows (red / blue)
pol = [P.area_light((2.8, -0.3, 1.5), (3.2, 3.5, 1.0), 0, 0.7, (1.0, 0.08, 0.06), name="Police red"),
       P.area_light((6.0, 2.9, 1.5), (2.5, 2.8, 1.0), 0, 0.7, (0.1, 0.25, 1.0), name="Police blue"),
       P.area_light((3.6, -0.3, 1.4), (3.2, 3.5, 1.0), 0, 0.7, (0.1, 0.25, 1.0), name="Police blue 2"),
       P.area_light((6.0, 2.1, 1.4), (2.5, 2.8, 1.0), 0, 0.7, (1.0, 0.08, 0.06), name="Police red 2")]
for li in pol:
    H.put(li, LC)
    li.data.keyframe_insert("energy", frame=1)
    li.data.keyframe_insert("energy", frame=fr(67.0) - 1)
f = fr(67.0)
k = 0
while f < N + 2:
    for j, li in enumerate(pol):
        on = (k + j) % 2 == 0
        li.data.energy = 700 if on else 0
        li.data.keyframe_insert("energy", frame=f)
    k += 1
    f += 5

# ---------------------------------------------------------------- render settings
sc.render.engine = "CYCLES"
sc.cycles.samples = int(os.environ.get("SAMPLES", "10"))
sc.cycles.use_denoising = True
sc.cycles.max_bounces = 3
sc.cycles.diffuse_bounces = 2
sc.cycles.glossy_bounces = 1
sc.cycles.transmission_bounces = 2
sc.cycles.caustics_reflective = sc.cycles.caustics_refractive = False
sc.cycles.adaptive_threshold = 0.05
sc.cycles.use_light_tree = True
sc.render.resolution_x, sc.render.resolution_y = 540, 960
sc.render.fps = FPS
sc.frame_start, sc.frame_end = 1, N
sc.render.use_persistent_data = True
sc.view_settings.view_transform = "AgX"
sc.view_settings.look = "AgX - Medium Low Contrast"
sc.view_settings.exposure = float(os.environ.get("EXPOSURE", "0.4"))
sc.world.color = (0.02, 0.025, 0.04)
if os.environ.get("OUTLINES", "hull") == "freestyle":
    P.enable_outlines(sc, 1.1)
else:
    for ch in (me, arian, nina, i1, i2):
        C.hull_outlines(ch)
args = sys.argv
if "--still" in args:
    os.makedirs(os.path.join(HERE, "test"), exist_ok=True)
    for f in [int(v) for v in args[args.index("--still") + 1].split(",")]:
        sc.frame_set(f)
        sc.render.filepath = os.path.join(HERE, "test", f"r_{f:04d}.png")
        bpy.ops.render.render(write_still=True)
if "--save" in args:
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(HERE, "film_rules.blend"))
if "--render" in args:
    i = args.index("--render")
    if i + 1 < len(args) and "-" in args[i + 1]:
        a, b = args[i + 1].split("-")
        sc.frame_start, sc.frame_end = int(a), int(b)
    os.makedirs(os.path.join(HERE, "frames", "rules"), exist_ok=True)
    sc.render.filepath = os.path.join(HERE, "frames", "rules", "f_")
    sc.render.use_overwrite = False
    sc.render.use_placeholder = True
    bpy.ops.render.render(animation=True)
