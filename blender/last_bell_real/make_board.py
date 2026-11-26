"""Chalkboard for the realistic «زنگ آخر»: an English lesson written in chalk (textures/board_en.png)."""
import os, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 2160, 870
random.seed(3)
img = Image.new("RGB", (W, H), (32, 58, 44))
px = img.load()
for _ in range(60000):  # board texture: faint chalk dust
    x, y = random.randrange(W), random.randrange(H)
    c = px[x, y]
    k = random.randint(-6, 10)
    px[x, y] = (c[0] + k, c[1] + k, c[2] + k)
for _ in range(14):  # old erased smears
    x, y = random.randrange(W), random.randrange(H)
    ImageDraw.Draw(img).ellipse((x, y, x + random.randint(200, 600), y + random.randint(40, 120)), fill=(44, 70, 56))
img = img.filter(ImageFilter.GaussianBlur(6))
text = Image.new("L", (W, H), 0)
d = ImageDraw.Draw(text)
F = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
lines = [
    (FB, 78, (120, 60), "English  -  Lesson 42"),
    (F, 52, (1500, 75), "page 42"),
    (FB, 64, (120, 200), "Present Simple"),
    (F, 58, (160, 310), "I  go  to school every day."),
    (F, 58, (160, 400), "She  goes  to school every day."),
    (F, 58, (160, 490), "Do you like English?  -  Yes, I do."),
    (F, 58, (160, 580), "He doesn't play football on Monday."),
    (F, 50, (120, 720), "Homework:  page 43,  exercises 1 - 3"),
]
for f, size, (x, y), s in lines:
    font = ImageFont.truetype(f, size)
    cx = x
    for ch in s:  # hand-written wobble
        d.text((cx, y + random.uniform(-3, 3)), ch, font=font, fill=random.randint(200, 245))
        cx += font.getlength(ch) * random.uniform(0.98, 1.04)
d.line((120, 160, 1150, 168), fill=210, width=5)
d.line((150, 285, 760, 290), fill=190, width=4)
noise = Image.effect_noise((W, H), 90).point(lambda v: 255 if v > 95 else 120)
text = Image.composite(text, Image.new("L", (W, H), 0), noise).filter(ImageFilter.GaussianBlur(1.1))
img = Image.composite(Image.new("RGB", (W, H), (235, 238, 232)), img, text)
img.save(os.path.join(HERE, "textures", "board_en.png"))
print("ok")
