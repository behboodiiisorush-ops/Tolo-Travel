---
name: film-toon
description: Make a cartoon (toon-shaded) POV short film in Blender, the style of the first episodes «واگن آخر» (blender/train_pov) and the cartoon «زنگ آخر» (blender/school_pov) — puppet characters, Freestyle outlines, fisheye POV, Persian captions, synthesised sound effects, the user's ElevenLabs voices. Use when the user runs /film-toon or asks for a film "به روش قسمت اول / کارتونی / مثل واگن آخر".
---

# Cartoon POV film (the first-episode style)

Reply in the user's language (Persian if they wrote Persian). Work without stopping until the film is delivered.
For realistic films with the permanent human cast use `/film-3d` instead.

## Rules from the user (always)
- No hijab on anyone. No flags, emblems, logos or place names in any shot.
- The story never depends on the audience; the film may end with one question card.
- The user records the voices (ElevenLabs). Deliver a silent version, give the voice script as copyable
  code blocks per speaker, then cut and place their recording when it arrives.

## Reference films (copy their structure)
- `blender/train_pov/` — «واگن آخر» (70 s): `common.py` (toon materials, primitives, `Person` puppets with
  pivot empties, `POVArms`, render settings), `part_station.py` + `part_wagon.py` (one script per set,
  global frame numbers), `captions.py`, `make_textures.py` (phone/TV screens with Persian text),
  `sfx.py` (numpy-synthesised effects), `post.py` (fisheye, upscale, captions, card),
  `cut_voices.py` + `voice_fx.py` + `mix_voices.py` (the user's voices), `run_all.sh`.
- `blender/school_pov/` — the cartoon «زنگ آخر» (75 s + 5 s card), one `scene.py` with all sets side by side.

## Steps
1. Python with bpy: `blender/cast/vendor/venv/bin/python` (run `blender/cast/setup.sh` on a fresh machine,
   or `pip install bpy==5.3.0` into a venv). Scripts take `--save`, `--still a,b`, `--render [--range a b]`.
2. Write `captions.py` first `(start, end, speaker, text)`; it drives captions, mouths and voices.
3. Build sets + puppets with `common.py` helpers; camera rotation is (90 + pitch, roll, yaw), yaw 0 = +Y.
4. Render test stills, combine with ffmpeg `hstack`, LOOK at them and fix before the long render.
5. Long render: start detached (`setsid nohup ./run_all.sh > log 2>&1 &`) AND keep a tracked background
   Bash task waiting on it (`run_in_background`, timeout 7200000, restart when it times out) — an idle
   cloud session is shut down within minutes. Frames already on disk are skipped on restart.
6. `sfx.py` -> `out/sfx.wav`; `post.py` -> silent film + film with effects.
7. Voices: transcribe the user's export with faster-whisper (word timestamps), cut lines (`cut_voices.py`),
   colour them per character (`voice_fx.py`: pitch, phone, TV, loudspeaker), place without overlaps and
   duck effects (`mix_voices.py`). Tell the user which lines were missing.
8. Send the mp4s with SendUserFile; commit and push (not frames).
