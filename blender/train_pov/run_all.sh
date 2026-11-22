#!/usr/bin/env bash
# Render the whole film and build the final video. Re-running resumes: frames
# that already exist are skipped.  BLENDER_PY can point at a python with bpy,
# otherwise "blender -b --python" is used.
set -euo pipefail
cd "$(dirname "$0")"
run() {
  if [ -n "${BLENDER_PY:-}" ]; then "$BLENDER_PY" "$@"; else blender -b --python "$1" -- "${@:2}"; fi
}
python3 make_textures.py
run part_station.py --save --render
run part_wagon.py --save --render
python3 post.py
