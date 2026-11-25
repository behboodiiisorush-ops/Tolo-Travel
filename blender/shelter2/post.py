"""
Post-processing for «پناهگاه ۲ — چراغ سبز»: frames rendered on twos -> 24 fps, fisheye look, upscale to
1080x1920, narration captions, the viewer question (start, middle, final card), episode badge.

    python3 post.py     # frames/ -> out/shelter2_full.mp4 (+ out/shelter2_sfx.mp4 with effects)
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
from captions import CAPTIONS, CARD_SECONDS, END, KEY_OF, NARRATION, NOTIFS, QUESTION  # noqa: E402

TITLE_END = 2.4   # seconds of the black opening title


def font(size):
    return ImageFont.truetype(FONT, size, layout_engine=ImageFont.Layout.RAQM)


def draw_text(d, xy, text, size, fill=(255, 255, 255), stroke=9, max_w=W - 90):
    """Centred RTL text; long lines shrink until they fit the frame width."""
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


def notification(img, t, start, end, app, icon_col, title, body):
    """A phone notification banner sliding down from the top of the screen (RTL)."""
    if not (start <= t <= end):
        return
    k = min(1.0, (t - start) / 0.3, (end - t) / 0.3)
    k = k * k * (3 - 2 * k)
    top = int(-260 + (60 + 260) * k)
    d = ImageDraw.Draw(img, "RGBA")
    x0, x1, h = 28, W - 28, 230
    d.rounded_rectangle((x0 + 6, top + 10, x1 + 6, top + h + 10), radius=44, fill=(0, 0, 0, 70))
    d.rounded_rectangle((x0, top, x1, top + h), radius=44, fill=(246, 246, 246, 255))
    # icon + app name on the right (RTL), "الان" on the left
    ix = x1 - 40 - 56
    d.rounded_rectangle((ix, top + 30, ix + 56, top + 86), radius=14, fill=icon_col)
    d.rounded_rectangle((ix + 13, top + 44, ix + 43, top + 66), radius=8, fill=(255, 255, 255))
    d.polygon([(ix + 18, top + 64), (ix + 26, top + 64), (ix + 16, top + 74)], fill=(255, 255, 255))
    d.text((ix - 18, top + 58), app, font=font(36), fill=(110, 110, 115), anchor="rm", direction="rtl", language="fa")
    d.text((x0 + 40, top + 58), "الان", font=font(34), fill=(140, 140, 145), anchor="lm", direction="rtl", language="fa")
    d.text((x1 - 40, top + 120), title, font=font(46), fill=(10, 10, 10), anchor="rm", direction="rtl", language="fa")
    size = 40
    while size > 26 and d.textlength(body, font=font(size), direction="rtl", language="fa") > (x1 - x0 - 80):
        size -= 2
    d.text((x1 - 40, top + 182), body, font=font(size), fill=(30, 30, 30), anchor="rm", direction="rtl", language="fa")


def overlay(img, t):
    d = ImageDraw.Draw(img)
    pill(d, W - 170, 150, "پناهگاه ۲", (60, 60, 70), 46)
    current = [c for c in CAPTIONS if c[0] <= t <= c[1]]
    for start, end, who, text in current[-1:]:  # when two lines overlap, the newer one wins
        if True:
            k = min(1.0, (t - start) / 0.15)
            if start in NARRATION:
                draw_text(d, (W // 2, int(H * 0.7)), text, int(76 * (0.85 + 0.15 * k)), stroke=10)
            else:
                name, col = SPEAKERS[who]
                y = int(H * 0.68)
                pill(d, W // 2, y - 105 - 50 * text.count("\n"), name, col)
                draw_text(d, (W // 2, y), text, int(80 * (0.85 + 0.15 * k)))
    for n in NOTIFS:
        notification(img, t, *n)
    if t < TITLE_END:  # the opening title on black: "three days later", then the bunker fades in
        black = Image.new("RGB", img.size, (0, 0, 0))
        k = min(1.0, max(0.0, (t - (TITLE_END - 0.7)) / 0.7))
        img = Image.blend(black, img, k)
        d2 = ImageDraw.Draw(img)
        a = min(1.0, t / 0.35) * (1 - k)
        if a > 0.02:
            col = tuple(int(c * a) for c in (255, 235, 150))
            draw_text(d2, (W // 2, H // 2 - 60), "سه روز بعد...", int(120 * (0.92 + 0.08 * a)), fill=col,
                      stroke=0)

    return img


def final_card(img, k):
    img = Image.blend(img, Image.new("RGB", img.size, (0, 0, 0)), 0.6 * k)
    if k < 0.05:
        return img
    d = ImageDraw.Draw(img)
    draw_text(d, (W // 2, 500), "اگه تو بودی...\nتوی پناهگاه می‌موندی\nیا می‌زدی بیرون؟",
              int(84 * (0.8 + 0.2 * k)), stroke=12)
    for i, (label, col) in enumerate((("می‌موندم", (30, 110, 200)),
                                      ("می‌زدم بیرون", (200, 40, 45)))):
        y = 950 + i * 220
        d.rounded_rectangle((140, y - 80, W - 140, y + 80), radius=60, fill=col, outline=(255, 255, 255), width=8)
        d.text((W // 2 + 30, y), label, font=font(54), fill=(255, 255, 255), anchor="mm", direction="rtl", language="fa")
        d.ellipse((170, y - 45, 260, y + 45), fill=(255, 255, 255))
        d.text((215, y), "AB"[i], font=font(56), fill=col, anchor="mm")
    draw_text(d, (W // 2, 1480), "جوابت رو کامنت کن", 64, fill=(255, 230, 120), stroke=9)
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
    out = os.path.join(OUT, "shelter2_full.mp4")
    subprocess.run([
        "ffmpeg", "-loglevel", "error", "-y", "-framerate", str(FPS), "-i", os.path.join(TMP, "c_%04d.png"),
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", "-movflags", "+faststart", out], check=True)
    print(out)
    sfx = os.path.join(OUT, "sfx.wav")
    if os.path.exists(sfx):
        out_fx = os.path.join(OUT, "shelter2_sfx.mp4")
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", out, "-i", sfx, "-map", "0:v", "-map", "1:a",
                        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", out_fx], check=True)
        print(out_fx)


if __name__ == "__main__":
    main()
