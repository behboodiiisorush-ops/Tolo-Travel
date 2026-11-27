"""Screen-message layers for «جرقه ۲» (system python3: Pillow + raqm).  python3 make_textures.py -> textures/msg_*.png"""
import os
from PIL import Image, ImageDraw, ImageFont
from captions import SCREEN
HERE = os.path.dirname(os.path.abspath(__file__))
FONT = os.path.join(HERE, "..", "fonts", "Vazirmatn-FD-ExtraBold.ttf")
W, H = 1160, 680
os.makedirs(os.path.join(HERE, "textures"), exist_ok=True)
for i, line in enumerate(SCREEN):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    f = ImageFont.truetype(FONT, 150, layout_engine=ImageFont.Layout.RAQM)
    w = d.textlength(line, font=f, direction="rtl", language="fa")
    d.text(((W - w) / 2, 40 + i * 200), line, font=f, fill=(255, 255, 255, 255), direction="rtl", language="fa")
    im.save(os.path.join(HERE, "textures", f"msg_{i}.png"))
print("textures ok")
