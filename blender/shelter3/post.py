"""
Post-processing for «پناهگاه ۳ — اتوبوس نجات» (16:9): frames rendered on twos at 960x540 -> 24 fps 1920x1080,
the opening title on black, Persian captions (name pill + line), episode badge, the final question card.

    python3 post.py     # frames/ -> out/shelter3_full.mp4 (+ out/shelter3_sfx.mp4 with effects)
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
W, H = 1920, 1080

sys.path.insert(0, HERE)
from captions import CAPTIONS, CARD_SECONDS, END, NARRATION, SPEAKERS, TITLE  # noqa: E402

LAST = int(END * FPS)


def font(size):
    return ImageFont.truetype(FONT, size, layout_engine=ImageFont.Layout.RAQM)


def draw_text(d, xy, text, size, fill=(255, 255, 255), stroke=7, max_w=W - 260):
    while size > 26:
        l, t, r, b = d.multiline_textbbox(xy, text, font=font(size), anchor="mm", align="center", direction="rtl",
                                          language="fa", stroke_width=stroke, spacing=14)
        if r - l <= max_w:
            break
        size -= 3
    d.multiline_text(xy, text, font=font(size), fill=fill, anchor="mm", align="center", direction="rtl",
                     language="fa", stroke_width=stroke, stroke_fill=(12, 12, 12), spacing=14)


def pill(d, cx, cy, text, color, size=36):
    f = font(size)
    l, t, r, b = d.textbbox((cx, cy), text, font=f, anchor="mm", direction="rtl", language="fa")
    px, py = 24, 10
    d.rounded_rectangle((l - px, t - py, r + px, b + py), radius=(b - t) // 2 + py, fill=color, outline=(12, 12, 12),
                        width=4)
    d.text((cx, cy), text, font=f, fill=(255, 255, 255), anchor="mm", direction="rtl", language="fa")


def overlay(img, t):
    d = ImageDraw.Draw(img)
    pill(d, W - 150, 70, "پناهگاه ۳", (60, 60, 70), 38)
    current = [c for c in CAPTIONS if c[0] <= t <= c[1]]
    for start, end, who, text in current[-1:]:
        k = min(1.0, (t - start) / 0.15)
        lines = text.count("\n")
        if start in NARRATION:
            draw_text(d, (W // 2, H - 150 - 28 * lines), text, int(62 * (0.88 + 0.12 * k)), stroke=8)
        else:
            name, col = SPEAKERS[who]
            y = H - 140 - 26 * lines
            pill(d, W // 2, y - 70 - 34 * lines, name, col)
            draw_text(d, (W // 2, y), text, int(60 * (0.88 + 0.12 * k)))
    if t < TITLE:     # «یک هفته بعد...» on black, then the shelter fades in
        black = Image.new("RGB", img.size, (0, 0, 0))
        k = min(1.0, max(0.0, (t - (TITLE - 0.7)) / 0.7))
        img = Image.blend(black, img, k)
        d2 = ImageDraw.Draw(img)
        a = min(1.0, t / 0.35) * (1 - k)
        if a > 0.02:
            col = tuple(int(c * a) for c in (255, 235, 150))
            draw_text(d2, (W // 2, H // 2), "یک هفته بعد...", int(110 * (0.92 + 0.08 * a)), fill=col, stroke=0)
    return img


def final_card(img, k):
    img = Image.blend(img, Image.new("RGB", img.size, (0, 0, 0)), 0.6 * k)
    if k < 0.05:
        return img
    d = ImageDraw.Draw(img)
    draw_text(d, (W // 2, 250), "اگه تو بودی...\nاز اتوبوس پیاده می‌شدی\nیا منتظر اون ماشین می‌موندی؟",
              int(70 * (0.8 + 0.2 * k)), stroke=10)
    for i, (label, col) in enumerate((("پیاده می‌شدم", (30, 110, 200)), ("منتظر می‌موندم", (200, 40, 45)))):
        y = 560 + i * 170
        d.rounded_rectangle((W // 2 - 520, y - 62, W // 2 + 520, y + 62), radius=50, fill=col, outline=(255, 255, 255),
                            width=7)
        d.text((W // 2 + 30, y), label, font=font(50), fill=(255, 255, 255), anchor="mm", direction="rtl",
               language="fa")
        d.ellipse((W // 2 - 495, y - 38, W // 2 - 419, y + 38), fill=(255, 255, 255))
        d.text((W // 2 - 457, y), "AB"[i], font=font(46), fill=col, anchor="mm")
    draw_text(d, (W // 2, 930), "جوابت رو کامنت کن", 56, fill=(255, 230, 120), stroke=8)
    return img


def main():
    assert features.check("raqm"), "Pillow needs raqm for Persian text"
    shutil.rmtree(TMP, ignore_errors=True)
    os.makedirs(TMP)
    os.makedirs(OUT, exist_ok=True)
    seq = os.path.join(TMP, "seq")
    os.makedirs(seq)
    for i in range(1, LAST + 1):          # rendered on twos (1, 3, 5 ...): each drawing held for two frames
        os.symlink(os.path.join(FRAMES, f"f_{i - (1 - i % 2):04d}.png"), os.path.join(seq, f"s_{i:04d}.png"))
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-framerate", str(FPS), "-i", os.path.join(seq, "s_%04d.png"),
                    "-vf", f"scale={W}:{H}:flags=lanczos", os.path.join(TMP, "d_%05d.png")], check=True)
    names = sorted(n for n in os.listdir(TMP) if n.startswith("d_"))
    i = 0
    for n in names:
        overlay(Image.open(os.path.join(TMP, n)).convert("RGB"), i / FPS).save(os.path.join(TMP, f"c_{i:05d}.png"))
        i += 1
    last = Image.open(os.path.join(TMP, names[-1])).convert("RGB")
    for j in range(CARD_SECONDS * FPS):
        final_card(last.copy(), min(1.0, j / 12)).save(os.path.join(TMP, f"c_{i:05d}.png"))
        i += 1
    out = os.path.join(OUT, "shelter3_full.mp4")
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-framerate", str(FPS), "-i", os.path.join(TMP, "c_%05d.png"),
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "19", "-movflags", "+faststart", out], check=True)
    print(out)
    sfx = os.path.join(OUT, "sfx.wav")
    if os.path.exists(sfx):
        out_fx = os.path.join(OUT, "shelter3_sfx.mp4")
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", out, "-i", sfx, "-map", "0:v", "-map", "1:a",
                        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", out_fx], check=True)
        print(out_fx)


if __name__ == "__main__":
    main()
