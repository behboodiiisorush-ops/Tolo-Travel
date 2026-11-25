"""Dialogue track for «قانون‌ها» from the user's single ElevenLabs take (voices/rules_take1.mp3).

Each caption line is cut from the take (times from faster-whisper word stamps), pitched per character
(formants kept), coloured for the police loudspeaker, placed where the lips move, and mixed over the
effects (ducked).  Writes out/rules_voice.wav, out/rules_mix.wav and out/rules_voice.mp4.
"""
import os, sys, subprocess, wave
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from captions import LINES, END  # noqa: E402

SR = 48000
DUR = 79.5
SRC = os.path.join(HERE, "voices", "rules_take1.mp3")
SFX = os.path.join(HERE, "out", "rules_sfx.wav")
CARD = (END + 0.5, "card", "question")        # the question over the end card

# caption index (1-based, order of captions.py; 0 = the end-card question) -> pieces in the take
CUTS = {
    1: [(0.00, 2.42)], 2: [(17.30, 19.64)], 3: [(30.02, 33.26)], 4: [(2.42, 3.96)], 5: [(12.82, 15.28)],
    6: [(19.64, 22.34)], 7: [(33.26, 36.42)], 8: [(3.96, 5.36)], 9: [(15.28, 17.00)], 10: [(36.42, 40.64)],
    11: [(5.36, 8.80)], 12: [(8.80, 11.60)], 13: [(40.64, 44.64)], 14: [(22.34, 25.30), "gap0.25", (25.62, 27.48)],
    15: [(27.48, 30.02)], 16: [(44.64, 47.92)], 0: [(47.92, 51.40)],
}
PITCH = {}   # every character already has his/her own ElevenLabs voice (the masked man is Omid, Kabuli) - no pitch shift
DEVICE = {"police": "speaker"}
GAIN = {"police": 0.9, "rule": 0.7, "card": 0.8}


def decode(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).copy()


def snap(x, t, win=0.12):
    """Move a cut point to the quietest 10 ms within +-win s."""
    i0, i1 = max(0, int((t - win) * SR)), min(len(x), int((t + win) * SR))
    hop = int(0.01 * SR)
    best, bi = 1e9, int(t * SR)
    for i in range(i0, i1 - hop, hop // 2):
        e = float(np.mean(x[i:i + hop] ** 2))
        if e < best:
            best, bi = e, i
    return bi


def process(seg, who):
    p = PITCH.get(who, 0.0)
    af = []
    if p:
        af.append(f"rubberband=pitch={2 ** (p / 12):.4f}:formant=preserved")
    dev = DEVICE.get(who)
    if dev == "phone":
        af += ["highpass=f=320", "lowpass=f=3300", "acrusher=bits=10:mix=0.25", "volume=1.4"]
    elif dev == "tv":
        af += ["highpass=f=160", "lowpass=f=6500", "aecho=0.8:0.5:22:0.18"]
    elif dev == "speaker":
        af += ["highpass=f=450", "lowpass=f=3200", "acrusher=bits=8:mix=0.35", "aecho=0.8:0.6:90|170:0.35|0.2",
               "volume=1.6"]
    if not af:
        return seg
    r = subprocess.run(["ffmpeg", "-v", "error", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-",
                        "-af", ",".join(af), "-f", "f32le", "-"], input=seg.astype(np.float32).tobytes(),
                       capture_output=True, check=True)
    return np.frombuffer(r.stdout, np.float32).copy()


def fit(seg, room):
    """Speed up (pitch kept) a line that would run over its slot, at most 1.3x."""
    d = len(seg) / SR
    if d <= room:
        return seg
    k = min(1.3, d / room)
    r = subprocess.run(["ffmpeg", "-v", "error", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-",
                        "-af", f"atempo={k:.3f}", "-f", "f32le", "-"], input=seg.astype(np.float32).tobytes(),
                       capture_output=True, check=True)
    return np.frombuffer(r.stdout, np.float32).copy()


def write(path, data):
    data = np.clip(data, -1, 1)
    pcm = (data * 32767).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(2 if data.ndim == 2 else 1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


def read_wav(path):
    with wave.open(path) as w:
        n, ch, sr = w.getnframes(), w.getnchannels(), w.getframerate()
        a = np.frombuffer(w.readframes(n), np.int16).astype(np.float32) / 32768
    a = a.reshape(-1, ch)
    if sr != SR:
        idx = np.linspace(0, len(a) - 1, int(len(a) * SR / sr))
        a = np.stack([np.interp(idx, np.arange(len(a)), a[:, c]) for c in range(ch)], 1)
    return a


def cut(src, pieces):
    parts = []
    for p in pieces:
        if isinstance(p, str):
            parts.append(np.zeros(int(float(p[3:]) * SR), np.float32))
            continue
        s, e = snap(src, p[0]), snap(src, p[1])
        seg = src[s:e].copy()
        f = min(len(seg) // 4, int(0.012 * SR))
        seg[:f] *= np.linspace(0, 1, f)
        seg[-f:] *= np.linspace(1, 0, f)
        parts.append(seg)
    return np.concatenate(parts)


def main():
    src = decode(SRC)
    src /= max(1e-6, np.max(np.abs(src)))
    N = int(DUR * SR)
    track = np.zeros(N, np.float32)
    lines = list(LINES) + [(CARD[0], DUR - 0.2, CARD[1], CARD[2])]
    starts = [c[0] for c in lines] + [DUR]
    placed, prev_end = [], 0.0
    for i, (a, b, who, text) in enumerate(lines, 1):
        key = 0 if who == "card" else i
        if key not in CUTS:
            continue
        seg = process(cut(src, CUTS[key]), who)
        a = max(a, prev_end + 0.06)
        room = starts[i] - a - 0.06
        seg = fit(seg, max(room, b - a))
        prev_end = a + len(seg) / SR
        i0 = int(a * SR)
        seg = seg[: N - i0] * GAIN.get(who, 1.0)
        track[i0:i0 + len(seg)] += seg
        placed.append((i, a, prev_end, who, text))
    track /= max(1e-6, np.max(np.abs(track))) / 0.85
    out = os.path.join(HERE, "out")
    write(os.path.join(out, "rules_voice.wav"), np.stack([track, track], 1))
    sfx = read_wav(SFX)[:N]
    if len(sfx) < N:
        sfx = np.vstack([sfx, np.zeros((N - len(sfx), 2), np.float32)])
    k = int(0.15 * SR)
    env = np.convolve(np.abs(track), np.ones(k) / k, mode="same")
    duck = 1.0 - 0.55 * np.clip(env / 0.08, 0, 1)
    mix = sfx * duck[:, None] * 0.8 + np.stack([track, track], 1) * 0.95
    mix /= max(1.0, np.max(np.abs(mix)) / 0.95)
    write(os.path.join(out, "rules_mix.wav"), mix)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", os.path.join(out, "rules_captions.mp4"),
                    "-i", os.path.join(out, "rules_mix.wav"), "-map", "0:v", "-map", "1:a", "-c:v", "copy",
                    "-c:a", "aac", "-b:a", "192k", "-shortest", os.path.join(out, "rules_voice.mp4")], check=True)
    for p in placed:
        print(f"{p[0]:2d} {p[1]:5.2f}-{p[2]:5.2f} {p[3]:8s} {p[4]}")


if __name__ == "__main__":
    main()
