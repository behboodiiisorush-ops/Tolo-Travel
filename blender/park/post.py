"""Post for «پارک»: frames (any size) -> 1080x1920, bouncy title at the start, fade in/out, music + sfx.

    python3 post.py [frames_dir]     -> out/park.mp4 (title + sound), out/park_notitle.mp4 (sound, no title)
"""
import math, os, shutil, subprocess, sys
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "frames")
OW, OH, FPS, NF = 1080, 1920, 24, 1440
FONT = os.path.join(HERE, "..", "fonts", "Vazirmatn-FD-ExtraBold.ttf")
TITLE = "یه روز توی پارک"


def title(img, t):
    if not (0.3 <= t < 4.0):
        return img
    u = (t - 0.3) / 0.45
    s = 1.0 if u >= 1 else max(0.01, math.sin(min(1, u) * math.pi * 0.5) * (1 + 0.25 * math.sin(u * math.pi)))
    a = min(1.0, (4.0 - t) / 0.4)
    size = int(130 * s)
    if size < 8:
        return img
    f = ImageFont.truetype(FONT, size)
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    y = int(OH * 0.2) + int(10 * math.sin(t * 3))
    d.text((OW // 2, y), TITLE, font=f, anchor="mm", fill=(255, 210, 60, int(255 * a)), direction="rtl",
           language="fa", stroke_width=max(2, size // 11), stroke_fill=(120, 50, 30, int(255 * a)))
    return Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB")


def main():
    tmp = os.path.join(HERE, "post_tmp")
    shutil.rmtree(tmp, ignore_errors=True)
    os.makedirs(tmp + "/a"); os.makedirs(tmp + "/b")
    files = sorted(x for x in os.listdir(SRC) if x.endswith(".png"))
    have = {int(x[2:6]): x for x in files}
    last = None
    for f in range(NF):
        # previews may hold every 2nd frame only: reuse the previous one
        name = have.get(f) or have.get(f - 1) or last
        last = name
        img = Image.open(os.path.join(SRC, name)).convert("RGB").resize((OW, OH), Image.LANCZOS)
        t = f / FPS
        k = min(1.0, t / 0.5, (NF / FPS - t) / 0.5)
        if k < 1:
            img = Image.blend(Image.new("RGB", img.size, (255, 255, 255)), img, max(0.0, k))
        img.save(os.path.join(tmp, "b", "%04d.png" % f))
        title(img, t).save(os.path.join(tmp, "a", "%04d.png" % f))
    os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
    mix = os.path.join(HERE, "audio", "mix.wav")
    for sub, out in (("a", "park.mp4"), ("b", "park_notitle.mp4")):
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-framerate", str(FPS),
                        "-i", os.path.join(tmp, sub, "%04d.png"), "-i", mix,
                        "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", "-c:v", "libx264", "-crf", "18",
                        "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest",
                        "-movflags", "+faststart", os.path.join(HERE, "out", out)], check=True)
    print("done")


if __name__ == "__main__":
    main()
