"""ENV_CITY_STREET — the abandoned night avenue (section A) and side street B for EP01 (CH01_SC001–SC004).

    import env_city
    S = env_city.build()        # returns {"bus": obj, "phone_spot": (x,y,z), "side_street_origin": ..., ...}

Layout (metres, +Y = up the avenue):
  avenue: road x ∈ [-6, 6], y ∈ [-45, 45]; sidewalks to |x| = 9; buildings beyond.
  fallen night bus «۴» across the lanes at y ≈ 6, lying on its LEFT side, roof towards -Y, tilted so one
  edge is raised ~0.45 m (Arin hides under it). Phone puddle at (1.6, 3.2, 0).
  side street B: branches off to +X at y ≈ 22 (width 7 m): trolley, fallen cable, parked car, lit shop window.
No signs with words, no logos, no flags, no place names. Only the route number «۴» on the bus.
"""
import bpy, math, random, os
from mathutils import Vector
import props as P

FONT = os.path.join(os.path.dirname(__file__), "..", "..", "fonts", "Vazirmatn-FD-ExtraBold.ttf")
R = random.Random(7)
COLL = None


def _coll():
    global COLL
    if COLL is None:
        COLL = bpy.data.collections.get("03_ENVIRONMENTS") or bpy.data.collections.new("03_ENVIRONMENTS")
        if COLL.name not in bpy.context.scene.collection.children:
            bpy.context.scene.collection.children.link(COLL)
    return COLL


def _own(o):
    for c in list(o.users_collection):
        c.objects.unlink(o)
    _coll().objects.link(o)
    return o


# ---------------------------------------------------------------- materials
def asphalt():
    m = P.mat("MAT_Asphalt_Wet", (0.12, 0.12, 0.13), rough=0.6)
    nt = m.node_tree; p = P._bsdf(m)
    tc = nt.nodes.new("ShaderNodeTexCoord")
    # fine grain
    g = nt.nodes.new("ShaderNodeTexNoise"); g.inputs["Scale"].default_value = 180; g.inputs["Detail"].default_value = 6
    nt.links.new(tc.outputs["Object"], g.inputs["Vector"])
    # large wet patches / puddles
    w = nt.nodes.new("ShaderNodeTexNoise"); w.inputs["Scale"].default_value = 0.35; w.inputs["Detail"].default_value = 4
    nt.links.new(tc.outputs["Object"], w.inputs["Vector"])
    wr = nt.nodes.new("ShaderNodeMapRange"); wr.inputs["From Min"].default_value = 0.52; wr.inputs["From Max"].default_value = 0.58
    nt.links.new(w.outputs["Fac"], wr.inputs["Value"])          # 1 = puddle
    rough = nt.nodes.new("ShaderNodeMapRange"); rough.inputs["To Min"].default_value = 0.55; rough.inputs["To Max"].default_value = 0.04
    nt.links.new(wr.outputs["Result"], rough.inputs["Value"])
    nt.links.new(rough.outputs["Result"], p.inputs["Roughness"])
    col = nt.nodes.new("ShaderNodeMix"); col.data_type = "RGBA"
    col.inputs[6].default_value = (0.018, 0.018, 0.02, 1); col.inputs[7].default_value = (0.008, 0.008, 0.009, 1)
    gm = nt.nodes.new("ShaderNodeMath"); gm.operation = "MAXIMUM"
    nt.links.new(wr.outputs["Result"], gm.inputs[0]); nt.links.new(g.outputs["Fac"], gm.inputs[1])
    gm.inputs[1].default_value = 0
    nt.links.new(wr.outputs["Result"], col.inputs[0])
    nt.links.new(col.outputs[2], p.inputs["Base Color"])
    b = nt.nodes.new("ShaderNodeBump"); b.inputs["Strength"].default_value = 0.25
    inv = nt.nodes.new("ShaderNodeMath"); inv.operation = "MULTIPLY"
    nt.links.new(g.outputs["Fac"], inv.inputs[0])
    one = nt.nodes.new("ShaderNodeMath"); one.operation = "SUBTRACT"; one.inputs[0].default_value = 1.0
    nt.links.new(wr.outputs["Result"], one.inputs[1])
    nt.links.new(one.outputs[0], inv.inputs[1])                  # no bump inside puddles (flat mirror)
    nt.links.new(inv.outputs[0], b.inputs["Height"]); nt.links.new(b.outputs["Normal"], p.inputs["Normal"])
    return m


