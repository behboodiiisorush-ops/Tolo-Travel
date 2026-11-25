# «زنگ آخر» — نسخهٔ کارتونی با هوش مصنوعی (هوش مصنوعی + تدوین ما)

همان داستان و همان زمان‌بندی `blender/last_bell_real/voice_script.md`، ولی هر شات با ابزار
«تصویر ← ویدیو» (Veo / Kling / Runway / Sora) و با ظاهر **خیلی کارتونی** ساخته می‌شود:
انیمیشن سه‌بعدی سینمایی، چشم‌های درشت، بدن‌های اغراق‌شده، رنگ‌های شاد، حرکت کش‌دار و پرانرژی.
شخصیت‌ها همان بازیگران ثابت `blender/cast/` هستند، فقط کارتونی‌شده.

## روند کار (۴ مرحله)

1. **تصویر مرجع کارتونی هر شخصیت** (یک بار برای همیشه) — بخش ۳.
   عکس `blender/cast/sheets/<key>_face.png` و `<key>_full.png` را به ابزار تصویر بدهید
   (حالت image-to-image / character reference) + پرامپت همان شخصیت. از بین نتیجه‌ها **یکی** را انتخاب کنید
   و اسمش را بگذارید `ref_<key>.png`. از این به بعد همیشه همین یک عکس مرجع است.
2. **فریم شروع هر شات** — پرامپت «Start frame» هر شات + عکس‌های مرجع شخصیت‌های داخل آن شات.
3. **ویدیو** — فریم شروع را بدهید به حالت image-to-video + پرامپت «Motion» + بلوک حرکت کارتونی. نسبت ۹:۱۶.
   - **صدای ساخته‌شده را خاموش کنید** — صداها را خودتان با ElevenLabs می‌سازید.
   - در شات‌هایی که کسی حرف می‌زند، عبارت *speaking* در پرامپت هست تا لب‌ها تکان بخورد.
   - از هر شات ۲ تا ۴ نسخه بگیرید و بهترین را نگه دارید.
4. **تحویل به من** — فایل‌ها را با اسم شات (`S01.mp4`, `S02.mp4`, …) آپلود کنید.
   من: برش و ترتیب، یکسان کردن رنگ، زیرنویس فارسی (وزیرمتن)، جای صداها، افکت صوتی، خروجی نهایی.

## قوانین ثابت (در همهٔ شات‌ها)
- هیچ‌کس حجاب ندارد.
- هیچ پرچم، آرم، نشان، نوشته روی دیوار، اسم مکان یا لوگوی تلویزیون/ارتش. هلیکوپتر و کامیون بی‌علامت.
- زامبی‌ها کارتونی: سبز کم‌رنگ، چشم سفید گرد، لباس پاره — بدون خون واقعی (ابزارها هم راحت‌تر قبول می‌کنند).

---

## ۱. بلوک سبک — آخر *همهٔ* پرامپت‌های تصویر و ویدیو اضافه شود

```
Stylized 3D animated feature film look, very cartoony: big expressive eyes, exaggerated
proportions, oversized heads and hands, soft rounded shapes, smooth clean skin, bright saturated
colours, warm cinematic lighting with rim light, playful toy-like environments,
vertical 9:16 frame. Iranian characters with warm olive skin.
No text, no logos, no flags, no emblems, no signs, no headscarves.
```

### بلوک حرکت — فقط آخر پرامپت‌های «Motion»

```
Snappy exaggerated cartoon animation: squash and stretch, big anticipation before every action,
bouncy follow-through, rubbery limbs, huge facial expressions, cartoon sweat drops and
motion lines when scared or rushing.
```

### سبک‌های جایگزین (اگر خواستید عوض کنید — فقط بلوک سبک را جابه‌جا کنید)
- **دوبعدی دستی:** `Hand-drawn 2D cartoon, thick clean black outlines, flat bright colours, simple painted backgrounds, big round eyes, 9:16.`
- **مثل «واگن آخر» خودمان (تون):** `Toon-shaded 3D puppet characters, bold black outlines, flat cel shading, chunky simple shapes, saturated colours, 9:16.`

## ۲. پرامپت منفی (اگر ابزار جایش را دارد)

