"""Every frame of the big screen in «سال ۱۵۰۰» -> screen/s_XXXX.png (480x270, one per film frame).
  flashback   calm moving colour bands (the new city's screen, no text, no logos)
  the fall    glitch: torn bars, noise
  present     dead and cracked; 33 s it crackles (static, rolling bars), 37-45 s the home video (screen/mom_*.png,
              from screen_mom.py) with scanlines and glitches, then static again and dead.
brightness(t) is also used by scene.py for the screen's glow on the people.   python3 screen_frames.py"""
import math, os, random, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from captions import END, FLASHBACK  # noqa: E402
FPS, W, H = 24, 480, 270
FB0, FB1 = FLASHBACK
FALL = 17.0
ON0, PIC0, PIC1, OFF = 33.0, 37.0, 45.0, 46.6


def _r(t, salt=0):
    return random.Random(int(t * FPS) * 7919 + salt).random()


def brightness(t):
    if FB0 <= t < FALL:
        return 0.45
    if FALL <= t < FB1:
        return 1.0 if _r(t, 1) < 0.45 else 0.08
    if ON0 <= t < PIC0:
        u = (t - ON0) / (PIC0 - ON0)
        return (0.15 + 0.5 * u) if _r(t, 2) < 0.35 + 0.5 * u else 0.03
    if PIC0 <= t < PIC1:
        return 0.75 if _r(t, 3) > 0.06 else 0.3
    if PIC1 <= t < OFF:
        return 0.5 * (1 - (t - PIC1) / (OFF - PIC1)) if _r(t, 4) < 0.6 else 0.0
    return 0.0


def main():
    import numpy as np
    from PIL import Image, ImageDraw
    out = os.path.join(HERE, "screen")
    os.makedirs(out, exist_ok=True)
    rng = np.random.default_rng(5)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    # cracks on the dead screen (fixed): a few jagged lines from one impact point
    crack = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(crack)
    cr = random.Random(9)
    cx, cy = 330, 95
    for k in range(9):
        a = cr.uniform(0, 2 * math.pi)
        x, y = cx, cy
        for s in range(cr.randint(4, 9)):
            a += cr.uniform(-0.5, 0.5)
            nx_, ny_ = x + math.cos(a) * cr.uniform(15, 40), y + math.sin(a) * cr.uniform(15, 40)
            d.line((x, y, nx_, ny_), fill=200, width=2)
            x, y = nx_, ny_
    d.ellipse((cx - 6, cy - 6, cx + 6, cy + 6), fill=230)
    crack = np.asarray(crack, dtype=np.float32)[..., None] / 255.0
    mom_dir = os.path.join(HERE, "screen")
    n = int(END * FPS)
    for f in range(1, n + 1):
        t = (f - 1) / FPS
        p = os.path.join(out, f"s_{f:04d}.png")
        b = brightness(t)
        img = np.zeros((H, W, 3), np.float32) + 0.025              # dead screen: almost black
        if FB0 <= t < FALL:                                           # calm bands
            v = 0.5 + 0.5 * np.sin(xx * 0.018 + yy * 0.01 - t * 1.2)
            w = 0.5 + 0.5 * np.sin(xx * 0.007 - yy * 0.02 + t * 0.7)
            img = np.stack([0.25 + 0.6 * v * w, 0.55 + 0.3 * w, 0.65 + 0.25 * v], -1)
        elif FALL <= t < FB1 or ON0 <= t < PIC0 or PIC1 <= t < OFF:  # static / glitch
            g = rng.random((H // 3, W // 3)).repeat(3, 0).repeat(3, 1)[:H, :W]
            img = np.stack([g, g, g], -1) * (0.4 + 0.6 * b)
            for _ in range(rng.integers(1, 5)):                       # rolling / torn bars
                y0 = int(rng.integers(0, H))
                h = int(rng.integers(4, 30))
                img[y0:y0 + h] = img[y0:y0 + h] * 0.3 + np.array([rng.random(), rng.random(), rng.random()]) * 0.6
            if ON0 <= t < PIC0 and rng.random() < 0.15 * (t - ON0):   # the picture flashes through
                k = max(1, min(192, int((PIC0 - ON0 - (PIC0 - t)) * 6) + 1))
                src = os.path.join(mom_dir, f"mom_{k:04d}.png")
                if os.path.exists(src):
                    m = np.asarray(Image.open(src).convert("RGB"), np.float32) / 255
                    img = img * 0.5 + m * 0.5
        elif PIC0 <= t < PIC1:                                        # the home video
            k = min(192, int((t - PIC0) * FPS) + 1)
            src = os.path.join(mom_dir, f"mom_{k:04d}.png")
            m = np.asarray(Image.open(src).convert("RGB"), np.float32) / 255 if os.path.exists(src) else img
            m = m * (0.88 + 0.12 * (np.sin(yy * 1.6) > 0)[..., None])  # scanlines
            m = m * 0.92 + rng.random((H, W, 1)) * 0.08                 # grain
            if rng.random() < 0.08:                                    # glitch: a band slides sideways
                y0 = int(rng.integers(0, H - 20))
                h = int(rng.integers(6, 30))
                m[y0:y0 + h] = np.roll(m[y0:y0 + h], int(rng.integers(-40, 40)), axis=1)
            img = m
        if not (FB0 <= t < FB1):                                       # cracked glass in the present
            img = img * (1 - crack * 0.8) + crack * 0.5
        Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8)).save(p)
    print("screen frames", n)


if __name__ == "__main__":
    main()
