"""«زنگ آخر ۲ — آستین»: a gym hall turned into a temporary shelter at night. The soldier who saved the kids hides a
bite under his sleeve. Comic look (EEVEE cel shading + ink outlines) on the cast, bodies driven by Mixamo clips.

    ../cast/bpy.sh scene.py --still 40,120,...      -> test/s_XXXX.png
    ../cast/bpy.sh scene.py --save                  -> sleeve.blend (render.py renders from it)
Shots (seconds) — short shots, clips played a bit faster than real time (the user found «دیوار» slow):
  A  0.0- 4.5 wide: kids on camp beds, soldier at the back      B  4.5- 8.0 soldier fiddles with his sleeve
  C  8.0-12.5 Kazemi on the radio (static)                      D 12.5-15.6 Kian: "will the mums come?"
  E 15.6-19.5 soldier answers without looking                   F 19.5-24.0 Mahsa searches the floor
  G 24.0-27.0 low: blood drops, Mahsa whispers                  H 27.0-30.5 close: the stain on the sleeve
  I 30.5-34.5 Arian's joke, nobody laughs                       J 34.5-39.0 Kazemi walks up to the soldier
  K 39.0-41.2 soldier pauses; K2 41.2-44.0 close: the bite      L 44.0-46.0 the kids step back
  M 46.0-54.5 "wait, listen... the key"; he tosses it           N 54.5-57.0 I pick the key up
  O 57.0-62.0 he goes into the storeroom himself                P 62.0-67.5 the door, the window, the growl
  Q 67.5-72.5 the hall doors: mum calls from behind them, fists  R 72.5-74.5 Kazemi frozen by the radio
  S 74.5-76.5 Kian looks at me
"""
import bpy, sys, os, math, random
from mathutils import Vector, Matrix
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "studio"))
sys.path.insert(0, os.path.join(HERE, "..", "cast"))
sys.path.insert(0, HERE)              # first: our captions.py, not studio/captions.py
bpy.ops.wm.read_factory_settings(use_empty=True)
import cast, mocap, anim  # noqa: E402
import props as P         # noqa: E402
import toon_look as T     # noqa: E402
import arm as ARM         # noqa: E402
from captions import LINES, END, speaking  # noqa: E402

cast.STYLE = cast.CARTOON
FPS = 24
N = int(END * FPS)
sc = bpy.context.scene
sc.render.fps = FPS
sc.frame_start, sc.frame_end = 1, N
MOC = os.path.join(HERE, "..", "mocap")
SPEED = 1.2            # default playback speed of the mocap clips


def fr(t):
    return int(round(t * FPS)) + 1


def seg(t, a, b):
    if t <= a:
        return 0.0
    if t >= b:
        return 1.0
    u = (t - a) / (b - a)
    return u * u * (3 - 2 * u)


def fcurves_of(owner):
    ad = owner.animation_data
    if not ad or not ad.action:
        return []
    act_ = ad.action
    if hasattr(act_, "fcurves") and len(act_.fcurves):
        return list(act_.fcurves)
    out = []
    for layer in getattr(act_, "layers", []):
        for strip in layer.strips:
            for cb in getattr(strip, "channelbags", []):
                out += list(cb.fcurves)
    return out


def key_vis(o, pts):
    """pts: [(seconds, visible)] constant keys on hide_render."""
    for t, v in pts:
        o.hide_render = not v
        o.keyframe_insert("hide_render", frame=max(1, fr(t)) if t > 0 else 1)
    for fc in fcurves_of(o):
        if fc.data_path == "hide_render":
            for k in fc.keyframe_points:
                k.interpolation = "CONSTANT"


def show(objs, spans):
    for o in objs:
        pts = [(0, False)]
        for a, b in spans:
            pts += [(a, True), (b, False)]
        key_vis(o, pts)


def mats():
    return dict(
        floor=P.mat("Gym floor", (0.78, 0.55, 0.32), 0.6), line=P.mat("Court line", (0.95, 0.95, 0.9), 0.6),
        wall_lo=P.mat("Wall low", (0.42, 0.56, 0.5), 0.8), wall_hi=P.mat("Wall high", (0.86, 0.84, 0.76), 0.9),
        ceil=P.mat("Ceiling", (0.62, 0.62, 0.6), 0.9), beam=P.mat("Beam", (0.45, 0.45, 0.47), 0.6, metal=0.5),
        night=P.mat("Night glass", (0.08, 0.12, 0.25), 0.1, emit=(0.08, 0.12, 0.3), strength=0.6),
        tube=P.mat("Light tube", (1, 1, 1), 0.3, emit=(0.95, 0.98, 1.0), strength=6.0),
        door=P.mat("Metal door", (0.32, 0.42, 0.55), 0.4, metal=0.4), bar=P.mat("Push bar", (0.75, 0.76, 0.78), 0.3, metal=0.8),
        sdoor=P.mat("Store door", (0.55, 0.56, 0.5), 0.5, metal=0.3), frame=P.mat("Door frame", (0.25, 0.25, 0.27), 0.5),
        canvas=P.mat("Cot canvas", (0.36, 0.42, 0.24), 0.9), steel=P.mat("Cot steel", (0.5, 0.5, 0.52), 0.4, metal=0.7),
        blanket=P.mat("Blanket", (0.55, 0.2, 0.18), 0.9), table=P.mat("Folding table", (0.85, 0.85, 0.82), 0.5),
        radio=P.mat("Radio", (0.18, 0.2, 0.16), 0.5), led=P.mat("Radio LED", (0.2, 1.0, 0.3), 0.3, emit=(0.2, 1.0, 0.3), strength=8),
        mat=P.mat("Gym mat", (0.2, 0.32, 0.6), 0.8), vault=P.mat("Vault box", (0.6, 0.42, 0.25), 0.7),
        store=P.mat("Store wall", (0.3, 0.3, 0.32), 0.9), shelf=P.mat("Shelf", (0.4, 0.38, 0.34), 0.7),
        crate=P.mat("Crate", (0.45, 0.4, 0.22), 0.8), blood=P.mat("Blood drop", (0.38, 0.02, 0.03), 0.3),
        key=P.mat("Key", (0.8, 0.72, 0.35), 0.3, metal=0.9), wire=P.mat("Window wire", (0.1, 0.1, 0.1), 0.5),
        bag=P.mat("Bag", (0.3, 0.32, 0.22), 0.8), dark=P.mat("Dark", (0.03, 0.03, 0.04), 0.9),
    )


M_ = mats()
SET = []


def box(loc, size, m, name="Set", rot=(0, 0, 0)):
    o = P.box(loc, size, M_[m] if isinstance(m, str) else m, name)
    o.rotation_euler = rot
    SET.append(o)
    return o


