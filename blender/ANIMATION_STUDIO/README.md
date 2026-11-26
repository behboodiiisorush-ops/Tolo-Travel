# ANIMATION_STUDIO — Universal Human Animation System (UHAS)

سیستم انیمیشن انسانیِ قابل‌استفاده‌ی دوباره برای همه‌ی شخصیت‌های استودیو: ریگ Rigify، موشن‌کپچر Mixamo،
قفل پا، چهره، کتابخانه‌ی حرکت، NLA و تست‌های عددی. همه‌چیز با اسکریپت ساخته می‌شود و هر عددی که اینجا آمده
در خود بلندر روی انیمیشن واقعی **اندازه‌گیری** شده است.

```
blender/cast/setup.sh                                                         # once per machine
blender/cast/bpy.sh blender/ANIMATION_STUDIO/11_PYTHON_TOOLS/create_character.py ARIAN   # build + library + QC + tests
blender/cast/bpy.sh blender/ANIMATION_STUDIO/12_EPISODES/EP_001/build_ep001.py --render   # demo episode
blender/cast/bpy.sh blender/ANIMATION_STUDIO/08_ENVIRONMENT/build_environments.py         # sets
```
Headless renders of Workbench/EEVEE need Mesa's software OpenGL: `apt-get install -y libegl1 libgl1-mesa-dri`.

## Layout (what is in each folder)
| folder | content |
|---|---|
| 00_CORE_SYSTEM | `project_config.py` (paths, roster), `rig_config.py` (bone maps, IK/FK, proportions), `motion_config.py` (library + QC thresholds), `naming_conventions.md` |
| 01_CHARACTER_LIBRARY | `CHAR_001_ARIAN`: `Rig.blend` (work file), `Model.blend`, `Face.blend`, `Materials.blend`, `Animation_Library.blend`, `REFERENCES/`, `TESTS/` |
| 02_UNIVERSAL_RIG … 07_PHYSICS_AND_SECONDARY | how each part of the spec is implemented (README per folder) |
| 08_ENVIRONMENT | Bedroom, Living_Room, Kitchen, Street (`.blend` + preview) |
| 09_CAMERA_AND_RENDER | 9:16 cameras, lighting, engines (`render_shorts.py`) |
| 10_QUALITY_CONTROL | JSON per test + `FINAL_REVIEW/ARIAN_report.md` |
| 11_PYTHON_TOOLS | the system (see its README) |
| 12_EPISODES | `EP_001` demo (built from the library through the NLA) |

## Status — implemented / tested / incomplete (Arian, CHAR_001)

**Tested** = measured by `motion_validation.py` and checked in renders.

| part | status |
|---|---|
| Rigify rig, DEF bones separate from controls, IK+FK arms and legs, fingers, toes, poles | done, tested (stress poses rendered; IK↔FK switch jump ≤ 0.22 cm on every action) |
| Weights (body MPFB Rigify weights, clothes via MPFB mhclo interpolation, cartoon face rigid) | done, tested (0 unweighted visible vertices) |
| Puppet proportions (head ×1.38, hands ×1.2, feet ×1.12) | done |
| Mixamo -> Rigify retarget (FK baked, IK snapped from FK) | done, tested |
| Foot calibration (capture stood ~13–19° toe-down) | done, tested (flat after correction: 0.8°) |
| Root motion from the planted feet, loops closed on whole frames | done, tested |
| Foot locking (heel / ball / toe pivots, eased, reach-safe) | done, tested — 12 of 17 actions under 1.5 cm slip |
| Limb stretch / knee & elbow / reverse bends / flips / pops | done, tested — 0 stretch, 0 reverse bends, 0 flips, 0 pops on all 17 |
| Balance (centre of mass over planted soles, standing clips) | done, tested |
| Facial system (FACE_CTRL sliders, 5 expression presets, blinks, brows, jaw, eyes, lip sync) | done, tested (11/11 presets move the right parts) — lip sync is loudness/brightness based, not phoneme-accurate |
| Action library (17 actions, assets, fake users) + `Animation_Library.blend` | done |
| NLA organisation (BODY_A/B cross-fades, ROOT, additive FOOTLOCK, FACE) | done — demo in `12_EPISODES/EP_001` |
| Secondary motion (spring follow-through, head stabilisation, COMBINE layers) | implemented; not yet used in a rendered shot |
| Environments: bedroom, living room, kitchen, street | done (previews) |

**Not passing yet (honest list):**
- `UHS_WALK_Natural` 3.7 cm: the heel skims the floor for one frame before landing (threshold 1.5 cm).
- `UHS_INTERACT_OpenDoor` 18 cm, `UHS_TRANS_IdleToWalk` 13 cm, `UHS_INTERACT_Punch` 5 cm: non-looping clips that
  travel; the root curve from the feet is not yet good enough where the speed changes fast.
- `UHS_STAND_UpFromFloor` 6 cm: kneeling, the toes pivot and slide.

**Not done:** cloth and hair simulation, collision setup; STAND_TO_SIT and TURNING transitions (need captures);
the other five characters (DANIEL, LINA, FATHER, MOTHER, SHADOW): following the spec, they are reused only after
CHAR_001 passes — their designs are ready in `project_config.EXTRA_PUPPETS` and one command builds each
(`create_character.py DANIEL`).

## Bugs the tests found (and that are fixed)
1. Child Of bakes moved nested controls twice (feet 1–3 m away) → helper bones + world Copy Transforms.
2. Rigify's IK solver shrank the legs by 3 % (`ik_stretch` on MCH bones) → set to 0.
3. Source legs reached further than Rigify legs: the toe tore off the foot by 3 cm → IK is snapped from FK.
4. Retargeted feet stood 13–19° toe-down → calibration on a standing clip.
5. Loops didn't close on whole frames; Blender clamps negative frames (padding broke) → time-scaled loops, positive padding.
6. NLA strips of cyclic actions were one frame short per cycle (8 cm jump at every loop) → frame range 1..n+1.
7. Test bugs too: quaternion angles of 359° counted as pops; heel->ball roll counted as slip; driven values read
   from the original instead of the evaluated data; masked helper vertices counted as unweighted.
