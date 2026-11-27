"""Post for «سایه‌ی دانیال» (EP_002): upscale, Persian captions, fade to black, question card.
    out/sayeh_captions.mp4   captions, no sound (for the user's ElevenLabs voices)
    out/sayeh_clean.mp4      no captions, no sound
    out/sayeh_sfx.mp4        captions + synthesised sound effects (if out/sayeh_sfx.wav exists)
"""
import os, shutil, subprocess, sys
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from lines import LINES, NAMES, END, QUESTION, COLD, COLD_CARD  # noqa: E402
FONT = os.path.join(HERE, "..", "..", "..", "fonts", "Vazirmatn-FD-ExtraBold.ttf")
FPS, W, H = 24, 1080, 1920
CARD = 4.0
SRC = os.path.join(HERE, "frames")
TMP, OUT = os.path.join(HERE, "post_tmp"), os.path.join(HERE, "out")
COL = {"mother": (255, 150, 170), "father": (150, 200, 255), "arian": (140, 220, 120), "lina": (255, 210, 120),
       "daniel": (255, 120, 100)}


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


def caption(img, who, text, alpha=1.0):
    d = ImageDraw.Draw(img)
    f, fs = font(76), font(44)
    lines = wrap(d, text, f, W - 140)
    y = 1330 - 45 * (len(lines) - 1)
    if who == "rule":
        box = (60, y - 135, W - 60, y + 95 * len(lines) - 20)
        ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
        ImageDraw.Draw(ov).rounded_rectangle(box, 30, fill=(10, 10, 14, 170), outline=(230, 40, 50, 255), width=5)
        img.paste(Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB"))
        d = ImageDraw.Draw(img)
    d.text((W // 2, y - 80), NAMES[who], font=fs, fill=COL[who], anchor="mm", direction="rtl", language="fa",
           stroke_width=6, stroke_fill=(0, 0, 0))
    for k, ln in enumerate(lines):
        d.text((W // 2, y + k * 92), ln, font=f, fill=(255, 255, 255), anchor="mm", direction="rtl", language="fa",
               stroke_width=9, stroke_fill=(0, 0, 0))


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


def title_card(t, text):
    img = Image.new("RGB", (W, H), (0, 0, 0))
    d = ImageDraw.Draw(img)
    a = min(1.0, t / 0.3)
    c = int(235 * a)
    d.text((W // 2, H // 2), text, font=font(80), fill=(c, c, c), anchor="mm", direction="rtl", language="fa")
    return img


def night(img, t):
    """The render's dim light was too weak: grade the blackout (7.2 s .. the flash at 27 s) dark and moonlit blue."""
    if 5.0 <= t < 7.0:                                   # the lights flicker (same pattern as render.py)
        pat = [1, .15, 1, 1, .1, .6, .05, 1, .1, .1, .7, .05, .05, .4, .05, .05]
        k = 1 - pat[int((t - 5.0) * 7) % len(pat)]
    elif t < 7.0 or t >= 27.6:
        return img
    else:
        k = min(1.0, (t - 7.0) / 0.25) if t < 27.0 else max(0.0, 1 - (t - 27.0) / 0.6)
    r, g, b = img.split()
    m = [(1 - k) + k * c for c in (0.40, 0.47, 0.66)]
    return Image.merge("RGB", [ch.point(lambda v, q=q: int(v * q)) for ch, q in zip((r, g, b), m)])


def timeline():
    """(kind, film_time) per output frame: cold open, card, the film, question card."""
    out = [("film", COLD[0] + i / FPS) for i in range(int((COLD[1] - COLD[0]) * FPS))]
    out += [("cold", i / FPS) for i in range(int(COLD_CARD[0] * FPS))]
    out += [("film", i / FPS) for i in range(int(END * FPS))]
    out += [("card", i / FPS) for i in range(int(CARD * FPS))]
    return out


def main():
    shutil.rmtree(TMP, ignore_errors=True)
    os.makedirs(TMP)
    os.makedirs(OUT, exist_ok=True)
    n_pic = int(END * FPS)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-i", os.path.join(SRC, "f_%04d.png"),
                    "-frames:v", str(n_pic), "-vf", f"scale={W}:{H}:flags=lanczos,vignette=PI/6",
                    "-q:v", "2", os.path.join(TMP, "u_%04d.jpg")], check=True)
    n_have = len([n for n in os.listdir(TMP) if n.startswith("u_")])
    tl = timeline()
    first_film = int((COLD[1] - COLD[0]) * FPS) + int(COLD_CARD[0] * FPS)
    for i, (kind, t) in enumerate(tl):
        if kind == "film":
            k = min(n_have, int(round(t * FPS)) + 1)
            img = night(Image.open(os.path.join(TMP, f"u_{k:04d}.jpg")).convert("RGB"), t)
            if i >= first_film:
                fade = min(1.0, max(0.0, (END - t) / 0.6), (i - first_film + 1) / 8)
            else:
                fade = min(1.0, i / 6, max(0.0, (COLD[1] - t) / 0.4))
            if fade < 1:
                img = Image.blend(Image.new("RGB", img.size), img, max(0.0, fade))
        elif kind == "cold":
            img = title_card(t, COLD_CARD[1])
        else:
            img = card(t)
        img.save(os.path.join(TMP, f"n_{i:04d}.jpg"), quality=95)
        if kind == "film":
            for a, b, who, text in LINES:
                if a <= t <= b:
                    caption(img, who, text)
        img.save(os.path.join(TMP, f"c_{i:04d}.jpg"), quality=95)
    for n in os.listdir(TMP):
        if n.startswith("u_"):
            os.remove(os.path.join(TMP, n))
    encode(os.path.join(TMP, "c_%04d.jpg"), os.path.join(OUT, "sayeh_captions.mp4"))
    encode(os.path.join(TMP, "n_%04d.jpg"), os.path.join(OUT, "sayeh_clean.mp4"))
    sfx = os.path.join(OUT, "sayeh_sfx.wav")
    if os.path.exists(sfx):
        encode(os.path.join(TMP, "c_%04d.jpg"), os.path.join(OUT, "sayeh_sfx.mp4"), sfx)
    shutil.rmtree(TMP, ignore_errors=True)


if __name__ == "__main__":
    main()
