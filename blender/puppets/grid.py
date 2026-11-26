"""sheets/p_*.png -> sheets/portraits.png (4 x 2) with Persian names (Vazirmatn, raqm)."""
import os
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__))
ORDER = [("me", "من"), ("mom", "مامان"), ("kazemi", "آقای کاظمی"), ("arian", "آرین"),
         ("mahsa", "مهسا"), ("kian", "کیان"), ("rezaei", "آقای رضایی"), ("anchor", "گوینده اخبار")]
f = ImageFont.truetype(os.path.join(HERE, "..", "fonts", "Vazirmatn-FD-ExtraBold.ttf"), 44)
tw, th = 600, 760
g = Image.new("RGB", (tw * 4, (th + 80) * 2), (30, 30, 36))
d = ImageDraw.Draw(g)
for i, (k, fa) in enumerate(ORDER):
    p = os.path.join(HERE, "sheets", f"p_{k}.png")
    if not os.path.exists(p):
        continue
    x, y = (i % 4) * tw, (i // 4) * (th + 80)
    g.paste(Image.open(p).convert("RGB"), (x, y))
    d.text((x + tw // 2, y + th + 40), fa, font=f, fill=(255, 255, 255), anchor="mm", direction="rtl", language="fa")
g.save(os.path.join(HERE, "sheets", "portraits.png"))
print("ok")