def facade(name, base, lit_frac=0.06, seed=0):
    """Building wall with a procedural window grid: dark glass, a few dim lit windows, concrete between."""
    m = P.mat(name, base, rough=0.85)
    nt = m.node_tree; p = P._bsdf(m)
    tc = nt.nodes.new("ShaderNodeTexCoord")
    wc = P.wall_coords(nt, tc.outputs["Object"])
    sep = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(wc, sep.inputs[0])
    def frac(sock, period, lo, hi):
        d = nt.nodes.new("ShaderNodeMath"); d.operation = "DIVIDE"; d.inputs[1].default_value = period
        nt.links.new(sock, d.inputs[0])
        f = nt.nodes.new("ShaderNodeMath"); f.operation = "FRACT"; nt.links.new(d.outputs[0], f.inputs[0])
        a = nt.nodes.new("ShaderNodeMath"); a.operation = "GREATER_THAN"; a.inputs[1].default_value = lo
        b = nt.nodes.new("ShaderNodeMath"); b.operation = "LESS_THAN"; b.inputs[1].default_value = hi
        nt.links.new(f.outputs[0], a.inputs[0]); nt.links.new(f.outputs[0], b.inputs[0])
        m_ = nt.nodes.new("ShaderNodeMath"); m_.operation = "MULTIPLY"
        nt.links.new(a.outputs[0], m_.inputs[0]); nt.links.new(b.outputs[0], m_.inputs[1])
        return m_.outputs[0], d.outputs[0]
    wx, cellx = frac(sep.outputs[0], 3.0, 0.22, 0.78)
    wz, cellz = frac(sep.outputs[1], 3.2, 0.3, 0.82)
    win = nt.nodes.new("ShaderNodeMath"); win.operation = "MULTIPLY"
    nt.links.new(wx, win.inputs[0]); nt.links.new(wz, win.inputs[1])
    # no windows on the ground floor (shops: handled with separate geometry)
    gf = nt.nodes.new("ShaderNodeMath"); gf.operation = "GREATER_THAN"; gf.inputs[1].default_value = 3.6
    nt.links.new(sep.outputs[1], gf.inputs[0])
    win2 = nt.nodes.new("ShaderNodeMath"); win2.operation = "MULTIPLY"
    nt.links.new(win.outputs[0], win2.inputs[0]); nt.links.new(gf.outputs[0], win2.inputs[1])
    # which windows are lit: white noise per cell
    fl1 = nt.nodes.new("ShaderNodeMath"); fl1.operation = "FLOOR"; nt.links.new(cellx, fl1.inputs[0])
    fl2 = nt.nodes.new("ShaderNodeMath"); fl2.operation = "FLOOR"; nt.links.new(cellz, fl2.inputs[0])
    cmb = nt.nodes.new("ShaderNodeCombineXYZ"); nt.links.new(fl1.outputs[0], cmb.inputs[0]); nt.links.new(fl2.outputs[0], cmb.inputs[1])
    cmb.inputs[2].default_value = seed
    wn = nt.nodes.new("ShaderNodeTexWhiteNoise"); wn.noise_dimensions = "3D"; nt.links.new(cmb.outputs[0], wn.inputs["Vector"])
    lit = nt.nodes.new("ShaderNodeMath"); lit.operation = "LESS_THAN"; lit.inputs[1].default_value = lit_frac
    nt.links.new(wn.outputs["Value"], lit.inputs[0])
    litw = nt.nodes.new("ShaderNodeMath"); litw.operation = "MULTIPLY"
    nt.links.new(lit.outputs[0], litw.inputs[0]); nt.links.new(win2.outputs[0], litw.inputs[1])
    # colours
    wall_glass = nt.nodes.new("ShaderNodeMix"); wall_glass.data_type = "RGBA"
    wall_glass.inputs[6].default_value = (*P.lin(base), 1); wall_glass.inputs[7].default_value = (0.01, 0.012, 0.016, 1)
    nt.links.new(win2.outputs[0], wall_glass.inputs[0])
    nt.links.new(wall_glass.outputs[2], p.inputs["Base Color"])
    rr = nt.nodes.new("ShaderNodeMapRange"); rr.inputs["To Min"].default_value = 0.85; rr.inputs["To Max"].default_value = 0.08
    nt.links.new(win2.outputs[0], rr.inputs["Value"]); nt.links.new(rr.outputs["Result"], p.inputs["Roughness"])
    p.inputs["Emission Color"].default_value = (1.0, 0.62, 0.3, 1)
    es = nt.nodes.new("ShaderNodeMath"); es.operation = "MULTIPLY"; es.inputs[1].default_value = 0.05
    nt.links.new(litw.outputs[0], es.inputs[0]); nt.links.new(es.outputs[0], p.inputs["Emission Strength"])
    P.grime(m, scale=0.4, dark=0.55, rough_var=0.05, bump=0.0)
    return m


