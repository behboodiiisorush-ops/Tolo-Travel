# QC report — LINA

Every number below is measured on the baked animation (frames evaluated in Blender), not assumed.

| action | speed m/s | raw slip cm | locked slip cm | lowest cm | stretch | max knee/elbow ° | rev/flip | pops | IK-FK cm | balance | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| UHS_IDLE_Breathing | 0.0 | 1.06 | 0.0 | -0.0 | 0.000 | 38 / 32 | 0/0 | 0 | 0.0 | 0.0 | PASS |
| UHS_IDLE_Nervous | 0.0 | 1.72 | 0.0 | -0.0 | 0.000 | 44 / 103 | 0/0 | 0 | 0.0 | 0.0 | PASS |
| UHS_WALK_Natural | 1.51 | 1.35 | 1.95 | -0.0 | 0.000 | 72 / 66 | 0/0 | 0 | 0.22 | – | **FAIL** |
| UHS_WALK_Sneak | 1.735 | 2.73 | 0.1 | -0.0 | 0.000 | 123 / 70 | 20/0 | 0 | 0.03 | – | **FAIL** |
| UHS_RUN_Cartoon | 1.611 | 5.77 | 0.19 | -0.0 | 0.000 | 111 / 127 | 0/0 | 0 | 0.0 | – | PASS |
| UHS_JUMP_Forward | 0.004 | 3.15 | 0.42 | -0.0 | 0.000 | 143 / 97 | 9/0 | 0 | 0.0 | – | **FAIL** |
| UHS_SIT_Idle | 0.0 | 0.15 | 0.0 | -0.0 | 0.000 | 101 / 59 | 0/0 | 0 | 0.0 | – | PASS |
| UHS_STAND_UpFromFloor | 0.0 | 8.62 | 4.95 | -0.0 | 0.000 | 159 / 113 | 0/0 | 1 | 0.14 | – | **FAIL** |
| UHS_GESTURE_Yes | 0.0 | 0.54 | 0.0 | -0.0 | 0.000 | 20 / 7 | 0/0 | 0 | 0.0 | 0.0 | PASS |
| UHS_GESTURE_No | 0.0 | 1.48 | 0.0 | -0.0 | 0.000 | 20 / 7 | 0/0 | 0 | 0.0 | 0.0 | PASS |
| UHS_GESTURE_ForgetIt | 0.0 | 0.46 | 0.13 | 0.03 | 0.000 | 2 / 83 | 0/0 | 0 | 0.21 | 0.0 | PASS |
| UHS_GESTURE_Wait | 0.0 | 1.25 | 0.0 | -0.0 | 0.000 | 23 / 86 | 0/0 | 0 | 0.0 | 0.0 | PASS |
| UHS_GESTURE_Thinking | 0.0 | 2.85 | 0.74 | -0.0 | 0.000 | 59 / 150 | 0/0 | 0 | 0.0 | 0.0 | PASS |
| UHS_EMOTION_Terrified | 0.0 | 7.94 | 0.0 | -0.0 | 0.000 | 92 / 149 | 0/0 | 0 | 0.0 | 0.0 | PASS |
| UHS_INTERACT_OpenDoor | 0.207 | 13.57 | 21.8 | -0.7 | 0.000 | 81 / 104 | 0/0 | 0 | 0.22 | – | **FAIL** |
| UHS_INTERACT_Punch | 0.014 | 3.82 | 0.0 | -0.0 | 0.000 | 76 / 138 | 0/0 | 0 | 0.0 | – | PASS |
| UHS_TRANS_IdleToWalk | 0.396 | 10.15 | 16.25 | -0.63 | 0.000 | 68 / 74 | 0/0 | 0 | 0.21 | – | **FAIL** |

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
- LINA_BODY: 16 of 19158 vertices unweighted

Thresholds: `00_CORE_SYSTEM/motion_config.py` (QC).
