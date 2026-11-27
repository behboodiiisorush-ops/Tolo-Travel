"""«سایه‌ی دانیال» — build EP_002.blend from the studio: living room set, the six Rigify characters, their motion
libraries through the NLA (cross-fades, root travel, foot lock passes), faces (blinks, expressions, lip flaps for
the user's voices), lights and cameras. Per-frame changes (which camera, flicker, who casts a shadow) live in
render.py's state(f), so the .blend stays simple.

    blender/cast/bpy.sh ANIMATION_STUDIO/12_EPISODES/EP_002_SAYEH/scene.py [--still 60,250,...]
Shots (s):  1  0-5   wide: family, Daniel comes in late      2  5-9   lights flicker and go out
            3  9-13  reverse: the Shadow in the doorway       4  13-17 medium: fear
            5  17-22 floor: everyone has a shadow but Daniel  6  22-27 reverse: the Shadow walks up to Daniel
            7  27-31 wide: flash, lights back, Daniel's shadow is back
"""
import bpy, os, sys, math, random
from mathutils import Vector
HERE = os.path.dirname(os.path.abspath(__file__))
STUDIO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(STUDIO, "00_CORE_SYSTEM"))
sys.path.insert(0, HERE)
import project_config as PC  # noqa: E402
sys.path.insert(0, HERE)
import generate_rig as G  # noqa: E402
import setup_face as F  # noqa: E402
import nla_sequencer as SEQ  # noqa: E402
import render_shorts as RS  # noqa: E402
import puppets as PP  # noqa: E402
from lines import LINES, END, fr  # noqa: E402

N = fr(END) - 1
WHO = {"mother": "MOTHER", "father": "FATHER", "arian": "ARIAN", "lina": "LINA", "daniel": "DANIEL"}
# where everyone stands (x, y) and the heading they face (0 = towards the camera, -Y)
SPOT = {"FATHER": (-1.25, -1.0), "MOTHER": (-0.5, -1.05), "LINA": (0.15, -0.95), "ARIAN": (0.8, -1.05),
        "DANIEL": (2.9, -1.05), "SHADOW": (0.2, -2.45)}
DOOR_X = 0.2


def A(key, name):
    return f"{key}:{name}"


def load_world():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    G.enable_addons()
    sc = bpy.context.scene
    sc.render.fps = PC.FPS
    sc.frame_start, sc.frame_end = 1, N
    with bpy.data.libraries.load(PC.path("08_ENVIRONMENT", "LIVING_ROOM", "Living_Room.blend"), link=False) as (s, d):
        d.collections = ["Living_Room"]
    sc.collection.children.link(d.collections[0])
    for o in d.collections[0].objects:              # the TV corner and its light are not needed; the set's own lamp stays
        if o.type == "LIGHT" and "Floor lamp" not in o.name:
            bpy.data.objects.remove(o)
    rigs = {}
    for k in ("ARIAN", "DANIEL", "LINA", "FATHER", "MOTHER", "SHADOW"):
        with bpy.data.libraries.load(PC.char_dir(k, "Rig.blend"), link=False) as (s, d):
            d.collections = [k]
        c = d.collections[0]
        sc.collection.children.link(c)
        for sub in c.children:
            if sub.name.endswith("_HELPERS"):
                sub.hide_render = True
        with bpy.data.libraries.load(PC.char_dir(k, "Animation_Library.blend"), link=False) as (s, d):
            d.actions = [a for a in s.actions if a.startswith("UHS_")]
        for a in d.actions:
            a.name = A(k, a.name.split(".")[0])
        rig = bpy.data.objects[k + "_RIG"]
        if rig.animation_data:
            rig.animation_data.action = None
            for t in list(rig.animation_data.nla_tracks):
                rig.animation_data.nla_tracks.remove(t)
        rigs[k] = rig
    return sc, rigs


