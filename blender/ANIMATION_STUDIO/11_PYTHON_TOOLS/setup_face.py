"""Facial animation system for the puppet head on a Rigify rig.

Controls (all on the rig, no Python needed when the file is opened — drivers use Blender's simple expressions):
  FACE_CTRL   pose bone in front of the face carrying sliders (custom properties):
              blink_L, blink_R, lids_wide, squint, brow_up_L, brow_up_R, brow_angle (-1 angry .. +1 worried),
              smile, frown, jaw_open, mouth_o, mouth_wide, and expression presets happy, sad, angry, surprise, fear
  EYES_TARGET look-at control (child of the head control); both eyes Damped-Track it.
Driven: lid bones (rotation), brow bones (tilt + lift), the mouth's shape keys (open, smile, frown, wide, o).

Tools: expression actions (UHS_FACE_*), auto_blink(), lip_sync_from_audio() (amplitude + spectral brightness
-> jaw / o / wide; a light viseme approximation, not phoneme-accurate).
"""
import bpy
import math
import random
import subprocess
import numpy as np
from mathutils import Vector

import project_config as PC
import rig_config as RC


class FaceError(RuntimeError):
    pass


SLIDERS = {   # name: (default, min, max, description)
    "blink_L": (0.0, 0.0, 1.0, "close the left eye"), "blink_R": (0.0, 0.0, 1.0, "close the right eye"),
    "lids_wide": (0.0, 0.0, 1.0, "eyes wide open"), "squint": (0.0, 0.0, 1.0, "suspicious squint"),
    "brow_up_L": (0.0, -1.0, 1.0, "raise / lower left brow"), "brow_up_R": (0.0, -1.0, 1.0, "raise / lower right brow"),
    "brow_angle": (0.0, -1.0, 1.0, "-1 angry (inner ends down) .. +1 worried (inner ends up)"),
    "smile": (0.0, 0.0, 1.0, "smile"), "frown": (0.0, 0.0, 1.0, "frown"), "jaw_open": (0.0, 0.0, 1.0, "open the mouth"),
    "mouth_o": (0.0, 0.0, 1.0, "round 'o' mouth"), "mouth_wide": (0.0, 0.0, 1.0, "wide, tense mouth"),
    "happy": (0.0, 0.0, 1.0, "preset"), "sad": (0.0, 0.0, 1.0, "preset"), "angry": (0.0, 0.0, 1.0, "preset"),
    "surprise": (0.0, 0.0, 1.0, "preset"), "fear": (0.0, 0.0, 1.0, "preset"),
}

# driven values (simple expressions; variable names = slider names)
LID_DEG = "max(95*{b}, 45*squint + 25*sad + 20*angry - 12*lids_wide - 12*surprise - 12*fear)"
BROW_DEG = "16*brow_angle + 14*sad + 14*fear + 4*surprise - 18*angry"
BROW_LIFT = "0.009*({u} + 0.6*sad + 0.8*fear + 1.3*surprise + 0.3*happy - 0.5*angry)"
MOUTH = {
    "open": "min(1, jaw_open + 0.6*surprise + 0.35*fear)",
    "smile": "min(1, smile + happy)",
    "frown": "min(1, frown + 0.8*sad + 0.4*angry)",
    "wide": "min(1, mouth_wide + 0.6*fear + 0.3*angry)",
    "o": "min(1, mouth_o + 0.5*surprise)",
}
EXPRESSIONS = {
    "Neutral": {}, "Happy": dict(happy=1.0), "Sad": dict(sad=1.0), "Angry": dict(angry=1.0),
    "Surprise": dict(surprise=1.0), "Fear": dict(fear=1.0),
    "Blink": dict(blink_L=1.0, blink_R=1.0), "Wink": dict(blink_L=1.0, smile=0.6),
    "Talk_A": dict(jaw_open=0.8), "Talk_O": dict(jaw_open=0.4, mouth_o=1.0), "Talk_E": dict(jaw_open=0.3, mouth_wide=0.8),
}


def mouth_object(rig):
    m = next((o for o in rig.children if o.name.endswith("FACE_mouth")), None)
    if m is None or not m.data.shape_keys:
        raise FaceError("no mouth with shape keys under the rig")
    for k in MOUTH:
        if k not in m.data.shape_keys.key_blocks:
            raise FaceError(f"mouth shape key '{k}' missing")
    return m


