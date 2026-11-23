#!/bin/bash
# One-time setup for the realistic cast (run from anywhere; idempotent).
#  - Python venv with the bpy module (Blender as a library)
#  - MPFB 2 (MakeHuman for Blender) from extensions.blender.org
#  - MakeHuman asset packs (skins, hair, clothes...) from files.makehumancommunity.org
# Everything lands in blender/cast/vendor/ (git-ignored, ~1.4 GB).
# Needs network access to extensions.blender.org and files.makehumancommunity.org.
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
V="$HERE/vendor"
mkdir -p "$V/dl" "$V/assets" "$V/bconf" "$V/ext/user_default"

if [ ! -x "$V/venv/bin/python" ]; then
  python3 -m venv "$V/venv"
  "$V/venv/bin/pip" install -q bpy==5.3.0 numpy
fi

MPFB_URL='https://extensions.blender.org/download/sha256:c075b3e9b94b8e5556a5f03f4653602d02ea306de08126e8f55ed6dee28a2dad/add-on-mpfb-v2.0.18.zip?repository=%2Fapi%2Fv1%2Fextensions%2F&blender_version_min=4.2.0'
if [ ! -d "$V/ext/user_default/mpfb" ]; then
  curl -sL -o "$V/dl/mpfb.zip" "$MPFB_URL"
  mkdir -p "$V/ext/user_default/mpfb"
  (cd "$V/ext/user_default/mpfb" && unzip -qo "$V/dl/mpfb.zip")
fi

PACKS="makehuman_system_assets/makehuman_system_assets_cc0 shirts01/shirts01_cc0 pants01/pants01_cc0
shoes01/shoes01_cc0 glasses01/glasses01_cc0 hats01/hats01_cc0 hats02/hats02_cc0 equipment01/equipment01_cc0
gloves01/gloves01_cc0 dress01/dress01_cc0 hair02/hair02_ccby hair03/hair03_ccby hats04/hats04_cc-by
shirts02/shirts02_ccby shirts03/shirts03_ccby pants02/pants02_ccby shoes02/shoes02_ccby"
for p in $PACKS; do
  f="$V/dl/$(basename "$p").zip"
  [ -s "$f" ] || curl -sL -o "$f" "https://files.makehumancommunity.org/asset_packs/$p.zip"
  (cd "$V/assets" && unzip -qo "$f")
done

U="$V/ext/.user/user_default/mpfb/data"
mkdir -p "$U"
for d in "$V"/assets/*; do ln -sfn "$d" "$U/$(basename "$d")"; done
echo "cast ready: $V"
