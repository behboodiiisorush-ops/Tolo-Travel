#!/bin/bash
# Rebuild every .blend in BLENDER_ANIMATION from scratch (~10 min). Order matters: the shorts append the
# environments and effects, so those are built first. Previews land in _preview/ (git-ignored).
set -e
cd "$(dirname "$0")"
B=../../cast/bpy.sh
$B build_characters.py
$B build_sets.py
$B build_animations.py
$B build_shorts.py
echo "all built"
