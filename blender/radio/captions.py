"""«زنگ آخر ۵ — صدای رادیو» — every spoken line (seconds). Single source for captions, lip sync and the voices.
Times are fitted to the real ElevenLabs takes in voices/ (eleven_multilingual_v2)."""
# (start, end, who, text)
LINES = [
    (1.0, 3.75, "me", "بنزین تموم شد... وسط یه جاده‌ی تاریک."),
    (6.2, 9.8, "radio", "پسرم... بیا به خونه‌ی قدیمی‌مون. ته همین جاده‌ست."),
    (12.0, 13.7, "kian", "مامانه! باید بریم پیشش!"),
    (15.0, 19.45, "kazemi", "این صدا هر شب همینو می‌گه. تله‌ست. هیچ‌کس بیرون نمی‌ره."),
    (21.6, 23.55, "mahsa", "آروم... بیدار نشه."),
    (27.2, 29.9, "me", "خونه همونجا بود. چراغش هنوز روشن بود."),
    (39.2, 42.0, "tape", "پسرم؟... بیا درو باز کن. سردمه."),
    (45.8, 47.3, "me", "این فقط یه ضبط صوته."),
    (50.0, 51.8, "mahsa", "کیان... اینا کفشای مامانته؟"),
    (56.2, 57.25, "kian", "هنوز گرمن..."),
]
# voice file per line (same order), and the card line read after the film
FILES = ["01_me", "02_mom", "03_kian", "04_kazemi", "05_mahsa", "06_me", "07_mom", "08_me", "09_mahsa", "10_kian"]
NAMES = {"me": "من", "radio": "رادیوی ماشین", "kian": "کیان", "kazemi": "آقای کاظمی", "mahsa": "مهسا",
         "tape": "ضبط صوت"}
VOICEOVER = {0, 5}          # «من» narrates these two (lips closed)
END = 64.5
QUESTION = "اگه مامان اینجا بوده... الان کجاست؟"
CARD_VOICE = "11_card"


def speaking(who, t):
    return any(a <= t <= b and w == who for i, (a, b, w, _) in enumerate(LINES) if i not in VOICEOVER)
