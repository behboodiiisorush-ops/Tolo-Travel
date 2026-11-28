"""Post for the «خیاط کوچولو» style test: character layer (on twos) over the painted plate, line boil,
impact lines + shake, sparkles, old-film grade (warmth, grain, gate weave, flicker, dust), word-by-word
Persian captions (Vazirmatn + raqm), 1080x1920 mp4 without sound.

    python3 post.py            -> out/tailor_test.mp4  (and out/tailor_test_nocap.mp4)
"""
import json, math, os, random, subprocess, shutil
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
W, H, OW, OH, N, FPS = 720, 1280, 1080, 1920, 156, 24
PLATE = Image.open(os.path.join(HERE, "plate.png")).convert("RGBA")
MARKS = json.load(open(os.path.join(HERE, "marks.json")))
FONT = ImageFont.truetype(os.path.join(HERE, "..", "fonts", "Vazirmatn-FD-ExtraBold.ttf"), 76)

# narration, word by word: (frame the word appears, word); a line stays until its end frame
LINES = [((4, 36), [(4, "یه"), (10, "خیاط"), (18, "کوچولو...")]),
         ((40, 66), [(40, "و"), (44, "یه"), (48, "عالمه"), (56, "مگس!")]),
         ((72, 100), [(72, "با"), (78, "یک"), (84, "ضربه...")]),
         ((106, 156), [(108, "هفت"), (116, "تا!")])]


def smooth_noise(seed, scale, w=W, h=H):
    r = np.random.default_rng(seed)
    g = r.random((int(h / scale) + 3, int(w / scale) + 3)).astype(np.float32)
    return np.asarray(Image.fromarray(g).resize((w, h), Image.BICUBIC), np.float32) - 0.5


def boil(img, d):
    """Hand-drawn line boil: every drawing is redrawn slightly differently (sub-pixel warp)."""
    a = np.asarray(img, np.float32)
    dx = smooth_noise(1000 + d, 26) * 2.6
    dy = smooth_noise(2000 + d, 26) * 2.6
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    x = np.clip(xx + dx, 0, W - 1.001)
    y = np.clip(yy + dy, 0, H - 1.001)
    x0, y0 = x.astype(np.int32), y.astype(np.int32)
    fx, fy = (x - x0)[..., None], (y - y0)[..., None]
    out = (a[y0, x0] * (1 - fx) * (1 - fy) + a[y0, x0 + 1] * fx * (1 - fy) + a[y0 + 1, x0] * (1 - fx) * fy
           + a[y0 + 1, x0 + 1] * fx * fy)
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), "RGBA")


def star(draw, cx, cy, r, fill, width=3):
    pts = []
    for k in range(8):
        rr = r if k % 2 == 0 else r * 0.32
        a = math.pi / 4 * k - math.pi / 2
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    draw.polygon(pts, fill=fill, outline=(20, 15, 12, 255), width=width)


def effects(img, f, d):
    m = MARKS[str(d)]
    dr = ImageDraw.Draw(img)
    ix, iy = m["impact"]
    if d == 68:                                  # smear drawing: speed lines along the swing
        for k in range(5):
            o = (k - 2) * 26
            dr.line([(ix - 40 + o, iy - 560), (ix - 10 + o * 0.6, iy - 320), (ix + o * 0.3, iy - 120)],
                    fill=(30, 22, 18, 255), width=max(2, 6 - abs(k - 2) * 2))
    if 70 <= d <= 76:                            # impact burst
        rnd = random.Random(d)
        for k in range(14):
            a = math.pi * (1.05 + 0.9 * k / 13) + rnd.uniform(-0.06, 0.06)
            r0, r1 = 110 + rnd.uniform(0, 30), 190 + rnd.uniform(0, 60) + (76 - d) * 8
            dr.line([(ix + r0 * math.cos(a), iy + r0 * math.sin(a) * 0.7),
                     (ix + r1 * math.cos(a), iy + r1 * math.sin(a) * 0.7)], fill=(30, 22, 18, 255), width=5)
    if d >= 134:                                 # proud sparkles round his head
        hx, hy = m["head"]
        for k, (ox, oy, ph) in enumerate(((-170, -150, 0), (170, -190, 2), (200, -40, 4), (-200, -10, 6))):
            s = 0.5 + 0.5 * math.sin((d - 134) * 0.45 + ph)
            if s > 0.15:
                star(dr, hx + ox, hy + oy, 14 + 18 * s, (255, 222, 90, 255))
    return img


def shake(d):
    return {70: (9, -6), 72: (-7, 5), 74: (4, -3)}.get(d, (0, 0))


