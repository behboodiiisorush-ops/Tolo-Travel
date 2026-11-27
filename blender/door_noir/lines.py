"""«در رو باز نکن» — every spoken line (film seconds). Single source for captions, lips, sound and the voice script.
(start, end, who, text, voice file in voices/, how it is heard)"""
LINES = [
    (0.30, 2.50, "me_msg", "در رو باز نکن... اون مامان نیست.", "01_me_msg", "phone"),
    (6.20, 10.60, "fake", "عزیزم؟ منم... کلیدم رو جا گذاشتم. در رو باز کن.", "02_fake_key", "door"),
    (19.00, 19.80, "me", "مامان؟", "03_me_mom", "me"),
    (20.20, 26.30, "mom", "الو عزیزم؟ من که امشب تا صبح شیفتم... بیمارستانم. چیزی شده؟", "04_mom_call", "phone"),
    (26.90, 28.90, "fake", "چرا در رو باز نمی‌کنی؟", "05_fake_why", "door"),
    (29.30, 32.40, "mom", "کی پشت دره؟... هر کاری می‌کنی، در رو باز نکن!", "06_mom_dont", "phone"),
    (36.80, 37.80, "brother", "داداش؟", "08_brother_call", "close"),
    (39.30, 40.80, "brother", "داداش... ترسیدم.", "09_brother_scared", "me"),
]
NAMES = {"me_msg": "پیام صوتی از: من", "fake": "مامان (پشت در)", "me": "من", "mom": "مامان (پشت تلفن)",
         "brother": "داداش کوچیکم"}
END = 42.0
FPS = 24
QUESTION = "اگه جای من بودی، در رو باز می‌کردی؟"
TITLE = "در رو باز نکن"
PEEP = [(14.2, 17.7), (26.6, 29.2), (33.0, 36.0)]     # seen through the door's peephole
BLACK = (41.2, 43.0)                                   # black after my brother; a knock in the dark
PITCH = {}                                             # the user: voices exactly as ElevenLabs made them


def fr(t):
    return int(round(t * FPS)) + 1


def peep(t):
    return any(a <= t < b for a, b in PEEP)