```
photorealistic, realistic skin, live action, photo, uncanny, gore, realistic blood, extra fingers,
deformed hands, text, watermark, logo, flag, emblem, insignia, subtitles, headscarf, hijab, blurry face
```

---

## ۳. شخصیت‌ها — متن ثابت هر نفر (عیناً کپی شود، هر بار همین)

| key | نام | Identity block (انگلیسی، ثابت) |
|---|---|---|
| `me` | من | `a cartoon 15-year-old Iranian boy, slim, big dark-brown side-swept fringe flopping over one eye, navy blue hoodie, blue jeans` |
| `arian` | آرین | `a cartoon 15-year-old Iranian boy, super tall and noodle-thin with long arms, spiky short black hair, huge mischievous grin, slate-blue polo shirt, dark jeans` |
| `mahsa` | مهسا | `a cartoon 15-year-old Iranian girl, black hair in a bouncy ponytail, big red rectangular glasses, determined eyebrows, navy t-shirt, grey trousers, red flat shoes` |
| `kian` | کیان | `a tiny cartoon 13-year-old Iranian boy, round face, huge teary eyes, messy black hair, light-blue hoodie, jeans, a giant green backpack almost as big as him` |
| `mom` | مامان | `a cartoon 42-year-old Iranian mother, round friendly face, brown hair in a big tall bun, uncovered head, cream knitted sweater, navy trousers` |
| `kazemi` | آقای کاظمی | `a cartoon 50-year-old Iranian male teacher, tall and stiff, square jaw, bushy grey eyebrows, greying brown hair, thick black rectangular glasses, brown jacket and trousers` |
| `rezaei` | آقای رضایی | `a cartoon 58-year-old Iranian janitor, short and round, big grey moustache, grey slicked-back hair, kind crinkly eyes, plain blue work overalls` |
| `rezaei_z` | رضایی زامبی | `the same cartoon janitor in blue overalls, now a goofy-scary cartoon zombie: pale mint-green skin, big blank white round eyes, droopy jaw, torn dirty overalls, arms stretched forward` |
| `anchor` | گوینده اخبار | `a cartoon 45-year-old Iranian male news anchor, perfectly combed shiny dark hair, big square chin, dark suit, white shirt, plain tie` |
| `soldier` | سرباز | `a cartoon 28-year-old Iranian soldier, broad heroic shoulders, plain olive-green uniform with no patches or insignia, round olive helmet, black gloves` |

### پرامپت تصویر مرجع (مرحلهٔ ۱) — برای هر شخصیت

ورودی: `<key>_face.png` + `<key>_full.png`. پرامپت:

```
Redesign this 3D character as a cartoon animated-movie character. Keep the same hairstyle, hair
colour, glasses and clothes, but make the face and body cartoony and appealing. [IDENTITY BLOCK].
Character turnaround sheet: front view, three-quarter view and full body, plain light background,
friendly neutral expression. [STYLE BLOCK]
```

---

## ۴. شات‌ها (≈ ۷۶ ثانیه)

ستون «دیالوگ» فقط برای این است که دهان در آن لحظه تکان بخورد — متن روی تصویر نمی‌آید.
POV یعنی دوربین چشم «من» است (خودش دیده نمی‌شود، فقط گاهی دست‌هایش).

### S01 · ۰–۴ ث · اتاق خواب، صبح · POV
- **Start frame:** `First-person POV lying in bed in a modest Iranian apartment bedroom at dawn, pale light through thin curtains, a phone alarm glowing on the nightstand, the viewer's own hand reaching for it.`
- **Motion:** `Slow handheld POV: the hand turns off the alarm, the camera sits up groggily and looks toward the window. Dust in the light beam. Quiet, tense mood.`
- دیالوگ (راوی، صدای ذهن): «اون روز صبح... نباید می‌رفتم.»

### S02 · ۴–۸ ث · تلویزیون اخبار
- **Start frame:** `[anchor]. Sitting at a plain grey news desk in a simple studio, no screens with text, no logos. Seen on a living-room TV, slightly out of focus room edges.`
- **Motion:** `The anchor speaking seriously to camera, glancing down at papers, slight camera push-in toward the TV. TV screen flicker.`
- دیالوگ: «...گزارش‌ها حاکی است... ارتش دچار نابسامانی شده...»

