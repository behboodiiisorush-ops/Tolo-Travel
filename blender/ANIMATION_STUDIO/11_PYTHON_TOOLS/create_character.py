"""Build, animate, validate and document one studio character — the whole UHAS pipeline.

    blender/cast/bpy.sh ANIMATION_STUDIO/11_PYTHON_TOOLS/create_character.py ARIAN [--stage build,library,qc,tests]

Stages (each saves its result, so a crash only repeats one stage):
  build    puppet + Rigify rig + face controls + soles     -> CHAR/Rig.blend (work file)
  library  every MOTION_LIBRARY entry baked onto this rig   -> Rig.blend, Animation_Library.blend (actions only)
  qc       motion/face/weight validation                    -> 10_QUALITY_CONTROL/*, CHAR/TESTS/qc_summary.json
  tests    reference renders + WALK / RUN / EXPRESSIONS mp4 -> CHAR/REFERENCES, CHAR/TESTS;
           then Face.blend, Materials.blend, Model.blend are written from Rig.blend
"""
import bpy
import json
import os
import sys
import time
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "00_CORE_SYSTEM"))
import project_config as PC  # noqa: E402
import rig_config as RC  # noqa: E402
import motion_config as MC  # noqa: E402


def log(*a):
    print("[UHAS]", time.strftime("%H:%M:%S"), *a, flush=True)


def rig_file(key):
    return PC.char_dir(key, "Rig.blend")


