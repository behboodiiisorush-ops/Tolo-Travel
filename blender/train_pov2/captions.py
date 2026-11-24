"""Narration and on-screen text of «واگن آخر ۲».

Episode 2 is told with voice-over only (no lip-sync): we kneel in the open door of the train
at the border, holding Lena's hand while the train starts rolling back towards the last wagon.
"""

# Timed to the recorded voices (voices/recording_1.mp3).
# (start, end, speaker, text): the speaker's jaw moves while they talk (Lena,
# Mum); Rahim is off screen at the front of the train, grandma's line is her voice message
# from episode 1 echoing in our head.
CAPTIONS = [
    (0.3, 2.5, "Me", "قطار داره برمی‌گرده..."),
    (2.8, 4.4, "Lena", "داره راه میفته!"),
    (4.7, 6.4, "Me", "دستمو محکم بگیر، لنا."),
    (6.7, 8.5, "Mom", "لنا! برگرد اینجا!"),
    (8.8, 11.0, "Lena", "مامان داره صدام می‌کنه..."),
    (11.3, 13.3, "Me", "می‌دونم... می‌دونم."),
    (13.6, 16.1, "Mom", "بپر پایین! قطار داره میره!"),
    (16.4, 19.7, "Me", "مامان اون طرف فنسه...\nمامان‌بزرگ این طرف."),
    (20.0, 21.6, "Lena", "دستمو ول نکنیا..."),
    (21.9, 24.3, "Me", "ول نمی‌کنم. قول دادم."),
    (24.6, 26.6, "Lena", "مامان‌بزرگ تنهاست؟"),
    (26.9, 27.6, "Me", "...آره."),
    (27.9, 31.0, "Me", "هر ثانیه...\nیکی‌شون ازم دورتر میشه."),
    (32.0, 34.7, "Grandma voice", "من زنده‌ام...\nمنتظرتونم..."),
    (35.0, 36.9, "Rahim", "هر کی می‌مونه، بیاد بالا!"),
    (37.2, 39.5, "Rahim", "دارم درو می‌بندم!\nزود باشید!"),
    (39.8, 42.2, "Lena", "تو هم میای... مگه نه؟"),
    (42.5, 44.2, "Lena", "منو تنها نذار..."),
    (44.8, 50.0, "Me", "اگه برم، لنا تنها می‌مونه.\nاگه بمونم، مامان‌بزرگ تنها می‌مونه."),
    (50.3, 52.7, "Mom", "لنا! ولش کن! بیا!"),
    (53.0, 54.3, "Lena", "نمی‌خوام!"),
    (54.6, 56.2, "Rahim", "آخرین فرصته!"),
    (56.8, 59.7, "Me", "و من فقط...\nیه ثانیه وقت داشتم."),
]
NARRATION = {0.3, 16.4, 27.9, 44.8, 56.8}  # start times of the narrator's inner voice (big centred text, no name)

# the viewer question, shown at the start, in the middle and on the final card
QUESTION = "اگه تو بودی از قطار پیاده می‌شدی یا می‌موندی؟"
QUESTION_AT = [(0.8, 4.6), (26.5, 30.0)]
SUB_QUESTION = "قسمت ۳ رو چی انتخاب می‌کنی؟"

END = 60.0        # last rendered second; the question card follows
CARD_SECONDS = 10  # 5 s question + 5 s hold
