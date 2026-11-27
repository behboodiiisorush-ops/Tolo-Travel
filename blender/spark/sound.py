"""Sound effects + voices for «جرقه» -> out/spark_sfx.wav (effects only) and out/spark_mix.wav (with voices).
Rain all along, thunder after each lightning flash, the power dying and coming back, the spark, the hum of the
glow in his hand, a knock before mom, footsteps to the window. Voices: voices/clips (ElevenLabs), mom through a door."""
import os, subprocess, sys, wave
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "school_pov"))
sys.path.insert(0, HERE)
import sfx as S          # noqa: E402
from captions import END, LINES, CLIPS  # noqa: E402

CARD = 4.0
TOTAL = END + CARD
FLASH = [(8.6, 1.0), (9.6, 1.0), (24.0, 0.5), (45.5, 0.8)]


def crackle(length=0.5, k=1.0):
    n = int(length * S.SR)
    x = S.noise(n) * (S.rng.random(n) < 0.08) * 1.0
    x = S.band(x, 1500, 9000) * k
    return x * S.env(n, 0.002, length * 0.6)


def hum(length, f=60.0):
    n = int(length * S.SR)
    t = S.tt(n)
    x = 0.5 * np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * 2 * f * t) + 0.15 * np.sin(2 * np.pi * 3 * f * t)
    return x * (0.8 + 0.2 * np.sin(2 * np.pi * 3.1 * t))


def thunder(length=4.0, k=1.0):
    n = int(length * S.SR)
    x = S.band(S.noise(n), 30, 400) * k
    x *= S.env(n, 0.05, length * 0.85)
    x += S.band(S.noise(n), 200, 2500) * 0.4 * k * S.env(n, 0.005, 0.5)
    return x


def clip(name):
    """an ElevenLabs sound effect from sfx_el/ (stereo-folded to mono float)"""
    return read(os.path.join(HERE, "sfx_el", name + ".mp3"))


def onset(x, th=0.15):
    """seconds into the clip where the sound really starts, so it lands on the exact frame"""
    i = np.argmax(np.abs(x) > th * np.abs(x).max())
    return i / S.SR


def at(name, t, gain=1.0, pan=0.0, length=None, fade=0.3):
    x = clip(name)
    x = x / max(1e-9, np.abs(x).max())
    if length:
        x = x[:int(length * S.SR)]
        f = int(fade * S.SR)
        x[-f:] *= np.linspace(1, 0, f)
    S.put(x, max(0.0, t - onset(x)), gain, pan)


def bed(name, t0, t1, gain, fade=1.5):
    """loop a clip with crossfades from t0 to t1 (rain, hum)"""
    x = clip(name)
    x = x / max(1e-9, np.abs(x).max())
    n, xf = int((t1 - t0) * S.SR), int(fade * S.SR)
    out, pos = np.zeros(n + len(x)), 0
    while pos < n:
        y = x.copy()
        y[:xf] *= np.linspace(0, 1, xf)
        y[-xf:] *= np.linspace(1, 0, xf)
        out[pos:pos + len(y)] += y
        pos += len(y) - xf
    out = out[:n]
    out[:xf] *= np.linspace(0, 1, xf)
    out[-xf:] *= np.linspace(1, 0, xf)
    S.put(out, t0, gain, 0.0)


def build():
    """every effect is a real ElevenLabs sound effect (sfx_el/, flow "Spark SFX")"""
    n = int(TOTAL * S.SR)
    bed("rain", 0.0, TOTAL, 0.35)
    for t, k in FLASH:
        at("thunder", t + 0.35, 0.8 * k)
    at("power_down", 10.4, 0.7)
    at("spark", 19.05, 1.0, 0.3)
    bed("glow", 19.5, 38.2, 0.25)
    at("knock", 26.6, 0.8, -0.5)
    at("surge", 38.2, 0.9, 0.3)
    at("steps", 43.2, 0.6)
    at("drone", END - 1.0, 0.5)
    return np.stack([S.L[:n], S.R[:n]], axis=1)


def read(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ar", str(S.SR), "-ac", "1", "-f", "f32le", "-"],
                         check=True, capture_output=True).stdout
    return np.frombuffer(raw, dtype=np.float32).astype(np.float64)


def voices(n):
    v = np.zeros(n)
    for (a, b, who, _), name in zip(LINES, CLIPS):
        p = os.path.join(HERE, "voices", "clips", name + ".wav")
        if who == "mom":      # through the closed door
            tmp = os.path.join(HERE, "voices", "door_" + name + ".wav")
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", p, "-af",
                            "lowpass=f=1800,highpass=f=180,aecho=0.8:0.5:35:0.25,volume=0.8", tmp], check=True)
            p = tmp
        x = read(p)
        x = x / max(1e-6, np.abs(x).max()) * 0.9
        i = int(a * S.SR)
        m = min(len(x), n - i)
        v[i:i + m] += x[:m]
    return v


def write(path, data):
    data = data / max(1e-9, np.max(np.abs(data))) * 0.89
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(S.SR)
        w.writeframes((data * 32767).astype(np.int16).tobytes())


if __name__ == "__main__":
    os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
    fx = build()
    write(os.path.join(HERE, "out", "spark_sfx.wav"), fx)
    v = voices(len(fx))
    mix = fx * 0.55 + np.stack([v, v], axis=1)
    write(os.path.join(HERE, "out", "spark_mix.wav"), mix)
    print("ok")