def grade(rgb, f, d):
    a = np.asarray(rgb, np.float32) / 255
    a = a * np.array([1.05, 1.0, 0.88], np.float32)                         # warm technicolour print
    lum = a.mean(-1, keepdims=True)
    a = lum + (a - lum) * 1.12
    a = np.clip(a, 0, 1)
    a = a * a * (3 - 2 * a) * 0.35 + a * 0.65                                 # gentle S-curve
    r = np.random.default_rng(f)
    g = r.normal(0, 0.035, (OH // 2, OW // 2)).astype(np.float32)
    g = np.asarray(Image.fromarray(g).resize((OW, OH), Image.BILINEAR), np.float32)
    a = a + g[..., None] * (0.6 + 0.4 * (1 - a))
    a *= 1 + 0.02 * math.sin(f * 2.1) + 0.012 * r.normal()                   # projector flicker
    yy, xx = np.mgrid[0:OH, 0:OW].astype(np.float32)
    vig = 1 - 0.30 * (((xx - OW / 2) / (OW * 0.72)) ** 2 + ((yy - OH / 2) / (OH * 0.72)) ** 2)
    a *= vig[..., None]
    img = Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))
    rr = random.Random(f * 7 + 3)
    if rr.random() < 0.35:                                                    # dust and hair on the print
        dr = ImageDraw.Draw(img)
        for _ in range(rr.randint(1, 3)):
            x, y, s = rr.uniform(0, OW), rr.uniform(0, OH), rr.uniform(2, 6)
            dr.ellipse((x, y, x + s, y + s * rr.uniform(0.6, 1.4)), fill=(25, 20, 16))
        if rr.random() < 0.3:
            x = rr.uniform(0, OW)
            dr.line([(x, rr.uniform(0, OH)), (x + rr.uniform(-6, 6), rr.uniform(0, OH))], fill=(235, 225, 200),
                    width=1)
    return img


def caption(img, f):
    for (a, b), words in LINES:
        if not (a <= f < b):
            continue
        shown = [w for t, w in words if f >= t]
        if not shown:
            return img
        text = " ".join(shown)
        full = " ".join(w for _, w in words)
        dr = ImageDraw.Draw(img)
        fw = dr.textlength(full, font=FONT, direction="rtl", language="fa")
        x0 = (OW + fw) / 2                                                    # right edge of the full line
        tw = dr.textlength(text, font=FONT, direction="rtl", language="fa")
        last = shown[-1]
        age = f - max(t for t, w in words if f >= t)
        pop = 1.0 + 0.18 * max(0, 1 - age / 4)                                # new word pops in
        y = int(OH * 0.80)
        if len(shown) > 1:
            prev = " ".join(shown[:-1])
            dr.text((x0, y), prev, font=FONT, fill=(255, 246, 225), anchor="rs", direction="rtl", language="fa",
                    stroke_width=7, stroke_fill=(25, 18, 14))
            pw = dr.textlength(prev + " ", font=FONT, direction="rtl", language="fa")
        else:
            pw = 0
        f2 = ImageFont.truetype(FONT.path, int(76 * pop))
        dr.text((x0 - pw, y), last, font=f2, fill=(255, 214, 70), anchor="rs", direction="rtl", language="fa",
                stroke_width=7, stroke_fill=(25, 18, 14))
    return img


def main():
    tmp = os.path.join(HERE, "post_tmp")
    shutil.rmtree(tmp, ignore_errors=True)
    os.makedirs(tmp + "/c"); os.makedirs(tmp + "/n")
    cache = {}
    for f in range(N):
        d = f - f % 2
        if d not in cache:
            layer = Image.open(os.path.join(HERE, "layer", "d_%04d.png" % d)).convert("RGBA")
            frame = PLATE.copy()
            frame.alpha_composite(boil(layer, d))
            frame = effects(frame, f, d)
            sx, sy = shake(d)
            wx, wy = random.Random(d).choice([(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1)])   # gate weave
            moved = Image.new("RGBA", (W, H), (20, 14, 10, 255))
            moved.alpha_composite(frame, (sx + wx, sy + wy))
            cache = {d: moved.convert("RGB").resize((OW, OH), Image.LANCZOS)}
        base = grade(cache[d], f, d)
        base.save(os.path.join(tmp, "n", "%04d.png" % f))
        caption(base, f).save(os.path.join(tmp, "c", "%04d.png" % f))
    os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
    for sub, name in (("c", "tailor_test.mp4"), ("n", "tailor_test_nocap.mp4")):
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-framerate", str(FPS), "-i",
                        os.path.join(tmp, sub, "%04d.png"), "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p",
                        "-movflags", "+faststart", os.path.join(HERE, "out", name)], check=True)
    print("done")


if __name__ == "__main__":
    main()
