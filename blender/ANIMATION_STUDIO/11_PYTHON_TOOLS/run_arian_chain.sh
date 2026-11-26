#!/bin/bash
# Arian end to end (library, QC, test renders, split files, demo episode). One Blender at a time.
cd "$(dirname "$0")/.."
B=../cast/bpy.sh
L=10_QUALITY_CONTROL/logs
$B 11_PYTHON_TOOLS/create_character.py ARIAN --stage library,qc > $L/ARIAN_pipeline.log 2>&1
$B 11_PYTHON_TOOLS/create_character.py ARIAN --stage tests > $L/ARIAN_tests.log 2>&1
$B 11_PYTHON_TOOLS/create_character.py ARIAN --stage split > $L/ARIAN_split.log 2>&1
$B 12_EPISODES/EP_001/build_ep001.py --render > $L/EP_001.log 2>&1
echo CHAIN DONE >> $L/EP_001.log
