---
name: film-3d
description: Make a realistic 3D short film (vertical 1080x1920, Persian captions) in Blender with the permanent Tolo Travel cast (من، آرین، مهسا، کیان، مامان، آقای کاظمی، آقای رضایی، گوینده اخبار، سرباز، zombies). Use when the user runs /film-3d or asks for a 3D / realistic / Blender video, a new episode, or a film from a story idea (فیلم سه‌بعدی، ویدیو واقعی، قسمت بعد).
---

# Realistic 3D film with the permanent cast

Reply in the user's language (Persian if they wrote Persian). Work without stopping until the film is
delivered; the user does not want to be asked to continue.

## 0. Rules from the user (always)
- No hijab on anyone. No flags, emblems, logos, insignia or place names in any shot.
- The story never depends on the audience; the film may end with one question card to the viewer.
- Reuse the cast — read `blender/cast/CAST.md` (and look at `blender/cast/sheets/overview.png`).
  Never redesign a recurring face. New recurring people: add to `CAST` in `blender/cast/cast.py`
  and render a sheet (`blender/cast/bpy.sh blender/cast/sheet.py <key>`), then rebuild `overview.png`.
- The user records voices in ElevenLabs. Deliver a version without sound and give them the voice script.

## 1. Setup (once per fresh machine, ~5 min)
```bash
blender/cast/setup.sh          # bpy venv + MPFB + MakeHuman assets into blender/cast/vendor (git-ignored)
```
Needs network access to extensions.blender.org, files.makehumancommunity.org and
static.makehumancommunity.org (already allowed in the Tolo-Travel environment).
Run every Blender script through `blender/cast/bpy.sh script.py ...`.

## 2. Write the film
Copy the structure of `blender/last_bell_real/` (the reference film):
- `captions.py`-style list `(start, end, speaker, text)` — the single source for captions, lip sync and voices.
- `scene.py --part <name>`: each part builds only its set + the characters it needs; sets use the
  realistic materials in `blender/cast/props.py`; characters via `cast.spawn(key)` /
  `cast.spawn_extra("student"|"passerby", i)` / `zombie=1.0`.
- Animate per frame with `ch.animate(f, t, pos, facing, walk|run|sit|crouch|shamble, arms=..., look=..., worry=..., talking=...)`
  and call `ch.flush()` after the loop. `talking=True` during that character's caption lines.
- POV camera = من (yaw 0 = +Y, 90 = -X; same convention as `facing`).
- Render: Cycles, 540x960, 12 samples + denoise, AgX; post upscales to 1080x1920.

## 3. Check before the long render
Render 3–6 stills per part (`--still f1,f2,...`), combine them with ffmpeg `hstack`, LOOK at them,
fix framing / poses / materials. Typical problems: camera inside a wall or window bar, a character
blocking the action, colours in the wrong space (cast colours are sRGB), mirrored text planes.

## 4. Long render — keep the machine alive
A cloud container is shut down a few minutes after the session goes idle, even with a detached process.
Start the chain detached (`setsid nohup ./chain.sh > log 2>&1 &`) **and** keep a tracked background
Bash task waiting on it (`run_in_background: true`, `timeout: 7200000`, loop `while pgrep -f chain.sh; do sleep 60; done`).
When it times out after 2 h, start it again. Never rely on `send_later` alone. Frames are skipped if
they exist, so a restarted chain resumes. Push each finished part (mp4) so nothing is lost.
Speed: ~12–20 s per frame on 4 CPUs (an 80 s film ≈ 7–9 h).

## 5. Post, voices, delivery
- `post.py`: upscale, phone-screen overlays, Persian captions (Vazirmatn, Pillow + raqm), question card;
  outputs with captions, clean, with synthesised effects, and with the user's voices.
- Voice script: generate a per-speaker list from the captions (see `voice_script.md`) and give it in
  copyable code blocks.
- When the user sends ElevenLabs audio: transcribe with faster-whisper (word timestamps), cut each line,
  give each character a pitch (rubberband, formants preserved), phone/TV/loudspeaker colour where needed,
  place lines on their caption times without overlaps (`voice.py`), duck the effects under the dialogue.
  Tell the user which lines were missing from their recording.
- Send the mp4s with SendUserFile and commit + push everything except frames/vendor.
