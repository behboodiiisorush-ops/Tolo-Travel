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


def build():
    n = int(TOTAL * S.SR)
    rain = S.band(S.noise(n), 800, 7000) * 0.06 + S.band(S.noise(n), 150, 800) * 0.03
    rain *= np.minimum(1.0, S.tt(n) / 1.5)
    S.L[:n] += rain
    S.R[:n] += rain * 0.95
    for t, k in FLASH:
        S.put(thunder(4.5, k), t + 0.35, 0.9 * k)
    S.put(hum(10.0, 50) * 0.04, 0.0, 0.5)                                # fridge/electrics until the cut
    S.put(S.tone(90, 0.9, 0.5) * np.linspace(1, 0, int(0.9 * S.SR)), 10.0, 0.4)   # power dies
    S.put(crackle(0.6, 1.0), 19.05, 1.0, 0.3)                            # the spark
    S.put(crackle(0.3, 0.7), 19.4, 0.8, 0.3)
    glow = hum(15.0, 110) * 0.05                                          # the glow in his hand
    S.put(glow * S.env(len(glow), 1.0, 2.0), 19.5, 0.6)
    for k in (26.6, 26.85):                                               # knock before mom calls
        S.put(S.knock(0.8), k, 0.7, -0.5)
    S.put(crackle(0.5, 1.0), 38.2, 1.0, 0.3)                              # surge back into the lamp
    S.put(S.tone(70, 1.0, 0.5) * np.linspace(0, 1, S.SR), 38.0, 0.35)     # power comes back
    S.put(hum(18.0, 50) * 0.04, 38.5, 0.5)
    S.footsteps(43.2, 46.0, 1.9, 0.35)
    S.put(S.tone(55, 4.0, 0.2) * S.env(int(4.0 * S.SR), 0.8, 1.5), END - 0.5, 1.0)
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
