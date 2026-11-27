# EP01 — «آخرین پیام» (part 1) · production plan
Scenes CH01_SC001–SC005 · 00:00–05:05 (305 s) + ~6 s recap/title card · 1280×720 · 24 fps · EEVEE
Ends on: the stranger's call «کسی که بهت بدهکاره» and the pharmacy door being hit.

## Build order (each step is checked before the next — PROJECT_STATE §0)
| # | step | status |
|---|---|---|
| 1 | Motion system: Mixamo retarget + grounding + IK foot lock + measured QC (`motion_qc.py`, `footlock.py`) | walk: slide 0.25 cm/frame mean, 0 cm sinking — preview being checked |
| 2 | Run test (panic run) with the same pipeline | next |
| 3 | ENV_CITY_STREET: avenue section A (fallen night bus «۴», 6 abandoned cars, blinking amber traffic light, wet asphalt, fog), side street B (trolley, fallen cable, parked car, lit shop window) | waiting for CC0 textures/HDRI access |
| 4 | ENV_CITY_PHARMACY: broken glass door, counter, 4 shelves, wall TV with the emergency card (no channel logo) | after 3 |
| 5 | ENV_NIKA_VIDEO_ROOM (white room) for the phone video, rendered separately and put on the phone screen | after 3 |
| 6 | Zombies: Z1 shambler (woman, torn office coat), Z6 the Driver (plain short-sleeve shirt), Z3 crawler (plain delivery jacket, broken legs), Z5 at the pharmacy (grey tracksuit) | after 2 |
| 7 | Props: Arin's phone (lock screen, video, incoming call screens), broken bottle, gauze, disinfectant, bracelet, transit card «۴» | with 3–4 |
| 8 | Shots, one scene at a time: SC001 → SC005, low-res preview + QC per scene | — |
| 9 | ElevenLabs voices (Arin, Nika, Mark) + SFX, lips + captions fitted | — |
| 10 | Full render split over worker chats (~140 frames each), post: captions, branding overlay, credits | — |
| 11 | QC report → delivery | — |

## Motion sources per action (honest)
| action | source |
|---|---|
| walk, run, jog | Mixamo `walking`, `jog_in_circle`, `goofy_running` (+ foot lock) |
| fear, look around, hide | `terrified`, `nervously_look_around`, `male_action_pose` |
| crawl out from under the bus, get up | `pushing` (down on hands and feet → wary half-crouch) |
| trip and fall, knocked down | `getting_smashed` |
| Driver sprint / pin / bite / sniff | `zombie_run`, `zombie_attack`, `zombie_biting`, `zombie_neck_bite` (sniff = neck-bite clip slowed, no bite) |
| crawler | `zombie_crawl`, `zombie_running_crawl` |
| shambler | `zombie_walk`, `walking_2` |
| vault a bonnet | `jump` (crouch, leap forward, land) |
| kick back, barricade push, phone handling, bandaging | no clip — keyframed on the rig with IK (hands on props), then QC |
Missing clips that would raise quality (the user can download from Mixamo, "Without Skin", FBX): a kick, a vault, pushing a heavy object, texting/looking at a phone while crouched, wrapping a bandage.

## Timing reality
One-time builds (city, pharmacy, zombies, motion system) come before EP01 and take several working days.
EP01 will not be ready for the first 19:00 slot if quality is kept — per §0 it ships late rather than unfinished.
From EP02 on, sets and assets are reused and the two-day rhythm becomes realistic.
