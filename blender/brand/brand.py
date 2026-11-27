"""Channel branding for every Tolo Travel / agetobudi film (the user's rule, see CLAUDE.md).

    from brand import overlay
    overlay(img, "هشدار")      # PIL RGB image of any size (vertical or 16:9), drawn in place

Top-right: the film's name (big). (The user removed the «ساخته شده توسط بلندر» text — CREDIT is empty.)
Top-left:  the round channel logo (agetobudi_logo_round.png, the user's logo).
Use it on every frame of every delivered version (with and without captions, with and without sound).
"""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONT = os.path.join(HERE, "..", "fonts", "Vazirmatn-FD-ExtraBold.ttf")
LOGO = os.path.join(HERE, "agetobudi_logo_round.png")
CREDIT, CHANNEL = "", "agetobudi"     # no «ساخته شده توسط بلندر» text any more (user)
_cache = {}


def _font(size):
    if size not in _cache:
        _cache[size] = ImageFont.truetype(FONT, size, layout_engine=ImageFont.Layout.RAQM)
    return _cache[size]


def _logo(size):
    key = ("logo", size)
    if key not in _cache:
        _cache[key] = Image.open(LOGO).convert("RGBA").resize((size, size), Image.LANCZOS)
    return _cache[key]


def overlay(img, title):
    W, H = img.size
    u = min(W, H) / 1080.0                      # 1.0 for 1080x1920, 0.67 for 1280x720
    m = int(34 * u)
    lg = _logo(int(170 * u))
    img.paste(lg, (m, m), lg)
    d = ImageDraw.Draw(img)
    d.text((W - m, m + int(52 * u)), title, font=_font(int(78 * u)), fill=(255, 255, 255), anchor="rm",
           direction="rtl", language="fa", stroke_width=max(2, int(7 * u)), stroke_fill=(0, 0, 0))
    if CREDIT:
        d.text((W - m, m + int(122 * u)), CREDIT, font=_font(int(32 * u)), fill=(235, 235, 235), anchor="rm",
               direction="rtl", language="fa", stroke_width=max(1, int(4 * u)), stroke_fill=(0, 0, 0))
    return img
