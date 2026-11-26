"""Modular house (reusable across episodes) + interaction rigs (doors, drawers, switches, pickups).

    import house as H
    h = H.build()                 # returns a House with .doors, .drawers, .switches, .lights, .spots
    h.doors["living"].swing(f0, f1, 0, 95)        # open the living-room door (degrees)
    h.doors["living"].press_handle(f)              # handle dips when a hand presses it
    h.switches["hall"].flip(f, on=False)           # light switch (also turns its lamps off)
    h.drawers["kitchen_1"].slide(f0, f1, 0.0, 0.35)
Plan (metres, ground floor, walls 0.12 thick, ceiling 2.7):
    hallway x -0.7..0.7, y 0..7.5 (front door at y=0, arch to the kitchen, doors to living room + bedroom)
    kitchen x -4.2..-0.7, y 0..4      bedroom x -4.2..-0.7, y 4..7.5      living room x 0.7..5.7, y 0..5
"""
import bpy, math, random
from mathutils import Vector
import props as P

H_WALL, T = 2.7, 0.12
COLLS = ["CHARACTERS", "ENVIRONMENT", "FURNITURE", "PROPS", "CAMERAS", "LIGHTING", "RIGS", "ANIMATION"]


def collections():
    sc = bpy.context.scene
    out = {}
    for n in COLLS:
        c = bpy.data.collections.get(n) or bpy.data.collections.new(n)
        if c.name not in sc.collection.children:
            sc.collection.children.link(c)
        out[n] = c
    return out


def put(obj, coll):
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    coll.objects.link(obj)
    for ch in obj.children:
        put(ch, coll)
    return obj


# ------------------------------------------------------------------ palette (muted blue-grey, matte)
def mats():
    g = P.grime
    return dict(
        wall=g(P.mat("Wall paint", (0.46, 0.52, 0.57), 0.85), 1.2, 0.86, 0.05, 0.015),
        wall_k=g(P.mat("Kitchen wall", (0.55, 0.58, 0.56), 0.85), 1.2, 0.86, 0.05, 0.015),
        ceiling=P.mat("Ceiling", (0.7, 0.72, 0.74), 0.9),
        wood=P.wood("Floor boards", (0.36, 0.26, 0.19), True, 0.55),
        tiles=P.tiles("Kitchen tiles", (0.5, 0.53, 0.55), (0.44, 0.47, 0.5), (0.3, 0.32, 0.34), 0.3, 0.5),
        trim=P.mat("Trim", (0.82, 0.84, 0.85), 0.6),
        door=g(P.mat("Door paint", (0.62, 0.66, 0.68), 0.6), 3, 0.9, 0.05, 0.01),
        frame=P.mat("Door frame", (0.78, 0.8, 0.81), 0.55),
        metal=P.mat("Brushed metal", (0.62, 0.64, 0.66), 0.35, 0.9),
        dark=P.mat("Dark metal", (0.12, 0.13, 0.14), 0.5, 0.6),
        glass=P.mat("Window glass", (0.75, 0.85, 0.9), 0.04, alpha=0.18),
        sky=P.emit("Night sky", (0.42, 0.55, 0.7), 0.7),
        counter=P.mat("Counter top", (0.56, 0.57, 0.56), 0.45),
        cabinet=g(P.mat("Cabinet", (0.32, 0.4, 0.44), 0.6), 4, 0.9, 0.05, 0.01),
        fabric=g(P.mat("Sofa fabric", (0.3, 0.36, 0.42), 0.95), 25, 0.85, 0.05, 0.12),
        fabric2=g(P.mat("Armchair fabric", (0.45, 0.32, 0.3), 0.95), 25, 0.85, 0.05, 0.12),
        rug=g(P.mat("Rug", (0.4, 0.3, 0.32), 0.95), 30, 0.75, 0.05, 0.15),
        runner=g(P.mat("Runner", (0.32, 0.38, 0.5), 0.95), 30, 0.7, 0.05, 0.15),
        furn=P.wood("Furniture wood", (0.42, 0.3, 0.2), False, 0.5, 3),
        bed=g(P.mat("Bed linen", (0.7, 0.72, 0.74), 0.95), 12, 0.9, 0.05, 0.08),
        plastic=P.mat("Switch plastic", (0.9, 0.9, 0.88), 0.4),
        tv=P.mat("TV", (0.03, 0.03, 0.035), 0.25),
        lamp=P.emit("Lamp glow", (1.0, 0.92, 0.78), 6.0),
        fridge=P.mat("Fridge", (0.78, 0.8, 0.8), 0.4, 0.2),
        art=[P.grime(P.mat(f"Picture {i}", c, 0.8), 3, 0.6) for i, c in
             enumerate([(0.35, 0.45, 0.55), (0.55, 0.5, 0.4), (0.3, 0.42, 0.38)])],
    )