# ------------------------------------------------------------------ set: gym hall X 0..14, Y 0..9, H 4.6
W, D, H = 14.0, 9.0, 4.6
WT = 0.2
box((W / 2, D / 2, -0.05), (W, D, 0.1), "floor", "Floor")
box((W / 2, D / 2, H + 0.05), (W, D, 0.1), "ceil", "Ceiling")
for x in (2.0, 5.5, 9.0, 12.5):                       # roof beams
    box((x, D / 2, H - 0.15), (0.2, D, 0.3), "beam", "Beam")
# court lines (plain, no markings)
for (x, y, sx, sy) in ((W / 2, 0.8, W - 1.6, 0.06), (W / 2, D - 0.8, W - 1.6, 0.06), (0.8, D / 2, 0.06, D - 1.6),
                       (W - 0.8, D / 2, 0.06, D - 1.6), (W / 2, D / 2, 0.06, D - 1.6)):
    box((x, y, 0.003), (sx, sy, 0.006), "line", "Court line")
bpy.ops.mesh.primitive_torus_add(location=(W / 2, D / 2, 0.003), major_radius=1.6, minor_radius=0.03)
ring = bpy.context.object
ring.scale = (1, 1, 0.1)
ring.data.materials.append(M_["line"])
ring.name = "Court circle"
SET.append(ring)


def wall_x(x, y0, y1, holes=(), name="Wall"):
    """Wall across Y at x from y0 to y1; holes: [(ya, yb, za, zb)]. Two-tone (low green, high cream)."""
    cuts = sorted(holes)
    spans, y = [], y0
    for ya, yb, za, zb in cuts:
        spans.append((y, ya, 0, H))
        spans.append((ya, yb, zb, H))
        if za > 0:
            spans.append((ya, yb, 0, za))
        y = yb
    spans.append((y, y1, 0, H))
    for a, b, za, zb in spans:
        if b - a < 1e-3:
            continue
        lo_top = min(zb, 1.6)
        if lo_top > za:
            box((x, (a + b) / 2, (za + lo_top) / 2), (WT, b - a, lo_top - za), "wall_lo", name)
        hi_bot = max(za, 1.6)
        if zb > hi_bot:
            box((x, (a + b) / 2, (hi_bot + zb) / 2), (WT, b - a, zb - hi_bot), "wall_hi", name)


def wall_y(y, x0, x1, holes=(), name="Wall"):
    cuts = sorted(holes)
    spans, x = [], x0
    for xa, xb, za, zb in cuts:
        spans.append((x, xa, 0, H))
        spans.append((xa, xb, zb, H))
        if za > 0:
            spans.append((xa, xb, 0, za))
        x = xb
    spans.append((x, x1, 0, H))
    for a, b, za, zb in spans:
        if b - a < 1e-3:
            continue
        lo_top = min(zb, 1.6)
        if lo_top > za:
            box(((a + b) / 2, y, (za + lo_top) / 2), (b - a, WT, lo_top - za), "wall_lo", name)
        hi_bot = max(za, 1.6)
        if zb > hi_bot:
            box(((a + b) / 2, y, (hi_bot + zb) / 2), (b - a, WT, zb - hi_bot), "wall_hi", name)


# back wall (y = D): high night windows + the storeroom door at x 10.85..11.75
STORE_X0, STORE_X1 = 10.85, 11.75
wins = [(1.0 + 2.3 * i, 2.6 + 2.3 * i, 3.0, 4.0) for i in range(4)] + [(12.2, 13.6, 3.0, 4.0)]
wall_y(D + WT / 2, -WT, W + WT, holes=wins + [(STORE_X0, STORE_X1, 0, 2.1)], name="Back wall")
for xa, xb, za, zb in wins:
    box(((xa + xb) / 2, D + 0.1, (za + zb) / 2), (xb - xa, 0.02, zb - za), "night", "Night window")
    box(((xa + xb) / 2, D + 0.05, (za + zb) / 2), (0.04, 0.06, zb - za), "frame", "Window bar")
wall_y(-WT / 2, -WT, W + WT, holes=[(1.0 + 2.3 * i, 2.6 + 2.3 * i, 3.0, 4.0) for i in range(6)], name="Front wall")
for i in range(6):
    xa, xb = 1.0 + 2.3 * i, 2.6 + 2.3 * i
    box(((xa + xb) / 2, -0.1, 3.5), (xb - xa, 0.02, 1.0), "night", "Night window")
# left wall (x = 0): the hall's double doors at y 4.0..5.8
HALL_Y0, HALL_Y1 = 4.0, 5.8
wall_x(-WT / 2, 0, D, holes=[(HALL_Y0, HALL_Y1, 0, 2.3)], name="Left wall")
box((-0.4, (HALL_Y0 + HALL_Y1) / 2, 1.15), (0.1, HALL_Y1 - HALL_Y0 + 0.2, 2.4), "dark", "Behind hall doors")
wall_x(W + WT / 2, 0, D, name="Right wall")
HALL_LEAVES = []
for k, (hy, sgn) in enumerate(((HALL_Y0, 1), (HALL_Y1, -1))):
    hinge = P.empty(f"Hall hinge {k}", (0.02, hy, 0))
    leaf = P.box((0.02, hy + sgn * 0.45, 1.13), (0.05, 0.88, 2.24), M_["door"], f"Hall door {k}")
    bar = P.box((0.07, hy + sgn * 0.45, 1.0), (0.05, 0.7, 0.06), M_["bar"], f"Hall bar {k}")
    win = P.box((0.0, hy + sgn * 0.45, 1.7), (0.07, 0.25, 0.4), M_["dark"], f"Hall door window {k}")
    for o in (leaf, bar, win):
        o.parent = hinge
        o.matrix_parent_inverse = hinge.matrix_world.inverted()
        SET.append(o)
    HALL_LEAVES.append((hinge, sgn))
for s in (HALL_Y0 - 0.05, HALL_Y1 + 0.05):
    box((0.0, s, 1.15), (0.24, 0.1, 2.3), "frame", "Hall door frame")
box((0.0, (HALL_Y0 + HALL_Y1) / 2, 2.35), (0.24, HALL_Y1 - HALL_Y0 + 0.2, 0.1), "frame", "Hall door frame")
# a chain through the push bars (they barricaded the hall)
for j in range(9):
    l = P.sphere((0.12, (HALL_Y0 + HALL_Y1) / 2 - 0.4 + j * 0.1, 1.0), 0.025, M_["bar"], "Chain", scale=(1, 1.6, 0.7))
    SET.append(l)
# storeroom behind the back wall
box(((STORE_X0 + STORE_X1) / 2, D + 2.2, 1.5), (2.6, 0.15, 3.0), "store", "Store back")
box((STORE_X0 - 0.85, D + 1.15, 1.5), (0.15, 2.1, 3.0), "store", "Store side")
box((STORE_X1 + 0.85, D + 1.15, 1.5), (0.15, 2.1, 3.0), "store", "Store side")
box(((STORE_X0 + STORE_X1) / 2, D + 1.15, 3.05), (2.6, 2.2, 0.1), "store", "Store ceiling")
box((STORE_X1 + 0.6, D + 1.6, 0.9), (0.4, 1.0, 1.8), "shelf", "Store shelf")
box((STORE_X0 - 0.55, D + 1.8, 0.3), (0.5, 0.5, 0.6), "crate", "Store crate")
store_lamp = P.area_light(((STORE_X0 + STORE_X1) / 2, D + 1.2, 2.9), ((STORE_X0 + STORE_X1) / 2, D + 1.2, 0), 18, 0.6,
                          (1.0, 0.45, 0.35), name="Store lamp")
