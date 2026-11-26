# 05_MOTION_LIBRARY

The library is defined in `00_CORE_SYSTEM/motion_config.py` (`LIBRARY`) and baked per character by
`create_character.py --stage library`. The actions live in each character's `Animation_Library.blend`
(actions only, fake user, marked as assets) and in `Rig.blend`. Sub-folders = categories (`UHS_<CATEGORY>_<Name>`).

What exists (clip -> action): see the QC report of each character (`10_QUALITY_CONTROL/FINAL_REVIEW`).
Missing because no capture exists yet: LANDING as its own clip (the jump contains a landing), TURNING,
STANDING from a chair, a proper (non-cartoon) RUN. Add a Mixamo FBX to `blender/mocap` + a line in `LIBRARY`.
