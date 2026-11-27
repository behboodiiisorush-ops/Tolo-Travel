"""Post for «در رو باز نکن» — the graphic-noir look: black-and-white with hard contrast, film grain and vignette,
only RED keeps its colour (her sweater, the red buttons on the phone). POV frames get my eyes' fisheye, peephole
frames a round fish-eye lens with black around it. Persian captions, branding on every frame, question card.
    out/door_final.mp4      captions + ElevenLabs voices and effects (out/door_mix.wav from audio.py)
    out/door_captions.mp4   captions, no sound
    out/door_clean.mp4      no captions, voices and effects
    python3 post.py [--grade-test f1,f2,...]   -> test/g_XXXX.jpg (graded single frames, no video)
"""
import os, shutil, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from lines import LINES, NAMES, END, QUESTION, TITLE, PEEP, BLACK, FPS, peep  # noqa: E402
sys.path.insert(0, os.path.join(HERE, "..", "brand"))
from brand import overlay, CREDIT, CHANNEL  # noqa: E402
FONT = os.path.join(HERE, "..", "fonts", "Vazirmatn-FD-ExtraBold.ttf")
W, H = 1080, 1920
CARD = 4.0
SRC = os.path.join(HERE, "frames")
TMP, OUT = os.path.join(HERE, "post_tmp"), os.path.join(HERE, "out")
COL = {"me_msg": (200, 200, 200), "fake": (235, 40, 50), "me": (200, 200, 200), "mom": (200, 200, 200)}
POV_VF = f"scale={W}:{H}:flags=lanczos,lenscorrection=k1=0.2:k2=0.04:i=bilinear,scale={int(W * 1.18)}:{int(H * 1.18)}:flags=lanczos,crop={W}:{H}"
PEEP_VF = f"scale={W}:{H}:flags=lanczos,lenscorrection=k1=0.55:k2=0.25:i=bilinear"


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