for s in (STORE_X0 - 0.05, STORE_X1 + 0.05):
    box((s, D, 1.07), (0.1, 0.26, 2.14), "frame", "Store frame")
box(((STORE_X0 + STORE_X1) / 2, D, 2.15), (STORE_X1 - STORE_X0 + 0.2, 0.26, 0.1), "frame", "Store frame")
# storeroom door: hinge at STORE_X0, leaf with a small wired window (a real opening you see through)
s_hinge = P.empty("Store hinge", (STORE_X0, D - 0.06, 0))
lw = STORE_X1 - STORE_X0 - 0.02
wx0, wx1, wz0, wz1 = 0.28, 0.62, 1.32, 1.74          # window in leaf coords (x from hinge)
parts = [((lw / 2, 1.05), (lw, 0.04, 2.1 - 0.0))]
leaf_objs = []
for (cx, cz), sz in (((wx0 / 2, 1.05), (wx0, 0.05, 2.1)), (((wx1 + lw) / 2, 1.05), (lw - wx1, 0.05, 2.1)),
                     (((wx0 + wx1) / 2, wz0 / 2), (wx1 - wx0, 0.05, wz0)),
                     (((wx0 + wx1) / 2, (wz1 + 2.1) / 2), (wx1 - wx0, 0.05, 2.1 - wz1))):
    leaf_objs.append(P.box((STORE_X0 + cx, D - 0.06, cz), sz, M_["sdoor"], "Store door"))
for k in range(3):                                    # wire grid in the window
    leaf_objs.append(P.box((STORE_X0 + wx0 + (k + 1) * (wx1 - wx0) / 4, D - 0.06, (wz0 + wz1) / 2), (0.008, 0.01, wz1 - wz0),
                           M_["wire"], "Window wire"))
    leaf_objs.append(P.box((STORE_X0 + (wx0 + wx1) / 2, D - 0.06, wz0 + (k + 1) * (wz1 - wz0) / 4), (wx1 - wx0, 0.01, 0.008),
                           M_["wire"], "Window wire"))
leaf_objs.append(P.sphere((STORE_X0 + lw - 0.1, D - 0.11, 1.0), 0.03, M_["bar"], "Store knob"))
for o in leaf_objs:
    o.parent = s_hinge
    o.matrix_parent_inverse = s_hinge.matrix_world.inverted()
    SET.append(o)
# door opens towards the hall (-Y), he goes through, it shuts
for t, a in ((0, 0), (59.0, 0), (59.9, -85), (61.2, -85), (61.9, 0), (END, 0)):
    s_hinge.rotation_euler = (0, 0, math.radians(a))
    s_hinge.keyframe_insert("rotation_euler", index=2, frame=fr(t))
# hall doors: banged on from outside from "باز کنید!" (70.6) to the end
rr = random.Random(3)
for hinge, sgn in HALL_LEAVES:
    pts = [(0, 0), (70.6, 0)]
    t = 70.6
    while t < END:
        t += rr.uniform(0.18, 0.34)
        pts += [(t, sgn * rr.uniform(2.5, 5.0)), (t + 0.08, 0)]
    for t, a in pts:
        hinge.rotation_euler = (0, 0, math.radians(a))
        hinge.keyframe_insert("rotation_euler", index=2, frame=fr(t))

# camp beds: long along X, kids sit on the front edge facing -Y
COTS = {"arian": 3.0, "me": 5.2, "kian": 7.4, "mahsa": 9.6}
COT_Y = 3.6
for who, cx in COTS.items():
    box((cx, COT_Y, 0.52), (1.9, 0.72, 0.08), "canvas", "Cot")
    for dx in (-0.85, 0.85):
        for dy in (-0.3, 0.3):
            box((cx + dx, COT_Y + dy, 0.25), (0.04, 0.04, 0.5), "steel", "Cot leg")
    box((cx + 0.55, COT_Y + 0.05, 0.6), (0.7, 0.6, 0.06), "blanket", "Folded blanket")
box((12.6, 3.3, 0.52), (1.9, 0.72, 0.08), "canvas", "Cot")                 # the soldier's cot (empty)
for dx in (-0.85, 0.85):
    for dy in (-0.3, 0.3):
        box((12.6 + dx, 3.3 + dy, 0.25), (0.04, 0.04, 0.5), "steel", "Cot leg")
box((13.2, 3.5, 0.68), (0.5, 0.35, 0.25), "bag", "Kit bag")
# folding table with the radio (base unit) by the back wall
TABLE = (8.6, 8.35)
box((TABLE[0], TABLE[1], 0.74), (1.6, 0.7, 0.04), "table", "Table")
for dx in (-0.72, 0.72):
    box((TABLE[0] + dx, TABLE[1], 0.37), (0.04, 0.6, 0.74), "steel", "Table leg")
box((TABLE[0] - 0.2, TABLE[1] + 0.05, 0.86), (0.42, 0.26, 0.2), "radio", "Radio")
SET.append(P.cyl((TABLE[0] - 0.36, TABLE[1] + 0.12, 0.96), (TABLE[0] - 0.36, TABLE[1] + 0.12, 1.45), 0.008, M_["radio"], "Antenna"))
led = P.sphere((TABLE[0] - 0.05, TABLE[1] - 0.085, 0.92), 0.015, M_["led"], "Radio LED")
SET.append(led)
box((TABLE[0] + 0.45, TABLE[1], 0.8), (0.35, 0.25, 0.08), "crate", "Ration box")
# stacked gym mats and a vaulting box along the right wall
for k in range(4):
    box((13.3, 6.5, 0.08 + k * 0.15), (1.0, 2.0, 0.14), "mat", "Gym mat")
box((13.2, 1.4, 0.45), (1.2, 0.5, 0.9), "vault", "Vault box")
# blood drops near where the soldier stands
DROPS = []
r = random.Random(11)
for k in range(7):
    p = (11.2 + r.uniform(-0.35, 0.3), 5.75 + r.uniform(-0.25, 0.3), 0.004)
    o = P.sphere(p, 0.03, M_["blood"], "Blood drop", scale=(r.uniform(0.6, 1.3), r.uniform(0.6, 1.3), 0.06))
    SET.append(o)
    DROPS.append(o)
show(DROPS, [(4.0, END)])

