"""Arin's phone screen for CH01_SC002, one PNG per scene frame (1081–2684) -> out/sc002_screen/s_####.png.
Plain python3 + Pillow (no Blender). Uses Nika's video frames (out/sc002_video/f_####.png, else prev_####.png).

 1081–1248  paused on the first video frame, play icon; he dims the screen (~1190)
 1249–1964  the video plays (video frames 1–716), progress bar + time
 1965–2068  the video has cut to black (abrupt end), time 00:30
 2069–2088  he drags the scrubber back one second (frames run backwards fast)
 2089–2113  the last second again (video 692–716)
 2114–2684  paused on the last frame (her face, very close), pause icon — the glow the Driver turns towards
"""
import os, sys
from PIL import Image, ImageDraw, ImageFont, ImageEnhance

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out", "sc002_screen")
VID = os.path.join(HERE, "out", "sc002_video")
FONT = os.path.join(HERE, "..", "..", "..", "fonts", "Vazirmatn-FD-ExtraBold.ttf")
W, H = 540, 1170
F0, F1, VS, VN = 1081, 2684, 1249, 716
B0, S0, R0, P0 = 1965, 2069, 2089, 2114        # black, scrub, replay, paused
_cache = {}


def video(vf):
    vf = max(1, min(VN, vf))
    for name in (f"f_{vf:04d}.png", f"prev_{vf:04d}.png", f"prev_{vf - 1:04d}.png" if vf > 1 else "none"):
        p = os.path.join(VID, name)
        if os.path.exists(p):
            if p not in _cache:
                _cache.clear()
                _cache[p] = Image.open(p).convert("RGB").resize((540, 960))
            return _cache[p]
    return Image.new("RGB", (540, 960), (60, 62, 60))


def frame(sf):
    im = Image.new("RGB", (W, H), (0, 0, 0))
    d = ImageDraw.Draw(im)
    bright = 1.0
    state, vf = "play", 1
    if sf < VS:
        state, vf = "paused", 1
        bright = 1.0 if sf < 1190 else max(0.55, 1.0 - (sf - 1190) / 20 * 0.45)
    elif sf < VS + VN:
        vf = sf - VS + 1
    elif sf < S0:
        state, vf = "black", VN
    elif sf < R0:
        state, vf = "scrub", int(VN - (sf - S0 + 1) / (R0 - S0) * 24)
    elif sf < P0:
        vf = VN - 24 + (sf - R0)
    else:
        state, vf = "paused", VN
    if sf >= VS:
        bright = 0.55
    if state != "black":
        v = video(vf)
        if bright < 1.0:
            v = ImageEnhance.Brightness(v).enhance(bright)
        im.paste(v, (0, (H - 960) // 2))
    # player UI (no app name, no logo)
    y = H - 70
    d.rectangle([30, y, W - 30, y + 5], fill=(90, 90, 95))
    prog = 1.0 if state == "black" else (vf - 1) / (VN - 1)
    x = 30 + (W - 60) * prog
    d.rectangle([30, y, x, y + 5], fill=(225, 225, 230))
    d.ellipse([x - 9, y - 7, x + 9, y + 11], fill=(240, 240, 245))
    secs = int(round((VN if state == "black" else vf) / 24))
    f = ImageFont.truetype(FONT, 26)
    d.text((30, y + 16), f"00:{secs:02d}", font=f, fill=(200, 200, 205))
    d.text((W - 30, y + 16), f"00:{round(VN / 24):02d}", font=f, fill=(200, 200, 205), anchor="ra")
    if state == "paused":
        cx, cy = W // 2, H // 2
        d.ellipse([cx - 46, cy - 46, cx + 46, cy + 46], fill=(0, 0, 0, 120), outline=(230, 230, 235), width=3)
        if vf == 1:
            d.polygon([(cx - 14, cy - 22), (cx - 14, cy + 22), (cx + 24, cy)], fill=(235, 235, 240))
        else:
            d.rectangle([cx - 16, cy - 20, cx - 6, cy + 20], fill=(235, 235, 240))
            d.rectangle([cx + 6, cy - 20, cx + 16, cy + 20], fill=(235, 235, 240))
    return im


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    a = int(sys.argv[1]) if len(sys.argv) > 1 else F0
    b = int(sys.argv[2]) if len(sys.argv) > 2 else F1
    for sf in range(a, b + 1):
        frame(sf).save(os.path.join(OUT, f"s_{sf:04d}.png"), compress_level=1)
    print("screen frames", a, b)
