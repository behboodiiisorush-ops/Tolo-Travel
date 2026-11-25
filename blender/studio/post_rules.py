"""Post for «قانون‌ها»: upscale + light fisheye, Persian captions, fade to black, question card.
    out/rules_captions.mp4   captions, no sound (for the user's ElevenLabs voices)
    out/rules_clean.mp4      no captions, no sound
    out/rules_sfx.mp4        captions + synthesised sound effects (if out/rules_sfx.wav exists)
"""
import os, shutil, subprocess, sys
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from captions import LINES, NAMES, END, QUESTION  # noqa: E402
FONT = os.path.join(HERE, "..", "fonts", "Vazirmatn-FD-ExtraBold.ttf")
FPS, W, H = 24, 1080, 1920
CARD = 4.0
SRC = os.path.join(HERE, "frames", "rules")
TMP, OUT = os.path.join(HERE, "post_tmp", "rules"), os.path.join(HERE, "out")
COL = {"arian": (140, 220, 120), "me": (255, 220, 90), "nina": (150, 200, 255), "intruder": (255, 120, 110),
       "police": (120, 170, 255), "rule": (255, 70, 80)}


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


def main():
    shutil.rmtree(TMP, ignore_errors=True)
    os.makedirs(TMP)
    os.makedirs(OUT, exist_ok=True)
    n_pic = int(END * FPS)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-i", os.path.join(SRC, "f_%04d.png"),
                    "-frames:v", str(n_pic),
                    "-vf", f"scale={W}:{H}:flags=lanczos,lenscorrection=k1=0.1:k2=0.02:i=bilinear,"
                           f"scale={int(W * 1.08)}:{int(H * 1.08)},crop={W}:{H},vignette=PI/5",
                    "-q:v", "2", os.path.join(TMP, "u_%04d.jpg")], check=True)
    names = sorted(n for n in os.listdir(TMP) if n.startswith("u_"))
    total = len(names) + int(CARD * FPS)
    for i in range(total):
        t = i / FPS
        if i < len(names):
            img = Image.open(os.path.join(TMP, names[i])).convert("RGB")
            os.remove(os.path.join(TMP, names[i]))      # keep the disk small
            fade = min(1.0, max(0.0, (END - t) / 0.6))
            if fade < 1:
                img = Image.blend(Image.new("RGB", img.size), img, fade)
        else:
            img = card(t - len(names) / FPS)
        img.save(os.path.join(TMP, f"n_{i:04d}.jpg"), quality=95)
        for a, b, who, text in LINES:
            if a <= t <= b and i < len(names):
                caption(img, who, text)
        img.save(os.path.join(TMP, f"c_{i:04d}.jpg"), quality=95)
    encode(os.path.join(TMP, "c_%04d.jpg"), os.path.join(OUT, "rules_captions.mp4"))
    encode(os.path.join(TMP, "n_%04d.jpg"), os.path.join(OUT, "rules_clean.mp4"))
    sfx = os.path.join(OUT, "rules_sfx.wav")
    if os.path.exists(sfx):
        encode(os.path.join(TMP, "c_%04d.jpg"), os.path.join(OUT, "rules_sfx.mp4"), sfx)
    shutil.rmtree(TMP, ignore_errors=True)


if __name__ == "__main__":
    main()
