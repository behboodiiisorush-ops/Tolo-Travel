"""Lines of «واگن آخر ۷ — اون طرف آب».  Times come from times.py (layout.py, from the user's recording cut into voices/clips)."""

LINES = [
    ("mom1", "Mom", "بچه‌ها، گوش کنید...\nما داریم فرود میایم!"),
    ("mom2", "Mom", "این طرف پل منتظرتون می‌مونیم...\nسوارتون می‌کنیم!"),
    ("lena1", "Lena", "مامان! زود بیا!"),
    ("n1", "Me", "برای اولین بار...\nفکر کردم همه‌چیز تموم شد."),
    ("mom3", "Mom", "وای... خدای من..."),
    ("lena2", "Lena", "مامان؟... مامان؟!"),
    ("lena3", "Lena", "مامان! چی شد؟!\nجواب بده!"),
    ("rahim1", "Rahim", "اون طرف...\nیه چیزی هست."),
    ("lena4", "Lena", "مامان‌بزرگ؟...\nیکی جواب بده..."),
    ("n2", "Me", "مامان یه رودخونه\nبا ما فاصله داشت..."),
    ("n3", "Me", "و قطار...\nدیگه از این جلوتر نمی‌رفت."),
    ("lena5", "Lena", "شنیدی؟! سه تا!"),
    ("lena6", "Lena", "مامان‌بزرگه!\nهمیشه سه بار در می‌زد!"),
    ("n4", "Me", "زنده بودن...\nحداقل یکی‌شون."),
    ("rahim2", "Rahim", "این پل وزن یه گربه رو هم\nتحمل نمی‌کنه."),
    ("n5", "Me", "ولی اونا اون طرفن...\nبا همون چیزی که ما تو شهر دیدیم."),
    ("rahim3", "Rahim", "باشه...\nطناب رو به کمرتون ببندید."),
    ("rahim4", "Rahim", "من می‌مونم. اگه چیزی اومد...\nبوق قطار رو می‌زنم."),
    ("lena7", "Lena", "عمو رحیم... تو هم بیا."),
    ("rahim5", "Rahim", "یکی باید مراقب قطار باشه، دخترم."),
    ("n6", "Me", "آروم...\nپاتو بذار جای پای من."),
    ("lena8", "Lena", "به پایین نگاه نکن...\nبه من نگاه کن."),
    ("n7", "Me", "اینو آقا جلال یادش داده بود..."),
    ("lena9", "Lena", "اون... مامانه؟"),
    ("n8", "Me", "پشت سرمون خطر بود...\nجلومون یه سایه..."),
    ("n9", "Me", "و ما...\nدرست وسط پل بودیم."),
]
# the order the user recorded them in (one file, script order of the voice blocks)
RECORDED = ["mom1", "mom2", "mom3", "lena1", "lena2", "lena3", "lena4", "lena5", "lena6", "lena7", "lena8", "lena9",
            "n1", "n2", "n3", "n4", "n5", "n6", "n7", "n8", "n9", "rahim1", "rahim2", "rahim3", "rahim4", "rahim5"]
NARRATION_KEYS = {"n1", "n2", "n3", "n4", "n5", "n7", "n8", "n9"}

TIMES = {}
try:
    from times import TIMES  # noqa: F401
except ImportError:
    pass

CAPTIONS = [(TIMES.get(k, (0, 0))[0], TIMES.get(k, (0, 0))[1], who, text) for k, who, text in LINES]
NARRATION = {TIMES[k][0] for k in NARRATION_KEYS if k in TIMES}
KEY_OF = {k: TIMES.get(k, (0, 0)) for k, _, _ in LINES}

TITLE = "واگن آخر ۷ — اون طرف آب"
QUESTION = "اگه تو بودی...\nجلو می‌رفتی\nیا برمی‌گشتی پیش رحیم؟"
END = max([e for s, e in TIMES.values()], default=60.0) + 2.5
CARD_SECONDS = 8
NOTIFS = []
