"""
Post-processing for «واگن آخر»: fisheye look, upscale to 1080x1920,
Persian captions (Vazirmatn font), episode badge and fade-in.

    python3 post.py            # frames/ -> out/last_wagon_part1.mp4
Needs ffmpeg and Pillow with raqm (for right-to-left Persian shaping).
"""

import os
import shutil
import subprocess

from PIL import Image, ImageDraw, ImageFont, features

HERE = os.path.dirname(os.path.abspath(__file__))
FRAMES = os.path.join(HERE, "frames")
TMP = os.path.join(HERE, "post_tmp")
OUT = os.path.join(HERE, "out")
FONT = os.path.join(HERE, "..", "fonts", "Vazirmatn-FD-ExtraBold.ttf")
FPS = 24
W, H = 1080, 1920

SPEAKERS = {
    "من": (60, 160, 80),
    "مامان": (40, 90, 190),
    "لنا": (210, 50, 45),
    "عمو رحیم": (235, 120, 20),
}

# (start s, end s, speaker or None for the hook, text)
CAPTIONS = [
    (0.3, 3.0, None, "یک ثانیه...\nخانواده‌ام نصف شد."),
    (3.6, 5.0, "مامان", "بدوید! داره میره!"),
    (5.1, 6.4, "لنا", "دستمو ول نکنی!"),
    (6.5, 7.6, "من", "ول نمی‌کنم، بدو!"),
    (8.0, 9.4, "عمو رحیم", "بپر! دستتو بده!"),
    (11.2, 12.6, "من", "لنا! دستتو بده!"),
    (12.9, 14.0, "عمو رحیم", "آفرین! برید تو!"),
]


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
    pill(d, W - 150, 150, "قسمت ۱", (200, 40, 40), 46)
    for start, end, who, text in CAPTIONS:
        if start <= t <= end:
            # quick pop-in
            k = min(1.0, (t - start) / 0.15)
            if who is None:
                draw_text(d, (W // 2, int(H * 0.42)), text, int(92 * (0.85 + 0.15 * k)), stroke=11)
            else:
                y = int(H * 0.6)
                pill(d, W // 2, y - 105, who, SPEAKERS[who])
                draw_text(d, (W // 2, y), text, int(84 * (0.85 + 0.15 * k)))
    # fade in from black
    if t < 0.5:
        black = Image.new("RGB", img.size, (0, 0, 0))
        img = Image.blend(black, img, t / 0.5)
    return img


def main():
    assert features.check("raqm"), "Pillow needs raqm for Persian text"
    shutil.rmtree(TMP, ignore_errors=True)
    os.makedirs(TMP)
    os.makedirs(OUT, exist_ok=True)
    # fisheye-style barrel distortion, then zoom in to hide the bent borders
    subprocess.run([
        "ffmpeg", "-loglevel", "error", "-y", "-framerate", str(FPS), "-i", os.path.join(FRAMES, "f_%04d.png"),
        "-vf", f"lenscorrection=k1=0.22:k2=0.05:i=bilinear,scale={int(W * 1.2)}:{int(H * 1.2)}:flags=lanczos,"
               f"crop={W}:{H}",
        os.path.join(TMP, "d_%04d.png")], check=True)
    names = sorted(n for n in os.listdir(TMP) if n.startswith("d_"))
    for i, n in enumerate(names):
        t = i / FPS
        img = overlay(Image.open(os.path.join(TMP, n)).convert("RGB"), t)
        img.save(os.path.join(TMP, f"c_{i:04d}.png"))
    out = os.path.join(OUT, "last_wagon_part1.mp4")
    subprocess.run([
        "ffmpeg", "-loglevel", "error", "-y", "-framerate", str(FPS), "-i", os.path.join(TMP, "c_%04d.png"),
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "19", "-movflags", "+faststart", out], check=True)
    print(out)


if __name__ == "__main__":
    main()
