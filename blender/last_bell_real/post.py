"""Final film for the realistic «زنگ آخر».

frames/ (540x960) -> 1080x1920, phone screens + Persian captions (same as the cartoon) + the question card.
Outputs (all 80 s):
  out/last_bell_real.mp4        captions, no sound (for the user's own voices)
  out/last_bell_real_clean.mp4  no captions, no sound
  out/last_bell_real_sfx.mp4    captions + the synthesised sound effects of the cartoon (same timeline)
"""
import os, sys, shutil, subprocess
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SP = os.path.join(HERE, "..", "school_pov")
sys.path.insert(0, SP)
import post as base  # noqa: E402  (the cartoon's caption / phone / card drawing)

FPS, LAST, CARD = 24, 1800, 5
TMP = os.path.join(HERE, "post_tmp")
OUT = os.path.join(HERE, "out")


def encode(pattern, out, audio=None):
    cmd = ["ffmpeg", "-loglevel", "error", "-y", "-framerate", str(FPS), "-i", pattern]
    if audio:
        cmd += ["-i", audio, "-map", "0:v", "-map", "1:a", "-c:a", "aac", "-b:a", "192k", "-shortest"]
    cmd += ["-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "19", "-movflags", "+faststart", out]
    subprocess.run(cmd, check=True)
    print(out)


def main():
    if os.path.exists(TMP):
        shutil.rmtree(TMP)
    os.makedirs(TMP)
    os.makedirs(OUT, exist_ok=True)
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-framerate", str(FPS), "-start_number", "1",
                    "-i", os.path.join(HERE, "frames", "f_%04d.png"), "-frames:v", str(LAST),
                    "-vf", "scale=1080:1920:flags=lanczos,unsharp=5:5:0.4", os.path.join(TMP, "u_%04d.png")], check=True)
    names = sorted(n for n in os.listdir(TMP) if n.startswith("u_"))
    i = 0
    for n in names:
        t = i / FPS
        img = Image.open(os.path.join(TMP, n)).convert("RGB")
        clean = base.phone_overlay(img.copy(), t)
        clean.save(os.path.join(TMP, f"k_{i:04d}.png"))
        base.overlay(img, t).save(os.path.join(TMP, f"c_{i:04d}.png"))
        i += 1
    last = Image.open(os.path.join(TMP, names[-1])).convert("RGB")
    for j in range(CARD * FPS):
        card = base.choice_card(last.copy(), min(1.0, j / 12))
        card.save(os.path.join(TMP, f"c_{i:04d}.png"))
        card.save(os.path.join(TMP, f"k_{i:04d}.png"))
        i += 1
    encode(os.path.join(TMP, "c_%04d.png"), os.path.join(OUT, "last_bell_real.mp4"))
    encode(os.path.join(TMP, "k_%04d.png"), os.path.join(OUT, "last_bell_real_clean.mp4"))
    sfx = os.path.join(SP, "out", "sfx.wav")
    if os.path.exists(sfx):
        encode(os.path.join(TMP, "c_%04d.png"), os.path.join(OUT, "last_bell_real_sfx.mp4"), sfx)


if __name__ == "__main__":
    main()