# ------------------------------------------------------------------ walls with openings
def wall(a, b, openings, m, name, coll, h=H_WALL):
    """Wall from a to b (2D). openings: list of (offset along wall, width, bottom, top)."""
    a, b = Vector((a[0], a[1], 0)), Vector((b[0], b[1], 0))
    d = (b - a)
    L = d.length
    u = d.normalized()
    ang = math.atan2(u.y, u.x)
    cuts = sorted(openings)
    segs, x = [], 0.0
    for off, w, lo, hi in cuts:
        segs.append((x, off - w / 2, 0, h))
        if lo > 0:
            segs.append((off - w / 2, off + w / 2, 0, lo))
        segs.append((off - w / 2, off + w / 2, hi, h))
        x = off + w / 2
    segs.append((x, L, 0, h))
    out = []
    for s0, s1, z0, z1 in segs:
        if s1 - s0 < 1e-3 or z1 - z0 < 1e-3:
            continue
        c = a + u * ((s0 + s1) / 2)
        o = P.box((c.x, c.y, (z0 + z1) / 2), (s1 - s0, T, z1 - z0), m, name, rot=(0, 0, ang))
        out.append(put(o, coll))
    return out


class Door:
    """A hinged door leaf with a lever handle. The hinge empty rotates about Z."""
    def __init__(self, name, center, axis, width, M, C, hinge_side=1, swing_dir=1):
        cx, cy = center
        self.name = name
        ang = 0.0 if axis == "x" else math.pi / 2
        u = Vector((math.cos(ang), math.sin(ang), 0))
        n = Vector((-u.y, u.x, 0))
        hp = Vector((cx, cy, 0)) - u * (width / 2) * hinge_side
        self.hinge = put(P.empty(f"{name} hinge", hp), C["RIGS"])
        self.hinge.rotation_mode = "XYZ"
        leaf = P.box((cx, cy, 1.03), (width - 0.02, 0.04, 2.05), M["door"], f"{name} door", rot=(0, 0, ang), bevel=0.006)
        # raised panels
        for z in (0.55, 1.5):
            for s in (1, -1):
                pnl = P.box((cx + n.x * s * 0.022, cy + n.y * s * 0.022, z), (width * 0.62, 0.006, 0.7), M["door"],
                            f"{name} panel", rot=(0, 0, ang), bevel=0.004)
                P.parent_keep(pnl, leaf)
        self.handle = put(P.empty(f"{name} handle pivot", (cx + u.x * hinge_side * (width / 2 - 0.08),
                                                            cy + u.y * hinge_side * (width / 2 - 0.08), 1.0)), C["RIGS"])
        self.handle.rotation_mode = "XYZ"
        for s in (1, -1):
            hp2 = self.handle.location + n * s * 0.04
            lever = P.box(tuple(hp2 - u * hinge_side * 0.055), (0.11, 0.018, 0.018), M["metal"], f"{name} lever",
                          rot=(0, 0, ang), bevel=0.006)
            rose = P.cyl(hp2 - n * s * 0.02, hp2, 0.025, M["metal"], f"{name} rose")
            for o in (lever, rose):
                P.parent_keep(o, self.handle)
        P.parent_keep(self.handle, leaf)
        P.parent_keep(leaf, self.hinge)
        put(leaf, C["ENVIRONMENT"])
        self.leaf = leaf
        self.u, self.n, self.sdir = u, n, swing_dir * hinge_side
        # frame (casing) on both faces
        for s in (1, -1):
            off = n * s * (T / 2 + 0.01)
            for k in (1, -1):
                put(P.box((cx + u.x * k * (width / 2 + 0.04) + off.x, cy + u.y * k * (width / 2 + 0.04) + off.y, 1.06),
                          (0.07, 0.02, 2.12), M["frame"], f"{name} casing", rot=(0, 0, ang)), C["ENVIRONMENT"])
            put(P.box((cx + off.x, cy + off.y, 2.15), (width + 0.15, 0.02, 0.07), M["frame"], f"{name} casing",
                      rot=(0, 0, ang)), C["ENVIRONMENT"])

    def handle_world(self):
        bpy.context.view_layer.update()
        return self.handle.matrix_world.translation.copy()

    def swing(self, f0, f1, a0, a1):
        for f, a in ((f0, a0), (f1, a1)):
            self.hinge.rotation_euler.z = math.radians(a) * self.sdir
            self.hinge.keyframe_insert("rotation_euler", index=2, frame=f)

    def press_handle(self, f, hold=10):
        for ff, a in ((f - 3, 0), (f, -35), (f + hold, -35), (f + hold + 4, 0)):
            self.handle.rotation_euler = (0, 0, 0)
            self.handle.rotation_euler[0 if abs(self.u.x) > 0.5 else 1] = math.radians(a)
            self.handle.keyframe_insert("rotation_euler", frame=ff)


