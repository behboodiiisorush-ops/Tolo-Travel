# 10_QUALITY_CONTROL — `11_PYTHON_TOOLS/motion_validation.py`

Numbers measured on the evaluated animation in Blender. Thresholds: `00_CORE_SYSTEM/motion_config.py` (`QC`).
- WALK_TEST / RUN_TEST / FINAL_REVIEW: one JSON per action, `FINAL_REVIEW/<CHAR>_report.md` = the summary table
- FOOT_SLIP_TEST: raw (before locking) vs locked slip, ground penetration / floating
- RIG_DEFORMATION_TEST: unweighted vertices per mesh; stress-pose renders in the character's `TESTS`
- FACIAL_TEST: every preset moves the parts it should (read from the evaluated depsgraph)
- logs/: pipeline logs
Videos you should look at too: `01_CHARACTER_LIBRARY/CHAR_###/TESTS/*.mp4`, `12_EPISODES/EP_001/Renders/`.
