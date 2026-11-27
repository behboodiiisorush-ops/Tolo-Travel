"""Lip sync from the real ElevenLabs voices (shared by every film) — no paid add-on needed.

The cast's faces already blink on their own (anim.blink) and open the mouth by `talking=`; when `talking` is a
number 0..1 instead of True, the mouth follows that loudness. This module turns the voice clips into that number.

    import lipsync
    LS = lipsync.Voices(fps=24)
    LS.add("kian", "el/kian1.mp3", start=3.0)          # one call per line: who, clip, where it starts (s)
    ...
    ch.animate(f, t, ..., talking=LS.level("kian", t))  # 0 when silent -> mouth closed, else loudness

Persian works fine: it follows the sound, not the words. Lines that were sped up/trimmed in the mix should be
added with the same file + `af` filter used there (e.g. af="rubberband=tempo=1.2") so the lips match.
"""
import subprocess
import numpy as np

SR = 16000
HOP = SR // 100                                     # 10 ms envelope


def _decode(path, af=None):
    flt = "silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse"
    if af:
        flt += "," + af
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-af", flt, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32)


class Voices:
    def __init__(self, fps=24):
        self.fps = fps
        self.lines = {}                               # who -> [(start, end, env)]

    def add(self, who, path, start, af=None):
        a = _decode(path, af)
        env = np.sqrt(np.convolve(a ** 2, np.ones(HOP * 4) / (HOP * 4), mode="same"))[::HOP]
        ref = float(np.percentile(env[env > 0.01], 90)) if np.any(env > 0.01) else 1.0
        env = np.clip(env / ref, 0, 1)
        self.lines.setdefault(who, []).append((start, start + len(env) / 100.0, env))
        return start + len(env) / 100.0             # end time, handy for captions

    def level(self, who, t):
        """0 when this character is silent at time t, else its loudness 0.02..1."""
        for a, b, env in self.lines.get(who, ()):
            if a <= t <= b:
                return max(0.02, float(env[min(int((t - a) * 100), len(env) - 1)]))
        return 0.0

    def speaking(self, who, t):
        return self.level(who, t) > 0
