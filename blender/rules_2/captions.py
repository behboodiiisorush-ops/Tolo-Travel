"""«قانون‌ها — قسمت دوم» — every spoken line and phone message (seconds).
Single source for captions (post.py), lip movement (scene.py, talking=True on these spans) and the voice script."""
# (start, end, who, text)   who: me | arian | nina | fake (the masked man on a megaphone outside) | rule (phone message)
LINES = [
    (0.8, 3.8, "fake", "آرین! آرین!... بیا بیرون. ما پلیسیم!"),
    (6.6, 8.0, "arian", "پلیس اومد! تموم شد!"),
    (8.6, 11.4, "me", "وایسا! قانون دو... به اسمت جواب نده."),
    (12.2, 15.0, "nina", "دوربین جلوی در رو ببینید... پلیس نیستن."),
    (15.6, 17.8, "arian", "خودشونن... با همون نقاب‌ها."),
    (19.2, 23.8, "rule", "قانون ۶ — ده ثانیه دیگه نینا گوشیش رو درمیاره. نذار زنگ بزنه."),
    (27.4, 29.0, "me", "نینا! به کی زنگ می‌زنی؟"),
    (29.6, 32.4, "nina", "به مامانم... باید بدونه کجام."),
    (34.2, 36.6, "nina", "از در پشتی! دنبالم بیاید!"),
    (56.0, 58.8, "nina", "اینجا امنه... هیچ‌کس اینجا رو نمی‌دونه."),
    (62.6, 65.6, "rule", "قانون ۷ — برنگرد."),
    (66.4, 68.2, "me", "یکی... پشت سرمونه."),
]
NAMES = {"me": "من", "arian": "آرین", "nina": "نینا", "fake": "بلندگوی بیرون", "rule": "پیام"}
END = 75.5            # picture ends (then the question card)
TITLE = "قانون‌ها"
SUBTITLE = "قسمت دوم"
QUESTION = "تو بودی... برمی‌گشتی نگاه کنی؟"
# phone screens shown full-size in post (start, end, which): rule texts appear as a phone message box
PHONE = [(19.0, 24.2, "rule6"), (62.4, 66.2, "rule7")]


def speaking(who, t, pad=0.0):
    return any(a - pad <= t <= b + pad for a, b, w, _ in LINES if w == who)
