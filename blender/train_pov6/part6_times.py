"""Story beat times of «واگن آخر ۶» (seconds), shared by part6.py (scene) and el_mix.py (sound)."""
from captions import END, KEY_OF

FPS = 24
GROUND = -1.3
T = KEY_OF


def at(key, k=0):
    return T[key][k]


def ease(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def seg(t, a, b):
    return ease((t - a) / (b - a))


# ---------------------------------------------------------------- story beats (seconds)
CURTAIN0 = at("rahim1", 1) + 0.1           # curtains pulled shut
OPEN0 = at("me1") - 0.3                    # I pull our curtain aside
BLINKS = [at("me1", 1) + 0.35 + 0.8 * k for k in range(3)]
SEARCH_T = BLINKS[-1] + 0.85               # the searchlight finds us
DESC0, DESC1 = at("rahim3") + 0.2, at("rahim3", 1) + 0.6      # helicopter comes down beside the window
LOWER0, LOWER1 = at("rahim3") + 1.0, at("me2") - 2.3          # the bag comes down the rope
GRAB_T = at("me2") - 1.4                   # I grab it
TABLE_T = at("me2") - 0.3                  # on the table
LEAVE_T = at("me2", 1) + 0.6               # the helicopter leaves
RADIO_T = at("me2", 1) + 0.2               # the radio out of the bag, in my hand
RUN0 = at("rahim4", 1) - 0.9               # Rahim runs to the front
BRAKE0, BRAKE1 = at("rahim4", 1) + 0.9, at("rahim4", 1) + 5.6
DEAD_T = at("mom3", 1) + 0.4               # the radio goes dead


def speed(t):
    return 9.0 * (1 - seg(t, BRAKE0, BRAKE1))


_S = [0.0]
for _f in range(1, int(END * FPS) + 4):
    _S.append(_S[-1] + speed((_f - 1) / FPS) / FPS)


def travelled(t):
    return _S[max(0, min(len(_S) - 1, int(round(t * FPS))))]


S_STOP = travelled(END)
BR0 = S_STOP + 24.5          # bridge abutment (outside coordinates); the locomotive stops just before it
GAP0, GAP1 = BR0 + 5, BR0 + 35
BR1 = BR0 + 140              # the far bank
RIVER_Z = GROUND - 5
