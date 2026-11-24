"""Lines of «واگن آخر ۳ — در بسته شد», timed to the recorded voices (voices/recording_1.mp3).

(start, end, speaker, text).  Speakers on screen move their jaw while they talk (Lena, Rahim,
Mom and the soldiers in the border scene).  NARRATION lines are the narrator's inner voice.
"""

# times are filled in from the recording by layout.py (see TIMES below)
LINES = [
    ("n1", "Me", "در بسته شد. من موندم...\nو دست لنا رو ول نکردم."),
    ("mom1", "Mom", "لنا!!"),
    ("n2", "Me", "قطار عقب‌عقب راه افتاد...\nهر چی نزدیک‌تر می‌شدیم،\nصدای مامان‌بزرگ دورتر می‌شد."),
    ("gm1", "Grandma far", "بچه‌ها..."),
    ("lena1", "Lena", "دیگه صداش نمیاد..."),
    ("me1", "Me", "میاد عزیزم... حتماً میاد."),
    ("n3", "Me", "ولی نیومد. فقط صدای چرخ‌ها بود...\nو نفس‌های لنا."),
    ("n4", "Me", "اونجا بود که فهمیدم...\nموندن هم یه جور رفتنه."),
    ("rahim1", "Rahim", "همین‌جا بود...\nقسم می‌خورم همین‌جا بود!"),
    ("n5", "Me", "همین چند دقیقه پیش چراغاش رو دیدم...\nحالا هیچی نبود. نه واگن، نه مامان‌بزرگ."),
    ("n6", "Me", "فقط شالش روی ریل بود...\nهنوز گرم بود."),
    ("lena2", "Lena", "مامان‌بزرگ... اینجا بود؟"),
    ("me2", "Me", "آره... بود. ولی اگه اینجا بود...\nپس اون چراغای روشن، مال کی بود؟"),
    ("sol1", "Soldier1", "خانم، وقت نداریم! باید از مرز دور شید،\nاینجا خطرناکه!"),
    ("mom2", "Mom", "بچه‌هام توی اون قطارن!"),
    ("sol2", "Soldier2", "همین الان! برید عقب!"),
    ("lena3", "Lena", "حالا چیکار کنیم؟"),
    ("n7", "Me", "و من جواب نداشتم... مامان‌بزرگ اونجا نبود.\nمامان داشت دور می‌شد...\nبرای اولین بار، همه‌مون از هم جدا شده بودیم."),
]
NARRATION_KEYS = {"n1", "n2", "n3", "n4", "n5", "n6", "n7"}

TIMES = {}  # key -> (start, end); written by layout.py
try:
    from times import TIMES  # noqa: F401
except ImportError:
    pass

CAPTIONS = [(TIMES.get(k, (0, 0))[0], TIMES.get(k, (0, 0))[1], who, text) for k, who, text in LINES]
NARRATION = {TIMES[k][0] for k in NARRATION_KEYS if k in TIMES}
KEY_OF = {k: TIMES.get(k, (0, 0)) for k, _, _ in LINES}

QUESTION = "اگه تو بودی، دنبال مامان‌بزرگ می‌گشتی...\nیا لنا رو برمی‌گردوندی پیش مامان؟"
END = 73.6
CARD_SECONDS = 8
