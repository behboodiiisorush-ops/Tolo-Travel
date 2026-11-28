"""Story beat times of «واگن آخر ۷» (seconds) without bpy — the same formulas as part7.py, for el_mix.py / post.py."""
from captions import KEY_OF as T


def at(key, k=0):
    return T[key][k]


LAND1 = at("n1") - 0.3
DOOR_T = at("mom3") - 1.4
DEAD_T = at("mom3", 1) + 0.25
LIGHT_OFF = DEAD_T + 0.6
WIND0 = at("lena4") - 2.2
KNOCK0 = at("lena5") - 3.4
KNOCKS = [KNOCK0 + d for d in (0.4, 1.4, 2.4)]
CUT2 = at("rahim2") - 1.6
TIE0, TIE1 = at("rahim3") + 0.2, at("rahim4") - 0.1
WALK0 = at("n6") - 2.4
PLANK_T = at("lena8") - 1.8
WALK1 = at("lena9") - 3.4
HORN_T = at("lena9") - 3.2
SHADOW0 = at("lena9") - 2.1
BLACK_T = at("n9", 1) + 0.4
