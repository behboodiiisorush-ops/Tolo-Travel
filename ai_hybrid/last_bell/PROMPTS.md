# «زنگ آخر» — نسخهٔ ترکیبی (هوش مصنوعی + تدوین ما)

همان داستان و همان زمان‌بندی `blender/last_bell_real/voice_script.md`، ولی هر شات با ابزار
«تصویر ← ویدیو» (Veo / Kling / Runway / Sora) ساخته می‌شود تا حرکت، پوست، عرق و نور طبیعی شود.
شخصیت‌ها همان بازیگران ثابت `blender/cast/` هستند.

## روند کار (۴ مرحله)

1. **تصویر مرجع هر شخصیت** (یک بار برای همیشه) — بخش ۳.
   عکس `blender/cast/sheets/<key>_face.png` و `<key>_full.png` را به ابزار تصویر بدهید
   (حالت image-to-image / character reference) + پرامپت همان شخصیت. از بین نتیجه‌ها **یکی** را انتخاب کنید
   و اسمش را بگذارید `ref_<key>.png`. از این به بعد همیشه همین یک عکس مرجع است.
2. **فریم شروع هر شات** — پرامپت «Start frame» هر شات + عکس‌های مرجع شخصیت‌های داخل آن شات.
3. **ویدیو** — فریم شروع را بدهید به حالت image-to-video + پرامپت «Motion». نسبت ۹:۱۶، ۲۴ فریم.
   - **صدای ساخته‌شده را خاموش کنید** (یا بعداً دور می‌ریزیم) — صداها را خودتان با ElevenLabs می‌سازید.
   - در شات‌هایی که کسی حرف می‌زند، عبارت *speaking* در پرامپت هست تا لب‌ها تکان بخورد.
   - از هر شات ۲ تا ۴ نسخه بگیرید و بهترین را نگه دارید.
4. **تحویل به من** — فایل‌ها را با اسم شات (`S01.mp4`, `S02.mp4`, …) آپلود کنید.
   من: برش و ترتیب، یکسان کردن رنگ همهٔ شات‌ها، زیرنویس فارسی (وزیرمتن)، جای صداها، افکت صوتی، خروجی نهایی.

## قوانین ثابت (در همهٔ شات‌ها)
- هیچ‌کس حجاب ندارد.
- هیچ پرچم، آرم، نشان، نوشته روی دیوار، اسم مکان یا لوگوی تلویزیون/ارتش. هلیکوپتر و کامیون بی‌علامت.
- زامبی‌ها «ترسناک ولی نه خون‌آلود زیاد» — بعضی ابزارها خون زیاد را رد می‌کنند؛ پرامپت‌ها عمداً ملایم نوشته شده.

---

## ۱. بلوک سبک — آخر *همهٔ* پرامپت‌ها اضافه شود

```
Photorealistic live-action film still, shot on 35mm, natural skin texture with pores and fine sweat,
soft realistic lighting, shallow depth of field, subtle film grain, muted warm colour grade,
vertical 9:16 frame. Middle-Eastern (Iranian) people with warm olive skin.
No text, no logos, no flags, no emblems, no signs, no headscarves.
```

## ۲. پرامپت منفی (اگر ابزار جایش را دارد)

```
cartoon, 3D render, CGI, plastic skin, doll face, extra fingers, deformed hands, text, watermark,
logo, flag, emblem, insignia, subtitles, headscarf, hijab, oversaturated, blurry face
```

---

## ۳. شخصیت‌ها — متن ثابت هر نفر (عیناً کپی شود، هر بار همین)

| key | نام | Identity block (انگلیسی، ثابت) |
|---|---|---|
| `me` | من | `a 15-year-old Iranian boy, slim, dark brown side-swept hair falling over his forehead, navy blue hoodie, blue jeans` |
| `arian` | آرین | `a tall lanky 15-year-old Iranian boy, short black hair, playful grin, slate-blue polo shirt, dark jeans` |
| `mahsa` | مهسا | `a 15-year-old Iranian girl, black hair tied back in a low ponytail, red rectangular glasses, navy t-shirt, grey trousers, red flat shoes, sharp confident eyes` |
| `kian` | کیان | `a small 13-year-old Iranian boy, short messy black hair, light-blue hoodie, jeans, green backpack, nervous eyes` |
| `mom` | مامان | `a 42-year-old Iranian woman, brown hair in a neat bun, uncovered head, cream knitted sweater, navy trousers, warm worried face` |
| `kazemi` | آقای کاظمی | `a 50-year-old Iranian male teacher, greying brown hair, black rectangular glasses, brown jacket and brown trousers, stern face` |
| `rezaei` | آقای رضایی | `a 58-year-old Iranian janitor, grey slicked-back hair, wrinkled kind face, plain blue work overalls` |
| `rezaei_z` | رضایی زامبی | `the same 58-year-old janitor in blue overalls, now infected: pale grey-green skin, dark veins, cloudy white eyes, dirty torn overalls, dark stains around the mouth` |
| `anchor` | گوینده اخبار | `a 45-year-old Iranian male news anchor, short dark hair, dark suit, white shirt, plain tie` |
| `soldier` | سرباز | `a 28-year-old Iranian soldier, plain olive-green uniform with no patches or insignia, olive steel helmet with net, black gloves` |

### پرامپت تصویر مرجع (مرحلهٔ ۱) — برای هر شخصیت

ورودی: `<key>_face.png` + `<key>_full.png`. پرامپت:

```
Turn this 3D character into a real person. Keep exactly the same face shape, hairstyle, hair colour,
glasses and clothes. [IDENTITY BLOCK]. Studio portrait, plain light-grey background,
front view, head and shoulders, neutral expression, soft daylight. [STYLE BLOCK]
```

بعد با همان عکس مرجع یک **عکس تمام‌قد** هم بگیرید (`full body, standing, front view`) — برای شات‌های دور.

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
- **Motion:** `The waveform plays; the thumb hesitates over the screen; the camera glances up at the teacher and back down. Close, intimate, slightly shaky.`
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
- **Start frame:** `Extreme close-up of [rezaei_z] face pressed against a window from outside, cloudy white eyes, breath fogging the glass.`
- **Motion:** `His eyes snap to the camera; he slams a palm on the glass. Behind the camera [kian] gasps (reflection in the glass).`
- دیالوگ: کیان «چشماش!»

### S13 · ۴۵–۵۰ ث · سنگر
- **Start frame:** `[kazemi] and [arian] pushing heavy wooden school desks against a classroom door, other students helping, chaos, sweat on their faces.`
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
- **Start frame:** `Close-up of [soldier] gripping the camera's wrist, pulling up. Just above his right elbow: a torn sleeve and a fresh bite wound.`
- **Motion:** `He pulls; the camera's gaze drops to the bite, then rises to his face — his eyes slowly turn cloudy white. Wind noise, slow motion. Hard cut to black.`
- دیالوگ: من «ارتش... نابسامان شده...»

---

## چک‌لیست یکدستی
- [ ] برای هر شخصیت فقط **یک** عکس مرجع (`ref_<key>.png`) — هر شات همان را بگیرد.
- [ ] Identity block را هیچ‌وقت تغییر ندهید، فقط کپی.
- [ ] همهٔ شات‌ها ۹:۱۶، ۲۴ فریم، صدای ابزار خاموش.
- [ ] شات‌های یک مکان (کلاس: S06 تا S16) را پشت سر هم بسازید و از یک فریم شروع کلاس برای همه استفاده کنید.
- [ ] اگر ابزار خون یا زامبی را رد کرد: کلمهٔ *infected* را به *sick, pale, feverish* تغییر دهید.
