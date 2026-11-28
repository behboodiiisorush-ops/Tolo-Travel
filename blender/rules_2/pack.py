"""Pack rules_2.blend with every texture into one file for the render workers: ../cast/bpy.sh pack.py OUT.blend"""
import bpy, sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
bpy.ops.wm.open_mainfile(filepath=os.path.join(HERE, "rules_2.blend"))
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=sys.argv[-1], compress=True)
print("PACKED", sys.argv[-1])
