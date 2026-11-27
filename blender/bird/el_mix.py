"""Mix the ElevenLabs voices + sound effects of «هشدار» (files in el/, generated with the ElevenLabs MCP tools).
    out/bird_sfx.wav     ElevenLabs sound effects only
    out/bird_voice.wav   ElevenLabs voices + sound effects
Voices: Kian = "Sara - Neutral Persian Female" pitched up 2 semitones (formants kept) -> a boy;
        Mom = "Hengameh"; passer-by = "Aidin Podcast" (all eleven_v3, delivery tags from voice_script.md).
Each line starts at its caption start (the lips are already rendered there); a line longer than its caption
window + 0.5 s is sped up (max 1.3x) so it ends with the lips.
"""
import os, subprocess, sys, wave
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from captions import LINES, END  # noqa: E402
EL, OUT = os.path.join(HERE, "el"), os.path.join(HERE, "out")
SR = 48000
TOTAL = END + 4.0
FLIGHTS = [(5.8, 8.8), (13.9, 17.4), (22.6, 25.6), (27.0, 27.7), (33.0, 33.7), (41.0, 41.7),
           (49.0, 49.8), (49.8, 52.6), (52.6, 54.0)]
VOICE_FILES = {(3.0, "kian"): "kian1", (44.0, "kian"): "kian2", (50.8, "kian"): "kian3", (57.0, "kian"): "kian4",
               (10.8, "mom"): "mom1", (46.9, "mom"): "mom2", (13.6, "passerby"): "pass1", (18.0, "passerby"): "pass2"}


def load(name, af=None):
    """Decode el/<name>.mp3 to mono float32 at SR, trimming silence at both ends, with optional ffmpeg filters."""
    flt = "silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse"
    if af:
        flt += "," + af
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", os.path.join(EL, name + ".mp3"), "-af", flt,
                          "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).copy()


def put(buf, x, t, gain=1.0, pan=0.0, length=None, fade=0.05):
    if length is not None:
        x = x[:int(length * SR)]
    x = x * gain
    nf = min(len(x) // 2, int(fade * SR))
    if nf:
        x[:nf] *= np.linspace(0, 1, nf)
        x[-nf:] *= np.linspace(1, 0, nf)
    i = int(t * SR)
    j = min(buf.shape[0], i + len(x))
    if j <= i:
        return
    buf[i:j, 0] += x[:j - i] * (1 - max(0, pan))
    buf[i:j, 1] += x[:j - i] * (1 + min(0, pan))


def voices(buf):
    windows = []
    for a, b, who, _ in LINES:
        name = VOICE_FILES[(a, who)]
        af = {"kian": "rubberband=pitch=1.122:formant=preserved",
              "mom": "lowpass=f=3800,aecho=0.8:0.5:40:0.25",                         # from another room
              "passerby": "lowpass=f=5000,aecho=0.8:0.4:60:0.2"}[who]               # across the street
        x = load(name, af)
        dur, room = len(x) / SR, (b - a) + 0.5
        if dur > room:
            x = load(name, af + f",rubberband=tempo={min(1.3, dur / room):.3f}")
        gain = {"kian": 0.95, "mom": 0.8, "passerby": 0.6}[who]
        put(buf, x, a, gain, {"kian": 0.0, "mom": -0.25, "passerby": 0.3}[who])
        windows.append((a, a + len(x) / SR))
        print(f"{name:6s} {who:8s} {a:5.1f}s  {dur:.2f}s -> {len(x) / SR:.2f}s (window {b - a:.1f}s)")
    return windows


def effects(buf, duck=()):
    amb = load("amb")
    n_end = int(END * SR)
    bed = np.tile(amb, int(np.ceil(n_end / len(amb))) + 1)[:n_end]
    env = np.ones(n_end, np.float32)
    for a, b in duck:                                   # ambience dips under the dialogue
        i, j = int((a - 0.2) * SR), int((b + 0.2) * SR)
        env[max(0, i):j] = 0.55
    env = np.convolve(env, np.ones(4800) / 4800, mode="same")
    put(buf, bed * env, 0.0, 0.45, fade=1.5)
    wings, chirp = load("wings"), load("chirp")
    for a, b in FLIGHTS:
        put(buf, wings, a, 0.55, 0.0, length=max(0.6, b - a))
    for t, g in ((0.3, 0.6), (9.2, 0.5), (26.0, 0.5), (49.9, 0.8)):
        put(buf, chirp, t, g)
    put(buf, load("attack"), 16.8, 0.6, 0.35)            # Rezaei attacks the passer-by
    put(buf, load("heart"), 17.6, 0.35, length=9.0, fade=0.8)
    put(buf, load("bang"), 39.0, 0.75, 0.1)              # he bangs the entrance door
    put(buf, load("buzzer"), 40.2, 0.5, -0.3)
    heart = load("heart")
    for t in np.arange(42.0, 61.0, len(heart) / SR - 0.3):
        put(buf, heart, t, 0.4, length=min(len(heart) / SR, 61.0 - t), fade=0.3)
    put(buf, load("scream"), 56.6, 0.95)                 # he screams up at them


def write(path, buf):
    buf = buf / max(1e-9, np.abs(buf).max()) * 0.89
    tail = int(1.0 * SR)                                 # fade out into the question card
    e = int(END * SR)
    buf[e:e + tail] *= np.linspace(1, 0, min(tail, len(buf) - e))[:, None]
    buf[e + tail:] = 0
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((buf * 32767).astype("<i2").tobytes())
    print(path)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    n = int(TOTAL * SR)
    v = np.zeros((n, 2), np.float32)
    win = voices(v)
    fx = np.zeros((n, 2), np.float32)
    effects(fx)
    write(os.path.join(OUT, "bird_sfx.wav"), fx.copy())
    fx2 = np.zeros((n, 2), np.float32)
    effects(fx2, win)
    write(os.path.join(OUT, "bird_voice.wav"), fx2 * 0.8 + v)
