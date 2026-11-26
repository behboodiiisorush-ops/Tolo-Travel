"""Post for the studio test: light fisheye, upscale, captions in the reference style -> out/studio_test.mp4"""
import os, shutil, subprocess
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__))
FONT = os.path.join(HERE, "..", "fonts", "Vazirmatn-FD-ExtraBold.ttf")
FPS, W, H = 24, 1080, 1920
SUBS = [(5.3, 6.3, "نینا", "تو اینجا چیکار می‌کنی؟"), (8.6, 9.5, "نینا", "پشت سرت!")]
TMP, OUT = os.path.join(HERE, "post_tmp"), os.path.join(HERE, "out")


def main():
    shutil.rmtree(TMP, ignore_errors=True)
    os.makedirs(TMP)
    os.makedirs(OUT, exist_ok=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-i", os.path.join(HERE, "frames", "f_%04d.png"),
                    "-vf", f"scale={W}:{H}:flags=lanczos,lenscorrection=k1=0.12:k2=0.03:i=bilinear,"
                           f"scale={int(W * 1.1)}:{int(H * 1.1)},crop={W}:{H}", os.path.join(TMP, "u_%04d.png")], check=True)
    f = ImageFont.truetype(FONT, 84, layout_engine=ImageFont.Layout.RAQM)
    fs = ImageFont.truetype(FONT, 44, layout_engine=ImageFont.Layout.RAQM)
    names = sorted(n for n in os.listdir(TMP) if n.startswith("u_"))
    for i, n in enumerate(names):
        t = i / FPS
        img = Image.open(os.path.join(TMP, n)).convert("RGB")
        d = ImageDraw.Draw(img)
        for a, b, who, text in SUBS:
            if a <= t <= b:
                d.text((W // 2, 1180), who, font=fs, fill=(255, 220, 90), anchor="mm", direction="rtl", language="fa",
                       stroke_width=6, stroke_fill=(0, 0, 0))
                d.text((W // 2, 1270), text, font=f, fill=(255, 255, 255), anchor="mm", direction="rtl", language="fa",
                       stroke_width=10, stroke_fill=(0, 0, 0))
        img.save(os.path.join(TMP, f"c_{i:04d}.png"))
    out = os.path.join(OUT, "studio_test.mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-i", os.path.join(TMP, "c_%04d.png"),
                    "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", "-movflags", "+faststart", out], check=True)
    print(out)


if __name__ == "__main__":
    main()
