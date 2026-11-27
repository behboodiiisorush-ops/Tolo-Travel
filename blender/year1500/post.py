"""Post for «سال ۱۵۰۰»: upscale, flashback grade, white flash and black, title, Persian captions, question card.
    out/year1500_captions.mp4   captions, no sound (for the user's ElevenLabs voices)
    out/year1500_clean.mp4      no captions, no sound
    out/year1500_sfx.mp4        captions + ElevenLabs sound effects only (sound_el.py -> out/year1500_sfx.wav)
    out/year1500.mp4            the finished film: captions + ElevenLabs voices + effects (voices.py -> year1500_mix.wav)
"""
import os, shutil, subprocess, sys
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from captions import LINES, NAMES, END, QUESTION, TITLE, FLASHBACK, WAKE  # noqa: E402
FONT = os.path.join(HERE, "..", "fonts", "Vazirmatn-FD-ExtraBold.ttf")
FPS, W, H = 24, 1080, 1920
CARD = 4.0
FB0, FB1 = FLASHBACK
SRC = os.path.join(HERE, "frames")
TMP, OUT = os.path.join(HERE, "post_tmp"), os.path.join(HERE, "out")
COL = {"me": (60, 160, 80), "mom": (150, 40, 80), "kian": (30, 110, 200)}   # name pills, like «واگن آخر»


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


def pill(d, cx, cy, text, color, size=44):
    f = font(size)
    l, t, r, b = d.textbbox((cx, cy), text, font=f, anchor="mm", direction="rtl", language="fa")
    px, py = 30, 14
    d.rounded_rectangle((l - px, t - py, r + px, b + py), radius=(b - t) // 2 + py, fill=color, outline=(15, 15, 15),
                        width=5)
    d.text((cx, cy), text, font=f, fill=(255, 255, 255), anchor="mm", direction="rtl", language="fa")


