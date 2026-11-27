# PROJECT_STATE — THE ZOMBIE CENTER (مرکز زامبی‌ها) · subtitle: PATIENT ZERO
**Last updated:** 2026-11-26 23:12 (Berlin) · Production: AGETOBUDI · Branch: `claude/great-newton-w2xf6z`
Read this file first at the start of every new conversation. Never continue from guesswork.

---

## 0. PERMANENT PROJECT LAW — quality before speed (set by the user, 2026-11-26)
**The two-day release rhythm is a production target, not permission to deliver unfinished work.**
If an episode needs more time to reach this standard, say so honestly and deliver it late. Never trade quality for the date.
The goal is a professional cinematic horror film, not an ordinary animation.

Every episode is checked before delivery — whole motions frame by frame AND at real speed, never only first/last frame:
1. **Walking / running** — human gait; no foot sliding; feet never sink into the ground; knees bend naturally;
   pelvis, shoulders and spine move together; weight shifts between the feet; running has balance and acceleration;
   stops and turns are never abrupt or artificial.
2. **Arms / hands** — arm swing matches the gait; natural elbows and wrists; no broken fingers; hands never pass
   through the body or objects; exact contact when grabbing; logical hands in fear, defence and fights.
3. **Head / face** — eyes look at the right target; natural blinking; the head is not frozen while walking;
   expressions match the emotion; lip movement matches the dialogue; fear, shock, anger and pain are readable.
4. **Physics / contact** — no impossible contact between characters; real weight when sitting, standing up and falling;
   clothes and hair react to the body; correct contact with walls, doors, tables and props; nothing sinks into objects.
5. **Animation tests in Blender** — Foot Contact Test · Walk Cycle Test · Run Cycle Test · IK/FK Validation ·
   Ground Contact · Collision Check · Root Motion · Graph Editor curve inspection · Facial Animation Review ·
   Motion Continuity Check (done with scripts that measure, plus frame-by-frame contact sheets and a real-speed preview).
6. **Cinematic QC** — same characters, clothes, faces, proportions in every shot; no unneeded camera shake;
   lighting fits the scene; sound in sync; no black, broken or incomplete frames; no contradiction with earlier episodes.
7. **Delivery rule** — every episode ships with a QC report: 1 feet · 2 hands · 3 body/balance · 4 face/eyes ·
   5 environment contact · 6 camera · 7 light & sound · 8 story continuity · 9 render errors · 10 final verdict.
   **If even one important problem remains, fix it first, then deliver.**

## 1. Project identity
| | |
|---|---|
| Title | THE ZOMBIE CENTER — مرکز زامبی‌ها (subtitle PATIENT ZERO / بیمار صفر) |
| Genre | cinematic horror · zombie thriller · psychological horror · survival |
| Format (current) | **series of 12 episodes × ~5 min**, long-form 16:9, **1280×720**, 24 fps, EEVEE; one episode every 2 days, user publishes on YouTube at **19:00 Berlin** (`docs/SERIES_PLAN.md`) |
| Story runtime | 60:00 · 8 chapters × 7:30 (screenplay v1.0) |
| Format | 1920×1080, 16:9, Blender Cycles, photorealistic |
| Dialogue | Persian; the user connected ElevenLabs — Claude generates the voices (one fixed designed voice per character, v3 tags); Persian captions (Vazirmatn) |
| Project rules | no hijab · no flags/emblems/logos/real places · ends with one question to the viewer · silent version + lip movement on every line · times in Berlin time |

## 2. Story canon (locked — changes only with the user's approval)
- Secret research centre; medical on the surface, illegal human experiments underground. Virus destroys the nervous system and makes people aggressive.
- **Arin = SUBJECT 001.** 19, black centre-parted hair, dark eyes, small eyebrow scar, dark practical jacket and trousers. Not the creator of the virus — the first carrier who spread it outside the centre (Patient Zero).
- **Nika = SUBJECT 002.** Arin's sister, held inside; infection progresses; recognises Arin for part of the story.
- **Dr. Elena** — scientist in charge; knows Arin's past; hides the truth; morally complicated.
- **Sara** — survivor, suspicious of the centre, joins Arin's mission.
- **Mark** — security; knows more than he says; history with the centre.
- Supporting (defined by Claude, awaiting approval): **Sam** (survivor, causes the power failure), **Kaveh** (lucid infected researcher).
- Ending must be tragic, shocking, unpredictable, emotionally strong.

