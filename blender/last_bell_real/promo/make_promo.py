"""Teaser images for the new series: promo/teaser_16x9.png (YouTube post) and promo/teaser_9x16.png (story)."""
import os, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
HERE = os.path.dirname(os.path.abspath(__file__))
FONT = os.path.join(HERE, "..", "..", "fonts", "Vazirmatn-FD-ExtraBold.ttf")
src = Image.open(sys.argv[1]).convert("RGB")          # the soldier (1080x1920 still)
door = Image.open(sys.argv[2]).convert("RGB")         # zombie behind the door glass


def f(size):
    return ImageFont.truetype(FONT, size, layout_engine=ImageFont.Layout.RAQM)


def text(d, xy, s, size, fill, anchor="mm", stroke=8):
    d.text(xy, s, font=f(size), fill=fill, anchor=anchor, direction="rtl", language="fa",
           stroke_width=stroke, stroke_fill=(10, 6, 6))


def grade(im):
    im = ImageEnhance.Color(im).enhance(0.75)
    im = ImageEnhance.Contrast(im).enhance(1.15)
    red = Image.new("RGB", im.size, (60, 0, 0))
    return Image.blend(im, red, 0.18)


def vignette(im, strength=0.85):
    w, h = im.size
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).ellipse((-w * 0.25, -h * 0.25, w * 1.25, h * 1.25), fill=255)
    m = m.filter(ImageFilter.GaussianBlur(w // 6))
    dark = Image.new("RGB", (w, h), (0, 0, 0))
    return Image.composite(im, Image.blend(im, dark, strength), m)


# ---- 16:9
crop = src.crop((0, 600, 1080, 1208)).resize((1920, 1080), Image.LANCZOS)
im = vignette(grade(crop))
grad = Image.new("L", (1920, 1080))
gd = ImageDraw.Draw(grad)
for x in range(1920):
    gd.line((x, 0, x, 1080), fill=int(235 * max(0, 1 - x / 1100)))
im = Image.composite(Image.new("RGB", im.size, (8, 4, 4)), im, grad)
inset = grade(door.crop((180, 560, 780, 1160))).resize((360, 360), Image.LANCZOS)
d = ImageDraw.Draw(im)
d.rectangle((88, 618, 460, 990), outline=(170, 20, 20), width=6)
im.paste(inset, (94, 624))
text(d, (560, 300), "زنگ آخر", 230, (235, 30, 30), stroke=10)
text(d, (560, 470), "سریال جدید", 96, (245, 245, 240))
text(d, (760, 800), "...به‌زودی", 110, (255, 215, 80))
im.save(os.path.join(HERE, "teaser_16x9.png"))

# ---- 9:16
v = vignette(grade(src), 0.8)
grad = Image.new("L", (1080, 1920))
gd = ImageDraw.Draw(grad)
for y in range(1920):
    k = max(0, 1 - y / 700) * 230 + max(0, (y - 1350) / 570) * 240
    gd.line((0, y, 1080, y), fill=int(min(255, k)))
v = Image.composite(Image.new("RGB", v.size, (8, 4, 4)), v, grad)
d = ImageDraw.Draw(v)
text(d, (540, 250), "زنگ آخر", 220, (235, 30, 30), stroke=10)
text(d, (540, 420), "سریال جدید", 92, (245, 245, 240))
text(d, (540, 1690), "...به‌زودی", 120, (255, 215, 80))
v.save(os.path.join(HERE, "teaser_9x16.png"))
print("ok")