def _driver(owner, path, index, expr, rig, names):
    if index is None:
        fc = owner.driver_add(path)
    else:
        fc = owner.driver_add(path, index)
    d = fc.driver
    d.type = "SCRIPTED"
    for v in list(d.variables):
        d.variables.remove(v)
    for n in names:
        if n not in expr:
            continue
        v = d.variables.new()
        v.name = n
        v.type = "SINGLE_PROP"
        v.targets[0].id_type = "OBJECT"
        v.targets[0].id = rig
        v.targets[0].data_path = f'pose.bones["{RC.FACE_CTRL}"]["{n}"]'
    d.expression = expr
    if not d.is_simple_expression:
        raise FaceError(f"driver expression is not a simple expression (would need auto-run): {expr}")
    return fc


def _quat_drivers(rig, pb, axis_arm, deg_expr):
    """Drive a bone's quaternion = rotation of deg_expr degrees about an armature-space axis."""
    ax = (pb.bone.matrix_local.to_3x3().inverted() @ Vector(axis_arm)).normalized()
    pb.rotation_mode = "QUATERNION"
    half = f"(({deg_expr})*0.00872665)"
    comps = [f"cos{half}", f"{ax.x:.6f}*sin{half}", f"{ax.y:.6f}*sin{half}", f"{ax.z:.6f}*sin{half}"]
    for i, e in enumerate(comps):
        _driver(pb, "rotation_quaternion", i, e, rig, SLIDERS)


def build(rig):
    """Add FACE_CTRL + EYES_TARGET and wire every driver. Safe to call once per rig."""
    for b in RC.FACE_BONES:
        if b not in rig.pose.bones:
            raise FaceError(f"face bone {b} missing (generate_rig.build adds them)")
    mouth = mouth_object(rig)
    if RC.FACE_CTRL in rig.data.bones:
        raise FaceError("face controls already built on this rig")
    # bones
    bpy.context.view_layer.objects.active = rig
    for o in bpy.context.view_layer.objects:
        o.select_set(False)
    rig.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    eb = rig.data.edit_bones
    hd = eb[RC.HEAD_DEF]
    eyes = (eb["eye_l"].head + eb["eye_r"].head) / 2
    top = hd.head + (hd.tail - hd.head) * 1.3
    fc = eb.new(RC.FACE_CTRL)
    fc.head = Vector((0.0, eyes.y - 0.28, top.z + 0.08))
    fc.tail = fc.head + Vector((0, 0, 0.06))
    fc.parent = eb["head"]
    fc.use_deform = False
    et = eb.new(RC.EYES_TARGET)
    et.head = Vector((eyes.x, eyes.y - 0.65, eyes.z))
    et.tail = et.head + Vector((0, 0, 0.05))
    et.parent = eb["head"]
    et.use_deform = False
    coll = rig.data.collections.get("Face (Puppet)") or rig.data.collections.new("Face (Puppet)")
    coll.assign(fc)
    coll.assign(et)
    bpy.ops.object.mode_set(mode="OBJECT")
    # sliders
    pb = rig.pose.bones[RC.FACE_CTRL]
    for n, (dv, lo, hi, desc) in SLIDERS.items():
        pb[n] = dv
        ui = pb.id_properties_ui(n)
        ui.update(min=lo, max=hi, soft_min=lo, soft_max=hi, description=desc, default=dv)
    for b in (RC.FACE_CTRL, RC.EYES_TARGET):
        rig.pose.bones[b].lock_rotation = (True, True, True)
        rig.pose.bones[b].lock_scale = (True, True, True)
    rig.pose.bones[RC.FACE_CTRL].lock_location = (True, True, True)
    # eyes
    for s in ("l", "r"):
        e = rig.pose.bones[f"eye_{s}"]
        for c in list(e.constraints):
            e.constraints.remove(c)
        c = e.constraints.new("DAMPED_TRACK")
        c.target, c.subtarget, c.track_axis = rig, RC.EYES_TARGET, "TRACK_Y"
    # lids and brows
    for s, S, sign in (("l", "L", 1), ("r", "R", -1)):
        _quat_drivers(rig, rig.pose.bones[f"lid_{s}"], (1, 0, 0), LID_DEG.format(b=f"blink_{S}"))
        bb = rig.pose.bones[f"brow_{s}"]
        _quat_drivers(rig, bb, (0, 1, 0), f"{sign}*({BROW_DEG})")
        inv = bb.bone.matrix_local.to_3x3().inverted() @ Vector((0, 0, 1))
        lift = BROW_LIFT.format(u=f"brow_up_{S}")
        for i in range(3):
            _driver(bb, "location", i, f"{inv[i]:.6f}*{lift}", rig, SLIDERS)
    # mouth shape keys
    kb = mouth.data.shape_keys.key_blocks
    for k, expr in MOUTH.items():
        kb[k].value = 0.0
        _driver(kb[k], "value", None, expr, rig, SLIDERS)
    return pb


