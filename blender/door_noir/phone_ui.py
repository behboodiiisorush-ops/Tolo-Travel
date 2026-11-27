"""Phone screens for «در رو باز نکن» (PIL + raqm, Vazirmatn) -> textures/phone_*.png (360x780).
msg: a voice message from «من» at 23:58 · incoming/call: mom calling · record: I record a voice message to «من»
· sent: delivered «دیروز ۲۳:۵۸» (the loop: it is the message I got at the start)."""
import os, math, random
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__))
FONT = os.path.join(HERE, "..", "fonts", "Vazirmatn-FD-ExtraBold.ttf")
W, H = 360, 780
RED, GREEN = (235, 30, 40), (60, 200, 90)


def F(s):
    return ImageFont.truetype(FONT, s, layout_engine=ImageFont.Layout.RAQM)


def txt(d, xy, s, size, fill=(255, 255, 255), anchor="mm"):
    d.text(xy, s, font=F(size), fill=fill, anchor=anchor, direction="rtl", language="fa")


def base(clock):
    im = Image.new("RGB", (W, H), (14, 14, 18))
    d = ImageDraw.Draw(im)
    txt(d, (W // 2, 26), clock, 22, (200, 200, 205))
    return im, d


def wave(d, x0, y, w, n=26, seed=3, played=1.0, col=(255, 255, 255)):
    r = random.Random(seed)
    for i in range(n):
        h = 6 + 26 * abs(math.sin(i * 0.7 + r.random())) * r.uniform(0.4, 1.0)
        x = x0 + i * w / n
        c = col if i / n <= played else (110, 110, 120)
        d.rounded_rectangle((x, y - h / 2, x + w / n * 0.55, y + h / 2), 2, fill=c)


def header(d, name):
    d.rectangle((0, 46, W, 110), fill=(28, 28, 34))
    d.ellipse((W - 70, 56, W - 24, 102), fill=(70, 70, 80))
    txt(d, (W - 47, 79), name[0], 24)
    txt(d, (W - 90, 79), name, 26, anchor="rm")


def bubble(d, y, played, label, seed=3):
    d.rounded_rectangle((40, y, W - 30, y + 92), 22, fill=(45, 45, 55))
    d.polygon([(W - 60, y + 22), (W - 40, y + 46), (W - 60, y + 70)], fill=(255, 255, 255))   # play
    wave(d, 62, y + 46, 220, played=played, seed=seed)
    txt(d, (70, y + 78), label, 15, (170, 170, 180), anchor="lm")


def save(im, name):
    im.save(os.path.join(HERE, "textures", f"phone_{name}.png"))


im, d = base("۲۳:۵۸")
header(d, "من")
txt(d, (W // 2, 160), "امروز", 16, (150, 150, 160))
bubble(d, 330, 0.55, "۰:۰۳  ·  ۲۳:۵۸")
save(im, "msg")

for name, sub, btns in (("incoming", "تماس ورودی...", True), ("call", "۰۰:۰۴", False), ("ended", "تماس قطع شد", None)):
    im, d = base("۰۰:۰۲")
    d.ellipse((W // 2 - 70, 150, W // 2 + 70, 290), fill=(70, 70, 80))
    txt(d, (W // 2, 218), "م", 70)
    txt(d, (W // 2, 350), "مامان", 44)
    txt(d, (W // 2, 400), sub, 22, (190, 190, 200))
    if btns:
        d.ellipse((50, 600, 130, 680), fill=RED)
        d.ellipse((W - 130, 600, W - 50, 680), fill=GREEN)
    elif btns is False:
        d.ellipse((W // 2 - 40, 600, W // 2 + 40, 680), fill=RED)
        txt(d, (W // 2, 520), "بلندگو", 18, (190, 190, 200))
    save(im, name)

im, d = base("۰۰:۱۴")
header(d, "من")
wave(d, 70, 170, 220, seed=3)
txt(d, (W // 2, 235), "در حال ضبط...  ۰:۰۲", 22, (230, 230, 235))
d.ellipse((W // 2 - 38, 268, W // 2 + 38, 344), fill=RED)
save(im, "record")

im, d = base("۰۰:۱۴")
header(d, "من")
bubble(d, 130, 0.0, "ارسال شد", seed=3)
txt(d, (W // 2, 270), "تحویل: دیروز ۲۳:۵۸", 26, RED)
save(im, "sent")
print("ok")
