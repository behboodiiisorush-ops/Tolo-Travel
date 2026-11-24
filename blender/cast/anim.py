"""Procedural body animation for the game_engine rig.

pose_spec(st) turns a small "state" dict into bone rotations (armature axes, degrees).
Conventions found by testing the MPFB game_engine rig (character facing -Y at rest):
  legs/arms forward = -X, knee / elbow bend = +X (calf) / -X (forearm),
  spine & head forward (down) = +X, head turn to own left = +Z,
  upperarm_l down = +Y, upperarm_r down = -Y.
State keys (all optional):
  walk, run       : weight 0..1        phase : radians of the gait cycle
  sit, crouch     : 0..1               hug   : arms around the knees / chest 0..1
  arms            : "rest" | "desk" | "write" | "wave" | "reach" | "push" | "bang" | "shamble" | "phone" | "hold"
  reach           : forward raise of both arms for "reach" (deg), arm_l / arm_r override (fwd, elbow)
  look            : (yaw, pitch) deg, pitch > 0 = up      lean : forward lean deg
  shamble         : 0..1 zombie gait   t : seconds (for idle motion)   seed : int
"""
import math


def _add(spec, bone, **ang):
    d = spec.setdefault(bone, {})
    for k, v in ang.items():
        d[k] = d.get(k, 0.0) + v


def _arm(spec, side, fwd, elbow, down=48.0, twist=0.0, out=0.0):
    s = 1 if side == "l" else -1
    _add(spec, f"upperarm_{side}", y=s * (down - out), x=-fwd, z=s * twist)
    _add(spec, f"lowerarm_{side}", x=-elbow)


def leg_extent(spec, thigh_len, calf_len):
    """Vertical hip->ankle extent of the lower leg (for keeping a foot on the ground)."""
    best = 0.0
    for side in ("l", "r"):
        a = math.radians(-spec.get(f"thigh_{side}", {}).get("x", 0.0))
        b = math.radians(spec.get(f"calf_{side}", {}).get("x", 0.0))
        best = max(best, thigh_len * math.cos(a) + calf_len * math.cos(a - b))
    return best


