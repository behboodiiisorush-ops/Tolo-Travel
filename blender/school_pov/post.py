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
TEX = os.path.join(HERE, "textures")
# moments when the phone fills the screen so its message can be read: (start, end, screen)
PHONE_SHOTS = [(21.6, 25.6, "voice"), (25.6, 27.5, "failed"), (55.2, 57.0, "failed")]
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


_phones = {}


def phone_card(key):
    """The phone texture with a dark rounded bezel, about half the screen wide."""
    if key not in _phones:
        scr = Image.open(os.path.join(TEX, f"phone_{key}.png")).convert("RGB").resize((500, 1000), Image.LANCZOS)
        card = Image.new("RGBA", (560, 1060), (0, 0, 0, 0))
        d = ImageDraw.Draw(card)
        d.rounded_rectangle((0, 0, 559, 1059), radius=60, fill=(20, 20, 24, 255), outline=(70, 70, 80, 255), width=4)
        mask = Image.new("L", scr.size, 0)
        ImageDraw.Draw(mask).rounded_rectangle((0, 0, 499, 999), radius=36, fill=255)
        card.paste(scr, (30, 30), mask)
        _phones[key] = card
    return _phones[key]


def phone_overlay(img, t):
    for start, end, key in PHONE_SHOTS:
        if start <= t < end:
            first = not any(abs(e - start) < 1e-6 for _, e, _ in PHONE_SHOTS)  # slide in only on a new shot
            last = not any(abs(s - end) < 1e-6 for s, _, _ in PHONE_SHOTS)
            k_in = min(1.0, (t - start) / 0.25) if first else 1.0
            k_out = min(1.0, (end - t) / 0.25) if last else 1.0
            k = min(k_in, k_out)
            k = 1 - (1 - k) ** 3
            card = phone_card(key)
            x = (W - card.width) // 2
            y = int(lerp_i(H, 120, k))
            dim = Image.new("RGB", img.size, (0, 0, 0))
            img = Image.blend(img, dim, 0.35 * k)
            img.paste(card, (x, y), card)
    return img


def lerp_i(a, b, k):
    return a + (b - a) * k


def overlay(img, t):
    img = phone_overlay(img, t)
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
                y = int(H * (0.72 if any(a <= t < b for a, b, _ in PHONE_SHOTS) else 0.6))
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
    sfx = os.path.join(OUT, "sfx.wav")
    if os.path.exists(sfx):  # the same picture with the sound effects under it
        out2 = os.path.join(OUT, "last_bell_sfx.mp4")
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", out, "-i", sfx, "-map", "0:v", "-map", "1:a",
                        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", out2],
                       check=True)
        print(out2)


if __name__ == "__main__":
    main()
