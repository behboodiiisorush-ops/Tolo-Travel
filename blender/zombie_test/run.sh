#!/bin/bash
# usage: ./run.sh scene.py --still 40,120   (paths are this machine's scratchpad setup)
S=/tmp/claude-0/-home-user-Tolo-Travel/d4d58d50-fa41-5eeb-9945-b51a3decd315/scratchpad
cd "$(dirname "$0")"
MPFB_ASSETS=$S/mh/assets BLENDER_USER_EXTENSIONS=$S/mh/ext BLENDER_USER_CONFIG=$S/mh/bconf exec $S/bvenv/bin/python "$@"
