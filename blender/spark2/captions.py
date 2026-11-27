"""«جرقه ۲» — the same night: the kid across the street answers, a message appears on Arian's screen.
Every spoken line (seconds). Single source for captions, lip sync and the voice script."""
# (start, end, who, text)
LINES = [
    (2.5, 4.6, "arian", "هنوز اونجاست..."),
    (9.4, 10.9, "arian", "سلام...؟"),
    (16.0, 17.8, "arian", "داره جواب می‌ده!"),
    (27.0, 31.0, "arian", "فردا... ساعت دوازده... پشت‌بوم؟"),
    (32.6, 34.6, "mom", "آرین؟ هنوز بیداری؟"),
    (35.6, 37.6, "arian", "دارم می‌خوابم مامان!"),
    (48.5, 50.8, "arian", "تو کی هستی...؟"),
]
NAMES = {"arian": "آرین", "mom": "مامان (پشت در)"}
END = 54.0
QUESTION = "اگه جای آرین بودی، فردا می‌رفتی پشت‌بوم؟"
SCREEN = ["فردا.", "ساعت ۱۲.", "پشت‌بوم."]     # the message on Arian's monitor (letters appear 23.5-26.5 s)


def speaking(who, t):
    return any(a <= t <= b and w == who for a, b, w, _ in LINES)
