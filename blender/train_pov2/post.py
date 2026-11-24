"""
Post-processing for «واگن آخر ۲»: frames rendered on twos -> 24 fps, fisheye look, upscale to
1080x1920, narration captions, the viewer question (start, middle, final card), episode badge.

    python3 post.py     # frames/ -> out/last_wagon2_full.mp4 (+ out/last_wagon2_sfx.mp4 with effects)
Needs ffmpeg and Pillow with raqm (right-to-left Persian shaping).
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
from captions import CAPTIONS, CARD_SECONDS, END, QUESTION, QUESTION_AT, SUB_QUESTION  # noqa: E402

LAST = int(END * FPS)


def font(size):
    return ImageFont.truetype(FONT, size, layout_engine=ImageFont.Layout.RAQM)


def draw_text(d, xy, text, size, fill=(255, 255, 255), stroke=9):
    d.multiline_text(xy, text, font=font(size), fill=fill, anchor="mm", align="center", direction="rtl",
                     language="fa", stroke_width=stroke, stroke_fill=(15, 15, 15), spacing=18)


def pill(d, cx, cy, text, color, size=44):
    f = font(size)
    l, t, r, b = d.textbbox((cx, cy), text, font=f, anchor="mm", direction="rtl", language="fa")
    pad_x, pad_y = 30, 14
    d.rounded_rectangle((l - pad_x, t - pad_y, r + pad_x, b + pad_y), radius=(b - t) // 2 + pad_y,
                        fill=color, outline=(15, 15, 15), width=5)
    d.text((cx, cy), text, font=f, fill=(255, 255, 255), anchor="mm", direction="rtl", language="fa")


def question_banner(d, k):
    """The viewer question in a dark box near the top (k: 0..1 pop-in)."""
    f = font(int(46 * (0.85 + 0.15 * k)))
    cx, cy = W // 2, 330
    l, t, r, b = d.textbbox((cx, cy), QUESTION, font=f, anchor="mm", direction="rtl", language="fa")
    d.rounded_rectangle((l - 36, t - 26, r + 36, b + 26), radius=30, fill=(20, 18, 28), outline=(230, 60, 70),
                        width=6)
    d.text((cx, cy), QUESTION, font=f, fill=(255, 255, 255), anchor="mm", direction="rtl", language="fa")


def overlay(img, t):
    d = ImageDraw.Draw(img)
    pill(d, W - 180, 150, "واگن آخر ۲", (200, 40, 40), 46)
    for a, b in QUESTION_AT:
        if a <= t <= b:
            question_banner(d, min(1.0, (t - a) / 0.15))
    for start, end, who, text in CAPTIONS:
        if start <= t <= end:
            k = min(1.0, (t - start) / 0.15)
            draw_text(d, (W // 2, int(H * 0.7)), text, int(76 * (0.85 + 0.15 * k)), stroke=10)
    if t < 0.5:
        img = Image.blend(Image.new("RGB", img.size, (0, 0, 0)), img, t / 0.5)
    return img


def final_card(img, k):
    img = Image.blend(img, Image.new("RGB", img.size, (0, 0, 0)), 0.6 * k)
    if k < 0.05:
        return img
    d = ImageDraw.Draw(img)
    draw_text(d, (W // 2, 520), "اگه تو بودی\nاز قطار پیاده می‌شدی\nیا می‌موندی؟", int(96 * (0.8 + 0.2 * k)),
              stroke=12)
    for i, (label, col) in enumerate((("پیاده می‌شدم", (30, 110, 200)), ("می‌موندم", (200, 40, 45)))):
        y = 950 + i * 220
        d.rounded_rectangle((140, y - 80, W - 140, y + 80), radius=60, fill=col, outline=(255, 255, 255), width=8)
        d.text((W // 2, y), label, font=font(66), fill=(255, 255, 255), anchor="mm", direction="rtl", language="fa")
        d.ellipse((170, y - 45, 260, y + 45), fill=(255, 255, 255))
        d.text((215, y), "AB"[i], font=font(56), fill=col, anchor="mm")
    draw_text(d, (W // 2, 1440), SUB_QUESTION, 64, fill=(255, 230, 120), stroke=9)
    draw_text(d, (W // 2, 1560), "جوابت رو کامنت کن", 58, stroke=8)
    return img


def main():
    assert features.check("raqm"), "Pillow needs raqm for Persian text"
    shutil.rmtree(TMP, ignore_errors=True)
    os.makedirs(TMP)
    os.makedirs(OUT, exist_ok=True)
    # frames are rendered on twos (1, 3, 5, ...): hold each drawing for two frames
    seq = os.path.join(TMP, "seq")
    os.makedirs(seq)
    for i in range(1, LAST + 1):
        src = os.path.join(FRAMES, f"f_{i - (1 - i % 2):04d}.png")
        os.symlink(src, os.path.join(seq, f"s_{i:04d}.png"))
    subprocess.run([
        "ffmpeg", "-loglevel", "error", "-y", "-framerate", str(FPS), "-i", os.path.join(seq, "s_%04d.png"),
        "-vf", f"lenscorrection=k1=0.22:k2=0.05:i=bilinear,scale={int(W * 1.2)}:{int(H * 1.2)}:flags=lanczos,"
               f"crop={W}:{H}",
        os.path.join(TMP, "d_%04d.png")], check=True)
    names = sorted(n for n in os.listdir(TMP) if n.startswith("d_"))
    i = 0
    for n in names:
        overlay(Image.open(os.path.join(TMP, n)).convert("RGB"), i / FPS).save(os.path.join(TMP, f"c_{i:04d}.png"))
        i += 1
    last = Image.open(os.path.join(TMP, names[-1])).convert("RGB")
    for j in range(CARD_SECONDS * FPS):
        final_card(last.copy(), min(1.0, j / 12)).save(os.path.join(TMP, f"c_{i:04d}.png"))
        i += 1
    out = os.path.join(OUT, "last_wagon2_full.mp4")
    subprocess.run([
        "ffmpeg", "-loglevel", "error", "-y", "-framerate", str(FPS), "-i", os.path.join(TMP, "c_%04d.png"),
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", "-movflags", "+faststart", out], check=True)
    print(out)
    sfx = os.path.join(OUT, "sfx.wav")
    if os.path.exists(sfx):
        out_fx = os.path.join(OUT, "last_wagon2_sfx.mp4")
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", out, "-i", sfx, "-map", "0:v", "-map", "1:a",
                        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", out_fx], check=True)
        print(out_fx)


if __name__ == "__main__":
    main()
