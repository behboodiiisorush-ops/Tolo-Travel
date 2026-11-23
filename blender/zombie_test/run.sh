#!/bin/bash
# usage: ./run.sh scene.py --still 40,120
cd "$(dirname "$0")"
exec ../cast/bpy.sh "$@"
