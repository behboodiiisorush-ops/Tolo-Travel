"""«هشدار» — every spoken line (seconds). Single source for captions, lip sync and the voice script."""
# (start, end, who, text)
LINES = [
    (3.0, 5.6, "kian", "بیا پرنده کوچولو... برات نون آوردم."),
    (10.8, 12.6, "mom", "کیان! بیا صبحونه!"),
    (13.6, 15.6, "passerby", "آقای رضایی؟ حالتون خوبه؟"),
    (18.0, 19.2, "passerby", "ولم کن!"),
    (44.0, 46.6, "kian", "مامان، آقای رضاییه! درو باز کنم؟"),
    (46.9, 48.9, "mom", "آره، حتماً کلیدشو جا گذاشته. باز کن."),
    (50.8, 52.6, "kian", "هی! چیکار می‌کنی؟!"),
    (57.0, 59.8, "kian", "مامان... اون آقای رضایی نیست."),
]
NAMES = {"kian": "کیان", "mom": "مامان", "passerby": "رهگذر"}
END = 61.0
QUESTION = "اگه یه پرنده بهت هشدار می‌داد، باور می‌کردی؟"


def speaking(who, t):
    return any(a <= t <= b and w == who for a, b, w, _ in LINES)
