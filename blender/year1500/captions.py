"""«سال ۱۵۰۰» — every spoken line (seconds). Single source for captions, lip sync and the voice script.
"me" lines are the narrator (voice-over, no lips) except where he speaks on screen (ON_SCREEN)."""
# (start, end, who, text)
LINES = [
    (1.0, 5.4, "me", "سال ۱۵۰۰. شهری که همه‌چیزش نو بود..."),
    (6.2, 9.2, "me", "...حالا فقط ما دو نفر توش مونده بودیم."),
    (10.2, 13.6, "me", "قبلاً همه‌چی خوب بود. مامان بود، کیان بود، شهر پر از آدم بود."),
    (14.2, 16.2, "mom", "زود باشین بچه‌ها، دیر می‌رسیم!"),
    (17.4, 19.8, "me", "یه‌هو... همه‌چی به هم ریخت."),
    (25.4, 27.4, "kian", "داداش؟... ما کجاییم؟"),
    (29.0, 31.8, "kian", "مامان!... کسی اینجا نیست؟!"),
    (38.0, 43.6, "mom", "کیان جان، هر جا باشی مامان پیشته. قول بده هیچ‌وقت نترسی."),
    (46.4, 50.4, "kian", "مامان دیگه نیست... هیچ‌کس نیست."),
    (51.6, 55.6, "me", "پس خودمون می‌گردیم. شاید یه جایی هنوز زندگی باشه."),
    (58.0, 63.4, "me", "همه رفته بودن. حالا نوبت ما بود که دنبال سرنوشت خودمون بریم."),
]
ON_SCREEN = {(51.6, 55.6)}          # 'me' lines said on camera (lips move); the others are voice-over
NAMES = {"me": "من", "mom": "مامان", "kian": "کیان"}
END = 72.0
FLASHBACK = (9.5, 20.6)             # warm, clean, crowded; then the fall
TITLE = "سال ۱۵۰۰"
QUESTION = "اگه توی این شهر به این بزرگی فقط تو مونده بودی، اول دنبال چی می‌گشتی؟"


def speaking(who, t):
    for a, b, w, _ in LINES:
        if w == who and a <= t <= b:
            if who == "me" and (a, b) not in ON_SCREEN:
                return False
            if who == "mom" and a > 30:          # mom's second line comes from the screen
                return False
            return True
    return False