# ------------------------------------------------------------------ animation helpers
def key(rig, frame, **values):
    pb = rig.pose.bones[RC.FACE_CTRL]
    for n, v in values.items():
        if n not in SLIDERS:
            raise FaceError(f"unknown face slider {n}")
        pb[n] = float(v)
        pb.keyframe_insert(f'["{n}"]', frame=frame, group="Face")


def pose(rig, **values):
    """Set sliders (others back to their defaults) without keying."""
    pb = rig.pose.bones[RC.FACE_CTRL]
    for n, (dv, *_rest) in SLIDERS.items():
        pb[n] = float(values.get(n, dv))
    rig.update_tag()                     # ID-property edits do not tag the depsgraph by themselves
    bpy.context.view_layer.update()


def expression_actions(rig):
    """One single-frame action per expression (UHS_FACE_<Name>): keys on FACE_CTRL sliders only."""
    ad = rig.animation_data or rig.animation_data_create()
    keep = ad.action
    out = []
    for name, vals in EXPRESSIONS.items():
        act = bpy.data.actions.get(f"UHS_FACE_{name}") or bpy.data.actions.new(f"UHS_FACE_{name}")
        ad.action = act
        full = {n: vals.get(n, SLIDERS[n][0]) for n in SLIDERS}
        key(rig, 1, **full)
        act.use_fake_user = True
        try:
            act.asset_mark()
            act.asset_data.tags.new("face")
        except Exception:
            pass
        out.append(act)
    ad.action = keep
    return out


def auto_blink(rig, f0, f1, seed=1, every=(2.2, 5.0)):
    """Natural blinks: random gaps, 2 frames closing, 1 closed, 3 opening; both eyes (one frame apart sometimes)."""
    r = random.Random(seed)
    f = f0 + int(r.uniform(0.5, 2.0) * PC.FPS)
    key(rig, f0, blink_L=0.0, blink_R=0.0)
    while f + 6 < f1:
        lag = 1 if r.random() < 0.2 else 0
        for side, d in (("blink_L", 0), ("blink_R", lag)):
            key(rig, f + d, **{side: 0.0})
            key(rig, f + d + 2, **{side: 1.0})
            key(rig, f + d + 3, **{side: 1.0})
            key(rig, f + d + 6, **{side: 0.0})
        f += int(r.uniform(*every) * PC.FPS)


def lip_sync_from_audio(rig, audio, f0, gain=1.0, start_sec=0.0, dur_sec=None):
    """Mouth from a voice recording: per frame RMS -> jaw_open, spectral brightness -> wide (bright) or o (dark).
    Returns the number of keyed frames. Light approximation of visemes, made for cartoon mouths."""
    sr = 16000
    cmd = ["ffmpeg", "-loglevel", "error", "-ss", str(start_sec)] + (["-t", str(dur_sec)] if dur_sec else []) + \
          ["-i", audio, "-ac", "1", "-ar", str(sr), "-f", "s16le", "-"]
    pcm = subprocess.run(cmd, capture_output=True, check=True).stdout
    x = np.frombuffer(pcm, dtype=np.int16).astype(np.float32) / 32768.0
    if len(x) < sr // 10:
        raise FaceError(f"audio too short or unreadable: {audio}")
    hop = sr // PC.FPS
    n = len(x) // hop
    rms, bright = np.zeros(n), np.zeros(n)
    freqs = np.fft.rfftfreq(hop * 2, 1 / sr)
    for i in range(n):
        seg = x[i * hop: i * hop + hop * 2]
        if len(seg) < hop * 2:
            seg = np.pad(seg, (0, hop * 2 - len(seg)))
        rms[i] = np.sqrt(np.mean(seg ** 2))
        sp = np.abs(np.fft.rfft(seg * np.hanning(len(seg))))
        bright[i] = (sp * freqs).sum() / (sp.sum() + 1e-9)
    ref = np.percentile(rms, 95) + 1e-6
    level = np.clip(rms / ref * gain, 0, 1)
    level = np.where(level < 0.12, 0.0, level)                 # silence closes the mouth
    sm = np.convolve(level, [0.25, 0.5, 0.25], mode="same")     # no single-frame flutter
    bn = np.clip((bright - 900) / 1800, 0, 1)
    for i in range(n):
        key(rig, f0 + i, jaw_open=0.85 * sm[i], mouth_wide=0.7 * sm[i] * bn[i], mouth_o=0.8 * sm[i] * (1 - bn[i]))
    key(rig, f0 + n, jaw_open=0.0, mouth_wide=0.0, mouth_o=0.0)
    return n
