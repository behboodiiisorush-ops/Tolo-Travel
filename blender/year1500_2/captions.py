"""«سال ۱۵۰۰ — قسمت دوم» — every spoken line (seconds), fitted to the ElevenLabs takes in voices/.
Single source for captions, voice placement (voices.py) and lip sync (lips.py)."""
# (start, end, who, text, take)
LINES = [
    (0.8, 6.7, "me", "دو روز بود چیزی نخورده بودیم. شهر پر از غذا بود... ولی هیچ‌کس توش نبود.", "01_me"),
    (9.5, 13.6, "kian", "داداش، ببین! همه‌ی مغازه‌ها درشون بازه!", "02_kian"),
    (14.2, 17.6, "me", "آره... ولی چرا هیچ‌کس نیست؟", "03_me"),
    (21.0, 23.8, "kian", "شنیدی؟... اون صدا چی بود؟", "04_kian"),
    (25.0, 28.7, "me", "هیچی نیست. زود یه چیزی برداریم و بریم.", "05_me"),
    (36.4, 40.8, "kian", "اینجا همه‌چی هست! نون، کنسرو، آب...", "06_kian"),
    (50.8, 57.3, "voice", "خوش اومدی... به دنیای فانی.", "07_voice"),
    (59.2, 61.5, "kian", "داداش! بریم! بریم!", "08_kian"),
    (69.6, 72.8, "me", "صبر کن... یه نفر اونجاست!", "09_me"),
    (80.4, 82.2, "kian", "بریم دنبالش؟", "10_kian"),
]
NAMES = {"me": "من", "kian": "کیان", "voice": "بلندگو"}
END = 86.0
CARD = (86.2, "11_card")                      # the question card's voice (start, take)
TITLE = "سال ۱۵۰۰"
SUBTITLE = "قسمت دوم"
QUESTION = "اگه جای ما بودی... دنبالش می‌رفتی؟"
FLASHBACK = (-10.0, -9.0)                     # (none in this episode; post.py's flashback grade stays off)
WAKE = -10.0
SPEAKER = (50.0, 57.6)                        # the shop's speaker crackles on, laughs, talks