# ---------------------------------------------------------------- props
def car(loc, yaw, colour, name, damaged=False, door_open=False):
    body_m = P.mat(name + "_paint", colour, rough=0.35, metal=0.4)
    P.grime(body_m, scale=3.0, dark=0.5, rough_var=0.15, bump=0.0)
    glass = P.mat(name + "_glass", (0.02, 0.025, 0.03), rough=0.05)
    tyre = P.mat(name + "_tyre", (0.03, 0.03, 0.03), rough=0.8)
    root = P.empty(name, (0, 0, 0)); _own(root)
    low = P.box((0, 0, 0.55), (1.8, 4.5, 0.62), body_m, name + "_body", bevel=0.12); _own(low)
    cab = P.box((0, -0.25, 1.1), (1.62, 2.3, 0.56), glass, name + "_cabin", bevel=0.1); _own(cab)
    # taper the cabin roof (windscreen slope)
    me = cab.data
    for v in me.vertices:
        if v.co.z > 1.2:
            v.co.y *= 0.72; v.co.x *= 0.9
    roof = P.box((0, -0.35, 1.37), (1.45, 1.55, 0.05), body_m, name + "_roof", bevel=0.03); _own(roof)
    for x in (-0.82, 0.82):
        for y in (-1.45, 1.45):
            w = P.cyl((x - 0.1, y, 0.34), (x + 0.1, y, 0.34), 0.34, tyre, name + "_wheel", 20); _own(w)
            P.parent_keep(w, root)
    for o in (low, cab, roof):
        P.parent_keep(o, root)
    lights = P.mat(name + "_lamp", (0.6, 0.6, 0.55), rough=0.1)
    for x in (-0.6, 0.6):
        l = P.box((x, 2.26, 0.7), (0.35, 0.03, 0.12), lights, name + "_head"); _own(l); P.parent_keep(l, root)
    root.location = loc
    root.rotation_euler = (0, 0, math.radians(yaw))
    if damaged:
        root.rotation_euler = (math.radians(R.uniform(-2, 2)), math.radians(R.uniform(-3, 3)), math.radians(yaw))
    return root


