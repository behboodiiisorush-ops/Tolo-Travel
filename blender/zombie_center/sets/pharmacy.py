"""ENV_CITY_PHARMACY — the small dark pharmacy of CH01_SC005 (interior only; the door looks out on side street B).

Room x -3..3, y -2.5..2.5, floor 0, ceiling 2.8. The broken glass door is in the front wall (y = -2.5, x ≈ -1.6);
the counter runs across the back third; drawers behind it; four shelves (two tipped over), pills and boxes on the floor;
a battery-powered wall TV loops a plain emergency card (white on blue, no channel name, no emblem).

    import pharmacy
    R = pharmacy.build()   # dict: door, counter_back (where Arin crouches), tv, shelf_drag (the shelf he drags)
"""
import bpy, math, os, random
import props as P
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONT = os.path.join(HERE, "..", "..", "fonts", "Vazirmatn-FD-ExtraBold.ttf")
W, D, H = 6.0, 5.0, 2.8


def tv_card(path):
    im = Image.new("RGB", (1280, 720), (18, 52, 120))
    d = ImageDraw.Draw(im)
    f1 = ImageFont.truetype(FONT, 66, layout_engine=ImageFont.Layout.RAQM)
    f2 = ImageFont.truetype(FONT, 44, layout_engine=ImageFont.Layout.RAQM)
    d.rectangle([0, 0, 1280, 120], fill=(200, 30, 30))
    d.text((640, 60), "وضعیت اضطراری", font=f1, fill=(255, 255, 255), anchor="mm", direction="rtl", language="fa")
    lines = ["منطقه تحت قرنطینه.", "اولین مورد تأییدشده: ۲۴ روز پیش، منطقه‌ی شمالی.",
             "افراد دارای تب، خود را معرفی کنند."]
    for i, t in enumerate(lines):
        d.text((640, 260 + i * 110), t, font=f2, fill=(240, 244, 255), anchor="mm", direction="rtl", language="fa")
    im.save(path)
    return path


