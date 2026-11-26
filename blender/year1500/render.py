"""Render frames of year1500.blend: ../cast/bpy.sh render.py a-b  -> frames/f_XXXX.png (skips frames on disk)."""
import bpy, sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from captions import FLASHBACK, WAKE  # noqa: E402
bpy.ops.wm.open_mainfile(filepath=os.path.join(HERE, "year1500.blend"))
sc = bpy.context.scene
sc.eevee.taa_render_samples = int(os.environ.get("SAMPLES", "6"))   # soft stylized look: 6 keeps the AO calm
a, b = [int(v) for v in sys.argv[-1].split("-")]
os.makedirs(os.path.join(HERE, "frames"), exist_ok=True)
# Sun shadows cost 5-7x on this CPU renderer in the POV shots and barely show in the flat cel look:
# keep them only for the drone shots; the screen glow never casts shadows.
SUN = bpy.data.objects["Sun"].data
for o in sc.objects:
    if o.type == "LIGHT" and o.data.type != "SUN":
        o.data.use_shadow = False
MARKS = sorted((m.frame, m.camera.name) for m in sc.timeline_markers if m.camera)


def cam_at(f):
    name = MARKS[0][1]
    for fr, n in MARKS:
        if fr <= f:
            name = n
    return name


for f in range(a, b + 1):
    out = os.path.join(HERE, "frames", f"f_{f:04d}.png")
    if os.path.exists(out) and os.path.getsize(out) > 0:
        continue
    if FLASHBACK[1] * 24 < f <= WAKE * 24:   # the black between the fall and waking up (post draws it)
        continue
    sc.frame_set(f)
    if os.environ.get("LOOK") == "comic":
        sc.eevee.use_shadows = cam_at(f) != "POV"   # also the world light's own sun shadow
    sc.render.filepath = out
    bpy.ops.render.render(write_still=True)
