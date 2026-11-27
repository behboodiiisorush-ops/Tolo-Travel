"""ENV_NIKA_VIDEO_ROOM — the small white room Nika films herself in (seen only through her phone video).

Flat, slightly green fluorescent overhead light; a narrow metal bed; a heavy door with a small wire-glass window;
painted block walls; a ventilation grille (the hum we will hear again in the Centre). No signs, no logos.

    import nika_room
    R = nika_room.build()      # dict: bed_seat (x, y, z of the mattress top), door (world centre of the door)
Room: x -2..2, y -1.8..1.8, floor z 0, ceiling 2.7. The bed stands along the back wall (+Y), the door on the left wall.
"""
import bpy, math
import props as P

W, D, H = 4.0, 3.6, 2.7


def build():
    sc = bpy.context.scene
    wall = P.grime(P.tiles("MAT_NR_Block", (0.82, 0.83, 0.8), (0.8, 0.81, 0.78), (0.7, 0.71, 0.68),
                           size=0.4, rough=0.75, gap=0.004, width=0.2, wall=True), 3.0, 0.15, 0.1, 0.02)
    floor = P.grime(P.tiles("MAT_NR_Floor", (0.62, 0.64, 0.6), (0.6, 0.62, 0.58), (0.45, 0.46, 0.43), size=0.3, rough=0.35),
                    2.0, 0.25, 0.15, 0.03)
    ceil = P.mat("MAT_NR_Ceiling", (0.85, 0.86, 0.84), rough=0.9)
    metal = P.grime(P.mat("MAT_NR_Metal", (0.55, 0.57, 0.56), rough=0.45, metal=0.6), 5.0, 0.3, 0.2, 0.02)
    door_m = P.grime(P.mat("MAT_NR_Door", (0.7, 0.72, 0.7), rough=0.5, metal=0.3), 3.0, 0.3, 0.15, 0.02)
    sheet = P.mat("MAT_NR_Sheet", (0.86, 0.87, 0.86), rough=0.9)
    blanket = P.mat("MAT_NR_Blanket", (0.55, 0.6, 0.62), rough=0.95)
    P.plane((0, 0, 0), (W, D), floor, name="NR_Floor")
    P.plane((0, 0, H), (W, D), ceil, rot=(math.pi, 0, 0), name="NR_Ceiling")
    P.box((0, D / 2 + 0.05, H / 2), (W, 0.1, H), wall, "NR_Wall_back")
    P.box((0, -D / 2 - 0.05, H / 2), (W, 0.1, H), wall, "NR_Wall_front")
    P.box((W / 2 + 0.05, 0, H / 2), (0.1, D, H), wall, "NR_Wall_right")
    # left wall with a door opening
    dy, dw, dh = -0.3, 0.95, 2.1
    P.box((-W / 2 - 0.05, (dy - dw / 2 - D / 2) / 2, H / 2), (0.1, (dy - dw / 2) + D / 2, H), wall, "NR_Wall_left_a")
    P.box((-W / 2 - 0.05, (dy + dw / 2 + D / 2) / 2, H / 2), (0.1, D / 2 - (dy + dw / 2), H), wall, "NR_Wall_left_b")
    P.box((-W / 2 - 0.05, dy, (dh + H) / 2), (0.1, dw, H - dh), wall, "NR_Wall_left_top")
    P.box((-W / 2 - 0.02, dy, dh / 2), (0.05, dw - 0.02, dh - 0.01), door_m, "NR_Door", bevel=0.005)
    P.box((-W / 2 + 0.01, dy, dh / 2), (0.03, dw + 0.08, dh + 0.06), metal, "NR_DoorFrame_in")   # frame, thin
    glass = P.glass("MAT_NR_WireGlass", tint=(0.75, 0.8, 0.78), rough=0.25)
    P.box((-W / 2 + 0.005, dy, 1.55), (0.012, 0.22, 0.3), glass, "NR_DoorWindow")
    P.cyl((-W / 2 + 0.06, dy + 0.36, 1.02), (-W / 2 + 0.06, dy + 0.36, 1.1), 0.018, metal, "NR_DoorHandle")
    P.box((-W / 2 + 0.03, dy + 0.36, 1.18), (0.03, 0.06, 0.1), metal, "NR_DoorLock")
    # bed along the back wall
    bx, by = 0.3, D / 2 - 0.5
    for sx in (-0.95, 0.95):
        for sy in (-0.42, 0.42):
            P.cyl((bx + sx, by + sy, 0), (bx + sx, by + sy, 0.42), 0.02, metal, "NR_BedLeg")
    P.box((bx, by, 0.44), (2.0, 0.9, 0.04), metal, "NR_BedFrame")
    P.box((bx, by, 0.53), (1.95, 0.86, 0.14), sheet, "NR_Mattress", bevel=0.04)
    P.box((bx + 0.45, by + 0.05, 0.61), (1.0, 0.82, 0.03), blanket, "NR_Blanket", bevel=0.01)
    P.box((bx + 0.8, by + 0.15, 0.66), (0.4, 0.55, 0.1), sheet, "NR_Pillow", bevel=0.04)
    # ventilation grille high on the back wall, a small steel shelf, a plastic cup
    P.box((-1.2, D / 2 - 0.005, 2.35), (0.4, 0.02, 0.25), metal, "NR_Vent")
    for i in range(6):
        P.box((-1.2, D / 2 - 0.018, 2.26 + i * 0.035), (0.36, 0.01, 0.008), P.mat("MAT_NR_VentSlat", (0.2, 0.2, 0.2), 0.6), "NR_VentSlat")
    P.box((1.55, D / 2 - 0.15, 0.95), (0.5, 0.28, 0.02), metal, "NR_Shelf")
    P.cyl((1.5, D / 2 - 0.15, 0.96), (1.5, D / 2 - 0.15, 1.06), 0.035, P.mat("MAT_NR_Cup", (0.9, 0.9, 0.88), 0.3), "NR_Cup")
    # flat fluorescent overhead light, slightly green; low fill so the shadows stay soft and dull
    tube = P.emit("MAT_NR_Tube", (0.9, 1.0, 0.92), 6.0)
    P.box((0.2, 0.2, H - 0.03), (1.2, 0.18, 0.04), tube, "NR_LightTube")
    P.area_light((0.2, 0.2, H - 0.08), (0.2, 0.2, 0), 260, size=1.2, size_y=0.25, color=(0.92, 1.0, 0.9), name="NR_Fluo")
    P.area_light((0.0, -1.5, 1.6), (0.3, 1.0, 1.0), 40, size=2.0, color=(0.95, 1.0, 0.95), name="NR_Bounce")
    w = sc.world or bpy.data.worlds.new("World"); sc.world = w
    w.use_nodes = True
    w.node_tree.nodes["Background"].inputs["Color"].default_value = (0.02, 0.022, 0.02, 1)
    return dict(bed_seat=(bx - 0.4, by - 0.25, 0.6), door=(-W / 2, dy, 1.1))
