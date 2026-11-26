"""Motion library definition + quality thresholds.

Each entry becomes a Blender Action on the Rigify controls, named  UHS_<CATEGORY>_<Name>  (see naming_conventions.md).
  clip       Mixamo FBX in blender/mocap (what it really shows: blender/mocap/CLIPS.md)
  start/len  seconds into the clip / length in seconds (None = to the end)
  loop       True: cyclic action (walk/run/idle); the last frame is made to match the first
  root       how forward travel is recovered and moved to the `root` bone:
             "feet" (in-place clip: speed from the planted foot), "clip" (take the clip's own hip travel), "none",
             "auto" (measure the hip travel: "clip" if it travels, else "feet")
  lock       foot locking (heel / ball / toe contact points pinned while planted)
  folder     05_MOTION_LIBRARY sub-folder it belongs to
"""

LIBRARY = [
    dict(name="UHS_IDLE_Breathing",      clip="breathing_idle",        start=0.0, len=8.0, loop=True,  root="none", lock=True,  folder="IDLE"),
    dict(name="UHS_IDLE_Nervous",        clip="nervously_look_around", start=0.0, len=6.0, loop=False, root="none", lock=True,  folder="IDLE"),
    dict(name="UHS_WALK_Natural",        clip="walking",               start=0.0, len=None, loop=True, root="auto", lock=True,  folder="WALK"),
    dict(name="UHS_WALK_Sneak",          clip="sneak_walk",            start=0.0, len=None, loop=True, root="auto", lock=True,  folder="WALK"),
    dict(name="UHS_RUN_Cartoon",         clip="goofy_running",         start=0.0, len=None, loop=True, root="auto", lock=True,  folder="RUN"),
    dict(name="UHS_JUMP_Forward",        clip="jump",                  start=0.0, len=None, loop=False, root="clip", lock=True, folder="JUMP"),
    dict(name="UHS_SIT_Idle",            clip="sitting_idle",          start=0.0, len=4.0, loop=True,  root="none", lock=True,  folder="SITTING"),
    dict(name="UHS_STAND_UpFromFloor",   clip="pushing",               start=0.0, len=None, loop=False, root="none", lock=True, folder="STANDING"),
    dict(name="UHS_GESTURE_Yes",         clip="head_nod_yes",          start=0.0, len=None, loop=False, root="none", lock=True, folder="HAND_GESTURES"),
    dict(name="UHS_GESTURE_No",          clip="shaking_head_no",       start=0.0, len=None, loop=False, root="none", lock=True, folder="HAND_GESTURES"),
    dict(name="UHS_GESTURE_ForgetIt",    clip="dismissing_gesture",    start=0.0, len=None, loop=False, root="none", lock=True, folder="HAND_GESTURES"),
    dict(name="UHS_GESTURE_Wait",        clip="hands_forward_gesture", start=0.0, len=None, loop=False, root="none", lock=True, folder="HAND_GESTURES"),
    dict(name="UHS_GESTURE_Thinking",    clip="thinking",              start=0.0, len=None, loop=False, root="none", lock=True, folder="HAND_GESTURES"),
    dict(name="UHS_EMOTION_Terrified",   clip="terrified",             start=8.0, len=6.0, loop=False, root="none", lock=True,  folder="EMOTIONS"),
    dict(name="UHS_INTERACT_OpenDoor",   clip="opening_door_inwards",  start=0.0, len=None, loop=False, root="clip", lock=True, folder="INTERACTIONS"),
    dict(name="UHS_INTERACT_Punch",      clip="cross_punch",           start=0.0, len=None, loop=False, root="clip", lock=True, folder="INTERACTIONS"),
    dict(name="UHS_TRANS_IdleToWalk",    clip="start_walking",         start=0.0, len=None, loop=False, root="clip", lock=True, folder="IDLE_TO_WALK"),
]

# ------------------------------------------------------------------ contact detection / foot locking
CONTACT_HEIGHT = 0.035        # m: a sole point this close to the ground can be planted
CONTACT_SPEED = 0.45          # m/s (relative to the moving root): slower than this = planted
MIN_CONTACT_FRAMES = 3        # shorter contacts are ignored (brushes)
LOCK_BLEND = 3                # frames to ease the lock in / out (no pops)
LOCK_TOUCH_CM = 1.0           # a sole point this low is touching: it is pinned however fast it moves.
                              # (2.5 cm was tried: it also caught the swinging foot near the floor — walk slip 3.7 ->
                              # 21.8 cm in QC — so it stays at the QC touch height)

# ------------------------------------------------------------------ QC thresholds (pass/fail)
QC = dict(
    touch_cm=1.0,             # a sole point within this height of the ground is touching it (slip is measured there)
    foot_slip_cm=1.5,         # max sliding of a touching contact point during one contact
    penetration_cm=1.5,       # sole below the ground
    float_cm=2.5,             # planted sole above the ground
    limb_stretch=0.02,        # |deformed length / rest length - 1|
    knee_max_deg=165.0, elbow_max_deg=160.0,
    joint_flip_deg=55.0,      # knee / elbow bend direction jumping between two frames
    transition_spike=3.0,     # a frame's angular speed > this x the clip's 95th percentile = pop
    min_spike_deg=12.0,       # ...and at least this many degrees per frame
)