def pose_spec(st):
    t = st.get("t", 0.0)
    seed = st.get("seed", 0)
    spec = {}
    walk, run, sham = st.get("walk", 0.0), st.get("run", 0.0), st.get("shamble", 0.0)
    ph = st.get("phase", 0.0)
    s, c = math.sin(ph), math.cos(ph)
    sit, crouch, hug = st.get("sit", 0.0), st.get("crouch", 0.0), st.get("hug", 0.0)

    # ---------------- breathing / idle sway
    br = math.sin(t * 2 * math.pi * st.get("breath", 0.28) + seed)
    _add(spec, "spine_02", x=1.2 * br)
    _add(spec, "spine_03", x=0.8 * br, z=1.5 * math.sin(t * 0.37 + seed))

    # ---------------- legs
    if walk:
        _add(spec, "thigh_l", x=-20 * walk * s)
        _add(spec, "thigh_r", x=20 * walk * s)
        _add(spec, "calf_l", x=4 + 35 * walk * max(0, c))
        _add(spec, "calf_r", x=4 + 35 * walk * max(0, -c))
        _add(spec, "foot_l", x=-10 * walk * max(0, c))
        _add(spec, "foot_r", x=-10 * walk * max(0, -c))
        _add(spec, "pelvis", z=4 * walk * s)
        _add(spec, "spine_01", z=-3 * walk * s)
    if run:
        _add(spec, "thigh_l", x=-(32 * s + 8) * run)
        _add(spec, "thigh_r", x=(32 * s - 8) * run)
        _add(spec, "calf_l", x=(12 + 55 * max(0, c)) * run)
        _add(spec, "calf_r", x=(12 + 55 * max(0, -c)) * run)
        _add(spec, "pelvis", z=7 * run * s)
        _add(spec, "spine_01", x=8 * run, z=-6 * run * s)
        _add(spec, "spine_02", x=5 * run)
    if sham:
        _add(spec, "thigh_l", x=-18 * sham * s)
        _add(spec, "thigh_r", x=10 * sham * s)
        _add(spec, "calf_l", x=(8 + 30 * max(0, c)) * sham)
        _add(spec, "calf_r", x=(14 + 10 * max(0, -c)) * sham)
        _add(spec, "pelvis", z=7 * sham * s, y=4 * sham * c)
        _add(spec, "spine_01", x=10 * sham)
        _add(spec, "spine_02", x=9 * sham, y=5 * sham * s)
        _add(spec, "neck_01", x=-6 * sham, y=9 * sham)
        _add(spec, "head", y=(15 + 4 * math.sin(1.7 * t + seed)) * sham, x=-14 * sham)
    climb = st.get("climb", 0.0)
    if climb:  # running up stairs: swing leg lifted high, stance leg almost straight
        for side, sg in (("l", s), ("r", -s)):
            lift = max(0.0, sg)
            _add(spec, f"thigh_{side}", x=-(8 + 62 * lift) * climb)
            _add(spec, f"calf_{side}", x=(6 + 85 * lift) * climb)
            _add(spec, f"foot_{side}", x=-12 * lift * climb)
        _add(spec, "pelvis", z=6 * climb * s)
        _add(spec, "spine_01", x=6 * climb, z=-5 * climb * s)
    if sit:
        for side in ("l", "r"):
            _add(spec, f"thigh_{side}", x=-88 * sit, z=(4 if side == "l" else -4) * sit)
            _add(spec, f"calf_{side}", x=85 * sit)
    if crouch:
        for side in ("l", "r"):
            _add(spec, f"thigh_{side}", x=-118 * crouch, z=(10 if side == "l" else -10) * crouch)
            _add(spec, f"calf_{side}", x=135 * crouch)
            _add(spec, f"foot_{side}", x=-25 * crouch)
        _add(spec, "spine_01", x=22 * crouch)
        _add(spec, "spine_02", x=12 * crouch)

    # ---------------- arms
    arms = st.get("arms", "rest")
    k = st.get("arms_w", 1.0)
    swing = 14 * walk * s
    if arms == "rest":   # relaxed: arms a little away from the body, soft elbows, palms to the thighs
        sw = 24 * walk * s
        idle = 2.5 * math.sin(t * 1.3 + seed) * (1 - walk)
        _arm(spec, "l", sw + 6 + idle, 14 + 6 * walk + 8 * max(0, sw / 24), down=37, twist=-14)
        _arm(spec, "r", -sw + 6 - idle, 14 + 6 * walk + 8 * max(0, -sw / 24), down=37, twist=-14)
        _add(spec, "clavicle_l", z=2 * math.sin(t * 1.3 + seed))
        _add(spec, "clavicle_r", z=-2 * math.sin(t * 1.3 + seed))
        _add(spec, "hand_l", x=-8, z=4 * math.sin(t * 0.9 + seed))
        _add(spec, "hand_r", x=-8, z=-4 * math.sin(t * 0.9 + seed))
    elif arms == "desk":
        _arm(spec, "l", 18, 72, down=50, twist=-15)
        _arm(spec, "r", 18, 72, down=50, twist=-15)
    elif arms == "write":
        w = 6 * math.sin(t * 5.0)
        _arm(spec, "r", 145 + w, 35, down=40)
        _arm(spec, "l", -2, 12)
    elif arms == "wave":
        _arm(spec, "r", 150, 35 + 28 * math.sin(t * 11), down=25)
        _arm(spec, "l", -2, 12)
    elif arms == "reach":
        r = st.get("reach", 80)
        _arm(spec, "l", r + 5 * math.sin(t * 2 + seed), 12, down=40)
        _arm(spec, "r", r - 8 + 5 * math.sin(t * 2.3 + seed), 16, down=40)
    elif arms == "push":  # hands on a waist-high desk, shoving in pulses
        pulse = 8 * math.sin(t * 7.5 + seed)
        _arm(spec, "l", 42 + pulse, 18 - pulse, down=40)
        _arm(spec, "r", 42 - pulse, 18 + pulse, down=40)
        _add(spec, "spine_01", x=16)
        _add(spec, "spine_02", x=10)
    elif arms == "bang":
        _arm(spec, "l", 110 + 25 * math.sin(t * 9 + seed), 25 + 20 * math.sin(t * 9 + seed), down=30)
        _arm(spec, "r", 110 + 25 * math.sin(t * 9 + seed + 2.5), 25 + 20 * math.sin(t * 9 + seed + 2.5), down=30)
    elif arms == "shamble":
        r = st.get("reach", 72)
        _arm(spec, "l", r + 7 * s, 18, down=45)
        _arm(spec, "r", r - 12 - 7 * s, 10, down=45)
        _add(spec, "hand_l", x=15)
        _add(spec, "hand_r", x=20)
    elif arms == "run":
        _arm(spec, "l", 40 * s + 10, 85)
        _arm(spec, "r", -40 * s + 10, 85)
    elif arms == "hug":
        _arm(spec, "l", 50, 115, down=58)
        _arm(spec, "r", 50, 115, down=58)
    elif arms == "hold":  # one hand held out low (holding someone's hand), other running
        _arm(spec, "r", 30, 10)
        _arm(spec, "l", 40 * s + 10, 85)
    elif arms == "mug":
        _arm(spec, "r", 50, 105, down=50)
        _arm(spec, "l", 25, 40, down=45)
    elif arms == "chalk":
        _arm(spec, "r", 35, 70, down=46)
        _arm(spec, "l", -2, 12)
    tk = st.get("talking")
    g = (1.0 if tk is True else float(tk or 0.0)) if tk else 0.0
    if g and arms in ("rest", "desk", "chalk", "mug"):   # talk with the hands and the head
        w1 = math.sin(t * 4.1 + seed)
        w2 = math.sin(t * 3.3 + 1.3 + seed)
        _add(spec, "upperarm_r", x=-(14 + 10 * w1) * min(1.0, 0.5 + g))
        _add(spec, "lowerarm_r", x=-(28 + 18 * w2) * min(1.0, 0.5 + g))
        _add(spec, "upperarm_l", x=-(6 + 6 * w2) * min(1.0, 0.5 + g))
        _add(spec, "lowerarm_l", x=-(12 + 10 * w1) * min(1.0, 0.5 + g))
        _add(spec, "head", x=4 * math.sin(t * 5.3 + seed) * g, z=5 * math.sin(t * 1.9 + seed) * g)
    for side in ("l", "r"):
        o = st.get(f"arm_{side}")
        if o:
            spec[f"upperarm_{side}"] = {}
            spec[f"lowerarm_{side}"] = {}
            _arm(spec, side, *o)
    if hug and arms != "hug":
        for side in ("l", "r"):
            spec[f"upperarm_{side}"] = {}
            spec[f"lowerarm_{side}"] = {}
        _arm(spec, "l", 50 * hug, 115 * hug, down=48 + 10 * hug)
        _arm(spec, "r", 50 * hug, 115 * hug, down=48 + 10 * hug)
    if k != 1.0:
        for b in ("upperarm_l", "upperarm_r", "lowerarm_l", "lowerarm_r"):
            for a in spec.get(b, {}):
                spec[b][a] *= k

    # ---------------- torso & head
    lean = st.get("lean", 0.0)
    _add(spec, "spine_01", x=0.5 * lean)
    _add(spec, "spine_02", x=0.5 * lean)
    yaw, pitch = st.get("look", (0.0, 0.0))
    _add(spec, "spine_03", z=0.15 * yaw)
    _add(spec, "neck_01", z=0.35 * yaw, x=-0.35 * pitch)
    _add(spec, "head", z=0.5 * yaw, x=-0.65 * pitch)
    if run:
        _add(spec, "head", x=-8 * run)
    return spec


