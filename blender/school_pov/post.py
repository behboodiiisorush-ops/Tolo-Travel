"""
Post-processing for «زنگ آخر»: fisheye look, upscale to 1080x1920,
Persian captions (Vazirmatn font), episode badge and fade-in.

    python3 post.py            # frames/ -> out/last_bell_full.mp4 (80 s with the question card)
Needs ffmpeg and Pillow with raqm (for right-to-left Persian shaping).
"""

import os
import shutil
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont, features

HERE = os.path.dirname(os.path.abspath(__file__))
FRAMES = os.path.join(HERE, "frames")
TMP = os.path.join(HERE, "post_tmp")
OUT = os.path.join(HERE, "out")
FONT = os.path.join(HERE, "..", "fonts", "Vazirmatn-FD-ExtraBold.ttf")
FPS = 24
W, H = 1080, 1920

sys.path.insert(0, HERE)
from captions import CAPTIONS  # noqa: E402

SPEAKERS = {  # caption key -> (name shown, colour)
    "Me": ("من", (40, 90, 190)),
    "Mom": ("مامان", (200, 90, 40)),
    "Mom voice": ("پیام صوتی مامان", (40, 90, 160)),
    "Anchor": ("اخبار", (200, 30, 35)),
    "Rezaei": ("آقای رضایی", (40, 80, 160)),
    "Kazemi": ("آقای کاظمی", (120, 75, 40)),
    "Arian": ("آرین", (235, 120, 20)),
    "Mahsa": ("مهسا", (40, 50, 110)),
    "Kian": ("کیان", (60, 150, 60)),
    "Principal": ("بلندگوی مدرسه", (90, 90, 100)),
    "Heli": ("بلندگوی هلیکوپتر", (70, 90, 60)),
    "Soldier": ("سرباز", (70, 90, 60)),
}
LAST = 1800          # last rendered frame (75 s)
CARD_SECONDS = 5


def font(size):
    return ImageFont.truetype(FONT, size, layout_engine=ImageFont.Layout.RAQM)


def draw_text(d, xy, text, size, fill=(255, 255, 255), stroke=9):
    f = font(size)
    d.multiline_text(xy, text, font=f, fill=fill, anchor="mm", align="center", direction="rtl",
                     language="fa", stroke_width=stroke, stroke_fill=(15, 15, 15), spacing=18)


def pill(d, cx, cy, text, color, size=44):
    f = font(size)
    l, t, r, b = d.textbbox((cx, cy), text, font=f, anchor="mm", direction="rtl", language="fa")
    pad_x, pad_y = 30, 14
    d.rounded_rectangle((l - pad_x, t - pad_y, r + pad_x, b + pad_y), radius=(b - t) // 2 + pad_y,
                        fill=color, outline=(15, 15, 15), width=5)
    d.text((cx, cy), text, font=f, fill=(255, 255, 255), anchor="mm", direction="rtl", language="fa")


def overlay(img, t):
    d = ImageDraw.Draw(img)
    # episode badge
    pill(d, W - 150, 150, "زنگ آخر", (40, 90, 190), 46)
    for start, end, who, text in CAPTIONS:
        if start <= t <= end:
            # quick pop-in
            k = min(1.0, (t - start) / 0.15)
            if who is None:
                draw_text(d, (W // 2, int(H * 0.42)), text, int(92 * (0.85 + 0.15 * k)), stroke=11)
            else:
                y = int(H * 0.6)
                name, col = SPEAKERS[who]
                pill(d, W // 2, y - 105, name, col)
                draw_text(d, (W // 2, y), text, int(84 * (0.85 + 0.15 * k)))
    # fade in from black
    if t < 3.0:
        black = Image.new("RGB", img.size, (0, 0, 0))
        img = Image.blend(black, img, max(0.0, (t - 2.4) / 0.6))
        if t < 2.4:  # the hook is said over black
            d = ImageDraw.Draw(img)
            for start, end, who, text in CAPTIONS:
                if who is None and start <= t <= end:
                    draw_text(d, (W // 2, int(H * 0.42)), text, 92, stroke=11)
    return img


def choice_card(img, k):
    """The closing question on black."""
    img = Image.new("RGB", img.size, (0, 0, 0))
    d = ImageDraw.Draw(img)
    if k < 0.05:
        return img
    draw_text(d, (W // 2, 760), "اگه جای من بودی...", int(96 * (0.8 + 0.2 * k)), stroke=10)
    draw_text(d, (W // 2, 930), "اون روز صبح\nمی‌رفتی مدرسه؟", int(104 * (0.8 + 0.2 * k)), fill=(255, 220, 90), stroke=10)
    draw_text(d, (W // 2, 1250), "جوابت رو کامنت کن", 68, fill=(255, 255, 255), stroke=8)
    d.polygon([(W // 2 - 45, 1330), (W // 2 + 45, 1330), (W // 2, 1400)], fill=(255, 220, 90), outline=(15, 15, 15))
    return img


def main():
    assert features.check("raqm"), "Pillow needs raqm for Persian text"
    shutil.rmtree(TMP, ignore_errors=True)
    os.makedirs(TMP)
    os.makedirs(OUT, exist_ok=True)
    # fisheye-style barrel distortion, then zoom in to hide the bent borders
    subprocess.run([
        "ffmpeg", "-loglevel", "error", "-y", "-framerate", str(FPS), "-start_number", "1",
        "-i", os.path.join(FRAMES, "f_%04d.png"), "-frames:v", str(LAST),
        "-vf", f"lenscorrection=k1=0.22:k2=0.05:i=bilinear,scale={int(W * 1.2)}:{int(H * 1.2)}:flags=lanczos,"
               f"crop={W}:{H}",
        os.path.join(TMP, "d_%04d.png")], check=True)
    names = sorted(n for n in os.listdir(TMP) if n.startswith("d_"))
    i = 0
    for n in names:
        img = overlay(Image.open(os.path.join(TMP, n)).convert("RGB"), i / FPS)
        img.save(os.path.join(TMP, f"c_{i:04d}.png"))
        i += 1
    last = Image.open(os.path.join(TMP, names[-1])).convert("RGB")
    for j in range(CARD_SECONDS * FPS):
        k = min(1.0, j / 12)
        choice_card(last.copy(), k).save(os.path.join(TMP, f"c_{i:04d}.png"))
        i += 1
    out = os.path.join(OUT, "last_bell_full.mp4")
    subprocess.run([
        "ffmpeg", "-loglevel", "error", "-y", "-framerate", str(FPS), "-i", os.path.join(TMP, "c_%04d.png"),
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", "-movflags", "+faststart", out], check=True)
    print(out)


if __name__ == "__main__":
    main()
