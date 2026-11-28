"""Screens of «قانون‌ها ۲»: textures/doorcam.png (Nina's laptop: the front-door camera at night)."""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__))
FONT = os.path.join(HERE, "..", "fonts", "Vazirmatn-FD-ExtraBold.ttf")
W, H = 960, 600


def doorcam():
    im = Image.new("RGB", (W, H), (120, 128, 118))
    d = ImageDraw.Draw(im)
    d.rectangle((0, 380, W, H), fill=(150, 156, 146))                    # street (night-vision grey-green)
    d.polygon([(0, 380), (W, 380), (W, 300), (0, 330)], fill=(105, 112, 102))
    for x, w, h in ((40, 180, 200), (260, 150, 250), (650, 240, 220)):  # houses across the street
        d.rectangle((x, 380 - h, x + w, 380), fill=(80, 86, 78))
    d.rounded_rectangle((330, 300, 640, 400), 30, fill=(40, 42, 40))     # a plain dark car (no markings)
    d.rectangle((420, 285, 470, 300), fill=(230, 40, 40))                # a light on its roof
    d.rectangle((470, 285, 520, 300), fill=(40, 80, 240))
    glow = Image.new("RGB", (W, H), (0, 0, 0))
    ImageDraw.Draw(glow).ellipse((330, 200, 640, 380), fill=(255, 120, 160))
    im = Image.blend(im, Image.composite(glow, im, glow.convert("L")), 0.4)
    d = ImageDraw.Draw(im)
    for cx, sc_ in ((260, 1.0), (720, 0.9)):                              # two masked men, one with a megaphone
        s = int(150 * sc_)
        d.ellipse((cx - 32, 230 - s // 2, cx + 32, 300 - s // 2), fill=(8, 8, 10))
        d.rounded_rectangle((cx - 60, 300 - s // 2 - 6, cx + 60, 560), 30, fill=(10, 10, 12))
        for ex in (-14, 14):
            d.ellipse((cx + ex - 7, 255 - s // 2, cx + ex + 7, 265 - s // 2), fill=(230, 225, 215))
    d.polygon([(320, 300), (380, 280), (380, 330)], fill=(60, 60, 64))  # megaphone
    im = im.filter(ImageFilter.GaussianBlur(1.2))
    d = ImageDraw.Draw(im)
    for y in range(0, H, 4):                                             # scan lines
        d.line((0, y, W, y), fill=(0, 0, 0), width=1)
    f = ImageFont.truetype(FONT, 34, layout_engine=ImageFont.Layout.RAQM)
    d.text((W - 30, 30), "دوربین در ورودی", font=f, fill=(220, 220, 220), anchor="ra", direction="rtl", language="fa")
    d.ellipse((30, 34, 54, 58), fill=(230, 30, 30))
    d.text((70, 30), "REC 02:13", font=f, fill=(220, 220, 220))
    im.save(os.path.join(HERE, "textures", "doorcam.png"))


if __name__ == "__main__":
    doorcam()
