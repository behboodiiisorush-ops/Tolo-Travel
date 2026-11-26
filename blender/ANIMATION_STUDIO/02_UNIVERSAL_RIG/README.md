# 02_UNIVERSAL_RIG — one rig layout for every character

Built by `11_PYTHON_TOOLS/generate_rig.py` from `00_CORE_SYSTEM/rig_config.py`. Not a separate file per piece:
the Rigify rig *is* the universal rig; these sub-folders map the spec's components onto it.

| folder | what it is in the rig | where it is set up |
|---|---|---|
| DEFORMATION_RIG | `DEF-*` bones only carry weights (body via MPFB Rigify weights, clothes via MPFB mhclo interpolation, cartoon face parts rigid) | `generate_rig.build` |
| CONTROL_RIG | Rigify controls (`torso`, `hips`, `chest`, `neck`, `head`, limbs, fingers, toes) + puppet face controls | Rigify + `setup_face.build` |
| IK_FK_SYSTEM | `IK_FK` slider on `thigh_parent.*` / `upper_arm_parent.*`; every library action has FK **and** IK keys; `fk_from_ik()` snaps FK to the (foot-locked) IK; `ik_fk_mismatch()` measures the jump by really toggling | `setup_ik_fk.py` |
| HAND_CONTROLS | `hand_fk/ik`, `f_index.01…03`, `thumb.01…03`, finger masters (Rigify) | Rigify |
| FOOT_CONTROLS | `foot_ik`, `toe_ik`, heel roll `foot_heel_ik`, knee poles `thigh_ik_target` (pole on) | Rigify + `rig_config.USE_POLE` |
| SPINE_CONTROLS | `torso` (master), `hips`, `chest`, spine FK + tweak chain | Rigify |
| RIGIFY_SETUP | meta-rig `rigify.human_toes` fitted by MPFB to the MakeHuman body, generated with Rigify (Blender's bundled add-on) | `generate_rig.build` |

Settings that matter: IK stretch **off** (also `ik_stretch = 0` on the IK solver bones — otherwise Rigify's solver
shrank the legs by up to 3 %, caught by QC), legs default IK, arms FK, puppet proportions as `Limit Scale` on
`DEF-spine.006` (head ×1.38), `DEF-hand.*` (×1.2), `DEF-foot.*` (×1.12). Opening a rig in Blender: allow
"Auto Run Python Scripts" for the Rigify rig UI panel (IK/FK snap buttons); the face drivers need no scripts.
