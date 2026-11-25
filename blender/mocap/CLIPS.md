# Mixamo clips (FBX, Without Skin) — put them on any cast character with `blender/cast/mocap.py`

```python
import cast, mocap
ch = cast.spawn("arian")
clip = mocap.load("blender/mocap/sneak_walk.fbx")
n = mocap.apply(ch, clip, start=1, offset=(x, y, 0), facing=90, in_place=False)   # returns frame count
```
Check poses fast: `../cast/bpy.sh test_clips.py --clips a,b,c` -> `test/clips_<name>_<k>.png`.

| file | seconds | what |
|---|---|---|
| breathing_idle | 9.9 | calm standing, breathing (loop) |
| nervously_look_around | 6.3 | standing, glancing around nervously |
| sitting_idle | 4.3 | seated idle (put a chair/bed under the hips) |
| start_walking | 2.9 | from standing into a walk |
| walking | 1.0 | walk cycle (loop) |
| walking_2 | 1.5 | hunched / stumbling walk (loop) |
| sneak_walk | 1.1 | crouched sneaking (loop) |
| pistol_walk | 0.8 | walk holding a pistol in both hands (loop) |
| jog_in_circle | 5.9 | jog along a circle |
| climbing_to_top | 4.0 | climb up onto a ledge |
| opening_door_inwards | 6.4 | grab handle, pull door, step through |
| reloading | 3.7 | reload a rifle |
| dismissing_gesture | 2.2 | "forget it" hand wave |
| hands_forward_gesture | 3.1 | both hands forward, open palms ("wait, listen" / explaining) |
| zombie_idle | 4.3 | swaying zombie stand |
| zombie_walk | 4.0 | zombie walk |
| zombie_run | 0.8 | zombie run (loop) |
| zombie_attack | 2.6 | lunge and swipe |
| zombie_scream | 2.8 | crouch and scream |
| zombie_neck_bite | 4.2 | grab and bite a neck |
| zombie_biting | 6.9 | down on the ground eating, then stands |
| zombie_biting_2 | 2.3 | eating on the ground (loop) |
| zombie_crawl | 5.1 | crawling on the floor |
| zombie_running_crawl | 0.7 | fast crawl on all fours (loop) |
| zombie_death | 3.0 | shot, falls on the back |
| zombie_dying | 3.3 | sinks to the knees, falls forward |