def build_set(sc):
    """Front wall with a dark doorway (seen only in the reverse shots) + floor running out towards the camera."""
    import puppets as PP
    c = bpy.data.collections.new("EP002_SET")
    sc.collection.children.link(c)

    def box(name, loc, size, mat):
        bpy.ops.mesh.primitive_cube_add(location=loc)
        o = bpy.context.object
        o.name = name
        o.scale = (size[0] / 2, size[1] / 2, size[2] / 2)
        bpy.ops.object.transform_apply(scale=True)
        o.data.materials.append(mat)
        for u in list(o.users_collection):
            u.objects.unlink(o)
        c.objects.link(o)
        return o
    wall = PP.toon_mat("ep2 wall", (0.82, 0.9, 0.78), 0.22)
    dark = PP.toon_mat("ep2 doorway", (0.02, 0.02, 0.03), 0.0)
    frame_m = PP.toon_mat("ep2 door frame", (0.97, 0.97, 0.95), 0.22)
    floor = PP.toon_mat("ep2 floor", (0.6, 0.42, 0.3), 0.22)
    H, Y, W = 2.7, -2.28, 5.0
    dw, dh = 1.0, 2.1
    parts = [box("front wall L", ((-W / 2 + DOOR_X - dw / 2) / 2, Y, H / 2), (DOOR_X - dw / 2 + W / 2, 0.16, H), wall),
             box("front wall R", ((W / 2 + DOOR_X + dw / 2) / 2, Y, H / 2), (W / 2 - DOOR_X - dw / 2, 0.16, H), wall),
             box("front wall top", (DOOR_X, Y, (dh + H) / 2), (dw, 0.16, H - dh), wall),
             box("doorway dark", (DOOR_X, Y - 1.2, dh / 2), (dw + 0.4, 2.2, dh + 0.3), dark),
             box("door frame L", (DOOR_X - dw / 2 - 0.04, Y + 0.02, dh / 2), (0.08, 0.2, dh), frame_m),
             box("door frame R", (DOOR_X + dw / 2 + 0.04, Y + 0.02, dh / 2), (0.08, 0.2, dh), frame_m),
             box("door frame T", (DOOR_X, Y + 0.02, dh + 0.04), (dw + 0.16, 0.2, 0.08), frame_m)]
    box("floor front", (0, -5.0, -0.05), (12, 5.5, 0.1), floor)
    for p in parts:
        p["front"] = 1
    return c


def lights(sc):
    w = bpy.data.worlds.new("EP002 world")
    sc.world = w
    w.use_nodes = True
    w.node_tree.nodes["Background"].inputs["Color"].default_value = (0.55, 0.62, 0.75, 1)
    w.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.6
    out = {}
    key = bpy.data.objects.new("EP2 key", bpy.data.lights.new("EP2 key", "SUN"))
    key.data.angle = math.radians(3)                  # crisp floor shadows (shot 5 depends on them)
    key.rotation_euler = (math.radians(42), 0, math.radians(200))
    sc.collection.objects.link(key)
    room = bpy.data.objects.new("EP2 room", bpy.data.lights.new("EP2 room", "AREA"))
    room.data.size = 3.0
    room.location = (0, 0, 2.6)
    sc.collection.objects.link(room)
    eye = bpy.data.objects.new("EP2 fill", bpy.data.lights.new("EP2 fill", "AREA"))
    eye.data.size = 4.0
    eye.location = (0, -4.0, 2.2)
    eye.rotation_euler = (math.radians(70), 0, 0)
    sc.collection.objects.link(eye)
    return key, room, eye


def cameras(sc):
    cams = {}
    for name, loc, tgt, lens in (("WIDE", (0.35, -4.6, 1.3), (0.35, 0, 0.95), 20),
                                 ("MED", (0.2, -3.35, 1.45), (0.2, -0.8, 1.25), 24),
                                 ("REV", (0.6, 1.9, 1.55), (0.3, -2.3, 1.0), 22),
                                 ("FLOOR", (0.9, -2.3, 0.28), (0.4, 0.2, 0.0), 18)):
        cam = RS.camera(sc, name="CAM_" + name, lens=lens)
        RS.aim(cam, loc, tgt)
        cams[name] = cam
    return cams


def talk(rig, f0, f1, seed):
    """Silent-version lip flaps (the user's ElevenLabs voices replace them): syllables every 3-5 frames."""
    r = random.Random(seed)
    F.key(rig, f0 - 1, jaw_open=0.0, mouth_o=0.0, mouth_wide=0.0)
    f = f0
    while f < f1:
        F.key(rig, f, jaw_open=r.uniform(0.45, 0.9), mouth_o=r.uniform(0, 0.5), mouth_wide=r.uniform(0, 0.5))
        F.key(rig, f + 2, jaw_open=r.uniform(0.05, 0.2), mouth_o=0.0, mouth_wide=0.0)
        f += r.choice((3, 4, 4, 5))
    F.key(rig, f1, jaw_open=0.0, mouth_o=0.0, mouth_wide=0.0)


