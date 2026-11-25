"""Lines of «تک‌تیرانداز ۱ — نقطهٔ قرمز».  Times come from times.py (layout.py: from the recorded
voices, or estimated from the text until the recording arrives).

The commander speaks over the radio; the man and the girl are seen through the scope.
"""

LINES = [
    ("n1", "Me", "از این بالا...\nهمه شبیه هم‌ان."),
    ("cmd1", "Commander", "هدف: مرد با کت قرمز. کنار فواره.\nشلیک فقط با دستور من."),
    ("me1", "Me", "هدف رو دیدم. کت قرمز."),
    ("me2", "Me", "یه کیف دستشه...\nداره به ساعتش نگاه می‌کنه."),
    ("cmd2", "Commander", "توی کیفش بمبه.\nسه ثانیه وقت داری."),
    ("me3", "Me", "داره... یه جعبه درمیاره؟"),
    ("girl1", "Girl", "بابا!"),
    ("man1", "Man", "تولدت مبارک، عزیزم!"),
    ("cmd3", "Commander", "شلیک کن! همین الان!"),
    ("me4", "Me", "صبر کن...\nاون یه بچه‌ست..."),
    ("n2", "Me", "اون منو دید...\nیعنی می‌دونست؟"),
]
NARRATION_KEYS = {"n1", "n2"}

TIMES = {}
try:
    from times import TIMES  # noqa: F401
except ImportError:
    pass

CAPTIONS = [(TIMES.get(k, (0, 0))[0], TIMES.get(k, (0, 0))[1], who, text) for k, who, text in LINES]
NARRATION = {TIMES[k][0] for k in NARRATION_KEYS if k in TIMES}
KEY_OF = {k: TIMES.get(k, (0, 0)) for k, _, _ in LINES}

QUESTION = "اگه تو بودی...\nشلیک می‌کردی؟"
END = max([e for s, e in TIMES.values()], default=60.0) + 1.8
CARD_SECONDS = 8
NOTIFS = []


def scope_windows():
    """[(start, end)] of the shots through the rifle scope (post.py draws the round mask then)."""
    return [(0.0, KEY_OF["cmd1"][0] - 1.0), (KEY_OF["me1"][0] - 1.2, END)]
