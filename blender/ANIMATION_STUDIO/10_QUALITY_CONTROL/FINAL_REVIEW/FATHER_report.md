# QC report — FATHER

Every number below is measured on the baked animation (frames evaluated in Blender), not assumed.

| action | speed m/s | raw slip cm | locked slip cm | lowest cm | stretch | max knee/elbow ° | rev/flip | pops | IK-FK cm | balance | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| UHS_IDLE_Breathing | 0.0 | 1.65 | 0.32 | -0.0 | 0.000 | 37 / 32 | 0/0 | 0 | 0.0 | 0.0 | PASS |
| UHS_IDLE_Nervous | 0.0 | 2.5 | 1.29 | -0.0 | 0.000 | 42 / 103 | 0/0 | 0 | 0.0 | 0.0 | PASS |
| UHS_WALK_Natural | 2.129 | 2.84 | 3.98 | -0.72 | 0.000 | 72 / 66 | 0/0 | 0 | 0.22 | – | **FAIL** |
| UHS_WALK_Sneak | 2.466 | 3.94 | 0.2 | -0.0 | 0.000 | 123 / 70 | 0/0 | 0 | 0.01 | – | PASS |
| UHS_RUN_Cartoon | 2.277 | 7.75 | 0.27 | -0.0 | 0.000 | 111 / 127 | 0/0 | 0 | 0.0 | – | PASS |
| UHS_JUMP_Forward | 0.041 | 4.54 | 0.19 | -0.0 | 0.000 | 143 / 97 | 2/0 | 0 | 0.01 | – | **FAIL** |
| UHS_SIT_Idle | 0.0 | 0.24 | 0.02 | -0.0 | 0.000 | 99 / 59 | 0/0 | 0 | 0.0 | – | PASS |
| UHS_STAND_UpFromFloor | 0.0 | 12.54 | 6.21 | -0.0 | 0.000 | 159 / 113 | 0/0 | 1 | 0.12 | – | **FAIL** |
| UHS_GESTURE_Yes | 0.0 | 0.81 | 0.03 | -0.0 | 0.000 | 21 / 7 | 0/0 | 0 | 0.0 | 0.0 | PASS |
| UHS_GESTURE_No | 0.0 | 2.14 | 0.08 | -0.0 | 0.000 | 21 / 7 | 0/0 | 0 | 0.0 | 0.0 | PASS |
| UHS_GESTURE_ForgetIt | 0.0 | 0.59 | 0.0 | -0.0 | 0.000 | 23 / 83 | 0/0 | 0 | 0.0 | 0.0 | PASS |
| UHS_GESTURE_Wait | 0.0 | 1.97 | 0.16 | -0.0 | 0.000 | 21 / 86 | 0/0 | 0 | 0.0 | 0.0 | PASS |
| UHS_GESTURE_Thinking | 0.0 | 4.07 | 1.85 | -0.0 | 0.000 | 59 / 150 | 0/0 | 0 | 0.0 | 0.029 | **FAIL** |
| UHS_EMOTION_Terrified | 0.0 | 11.18 | 0.38 | -0.0 | 0.000 | 93 / 149 | 0/0 | 0 | 0.01 | 0.0 | PASS |
| UHS_INTERACT_OpenDoor | 0.331 | 25.36 | 21.77 | -0.76 | 0.000 | 81 / 104 | 0/0 | 0 | 0.21 | – | **FAIL** |
| UHS_INTERACT_Punch | 0.022 | 5.25 | 5.3 | -0.0 | 0.000 | 76 / 138 | 0/0 | 0 | 0.01 | – | **FAIL** |
| UHS_TRANS_IdleToWalk | 0.0 | 77.6 | 44.25 | -0.18 | 0.000 | 69 / 74 | 0/0 | 0 | 0.18 | – | **FAIL** |

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
- FATHER_BODY: 16 of 19158 vertices unweighted

Thresholds: `00_CORE_SYSTEM/motion_config.py` (QC).
