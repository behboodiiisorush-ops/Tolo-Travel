"""
16:9 long-form version of «پناهگاه ۳»: frames_wide/ (1280x720, rendered on twos with WIDE=1) -> 1920x1080 24 fps,
light fisheye, captions at the bottom, title, branding on every frame, the question card; then the same mixes
as the vertical film (out/voice.wav, out/sfx.wav).  Resumable: frames already drawn in post_wide_tmp/ are kept.

    python3 post_wide.py  ->  out/shelter3_long_voice.mp4, _sfx.mp4, _captions.mp4, _clean.mp4
"""
import os
import subprocess
import sys
from multiprocessing import Pool

from PIL import Image, ImageDraw, ImageFont, features

HERE = os.path.dirname(os.path.abspath(__file__))
FRAMES = os.path.join(HERE, "frames_wide")
TMP = os.path.join(HERE, "post_wide_tmp")
OUT = os.path.join(HERE, "out")
FONT = os.path.join(HERE, "..", "fonts", "Vazirmatn-FD-ExtraBold.ttf")
FPS = 24
W, H = 1920, 1080
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "brand"))
from captions import CAPTIONS, CARD_SECONDS, END, NARRATION, QUESTION, TITLE  # noqa: E402
from brand import overlay as brand, CHANNEL  # noqa: E402

FILM = "پناهگاه ۳"
LAST = int(END * FPS)
SPEAKERS = {"Me": ("من", (60, 160, 80)), "Mom": ("مامان", (150, 40, 80)), "Lena": ("لنا", (210, 50, 45)),
            "Guard": ("نگهبان", (235, 130, 20)), "Rescuer": ("امدادگر", (200, 70, 20)),
            "Old man": ("پیرمرد", (120, 90, 60)), "Radio": ("بی‌سیم", (70, 80, 70))}


def font(size):
    return ImageFont.truetype(FONT, size, layout_engine=ImageFont.Layout.RAQM)


def draw_text(d, xy, text, size, fill=(255, 255, 255), stroke=7, max_w=W - 300):
    text = text.replace("\n", " ")
    while size > 28:
        l, t, r, b = d.textbbox(xy, text, font=font(size), anchor="mm", direction="rtl", language="fa",
                                stroke_width=stroke)
        if r - l <= max_w:
            break
        size -= 2
    d.text(xy, text, font=font(size), fill=fill, anchor="mm", direction="rtl", language="fa",
           stroke_width=stroke, stroke_fill=(15, 15, 15))


def pill(d, cx, cy, text, color, size=34):
    f = font(size)
    l, t, r, b = d.textbbox((cx, cy), text, font=f, anchor="mm", direction="rtl", language="fa")
    d.rounded_rectangle((l - 24, t - 10, r + 24, b + 10), radius=(b - t) // 2 + 10, fill=color, outline=(15, 15, 15),
                        width=4)
    d.text((cx, cy), text, font=f, fill=(255, 255, 255), anchor="mm", direction="rtl", language="fa")


