"""Group picture of every built studio character: appends each CHAR_###/Rig.blend character collection, stands
them in a row (rest pose, slight smile) -> 01_CHARACTER_LIBRARY/lineup.png
    blender/cast/bpy.sh ANIMATION_STUDIO/01_CHARACTER_LIBRARY/lineup.py
"""
import bpy, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "00_CORE_SYSTEM"))
import project_config as PC  # noqa: E402
import generate_rig as G  # noqa: E402
import render_shorts as RS  # noqa: E402
import setup_face as F  # noqa: E402

bpy.ops.wm.read_factory_settings(use_empty=True)
G.enable_addons()
sc = bpy.context.scene
keys = [k for k in PC.CHARACTERS if os.path.exists(PC.char_dir(k, "Rig.blend"))]
gap = 0.85
for i, k in enumerate(keys):
    with bpy.data.libraries.load(PC.char_dir(k, "Rig.blend"), link=False) as (src, dst):
        dst.collections = [k]
    c = dst.collections[0]
    sc.collection.children.link(c)
    for sub in c.children:
        if sub.name.endswith("_HELPERS"):
            sub.hide_render = True
    rig = bpy.data.objects[k + "_RIG"]
    if rig.animation_data:
        rig.animation_data.action = None
        for t in rig.animation_data.nla_tracks:
            t.mute = True
    for pb in rig.pose.bones:
        pb.location = (0, 0, 0)
        pb.rotation_quaternion = (1, 0, 0, 0)
        pb.rotation_euler = (0, 0, 0)
    rig.location = ((i - (len(keys) - 1) / 2) * gap, 0, 0)
    F.pose(rig, smile=0.4)
RS.stage(sc)
cam = RS.camera(sc, lens=40)
RS.aim(cam, (0, -gap * len(keys) * 1.05 - 1.2, 1.0), (0, 0, 0.9))
RS.setup_engine(sc, "CYCLES", (1800, 900), samples=12)
sc.render.filepath = os.path.join(HERE, "lineup.png")
bpy.ops.render.render(write_still=True)
print("[UHAS] lineup", keys)