def save(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=path, compress=True)
    log("saved", os.path.relpath(path, PC.STUDIO), os.path.getsize(path) // 1024, "KB")


class meshes_hidden:
    """Bone-only work (bakes, foot locks, motion QC) runs several times faster without deforming the meshes:
    hidden objects are not evaluated by Blender."""
    def __init__(self, rig):
        self.objs = [o for o in rig.children if o.type == "MESH"]

    def __enter__(self):
        self.keep = {o.name: o.hide_viewport for o in self.objs}
        for o in self.objs:
            o.hide_viewport = True

    def __exit__(self, *a):
        for o in self.objs:
            o.hide_viewport = self.keep[o.name]


def open_rig(key):
    import generate_rig as G
    bpy.ops.wm.open_mainfile(filepath=rig_file(key))
    G.enable_addons()
    rig = bpy.data.objects[key + RC.RIG_SUFFIX]
    src = bpy.data.objects[key + RC.SRC_SUFFIX]
    return rig, src


# ------------------------------------------------------------------ stages
def stage_build(key):
    import generate_rig as G
    import setup_face as F
    import import_motion as IM
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.scene.render.fps = PC.FPS
    r = G.build(key)
    rig = r["rig"]
    F.build(rig)
    F.expression_actions(rig)
    IM.store_soles(rig)
    rig.animation_data.action = None
    save(rig_file(key))


def stage_library(key, only=None):
    import import_motion as IM
    rig, src = open_rig(key)
    done, failed = [], {}
    hid = meshes_hidden(rig)
    hid.__enter__()
    if "uhas_foot_pitch_deg" not in rig:
        measured, remaining = IM.calibrate_feet(rig, src)
        log("feet calibrated: capture pitch (deg, + = toe-down)", {k: round(v, 1) for k, v in measured.items()},
            "-> after correction", {k: round(v, 2) for k, v in remaining.items()})
        if min(abs(v) for v in remaining.values()) > 2.0:          # the flatter foot must end up flat
            raise RuntimeError(f"foot calibration did not converge: {remaining}")
    for e in MC.LIBRARY:
        if only and e["name"] not in only:
            continue
        old = bpy.data.actions.get(e["name"])
        if old:
            bpy.data.actions.remove(old)
        t = time.time()
        try:
            act = IM.import_action(rig, src, e, key)
            done.append(act.name)
            log(f"action {act.name}: {act['frames']} f, root={act['root_mode']}, raw slip {act['raw_slip_cm']:.1f} cm "
                f"({time.time() - t:.0f}s)")
        except Exception as ex:                    # keep going: one bad clip must not stop the library
            failed[e["name"]] = f"{type(ex).__name__}: {ex}"
            log("FAILED", e["name"], failed[e["name"]])
            traceback.print_exc()
    hid.__exit__()
    rig.animation_data.action = None
    rig["uhas_library_failed"] = json.dumps(failed)
    save(rig_file(key))
    acts = {a for a in bpy.data.actions if a.name.startswith("UHS_")}
    lib = PC.char_dir(key, "Animation_Library.blend")
    bpy.data.libraries.write(lib, acts, fake_user=True, compress=True)
    log("wrote", os.path.relpath(lib, PC.STUDIO), len(acts), "actions")
    return done, failed


def stage_qc(key):
    import motion_validation as V
    rig, src = open_rig(key)
    conv = V.joint_conventions(rig)
    results = []
    hid = meshes_hidden(rig)
    hid.__enter__()
    for e in MC.LIBRARY:
        act = bpy.data.actions.get(e["name"])
        if act is None:
            continue
        t = time.time()
        r = V.validate_action(rig, act, conv)
        results.append(r)
        log(f"QC {act.name}: {'PASS' if r['pass'] else 'FAIL'} slip {r['foot_slip']['max_cm']} cm, "
            f"pops {r['pops']['count']}, ikfk {r['ik_fk']['max_cm']} cm ({time.time() - t:.0f}s)")
    hid.__exit__()
    face = V.validate_face(rig)
    deform = V.deformation(rig)
    failed = json.loads(rig.get("uhas_library_failed", "{}"))
    rep = V.write_reports(key, results, face, deform)
    summary = dict(character=key, actions=len(results), passed=sum(r["pass"] for r in results),
                   failed_imports=failed, face=face["pass_"], weights=deform["pass_"],
                   per_action={r["action"]: r["pass"] for r in results})
    os.makedirs(PC.char_dir(key, "TESTS"), exist_ok=True)
    with open(PC.char_dir(key, "TESTS", "qc_summary.json"), "w") as fh:
        json.dump(summary, fh, indent=1)
    log("QC report", os.path.relpath(rep, PC.STUDIO), summary["passed"], "/", summary["actions"])


def stage_tests(key, which=("refs", "walk", "run", "expressions")):
    import render_shorts as RS
    import import_motion as IM
    import setup_face as F
    tests = PC.char_dir(key, "TESTS")
    refs = PC.char_dir(key, "REFERENCES")
    made = []
    rig, src = open_rig(key)
    sc = bpy.context.scene
    RS.stage(sc)
    cam = RS.camera(sc, lens=50)
    ad = rig.animation_data or rig.animation_data_create()
    if "refs" in which:
        ad.action = None
        for t in list(ad.nla_tracks):
            t.mute = True
        for pb in rig.pose.bones:                      # removing the action leaves the last pose: reset to rest
            pb.location = (0, 0, 0)
            pb.rotation_quaternion = (1, 0, 0, 0)
            pb.rotation_euler = (0, 0, 0)
            pb.scale = (1, 1, 1)
        F.pose(rig, smile=0.3)
        RS.setup_engine(sc, "CYCLES", (720, 1080))
        for name, loc in (("FRONT", (0, -4.6, 1.05)), ("SIDE", (4.6, 0, 1.05)), ("BACK", (0, 4.6, 1.05))):
            RS.aim(cam, loc, (0, 0, 0.95))
            sc.render.filepath = os.path.join(refs, name + ".png")
            os.makedirs(refs, exist_ok=True)
            bpy.ops.render.render(write_still=True)
            made.append(sc.render.filepath)
        F.pose(rig)

    def play(action_name, loops, out, offset=(3.6, 0.0, 0.35)):
        act = bpy.data.actions[action_name]
        n = int(act["frames"])
        N = n * loops if act.get("loop") else n
        for t in list(ad.nla_tracks):
            ad.nla_tracks.remove(t)
        ad.action = None
        IM.nla_strip(rig, "BODY", act, 1, repeat=float(loops) if act.get("loop") else 1.0)
        ad.action = IM.key_root(rig, 1, N, IM.root_fn(act), f"TEST_{action_name}_ROOT")
        F.auto_blink(rig, 1, N, seed=3)
        F.key(rig, 1, smile=0.35)
        sc.frame_start, sc.frame_end = 1, N
        RS.follow(cam, rig, 1, N, offset=offset)
        RS.setup_engine(sc, "CYCLES", (432, 768), samples=6)
        o = os.path.join(tests, out)
        mp4 = RS.render(sc, o, 1, N)
        RS.clean_frames(o)
        made.append(mp4)
    if "walk" in which:
        play("UHS_WALK_Natural", 3, "WALK")
    if "run" in which:
        play("UHS_RUN_Cartoon", 4, "RUN")
    if "expressions" in which:
        for t in list(ad.nla_tracks):
            ad.nla_tracks.remove(t)
        idle = bpy.data.actions["UHS_IDLE_Breathing"]
        IM.nla_strip(rig, "BODY", idle, 1, repeat=1.0)
        face_act = bpy.data.actions.new(f"TEST_{key}_FACE")
        ad.action = face_act
        f = 1
        for name in ("Neutral", "Happy", "Sad", "Angry", "Surprise", "Fear", "Wink"):
            vals = {n: F.EXPRESSIONS[name].get(n, F.SLIDERS[n][0]) for n in F.SLIDERS}
            F.key(rig, f, **vals)
            F.key(rig, f + 10, **vals)
            f += 16
        voice = os.path.join(PC.BLENDER_DIR, "wall_toon", "voices", "wall_take1.mp3")
        F.key(rig, f, **{n: F.SLIDERS[n][0] for n in F.SLIDERS})
        if os.path.exists(voice):
            n = F.lip_sync_from_audio(rig, voice, f + 1, start_sec=0.0, dur_sec=3.0)
            f += n + 2
        F.auto_blink(rig, 150, f, seed=5)
        sc.frame_start, sc.frame_end = 1, f
        sc.frame_set(1)
        eye = (rig.matrix_world @ rig.pose.bones["eye_l"].head + rig.matrix_world @ rig.pose.bones["eye_r"].head) / 2
        cam.animation_data_clear()
        cam.data.lens = 70
        # the idle sways the body ~15 cm: the face camera follows the head (smoothed), or the face leaves the frame
        RS.follow(cam, rig, 1, f, offset=(0.3, -1.6, 0.07), look_h=eye.z - 0.12, bone="head", smooth=8)
        RS.setup_engine(sc, "CYCLES", (432, 768), samples=6)
        o = os.path.join(tests, "EXPRESSIONS")
        mp4 = RS.render(sc, o, 1, f)
        if os.path.exists(voice):                 # put the voice under the lip-sync part
            import subprocess
            subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", mp4, "-itsoffset", f"{(7 * 16 + 1) / PC.FPS:.3f}",
                            "-t", "3", "-i", voice, "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac",
                            "-shortest", o + "_voice.mp4"], check=True)
            os.replace(o + "_voice.mp4", mp4)
        RS.clean_frames(o)
        made.append(mp4)
    with open(os.path.join(tests, "renders.json"), "w") as fh:
        json.dump([os.path.relpath(p, PC.STUDIO) for p in made], fh, indent=1)
    return made