## 3. Open decisions (need the user)
| # | decision | options | status |
|---|---|---|---|
| D1 | **Chapter structure** (series uses the screenplay v1.0 scenes; chapter names matter only for titles) — two different structures were given | A) first brief: 1 THE LAST MESSAGE · 2 THE SAFE SHELTER · 3 THE RED DOOR · 4 THE LABORATORY TRUTH · 5 THE FALL OF THE CENTER · 6 MY SISTER · 7 THE LAST EXIT · 8 PATIENT ZERO (screenplay v0.1 is written to this) · B) master prompt: 1 THE FACILITY · 2 SUBJECT 001 · 3 THE FIRST OUTBREAK · 4 LOCKDOWN · 5 THE UNDERGROUND · 6 NO WAY OUT · 7 THE LAST EXPERIMENT · 8 THE ZOMBIE CENTER | **OPEN** |
| D2 | Render engine | user has only a phone → EEVEE on this server, 720p (measured ~20–37 s/frame) | **DECIDED** |
| D3 | Folder structure — two trees were given | keep everything under `blender/zombie_center/` using the master-prompt tree (00_PROJECT … 17_BACKUPS) | proposed |
| D4 | Screenplay story, ending and v1.0 additions | — | **APPROVED** |
| D5 | New cast separate from the permanent Tolo cast (keys `zc_arin`, …) | — | proposed |

## 4. Production phases (master-prompt order) and status
| # | phase | status | deliverables |
|---|---|---|---|
| 01 | Project setup | **DONE (awaiting approval)** | master .blend, collections, settings, test render (§5) |
| 02 | Character design | not started | 02_CHARACTER_BIBLE.md, sheets |
| 03 | Character modeling | not started | CHAR_*_MASTER.blend |
| 04 | Character rigging | feasibility tested only | Rigify rig per character |
| 05 | Facial rigging | not started | face rig + expression set |
| 06 | Human animation tests | not started | 07_ANIMATION_LIBRARY.md, tests |
| 07 | Zombie animation system | not started | Z1–Z7, ZOMBIE_ANIMATION_LIBRARY |
| 08 | Environment modeling | not started | 03_LOCATION_BIBLE.md, ENV_*.blend |
| 09 | Props and materials | not started | 04_PROP_LIST.md, PROP_*.blend |
| 10 | Lighting | not started | per-location rigs |
| 11 | Camera and cinematography | not started (brief received: CAM_POV / WIDE / MEDIUM / CLOSE / DETAIL / OTS / TRACK / STATIC / ORBIT) | 08_CAMERA_PLAN.md, 06_SHOT_LIST.csv |
| 12 | Scene production | not started | CHxx_SCxxx.blend, one scene at a time |
| 13 | VFX | not started | fog, blood, sparks, screens |
| 14 | Sound design | not started (brief received) | 09_SOUND_PLAN.md, AUDIO_ASSET_CHECKLIST.md |
| 15 | Editing | not started (brief received) | FINAL_EDIT_PLAN.md |
| 16 | Color grading | not started | — |
| 17 | Rendering | not started | 11_RENDER_PLAN.md, FINAL_RENDER_SETTINGS.md |
| 18 | Quality control | not started (brief received) | 12_QC_REPORT.md |
| 19 | Final export | not started | FINAL.mp4, SUBTITLES.srt, CREDITS.txt |
| — | Story (runs before 02) | **v1.0 DONE (awaiting approval)**: 64 scenes, 20-field format, 60:00 validated, no gap | 00_MASTER_BIBLE.md, 01_FULL_SCREENPLAY.md, 05_SCENE_BREAKDOWN.md, 10_CONTINUITY_LEDGER.md |

