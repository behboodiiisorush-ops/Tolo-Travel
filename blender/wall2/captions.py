"""«دیوار ۲» — every spoken line (seconds of film time, the opening card not counted).
Single source for captions, lip sync and the ElevenLabs voices (voices/NN_who.mp3, placed at VOICE start)."""
# (start, end, who, text) — start/end = where the speech really is inside the generated clip
LINES = [
    (1.16, 3.84, "kian", "آروم برید عقب... به چشماش نگاه نکنید."),
    (4.56, 8.64, "rezaei", "چرا می‌ترسین؟ من فقط... گرسنمه."),
    (9.56, 11.14, "mom", "بچه‌ها! برگردین!"),
    (19.26, 20.8, "kazemi", "مبل! کمک کن!"),
    (39.64, 42.42, "arian", "آنتن اومد! یه پیام اومده."),
    (43.36, 49.04, "arian", "درها ساعت شش صبح باز می‌شن... فقط اگه هیچ‌کس آلوده نباشه."),
    (50.14, 53.36, "mom", "چیزی نمونده... همه‌مون سالمیم."),
    (54.52, 57.1, "mahsa", "دستت... چرا خون میاد؟"),
    (58.48, 61.32, "me", "این... از دیواره. فکر کنم."),
]
# ElevenLabs clips and where each one starts in the film
VOICE = [("01_kian", 1.0), ("02_rezaei", 4.4), ("03_mom", 9.4), ("04_kazemi", 19.2), ("05_arian", 39.6),
         ("06_arian", 43.2), ("07_mom", 50.0), ("08_mahsa", 54.4), ("09_me", 58.4)]
NAMES = {"mom": "مامان", "kazemi": "آقای کاظمی", "arian": "آرین", "mahsa": "مهسا", "rezaei": "آقای رضایی",
         "kian": "کیان", "me": "من"}
END = 64.5
TITLE = "دیوار ۲"
QUESTION = "اگه جای اونا بودی، حرفش رو باور می‌کردی؟"
# the message on Arian's phone (shown as a screen insert while he reads it)
MESSAGE = (43.2, 49.4, "درها ساعت ۶ صبح باز می‌شوند.\nفقط اگر هیچ‌کس آلوده نباشد.")


def speaking(who, t):
    return any(a <= t <= b and w == who for a, b, w, _ in LINES)
