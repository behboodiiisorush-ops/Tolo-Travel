# Tolo Travel — notes for Claude

## Films (Blender, Python `bpy`)
- **Realistic films use the permanent cast in `blender/cast/`** — read `blender/cast/CAST.md` first.
  Reuse those characters (من، آرین، مهسا، کیان، مامان، آقای کاظمی، آقای رضایی، گوینده اخبار، سرباز) for every
  new film idea instead of designing new faces. New recurring people get added to `cast.py` + a sheet.
- Setup on a fresh machine: `blender/cast/setup.sh`, then run scripts with `blender/cast/bpy.sh script.py`.
- Example of a full film built on the cast: `blender/last_bell_real/` (render in parts, `run_all.sh`).
- The whole workflow is the project skill `/film-3d` (`.claude/skills/film-3d/SKILL.md`).
- **Comic look + Mixamo motion (newest style, the user's favourite):** `blender/wall/` («دیوار») is the full example.
  Cast with `cast.STYLE = cast.CARTOON`, cel shading + ink outlines from `blender/studio/toon_look.py`,
  body motion from the Mixamo FBX clips in `blender/mocap/` via `blender/cast/mocap.py`
  (read `blender/mocap/CLIPS.md` — clips are described by what they really show, not their file names).
  EEVEE render with auto-restart (`chain.sh` + `render.py`), then `sound.py` and `post.py`.
  Use this style for new episodes and series (e.g. «زنگ آخر») unless the user asks otherwise.
- **Mixamo library (the user keeps adding clips):** every new film uses the clips in `blender/mocap/` for body motion
  — read `CLIPS.md` first and pick the clip that really shows the action (sitting_talking, driving, pointing, crying,
  picking_up, falling_down, crawling, laying_idle, …). Pull the newest clips from `claude/great-newton-w2xf6z`
  (`git checkout FETCH_HEAD -- blender/mocap`). Mixamo has no hug: make hugs by hand (two characters close, arms
  posed with IK around the other's back, blended in from `breathing_idle`).
- Older cartoon (toon) films: `blender/school_pov/`, `blender/train_pov/` — workflow skill `/film-toon`.

## Rules the user set
- No hijab on anyone. No flags, emblems, logos or anything that ties a shot to a real place.
- The story never depends on the audience; a film may end with one question to the viewer.
- **Voices and sound effects always come from ElevenLabs** (the connected ElevenLabs MCP tools, `mcp__ElevenLabs__*`):
  Claude generates every spoken line (one fixed voice per character — designed once with `creative_design_voice` +
  `creative_save_designed_voice` and reused across films, never a voice_id from memory) and every sound effect
  (no synthesised numpy effects any more). Keep `talking=True` lip movement on the lines in `captions.py` and fit
  captions + lips to the generated lengths. Also keep a version without sound. If the ElevenLabs tools are not
  available in a chat, say so to the user instead of falling back silently.
- **Branding on every video** (all versions, every frame): the film's name in the top-right corner and the channel
  logo (`blender/brand/agetobudi_logo_round.png`, the user's «داستان‌های POV — Agetobudi» logo) in the top-left,
  plus the credit «ساخته شده توسط بلندر» (channel «agetobudi»). Use `overlay(img, title)` from `blender/brand/brand.py`
  in post (works for vertical and 16:9); the closing card also shows the credit.
- Voice scripts: give each line in its own copyable block, per speaker. Put the delivery (how to say it)
  inside the line as ElevenLabs v3 audio tags in square brackets, in English, e.g. `[whispers]`, `[shouting]`,
  `[scared]`, `[sighs]` — ElevenLabs performs these and does not read them aloud. Never write the delivery
  as plain text, and never put Persian words in brackets.
- Persian captions: Vazirmatn font in `blender/fonts/`, Pillow with raqm.
- Always give times to the user in Berlin time (Europe/Berlin), not UTC.
- When a film is finished (final mp4s made), tell the user with a push notification (PushNotification tool,
  status "proactive", one short Persian line with the film's name) and send the videos with SendUserFile
  (status "proactive") so they reach the phone with a sound.

## THE ZOMBIE CENTER (series, `blender/zombie_center/`)
- **Read `blender/zombie_center/PROJECT_STATE.md` first** in every new conversation; never continue from guesswork.
- Its §0 is a permanent law from the user: quality and natural, realistic motion before speed. Every episode ships
  with a QC report; any important problem is fixed before delivery, even if the episode is late.
- 12 episodes × ~5 min, 16:9 720p, every 2 days, the user publishes at 19:00 Berlin. For this series the user
  connected ElevenLabs and asked Claude to generate the voices (one fixed designed voice per character) — now the rule for every film.
- Long renders are always split across several chats (the user's wish): render one frame range here and start
  ~6 worker chats with create_session, each rendering its range (`chain.sh A B`, see `blender/bird/chain.sh`)
  with a keep-alive waiter and pushing only its frames to its own branch `claude/<film>-frames-a…f`;
  collect the branches, post, deliver, archive the workers.
