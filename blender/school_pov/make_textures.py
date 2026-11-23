"""Phone + TV textures (Persian UI) for «زنگ آخر». Run: python3 make_textures.py"""
import math
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


def status(d, bars, dark=False):
    c = (30, 30, 30) if dark else (255, 255, 255)
    d.text((40, 26), "۰۹:۱۴", font=f(24), fill=c, anchor="lm")
    for i in range(4):
        h = 8 + i * 6
        x = W - 120 + i * 12
        d.rectangle((x, 36 - h, x + 8, 36), fill=c if i < bars else (150, 150, 150))
    if bars == 0:
        d.line((W - 125, 10, W - 75, 40), fill=(230, 60, 60), width=4)


def voice_msg():
    im = Image.new("RGB", (W, H), (235, 228, 215))
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, W, 110), fill=(40, 90, 160))
    status(d, 1)
    text(d, (W / 2 + 20, 75), "مامان", 34)
    d.ellipse((24, 52, 70, 98), fill=(240, 170, 120))
    # the voice note
    d.rounded_rectangle((60, 170, W - 30, 260), radius=26, fill=(255, 255, 255))
    d.ellipse((W - 95, 190, W - 45, 240), fill=(40, 90, 160))
    d.polygon([(W - 78, 202), (W - 78, 228), (W - 58, 215)], fill=(255, 255, 255))
    for i in range(18):
        h = 8 + 26 * abs(math.sin(i * 1.3))
        x = W - 120 - i * 11
        d.rounded_rectangle((x, 215 - h / 2, x + 6, 215 + h / 2), radius=3, fill=(70, 120, 190))
    d.text((78, 248), "۰:۰۸", font=f(18), fill=(120, 120, 120), anchor="lm")
    # its text, so the viewer can read what mum said
    d.rounded_rectangle((40, 290, W - 30, 450), radius=26, fill=(255, 255, 255))
    d.multiline_text((W / 2 + 5, 370), "داره اتفاقایی میفته...\nمواظب خودت باش!", font=f(28), fill=(30, 30, 30),
                     anchor="mm", align="center", direction="rtl", language="fa", spacing=14)
    text(d, (W / 2, 520), "پیام صوتی", 26, (40, 90, 160))
    return im


def call_failed():
    im = Image.new("RGB", (W, H), (35, 35, 45))
    d = ImageDraw.Draw(im)
    status(d, 0)
    d.ellipse((W / 2 - 80, 140, W / 2 + 80, 300), fill=(240, 170, 120), outline=(255, 255, 255), width=4)
    text(d, (W / 2, 220), "م", 90)
    text(d, (W / 2, 350), "مامان", 42)
    text(d, (W / 2, 410), "تماس ناموفق", 32, (255, 110, 110))
    d.ellipse((W / 2 - 45, 560, W / 2 + 45, 650), fill=(230, 60, 60))
    d.rounded_rectangle((W / 2 - 25, 598, W / 2 + 25, 612), radius=6, fill=(255, 255, 255))
    return im


def tv_banner():
    im = Image.new("RGB", (800, 120), (200, 30, 35))
    d = ImageDraw.Draw(im)
    d.rectangle((560, 0, 800, 120), fill=(250, 220, 40))
    d.text((680, 60), "فوری", font=f(64), fill=(160, 20, 25), anchor="mm", direction="rtl", language="fa")
    d.text((280, 60), "اخبار", font=f(56), fill=(255, 255, 255), anchor="mm", direction="rtl", language="fa")
    return im


def chalkboard():
    im = Image.new("RGB", (1000, 400), (35, 75, 55))
    d = ImageDraw.Draw(im)
    chalk = (235, 235, 225)
    d.text((820, 70), "درس ۷", font=f(54), fill=chalk, anchor="mm", direction="rtl", language="fa")
    d.text((500, 200), "۲x + ۵ = ۱۷", font=f(70), fill=chalk, anchor="mm")
    d.text((500, 310), "x = ?", font=f(60), fill=(250, 220, 120), anchor="mm")
    return im


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    voice_msg().save(os.path.join(OUT, "phone_voice.png"))
    call_failed().save(os.path.join(OUT, "phone_failed.png"))
    tv_banner().save(os.path.join(OUT, "tv_banner.png"))
    chalkboard().save(os.path.join(OUT, "chalkboard.png"))
    print("ok")
