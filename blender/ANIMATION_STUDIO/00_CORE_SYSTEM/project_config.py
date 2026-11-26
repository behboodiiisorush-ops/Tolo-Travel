"""Project-wide settings for the Universal Human Animation System (UHAS).

Everything else imports paths and constants from here, so the studio folder can move without code changes.
Run any tool through the cast's Blender runner:   blender/cast/bpy.sh ANIMATION_STUDIO/11_PYTHON_TOOLS/<tool>.py
"""
import os
import sys

STUDIO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # .../blender/ANIMATION_STUDIO
BLENDER_DIR = os.path.dirname(STUDIO)                                  # .../blender
MOCAP_DIR = os.path.join(BLENDER_DIR, "mocap")                         # Mixamo FBX clips (see CLIPS.md)
FONTS_DIR = os.path.join(BLENDER_DIR, "fonts")

for _p in (os.path.join(STUDIO, "00_CORE_SYSTEM"), os.path.join(STUDIO, "11_PYTHON_TOOLS"),
           os.path.join(BLENDER_DIR, "cast"), os.path.join(BLENDER_DIR, "studio"), os.path.join(BLENDER_DIR, "puppets")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

FPS = 24
SHORTS_RES = (1080, 1920)          # 9:16
PREVIEW_PERCENT = 50               # tests render at 540x960
ENGINE = "CYCLES"                  # the approved puppet look; "BLENDER_EEVEE" also supported by render_shorts.py
CYCLES_SAMPLES = 10


def path(*parts):
    return os.path.join(STUDIO, *parts)


# ------------------------------------------------------------------ characters
# key: folder, puppet key in blender/puppets (look), status. New people get a puppet entry in EXTRA_PUPPETS.
CHARACTERS = {
    "ARIAN":  dict(folder="CHAR_001_ARIAN", puppet="arian", fa="آرین"),
    "DANIEL": dict(folder="CHAR_002_DANIEL", puppet="daniel", fa="دانیال"),
    "LINA":   dict(folder="CHAR_003_LINA", puppet="lina", fa="لینا"),
    "FATHER": dict(folder="CHAR_004_FATHER", puppet="father", fa="بابا"),
    "MOTHER": dict(folder="CHAR_005_MOTHER", puppet="mom", fa="مامان"),
    "SHADOW": dict(folder="CHAR_006_SHADOW", puppet="shadow", fa="سایه"),
}

# puppet designs for the people that are not in blender/puppets yet (same format as puppets.CAST)
EXTRA_PUPPETS = {
    "daniel": dict(fa="دانیال", gender=1.0, age=0.38, height=0.5, weight=0.5, skin=(0.9, 0.7, 0.55),
                   hair=("messy", (0.3, 0.18, 0.1)),
                   clothes={"elvs_crude_t-shirt_male": (0.95, 0.35, 0.3), "punkduck_male_classic_jeans": (0.25, 0.25, 0.3),
                            "culturalibre_sneakers": (0.95, 0.95, 0.92)}),
    "lina":   dict(fa="لینا", gender=0.0, age=0.36, height=0.42, weight=0.4, skin=(0.93, 0.75, 0.62),
                   hair=("bun", (0.35, 0.2, 0.1)),
                   clothes={"mindfront_knitted_sweater_02": (0.95, 0.75, 0.25), "toigo_wool_pants": (0.3, 0.35, 0.6),
                            "elvs_flatshoe_plain1": (0.2, 0.5, 0.35)}),
    "father": dict(fa="بابا", gender=1.0, age=0.7, height=0.62, weight=0.6, skin=(0.88, 0.66, 0.5),
                   hair=("short", (0.2, 0.17, 0.15)), moustache=True,
                   clothes={"elvs_male_shirt_untucked_bd1": (0.4, 0.55, 0.75), "punkduck_male_classic_jeans": (0.22, 0.22, 0.25),
                            "culturalibre_male_boots": (0.3, 0.2, 0.12)}),
    "shadow": dict(fa="سایه", gender=1.0, age=0.55, height=0.65, weight=0.45, skin=(0.12, 0.12, 0.16),
                   hair=("short", (0.05, 0.05, 0.07)),
                   clothes={"elvs_hooded_sweat_jacket1": (0.08, 0.08, 0.1), "punkduck_male_classic_jeans": (0.06, 0.06, 0.08),
                            "culturalibre_male_boots": (0.05, 0.05, 0.05)}),
}


def char_dir(key, *parts):
    return path("01_CHARACTER_LIBRARY", CHARACTERS[key]["folder"], *parts)
