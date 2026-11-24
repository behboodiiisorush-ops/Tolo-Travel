"""Narration and on-screen text of «واگن آخر ۲».

Episode 2 is told with voice-over only (no lip-sync): we kneel in the open door of the train
at the border, holding Lena's hand while the train starts rolling back towards the last wagon.
"""

# (start, end, speaker, text): the speaker's jaw moves while they talk (Lena,
# Mum); Rahim is off screen at the front of the train, grandma's line is her voice message
# from episode 1 echoing in our head.
CAPTIONS = [
    (0.4, 4.0, "Me", "قطار داره برمی‌گرده..."),
    (8.4, 9.8, "Mom", "لنا! برگرد اینجا!"),
    (13.6, 15.2, "Mom", "بپر پایین! قطار داره میره!"),
    (18.0, 19.4, "Lena", "دستمو ول نکنیا..."),
    (31.2, 33.8, "Grandma voice", "من زنده‌ام...\nمنتظرتونم..."),
    (36.0, 37.4, "Rahim", "هر کی می‌مونه، بیاد بالا!"),
    (40.8, 42.2, "Lena", "تو هم میای... مگه نه؟"),
    (45.0, 49.8, "Me", "اگه برم، لنا تنها می‌مونه.\nاگه بمونم، مامان‌بزرگ تنها می‌مونه."),
]
NARRATION = {0.4, 45.0}  # start times of the narrator's inner voice (big centred text, no name)

# the viewer question, shown at the start, in the middle and on the final card
QUESTION = "اگه تو بودی از قطار پیاده می‌شدی یا می‌موندی؟"
QUESTION_AT = [(0.8, 4.6), (26.5, 30.0)]
SUB_QUESTION = "قسمت ۳ رو چی انتخاب می‌کنی؟"

END = 52.0        # last rendered second; the question card follows
CARD_SECONDS = 10  # 5 s question + 5 s hold
