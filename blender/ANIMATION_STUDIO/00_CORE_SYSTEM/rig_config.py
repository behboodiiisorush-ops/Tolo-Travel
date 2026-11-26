"""Rig layout shared by every character: the Rigify meta-rig, the motion-source (MakeHuman game_engine) skeleton
and how its bones drive the Rigify controls, IK/FK defaults, puppet proportions and the puppet face bones."""

METARIG = "rigify.human_toes"          # MPFB meta-rig fitted to the MakeHuman body (has toe + face bones)
RIG_SUFFIX = "_RIG"                    # generated Rigify rig: ARIAN_RIG
SRC_SUFFIX = "_MOTION_SRC"             # hidden game_engine skeleton that receives the Mixamo clips

HEAD_DEF = "DEF-spine.006"             # head deform bone in the Rigify human meta-rig
NECK_DEF = "DEF-spine.004"

# Rigify control  <-  motion-source bone. The control is attached rigidly to the source bone's movement
# (Child Of with the inverse taken in the rest pose) and then baked. FK and IK controls are both baked,
# so the IK_FK switch works on every action.
CONTROL_FROM_SOURCE = {
    "torso": "pelvis", "hips": "pelvis", "chest": "spine_03", "neck": "neck_01", "head": "head",
}
for S, s in (("L", "l"), ("R", "r")):
    CONTROL_FROM_SOURCE.update({
        f"shoulder.{S}": f"clavicle_{s}",
        f"upper_arm_fk.{S}": f"upperarm_{s}", f"forearm_fk.{S}": f"lowerarm_{s}", f"hand_fk.{S}": f"hand_{s}",
        f"thigh_fk.{S}": f"thigh_{s}", f"shin_fk.{S}": f"calf_{s}", f"foot_fk.{S}": f"foot_{s}", f"toe_fk.{S}": f"ball_{s}",
    })
    for f in ("thumb", "index", "middle", "ring", "pinky"):
        rf = "thumb" if f == "thumb" else "f_" + f
        for i in (1, 2, 3):
            CONTROL_FROM_SOURCE[f"{rf}.0{i}.{S}"] = f"{f}_0{i}_{s}"

# IK controls are NOT taken from the source skeleton (its legs are a few cm longer than the Rigify legs: the IK
# target would be out of reach and the toe tore off the foot — found by QC). They are snapped to where the FK chain
# ends, every frame: IK control <- ORG bone (rigid, rest-relative).
IK_FROM_FK = {}
for S in ("L", "R"):
    IK_FROM_FK.update({f"foot_ik.{S}": f"ORG-foot.{S}", f"toe_ik.{S}": f"ORG-toe.{S}",
                       f"thigh_ik_target.{S}": f"ORG-shin.{S}", f"hand_ik.{S}": f"ORG-hand.{S}",
                       f"upper_arm_ik_target.{S}": f"ORG-forearm.{S}"})

# controls that keep baked *location* keys; every other control only rotates (its position follows its parent).
# (toe_ik with its own location detached the toe from a foot-locked foot by 3 cm — found by QC)
LOCATION_CONTROLS = ("torso", "foot_ik.L", "foot_ik.R", "hand_ik.L", "hand_ik.R",
                     "thigh_ik_target.L", "thigh_ik_target.R", "upper_arm_ik_target.L", "upper_arm_ik_target.R")

LIMB_PARENTS = {"arm": ("upper_arm_parent.L", "upper_arm_parent.R"), "leg": ("thigh_parent.L", "thigh_parent.R")}
DEFAULT_IK_FK = {"arm": 1.0, "leg": 0.0}   # Rigify: 0 = IK, 1 = FK. Legs IK (foot locking), arms FK (swing)
IK_STRETCH = 0.0                           # no rubber limbs
USE_POLE = 1                               # knees / elbows aim at the *_ik_target pole controls

# puppet proportions («واگن آخر» look): forced local scale on these deform bones (Limit Scale, last in stack)
PROPORTIONS = {HEAD_DEF: 1.38, "DEF-hand.L": 1.2, "DEF-hand.R": 1.2, "DEF-foot.L": 1.12, "DEF-foot.R": 1.12}

# the cartoon face (blender/studio/characters.py): rigid parts are weighted to these bones
FACE_BONES = ["eye_l", "eye_r", "lid_l", "lid_r", "brow_l", "brow_r"]
FACE_CTRL = "FACE_CTRL"                    # all facial sliders live here as custom properties
EYES_TARGET = "EYES_TARGET"                # look-at control in front of the face
HIDDEN_COLLECTIONS = ("Face", "Face (Primary)", "Face (Secondary)", "Face (Expressions)")   # realistic face: masked away

# QC: which deform bones count for joint checks
JOINTS = {"knee.L": ("DEF-thigh.L", "DEF-shin.L"), "knee.R": ("DEF-thigh.R", "DEF-shin.R"),
          "elbow.L": ("DEF-upper_arm.L", "DEF-forearm.L"), "elbow.R": ("DEF-upper_arm.R", "DEF-forearm.R")}