def stage_split(key):
    """Face.blend, Materials.blend, Model.blend written from the rig file (smaller, single-purpose files)."""
    rig, src = open_rig(key)
    # Materials: every material used by the character, marked as assets
    mats = set()
    for o in rig.children:
        for s in o.material_slots:
            if s.material:
                mats.add(s.material)
    for m in mats:
        try:
            m.asset_mark()
            m.asset_data.tags.new(key.lower())
        except Exception:
            pass
    bpy.data.libraries.write(PC.char_dir(key, "Materials.blend"), mats, fake_user=True, compress=True)
    log("wrote Materials.blend", len(mats), "materials")
    # Face: the rig + the face parts + expression actions in a scene of their own
    sc_face = bpy.data.scenes.new(f"{key}_FACE")
    col = bpy.data.collections.new(f"{key}_FACE_RIG")
    sc_face.collection.children.link(col)
    for o in [rig] + [o for o in rig.children if "_FACE_" in o.name]:
        col.objects.link(o)
    acts = {a for a in bpy.data.actions if a.name.startswith("UHS_FACE_")}
    bpy.data.libraries.write(PC.char_dir(key, "Face.blend"), {sc_face} | acts, fake_user=True, compress=True)
    log("wrote Face.blend")
    # Model: meshes only, rest pose, no rig
    for o in list(bpy.data.objects):
        if o.type == "ARMATURE":
            bpy.data.objects.remove(o)
    for o in bpy.data.objects:
        if o.type == "MESH":
            for m in list(o.modifiers):
                if m.type == "ARMATURE":
                    o.modifiers.remove(m)
            if o.data.shape_keys and o.data.shape_keys.animation_data:
                o.data.shape_keys.animation_data_clear()
    for a in list(bpy.data.actions):
        bpy.data.actions.remove(a)
    for s in list(bpy.data.scenes):
        if s.name.endswith("_FACE"):
            bpy.data.scenes.remove(s)
    save(PC.char_dir(key, "Model.blend"))


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    key = next(a for a in argv if a.isupper())
    stages = argv[argv.index("--stage") + 1].split(",") if "--stage" in argv else ["build", "library", "qc", "tests", "split"]
    only = argv[argv.index("--only") + 1].split(",") if "--only" in argv else None
    for s in stages:
        t = time.time()
        log("stage", s, key)
        if s == "build":
            stage_build(key)
        elif s == "library":
            stage_library(key, only)
        elif s == "qc":
            stage_qc(key)
        elif s == "tests":
            stage_tests(key, tuple(only) if only else ("refs", "walk", "run", "expressions"))
        elif s == "split":
            stage_split(key)
        log("stage", s, "done in", int(time.time() - t), "s")


if __name__ == "__main__":
    main()
