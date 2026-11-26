"""Builds the dialogue track from the user's single ElevenLabs recording (voices/all_lines.mp3).

Each caption line is cut from the recording (times found with word-level speech recognition),
given a character pitch (formants kept) and a device colour (phone / TV / loudspeaker),
then placed where the character's lips move.  Writes out/voice.wav and out/mix.wav (voice + sfx).
"""
import os, sys, subprocess, wave
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "school_pov"))
from captions import CAPTIONS  # noqa: E402

SR = 48000
DUR = 80.0
SRC = os.path.join(HERE, "voices", "all_lines.mp3")
SFX = os.path.join(HERE, "..", "school_pov", "out", "sfx.wav")

# caption index (1-based, order of captions.py) -> pieces (start, end) in the recording
CUTS = {
    1: [(0.00, 2.62)], 2: [(16.50, 18.10)], 3: [(18.18, 20.40)], 4: [(9.64, 11.05)], 5: [(2.70, 4.55)],
    6: [(11.20, 12.85)], 8: [(20.50, 22.70)], 9: [(28.05, 29.85)], 10: [(22.75, 24.70)],
    11: [(12.90, 14.75)], 12: [(14.88, 16.40)], 13: [(4.72, 6.50)], 14: [(29.80, 31.15)], 15: [(24.76, 26.08)],
    16: [(41.48, 42.45), (42.68, 44.22)], 17: [(44.16, 45.72)], 18: [(45.65, 47.02)], 19: [(35.34, 37.70)],
    20: [(37.62, 38.80)], 21: [(26.00, 27.28)], 22: [(31.08, 32.72)], 23: [(38.92, 40.00)], 24: [(6.54, 7.68)],
    25: [(46.98, 48.95)], 26: [(32.80, 35.38)], 27: [(27.24, 28.10)], 28: [(39.92, 41.55)], 29: [(7.88, 9.65)],
    30: [(48.88, 50.83)],
    31: [(18.18, 18.66), "gap0.35", (19.04, 20.40)],   # "ارتش... نابسامانی شده" from the news line
}
# line 7 (آقای رضایی) was not recorded -> silent until the user sends it
PITCH = {"Me": 1.0, "Mom": 3.5, "Mom voice": 3.5, "Anchor": -0.5, "Rezaei": -2.0, "Kazemi": -1.5, "Arian": 1.5,
         "Mahsa": 4.5, "Kian": 3.5, "Principal": -1.0, "Heli": 0.0, "Soldier": -2.0, None: 1.0}
DEVICE = {"Mom voice": "phone", "Anchor": "tv", "Principal": "speaker", "Heli": "speaker"}
GAIN = {"Principal": 0.9, "Heli": 0.85, "Anchor": 0.8, "Mom voice": 0.85}


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


def main():
    src = decode(SRC)
    src /= max(1e-6, np.max(np.abs(src)))
    N = int(DUR * SR)
    track = np.zeros(N, np.float32)
    starts = [c[0] for c in CAPTIONS] + [DUR]
    placed = []
    prev_end = 0.0
    for i, (a, b, who, text) in enumerate(CAPTIONS, 1):
        if i not in CUTS:
            continue
        parts = []
        for p in CUTS[i]:
            if isinstance(p, str):
                parts.append(np.zeros(int(float(p[3:]) * SR), np.float32))
                continue
            s, e = snap(src, p[0]), snap(src, p[1])
            seg = src[s:e].copy()
            f = min(len(seg) // 4, int(0.012 * SR))
            seg[:f] *= np.linspace(0, 1, f)
            seg[-f:] *= np.linspace(1, 0, f)
            parts.append(seg)
        seg = process(np.concatenate(parts), who)
        a = max(a, prev_end + 0.06)          # never on top of the previous line
        room = starts[i] - a - 0.06          # until the next line is due
        seg = fit(seg, max(room, b - a))
        prev_end = a + len(seg) / SR
        i0 = int(a * SR)
        seg = seg[: N - i0] * GAIN.get(who, 1.0)
        track[i0:i0 + len(seg)] += seg
        placed.append((i, a, a + len(seg) / SR, who, text.replace("\n", " ")))
    track /= max(1e-6, np.max(np.abs(track))) / 0.85
    os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
    write(os.path.join(HERE, "out", "voice.wav"), np.stack([track, track], 1))
    # mix with the effects, ducking them under the dialogue
    sfx = read_wav(SFX)[:N]
    if len(sfx) < N:
        sfx = np.vstack([sfx, np.zeros((N - len(sfx), 2), np.float32)])
    env = np.abs(track)
    k = int(0.15 * SR)
    env = np.convolve(env, np.ones(k) / k, mode="same")
    duck = 1.0 - 0.55 * np.clip(env / 0.08, 0, 1)
    mix = sfx * duck[:, None] * 0.8 + np.stack([track, track], 1) * 0.95
    mix /= max(1.0, np.max(np.abs(mix)) / 0.95)
    write(os.path.join(HERE, "out", "mix.wav"), mix)
    import json
    json.dump([dict(line=p[0], start=p[1], end=p[2], who=p[3], text=p[4]) for p in placed],
              open(os.path.join(HERE, "out", "voice_times.json"), "w"), ensure_ascii=False, indent=1)
    for p in placed:
        print(f"{p[0]:2d} {p[1]:5.2f}-{p[2]:5.2f} {p[3]} {p[4]}")


if __name__ == "__main__":
    main()
