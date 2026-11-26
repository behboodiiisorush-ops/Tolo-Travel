"""Post for «سال ۱۵۰۰»: upscale, flashback grade, white flash and black, title, Persian captions, question card.
    out/year1500_captions.mp4   captions, no sound (for the user's ElevenLabs voices)
    out/year1500_clean.mp4      no captions, no sound
    out/year1500_sfx.mp4        captions + synthesised sound effects (if out/year1500_sfx.wav exists)
"""
import os, shutil, subprocess, sys
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from captions import LINES, NAMES, END, QUESTION, TITLE, FLASHBACK  # noqa: E402
FONT = os.path.join(HERE, "..", "fonts", "Vazirmatn-FD-ExtraBold.ttf")
FPS, W, H = 24, 1080, 1920
CARD = 4.0
FB0, FB1 = FLASHBACK
WAKE = 22.0
SRC = os.path.join(HERE, "frames")
TMP, OUT = os.path.join(HERE, "post_tmp"), os.path.join(HERE, "out")
COL = {"me": (150, 200, 255), "mom": (255, 150, 170), "kian": (255, 230, 90)}


def font(s):
    return ImageFont.truetype(FONT, s, layout_engine=ImageFont.Layout.RAQM)


def wrap(d, text, f, maxw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if d.textlength(test, font=f, direction="rtl", language="fa") > maxw and cur:
            lines.append(cur)
            cur = w
        else:
            cur = test
    lines.append(cur)
    return lines


def caption(img, who, text):
    d = ImageDraw.Draw(img)
    f, fs = font(72), font(44)
    lines = wrap(d, text, f, W - 140)
    y = 1400 - 45 * (len(lines) - 1)
    d.text((W // 2, y - 80), NAMES[who], font=fs, fill=COL[who], anchor="mm", direction="rtl", language="fa",
           stroke_width=6, stroke_fill=(0, 0, 0))
    for k, ln in enumerate(lines):
        d.text((W // 2, y + k * 90), ln, font=f, fill=(255, 255, 255), anchor="mm", direction="rtl", language="fa",
               stroke_width=9, stroke_fill=(0, 0, 0))


def title(img, t):
    a = min(1.0, (t - 0.6) / 0.8, (5.8 - t) / 0.6)
    if a <= 0:
        return img
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    d.text((W // 2, 520), TITLE, font=font(150), fill=(255, 245, 230, int(255 * a)), anchor="mm", direction="rtl",
           language="fa", stroke_width=10, stroke_fill=(20, 16, 14, int(255 * a)))
    return Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB")


def grade_flashback(img):
    """The past: warmer, brighter, a little more colour and a soft glow."""
    img = ImageEnhance.Color(img).enhance(1.45)
    img = ImageEnhance.Brightness(img).enhance(1.06)
    r, g, b = img.split()
    img = Image.merge("RGB", (r.point(lambda v: min(255, int(v * 1.06 + 6))), g, b.point(lambda v: int(v * 0.92))))
    glow = img.filter(ImageFilter.GaussianBlur(18))
    return Image.blend(img, glow, 0.18)


def card(t):
    img = Image.new("RGB", (W, H), (0, 0, 0))
    d = ImageDraw.Draw(img)
    a = min(1.0, t / 0.8)
    f = font(80)
    lines = wrap(d, QUESTION, f, W - 160)
    y0 = H // 2 - 60 * (len(lines) - 1)
    c = int(255 * a)
    for k, ln in enumerate(lines):
        d.text((W // 2, y0 + k * 115), ln, font=f, fill=(c, c, c), anchor="mm", direction="rtl", language="fa")
    d.text((W // 2, y0 - 190), "؟", font=font(140), fill=(int(120 * a), int(190 * a), int(255 * a)), anchor="mm")
    return img


def encode(pattern, out, audio=None):
    cmd = ["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-i", pattern]
    if audio:
        cmd += ["-i", audio, "-c:a", "aac", "-b:a", "192k", "-shortest"]
    cmd += ["-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", "-movflags", "+faststart", out]
    subprocess.run(cmd, check=True)
    print(out)


def vignette():
    m = Image.new("L", (W // 8, H // 8), 0)
    ImageDraw.Draw(m).ellipse((-W // 16, -H // 20, W // 8 + W // 16, H // 8 + H // 20), fill=255)
    return m.filter(ImageFilter.GaussianBlur(14)).resize((W, H), Image.BILINEAR)


def main():
    shutil.rmtree(TMP, ignore_errors=True)
    os.makedirs(TMP)
    os.makedirs(OUT, exist_ok=True)
    vig = vignette()
    black = Image.new("RGB", (W, H))
    n_pic = int(END * FPS)
    total = n_pic + int(CARD * FPS)
    for i in range(total):
        t = i / FPS
        f = i + 1
        if i < n_pic:
            p = os.path.join(SRC, f"f_{f:04d}.png")
            if os.path.exists(p) and not (FB1 <= t < WAKE):
                img = Image.open(p).convert("RGB").resize((W, H), Image.LANCZOS)
            else:
                img = black.copy()
            if FB0 <= t < FB1:
                img = grade_flashback(img)
                if t > FB1 - 0.7:                                   # white flash, then black
                    u = (t - (FB1 - 0.7)) / 0.7
                    img = Image.blend(img, Image.new("RGB", (W, H), (255, 255, 255)), min(1.0, u * 1.6))
            if WAKE <= t < WAKE + 1.2:                              # eyes opening
                img = Image.blend(black, img, (t - WAKE) / 1.2)
            if FB0 - 0.15 <= t < FB0 + 0.25:                        # a soft white dip into the memory
                u = 1 - abs(t - (FB0 + 0.05)) / 0.2
                img = Image.blend(img, Image.new("RGB", (W, H), (255, 250, 240)), max(0.0, u) * 0.8)
            img = Image.composite(img, Image.blend(black, img, 0.55), vig)
            if t < 6.2:
                img = title(img, t)
            fade = min(1.0, max(0.0, (END - t) / 0.8))
            if fade < 1:
                img = Image.blend(black, img, fade)
        else:
            img = card(t - n_pic / FPS)
        img.save(os.path.join(TMP, f"n_{i:04d}.jpg"), quality=94)
        if i < n_pic:
            for a, b, who, text in LINES:
                if a <= t <= b:
                    caption(img, who, text)
        img.save(os.path.join(TMP, f"c_{i:04d}.jpg"), quality=94)
    encode(os.path.join(TMP, "c_%04d.jpg"), os.path.join(OUT, "year1500_captions.mp4"))
    encode(os.path.join(TMP, "n_%04d.jpg"), os.path.join(OUT, "year1500_clean.mp4"))
    sfx = os.path.join(OUT, "year1500_sfx.wav")
    if os.path.exists(sfx):
        encode(os.path.join(TMP, "c_%04d.jpg"), os.path.join(OUT, "year1500_sfx.mp4"), sfx)
    shutil.rmtree(TMP, ignore_errors=True)


if __name__ == "__main__":
    main()
