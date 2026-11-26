# 11_PYTHON_TOOLS — run with `blender/cast/bpy.sh <script>` (after `blender/cast/setup.sh`)

| file | role |
|---|---|
| create_character.py | the pipeline for one character: `ARIAN --stage build,library,qc,tests,split` |
| generate_rig.py | puppet body -> Rigify rig, clothes/face rebinding, proportions, sole points, weight report |
| setup_ik_fk.py | bake source motion onto FK + IK controls, IK/FK switch, FK-from-IK snap, action helpers |
| setup_face.py | FACE_CTRL sliders + drivers, eye target, expressions, auto blink, lip sync |
| import_motion.py | Mixamo -> action: root motion, contacts, foot locking, root curves, NLA helpers |
| motion_validation.py | QC metrics and reports |
| render_shorts.py | stage, cameras, engines, frames -> mp4 |
| nla_sequencer.py | episodes from library strips: cross-fades, blended root, additive foot lock, face track |
| secondary_motion.py | follow-through and head stabilisation layers |
Every tool raises a named error (`RigBuildError`, `BakeError`, `MotionError`, `FaceError`, `SequenceError`) with the
reason instead of continuing half-done; the library stage records failed clips and goes on.