# ------------------------------------------------------------------ lights
w = bpy.data.worlds.new("W")
sc.world = w
w.color = (0.05, 0.06, 0.09)
sun = bpy.data.objects.new("Moon", bpy.data.lights.new("Moon", "SUN"))
sc.collection.objects.link(sun)
sun.data.energy = 1.4
sun.data.color = (0.75, 0.82, 1.0)
sun.data.use_shadow = False
sun.rotation_euler = (math.radians(55), 0, math.radians(-30))
LAMPS = []
for k, (x, y) in enumerate(((3.5, 3.0), (7.5, 3.0), (11.0, 3.2), (4.0, 6.8), (9.0, 6.8))):
    l = P.area_light((x, y, H - 0.4), (x, y, 0), 220, 1.6, (0.92, 0.97, 1.0), size_y=0.25, name=f"Tube light {k}")
    tube = P.box((x, y, H - 0.33), (1.6, 0.12, 0.06), M_["tube"], f"Tube {k}")
    SET.append(tube)
    LAMPS.append((l, tube))


def flicker(lamp_idx, t0, t1, seed):
    l, tube = LAMPS[lamp_idx]
    rr_ = random.Random(seed)
    pts = [(0, 1.0), (t0, 1.0)]
    t = t0
    while t < t1:
        t += rr_.uniform(0.06, 0.4)
        pts.append((t, rr_.choice([0.0, 0.15, 1.0, 0.4])))
    pts += [(t1, 1.0)]
    base = l.data.energy
    for t, v in pts:
        l.data.energy = base * v
        l.data.keyframe_insert("energy", frame=fr(t))
        tube.hide_render = v < 0.3
        tube.keyframe_insert("hide_render", frame=fr(t))
    for fc in fcurves_of(l.data) + fcurves_of(tube):
        for k in fc.keyframe_points:
            k.interpolation = "CONSTANT"


flicker(2, 62.0, 67.4, 5)
flicker(4, 63.0, 67.0, 9)
flicker(2, 72.5, END, 6) if False else None
# radio LED: dark, blinking on the static 8-12.5 (nobody answers on the radio)
led_pts = [(0, 0.0), (8.2, 1), (8.5, 0), (9.1, 1), (9.3, 0), (10.2, 1), (10.5, 0), (11.4, 1), (11.6, 0), (END, 0)]
for t, v in led_pts:
    led.hide_render = v < 0.5
    led.keyframe_insert("hide_render", frame=fr(t))
for fc in fcurves_of(led):
    for k in fc.keyframe_points:
        k.interpolation = "CONSTANT"

# ------------------------------------------------------------------ cast
KEYS = ["me", "arian", "mahsa", "kian", "kazemi", "soldier"]
CH = {}
for k in KEYS:
    ch = cast.spawn(k)
    T.register(ch, k, realistic=True)
    CH[k] = ch
# the same soldier later, behind the storeroom window: turned
CH["soldierZ"] = cast.spawn("soldier", zombie=0.85, name="SoldierZ", seed=4)
T.register(CH["soldierZ"], "soldier", realistic=True)
skin_z, clothes_z = T.SKIN[CH["soldierZ"].name]
T.SKIN[CH["soldierZ"].name] = ((0.5, 0.56, 0.46), clothes_z)
A = ARM.build(CH["soldier"], FPS)          # sleeve, stain, bite (rig still in rest pose)
A.stain([(0, 0.35), (8, 0.55), (27, 0.85), (30, 1.05)])
REVEAL_T = 41.2
A.reveal(REVEAL_T)
A.veins_grow([(REVEAL_T, 0.7), (44.0, 1.0), (54.0, 1.4)])
M_ = mats()                                # cast building purges unused materials: re-create for later props
CLIP = {}


def clip(name):
    if name not in CLIP:
        CLIP[name] = mocap.load(os.path.join(MOC, name + ".fbx"))
    return CLIP[name]


def act(who, name, t0, t1, pos, facing, speed=SPEED, **kw):
    """Character `who` plays clip `name` from t0 to t1 (seconds) at pos/facing."""
    n = fr(t1) - fr(t0)
    mocap.apply(CH[who], clip(name), start=fr(t0), length=n, offset=pos, facing=facing, speed=speed, **kw)
    rig = CH[who].rig
    if "place" in kw:
        return
    rig.location = pos
    rig.rotation_euler = (0, 0, math.radians(facing) + math.pi)
    rig.keyframe_insert("location", frame=fr(t1) - 1)
    rig.keyframe_insert("rotation_euler", index=2, frame=fr(t1) - 1)


NAT = {}


