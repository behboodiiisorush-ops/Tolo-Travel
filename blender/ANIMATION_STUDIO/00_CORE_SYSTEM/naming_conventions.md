# Naming conventions (UHAS)

## Files and folders
| thing | pattern | example |
|---|---|---|
| character folder | `CHAR_###_NAME` | `CHAR_001_ARIAN` |
| character files | `Model.blend`, `Rig.blend`, `Face.blend`, `Materials.blend`, `Animation_Library.blend` | |
| episode folder | `EP_###` | `EP_001` |
| QC report | `10_QUALITY_CONTROL/<TEST>/<CHAR>_<test>.json` + `.md` | `ARIAN_foot_slip.json` |
| renders | `<CHAR or EP>_<what>.mp4` | `ARIAN_walk.mp4` |

## Objects
| thing | pattern | example |
|---|---|---|
| Rigify rig (animate this) | `<CHAR>_RIG` | `ARIAN_RIG` |
| motion source skeleton (hidden, never animate by hand) | `<CHAR>_MOTION_SRC` | `ARIAN_MOTION_SRC` |
| body / clothes / face parts | `<CHAR>_BODY`, `<CHAR>_CLOTH_<asset>`, `<CHAR>_FACE_<part>` | `ARIAN_FACE_mouth` |
| collections | `<CHAR>` › `<CHAR>_GEO`, `<CHAR>_RIG`, `<CHAR>_HELPERS` | |

## Bones (Rigify human, unchanged names — shared by every character)
- deform: `DEF-*` (only these carry weights). Mechanism: `MCH-*`, originals: `ORG-*` (hidden).
- animator controls: `torso`, `hips`, `chest`, `neck`, `head`, `shoulder.L`, `upper_arm_fk.L`, `hand_ik.L`, `thigh_fk.L`,
  `foot_ik.L`, `toe_ik.L`, `thigh_ik_target.L` (knee pole), `upper_arm_ik_target.L` (elbow pole), fingers `f_index.01.L`, `thumb.01.L` ...
- IK/FK switch: custom property `IK_FK` on `upper_arm_parent.L` / `thigh_parent.L` (0 = IK, 1 = FK).
- puppet face (added by `setup_face.py`): `eye_l/r`, `lid_l/r`, `brow_l/r` (deform the cartoon parts),
  `FACE_CTRL` (sliders as custom properties), `EYES_TARGET` (look-at).
- `.L` / `.R` = the character's own left / right.

## Actions
- reusable library: `UHS_<CATEGORY>_<Name>` (category = folder in `05_MOTION_LIBRARY`), on the Rigify controls only,
  in place: travel lives on the `root` bone of *episode* actions; the library action stores it as the custom
  properties `root_x` / `root_y` (metres per frame from frame 1, character space). Other properties: `loop`,
  `frames`, `speed`, `raw_slip_cm`, `character`. Library actions have a fake user and are marked as assets.
- each character's `Animation_Library.blend` holds the library baked onto *its* rig (same names, IK targets and
  root curves fitted to that body; the custom property `character` says which)
- episode-specific: `EP###_<CHAR>_<what>` (e.g. `EP001_ARIAN_ROOT`, `EP001_ARIAN_FOOTLOCK`)
- facial: `UHS_FACE_<Expression>` (keys only on `FACE_CTRL` properties)

## NLA tracks (per character, bottom to top)
1. `BODY_00`, `BODY_01`, … — one library strip per track, each fading in over the ones below (Replace)
2. `ROOT` — episode root path (Replace, root bone only)
3. `FACE` — facial actions / lip sync (Replace, FACE_CTRL + EYES_TARGET only)
4. `FOOTLOCK`, `FOOTLOCK_2` — additive corrections from the foot-lock passes, computed last (Add)
5. `SECONDARY`, `HEAD_STABILIZE` — optional follow-through layers (Combine)
