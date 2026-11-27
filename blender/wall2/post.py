"""Post for «دیوار ۲»: fisheye + upscale, opening card, corner credit, Persian captions, the phone message,
fade, question card; then the ElevenLabs sound (audio.py) is laid under it.

    out/wall2_full.mp4          captions + voices + effects   (the main version)
    out/wall2_full_clean.mp4    voices + effects, no captions
    out/wall2_captions.mp4      captions, no sound
    out/wall2_clean.mp4         no captions, no sound
Every version carries the credit «ساخته شده توسط بلندر» + «agetobudi» (opening card, corner, end card).
"""
import os, shutil, subprocess, sys
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from captions import LINES, NAMES, END, QUESTION, TITLE, MESSAGE  # noqa: E402
FONTS = os.path.join(HERE, "..", "fonts")
FONT = os.path.join(FONTS, "Vazirmatn-FD-ExtraBold.ttf")
FONT_R = os.path.join(FONTS, "Vazirmatn-FD-Regular.ttf") if os.path.exists(os.path.join(FONTS, "Vazirmatn-FD-Regular.ttf")) else FONT
FPS, W, H = 24, 1080, 1920
OPEN, CARD = 3.0, 4.0
MADE, CHANNEL = "ساخته شده توسط بلندر", "agetobudi"
SRC = os.path.join(HERE, "frames")
TMP, OUT = os.path.join(HERE, "post_tmp"), os.path.join(HERE, "out")
COL = {"mom": (255, 150, 170), "kazemi": (255, 210, 120), "arian": (140, 220, 120), "mahsa": (150, 200, 255),
       "rezaei": (200, 200, 190), "kian": (255, 230, 90), "me": (255, 170, 90)}


def font(s, regular=False):
    return ImageFont.truetype(FONT_R if regular else FONT, s, layout_engine=ImageFont.Layout.RAQM)


def txt(d, xy, s, f, fill, **kw):
    fa = any("؀" <= ch <= "ۿ" for ch in s)
    d.text(xy, s, font=f, fill=fill, anchor=kw.pop("anchor", "mm"), direction="rtl" if fa else None,
           language="fa" if fa else None, **kw)


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


def credit_corner(img):
    """Small credit, top-left corner, on every frame of the film."""
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    txt(d, (40, 58), CHANNEL, font(40), (255, 255, 255, 200), anchor="lm", stroke_width=4, stroke_fill=(0, 0, 0, 160))
    txt(d, (40, 104), MADE, font(26, True), (255, 255, 255, 170), anchor="lm", stroke_width=3, stroke_fill=(0, 0, 0, 140))
    return Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB")


