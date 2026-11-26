"""08_ENVIRONMENT: Bedroom, Living_Room, Kitchen, Street — toon sets in the puppet look, one .blend per folder.
Props and the bedroom/street come from blender/BLENDER_ANIMATION/_build/lib.py (shared builders); the living room
and kitchen are built here from the same parts. Every set: its own collection, floor at z=0, open towards -Y
(where the 9:16 camera stands), no logos/flags/text.

    blender/cast/bpy.sh ANIMATION_STUDIO/08_ENVIRONMENT/build_environments.py [--only kitchen,...]
"""
import bpy, os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "00_CORE_SYSTEM"))
import project_config as PC  # noqa: E402
sys.path.insert(0, os.path.join(PC.BLENDER_DIR, "BLENDER_ANIMATION", "_build"))
import lib as L  # noqa: E402

L.PAL.update(sofa=(0.35, 0.55, 0.8), cushion=(0.98, 0.8, 0.35), wall_liv=(0.82, 0.9, 0.78), floor_liv=(0.6, 0.42, 0.3),
             wall_kit=(0.98, 0.95, 0.82), tile=(0.85, 0.88, 0.9), counter=(0.95, 0.95, 0.93), cab=(0.45, 0.7, 0.75),
             fridge=(0.92, 0.94, 0.95), stove=(0.25, 0.25, 0.28), plant=(0.3, 0.65, 0.35), pot=(0.85, 0.45, 0.3))


def room(r, W_, D_, H_, wall, floor):
    M = L.M
    L.B(r, (0, 0, -0.05), (W_, D_, 0.1), M(floor), "floor", line=0)
    L.B(r, (0, D_ / 2 + 0.08, H_ / 2), (W_, 0.16, H_), M(wall), "back wall", line=0)
    L.B(r, (-W_ / 2 - 0.08, 0, H_ / 2), (0.16, D_, H_), M(wall), "left wall", line=0)
    L.B(r, (W_ / 2 + 0.08, 0, H_ / 2), (0.16, D_, H_), M(wall), "right wall", line=0)
    L.B(r, (0, 0, H_ + 0.05), (W_, D_, 0.1), M("ceil"), "ceiling", line=0)


def window(r, x, D_, z=1.55, w=1.3, h=1.1):
    M = L.M
    L.B(r, (x, D_ / 2, z), (w, 0.18, h), M("glass", 0.9), "window", line=0.008)
    L.B(r, (x, D_ / 2 - 0.1, z), (w + 0.1, 0.05, 0.06), M("white"), "window bar", line=0.006)
    L.B(r, (x, D_ / 2 - 0.1, z), (0.05, 0.05, h + 0.1), M("white"), "window bar", line=0.006)


def sofa(c, name="Sofa"):
    r = L.root(name, c)
    M = L.M
    L.B(r, (0, 0, 0.25), (2.0, 0.9, 0.3), M("sofa"), "seat base", 0.05)
    L.B(r, (0, 0.33, 0.62), (2.0, 0.24, 0.6), M("sofa"), "back", 0.06)
    for x in (-0.95, 0.95):
        L.B(r, (x, 0, 0.5), (0.22, 0.9, 0.36), M("sofa"), "arm", 0.06)
    for x in (-0.45, 0.45):
        L.B(r, (x, -0.05, 0.47), (0.86, 0.75, 0.16), M("sofa"), "cushion", 0.06)
    L.B(r, (0.55, 0.15, 0.68), (0.4, 0.14, 0.36), M("cushion"), "pillow", 0.06)
    return r


def tv(c, name="TV"):
    r = L.root(name, c)
    M = L.M
    L.B(r, (0, 0, 0.25), (1.6, 0.45, 0.5), M("wood"), "cabinet", 0.02)
    L.B(r, (0, 0.05, 0.92), (1.2, 0.06, 0.7), M("dark"), "screen", 0.01)        # blank screen, no logo
    L.B(r, (0, 0.05, 0.54), (0.3, 0.2, 0.06), M("dark"), "stand")
    return r


def coffee_table(c, name="Coffee table"):
    r = L.root(name, c)
    M = L.M
    L.B(r, (0, 0, 0.4), (1.1, 0.6, 0.05), M("wood"), "top", 0.01)
    for x in (-0.5, 0.5):
        for y in (-0.25, 0.25):
            L.B(r, (x, y, 0.19), (0.05, 0.05, 0.38), M("wood_dark"), "leg")
    L.CY(r, (0.2, 0.05, 0.47), 0.05, 0.1, M("white"), "cup")
    return r


def plant(c, name="Plant"):
    r = L.root(name, c)
    M = L.M
    L.CY(r, (0, 0, 0.2), 0.18, 0.4, M("pot"), "pot")
    for i, (x, y, z, s) in enumerate(((0, 0, 0.65, 0.28), (0.12, 0.05, 0.85, 0.2), (-0.1, -0.06, 0.8, 0.22))):
        L.SP(r, (x, y, z), s, M("plant"), f"leaves{i}")
    return r


