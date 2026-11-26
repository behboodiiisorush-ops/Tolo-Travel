"""Preview of «دیوار» while the render is still running: post.py on the frames that exist so far
-> out/preview/wall_captions.mp4 (+ wall_sfx.mp4 with the effects), no question card."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import post
n = 0
while os.path.exists(os.path.join(post.SRC, f"f_{n + 1:04d}.png")):
    n += 1
n = min(n, int(os.environ.get("PREVIEW_FRAMES", n)))
post.END = n / post.FPS
post.CARD = 0
post.TMP = os.path.join(HERE, "post_tmp_preview")
post.OUT = os.path.join(HERE, "out", "preview")
sfx = os.path.join(HERE, "out", "wall_sfx.wav")
os.makedirs(post.OUT, exist_ok=True)
if os.path.exists(sfx):
    os.system(f"cp '{sfx}' '{post.OUT}/wall_sfx.wav'")
print("frames", n)
post.main()
