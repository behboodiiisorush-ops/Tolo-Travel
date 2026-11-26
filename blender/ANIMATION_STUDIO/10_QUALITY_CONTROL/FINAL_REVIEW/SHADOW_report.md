# QC report — SHADOW

Every number below is measured on the baked animation (frames evaluated in Blender), not assumed.

| action | speed m/s | raw slip cm | locked slip cm | lowest cm | stretch | max knee/elbow ° | rev/flip | pops | IK-FK cm | balance | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| UHS_IDLE_Breathing | 0.0 | 1.53 | 0.33 | -0.0 | 0.000 | 37 / 32 | 0/0 | 0 | 0.0 | 0.0 | PASS |
| UHS_IDLE_Nervous | 0.0 | 2.65 | 1.33 | -0.0 | 0.000 | 43 / 103 | 0/0 | 0 | 0.0 | 0.0 | PASS |
| UHS_WALK_Natural | 2.234 | 2.97 | 4.15 | -0.76 | 0.000 | 72 / 66 | 0/0 | 0 | 0.22 | – | **FAIL** |
| UHS_WALK_Sneak | 2.501 | 3.76 | 0.21 | -0.0 | 0.000 | 123 / 70 | 0/0 | 0 | 0.01 | – | PASS |
| UHS_RUN_Cartoon | 2.291 | 7.88 | 0.28 | -0.0 | 0.000 | 111 / 127 | 0/0 | 0 | 0.0 | – | PASS |
| UHS_JUMP_Forward | 0.006 | 4.72 | 0.2 | -0.0 | 0.000 | 143 / 97 | 0/0 | 0 | 0.01 | – | PASS |
| UHS_SIT_Idle | 0.0 | 0.27 | 0.02 | -0.0 | 0.000 | 98 / 59 | 0/0 | 0 | 0.0 | – | PASS |
| UHS_STAND_UpFromFloor | 0.0 | 12.67 | 6.39 | -0.0 | 0.000 | 159 / 113 | 0/0 | 1 | 0.03 | – | **FAIL** |
| UHS_GESTURE_Yes | 0.0 | 0.82 | 0.03 | -0.0 | 0.000 | 21 / 7 | 0/0 | 0 | 0.0 | 0.0 | PASS |
| UHS_GESTURE_No | 0.0 | 2.16 | 0.09 | -0.0 | 0.000 | 21 / 7 | 0/0 | 0 | 0.0 | 0.0 | PASS |
| UHS_GESTURE_ForgetIt | 0.0 | 0.42 | 0.0 | -0.0 | 0.000 | 23 / 83 | 0/0 | 0 | 0.0 | 0.0 | PASS |
| UHS_GESTURE_Wait | 0.0 | 2.27 | 0.17 | -0.0 | 0.000 | 22 / 86 | 0/0 | 0 | 0.0 | 0.0 | PASS |
| UHS_GESTURE_Thinking | 0.0 | 3.97 | 1.51 | -0.0 | 0.000 | 59 / 150 | 0/0 | 0 | 0.0 | 0.029 | **FAIL** |
| UHS_EMOTION_Terrified | 0.0 | 11.45 | 0.26 | -0.0 | 0.000 | 93 / 149 | 0/0 | 0 | 0.01 | 0.0 | PASS |
| UHS_INTERACT_OpenDoor | 0.341 | 25.8 | 22.38 | -0.65 | 0.000 | 81 / 104 | 0/0 | 0 | 0.22 | – | **FAIL** |
| UHS_INTERACT_Punch | 0.045 | 4.83 | 4.05 | -0.0 | 0.000 | 76 / 138 | 0/0 | 0 | 0.21 | – | **FAIL** |
| UHS_TRANS_IdleToWalk | 0.0 | 62.87 | 18.08 | -0.0 | 0.000 | 69 / 74 | 0/0 | 2 | 0.17 | – | **FAIL** |

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
- SHADOW_BODY: 16 of 19158 vertices unweighted

Thresholds: `00_CORE_SYSTEM/motion_config.py` (QC).