def living_room(c):
    r = L.root("Living_Room", c)
    W_, D_, H_ = 5.0, 4.4, 2.7
    room(r, W_, D_, H_, "wall_liv", "floor_liv")
    window(r, 1.2, D_)
    for o, at, rz in ((sofa(c), (-1.2, 0.4, 0), 90), (tv(c), (2.25, 0.4, 0), -90), (coffee_table(c), (0.4, 0.4, 0), 90),
                      (L.rug(c, "Living rug"), (0.4, 0.3, 0), 0), (plant(c), (-2.1, 1.75, 0), 0),
                      (L.lamp(c, "Floor lamp"), (2.0, 1.7, 0.0), 0), (L.shelf(c, "Living shelf"), (-0.9, 2.05, 1.25), 0)):
        L.place(o, at, rz)
        o.parent = r
    return r


def kitchen(c):
    r = L.root("Kitchen", c)
    W_, D_, H_ = 4.4, 4.0, 2.7
    M = L.M
    room(r, W_, D_, H_, "wall_kit", "tile")
    for i in range(int(W_ / 0.4)):                          # floor tiles
        L.B(r, (-W_ / 2 + 0.2 + i * 0.4, 0, 0.002), (0.012, D_, 0.004), M("curb"), "tile line", line=0)
    window(r, -0.4, D_, z=1.65, w=1.0, h=0.8)
    # counter along the back wall with cabinets, sink, stove
    L.B(r, (0, D_ / 2 - 0.32, 0.45), (W_ - 0.2, 0.6, 0.9), M("cab"), "cabinets", 0.01)
    L.B(r, (0, D_ / 2 - 0.32, 0.92), (W_ - 0.1, 0.64, 0.05), M("counter"), "worktop", 0.01)
    for k in range(6):
        L.B(r, (-W_ / 2 + 0.45 + k * 0.7, D_ / 2 - 0.63, 0.48), (0.62, 0.02, 0.8), M("cab"), "cabinet door", line=0.006)
    L.B(r, (-0.4, D_ / 2 - 0.3, 0.93), (0.6, 0.4, 0.04), M("metal"), "sink", line=0.006)
    L.B(r, (1.0, D_ / 2 - 0.3, 0.95), (0.6, 0.5, 0.03), M("stove"), "hob", line=0.006)
    for x in (0.85, 1.15):
        for y in (-0.1, 0.1):
            L.CY(r, (x, D_ / 2 - 0.3 + y, 0.975), 0.08, 0.01, M("dark"), "burner", line=0)
    L.B(r, (0, D_ / 2 - 0.18, 1.75), (W_ - 0.2, 0.35, 0.7), M("cab"), "wall cabinets", 0.01)
    # fridge on the right, table + chairs in the middle
    L.B(r, (W_ / 2 - 0.45, 0.6, 0.95), (0.8, 0.7, 1.9), M("fridge"), "fridge", 0.04)
    L.B(r, (W_ / 2 - 0.84, 0.6, 1.2), (0.03, 0.04, 0.5), M("metal"), "fridge handle", line=0)
    t = L.root("Kitchen table", c)
    L.CY(t, (0, 0, 0.74), 0.55, 0.05, M("wood"), "top", verts=32)
    L.CY(t, (0, 0, 0.37), 0.06, 0.7, M("wood_dark"), "leg")
    L.CY(t, (0, 0, 0.02), 0.3, 0.04, M("wood_dark"), "foot", verts=24)
    L.place(t, (-0.3, -0.3, 0)).parent = r
    for k, (x, y, rz) in enumerate(((-1.05, -0.3, 90), (0.45, -0.3, -90), (-0.3, 0.45, 180))):
        L.place(L.chair(c, f"Kitchen chair {k + 1}"), (x, y, 0), rz).parent = r
    return r


SETS = {"bedroom": ("BEDROOM", "Bedroom", L.bedroom), "living_room": ("LIVING_ROOM", "Living_Room", living_room),
        "kitchen": ("KITCHEN", "Kitchen", kitchen), "street": ("STREET", "Street", L.street)}


def main():
    only = sys.argv[sys.argv.index("--only") + 1].split(",") if "--only" in sys.argv else list(SETS)
    for key in only:
        folder, name, fn = SETS[key]
        sc = L.reset()
        c = L.coll(name)
        fn(c)
        L.look(sc, res=(540, 960), sky=(0.75, 0.86, 0.98), sun=2.4, sun_rot=(58, 0, 160 if key != "street" else -40))
        if key != "street":
            li = bpy.data.objects.new(name + " light", bpy.data.lights.new(name + " light", "AREA"))
            li.data.energy, li.data.size = 70, 2.5
            li.location = (0, 0, 2.6)
            c.objects.link(li)
            L.camera(sc, (0.1, -2.15 if key != "living_room" else -2.25, 1.5), (0.1, 1.0, 0.85), lens=16)
        else:
            L.camera(sc, (-4.0, -4.6, 1.7), (3.0, 4.5, 2.4), lens=20)
        out = PC.path("08_ENVIRONMENT", folder, name + ".blend")
        os.makedirs(os.path.dirname(out), exist_ok=True)
        bpy.context.preferences.filepaths.save_version = 0
        bpy.ops.wm.save_as_mainfile(filepath=out, compress=True)
        sc.frame_set(1)
        sc.render.filepath = PC.path("08_ENVIRONMENT", folder, name + "_preview.png")
        bpy.ops.render.render(write_still=True)
        print("saved", out)


if __name__ == "__main__":
    main()
