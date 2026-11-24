"""Phone lock screen with the rule notification -> textures/phone_rule.png (portrait 600x1200)."""
import os
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__))
F = os.path.join(HERE, "..", "fonts", "Vazirmatn-FD-ExtraBold.ttf")
W, H = 600, 1200


def f(s):
    return ImageFont.truetype(F, s, layout_engine=ImageFont.Layout.RAQM)


def rtl(d, xy, s, size, fill, anchor="mm"):
    d.text(xy, s, font=f(size), fill=fill, anchor=anchor, direction="rtl", language="fa")


img = Image.new("RGB", (W, H))
d = ImageDraw.Draw(img)
for y in range(H):  # dark blue wallpaper
    k = y / H
    d.line((0, y, W, y), fill=(int(20 + 30 * k), int(30 + 25 * k), int(70 + 40 * k)))
d.text((W // 2, 120), "12:14", font=f(96), fill=(240, 240, 245), anchor="mm")
d.rounded_rectangle((18, 250, W - 18, 820), 48, fill=(250, 250, 252))
d.rounded_rectangle((W - 120, 285, W - 45, 360), 18, fill=(225, 30, 40))
rtl(d, (W - 82, 322), "!", 56, (255, 255, 255))
rtl(d, (W - 140, 322), "ناشناس", 52, (60, 60, 66), anchor="rm")
rtl(d, (W // 2, 500), "قانون ۱", 130, (215, 20, 30))
rtl(d, (W // 2, 680), "از زیر میز", 92, (20, 20, 22))
rtl(d, (W // 2, 775), "بیرون نیا.", 80, (20, 20, 22))
os.makedirs(os.path.join(HERE, "textures"), exist_ok=True)
img.save(os.path.join(HERE, "textures", "phone_rule.png"))
print("ok")
