# Tolo Travel — notes for Claude

## Films (Blender, Python `bpy`)
- **Realistic films use the permanent cast in `blender/cast/`** — read `blender/cast/CAST.md` first.
  Reuse those characters (من، آرین، مهسا، کیان، مامان، آقای کاظمی، آقای رضایی، گوینده اخبار، سرباز) for every
  new film idea instead of designing new faces. New recurring people get added to `cast.py` + a sheet.
- Setup on a fresh machine: `blender/cast/setup.sh`, then run scripts with `blender/cast/bpy.sh script.py`.
- Example of a full film built on the cast: `blender/last_bell_real/` (render in parts, `run_all.sh`).
- The whole workflow is the project skill `/film-3d` (`.claude/skills/film-3d/SKILL.md`).
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
