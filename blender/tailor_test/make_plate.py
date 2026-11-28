"""Painted background plate for the «خیاط کوچولو» style test (system python3: numpy + Pillow).
Watercolour / gouache look: soft pigment variation, darker pooled edges, paper grain, wobbly hand-cut shapes.
No outlines on the background (as in 1930s cartoons: inked characters over painted sets).

    python3 make_plate.py          -> plate.png (720x1280)
"""
import math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

W, H = 720, 1280
rng = np.random.default_rng(7)
random.seed(7)


def noise(scale, seed, octaves=3):
    out = np.zeros((H, W), np.float32)
    amp, tot = 1.0, 0.0
    r = np.random.default_rng(seed)
    for o in range(octaves):
        gw, gh = max(2, int(W / scale) + 2), max(2, int(H / scale) + 2)
        g = Image.fromarray((r.random((gh, gw)) * 255).astype(np.uint8))
        out += amp * (np.asarray(g.resize((W, H), Image.BICUBIC), np.float32) / 255 - 0.5)
        tot += amp
        amp *= 0.5
        scale /= 2.2
    return out / tot


GRAIN = noise(3, 1, 2)
BLOT = noise(90, 2, 4)
canvas = np.zeros((H, W, 3), np.float32)


def C(hexs):
    return np.array([int(hexs[i:i + 2], 16) / 255 for i in (1, 3, 5)], np.float32)


def wobble(pts, amp=2.5, step=14):
    out = []
    for (x0, y0), (x1, y1) in zip(pts, pts[1:] + pts[:1]):
        n = max(1, int(math.hypot(x1 - x0, y1 - y0) / step))
        for k in range(n):
            t = k / n
            out.append((x0 + (x1 - x0) * t + random.uniform(-amp, amp), y0 + (y1 - y0) * t + random.uniform(-amp, amp)))
    return out


def mask_of(draw_fn):
    m = Image.new("L", (W, H), 0)
    draw_fn(ImageDraw.Draw(m))
    return np.asarray(m.filter(ImageFilter.GaussianBlur(0.8)), np.float32) / 255


def paint(mask, col, var=0.07, edge=0.22, seed=0, grad=None):
    """Lay a wash: colour with pigment variation, darker rim where the paint pooled."""
    global canvas
    col = C(col) if isinstance(col, str) else np.asarray(col, np.float32)
    v = noise(40, 100 + seed, 3)
    c = col[None, None, :] * (1 + var * 2 * v[..., None] + 0.05 * GRAIN[..., None])
    if grad is not None:
        c = c * grad[..., None]
    soft = np.asarray(Image.fromarray((mask * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(6)),
                      np.float32) / 255
    rim = np.clip(mask - soft, 0, 1) * 2.2
    c = c * (1 - edge * rim[..., None])
    a = mask[..., None]
    canvas = canvas * (1 - a) + c * a


def rect(x0, y0, x1, y1, amp=2.0):
    return lambda d: d.polygon(wobble([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], amp), fill=255)


def ellipse(cx, cy, rx, ry, amp=1.5, n=48):
    pts = [(cx + rx * math.cos(2 * math.pi * k / n) + random.uniform(-amp, amp),
            cy + ry * math.sin(2 * math.pi * k / n) + random.uniform(-amp, amp)) for k in range(n)]
    return lambda d: d.polygon(pts, fill=255)


yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)

