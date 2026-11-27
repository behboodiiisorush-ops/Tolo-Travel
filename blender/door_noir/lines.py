"""«در رو باز نکن» — every spoken line (film seconds). Single source for captions, lips, sound and the voice script.
(start, end, who, text, voice file in voices/, how it is heard)"""
LINES = [
    (0.30, 2.80, "me_msg", "در رو باز نکن... اون مامان نیست.", "01_me_msg", "phone"),
    (6.20, 10.60, "fake", "عزیزم؟ منم... کلیدم رو جا گذاشتم. در رو باز کن.", "02_fake_key", "door"),
    (19.00, 19.90, "me", "مامان؟", "03_me_mom", "me"),
    (20.20, 26.30, "mom", "الو عزیزم؟ من که امشب تا صبح شیفتم... بیمارستانم. چیزی شده؟", "04_mom_call", "phone"),
    (26.90, 29.00, "fake", "چرا در رو باز نمی‌کنی؟", "05_fake_why", "door"),
    (29.30, 33.00, "mom", "کی پشت دره؟... هر کاری می‌کنی، در رو باز نکن!", "06_mom_dont", "phone"),
    (36.80, 39.20, "fake", "چرا... باز نکردی؟", "07_fake_behind", "close"),
    (42.00, 44.50, "me", "در رو باز نکن... اون مامان نیست.", "01_me_msg", "me"),
]
NAMES = {"me_msg": "پیام صوتی از: من", "fake": "مامان (پشت در)", "me": "من", "mom": "مامان (پشت تلفن)"}
NAMES_CLOSE = "مامان؟"                       # line 7: she is inside now
END = 47.0
FPS = 24
QUESTION = "اگه یه پیام از خودت می‌گرفتی، باورش می‌کردی؟"
TITLE = "در رو باز نکن"
PEEP = [(14.2, 17.7), (26.6, 29.2), (33.0, 36.0)]     # seen through the door's peephole
BLACK = (40.2, 41.0)                                   # cut to black after the reveal
PITCH = {"me": 1.5, "me_msg": 1.5}                     # the cast rule: «من» +1.5 semitones


def fr(t):
    return int(round(t * FPS)) + 1


def peep(t):
    return any(a <= t < b for a, b in PEEP)
