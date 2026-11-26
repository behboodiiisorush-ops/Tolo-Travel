"""Lines of «پناهگاه ۳ — اتوبوس نجات» (long, 16:9).  Times come from times.py (layout.py: from the
recorded voices, or estimated from the text until the recording arrives).

The rescuer first speaks through the bus loudspeaker; Radio is an unknown voice on our walkie-talkie.
"""

LINES = [
    ("n1", "Me", "یک هفته گذشته بود...\nبیشتر آدما دیگه زنده نبودن."),
    ("n2", "Me", "اونایی هم که زنده موندن...\nدیگه مثل قبل نبودن."),
    ("lena1", "Lena", "داداش... چرا دست آقای نگهبان می‌لرزه؟"),
    ("guard1", "Guard", "چیزی نیست، دخترم... فقط خسته‌ام."),
    ("mom1", "Mom", "آب فقط واسه دو روز دیگه مونده."),
    ("me1", "Me", "این بی‌سیم تنها چیزیه که هنوز کار می‌کنه...\nولی هیچ‌کس جواب نمی‌ده."),
    ("resc1", "Rescuer", "ما گروه نجاتیم!\nاگه کسی زنده‌ست، درو باز کنه!"),
    ("lena2", "Lena", "صدای آدمه! یه آدم واقعی!"),
    ("guard2", "Guard", "صبر کنید! شاید تله باشه."),
    ("resc2", "Rescuer", "فقط پنج دقیقه اینجاییم!\nبعدش میریم!"),
    ("mom2", "Mom", "اگه نریم، اینجا از گشنگی می‌میریم."),
    ("guard3", "Guard", "چراغ سبزه... برید.\nمن پشت سرتونم."),
    ("me2", "Me", "درو باز می‌کنم!"),
    ("n3", "Me", "یه اتوبوس قدیمی بود...\nپر از آدمای خسته و خاکی."),
    ("resc3", "Rescuer", "سریع سوار شید!\nتا شب نشده باید از شهر رد شیم."),
    ("old1", "Old man", "خوش اومدید...\nاگه بشه اسمش رو گذاشت خوش‌آمد."),
    ("lena3", "Lena", "کجا داریم میریم؟"),
    ("resc4", "Rescuer", "اون طرف مرز.\nمیگن اونجا هوا هنوز پاکه."),
    ("n4", "Me", "از وسط شهری رد شدیم...\nکه یه روزی خونه‌مون بود."),
    ("mom3", "Mom", "اون... مدرسه‌ت بود."),
    ("me3", "Me", "دیگه چیزی ازش نمونده."),
    ("old2", "Old man", "سه بار تا حالا این مسیر رو رفتیم.\nهر بار یه نفر کمتر برگشت."),
    ("lena4", "Lena", "یعنی چی یه نفر کمتر؟"),
    ("mom4", "Mom", "هیچی عزیزم... بخواب."),
    ("radio1", "Radio", "به هر کی صدامو می‌شنوه...\nاز جادهٔ جنگل نیاید... حیوونا..."),
    ("me4", "Me", "بی‌سیم! یکی داره حرف می‌زنه!"),
    ("resc5", "Rescuer", "جادهٔ دیگه‌ای نداریم.\nباید از جنگل رد شیم."),
    ("n5", "Me", "توی جنگل...\nهمه‌چی زیادی ساکت بود."),
    ("lena5", "Lena", "اون چشما چیه لای درختا؟"),
    ("old3", "Old man", "سگای وحشی...\nولی اینا دیگه سگ نیستن."),
    ("resc6", "Rescuer", "محکم بشینید! گاز میدم!"),
    ("me5", "Me", "دارن لاستیکا رو می‌جوَن!"),
    ("resc7", "Rescuer", "لاستیک ترکید!\nنمی‌تونم کنترلش کنم!"),
    ("mom5", "Mom", "لنا! بیا اینجا! سرتو بدزد!"),
    ("n6", "Me", "اتوبوس وایستاد...\nو صدای پنجه‌ها از همه طرف میومد."),
    ("radio2", "Radio", "صدامو دارید...؟\nما شما رو می‌بینیم..."),
    ("me6", "Me", "شما کی هستید؟!"),
    ("n7", "Me", "بی‌سیم ساکت شد...\nو چراغای یه ماشین، از ته جاده روشن شد."),
]
NARRATION_KEYS = {"n1", "n2", "n3", "n4", "n5", "n6", "n7"}

TIMES, TAIL, TITLE = {}, 3.0, 2.6
try:
    from times import TIMES, TAIL, TITLE  # noqa: F401
except ImportError:
    pass

CAPTIONS = [(TIMES.get(k, (0, 0))[0], TIMES.get(k, (0, 0))[1], who, text) for k, who, text in LINES]
NARRATION = {TIMES[k][0] for k in NARRATION_KEYS if k in TIMES}
KEY_OF = {k: TIMES.get(k, (0, 0)) for k, _, _ in LINES}

QUESTION = "اگه تو بودی...\nاز اتوبوس پیاده می‌شدی\nیا منتظر اون ماشین می‌موندی؟"
END = max([e for s, e in TIMES.values()], default=180.0) + TAIL
CARD_SECONDS = 8
NOTIFS = []

CAST_KEY = {"Me": "me", "Mom": "mom", "Lena": "lena", "Guard": "guard", "Rescuer": "rescuer", "Old man": "oldman"}
SPEAKERS = {"Me": ("من", (60, 160, 80)), "Mom": ("مامان", (150, 40, 80)), "Lena": ("لنا", (210, 50, 45)),
            "Guard": ("نگهبان", (230, 120, 20)), "Rescuer": ("امدادگر", (200, 40, 40)),
            "Old man": ("پیرمرد", (120, 90, 60)), "Radio": ("بی‌سیم", (40, 110, 160))}


def at(key):
    return KEY_OF[key][0]


def end_of(key):
    return KEY_OF[key][1]


def speaking(cast_key, t):
    return any(CAST_KEY.get(who) == cast_key and TIMES.get(k, (0, -1))[0] <= t <= TIMES.get(k, (0, -1))[1]
               for k, who, _ in LINES)
