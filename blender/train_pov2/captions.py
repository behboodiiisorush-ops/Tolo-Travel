"""Narration and on-screen text of «واگن آخر ۲».

Episode 2 is told with voice-over only (no lip-sync): we kneel in the open door of the train
at the border, holding Lena's hand while the train starts rolling back towards the last wagon.
"""

# (start, end, speaker, text): "Me" is the narrator's voice-over, nobody's jaw moves.
CAPTIONS = [
    (0.4, 4.0, "Me", "قطار داره برمی‌گرده..."),
    (45.0, 49.8, "Me", "اگه برم، لنا تنها می‌مونه.\nاگه بمونم، مامان‌بزرگ تنها می‌مونه."),
]

# the viewer question, shown at the start, in the middle and on the final card
QUESTION = "اگه تو بودی از قطار پیاده می‌شدی یا می‌موندی؟"
QUESTION_AT = [(0.8, 4.6), (26.5, 30.0)]
SUB_QUESTION = "قسمت ۳ رو چی انتخاب می‌کنی؟"

END = 52.0        # last rendered second; the question card follows
CARD_SECONDS = 10  # 5 s question + 5 s hold