# ---- wall: warm plaster, lit from the window on the left, darker high corners
light = 1.0 + 0.10 * np.exp(-(((xx - 200) / 330) ** 2 + ((yy - 520) / 420) ** 2)) - 0.16 * (yy < 300) * (1 - yy / 300) ** 2
light -= 0.10 * (xx / W) ** 3
paint(np.ones((H, W), np.float32), "#efd3a0", var=0.06, edge=0, seed=1, grad=light + 0.05 * BLOT)
# soft sunbeam from the window
beam = mask_of(lambda d: d.polygon([(300, 240), (330, 520), (640, 980), (470, 980)], fill=255))
beam = np.asarray(Image.fromarray((beam * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(40)), np.float32) / 255
canvas *= 1 + 0.10 * beam[..., None]

# ---- timber frame: top beam, two posts, wainscot
paint(mask_of(rect(-10, 40, W + 10, 104, 2.5)), "#8a5530", seed=2, edge=0.3)
paint(mask_of(rect(-10, 98, W + 10, 112, 1.5)), "#5e3519", seed=3, edge=0.1)
for x in (18, 660):
    paint(mask_of(rect(x, 100, x + 46, 1000, 2.5)), "#8a5530", seed=4 + x, edge=0.3)
    paint(mask_of(rect(x + 34, 100, x + 46, 1000, 1.5)), "#5e3519", seed=5 + x, edge=0.1)
paint(mask_of(rect(-10, 800, W + 10, 1000, 2.0)), "#a76a3b", seed=6, edge=0.25)
paint(mask_of(rect(-10, 796, W + 10, 812, 1.5)), "#6b3d1d", seed=7, edge=0.1)
for x in range(30, W, 120):
    paint(mask_of(rect(x + 8, 830, x + 104, 990, 2.0)), "#93592e", seed=8 + x, edge=0.35)

# ---- window (left): frame, sky, hills, a tree, muntins
paint(mask_of(rect(80, 176, 318, 540, 2.5)), "#7d4a27", seed=20, edge=0.3)
sky = 1.0 - 0.25 * np.clip((yy - 190) / 330, 0, 1)
paint(mask_of(rect(98, 192, 300, 522, 1.5)), "#7fb7e0", seed=21, edge=0.15, grad=sky + 0.0)
for cx, cy, rx, ry in ((150, 260, 40, 16), (250, 300, 34, 12)):
    paint(mask_of(ellipse(cx, cy, rx, ry, 2.5)), "#f4f1e6", seed=22 + cx, edge=0.05, var=0.03)
paint(mask_of(lambda d: d.polygon(wobble([(98, 440), (160, 400), (230, 420), (300, 395), (300, 522), (98, 522)], 3), fill=255)),
      "#7aa64e", seed=23, edge=0.2)
paint(mask_of(lambda d: d.polygon(wobble([(98, 480), (190, 452), (300, 470), (300, 522), (98, 522)], 3), fill=255)),
      "#5d8a3a", seed=24, edge=0.2)
paint(mask_of(rect(246, 420, 256, 470, 1.0)), "#6b4423", seed=25)
paint(mask_of(ellipse(251, 405, 30, 34, 3)), "#4f7d32", seed=26, edge=0.25)
paint(mask_of(rect(192, 192, 206, 522, 1.2)), "#7d4a27", seed=27, edge=0.2)
paint(mask_of(rect(98, 350, 300, 364, 1.2)), "#7d4a27", seed=28, edge=0.2)
paint(mask_of(rect(70, 530, 328, 556, 2.0)), "#8f5a31", seed=29, edge=0.3)        # sill
# curtain
paint(mask_of(lambda d: d.polygon(wobble([(72, 160), (130, 160), (118, 300), (96, 420), (70, 560), (60, 560)], 3), fill=255)),
      "#c9473b", seed=30, edge=0.3)

# ---- clock (no numbers, just dots)
paint(mask_of(ellipse(560, 175, 48, 48, 1.5)), "#7d4a27", seed=40, edge=0.3)
paint(mask_of(ellipse(560, 175, 38, 38, 1.2)), "#f3e7c8", seed=41, edge=0.15)
dots = Image.new("L", (W, H), 0)
dd = ImageDraw.Draw(dots)
for k in range(12):
    a = 2 * math.pi * k / 12
    dd.ellipse((560 + 30 * math.cos(a) - 2.5, 175 + 30 * math.sin(a) - 2.5, 560 + 30 * math.cos(a) + 2.5,
                175 + 30 * math.sin(a) + 2.5), fill=255)
dd.line((560, 175, 560, 152), fill=255, width=4)
dd.line((560, 175, 578, 182), fill=255, width=4)
paint(np.asarray(dots.filter(ImageFilter.GaussianBlur(0.6)), np.float32) / 255, "#3b2414", seed=42, edge=0)

# ---- shelves (right) with bolts of cloth and spools
for y in (330, 560):
    paint(mask_of(rect(450, y, 664, y + 18, 1.5)), "#8a5530", seed=50 + y, edge=0.3)
    paint(mask_of(rect(450, y + 16, 664, y + 24, 1.0)), "#5e3519", seed=51 + y, edge=0.1)
x = 462
for col, w, h in (("#c23b33", 40, 120), ("#e0b23c", 34, 96), ("#3c8f86", 44, 130), ("#7a4c9a", 36, 104),
                  ("#e9e2cf", 40, 112)):
    paint(mask_of(lambda d, x=x, w=w, h=h: d.rounded_rectangle((x, 330 - h, x + w, 332), 10, fill=255)), col,
          seed=60 + x, edge=0.35)
    stripe = mask_of(lambda d, x=x, w=w, h=h: d.rectangle((x + 4, 330 - h + 14, x + w - 4, 330 - h + 20), fill=255))
    paint(stripe, "#ffffff", seed=61 + x, edge=0, var=0.02)
    canvas *= 1 - 0.0 * stripe[..., None]
    x += w + 3
for k, (col, cx) in enumerate((("#c23b33", 480), ("#3b6fc2", 520), ("#e0b23c", 560), ("#4f9a4f", 600), ("#e9e2cf", 638))):
    paint(mask_of(rect(cx - 13, 520, cx + 13, 560, 1.0)), "#b98a5a", seed=70 + k, edge=0.2)
    paint(mask_of(rect(cx - 10, 526, cx + 10, 554, 1.0)), col, seed=71 + k, edge=0.25)
for k, col in enumerate(("#3c8f86", "#c9473b", "#e0b23c")):
    paint(mask_of(rect(470, 470 + k * 16, 545, 486 + k * 16, 1.5)), col, seed=80 + k, edge=0.3)

# ---- hanging scissors on a nail + a tape measure
sc = Image.new("L", (W, H), 0)
sd = ImageDraw.Draw(sc)
sd.ellipse((364, 196, 390, 222), outline=255, width=7)
sd.ellipse((394, 196, 420, 222), outline=255, width=7)
sd.polygon([(380, 220), (392, 216), (402, 320), (396, 322)], fill=255)
sd.polygon([(404, 220), (392, 216), (388, 320), (394, 322)], fill=255)
paint(np.asarray(sc.filter(ImageFilter.GaussianBlur(0.7)), np.float32) / 255, "#8d929c", seed=90, edge=0.3)
paint(mask_of(ellipse(392, 190, 5, 5, 0.3)), "#3b2414", seed=91, edge=0)
tm = Image.new("L", (W, H), 0)
td = ImageDraw.Draw(tm)
td.arc((360, 600, 440, 700), 200, 340, fill=255, width=10)
td.line((365, 640, 352, 760), fill=255, width=10)
td.line((436, 640, 446, 740), fill=255, width=10)
paint(np.asarray(tm.filter(ImageFilter.GaussianBlur(0.7)), np.float32) / 255, "#e6c542", seed=92, edge=0.25)
paint(mask_of(ellipse(400, 605, 5, 5, 0.3)), "#3b2414", seed=93, edge=0)

# ---- finishing: paper grain + soft vignette + slight warmth
canvas *= 1 + 0.035 * GRAIN[..., None]
vig = 1 - 0.28 * (((xx - W / 2) / (W * 0.75)) ** 2 + ((yy - H * 0.45) / (H * 0.7)) ** 2)
canvas *= vig[..., None]
img = Image.fromarray((np.clip(canvas, 0, 1) * 255).astype(np.uint8))
img.save("plate.png")
print("plate.png")
