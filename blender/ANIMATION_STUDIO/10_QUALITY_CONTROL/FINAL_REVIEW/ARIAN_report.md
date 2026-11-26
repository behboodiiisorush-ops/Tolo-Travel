# QC report — ARIAN

Every number below is measured on the baked animation (frames evaluated in Blender), not assumed.

| action | speed m/s | raw slip cm | locked slip cm | lowest cm | stretch | max knee/elbow ° | rev/flip | pops | IK-FK cm | balance | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| UHS_IDLE_Breathing | 0.0 | 1.44 | 0.3 | -0.0 | 0.000 | 38 / 32 | 0/0 | 0 | 0.0 | 0.0 | PASS |
| UHS_IDLE_Nervous | 0.0 | 2.46 | 1.33 | -0.0 | 0.000 | 43 / 103 | 0/0 | 0 | 0.0 | 0.0 | PASS |
| UHS_WALK_Natural | 2.002 | 2.62 | 3.67 | -0.73 | 0.000 | 72 / 66 | 0/0 | 0 | 0.22 | – | **FAIL** |
| UHS_WALK_Sneak | 2.262 | 3.56 | 0.19 | -0.0 | 0.000 | 123 / 70 | 0/0 | 0 | 0.01 | – | PASS |
| UHS_RUN_Cartoon | 2.089 | 7.13 | 0.25 | -0.0 | 0.000 | 111 / 127 | 0/0 | 0 | 0.0 | – | PASS |
| UHS_JUMP_Forward | 0.039 | 4.26 | 0.18 | -0.0 | 0.000 | 143 / 97 | 0/0 | 0 | 0.01 | – | PASS |
| UHS_SIT_Idle | 0.0 | 0.25 | 0.02 | -0.0 | 0.000 | 99 / 59 | 0/0 | 0 | 0.0 | – | PASS |
| UHS_STAND_UpFromFloor | 0.0 | 12.38 | 6.23 | -0.0 | 0.000 | 159 / 113 | 0/0 | 0 | 0.01 | – | **FAIL** |
| UHS_GESTURE_Yes | 0.0 | 0.76 | 0.03 | -0.0 | 0.000 | 22 / 7 | 0/0 | 0 | 0.0 | 0.0 | PASS |
| UHS_GESTURE_No | 0.0 | 1.97 | 0.08 | -0.0 | 0.000 | 22 / 7 | 0/0 | 0 | 0.0 | 0.0 | PASS |
| UHS_GESTURE_ForgetIt | 0.0 | 0.44 | 0.0 | -0.0 | 0.000 | 24 / 83 | 0/0 | 0 | 0.0 | 0.0 | PASS |
| UHS_GESTURE_Wait | 0.0 | 2.01 | 0.15 | -0.0 | 0.000 | 23 / 86 | 0/0 | 0 | 0.0 | 0.0 | PASS |
| UHS_GESTURE_Thinking | 0.0 | 3.82 | 1.22 | -0.0 | 0.000 | 59 / 150 | 0/0 | 0 | 0.0 | 0.0 | PASS |
| UHS_EMOTION_Terrified | 0.0 | 10.63 | 0.36 | -0.0 | 0.000 | 93 / 149 | 0/0 | 0 | 0.01 | 0.0 | PASS |
| UHS_INTERACT_OpenDoor | 0.302 | 23.11 | 18.17 | -0.74 | 0.000 | 81 / 104 | 0/0 | 0 | 0.22 | – | **FAIL** |
| UHS_INTERACT_Punch | 0.019 | 5.0 | 4.96 | -0.0 | 0.000 | 76 / 138 | 0/0 | 0 | 0.0 | – | **FAIL** |
| UHS_TRANS_IdleToWalk | 0.497 | 16.64 | 13.0 | -0.12 | 0.000 | 69 / 74 | 0/0 | 0 | 0.22 | – | **FAIL** |

## Face — PASS

| expression | open | smile | frown | wide | o | lid ° | brow mm | |
|---|---|---|---|---|---|---|---|---|
| Neutral | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | PASS |
| Happy | 0.0 | 1.0 | 0.0 | 0.0 | 0.0 | 0.0 | 2.7 | PASS |
| Sad | 0.0 | 0.0 | 0.8 | 0.0 | 0.0 | 25.0 | 5.4 | PASS |
| Angry | 0.0 | 0.0 | 0.4 | 0.3 | 0.0 | 20.0 | 4.5 | PASS |
| Surprise | 0.6 | 0.0 | 0.0 | 0.0 | 0.5 | 0.0 | 11.7 | PASS |
| Fear | 0.35 | 0.0 | 0.0 | 0.6 | 0.0 | 0.0 | 7.2 | PASS |
| Blink | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 95.0 | 0.0 | PASS |
| Wink | 0.0 | 0.6 | 0.0 | 0.0 | 0.0 | 95.0 | 0.0 | PASS |
| Talk_A | 0.8 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | PASS |
| Talk_O | 0.4 | 0.0 | 0.0 | 0.0 | 1.0 | 0.0 | 0.0 | PASS |
| Talk_E | 0.3 | 0.0 | 0.0 | 0.8 | 0.0 | 0.0 | 0.0 | PASS |

Eye tracking constraints: PASS

## Weights — PASS

Visible unweighted body vertices: 0
- ARIAN_BODY: 16 of 19158 vertices unweighted

Thresholds: `00_CORE_SYSTEM/motion_config.py` (QC).
