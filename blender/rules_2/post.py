"""Post for «قانون‌ها — قسمت دوم»: upscale, title, the phone messages (big phone on screen), Persian captions,
fade to black, question card, channel logo + film name on every frame (brand.overlay).
    out/rules2_captions.mp4   captions, no sound (for the voices)
    out/rules2_clean.mp4      no captions, no sound
    out/rules2_sfx.mp4        captions + synthesised sound effects (if out/rules2_sfx.wav exists)
    out/rules2.mp4            captions + voices + effects (if out/rules2_mix.wav exists)
"""
import os, shutil, subprocess, sys
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "brand"))
from captions import LINES, NAMES, END, QUESTION, TITLE, SUBTITLE, PHONE  # noqa: E402
from brand import overlay  # noqa: E402
FONT = os.path.join(HERE, "..", "fonts", "Vazirmatn-FD-ExtraBold.ttf")
FONT_R = os.path.join(HERE, "..", "fonts", "Vazirmatn-FD-Regular.ttf")
FPS, W, H = 24, 1080, 1920
CARD = 4.0
SRC = os.path.join(HERE, "frames")
TMP, OUT = os.path.join(HERE, "post_tmp"), os.path.join(HERE, "out")
COL = {"me": (150, 190, 255), "arian": (170, 220, 110), "nina": (255, 140, 160), "fake": (255, 110, 90),
       "rule": (255, 255, 255)}
MSG = {"rule6": ("شماره‌ی خودم", "قانون ۶: ده ثانیه دیگه نینا گوشیش رو درمیاره. نذار زنگ بزنه.", None),
       "rule7": ("شماره‌ی خودم", "قانون ۷: برنگرد.", os.path.join(HERE, "textures", "spy.png"))}
_fc = {}