def build(tex_dir):
    rr = random.Random(11)
    floor = P.grime(P.tiles("MAT_PH_Floor", (0.75, 0.75, 0.72), (0.7, 0.7, 0.68), (0.4, 0.4, 0.38), size=0.4, rough=0.3),
                    2.5, 0.35, 0.2, 0.02)
    wall = P.grime(P.mat("MAT_PH_Wall", (0.72, 0.75, 0.72), rough=0.8), 2.0, 0.3, 0.1, 0.02)
    wood = P.wood("MAT_PH_Counter", (0.42, 0.3, 0.2), planks=False, rough=0.45)
    metal = P.grime(P.mat("MAT_PH_Shelf", (0.7, 0.72, 0.72), rough=0.4, metal=0.7), 4.0, 0.3, 0.15, 0.02)
    P.plane((0, 0, 0), (W, D), floor, name="PH_Floor")
    P.plane((0, 0, H), (W, D), P.mat("MAT_PH_Ceil", (0.8, 0.8, 0.78), rough=0.9), rot=(math.pi, 0, 0), name="PH_Ceiling")
    P.box((0, D / 2 + 0.05, H / 2), (W, 0.1, H), wall, "PH_Wall_back")
    P.box((W / 2 + 0.05, 0, H / 2), (0.1, D, H), wall, "PH_Wall_right")
    P.box((-W / 2 - 0.05, 0, H / 2), (0.1, D, H), wall, "PH_Wall_left")
    # front wall: shop window (right, dirty glass) + door opening (left)
    dx, dw = -1.6, 1.0
    P.box(((dx - dw / 2 - W / 2) / 2, -D / 2 - 0.05, H / 2), ((dx - dw / 2) + W / 2, 0.1, H), wall, "PH_Front_a")
    P.box((dx, -D / 2 - 0.05, (2.2 + H) / 2), (dw, 0.1, H - 2.2), wall, "PH_Front_top")
    P.box(((dx + dw / 2 + W / 2) / 2, -D / 2 - 0.05, 0.4), (W / 2 - (dx + dw / 2), 0.1, 0.8), wall, "PH_Front_low")
    glass = P.glass("MAT_PH_Glass", tint=(0.7, 0.75, 0.75), rough=0.35)
    P.box(((dx + dw / 2 + W / 2) / 2, -D / 2 - 0.03, 1.6), (W / 2 - (dx + dw / 2) - 0.1, 0.02, 1.55), glass, "PH_ShopWindow")
    frame = P.mat("MAT_PH_DoorFrame", (0.25, 0.26, 0.27), rough=0.4, metal=0.8)
    door = P.box((dx + 0.42, -D / 2 - 0.3, 1.08), (0.05, 0.9, 2.12), frame, "PH_Door")   # swung half open, glass gone
    door.rotation_euler.z = math.radians(-35)
    for i in range(26):                                              # glass shards at the door
        s = P.box((dx + rr.uniform(-0.6, 0.6), -D / 2 + rr.uniform(-0.3, 0.9), 0.004),
                  (rr.uniform(0.03, 0.12), rr.uniform(0.03, 0.1), 0.004), glass, "PH_Shard")
        s.rotation_euler.z = rr.uniform(0, 6.28)
    # counter across the back third, drawers behind it
    P.box((0.4, 0.9, 0.5), (4.2, 0.6, 1.0), wood, "PH_Counter", bevel=0.01)
    P.box((0.4, 0.9, 1.02), (4.3, 0.66, 0.04), P.mat("MAT_PH_Top", (0.85, 0.85, 0.83), rough=0.25), "PH_CounterTop")
    for i in range(6):
        for j in range(4):
            P.box((-1.5 + i * 0.75, D / 2 - 0.25, 0.3 + j * 0.42), (0.7, 0.4, 0.38), wood, "PH_Drawer", bevel=0.01)
            P.box((-1.5 + i * 0.75, D / 2 - 0.46, 0.3 + j * 0.42), (0.12, 0.02, 0.03), metal, "PH_DrawerHandle")
    # four shelves: two upright, two tipped over (one is the one he drags across the door)
    box_cols = [(0.85, 0.85, 0.82), (0.6, 0.75, 0.85), (0.9, 0.8, 0.6), (0.75, 0.85, 0.7)]

    def shelf(name, loc, rot, fill=True):
        root = P.empty(name, (0, 0, 0))
        for z in (0.1, 0.6, 1.1, 1.6):
            b = P.box((0, 0, z), (1.2, 0.4, 0.02), metal, name + "_board"); b.parent = root
            if fill:
                for k in range(5):
                    if rr.random() < 0.7:
                        bx = P.box((-0.5 + k * 0.24, 0, z + 0.09), (0.16, 0.12, 0.16),
                                   P.mat(f"MAT_PH_Box{k}", box_cols[k % 4], rough=0.7), name + "_box"); bx.parent = root
        for x in (-0.6, 0.6):
            for y in (-0.2, 0.2):
                c = P.cyl((x, y, 0), (x, y, 1.8), 0.012, metal, name + "_post", 6); c.parent = root
        root.location = loc; root.rotation_euler = rot
        return root
    shelf("PH_Shelf_A", (-2.3, 0.0, 0), (0, 0, math.radians(90)))
    shelf("PH_Shelf_B", (2.3, -0.6, 0), (0, 0, math.radians(90)))
    shelf("PH_Shelf_C", (0.6, -1.0, 0.2), (math.radians(84), 0, math.radians(8)), fill=False)        # tipped over
    drag = shelf("PH_Shelf_DRAG", (-0.4, -1.6, 0), (0, 0, math.radians(15)), fill=False)
    pills = [P.mat("MAT_PH_Pill_w", (0.95, 0.95, 0.92), 0.4), P.mat("MAT_PH_Pill_r", (0.8, 0.3, 0.25), 0.4),
             P.mat("MAT_PH_Pill_b", (0.4, 0.55, 0.85), 0.4)]
    for i in range(120):                                              # spilled pills and boxes on the floor
        P.sphere((rr.uniform(-2.6, 2.6), rr.uniform(-2.0, 0.4), 0.006), 0.007, pills[i % 3], "PH_Pill", scale=(1.6, 1, 0.8))
    for i in range(18):
        b = P.box((rr.uniform(-2.5, 2.5), rr.uniform(-1.9, 0.3), 0.06), (0.16, 0.12, 0.12),
                  P.mat(f"MAT_PH_FBox{i % 4}", box_cols[i % 4], rough=0.7), "PH_FloorBox")
        b.rotation_euler = (rr.uniform(-0.3, 0.3), rr.uniform(-0.3, 0.3), rr.uniform(0, 6.28))
    # the wall TV (left wall, high), running on a battery: the only bright thing in the room
    card = tv_card(os.path.join(tex_dir, "tv_card.png"))
    tv_m = P.image("MAT_PH_TV", card, strength=2.2)
    P.box((-W / 2 + 0.06, 0.6, 2.05), (0.06, 1.0, 0.6), P.mat("MAT_PH_TVbody", (0.03, 0.03, 0.03), 0.4), "PH_TV_body")
    scr = P.plane((-W / 2 + 0.095, 0.6, 2.05), (0.92, 0.52), tv_m, rot=(math.radians(90), 0, math.radians(-90)), name="PH_TV_screen")
    tvl = P.area_light((-W / 2 + 0.4, 0.6, 2.0), (1.0, 0.6, 1.0), 45, size=0.9, color=(0.45, 0.6, 1.0), name="PH_TV_glow")
    # cold street light through the door and the dirty window, a faint red exit light, nothing else
    P.area_light((dx, -D / 2 - 1.2, 2.2), (dx + 0.6, 0.5, 0.2), 180, size=1.0, color=(0.7, 0.8, 1.0), name="PH_Street")
    P.area_light((1.4, -D / 2 - 1.2, 2.0), (1.0, 0.6, 0.3), 120, size=2.2, color=(0.7, 0.8, 1.0), name="PH_Street_window")
    P.area_light((2.6, 2.2, 2.6), (2.0, 1.5, 1.6), 6, size=0.2, color=(1.0, 0.15, 0.1), name="PH_Exit")
    w = bpy.context.scene.world or bpy.data.worlds.new("World"); bpy.context.scene.world = w
    w.use_nodes = True; w.node_tree.nodes["Background"].inputs["Color"].default_value = (0.01, 0.012, 0.02, 1)
    return dict(door=(dx, -D / 2, 0.0), counter_back=(0.4, 1.55, 0.0), tv=(-W / 2 + 0.1, 0.6, 2.05), shelf_drag=drag)
