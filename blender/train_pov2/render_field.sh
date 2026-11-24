#!/usr/bin/env bash
cd "$(dirname "$0")"
../cast/vendor/venv/bin/python part_field.py --render --range 649 1344
echo FIELD_DONE
