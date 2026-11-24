#!/usr/bin/env bash
# Render «واگن آخر ۲» and build the final videos. Re-running resumes: frames that already
# exist are skipped.  BLENDER_PY: a python with bpy (default: the cast venv).
set -euo pipefail
cd "$(dirname "$0")"
PY="${BLENDER_PY:-../cast/vendor/venv/bin/python}"
python3 make_textures.py
"$PY" part_wagon.py --render --range 1 648        # 0-27 s: goodbye at the border, the ride back
"$PY" part_field.py --render --range 649 1344     # 27-56 s: the lone wagon, grandma
"$PY" part_wagon.py --render --range 1345 1584    # 56-66 s: towards the border again
python3 sfx.py
python3 post.py