def animate(sc, rigs):
    T = lambda s: fr(s)                                                              # noqa: E731
    plan = {
        "FATHER": [dict(action="UHS_IDLE_Breathing", frames=T(5.5)), dict(action="UHS_IDLE_Nervous", frames=T(9.5) - T(5.5), blend=10),
                   dict(action="UHS_GESTURE_Wait", blend=8), dict(action="UHS_IDLE_Breathing", frames=N, blend=12)],
        "MOTHER": [dict(action="UHS_GESTURE_Thinking", frames=T(5.2)), dict(action="UHS_IDLE_Nervous", frames=T(13.6) - T(5.2), blend=10),
                   dict(action="UHS_GESTURE_No", blend=8), dict(action="UHS_IDLE_Breathing", frames=N, blend=12)],
        "LINA": [dict(action="UHS_IDLE_Breathing", frames=T(5.6)), dict(action="UHS_IDLE_Nervous", frames=T(13.2) - T(5.6), blend=10),
                 dict(action="UHS_EMOTION_Terrified", blend=8), dict(action="UHS_IDLE_Breathing", frames=N, blend=14)],
        "ARIAN": [dict(action="UHS_IDLE_Breathing", frames=T(5.3)), dict(action="UHS_IDLE_Nervous", frames=T(12.8) - T(5.3), blend=10),
                  dict(action="UHS_EMOTION_Terrified", blend=8), dict(action="UHS_IDLE_Breathing", frames=N, blend=14)],
        "DANIEL": [dict(action="UHS_IDLE_Breathing", frames=T(0.4), heading=-90),
                   dict(action="UHS_TRANS_IdleToWalk", blend=4, heading=-90),
                   dict(action="UHS_IDLE_Breathing", frames=T(5.4) - T(3.3), blend=12, heading=0),
                   dict(action="UHS_IDLE_Nervous", frames=T(17.5) - T(5.4), blend=10),
                   dict(action="UHS_IDLE_Nervous", frames=T(24.6) - T(17.5), blend=10),
                   dict(action="UHS_GESTURE_Yes", blend=8), dict(action="UHS_IDLE_Breathing", frames=N, blend=12)],
        "SHADOW": [dict(action="UHS_IDLE_Breathing", frames=T(23.2), heading=180),
                   dict(action="UHS_WALK_Natural", frames=20, blend=8, heading=128),
                   dict(action="UHS_IDLE_Breathing", frames=T(24.9) - T(23.2) - 20, blend=10, heading=128),
                   dict(action="UHS_GESTURE_Yes", blend=8, heading=128), dict(action="UHS_IDLE_Breathing", frames=N, blend=10, heading=128)],
    }
    for k, items in plan.items():
        rig = rigs[k]
        x, y = SPOT[k]
        rig.location = (x, y, 0)
        rig.rotation_euler = (0, 0, 0)
        its = [dict(it, action=A(k, it["action"])) for it in items]
        seq = SEQ.sequence(rig, its, f"EP002_{k}")
        ad = rig.animation_data
        # trim: nothing past the film's end
        face = bpy.data.actions.new(f"EP002_{k}_FACE")
        ad.action = face
        F.key(rig, 1, smile=0.3 if k != "SHADOW" else 0.0)
        F.auto_blink(rig, 1, N, seed=7 + 13 * list(plan).index(k))
        # fear from the flicker on, relief at the end
        if k in ("ARIAN", "LINA", "MOTHER", "FATHER", "DANIEL"):
            F.key(rig, T(5.6), smile=0.3, fear=0.0)
            F.key(rig, T(6.4), smile=0.0, fear=0.5)
            F.key(rig, T(12.6), fear=0.5)
            F.key(rig, T(13.2), fear=1.0 if k in ("ARIAN", "LINA") else 0.7)
            F.key(rig, T(27.6), fear=1.0 if k in ("ARIAN", "LINA") else 0.7, happy=0.0)
            F.key(rig, T(28.4), fear=0.0, happy=0.8)
        if k == "DANIEL":
            F.key(rig, T(17.6), sad=0.0)
            F.key(rig, T(18.4), sad=0.8)
            F.key(rig, T(27.6), sad=0.8)
            F.key(rig, T(28.4), sad=0.0)
            pb = rig.pose.bones["EYES_TARGET"]          # looks down at the floor where his shadow should be
            for t, z in ((17.4, 0.0), (18.2, -0.45), (22.0, -0.45), (22.8, 0.0)):
                pb.location = (0, 0, z)
                pb.keyframe_insert("location", frame=T(t))
        for a, b, who, _ in LINES:
            if WHO[who] == k:
                talk(rig, T(a), T(b), seed=int(a * 10))
        ad.action = None
        SEQ.face_track(rig, face)
        for o in rig.children:
            o.hide_viewport = True
        SEQ.footlock_track(rig, 1, N, f"EP002_{k}", "FOOTLOCK")
        SEQ.footlock_track(rig, 1, N, f"EP002_{k}", "FOOTLOCK_2")
        for o in rig.children:
            o.hide_viewport = False
        print("[EP002]", k, "animated, strips:", [t.name for t in ad.nla_tracks])
    # the Shadow's eyes glow
    m = bpy.data.materials.get("PP Shadow shadow eye white")
    if m:
        for n in m.node_tree.nodes:
            if n.type == "EMISSION":
                n.inputs["Strength"].default_value = 2.5


def main():
    sc, rigs = load_world()
    build_set(sc)
    lights(sc)
    cams = cameras(sc)
    animate(sc, rigs)
    sc.camera = cams["WIDE"]
    RS.setup_engine(sc, "CYCLES", (540, 960), samples=8)
    out = os.path.join(HERE, "EP_002.blend")
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=out, compress=True)
    print("[EP002] saved", out, os.path.getsize(out) // 1024, "KB")


if __name__ == "__main__":
    main()
