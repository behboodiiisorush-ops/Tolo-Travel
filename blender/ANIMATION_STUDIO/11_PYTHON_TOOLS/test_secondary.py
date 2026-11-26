"""Test of secondary_motion.py on a real action (walk, 2 cycles): does the COMBINE layer produce exactly the world
rotations it computed, does it add pops, how much does it change the motion?  -> 10_QUALITY_CONTROL/FINAL_REVIEW/
    blender/cast/bpy.sh ANIMATION_STUDIO/11_PYTHON_TOOLS/test_secondary.py ARIAN
"""
import bpy, os, sys, json, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "00_CORE_SYSTEM"))
import project_config as PC  # noqa: E402
import create_character as CC  # noqa: E402
import import_motion as IM  # noqa: E402
import secondary_motion as SM  # noqa: E402
import motion_validation as V  # noqa: E402
from mathutils import Quaternion  # noqa: E402


def main(key="ARIAN", action="UHS_WALK_Natural", loops=2):
    rig, src = CC.open_rig(key)
    for o in rig.children:
        o.hide_viewport = True
    ad = rig.animation_data
    act = bpy.data.actions[action]
    n = int(act["frames"])
    N = n * loops
    for t in list(ad.nla_tracks):
        ad.nla_tracks.remove(t)
    ad.action = None
    IM.nla_strip(rig, "BODY", act, 1, repeat=float(loops))
    root = IM.key_root(rig, 1, N, IM.root_fn(act), "TEST_ROOT")
    tr = ad.nla_tracks.new()
    tr.name = "ROOT"
    tr.strips.new(root.name, 1, root)
    before = V.validate_range(rig, 1, N, "walk without secondary")
    hands_before = {b: SM._as_array(SM._world_rot(rig, b, 1, N)) for b in ("hand_fk.L", "hand_fk.R")}
    head_before = SM._as_array(SM._world_rot(rig, "head", 1, N))
    want_hands = SM.follow_through(rig, 1, N)
    SM.stabilize_head(rig, 1, N)
    smooth = SM._lowpass(head_before, 4)
    want_head = [tuple(Quaternion(a).slerp(Quaternion(b), 0.6)) for a, b in zip(head_before, smooth)]
    err = {b: SM.check(rig, b, 1, N, want_hands[b]) for b in want_hands}
    err["head"] = SM.check(rig, "head", 1, N, want_head)
    change = {b: max(math.degrees(Quaternion(a).rotation_difference(Quaternion(w)).angle) for a, w in
                     zip(hands_before[b], want_hands[b])) for b in want_hands}
    after = V.validate_range(rig, 1, N, "walk with secondary")
    rep = dict(action=action, frames=N, layer_error_deg={k: round(v, 3) for k, v in err.items()},
               max_change_deg={k: round(v, 1) for k, v in change.items()},
               pops_before=before["pops"]["count"], pops_after=after["pops"]["count"],
               slip_before=before["foot_slip"]["max_cm"], slip_after=after["foot_slip"]["max_cm"],
               pass_=all(v < 0.5 for v in err.values()) and after["pops"]["count"] <= before["pops"]["count"])
    out = PC.path("10_QUALITY_CONTROL", "FINAL_REVIEW", f"{key}_secondary_motion.json")
    with open(out, "w") as fh:
        json.dump(rep, fh, indent=1)
    print("[UHAS] secondary motion test", json.dumps(rep))


if __name__ == "__main__":
    main(next((a for a in sys.argv[1:] if a.isupper()), "ARIAN"))
