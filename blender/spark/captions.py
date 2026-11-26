"""«جرقه» — Arian, alone in his room on a stormy night, finds that electricity obeys his hand.
Every spoken line (seconds). Single source for captions, lip sync and the voice script.
Voices: ElevenLabs v4, Arian = "amir", Mom = "Sara - Neutral Persian Female"; clips in voices/clips (a1..a6, m1)."""
# (start, end, who, text)
LINES = [
    (3.0, 6.1, "arian", "یه سؤال دیگه مونده... بعدش می‌خوابم."),
    (11.0, 14.55, "arian", "ای بابا... باز برق رفت."),
    (19.5, 22.4, "arian", "آخ! این... چیه؟"),
    (27.0, 29.5, "mom", "آرین؟ چراغ‌قوه داری؟"),
    (29.9, 32.15, "arian", "آ... آره مامان! دارم!"),
    (40.0, 41.6, "arian", "این... کار منه؟"),
    (52.0, 54.1, "arian", "یعنی... من تنها نیستم؟"),
]
NAMES = {"arian": "آرین", "mom": "مامان (پشت در)"}
END = 58.0
QUESTION = "اگه جای آرین بودی، به مامانت می‌گفتی؟"


def speaking(who, t):
    return any(a <= t <= b and w == who for a, b, w, _ in LINES)

CLIPS = ["a1", "a2", "a3", "m1", "a4", "a5", "a6"]   # voice clip per line, in LINES order
