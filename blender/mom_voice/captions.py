"""«صدای مامان» — every spoken line (seconds). Single source for captions, lip sync, voices and the voice script.
Times are fitted to the ElevenLabs takes in voices/ (start = when the clip starts in the film)."""
# (start, end, who, text, clip)
LINES = [
    (3.6, 7.64, "mom_phone", "سلام عزیزم... من هنوز تو ترافیکم. یه ساعت دیگه می‌رسم خونه.", "l1_mom_phone"),
    (9.2, 11.06, "mom", "بچه‌ها! بیاید، شام حاضره!", "l2_mom_kitchen"),
    (16.2, 19.4, "arian", "مامان تو آشپزخونه‌ست... پس تو داری با کی حرف می‌زنی؟", "l3_arian"),
    (20.4, 25.88, "mom_phone", "الو؟ چرا ساکتی؟ ... در رو برای هیچکس باز نکنید، باشه؟", "l4_mom_phone"),
    (28.0, 30.04, "mom", "چرا نمیاید؟ ... غذا سرد میشه.", "l5_mom_door"),
]
NAMES = {"mom_phone": "مامان (پشت تلفن)", "mom": "مامان", "arian": "آرین"}
TITLE = "صدای مامان"
END = 33.0
QUESTION = "اگه جای من بودی، حرف کدوم مامان رو باور می‌کردی؟"


def speaking(who, t):
    return any(a <= t <= b and w == who for a, b, w, _, _ in LINES)