def font(s, bold=True):
    k = (s, bold)
    if k not in _fc:
        p = FONT if bold or not os.path.exists(FONT_R) else FONT_R
        _fc[k] = ImageFont.truetype(p, s, layout_engine=ImageFont.Layout.RAQM)
    return _fc[k]


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
    y = 1450 - 45 * (len(lines) - 1)
    d.text((W // 2, y - 80), NAMES[who], font=fs, fill=COL[who], anchor="mm", direction="rtl", language="fa",
           stroke_width=6, stroke_fill=(0, 0, 0))
    for k, ln in enumerate(lines):
        d.text((W // 2, y + k * 90), ln, font=f, fill=(255, 255, 255), anchor="mm", direction="rtl", language="fa",
               stroke_width=9, stroke_fill=(0, 0, 0))


def phone(img, which, u):
    """A big phone rising from the bottom with the message (and the photo for rule 7). u: 0..1 slide-in."""
    sender, text, photo = MSG[which]
    pw, ph = 640, 1040
    x0 = (W - pw) // 2
    y0 = int(H - 120 - ph + (1 - u) * (ph + 200))
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    d.rounded_rectangle((x0 - 18, y0 - 18, x0 + pw + 18, y0 + ph + 18), 70, fill=(12, 12, 14, 255))
    d.rounded_rectangle((x0, y0, x0 + pw, y0 + ph), 56, fill=(24, 26, 34, 255))
    d.rounded_rectangle((x0 + pw // 2 - 70, y0 + 16, x0 + pw // 2 + 70, y0 + 40), 12, fill=(8, 8, 10, 255))
    d.rectangle((x0, y0 + 70, x0 + pw, y0 + 190), fill=(34, 37, 48, 255))
    d.ellipse((x0 + pw - 140, y0 + 90, x0 + pw - 60, y0 + 170), fill=(200, 40, 50, 255))
    d.text((x0 + pw - 100, y0 + 130), "؟", font=font(56), fill=(255, 255, 255, 255), anchor="mm")
    d.text((x0 + pw - 165, y0 + 130), sender, font=font(44), fill=(235, 235, 240, 255), anchor="rm",
           direction="rtl", language="fa")
    y = y0 + 240
    if photo and os.path.exists(photo):
        im = Image.open(photo).convert("RGB")
        iw = pw - 120
        ih = int(iw * im.height / im.width)
        im = im.resize((iw, ih), Image.LANCZOS)
        bx = x0 + pw - 50 - iw
        d.rounded_rectangle((bx - 14, y - 14, bx + iw + 14, y + ih + 14), 28, fill=(52, 56, 70, 255))
        ov.paste(im, (bx, y))
        y += ih + 50
    f = font(50)
    lines = wrap(d, text, f, pw - 170)
    bh = 40 + 74 * len(lines)
    d.rounded_rectangle((x0 + 50, y, x0 + pw - 50, y + bh), 34, fill=(52, 56, 70, 255))
    for k, ln in enumerate(lines):
        d.text((x0 + pw - 85, y + 55 + k * 74), ln, font=f, fill=(255, 255, 255, 255), anchor="rm",
               direction="rtl", language="fa")
    return Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB")


def title(img, t):
    a = min(1.0, (t - 0.3) / 0.8, (5.6 - t) / 0.6)
    if a <= 0:
        return img
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    d.text((W // 2, 520), TITLE, font=font(150), fill=(255, 245, 230, int(255 * a)), anchor="mm", direction="rtl",
           language="fa", stroke_width=10, stroke_fill=(20, 16, 14, int(255 * a)))
    d.text((W // 2, 660), SUBTITLE, font=font(90), fill=(230, 60, 60, int(255 * a)), anchor="mm", direction="rtl",
           language="fa", stroke_width=8, stroke_fill=(20, 16, 14, int(255 * a)))
    return Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB")


def card(t):
    img = Image.new("RGB", (W, H), (0, 0, 0))
    d = ImageDraw.Draw(img)
    a = min(1.0, t / 0.8)
    f = font(84)
    lines = wrap(d, QUESTION, f, W - 160)
    y0 = H // 2 - 60 * (len(lines) - 1)
    c = int(255 * a)
    for k, ln in enumerate(lines):
        d.text((W // 2, y0 + k * 120), ln, font=f, fill=(c, c, c), anchor="mm", direction="rtl", language="fa")
    d.text((W // 2, y0 - 190), "؟", font=font(140), fill=(int(230 * a), int(40 * a), int(50 * a)), anchor="mm")
    return img


def encode(pattern, out, audio=None):
    cmd = ["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-i", pattern]
    if audio:
        cmd += ["-i", audio, "-c:a", "aac", "-b:a", "192k", "-shortest"]
    cmd += ["-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", "-movflags", "+faststart", out]
    subprocess.run(cmd, check=True)
    print(out)


def main():
    shutil.rmtree(TMP, ignore_errors=True)
    os.makedirs(TMP)
    os.makedirs(OUT, exist_ok=True)
    n_pic = int(END * FPS)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-i", os.path.join(SRC, "f_%04d.png"),
                    "-frames:v", str(n_pic), "-vf", f"scale={W}:{H}:flags=lanczos,vignette=PI/5",
                    "-q:v", "2", os.path.join(TMP, "u_%04d.jpg")], check=True)
    names = sorted(n for n in os.listdir(TMP) if n.startswith("u_"))
    total = len(names) + int(CARD * FPS)
    black = Image.new("RGB", (W, H))
    for i in range(total):
        t = i / FPS
        if i < len(names):
            img = Image.open(os.path.join(TMP, names[i])).convert("RGB")
            os.remove(os.path.join(TMP, names[i]))
            if t < 6.0:
                img = title(img, t)
            for a, b, which in PHONE:
                if a <= t < b:
                    u = min(1.0, (t - a) / 0.45, (b - t) / 0.35)
                    img = phone(img, which, u * u * (3 - 2 * u))
            fade = min(1.0, max(0.0, (END - t) / 0.5))
            if fade < 1:
                img = Image.blend(black, img, fade)
        else:
            img = card(t - len(names) / FPS)
        overlay(img, TITLE + " ۲")
        img.save(os.path.join(TMP, f"n_{i:04d}.jpg"), quality=94)
        if i < len(names):
            for a, b, who, text in LINES:
                if a <= t <= b and who != "rule":          # phone messages are on the phone itself
                    caption(img, who, text)
        img.save(os.path.join(TMP, f"c_{i:04d}.jpg"), quality=94)
    encode(os.path.join(TMP, "c_%04d.jpg"), os.path.join(OUT, "rules2_captions.mp4"))
    encode(os.path.join(TMP, "n_%04d.jpg"), os.path.join(OUT, "rules2_clean.mp4"))
    sfx = os.path.join(OUT, "rules2_sfx.wav")
    if os.path.exists(sfx):
        encode(os.path.join(TMP, "c_%04d.jpg"), os.path.join(OUT, "rules2_sfx.mp4"), sfx)
    mix = os.path.join(OUT, "rules2_mix.wav")
    if os.path.exists(mix):
        encode(os.path.join(TMP, "c_%04d.jpg"), os.path.join(OUT, "rules2.mp4"), mix)
    shutil.rmtree(TMP, ignore_errors=True)


if __name__ == "__main__":
    main()
