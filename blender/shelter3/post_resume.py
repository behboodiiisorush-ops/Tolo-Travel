"""Resume post_pov.py after an interruption: finish the final-card frames, then encode (keeps post_tmp/)."""
import os, subprocess
import post_pov as P
from PIL import Image
TMP, OUT, FPS = P.TMP, P.OUT, P.FPS
n_c = len([n for n in os.listdir(TMP) if n.startswith("c_")])
n_k = len([n for n in os.listdir(TMP) if n.startswith("k_")])
i0 = min(n_c, n_k)
start = P.LAST                                  # index of the first card frame
last = Image.open(os.path.join(P.FRAMES, sorted(os.listdir(P.FRAMES))[-1])).convert("RGB").resize((P.W, P.H))
for i in range(i0, start + P.CARD_SECONDS * FPS):
    j = i - start
    card = P.final_card(last.copy(), min(1.0, j / 12))
    card.save(os.path.join(TMP, f"c_{i:05d}.png"))
    card.save(os.path.join(TMP, f"k_{i:05d}.png"))
enc = ["-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", "-movflags", "+faststart"]
cap, clean = os.path.join(OUT, "shelter3_captions.mp4"), os.path.join(OUT, "shelter3_clean.mp4")
for pre, out in (("c", cap), ("k", clean)):
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-framerate", str(FPS), "-i",
                    os.path.join(TMP, pre + "_%05d.png")] + enc + [out], check=True)
    print(out, flush=True)
for wav, name in (("sfx.wav", "shelter3_sfx.mp4"), ("voice.wav", "shelter3_voice.mp4")):
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", cap, "-i", os.path.join(OUT, wav), "-map", "0:v",
                    "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", os.path.join(OUT, name)],
                   check=True)
    print(os.path.join(OUT, name), flush=True)
print("POST_DONE", flush=True)