def overlay(img, t, captions=True):
    d = ImageDraw.Draw(img)
    if captions:
        current = [c for c in CAPTIONS if c[0] <= t <= c[1]]
        for start, end, who, text in current[-1:]:
            k = min(1.0, (t - start) / 0.15)
            y = int(H * 0.88)
            if start not in NARRATION:
                name, col = SPEAKERS[who]
                pill(d, W // 2, y - 72, name, col)
            draw_text(d, (W // 2, y), text, int(58 * (0.88 + 0.12 * k)))
    if t < TITLE:
        black = Image.new("RGB", img.size, (0, 0, 0))
        k = min(1.0, max(0.0, (t - (TITLE - 0.7)) / 0.7))
        img = Image.blend(black, img, k)
        d2 = ImageDraw.Draw(img)
        a = min(1.0, t / 0.35) * (1 - k)
        if a > 0.02:
            col = tuple(int(c * a) for c in (255, 235, 150))
            draw_text(d2, (W // 2, H // 2), "یک هفته بعد...", int(110 * (0.92 + 0.08 * a)), fill=col, stroke=0)
    return brand(img, FILM)


def final_card(img, k):
    img = Image.blend(img, Image.new("RGB", img.size, (0, 0, 0)), 0.6 * k)
    if k >= 0.05:
        d = ImageDraw.Draw(img)
        q = QUESTION.split("\n")
        for i, line in enumerate(q):
            draw_text(d, (W // 2, 250 + i * 95), line, int(72 * (0.8 + 0.2 * k)), stroke=10)
        y = 300 + len(q) * 95 + 60
        for i, (label, col) in enumerate((("پیاده می‌شدم", (30, 110, 200)), ("منتظر می‌موندم", (200, 40, 45)))):
            cx = W // 2 + (300 if i == 0 else -300)          # A on the right (RTL), B on the left
            d.rounded_rectangle((cx - 260, y - 70, cx + 260, y + 70), radius=55, fill=col, outline=(255, 255, 255),
                                width=7)
            d.text((cx - 30, y), label, font=font(48), fill=(255, 255, 255), anchor="mm", direction="rtl",
                   language="fa")
            d.ellipse((cx + 150, y - 40, cx + 230, y + 40), fill=(255, 255, 255))
            d.text((cx + 190, y), "AB"[i], font=font(50), fill=col, anchor="mm")
        draw_text(d, (W // 2, y + 170), "جوابت رو کامنت کن", 58, fill=(255, 230, 120), stroke=8)
        draw_text(d, (W // 2, y + 260), CHANNEL, 36, fill=(230, 230, 230), stroke=5)
    return brand(img, FILM)


def job(i):
    c, kk = os.path.join(TMP, f"c_{i:05d}.png"), os.path.join(TMP, f"k_{i:05d}.png")
    if os.path.exists(c) and os.path.exists(kk):
        return
    src = Image.open(os.path.join(TMP, f"d_{i + 1:05d}.png")).convert("RGB")
    overlay(src.copy(), i / FPS, captions=False).save(kk)
    overlay(src, i / FPS).save(c)


def card(j):
    last = Image.open(os.path.join(TMP, f"d_{LAST:05d}.png")).convert("RGB")
    im = final_card(last, min(1.0, j / 12))
    im.save(os.path.join(TMP, f"c_{LAST + j:05d}.png"))
    im.save(os.path.join(TMP, f"k_{LAST + j:05d}.png"))


def main():
    assert features.check("raqm"), "Pillow needs raqm for Persian text"
    os.makedirs(TMP, exist_ok=True)
    os.makedirs(OUT, exist_ok=True)
    if not os.path.exists(os.path.join(TMP, f"d_{LAST:05d}.png")):
        seq = os.path.join(TMP, "seq")
        os.makedirs(seq, exist_ok=True)
        for i in range(1, LAST + 1):      # rendered on twos: each drawing held for two frames
            p = os.path.join(seq, f"s_{i:04d}.png")
            if not os.path.lexists(p):
                os.symlink(os.path.join(FRAMES, f"f_{i - (1 - i % 2):04d}.png"), p)
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-framerate", str(FPS), "-i",
                        os.path.join(seq, "s_%04d.png"), "-vf",
                        f"lenscorrection=k1=0.12:k2=0.03:i=bilinear,scale={int(W * 1.1)}:{int(H * 1.1)}:flags=lanczos,"
                        f"crop={W}:{H}", os.path.join(TMP, "d_%05d.png")], check=True)
    with Pool(max(1, os.cpu_count() - 1)) as pool:
        pool.map(job, range(LAST), chunksize=16)
        pool.map(card, range(CARD_SECONDS * FPS))
    print("frames drawn", flush=True)
    enc = ["-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", "-preset", "medium", "-movflags", "+faststart"]
    cap, clean = os.path.join(OUT, "shelter3_long_captions.mp4"), os.path.join(OUT, "shelter3_long_clean.mp4")
    for pre, out in (("c", cap), ("k", clean)):
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-framerate", str(FPS), "-i",
                        os.path.join(TMP, pre + "_%05d.png")] + enc + [out], check=True)
        print(out, flush=True)
    for wav, name in (("sfx.wav", "shelter3_long_sfx.mp4"), ("voice.wav", "shelter3_long_voice.mp4")):
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", cap, "-i", os.path.join(OUT, wav), "-map", "0:v",
                        "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest",
                        os.path.join(OUT, name)], check=True)
        print(os.path.join(OUT, name), flush=True)
    print("POST_WIDE_DONE", flush=True)


if __name__ == "__main__":
    main()
