"""ANIMATIONS/Walk_Cycle.blend, Run_Cycle.blend, Reactions.blend — «من» driven by Mixamo clips, with face keys.
Walk and run are in-place loops (frames 1..48 loop seamlessly); Reactions is a row of six reactions, each one
named by a timeline marker (scared, yes, no, forget it, thinking, wait)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib  # noqa: E402
import bpy, math  # noqa: E402

ONLY = sys.argv[sys.argv.index("--only") + 1].split(",") if "--only" in sys.argv else None


def stage(sc, frames, cam_loc, cam_to, res=(1080, 1080)):
    st = lib.coll("Stage")
    r = lib.root("Stage", st)
    lib.B(r, (0, 0, -0.05), (30, 30, 0.1), lib.M("walk"), "floor", line=0)
    lib.B(r, (0, 4, 3), (30, 0.1, 6), lib.M("house2"), "backdrop", line=0)
    for i in range(-6, 7):                                    # floor marks: you can see the feet stay in place
        lib.B(r, (i * 0.5, 0, 0.002), (0.02, 0.6, 0.004), lib.M("curb"), "mark", line=0)
    sc.frame_start, sc.frame_end = frames
    lib.look(sc, res=res)
    lib.camera(sc, cam_loc, cam_to, lens=40)


def cycle(fname, clipname, n, face, speed=1.0):
    import mocap, puppets as PP
    sc = lib.reset()
    ch = lib.character("me", name=fname.split("_")[0])
    cl = lib.clip(clipname)
    mocap.apply(ch, cl, start=1, length=n, offset=(0, 0, 0), facing=90, in_place=True, loop=True, speed=speed)
    bpy.data.objects.remove(cl.arm)
    lib.faces(ch, 1, n, face)
    sc.frame_set(1)
    PP.finish(ch, smile=0)
    lib.into(lib.coll(fname), lib.char_objects(ch))
    # make the loop explicit: cyclic F-curves (play/loop it past frame n in any shot)
    act = ch.rig.animation_data.action if ch.rig.animation_data else None
    stage(sc, (1, n), (0.6, -4.2, 1.1), (0, 0, 0.9))
    sc["loop"] = f"1-{n}"
    return ch, act


if not ONLY or "walk" in ONLY:
    cycle("Walk_Cycle", "walking", 48, lambda t: dict(smile=0.4, look_at=(-3, 0, 1.45)))
    lib.save("ANIMATIONS/Walk_Cycle.blend", still=[1, 7, 13, 19])

if not ONLY or "run" in ONLY:
    cycle("Run_Cycle", "goofy_running", 43, lambda t: dict(smile=0.7, look_at=(-3, 0, 1.45)))
    lib.save("ANIMATIONS/Run_Cycle.blend", still=[1, 4, 8, 11])

if not ONLY or "reactions" in ONLY:
    import mocap, puppets as PP
    sc = lib.reset()
    ch = lib.character("me", name="Reactions")
    # (clip, seconds into it, length s, marker, face)
    R = [("terrified", 9.0, 3.0, "scared", dict(worry=1.8)),
         ("head_nod_yes", 0.0, 2.6, "yes", dict(smile=0.8)),
         ("shaking_head_no", 0.0, 1.8, "no", dict(worry=0.6)),
         ("dismissing_gesture", 0.0, 2.2, "forget it", dict(brows="angry")),
         ("thinking", 0.0, 4.2, "thinking", dict(brows="confused")),
         ("hands_forward_gesture", 0.0, 3.1, "wait", dict(worry=0.8, talking=True))]
    f = 1
    spans = []
    for name, at, ln, mk, face in R:
        cl = lib.clip(name)
        n = int(ln * lib.FPS)
        mocap.apply(ch, cl, start=f, length=n, offset=(0, 0, 0), facing=180, in_place=True, src_from=at, blend=8)
        bpy.data.objects.remove(cl.arm)
        sc.timeline_markers.new(mk, frame=f)
        spans.append((f, f + n - 1, face))
        f += n

    def face(t):
        fr = int(t * lib.FPS) + 1
        for a, b, fc in spans:
            if a <= fr <= b:
                d = dict(fc)
                d["look_at"] = (0.0, -3.0, 1.45)
                return d
        return {}
    lib.faces(ch, 1, f - 1, face)
    sc.frame_set(1)
    PP.finish(ch, smile=0)
    lib.into(lib.coll("Reactions"), lib.char_objects(ch))
    stage(sc, (1, f - 1), (0.5, -3.6, 1.3), (0, 0, 1.0))
    lib.save("ANIMATIONS/Reactions.blend", still=[a + (b - a) // 2 for a, b, _ in spans])