def caption(img, who, text, t):
    d = ImageDraw.Draw(img)
    f, fs = font(74), font(42)
    lines = wrap(d, text, f, W - 140)
    y = 1400 - 45 * (len(lines) - 1)
    name = NAMES[who] if not (who == "fake" and t > 36) else "؟"
    d.text((W // 2, y - 80), name, font=fs, fill=COL[who], anchor="mm", direction="rtl", language="fa",
           stroke_width=6, stroke_fill=(0, 0, 0))
    for k, ln in enumerate(lines):
        d.text((W // 2, y + k * 90), ln, font=f, fill=(255, 255, 255), anchor="mm", direction="rtl", language="fa",
               stroke_width=9, stroke_fill=(0, 0, 0))


# ---------------------------------------------------------------- the noir grade
YY, XX = np.mgrid[0:H, 0:W]
_r = np.sqrt(((XX - W / 2) / (W / 2)) ** 2 + ((YY - H / 2) / (H / 2)) ** 2)
VIGN = np.clip(1.15 - 0.55 * _r ** 2, 0.25, 1.0)[..., None]
_pr = np.sqrt((XX - W / 2) ** 2 + (YY - H * 0.47) ** 2)
PEEP_MASK = np.clip((W * 0.47 - _pr) / 22.0, 0, 1)[..., None]                  # the round lens
PEEP_RIM = np.clip(1 - np.abs(_pr - W * 0.47) / 14.0, 0, 1)[..., None] * 0.35   # a faint glint on its rim


def noir(img, t, seed):
    a = np.asarray(img).astype(np.float32) / 255.0
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    L = 0.3 * r + 0.59 * g + 0.11 * b
    L = np.clip((L - 0.03) * 1.35, 0, 1)
    L = L * L * (3 - 2 * L) * 0.75 + L * 0.25                           # S-curve: deep blacks, hot whites
    mx, mn = a.max(-1), a.min(-1)
    sat = (mx - mn) / (mx + 1e-4)
    # hue distance from pure red (0..1 of a 60-degree sector), only saturated and not too dark
    hue = np.abs(g - b) / (mx - mn + 1e-4) * (r >= np.maximum(g, b)) + (r < np.maximum(g, b))
    red = np.clip((0.4 - hue) / 0.2, 0, 1) * np.clip((sat - 0.5) * 4, 0, 1) * np.clip((mx - 0.08) * 8, 0, 1)
    grey = np.repeat(L[..., None], 3, -1)
    col = np.stack([np.clip(r * 1.25 + 0.03, 0, 1), g * 0.35, b * 0.35], -1)
    out = grey * (1 - red[..., None]) + col * red[..., None]
    rng = np.random.default_rng(seed)
    out = out + (rng.standard_normal((H // 2, W // 2)).repeat(2, 0).repeat(2, 1)[..., None] * 0.035)
    if peep(t):
        out = out * PEEP_MASK + PEEP_RIM * np.clip(out.mean(), 0.2, 1)
    else:
        out = out * VIGN
    return Image.fromarray((np.clip(out, 0, 1) * 255).astype(np.uint8))


def card(t):
    img = Image.new("RGB", (W, H), (0, 0, 0))
    d = ImageDraw.Draw(img)
    a = min(1.0, t / 0.8)
    f = font(80)
    lines = wrap(d, QUESTION, f, W - 160)
    y0 = H // 2 - 60 * (len(lines) - 1)
    c = int(255 * a)
    for k, ln in enumerate(lines):
        d.text((W // 2, y0 + k * 120), ln, font=f, fill=(c, c, c), anchor="mm", direction="rtl", language="fa")
    d.text((W // 2, y0 - 190), "؟", font=font(140), fill=(int(230 * a), int(30 * a), int(40 * a)), anchor="mm")
    gg = int(170 * a)
    d.text((W // 2, H - 260), CHANNEL, font=font(40), fill=(gg, gg, gg), anchor="mm")
    return img


def delivered(img, t):
    """45.2-47: the payoff the phone shows, big enough to read: «تحویل: دیروز ۲۳:۵۸»."""
    if not 45.3 <= t < END:
        return
    a = min(1.0, (t - 45.3) / 0.4)
    d = ImageDraw.Draw(img)
    d.text((W // 2, 1450), "تحویل: دیروز ۲۳:۵۸", font=font(78), fill=(int(235 * a), int(30 * a), int(40 * a)),
           anchor="mm", direction="rtl", language="fa", stroke_width=8, stroke_fill=(0, 0, 0))


def encode(pattern, out, audio=None):
    cmd = ["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-i", pattern]
    if audio:
        cmd += ["-i", audio, "-c:a", "aac", "-b:a", "192k", "-shortest"]
    cmd += ["-vf", "scale=720:1280:flags=lanczos", "-c:v", "libx264", "-crf", "27", "-preset", "slow", "-tune", "grain",
            "-pix_fmt", "yuv420p", "-movflags", "+faststart", out]          # the grain is heavy: 720p keeps it ~20 MB
    subprocess.run(cmd, check=True)
    print(out)


def upscale(src_png, t, dst):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src_png, "-vf", PEEP_VF if peep(t) else POV_VF,
                    "-q:v", "2", dst], check=True)


def frame(i, t, src_dir=SRC):
    """Graded film frame i (1-based render frame) at film time t."""
    if BLACK[0] <= t < BLACK[1]:
        return Image.new("RGB", (W, H))
    dst = os.path.join(TMP, "u.jpg")
    upscale(os.path.join(src_dir, f"f_{i:04d}.png"), t, dst)
    img = noir(Image.open(dst).convert("RGB"), t, i)
    fade = min(1.0, max(0.0, (END - t) / 0.6), max(0.0, (BLACK[0] - t) / 0.12) if t < BLACK[0] else 1.0,
               (t - BLACK[1]) / 0.5 if t >= BLACK[1] else 1.0, (t + 0.04) / 0.25)
    for a, b in PEEP:                                              # a dip to black at every peephole cut
        for c in (a, b):
            fade = min(fade, 0.35 + 0.65 * min(1.0, abs(t - c) / 0.12))
    if fade < 1:
        img = Image.blend(Image.new("RGB", img.size), img, max(0.0, fade))
    return img


def main():
    args = sys.argv
    os.makedirs(TMP, exist_ok=True)
    if "--grade-test" in args:
        src = os.path.join(HERE, "test")
        for f in [int(v) for v in args[args.index("--grade-test") + 1].split(",")]:
            t = (f - 1) / FPS
            shutil.copy(os.path.join(src, f"s_{f:04d}.png"), os.path.join(TMP, f"f_{f:04d}.png"))
            img = frame(f, t, TMP)
            overlay(img, TITLE)
            for a, b, who, text, *_ in LINES:
                if a <= t <= b:
                    caption(img, who, text, t)
            img.resize((540, 960)).save(os.path.join(src, f"g_{f:04d}.jpg"), quality=90)
        shutil.rmtree(TMP, ignore_errors=True)
        return
    shutil.rmtree(TMP, ignore_errors=True)
    os.makedirs(TMP)
    os.makedirs(OUT, exist_ok=True)
    n_film = int(END * FPS)
    total = n_film + int(CARD * FPS)
    for i in range(total):
        t = i / FPS
        img = frame(i + 1, t) if i < n_film else card(t - END)
        overlay(img, TITLE)
        img.save(os.path.join(TMP, f"n_{i:04d}.jpg"), quality=94)
        if i < n_film:
            delivered(img, t)
            for a, b, who, text, *_ in LINES:
                if a <= t <= b:
                    caption(img, who, text, t)
        img.save(os.path.join(TMP, f"c_{i:04d}.jpg"), quality=94)
        if i % 100 == 0:
            print("post", i, "/", total, flush=True)
    mix = os.path.join(OUT, "door_mix.wav")
    encode(os.path.join(TMP, "c_%04d.jpg"), os.path.join(OUT, "door_final.mp4"), mix)
    encode(os.path.join(TMP, "c_%04d.jpg"), os.path.join(OUT, "door_captions.mp4"))
    encode(os.path.join(TMP, "n_%04d.jpg"), os.path.join(OUT, "door_clean.mp4"), mix)
    shutil.rmtree(TMP, ignore_errors=True)


if __name__ == "__main__":
    main()
