"""Post for the comic-style test: fisheye, phone 'rule' notification card, white Persian captions.
    python3 post.py   -> out/toon_test.mp4
"""
import os, shutil, subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
FONT = os.path.join(HERE, "..", "fonts", "Vazirmatn-FD-ExtraBold.ttf")
FPS, W, H = 24, 1080, 1920
TMP, OUT = os.path.join(HERE, "post_tmp"), os.path.join(HERE, "out")

SUBS = [  # (start, end, speaker, text)
    (0.4, 1.9, "آرین", "صداشو شنیدی...؟"),
    (3.4, 4.5, "من", "شماره ناشناس..."),
    (5.3, 6.6, "آرین", "نه... نه... نه!"),
    (7.0, 7.9, "آرین", "نگاش نکن!"),
    (8.2, 9.4, "آرین", "بیا! از این طرف... سینه‌خیز!"),
]
NOTE = (2.3, 4.6, "قانون ۱", "از زیر میز بیرون نیا.")   # the phone notification


def font(s):
    return ImageFont.truetype(FONT, s, layout_engine=ImageFont.Layout.RAQM)


def rtl(d, xy, s, size, fill, anchor="mm", stroke=0, sfill=(0, 0, 0)):
    d.text(xy, s, font=font(size), fill=fill, anchor=anchor, direction="rtl", language="fa",
           stroke_width=stroke, stroke_fill=sfill)


def ease(x):
    x = min(1.0, max(0.0, x))
    return 1 - (1 - x) ** 3


def card():
    c = Image.new("RGBA", (980, 250), (0, 0, 0, 0))
    sh = Image.new("RGBA", c.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((10, 14, 970, 244), 44, fill=(0, 0, 0, 110))
    c.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10)))
    d = ImageDraw.Draw(c)
    d.rounded_rectangle((0, 0, 960, 230), 44, fill=(250, 250, 252, 245))
    d.rounded_rectangle((870, 26, 930, 86), 14, fill=(225, 30, 40))
    rtl(d, (900, 57), "!", 44, (255, 255, 255))
    rtl(d, (850, 57), "ناشناس", 40, (40, 40, 45), anchor="rm")
    d.text((40, 57), "12:14", font=font(36), fill=(120, 120, 128), anchor="lm")
    rtl(d, (920, 128), NOTE[2], 58, (215, 20, 30), anchor="rm")
    rtl(d, (920, 192), NOTE[3], 48, (20, 20, 22), anchor="rm")
    return c


CARD = card()


def overlay(img, t):
    img = img.convert("RGBA")
    a, b = NOTE[0], NOTE[1]
    if a <= t <= b + 0.4:
        k = ease((t - a) / 0.35) * (1 - ease((t - b) / 0.35))
        y = int(-260 + (110 + 260) * k)
        if t - a < 0.12:  # red flash on arrival
            img.alpha_composite(Image.new("RGBA", img.size, (220, 0, 0, 60)))
    d = ImageDraw.Draw(img)
    for s, e, who, text in SUBS:
        if s <= t <= e:
            k = ease((t - s) / 0.12)
            rtl(d, (W // 2, 1560), who, 44, (255, 220, 90), stroke=6)
            rtl(d, (W // 2, 1650), text, int(80 * (0.9 + 0.1 * k)), (255, 255, 255), stroke=10)
    return img.convert("RGB")


def main():
    if os.path.exists(TMP):
        shutil.rmtree(TMP)
    os.makedirs(TMP)
    os.makedirs(OUT, exist_ok=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-i", os.path.join(HERE, "frames", "f_%04d.png"),
                    "-vf", f"scale={W}:{H}:flags=lanczos,lenscorrection=k1=0.25:k2=0.06:i=bilinear,"
                           f"scale={int(W * 1.22)}:{int(H * 1.22)},crop={W}:{H}",
                    os.path.join(TMP, "u_%04d.png")], check=True)
    names = sorted(n for n in os.listdir(TMP) if n.startswith("u_"))
    for i, n in enumerate(names):
        overlay(Image.open(os.path.join(TMP, n)), i / FPS).save(os.path.join(TMP, f"c_{i:04d}.png"))
    out = os.path.join(OUT, "toon_test.mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-i", os.path.join(TMP, "c_%04d.png"),
                    "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", "-movflags", "+faststart", out], check=True)
    print(out)


if __name__ == "__main__":
    main()
