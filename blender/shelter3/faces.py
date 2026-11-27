"""Portrait sheet of the series' characters (pcommon puppets) for checking faces:
    ../cast/bpy.sh faces.py out/faces_before.png"""
import bpy, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pov  # noqa: E402
from pcommon import *  # noqa: F401,F403,E402
from mathutils import Vector  # noqa: E402

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
people = [pov.make_lena(), pov.make_mom(), pov.make_guard(), pov.make_rescuer(), pov.make_oldman(), make_extra(1, 0.95)]
for i, p in enumerate(people):
    p.p["root"].location = (i * 1.0, 0, 0)
    p.pose(1, 0.0, Vector((i * 1.0, 0, 0)), facing=0, look=(0, 0), talk=False, worry=0.6)
cam = make_camera(sc)
cam.data.lens = 46
cam.data.sensor_fit = "HORIZONTAL"
cam.location = (2.5, 8.6, 1.42)
cam.rotation_euler = (D(90), 0, D(180))
bpy.ops.object.light_add(type="SUN", rotation=(D(50), D(10), D(200)))
bpy.context.object.data.energy = 1.2
bpy.ops.object.light_add(type="AREA", location=(1.5, 4, 2.5))
a = bpy.context.object
a.data.energy = 120
a.data.size = 3
a.rotation_euler = (D(70), 0, D(160))
setup_render(sc, samples=24, res=(2400, 560), sky=(0.75, 0.75, 0.78), sky_strength=1.0)
sc.frame_set(1)
sc.render.filepath = os.path.join(HERE, sys.argv[-1])
bpy.ops.render.render(write_still=True)
