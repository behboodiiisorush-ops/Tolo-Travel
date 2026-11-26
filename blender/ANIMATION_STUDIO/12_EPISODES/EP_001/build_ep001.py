"""EP_001 — demonstration short (9:16): Arian on the street.
idle -> starts walking -> walk -> run -> walk -> stops with a "wait" gesture and talks (lip sync from a recording).
Everything comes from the reusable library through the NLA (BODY_A/B, ROOT, FOOTLOCK, FACE); then the episode is
validated (transitions included) and rendered.

    blender/cast/bpy.sh ANIMATION_STUDIO/12_EPISODES/EP_001/build_ep001.py [--render] [--engine CYCLES|VIEWPORT]
"""
import bpy, os, sys, json, math, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
STUDIO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(STUDIO, "00_CORE_SYSTEM"))
import project_config as PC  # noqa: E402
import create_character as CC  # noqa: E402

KEY = "ARIAN"
PREFIX = "EP001_ARIAN"
START = (-12.0, -4.75, 0.14)          # on the near sidewalk of the street, walking along +X
HEADING = 90.0                         # rig rotation: its forward (-Y) turned to +X
VOICE = os.path.join(PC.BLENDER_DIR, "wall_toon", "voices", "wall_take1.mp3")
ITEMS = [
    dict(action="UHS_IDLE_Breathing", frames=36),
    dict(action="UHS_TRANS_IdleToWalk", blend=6),
    dict(action="UHS_WALK_Natural", loops=2, blend=6),
    dict(action="UHS_RUN_Cartoon", loops=4, blend=6),
    dict(action="UHS_WALK_Natural", loops=2, blend=8),
    dict(action="UHS_GESTURE_Wait", blend=10),
]


def build():
    import nla_sequencer as SEQ
    import setup_face as F
    import motion_validation as V
    rig, src = CC.open_rig(KEY)
    sc = bpy.context.scene
    # set
    with bpy.data.libraries.load(PC.path("08_ENVIRONMENT", "STREET", "Street.blend"), link=False) as (a, b):
        b.collections = ["Street"]
    sc.collection.children.link(b.collections[0])
    rig.location = START
    rig.rotation_euler = (0, 0, math.radians(HEADING))
    # body + root + foot lock
    seq = SEQ.sequence(rig, ITEMS, PREFIX)
    f0, f1 = seq["start"], seq["end"]
    # face: blinks, smile on the way, big grin running, then talks
    ad = rig.animation_data
    face = bpy.data.actions.new(f"{PREFIX}_FACE")
    ad.action = face
    run = next(sp for sp in seq["spans"] if sp["act"].name == "UHS_RUN_Cartoon")
    talk = int(seq["spans"][-1]["s"]) + 12
    F.key(rig, f0, smile=0.3, happy=0.0, brow_up_L=0.0, brow_up_R=0.0)
    F.key(rig, int(run["s"]), happy=0.0)
    F.key(rig, int(run["s"]) + 8, happy=1.0)
    F.key(rig, int(run["e"]), happy=1.0)
    F.key(rig, int(run["e"]) + 10, happy=0.0)
    F.key(rig, talk - 6, brow_up_L=0.0, brow_up_R=0.0)
    F.key(rig, talk, brow_up_L=0.5, brow_up_R=0.5)
    F.auto_blink(rig, f0, f1, seed=11)
    n_talk = 0
    if os.path.exists(VOICE):
        n_talk = F.lip_sync_from_audio(rig, VOICE, talk, start_sec=0.0, dur_sec=min(3.0, (f1 - talk) / PC.FPS))
    ad.action = None
    SEQ.face_track(rig, face)
    sc.frame_start, sc.frame_end = f0, f1
    # eyes: look along the way, then at the camera while talking
    eyes = rig.pose.bones["EYES_TARGET"]
    ad.action = face
    eyes.location = (0, 0, 0)
    eyes.keyframe_insert("location", frame=talk - 8)
    eyes.location = (0.25, 0.0, 0.0)
    eyes.keyframe_insert("location", frame=talk)
    ad.action = None
    # foot locking last, on the complete stack; two additive passes
    for o in rig.children:
        o.hide_viewport = True
    SEQ.footlock_track(rig, f0, f1, PREFIX, "FOOTLOCK")
    SEQ.footlock_track(rig, f0, f1, PREFIX, "FOOTLOCK_2")
    for o in rig.children:
        o.hide_viewport = False
    # QC of the whole episode (transitions included)
    qc = V.validate_range(rig, f0, f1, PREFIX)
    out = PC.path("10_QUALITY_CONTROL", "FINAL_REVIEW", f"{PREFIX}_episode_qc.json")
    with open(out, "w") as fh:
        json.dump(dict(qc, items=ITEMS, talk_frame=talk, lip_frames=n_talk), fh, indent=1, default=str)
    print("[UHAS] EP_001 QC", "PASS" if qc["pass"] else "FAIL", json.dumps({k: qc[k] for k in ("foot_slip", "ground", "pops", "joints")}, default=str))
    CC.save(os.path.join(HERE, "EP_001.blend"))
    return rig, f0, f1, talk


def render(engine="CYCLES"):
    import render_shorts as RS
    bpy.ops.wm.open_mainfile(filepath=os.path.join(HERE, "EP_001.blend"))
    import generate_rig as G
    G.enable_addons()
    sc = bpy.context.scene
    rig = bpy.data.objects[KEY + "_RIG"]
    f0, f1 = sc.frame_start, sc.frame_end
    RS.stage(sc, ground=False, sky=(0.62, 0.78, 0.95), sun=3.0)   # the street comes without its sky and sun
    cam = RS.camera(sc, lens=35)
    RS.follow(cam, rig, f0, f1, offset=(0.0, -3.9, 0.25), look_h=1.0, smooth=10)
    RS.setup_engine(sc, engine, (432, 768), samples=6)
    out = os.path.join(HERE, "Renders", "EP_001_demo")
    mp4 = RS.render(sc, out, f0, f1)
    qc = json.load(open(PC.path("10_QUALITY_CONTROL", "FINAL_REVIEW", f"{PREFIX}_episode_qc.json")))
    if os.path.exists(VOICE):
        off = (qc["talk_frame"] - f0) / PC.FPS
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", mp4, "-itsoffset", f"{off:.3f}", "-t", "3",
                        "-i", VOICE, "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", out + "_v.mp4"], check=True)
        os.replace(out + "_v.mp4", mp4)
    RS.clean_frames(out)
    print("[UHAS] rendered", mp4)


if __name__ == "__main__":
    if "--render-only" not in sys.argv:
        build()
    if "--render" in sys.argv or "--render-only" in sys.argv:
        eng = sys.argv[sys.argv.index("--engine") + 1] if "--engine" in sys.argv else "CYCLES"
        render(eng)