def caption(img, who, text):
    d = ImageDraw.Draw(img)
    f, fs = font(76), font(44)
    lines = wrap(d, text, f, W - 140)
    y = 1330 - 45 * (len(lines) - 1)
    txt(d, (W // 2, y - 80), NAMES[who], fs, COL[who], stroke_width=6, stroke_fill=(0, 0, 0))
    for k, ln in enumerate(lines):
        txt(d, (W // 2, y + k * 92), ln, f, (255, 255, 255), stroke_width=9, stroke_fill=(0, 0, 0))


def message(img, t):
    """The message on Arian's phone, as a screen insert in the upper half."""
    a0, a1, text = MESSAGE
    a = min(1.0, (t - a0) / 0.35, (a1 - t) / 0.35)
    if a <= 0:
        return img
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    al = int(255 * a)
    box = (110, 300, W - 110, 690)
    d.rounded_rectangle(box, 42, fill=(245, 247, 250, int(235 * a)), outline=(40, 40, 50, al), width=4)
    d.rounded_rectangle((box[0], box[1], box[2], box[1] + 86), 42, fill=(60, 120, 230, al))
    d.rectangle((box[0], box[1] + 50, box[2], box[1] + 86), fill=(60, 120, 230, al))
    txt(d, (W // 2, box[1] + 45), "پیام جدید", font(40), (255, 255, 255, al))
    for k, ln in enumerate(text.split("\n")):
        txt(d, (W // 2, box[1] + 170 + k * 92), ln, font(54), (20, 20, 30, al))
    return Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB")


def opening(t):
    img = Image.new("RGB", (W, H), (0, 0, 0))
    d = ImageDraw.Draw(img)
    a = max(0.0, min(1.0, t / 0.6, (OPEN - t) / 0.5))
    c = int(255 * a)
    txt(d, (W // 2, H // 2 - 120), TITLE, font(150), (c, c, c))
    txt(d, (W // 2, H // 2 + 60), MADE, font(52, True), (int(200 * a),) * 3)
    txt(d, (W // 2, H // 2 + 150), CHANNEL, font(64), (int(230 * a), int(60 * a), int(70 * a)))
    return img


def card(t):
    img = Image.new("RGB", (W, H), (0, 0, 0))
    d = ImageDraw.Draw(img)
    a = min(1.0, t / 0.8)
    f = font(84)
    lines = wrap(d, QUESTION, f, W - 160)
    y0 = H // 2 - 60 * (len(lines) - 1)
    c = int(255 * a)
    for k, ln in enumerate(lines):
        txt(d, (W // 2, y0 + k * 120), ln, f, (c, c, c))
    txt(d, (W // 2, y0 - 190), "؟", font(140), (int(230 * a), int(40 * a), int(50 * a)))
    txt(d, (W // 2, H - 260), MADE, font(42, True), (int(170 * a),) * 3)
    txt(d, (W // 2, H - 190), CHANNEL, font(56), (int(230 * a), int(60 * a), int(70 * a)))
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
                    "-vf", f"scale={W}:{H}:flags=lanczos,lenscorrection=k1=0.22:k2=0.05:i=bilinear,"
                           f"scale={int(W * 1.2)}:{int(H * 1.2)}:flags=lanczos,crop={W}:{H},vignette=PI/5",
                    "-q:v", "2", os.path.join(TMP, "u_%04d.jpg")], check=True)
    names = sorted(n for n in os.listdir(TMP) if n.startswith("u_"))
    n_open = int(OPEN * FPS)
    total = n_open + len(names) + int(CARD * FPS)
    for i in range(total):
        if i < n_open:
            img = opening(i / FPS)
            img.save(os.path.join(TMP, f"n_{i:04d}.jpg"), quality=95)
            img.save(os.path.join(TMP, f"c_{i:04d}.jpg"), quality=95)
            continue
        j = i - n_open
        t = j / FPS
        if j < len(names):
            img = Image.open(os.path.join(TMP, names[j])).convert("RGB")
            os.remove(os.path.join(TMP, names[j]))
            fade = min(1.0, max(0.0, (END - t) / 0.6), t / 0.4)
            if fade < 1:
                img = Image.blend(Image.new("RGB", img.size), img, fade)
            if MESSAGE[0] <= t <= MESSAGE[1]:
                img = message(img, t)
            img = credit_corner(img)
        else:
            img = card(t - len(names) / FPS)
        img.save(os.path.join(TMP, f"n_{i:04d}.jpg"), quality=95)
        for a, b, who, text in LINES:
            if a <= t <= b and j < len(names):
                caption(img, who, text)
        img.save(os.path.join(TMP, f"c_{i:04d}.jpg"), quality=95)
    encode(os.path.join(TMP, "c_%04d.jpg"), os.path.join(OUT, "wall2_captions.mp4"))
    encode(os.path.join(TMP, "n_%04d.jpg"), os.path.join(OUT, "wall2_clean.mp4"))
    mix = os.path.join(OUT, "wall2_mix.wav")
    if os.path.exists(mix):
        encode(os.path.join(TMP, "c_%04d.jpg"), os.path.join(OUT, "wall2_full.mp4"), mix)
        encode(os.path.join(TMP, "n_%04d.jpg"), os.path.join(OUT, "wall2_full_clean.mp4"), mix)
    shutil.rmtree(TMP, ignore_errors=True)


if __name__ == "__main__":
    main()