def bus(loc, name="PROP_BUS_NIGHT_4"):
    paint = P.mat("MAT_Bus_Paint", (0.62, 0.6, 0.55), rough=0.45, metal=0.2)
    P.grime(paint, scale=1.2, dark=0.45, rough_var=0.2, bump=0.02)
    glass = P.mat("MAT_Bus_Glass", (0.015, 0.02, 0.025), rough=0.05)
    tyre = P.mat("MAT_Bus_Tyre", (0.03, 0.03, 0.03), rough=0.85)
    root = P.empty(name, (0, 0, 0)); _own(root)
    # built upright (length along X, width along Y, height Z), then tipped onto its left side
    parts = [P.box((0, 0, 1.95), (11.5, 2.5, 2.5), paint, name + "_body", bevel=0.15)]
    # underside (faces the avenue once the bus is on its side): chassis rails, axles, tank, exhaust, dirt
    under = P.grime(P.mat("MAT_Bus_Under", (0.08, 0.075, 0.07), rough=0.85, metal=0.3), 3.0, 0.5, 0.1, 0.08)
    for y in (-0.55, 0.55):
        parts.append(P.box((0, y, 0.6), (10.4, 0.2, 0.25), under, name + "_rail"))
    for x in (-3.8, 3.6):
        parts.append(P.cyl((x, -1.1, 0.52), (x, 1.1, 0.52), 0.07, under, name + "_axle"))
    parts.append(P.box((0.4, 0.75, 0.62), (1.6, 0.6, 0.45), under, name + "_tank", bevel=0.05))
    parts.append(P.cyl((-1.0, -0.8, 0.55), (-5.5, -0.8, 0.55), 0.06, under, name + "_exhaust"))
    parts.append(P.box((0, 0, 0.72), (11.0, 2.3, 0.05), under, name + "_floor"))
    for x in (-3.8, 3.6):          # wheel arches (dark recess around each wheel)
        for y in (-1.2, 1.2):
            parts.append(P.box((x, y, 0.85), (1.3, 0.12, 0.6), under, name + "_arch"))
    for side in (-1, 1):
        parts.append(P.box((0.3, side * 1.26, 2.15), (9.6, 0.04, 1.0), glass, name + "_windows"))
    parts.append(P.box((5.76, 0, 2.0), (0.05, 2.2, 1.4), glass, name + "_windscreen"))
    parts.append(P.box((-5.76, 0, 2.3), (0.05, 2.0, 0.8), glass, name + "_rearwindow"))
    roof_m = P.grime(P.mat("MAT_Bus_Roof", (0.5, 0.5, 0.48), rough=0.6, metal=0.3), 2.5, 0.4, 0.2, 0.03)
    parts.append(P.box((-1.5, 0, 3.32), (2.6, 1.7, 0.28), roof_m, name + "_aircon", bevel=0.06))
    for x in (1.8, 4.0):
        parts.append(P.box((x, 0, 3.24), (0.9, 0.9, 0.1), roof_m, name + "_hatch", bevel=0.02))
    for y in (-1.22, 1.22):
        parts.append(P.box((0, y, 3.2), (11.2, 0.06, 0.06), roof_m, name + "_gutter"))
    stripe = P.mat("MAT_Bus_Stripe", (0.55, 0.1, 0.06), rough=0.5)
    for y in (-1.27, 1.27):
        parts.append(P.box((0, y, 1.15), (11.4, 0.02, 0.18), stripe, name + "_stripe"))
    for x in (-2.5, 2.6):
        for y in (-1.26, 1.26):
            parts.append(P.box((x, y, 1.3), (1.1, 0.03, 1.9), glass, name + "_door"))
    for x in (-3.8, 3.6):
        for y in (-1.15, 1.15):
            parts.append(P.cyl((x, y - 0.16, 0.52), (x, y + 0.16, 0.52), 0.52, tyre, name + "_wheel", 28))
            rim = bpy.data.materials.get("MAT_Bus_Rim") or P.mat("MAT_Bus_Rim", (0.4, 0.4, 0.4), rough=0.4, metal=0.8)
            parts.append(P.cyl((x, y - 0.17 * (1 if y < 0 else -1), 0.52), (x, y - 0.19 * (1 if y < 0 else -1), 0.52), 0.3, rim, name + "_rim", 20))
    # destination display: route number only
    disp = P.mat("MAT_Bus_Display", (0.02, 0.02, 0.02), rough=0.3, emit=(1.0, 0.55, 0.1), strength=2.5)
    parts.append(P.box((5.79, 0, 3.0), (0.03, 1.4, 0.3), P.mat("MAT_Bus_DispBg", (0.01, 0.01, 0.01), rough=0.3), name + "_dispbg"))
    bpy.ops.object.text_add(location=(5.82, 0, 2.9), rotation=(math.pi / 2, 0, math.pi / 2))
    t = bpy.context.object; t.name = name + "_route"; t.data.body = "۴"; t.data.size = 0.26; t.data.align_x = "CENTER"
    if os.path.exists(FONT):
        t.data.font = bpy.data.fonts.load(FONT, check_existing=True)
    t.data.materials.append(disp); parts.append(t)
    for o in parts:
        _own(o); P.parent_keep(o, root)
    # tip onto its left side (roof towards -Y), raised edge ~0.45 m on the +Y... side resting on debris
    root.rotation_euler = (math.radians(-90 + 22), 0, math.radians(8))   # side down, tipped past 90° so the chassis overhangs a low wedge gap
    root.location = (loc[0], loc[1], 1.25 + 0.2)
    return root


