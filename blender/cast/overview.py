"""Builds sheets/overview.png: one card per cast member (face + full body + name)."""
import os
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__))
S = os.path.join(HERE, "sheets")
FONT = os.path.join(HERE, "..", "fonts", "Vazirmatn-FD-ExtraBold.ttf")
CARDS = [("me", "من (راوی)"), ("arian", "آرین"), ("mahsa", "مهسا"), ("kian", "کیان"), ("mom", "مامان"),
         ("kazemi", "آقای کاظمی"), ("rezaei", "آقای رضایی"), ("anchor", "گوینده اخبار"), ("soldier", "سرباز"),
         ("rezaei_z", "رضایی زامبی"), ("passerby0_z", "زامبی رهگذر"), ("student0", "دانش‌آموز")]
f = ImageFont.truetype(FONT, 40, layout_engine=ImageFont.Layout.RAQM)
W, H = 480, 1000
cols = 6
out = Image.new("RGB", (W * cols, H * ((len(CARDS) + cols - 1) // cols)), (24, 24, 26))
for i, (k, name) in enumerate(CARDS):
    face = Image.open(f"{S}/{k}_face.png").convert("RGB").crop((0, 60, 480, 600))
    full = Image.open(f"{S}/{k}_full.png").convert("RGB").crop((90, 140, 390, 560)).resize((300, 420))
    card = Image.new("RGB", (W, H), (24, 24, 26))
    card.paste(face, (0, 0))
    card.paste(full, (90, 545))
    d = ImageDraw.Draw(card)
    d.text((W // 2, 975), name, font=f, fill=(255, 255, 255), anchor="ms", direction="rtl", language="fa")
    out.paste(card, ((i % cols) * W, (i // cols) * H))
out.save(f"{S}/overview.png")
print("ok")
