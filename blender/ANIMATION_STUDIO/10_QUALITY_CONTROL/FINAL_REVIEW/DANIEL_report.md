# QC report — DANIEL

Every number below is measured on the baked animation (frames evaluated in Blender), not assumed.

| action | speed m/s | raw slip cm | locked slip cm | lowest cm | stretch | max knee/elbow ° | rev/flip | pops | IK-FK cm | balance | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| UHS_IDLE_Breathing | 0.0 | 1.47 | 0.0 | -0.0 | 0.000 | 38 / 32 | 0/0 | 0 | 0.0 | 0.0 | PASS |
| UHS_IDLE_Nervous | 0.0 | 2.56 | 0.1 | -0.0 | 0.000 | 44 / 103 | 0/0 | 0 | 0.0 | 0.0 | PASS |
| UHS_WALK_Natural | 1.808 | 2.66 | 3.49 | -0.0 | 0.000 | 72 / 66 | 0/0 | 0 | 0.22 | – | **FAIL** |
| UHS_WALK_Sneak | 2.051 | 3.46 | 0.11 | -0.0 | 0.000 | 123 / 70 | 0/0 | 0 | 0.01 | – | PASS |
| UHS_RUN_Cartoon | 1.9 | 14.15 | 4.21 | -0.0 | 0.000 | 111 / 127 | 0/0 | 0 | 0.18 | – | **FAIL** |
| UHS_JUMP_Forward | 0.001 | 3.82 | 0.0 | -0.0 | 0.000 | 143 / 97 | 0/0 | 0 | 0.01 | – | PASS |
| UHS_SIT_Idle | 0.0 | 0.23 | 0.0 | -0.0 | 0.000 | 100 / 59 | 0/0 | 0 | 0.0 | – | PASS |
| UHS_STAND_UpFromFloor | 0.0 | 11.71 | 5.79 | -0.0 | 0.000 | 159 / 113 | 0/0 | 0 | 0.01 | – | **FAIL** |
| UHS_GESTURE_Yes | 0.0 | 0.69 | 0.0 | -0.0 | 0.000 | 23 / 7 | 0/0 | 0 | 0.0 | 0.0 | PASS |
| UHS_GESTURE_No | 0.0 | 1.81 | 0.0 | -0.0 | 0.000 | 23 / 7 | 0/0 | 0 | 0.0 | 0.0 | PASS |
| UHS_GESTURE_ForgetIt | 0.0 | 0.54 | 0.0 | -0.0 | 0.000 | 20 / 83 | 0/0 | 0 | 0.0 | 0.0 | PASS |
| UHS_GESTURE_Wait | 0.0 | 1.62 | 0.0 | -0.0 | 0.000 | 24 / 86 | 0/0 | 0 | 0.0 | 0.0 | PASS |
| UHS_GESTURE_Thinking | 0.0 | 3.59 | 0.91 | -0.0 | 0.000 | 59 / 150 | 0/0 | 0 | 0.0 | 0.0 | PASS |
| UHS_EMOTION_Terrified | 0.0 | 10.23 | 0.0 | -0.0 | 0.000 | 94 / 149 | 0/0 | 0 | 0.0 | 0.0 | PASS |
| UHS_INTERACT_OpenDoor | 0.261 | 17.12 | 19.15 | -0.63 | 0.000 | 81 / 104 | 0/0 | 0 | 0.22 | – | **FAIL** |
| UHS_INTERACT_Punch | 0.016 | 4.51 | 5.3 | -0.0 | 0.000 | 77 / 138 | 0/0 | 0 | 0.0 | – | **FAIL** |
| UHS_TRANS_IdleToWalk | 0.474 | 15.02 | 11.25 | -0.75 | 0.000 | 70 / 74 | 0/0 | 0 | 0.21 | – | **FAIL** |

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
- DANIEL_BODY: 16 of 19158 vertices unweighted

Thresholds: `00_CORE_SYSTEM/motion_config.py` (QC).
