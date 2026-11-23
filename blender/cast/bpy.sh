#!/bin/bash
# Run a Blender python script with the cast (MPFB + assets) available:
#   blender/cast/bpy.sh some_scene.py --still 100
C="$(cd "$(dirname "$0")" && pwd)"
V="$C/vendor"
export MPFB_ASSETS="$V/assets" BLENDER_USER_EXTENSIONS="$V/ext" BLENDER_USER_CONFIG="$V/bconf"
export PYTHONPATH="$C${PYTHONPATH:+:$PYTHONPATH}"
exec "$V/venv/bin/python" "$@"