def traffic_light(loc, name="PROP_TRAFFIC_LIGHT"):
    pole_m = P.mat("MAT_Pole", (0.15, 0.16, 0.15), rough=0.5, metal=0.6)
    house_m = P.mat("MAT_TL_House", (0.04, 0.04, 0.04), rough=0.6)
    amber = P.mat("MAT_TL_Amber", (0.3, 0.15, 0.0), rough=0.2, emit=(1.0, 0.55, 0.05), strength=6.0)
    off = P.mat("MAT_TL_Off", (0.05, 0.02, 0.02), rough=0.2)
    root = P.empty(name, (0, 0, 0)); _own(root)
    ps = [P.cyl((0, 0, 0), (0, 0, 4.2), 0.08, pole_m, name + "_pole"),
          P.cyl((0, 0, 4.1), (-2.6, 0, 4.1), 0.06, pole_m, name + "_arm"),
          P.box((-2.6, 0, 3.7), (0.32, 0.3, 0.95), house_m, name + "_house", bevel=0.03)]
    for i, (z, mm) in enumerate(((4.0, off), (3.7, amber), (3.4, off))):
        ps.append(P.cyl((-2.6, -0.16, z), (-2.6, -0.2, z), 0.1, mm, name + f"_lamp{i}"))
    for o in ps:
        _own(o); P.parent_keep(o, root)
    tl = bpy.data.lights.new(name + "_glow", "POINT"); tl.energy = 25; tl.color = (1.0, 0.6, 0.15); tl.shadow_soft_size = 0.1
    lo = bpy.data.objects.new(name + "_glow", tl); lo.location = (-2.6, -0.4, 3.7); _coll().objects.link(lo); P.parent_keep(lo, root)
    root.location = loc
    root["amber_material"] = amber.name
    return root


def street_lamp(loc, on=True, name="PROP_STREET_LAMP", sodium=False):
    pole_m = bpy.data.materials.get("MAT_Pole") or P.mat("MAT_Pole", (0.15, 0.16, 0.15), rough=0.5, metal=0.6)
    col = (1.0, 0.62, 0.3) if sodium else (0.78, 0.88, 1.0)
    head = P.mat(name + "_head", (0.4, 0.4, 0.4), rough=0.3, emit=col if on else None, strength=8.0 if on else 0)
    root = P.empty(name, (0, 0, 0)); _own(root)
    side = -1 if loc[0] > 0 else 1
    ps = [P.cyl((0, 0, 0), (0, 0, 7.5), 0.09, pole_m, name + "_pole"),
          P.cyl((0, 0, 7.4), (side * 1.4, 0, 7.6), 0.06, pole_m, name + "_arm"),
          P.box((side * 1.5, 0, 7.5), (0.6, 0.25, 0.12), head, name + "_lamp")]
    for o in ps:
        _own(o); P.parent_keep(o, root)
    if on:
        L = bpy.data.lights.new(name + "_light", "SPOT"); L.energy = 1400; L.color = col
        L.spot_size = math.radians(110); L.spot_blend = 0.6; L.shadow_soft_size = 0.3
        lo = bpy.data.objects.new(name + "_light", L); lo.location = (side * 1.5, 0, 7.35)
        _coll().objects.link(lo); P.parent_keep(lo, root)
    root.location = loc
    return root


def building_block(x0, x1, y0, y1, h, colour, seed):
    m = facade(f"MAT_Facade_{seed}", colour, lit_frac=0.03, seed=seed)
    o = P.box(((x0 + x1) / 2, (y0 + y1) / 2, h / 2), (abs(x1 - x0), abs(y1 - y0), h), m, f"ENV_Building_{seed}")
    _own(o)
    # ground-floor shutters (closed, dirty) on the street face
    sh = bpy.data.materials.get("MAT_Shutter") or P.grime(P.mat("MAT_Shutter", (0.25, 0.25, 0.24), rough=0.5, metal=0.5), 0.8, 0.5, 0.2, 0.0)
    face_x = x0 if abs(x0) < abs(x1) else x1
    s = 1 if face_x > 0 else -1
    y = y0 + 1.2
    while y < y1 - 2.0:
        w = R.uniform(2.4, 3.6)
        _own(P.box((face_x - s * 0.05, y + w / 2, 1.5), (0.08, w - 0.3, 2.9), sh, "ENV_Shutter"))
        y += w + 0.6
    # floor ledges + a cornice on the street face: breaks the flat wall, catches light, reads as real buildings
    led = bpy.data.materials.get("MAT_Ledge") or P.grime(P.mat("MAT_Ledge", (0.5, 0.48, 0.45), rough=0.8), 1.5, 0.5, 0.1, 0.03)
    z = 3.4
    while z < h - 1.0:
        _own(P.box((face_x - s * 0.12, (y0 + y1) / 2, z), (0.25, abs(y1 - y0), 0.14), led, "ENV_Ledge"))
        z += 3.2
    _own(P.box((face_x - s * 0.2, (y0 + y1) / 2, h - 0.2), (0.4, abs(y1 - y0), 0.4), led, "ENV_Cornice"))
    return o