def natural_speed(who, clipname):
    """metres per second the clip's feet really travel, on this character (for foot-locked walking)."""
    key = (who, clipname)
    if key in NAT:
        return NAT[key]
    c = clip(clipname)
    a = c.arm
    Mw = a.matrix_world
    b = {s: a.pose.bones[mocap._src_name(a, s)] for s in ("Hips", "LeftFoot", "RightFoot", "LeftUpLeg")}
    rest = {s: Mw @ pb.bone.matrix_local for s, pb in b.items()}
    src_leg = (rest["LeftUpLeg"].translation - rest["LeftFoot"].translation).length
    tr = CH[who].rig.data.bones
    tgt_leg = (tr["thigh_l"].matrix_local.translation - tr["foot_l"].matrix_local.translation).length
    hips, feet = [], []
    f = int(c.first)
    while f <= c.last:
        sc.frame_set(f)
        hips.append((Mw @ b["Hips"].head).copy())
        feet.append(((Mw @ b["LeftFoot"].head).copy(), (Mw @ b["RightFoot"].head).copy()))
        f += 1
    root = (hips[-1] - hips[0])
    root.z = 0
    sp = []
    for i in range(1, len(hips)):
        low = min(feet[i][0].z, feet[i][1].z)
        for s_ in (0, 1):
            if feet[i][s_].z < low + 0.02:
                v = (feet[i][s_] - hips[i]) - (feet[i - 1][s_] - hips[i - 1])
                v.z = 0
                sp.append(v.length * c.fps)
    sp.sort()
    v = sp[len(sp) // 2] if sp else 1.0
    if root.length > 0.5:                      # clip with real root motion: use it
        v = root.length / c.seconds
    NAT[key] = v * tgt_leg / max(1e-6, src_leg)
    print("NATURAL SPEED", who, clipname, round(NAT[key], 3))
    return NAT[key]


def pos_at(who, t):
    """where `who` stands (pelvis on the floor) at time t, from the motion keyed so far."""
    sc.frame_set(fr(t))
    rig = CH[who].rig
    p = rig.matrix_world @ rig.pose.bones["pelvis"].head
    return (p.x, p.y)


def facing_at(who, t):
    sc.frame_set(fr(t))
    return math.degrees(CH[who].rig.rotation_euler.z - math.pi)


def walk(who, t0, t1, pts, clipname="walking", back=False, end_face=None, turn=0.35):
    """`who` walks along the polyline pts (first point None = from where he stands) from t0 to t1.
    Feet keep their real stride: the clip speed follows the path speed. back=True: steps backwards,
    facing against the direction of travel. Turns smoothly into the path and (end_face) at the end."""
    pts = list(pts)
    if pts[0] is None:
        pts[0] = pos_at(who, t0 - 1.0 / FPS)
    P_ = [Vector((p[0], p[1], 0.0)) for p in pts]
    d0 = P_[1] - P_[0]
    f_prev = math.degrees(math.atan2(-d0.x, d0.y)) + (180 if back else 0)
    if t0 > 0.05:
        f_prev = facing_at(who, t0 - 1.0 / FPS)
    L = [0.0]
    for a, b in zip(P_, P_[1:]):
        L.append(L[-1] + (b - a).length)
    total = max(1e-4, L[-1])
    n = fr(t1) - fr(t0)
    dur = n / FPS
    ease = min(0.25, dur * 0.2)                    # accelerate / slow down over `ease` seconds
    vmax = total / (dur - ease)

    def dist(tt):                                  # distance along the path at tt seconds into the walk
        if tt < ease:
            return 0.5 * vmax * tt * tt / ease
        if tt > dur - ease:
            r = dur - tt
            return total - 0.5 * vmax * r * r / ease
        return vmax * (tt - ease / 2)

    def at(d):
        d = max(0.0, min(total, d))
        for i in range(len(P_) - 1):
            if d <= L[i + 1] or i == len(P_) - 2:
                u = (d - L[i]) / max(1e-6, L[i + 1] - L[i])
                return P_[i].lerp(P_[i + 1], max(0.0, min(1.0, u)))

    def angdiff(a, b):
        return (b - a + 180) % 360 - 180

    def place(j):
        tt = j / FPS
        d = dist(tt)
        p = at(d)
        q = at(min(total, d + 0.35)) - at(max(0.0, d - 0.05))
        if q.length < 1e-4:
            q = P_[-1] - P_[-2]
        fac = math.degrees(math.atan2(-q.x, q.y)) + (180 if back else 0)
        if tt < turn:
            fac = f_prev + angdiff(f_prev, fac) * seg(tt, 0, turn)
        if end_face is not None and tt > dur - turn:
            fac = fac + angdiff(fac, end_face) * seg(tt, dur - turn, dur)
        return tuple(p), fac

    sp = vmax / natural_speed(who, clipname)
    sp = max(0.5, min(2.2, sp))
    mocap.apply(CH[who], clip(clipname), start=fr(t0), length=n, offset=tuple(P_[0]), facing=f_prev,
                speed=-sp if back else sp, in_place=True, loop=True, place=place)
    return tuple(P_[-1])


def pace(who, name, t0, t1, pieces, start, facing, speed=1.0, center=True):
    """Root-motion clip played as a chain of short pieces [(src_a, src_b), ...] (repeated until t1), each one
    picking up exactly where the last one stopped, so he really walks to and fro without leaving the area.
    center: the whole walk is shifted so that its average position is `start`."""
    _pace(who, name, t0, t1, pieces, start, facing, speed)
    if center:
        ps = [Vector(pos_at(who, t0 + (t1 - t0) * k / 20) + (0.0,)) for k in range(20)]
        mid = sum(ps, Vector()) / len(ps)
        st = Vector((start[0], start[1], 0.0)) + (Vector((start[0], start[1], 0.0)) - mid)
        _pace(who, name, t0, t1, pieces, tuple(st), facing, speed)


def _pace(who, name, t0, t1, pieces, start, facing, speed):
    t, i = t0, 0
    want = Vector((start[0], start[1], 0.0))
    while t < t1 - 0.05:
        a, b = pieces[i % len(pieces)]
        te = min(t1, t + (b - a) / speed)
        off = Vector(want)
        for _ in range(2):                         # place the piece so that its first frame lands on `want`
            act(who, name, t, te, tuple(off), facing, speed=speed, src_from=a)
            got = Vector(pos_at(who, t) + (0.0,))
            off += want - got
        act(who, name, t, te, tuple(off), facing, speed=speed, src_from=a)
        want = Vector(pos_at(who, te - 1.0 / FPS) + (0.0,))
        t, i = te, i + 1


def face(a, b):
    """facing (deg) from point a towards point b (0 = +Y, 90 = -X)."""
    return math.degrees(math.atan2(-(b[0] - a[0]), b[1] - a[1]))


SOLDIER = (11.6, 6.4)
SIT = {k: (x - 0.25, COT_Y - 0.3, 0.0) for k, x in COTS.items()}
# ---- the four kids sitting 0-30.5 (Mahsa gets up at 19.5)
for k, off in (("arian", 0.0), ("me", 1.3), ("kian", 2.6)):
    act(k, "sitting_idle", 0.0, 30.5, SIT[k], 180, loop=True, src_from=off, speed=1.0)
act("mahsa", "sitting_idle", 0.0, 19.5, SIT["mahsa"], 180, loop=True, src_from=3.1, speed=1.0)
# Mahsa searches the floor by the drops 19.5-30.5 (squats, searches, stands)
MAHSA_SEARCH = (10.65, 5.3, 0)
walk("mahsa", 19.5, 20.7, [(9.95, 4.15), MAHSA_SEARCH[:2]], end_face=face(MAHSA_SEARCH, (11.2, 5.8)))
act("mahsa", "opening_a_filing_cabinet", 20.7, 30.5, MAHSA_SEARCH, face(MAHSA_SEARCH, (11.2, 5.8)), speed=1.25)
# ---- standing 30.5-44
STAND = {"arian": (3.6, 4.1, 0), "me": (7.6, 4.3, 0), "kian": (7.05, 4.05, 0), "mahsa": (9.9, 4.7, 0)}
act("arian", "dismissing_gesture", 30.5, 33.4, STAND["arian"], face(STAND["arian"], (7.3, 4.2)), speed=1.0)
act("arian", "breathing_idle", 33.4, 44.0, STAND["arian"], face(STAND["arian"], SOLDIER), src_from=2.0)
walk("me", 30.5, 31.8, [(6.3, 4.45), STAND["me"][:2]], end_face=face(STAND["me"], SOLDIER))
act("me", "nervously_look_around", 31.8, 44.0, STAND["me"], face(STAND["me"], SOLDIER), loop=True)
act("kian", "breathing_idle", 30.5, 41.2, STAND["kian"], face(STAND["kian"], SOLDIER), src_from=1.0)
act("kian", "terrified", 41.2, 44.0, STAND["kian"], face(STAND["kian"], SOLDIER), src_from=0.0, speed=1.5)
walk("mahsa", 30.5, 31.6, [MAHSA_SEARCH[:2], STAND["mahsa"][:2]], end_face=face(STAND["mahsa"], SOLDIER))
act("mahsa", "nervously_look_around", 31.6, 44.0, STAND["mahsa"], face(STAND["mahsa"], SOLDIER), src_from=2.0, loop=True)
# ---- they step back 44-57
BACK = {"arian": (5.9, 3.9, 0), "me": (7.05, 3.95, 0), "kian": (6.55, 3.75, 0), "mahsa": (8.9, 3.4, 0)}
walk("arian", 44.0, 46.0, [STAND["arian"][:2], BACK["arian"][:2]], end_face=face(BACK["arian"], SOLDIER))
act("arian", "nervously_look_around", 46.0, 57.0, BACK["arian"], face(BACK["arian"], SOLDIER), loop=True, src_from=1.0)
walk("me", 44.0, 44.8, [STAND["me"][:2], BACK["me"][:2]], back=True)
act("me", "terrified", 44.8, 54.5, BACK["me"], face(BACK["me"], SOLDIER), src_from=8.0, speed=1.0)
walk("kian", 44.0, 44.75, [STAND["kian"][:2], BACK["kian"][:2]], back=True)
act("kian", "terrified", 44.75, 57.0, BACK["kian"], face(BACK["kian"], SOLDIER), src_from=3.0, speed=1.0)
walk("mahsa", 44.0, 45.4, [STAND["mahsa"][:2], BACK["mahsa"][:2]], back=True)
act("mahsa", "breathing_idle", 45.4, 57.0, BACK["mahsa"], face(BACK["mahsa"], SOLDIER), loop=True)
KEY_FLOOR = (7.35, 4.3, 0.012)
act("me", "opening_a_filing_cabinet", 54.5, 57.0, (7.15, 4.0, 0), face((7.15, 4.0), KEY_FLOOR), speed=1.6)
# ---- after he's gone 57-END
ME_END = (7.1, 4.0, 0)
KIAN_END = (6.55, 3.8, 0)
act("me", "breathing_idle", 57.0, 72.5, ME_END, face(ME_END, (11.3, 9.0)), loop=True)
act("me", "nervously_look_around", 72.5, 74.5, ME_END, 100, speed=1.4)
act("me", "breathing_idle", 74.5, END, ME_END, face(ME_END, KIAN_END), src_from=3.0)
act("kian", "terrified", 57.0, 72.5, KIAN_END, face(KIAN_END, (11.3, 9.0)), src_from=6.0, speed=1.0)
act("kian", "nervously_look_around", 72.5, 74.5, KIAN_END, 95, speed=1.4)
act("kian", "breathing_idle", 74.5, END, KIAN_END, face(KIAN_END, ME_END), src_from=1.0)
act("arian", "nervously_look_around", 57.0, END, (5.9, 3.9, 0), face((5.9, 3.9), (11.3, 9.0)), loop=True, src_from=3.0)
act("mahsa", "nervously_look_around", 57.0, END, (8.9, 3.4, 0), face((8.9, 3.4), (11.3, 9.0)), loop=True, src_from=0.5)
# ---- Kazemi
KZ_RADIO = (TABLE[0], TABLE[1] - 0.6, 0)
# he comes back from the windows to the radio, then paces up and down beside the table with the handset
walk("kazemi", 0.0, 3.4, [(4.6, 7.2), (6.6, 7.55), KZ_RADIO[:2]], end_face=0)
act("kazemi", "breathing_idle", 3.4, 8.0, KZ_RADIO, 0, speed=1.0)
# pieces of the pacing clip that turn round and come back (out-and-back ~2.5 m along the table)
pace("kazemi", "talking_phone_pacing", 8.0, 34.5, [(3.0, 7.5), (11.0, 15.0)], (KZ_RADIO[0] - 0.3, KZ_RADIO[1] - 0.1), 90)
KZ_MEET = (10.85, 5.75, 0)
walk("kazemi", 34.5, 37.0, [None, (9.6, 6.6), KZ_MEET[:2]], end_face=face(KZ_MEET, SOLDIER))
act("kazemi", "breathing_idle", 37.0, 44.0, KZ_MEET, face(KZ_MEET, SOLDIER), speed=1.0)
KZ_BACK = (10.6, 4.6, 0)
walk("kazemi", 44.0, 45.2, [KZ_MEET[:2], KZ_BACK[:2]], back=True)
act("kazemi", "hands_forward_gesture", 45.2, 47.3, KZ_BACK, face(KZ_BACK, SOLDIER), speed=1.5)
act("kazemi", "breathing_idle", 47.3, 62.0, KZ_BACK, face(KZ_BACK, SOLDIER), loop=True)
walk("kazemi", 62.0, 64.8, [KZ_BACK[:2], (9.7, 6.4), KZ_RADIO[:2]], end_face=215)
# mum's voice comes from behind the hall doors: he only listens, frozen, the handset stays on the table
act("kazemi", "breathing_idle", 64.8, 72.5, KZ_RADIO, 215, loop=True, speed=0.8)
act("kazemi", "nervously_look_around", 72.5, END, pos_at("kazemi", 72.45) + (0,), 120, speed=1.3)
# ---- the soldier
walk("soldier", 0.0, 5.6, [(8.2, 4.7), (10.3, 5.6), SOLDIER], clipname="reloading", end_face=15)
act("soldier", "breathing_idle", 5.6, 15.6, SOLDIER + (0,), 15, loop=True)
act("soldier", "breathing_idle", 15.6, 27.0, SOLDIER + (0,), 20, src_from=2.0, loop=True)
act("soldier", "thinking", 27.0, 34.5, SOLDIER + (0,), 30, loop=True, speed=1.0)
act("soldier", "breathing_idle", 34.5, 39.0, SOLDIER + (0,), face(SOLDIER, KZ_MEET), speed=1.0)
act("soldier", "thinking", 39.0, 44.0, SOLDIER + (0,), face(SOLDIER, KZ_MEET), speed=1.1)
S_TALK = (11.4, 6.1, 0)
act("soldier", "hands_forward_gesture", 44.0, 48.4, S_TALK, face(S_TALK, BACK["me"]), speed=1.0)
act("soldier", "thinking", 48.4, 53.2, S_TALK, face(S_TALK, BACK["me"]), speed=1.0)
act("soldier", "dismissing_gesture", 53.2, 54.5, S_TALK, face(S_TALK, BACK["me"]), speed=1.5)
act("soldier", "breathing_idle", 54.5, 57.0, S_TALK, face(S_TALK, BACK["me"]), speed=1.0)
DOOR_IN = ((STORE_X0 + STORE_X1) / 2, D - 0.75)
walk("soldier", 57.0, 58.8, [S_TALK[:2], DOOR_IN], end_face=0)
act("soldier", "opening_door_inwards", 58.8, 62.0, DOOR_IN + (0,), 0, speed=1.6)
act("soldierZ", "zombie_idle", 61.5, END, ((STORE_X0 + STORE_X1) / 2 + 0.08, D + 0.55, 0), 180, loop=True, speed=1.0)

# who may be on screen (refined per shot after the camera is set: hidden otherwise, faster renders)
PRESENT = {"me": [(0, END)], "arian": [(0, END)], "mahsa": [(0, END)], "kian": [(0, END)], "kazemi": [(0, END)],
           "soldier": [(0, 61.9)], "soldierZ": [(61.5, END)]}
WORRY = {"me": [(0, 0.6), (24, 1.0), (41, 2.0), (57, 1.6), (67.5, 1.2), (72.5, 2.0)],
         "arian": [(0, 0.4), (30.5, 0.0), (33.5, 1.0), (41, 2.0), (57, 1.6), (72.5, 2.0)],
         "mahsa": [(0, 0.5), (19.5, 1.4), (41, 2.0), (57, 1.6), (72.5, 2.0)],
         "kian": [(0, 1.2), (41, 2.0)], "kazemi": [(0, 0.8), (34.5, 1.3), (41, 1.8), (67.5, 1.2), (72.5, 2.0)],
         "soldier": [(0, 0.6), (15, 0.9), (39, 1.4), (46, 1.8)], "soldierZ": [(0, 0.0)]}


def worry(who, t):
    pts = WORRY[who]
    v = pts[0][1]
    for (a, va), (b, vb) in zip(pts, pts[1:] + [(999, pts[-1][1])]):
        if a <= t < b:
            v = va + (vb - va) * seg(t, a, min(b, a + 0.8))
    return v


def present(who, t):
    return any(a <= t < b for a, b in PRESENT[who])


show(A.objs_reveal, [(REVEAL_T, 61.9)])
show(A.objs_stain, [(0, REVEAL_T)])

# ------------------------------------------------------------------ props in hands


def in_hand(obj, who, bone, t_ref):
    rig = CH[who].rig
    sc.frame_set(fr(t_ref))
    hm = rig.matrix_world @ rig.pose.bones[bone].matrix
    con = obj.constraints.new("CHILD_OF")
    con.target, con.subtarget = rig, bone
    con.inverse_matrix = hm.inverted()


def key_mesh(name):
    k = P.box((0, 0, 0), (0.012, 0.055, 0.004), M_["key"], name)
    bpy.ops.mesh.primitive_torus_add(major_radius=0.022, minor_radius=0.005)
    ringo = bpy.context.object
    ringo.data.materials.append(M_["key"])
    ringo.location = (0, -0.045, 0)
    ringo.parent = k
    return [k, ringo]


def place_in_hand(objs, who, t_ref, along=(0, 0.08, 0)):
    rig = CH[who].rig
    sc.frame_set(fr(t_ref))
    hm = rig.matrix_world @ rig.pose.bones["hand_r"].matrix
    objs[0].matrix_world = hm @ Matrix.Translation(along)
    in_hand(objs[0], who, "hand_r", t_ref)


# radio handset in Kazemi's right hand (8-34.5)
hs = [P.box((0, 0, 0), (0.06, 0.04, 0.17), M_["radio"], "Handset")]
place_in_hand(hs, "kazemi", 9.0, along=(0, 0.07, 0.03))
show(hs, [(8.0, 34.5)])
hs2 = P.box((TABLE[0] + 0.12, TABLE[1] - 0.05, 0.8), (0.06, 0.17, 0.04), M_["radio"], "Handset on table")
show([hs2], [(0, 8.0), (34.5, END)])
# the key: in the soldier's hand 48.8-53.6, flying 53.6-54.25, on the floor, in my hand from 56.6
kh = key_mesh("Key soldier")
place_in_hand(kh, "soldier", 50.0)
show(kh, [(48.8, 53.6)])
kf = key_mesh("Key flying")
sc.frame_set(fr(53.6))
rig = CH["soldier"].rig
p0 = (rig.matrix_world @ rig.pose.bones["hand_r"].matrix).translation.copy()
p1 = Vector(KEY_FLOOR)
dur = 0.65
for j in range(int(dur * FPS) + 1):
    u = j / (dur * FPS)
    pos = p0.lerp(p1, u) + Vector((0, 0, 1.0 * 4 * u * (1 - u)))
    kf[0].location = pos
    kf[0].rotation_euler = (u * 14, u * 6, u * 3)
    kf[0].keyframe_insert("location", frame=fr(53.6) + j)
    kf[0].keyframe_insert("rotation_euler", frame=fr(53.6) + j)
kf[0].rotation_euler = (math.radians(90), 0, 0.6)
kf[0].location = p1
kf[0].keyframe_insert("location", frame=fr(53.6 + dur) + 1)
kf[0].keyframe_insert("rotation_euler", frame=fr(53.6 + dur) + 1)
for fc in fcurves_of(kf[0]):
    for k in fc.keyframe_points:
        k.interpolation = "LINEAR"
show(kf, [(53.6, 56.6)])
km = key_mesh("Key me")
place_in_hand(km, "me", 60.0)
show(km, [(56.6, END)])

# ------------------------------------------------------------------ camera: (t0, t1, cam0, cam1, aim0, aim1, lens)
SHOTS = [
    (0.0, 4.5, (1.2, 0.45, 2.3), (1.6, 0.6, 2.2), (8.5, 5.6, 0.9), (8.6, 5.7, 0.95), 18),
    (4.5, 8.0, (12.65, 7.75, 1.6), (12.55, 7.6, 1.55), (11.65, 6.4, 1.3), (11.65, 6.4, 1.3), 28),
    (8.0, 12.5, (7.3, 6.0, 1.6), (7.45, 6.25, 1.6), (8.6, 7.9, 1.45), (8.6, 7.9, 1.45), 26),
    (12.5, 15.6, (7.15, 1.75, 1.0), (7.15, 1.95, 1.0), (7.15, 3.3, 0.95), (7.15, 3.3, 0.95), 32),
    (15.6, 19.5, (6.75, 2.6, 1.05), (6.85, 2.75, 1.08), (11.6, 6.4, 1.45), (11.6, 6.4, 1.45), 32),
    (19.5, 24.0, (9.4, 3.9, 1.3), (9.6, 4.1, 1.2), (10.95, 5.5, 0.45), (10.95, 5.5, 0.4), 24),
    (24.0, 27.0, (11.75, 6.15, 0.25), (11.7, 6.1, 0.28), (10.6, 5.25, 0.55), (10.6, 5.25, 0.6), 26),
    None,   # H: the stain, computed below
    (30.5, 34.5, (5.6, 3.15, 1.5), (5.5, 3.25, 1.5), (3.6, 4.1, 1.4), (3.6, 4.1, 1.4), 30),
    (34.5, 39.0, (9.0, 3.0, 1.6), (9.45, 3.45, 1.6), (10.5, 6.0, 1.35), (10.9, 6.1, 1.35), 24),
    (39.0, 41.2, (12.4, 4.85, 1.5), (12.3, 4.95, 1.5), (11.55, 6.35, 1.35), (11.55, 6.35, 1.35), 30),
    None,   # K2: the bite, computed below
    (44.0, 46.0, (11.75, 6.55, 1.75), (11.65, 6.45, 1.72), (7.2, 3.9, 1.0), (7.2, 3.9, 1.0), 24),
    (46.0, 54.5, (8.9, 4.55, 1.5), (9.3, 4.8, 1.5), (11.4, 6.1, 1.45), (11.4, 6.1, 1.4), 28),
    (54.5, 57.0, (8.3, 4.75, 0.6), (8.2, 4.7, 0.65), (7.25, 4.15, 0.4), (7.25, 4.1, 0.55), 24),
    (57.0, 62.0, (7.4, 2.9, 1.55), (7.8, 3.3, 1.55), (11.3, 8.6, 1.3), (11.3, 8.8, 1.35), 24),
    (62.0, 67.5, (11.3, 6.2, 1.5), (11.3, 7.3, 1.53), (11.3, 9.0, 1.5), (11.3, 9.0, 1.53), 30),
    (67.5, 72.5, (3.6, 2.8, 1.45), (2.4, 3.6, 1.5), (0.0, 4.9, 1.2), (0.0, 4.9, 1.2), 24),
    (72.5, 74.5, (9.95, 6.95, 1.35), (9.85, 7.05, 1.4), (8.45, 8.25, 1.0), (8.6, 7.85, 1.4), 26),
    (74.5, END, (7.65, 4.3, 1.55), (7.6, 4.25, 1.52), (6.55, 3.8, 1.25), (6.55, 3.8, 1.25), 34),
]


def upper_arm(t):
    sc.frame_set(fr(t))
    r_ = CH["soldier"].rig
    return (r_.matrix_world @ r_.pose.bones["upperarm_r"].head).lerp(r_.matrix_world @ r_.pose.bones["lowerarm_r"].head, 0.6)


ua = upper_arm(28.5)
fwd = Vector((-math.sin(math.radians(30)), math.cos(math.radians(30)), 0))   # soldier's facing in H
side = Vector((fwd.y, -fwd.x, 0))                                            # his right
SHOTS[7] = (27.0, 30.5, tuple(ua + side * 0.55 + fwd * 0.5 + Vector((0, 0, 0.12))),
            tuple(ua + side * 0.48 + fwd * 0.44 + Vector((0, 0, 0.1))), tuple(ua), tuple(ua), 34)
ua = upper_arm(42.5)
fs = face(SOLDIER, KZ_MEET)
fwd = Vector((-math.sin(math.radians(fs)), math.cos(math.radians(fs)), 0))
side = Vector((fwd.y, -fwd.x, 0))
SHOTS[11] = (41.2, 44.0, tuple(ua + side * 0.5 + fwd * 0.35 + Vector((0, 0, 0.1))),
             tuple(ua + side * 0.4 + fwd * 0.3 + Vector((0, 0, 0.08))), tuple(ua), tuple(ua), 34)
cam = bpy.data.objects.new("Camera", bpy.data.cameras.new("Camera"))
sc.collection.objects.link(cam)
sc.camera = cam
cam.data.clip_start = 0.05
for t0, t1, c0, c1, a0, a1, lens in SHOTS:
    f0, f1 = fr(t0), fr(t1) - 1
    for f, c, a in ((f0, c0, a0), (f1, c1, a1)):
        cam.location = c
        cam.rotation_euler = (Vector(a) - Vector(c)).to_track_quat("-Z", "Y").to_euler()
        cam.keyframe_insert("location", frame=f)
        cam.keyframe_insert("rotation_euler", frame=f)
        cam.data.lens = lens
        cam.data.keyframe_insert("lens", frame=f)
for owner in (cam, cam.data):
    for fc in fcurves_of(owner):
        for k in fc.keyframe_points:
            k.interpolation = "LINEAR"
# ---- per shot: keep only the characters the camera can see (sampled every 4 frames, generous margins)
from bpy_extras.object_utils import world_to_camera_view
BONES = ("head", "pelvis", "hand_r", "hand_l", "foot_r", "foot_l", "spine_03", "lowerarm_r", "lowerarm_l", "calf_l", "calf_r")
VIS = {k: [] for k in CH}
for t0, t1, *_ in SHOTS:
    seen = set()
    for f in range(fr(t0), fr(t1), 4):
        sc.frame_set(f)
        for who, ch in CH.items():
            if who in seen or not any(a <= (f - 1) / FPS < b for a, b in PRESENT[who]):
                continue
            for bn in BONES:
                p = ch.rig.matrix_world @ ch.rig.pose.bones[bn].head
                v = world_to_camera_view(sc, cam, p)
                if v.z > 0 and -0.25 < v.x < 1.25 and -0.25 < v.y < 1.25:
                    seen.add(who)
                    break
    for who in seen:
        VIS[who].append((t0, t1))
print("VISIBLE", {k: [(round(a, 1), round(b, 1)) for a, b in v] for k, v in VIS.items()})
PRESENT = {k: [(max(a, c), min(b, d)) for a, b in VIS[k] for c, d in PRESENT[k] if max(a, c) < min(b, d)] for k in CH}
for who, ch in CH.items():
    for f in range(1, N + 1):
        t = (f - 1) / FPS
        st = dict(t=t, seed=ch.seed, worry=worry(who, t), talking=speaking(who, t), zombie=ch.zombie)
        if who == "soldierZ":
            st["scream"] = 0.25 + 0.35 * seg(t, 64.5, 66.0)
            st["talking"] = 64.5 < t < 67.0
        if who == "arian" and 31.0 <= t <= 33.4:
            st["smile"] = 0.8
        sk = ch.body.data.shape_keys
        for k, v in anim.face(st).items():
            if k in ch.keys:
                ch._put(sk, f'key_blocks["{k}"].value', 0, f, max(0.0, min(1.0, v)))
        if f == 1 or present(who, t) != present(who, t - 1 / FPS):
            ch.hide(f, not present(who, t))
    ch.flush()
import json
os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
json.dump({"cuts": [s[0] for s in SHOTS]}, open(os.path.join(HERE, "out", "cuts.json"), "w"))

# ------------------------------------------------------------------ look
sc.frame_set(1)
T.toonify(sc, samples=int(os.environ.get("SAMPLES", "4")))
for o in bpy.data.objects:                 # subdivision adds nothing in the flat look but triples the render time
    for md in o.modifiers:
        if md.type == "SUBSURF":
            md.render_levels = 0
inked = [o for o in bpy.data.objects if o.type == "MESH" and not any(
    k in o.name.lower() for k in ("high-poly", "lash", "brow", "teeth", "tongue", "court", "floor", "ceiling", "bite",
                                  "stain", "blood", "night", "tube", "wire", "chain", "led"))]
T.ink(inked, 0.005)
sc.render.resolution_x, sc.render.resolution_y = 540, 960
sc.render.film_transparent = False

args = sys.argv
if "--still" in args:
    os.makedirs(os.path.join(HERE, "test"), exist_ok=True)
    for f in [int(v) for v in args[args.index("--still") + 1].split(",")]:
        sc.frame_set(f)
        sc.render.filepath = os.path.join(HERE, "test", f"s_{f:04d}.png")
        bpy.ops.render.render(write_still=True)
if "--save" in args:
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(HERE, "sleeve.blend"))
