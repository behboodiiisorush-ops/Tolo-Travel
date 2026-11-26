"""Per-frame finishing for the style tests / films (Pillow + numpy):
    noir  : black & white, hard contrast, only reds (blood, lamps) kept in colour
    anime : soft bloom on bright areas, cool night grade, slight softening
    python3 look_post.py noir in.png out.png
"""
import sys
import numpy as np
from PIL import Image, ImageFilter


def noir(img):
    a = np.asarray(img.convert("RGB")).astype(np.float32) / 255.0
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    lum = 0.3 * r + 0.59 * g + 0.11 * b
    lum = np.clip((lum - 0.18) * 1.9 + 0.1, 0, 1) ** 1.15          # hard contrast
    red = np.clip((r - np.maximum(g, b)) * 4.0 - 0.35, 0, 1)        # how "red" a pixel is
    gray = np.stack([lum] * 3, -1)
    redc = np.stack([np.clip(r * 1.3, 0, 1), g * 0.25, b * 0.25], -1)
    out = gray * (1 - red[..., None]) + redc * red[..., None]
    # film grain + vignette
    h, w = lum.shape
    yy, xx = np.mgrid[0:h, 0:w]
    v = 1 - 0.45 * (((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2)
    out = out * np.clip(v, 0.35, 1)[..., None]
    out += np.random.default_rng(0).normal(0, 0.025, out.shape)
    return Image.fromarray((np.clip(out, 0, 1) * 255).astype(np.uint8))


def anime(img):
    img = img.convert("RGB")
    a = np.asarray(img).astype(np.float32) / 255.0
    lum = a.max(-1)
    bright = np.clip((lum - 0.75) * 4, 0, 1)[..., None] * a
    glow = Image.fromarray((bright * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(radius=img.width / 40))
    g = np.asarray(glow).astype(np.float32) / 255.0
    out = 1 - (1 - a) * (1 - g * 0.9)                                # screen blend
    out = out * np.array([0.93, 0.98, 1.06]) + np.array([0.0, 0.01, 0.03])   # cool night grade
    out = Image.fromarray((np.clip(out, 0, 1) * 255).astype(np.uint8))
    return out.filter(ImageFilter.SMOOTH)


if __name__ == "__main__":
    look, src, dst = sys.argv[1:4]
    {"noir": noir, "anime": anime}[look](Image.open(src)).save(dst)
