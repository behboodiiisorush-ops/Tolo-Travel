"""«جرقه» — Arian, alone in his room on a stormy night, finds that electricity obeys his hand.
Every spoken line (seconds). Single source for captions, lip sync and the voice script.
Times are estimates until the user's voices arrive (then cut_voices + layout fix them)."""
# (start, end, who, text)
LINES = [
    (3.0, 5.6, "arian", "یه سؤال دیگه مونده... بعدش می‌خوابم."),
    (11.0, 13.0, "arian", "ای بابا... باز برق رفت."),
    (19.5, 21.0, "arian", "آخ! این... چیه؟"),
    (27.0, 29.2, "mom", "آرین؟ چراغ‌قوه داری؟"),
    (29.8, 31.8, "arian", "آ... آره مامان! دارم!"),
    (40.0, 42.0, "arian", "این... کار منه؟"),
    (52.0, 54.8, "arian", "یعنی... من تنها نیستم؟"),
]
NAMES = {"arian": "آرین", "mom": "مامان (پشت در)"}
END = 58.0
QUESTION = "اگه جای آرین بودی، به مامانت می‌گفتی؟"


def speaking(who, t):
    return any(a <= t <= b and w == who for a, b, w, _ in LINES)
