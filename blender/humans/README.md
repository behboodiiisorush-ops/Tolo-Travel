# Realistic humans (MakeHuman / MPFB)

`test_humans.py` builds characters with the MPFB 2 extension (CC0 MakeHuman assets).

Setup (kept out of git, ~450 MB):
- MPFB from extensions.blender.org, unpacked to `<ext>/user_default/mpfb`
- Asset packs from files.makehumancommunity.org (makehuman_system_assets, shirts01, pants01, shoes01), linked into `<ext>/.user/user_default/mpfb/data`

Run: `BLENDER_USER_EXTENSIONS=<ext> BLENDER_USER_CONFIG=<conf> python test_humans.py <out_dir>`
