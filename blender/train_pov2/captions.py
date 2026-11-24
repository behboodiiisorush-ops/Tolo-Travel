"""Narration and on-screen text of «واگن آخر ۲».

Episode 2 is told with voice-over only (no lip-sync): we kneel in the open door of the train
at the border, holding Lena's hand while the train starts rolling back towards the last wagon.
"""

# (start, end, speaker, text): the speaker's jaw moves while they talk (Lena,
# Mum); Rahim is off screen at the front of the train, grandma's line is her voice message
# from episode 1 echoing in our head.
CAPTIONS = [
    (0.4, 4.0, "Me", "قطار داره برمی‌گرده..."),
    (4.5, 6.0, "Lena", "داره راه میفته!"),
    (6.4, 7.8, "Me", "دستمو محکم بگیر، لنا."),
    (8.4, 9.8, "Mom", "لنا! برگرد اینجا!"),
    (10.2, 11.5, "Lena", "مامان داره صدام می‌کنه..."),
    (11.8, 12.8, "Me", "می‌دونم... می‌دونم."),
    (13.2, 14.9, "Mom", "بپر پایین! قطار داره میره!"),
    (15.4, 17.6, "Me", "مامان اون طرف فنسه...\nمامان‌بزرگ این طرف."),
    (18.0, 19.4, "Lena", "دستمو ول نکنیا..."),
    (20.0, 21.4, "Me", "ول نمی‌کنم. قول دادم."),
    (22.5, 24.2, "Lena", "مامان‌بزرگ تنهاست؟"),
    (24.8, 25.8, "Me", "...آره."),
    (27.0, 29.6, "Me", "هر ثانیه...\nیکی‌شون ازم دورتر میشه."),
    (31.2, 33.8, "Grandma voice", "من زنده‌ام...\nمنتظرتونم..."),
    (35.8, 37.2, "Rahim", "هر کی می‌مونه، بیاد بالا!"),
    (38.0, 39.6, "Rahim", "دارم درو می‌بندم!\nزود باشید!"),
    (40.8, 42.2, "Lena", "تو هم میای... مگه نه؟"),
    (43.0, 44.4, "Lena", "منو تنها نذار..."),
    (45.0, 49.8, "Me", "اگه برم، لنا تنها می‌مونه.\nاگه بمونم، مامان‌بزرگ تنها می‌مونه."),
    (50.5, 52.0, "Mom", "لنا! ولش کن! بیا!"),
    (52.5, 53.8, "Lena", "نمی‌خوام!"),
    (54.2, 55.6, "Rahim", "آخرین فرصته!"),
    (56.5, 59.6, "Me", "و من فقط...\nیه ثانیه وقت داشتم."),
]
NARRATION = {0.4, 15.4, 27.0, 45.0, 56.5}  # start times of the narrator's inner voice (big centred text, no name)

# the viewer question, shown at the start, in the middle and on the final card
QUESTION = "اگه تو بودی از قطار پیاده می‌شدی یا می‌موندی؟"
QUESTION_AT = [(0.8, 4.6), (26.5, 30.0)]
SUB_QUESTION = "قسمت ۳ رو چی انتخاب می‌کنی؟"

END = 60.0        # last rendered second; the question card follows
CARD_SECONDS = 10  # 5 s question + 5 s hold