def _bag(xy, m, rr):
    """A tied bin bag: lumpy, slumped on the ground, creased plastic (not a ball)."""
    sz = rr.uniform(0.26, 0.34); sq = rr.uniform(0.5, 0.62)
    o = P.sphere((xy[0], xy[1], sz * sq * 0.78), sz, m, "ENV_TrashBag", scale=(1, rr.uniform(0.75, 1.2), sq))
    o.rotation_euler.z = rr.uniform(0, 6.28)
    tx = bpy.data.textures.new("TX_Bag", "CLOUDS"); tx.noise_scale = rr.uniform(0.09, 0.13); tx.noise_depth = 2
    sub = o.modifiers.new("sub", "SUBSURF"); sub.levels = sub.render_levels = 2
    d = o.modifiers.new("lumps", "DISPLACE"); d.texture = tx; d.strength = 0.07; d.mid_level = 0.5
    tx2 = bpy.data.textures.new("TX_BagCrease", "STUCCI"); tx2.noise_scale = 0.04
    d2 = o.modifiers.new("creases", "DISPLACE"); d2.texture = tx2; d2.strength = 0.012
    knot = P.sphere((xy[0], xy[1], sz * sq * 1.5), 0.045, m, "ENV_TrashBagKnot", scale=(1, 1, 1.6))
    knot.parent = o; knot.matrix_parent_inverse = o.matrix_world.inverted()
    _own(knot)
    return o


def debris(n, area, seed=3):
    rr = random.Random(seed)
    paper = P.mat("MAT_Paper", (0.6, 0.58, 0.52), rough=0.8)
    bag = P.mat("MAT_Bag", (0.025, 0.025, 0.027), rough=0.42)
    (xa, xb), (ya, yb) = area
    for i in range(n):
        x, y = rr.uniform(xa, xb), rr.uniform(ya, yb)
        if rr.random() < 0.7:
            o = P.plane((x, y, 0.004), (rr.uniform(0.15, 0.3), rr.uniform(0.2, 0.3)), paper,
                        (0, 0, rr.uniform(0, 6.28)), "ENV_Paper")
        else:
            o = _bag((x, y), bag, rr)
        _own(o)


