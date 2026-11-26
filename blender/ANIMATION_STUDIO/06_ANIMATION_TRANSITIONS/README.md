# 06_ANIMATION_TRANSITIONS — `11_PYTHON_TOOLS/nla_sequencer.py`

Library strips sit on NLA tracks `BODY_00`, `BODY_01`, … stacked upwards; each one fades in (`blend_in`) over the
one below (alternating two tracks was tried: every other strip ended up underneath -> hard cuts, found by QC).
The root travel is blended with the same weights and integrated (a walk blending into a run speeds up smoothly), and
the foot-lock pass runs on the evaluated stack, so blends don't slide the feet. QC (`validate_range`) checks pops.

| folder | how it is done now |
|---|---|
| IDLE_TO_WALK | real capture `UHS_TRANS_IdleToWalk` (start_walking) |
| WALK_TO_RUN | cross-fade 6 frames + blended root speed + foot lock |
| RUN_TO_STOP | cross-fade run -> walk -> gesture (no stopping capture yet) |
| STAND_TO_SIT | not done: needs a stand-to-sit capture (cross-fading standing into `UHS_SIT_Idle` would float) |
| ACTION_BLENDING | any two library actions: `sequence(rig, [dict(action=..., blend=8), ...])` |
