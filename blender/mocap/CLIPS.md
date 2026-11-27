# Mixamo clips (FBX, Without Skin) — put them on any cast character with `blender/cast/mocap.py`

```python
import cast, mocap
ch = cast.spawn("arian")
clip = mocap.load("blender/mocap/sneak_walk.fbx")
n = mocap.apply(ch, clip, start=1, offset=(x, y, 0), facing=90, in_place=False)   # returns frame count
```
Check poses fast: `../cast/bpy.sh test_clips.py --clips a,b,c` -> `test/clips_<name>_<k>.png`.

| file | sec | what it REALLY shows (checked frame by frame, 12 moments each) | use it for |
|---|---|---|---|
| breathing_idle | 9.9 | standing still, slow breathing, tiny weight shifts | anyone waiting / listening |
| nervously_look_around | 6.3 | knees a bit bent, hands half-open, head turning left/right | fear, listening for a noise |
| thinking | 4.2 | one hand to the chest, other on the hip, weight shifts, then relaxes | thinking, explaining |
| head_nod_yes | 2.6 | small nods | "yes" |
| shaking_head_no | 1.8 | head shakes | "no" |
| dismissing_gesture | 2.2 | right hand rises and waves off | "forget it" |
| hands_forward_gesture | 3.1 | both open hands come forward, then down | "wait / listen / calm down" |
| talking_phone_pacing | 42.2 | phone at the ear, walking around, turning, free hand gesturing | phone calls (cut a piece) |
| terrified | 20.0 | hands clasped at the chest with the head down, then arms over the head (flinch), cowering, looking around | panic, hiding from a sound |
| sitting_idle | 4.3 | seated, hands on knees, small moves | sitting on a bed / chair |
| sneak_walk | 1.1 | deep crouch, sneaking step (in place) | creeping, crouched walking |
| male_action_pose | still | crouched low, one arm up, ready to spring | hiding behind something |
| pushing | 4.0 | down on hands and feet near the floor, head low, then gets up into a wary half-crouch | getting up from the floor / out of hiding |
| pushing_2 | 2.7 | half-kneeling, one hand held out, other by the face | kneeling, warding something off |
| opening_a_filing_cabinet | 14.2 | squats right down, searches low on the floor, stands up | looking under a bed / searching the floor |
| opening_door_inwards | 6.4 | hand to handle, pulls the door, leans and steps through | doors |
| double_dagger_stab | 3.1 | fighter crouch, BOTH hands together raised above the head, then driven down hard (twice) | sledgehammer blows on a wall |
| jump | 2.2 | crouch, leap forward with arms out, land, straighten | jumping over rubble / through a hole |
| getting_smashed | 2.3 | hunched, hit in the chest, thrown back, lands on the back | being knocked down / attacked |
| cross_punch | 2.0 | boxer guard, one big straight punch forward with a step, back to guard | one hard punch on the steel door |
| punching_bag | 3.2 | upright guard, a run of quick short punches | hammering the door with fists |
| start_walking | 2.9 | standing -> walking | starting to walk |
| start_walking_2 | 2.9 | the same motion as start_walking, exported from a shorter (custom) Mixamo skeleton (`mixamorig1:`); retargets the same | starting to walk |
| walking | 1.0 | normal walk (in place) | walking |
| walking_2 | 1.5 | slouched shuffle, arms dangling (not a normal walk) | exhausted / zombie-like walk |
| pistol_walk | 0.8 | both hands together at chest height, walking (in place) | walking holding something in front |
| goofy_running | 0.6 | loose silly run (in place) | comic run |
| jog_in_circle | 5.9 | jogging along a circle | running |
| climbing_to_top | 4.0 | reaches up, pulls up, steps over, stands with arms out | climbing onto a ledge / into a vent |
| reloading | 3.7 | hands working in front of the body (rifle reload) | fiddling with an object in the hands |
| walking_3 | 1.0 | normal relaxed walk, slightly longer stride than `walking` (in place) | ordinary walking, variety in crowds |
| sitting_talking | 45.0 | seated with the legs crossed, talking with both hands, small leans and weight shifts (cut a piece) | conversations on a bus / train seat, sofa |
| sit_to_stand | 2.3 | from sitting: leans forward, pushes on the knees, stands up straight | getting up from a seat |
| pointing | 2.8 | standing, right arm rises across the body and points to the character's left, holds, lowers | "look there!" — rotate `facing` so the arm aims at the target |
| crying | 6.3 | standing, hands to the face, wipes the eyes, shoulders shake, one arm drops open in despair | grief, crying |
| driving | 5.0 | seated, both hands forward at wheel height, small steering turns (loop) | bus / car driver |
| zombie_idle | 4.3 | hunched, swaying | zombies |
| zombie_walk | 4.0 | hunched lurching walk, arms forward | zombies |
| zombie_run | 0.8 | hunched run, arms back | zombies |
| zombie_attack | 2.6 | lunge, swipe, recover | zombies |
| zombie_scream | 2.8 | crouches low, screams, rises | zombies |
| zombie_neck_bite | 4.2 | grabs forward, bites, pulls back | zombies |
| zombie_biting | 6.9 | drops to the ground eating, gets back up | zombies |
| zombie_biting_2 | 2.3 | on the ground eating (loop) | zombies |
| zombie_crawl | 5.1 | slow crawl on the belly | zombies |
| zombie_running_crawl | 0.7 | fast crawl on all fours (loop) | zombies |
| zombie_death | 3.0 | hit, twists, falls on the back | deaths |
| zombie_dying | 3.3 | drops to the knees, falls forward | deaths |
