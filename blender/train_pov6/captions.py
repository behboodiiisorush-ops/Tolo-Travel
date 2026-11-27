"""Lines of «واگن آخر ۶ — سیگنال».  Times come from times.py (layout.py: from the ElevenLabs clips in el/)."""

LINES = [
    ("n1", "Me", "بالگرد داشت دنبال قطار میومد...\nدرست بالای سر ما."),
    ("rahim1", "Rahim", "پرده‌ها رو بکشید!\nسرتون رو بدزدید!"),
    ("lena1", "Lena", "شاید مامان فرستادتش..."),
    ("rahim2", "Rahim", "نمی‌دونیم مال کیه.\nهیچ‌کس تکون نخوره."),
    ("n2", "Me", "ولی من چراغ‌قوه رو\nاز جیبم درآوردم."),
    ("me1", "Me", "اگه دنبال ماست...\nباید ما رو ببینه."),
    ("lena2", "Lena", "دیدمون! دیدمون!"),
    ("rahim3", "Rahim", "داره پایین میاد...\nیه چیزی داره میده پایین!"),
    ("me2", "Me", "یه کیفه...\nیه رادیو توشه!"),
    ("mom1", "Mom", "بچه‌ها؟\nصدامو می‌شنوید؟"),
    ("lena3", "Lena", "مامان!!"),
    ("mom2", "Mom", "گوش کنید... پل خراب شده.\nقبل از پل وایسید!"),
    ("rahim4", "Rahim", "پل؟!\nما داریم با تمام سرعت می‌ریم سمتش!"),
    ("mom3", "Mom", "اون طرف رودخونه...\nمنتظرتونم..."),
    ("lena4", "Lena", "مامان؟...\nمامان؟!"),
    ("n3", "Me", "مامان زنده بود... و منتظرمون بود.\nولی بین ما یه رودخونه بود...\nو یه پل که دیگه نبود."),
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

TITLE = "واگن آخر ۶ — سیگنال"
QUESTION = "اگه تو بودی...\nکنار قطار می‌موندی\nیا از رودخونه رد می‌شدی؟"
END = max([e for s, e in TIMES.values()], default=60.0) + 2.0
CARD_SECONDS = 8
NOTIFS = []
