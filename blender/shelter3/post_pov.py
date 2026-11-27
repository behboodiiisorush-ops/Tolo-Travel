"""
Post-processing for «پناهگاه ۳» (vertical POV, the series' form): frames rendered on twos -> 24 fps, the
fisheye look of episodes 1-2, upscale to 1080x1920, the opening title, captions in the series style, the
channel branding on every frame (brand.overlay), the final question card with the credit.

    python3 post_pov.py   # frames/ + out/voice.wav, out/sfx.wav ->
                          #   out/shelter3_voice.mp4 (voices + effects, captions)
                          #   out/shelter3_sfx.mp4   (effects only, captions)
                          #   out/shelter3_captions.mp4 (captions, no sound)
                          #   out/shelter3_clean.mp4 (no captions, no sound)
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
sys.path.insert(0, os.path.join(HERE, "..", "brand"))
from captions import CAPTIONS, CARD_SECONDS, END, NARRATION, QUESTION, TITLE  # noqa: E402
from brand import overlay as brand, CREDIT, CHANNEL  # noqa: E402

FILM = "پناهگاه ۳"
LAST = int(END * FPS)
SPEAKERS = {"Me": ("من", (60, 160, 80)), "Mom": ("مامان", (150, 40, 80)), "Lena": ("لنا", (210, 50, 45)),
            "Guard": ("نگهبان", (235, 130, 20)), "Rescuer": ("امدادگر", (200, 70, 20)),
            "Old man": ("پیرمرد", (120, 90, 60)), "Radio": ("بی‌سیم", (70, 80, 70))}


def font(size):
    return ImageFont.truetype(FONT, size, layout_engine=ImageFont.Layout.RAQM)


def draw_text(d, xy, text, size, fill=(255, 255, 255), stroke=9, max_w=W - 90):
    while size > 30:
        l, t, r, b = d.multiline_textbbox(xy, text, font=font(size), anchor="mm", align="center", direction="rtl",
                                          language="fa", stroke_width=stroke, spacing=18)
        if r - l <= max_w:
            break
        size -= 3
    d.multiline_text(xy, text, font=font(size), fill=fill, anchor="mm", align="center", direction="rtl",
                     language="fa", stroke_width=stroke, stroke_fill=(15, 15, 15), spacing=18)


def pill(d, cx, cy, text, color, size=44):
    f = font(size)
    l, t, r, b = d.textbbox((cx, cy), text, font=f, anchor="mm", direction="rtl", language="fa")
    d.rounded_rectangle((l - 30, t - 14, r + 30, b + 14), radius=(b - t) // 2 + 14, fill=color, outline=(15, 15, 15),
                        width=5)
    d.text((cx, cy), text, font=f, fill=(255, 255, 255), anchor="mm", direction="rtl", language="fa")


def overlay(img, t, captions=True):
    d = ImageDraw.Draw(img)
    if captions:
        current = [c for c in CAPTIONS if c[0] <= t <= c[1]]
        for start, end, who, text in current[-1:]:
            k = min(1.0, (t - start) / 0.15)
            if start in NARRATION:
                draw_text(d, (W // 2, int(H * 0.7)), text, int(72 * (0.85 + 0.15 * k)), stroke=10)
            else:
                name, col = SPEAKERS[who]
                y = int(H * 0.68)
                pill(d, W // 2, y - 105 - 50 * text.count("\n"), name, col)
                draw_text(d, (W // 2, y), text, int(76 * (0.85 + 0.15 * k)))
    if t < TITLE:                       # «یک هفته بعد...» on black, then the bunker fades in
        black = Image.new("RGB", img.size, (0, 0, 0))
        k = min(1.0, max(0.0, (t - (TITLE - 0.7)) / 0.7))
        img = Image.blend(black, img, k)
        d2 = ImageDraw.Draw(img)
        a = min(1.0, t / 0.35) * (1 - k)
        if a > 0.02:
            col = tuple(int(c * a) for c in (255, 235, 150))
            draw_text(d2, (W // 2, H // 2 - 60), "یک هفته بعد...", int(120 * (0.92 + 0.08 * a)), fill=col, stroke=0)
    return brand(img, FILM)


def final_card(img, k):
    img = Image.blend(img, Image.new("RGB", img.size, (0, 0, 0)), 0.6 * k)
    if k >= 0.05:
        d = ImageDraw.Draw(img)
        draw_text(d, (W // 2, 520), QUESTION, int(80 * (0.8 + 0.2 * k)), stroke=12)
        for i, (label, col) in enumerate((("پیاده می‌شدم", (30, 110, 200)), ("منتظر می‌موندم", (200, 40, 45)))):
            y = 970 + i * 220
            d.rounded_rectangle((140, y - 80, W - 140, y + 80), radius=60, fill=col, outline=(255, 255, 255), width=8)
            d.text((W // 2 + 30, y), label, font=font(54), fill=(255, 255, 255), anchor="mm", direction="rtl",
                   language="fa")
            d.ellipse((170, y - 45, 260, y + 45), fill=(255, 255, 255))
            d.text((215, y), "AB"[i], font=font(56), fill=col, anchor="mm")
        draw_text(d, (W // 2, 1480), "جوابت رو کامنت کن", 64, fill=(255, 230, 120), stroke=9)
        draw_text(d, (W // 2, 1640), f"{CREDIT}  —  {CHANNEL}", 40, fill=(230, 230, 230), stroke=6)
    return brand(img, FILM)


def main():
    assert features.check("raqm"), "Pillow needs raqm for Persian text"
    shutil.rmtree(TMP, ignore_errors=True)
    os.makedirs(TMP)
    os.makedirs(OUT, exist_ok=True)
    seq = os.path.join(TMP, "seq")
    os.makedirs(seq)
    for i in range(1, LAST + 1):          # rendered on twos: each drawing held for two frames
        os.symlink(os.path.join(FRAMES, f"f_{i - (1 - i % 2):04d}.png"), os.path.join(seq, f"s_{i:04d}.png"))
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-framerate", str(FPS), "-i", os.path.join(seq, "s_%04d.png"),
                    "-vf", f"lenscorrection=k1=0.22:k2=0.05:i=bilinear,scale={int(W * 1.2)}:{int(H * 1.2)}:flags=lanczos,"
                           f"crop={W}:{H}", os.path.join(TMP, "d_%05d.png")], check=True)
    names = sorted(n for n in os.listdir(TMP) if n.startswith("d_"))
    i = 0
    for n in names:
        src = Image.open(os.path.join(TMP, n)).convert("RGB")
        overlay(src.copy(), i / FPS).save(os.path.join(TMP, f"c_{i:05d}.png"))
        overlay(src, i / FPS, captions=False).save(os.path.join(TMP, f"k_{i:05d}.png"))
        os.remove(os.path.join(TMP, n))
        i += 1
    last = Image.open(os.path.join(FRAMES, sorted(os.listdir(FRAMES))[-1])).convert("RGB").resize((W, H))
    for j in range(CARD_SECONDS * FPS):
        card = final_card(last.copy(), min(1.0, j / 12))
        card.save(os.path.join(TMP, f"c_{i:05d}.png"))
        card.save(os.path.join(TMP, f"k_{i:05d}.png"))
        i += 1
    enc = ["-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", "-movflags", "+faststart"]
    cap, clean = os.path.join(OUT, "shelter3_captions.mp4"), os.path.join(OUT, "shelter3_clean.mp4")
    for pre, out in (("c", cap), ("k", clean)):
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-framerate", str(FPS), "-i",
                        os.path.join(TMP, pre + "_%05d.png")] + enc + [out], check=True)
        print(out)
    for wav, name in (("sfx.wav", "shelter3_sfx.mp4"), ("voice.wav", "shelter3_voice.mp4")):
        a = os.path.join(OUT, wav)
        if os.path.exists(a):
            subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", cap, "-i", a, "-map", "0:v", "-map", "1:a",
                            "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", os.path.join(OUT, name)],
                           check=True)
            print(os.path.join(OUT, name))
    shutil.rmtree(TMP, ignore_errors=True)


if __name__ == "__main__":
    main()
