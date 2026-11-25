"""The phone's emergency-alert screen for «پناهگاه ۱». Run with: python3 make_textures.py"""

import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONT = os.path.join(HERE, "..", "fonts", "Vazirmatn-FD-ExtraBold.ttf")
OUT = os.path.join(HERE, "textures")
W, H = 360, 720


def f(size):
    return ImageFont.truetype(FONT, size, layout_engine=ImageFont.Layout.RAQM)


def text(d, xy, s, size, fill=(255, 255, 255)):
    d.multiline_text(xy, s, font=f(size), fill=fill, anchor="mm", align="center", direction="rtl", language="fa",
                     spacing=10)


def alert():
    im = Image.new("RGB", (W, H), (20, 10, 12))
    d = ImageDraw.Draw(im)
    for y in range(H):
        c = int(40 + 50 * (1 - y / H))
        d.line((0, y, W, y), fill=(c + 30, c // 5, c // 5))
    d.text((40, 26), "۲۳:۴۱", font=f(24), fill=(255, 255, 255), anchor="lm")
    d.rounded_rectangle((20, 80, W - 20, 470), radius=28, fill=(235, 235, 235))
    d.rounded_rectangle((20, 80, W - 20, 150), radius=28, fill=(200, 30, 30))
    d.rectangle((20, 120, W - 20, 150), fill=(200, 30, 30))
    text(d, (W / 2, 115), "⚠ هشدار اضطراری", 30)
    text(d, (W / 2, 225), "حملهٔ هسته‌ای", 40, (180, 20, 20))
    text(d, (W / 2, 320), "فوراً به نزدیک‌ترین\nپناهگاه بروید", 30, (30, 30, 30))
    text(d, (W / 2, 420), "این یک آزمایش نیست", 24, (120, 120, 120))
    text(d, (W / 2, 560), "۰۹:۰۰", 90, (255, 60, 60))
    return im


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    alert().save(os.path.join(OUT, "phone_alert.png"))
    print("ok")
