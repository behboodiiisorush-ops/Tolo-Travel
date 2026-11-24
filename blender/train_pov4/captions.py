"""Lines of «واگن آخر ۴ — چراغای روشن».  Times come from times.py (layout.py: from the recorded
voices, or estimated from the text length until the recording arrives).

Speakers on screen move their jaw while they talk.  NARRATION lines are the narrator's inner voice.
"""

LINES = [
    ("n1", "Me", "شب شده بود. فقط من بودم، لنا...\nو شال مامان‌بزرگ."),
    ("rahim1", "Rahim", "یه ساعت. اگه برنگشتید،\nخودم میام دنبالتون."),
    ("lena1", "Lena", "تاریکه... می‌ترسم."),
    ("me1", "Me", "چراغ‌قوه رو روشن می‌کنم...\nببین. دیگه تاریک نیست."),
    ("n2", "Me", "دنبال همون چراغا راه افتادیم...\nکنار ریل، توی تاریکی."),
    ("lena2", "Lena", "اونجا! چراغ!"),
    ("n3", "Me", "واگن آخر بود. روی یه ریل فرعی،\nوسط دشت... هنوز روشن."),
    ("me2", "Me", "مامان‌بزرگ؟ کسی اینجاست؟"),
    ("jalal1", "Jalal", "آروم... بچه‌ها خوابن."),
    ("lena3", "Lena", "عمو جلال!"),
    ("me3", "Me", "مامان‌بزرگ ما... اینجاست؟"),
    ("jalal2", "Jalal", "یه ساعت پیش پیاده شد...\nگفت می‌رم دنبال بچه‌ها. سمت ریل رفت."),
    ("n4", "Me", "پس شالش... مال همون موقع بود.\nاون دنبال ما می‌گشت... ما دنبال اون."),
    ("mom1", "Mom", "بچه‌هام..."),
    ("gm1", "Grandma", "دخترم..."),
    ("mom2", "Mom", "مامان؟!"),
    ("lena4", "Lena", "حالا مامان‌بزرگ کجاست؟"),
    ("n5", "Me", "همون لحظه که ما به واگن رسیدیم...\nاون به مامان رسیده بود.\nو حالا... ما دو تا بودیم که گم شده بودیم."),
]
NARRATION_KEYS = {"n1", "n2", "n3", "n4", "n5"}

TIMES = {}
try:
    from times import TIMES  # noqa: F401
except ImportError:
    pass

CAPTIONS = [(TIMES.get(k, (0, 0))[0], TIMES.get(k, (0, 0))[1], who, text) for k, who, text in LINES]
NARRATION = {TIMES[k][0] for k in NARRATION_KEYS if k in TIMES}
KEY_OF = {k: TIMES.get(k, (0, 0)) for k, _, _ in LINES}

QUESTION = "اگه تو بودی، برمی‌گشتی سمت مرز...\nیا با واگن آخر جلوتر می‌رفتی؟"
END = max([e for s, e in TIMES.values()], default=70.0) + 1.0
CARD_SECONDS = 8
