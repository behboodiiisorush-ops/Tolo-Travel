"""Phone screen textures (Persian UI) for «واگن آخر». Run with: python3 make_textures.py"""

import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONT = os.path.join(HERE, "..", "fonts", "Vazirmatn-FD-ExtraBold.ttf")
OUT = os.path.join(HERE, "textures")
W, H = 360, 720


def f(size):
    return ImageFont.truetype(FONT, size, layout_engine=ImageFont.Layout.RAQM)


def text(d, xy, s, size, fill=(255, 255, 255)):
    d.text(xy, s, font=f(size), fill=fill, anchor="mm", direction="rtl", language="fa")


def status_bar(d, signal):
    d.text((40, 26), "۱۹:۴۲", font=f(24), fill=(255, 255, 255), anchor="lm")
    for i in range(4):  # signal bars, all empty when there is no signal
        h = 8 + i * 6
        x = W - 120 + i * 12
        fill = (255, 255, 255) if i < signal else (90, 90, 100)
        d.rectangle((x, 36 - h, x + 8, 36), fill=fill)
    if signal == 0:
        d.line((W - 125, 10, W - 75, 40), fill=(240, 70, 70), width=4)
    d.rounded_rectangle((W - 60, 16, W - 22, 36), radius=4, outline=(255, 255, 255), width=2)
    d.rectangle((W - 56, 20, W - 44, 32), fill=(240, 70, 70))


def calling():
    im = Image.new("RGB", (W, H), (25, 40, 70))
    d = ImageDraw.Draw(im)
    for y in range(H):
        c = int(25 + 40 * y / H)
        d.line((0, y, W, y), fill=(c, c + 15, c + 45))
    status_bar(d, 0)
    d.ellipse((W / 2 - 80, 120, W / 2 + 80, 280), fill=(230, 120, 130), outline=(255, 255, 255), width=4)
    text(d, (W / 2, 200), "م", 90)
    text(d, (W / 2, 330), "مامان‌بزرگ ❤", 40)
    text(d, (W / 2, 380), "در حال تماس...", 28, (200, 210, 230))
    text(d, (W / 2, 425), "بدون آنتن", 26, (255, 120, 120))
    d.ellipse((W / 2 - 45, 560, W / 2 + 45, 650), fill=(230, 60, 60))
    d.rounded_rectangle((W / 2 - 25, 598, W / 2 + 25, 612), radius=6, fill=(255, 255, 255))
    return im


def voice():
    im = Image.new("RGB", (W, H), (235, 228, 215))
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, W, 110), fill=(30, 110, 90))
    status_bar(d, 1)
    text(d, (W / 2 + 20, 75), "مامان‌بزرگ ❤", 32)
    d.ellipse((24, 52, 70, 98), fill=(230, 120, 130))
    d.rounded_rectangle((60, 300, W - 30, 400), radius=26, fill=(255, 255, 255))
    d.polygon([(W - 60, 300), (W - 20, 300), (W - 40, 330)], fill=(255, 255, 255))
    d.ellipse((W - 95, 325, W - 45, 375), fill=(30, 110, 90))
    d.polygon([(W - 78, 337), (W - 78, 363), (W - 58, 350)], fill=(255, 255, 255))
    import math
    for i in range(18):
        h = 8 + 26 * abs(math.sin(i * 1.7))
        x = W - 120 - i * 11
        d.rounded_rectangle((x, 350 - h / 2, x + 6, 350 + h / 2), radius=3, fill=(60, 140, 120))
    text(d, (110, 420), "۰:۰۴", 22, (90, 90, 90))
    text(d, (W / 2, 470), "پیام صوتی جدید", 30, (30, 110, 90))
    return im


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    calling().save(os.path.join(OUT, "phone_call.png"))
    voice().save(os.path.join(OUT, "phone_voice.png"))
    print("ok")
