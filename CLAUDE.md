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
- Older cartoon (toon) films: `blender/school_pov/`, `blender/train_pov/` — workflow skill `/film-toon`.

## Rules the user set
- No hijab on anyone. No flags, emblems, logos or anything that ties a shot to a real place.
- The story never depends on the audience; a film may end with one question to the viewer.
- The user records the voices (ElevenLabs); deliver a version without sound, and keep `talking=True`
  lip movement on the lines in `captions.py` so their voices fit.
- Voice scripts: give each line in its own copyable block, per speaker. Put the delivery (how to say it)
  inside the line as ElevenLabs v3 audio tags in square brackets, in English, e.g. `[whispers]`, `[shouting]`,
  `[scared]`, `[sighs]` — ElevenLabs performs these and does not read them aloud. Never write the delivery
  as plain text, and never put Persian words in brackets.
- Persian captions: Vazirmatn font in `blender/fonts/`, Pillow with raqm.
- Always give times to the user in Berlin time (Europe/Berlin), not UTC.
- When a film is finished (final mp4s made), tell the user with a push notification (PushNotification tool,
  status "proactive", one short Persian line with the film's name) and send the videos with SendUserFile
  (status "proactive") so they reach the phone with a sound.