# ---------------------------------------------------------------- build
def build():
    sc = bpy.context.scene
    asph = asphalt()
    side = P.tiles("MAT_Sidewalk", (0.32, 0.31, 0.3), (0.28, 0.27, 0.26), (0.15, 0.15, 0.15), size=0.5, rough=0.7)
    curb = P.grime(P.mat("MAT_Curb", (0.4, 0.39, 0.37), rough=0.8), 2.0, 0.6, 0.1, 0.05)
    _own(P.plane((0, 0, 0), (12, 90), asph, name="ENV_Road_A"))
    for s in (-1, 1):
        _own(P.box((s * 7.5, 0, 0.075), (3.0, 90, 0.15), side, "ENV_Sidewalk_A"))
        _own(P.box((s * 6.05, 0, 0.075), (0.15, 90, 0.16), curb, "ENV_Curb_A"))
    # side street B (+X at y = 22): road + gap in the right-hand buildings
    _own(P.plane((22, 22, 0.001), (32, 7), asph, name="ENV_Road_B"))
    for s in (-1, 1):
        _own(P.box((22, 22 + s * 4.75, 0.075), (32, 2.5, 0.15), side, "ENV_Sidewalk_B"))
    cols = [(0.42, 0.4, 0.37), (0.36, 0.34, 0.32), (0.48, 0.44, 0.38), (0.3, 0.31, 0.32), (0.44, 0.42, 0.4)]
    seed = 0
    for s in (-1, 1):
        y = -45.0
        while y < 45:
            w = R.uniform(9, 15)
            if s == 1 and y < 26 and y + w > 18:        # leave the side street open
                y = 26.0
                continue
            building_block(s * 9.0, s * 22.0, y, min(45, y + w), R.uniform(12, 28), cols[seed % len(cols)], seed)
            seed += 1
            y += w + 0.15
    for s in (-1, 1):                                    # buildings along side street B
        x = 10.5
        while x < 38:
            w = R.uniform(8, 12)
            building_block(x, x + w, 22 + s * 6.0, 22 + s * 18.0, R.uniform(10, 20), cols[seed % len(cols)], seed)
            seed += 1
            x += w + 0.15
    S = {}
    S["bus"] = bus((0.5, 7.0, 0))
    S["traffic_light"] = traffic_light((5.7, -6.0, 0.15))
    for i, (x, y, on) in enumerate(((7.2, -20, True), (-7.2, -4, False), (7.2, 3.0, True), (7.2, 14, True), (-7.2, 30, True),
                                    (7.2, 40, False), (-7.2, -34, True))):
        street_lamp((x, y, 0.15), on, f"PROP_STREET_LAMP_{i}", sodium=(i in (5,)))
    carcols = [(0.25, 0.26, 0.28), (0.55, 0.53, 0.5), (0.18, 0.2, 0.25), (0.35, 0.12, 0.1), (0.5, 0.5, 0.48), (0.12, 0.13, 0.12)]
    spots = [(-3.0, -12, 4), (3.2, -18, -8), (-3.4, 16, 172), (3.0, 26, 186), (-2.8, -28, 10), (4.4, 33, -20)]
    S["cars"] = [car((x, y, 0), yaw, carcols[i], f"PROP_CAR_ABANDONED_{i}", damaged=True) for i, (x, y, yaw) in enumerate(spots)]
    S["side_car"] = car((26, 24.2, 0), 90, (0.3, 0.3, 0.32), "PROP_CAR_PARKED_B")
    for i, (x, y, on) in enumerate(((16, 26.6, True), (30, 17.4, True))):
        street_lamp((x, y, 0.15), on, f"PROP_STREET_LAMP_B{i}")
    # lit shop window on side street B (the crawler stops in its light): warm interior glow, no sign
    shop = P.mat("MAT_ShopWindow", (0.2, 0.2, 0.2), rough=0.05, emit=(1.0, 0.85, 0.6), strength=3.0)
    S["shop_window"] = _own(P.box((20.0, 15.95, 1.5), (4.0, 0.05, 2.4), shop, "PROP_SHOP_WINDOW_LIT"))
    sl = bpy.data.lights.new("LGT_ShopWindow", "AREA"); sl.energy = 220; sl.size = 3.5; sl.color = (1.0, 0.85, 0.6)
    so = bpy.data.objects.new("LGT_ShopWindow", sl); so.location = (20.0, 16.2, 1.5); so.rotation_euler = (math.radians(-90), 0, 0)
    _coll().objects.link(so)
    debris(40, ((-5.5, 5.5), (-30, 30)))
    debris(15, ((12, 34), (19.5, 24.5)), seed=9)
    S["phone_spot"] = (1.6, 3.4, 0.0)
    S["side_street_origin"] = (10.0, 22.0, 0.0)
    # world: night sky + atmospheric fog
    w = bpy.data.worlds.new("WORLD_City_Night"); sc.world = w; w.use_nodes = True
    bg = w.node_tree.nodes["Background"]; bg.inputs[0].default_value = (0.03, 0.045, 0.085, 1); bg.inputs[1].default_value = 3.0
    vol = w.node_tree.nodes.new("ShaderNodeVolumePrincipled")
    vol.inputs["Density"].default_value = 0.004; vol.inputs["Color"].default_value = (0.55, 0.6, 0.7, 1)
    w.node_tree.links.new(vol.outputs[0], w.node_tree.nodes["World Output"].inputs["Volume"])
    moon = bpy.data.lights.new("LGT_Moon", "SUN"); moon.energy = 6.0; moon.color = (0.6, 0.7, 1.0); moon.angle = math.radians(1)
    mo = bpy.data.objects.new("LGT_Moon", moon); mo.rotation_euler = (math.radians(55), 0, math.radians(-35)); _coll().objects.link(mo)
    # low ground fog layer
    fog = P.box((0, 5, 0.45), (14, 90, 0.9), bpy.data.materials.new("MAT_GroundFog"), "FX_GroundFog"); _own(fog)
    fm = fog.data.materials[0]; fm.use_nodes = True; nt = fm.node_tree
    nt.nodes.remove(nt.nodes["Principled BSDF"])
    v = nt.nodes.new("ShaderNodeVolumePrincipled"); v.inputs["Density"].default_value = 0.025
    nt.links.new(v.outputs[0], nt.nodes["Material Output"].inputs["Volume"])
    return S
