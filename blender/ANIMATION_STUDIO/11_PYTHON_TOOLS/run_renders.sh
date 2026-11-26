#!/bin/bash
cd "$(dirname "$0")/.."
B=../cast/bpy.sh
L=10_QUALITY_CONTROL/logs
$B 12_EPISODES/EP_001/build_ep001.py --render-only > $L/EP_001_render.log 2>&1
rm -f 01_CHARACTER_LIBRARY/CHAR_001_ARIAN/TESTS/EXPRESSIONS*
$B 11_PYTHON_TOOLS/create_character.py ARIAN --stage tests --only expressions > $L/ARIAN_expr.log 2>&1
echo RENDERS DONE >> $L/ARIAN_expr.log
