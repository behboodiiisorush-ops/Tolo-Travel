# QC report — MOTHER

Every number below is measured on the baked animation (frames evaluated in Blender), not assumed.

| action | speed m/s | raw slip cm | locked slip cm | lowest cm | stretch | max knee/elbow ° | rev/flip | pops | IK-FK cm | balance | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| UHS_IDLE_Breathing | 0.0 | 1.24 | 0.0 | -0.0 | 0.000 | 36 / 32 | 0/0 | 0 | 0.0 | 0.0 | PASS |
| UHS_IDLE_Nervous | 0.0 | 1.78 | 0.06 | -0.0 | 0.000 | 42 / 103 | 0/0 | 0 | 0.0 | 0.0 | PASS |
| UHS_WALK_Natural | 1.672 | 1.59 | 1.63 | -0.0 | 0.000 | 72 / 66 | 0/0 | 0 | 0.21 | – | **FAIL** |
| UHS_WALK_Sneak | 1.912 | 3.23 | 0.11 | -0.0 | 0.000 | 123 / 70 | 4/0 | 0 | 0.03 | – | **FAIL** |
| UHS_RUN_Cartoon | 1.82 | 6.73 | 0.21 | -0.0 | 0.000 | 111 / 127 | 0/0 | 0 | 0.0 | – | PASS |
| UHS_JUMP_Forward | 0.002 | 3.57 | 0.0 | -0.0 | 0.000 | 143 / 97 | 2/0 | 0 | 0.01 | – | **FAIL** |
| UHS_SIT_Idle | 0.0 | 0.19 | 0.0 | -0.0 | 0.000 | 101 / 59 | 0/0 | 0 | 0.0 | – | PASS |
| UHS_STAND_UpFromFloor | 0.0 | 10.22 | 5.49 | -0.0 | 0.000 | 159 / 113 | 0/0 | 0 | 0.15 | – | **FAIL** |
| UHS_GESTURE_Yes | 0.0 | 0.63 | 0.0 | -0.0 | 0.000 | 16 / 7 | 0/0 | 0 | 0.0 | 0.0 | PASS |
| UHS_GESTURE_No | 0.0 | 1.68 | 0.0 | -0.0 | 0.000 | 16 / 7 | 0/0 | 0 | 0.0 | 0.0 | PASS |
| UHS_GESTURE_ForgetIt | 0.0 | 0.41 | 0.15 | -0.0 | 0.000 | 4 / 83 | 0/0 | 0 | 0.21 | 0.0 | PASS |
| UHS_GESTURE_Wait | 0.0 | 1.4 | 0.0 | -0.0 | 0.000 | 20 / 86 | 0/0 | 0 | 0.0 | 0.0 | PASS |
| UHS_GESTURE_Thinking | 0.0 | 3.36 | 1.3 | -0.0 | 0.000 | 59 / 150 | 0/0 | 0 | 0.0 | 0.0 | PASS |
| UHS_EMOTION_Terrified | 0.0 | 8.38 | 0.0 | -0.0 | 0.000 | 92 / 149 | 0/0 | 0 | 0.01 | 0.0 | PASS |
| UHS_INTERACT_OpenDoor | 0.232 | 5.57 | 13.59 | -0.71 | 0.000 | 81 / 104 | 0/0 | 0 | 0.22 | – | **FAIL** |
| UHS_INTERACT_Punch | 0.029 | 5.63 | 4.61 | -0.0 | 0.000 | 74 / 138 | 0/0 | 0 | 0.21 | – | **FAIL** |
| UHS_TRANS_IdleToWalk | 0.0 | 49.94 | 18.81 | -0.08 | 0.000 | 69 / 74 | 0/0 | 2 | 0.21 | – | **FAIL** |

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
- MOTHER_BODY: 16 of 19158 vertices unweighted

Thresholds: `00_CORE_SYSTEM/motion_config.py` (QC).