## 5. Files that exist (verified on disk)
| file | what |
|---|---|
| `docs/00_MASTER_BIBLE.md` | story bible v0.1 (canon, hidden backstory, reveal order, zombie types, night timeline, feasibility) |
| `docs/01_FULL_SCREENPLAY.md` | screenplay v1.0: 64 scenes, 20 fields each, 60:00 validated (structure A); v0.1 kept in `docs/versions/` |
| `docs/05_SCENE_BREAKDOWN.md` | one row per scene (64) |
| `docs/10_CONTINUITY_LEDGER.md` | cross-chapter facts + end state of all 64 scenes |
| `docs/PROJECT_SETTINGS.json` | project settings |
| `init_master.py` | script that builds the master project (re-runnable, never overwrites a version) |
| `blend/THE_ZOMBIE_CENTER_MASTER.blend` | master: 11 collections 00_MASTER…10_RENDER, 1920×1080, 24 fps, Cycles, test scene |
| `blend/versions/THE_ZOMBIE_CENTER_MASTER_v001.blend` | preserved version |
| `test/phase4_test_frame.png` | Cycles test frame (64 samples, denoised, 43 s on CPU) — inspected: correct |
Incomplete / in progress: none.

## 6. Technical reality (checked, not guessed)
**Claude ↔ Blender connection:** there is **no Blender MCP / live Blender session** connected. What does work:
Blender 5.3 as a Python module (`bpy`) inside this cloud container, run headless through `blender/cast/bpy.sh script.py`.
So Claude can: build and save .blend files, rig, animate, render stills and sequences, inspect renders as images,
mix audio (ffmpeg), make captions (Pillow + raqm, Vazirmatn), check sync (faster-whisper), time-stretch (rubberband).
Claude cannot: watch a live viewport, scrub the timeline interactively, or use a GPU.

| tool | state |
|---|---|
| bpy 5.3 + numpy (venv) | working |
| MPFB 2.0.18 + MakeHuman assets (CC0/CC-BY) | working (human 1.70 m built in test) |
| Rigify (via MPFB `rigify.human_toes`) | working: 1,090 bones, IK/FK, root, torso, foot, eye and jaw controls, generated in ~1 s |
| Mixamo FBX clips `blender/mocap/` | 44 clips; retargeting onto Rigify still to be built |
| ffmpeg 6.1, Pillow+raqm, faster-whisper, rubberband, libEGL | working |
| Hardware | 4 CPU cores, 15 GB RAM, **no GPU**; container is reclaimed when idle (work must be committed) |

**Render cost:** test frame 43 s (empty scene). Real film frames (people, hair, glass, fog) ≈ 3–10 min each on this CPU →
86,400 frames = months of rendering. This is decision D2.

**What the user must do:** approve phases; record voices (ElevenLabs); download extra Mixamo clips (crying, falling,
dying, grabbing, crawling, arguing, sitting down/standing up…); provide GPU rendering if Cycles is kept for the whole film;
optional: open the .blend files in desktop Blender to review.

## 7. Approved changes
- 2026-11-26 (user) **Render method for every episode:** split the render over new chats made with create_session (model **sonnet**), **~140 frames each**; each worker renders its range, encodes its piece as **mp4** and pushes it to its own branch (`claude/zc-ep<NN>-part-<k>`); this chat renders from the **start** of the episode and, after its own piece, keeps going into the following pieces so any failed worker's range is already covered; at the end all mp4 pieces are checked (frame count, no black/broken frames) and joined in order. (720p episode ≈ 7,200 frames ≈ 50 workers.)
- From CLAUDE.md (set in other chats, apply here too): voices AND sound effects from ElevenLabs (one designed voice per character, reused); credit «ساخته شده توسط بلندر» + «agetobudi» in every episode (opening/closing card + small corner credit); long renders split over ~6 worker chats (`chain.sh A B` pattern, frames pushed to `claude/<film>-frames-a…f`); push notification + SendUserFile when an episode is finished. Render splitting makes 720p episodes ≈ 6–8 h wall-clock instead of ~40 h.
- 2026-11-26 (user): screenplay v1.0 additions approved (drawing in Arin's pocket, second drawing hint for Mark, music motifs, fevered man at the gate, route «۴» bus clue, merge fixes).
- 2026-11-26 (user): phone only; one episode every 2 days at 720p; YouTube release 19:00 Berlin; ElevenLabs connected for Claude to use; PERMANENT QUALITY LAW (§0).
- 2026-11-26 (user): format changes to a **series of 12 × ~5 min long-form episodes**, released one by one (`docs/SERIES_PLAN.md`). Release time, pace and visual style still open.

## 8. Next task
PHASE 02 — build and test the six main characters (MPFB + Rigify), reference sheets, then 02_CHARACTER_BIBLE.md from the built models. Then rigs + Mixamo retarget + motion QC tests (walk/run/foot contact) before any episode scene.
