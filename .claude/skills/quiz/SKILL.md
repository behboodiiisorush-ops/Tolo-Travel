---
name: quiz
description: Make a new 60-second YouTube Shorts driving quiz («کوییز رانندگی») — 5 new questions that never repeat earlier episodes, motion graphics (vertical 1080x1920), ElevenLabs narrator + sound effects + music. Use whenever the user says "Quiz", "کوییز", "کوییز رانندگی", "quiz بعدی" or asks for a driving/traffic quiz video.
---

# Driving quiz (Shorts, 60 s)

When the user just says **Quiz** they mean: make the next episode of the driving quiz, finished, with sound.
Reply in Persian. Work through to the delivered mp4 without stopping to ask.

Everything lives in `quiz/driving/`:
- `engine/template.html` — the motion-graphics page (intro → 5 questions → outro), drawn per frame by `renderAt(t)`.
- `engine/build.py` — cleans the voice, works out the timeline that fills exactly 60 s, mixes voice + SFX + music.
- `engine/render.js` — headless Chromium → ffmpeg, then muxes `audio/mix.wav`.
- `USED_QUESTIONS.md` — **every question ever used. Read it first; never repeat a topic.**
- `IDEAS.md` — pool of fresh topics.
- `episodes/epNN/` — one folder per episode (`episode.json`, `timeline.json`, `audio/`, `out/`).

## 1. Write the episode
1. Next number = highest `episodes/epNN` + 1. Copy `episodes/ep01/episode.json` as the shape.
2. Pick 5 questions not in `USED_QUESTIONS.md` (same sign/rule/situation counts as a repeat, whatever the wording).
   Easy → hard; the 5th is announced as «سوال آخر، سخت‌ترینش!». General rules valid in most countries.
3. 4 short options each (≤ 4 words); vary the correct position (not the same letter twice in a row).
4. Every question needs a `visual` kind drawn in `template.html` → `visual(kind, lt)`. Existing kinds:
   `sign_octagon`, `light_flashing_yellow`, `sign_no_entry`, `ambulance`, `rain_distance`.
   Add new kinds as inline SVG (520×520 viewBox), animated by `lt` (seconds since the question began).
5. Narration lines (Persian, short): `intro.say`, per question `say_q` («سوال اول/دوم/سوم/چهارم» + question)
   and `say_a` (answer + one reason), `outro.say` (ends with one question to the viewer: how many did you get, write it in the comments).
   Delivery as English ElevenLabs v3 tags in brackets: `[excited]`, `[curious]`, `[confident]`, `[serious]`, `[dramatically]`.
   Total voice ≈ 50 s before speed-up; keep `say_q` ≤ ~4.5 s.

## 2. Sound from ElevenLabs (MCP)
- One flow per episode: `creative_create_flow` ("Driving Quiz epNN"), store its id in `episode.json` → `elevenlabs_flow`.
- Narrator: `creative_generate_speech`, model `eleven_v4`, voice **Arash – Clear, Confident Narrator**
  `Mn0jJ3FC9Ijz7lQe8ELI` (same voice every episode). 12 lines: intro, q1..q5, a1..a5, outro — launch them in parallel.
- SFX (`creative_generate_in_flow`, node_type `sfx`, model `eleven_text_to_sound_v3`): whoosh, tick (countdown clock tick),
  ding (correct answer), pop (UI pop), hit (intro engine rev + boom). Music: node_type `music`, `eleven_music_v2_5`,
  instrumental 60 s game-show bed. ep01's SFX/music in `episodes/ep01/audio/raw/` may be reused (copy them) to save credits.
- Poll `creative_get_flow_run_status`, then `curl` each `content_url` into `episodes/epNN/audio/raw/`
  as `intro.mp3, q1.mp3 … a5.mp3, outro.mp3` and `whoosh_a.mp3, tick_a.mp3, ding_a.mp3, pop_a.mp3, hit_a.mp3, music_a.mp3`
  (`_b` for the second take; choose with `"takes": {"music": "b"}` in episode.json).

## 3. Build and check
```bash
cd quiz/driving
python3 engine/build.py episodes/epNN --tempo 1.17     # prints the countdown length; must be ≥ 1.8 s
node engine/render.js episodes/epNN --still 0.7,2.2,<q1 reveal+0.3>,...   # stills → episodes/epNN/stills/
```
If the countdown is too short raise `--tempo` (max ~1.22) or shorten lines. LOOK at the stills
(hstack them) before the full render: text wraps, the new visuals, nothing off-screen.

## 4. Render and deliver
```bash
node engine/render.js episodes/epNN --workers 4     # ~5–10 min → out/epNN_quiz.mp4 (+ out/epNN_silent.mp4)
```
- Check the mp4 (duration 60.0 s, a few frames, loudness). Send it with SendUserFile.
- Append the 5 questions to `USED_QUESTIONS.md`, remove them from `IDEAS.md`.
- Commit (`episode.json`, raw audio, mix, timeline, the mp4) and push to the working branch.
- Tell the user: the 5 questions, the voice used, and a suggested title + description + hashtags for Shorts.

## Rules (from CLAUDE.md)
No hijab, flags, emblems, logos, place names or real-country signs with text. The video may end with one question to the viewer.
Persian text in Vazirmatn (`blender/fonts/Vazirmatn-FD-ExtraBold.ttf`). Times to the user in Berlin time.