### S03 · ۸–۱۱ ث · آشپزخانه
- **Start frame:** `[mom] standing by a small kitchen table holding a plate of bread and cheese, morning light, POV from the doorway.`
- **Motion:** `Mom speaking, holding out the plate; the POV camera hurries past her toward the front door; she turns and speaks again, worried.`
- دیالوگ: مامان «صبحونه نخوردی!» — من «دیرم شده. خداحافظ!» — مامان «زود برگردی خونه‌ها!»

### S04 · ۱۱–۱۳.۵ ث · خیابان
- **Start frame:** `POV walking down a quiet residential street of an Iranian city in early morning, parked cars, plane trees, apartment buildings, no signs.`
- **Motion:** `Walking POV with gentle head bob. A plain unmarked olive army truck drives past fast in the background. Distant birds lift off a wire.`

### S05 · ۱۳.۵–۱۵ ث · حیاط مدرسه
- **Start frame:** `[rezaei] sweeping a concrete school yard with a broom, plain building behind, no signs, morning sun.`
- **Motion:** `He looks up at the camera, smiles and waves, speaking cheerfully. POV keeps walking past him.`
- دیالوگ: «صبح بخیر! بازم دیر کردی!»

### S06 · ۱۵–۱۷ ث · کلاس
- **Start frame:** `[kazemi] standing in front of a green chalkboard with only maths scribbles, a classroom of teenage students at old wooden desks, seen from a desk in the third row.`
- **Motion:** `The teacher snaps a textbook shut and speaks sharply; students sit up straight.`
- دیالوگ: «ساکت! صفحهٔ چهل‌ودو.»

### S07 · ۱۷–۲۰ ث · آرین کنار من
- **Start frame:** `[arian] sitting at the desk right next to the camera, leaning in to whisper, in the classroom.`
- **Motion:** `Arian whispers with a grin, then freezes as the teacher [kazemi] in the background points at him and speaks.`
- دیالوگ: آرین «بازم امتحان داریم؟» — کاظمی «آرین! حواست کجاست؟»

### S08 · ۲۰–۲۶ ث · پیام صوتی مامان
- **Start frame:** `POV looking down at a smartphone hidden under a wooden desk, the screen shows only a plain audio waveform, no app interface, no text.`
- **Motion:** `The waveform plays; the thumb hesitates over the screen; the camera glances up at the teacher and back down. Close and slightly shaky.`
- دیالوگ (صدای مامان): «داره اتفاقایی میفته... مواظب خودت باش...»

### S09 · ۲۶–۳۳ ث · خنده
- **Start frame:** `[arian] laughing silently with a hand over his mouth at the next desk.`
- **Motion:** `Arian whispers a joke and laughs; then cut of focus to the background where [kazemi] slowly turns from the board with raised eyebrows and speaks.`
- دیالوگ: من «مامانم باز شلوغش کرده.» — آرین «لابد اخبار دیده!» — کاظمی «چی خنده‌داره؟»

### S10 · ۳۳–۳۷ ث · بلندگوی مدرسه
- **Start frame:** `Low angle of a plain grey wall loudspeaker above the classroom door, students below looking up.`
- **Motion:** `The speaker crackles; every student turns and looks up, frozen; the classroom light flickers once; the sound cuts off abruptly.`
- دیالوگ (بلندگو): «توجه! همه در کلاس بمونید! درها رو قفل کنید! هیچ‌کس بیرون نـ...»

### S11 · ۳۷–۴۳ ث · از پنجره
- **Start frame:** `[mahsa] standing at a classroom window, looking down into the school yard, hand on the glass. Through the window, far below: [rezaei_z] standing still with his back to us.`
- **Motion:** `The janitor twitches, his head jerks at an unnatural angle and he starts to stagger. Mahsa slowly turns to the camera, scared, speaking quietly.`
- دیالوگ: مهسا «اون... آقای رضاییه؟»

### S12 · ۴۳–۴۵ ث · چشم‌ها
- **Start frame:** `Extreme close-up of [rezaei_z] face pressed against a window from outside, big blank white eyes, cheek squished flat against the glass, breath fogging it.`
- **Motion:** `His eyes snap to the camera; he slams a palm on the glass. Behind the camera [kian] gasps (reflection in the glass).`
- دیالوگ: کیان «چشماش!»

