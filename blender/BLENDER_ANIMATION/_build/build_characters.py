"""CHARACTERS/Main_Character.blend («من») and CHARACTERS/Secondary_Character.blend («مهسا»):
the puppet in its own collection, breathing idle (10 s loop) with blinks, on a turntable-style stage + camera."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib  # noqa: E402
import bpy, math  # noqa: E402

ONLY = sys.argv[sys.argv.index("--only") + 1] if "--only" in sys.argv else None
for fname, key, fa in (("Main_Character", "me", "من"), ("Secondary_Character", "mahsa", "مهسا")):
    if ONLY and ONLY != key:
        continue
    sc = lib.reset()
    import mocap
    import puppets as PP
    ch = lib.character(key, name=fname)
    cl = lib.clip("breathing_idle")
    n = mocap.apply(ch, cl, start=1, length=240, offset=(0, 0, 0), facing=180, in_place=True, loop=True)
    bpy.data.objects.remove(cl.arm)
    lib.faces(ch, 1, 240, lambda t: dict(smile=0.35, look_at=(0.3 * math.sin(t * 0.8), -3.0, 1.45)))
    sc.frame_set(1)
    PP.finish(ch, smile=0)
    c = lib.coll(fname)
    lib.into(c, lib.char_objects(ch))
    st = lib.coll("Stage")
    floor = lib.root("Stage", st)
    lib.CY(floor, (0, 0, -0.03), 1.2, 0.06, lib.M("pillow"), "disc", verts=48)
    lib.B(floor, (0, 3, 3), (20, 0.1, 6), lib.M("house2"), "backdrop", line=0)
    lib.B(floor, (0, 0, -0.07), (20, 20, 0.02), lib.M("walk"), "floor", line=0)
    sc.frame_start, sc.frame_end = 1, 240
    lib.look(sc, res=(1080, 1080))
    lib.camera(sc, (1.1, -3.4, 1.25), (0, 0, 0.95), lens=42)
    sc["character"] = fa
    lib.save(f"CHARACTERS/{fname}.blend", still=[1])