# ================================================================ faces
def blink(t, seed=0):
    period = 3.1 + (seed % 5) * 0.37
    u = (t + seed * 0.71) % period
    return max(0.0, 1 - abs(u - 0.08) / 0.08)


def talk(t, seed=0):
    return 0.12 + 0.28 * abs(math.sin(t * 11.0 + seed) * math.sin(t * 4.3 + 1.7 * seed))


def face(st):
    """Shape key values from a state: worry 0..2, talking bool, zombie 0..1, scream 0..1, smile 0..1."""
    t, seed = st.get("t", 0.0), st.get("seed", 0)
    w = st.get("worry", 0.0)
    fear = min(1.0, max(0.0, w - 0.7))
    z = st.get("zombie", 0.0)
    scream = st.get("scream", 0.0)
    smile = st.get("smile", 0.0)
    b = 0.0 if z else blink(t, seed)
    tk = st.get("talking")
    if isinstance(tk, bool):
        mouth = talk(t, seed) if tk else 0.04 * fear
    else:  # audio level 0..1 of this character's voice at this frame
        mouth = 0.06 + 0.9 * float(tk or 0.0) if tk else 0.04 * fear
    if z:
        g = 0.5 + 0.25 * math.sin(2.3 * t + seed) + 0.15 * math.sin(5.1 * t + seed)
        mouth = max(g, scream)
    else:
        mouth = max(mouth, 0.8 * scream)
    return {
        "eyebrows-left-inner-up": fear * (1 - z), "eyebrows-right-inner-up": fear * (1 - z),
        "eyebrows-left-down": 0.9 * z, "eyebrows-right-down": 0.9 * z,
        "eyebrows-left-up": 0.6 * fear * (1 - z), "eyebrows-right-up": 0.6 * fear * (1 - z),
        "eye-left-opened-up": max(0.7 * fear, 0.5 * z + 0.5 * scream),
        "eye-right-opened-up": max(0.7 * fear, 0.5 * z + 0.5 * scream),
        "eye-left-closure": b, "eye-right-closure": b,
        "mouth-open": mouth, "mouth-depression": 0.35 * fear * (1 - z),
        "mouth-retraction": 0.6 * z + 0.4 * scream * z,
        "mouth-corner-puller": smile,
        "nose-left-elevation": 0.5 * z + 0.5 * scream * z, "nose-right-elevation": 0.5 * z + 0.5 * scream * z,
    }


FACE_KEYS = list(face({}).keys())
