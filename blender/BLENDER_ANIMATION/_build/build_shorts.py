"""SHORTS/Episode_01.blend and Episode_02.blend — vertical 1080x1920 shorts that pull their sets from
ENVIRONMENTS/*.blend and effects from ASSETS/Effects (appended copies), with the puppets driven by Mixamo clips.
Render output goes to SHORTS/Renders/ (relative path, so it works wherever the folder lives).

  Episode 01 «صبح» (bedroom, 7 s): «من» walks in from the door, stops by the rug, turns to us and thinks.
  Episode 02 «باران» (street, 7 s): «من» and «مهسا» walk along the sidewalk in the rain; Mahsa stops him
  («صبر کن!») and he looks around, nervous.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib  # noqa: E402
import bpy, math  # noqa: E402
from mathutils import Vector  # noqa: E402

ONLY = sys.argv[sys.argv.index("--only") + 1].split(",") if "--only" in sys.argv else None
FPS = lib.FPS


def ease(u):
    u = min(1.0, max(0.0, u))
    return u * u * (3 - 2 * u)


def vertical(sc, out):
    lib.look(sc, res=(1080, 1920))
    sc.render.resolution_percentage = 50          # preview size; set 100 for the final render
    sc.render.filepath = "//Renders/" + out + "_"
    sc.render.image_settings.file_format = "PNG"


def walk_then(ch, cl_walk, n_walk, p0, p1, fac_walk, cl2, n2, fac2, src2=0.0, turn=12):
    """Walk in a straight line p0 -> p1 for n_walk frames, then play clip 2 in place, turning fac_walk -> fac2."""
    import mocap
    mocap.apply(ch, cl_walk, start=1, length=n_walk, in_place=True, loop=True,
                place=lambda j: (tuple(Vector(p0).lerp(Vector(p1), j / (n_walk - 1))), fac_walk))
    mocap.apply(ch, cl2, start=n_walk + 1, length=n2, in_place=True, src_from=src2, blend=8,
                place=lambda j: (p1, fac_walk + (fac2 - fac_walk) * ease(j / turn)))


if not ONLY or "ep1" in ONLY:
    import puppets as PP
    sc = lib.reset()
    lib.append(lib.path("ENVIRONMENTS", "Bedroom.blend"), "Bedroom")
    ch = lib.character("me", name="Me")
    walk, think = lib.clip("walking"), lib.clip("thinking")
    NW, NT = 72, 96
    walk_then(ch, walk, NW, (-1.9, 0.45, 0), (-0.05, 0.25, 0), -96, think, NT, -195)
    for c in (walk, think):
        bpy.data.objects.remove(c.arm)
    N = NW + NT
    cam_loc = Vector((0.15, -1.95, 1.45))
    lib.faces(ch, 1, N, lambda t: dict(smile=0.35, look_at=(2.0, -0.4, 1.4)) if t < NW / FPS - 0.3 else
              dict(brows="confused", look_at=tuple(cam_loc)))
    sc.frame_set(1)
    PP.finish(ch, smile=0)
    lib.into(lib.coll("Characters"), lib.char_objects(ch))
    sc.frame_start, sc.frame_end = 1, N
    vertical(sc, "Episode_01")
    li = bpy.data.objects.new("Room light", bpy.data.lights.new("Room light", "AREA"))
    li.data.energy, li.data.size = 70, 2.5
    li.location = (0, 0, 2.6)
    sc.collection.objects.link(li)
    lib.camera(sc, tuple(cam_loc), (0.0, 0.4, 0.95), lens=18)
    sc.timeline_markers.new("walks in", frame=1)
    sc.timeline_markers.new("thinks", frame=NW + 1)
    sc["title"] = "صبح"
    lib.save("SHORTS/Episode_01.blend", still=[20, 60, 110, 160])

if not ONLY or "ep2" in ONLY:
    import mocap, puppets as PP
    sc = lib.reset()
    lib.append(lib.path("ENVIRONMENTS", "Street.blend"), "Street")
    rain = lib.append(lib.path("ASSETS", "Effects", "Effects.blend"), "FX Rain")
    me, ma = lib.character("me", name="Me"), lib.character("mahsa", name="Mahsa")
    walk, nerv, wait = lib.clip("walking"), lib.clip("nervously_look_around"), lib.clip("hands_forward_gesture")
    NW, N2 = 96, 72
    Y_ME, Y_MA = -4.75, -5.35
    walk_then(me, walk, NW, (-3.0, Y_ME, 0.14), (1.6, Y_ME, 0.14), -90, nerv, N2, -150, src2=0.5)
    walk_then(ma, walk, NW - 6, (-3.3, Y_MA, 0.14), (1.0, Y_MA, 0.14), -90, wait, N2 + 6, -40, turn=10)
    for c in (walk, nerv, wait):
        bpy.data.objects.remove(c.arm)
    N = NW + N2
    hm = lambda: (me.rig.matrix_world @ me.rig.pose.bones["head"].head)     # noqa: E731
    lib.faces(me, 1, N, lambda t: dict(smile=0.4, look_at=(6, Y_ME, 1.4)) if t < NW / FPS else
              dict(worry=1.4, look_at=(1.6 + 3 * math.sin(t * 2.0), -9, 1.5)))
    lib.faces(ma, 1, N, lambda t: dict(smile=0.3, look_at=(6, Y_MA, 1.4)) if t < (NW - 6) / FPS else
              dict(worry=0.9, talking=t < (NW - 6) / FPS + 1.2, look_at=tuple(hm())))
    sc.frame_set(1)
    for ch in (me, ma):
        PP.finish(ch, smile=0)
    lib.into(lib.coll("Characters"), lib.char_objects(me) + lib.char_objects(ma))
    for o in rain.objects:                       # the rain box rides along with the two of them
        o.location = (-0.8, -5.0, 0.1)
        o.scale = (1.6, 0.55, 0.9)                # (only around them: no huge streaks at the lens)
        o.keyframe_insert("location", frame=1)
        o.location.x = 1.6
        o.keyframe_insert("location", frame=NW)
    sc.frame_start, sc.frame_end = 1, N
    vertical(sc, "Episode_02")
    sc.world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.25, 0.32, 0.42, 1)   # grey rain sky
    bpy.data.objects["Sun"].data.energy = 1.6
    cam = lib.camera(sc, (-3.0, -8.4, 1.35), (-3.0, -5.0, 1.0), lens=26)
    for f, x in ((1, -3.0), (NW, 1.3), (N, 1.35)):         # follow them, then hold
        cam.location.x = x
        cam.keyframe_insert("location", index=0, frame=f)
    sc.timeline_markers.new("walk in the rain", frame=1)
    sc.timeline_markers.new("wait!", frame=NW - 5)
    sc["title"] = "باران"
    lib.save("SHORTS/Episode_02.blend", still=[30, 85, 115, 160])
