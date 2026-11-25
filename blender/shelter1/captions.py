"""Lines of «پناهگاه ۱ — نُه دقیقه».  Times come from times.py (layout.py: from the recorded
voices, or estimated from the text until the recording arrives).

Speakers on screen move their jaw while they talk.  NARRATION lines are the narrator's inner voice.
"""

LINES = [
    ("n1", "Me", "نُه دقیقه. فقط نُه دقیقه وقت داشتیم...\nتا دنیا تموم بشه."),
    ("mom1", "Mom", "فقط آب و دارو...\nبقیه‌ش مهم نیست!"),
    ("lena1", "Lena", "بیرون چی شده؟\nچرا همه جیغ می‌زنن؟"),
    ("me1", "Me", "لنا! کفشاتو بپوش!\nهمین الان!"),
    ("mom2", "Mom", "از این طرف! سمت پارک!"),
    ("me2", "Me", "مامان، دستشو ول نکن!"),
    ("lena2", "Lena", "خرگوشم! خرگوشم افتاد!"),
    ("guard1", "Guard", "فقط بیست نفر دیگه جا داره!\nبچه‌ها اول!"),
    ("me3", "Me", "صبر کنید! ما سه نفریم!"),
    ("jalal1", "Jalal", "صبر کنید!\nتو رو خدا صبر کنید!"),
    ("guard2", "Guard", "در بسته میشه!\nدیگه وقت نیست!"),
    ("n2", "Me", "آقا جلال...\nاون هنوز بیرون بود."),
    ("lena3", "Lena", "تاریکه... صدای چی بود؟"),
    ("radio1", "Radio", "...اگه کسی صدامو می‌شنوه...\nما هنوز زنده‌ایم."),
    ("n3", "Me", "صدای در زدن بود...\nیعنی هنوز کسی اون بیرون زنده‌ست؟"),
]
NARRATION_KEYS = {"n1", "n2", "n3"}

TIMES = {}
try:
    from times import TIMES  # noqa: F401
except ImportError:
    pass

CAPTIONS = [(TIMES.get(k, (0, 0))[0], TIMES.get(k, (0, 0))[1], who, text) for k, who, text in LINES]
NARRATION = {TIMES[k][0] for k in NARRATION_KEYS if k in TIMES}
KEY_OF = {k: TIMES.get(k, (0, 0)) for k, _, _ in LINES}

QUESTION = "اگه تو بودی...\nدرِ پناهگاه رو باز می‌کردی؟"
END = max([e for s, e in TIMES.values()], default=70.0) + 1.5
CARD_SECONDS = 8
FLASH_AFTER = 0.6   # the flash comes this long after the line "n2" ends

# phone notifications shown as a banner at the top of the screen:
# (start, end, app name, icon colour, title, message)
NOTIFS = [
    (0.5, 6.4, "هشدار اضطراری", (210, 40, 40), "هشدار اضطراری",
     "حملهٔ هسته‌ای! فوراً به نزدیک‌ترین پناهگاه بروید."),
]
