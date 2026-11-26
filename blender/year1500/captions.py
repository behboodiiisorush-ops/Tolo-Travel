"""«سال ۱۵۰۰» — every spoken line (seconds). Single source for captions, lip sync and the voice script.
The film is seen through my eyes (POV, like «واگن آخر»): 'me' is never seen talking, his lines are his voice."""
# (start, end, who, text)
LINES = [
    (0.8, 6.6, "me", "سال ۱۵۰۰. شهری که همه‌چیزش نو بود... حالا فقط ما دو نفر توش مونده بودیم."),
    (7.6, 11.0, "me", "قبلاً همه‌چی خوب بود. مامان بود، کیان بود، شهر پر از آدم بود."),
    (12.0, 14.0, "mom", "زود باشین بچه‌ها، دیر می‌رسیم!"),
    (15.4, 17.8, "me", "یه‌هو... همه‌چی به هم ریخت."),
    (23.2, 25.2, "kian", "داداش؟... ما کجاییم؟"),
    (27.0, 29.8, "kian", "مامان!... کسی اینجا نیست؟!"),
    (36.0, 41.6, "mom", "کیان جان، هر جا باشی مامان پیشته. قول بده هیچ‌وقت نترسی."),
    (44.4, 48.4, "kian", "مامان دیگه نیست... هیچ‌کس نیست."),
    (49.6, 53.6, "me", "پس خودمون می‌گردیم. شاید یه جایی هنوز زندگی باشه."),
    (56.0, 61.4, "me", "همه رفته بودن. حالا نوبت ما بود که دنبال سرنوشت خودمون بریم."),
]
NAMES = {"me": "من", "mom": "مامان", "kian": "کیان"}
END = 72.0
FLASHBACK = (7.0, 18.6)             # warm, clean, crowded; the fall starts at FALL
FALL = 15.0
WAKE = 20.0                         # black between FLASHBACK end and WAKE
TITLE = "سال ۱۵۰۰"
QUESTION = "اگه توی این شهر به این بزرگی فقط تو مونده بودی، اول دنبال چی می‌گشتی؟"
SCREEN = dict(on=31.0, pic0=35.0, pic1=43.0, off=44.6)


def speaking(who, t):
    """Lip movement: only for people we see talking (not me, not mom's voice from the screen)."""
    if who == "me":
        return False
    for a, b, w, _ in LINES:
        if w == who and a <= t <= b:
            if who == "mom" and a > 30:
                return False
            return True
    return False
