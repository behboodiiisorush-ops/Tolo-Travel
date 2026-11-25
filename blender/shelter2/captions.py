"""Lines of «پناهگاه ۲ — چراغ سبز».  Times come from times.py (layout.py: from the recorded
voices, or estimated from the text until the recording arrives).

Speakers on screen move their jaw while they talk.  NARRATION lines are the narrator's inner voice.
"""

LINES = [
    ("n1", "Me", "سه روز...\nسه روز چراغ بالای در قرمز بود."),
    ("n2", "Me", "هر شب صدای در زدن میومد...\nو هیچ‌کس جرأت نداشت جواب بده."),
    ("lena1", "Lena", "کی می‌تونیم بریم بیرون؟"),
    ("guard1", "Guard", "تا چراغ قرمزه، هیچ‌کس درو باز نمی‌کنه.\nبیرون هوا سمیه."),
    ("mom1", "Mom", "سبز شد! چراغ سبز شد!"),
    ("guard2", "Guard", "آروم... فقط یه نگاه."),
    ("n3", "Me", "همه‌جا ساکت بود...\nانگار همه‌چیز تموم شده بود."),
    ("lena2", "Lena", "خرگوشم! شاید هنوز اونجاست!"),
    ("me1", "Me", "لنا، صبر کن!"),
    ("me2", "Me", "آقا جلال...؟"),
    ("guard3", "Guard", "درو ببندید! درو ببندید!"),
    ("me3", "Me", "هل بدید! هل بدید!"),
    ("lena3", "Lena", "اون... آقا جلال بود؟"),
    ("guard4", "Guard", "اون دیگه آقا جلال نیست."),
    ("mom2", "Mom", "حالا... چی کار کنیم؟"),
    ("n4", "Me", "چراغ سبز بود...\nولی بیرون، دیگه مال ما نبود."),
]
NARRATION_KEYS = {"n1", "n2", "n3", "n4"}

TIMES = {}
try:
    from times import TIMES  # noqa: F401
except ImportError:
    pass

CAPTIONS = [(TIMES.get(k, (0, 0))[0], TIMES.get(k, (0, 0))[1], who, text) for k, who, text in LINES]
NARRATION = {TIMES[k][0] for k in NARRATION_KEYS if k in TIMES}
KEY_OF = {k: TIMES.get(k, (0, 0)) for k, _, _ in LINES}

QUESTION = "اگه تو بودی...\nتوی پناهگاه می‌موندی\nیا می‌زدی بیرون؟"
END = max([e for s, e in TIMES.values()], default=70.0) + 1.5
CARD_SECONDS = 8
NOTIFS = []
