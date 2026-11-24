#!/usr/bin/env bash
# Render «واگن آخر ۲» and build the videos. Re-running resumes (existing frames are skipped).
# BLENDER_PY: a python with bpy (default: the cast venv).
set -euo pipefail
cd "$(dirname "$0")"
PY="${BLENDER_PY:-../cast/vendor/venv/bin/python}"
"$PY" part_door.py --render --range 1 1248     # on twos: every second frame
python3 sfx.py
python3 post.py