class Drawer:
    def __init__(self, name, loc, size, axis_out, M, C):
        self.body = put(P.box(loc, size, M["cabinet"], f"{name} drawer", bevel=0.005), C["FURNITURE"])
        self.out = Vector(axis_out)
        self.rest = Vector(loc)
        knob = P.cyl(Vector(loc) + self.out * (size[1] / 2 if abs(self.out.y) else size[0] / 2),
                     Vector(loc) + self.out * (size[1] / 2 + 0.03 if abs(self.out.y) else size[0] / 2 + 0.03),
                     0.012, M["metal"], f"{name} knob")
        P.parent_keep(knob, self.body)

    def slide(self, f0, f1, d0, d1):
        for f, d in ((f0, d0), (f1, d1)):
            self.body.location = self.rest + self.out * d
            self.body.keyframe_insert("location", frame=f)


class Switch:
    def __init__(self, name, loc, facing, M, C, lights=()):
        ang = {"+x": math.pi / 2, "-x": -math.pi / 2, "+y": math.pi, "-y": 0}[facing]
        plate = P.box(loc, (0.08, 0.012, 0.12), M["plastic"], f"{name} switch plate", rot=(0, 0, ang), bevel=0.004)
        self.rocker = P.box(loc, (0.035, 0.02, 0.05), M["plastic"], f"{name} switch rocker", rot=(0, 0, ang), bevel=0.004)
        put(plate, C["PROPS"]), put(self.rocker, C["PROPS"])
        self.lights = list(lights)

    def flip(self, f, on):
        self.rocker.rotation_euler.x = math.radians(0 if on else 14)
        self.rocker.keyframe_insert("rotation_euler", index=0, frame=f)
        for li, e, mat in self.lights:
            li.data.energy = e if on else 0
            li.data.keyframe_insert("energy", frame=f)
            if mat:
                s = mat.node_tree.nodes["Emission"].inputs["Strength"]
                s.default_value = 6.0 if on else 0.0
                s.keyframe_insert("default_value", frame=f)


def pickup(obj, rig, bone, f_grab, f_release=None):
    """Hand picks an object up at f_grab (Child Of constraint keyed on)."""
    c = obj.constraints.new("CHILD_OF")
    c.target = rig
    c.subtarget = bone
    bpy.context.scene.frame_set(f_grab)
    c.set_inverse_pending = True
    for f, v in ((f_grab - 1, 0.0), (f_grab, 1.0)) + (((f_release - 1, 1.0), (f_release, 0.0)) if f_release else ()):
        c.influence = v
        c.keyframe_insert("influence", frame=f)
    return c


# ------------------------------------------------------------------ the house
class House:
    pass


