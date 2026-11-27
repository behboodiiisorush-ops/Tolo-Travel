"""Render EP_002.blend frame by frame with the per-shot state (camera, front wall, who is visible, who casts a
shadow, light levels). Resumable: existing frames are skipped.
    blender/cast/bpy.sh ANIMATION_STUDIO/12_EPISODES/EP_002_SAYEH/render.py [F0 F1] [--still 60,250 --out DIR]
"""
import bpy, os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__))
STUDIO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(STUDIO, "00_CORE_SYSTEM"))
import project_config as PC  # noqa: E402
sys.path.insert(0, HERE)
from lines import fr, END  # noqa: E402

T = fr
N = fr(END) - 1
SHOTS = [(T(0), "WIDE"), (T(9), "REV"), (T(13), "MED"), (T(17), "FLOOR"), (T(22), "REV"), (T(27), "WIDE")]
FLASH = T(27.0)


def shot(f):
    cam = SHOTS[0][1]
    for s, c in SHOTS:
        if f >= s:
            cam = c
    return cam


def light_level(f):
    """1 = normal evening light, flicker at 5-7 s, dim (only the night through the window) until the flash."""
    t = (f - 1) / PC.FPS
    if t < 5.0:
        return 1.0
    if t < 7.2:
        pat = [1, .15, 1, 1, .1, .6, .05, 1, .1, .1, .7, .05, .05, .4, .05, .05]
        return pat[int((t - 5.0) * 7) % len(pat)]
    if f < FLASH:
        return 0.12
    if f < FLASH + 3:
        return 6.0                                  # the white flash
    return min(1.0, 0.5 + (f - FLASH) / 24)


def state(f):
    cam = shot(f)
    shadow_vis = cam == "REV" and f >= T(9)
    return dict(cam=cam, front=(cam == "REV"), shadow=shadow_vis, daniel_shadow=(f >= FLASH), light=light_level(f))


def apply(sc, f, base):
    st = state(f)
    sc.camera = bpy.data.objects["CAM_" + st["cam"]]
    for o in bpy.data.objects:
        if o.get("front"):
            o.hide_render = not st["front"]
    for o in bpy.data.objects:
        if o.type != "MESH":
            continue
        if o.name.startswith("SHADOW_"):
            o.hide_render = not st["shadow"]
            o.visible_shadow = False
        elif o.name.startswith("DANIEL_"):
            o.visible_shadow = st["daniel_shadow"]
        elif o.name.startswith("Coffee table"):
            o.hide_render = st["cam"] == "REV"          # it stands between the reverse camera and the family
    L = st["light"]
    for name, e in base.items():
        lt = bpy.data.objects[name]
        if name == "EP2 key":                       # the moon through the window stays a little
            lt.data.energy = e * max(L, 0.5) if L <= 1 else e * 2
        else:
            lt.data.energy = e * L
    w = sc.world.node_tree.nodes["Background"].inputs["Strength"]
    w.default_value = 0.6 * (L if L <= 1 else 3)
    return st


def fix_scene(sc):
    """Framing fixes found on the test stills (kept here so the 19-minute scene build need not run again)."""
    import render_shorts as RS
    ceil = bpy.data.objects["Living_Room ceiling"]
    if "ceiling front" not in bpy.data.objects:
        c = ceil.copy()
        c.data = ceil.data.copy()
        c.name = "ceiling front"
        sc.collection.objects.link(c)
        c.location = (ceil.location.x, -2.2 - 2.0 - 0.01, ceil.location.z + 0.04)   # no z-fighting with the room's ceiling
        c.scale = (3.0, 1.0, 1.0)
    fl = bpy.data.objects["floor front"]
    fl.data.materials.clear()
    fl.data.materials.append(bpy.data.materials["PP set floor_liv"])
    for name, loc, tgt, lens in (("WIDE", (0.35, -4.4, 1.2), (0.35, 0, 1.05), 20),
                                 ("MED", (0.1, -3.7, 1.25), (0.2, -1.0, 1.0), 22),
                                 ("FLOOR", (0.35, -3.7, 0.3), (0.35, -0.6, 0.4), 16)):
        cam = bpy.data.objects["CAM_" + name]
        RS.aim(cam, loc, tgt)
        cam.data.lens = lens
    key = bpy.data.objects["EP2 key"]
    key.rotation_euler = (math.radians(42), 0, math.radians(180))      # shadows fall towards the camera, close to the feet
    key.data.energy = 4.0                                               # strong enough to draw shadows on the floor
    for n in ("Living_Room ceiling", "ceiling front"):
        bpy.data.objects[n].visible_shadow = False                      # the ceiling blocked the moon: no floor shadows
    bpy.data.objects["EP2 fill"].location = (0.3, -5.2, 2.4)           # was in front of the wide camera (a bright band)
    for o in bpy.data.objects:
        if o.type == "LIGHT" and o.data.type == "AREA":
            o.visible_camera = False                                    # seen edge-on it was a bright line


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    argv = [a for a in argv if not a.endswith(".py")]
    bpy.ops.wm.open_mainfile(filepath=os.path.join(HERE, "EP_002.blend"))
    import generate_rig as G
    G.enable_addons()
    sc = bpy.context.scene
    fix_scene(sc)
    base = {o.name: o.data.energy for o in bpy.data.objects if o.type == "LIGHT"}
    out = os.path.join(HERE, "frames")
    if "--still" in argv:
        fl = [int(x) for x in argv[argv.index("--still") + 1].split(",")]
        out = argv[argv.index("--out") + 1] if "--out" in argv else os.path.join(HERE, "stills")
    else:
        nums = [int(a) for a in argv if a.isdigit()]
        f0, f1 = (nums + [1, N])[:2] if nums else (1, N)
        fl = list(range(f0, f1 + 1))
    os.makedirs(out, exist_ok=True)
    for f in fl:
        p = os.path.join(out, f"f_{f:04d}.png")
        if os.path.exists(p):
            continue
        sc.frame_set(f)
        st = apply(sc, f, base)
        sc.render.filepath = p
        bpy.ops.render.render(write_still=True)
        print("[EP002] frame", f, st, flush=True)


if __name__ == "__main__":
    main()
