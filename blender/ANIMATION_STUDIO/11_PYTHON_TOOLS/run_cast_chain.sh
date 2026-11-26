#!/bin/bash
# Build the remaining studio characters one after the other (one Blender at a time).
cd "$(dirname "$0")/.."
B=../cast/bpy.sh
L=10_QUALITY_CONTROL/logs
mkdir -p $L
for K in DANIEL LINA FATHER MOTHER SHADOW; do
  $B 11_PYTHON_TOOLS/create_character.py $K --stage build,library,qc > $L/${K}_pipeline.log 2>&1
  $B 11_PYTHON_TOOLS/create_character.py $K --stage tests --only refs > $L/${K}_tests.log 2>&1
  $B 11_PYTHON_TOOLS/create_character.py $K --stage split > $L/${K}_split.log 2>&1
  echo "$K done $(date +%T)" >> $L/cast_chain.log
done
echo CAST DONE >> $L/cast_chain.log