def build():
    C = collections()
    M = mats()
    E, F, PR, L = C["ENVIRONMENT"], C["FURNITURE"], C["PROPS"], C["LIGHTING"]
    h = House()
    h.doors, h.drawers, h.switches, h.lights, h.spots = {}, {}, {}, {}, {}
    rnd = random.Random(3)
    # floors / ceilings
    put(P.box((0, 3.75, -0.05), (1.4, 7.5, 0.1), M["wood"], "Hall floor"), E)
    put(P.box((3.2, 2.5, -0.05), (5.0, 5.0, 0.1), M["wood"], "Living floor"), E)
    put(P.box((-2.45, 2.0, -0.05), (3.5, 4.0, 0.1), M["tiles"], "Kitchen floor"), E)
    put(P.box((-2.45, 5.75, -0.05), (3.5, 3.5, 0.1), M["wood"], "Bedroom floor"), E)
    for c, s in (((0, 3.75), (1.4, 7.5)), ((3.2, 2.5), (5.0, 5.0)), ((-2.45, 3.75), (3.5, 7.5))):
        put(P.box((c[0], c[1], H_WALL + 0.05), (s[0], s[1], 0.1), M["ceiling"], "Ceiling"), E)
    # walls: (a, b, openings[(offset, width, bottom, top)], material)
    W = [((-4.2, 0), (5.7, 0), [(4.2, 0.95, 0, 2.12), (1.7, 1.2, 0.95, 2.05), (7.4, 1.6, 0.8, 2.1)], "wall"),
         ((-4.2, 7.5), (0.7, 7.5), [(1.7, 1.2, 0.9, 2.05), (4.2, 0.8, 1.0, 2.0)], "wall"),
         ((0.7, 5.0), (5.7, 5.0), [], "wall"),
         ((5.7, 0), (5.7, 5.0), [(2.5, 1.6, 0.8, 2.1)], "wall"),
         ((-4.2, 0), (-4.2, 7.5), [(2.0, 1.2, 0.95, 2.05), (5.8, 1.2, 0.9, 2.05)], "wall"),
         ((-0.7, 0), (-0.7, 7.5), [(1.7, 1.1, 0, 2.25), (5.0, 0.9, 0, 2.12)], "wall"),
         ((0.7, 0), (0.7, 7.5), [(2.0, 0.9, 0, 2.12)], "wall"),
         ((-4.2, 4.0), (-0.7, 4.0), [], "wall_k")]
    for a, b, op, m in W:
        wall(a, b, op, M[m], "Wall", E)
    # opening to the kitchen: wide cased opening with a header (clean, like the reference hallway)
    put(P.box((-0.7, 1.7, 2.3), (T + 0.06, 1.3, 0.1), M["trim"], "Opening header"), E)
    for k in range(-1, 2, 2):
        put(P.box((-0.7, 1.7 + k * 0.6, 1.15), (T + 0.06, 0.08, 2.3), M["trim"], "Opening column"), E)
    # baseboards
    for a, b in (((-0.64, 0.1), (-0.64, 7.4)), ((0.64, 0.1), (0.64, 7.4)), ((0.76, 0.06), (5.64, 0.06)),
                 ((0.76, 4.94), (5.64, 4.94)), ((5.64, 0.1), (5.64, 4.9)), ((-4.14, 0.1), (-4.14, 7.4)),
                 ((-4.1, 0.06), (-0.76, 0.06)), ((-4.1, 7.44), (-0.76, 7.44))):
        a, b = Vector(a), Vector(b)
        c = (a + b) / 2
        d = b - a
        put(P.box((c.x, c.y, 0.05), (d.length, 0.02, 0.1), M["trim"], "Baseboard", rot=(0, 0, math.atan2(d.y, d.x))), E)
    # windows: glass + frame + night sky beyond
    for (x, y, z, w, hh, axis) in ((-2.5, 0, 1.5, 1.2, 1.1, "x"), (3.2, 0, 1.45, 1.6, 1.3, "x"), (-2.5, 7.5, 1.48, 1.2, 1.15, "x"),
                                   (0, 7.5, 1.5, 0.8, 1.0, "x"), (5.7, 2.5, 1.45, 1.6, 1.3, "y"), (-4.2, 2.0, 1.5, 1.2, 1.1, "y"),
                                   (-4.2, 5.8, 1.48, 1.2, 1.15, "y")):
        rot = (math.pi / 2, 0, 0) if axis == "x" else (math.pi / 2, 0, math.pi / 2)
        out = Vector((0, -0.6 if y == 0 else 0.6, 0)) if axis == "x" else Vector((0.6 if x > 0 else -0.6, 0, 0))
        put(P.plane((x, y, z), (w, hh), M["glass"], rot, "Window glass"), E)
        put(P.plane((x + out.x, y + out.y, z), (w * 1.6, hh * 1.6), M["sky"], rot, "Window sky"), E)
        for dz in (-hh / 2, hh / 2):
            put(P.box((x, y, z + dz), (w if axis == "x" else 0.14, 0.14 if axis == "x" else w, 0.05), M["trim"], "Window frame"), E)
        for dw in (-w / 2, 0, w / 2):
            put(P.box((x + (dw if axis == "x" else 0), y + (0 if axis == "x" else dw), z),
                      (0.05 if axis == "x" else 0.14, 0.14 if axis == "x" else 0.05, hh), M["trim"], "Window frame"), E)
    # doors
    h.doors["front"] = Door("Front", (0, 0), "x", 0.95, M, C, hinge_side=1, swing_dir=1)
    h.doors["living"] = Door("Living", (0.7, 2.0), "y", 0.9, M, C, hinge_side=1, swing_dir=-1)
    h.doors["bedroom"] = Door("Bedroom", (-0.7, 5.0), "y", 0.9, M, C, hinge_side=-1, swing_dir=1)
    # ---- hallway: coat hooks with jackets, framed picture, runner, console + bowl, shoes
    put(P.box((0.67, 5.2, 1.65), (0.04, 0.9, 0.05), M["furn"], "Coat rail"), F)
    for k, col in enumerate([(0.2, 0.24, 0.3), (0.3, 0.32, 0.22)]):
        put(P.cyl((0.6, 4.95 + k * 0.4, 1.62), (0.6, 4.95 + k * 0.4, 1.0), 0.13,
                  P.grime(P.mat(f"Coat {k}", col, 0.95), 10, 0.8), "Hanging coat"), PR)
    put(P.box((-0.67, 3.3, 1.5), (0.03, 0.7, 0.5), M["frame"], "Picture frame"), PR)
    put(P.box((-0.655, 3.3, 1.5), (0.01, 0.6, 0.4), M["art"][0], "Picture"), PR)
    put(P.box((0, 3.6, 0.006), (0.8, 5.6, 0.012), M["runner"], "Hall runner"), PR)
    put(P.box((0.5, 0.9, 0.42), (0.3, 0.9, 0.04), M["furn"], "Console top"), F)
    for dy in (-0.4, 0.4):
        put(P.box((0.5, 0.9 + dy, 0.2), (0.28, 0.03, 0.4), M["furn"], "Console side"), F)
    put(P.sphere((0.5, 0.75, 0.47), 0.08, M["metal"], "Key bowl", (1, 1, 0.35)), PR)
    for k in range(2):
        put(P.box((-0.45, 0.45 + k * 0.18, 0.04), (0.12, 0.28, 0.08), M["dark"], "Shoe"), PR)
    # ---- kitchen (like the reference: sink under the window, cabinets, drawers)
    put(P.box((-2.45, 0.32, 0.45), (3.4, 0.6, 0.9), M["cabinet"], "Base cabinets", bevel=0.01), F)
    # counter top with a real hole for the sink
    for x0, x1, y0, y1 in ((-4.175, -2.78, 0.0, 0.64), (-2.22, -0.725, 0.0, 0.64), (-2.78, -2.22, 0.0, 0.12),
                           (-2.78, -2.22, 0.52, 0.64)):
        put(P.box(((x0 + x1) / 2, (y0 + y1) / 2, 0.92), (x1 - x0, y1 - y0, 0.04), M["counter"], "Counter"), F)
    # recessed stainless basin: bottom, four sides, drain
    sx, sy, bw, bd, dep = -2.5, 0.32, 0.56, 0.4, 0.18
    put(P.box((sx, sy, 0.94 - dep), (bw, bd, 0.012), M["metal"], "Sink bottom"), F)
    for dx, dy, w_, d_ in ((-bw / 2, 0, 0.012, bd), (bw / 2, 0, 0.012, bd), (0, -bd / 2, bw, 0.012), (0, bd / 2, bw, 0.012)):
        put(P.box((sx + dx, sy + dy, 0.94 - dep / 2), (w_, d_, dep), M["metal"], "Sink side"), F)
    put(P.box((sx, sy, 0.94), (bw + 0.04, bd + 0.04, 0.008), M["metal"], "Sink rim") , F)
    put(P.cyl((sx, sy, 0.94 - dep + 0.007), (sx, sy, 0.94 - dep + 0.01), 0.03, M["dark"], "Drain"), F)
    rim = [o for o in bpy.data.objects if o.name.startswith("Sink rim")][-1]
    hole = P.box((sx, sy, 0.94), (bw - 0.01, bd - 0.01, 0.05), M["metal"], "rim cut")
    bo = rim.modifiers.new("cut", "BOOLEAN")
    bo.object = hole
    bo.operation = "DIFFERENCE"
    hole.hide_render = True
    hole.hide_viewport = True
    put(P.cyl((-2.5, 0.08, 0.94), (-2.5, 0.08, 1.22), 0.018, M["metal"], "Tap"), F)
    put(P.cyl((-2.5, 0.08, 1.22), (-2.5, 0.3, 1.16), 0.016, M["metal"], "Tap spout"), F)
    put(P.box((-2.45, 0.2, 2.05), (3.4, 0.36, 0.7), M["cabinet"], "Wall cabinets", bevel=0.01), F)
    for k, x in enumerate((-3.8, -3.3, -1.7, -1.2)):
        h.drawers[f"kitchen_{k + 1}"] = Drawer(f"Kitchen {k + 1}", (x, 0.63, 0.75), (0.45, 0.04, 0.22), (0, 1, 0), M, C)
    put(P.box((-3.9, 3.55, 0.95), (0.7, 0.7, 1.9), M["fridge"], "Fridge", bevel=0.03), F)
    put(P.box((-2.3, 2.4, 0.75), (1.2, 0.8, 0.05), M["furn"], "Kitchen table"), F)
    for dx in (-0.55, 0.55):
        for dy in (-0.35, 0.35):
            put(P.box((-2.3 + dx, 2.4 + dy, 0.37), (0.05, 0.05, 0.74), M["furn"], "Table leg"), F)
    for x, y, r in ((-2.8, 1.85, 0), (-1.8, 1.85, 0), (-2.3, 3.0, math.pi)):
        put(P.box((x, y, 0.45), (0.42, 0.42, 0.04), M["furn"], "Chair seat"), F)
        put(P.box((x, y - 0.19 if r == 0 else y + 0.19, 0.72), (0.42, 0.04, 0.52), M["furn"], "Chair back"), F)
    put(P.cyl((-2.3, 2.4, 0.78), (-2.3, 2.4, 0.86), 0.06, M["plastic"], "Mug"), PR)
    # ---- living room
    put(P.box((3.2, 4.45, 0.25), (2.3, 0.9, 0.42), M["fabric"], "Sofa seat", bevel=0.06), F)
    put(P.box((3.2, 4.85, 0.6), (2.3, 0.22, 0.75), M["fabric"], "Sofa back", bevel=0.06), F)
    for dx in (-1.2, 1.2):
        put(P.box((3.2 + dx, 4.45, 0.4), (0.22, 0.9, 0.55), M["fabric"], "Sofa arm", bevel=0.06), F)
    put(P.box((3.2, 3.3, 0.38), (1.1, 0.6, 0.04), M["furn"], "Coffee table"), F)
    put(P.box((3.2, 3.3, 0.18), (1.0, 0.5, 0.02), M["furn"], "Coffee shelf"), F)
    put(P.box((3.2, 2.9, 0.006), (2.6, 2.0, 0.012), M["rug"], "Living rug"), PR)
    put(P.box((3.2, 0.3, 0.3), (1.8, 0.45, 0.6), M["furn"], "TV unit", bevel=0.01), F)
    put(P.box((3.2, 0.32, 1.05), (1.3, 0.05, 0.75), M["tv"], "TV"), F)
    put(P.box((5.45, 3.6, 1.0), (0.4, 1.2, 2.0), M["furn"], "Bookcase"), F)
    for k in range(4):
        for j in range(6):
            put(P.box((5.38, 3.1 + j * 0.18, 0.35 + k * 0.45), (0.22, 0.12, 0.3),
                      P.mat(f"Book {k}{j}", rnd.choice([(0.5, 0.25, 0.22), (0.25, 0.35, 0.45), (0.55, 0.5, 0.35),
                                                         (0.3, 0.4, 0.3)]), 0.8), "Book"), PR)
    put(P.box((1.6, 3.9, 0.35), (0.8, 0.8, 0.45), M["fabric2"], "Armchair", bevel=0.06), F)
    put(P.cyl((5.2, 4.6, 0), (5.2, 4.6, 1.5), 0.015, M["dark"], "Floor lamp pole"), F)
    put(P.cyl((5.2, 4.6, 1.45), (5.2, 4.6, 1.7), 0.18, P.mat("Lamp shade", (0.85, 0.8, 0.7), 0.9), "Lamp shade"), F)
    for k, (y, z) in enumerate(((1.4, 1.6), (2.8, 1.55))):
        put(P.box((0.77, y, z), (0.03, 0.6, 0.45), M["frame"], "Picture frame"), PR)
        put(P.box((0.79, y, z), (0.01, 0.5, 0.36), M["art"][1 + k % 2], "Picture"), PR)
    # ---- bedroom
    put(P.box((-3.3, 6.6, 0.25), (1.5, 2.0, 0.4), M["furn"], "Bed frame"), F)
    put(P.box((-3.3, 6.5, 0.5), (1.45, 1.8, 0.14), M["bed"], "Mattress", bevel=0.04), F)
    put(P.box((-3.3, 7.35, 0.75), (1.55, 0.08, 0.9), M["furn"], "Headboard"), F)
    put(P.box((-3.3, 7.05, 0.62), (0.9, 0.3, 0.12), M["bed"], "Pillow", bevel=0.05), F)
    put(P.box((-1.25, 4.35, 0.75), (0.9, 0.5, 0.04), M["furn"], "Desk"), F)
    put(P.box((-3.9, 4.4, 1.05), (0.55, 0.7, 2.1), M["furn"], "Wardrobe", bevel=0.01), F)
    # switches, outlets, lamps
    lamp_specs = {"hall": [(0, 1.8), (0, 5.2)], "kitchen": [(-2.45, 1.8)], "living": [(3.2, 2.5)], "bedroom": [(-2.45, 5.8)]}
    for room, spots in lamp_specs.items():
        lst = []
        for (x, y) in spots:
            shade = P.cyl((x, y, H_WALL - 0.02), (x, y, H_WALL - 0.1), 0.22, M["lamp"], f"{room} ceiling lamp")
            put(shade, L)
            li = P.area_light((x, y, H_WALL - 0.12), (x, y, 0), 90, 0.6, (1.0, 0.9, 0.75), name=f"{room} light")
            put(li, L)
            lst.append((li, 90, None))
        h.lights[room] = lst
    h.switches["hall"] = Switch("Hall", (0.63, 0.55, 1.1), "-x", M, C, h.lights["hall"])
    h.switches["kitchen"] = Switch("Kitchen", (-0.77, 2.45, 1.1), "-x", M, C, h.lights["kitchen"])
    h.switches["living"] = Switch("Living", (0.77, 2.65, 1.1), "+x", M, C, h.lights["living"])
    for (x, y, f) in ((-0.63, 4.0, "+x"), (0.77, 4.2, "+x"), (-3.5, 0.63, "-y")):
        put(P.box((x, y, 0.3), (0.07, 0.012, 0.07) if f == "-y" else (0.012, 0.07, 0.07), M["plastic"], "Outlet"), PR)
    w = bpy.data.worlds.new("House world")
    bpy.context.scene.world = w
    w.color = (0.05, 0.06, 0.08)
    h.M, h.C = M, C
    return h