def caption(img, who, text, k=1.0):
    d = ImageDraw.Draw(img)
    f = font(int(80 * (0.85 + 0.15 * k)))
    lines = wrap(d, text, f, W - 140)
    y = int(H * 0.6) - 45 * (len(lines) - 1)
    pill(d, W // 2, y - 105, NAMES[who], COL[who])
    for j, ln in enumerate(lines):
        d.text((W // 2, y + j * 95), ln, font=f, fill=(255, 255, 255), anchor="mm", direction="rtl", language="fa",
               stroke_width=9, stroke_fill=(15, 15, 15))


def title(img, t):
    a = min(1.0, (t - 0.6) / 0.8, (6.6 - t) / 0.6)
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


def eyelids(img, u):
    """Opening eyes: black lids from top and bottom part, close once, open again."""
    if u < 0.9:
        o = u / 0.9
    elif u < 1.3:
        o = 1 - (u - 0.9) / 0.4 * 0.8
    else:
        o = min(1.0, 0.2 + (u - 1.3) / 0.8 * 0.8)
    o = o * o * (3 - 2 * o)
    gap = int(H / 2 * o)
    m = Image.new("L", (W, H), 0)
    ImageDraw.Draw(m).ellipse((-W * 0.3, H / 2 - gap * 1.25, W * 1.3, H / 2 + gap * 1.25), fill=255)
    m = m.filter(ImageFilter.GaussianBlur(40))
    blur = img.filter(ImageFilter.GaussianBlur(int(14 * (1 - o))))
    return Image.composite(blur, Image.new("RGB", (W, H)), m)


def badge(img):
    pill(ImageDraw.Draw(img), W - 150, 150, TITLE, (200, 40, 40), 46)


CHANNEL = "agetobudi"
MADE = "ساخته شده توسط بلندر"
LOGO = os.path.join(HERE, "..", "brand", "logo.png")      # the channel logo (optional until it is in the repo)


def _logo(h):
    if not os.path.exists(LOGO):
        return None
    lg = Image.open(LOGO).convert("RGBA")
    return lg.resize((max(1, int(lg.width * h / lg.height)), h), Image.LANCZOS)


def credit(img, a=0.8):
    """Small corner credit on every frame of every version: logo (if any), channel name, «made with Blender»."""
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    x, y = 48, H - 70
    lg = _logo(84)
    if lg is not None:
        lg.putalpha(lg.getchannel("A").point(lambda v: int(v * a)))
        ov.alpha_composite(lg, (x, y - 84 - 66))
    d.text((x, y - 38), CHANNEL, font=font(40), fill=(255, 255, 255, int(255 * a)), anchor="lm",
           stroke_width=4, stroke_fill=(15, 15, 15, int(200 * a)))
    d.text((x, y + 8), MADE, font=font(28), fill=(235, 235, 235, int(230 * a)), anchor="lm", direction="rtl",
           language="fa", stroke_width=3, stroke_fill=(15, 15, 15, int(200 * a)))
    return Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB")


def big_credit(img, a, y):
    """The opening / closing credit: logo, «ساخته شده توسط بلندر» and the channel name, centred."""
    if a <= 0:
        return img
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    lg = _logo(150)
    if lg is not None:
        lg.putalpha(lg.getchannel("A").point(lambda v: int(v * a)))
        ov.alpha_composite(lg, (W // 2 - lg.width // 2, y - 230))
    d.text((W // 2, y), MADE, font=font(56), fill=(255, 255, 255, int(255 * a)), anchor="mm", direction="rtl",
           language="fa", stroke_width=6, stroke_fill=(15, 15, 15, int(255 * a)))
    d.text((W // 2, y + 80), CHANNEL, font=font(64), fill=(255, 210, 90, int(255 * a)), anchor="mm",
           stroke_width=6, stroke_fill=(15, 15, 15, int(255 * a)))
    return Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB")


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
    return big_credit(img, a, H - 330)


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
    # fisheye-style barrel distortion, then zoom in to hide the bent borders (as in «واگن آخر»); the black gap
    # between the fall and waking up has no frames: fill it with copies so the numbering stays continuous
    part = float(os.environ.get("PART", "0"))     # PART=20 -> only the first 20 s, as a preview (year1500_part.mp4)
    n_pic = int((part or END) * FPS)
    fill = os.path.join(TMP, "fill")
    os.makedirs(fill)
    last = None
    for f in range(1, n_pic + 1):
        p = os.path.join(SRC, f"f_{f:04d}.png")
        if os.path.exists(p):
            last = p
        if last:
            os.symlink(os.path.abspath(last), os.path.join(fill, f"f_{f:04d}.png"))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-start_number", "1",
                    "-i", os.path.join(fill, "f_%04d.png"), "-frames:v", str(n_pic),
                    "-vf", f"lenscorrection=k1=0.22:k2=0.05:i=bilinear,scale={int(W * 1.2)}:{int(H * 1.2)}:flags=lanczos,"
                           f"crop={W}:{H}", "-start_number", "1", os.path.join(TMP, "d_%04d.png")], check=True)
    shutil.rmtree(fill)
    vig = vignette()
    black = Image.new("RGB", (W, H))
    total = n_pic + (0 if part else int(CARD * FPS))
    for i in range(total):
        t = i / FPS
        f = i + 1
        if i < n_pic:
            p = os.path.join(SRC, f"f_{f:04d}.png")
            q = os.path.join(TMP, f"d_{f:04d}.png")
            if os.path.exists(q) and not (FB1 <= t < WAKE):
                img = Image.open(q).convert("RGB")
                os.remove(q)
            else:
                img = black.copy()
            if FB0 <= t < FB1:
                img = grade_flashback(img)
                if t > FB1 - 0.7:                                   # white flash, then black
                    u = (t - (FB1 - 0.7)) / 0.7
                    img = Image.blend(img, Image.new("RGB", (W, H), (255, 255, 255)), min(1.0, u * 1.6))
            if WAKE <= t < WAKE + 2.4:                              # my eyes open: lids, a blink
                img = eyelids(img, t - WAKE)
            if FB0 - 0.15 <= t < FB0 + 0.25:                        # a soft white dip into the memory
                u = 1 - abs(t - (FB0 + 0.05)) / 0.2
                img = Image.blend(img, Image.new("RGB", (W, H), (255, 250, 240)), max(0.0, u) * 0.8)
            img = Image.composite(img, Image.blend(black, img, 0.55), vig)
            if t < 6.8:
                img = title(img, t)
                img = big_credit(img, min(1.0, (t - 1.0) / 0.8, (6.6 - t) / 0.6), 760)
            elif t > 7.2:
                badge(img)
            fade = min(1.0, max(0.0, (END - t) / 0.8))
            if fade < 1:
                img = Image.blend(black, img, fade)
        else:
            img = card(t - n_pic / FPS)
        if i < n_pic:
            img = credit(img)
        img.save(os.path.join(TMP, f"n_{i:04d}.jpg"), quality=94)
        if i < n_pic:
            for a, b, who, text in LINES:
                if a <= t <= b:
                    caption(img, who, text, min(1.0, (t - a) / 0.15))
        img.save(os.path.join(TMP, f"c_{i:04d}.jpg"), quality=94)
    mix = os.path.join(OUT, "year1500_mix.wav")
    if part:
        sfx = mix if os.path.exists(mix) else os.path.join(OUT, "year1500_sfx.wav")
        encode(os.path.join(TMP, "c_%04d.jpg"), os.path.join(OUT, "year1500_part.mp4"),
               sfx if os.path.exists(sfx) else None)
        shutil.rmtree(TMP, ignore_errors=True)
        return
    encode(os.path.join(TMP, "c_%04d.jpg"), os.path.join(OUT, "year1500_captions.mp4"))
    encode(os.path.join(TMP, "n_%04d.jpg"), os.path.join(OUT, "year1500_clean.mp4"))
    sfx = os.path.join(OUT, "year1500_sfx.wav")
    if os.path.exists(sfx):
        encode(os.path.join(TMP, "c_%04d.jpg"), os.path.join(OUT, "year1500_sfx.mp4"), sfx)
    if os.path.exists(mix):                                         # the finished film: ElevenLabs voices + sfx
        encode(os.path.join(TMP, "c_%04d.jpg"), os.path.join(OUT, "year1500.mp4"), mix)
    shutil.rmtree(TMP, ignore_errors=True)


if __name__ == "__main__":
    main()