### S13 · ۴۵–۵۰ ث · سنگر
- **Start frame:** `[kazemi] and [arian] pushing heavy wooden school desks against a classroom door, other students helping, chaos, big cartoon sweat drops flying.`
- **Motion:** `Fast handheld: desks scrape across the floor, Kazemi shouts orders, Arian pushes with all his weight, sweat and strain, chairs fall.`
- دیالوگ: کاظمی «میزها رو بیارید!» — آرین «هل بده! هل بده!»

### S14 · ۵۰–۵۵ ث · در می‌لرزد
- **Start frame:** `[kian] crouched in a classroom corner hugging his green backpack, crying, the barricaded door shaking behind him, shadows moving behind the frosted glass.`
- **Motion:** `The door shakes from heavy banging, dust falls from the frame; Kian rocks and speaks through tears; slow push-in on his face.`
- دیالوگ: کیان «می‌خوام برم خونه...» — من «حق با مامان بود...»

### S15 · ۵۵–۶۰ ث · هلیکوپتر
- **Start frame:** `Classroom window, a plain unmarked olive helicopter passing low outside, wind shaking the trees, students rushing to the window.`
- **Motion:** `Rotor wash rattles the glass; [arian] turns to the camera with a huge relieved smile, speaking excitedly.`
- دیالوگ: بلندگوی هلیکوپتر «بچه‌ها! بیاید پشت‌بوم!» — آرین «ارتش اومد! نجات پیدا کردیم!»

### S16 · ۶۰–۶۳ ث · فرار
- **Start frame:** `[kazemi] pulling desks away from a side door, glasses crooked, sweating, waving the students forward.`
- **Motion:** `He shouts and waves, students run past him into a dim corridor.`
- دیالوگ: «همه دنبال من!»

### S17 · ۶۳–۶۶ ث · راه‌پله
- **Start frame:** `POV running up a dim concrete school stairwell, the viewer's hand gripping [kian]'s hand who runs just ahead, green backpack bouncing.`
- **Motion:** `Fast shaky running POV up the stairs, Kian looks back, terrified, speaking.`
- دیالوگ: کیان «دستمو ول نکن!»

### S18 · ۶۶–۶۹ ث · در پشت‌بام
- **Start frame:** `POV at the top of the stairs, a metal rooftop door with bright daylight leaking around its edges.`
- **Motion:** `The camera shoulders the door open, it bursts outward into blinding daylight and strong wind.`
- دیالوگ: من «بدو! فقط بدو!»

### S19 · ۶۹–۷۲ ث · سرباز
- **Start frame:** `Rooftop of a school building, a plain unmarked olive helicopter hovering just above the edge, [soldier] leaning out reaching a gloved hand toward the camera.`
- **Motion:** `Rotor wind whips hair and dust; the soldier shouts and stretches his hand; the camera's own hand reaches toward his.`
- دیالوگ: «زود باش! دستتو بده!»

### S20 · ۷۲–۷۶ ث · پایان
- **Start frame:** `Close-up of [soldier] gripping the camera's wrist, pulling up. Just above his right elbow: a torn sleeve and a small cartoon bite mark.`
- **Motion:** `He pulls; the camera's gaze drops to the bite, then rises to his face — his pupils slowly fade to blank white and his skin tints mint-green. Wind noise, slow motion. Hard cut to black.`
- دیالوگ: من «ارتش... نابسامان شده...»

---

## چک‌لیست یکدستی
- [ ] برای هر شخصیت فقط **یک** عکس مرجع (`ref_<key>.png`) — هر شات همان را بگیرد.
- [ ] Identity block را هیچ‌وقت تغییر ندهید، فقط کپی.
- [ ] همهٔ شات‌ها ۹:۱۶، ۲۴ فریم، صدای ابزار خاموش.
- [ ] شات‌های یک مکان (کلاس: S06 تا S16) را پشت سر هم بسازید و از یک فریم شروع کلاس برای همه استفاده کنید.
- [ ] اگر ابزار زامبی را رد کرد: کلمهٔ *zombie* را به *sick, sleepy, pale green* تغییر دهید.
- [ ] اگر نتیجه زیادی واقعی شد: «very cartoony» را اول پرامپت هم بنویسید و پرامپت منفی را حتماً بدهید.
