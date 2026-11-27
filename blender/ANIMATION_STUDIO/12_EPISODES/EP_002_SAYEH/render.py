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
    for o in bpy.data.collections["SHADOW"].all_objects:
        if o.type == "MESH":
            o.hide_render = not st["shadow"]
            o.visible_shadow = False
    for o in bpy.data.collections["DANIEL"].all_objects:
        if o.type == "MESH":
            o.visible_shadow = st["daniel_shadow"]
    L = st["light"]
    for name, e in base.items():
        lt = bpy.data.objects[name]
        if name == "EP2 key":                       # the moon through the window stays a little
            lt.data.energy = e * max(L, 0.18) if L <= 1 else e * 2
        else:
            lt.data.energy = e * L
    w = sc.world.node_tree.nodes["Background"].inputs["Strength"]
    w.default_value = 0.6 * (L if L <= 1 else 3)
    return st


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    argv = [a for a in argv if not a.endswith(".py")]
    bpy.ops.wm.open_mainfile(filepath=os.path.join(HERE, "EP_002.blend"))
    import generate_rig as G
    G.enable_addons()
    sc = bpy.context.scene
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
