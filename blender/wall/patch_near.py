"""«دیوار» POV: Kazemi climbs through the hole right in front of me and the camera passes through his head
(frames 632-639). Pulling the camera back showed my own hood, so instead Kazemi is hidden for those frames
(he is already through the hole; a third of a second). wall.blend (look patch) -> wall_fix2.blend."""
import bpy, os
HERE = os.path.dirname(os.path.abspath(__file__))
bpy.ops.wm.open_mainfile(filepath=os.path.join(HERE, "wall_fix1.blend"))
sc = bpy.context.scene
kz = bpy.data.objects["Kazemi_rig"]
objs = [o for o in bpy.data.objects if o.parent == kz or (o.parent and o.parent.parent == kz)]
A, B = 632, 639
for o in objs:
    for f, h in ((A - 1, False), (A, True), (B, True), (B + 1, False)):
        o.hide_render = h
        o.keyframe_insert("hide_render", frame=f)
print("HIDDEN", [o.name for o in objs])
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(HERE, "wall_fix2.blend"))
