#!/usr/bin/env bash
# Render «زنگ آخر» and build the final video (re-running resumes: existing frames are skipped).
set -euo pipefail
cd "$(dirname "$0")"
run() { if [ -n "${BLENDER_PY:-}" ]; then "$BLENDER_PY" "$@"; else blender -b --python "$1" -- "${@:2}"; fi; }
python3 make_textures.py
run scene.py --save --render
python3 sfx.py
python3 post.py
