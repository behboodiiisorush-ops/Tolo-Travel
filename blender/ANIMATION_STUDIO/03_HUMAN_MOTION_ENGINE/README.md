# 03_HUMAN_MOTION_ENGINE

Real motion comes from motion capture (Mixamo clips in `blender/mocap`); the engine retargets it and fixes what
retargeting breaks. Code: `11_PYTHON_TOOLS/import_motion.py`, `secondary_motion.py`, `nla_sequencer.py`.

| folder | implementation | status |
|---|---|---|
| BODY_MECHANICS | pelvis rotation/translation, spine, shoulders, weight shift come from the capture; the pelvis keeps its sway and bob (only the smooth travel is moved to `root`) | done, tested (QC per action) |
| CENTER_OF_GRAVITY | centre of mass from 18 weighted deform segments (`motion_validation.MASS`) | done (measured) |
| WEIGHT_TRANSFER | comes from capture; checked through balance + contact timing | measured, not synthesised |
| FOOT_LOCKING | heel / ball / toe-tip contact points measured on the real shoe mesh; planted (or touching ≤1 cm) points pinned; pivot hands over heel→ball→tip (toe roll kept); eased in/out; loops baked with padding; episodes get an additive FOOTLOCK NLA track | done, tested |
| BALANCE_SYSTEM | COM over the support polygon of the planted soles, for standing clips | done (measured) |
| SECONDARY_MOTION | `follow_through()` damped-spring overlap, `stabilize_head()` — separate COMBINE NLA layers | done, see report |
| MOTION_SMOOTHING | baked keys use Bezier + auto-clamped handles (no overshoot between frames); no blanket smoothing — impacts stay sharp; pops are *detected* (QC), not blurred | done |
