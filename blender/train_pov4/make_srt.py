"""Write out/dialogue.srt and out/voice_lines.txt — a timing sheet for recording the voices."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from captions import CAPTIONS  # noqa: E402

NAMES = {None: "راوی (من)", "Me": "من", "Mom": "مامان", "Lena": "لنا", "Grandma": "مامان‌بزرگ",
         "Grandma voice": "مامان‌بزرگ (پیام صوتی، صدای گوشی)", "Rahim": "عمو رحیم", "Jalal": "آقا جلال",
         "Sara": "سارا", "Phone": "صدای ضبط‌شدهٔ تلفن", "Radio": "بی‌سیم (صدای خش‌دار)"}


def ts(x, sep=","):
    h, m = int(x // 3600), int(x % 3600 // 60)
    s = x % 60
    return f"{h:02d}:{m:02d}:{int(s):02d}{sep}{int(round((s - int(s)) * 1000)):03d}"


os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
with open(os.path.join(HERE, "out", "dialogue.srt"), "w", encoding="utf-8") as f:
    for i, (a, b, who, text) in enumerate(CAPTIONS, 1):
        f.write(f"{i}\n{ts(a)} --> {ts(b)}\n{NAMES[who]}: {text.replace(chr(10), ' ')}\n\n")
with open(os.path.join(HERE, "out", "voice_lines.txt"), "w", encoding="utf-8") as f:
    f.write("واگن آخر — دیالوگ‌ها برای ضبط صدا (زمان = ثانیهٔ ویدیو)\n\n")
    for a, b, who, text in CAPTIONS:
        f.write(f"{a:5.1f} تا {b:5.1f} ثانیه | {NAMES[who]}: {text.replace(chr(10), ' ')}\n")
print("ok")
