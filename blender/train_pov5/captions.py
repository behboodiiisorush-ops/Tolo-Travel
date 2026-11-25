"""Lines of «واگن آخر ۵ — شهر خاموش».  Times come from times.py (layout.py: from the recorded
voices, or estimated from the text until the recording arrives)."""

LINES = [
    ("n1", "Me", "قطار دوباره راه افتاد...\nولی نه به سمت مرز."),
    ("rahim1", "Rahim", "خط مرز بسته شد.\nفقط یه راه مونده... از وسط شهر."),
    ("lena1", "Lena", "اون آدما چرا\nاینجوری راه میرن؟"),
    ("jalal1", "Jalal", "نگاه نکن، دخترم.\nفقط به من نگاه کن."),
    ("n2", "Me", "اونا آدم نبودن...\nدیگه نه."),
    ("lena2", "Lena", "یکیشون داره\nبه ما نگاه می‌کنه..."),
    ("rahim2", "Rahim", "ترمز! یه اتوبوس روی ریله!"),
    ("rahim3", "Rahim", "یکی باید بره پایین...\nسه دقیقه وقت داریم."),
    ("me1", "Me", "دارن میان سمت ما..."),
    ("lena3", "Lena", "من می‌خوام برگردیم\nپیش مامان..."),
    ("jalal2", "Jalal", "من میرم.\nمن دیگه چیزی برای از دست دادن ندارم."),
    ("jalal3", "Jalal", "برید!\nمنتظر من نمونید!"),
    ("lena4", "Lena", "عمو جلال!!"),
    ("rahim4", "Rahim", "راه باز شد!\nحرکت کن! همین الان!"),
    ("me2", "Me", "دارن دنبال قطار می‌دوئن!"),
    ("n4", "Me", "آقا جلال راه رو باز کرد...\nولی خودش برنگشت."),
    ("lena5", "Lena", "اونجا! بالگرد!"),
    ("n3", "Me", "هر متری که جلو می‌رفتیم...\nاز مرز، از مامان، از مامان‌بزرگ\nدورتر می‌شدیم."),
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

QUESTION = "اگه تو بودی...\nبه اون بالگرد علامت می‌دادی\nیا قایم می‌شدی؟"
END = max([e for s, e in TIMES.values()], default=60.0) + 1.5
CARD_SECONDS = 8
NOTIFS = []
