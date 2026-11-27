"""Replace the random lip flaps in EP_002.blend with lips driven by the real ElevenLabs voices
(blender/cast/lipsync.py). Each line starts where audio.py puts it (speech onset at the caption start + 0.05 s),
with the same pitch filter, so mouth and sound match. Saves EP_002.blend in place.
    blender/cast/bpy.sh ANIMATION_STUDIO/12_EPISODES/EP_002_SAYEH/lips.py
"""
import bpy, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
STUDIO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(STUDIO, "00_CORE_SYSTEM"))
sys.path.insert(0, os.path.join(STUDIO, "..", "cast"))
sys.path.insert(0, HERE)
import project_config as PC  # noqa: E402,F401
import lipsync  # noqa: E402
from lines import LINES, fr  # noqa: E402
from audio import VOICE_FILES, PITCH  # noqa: E402

WHO = {"mother": "MOTHER", "father": "FATHER", "arian": "ARIAN", "lina": "LINA", "daniel": "DANIEL"}
MOUTH = ("jaw_open", "mouth_o", "mouth_wide")
FPS = 24


def main():
    bpy.ops.wm.open_mainfile(filepath=os.path.join(HERE, "EP_002.blend"))
    LS = lipsync.Voices(fps=FPS)
    spans = {}
    for (a, b, who, _), name in zip(LINES, VOICE_FILES):
        af = f"rubberband=pitch={2 ** (PITCH[who] / 12):.4f}:formant=preserved" if PITCH.get(who) else None
        end = LS.add(who, os.path.join(HERE, "voices", name + ".mp3"), a + 0.05, af=af)
        spans.setdefault(who, []).append((a, max(b, end)))
        print("[lips]", who, name, f"{a + 0.05:.2f}-{end:.2f}s")
    for who, sp in spans.items():
        rig = bpy.data.objects[WHO[who] + "_RIG"]
        tr = rig.animation_data.nla_tracks["FACE"]
        act = tr.strips[0].action
        bag = act.layers[0].strips[0].channelbags[0] if getattr(act, "layers", None) else act
        for fc in bag.fcurves:
            parts = fc.data_path.split('"')
            n = parts[3] if len(parts) > 3 else ""
            if n not in MOUTH:
                continue
            for a, b in sp:                                     # drop the old flaps of these lines
                lo, hi = fr(a) - 2, fr(b) + 3
                for i in reversed([i for i, k in enumerate(fc.keyframe_points) if lo <= k.co.x <= hi]):
                    fc.keyframe_points.remove(fc.keyframe_points[i], fast=True)
            fc.update()
        fcs = {}
        for n in MOUTH:
            dp = f'pose.bones["FACE_CTRL"]["{n}"]'
            fcs[n] = bag.fcurves.find(dp)
            assert fcs[n], dp
        for a, b in sp:
            f0, f1 = fr(a) - 1, fr(b) + 2
            prev = 0.0
            for f in range(f0, f1 + 1):
                t = (f - 1) / FPS
                lv = LS.level(who, t)
                lv = 0.0 if lv < 0.08 else lv
                lv = 0.5 * lv + 0.5 * prev if lv < prev else lv     # open fast, close a little slower
                prev = lv
                wob = 0.5 + 0.5 * ((f * 7) % 5) / 4.0                  # vary the shape between syllables
                vals = {"jaw_open": 0.85 * lv, "mouth_o": 0.45 * lv * (1 - wob), "mouth_wide": 0.45 * lv * wob}
                for n, v in vals.items():
                    fcs[n].keyframe_points.insert(f, v, options={"FAST"})
            for n in MOUTH:
                fcs[n].update()
        print("[lips]", who, "keyed", sp)
    bpy.ops.wm.save_mainfile()
    print("[lips] saved")


if __name__ == "__main__":
    main()
