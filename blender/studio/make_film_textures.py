"""Phone screens for the five rules + the laptop camera-feed screen -> textures/*.png"""
import os, random
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__))
FB = os.path.join(HERE, "..", "fonts", "Vazirmatn-FD-ExtraBold.ttf")
W, H = 600, 1200
OUT = os.path.join(HERE, "textures")
os.makedirs(OUT, exist_ok=True)


def f(s):
    return ImageFont.truetype(FB, s, layout_engine=ImageFont.Layout.RAQM)


def rtl(d, xy, s, size, fill, anchor="mm"):
    d.text(xy, s, font=f(size), fill=fill, anchor=anchor, direction="rtl", language="fa")


RULES = {1: ["جواب هیچ", "تماسی رو نده."], 2: ["به اسمت", "جواب نده."], 3: ["سینه‌خیز،", "تا اتاق‌خواب.", "الان."],
         4: ["کمد.", "بالا.", "دریچه."], 5: ["به نینا", "اعتماد نکن."]}
NUM = "۱۲۳۴۵"


def screen(n, sender, glitch=0):
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img)
    for y in range(H):
        k = y / H
        d.line((0, y, W, y), fill=(int(14 + 20 * k), int(18 + 18 * k), int(40 + 40 * k)))
    d.text((W // 2, 115), "23:4" + str(n + 1), font=f(100), fill=(235, 238, 245), anchor="mm")
    d.rounded_rectangle((20, 230, W - 20, 1000), 46, fill=(248, 248, 250))
    d.rounded_rectangle((W - 125, 268, W - 45, 348), 20, fill=(220, 28, 38))
    rtl(d, (W - 85, 306), "!", 58, (255, 255, 255))
    rtl(d, (W - 145, 308), sender, 50 if len(sender) < 10 else 40, (70, 70, 78), anchor="rm")
    rtl(d, (W // 2, 470), "قانون " + NUM[n - 1], 140, (210, 18, 28))
    ys = 640
    for line in RULES[n]:
        rtl(d, (W // 2, ys), line, 96 if len(line) < 9 else 80, (18, 18, 22))
        ys += 115
    if glitch:
        rnd = random.Random(glitch)
        for _ in range(14):
            y0 = rnd.randint(0, H - 60)
            h = rnd.randint(6, 50)
            dx = rnd.randint(-90, 90)
            band = img.crop((0, y0, W, y0 + h))
            img.paste(band, (dx, y0))
        px = img.load()
        for _ in range(9):
            y0 = rnd.randint(0, H - 30)
            col = rnd.choice([(255, 0, 60), (0, 255, 220), (255, 255, 255)])
            d.rectangle((0, y0, W, y0 + rnd.randint(2, 8)), fill=col)
        r, g, b = img.split()
        img = Image.merge("RGB", (r.transform(img.size, Image.AFFINE, (1, 0, 8, 0, 1, 0)), g,
                                  b.transform(img.size, Image.AFFINE, (1, 0, -8, 0, 1, 0))))
    return img


for n in range(1, 5):
    screen(n, "ناشناس").save(os.path.join(OUT, f"rule{n}.png"))
screen(5, "شماره‌ی خودم").save(os.path.join(OUT, "rule5.png"))
screen(5, "شماره‌ی خودم", glitch=3).save(os.path.join(OUT, "rule5_g1.png"))
screen(5, "شماره‌ی خودم", glitch=7).save(os.path.join(OUT, "rule5_g2.png"))

# laptop: four security-camera feeds of this house (greenish night vision)
LW, LH = 1200, 760
img = Image.new("RGB", (LW, LH), (8, 10, 10))
d = ImageDraw.Draw(img)
fe = ImageFont.truetype(FB, 30)
panels = [(10, 10, 595, 375), (605, 10, 1190, 375), (10, 385, 595, 750), (605, 385, 1190, 750)]
labels = ["CAM 1  KITCHEN", "CAM 2  HALL", "CAM 3  BEDROOM", "CAM 4  DOOR"]
rnd = random.Random(5)
for (x0, y0, x1, y1), lab in zip(panels, labels):
    for y in range(y0, y1):
        v = 40 + int(25 * ((y - y0) / (y1 - y0)))
        d.line((x0, y, x1, y), fill=(int(v * 0.55), v, int(v * 0.6)))
    w, h = x1 - x0, y1 - y0
    d.polygon([(x0, y1), (x0 + w * 0.25, y0 + h * 0.55), (x1 - w * 0.25, y0 + h * 0.55), (x1, y1)], fill=(52, 84, 58))
    if "KITCHEN" in lab:
        d.rectangle((x0 + w * 0.35, y0 + h * 0.6, x0 + w * 0.65, y0 + h * 0.68), fill=(30, 50, 34))
        for px in (0.38, 0.62):
            d.rectangle((x0 + w * px, y0 + h * 0.68, x0 + w * px + 6, y0 + h * 0.85), fill=(30, 50, 34))
        d.ellipse((x0 + w * 0.43, y0 + h * 0.72, x0 + w * 0.5, y0 + h * 0.8), fill=(150, 200, 150))
        d.ellipse((x0 + w * 0.52, y0 + h * 0.72, x0 + w * 0.59, y0 + h * 0.8), fill=(150, 200, 150))
    else:
        cx = x0 + w * (0.4 + 0.2 * rnd.random())
        d.ellipse((cx - 16, y0 + h * 0.38, cx + 16, y0 + h * 0.48), fill=(18, 26, 20))
        d.rectangle((cx - 24, y0 + h * 0.48, cx + 24, y0 + h * 0.78), fill=(18, 26, 20))
        d.rectangle((cx - 22, y0 + h * 0.78, cx - 4, y0 + h * 0.95), fill=(18, 26, 20))
        d.rectangle((cx + 4, y0 + h * 0.78, cx + 22, y0 + h * 0.95), fill=(18, 26, 20))
    for _ in range(300):
        nx, ny = rnd.randint(x0, x1 - 2), rnd.randint(y0, y1 - 2)
        d.point((nx, ny), fill=(120, 160, 120))
    d.text((x0 + 14, y0 + 10), lab, font=fe, fill=(220, 240, 220))
    d.ellipse((x1 - 40, y0 + 16, x1 - 18, y0 + 38), fill=(230, 30, 30))
    d.text((x1 - 120, y1 - 44), "REC", font=fe, fill=(230, 60, 60))
img.save(os.path.join(OUT, "laptop_cams.png"))
print("ok")
