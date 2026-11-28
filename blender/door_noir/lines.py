"""«در رو باز نکن» — every spoken line (film seconds). Single source for captions, lips, sound and the voice script.
(start, end, who, text, voice file in voices/, how it is heard)"""
LINES = [
    (0.30, 3.00, "me_msg", "در رو باز نکن... اون مامان نیست.", "user/01_me_msg", "phone"),
    (6.20, 11.00, "fake", "عزیزم؟ منم... کلیدم رو جا گذاشتم. در رو باز کن.", "user/02_fake_key", "door"),
    (19.00, 19.90, "me", "مامان؟", "user/03_me_mom", "me"),
    (20.20, 26.00, "mom", "الو عزیزم؟ من که امشب تا صبح شیفتم... بیمارستانم. چیزی شده؟", "user/04_mom_call", "phone"),
    (26.90, 29.10, "fake", "چرا در رو باز نمی‌کنی؟", "user/05_fake_why", "door"),
    (29.30, 33.00, "mom", "کی پشت دره؟... هر کاری می‌کنی، در رو باز نکن!", "user/06_mom_dont", "phone"),
    (36.80, 37.70, "brother", "داداش؟", "user/08_brother_call", "close"),
    (39.30, 41.40, "brother", "داداش... ترسیدم.", "user/09_brother_scared", "me"),
    (56.70, 60.40, "fake", "منم... مادرت. پسرم، در رو باز کن.", "user/10_fake_mother", "door"),
]
NAMES = {"me_msg": "پیام صوتی از: من", "fake": "مامان (پشت در)", "me": "من", "mom": "مامان (پشت تلفن)",
         "brother": "داداش کوچیکم"}
END = 60.5
FPS = 24
QUESTION = "تو بودی باز می‌کردی؟"
TITLE = "در رو باز نکن"
PEEP = [(14.2, 17.7), (26.6, 29.2), (33.0, 36.0)]     # seen through the door's peephole
BLACK = (99.0, 99.5)                                   # (no black cut any more)
PITCH = {}                                             # the user: voices exactly as ElevenLabs made them


def fr(t):
    return int(round(t * FPS)) + 1


def peep(t):
    return any(a <= t < b for a, b in PEEP)
