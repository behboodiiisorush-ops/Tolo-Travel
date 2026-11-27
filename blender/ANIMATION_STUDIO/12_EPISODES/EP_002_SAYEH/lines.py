"""«سایه‌ی دانیال» — every spoken line (seconds). Single source for captions, lip flaps and the voice script."""
# (start, end, who, text)
LINES = [
    (2.6, 4.6, "mother", "دانیال! باز دیر کردی."),
    (6.2, 7.6, "lina", "برق رفت؟"),
    (13.4, 15.2, "arian", "اون... چیه؟!"),
    (15.6, 17.0, "father", "تکون نخورین!"),
    (18.6, 21.6, "daniel", "صبر کنین... سایه‌ی من کجاست؟"),
    (27.9, 29.6, "daniel", "...خوش برگشتی."),
]
NAMES = {"mother": "مامان", "father": "بابا", "arian": "آرین", "lina": "لینا", "daniel": "دانیال"}
END = 31.0
QUESTION = "اگه سایه‌ت یه روز ازت جدا بشه، کجا می‌ره؟"
FPS = 24


def fr(t):
    return int(round(t * FPS)) + 1

# cold open (the hook): this part of the film plays first, then a black card, then the film from the start
COLD = (17.6, 21.6)
COLD_CARD = (1.3, "ده دقیقه قبل...")
